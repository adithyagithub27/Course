# Quiz: Incident Response (Section 11)

| Field | Value |
|---|---|
| Udemy lecture | 11.7 Quiz: Incident response |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 11.1 to 11.6 |

---

### Q1. Lecture 11.1's method is "timeline first, then blast radius, then hypotheses, then evidence in traces". A student opens the first slow trace they find and starts fixing the prompt. What did they skip, and why does it matter?

*Related lecture: 11.1 How to read an incident like an SRE*

- **A.** They should have restarted the service first.
  - *Explanation:* Incorrect. Restarting without a hypothesis destroys evidence and rarely fixes anything in this course's incidents.
- **B.** Nothing; the trace is the evidence.
  - *Explanation:* Incorrect. One trace is an anecdote; without the timeline you do not know whether it is representative or when the problem began.
- **C.** They skipped the timeline and blast radius, so they cannot tell when the change started (which points at releases and external events), who is affected (one tenant or all, one feature or all), or whether the trace they picked is typical; and they skipped hypotheses, so a fix is applied before a cause is established.
  - *Explanation:* Correct. In Incident 2 the first slow trace shows a retriever with top-k 18, which looks guilty; the timeline (p95 out of budget from 13:00, back at 17:00) and the flat input tokens show the provider was the cause and top-k a red herring.
- **D.** They skipped writing the postmortem first.
  - *Explanation:* Incorrect. The postmortem comes after mitigation; the method is about investigation order.

**Correct answer: C**

---

### Q2. Lecture 11.1's page map tells you where to look first. During an incident, input tokens per generation are flat but p95 has doubled. Which page and which number separate "the provider got slower" from "we made the requests bigger"?

*Related lecture: 11.1 How to read an incident like an SRE*

- **A.** The Traffic page: requests against the shadow line.
  - *Explanation:* Incorrect. Traffic answers "is it more requests?", not "is it the provider?".
- **B.** The Latency page: time to first token (`atlas.ttft_ms`) by hour. Nothing in our code runs between sending a prompt and receiving the first token, so TTFT rising while prompt sizes stay flat is the provider's fingerprint.
  - *Explanation:* Correct. In Incident 2, TTFT p95 went from 556 ms to about 1.9 s at 13:00 and back at 17:00 while input tokens stayed near 4,600 per generation.
- **C.** The Budgets page: tenant spend against the caps.
  - *Explanation:* Incorrect. Budgets answer "is someone about to be refused?"; cost per request did not move in this incident.
- **D.** The Safety page: guardrail events.
  - *Explanation:* Incorrect. Guardrails do not explain a latency change.

**Correct answer: B**

---

### Q3. Incident 1: ops's spend broke away at 09:00 and again at 10:00. At 08:55 a change switched the context diet off and raised retrieval top-k for ops; from 10:00 the provider timed out and Atlas resent those prompts up to three times. The same timeouts on a normal day (the full-day `retry_storm` replay) cost $58.00 against $56.28; with the retrieval change as well (`cost_spike`) the day costs $64.99. In postmortem terms, what is the root cause and what is the trigger?

*Related lecture: 11.5 Writing the postmortem*

- **A.** Root cause: the provider timeouts. Trigger: the retrieval change.
  - *Explanation:* Incorrect, reversed. The timeouts on their own cost $1.72 on a normal day; they pushed on a system the retrieval change had already made fragile.
- **B.** Root cause: the retrieval change shipped with no eval, cost check or gate. Trigger: the provider timeouts. Contributing factors: the 20-second timeout, a breaker that never saw three failures in a row, and a retry-storm alert nobody routed.
  - *Explanation:* Correct. The root cause is the thing that, removed, means the incident doesn't happen. A trigger pushes on it; contributing factors make it bigger or longer. If you missed this, rewatch the root-cause slide in 11.5 before Project 2.
- **C.** Root cause: human error by whoever merged the change.
  - *Explanation:* Incorrect. "Human error" is where a blameless postmortem starts asking questions, not where it stops; the system had no gate.
- **D.** There is no single root cause, so the postmortem should list everything equally.
  - *Explanation:* Incorrect. Separating root cause, trigger and contributing factors is what makes the action items land on the right thing.

