# Quiz: Foundations (Section 1)

| Field | Value |
|---|---|
| Udemy lecture | 1.6 Quiz: Foundations |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 1.1 to 1.5 |

---

### Q1. In the "$4,000 weekend" demo, Atlas hits a tool error, retries, and the cost meter climbs faster with every step even though each step is one model call. What is the mechanism that makes cost accelerate rather than grow steadily?

*Related lecture: 1.1 The $4,000 weekend*

- **A.** Each retry is billed at a higher rate by the provider as a penalty.
  - *Explanation:* Incorrect. Providers bill per token at a flat rate; there is no retry surcharge. The acceleration comes from the agent's own behaviour.
- **B.** Every step re-sends the whole conversation, including all previous failed tool results, so input tokens per step grow with each step and total cost grows roughly quadratically in the number of steps.
  - *Explanation:* Correct. The agent loop appends each tool result to the history and sends the entire history to the model on the next step. Input tokens rise linearly per step, so the sum over steps rises quadratically. That is why a step limit and tool-result truncation are the first two controls in the course.
- **C.** The escalation model is automatically selected after the first error.
  - *Explanation:* Incorrect. Escalation is a deliberate routing decision (Section 6), not an automatic consequence of a tool error, and the demo's run stays on the same model.
- **D.** Output tokens double on every retry because the model explains the error at greater length.
  - *Explanation:* Incorrect. Output stays short; the growth is on the input side, which is the part that carries the conversation history.

**Correct answer: B**

---

### Q2. A team already has a mature MLOps platform: model registry, feature store, training pipelines, drift monitoring on input feature distributions. They plan to reuse it unchanged to operate an LLM agent. Which agent property most directly breaks that plan?

*Related lecture: 1.2 What LLMOps means for agents*

- **A.** LLM providers do not expose metrics.
  - *Explanation:* Incorrect. Providers return usage on every call. The gap is that generic MLOps tools do not know what to do with token usage across a multi-step trace.
- **B.** Agents run on GPUs.
  - *Explanation:* Incorrect. Where the model runs is irrelevant when you call a hosted API, and MLOps platforms already handle GPU workloads.
- **C.** An agent's "prediction" is a multi-step, non-deterministic sequence of model calls and tool calls with a per-token cost, so there is no single input vector, output label or fixed inference cost to monitor.
  - *Explanation:* Correct. Classic MLOps assumes one input, one output, one inference cost. An agent request fans out into several generations and tool executions whose count and size vary per run, and whose cost is metered in tokens. Traces, quality-in-production and cost attribution are the three pillars that replace feature-drift monitoring.
- **D.** Agents cannot be versioned.
  - *Explanation:* Incorrect. Prompts, models and code are all versioned (Section 4 covers prompt versions with labels). Versioning is not the problem; the shape of a request is.

**Correct answer: C**

---

### Q3. Lecture 1.3 argues that emitting OpenTelemetry with the GenAI semantic conventions is the right foundation even though the course uses Langfuse as the backend. What is the argument?

*Related lecture: 1.3 The observability stack you will build*

- **A.** Langfuse only accepts OpenTelemetry data and has no SDK of its own.
  - *Explanation:* Incorrect. Langfuse has a full SDK with `@observe`, scores, prompts and datasets; it happens to be OTel-based underneath.
- **B.** GenAI semantic conventions are a stable, finalised standard, so nothing will change.
  - *Explanation:* Incorrect. The GenAI conventions are explicitly incubating and names may change, which is why the course routes them through a helper module. Portability, not stability, is the argument.
- **C.** OpenTelemetry is faster than Langfuse's native SDK.
  - *Explanation:* Incorrect. Langfuse's SDK v4 is itself built on OpenTelemetry, so there is no separate faster path.
