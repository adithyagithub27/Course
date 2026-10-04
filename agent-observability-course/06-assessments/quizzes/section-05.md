# Quiz: Agent Patterns (Section 5)

| Field | Value |
|---|---|
| Udemy lecture | 5.8 Quiz: Agent patterns |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 5.1 to 5.7 |

---

### Q1. A trace of a three-step Atlas request shows four generations and two tool spans as a flat list under the agent span. A colleague asks "which step escalated to gpt-4.1 and why?" What structural change to the trace answers that question?

*Related lecture: 5.2 Code-along: tracing the tool loop step by step*

- **A.** Emit a Prometheus counter `escalations_total{step="2"}`.
  - *Explanation:* Incorrect. A counter tells you how often escalation happens at step 2 across all requests, not why this request escalated.
- **B.** Add the step number to the span name of every generation.
  - *Explanation:* Incorrect. It helps you eyeball order, but it does not group a step's generation with its tool calls, nor record why escalation happened.
- **C.** Wrap each loop iteration in a step span (`atlas.step N`) that is the parent of that step's generation and tool spans, and set attributes on it such as `atlas.step`, `atlas.context_tokens`, `atlas.escalated` and `atlas.escalation_reason`.
  - *Explanation:* Correct. The waterfall then shows step 2 escalated because of a stale ticket, its gpt-4.1 generation nested under it with its own cost, and context growing from step to step. Lab 3 builds exactly this.
- **D.** Log the decision with `print` and correlate by timestamp.
  - *Explanation:* Incorrect. Logs without `trace_id` correlation are the anti-pattern lecture 5.5 warns about, and timestamps do not survive concurrency.

**Correct answer: C**

---

### Q2. Why does lecture 5.3 treat the retriever observation (query, top-k, scores, empty-result flag) as a production metric rather than a debugging detail?

*Related lecture: 5.3 RAG spans: retrieval quality is a production metric*

- **A.** Because Langfuse requires a retriever observation for every trace.
  - *Explanation:* Incorrect. Langfuse has no such requirement; the observation type exists so retrieval renders well when you choose to record it.
- **B.** Because the knowledge base is updated daily.
  - *Explanation:* Incorrect. Update frequency is irrelevant to whether retrieval should be observed.
- **C.** Because retrieval is the most expensive step in tokens.
  - *Explanation:* Incorrect. Retrieval itself uses no LLM tokens; it *determines* how many tokens go into the prompt, which is a different point.
- **D.** Because the empty-result rate, the score distribution and the chosen top-k explain both quality (ungrounded answers follow empty or low-score retrievals) and cost (top-k times chunk size is a large share of input tokens), so a change in either shows up here first.
  - *Explanation:* Correct. Incident 2 is found through `atlas.retrieval.top_k` on the retriever span, and Lab 5's grounded score correlates with retrieval scores. If retrieval is not a span, both stories are invisible.

**Correct answer: D**

---

### Q3. A streamed response has 181 output tokens; the first token arrives at 400 ms and the last at 2,400 ms. What are TTFT and the decode speed, and which one do users feel most?

*Related lecture: 5.4 Streaming: time to first token and tokens per second*

- **A.** TTFT 400 ms; (181 − 1) tokens / 2.0 s = 90 tokens/s; users feel TTFT most because it is the silence before anything appears, which is why the course records `gen_ai.response.time_to_first_chunk` and `atlas.ttft_ms` on the generation span and Langfuse's `completion_start_time`.
  - *Explanation:* Correct. TPOT is the inverse, about 11 ms per token. Total time matters too, but a 400 ms start with steady streaming feels responsive while a 2.4 s silence followed by a burst does not.
- **B.** TTFT 400 ms; 181 tokens / 2.4 s = 75 tokens/s; users feel tokens per second most.
  - *Explanation:* Incorrect. The decode rate excludes the first token's time and the first token itself, and TTFT dominates perceived latency.