**Correct answer: B**

---

### Q4. Incident 2: a provider slowdown tripled time to first token from 13:00 to 17:00. Atlas has `FALLBACKS` for every model and a `CircuitBreaker` that opens after three consecutive failures, yet the fallback never fired and p95 stayed around 8 s. Why, and what is the fix?

*Related lecture: 11.3 Incident 2: p95 doubled after lunch*

- **A.** The fallback table was empty; add entries.
  - *Explanation:* Incorrect. The fallbacks exist; nothing triggered them.
- **B.** With a 20-second per-call timeout, slow calls still succeeded, so the breaker, which counts only errors, never saw a failure. Fix: derive the per-call timeout from the step budget, and count a call over 4 s as a breaker failure (an action item; not in the shipped code) so three slow calls open the circuit.
  - *Explanation:* Correct. A breaker that only counts errors never protects a latency SLO. Lab 4 is where you build and tune the slow-call rule.
- **C.** Raise top-k back to 4; the retrieval change caused the slowdown.
  - *Explanation:* Incorrect. Top-k was a red herring: the context diet capped tool results, so prompt sizes stayed flat.
- **D.** Raise `ATLAS_MAX_RETRIES` so slow calls are retried.
  - *Explanation:* Incorrect. Nothing errored, so nothing is retried; more retries would only lengthen the tail once something did.

**Correct answer: B**

---

### Q5. Incident 3: judge `grounded` fell from about 0.94 to 0.56 at 11:00, cost per request fell about 7% and p95 fell from 3.5 s to 2.0 s; `atlas.prompt_version` reads `v1` before 11:00 and `v2` after. You run `python -m app.prompts promote --version 1`. What does it do, and what is the trap in the cost and latency numbers?

*Related lecture: 11.4 Incident 3: users are unhappy but nothing is red*

- **A.** It redeploys Atlas with v1 baked in; the trap is that cost went down, so nothing is wrong.
  - *Explanation:* Incorrect on the mechanism: no deploy happens. And falling cost is the trap, not the all-clear.
- **B.** It deletes version 2 from Langfuse so nobody can use it again.
  - *Explanation:* Incorrect. Versions are kept; only the label moves. Keep v2 for the postmortem.
- **C.** It calls `promote_prompt("atlas-system", 1, label="production")`, moving the `production` label back to version 1 (labels are unique, so v2 loses it); Atlas picks it up within the 60-second prompt cache, with no deploy or restart. The trap: v2's answers are shorter (output tokens 115 → 42), and shorter answers are cheaper and faster, so a cost or latency view rewards the regression.
  - *Explanation:* Correct. Offline, the same rollback is `ATLAS_PROMPT_VERSION=v1`. The prevention is to promote only from CI after an offline eval on `atlas-failures`, and to alert on the judge (the shipped `AtlasJudgeScoreLow` cannot fire because nothing exports judge scores to Prometheus).
- **D.** It switches the model to gpt-4.1 to make answers longer.
  - *Explanation:* Incorrect. The model did not change; the prompt did.

**Correct answer: C**

---

### Q5. Which sentence belongs in a blameless postmortem, according to lecture 11.5?

*Related lecture: 11.5 Writing the postmortem*

- **A.** "The on-call engineer failed to notice the cost spike for three hours."
  - *Explanation:* Incorrect. It names a person's failure; the system had no alert that would have told anyone.
- **B.** "The prompt author should have run the evals."
  - *Explanation:* Incorrect. It assigns blame to a role for a step the process did not require.
- **C.** "No cost anomaly alert existed for per-tenant hourly spend, so the spike was detected by a human reading an invoice page three hours after onset; action: add the EWMA anomaly alert (owner: platform team, verified by the Ops Console Alerts page flagging the `context_bloat` replay)."
  - *Explanation:* Correct. It describes the system gap, the consequence, and an action item mapped to instrumentation, budget or test with an owner role and a verification. That is the template's shape.
- **D.** "Root cause: human error."
  - *Explanation:* Incorrect. "Human error" is where a blameless postmortem starts asking questions, not where it stops.

**Correct answer: C**
