# Course 4 Code Changes: Reference for Script Fixes

> Written 2026-10-02 after the code fix pass on `agent-observability-course/03-code/`. Every lecture, lab, quiz and production doc must match this file and `agent-observability-course/01-curriculum/numbers-card.md`. Where a script cites a name listed under "old → real", use the real name.

**State (after the second pass, §16, 2026-10-04):** `make test` = **419 passed** (372 unit, 42 integration, 5 budget gate). `make lint` clean. `uv.lock` committed: langfuse 4.16.0, opentelemetry-sdk 1.45.0, litellm 1.103.2, fastapi 0.142.2, openai 2.54.0, deepeval 4.2.7, streamlit 1.64.0.

---

## 1. Root span

FastAPI 0.142's built-in OpenTelemetry made `invoke_agent atlas` a grandchild of a `POST /chat` span. `app/server.py` now turns FastAPI telemetry off, so the code matches 3.2 and 3.6: exactly one root span, `invoke_agent atlas`, `parent_id null`. The agent runs via `asyncio.to_thread`. `metrics.set_build_info(...)` is called at startup, so the Grafana deploy annotation fires.

## 2. Tests (names scripts may cite)

All in `tests/integration/test_spans.py` unless noted. Fixture is `client` (TestClient), not `atlas_offline` or `spans`.

| Lecture | Test |
|---|---|
| 3.4 | `test_ticket_question_emits_tagged_tool_span` |
| 3.6 | `test_no_orphan_spans`, `test_tool_spans_are_children_of_agent` (tool spans are children of `step n` spans, which are children of the agent), `test_one_generation_per_model_call` |
| 4.7 | `test_guardrail_observation`; `tests/integration/test_guardrail.py` |
| 5.6 | `test_loop_scenario_stops_at_step_limit` (defaults, 6 steps); `test_loop_scenario_stops_early` (`ATLAS_MAX_TOOL_RETRIES=2`, 3 steps, `result.resolved is False`) |
| 10.2 | `test_no_raw_pii_reaches_any_span`. Placeholders are `<CARD…>`, `<EMAIL…>`, `<EMPLOYEE_ID…>` (not `[card]`, `[email]`, `[emp:`). Employee ID format `NW-\d{5}`; `NW-004471` does not match. |
| 6.5 | `tests/unit/test_tokens.py::test_context_diet_bounds_tokens` |
| 13.3 | `tests/budget/test_budget_gate.py::test_max_input_tokens_per_generation` (the "tokens test") |
| Project 2 | `test_tool_retries_are_bounded` is a student deliverable, not shipped |

## 3. Agent and config

- `ATLAS_MAX_STEPS=0` means **unlimited**. The only stop is the request deadline `ATLAS_REQUEST_DEADLINE_S` (default 600 s; offline counts simulated latency). Hitting it: outcome **`timeout`**, event `request_deadline_exceeded`, `error.type=deadline_exceeded`. Last-resort cap `UNLIMITED_STEP_CEILING=2000`. **Default step limit is 6** (never 8).
- New settings: `ATLAS_MOCK_LATENCY_SCALE`, `ATLAS_TENANT_MAX_INFLIGHT` (default `ops=13,eng=7,finance=6,hr=6,other=2`), `ATLAS_QUEUE_TIMEOUT_S` (3), `ATLAS_ROUTER_ALLOWED_FAILS` (3), `ATLAS_ROUTER_COOLDOWN_S` (30), `BUDGET_MAX_INPUT_TOKENS_PER_GENERATION` (alias `MAX_INPUT_TOKENS_PER_GENERATION`, default 24,000), `JUDGE_MAX_CALLS`.
- `AgentResult` gained `feature`, `model_calls`, `resolved`. `AtlasAgent(on_step=...)` progress callback.
- Event name is **`tool_retries_exhausted`** (plural).
- **No escalation on repeated tool errors.** Escalation only for sensitive intents. Cut "escalating to gpt-4.1 after repeated tool errors" (1.1, 5.2, 5.6).
- `ATLAS_MAX_TOOL_RETRIES` defaults to 0 (unlimited); the 5.6 "after" run sets `ATLAS_MAX_TOOL_RETRIES=2` explicitly.
- Failed tool spans carry ERROR status and `atlas.tenant`; all tool spans carry `atlas.tool.result_tokens`.
- `llm_first_token_timeout_s`, `llm_total_timeout_s`, `llm_max_retries` **do not exist**. Use `ATLAS_REQUEST_TIMEOUT_S` (`request_timeout_s`, 20) and `ATLAS_MAX_RETRIES` (`max_retries`, 2).

