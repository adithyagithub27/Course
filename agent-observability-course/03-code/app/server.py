"""FastAPI front door for Atlas.

* ``POST /chat``      — headers ``X-Tenant`` (required), ``X-User``, ``X-Session``; body ``{"message": ...}``
* ``POST /feedback``  — thumbs up/down for a trace (Section 8.3)
* ``GET  /metrics``   — Prometheus (``prometheus_client.make_asgi_app``)
* ``GET  /healthz``   — liveness + exporter health
* ``GET  /budget``    — per-tenant budget status

Run: ``uvicorn app.server:app --reload`` (or ``make run``).
"""

from __future__ import annotations

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
        app.state.sessions = SessionMemory()
        app.state.started = time.time()
        log.info(
            "atlas started", extra={"offline": settings.offline, "exporter": settings.otel_exporter}
        )
        try:
            yield
        finally:
            force_flush()
            shutdown_tracing()

    app = FastAPI(title="Atlas helpdesk agent", version="1.0.0", lifespan=lifespan)
    app.mount("/metrics", metrics.metrics_app())

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
        result = agent.run(
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
        comment = " | ".join(x for x in [fb.reason, fb.comment] if x)
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
