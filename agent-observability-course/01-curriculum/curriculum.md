# Curriculum: AI Agent Observability, LLMOps and Cost Control

> **Source of truth.** Every lecture script, lab, quiz, code file and Udemy listing field must match the section numbers, lecture IDs, file names and running example defined here.
>
> **Verified stack (checked against installed packages on 2026-09-28):** Python 3.11+, `langfuse` 4.15 (OpenTelemetry-based SDK), `opentelemetry-sdk` 1.45, `opentelemetry-semantic-conventions` 0.66b0 (GenAI attributes including agent and tool), `openinference-instrumentation-openai` 0.1.61, `langsmith` 0.14, `litellm` 1.103 (price tables, Router, BudgetManager), `openai` 2.54, `deepeval` 4.2, `prometheus-client`, `fastapi`.
>
> **Design principles (from the Course 3 review):** first win inside Section 2, failure-first demos, pause-then-solution challenges, a quiz in every technical section, a student-first capstone gate, a domain-swap project, and a careers lecture. Section 11 (Incident Labs) is the engagement centrepiece: students play detective on real-shaped incidents before the reveal.

---

## 1. Course at a Glance

| Field | Value |
|---|---|
| Working title | AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse |
| Runtime | ≈11 h video (≈660 min) across 15 sections, 92 lectures; ≈12.5 h with quizzes and labs |
| Level | Intermediate. Basic Python and one LLM API call before. Sections 1-3 are beginner-safe. |
| Running example | **"Atlas"**, the internal IT and HR helpdesk agent at **Northwind Logistics** (fictional, 4 departments as tenants). Atlas answers policy questions from a knowledge base, looks up and creates tickets, resets passwords after verification, and checks shipment status. Served over HTTP so traffic can be generated. |
| The twist | A **traffic simulator** ("the swarm") replays a realistic day of multi-tenant load, deterministically, with injectable incidents (runaway loop, context bloat, retry storm, provider slowdown, prompt version regression). Students always have data to look at, even without spending money. |
| Primary tools | Langfuse (tracing, scores, prompts, datasets, dashboards), OpenTelemetry SDK + GenAI semantic conventions, OpenInference auto-instrumentation, LiteLLM (price tables, routing, budgets, gateway), Prometheus + Grafana, DeepEval (online judge) |
| Alternatives covered | LangSmith, Arize Phoenix, OpenLLMetry/Traceloop, Datadog LLM Observability (conceptual) |
| Models (default) | `gpt-4.1-mini` for Atlas, `gpt-4.1` as escalation model, `gpt-5-mini` in routing demos; all via env vars in `src/northwind/config.py` |
| Offline mode | `OFFLINE=1` uses a deterministic mock LLM with realistic token counts and latencies; spans go to a local SQLite/JSONL store and the local Streamlit Ops Console. Every lab has an offline path. |
| Student cost | ≈$5-15 total. Langfuse Cloud free tier (or self-host), OpenAI pay-as-you-go with a cap, everything else open source. |
| Relationship to other courses | Course 4 of Build → Test → Deploy → Operate. Standalone; cross-links to *AI Agent Testing & Evaluation* (offline evals) and *Production Voice AI Agents* (latency budgets). |

### Learning outcomes (Udemy "What you'll learn")

1. Instrument any LLM agent with OpenTelemetry traces that follow the GenAI semantic conventions for models, tools and agents.
2. Use Langfuse to trace sessions, users and tenants, manage prompt versions, score outputs and build datasets from production traffic.
3. Calculate the true cost of every request, session, user and feature, and produce a showback report your finance team accepts.
4. Cut LLM spend with prompt caching, context diets, small-model-first routing and per-tenant budgets, and prove the savings with data.
5. Set latency budgets, measure time to first token and p95, and add timeouts, retries, fallbacks and circuit breakers that hold under provider outages.
6. Run online evaluation on live traffic with sampled LLM-as-judge scoring, user feedback and drift detection.
7. Define SLIs and SLOs for agents, build Grafana and Langfuse dashboards, and write alert rules and runbooks.
8. Mask PII in telemetry, set retention, separate tenants and meet logging obligations.
9. Investigate real-shaped incidents (cost spike, latency regression, quality drift) from traces alone and find root cause.
10. Deploy a self-hosted observability stack with Docker Compose and gate pull requests on cost and latency budgets in CI.

---

## 2. Code Repository Layout (student repo: `agent-observability-course`)

Lives in `agent-observability-course/03-code/`. Scripts and labs must reference these exact paths.

