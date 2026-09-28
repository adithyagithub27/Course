# Incident 01 — Solution (revealed in lecture 11.2)

## Root cause

PR #412 changed the `search_knowledge_base` tool for the **ops** tenant to "improve recall": it raised `top_k` from 4 to 12, dropped the relevance floor (`KB_MIN_SCORE=0`) and — because whole articles are now returned — the deploy also disabled the context diet so results would not be truncated. Every ops request from 09:00 carried 8–12 full articles (thousands of input tokens) into step 2, and multi-turn sessions carried them again on every follow-up.

At 10:00 the provider started timing out under the bigger prompts. Atlas retried each call up to 2 times. **A timed-out call still bills the input tokens**, so each retry storm re-billed the bloated context: the `retry_storm` compounds the `context_bloat`.

## Evidence in the spans

| Where | What you see |
|---|---|
| `invoke_agent atlas` spans, `atlas.tenant = "ops"`, 09:00–13:00 | `gen_ai.usage.input_tokens` per request 3–5× the pre-09:00 median; `atlas.cost_usd` similarly |
| retriever spans (`gen_ai.operation.name = "retrieval"`) | `atlas.retrieval.top_k = 12`, `atlas.retrieval.hits = 12` after 09:00 vs `4` / `1–3` before |
| `gen_ai.tool.call.result` on those spans | whole articles (`"content": "# ..."`) instead of snippets |
| generation spans 10:00–12:00 | `status = ERROR`, `error.type = "APITimeoutError"`, `atlas.retries = 1..2`, still carrying `gen_ai.usage.input_tokens` and `atlas.cost_usd` |
| `atlas.scenario` attribute | `context_bloat` / `retry_storm` (the simulator's label; in real life you don't get this one) |

`python console/ops_console.py --text` over the dataset shows the hourly bar chart spike for 09–13h and the `cost_anomaly` alert.

## Fix

1. Roll back `top_k` to 4 and `KB_MIN_SCORE` to 0.5 (`ATLAS_TOP_K`, `KB_MIN_SCORE`); keep the context diet on (`ATLAS_CONTEXT_DIET=1`). Retrieval quality is measured with `atlas.retrieval.hits` and the judge's `grounded` score, not with "more context".
2. Make retries a **cost event**: bound retries (`ATLAS_MAX_RETRIES=1` under load), add jitter, and open the circuit breaker so the fallback model takes over instead of re-billing the same prompt.
3. Put the per-tenant budget guard in front of the loop (`northwind.budget.BudgetGuard`): ops would have been degraded to `gpt-4.1-nano` at the soft cap and the alert would have fired an hour earlier.
4. Add the CI budget gate (`tests/budget/test_budget_gate.py`) so PR #412 would have failed on cost per session.

## Postmortem action items

- Retrieval changes need an eval on `judge_grounded` and a replayed cost delta before merge.
- Alert on `sum(rate(atlas_tokens_total{kind="input"}[5m])) by (tenant)` per request, not only on dollars.
