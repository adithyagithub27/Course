# Section 7: Latency and Reliability

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 50 minutes (8 lectures, including one chaos demo, one lab intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics (tenants `operations`, `warehouse`, `finance`, `sales`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Latency charts: one metric per chart, p95 annotated with a callout, budget line drawn in red.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on litellm 1.103 / langfuse 4.15 / opentelemetry-semantic-conventions 0.66b0 (GenAI attributes are incubating; names may change)."
> **Companion course tie-in:** Lecture 7.1 links once to *Production Voice AI Agents* for the 800 ms voice budget. Never require it.

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.latency` (`percentile`, `StepTiming`, `RequestTiming`, `LatencyBudget`, `violations`), `app.agent.AtlasAgent` (`mode="router"`, `build_router`, `_choose_deployment`), `telemetry.metrics` (`FIRST_TOKEN_SECONDS`, `REQUEST_SECONDS`, `STEP_SECONDS`, `TOOL_ERRORS`, `FALLBACKS`, `RETRIES`, `SHED`), `simulator/scenarios.py` (`slow_provider`, `retry_storm`), `tests/budget/test_budget_gate.py`. On screen, all of this is "Atlas".

**The numbers card (one set of figures for the section):**

| Item | Value |
|---|---|
| Model timing (gpt-4.1-mini, observed, illustrative) | time to first token p50 0.55 s, p95 1.1 s; about 9 ms per output token (about 110 tokens/s) |
| gpt-4.1 | first token p50 0.9 s; about 18 ms per output token |
| Atlas normal day, user-facing first token | p50 1.9 s, p95 3.4 s, p99 5.6 s |
| Atlas normal day, full answer | p50 3.6 s, p95 6.8 s, p99 11.0 s |
| Budget | first visible token ≤ 4.0 s at p95; full answer ≤ 8.0 s at p95; each tool step ≤ 1.2 s at p95 |
| `slow_provider` (12:00 to 12:45, 35% of calls get first token 4 to 6 s) | untuned: about 72% of requests over the 4 s budget, first-token p95 11.2 s, 0 fallbacks, +$0.00 · tuned: 4.6% over budget, p95 3.8 s, 18% of requests fell back one step, about +$1.20 for the window |
| `retry_storm` (one tool failing, unbounded retries) | +$7.10 in two hours on one tenant (baseline prices); bounded to 2 retries: +$1.10 |

---

## Lecture 7.1: Latency budgets for agents

| Field | Value |
|---|---|
| ID | 7.1 |
| Title | Latency budgets for agents |
| Type | SL (slides + avatar) |
| Target duration | 7:00 (about 730 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Write a latency budget per step and end to end, measure it at p95, and treat the budget as a contract the rest of the section enforces. |
| Prerequisites | Section 5 (streaming, TTFT and TPOT from spans) |
| Files used | `10-resources/latency-budget-worksheet.md` |

**Learning objectives**

1. Distinguish time to first token, time per output token and total time, and pick the one users feel.
2. Explain why averages hide the pain and why p95 is the planning number.
3. Fill in the latency budget worksheet for Atlas: per step, end to end, and the headroom left for chaos.

### Script

[B-ROLL: Ops Console latency page. Top: a single stat tile, "mean latency today: 2.3 s", green. Underneath: the p95 line by five-minute window: 3.4 s most of the day, then a spike to 11 s between 12:00 and 12:45, red.]

[AVATAR]

Two numbers, same day, same requests. The top one is the daily average. Two point three seconds. Boring. Nobody would look twice. The bottom one is the ninety-fifth percentile, by five-minute window. [PAUSE] From noon to quarter to one, one in four users waited more than eight seconds for Atlas to say anything, and one in twenty waited eleven. Nearly three hundred people. The average moved by four tenths of a second and nobody noticed. That's why averages lie, and why this section measures in percentiles.

[SLIDE 1: Three clocks]
- Time to first token (TTFT): from send to the first streamed token. What users feel as "is it alive?"
- Time per output token (TPOT): the streaming speed. What users feel as "is it fast?"
- Total time: the whole thing. What your logs record by default.
- Agents have a fourth: time to first *visible* token, after all the tool steps

[AVATAR]

Three clocks, and for agents a fourth. Time to first token is how long the model takes to start. Time per output token is how fast it streams once started. Total time is the whole answer. And for an agent, the one users actually feel is the fourth: time to first visible token. Atlas runs two tool steps before the user sees a single word. The first two model calls stream nothing to the screen. So the user's clock starts at send and stops when the final answer begins. [PAUSE] Measure that one. It's the one that makes people close the tab.

[SLIDE 2: Where the time goes in one Atlas request (p50, normal day)]

| Step | What happens | p50 |
|---|---|---|
| 1 | model → tool call (`search_knowledge_base`) | 0.55 s first token + 0.15 s for 60 tokens + 0.20 s tool = 0.90 s |
| 2 | model → tool call (`lookup_ticket`) | 0.55 + 0.15 + 0.10 tool = 0.80 s |
| 3 | model → answer, first token | 0.55 s, plus 0.10 s of overhead = 0.65 s |
| User sees the first word | | **≈ 1.9 s** (p95: 3.4 s) |
| 3 | streaming 220 tokens at 9 ms | + 2.0 s |
| Full answer | | **≈ 3.6 s** (p95: 6.8 s) |

[AVATAR]

Here's the anatomy. Three model calls at about half a second each to first token. Two tool executions, a couple of hundred milliseconds. Two tool-call outputs of sixty tokens each, streamed at nine milliseconds a token. The user sees the first word of the answer at about one point nine seconds on a median request, and three point four at p95. The full answer lands at three point six seconds, six point eight at p95, because two hundred twenty tokens at nine milliseconds is two seconds of streaming.

Notice where the time is. [PAUSE] Not in the tools. In waiting for the model to start, three times. Every step you add is another half second before the user sees anything. That's the cost lesson from Section 6 in a different currency.

[SLIDE 3: The budget (Atlas, from the worksheet)]
- First visible token: ≤ 4.0 s at p95 (users start re-typing at about 5 s)
- Full answer: ≤ 8.0 s at p95
- Each tool step: ≤ 1.2 s at p95 (model 1.1 s p95 alone; tools must be fast)
- Headroom at p95 today: 0.6 s on first token, 1.2 s on full answer
- Voice agents (Course 3) budget 800 ms end to end; a chat helpdesk gets 4 s; know which you are

[AVATAR]

Now the budget. Four seconds to the first visible token, at p95. Eight seconds to the full answer. One point two seconds per tool step. Where do those come from? From users. In our replay's feedback data, re-typing and abandonment start climbing at about five seconds of silence. Four gives us a margin. [PAUSE] And the headroom today is six tenths of a second at p95. That's the number that matters for the chaos demo in 7.6. When a provider gets slow, six tenths of a second is what we have before we're outside the contract.

If you've taken the voice agents course, you'll remember eight hundred milliseconds end to end. A voice agent has to answer before the silence gets awkward. A chat helpdesk gets five times that. Same discipline, different number. Know which product you are.

[SLIDE 4: Why p95 and not p99 or the mean]
- Mean: hides everything; one slow provider minute vanishes into 10,000 requests
- p50: what the typical user gets; fine for capacity, useless for pain
- p95: one in twenty; the number an engineering team can actually hold
- p99: one in a hundred; watch it, alert on trend, don't budget on it for an LLM app
- Budget at p95, alert on p95 and p99 slope, report p50 alongside

[AVATAR]

Why p95, specifically? The mean hides everything, you've seen that. p50 is what the typical person gets; useful for capacity, useless for pain. p99 is one in a hundred, and with a third-party model provider in the loop, you don't control the tail well enough to promise it. p95 is the one an engineering team can actually hold: one in twenty. We budget at p95, we watch p99 for trend, and we report p50 next to it so nobody thinks the typical experience is slow.

[SLIDE 5: The budget worksheet]
- `10-resources/latency-budget-worksheet.md`
- Rows: each step, each tool, each model call; columns: p50, p95, budget, headroom
- Fill it from spans, not from guesses (7.2)
- Every reliability control in 7.3 to 7.5 is justified by a row in this sheet

[AVATAR]

The worksheet is in the resources folder. One row per step, per tool, per model call. Columns for p50, p95, the budget and the headroom. You'll fill it from spans in the next lecture, not from guesses. And every timeout, retry and fallback we add in this section will point back to a row. A timeout you can't justify from the sheet is a timeout that will bite you on a busy day.

[AVATAR]

One more thing before we measure. [PAUSE] Latency and cost pull in opposite directions in one place: retries. A retry is the fastest way to fix a slow call and the fastest way to double your bill. Hold both numbers in your head through this section. In 7.3 we'll make retries bounded, so they cost you a known amount of both.

### Recap

Agents have a fourth clock, time to first visible token; budget it at p95, four seconds for Atlas, with per-step budgets underneath, and fill the budget from spans.

### Transition

Next, the code: aggregate TTFT, TPOT and total time from the span store, expose them as Prometheus histograms, and light up the latency page of the Ops Console.

### Speaker notes: common mistakes and Q&A

- **Measuring total time only.** Most frameworks log total duration. Users feel first visible token. Both matter; budget both.
- **Budgeting the mean.** If a student's worksheet has a mean column, send them back to the chart from the hook.
- **"Just use a faster model."** Model TTFT is half the story; the number of steps is the other half. Fewer steps beat a faster model.
- **Voice comparison.** The 800 ms figure comes from Course 3's latency section. One sentence, then move on.
- **Numbers on screen are observed on one day and illustrative.** Provider latency changes; the method doesn't.

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
| Files used | `src/northwind/latency.py`, `telemetry/metrics.py`, `telemetry/local_store.py`, `console/ops_console.py`, `tests/unit/test_latency.py` |

**Learning objectives**

1. Compute TTFT, TPOT and total time for a generation from span start, first-chunk time, end time and output tokens.
2. Implement `percentile(values, p)` with nearest-rank and use it for p50, p95 and p99 per step and per request.
3. Record `FIRST_TOKEN_SECONDS` and `REQUEST_SECONDS` histograms with buckets that bracket the budget, and labels for feature only.

### Script

[AVATAR]

You already have the data. Every generation span in Atlas carries a start time, an end time, the moment the first chunk arrived, and the output token count. [PAUSE] That's four numbers, and from four numbers you get all three clocks. No new instrumentation today. Just arithmetic and a histogram.

[SLIDE 1: From span to clocks]
- TTFT = `first_chunk_at − start`
- TPOT = `(end − first_chunk_at) / max(output_tokens − 1, 1)`
- Total = `end − start`
- Request first visible token = final generation's `first_chunk_at − request start`
- Attributes: `gen_ai.response.time_to_first_chunk` (incubating), Langfuse `completion_start_time`

[AVATAR]

Time to first token is first chunk minus start. Time per output token is the rest of the streaming window divided by the tokens in it. Total is end minus start. And the agent's fourth clock is the final generation's first chunk minus the start of the whole request. All four come from attributes you set in lecture 5.4: the incubating `gen_ai.response.time_to_first_chunk` on the OTel side, and `completion_start_time` in Langfuse.

[SCREEN: VS Code, `src/northwind/latency.py`]

[CODE: `src/northwind/latency.py` (excerpt)]

```python
from dataclasses import dataclass
import math


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile, no numpy. p in [0, 100]."""
    if not values:
        return math.nan
    xs = sorted(values)
    k = max(1, math.ceil(p / 100 * len(xs)))
    return xs[k - 1]


@dataclass(frozen=True)
class StepTiming:
    step: int
    start: float
    first_chunk_at: float | None
    end: float
    output_tokens: int
    tool_seconds: float = 0.0

    @property
    def ttft(self) -> float:
        return (self.first_chunk_at or self.end) - self.start

    @property
    def tpot(self) -> float:
        if not self.first_chunk_at or self.output_tokens < 2:
            return 0.0
        return (self.end - self.first_chunk_at) / (self.output_tokens - 1)

    @property
    def total(self) -> float:
        return self.end - self.start + self.tool_seconds


@dataclass(frozen=True)
class RequestTiming:
    steps: list[StepTiming]

    @property
    def first_visible_token(self) -> float:
        final = self.steps[-1]
        return (final.first_chunk_at or final.end) - self.steps[0].start

    @property
    def total(self) -> float:
        return self.steps[-1].end - self.steps[0].start


@dataclass(frozen=True)
class LatencyBudget:
    first_visible_p95_s: float = 4.0
    total_p95_s: float = 8.0
    step_p95_s: float = 1.2


def violations(requests: list[RequestTiming], budget: LatencyBudget) -> dict[str, float]:
    fv = percentile([r.first_visible_token for r in requests], 95)
    tot = percentile([r.total for r in requests], 95)
    step = percentile([s.total for r in requests for s in r.steps[:-1]], 95)
    return {k: v for k, v in {
        "first_visible_p95": fv if fv > budget.first_visible_p95_s else None,
        "total_p95": tot if tot > budget.total_p95_s else None,
        "step_p95": step if step > budget.step_p95_s else None,
    }.items() if v is not None}
```

Four pieces. `percentile` is nearest-rank: sort, take the element at the ceiling of p percent of the length. No numpy, because this runs in the CI gate and in the browser coding exercise. `StepTiming` is one generation plus the tool time that followed it; the three clocks are properties. `RequestTiming` gives the agent's fourth clock: the final step's first chunk minus the first step's start. And `violations` compares p95s to the budget and returns only what's over. [PAUSE] Empty dict means green. That's what the CI gate in Section 13 asserts.

Now the source: the local span store.

[SCREEN: `telemetry/local_store.py`, then terminal]

```bash
OFFLINE=1 make replay
uv run python -m northwind.latency --day 2026-09-22
```

[DEMO: output:]

```
requests: 10000
first visible token   p50 1.90s  p95 3.41s  p99 5.62s   budget p95 4.00s  OK  (headroom 0.59s)
full answer           p50 3.58s  p95 6.79s  p99 10.97s  budget p95 8.00s  OK
tool steps            p50 0.86s  p95 1.14s  p99 1.71s   budget p95 1.20s  OK
by step  1: ttft p50 0.55 p95 1.08 | 2: ttft p50 0.54 p95 1.10 | 3: ttft p50 0.56 p95 1.12 tpot p50 9.1ms
by tool  search_knowledge_base p95 0.31s | lookup_ticket p95 0.14s | check_shipment p95 0.62s
```

A word on where these numbers come from in offline mode. The mock LLM doesn't sleep for two seconds per call; it stamps spans with timings drawn from a distribution fitted to real gpt-4.1-mini calls, so a full day replays in a couple of minutes and the percentiles come out realistic. In live mode the same code reads real spans. Either way, the aggregation reads our local store rather than the Langfuse API, because ten thousand traces through a paginated API is slow and Langfuse already shows its own latency views in the UI for browsing. The store is for arithmetic. The UI is for looking.

There's the worksheet, filled from spans. First visible token p95 three point four one, budget four, fifty-nine hundredths of headroom. Every step's time to first token is just over a second at p95, which is why the step budget is one point two. And look at the tools: `check_shipment` is the slow one, six hundred milliseconds at p95, because it calls an external carrier API. Remember that for the chaos demo.

Now the metrics.

[SCREEN: `telemetry/metrics.py`]

[CODE: `telemetry/metrics.py` (excerpt)]

```python
from prometheus_client import Counter, Histogram

LATENCY_BUCKETS = (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 20.0)   # bracket the 4 s and 8 s budgets

FIRST_TOKEN_SECONDS = Histogram("atlas_first_token_seconds", "Time to first visible token per request",
                                ["feature"], buckets=LATENCY_BUCKETS)
REQUEST_SECONDS = Histogram("atlas_request_seconds", "Full answer time per request",
                            ["feature"], buckets=LATENCY_BUCKETS)
STEP_SECONDS = Histogram("atlas_step_seconds", "Model call + tool time per step",
                         ["model"], buckets=(0.25, 0.5, 0.75, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0))
TOOL_CALLS = Counter("atlas_tool_calls_total", "Tool invocations", ["tool"])
TOOL_ERRORS = Counter("atlas_tool_errors_total", "Tool invocations that raised", ["tool"])
```

Two rules in this file. First, the buckets bracket the budget: there's a bucket edge at exactly four seconds and at eight, so `histogram_quantile` can answer "what fraction was under budget" precisely, not by interpolation. Second, labels: `feature` and `model`, nothing else. Never tenant on a latency histogram, and never user. Four tenants times five features times eleven buckets is fine; four thousand users is not. [PAUSE] Tenant latency lives in the span store, where cardinality is free.

[SCREEN: `app/agent.py`, one line: `FIRST_TOKEN_SECONDS.labels(feature=ctx.feature).observe(timing.first_visible_token)`; then the Ops Console latency page]

One `observe` call at the end of the request, and the Ops Console latency page lights up: p50, p95, p99 lines, the four-second budget in red, per-step breakdown, per-tool p95. Same functions, same numbers as the terminal.

Two habits with histograms. Observe once per request, at the end, with the value you computed from spans; don't wrap the whole request in a timer and observe that, because then you've measured total time when the SLI is first visible token. And choose buckets before you have a month of data, because changing buckets later makes old and new data incomparable. Ours run from a quarter second to twenty, with edges at the two budgets. [PAUSE] If you ever find yourself wanting p99.9 from a histogram, stop: eleven buckets can't give you that, and neither can a provider you don't control.

[SCREEN: `tests/unit/test_latency.py`]

Three unit tests: `percentile` on a known list, `first_visible_token` on a three-step request, and `violations` returning empty on a within-budget set and non-empty when one step is slow.

### Recap

TTFT, TPOT and total time fall out of four span attributes; `percentile` is nearest-rank without numpy; histograms get bucket edges at the budget and labels for feature and model only.

### Transition

Now you can see where the time goes. Next, the controls that hold it: timeouts, bounded retries and backoff, done so they don't turn a slow minute into a cost incident.

### Speaker notes: common mistakes and Q&A

- **TPOT with one token.** Division by zero; the code returns 0 for fewer than two output tokens.
- **Missing `first_chunk_at`.** Non-streaming calls have none; `ttft` falls back to the end time and is then equal to total. Say it on screen.
- **Nearest-rank vs interpolated percentiles.** Prometheus interpolates within a bucket; our function doesn't. Small differences are expected. Bucket edges at the budget minimise them where it matters.
- **Coding exercise.** "Percentile latency" in `06-assessments/coding-exercises.md` is this `percentile` function, stdlib only.

---

## Lecture 7.3: Timeouts, retries and backoff done right

| Field | Value |
|---|---|
| ID | 7.3 |
| Title | Timeouts, retries and backoff done right |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 680 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Give every call a timeout derived from the budget, bound retries with jittered backoff, make tool calls idempotent, and count every retry as the cost event it is. |
| Prerequisites | 7.2; 6.7 (budget guard) |
| Files used | `app/agent.py`, `app/tools.py`, `src/northwind/config.py`, `telemetry/metrics.py`, `simulator/scenarios.py::retry_storm` |

**Learning objectives**

1. Set per-call timeouts (first token and total) from the latency budget and pass them to the Router.
2. Implement bounded retries with exponential backoff and full jitter, only for retryable errors, and never for a call that already streamed output.
3. Make `create_ticket` idempotent with a request key, and emit `RETRIES` so a retry storm is visible in Prometheus and in cost.

### Script

[B-ROLL: Ops Console. Operations tenant, 10:05. A tool error rate line jumps to 40%. Below it, the cost line for operations bends upward. Caption: `retry_storm`.]

[AVATAR]

Ten oh five on a Tuesday. The ticketing system starts returning errors for one tenant. Atlas does what version one was written to do: try again. And again. Five times per step, three steps per request, eight hundred thirty requests over two hours. [PAUSE] Seven dollars ten of extra model calls, on a tenant that spends five dollars in a normal two hours, and every one of those users still got an error. Retries didn't fix anything. They just paid for the failure five times.

[SLIDE 1: Three rules]
- Timeouts come from the budget, not from a default
- Retries are bounded, jittered, and only for errors that a retry can fix
- Every retry is a cost event: count it, and let the budget guard see it

[AVATAR]

Three rules. Timeouts derive from the budget you wrote in 7.1. Retries are bounded, jittered, and only for errors a retry can actually fix. And every retry is a cost event. It goes on a counter and into the budget guard's spend, so a storm hits the soft cap instead of the credit card.

[SLIDE 2: Timeouts from the budget]
- Step budget 1.2 s p95; model TTFT p95 1.1 s → first-token timeout 6 s (5× p95, catches a stalled provider, not a slow one)
- Total call timeout 25 s (a 220-token answer at 3× normal TPOT is 6 s; 25 leaves room for gpt-4.1)
- Stream idle timeout 5 s: no new chunk for 5 s means the stream is dead
- Tool timeouts per tool: `check_shipment` 3 s (p95 0.62 s), the rest 1 s
- The old default was 20 s flat and no first-token timeout: a stalled call ate the whole budget five times over

[AVATAR]

Timeouts. The step budget is one point two seconds at p95, and the model's first token is one point one at p95. So a first-token timeout of six seconds, about five times p95, catches a stalled provider without cutting off a merely slow one. Total call timeout, twenty-five seconds, generous because gpt-4.1 streams at half the speed. A stream idle timeout of five seconds: if no chunk arrives for five seconds, the stream is dead, stop waiting. And per-tool timeouts: three seconds for `check_shipment`, one for the rest. [PAUSE] Version one had a twenty-second flat timeout and nothing on first token. A stalled provider ate twenty seconds, then retried, five times. That's a hundred seconds before the user got an error.

[SCREEN: VS Code, `app/agent.py`]

[CODE: `app/agent.py` (excerpt): timeouts and bounded retries]

```python
RETRYABLE = (litellm.exceptions.Timeout, litellm.exceptions.RateLimitError,
             litellm.exceptions.APIConnectionError, litellm.exceptions.InternalServerError)


def _call_model(self, ctx: RequestContext, deployment: str, messages: list[dict]) -> ModelResult:
    attempt = 0
    while True:
        try:
            stream = self.router.completion(
                model=deployment, messages=messages, tools=self.tool_schemas, stream=True,
                timeout=self.cfg.llm_total_timeout_s,                 # 25 s
                prompt_cache_key=self._cache_key(ctx),
            )
            return self._consume(stream, first_token_timeout=self.cfg.llm_first_token_timeout_s,   # 6 s
                                 idle_timeout=self.cfg.llm_stream_idle_timeout_s)                 # 5 s
        except RETRYABLE as exc:
            if attempt >= self.cfg.llm_max_retries or getattr(exc, "streamed_tokens", 0) > 0:   # max 2; never retry a partial answer
                raise
            attempt += 1
            RETRIES.labels(kind="llm", reason=type(exc).__name__, tenant=ctx.tenant).inc()
            delay = random.uniform(0, min(self.cfg.retry_cap_s, self.cfg.retry_base_s * 2 ** attempt))  # full jitter: 0..min(8, 0.5*2^n)
            lf.update_current_span(level="WARNING", status_message=f"retry {attempt}: {type(exc).__name__} after {delay:.2f}s")
            time.sleep(delay)
```

Read the `except`. Four things happen. Only `RETRYABLE` errors get here: timeouts, rate limits, connection errors, server errors. A bad request or an auth error is raised immediately, because retrying it is pointless. Then the bound: two retries, and never if the call already streamed tokens to the user, because a retry would produce a second, different answer. Then the counter, with the reason and the tenant. Then full-jitter backoff: a random delay between zero and half a second times two to the attempt, capped at eight. [PAUSE] Jitter is not optional. Without it, a thousand clients that failed at the same instant retry at the same instant, and you've built a synchronised storm.

Now tools, which have their own retry problem.

[SCREEN: `app/tools.py`]

[CODE: `app/tools.py` (excerpt): idempotent ticket creation]

```python
def create_ticket(subject: str, body: str, priority: str = "normal", *, request_key: str) -> Ticket:
    """Idempotent: the same request_key always returns the same ticket, never a duplicate."""
    if (existing := ticket_store.by_request_key(request_key)) is not None:
        return existing
    with tool_timeout(seconds=1.0, tool="create_ticket"):
        return ticket_store.create(subject=subject, body=body, priority=priority, request_key=request_key)
```

`create_ticket` takes a `request_key`, which the agent derives from the trace id and the step number. Same key, same ticket. So if the tool timed out after the ticket was created but before the response arrived, the retry returns the existing ticket instead of opening a second one. [PAUSE] Without this, the retry storm from the hook also opened four thousand duplicate tickets. Reads like `lookup_ticket` are naturally idempotent. Writes need a key.

Tool retries follow the same shape: at most two, jittered, counted with `kind="tool"`, and a tool that fails twice sends the step to the strong model, which you saw in 6.6.

[SCREEN: terminal]

Replay the storm, before and after.

```bash
OFFLINE=1 make replay SCENARIO=retry_storm TENANT=operations          # v1 retry loop
OFFLINE=1 BOUNDED_RETRIES=1 make replay SCENARIO=retry_storm TENANT=operations
```

[SLIDE 3: The storm, before and after (two hours, operations, baseline prices)]

| | Unbounded retries (v1) | Bounded, jittered, idempotent |
|---|---|---|
| Extra generations | 4,150 | 640 |
| Extra cost | $7.10 | $1.10 |
| Duplicate tickets | 3,900 | 0 |
| p95 first visible token during storm | 41 s (timeouts stacked) | 4.9 s (fast fail after 2 tries, then escalation or honest error) |
| User outcome | error after ~100 s | error or strong-model answer within 5 s |

[AVATAR]

Same storm. Extra cost drops from seven dollars to one. Duplicate tickets from thirty-nine hundred to zero. And p95 during the storm drops from forty-one seconds, because five twenty-second timeouts stacked up, to under five. [PAUSE] The users still saw a broken ticketing system. That's not Atlas's fault. But they saw it in five seconds instead of a hundred, they didn't get four duplicate tickets, and the department wasn't billed seven dollars for the privilege.

[SLIDE 4: Retry checklist]
- Timeouts: first token, total, stream idle, per tool, all from the budget
- Retry only `RETRYABLE`; never after streamed output
- Max 2, full jitter, capped
- Writes take a request key
- `RETRIES` counter feeds the anomaly detector and the Section 9 alert

[AVATAR]

The checklist. Every timeout justified by a budget row. Retry only what can succeed, never a partial answer. Two attempts, jittered. Writes idempotent. And the counter, which is what turns a retry storm into a page instead of an invoice.

### Recap

Derive first-token, total, idle and per-tool timeouts from the budget, bound retries to two with full jitter and only for retryable errors, give writes a request key, and count every retry as a cost event.

### Transition

Retries help when the failure is brief. When a whole model or provider goes slow for an hour, you need somewhere else to send the traffic. Next: fallbacks and circuit breakers with the Router.

### Speaker notes: common mistakes and Q&A

- **Retrying after partial output.** The classic double-answer bug. The `streamed_tokens` check is the guard; explain it slowly.
- **`num_retries` on the Router and our own loop.** Choose one. The code sets `num_retries=0` on the Router when the agent manages retries, or drops the loop and uses the Router's. Say which you're demoing; the repo uses the agent loop for visibility.
- **Idempotency keys from timestamps.** Time changes between attempts. Use trace id plus step.
- **Exponential backoff without a cap.** Attempt 6 waits 32 s. The cap is 8 s; with max 2 retries it never matters, but keep it.
- **Verify exception class names** on the installed litellm before recording.

---

## Lecture 7.4: Fallbacks and circuit breakers with the Router

| Field | Value |
|---|---|
| ID | 7.4 |
| Title | Fallbacks and circuit breakers with the Router |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 650 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Configure model and provider fallback lists with cooldowns in the LiteLLM Router so a slow or failing deployment is bypassed automatically, and log every fallback with a reason so you can see what it cost. |
| Prerequisites | 7.3; 6.6 (Router setup) |
| Files used | `app/agent.py`, `src/northwind/config.py`, `telemetry/metrics.py` |

**Learning objectives**

1. Extend the Router with `fallbacks`, `context_window_fallbacks`, `allowed_fails`, `cooldown_time` and `retry_after`, and explain each as a circuit-breaker term (closed, open, half-open).
2. Add a second provider deployment for the same logical model and order the fallback list by latency and cost.
3. Log a fallback on the span and in `FALLBACKS{from_model,to_model,reason}`, and read the cost of fallbacks from the showback.

### Script

[AVATAR]

A retry says: try the same thing again. A fallback says: try something else. [PAUSE] When gpt-4.1-mini's first token goes from half a second to five seconds for forty-five minutes, retrying it is just waiting twice. Sending the step to another deployment is what gets the user an answer. The Router does this for us, and a circuit breaker stops us from hammering the slow one while it recovers.

[SLIDE 1: Circuit breaker in three states]
- Closed: traffic flows to the deployment; failures are counted
- Open: after `allowed_fails` failures within a minute, the deployment is cooled down for `cooldown_time` seconds; traffic goes to the fallback
- Half-open: after the cooldown, one request probes; success closes the circuit, failure re-opens it
- LiteLLM Router: `allowed_fails=3`, `cooldown_time=30`; timeouts count as failures

[AVATAR]

Three states. Closed is normal: requests flow, failures get counted. Open: after three failures in a minute, the Router puts that deployment in a thirty-second cooldown and sends everything to the fallback. Half-open: when the cooldown ends, the next request probes the deployment. Success closes the circuit. Another failure re-opens it. In the Router those are `allowed_fails` and `cooldown_time`, and a timeout counts as a failure, which is exactly what we want for a slow provider.

[SCREEN: VS Code, `app/agent.py`, `build_router`]

[CODE: `app/agent.py` (excerpt): fallback lists]

```python
def build_router(cfg: Settings) -> Router:
    return Router(
        model_list=[
            {"model_name": "atlas-default",
             "litellm_params": {"model": "gpt-4.1-mini", "api_key": cfg.openai_api_key}},
            {"model_name": "atlas-default",                      # same logical name, second provider
             "litellm_params": {"model": "azure/gpt-4.1-mini", "api_base": cfg.azure_base,
                                "api_key": cfg.azure_api_key, "api_version": cfg.azure_api_version}},
            {"model_name": "atlas-strong",
             "litellm_params": {"model": "gpt-4.1", "api_key": cfg.openai_api_key}},
            {"model_name": "atlas-fast",
             "litellm_params": {"model": "gpt-5-mini", "api_key": cfg.openai_api_key}},
        ],
        fallbacks=[
            {"atlas-default": ["atlas-fast", "atlas-strong"]},   # cheapest viable first, strongest last
            {"atlas-strong": ["atlas-default"]},                 # if the strong model is down, answer anyway
        ],
        context_window_fallbacks=[{"atlas-default": ["atlas-strong"]}],
        num_retries=0,                # the agent loop owns retries (7.3)
        timeout=cfg.llm_total_timeout_s,
        allowed_fails=3,
        cooldown_time=30,
        retry_after=1,
        routing_strategy="latency-based-routing",
    )
```

Four deployments, three logical names. `atlas-default` appears twice: once on OpenAI, once on Azure, same model. When two deployments share a name, the Router load-balances between them, and with `routing_strategy="latency-based-routing"` it prefers the one that has been faster recently. That's the provider fallback, and it's automatic.

Then the model fallback lists. If `atlas-default` fails, try `atlas-fast`, a different small model, then `atlas-strong`. Cheapest viable first, strongest last, because a fallback step on gpt-4.1 costs a cent. If `atlas-strong` fails, fall back down to `atlas-default`, because a slightly weaker answer beats no answer. And `context_window_fallbacks`: if a prompt is too long for the default, send it up rather than error. [PAUSE] `num_retries` is zero here, because the agent loop from 7.3 owns retries and we want one place to count them.

One thing the Router does not tell you by default: that a fallback happened. We need that on the span and on a counter.

[CODE: `app/agent.py` (excerpt): logging fallbacks]

```python
result = self._call_model(ctx, deployment, messages)
served = result.response.model                                     # the model that actually answered
requested = self.router.get_model_list(model_name=deployment)[0]["litellm_params"]["model"]
if served.split("/")[-1] != requested.split("/")[-1]:
    reason = result.fallback_reason or "router_fallback"          # Timeout | RateLimitError | cooldown | ...
    FALLBACKS.labels(from_model=requested, to_model=served, reason=reason).inc()
    lf.update_current_generation(model=served, level="WARNING", status_message=f"fallback: {requested} -> {served} ({reason})",
                                 metadata={"fallback": True, "fallback_reason": reason, "requested_model": requested})
```

After each call, compare the model that answered with the model we asked for. If they differ, a fallback fired. Count it with from, to and reason, and mark the generation as a warning with the requested model in the metadata. [PAUSE] Two things this buys you. Cost attribution stays honest: the generation is priced on the model that answered. And the fallback rate becomes a time series, which is the first thing you look at in the chaos demo.

[SLIDE 2: What to log when a fallback fires]
- On the generation: served model (for cost), requested model, reason, `level="WARNING"`
- Counter: `atlas_llm_fallbacks_total{from_model,to_model,reason}`
- Not on the span: the full error body (size and PII); put it in the structured log with the trace id
- A fallback is not an error to the user; it's a warning to you

[AVATAR]

Log the served model, the requested model and the reason. Keep the error body in the structured log, not the span, because error bodies are big and sometimes contain the prompt. And notice the level: warning. A fallback is a success for the user and a warning for you. If you log it as an error, your error rate lies during every provider hiccup.

[SLIDE 3: The cost of resilience (from the showback, `by model`)]
- Normal day: fallbacks 0.3% of steps, about $0.40 (mostly rate-limit blips at peak)
- 45-minute slow provider (7.6, tuned): 18% of requests fall back one step; about 110 of them land on gpt-4.1: about $1.20
- Cheaper than the alternative: 200 users waiting 11 seconds and re-typing
- Read fallback cost weekly; a rising baseline means a provider is degrading

[AVATAR]

Resilience has a price, and you can read it in the showback by model. On a normal day, fallbacks are a third of a percent of steps, forty cents, mostly rate-limit blips at lunchtime. During a slow-provider window, tuned the way we'll do in 7.6, eighteen percent of requests fall back one step, about a hundred ten of them to gpt-4.1: a dollar twenty. [PAUSE] A dollar twenty to keep two hundred users under four seconds. That's the cheapest reliability you'll ever buy. And watch the weekly number: a fallback baseline that creeps up is a provider quietly degrading before it has an incident.

[SCREEN: terminal, `uv run pytest tests/integration/test_router_fallback.py -q`]

[DEMO: 4 passed. Tests use the mock LLM with a scripted `Timeout` on the first deployment and assert: served model differs, `FALLBACKS` incremented once, generation level WARNING, cost computed on the served model.]

Four integration tests, offline, using the mock LLM with a scripted timeout. They assert the served model, the counter, the warning level, and that the cost was computed on the model that actually answered.

### Recap

Give the Router a second provider under the same name, ordered model fallbacks from cheapest viable to strongest, and `allowed_fails` plus `cooldown_time` as the circuit breaker; log every fallback as a warning with the served model, and read its cost in the showback.

### Transition

Fallbacks handle a slow model. Next, the provider says no: rate limits, per-tenant queues, and how to degrade gracefully instead of failing loudly.

### Speaker notes: common mistakes and Q&A

- **Fallback to the same model on the same provider.** It fails the same way. Different provider or different model, never the same deployment.
- **Strongest model first in the list.** It works and costs 5× for the whole outage. Cheapest viable first.
- **Silent fallbacks.** The Router does not annotate spans. The served-vs-requested comparison is our code; without it, the trace says gpt-4.1-mini and the bill says gpt-4.1.
- **Cooldown too long.** 30 s means a 45-minute slowdown costs you many probes, which is fine. 30 minutes means you miss the recovery. Keep it short; the half-open probe is cheap.
- **Verify Router kwargs** on the installed litellm: `model_list`, `fallbacks`, `context_window_fallbacks`, `num_retries`, `timeout`, `allowed_fails`, `cooldown_time`, `retry_after`, `routing_strategy` all present on 1.103.

---

## Lecture 7.5: Rate limits, queues and graceful degradation

| Field | Value |
|---|---|
| ID | 7.5 |
| Title | Rate limits, queues and graceful degradation |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 610 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Treat 429s and queues as a capacity problem: honour `Retry-After`, cap concurrency per tenant, shed the least valuable traffic first, and tell users the truth in degraded mode. |
| Prerequisites | 7.4; 6.7 (economy mode) |
| Files used | Diagram "request path with per-tenant semaphores"; `app/server.py` (concept) |

**Learning objectives**

1. Handle HTTP 429 correctly: read `Retry-After`, back off, count it, and let the Router cool the deployment.
2. Design per-tenant concurrency limits so one department's burst can't starve the others.
3. Define a shedding order and a degraded-mode message that keeps trust.

### Script

[AVATAR]

Twelve thirty on the busiest day of the quarter. Operations opens a hundred sessions in a minute because a shipping system went down and everyone wants to know where their pallets are. The provider answers a third of Atlas's calls with 429: too many requests. [PAUSE] Here's the question. Who should wait? If your answer is "whoever came last," finance is about to lose its payroll question to a hundred pallet lookups.

[SLIDE 1: What a 429 is telling you]
- You are over a tokens-per-minute or requests-per-minute limit for this key or model
- It carries `Retry-After` (seconds); honour it, don't guess
- It is retryable, but retrying immediately makes it worse for everyone on the key
- Count it: `RETRIES{reason="RateLimitError"}`; the Router counts it toward `allowed_fails`
- Persistent 429s are a capacity signal: raise the limit, add a provider, or shed load

[AVATAR]

A 429 is the provider telling you you've exceeded a per-minute limit for tokens or requests. It usually carries a `Retry-After` header. Honour that number. Don't guess, and don't retry immediately, because everyone else on the same key is retrying too. Our retry loop from 7.3 handles it: bounded, jittered, counted, and the Router counts it toward the cooldown, so a rate-limited deployment gets bypassed. [PAUSE] But if 429s are persistent, that's not an error. It's capacity. And capacity has three answers: pay for more, add a second provider under the same name like we did in 7.4, or decide who waits.

[SLIDE 2: Per-tenant concurrency]
- One semaphore per tenant, sized from the showback share: operations 12, warehouse 10, finance 6, sales 4 (32 total)
- A tenant at its limit waits in its own queue, up to 3 s, then gets degraded mode
- No tenant can consume more than its share of the provider limit
- Metrics: `atlas_inflight{tenant}` gauge, `atlas_queue_wait_seconds{tenant}` histogram
- Diagram: requests → tenant semaphores → shared Router → provider

[B-ROLL: diagram builds. Four lanes labelled by tenant, each with a small number, merging into the Router, then a single pipe to the provider. Operations' lane fills to red; the other three stay green.]

[AVATAR]

Per-tenant concurrency. One semaphore per tenant, sized from the tenant's share of the bill: operations gets twelve slots, warehouse ten, finance six, sales four. When operations fills its twelve, the hundred-and-first pallet question waits in operations' queue, up to three seconds, and then gets degraded mode. Finance's six slots are untouched. [PAUSE] That's the whole trick. The provider's limit is shared, so somebody has to divide it before the provider does it for you, and the provider divides it by who asked first.

Two metrics: an in-flight gauge per tenant, and a queue-wait histogram, both low cardinality. When queue wait shows up on the dashboard for one tenant, that tenant has outgrown its slots, and the showback tells you whether to give it more.

[SLIDE 3: Shedding order (what to drop first when you must)]
1. Repeat `shipment_status` checks within 5 minutes: serve the cached tool result, no model call
2. Non-urgent `policy_question` from a tenant over its soft cap: economy mode (6.7)
3. Judge sampling (Section 8): pause it; it's your own traffic
4. Escalations to gpt-4.1: hold, unless `sensitive_action`
5. Never shed: `password_reset`, `create_ticket` for priority "high"

[AVATAR]

When you must shed, shed in a declared order. First, repeated shipment checks within five minutes: serve the tool result you already have, no model call at all. Second, policy questions from a tenant already over its soft cap go to economy mode. Third, your own traffic: pause the judge sampling from Section 8, because grading answers is less important than giving them. Fourth, hold escalations to the strong model unless they're sensitive actions. And two things you never shed: password resets and high-priority tickets, because those are the requests where a delay costs more than the tokens. [PAUSE] Write this list down before the incident. During the incident nobody has time to argue about it.

[SLIDE 4: Degraded mode messaging]
- Say what's happening: "Atlas is busy right now, so this answer is shorter than usual."
- Say what still works: "Ticket creation and password resets are unaffected."
- Say what to do: "For the full policy text, see the linked article, or ask again in a few minutes."
- Never fake it: no invented answers to fill a shorter budget
- Mark the response `degraded=True` and tag the trace `degraded` so you can count it

[AVATAR]

And the message. Degraded mode is not a failure if you tell the truth. Say what's happening, in one sentence. Say what still works. Say what to do. And never let the shorter budget turn into an invented answer. A three-line honest reply keeps trust. A confident wrong one loses it for a quarter. Mark the response and tag the trace, so the number of degraded answers is on the dashboard next to the number of fallbacks.

[SLIDE 5: The reliability stack so far]
- 7.3 timeouts and bounded retries: survive a blip
- 7.4 fallbacks and cooldowns: survive a slow or failing model
- 7.5 per-tenant concurrency and shedding: survive your own success
- 6.7 budgets and economy mode: survive a runaway
- Next: prove it, with chaos

[AVATAR]

Here's the stack. Timeouts and bounded retries survive a blip. Fallbacks and cooldowns survive a slow model. Per-tenant concurrency and shedding survive your own success. Budgets survive a runaway. [PAUSE] Four layers, each justified by a number from a worksheet or a report. Next, we break the provider on purpose and see whether they hold.

### Recap

Honour `Retry-After` and count 429s, divide the provider's limit with per-tenant semaphores sized from the showback, shed in a declared order starting with your own traffic, and tell users the truth in degraded mode.

### Transition

Time for chaos. In the next lecture we inject a slow provider at peak and watch p95, fallback rate and cost, then tune and run it again.

### Speaker notes: common mistakes and Q&A

- **Global concurrency only.** One tenant's burst still starves the others. Per-tenant is the point.
- **Semaphore sizes as guesses.** Derive from the showback share of sessions; revisit monthly.
- **Shedding writes first.** Students often drop `create_ticket` because it's "expensive". It's the one thing users can't get elsewhere. Never shed writes.
- **Degraded answers that hallucinate.** Economy mode caps output tokens; the prompt must say "if you cannot answer within the limit, say so and link the article", or the model fills the gap.
- **This is a slides lecture.** The semaphore code lives in `app/server.py`; Lab 4 has students read it.

---

## Lecture 7.6: Chaos demo: slow provider during peak

| Field | Value |
|---|---|
| ID | 7.6 |
| Title | Chaos demo: slow provider during peak |
| Type | DM (live demo) |
| Target duration | 7:00 (about 720 spoken words at ~140 wpm; remaining time is dashboards and runs) |
| One idea | Inject a slow provider at lunchtime peak, watch p95 blow through the budget with zero fallbacks, then tune first-token timeouts and fallbacks and hold p95 at 3.8 seconds for about a dollar. |
| Prerequisites | 7.1 to 7.5 |
| Files used | `simulator/scenarios.py::slow_provider`, `console/ops_console.py`, `src/northwind/config.py` |

**Learning objectives**

1. Read a latency incident from three charts: p95 first visible token, fallback rate and cost per hour.
2. Explain why untuned timeouts produce a slow failure rather than a fast fallback.
3. Tune first-token timeout and fallback order, re-run, and verify against the budget.

### Script

[AVATAR]

Everything in this section has been a claim. Timeouts from the budget, fallbacks with cooldowns, per-tenant queues. [PAUSE] Claims are cheap. Let's break the provider at the busiest time of day and see what's true.

[SLIDE 1: The scenario: `slow_provider`]
- 12:00 to 12:45, lunchtime peak: 1,400 requests in the hour, up from 1,000
- 35% of calls to gpt-4.1-mini get a first token after 4 to 6 seconds instead of 0.55
- No errors. No 429s. Just slow. The hardest kind of incident to see.
- Run 1: version-one settings (20 s flat timeout, no first-token timeout, no fallbacks)
- Run 2: tuned settings from 7.3 and 7.4

[AVATAR]

The scenario. Forty-five minutes at lunchtime. Traffic up forty percent. About a third of calls to the small model take four to six seconds to start instead of half a second. No errors. Nothing returns a status code you could alert on. Just slow. This is the incident that gets you a Slack message saying "is Atlas down?" while every health check is green.

[SCREEN: terminal, then Ops Console with three panels: p95 first visible token with the red 4 s line, fallback rate, cost per hour]

Run one. Version-one settings.

```bash
OFFLINE=1 RELIABILITY=v1 make replay SCENARIO=slow_provider
```

[DEMO: the three panels fill in. From 12:00 the p95 line climbs: 3.4 → 6.1 → 9.8 → 11.2 s by 12:20 and stays there until 12:45. Fallback rate: flat zero. Cost per hour: flat, $2.50, unchanged. Requests in flight (fourth small panel): climbing to the concurrency ceiling. Error rate: 0.2%, unchanged.]

Watch the p95. Twelve oh five, six seconds. Twelve ten, almost ten. Twelve twenty, eleven point two, and it stays there for the rest of the window. Now look at the other two panels. [PAUSE] Fallback rate: zero. Cost: unchanged, two dollars fifty an hour, exactly normal. Error rate: normal.

This is what a slow failure looks like. Nothing failed, so nothing fell back. The twenty-second timeout never fired, because five seconds is under twenty. Every one of those slow calls just... completed. Slowly. Three steps, each with roughly a one-in-three chance of a five-second start. Seven requests in ten hit at least one. One in four hit two, and that's eleven seconds to the first word. For forty-five minutes. Nearly three hundred people waited more than eight seconds.

And the cost panel is the cruelest part. Finance would never know. Nothing cost more. The bill for a terrible lunch hour was identical to a good one.

[AVATAR]

So what do we change? Not the fallback list; it was fine, it just never fired. The thing that never fired is the timeout. [PAUSE] Six seconds to first token, from 7.3. Five times the p95. Slow enough that a normal slow call gets through, fast enough that a stalled one fails in time to fall back within the budget.

[SCREEN: `src/northwind/config.py` diff, then terminal]

```python
llm_first_token_timeout_s: float = 6.0      # was: none
llm_total_timeout_s: float = 25.0           # was: 20.0 flat
llm_max_retries: int = 0                    # for a slow provider, don't retry the same deployment; fall back
```

Note the last line. For this scenario we set the agent's retries to zero, because retrying a slow deployment is waiting twice. The Router's fallback list takes over. Run two.

```bash
OFFLINE=1 RELIABILITY=tuned make replay SCENARIO=slow_provider
```

[DEMO: p95 climbs to 4.4 s at 12:05, then settles at 3.8 s from 12:10 to 12:45. Fallback rate: rises to 18% by 12:10 and holds; a small panel shows to_model split: `gpt-5-mini` 62%, `gpt-4.1` 38%. Cost per hour: $2.50 → $3.70 for the window. Cooldown events: a step chart showing the OpenAI mini deployment cycling open/half-open every 30 s.]

Now the same forty-five minutes. p95 pokes up to four point four at twelve oh five, one window of pain, then the cooldowns kick in and it settles at three point eight. Under budget. Fallback rate: eighteen percent, holding. Sixty-two percent of those fallbacks went to `gpt-5-mini`, cheapest viable first, and thirty-eight percent to gpt-4.1 when the fast model was also busy. Cost per hour: two fifty to three seventy. [PAUSE] A dollar twenty for the window. And the cooldown chart shows the circuit breaker doing exactly what 7.4 described: open for thirty seconds, one probe, open again, until twelve forty-five when the probe succeeds and it closes.

[SLIDE 2: Run 1 vs Run 2 (12:00 to 12:45)]

| | v1 settings | Tuned |
|---|---|---|
| p95 first visible token | 11.2 s | 3.8 s |
| Requests over 4 s budget | 72% | 4.6% |
| Fallback rate | 0% | 18% |
| Extra cost for the window | $0.00 | about $1.20 |
| Users who waited more than 8 s | about 290 | 3 |
| Visible in cost panel? | No | Yes: fallbacks are a line item |

[AVATAR]

Side by side. Eleven point two to three point eight. Users over eight seconds: two hundred ten to three. A dollar twenty. And the last row is the one I want you to remember: in the tuned version, the incident shows up in the cost panel, because fallbacks cost money and we attribute them honestly. Reliability made the incident visible to finance. [PAUSE] That's not a side effect. That's observability.

[SLIDE 3: What we did not change]
- Fallback list: already right, never fired
- Concurrency limits: held; operations queued for 1.1 s at worst
- Budget guard: never triggered; $1.20 is inside every tenant's headroom
- The agent's prompt, models or tools: untouched

[AVATAR]

And what we didn't touch. The fallback list. The concurrency limits, which held; operations queued for a second at worst. The budget guard, which never fired, because a dollar twenty is inside everyone's headroom. The prompt, the models, the tools. One timeout was the whole fix, and the reason we knew which one was that three charts told us fallbacks were at zero while p95 was at eleven.

One more run for you to try yourself: set the first-token timeout to two seconds instead of six and watch what happens. [PAUSE] Fallback rate goes to forty percent on a normal day, cost goes up a third, and p95 barely moves. Too tight is its own incident. The lab is about finding the number in between.

### Recap

A slow provider is a silent incident: p95 blows the budget while errors, fallbacks and cost stay flat; a first-token timeout of five times p95 turns it into fallbacks that hold p95 at 3.8 s for about a dollar.

### Transition

Your turn. Lab 4 hands you the same scenario with a different seed and asks you to hold p95 under four seconds until the budget gate passes.

### Speaker notes: common mistakes and Q&A

- **"Why not just fall back on latency?"** The Router falls back on errors and timeouts. A timeout is how you turn latency into an error. That's the insight of the whole demo.
- **Latency-based routing alone.** It helps between two deployments with the same name but reacts over minutes; the timeout reacts in six seconds. Use both.
- **Retries during a slowdown.** Show the `llm_max_retries=0` line and explain that for this scenario the fallback list is the retry.
- **The 4.4 s blip.** The first five minutes are over budget because the breaker needs three failures to open. That's the trade; tighter `allowed_fails` opens faster and flaps more.
- **Panel layout for recording.** Three panels stacked, same time axis, p95 with the red budget line. Annotate 12:00 and 12:45.

---

## Lecture 7.7: Lab 4: Hold p95 under 4 seconds during chaos

| Field | Value |
|---|---|
| ID | 7.7 |
| Title | Lab 4: Hold p95 under 4 seconds during chaos |
| Type | LAB (guided lab; short video intro, work off-video) |
| Target duration | Video 3:00 (about 260 spoken words at ~140 wpm, plus slide time); lab work 45 to 90 minutes |
| One idea | Tune timeouts, fallbacks and concurrency until the budget gate passes on a slow-provider day with a new seed, and explain each setting from the worksheet. |
| Prerequisites | 7.1 to 7.6 |
| Files used | `04-labs/lab-04-latency-chaos.md`, `src/northwind/config.py`, `tests/budget/test_budget_gate.py`, `simulator/scenarios.py` |

**Learning objectives**

1. Run the `slow_provider` scenario with seed `lab4` and read the three charts.
2. Adjust `llm_first_token_timeout_s`, fallback order, `allowed_fails`, `cooldown_time` and per-tenant concurrency until `make budget-check` passes.
3. Justify every changed setting with a row from the latency budget worksheet.

### Script

[AVATAR]

Lab four. Same scenario as the demo, different seed, and this time the slow calls hit a different model and a different hour. [PAUSE] Your job is to make the budget gate pass, and to write one line for every setting you changed saying which worksheet row justifies it.

[SCREEN: `04-labs/lab-04-latency-chaos.md`, the checklist]

The lab starts with `OFFLINE=1 make replay SCENARIO=slow_provider SEED=lab4`, then `make budget-check`. The gate asserts three things: p95 first visible token under four seconds, cost per session under seventy-five hundredths of a cent, and zero duplicate tickets. On the lab seed, the default settings fail the first one and, if you're not careful with retries, the second.

Then you tune. `llm_first_token_timeout_s`. The order of the fallback list. `allowed_fails` and `cooldown_time`. And the per-tenant concurrency numbers, because on this seed the slow window hits the warehouse tenant's burst.

[SLIDE 1: Lab 4 checklist]
- Replay `slow_provider` with seed `lab4`; screenshot the three charts, gate red
- Tune config until `make budget-check` is green; screenshot again
- Fill the worksheet row for each changed setting
- Stretch: make it pass with fallback cost under $1.00 for the window
- Submit: both screenshots, the config diff, the worksheet

[AVATAR]

Two hints. First, look at the fallback panel before you touch anything; if it's at zero, the fix is a timeout, not a fallback. Second, when the gate passes, try to make it pass cheaper. The stretch goal is fallback cost under a dollar for the window, and it's harder than it sounds, because tightening the timeout raises the fallback rate on healthy calls too.

The lab is written for offline mode. If you have keys and want to run it against the real provider, the lab tells you how, and reminds you to set a spending cap first.

### Recap

Lab 4 makes the budget gate pass on a slow-provider day with a new seed, with every changed setting justified from the worksheet.

### Transition

Before the lab, the Section 7 quiz.

### Speaker notes: common mistakes and Q&A

- **Retries on.** Students who leave `llm_max_retries=2` pass the latency gate and fail the cost gate. That's the intended lesson.
- **Timeout too tight.** 2 s passes p95 but fails the stretch goal on cost. Point them at the fallback rate on the healthy hours.
- **Skipping the worksheet.** Grade it. The setting without a justification is the one that breaks next quarter.

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

Six questions. You'll compute a p95 from a short list with the nearest-rank rule. You'll be given a provider's TTFT p95 and asked for a sensible first-token timeout. You'll match four failure shapes, a blip, a slow provider, an outage and a burst, to the control that handles each. And you'll spot the one setting in a Router config that makes a slow provider invisible.

[SLIDE 1: Quiz: 6 questions]
- Percentiles and budgets
- Timeouts from p95
- Failure shape → control
- Reading a Router config

[AVATAR]

One tip: whenever a question shows you a chart with flat errors and rising latency, the answer involves a timeout.

### Recap

The quiz checks that you can budget in percentiles and choose the right reliability control for each failure shape.

### Transition

Atlas is fast and it stays up. Next section: is it any good? Online evaluation, feedback and drift on live traffic.

### Speaker notes: common mistakes and Q&A

- Most-missed: "p95 of [1, 2, 2, 3, 3, 3, 4, 5, 9, 12]" with nearest rank. Answer: ceil(0.95 × 10) = 10th value = 12.
- Second: students pick "add a fallback" for the slow-provider chart; the answer is "add a first-token timeout so the fallback fires".