## 4. Guardrail (4.7)

- `northwind.guardrails.looks_like_injection` → **`app.guardrails.injection_check(message) -> GuardrailResult(flagged: bool, reason: str | None, confidence: float)`** (matches `05-projects/challenges.md`). `app.guardrails.looks_like_injection(text) -> bool` remains.
- Reasons: `instruction_override` (0.95), `prompt_exfiltration` (0.9), `role_hijack` (0.85), `bulk_data_request` (0.8).
- Span `guardrail injection_check`, type guardrail, level WARNING when flagged, output JSON `{"flagged","reason","confidence"}`, attribute `atlas.guardrail.confidence`.
- Langfuse-native version: `app.langfuse_native.injection_guardrail`. `AtlasAgent._injection_check` does not exist.
- Score with `score_current_trace(name="injection_flagged", value=1|0, data_type="BOOLEAN")` on every trace. Never `score_current_span`.

## 5. Prompts

`python -m app.prompts register [--production v1]`, `promote --version N [--label production]`, `show`. `make prompts` runs register. `telemetry.langfuse_setup.promote_prompt(name, version, *, label="production")` wraps `Langfuse.update_prompt(name=, version=, new_labels=)` (present in 4.16). Aliases `ATLAS_V1`/`ATLAS_V2`. **There is no v3.**

## 6. Drift (8.5)

`python -m evals.drift_report --prev 2026-W38 --curr 2026-W39 [--store P] [--out evals/out/drift-report.md]`. Two weeks in one store: `make replay`, then `make replay DAY=2026-09-21 SCENARIO=quality_drift KEEP=1`. The 8.4 "seven-day replay with Thursday/Wednesday bumps" has no backing scenario: re-cue it.

## 7. Replay and Makefile

- `--day YYYY-MM-DD` on replay; non-default days get session ids like `s07-0921-00001`.
- Makefile flags: `DAY=`, `STORE=`, `KEEP=1`, `PACE=`, `MSG=`, plus existing `CACHE=1 DIET=1 ROUTER=1`.
- `make replay SCENARIO=<preset>` works (cost_spike, latency_regression, quality_drift, mixed, context_bloat, retry_storm). `make run` takes base scenarios only.
- `make replay PROM=1` **does nothing**. Prometheus path: `make stack`, `make run`, `make swarm`.
- `make report DAY=` and `console/fixtures/` **do not exist**.
- New targets: `make loop-demo`, `make langfuse-native`, `make prompts`, `make lock`. `make incident N=n` writes `.atlas/incident-0N.sqlite`; open with `make console STORE=.atlas/incident-0N.sqlite`.
- `make swarm SCENARIO=loop` barely loops. Use **`make loop-demo`** (in-process; `PACE=0.1 make loop-demo` for a live meter). With a server: terminal 1 `ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 OFFLINE=1 make run`; terminal 2 `python simulator/loop_demo.py --url http://127.0.0.1:8000`.
- Demo request in 6.4/6.5: add `OTEL_EXPORTER=none` or span JSON prints after the output.

## 8. Metrics

| Script says | Real |
|---|---|
| `atlas_requests_total` | `{tenant,model,outcome,feature}` |
| `atlas_request_latency_seconds` | `{tenant,feature}` (end-to-end latency, not first token) |
| per-generation TTFT | `atlas_ttft_seconds{model}` |
| `atlas_inflight`, `atlas_queue_wait_seconds` | exist, `{tenant}`; plus `atlas_requests_shed_total{tenant}` (429, `Retry-After: 1`) |
| `atlas_step_limit_total` | `atlas_requests_total{outcome="step_limit"}` |
| `atlas_budget_hits_total`, `budget_events{action=}` | `atlas_budget_decisions_total{tenant,decision}` |
| `atlas_tool_duration_seconds` | `atlas_tool_latency_seconds{tool}` |
| `atlas_circuit_open` | not shipped (Lab 4 stretch) |
| `outcome="ok"` | `outcome="resolved"` |
| `outcome=~"refused\|degraded"` | `outcome="refused"`; degrade is `atlas_budget_decisions_total{decision="degrade"}` |
| cache hit-rate denominator `kind=~"input\|cached"` | `kind="input"` (input already includes cached) |

