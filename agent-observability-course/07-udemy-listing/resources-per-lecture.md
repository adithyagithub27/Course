# Resources per Lecture

> What to attach to each lecture in Udemy's **Resources** panel (downloadable file or external resource link). Paths are relative to `agent-observability-course/`. Code paths in `03-code/` are published in the student repo `agent-observability-course`.

## How to attach

- **Downloadable files:** export each `10-resources/*.md` to **PDF** (keep the .md too if you like). Students expect PDFs, and PDFs are accessible offline. Name them `S{section}-{slug}.pdf`, e.g., `S07-latency-budget-worksheet.pdf`.
- **Code:** attach a **link to the exact repo folder or file** (external resource link) where Udemy allows it for required learning materials (verify current external-link rules). Where a link isn't allowed, attach a ZIP of the relevant `03-code/` folder at the tagged version.
- **Repo version:** tag the repo per section (`s03`, `s06`...) so links point at code that matches the video. After a dependency update, update the tag and send an educational announcement.
- **Incident datasets:** attach `spans.jsonl` and `brief.md` only. **Never attach `solution.md` to the investigation lecture (Part A).** Attach it to the reveal (Part B) or reference the repo tag that includes it. The fourth incident (Project 2) has no solution in the public repo.
- **Quizzes, assignments, practice test and coding exercises** are Udemy-native items built from the listed source files. They aren't downloads.
- **No promotional links** in any resource except the bonus lecture 15.4 (see `publish-checklist.md` §9).
- **Part A / Part B uploads** (6.3, 6.6, 11.2, 11.3, 11.4, 14.2, 14.3): attach the resources to **Part A** and add "Resources are attached to Part A" to the Part B description, except incident solutions (Part B only).

## Lecture → resource map

### Section 1

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 1.1 | The $4,000 weekend | DM | `simulator/scenarios.py::loop`, `console/ops_console.py` | none | None (video only); code appears again in 5.6 |
| 1.2 | What LLMOps means for agents | SL | Diagram: three pillars (D1) | `10-resources/glossary.md` | Diagram PNG/PDF from slide deck + PDF download |
| 1.3 | The observability stack you will build | SL | Diagram: architecture (D2) | `10-resources/backend-decision-matrix.md` (preview) | Diagram PNG/PDF from slide deck |
| 1.4 | Meet Atlas and the swarm | SC | `app/`, `simulator/` | Course repo link | Repo link to folder (or ZIP) |
| 1.5 | Course roadmap | SC | `03-code/README.md` | `10-resources/glossary.md`, `10-resources/troubleshooting.md` | Repo link + PDF downloads |
| 1.6 | Quiz: Foundations | QZ | `06-assessments/quizzes/section-01.md` | none | Udemy quiz |

### Section 2

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 2.1 | Accounts, keys and spending caps | SC | `.env.example`, `10-resources/cost-guide.md` | none | Repo link + PDF download |
| 2.2 | Project setup with uv and the Makefile | SC | `pyproject.toml`, `Makefile` | `10-resources/troubleshooting.md` (install section) | Repo link + PDF download |
| 2.3 | Quick win: one request, one trace | SC | `app/server.py`, `telemetry/langfuse_setup.py` | `10-resources/langfuse-v4-cheatsheet.md` | Repo link + PDF download |
| 2.4 | Offline mode | SC | `simulator/replay.py`, `console/ops_console.py` | `10-resources/troubleshooting.md` (offline mode section) | Repo link + PDF download |
| 2.5 | Lab 1: Environment and first trace | LAB | `04-labs/lab-01-first-trace.md` | `10-resources/troubleshooting.md` | Lab doc (download) + walkthrough video |
| 2.6 | Quiz: Setup and tracing basics | QZ | `06-assessments/quizzes/section-02.md` | none | Udemy quiz |

### Section 3

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 3.1 | Traces, spans and context | SL | Diagram: trace anatomy (D3, first build) | `10-resources/glossary.md` | Diagram PNG/PDF |
| 3.2 | Code-along: manual OTel instrumentation | SC | `telemetry/otel_setup.py` | `10-resources/instrumentation-template.md` | Repo link + PDF download |
| 3.3 | GenAI semantic conventions | SL | `telemetry/genai_attrs.py` | `10-resources/genai-semconv-cheatsheet.md` | Repo link + PDF download |
| 3.4 | Code-along: tag every span | SC | `app/agent.py`, `telemetry/genai_attrs.py` | `10-resources/genai-semconv-cheatsheet.md` | Repo link + PDF download |
| 3.5 | Auto-instrumentation with OpenInference | SC | `telemetry/openinference_setup.py` | none | Repo link |
| 3.6 | Break it: orphan spans | DM | `tests/integration/test_spans.py` | `10-resources/troubleshooting.md` (tracing section) | Repo link + PDF download |
| 3.7 | Lab 2: Instrument a new tool | LAB | `04-labs/lab-02-instrument-tool.md` | `10-resources/instrumentation-template.md` | Lab doc + walkthrough video |
| 3.8 | Quiz: Tracing and semconv | QZ | `06-assessments/quizzes/section-03.md` | none | Udemy quiz |

