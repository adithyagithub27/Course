# Quiz: Latency and Reliability (Section 7)

| Field | Value |
|---|---|
| Udemy lecture | 7.8 Quiz: Latency and reliability |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 7.1 to 7.7 |

---

### Q1. Twenty requests: eighteen take 900 ms and two take 12,000 ms. The latency budget is "p95 ≤ 4,000 ms". A teammate says "mean is 2,010 ms, we're fine." What is the correct reading?

*Related lecture: 7.1 Latency budgets for agents*

- **A.** Fail: p95 is 12,000 ms (with linear interpolation the 95th percentile of this sample lands in the two slow values), so a tenth of users had an unacceptable experience while the average looked healthy. Percentile budgets exist precisely because averages hide tails.
  - *Explanation:* Correct. Coding exercise CE2 uses this exact sample. Report p50, p95 and p99 together; act on p95; never quote a mean as a latency SLI.
- **B.** Pass, because two slow requests out of twenty is 10% and the budget allows 5%.
  - *Explanation:* Incorrect. The logic is inverted: p95 ≤ 4,000 ms means at most 5% may exceed 4,000 ms, and here 10% do.
- **C.** Inconclusive: twenty requests is too few to compute a percentile.
  - *Explanation:* Incorrect. Twenty is small but computable; the CI gate replays thousands, and the conclusion here is unambiguous.
- **D.** Pass: the mean is under budget, and p95 is a statistical curiosity.
  - *Explanation:* Incorrect. The budget is defined on p95, and the mean is dragged down by the eighteen fast requests; one in ten users waited 12 seconds.

**Correct answer: A**

---

### Q2. During the `slow_provider` chaos demo you cut the per-call timeout from 20 s to 6 s and nothing else. p95 improves from 9,900 ms to 7,100 ms, but the error rate in the slow window doubles from 16% to 31%. Why, and what is missing?

*Related lecture: 7.3 Timeouts, retries and backoff done right*

- **A.** The timeout is too short for normal traffic; raise it back.
  - *Explanation:* Incorrect. Normal calls finish in under a second; 6 s is generous for them. The problem is what happens after a timeout.
- **B.** Failing faster shortens the tail, but every timed-out call is retried against the *same* slow provider, so calls that would have completed in 8 s are now cut off and re-attempted, and more of them end in failure. A shorter timeout only helps when the retry has somewhere better to go: a fallback provider or model.
  - *Explanation:* Correct. Lab 4 walks through this trap. Timeouts bound the wait; fallbacks change the destination; circuit breakers stop paying the timeout at all once the provider is known to be slow.
- **C.** The error rate doubled because the mock LLM has a bug.
  - *Explanation:* Incorrect. The mock reproduces real provider behaviour: a slow endpoint plus a short timeout is a timeout error.
- **D.** p95 and error rate are unrelated; this is a coincidence.
  - *Explanation:* Incorrect. They are directly coupled through the timeout: the same knob moved both.

**Correct answer: B**

---

### Q3. A LiteLLM `Router` is configured with `fallbacks=[{"atlas-primary": ["atlas-fallback"]}]`, `allowed_fails=2`, `cooldown_time=120`. What does the cooldown do, and why does the fallback *rate* going up during an outage indicate success rather than failure?

*Related lecture: 7.4 Fallbacks and circuit breakers with the Router*

- **A.** Fallbacks are free, so the rate does not matter either way.
  - *Explanation:* Incorrect. Fallbacks change model and therefore cost and quality; Lab 4 measures both (nano is cheaper and scores lower on `grounded`).
- **B.** Cooldown pauses all traffic for 120 s after two failures; a high fallback rate means users are being rejected.
  - *Explanation:* Incorrect. Cooldown removes one deployment from rotation, not all traffic; fallbacks serve users, they do not reject them.
- **C.** After two failures within the window, the primary deployment is taken out of rotation for 120 s and requests go straight to the fallback without first paying the primary's timeout; a rising fallback rate means the breaker is open and users are being served quickly by the healthy path, which is exactly the intended behaviour during a provider incident.
  - *Explanation:* Correct. This is the circuit-breaker pattern (closed → open → half-open probe). Lab 4's tuned run has a 71% fallback rate in the slow window and a p95 of 3,400 ms. Alert on the breaker staying open too long, not on fallbacks happening.
- **D.** Cooldown lowers the temperature of the model to make it faster.
  - *Explanation:* Incorrect. Cooldown is a routing concept, unrelated to sampling temperature.

**Correct answer: C**

---

### Q4. Which fallback configuration passes the p95 gate but is rejected by the course, and why?

*Related lecture: 7.4 Fallbacks and circuit breakers with the Router*

- **A.** Falling back to a second provider serving the same model.
  - *Explanation:* Incorrect (acceptable): same model, same cost, different availability domain. Lecture 7.4 lists it as the ideal when available.
- **B.** No fallback, retries only.
  - *Explanation:* Incorrect as the answer to this question: it fails the gate rather than passing it, since retries against a slow provider extend the tail.
- **C.** Falling back from `gpt-4.1-mini` to `gpt-4.1-nano`.
  - *Explanation:* Incorrect (this is the accepted one): a cheaper, faster model keeps cost per session down during the outage at a measured, temporary quality cost.
- **D.** Falling back from `gpt-4.1-mini` to `gpt-4.1` (the escalation model).
  - *Explanation:* Correct, this is the rejected one. It passes p95 and, in the offline replay, even cost, but in a real outage it routes most traffic to a model five times the price, tripling cost per session, and it hides the outage behind better answers so nobody investigates. Escalation and fallback are different decisions with different models.

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

### Q6. `create_ticket` is not idempotent. During a `retry_storm`, what is the specific harm, and what is the fix from lecture 7.3?

*Related lecture: 7.3 Timeouts, retries and backoff done right*

- **A.** No harm: retries only affect latency.
  - *Explanation:* Incorrect. A retried write that succeeded the first time (the response was just slow) creates a duplicate.
- **B.** A timed-out `create_ticket` whose first attempt actually succeeded is retried and creates a second, third ticket for the same request: cost (extra tool and model calls) plus a data-quality incident for the helpdesk team. Fix: derive an idempotency key from `(session_id, step, arguments hash)` and have the tool return the existing ticket when the key repeats.
  - *Explanation:* Correct. Lab 4's stretch goal asserts no session creates two tickets with the same key under `retry_storm`. Reads can be retried freely; writes need idempotency before they are retried at all.
- **C.** The harm is that tickets get the wrong priority.
  - *Explanation:* Incorrect. Priority is unaffected by retries; duplication is the problem.
- **D.** The fix is to never retry any tool.
  - *Explanation:* Incorrect. Idempotent reads like `lookup_ticket` benefit from a bounded retry; the rule is "retry only what is safe to repeat".

**Correct answer: B**