```
03-code/
├── README.md                       # setup, run commands, lecture→file map, offline mode
├── pyproject.toml                  # pinned majors; extras: dev, langsmith, phoenix, dashboards
├── .env.example                    # OPENAI_API_KEY, LANGFUSE_PUBLIC_KEY/SECRET_KEY/BASE_URL, OFFLINE, model env vars
├── Makefile                        # install | run | swarm | replay | console | test | eval | budget-check | lint
├── src/northwind/                  # pure Python, no network, fully unit-tested
│   ├── config.py                   # env-driven settings: models, budgets, sampling rate, OFFLINE
│   ├── pricing.py                  # price table (from litellm.model_cost with a pinned fallback), per-token math incl. cached + reasoning tokens
│   ├── cost.py                     # cost per request/session/user/tenant/feature; showback aggregation
│   ├── budget.py                   # per-tenant budgets, soft/hard caps, spend windows, anomaly detection (z-score / EWMA)
│   ├── tokens.py                   # approximate token counter (no network; tiktoken optional) + context-diet helpers
│   ├── latency.py                  # TTFT/TPOT/total, percentiles, budgets, violations
│   ├── slo.py                      # SLI definitions, error budgets, burn rate
│   ├── sampling.py                 # head/tail sampling policies for traces and judge sampling
│   ├── drift.py                    # window comparison for scores, cost, latency; PSI/Jensen-Shannon lite
│   ├── pii.py                      # mask emails, phones, employee IDs, card numbers in spans
│   ├── report.py                   # weekly ops report (markdown) from aggregated spans
│   └── data/kb/*.md                # Northwind IT/HR knowledge base (VPN, laptop policy, leave, expenses, security, onboarding, payroll dates, ...)
├── app/                            # Atlas agent
│   ├── agent.py                    # tool-calling loop over OpenAI Responses/Chat API, step limits, escalation model
│   ├── tools.py                    # search_knowledge_base, lookup_ticket, create_ticket, reset_password(verify), check_shipment
│   ├── knowledge.py                # BM25-lite retriever over data/kb
│   ├── mock_llm.py                 # deterministic offline LLM with realistic usage + latency; scenario-aware
│   ├── server.py                   # FastAPI: POST /chat, /feedback, /metrics (Prometheus), /healthz; tenant + user headers
│   └── prompts.py                  # Atlas instructions v1, v2 (the regression used in Incident 3)
├── telemetry/
│   ├── otel_setup.py               # TracerProvider, resource attrs, exporters (console | otlp | file | langfuse)
│   ├── genai_attrs.py              # helpers to set gen_ai.* attributes per semconv 0.66 (operation, model, usage, tool, agent)
│   ├── langfuse_setup.py           # get_client(), observe decorators, sessions/users/tags, mask fn, environment/release
│   ├── openinference_setup.py      # OpenAIInstrumentor().instrument(tracer_provider=...)
│   ├── langsmith_setup.py          # traceable + wrap_openai (Section 12)
│   ├── metrics.py                  # Prometheus counters/histograms: tokens, cost, latency, tool errors, budget hits
│   ├── local_store.py              # SQLite/JSONL span store for offline mode and the Ops Console
│   └── logging_setup.py            # structured JSON logs with trace_id correlation
├── simulator/
│   ├── personas.py                 # employees, departments, intents, misbehaviour (injection, rambling)
│   ├── scenarios.py                # a day of traffic; incident injectors: loop, context_bloat, retry_storm, slow_provider, prompt_regression
│   ├── swarm.py                    # drives the FastAPI app at configurable RPS with seeds
│   └── replay.py                   # offline: emit a full day of spans into local store / Langfuse without any LLM calls
├── evals/
│   ├── online_judge.py             # sample traces, DeepEval G-Eval judge, write Langfuse scores
│   ├── feedback.py                 # thumbs up/down → scores; correlate with judge
│   ├── drift_report.py             # weekly window comparison using northwind.drift
│   └── to_dataset.py               # promote bad traces to Langfuse dataset items (feeds Course 2 style offline evals)
├── console/
│   └── ops_console.py              # Streamlit Ops Console over local store: cost, latency, quality, budgets, alerts
├── incidents/
│   ├── incident-01-cost-spike/     # spans.jsonl, brief.md, (solution.md revealed in lecture 11.2)
│   ├── incident-02-latency-regression/
│   └── incident-03-quality-drift/
├── deploy/
│   ├── docker-compose.langfuse.yml # self-hosted Langfuse (verify against current Langfuse compose)
│   ├── docker-compose.observability.yml  # OTel Collector + Prometheus + Grafana
│   ├── otel-collector.yaml
│   ├── grafana/dashboards/atlas-ops.json
│   └── Dockerfile
├── tests/
│   ├── unit/                       # offline, no keys, 150+ tests over src/northwind + simulator + mock_llm
│   ├── integration/                # FastAPI app in OFFLINE mode; span assertions via in-memory exporter
│   └── budget/test_budget_gate.py  # CI gate: replay day, assert cost/session and p95 within budgets
└── .github/workflows/ci.yml        # unit + integration always; budget gate always (offline); live evals when secrets exist
```

---

## 3. Section-by-Section Curriculum

