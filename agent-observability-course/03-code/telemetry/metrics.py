"""Prometheus metrics for Atlas with **low-cardinality labels only**.

Allowed label names: ``tenant`` (4 values), ``model`` (a handful), ``tool``
(5), ``outcome``, ``kind``, ``decision``, ``feature``, ``name``, ``from_model``,
``to_model``. Never ``user_id``, ``session_id`` or ``trace_id`` — each unique
value creates a new time series and takes Prometheus down (Section 5.5).
"""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, make_asgi_app

#: The only label names any Atlas metric may use.
ALLOWED_LABELS: frozenset[str] = frozenset(
    {
        "tenant",
        "model",
        "tool",
        "outcome",
        "kind",
        "decision",
        "feature",
        "name",
        "from_model",
        "to_model",
        "reason",
        "version",
        "prompt_version",
    }
)
FORBIDDEN_LABELS: frozenset[str] = frozenset({"user_id", "session_id", "trace_id", "user", "email"})

REGISTRY = CollectorRegistry()

LATENCY_BUCKETS = (0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 20.0)
TTFT_BUCKETS = (0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)

REQUESTS = Counter(
    "atlas_requests_total",
    "Chat requests",
    ["tenant", "model", "outcome", "feature"],
    registry=REGISTRY,
)
TOKENS = Counter(
    "atlas_tokens_total",
    "LLM tokens by kind (input|output|cached|reasoning)",
    ["tenant", "model", "kind"],
    registry=REGISTRY,
)
COST = Counter(
    "atlas_cost_usd_total", "LLM cost in USD", ["tenant", "model", "feature"], registry=REGISTRY
)
LATENCY = Histogram(
    "atlas_request_latency_seconds",
    "End-to-end request latency",
    ["tenant", "feature"],
    buckets=LATENCY_BUCKETS,
    registry=REGISTRY,
)
TTFT = Histogram(
    "atlas_ttft_seconds",
    "Time to first token of each generation (one observation per model call)",
    ["model"],
    buckets=TTFT_BUCKETS,
    registry=REGISTRY,
)
STEPS = Histogram(
    "atlas_agent_steps",
    "Tool-loop steps per request",
    ["tenant"],
    buckets=(1, 2, 3, 4, 5, 6, 8, 10),
    registry=REGISTRY,
)
TOOL_CALLS = Counter(
    "atlas_tool_calls_total", "Tool invocations", ["tool", "outcome"], registry=REGISTRY
)
TOOL_LATENCY = Histogram(
    "atlas_tool_latency_seconds",
    "Tool execution time",
    ["tool"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
    registry=REGISTRY,
)
LLM_RETRIES = Counter(
    "atlas_llm_retries_total", "LLM call retries", ["model", "reason"], registry=REGISTRY
)
FALLBACKS = Counter(
    "atlas_model_fallbacks_total",
    "Model fallbacks fired",
    ["from_model", "to_model"],
    registry=REGISTRY,
)
BUDGET_DECISIONS = Counter(
    "atlas_budget_decisions_total",
    "Budget guard decisions",
    ["tenant", "decision"],
    registry=REGISTRY,
)
BUDGET_SPENT = Gauge(
    "atlas_budget_spent_usd", "Rolling-window spend per tenant", ["tenant"], registry=REGISTRY
)
GUARDRAIL = Counter(
    "atlas_guardrail_events_total",
    "Guardrail triggers (injection, pii_in_output, refusal)",
    ["tenant", "kind"],
    registry=REGISTRY,
)
JUDGE_SCORE = Histogram(
    "atlas_judge_score",
    "Online judge scores",
    ["name"],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=REGISTRY,
)
FEEDBACK = Counter(
    "atlas_feedback_total", "User feedback", ["tenant", "outcome"], registry=REGISTRY
)
INFLIGHT = Gauge(
    "atlas_inflight", "Requests holding a tenant concurrency slot", ["tenant"], registry=REGISTRY
)
QUEUE_WAIT = Histogram(
    "atlas_queue_wait_seconds",
    "Time a request waited for its tenant's concurrency slot",
    ["tenant"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0),
    registry=REGISTRY,
)
SHED = Counter(
    "atlas_requests_shed_total",
    "Requests refused with 429 because the tenant's queue wait ran out",
    ["tenant"],
    registry=REGISTRY,
)
EXPORTER_FAILURES = Counter(
    "atlas_telemetry_export_failures_total", "Span export failures", ["name"], registry=REGISTRY
)

BUILD_INFO = Gauge(
    "atlas_build_info",
    "Build / release info (value is always 1)",
    ["version", "model", "prompt_version"],
    registry=REGISTRY,
)

ALL_METRICS = [
    REQUESTS,
    TOKENS,
    COST,
    LATENCY,
    TTFT,
    STEPS,
    TOOL_CALLS,
    TOOL_LATENCY,
    LLM_RETRIES,
    FALLBACKS,
    BUDGET_DECISIONS,
    BUDGET_SPENT,
    GUARDRAIL,
    JUDGE_SCORE,
    FEEDBACK,
    EXPORTER_FAILURES,
    BUILD_INFO,
    INFLIGHT,
    QUEUE_WAIT,
    SHED,
]

# Names used in the lecture scripts (same objects).
FIRST_TOKEN_SECONDS = TTFT
LLM_COST = COST
BUDGET_EVENTS = BUDGET_DECISIONS
GUARDRAIL_EVENTS = GUARDRAIL


def set_build_info(*, version: str, model: str, prompt_version: str) -> None:
    BUILD_INFO.labels(version, model, prompt_version).set(1)


def label_names() -> set[str]:
    """All label names in use (guarded by a unit test against the allowlist)."""
    names: set[str] = set()
    for m in ALL_METRICS:
        names.update(m._labelnames)  # noqa: SLF001 - prometheus_client has no public accessor
    return names


def metrics_app():  # type: ignore[no-untyped-def]
    """ASGI app to mount at ``/metrics``."""
    return make_asgi_app(registry=REGISTRY)


def record_generation(
    *,
    tenant: str,
    model: str,
    feature: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int,
    reasoning_tokens: int,
    cost_usd: float,
    ttft_s: float | None,
) -> None:
    TOKENS.labels(tenant, model, "input").inc(input_tokens)
    TOKENS.labels(tenant, model, "output").inc(output_tokens)
    if cached_tokens:
        TOKENS.labels(tenant, model, "cached").inc(cached_tokens)
    if reasoning_tokens:
        TOKENS.labels(tenant, model, "reasoning").inc(reasoning_tokens)
    COST.labels(tenant, model, feature).inc(cost_usd)
    if ttft_s is not None:
        TTFT.labels(model).observe(ttft_s)


def record_request(
    *,
    tenant: str,
    model: str,
    outcome: str,
    latency_s: float,
    steps: int,
    feature: str = "chat",
) -> None:
    """``feature`` is one of the seven ``app.mock_llm.FEATURES`` values (bounded cardinality)."""
    REQUESTS.labels(tenant, model, outcome, feature).inc()
    LATENCY.labels(tenant, feature).observe(latency_s)
    STEPS.labels(tenant).observe(steps)


def record_tool(*, tool: str, ok: bool, latency_s: float) -> None:
    TOOL_CALLS.labels(tool, "ok" if ok else "error").inc()
    TOOL_LATENCY.labels(tool).observe(latency_s)
