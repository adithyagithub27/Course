"""Offline replay: a full day of spans into the local store (and optionally Langfuse)
without a single LLM call.

For every planned request the real :class:`app.agent.AtlasAgent` runs against the
mock LLM (so token counts, tool calls, retries and answers are genuine agent
behaviour). The resulting generation/tool records are then laid out on the
planned timeline as :class:`telemetry.local_store.SpanRecord` rows. The heuristic
judge from ``evals.online_judge`` scores a sample, and some users leave feedback.

Deterministic by seed; ~400 sessions replay in a few seconds.

CLI::

    OFFLINE=1 python simulator/replay.py --seed 7 --sessions 400 --incidents cost_spike
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from opentelemetry.trace import NoOpTracer  # noqa: E402

from app.agent import AgentResult, AtlasAgent, CircuitBreaker  # noqa: E402
from app.knowledge import get_kb  # noqa: E402
from app.mock_llm import MockLLM  # noqa: E402
from app.tools import TicketStore  # noqa: E402
from northwind.config import Settings  # noqa: E402
from northwind.pii import contains_pii, mask_text  # noqa: E402
from simulator.scenarios import (  # noqa: E402
    DEFAULT_DATE,
    INCIDENT_PRESETS,
    Incident,
    PlannedRequest,
    generate_day,
    summarize_plan,
)
from telemetry import genai_attrs as ga  # noqa: E402
from telemetry.local_store import LocalSpanStore, ScoreRecord, SpanRecord  # noqa: E402

TOOL_LATENCY_MS: dict[str, tuple[float, float]] = {
    "search_knowledge_base": (12.0, 45.0),
    "lookup_ticket": (40.0, 120.0),
    "create_ticket": (60.0, 160.0),
    "reset_password": (180.0, 420.0),
    "check_shipment": (80.0, 300.0),
}

RESOURCE = {
    "service.name": "atlas",
    "service.version": "v1.0.0",
    "deployment.environment": "replay",
    "atlas.offline": True,
}


def _masked(text: str | None, limit: int) -> str:
    """Mask PII (hashed placeholders, as ``genai_attrs._safe`` does), then clip."""
    return mask_text(text or "", hash_ids=True)[:limit]


def _hex(*parts: Any, n: int) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:n]


@dataclass
class ReplaySummary:
    seed: int
    requests: int = 0
    sessions: int = 0
    spans: int = 0
    scores: int = 0
    feedback: int = 0
    cost_usd: float = 0.0
    by_tenant_cost: dict[str, float] = field(default_factory=dict)
    by_scenario: dict[str, int] = field(default_factory=dict)
    outcomes: dict[str, int] = field(default_factory=dict)
    p95_latency_ms: float = 0.0
    elapsed_s: float = 0.0
    incidents: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    def render(self) -> str:
        lines = [
            f"Replay seed={self.seed}  requests={self.requests}  sessions={self.sessions}  spans={self.spans}  scores={self.scores}  feedback={self.feedback}",
            f"Total cost ${self.cost_usd:.4f}   p95 latency {self.p95_latency_ms:.0f} ms   elapsed {self.elapsed_s:.1f}s",
            "Cost by tenant: "
            + ", ".join(f"{k}=${v:.4f}" for k, v in sorted(self.by_tenant_cost.items())),
            "Outcomes: " + ", ".join(f"{k}={v}" for k, v in sorted(self.outcomes.items())),
            "Scenarios: " + ", ".join(f"{k}={v}" for k, v in sorted(self.by_scenario.items())),
        ]
        if self.incidents:
            lines.append("Incidents: " + ", ".join(self.incidents))
        return "\n".join(lines)


class ReplayEngine:
    """Turns a plan into spans. One MockLLM is shared so prompt-cache state is realistic."""

    def __init__(self, seed: int, base_settings: Settings | None = None) -> None:
        logging.getLogger("atlas.agent").setLevel(logging.ERROR)  # retries are expected here
        self.seed = seed
        self.settings = (base_settings or Settings.from_env({})).with_overrides(
            offline=True, otel_exporter="none", scenario=None
        )
        self.llm = MockLLM(seed=seed)
        self.kb = get_kb()
        self.tickets = TicketStore()
        self._tracer = (
            NoOpTracer()
        )  # the replay builds its own SpanRecords; agent spans are discarded
        self._agents: dict[tuple[Any, ...], AtlasAgent] = {}
        self.rng = random.Random(seed)
        # One circuit breaker for the whole replay (one process, one set of deployments), on the
        # *replayed* clock: the cooldown is measured in day time, not in wall time, so a replay
        # is deterministic however fast the machine is.
        self._now = 0.0
        self.breaker = CircuitBreaker(
            threshold=max(1, self.settings.router_allowed_fails),
            cooldown_s=float(self.settings.router_cooldown_s),
            clock=lambda: self._now,
        )

    def _agent(self, params: dict[str, Any]) -> AtlasAgent:
        key = (
            params.get("prompt_version", self.settings.prompt_version),
            params.get("top_k", self.settings.retrieval_top_k),
            params.get("context_diet", self.settings.context_diet),
        )
        if key not in self._agents:
            s = self.settings.with_overrides(
                prompt_version=key[0], retrieval_top_k=key[1], context_diet=key[2]
            )
            self._agents[key] = AtlasAgent(
                s,
                llm=self.llm,
                kb=self.kb,
                tickets=self.tickets,
                clock=lambda: 0.0,
                sleep=lambda _s: None,
                tracer=self._tracer,
                capture_content=False,
            )
            self._agents[key].breaker = self.breaker
        return self._agents[key]

    # ------------------------------------------------------------------ span building
    def build_trace(
        self, req: PlannedRequest, result: AgentResult, history: list[dict[str, Any]]
    ) -> list[SpanRecord]:
        rng = random.Random(f"{self.seed}:{req.session_id}:{req.turn}")
        trace_id = _hex(self.seed, req.session_id, req.turn, n=32)
        t = req.ts
        spans: list[SpanRecord] = []
        common = {
            ga.ATLAS_TENANT: req.tenant,
            ga.ATLAS_FEATURE: result.feature,
            ga.ATLAS_INTENT: result.intent,
            ga.LF_SESSION_ID: req.session_id,
            ga.LF_USER_ID: req.persona.user_id,
        }
        if req.scenario:
            common[ga.ATLAS_SCENARIO] = req.scenario
        root_id = _hex(trace_id, "root", n=16)
        # guardrail
        g_ms = 0.4 + rng.random() * 0.8
        spans.append(
            SpanRecord(
                trace_id,
                _hex(trace_id, "guard", n=16),
                "guardrail injection_check",
                "guardrail",
                t,
                t + g_ms / 1000,
                root_id,
                "OK",
                {
                    **common,
                    ga.LF_OBS_TYPE: "guardrail",
                    ga.ATLAS_GUARDRAIL_KIND: "prompt_injection",
                    ga.ATLAS_GUARDRAIL_TRIGGERED: result.guardrail_triggered,
                },
                RESOURCE,
            )
        )
        t += g_ms / 1000
        gens_by_step: dict[int, list[Any]] = {}
        for g in result.generations:
            gens_by_step.setdefault(g.step, []).append(g)
        tools_by_step: dict[int, list[Any]] = {}
        for tr in result.tools:
            tools_by_step.setdefault(tr.step, []).append(tr)
        first_token_at: float | None = None
        for step in range(1, result.steps + 1):
            step_id = _hex(trace_id, "step", step, n=16)
            step_start = t
            for gi, g in enumerate(gens_by_step.get(step, [])):
                gen_id = _hex(trace_id, "gen", step, gi, n=16)
                dur = g.latency_ms / 1000
                attrs: dict[str, Any] = {
                    **common,
                    ga.LF_OBS_TYPE: "generation",
                    "gen_ai.operation.name": "chat",
                    "gen_ai.provider.name": "openai",
                    "gen_ai.request.model": g.model,
                    "langfuse.observation.model.name": g.model,
                    "gen_ai.usage.input_tokens": g.input_tokens,
                    "gen_ai.usage.output_tokens": g.output_tokens,
                    ga.ATLAS_STEP: step,
                    ga.ATLAS_PROMPT_VERSION: result.prompt_version,
                    ga.ATLAS_COST_USD: g.cost_usd,
                    "atlas.latency_ms": round(g.latency_ms, 1),
                    "langfuse.observation.usage_details": json.dumps(
                        {
                            "input": g.input_tokens,
                            "output": g.output_tokens,
                            "cache_read_input_tokens": g.cached_tokens,
                        }
                    ),
                }
                if g.cached_tokens:
                    attrs["gen_ai.usage.cache_read.input_tokens"] = g.cached_tokens
                if g.reasoning_tokens:
                    attrs["gen_ai.usage.reasoning.output_tokens"] = g.reasoning_tokens
                if g.attempt > 1:
                    attrs[ga.ATLAS_RETRIES] = g.attempt - 1
                status = "OK"
                if not g.ok:
                    status = "ERROR"
                    attrs["error.type"] = g.error
                    attrs[ga.LF_OBS_LEVEL] = "ERROR"
                    dur = (
                        self.settings.request_timeout_s
                    )  # a timeout takes the whole timeout budget
                elif g.ttft_ms is not None:
                    attrs["gen_ai.response.time_to_first_chunk"] = round(g.ttft_ms / 1000, 3)
                    attrs[ga.ATLAS_TTFT_MS] = round(g.ttft_ms, 1)
                    if first_token_at is None or gi == len(gens_by_step[step]) - 1:
                        first_token_at = t + g.ttft_ms / 1000
                spans.append(
                    SpanRecord(
                        trace_id,
                        gen_id,
                        f"chat {g.model}",
                        "generation",
                        t,
                        t + dur,
                        step_id,
                        status,
                        attrs,
                        RESOURCE,
                    )
                )
                t += dur
            for ti, tr in enumerate(tools_by_step.get(step, [])):
                lo, hi = TOOL_LATENCY_MS.get(tr.name, (20.0, 80.0))
                dur = (lo + rng.random() * (hi - lo)) / 1000
                if tr.name == "search_knowledge_base":
                    dur += 0.004 * (tr.top_k or 4)  # retrieval time grows with top-k
                attrs = {
                    **common,
                    ga.LF_OBS_TYPE: "retriever" if tr.name == "search_knowledge_base" else "tool",
                    "gen_ai.operation.name": "retrieval"
                    if tr.name == "search_knowledge_base"
                    else "execute_tool",
                    "gen_ai.tool.name": tr.name,
                    "gen_ai.tool.type": "function",
                    "gen_ai.tool.call.id": tr.call_id,
                    # masked like the live path (genai_attrs._safe), then clipped
                    "gen_ai.tool.call.arguments": _masked(tr.arguments, 300),
                    "gen_ai.tool.call.result": _masked(tr.result, 300),
                    "atlas.tool.result_tokens": tr.result_tokens,
                    ga.ATLAS_STEP: step,
                }
                if tr.name == "search_knowledge_base":
                    attrs[ga.ATLAS_RETRIEVAL_TOP_K] = tr.top_k
                    attrs[ga.ATLAS_RETRIEVAL_HITS] = tr.hits
                    attrs[ga.ATLAS_RETRIEVAL_EMPTY] = (tr.hits or 0) == 0
                status = "OK" if tr.ok else "ERROR"
                if not tr.ok:
                    attrs[ga.LF_OBS_LEVEL] = "WARNING"
                    try:
                        attrs["error.type"] = json.loads(tr.result).get("error", "tool_error")
                    except Exception:  # noqa: BLE001
                        attrs["error.type"] = "tool_error"
                spans.append(
                    SpanRecord(
                        trace_id,
                        _hex(trace_id, "tool", step, ti, n=16),
                        f"execute_tool {tr.name}",
                        attrs[ga.LF_OBS_TYPE] if attrs[ga.LF_OBS_TYPE] == "retriever" else "tool",
                        t,
                        t + dur,
                        step_id,
                        status,
                        attrs,
                        RESOURCE,
                    )
                )
                t += dur
            spans.append(
                SpanRecord(
                    trace_id,
                    step_id,
                    f"step {step}",
                    "span",
                    step_start,
                    t,
                    root_id,
                    "OK",
                    {**common, ga.ATLAS_STEP: step, ga.LF_OBS_TYPE: "span"},
                    RESOURCE,
                )
            )
        total_ms = (t - req.ts) * 1000
        root_attrs: dict[str, Any] = {
            **common,
            ga.LF_OBS_TYPE: "agent",
            "gen_ai.operation.name": "invoke_agent",
            "gen_ai.agent.name": "atlas",
            "gen_ai.provider.name": "openai",
            "gen_ai.conversation.id": req.session_id,
            "gen_ai.request.model": result.model,
            "gen_ai.usage.input_tokens": result.input_tokens,
            "gen_ai.usage.output_tokens": result.output_tokens,
            ga.LF_TRACE_TAGS: [
                f"tenant:{req.tenant}",
                f"feature:{result.feature}",
                f"intent:{result.intent}",
                f"prompt:{result.prompt_version}",
            ]
            + ([f"scenario:{req.scenario}"] if req.scenario else []),
            ga.ATLAS_STEPS: result.steps,
            ga.ATLAS_OUTCOME: result.outcome,
            ga.ATLAS_COST_USD: round(result.cost_usd, 8),
            ga.ATLAS_ESCALATED: result.escalated,
            ga.ATLAS_RETRIES: result.retries,
            ga.ATLAS_PROMPT_VERSION: result.prompt_version,
            "atlas.turn": req.turn,
            "atlas.latency_ms": round(total_ms, 1),
            "atlas.tool_calls": list(result.tool_calls),
            # masked exactly like the live path (genai_attrs._safe); the batch judge reads it
            ga.LF_OBS_INPUT: _masked(req.message, 300),
            ga.LF_OBS_OUTPUT: ga._safe(result.answer, True),
        }
        if result.cached_tokens:
            root_attrs["gen_ai.usage.cache_read.input_tokens"] = result.cached_tokens
        if first_token_at is not None:
            root_attrs[ga.ATLAS_TTFT_MS] = round((first_token_at - req.ts) * 1000, 1)
        events = []
        if result.outcome == "step_limit":
            events.append(
                {
                    "name": "step_limit_reached",
                    "time": t,
                    "attributes": {"max_steps": self.settings.max_steps},
                }
            )
        if result.answer and contains_pii(result.answer):
            events.append({"name": "pii_in_output", "time": t, "attributes": {}})
        if result.escalated:
            events.append(
                {
                    "name": "escalation",
                    "time": t,
                    "attributes": {"to_model": self.settings.escalation_model},
                }
            )
        status = "ERROR" if result.outcome == "error" else "OK"
        spans.insert(
            0,
            SpanRecord(
                trace_id,
                root_id,
                "invoke_agent atlas",
                "agent",
                req.ts,
                t,
                None,
                status,
                root_attrs,
                RESOURCE,
                events,
            ),
        )
        return spans

    # ------------------------------------------------------------------ main
    def run(
        self,
        plan: list[PlannedRequest],
        store: LocalSpanStore,
        *,
        judge_rate: float = 0.35,
        feedback_rate: float = 0.12,
        langfuse: bool = False,
    ) -> ReplaySummary:
        from evals.online_judge import OfflineJudge

        started = time.perf_counter()
        judge = OfflineJudge()
        summary = ReplaySummary(seed=self.seed)
        histories: dict[str, list[dict[str, Any]]] = {}
        latencies: list[float] = []
        batch: list[SpanRecord] = []
        lf = None
        if langfuse:
            lf = _langfuse_client()
        for req in plan:
            agent = self._agent(req.params)
            self._now = req.ts
            history = histories.get(req.session_id, [])
            result = agent.run(
                req.message,
                tenant=req.tenant,
                user_id=req.persona.user_id,
                session_id=req.session_id,
                history=history,
                scenario=req.scenario,
                stream=True,
            )
            turn_msgs = (
                result.messages[len(history) + 1 :]
                if result.messages
                else [
                    {"role": "user", "content": req.message},
                    {"role": "assistant", "content": result.answer},
                ]
            )
            histories[req.session_id] = history + [
                m for m in turn_msgs if m.get("role") != "system"
            ]
            spans = self.build_trace(req, result, history)
            batch.extend(spans)
            root = spans[0]
            trace_id = root.trace_id
            latencies.append(root.duration_ms)
            summary.requests += 1
            summary.cost_usd += result.cost_usd
            summary.by_tenant_cost[req.tenant] = (
                summary.by_tenant_cost.get(req.tenant, 0.0) + result.cost_usd
            )
            summary.by_scenario[req.scenario or "none"] = (
                summary.by_scenario.get(req.scenario or "none", 0) + 1
            )
            summary.outcomes[result.outcome] = summary.outcomes.get(result.outcome, 0) + 1
            # judge sample (deterministic by trace id)
            u = int(trace_id[:8], 16) / 0xFFFFFFFF
            end_ts = root.end_time
            if u < judge_rate and result.outcome not in {"guardrail", "refused"}:
                scores = judge.score(
                    question=req.message,
                    answer=result.answer,
                    intent=result.intent,
                    outcome=result.outcome,
                    tool_calls=result.tool_calls,
                    trace_id=trace_id,
                )
                for name, value in scores.items():
                    store.add_score(
                        ScoreRecord(
                            trace_id,
                            f"judge_{name}",
                            value,
                            "judge",
                            "",
                            end_ts + 30,
                            req.tenant,
                            req.session_id,
                        )
                    )
                    summary.scores += 1
                overall = scores["overall"]
            else:
                overall = None
            # feedback: unhappy users click more often
            fb_u = int(trace_id[8:16], 16) / 0xFFFFFFFF
            quality = (
                overall
                if overall is not None
                else judge.score(
                    question=req.message,
                    answer=result.answer,
                    intent=result.intent,
                    outcome=result.outcome,
                    tool_calls=result.tool_calls,
                    trace_id=trace_id,
                )["overall"]
            )
            p_feedback = feedback_rate * (2.2 if quality < 0.6 else 1.0)
            if fb_u < p_feedback and result.outcome not in {"guardrail"}:
                positive = (
                    quality >= 0.6
                    and int(trace_id[16:20], 16) % 10 < 8
                    or quality < 0.6
                    and int(trace_id[16:20], 16) % 10 < 2
                )
                store.add_score(
                    ScoreRecord(
                        trace_id,
                        "user_feedback",
                        1.0 if positive else 0.0,
                        "user",
                        "" if positive else "unhelpful",
                        end_ts + 45,
                        req.tenant,
                        req.session_id,
                    )
                )
                summary.feedback += 1
            if lf is not None:
                _push_langfuse(lf, req, result, trace_id)
            if len(batch) >= 500:
                summary.spans += store.insert(batch)
                batch = []
        summary.spans += store.insert(batch)
        summary.sessions = len({r.session_id for r in plan})
        if latencies:
            from northwind.latency import percentile

            summary.p95_latency_ms = percentile(latencies, 95)
        summary.elapsed_s = time.perf_counter() - started
        if lf is not None:
            lf.flush()
        return summary


def _langfuse_client() -> Any:
    from northwind.config import Settings as _S
    from telemetry.langfuse_setup import init_langfuse

    return init_langfuse(_S.from_env())


def _push_langfuse(lf: Any, req: PlannedRequest, result: AgentResult, trace_id: str) -> None:
    """Mirror a replayed request into Langfuse as agent > generation/tool observations.

    The Langfuse trace uses the **same trace id** as the local store, so ``make judge`` and
    ``make feedback`` scores (``create_score(trace_id=...)``) attach to it, and carries the same
    tags as the stored root span (tenant, feature, intent, prompt version, scenario). Inputs and
    outputs pass through the client's ``mask=langfuse_mask``. Langfuse v4 observations are
    timestamped when created, so replayed traces appear at replay time (durations are preserved
    via explicit ``end_time``).
    """
    from langfuse import propagate_attributes

    now_ns = time.time_ns()
    tags = [
        f"tenant:{req.tenant}",
        f"feature:{result.feature}",
        f"intent:{result.intent}",
        f"prompt:{result.prompt_version}",
        "replay",
    ] + ([f"scenario:{req.scenario}"] if req.scenario else [])
    with propagate_attributes(
        session_id=req.session_id,
        user_id=req.persona.user_id,
        tags=tags,
        trace_name="invoke_agent atlas",
    ):
        root = lf.start_observation(
            trace_context={"trace_id": trace_id},
            name="invoke_agent atlas",
            as_type="agent",
            input=req.message,
            metadata={
                "tenant": req.tenant,
                "feature": result.feature,
                "prompt_version": result.prompt_version,
                "scenario": req.scenario,
                "replay": True,
            },
        )
        try:
            offset = 0
            for g in result.generations:
                gen = root.start_observation(
                    name=f"chat {g.model}",
                    as_type="generation",
                    model=g.model,
                    usage_details={
                        "input": g.input_tokens,
                        "output": g.output_tokens,
                        "cache_read_input_tokens": g.cached_tokens,
                    },
                    cost_details={"total": g.cost_usd},
                    level="ERROR" if not g.ok else None,
                    status_message=g.error,
                )
                offset += int(g.latency_ms * 1_000_000)
                gen.end(end_time=now_ns + offset)
            for tr in result.tools:
                t = root.start_observation(
                    name=f"execute_tool {tr.name}",
                    as_type="retriever" if tr.name == "search_knowledge_base" else "tool",
                    input=tr.arguments,
                    output=tr.result[:500],
                )
                offset += 50_000_000
                t.end(end_time=now_ns + offset)
            root.update(
                output=result.answer,
                metadata={"cost_usd": result.cost_usd, "outcome": result.outcome},
            )
        finally:
            root.end()


def replay_day(
    seed: int = 7,
    *,
    sessions: int = 400,
    incidents: list[Incident] | str | None = None,
    store: LocalSpanStore | None = None,
    judge_rate: float = 0.35,
    feedback_rate: float = 0.12,
    langfuse: bool = False,
    settings: Settings | None = None,
    day: date = DEFAULT_DATE,
) -> tuple[ReplaySummary, LocalSpanStore]:
    """Generate the plan and replay it into ``store`` (new in-memory store if None).

    ``day`` defaults to the course's fixture Monday (2026-09-14); another day gets its own
    session and trace ids, so two days can share one store (drift report ``--prev/--curr``)."""
    if isinstance(incidents, str):
        incidents = INCIDENT_PRESETS[incidents]
    plan = generate_day(seed, sessions=sessions, incidents=incidents or [], day=day)
    store = store or LocalSpanStore(":memory:")
    engine = ReplayEngine(seed, settings)
    summary = engine.run(
        plan, store, judge_rate=judge_rate, feedback_rate=feedback_rate, langfuse=langfuse
    )
    summary.incidents = [
        f"{i.scenario}@{i.start_hour:g}-{i.end_hour:g}h" + (f"[{i.tenant}]" if i.tenant else "")
        for i in (incidents or [])
    ]
    return summary, store


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Replay a day of Atlas traffic offline into the local span store."
    )
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument(
        "--day",
        type=date.fromisoformat,
        default=DEFAULT_DATE,
        help="day to replay, YYYY-MM-DD (default 2026-09-14, the course's fixture Monday)",
    )
    ap.add_argument(
        "--sessions", type=int, default=4000, help="sessions in the day (~2.5 requests each)"
    )
    ap.add_argument(
        "--incidents",
        default=None,
        choices=sorted(INCIDENT_PRESETS),
        help="incident preset (default: ATLAS_SCENARIO if set, else none)",
    )
    ap.add_argument(
        "--store",
        default=None,
        help="SQLite path (default: ATLAS_LOCAL_STORE or .atlas/spans.sqlite)",
    )
    ap.add_argument("--jsonl", default=None, help="also export spans to this JSONL file")
    ap.add_argument("--clear", action="store_true", help="clear the store first")
    ap.add_argument(
        "--langfuse", action="store_true", help="also push traces to Langfuse (needs keys)"
    )
    ap.add_argument("--judge-rate", type=float, default=0.3)
    ap.add_argument("--plan-only", action="store_true", help="print the plan summary and exit")
    args = ap.parse_args(argv)
    settings = Settings.from_env()
    if (
        args.incidents is None
    ):  # `ATLAS_SCENARIO=slow_provider make replay` == `make replay SCENARIO=slow_provider`
        args.incidents = settings.scenario or "none"
    if args.plan_only:
        plan = generate_day(
            args.seed,
            sessions=args.sessions,
            incidents=INCIDENT_PRESETS[args.incidents],
            day=args.day,
        )
        print(json.dumps(summarize_plan(plan), indent=2))
        return 0
    store = LocalSpanStore(args.store or settings.local_store_path)
    if args.clear:
        store.clear()
    summary, _ = replay_day(
        args.seed,
        sessions=args.sessions,
        incidents=args.incidents,
        store=store,
        judge_rate=args.judge_rate,
        langfuse=args.langfuse,
        settings=settings,
        day=args.day,
    )
    if args.jsonl:
        store.export_jsonl(args.jsonl, scores_path=Path(args.jsonl).with_name("scores.jsonl"))
    print(summary.render())
    print(f"Store: {store.path}  (total spans now {store.count()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