Lecture types: **TH** talking head/avatar, **SL** slides, **SC** screencast/code-along, **DM** live demo, **LAB** guided lab, **QZ** quiz, **AS** assignment, **CH** challenge (pause-then-solution).

### Section 1: Welcome: The $4,000 Weekend (≈36 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 1.1 | The $4,000 weekend: watch an agent burn money in real time | DM | 5 | Hook by contrast. Atlas hits a tool error, retries in a loop, context grows every step; a live cost meter climbs. Then the same run with a step limit, a budget guard and an alert. Promise: by Section 14 you can see, explain and stop this. | `simulator/scenarios.py::loop`, `console/ops_console.py` |
| 1.2 | What LLMOps means for agents (and why MLOps tools miss it) | SL | 8 | Agents are non-deterministic, multi-step, tool-using, token-metered. Three pillars: traces, quality-in-production, cost. Where classic APM stops. | Diagram: pillars |
| 1.3 | The observability stack you will build | SL | 7 | OTel as the wire format, Langfuse as the LLM-native backend, Prometheus/Grafana for metrics, LiteLLM for cost and routing. Portability argument. | Diagram: architecture |
| 1.4 | Meet Atlas and the swarm | SC | 7 | Tour of the agent, tools, tenants, the traffic simulator and offline mode. Why every lab has an offline path. | `app/`, `simulator/` |
| 1.5 | Course roadmap and how to get the most out of it | SC | 6 | Fifteen sections, build log habit, Q&A, version banner (langfuse 4 / otel 1.45). | `03-code/README.md` |
| 1.6 | Quiz: Foundations | QZ | 3 | 6 questions | `06-assessments/quizzes/section-01.md` |

### Section 2: Setup and Your First Trace in 10 Minutes (≈38 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 2.1 | Accounts, keys and spending caps | SC | 7 | Langfuse Cloud free tier (or self-host later), OpenAI project with hard cap, `.env`. Student budget ≈$5-15. | `.env.example`, `10-resources/cost-guide.md` |
| 2.2 | Project setup with uv and the Makefile | SC | 6 | `uv sync`, `make test` green offline, `make run` starts Atlas. | `pyproject.toml`, `Makefile` |
| 2.3 | Quick win: one request, one trace | SC | 8 | `curl` a question to Atlas, open Langfuse, read the trace: agent span, retriever span, generation with usage and cost, tool span. The whole course is explaining and improving this screen. | `app/server.py`, `telemetry/langfuse_setup.py` |
| 2.4 | Offline mode: a full day of traffic for free | SC | 8 | `OFFLINE=1 make replay` fills the local store and Langfuse with a day of spans from the mock LLM; open the Ops Console. | `simulator/replay.py`, `console/ops_console.py` |
| 2.5 | Lab 1: Environment and first trace | LAB | 4 | Checklist plus screenshot of first trace. | `04-labs/lab-01-first-trace.md` |
| 2.6 | Quiz: Setup and tracing basics | QZ | 2 | 5 questions | `06-assessments/quizzes/section-02.md` |

### Section 3: Tracing Fundamentals and the GenAI Semantic Conventions (≈52 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 3.1 | Traces, spans and context in five minutes | SL | 6 | Trace, span, parent/child, attributes, events, status; context propagation; sampling. | Diagram |
| 3.2 | Code-along: manual OpenTelemetry instrumentation of Atlas | SC | 10 | `TracerProvider`, resource attributes (service.name, deployment.environment), `tracer.start_as_current_span`, `ConsoleSpanExporter` then OTLP. | `telemetry/otel_setup.py` |
| 3.3 | GenAI semantic conventions: naming things so tools understand them | SL | 8 | `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens/output_tokens/cache_read`, `gen_ai.tool.name/call.arguments/call.result`, `gen_ai.agent.name`, `gen_ai.conversation.id`; incubating status; why it buys portability. | `telemetry/genai_attrs.py` |
| 3.4 | Code-along: tag every LLM, tool and agent span correctly | SC | 9 | Apply `genai_attrs` helpers in the agent loop and tools; verify in console exporter output. | `app/agent.py`, `telemetry/genai_attrs.py` |
| 3.5 | Auto-instrumentation with OpenInference | SC | 6 | `OpenAIInstrumentor().instrument(tracer_provider=...)`; what you get for free; when manual spans still matter. Note: the otel-contrib OpenAI instrumentor was broken at verification time; we use OpenInference. | `telemetry/openinference_setup.py` |
| 3.6 | Break it: orphan spans, missing context and double counting | DM | 6 | Three broken traces and their fixes: async task without context, tool span outside the agent span, instrumenting twice. | `tests/integration/test_spans.py` |
| 3.7 | Lab 2: Instrument a new tool end to end | LAB | 4 | Add `check_shipment` spans with correct attributes; assert in a test. | `04-labs/lab-02-instrument-tool.md` |
| 3.8 | Quiz: Tracing and semantic conventions | QZ | 3 | 6 questions | `06-assessments/quizzes/section-03.md` |

