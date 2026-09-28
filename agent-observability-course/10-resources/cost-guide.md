# Cost Guide

**Used in:** 2.1 (accounts and caps), 6.1 (token anatomy), 6.2 (price table), 6.9 (showback project), 12.4 (cost of observability add-ons)

> **Check current pricing.** Every price and free-tier detail in this space changes often: model launches, renames, plan changes, new token types. **This guide contains no vendor prices on purpose.** It tells you *how each vendor charges*, *where to look*, *which usage fields to read*, and *how to compute cost per request, session and tenant*, and it gives you a table to fill in on the day you start. The course's overall student estimate is **about $5-15 in total** (curriculum), because every lab has an offline path, but **check current pricing**, since it may be different when you take the course.

---

## 1. How each vendor charges (units)

| Vendor (course default) | Role | Pricing unit (typical; check current pricing) | Free tier / caps (check current pricing) | Where it shows up in `src/northwind/pricing.py` / `cost.py` |
|---|---|---|---|---|
| OpenAI `gpt-4.1-mini` (Atlas default) | LLM | Per 1M **input** tokens, per 1M **output** tokens; **cached input** tokens usually at a lower rate | Pay-as-you-go; set a **hard monthly cap** on the project (2.1) | `input_cost_per_token`, `output_cost_per_token`, cache-read rate |
| OpenAI `gpt-4.1` (escalation) | LLM | Same structure, higher rates | Same | Same, per-model row |
| OpenAI `gpt-5-mini` (routing demos) | LLM | Same structure; **reasoning tokens** are billed as output tokens | Same | `output_tokens_details.reasoning_tokens` counted as output |
| Judge model (DeepEval G-Eval, 8.2) | Evaluation | Same as the LLM line for whichever model judges | Same | A separate line item ("judge") in the showback, never hidden in Atlas's cost |
| Langfuse Cloud | Tracing backend | Free tier with monthly unit/event limits; paid tiers by volume (check) | Free tier (check) | Excluded from per-request cost; tracked as "cost of observability" (4.6) |
| Langfuse self-hosted (13.1) | Tracing backend | Your infrastructure only | $0 software | Same |
| LangSmith, Arize Phoenix (Section 12) | Alternative backends | LangSmith: free tier + paid by traces/seats (check); Phoenix: open source, self-host $0 | Check | Same |
| Datadog LLM Observability (12.4, conceptual) | Enterprise APM add-on | Typically usage-based on top of an APM subscription (check) | n/a | Decision matrix only |
| Prometheus, Grafana, OTel Collector, LiteLLM, DeepEval, Streamlit | Open source | $0 software | | |

> **Cached tokens and reasoning tokens matter.** The two most common mistakes in a home-made price table are (1) charging cached input at the full input rate, which over-reports cost after you add caching in 6.4, and (2) forgetting reasoning tokens on reasoning models, which under-reports cost by a lot. `pricing.py` handles both; check its dated fallback table against the pricing page.

## 2. Which usage fields to read (lecture 6.1)

| API | Field | Meaning | Feeds |
|---|---|---|---|
| Chat Completions | `usage.prompt_tokens` | Total input tokens (includes cached) | input |
| Chat Completions | `usage.completion_tokens` | Output tokens (includes reasoning on reasoning models) | output |
| Chat Completions | `usage.prompt_tokens_details.cached_tokens` | The cached portion of input | cache read (cheaper) |
| Responses | `usage.input_tokens`, `usage.output_tokens` | Same idea | input, output |
| Responses | `usage.input_tokens_details`, `usage.output_tokens_details` | Cached input breakdown; reasoning output breakdown | cache read; reasoning |
| Both | `prompt_cache_key` (request parameter) | Groups requests so stable prefixes hit the cache | not a usage field, but the lever in 6.4 |

Map them to GenAI semantic-convention attributes with `telemetry/genai_attrs.py` (see `genai-semconv-cheatsheet.md`).

