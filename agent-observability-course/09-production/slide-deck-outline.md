# Slide Deck Outline

> Slide-by-slide outline for every section. Uses the scene kits K1-K7 from `../../10-graphics/design-system.md` (K1 Hook, K2 Title card, K3 Teaching slide, K4 Architecture diagram, K5 Code/demo, K6 Recap card, K7 Bridge). Design rules: ≤ 12 words per slide, one concept per slide, ≤ 15 visible code lines, Deep Navy background, Teal accent, Red only for failures and SLO breaches, Amber only for thresholds, budgets and latency markers.
>
> Every lecture opens with K1 → K2 and closes with K6 (3 bullets) → K7. The **last lecture of each section** also ends with a 10-second **"You can now..." card** (three abilities; see `recording-guide.md` §9). These are listed once per section as "Standard open/close" and not repeated per lecture.
>
> Code slides use **only** the API forms in curriculum §6 and carry the corner note "APIs verified on langfuse 4 / opentelemetry-sdk 1.45 / semconv 0.66 (incubating)". Every dollar figure carries the footer "Simulated traffic · price table dated YYYY-MM-DD".

---

## Master diagram list

| ID | Diagram | Used in | Type | Spec |
|---|---|---|---|---|
| D1 | **Three pillars** | 1.2, 15.1, promo | K4 | Three columns on a shared base labelled "OpenTelemetry (wire format)": **Traces** (a small waterfall glyph), **Quality in production** (a judge/score glyph with a trend line), **Cost** (a meter glyph). Under the base: "where classic APM stops" as a dashed line with request/error/latency glyphs left of it and tokens/tools/steps right of it. Build: columns appear one per click; the APM line last |
| D2 | **Architecture** | 1.3, 13.4, 14.1 | K4 | Atlas (FastAPI box) → OTel SDK → OTel Collector (processors: attributes, tail sampling) → fan-out to **Langfuse** (traces, scores, prompts, datasets) and **Prometheus → Grafana** (metrics). Side: **LiteLLM** (price table, Router, budgets) inside Atlas; **DeepEval judge** reading from Langfuse and writing scores back; **Ops Console** reading the local store. Second build: dashed alternatives (LangSmith, Phoenix, Datadog) hanging off the collector |
| D3 | **Trace waterfall of an agent step** | 3.1, 5.1, 5.2, 5.6, 11.1, promo | K4 | Horizontal time axis. Root span `agent atlas` (teal). Children stepping right: `retriever search_knowledge_base` → `generation gpt-4.1-mini` (with a usage chip: in / out / cached) → `tool lookup_ticket` (arguments chip, result chip, redacted) → `generation` (step 2) → … Build 1: happy path, 3 steps. Build 2 (5.6, 1.1): the same tool span repeating 12 times in red with the generation chips growing wider each step (context bloat). Build 3 (11.1): a timeline ruler with T0 (first alert), blast radius bracket, hypothesis marker |
| D4 | **Langfuse on OpenTelemetry** | 4.1, 12.1 | K4 | Left: OTel span (attributes: `gen_ai.*`). Right: Langfuse observation types stacked (agent, tool, generation, retriever, guardrail, chain) as coloured chips, with trace / session / user / environment / release as outer rings. An arrow labelled "SDK v4 = OTel exporter + semantics". Second build (12.1): a red "not portable" bracket around scores, prompts, datasets |
| D5 | **Token anatomy** | 6.1, 6.4, 6.5, promo | K4 / stacked bar | One request as a horizontal stacked bar: **input** (grey) split into **cached input** (teal hatch) and uncached; **output** (amber); **reasoning** (amber hatch, "billed as output"); small extra segments: **tool schemas** (in input), **retries** (a second faded bar behind), **judge call** (a small separate bar). Labels map to OpenAI usage fields: `prompt_tokens_details.cached_tokens`, `output_tokens_details`. Build 2 (6.4): the cached hatch grows; 6.5: the input bar shrinks |
| D6 | **Cost rollup tree** | 6.3, 6.9, 14.4 | K4 | Leaves at the bottom: generations with a cost chip each. Roll up: generation → **request** → **session** → **user** → **tenant** (hr / it / ops / logistics) → **Northwind total**. A parallel dashed roll-up by **feature** (kb_answer, ticket, password_reset, shipment) crossing the tree. Amber callout at the tenant level: "cost per resolved session". Build: leaves first, then each level |
| D7 | **Latency budget** | 7.1, 7.2, 7.6, 5.4 | K4 / waterfall | Per-step budget bars stacked into an end-to-end budget bar with an amber target line (student-set, labelled "example"). Segments per step: queue → **TTFT** → **TPOT × tokens** → tool call → next step. Build 2: a p50 bar under budget (teal) and a p95 bar overshooting (red). Build 3 (7.6): a fallback segment appearing when the provider segment exceeds its timeout |
| D8 | **SLO / error budget burn** | 9.1, 9.5, 11.3 | K4 / chart | Top: an SLI line (e.g., task success) with the SLO as an amber horizontal line. Bottom: **error budget remaining** draining over 30 days; two burn-rate slopes (fast burn = red steep, slow burn = amber shallow) with the alert thresholds as dashed lines. Build: SLI first, then budget, then the two burn scenarios |
| D9 | **Incident timeline** | 11.1, 11.2-11.4 reveals, 11.5 | K4 | Horizontal timeline: **T-∞ change** (e.g., prompt v2 deployed, top-k raised) → **T0 first symptom in traces** → **T+ alert (or no alert, red "silent")** → **detection** → **mitigation** → **root cause** → **postmortem actions** (chips: budget, alert, test). Blast radius bracket above (tenants affected). Reused per incident with the real timestamps from the fixture |
| D10 | **Observability threat model** | 10.1, 10.2 | K4 | Prompt (PII chip) → tool result (record chip) → span → exporter → backend → judge (sees everything) → dashboards (shared with stakeholders). Shields at: SDK `mask=`, Collector attribute processor, backend retention, RBAC. Red dots where PII leaks without a shield |
| D11 | **Ops dashboard mock-up** | 9.3, 14.3, promo | K4 / mock-up | Six panels: p95 latency (line + amber SLO), cost per resolved session by tenant (bars), task success / containment (gauge), tool error rate (line), judge score (line with drift band), budget remaining per tenant (bars with red hard cap). Release annotations as vertical dashed lines |
| D12 | **Backend decision matrix** | 12.5, 1.3 preview | K3 table | Langfuse / LangSmith / Phoenix / OpenLLMetry / Datadog × control, cost model, compliance/self-host, features, lock-in (qualitative ●●●). From `../10-resources/backend-decision-matrix.md` |

