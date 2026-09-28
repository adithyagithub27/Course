# Telemetry Governance Checklist

**Used in:** 10.1 (threat model), 10.2 (masking), 10.3 (retention, access, tenant separation), 10.4 (regulatory logging obligations), 4.6 (masking and sampling), 13.4 (production readiness)

> ## NOT LEGAL ADVICE
> This checklist is an educational starting point for engineers. It isn't legal advice, it isn't complete, and laws change and vary by country, sector and use case. **Before shipping an agent whose traces contain personal data, employee records or regulated information, have qualified counsel and your privacy or compliance function review your specific situation.** Where this document names a regulation, treat it as a pointer for your own research and verify its current text and applicability.

The running example is **Northwind Logistics** (fictional). Atlas handles employee questions, tickets, password resets and shipment lookups, so its prompts and tool results contain **employee PII and internal records** by design. Everything below is about what leaves Atlas as **telemetry**: spans, logs, metrics, judge inputs, datasets and dashboards.

---

## 1. Threat model for telemetry (lecture 10.1)

- [ ] **Prompts contain PII.** Employee names, ids, emails, phone numbers, sometimes health or payroll details typed by users. Any span that records the prompt records all of it.
- [ ] **Tool results contain records.** `lookup_ticket`, `reset_password`, `check_shipment` return internal data. A tool span with `gen_ai.tool.call.result` recorded in full is a copy of your ticketing system in your tracing backend.
- [ ] **Judges see everything.** The online judge (8.2) sends sampled traces to an LLM. That's a third-party data transfer of whatever is in the trace.
- [ ] **Datasets outlive traces.** Promoting a trace to a dataset item (4.5, 8.6) copies it out of the retention window and into a long-lived artifact.
- [ ] **Dashboards are shared.** Saved views shared with stakeholders (9.4) expose whatever the traces contain.
- [ ] **Metrics leak through labels.** A `user_id` label on a Prometheus metric is a user list (5.5).
- [ ] **Telemetry backends are third parties** (Langfuse Cloud, LangSmith, Datadog) unless self-hosted (13.1). Your data-processing agreements have to cover them.

## 2. Minimise and mask (lecture 10.2)

- [ ] **Decide what a span needs.** For a generation: model, usage, cost, latency, prompt *version*, a hash of the prompt. The prompt text itself is opt-in per environment.
- [ ] **Mask in the SDK first:** Langfuse `mask=` function (`src/northwind/pii.py`) so PII never leaves the process. Mask emails, phones, employee ids, card numbers; keep **stable hashes** so you can still join a user's sessions without storing the identifier.
- [ ] **Mask again in the OTel Collector** (`deploy/otel-collector.yaml` attribute processors) as defence in depth and to cover any exporter path that bypasses the SDK.
- [ ] **Redact tool results** to what the investigation needs (status, counts, ids-as-hashes), not the full record (5.2).
- [ ] **Sample** (4.6, 13.2): fewer full traces means less exposure. Keep 100% of metrics, a sample of full traces, and 100% of error traces with masking on.
- [ ] **Judge inputs are masked too.** The judge scores the masked trace, not the raw one. Check that grounding criteria still work on masked text.
- [ ] **Never a `user_id`, email or name as a metric label.** Tenant and feature are fine (low cardinality).
- [ ] **Test the mask** (`tests/unit/test_pii.py`): a fixture with every PII type must come out clean in the SDK path and the collector path.

## 3. Retention (lecture 10.3)

- [ ] Write down a **retention window per signal**: e.g., full traces N days, masked traces M days, metrics longer, datasets reviewed quarterly, incident fixtures kept but re-masked. Numbers are yours; the point is that they exist and are enforced.
- [ ] **Configure retention in the backend** (Langfuse project settings or self-hosted database policy; check what your plan supports) and in Prometheus (`--storage.tsdb.retention.time`).
- [ ] **Datasets and incident fixtures**: review before promoting; keep only masked content; record the source trace id, not the content, where possible.
- [ ] **Deletion requests**: know how to delete one user's traces (by hashed `user_id`) in every system: backend, local store, datasets, exported reports.
- [ ] **Backups** of self-hosted backends inherit the retention problem; include them.