### Section 4: Langfuse Deep Dive (≈55 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 4.1 | How Langfuse sits on OpenTelemetry | SL | 6 | SDK v4 is an OTel exporter plus semantics: observation types (agent, tool, generation, retriever, guardrail, chain), traces, sessions, users, environments, releases. | Diagram |
| 4.2 | Code-along: `@observe` and observation types | SC | 9 | `observe(as_type="agent" / "tool" / "generation" / "retriever")`, `get_client()`, `update_current_generation(model=, usage_details=, cost_details=)`, `update_current_trace(session_id=, user_id=, tags=, metadata=)`. | `telemetry/langfuse_setup.py`, `app/agent.py` |
| 4.3 | Sessions, users, tenants and tags: slicing production | SC | 7 | Map Northwind departments to tags/metadata, employees to user_id, conversations to session_id. Filtering in the UI. | `app/server.py` |
| 4.4 | Prompt management and versions | SC | 8 | `create_prompt`, labels (production/staging), `get_prompt` with fallback and cache, linking generations to prompt versions. Sets up Incident 3. | `app/prompts.py` |
| 4.5 | Scores, datasets and the feedback loop | SC | 8 | `score_current_trace`, `create_score`, `create_dataset_item(source_trace_id=)`; how production becomes your next regression suite (bridge to Course 2). | `evals/to_dataset.py` |
| 4.6 | Masking, sampling and cost of observability itself | SC | 6 | `mask=` function, `sample_rate`, `blocked_instrumentation_scopes`, `flush()`/`shutdown()` on exit. | `telemetry/langfuse_setup.py`, `src/northwind/pii.py` |
| 4.7 | Challenge: add a guardrail observation | CH | 6 | Spec: wrap the injection check as `as_type="guardrail"` with a boolean score. Pause. Then the solution and the two common mistakes. | `app/agent.py` |
| 4.8 | Quiz: Langfuse | QZ | 5 | 8 questions | `06-assessments/quizzes/section-04.md` |

### Section 5: Agent Observability Patterns (≈48 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 5.1 | What an agent trace must answer | SL | 6 | Why did it call that tool, with what, what came back, how many steps, where did the tokens go, where did time go. | |
| 5.2 | Code-along: tracing the tool loop step by step | SC | 9 | Step spans, tool spans with arguments and results (redacted), step limit as an event, escalation model as a child generation. | `app/agent.py` |
| 5.3 | RAG spans: retrieval quality is a production metric | SC | 7 | Retriever observation with query, top-k, scores; empty-result rate; grounding flag. | `app/knowledge.py` |
| 5.4 | Streaming: time to first token and tokens per second | SC | 7 | Measure TTFT and TPOT from stream events; `gen_ai.response.time_to_first_chunk`; `completion_start_time` in Langfuse. | `app/agent.py`, `src/northwind/latency.py` |
| 5.5 | Logs vs traces vs metrics for agents | SL | 6 | Structured JSON logs with trace_id, when to emit metrics instead of spans, cardinality traps (never a user_id label in Prometheus). | `telemetry/logging_setup.py`, `telemetry/metrics.py` |
| 5.6 | Break it: the loop you can only see in a trace | DM | 6 | Inject the `loop` scenario; read the waterfall; add step limit and error surfacing. | `simulator/scenarios.py` |
| 5.7 | Lab 3: Trace a multi-step ticket escalation | LAB | 4 | Add spans and a test for the escalation path. | `04-labs/lab-03-agent-trace.md` |
| 5.8 | Quiz: Agent patterns | QZ | 3 | 6 questions | `06-assessments/quizzes/section-05.md` |

