"""Atlas: a tool-calling loop with step limits, retries, fallbacks, an escalation
model, streaming TTFT capture, prompt caching and the context diet — every step
traced with GenAI semantic conventions.

Modes:

* **offline** (``OFFLINE=1``): :class:`app.mock_llm.MockLLM`
* **openai**: ``openai.OpenAI().chat.completions.create`` (+ OpenInference auto-spans if enabled)
* **router** (``ATLAS_ROUTER_MODE=1``): LiteLLM ``Router`` with small-model-first and fallbacks

The public entry point is :meth:`AtlasAgent.run`.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol

from opentelemetry import trace as otel_trace

from app.guardrails import injection_check
from app.knowledge import KnowledgeBase, get_kb
from app.mock_llm import (
    SIMPLE_INTENTS,
    MockLLM,
    classify_intent,
    feature_for_intent,
)
from app.prompts import get_system_prompt, prompt_cache_key
from app.tools import TOOL_SCHEMAS, TicketStore, ToolContext, execute_tool
from northwind.budget import BudgetGuard, Decision
from northwind.config import Settings, get_settings
from northwind.pii import contains_pii
from northwind.pricing import CostBreakdown, estimate_cost
from northwind.tokens import (
    approx_tokens,
    context_diet,
    count_message_tokens,
    truncate_tool_result,
)
from telemetry import genai_attrs as ga
from telemetry import metrics
from telemetry.langfuse_setup import trace_attributes
from telemetry.otel_setup import get_tracer

log = logging.getLogger("atlas.agent")

RETRYABLE: tuple[type[BaseException], ...]
try:
    import openai

    RETRYABLE = (
        openai.APITimeoutError,
        openai.RateLimitError,
        openai.APIConnectionError,
        openai.InternalServerError,
    )
except Exception:  # noqa: BLE001 - pragma: no cover
    RETRYABLE = (TimeoutError, ConnectionError)

#: Fallback chain used when a model's circuit is open or retries are exhausted.
FALLBACKS: dict[str, str] = {
    "gpt-4.1-mini": "gpt-4o-mini",
    "gpt-4o-mini": "gpt-4.1",
    "gpt-4.1": "gpt-4.1-mini",
    "gpt-5-mini": "gpt-4.1-mini",
    "gpt-4.1-nano": "gpt-4.1-mini",
}

OUTCOMES: tuple[str, ...] = (
    "resolved",
    "escalated",
    "step_limit",
    "tool_error",
    "error",
    "refused",
    "guardrail",
    "timeout",
)

#: Belt and braces for ``ATLAS_MAX_STEPS=0`` (unlimited): the request deadline normally stops the
#: loop long before this, but a server thread must never spin forever.
UNLIMITED_STEP_CEILING = 2000

ESCALATE_MARKER = "[ESCALATE]"
INJECTION_REFUSAL = (
    "I can't follow instructions embedded in a request that ask me to ignore my rules. "
    "I'm happy to help with IT access, hardware, HR policy, tickets or shipment status."
)
BUDGET_REFUSAL = (
    "Atlas has reached this department's daily AI budget. Please open a ticket in ServiceHub "
    "or try again tomorrow; urgent issues can call extension 4000."
)
TOOL_ERROR_ANSWER = (
    "The {tool} service is not responding right now, so I couldn't finish this. "
    "I've stopped retrying; please try again in a few minutes or reply and I'll open a ticket."
)
STEP_LIMIT_ANSWER = (
    "I wasn't able to complete this automatically. I've noted the details; please open a ticket "
    "in ServiceHub or reply and I'll create one for you."
)
ERROR_ANSWER = "Atlas is temporarily unavailable. Please try again in a minute."
TIMEOUT_ANSWER = (
    "This request took too long and was stopped. Please try again, or open a ticket in ServiceHub."
)


class LLMClient(Protocol):
    def chat(self, **kwargs: Any) -> Any: ...


class OpenAIChatClient:
    """Thin wrapper over ``openai.OpenAI`` so the agent has one ``chat`` signature."""

    def __init__(self, api_key: str | None = None, *, timeout: float = 20.0) -> None:
        import openai as _openai

        from telemetry.langsmith_setup import wrap_openai_if_enabled

        self._client = wrap_openai_if_enabled(
            _openai.OpenAI(api_key=api_key, timeout=timeout, max_retries=0)
        )

    def chat(self, **kwargs: Any) -> Any:
        kwargs.pop("scenario", None)
        if kwargs.get("stream"):
            kwargs.setdefault("stream_options", {"include_usage": True})
        return self._client.chat.completions.create(**kwargs)


def build_router_config(settings: Settings) -> dict[str, Any]:
    """LiteLLM Router kwargs (verified against litellm 1.103): model_list, fallbacks,
    num_retries, timeout, allowed_fails, cooldown_time. Pure data — testable offline."""
    models = sorted(
        {
            settings.model,
            settings.escalation_model,
            settings.routing_model,
            settings.degraded_model,
            "gpt-4o-mini",
        }
    )
    return {
        "model_list": [
            {
                "model_name": m,
                "litellm_params": {"model": f"openai/{m}", "api_key": settings.openai_api_key},
            }
            for m in models
        ],
        "fallbacks": [{m: [FALLBACKS[m]]} for m in models if m in FALLBACKS],
        "num_retries": settings.max_retries,
        "timeout": settings.request_timeout_s,
        "allowed_fails": settings.router_allowed_fails,
        "cooldown_time": settings.router_cooldown_s,
    }


class RouterClient:
    """LiteLLM Router mode (Section 6.6 / 7.4). Imported lazily: LiteLLM is heavy."""

    def __init__(self, settings: Settings) -> None:
        from litellm import Router

        self.router = Router(**build_router_config(settings))

    def chat(self, **kwargs: Any) -> Any:
        kwargs.pop("scenario", None)
        kwargs.pop("prompt_cache_key", None)  # not all providers accept it
        if kwargs.get("stream"):
            kwargs.setdefault("stream_options", {"include_usage": True})
        return self.router.completion(**kwargs)


class CircuitBreaker:
    """Per-model breaker: open after ``threshold`` consecutive failures, half-open after cooldown."""

    def __init__(
        self,
        threshold: int = 3,
        cooldown_s: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.threshold = threshold
        self.cooldown_s = cooldown_s
        self._clock = clock
        self._failures: dict[str, int] = {}
        self._opened_at: dict[str, float] = {}

    def is_open(self, model: str) -> bool:
        opened = self._opened_at.get(model)
        if opened is None:
            return False
        if self._clock() - opened >= self.cooldown_s:
            return False  # half-open: allow a probe
        return True

    def record_failure(self, model: str) -> None:
        n = self._failures.get(model, 0) + 1
        self._failures[model] = n
        if n >= self.threshold:
            self._opened_at[model] = self._clock()

    def record_success(self, model: str) -> None:
        self._failures[model] = 0
        self._opened_at.pop(model, None)

    def state(self, model: str) -> str:
        if model in self._opened_at:
            return "open" if self.is_open(model) else "half-open"
        return "closed"


@dataclass
class GenerationRecord:
    model: str
    step: int
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    ttft_ms: float | None = None
    ok: bool = True
    error: str | None = None
    attempt: int = 1

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ToolRecord:
    name: str
    step: int
    ok: bool
    latency_ms: float
    arguments: str = ""
    result: str = ""
    hits: int | None = None
    top_k: int | None = None
    call_id: str | None = None
    result_tokens: int = 0  # tokens of the result as sent to the model (after the context diet)

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AgentResult:
    answer: str
    trace_id: str
    session_id: str
    model: str
    steps: int
    outcome: str
    intent: str
    feature: str = "chat"
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    ttft_ms: float | None = None
    tool_calls: list[str] = field(default_factory=list)
    escalated: bool = False
    retries: int = 0
    fallbacks: int = 0
    budget_decision: str | None = None
    prompt_version: str = "v1"
    generations: list[GenerationRecord] = field(default_factory=list)
    tools: list[ToolRecord] = field(default_factory=list)
    messages: list[dict[str, Any]] = field(default_factory=list)
    guardrail_triggered: bool = False

    @property
    def model_calls(self) -> int:
        """LLM calls made (one generation span each, retried attempts included)."""
        return len(self.generations)

    @property
    def resolved(self) -> bool:
        return self.outcome == "resolved"

    @property
    def usage(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }


def collect_stream(
    chunks: Iterable[Any], clock: Callable[[], float] = time.monotonic
) -> tuple[dict[str, Any], Any, float | None, str | None, Any]:
    """Consume a chat-completion stream. Returns (message, usage, ttft_s, finish_reason, last_chunk).

    Works for real OpenAI chunks and the mock's typed chunks alike.
    """
    started = clock()
    ttft: float | None = None
    content_parts: list[str] = []
    tool_calls: dict[int, dict[str, Any]] = {}
    usage = None
    finish = None
    last = None
    for ch in chunks:
        last = ch
        if getattr(ch, "usage", None) is not None:
            usage = ch.usage
        if not ch.choices:
            continue
        choice = ch.choices[0]
        delta = choice.delta
        if choice.finish_reason:
            finish = choice.finish_reason
        if delta is None:
            continue
        if delta.content:
            if ttft is None:
                ttft = clock() - started
            content_parts.append(delta.content)
        for tc in delta.tool_calls or []:
            if ttft is None:
                ttft = clock() - started
            idx = getattr(tc, "index", 0) or 0
            slot = tool_calls.setdefault(
                idx, {"id": None, "type": "function", "function": {"name": "", "arguments": ""}}
            )
            if getattr(tc, "id", None):
                slot["id"] = tc.id
            fn = getattr(tc, "function", None)
            if fn is not None:
                if getattr(fn, "name", None):
                    slot["function"]["name"] = fn.name
                if getattr(fn, "arguments", None):
                    slot["function"]["arguments"] += fn.arguments
    message: dict[str, Any] = {"role": "assistant", "content": "".join(content_parts) or None}
    if tool_calls:
        message["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls)]
    return message, usage, ttft, finish, last


def message_from_completion(resp: Any) -> tuple[dict[str, Any], Any, str | None]:
    """Normalise a non-streaming completion (OpenAI or LiteLLM) to a plain message dict."""
    choice = resp.choices[0]
    msg = choice.message
    out: dict[str, Any] = {"role": "assistant", "content": getattr(msg, "content", None)}
    tcs = getattr(msg, "tool_calls", None) or []
    if tcs:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in tcs
        ]
    return out, resp.usage, getattr(choice, "finish_reason", None)


def usage_numbers(usage: Any) -> tuple[int, int, int, int]:
    """(input, output, cached, reasoning) from an OpenAI/LiteLLM usage object or dict."""
    if usage is None:
        return 0, 0, 0, 0

    def g(obj: Any, *names: str) -> int:
        for n in names:
            v = obj.get(n) if isinstance(obj, dict) else getattr(obj, n, None)
            if v is not None:
                return int(v)
        return 0

    def sub(obj: Any, name: str) -> Any:
        return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)

    inp = g(usage, "prompt_tokens", "input_tokens")
    out = g(usage, "completion_tokens", "output_tokens")
    pd = sub(usage, "prompt_tokens_details") or sub(usage, "input_tokens_details")
    cd = sub(usage, "completion_tokens_details") or sub(usage, "output_tokens_details")
    cached = g(pd, "cached_tokens") if pd is not None else 0
    reasoning = g(cd, "reasoning_tokens") if cd is not None else 0
    return inp, out, cached, reasoning


class AtlasAgent:
    """The agent. Construct once per process; ``run`` is safe to call concurrently
    (all per-request state is local)."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        llm: LLMClient | None = None,
        kb: KnowledgeBase | None = None,
        tickets: TicketStore | None = None,
        budget_guard: BudgetGuard | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        tracer: otel_trace.Tracer | None = None,
        capture_content: bool = True,
        on_step: Callable[[int, int, AgentResult], None] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.capture_content = capture_content  # record (masked) messages / tool I/O on spans
        self.kb = kb or get_kb()
        self.tickets = tickets or TicketStore()
        self.budget_guard = budget_guard
        self._clock = clock
        self._sleep = sleep
        self._tracer = tracer
        self.breaker = CircuitBreaker()
        self.on_step = on_step  # progress callback (step, context_tokens, result): loop demo
        self.llm: LLMClient = llm or self._default_llm()

    def _default_llm(self) -> LLMClient:
        s = self.settings
        if s.offline or not s.openai_api_key:
            return MockLLM(seed=7, scenario=s.scenario, latency_scale=s.mock_latency_scale)
        if s.router_mode:
            return RouterClient(s)
        return OpenAIChatClient(s.openai_api_key, timeout=s.request_timeout_s)

    @property
    def tracer(self) -> otel_trace.Tracer:
        return self._tracer or get_tracer()

    # ------------------------------------------------------------------ helpers
    def _choose_deployment(self, intent: str, *, degraded: bool = False) -> str:
        """Small-model-first routing (Section 6.6).

        Without router mode every request uses ``settings.model``. With router mode
        (``ATLAS_ROUTER_MODE=1``) simple intents go to the cheap model and sensitive
        ones to the escalation model; the budget guard's *degrade* decision always wins.
        """
        s = self.settings
        if degraded:
            return s.degraded_model
        if not s.router_mode:
            return s.model
        if intent in SIMPLE_INTENTS:
            return s.degraded_model  # gpt-4.1-nano
        if intent == "escalation":
            return s.escalation_model
        return s.model

    def _cache_key(self, prompt_version: str, tenant: str) -> str | None:
        """``prompt_cache_key`` sent to OpenAI (None when caching is off)."""
        return prompt_cache_key(prompt_version, tenant) if self.settings.prompt_cache else None

    def build_router(self) -> Any:
        """Construct the LiteLLM Router (online) from :func:`build_router_config`."""
        return RouterClient(self.settings)

    def _backoff(self, attempt: int) -> float:
        if self.settings.offline:
            return 0.0
        return min(2.0**attempt * 0.25, 4.0) * (0.5 + 0.5 * (hash(attempt) % 100) / 100)

    def _price(self, model: str, inp: int, out: int, cached: int, reasoning: int) -> CostBreakdown:
        return estimate_cost(model, inp, out, cached_tokens=cached, reasoning_tokens=reasoning)

    def _call_model(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        step: int,
        tenant: str,
        feature: str,
        session_id: str,
        scenario: str | None,
        stream: bool,
        prompt_version: str,
        cache_key: str | None,
        result: AgentResult,
    ) -> tuple[dict[str, Any], str | None, str]:
        """One logical LLM call with bounded retries, fallback and one generation span per attempt.

        Returns (assistant_message, finish_reason, model_used)."""
        attempts = 0
        current = model
        last_exc: BaseException | None = None
        while attempts <= self.settings.max_retries:
            attempts += 1
            if self.breaker.is_open(current) and current in FALLBACKS:
                nxt = FALLBACKS[current]
                metrics.FALLBACKS.labels(current, nxt).inc()
                result.fallbacks += 1
                log.warning("circuit open for %s; falling back to %s", current, nxt)
                current = nxt
            gen = GenerationRecord(model=current, step=step, attempt=attempts)
            with self.tracer.start_as_current_span(ga.llm_span_name(current)) as span:
                ga.set_llm_request(
                    span,
                    model=current,
                    conversation_id=session_id,
                    prompt_version=prompt_version,
                    prompt_cache_key=cache_key,
                )
                span.set_attribute(ga.ATLAS_STEP, step)
                span.set_attribute(ga.ATLAS_TENANT, tenant)
                span.set_attribute(ga.ATLAS_FEATURE, feature)
                span.set_attribute(ga.LF_SESSION_ID, session_id)
                if attempts > 1:
                    span.set_attribute(ga.ATLAS_RETRIES, attempts - 1)
                started = self._clock()
                t0 = datetime.now(UTC)
                try:
                    kwargs: dict[str, Any] = dict(
                        model=current,
                        messages=messages,
                        tools=TOOL_SCHEMAS,
                        stream=stream,
                        scenario=scenario,
                        timeout=self.settings.request_timeout_s,
                    )
                    if cache_key:
                        kwargs["prompt_cache_key"] = cache_key
                    resp = self.llm.chat(**kwargs)
                    if stream:
                        message, usage, ttft_s, finish, last = collect_stream(resp, self._clock)
                        sim_ttft = (
                            getattr(last, "simulated_ttft_ms", None) if last is not None else None
                        )
                        sim_total = (
                            getattr(last, "simulated_latency_ms", None)
                            if last is not None
                            else None
                        )
                    else:
                        message, usage, finish = message_from_completion(resp)
                        ttft_s = None
                        sim_ttft = getattr(resp, "simulated_ttft_ms", None)
                        sim_total = getattr(resp, "simulated_latency_ms", None)
                    elapsed_ms = (self._clock() - started) * 1000.0
                    if sim_total is not None:  # offline: prefer simulated timings
                        elapsed_ms = float(sim_total)
                        ttft_s = float(sim_ttft) / 1000.0 if sim_ttft is not None else ttft_s
                    inp, out, cached, reasoning = usage_numbers(usage)
                    cost = self._price(current, inp, out, cached, reasoning)
                    ga.set_llm_usage(
                        span,
                        input_tokens=inp,
                        output_tokens=out,
                        cached_tokens=cached,
                        reasoning_tokens=reasoning,
                        response_model=getattr(resp, "model", None)
                        if not stream
                        else getattr(last, "model", None),
                        finish_reasons=[finish] if finish else None,
                        ttft_s=ttft_s,
                        completion_start_time=t0 if ttft_s is None else None,
                    )
                    ga.set_cost(span, cost)
                    if self.capture_content:
                        ga.set_llm_messages(
                            span, input_messages=messages[-1:], output_message=message
                        )
                    span.set_attribute("atlas.latency_ms", elapsed_ms)
                    gen.input_tokens, gen.output_tokens, gen.cached_tokens, gen.reasoning_tokens = (
                        inp,
                        out,
                        cached,
                        reasoning,
                    )
                    gen.cost_usd, gen.latency_ms = float(cost.total_usd), elapsed_ms
                    gen.ttft_ms = ttft_s * 1000.0 if ttft_s is not None else None
                    result.generations.append(gen)
                    metrics.record_generation(
                        tenant=tenant,
                        model=current,
                        feature=feature,
                        input_tokens=inp,
                        output_tokens=out,
                        cached_tokens=cached,
                        reasoning_tokens=reasoning,
                        cost_usd=float(cost.total_usd),
                        ttft_s=ttft_s,
                    )
                    self.breaker.record_success(current)
                    return message, finish, current
                except RETRYABLE as exc:
                    last_exc = exc
                    # A timed-out call still cost tokens on the provider side: estimate and record it.
                    inp = count_message_tokens(messages)
                    cost = self._price(current, inp, 0, 0, 0)
                    ga.set_llm_usage(span, input_tokens=inp, output_tokens=0)
                    ga.set_cost(span, cost)
                    ga.set_error(span, exc)
                    gen.ok, gen.error, gen.input_tokens, gen.cost_usd = (
                        False,
                        type(exc).__name__,
                        inp,
                        float(cost.total_usd),
                    )
                    gen.latency_ms = (self._clock() - started) * 1000.0
                    result.generations.append(gen)
                    result.retries += 1
                    metrics.LLM_RETRIES.labels(current, type(exc).__name__).inc()
                    metrics.record_generation(
                        tenant=tenant,
                        model=current,
                        feature=feature,
                        input_tokens=inp,
                        output_tokens=0,
                        cached_tokens=0,
                        reasoning_tokens=0,
                        cost_usd=float(cost.total_usd),
                        ttft_s=None,
                    )
                    self.breaker.record_failure(current)
                    log.warning(
                        "llm call failed (%s) attempt %d/%d",
                        type(exc).__name__,
                        attempts,
                        self.settings.max_retries + 1,
                    )
            self._sleep(self._backoff(attempts))
        raise RuntimeError(f"LLM unavailable after {attempts} attempts") from last_exc

    # ------------------------------------------------------------------ main loop
    def run(
        self,
        message: str,
        *,
        tenant: str,
        user_id: str = "anonymous",
        session_id: str | None = None,
        history: list[dict[str, Any]] | None = None,
        scenario: str | None = None,
        feature: str = "chat",
        stream: bool | None = None,
        model: str | None = None,
    ) -> AgentResult:
        """Answer one user message. Returns an :class:`AgentResult`; never raises for LLM/tool errors."""
        s = self.settings
        session_id = session_id or uuid.uuid4().hex[:16]
        scenario = scenario or s.scenario
        intent = classify_intent(message)
        if feature == "chat":
            feature = feature_for_intent(intent)
        model = model or self._choose_deployment(intent)
        stream = s.stream if stream is None else stream
        top_k = s.retrieval_top_k
        prompt_text, prompt_version = get_system_prompt(
            s.prompt_version, use_langfuse=s.langfuse_enabled, label=s.prompt_label
        )
        cache_key = self._cache_key(prompt_version, tenant)
        tags = [
            f"tenant:{tenant}",
            f"feature:{feature}",
            f"intent:{intent}",
            f"prompt:{prompt_version}",
        ]
        if scenario:
            tags.append(f"scenario:{scenario}")
        started = self._clock()
        result = AgentResult(
            answer="",
            trace_id="",
            session_id=session_id,
            model=model,
            steps=0,
            outcome="resolved",
            intent=intent,
            feature=feature,
            prompt_version=prompt_version,
        )

        with (
            self.tracer.start_as_current_span(ga.agent_span_name("atlas")) as root,
            trace_attributes(
                session_id=session_id,
                user_id=user_id,
                tags=tags,
                metadata={"tenant": tenant, "scenario": scenario},
            ),
        ):
            ctx = root.get_span_context()
            result.trace_id = f"{ctx.trace_id:032x}"
            ga.set_agent(root, conversation_id=session_id)
            ga.set_tenant_context(
                root,
                tenant=tenant,
                user_id=user_id,
                session_id=session_id,
                feature=feature,
                intent=intent,
                tags=tags,
            )
            root.set_attribute(ga.ATLAS_PROMPT_VERSION, prompt_version)
            if self.capture_content:
                root.set_attribute(ga.LF_OBS_INPUT, ga._safe(message, True))
            if scenario:
                root.set_attribute(ga.ATLAS_SCENARIO, scenario)

            # 1. guardrail: prompt injection ------------------------------------------------
            with self.tracer.start_as_current_span("guardrail injection_check") as g:
                check = injection_check(message)
                triggered = check.flagged
                ga.set_guardrail(
                    g,
                    kind="prompt_injection",
                    triggered=triggered,
                    detail=json.dumps(check.as_dict()),
                )
                g.set_attribute("atlas.guardrail.confidence", check.confidence)
            if triggered:
                metrics.GUARDRAIL.labels(tenant, "prompt_injection").inc()
                result.guardrail_triggered = True
                result.answer, result.outcome = INJECTION_REFUSAL, "guardrail"
                return self._finish(root, result, tenant, started)

            # 2. budget guard ----------------------------------------------------------------
            if self.budget_guard is not None:
                decision = self.budget_guard.decide(
                    tenant, time.time(), next_cost_usd=self.budget_guard.estimate(tenant)
                )
                result.budget_decision = decision.decision.value
                root.set_attribute(ga.ATLAS_BUDGET_DECISION, decision.decision.value)
                metrics.BUDGET_DECISIONS.labels(tenant, decision.decision.value).inc()
                metrics.BUDGET_SPENT.labels(tenant).set(decision.spent_usd)
                if decision.decision is Decision.REFUSE:
                    result.answer, result.outcome = BUDGET_REFUSAL, "refused"
                    ga.add_event(root, "budget.refused", reason=decision.reason)
                    return self._finish(root, result, tenant, started)
                if decision.decision is Decision.DEGRADE:
                    ga.add_event(
                        root, "budget.degraded", reason=decision.reason, model=s.degraded_model
                    )
                    model, top_k = self._choose_deployment(intent, degraded=True), min(top_k, 2)
                    result.model = model

            # 3. build context ---------------------------------------------------------------
            messages: list[dict[str, Any]] = [{"role": "system", "content": prompt_text}]
            messages.extend(history or [])
            messages.append({"role": "user", "content": message})
            diet_on = s.context_diet and scenario != "context_bloat"
            if diet_on:
                messages, stats = context_diet(
                    messages,
                    history_budget=s.history_token_budget,
                    tool_result_budget=s.tool_result_token_budget,
                )
                if stats["saved"]:
                    ga.add_event(root, "context.trimmed", **stats)
            tool_ctx = ToolContext(
                kb=self.kb,
                tickets=self.tickets,
                tenant=tenant,
                user_id=user_id,
                top_k=top_k,
                min_score=s.kb_min_score,
                scenario=scenario,
            )

            # 4. the loop ----------------------------------------------------------------------
            try:
                self._loop(
                    messages,
                    model=model,
                    tenant=tenant,
                    feature=feature,
                    session_id=session_id,
                    scenario=scenario,
                    stream=stream,
                    prompt_version=prompt_version,
                    cache_key=cache_key,
                    tool_ctx=tool_ctx,
                    diet_on=diet_on,
                    result=result,
                    root=root,
                    started=started,
                )
            except RuntimeError as exc:
                result.outcome, result.answer = "error", ERROR_ANSWER
                ga.set_error(root, exc)

            # PII in output is a safety metric (Section 8.4)
            if result.answer and contains_pii(result.answer):
                metrics.GUARDRAIL.labels(tenant, "pii_in_output").inc()
                ga.add_event(root, "pii_in_output")
            result.messages = messages
            return self._finish(root, result, tenant, started)

    # ------------------------------------------------------------------ the loop
    def _loop(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str,
        tenant: str,
        feature: str,
        session_id: str,
        scenario: str | None,
        stream: bool,
        prompt_version: str,
        cache_key: str | None,
        tool_ctx: ToolContext,
        diet_on: bool,
        result: AgentResult,
        root: otel_trace.Span,
        started: float | None = None,
    ) -> None:
        """Model -> tools -> model until a final answer, the step limit, a tool-retry limit or the
        request deadline.

        ``max_steps=0`` (``ATLAS_MAX_STEPS=0``) means *unlimited*: the "guards off" run of
        Lectures 1.1 and 5.6, where only the request deadline (``ATLAS_REQUEST_DEADLINE_S``,
        default 600 s, like a gateway timeout) ends the conversation.
        """
        s = self.settings
        tool_failures: dict[str, int] = {}
        unlimited = s.max_steps <= 0
        last_step = UNLIMITED_STEP_CEILING if unlimited else s.max_steps
        started = self._clock() if started is None else started
        for step in range(1, last_step + 1):
            if step > 1 and self._elapsed_ms(result, started) >= s.request_deadline_s * 1000.0:
                result.outcome = "timeout"
                result.answer = TIMEOUT_ANSWER
                ga.add_event(
                    root,
                    "request_deadline_exceeded",
                    deadline_s=s.request_deadline_s,
                    steps=result.steps,
                )
                root.set_attribute("error.type", "deadline_exceeded")
                root.set_attribute(ga.LF_OBS_LEVEL, "WARNING")
                return
            result.steps = step
            with self.tracer.start_as_current_span(f"step {step}") as st:
                st.set_attribute(ga.ATLAS_STEP, step)
                context_tokens = count_message_tokens(messages)
                st.set_attribute("atlas.context_tokens", context_tokens)
                assistant, finish, used_model = self._call_model(
                    model=model,
                    messages=messages,
                    step=step,
                    tenant=tenant,
                    feature=feature,
                    session_id=session_id,
                    scenario=scenario,
                    stream=stream,
                    prompt_version=prompt_version,
                    cache_key=cache_key,
                    result=result,
                )
                result.model = used_model
                if self.on_step is not None:
                    self.on_step(step, context_tokens, result)
                tool_calls = assistant.get("tool_calls") or []
                if not tool_calls:
                    content = assistant.get("content") or ""
                    if (
                        content.startswith(ESCALATE_MARKER)
                        and not result.escalated
                        and used_model != s.escalation_model
                    ):
                        ga.add_event(
                            root,
                            "escalation",
                            to_model=s.escalation_model,
                            reason="model requested human-grade handling",
                        )
                        result.escalated = True
                        esc_msgs = messages + [
                            {
                                "role": "system",
                                "content": "Escalation: handle this sensitive request carefully and offer a confidential HR ticket.",
                            }
                        ]
                        assistant, finish, used_model = self._call_model(
                            model=s.escalation_model,
                            messages=esc_msgs,
                            step=step,
                            tenant=tenant,
                            feature=feature,
                            session_id=session_id,
                            scenario=scenario,
                            stream=stream,
                            prompt_version=prompt_version,
                            cache_key=None,
                            result=result,
                        )
                        result.model = used_model
                        content = (
                            (assistant.get("content") or "").replace(ESCALATE_MARKER, "").strip()
                        )
                        result.outcome = "escalated"
                    result.answer = content
                    messages.append({"role": "assistant", "content": content})
                    return
                messages.append(assistant)
                for tc in tool_calls:
                    tool_msg, ok = self._run_tool(
                        tc, step=step, tool_ctx=tool_ctx, diet_on=diet_on, result=result
                    )
                    messages.append(tool_msg)
                    name = tc["function"]["name"]
                    if not ok:
                        tool_failures[name] = tool_failures.get(name, 0) + 1
                        # ATLAS_MAX_TOOL_RETRIES: surface the error instead of looping (Lecture 5.6 fix)
                        if s.max_tool_retries > 0 and tool_failures[name] > s.max_tool_retries:
                            result.outcome = "tool_error"
                            result.answer = TOOL_ERROR_ANSWER.format(tool=name)
                            ga.add_event(
                                root,
                                "tool_retries_exhausted",
                                tool=name,
                                failures=tool_failures[name],
                                max_tool_retries=s.max_tool_retries,
                            )
                            root.set_attribute(ga.LF_OBS_LEVEL, "WARNING")
                            root.set_attribute("error.type", "tool_retries_exhausted")
                            messages.append({"role": "assistant", "content": result.answer})
                            return
        result.outcome = "step_limit"
        result.answer = STEP_LIMIT_ANSWER
        ga.add_event(root, "step_limit_reached", max_steps=last_step)
        root.set_attribute(ga.LF_OBS_LEVEL, "WARNING")

    def _elapsed_ms(self, result: AgentResult, started: float) -> float:
        """Request time so far: simulated model latency offline, wall clock online."""
        if self.settings.offline:
            return sum(g.latency_ms for g in result.generations)
        return (self._clock() - started) * 1000.0

    def _run_tool(
        self,
        tc: dict[str, Any],
        *,
        step: int,
        tool_ctx: ToolContext,
        diet_on: bool,
        result: AgentResult,
    ) -> tuple[dict[str, Any], bool]:
        """Execute one tool call inside an ``execute_tool <name>`` span; returns (tool message, ok)."""
        name = tc["function"]["name"]
        args = tc["function"]["arguments"]
        result.tool_calls.append(name)
        top_k = tool_ctx.top_k
        with self.tracer.start_as_current_span(ga.tool_span_name(name)) as tspan:
            tspan.set_attribute(ga.ATLAS_TENANT, tool_ctx.tenant)
            t0 = self._clock()
            hits: int | None = None
            used_k: int | None = None
            try:
                tres = execute_tool(name, args, tool_ctx)
                content, ok = tres.content, tres.ok
                ga.set_tool(
                    tspan,
                    name=name,
                    call_id=tc.get("id"),
                    arguments=args if self.capture_content else None,
                    result=content if self.capture_content else None,
                )
                if (
                    name == "search_knowledge_base" and ok
                ):  # a retriever: overrides operation/type, keeps tool.name
                    hits = int(tres.data.get("count", 0))
                    used_k = int(tres.data.get("top_k", top_k))
                    ga.set_retrieval(
                        tspan,
                        query=str(tres.data.get("query", "")),
                        top_k=used_k,
                        hits=hits,
                        scores=[float(r.get("score", 0)) for r in tres.data.get("results", [])],
                        doc_ids=[str(r.get("id")) for r in tres.data.get("results", [])],
                    )
                if not ok:  # a failed tool is a WARNING-level observation with ERROR status
                    err_type = str(tres.data.get("error", "tool_error"))
                    tspan.set_attribute(ga.LF_OBS_LEVEL, "WARNING")
                    tspan.set_attribute("error.type", err_type)
                    tspan.set_status(otel_trace.Status(otel_trace.StatusCode.ERROR, err_type))
            except Exception as exc:  # noqa: BLE001 - unknown tool / bug: surface to the model
                ok = False
                content = json.dumps({"error": "tool_exception", "detail": str(exc)[:200]})
                ga.set_tool(tspan, name=name, call_id=tc.get("id"), arguments=args, result=content)
                ga.set_error(tspan, exc)
            tool_ms = (self._clock() - t0) * 1000.0
            metrics.record_tool(tool=name, ok=ok, latency_s=tool_ms / 1000.0)
            raw = content
            if diet_on:
                content = truncate_tool_result(content, self.settings.tool_result_token_budget)
            result_tokens = approx_tokens(content)
            tspan.set_attribute("atlas.tool.result_tokens", result_tokens)
            result.tools.append(
                ToolRecord(
                    name=name,
                    step=step,
                    ok=ok,
                    latency_ms=tool_ms,
                    arguments=args if isinstance(args, str) else json.dumps(args),
                    result=raw,
                    call_id=tc.get("id"),
                    hits=hits,
                    top_k=used_k,
                    result_tokens=result_tokens,
                )
            )
        return {"role": "tool", "tool_call_id": tc.get("id"), "content": content}, ok

    def _finish(
        self, root: otel_trace.Span, result: AgentResult, tenant: str, started: float
    ) -> AgentResult:
        s = self.settings
        gens = result.generations
        result.input_tokens = sum(g.input_tokens for g in gens)
        result.output_tokens = sum(g.output_tokens for g in gens)
        result.cached_tokens = sum(g.cached_tokens for g in gens)
        result.reasoning_tokens = sum(g.reasoning_tokens for g in gens)
        result.cost_usd = round(sum(g.cost_usd for g in gens), 8)
        simulated = [g.latency_ms for g in gens]
        wall = (self._clock() - started) * 1000.0
        # offline: simulated per-call latencies add up; online: wall clock
        result.latency_ms = round(sum(simulated) if (s.offline and simulated) else wall, 1)
        ttfts = [g.ttft_ms for g in gens if g.ttft_ms is not None and g.ok]
        # TTFT that the user perceives = time until the first token of the *final* answer
        if ttfts:
            result.ttft_ms = (
                round(sum(g.latency_ms for g in gens[:-1]) + ttfts[-1], 1)
                if s.offline
                else round(ttfts[-1], 1)
            )
        root.set_attribute(ga.ATLAS_STEPS, result.steps)
        root.set_attribute(ga.ATLAS_OUTCOME, result.outcome)
        root.set_attribute(ga.ATLAS_COST_USD, result.cost_usd)
        root.set_attribute(ga.ATLAS_ESCALATED, result.escalated)
        root.set_attribute(ga.ATLAS_RETRIES, result.retries)
        root.set_attribute("gen_ai.usage.input_tokens", result.input_tokens)
        root.set_attribute("gen_ai.usage.output_tokens", result.output_tokens)
        if result.cached_tokens:
            root.set_attribute("gen_ai.usage.cache_read.input_tokens", result.cached_tokens)
        root.set_attribute("gen_ai.request.model", result.model)
        root.set_attribute("atlas.latency_ms", result.latency_ms)
        if result.ttft_ms is not None:
            root.set_attribute(ga.ATLAS_TTFT_MS, result.ttft_ms)
        if self.capture_content:
            root.set_attribute(ga.LF_OBS_OUTPUT, ga._safe(result.answer, True))
        root.set_attribute("atlas.tool_calls", list(result.tool_calls))
        if self.budget_guard is not None and result.cost_usd:
            self.budget_guard.record(tenant, result.cost_usd, time.time())
        metrics.record_request(
            tenant=tenant,
            model=result.model,
            outcome=result.outcome,
            latency_s=result.latency_ms / 1000.0,
            steps=result.steps,
            feature=result.feature,
        )
        return result
