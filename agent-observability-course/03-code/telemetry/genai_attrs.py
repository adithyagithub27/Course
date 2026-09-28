"""Helpers that set ``gen_ai.*`` attributes per OpenTelemetry semantic conventions 0.66
(incubating — names may change) plus the ``langfuse.*`` attributes Langfuse reads.

Span naming follows the spec: ``"{operation} {model}"`` for LLM calls,
``"execute_tool {tool}"`` for tools and ``"invoke_agent {agent}"`` for the agent.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from opentelemetry.semconv._incubating.attributes import error_attributes as err
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g
from opentelemetry.trace import Span, Status, StatusCode

from northwind.pii import mask_value
from northwind.pricing import CostBreakdown

# ---- operation names (semconv enum values) -----------------------------------------
OP_CHAT = g.GenAiOperationNameValues.CHAT.value  # "chat"
OP_EXECUTE_TOOL = g.GenAiOperationNameValues.EXECUTE_TOOL.value  # "execute_tool"
OP_INVOKE_AGENT = g.GenAiOperationNameValues.INVOKE_AGENT.value  # "invoke_agent"
OP_RETRIEVAL = g.GenAiOperationNameValues.RETRIEVAL.value  # "retrieval"
PROVIDER_OPENAI = g.GenAiProviderNameValues.OPENAI.value  # "openai"

# ---- Atlas-specific attribute keys (our namespace) ----------------------------------
ATLAS_TENANT = "atlas.tenant"
ATLAS_FEATURE = "atlas.feature"
ATLAS_INTENT = "atlas.intent"
ATLAS_COST_USD = "atlas.cost_usd"
ATLAS_STEP = "atlas.step"
ATLAS_STEPS = "atlas.steps"
ATLAS_OUTCOME = "atlas.outcome"
ATLAS_SCENARIO = "atlas.scenario"
ATLAS_PROMPT_VERSION = "atlas.prompt_version"
ATLAS_ESCALATED = "atlas.escalated"
ATLAS_RETRIES = "atlas.retries"
ATLAS_TTFT_MS = "atlas.ttft_ms"
ATLAS_RETRIEVAL_TOP_K = "atlas.retrieval.top_k"
ATLAS_RETRIEVAL_HITS = "atlas.retrieval.hits"
ATLAS_RETRIEVAL_EMPTY = "atlas.retrieval.empty"
ATLAS_RETRIEVAL_SCORES = "atlas.retrieval.scores"
ATLAS_GUARDRAIL_KIND = "atlas.guardrail.kind"
ATLAS_GUARDRAIL_TRIGGERED = "atlas.guardrail.triggered"
ATLAS_BUDGET_DECISION = "atlas.budget.decision"
ATLAS_JUDGE_SCORE = "atlas.judge.score"

# Langfuse trace-level keys (same as langfuse._client.attributes.LangfuseOtelSpanAttributes)
LF_SESSION_ID = "session.id"
LF_USER_ID = "user.id"
LF_TRACE_TAGS = "langfuse.trace.tags"
LF_TRACE_NAME = "langfuse.trace.name"
LF_OBS_TYPE = "langfuse.observation.type"
LF_OBS_MODEL = "langfuse.observation.model.name"
LF_OBS_USAGE = "langfuse.observation.usage_details"
LF_OBS_COST = "langfuse.observation.cost_details"
LF_OBS_INPUT = "langfuse.observation.input"
LF_OBS_OUTPUT = "langfuse.observation.output"
LF_OBS_COMPLETION_START = "langfuse.observation.completion_start_time"
LF_OBS_LEVEL = "langfuse.observation.level"

MAX_ATTR_CHARS = 4000


def _clip(value: Any, limit: int = MAX_ATTR_CHARS) -> str:
    s = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return s if len(s) <= limit else s[: limit - 12] + "…[clipped]"


def _safe(value: Any, redact: bool) -> str:
    return _clip(mask_value(value, hash_ids=True) if redact else value)


# ---- span names -----------------------------------------------------------------------
def llm_span_name(model: str, operation: str = OP_CHAT) -> str:
    return f"{operation} {model}"


def tool_span_name(tool: str) -> str:
    return f"{OP_EXECUTE_TOOL} {tool}"


def agent_span_name(agent: str = "atlas") -> str:
    return f"{OP_INVOKE_AGENT} {agent}"


# ---- setters --------------------------------------------------------------------------
def set_agent(
    span: Span,
    *,
    name: str = "atlas",
    agent_id: str | None = None,
    conversation_id: str | None = None,
    provider: str = PROVIDER_OPENAI,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, OP_INVOKE_AGENT)
    span.set_attribute(g.GEN_AI_AGENT_NAME, name)
    span.set_attribute(g.GEN_AI_PROVIDER_NAME, provider)
    span.set_attribute(LF_OBS_TYPE, "agent")
    if agent_id:
        span.set_attribute(g.GEN_AI_AGENT_ID, agent_id)
    if conversation_id:
        span.set_attribute(g.GEN_AI_CONVERSATION_ID, conversation_id)
        span.set_attribute(LF_SESSION_ID, conversation_id)


def set_tenant_context(
    span: Span,
    *,
    tenant: str,
    user_id: str | None = None,
    session_id: str | None = None,
    feature: str = "chat",
    intent: str | None = None,
    tags: list[str] | None = None,
) -> None:
    """Business dimensions used for cost attribution and Langfuse filtering."""
    span.set_attribute(ATLAS_TENANT, tenant)
    span.set_attribute(ATLAS_FEATURE, feature)
    if intent:
        span.set_attribute(ATLAS_INTENT, intent)
    if user_id:
        span.set_attribute(LF_USER_ID, user_id)
    if session_id:
        span.set_attribute(LF_SESSION_ID, session_id)
        span.set_attribute(g.GEN_AI_CONVERSATION_ID, session_id)
    span.set_attribute(LF_TRACE_TAGS, list(tags or [f"tenant:{tenant}", f"feature:{feature}"]))


def set_llm_request(
    span: Span,
    *,
    model: str,
    provider: str = PROVIDER_OPENAI,
    operation: str = OP_CHAT,
    temperature: float | None = None,
    max_tokens: int | None = None,
    conversation_id: str | None = None,
    prompt_version: str | None = None,
    prompt_cache_key: str | None = None,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, operation)
    span.set_attribute(g.GEN_AI_PROVIDER_NAME, provider)
    span.set_attribute(g.GEN_AI_REQUEST_MODEL, model)
    span.set_attribute(LF_OBS_TYPE, "generation")
    span.set_attribute(LF_OBS_MODEL, model)
    if temperature is not None:
        span.set_attribute(g.GEN_AI_REQUEST_TEMPERATURE, temperature)
    if max_tokens is not None:
        span.set_attribute(g.GEN_AI_REQUEST_MAX_TOKENS, max_tokens)
    if conversation_id:
        span.set_attribute(g.GEN_AI_CONVERSATION_ID, conversation_id)
    if prompt_version:
        span.set_attribute(ATLAS_PROMPT_VERSION, prompt_version)
    if prompt_cache_key:
        span.set_attribute("openai.request.prompt_cache_key", prompt_cache_key)


def set_llm_messages(
    span: Span, *, input_messages: Any = None, output_message: Any = None, redact: bool = True
) -> None:
    """Record (masked, clipped) messages. Off by default in production; on in demos."""
    if input_messages is not None:
        s = _safe(input_messages, redact)
        span.set_attribute(g.GEN_AI_INPUT_MESSAGES, s)
        span.set_attribute(LF_OBS_INPUT, s)
    if output_message is not None:
        s = _safe(output_message, redact)
        span.set_attribute(g.GEN_AI_OUTPUT_MESSAGES, s)
        span.set_attribute(LF_OBS_OUTPUT, s)


def set_llm_usage(
    span: Span,
    *,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0,
    response_model: str | None = None,
    response_id: str | None = None,
    finish_reasons: list[str] | None = None,
    ttft_s: float | None = None,
    completion_start_time: datetime | None = None,
) -> None:
    span.set_attribute(g.GEN_AI_USAGE_INPUT_TOKENS, int(input_tokens))
    span.set_attribute(g.GEN_AI_USAGE_OUTPUT_TOKENS, int(output_tokens))
    if cached_tokens:
        span.set_attribute(g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, int(cached_tokens))
    if reasoning_tokens:
        span.set_attribute(g.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS, int(reasoning_tokens))
    if response_model:
        span.set_attribute(g.GEN_AI_RESPONSE_MODEL, response_model)
    if response_id:
        span.set_attribute(g.GEN_AI_RESPONSE_ID, response_id)
    if finish_reasons:
        span.set_attribute(g.GEN_AI_RESPONSE_FINISH_REASONS, list(finish_reasons))
    if ttft_s is not None:
        span.set_attribute(g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK, float(ttft_s))
        span.set_attribute(ATLAS_TTFT_MS, float(ttft_s) * 1000.0)
    if completion_start_time is not None:
        span.set_attribute(
            LF_OBS_COMPLETION_START,
            completion_start_time.astimezone(UTC).isoformat(),
        )
    usage: dict[str, int] = {"input": int(input_tokens), "output": int(output_tokens)}
    if cached_tokens:
        usage["cache_read_input_tokens"] = int(cached_tokens)
    if reasoning_tokens:
        usage["reasoning_tokens"] = int(reasoning_tokens)
    span.set_attribute(LF_OBS_USAGE, json.dumps(usage))


def set_cost(span: Span, cost: CostBreakdown) -> None:
    span.set_attribute(ATLAS_COST_USD, float(cost.total_usd))
    span.set_attribute(
        LF_OBS_COST,
        json.dumps(
            {
                "input": float(cost.input_usd),
                "output": float(cost.output_usd),
                "cache_read_input_tokens": float(cost.cached_usd),
                "total": float(cost.total_usd),
            }
        ),
    )


def set_tool(
    span: Span,
    *,
    name: str,
    call_id: str | None = None,
    arguments: Any = None,
    result: Any = None,
    tool_type: str = "function",
    redact: bool = True,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, OP_EXECUTE_TOOL)
    span.set_attribute(g.GEN_AI_TOOL_NAME, name)
    span.set_attribute(g.GEN_AI_TOOL_TYPE, tool_type)
    span.set_attribute(LF_OBS_TYPE, "tool")
    if call_id:
        span.set_attribute(g.GEN_AI_TOOL_CALL_ID, call_id)
    if arguments is not None:
        s = _safe(arguments, redact)
        span.set_attribute(g.GEN_AI_TOOL_CALL_ARGUMENTS, s)
        span.set_attribute(LF_OBS_INPUT, s)
    if result is not None:
        s = _safe(result, redact)
        span.set_attribute(g.GEN_AI_TOOL_CALL_RESULT, s)
        span.set_attribute(LF_OBS_OUTPUT, s)


def set_retrieval(
    span: Span,
    *,
    query: str,
    top_k: int,
    hits: int,
    scores: list[float] | None = None,
    doc_ids: list[str] | None = None,
    redact: bool = True,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, OP_RETRIEVAL)
    span.set_attribute(LF_OBS_TYPE, "retriever")
    span.set_attribute(LF_OBS_INPUT, _safe(query, redact))
    span.set_attribute(ATLAS_RETRIEVAL_TOP_K, int(top_k))
    span.set_attribute(ATLAS_RETRIEVAL_HITS, int(hits))
    span.set_attribute(ATLAS_RETRIEVAL_EMPTY, hits == 0)
    if scores:
        span.set_attribute(ATLAS_RETRIEVAL_SCORES, [round(float(s), 4) for s in scores])
    if doc_ids:
        span.set_attribute(LF_OBS_OUTPUT, json.dumps(doc_ids))


def set_guardrail(span: Span, *, kind: str, triggered: bool, detail: str | None = None) -> None:
    span.set_attribute(LF_OBS_TYPE, "guardrail")
    span.set_attribute(ATLAS_GUARDRAIL_KIND, kind)
    span.set_attribute(ATLAS_GUARDRAIL_TRIGGERED, bool(triggered))
    if detail:
        span.set_attribute(LF_OBS_OUTPUT, _clip(detail))
    if triggered:
        span.set_attribute(LF_OBS_LEVEL, "WARNING")


def set_error(span: Span, exc: BaseException, *, error_type: str | None = None) -> None:
    span.set_attribute(err.ERROR_TYPE, error_type or type(exc).__name__)
    span.set_attribute(LF_OBS_LEVEL, "ERROR")
    span.set_status(Status(StatusCode.ERROR, str(exc)[:200]))
    span.record_exception(exc)


def add_event(span: Span, name: str, **attributes: Any) -> None:
    span.add_event(name, {k: _jsonable(v) for k, v in attributes.items()})


def _jsonable(v: Any) -> Any:
    if isinstance(v, (str, int, float, bool)):
        return v
    return _clip(v, 500)


# ---- convenience names used in the lecture scripts ------------------------------------
def set_agent_attrs(span: Span, **kwargs: Any) -> None:
    """Alias of :func:`set_agent` (agent name, provider, conversation id)."""
    set_agent(span, **kwargs)


def set_llm_attrs(
    span: Span,
    *,
    model: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0,
    response_model: str | None = None,
    ttft_s: float | None = None,
    finish_reasons: list[str] | None = None,
    **request_kwargs: Any,
) -> None:
    """Request + usage attributes in one call (wraps :func:`set_llm_request` and :func:`set_llm_usage`)."""
    set_llm_request(span, model=model, **request_kwargs)
    if input_tokens is not None and output_tokens is not None:
        set_llm_usage(
            span,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            response_model=response_model,
            ttft_s=ttft_s,
            finish_reasons=finish_reasons,
        )


def set_tool_attrs(span: Span, **kwargs: Any) -> None:
    """Alias of :func:`set_tool` (tool name, call id, arguments, result)."""
    set_tool(span, **kwargs)
