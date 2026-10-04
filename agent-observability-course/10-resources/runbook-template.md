# Runbook Template

**Used in:** 9.5 (alert rules and the runbook), 9.6 (Lab 6), 11.5 (postmortem action items), 13.4 (alert ownership)

> One runbook per alert. If an alert has no runbook, it isn't ready to page anyone. Keep runbooks next to the alert rules in the repo (`deploy/grafana/` or `deploy/alerts/`) so they version together. Every step should be something a tired person can do at 3 a.m. without deciding anything hard. Fill in the four example runbooks at the bottom during 9.5 and Lab 6.

---

## Template

```markdown
# Runbook: <ALERT NAME>

**Alert rule:** <file and rule name, e.g. deploy/alerts.yml :: AtlasTenantCostAnomaly>
**Severity:** <page | ticket | info>
**Owner (team / rotation):** <who is paged; who reviews this runbook quarterly>
**Last reviewed:** <date>   **Last fired:** <date, link to incident>

## What this alert means
<One paragraph in plain words. Which SLI moved, in which direction, for whom (tenant / feature / all).
 What the user or the finance team experiences if nothing is done.>

## Is it real? (2 minutes)
- [ ] Open <dashboard link> and confirm the panel matches the alert (not a scrape gap or a dashboard bug)
- [ ] Check the release annotations: did a deploy, prompt label change or config change land in the last <N> minutes?
- [ ] Check provider status: <provider status page>
- [ ] Check the swarm / traffic: is this a traffic spike (more sessions) or a per-session change (same sessions, more cost / time)?

## Blast radius (3 minutes)
- [ ] Which tenants? (Grafana tenant variable / Langfuse tag filter `tenant=`)
- [ ] Which feature? (`feature=` tag)
- [ ] Since when? (first bad trace; note the timestamp for the incident timeline)
- [ ] How many sessions affected so far?

## Mitigate first (stop the bleeding; don't diagnose yet)
| Symptom | Action | Command / where |
|---|---|---|
| Cost spike on one tenant | Enable the tenant's **hard cap** (refuse politely) | `budget.py` config / env `BUDGET_HARD_CAP_<TENANT>` |
| Runaway steps | Lower the **step limit** | env `AGENT_MAX_STEPS`; restart Atlas |
| Latency regression | Force **fallback model** / shorten timeouts | Router config env; restart |
| Quality drift after a prompt change | **Roll back the prompt label** (`production` → previous version) | Langfuse prompts UI or `create_prompt(..., labels=["production"])` on the old version |
| Provider outage | **Circuit breaker open**; degraded-mode message | Router `cooldown_time`; feature flag `DEGRADED_MODE=1` |
| Telemetry backend down | Nothing for users; confirm Atlas is still serving; exporter drops telemetry not requests | Check `/healthz`; check exporter queue logs (13.5) |

## Diagnose (after mitigation)
- [ ] Open the top-cost / slowest / lowest-scored session in Langfuse (link: <saved view>)
- [ ] Read the waterfall top-down: steps, tool errors, context growth, retries, fallbacks
- [ ] Compare with a good session from before the first bad trace
- [ ] Write the hypothesis in the incident doc (`incident-template.md`) before changing anything else

## Resolve and verify
- [ ] Fix applied (config, prompt version, code)
- [ ] Alert cleared and stayed clear for <N> minutes
- [ ] Replay the affected window offline with the fix (`OFFLINE=1 make replay`) and confirm the SLI recovers
- [ ] Budget gate still passes (`make budget-check`)

## Escalate if
- <condition, e.g., cost per resolved session > 3× baseline after mitigation> → <who>
- <condition, e.g., two tenants affected> → <who>
- <condition, e.g., PII suspected in traces> → security on-call (see telemetry-governance-checklist.md)

## Afterwards
- [ ] Incident doc completed; postmortem scheduled (`postmortem-template.md`)
- [ ] Alert threshold / window reviewed: did it fire early enough? too often?
- [ ] This runbook updated with what you learned
```

---

## Alert fatigue rules (lecture 9.5)

