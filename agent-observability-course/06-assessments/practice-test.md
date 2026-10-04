# Final Practice Test: AI Agent Observability & Cost Control

| Field | Value |
|---|---|
| Udemy lecture | 15.3 Final practice test (Udemy "Practice test" item) |
| Questions | 40 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Suggested time limit | 60 minutes |
| **Passing score** | **70% (28 of 40)** |
| Knowledge areas | Enter each question's "Domain" in Udemy's "Knowledge area" field so the results page breaks scores down by domain |

None of these questions repeats a section-quiz question; they test the same skills in new scenarios, with numbers to compute where the skill is numeric.

## Domain weighting

| # | Domain (Udemy knowledge area) | Sections | Questions | Weight |
|---|---|---|---|---|
| D1 | Foundations and tracing fundamentals | 1, 2, 3 | 5 | 12.5% |
| D2 | Langfuse and agent observability patterns | 4, 5 | 5 | 12.5% |
| D3 | Cost engineering | 6 | 7 | 17.5% |
| D4 | Latency and reliability | 7 | 5 | 12.5% |
| D5 | Online evaluation and drift | 8 | 5 | 12.5% |
| D6 | Dashboards, SLOs and alerting | 9 | 4 | 10% |
| D7 | Privacy, security and governance | 10 | 3 | 7.5% |
| D8 | Incident response | 11 | 3 | 7.5% |
| D9 | Portability, deployment and CI gates | 12, 13 | 3 | 7.5% |
| | **Total** | | **40** | **100%** |

Cost engineering carries the largest weight because it is the course's signature section (Section 6) and the skill employers ask for first.

## Answer key

| Q | Ans | Q | Ans | Q | Ans | Q | Ans |
|---|---|---|---|---|---|---|---|
| 1 | C | 11 | A | 21 | B | 31 | D |
| 2 | A | 12 | D | 22 | C | 32 | B |
| 3 | D | 13 | B | 23 | A | 33 | A |
| 4 | B | 14 | C | 24 | D | 34 | C |
| 5 | C | 15 | A | 25 | B | 35 | B |
| 6 | A | 16 | D | 26 | C | 36 | D |
| 7 | D | 17 | B | 27 | A | 37 | A |
| 8 | B | 18 | C | 28 | D | 38 | C |
| 9 | C | 19 | A | 29 | B | 39 | B |
| 10 | B | 20 | D | 30 | C | 40 | D |

---

## D1: Foundations and tracing fundamentals

### Q1. A platform team proposes monitoring their new LLM agent with the same three signals they use for a REST service: request rate, error rate, p95 latency. After a month, the bill has doubled and the dashboard is green. Which pillar did they miss and what would have shown the problem?

*Domain: D1 · Related lecture: 1.2 What LLMOps means for agents*

- **A.** They missed uptime; a synthetic health check would have shown it.
  - *Explanation:* Incorrect. The service was up; the problem was what each request consumed.
- **B.** They missed logs; grepping error logs would have shown it.
  - *Explanation:* Incorrect. Nothing errored. Logs without token usage say nothing about spend.
- **C.** They missed cost as a first-class signal: token usage and dollars attributed per generation, rolled up per tenant and per feature, would have shown cost per request rising while request count and errors stayed flat.
  - *Explanation:* Correct. Agents are token-metered; the same request can cost ten times more depending on steps, history and model. Rate, errors and latency are blind to that.
- **D.** They missed nothing; bills double when usage doubles.
  - *Explanation:* Incorrect. Request rate was flat; usage per request is what doubled.

**Correct answer: C**

### Q2. A span printed by `ConsoleSpanExporter` shows `"parent_id": null` and `"kind": "SpanKind.INTERNAL"` for a span named `execute_tool lookup_ticket`. What is certain about this span?

*Domain: D1 · Related lecture: 3.1 Traces, spans and context in five minutes*

- **A.** It is the root of its own trace: no span was current when it was created, so it is not attached to the agent's trace and any per-tenant roll-up will miss it.
  - *Explanation:* Correct. `parent_id: null` means root. For a tool span that is a context-propagation bug (thread or task without copied context, or created before the agent span).
- **B.** It failed, because internal spans are only created on error.
  - *Explanation:* Incorrect. `INTERNAL` is the default span kind for in-process work; it says nothing about status.
- **C.** It is a child of the most recent generation span.
  - *Explanation:* Incorrect. Parentage is explicit in `parent_id`; `null` means no parent.
- **D.** The exporter dropped its parent to save space.
  - *Explanation:* Incorrect. Exporters do not modify span relationships.

**Correct answer: A**

### Q3. Which attribute value on a span tells a GenAI-convention-aware backend that the span represents the agent invocation as a whole, rather than a model call or a tool execution?

*Domain: D1 · Related lecture: 3.3 GenAI semantic conventions*

- **A.** `gen_ai.operation.name = "chat"`
  - *Explanation:* Incorrect. `chat` marks a model call.
- **B.** `gen_ai.operation.name = "execute_tool"`
  - *Explanation:* Incorrect. That marks a tool execution.
- **C.** `span.kind = "SERVER"`
  - *Explanation:* Incorrect. Span kind describes the RPC role, not the GenAI operation.
- **D.** `gen_ai.operation.name = "invoke_agent"` together with `gen_ai.agent.name = "atlas"`
  - *Explanation:* Correct. The conventions define `invoke_agent` (and `create_agent`) as agent-level operations; `gen_ai.agent.name` identifies which agent. Langfuse renders it as an `agent` observation.

**Correct answer: D**

### Q4. Your service handles 200 requests per second. You export spans with a `SimpleSpanProcessor` to an OTLP endpoint that takes 40 ms per export. What is the effect on the request path?

*Domain: D1 · Related lecture: 3.2 Code-along: manual OpenTelemetry instrumentation of Atlas*

- **A.** None; export is always asynchronous in OpenTelemetry.
  - *Explanation:* Incorrect. `SimpleSpanProcessor` exports synchronously when each span ends.