---

## Section 1: Welcome: The $4,000 Weekend

Standard open/close for each lecture.

**1.1 The $4,000 weekend (DM):** K1 cold open on the Ops Console cost meter climbing over **D3 build 2** (red repeating tool span), footer `Simulated traffic` → K5 the fixed run (step limit event, budget guard refusing, alert card) → K3 "By Section 14 you can see, explain and stop this" → K7.
**1.2 What LLMOps means for agents (SL):**
1. K1 "Your APM says everything is fine"
2. K3 Agents are: non-deterministic · multi-step · tool-using · token-metered (4 chips)
3. K4 **D1** build 1: three pillars
4. K4 **D1** build 2: where classic APM stops
5. K3 "MLOps tools watch models. You need to watch runs."
6. K6 recap
**1.3 The stack (SL):** K4 **D2** built component by component → K3 "OTel first, backend second: the portability argument" → K4 **D2** build 2 (alternatives dashed) → K6.
**1.4 Meet Atlas and the swarm (SC):** K5 `app/` tree → K3 four tools, four tenants → K5 `simulator/scenarios.py` incident list → K3 "Every lab has an offline path" → K6.
**1.5 Roadmap (SC):** K3 the 15 sections as 5 arcs (Foundations / See / Control / Operate / Choose and ship) → K5 repo tree and Makefile → K3 build log prompt → K3 version banner explained → K6.