## 3. Fill in your price table (date: __________)

| Model | Input per 1M tokens | Cached input per 1M | Output per 1M | Reasoning billed as | Source URL (pricing page) |
|---|---|---|---|---|---|
| `gpt-4.1-mini` | | | | output | |
| `gpt-4.1` | | | | output | |
| `gpt-5-mini` | | | | output | |
| Judge model: ________ | | | | | |

Put the same values into the pinned fallback in `src/northwind/pricing.py` (lecture 6.2) with the date, and prefer `litellm.model_cost` at runtime when it has the model.

## 4. Cost formulas (lectures 6.2, 6.3)

```
cost_per_generation = (uncached_input_tokens × input_rate
                     + cached_input_tokens   × cache_read_rate
                     + output_tokens         × output_rate) / 1e6
                     # reasoning tokens are already inside output_tokens

cost_per_request  = Σ generations in the request (including retries and the escalation model)
cost_per_session  = Σ requests with the same session_id
cost_per_user     = Σ sessions with the same user_id
cost_per_tenant   = Σ users (or Σ generations tagged tenant=<name>)
cost_per_feature  = Σ generations tagged feature=<kb_answer | ticket | password_reset | shipment>

cost_per_resolved_session = cost_per_tenant / resolved_sessions_in_tenant   # the manager's number
cost_of_observability     = judge calls + backend fees (kept as separate lines)
```

**Worked example with made-up round numbers (NOT real prices):** a session with three requests; the requests contain 1,200 / 1,500 / 1,800 input tokens (of which 900 / 900 / 900 cached), 180 / 200 / 220 output tokens, no reasoning. Hypothetical rates: input $0.40 per 1M, cached input $0.10 per 1M, output $1.60 per 1M.

- Request 1: (300 × 0.40 + 900 × 0.10 + 180 × 1.60) / 1e6 = $0.000498
- Request 2: (600 × 0.40 + 900 × 0.10 + 200 × 1.60) / 1e6 = $0.000650
- Request 3: (900 × 0.40 + 900 × 0.10 + 220 × 1.60) / 1e6 = $0.000802
- **Session ≈ $0.00195** (hypothetical). Notice the uncached input grows each turn because history is re-sent; that is the context-bloat curve of Incident 1 in miniature.

The exercise shows *which lines dominate* with your real prices. In most agent workloads, **re-sent history** and **retries** dominate, not output. Check this with your own numbers in the Ops Console.

## 5. Keeping your course spend low (lecture 2.1)

- [ ] **Set a hard monthly cap** on the OpenAI project you use for the course, before running anything live.
- [ ] Use `OFFLINE=1` for every lab first. The mock LLM produces realistic usage numbers and latencies at zero cost; the Ops Console and Langfuse fill up from the replay.
- [ ] Run the live path only where the lecture says "live" (2.3, parts of 6.6, 8.2, 13.5).
- [ ] Cap the online judge with `JUDGE_MAX_CALLS` and a sample rate ≤ 10% while learning (8.2).
- [ ] Watch the Langfuse Cloud free-tier limits; a full replayed day is a lot of spans. Lower the replay's RPS or use `sample_rate` (4.6) if you approach the limit.
- [ ] Revoke keys you no longer need.

## 6. Cost of observability itself (lectures 4.6, 12.4)

| Line | How it's charged (typical; check) | How to bound it |
|---|---|---|
| Trace volume in the backend | Events/units per month | `sample_rate`, tail sampling in the collector (13.2), shorter retention (10.3) |
| Judge calls | LLM tokens | Sample rate, cheaper judge model, judge only on flagged traces |
| Metrics | Storage by series count | Low-cardinality labels only (5.5) |
| APM add-ons | Per-host or per-span pricing on top of the APM contract (check) | Route only what you need through the collector; keep the rest in Langfuse |

Report these as their own lines in the showback (Project 1). Observability that costs more than the savings it finds is a finding too.
