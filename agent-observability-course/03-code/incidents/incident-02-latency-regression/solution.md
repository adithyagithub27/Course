# Incident 02 — Solution (revealed in lecture 11.3)

## Root cause

A regional provider slowdown from 13:00 to 17:00 (`slow_provider`: TTFT x3.5, tokens per second halved, on about three quarters of requests) tripled time to first token on every tenant while prompt sizes did not change. With the default 20 s per-call timeout a 5 s generation is a success, so neither the LiteLLM Router nor the circuit breaker in `_call_model` saw a failure, and the fallback model never fired.

The 12:30 "top-k to 20" change is a **red herring in this dataset**: the relevance floor (`KB_MIN_SCORE=0.5`) let only 5–7 of the 20 results through and the context diet caps every tool result at about 1,400 tokens, so input tokens per generation stayed flat. The only thing top-k 20 did here was make retriever spans about 65 ms slower at p95. (In the spans the top-k change appears at 13:00, not 12:30: when a person and a span disagree about a time, trust the span.)

## Evidence in the spans

| Where | What you see |
|---|---|
| `invoke_agent atlas` durations by hour | p95 3,589 ms at 11:00, 3,472 ms at 12:00, then **8,090 / 7,671 / 7,880 / 7,575 ms** from 13:00 to 16:00, back to 3,467 ms at 17:00. p50 3.2 s → 5.1–5.5 s. Nothing is left over after the recovery |
| generation spans, `atlas.ttft_ms` p95 | 556 ms at 12:00, 1,895–1,993 ms from 13:00 to 16:00, 562 ms at 17:00 (x3.5); generation duration p95 2.6 s → 4.5–5.2 s → 2.6 s |
| generation spans, tokens | mean input tokens per generation **flat at about 4,600** (4,630 at 12:00, 4,573 at 13:00, 4,709 at 14:00, 4,504 at 15:00); output tokens 117 → 94–101; cost per request $0.0021 → $0.0020 |
| span duration p95 by type | generation 2,592 ms → 4,499–5,235 ms; retriever 56 ms → 121–124 ms; tool 220–330 ms all day |
| retriever spans 13:00–16:00 | `atlas.retrieval.top_k = 20` on most calls (hourly mean 15–16; every call before 13:00 is `top_k = 4`), `atlas.retrieval.hits` about 6.5 instead of 3.7, `atlas.tool.result_tokens` unchanged at about 1,200 |
| sessions `s22-00108` (10:50, 3,245 ms) and `s22-00200` (14:26, 7,417 ms), same VPN question | retriever `top_k 4 → 20`, `hits 4 → 5`, `result_tokens 1,366 → 1,367`, 54 → 108 ms; agent input tokens 7,934 → 7,935; step-1 generation 834 ms (TTFT 533) → 2,469 ms (TTFT 1,867); step-2 generation 2,356 → 4,839 ms on 4,672 vs 4,673 input tokens |
| Reliability page | zero failed attempts, zero tool errors all afternoon, so the breaker never recorded a failure and cannot open |
| `atlas.scenario` | `slow_provider` on 200 of the 265 requests between 13:00 and 17:00 (the simulator's label) |

Hypotheses: provider slowdown — confirmed (TTFT up, prompts flat, recovers with the provider). Top-k 20 bloats prompts — killed (diet capped results). Slow retriever or tool — killed (+65 ms at p95, not 4 s). Traffic or rate limiting — killed (no errors, every tenant).

## Fix

1. **A per-call timeout derived from the step budget, not the inherited default:** `ATLAS_REQUEST_TIMEOUT_S=4` instead of 20. Now a stalled call fails, and a failure is something the breaker can count.
2. **Slowness must count as failure:** with `ATLAS_MAX_RETRIES=2 ATLAS_ROUTER_ALLOWED_FAILS=2 ATLAS_ROUTER_COOLDOWN_S=1800` the breaker opens after two timeouts and calls go to `FALLBACKS` (`gpt-4o-mini`, which the slowdown does not touch); the same knobs feed the LiteLLM Router (`ATLAS_ROUTER_MODE=1`, `build_router_config`). On the full-day `SCENARIO=slow_provider` replay this takes p95 from 8,877 ms to 3,859 ms with 0 errors and a lower bill ($55.86 → $43.29), because the fallback model is cheaper. A fallback that only fires on errors protects an availability promise, not a latency promise.
3. **Keep `ATLAS_TOP_K=4`** until recall is measured against tokens. The diet made top-k 20 harmless here, but the Makefile's full-day replay runs with `DIET=0`: there, `latency_regression` (slowdown + top-k 20) has p95 9,474 ms against 8,877 ms for `slow_provider` alone, and mean input tokens per generation rise from 6,600 to 8,400. The CI gate (`ATLAS_TOP_K=20 make budget-check`) fails on p95 and tokens.
4. Stream the final answer so users see the first token early (with streaming, time out on TTFT instead; Lecture 5.4).
5. Lab 4 (`04-labs/lab-04-latency-chaos.md`): replay with `--incidents latency_regression` and tune until the budget gate passes.