## Section 2: Setup and Your First Trace

**2.1 Accounts, keys and caps (SC):** K3 account list (text labels, no logos) → K5 masked OpenAI cap screen → K3 "≈$5-15 total (check current pricing)" → K5 `.env.example`.
**2.2 uv and the Makefile (SC):** K5 throughout; K3 Makefile targets table; K3 "Never commit .env".
**2.3 Quick win (SC):** K5 `curl` → K5 Langfuse trace collapsed → expanded top-down (**D3** live) → K3 "The whole course explains this screen" → K6.
**2.4 Offline mode (SC):** K5 replay progress → K5 Ops Console first appearance (reference frame) → K3 "Free, deterministic, repeatable".
**2.5 Lab 1:** K3 checklist slide.
**Section-end card:** "You can now: run Atlas · read your first trace · replay a day for free".

## Section 3: Tracing Fundamentals and the GenAI Semantic Conventions

**3.1 Traces, spans, context (SL):** K4 **D3** build 1 with callouts: trace id, parent, attributes, events, status → K3 context propagation (two boxes, one arrow) → K3 sampling (head vs tail) → K6.
**3.2 Manual OTel (SC):** K5 `TracerProvider(resource=Resource.create({"service.name": "atlas"}))` → K5 `start_as_current_span` → K5 `ConsoleSpanExporter` output → K5 `BatchSpanProcessor(OTLPSpanExporter(...))` → K6.
**3.3 GenAI semconv (SL):** K3 "Naming things so tools understand them" → K3 attribute families, one per slide: operation and model · usage (input, output, cache read, reasoning) · tool (name, arguments, result) · agent and conversation → K5 `from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g` → K3 **"Incubating: names may change. Pin your version."** (amber) → K6.
**3.4 Tag every span (SC):** K5 `genai_attrs.py` helpers → K5 applied in `agent.py` → K5 console exporter showing `gen_ai.*` → K6.
**3.5 OpenInference (SC):** K5 `OpenAIInstrumentor().instrument(tracer_provider=provider)` → K3 "Free: generations. Still yours: agent, tool, retriever spans" → K3 note on the otel-contrib instrumentor → K6.
**3.6 Break it (DM):** three K1 (failure, red trace) → K5 (the fix) → K3 AFTER (teal) pairs: orphan async span · tool span outside agent span · double instrumentation.
**Section-end card:** "You can now: emit OTel spans · tag them with gen_ai.* · spot a broken trace".

## Section 4: Langfuse Deep Dive

**4.1 Langfuse on OTel (SL):** K4 **D4** build → K3 observation types, one line each → K3 trace / session / user / environment / release → K6.
**4.2 @observe (SC):** K5 `@observe(as_type="agent")` → K5 `get_client()` and `update_current_generation(model=, usage_details=, cost_details=)` → K5 `update_current_trace(session_id=, user_id=, tags=)` (corner note: "verify exact name on installed SDK") → K6.
**4.3 Sessions, users, tenants (SC):** K3 mapping table (department → tag, employee → user_id, conversation → session_id) → K5 Langfuse filters.
**4.4 Prompts (SC):** K5 `create_prompt(..., labels=["production"])` → K5 `get_prompt(..., label="production", fallback=..., cache_ttl_seconds=60)` → K3 "This sets up Incident 3" (amber).
**4.5 Scores and datasets (SC):** K5 `score_current_trace(...)`, `create_score(...)` → K5 `create_dataset_item(..., source_trace_id=...)` → K3 "Production → regression suite" (one-line factual bridge to Course 2).
**4.6 Masking, sampling, cost of observability (SC):** K5 `mask=`, `sample_rate`, `blocked_instrumentation_scopes`, `flush()`/`shutdown()` → K3 "Observability has a bill too".
**4.7 Challenge (CH):** K3 spec card (`as_type="guardrail"`, boolean score) → full-screen **pause card** → K5 solution → K3 "Two common mistakes".
**Section-end card:** "You can now: type your observations · slice by tenant · version your prompts".