### Section 6: Cost Engineering (≈70 min) — signature section

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 6.1 | Where the money goes: token anatomy | SL | 7 | Input, output, cached input, reasoning tokens, tool-call overhead, retries, judge calls. Usage fields from the OpenAI API (`prompt_tokens_details.cached_tokens`, `output_tokens_details`). | Diagram |
| 6.2 | Code-along: a price table you can trust | SC | 8 | `litellm.model_cost` with a pinned fallback table, `cost_per_token`, per-model overrides, currency and rounding. | `src/northwind/pricing.py` |
| 6.3 | Cost per request, session, user, tenant and feature | SC | 9 | Attribute cost on every generation, roll up by tags; the showback report finance accepts. | `src/northwind/cost.py`, `src/northwind/report.py` |
| 6.4 | Prompt caching: the cheapest win | SC | 8 | Stable prefixes, `prompt_cache_key`, measuring `cached_tokens`, before/after cost on the same day of traffic. | `app/agent.py` |
| 6.5 | The context diet | SC | 8 | History trimming, tool-result truncation, summarisation, retrieval top-k; measure tokens per step before/after. | `src/northwind/tokens.py` |
| 6.6 | Small-model-first routing with LiteLLM Router | SC | 9 | Router with `gpt-4.1-mini` default and `gpt-4.1` escalation on confidence/complexity; fallbacks; cost impact. | `app/agent.py` (router mode) |
| 6.7 | Budgets and anomaly alerts per tenant | SC | 8 | `BudgetManager` concepts and our own `budget.py`: soft cap (degrade), hard cap (refuse politely), EWMA anomaly detection, Prometheus counter. | `src/northwind/budget.py`, `telemetry/metrics.py` |
| 6.8 | Challenge: cut Atlas's daily cost by 40% | CH | 7 | Replay the day, apply caching + diet + routing, prove the saving in the Ops Console. Pause, then the reference solution. | `simulator/replay.py`, `console/ops_console.py` |
| 6.9 | Project 1: The showback report | AS | 3 | Weekly cost report by tenant and feature with three recommendations. | `05-projects/project-1-showback-report.md` |
| 6.10 | Quiz: Cost engineering | QZ | 3 | 8 questions | `06-assessments/quizzes/section-06.md` |

### Section 7: Latency and Reliability (≈50 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 7.1 | Latency budgets for agents | SL | 7 | Per-step budget, end-to-end budget, p50 vs p95 vs p99, why averages lie. Link to Course 3 voice budgets. | `10-resources/latency-budget-worksheet.md` |
| 7.2 | Code-along: measure TTFT, TPOT and p95 from spans | SC | 8 | Aggregate from the local store; expose Prometheus histograms; Ops Console latency page. | `src/northwind/latency.py`, `telemetry/metrics.py` |
| 7.3 | Timeouts, retries and backoff done right | SC | 8 | Per-call timeouts, bounded retries with jitter, idempotency for tool calls, retry storms as a cost event. | `app/agent.py` |
| 7.4 | Fallbacks and circuit breakers with the Router | SC | 8 | Model and provider fallback lists, cooldowns, half-open probes; what to log when a fallback fires. | `app/agent.py` |
| 7.5 | Rate limits, queues and graceful degradation | SL | 6 | 429 handling, per-tenant concurrency, shedding low-priority traffic, degraded mode messaging. | |
| 7.6 | Chaos demo: slow provider during peak | DM | 7 | Inject `slow_provider`; watch p95, fallback rate and cost; tune and re-run. | `simulator/scenarios.py::slow_provider` |
| 7.7 | Lab 4: Hold p95 under 4 seconds during chaos | LAB | 4 | Tune timeouts and fallbacks until the budget gate passes. | `04-labs/lab-04-latency-chaos.md` |
| 7.8 | Quiz: Latency and reliability | QZ | 2 | 6 questions | `06-assessments/quizzes/section-07.md` |

### Section 8: Quality in Production: Online Evaluation and Drift (≈52 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 8.1 | Offline evals are not enough | SL | 6 | Distribution shift, new intents, prompt and model changes, silent regressions. What "quality in production" means. | |
| 8.2 | Code-along: sampled LLM-as-judge on live traces | SC | 9 | `sampling.py` policies, DeepEval G-Eval with agent-specific criteria (resolved, grounded, safe escalation), scores written back to Langfuse. Cost of judging as a line item. | `evals/online_judge.py` |
| 8.3 | Capturing user feedback that means something | SC | 7 | `/feedback` endpoint, thumbs and reasons, correlation with judge scores, avoiding survivorship bias. | `app/server.py`, `evals/feedback.py` |
| 8.4 | Guardrail and safety metrics | SC | 6 | Injection attempts, refusal rate, PII-in-output rate as time series. | `telemetry/metrics.py` |
| 8.5 | Drift detection: compare this week to last week | SC | 8 | Score, cost and latency windows; PSI-lite; alert thresholds; the weekly drift report. | `src/northwind/drift.py`, `evals/drift_report.py` |
| 8.6 | From bad trace to regression test | SC | 6 | Promote failures to a Langfuse dataset; run Course 2 style offline evals against new prompt versions. | `evals/to_dataset.py` |
| 8.7 | Lab 5: Build the quality page of the Ops Console | LAB | 5 | Judge scores, feedback, drift indicators for a replayed week. | `04-labs/lab-05-online-evals.md` |
| 8.8 | Quiz: Online evaluation | QZ | 5 | 8 questions | `06-assessments/quizzes/section-08.md` |