### Section 4

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 4.1 | How Langfuse sits on OpenTelemetry | SL | Diagram: Langfuse on OTel (D4) | `10-resources/langfuse-v4-cheatsheet.md` | Diagram PNG/PDF + PDF download |
| 4.2 | Code-along: @observe | SC | `telemetry/langfuse_setup.py`, `app/agent.py` | `10-resources/langfuse-v4-cheatsheet.md` | Repo link + PDF download |
| 4.3 | Sessions, users, tenants and tags | SC | `app/server.py` | none | Repo link |
| 4.4 | Prompt management and versions | SC | `app/prompts.py` | none | Repo link |
| 4.5 | Scores, datasets and the feedback loop | SC | `evals/to_dataset.py` | none | Repo link |
| 4.6 | Masking, sampling and cost of observability | SC | `telemetry/langfuse_setup.py`, `src/northwind/pii.py` | `10-resources/telemetry-governance-checklist.md` (preview) | Repo link + PDF download |
| 4.7 | Challenge: guardrail observation | CH | `app/agent.py` (starter and solution at tag `s04`) | none | Video with pause point + repo link |
| 4.8 | Quiz: Langfuse | QZ | `06-assessments/quizzes/section-04.md` | none | Udemy quiz |

### Section 5

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 5.1 | What an agent trace must answer | SL | Diagram: trace waterfall of an agent step (D3) | none | Diagram PNG/PDF |
| 5.2 | Code-along: tracing the tool loop | SC | `app/agent.py` | none | Repo link |
| 5.3 | RAG spans | SC | `app/knowledge.py` | none | Repo link |
| 5.4 | Streaming: TTFT and tokens per second | SC | `app/agent.py`, `src/northwind/latency.py` | `10-resources/latency-budget-worksheet.md` (preview) | Repo link + PDF download |
| 5.5 | Logs vs traces vs metrics | SL | `telemetry/logging_setup.py`, `telemetry/metrics.py` | none | Repo link |
| 5.6 | Break it: the loop | DM | `simulator/scenarios.py` | none | Repo link |
| 5.7 | Lab 3: Trace a ticket escalation | LAB | `04-labs/lab-03-agent-trace.md` | none | Lab doc + walkthrough video |
| 5.8 | Quiz: Agent patterns | QZ | `06-assessments/quizzes/section-05.md` | none | Udemy quiz |

### Section 6

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 6.1 | Token anatomy | SL | Diagram: token anatomy (D5) | `10-resources/cost-guide.md` | Diagram PNG/PDF + PDF download |
| 6.2 | Code-along: a price table you can trust | SC | `src/northwind/pricing.py` | `10-resources/cost-guide.md` | Repo link + PDF download |
| 6.3 | Cost per request, session, user, tenant, feature | SC | `src/northwind/cost.py`, `src/northwind/report.py` | Diagram: cost rollup tree (D6) | Repo link + diagram PNG/PDF (attach to Part A) |
| 6.4 | Prompt caching | SC | `app/agent.py` | none | Repo link |
| 6.5 | The context diet | SC | `src/northwind/tokens.py` | none | Repo link |
| 6.6 | Small-model-first routing | SC | `app/agent.py` (router mode) | none | Repo link (attach to Part A) |
| 6.7 | Budgets and anomaly alerts per tenant | SC | `src/northwind/budget.py`, `telemetry/metrics.py` | none | Repo link |
| 6.8 | Challenge: cut daily cost by 40% | CH | `simulator/replay.py`, `console/ops_console.py` | none | Video with pause point + repo link |
| 6.9 | Project 1: The showback report | AS | `05-projects/project-1-showback-report.md` | `10-resources/cost-guide.md` | Udemy assignment + PDF |
| 6.10 | Quiz: Cost engineering | QZ | `06-assessments/quizzes/section-06.md` | none | Udemy quiz |

