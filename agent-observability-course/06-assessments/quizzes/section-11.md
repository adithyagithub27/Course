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
  - *Explanation:* Correct. In Incident 2 the first slow trace shows a slow model call, which is only half the story; the timeline reveals the 12:30 release and the 13:10 provider slowdown as two separate events.
- **D.** They skipped writing the postmortem first.
  - *Explanation:* Incorrect. The postmortem comes after mitigation; the method is about investigation order.

**Correct answer: C**

---

### Q2. Incident 1: finance's hourly cost jumped 20× with flat request counts, `lookup_ticket` errors at 9%, p95 up but under budget. What was the root cause and the compounding mechanism?

*Related lecture: 11.2 Incident 1: Monday's cost spike*

- **A.** A user ran a script hammering the API.
  - *Explanation:* Incorrect. Requests per hour were flat; cost per request is what rose.
- **B.** A prompt change made answers longer.
  - *Explanation:* Incorrect. Output tokens were flat; the growth was on the input side, and there was no release.
- **C.** The provider raised prices.
  - *Explanation:* Incorrect. Prices are pinned and the other tenants were unaffected.
- **D.** The finance ticket API began failing intermittently; Atlas retried `lookup_ticket` per step up to `max_retries` and kept every failed result (about 560 tokens each) in the conversation, so a retry storm at the tool level compounded with context bloat, making each successive model call larger until the step limit.
  - *Explanation:* Correct. Two mechanisms, one cause. Evidence: `execute_tool lookup_ticket` spans per trace rose from 1.1 to 11.4, and `atlas.context_tokens` climbed from 1,180 to 5,900 across steps. The tool error alert threshold (10%) was just above the observed 9%.

**Correct answer: D**

---

### Q3. Incident 2: p95 doubled to 4.9 s after lunch; a 12:30 release raised retrieval `top_k` from 4 to 12; the provider slowed from 13:10. Which statement is correct?

*Related lecture: 11.3 Incident 2: p95 doubled after lunch*

- **A.** Neither alone breached the budget; together they did, because 2.4× more input tokens made every already-slow call slower and every retry after a timeout costlier. The fix is both a fallback with a shorter timeout (for the provider) and `ATLAS_TOP_K=4` (for the release), and a CI budget gate would have blocked the `top_k` PR at +25% cost before it ever met the slow provider.
  - *Explanation:* Correct. "No single change caused it" is a valid and common root-cause statement; the postmortem names both and maps prevention to each.
- **B.** The judge scores should have caught this.
  - *Explanation:* Incorrect. A judge reads text and is blind to latency; scores stayed normal, correctly.
- **C.** The release alone caused the incident; roll it back and p95 returns to normal.
  - *Explanation:* Incorrect. The `top_k` change alone added about 300 ms and 25% cost, under both budgets.
- **D.** The provider alone caused the incident; the release is irrelevant.
  - *Explanation:* Incorrect. The slowdown alone would have pushed p95 to about 3.6 s, still under the 4 s budget.

**Correct answer: A**

---

### Q4. Incident 3: cost per session *fell* 8%, task success 94%, p95 normal, no alerts, yet HR reports vague and sometimes wrong answers after prompt v2 went to production on Wednesday. How do you confirm the cause and roll back, and what is the trap in the cost number?

*Related lecture: 11.4 Incident 3: users are unhappy but nothing is red*

- **A.** Celebrate the 8% saving and ask HR for examples.
  - *Explanation:* Incorrect. The saving *is* the symptom.
- **B.** Slice judge scores by `atlas.prompt_version` (v2 grounded 0.77 vs v1 0.90), confirm output tokens fell 26% from the promotion time, then move the `production` label in Langfuse back to v1 so every instance picks it up within `cache_ttl_seconds` with no deploy; the trap is that shorter, vaguer answers are *cheaper*, so a cost-only view rewards the regression.
  - *Explanation:* Correct. Task success is self-reported and stayed high; only judge scores, feedback and answer length moved, none of which had an alert before Sections 8 and 9. Prevention: offline eval on the failures dataset before promotion, and a drift alert on judge scores.
- **C.** Redeploy Atlas with the old prompt hard-coded.
  - *Explanation:* Incorrect. Unnecessary: the prompt is managed by label, and hard-coding removes the versioning that made diagnosis possible.
- **D.** Increase `top_k` to give the model more context.
  - *Explanation:* Incorrect. Retrieval did not change; the instruction to be brief did. This would add cost without addressing the cause.

**Correct answer: B**

---

### Q5. Which sentence belongs in a blameless postmortem, according to lecture 11.5?

*Related lecture: 11.5 Writing the postmortem*

- **A.** "The on-call engineer failed to notice the cost spike for three hours."
  - *Explanation:* Incorrect. It names a person's failure; the system had no alert that would have told anyone.
- **B.** "The prompt author should have run the evals."
  - *Explanation:* Incorrect. It assigns blame to a role for a step the process did not require.
- **C.** "No cost anomaly alert existed for per-tenant hourly spend, so the spike was detected by a human reading an invoice page three hours after onset; action: add the EWMA anomaly alert (owner: platform team, verified by the alert firing in the `context_bloat` replay)."
  - *Explanation:* Correct. It describes the system gap, the consequence, and an action item mapped to instrumentation, budget or test with an owner role and a verification. That is the template's shape.
- **D.** "Root cause: human error."
  - *Explanation:* Incorrect. "Human error" is where a blameless postmortem starts asking questions, not where it stops.

**Correct answer: C**

---

### Q6. Project 2 asks for prevention items that "map to instrumentation, budgets/alerts and tests/gates". Which set qualifies?

*Related lecture: 11.6 Project 2: Investigate a fourth incident*

- **A.** Rewrite Atlas in a different framework.
  - *Explanation:* Incorrect. A rewrite is not a prevention item; it is a project with its own risks and no guarantee the same gap is closed.
- **B.** Add more people to on-call.
  - *Explanation:* Incorrect. Staffing does not fix a missing signal; the incident went unnoticed because nothing alerted, not because nobody was there.
- **C.** "Be more careful with tool results", "monitor cost", "test more".
  - *Explanation:* Incorrect. None is checkable; no owner, no verification, no artefact.
- **D.** Instrumentation: add a `tool_result_bytes` histogram per tool (owner: agent team, verified in `/metrics`); alert: EWMA cost anomaly per tenant with a 2-hour detection target (owner: platform, verified by firing in the replay); gate: `test_tool_result_under_budget` in `tests/integration/` asserting every tool result attribute is under `tool_result_token_budget` (owner: agent team, verified by CI).
  - *Explanation:* Correct. Each item names an artefact, an owner role and how you know it was done. The rubric grades exactly this.

**Correct answer: D**
