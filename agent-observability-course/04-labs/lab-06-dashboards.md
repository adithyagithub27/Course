# Lab 6: Ship the Dashboard and One Alert

| Field | Details |
|---|---|
| **Section / lecture** | Section 9, lecture 9.6 |
| **Time estimate** | 60 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Bring up Prometheus and Grafana with Docker Compose, scrape Atlas's `/metrics`, import the Atlas Ops dashboard, then write one alert rule (tool error spike) and make it fire during a replayed `retry_storm`, with a runbook link on the alert. |
| **You will produce** | A running compose stack, `deploy/prometheus/alerts.yml` with your rule, a screenshot of the alert in `FIRING`, and `notes/lab-06.md` |

---

## Prerequisites

- Labs 1 to 5 complete (Lab 4 for the `retry_storm` intuition).
- Lectures 9.1 to 9.5 watched.
- Docker Desktop or Docker Engine with Compose v2 (`docker compose version`).
- Ports 8000 (Atlas), 9090 (Prometheus) and 3001 (Grafana) free. Grafana is on 3001 in this course because Langfuse takes 3000 in Lab 7.

## Offline note

This lab is entirely offline. Metrics come from Atlas's own `/metrics` endpoint, and the swarm drives Atlas with the mock LLM. No keys, no cost.

---

## Step 1: Look at the raw metrics

```bash
OFFLINE=1 make run
```

```bash
curl -s http://localhost:8000/metrics | grep -E '^atlas_' | head -30
```

Expected (after at least one request; send a curl from Lab 1 if the list is empty):

```text
atlas_requests_total{tenant="hr",model="gpt-4.1-mini",outcome="resolved"} 1.0
atlas_request_latency_seconds_bucket{tenant="hr",le="0.5"} 0.0
atlas_request_latency_seconds_bucket{tenant="hr",le="1.0"} 1.0
atlas_request_latency_seconds_bucket{tenant="hr",le="2.0"} 1.0
atlas_request_latency_seconds_bucket{tenant="hr",le="4.0"} 1.0
atlas_request_latency_seconds_bucket{tenant="hr",le="8.0"} 1.0
atlas_request_latency_seconds_bucket{tenant="hr",le="+Inf"} 1.0
atlas_request_latency_seconds_count{tenant="hr"} 1.0
atlas_request_latency_seconds_sum{tenant="hr"} 0.812
atlas_tokens_total{tenant="hr",model="gpt-4.1-mini",kind="input"} 1184.0
atlas_tokens_total{tenant="hr",model="gpt-4.1-mini",kind="output"} 58.0
atlas_cost_usd_total{tenant="hr",model="gpt-4.1-mini",feature="policy_question"} 0.000566
atlas_tool_calls_total{tool="search_knowledge_base",outcome="ok"} 1.0
atlas_tool_calls_total{tool="lookup_ticket",outcome="error"} 0.0
atlas_budget_decisions_total{tenant="hr",decision="allow"} 1.0
atlas_budget_spent_usd{tenant="hr"} 0.000566
atlas_model_fallbacks_total{from_model="gpt-4.1-mini",to_model="gpt-4.1-nano"} 0.0
```

Look at the label sets. `tenant` has 4 values, `model` 3 to 4, `tool` 5, `outcome` 3, `decision` 3. There is **no** `user_id`, `session_id` or `trace_id` label anywhere. That is the cardinality rule from lecture 5.5: each unique label combination is a separate time series in Prometheus memory, and a user id label on a histogram with 7 buckets across 4 tenants and 2,000 employees would be 56,000 series for one metric.

Questions for your notes: how many time series does `atlas_request_latency_seconds` produce at most? (Answer in the solution notes.)

> **Checkpoint 1:** you can read a counter, a histogram bucket and explain why no per-user labels exist.

---

## Step 2: Bring up Prometheus and Grafana

```bash
docker compose -f deploy/docker-compose.observability.yml up -d
docker compose -f deploy/docker-compose.observability.yml ps
```

Expected:

