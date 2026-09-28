# QA Checklist

> Run this before any lecture is marked final (milestone M6 in `production-schedule.md`) and again for the full course before submission. Complements the Quality Bar in `../../09-heygen/PRODUCTION-GUIDE.md` and `../07-udemy-listing/publish-checklist.md`.

---

## 1. Per-lecture checks (every video lecture)

### Technical / content
- [ ] Matches `../01-curriculum/curriculum.md`: ID, title, objective and key points all covered; runtime within ±20% of the curriculum minutes
- [ ] Lectures over 10 minutes split into Part A / Part B where the curriculum says so (6.3, 6.6, 11.2, 11.3, 11.4, 14.2, 14.3), each part with its own hook and bridge
- [ ] Engagement mechanics present (see `recording-guide.md` §9): section-end "You can now..." card on the last lecture of each section; BEFORE/AFTER card on every change that alters a number; failure-first opening on build sections; version-pin note on the first slide of code lectures
- [ ] Every API call and attribute on screen uses **only** the forms in curriculum §6; none of the banned idioms (`opentelemetry-instrumentation-openai-v2`, hand-typed `gen_ai.*` strings instead of `g.GEN_AI_*` constants, Langfuse v2/v3 idioms such as `langfuse.trace()` / `langfuse_context`)
- [ ] Version banner visible on code lectures: "APIs verified on langfuse 4 / opentelemetry-sdk 1.45 / semconv 0.66 (incubating)"
- [ ] "Incubating, names may change" said or shown wherever a `gen_ai.*` attribute is introduced
- [ ] File paths on screen match `03-code/` exactly
- [ ] **Numbers stated (cost, tokens, p95, cached share, judge score) match the `[NUMBERS]` block for the frozen replay and the number visible on screen**; live-request lectures quote ranges and say "live"
- [ ] Every dollar figure carries "Simulated traffic · price table dated YYYY-MM-DD"; prices are labelled "check current pricing"
- [ ] Governance statements are labelled "not legal advice" (10.4 and anywhere else they appear)
- [ ] No promotional content outside 15.4; cross-links to Courses 2 and 3 are one-line, factual, link-free

### Audio / video
- [ ] 1920×1080, 30 fps, H.264; no dropped frames or stutter
- [ ] Integrated loudness -16 LUFS (±1), true peak ≤ -1 dBTP; music ≤ -24 LUFS under voice; no music under incident investigations
- [ ] No clipping, hum, room echo, mouth clicks or keyboard thuds louder than the voice; room tone under cuts
- [ ] Avatar: lip sync, pronunciation glossary applied (Langfuse, OpenTelemetry, OTLP, OpenInference, LiteLLM, DeepEval, Prometheus, Grafana, TTFT, TPOT, p95, SLO, EWMA, PSI, Northwind, Atlas)
- [ ] Visual change at least every 30 s; avatar ≤ 60 s continuous; hook in first 15 s; 3-bullet recap; bridge
- [ ] Code font legible at 720p playback (JetBrains Mono 20-22 px); ≤ 15 lines visible

### Dashboard and trace capture (Track C)
- [ ] Langfuse at 125-150% zoom, Grafana at 125% kiosk, Ops Console at 100% with ≥ 18 px fonts
- [ ] **25% test passed:** span names, attribute names and the discussed number legible at ≈480×270
- [ ] Waterfall expanded top-down in execution order; zoom-and-hold on the discussed element; cursor large and parked when idle
- [ ] Ops Console theme, page order, sidebar width, window size and date range identical to the Section 2 reference frame
- [ ] On-screen labels present (`Langfuse · trace view`, `Grafana · Atlas Ops`, `Ops Console · Cost`, …)

### Security scrub
- [ ] No API keys, Langfuse secret keys, OTLP auth header values, `.env` contents, project ids, organisation names, regions in URLs
- [ ] Address bar cropped in Langfuse/Grafana scenes; OBS masks in place over project switcher, user menu, GitHub org avatar
- [ ] No personal emails, home paths, usernames, browser autofill, notifications
- [ ] Persona and tenant names are the fixture's fictional names; PII masking on in demos
- [ ] Incident Part A recorded from a checkout with no `solution.md` in any visible file tree