- **D.** OpenTelemetry is the vendor-neutral wire format: the same spans can be sent to Langfuse today and to Phoenix, LangSmith via OTLP, Datadog or a file tomorrow, so the instrumentation work is not lost if the backend changes.
  - *Explanation:* Correct. Instrumenting once in OTel with standard attribute names buys portability. What does not port automatically is backend-specific state such as scores, prompts and datasets, which Section 12 discusses.

**Correct answer: D**

---

### Q4. Why does every lab in the course have an offline path (`OFFLINE=1`), rather than requiring students to use real API keys?

*Related lecture: 1.4 Meet Atlas and the swarm*

- **A.** Because observability is about having data to look at, and a deterministic mock LLM plus a traffic simulator produces a full day of realistic, multi-tenant spans with injectable incidents at zero cost and with reproducible numbers, which real traffic cannot guarantee.
  - *Explanation:* Correct. The swarm replays a seeded day of traffic; incidents like `loop` or `slow_provider` can be injected on demand. Students always have rich data, and instructor and student see the same numbers. Real keys are used for the parts that need them (first trace, online judge).
- **B.** Because the mock LLM gives better answers than the real model.
  - *Explanation:* Incorrect. The mock gives deterministic, plausible answers with realistic token counts and latencies. It is not a quality benchmark.
- **C.** Because Langfuse does not work with real traffic.
  - *Explanation:* Incorrect. Langfuse works with real and replayed traffic alike; the offline path only replaces the LLM and, optionally, the backend.
- **D.** Because the OpenAI API cannot be called from a laptop.
  - *Explanation:* Incorrect. It can; Section 2 does exactly that for the first trace.

**Correct answer: A**

---

### Q5. The Atlas agent serves four Northwind departments as tenants. Which design choice in lecture 1.4 makes per-department cost attribution possible later in the course?

*Related lecture: 1.4 Meet Atlas and the swarm*

- **A.** Each department gets its own OpenAI API key, and the invoice is split by key.
  - *Explanation:* Incorrect. Separate keys give a monthly total per key at best, with no link to sessions, features or traces. The course attributes cost from spans, not invoices.
- **B.** Every request carries tenant, user and session identifiers as HTTP headers, which become trace attributes (tags, `user_id`, `session_id`), so cost recorded on each generation can be rolled up by any of them.
  - *Explanation:* Correct. `X-Tenant`, `X-User-Id` and `X-Session-Id` are set on the trace. Because cost is attributed per generation span and every span belongs to a trace with those attributes, roll-ups by tenant, user, session and feature are queries rather than guesses.
- **C.** Atlas runs four separate copies, one per department.
  - *Explanation:* Incorrect. One service serves all tenants; separation is by attributes, not by deployment.
- **D.** Cost is estimated from request counts times an average price.
  - *Explanation:* Incorrect. Averages hide exactly the variation (loops, escalations, long histories) that the course is about. Cost is computed per generation from real usage.

**Correct answer: B**

---

### Q6. The course roadmap promises that by Section 14 you can "see, explain and stop" the runaway agent from lecture 1.1. Which trio of course tools maps to "see", "explain" and "stop" respectively?

*Related lecture: 1.5 Course roadmap*

- **A.** Logs; more logs; restarting the service.
  - *Explanation:* Incorrect. Logs without trace correlation cannot explain a multi-step run, and a restart is not a control.
- **B.** Prometheus counters; a Grafana dashboard; a Slack message.
  - *Explanation:* Incorrect. Metrics show that something is happening but not why for a single request, and a message stops nothing.
- **C.** A cost anomaly alert; a trace with step spans showing context growth and repeated tool errors; a step limit plus a per-tenant hard budget cap.
  - *Explanation:* Correct. The alert makes the problem visible in minutes (see), the trace explains the mechanism per request (explain), and the step limit and budget cap stop it automatically without a human (stop). Sections 6, 5 and 9 build each one.
- **D.** Langfuse prompt management; a dataset; an offline eval.
  - *Explanation:* Incorrect. Those are the quality loop of Sections 4 and 8; they do not stop a live cost runaway.

**Correct answer: C**
