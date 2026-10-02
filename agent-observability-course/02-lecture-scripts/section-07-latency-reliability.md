# Section 7: Latency and Reliability

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 50 minutes (8 lectures, including one chaos demo, one lab intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `ops`, `finance`, `hr`, `eng`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Latency charts: one metric per chart, p95 annotated with a callout, budget line drawn in red.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on litellm 1.103 / langfuse 4.15 / opentelemetry-semantic-conventions 0.66b0 (GenAI attributes are incubating; names may change)."
> **Companion course tie-in:** Lecture 7.1 links once to *Production Voice AI Agents* for the 800 ms voice budget. Never require it.
> **Offline latency note:** offline, the mock LLM stamps every call with a simulated latency (`simulated_ttft_ms`, `simulated_latency_ms`) drawn per model, and the agent records those instead of wall time. The mock never times out a slow call: it ignores `timeout=`. Timeouts, retries on timeouts and fallbacks are therefore shown with scripted failures (`retry_storm`, a stalling provider in 7.4) and unit tests, and apply to a real provider with `OFFLINE=0` (see `03-code/.env.chaos.example`).

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.latency` (`LatencySample`, `StepTiming`, `RequestTiming`, `percentile`, `summarize`, `LatencyBudget`, `violations`, `hourly_p95`), `app.agent` (`RETRYABLE`, `FALLBACKS`, `CircuitBreaker`, `AtlasAgent._call_model`, `_backoff`, `build_router_config`, `RouterClient`), `app.server.TenantLimiter`, `telemetry.metrics` (`atlas_request_latency_seconds{tenant,feature}`, `atlas_ttft_seconds{model}`, `atlas_tool_latency_seconds{tool}`, `atlas_llm_retries_total{model,reason}`, `atlas_model_fallbacks_total{from_model,to_model}`, `atlas_inflight{tenant}`, `atlas_queue_wait_seconds{tenant}`, `atlas_requests_shed_total{tenant}`), settings `ATLAS_REQUEST_TIMEOUT_S` (20), `ATLAS_MAX_RETRIES` (2), `ATLAS_ROUTER_ALLOWED_FAILS` (3), `ATLAS_ROUTER_COOLDOWN_S` (30), `ATLAS_TENANT_MAX_INFLIGHT`, `ATLAS_QUEUE_TIMEOUT_S` (3), `simulator/scenarios.py` presets `slow_provider` and `retry_storm`, `tests/budget/test_budget_gate.py`. On screen, all of this is "Atlas".

**The numbers card for this section (from `01-curriculum/numbers-card.md`; offline latency is the mock's simulated latency):**

| Item | Value |
|---|---|
| End-to-end latency, baseline day (`make console-text`) | p50 3,232 ms · p95 3,827 ms · p99 3,934 ms · max 4,138 ms (budget p95 4,000 ms) |
| Time to first token of the final answer (`atlas.ttft_ms` on the agent span; includes step 1) | p50 1,427 ms · p95 1,702 ms |
| Per-generation time to first token (`atlas_ttft_seconds`) | p50 509 ms · p95 652 ms |
| Generation duration | p50 960 ms · p95 2,824 ms |
| p50 / p95 by tenant | ops 2,168 / 3,670 · eng 3,303 / 3,844 · hr 3,345 / 3,836 · finance 3,511 / 3,905 ms |
| Hourly p95, baseline | flat, 3,647 to 3,870 ms |
| `slow_provider` preset (13:00 to 17:00, 75% of requests; TTFT ×3.5, tokens/s halved) | day p95 8,877 ms; hourly p95 about 9.2 to 9.4 s from 13:00 to 17:00; cost $55.86 (baseline $56.28); no errors, no retries, no fallbacks |
| `retry_storm` preset (ops, 10:00 to 12:00, 70%; the first two attempts of each call time out) | $58.00 vs $56.28; 1,002 failed attempts, all `APITimeoutError`; every request still resolves with the default 2 retries |
| `retry_storm` with `ATLAS_MAX_RETRIES=1` | $50.13; 397 requests end `error` |

---

## Lecture 7.1: Latency budgets for agents

| Field | Value |
|---|---|
| ID | 7.1 |
| Title | Latency budgets for agents |
| Type | SL (slides + avatar, with one terminal beat) |
| Target duration | 7:00 (about 730 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Write a latency budget end to end, measure it at p95, and treat the budget as a contract the rest of the section enforces. |
| Prerequisites | Section 5 (streaming, TTFT and TPOT from spans) |
| Files used | `10-resources/latency-budget-worksheet.md`; Diagram D7 "latency budget of one request"; `make console-text` |

**Learning objectives**

1. Distinguish time to first token, time per output token and total time, and pick the one users feel.
2. Explain why averages hide the pain and why p95 is the planning number.
3. Fill in the latency budget worksheet for Atlas: the end-to-end contract, the diagnostic numbers underneath, and the headroom left for chaos.

### Script

[B-ROLL: Ops Console Latency page on the `slow_provider` replay. Top: four tiles, p95 reads 8,877 ms. Underneath: end-to-end p95 per hour, flat at about 3.8 s all morning, then 9.2 to 9.4 s from 13:00 to 17:00, the red budget line at 4 s.]

[AVATAR]

Two numbers, same day, same requests. The mean latency for the whole day: four seconds, almost exactly the budget. Nobody would look twice. Underneath, the ninety-fifth percentile per hour. [PAUSE] Flat at three point eight all morning. Then, from one o'clock to five, nine point four seconds. Three in four requests in that window waited more than four seconds for their answer. The mean barely noticed. That's why averages lie, and why this section measures in percentiles.

[SLIDE 1: Three clocks, and the one agents add]
- Time to first token (TTFT): send to first streamed token of one model call. "Is it alive?"
- Time per output token (TPOT): the streaming speed. "Is it fast?"
- Total time: the whole request. What your logs record by default
- Agents add a fourth: time to the first token of the *final answer*, after every tool step

[AVATAR]

Three clocks, and for agents a fourth. Time to first token is how long one model call takes to start. Time per output token is how fast it streams once started. Total time is the whole request. And for an agent, the one users actually feel is the fourth: the first token of the final answer. Atlas runs a tool step before the user sees a single word. The first model call streams nothing to the screen. So the user's clock starts at send and stops when the answer begins. [PAUSE] Measure that one. It's the one that makes people close the tab.

[SLIDE 2: Where the time goes in one Atlas request (the demo request from 6.1, offline)]

Diagram: D7 build 1, latency budget of one request.

| Step | What happens | Time |
|---|---|---|
| 1 | model → tool call: first token 457 ms, 42 tokens | 746 ms |
| tool | `search_knowledge_base` (local index) | a few ms |
| 2 | model → answer: first token 429 ms | first word of the answer at **1,174 ms** |
| 2 | streaming 282 tokens at about 7 ms each | + 2,015 ms |
| Full answer | | **3,189 ms** |

[AVATAR]

Here's the anatomy of the demo request from Section 6. Step one: the model takes under half a second to start and three quarters of a second to finish a forty-two-token tool call. The tool itself takes a few milliseconds. Step two: another half second to start, and the user sees the first word at about one point two seconds. Then two seconds of streaming for a two-hundred-eighty-two-token answer. Three point two seconds in total.

Notice where the time is. [PAUSE] Not in the tool. In the model, twice. Every step you add is another model call before the user sees anything. That's the cost lesson from Section 6 in a different currency.

[SCREEN: terminal, `make console-text`, scrolled to the Latency block]

```
-- Latency ---------------------------------------------------------------------
total  p50=3232ms  p95=3827ms  p99=3934ms  max=4138ms  n=10184
ttft   p50=1427ms  p95=1702ms  n=10112
  eng        p50=3303ms p95=3844ms n=2171
  finance    p50=3511ms p95=3905ms n=1866
  hr         p50=3345ms p95=3836ms n=1851
  ops        p50=2168ms p95=3670ms n=4296
```

Now the whole replayed day. End to end, p50 three point two seconds, p95 three point eight. The `ttft` row is the fourth clock, first token of the final answer: one point four at the median, one point seven at p95. And ops is fastest, because its shipment and ticket questions return short answers.

[SLIDE 3: The budget (Atlas, from the worksheet)]
- Contract: p95 end to end ≤ 4.0 s (`BUDGET_P95_LATENCY_MS`, the CI gate in 13.3, the alert in 9.5)
- Today: p95 3.83 s, so 173 ms of headroom
- Diagnostics under it: answer TTFT p95 1.70 s; per-call TTFT p95 0.65 s; generation p95 2.82 s
- Users feel the first word: watch answer TTFT even though the contract is end to end
- Voice agents (Course 3) budget 800 ms end to end; a chat helpdesk gets 4 s; know which you are

[AVATAR]

Now the budget. One contract: four seconds end to end, at p95. It's in the config as `BUDGET_P95_LATENCY_MS`, the CI gate in Section 13 fails the build above it, and the alert in Section 9 pages on it. [PAUSE] Today's p95 is three point eight three. That's a hundred seventy-three milliseconds of headroom. Not much. When a provider gets slow, that's what we have before we're outside the contract. Underneath the contract sit the diagnostics: the answer's first token, each call's first token, each generation's duration. They tell you which part moved.

If you've taken the voice agents course, you'll remember eight hundred milliseconds end to end. A voice agent has to answer before the silence gets awkward. A chat helpdesk gets five times that. Same discipline, different number. Know which product you are.

[SLIDE 4: Why p95 and not p99 or the mean]
- Mean: hides everything; four slow hours vanish into a day of 10,000 requests
- p50: what the typical user gets; fine for capacity, useless for pain
- p95: one in twenty; the number an engineering team can actually hold
- p99: one in a hundred; watch it, alert on trend, don't budget on it for an LLM app
- Budget at p95, alert on p95, report p50 alongside

[AVATAR]

Why p95, specifically? The mean hides everything; you've seen that. p50 is what the typical person gets; useful for capacity, useless for pain. p99 is one in a hundred, and with a third-party model provider in the loop, you don't control the tail well enough to promise it. p95 is the one an engineering team can actually hold: one in twenty. We budget at p95, we watch p99 for trend, and we report p50 next to it so nobody thinks the typical experience is slow.

[SLIDE 5: The budget worksheet]
- `10-resources/latency-budget-worksheet.md`
- Rows: each step, each tool, each model call; columns: p50, p95, budget, headroom
- Fill it from spans, not from guesses (7.2)
- Every reliability control in 7.3 to 7.5 is justified by a row in this sheet

[AVATAR]

The worksheet is in the resources folder. One row per step, per tool, per model call. Columns for p50, p95, the budget and the headroom. You'll fill it from spans in the next lecture, not from guesses. And every timeout, retry and fallback we add in this section will point back to a row. [PAUSE] Latency and cost pull in opposite directions in one place: retries. A retry is the fastest way to fix a failed call and the fastest way to double your bill. Hold both numbers in your head through this section.

[SLIDE 6: Recap]
- Users feel the answer's first token
- Budget at p95: 4 seconds end to end
- Atlas has 173 ms of headroom today

### Recap

Agents have a fourth clock, the first token of the final answer; Atlas's contract is p95 end to end under four seconds, with 173 ms of headroom on a normal day and the diagnostic clocks underneath, all filled from spans.

### Transition

Next, the code: aggregate TTFT, TPOT and total time from the span store, expose them as Prometheus histograms, and read the Latency page of the Ops Console.

### Speaker notes: common mistakes and Q&A

- **Measuring total time only.** Most frameworks log total duration. Users feel the answer's first token. Both matter; budget the one you can enforce, watch the one they feel.
- **Budgeting the mean.** If a student's worksheet has a mean column, send them back to the chart from the hook.
- **"Just use a faster model."** Model TTFT is half the story; the number of steps is the other half. Fewer steps beat a faster model.
- **Offline numbers.** The mock draws latency per model and per prompt size; the shape is realistic, the constants are simulated. Provider latency changes; the method doesn't.
- **Voice comparison.** The 800 ms figure comes from Course 3's latency section. One sentence, then move on.
- **The hook chart.** Record it with `OFFLINE=1 make replay SCENARIO=slow_provider` and `make console` (Latency page). Lecture 7.6 runs the same replay.

---

## Lecture 7.2: Code-along: measure TTFT, TPOT and p95 from spans

| Field | Value |
|---|---|
| ID | 7.2 |
| Title | Code-along: measure TTFT, TPOT and p95 from spans |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 700 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Derive first-token, per-token and total timings from the span attributes you already emit, compute percentiles without numpy, and expose them as Prometheus histograms with low-cardinality labels. |
| Prerequisites | 7.1; Section 5.4 (`completion_start_time`, `gen_ai.response.time_to_first_chunk`) |
| Files used | `src/northwind/latency.py`, `telemetry/metrics.py`, `telemetry/local_store.py`, `app/agent.py` (`_finish`), Ops Console Latency page, `tests/unit/test_latency.py` |

**Learning objectives**

1. Compute TTFT, TPOT and total time for a request from its generations, and the answer's first token as the sum of the earlier steps plus the last step's TTFT.
2. Use `percentile(values, p)` (linear interpolation, no numpy) and `summarize` for p50, p95 and p99 per tenant and per hour.
3. Read the `atlas_request_latency_seconds{tenant,feature}` and `atlas_ttft_seconds{model}` histograms, with buckets that put an edge on the budget.

### Script

[AVATAR]

You already have the data. Every generation span in Atlas carries its duration, its time to first token, and its output token count. [PAUSE] Three numbers per step, and from them you get all four clocks. No new instrumentation today. Just arithmetic and a histogram.

[SLIDE 1: From spans to clocks]
- TTFT of a call: `atlas.ttft_ms` on the generation span (also `gen_ai.response.time_to_first_chunk`, incubating)
- TPOT: `(total − TTFT) / (output_tokens − 1)`
- Total: the request's duration, `atlas.latency_ms` on the agent span
- Answer's first token: all earlier steps + the last step's TTFT, `atlas.ttft_ms` on the agent span
- Langfuse sees the same moment as `completion_start_time`

[AVATAR]

Time to first token of one call is on the generation span. Time per output token is the rest of the streaming window divided by the tokens in it. Total is the request's duration. And the agent's fourth clock is every earlier step plus the last step's first token, which `_finish` writes on the agent span. All of it comes from attributes you set in lecture 5.4: the incubating `gen_ai.response.time_to_first_chunk` on the OTel side, `completion_start_time` in Langfuse, and our own `atlas.ttft_ms`.

[SCREEN: VS Code, `src/northwind/latency.py`]

[CODE: `src/northwind/latency.py` (excerpt)]

```python
@dataclass(frozen=True)
class LatencySample:
    """One request's timings in milliseconds."""

    total_ms: float
    ttft_ms: float | None = None
    output_tokens: int = 0
    steps: int = 1
    trace_id: str = ""
    tenant: str = ""
    model: str = ""

    @property
    def tpot_ms(self) -> float | None:
        """Time per output token after the first token (ms/token)."""
        if self.ttft_ms is None or self.output_tokens <= 1:
            return None
        return max(0.0, (self.total_ms - self.ttft_ms) / (self.output_tokens - 1))


@dataclass(frozen=True)
class RequestTiming:
    """Whole request assembled from steps; ``to_sample`` gives the aggregate view."""

    trace_id: str
    steps: tuple[StepTiming, ...]
    tenant: str = ""

    @property
    def total_ms(self) -> float:
        return sum(s.total_ms for s in self.steps)

    @property
    def ttft_ms(self) -> float | None:
        """Time until the first token of the *final* answer (what the user perceives)."""
        if not self.steps:
            return None
        last = self.steps[-1]
        if last.ttft_ms is None:
            return None
        return sum(s.total_ms for s in self.steps[:-1]) + last.ttft_ms


def percentile(values: Sequence[float], p: float) -> float:
    """Linear-interpolated percentile; ``p`` in [0, 100]."""
    if not values:
        raise ValueError("percentile of empty sequence")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    k = (len(xs) - 1) * p / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return float(xs[int(k)])
    return float(xs[lo] + (xs[hi] - xs[lo]) * (k - lo))
```

Three pieces. `LatencySample` is one request's timings, and TPOT is a property: the time after the first token, divided by the tokens after the first. Fewer than two tokens, no TPOT. `RequestTiming` builds the agent's fourth clock: every earlier step in full, plus the last step's first token. That's the number on the agent span, and it's the one users feel.

[SCREEN: zoom on `percentile`; the `k = (len(xs) - 1) * p / 100.0` line highlighted]

`percentile` sorts and interpolates linearly between the two neighbours, the same definition pandas uses by default. No numpy, because this runs in the CI gate and in the browser coding exercise. [PAUSE] `summarize`, just below it, gives count, mean, p50, p90, p95, p99, min and max in one call, and `violations` compares a set of samples against a `LatencyBudget` and returns only what's over. Empty list means green. That's what the CI gate in Section 13 asserts for p95.

Now the source: the local span store.

[SCREEN: `telemetry/local_store.py` (`latency_samples`), then terminal]

```bash
OFFLINE=1 make replay
make console-text            # the Latency block: totals, answer TTFT, per tenant, hourly p95
```

[DEMO: output (Latency block):]

```
-- Latency ---------------------------------------------------------------------
total  p50=3232ms  p95=3827ms  p99=3934ms  max=4138ms  n=10184
ttft   p50=1427ms  p95=1702ms  n=10112
  eng        p50=3303ms p95=3844ms n=2171
  finance    p50=3511ms p95=3905ms n=1866
  hr         p50=3345ms p95=3836ms n=1851
  ops        p50=2168ms p95=3670ms n=4296
hourly p95: 00h=3696 01h=3870 02h=3733 03h=3768 04h=3725 05h=3647 06h=3841 07h=3816 08h=3810 09h=3796 10h=3824 11h=3829 12h=3825 13h=3829 14h=3837 15h=3834 16h=3779 17h=3825 18h=3823 19h=3849 20h=3816 21h=3757 22h=3843 23h=3763
```

A word on where these numbers come from in offline mode. The mock LLM doesn't sleep for three seconds per call; it stamps each response with a simulated first-token time and duration, drawn per model and growing with prompt size, so a full day replays in twenty seconds and the percentiles come out realistic. In live mode the same code reads real spans. Either way, the aggregation reads our local store rather than the Langfuse API, because ten thousand traces through a paginated API is slow and Langfuse already shows its own latency views in the UI for browsing. The store is for arithmetic. The UI is for looking.

[SLIDE 2: The worksheet, filled from spans]
- End to end: p50 3,232 ms, p95 3,827 ms, budget 4,000 ms, headroom 173 ms
- Answer's first token: p50 1,427 ms, p95 1,702 ms
- Per call: TTFT p95 652 ms; generation p95 2,824 ms
- Hourly p95: flat, 3,647 to 3,870 ms; no lunchtime bump on a normal day
- By tenant: ops fastest (p95 3,670), finance slowest (p95 3,905)

[AVATAR]

There's the worksheet, filled from spans. End to end, three point eight at p95 against a budget of four. The answer's first token, one point seven. Each model call starts in about two thirds of a second at p95, and the longest generations take nearly three seconds, because that's where the answer streams. And the hourly line is flat: on a normal day, load doesn't move latency. Remember that shape for the chaos demo.

Now the metrics.

[SCREEN: `telemetry/metrics.py`]

[CODE: `telemetry/metrics.py` (excerpt)]

```python
LATENCY_BUCKETS = (0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 20.0)
TTFT_BUCKETS = (0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0)

LATENCY = Histogram(
    "atlas_request_latency_seconds",
    "End-to-end request latency",
    ["tenant", "feature"],
    buckets=LATENCY_BUCKETS,
    registry=REGISTRY,
)
TTFT = Histogram(
    "atlas_ttft_seconds",
    "Time to first token of the final answer",
    ["model"],
    buckets=TTFT_BUCKETS,
    registry=REGISTRY,
)
TOOL_LATENCY = Histogram(
    "atlas_tool_latency_seconds",
    "Tool execution time",
    ["tool"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
    registry=REGISTRY,
)
```

Two rules in this file. First, the buckets bracket the budget: there's a bucket edge at exactly four seconds, so the fraction of requests under budget is a ratio of two counters, not an interpolation. Second, labels: `tenant` and `feature` on the request histogram, `model` on time to first token, `tool` on tool latency, nothing else, and never user or session. Four tenants times seven features times thirteen buckets is fine; four thousand users is not. [PAUSE] Per-user latency lives in the span store, where cardinality is free.

[SCREEN: `app/agent.py`: in `_finish`, `metrics.record_request(tenant=tenant, model=result.model, outcome=result.outcome, latency_s=result.latency_ms / 1000.0, steps=result.steps, feature=result.feature)`; in `_call_model`, `metrics.record_generation(..., ttft_s=ttft_s)`]

One `record_request` at the end of the request feeds the request histogram, and one `record_generation` per model call feeds `atlas_ttft_seconds`. Read that carefully: despite its help text, `atlas_ttft_seconds` is observed once per model call, so its p95 is the six-hundred-fifty-millisecond number, not the answer's one point seven. The answer's first token lives on the agent span. Label your panels with the one you mean.

[SCREEN: Ops Console Latency page: the p50 / p95 / p99 and "TTFT p95 (final answer)" tiles, hourly p50 and p95 with the 4 s budget line, span p95 by observation type, generation TTFT and duration p95 per hour]

The Latency page shows the same numbers: four tiles, the hourly chart with the budget line in red, span p95 by observation type, and the generation detail. Same store, same functions, same numbers as the terminal.

[SCREEN: `tests/unit/test_latency.py`, then terminal `uv run pytest tests/unit/test_latency.py -q`: `13 passed`]

The unit tests pin the arithmetic: `test_percentile_linear_interpolation`, `test_request_timing_ttft_is_perceived` for the fourth clock, and `test_violations_aggregate_and_per_sample` for the budget check.

[SLIDE 3: Recap]
- Four clocks fall out of span attributes
- Percentiles: linear interpolation, no numpy
- Histograms: bucket edge at the budget

### Recap

TTFT, TPOT, total time and the answer's first token fall out of the span attributes you already emit; `percentile` interpolates without numpy; histograms get a bucket edge at the four-second budget and labels for tenant, feature, model and tool only.

### Transition

Now you can see where the time goes. Next, the controls that hold it: timeouts, bounded retries and backoff, done so they don't turn a slow minute into a cost incident.

### Speaker notes: common mistakes and Q&A

- **TPOT with one token.** Division by zero; the code returns `None` for fewer than two output tokens.
- **Missing TTFT.** Non-streaming calls have no first chunk; online, the agent then records `completion_start_time` instead and TTFT is unknown for that call. Offline the mock always reports one.
- **`atlas_ttft_seconds` naming.** The help text says "final answer", but it is observed per generation. The answer's first token is `atlas.ttft_ms` on the agent span and the console's "TTFT p95 (final answer)" tile. Flag this to students who build their own panel.
- **Interpolated percentiles.** Our `percentile` and Prometheus's `histogram_quantile` both interpolate, but Prometheus interpolates inside a bucket. Small differences are expected; the bucket edge at 4 s makes the SLO ratio exact.
- **Coding exercise.** "Percentile latency" in `06-assessments/coding-exercises.md` is this `percentile` function, stdlib only.

---

## Lecture 7.3: Timeouts, retries and backoff done right

| Field | Value |
|---|---|
| ID | 7.3 |
| Title | Timeouts, retries and backoff done right |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 700 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Give every call a timeout derived from the budget, bound retries with jittered backoff, keep tool writes safe to repeat, and count every retry as the cost event it is. |
| Prerequisites | 7.2; 6.7 (budget guard) |
| Files used | `app/agent.py`, `src/northwind/config.py`, `telemetry/metrics.py`, `simulator/scenarios.py` (`retry_storm`), Ops Console Reliability page |

**Learning objectives**

1. Set the per-call timeout (`ATLAS_REQUEST_TIMEOUT_S`) and the retry bound (`ATLAS_MAX_RETRIES`) from the latency budget and the failure shape.
2. Read Atlas's bounded retries with exponential backoff and jitter, only for `RETRYABLE` errors, and the generation span each failed attempt leaves behind.
3. Measure a retry storm as a cost event (`atlas_llm_retries_total{model,reason}`, the Reliability page) and choose the bound with both cost and outcomes in view.

### Script

[B-ROLL: Ops Console, Reliability page on the `retry_storm` replay. "LLM retries by error.type": 588 `APITimeoutError` at 10:00, 414 at 11:00, nothing before or after. Caption: `retry_storm`, ops, 10:00 to 12:00.]

[AVATAR]

Ten o'clock on a Monday. The provider starts timing out on most of ops's calls. Atlas does what it was built to do: try again. Each timed-out call fails twice before the third attempt gets through. [PAUSE] One thousand and two failed attempts in two hours, every one of them billed for its input tokens, and every user still got an answer, a bit later. Was that retry policy right? By the end of this lecture you'll be able to answer with a number, not a feeling.

[SLIDE 1: Three rules]
- Timeouts come from the budget, not from a default
- Retries are bounded, jittered, and only for errors that a retry can fix
- Every retry is a cost event: count it, and price it

[AVATAR]

Three rules. Timeouts derive from the budget you wrote in 7.1. Retries are bounded, jittered, and only for errors a retry can actually fix. And every retry is a cost event. It goes on a counter and on its own generation span with a price, so a storm shows up on the bill you can see, not just on the invoice.

[SLIDE 2: Timeouts from the budget]
- `ATLAS_REQUEST_TIMEOUT_S`: per model call, default 20 s, passed to the client and the Router
- Normal calls: TTFT p95 0.65 s, generation p95 2.8 s (7.2)
- A timeout near 2× the slowest normal call (about 6 s) cuts off a stall, not a long answer
- 20 s × 3 attempts is a minute of waiting before the user sees an error
- Offline the mock never times out a call; this setting matters against a real provider (verify the client's timeout semantics)

[AVATAR]

Timeouts. Atlas has one, `ATLAS_REQUEST_TIMEOUT_S`, twenty seconds by default, passed to the OpenAI client and the Router on every call. Is twenty right? Look at the worksheet. A normal call starts in two thirds of a second at p95 and finishes in under three. So twenty seconds is seven times the slowest normal call. [PAUSE] With two retries, a stalled provider can make one user wait a minute before they see an error. Something near twice the slowest normal call, around six seconds, cuts off a stall without cutting off a long answer. One caution: offline, the mock never times out, so this knob only shows its effect against a real provider. Lab 4 and `.env.chaos.example` spell that out.

[SCREEN: VS Code, `app/agent.py`]

[CODE: `app/agent.py` (excerpt): retryable errors, backoff and the retry loop]

```python
RETRYABLE: tuple[type[BaseException], ...]
try:
    import openai

    RETRYABLE = (
        openai.APITimeoutError,
        openai.RateLimitError,
        openai.APIConnectionError,
        openai.InternalServerError,
    )
except Exception:  # noqa: BLE001 - pragma: no cover
    RETRYABLE = (TimeoutError, ConnectionError)
```

```python
    def _backoff(self, attempt: int) -> float:
        if self.settings.offline:
            return 0.0
        return min(2.0**attempt * 0.25, 4.0) * (0.5 + 0.5 * (hash(attempt) % 100) / 100)
```

```python
        # _call_model(): one logical LLM call with bounded retries, fallback and one generation span per attempt
        attempts = 0
        current = model
        last_exc: BaseException | None = None
        while attempts <= self.settings.max_retries:
            attempts += 1
            if self.breaker.is_open(current) and current in FALLBACKS:
                ...                                         # 7.4: switch to FALLBACKS[current]
            gen = GenerationRecord(model=current, step=step, attempt=attempts)
            with self.tracer.start_as_current_span(ga.llm_span_name(current)) as span:
                ...
                if attempts > 1:
                    span.set_attribute(ga.ATLAS_RETRIES, attempts - 1)
                try:
                    ...
                    resp = self.llm.chat(**kwargs)          # kwargs include timeout=settings.request_timeout_s
                    ...
                    self.breaker.record_success(current)
                    return message, finish, current
                except RETRYABLE as exc:
                    last_exc = exc
                    # A timed-out call still cost tokens on the provider side: estimate and record it.
                    inp = count_message_tokens(messages)
                    cost = self._price(current, inp, 0, 0, 0)
                    ga.set_llm_usage(span, input_tokens=inp, output_tokens=0)
                    ga.set_cost(span, cost)
                    ga.set_error(span, exc)
                    ...
                    result.retries += 1
                    metrics.LLM_RETRIES.labels(current, type(exc).__name__).inc()
                    ...
                    self.breaker.record_failure(current)
            self._sleep(self._backoff(attempts))
        raise RuntimeError(f"LLM unavailable after {attempts} attempts") from last_exc
```

Read the `except`. Only `RETRYABLE` errors get here: timeouts, rate limits, connection errors, server errors. A bad request or an auth error propagates immediately, because retrying it is pointless. Then the honest bill: a timed-out call still cost input tokens on the provider side, so the attempt gets its own generation span with the estimated input tokens, the cost and the error type. That is the line Incident 1 is about.

[SCREEN: zoom on `metrics.LLM_RETRIES` and `_backoff`]

Then the counter, `atlas_llm_retries_total`, with the model and the reason. Then the breaker learns about the failure, and the loop bound, `ATLAS_MAX_RETRIES`, two by default, decides whether there is another attempt. Then jittered backoff: a quarter second doubling per attempt, capped at four seconds, with up to half of it random, and zero offline so the replay stays fast. [PAUSE] Jitter is not optional. Without it, a thousand clients that failed at the same instant retry at the same instant, and you've built a synchronised storm.

[SLIDE 3: Tool calls: who retries, and what must be safe to repeat]
- Atlas never re-runs a tool by itself; the model decides to call it again (the loop scenario in 5.6)
- `ATLAS_MAX_TOOL_RETRIES` bounds that: after N failures of one tool, stop and say so (`tool_retries_exhausted`)
- Reads (`lookup_ticket`, `check_shipment`) are naturally safe to repeat
- Writes (`create_ticket`) are not: give a write an idempotency key (trace id + step) before you let anything retry it
- Atlas's `create_ticket` has no key yet: it is only ever called once per step, and that's the rule to keep

[AVATAR]

Tools have their own retry problem. Atlas never re-runs a tool by itself. The model asks for it again, which is exactly the loop from lecture 5.6, and `ATLAS_MAX_TOOL_RETRIES` is the bound that turns a failing tool into an honest answer. Reads are safe to repeat. Writes aren't. If anything in your stack ever retries `create_ticket`, give it an idempotency key first, the trace id plus the step, so a retry returns the same ticket instead of opening a second one.

[SCREEN: terminal]

Now replay the storm, twice.

```bash
OFFLINE=1 make replay SCENARIO=retry_storm STORE=.atlas/retry2.sqlite                    # shipped bound: 2 retries
OFFLINE=1 ATLAS_MAX_RETRIES=1 make replay SCENARIO=retry_storm STORE=.atlas/retry1.sqlite  # tighter bound
```

[DEMO: the two summaries:]

```
Total cost $57.9980   p95 latency 3889 ms   elapsed 19.4s
Outcomes: escalated=40, guardrail=66, resolved=10088
...
Total cost $50.1286   p95 latency 3946 ms   elapsed 19.7s
Outcomes: error=397, escalated=36, guardrail=66, resolved=9695
```

[SLIDE 4: The storm, two bounds (ops, 10:00 to 12:00; full day)]

| | 2 retries (shipped) | 1 retry |
|---|---|---|
| Day cost | $58.00 (+$1.72 vs $56.28) | $50.13 |
| Failed attempts billed (Reliability page) | 1,002, all `APITimeoutError` | 806 |
| Requests ending `error` | 0 | **397** |
| What users saw | every answer, a little later | 397 "Atlas is temporarily unavailable" |

[AVATAR]

With the shipped bound of two, the storm costs a dollar seventy-two extra, a thousand failed attempts billed for their input, and every request still resolves. Tighten it to one retry, and the day gets cheaper, fifty dollars thirteen. [PAUSE] Cheaper because three hundred ninety-seven people got an error instead of an answer, and their requests stopped spending. That's not a saving. The right bound comes from the failure shape: here the provider fails exactly twice, so two is the smallest bound that works. Retries are a trade between cost and outcomes, and you only see the trade when both are on the same table.

[SLIDE 5: Retry checklist]
- One timeout per call, justified by a row in the worksheet
- Retry only `RETRYABLE`; never a bad request
- Bounded (`ATLAS_MAX_RETRIES`), jittered, capped
- Every failed attempt: its own span, its own price, a counter
- Writes take an idempotency key before anything retries them

[AVATAR]

The checklist. Every timeout justified by a worksheet row. Retry only what can succeed. Bounded, jittered, capped. Every failed attempt priced on its own span and counted. Writes idempotent. And the counter is what turns a retry storm into a page instead of an invoice: Section 9 alerts above a fifth of a retry per request.

[SLIDE 6: Recap]
- One timeout per call, from the budget
- Bounded, jittered retries; every attempt priced
- Choose the bound with cost and outcomes together

### Recap

Derive the per-call timeout from the budget, bound retries with jittered backoff and only for retryable errors, price every failed attempt on its own span, and choose the bound by looking at cost and outcomes together: one retry saved money on `retry_storm` by turning 397 answers into errors.

### Transition

Retries help when the failure is brief. When a whole model goes bad for an hour, you need somewhere else to send the traffic. Next: fallbacks and circuit breakers.

### Speaker notes: common mistakes and Q&A

- **Retrying after partial output.** With streaming, a failure mid-stream is still an exception on the call; Atlas retries the whole step. That's acceptable because nothing reached the user before the final step; on the final step it would mean a repeated beginning. Mention it as a production edge case.
- **`num_retries` on the Router and our own loop.** `build_router_config` passes `num_retries=settings.max_retries` to the Router, and the agent loop has its own bound. In router mode they multiply; say which one you are demoing and prefer one.
- **Idempotency keys from timestamps.** Time changes between attempts. Use trace id plus step.
- **Retry-After.** The loop backs off with jitter but does not read a provider's `Retry-After` header yet; 7.5 covers why you should.
- **Backoff cap.** `min(2**attempt * 0.25, 4.0)`: with two retries the cap never matters, but keep it.
- **Verify exception class names** on the installed `openai` before recording.

---

## Lecture 7.4: Fallbacks and circuit breakers with the Router

| Field | Value |
|---|---|
| ID | 7.4 |
| Title | Fallbacks and circuit breakers with the Router |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 650 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Give every model a fallback, put a circuit breaker in front of it so a failing deployment is bypassed automatically, and log every fallback with the served model so you can see what it cost. |
| Prerequisites | 7.3; 6.6 (Router setup) |
| Files used | `app/agent.py` (`FALLBACKS`, `build_router_config`, `CircuitBreaker`, `_call_model`), `src/northwind/config.py`, `telemetry/metrics.py`, `tests/unit/test_agent.py` |

**Learning objectives**

1. Explain a circuit breaker's three states (closed, open, half-open) and map them to the Router's `allowed_fails` and `cooldown_time` and to Atlas's own `CircuitBreaker`.
2. Read the `FALLBACKS` table and order a fallback list by cost and failure independence.
3. Log a fallback on the span (served model, `error.type` on the failed attempts) and in `atlas_model_fallbacks_total{from_model,to_model}`, and price it on the model that answered.

### Script

[AVATAR]

A retry says: try the same thing again. A fallback says: try something else. [PAUSE] When gpt-4.1-mini stops answering for twenty minutes, retrying it is just waiting three times. Sending the step to another model is what gets the user an answer. And a circuit breaker stops you from hammering the broken one while it recovers.

[SLIDE 1: Circuit breaker in three states]
- Closed: traffic flows to the model; failures are counted
- Open: after `threshold` consecutive failures, skip the model for `cooldown_s`; traffic goes to the fallback
- Half-open: after the cooldown, the next request probes; success closes the circuit, failure re-opens it
- Atlas's `CircuitBreaker`: 3 failures, 30 s. The Router's equivalents: `allowed_fails`, `cooldown_time`

[AVATAR]

Three states. Closed is normal: requests flow, failures get counted. Open: after three failures in a row, the model is skipped for thirty seconds and everything goes to the fallback. Half-open: when the cooldown ends, the next request probes the model. Success closes the circuit. Another failure re-opens it. In the LiteLLM Router those are `allowed_fails` and `cooldown_time`; Atlas also has its own small breaker, because it runs without the Router offline and in tests.

[SCREEN: VS Code, `app/agent.py`]

[CODE: `app/agent.py` (excerpt): fallback table, Router config and the breaker]

```python
FALLBACKS: dict[str, str] = {
    "gpt-4.1-mini": "gpt-4o-mini",
    "gpt-4o-mini": "gpt-4.1",
    "gpt-4.1": "gpt-4.1-mini",
    "gpt-5-mini": "gpt-4.1-mini",
    "gpt-4.1-nano": "gpt-4.1-mini",
}
```

```python
def build_router_config(settings: Settings) -> dict[str, Any]:
    ...
    return {
        "model_list": [...],                                   # one deployment per model (6.6)
        "fallbacks": [{m: [FALLBACKS[m]]} for m in models if m in FALLBACKS],
        "num_retries": settings.max_retries,
        "timeout": settings.request_timeout_s,
        "allowed_fails": settings.router_allowed_fails,        # ATLAS_ROUTER_ALLOWED_FAILS, default 3
        "cooldown_time": settings.router_cooldown_s,           # ATLAS_ROUTER_COOLDOWN_S, default 30
    }
```

```python
class CircuitBreaker:
    """Per-model breaker: open after ``threshold`` consecutive failures, half-open after cooldown."""

    def __init__(
        self,
        threshold: int = 3,
        cooldown_s: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        ...

    def is_open(self, model: str) -> bool:
        opened = self._opened_at.get(model)
        if opened is None:
            return False
        if self._clock() - opened >= self.cooldown_s:
            return False  # half-open: allow a probe
        return True
```

Five models and one fallback each, in a plain table. `gpt-4.1-mini` falls back to `gpt-4o-mini`, a different model family, so a problem with one family doesn't take both; `gpt-4o-mini` falls back up to `gpt-4.1`, because a dearer answer beats no answer; `gpt-4.1` falls back down to mini, because if the strong model is down you still answer; and nano and `gpt-5-mini` fall back to mini.

[SCREEN: zoom on `allowed_fails` and `cooldown_time`, then on `is_open`]

The Router gets the same table through `build_router_config`, plus `allowed_fails` and `cooldown_time`, both from the environment. [PAUSE] And because Atlas also runs without the Router, `CircuitBreaker` does the same job in-process: it opens for a model after three consecutive failures, half-opens after thirty seconds, and `_call_model` consults it before every attempt.

One thing the Router does not tell you by default: that a fallback happened. We need that on the span and on a counter.

[CODE: `app/agent.py` (excerpt): logging fallbacks, in `_call_model`]

```python
            if self.breaker.is_open(current) and current in FALLBACKS:
                nxt = FALLBACKS[current]
                metrics.FALLBACKS.labels(current, nxt).inc()
                result.fallbacks += 1
                log.warning("circuit open for %s; falling back to %s", current, nxt)
                current = nxt
            gen = GenerationRecord(model=current, step=step, attempt=attempts)
            with self.tracer.start_as_current_span(ga.llm_span_name(current)) as span:
```

Before each attempt, if the breaker is open for the model we wanted, switch to its fallback, count it with from and to, log a warning with both names, and open the generation span under the model that will actually answer. [PAUSE] Two things this buys you. Cost attribution stays honest: `_price` runs on `current`, the model that answered, and the span is named after it. And the fallback rate becomes a time series, `atlas_model_fallbacks_total`, which Grafana plots next to the retries in Section 9.

[SCREEN: terminal]

Let's watch it happen. Offline, with a provider that never answers gpt-4.1-mini in time.

```bash
OFFLINE=1 OTEL_EXPORTER=none ATLAS_PROMPT_CACHE=0 ATLAS_CONTEXT_DIET=0 uv run python -c "
import logging; logging.disable(logging.WARNING)
import httpx, openai
from app.agent import AtlasAgent
from app.mock_llm import MockLLM

class StallingProvider(MockLLM):
    '''gpt-4.1-mini never answers within the timeout; every other model does.'''
    def chat(self, *, model, **kw):
        if model == 'gpt-4.1-mini':
            raise openai.APITimeoutError(request=httpx.Request('POST', 'https://api.openai.com/v1/chat/completions'))
        return super().chat(model=model, **kw)

a = AtlasAgent(llm=StallingProvider(seed=7))
for i in range(3):
    r = a.run('When is payroll paid?', tenant='hr')
    print(i + 1, r.outcome, r.model, f'retries={r.retries} fallbacks={r.fallbacks} cost=\${r.cost_usd:.5f}')
print('breaker:', a.breaker.state('gpt-4.1-mini'))
"
```

[DEMO: output:]

```
1 error gpt-4.1-mini retries=3 fallbacks=0 cost=$0.00302
2 resolved gpt-4o-mini retries=0 fallbacks=2 cost=$0.00167
3 resolved gpt-4o-mini retries=0 fallbacks=2 cost=$0.00167
breaker: open
```

Request one pays for the lesson: three timed-out attempts, all billed for their input, three tenths of a cent, and the user gets an error. Those three failures open the circuit. [PAUSE] Request two never touches mini: both steps go straight to `gpt-4o-mini`, two fallbacks, resolved. Request three, same. And notice the price: the fallback answer cost less than a mini answer, because gpt-4o-mini is cheaper per token. A fallback can make a request dearer or cheaper. That's why it's priced on the served model.

[SLIDE 2: What to log when a fallback fires]
- On the generation span: the served model (span name and `gen_ai.request.model`), cost on that model
- On each failed attempt: its own span with `error.type` and an estimated cost (7.3)
- Counter: `atlas_model_fallbacks_total{from_model,to_model}`; the reason is in the failed attempts and the warning log
- Not on the span: the full error body (size and PII); put it in the structured log with the trace id
- A fallback is not an error to the user; it's a warning to you

[AVATAR]

Log the served model and the reason. Keep the error body in the structured log, not the span, because error bodies are big and sometimes contain the prompt. And treat a fallback as a warning, not an error. A fallback is a success for the user. If you log it as an error, your error rate lies during every provider hiccup. [PAUSE] Resilience has a price, and you can read it in the showback by model: when fallbacks fire, a new model appears in the "Cost by model" table. Read that table weekly. A fallback line that creeps up is a provider degrading before it has an incident.

[SCREEN: terminal, `uv run pytest tests/unit/test_agent.py -q -k "retry or fallback or breaker"`]

[DEMO: `3 passed, 21 deselected`: `test_retry_storm_is_billed`, `test_circuit_breaker_states`, `test_fallback_after_circuit_opens`]

Three unit tests pin this offline: failed attempts are billed with their error type, the breaker moves through closed, open and half-open on a fake clock, and once it's open the next call goes to `FALLBACKS[model]`.

[SLIDE 3: Recap]
- Every model has one fallback
- Breaker: 3 failures open, 30 s cooldown
- Price the fallback on the served model

### Recap

Give every model a fallback in `FALLBACKS`, open a breaker after three failures and probe after thirty seconds (`CircuitBreaker`, or the Router's `allowed_fails` and `cooldown_time`), count every fallback in `atlas_model_fallbacks_total{from_model,to_model}`, and price the generation on the model that answered.

### Transition

Fallbacks handle a failing model. Next, the provider and your own traffic say "too much": rate limits, per-tenant queues, and how to degrade gracefully instead of failing loudly.

### Speaker notes: common mistakes and Q&A

- **Fallback to the same model on the same provider.** It fails the same way. Different model or different provider, never the same deployment.
- **Strongest model first in the list.** It works and costs 5× for the whole outage. Cheapest viable first.
- **Silent fallbacks.** The Router does not annotate spans. Opening the generation span under `current`, the model that answers, is our code; without it, the trace says gpt-4.1-mini and the bill says something else.
- **Cooldown too long.** 30 s means a long outage costs you a probe every 30 s, which is cheap. 30 minutes means you miss the recovery.
- **The demo's first request errors.** With `ATLAS_MAX_RETRIES=2` the first request uses all three attempts on mini before the breaker opens. That's the price of learning; a lower `threshold` opens sooner and flaps more.
- **Verify Router kwargs** on the installed litellm: `model_list`, `fallbacks`, `num_retries`, `timeout`, `allowed_fails`, `cooldown_time` are present on 1.103; `context_window_fallbacks` and `routing_strategy` are extensions for a second provider under the same logical name.

---

## Lecture 7.5: Rate limits, queues and graceful degradation

| Field | Value |
|---|---|
| ID | 7.5 |
| Title | Rate limits, queues and graceful degradation |
| Type | SL (slides + avatar, with a short code and terminal beat) |
| Target duration | 6:00 (about 640 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Treat 429s and queues as a capacity problem: back off and count, cap concurrency per tenant, shed the least valuable traffic first, and tell users the truth in degraded mode. |
| Prerequisites | 7.4; 6.7 (economy mode) |
| Files used | `app/server.py` (`TenantLimiter`), `src/northwind/config.py` (`ATLAS_TENANT_MAX_INFLIGHT`, `ATLAS_QUEUE_TIMEOUT_S`), `telemetry/metrics.py`; diagram "request path with per-tenant semaphores" |

**Learning objectives**

1. Handle a provider's HTTP 429 correctly: back off with jitter, count it, let the breaker or the Router cool the deployment, and know where `Retry-After` fits.
2. Read Atlas's per-tenant concurrency limiter (`TenantLimiter`) and its three metrics, and size the slots from the showback.
3. Define a shedding order and a degraded-mode message that keeps trust.

### Script

[AVATAR]

Half past nine on the busiest day of the quarter. A shipping system goes down and everyone in operations opens Atlas at once to ask where their pallets are. The provider starts answering a third of Atlas's calls with 429: too many requests. [PAUSE] Here's the question. Who should wait? If your answer is "whoever came last," finance is about to lose its payroll question to a hundred pallet lookups.

[SLIDE 1: What a provider's 429 is telling you]
- You are over a tokens-per-minute or requests-per-minute limit for this key or model
- It often carries `Retry-After` (seconds); honour it rather than guessing
- It is retryable, but retrying immediately makes it worse for everyone on the key
- Atlas: `RateLimitError` is in `RETRYABLE`; counted in `atlas_llm_retries_total{reason="RateLimitError"}`; three in a row open the breaker
- Persistent 429s are a capacity signal: raise the limit, add a provider, or shed load

[AVATAR]

A 429 from the provider means you've exceeded a per-minute limit for tokens or requests. It often carries a `Retry-After` header. Honour that number, and don't retry immediately, because everyone else on the same key is retrying too. Atlas's loop from 7.3 handles the basics: `RateLimitError` is retryable, the backoff is jittered, every one is counted with its reason, and three in a row open the breaker so the fallback takes over. Reading `Retry-After` itself is the next improvement, and a short one. [PAUSE] But if 429s are persistent, that's not an error. It's capacity. And capacity has three answers: pay for more, add a second provider, or decide who waits. The third one is ours to build.

[SLIDE 2: Per-tenant concurrency]
- One semaphore per tenant, sized from the showback share of sessions: ops 13, eng 7, finance 6, hr 6, unknown tenants 2
- A request waits up to `ATLAS_QUEUE_TIMEOUT_S` (3 s) for a slot in its own tenant's queue, then gets HTTP 429 with `Retry-After: 1`
- No tenant can take more than its share of the provider's capacity
- Metrics: `atlas_inflight{tenant}`, `atlas_queue_wait_seconds{tenant}`, `atlas_requests_shed_total{tenant}`
- Diagram: requests → tenant semaphores → agent → provider

[B-ROLL: diagram builds. Four lanes labelled by tenant, each with its slot count, merging into Atlas, then a single pipe to the provider. The ops lane fills to red; the other three stay green.]

[AVATAR]

One semaphore per tenant, sized from the showback: ops gets thirteen slots, eng seven, finance six, hr six, and an unknown tenant two. When ops fills its thirteen, the next pallet question waits in ops's own queue, up to three seconds, and is then turned away with a 429 and a one-second `Retry-After`. Finance's six slots are untouched. [PAUSE] That's the whole trick. The provider's limit is shared, so somebody has to divide it before the provider does it for you, and the provider divides it by who asked first.

[SCREEN: VS Code, `app/server.py`]

[CODE: `app/server.py` (excerpt): `TenantLimiter`]

```python
class TenantLimiter:
    """One semaphore per tenant (Lecture 7.5). A request waits up to ``timeout_s`` for a slot in
    its own tenant's queue; then it is shed with 429 so one noisy tenant cannot take every
    provider slot. ``atlas_inflight{tenant}`` and ``atlas_queue_wait_seconds{tenant}`` show it."""

    @asynccontextmanager
    async def slot(self, tenant: str):  # type: ignore[no-untyped-def]
        sem = self._sem(tenant)
        t0 = time.perf_counter()
        try:
            await asyncio.wait_for(sem.acquire(), timeout=self.timeout_s)
        except TimeoutError:
            metrics.QUEUE_WAIT.labels(tenant).observe(time.perf_counter() - t0)
            metrics.SHED.labels(tenant).inc()
            raise HTTPException(
                status_code=429,
                detail=f"tenant {tenant} is at its concurrency limit; retry shortly",
                headers={"Retry-After": "1"},
            ) from None
        metrics.QUEUE_WAIT.labels(tenant).observe(time.perf_counter() - t0)
        metrics.INFLIGHT.labels(tenant).inc()
        try:
            yield
        finally:
            metrics.INFLIGHT.labels(tenant).dec()
            sem.release()
```

Twenty lines. Wait for your tenant's semaphore, up to the queue timeout. If the wait runs out, record how long it waited, count a shed, and answer 429 with `Retry-After`. Otherwise count yourself in flight, run the agent, and release on the way out, even on an exception. The `/chat` route wraps the agent call in `async with limiter.slot(tenant)`.

[SCREEN: terminal: Atlas started with one slot for ops and a half-second queue, and the mock sleeping its simulated latency; then five requests at once, four from ops and one from finance]

```bash
# terminal 1
OFFLINE=1 OTEL_EXPORTER=none ATLAS_TENANT_MAX_INFLIGHT=ops=1 ATLAS_QUEUE_TIMEOUT_S=0.5 ATLAS_MOCK_LATENCY_SCALE=1 make run
```

```bash
# terminal 2: five requests at once
for t in ops ops ops ops finance; do
  curl -s -o /dev/null -w "$t %{http_code} %{time_total}s\n" -X POST localhost:8000/chat \
       -H 'Content-Type: application/json' -H "X-Tenant: $t" -d '{"message": "When is payroll paid?"}' &
done; wait
```

[DEMO: the five responses, then `curl -s localhost:8000/metrics/ | grep -E "^atlas_(inflight|requests_shed_total|queue_wait_seconds_count)"`:]

```
ops 429 0.505642s
ops 429 0.504116s
ops 429 0.508527s
finance 200 2.975176s
ops 200 2.979478s
atlas_inflight{tenant="ops"} 0.0
atlas_inflight{tenant="finance"} 0.0
atlas_queue_wait_seconds_count{tenant="ops"} 4.0
atlas_queue_wait_seconds_count{tenant="finance"} 1.0
atlas_requests_shed_total{tenant="ops"} 3.0
```

One ops request gets the slot and takes three seconds. Three more ops requests wait half a second each and are shed. Finance never notices: its own slot, answered in three seconds. The counters agree: three shed, all ops.

[SLIDE 3: Shedding order (what to drop first when you must)]
1. Repeat `shipment_status` checks within 5 minutes: serve the tool result you already have, no model call
2. Non-urgent `policy_question` from a tenant over its soft cap: economy mode (6.7)
3. Judge sampling (Section 8): pause it; it's your own traffic
4. Escalations to gpt-4.1: hold, unless the request is sensitive
5. Never shed: `password_reset`, and `create_ticket` for priority P1 and P2

[AVATAR]

When you must shed, shed in a declared order. This is policy you write, not something Atlas ships today beyond the economy mode from 6.7. First, repeated shipment checks: serve the tool result you already have. Second, policy questions from a tenant already over its soft cap go to economy mode. Third, your own traffic: pause the judge sampling from Section 8. Fourth, hold escalations to the strong model unless they're sensitive. And never shed password resets and urgent tickets. [PAUSE] Write this list down before the incident. During the incident nobody has time to argue about it.

[SLIDE 4: Degraded mode messaging]
- Say what's happening: "Atlas is busy right now, so this answer is shorter than usual."
- Say what still works: "Ticket creation and password resets are unaffected."
- Say what to do: Atlas's budget refusal already does: "open a ticket in ServiceHub ... urgent issues can call extension 4000"
- Never fake it: no invented answers to fill a shorter budget
- Make it countable: `budget_decision` is in every response and `atlas.budget.decision` on the trace

[AVATAR]

And the message. Degraded mode is not a failure if you tell the truth. Say what's happening, say what still works, say what to do; Atlas's budget refusal from 6.7 already points to a ticket and a phone extension. Never let a shorter budget turn into an invented answer. And make it countable: the decision is in every response and on every trace, so the number of degraded answers sits on the dashboard next to the number of fallbacks.

[SLIDE 5: Recap]
- Back off on 429s; persistent ones mean capacity
- One semaphore per tenant, sized from the showback
- Shed in a declared order; tell users the truth

### Recap

Back off and count on 429s, divide capacity with per-tenant semaphores sized from the showback (`TenantLimiter`, shed with 429 and `Retry-After`), shed in a declared order starting with your own traffic, and tell users the truth in degraded mode.

### Transition

Time for chaos. In the next lecture we inject a slow provider in the busy afternoon and watch p95, retries and cost, then work out what would actually fix it.

### Speaker notes: common mistakes and Q&A

- **Global concurrency only.** One tenant's burst still starves the others. Per-tenant is the point.
- **Semaphore sizes as guesses.** The defaults come from the showback share of sessions (ops 43%); `ATLAS_TENANT_MAX_INFLIGHT=ops=13,eng=7,...` or a single number for every tenant. Revisit monthly.
- **Two different 429s.** The provider's 429 is an error Atlas retries; Atlas's own 429 is a shed it returns to the caller. Name them differently on the dashboard.
- **Shedding writes first.** Students often drop `create_ticket` because it's "expensive". It's the one thing users can't get elsewhere. Never shed writes.
- **The demo needs `ATLAS_MOCK_LATENCY_SCALE=1`.** Offline the mock answers instantly unless it sleeps its simulated latency; without it, nobody ever waits for a slot. `test_tenant_limiter_sheds_after_queue_timeout` pins the same behavior in CI.

---

## Lecture 7.6: Chaos demo: slow provider during peak

| Field | Value |
|---|---|
| ID | 7.6 |
| Title | Chaos demo: slow provider during peak |
| Type | DM (live demo) |
| Target duration | 7:00 (about 760 spoken words at ~140 wpm; remaining time is dashboards and runs) |
| One idea | Inject a slow provider in the busy afternoon, read the silent incident from three charts (p95 up, retries and cost flat), and see which fixes buy seconds and which buy milliseconds. |
| Prerequisites | 7.1 to 7.5 |
| Files used | `simulator/scenarios.py` (`slow_provider` preset), Ops Console Latency, Reliability and Cost pages, `.env.chaos.example`, `tests/unit/test_agent.py` |

**Learning objectives**

1. Read a latency incident from three charts: hourly p95 against the budget, LLM retries by error type, and cost per hour.
2. Explain why a slow provider produces no errors, no retries and no fallbacks until something turns slowness into an error.
3. Measure what you control (the context diet, routing) against the incident, and say what only a timeout plus a second provider can fix.

### Script

[AVATAR]

Everything in this section has been a claim. Budgets, timeouts, retries, fallbacks, per-tenant queues. [PAUSE] Claims are cheap. Let's slow the provider down in the busiest part of the afternoon and see what's true.

[SLIDE 1: The scenario: `slow_provider`]
- 13:00 to 17:00, the afternoon peak, 75% of requests hit
- Every call's time to first token ×3.5, streaming speed halved
- No errors. No 429s. Just slow. The hardest kind of incident to see
- Same seed, same 4,000 sessions as the baseline day

[AVATAR]

The scenario. Four hours of the afternoon peak. Three in four requests get a provider that takes three and a half times longer to start and streams at half speed. No errors. Nothing returns a status code you could alert on. Just slow. This is the incident that gets you a chat message saying "is Atlas down?" while every health check is green.

[SCREEN: terminal, then the Ops Console with three pages side by side: Latency (hourly p50 and p95, red 4 s budget line), Reliability (LLM retries by `error.type`), Cost (cost per hour by tenant)]

Run it.

```bash
OFFLINE=1 make replay SCENARIO=slow_provider STORE=.atlas/slow.sqlite
make console STORE=.atlas/slow.sqlite
```

[DEMO: the replay summary, then the three pages:]

```
Replay seed=7  requests=10114  sessions=4000  spans=69989  scores=11956  feedback=1284
Total cost $55.8560   p95 latency 8877 ms   elapsed 19.5s
Outcomes: escalated=47, guardrail=71, resolved=9996
Scenarios: none=7473, slow_provider=2641
Incidents: slow_provider@13-17h
```

Watch the p95 line. Flat at three point eight all morning. At one o'clock it jumps to nine point four, and it stays between nine point two and nine point four until five. Now look at the other two pages. [PAUSE] The Reliability page says "No failed LLM attempts in this store." Not one failed call all day. Cost per hour: the afternoon bars look like any other afternoon. The whole day costs fifty-five eighty-six, slightly less than the baseline, not more.

[SCREEN: Latency page, "Generation detail": generation duration p95 about 2.8 s all morning, about 6.5 s from 13:00 to 17:00]

This is what a slow failure looks like. Nothing failed, so nothing retried and nothing fell back. The twenty-second timeout never fired, because a slow call here takes six or seven seconds, well under twenty. Every one of those slow calls just completed. Slowly. Two model calls per request, both slow, and the user waits nine seconds for an answer.

And the cost panel is the cruelest part. Finance would never know. The bill for a terrible afternoon is the same as for a good one.

[SLIDE 2: The diagnosis, from three charts]
- p95 9.2 to 9.4 s from 13:00 to 17:00; 3.8 s outside
- Generation TTFT p95 about 650 ms → about 2,250 ms in the window (Latency page, generation detail)
- LLM retries: zero. Fallbacks: zero. Errors: zero
- Cost per hour: unchanged
- Red latency with nothing else moving means: the provider is slow, and nothing is turning slowness into an error

[AVATAR]

Read the three charts together. Latency red. Retries flat. Cost flat. The generation detail on the Latency page shows each call's first token going from about two thirds of a second to over two seconds. [PAUSE] That combination, red latency with nothing else moving, has exactly one meaning: the provider is slow, and nothing in your stack is turning slowness into an error. The fallback list from 7.4 is fine. It never fired, because fallbacks fire on errors.

So what can you change? Start with what you control. Fewer tokens per call means less to stream.

[SCREEN: terminal, then the Latency page for the new store]

```bash
OFFLINE=1 make replay SCENARIO=slow_provider DIET=1 STORE=.atlas/slow_diet.sqlite            # context diet on
OFFLINE=1 make replay SCENARIO=slow_provider DIET=1 ROUTER=1 STORE=.atlas/slow_dr.sqlite       # + small-model routing
```

[DEMO: both summaries end `p95 latency 8404 ms`. The hourly p95 in the window drops from about 9.3 s to about 8.8 s with the diet; routing doesn't move it, because the slowest requests are policy questions that stay on gpt-4.1-mini. The diet run costs $41.68 for the day, diet plus routing $33.70.]

[AVATAR]

The diet takes the afternoon from nine point three to eight point eight. Routing moves the cost, not the p95, because the slowest requests are long policy answers that stay on the mid-size model. [PAUSE] Half a second. That's what your own levers buy when the provider is slow everywhere: milliseconds, not seconds. Worth having, and nowhere near four seconds.

[SLIDE 3: What actually fixes a slow provider]
- A timeout that turns a stall into an error: `ATLAS_REQUEST_TIMEOUT_S`, about 2× the slowest normal call (7.3)
- The error opens the breaker; the next calls go to `FALLBACKS[model]` (7.4)
- The fallback must be somewhere the slowness isn't: another model family or another provider
- Offline, the mock slows every model and never times out, so this half is proven by tests, not by the replay
- Against a real provider: `.env.chaos.example` (`ATLAS_REQUEST_TIMEOUT_S=4`, `ATLAS_MAX_RETRIES=1`, `ATLAS_ROUTER_MODE=1`, `OFFLINE=0`)

[AVATAR]

The fix that buys seconds has two halves. First, a timeout tight enough to turn a stalled call into an error: around twice the slowest normal call, not twenty seconds. Second, somewhere else to send the step once the breaker opens, and it has to be somewhere the slowness isn't: another model family, or better, another provider. [PAUSE] Here's the honest part. In this replay the whole provider is slow, every model, and the offline mock never times out a call. So the replay can't show the second half. You saw it work in 7.4, with the stalling provider: three timeouts, breaker open, every following request answered by the fallback. Against a real provider, `.env.chaos.example` has the settings, and the lab walks you through them.

[SCREEN: terminal, `uv run pytest tests/unit/test_agent.py -q -k "slow_provider or fallback"`: `2 passed`]

Two tests pin the mechanism offline: the slow-provider scenario really makes a request slower, and once the breaker is open the next call goes to the fallback.

[SLIDE 4: What we did not change, and why]
- The fallback list: right already, it just needs an error to fire
- Concurrency limits (7.5): a slow provider fills slots; watch `atlas_queue_wait_seconds` live (Section 9), not in a replay
- Budget guard: never triggered; the day cost the same
- The prompt and the tools: untouched; this was never Atlas's bug

[AVATAR]

And what we didn't touch. The fallback list, which is right; it just needs an error. The concurrency limits: a slow provider holds every slot longer, so on a live server `atlas_queue_wait_seconds` and the shed counter climb, which you'll watch in Grafana in Section 9; a replay has no server and no queue. The budget guard, which never fired, because the day cost the same. The prompt and the tools. [PAUSE] One more run for you to try in the lab: a timeout that's too tight. On a real provider, set it below your slowest normal call, and healthy answers start timing out and falling back, cost goes up and p95 barely moves. Too tight is its own incident. The lab is about finding the number in between.

[SLIDE 5: Recap]
- Slow provider: p95 red, everything else flat
- Your levers buy milliseconds, not seconds
- Seconds need a timeout and a second provider

### Recap

A slow provider is a silent incident: p95 goes to 9.4 seconds while retries, fallbacks and cost stay flat; the context diet buys half a second, and only a timeout that turns stalls into errors, plus a fallback somewhere the slowness isn't, gets you back under four.

### Transition

Your turn. Lab 4 hands you the same scenario and asks you to bring p95 back toward four seconds, with every changed setting justified from the worksheet.

### Speaker notes: common mistakes and Q&A

- **"Why not just fall back on latency?"** Fallbacks fire on errors and timeouts. A timeout is how you turn latency into an error. That's the insight of the whole demo.
- **Latency-based routing.** It helps between two deployments of the same model but reacts over minutes; a timeout reacts in seconds. Use both.
- **"Why doesn't the replay show the tuned run?"** The mock draws a simulated latency and returns it; it has no wall clock to time out and it slows every model in the scenario. Say it on camera; `.env.chaos.example` says the same in its header.
- **The 20 s default.** `ATLAS_REQUEST_TIMEOUT_S=20` is generous on purpose so a first install never times out. Production sets it from the worksheet.
- **Recording.** Three pages, same time axis, p95 with the red budget line. Annotate 13:00 and 17:00.

---

## Lecture 7.7: Lab 4: Hold p95 under 4 seconds during chaos

| Field | Value |
|---|---|
| ID | 7.7 |
| Title | Lab 4: Hold p95 under 4 seconds during chaos |
| Type | LAB (guided lab; short video intro, work off-video) |
| Target duration | Video 3:00 (about 290 spoken words at ~140 wpm, plus slide time); lab work about 75 minutes |
| One idea | Reproduce the slow-provider day, tune timeouts, retries, fallbacks and concurrency with every change justified from the worksheet, and prove the result with the budget gate and a before/after table. |
| Prerequisites | 7.1 to 7.6 |
| Files used | `04-labs/lab-04-latency-chaos.md`, `.env.chaos.example`, `src/northwind/config.py`, `tests/budget/test_budget_gate.py`, `simulator/scenarios.py` |

**Learning objectives**

1. Run the `slow_provider` scenario and read the three charts from 7.6.
2. Tune `ATLAS_REQUEST_TIMEOUT_S`, `ATLAS_MAX_RETRIES`, `ATLAS_ROUTER_ALLOWED_FAILS`, `ATLAS_ROUTER_COOLDOWN_S` and `ATLAS_TENANT_MAX_INFLIGHT`, and check each change against the budget gate.
3. Justify every changed setting with a row from the latency budget worksheet.

### Script

[AVATAR]

Lab four. Same scenario as the demo, and this time you hold the controls. [PAUSE] Your job is to bring p95 back under the four-second budget, and to write one line for every setting you changed saying which worksheet row justifies it.

[SCREEN: `04-labs/lab-04-latency-chaos.md`, the checklist; then `03-code/.env.chaos.example`]

You start by reproducing the incident: `make replay SCENARIO=slow_provider`, then the budget gate with the same incident, `BUDGET_GATE_INCIDENTS=slow_provider make budget-check`. It fails on p95, as it should. Then you copy `.env.chaos.example` to `.env.chaos` and tune: the per-call timeout, the retry bound, the Router's `allowed_fails` and cooldown, and the per-tenant concurrency slots.

[SLIDE 1: Lab 4 checklist]
- Replay `slow_provider`; screenshot the three charts; gate red on p95
- Tune `.env.chaos`; re-run; record p95, cost per session and outcomes after each change
- Fill the worksheet row for each changed setting in `notes/lab-04.md`
- Keep cost per session under $0.05 the whole time
- Submit: the screenshots, the `.env.chaos` diff, the before/after table

[AVATAR]

Two hints. First, look at the retries and fallback panels before you touch anything; if they're at zero, the fix starts with a timeout, not a fallback. Second, remember what 7.6 showed: offline, the mock slows every model and never times out a call, so the replay shows the problem and the context diet's half second, and the timeout-and-fallback half needs a real provider or the stalling provider from 7.4. The lab tells you which steps run where, and if you have keys, how to set a spending cap before you run anything against the real API.

[SLIDE 2: You can now]
- Budget latency at p95 and measure it from spans
- Bound retries and price every failed attempt
- Contain a failing model with breakers, fallbacks and per-tenant queues

### Recap

Lab 4 reproduces the slow-provider day and asks you to tune the reliability settings toward the four-second budget, with every change justified from the worksheet and measured on cost as well as latency.

### Transition

Before the lab, the Section 7 quiz.

### Speaker notes: common mistakes and Q&A

- **Retries on during a slowdown.** More retries only add waiting when nothing errors; when the timeout does fire, every retry is billed. Point students at the 7.3 table.
- **Timeout too tight.** Below the slowest normal call, healthy answers time out and fall back; cost rises and p95 barely moves.
- **Skipping the worksheet.** Grade it. The setting without a justification is the one that breaks next quarter.
- **Gate store.** `make budget-check` writes `.atlas/budget-gate.sqlite`; `BUDGET_GATE_STORE` moves it if two runs share a machine.

---

## Lecture 7.8: Quiz: Latency and reliability

| Field | Value |
|---|---|
| ID | 7.8 |
| Title | Quiz: Latency and reliability |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 120 spoken words at ~140 wpm, plus slide time) |
| One idea | Check you can pick the right percentile, the right timeout and the right control for each failure shape. |
| Prerequisites | 7.1 to 7.6 |
| Files used | `06-assessments/quizzes/section-07.md` (6 questions) |

**Learning objectives**

1. Read a latency table and choose the budget number.
2. Match blip, slow provider, outage and burst to retry, timeout, fallback and shedding.

### Script

[AVATAR]

Six questions. You'll compute a p95 from a short list, the way `percentile` does it, with linear interpolation. You'll be given a provider's normal call times and asked for a sensible per-call timeout. You'll match four failure shapes, a blip, a slow provider, an outage and a burst, to the control that handles each. And you'll spot the one setting in a Router config that makes a slow provider invisible.

[SLIDE 1: Quiz: 6 questions]
- Percentiles and budgets
- Timeouts from p95
- Failure shape → control
- Reading a Router config

[AVATAR]

One tip: whenever a question shows you a chart with flat errors and rising latency, the answer involves a timeout, because nothing falls back until something errors.

### Recap

The quiz checks that you can budget in percentiles and choose the right reliability control for each failure shape.

### Transition

Atlas is fast and it stays up. Next section: is it any good? Online evaluation, feedback and drift on live traffic.

### Speaker notes: common mistakes and Q&A

- Most-missed: "p95 of [1, 2, 2, 3, 3, 3, 4, 5, 9, 12]" the way `northwind.latency.percentile` computes it. Answer: k = 9 × 0.95 = 8.55, so 9 + 0.55 × (12 − 9) = 10.65. Nearest rank would give 12; check which definition the quiz file uses before recording.
- Second: students pick "add a fallback" for the slow-provider chart; the answer is "tighten the per-call timeout so the fallback can fire".