### Section 9: Dashboards, SLOs and Alerting (≈42 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 9.1 | SLIs for agents that leadership understands | SL | 8 | Task success, containment, tool error rate, p95 latency, cost per resolved session, judge score. Error budgets and burn rate. | `src/northwind/slo.py` |
| 9.2 | Code-along: Prometheus metrics from Atlas | SC | 8 | `/metrics` endpoint, counters and histograms with low-cardinality labels, scraping with the compose stack. | `telemetry/metrics.py`, `deploy/docker-compose.observability.yml` |
| 9.3 | Grafana: the Atlas Ops dashboard | SC | 9 | Import `atlas-ops.json`, panels per SLI, tenant variable, annotations for releases. | `deploy/grafana/dashboards/atlas-ops.json` |
| 9.4 | Langfuse dashboards and saved views | DM | 5 | Cost and score views by tag, session explorer, sharing with stakeholders. | |
| 9.5 | Alert rules and the runbook | SC | 7 | Burn-rate alerts, cost anomaly alert, tool error spike; runbook template; alert fatigue rules. | `10-resources/runbook-template.md` |
| 9.6 | Lab 6: Ship the dashboard and one alert | LAB | 3 | Compose stack up, dashboard live, one alert fires during a replay. | `04-labs/lab-06-dashboards.md` |
| 9.7 | Quiz: SLOs and alerting | QZ | 2 | 6 questions | `06-assessments/quizzes/section-09.md` |

### Section 10: Privacy, Security and Governance of Telemetry (≈32 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 10.1 | Your traces are a data breach waiting to happen | SL | 6 | Prompts contain PII, tool results contain records, judges see everything. Threat model for telemetry. | |
| 10.2 | Code-along: masking in the SDK and the collector | SC | 8 | Langfuse `mask=` function, OTel collector attribute processors, redact tool results, keep hashes for joins. | `src/northwind/pii.py`, `deploy/otel-collector.yaml` |
| 10.3 | Retention, access and tenant separation | SL | 6 | Retention windows, project-per-environment, role-based access, tenant tags vs separate projects. | |
| 10.4 | Regulatory logging obligations (not legal advice) | TH | 6 | EU AI Act record-keeping for high-risk systems, audit trails, what to keep and what never to log. Flag to verify with counsel. | `10-resources/telemetry-governance-checklist.md` |
| 10.5 | Quiz: Governance | QZ | 6 | 6 questions | `06-assessments/quizzes/section-10.md` |

### Section 11: Incident Labs: You Are On Call (≈55 min) — engagement centrepiece

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 11.1 | How to read an incident like an SRE | SL | 6 | Timeline first, then blast radius, then hypothesis, then evidence in traces. The investigation template. | `10-resources/incident-template.md` |
| 11.2 | Incident 1: Monday's cost spike (investigate, then reveal) | CH | 12 | Students get `incident-01` spans and a brief; 8 minutes to find root cause (context bloat plus retry storm on one tenant). Reveal walkthrough. | `incidents/incident-01-cost-spike/` |
| 11.3 | Incident 2: p95 doubled after lunch | CH | 12 | Provider slowdown compounded by retrieval top-k change; fix with fallback and k. | `incidents/incident-02-latency-regression/` |
| 11.4 | Incident 3: users are unhappy but nothing is red | CH | 12 | Prompt version 2 went to production without evals; judge scores drift; roll back via prompt labels. | `incidents/incident-03-quality-drift/` |
| 11.5 | Writing the postmortem | SC | 7 | Blameless postmortem template, action items that map to instrumentation, budgets and tests. | `10-resources/postmortem-template.md` |
| 11.6 | Project 2: Investigate a fourth incident | AS | 3 | An unrevealed incident dataset; submit the postmortem. | `05-projects/project-2-incident-postmortem.md` |
| 11.7 | Quiz: Incident response | QZ | 3 | 6 questions | `06-assessments/quizzes/section-11.md` |

### Section 12: Portability and Alternatives (≈34 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 12.1 | Vendor lock-in and the OTel escape hatch | SL | 6 | Because we emit OTel with GenAI conventions, backends are swappable. What is not portable (scores, prompts, datasets). | |
| 12.2 | Code-along: same Atlas, traced to LangSmith | SC | 8 | `traceable`, `wrap_openai`, feedback API; what differs from Langfuse. | `telemetry/langsmith_setup.py` |
| 12.3 | Arize Phoenix and OpenInference | SC | 7 | Point the OTLP exporter at Phoenix; OpenInference conventions vs GenAI conventions. | `telemetry/otel_setup.py` |
| 12.4 | OpenLLMetry, Datadog and the enterprise APMs | SL | 6 | When your company already has an APM; cost of LLM observability add-ons; hybrid setups. | |
| 12.5 | Decision matrix: choosing your backend | SL | 5 | Control, cost, compliance, features, lock-in. | `10-resources/backend-decision-matrix.md` |
| 12.6 | Quiz: Portability | QZ | 2 | 5 questions | `06-assessments/quizzes/section-12.md` |