## 4. Access and tenant separation (lecture 10.3)

- [ ] **Project per environment** (dev / staging / prod) in the tracing backend; never mix.
- [ ] **Role-based access:** who can read prompts and tool results? Who can only see metrics and scores? Give stakeholders dashboards (9.4), not trace access.
- [ ] **Tenant separation:** tags (`tenant=`) are fine for slicing one company's departments (Northwind). For separate **customers**, use separate projects (or separate backends) so an access grant can't cross tenants. Decide and document which model you use.
- [ ] **Secrets:** Langfuse secret keys, OTLP auth headers and OpenAI keys in a secrets manager; rotated; never in the repo, the image, logs or on screen (see `../09-production/recording-guide.md` §6.2).
- [ ] **Audit access** to the tracing backend where the plan supports it.

## 5. Regulatory record-keeping (lecture 10.4; not legal advice)

The point of this section is that telemetry is both a **privacy risk** (too much) and a **compliance asset** (too little). Engineers are usually asked for both at once.

- [ ] **Personal data law (e.g., GDPR in the EU/UK; other regimes elsewhere):** traces containing personal data need a lawful basis, purpose limitation, minimisation, retention limits, data-subject rights (access, deletion) and appropriate safeguards for transfers to third-party backends and judge providers. Verify what applies to you.
- [ ] **EU AI Act (as understood; verify current text and timelines with counsel):** the Act sets **record-keeping / logging obligations for high-risk AI systems**, broadly to allow traceability of the system's operation over its lifetime, and transparency and human-oversight expectations. Whether an internal helpdesk agent like Atlas is high-risk depends on its use (for example, HR decisions about employees are an area the Act treats seriously). **Do not assume you are out of scope, and do not assume your traces satisfy the obligations.** Ask counsel what must be logged, for how long, and in what form.
- [ ] **Sector rules:** if Atlas touches payroll, health, or financial data, sector-specific rules (employment law, health-data rules, financial record-keeping) may add requirements. Verify.
- [ ] **What to keep (typical asks; verify):** which model and prompt version answered, when, for which (pseudonymised) user and tenant, which tools were called, what the outcome was, what the judge scored, who accessed the record. The GenAI semantic conventions and Langfuse's prompt versioning give you most of this without storing prompt text.
- [ ] **What never to log:** raw credentials, password-reset secrets, full card numbers, health details typed by employees, tool results beyond what the record needs. Mask before it leaves the process.
- [ ] **Audit trail of the observability system itself:** who changed a mask, a retention setting, an alert threshold, a prompt label. Dashboards as code (13.4) and prompt versioning give you this for free.
- [ ] **Judge and evaluation data** may itself count as processing of personal data. Cover it in your records and DPAs.

## 6. Incident-related obligations (not legal advice)

- [ ] If PII reaches a trace unmasked, treat it as a potential **data incident**: contain (delete / re-mask), assess (what, whose, how long exposed, which third parties), and check **notification obligations** (personal-data breach rules in your jurisdiction have deadlines). Verify with counsel.
- [ ] Keep the postmortem (`postmortem-template.md`) itself free of the leaked data.

## 7. Go-live sign-off

| Item | Owner | Done | Notes |
|---|---|---|---|
| Span content policy written (what each observation type records) | | [ ] | |
| SDK mask + collector mask tested on the PII fixture | | [ ] | |
| Judge inputs confirmed masked | | [ ] | |
| Retention configured per signal and documented | | [ ] | |
| Project per environment; RBAC; stakeholder dashboards instead of trace access | | [ ] | |
| Tenant model decided (tags vs projects) and documented | | [ ] | |
| Secrets in a manager; rotated; nothing in repo or logs | | [ ] | |
| Deletion procedure tested end to end | | [ ] | |
| DPAs / terms reviewed for backend and judge providers | | [ ] | |
| Regulatory record-keeping requirements confirmed with counsel | | [ ] | Not optional for real deployments |
| **Legal / privacy review completed** | | [ ] | |
