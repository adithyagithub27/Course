# Production Readiness Checklist for Observability

**Used in:** 13.4 (production readiness), 7.5 (degradation), 13.5 (chaos: backend down), 13.6 (Lab 7), 14.1 (capstone acceptance)
**Companions:** `runbook-template.md`, `telemetry-governance-checklist.md`, `latency-budget-worksheet.md`

> Tick every item before an agent's observability stack is called "production". Items reference the course lectures where each one is built. The order is deliberate: the stack must **never hurt the agent** (§1), must **see the right things** (§2-4), must **tell the right people** (§5), and must **cost and leak less than it saves** (§6-7).

---

## 1. Telemetry never takes the agent down

- [ ] **Exporter back-pressure understood:** `BatchSpanProcessor` queue size and export timeout set; when the backend is slow or down, spans are **dropped, not requests** (13.5)
- [ ] Exporter and backend failures are logged as metrics (`telemetry_export_failures_total`), not exceptions in the request path
- [ ] Langfuse `flush()` / `shutdown()` on process exit; no blocking flush inside the request handler (4.6)
- [ ] Chaos test passed: backend stopped mid-swarm, Atlas keeps serving, `/healthz` stays green (13.5)
- [ ] Judge and drift jobs run out of band (a scheduled process), never inline in the request (8.2)

## 2. Traces

- [ ] Every LLM call, tool call, retrieval and agent run is a span with the **GenAI semantic conventions** attributes from `genai_attrs.py` (3.3, 3.4); attribute constants from `opentelemetry.semconv._incubating`, never hand-typed strings
- [ ] Resource attributes set: `service.name`, `deployment.environment`, release/version (3.2); Langfuse `environment` and `release` set (4.1)
- [ ] Session, user (pseudonymised) and tenant on every trace (4.3)
- [ ] Prompt **version** on every generation (4.4); the version is what Incident 3's rollback depends on
- [ ] Step spans with a step-limit event; escalation model as a child generation (5.2)
- [ ] Tool spans record status, redacted arguments and redacted results (5.2, 10.2)
- [ ] Streaming: TTFT recorded (`gen_ai.response.time_to_first_chunk`, `completion_start_time`) (5.4)
- [ ] No orphan spans, no double instrumentation: `tests/integration/test_spans.py` green (3.6)
- [ ] **Sampling policy in prod** written down and implemented: head sampling in the SDK (`sample_rate`) and/or tail sampling in the collector keeping 100% of errors and budget hits (4.6, 13.2)

## 3. Cost

- [ ] Price table sourced from `litellm.model_cost` with a **dated** pinned fallback; cached and reasoning tokens handled (6.2)
- [ ] Cost on every generation; rollups by request, session, user, tenant, feature reconcile to the provider invoice within a tolerance you've written down (6.3)
- [ ] **Per-tenant budgets** on by default: soft cap degrades, hard cap refuses politely; both emit metrics and trace events (6.7)
- [ ] Cost anomaly detection (EWMA) per tenant with an alert and a runbook (6.7, 9.5)
- [ ] Showback report generated weekly and read by someone in finance (6.9, 14.4)
- [ ] Cost of observability (judge calls, backend fees) reported as its own line (4.6)

## 4. Latency and reliability

- [ ] Latency budget written (`latency-budget-worksheet.md`) and **p95 within budget** on the replayed day (7.1, 7.2)
- [ ] Per-call timeouts, bounded retries with jitter, idempotent tool calls (7.3)
- [ ] Fallback lists and circuit breaker (Router `fallbacks`, `allowed_fails`, `cooldown_time`); fallback events on the trace and a fallback-rate metric (7.4)
- [ ] Rate-limit handling, per-tenant concurrency, shedding and a degraded-mode message (7.5)
- [ ] Chaos test passed: `slow_provider` during peak with p95 holding (7.6)
- [ ] Step limit enforced (5.2, 5.6)

## 5. Quality in production

- [ ] Sampled online judge running with a **cost cap**, criteria reviewed, scores written back (8.2)
- [ ] User feedback captured and correlated with judge scores (8.3)
- [ ] Guardrail metrics as time series: injection attempts, refusal rate, PII-in-output (8.4)
- [ ] Weekly drift report with thresholds and an owner (8.5)
- [ ] Path from bad trace → dataset → offline eval → prompt promotion exists and is used before any prompt label change (8.6)

## 6. Dashboards, SLOs, alerts

- [ ] SLIs defined in `slo.py`: task success, containment, tool error rate, p95, cost per resolved session, judge score (9.1)
- [ ] SLOs with error budgets and burn-rate alerts (fast + slow windows) (9.1, 9.5)
- [ ] Prometheus metrics with **low-cardinality labels only** (no `user_id`) (5.5, 9.2)
- [ ] **Dashboards as code:** `atlas-ops.json` in the repo, provisioned, not hand-edited in the UI (9.3, 13.4)
- [ ] Release annotations on dashboards and release tags in the tracing backend (9.3, 13.3)
- [ ] Every alert has a **runbook and an owner**; alerts reviewed monthly for fatigue (`runbook-template.md`)
- [ ] Stakeholders get saved views / dashboards, not raw trace access (9.4, 10.3)

## 7. Privacy, security, governance

- [ ] Masking in the SDK **and** the collector, tested on the PII fixture (10.2)
- [ ] Judge inputs masked; datasets masked (10.2)
- [ ] Retention per signal configured; deletion procedure tested (10.3)
- [ ] Project per environment; RBAC; tenant model decided (tags vs projects) (10.3)
- [ ] Secrets in a manager; rotated; nothing in repo, image, logs or dashboards (13.4)
- [ ] Regulatory record-keeping requirements confirmed with counsel; `telemetry-governance-checklist.md` sign-off complete (10.4; not legal advice)

## 8. Deployment and CI

- [ ] Self-hosted stack (or cloud equivalent) reproducible from `deploy/` with pinned image versions; compose file verified against the current Langfuse release (13.1)
- [ ] OTel Collector is the single routing point: receivers, processors (attributes, tail sampling), exporters (13.2)
- [ ] **CI budget gate** replays the day offline and fails the PR on cost per session or p95 regression; runs on every PR without secrets (13.3)
- [ ] Unit + integration tests green offline; live evals only when secrets exist (13.3)
- [ ] Rollback rehearsed for: prompt label, model config, collector config, dashboard JSON
- [ ] Version pins documented; upgrade plan for semconv (incubating) and SDK minors: re-run the full suite and the replay before bumping

## 9. Operations

- [ ] On-call rotation and escalation path written into the runbooks
- [ ] Weekly ops report (`report.py`) generated and reviewed; recommendations tracked (14.4)
- [ ] Postmortem process in place (`postmortem-template.md`); incident fixtures added to `incidents/` after each real incident (11.5)
- [ ] Quarterly review: retention, alert thresholds, price table date, semconv version, backend decision (`backend-decision-matrix.md`)
