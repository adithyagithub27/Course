# Quiz: Cost Engineering (Section 6)

| Field | Value |
|---|---|
| Udemy lecture | 6.10 Quiz: Cost engineering |
| Questions | 8 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 6.1 to 6.9 |

---

### Q1. An OpenAI Chat Completions response reports `usage.prompt_tokens = 1200`, `usage.prompt_tokens_details.cached_tokens = 900`, `usage.completion_tokens = 180`. Prices for gpt-4.1-mini: input $0.40, cached input $0.10, output $1.60 per million tokens. What is the cost of this call?

*Related lecture: 6.1 Where the money goes: token anatomy*

- **A.** $0.000498 (300 uncached input at $0.40 = $0.00012, plus 900 cached at $0.10 = $0.00009, plus 180 output at $1.60 = $0.000288).
  - *Explanation:* Correct. `cached_tokens` is a subset of `prompt_tokens`; only the remainder is billed at the full input price. Getting this wrong overstates cost on cache-heavy traffic by up to 25 percent, which is why coding exercise CE1 tests exactly this case.
- **B.** $0.000768 (1,200 at $0.40 plus 180 at $1.60, ignoring the cache).
  - *Explanation:* Incorrect. Ignoring the cache overstates the cost; the provider did give the discount.
- **C.** $0.000378 (900 cached at $0.10 plus 180 output; uncached input is free).
  - *Explanation:* Incorrect. The 300 uncached input tokens are billed at the input price.
- **D.** $0.000846 (1,200 input at $0.40 plus 900 cached at $0.10 plus 180 output).
  - *Explanation:* Incorrect. This double-counts the cached tokens: they are already part of the 1,200 prompt tokens.

**Correct answer: A**

---

### Q2. `pricing.py` uses `litellm.model_cost` as its price source but also ships a pinned fallback table. Why both?

*Related lecture: 6.2 Code-along: a price table you can trust*

- **A.** LiteLLM's table is often wrong, so the fallback is the real source.
  - *Explanation:* Incorrect. LiteLLM's table is well maintained and updated quickly; it is the preferred live source.
- **B.** The live table is comprehensive and current but is an external dependency that can be missing, offline or change under you; the pinned table makes offline mode, tests and the CI budget gate deterministic and lets you record which price version a report used.
  - *Explanation:* Correct. A showback report has to state "prices as of <date>"; a deterministic gate cannot depend on a package update changing cost per session overnight. Per-model overrides handle negotiated or custom prices.
- **C.** LiteLLM only prices OpenAI models.
  - *Explanation:* Incorrect. LiteLLM prices hundreds of models across providers.
- **D.** The fallback table is used for reasoning tokens, which LiteLLM does not price.
  - *Explanation:* Incorrect. Reasoning tokens are billed as output tokens and both sources handle that; the fallback is about determinism and availability.

**Correct answer: B**

---

### Q3. Over a week, Atlas served 5,410 sessions for $246.10; 4,980 of the sessions ended `resolved`. Finance asks for "cost per session" and the engineering manager asks for "cost per resolved session". What are the numbers and why does the course make the second one the headline?

*Related lecture: 6.3 Cost per request, session, user, tenant and feature*

- **A.** Neither can be computed without user feedback.
  - *Explanation:* Incorrect. `resolved` is the agent's outcome attribute; feedback and judge scores refine it but are not required for the roll-up.
- **B.** Both are $0.0455, because unresolved sessions are free.
  - *Explanation:* Incorrect. Unresolved sessions still consume tokens; they are in the numerator either way.
- **C.** Cost per session $0.0455; cost per resolved session $0.0494. The second divides all spend, including failed and handed-off sessions, by the sessions that actually delivered value, so a cost-cutting change that also lowers resolution shows up as *worse*, not better.
  - *Explanation:* Correct. $246.10 / 5,410 = $0.0455 and $246.10 / 4,980 = $0.0494. Cost per resolved session couples cost to quality in one number; it is the SLI leadership can act on (lecture 9.1).
