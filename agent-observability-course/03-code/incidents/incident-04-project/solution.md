# Incident 04 — INSTRUCTOR ONLY (grading key for Project 2)

> Do not publish this file to students. It is committed so the grading is reproducible; the course repo published to students should have it removed (see `Makefile` target `student-repo`).

## What actually happened (simulator preset `mixed`, seed 44)

1. **10:00–12:00, all tenants (`ticket_flaky`, 90% of requests in the window):** the ticket service became flaky (two timeouts, then success). `lookup_ticket` returned `{"error": "ticket_service_timeout", "retry": true}`; the model obliged and re-called the tool. With `ATLAS_MAX_TOOL_RETRIES=0` (unlimited, the default) nothing stopped it except success on the third call. In this 300-session sample the window contains only 5 ticket lookups, in 3 sessions: `s44-00079` (ops, 10:00 and 10:01), `s44-00083` (finance, 10:44) and `s44-00135` (eng, 11:37 and 11:38). Each shows 3 `execute_tool lookup_ticket` spans (two `ERROR` with `error.type = ticket_service_timeout`, one `OK`), `atlas.steps = 4` instead of 2, and about 2x the cost of a normal lookup (median $0.0024 vs $0.0011). 10 ERROR spans in total, out of 74 `lookup_ticket` calls for the day (13.5%; 6 of 11 in the 10:00 hour). This is the "tool retry storm" that Lecture 5.6 fixes with `ATLAS_MAX_TOOL_RETRIES` and error surfacing.
2. **15:00–16:00, all tenants (`slow_provider`, 60% of requests; 43 of the 66 requests in that hour carry the tag):** TTFT x3.5, tokens per second halved on the primary deployment. Unrelated to the morning. p95 8,501 ms against ~3,600 ms in the other hours (2.3x); cost per request $0.00224 → $0.00230, because slower generations in the mock are not more expensive per token but the affected mix skews to longer answers. No errors, no retries, so the circuit breaker never opened and no fallback fired.

`make incident N=4` prints `latency_p95` (4,652 ms > 4,000 ms) and `slo_burn:tool_success` 3.85. The console's overall `tool_error_rate` ticket (> 5% of *all* tool calls) does not fire: 10 of 733 tool calls is 1.4%. A per-tool rule such as `AtlasToolErrorRate` does.

## Grading rubric (20 points)

| Points | Criterion |
|---:|---|
| 4 | Timeline correct for both alerts (10:00–12:00 tool errors on `lookup_ticket` only; 15:00–16:00 slow TTFT on every model call) with span-level evidence (`gen_ai.tool.name`, `error.type = ticket_service_timeout`, `atlas.steps`, `gen_ai.response.time_to_first_chunk` / `atlas.ttft_ms`) |
| 4 | Correct root cause for each alert and the explicit statement that they are **unrelated** |
| 3 | Blast radius quantified from the data (3 sessions / 5 requests in the morning; 66 requests across all four tenants in the 15:00 hour; cost delta for finance) |
| 4 | Three action items that name real files: `app/agent.py` (`ATLAS_MAX_TOOL_RETRIES`, `ATLAS_REQUEST_TIMEOUT_S`, circuit breaker / `FALLBACKS`), `northwind/budget.py`, `tests/budget/test_budget_gate.py`, `deploy/grafana/dashboards/atlas-ops.json`, `telemetry/metrics.py` |
| 3 | One concrete SLO/alert with threshold (e.g. `tool_success` SLO 99% with 1h burn-rate page at 14.4; or per-tool `atlas_tool_calls_total{outcome="error"}` > 5% for 10 min, noting that an all-tools rate hides a 13% failure on one tool) |
| 2 | Blameless tone, no "the model was dumb" |

Common misses: blaming the morning on the LLM provider; treating the two alerts as one incident; proposing "add more retries" (which makes both worse); calling the morning "every tenant that looks up tickets" when the sample shows three sessions.
