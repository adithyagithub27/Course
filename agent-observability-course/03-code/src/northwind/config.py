"""Environment-driven settings for Atlas.

Everything the course varies from lecture to lecture (models, budgets, sampling
rates, exporters, feature toggles) lives here as a frozen dataclass built from
environment variables, so scripts can say "set ``ATLAS_PROMPT_VERSION=v2``" and
the code path is unambiguous.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields, replace
from typing import Literal

ExporterKind = Literal["console", "otlp", "file", "langfuse", "none", "memory"]
EXPORTER_KINDS: tuple[str, ...] = ("console", "otlp", "file", "langfuse", "none", "memory")

#: The four Northwind departments that act as tenants.
TENANTS: tuple[str, ...] = ("ops", "finance", "hr", "eng")

#: Legacy / long names accepted in the X-Tenant header and mapped to a tenant id.
TENANT_ALIASES: dict[str, str] = {
    "logistics-ops": "ops",
    "logistics": "ops",
    "operations": "ops",
    "warehouse": "ops",
    "engineering": "eng",
    "it": "eng",
    "people": "hr",
    "human-resources": "hr",
    "accounting": "finance",
}

#: Incident scenarios understood by the mock LLM, the tools and the simulator.
SCENARIOS: tuple[str, ...] = (
    "loop",
    "ticket_flaky",
    "context_bloat",
    "retry_storm",
    "slow_provider",
    "prompt_regression",
)


_DOTENV_LOADED = False


def load_dotenv_once() -> str | None:
    """Load ``.env`` from the current directory (or a parent) into ``os.environ``, once.

    Real environment variables always win (``override=False``), so ``make`` flags such as
    ``CACHE=1`` and one-off ``FOO=bar make ...`` prefixes behave as before, and the older
    ``set -a; source .env; set +a`` workaround still works. ``ATLAS_DOTENV=0`` turns it off
    (the test suite does). Returns the loaded path, or None."""
    global _DOTENV_LOADED
    if _DOTENV_LOADED or os.environ.get("ATLAS_DOTENV", "1").strip() == "0":
        return None
    _DOTENV_LOADED = True
    try:
        from dotenv import find_dotenv, load_dotenv
    except ImportError:  # pragma: no cover - python-dotenv is a runtime dependency
        return None
    path = find_dotenv(usecwd=True)
    if path:
        load_dotenv(path, override=False)
        return path
    return None


def normalise_tenant_id(value: str | None) -> str | None:
    """Map header values to a tenant id; unknown values return ``None``."""
    if not value:
        return None
    v = value.strip().lower()
    if v in TENANTS:
        return v
    return TENANT_ALIASES.get(v)


def _truthy(value: str | None, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _float(value: str | None, default: float) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError:
        return default


def _int(value: str | None, default: int) -> int:
    try:
        return int(value) if value not in (None, "") else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """Immutable runtime configuration.

    Build with :meth:`Settings.from_env`; override fields in tests with
    :func:`dataclasses.replace` or :meth:`Settings.with_overrides`.
    """

    # Mode
    offline: bool = True
    scenario: str | None = None

    # Models
    model: str = "gpt-4.1-mini"
    escalation_model: str = "gpt-4.1"
    routing_model: str = "gpt-5-mini"
    judge_model: str = "gpt-4.1-mini"
    degraded_model: str = "gpt-4.1-nano"

    # Agent behaviour
    prompt_version: str = "v1"
    prompt_label: str = "production"
    max_steps: int = 6  # 0 = unlimited: only request_deadline_s stops the loop (Lectures 1.1, 5.6)
    max_tool_retries: int = 0  # 0 = unlimited (the "before" state of Lecture 5.6)
    request_deadline_s: float = 600.0  # whole-request deadline (the gateway's 10-minute timeout)
    mock_latency_scale: float = (
        0.0  # offline: sleep this fraction of simulated latency (live demos)
    )
    stream: bool = True
    retrieval_top_k: int = 4
    kb_min_score: float = 0.5
    prompt_cache: bool = True
    context_diet: bool = True
    router_mode: bool = False
    router_allowed_fails: int = 3  # LiteLLM Router: failures per minute before cooldown
    router_cooldown_s: int = 30  # LiteLLM Router: seconds a failing deployment is skipped
    request_timeout_s: float = 20.0
    max_retries: int = 2
    history_token_budget: int = 8000
    tool_result_token_budget: int = 1400

    # Keys and backends
    openai_api_key: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str = "https://cloud.langfuse.com"
    langfuse_environment: str = "dev"
    langfuse_release: str = "v1.0.0"
    langfuse_sample_rate: float = 1.0
    langsmith_api_key: str | None = None
    langsmith_project: str = "atlas"

    # OpenTelemetry
    otel_exporter: str = "console"
    otel_endpoint: str = "http://localhost:4318/v1/traces"
    service_name: str = "atlas"
    deployment_environment: str = "dev"
    trace_sample_rate: float = 1.0
    judge_sample_rate: float = 0.1
    local_store_path: str = ".atlas/spans.sqlite"
    log_level: str = "INFO"

    # Budgets
    budget_cost_per_session_usd: float = 0.05
    budget_p95_latency_ms: float = 4000.0
    max_input_tokens_per_generation: int = 24_000  # CI gate: one prompt this big = context bloat
    tenant_soft_cap_usd: float = 25.0
    tenant_hard_cap_usd: float = 40.0
    budget_window_s: int = 86_400

    # Per-tenant concurrency (Lecture 7.5): slots sized from the showback share of sessions
    tenant_max_inflight: str = "ops=13,eng=7,finance=6,hr=6,other=2"
    queue_timeout_s: float = 3.0

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        """Read settings from ``env`` (defaults to ``os.environ``, after loading ``.env``)."""
        if env is None:
            load_dotenv_once()
        e = os.environ if env is None else env
        g = e.get
        exporter = (g("OTEL_EXPORTER") or "console").strip().lower()
        if exporter not in EXPORTER_KINDS:
            raise ValueError(
                f"OTEL_EXPORTER={exporter!r} is not one of {', '.join(EXPORTER_KINDS)}"
            )
        scenario = (g("ATLAS_SCENARIO") or "").strip() or None
        if scenario is not None and scenario not in SCENARIOS:
            raise ValueError(f"ATLAS_SCENARIO={scenario!r} is not one of {', '.join(SCENARIOS)}")
        return cls(
            offline=_truthy(g("OFFLINE"), True),
            scenario=scenario,
            model=g("ATLAS_MODEL") or cls.model,
            escalation_model=g("ATLAS_ESCALATION_MODEL") or cls.escalation_model,
            routing_model=g("ATLAS_ROUTING_MODEL") or cls.routing_model,
            judge_model=g("ATLAS_JUDGE_MODEL") or cls.judge_model,
            degraded_model=g("ATLAS_DEGRADED_MODEL") or cls.degraded_model,
            prompt_version=g("ATLAS_PROMPT_VERSION") or cls.prompt_version,
            prompt_label=g("ATLAS_PROMPT_LABEL") or cls.prompt_label,
            max_steps=_int(g("ATLAS_MAX_STEPS"), cls.max_steps),
            max_tool_retries=_int(g("ATLAS_MAX_TOOL_RETRIES"), cls.max_tool_retries),
            request_deadline_s=_float(g("ATLAS_REQUEST_DEADLINE_S"), cls.request_deadline_s),
            mock_latency_scale=_float(g("ATLAS_MOCK_LATENCY_SCALE"), cls.mock_latency_scale),
            stream=_truthy(g("ATLAS_STREAM"), cls.stream),
            retrieval_top_k=_int(g("ATLAS_TOP_K"), cls.retrieval_top_k),
            kb_min_score=_float(g("KB_MIN_SCORE"), cls.kb_min_score),
            prompt_cache=_truthy(g("ATLAS_PROMPT_CACHE"), cls.prompt_cache),
            context_diet=_truthy(g("ATLAS_CONTEXT_DIET"), cls.context_diet),
            router_mode=_truthy(g("ATLAS_ROUTER_MODE"), cls.router_mode),
            router_allowed_fails=_int(g("ATLAS_ROUTER_ALLOWED_FAILS"), cls.router_allowed_fails),
            router_cooldown_s=_int(g("ATLAS_ROUTER_COOLDOWN_S"), cls.router_cooldown_s),
            request_timeout_s=_float(g("ATLAS_REQUEST_TIMEOUT_S"), cls.request_timeout_s),
            max_retries=_int(g("ATLAS_MAX_RETRIES"), cls.max_retries),
            history_token_budget=_int(g("ATLAS_HISTORY_TOKENS"), cls.history_token_budget),
            tool_result_token_budget=_int(
                g("ATLAS_TOOL_RESULT_TOKENS"), cls.tool_result_token_budget
            ),
            openai_api_key=g("OPENAI_API_KEY") or None,
            langfuse_public_key=g("LANGFUSE_PUBLIC_KEY") or None,
            langfuse_secret_key=g("LANGFUSE_SECRET_KEY") or None,
            langfuse_base_url=g("LANGFUSE_BASE_URL") or g("LANGFUSE_HOST") or cls.langfuse_base_url,
            langfuse_environment=g("LANGFUSE_TRACING_ENVIRONMENT") or cls.langfuse_environment,
            langfuse_release=g("LANGFUSE_RELEASE") or cls.langfuse_release,
            langfuse_sample_rate=_float(g("LANGFUSE_SAMPLE_RATE"), cls.langfuse_sample_rate),
            langsmith_api_key=g("LANGSMITH_API_KEY") or None,
            langsmith_project=g("LANGSMITH_PROJECT") or cls.langsmith_project,
            otel_exporter=exporter,
            otel_endpoint=g("OTEL_EXPORTER_OTLP_ENDPOINT") or cls.otel_endpoint,
            service_name=g("OTEL_SERVICE_NAME") or cls.service_name,
            deployment_environment=g("DEPLOYMENT_ENVIRONMENT") or cls.deployment_environment,
            trace_sample_rate=_float(g("TRACE_SAMPLE_RATE"), cls.trace_sample_rate),
            judge_sample_rate=_float(g("JUDGE_SAMPLE_RATE"), cls.judge_sample_rate),
            local_store_path=g("ATLAS_LOCAL_STORE") or cls.local_store_path,
            log_level=(g("LOG_LEVEL") or cls.log_level).upper(),
            budget_cost_per_session_usd=_float(
                g("BUDGET_COST_PER_SESSION_USD"), cls.budget_cost_per_session_usd
            ),
            budget_p95_latency_ms=_float(g("BUDGET_P95_LATENCY_MS"), cls.budget_p95_latency_ms),
            max_input_tokens_per_generation=_int(
                g("BUDGET_MAX_INPUT_TOKENS_PER_GENERATION") or g("MAX_INPUT_TOKENS_PER_GENERATION"),
                cls.max_input_tokens_per_generation,
            ),
            tenant_soft_cap_usd=_float(g("TENANT_SOFT_CAP_USD"), cls.tenant_soft_cap_usd),
            tenant_hard_cap_usd=_float(g("TENANT_HARD_CAP_USD"), cls.tenant_hard_cap_usd),
            budget_window_s=_int(g("BUDGET_WINDOW_S"), cls.budget_window_s),
            tenant_max_inflight=g("ATLAS_TENANT_MAX_INFLIGHT") or cls.tenant_max_inflight,
            queue_timeout_s=_float(g("ATLAS_QUEUE_TIMEOUT_S"), cls.queue_timeout_s),
        )

    def with_overrides(self, **changes: object) -> Settings:
        """Return a copy with the given fields replaced (validates field names)."""
        valid = {f.name for f in fields(self)}
        unknown = set(changes) - valid
        if unknown:
            raise TypeError(f"unknown settings: {sorted(unknown)}")
        return replace(self, **changes)  # type: ignore[arg-type]

    def inflight_limits(self) -> dict[str, int]:
        """``ATLAS_TENANT_MAX_INFLIGHT`` as {tenant: slots}. ``"8"`` gives every tenant 8 slots;
        ``"ops=13,eng=7"`` sets some and leaves the others at the default sizes."""
        defaults = {"ops": 13, "eng": 7, "finance": 6, "hr": 6, "other": 2}
        raw = (self.tenant_max_inflight or "").strip()
        if raw.isdigit():
            return {t: int(raw) for t in defaults}
        out = dict(defaults)
        for part in raw.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                if v.strip().isdigit():
                    out[k.strip()] = max(1, int(v))
        return out

    @property
    def langfuse_enabled(self) -> bool:
        """True when both Langfuse keys are present."""
        return bool(self.langfuse_public_key and self.langfuse_secret_key)

    @property
    def openai_enabled(self) -> bool:
        """True when a real OpenAI call is possible (key present and not offline)."""
        return (not self.offline) and bool(self.openai_api_key)


_SETTINGS: Settings | None = None


def get_settings() -> Settings:
    """Process-wide cached settings (call :func:`reload_settings` after changing env)."""
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings.from_env()
    return _SETTINGS


def reload_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Rebuild the cached settings from ``env`` and return them."""
    global _SETTINGS
    _SETTINGS = Settings.from_env(env)
    return _SETTINGS