### Section 7

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 7.1 | Latency budgets for agents | SL | `10-resources/latency-budget-worksheet.md` | Diagram: latency budget (D7) | PDF download + diagram PNG/PDF |
| 7.2 | Code-along: TTFT, TPOT and p95 | SC | `src/northwind/latency.py`, `telemetry/metrics.py` | none | Repo link |
| 7.3 | Timeouts, retries and backoff | SC | `app/agent.py` | none | Repo link |
| 7.4 | Fallbacks and circuit breakers | SC | `app/agent.py` | none | Repo link |
| 7.5 | Rate limits, queues and degradation | SL | none | `10-resources/production-checklist.md` (preview) | PDF download |
| 7.6 | Chaos demo: slow provider | DM | `simulator/scenarios.py::slow_provider` | none | Repo link |
| 7.7 | Lab 4: Hold p95 under 4 seconds | LAB | `04-labs/lab-04-latency-chaos.md` | `10-resources/latency-budget-worksheet.md` | Lab doc + walkthrough video + PDF |
| 7.8 | Quiz: Latency and reliability | QZ | `06-assessments/quizzes/section-07.md` | none | Udemy quiz |

### Section 8

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 8.1 | Offline evals are not enough | SL | none | none | none |
| 8.2 | Code-along: sampled LLM-as-judge | SC | `evals/online_judge.py` | `src/northwind/sampling.py` | Repo link |
| 8.3 | User feedback that means something | SC | `app/server.py`, `evals/feedback.py` | none | Repo link |
| 8.4 | Guardrail and safety metrics | SC | `telemetry/metrics.py` | none | Repo link |
| 8.5 | Drift detection | SC | `src/northwind/drift.py`, `evals/drift_report.py` | none | Repo link |
| 8.6 | From bad trace to regression test | SC | `evals/to_dataset.py` | none | Repo link |
| 8.7 | Lab 5: Quality page of the Ops Console | LAB | `04-labs/lab-05-online-evals.md` | none | Lab doc + walkthrough video |
| 8.8 | Quiz: Online evaluation | QZ | `06-assessments/quizzes/section-08.md` | none | Udemy quiz |

### Section 9

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 9.1 | SLIs for agents | SL | `src/northwind/slo.py` | Diagram: SLO / error budget burn (D8) | Repo link + diagram PNG/PDF |
| 9.2 | Code-along: Prometheus metrics | SC | `telemetry/metrics.py`, `deploy/docker-compose.observability.yml` | none | Repo link |
| 9.3 | Grafana: the Atlas Ops dashboard | SC | `deploy/grafana/dashboards/atlas-ops.json` | none | Repo link (dashboard JSON as download too) |
| 9.4 | Langfuse dashboards and saved views | DM | none | none | none |
| 9.5 | Alert rules and the runbook | SC | `10-resources/runbook-template.md` | none | PDF download |
| 9.6 | Lab 6: Ship the dashboard and one alert | LAB | `04-labs/lab-06-dashboards.md` | `10-resources/runbook-template.md` | Lab doc + walkthrough video + PDF |
| 9.7 | Quiz: SLOs and alerting | QZ | `06-assessments/quizzes/section-09.md` | none | Udemy quiz |

### Section 10

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 10.1 | Your traces are a data breach waiting to happen | SL | none | `10-resources/telemetry-governance-checklist.md` | PDF download |
| 10.2 | Code-along: masking in SDK and collector | SC | `src/northwind/pii.py`, `deploy/otel-collector.yaml` | none | Repo link |
| 10.3 | Retention, access and tenant separation | SL | none | `10-resources/telemetry-governance-checklist.md` | PDF download |
| 10.4 | Regulatory logging obligations (not legal advice) | TH | `10-resources/telemetry-governance-checklist.md` | none | PDF download |
| 10.5 | Quiz: Governance | QZ | `06-assessments/quizzes/section-10.md` | none | Udemy quiz |

### Section 11

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 11.1 | How to read an incident like an SRE | SL | `10-resources/incident-template.md` | Diagram: incident timeline (D9) | PDF download + diagram PNG/PDF |
| 11.2 | Incident 1: Monday's cost spike | CH | `incidents/incident-01-cost-spike/` (`spans.jsonl`, `brief.md`) | `incident-template.md`; **`solution.md` on Part B only** | Repo link / ZIP of spans + brief (Part A); solution (Part B) |
| 11.3 | Incident 2: p95 doubled after lunch | CH | `incidents/incident-02-latency-regression/` | same rule | same |
| 11.4 | Incident 3: users are unhappy but nothing is red | CH | `incidents/incident-03-quality-drift/` | same rule | same |
| 11.5 | Writing the postmortem | SC | `10-resources/postmortem-template.md` | none | PDF download |
| 11.6 | Project 2: Investigate a fourth incident | AS | `05-projects/project-2-incident-postmortem.md` | `incident-template.md`, `postmortem-template.md` | Udemy assignment + PDFs (no solution attached) |
| 11.7 | Quiz: Incident response | QZ | `06-assessments/quizzes/section-11.md` | none | Udemy quiz |