`atlas_telemetry_export_failures_total{name}` is now incremented.

## 9. Files

- Added: `.env.chaos.example` (Lab 4), `app/guardrails.py`, `app/langfuse_native.py`, `console/data.py`, `console/_ui.py`, `console/pages/*.py`, `simulator/loop_demo.py`.
- `tests/budget/report.py` (Lab 7) **not added**: remove from the lab.
- Lab 6: real files `deploy/alerts.yml` (already contains `AtlasToolErrorRate`, 10 rules) and `deploy/prometheus.yml` (scrapes `atlas:8000`).
- Lab 2: `check_shipment(tracking_id)` is already instrumented. `TestCheckShipment` and `TestEscalation` (Labs 2, 3) do not exist.
- `make report` now prints a real per-feature showback.

## 10. Langfuse-native module (`app/langfuse_native.py`), taught in Sections 4 and 5

Runs offline with a real `Langfuse` client on a private TracerProvider, `InMemorySpanExporter` and an `httpx.MockTransport`. Run: `make langfuse-native [MSG="..."]` or `python -m app.langfuse_native "<msg>" [--tenant eng --user --session --scenario loop --offline]`. Prints the observation tree, scores and cost. Atlas's production path is unchanged (OTel spans plus `ga.*` setters); Sections 4 and 5 should say that Atlas itself uses the vendor-neutral path from Section 3, which Section 12 relies on.

- `setup_langfuse_native(settings=None, *, offline=None) -> (Langfuse, OfflineCapture | None)`
- `handle_chat(message, *, tenant, user_id="anonymous", session_id=None, scenario=None, settings=None) -> NativeResult`: `propagate_attributes(session_id=, user_id=, tags=["tenant:…"], metadata={"tenant","scenario"}, trace_name="atlas")` around the root.
- `@observe(name="atlas", as_type="agent") run_agent(message, *, tenant, settings=None, scenario=None, llm=None)`: nested `propagate_attributes(tags=["feature:…"])`; scores `resolved` (BOOLEAN), `steps` (NUMERIC), `step_limit_hit` (BOOLEAN).
- `@observe(name="injection_check", as_type="guardrail") injection_guardrail(message) -> GuardrailResult`
- `@observe(name="chat", as_type="generation") call_model(run, messages, *, model)`: `get_client().update_current_generation(input=, output=, model=, model_parameters=, usage_details={"input","output","cache_read_input_tokens"[, "reasoning_tokens"]}, cost_details={"input","output","cache_read_input_tokens","total"}, completion_start_time=, metadata=)`.
- `@observe(name="search_knowledge_base", as_type="retriever")`; tools `lookup_ticket`, `create_ticket`, `reset_password`, `check_shipment` with `@observe(as_type="tool")`, setting `update_current_span(input=, output=, level="ERROR", status_message=)` on failure.
- Steps: `get_client().start_as_current_observation(name="step n", as_type="chain")`.
- Events: `get_client().create_event(name="step_limit_reached" | "tool_retries_exhausted" | "escalation", level=, metadata=)`.
- `OfflineCapture.spans(trace_id)`, `.scores(trace_id)`, `.reset()`; `observation_tree(spans)`, `render_trace(result, capture)`.
- `NativeResult`: `answer, trace_id, outcome, intent, feature, steps, model, input_tokens, output_tokens, cached_tokens, cost_usd, tool_calls, guardrail, .resolved`.

## 11. Ops Console

Streamlit multipage: `console/ops_console.py` home (tiles: cost, requests/sessions, p95, judge or "not yet scored"); pages auto-discovered from `console/pages/`; pure data in `console/data.py` (`StoreData.load(store)`). Pages:

