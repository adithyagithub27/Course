# Runbook Template

**Used in:** 9.5 (alert rules and the runbook), 9.6 (Lab 6), 11.5 (postmortem action items), 13.4 (alert ownership)

> One runbook per alert. If an alert has no runbook, it isn't ready to page anyone. Keep runbooks next to the alert rules in the repo (`deploy/grafana/` or `deploy/alerts/`) so they version together. Every step should be something a tired person can do at 3 a.m. without deciding anything hard. Fill in the four example runbooks at the bottom during 9.5 and Lab 6.

---

## Template

```markdown
# Runbook: <ALERT NAME>

**Alert rule:** <file and rule name, e.g. deploy/alerts/atlas.yml :: AtlasCostAnomaly>
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

1. **Every page has a runbook and an owner.** No owner, no page: make it a ticket instead.
2. **Alert on symptoms users or finance feel** (SLO burn, cost per resolved session, p95), not on causes (CPU, one 429). Causes go on the dashboard.
3. **Use burn-rate alerts with two windows** (fast burn: page; slow burn: ticket) rather than a static threshold on the raw SLI.
4. **Cost anomaly alerts use the EWMA baseline** from `budget.py`, per tenant, so a big tenant's normal day doesn't page for a small tenant's spike, and vice versa.
5. **Review every alert that fired this month.** If it wasn't actionable, change the threshold, the window, or delete it.
6. **Silence with an expiry** during known changes (a prompt rollout), never indefinitely.

## The four course alerts (fill in during 9.5 and Lab 6)

| Alert | SLI | Rule sketch | Severity | Runbook file |
|---|---|---|---|---|
| `AtlasErrorBudgetFastBurn` | task success SLO | burn rate > <X> over 1 h **and** > <X> over 5 min | page | `runbooks/error-budget-fast-burn.md` |
| `AtlasErrorBudgetSlowBurn` | task success SLO | burn rate > <Y> over 6 h and 30 min | ticket | `runbooks/error-budget-slow-burn.md` |
| `AtlasCostAnomaly` | cost per resolved session per tenant | > EWMA baseline + <k>σ for 15 min, or hard cap hits > 0 | page (hard cap) / ticket (anomaly) | `runbooks/cost-anomaly.md` |
| `AtlasToolErrorSpike` | tool error rate | > <Z>% over 10 min for any tool | ticket; page if it coincides with fast burn | `runbooks/tool-error-spike.md` |

Thresholds are yours to set from the replayed baseline; the worksheet in `latency-budget-worksheet.md` and the SLO definitions in `src/northwind/slo.py` give you the starting numbers.
