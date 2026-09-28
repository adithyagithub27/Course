# Latency Budget Worksheet

**Course:** AI Agent Observability & Cost Control · **Used in:** 7.1 (set the budget), 7.2 (measure it), 7.6 and Lab 4 (hold it under chaos), 5.4 (streaming metrics), 9.1 (as an SLI)

> An agent's latency is not one number. It is a **per-step** budget (each LLM call and tool call) inside an **end-to-end** budget (from the user's request to the final answer), and for streaming agents it also includes **time to first token**, which is what the user feels. This course uses **4 seconds end-to-end at p95** as the *example* budget for Atlas over HTTP (Lab 4's target). Set your own target and measure it. Don't assume it. If you took the voice course, its ≈800 ms voice-to-voice budget is the same idea with much tighter numbers.

---

## 1. The stages of one agent step

```
request arrives
│
├─ [Q] Queue / rate-limit wait (per-tenant concurrency, 429 backoff)
├─ [R] Retrieval (search_knowledge_base: BM25 or vector lookup)
├─ [F] LLM time to first token (TTFT)
├─ [O] LLM output: time per output token (TPOT) × output tokens
├─ [T] Tool call (lookup_ticket, create_ticket, reset_password, check_shipment)
├─ [X] Retries / fallbacks (each adds a whole [F]+[O] again, or a timeout first)
│
next step (the agent loops until done or step limit)  ◄── end-to-end = Σ steps + overhead
```

Stages can overlap only a little in an agent (a tool result is needed before the next generation), so **steps add up**. An agent with six "fast" 700 ms steps is a 4-second agent.

| Stage | What to read | What you control |
|---|---|---|
| Q. Queue | Time between request receipt and first span start; 429 count | Per-tenant concurrency, shedding low-priority traffic (7.5) |
| R. Retrieval | Retriever span duration | Index type, top-k (Incident 2 is a top-k change), caching |
| F. TTFT | `gen_ai.response.time_to_first_chunk` on the generation span; `completion_start_time` in Langfuse | Model choice, prompt length (context diet), provider region, routing (6.6) |
| O. TPOT × tokens | Generation span duration minus TTFT, divided by output tokens | Output length instructions, model choice |
| T. Tool | Tool span duration | Tool implementation, timeouts, idempotency |
| X. Retries / fallbacks | Retry events on the span; fallback events (7.4) | Bounded retries with jitter, timeouts, circuit breaker |
| Steps | Count of step spans per trace | Step limit (5.2), better tool descriptions, escalation model |

## 2. Set your budget

Fill in your target per stage. The "example" column is **illustrative only**, a starting split for a 4 s end-to-end p95 target with a 3-step agent, not a benchmark. Replace it with your measurements from `make report` and the Ops Console latency page.

| Stage | Example split (illustrative) | Your target (ms) | Measured p50 (ms) | Measured p95 (ms) | Over budget? |
|---|---|---|---|---|---|
| Q. Queue | 50 | | | | |
| R. Retrieval | 150 | | | | |
| F. TTFT (per generation) | 600 | | | | |
| O. Output (per generation) | 400 | | | | |
| T. Tool call (per tool) | 300 | | | | |
| X. Retries / fallbacks | 0 in budget (alert if > 5% of requests) | | | | |
| Steps per request (count) | 3 | | | | |
| **End-to-end p95** | **≈4,000** | | | | |
| **TTFT of the first generation** (what the user feels) | 600 | | | | |

**Rules of thumb (for thinking, not measurements):**

- **Use p95 for budgets, not averages.** The slow requests are the ones that become tickets (7.1).
- **Steps are the biggest lever.** Halving the average step count usually beats every other optimisation.
- **A retry storm is a latency event and a cost event at once** (7.3, Incident 1). Budget zero retries and alert on the rate.
- **Fallbacks cost latency before they save it.** A fallback fires after a timeout; the timeout is on your critical path (7.4).
- **Stream, and measure TTFT separately.** A 4 s answer that starts in 600 ms feels fast; a 2 s answer that starts at 2 s feels slow (5.4).

## 3. Scenario comparison (fill in during Lab 4 / lecture 7.6)

| Scenario | Steps p50 | End-to-end p50 | End-to-end p95 | Fallback rate | Cost delta | Notes |
|---|---|---|---|---|---|---|
| Baseline day (offline replay) | | | | | | |
| `slow_provider` injected, no tuning | | | | | | |
| `slow_provider` + timeouts tuned | | | | | | |
| `slow_provider` + timeouts + fallbacks | | | | | | |
| Routing on (`gpt-4.1-mini` default, `gpt-4.1` escalation) | | | | | | |

## 4. Budget test (lecture 13.3)

Put your targets into the CI budget gate so a pull request fails when p95 or cost per session regresses:

- `tests/budget/test_budget_gate.py` replays the day offline and asserts `p95_end_to_end_ms <= BUDGET_P95_MS` and `cost_per_session <= BUDGET_COST_PER_SESSION`.
- Set the thresholds to **your** column above, with a small tolerance (e.g., 5%) so noise doesn't fail the build.
- Keep the offline replay deterministic (fixed seed) so the gate is reproducible.

## 5. When you're over budget: fix list

| Over budget in | Try (in this order) |
|---|---|
| Steps | Step limit; clearer tool descriptions and schemas; return richer tool results so fewer follow-up calls are needed; escalate hard questions to the larger model once instead of looping on the small one |
| F. TTFT | Context diet (6.5); prompt caching (6.4: cached prefixes are often faster as well as cheaper); smaller model by default (6.6); provider region |
| O. Output | "Answer in ≤ N sentences" instructions; structured outputs instead of prose; smaller model |
| R. Retrieval | Lower top-k (measure grounding, don't guess); cache frequent queries; faster index |
| T. Tool | Per-tool timeout; async I/O; cache lookups; idempotency so a retry is safe |
| X. Retries / fallbacks | Bounded retries with jitter; shorter timeouts on the primary so the fallback fires sooner; circuit breaker with cooldown so a dead provider isn't retried every request |
| Q. Queue | Per-tenant concurrency limits; shed or defer low-priority traffic; degraded mode message (7.5) |