```text
NAME                 IMAGE                             STATUS         PORTS
atlas-otel-collector otel/opentelemetry-collector-contrib   Up 10 seconds  0.0.0.0:4317-4318->4317-4318/tcp
atlas-prometheus     prom/prometheus                   Up 10 seconds  0.0.0.0:9090->9090/tcp
atlas-grafana        grafana/grafana                   Up 10 seconds  0.0.0.0:3001->3000/tcp
```

`deploy/prometheus/prometheus.yml` scrapes `host.docker.internal:8000/metrics` every 15 s (on Linux the compose file adds `extra_hosts: host.docker.internal:host-gateway`). Check the target is up: open `http://localhost:9090/targets`; `atlas` should be `UP`.

If it says `DOWN` with a connection refused, Atlas is not running or is bound to `127.0.0.1` only; start it with `make run` (uvicorn binds 0.0.0.0).

> **Checkpoint 2:** Prometheus target `atlas` is UP.

---

## Step 3: Generate traffic and query it

Terminal 3:

```bash
OFFLINE=1 make swarm            # 2 RPS for 5 minutes, all tenants, seed 42
```

In Prometheus (`http://localhost:9090/graph`) run these, one at a time:

```promql
sum(rate(atlas_requests_total[1m])) by (tenant)
```

```promql
histogram_quantile(0.95, sum(rate(atlas_request_latency_seconds_bucket[5m])) by (le))
```

```promql
sum(increase(atlas_cost_usd_total[1h])) by (tenant)
```

```promql
sum(rate(atlas_tool_calls_total{outcome="error"}[5m])) by (tool) / sum(rate(atlas_tool_calls_total[5m])) by (tool)
```

Expected after two minutes of swarm: requests ≈ 0.5/s per tenant, p95 ≈ 2.1 s, cost accumulating, tool error ratio ≈ 0.01 to 0.02 for `lookup_ticket` (the mock has a 1.5% base error rate) and 0 for the rest.

Note about `histogram_quantile`: it interpolates inside the bucket that contains the 95th percentile, so with buckets `2.0` and `4.0` a true p95 of 2.14 s shows as something between 2.0 and 4.0 depending on the distribution. If you need p95 to the millisecond, that is what the spans and Lab 4's report are for. Dashboards need trends and thresholds; buckets are chosen so the budget (4 s) is a bucket boundary.

> **Checkpoint 3:** the four queries return data and you can explain the bucket-resolution caveat.

---

## Step 4: Import the Atlas Ops dashboard

Grafana: `http://localhost:3001` (admin / admin, then skip the password change for the lab). The Prometheus datasource and the dashboard are provisioned from `deploy/grafana/provisioning/`, so **Dashboards → Atlas Ops** should already exist. If you prefer to import by hand: **Dashboards → New → Import → Upload JSON** → `deploy/grafana/dashboards/atlas-ops.json`.

Panels, one per SLI from lecture 9.1:

| Panel | Query (simplified) | SLI |
|---|---|---|
| Requests / s by tenant | `sum(rate(atlas_requests_total[1m])) by (tenant)` | traffic |
| Task success rate | `sum(rate(atlas_requests_total{outcome="resolved"}[5m])) / sum(rate(atlas_requests_total[5m]))` | task success |
| p95 latency | `histogram_quantile(0.95, sum(rate(atlas_request_latency_seconds_bucket[5m])) by (le))` with a 4 s threshold line | latency |
| Tool error rate | errors / calls by tool | tool reliability |
| Cost per hour by tenant | `sum(increase(atlas_cost_usd_total[1h])) by (tenant)` | cost |
| Cost per resolved session | `sum(increase(atlas_cost_usd_total[1h])) / sum(increase(atlas_requests_total{outcome="resolved"}[1h]))` (per resolved request; per resolved *session* comes from the span store) | the number leadership asks for |
| Budget decisions | `sum(increase(atlas_budget_decisions_total[1h])) by (decision)` | budget health |
| Fallbacks and circuit state | `atlas_model_fallbacks_total`, `atlas_llm_retries_total` | reliability |

Use the **tenant** variable at the top to filter to `finance`. Add an annotation: **Dashboard settings → Annotations → New**, query `changes(atlas_build_info[1m]) > 0`, so a redeploy (which changes the `release` label on `atlas_build_info`) draws a vertical line. That is how you will see "the regression started at the release" in Section 11.