| Page | Backs | Not backed (re-cue) |
|---|---|---|
| Live cost | 1.1: spend meter, per-tenant table, steps counter, context-size and cost sparklines, Alerts panel (line `lookup_ticket 100% over 60 s (ops)` under rule `tool_error_rate`), refresh 2 s | 1.1's "$0.00 table" layout is a tenant bar chart |
| Cost | 2.4, 6.3, 6.4, 11.x: tenant, feature, cost/session, cost/resolved session, cache-hit tile, cost/hour by tenant, hourly cost/session and mean tokens per generation, top-10 conversations linking to Traces | |
| Latency | p50/p95/p99, hourly with 4 s budget line, span p95 by type, TTFT p95 | |
| Quality | 5.3, 8.3, 11.4: judge means, grounded rate, empty-retrieval rate, feedback tile, judge hourly, judge by prompt version, feedback by session length, thumbs-down hourly, clickable judge-vs-user disagreement table, top comments | 8.3's `not_what_i_asked` breakdown (replay comments are only `unhelpful`) |
| Budgets | 6.7: cumulative spend vs soft/hard caps; anomaly = 15-min cost/request above 2× tenant median | "soft cap triggers, line flattens" and the no-guard comparison: re-cue to `BudgetGuard` unit tests or a live `make run` |
| Traffic | 11.2 E2: requests/min by tenant with shadow line (previous week if stored via `make replay DAY=2026-09-07 KEEP=1`, else "replayed plan, seed 6") | "last Monday" wording |
| Retrieval | 11.2 E5: mean top_k, hits, result tokens, empty share by tenant | |
| Reliability | 11.2 E4: tool error share per tool, LLM retries by `error.type` and per generation | breaker state and fallbacks: re-cue to Grafana `atlas_model_fallbacks_total` |
| Safety | 8.4: injection, refusal, PII-in-output rates per hour | seven-day bumps |
| Alerts | batch rules, SLOs, budgets | |
| Traces | 2.4, 11.x E6: waterfall by `?trace=<id>`, session id, or top 10 | |
| Compare replays | 14.2, 6.8: pick `.atlas/*.sqlite`; cost, Δ%, cost/session, cache ratio, p95, judge | per-lever "breakdown bar" (use the card's lever table) |

Also not backed: 3.6's "$12.84 = exactly double with OpenInference on"; 7.6's offline "requests in flight" panel.

## 12. Alerts and SLOs (truth: `deploy/alerts.yml`, 10 rules)

| Rule | Condition | Severity |
|---|---|---|
| `AtlasLatencyP95High` | p95 > 4 s for 10m | page |
| `AtlasTaskSuccessBurnRateFast` | 14.4× over 1h, for 5m; bad = `error\|step_limit\|tool_error\|timeout`; SLO 95% | page |
| `AtlasTaskSuccessBurnRateSlow` | 6× over 6h, for 30m | ticket |
| `AtlasToolErrorRate` | > 5% per tool over 10m, for 10m | ticket |
| `AtlasTenantCostAnomaly` | hourly spend > 2.5× previous day's average hour and > $1, for 15m | ticket |
| `AtlasBudgetHardCapHit` | any refusals | page |
| `AtlasRetryStorm` | > 0.2 retries per request | page |
| `AtlasJudgeScoreLow` | judge_grounded < 0.75 over 2h. **Can never fire**: `atlas_judge_score` is never observed (judge is a batch CLI). Say so in 9.5 or drop it. | ticket |
| `AtlasNegativeFeedbackSpike` | > 40% negative | ticket |
| `AtlasTelemetryExportFailures` | > 20 in 10m | ticket |

9.1's 6×/30m design does not exist. Prometheus retention is now **45d** (covers the 30-day SLO window). Grafana has a `$feature` variable.

## 13. Collector (13.2, 10.2)

Processors exactly: `memory_limiter`, `attributes/redact`, `tail_sampling`, `batch`. `attributes/redact` **deletes** `gen_ai.tool.call.result`, input/output message attributes, `gen_ai.system_instructions`, `langfuse.observation.input`/`output`, and **hashes** `gen_ai.tool.call.arguments` only; since §16 it **deletes** `user.id` and `enduser.id` (the collector's `hash` is unkeyed SHA-256, reversible for a five-digit ID). (`redaction`, `transform`, `attributes/mask` do not exist.) Exporters: `otlphttp/langfuse` (`${LANGFUSE_BASE_URL}/api/public/otel`), `otlphttp/phoenix` (`http://phoenix:6006`; compose service `arizephoenix/phoenix:version-20.18.0`, verify), `debug`, `spanmetrics`. `make replay` does not go through the collector; the 13.2 demo uses `make stack` + `make swarm`. Standalone Phoenix on 6006 (12.3) conflicts with the stack.

## 14. Headline numbers (full card: `01-curriculum/numbers-card.md`)

- Baseline day: 10,184 requests, 4,000 sessions, **$56.28**, $0.0141/session; ops $20.27, eng $12.50, finance $11.91, hr $11.59. Feature: policy_question 76.2% ($42.91), create_ticket $6.66, ticket_lookup $3.21, shipment_status $2.21, password_reset $0.78, escalation $0.38, other $0.13.
- Latency p50/p95 3,232/3,827 ms; final-answer TTFT 1,427/1,702 ms; per-generation TTFT 509/652 ms.
- Judge overall 0.912, grounded 0.943, resolved 0.892. Task success 0.993, containment 0.989.
- Levers: caching $37.00 (−34.3%), diet $41.99 (−25.4%), router $47.07 (−16.4%), caching+diet $22.71 (−59.6%), all three $19.07 (−66.1%).
- 6.4/6.5 demo request: 9,926 input tokens, $0.00449; caching $0.00257; diet 7,861 tokens, $0.00366; both $0.00174.
- Loop demo: guards off 549 steps, $4.90, 12.17M input tokens, 600.8 s, outcome timeout; default 6 steps, $0.0086; `ATLAS_MAX_TOOL_RETRIES=2` 3 steps, $0.0042.
- Incident 1 fix: `make replay SCENARIO=retry_storm` $58.00 vs cost_spike $64.99.
- Incident session ids use seeds 11/22/33/44 (`s11-…`), not `s07-`.

## 15. Known code issues found during the script pass (2026-10-02)

Fixed: Atlas set `langfuse.observation.completion_start_time` to the call start when there was no TTFT (Langfuse showed TTFT 0); it now sets start + TTFT, or nothing. `atlas_ttft_seconds` help text now says "each generation". The `langfuse_native` docstring now says the LLM is always the mock.

Fixed in the second pass (§16): `.env` is now loaded automatically (python-dotenv, real env vars win; `set -a; source .env; set +a` still works and is now optional); `/metrics` and `/metrics/` both answer 200 (`curl -sL` still works and is now optional).

Still open, with the workaround the scripts use:
- `make console` replays a full day into an empty store. Live demos on a fresh store set `STREAMLIT_SERVER_HEADLESS=true` and start the console after the store has data.
- Offline server-path spans have millisecond durations unless `ATLAS_MOCK_LATENCY_SCALE` is set; recordings that show the trace waterfall set it to 1.

## 16. Second code pass (O-CODE2, 2026-10-04)

`make test` = **419 passed** (372 unit, 42 integration, 5 budget gate; was 401). `make lint` clean, `uv lock --check` ok. Headline figures re-run and **unchanged**: baseline $56.28 / 10,184 requests / p95 3,827 ms / final-answer TTFT 1,427/1,702 ms; levers $37.00, $41.99, $47.07, $22.71, $19.07; judge 0.912/0.943; presets cost_spike $64.99, retry_storm $58.00, latency_regression $61.63, slow_provider $55.86, quality_drift $53.68, loop, ticket_flaky, mixed, context_bloat; incidents 1–4 $2.35/$1.64/$1.52/$1.66; loop demo 549 steps $4.90 / 6 steps $0.0086; langfuse-native $0.004514; budget gate 5 passed, cost_spike gate 2 failed (51,835 tokens).

| # | Change | Files | Moves |
|---|---|---|---|
| 1 | Grafana "Releases" annotation: `changes(atlas_build_info[5m]) > 0` never fires on a constant gauge; now `count by (version, prompt_version) (atlas_build_info unless atlas_build_info offset 5m)`. Verified with promtool 2.55.1 `test rules`: old expr returns nothing at a deploy, new one returns `{version="v1.1.0",prompt_version="v2"} 1` for 5 minutes after it, nothing before or after. | `deploy/grafana/dashboards/atlas-ops.json` | 9.x note "shipped JSON still uses changes(...)" is now false |
| 2 | `make judge`: `main` calls `init_langfuse` when keys are set and (`OFFLINE=0` or `--langfuse`; `make judge LANGFUSE=1`), and flushes; offline without the flag stays offline. `run_judge` sets `feedback_negative` from `user_feedback` ≤ 0.25, so every thumbs-down is judged. A run capped by `JUDGE_MAX_CALLS`/`--limit` reports `sampled == scored` (was limit + 1). | `evals/online_judge.py`, `Makefile` | `make judge` / `make feedback` output (below) |
| 3 | PII pseudonyms are **HMAC-SHA256** keyed with `ATLAS_PII_HASH_KEY` (`.env.example` shows `python -c "import secrets; print(secrets.token_hex(32))"`). Unset: public `DEMO_PII_HASH_KEY`, with one warning logged when `OFFLINE` is not 1. Same 8-hex format, so placeholders look the same; every hash value changes. `short_hash(value, salt="northwind", length=8, *, key=None)`; `salt` is now a domain label. New: `pii_hash_key()`, `DEMO_PII_HASH_KEY`, `PII_HASH_KEY_ENV`. Collector: `user.id`/`enduser.id` now `delete` (the attributes processor's `hash` is unkeyed SHA-256 and contrib 0.116.1 has no keyed option); `gen_ai.tool.call.arguments` stays `hash` (already masked at the source); limitation documented in the YAML. | `src/northwind/pii.py`, `.env.example`, `deploy/otel-collector.yaml` | 10.2 code excerpt and hash outputs; 10.x audit line; 10.1 table, 10.2 and 13.2 YAML excerpts |
| 4 | Replay masks agent input/output and tool arguments/results exactly like the live path (`mask_text(..., hash_ids=True)`, then clipped). The Langfuse mirror (`make replay LANGFUSE=1`) uses the store's trace id (`trace_context={"trace_id": ...}`) and the tags `tenant`, `feature`, `intent`, `prompt`, `scenario`, `replay`, so judge/feedback scores attach. `incidents/*/spans.jsonl` regenerated (content masked; costs, requests, p95 identical). | `simulator/replay.py`, `incidents/*/spans.jsonl` | 9.x note "tenant and intent tags only … new trace ids" is now false |
| 5 | `/feedback` stores and sends `reason`/`comment` through `mask_text(..., hash_ids=True)`. | `app/server.py` | none |
| 6 | `LatencyBudget().ttft_p95_ms` 1,200 → **2,000 ms**, documented as the final-answer TTFT (7.1's fourth clock; baseline p95 1,702 passes). `slo.BURN_RATE_ALERTS` 6×/6h is now `ticket`, matching `AtlasTaskSuccessBurnRateSlow`. | `src/northwind/latency.py`, `src/northwind/slo.py` | none quoted |
| 7 | `contains_pii` ignores values the KB itself publishes (`published_values()`: `NW-12345`, `helpdesk@`, `security@`, `network-eng@northwind.example`, `0800-555-0199`) plus `NW-00000`; any other e-mail, phone, ID or card still counts, and telemetry masking still masks them all. | `src/northwind/pii.py` | PII-in-output flags 678 → **0** (8.4, 10.1) |
| 8 | Mock honours `timeout=` (the agent passes `ATLAS_REQUEST_TIMEOUT_S`) as a whole-call deadline: raises `APITimeoutError` with `simulated_latency_ms = timeout`, which the agent records as the failed attempt's latency. `slow_provider` slows only `SLOW_PROVIDER_MODELS` (gpt-4.1-mini, gpt-4.1, gpt-4.1-nano); gpt-4o-mini, the first fallback, is unaffected. The agent's `CircuitBreaker` takes `ATLAS_ROUTER_ALLOWED_FAILS`/`ATLAS_ROUTER_COOLDOWN_S` (defaults 3/30, unchanged). The replay shares one breaker on the **replayed clock** (it used wall time, so `ATLAS_MAX_RETRIES=1` results depended on machine speed). `.env.chaos.example` updated to a config that passes offline. | `app/mock_llm.py`, `app/agent.py`, `simulator/replay.py`, `.env.chaos.example` | retry1 row; Section 7/Lab 4 "the mock never times out / slows every model" notes; `.env.chaos.example` values quoted in 7.6 and Lab 4 |
| 9 | `.env` loaded by `Settings.from_env()` via python-dotenv (`load_dotenv_once`, `override=False`, `ATLAS_DOTENV=0` disables; the test suite sets it). `/metrics` and `/metrics/` both 200. | `src/northwind/config.py`, `app/server.py`, `tests/conftest.py` | workarounds still work; notes saying ".env is not loaded" / "307" are now false |
| 10 | Numbers card: new §3a (slow-provider day), §4a (two weeks, drift table, dataset), per-user and per-feature/by-model lever figures, gate rows; fixed cost_spike soft-cap claim (ops crosses $25 at 16:08) and `make drift` 0.911 → 0.913. | `01-curriculum/numbers-card.md` | see card |

Lab 4 offline result: `BUDGET_GATE_INCIDENTS=slow_provider make budget-check` fails 1 (p95 8,755 ms). With `ATLAS_REQUEST_TIMEOUT_S=4 ATLAS_MAX_RETRIES=2 ATLAS_ROUTER_ALLOWED_FAILS=2 ATLAS_ROUTER_COOLDOWN_S=1800`: **5 passed**, p95 3,882 ms, $0.01114/session, 0 errors (ROUTER=1 too: 5 passed, p95 3,885 ms, $0.00962). The old reference values (retries 1, cooldown 120 s) fail: p95 10,349 ms, 58 errors, because `allowed_fails > max_retries` ends the breaking request in `error` and a 120 s cooldown re-probes the slow deployment almost every request on a 300-session day. Full day with the passing config: p95 3,859 ms, $43.29.

Moved figures (old → new): `make test` 401 → 419; retry_storm + `ATLAS_MAX_RETRIES=1` $50.13 → **$54.59**, p95 3,946 → 3,934 ms, errors 397 → **392**, failed attempts 806 → **799**, `resolved=9695` → `resolved=9700`, plus 795 fallback calls to gpt-4o-mini; `make judge` `sampled=712 scored=712 mean_overall=0.907 est_judge_cost=$1.5379` → `sampled=894 scored=894 mean_overall=0.909 est_judge_cost=$1.9310`; `make feedback` after it `joined_with_judge=457 agreement=80%` → `joined_with_judge=639 agreement=57%`; PII flags 678 → 0; hashes `<CARD:ed595cb8>` `<EMAIL:c8124ed3>` `<PHONE:953a8f02>` `<EMPLOYEE_ID:a116ca8c>` → `<CARD:594e45cc>` `<EMAIL:4470f829>` `<PHONE:d7602242>` `<EMPLOYEE_ID:4fbbe98e>` (demo key); brute force of `4fbbe98e` still prints `NW-04471` (0.017 s; the demo key is public); audit line `"user": "14c293e9"` → `"user": "ead71000"` (`answer_sha256` unchanged). Candidate check 136/170 vs 168/170 is not reproducible (random trace ids key the judge's noise): 4 runs gave v2 143–147, v1 166–170.

Tests added: `test_pii.py` (`test_hash_is_keyed_hmac`, `test_demo_key_warns_outside_offline`, `test_contains_pii_skips_documented_format_examples`, `test_contains_pii_skips_values_published_in_the_kb`), `test_mock_llm.py` (`test_mock_honours_timeout`, `test_slow_provider_spares_the_fallback_deployment`), `test_agent.py` (`test_slow_provider_timeout_trips_breaker_and_falls_back`, `test_breaker_uses_router_knobs`), `test_replay.py` (`test_replay_masks_span_content_like_the_live_path`, `test_langfuse_mirror_reuses_trace_id_and_tags`, `test_replay_breaker_runs_on_replayed_time`), `test_evals.py` (`test_judge_always_judges_thumbs_down`, `test_judge_cap_reports_sampled_equal_to_scored`, `test_judge_main_initialises_langfuse_when_keys_set`), `test_latency.py` (`test_default_budget_targets_final_answer_ttft`), `test_config.py` (`test_dotenv_loaded_without_overriding_real_env`), `test_server.py` (`test_metrics_answers_without_redirect`, `test_feedback_comment_is_redacted`). `test_slo.py::test_burn_alert` now expects `ticket` for 6×/6h.
