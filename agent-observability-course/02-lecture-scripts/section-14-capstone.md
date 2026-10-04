# Section 14: Capstone: The Atlas Ops Console

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈53 min (8 lectures; 14.3 reduced to 10:00 on 2026-10-02)
> **Source of truth:** `01-curriculum/curriculum.md`; project brief `05-projects/capstone-atlas-ops.md`; domain swap `10-resources/instrumentation-template.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / langsmith 0.14; check the repo README for updates."
> **Recording note:** 14.2 and 14.3 are each recorded as Part A and Part B uploads (14.2: 6:00 + 6:00; 14.3: 5:00 + 5:00). 14.1a is the build-first gate: it must be uploaded between 14.1 and 14.2 and never merged into either.

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with Atlas, the Ops Console, Langfuse or Grafana. Record the real screen. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only, not cues, code, tables or slide text.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 14.1 | Capstone brief and acceptance criteria | SL | 6:00 | ~750 |
| 14.1a | Build it yourself first: the capstone gate | TH | 3:00 | ~407 |
| 14.2 | Reference solution part A: instrumentation and cost (Part A / Part B) | SC | 12:00 (6:00 + 6:00) | ~830 |
| 14.3 | Reference solution part B: quality, dashboards, alerts, CI (Part A / Part B) | SC | 10:00 (5:00 + 5:00) | ~890 |
| 14.4 | The weekly ops report your manager reads | SC | 8:00 | ~675 |
| 14.5 | Capstone submission and portfolio | TH | 5:00 | ~510 |
| 14.6 | Domain swap: observe a different agent | AS | 4:00 video | ~452 |
| 14.7 | Quiz: Capstone review | QZ | 5:00 total (1:00 video) | ~105 |

**Names used in this section (match `03-code/`).** Students build in their own branch or fork of `03-code/` and name their console module `console/my_ops_console.py` so it never collides with the reference `console/ops_console.py`. Shipped entry points: `telemetry/otel_setup.py::configure_tracing(settings, exporter_kind=, store=, batch=)`, `shutdown_tracing`, `exporter_health`; `telemetry/langfuse_setup.py::init_langfuse(settings, tracer_provider=)`, `trace_attributes`, `create_score`, `get_prompt_text`, `push_prompts`; `telemetry/genai_attrs.py::set_agent`, `set_tenant_context`, `set_llm_request`, `set_llm_usage`, `set_cost`, `set_tool`, `set_retrieval`, `set_guardrail`, `add_event`; `telemetry/metrics.py::record_generation`, `record_request`, `record_tool`, `metrics_app`, counters `REQUESTS`, `COST`, `BUDGET_DECISIONS`, `FALLBACKS`, `TOOL_CALLS`, `JUDGE_SCORE`, `EXPORTER_FAILURES`; `src/northwind/pricing.py::estimate_cost -> CostBreakdown`; `src/northwind/cost.py::CostRecord`, `rollup`, `total_cost`, `cost_per_session`, `showback_table`; `src/northwind/budget.py::BudgetGuard.decide -> BudgetDecision`, `Decision`, `EWMAAnomalyDetector`; `app/agent.py::AtlasAgent.run`, `build_router_config`, `CircuitBreaker`, `FALLBACKS`; `src/northwind/slo.py::compute_slis`, `burn_rate`, `DEFAULT_SLOS`; `src/northwind/drift.py::compare_windows`, `DriftResult`, `drift_report_markdown`; `src/northwind/report.py::ReportInputs`, `IncidentNote`, `weekly_report`, `default_recommendations`; `src/northwind/sampling.py::JudgeSamplingPolicy`, `TraceSummary`. Also shipped: `evals/online_judge.py::run_judge(store, rate=, dry_run=, model=)` with `OfflineJudge`, `DeepEvalJudge`, `pick_judge`; `evals/drift_report.py::compare_split(store, split_ts)` and `compare_stores(baseline, current)`; `evals/to_dataset.py::select_bad_traces(store, threshold=)`, `write_jsonl`, `push_to_langfuse`; `deploy/alerts.yml`; `tests/budget/test_budget_gate.py`; `simulator/replay.py::replay_day(seed, sessions=, incidents=, store=) -> (ReplaySummary, LocalSpanStore)`; Makefile targets `replay`, `judge`, `feedback`, `drift`, `dataset`, `budget-check`, `report`, `stack`, `langfuse-up`, `incident N=`. Acceptance tests are numbered AT-01 to AT-24 in the brief (pass: 15; excellent evidence: 20). Ops Console pages that exist (`console/pages/`): Live cost, Cost, Latency, Quality, Budgets, Traffic, Retrieval, Reliability, Safety, Alerts, Traces, Compare replays. `make test` = 419 passed; `make budget-check` = 5 passed. Not in the shipped code (shown as student additions): an `anomaly` increment on `atlas_budget_decisions_total`, a slow-call rule in `CircuitBreaker`, an hourly drift gauge.

---

## Lecture 14.1 — Capstone brief and acceptance criteria

| Field | Value |
|---|---|
| ID | 14.1 |
| Type | SL (slides + avatar, one screen beat) |
| Target duration | 6:00 (~750 spoken words) |
| Learning objectives | 1. Turn the engineering manager's request into requirements by pillar: traces, cost, reliability, quality, operations. 2. Explain the 24 acceptance tests, how each is verified, and the pass bar. 3. Draw the capstone architecture from Atlas to the Collector, Langfuse, Prometheus, Grafana and CI. |
| Prerequisites | Sections 3 to 13 |
| Files used | `05-projects/capstone-atlas-ops.md` |

### Script

[B-ROLL: An email. Subject: "Atlas: can we run this for real?" Body visible: "Before I put Atlas in front of all four departments I need to know what it costs per resolved question, whether it's getting better or worse, and that someone gets paged before finance does."]

[AVATAR]
Every section so far added one capability to Atlas. Traces. Cost. Budgets. Latency. Online evals. Dashboards. Governance. Incidents. Portability. Deployment. Each one worked on its own.

The capstone is where they have to work together, as one system, under one set of acceptance criteria. And the brief is written the way an engineering manager writes it, not the way a course writes it.

[SLIDE 1: The request]
> "Before I put Atlas in front of all four departments I need to know: what it costs per resolved question, by department; whether it's getting better or worse week over week; that someone gets paged before finance does; and that a bad change can't reach production without a number telling us so. Show me the console, show me the report, show me the pull request that failed."
> Priya Raman, Engineering Manager, Northwind Logistics (fictional)

Priya Raman runs engineering at Northwind. Atlas has been in pilot with one department, and she won't roll it out to all four until she gets four things.

[SLIDE 2: Her sentence, read by an engineer]
- "Cost per resolved question": cost joined with resolution (Sections 6, 8)
- "Better or worse week over week": drift (8.5)
- "Paged before finance": anomaly alerts with owners (6.7, 9.5)
- "A number telling us so": the CI budget gate (13.3)

Read her sentence like an engineer. "Cost per resolved question" is cost attribution joined with a resolution signal. "Better or worse week over week" is drift. "Paged before finance" is anomaly alerts with owners. "A number telling us so" is the CI budget gate. And "show me the console, the report, the pull request" are three deliverables.

[SLIDE 3: Requirements by pillar]
- Traces: every LLM, tool, retriever and agent span with GenAI attributes; sessions, users, tenants; release tag; masking
- Cost: price table with fallback; cost per request, session, user, tenant, feature; caching, context diet, small-model-first routing; per-tenant budgets
- Reliability: TTFT and p95 measured; timeouts, bounded retries, fallback; p95 ≤ 4 s during the `slow_provider` scenario
- Quality: sampled online judge; feedback endpoint; weekly drift; failures promoted to a dataset
- Operations: Prometheus metrics, Grafana dashboard, three alert rules with runbooks; self-hosted stack; CI budget gate; weekly report

The brief's requirements fall into five pillars. Traces, tagged and masked. Cost, attributed at every level and cut with the three techniques. Reliability, holding p95 under four seconds while the provider is slow. Quality: the judge, feedback, drift and the dataset loop. And operations: metrics, dashboard, alerts, the stack, the gate and the report.

You've built every one of these. The capstone is assembling them so they agree with each other. The cost on the span, the cost in Prometheus and the cost in the report must be the same number. That's harder than it sounds and it's where most of the marks are.

[SCREEN: Terminal in your fork of `03-code/`: `make test` → `419 passed`; `make budget-check` → `5 passed`.]

Here's your starting line. Fork the repo, run the tests, run the gate. Four hundred and one passed, five passed. Every change you make this week keeps both green.

[SLIDE 4: 24 acceptance tests]
| Area | Examples | Layer |
|---|---|---|
| Instrumentation (AT-01 to AT-06) | AT-02 every generation carries `gen_ai.usage.*`; AT-06 an email, phone and employee ID are masked | integration |
| Cost (AT-07 to AT-12) | AT-09 total cost agrees within 2% across the store, `/metrics` and the report; AT-10 caching cuts input-token cost by 30%+ | unit, replay |
| Containment (AT-13 to AT-17) | AT-14 the hard cap refuses with no LLM call; AT-15 the anomaly fires on `context_bloat` | integration, replay |
| Reliability and quality (AT-18 to AT-20) | AT-18 p95 ≤ 4,000 ms on `slow_provider`; AT-19 drift isolates prompt v2 | replay, eval |
| Operations (AT-21 to AT-24) | AT-22 three alerts seen firing; AT-24 the gate goes red on a top-k change | manual with evidence |

- Pass: 15 of 24; excellent evidence: 20 or more

Twenty-four acceptance tests in five areas, each with a layer that says how it's verified. Some are tests: an integration test asserts every generation carries usage and model attributes. Some are replays: run the slow-provider day and read p95. Some are evidence you record: a screenshot of an alert firing, a link to a red CI run on a top-k change.

[AVATAR]
The one I'd look at first as a reviewer is AT-09. Total cost must agree within two percent across the span store, the Prometheus counter and the weekly report. If those three disagree, one of them is lying, and finance will find out which.

Fifteen of twenty-four passes. Twenty or more is excellent. And write your budgets and thresholds down before you measure. Moving the target after the fact is the first thing a reviewer notices.

[AVATAR]
Now the shape of the whole thing.

[SLIDE 5: Architecture]
Diagram (from the Mermaid chart in `05-projects/capstone-atlas-ops.md`):
- Employees (4 tenants) and the swarm → FastAPI `/chat`, `/feedback` → `AtlasAgent` (router mode, budgets, step limit)
- Tools → `src/northwind` (pricing, cost, budget, tokens, latency, pii); KB retriever
- Telemetry: OTel SDK + `genai_attrs` → OTLP → Collector (mask, tail sample) → Langfuse (self-hosted) and optional second backend
- `/metrics` → Prometheus → Grafana `atlas-ops` dashboard + alert rules → runbooks
- Evals: `online_judge` (sampled) and `feedback` → Langfuse scores → `drift_report` weekly → `to_dataset`
- CI: unit + integration + budget gate on every PR; live evals on main; release tag on every trace
- `report.py` → weekly markdown to the manager

Here's the architecture on one slide. Employees and the swarm hit the FastAPI endpoints. The agent runs in router mode with budgets and a step limit. Tools call into the pure-Python core. Telemetry goes out over OTLP to the Collector, which masks and samples, then to your self-hosted Langfuse. Metrics go to Prometheus and Grafana, with alert rules linked to runbooks. The judge and feedback write scores, the drift report reads them weekly, failures become dataset items. CI gates every pull request. And `report.py` turns the week into one page for Priya.

[SLIDE 6: Deliverables]
- D1 Repository: your fork with `console/my_ops_console.py`, tests, deploy files, CI
- D2 `ACCEPTANCE.md`: 24 tests, PASS or FAIL, evidence for each
- D3 `REPORT-week.md` from your own report function
- D4 `INCIDENTS.md`: five scenarios, detection and containment
- D5 Screenshots or a short recording; D6 architecture diagram
- D7 `DIFF_NOTES.md`; D8 portfolio write-up

Eight deliverables. Your repository. An acceptance report with evidence per test. The weekly report your code generated. Notes on how your stack detected and contained each of the five failure scenarios. Screenshots or a short recording, and your own architecture diagram. Diff notes, which the next lecture explains. And a portfolio write-up.

[SLIDE 7: The week]
- Day 1 audit and instrumentation; Day 2 cost
- Day 3 reliability and budgets; Day 4 quality
- Day 5 dashboards and alerts; Day 6 deploy and gate
- Day 7 report, acceptance and write-up

The brief has a suggested week plan. Day one is an audit, not a rewrite. Then cost, reliability and budgets, quality, dashboards and alerts, the stack and the gate, and on day seven the report and the write-up.

And there's a minimum viable capstone if the week runs short: full instrumentation, cost per tenant and per resolved session, caching and the diet measured, a hard cap that refuses, metrics and the dashboard, one alert with a runbook, the CI gate, and the report. At least fifteen tests. A finished smaller scope beats an unfinished big one.

[AVATAR]
The full brief, all twenty-four tests and the rubric are in `05-projects/capstone-atlas-ops.md`. Read it before the next lecture, because in the next lecture I'm going to ask you to stop watching.

[SLIDE 8: Recap]
- Four questions become five pillars
- 24 acceptance tests; pass at 15
- Cost must agree in three places

**Recap:** The capstone turns a manager's four questions into requirements across five pillars, 24 verifiable acceptance tests and eight deliverables, on the architecture you assembled across the course.

**Transition:** Next, the capstone gate: why you should build this from the brief before you watch the reference.

### Speaker notes: common student mistakes / Q&A

- Mistake: treating AT-09 as trivial. Rounding, cached tokens and the judge's own cost are the usual sources of disagreement between span cost and the Prometheus counter. Point to Lecture 6.1 on token anatomy.
- "Do I need real API keys?" No. Every criterion is verifiable in offline mode. Live keys make the judge real; the mock judge produces deterministic scores for offline students.
- "Can I use LangSmith or Phoenix instead of Langfuse?" Yes, if you meet the same tests. AT-19 and AT-20 need scores in whichever backend you pick.
- Remind students to keep their own console file separate from the reference so `git pull` on the course repo never clobbers their work.

---

## Lecture 14.1a — Build it yourself first: the capstone gate

| Field | Value |
|---|---|
| ID | 14.1a |
| Type | TH (talking head / avatar) |
| Target duration | 3:00 (~410 spoken words) |
| Learning objectives | 1. Commit to a one-week, time-boxed attempt at the capstone from the brief alone. 2. Know what is allowed during the week and how to use the reference solution afterwards through `DIFF_NOTES.md`. |
| Prerequisites | 14.1 |
| Files used | `05-projects/capstone-atlas-ops.md` |

### Script

[AVATAR]
Stop here.

[PAUSE]

I mean it. The next three lectures are my reference solution. I'll assemble the telemetry, make the cost numbers agree, wire the judge and the alerts and the CI gate. If you watch them now, you'll type along, it'll work, and you'll learn about a third of what you could.

[SLIDE 1: Why build first]
- Watching teaches what the answer looks like
- Building teaches why it looks like that
- Interviews ask for the "why"

Here's why. Watching someone assemble a system teaches you what the answer looks like. Building it from the brief teaches you why. Why the cost on the span and the cost in Prometheus drift apart. Why the alert fires twice. Why the judge's own tokens show up in the tenant's bill. You only learn those by hitting them, and you only hit them by building.

And there's a career reason. In Section 15 I'll give you twelve interview questions. Every one of them is easier to answer with a story that starts "when I built this, the hard part was". You don't get that story from typing along.

[SLIDE 2: The capstone gate]
- Time box: one week. Put the end date in your calendar now
- Build from `05-projects/capstone-atlas-ops.md` in your own branch: `console/my_ops_console.py`
- Allowed: everything from Sections 3 to 13, your labs and projects, the docs, the Q&A for concepts
- Not yet: lectures 14.2 to 14.4 and the reference `console/ops_console.py` internals
- Stuck for more than 90 minutes? Write down what you tried, cut scope, move on

So here's the deal. One week, end date in your calendar. Build from the brief in your own branch, with your own console module.

You can use everything you've built so far: every module from Sections 3 through 13, your labs, your projects, the docs, and the Q&A for concept questions. What you can't open yet is the next three lectures, or the internals of the reference console.

If you're stuck on one thing for more than ninety minutes, don't burn a day on it. Write down what you tried, use the minimum viable capstone list in the brief to cut scope, and move on. Unfinished but honest beats finished but copied.

[SLIDE 3: When you come back]
- Watch 14.2 to 14.4 as a code reviewer
- Write `DIFF_NOTES.md`: three things the reference does differently, and whether you adopted each
- Keep your version wherever it passes the acceptance criteria

When the week is up, whatever state you're in, come back and watch the reference as a code reviewer. Then write `DIFF_NOTES.md`: three things the reference does differently from yours, and whether you adopted each one. Some of mine will be better. Some of yours will be. That comparison is often the most valuable hour of the course. And wherever your version passes the criteria, keep it. It's yours.

[AVATAR]
I know it's tempting to click next. Close this video, open the brief, and start with day one.

I'll see you in a week.

[SLIDE 4: Recap]
- One week, from the brief alone
- Then watch the reference as a reviewer
- Write `DIFF_NOTES.md`: three differences

**Recap:** Build the capstone from the brief first, time-boxed to one week, then use the reference solution as a code review and write down the differences.

**Transition:** When you're back, the next lecture is the reference solution, starting with instrumentation and cost.

### Speaker notes: common student mistakes / Q&A

- This is the one lecture designed to be paused for a week. Do not merge it into 14.1 or 14.2 in the upload.
- Students short on time: the minimum viable capstone in the brief is fourteen criteria and roughly three days.
- "Can I share my repo in the Q&A for feedback?" Yes, and encourage it. Remind them that `.env` must not be committed and that incident datasets are synthetic.
- Instructor tip: pin a Q&A thread titled "Capstone week" for progress and blockers.

---

## Lecture 14.2 — Reference solution part A: instrumentation and cost (Part A and Part B)

| Field | Value |
|---|---|
| ID | 14.2 (recorded and uploaded as 14.2 Part A and 14.2 Part B, each under ten minutes) |
| Type | SC (screencast / code-along) |
| Target duration | 12:00 total: Part A 6:00 (~425 spoken words), Part B 6:00 (~415 spoken words); the rest is code, console and typing time |
| Learning objectives | 1. Assemble the telemetry stack in one startup call: OTel provider, exporters, local store, Langfuse client with masking and release. 2. Make cost agree across the span, the Prometheus counter and the aggregation used by the report. 3. Wire budgets and small-model-first routing into the agent loop and prove the saving on the replayed day. |
| Prerequisites | 14.1a gate completed; Sections 3, 4, 6 and 7 |
| Files used | `telemetry/otel_setup.py`, `telemetry/langfuse_setup.py`, `telemetry/genai_attrs.py`, `telemetry/metrics.py`, `app/agent.py`, `app/server.py`, `src/northwind/pricing.py`, `src/northwind/cost.py`, `src/northwind/budget.py`, `console/ops_console.py` |

### Script: Part A — one startup call, one cost number

[AVATAR]
Two tracer providers. That's the most common note students write in `DIFF_NOTES.md` after this lecture, and it doubles every span in Langfuse. If you just finished your week, open your own branch in a second window and see whether you have it.

Here's the headline for Part A. The reference adds almost no new code. It makes one startup call that wires everything you already built, in the right order, and it follows one rule: cost is computed once, in one place, and everything else reads it.

[SCREEN: `app/server.py::create_app`, the `lifespan` function. Footer visible.]

[CODE: startup, `app/server.py` (as shipped, abbreviated)]
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)
    configure_tracing(settings, store=store)      # provider, exporter, local store, then Langfuse on the same provider
    app.state.budget = budget_guard or BudgetGuard.from_caps(
        list(TENANTS) + ["other"], soft=settings.tenant_soft_cap_usd,
        hard=settings.tenant_hard_cap_usd, window_s=settings.budget_window_s)
    app.state.agent = AtlasAgent(settings, llm=llm, budget_guard=app.state.budget)
    metrics.set_build_info(version=settings.langfuse_release, model=settings.model,
                           prompt_version=settings.prompt_version)
    ...
    try:
        yield
    finally:
        force_flush()
        shutdown_tracing()                        # bounded: 5 s by default

app = FastAPI(title="Atlas helpdesk agent", lifespan=lifespan, **_fastapi_telemetry_off())
app.mount("/metrics", metrics.metrics_app())
```