1. **Page only on user-facing symptoms and budget burn**; everything else is a ticket.
2. **Every alert has a runbook entry and an owner**, or it doesn't ship. In the shipped `deploy/alerts.yml` only `AtlasLatencyP95High` has a `runbook` annotation and no rule has an `owner` label; adding both is part of Lab 6 and capstone AT-22.
3. **Two windows or a `for:` clause on anything rate-based**: burn-rate alerts with a fast window (page) and a slow window (ticket) rather than a static threshold on the raw SLI.
4. **Cost anomaly alerts compare a tenant with its own history**: `AtlasTenantCostAnomaly` fires when a tenant's last hour is above 2.5× its average hour over the previous day (and above $1) for 15 minutes, so a big tenant's normal day doesn't page for a small tenant's spike. It needs a day of history; the EWMA detector in `budget.py` does the per-request version on the Ops Console's Budgets page.
5. **Review the alert log weekly**: any alert that fired three times with no action gets deleted or demoted.
6. **Unit-test every rule with `promtool test rules`** before it goes live, including that it *can* fire (`AtlasJudgeScoreLow` can't until judge scores reach Prometheus).
7. **Silence with an expiry** during known changes (a prompt rollout), never indefinitely.

## The shipped rules (`deploy/alerts.yml`, ten rules in three groups)

| Group | Alert | Rule (as shipped) | Severity | Runbook entry |
|---|---|---|---|---|
| SLO | `AtlasLatencyP95High` | p95 of `atlas_request_latency_seconds` > 4 s for 10 min | page | [#latency](#latency) (shipped link) |
| SLO | `AtlasTaskSuccessBurnRateFast` | bad-outcome share / (1 − 0.95) > 14.4 over 1 h, for 5 min | page | #latency (add the annotation) |
| SLO | `AtlasTaskSuccessBurnRateSlow` | same, > 6 over 6 h, for 30 min | ticket | #latency (add) |
| SLO | `AtlasToolErrorRate` | any tool's error share > 5% over 10 min, for 10 min | ticket | write `#tool-errors` |
| Cost | `AtlasTenantCostAnomaly` | last hour > 2.5× previous day's average hour and > $1, for 15 min | ticket | write `#cost-anomaly` |
| Cost | `AtlasBudgetHardCapHit` | any `refuse` budget decision in 15 min | page | write `#cost-anomaly` |
| Cost | `AtlasRetryStorm` | > 0.2 LLM retries per request over 10 min, for 10 min | page | write `#retry-storm` |
| Quality | `AtlasJudgeScoreLow` | mean `judge_grounded` < 0.75 over 2 h, for 30 min (cannot fire: nothing exports judge scores to Prometheus) | ticket | write once it can fire |
| Quality | `AtlasNegativeFeedbackSpike` | negative share of feedback > 40% over 2 h, for 30 min | ticket | write `#quality` |
| Quality | `AtlasTelemetryExportFailures` | more than 20 export failures in 10 min | ticket | write `#telemetry` |

Read the exact expressions in `deploy/alerts.yml`; the table paraphrases them.

## latency

The entry `AtlasLatencyP95High` links to (`runbook: "10-resources/runbook-template.md#latency"`). Lecture 9.5 fills it in from the template above.

```markdown
## latency  (AtlasLatencyP95High; AtlasTaskSuccessBurnRateFast / Slow)
Owner: Atlas on-call (#atlas-ops). Severity: page (fast) / ticket (slow).
First look (2 min): Grafana "Atlas Ops": p95 latency, "LLM retries and fallbacks / s", outcomes / s.
Decision tree:
  - retries and fallbacks ≈ 0 and p95 high → provider is slow, not failing; lower ATLAS_REQUEST_TIMEOUT_S so stalls error and fall back (7.3, 7.6)
  - fallbacks high, cost per hour rising → fallbacks working; check from_model/to_model; add a second provider (7.4)
  - one tenant's atlas_queue_wait_seconds rising, sheds climbing → burst; raise that tenant's slots in ATLAS_TENANT_MAX_INFLIGHT temporarily (7.5)
  - retries by reason = RateLimitError → provider 429s; check provider status (7.5)
Verify: p95 under 4 s for 10 min; task-success burn rate < 1.
Postmortem needed if: fast burn > 30 min, or budget remaining < 20%.
```

The thresholds come from the replayed baseline (p95 3,827 ms against the 4,000 ms budget) and the SLO definitions in `src/northwind/slo.py` (`DEFAULT_SLOS`: task success 0.95, containment 0.80, tool success 0.99, latency 0.95, cost 0.90, quality 0.90); the worksheet in `latency-budget-worksheet.md` gives you the per-step numbers.
