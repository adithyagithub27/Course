# Incident 01 — Monday's cost spike

**Paged:** Monday 2026-09-14, 11:40 UTC, by `AtlasTenantCostAnomaly` ("tenant `ops` hourly spend is 2.5x its daily average"). The Ops Console's batch `cost_anomaly` rule (hourly cost per request > 2.5x the tenant's median hour) marks ops at 09:00, 10:00 and 11:00; its Budgets page flags ops cost-per-request bins from 09:15.

**Dataset:** `incidents/incident-01-cost-spike/` — 300 sessions, seed 11, session ids `s11-…`; 785 requests, $2.35 for the day, p95 6.8 s.

## What on-call sees

- Ops Console, Cost page: by noon the day has spent $1.40 and **$0.76 of it is one tenant, `ops`**; the other three tenants are at $0.19–0.24 each.
- Prometheus: `atlas_cost_usd_total{tenant="ops"}` per hour goes $0.04 at 08:00 → **$0.23 at 09:00 → $0.30 at 10:00** (five times, then seven times the 08:00 hour), $0.15 at 11:00, back to $0.07 at 12:00. The other tenants stay between $0.01 and $0.08 an hour all day. Request counts for ops are normal.
- `atlas_llm_retries_total{model="gpt-4.1-mini",reason="APITimeoutError"}` climbs between 10:00 and 12:00 (about 0.25 failed attempts per generation in the 10:00 hour, 0.16 at 11:00) and is zero in every other hour.
- No 5xx from Atlas. `/healthz` is green. Tool error share is zero for every tool. Users have not complained, although some requests took **over a minute** (p95 request latency for the 10:00 and 11:00 hours is 82–83 s; the console's `latency_p95` rule is red).
- A deploy went out at 08:55 ("retrieval recall improvements", PR #412).

## Your job (8 minutes)

1. Load `spans.jsonl` and confirm the blast radius: which tenant, which hours, which intents.
2. Find *where the tokens went*: input vs output vs cached, tokens per step, per request, per turn of a multi-turn session.
3. Find the second contributing factor hiding behind the first. Two bends in the cost curve (09:00 and 10:00) usually mean two causes.
4. Write one sentence for the root cause and list two fixes.

Hints: compare `gen_ai.usage.input_tokens` on generation spans for ops before and after 09:00 (and against the other tenants); look at `atlas.retrieval.top_k`, `atlas.retrieval.hits` and `atlas.tool.result_tokens` on retriever spans; look for generation spans with `status = ERROR` and read `error.type`, their duration and whether they still carry tokens and `atlas.cost_usd`. Sort sessions by cost and open the most expensive one.

Do not open `solution.md` until you have written your hypothesis down.
