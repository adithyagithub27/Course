# Lab 6: Ship the Dashboard and One Alert

| Field | Details |
|---|---|
| **Section / lecture** | Section 9, lecture 9.6 |
| **Time estimate** | 60 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Bring up the observability stack with Docker Compose, read Atlas's `/metrics`, open the provisioned Atlas Ops dashboard, then write one alert rule the repo doesn't ship yet (a step-limit spike: the runaway loop from Lecture 5.6) and make it fire, with a runbook link on the alert. |
| **You will produce** | A running stack, a new rule in `deploy/alerts.yml`, `10-resources/runbooks/step-limit-spike.md`, a screenshot of the alert firing, and `notes/lab-06.md` |

---

## Prerequisites

- Labs 1 to 5 complete.
- Lectures 9.1 to 9.5 watched.
- Docker Desktop or Docker Engine with Compose v2 (`docker compose version`).
- Free ports: 8000 (Atlas), 9091 (Prometheus), 3001 (Grafana), 4317/4318/8888 (Collector), 6006 (Phoenix). Grafana is on 3001 and Prometheus on 9091 so they don't collide with Langfuse (3000) and a local Prometheus (9090).

## Offline note

This lab is entirely offline: the Atlas container runs with `OFFLINE=1`, the swarm drives it, and the mock LLM answers. No keys, no cost. Prometheus and alert behaviour need the live stack; the offline replay never reaches Prometheus.

---

## Step 1: Look at the raw metrics

Before Docker, look at what Atlas exposes. Terminal 1:

```bash
OFFLINE=1 make run
```

Terminal 2: send one request (the Lab 1 curl), then:

```bash
curl -sL http://localhost:8000/metrics | grep -E '^atlas_' | grep -v _created | head -40
```

(`-L` matters: `/metrics` answers with a redirect to `/metrics/`.) Expected, abridged:

```text
atlas_requests_total{feature="policy_question",model="gpt-4.1-mini",outcome="resolved",tenant="hr"} 1.0
atlas_tokens_total{kind="input",model="gpt-4.1-mini",tenant="hr"} 9940.0
atlas_tokens_total{kind="output",model="gpt-4.1-mini",tenant="hr"} 315.0
atlas_cost_usd_total{feature="policy_question",model="gpt-4.1-mini",tenant="hr"} 0.00448
atlas_request_latency_seconds_bucket{feature="policy_question",le="3.0",tenant="hr"} 0.0
atlas_request_latency_seconds_bucket{feature="policy_question",le="4.0",tenant="hr"} 1.0
...
atlas_request_latency_seconds_count{feature="policy_question",tenant="hr"} 1.0
atlas_request_latency_seconds_sum{feature="policy_question",tenant="hr"} 3.3331
atlas_ttft_seconds_bucket{le="0.5",model="gpt-4.1-mini"} 1.0
atlas_agent_steps_bucket{le="2.0",tenant="hr"} 1.0
```

Look at the label sets: `tenant`, `model`, `outcome`, `feature`, `tool`, `kind`, `decision`. There is **no** `user_id`, `session_id` or `trace_id` label anywhere; `tests/integration/test_server.py` asserts it. That's the cardinality rule from Lecture 5.5: each unique label combination is a separate series in Prometheus memory.

Question for your notes: how many series can `atlas_request_latency_seconds` produce at most across the four tenants? (Answer in the solution notes.)

Stop the server (Ctrl+C) before Step 2: the stack runs its own Atlas container on port 8000.

> **Checkpoint 1:** you can read a counter and a histogram bucket and explain why no per-user labels exist.

---

## Step 2: Bring up the stack

```bash
make stack
docker compose -f deploy/docker-compose.observability.yml ps
```

`make stack` builds Atlas from `deploy/Dockerfile` and starts five services: `atlas` (port 8000, `OFFLINE=1`, exporting OTLP to the Collector), `otel-collector`, `phoenix`, `prometheus` (port 9091) and `grafana` (port 3001). The Atlas container reads `../.env`; leave the Langfuse keys out of it for this lab.

`deploy/prometheus.yml` scrapes `atlas:8000/metrics` (the compose service name) every 15 s, plus the Collector's own metrics, and loads `deploy/alerts.yml`. Open `http://localhost:9091/targets`: the `atlas` job should be `UP`.

> **Checkpoint 2:** Prometheus target `atlas` is UP.

---

## Step 3: Generate traffic and query it

```bash
make swarm RPS=2 DURATION=300
```

The swarm drives the containerised Atlas on `localhost:8000` with the seeded traffic plan. In Prometheus (`http://localhost:9091/graph`), run these one at a time:

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

