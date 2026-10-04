# Quiz: SLOs and Alerting (Section 9)

| Field | Value |
|---|---|
| Udemy lecture | 9.7 Quiz: SLOs and alerting |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 9.1 to 9.6 |

---

### Q1. Atlas's task-success SLO is 95%. In the last hour, 20% of requests ended `error`, `step_limit`, `tool_error` or `timeout`. What is the burn rate, and does either burn-rate rule in `deploy/alerts.yml` fire on this hour alone?

*Related lecture: 9.1 SLIs for agents that leadership understands*

- **A.** Burn rate cannot be computed without a full month of data.
  - *Explanation:* Incorrect. Burn rate is computed over a short window precisely so you can act before the month is over.
- **B.** Burn rate 0.80; the SLO is healthy because 80% is close to 95%.
  - *Explanation:* Incorrect. Burn rate is not the SLI value; it is how fast you are consuming the error budget relative to the allowed rate.
- **C.** Burn rate 4: the allowed bad fraction is 5% (1 − 0.95), the observed bad fraction is 20%, and 20% / 5% = 4, so a 30-day budget would be gone in 7.5 days. The fast rule pages at 14.4 over 1 h and the slow rule tickets at 6 over 6 h, so neither fires yet; the hour still eats budget and shows on the dashboard.
  - *Explanation:* Correct. Burn rate = observed bad fraction / allowed bad fraction. Write both fractions down first. `northwind.slo.burn_rate` implements it, and `AtlasTaskSuccessBurnRateFast` / `Slow` encode the two windows.
- **D.** Burn rate 15; the fast rule pages.
  - *Explanation:* Incorrect arithmetic: 15 would need a 75% bad fraction.

**Correct answer: C**

---

### Q2. Which Prometheus query gives the p95 request latency across all tenants, and what caveat applies?

*Related lecture: 9.2 Code-along: Prometheus metrics from Atlas*

- **A.** `quantile(0.95, atlas_request_latency_seconds_count)`; counts are quantile-able.
  - *Explanation:* Incorrect. `quantile` over a count series computes the quantile of counts across label sets, not of durations.
- **B.** `avg(atlas_request_latency_seconds_sum / atlas_request_latency_seconds_count)`; it is exact.
  - *Explanation:* Incorrect. That is the mean, which hides the tail (Section 7).
- **C.** `max(atlas_request_latency_seconds_bucket)`; buckets hold the slowest request.
  - *Explanation:* Incorrect. Buckets are cumulative counts of observations at or below `le`, not durations.
