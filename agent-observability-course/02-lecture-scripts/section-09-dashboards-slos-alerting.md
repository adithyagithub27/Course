# Section 9: Dashboards, SLOs and Alerting

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 42 minutes (7 lectures, including one lab intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `operations`, `warehouse`, `finance`, `sales`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Dashboard recordings: one panel per metric, the key number annotated, dark Grafana theme, 1920×1080 with the browser zoomed to 125%.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on prometheus-client (current) / langfuse 4.15. Grafana and Langfuse screens change: verify against the current UI before recording."

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.slo` (`SLO`, `error_budget`, `burn_rate`, `ATLAS_SLOS`), `telemetry/metrics.py` (`REQUESTS`, `FIRST_TOKEN_SECONDS`, `REQUEST_SECONDS`, `TOOL_CALLS`, `TOOL_ERRORS`, `LLM_TOKENS`, `LLM_COST`, `BUDGET_EVENTS`, `ANOMALIES`, `FALLBACKS`, `ESCALATIONS`, `GUARDRAIL_EVENTS`, `JUDGE_SCORE`, `JUDGE_COST`, `BUILD_INFO`), `app/server.py` (`/metrics` via `make_asgi_app()`), `deploy/docker-compose.observability.yml`, `deploy/prometheus.yml` (scrape config; assumed name), `deploy/alerts.yml` (Prometheus rules; assumed name), `deploy/grafana/dashboards/atlas-ops.json`, `10-resources/runbook-template.md`.

**The numbers card (one set of figures for the section, from Sections 6 to 8):**

| SLI | Normal week | SLO |
|---|---|---|
| Task success (judge `resolved` ≥ 0.7 on head sample, or thumbs up) | 83% | ≥ 80% weekly |
| Containment (sessions resolved without a human ticket, question intents only) | 78% | ≥ 75% weekly |
| Tool error rate (`atlas_tool_errors_total / atlas_tool_calls_total`) | 1.8% | < 3% over 1 h |
| First visible token p95 | 3.4 s | 95% of requests under 4 s, 30-day window |
| Cost per resolved session ($24.86 ÷ (4,000 × 0.83)) | $0.0075 | ≤ $0.010 weekly |
| Judge grounded (head sample) | 0.90 | ≥ 0.85 weekly |
| Error budget, latency SLO | 5% of 300,000 requests per 30 days = 15,000 slow requests | |
| `slow_provider` untuned (7.6): 72% of requests slow for 45 min | burn rate 14.5× | Atlas fast-burn page (6× over 30 m and 5 m) fires at 12:15 |

---

## Lecture 9.1: SLIs for agents that leadership understands

| Field | Value |
|---|---|
| ID | 9.1 |
| Title | SLIs for agents that leadership understands |
| Type | SL (slides + avatar) |
| Target duration | 8:00 (about 830 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Pick six SLIs that a director can read, set an SLO for each with a window, and use error budgets and burn rate to decide when to page. |
| Prerequisites | Sections 6 to 8 (every SLI here is a number those sections produced) |
| Files used | `src/northwind/slo.py` |

**Learning objectives**

1. Define the six Atlas SLIs and where each number comes from.
2. Write an SLO as target plus window, compute the error budget, and explain burn rate.
3. Choose multi-window burn-rate thresholds so a fast burn pages and a slow burn opens a ticket.

### Script

[AVATAR]

"Is Atlas doing well?" [PAUSE] Your director asks that in a meeting, and you have forty metrics. Forty is the same as zero. What they need is six numbers, each with a target, each green or red, and a rule for when the red one becomes a phone call. That's SLIs, SLOs and error budgets, and every number in this lecture is one you already produce.

[SLIDE 1: Six SLIs for Atlas]

| SLI | What it means to a director | Source |
|---|---|---|
| Task success | "Did people get their answer?" | judge `resolved` head sample, or thumbs up (8.2, 8.3) |
| Containment | "How often did it need a human?" | sessions without a human ticket, question intents only (5.2) |
| Tool error rate | "Are the systems it talks to healthy?" | `tool_errors / tool_calls` (7.3) |
| First visible token p95 | "Is it fast?" | `atlas_first_token_seconds` (7.2) |
| Cost per resolved session | "What does an answer cost?" | cost ÷ resolved sessions (6.3) |
| Judge grounded | "Is it making things up?" | judge `grounded` head sample (8.2) |

[AVATAR]

Six. Task success: did people get their answer, from the head-sampled judge or a thumbs up. Containment: how often it needed a human, measured on question intents only, because a password reset that creates a ticket is doing its job. Tool error rate: are the systems it talks to healthy. p95 first visible token: is it fast. Cost per resolved session: what an answer costs. And grounded: is it making things up. [PAUSE] Each one is a sentence a director can say back to you. That's the test of a good SLI. If you have to explain it, it's a metric, not an SLI.

[SLIDE 2: The SLOs]

| SLI | Normal | SLO | Window |
|---|---|---|---|
| Task success | 83% | ≥ 80% | weekly |
| Containment | 78% | ≥ 75% | weekly |
| Tool error rate | 1.8% | < 3% | 1 hour |
| First visible token | p95 3.4 s | 95% under 4 s | 30 days rolling |
| Cost per resolved session | $0.0075 | ≤ $0.010 | weekly |
| Grounded | 0.90 | ≥ 0.85 | weekly |

[AVATAR]

An SLO is a target and a window. Task success at least eighty percent, weekly. Tool errors under three percent over any hour. Ninety-five percent of requests under four seconds, over a rolling thirty days. Cost per resolved session under a cent. Notice the targets sit a little below normal. [PAUSE] An SLO at your current performance is a promise you'll break on the first bad Tuesday. Leave room. The room is called the error budget.

[SLIDE 3: Error budget]
- SLO: 95% of requests under 4 s over 30 days
- Traffic: 10,000 a day × 30 = 300,000 requests
- Error budget: 5% = 15,000 slow requests per 30 days, about 500 a day
- Normal day: p95 at 3.4 s means about 3% slow = 300 a day. You spend 60% of budget in a normal month
- The budget is a spending account: incidents draw it down; when it's empty, you stop shipping risk

[AVATAR]

Take the latency SLO. Ninety-five percent under four seconds means five percent may be slower. Three hundred thousand requests a month, so fifteen thousand slow ones are allowed. Five hundred a day. On a normal day about three percent are slow, three hundred, so a normal month spends sixty percent of the budget just existing. That leaves forty percent, six thousand slow requests, for incidents. [PAUSE] Here's the rule that makes the budget useful. When it's spent, you stop shipping risk: no prompt rollouts, no model swaps, until the window rolls forward. It's the number that ends the argument between "ship it" and "make it reliable."

[SLIDE 4: Burn rate]
- Burn rate = (fraction of bad requests right now) ÷ (fraction the SLO allows)
- Allowed: 5%. Observed 5% → burn rate 1: you'll use exactly the budget in 30 days
- `slow_provider` untuned: 72% slow → burn rate 14.5: the month's budget gone in about 2 days
- A loop that makes every request slow: burn rate 20: budget gone in 36 hours
- Page on burn rate, not on a single p95 reading

[AVATAR]

Burn rate is how fast you're spending the budget. Divide the fraction of bad requests now by the fraction the SLO allows. Five percent slow against five percent allowed is a burn rate of one: you'll use exactly the budget, no more. The slow provider from 7.6, untuned, made seventy-two percent of requests slow. Fourteen and a half. At that rate the whole month's budget is gone in about two days. [PAUSE] That number is why you page. Not because p95 crossed a line for one minute, but because at this rate, the promise breaks.

[SLIDE 5: Multi-window burn-rate alerts]

| Alert | Burn rate | Long window | Short window | Meaning at a 95% SLO | Action |
|---|---|---|---|---|---|
| Textbook fast burn (SRE workbook) | 14.4× | 1 h | 5 min | 72% of requests bad for an hour | page |
| **Atlas fast burn** | 6× | 30 min | 5 min | 30% of requests bad for half an hour | page |
| Atlas slow burn | 1× | 3 days | 6 h | on track to spend the whole budget | ticket |

- Both windows must exceed the rate: the long one proves it's real, the short one proves it's still happening
- The textbook numbers were written for 99.9% SLOs; at 95%, 14.4× means 72% of users are waiting, and a 1 h window would not fire on a 45-minute event
- On the untuned `slow_provider`, the Atlas fast-burn alert goes pending at 12:13 and fires at 12:15

[AVATAR]

The recipe comes from the SRE books: a burn-rate threshold checked over a long window and a short window. The long one proves the problem is real, the short one proves it hasn't already stopped. The textbook thresholds are fourteen point four times over an hour, six times over six hours, one times over three days. [PAUSE] Here's the catch for agents. Those numbers were written for ninety-nine point nine percent SLOs. At ninety-five percent, fourteen point four times means seventy-two percent of your users are waiting, and a one-hour window wouldn't fire on a forty-five-minute event at all. So Atlas tightens the fast alert: six times, thirty percent of requests slow, over thirty minutes and five minutes. That pages. And the slow burn stays at one times over three days and six hours: a ticket. On the untuned slow provider, the Atlas fast-burn alert goes pending at thirteen minutes past noon and fires at a quarter past. Fifteen minutes. Without it, you'd have found out from Slack at one.

[SCREEN: VS Code, `src/northwind/slo.py`]

[CODE: `src/northwind/slo.py` (excerpt)]

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class SLO:
    name: str
    target: float          # fraction of good events, e.g. 0.95
    window_days: int

    @property
    def allowed_bad_fraction(self) -> float:
        return 1.0 - self.target


def error_budget(slo: SLO, total: int, bad: int) -> dict[str, float]:
    budget = slo.allowed_bad_fraction * total
    return {"budget_events": budget, "spent_events": bad, "remaining_fraction": max(0.0, 1 - bad / budget) if budget else 0.0}


def burn_rate(slo: SLO, total: int, bad: int) -> float:
    if total == 0:
        return 0.0
    return (bad / total) / slo.allowed_bad_fraction


ATLAS_SLOS = {
    "latency": SLO("first_visible_token_under_4s", target=0.95, window_days=30),
    "task_success": SLO("resolved", target=0.80, window_days=7),
    "tool_errors": SLO("tool_calls_without_error", target=0.97, window_days=0),   # 1-hour window handled by the rule
}
```

Three functions, ten lines each, so the CI gate and the console compute the same thing Prometheus does. `error_budget` gives the budget in events and the fraction remaining. `burn_rate` is the division from the slide. And `ATLAS_SLOS` pins the targets in code, next to the tests, so a change to a promise is a pull request.

[SLIDE 6: Presenting to leadership]
- One page: six SLIs, target, this week, trend arrow, budget remaining
- Green, amber, red; no charts on the summary page
- Cost per resolved session and task success on the same line: quality and cost together
- "We have 40% of our latency budget left this month; we're pausing the model swap until it rolls over"
- The dashboard in 9.3 has this as its top row

[AVATAR]

And the meeting. One page. Six rows, target, this week, a trend arrow, budget remaining. Colours, no charts. Cost per resolved session and task success on the same line, so nobody optimises one by breaking the other. And the sentence that makes you sound like an operator: "We have forty percent of our latency budget left this month, so we're pausing the model swap until it rolls over." [PAUSE] That sentence is the entire point of SLOs. It turns reliability from a feeling into a budget line, and budgets are a language leadership already speaks.

### Recap

Six SLIs a director can say back to you, each with a target and a window, an error budget that says how much failure is allowed, and burn-rate alerts that page when the promise is about to break.

### Transition

The SLIs need numbers. Next, the code: Atlas's `/metrics` endpoint, the counters and histograms behind every SLI, and the compose stack that scrapes them.

### Speaker notes: common mistakes and Q&A

- **SLO at current performance.** Leave headroom; the budget is the headroom.
- **Too many SLIs.** Six is the ceiling for a leadership page. Everything else is a diagnostic panel.
- **Paging on p95.** A one-minute p95 spike pages you for nothing; burn rate over two windows doesn't.
- **Containment on all intents.** Ticket creation "fails" containment by design. Measure on question intents only.
- **The 14.4 / 6 / 1 recipe** comes from the Google SRE workbook; say so once, then explain why Atlas tightens the fast alert to 6× over 30 m at a 95% SLO. Students who copy the textbook numbers will never see the alert fire in Lab 6.

---

## Lecture 9.2: Code-along: Prometheus metrics from Atlas

| Field | Value |
|---|---|
| ID | 9.2 |
| Title | Code-along: Prometheus metrics from Atlas |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 650 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Mount `/metrics` with `make_asgi_app()`, define every counter and histogram with low-cardinality labels in one file, and scrape it with the compose stack. |
| Prerequisites | 9.1; 5.5 (cardinality); 7.2 (histograms) |
| Files used | `telemetry/metrics.py`, `app/server.py`, `deploy/docker-compose.observability.yml`, `deploy/prometheus.yml` |

**Learning objectives**

1. Mount the Prometheus ASGI app on FastAPI and read the exposition format.
2. Define the full Atlas metric set with a naming convention and a label allow-list, and explain each label's cardinality.
3. Bring up Prometheus and Grafana with Docker Compose and confirm the scrape.

### Script

[AVATAR]

Every SLI from the last lecture is a division. Slow requests over all requests. Tool errors over tool calls. Cost over resolved sessions. [PAUSE] Prometheus is the thing that does divisions over time, cheaply, for years. Today we give it the numerators and denominators, and we're going to be strict about labels, because the wrong label turns a cheap metric into a memory leak.

[SLIDE 1: One file, one convention]
- All metrics in `telemetry/metrics.py`; nothing defines a metric anywhere else
- Names: `atlas_<thing>_<unit>_total` for counters, `atlas_<thing>_seconds` for histograms
- Label allow-list: `tenant` (4), `feature` (6), `model` (4), `tool` (5), `kind`, `reason`, `action` (fixed small sets)
- Never: `user_id`, `session_id`, `trace_id`, free text
- Worst case series count: about 4 × 6 × 4 = 96 per metric; fine

[AVATAR]

One file, one convention. Counters end in `_total` with a unit. Histograms end in `_seconds` or the unit. And a label allow-list: tenant, feature, model, tool, and a few fixed enumerations like kind and reason. That's it. Never a user, session or trace id, never free text. Worst case, a metric with tenant, feature and model has about a hundred series. A metric with user id has four thousand today and forty thousand next year, and Prometheus keeps every one in memory. [PAUSE] Those ids live in the span store, where they belong.

[SCREEN: VS Code, `telemetry/metrics.py`]

[CODE: `telemetry/metrics.py` (the full set, excerpt)]

```python
from prometheus_client import Counter, Gauge, Histogram

LATENCY_BUCKETS = (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 20.0)

# traffic and latency (numerators and denominators for the latency SLO)
REQUESTS = Counter("atlas_requests_total", "Requests served", ["tenant", "feature", "outcome"])   # outcome: ok|refused|degraded|error
FIRST_TOKEN_SECONDS = Histogram("atlas_first_token_seconds", "Time to first visible token", ["feature"], buckets=LATENCY_BUCKETS)
REQUEST_SECONDS = Histogram("atlas_request_seconds", "Full answer time", ["feature"], buckets=LATENCY_BUCKETS)

# tools (tool error SLO)
TOOL_CALLS = Counter("atlas_tool_calls_total", "Tool invocations", ["tool"])
TOOL_ERRORS = Counter("atlas_tool_errors_total", "Tool invocations that raised", ["tool"])

# tokens and cost (Section 6)
LLM_TOKENS = Counter("atlas_llm_tokens_total", "Tokens by kind", ["model", "kind"])                 # kind: input|cached|output|reasoning
LLM_COST = Counter("atlas_llm_cost_usd_total", "LLM spend in USD", ["model", "tenant", "feature"])
BUDGET_EVENTS = Counter("atlas_budget_events_total", "Budget guard decisions", ["tenant", "action"])  # action: ok|degrade|refuse
ANOMALIES = Counter("atlas_cost_anomalies_total", "EWMA cost anomalies", ["tenant"])

# reliability (Section 7)
RETRIES = Counter("atlas_retries_total", "Retried calls", ["kind", "reason", "tenant"])
FALLBACKS = Counter("atlas_llm_fallbacks_total", "Model fallbacks", ["from_model", "to_model", "reason"])
ESCALATIONS = Counter("atlas_escalations_total", "Small-to-strong escalations", ["reason", "tenant"])

# quality and safety (Section 8)
GUARDRAIL_EVENTS = Counter("atlas_guardrail_events_total", "Guardrail outcomes", ["kind"])
JUDGE_SCORE = Histogram("atlas_judge_score", "Online judge scores", ["metric"], buckets=(0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 1.0))
JUDGE_COST = Counter("atlas_judge_cost_usd_total", "Judge spend in USD", ["model"])
FEEDBACK = Counter("atlas_feedback_total", "User feedback", ["tenant", "value", "reason"])

# release annotations (9.3)
BUILD_INFO = Gauge("atlas_build_info", "Always 1; labels carry the version", ["version", "prompt_version", "default_model"])
```

There's the whole set, and you've met most of it already in Sections 6 to 8. Two additions. `REQUESTS` with an `outcome` label, which is the denominator for almost everything and the numerator for refused and degraded rates. And `BUILD_INFO`, a gauge that's always one, whose labels carry the version, the prompt version and the default model. That's how Grafana draws a vertical line on the chart when you deploy. [PAUSE] Count the labels on each line. None has more than three, and every value is from a fixed set.

Why is cost a counter and not a gauge? Because a counter only goes up, and Prometheus can take its rate. `increase(atlas_llm_cost_usd_total[1h])` is spend per hour, `[1d]` is spend per day, `[7d]` is the week, all from one series, and a restart doesn't corrupt it because `increase` understands resets. A gauge of "today's spend" would need your code to know when today ends. Counters for anything you add up; gauges for anything you read off, like in-flight requests. Histograms for anything you take a percentile of.

Now the endpoint.

[SCREEN: `app/server.py`]

[CODE: `app/server.py` (excerpt)]

```python
from prometheus_client import make_asgi_app

app = FastAPI(title="Atlas")
app.mount("/metrics", make_asgi_app())          # Prometheus exposition at GET /metrics

BUILD_INFO.labels(version=settings.release, prompt_version=settings.prompt_version, default_model=settings.default_model).set(1)
```

One line mounts it. `make_asgi_app` gives you an ASGI app that renders the registry in exposition format, and FastAPI serves it at `/metrics`. Set `BUILD_INFO` once at startup.

One security note before we scrape it. The metrics endpoint has no PII, but it does show your traffic, your spend and your model names, and it's on the same port as the chat API. In production, bind it to an internal interface or put it behind the network policy that only Prometheus can reach. The compose stack keeps everything on one Docker network, which is fine for the lab and not a production design. [PAUSE] And one Prometheus habit: the scrape interval is fifteen seconds, so any `rate()` window should be at least a minute, four scrapes, or you'll get gaps. Our panels use five minutes.

[SCREEN: terminal]

```bash
make run &
curl -s localhost:8000/metrics | grep -E "^atlas_(requests_total|first_token_seconds_bucket\{feature=\"policy_question\",le=\"4.0\"\}|llm_cost_usd_total)"
```

[DEMO: output (after a few requests):]

```
atlas_requests_total{feature="policy_question",outcome="ok",tenant="operations"} 14.0
atlas_first_token_seconds_bucket{feature="policy_question",le="4.0"} 13.0
atlas_llm_cost_usd_total{feature="policy_question",model="gpt-4.1-mini",tenant="operations"} 0.04211
```

That's the format Prometheus scrapes. Fourteen requests. Thirteen of them under the four-second bucket. Four cents of spend. [PAUSE] The `le="4.0"` bucket is the whole latency SLO: requests under four seconds over all requests, straight from the histogram, no interpolation, because we put a bucket edge at the budget in 7.2.

Now the stack.

[SCREEN: `deploy/docker-compose.observability.yml` and `deploy/prometheus.yml`]

[CODE: `deploy/prometheus.yml` (excerpt) and compose (excerpt)]

```yaml
# deploy/prometheus.yml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: atlas
    static_configs:
      - targets: ["host.docker.internal:8000"]     # Atlas runs on the host; Linux: add extra_hosts in compose
rule_files:
  - /etc/prometheus/alerts.yml
```

```yaml
# deploy/docker-compose.observability.yml (services excerpt)
services:
  prometheus:
    image: prom/prometheus:latest            # pin a version before recording
    volumes: ["./prometheus.yml:/etc/prometheus/prometheus.yml", "./alerts.yml:/etc/prometheus/alerts.yml"]
    ports: ["9090:9090"]
  grafana:
    image: grafana/grafana:latest            # pin a version before recording
    environment: [GF_SECURITY_ADMIN_PASSWORD=atlas]
    volumes: ["./grafana/dashboards:/var/lib/grafana/dashboards", "./grafana/provisioning:/etc/grafana/provisioning"]
    ports: ["3001:3000"]
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    volumes: ["./otel-collector.yaml:/etc/otelcol/config.yaml"]
    ports: ["4318:4318"]
```

Prometheus scrapes Atlas every fifteen seconds and loads the alert rules we'll write in 9.5. Grafana loads dashboards from the folder, so `atlas-ops.json` is provisioned, not clicked. And the collector, which Section 13 covers in depth. Pin the image versions before you record; `latest` is for the screencast, not for the repo.

```bash
docker compose -f deploy/docker-compose.observability.yml up -d
OFFLINE=1 make swarm RPS=2
```

[DEMO: Prometheus UI, Status → Targets: `atlas` UP. Graph tab: `sum(rate(atlas_requests_total[1m]))` climbing to 2.]

Target up, two requests a second, and the SLI numbers are now a query away. Next lecture, we put them on a dashboard.

### Recap

One file defines every metric with a fixed label allow-list, `make_asgi_app()` mounts `/metrics` in one line, and the compose stack scrapes it every fifteen seconds with alert rules and provisioned dashboards.

### Transition

Next, Grafana: the Atlas Ops dashboard, one panel per SLI, a tenant variable, and release annotations from `atlas_build_info`.

### Speaker notes: common mistakes and Q&A

- **Defining metrics in two places.** Duplicate registration raises at import. One file.
- **`host.docker.internal` on Linux.** Needs `extra_hosts: ["host.docker.internal:host-gateway"]` on the Prometheus service. Say it on screen.
- **Counters reset on restart.** `rate()` and `increase()` handle it; raw values don't. Never graph a raw counter.
- **`BUILD_INFO` cardinality.** One series per version ever deployed; fine for years, but don't put a git SHA per commit if you deploy 50 times a day.
- **Verify** `Counter`, `Histogram`, `Gauge`, `make_asgi_app` on the installed prometheus-client; all present.

---

## Lecture 9.3: Grafana: the Atlas Ops dashboard

| Field | Value |
|---|---|
| ID | 9.3 |
| Title | Grafana: the Atlas Ops dashboard |
| Type | SC (screencast code-along) |
| Target duration | 9:00 (about 780 spoken words at ~140 wpm; remaining time is the dashboard) |
| One idea | Import `atlas-ops.json`, read the PromQL behind each SLI panel, filter by tenant with a variable, and mark releases with annotations from `atlas_build_info`. |
| Prerequisites | 9.2; the compose stack running |
| Files used | `deploy/grafana/dashboards/atlas-ops.json` |

**Learning objectives**

1. Import the dashboard and identify the SLO row, the cost row, the reliability row and the quality row.
2. Read and modify the PromQL for p95, the SLO ratio, tool error rate, cost per hour by tenant and cost per resolved session.
3. Add the `$tenant` variable and the release annotation query.

### Script

[AVATAR]

A dashboard is a set of questions with answers already on screen. [PAUSE] The Atlas Ops dashboard answers the six questions from 9.1 in its top row, and the "why" questions underneath. Let's import it, and then read the queries, because a dashboard you can't read is a dashboard you can't fix at three in the morning.

[SCREEN: Grafana at localhost:3001. Dashboards → the provisioned "Atlas Ops" opens. Full dashboard visible: four rows.]

It's already there, provisioned from the compose volume. If you're importing by hand: Dashboards, New, Import, upload `atlas-ops.json`, choose the Prometheus data source. [PAUSE] Four rows. SLOs at the top. Cost. Reliability. Quality and safety.

[SLIDE 1: Row 1: SLOs (the leadership row)]
- Task success (7 d): stat, from `atlas_judge_score` head-sample ratio
- First visible token p95 (5 m): stat with a red threshold at 4 s
- Latency SLO ratio (30 d): requests under 4 s ÷ all requests, target line at 95%
- Error budget remaining (30 d): gauge
- Tool error rate (1 h): stat, threshold 3%
- Cost per resolved session (7 d): stat, threshold $0.010

[SCREEN: zoom on the p95 panel; open Edit; the query is visible]

[CODE: PromQL behind row 1]

```promql
# p95 first visible token, last 5 minutes
histogram_quantile(0.95, sum by (le) (rate(atlas_first_token_seconds_bucket{feature=~"$feature"}[5m])))

# latency SLO ratio over 30 days: fraction under the 4 s bucket edge
sum(increase(atlas_first_token_seconds_bucket{le="4.0"}[30d])) / sum(increase(atlas_first_token_seconds_count[30d]))

# error budget remaining (target 0.95)
1 - (1 - (sum(increase(atlas_first_token_seconds_bucket{le="4.0"}[30d])) / sum(increase(atlas_first_token_seconds_count[30d])))) / 0.05

# tool error rate, 1 h
sum(rate(atlas_tool_errors_total[1h])) / sum(rate(atlas_tool_calls_total[1h]))

# cost per resolved session, 7 d (resolved sessions ≈ sessions × head-sample resolved rate)
sum(increase(atlas_llm_cost_usd_total{tenant=~"$tenant"}[7d]))
  / (sum(increase(atlas_requests_total{tenant=~"$tenant",outcome="ok"}[7d])) / 2.5 * 0.83)
```

Five queries, and they're the five SLIs. The p95 is `histogram_quantile` over the rate of the bucket counters, summed by `le`. The SLO ratio is the four-second bucket over the count, over thirty days, no quantile function at all, because the bucket edge is the budget. The error budget remaining is that ratio turned into a fraction of the five percent allowance. Tool error rate is errors over calls. [PAUSE] And cost per resolved session. Look at the denominator: requests divided by two point five for sessions, times the resolved rate. That's a Prometheus approximation, because sessions and resolution live in the span store. The exact number is on the Ops Console and in the weekly report; this panel is the trend. Label it "approx" on the panel. Honesty on the dashboard is a feature.

[SLIDE 2: Rows 2 to 4]
- Cost: spend per hour by tenant (stacked), by model, cache hit rate, budget events, anomalies
- Reliability: request rate by outcome, fallback rate, retries by reason, escalations by reason, in-flight by tenant
- Quality and safety: judge means by metric, feedback rate and score, guardrail rates, judge cost

[SCREEN: scroll through rows 2 to 4; pause on "spend per hour by tenant" and "fallback rate"]

[CODE: PromQL behind rows 2 and 3]

```promql
# spend per hour by tenant
sum by (tenant) (increase(atlas_llm_cost_usd_total[1h]))

# cache hit rate
sum(rate(atlas_llm_tokens_total{kind="cached"}[15m])) / sum(rate(atlas_llm_tokens_total{kind=~"input|cached"}[15m]))

# fallback rate (fallbacks per request)
sum(rate(atlas_llm_fallbacks_total[5m])) / sum(rate(atlas_requests_total[5m]))

# refused and degraded share
sum(rate(atlas_requests_total{outcome=~"refused|degraded"}[5m])) / sum(rate(atlas_requests_total[5m]))
```

Spend per hour by tenant is the showback as a stacked chart. Cache hit rate is cached over input-plus-cached tokens; if this drops, someone put a date at the front of the prompt. Fallback rate is the chart that told the whole story in 7.6. And the refused-and-degraded share is what the budget guard and the shedder are doing to users right now. [PAUSE] Every one of these is a question from Sections 6 and 7, answered continuously.

Here's how you read the dashboard during an incident, using the slow provider from 7.6 as the example. Row one: p95 stat is red. Row three: fallback rate flat at zero, retries flat, in-flight climbing. Row two: cost flat. That combination, red latency with nothing else moving, has exactly one meaning: the provider is slow and nothing is timing out. You knew the fix before you opened a trace. [PAUSE] Compare the tuned run: p95 green, fallback rate at eighteen percent, cost up a dollar. Everything moved a little, and that's what healthy resilience looks like. Learn the shapes. Most incidents have one.

Now the two features that make this a working dashboard instead of a pretty one.

[SCREEN: Dashboard settings → Variables. `$tenant` and `$feature`.]

[CODE: dashboard variables and the annotation query]

```
# variable: tenant   (type: query, multi-value, include All)
label_values(atlas_requests_total, tenant)

# variable: feature
label_values(atlas_requests_total, feature)

# annotation: releases   (type: Prometheus query, step 1m)
changes(atlas_build_info[2m]) > 0
#  title: Release   text: {{version}} / prompt {{prompt_version}} / {{default_model}}
```

The tenant variable is a `label_values` query, so it fills itself, and every panel filters on `tenant=~"$tenant"`. Pick finance and the whole dashboard becomes finance's dashboard. The feature variable does the same. [PAUSE] And the annotation. `changes(atlas_build_info[2m]) > 0` is true for one minute whenever the version labels change, which happens exactly when you deploy. Grafana draws a vertical line with the version, the prompt version and the model.

[DEMO: replay the seven days from 8.4 into Prometheus (`OFFLINE=1 make replay DAYS=7 PROM=1`). On the quality row, the judge `resolved` line drops on Wednesday. A vertical annotation line at Wednesday 14:10 reads "v1.6.0 / prompt v2 / gpt-4.1-mini". Hover shows the text.]

Here's why the annotation earns its place. Seven days replayed. The resolved line drops on Wednesday. And right there, at ten past two on Wednesday, a vertical line: version one point six, prompt v2. [PAUSE] Nobody had to correlate a deploy log with a chart. The chart correlated itself. That's the difference between a dashboard and a diagnosis, and it's one gauge and one query.

[SLIDE 3: Dashboard hygiene]
- Every panel has a unit and a threshold, or it's a diagnostic and lives in a collapsed row
- Top row is stats, not time series: red or green at a glance
- The JSON is in git; edits happen in the UI, then export, then commit (`make dashboard-export`)
- One dashboard per audience: Ops (this one), Finance (cost row only, weekly), Leadership (row 1 only)
- Annotations for releases, prompt label changes and incidents

[AVATAR]

Thresholds and colours come from the SLOs in 9.1, not from taste. The p95 stat turns amber at three point six seconds, ninety percent of budget, and red at four. Tool error rate turns amber at two percent and red at three. Cost per resolved session turns red at a cent. When a threshold changes, it changes in `slo.py` and in the JSON in the same pull request, and the CI gate in Section 13 checks they agree. A dashboard that disagrees with the SLO document is worse than no dashboard, because people trust the colours.

Hygiene. Every panel has a unit and a threshold, or it's a diagnostic and it collapses. The top row is stats, red or green. The JSON lives in git: edit in the UI, export, commit, so a dashboard change is a pull request. One dashboard per audience; finance gets the cost row, leadership gets row one. And annotate everything that could explain a change: releases, prompt labels, incidents.

### Recap

`atlas-ops.json` answers the six SLIs in its top row with PromQL you can read, filters everything by a `$tenant` variable, and marks every release with an annotation from `atlas_build_info`, so the chart explains itself.

### Transition

Grafana sees metrics. Langfuse sees traces and scores. Next, a short demo of the Langfuse views that answer the questions Grafana can't: which sessions, which users, which prompt version.

### Speaker notes: common mistakes and Q&A

- **Cost per resolved session on Prometheus.** It's an approximation; label it. The exact figure comes from the span store in `report.py`.
- **`histogram_quantile` with no `sum by (le)`.** Returns nonsense or nothing. Always aggregate by `le` first.
- **`increase` over 30 d on short retention.** Prometheus default retention is 15 days; the compose file sets `--storage.tsdb.retention.time=45d`. Verify on screen.
- **Annotation query step.** Set the annotation step to 1 m or `changes()` can miss a deploy between scrapes.
- **Grafana UI changes.** Menu paths move between versions; record the current ones.

---

## Lecture 9.4: Langfuse dashboards and saved views

| Field | Value |
|---|---|
| ID | 9.4 |
| Title | Langfuse dashboards and saved views |
| Type | DM (live demo) |
| Target duration | 5:00 (about 520 spoken words at ~140 wpm; remaining time is the UI) |
| One idea | Use Langfuse for the questions metrics can't answer, which sessions, which users, which prompt version, and save the views so stakeholders can open them without you. |
| Prerequisites | 9.3; Section 4 |
| Files used | Langfuse UI (screens change; verify before recording) |

**Learning objectives**

1. Build a cost-by-tag view and a score-by-tag view in Langfuse and read them against the Grafana cost row.
2. Use the session explorer to go from a drifted feature to the actual conversations.
3. Save and share a view with a stakeholder, and know what Langfuse is for versus Grafana.

### Script

[AVATAR]

Grafana told you policy questions got worse on Wednesday. It can't show you a policy question. [PAUSE] Langfuse can. This is a short demo of the four views I open every week, and how to hand them to someone who isn't you. The screens move between Langfuse versions, so if yours look different, the ideas don't.

[SLIDE 1: Grafana vs Langfuse]
- Grafana: rates, percentiles, budgets, alerts. Aggregates over time. No ids.
- Langfuse: traces, sessions, users, scores, prompts, datasets. Individual things. Every id.
- Question starts with "how much" or "how often": Grafana
- Question starts with "which" or "show me": Langfuse
- Both fed by the same spans and the same numbers (6.3)

[AVATAR]

The split. Grafana for how much and how often. Langfuse for which and show me. Same spans, same cost numbers, different questions.

[SCREEN: Langfuse project. Dashboards (or Metrics) view: cost over time grouped by the `tenant` tag, then by `feature`.]

View one: cost by tag. Group cost by the tenant tag, and it matches the Grafana stacked chart, which it should, because both came from `cost_details` in 6.3. Switch the grouping to feature, and policy questions dominate, like the showback said. [PAUSE] Where this beats Grafana: click a bar and you're looking at the generations behind it.

[SCREEN: Scores view: `judge_resolved` mean over time, grouped by `feature` tag; then filter to `policy_question`, last 14 days.]

View two: scores by tag. `judge_resolved` grouped by feature, last two weeks. Policy questions drop on Wednesday, same as Grafana. Now filter to just policy questions and set the score filter to under point five. [PAUSE] That's the low cluster from the drift report, as a list of traces. Open one. Input, the retrieved chunks, the answer, three scores, and the judge's reason: "answer says 30 days; context says 45." Two clicks from the chart to the sentence that's wrong.

[SCREEN: Sessions view: filter tag `policy_question`, sort by session length; open a 6-turn session.]

View three: the session explorer. Sessions are conversations. Filter to policy questions, sort by length, open a long one. Six turns, and you can read the whole thing: the employee asked, got a wrong number, pushed back, got it again, gave up and opened a ticket. That's the containment SLI failing, in a transcript. [PAUSE] Metrics said seventy-eight percent contained. This shows you what the other twenty-two percent feels like.

[SCREEN: Prompts view: `atlas-system`, versions 1 and 2 side by side, the `production` label on v2; the generations linked to v2 with their scores.]

View four: prompts. Version one and version two side by side, the diff highlighted: one added instruction. The production label on v2 since Wednesday. And because generations are linked to prompt versions, you can see scores per version right here: v1 resolved point eight five, v2 point seven six, on the same feature. [PAUSE] That's the evidence for the rollback, and in Section 11 you'll do the rollback by moving the label.

[SCREEN: Save the scores view as "Policy quality, 14 d"; share the link; the settings page showing a Viewer role.]

Now save it. Name the view, share the link, and give your stakeholder a viewer role, which is read-only. Your HR partner opens "Policy quality, fourteen days" every Monday, sees the same chart you see, and never needs Grafana or a Prometheus query. [PAUSE] Four views, saved, shared. That's most of the weekly review.

[SLIDE 2: The weekly review, in views]
- Cost by tenant and feature (Langfuse) against the showback (report.py)
- Scores by feature, 14 d, with the low-score filter saved
- Longest sessions this week, by feature
- Prompt versions with scores per version
- Grafana row 1 for the SLOs; this for the "which"

[AVATAR]

That's the weekly review. Cost by tenant against the report. Scores by feature with the low-score filter. The longest sessions. Prompt versions with their scores. And Grafana's top row for the SLOs. Fifteen minutes, every Monday, and nothing drifts for a month without someone noticing.

### Recap

Langfuse answers "which" and "show me": cost and scores by tag with click-through to traces, sessions to read failures as conversations, prompts with scores per version, and saved views a stakeholder can open with a viewer role.

### Transition

Dashboards are for when you're looking. Next, alerts, for when you're not: burn-rate rules, the cost anomaly alert, the tool error spike, and the runbook that goes with each.

### Speaker notes: common mistakes and Q&A

- **Verify the screens.** Langfuse's dashboards, metrics and saved-view features change between releases. Record against the current UI and say "your version may differ".
- **Sharing with edit rights.** Stakeholders get Viewer. Role names vary by version; check the project settings.
- **Cost mismatch between Langfuse and Grafana.** If they differ, someone sent `usage_details` without `cost_details`, and Langfuse priced it from its own table. 6.3 covers why we always send both.
- **Session view on Langfuse Cloud free tier.** Retention limits apply; Section 10 covers retention.

---

## Lecture 9.5: Alert rules and the runbook

| Field | Value |
|---|---|
| ID | 9.5 |
| Title | Alert rules and the runbook |
| Type | SC (screencast code-along) |
| Target duration | 7:00 (about 520 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Write three alert rules, latency burn rate, cost anomaly and tool error spike, each linked to a runbook entry, and adopt the rules that stop alert fatigue before it starts. |
| Prerequisites | 9.1 to 9.3; 6.7 (anomaly counter) |
| Files used | `deploy/alerts.yml`, `10-resources/runbook-template.md` |

**Learning objectives**

1. Write the multi-window burn-rate alert for the latency SLO in Prometheus rule syntax.
2. Write a cost anomaly alert on `atlas_cost_anomalies_total` and a tool error spike alert on the error ratio.
3. Fill the runbook template so every alert has an owner, a first query and a known fix.

### Script

[AVATAR]

An alert that fires and nobody knows what to do is noise with a pager attached. [PAUSE] Three rules today, and each one has a runbook entry before it goes live. That's not process for its own sake. It's the difference between "Atlas is slow, good luck" and "Atlas is slow; check fallback rate; if it's zero, lower the first-token timeout; here's the config line."

[SCREEN: VS Code, `deploy/alerts.yml`]

[CODE: `deploy/alerts.yml`]

```yaml
groups:
  - name: atlas-slo
    rules:
      # Latency SLO: 95% of requests under 4 s over 30 d. Atlas fast burn: 6x (30% slow) over 30 m AND 5 m (9.1).
      - alert: AtlasLatencyBurnRateFast
        expr: |
          (1 - sum(rate(atlas_first_token_seconds_bucket{le="4.0"}[30m])) / sum(rate(atlas_first_token_seconds_count[30m]))) / 0.05 > 6
          and
          (1 - sum(rate(atlas_first_token_seconds_bucket{le="4.0"}[5m])) / sum(rate(atlas_first_token_seconds_count[5m]))) / 0.05 > 6
        for: 2m
        labels: {severity: page, slo: latency}
        annotations:
          summary: "Atlas latency burn rate {{ $value | printf \"%.1f\" }}x: 30%+ of requests over 4 s for 30 min"
          runbook: "10-resources/runbook-template.md#latency-burn"
      - alert: AtlasLatencyBurnRateSlow
        expr: |
          (1 - sum(rate(atlas_first_token_seconds_bucket{le="4.0"}[3d])) / sum(rate(atlas_first_token_seconds_count[3d]))) / 0.05 > 1
          and
          (1 - sum(rate(atlas_first_token_seconds_bucket{le="4.0"}[6h])) / sum(rate(atlas_first_token_seconds_count[6h]))) / 0.05 > 1
        for: 30m
        labels: {severity: ticket, slo: latency}
        annotations: {summary: "Atlas latency on track to exhaust the 30-day budget", runbook: "10-resources/runbook-template.md#latency-burn"}

  - name: atlas-cost
    rules:
      - alert: AtlasCostAnomaly
        expr: sum by (tenant) (increase(atlas_cost_anomalies_total[10m])) >= 2
        for: 0m
        labels: {severity: page, slo: cost}
        annotations:
          summary: "Cost anomaly for {{ $labels.tenant }}: EWMA detector fired twice in 10 min"
          runbook: "10-resources/runbook-template.md#cost-anomaly"
      - alert: AtlasBudgetDegraded
        expr: sum by (tenant) (increase(atlas_budget_events_total{action="degrade"}[15m])) > 0
        labels: {severity: ticket, slo: cost}
        annotations: {summary: "{{ $labels.tenant }} is in economy mode (soft cap)", runbook: "10-resources/runbook-template.md#budget"}

  - name: atlas-tools
    rules:
      - alert: AtlasToolErrorSpike
        expr: sum by (tool) (rate(atlas_tool_errors_total[10m])) / sum by (tool) (rate(atlas_tool_calls_total[10m])) > 0.10
        for: 5m
        labels: {severity: page, slo: tools}
        annotations:
          summary: "{{ $labels.tool }} failing {{ $value | humanizePercentage }} of calls"
          runbook: "10-resources/runbook-template.md#tool-errors"
```

Three groups. The burn-rate alerts are the 9.1 recipe in PromQL: the bad fraction, one minus the under-four-seconds ratio, divided by the five percent allowance, over the long window and the short window, both above the threshold. The fast one uses Atlas's tightened numbers, six times over thirty minutes and five minutes, and pages after two minutes. The slow one uses the textbook one times over three days and six hours, and opens a ticket after thirty minutes. [PAUSE] Cost: the EWMA detector from 6.7 firing twice in ten minutes for one tenant pages, because one firing can be a lunch rush; two is a pattern. Economy mode is a ticket, because the guard already handled it. Tools: any tool failing more than ten percent of calls for five minutes pages, with the tool name in the summary. And every rule has a `runbook` annotation. That's the link in the page.

[SCREEN: `10-resources/runbook-template.md`, the `#latency-burn` entry filled in]

[CODE: runbook entry (excerpt)]

```markdown
## latency-burn  (AtlasLatencyBurnRateFast / Slow)
Owner: Atlas on-call (#atlas-ops). Severity: page (fast) / ticket (slow).
First look (2 min): Grafana "Atlas Ops" row 3: fallback rate, retries by reason, in-flight by tenant.
Decision tree:
  - fallback rate ≈ 0 and p95 high  → provider is slow, not failing. Lower `llm_first_token_timeout_s` (config), redeploy. (7.6)
  - fallback rate high, cost rising → fallbacks working; check which to_model; if gpt-4.1 > 50%, add capacity on atlas-fast. (7.4)
  - one tenant's in-flight at its cap → burst; raise that tenant's semaphore temporarily; open a showback ticket. (7.5)
  - retries by reason = RateLimitError → 429s; check provider status; consider second provider. (7.5)
Verify: p95 panel back under 4 s for 10 min; burn rate < 1.
Postmortem needed if: fast burn > 30 min, or budget remaining < 20%.
```

Owner, severity, and a two-minute first look: three panels to open. Then a decision tree keyed on what those panels show, with the fix and the lecture that explains it. Fallback rate near zero with high p95: slow provider, lower the timeout. Fallback rate high: it's working, check where the traffic went. One tenant capped: a burst. Rate limits: the provider. Then how to verify it's fixed, and when a postmortem is required. [PAUSE] The whole entry fits on one screen, because at three in the morning nobody scrolls.

[SCREEN: terminal, then Prometheus Alerts page]

```bash
OFFLINE=1 RELIABILITY=v1 make replay SCENARIO=slow_provider PROM=1
```

[DEMO: Prometheus → Alerts. At 12:13 `AtlasLatencyBurnRateFast` goes PENDING, at 12:15 FIRING, with the summary and runbook link. Nothing else fires. Then the tuned replay: the alert never leaves inactive; `AtlasCostAnomaly` stays quiet; the Grafana cost row shows the $1.20 fallback bump but no alert, correctly.]

The untuned slow provider. Twelve thirteen, pending. Twelve fifteen, firing, with the runbook link. Nothing else fires: no cost alert, no tool alert, because nothing else is wrong. Then the tuned run: the alert never fires, the cost row shows the dollar-twenty of fallbacks, and the anomaly detector correctly ignores it, because a dollar twenty over forty-five minutes is inside three standard deviations. [PAUSE] One alert, for the one real problem, with the fix attached. That's the standard.

[SLIDE 1: Alert fatigue rules]
- Page only on user-facing symptoms and budget burn; everything else is a ticket
- Every alert has a runbook entry with an owner, or it doesn't ship
- Two windows for anything rate-based; `for:` on anything else
- Review the alert log weekly: any alert that fired 3× with no action gets deleted or demoted
- Test every alert with a replay scenario before it goes live; it's in Lab 6

[AVATAR]

Five rules against fatigue. Page only for symptoms users feel and for budget burn. Every alert has a runbook and an owner, or it doesn't merge. Two windows for rates, a `for:` clause for everything else. Review the alert log weekly, and delete anything that fired three times without anyone acting. And test every alert with a replay before it goes live. [PAUSE] An alert you've never seen fire is an alert you can't trust, the same way as a test.

### Recap

Three rule groups, latency burn rate with two windows, cost anomaly twice in ten minutes, and tool error ratio over ten percent, each with a runbook entry that has an owner, a two-minute first look and a decision tree.

### Transition

Lab 6 puts it together: stack up, dashboard live, and one alert that fires during a replay.

### Speaker notes: common mistakes and Q&A

- **Burn-rate expression without the `and`.** One window alone flaps. Both windows, always.
- **Alerting on the raw anomaly counter.** `increase(...[10m]) >= 2` is the debounce. One firing is a warning, not a page.
- **Runbook as a wiki page nobody updates.** Keep it in the repo next to the rules; the annotation links to the file.
- **Alertmanager routing** (who gets paged) is out of scope; say so, and point to the compose file's commented Alertmanager service.
- **Verify** rule syntax against the Prometheus version in the compose file.

---

## Lecture 9.6: Lab 6: Ship the dashboard and one alert

| Field | Value |
|---|---|
| ID | 9.6 |
| Title | Lab 6: Ship the dashboard and one alert |
| Type | LAB (guided lab; short video intro, work off-video) |
| Target duration | Video 2:30 (about 200 spoken words at ~140 wpm, plus slide time); lab work 45 to 60 minutes |
| One idea | Bring up the compose stack, get the Atlas Ops dashboard live on replayed traffic, and make one alert fire and clear during a scenario. |
| Prerequisites | 9.1 to 9.5; Docker installed |
| Files used | `04-labs/lab-06-dashboards.md`, `deploy/docker-compose.observability.yml`, `deploy/alerts.yml`, `deploy/grafana/dashboards/atlas-ops.json` |

**Learning objectives**

1. Run the observability compose stack and confirm the scrape target is up.
2. Verify every top-row panel shows data during a replay, and add one panel of your own.
3. Trigger, observe and clear one alert with a replay scenario, and screenshot both states.

### Script

[AVATAR]

Lab six is the one where it all appears on screen. [PAUSE] Compose stack up. Dashboard live. One alert that fires and clears. Forty-five minutes if Docker behaves.

[SCREEN: `04-labs/lab-06-dashboards.md`, the checklist]

Bring up the stack with the compose file, confirm the `atlas` target is up in Prometheus, and replay a normal day with `PROM=1` so the metrics flow. Open the Atlas Ops dashboard and check every panel in the top row has a number. Then add one panel of your own: the lab suggests escalation rate by reason, but anything from the metric set counts, and it has to have a unit and a threshold.

Then the alert. Replay the `retry_storm` scenario. `AtlasToolErrorSpike` should go pending, then firing, for `create_ticket`. Screenshot it. Fix it: the lab tells you which config flag ends the storm. Replay again, and screenshot the alert clearing.

[SLIDE 1: Lab 6 checklist]
- `docker compose up`, target UP
- Top row populated during a normal replay
- One new panel with unit and threshold, exported to `atlas-ops.json`
- `retry_storm`: `AtlasToolErrorSpike` firing, screenshot; fixed and cleared, screenshot
- Stretch: write a fourth alert for refusal rate (8.4) with its runbook entry
- Submit: three screenshots and the exported JSON diff

[AVATAR]

The stretch goal is a fourth alert, for refusal rate from 8.4, and its runbook entry. Write the runbook first. If you can't say what someone should do when it fires, it isn't ready to fire.

### Recap

Lab 6 ships the stack, the dashboard and one alert that provably fires and clears.

### Transition

Before the lab, the Section 9 quiz.

### Speaker notes: common mistakes and Q&A

- **Metrics not appearing.** Usually `host.docker.internal` on Linux; the lab has the `extra_hosts` fix.
- **Alert stuck pending.** The `for:` clause needs the condition to hold; the storm scenario runs 2 hours of replay in a few minutes, so check the replay's time compression flag.
- **Editing JSON by hand.** Edit in the UI, export with `make dashboard-export`.

---

## Lecture 9.7: Quiz: SLOs and alerting

| Field | Value |
|---|---|
| ID | 9.7 |
| Title | Quiz: SLOs and alerting |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 120 spoken words at ~140 wpm, plus slide time) |
| One idea | Check you can compute an error budget and a burn rate, read PromQL for an SLI, and choose page versus ticket. |
| Prerequisites | 9.1 to 9.5 |
| Files used | `06-assessments/quizzes/section-09.md` (6 questions) |

**Learning objectives**

1. Compute an error budget and a burn rate from traffic and an SLO.
2. Read a PromQL expression and say which SLI it computes.

### Script

[AVATAR]

Six questions. One error budget calculation from an SLO and a traffic number. One burn rate from an observed bad fraction. Two PromQL expressions to identify: which SLI, and what's wrong with one of them. One on page versus ticket for a given alert. And one on which label would break Prometheus.

[SLIDE 1: Quiz: 6 questions]
- Error budget and burn rate arithmetic
- Reading PromQL
- Page vs ticket
- Label cardinality

[AVATAR]

A tip: burn rate is just observed bad fraction over allowed bad fraction. Write both fractions down first.

### Recap

The quiz checks that you can turn an SLO into a budget and a burn rate, and read the queries behind the dashboard.

### Transition

Atlas is observable end to end. Next section, we make sure that observability doesn't become your next data breach: masking, retention, tenant separation and what the regulations expect you to keep.

### Speaker notes: common mistakes and Q&A

- Most-missed: "SLO 99%, 300,000 requests, error budget?" Answer: 3,000. Students who computed 15,000 used the 95% from the lecture.
- Second: the PromQL with `histogram_quantile` and no `sum by (le)`; the answer is "it doesn't aggregate correctly".