## Section 5: Agent Observability Patterns

**5.1 What an agent trace must answer (SL):** K3 six questions, one per slide → K4 **D3** annotated with which span answers which → K6.
**5.2 Tool loop (SC):** K5 step spans, tool spans, step-limit event, escalation generation → K4 **D3** as recorded.
**5.3 RAG spans (SC):** K5 retriever observation (query, top-k, scores) → K3 empty-result rate · grounding flag as metrics.
**5.4 Streaming (SC):** K4 **D7** TTFT / TPOT segments → K5 `completion_start_time`, `GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK`.
**5.5 Logs vs traces vs metrics (SL):** K3 three columns → K3 "Cardinality trap: never a user_id label" (red) → K6.
**5.6 Break it: the loop (DM):** K1 **D3 build 2** in the real trace → K5 step limit + error surfacing → K3 AFTER.
**Section-end card:** "You can now: trace a tool loop · measure retrieval · stream and still measure".

## Section 6: Cost Engineering (signature section)

**6.1 Token anatomy (SL):** K1 "Cost per request is not one number" → K4 **D5** segment by segment → K3 OpenAI usage fields (Chat vs Responses) → K6.
**6.2 Price table (SC):** K5 `litellm.model_cost[...]`, `cost_per_token(...)` → K5 pinned fallback with a date → K3 "Every price: check current pricing".
**6.3 Rollups (SC, Part A/B):** K4 **D6** build → K5 `cost.py` → K5 `report.py` output → K3 "cost per resolved session" (amber callout).
**6.4 Caching (SC):** K4 **D5** cached hatch grows → K5 `prompt_cache_key`, stable prefix → K5 BEFORE/AFTER card.
**6.5 Context diet (SC):** K4 **D5** input shrinks → K5 `tokens.py` helpers → K5 tokens per step BEFORE/AFTER.
**6.6 Routing (SC, Part A/B):** K4 mini-diagram: request → Router → `gpt-4.1-mini` default / `gpt-4.1` escalation → K5 `Router(model_list=[...], fallbacks=[...], ...)` → K5 cost BEFORE/AFTER.
**6.7 Budgets (SC):** K3 soft cap (degrade) vs hard cap (refuse) → K5 `budget.py` EWMA → K5 Prometheus counter.
**6.8 Challenge: −40% (CH):** K3 spec card → **pause card** → K5 reference solution in the console → K3 "Where the 40% came from" (stacked bar of the three cuts).
**6.9 Project 1 (AS):** K3 brief; K3 report sections.
**Section-end card:** "You can now: price every token · roll up cost by tenant · prove a 40% saving".

## Section 7: Latency and Reliability

**7.1 Latency budgets (SL):** K1 "Average latency is 1.8 s" (then p95 9 s in red) → K4 **D7** build → K3 "p95, not the mean" → K5 worksheet preview → K6.
**7.2 Measure (SC):** K5 `latency.py` percentiles → K5 histograms → K5 Ops Console latency page.
**7.3 Timeouts and retries (SC):** K3 bounded retries with jitter (a small timeline) → K3 "A retry storm is a cost event" (red) → K5.
**7.4 Fallbacks and circuit breakers (SC):** K4 **D7** build 3 → K5 `Router(fallbacks=..., allowed_fails=..., cooldown_time=...)` → K3 "What to log when a fallback fires".
**7.5 Rate limits and degradation (SL):** K3 429 handling · per-tenant concurrency · shedding · degraded-mode message → K6.
**7.6 Chaos demo (DM):** K1 p95 climbing (Grafana) → K5 tuning → K3 AFTER: p95 holds, fallback rate up, cost delta.
**Section-end card:** "You can now: set a latency budget · measure p95 · survive a slow provider".

