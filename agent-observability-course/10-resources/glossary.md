# Glossary

**Used in:** 1.2, 1.5, 3.1 and throughout. Also the reference spelling list for captions (see `../09-production/qa-checklist.md`).

| Term | Meaning (in this course) | Lecture |
|---|---|---|
| **Agent (observation type)** | Langfuse observation type for a whole agent run; the root of Atlas's trace | 4.1, 4.2 |
| **Atlas** | The course's fictional IT and HR helpdesk agent at Northwind Logistics | 1.4 |
| **Attribute** | A key-value pair on a span; the GenAI semantic conventions define the `gen_ai.*` keys | 3.1, 3.3 |
| **Blast radius** | Which tenants, features, users and sessions an incident affects | 11.1 |
| **Budget (cost)** | A per-tenant spend limit: soft cap (degrade) and hard cap (refuse politely) | 6.7 |
| **Budget gate** | The CI tests (`tests/budget/test_budget_gate.py`, five of them) that replay a day offline and fail a PR if cost per session, p95, a tenant's soft cap, the task-success SLO or input tokens per generation regress | 13.3 |
| **Burn rate** | How fast an error budget is being consumed relative to the SLO window; alerted on with fast and slow windows | 9.1, 9.5 |
| **Cached input tokens** | Input tokens served from the provider's prompt cache, usually cheaper; reported in `prompt_tokens_details.cached_tokens` / `input_tokens_details` | 6.1, 6.4 |
| **Circuit breaker** | Stops calling a failing provider for a cooldown, then probes (half-open) before resuming | 7.4 |
| **Containment** | Share of sessions handled without escalation to a human or a larger model | 9.1 |
| **Context bloat** | The prompt growing every step because history and tool results are re-sent; a cost and latency driver (Incident 1, the `context_bloat` scenario) | 6.5, 11.2 |
| **Context diet** | Trimming history, truncating tool results, summarising and tuning top-k to cut tokens per step | 6.5 |
| **Context propagation** | Carrying the trace context into child calls and async tasks so spans nest correctly | 3.1, 3.6 |
| **Cost per resolved session** | Total cost for a tenant divided by sessions the agent resolved; the manager's number | 6.3, 9.1 |
| **DeepEval / G-Eval** | Evaluation library and its LLM-as-judge method with custom criteria; the course's online judge | 8.2 |
| **Drift** | A change in score, cost or latency distribution between time windows; measured with a PSI-lite comparison | 8.5 |
| **Error budget** | The allowed amount of SLO violation over the window (1 − SLO target) | 9.1 |
| **Escalation model** | The larger model (`gpt-4.1`) Atlas hands hard questions to; traced as a child generation | 5.2, 6.6 |
| **EWMA** | Exponentially weighted moving average; the baseline for cost anomaly detection | 6.7 |
| **Exporter** | The OTel component that ships spans to a backend (console, OTLP, file, Langfuse) | 3.2 |
| **Fallback** | An alternative model or provider used when the primary fails or times out | 7.4 |
| **Feature (tag)** | Which Atlas capability a request used (`atlas.feature`): `policy_question`, `create_ticket`, `ticket_lookup`, `shipment_status`, `password_reset`, `escalation`, `other` | 6.3 |
| **GenAI semantic conventions (semconv)** | OpenTelemetry's incubating attribute and metric names for GenAI operations, models, usage, tools and agents | 3.3 |
| **Generation** | A span/observation for one LLM call, carrying model, usage and cost | 4.1 |
| **Grafana** | Dashboard tool; the Atlas Ops dashboard is `atlas-ops.json` | 9.3 |
| **Guardrail (observation type)** | Langfuse observation type for a safety check, e.g., the injection check with a boolean score | 4.7 |
| **Hard cap / soft cap** | See Budget | 6.7 |
| **Head / tail sampling** | Deciding to keep a trace at the start (SDK `sample_rate`) vs after seeing it (collector, e.g., keep all errors) | 4.6, 13.2 |
| **Incident** | A period where an SLI is out of bounds; the course has three revealed incidents and one unrevealed | 11.x |
| **Judge (online)** | An LLM scoring sampled live traces against criteria; its cost is a line item | 8.2 |
| **Langfuse** | LLM-native tracing backend with scores, prompts and datasets; SDK v4 is OpenTelemetry-based; cloud or self-hosted | 4.1, 13.1 |
| **LangSmith** | LangChain's tracing and evaluation platform; Section 12 alternative | 12.2 |
| **LiteLLM** | Library providing model price tables, cost functions, a Router with fallbacks, and budget concepts | 6.2, 6.6, 7.4 |
| **LLMOps** | Operating LLM applications in production: tracing, quality, cost, reliability, incidents | 1.2 |
| **Local store** | SQLite/JSONL span store used in offline mode and by the Ops Console | 2.4 |
| **Mask function** | The Langfuse `mask=` hook (`langfuse_mask(*, data)`, which calls `mask_value(data, hash_ids=True)`) that replaces PII with `<EMAIL>`-style placeholders or keyed hashes before export; the collector's `attributes/redact` is the second layer | 4.6, 10.2 |
| **Mock LLM** | The deterministic offline model with realistic usage and latency, scenario-aware | 2.4 |
| **Northwind Logistics** | The fictional company; four departments as tenants: `ops`, `finance`, `hr`, `eng` | 1.4 |
| **Observation** | Langfuse's name for a span with a type (agent, tool, generation, retriever, guardrail, chain, embedding) | 4.1 |
| **OFFLINE=1** | Env flag: mock LLM, local store, Ops Console; every lab has this path | 2.4 |
| **OpenInference** | Instrumentation library and convention family from Arize; the course uses its OpenAI instrumentor | 3.5, 12.3 |
| **OpenLLMetry** | Open-source OTel instrumentation for LLM apps (Traceloop); Section 12 alternative | 12.4 |
| **Ops Console** | The course's Streamlit app over the local store (`make console`): Live cost, Cost, Latency, Quality, Budgets, Traffic, Retrieval, Reliability, Safety, Alerts, Traces and Compare replays pages | 2.4, 14.x |
| **OTel Collector** | The OpenTelemetry service that receives, processes (attributes, tail sampling) and exports telemetry to one or more backends | 13.2 |
| **OTLP** | OpenTelemetry's wire protocol for exporting traces, metrics and logs | 3.2 |
| **p50 / p95 / p99** | Median and tail percentiles; budgets and alerts use p95 | 7.1 |
| **Phoenix (Arize)** | Open-source tracing and evaluation backend using OpenInference; Section 12 alternative | 12.3 |
| **Postmortem** | Blameless write-up after an incident with action items mapped to instrumentation, budgets and tests | 11.5 |
| **Prompt caching** | Provider-side reuse of a stable prompt prefix, cheaper and often faster; controlled with `prompt_cache_key` | 6.4 |
| **Prompt label** | Langfuse label (`production`, `staging`) pointing at a prompt version; rollback = move the label | 4.4, 11.4 |
| **Prometheus** | Metrics store; Atlas exposes `/metrics` with counters and histograms | 9.2 |
| **PSI (lite)** | Population stability index, simplified; the drift measure between two windows | 8.5 |
| **Reasoning tokens** | Output tokens spent on reasoning by reasoning models; billed as output | 6.1 |
| **Release** | A version tag on traces (Langfuse `release`) and an annotation on dashboards | 4.1, 9.3, 13.3 |
| **Resource attributes** | Span attributes describing the service (`service.name`, `deployment.environment`) | 3.2 |
| **Retriever (observation type)** | Span/observation for a knowledge-base lookup with query, top-k and scores | 5.3 |
| **Retry storm** | Many retries in a short time after failures; both a latency and a cost event | 7.3, 11.2 |
| **Runbook** | Step-by-step response for one alert, with an owner | 9.5 |
| **Sampling rate** | Fraction of traces (or judged traces) kept | 4.6, 8.2 |
| **Score** | A named value attached to a trace (boolean, numeric, categorical): judge results, feedback, guardrail flags | 4.5 |
| **Session / user / tenant** | Conversation id, pseudonymised person, department: the three slicing dimensions | 4.3 |
| **Showback** | A cost report by tenant and feature that finance accepts | 6.3, 6.9 |
| **SLI / SLO** | Service level indicator (a measured signal) and objective (a target on it over a window) | 9.1 |
| **Span** | One timed operation in a trace, with attributes, events and status | 3.1 |
| **Step (span)** | One iteration of the agent's tool loop | 5.2 |
| **Step limit** | Maximum iterations (`ATLAS_MAX_STEPS`, default 6) before the agent stops with an honest answer; emits a `step_limit_reached` event | 5.2, 5.6 |
| **Swarm** | The traffic simulator driving a running Atlas at configurable RPS (`make swarm RPS=`) with seeds and injectable incidents; `make replay` is its offline, in-process sibling | 1.4 |
| **Tail sampling** | See Head / tail sampling | 13.2 |
| **Tool (observation type)** | Span/observation for a tool call with redacted arguments and result | 5.2 |
| **Trace** | The tree of spans for one run, identified by a trace id | 3.1 |
| **TTFT / TPOT** | Time to first token; time per output token (streaming latency components) | 5.4, 7.2 |
| **Waterfall** | The time-ordered visual of a trace's spans; where you read steps, tokens and time | 5.1 |

### Names to spell correctly in captions

Langfuse · OpenTelemetry · OTel · OTLP · OpenInference · LiteLLM · DeepEval · G-Eval · Prometheus · Grafana · Streamlit · FastAPI · LangSmith · Arize Phoenix · OpenLLMetry · Traceloop · Datadog · Docker Compose · GitHub Actions · GPT-4.1 mini · GPT-4.1 · GPT-5 mini · `gen_ai.*` · `prompt_cache_key` · TTFT · TPOT · p95 · SLI · SLO · EWMA · PSI · Atlas · Northwind Logistics · uv
