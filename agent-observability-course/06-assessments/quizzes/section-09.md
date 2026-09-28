# Quiz: SLOs and Alerting (Section 9)

| Field | Value |
|---|---|
| Udemy lecture | 9.7 Quiz: SLOs and alerting |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 9.1 to 9.6 |

---

### Q1. Atlas's task-success SLO is 99% over 30 days. In the last hour, 96% of requests were resolved. What is the burn rate, and what does it mean?

*Related lecture: 9.1 SLIs for agents that leadership understands*

- **A.** Burn rate cannot be computed without a full month of data.
  - *Explanation:* Incorrect. Burn rate is computed over a short window precisely so you can act before the month is over.
- **B.** Burn rate 0.96; the SLO is healthy because 96% is close to 99%.
  - *Explanation:* Incorrect. Burn rate is not the SLI value; it is how fast you are consuming the error budget relative to the allowed rate.
- **C.** Burn rate 4: the error budget is 1% (100% − 99%), the observed error rate is 4%, and 4% / 1% = 4, meaning at this rate the whole month's error budget is gone in 30 / 4 = 7.5 days.
  - *Explanation:* Correct. Burn rate = observed error rate / (1 − SLO). Multi-window burn-rate alerts (for example 14.4× over 1 h and 5 m for fast burn, 6× over 6 h and 30 m for slow burn) page on rate of consumption rather than on a single bad minute. `northwind.slo.burn_rate` implements this.
- **D.** Burn rate 3; the SLO is breached for the month.
  - *Explanation:* Incorrect arithmetic, and one bad hour does not breach a 30-day SLO; it consumes budget.

**Correct answer: C**

---

### Q2. Which Prometheus query gives the p95 request latency across all tenants, and what caveat applies?

*Related lecture: 9.2 Code-along: Prometheus metrics from Atlas*

- **A.** `quantile(0.95, atlas_request_duration_seconds_count)`; counts are quantile-able.
  - *Explanation:* Incorrect. `quantile` over a count series computes the quantile of counts across label sets, not of durations.
- **B.** `avg(atlas_request_duration_seconds_sum / atlas_request_duration_seconds_count)`; it is exact.
  - *Explanation:* Incorrect. That is the mean, which hides the tail (Section 7).
- **C.** `max(atlas_request_duration_seconds_bucket)`; buckets hold the slowest request.
  - *Explanation:* Incorrect. Buckets are cumulative counts of observations at or below `le`, not durations.
- **D.** `histogram_quantile(0.95, sum(rate(atlas_request_duration_seconds_bucket[5m])) by (le))`; the result is interpolated within the bucket that contains the 95th percentile, so precision is limited by bucket boundaries, which is why Atlas's buckets include the 4 s budget as a boundary.
  - *Explanation:* Correct. Summing by `le` across tenants first, then applying `histogram_quantile`, gives the global p95 at bucket resolution. For millisecond precision on a single day, use the spans (Lab 4's report).

**Correct answer: D**

---

### Q3. In the Grafana Atlas Ops dashboard, lecture 9.3 adds an annotation query that draws a vertical line whenever `atlas_build_info` changes. What problem does that solve during an incident?

*Related lecture: 9.3 Grafana: the Atlas Ops dashboard*

- **A.** It shows the release boundary on every panel, so "the regression started when p95 or cost changed" can be read against "the release happened at 12:30" without leaving the dashboard; Incident 2's `top_k` change is found this way, and Langfuse's `release` field does the same on the trace side.
  - *Explanation:* Correct. Releases are the most common cause of step changes; putting them on the time axis is the cheapest correlation you can buy.
- **B.** It forces Grafana to re-import the dashboard JSON.
  - *Explanation:* Incorrect. Provisioning and annotations are unrelated.
- **C.** It marks the moment the dashboard was refreshed.
  - *Explanation:* Incorrect. Annotations are about events in the system being observed, not about the viewer.
- **D.** It hides data from before the release.
  - *Explanation:* Incorrect. It adds a marker; nothing is hidden.

**Correct answer: A**

---

### Q4. Two alert rules for tool errors are proposed. Rule 1: `rate(atlas_tool_errors_total[5m]) > 0.5`. Rule 2: `(sum(rate(atlas_tool_errors_total[5m])) by (tool) / sum(rate(atlas_tool_calls_total[5m])) by (tool)) > 0.10 and sum(rate(atlas_tool_calls_total[5m])) by (tool) > 0.1` with `for: 2m` and a `runbook_url`. Which is better and why?

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

### Q6. Lecture 9.4 builds saved views and a cost dashboard in Langfuse filtered by tag. Given that Grafana already shows cost per tenant, what does the Langfuse view add?

*Related lecture: 9.4 Langfuse dashboards and saved views*

- **A.** Alerting, which Grafana cannot do.
  - *Explanation:* Incorrect. Grafana and Prometheus are the alerting path in this course.
- **B.** Nothing; it duplicates Grafana.
  - *Explanation:* Incorrect. They answer different questions from different data.
- **C.** Higher-resolution numbers, because Langfuse polls Prometheus more often.
  - *Explanation:* Incorrect. Langfuse does not read Prometheus; it aggregates its own traces.
- **D.** Drill-down: from "finance cost rose" in a Langfuse view you can click through to the sessions, users (hashed), prompt versions and individual traces that made up the number, and share that view with a stakeholder who will never open Grafana; metrics give the trend, traces give the explanation.
  - *Explanation:* Correct. Grafana is for on-call and SLOs; Langfuse views are for engineers and product owners investigating *which* traffic cost or scored what. Together they form the "see" and "explain" pair from lecture 1.5.

**Correct answer: D**