One call does the heavy lifting. `configure_tracing` builds the tracer provider with the resource attributes; adds the exporter named in settings, wrapped in `SafeSpanExporter` and a batch processor; mirrors every span into the local store for the Ops Console; and, if Langfuse keys are present, calls `init_langfuse` with the *same* provider. Then the budget guard, the agent, and the build-info metric that drives Grafana's release annotation. On shutdown, a flush and a bounded shutdown.

Notice the last line of the factory. FastAPI's own telemetry is switched off, so `invoke_agent atlas` stays the root span, as Lecture 3.6 demanded. And notice what's absent: the OpenInference instrumentor. If you add it for live OpenAI calls, Lecture 3.5, pass it this same provider. Order matters: provider first, then Langfuse on it, then the instrumentor on it.

[CODE: `telemetry/langfuse_setup.py::init_langfuse`, as shipped]
```python
_CLIENT = Langfuse(
    public_key=settings.langfuse_public_key, secret_key=settings.langfuse_secret_key,
    base_url=settings.langfuse_base_url,
    environment=settings.langfuse_environment, release=settings.langfuse_release,
    sample_rate=settings.langfuse_sample_rate,          # head sampling; tail sampling is in the Collector
    mask=langfuse_mask,                                  # northwind.pii, Lecture 4.6
    blocked_instrumentation_scopes=["httpx", "urllib3", "sqlite3"],
    tracer_provider=tracer_provider,                     # the shared provider
    should_export_span=_should_export,                   # export atlas.* spans even without gen_ai.* attributes
    flush_at=50, flush_interval=2.0,
)
```