## Section 8: Quality in Production

**8.1 Offline evals are not enough (SL):** K3 four ways production differs (shift, new intents, changes, silent regressions) → K3 definition of "quality in production" → K6.
**8.2 Sampled judge (SC):** K5 `sampling.py` → K5 `GEval(name=, criteria=, evaluation_params=[...], threshold=, model=)` → K5 scores in Langfuse → K3 "The judge has a bill" (line item card).
**8.3 Feedback (SC):** K5 `/feedback` → K3 survivorship bias (who rates?) → K5 correlation chart.
**8.4 Guardrail metrics (SC):** K5 three time series.
**8.5 Drift (SC):** K3 window comparison → K5 `drift.py` PSI-lite → K5 weekly report.
**8.6 Bad trace → regression test (SC):** K5 `to_dataset.py` → K3 loop diagram (production → dataset → offline eval → new prompt version).
**Section-end card:** "You can now: judge live traffic · trust feedback · detect drift".

## Section 9: Dashboards, SLOs and Alerting

**9.1 SLIs (SL):** K3 six SLIs, one per slide → K4 **D8** build → K3 "Error budgets and burn rate" → K6.
**9.2 Prometheus (SC):** K5 `Counter`, `Histogram`, `make_asgi_app()` at `/metrics` → K5 compose scrape → K3 low-cardinality labels (red for `user_id`).
**9.3 Grafana (SC):** K4 **D11** panel by panel → K5 import `atlas-ops.json` → K5 tenant variable and release annotations.
**9.4 Langfuse dashboards (DM):** K5 saved views.
**9.5 Alerts and runbook (SC):** K4 **D8** burn-rate thresholds → K5 alert rules → K3 runbook template fields → K3 alert-fatigue rules.
**Section-end card:** "You can now: define an SLO · ship a dashboard · write an alert with a runbook".

## Section 10: Privacy, Security and Governance of Telemetry

**10.1 Threat model (SL):** K4 **D10** build (red dots first) → K6.
**10.2 Masking (SC):** K5 `mask=` → K5 collector attribute processor YAML → K4 **D10** shields appear.
**10.3 Retention and access (SL):** K3 retention · project per environment · RBAC · tags vs projects → K6.
**10.4 Regulatory obligations (TH):** avatar + K3 cards: record-keeping expectations · audit trails · keep vs never log · **"Not legal advice. Verify with counsel."** footer on every card.
**Section-end card:** "You can now: mask PII in spans · set retention · separate tenants".

## Section 11: Incident Labs (engagement centrepiece)

**11.1 Read an incident like an SRE (SL):** K4 **D9** build → K3 the template fields → K6.
**11.2-11.4 Incidents (CH, Part A/B):** Part A: K1 the brief card (timestamp, symptom, "nothing else alerting") → K5 investigation in the Ops Console and Langfuse (with one `[RED HERRING]`) → full-screen **pause card** ("Eight minutes. Spans and brief. Go.") with a static timer graphic. Part B: K3 recap of the brief → K5 reveal walkthrough → K4 **D9** with the real timestamps → K5 the fix applied and re-run → K6.
**11.5 Postmortem (SC):** K3 template sections → K3 "Every action item maps to: instrumentation · budget · test".
**11.6 Project 2 (AS):** K3 brief; K3 "No solution exists in the repo".
**Section-end card:** "You can now: read a timeline · find root cause from spans · write a blameless postmortem".

## Section 12: Portability and Alternatives

