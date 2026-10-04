# Incident 01 — Solution (revealed in lecture 11.2)

## Root cause

PR #412 changed the `search_knowledge_base` tool for the **ops** tenant to "improve recall": it raised `top_k` from 4 to 12, dropped the relevance floor (`KB_MIN_SCORE=0`) and — because whole articles are now returned — the deploy also disabled the context diet so results would not be truncated. From 09:00 every ops request carried whole articles (about 10,800 result tokens per retriever call instead of 1,200) into step 2, and multi-turn sessions carried the untrimmed history again on every follow-up.

At 10:00 the provider started timing out on ops calls (20 s per-call timeout, two retries, so up to three attempts per call). **A timed-out call still bills the input tokens**, so each retry re-billed the bloated prompt: the `retry_storm` compounds the `context_bloat`. The storm stops by 12:00; the bloat lasts until 13:00.

## Evidence in the spans

| Where | What you see |
|---|---|
| Cost page, hourly cost by tenant | `ops` $0.043 at 08:00, $0.228 at 09:00, $0.303 at 10:00, $0.146 at 11:00, $0.072 at 12:00; other tenants $0.01–0.08 every hour |
| Cost page, unit costs for `ops` | cost per session $0.0035 at 08:00 → $0.0228 at 09:00; mean input tokens per generation 4,018 → 12,032 at 09:00 (3x); per request, mean input tokens 8,400 before 09:00 → 22,200 between 09:00 and 13:00 |
| Traffic page, `ops` vs the shadow line | 115 ops requests 06:00–12:00 against 118 on the replayed plan: same traffic, bigger requests |
| retriever spans (`gen_ai.operation.name = "retrieval"`), `ops`, 09:00–13:00 | `atlas.retrieval.top_k` 12 or 20 (the model asks for 20; the preset caps the tool at 12), hourly mean about 15; `atlas.retrieval.hits` 7–14 instead of 4; `atlas.tool.result_tokens` about 10,800 instead of about 1,200. Other tenants stay at `top_k = 4`, `hits ≤ 4` |
| `gen_ai.tool.call.result` on those spans | whole articles (`"content": "# ..."`) instead of snippets |
| generation spans 10:00–11:59 | 72 spans with `status = ERROR`, `error.type = "APITimeoutError"`, all `atlas.tenant = ops`, all `gpt-4.1-mini`, each exactly 20,000 ms, `atlas.retries = 1` or `2`, still carrying `gen_ai.usage.input_tokens` and `atlas.cost_usd` ($0.175 billed on failed attempts, 7% of the day) |
| Reliability page | tool error share zero for every tool all day; failed LLM attempts per generation 0.25 at 10:00 and 0.16 at 11:00, nothing elsewhere; 0.64 failed attempts per *request* in the 10:00 hour |
| session `s11-00110` (ops, three questions about leave, 10:24–10:25) | the most expensive session, $0.103: three turns of about 83 s each; step-2 input tokens 11,526 → 19,294 → 27,110 across the turns; 268,815 input tokens billed in total; the twelve timed-out attempts cost $0.070 (68% of the session), the six successful calls $0.033. A normal ops session at 08:00 costs $0.0035 |
| `atlas.scenario` attribute | `context_bloat` / `retry_storm` (the simulator's label; in real life you don't get this one) |

`make incident N=1` prints the hourly bar chart spike for 09–13h and two alerts: `latency_p95` (6,819 ms > 4,000) and `cost_anomaly` (ops at 09:00, 10:00, 11:00).

## Fix

1. **Now:** roll back `top_k` to 4 and `KB_MIN_SCORE` to 0.5 (`ATLAS_TOP_K`, `KB_MIN_SCORE`); keep the context diet on (`ATLAS_CONTEXT_DIET=1`) and remove the per-tenant path that can switch it off. Retrieval quality is measured with `atlas.retrieval.hits` and the judge's `grounded` score, not with "more context". On the full-day replay (`OFFLINE=1 make replay SCENARIO=...`) the incident day costs **$64.99** (p95 6,763 ms); with the retrieval change rolled back and the same provider storm (`retry_storm`) **$58.00** (p95 3,889 ms) against a **$56.28** baseline (p95 3,827 ms). The storm alone is a small problem; the bloat is what made it expensive.
2. **Make a retry storm a cost event, not just a reliability event.** `ATLAS_MAX_RETRIES=1` is a dial, not a fix: on the full day it costs $54.59 but the mock provider times out twice before succeeding, so 392 requests end in `error`. The real action item is a circuit breaker that counts failures over a time window: `app/agent.py::CircuitBreaker` opens only after `ATLAS_ROUTER_ALLOWED_FAILS` (3) *consecutive* failures and a success resets it, so "fail, fail, succeed" never opens it and the fallback model never got a call.
3. **Detect it two hours earlier.** `deploy/alerts.yml` ships `AtlasRetryStorm` (more than 0.2 LLM retries per request for 10 minutes, severity page). This dataset runs at about 0.64 per request in the 10:00 hour, so it would have paged at about 10:10 instead of 11:40; route it to a person. The Budgets page's cost-per-request bins flag ops from 09:15.
4. **Backstop and gate.** The per-tenant `BudgetGuard` (`northwind.budget`) is not in the replay path, so nothing degrades in this dataset (ops spends $1.14 of a $25 soft cap in the 300-session sample; on the full-day replay ops crosses the soft cap at 16:08 and would have been degraded to `gpt-4.1-nano`). The CI budget gate (`tests/budget/test_budget_gate.py`, Lecture 13.3) fails on these exact settings: `ATLAS_TOP_K=12 KB_MIN_SCORE=0 make budget-check`.

## Postmortem action items

- Retrieval changes need an eval on `judge_grounded` and a replayed cost delta before merge; a test that three turns with twelve articles stays inside the token budget would have failed PR #412.
- Alert on `sum(rate(atlas_tokens_total{kind="input"}[5m])) by (tenant)` per request, not only on dollars; keep `AtlasRetryStorm` routed to a person.
- A breaker that counts failures over a window, tested against `SCENARIO=retry_storm`.