The Langfuse client takes the shared provider. The mask function from `pii.py`. Blocked scopes so HTTP client spans don't flood the trace. And `should_export_span`, which matters: by default Langfuse exports only spans with `gen_ai` attributes or its own, and our guardrail and step spans have neither. Without this line your traces have holes.

Now the agent loop, where every generation gets its attributes and its cost.

[CODE: `app/agent.py::_call_model`, the generation step, abbreviated]
```python
with self.tracer.start_as_current_span(ga.llm_span_name(current)) as span:
    ga.set_llm_request(span, model=current, conversation_id=session_id,
                       prompt_version=prompt_version, prompt_cache_key=cache_key)
    ...
    resp = self.llm.chat(**kwargs)
    inp, out, cached, reasoning = usage_numbers(usage)
    cost = self._price(current, inp, out, cached, reasoning)          # estimate_cost -> CostBreakdown
    ga.set_llm_usage(span, input_tokens=inp, output_tokens=out, cached_tokens=cached,
                     reasoning_tokens=reasoning, ttft_s=ttft_s, ...)
    ga.set_cost(span, cost)                                            # atlas.cost_usd + Langfuse cost details
    metrics.record_generation(tenant=tenant, model=current, feature=feature,
                              input_tokens=inp, output_tokens=out, cached_tokens=cached,
                              reasoning_tokens=reasoning, cost_usd=float(cost.total_usd), ttft_s=ttft_s)
```

One generation span. Request attributes, then usage from the response, then the line that makes AT-09 pass: `self._price`, which calls `estimate_cost` in `pricing.py`. One computation, one `CostBreakdown`, written three ways. `set_cost` puts it on the span. `record_generation` adds it to the Prometheus counter `atlas_cost_usd_total`, labelled by tenant, model and feature, never by user. And the local store reads the span attribute for the console and the report.

[SCREEN: Terminal 1: `make run`. Terminal 2: `make swarm RPS=2 DURATION=20` ends with `sent=63 ok=63 … cost=$0.3585`. Then `curl -sL localhost:8000/metrics | grep '^atlas_cost_usd_total' | awk '{s+=$2} END {print s}'` prints `0.358492`. Then the Ops Console Cost page over the same store: total cost $0.3585.]

Prove it. Run Atlas, send sixty-three requests with the swarm, and read the total three ways. The swarm's own tally: thirty-five point eight five cents. The sum of the Prometheus counter: thirty-five point eight five. The console, reading the spans: thirty-five point eight five. And on the full replayed day, the console and `make report` both say fifty-six twenty-eight. Three places, one number. That's AT-09.

[SLIDE 1: Recap, Part A]
- One `configure_tracing` call, one provider
- Cost computed once, written three ways
- Prove agreement: swarm, `/metrics`, console

[SCREEN: Switch to Part B title card.]

### Script: Part B — budgets, routing and the saving

[AVATAR]
Part B. Budgets and routing, and then proving the saving that Section 6 promised.

[CODE: `app/agent.py::run`, the budget guard, as shipped]
```python
            if self.budget_guard is not None:
                decision = self.budget_guard.decide(
                    tenant, time.time(), next_cost_usd=self.budget_guard.estimate(tenant)
                )
                result.budget_decision = decision.decision.value
                root.set_attribute(ga.ATLAS_BUDGET_DECISION, decision.decision.value)
                metrics.BUDGET_DECISIONS.labels(tenant, decision.decision.value).inc()
                metrics.BUDGET_SPENT.labels(tenant).set(decision.spent_usd)
                if decision.decision is Decision.REFUSE:
                    result.answer, result.outcome = BUDGET_REFUSAL, "refused"
                    ga.add_event(root, "budget.refused", reason=decision.reason)
                    return self._finish(root, result, tenant, started)
                if decision.decision is Decision.DEGRADE:
                    ga.add_event(
                        root, "budget.degraded", reason=decision.reason, model=s.degraded_model
                    )
                    model, top_k = self._choose_deployment(intent, degraded=True), min(top_k, 2)
                    result.model = model
```

[CODE: a capstone addition, two lines after the degrade branch (not in the shipped file)]
```python
                if decision.anomaly:                                     # the Incident 1 action item
                    metrics.BUDGET_DECISIONS.labels(tenant, "anomaly").inc()
```

Before the loop, the budget guard from Lecture 6.7. `decide` pre-charges the tenant's estimate for the next request and returns allow, degrade or refuse against the soft and hard caps, twenty-five and forty dollars by default. Refuse: an event, a polite answer, no model call, and the server returns a four-two-nine; `test_hard_cap_refuses_with_429` proves it. Degrade: the cheaper model and top-k capped at two. And the two lines in the second block are yours, not shipped: when the EWMA detector flags an anomaly, count it, so an alert can page on it.

