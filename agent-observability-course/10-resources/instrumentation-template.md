# Instrumentation Template: Observe Any Agent with the Course Stack

**Used in:** 3.2 (manual instrumentation), 3.7 (Lab 2), 14.6 (domain swap: observe a different agent), 14.5 (portfolio)

> A checklist and skeleton for taking **any** LLM agent (your own, the Course 3 voice agent, a LangGraph or OpenAI Agents SDK app) and instrumenting it the way Atlas is instrumented: OpenTelemetry spans with the GenAI semantic conventions, exported to Langfuse (and anywhere else), with cost, budgets, latency, online quality and dashboards on top. Work through the phases in order; each one is independently useful. Only API forms from curriculum §6 appear here (verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0; the conventions are incubating, so pin versions).

---

## Phase 0: Know your agent (30 minutes, no code)

| Question | Your answer |
|---|---|
| Framework / loop style (hand-rolled tool loop, LangGraph, OpenAI Agents SDK, voice pipeline, …) | |
| Where does one **run** start and end? (HTTP request, a call turn, a job) | |
| What is a **session**? (conversation id, call id, thread) | |
| What is a **user**? (employee id, caller hash) and how is it pseudonymised? | |
| What is a **tenant** / customer / department? | |
| List every **LLM call site** (model, streaming?, API: Chat or Responses) | |
| List every **tool** (name, arguments, does the result contain PII/records?) | |
| List every **retrieval** step (index, top-k) | |
| What does **"resolved"** mean for a run? (the task-success SLI) | |
| What is the **escalation** path? (bigger model, human) | |
| Which numbers does the owner want weekly? (cost per resolved session by …, p95, quality) | |

## Phase 1: Traces (Section 3)

- [ ] Add `telemetry/otel_setup.py` equivalent: `TracerProvider(resource=Resource.create({"service.name": "<agent>", "deployment.environment": env}))`, `BatchSpanProcessor(OTLPSpanExporter(endpoint=..., headers=...))` from `opentelemetry.exporter.otlp.proto.http.trace_exporter`; `ConsoleSpanExporter` for local checks
- [ ] Wrap **one run** in a root span (`tracer.start_as_current_span("agent <name>")`) and set `g.GEN_AI_AGENT_NAME`, `g.GEN_AI_OPERATION_NAME`, `g.GEN_AI_CONVERSATION_ID`
- [ ] Wrap **each LLM call** in a generation span: `g.GEN_AI_REQUEST_MODEL`, `g.GEN_AI_RESPONSE_MODEL`, `g.GEN_AI_PROVIDER_NAME`, `g.GEN_AI_USAGE_INPUT_TOKENS`, `g.GEN_AI_USAGE_OUTPUT_TOKENS`, `g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS`, `g.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS` (when present), `g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK` (when streaming)
- [ ] Wrap **each tool call** in a tool span: `g.GEN_AI_TOOL_NAME`, `g.GEN_AI_TOOL_CALL_ARGUMENTS` (redacted), `g.GEN_AI_TOOL_CALL_RESULT` (redacted), span status on failure
- [ ] Wrap **retrieval** in a retriever span (query, top-k, scores as attributes)
- [ ] Add a **step** span per loop iteration and an **event** when the step limit is hit
- [ ] Use `OpenAIInstrumentor().instrument(tracer_provider=provider)` from `openinference.instrumentation.openai` for the generation spans if the agent calls OpenAI directly; keep manual spans for agent, tool, retriever and step
- [ ] Async code: propagate context into tasks (the orphan-span failure in 3.6); instrument once (the double-counting failure)
- [ ] **Test:** an in-memory exporter test asserting the span tree and attributes for one run (`tests/integration/test_spans.py` pattern)

## Phase 2: Langfuse semantics (Section 4)

- [ ] `Langfuse(public_key=, secret_key=, base_url=, environment=, release=, sample_rate=, mask=mask_fn)`; `get_client()`
- [ ] `@observe(as_type="agent")` on the run; `"tool"`, `"retriever"`, `"generation"`, `"guardrail"`, `"chain"` where they apply
- [ ] `client.update_current_generation(model=, usage_details={"input":…, "output":…, "cache_read_input_tokens":…}, cost_details={…}, completion_start_time=…)`
- [ ] `with propagate_attributes(session_id=, user_id=, tags=[tenant, feature], metadata={…}):` around the request (langfuse 4.x; there is no `update_current_trace`)
- [ ] Prompts through `client.create_prompt(...)` / `client.get_prompt(name, label="production", fallback=, cache_ttl_seconds=)`, with the version recorded on each generation
- [ ] `client.score_current_trace(...)` for in-process signals (resolved, guardrail flags); `client.create_score(trace_id=, ...)` for out-of-band judges
- [ ] `client.flush(); client.shutdown()` on exit

## Phase 3: Cost (Section 6)