### Section 13: Deploying the Stack and CI Budget Gates (≈40 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 13.1 | Self-hosting Langfuse with Docker Compose | SC | 9 | Compose up, env, first project, pointing Atlas at it. Flag: verify against the current Langfuse compose file. | `deploy/docker-compose.langfuse.yml` |
| 13.2 | OTel Collector as the traffic cop | SC | 7 | Receivers, processors (attributes, tail sampling), exporters to two backends at once. | `deploy/otel-collector.yaml` |
| 13.3 | Code-along: the CI budget gate | SC | 9 | `tests/budget/test_budget_gate.py` replays the day offline and fails the PR if cost per session or p95 regress beyond budget; GitHub Actions wiring; release tags in Langfuse. | `.github/workflows/ci.yml` |
| 13.4 | Production readiness checklist for observability | SL | 6 | Sampling in prod, exporter back-pressure, secrets, dashboards as code, alert ownership. | `10-resources/production-checklist.md` |
| 13.5 | Chaos demo: kill the observability backend | DM | 5 | Langfuse down: does Atlas still serve? Exporter timeouts, queue limits, dropping telemetry not requests. | `telemetry/otel_setup.py` |
| 13.6 | Lab 7: Self-hosted stack end to end | LAB | 4 | Langfuse + collector + Grafana running locally, CI gate green. | `04-labs/lab-07-self-host.md` |

### Section 14: Capstone: The Atlas Ops Console (≈55 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 14.1 | Capstone brief and acceptance criteria | SL | 6 | Fully instrumented Atlas, budgets, routing, online judge, dashboards, alerts, CI gate, weekly report. | `05-projects/capstone-atlas-ops.md` |
| 14.1a | Build it yourself first: the capstone gate | TH | 3 | Stop and build from the brief for one week before watching the reference solution. | same |
| 14.2 | Reference solution part A: instrumentation and cost | SC | 12 | Assemble telemetry, pricing, budgets, routing. | `03-code/` |
| 14.3 | Reference solution part B: quality, dashboards, alerts, CI | SC | 12 | Online judge, drift, Grafana, alert rules, budget gate. | `03-code/` |
| 14.4 | The weekly ops report your manager reads | SC | 8 | `report.py` generates a one-page markdown: cost, quality, latency, incidents, recommendations. | `src/northwind/report.py` |
| 14.5 | Capstone submission and portfolio | TH | 5 | Repo, dashboard screenshots, report, postmortems on GitHub and LinkedIn. | `05-projects/capstone-atlas-ops.md` |
| 14.6 | Domain swap: observe a different agent | AS | 4 | Instrument the Course 3 voice agent or a student's own agent with the same stack; adapt SLIs. | `10-resources/instrumentation-template.md` |
| 14.7 | Quiz: Capstone review | QZ | 5 | 6 questions | `06-assessments/quizzes/section-14.md` |

### Section 15: Wrap-up and Careers (≈18 min)

| ID | Lecture | Type | Min | Objective and key points | Code / resource |
|---|---|---|---|---|---|
| 15.1 | What you can now do | TH | 4 | Recap by pillar; the Build → Test → Deploy → Operate path. | |
| 15.2 | Careers: LLMOps, AI platform and AI SRE roles | TH | 8 | Role titles, 12 interview questions with model answers, how to pitch observability to management with an ROI story. No salary figures. | `10-resources/interview-questions.md` |
| 15.3 | Final practice test | QZ | 0 | 40 questions | `06-assessments/practice-test.md` |
| 15.4 | Bonus lecture | TH | 5 | Instructor's other courses and community, per Udemy bonus-lecture rules. Upload last. | |

---

## 4. Runtime Totals

| Section | Minutes |
|---|---|
| 1 Welcome | 36 |
| 2 Setup and first trace | 38 |
| 3 Tracing fundamentals | 52 |
| 4 Langfuse deep dive | 55 |
| 5 Agent patterns | 48 |
| 6 Cost engineering | 70 |
| 7 Latency and reliability | 50 |
| 8 Online evaluation and drift | 52 |
| 9 Dashboards, SLOs, alerting | 42 |
| 10 Governance | 32 |
| 11 Incident labs | 55 |
| 12 Portability | 34 |
| 13 Deploy and CI gates | 40 |
| 14 Capstone | 55 |
| 15 Wrap-up | 18 |
| **Total** | **≈677 min (≈11.3 h incl. quizzes; ≈10.6 h video)** |

Recording note: split 6.3, 6.6, 11.2, 11.3, 11.4, 14.2 and 14.3 into Part A / Part B uploads to keep videos under ten minutes.

## 5. Assessments Summary

| Type | Count | Location |
|---|---|---|
| Quizzes | 13 section quizzes (all technical sections) | `06-assessments/quizzes/` |
| Practice test | 1 × 40 questions | `06-assessments/practice-test.md` |
| Labs | 7 | `04-labs/` |
| Challenges (pause-then-solution) | 5 (4.7, 6.8, 11.2, 11.3, 11.4) | scripts + `05-projects/challenges.md` |
| Projects | 2 + capstone + domain swap | `05-projects/` |
| Coding exercises (Udemy in-browser, stdlib only) | 5: per-token cost, percentile latency, EWMA anomaly, PII masking, context trimming | `06-assessments/coding-exercises.md` |