> **Checkpoint 4:** dashboard loads with live data; tenant filter works; the p95 panel shows the 4 s threshold line.

---

## Step 5: Write the alert rule

Open `deploy/prometheus/alerts.yml`. It has one example rule (cost anomaly). Add a tool error spike rule:

```yaml
groups:
  - name: atlas
    rules:
      - alert: AtlasToolErrorRate
        expr: |
          (
            sum(rate(atlas_tool_calls_total{outcome="error"}[5m])) by (tool)
            /
            sum(rate(atlas_tool_calls_total[5m])) by (tool)
          ) > 0.10
          and
          sum(rate(atlas_tool_calls_total[5m])) by (tool) > 0.1
        for: 2m
        labels:
          severity: page
          team: atlas-oncall
        annotations:
          summary: "Tool {{ $labels.tool }} error rate {{ $value | humanizePercentage }} over 5m"
          description: "More than 10% of calls to {{ $labels.tool }} are failing. Retries are multiplying cost; check the provider, the ticket API and the retry storm runbook."
          runbook_url: "https://github.com/<you>/agent-observability-course/blob/main/10-resources/runbooks/tool-error-spike.md"
```

Three deliberate choices, all from lecture 9.5:

- **Ratio, not count.** `> 0.10` of calls, so the rule behaves the same at 2 RPS in the lab and 200 RPS in production.
- **Minimum traffic guard.** `and ... > 0.1` calls/s stops a single failed call at 3 a.m. from paging anyone (1 error out of 1 call is a 100% error rate).
- **`for: 2m`.** Two consecutive minutes over threshold, so a 30-second blip does not page.

Reload Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

Open `http://localhost:9090/alerts`. `AtlasToolErrorRate` should show as **Inactive** (green).

> **Checkpoint 5:** the rule is loaded and inactive.

---

## Step 6: Make it fire

Stop the swarm and Atlas, restart Atlas with the retry storm scenario (the mock makes `lookup_ticket` fail 40% of the time and the agent retries), then swarm again:

```bash
OFFLINE=1 ATLAS_SCENARIO=retry_storm make run
```

```bash
OFFLINE=1 make swarm
```

Watch `http://localhost:9090/alerts`. Timeline you should see:

| Time | State | Why |
|---|---|---|
| 0:00-1:00 | Inactive | Rate window filling |
| ~1:00 | **Pending** (yellow) | Ratio crossed 0.10; the `for: 2m` clock starts |
| ~3:00 | **Firing** (red) | Sustained for 2 minutes |

In Grafana, **Alerting → Alert rules** shows the same rule (Grafana reads Prometheus rules through the datasource) and the **Tool error rate** panel shows `lookup_ticket` climbing to ~0.4. Take the screenshot with both the alert state and the panel visible.

Then stop the scenario (`Ctrl+C`, restart with `OFFLINE=1 make run`, run the swarm again) and watch the alert resolve after the error rate falls under 0.10 for the `for` window.

> **Checkpoint 6:** screenshot of `AtlasToolErrorRate` in FIRING with the `lookup_ticket` label, and evidence it resolved.

---

## Step 7: The runbook

Create `10-resources/runbooks/tool-error-spike.md` from `10-resources/runbook-template.md`. Minimum content:

```markdown
# Runbook: AtlasToolErrorRate

**Alert:** tool error ratio > 10% for 2 minutes on one tool.
**Impact:** users get "I couldn't look that up" answers; retries multiply cost (see Incident 1).

## First 5 minutes
1. Which tool? (`{{ $labels.tool }}`). Open Grafana → Tool error rate → filter by tool.
2. Is it one tenant? Open the Ops Console → Trace explorer → filter status=ERROR, tool=<tool>, last 15 min.
3. Read three failing tool spans. Exception type tells you: upstream 5xx (their outage), 4xx (our bad arguments = prompt/model change), timeout (their latency).

## Mitigation
- Upstream outage: enable degraded mode for that tool (`ATLAS_TOOL_DISABLED=lookup_ticket`), Atlas will hand off with a ticket instead of retrying.
- Retry storm: lower `ATLAS_MAX_RETRIES` to 0 for that tool; the alert clears when retries stop.
- Bad arguments after a release: check the release annotation; roll back the prompt label in Langfuse (lecture 4.4).

## Escalation
- After 15 minutes with no cause: page the platform team that owns the ticket API.

## After
- Postmortem within 48 h (template: 10-resources/postmortem-template.md).
```