- [ ] Price table: `litellm.model_cost` with a dated fallback; `litellm.cost_per_token(model=, prompt_tokens=, completion_tokens=, cache_read_input_tokens=)`
- [ ] Cost on every generation (`cost_details`), rolled up by request → session → user → tenant → feature (`cost.py` pattern)
- [ ] "Resolved" flag on every run so **cost per resolved session** is computable
- [ ] Prompt prefixes made stable; `prompt_cache_key` set; cached share charted (6.4)
- [ ] Context diet where history is re-sent (6.5)
- [ ] Routing if a smaller default model is viable: `Router(model_list=[...], fallbacks=[...], num_retries=, timeout=, allowed_fails=, cooldown_time=)` (6.6)
- [ ] Per-tenant soft/hard budgets with EWMA anomaly detection and a counter (6.7)
- [ ] Weekly showback (`report.py` pattern)

## Phase 4: Latency and reliability (Section 7)

- [ ] Fill in `latency-budget-worksheet.md` for this agent (a voice agent's budget is ~10× tighter than Atlas's)
- [ ] TTFT / TPOT / end-to-end percentiles from spans; Prometheus `Histogram`s
- [ ] Timeouts, bounded retries with jitter, idempotent tools; retry and fallback **events** on the span
- [ ] Fallback list and circuit breaker; degraded-mode behaviour
- [ ] Chaos: slow or dead provider injected in a test or a staging replay; p95 holds

## Phase 5: Quality in production (Section 8)

- [ ] Sampling policy (`sampling.py` pattern) and a **capped** online judge: `GEval(name=, criteria=, evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT], threshold=, model=)` over `LLMTestCase(input=, actual_output=, retrieval_context=)`; scores written back
- [ ] Domain-specific criteria (for a voice agent: turn-taking handled, booking confirmed, safe transfer; for Atlas: resolved, grounded, safe escalation)
- [ ] Feedback endpoint → scores; correlation with the judge
- [ ] Guardrail metrics as time series
- [ ] Weekly drift report (`drift.py` pattern)
- [ ] Bad trace → `client.create_dataset_item(dataset_name=, input=, expected_output=, source_trace_id=)` → offline eval before prompt promotion

## Phase 6: Dashboards, SLOs, alerts (Section 9)

- [ ] SLIs adapted to the domain (voice: containment, transfer rate, voice-to-voice p95, cost per minute; Atlas: task success, containment, tool error rate, p95, cost per resolved session, judge score)
- [ ] `/metrics` via `make_asgi_app()` with `Counter` / `Histogram` and low-cardinality labels
- [ ] Grafana dashboard JSON in the repo; tenant variable; release annotations
- [ ] Burn-rate, cost-anomaly and tool-error alerts with runbooks (`runbook-template.md`)

## Phase 7: Governance and deployment (Sections 10, 13)

- [ ] Mask in the SDK and in the collector; retention; RBAC; tenant model (`telemetry-governance-checklist.md`)
- [ ] Collector config routing to your backend(s) (13.2)
- [ ] CI budget gate on a deterministic offline replay (13.3). If the agent has no offline mode yet, build a mock model with realistic usage and latency first; it is the single most valuable piece of test infrastructure in this course
- [ ] `production-checklist.md` walked

---

## Skeleton (one run, minimal, all APIs from curriculum §6)

```python
from opentelemetry import trace
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g
from langfuse import get_client, observe

tracer = trace.get_tracer("my_agent")
lf = get_client()

@observe(as_type="agent")
def run(user_msg, *, session_id, user_id, tenant):
    with propagate_attributes(session_id=session_id, user_id=user_id, tags=[tenant]):  # langfuse 4.x: no update_current_trace
        ...
    with tracer.start_as_current_span("agent my_agent") as root:
        root.set_attribute(g.GEN_AI_AGENT_NAME, "my_agent")
        root.set_attribute(g.GEN_AI_CONVERSATION_ID, session_id)
        for step in range(MAX_STEPS):
            with tracer.start_as_current_span(f"step {step}"):
                resp = call_llm(...)            # generation span set inside (model, usage, TTFT)
                if resp.tool_call:
                    with lf.start_as_current_observation(
                        name=resp.tool_call.name, as_type="tool", input=redact(resp.tool_call.args)
                    ) as tool_span:
                        result = tools[resp.tool_call.name](**resp.tool_call.args)
                        tool_span.update(output=redact(result))
                    continue
                lf.score_current_trace(name="resolved", value=1, data_type="BOOLEAN")
                return resp.text
        root.add_event("step_limit_reached")
        lf.score_current_trace(name="resolved", value=0, data_type="BOOLEAN")
        return ESCALATION_MESSAGE
```

The generation helper sets `g.GEN_AI_REQUEST_MODEL`, the usage attributes and `lf.update_current_generation(model=, usage_details=, cost_details=, completion_start_time=)`; see `telemetry/genai_attrs.py` and `app/agent.py` in the course repo for the full form.

## Domain-swap notes (14.6)

| Agent | What changes | What stays |
|---|---|---|
| Course 3 voice agent (Riley) | Session = call; user = caller hash; steps = turns; SLIs = containment, transfer rate, voice-to-voice p95, cost per **minute**; tools = booking; judge criteria = turn-taking, read-back, safe transfer | Every attribute name, the exporter, Langfuse semantics, the price table shape, budgets, alerts, the collector, the CI gate pattern |
| A RAG chatbot | Fewer steps; retrieval quality is the main SLI (empty-result rate, grounding) | Same |
| A batch document agent | Session = document; user = requester; latency budget in minutes, not seconds; cost per document | Same |
| Your own | Fill Phase 0 first | Same |