## 6. Verified API Reference for Writers

Use these exact forms. Verified on the installed versions listed at the top.

```python
# Langfuse 4.x (OpenTelemetry-based)
from langfuse import Langfuse, get_client, observe
lf = Langfuse(public_key=..., secret_key=..., base_url=..., environment="dev", release="v1.2.0",
              sample_rate=1.0, mask=mask_fn, flush_at=..., flush_interval=...)
@observe(as_type="agent")            # also: "tool", "generation", "retriever", "guardrail", "chain", "embedding"
def run_atlas(...): ...
client = get_client()
client.update_current_generation(model=..., usage_details={"input": 1200, "output": 180, "cache_read_input_tokens": 900},
                                 cost_details={"input": 0.00048, "output": 0.000288}, completion_start_time=..., model_parameters={...})
client.update_current_span(metadata=..., level="WARNING", status_message=...)
client.update_current_trace(session_id=..., user_id=..., tags=[...], metadata={...})   # verify exact name on installed SDK
client.score_current_trace(name="resolved", value=1, data_type="BOOLEAN", comment=...)
client.create_score(trace_id=..., name="judge_grounded", value=0.8)
client.create_prompt(name="atlas-system", prompt=..., labels=["production"], type="text")
prompt = client.get_prompt("atlas-system", label="production", fallback=..., cache_ttl_seconds=60)
client.create_dataset(name="atlas-failures"); client.create_dataset_item(dataset_name=..., input=..., expected_output=..., source_trace_id=...)
with client.start_as_current_observation(name="search_knowledge_base", as_type="tool", input=...) as span: span.update(output=...)
client.flush(); client.shutdown()
```

- OpenTelemetry: `from opentelemetry import trace`; `TracerProvider(resource=Resource.create({"service.name": "atlas"}))`; `BatchSpanProcessor(OTLPSpanExporter(endpoint=..., headers=...))` from `opentelemetry.exporter.otlp.proto.http.trace_exporter`; `ConsoleSpanExporter` for demos.
- GenAI semantic conventions: `from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g` then `g.GEN_AI_OPERATION_NAME`, `g.GEN_AI_REQUEST_MODEL`, `g.GEN_AI_RESPONSE_MODEL`, `g.GEN_AI_USAGE_INPUT_TOKENS`, `g.GEN_AI_USAGE_OUTPUT_TOKENS`, `g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS`, `g.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS`, `g.GEN_AI_TOOL_NAME`, `g.GEN_AI_TOOL_CALL_ARGUMENTS`, `g.GEN_AI_TOOL_CALL_RESULT`, `g.GEN_AI_AGENT_NAME`, `g.GEN_AI_CONVERSATION_ID`, `g.GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK`, `g.GEN_AI_PROVIDER_NAME`. Metrics names from `gen_ai_metrics`: `gen_ai.client.operation.duration`, `gen_ai.client.token.usage`, `gen_ai.client.operation.time_to_first_chunk`. Say on screen: "incubating, names may change".
- Auto-instrumentation: `from openinference.instrumentation.openai import OpenAIInstrumentor; OpenAIInstrumentor().instrument(tracer_provider=provider)`. Do **not** teach `opentelemetry-instrumentation-openai-v2` (import error at verification time).
- OpenAI usage fields: Chat `usage.prompt_tokens`, `usage.completion_tokens`, `usage.prompt_tokens_details.cached_tokens`; Responses `usage.input_tokens`, `usage.output_tokens`, `usage.input_tokens_details`, `usage.output_tokens_details`. Caching: `prompt_cache_key` on both APIs.
- LiteLLM: `litellm.model_cost["gpt-4.1-mini"]["input_cost_per_token"]` etc.; `litellm.cost_per_token(model=, prompt_tokens=, completion_tokens=, cache_read_input_tokens=)`; `litellm.completion_cost(completion_response=)`; `Router(model_list=[...], fallbacks=[...], num_retries=..., timeout=..., allowed_fails=..., cooldown_time=...)`; `BudgetManager(project_name=...)` for the concept, our own `budget.py` for tenant caps.
- LangSmith: `from langsmith import traceable, Client; from langsmith.wrappers import wrap_openai`.
- DeepEval: `GEval(name=, criteria=, evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT], threshold=, model=)`, `LLMTestCase(input=, actual_output=, retrieval_context=)`.
- Prometheus: `Counter`, `Histogram` from `prometheus_client`; `make_asgi_app()` mounted at `/metrics`.
- tiktoken needs network to download encodings; `tokens.py` must work without it (approximation) and use it only if the encoding is cached.
