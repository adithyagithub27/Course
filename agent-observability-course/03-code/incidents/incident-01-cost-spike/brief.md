# Incident 01 — Monday's cost spike

**Paged:** Monday 2026-09-14, 11:40 UTC, by the `cost_anomaly` rule (a tenant's hourly cost per request > 2.5x its median hour; the EWMA detector in `BudgetGuard` had flagged ops at 10:05 already).

## What on-call sees

- Langfuse cost view: the day is tracking at roughly **2× last Monday's spend** by noon, and it is almost all one tenant.
- Prometheus: `atlas_cost_usd_total{tenant="ops"}` rate tripled between 09:00 and 13:00; other tenants are flat.
- `atlas_llm_retries_total{model="gpt-4.1-mini",reason="APITimeoutError"}` started climbing at 10:00.
- No 5xx from Atlas. `/healthz` is green. Users have not complained, although p95 latency also crept up mid-morning (some requests took 40 s+).
- A deploy went out at 08:55 ("retrieval recall improvements", PR #412).

## Your job (8 minutes)

1. Load `spans.jsonl` and confirm the blast radius: which tenant, which hours, which intents.
2. Find *where the tokens went*: input vs output vs cached, tokens per step, per request.
3. Find the second contributing factor hiding behind the first.
4. Write one sentence for the root cause and list two fixes.

Hints: compare `gen_ai.usage.input_tokens` on generation spans before and after 09:00; look at `atlas.retrieval.top_k` and `atlas.retrieval.hits` on retriever spans; look for generation spans with `status = ERROR` and `error.type`.

Do not open `solution.md` until you have written your hypothesis down.
