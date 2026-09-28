# Incident 02 — Solution (revealed in lecture 11.3)

## Root cause

Two things at once. The provider's regional slowdown multiplied TTFT by ~3.5 and halved tokens per second from about 13:00 (`slow_provider`). On its own that would have pushed p95 to about 5 s. But at 12:30 the retrieval `top_k` had been raised from 4 to **20** for a pilot. Each retriever span got longer (retrieval time grows with k) and — more importantly — the retrieved snippets made every step-2 prompt larger, and a slow provider is slowest on long prompts. The two changes compound into the 6–8 s p95.

## Evidence in the spans

| Where | What you see |
|---|---|
| `invoke_agent atlas` durations by hour | p95 ~3.0 s until 13:00, then 6–8 s until 17:00 |
| generation spans after 13:00 | `gen_ai.response.time_to_first_chunk` 3–4× higher for the same model and similar token counts |
| retriever spans after 12:30 | `atlas.retrieval.top_k = 20` (was 4), longer durations, more `atlas.retrieval.hits` |
| step spans | `atlas.context_tokens` higher in step 2 after 12:30 |
| requests before 13:00 with `top_k = 20` | already slightly slower than the morning: the k change alone was a small regression the provider then amplified |

The Ops Console prints `hourly p95` and fires `latency_p95`.

## Fix

1. Roll `ATLAS_TOP_K` back to 4 (retrieval hits show 4 articles were always enough; the judge's `grounded` score did not improve with 20).
2. Per-call timeouts (`ATLAS_REQUEST_TIMEOUT_S`) tuned to the TTFT budget, and the **circuit breaker + fallback model** in `app/agent.py` (`FALLBACKS`) or the LiteLLM Router (`ATLAS_ROUTER_MODE=1`, `fallbacks=`, `cooldown_time=`) so that when the primary region is slow the request moves to `gpt-4o-mini` instead of waiting.
3. Stream the final answer so users see the first token early even if total time is longer.
4. Lab 4 (`04-labs/lab-04-latency-chaos.md`): replay with `--incidents latency_regression` and tune until the budget gate passes.
