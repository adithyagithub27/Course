# Incident 02 — p95 doubled after lunch

**Paged:** Monday 2026-09-14, 14:20 UTC, by the `latency_p95` rule (p95 > 4 s for 15 minutes).

## What on-call sees

- Grafana: `atlas_request_latency_seconds` p95 went from ~3 s to **6–8 s** starting ~13:00; all tenants affected.
- TTFT p95 (`atlas_ttft_seconds`) roughly tripled. Tokens per request are *slightly* up.
- Cost is up only ~10%. Error rate is flat. No retries to speak of.
- The provider status page shows "elevated latency" for one region starting 12:50.
- Someone mentions a config change at 12:30: "bumped retrieval top-k to 20 for the FAQ pilot".

## Your job (8 minutes)

1. Load `spans.jsonl`; compute p50/p95 per hour before and after 13:00.
2. Decompose a slow trace: where does the time go — model TTFT, generation, retrieval, tools?
3. Decide: is it *only* the provider, or is something on our side making it worse?
4. Propose the fix that holds p95 under 4 s even while the provider is slow.

Hints: `gen_ai.response.time_to_first_chunk` and `atlas.ttft_ms` on generation spans; `atlas.retrieval.top_k` on retriever spans and their durations; `atlas.context_tokens` on step spans.
