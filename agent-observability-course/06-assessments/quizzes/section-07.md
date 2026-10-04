# Quiz: Latency and Reliability (Section 7)

| Field | Value |
|---|---|
| Udemy lecture | 7.8 Quiz: Latency and reliability |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 7.1 to 7.7 |

---

### Q1. Ten request latencies, in seconds: [1, 2, 2, 3, 3, 3, 4, 5, 9, 12]. What is the p95 the way `northwind.latency.percentile` computes it, and is it within a 4-second budget?

*Related lecture: 7.2 Code-along: measure TTFT, TPOT and p95 from spans*

- **A.** 10.65 s: sorted, the rank is k = (10 − 1) × 0.95 = 8.55, so the value is 9 + 0.55 × (12 − 9) = 10.65. Over budget.
  - *Explanation:* Correct. `percentile` interpolates linearly between the two neighbours, the same default as pandas. The mean of this list is 4.4 s and the median is 3 s; the budget is defined on p95 because averages hide the tail.
- **B.** 12 s: the 95th percentile of ten values is the largest one.
  - *Explanation:* Incorrect for this course. That is the nearest-rank definition; `percentile` interpolates, so it lands between 9 and 12. Both are over budget, but the CI gate compares the interpolated number.
- **C.** 9 s: 95% of ten values is 9.5, rounded down to the ninth value.
  - *Explanation:* Incorrect. Rounding down discards the interpolation and under-reports the tail.
- **D.** 4.4 s: the mean, just over budget.
  - *Explanation:* Incorrect. 4.4 s is the mean. The budget is "p95 ≤ 4,000 ms", never a mean.

**Correct answer: A**

---

### Q2. The latency worksheet says a normal model call starts in about 0.7 s at p95 and finishes in under 3 s. Atlas ships `ATLAS_REQUEST_TIMEOUT_S=20` with `ATLAS_MAX_RETRIES=2`. What per-call timeout does lecture 7.3 argue for, and why?

*Related lecture: 7.3 Timeouts, retries and backoff done right*

- **A.** Keep 20 s: a longer timeout means fewer errors.
  - *Explanation:* Incorrect. 20 s is about seven times the slowest normal call; with two retries a stalled provider can make one user wait a minute before seeing an error.
- **B.** About 6 s, roughly twice the slowest normal call: it cuts off a stall without cutting off a long answer, and it turns a stall into an error that a retry or a fallback can act on.
  - *Explanation:* Correct. The timeout is derived from a worksheet row, not guessed. Offline, the mock ignores `timeout=`, so the effect shows only against a real provider (`.env.chaos.example`).
- **C.** 1 s, the p95 time to first token: anything slower is a failure.
  - *Explanation:* Incorrect. The timeout covers the whole call; a 1 s limit would cut off most normal answers.
- **D.** No timeout; rely on the 4 s end-to-end budget.
  - *Explanation:* Incorrect. A budget is a measurement, not a control. Without a per-call timeout nothing stops a stalled call.

**Correct answer: B**

---

### Q3. Match each failure shape to the control that handles it: (1) a blip of a few transient 5xx errors; (2) a slow provider whose calls stall but do not error; (3) a provider outage; (4) a burst of traffic from one tenant.

*Related lecture: 7.4 Fallbacks and circuit breakers with the Router*

- **A.** (1) fallback; (2) retry; (3) shedding; (4) timeout.
  - *Explanation:* Incorrect. Retrying a stall just waits again, and shedding does not answer anyone during an outage.
- **B.** (1) shedding; (2) fallback; (3) retry; (4) circuit breaker.
  - *Explanation:* Incorrect. A fallback on a slow provider never fires, because nothing errors; that is why (2) needs a timeout first.
- **C.** (1) bounded, jittered retry; (2) a per-call timeout that turns the stall into an error so a fallback can fire; (3) fallback plus a circuit breaker so requests stop paying the primary's failures; (4) per-tenant concurrency limits that shed with 429 and `Retry-After`.
  - *Explanation:* Correct. Each shape gets its own control. The slow provider is the trap: errors stay flat while latency rises, and nothing falls back until something errors.