[CODE: `app/agent.py`, router config and the breaker, as shipped]
```python
def build_router_config(settings: Settings) -> dict[str, Any]:
    ...
    return {
        "model_list": [...],                                   # gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o-mini, gpt-5-mini
        "fallbacks": [{m: [FALLBACKS[m]]} for m in models if m in FALLBACKS],
        "num_retries": settings.max_retries,                   # ATLAS_MAX_RETRIES, 2
        "timeout": settings.request_timeout_s,                 # ATLAS_REQUEST_TIMEOUT_S, 20
        "allowed_fails": settings.router_allowed_fails,        # ATLAS_ROUTER_ALLOWED_FAILS, 3
        "cooldown_time": settings.router_cooldown_s,           # ATLAS_ROUTER_COOLDOWN_S, 30
    }

# _call_model: the breaker is consulted before every attempt
if self.breaker.is_open(current) and current in FALLBACKS:
    nxt = FALLBACKS[current]
    metrics.FALLBACKS.labels(current, nxt).inc()
    current = nxt
```

Router mode. `build_router_config` is pure data, so it's unit-tested offline: the fallback chain, retries, the timeout, the failure allowance and the cooldown, all from settings. And in `_call_model`, the circuit breaker: when it's open for a model, the next call goes to that model's fallback and the fallback counter increments. The shipped breaker opens after three consecutive failures. Section 11 gave you two improvements, counting failures over a window and treating slow calls as failures; if you built them, that's a diff note in your favour.

[SCREEN: Ops Console, Compare replays page with six stores from `OFFLINE=1 make replay <flags> STORE=.atlas/<name>.sqlite`: baseline $56.28; `CACHE=1` $37.00 (−34.3%); `DIET=1` $41.99 (−25.4%); `ROUTER=1` $47.07 (−16.4%); `CACHE=1 DIET=1` $22.71 (−59.6%); all three $19.07 (−66.1%). Judge resolved 0.892 and grounded 0.943 in every row.]

Now the saving. Six replays of the same day, same seed, each in its own store, side by side on the Compare replays page. Baseline: fifty-six twenty-eight. Caching alone: thirty-seven dollars, minus thirty-four percent. The diet alone: minus twenty-five. Routing alone: minus sixteen. Caching and the diet together: twenty-two seventy-one, minus sixty percent. All three: nineteen dollars and seven cents, minus sixty-six. And the judge scores are identical in every row. Cheaper, not worse.

[SLIDE 2: The saving, by lever]
| Lever | Daily cost | Δ vs baseline |
|---|---:|---:|
| Baseline | $56.28 | |
| Caching | $37.00 | −34.3% |
| Diet | $41.99 | −25.4% |
| Routing | $47.07 | −16.4% |
| All three | $19.07 | −66.1% |

The levers don't add up to sixty-six, because they overlap: the diet shrinks the very prompts that caching discounts. That's why you report each lever alone *and* the combination. "We saved money" is a claim. This table is evidence.

[SLIDE 3: Part A and B against the tests]
- AT-02, AT-06: attributes and masking, integration tests green
- AT-09: one cost in three places
- AT-10 to AT-12: caching, diet, routing measured on one seed
- AT-13, AT-14: degrade and refuse, 429 tested

[AVATAR]
Compare with your branch. The three most common diff notes from beta: two tracer providers, cost computed in two places, and savings measured on different days. If you had none of them, you're ahead of my first draft.

[SLIDE 4: Recap]
- Startup order: provider, Langfuse, instrumentor
- Cost once, written everywhere, proven equal
- Each lever measured alone and combined

**Recap:** One `configure_tracing` call wires the provider, exporters, local store and Langfuse in order; cost is computed once in `pricing.py` and written to the span, Langfuse and Prometheus; the budget guard and router sit in the agent loop, and six replays of one day prove a 66% saving with unchanged judge scores.

**Transition:** Next, part B of the reference: the judge, drift, the dashboard, alerts and the CI gate.

### Speaker notes: common student mistakes / Q&A

- Names as shipped: `configure_tracing(settings, exporter_kind=, store=, extra_exporter=, batch=)`, `init_langfuse(settings, tracer_provider=)`, `ga.set_llm_request / set_llm_usage / set_cost / add_event`, `estimate_cost -> CostBreakdown`, `metrics.record_generation`, `BudgetGuard.decide -> BudgetDecision(decision, anomaly, ...)`, `Decision.ALLOW|DEGRADE|REFUSE`, `build_router_config`, `CircuitBreaker`, `FALLBACKS`. The `anomaly` counter lines are a Section 11 action item and are **not** in `app/agent.py`; show them as a diff.
- `server.py` does not call `instrument_openai`; the helper exists in `telemetry/openinference_setup.py` (Lecture 3.5).
- AT-09 numbers (2026-10-02): `make run` + `make swarm RPS=2 DURATION=20` (Makefile defaults, so caching and diet off): 63 requests; swarm tally $0.3585; Prometheus `atlas_cost_usd_total` sum 0.358492; console $0.3585. `curl -sL` works either way (`/metrics` no longer redirects after the 2026-10-04 code pass). The swarm plan is seeded, but rerun before recording and show whatever three equal numbers you get.
- Lever table: numbers card §2. There is no per-lever "breakdown bar" in the console; Slide 2 is the breakdown.
- "Why write cost to Langfuse if it computes cost itself?" Langfuse's price table may differ from yours (negotiated rates, cached tokens). Your number is the one finance sees; send it.
- Prometheus label rule: tenant, model and feature only. A student who adds `user_id` gets a cardinality lecture; point to 5.5. `metrics.label_names()` exists so a unit test can assert it.

---

## Lecture 14.3 — Reference solution part B: quality, dashboards, alerts, CI (Part A and Part B)

| Field | Value |
|---|---|
| ID | 14.3 (recorded and uploaded as 14.3 Part A and 14.3 Part B, about five minutes each) |
| Type | SC (screencast / code-along) |
| Target duration | 10:00 total: Part A 5:00 (~400 spoken words), Part B 5:00 (~490 spoken words); the rest is code, dashboard and terminal time |
| Learning objectives | 1. Run the sampled online judge and feedback loop so scores land in Langfuse with prompt version metadata, and produce the weekly drift report. 2. Provision the Grafana dashboard and three alert rules as code, with runbook links and owners. 3. Make the CI budget gate a required check and show it red on a real regression. |
| Prerequisites | 14.2; Sections 8, 9 and 13 |
| Files used | `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py`, `evals/to_dataset.py`, `src/northwind/sampling.py`, `src/northwind/drift.py`, `src/northwind/slo.py`, `telemetry/metrics.py`, `deploy/grafana/dashboards/atlas-ops.json`, `deploy/alerts.yml`, `tests/budget/test_budget_gate.py`, `.github/workflows/ci.yml` |

### Script: Part A — quality that shows up on a timeline

[AVATAR]
Incident 3 taught you that quality without a timeline is an email from HR the next morning. Part A of the reference gave Priya cost. This part gives her "better or worse", "paged before finance", and "the pull request that failed."

Start with quality.

[CODE: `evals/online_judge.py::run_judge`, the sampled judge (abbreviated)]
```python
def run_judge(store, *, rate=0.1, limit=None, dry_run=True, model="gpt-4.1-mini", since=None, write_langfuse=True):
    judge = pick_judge(dry_run=dry_run, model=model)            # OfflineJudge offline, DeepEvalJudge with a key
    policy = JudgeSamplingPolicy(rate=rate)
    already = {s.trace_id for s in store.scores(name="judge_overall")}
    for span in store.spans(kind="agent", since=since):
        a = span.attributes
        ...
        t = TraceSummary(trace_id=span.trace_id, error=outcome == "error", duration_ms=span.duration_ms,
                         cost_usd=float(a.get("atlas.cost_usd", 0.0) or 0.0), steps=int(a.get("atlas.steps", 1) or 1),
                         tenant=str(a.get("atlas.tenant", "")), escalated=bool(a.get("atlas.escalated", False)))
        if not policy.should_judge(t):                            # rate from JUDGE_SAMPLE_RATE, plus the tail rules
            continue
        scores = judge.score(question=..., answer=..., intent=..., outcome=outcome, tool_calls=..., trace_id=span.trace_id)
        for name, value in scores.items():                        # resolved, grounded, safe_escalation, overall
            store.add_score(ScoreRecord(span.trace_id, f"judge_{name}", value, "judge", judge.name, ts, tenant, session_id))
            if write_langfuse and langfuse_enabled():
                create_score(span.trace_id, f"judge_{name}", value, comment=judge.name)
        summary.estimated_cost_usd += 3 * (1200 * 0.4e-6 + 150 * 1.6e-6)   # judging is a line item
```

The judge samples at the rate in settings, ten percent by default, plus the tail rules from `sampling.py`: every error, escalation, expensive trace and thumbs-down. Three criteria from Lecture 8.2, resolved, grounded and safe escalation, plus their mean as `overall`. Each writes a score to the local store and, through the guarded `create_score`, to the trace in Langfuse. And a running estimate of what the judging cost.

[SCREEN: Terminal after the baseline `OFFLINE=1 make replay`: `make judge` prints `candidates=10112 sampled=894 scored=894 already_scored=2971 mean_overall=0.909 est_judge_cost=$1.9310`. Then `make feedback` prints `feedback=1291 (12.7% of 10184 requests) positive=79% joined_with_judge=639 agreement=57% judge|👍=0.91 judge|👎=0.91`.]