- **D.** Cost per session $0.0494; cost per resolved session $0.0455.
  - *Explanation:* Incorrect. Swapped: dividing by a smaller denominator (resolved sessions) gives the larger number.

**Correct answer: C**

---

### Q4. You enable prompt caching but `cache_read_input_tokens` stays at zero on almost every generation. Which is the most likely cause?

*Related lecture: 6.4 Prompt caching: the cheapest win*

- **A.** Caching only works with the Responses API.
  - *Explanation:* Incorrect. Both Chat Completions and Responses report cached tokens and accept `prompt_cache_key`.
- **B.** Output tokens are too long to cache.
  - *Explanation:* Incorrect. Prompt caching concerns input tokens only; output length is irrelevant.
- **C.** Caching requires a paid enterprise tier.
  - *Explanation:* Incorrect. Prompt caching is automatic on supported models for prompts above the minimum length.
- **D.** The prompt's prefix is not stable: something variable (a timestamp, the user's name, the retrieved chunks) sits *before* the long static system instructions, so the cacheable prefix is shorter than the minimum, or differs on every request.
  - *Explanation:* Correct. Caching matches on an exact prefix of at least about 1,024 tokens. Put the static system prompt and tool schemas first, variable content (retrieval, history, the question) last, and use `prompt_cache_key` so related requests route to the same cache. Then measure `cached_tokens` before and after on the same replayed day.

**Correct answer: D**

---

### Q5. The context diet in lecture 6.5 applies two operations before each model call: truncate tool results to a token budget, then trim the oldest history to a total budget while keeping the system message and the latest message. Why that order, and what must never be dropped?

*Related lecture: 6.5 The context diet*

- **A.** Truncate tool results first, because oversized tool payloads are the biggest single contributor and shrinking them loses no conversational turns; then trim history oldest-first. The system message (which is also the cached prefix) and the most recent message are always kept.
  - *Explanation:* Correct. This is the pipeline in coding exercise CE5 and `northwind.tokens.context_diet`. It also compounds with caching: a stable, kept system prefix stays cacheable while the variable tail shrinks.
- **B.** Summarise everything with another LLM call first.
  - *Explanation:* Incorrect as the default: summarisation costs a call and adds latency; it is a later, optional step for long sessions, not the first move.
- **C.** Drop the latest user message if it is long; the model can infer it from history.
  - *Explanation:* Incorrect. The latest message is the request; without it the call is meaningless.
- **D.** Trim history first, because it is the largest; the system message can be dropped once the model has "learned" it.
  - *Explanation:* Incorrect. The model has no memory between calls; dropping the system prompt removes the instructions and also breaks the cached prefix.

**Correct answer: A**

---

### Q6. Atlas runs a LiteLLM `Router` with `gpt-4.1-mini` as default and `gpt-4.1` as the escalation model, used when a sensitive request (grievance, legal, medical) needs it. On the baseline day 0.4% of requests escalate, and with `ATLAS_ROUTER_MODE=1` a third of generations run on gpt-4.1-nano. A student proposes routing *everything* through `gpt-4.1` "for quality" and another proposes never escalating. What does the course's evidence say?

*Related lecture: 6.6 Small-model-first routing with LiteLLM Router*

- **A.** Route everything to gpt-4.1: quality is priceless.
  - *Explanation:* Incorrect. At 5× the price per token, the day would cost roughly 4 to 5× more for a judge score change the course measures as negligible on routine policy questions.
- **B.** Small-model-first with intent-based routing and signal-based escalation: nano handles the simple intents (a third of generations) at a quarter of mini's price, mini handles the policy questions, gpt-4.1 handles the cases where the judge shows it matters, and the trade-off is measured on the same replayed day (lecture 6.6 measures −16% for routing alone, $56.28 → $47.07, with the judge scores unchanged).
  - *Explanation:* Correct. The Router also gives fallbacks and cooldowns for reliability (Section 7). The decision is empirical: measure cost and judge score per routing policy on the same seed.