- **D.** All four: raise the retry bound.
  - *Explanation:* Incorrect. More retries lengthen the tail on (2), multiply load on (3) and amplify (4).

**Correct answer: C**

---

### Q4. A teammate's Router config has a fallback for every model, `allowed_fails=3` and `cooldown_time=30`, and `timeout=600`. During the `slow_provider` scenario p95 goes to 9.4 s, yet `atlas_model_fallbacks_total` stays flat and the breaker never opens. Which setting makes the slow provider invisible to the reliability controls?

*Related lecture: 7.4 Fallbacks and circuit breakers with the Router*

- **A.** `allowed_fails=3`: it should be 1.
  - *Explanation:* Incorrect. The breaker counts failures, and a stall that never times out is not a failure. Lowering the count changes nothing.
- **B.** `cooldown_time=30`: it should be 300.
  - *Explanation:* Incorrect. Cooldown only matters after the breaker opens, which it never does here.
- **C.** The fallback table: it needs a second provider.
  - *Explanation:* Incorrect. The fallbacks exist; they never fire, because no call fails.
- **D.** `timeout=600`: with a ten-minute timeout a slow call never errors, so retries, fallbacks and the breaker never see a failure. A timeout near twice the slowest normal call turns the stall into an error the other controls can act on.
  - *Explanation:* Correct. That is lecture 7.6's lesson: a slow provider is a silent incident until a timeout makes it loud. Fallbacks, priced on the model that answered (`gpt-4.1-mini` falls back to `gpt-4o-mini`), then move the traffic somewhere the slowness isn't.

**Correct answer: D**

---

### Q5. Atlas receives HTTP 429 from the provider with a `Retry-After: 4` header while under load, and the `finance` tenant is generating most of the traffic. Which response follows lecture 7.5?

*Related lecture: 7.5 Rate limits, queues and graceful degradation*

- **A.** Honour `Retry-After` with jittered backoff, apply a per-tenant concurrency limit so one noisy tenant cannot consume the whole quota, shed or queue low-priority traffic, and tell affected users they are in a degraded mode rather than failing silently.
  - *Explanation:* Correct. Rate limits are shared resources; per-tenant limits are fairness, jitter avoids synchronised retries, and honest degraded-mode messaging is part of graceful degradation.
- **B.** Switch every tenant to the escalation model, which has a separate quota.
  - *Explanation:* Incorrect. Quotas are usually per account, and the escalation model is five times the price; this converts a throttle into a cost incident.
- **C.** Disable retries entirely so 429s become user-facing errors.
  - *Explanation:* Incorrect. A single bounded, delayed retry after `Retry-After` is exactly what 429 asks for; disabling all retries throws away recoverable requests.
- **D.** Retry immediately in a tight loop until it succeeds.
  - *Explanation:* Incorrect. Hammering a rate-limited endpoint extends the limit and turns a throttle into a retry storm (a cost event as well as a latency one).

**Correct answer: A**

---

### Q6. Atlas never re-runs a tool by itself, but a teammate adds a generic HTTP retry wrapper around every tool call, including `create_ticket`. What is the specific harm, and what is the fix from lecture 7.3?

*Related lecture: 7.3 Timeouts, retries and backoff done right*

- **A.** No harm: retries only affect latency.
  - *Explanation:* Incorrect. A retried write that succeeded the first time (the response was just slow) creates a duplicate.
- **B.** A `create_ticket` call whose first attempt actually succeeded, but answered slowly, is retried and opens a second ticket for the same request: extra calls plus a data-quality incident for the helpdesk team. Fix: give the write an idempotency key (the trace id plus the step) before anything retries it, so a retry returns the same ticket.
  - *Explanation:* Correct. Reads like `lookup_ticket` are safe to repeat; writes need idempotency before they are retried at all. The model asking for a tool again is a different problem, bounded by `ATLAS_MAX_TOOL_RETRIES` (lecture 5.6).
- **C.** The harm is that tickets get the wrong priority.
  - *Explanation:* Incorrect. Priority is unaffected by retries; duplication is the problem.
- **D.** The fix is to never retry any tool.
  - *Explanation:* Incorrect. Reads benefit from a bounded retry; the rule is "retry only what is safe to repeat".

**Correct answer: B**