Link it from the alert's `runbook_url`.

> **Checkpoint 7:** the alert carries a runbook link and the runbook answers "what do I do in the first five minutes".

---

## Stretch goal

1. Add a **multi-window burn-rate alert** for the task-success SLO (99% resolved): fire when the 1 h burn rate > 14.4 **and** the 5 m burn rate > 14.4 (fast burn), and a second rule for 6 h / 30 m > 6 (slow burn). `src/northwind/slo.py::burn_rate` has the maths; lecture 9.1 has the reasoning.
2. Load the `AtlasTenantCostAnomaly` rule from `deploy/alerts.yml` (hourly `increase(atlas_cost_usd_total[1h])` per tenant against the daily average) and make it fire with `make run PROM=1 SCENARIO=context_bloat` in one terminal and `make swarm RPS=5 DURATION=1200 SCENARIO=context_bloat` in another.
3. Route alerts to a webhook with Alertmanager (`deploy/alertmanager.yml`) and confirm the JSON payload includes the runbook URL.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Prometheus target DOWN, "connection refused" | Atlas bound to 127.0.0.1 or not running | `make run` (uvicorn binds 0.0.0.0); on Linux confirm `extra_hosts` is in the compose file |
| Target UP but `atlas_*` metrics missing | No requests yet | Counters appear after the first observation; run the swarm |
| `histogram_quantile` returns NaN | No samples in the window | Wait for the swarm; check the `[5m]` window has data |
| Grafana shows "No data" but Prometheus has data | Datasource URL wrong inside Docker | Datasource must be `http://atlas-prometheus:9090`, not `localhost` |
| Alert stuck in Pending | Ratio hovering around 0.10 | The mock's 40% rate should be well over; check `ATLAS_SCENARIO=retry_storm` was set on the Atlas process, not the swarm |
| Alert fires immediately with no traffic | Missing the minimum-traffic guard | Add the `and sum(rate(...)) > 0.1` clause |
| `curl -X POST /-/reload` returns 403 | Lifecycle API not enabled | Compose passes `--web.enable-lifecycle`; otherwise `docker compose restart atlas-prometheus` |
| Grafana on 3001 not reachable | Port already used | Change the host port in the compose file; the container port stays 3000 |

---

## Solution notes

Reference files: `03-code/deploy/docker-compose.observability.yml`, `03-code/deploy/prometheus/prometheus.yml`, `03-code/deploy/prometheus/alerts.yml`, `03-code/deploy/grafana/dashboards/atlas-ops.json`, `03-code/telemetry/metrics.py`.

Answer to the cardinality question: `atlas_request_latency_seconds` has one `tenant` label with 4 values and 7 buckets (6 boundaries plus `+Inf`), plus `_count` and `_sum`, so at most 4 × (7 + 2) = **36 series**. Add a `user_id` label for 2,000 employees and it becomes 72,000. Add `session_id` and it is unbounded. Identity belongs in spans (Langfuse `user_id`, `session_id`), never in metric labels.

A good alert rule in this lab has all four properties: a ratio, a minimum-traffic guard, a `for` duration, and a runbook URL. Missing any one loses points in the peer review. The most common weak submission alerts on `rate(atlas_tool_calls_total{outcome="error"}[5m]) > 0.5` (a count that means different things at different traffic levels and has no guard).

Key takeaways:

1. Metrics answer "how much, how often, how fast" per low-cardinality group; traces answer "why" for one request. Both are needed; neither replaces the other.
2. Histograms give you percentiles at bucket resolution. Choose bucket boundaries at your budgets.
3. An alert without a runbook is a notification. An alert with a runbook is an operation.