- **C.** TTFT cannot be measured with a streaming API.
  - *Explanation:* Incorrect. Streaming is exactly what makes TTFT measurable: it is the timestamp of the first delta event.
- **D.** TTFT 2,400 ms; 75 tokens/s; users feel total time.
  - *Explanation:* Incorrect. TTFT is the time to the *first* token (400 ms), and the decode rate is computed after it.

**Correct answer: A**

---

### Q4. Which of these is a cardinality trap that lecture 5.5 says will eventually take down your Prometheus?

*Related lecture: 5.5 Logs vs traces vs metrics for agents*

- **A.** A counter of tokens labelled by `model` (3 values) and `kind` (input/output).
  - *Explanation:* Incorrect. Six series; perfectly fine.
- **B.** A counter of requests labelled by `user_id`, so you can see cost per employee in Grafana.
  - *Explanation:* Correct, this is the trap. Thousands of employees times every other label combination means tens of thousands of series for one metric, growing without bound as users come and go. Per-user views belong in traces (Langfuse `user_id`), where high cardinality is normal.
- **C.** A gauge for the circuit-breaker state labelled by `deployment` (3 values).
  - *Explanation:* Incorrect. Three series; fine.
- **D.** A histogram of request duration labelled by `tenant` (4 values).
  - *Explanation:* Incorrect. Four tenants times a handful of buckets is a few dozen series; that is the intended use.

**Correct answer: B**

---

### Q5. In the `loop` scenario, `lookup_ticket` returns `ticket_service_unavailable` with `"retry": true` for TCK-100231, the model tries again with the same id, and it repeats until the step limit (6 by default). In the trace, the generation's input tokens per step read 3,261, 3,330, 3,399, 3,468, ... What does the pattern tell you about cost, and what would you see without step spans?

*Related lecture: 5.6 Break it: the loop you can only see in a trace*

- **A.** The model is hallucinating ticket ids; the fix is a better prompt.
  - *Explanation:* Incorrect as the whole answer. The model does repeat the same id, but the operational fix is a step limit, surfacing the tool error to the model clearly, and truncating error payloads. Prompt tuning alone gives no guarantee.
- **B.** Cost per step is constant; without step spans you would see the same thing in the total.
  - *Explanation:* Incorrect. Input grows by 69 tokens per step (the failed tool result rides along in the history), so each step costs more than the last.
- **C.** Input tokens grow linearly per step (each failed result stays in history), so cumulative cost grows quadratically with steps; without step spans you would only see "one slow, expensive request with many generations" and no indication that the same tool call was repeated with the same arguments.
  - *Explanation:* Correct. Step spans plus tool spans with arguments make the repetition and the growth explicit. The step limit turns an unbounded quadratic into a bounded one, and the `step_limit_reached` event marks it.
- **D.** The provider is slowing down; this is a latency incident.
  - *Explanation:* Incorrect. Per-call latency is normal; the count of calls and the size of each prompt are the problem.

**Correct answer: C**

---

### Q6. Lecture 5.1 lists the questions an agent trace must answer. Which of the following is *not* answerable from a well-instrumented trace and needs a different signal?

*Related lecture: 5.1 What an agent trace must answer*

- **A.** Which model handled each step and what each step cost?
  - *Explanation:* Incorrect (answerable): each generation carries its model and usage, and cost is attributed per generation.
- **B.** Why did it call that tool, with what arguments, and what came back?
  - *Explanation:* Incorrect (it is answerable): tool spans carry name, arguments and result; the preceding generation shows the tool call decision.
- **C.** How many steps did it take, where did the tokens go and where did the time go?
  - *Explanation:* Incorrect (answerable): step spans, `context_tokens`, generation usage and span durations answer all three.
- **D.** Is the answer actually correct and grounded in the knowledge base?
  - *Explanation:* Correct: a trace records what happened, not whether it was right. Correctness needs a judgement, from a human, user feedback or an LLM-as-judge score (Section 8), attached to the trace as a score.

**Correct answer: D**