### Accessibility
- [ ] Captions present, corrected for domain terms and attribute names, synced (±0.5 s), ≤ 2 lines, ≤ ~42 chars/line
- [ ] Diagrams narrated (meaning doesn't depend on seeing them): the waterfall, the rollup tree, the burn-rate chart
- [ ] Pass/fail and SLO breach use ✓/✗ or labels, not color alone; text contrast meets WCAG AA (design system)
- [ ] No flashing content > 3 flashes/second (the cost meter counter is a smooth count, not a flash)
- [ ] Downloadable resources available as text-based PDF/Markdown

---

## 2. Code verification per lecture

> Run on a clean machine with the pinned versions. Record the date and installed versions (`uv pip list | grep -E "langfuse|opentelemetry|openinference|litellm|deepeval|langsmith|prometheus"`). Lectures without code show "n/a".

| ID | Lecture | Type | Verification | Pass | Date |
|---|---|---|---|---|---|
| 1.1 | The $4,000 weekend: watch an agent burn money in real time | DM | Cost meter climbs on the `loop` scenario against the frozen replay; fixed run (step limit, budget guard, alert) recorded in the same session; `Simulated traffic` label present throughout | [ ] | |
| 1.2 | What LLMOps means for agents (and why MLOps tools miss it) | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 1.3 | The observability stack you will build | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 1.4 | Meet Atlas and the swarm | SC | `app/` and `simulator/` trees on screen match the repo; `OFFLINE=1 make swarm` runs | [ ] | |
| 1.5 | Course roadmap and how to get the most out of it | SC | `make` targets listed on screen exist in `03-code/Makefile`; version banner text matches pinned versions | [ ] | |
| 1.6 | Quiz: Foundations | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 2.1 | Accounts, keys and spending caps | SC | Provider cap screens masked (account ids, billing); `.env.example` has placeholders only; "check current pricing" said | [ ] | |
| 2.2 | Project setup with uv and the Makefile | SC | Fresh clone → `uv sync` → `make test` green offline on macOS, Windows (WSL) and Linux | [ ] | |
| 2.3 | Quick win: one request, one trace | SC | Live `curl` produces a trace in Langfuse with agent, retriever, generation (usage + cost) and tool spans; address bar cropped | [ ] | |
| 2.4 | Offline mode: a full day of traffic for free | SC | `OFFLINE=1 make replay` fills the local store deterministically for the chosen seed; Ops Console reference frame saved for the consistency check | [ ] | |
| 2.5 | Lab 1: Environment and first trace | LAB | Complete the lab as a student on a clean machine (offline path first, then with keys); expected outputs match | [ ] | |
| 2.6 | Quiz: Setup and tracing basics | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 3.1 | Traces, spans and context in five minutes | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 3.2 | Code-along: manual OpenTelemetry instrumentation of Atlas | SC | `TracerProvider`, `Resource.create`, `start_as_current_span`, `ConsoleSpanExporter`, `BatchSpanProcessor(OTLPSpanExporter(...))` match curriculum §6 | [ ] | |
| 3.3 | GenAI semantic conventions: naming things so tools understand them | SL | Every attribute shown is in curriculum §6 verified list; "incubating, names may change" said on screen | [ ] | |
| 3.4 | Code-along: tag every LLM, tool and agent span correctly | SC | Console exporter output shows `gen_ai.*` attributes from `g.GEN_AI_*` constants; no hand-typed attribute strings | [ ] | |
| 3.5 | Auto-instrumentation with OpenInference | SC | `OpenAIInstrumentor().instrument(tracer_provider=provider)` from `openinference.instrumentation.openai`; the otel-contrib instrumentor is NOT shown | [ ] | |
| 3.6 | Break it: orphan spans, missing context and double counting | DM | Each broken case (orphan async span, tool span outside agent, double instrumentation) reproduces and `tests/integration/test_spans.py` catches it after the fix | [ ] | |
| 3.7 | Lab 2: Instrument a new tool end to end | LAB | Complete the lab as a student on a clean machine (offline path first, then with keys); expected outputs match | [ ] | |
| 3.8 | Quiz: Tracing and semantic conventions | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 4.1 | How Langfuse sits on OpenTelemetry | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 4.2 | Code-along: `@observe` and observation types | SC | `observe(as_type=...)`, `get_client()`, `update_current_generation(...)`, `update_current_trace(...)` forms match §6; the "verify exact name on installed SDK" note is visible for `update_current_trace` | [ ] | |
| 4.3 | Sessions, users, tenants and tags: slicing production | SC | Code on screen matches `03-code/` file and curriculum §6; runs offline where the curriculum says so | [ ] | |
| 4.4 | Prompt management and versions | SC | `create_prompt(..., labels=[...])` and `get_prompt(..., label=, fallback=, cache_ttl_seconds=)` run on langfuse 4.15.x | [ ] | |
| 4.5 | Scores, datasets and the feedback loop | SC | `score_current_trace`, `create_score`, `create_dataset_item(source_trace_id=)` run; dataset item appears in the UI | [ ] | |
| 4.6 | Masking, sampling and cost of observability itself | SC | `mask=`, `sample_rate`, `blocked_instrumentation_scopes`, `flush()`, `shutdown()` behave as narrated | [ ] | |
| 4.7 | Challenge: add a guardrail observation | CH | Spec card matches the guardrail solution; pause card shown; solution passes tests; two mistakes demonstrated | [ ] | |
| 4.8 | Quiz: Langfuse | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 5.1 | What an agent trace must answer | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 5.2 | Code-along: tracing the tool loop step by step | SC | Code on screen matches `03-code/` file and curriculum §6; runs offline where the curriculum says so | [ ] | |
| 5.3 | RAG spans: retrieval quality is a production metric | SC | Code on screen matches `03-code/` file and curriculum §6; runs offline where the curriculum says so | [ ] | |
| 5.4 | Streaming: time to first token and tokens per second | SC | TTFT/TPOT computed from real stream events; `completion_start_time` and `GEN_AI_RESPONSE_TIME_TO_FIRST_CHUNK` set | [ ] | |
| 5.5 | Logs vs traces vs metrics for agents | SL | JSON log lines carry `trace_id`; no `user_id` label in any Prometheus metric | [ ] | |
| 5.6 | Break it: the loop you can only see in a trace | DM | `loop` scenario reproduces the runaway waterfall; step limit stops it; error surfaced | [ ] | |
| 5.7 | Lab 3: Trace a multi-step ticket escalation | LAB | Complete the lab as a student on a clean machine (offline path first, then with keys); expected outputs match | [ ] | |
| 5.8 | Quiz: Agent patterns | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 6.1 | Where the money goes: token anatomy | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 6.2 | Code-along: a price table you can trust | SC | `litellm.model_cost[...]`, `cost_per_token(...)` forms match §6; fallback table dated; "check current pricing" label present | [ ] | |
| 6.3 | Cost per request, session, user, tenant and feature | SC | Rollups sum correctly (generations → request → session → user → tenant); `report.py` output matches `[NUMBERS]` block | [ ] | |
| 6.4 | Prompt caching: the cheapest win | SC | `prompt_cache_key` set; cached token share visible in usage; BEFORE/AFTER from the same replay | [ ] | |
| 6.5 | The context diet | SC | Tokens per step BEFORE/AFTER from the same replay; `tokens.py` works without tiktoken | [ ] | |
| 6.6 | Small-model-first routing with LiteLLM Router | SC | `Router(model_list=, fallbacks=, num_retries=, timeout=, allowed_fails=, cooldown_time=)` form matches §6; cost delta from the same replay | [ ] | |
| 6.7 | Budgets and anomaly alerts per tenant | SC | Soft cap degrades, hard cap refuses politely; EWMA anomaly fires on the injected spike; counter increments | [ ] | |
| 6.8 | Challenge: cut Atlas's daily cost by 40% | CH | The 40% figure is produced by the reference solution on the frozen replay; three cuts shown separately | [ ] | |
| 6.9 | Project 1: The showback report | AS | Brief complete; rubric + example solution run | [ ] | |
| 6.10 | Quiz: Cost engineering | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 7.1 | Latency budgets for agents | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 7.2 | Code-along: measure TTFT, TPOT and p95 from spans | SC | Percentiles from `latency.py` agree with a numpy check; histogram buckets sensible | [ ] | |
| 7.3 | Timeouts, retries and backoff done right | SC | Code on screen matches `03-code/` file and curriculum §6; runs offline where the curriculum says so | [ ] | |
| 7.4 | Fallbacks and circuit breakers with the Router | SC | Fallback fires when the primary is slowed; cooldown and half-open behaviour as narrated | [ ] | |
| 7.5 | Rate limits, queues and graceful degradation | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 7.6 | Chaos demo: slow provider during peak | DM | `slow_provider` injected; p95 climbs then recovers after tuning; fallback rate and cost delta shown from the same run | [ ] | |
| 7.7 | Lab 4: Hold p95 under 4 seconds during chaos | LAB | Complete the lab as a student on a clean machine (offline path first, then with keys); expected outputs match | [ ] | |
| 7.8 | Quiz: Latency and reliability | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 8.1 | Offline evals are not enough | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 8.2 | Code-along: sampled LLM-as-judge on live traces | SC | `GEval(name=, criteria=, evaluation_params=[...], threshold=, model=)` matches §6; scores land in Langfuse; `JUDGE_MAX_CALLS` cap active; judge cost line item shown | [ ] | |
| 8.3 | Capturing user feedback that means something | SC | `/feedback` writes scores; correlation chart from the frozen week | [ ] | |
| 8.4 | Guardrail and safety metrics | SC | Code on screen matches `03-code/` file and curriculum §6; runs offline where the curriculum says so | [ ] | |
| 8.5 | Drift detection: compare this week to last week | SC | Drift report flags the injected `prompt_regression` week; thresholds stated | [ ] | |
| 8.6 | From bad trace to regression test | SC | Promoted trace appears as a dataset item; offline eval run shown against the new prompt version | [ ] | |
| 8.7 | Lab 5: Build the quality page of the Ops Console | LAB | Complete the lab as a student on a clean machine (offline path first, then with keys); expected outputs match | [ ] | |
| 8.8 | Quiz: Online evaluation | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 9.1 | SLIs for agents that leadership understands | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 9.2 | Code-along: Prometheus metrics from Atlas | SC | `/metrics` served by `make_asgi_app()`; Prometheus target UP; labels low-cardinality | [ ] | |
| 9.3 | Grafana: the Atlas Ops dashboard | SC | `atlas-ops.json` imports cleanly on the pinned Grafana version; tenant variable works; kiosk mode, 125% zoom | [ ] | |
| 9.4 | Langfuse dashboards and saved views | DM | Scenario reproduces on the frozen replay; numbers on screen match `[NUMBERS]` | [ ] | |
| 9.5 | Alert rules and the runbook | SC | Alert rules load; burn-rate thresholds match D8; runbook fields filled for each alert | [ ] | |
| 9.6 | Lab 6: Ship the dashboard and one alert | LAB | One alert fires during the replay on camera | [ ] | |
| 9.7 | Quiz: SLOs and alerting | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 10.1 | Your traces are a data breach waiting to happen | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 10.2 | Code-along: masking in the SDK and the collector | SC | `mask=` and the collector attribute processor both redact the same test string; hashes preserved for joins | [ ] | |
| 10.3 | Retention, access and tenant separation | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 10.4 | Regulatory logging obligations (not legal advice) | TH | "Not legal advice" footer on every card; EU AI Act statements flagged "verify with counsel"; no jurisdiction-specific claims beyond the curriculum | [ ] | |
| 10.5 | Quiz: Governance | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 11.1 | How to read an incident like an SRE | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 11.2 | Incident 1: Monday's cost spike (investigate, then reveal) | CH | Part A recorded from a checkout with no `solution.md`; one red herring present and eliminated; pause card shown; Part B reveal matches `solution.md` (context bloat + retry storm on one tenant) | [ ] | |
| 11.3 | Incident 2: p95 doubled after lunch | CH | Same protocol; reveal matches `solution.md` (provider slowdown compounded by top-k change); fix = fallback + k | [ ] | |
| 11.4 | Incident 3: users are unhappy but nothing is red | CH | Same protocol; reveal matches `solution.md` (prompt v2 without evals; judge drift); rollback via prompt label shown | [ ] | |
| 11.5 | Writing the postmortem | SC | Code on screen matches `03-code/` file and curriculum §6; runs offline where the curriculum says so | [ ] | |
| 11.6 | Project 2: Investigate a fourth incident | AS | Brief complete; the fourth incident's solution exists only in the private assignment answer, not in the repo | [ ] | |
| 11.7 | Quiz: Incident response | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 12.1 | Vendor lock-in and the OTel escape hatch | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 12.2 | Code-along: same Atlas, traced to LangSmith | SC | `traceable`, `wrap_openai` produce the same trace shape in LangSmith; differences listed match the narration | [ ] | |
| 12.3 | Arize Phoenix and OpenInference | SC | OTLP exporter endpoint change is the only code diff; Phoenix shows the trace | [ ] | |
| 12.4 | OpenLLMetry, Datadog and the enterprise APMs | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 12.5 | Decision matrix: choosing your backend | SL | Matrix rows match `10-resources/backend-decision-matrix.md`; ratings qualitative and dated | [ ] | |
| 12.6 | Quiz: Portability | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 13.1 | Self-hosting Langfuse with Docker Compose | SC | Compose stack starts; "verify against current Langfuse compose" note visible; generated secrets masked | [ ] | |
| 13.2 | OTel Collector as the traffic cop | SC | Collector receives OTLP, applies attributes + tail sampling, exports to two backends; both show the trace | [ ] | |
| 13.3 | Code-along: the CI budget gate | SC | `tests/budget/test_budget_gate.py` fails the prepared PR and passes after the fix in GitHub Actions; release tag visible in Langfuse | [ ] | |
| 13.4 | Production readiness checklist for observability | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 13.5 | Chaos demo: kill the observability backend | DM | Langfuse container stopped mid-swarm; Atlas keeps serving; exporter timeouts and queue drops visible in logs; no request errors | [ ] | |
| 13.6 | Lab 7: Self-hosted stack end to end | LAB | Complete the lab as a student on a clean machine (offline path first, then with keys); expected outputs match | [ ] | |
| 14.1 | Capstone brief and acceptance criteria | SL | n/a (conceptual). Check facts and diagrams against curriculum; version banner if any code shown | [ ] | |
| 14.1a | Build it yourself first: the capstone gate | TH | Gate card clearly says pause and build; brief in `05-projects/capstone-atlas-ops.md` is sufficient to build without the walkthrough | [ ] | |
| 14.2 | Reference solution part A: instrumentation and cost | SC | Reference solution runs end to end offline; numbers match `[NUMBERS]` | [ ] | |
| 14.3 | Reference solution part B: quality, dashboards, alerts, CI | SC | Judge, drift, Grafana, alerts and budget gate all green on the reference solution | [ ] | |
| 14.4 | The weekly ops report your manager reads | SC | `report.py` produces the one-page report from the frozen week; figures match the console | [ ] | |
| 14.5 | Capstone submission and portfolio | TH | n/a (conceptual). Check facts against curriculum | [ ] | |
| 14.6 | Domain swap: observe a different agent | AS | Brief complete; rubric + example solution run | [ ] | |
| 14.7 | Quiz: Capstone review | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 15.1 | What you can now do | TH | n/a (conceptual). Check facts against curriculum | [ ] | |
| 15.2 | Careers: LLMOps, AI platform and AI SRE roles | TH | No salary figures; role titles and interview answers match `10-resources/interview-questions.md`; no promotional content (that belongs in 15.4) | [ ] | |
| 15.3 | Final practice test | QZ | Every question has correct answer + explanation; answers match current APIs and attribute names | [ ] | |
| 15.4 | Bonus lecture | TH | Only lecture with course links/coupons; complies with current bonus-lecture rules (verify) | [ ] | |

---

## 3. Course-level checks (before submission)

- [ ] Fresh clone on macOS, Windows (WSL and native if supported) and Linux: `make install`, `make test` (offline, 150+ tests) pass
- [ ] `OFFLINE=1 make replay` reproduces the frozen fixture day byte-for-byte for the course seed; `make budget-check` passes on it
- [ ] With keys: 2.3 live trace works; `make eval` (online judge) runs under the cap; CI green on a fresh fork (unit + integration + budget gate always; live evals only with secrets)
- [ ] 13 section quizzes + practice test present; 5 challenges (4.7, 6.8, 11.2, 11.3, 11.4) have clear pause/submit instructions; 14.1a gate present
- [ ] Coding exercises (5) pass hidden tests in Udemy's runner and fail on wrong answers; none imports a third-party package
- [ ] Quizzes (13) + practice test (40 Q): every answer reviewed; no question depends on a now-changed attribute name or SDK method
- [ ] All `../10-resources/` PDFs exported and attached per `../07-udemy-listing/resources-per-lecture.md`; incident solutions attached to Part B only
- [ ] Lecture order in Udemy matches the curriculum; free previews set
- [ ] Full watch-through in student preview (≥1.5×) with notes logged and fixed
- [ ] Q&A seeded: 5 likely questions per section posted with answers on launch day (recording-guide §9); incident-lab spoiler thread pinned
- [ ] Keys used in recording rotated; recording projects' traces deleted

## 4. Sign-off

| Section | QA by | Date | Issues found | Fixed |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
| 9 | | | | |
| 10 | | | | |
| 11 | | | | |
| 12 | | | | |
| 13 | | | | |
| 14 | | | | |
| 15 | | | | |
