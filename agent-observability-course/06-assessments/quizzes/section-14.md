# Quiz: Capstone Review (Section 14)

| Field | Value |
|---|---|
| Udemy lecture | 14.7 Quiz: Capstone review |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 14.1 to 14.6 (and everything they draw on) |

---

### Q1. Capstone acceptance test AT-14 says a tenant over its hard cap must receive a polite refusal and Atlas must make **no** LLM call. A submission returns the polite refusal (HTTP 429, `outcome="refused"`) but the mock records one model call per refused request. What happened and why does the test insist on zero?

*Related lecture: 14.2 Reference solution part A: instrumentation and cost*

- **A.** The test is too strict; one call is negligible.
  - *Explanation:* Incorrect. One call per refused request at a runaway tenant is exactly the spend the cap exists to stop; under a loop scenario it is many calls.
- **B.** The budget check runs *after* the first model call (for example inside the step loop) instead of before it; the refusal is real but the cap is charged for. The test asserts zero calls because a cap that still spends is not a cap.
  - *Explanation:* Correct. Order of operations: guardrail, then budget decision, then the loop. `BudgetGuard.decide()` is designed to be called before spending, optionally with a pre-charged estimate.
- **C.** The mock LLM has a bug that records phantom calls.
  - *Explanation:* Incorrect. The mock records what the agent asked it to do.
- **D.** Refusals require a model call to phrase the message.
  - *Explanation:* Incorrect. The refusal is a fixed, templated message; generating it with the model would be both a cost and a quality risk.

**Correct answer: B**

---

### Q2. A capstone README claims "prompt caching saved 34%" with no other detail. What does the rubric require for that claim to earn full marks?

*Related lecture: 14.1 Capstone brief and acceptance criteria*

- **A.** A statement that the vendor documentation promises up to 50%.
  - *Explanation:* Incorrect. Vendor ceilings are not your measurement.
- **B.** A screenshot of the OpenAI usage page.
  - *Explanation:* Incorrect. The usage page shows totals, not a controlled comparison.
- **C.** The claim stated relative to a named, reproducible baseline: same replayed day, same seed, same prompt version, the single change toggled, with cost, cache hit ratio and judge score before and after, so the saving is attributable to that change alone.
  - *Explanation:* Correct. Every cost control in the capstone is "measured before/after on the same replayed day". Without the baseline, 34% could be traffic mix, a price change or two changes at once.
- **D.** The claim rounded to the nearest 10%.
  - *Explanation:* Incorrect. Precision is not the issue; attribution is.

**Correct answer: C**

---

### Q3. On the Quality page, a submission reports the weekly `resolved` score as the mean over all judged traces, and the judged set was chosen with the tail-sampling policy (100% of errors plus 10% of the rest). What is wrong?

*Related lecture: 14.3 Reference solution part B: quality, dashboards, alerts, CI*

- **A.** The mean should be over sessions, not traces.
  - *Explanation:* Incorrect as the main issue; the unit of analysis is a secondary choice, the sampling bias is the error.
- **B.** Judge scores should never be averaged.
  - *Explanation:* Incorrect. Averages of an unbiased sample are exactly how weekly quality is tracked and drift is detected.
- **C.** Nothing; more judged traces means a better estimate.
  - *Explanation:* Incorrect. More traces of a biased sample is a more precise wrong number.
- **D.** The mean is biased downward because error traces are over-represented; the headline must come from the head (rate) sample only, while the tail extras feed the worst-traces table and the dataset. Mixing them makes quality look worse after every incident and better after every quiet week.
  - *Explanation:* Correct. The head sample is deterministic per trace id (`head_sample`), so the two uses can always be separated. Lab 5's quality page and AT-20 both check this.

**Correct answer: D**

---

### Q4. Which pair of alerts on the same underlying problem shows the difference between a notification and an operation, as the capstone's AT-22 requires?

*Related lecture: 14.3 Reference solution part B: quality, dashboards, alerts, CI*

- **A.** `AtlasToolErrorRate` with a ratio expression, a minimum-traffic guard, `for: 10m`, a severity, an `owner` label and a `runbook` annotation pointing to a repo file whose first section answers "what do I do in the first five minutes"; versus the same expression with no `for`, no guard, no owner and no runbook.
  - *Explanation:* Correct. The first can be handed to an on-call engineer who has never seen Atlas; the second pages them with nothing to do. AT-22 also asks for each alert to be seen firing; in the shipped `deploy/alerts.yml` only `AtlasLatencyP95High` has a runbook and none has an owner, so the capstone adds both.
- **B.** An alert in Grafana versus the same alert in Prometheus.
  - *Explanation:* Incorrect. Where the rule is evaluated does not change its quality.
- **C.** A Slack alert versus an email alert.
  - *Explanation:* Incorrect. Channel is delivery, not content.
- **D.** An alert on cost versus an alert on latency.
  - *Explanation:* Incorrect. Both are needed; neither is inherently more "operational".

**Correct answer: A**

---

### Q5. The weekly ops report (lecture 14.4) is described as "the one-page report your manager forwards to finance without editing". Which content decision most directly serves that goal?

*Related lecture: 14.4 The weekly ops report your manager reads*

- **A.** Include every Prometheus metric so nothing is missing.
  - *Explanation:* Incorrect. Completeness is the enemy of a one-pager; the reader is not on call.
- **B.** Lead with cost (total, week-on-week, per tenant, cost per resolved session), then quality, latency, incidents and budget status, each as a number with its budget or baseline beside it, and close with three recommendations that carry a dollar figure and a trade-off; pin the price table date; name no employees.
  - *Explanation:* Correct. Numbers next to their targets let a non-engineer judge them; recommendations with dollars make the report actionable; pinned prices and no PII make it forwardable.
- **C.** Attach the raw spans as a CSV.
  - *Explanation:* Incorrect. Raw spans contain masked but still sensitive operational detail and no reader of this report wants them.
- **D.** Write it as a narrative without tables.
  - *Explanation:* Incorrect. Finance readers scan tables; narrative belongs in the recommendations only.

**Correct answer: B**

---

### Q6. In the domain swap (lecture 14.6) a student instruments the Course 3 voice receptionist with the Atlas stack. Which adaptation shows they understood *what must change* rather than copying Atlas?

*Related lecture: 14.6 Domain swap: observe a different agent*

- **A.** They replace Langfuse with a spreadsheet because calls are few.
  - *Explanation:* Incorrect. Volume does not remove the need for traces, cost attribution and a budget; and the assignment requires a viewable backend.
- **B.** They rename the tenant header to `X-Clinic` and keep every SLI identical.
  - *Explanation:* Incorrect. Renaming is not adapting; a voice agent's success and latency are different quantities.
- **C.** They keep GenAI-convention spans, per-generation cost and budgets, but change the headline unit to cost per call minute (adding telephony, STT and TTS costs), replace TTFT with time to first audio and voice-to-voice p95, add phone numbers and recordings to the PII mask, define "degrade" as switching to a cheaper TTS voice, and write judge criteria for read-back confirmation and speakability that would be meaningless for Atlas.
  - *Explanation:* Correct. The instrumentation template asks precisely for what carried over unchanged and what changed; this answer shows the stack is domain-agnostic and the SLIs are not.
- **D.** They drop tracing because voice is real-time and spans add latency.
  - *Explanation:* Incorrect. Batched export adds no request-path latency (Section 13), and Course 3 already emits OTel from its pipeline.

**Correct answer: C**