- **B.** Every span end blocks for about 40 ms, so a request with five spans adds roughly 200 ms of exporter time inside the request, and a dead endpoint stalls requests until the export timeout; switch to `BatchSpanProcessor`.
  - *Explanation:* Correct. Telemetry must never be in the request path; batching moves export to a background thread with a bounded queue that drops spans, not requests, when the backend is slow.
- **C.** Spans are silently dropped because the processor cannot keep up.
  - *Explanation:* Incorrect. `SimpleSpanProcessor` does not drop; it blocks, which is worse.
- **D.** Throughput doubles because spans are smaller.
  - *Explanation:* Incorrect. Processor choice does not change span size.

**Correct answer: B**

### Q5. `OFFLINE=1 make replay` (seed 7) reports a day cost of $56.28 on your machine and $56.28 on the instructor's. Someone argues the replay is therefore "fake data" and worthless for learning cost engineering. What is the best counter?

*Domain: D1 · Related lecture: 2.4 Offline mode: a full day of traffic for free*

- **A.** The numbers are real API charges billed to the instructor.
  - *Explanation:* Incorrect. The replay makes no LLM calls.
- **B.** Determinism is a bug that will be fixed.
  - *Explanation:* Incorrect. Determinism is the design.
- **C.** Determinism is the point: the pricing, roll-up, budget and gate code that prices the mock's realistic usage is the same code that prices production usage, and a reproducible day is the only way to measure a change (caching on vs off) as a clean difference rather than noise.
  - *Explanation:* Correct. Every before/after claim in Section 6 and every CI gate in Section 13 relies on the same seed producing the same spans.
- **D.** The mock LLM is a fine-tuned model that behaves exactly like gpt-4.1-mini.
  - *Explanation:* Incorrect. The mock is a deterministic generator of plausible answers, usage and latency, not a model.

**Correct answer: C**

---

## D2: Langfuse and agent observability patterns

### Q6. You use `@observe(as_type="retriever")` on `search_knowledge_base` and want Langfuse to show the query, the number of chunks and their scores. Where should each go?

*Domain: D2 · Related lecture: 4.2 Code-along: `@observe` and observation types*

- **A.** Query as the observation input, chunks as the output, top-k and score statistics as metadata via `update_current_span(metadata=...)`; the observation type already tells Langfuse to render it as retrieval.
  - *Explanation:* Correct. Input/output are the primary fields Langfuse shows; low-cardinality descriptors go in metadata. Lecture 5.3 adds an empty-result flag the same way.
- **B.** Everything in the span name.
  - *Explanation:* Incorrect. Names are for identification, not payloads, and are not searchable as structured fields.
- **C.** Scores via `score_current_trace` one per chunk.
  - *Explanation:* Incorrect. Trace scores are evaluation signals about the trace; retrieval scores are observation data.
- **D.** As Prometheus labels on a counter.
  - *Explanation:* Incorrect. Queries and scores are high-cardinality; labels would explode.

**Correct answer: A**

### Q7. A Langfuse trace shows `session_id` set, `user_id` empty and the tag `tenant:finance`. In the Sessions view, the session groups correctly, but the Users view shows nothing for the employee. Which call is missing?

*Domain: D2 · Related lecture: 4.3 Sessions, users, tenants and tags*

- **A.** `create_score(name="user", value=...)`
  - *Explanation:* Incorrect. Scores are not identity.
- **B.** `update_current_generation(user_id=...)`
  - *Explanation:* Incorrect. Identity belongs on the trace; generations carry model and usage.
- **C.** `Langfuse(user_id=...)` at client construction.
  - *Explanation:* Incorrect. The client is process-wide; user is per request.
- **D.** `propagate_attributes(user_id=<hashed employee id>)` around the request, alongside the `session_id` and tags already being set.
  - *Explanation:* Correct. `user_id` is a trace-level field set per request; hashing it satisfies Section 10 while still populating the Users view.

**Correct answer: D**

### Q8. A student's `step N` spans record `atlas.context_tokens`. On a normal request the values are 2,521, 3,190, 3,604. On another request they read 2,521 at every one of six steps, each of which called a tool. What does the second pattern most likely indicate?

*Domain: D2 · Related lecture: 5.2 Code-along: tracing the tool loop step by step*

- **A.** A healthy request; constant context is ideal.
  - *Explanation:* Incorrect. In a tool loop, each step should add at least the previous tool result; perfectly flat context across six steps is suspicious.