### Section 12

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 12.1 | Vendor lock-in and the OTel escape hatch | SL | none | `10-resources/backend-decision-matrix.md` | PDF download |
| 12.2 | Code-along: Atlas traced to LangSmith | SC | `telemetry/langsmith_setup.py` | none | Repo link |
| 12.3 | Arize Phoenix and OpenInference | SC | `telemetry/otel_setup.py` | none | Repo link |
| 12.4 | OpenLLMetry, Datadog and the enterprise APMs | SL | none | none | none |
| 12.5 | Decision matrix | SL | `10-resources/backend-decision-matrix.md` | none | PDF download |
| 12.6 | Quiz: Portability | QZ | `06-assessments/quizzes/section-12.md` | none | Udemy quiz |

### Section 13

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 13.1 | Self-hosting Langfuse with Docker Compose | SC | `deploy/docker-compose.langfuse.yml` | `10-resources/troubleshooting.md` (Docker section) | Repo link + PDF download |
| 13.2 | OTel Collector as the traffic cop | SC | `deploy/otel-collector.yaml` | none | Repo link |
| 13.3 | Code-along: the CI budget gate | SC | `.github/workflows/ci.yml`, `tests/budget/test_budget_gate.py` | none | Repo link |
| 13.4 | Production readiness checklist | SL | `10-resources/production-checklist.md` | none | PDF download |
| 13.5 | Chaos demo: kill the observability backend | DM | `telemetry/otel_setup.py` | none | Repo link |
| 13.6 | Lab 7: Self-hosted stack end to end | LAB | `04-labs/lab-07-self-host.md` | `10-resources/production-checklist.md` | Lab doc + walkthrough video + PDF |

### Section 14

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 14.1 | Capstone brief and acceptance criteria | SL | `05-projects/capstone-atlas-ops.md` | `10-resources/production-checklist.md` | Brief (download) + PDF |
| 14.1a | Build it yourself first: the capstone gate | TH | same brief | none | none (points to 14.1's download) |
| 14.2 | Reference solution part A | SC | `03-code/` at tag `capstone` | none | Repo link (attach to Part A) |
| 14.3 | Reference solution part B | SC | `03-code/` at tag `capstone` | none | Repo link (attach to Part A) |
| 14.4 | The weekly ops report | SC | `src/northwind/report.py` | Example report output (markdown) | Repo link + download |
| 14.5 | Capstone submission and portfolio | TH | `05-projects/capstone-atlas-ops.md` | none | Udemy assignment |
| 14.6 | Domain swap: observe a different agent | AS | `10-resources/instrumentation-template.md` | none | Udemy assignment + PDF |
| 14.7 | Quiz: Capstone review | QZ | `06-assessments/quizzes/section-14.md` | none | Udemy quiz |

### Section 15

| ID | Lecture | Type | Primary resource (curriculum) | Also attach | Delivery |
|---|---|---|---|---|---|
| 15.1 | What you can now do | TH | none | none | none |
| 15.2 | Careers | TH | `10-resources/interview-questions.md` | none | PDF download |
| 15.3 | Final practice test | QZ | `06-assessments/practice-test.md` | none | Udemy practice test |
| 15.4 | Bonus lecture | TH | none | Course links per bonus-lecture rules (verify) | In-lecture text only |

## Downloadable resource inventory (export all to PDF)

| File | First attached at | Also attached at |
|---|---|---|
| `10-resources/cost-guide.md` | 2.1 | 6.1, 6.2, 6.9 |
| `10-resources/latency-budget-worksheet.md` | 7.1 | 5.4, 7.7 |
| `10-resources/runbook-template.md` | 9.5 | 9.6 |
| `10-resources/incident-template.md` | 11.1 | 11.2-11.4, 11.6 |
| `10-resources/postmortem-template.md` | 11.5 | 11.6 |
| `10-resources/telemetry-governance-checklist.md` | 10.1 | 4.6, 10.3, 10.4 |
| `10-resources/backend-decision-matrix.md` | 12.5 | 1.3, 12.1 |
| `10-resources/production-checklist.md` | 13.4 | 7.5, 13.6, 14.1 |
| `10-resources/instrumentation-template.md` | 3.2 | 3.7, 14.6 |
| `10-resources/genai-semconv-cheatsheet.md` | 3.3 | 3.4 |
| `10-resources/langfuse-v4-cheatsheet.md` | 2.3 | 4.1, 4.2 |
| `10-resources/interview-questions.md` | 15.2 | |
| `10-resources/glossary.md` | 1.2 | 1.5, 3.1 |
| `10-resources/troubleshooting.md` | 1.5 | 2.2, 2.4, 2.5, 3.6, 13.1 |
