# Incident 02 — p95 doubled after lunch

**Paged:** Monday 2026-09-14, 14:20 UTC, by `AtlasLatencyP95High` (p95 > 4 s for 10 minutes). The Ops Console agrees: `latency_p95` (p95 6,857 ms > 4,000 ms) and `slo_burn:latency` at 5.16.

**Dataset:** `incidents/incident-02-latency-regression/` — 300 sessions, seed 22, session ids `s22-…`; 759 requests, $1.64 for the day.

## What on-call sees

- Grafana: `atlas_request_latency_seconds` p95 was ~3.5 s all morning; in the **13:00 bin it jumps to 8.1 s** and stays at 7.6–7.9 s through 16:00; at 17:00 it is back to 3.5 s. p50 goes 3.2 s → 5.1–5.5 s in the same hours. **All four tenants** move at the same hour by about the same amount.
- TTFT p95 (`atlas_ttft_seconds`) goes from ~0.55 s to ~1.9–2.0 s, about **3.5x**, and drops straight back at 17:00.
- Cost per request has not moved ($0.0021 → $0.0020). Error rate is flat at zero. No retries, no failed attempts, no tool errors.
- The provider status page shows "elevated latency" for one region starting 12:50.
- Someone mentions a config change at 12:30: "bumped retrieval top-k to 20 for the FAQ pilot".

## Your job (8 minutes)

1. Load `spans.jsonl`; compute p50/p95 per hour before and after 13:00, and note when it recovers.
2. Decompose a slow trace: where does the time go — model TTFT, generation, retrieval, tools? Compare the same question asked before and after 13:00 (for example sessions `s22-00108` at 10:50 and `s22-00200` at 14:26, both "How do I connect to the VPN from home?").
3. Decide: is it *only* the provider, or is something on our side making it worse? Write down what each suspect would predict for input tokens per generation and for time to first token *before* you look.
4. Propose the fix that holds p95 under 4 s even while the provider is slow.

Hints: `gen_ai.response.time_to_first_chunk` and `atlas.ttft_ms` on generation spans; `gen_ai.usage.input_tokens` and `gen_ai.usage.output_tokens` on generation spans by hour; `atlas.retrieval.top_k`, `atlas.retrieval.hits` and `atlas.tool.result_tokens` on retriever spans, and the retriever spans' durations.

Do not open `solution.md` until you have written your hypothesis down.
