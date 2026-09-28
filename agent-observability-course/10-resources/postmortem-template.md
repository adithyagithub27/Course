# Blameless Postmortem Template

**Used in:** 11.5 (writing the postmortem), 11.6 (Project 2 submission), 14.5 (portfolio)

> A postmortem is not the investigation (that's `incident-template.md`). It is the document the team reads afterwards to make the next incident less likely or less painful. **Blameless** means it describes what the system allowed, not who pressed the button. Every action item must map to one of three things this course builds: **instrumentation** (you couldn't see it), a **budget or guard** (the system let it run), or a **test** (a change shipped without a check). Keep it to two pages.

---

## Template

```markdown
# Postmortem: <incident name>

| Field | Value |
|---|---|
| Incident id | <INC-YYYY-NNN> |
| Date of incident | <date> |
| Duration (first bad trace → mitigated) | <h:mm> |
| Severity | <S1 users blocked | S2 degraded | S3 cost or quality only, no user impact> |
| Author(s) | <names; the people closest to the system, not "the person who caused it"> |
| Reviewers | <someone outside the team> |
| Status | <draft | reviewed | actions complete> |

## 1. Summary (three sentences, readable by a manager)
<What happened, who was affected, what it cost (money, latency, quality), how it was found and fixed.>

## 2. Impact
| Dimension | Measurement | Source |
|---|---|---|
| Users / sessions affected | <count; % of the day> | Langfuse sessions filter |
| Tenants affected | <list> | tag filter |
| Cost impact | <$ over baseline, simulated or real; price-table date> | Ops Console cost page / showback |
| Latency impact | <p95 before / during / after> | Grafana / latency page |
| Quality impact | <judge score, feedback, refusal rate before / during / after> | Quality page |
| Error budget consumed | <% of the 30-day budget> | slo.py / burn-rate panel |

## 3. Timeline (from the investigation, cleaned up)
| Time | Event | Source |
|---|---|---|
| T-? | <change that set it up> | |
| T0 | <first bad trace> | |
| T+ | <alert fired / nothing fired> | |
| T+ | <detected by whom, how> | |
| T+ | <mitigation> | |
| T+ | <root cause identified> | |
| T+ | <resolved> | |

## 4. Root cause
<The condition that, had it been different, would have prevented the incident. One paragraph. Separate trigger from cause.>

**Trigger:** <e.g., tool `lookup_ticket` started returning 500s for tenant `ops`>
**Cause:** <e.g., the agent had no step limit and no per-tenant budget, so a tool failure became an unbounded retry loop with growing context>

## 5. Contributing factors
- <Detection: what should have alerted and didn't, e.g., no alert on steps per session or on cost anomaly per tenant>
- <Visibility: what you couldn't see, e.g., tool errors were not on the trace as span status>
- <Process: what shipped without a check, e.g., prompt v2 promoted to `production` without an eval run>
- <Design: what the system allowed, e.g., retries without backoff or cap>

## 6. What went well
- <e.g., the offline replay reproduced the incident in minutes>
- <e.g., the hard cap stopped the spend within one minute of being enabled>

## 7. What went badly / where we got lucky
- <e.g., detection was a finance email, not an alert>
- <e.g., it happened on a weekend with low traffic; on a weekday the cost would have been N×>

## 8. Action items (each maps to instrumentation, budget/guard or test)
| # | Action | Type | Owner | Due | Tracking | Done |
|---|---|---|---|---|---|---|
| 1 | <e.g., add `gen_ai`-attributed tool span status and a tool-error-rate metric> | Instrumentation | | | | [ ] |
| 2 | <e.g., per-tenant soft and hard budget caps in budget.py, default on> | Budget / guard | | | | [ ] |
| 3 | <e.g., step limit AGENT_MAX_STEPS enforced, with an event on the trace> | Budget / guard | | | | [ ] |
| 4 | <e.g., alert AtlasTenantCostAnomaly with runbook> | Instrumentation | | | | [ ] |
| 5 | <e.g., CI budget gate asserts cost per session on the replayed day> | Test | | | | [ ] |
| 6 | <e.g., prompt label promotion requires a passing offline eval on the dataset> | Test | | | | [ ] |
| 7 | <e.g., add this incident's spans as a regression fixture in incidents/> | Test | | | | [ ] |

## 9. Lessons for the runbook and the dashboard
- Runbook <name> updated: <what changed>
- Dashboard panel added / changed: <which SLI>
- Alert threshold / window changed: <from → to, why>

## 10. Appendix
- Links: investigation doc, traces (redacted), dashboards (time-ranged), PRs
- Glossary for readers outside the team
```

---

## Writing rules (lecture 11.5)

1. **Names of people never appear as causes.** "The on-call engineer restarted the service" is a timeline fact; "the engineer should have noticed" is not allowed.
2. **Numbers, not adjectives.** "Cost was 6.2× baseline for 5 h 40 m" beats "cost was very high for a while". Label simulated figures as simulated with the price-table date.
3. **Every contributing factor gets an action item or an explicit "accepted, not fixing because…".**
4. **Action items are small and verifiable.** "Improve monitoring" is not an action item; "add `AtlasToolErrorRate` alert with runbook, owner X, due date Y" is.
5. **Review it with someone outside the team.** They catch the jargon and the blame that slipped in.
6. **Re-read it after the actions are done.** Did the actions actually prevent a replay of the incident? Re-run `OFFLINE=1 make replay` with the incident scenario injected and confirm the alert fires and the guard holds. That re-run is the best possible closing line.

## The three course incidents mapped to action types (after the reveals; spoilers)

| Incident | Trigger | Cause | Instrumentation | Budget / guard | Test |
|---|---|---|---|---|---|
| 1. Cost spike | Tool errors on one tenant | No step limit, no tenant budget, retries without cap; context re-sent every step | tool error rate, steps per session, cost anomaly per tenant | step limit, soft/hard caps, bounded retries | budget gate on cost per session |
| 2. p95 doubled | Provider slowdown | Compounded by a retrieval top-k change with no annotation; no fallback, timeouts too long | release annotations, fallback-rate metric, retriever span with k | timeouts, fallback list, circuit breaker | budget gate on p95; chaos scenario in CI |
| 3. Quality drift | Prompt v2 promoted | No eval before promotion; no judge on live traffic; feedback not correlated | online judge scores, prompt version on every generation, drift report | label promotion policy | offline eval on the dataset before promotion |