- **C.** Never escalate: gpt-4.1-mini is good enough for everything.
  - *Explanation:* Incorrect. The escalation path (an employee asking for a person, the `[ESCALATE]` marker on grievance, legal or medical requests) is 0.4% of requests and $0.38 of the $56.28 day; dropping it saves almost nothing and removes the careful answer exactly where a wrong one is most expensive.
- **D.** Alternate models randomly to average out cost.
  - *Explanation:* Incorrect. Random routing buys the average cost with none of the targeting; quality on hard cases still suffers half the time.

**Correct answer: B**

---

### Q7. `budget.py` gives each tenant a soft cap and a hard cap over a rolling 24-hour window plus an EWMA anomaly detector. Which describes the intended behaviour at each threshold?

*Related lecture: 6.7 Budgets and anomaly alerts per tenant*

- **A.** Caps are per user, not per tenant, because users spend the money.
  - *Explanation:* Incorrect for Atlas's design: budgets are owned and paid per department (tenant); per-user caps are a possible extension (capstone "what I would do next").
- **B.** Soft cap: log a warning; hard cap: log an error; anomaly: log at debug level.
  - *Explanation:* Incorrect. Logging is not a control; nothing changes for the tenant or the spend.
- **C.** Soft cap ($25 by default): degrade (gpt-4.1-nano, top-k 2) and keep serving; hard cap ($40): refuse politely before any model call (the server returns 429); EWMA anomaly: flag requests whose cost is far above the tenant's own smoothed history even if no cap is near, because a cap catches runaway spend only hours later.
  - *Explanation:* Correct. Degrade, refuse and alert are three different responses to three different situations. The refusal must happen *before* the LLM call (capstone AT-14), and degrade and refuse each increment `atlas_budget_decisions_total{decision=...}` (an `anomaly` increment is a capstone extension, not shipped).
- **D.** Soft cap and hard cap both refuse; the anomaly detector raises the caps automatically.
  - *Explanation:* Incorrect. A soft cap that refuses is just a lower hard cap, and auto-raising caps defeats the purpose.

**Correct answer: C**

---

### Q8. In Challenge 6.8 a student reports a 73% saving ($56.28 → $15.06) by adding `ATLAS_TOP_K=2` on top of caching, the context diet and routing, and points out that the offline judge scores did not move. The reference ships only the first three (−66%, $19.07). What is the reasoning?

*Related lecture: 6.8 Challenge: cut Atlas's daily cost by 40%*

- **A.** `top_k` cannot be changed without a redeploy.
  - *Explanation:* Incorrect. `ATLAS_TOP_K` is configuration; the objection is evidence about quality, not mechanics.
- **B.** Retrieval is free, so `top_k` has no cost effect.
  - *Explanation:* Incorrect. Each retrieved chunk adds input tokens to every later generation in the request; that is where the extra $4 came from.
- **C.** −73% exceeds the −40% target, so the reference is being conservative for no reason.
  - *Explanation:* Incorrect. The target had two parts: cost at or below $33.77 *and* quality held (resolved ≥ 0.872, grounded ≥ 0.923). The reference already meets both without the change.
- **D.** The offline heuristic judge does not read the retrieved context, so "scores unchanged" is not evidence for a retrieval change; `grounded` is where cutting top-k would show, and it needs the real judge with `retrieval_context` before shipping. A saving without quality evidence is rejected for now and documented.
  - *Explanation:* Correct. Each change is measured on the same seed and accepted only if both criteria are proven. The other rejected change, `ATLAS_MAX_STEPS=1` ($6.16), shows the opposite case: the quality cost is visible at once (resolved 0.892 → 0.157).

**Correct answer: D**