**12.1 Lock-in and the OTel escape hatch (SL):** K4 **D4** build 2 (red "not portable" bracket) → K6.
**12.2 LangSmith (SC):** K5 `traceable`, `wrap_openai` → K5 the same trace in LangSmith → K3 what differs.
**12.3 Phoenix (SC):** K5 exporter endpoint change (one line) → K5 Phoenix → K3 OpenInference vs GenAI conventions.
**12.4 OpenLLMetry, Datadog (SL):** K3 "You already have an APM" decision tree → K3 hybrid setups → K6.
**12.5 Decision matrix (SL):** K3 **D12** row by row → K3 decision record template → K6.
**Section-end card:** "You can now: swap backends · know what won't move · justify the choice".

## Section 13: Deploying the Stack and CI Budget Gates

**13.1 Self-host Langfuse (SC):** K5 compose file (folded) with the "verify against current compose" note → K5 services up → K5 first project.
**13.2 OTel Collector (SC):** K4 **D2** collector zoom: receivers → processors → exporters ×2 → K5 YAML blocks.
**13.3 CI budget gate (SC):** K5 `test_budget_gate.py` assertions → K5 `ci.yml` → K5 failing PR (red) → K5 passing PR (teal) → K5 release tag in Langfuse.
**13.4 Production readiness (SL):** K3 checklist groups: sampling · back-pressure · secrets · dashboards as code · alert ownership → K6.
**13.5 Chaos: kill the backend (DM):** K1 Langfuse container stopped → K5 Atlas still answering → K5 exporter timeouts and queue limits in the log → K3 "Drop telemetry, never requests".
**Section-end card:** "You can now: self-host the stack · route telemetry through a collector · gate a PR on cost".

## Section 14: Capstone

**14.1 Brief (SL):** K3 requirements → K3 acceptance criteria → K4 **D2** as the target → K6.
**14.1a Gate (TH):** full-screen pause card: "Stop. Build it from the brief. Time box: one week."
**14.2-14.3 Reference solution (SC, Part A/B):** K5 throughout; K4 **D6** in 14.2, **D11** in 14.3.
**14.4 Weekly report (SC):** K5 `report.py` output → K3 "One page your manager reads".
**14.5 Portfolio (TH):** K3 checklist (README, dashboard screenshots with masks, weekly report, postmortems).
**14.6 Domain swap (AS):** K3 "Same stack, different agent" → K3 what changes (SLIs, tools, tenants) vs what stays (attributes, pipeline) → instrumentation template.
**Section-end card:** "You can now: operate an agent end to end · report it weekly · instrument any agent".

## Section 15: Wrap-up and Careers

**15.1 (TH):** K4 **D1** recap → K3 Build → Test → Deploy → Operate path (course names only; promotional detail only in 15.4).
**15.2 Careers (TH):** K3 role titles (LLMOps engineer, AI platform engineer, AI SRE) → K3 interview question examples (from `../10-resources/interview-questions.md`) → K3 the ROI pitch structure → **no salary figures**.
**15.3 Practice test:** none.
**15.4 Bonus (TH):** only lecture with course links/coupons (Udemy bonus rules; verify).

---

## Slide count estimate

| Section | SL lectures | Est. slides (incl. open/close, section-end card) |
|---|---|---|
| 1 | 2 (+DM/SC framing) | 40 |
| 2 | 0 | 20 |
| 3 | 2 | 45 |
| 4 | 1 | 40 |
| 5 | 2 | 35 |
| 6 | 1 | 55 |
| 7 | 2 | 40 |
| 8 | 1 | 35 |
| 9 | 1 | 35 |
| 10 | 2 (+TH) | 25 |
| 11 | 1 | 40 (pause cards, brief cards, D9 ×3) |
| 12 | 3 | 30 |
| 13 | 1 | 30 |
| 14 | 1 (+TH) | 25 |
| 15 | 0 (+TH) | 10 |
| **Total** | 20 | **≈ 505** (planning estimate) |
