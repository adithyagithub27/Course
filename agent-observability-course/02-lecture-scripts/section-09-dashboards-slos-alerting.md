# Section 9: Dashboards, SLOs and Alerting

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 42 minutes (7 lectures, including one lab intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `ops`, `finance`, `hr`, `eng`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Dashboard recordings: one panel per metric, the key number annotated, dark Grafana theme, 1920×1080 with the browser zoomed to 125%.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on prometheus-client (current) / langfuse 4.15. Prometheus v2.55.1 and Grafana 11.3.1 as pinned in `deploy/docker-compose.observability.yml`. Grafana and Langfuse screens change: verify against the current UI before recording."
> **Live-stack note:** Prometheus and Grafana only see a running Atlas. The path is `make stack` (collector, Prometheus, Grafana and Atlas itself in Docker) and `make swarm` (seeded traffic against it). `make replay` writes to the span store only and never reaches Prometheus. The stack exposes Atlas on :8000, Prometheus on :9091 and Grafana on :3001 (admin / admin).

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.slo` (`SLI`, `SLO`, `DEFAULT_SLOS`, `compute_slis`, `error_budget_remaining`, `burn_rate`, `BURN_RATE_ALERTS`), `telemetry/metrics.py` (`REQUESTS` = `atlas_requests_total{tenant,model,outcome,feature}`, `LATENCY` = `atlas_request_latency_seconds{tenant,feature}`, `TTFT` = `atlas_ttft_seconds{model}`, `TOKENS`, `COST`, `TOOL_CALLS`, `TOOL_LATENCY`, `LLM_RETRIES`, `FALLBACKS`, `BUDGET_DECISIONS`, `BUDGET_SPENT`, `GUARDRAIL`, `JUDGE_SCORE`, `FEEDBACK`, `INFLIGHT`, `QUEUE_WAIT`, `SHED`, `EXPORTER_FAILURES`, `BUILD_INFO`; `ALLOWED_LABELS`, `set_build_info`, `metrics_app`), `app/server.py` (`/metrics`), `deploy/docker-compose.observability.yml`, `deploy/prometheus.yml`, `deploy/alerts.yml` (10 rules), `deploy/grafana/dashboards/atlas-ops.json`, `10-resources/runbook-template.md`.

**The numbers card for this section (from `01-curriculum/numbers-card.md` and the shipped `deploy/` files):**

| Item | Value |
|---|---|
| SLIs on the baseline day (`make console-text`, `make report`) | task_success 0.993 (target 0.95) · containment 0.989 (0.80) · tool_success 1.000 (0.99) · latency 0.993 (0.95) · cost 1.000 (0.90) · quality 0.986 (0.90); all OK |
| Latency, baseline day | p50 3,232 ms · p95 3,827 ms (budget p95 4,000 ms); per-generation TTFT p95 652 ms |
| Cost per resolved session | $0.0144 (baseline) · $0.0048 per session after the Section 6 levers |
| Shipped alert rules (`deploy/alerts.yml`) | `AtlasLatencyP95High` p95 > 4 s for 10m (page) · `AtlasTaskSuccessBurnRateFast` 14.4× over 1h for 5m (page) · `AtlasTaskSuccessBurnRateSlow` 6× over 6h for 30m (ticket) · `AtlasToolErrorRate` > 5% per tool (ticket) · `AtlasTenantCostAnomaly` hourly > 2.5× previous day's average hour and > $1 (ticket) · `AtlasBudgetHardCapHit` (page) · `AtlasRetryStorm` > 0.2 retries per request (page) · `AtlasJudgeScoreLow` (ticket; cannot fire as shipped, 9.5) · `AtlasNegativeFeedbackSpike` > 40% negative (ticket) · `AtlasTelemetryExportFailures` > 20 in 10m (ticket) |
| Task-success SLO in the burn-rate rules | 95%; bad = outcome `error`, `step_limit`, `tool_error` or `timeout` |
| Prometheus retention | 45 days (`--storage.tsdb.retention.time=45d`), longer than the 28-day SLO window in `slo.py` |

---

## Lecture 9.1: SLIs for agents that leadership understands

| Field | Value |
|---|---|
| ID | 9.1 |
| Title | SLIs for agents that leadership understands |
| Type | SL (slides + avatar, with one code and terminal beat) |
| Target duration | 8:00 (about 790 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Pick six SLIs that a director can read, set an SLO for each with a window, and use error budgets and burn rate to decide when to page. |
| Prerequisites | Sections 6 to 8 (every SLI here is a number those sections produced) |
| Files used | `src/northwind/slo.py`, `deploy/alerts.yml`, `make console-text`; Diagram D8 "SLO, error budget, burn rate" |

**Learning objectives**

1. Define Atlas's six SLIs as `slo.py` computes them and where each number comes from.
2. Write an SLO as target plus window, compute the error budget, and explain burn rate.
3. Read the burn-rate alerts Atlas ships (14.4× over 1 hour pages, 6× over 6 hours opens a ticket) and say what each means at a 95% SLO.

### Script

[AVATAR]

"Is Atlas doing well?" [PAUSE] Your director asks that in a meeting, and you have forty metrics. Forty is the same as zero. What they need is six numbers, each with a target, each green or red, and a rule for when the red one becomes a phone call. That's SLIs, SLOs and error budgets, and every number in this lecture is one you already produce.

[SLIDE 1: Six SLIs for Atlas (`northwind.slo.compute_slis`)]

| SLI | What it means to a director | Good events / all events |
|---|---|---|
| Task success | "Did requests end well?" | resolved or escalated to a human / all requests |
| Containment | "How often did it manage alone?" | resolved / all requests |
| Tool success | "Are the systems it talks to healthy?" | tool calls without error / all tool calls |
| Latency | "Is it fast?" | requests under 4 s / all requests |
| Cost | "Is it within budget?" | sessions under $0.05 / all sessions |
| Quality | "Are the answers good?" | judged answers scoring ≥ 0.7 / all judged |

[AVATAR]

Six. Task success: did requests end well, answered or handed cleanly to a person. Containment: how often Atlas managed alone. Tool success: are the systems it talks to healthy. Latency: the share of requests under four seconds. Cost: the share of sessions under five cents. And quality: the share of judged answers the judge rated at least point seven. [PAUSE] Each one is a sentence a director can say back to you. That's the test of a good SLI. If you have to explain it, it's a metric, not an SLI. And every one is a ratio of good events to all events, which is what makes the arithmetic that follows work.

[SCREEN: terminal, `make console-text`, scrolled to the SLOs block]

```
-- SLOs ------------------------------------------------------------------------
task_success   value=0.993 target=0.95 budget_left=0.859 burn=0.14 OK
containment    value=0.989 target=0.8 budget_left=0.944 burn=0.06 OK
tool_success   value=1.000 target=0.99 budget_left=1.0 burn=0.0 OK
latency        value=0.993 target=0.95 budget_left=0.866 burn=0.13 OK
cost           value=1.000 target=0.9 budget_left=1.0 burn=0.0 OK
quality        value=0.986 target=0.9 budget_left=0.859 burn=0.14 OK
```

Here they are on the replayed day, straight from `slo.py`. Task success ninety-nine point three percent against a target of ninety-five. Containment ninety-nine against eighty. Latency ninety-nine point three against ninety-five. All green. Two columns you haven't met yet: budget left, and burn. That's the rest of this lecture.

[SLIDE 2: The SLOs (`DEFAULT_SLOS`, 28-day window)]

| SLI | Replayed day | SLO |
|---|---|---|
| Task success | 0.993 | ≥ 0.95 |
| Containment | 0.989 | ≥ 0.80 |
| Tool success | 1.000 | ≥ 0.99 |
| Latency (under 4 s) | 0.993 | ≥ 0.95 |
| Cost (sessions under $0.05) | 1.000 | ≥ 0.90 |
| Quality (judged ≥ 0.7) | 0.986 | ≥ 0.90 |

[AVATAR]

An SLO is a target and a window. Task success at least ninety-five percent. Latency: ninety-five percent of requests under four seconds. All over a rolling twenty-eight days in `slo.py`. Notice the targets sit below normal. [PAUSE] An SLO at your current performance is a promise you'll break on the first bad Tuesday. Leave room. The room is called the error budget.

[SLIDE 3: Error budget (latency SLO)]

Diagram: D8 build 2, error budget.

- SLO: 95% of requests under 4 s over 28 days
- Traffic: 10,184 a day; 5% of that is about 509 slow requests a day you may spend
- Normal day: 0.7% slow, about 68 requests; `budget_left` 0.866 means 87% of the day's allowance unspent
- The budget is a spending account: incidents draw it down; when it's empty, you stop shipping risk

[AVATAR]

Take the latency SLO. Ninety-five percent under four seconds means five percent may be slower. Ten thousand requests a day, so about five hundred slow ones a day are allowed. On the replayed day, sixty-eight were slow, and that's the `budget_left` of point eight seven: eighty-seven percent of the allowance unspent. [PAUSE] Here's the rule that makes the budget useful. When it's spent, you stop shipping risk: no prompt rollouts, no model swaps, until the window rolls forward. It's the number that ends the argument between "ship it" and "make it reliable."

[SLIDE 4: Burn rate]
- Burn rate = (fraction of bad events now) ÷ (fraction the SLO allows)
- Allowed: 5%. Observed 5% → burn rate 1: exactly the budget over the window
- Baseline day: latency burn 0.13, task success 0.14
- The slow provider from 7.6: 74% of requests in the afternoon window over 4 s → burn 14.8× for four hours
- Page on burn rate over a window, not on a single reading

[AVATAR]

Burn rate is how fast you're spending the budget. Divide the fraction of bad events now by the fraction the SLO allows. Five percent bad against five percent allowed is a burn rate of one: you'll use exactly the budget, no more. The normal day burns at about a seventh of that. Now the slow provider from 7.6: three in four requests in the afternoon window were over four seconds. That's a burn rate of almost fifteen, for four hours. [PAUSE] That number is why you page. Not because p95 crossed a line for one minute, but because at this rate, the promise breaks.

[SLIDE 5: The burn-rate alerts Atlas ships (`deploy/alerts.yml`, task-success SLO 95%)]

| Rule | Burn rate | Window | `for` | Bad fraction it takes at 95% | Severity |
|---|---|---|---|---|---|
| `AtlasTaskSuccessBurnRateFast` | 14.4× | 1 h | 5 m | 72% of requests failing | page |
| `AtlasTaskSuccessBurnRateSlow` | 6× | 6 h | 30 m | 30% failing | ticket |

- Bad = outcome `error`, `step_limit`, `tool_error` or `timeout`; guardrail and budget refusals are excluded on purpose
- Latency pages on its own threshold rule: `AtlasLatencyP95High`, p95 > 4 s for 10 minutes
- The multipliers come from the Google SRE workbook, where they were written for 99.9% SLOs

[AVATAR]

Now the rules Atlas actually ships. Two burn-rate alerts on task success. Fast burn: fourteen point four times the allowed rate over an hour, held for five minutes, pages. Slow burn: six times over six hours, held for thirty minutes, opens a ticket. "Bad" means a request ended in an error, a step limit, a tool error or a timeout; a guardrail refusal or a budget refusal is Atlas doing its job, so it's excluded.

[B-ROLL: D8 build 3, the error-budget line falling steeply during an incident, the fast-burn threshold crossed, then a gentle slope crossing the slow-burn threshold.]

[PAUSE] Do the arithmetic on those multipliers, because it's the catch for agents. They come from the SRE workbook, written for ninety-nine point nine percent SLOs, where fourteen point four times means one and a half percent of requests failing. At ninety-five percent, it means seventy-two percent failing for an hour. That page fires for an outage, not for a degradation. The six-hour ticket catches thirty percent. If your agent needs earlier warning, lower the multipliers, and test the rule before you trust it; 9.5 shows how. Latency doesn't use burn rate at all in the shipped rules: it pages when p95 stays over four seconds for ten minutes.

[SCREEN: VS Code, `src/northwind/slo.py`]

[CODE: `src/northwind/slo.py` (excerpt)]

```python
@dataclass(frozen=True)
class SLO:
    """Target ratio over a window (days)."""

    name: str
    target: float
    window_days: int = 28
    description: str = ""

    @property
    def error_budget_fraction(self) -> float:
        return 1.0 - self.target


def error_budget_remaining(slo: SLO, sli: SLI) -> float:
    """Fraction of the error budget still unspent (negative = overspent)."""
    allowed_bad = slo.error_budget_fraction * sli.total
    if allowed_bad == 0:
        return 1.0 if sli.bad == 0 else -1.0
    return (allowed_bad - sli.bad) / allowed_bad


def burn_rate(slo: SLO, sli: SLI) -> float:
    """How fast the budget burns: 1.0 = exactly on budget over the window; 14.4 = alert."""
    if slo.error_budget_fraction == 0:
        return float("inf") if sli.bad else 0.0
    bad_fraction = sli.bad / sli.total if sli.total else 0.0
    return bad_fraction / slo.error_budget_fraction
```

Three small pieces, so the CI gate, the console and the report compute the same thing Prometheus does. `error_budget_remaining` gives the fraction of the budget left. `burn_rate` is the division from the slide. And `DEFAULT_SLOS`, just below, pins the targets in code, next to the tests, so a change to a promise is a pull request.

[SLIDE 6: Presenting to leadership]
- One page: six SLIs, target, this week, trend arrow, budget remaining
- Green, amber, red; no charts on the summary page
- Cost per resolved session and task success on the same line: quality and cost together
- "We have 40% of our latency budget left this month; we're pausing the model swap until it rolls over"
- The dashboard in 9.3 has the SLIs as its top row

[AVATAR]

And the meeting. One page. Six rows, target, this week, a trend arrow, budget remaining. Colours, no charts. Cost per resolved session and task success on the same line, so nobody optimises one by breaking the other. And the sentence that makes you sound like an operator: "We have forty percent of our latency budget left this month, so we're pausing the model swap until it rolls over." [PAUSE] That sentence is the entire point of SLOs. It turns reliability from a feeling into a budget line, and budgets are a language leadership already speaks.

[SLIDE 7: Recap]
- Six SLIs, each a good-over-all ratio
- Error budget: the failure you may spend
- Atlas pages on 14.4× fast burn

### Recap

Six SLIs a director can say back to you, each a ratio with a target and a 28-day window, an error budget that says how much failure is allowed, and the shipped burn-rate rules: 14.4× over an hour pages, 6× over six hours opens a ticket, which at a 95% SLO means outages, not degradations.

### Transition

The SLIs need live numbers. Next, the code: Atlas's `/metrics` endpoint, the counters and histograms behind every SLI, and the compose stack that scrapes them.

### Speaker notes: common mistakes and Q&A

- **SLO at current performance.** Leave headroom; the budget is the headroom.
- **Too many SLIs.** Six is the ceiling for a leadership page. Everything else is a diagnostic panel.
- **Paging on p95.** A one-minute p95 spike pages you for nothing; the shipped latency rule holds for 10 minutes, and burn rate holds over a window.
- **Two definitions of task success.** `slo.py` counts escalations as good and every other non-resolved outcome as bad; the alert rule counts only `error|step_limit|tool_error|timeout` as bad. Say which one a number came from.
- **The 14.4 / 6 recipe** comes from the Google SRE workbook; say so once. At a 95% SLO it pages late; students who want earlier warning should change the multiplier and write a `promtool` test (9.5) before they ship it. `slo.py`'s `BURN_RATE_ALERTS` lists 6× over 6 h as "page"; the shipped `alerts.yml` makes it a ticket. The YAML is what runs.

---

## Lecture 9.2: Code-along: Prometheus metrics from Atlas

| Field | Value |
|---|---|
| ID | 9.2 |
| Title | Code-along: Prometheus metrics from Atlas |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 640 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Mount `/metrics`, define every counter and histogram with low-cardinality labels in one file, and scrape it with the compose stack. |
| Prerequisites | 9.1; 5.5 (cardinality); 7.2 (histograms) |
| Files used | `telemetry/metrics.py`, `app/server.py`, `deploy/docker-compose.observability.yml`, `deploy/prometheus.yml` |

**Learning objectives**

1. Mount the Prometheus ASGI app on FastAPI and read the exposition format.
2. Read the full Atlas metric set with its naming convention and label allow-list, and explain each label's cardinality.
3. Bring up Prometheus and Grafana with `make stack`, drive traffic with `make swarm`, and confirm the scrape.

### Script

[AVATAR]

Every SLI from the last lecture is a division. Slow requests over all requests. Tool errors over tool calls. Cost over resolved requests. [PAUSE] Prometheus is the thing that does divisions over time, cheaply, for years. Today we give it the numerators and denominators, and we're going to be strict about labels, because the wrong label turns a cheap metric into a memory leak.

[SLIDE 1: One file, one convention]
- All metrics in `telemetry/metrics.py`; nothing defines a metric anywhere else
- Names: `atlas_<thing>_total` for counters, `atlas_<thing>_seconds` for histograms, `_usd` when it's money
- Label allow-list (`ALLOWED_LABELS`): `tenant`, `model`, `tool`, `outcome`, `kind`, `decision`, `feature`, `name`, `from_model`, `to_model`, `reason`, `version`, `prompt_version`
- Forbidden (`FORBIDDEN_LABELS`): `user_id`, `session_id`, `trace_id`, `user`, `email`; a unit test enforces both lists
- Every label value comes from a small fixed set

[AVATAR]

One file, one convention. Counters end in `_total`. Histograms end in `_seconds`. Money says `_usd`. And a label allow-list: tenant, model, tool, outcome, feature, and a handful of fixed enumerations. A unit test, `test_metrics_label_allowlist`, fails the build if anyone adds a label outside the list. Never a user, session or trace id. A metric with tenant, feature and model has a few hundred series at most. A metric with user id has eighty today and eight thousand next year, and Prometheus keeps every one in memory. [PAUSE] Those ids live in the span store, where they belong.

[SCREEN: VS Code, `telemetry/metrics.py`]

[CODE: `telemetry/metrics.py` (excerpt; the full file has 20 metrics)]

```python
REQUESTS = Counter(
    "atlas_requests_total",
    "Chat requests",
    ["tenant", "model", "outcome", "feature"],
    registry=REGISTRY,
)
TOKENS = Counter(
    "atlas_tokens_total",
    "LLM tokens by kind (input|output|cached|reasoning)",
    ["tenant", "model", "kind"],
    registry=REGISTRY,
)
COST = Counter(
    "atlas_cost_usd_total", "LLM cost in USD", ["tenant", "model", "feature"], registry=REGISTRY
)
LATENCY = Histogram(
    "atlas_request_latency_seconds",
    "End-to-end request latency",
    ["tenant", "feature"],
    buckets=LATENCY_BUCKETS,
    registry=REGISTRY,
)
TTFT = Histogram("atlas_ttft_seconds", "Time to first token of the final answer", ["model"], ...)
TOOL_CALLS = Counter("atlas_tool_calls_total", "Tool invocations", ["tool", "outcome"], ...)
LLM_RETRIES = Counter("atlas_llm_retries_total", "LLM call retries", ["model", "reason"], ...)
FALLBACKS = Counter("atlas_model_fallbacks_total", "Model fallbacks fired", ["from_model", "to_model"], ...)
BUDGET_DECISIONS = Counter("atlas_budget_decisions_total", "Budget guard decisions", ["tenant", "decision"], ...)
GUARDRAIL = Counter("atlas_guardrail_events_total", "Guardrail triggers (injection, pii_in_output, refusal)", ["tenant", "kind"], ...)
FEEDBACK = Counter("atlas_feedback_total", "User feedback", ["tenant", "outcome"], ...)
INFLIGHT = Gauge("atlas_inflight", "Requests holding a tenant concurrency slot", ["tenant"], ...)
QUEUE_WAIT = Histogram("atlas_queue_wait_seconds", "Time a request waited for its tenant's concurrency slot", ["tenant"], ...)
SHED = Counter("atlas_requests_shed_total", "Requests refused with 429 because the tenant's queue wait ran out", ["tenant"], ...)
BUILD_INFO = Gauge("atlas_build_info", "Build / release info (value is always 1)", ["version", "model", "prompt_version"], ...)
```

You've met most of these already. `REQUESTS` with `outcome` and `feature`, which is the denominator for almost everything and the numerator for task success and containment. The latency histogram with `tenant` and `feature`, so you can ask for policy questions' p95 for finance. Tokens by kind, cost by tenant, model and feature.

[SCREEN: zoom on `INFLIGHT`, `QUEUE_WAIT`, `SHED` and `BUILD_INFO`]

The concurrency trio from 7.5. And `BUILD_INFO`, a gauge that's always one, whose labels carry the version, the default model and the prompt version; that's how Grafana can mark a release. [PAUSE] Count the labels on each line. None has more than four, and every value is from a fixed set.

Why is cost a counter and not a gauge? Because a counter only goes up, and Prometheus can take its rate. `increase(atlas_cost_usd_total[1h])` is spend per hour, `[1d]` is spend per day, all from one series, and a restart doesn't corrupt it because `increase` understands resets. Counters for anything you add up; gauges for anything you read off, like in-flight requests; histograms for anything you take a percentile of.

Now the endpoint.

[SCREEN: `app/server.py`]

[CODE: `app/server.py` (excerpt)]

```python
    app = FastAPI(
        title="Atlas helpdesk agent", version="1.0.0", lifespan=lifespan, **_fastapi_telemetry_off()
    )
    app.mount("/metrics", metrics.metrics_app())
```

```python
        # in lifespan(), at startup
        metrics.set_build_info(
            version=settings.langfuse_release,
            model=settings.model,
            prompt_version=settings.prompt_version,
        )
```

One line mounts it: `metrics_app` wraps `prometheus_client.make_asgi_app` over Atlas's own `REGISTRY`, and FastAPI serves it at `/metrics`. `set_build_info` runs once at startup. [PAUSE] One security note. The metrics endpoint has no PII, but it shows your traffic, your spend and your model names, on the same port as the chat API. In production, bind it to an internal interface or put it behind a network policy that only Prometheus can reach.

[SCREEN: terminal]

```bash
make run &      # Atlas on :8000, offline
# ...four requests from ops...
curl -sL localhost:8000/metrics | grep -E '^atlas_(requests_total|request_latency_seconds_bucket\{feature="policy_question",le="4.0",tenant="ops"\}|cost_usd_total)'
```

[DEMO: output (after four requests: three policy questions and one ticket lookup):]

```
atlas_requests_total{feature="policy_question",model="gpt-4.1-mini",outcome="resolved",tenant="ops"} 3.0
atlas_requests_total{feature="ticket_lookup",model="gpt-4.1-mini",outcome="resolved",tenant="ops"} 1.0
atlas_cost_usd_total{feature="policy_question",model="gpt-4.1-mini",tenant="ops"} 0.013424799999999999
atlas_cost_usd_total{feature="ticket_lookup",model="gpt-4.1-mini",tenant="ops"} 0.00276
atlas_request_latency_seconds_bucket{feature="policy_question",le="4.0",tenant="ops"} 3.0
```

That's the format Prometheus scrapes. Three policy questions and a ticket lookup, all resolved. A cent and a third of spend on the policy questions. And all three policy questions in the four-second bucket. [PAUSE] That `le="4.0"` bucket is the whole latency SLO: requests under four seconds over all requests, straight from the histogram, because we put a bucket edge at the budget in 7.2. Note the `-L`: `/metrics` is a mounted app and answers the bare path with a redirect to `/metrics/`.

Now the stack.

[SCREEN: `deploy/prometheus.yml` and `deploy/docker-compose.observability.yml`]

[CODE: `deploy/prometheus.yml` (excerpt) and the compose file (excerpt)]

```yaml
# deploy/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
rule_files:
  - /etc/prometheus/alerts.yml
scrape_configs:
  - job_name: atlas
    metrics_path: /metrics
    static_configs:
      - targets: ["atlas:8000"]
        labels: { service: atlas }
```

```yaml
# deploy/docker-compose.observability.yml (services excerpt)
  atlas:
    build: { context: .., dockerfile: deploy/Dockerfile }
    ports: ["8000:8000"]
  prometheus:
    image: prom/prometheus:v2.55.1
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.retention.time=45d   # > the 28-day SLO window
    ports: ["9091:9090"]
  grafana:
    image: grafana/grafana:11.3.1
    environment: { GF_SECURITY_ADMIN_USER: admin, GF_SECURITY_ADMIN_PASSWORD: admin }
    ports: ["3001:3000"]
```

Prometheus scrapes the `atlas` service every fifteen seconds and loads the alert rules from 9.5. Atlas itself runs in the stack, so the target is the service name, `atlas:8000`, not your laptop. Retention is forty-five days, longer than the twenty-eight-day SLO window, so a month of `increase` actually has a month of data. Grafana provisions its dashboard from the folder, so `atlas-ops.json` is loaded, not clicked. Images are pinned.

```bash
make stack                                  # docker compose up: collector, Phoenix, Prometheus, Grafana, Atlas
make swarm RPS=2 DURATION=600               # ten minutes of seeded traffic against localhost:8000
```

[DEMO: Prometheus at localhost:9091, Status → Targets: `atlas` UP. Graph tab: `sum(rate(atlas_requests_total[1m]))` climbing to about 2. Record the values from your own run.]

Target up, two requests a second, and every SLI is now a query away. Next lecture, we put them on a dashboard.

[SLIDE 2: Recap]
- One file, an allow-list of labels
- `/metrics` mounted; build info at startup
- `make stack` plus `make swarm` feed Prometheus

### Recap

One file defines every metric with a fixed label allow-list enforced by a test, `/metrics` is mounted in one line, and `make stack` plus `make swarm` give Prometheus a running Atlas to scrape every fifteen seconds, with alert rules and a provisioned dashboard.

### Transition

Next, Grafana: the Atlas Ops dashboard, one panel per question, tenant and feature variables, and a release marker that actually fires.

### Speaker notes: common mistakes and Q&A

- **Defining metrics in two places.** Duplicate registration raises at import. One file.
- **`make run` vs `make stack`.** `make run` serves Atlas on your laptop; the stack's Prometheus scrapes the `atlas` container, not your laptop. For a laptop Atlas, uncomment the `host.docker.internal:8000` target in `prometheus.yml` (on Linux also add `extra_hosts: ["host.docker.internal:host-gateway"]`).
- **`make replay PROM=1`.** Does nothing: a replay writes to the span store, and Prometheus only sees a running server.
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
| Target duration | 9:00 (about 720 spoken words at ~140 wpm; remaining time is the dashboard) |
| One idea | Open the provisioned `atlas-ops.json`, read the PromQL behind each row, filter by tenant and feature, and mark releases with a query that actually fires. |
| Prerequisites | 9.2; the compose stack running |
| Files used | `deploy/grafana/dashboards/atlas-ops.json`, `deploy/grafana/provisioning/`; Diagram D11 "Atlas Ops dashboard" |

**Learning objectives**

1. Open the dashboard and identify its four rows: SLIs, traffic and latency, cost, quality and safety.
2. Read and modify the PromQL for p95, task success, the 28-day latency SLO ratio, tool error rate, cache hit ratio and cost per resolved request.
3. Use the `$tenant` and `$feature` variables, and replace the release annotation's `changes()` query with one that fires.

### Script

[AVATAR]

A dashboard is a set of questions with answers already on screen. [PAUSE] The Atlas Ops dashboard answers the leadership questions from 9.1 in its top row, and the "why" questions underneath. Let's open it, and then read the queries, because a dashboard you can't read is a dashboard you can't fix at three in the morning.

[SCREEN: Grafana at localhost:3001 (admin / admin), the stack from 9.2 still running with `make swarm` traffic. Dashboards → "Atlas Ops" opens: four rows.]

It's already there, provisioned from the compose volume. If you're importing by hand: Dashboards, New, Import, upload `atlas-ops.json`, choose the Prometheus data source. [PAUSE] Four rows. SLIs at the top. Traffic and latency. Cost. Quality and safety.

[SLIDE 1: Row 1: SLIs (the leadership row)]

Diagram: D11 build 1, the SLI row.

- Task success: (resolved + escalated) ÷ all requests, stat
- Containment: resolved ÷ all requests, stat
- p95 latency, stat with a red threshold at 4 s
- Cost per resolved session (1 h): cost ÷ resolved requests, labelled as an approximation
- Every panel filters on `tenant=~"$tenant"` and `feature=~"$feature"`

[SCREEN: zoom on the p95 panel; open Edit; the query is visible]

[CODE: PromQL behind row 1 (from `atlas-ops.json`), plus two you add]

```promql
# task success: resolved or escalated over all requests
sum(rate(atlas_requests_total{tenant=~"$tenant",feature=~"$feature",outcome=~"resolved|escalated"}[$__rate_interval]))
  / sum(rate(atlas_requests_total{tenant=~"$tenant",feature=~"$feature"}[$__rate_interval]))

# p95 end-to-end latency
histogram_quantile(0.95, sum(rate(atlas_request_latency_seconds_bucket{tenant=~"$tenant",feature=~"$feature"}[$__rate_interval])) by (le))

# cost per resolved request, last hour (approximation of cost per resolved session)
sum(increase(atlas_cost_usd_total{tenant=~"$tenant"}[1h]))
  / sum(increase(atlas_requests_total{tenant=~"$tenant",feature=~"$feature",outcome="resolved"}[1h]))

# add: the latency SLO over the 28-day window, no quantile needed
sum(increase(atlas_request_latency_seconds_bucket{le="4.0"}[28d])) / sum(increase(atlas_request_latency_seconds_count[28d]))

# add: error budget remaining for that SLO (target 0.95)
1 - (1 - (sum(increase(atlas_request_latency_seconds_bucket{le="4.0"}[28d])) / sum(increase(atlas_request_latency_seconds_count[28d])))) / 0.05
```

Five queries. Task success is a ratio of two rates of the same counter, filtered by outcome. The p95 is `histogram_quantile` over the rate of the bucket counters, summed by `le`; the `feature` filter works because the latency histogram carries a `feature` label since Section 7. Cost per resolved session is an approximation: Prometheus has no sessions, so the shipped panel divides by resolved requests and says so in its title. Honesty on the dashboard is a feature.

[SCREEN: Dashboard → Add → Visualization; paste the two added queries as stat panels: "Latency SLO (28 d)" with a threshold at 0.95, and "Error budget left" as a gauge]

[PAUSE] The two you add are the leadership pair. The SLO ratio is the four-second bucket over the count, over twenty-eight days. No quantile function at all, because the bucket edge is the budget. And the error budget remaining turns that ratio into the fraction of the five-percent allowance you haven't spent, the same number `slo.py` prints. Retention is forty-five days, so twenty-eight days of `increase` has the data behind it.

[SLIDE 2: Rows 2 to 4]
- Traffic and latency: requests per second by tenant, p50 / p95 / p99, TTFT p95 by model, outcomes, agent steps p95, tool error rate by tool
- Cost: dollars per hour by tenant and by feature, tokens by kind, cache hit ratio, LLM retries and fallbacks, budget decisions
- Quality and safety: judge score mean, feedback per hour, guardrail events per hour, telemetry export failures
- A table of `atlas_build_info` at the bottom

[SCREEN: scroll through rows 2 to 4; pause on "Cost USD / hour by tenant", "Cache hit ratio" and "LLM retries and fallbacks / s"]

[CODE: PromQL behind rows 2 and 3 (from `atlas-ops.json`)]

```promql
# dollars per hour by tenant
sum(increase(atlas_cost_usd_total{tenant=~"$tenant",feature=~"$feature"}[1h])) by (tenant)

# cache hit ratio: cached over input tokens (input already includes cached)
sum(rate(atlas_tokens_total{tenant=~"$tenant",kind="cached"}[$__rate_interval]))
  / sum(rate(atlas_tokens_total{tenant=~"$tenant",kind="input"}[$__rate_interval]))

# LLM retries by reason, and fallbacks by from/to model
sum(rate(atlas_llm_retries_total[$__rate_interval])) by (reason)
sum(rate(atlas_model_fallbacks_total[$__rate_interval])) by (from_model, to_model)

# add: refused share, the budget guard turning users away
sum(rate(atlas_requests_total{outcome="refused"}[5m])) / sum(rate(atlas_requests_total[5m]))
```

Dollars per hour by tenant is the showback as a stacked chart. The cache hit ratio divides cached tokens by input tokens, not by input plus cached, because the input count already includes the cached ones, exactly the 6.1 rule. If this line drops, someone put a date at the front of the prompt. Retries and fallbacks sit on one panel. [PAUSE] And the refused share is what the budget guard is doing to users right now; degraded requests are the `decision="degrade"` line on the budget-decisions panel.

[SLIDE 3: Reading the shapes]
- Slow provider (7.6): p95 red; retries, fallbacks and cost flat; in-flight and queue wait climbing on a live server
- Retry storm (7.3): retries up, cost per hour up, p95 barely moves
- Cost spike (Incident 1): cost per hour up for one tenant, cache ratio unchanged, tokens per second up
- Quality drift (8.5): nothing on rows 1 to 3 turns red; the judge lives in the span store, not here

[AVATAR]

Here's how you read the dashboard during an incident. The slow provider from 7.6: p95 red, retries and fallbacks flat, cost flat. That combination has exactly one meaning: the provider is slow and nothing is timing out. You knew the fix before you opened a trace. A retry storm looks different: retries up, cost per hour up, p95 barely moving. And a quality drift doesn't show up here at all. [PAUSE] Look at the quality row: the judge-score panel is empty, because the judge runs as a batch job over the span store and never feeds this histogram. That's not a bug in your reading. It's where Prometheus stops and the span store and Langfuse take over, and 9.5 comes back to it.

Now the two features that make this a working dashboard instead of a pretty one.

[SCREEN: Dashboard settings → Variables: `$tenant` and `$feature`; then Annotations: "Releases"]

[CODE: dashboard variables and the release annotation]

```
# variable: tenant   (query, multi-value, include All)
label_values(atlas_requests_total, tenant)

# variable: feature
label_values(atlas_requests_total, feature)

# annotation "Releases" as shipped: never fires
changes(atlas_build_info[5m]) > 0

# replace it with: a build-info series that wasn't there 5 minutes ago
count by (version, prompt_version) (atlas_build_info unless atlas_build_info offset 5m)
#   title format: release {{version}} prompt {{prompt_version}}
```

The variables are `label_values` queries, so they fill themselves; pick finance and the whole dashboard becomes finance's dashboard. [PAUSE] Now the annotation, and a lesson in testing your dashboards. The shipped query asks for `changes()` on `atlas_build_info`. But that gauge is always one. A new release doesn't change a value; it creates a new series whose value is also one, so `changes()` stays at zero forever and the annotation never draws. The replacement asks for a build-info series that didn't exist five minutes ago, and that's true for five minutes after every deploy. I checked both with `promtool test rules` against a synthetic release; the shipped one returns nothing, the replacement returns the new version.

[SCREEN: edit `.env` to `ATLAS_PROMPT_VERSION=v2`, then `docker compose -f deploy/docker-compose.observability.yml up -d atlas`; the dashboard draws a vertical line labelled "release v1.0.0 prompt v2". Record from your run.]

Restart Atlas with a different prompt version and the line appears, labelled with the version and the prompt. Nobody has to correlate a deploy log with a chart. The chart correlates itself.

[SLIDE 4: Dashboard hygiene]
- Every panel has a unit and a threshold, or it's a diagnostic and lives in a collapsed row
- Top row is stats, not time series: red or green at a glance
- The JSON is in git: edit in the UI, export, commit to `deploy/grafana/dashboards/atlas-ops.json`
- One dashboard per audience: Ops (this one), Finance (cost row only, weekly), Leadership (row 1 only)
- Test what you can: queries and alerts with `promtool`, before you trust a colour

[AVATAR]

Thresholds and colours come from the SLOs in 9.1, not from taste: the p95 stat turns red at four seconds, task success turns red under ninety-five percent. When a threshold changes, it changes in `slo.py` and in the JSON in the same pull request. A dashboard that disagrees with the SLO document is worse than no dashboard, because people trust the colours. [PAUSE] And the JSON lives in git: edit in the UI, export, commit, so a dashboard change is a pull request. One dashboard per audience. And test what you can, because the annotation you just fixed looked perfectly reasonable for months.

[SLIDE 5: Recap]
- Four rows: SLIs, latency, cost, quality
- Every query filters by tenant and feature
- Test the release annotation; `changes()` never fires

### Recap

`atlas-ops.json` puts the SLIs in its top row with PromQL you can read, filters everything by `$tenant` and `$feature`, keeps cost per resolved session honest as an approximation, and marks releases once you replace the `changes()` annotation with a query that fires.

### Transition

Grafana sees metrics. Langfuse sees traces and scores. Next, a short demo of the Langfuse views that answer the questions Grafana can't: which sessions, which users, which prompt version.

### Speaker notes: common mistakes and Q&A

- **Cost per resolved session on Prometheus.** It's per resolved request over an hour; label it. The exact figure comes from the span store in `report.py` ($0.0144 on the baseline day).
- **`histogram_quantile` with no `sum by (le)`.** Returns nonsense or nothing. Always aggregate by `le` first.
- **`increase` over 28 d on short retention.** Prometheus's default retention is 15 days; the compose file sets 45d. Verify on screen.
- **The release annotation.** The shipped JSON still uses `changes(atlas_build_info[5m]) > 0`; until the repo is fixed, students should replace it in their copy and export. A `promtool` unit test for it is in the 9.5 pattern.
- **Empty judge panel.** `atlas_judge_score` is defined but never observed by the batch judge; expected, not a scrape problem.
- **Grafana UI changes.** Menu paths move between versions; record the current ones on Grafana 11.3.

---

## Lecture 9.4: Langfuse dashboards and saved views

| Field | Value |
|---|---|
| ID | 9.4 |
| Title | Langfuse dashboards and saved views |
| Type | DM (live demo) |
| Target duration | 5:00 (about 540 spoken words at ~140 wpm; remaining time is the UI) |
| One idea | Use Langfuse for the questions metrics can't answer, which sessions, which users, which prompt version, and save the views so stakeholders can open them without you. |
| Prerequisites | 9.3; Section 4 |
| Files used | Langfuse UI (screens change; verify before recording); `.env` with Langfuse keys; `make run`, `make swarm`, `make prompts` |

**Learning objectives**

1. Build a cost-by-tag view and a score view in Langfuse and read them against the Grafana cost row.
2. Use the session explorer to go from a number to the actual conversations.
3. Save and share a view with a stakeholder, and know what Langfuse is for versus Grafana.

### Script

[AVATAR]

Grafana told you policy questions are three quarters of the bill. It can't show you a policy question. [PAUSE] Langfuse can. This is a short demo of the four views I open every week, and how to hand them to someone who isn't you. The screens move between Langfuse versions, so if yours look different, the ideas don't.

[SLIDE 1: Grafana vs Langfuse]
- Grafana: rates, percentiles, budgets, alerts. Aggregates over time. No ids
- Langfuse: traces, sessions, users, scores, prompts, datasets. Individual things. Every id
- Question starts with "how much" or "how often": Grafana
- Question starts with "which" or "show me": Langfuse
- Both fed by the same spans and the same numbers (6.3)

[AVATAR]

The split. Grafana for how much and how often. Langfuse for which and show me. Same spans, same cost numbers, different questions.

[SCREEN: terminal: Langfuse keys in `.env`; `make prompts` registers prompt versions v1 and v2 (label `production` on v1); `make run`, then `make swarm RPS=2 DURATION=600`. Every live trace carries the tags `tenant:…`, `feature:…`, `intent:…`, `prompt:…`.]

The data first. With Langfuse keys in `.env`, `make run` exports every live trace to Langfuse as well as to the local store, with the tags from Section 4: tenant, feature, intent and prompt version. `make prompts` registers the two prompt versions. Then ten minutes of swarm traffic.

[SCREEN: Langfuse project. Dashboards (or Metrics) view: cost over time grouped by the `tenant:` tags, then by `feature:`.]

View one: cost by tag. Group cost by the tenant tag, and it has the same shape as the Grafana stacked chart, which it should, because both came from the `cost_details` and the counter written in the same moment in 6.3. Switch the grouping to feature, and policy questions dominate, as the showback said. [PAUSE] Where this beats Grafana: click a bar and you're looking at the generations behind it.

[SCREEN: Scores view: `user_feedback` and the judge's scores over time, filtered by the `feature:policy_question` tag; then the score filter set to below 0.5]

View two: scores. Feedback from `/feedback` and the judge's scores from `make judge` land on the same traces. Filter to policy questions and to scores below point five. [PAUSE] That's the low cluster from the drift report, as a list of traces. Open one: the input, the retrieved passages, the answer and the scores, two clicks from the chart to the sentence that's wrong.

[SCREEN: Sessions view: filter `feature:policy_question`, sort by number of traces; open a four-turn session.]

View three: the session explorer. Sessions are conversations. Filter to policy questions, sort by length, open a long one, and read it top to bottom: the question, the follow-ups, where the employee pushed back, whether they got there. [PAUSE] Metrics said ninety-nine percent contained on the replayed day. This shows you what the other one percent feels like.

[SCREEN: Prompts view: `atlas-system`, versions 1 and 2 side by side, the diff highlighted, the `production` label on version 1.]

View four: prompts. Version one and version two side by side, with the diff highlighted. And because traces are tagged with the prompt version, you can filter scores per version. On the drift day from 8.1, the judge put version one at point nine one and version two at point seven one. [PAUSE] That's the evidence for a rollback, and in Section 11 you'll do the rollback by moving the label.

[SCREEN: Save the scores view as "Policy quality, 14 d"; share the link; the project settings page showing a Viewer role.]

Now save it. Name the view, share the link, and give your stakeholder a viewer role, which is read-only. Your HR partner opens "Policy quality, fourteen days" every Monday, sees the same chart you see, and never needs Grafana or a Prometheus query.

[SLIDE 2: The weekly review, in views]
- Cost by tenant and feature (Langfuse) against the showback (`make report`)
- Scores by feature, 14 days, with the low-score filter saved
- Longest sessions this week, by feature
- Prompt versions, with scores per version
- Grafana row 1 for the SLOs; this for the "which"

[AVATAR]

That's the weekly review. Cost by tenant against the report. Scores by feature with the low-score filter. The longest sessions. Prompt versions with their scores. And Grafana's top row for the SLOs. Fifteen minutes, every Monday, and nothing drifts for a month without someone noticing.

[SLIDE 3: Recap]
- Grafana answers how much; Langfuse answers which
- Four views: cost, scores, sessions, prompts
- Share saved views with a read-only role

### Recap

Langfuse answers "which" and "show me": cost and scores by tag with click-through to traces, sessions to read failures as conversations, prompts with scores per version, and saved views a stakeholder can open with a viewer role.

### Transition

Dashboards are for when you're looking. Next, alerts, for when you're not: the ten rules Atlas ships, the one that can't fire, and the runbook that goes with each.

### Speaker notes: common mistakes and Q&A

- **Verify the screens.** Langfuse's dashboards, metrics and saved-view features change between releases. Record against the current UI and say "your version may differ".
- **Live traces, not replays.** `make replay LANGFUSE=1` mirrors replayed requests to Langfuse with tenant and intent tags only (no feature or prompt tags) and with new trace ids, so judge scores from the local store won't attach to them. For this demo, use live traffic from `make run` and `make swarm`.
- **Judge scores in Langfuse.** Check that `make judge` reports `langfuse_writes` above 0 (8.2); otherwise only `/feedback` scores appear.
- **Sharing with edit rights.** Stakeholders get Viewer. Role names vary by version; check the project settings.
- **Cost mismatch between Langfuse and Grafana.** If they differ, something sent `usage_details` without `cost_details`, and Langfuse priced it from its own table. 6.3 covers why Atlas always sends both.

---

## Lecture 9.5: Alert rules and the runbook

| Field | Value |
|---|---|
| ID | 9.5 |
| Title | Alert rules and the runbook |
| Type | SC (screencast code-along) |
| Target duration | 7:00 (about 720 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Read the ten shipped alert rules in three groups, SLO, cost and quality, each with a severity and a runbook entry, test them before they go live, and know which one can't fire. |
| Prerequisites | 9.1 to 9.3; 6.7 (budget decisions) |
| Files used | `deploy/alerts.yml`, `10-resources/runbook-template.md`, `promtool` (in the `prom/prometheus:v2.55.1` image) |

**Learning objectives**

1. Read the shipped rules: p95 latency, task-success burn rate (fast and slow), tool error rate, tenant cost anomaly, hard-cap refusals, retry storm, judge score, negative feedback and exporter failures.
2. Explain why `AtlasJudgeScoreLow` cannot fire as shipped, and what it would take to wire it.
3. Unit-test an alert rule with `promtool test rules`, and fill the runbook template so every alert has an owner, a first look and a known fix.

### Script

[AVATAR]

An alert that fires and nobody knows what to do is noise with a pager attached. [PAUSE] Ten rules in three groups today, each with a severity and a runbook entry before it goes live. That's not process for its own sake. It's the difference between "Atlas is slow, good luck" and "Atlas is slow; check retries and fallbacks; if they're flat, the timeout is too long; here's the config line."

[SCREEN: VS Code, `deploy/alerts.yml`]

[CODE: `deploy/alerts.yml` (the SLO group; the file has 10 rules)]

```yaml
# Alert rules for Atlas (Section 9.5). Severities: page (wake someone) / ticket (next business day).
groups:
  - name: atlas-slo
    rules:
      - alert: AtlasLatencyP95High
        expr: histogram_quantile(0.95, sum(rate(atlas_request_latency_seconds_bucket[5m])) by (le)) > 4
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "Atlas p95 latency above 4 s"
          runbook: "10-resources/runbook-template.md#latency"

      - alert: AtlasTaskSuccessBurnRateFast
        # 1h burn rate on the 95% task-success SLO: bad = error/step_limit/tool_error outcomes
        expr: |
          (
            sum(rate(atlas_requests_total{outcome=~"error|step_limit|tool_error|timeout"}[1h]))
            / sum(rate(atlas_requests_total[1h]))
          ) / (1 - 0.95) > 14.4
        for: 5m
        labels: { severity: page }

      - alert: AtlasTaskSuccessBurnRateSlow
        expr: |
          (
            sum(rate(atlas_requests_total{outcome=~"error|step_limit|tool_error|timeout"}[6h]))
            / sum(rate(atlas_requests_total[6h]))
          ) / (1 - 0.95) > 6
        for: 30m
        labels: { severity: ticket }

      - alert: AtlasToolErrorRate
        expr: |
          sum(rate(atlas_tool_calls_total{outcome="error"}[10m])) by (tool)
          / sum(rate(atlas_tool_calls_total[10m])) by (tool) > 0.05
        for: 10m
        labels: { severity: ticket }
```

The SLO group. `AtlasLatencyP95High` is the latency contract in PromQL: p95 above four seconds for ten minutes pages. The two burn-rate alerts are the 9.1 recipe on task success: errors, step limits, tool errors and timeouts over all requests, divided by the five percent allowance. Fourteen point four over an hour pages; six over six hours opens a ticket. And the tool error rate, per tool, above five percent for ten minutes.

[SCREEN: scroll to the `atlas-cost` and `atlas-quality` groups]

[SLIDE 1: The cost and quality groups]

| Rule | Fires when | Severity |
|---|---|---|
| `AtlasTenantCostAnomaly` | a tenant's last hour > 2.5× its average hour of the previous day, and > $1, for 15m | ticket |
| `AtlasBudgetHardCapHit` | any `decision="refuse"` in 15 minutes | page |
| `AtlasRetryStorm` | more than 0.2 LLM retries per request, for 10m | page |
| `AtlasJudgeScoreLow` | mean `judge_grounded` < 0.75 over 2 h, for 30m | ticket |
| `AtlasNegativeFeedbackSpike` | > 40% of feedback negative over 2 h, for 30m | ticket |
| `AtlasTelemetryExportFailures` | > 20 span export failures in 10 minutes | ticket |

[AVATAR]

Cost: a tenant whose last hour is two and a half times its average hour of the previous day, and more than a dollar, is a ticket, because one hour can be a lunch rush and the guard from 6.7 is already degrading it. A hard-cap refusal pages, because users are being turned away. More than a fifth of a retry per request is a retry storm, a cost event before it's a latency one. Quality: negative feedback over forty percent, and the exporter failing, are tickets. [PAUSE] And one rule in this file will never fire.

[SLIDE 2: `AtlasJudgeScoreLow` cannot fire as shipped]
- It reads `atlas_judge_score_sum` and `_count`
- `atlas_judge_score` is defined in `metrics.py`, but nothing observes it: the judge is a batch CLI writing to the span store and Langfuse
- No series, no alert. It stays "inactive" forever, which looks exactly like "healthy"
- To wire it: observe `metrics.JUDGE_SCORE.labels(f"judge_{name}").observe(value)` in a process Prometheus scrapes, or push the judge's means through a Pushgateway after each run
- Until then, quality drift is caught by the drift report (8.5) in CI, not by Prometheus

[AVATAR]

`AtlasJudgeScoreLow` reads the judge-score histogram. That histogram is defined, and nothing ever writes to it, because the judge runs as a batch job over the span store, not inside the server Prometheus scrapes. No series, no alert. It sits in the rules page as "inactive" forever, which looks exactly like healthy. [PAUSE] That's the most dangerous kind of alert: one that can't fail. Two ways to wire it: observe the scores in a process Prometheus scrapes, or push the judge's means to a Pushgateway after each run. Until you do, quality drift is caught by the drift report from 8.5, failing a CI job, not by a page.

Which brings us to the habit that would have caught it: test every rule.

[SCREEN: VS Code, a new file `deploy/alerts_test.yml`; then terminal]

[CODE: `deploy/alerts_test.yml` (you write this file)]

```yaml
# promtool test rules alerts_test.yml
rule_files: [alerts.yml]
evaluation_interval: 1m
tests:
  - interval: 1m
    # 2 requests/s; from minute 10 every request lands above the 4 s bucket (a slow provider)
    input_series:
      - series: 'atlas_request_latency_seconds_bucket{le="4.0",tenant="ops",feature="policy_question"}'
        values: '0+120x10 1200+0x30'
      - series: 'atlas_request_latency_seconds_bucket{le="12.0",tenant="ops",feature="policy_question"}'
        values: '0+120x40'
      - series: 'atlas_request_latency_seconds_bucket{le="+Inf",tenant="ops",feature="policy_question"}'
        values: '0+120x40'
    alert_rule_test:
      - eval_time: 14m
        alertname: AtlasLatencyP95High
        exp_alerts: []
      - eval_time: 21m
        alertname: AtlasLatencyP95High
        exp_alerts:
          - exp_labels: {severity: page}
            exp_annotations:
              summary: "Atlas p95 latency above 4 s"
              runbook: "10-resources/runbook-template.md#latency"
```

```bash
docker run --rm -v "$PWD/deploy:/d" -w /d --entrypoint promtool prom/prometheus:v2.55.1 test rules alerts_test.yml
```

[DEMO: output `  SUCCESS`. Then change `21m` to `20m` and run again:]

```
  FAILED:
    alertname: AtlasLatencyP95High, time: 20m, 
        exp:[
            0:
              Labels:{alertname="AtlasLatencyP95High", severity="page"}
              Annotations:{runbook="10-resources/runbook-template.md#latency", summary="Atlas p95 latency above 4 s"}
            ], 
        got:[]
```

A synthetic slow provider: from minute ten, every request is slower than four seconds. Four minutes in, the rule is pending, not firing. At minute twenty-one, it fires: one minute for p95 to cross the line, ten minutes of `for:`. Change twenty-one to twenty and the test fails, which tells you exactly how long you'll wait for the page. [PAUSE] The same file can hold a test for `AtlasJudgeScoreLow`. Feed it judge scores, and it passes; feed it what Atlas actually exports, and there's nothing to feed. That's the gap, found in CI instead of during an incident.

[SCREEN: `10-resources/runbook-template.md`, then the `#latency` entry you write from it]

[CODE: the `latency` runbook entry, filled in from the template (excerpt)]

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

Owner, severity, and a two-minute first look: three panels to open. Then a decision tree keyed on what those panels show, with the setting to change and the lecture that explains it. Then how to verify it's fixed, and when a postmortem is required. [PAUSE] The whole entry fits on one screen, because at three in the morning nobody scrolls.

[SCREEN: Prometheus at localhost:9091 → Alerts, with `make stack` running and `make swarm RPS=2 DURATION=5400 SCENARIO=slow_provider` in a second terminal (the preset's afternoon window arrives about 49 minutes in; time-lapse the recording)]

On the live stack, the swarm compresses the replayed day into ninety minutes, so the slow afternoon lasts about fifteen minutes. `AtlasLatencyP95High` goes pending shortly after it starts, and fires ten minutes later, with the summary and the runbook link. Nothing in the cost group moves, because nothing about cost changed. Record the timings from your own run.

[SLIDE 3: Alert fatigue rules]
- Page only on user-facing symptoms and budget burn; everything else is a ticket
- Every alert has a runbook entry with an owner, or it doesn't ship
- Two windows or a `for:` clause on anything rate-based
- Review the alert log weekly: any alert that fired 3× with no action gets deleted or demoted
- Unit-test every rule with `promtool` before it goes live, including that it *can* fire

[AVATAR]

Five rules against fatigue. Page only for symptoms users feel and for budget burn. Every alert has a runbook and an owner, or it doesn't merge. Windows or a `for:` clause on everything rate-based. Review the alert log weekly, and delete anything that fired three times without anyone acting. And test every rule, including that it can fire at all. [PAUSE] An alert you've never seen fire is an alert you can't trust, the same way as a test.

[SLIDE 4: Recap]
- Ten rules: SLO, cost and quality groups
- `AtlasJudgeScoreLow` has no data: it can't fire
- Test rules with `promtool`; runbook for each

### Recap

Ten shipped rules in three groups, SLO (p95 latency, task-success burn at 14.4× and 6×, tool errors), cost (hourly anomaly, hard-cap refusals, retry storms) and quality (judge score, negative feedback, exporter failures), each with a severity and a runbook entry; `AtlasJudgeScoreLow` can't fire until judge scores reach Prometheus, which a `promtool` test makes obvious.

### Transition

Lab 6 puts it together: stack up, dashboard live, and one alert that fires and clears.

### Speaker notes: common mistakes and Q&A

- **`promtool` without Docker.** The `promtool` binary ships in the Prometheus release tarball; `promtool check rules deploy/alerts.yml` should print `SUCCESS: 10 rules found`.
- **Burn-rate expression with one window.** The shipped rules use one window plus `for:`; the SRE workbook pairs a long and a short window with `and`. Both are defensible; know which you run.
- **Runbook as a wiki page nobody updates.** Keep it in the repo next to the rules; the annotation links to the file.
- **Alertmanager routing** (who gets paged) is out of scope; the compose stack has no Alertmanager, so alerts show in Prometheus's Alerts page only.
- **The swarm and `for:` clauses.** `make swarm` compresses 24 hours into `DURATION` seconds; a short `DURATION` makes the incident window shorter than the `for:` clause, and the alert never fires.
- **Verify** rule syntax against the Prometheus version in the compose file (v2.55.1).

---

## Lecture 9.6: Lab 6: Ship the dashboard and one alert

| Field | Value |
|---|---|
| ID | 9.6 |
| Title | Lab 6: Ship the dashboard and one alert |
| Type | LAB (guided lab; short video intro, work off-video) |
| Target duration | Video 2:30 (about 220 spoken words at ~140 wpm, plus slide time); lab work 45 to 60 minutes |
| One idea | Bring up the compose stack, get the Atlas Ops dashboard live on swarm traffic, and make one alert fire and clear with a scenario. |
| Prerequisites | 9.1 to 9.5; Docker installed |
| Files used | `04-labs/lab-06-dashboards.md`, `deploy/docker-compose.observability.yml`, `deploy/prometheus.yml`, `deploy/alerts.yml`, `deploy/grafana/dashboards/atlas-ops.json` |

**Learning objectives**

1. Run the observability stack and confirm the `atlas` scrape target is up.
2. Verify every top-row panel shows data under swarm traffic, and add one panel of your own.
3. Trigger, observe and clear one alert with a scenario, and screenshot both states.

### Script

[AVATAR]

Lab six is the one where it all appears on screen. [PAUSE] Stack up. Dashboard live. One alert that fires and clears. Forty-five minutes if Docker behaves.

[SCREEN: `04-labs/lab-06-dashboards.md`, the checklist]

Bring up the stack with `make stack`, confirm the `atlas` target is up in Prometheus on port ninety-ninety-one, and drive traffic with `make swarm`. Open the Atlas Ops dashboard and check every panel in the top row has a number. Then add one panel of your own, with a unit and a threshold, and export the JSON.

Then the alert. Put a scenario on the Atlas container so one rule's condition becomes true, keep the traffic running longer than the rule's `for:` clause, and watch it go pending, then firing. Screenshot it. Remove the scenario, and screenshot it clearing. The lab walks you through one that works, and reminds you to write the `promtool` test first, so you know how long to wait.

[SLIDE 1: Lab 6 checklist]
- `make stack`; Prometheus target `atlas` UP
- `make swarm`; top row populated
- One new panel with unit and threshold, exported to `atlas-ops.json`
- One alert pending, firing, then cleared: three screenshots
- Stretch: an alert for the refused share (`outcome="refused"`) with its runbook entry and a `promtool` test
- Submit: the screenshots and the exported JSON diff

[AVATAR]

The stretch goal is a new alert, for the share of requests the budget guard refuses, with its runbook entry and a `promtool` test. Write the runbook first. If you can't say what someone should do when it fires, it isn't ready to fire.

[SLIDE 2: You can now]
- Turn Atlas's numbers into six SLOs with budgets
- Read and fix the PromQL behind a live dashboard
- Ship alerts you've tested, each with a runbook

### Recap

Lab 6 ships the stack, the dashboard and one alert that provably fires and clears, tested with `promtool` before you trust it.

### Transition

Before the lab, the Section 9 quiz.

### Speaker notes: common mistakes and Q&A

- **Metrics not appearing.** The stack's Prometheus scrapes the `atlas` container (`atlas:8000`); if you run Atlas on the laptop with `make run` instead, switch the target to `host.docker.internal:8000` (Linux needs the `extra_hosts` line).
- **Alert stuck pending.** The `for:` clause needs the condition to hold. `make swarm` compresses a day into `DURATION` seconds, so a short run makes an incident window shorter than the `for:`.
- **Editing JSON by hand.** Edit in the UI, export the JSON and commit it to `deploy/grafana/dashboards/atlas-ops.json`.
- **The judge-score alert.** Students sometimes pick `AtlasJudgeScoreLow`; it can't fire (9.5). Point them to a rule with data.

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
