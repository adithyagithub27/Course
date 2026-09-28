# OpenTelemetry GenAI Semantic Conventions Cheat Sheet

**Used in:** 3.3, 3.4, 5.2, 5.4, 12.1, 12.3
**Scope:** only the attributes and metric names verified for the course in curriculum §6 (**`opentelemetry-semantic-conventions` 0.66b0**, imported from `opentelemetry.semconv._incubating`). Anything not on this sheet: check the semantic conventions for your installed version before using it.

> **Incubating: names may change.** These conventions are not stable. Pin the package version, import the **constants** (never hand-type the strings), and re-check this sheet when you bump the version. Say this on screen every time you introduce one (course rule).

---

## 1. Import

```python
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g
from opentelemetry.semconv._incubating.metrics import gen_ai_metrics
```

Use `g.GEN_AI_*` constants in code. The string values shown below are for reading traces in a UI, not for typing into code.

## 2. Verified attributes (curriculum §6)

| Constant | String (as of 0.66b0; verify) | Set on | Meaning (course usage) |
|---|---|---|---|
| `g.GEN_AI_OPERATION_NAME` | `gen_ai.operation.name` | generation, agent, embedding spans | What kind of GenAI operation this span is (e.g., chat, invoke_agent, execute_tool); used by backends to pick a view |
| `g.GEN_AI_PROVIDER_NAME` | `gen_ai.provider.name` | generation | Which provider served the call (e.g., openai) |
| `g.GEN_AI_REQUEST_MODEL` | `gen_ai.request.model` | generation | Model asked for (`gpt-4.1-mini` from `config.py`) |
| `g.GEN_AI_RESPONSE_MODEL` | `gen_ai.response.model` | generation | Model that actually answered (can differ after routing/fallback: record both) |
| `g.GEN_AI_USAGE_INPUT_TOKENS` | `gen_ai.usage.input_tokens` | generation | Total input tokens from the usage object |
| `g.GEN_AI_USAGE_OUTPUT_TOKENS` | `gen_ai.usage.output_tokens` | generation | Output tokens (includes reasoning on reasoning models) |
| `g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS` | `gen_ai.usage.cache_read.input_tokens` | generation | Cached portion of input (from `prompt_tokens_details.cached_tokens` / `input_tokens_details`); needed for a correct price (6.2) |
| `g.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS` | `gen_ai.usage.reasoning.output_tokens` | generation | Reasoning tokens (from `output_tokens_details`); shown separately in token anatomy (6.1) |
| `g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK` | `gen_ai.response.time_to_first_chunk` | generation (streaming) | TTFT in the unit the convention specifies (verify: seconds vs ms) (5.4) |
| `g.GEN_AI_TOOL_NAME` | `gen_ai.tool.name` | tool span | Tool called (`search_knowledge_base`, `lookup_ticket`, `create_ticket`, `reset_password`, `check_shipment`) |
| `g.GEN_AI_TOOL_CALL_ARGUMENTS` | `gen_ai.tool.call.arguments` | tool span | Arguments, **redacted** by `pii.py` before setting (10.2) |
| `g.GEN_AI_TOOL_CALL_RESULT` | `gen_ai.tool.call.result` | tool span | Result, **redacted / truncated** (5.2, 10.2) |
| `g.GEN_AI_AGENT_NAME` | `gen_ai.agent.name` | agent (root) span | `atlas` |
| `g.GEN_AI_CONVERSATION_ID` | `gen_ai.conversation.id` | agent span (and propagated) | The session id; maps to Langfuse `session_id` (4.3) |

**Not on this list = not verified for the course.** In particular, the course does **not** rely on attributes for prompt/completion content; content capture is handled through Langfuse observation input/output with masking, not through GenAI attributes.

## 3. Verified metric names (`gen_ai_metrics`)

| Name | Type | Meaning (course usage) |
|---|---|---|
| `gen_ai.client.operation.duration` | histogram | Duration of a GenAI client operation (a generation) |
| `gen_ai.client.token.usage` | histogram | Token usage per operation (with a token-type dimension) |
| `gen_ai.client.operation.time_to_first_chunk` | histogram | TTFT distribution |

The course exports its **own** Prometheus metrics from `telemetry/metrics.py` (tokens, cost, latency, tool errors, budget hits) with low-cardinality labels; the GenAI metric names above are what auto-instrumentation or a collector may emit and what a backend may expect. Don't put `user_id` on any metric label (5.5).

## 4. Course span layout (which attribute goes where)

```
agent atlas                     GEN_AI_AGENT_NAME, GEN_AI_CONVERSATION_ID, GEN_AI_OPERATION_NAME
├─ step 0                       (course-specific span; event "step_limit_reached" on the last step if hit)
│  ├─ retriever search_kb       (Langfuse as_type="retriever": query, top_k, scores as attributes)
│  ├─ generation gpt-4.1-mini   GEN_AI_OPERATION_NAME, GEN_AI_PROVIDER_NAME, GEN_AI_REQUEST_MODEL, GEN_AI_RESPONSE_MODEL,
│  │                            GEN_AI_USAGE_INPUT_TOKENS, GEN_AI_USAGE_OUTPUT_TOKENS, GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS,
│  │                            GEN_AI_USAGE_REASONING_OUTPUT_TOKENS (if any), GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK (if streaming)
│  └─ tool lookup_ticket        GEN_AI_TOOL_NAME, GEN_AI_TOOL_CALL_ARGUMENTS (redacted), GEN_AI_TOOL_CALL_RESULT (redacted), status
├─ step 1
│  └─ generation gpt-4.1        (escalation model as a child generation, 5.2)
└─ guardrail injection_check    (Langfuse as_type="guardrail", boolean score, 4.7)
```

Resource attributes (not GenAI, but required): `service.name="atlas"`, `deployment.environment` (3.2).

## 5. Mapping OpenAI usage fields → attributes (6.1)

| OpenAI field | Attribute |
|---|---|
| Chat `usage.prompt_tokens` / Responses `usage.input_tokens` | `GEN_AI_USAGE_INPUT_TOKENS` |
| Chat `usage.completion_tokens` / Responses `usage.output_tokens` | `GEN_AI_USAGE_OUTPUT_TOKENS` |
| Chat `usage.prompt_tokens_details.cached_tokens` / Responses `usage.input_tokens_details` (cached) | `GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS` |
| Responses `usage.output_tokens_details` (reasoning) | `GEN_AI_USAGE_REASONING_OUTPUT_TOKENS` |
| First stream event timestamp − request start | `GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK` (and Langfuse `completion_start_time`) |

`telemetry/genai_attrs.py` does this mapping; call its helpers rather than repeating it.

## 6. Auto-instrumentation

```python
from openinference.instrumentation.openai import OpenAIInstrumentor
OpenAIInstrumentor().instrument(tracer_provider=provider)
```

OpenInference emits its **own** convention family (`openinference.*` / `llm.*` style attributes) alongside or instead of `gen_ai.*`, depending on version; Phoenix reads it natively (12.3) and Langfuse maps it. **Do not** teach `opentelemetry-instrumentation-openai-v2` (import error at verification time; re-check on upgrades). Manual spans for agent, tool, retriever and step are still yours.

## 7. Portability notes (12.1)

- Traces carrying these attributes render as generations/tools/agents in Langfuse, Phoenix and (with mapping) LangSmith and Datadog; verify each backend's current mapping.
- Scores, prompts, datasets and dashboards are **not** described by these conventions and are not portable.
- When the conventions graduate from incubating, expect renames; the constants make that a version bump, and this sheet gets a new date.
