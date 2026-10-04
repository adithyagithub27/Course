"""FastAPI front door for Atlas.

* ``POST /chat``      — headers ``X-Tenant`` (required), ``X-User``, ``X-Session``; body ``{"message": ...}``
* ``POST /feedback``  — thumbs up/down for a trace (Section 8.3)
* ``GET  /metrics``   — Prometheus (``prometheus_client.make_asgi_app``)
* ``GET  /healthz``   — liveness + exporter health
* ``GET  /budget``    — per-tenant budget status

Run: ``uvicorn app.server:app --reload`` (or ``make run``).
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
from collections import OrderedDict
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.agent import AgentResult, AtlasAgent
from northwind.budget import BudgetGuard
from northwind.config import SCENARIOS, TENANTS, Settings, get_settings, normalise_tenant_id
from northwind.pii import mask_text
from telemetry import metrics
from telemetry.langfuse_setup import create_score
from telemetry.local_store import LocalSpanStore, ScoreRecord
from telemetry.logging_setup import configure_logging
from telemetry.otel_setup import (
    configure_tracing,
    exporter_health,
    force_flush,
    get_store,
    shutdown_tracing,
)

log = logging.getLogger("atlas.server")

MAX_SESSIONS = 5000
MAX_HISTORY_MESSAGES = 40


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None
    scenario: str | None = Field(default=None, description="incident injector for demos")
    stream: bool = True


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    trace_id: str
    model: str
    steps: int
    outcome: str
    intent: str
    usage: dict[str, int]
    cost_usd: float
    latency_ms: float
    ttft_ms: float | None
    tool_calls: list[str]
    escalated: bool
    retries: int
    budget_decision: str | None
    prompt_version: str


class FeedbackRequest(BaseModel):
    trace_id: str
    session_id: str | None = None
    score: int = Field(ge=-1, le=1, description="1 = thumbs up, -1 = thumbs down, 0 = neutral")
    reason: str | None = Field(
        default=None, max_length=64, description="e.g. wrong_answer, too_slow, unhelpful"
    )
    comment: str | None = Field(default=None, max_length=1000)


class SessionMemory:
    """Bounded in-memory conversation history per session (LRU)."""

    def __init__(
        self, max_sessions: int = MAX_SESSIONS, max_messages: int = MAX_HISTORY_MESSAGES
    ) -> None:
        self._d: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
        self.max_sessions = max_sessions
        self.max_messages = max_messages

    def get(self, session_id: str) -> list[dict[str, Any]]:
        hist = self._d.get(session_id, [])
        if session_id in self._d:
            self._d.move_to_end(session_id)
        return list(hist)

    def extend(self, session_id: str, turn_messages: list[dict[str, Any]]) -> None:
        """Append this turn's messages (user, tool calls, tool results, assistant): the naive
        baseline that the context diet later trims."""
        hist = self._d.setdefault(session_id, [])
        hist.extend(m for m in turn_messages if m.get("role") != "system")
        del hist[: -self.max_messages]
        self._d.move_to_end(session_id)
        while len(self._d) > self.max_sessions:
            self._d.popitem(last=False)

    def __len__(self) -> int:
        return len(self._d)


class TenantLimiter:
    """One semaphore per tenant (Lecture 7.5). A request waits up to ``timeout_s`` for a slot in
    its own tenant's queue; then it is shed with 429 so one noisy tenant cannot take every
    provider slot. ``atlas_inflight{tenant}`` and ``atlas_queue_wait_seconds{tenant}`` show it."""

    def __init__(self, limits: dict[str, int], *, timeout_s: float = 3.0) -> None:
        self.limits = dict(limits)
        self.timeout_s = timeout_s
        self._sems: dict[str, asyncio.Semaphore] = {}

    def _sem(self, tenant: str) -> asyncio.Semaphore:
        if tenant not in self._sems:
            self._sems[tenant] = asyncio.Semaphore(
                self.limits.get(tenant, self.limits.get("other", 2))
            )
        return self._sems[tenant]

    @asynccontextmanager
    async def slot(self, tenant: str):  # type: ignore[no-untyped-def]
        sem = self._sem(tenant)
        t0 = time.perf_counter()
        try:
            await asyncio.wait_for(sem.acquire(), timeout=self.timeout_s)
        except TimeoutError:
            metrics.QUEUE_WAIT.labels(tenant).observe(time.perf_counter() - t0)
            metrics.SHED.labels(tenant).inc()
            raise HTTPException(
                status_code=429,
                detail=f"tenant {tenant} is at its concurrency limit; retry shortly",
                headers={"Retry-After": "1"},
            ) from None
        metrics.QUEUE_WAIT.labels(tenant).observe(time.perf_counter() - t0)
        metrics.INFLIGHT.labels(tenant).inc()
        try:
            yield
        finally:
            metrics.INFLIGHT.labels(tenant).dec()
            sem.release()


def normalise_tenant(tenant: str | None) -> str:
    """Aliases (``logistics-ops`` -> ``ops``) are mapped; unknown tenants collapse to
    ``other`` so Prometheus labels stay bounded."""
    if not tenant:
        raise HTTPException(status_code=400, detail="X-Tenant header is required")
    return normalise_tenant_id(tenant) or "other"


def to_response(r: AgentResult) -> ChatResponse:
    return ChatResponse(
        answer=r.answer,
        session_id=r.session_id,
        trace_id=r.trace_id,
        model=r.model,
        steps=r.steps,
        outcome=r.outcome,
        intent=r.intent,
        usage=r.usage,
        cost_usd=r.cost_usd,
        latency_ms=r.latency_ms,
        ttft_ms=r.ttft_ms,
        tool_calls=r.tool_calls,
        escalated=r.escalated,
        retries=r.retries,
        budget_decision=r.budget_decision,
        prompt_version=r.prompt_version,
    )


#: FastAPI >= 0.142 ships native OpenTelemetry: with a global TracerProvider installed it opens a
#: ``POST /chat`` server span plus ``fastapi.dependencies`` / ``fastapi.endpoint`` /
#: ``fastapi.serialization`` operation spans, and ``invoke_agent atlas`` becomes their grandchild.
#: Atlas's trace contract (Lectures 3.2 and 3.6) is "exactly one root span, named
#: ``invoke_agent atlas``", so the framework's own telemetry is switched off. It would also
#: auto-configure OTLP exporters from ``OTEL_*`` env vars behind our back (``auto_configure``).
FASTAPI_TELEMETRY_OFF: dict[str, Any] = {
    "tracing": False,
    "operation_spans": False,
    "metrics": False,
    "logs": False,
    "auto_configure": False,
}


def _fastapi_telemetry_off() -> dict[str, Any]:
    """``{"telemetry": {...}}`` on FastAPI versions that have native telemetry, else ``{}``."""
    if "telemetry" in inspect.signature(FastAPI.__init__).parameters:
        return {"telemetry": dict(FASTAPI_TELEMETRY_OFF)}
    return {}


def _asgi_endpoint(asgi_app: Any) -> Any:
    """Wrap a raw ASGI app as a Starlette endpoint (an exact-path route, no redirect)."""

    async def endpoint(request: Request) -> Any:
        from starlette.responses import Response

        sent: dict[str, Any] = {"status": 200, "headers": [], "body": b""}

        async def send(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                sent["status"], sent["headers"] = message["status"], message.get("headers", [])
            elif message["type"] == "http.response.body":
                sent["body"] += message.get("body", b"")

        await asgi_app(request.scope, request.receive, send)
        headers = {k.decode(): v.decode() for k, v in sent["headers"]}
        headers.pop("content-length", None)
        return Response(content=sent["body"], status_code=sent["status"], headers=headers)

    return endpoint


def create_app(
    settings: Settings | None = None,
    *,
    store: LocalSpanStore | None = None,
    llm: Any = None,
    budget_guard: BudgetGuard | None = None,
) -> FastAPI:
    """Application factory. Tests pass ``OTEL_EXPORTER=memory`` settings and an in-memory store."""
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
        configure_logging(settings.log_level)
        configure_tracing(settings, store=store)
        app.state.store = get_store()
        app.state.budget = budget_guard or BudgetGuard.from_caps(
            list(TENANTS) + ["other"],
            soft=settings.tenant_soft_cap_usd,
            hard=settings.tenant_hard_cap_usd,
            window_s=settings.budget_window_s,
        )
        app.state.agent = AtlasAgent(settings, llm=llm, budget_guard=app.state.budget)
        metrics.set_build_info(
            version=settings.langfuse_release,
            model=settings.model,
            prompt_version=settings.prompt_version,
        )
        app.state.sessions = SessionMemory()
        app.state.limiter = TenantLimiter(
            settings.inflight_limits(), timeout_s=settings.queue_timeout_s
        )
        app.state.started = time.time()
        log.info(
            "atlas started", extra={"offline": settings.offline, "exporter": settings.otel_exporter}
        )
        try:
            yield
        finally:
            force_flush()
            shutdown_tracing()

    app = FastAPI(
        title="Atlas helpdesk agent", version="1.0.0", lifespan=lifespan, **_fastapi_telemetry_off()
    )
    # Mounted twice so both /metrics and /metrics/ answer 200 directly (a single mount at
    # "/metrics" made Starlette answer /metrics with a 307 redirect to /metrics/).
    metrics_asgi = metrics.metrics_app()
    app.add_route(
        "/metrics", _asgi_endpoint(metrics_asgi), methods=["GET"], include_in_schema=False
    )
    app.mount("/metrics/", metrics_asgi)

    @app.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {
            "status": "ok",
            "offline": settings.offline,
            "model": settings.model,
            "prompt_version": settings.prompt_version,
            "exporters": exporter_health(),
            "uptime_s": round(time.time() - getattr(app.state, "started", time.time()), 1),
        }

    @app.get("/budget")
    async def budget() -> list[dict[str, Any]]:
        return [d.as_dict() for d in app.state.budget.status(time.time())]

    @app.post("/chat", response_model=ChatResponse)
    async def chat(
        req: ChatRequest,
        request: Request,
        x_tenant: str | None = Header(default=None, alias="X-Tenant"),
        x_user: str | None = Header(default="anonymous", alias="X-User"),
        x_session: str | None = Header(default=None, alias="X-Session"),
    ) -> ChatResponse:
        tenant = normalise_tenant(x_tenant)
        if req.scenario is not None and req.scenario not in SCENARIOS:
            raise HTTPException(
                status_code=422, detail=f"scenario must be one of {list(SCENARIOS)}"
            )
        agent: AtlasAgent = app.state.agent
        sessions: SessionMemory = app.state.sessions
        session_id = req.session_id or x_session
        history = sessions.get(session_id) if session_id else []
        limiter: TenantLimiter = app.state.limiter
        async with limiter.slot(tenant):
            # The agent is synchronous (blocking provider calls): run it on a worker thread so
            # the event loop keeps serving. asyncio.to_thread copies the OTel context (3.6).
            result = await asyncio.to_thread(
                agent.run,
                req.message,
                tenant=tenant,
                user_id=x_user or "anonymous",
                session_id=session_id,
                history=history,
                scenario=req.scenario,
                stream=req.stream,
            )
        sessions.extend(
            result.session_id,
            result.messages[len(history) + 1 :]
            if result.messages
            else [
                {"role": "user", "content": req.message},
                {"role": "assistant", "content": result.answer},
            ],
        )
        status = 429 if result.outcome == "refused" else 200
        if status != 200:
            raise HTTPException(status_code=status, detail=to_response(result).model_dump())
        return to_response(result)

    @app.post("/feedback")
    async def feedback(
        fb: FeedbackRequest,
        x_tenant: str | None = Header(default=None, alias="X-Tenant"),
    ) -> dict[str, Any]:
        tenant = normalise_tenant(x_tenant) if x_tenant else "other"
        outcome = {1: "positive", -1: "negative", 0: "neutral"}[fb.score]
        metrics.FEEDBACK.labels(tenant, outcome).inc()
        value = 1.0 if fb.score == 1 else 0.0 if fb.score == -1 else 0.5
        # Free text is user data: redact it like every span attribute before storing or sending.
        comment = " | ".join(mask_text(x, hash_ids=True) for x in [fb.reason, fb.comment] if x)
        store: LocalSpanStore | None = app.state.store
        if store is not None:
            store.add_score(
                ScoreRecord(
                    trace_id=fb.trace_id,
                    name="user_feedback",
                    value=value,
                    source="user",
                    comment=comment,
                    timestamp=time.time(),
                    tenant=tenant,
                    session_id=fb.session_id or "",
                )
            )
        sent = create_score(
            fb.trace_id, "user_feedback", value, comment=comment or None, data_type="NUMERIC"
        )
        return {"recorded": True, "trace_id": fb.trace_id, "value": value, "langfuse": sent}

    return app


app = create_app()
