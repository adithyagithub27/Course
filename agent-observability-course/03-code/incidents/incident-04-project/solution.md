# Incident 04 — INSTRUCTOR ONLY (grading key for Project 2)

> Do not publish this file to students. It is committed so the grading is reproducible; the course repo published to students should have it removed (see `Makefile` target `student-repo`).

## What actually happened (simulator preset `mixed`, seed 44)

1. **10:00–12:00, all tenants:** the ticket service became flaky (`ticket_flaky` scenario: two timeouts, then success). `lookup_ticket` returned `{"error": "ticket_service_timeout", "retry": true}`; the model obliged and re-called the tool. With `ATLAS_MAX_TOOL_RETRIES=0` (unlimited) nothing stopped it except success on the third call, so affected requests show 3 `execute_tool lookup_ticket` spans (two `ERROR`, one `OK`), 4 steps, 3–4× the tokens and cost of a normal ticket lookup. This is the "tool retry storm" that Lecture 5.6 fixes with `ATLAS_MAX_TOOL_RETRIES` and error surfacing.
2. **15:00–16:00, all tenants:** provider slowdown (`slow_provider`, 50% of requests): TTFT ×3.5, tokens/s halved. Unrelated to the morning. p95 ≈ 2× baseline; cost slightly up because slower generations in the mock are not more expensive per token but the affected mix skews to longer answers.

## Grading rubric (20 points)

| Points | Criterion |
|---:|---|
| 4 | Timeline correct for both pages (10:00–12:00 tool errors on `lookup_ticket` only; 15:00–16:00 slow TTFT on every model call) with span-level evidence (`gen_ai.tool.name`, `error.type = ticket_service_timeout`, `atlas.steps`, `gen_ai.response.time_to_first_chunk`) |
| 4 | Correct root cause for each page and the explicit statement that they are **unrelated** |
| 3 | Blast radius quantified from the data (sessions, users, cost delta for finance) |
| 4 | Three action items that name real files: `app/agent.py` (`ATLAS_MAX_TOOL_RETRIES`, circuit breaker / `FALLBACKS`), `northwind/budget.py`, `tests/budget/test_budget_gate.py`, `deploy/grafana/dashboards/atlas-ops.json`, `telemetry/metrics.py` |
| 3 | One concrete SLO/alert with threshold (e.g. `tool_success` SLO 99% with 1h burn-rate page at 14.4; or `atlas_tool_calls_total{outcome="error"}` > 5% for 10 min) |
| 2 | Blameless tone, no "the model was dumb" |

Common misses: blaming the morning on the LLM provider; treating the two pages as one incident; proposing "add more retries" (which makes both worse).