Run it on the replayed day. Eight hundred and ninety-four traces sampled and scored, on top of the ones the replay already judged. Mean overall point nine one. Estimated judge cost: a dollar ninety-three. Against fifty-six dollars of serving, that's about three and a half percent. Priya's cost per resolved question includes the cost of knowing it was resolved. Leave it out and your report is wrong by a few percent.

Then feedback. Twelve point seven percent of requests got a thumbs, seventy-nine percent positive. Now every thumbs-down has a judge score too, and judge and user agree only fifty-seven percent of the time: the judge rates most thumbs-down answers as fine. That disagreement table on the Quality page is where you learn what your judge is missing.

[CODE: `evals/drift_report.py`, weekly comparison]
```python
def compare_stores(baseline: LocalSpanStore, current: LocalSpanStore, *,
                   thresholds: DriftThresholds = DriftThresholds()) -> list[DriftResult]: ...

def compare_split(store: LocalSpanStore, split_ts: float, *,
                  thresholds: DriftThresholds = DriftThresholds()) -> list[DriftResult]:
    b = _metrics(store, None, split_ts)
    c = _metrics(store, split_ts, None)
    return [compare_windows(m, bv, c.get(m, ([], hib))[0], thresholds=thresholds, higher_is_better=hib)
            for m, (bv, hib) in b.items()]
```

The drift report compares two windows: last week's store against this week's with `compare_stores`, two ISO weeks in one store with `--prev` and `--curr`, or one store split at an hour with `compare_split`. Every metric `_metrics` collects, judge scores, feedback, cost per request, latency and steps, goes through `compare_windows`, which computes the deltas and the PSI.

[SCREEN: `OFFLINE=1 make replay SCENARIO=prompt_regression`, then `make drift`. Output: `Drift report: .atlas/spans.sqlite split at 12h`, `3 alert(s): judge_overall, judge_grounded, judge_resolved`; `judge_grounded | alert | 0.877 | 0.588 | -32.9% | … | PSI 2.079`; `cost_per_request_usd | ok | -5.7%`; `latency_ms | watch … mean improved`. Then the Ops Console Quality page, "Judge scores by prompt version": v1 overall 0.910, v2 0.711.]

Replay the prompt-regression day and run the drift report. Three alerts, all judge scores. Grounded falls from point eight eight to point five nine, a PSI of two. Cost and latency? Cost per request down six percent, latency down: the incident's signature. And the Quality page's split by prompt version points straight at version two. That's AT-19.

[CODE: `evals/to_dataset.py`, close the loop (abbreviated)]
```python
def select_bad_traces(store, *, threshold: float = 0.6, limit: int = 100) -> list[DatasetItem]:
    judge = {s.trace_id: s.value for s in store.scores(name="judge_overall")}
    fb = {s.trace_id: s.value for s in store.scores(name="user_feedback")}
    ...   # judge below threshold, negative feedback, step_limit or error outcome -> a DatasetItem with
          # masked input, tenant, intent, prompt_version and source_trace_id

def push_to_langfuse(items, *, dataset_name="atlas-failures") -> int:
    ...
    lf.create_dataset_item(dataset_name=dataset_name, input=it.input, expected_output=it.expected_output,
                           metadata=it.metadata, source_trace_id=it.source_trace_id)
```

And the loop closes. `make dataset` turns every low-scoring or thumbs-down trace into a dataset item with its tenant and prompt version, and pushes it to `atlas-failures` when Langfuse is configured. The live-evals job in CI runs against that dataset. Production failures become next week's regression suite.

[SLIDE 1: Recap, Part A]
- Judge a sample; report what judging costs
- Drift by window and by prompt version
- Failures become the regression dataset

[SCREEN: Switch to Part B title card.]

### Script: Part B — dashboards, alerts and the red pull request

[AVATAR]
Now the operations pillar. Dashboard, alerts, CI. All as code, all in the repo.

[SCREEN: `deploy/grafana/dashboards/atlas-ops.json` in VS Code, collapsed to panel titles. Then Grafana on `localhost:3001` with the provisioned "Atlas Ops" dashboard and swarm traffic. Footer: "verify against current Grafana docs".]

[SLIDE 2: The Atlas Ops dashboard, as shipped]
- Variables: `tenant`, `feature`; annotation: releases from `atlas_build_info`
- SLIs: task success, containment, p95 latency, cost per resolved session
- Traffic and latency: requests, p50/p95/p99, TTFT by model, outcomes, steps, tool errors
- Cost: per tenant, per feature, tokens, cache hit ratio, retries, budget decisions
- Quality and safety: judge mean, feedback, guardrail events, export failures

Twenty-one panels in four rows, every one backed by a metric from `metrics.py`. Four SLI tiles across the top. Traffic and latency. Cost, including the cache hit ratio and budget decisions. Quality and safety, including the telemetry export failures from Lecture 13.5. Two variables, tenant and feature, because Priya's first question is always "which department". And a release annotation, so a deploy draws a vertical line.

One honest gap: the judge panel stays empty. The judge runs as a batch job and never writes the Prometheus histogram. If you wire it in your capstone, that's a diff note in your favour.

[CODE: `deploy/alerts.yml`, three of the ten rules]
```yaml
      - alert: AtlasLatencyP95High
        expr: histogram_quantile(0.95, sum(rate(atlas_request_latency_seconds_bucket[5m])) by (le)) > 4
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "Atlas p95 latency above 4 s"
          runbook: "10-resources/runbook-template.md#latency"

      - alert: AtlasTenantCostAnomaly
        expr: |
          sum(increase(atlas_cost_usd_total[1h])) by (tenant)
          > 2.5 * (sum(increase(atlas_cost_usd_total[1d] offset 1h)) by (tenant) / 24)
          and sum(increase(atlas_cost_usd_total[1h])) by (tenant) > 1
        for: 15m
        labels: { severity: ticket }

      - alert: AtlasToolErrorRate
        expr: |
          sum(rate(atlas_tool_calls_total{outcome="error"}[10m])) by (tool)
          / sum(rate(atlas_tool_calls_total[10m])) by (tool) > 0.05
        for: 10m
        labels: { severity: ticket }
```

Three of the ten rules, read exactly as written. Latency: p95 above four seconds for ten minutes pages someone. Cost: a tenant's spend in the last hour above two and a half times its average hour over the previous day, and above a dollar, for fifteen minutes, raises a ticket. Tool errors: any tool above five percent errors for ten minutes raises a ticket, not a page, because with bounded retries a failing tool at two a.m. is a morning problem.

Two gaps to close in your capstone. Only the latency rule carries a runbook link. And none carries an owner. AT-22 asks for both.

[SCREEN: `OFFLINE=1 make replay SCENARIO=context_bloat`, then the Ops Console Alerts page: `[PAGE] latency_p95 p95 6560 ms > 4000 ms` and `[TICKET] tenant_budget ops at 73% of hard cap`. Then the Budgets page, tenant ops: anomaly bins at 09:30, 09:45, 10:15, 10:30, 10:45.]

Now make one fire. Replay the context-bloat day and open the console's Alerts page. A page for latency at six and a half seconds, and a ticket because ops has used seventy-three percent of its hard cap. And the Budgets page flags ops's cost per request as anomalous from nine thirty, thirty minutes after the bloat starts. That's AT-15's detection half, offline. The Grafana version needs history: the cost-anomaly rule compares against the previous day, so on a fresh stack it has nothing to compare with. Run the stack for a day, then record it firing.

Last, the pull request.