- **D.** `histogram_quantile(0.95, sum(rate(atlas_request_latency_seconds_bucket[5m])) by (le))`; the result is interpolated within the bucket that contains the 95th percentile, so precision is limited by bucket boundaries, which is why Atlas's buckets include the 4 s budget as a boundary.
  - *Explanation:* Correct. Summing by `le` across tenants first, then applying `histogram_quantile`, gives the global p95 at bucket resolution. For millisecond precision on a single day, use the spans (Lab 4's report).

**Correct answer: D**

---

### Q3. The `tool_success` SLO is 99% over 30 days. Atlas makes about 200,000 tool calls a month, and 1,400 have errored so far this month. How much error budget is left?

*Related lecture: 9.1 SLIs for agents that leadership understands*

- **A.** 1% of the month, because the SLO is 99%.
  - *Explanation:* Incorrect. 1% is the allowed bad fraction, not what is left.
- **B.** 600 failed calls, 30% of the budget: the budget is 1% × 200,000 = 2,000 failed calls, and 2,000 − 1,400 = 600.
  - *Explanation:* Correct. The error budget is the number of bad events the SLO allows in the window. With 30% left, risky changes wait; the burn rate says how fast the rest is going.
- **C.** None: any failure breaches a 99% SLO.
  - *Explanation:* Incorrect. The SLO allows 1% failures; 1,400 of 200,000 is 0.7%.
- **D.** 98,600 calls: 99% of 200,000 minus the failures.
  - *Explanation:* Incorrect. That mixes good and bad events; the budget counts bad ones only.

**Correct answer: B**

---

### Q4. Two alert rules for tool errors are proposed. Rule 1: `rate(atlas_tool_calls_total{outcome="error"}[5m]) > 0.5`. Rule 2: `(sum(rate(atlas_tool_calls_total{outcome="error"}[5m])) by (tool) / sum(rate(atlas_tool_calls_total[5m])) by (tool)) > 0.10 and sum(rate(atlas_tool_calls_total[5m])) by (tool) > 0.1` with `for: 2m` and a `runbook` annotation. Which is better and why?

*Related lecture: 9.5 Alert rules and the runbook*

- **A.** Rule 1: it is simpler and fires faster.
  - *Explanation:* Incorrect. Simplicity is not the goal; 0.5 errors per second means different things at 2 RPS (25% failing) and 200 RPS (0.25% failing), and it has no guard against one failed call at low traffic, no `for` to absorb blips, and no runbook.
- **B.** Rule 2: it alerts on a *ratio* so the threshold means the same at any traffic level, the minimum-traffic guard stops a single error at 3 a.m. from paging (1 of 1 is 100%), `for: 2m` requires the condition to persist, and the runbook link turns a notification into an operation.
  - *Explanation:* Correct. Lab 6's four properties of a good alert rule. Rule 2 fires on `lookup_ticket` during the `retry_storm` replay and stays quiet on the base day.
- **C.** Neither: alerts should be on cost only.
  - *Explanation:* Incorrect. Tool errors are a leading indicator of both cost (retries) and quality (hand-offs); Incident 1's only red signal was tool errors.
- **D.** Both, with Rule 1 as a backup.
  - *Explanation:* Incorrect. Redundant, noisier rules cause alert fatigue, which lecture 9.5 lists as a failure mode in its own right.

**Correct answer: B**

---

### Q5. Which of these is a legitimate, low-cardinality dimension for the `atlas_cost_usd_total` counter, and which is not?

*Related lecture: 9.2 Code-along: Prometheus metrics from Atlas*

- **A.** `tenant` is not fine because departments may be renamed.
  - *Explanation:* Incorrect. Renames are rare, bounded events; the cardinality remains tiny.
- **B.** No labels at all is the only safe choice.
  - *Explanation:* Incorrect. Without `tenant` you cannot draw cost per department, which is the dashboard's main panel. Low cardinality, not zero cardinality.
- **C.** `tenant` and `model` are fine; `session_id` is not.
  - *Explanation:* Correct. Four tenants times a few models is a handful of series; `session_id` is unbounded and would create a new series per conversation. Sessions live in Langfuse, where per-session cost is a query over traces.
- **D.** `session_id` is fine because sessions are short-lived.
  - *Explanation:* Incorrect. Prometheus keeps series in memory and on disk long after the session ends; churn makes it worse, not better.

**Correct answer: C**

---

### Q6. Using the severities in `deploy/alerts.yml`, which pair is right: one alert that pages someone, and one that raises a ticket for the next business day?

*Related lecture: 9.5 Alert rules and the runbook*

- **A.** Page: `AtlasToolErrorRate` (any tool above 5% errors for 10 minutes). Ticket: `AtlasBudgetHardCapHit`.
  - *Explanation:* Incorrect, both reversed. With bounded tool retries a failing tool at 2 a.m. is a morning problem, while a tenant being refused is users locked out now.
- **B.** Page: `AtlasTenantCostAnomaly`. Ticket: `AtlasLatencyP95High`.
  - *Explanation:* Incorrect, both reversed. The cost anomaly is a ticket; p95 above 4 s for 10 minutes is the users' experience and pages.
- **C.** Page: `AtlasLatencyP95High` (p95 above 4 s for 10 minutes). Ticket: `AtlasTenantCostAnomaly` (a tenant's last hour above 2.5× its average hour over the previous day, and above $1, for 15 minutes).
  - *Explanation:* Correct. Page when users are hurting now or money is burning fast enough that it can't wait (`AtlasBudgetHardCapHit`, `AtlasRetryStorm`, the fast burn rate); ticket when the morning is soon enough. In the shipped file only `AtlasLatencyP95High` has a `runbook` annotation and none has an owner; Lab 6 and the capstone add them.
- **D.** Everything pages, so nothing is missed.
  - *Explanation:* Incorrect. An on-call who is paged for tickets stops reading pages.

**Correct answer: C**