```promql
sum(rate(atlas_requests_total{outcome="step_limit"}[5m])) / sum(rate(atlas_requests_total[5m]))
```

Expect requests split across the four tenants (ops the busiest), a p95 under four seconds (the latency histogram records the mock's simulated latency), cost climbing, and zero tool errors and zero step-limit outcomes on a normal day. Record what you see; numbers vary with how long the swarm has run.

About `histogram_quantile`: it interpolates inside the bucket that holds the 95th percentile. The latency buckets are 3.0 and 4.0 around the budget, so a p95 near the budget is accurate to within that bucket. Buckets are chosen so the 4 s budget is a boundary.

> **Checkpoint 3:** the queries return data and you can explain the bucket-resolution caveat.

---

## Step 4: Open the Atlas Ops dashboard

Grafana: `http://localhost:3001` (admin / admin). The Prometheus datasource (`http://prometheus:9090` inside the network) and the dashboard are provisioned from `deploy/grafana/provisioning/`, so **Dashboards → Atlas Ops** already exists. To import by hand instead: **Dashboards → New → Import → Upload JSON** → `deploy/grafana/dashboards/atlas-ops.json`.

It has 21 panels in four rows:

| Row | Panels |
|---|---|
| SLIs | task success, containment, p95 latency, cost per resolved session (1 h) |
| Traffic and latency | requests/s by tenant, latency p50/p95/p99, TTFT p95 by model, outcomes/s, agent steps p95, tool error rate by tool |
| Cost | cost/hour by tenant, by feature, tokens/s by kind, cache hit ratio, LLM retries and fallbacks/s, budget decisions/s |
| Quality and safety | judge score mean, feedback/h, guardrail events/h, telemetry export failures |

Plus a build-info table. Use the `tenant` and `feature` variables at the top to filter. The "Releases" annotation draws a line when `atlas_build_info` changes, so a redeploy is visible. Note the judge panel stays empty: the judge runs as a batch job and never writes `atlas_judge_score`.

> **Checkpoint 4:** the dashboard loads with live data and the tenant filter works.

---

## Step 5: Write a rule the repo doesn't have

Open `deploy/alerts.yml`. It already ships ten rules, including `AtlasToolErrorRate` (a tool above 5% errors for 10 minutes) and the task-success burn-rate pair. Nothing pages specifically when the agent starts hitting its step limit, which is the runaway loop from Lecture 5.6. The burn-rate rules count `step_limit` among bad outcomes, but they need the whole SLO to burn. Add a dedicated rule to the `atlas-slo` group:

```yaml
      - alert: AtlasStepLimitSpike
        expr: |
          (
            sum(rate(atlas_requests_total{outcome="step_limit"}[10m]))
            / sum(rate(atlas_requests_total[10m]))
          ) > 0.02
          and sum(rate(atlas_requests_total[10m])) > 0.05
        for: 5m
        labels: { severity: ticket, team: atlas-oncall }
        annotations:
          summary: "More than 2% of Atlas requests are hitting the step limit"
          runbook: "10-resources/runbooks/step-limit-spike.md"
```

Three deliberate choices, all from Lecture 9.5:

- **A ratio, not a count.** `> 0.02` of requests, so the rule means the same at 2 requests a second and at 200.
- **A minimum-traffic guard.** `and ... > 0.05` requests/s stops one stuck conversation at 3 a.m. from raising a ticket.
- **`for: 5m`.** A short burst doesn't page; five minutes of it does.

Reload Prometheus (the compose file enables the lifecycle API) and check the rule loaded:

```bash
curl -X POST http://localhost:9091/-/reload
```

Open `http://localhost:9091/alerts`: `AtlasStepLimitSpike` shows as inactive.

> **Checkpoint 5:** the rule is loaded and inactive.

---

## Step 6: Make it fire

Put the stack's Atlas into the `loop` scenario: add `ATLAS_SCENARIO=loop` to `.env` (the Atlas container reads it), recreate the container, and drive traffic:

```bash
docker compose -f deploy/docker-compose.observability.yml up -d atlas
make swarm RPS=2 DURATION=900
```

With `loop`, every ticket lookup fails and the model keeps retrying it until the default step limit (6) stops the request with outcome `step_limit`. Ticket lookups are about a tenth of the traffic, well over the 2% threshold. Watch `http://localhost:9091/alerts`: inactive, then **pending** once the ratio crosses 0.02, then **firing** after five minutes. In Grafana, "Outcomes / s" shows the `step_limit` series and "Agent steps p95" climbs to 6. Take one screenshot with the firing alert and those two panels.

Then remove `ATLAS_SCENARIO=loop` from `.env`, recreate the container the same way, keep the swarm running, and watch the alert resolve.

> **Checkpoint 6:** a screenshot of `AtlasStepLimitSpike` firing, and evidence it resolved.

---

## Step 7: The runbook

Create `10-resources/runbooks/step-limit-spike.md` from `10-resources/runbook-template.md`. Minimum content:

```markdown
# Runbook: AtlasStepLimitSpike

**Alert:** more than 2% of requests end at the step limit for 5 minutes.
**Impact:** users get "I wasn't able to complete this automatically"; each looping request costs up to six model calls.

## First 5 minutes
1. Which tool? Grafana → "Tool error rate by tool"; or the Ops Console Reliability page.
2. Is it one tenant? Filter the dashboard by `tenant`.
3. Open one looping trace (Ops Console → Traces, or Langfuse filtered on outcome `step_limit`): six `step n` spans, the same failing `execute_tool` span in each.

## Mitigation
- A failing tool: set `ATLAS_MAX_TOOL_RETRIES=2` so Atlas stops retrying it and says so (Lecture 5.6).
- A prompt or model change: check the release annotation; roll the prompt label back (`python -m app.prompts promote --version <n>`).

## Escalation
- After 15 minutes with no cause: the team that owns the failing tool.

## After
- Postmortem within 48 h (10-resources/postmortem-template.md).
```

The rule's `runbook` annotation points at this file.

> **Checkpoint 7:** the alert carries a runbook link and the runbook answers "what do I do in the first five minutes".

---

## Stretch goals

1. Read the two shipped burn-rate rules (`AtlasTaskSuccessBurnRateFast`: 14.4x over 1 h for 5 m; `AtlasTaskSuccessBurnRateSlow`: 6x over 6 h for 30 m) next to `src/northwind/slo.py::burn_rate`. Did your loop run move either of them? Why not, at this traffic level?
2. Make `AtlasToolErrorRate` fire: `ATLAS_SCENARIO=ticket_flaky` (the ticket service fails twice, then succeeds) in `.env`, recreate the container, swarm for 15 minutes.
3. Add a `runbook` annotation and an owner label to two more shipped rules. Only `AtlasLatencyP95High` has a runbook link today.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `make stack` fails: port 8000 in use | Your own `make run` is still up | Stop it; the stack runs its own Atlas |
| Prometheus target DOWN | The `atlas` container is still building or crashed | `docker compose -f deploy/docker-compose.observability.yml logs atlas` |
| Target UP but no `atlas_*` series | No requests yet | Counters appear after the first observation; run the swarm |
| `histogram_quantile` returns NaN | No samples in the window | Wait for the swarm to fill `[5m]` |
| Grafana "No data" but Prometheus has data | Datasource URL changed | It must be `http://prometheus:9090` (inside the network), not `localhost:9091` |
| `ATLAS_SCENARIO` change has no effect | Container not recreated | `docker compose -f deploy/docker-compose.observability.yml up -d atlas` |
| Alert stuck in pending | Ratio hovering near 0.02, or the guard not met | Raise `RPS`; check the `step_limit` series in "Outcomes / s" |
| `curl /metrics` prints nothing | Redirect not followed | `curl -sL` |

---

## Solution notes

Reference files: `03-code/deploy/docker-compose.observability.yml`, `03-code/deploy/prometheus.yml`, `03-code/deploy/alerts.yml`, `03-code/deploy/grafana/dashboards/atlas-ops.json`, `03-code/telemetry/metrics.py`. `AtlasStepLimitSpike` is the student's rule; it is not in the shipped `alerts.yml`.

Answer to the cardinality question: `atlas_request_latency_seconds` has two labels, `tenant` (4 values) and `feature` (7 values), and 13 bucket boundaries plus `+Inf`, plus `_count` and `_sum`: at most 4 × 7 × 16 = **448 series**. That's already a lot for one metric; add `user_id` for 4,800 employees and it becomes over two million. Identity belongs in spans (`user.id`, `session.id`), never in metric labels.

A good rule has all four properties: a ratio, a minimum-traffic guard, a `for` duration and a runbook link. The most common weak submission alerts on `rate(atlas_requests_total{outcome="step_limit"}[5m]) > 0.1`: a count that means different things at different traffic levels.

Key takeaways:

1. Metrics answer "how much, how often, how fast" per low-cardinality group; traces answer "why" for one request.
2. Histograms give percentiles at bucket resolution; put a bucket boundary at the budget.
3. An alert without a runbook is a notification. An alert with a runbook is an operation.