[DEMO: Branch `faq-pilot-topk-20`; in `.github/workflows/ci.yml` add `ATLAS_TOP_K: "20"` to the `budget-gate` job's `env`; push and open a PR. Checks: `unit + integration (offline)` green; `budget gate` red: `p95 4120 ms exceeds budget 4000 ms` and `a generation sent 34,990 input tokens (> 24,000)`. Branch protection shows the gate as required; the merge button is disabled.]

Branch, set top-k to twenty in the gate's environment, push, open the pull request. Tests pass. The budget gate fails twice, each time with a number. And because the gate is a required check in branch protection, the merge button is grey. That screenshot is AT-24, and it's the one Priya asked for by name: the pull request that failed.

[SLIDE 3: Part B against the tests]
- AT-19, AT-20: drift isolates v2; judge cost reported
- AT-21: no user or session labels on `/metrics`
- AT-22: three alerts, each with runbook, owner, a firing screenshot
- AT-24: gate red on a top-k change, required for merge

[AVATAR]
Three more diff notes to look for in your branch. Did your judge's cost make it into the report? Do your alerts have owners and runbooks? And is the gate *required*, or merely present? A gate that isn't required is a suggestion.

[SLIDE 4: Recap]
- Judge, feedback, drift, dataset: one loop
- Dashboard and alerts are code; add owners
- The gate is required, and red with a number

**Recap:** The sampled judge and feedback write scores and report their own cost, the drift report isolates a prompt version, failures become dataset items, the dashboard and alert rules are provisioned from the repo with runbooks and owners still to add, and the budget gate is a required check that goes red with a number.

**Transition:** Next, the last deliverable: the weekly ops report that turns all of this into one page a manager reads.

### Speaker notes: common student mistakes / Q&A

- Real outputs (numbers card §4, re-run 2026-10-04): `make judge` after the baseline replay: `candidates=10112 sampled=894 scored=894 already_scored=2971 mean_overall=0.909 est_judge_cost=$1.9310`; `make feedback` after it: `feedback=1291 (12.7% of 10184 requests) positive=79% joined_with_judge=639 agreement=57%`. Prompt-regression drift (`make replay SCENARIO=prompt_regression` then `make drift`, split at 12:00): three alerts; grounded 0.877 → 0.588, PSI 2.079. `context_bloat` console alerts: `latency_p95` 6,560 ms (page), `tenant_budget` ops 73% of hard cap (ticket). Gate with `ATLAS_TOP_K=20`: p95 4,120 ms; 34,990 tokens.
- Dashboard as shipped: 21 panels in 4 rows (plus a build-info table), variables `tenant` and `feature`, annotations "Annotations & Alerts" and "Releases". There is no drift gauge and no prompt-label annotation; do not narrate them.
- `AtlasJudgeScoreLow` exists in `alerts.yml` but cannot fire: `atlas_judge_score` is never observed. Same reason the judge panel is empty.
- `AtlasTenantCostAnomaly` uses `offset 1h` over a 1-day window; on a fresh Prometheus it has no baseline. Do not promise a Grafana firing inside one swarm run.
- In `deploy/alerts.yml` only `AtlasLatencyP95High` has a `runbook` annotation and no rule has an owner label. The capstone asks students to add both (AT-22).
- DeepEval calls per the curriculum reference: `GEval(name=, criteria=, evaluation_params=[...], threshold=, model=)`, `LLMTestCase(input=, actual_output=, retrieval_context=)`. Confirm `metric.score` and `metric.reason` on deepeval 4.2 before recording.
- Branch protection is a GitHub repo setting; students on personal forks must enable it themselves for AT-24's "required" part. A screenshot of the red check is acceptable if they explain that.

---

## Lecture 14.4 — The weekly ops report your manager reads

| Field | Value |
|---|---|
| ID | 14.4 |
| Type | SC (screencast / code-along) |
| Target duration | 8:00 (~675 spoken words; the rest is code and the report read on screen) |
| Learning objectives | 1. Generate a one-page weekly markdown report from cost records, latency samples, judge scores, feedback and incidents with `northwind.report.weekly_report`. 2. Choose the headline numbers a manager needs and the ones they don't. 3. Write recommendations that name a number and an action, and add the owner. |
| Prerequisites | 14.2, 14.3; Lecture 6.3 (showback), 8.5 (drift), 9.1 (SLIs) |
| Files used | `src/northwind/report.py`, `src/northwind/cost.py`, `src/northwind/slo.py`, `src/northwind/drift.py`, `src/northwind/latency.py`, `telemetry/local_store.py`, `Makefile` |

### Script

[B-ROLL: Two documents. Left: a twelve-page PDF titled "Atlas Observability Weekly", dense charts. Right: one page, a headline table at the top, numbered recommendations at the bottom. A hand picks up the right one.]

[AVATAR]
Nobody reads the twelve-page report. Everybody reads the one-pager, and then they ask a question, and *that's* when they want the twelve pages. So we build the one page, and we make sure the twelve pages are one click away in the console.

`report.py` is pure Python, no network, fully unit-tested, like everything in `src/northwind`. It takes a `ReportInputs` and returns markdown. Let's read it top to bottom, then generate one.

[SCREEN: `src/northwind/report.py`. Footer visible.]

[CODE: the inputs]
```python
@dataclass
class ReportInputs:
    records: Sequence[CostRecord]                 # from LocalSpanStore.cost_records()
    latencies: Sequence[LatencySample] = ()       # from LocalSpanStore.latency_samples()
    judge_scores: Sequence[float] = ()
    feedback_positive: int = 0
    feedback_negative: int = 0
    incidents: Sequence[IncidentNote] = ()        # title, started, duration_min, impact, root_cause, status
    drift: Sequence[DriftResult] = ()             # from evals.drift_report.compare_split / compare_stores
    previous_week_cost_usd: float | None = None
    period_start: date = ...; period_end: date = ...
    latency_budget_ms: float = 4000.0
    cost_budget_usd: float = 0.05
    tool_calls: int = 0; tool_errors: int = 0
    recommendations: list[str] = field(default_factory=list)

def weekly_report(inputs: ReportInputs) -> str: ...
```

One dataclass in, one string out. The inputs are the same objects the Ops Console uses: cost records and latency samples from the local store, judge scores, feedback counts, incident notes, drift results from the weekly drift report, last week's total for the comparison, and the two budgets. That's how AT-09 stays true: the report can't disagree with the console because it aggregates the same records with the same functions, `total_cost`, `cost_per_session`, `rollup`, `summarize`, `compute_slis`.

[CODE: the headline table, from `weekly_report`]
```python
lines.append("## Headline numbers\n")
lines.append("| metric | value | note |")
lines.append(f"| Total LLM cost | ${float(total):,.2f} | vs last week {_pct(float(total), prev)} |")
lines.append(f"| Requests | {len(recs):,} | sessions: {sessions:,} |")
lines.append(f"| Cost per session | ${float(cps):.4f} | budget ${inputs.cost_budget_usd:.4f} |")
lines.append(f"| Cost per resolved session | ${snap.cost_per_resolved_session:.4f} | |")
lines.append(f"| Latency p50 / p95 | {lat.p50:.0f} / {lat.p95:.0f} ms | budget p95 {inputs.latency_budget_ms:.0f} ms |")
lines.append(f"| TTFT p95 | {ttft.p95:.0f} ms | |")
lines.append(f"| Judge score (mean, n={len(inputs.judge_scores)}) | {mean:.2f} | sampled |")
lines.append(f"| User feedback | {pos}👍 / {neg}👎 | {pos / fb_total:.0%} positive |")
```

The headline table. Total cost against last week. Requests and sessions. Cost per session against its budget. Cost per resolved session, which is Priya's number and the number engineering managers are asked for in 2026. p50 and p95 against the budget. TTFT. The judge mean with the sample size, because a mean without an n is a rumour. And feedback as a positive share.

Notice what's not there. Tokens. Cache hit rate. Model mix. Those are your numbers, and they're in the console. The manager's rows are outcomes and money, with the budget beside each so they can see the gap without asking.

[CODE: SLOs and showback]
```python
lines.append("## SLOs\n")
for row in snap.report(DEFAULT_SLOS):                 # compute_slis(...) from slo.py, Lecture 9.1
    lines.append(f"| {row['sli']} | {row['value']:.3f} | {row['target']} | {row['error_budget_remaining']} | {row['burn_rate']} | {'✅' if row['ok'] else '❌'} |")

lines.append("## Cost by tenant (showback)\n");  lines.append(showback_table(recs, "tenant"))
lines.append("## Cost by feature\n");            lines.append(showback_table(recs, "feature"))
lines.append("## Cost by model\n");              lines.append(showback_table(recs, "model"))
```

Then the SLO table, straight from `compute_slis` and the default SLOs in `slo.py`: value, target, error budget remaining, burn rate, and a tick or a cross. This is the section that makes "better or worse" a yes-or-no question.

Then showback, three ways: by tenant, by feature, by model. That's Lecture 6.3's table, one week wide. Priya reads the tenant table. Finance reads all three.

[CODE: drift, incidents and recommendations]
```python
if inputs.drift:
    lines.append("## Drift vs previous week\n"); lines.append(drift_report_markdown(inputs.drift))

lines.append("## Incidents\n")
for i in inputs.incidents:
    lines.append(f"| {i.title} | {i.started} | {i.duration_min} min | {i.impact} | {i.root_cause} | {i.status} |")
# or: "No incidents this week."

lines.append("## Recommendations\n")
for n, r in enumerate(inputs.recommendations or default_recommendations(inputs), 1):
    lines.append(f"{n}. {r}")
```

Drift, rendered by the same `drift_report_markdown` the evals use. Incidents as a table with duration, impact and root cause in one line each, linking to the postmortem, or "No incidents this week", which is the best sentence in any report. And recommendations: yours if you pass them, otherwise generated.

[CODE: `default_recommendations`, abbreviated]
```python
def default_recommendations(inputs: ReportInputs) -> list[str]:
    recs = []
    if top_tenant_share > 0.4:
        recs.append(f"Tenant `{top.key}` is {share:.0%} of spend; review its budget cap and the context diet before the next billing cycle.")
    if total_cached / total_in < 0.3:
        recs.append(f"Prompt cache hit ratio is {ratio:.0%}; stabilise the prompt prefix and send `prompt_cache_key` to lift it above 50%.")
    if stats.p95 > inputs.latency_budget_ms:
        recs.append(f"p95 latency {stats.p95:.0f} ms exceeds the {budget:.0f} ms budget; check provider TTFT and retrieval top-k.")
    if mean_judge < 0.75:
        recs.append(f"Mean judge score {mean:.2f} is below 0.75; compare prompt versions and roll back if needed.")
    return recs or ["No action needed; keep the budget gate in CI and re-check next week."]
```

Four rules, and each recommendation they produce has two parts: a number and an action. "Prompt cache hit ratio is zero percent; stabilise the prefix and send the cache key." "p95 exceeds the four-thousand budget; check TTFT and top-k." When you paste the report into the email, add the third part yourself: an owner. A recommendation with a number, an action and a name gets done. And keep it to three. A report with nine recommendations is a report with none.

[SCREEN: Terminal, after the baseline `OFFLINE=1 make replay`: `mkdir -p reports && make report > reports/2026-09-14-atlas-weekly.md`. The file opens: "# Atlas weekly ops report — 2026-09-14 to 2026-09-20". Scroll it in fifteen seconds: headline table (Total LLM cost $56.28; Requests 10,184, sessions 4,000; Cost per session $0.0141, budget $0.0500; Cost per resolved session $0.0144; p50 / p95 3232 / 3827 ms; TTFT p95 1702 ms; Judge 0.91, n=2971; feedback 1016👍 / 275👎, 79% positive); SLOs, five rows, all ✅; showback by tenant (ops $20.27, 36.0%), feature and model; "No incidents this week."; one recommendation: "Prompt cache hit ratio is 0%; stabilise the prompt prefix and send `prompt_cache_key` to lift it above 50%."]

Generate it for the replayed day. One page. Total cost fifty-six twenty-eight, the same number as the console and the compare page. Cost per resolved session, one point four cents. p95 three point eight seconds against four. Five SLOs, all ticked. Showback with ops at thirty-six percent. No incidents. And one recommendation, with a number: the cache hit ratio is zero, because the baseline replay runs with caching off. Turn on the levers from 14.2, regenerate, and that line disappears. `make report` doesn't pass drift results or incident notes; your capstone report should, because Priya asked for both.

[SLIDE 1: Rules for the one-pager]
- Headline numbers with last week and the budget beside each
- Outcomes and money for the manager; tokens and model mix stay in the console
- Same aggregation code as the console, so the numbers cannot disagree
- Recommendations: at most three, each with a number and an action; add the owner when you send it
- Generated, dated, committed to `reports/`; never hand-edited

Five rules. Headline numbers with comparison and budget. Outcomes and money up top. Same aggregation code as the console. Three recommendations, each with a number and an action, plus an owner when you send it. And generated, dated and committed, never hand-edited, because the moment someone edits a report by hand it stops being evidence.

[AVATAR]
Send this every Monday morning. After three weeks, the manager starts forwarding it to their manager. That's how observability gets budget.

[SLIDE 2: Recap]
- One page: outcomes and money first
- Same aggregation code as the console
- At most three recommendations, with numbers

**Recap:** `weekly_report` turns a `ReportInputs` into one page: headline numbers against last week and the budgets, SLOs with ticks and crosses, showback by tenant, feature and model, drift, incidents and at most three recommendations, using the same aggregation as the console so nothing disagrees.

**Transition:** Next, submitting the capstone and turning it into a portfolio piece that gets you interviews.

### Speaker notes: common student mistakes / Q&A

- Mistake: the report computes its own cost. Insist on `cost.total_cost`, `cost_per_session` and `rollup` shared with the console; AT-09 depends on it.
- Names as shipped in `src/northwind/report.py`: `ReportInputs`, `IncidentNote(title, started, duration_min, impact, root_cause, status)`, `weekly_report`, `default_recommendations`, `_pct`. Section headings: "Headline numbers", "SLOs", "Cost by tenant (showback)", "Cost by feature", "Cost by model", "Drift vs previous week", "Incidents", "Recommendations".
- `make report` prints the markdown to stdout; redirect it into a `reports/` folder in your fork (create it first). The target builds `ReportInputs` from `LocalSpanStore.cost_records('request')`, `latency_samples()` and the `judge_overall` / `user_feedback` score records; it passes no `drift`, `incidents` or `previous_week_cost_usd`, so those sections show "-" or "No incidents this week". Real output for the baseline day is in the numbers card §1 and §4.
- Mistake: percentages without a denominator. The judge row prints `n=`; students who add their own rows should too.
- "Should the report include the incident postmortem text?" No; one line per incident, link the postmortem. One page.

---

## Lecture 14.5 — Capstone submission and portfolio

| Field | Value |
|---|---|
| ID | 14.5 |
| Type | TH (talking head / avatar with slides) |
| Target duration | 5:00 (~510 spoken words) |
| Learning objectives | 1. Assemble the seven deliverables into a repository a reviewer can evaluate in fifteen minutes. 2. Write a README and portfolio post that lead with numbers, not adjectives. 3. Present incident postmortems as evidence of operational judgement. |
| Prerequisites | 14.1 to 14.4 |
| Files used | `05-projects/capstone-atlas-ops.md`, `ACCEPTANCE.md`, `DIFF_NOTES.md`, `reports/` |

### Script

[B-ROLL: A GitHub README. Top: a Grafana screenshot. Below, an example student's headline: "Daily cost $56.28 → $19.07 on a replayed day (−66%), judge scores unchanged. 4,000 sessions, p95 3.7 s. 21 of 24 acceptance tests." A recruiter scrolls, stops, clicks.]

[AVATAR]
A reviewer, or a hiring manager, gives your repository about fifteen minutes. This lecture is about what they see in those fifteen minutes.

[SLIDE 1: Repository structure a reviewer can navigate]
- `README.md`: what it is, three numbers, how to run it offline in five commands, screenshots
- `ACCEPTANCE.md`: 24 tests, PASS or FAIL, evidence link per row
- `REPORT-week.md`: the generated weekly report
- `INCIDENTS.md` and `postmortems/`: five scenarios, plus Section 11 and Project 2
- `DIFF_NOTES.md`: three differences from the reference and what you did about each
- `deploy/`, `tests/`, `.github/workflows/`: the stack and the gate, unchanged in shape from the course

The README first. What Atlas is, in two sentences. Then three numbers before anything else: cost per resolved session and the saving against baseline, p95 under the slow-provider scenario, and your acceptance score. Then how to run it offline in five commands, because a reviewer who can't run it in five minutes won't. Then screenshots: console, Grafana, an alert firing, a red pull request.

`ACCEPTANCE.md` is the second thing they open. Twenty-four rows, pass or fail, and every pass links to evidence: a test name, a screenshot file, a CI run. A fail with an honest reason scores better than a pass without evidence.

Then the reports folder, the postmortems, and your diff notes.

[SLIDE 2: Numbers beat adjectives]
| Weak | Strong |
|---|---|
| "Comprehensive observability" | "Every generation, tool and retriever span carries GenAI attributes; 40 integration tests in CI" |
| "Significantly reduced costs" | "Daily cost $56.28 → $19.07 on a replayed day (−66%); caching −34%, diet −25%, routing −16% alone" |
| "Robust to failures" | "Collector down under load: spans dropped, every request served; 3 exporter-failure tests" |
| "Monitoring and alerting" | "21-panel Grafana dashboard as code; 3 owned alerts with runbooks; anomaly flagged 30 min after onset" |

Write with numbers. "Comprehensive observability" tells a reader nothing. "Every span carries GenAI attributes, forty integration tests in CI" tells them you know what the attributes are and that you tested them. "Significantly reduced costs" is marketing. "Sixty-six percent on a replayed day, broken down by lever" is engineering. Every line in the right-hand column comes from something measured in this course. Use your own numbers, not mine.

[SLIDE 3: The postmortems are the differentiator]
- Most portfolios show things that work; yours shows how you find out why things broke
- Include two postmortems from Section 11, written in your words, with the action items
- In the README: "Incident response" section, one line per incident, link to the postmortem
- Interviewers ask "tell me about a time something broke": now you have three

Here's what makes this portfolio different from a thousand "I built a RAG chatbot" repositories. The postmortems. Most portfolios show things that work. Yours shows how you find out why something broke, and what you changed so it can't break the same way. Put an "Incident response" section in the README with one line per incident and a link. When an interviewer asks "tell me about a time something broke in production", you have three stories with timelines and numbers. Say that they were simulated incidents on a replayed dataset. The method is real, and interviewers know the difference between method and luck.

[SLIDE 4: The portfolio post]
- Title with a number: "Cutting an AI agent's daily cost by 66% without moving its quality scores"
- Three paragraphs: the problem, what you built (with the architecture diagram), what you measured
- One incident story in four sentences
- Link to the repo; mention offline mode so anyone can run it
- No vendor bashing; credit the tools

The write-up, on GitHub, LinkedIn or your blog. A title with a number in it. Three paragraphs: the problem, what you built with the architecture diagram, what you measured. One incident story in four sentences. A link to the repo with a note that it runs offline, so anyone can try it. And credit the tools. Nobody hires the person who trashes Langfuse in public.

[SLIDE 5: Submission]
- Submit the repo link through the capstone assignment in this lecture
- Include `ACCEPTANCE.md` and the report in the submission text
- Post your three headline numbers in the Q&A thread "Capstone results"
- Rubric: 100 points in the brief; pass 70, distinction 90 with 22 tests passing

Submit the repository link through the assignment. Paste your acceptance summary and the report into the submission text so a reviewer sees them without cloning. And post your three headline numbers in the Q&A. The rubric in the brief is out of a hundred, pass at seventy, with the most points on cost engineering, instrumentation and quality.

[AVATAR]
One last thing. Add the domain-swap project from the next lecture before you publish the portfolio post. Two agents observed with the same stack is a much stronger story than one.

[SLIDE 6: Recap]
- Three numbers before the architecture
- Measurements, not adjectives
- Postmortems are the differentiator

**Recap:** Structure the repo so a reviewer finds the three numbers, the acceptance evidence and the postmortems in fifteen minutes, write with measurements instead of adjectives, and lead the portfolio post with a number.

**Transition:** Next, the domain swap: point the same observability stack at a different agent and adapt the SLIs.

### Speaker notes: common student mistakes / Q&A

- Mistake: READMEs that open with the architecture instead of the numbers. Numbers first; architecture in paragraph two.
- Mistake: claiming the incidents were real. Say "simulated on a replayed dataset". Honesty here is a credibility signal, not a weakness.
- "Can I include the reference solution's code?" Your branch already contains the course code under its licence; check `03-code/README.md`. Your console, tests and report must be your own.
- Check that no `.env`, API key or Langfuse secret is in the repo history before publishing. `git log -p | grep -i secret` is a five-second check.

---

## Lecture 14.6 — Domain swap: observe a different agent

| Field | Value |
|---|---|
| ID | 14.6 |
| Type | AS (assignment with short video brief) |
| Target duration | 4:00 video (~450 spoken words); assignment itself about 4 to 8 hours |
| Learning objectives | 1. Instrument a different agent, the Course 3 voice receptionist or your own, with the same OTel, Langfuse, metrics and CI stack. 2. Adapt the SLIs, budgets and alert thresholds to the new domain and justify each change. 3. Produce a second portfolio project that proves the method transfers. |
| Prerequisites | 14.2 to 14.5 (or your own capstone) |
| Files used | `10-resources/instrumentation-template.md`, `05-projects/capstone-atlas-ops.md`, Course 3 repo `agents/s13_capstone_receptionist.py` (optional) |

### Script

[AVATAR]
Here's a question an interviewer might ask. "Nice helpdesk agent. Could you instrument ours?"

The honest answer should be "Yes, here's the second one I did." This assignment gives you that second one.

[SLIDE 1: Pick one agent]
| Option | Agent | What changes about the SLIs |
|---|---|---|
| A | Riley, the voice receptionist from *Production Voice AI Agents* | Latency budget is voice-to-voice, about 1.6 s; cost per minute, not per session; TTFT matters more than p95 total |
| B | Your own agent (any framework, any provider) | You define the SLIs from the instrumentation template |
| C | A coding or data agent with long tool loops | Steps per task and tool error rate dominate; cost per completed task |

Three options. Option A is Riley, the voice receptionist from the voice course, if you took it. Voice changes almost every SLI: the latency budget is voice-to-voice at about one point six seconds, cost is per minute of call rather than per session, and time to first token matters more than total p95 because the caller is waiting in silence.

Option B is your own agent, in any framework with any provider. You define the SLIs using the instrumentation template.

Option C, if you have neither, is a coding or data agent with long tool loops, where steps per task and tool error rate dominate and the cost unit is a completed task.

[SLIDE 2: What changes, what stays]
| Changes | Stays |
|---|---|
| The agent code and its tools | `telemetry/otel_setup.py`, `genai_attrs.py`, `langfuse_setup.py`, the Collector config |
| SLIs, budgets and alert thresholds | `pricing.py`, `cost.py`, `budget.py`, `latency.py`, `slo.py`, `drift.py`, `pii.py` |
| The unit of cost (session, minute, task) | The dashboard structure, one panel per SLI; the alert rule shape |
| Judge criteria for the domain | The judge pipeline, feedback loop, dataset promotion |
| The traffic generator or replay | The CI budget gate pattern and the weekly report structure |

What changes and what stays. The agent, its tools and its traffic are new. The SLIs, budgets, thresholds and the unit of cost change, and you must justify each one in a sentence. The judge criteria change with the domain.

What stays is most of the hard work. The telemetry modules. The whole pure-Python core: pricing, cost, budgets, latency, SLOs, drift, PII masking. The dashboard structure. The judge pipeline. The CI gate pattern. The report structure. That's the point of the assignment. The architecture is reusable. The domain is a layer on top.

[SLIDE 3: Deliverables]
- D1 A separate repo or clearly separate folder: the instrumented agent, `telemetry/` reused, `OBSERVABILITY.md`
- D2 SLI table: each SLI, its budget, and one sentence on why the number differs from Atlas
- D3 One trace screenshot with GenAI attributes; one dashboard screenshot; one alert
- D4 CI budget gate adapted to the new unit of cost, green on a run
- D5 A "What changed from Atlas" table in the README
- Bar: every generation, tool and agent span attributed; cost agrees in two places; one alert fires in a test scenario

Five deliverables. The instrumented agent with the telemetry reused and an `OBSERVABILITY.md`. An SLI table with a justification per row. Three screenshots: a trace, a dashboard, an alert. The CI gate adapted to the new cost unit. And a "What changed from Atlas" table.

The bar: every span attributed, cost agreeing in two places, and one alert that fires in a scenario you inject.

[SLIDE 4: Tips]
- Start with `instrumentation-template.md`: it asks the SLI questions before you write code
- Instrument the model call first, then tools, then the agent span; verify each with the console exporter
- Copy `telemetry/` wholesale; change `service.name` and nothing else on day one
- The hardest part is usually the unit of cost; decide it before the dashboard

Four tips. Start with the template; it asks the SLI questions before you write any code. Instrument the model call first, then tools, then the agent span, verifying with the console exporter each time, exactly like Section 3. Copy the telemetry folder wholesale and change only the service name on day one. And decide the unit of cost before you build the dashboard, because every panel depends on it.

[AVATAR]
When you're done, you'll have two agents in two domains observed with one method. Submit through the assignment in this lecture and tell us in the Q&A which agent you picked.

[SLIDE 5: Recap]
- Swap the agent, keep the stack
- Justify every changed SLI and budget
- A second project proves the method

**Recap:** Swap the agent, keep the stack, adapt the SLIs with a reason for each, and ship a second portfolio project that proves the method transfers.

[SLIDE 6: You can now]
- Assemble tracing, cost, quality and alerts into one system
- Prove a saving and a gate with replayed data
- Report it on one page a manager reads

**Transition:** Next, a short quiz to review the capstone, then Section 15: what you can now do, and the careers it leads to.

### Speaker notes: common student mistakes / Q&A

- Mistake: copying Atlas's budgets unchanged. The rubric asks for a justification per SLI; "same as Atlas" without a reason loses marks.
- Voice students: cost per minute needs STT and TTS pricing in `pricing.py`'s fallback table; LiteLLM's table covers LLMs only. Say so in the README.
- "My agent uses a framework with its own tracing." Fine: OpenInference or OpenLLMetry instrumentors exist for most; pick one, not two (Lecture 3.6).
- Students without a second agent can use option C with the course's own `simulator/` as the traffic generator against a tiny stub agent; say so in Q&A.

---

## Lecture 14.7 — Quiz: Capstone review

| Field | Value |
|---|---|
| ID | 14.7 |
| Type | QZ (6 questions, short video intro) |
| Target duration | 5:00 total (1:00 video, ~105 spoken words, about 0:45 of talking at 140 wpm; the quiz itself is untimed) |
| Learning objectives | 1. Check the assembly order and the single-cost-computation rule. 2. Check the quality loop from judge to dataset. 3. Check what the CI gate does and does not catch. |
| Prerequisites | 14.1 to 14.6 |
| Files used | `06-assessments/quizzes/section-14.md` |

### Script

[AVATAR]
Six questions to review the capstone.

[SLIDE 1: Quiz: Capstone review]
- 6 questions
- Startup order: provider, Langfuse, instrumentor, metrics
- Cost computed once; where it is written
- Judge, drift, dataset: the loop
- What the budget gate catches and what it does not
- The headline numbers in the weekly report

They cover the startup order and why it matters, the one-place cost rule, the quality loop from judge to drift report to dataset, what the CI gate can and cannot catch, and which numbers belong at the top of the weekly report. If you miss the gate question, rewatch the last slide of Lecture 13.3; it comes up in interviews.

**Recap:** The quiz checks the assembly rules and the loops that make the capstone one system.

**Transition:** Section 15 is next: what you can now do, the roles that hire for it, and twelve interview questions with model answers.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "the budget gate catches provider slowdowns". It doesn't; the mock is not the provider. Point to Slide 1 of 13.3.
- Second: students list tokens and TTFT among the manager's six numbers. Outcomes and money; the rest lives in the console.