- **B.** The step span attribute is being set once from the initial message list and not recomputed per step (an instrumentation bug), or history is being reset each step (an agent bug); either way, the attribute is not measuring what it claims and needs a test that asserts the value grows when a step adds a tool result (Lab 3's test is the pattern).
  - *Explanation:* Correct. Instrumentation needs tests too. Six identical readings across steps that call tools is a signal the measurement is wrong or the agent is discarding its own results.
- **C.** Prompt caching is working.
  - *Explanation:* Incorrect. Caching changes the *price* of input tokens, not their count.
- **D.** The context diet trimmed history to exactly the same size each step.
  - *Explanation:* Incorrect as the likely cause: the diet trims history to `ATLAS_HISTORY_TOKENS` (8,000) and tool results to 1,400 tokens, both well above these values, and it is off by default (`DIET=0`).

**Correct answer: B**

### Q9. Atlas streams its answer. Your generation span records `gen_ai.response.time_to_first_chunk = 0.38` seconds and a total duration of 2.1 seconds with 160 output tokens. A product manager asks for "the latency users feel". Which single number do you give, and why?

*Domain: D2 · Related lecture: 5.4 Streaming: time to first token and tokens per second*

- **A.** 2.1 s; total is what matters.
  - *Explanation:* Incorrect for a streamed UI: the user starts reading at 0.38 s.
- **B.** 13 ms per token (TPOT); it is the most precise.
  - *Explanation:* Incorrect. Precise, but not what a user perceives as waiting.
- **C.** 380 ms, the time to first token, because with streaming that is the silence before anything appears; report total duration and tokens per second alongside it for completeness.
  - *Explanation:* Correct. Perceived latency in a streaming interface is TTFT; Langfuse's `completion_start_time` and the GenAI convention's time-to-first-chunk exist to capture it.
- **D.** 76 tokens per second.
  - *Explanation:* Incorrect. Decode speed matters for long answers but is not the headline.

**Correct answer: C**

### Q10. Which of the following is the *only* appropriate place, among the four, for the raw arguments of a `reset_password` tool call?

*Domain: D2 · Related lecture: 5.5 Logs vs traces vs metrics for agents*

- **A.** As Prometheus labels on `atlas_tool_calls_total`.
  - *Explanation:* Incorrect. High-cardinality and sensitive; both rules broken.
- **B.** As a masked attribute (`gen_ai.tool.call.arguments`) on the tool span, via the `genai_attrs` helper that applies the PII mask.
  - *Explanation:* Correct. Traces are the home of per-request detail; masking is mandatory because the arguments contain an employee id.
- **C.** In an `INFO` log line without the trace id.
  - *Explanation:* Incorrect. Unmasked, uncorrelated logs are the worst of both worlds.
- **D.** In the span name.
  - *Explanation:* Incorrect. Names are not payloads and are not masked.

**Correct answer: B**

---

## D3: Cost engineering

### Q11. A Responses API call returns `usage.input_tokens = 4000`, `usage.input_tokens_details.cached_tokens = 3000`, `usage.output_tokens = 500`, `usage.output_tokens_details.reasoning_tokens = 300`. Model `gpt-5-mini`: input $0.25, cached $0.025, output $2.00 per million. What is the cost?

*Domain: D3 · Related lecture: 6.1 Where the money goes: token anatomy*

- **A.** $0.001325: 1,000 uncached × $0.25/M = $0.00025, 3,000 cached × $0.025/M = $0.000075, 500 output × $2.00/M = $0.001; reasoning tokens are inside the 500 output tokens and are not billed again.
  - *Explanation:* Correct. Cached tokens are a subset of input; reasoning tokens are a subset of output. Both details fields inform you; neither adds to the bill.
- **B.** $0.001925: as A plus 300 reasoning tokens at $2.00/M.
  - *Explanation:* Incorrect. Reasoning tokens are already counted in `output_tokens`.
- **C.** $0.002075: 4,000 × $0.25/M plus 3,000 × $0.025/M plus 500 × $2.00/M.
  - *Explanation:* Incorrect. Double-counts the cached tokens.
- **D.** $0.002000: 4,000 × $0.25/M plus 500 × $2.00/M, ignoring the cache.
  - *Explanation:* Incorrect. The cache discount is real and must be applied.

**Correct answer: A**

### Q12. Three levers are measured on the same replayed day (baseline $56.28): caching alone $37.00, diet alone $41.99, routing alone $47.07. A manager adds the three individual savings ($19.28 + $14.29 + $9.21 = $42.78) and expects $13.50. All three together cost $19.07. Why is the combined saving smaller than the sum?

*Domain: D3 · Related lecture: 6.8 Challenge: cut Atlas's daily cost by 40%*

- **A.** One of the replays used a different seed.
  - *Explanation:* Incorrect (assuming the same seed, which the challenge requires); the effect is structural.
- **B.** Routing is broken when caching is on.
  - *Explanation:* Incorrect. All three work; they overlap.
- **C.** Savings always add linearly; the replay is wrong.
  - *Explanation:* Incorrect. Savings on the same tokens do not add.
- **D.** The levers act on overlapping tokens: once caching has cut the price of the prefix and the diet has cut the number of history and tool-result tokens, there is less spend left for routing to move to a cheaper model, so its saving on top is much smaller than its $9.21 alone. Measure changes cumulatively in the order you will ship them, as Challenge 6.8 does.
  - *Explanation:* Correct. Caching and the diet happen to add almost exactly on this day ($22.71 together), but routing on top saves only $3.64. Each step's delta is measured against the previous step, not against baseline.

**Correct answer: D**

### Q13. A showback report shows tenant shares: ops 28%, eng 22%, hr 31%, finance 18%, and lists "escalated" as a feature costing 19% of the total. A department head says "so finance and escalations are 37% together". What is wrong?

*Domain: D3 · Related lecture: 6.3 Cost per request, session, user, tenant and feature*

- **A.** Nothing; percentages add.
  - *Explanation:* Incorrect. These percentages come from two different partitions of the same total.
- **B.** Tenant and feature are two independent breakdowns of the same 100%; the escalated 19% is spread across all four tenants, so adding a tenant share to a feature share double-counts. The correct view is a nested roll-up (tenant × feature), for example `rollup_nested(records, "tenant", "feature")`.
  - *Explanation:* Correct. Reports must say which partition each table is, and provide the cross-tab when readers will want to combine them.
- **C.** Escalations should not be a feature.
  - *Explanation:* Incorrect. Escalation is a legitimate cost driver worth its own row; the rule for precedence just has to be stated.
- **D.** Finance's share is wrong because finance escalates the most.
  - *Explanation:* Incorrect. Finance's 18% already includes its escalations.

**Correct answer: B**

### Q14. Which prompt layout maximises cache hits under OpenAI's prefix-based prompt caching, given a 1,900-token system prompt, 600 tokens of tool schemas, retrieved chunks, conversation history and the new question?

*Domain: D3 · Related lecture: 6.4 Prompt caching: the cheapest win*

- **A.** Question, history, chunks, tools, system prompt (most relevant first).
  - *Explanation:* Incorrect. The variable content comes first, so the prefix differs on every request and nothing is cached.
- **B.** System prompt with the current date and user name embedded, then tools, chunks, history, question.
  - *Explanation:* Incorrect. Embedding the date or user name in the system prompt makes the prefix unique per user or day; move them to the end.
- **C.** Static system prompt, then static tool schemas (together about 2,500 tokens, above the minimum), then retrieved chunks, then history, then the question, with `prompt_cache_key` set per tenant so requests with the same static prefix route to the same cache.
  - *Explanation:* Correct. Caching matches the longest common prefix; everything that varies goes after everything that does not. Measure `cache_read_input_tokens` before and after.
- **D.** Chunks first because retrieval is the largest block.
  - *Explanation:* Incorrect. Chunks vary per question, so putting them first breaks the prefix.

**Correct answer: C**

### Q15. `BudgetGuard` for tenant `hr` has soft cap $25, hard cap $40 over 24 hours. Spend so far today is $24.90 and the next request is estimated at $0.20. What does `decide()` return and what should the request path do?

*Domain: D3 · Related lecture: 6.7 Budgets and anomaly alerts per tenant*

- **A.** `DEGRADE`: projected spend $25.10 is at or above the soft cap and below the hard cap, so serve the request with the cheaper model and tighter context budget, increment `atlas_budget_decisions_total{decision="degrade"}`, and keep going.
  - *Explanation:* Correct. Soft cap degrades, hard cap refuses. Pre-charging the estimate means the decision considers the request about to be made, not only past spend.
- **B.** `ALLOW`: $24.90 is under $25.
  - *Explanation:* Incorrect if the estimate is pre-charged: $24.90 + $0.20 ≥ $25.
- **C.** `REFUSE`: any cap crossing refuses.
  - *Explanation:* Incorrect. Only the hard cap refuses; that is the point of having two.
- **D.** An exception, because the budget is exhausted.
  - *Explanation:* Incorrect. Budget decisions are data, not errors.

**Correct answer: A**

### Q16. An EWMA detector (alpha 0.3, threshold 3.0, warm-up 5) watches hourly spend. After ten stable hours between $1.80 and $2.20 (running mean $1.99, running std about $0.09), hour A comes in at $2.20 and, on a separate day with the same history, hour B comes in at $2.45. Which is flagged?

*Domain: D3 · Related lecture: 6.7 Budgets and anomaly alerts per tenant*

- **A.** Both, because both are above the mean.
  - *Explanation:* Incorrect. Being above the mean is not an anomaly; being more than `threshold` running standard deviations away is.
- **B.** Neither, because the detector is still warming up.
  - *Explanation:* Incorrect. Warm-up is five points; ten have been seen.
- **C.** Hour A only, because $2.20 is the top of the historical range.
  - *Explanation:* Incorrect. $2.20 deviates $0.21, about 2.3 standard deviations, under the threshold of 3; a value inside the historical range is not flagged.
- **D.** Hour B only: $2.45 deviates $0.46, about 4.9 running standard deviations on such a stable history, so it is flagged even though it is only 23% above baseline; hour A is not. The lesson is that the threshold is in standard-deviation units, so a very stable history makes the detector sensitive to small absolute changes, which is why `budget.py` also keeps absolute soft and hard caps and a minimum-std guard.
  - *Explanation:* Correct. Coding exercise CE3's solution gives exactly these z-scores. Tune `alpha` (memory) and `threshold` (sensitivity) per tenant, and pair the detector with absolute caps so a noisy tenant does not hide a real spike and a quiet tenant does not page on noise.

**Correct answer: D**

### Q17. Which statement about small-model-first routing is supported by the course's measurements?

*Domain: D3 · Related lecture: 6.6 Small-model-first routing with LiteLLM Router*

- **A.** Routing saves the most money of the three cost controls.
  - *Explanation:* Incorrect. On the replayed day caching alone saves 34% and the diet 25%; routing alone saves 16% ($56.28 → $47.07).
- **B.** Routing's saving is bounded by the share of traffic in the intents it moves: a third of generations (6,700 of 20,087, the simple intents) move to gpt-4.1-nano at a quarter of mini's price, which is 16% of the day; and because it changes which model answers, it is the lever that needs a quality number per intent next to it.
  - *Explanation:* Correct. Know your model and intent mix before you expect a saving, and keep `atlas.intent` on every span so a quality drop on one intent can be moved back to mini with one line in `SIMPLE_INTENTS`.
- **C.** Routing has no possible quality cost, so it needs no measurement.
  - *Explanation:* Incorrect. The offline judge scores were unchanged, but a smaller model can be worse on real traffic; that is why the decision is made per intent and measured.
- **D.** The router should fall back to gpt-4.1 when the mini model is slow.
  - *Explanation:* Incorrect. Atlas's `FALLBACKS` send gpt-4.1-mini to gpt-4o-mini, a different family at a lower price; making the expensive model the default fallback turns an outage into a cost incident.

**Correct answer: B**

---

## D4: Latency and reliability

### Q18. Sample of nine request durations in ms: 800, 850, 900, 950, 1,000, 1,100, 1,200, 3,900, 6,000. Using linear interpolation (rank = p/100 × (n−1)), what is p95, and does it pass a 4,000 ms budget?

*Domain: D4 · Related lecture: 7.2 Code-along: measure TTFT, TPOT and p95 from spans*

- **A.** 3,900 ms; passes.
  - *Explanation:* Incorrect. Rank 0.95 × 8 = 7.6 lies between index 7 (3,900) and index 8 (6,000).
- **B.** 6,000 ms; fails.
  - *Explanation:* Incorrect. That would be p100 (the max).
- **C.** 3,900 + 0.6 × (6,000 − 3,900) = 5,160 ms; fails the 4,000 ms budget even though only one request exceeded 4,000 ms, because the sample is small and the tail is heavy.
  - *Explanation:* Correct. This is the definition coding exercise CE2 implements. Small samples make p95 volatile, which is why the gate runs over a full replayed day.
- **D.** 1,855 ms (the mean); passes.
  - *Explanation:* Incorrect. The mean is not a percentile and hides the two slow requests.

**Correct answer: C**

### Q19. A per-call timeout of 4 s, `num_retries=1` and a fallback to `gpt-4.1-nano` are configured. The primary is slow (every call takes 9 s). Without a circuit breaker, what does a typical request look like, and what does an open breaker change?

*Domain: D4 · Related lecture: 7.4 Fallbacks and circuit breakers with the Router*

- **A.** Without a breaker: primary times out at 4 s, fallback answers in about 1.2 s, total about 5.2 s per request, over the 4 s budget; with the breaker open, requests skip the primary and complete in about 1.2 s.
  - *Explanation:* Correct. The breaker's job is to stop paying the timeout once the provider is known to be slow; that is the slow-call rule Lab 4 asks you to add, since the shipped breaker counts only errors.
- **B.** Without a breaker the fallback never runs.
  - *Explanation:* Incorrect. Fallback runs after the timeout error.
- **C.** With the breaker open, all requests fail fast.
  - *Explanation:* Incorrect. Open breaker on one deployment routes to the other deployment; users are served.
- **D.** The retry makes it faster.
  - *Explanation:* Incorrect. A retry against the same slow primary adds another 4 s before the fallback.

**Correct answer: A**

### Q20. Which retry policy for `lookup_ticket` (a read) and `create_ticket` (a write) matches lecture 7.3?

*Domain: D4 · Related lecture: 7.3 Timeouts, retries and backoff done right*

- **A.** Retry both up to five times immediately.
  - *Explanation:* Incorrect. Immediate retries synchronise into storms, and writes must not be repeated blindly.
- **B.** Never retry either.
  - *Explanation:* Incorrect. A bounded, backed-off retry on an idempotent read recovers transient failures cheaply.
- **C.** Retry the write, not the read, because writes matter more.
  - *Explanation:* Incorrect. Importance is not the criterion; safety of repetition is.
- **D.** Retry the read once or twice with exponential backoff and jitter; retry the write only if it carries an idempotency key so a repeated attempt returns the existing ticket instead of creating another.
  - *Explanation:* Correct. Idempotency turns an unsafe retry into a safe one; without it, the retry storm creates duplicate tickets.

**Correct answer: D**

### Q21. During a provider incident, Atlas's fallback rate for `finance` is 80% and its judge `grounded` score in that window falls from 0.90 to 0.82. The on-call engineer wants to "fix" the fallback rate. What is the right framing?

*Domain: D4 · Related lecture: 7.6 Chaos demo: slow provider during peak*

- **A.** The fallback rate is a bug; disable the fallback.
  - *Explanation:* Incorrect. Disabling the fallback returns the timeouts and errors.
- **B.** The fallback rate is the system working: users are being served by the cheaper path during an outage; the quality dip is the known, temporary price of degraded mode. Alert on the breaker staying open too long (an incident that needs the provider, not the router) and report the quality delta honestly in the incident note.
  - *Explanation:* Correct. Reliability controls have a quality shadow; the job is to bound it and make it visible, not to hide it by turning the control off.
- **C.** Route fallbacks to gpt-4.1 to fix the quality dip.
  - *Explanation:* Incorrect. That trades a bounded quality dip for an unbounded cost spike.
- **D.** Raise the timeout so the primary succeeds more often.
  - *Explanation:* Incorrect. Longer timeouts push p95 back over budget.

**Correct answer: B**

### Q22. Atlas answers a step-limit stop and a guardrail refusal with HTTP 200 and an `outcome` field (`step_limit`, `guardrail`), and a budget refusal with HTTP 429 and `outcome="refused"`. Which reliability argument supports this design?

*Domain: D4 · Related lecture: 7.5 Rate limits, queues and graceful degradation*

- **A.** 5xx codes are deprecated.
  - *Explanation:* Incorrect. They are standard; the question is what they mean.
- **B.** Clients ignore status codes anyway.
  - *Explanation:* Incorrect. Clients and load balancers act on them, which is exactly why they must be accurate.
- **C.** These are *designed* outcomes, not server failures: the service did what it intended (stop, decline, refuse), so they are counted as their own outcome categories in the SLIs rather than as availability failures; and the budget refusal uses 429 because it is a quota decision the client should back off from, not a fault that a load balancer should retry elsewhere.
  - *Explanation:* Correct. Graceful degradation means the response is honest and structured; the SLI distinguishes "failed" from "declined for a reason", and the status code tells the client what to do next.
- **D.** 200 hides problems from the dashboard, which reduces alert noise.
  - *Explanation:* Incorrect. Hiding is not the goal; the `outcome` label on `atlas_requests_total` keeps them visible and countable.

**Correct answer: C**

---

## D5: Online evaluation and drift

### Q23. You judge 1,500 uniformly sampled traces per week with three G-Eval criteria on gpt-4.1-mini, at about 1,600 input and 120 output tokens per judge call. Estimate the weekly judge cost (input $0.40, output $1.60 per million).

*Domain: D5 · Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** About $3.74: 4,500 calls × (1,600 × $0.40/M + 120 × $1.60/M) = 4,500 × ($0.00064 + $0.000192) = 4,500 × $0.000832.
  - *Explanation:* Correct. Three criteria means three judge calls per trace. Report this next to serving cost so the judge's share is visible and tunable.
- **B.** About $1.25: 1,500 calls.
  - *Explanation:* Incorrect. Each criterion is its own judge call.
- **C.** About $37: the judge uses the expensive model.
  - *Explanation:* Incorrect. The judge model is configured as gpt-4.1-mini here.
- **D.** Zero; judging is included in the serving cost.
  - *Explanation:* Incorrect. Judge calls are separate LLM calls with their own usage.

**Correct answer: A**

### Q24. Two annotators (or two judge runs) disagree on 30% of pass/fail decisions for the `resolved` criterion. What should you do before building an alert on `resolved`?

*Domain: D5 · Related lecture: 8.2 Code-along: sampled LLM-as-judge on live traces*

- **A.** Alert anyway; the mean over thousands of traces cancels the noise.
  - *Explanation:* Incorrect. Systematic disagreement about what "resolved" means does not average out; it shifts the mean unpredictably when the traffic mix changes.
- **B.** Switch to thumbs-up rate instead.
  - *Explanation:* Incorrect. Feedback has survivorship bias and covers 8% of sessions.
- **C.** Lower the threshold until agreement rises.
  - *Explanation:* Incorrect. Moving the threshold changes what is called a pass, not how consistently it is judged.
- **D.** Tighten the criterion text with concrete, observable conditions (for example "the answer states the specific entitlement or ticket action, or explicitly hands off with a ticket id"), re-measure agreement (Cohen's kappa) on a fixed set, and only alert once agreement is acceptable; a criterion you cannot judge consistently cannot be alerted on.
  - *Explanation:* Correct. Measure agreement first (lecture 8.3's disagreement table is the starting point). Alerts on noisy judgements produce alert fatigue and eventually get muted.

**Correct answer: D**

### Q25. Week 1 vs week 2 drift report: `resolved` mean 0.92 → 0.91, PSI 0.02; answer length mean 96 → 95 tokens, PSI 0.31. How is a large PSI possible with an almost unchanged mean?

*Domain: D5 · Related lecture: 8.5 Drift detection: compare this week to last week*

- **A.** PSI is computed wrongly whenever means are close.
  - *Explanation:* Incorrect. PSI is a distribution comparison and is independent of the mean.
- **B.** The distribution's shape changed while its centre did not: for example answers became bimodal (many very short and some very long) instead of clustered around 95 tokens. PSI on binned distributions catches this; the mean cannot. Investigate by slicing (tenant, intent, prompt version).
  - *Explanation:* Correct. That is why the drift report uses PSI and not only deltas of means.
- **C.** Answer length is not a valid drift metric.
  - *Explanation:* Incorrect. It was the clearest signal in Incident 3.
- **D.** The baseline week was too short.
  - *Explanation:* Incorrect. A full week is the course's standard window.

**Correct answer: B**

### Q26. Which order of operations keeps Incident 3 from recurring when a new prompt version is written?

*Domain: D5 · Related lecture: 8.6 From bad trace to regression test*

- **A.** Promote to `production`, watch the judge for a week, roll back if needed.
  - *Explanation:* Incorrect. That is detection after exposure; the users are the test.
- **B.** Promote to `production` only if the author is confident.
  - *Explanation:* Incorrect. Confidence is what the v2 author had.
- **C.** Run the offline eval against the `atlas-failures` dataset (built from low-scoring production traces with `source_trace_id`), require it to pass, promote to `staging` and judge a day of shadow traffic, then move the `production` label; keep the drift alert as the backstop.
  - *Explanation:* Correct. The dataset makes last week's production failures this week's regression suite; labels make promotion and rollback deploy-free.
- **D.** Ask the judge to rewrite the prompt.
  - *Explanation:* Incorrect. The judge scores; it does not author.

**Correct answer: C**

### Q27. Feedback shows 950 thumbs-up and 312 thumbs-down in a week. The team proposes an alert "thumbs-down count > 300 per week". What is the better formulation?

*Domain: D5 · Related lecture: 8.3 Capturing user feedback that means something*

- **A.** Thumbs-down as a *rate* of sessions (2.0% this week vs 1.4% baseline), with a minimum-volume guard and evaluated as drift against the previous window, because a count scales with traffic and a fixed count alerts on growth rather than on quality.
  - *Explanation:* Correct. The same ratio-plus-guard principle as tool error alerts; and feedback rate is a targeting signal that should send you to the judge and the traces, not a verdict on its own.
- **B.** Thumbs-down count > 300, as proposed.
  - *Explanation:* Incorrect. Doubling traffic doubles thumbs-down with quality unchanged.
- **C.** Thumbs-up rate < 90%.
  - *Explanation:* Incorrect. Among clickers, the up/down mix is dominated by who clicks; use the population denominator (sessions).
- **D.** No alert; feedback is biased.
  - *Explanation:* Incorrect. Biased for measurement, useful for detection when expressed as a rate change.

**Correct answer: A**

---

## D6: Dashboards, SLOs and alerting

### Q28. An SLO says 99.5% of requests complete under 4 s over 30 days. Over the last 6 hours, 2.2% of requests exceeded 4 s. What is the 6-hour burn rate and which multi-window alert tier does it hit?

*Domain: D6 · Related lecture: 9.1 SLIs for agents that leadership understands*

- **A.** 0.44; no alert.
  - *Explanation:* Incorrect arithmetic: budget is 0.5%, observed 2.2%.
- **B.** 2.2; slow burn.
  - *Explanation:* Incorrect. Burn rate divides by the error budget (0.5%), not by 1%.
- **C.** 22; page immediately.
  - *Explanation:* Incorrect. 2.2 / 0.5 = 4.4, not 22.
- **D.** 4.4: observed 2.2% divided by the 0.5% budget; at that rate the monthly budget lasts about 6.8 days. With the course's tiers (fast burn 14.4× over 1 h and 5 m; slow burn 6× over 6 h and 30 m) this is *below* the slow-burn threshold, so it is a ticket or a warning, not a page, unless the shorter window is also elevated.
  - *Explanation:* Correct. Burn-rate alerting turns "how bad" and "how fast" into a single number and pages only when both windows agree.

**Correct answer: D**

### Q29. Histogram buckets for `atlas_request_latency_seconds` are `0.5, 1, 2, 4, 8, +Inf`. The p95 computed by `histogram_quantile` shows exactly 4.0 for an hour, then jumps to 6.3. What can and cannot you conclude?

*Domain: D6 · Related lecture: 9.2 Code-along: Prometheus metrics from Atlas*

- **A.** p95 was exactly 4,000 ms then exactly 6,300 ms.
  - *Explanation:* Incorrect. `histogram_quantile` interpolates within buckets; a value pinned at a boundary means the quantile fell at or just inside that bucket edge, not that it was exactly 4.0 s.
- **B.** You can conclude p95 crossed from at-or-under the 4 s bucket boundary into the 4 to 8 s bucket (a real budget breach), but the exact values are bucket-resolution estimates; for millisecond precision, query the spans. Choosing 4 s as a bucket boundary is what makes the breach unambiguous.
  - *Explanation:* Correct. Buckets at your budgets give exact answers to the question "is p95 over budget?", and approximate answers to everything else.
- **C.** The histogram is corrupted.
  - *Explanation:* Incorrect. This is normal behaviour.
- **D.** You should add a `user_id` label to see who caused it.
  - *Explanation:* Incorrect. Cardinality trap; use traces to find who.

**Correct answer: B**

### Q30. Which dashboard panel from lecture 9.3 most directly answers the engineering manager's Monday question "did Atlas earn its money last week"?

*Domain: D6 · Related lecture: 9.3 Grafana: the Atlas Ops dashboard*

- **A.** Requests per second by tenant.
  - *Explanation:* Incorrect. Volume, not value.
- **B.** p95 latency.
  - *Explanation:* Incorrect. Speed, not value.
- **C.** Cost per resolved session by tenant, next to its budget line, because it divides all spend by the sessions that actually helped someone and moves the wrong way when a cost cut also cuts resolution.
  - *Explanation:* Correct. It is the SLI that couples cost and quality; it is also the headline of the weekly report.
- **D.** Fallback count.
  - *Explanation:* Incorrect. Reliability detail, not value.

**Correct answer: C**

### Q31. An alert fires at 03:10: `AtlasTenantCostAnomaly tenant=ops`. The on-call engineer opens the runbook. What should its first section let them do within five minutes?

*Domain: D6 · Related lecture: 9.5 Alert rules and the runbook*

- **A.** Explain the theory of EWMA detection.
  - *Explanation:* Incorrect. Theory belongs in the course, not on the first page at 3 a.m.
- **B.** List every tenant's budget.
  - *Explanation:* Incorrect. Reference data, not action.
- **C.** Ask them to write a postmortem.
  - *Explanation:* Incorrect. Postmortems come after mitigation.
- **D.** Confirm the impact (which tenant, current hourly spend vs baseline, projected daily against the hard cap), find the mechanism (Ops Console: top sessions by cost in the last hour; model mix; tool result sizes; retries), and apply a bounded mitigation (lower the tenant's soft cap to force degraded mode, or disable the offending tool) with the metric that confirms it; escalation criteria follow.
  - *Explanation:* Correct. First five minutes: impact, mechanism, mitigation, each with where to look and what to run. That is the difference between a notification and an operation.

**Correct answer: D**

---

## D7: Privacy, security and governance

### Q32. A `mask=` function replaces emails and phone numbers but a Langfuse trace still shows `NW-10433` in a tool result. Where is the gap, and what is the fastest reliable check?

*Domain: D7 · Related lecture: 10.2 Code-along: masking in the SDK and the collector*

- **A.** Langfuse un-masks data on display; nothing to fix.
  - *Explanation:* Incorrect. Langfuse shows what it receives.
- **B.** The mask has no pattern for Northwind employee ids (`NW-` plus five digits), or the tool result bypassed the `genai_attrs` helper; the check is a unit test that feeds a string containing an email, a phone, an employee id and a Luhn-valid card through the mask and asserts all four are replaced (coding exercise CE4), plus an integration test asserting no `NW-` appears in any exported span attribute.
  - *Explanation:* Correct. Masking is code; code needs tests; and identifiers are domain-specific, so a generic PII library will miss them.
- **C.** Employee ids are not personal data.
  - *Explanation:* Incorrect. An identifier that resolves to a person is personal data.
- **D.** Set `sample_rate=0` to stop sending traces.
  - *Explanation:* Incorrect. That removes observability instead of fixing the mask.

**Correct answer: B**

### Q33. The collector's `attributes/redact` processor uses `action: hash` on `user.id` (and `delete` on message bodies and tool results). What does this achieve that `action: delete` would not, and what does it not achieve?

*Domain: D7 · Related lecture: 10.2 Code-along: masking in the SDK and the collector*

- **A.** It keeps a stable pseudonym so traces from the same user can still be grouped and joined, which `delete` would destroy; it does not achieve anonymisation, because the hash is deterministic and the data remains personal data requiring the same access controls and retention limits.
  - *Explanation:* Correct. Hash for joins, delete when joins are not needed; either way the raw value should already have been masked in the SDK.
- **B.** It encrypts the id so only Langfuse admins can read it.
  - *Explanation:* Incorrect. Hashing is one-way, not encryption with a key for reading back.
- **C.** It shortens the attribute to save storage.
  - *Explanation:* Incorrect. Size is incidental.
- **D.** It makes the data exempt from regulation.
  - *Explanation:* Incorrect. Pseudonymised data is still regulated.

**Correct answer: A**

### Q34. Northwind's counsel asks the platform team to "be able to show what the agent did for any HR request in the last six months". Which telemetry design decision satisfies this while respecting data minimisation?

*Domain: D7 · Related lecture: 10.4 Regulatory logging obligations (not legal advice)*

- **A.** Keep raw prompts and outputs for six months in a shared project.
  - *Explanation:* Incorrect. Raw PII for six months with broad access is the breach scenario of lecture 10.1.
- **B.** Delete everything after 30 days; six months is too long.
  - *Explanation:* Incorrect. If the obligation is real, deleting evidence is the opposite failure.
- **C.** Retain masked traces (release, prompt version, model, tool calls with masked arguments and results, decisions and scores) in a restricted HR project with six-month retention and role-based access, keep hashed identifiers for joins, keep raw application records in the systems of record rather than in telemetry, and confirm the classification and the period with counsel.
  - *Explanation:* Correct. The trace is the audit trail of *what the system did*; the systems of record hold *who*. Minimise in telemetry, retain what the obligation needs, separate access.
- **D.** Screenshot the Langfuse UI weekly.
  - *Explanation:* Incorrect. Not queryable, not complete, not an audit trail.

**Correct answer: C**

---

## D8: Incident response

### Q35. It is 10:20. Cost per resolved session for one tenant is up 45% since 09:00; requests are flat; p95 up 0.4 s; tool errors normal; judge normal. Which first query best separates the three candidate mechanisms (more steps, longer history, bigger tool results)?

*Domain: D8 · Related lecture: 11.1 How to read an incident like an SRE*

- **A.** Count of generations per hour.
  - *Explanation:* Incorrect. Flat requests with more steps would show here, but it says nothing about history or tool sizes.
- **B.** For the affected tenant, before vs after 09:00: mean steps per request, mean `atlas.context_tokens` at step 1, and mean tool-result length per tool; whichever moved is the mechanism, and only one query with three columns is needed.
  - *Explanation:* Correct. The three mechanisms have three distinct signatures on span attributes; compare before and after, then read three traces for confirmation.
- **C.** The OpenAI invoice.
  - *Explanation:* Incorrect. Invoices are daily totals with no mechanism.
- **D.** Restart Atlas and see if it stops.
  - *Explanation:* Incorrect. Destroys the timeline, proves nothing.

**Correct answer: B**

### Q36. In a postmortem, which "action item" would a reviewer send back as unverifiable?

*Domain: D8 · Related lecture: 11.5 Writing the postmortem*

- **A.** "Add `atlas_tool_result_bytes` histogram per tool (owner: agent team); verified when the panel shows data in Grafana."
  - *Explanation:* Incorrect (it is verifiable): artefact, owner role, check.
- **B.** "Lower the `lookup_ticket` error alert threshold to 5% (owner: platform); verified by the rule firing in the `retry_storm` replay."
  - *Explanation:* Incorrect (verifiable): rule change plus a reproducible test.
- **C.** "Add `test_retry_storm_cost_bounded` to `tests/budget/` asserting the `retry_storm` day costs at most 1.3× baseline (owner: agent team); verified by CI."
  - *Explanation:* Incorrect (verifiable): a gate that fails if the fix regresses.
- **D.** "Engineers should pay more attention to tool errors."
  - *Explanation:* Correct, this is the unverifiable one: no artefact, no owner, no check, and it blames attention rather than fixing the system that gave nobody a signal.

**Correct answer: D**

### Q37. Incident 4 (Project 2) presents two pages on one day: a `lookup_ticket` error-rate spike at 10:35 with sessions hitting the step limit, and a p95 doubling at 15:20 with tool errors back to normal and cost per request only slightly up. Judge scores are normal all day. Which hypothesis is the *last* one you should test, given the evidence?

*Domain: D8 · Related lecture: 11.6 Project 2: Investigate a fourth incident*

- **A.** "Judge scores dropped because of a prompt change" — quality is normal in both windows and `atlas.prompt_version` does not change all day; this hypothesis has the least support and goes last.
  - *Explanation:* Correct. Order hypotheses by how much the observed signals already support them: a tool error spike with step-limit sessions points at the tool loop first, a TTFT rise with unchanged tokens points at the provider first; a quality hypothesis contradicts a normal judge.
- **B.** "The model re-called a failing tool until the step limit" — plausible for the morning page.
  - *Explanation:* Incorrect as the last: this is the leading hypothesis for the 10:35 page (`execute_tool lookup_ticket` spans per trace, `error.type`, `atlas.steps`).
- **C.** "The provider got slow" — plausible for the afternoon page.
  - *Explanation:* Incorrect as the last: p95 up with tool errors normal and tokens unchanged is exactly what `atlas.ttft_ms` per hour would confirm.
- **D.** "More traffic" — two pages on one day suggest load.
  - *Explanation:* Incorrect as the last: it is quickly refuted by the flat request count per hour, which is why it goes first (fast to refute).

**Correct answer: A**

---

## D9: Portability, deployment and CI gates

### Q38. Atlas exports to the OTel Collector, which sends to Langfuse and to Phoenix. Langfuse is down for 12 minutes at 2 RPS. Which statement is true with the course's default configuration?

*Domain: D9 · Related lecture: 13.5 Chaos demo: kill the observability backend*

- **A.** Atlas requests fail for 12 minutes.
  - *Explanation:* Incorrect. The batch processor and collector are asynchronous; requests are unaffected.
- **B.** Every span is preserved and delivered when Langfuse returns.
  - *Explanation:* Incorrect. The Langfuse exporter retries each failed batch for at most 30 s (`retry_on_failure.max_elapsed_time`), then drops it.
- **C.** Atlas keeps serving with unchanged p95; Phoenix keeps receiving every sampled span; the Langfuse exporter retries each batch for up to 30 s and then drops it, so almost all of the 12 minutes is missing in Langfuse only, and the collector's own metrics (`otelcol_exporter_send_failed_spans`, port 8888) record the drops so you can alert on them.
  - *Explanation:* Correct. Drop telemetry, never requests; size `retry_on_failure` and `sending_queue` for your longest tolerable backend outage; alert on the dropping.
- **D.** The collector crashes when an exporter is unreachable.
  - *Explanation:* Incorrect. Exporters fail independently; the `memory_limiter` protects the collector.

**Correct answer: C**

### Q39. A pull request changes the retrieval `top_k` from 4 to 8. The CI budget gate replays the day and reports cost per session $0.0512 against a $0.05 budget and p95 2,300 ms against 4,000 ms. What happens and what is the correct engineering response?

*Domain: D9 · Related lecture: 13.3 Code-along: the CI budget gate*

- **A.** The PR merges because latency passed.
  - *Explanation:* Incorrect. Any budget breach fails the gate.
- **B.** `test_cost_per_session_within_budget` fails, so the required `budget gate` check goes red with the number in the assertion message; the author either finds a compensating saving (for example tighter tool-result truncation), justifies raising the budget in the PR with the quality evidence for `top_k=8`, or drops the change; the gate is not bypassed.
  - *Explanation:* Correct. The gate makes cost a first-class review criterion. Raising the budget is allowed, but as a visible, argued decision, not a workaround.
- **C.** The author sets `ATLAS_TOP_K=4` in CI only, so the gate passes.
  - *Explanation:* Incorrect. Testing a different configuration from the one you ship defeats the gate.
- **D.** The gate is disabled because the difference is small.
  - *Explanation:* Incorrect. 2.4% over budget on every session, every day, is exactly what accumulates into the "38% month on month" Project 1 starts with.

**Correct answer: B**

### Q40. Which combination gives Northwind the *least* lock-in while keeping Langfuse's prompt management and datasets today?

*Domain: D9 · Related lecture: 12.1 Vendor lock-in and the OTel escape hatch*

- **A.** Use only Langfuse's `@observe` and never OpenTelemetry attributes.
  - *Explanation:* Incorrect. The Langfuse SDK is OTel underneath, but relying on its decorators alone without GenAI attributes makes spans less portable to other backends.
- **B.** Use Prometheus only and skip traces.
  - *Explanation:* Incorrect. Metrics cannot explain a single request; and prompts and datasets need an LLM-native tool.
- **C.** Store prompts in code and skip Langfuse features.
  - *Explanation:* Incorrect. That avoids lock-in by giving up the features the question requires.
- **D.** Emit OpenTelemetry spans with GenAI semantic conventions through the collector (so traces can fan out to any backend at any time), use Langfuse for prompts, scores and datasets knowing those are backend state, and keep export scripts for scores and datasets plus prompts versioned in git as a mirror, so the switching cost is known and bounded.
  - *Explanation:* Correct. Portability is a design property of the wire format plus an honest inventory of what is not portable and how you would move it.

**Correct answer: D**
