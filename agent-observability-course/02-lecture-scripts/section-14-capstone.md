# Section 14: Capstone: The Atlas Ops Console

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈55 min (8 lectures, curriculum v1.0)
> **Source of truth:** `01-curriculum/curriculum.md`; project brief `05-projects/capstone-atlas-ops.md`; domain swap `10-resources/instrumentation-template.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / langsmith 0.14; check the repo README for updates."
> **Recording note:** 14.2 and 14.3 are each recorded as Part A and Part B uploads, each under ten minutes. 14.1a is the build-first gate: it must be uploaded between 14.1 and 14.2 and never merged into either.

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
| 14.1 | Capstone brief and acceptance criteria | SL | 6:00 | ~757 |
| 14.1a | Build it yourself first: the capstone gate | TH | 3:00 | ~407 |
| 14.2 | Reference solution part A: instrumentation and cost (Part A / Part B) | SC | 12:00 (6:00 + 6:00) | ~912 |
| 14.3 | Reference solution part B: quality, dashboards, alerts, CI (Part A / Part B) | SC | 12:00 (6:00 + 6:00) | ~768 |
| 14.4 | The weekly ops report your manager reads | SC | 8:00 | ~634 |
| 14.5 | Capstone submission and portfolio | TH | 5:00 | ~510 |
| 14.6 | Domain swap: observe a different agent | AS | 4:00 video | ~452 |
| 14.7 | Quiz: Capstone review | QZ | 5:00 (1:00 video intro) | ~106 |

**Names used in this section (match `03-code/`).** Students build in their own branch or fork of `03-code/` and name their console module `console/my_ops_console.py` so it never collides with the reference `console/ops_console.py`. Shipped entry points: `telemetry/otel_setup.py::configure_tracing(settings, exporter_kind=, store=, batch=)`, `shutdown_tracing`, `exporter_health`; `telemetry/langfuse_setup.py::init_langfuse(settings, tracer_provider=)`, `trace_attributes`, `create_score`, `get_prompt_text`, `push_prompts`; `telemetry/genai_attrs.py::set_agent`, `set_tenant_context`, `set_llm_request`, `set_llm_usage`, `set_cost`, `set_tool`, `set_retrieval`, `set_guardrail`, `add_event`; `telemetry/metrics.py::record_generation`, `record_request`, `record_tool`, `metrics_app`, counters `REQUESTS`, `COST`, `BUDGET_DECISIONS`, `FALLBACKS`, `TOOL_CALLS`, `JUDGE_SCORE`, `EXPORTER_FAILURES`; `src/northwind/pricing.py::estimate_cost -> CostBreakdown`; `src/northwind/cost.py::CostRecord`, `rollup`, `total_cost`, `cost_per_session`, `showback_table`; `src/northwind/budget.py::BudgetGuard.decide -> BudgetDecision`, `Decision`, `EWMAAnomalyDetector`; `app/agent.py::AtlasAgent.run`, `build_router_config`, `CircuitBreaker`, `FALLBACKS`; `src/northwind/slo.py::compute_slis`, `burn_rate`, `DEFAULT_SLOS`; `src/northwind/drift.py::compare_windows`, `DriftResult`, `drift_report_markdown`; `src/northwind/report.py::ReportInputs`, `IncidentNote`, `weekly_report`, `default_recommendations`; `src/northwind/sampling.py::JudgeSamplingPolicy`, `TraceSummary`. Not yet written at scripting time (names assumed): `evals/online_judge.py::judge_sample`, `evals/drift_report.py::weekly_drift`, `evals/to_dataset.py::promote_failures`, `deploy/alerts/atlas-rules.yml`, `tests/budget/test_budget_gate.py`, `simulator/replay.py`, Makefile targets. Acceptance criteria are numbered AC-01 to AC-20 in the brief.

---

## Lecture 14.1 — Capstone brief and acceptance criteria

| Field | Value |
|---|---|
| ID | 14.1 |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (~760 spoken words) |
| Learning objectives | 1. Turn the engineering manager's request into requirements by pillar: traces, cost, reliability, quality, operations. 2. Explain the twenty acceptance criteria, how each is verified, and the pass bar. 3. Draw the capstone architecture from Atlas to the Collector, Langfuse, Prometheus, Grafana and CI. |
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

Here's the scenario. Priya Raman runs engineering at Northwind. Atlas has been in pilot with one department. She wants to roll it out to all four, and she won't until she gets four things. Cost per resolved question, by department. A week-over-week quality trend. Paging before finance notices. And a gate that stops bad changes with a number.

Read her sentence like an engineer. "Cost per resolved question" means cost attribution joined with a resolution signal: Sections 6 and 8. "Better or worse week over week" means drift: Lecture 8.5. "Paged before finance" means anomaly alerts with owners: Lectures 6.7 and 9.5. "A number telling us so" means the CI budget gate: Lecture 13.3. And "show me the console, the report, the pull request" are three deliverables.

[SLIDE 2: Requirements by pillar]
- Traces: every LLM, tool, retriever and agent span with GenAI attributes; sessions, users, tenants; release tag; masking
- Cost: price table with fallback; cost per request, session, user, tenant, feature; caching, context diet, small-model-first routing; per-tenant budgets
- Reliability: TTFT and p95 measured; timeouts, bounded retries, fallback; p95 ≤ 4 s during the `slow_provider` scenario
- Quality: sampled online judge; feedback endpoint; weekly drift; failures promoted to a dataset
- Operations: Prometheus metrics, Grafana dashboard, three alert rules with runbooks; self-hosted stack; CI budget gate; weekly report

The requirements table in the brief has five pillars. Traces: everything tagged, sessioned, released and masked. Cost: attribution at every level, plus the three savings techniques and per-tenant budgets. Reliability: measured latency and the fallbacks, holding p95 under four seconds while the provider is slow. Quality: the judge, feedback, drift and the dataset loop. Operations: metrics, a dashboard, alerts, the self-hosted stack, the CI gate and the weekly report.

You've built every one of these. The capstone is assembling them so they agree with each other. The cost on the span, the cost in Prometheus and the cost in the report must be the same number. That's harder than it sounds and it's where most of the marks are.

[SLIDE 3: 20 acceptance criteria]
| Pillar | Examples | Verified by |
|---|---|---|
| Traces (AC-01 to AC-04) | AC-01 every generation carries `gen_ai.usage.*` and `gen_ai.request.model`; AC-03 tool result masked | integration test with in-memory exporter |
| Cost (AC-05 to AC-09) | AC-05 cost per session within 2% across span, `/metrics` and report; AC-08 40% saving on the replayed day vs baseline | replay comparison in Ops Console |
| Reliability (AC-10 to AC-12) | AC-10 p95 ≤ 4,000 ms in `slow_provider`; AC-11 fallback rate > 0 in that scenario | `ATLAS_SCENARIO=slow_provider make replay` |
| Quality (AC-13 to AC-16) | AC-13 judge on ≥ 5% of traces (`JUDGE_SAMPLE_RATE`); AC-15 drift report flags `prompt_regression` scenario | `evals/drift_report.py` output |
| Operations (AC-17 to AC-20) | AC-17 dashboard with tenant variable; AC-18 an alert fires during `context_bloat`; AC-19 CI gate red on `ATLAS_TOP_K=20`; AC-20 weekly report generated | screenshots, CI link, report file |

Pass: 14 of 20. Excellent: 18 or more.

Twenty acceptance criteria, four per pillar, each with a way to verify it. Some are tests: an integration test asserts every generation span carries usage and model attributes. Some are replays: run the slow-provider scenario and read p95 from the console. Some are artefacts: a screenshot of an alert firing during the context-bloat scenario, a link to a red CI run on the top-k change, the generated report.

The one I'd look at first as a reviewer is AC-05. Cost per session must agree within two percent across the span attribute, the Prometheus counter and the weekly report. If those three disagree, one of them is lying, and finance will find out which.

Fourteen of twenty passes. Eighteen or more is excellent. And write your budgets and thresholds down before you measure. Moving the target after the fact is the first thing a reviewer notices.

[SLIDE 4: Architecture]
Diagram (from the Mermaid chart in `05-projects/capstone-atlas-ops.md`):
- Employees (4 tenants) and the swarm → FastAPI `/chat`, `/feedback` → `AtlasAgent` (router mode, budgets, step limit)
- Tools → `src/northwind` (pricing, cost, budget, tokens, latency, pii); KB retriever
- Telemetry: OTel SDK + `genai_attrs` → OTLP → Collector (mask, tail sample) → Langfuse (self-hosted) and optional second backend
- `/metrics` → Prometheus → Grafana `atlas-ops` dashboard + alert rules → runbooks
- Evals: `online_judge` (sampled) and `feedback` → Langfuse scores → `drift_report` weekly → `to_dataset`
- CI: unit + integration + budget gate on every PR; live evals on main; release tag on every trace
- `report.py` → weekly markdown to the manager

Here's the architecture on one slide. Employees and the swarm hit the FastAPI endpoints. The agent runs in router mode with budgets and a step limit. Tools call into the pure-Python core. Telemetry goes out over OTLP to the Collector, which masks and samples, then to your self-hosted Langfuse. Metrics go to Prometheus and Grafana, with alert rules linked to runbooks. The judge and feedback write scores, the drift report reads them weekly, failures become dataset items. CI gates every pull request. And `report.py` turns the week into one page for Priya.

[SLIDE 5: Deliverables]
- D1 Repository: your branch of `03-code/` with `console/my_ops_console.py`, tests, deploy files, CI
- D2 `ACCEPTANCE.md`: 20 criteria, PASS or FAIL, evidence for each
- D3 Screenshots: Ops Console (cost, latency, quality), Grafana, one alert, one red CI run
- D4 Weekly report generated by your `report.py` for the replayed week
- D5 Incident postmortems from Section 11 (at least two)
- D6 `DIFF_NOTES.md`, written after the reference solution
- D7 Portfolio write-up

Seven deliverables. Your repository. An acceptance report with evidence per criterion. Screenshots. The weekly report your code generated. Two postmortems from Section 11. Diff notes, which the next lecture explains. And a portfolio write-up.

The brief has a suggested week plan. Day one, telemetry and attributes clean. Day two, cost agreement across span, metrics and report. Day three, budgets, routing and the forty percent saving. Day four, reliability under the slow-provider scenario. Day five, judge, feedback and drift. Day six, dashboard, alerts and CI gate. Day seven, the report and the write-up.

And there's a minimum viable capstone if the week runs short: traces with attributes, cost per session agreeing in two places, one budget, one alert, the CI gate, and the report. Fourteen criteria. A finished smaller scope beats an unfinished big one.

[AVATAR]
The full brief, all twenty criteria and the rubric are in `05-projects/capstone-atlas-ops.md`. Read it before the next lecture, because in the next lecture I'm going to ask you to stop watching.

**Recap:** The capstone turns a manager's four questions into requirements across five pillars, twenty verifiable acceptance criteria and seven deliverables, on the architecture you assembled across the course.

**Transition:** Next, the capstone gate: why you should build this from the brief before you watch the reference.

### Speaker notes: common student mistakes / Q&A

- Mistake: treating AC-05 as trivial. Rounding, cached tokens and the judge's own cost are the usual sources of disagreement between span cost and the Prometheus counter. Point to Lecture 6.1 on token anatomy.
- "Do I need real API keys?" No. Every criterion is verifiable in offline mode. Live keys make the judge real; the mock judge produces deterministic scores for offline students.
- "Can I use LangSmith or Phoenix instead of Langfuse?" Yes, if you meet the same criteria. AC-15 and AC-16 need scores and datasets in whichever backend you pick.
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

Here's why. Watching someone assemble a system teaches you what the answer looks like. Building it from the brief teaches you why. Why the cost on the span and the cost in Prometheus drift apart. Why the alert fires twice. Why the judge's own tokens show up in the tenant's bill. You only learn those by hitting them, and you only hit them by building.

And there's a career reason. In Section 15 I'll give you twelve interview questions. Every one of them is easier to answer with a story that starts "when I built this, the hard part was". You don't get that story from typing along.

[SLIDE 1: The capstone gate]
- Time box: one week. Put the end date in your calendar now
- Build from `05-projects/capstone-atlas-ops.md` in your own branch: `console/my_ops_console.py`
- Allowed: everything from Sections 3 to 13, your labs and projects, the docs, the Q&A for concepts
- Not yet: lectures 14.2 to 14.4 and the reference `console/ops_console.py` internals
- Stuck for more than 90 minutes? Write down what you tried, cut scope, move on

So here's the deal. One week, end date in your calendar. Build from the brief in your own branch, with your own console module.

You can use everything you've built so far: every module from Sections 3 through 13, your labs, your projects, the docs, and the Q&A for concept questions. What you can't open yet is the next three lectures, or the internals of the reference console.

If you're stuck on one thing for more than ninety minutes, don't burn a day on it. Write down what you tried, use the minimum viable capstone list in the brief to cut scope, and move on. Unfinished but honest beats finished but copied.

[SLIDE 2: When you come back]
- Watch 14.2 to 14.4 as a code reviewer
- Write `DIFF_NOTES.md`: three things the reference does differently, and whether you adopted each
- Keep your version wherever it passes the acceptance criteria

When the week is up, whatever state you're in, come back and watch the reference as a code reviewer. Then write `DIFF_NOTES.md`: three things the reference does differently from yours, and whether you adopted each one. Some of mine will be better. Some of yours will be. That comparison is often the most valuable hour of the course. And wherever your version passes the criteria, keep it. It's yours.

[AVATAR]
I know it's tempting to click next. Close this video, open the brief, and start with day one.

I'll see you in a week.

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
| Target duration | 12:00 total: Part A 6:00 (~460 spoken words), Part B 6:00 (~450 spoken words); the rest is screen and typing time |
| Learning objectives | 1. Assemble the telemetry stack in one startup call: OTel provider, exporters, local store, Langfuse client with masking and release. 2. Make cost agree across the span, the Prometheus counter and the aggregation used by the report. 3. Wire budgets and small-model-first routing into the agent loop and prove the saving on the replayed day. |
| Prerequisites | 14.1a gate completed; Sections 3, 4, 6 and 7 |
| Files used | `telemetry/otel_setup.py`, `telemetry/langfuse_setup.py`, `telemetry/genai_attrs.py`, `telemetry/metrics.py`, `app/agent.py`, `app/server.py`, `src/northwind/pricing.py`, `src/northwind/cost.py`, `src/northwind/budget.py`, `console/ops_console.py` |

### Script: Part A — one startup call, one cost number

[AVATAR]
Welcome back. If you've just finished your week, well done. Open your own branch in a second window. As I walk through mine, keep notes for `DIFF_NOTES.md`.

Here's the headline for part A. The reference adds almost no new code. It makes one startup call that wires everything you already built, in the right order, and it follows one rule: cost is computed once, in one place, and everything else reads it.

[SCREEN: `app/server.py::create_app`, the startup section. Footer visible.]

[CODE: startup, `app/server.py`]
```python
from telemetry.otel_setup import configure_tracing, shutdown_tracing
from telemetry.metrics import metrics_app
from telemetry.openinference_setup import instrument_openai      # Lecture 3.5

def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    provider = configure_tracing(settings)            # provider + exporter(s) + local store + Langfuse, in that order
    if settings.openai_enabled:
        instrument_openai(provider)                   # OpenAIInstrumentor().instrument(tracer_provider=provider)
    app = FastAPI(lifespan=_lifespan)                 # lifespan calls shutdown_tracing(timeout_ms=5000) on exit
    app.mount("/metrics", metrics_app())              # Lecture 9.2
    ...
```

One call does the heavy lifting. `configure_tracing` builds the tracer provider with the resource attributes, service name, environment and release; adds the exporter named in settings, wrapped in `SafeSpanExporter` and a batch processor; mirrors every span into the local store for the Ops Console; and, if Langfuse keys are present, calls `init_langfuse` with the *same* provider. If you built two providers in your capstone, one for OTel and one for Langfuse, you got duplicate spans; that's the most common diff note from beta.

Then, only when a real OpenAI key is in play, the OpenInference instrumentor on that same provider. Then the metrics app. And on shutdown, `shutdown_tracing` with a five-second deadline, checklist item six.

Order matters. Provider first, then Langfuse on that provider, then the instrumentor on that provider. Get it out of order and either the instrumentor writes to a default provider nobody exports, or Langfuse creates its own.

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

The Langfuse client takes the shared tracer provider. Sample rate here is head sampling from Lecture 4.6; tail sampling lives in the Collector. The mask function from `pii.py`. Blocked scopes so HTTP client spans don't flood the trace. And `should_export_span`, which matters: by default Langfuse exports only spans it created or spans with `gen_ai` attributes, and our guardrail and step spans have neither. Without this line your Langfuse traces have holes.

Now the agent loop, where every span gets its attributes and its cost.

[CODE: `app/agent.py`, the generation step, abbreviated]
```python
with self.tracer.start_as_current_span(ga.llm_span_name(model)) as gen_span:
    ga.set_llm_request(gen_span, model=model, provider=ga.PROVIDER_OPENAI, conversation_id=session_id, ...)
    resp, ttft_s = self._call_llm(model=model, messages=messages, ...)
    inp, out, cached, reasoning = usage_numbers(resp.usage)
    ga.set_llm_usage(gen_span, input_tokens=inp, output_tokens=out, cache_read=cached, reasoning=reasoning, ttft_s=ttft_s)
    cost = self._price(used_model, inp, out, cached, reasoning)      # estimate_cost() from pricing.py: the ONE cost computation
    ga.set_cost(gen_span, cost)                                        # atlas.cost_usd + langfuse.observation.cost_details
    metrics.record_generation(tenant=tenant, model=used_model, feature=feature,
                              input_tokens=inp, output_tokens=out, cached=cached, cost_usd=cost.total_usd, ttft_s=ttft_s)
```

One generation span. Request attributes: model, provider, conversation id. Usage attributes from the response: input, output, cached and reasoning tokens, and TTFT from the stream. Then the line that makes AC-05 pass: `self._price`, which calls `estimate_cost` in `pricing.py`. One computation, one `CostBreakdown`. The result is written three ways. `set_cost` puts it on the span as `atlas.cost_usd` and as Langfuse's cost details attribute. `record_generation` adds it to the Prometheus counter `atlas_cost_usd_total`, labelled by tenant, model and feature, never by user. And the local store reads the same span attribute for the console and the report.

If your capstone computed cost in the metrics module and again in the report, that's the diff note. Compute once, write everywhere.

[SCREEN: Run `OFFLINE=1 make replay`, then open the Ops Console cost page and `curl localhost:8000/metrics | grep atlas_cost_usd_total`. Callout: console total $2.41 for the 400-session day; Prometheus sum $2.41.]

Replay the four-hundred-session day. Console says two dollars forty-one. Prometheus says two forty-one. In Part B, the report will say the same number. That's the criterion.

[SCREEN: Switch to Part B title card.]

### Script: Part B — budgets, routing and the saving

[AVATAR]
Part B. Budgets and routing, and then proving the saving that Section 6 promised.

[CODE: `app/agent.py::run`, the budget guard, as shipped]
```python
if self.budget_guard is not None:
    decision = self.budget_guard.decide(tenant, time.time(), next_cost_usd=0.01)
    result.budget_decision = decision.decision.value
    metrics.BUDGET_DECISIONS.labels(tenant, decision.decision.value).inc()
    if decision.decision is Decision.REFUSE:
        ga.add_event(root, "budget.refused", reason=decision.reason)
        return self._refusal(result)                         # BUDGET_REFUSAL_MESSAGE: polite, one sentence
    if decision.decision is Decision.DEGRADE:
        ga.add_event(root, "budget.degraded", reason=decision.reason, model=s.degraded_model)
        model, top_k = s.degraded_model, min(top_k, 2)
    if decision.anomaly:                                     # the Incident 1 action item
        metrics.BUDGET_DECISIONS.labels(tenant, "anomaly").inc()
```

Before the loop, the budget guard from Lecture 6.7. `decide` pre-charges an estimated cent and returns allow, degrade or refuse against the tenant's soft and hard caps, twenty-five and forty dollars by default. Refuse: an event on the root span and a polite one-sentence refusal. Degrade: an event, the degraded model, `gpt-4.1-nano`, and top-k capped at two. And the line the shipped code didn't have until Incident 1: when the EWMA detector flags an anomaly, count it, so the alert rule in the next lecture can page. That's the seventy-one minutes Incident 1 lost, recovered.

[CODE: `app/agent.py`, router mode and the breaker]
```python
def build_router_config(settings: Settings) -> dict[str, Any]:
    return {
        "model_list": [...],                                      # gpt-4.1-mini, gpt-4.1, gpt-5-mini, gpt-4.1-nano
        "fallbacks": [{m: [FALLBACKS[m]]} for m in models if m in FALLBACKS],
        "num_retries": settings.max_retries,
        "timeout": settings.request_timeout_s,                    # 8.0 after Incident 2, was 20.0
        "allowed_fails": 3, "cooldown_time": 60,
    }

# _call_llm: the breaker counts timeouts and slow calls, not only exhausted retries (Incidents 1 and 2)
if self.breaker.is_open(current) and current in FALLBACKS:
    nxt = FALLBACKS[current]; metrics.FALLBACKS.labels(current, nxt).inc(); current = nxt
```

Router mode. `build_router_config` is pure data, so it's unit-tested offline: the fallback chain from `FALLBACKS`, retries and the timeout from settings. Eight seconds now, not twenty. And in `_call_llm`, the circuit breaker: when it's open for a model, the next call goes to that model's fallback and the fallback counter increments. After Section 11 it opens on timeouts and on slow calls, not only when retries are exhausted. Escalation to `gpt-4.1` is separate and unchanged: the model asks for it with the escalate marker, the agent records an event and re-runs the step on the escalation model.

Now the saving. AC-08 says forty percent against the baseline day.

[SCREEN: Ops Console, cost page, "compare replays" view. Baseline (`ATLAS_PROMPT_CACHE=0 ATLAS_CONTEXT_DIET=0 ATLAS_ROUTER_MODE=0`): $4.23. With cache, diet and router mode: $2.41. Callout: -43%. Breakdown bar: caching 19%, context diet 15%, routing 9%.]

Two replays of the same day, same seed. Baseline with caching off, the diet off and no routing: four dollars twenty-three. With all three on: two forty-one. Forty-three percent. And the console breaks it down, because "we saved money" is a claim and "caching saved nineteen percent, the diet fifteen, routing nine" is evidence. Caching is the biggest because the system prompt and tool schemas are a stable prefix over a thousand tokens; `prompt_cache_key` per prompt version and tenant, from Lecture 6.4, makes them hit.

[SLIDE 1: Part A checklist against the criteria]
- AC-01, AC-02: every generation and tool span carries `gen_ai.*`; integration test green
- AC-03: tool results masked in SDK (`langfuse_mask`) and Collector
- AC-05: cost agrees across span, `/metrics`, report: $2.41 on the 400-session day
- AC-06, AC-07: per-tenant budgets with degrade and refuse events; anomaly counter
- AC-08: 43% saving on the replayed day, broken down by technique
- AC-10, AC-11: `slow_provider` replay p95 3.5 s, fallback rate 30%

Where this leaves you against the criteria. Traces one through three, green. Cost five through eight, green, with the forty-three percent. Reliability ten and eleven, green from the slow-provider replay, same numbers as Incident 2's fix.

[AVATAR]
Compare with your branch. The three most common diff notes from beta: two tracer providers, cost computed in two places, and a breaker that only counts exhausted retries. If you had none of them, you're ahead of my first draft.

**Recap:** One `configure_tracing` call wires the provider, exporters, local store and Langfuse in order; cost is computed once in `pricing.py` and written to the span, Langfuse and Prometheus; the budget guard and the router with its breaker sit in the agent loop, and the replay comparison proves a 43% saving by technique.

**Transition:** Next, part B of the reference: the judge, drift, the dashboard, alerts and the CI gate.

### Speaker notes: common student mistakes / Q&A

- Names as shipped: `configure_tracing(settings, exporter_kind=, store=, batch=)`, `init_langfuse(settings, tracer_provider=)`, `ga.set_llm_request / set_llm_usage / set_cost / add_event`, `estimate_cost -> CostBreakdown`, `metrics.record_generation`, `BudgetGuard.decide -> BudgetDecision(decision, anomaly, ...)`, `Decision.ALLOW|DEGRADE|REFUSE`, `build_router_config`, `CircuitBreaker`, `FALLBACKS`. The `anomaly` counter line and the slow-call breaker rule are Section 11 action items; show them as the diff from the shipped file.
- `instrument_openai(provider)` is the assumed helper name in `telemetry/openinference_setup.py`; confirm before recording.
- "Why write cost to Langfuse if it computes cost itself?" Langfuse's price table may differ from yours (negotiated rates, cached tokens). Your number is the one finance sees; send it.
- The $2.41 / $4.23 / 43% figures depend on the mock LLM's cache behaviour and the 400-session default; confirm against the actual replay before recording and update the slide and the AC-05 number in 14.4.
- Prometheus label rule: tenant, model and feature only. A student who adds `user_id` gets a cardinality lecture; point to 5.5. `metrics.label_names()` exists so a unit test can assert it.

---

## Lecture 14.3 — Reference solution part B: quality, dashboards, alerts, CI (Part A and Part B)

| Field | Value |
|---|---|
| ID | 14.3 (recorded and uploaded as 14.3 Part A and 14.3 Part B, each under ten minutes) |
| Type | SC (screencast / code-along) |
| Target duration | 12:00 total: Part A 6:00 (~320 spoken words), Part B 6:00 (~450 spoken words) |
| Learning objectives | 1. Run the sampled online judge and feedback loop so scores land in Langfuse with prompt version metadata, and produce the weekly drift report. 2. Provision the Grafana dashboard and three alert rules as code, with runbook links and owners. 3. Make the CI budget gate a required check and show it red on a real regression. |
| Prerequisites | 14.2; Sections 8, 9 and 13 |
| Files used | `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py`, `evals/to_dataset.py`, `src/northwind/sampling.py`, `src/northwind/drift.py`, `src/northwind/slo.py`, `telemetry/metrics.py`, `deploy/grafana/dashboards/atlas-ops.json`, `deploy/alerts/atlas-rules.yml`, `tests/budget/test_budget_gate.py`, `.github/workflows/ci.yml` |

### Script: Part A — quality that shows up on a timeline

[AVATAR]
Part A of the reference gave Priya cost. Part B gives her "better or worse", "paged before finance", and "the pull request that failed."

Start with quality, because Incident 3 taught you that quality without a timeline is an email from HR.

[CODE: `evals/online_judge.py`, the sampled judge]
```python
from northwind.sampling import JudgeSamplingPolicy, TraceSummary
from telemetry.langfuse_setup import create_score
from telemetry import metrics

def judge_sample(store, *, since: float, policy: JudgeSamplingPolicy) -> int:
    judged = 0
    for t in store.traces_since(since):
        summary = TraceSummary.from_spans(t)                     # cost, latency, error, feedback, prompt_version
        if not policy.should_judge(summary):                     # rate from settings.judge_sample_rate, always on error or thumbs-down
            continue
        case = LLMTestCase(input=t.question, actual_output=t.answer, retrieval_context=t.snippets)
        for metric in (GROUNDED, RESOLVED, SAFE_ESCALATION):     # GEval, Lecture 8.2
            metric.measure(case)
            create_score(t.trace_id, f"judge_{metric.name}", metric.score, comment=metric.reason)
            metrics.JUDGE_SCORE.labels(metric.name).observe(metric.score)
        create_score(t.trace_id, "judge_cost_usd", judge_cost(case))   # judging is a line item
        judged += 1
    return judged
```

The judge samples at the rate in settings, ten percent by default, plus every error and every thumbs-down, because those are the ones worth a second opinion. `JudgeSamplingPolicy` from `sampling.py` makes that decision from a `TraceSummary`. Three G-Eval metrics from Lecture 8.2: grounded, resolved, safe escalation. Each writes a score to the trace with the judge's reason as the comment, through the guarded `create_score`, and observes the same value into the `atlas_judge_score` histogram so Grafana sees it within a scrape. And a fourth score: what the judging cost. Priya's cost per resolved question includes the cost of knowing it was resolved. Leave it out and your report is wrong by a few percent.

The root spans already carry `atlas.prompt_version`, so every score is sliceable by prompt version. That's the exhibit that solved Incident 3, built in.

[CODE: `evals/drift_report.py`, weekly comparison]
```python
from northwind.drift import compare_windows, drift_report_markdown

def weekly_drift(store, *, week_start: float) -> list[DriftResult]:
    this_week = store.window(week_start, week_start + WEEK)
    last_week = store.window(week_start - WEEK, week_start)
    results = [
        compare_windows("judge_grounded", last_week.scores("judge_grounded"), this_week.scores("judge_grounded")),
        compare_windows("judge_resolved", last_week.scores("judge_resolved"), this_week.scores("judge_resolved")),
        compare_windows("user_feedback",  last_week.scores("user_feedback"),  this_week.scores("user_feedback")),
        compare_windows("cost_usd",       last_week.costs(),                  this_week.costs()),
        compare_windows("latency_ms",     last_week.latencies(),              this_week.latencies()),
    ]
    results += [compare_windows(f"judge_grounded[{v}]", last_week.scores("judge_grounded"), this_week.scores("judge_grounded", prompt_version=v))
                for v in this_week.prompt_versions()]
    return results          # drift_report_markdown(results) renders it; DriftResult.alert uses DriftThresholds
```

The drift report compares this week to last for five signals with `compare_windows`, which computes the delta and the PSI from `drift.py`, and adds a comparison per prompt version. `DriftResult.alert` applies the thresholds. The reference also runs `compare_windows` hourly on `judge_grounded` alone, feeding a Prometheus gauge, because a weekly report finds Incident 3 on Monday and an hourly check finds it at ten past twelve.

[SCREEN: `OFFLINE=1 ATLAS_SCENARIO=prompt_regression make replay`, then `make eval`. Terminal shows the drift report: `judge_grounded: 0.91 → 0.72 (PSI 0.34, ALERT)`, `judge_grounded[langfuse:2]: 0.72`.]

Replay the prompt-regression scenario and run the evals. The drift report flags grounded with a PSI above the threshold, and the version breakdown points straight at version two. AC-15, green.

[CODE: `evals/to_dataset.py`, close the loop]
```python
def promote_failures(store, *, since: float, dataset: str = "atlas-failures") -> int:
    lf = client()
    bad = [t for t in store.traces_since(since) if t.score("judge_grounded") == 0 or t.score("user_feedback") == -1]
    for t in bad:
        lf.create_dataset_item(dataset_name=dataset, input=t.question, expected_output=None,
                               source_trace_id=t.trace_id,
                               metadata={"tenant": t.tenant, "prompt_version": t.prompt_version})
    return len(bad)
```

And the loop closes: every ungrounded or thumbs-down trace becomes a dataset item with its tenant and prompt version. The live-evals job in CI runs against this dataset. Production failures become next week's regression suite. AC-16.

[SCREEN: Switch to Part B title card.]

### Script: Part B — dashboards, alerts and the red pull request

[AVATAR]
Now the operations pillar. Dashboard, alerts, CI. All as code, all with owners.

[SCREEN: `deploy/grafana/dashboards/atlas-ops.json` in VS Code, collapsed to panel titles. Then Grafana with the dashboard provisioned from `deploy/grafana/provisioning/`. Footer: "verify against current Grafana docs".]

[SLIDE 1: The Atlas Ops dashboard, one panel per SLI]
- Variable: `tenant` (all, logistics-ops, warehouse, hr, finance)
- Row 1: `atlas_requests_total` rate, p95 from `atlas_request_latency_seconds` vs 4 s budget, `atlas_ttft_seconds` p95, error outcome share
- Row 2: `atlas_cost_usd_total` per hour and per session, model mix, `atlas_budget_decisions_total` by decision
- Row 3: `atlas_judge_score` (7-day), `atlas_feedback_total` thumbs-down rate, containment, drift gauge
- Row 4: `atlas_tool_calls_total` error share by tool, `atlas_model_fallbacks_total`, `atlas_telemetry_export_failures_total`
- Annotations: `deployment.release` changes and prompt label changes

Twelve panels, one per SLI from Lecture 9.1, in four rows, every one backed by a metric from `metrics.py`. Traffic and latency. Cost and budget decisions. Quality: judge, thumbs, containment, drift. Reliability: tool errors, fallbacks and telemetry export failures from Lecture 13.5. A tenant variable at the top, because Priya's first question is always "which department." And annotations for release changes and prompt label changes, so every incident from Section 11 would show a vertical line at its cause.

The dashboard JSON is provisioned from the repo, Lecture 13.4 item ten. Verify the provisioning config against current Grafana docs; the mechanism is stable, the file format details move.

[CODE: `deploy/alerts/atlas-rules.yml`, three rules]
```yaml
groups:
  - name: atlas
    rules:
      - alert: AtlasLatencyBurnRate
        expr: atlas_slo_burn_rate{sli="latency_p95"} > 14.4       # 1h window; slo.burn_rate() exposed as a gauge
        for: 15m
        labels: {severity: page, owner: atlas-oncall}
        annotations: {runbook: "runbooks/latency-burn.md"}
      - alert: AtlasTenantSpendAnomaly
        expr: increase(atlas_budget_decisions_total{decision=~"anomaly|degrade"}[15m]) > 0
        for: 5m
        labels: {severity: page, owner: atlas-oncall}
        annotations: {runbook: "runbooks/cost-anomaly.md"}
      - alert: AtlasToolErrorSpike
        expr: sum(rate(atlas_tool_calls_total{outcome="error"}[10m])) / sum(rate(atlas_tool_calls_total[10m])) > 0.2
        for: 10m
        labels: {severity: ticket, owner: atlas-team}
        annotations: {runbook: "runbooks/tool-errors.md"}
```

Three alert rules, from Lecture 9.5. Latency burn rate above fourteen point four for fifteen minutes, which is the fast-burn threshold from `slo.py`. Tenant spend anomaly or degradation, from the budget decisions counter you saw in Part A of 14.2; this is the one that would have paged at ten oh nine on Monday. And a tool error spike above twenty percent, which is a ticket, not a page, because a failing tool at two a.m. with bounded retries is a morning problem now.

Every rule has an owner label and a runbook. That's checklist item twelve.

[DEMO: `make stack-up` both stacks. `OFFLINE=1 ATLAS_SCENARIO=context_bloat make replay`. Grafana alert list: `AtlasTenantSpendAnomaly` goes pending, then firing after five minutes, tenant `logistics-ops`. Screenshot.]

Replay the context-bloat scenario. Within the first hour of simulated traffic, the spend anomaly alert fires for logistics-ops. That screenshot is AC-18. And it's Incident 1 detected in the first hour instead of the third.

Last, the pull request.

[DEMO: Create branch `kb-topk-20`, set `ATLAS_TOP_K=20` in the CI env for the budget gate (or change the `Settings` default), push, open a PR. GitHub checks: `unit` green, `budget-gate` red with the message "p95 4,310 ms > 4,000 ms budget". Branch protection shows `budget-gate` as required.]

Branch, change the top-k default to twenty, push, open the pull request. Unit tests pass. The budget gate fails with a number. And because the gate is a required check in branch protection, the merge button is grey. That screenshot is AC-19, and it's the one Priya asked for by name: the pull request that failed.

[SLIDE 2: Part B checklist against the criteria]
- AC-13, AC-14: judge on 10% plus errors and thumbs-down; feedback correlated
- AC-15: drift report flags `prompt_regression`, by prompt version
- AC-16: failures promoted to `atlas-failures`
- AC-17: dashboard provisioned, tenant variable, release annotations
- AC-18: spend anomaly alert fires during `context_bloat`
- AC-19: CI gate red on `ATLAS_TOP_K=20`, required for merge
- AC-20: weekly report (next lecture)

Where this leaves you. Quality thirteen through sixteen, green. Operations seventeen through nineteen, green. Twenty is the report, next lecture.

[AVATAR]
Three more diff notes to look for in your branch: did your judge charge its own cost to the tenant? Do your alerts have owners? And is the gate *required*, or merely present? A gate that isn't required is a suggestion.

**Recap:** The sampled judge and feedback write versioned scores, the drift report compares weeks and versions, failures become dataset items, the dashboard and three owned alert rules are provisioned from the repo, and the budget gate is a required check that goes red with a number.

**Transition:** Next, the last deliverable: the weekly ops report that turns all of this into one page a manager reads.

### Speaker notes: common student mistakes / Q&A

- Shipped names used here: `northwind.sampling.JudgeSamplingPolicy.should_judge`, `TraceSummary`; `telemetry.langfuse_setup.create_score`; `metrics.JUDGE_SCORE`, `BUDGET_DECISIONS`, `TOOL_CALLS`, `FALLBACKS`, `EXPORTER_FAILURES`; `northwind.drift.compare_windows`, `DriftResult.alert`, `drift_report_markdown`; `northwind.slo.burn_rate`, `BURN_RATE_ALERTS`. `store.traces_since`, `store.window`, `TraceSummary.from_spans` and `evals/*` are assumed interfaces not yet written at scripting time; align with the final `evals/` modules.
- DeepEval calls per the curriculum reference: `GEval(name=, criteria=, evaluation_params=[...], threshold=, model=)`, `LLMTestCase(input=, actual_output=, retrieval_context=)`. Confirm `metric.score` and `metric.reason` on deepeval 4.2 before recording.
- The 14.4 burn-rate threshold is the standard fast-burn number for a 1-hour window on a 30-day SLO (`BURN_RATE_ALERTS` in `slo.py`); students who chose different windows should show their arithmetic in `ACCEPTANCE.md`.
- Grafana provisioning and alerting file formats: verify against current docs. The rules above are Prometheus-style; if the repo uses Grafana-managed alerts, adjust the narration to match the actual file.
- Branch protection is a GitHub repo setting; students on personal forks must enable it themselves for AC-19's "required" part. The screenshot of a red check is acceptable if they explain that.

---

## Lecture 14.4 — The weekly ops report your manager reads

| Field | Value |
|---|---|
| ID | 14.4 |
| Type | SC (screencast / code-along) |
| Target duration | 8:00 (~630 spoken words; the rest is code and the report read on screen) |
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
    drift: Sequence[DriftResult] = ()             # from evals.drift_report.weekly_drift
    previous_week_cost_usd: float | None = None
    period_start: date = ...; period_end: date = ...
    latency_budget_ms: float = 4000.0
    cost_budget_usd: float = 0.05
    tool_calls: int = 0; tool_errors: int = 0
    recommendations: list[str] = field(default_factory=list)

def weekly_report(inputs: ReportInputs) -> str: ...
```

One dataclass in, one string out. The inputs are the same objects the Ops Console uses: cost records and latency samples from the local store, judge scores, feedback counts, incident notes, drift results from the weekly drift report, last week's total for the comparison, and the two budgets. That's how AC-05 stays true: the report can't disagree with the console because it aggregates the same records with the same functions, `total_cost`, `cost_per_session`, `rollup`, `summarize`, `compute_slis`.

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

Four rules, and each recommendation they produce has two parts: a number and an action. "Cache hit ratio is twenty-eight percent; stabilise the prefix and send the cache key." "p95 four thousand three hundred exceeds the four-thousand budget; check TTFT and top-k." When you paste the report into the email, add the third part yourself: an owner. A recommendation with a number, an action and a name gets done. And keep it to three. A report with nine recommendations is a report with none.

[SCREEN: Terminal, `make report WEEK=2026-09-14`. Output file `reports/2026-09-14-atlas-weekly.md` opens. Scroll it in fifteen seconds: headline table, SLOs with one ❌ on containment, showback by tenant, drift, one incident row for Monday's cost spike with its root cause, two recommendations.]

Generate it for the replayed week. One page. Headline table, SLOs with one cross on containment, showback, drift, one incident row for Monday with its root cause in a sentence, two recommendations. Total cost in the headline: the same number you saw in the console and in Prometheus. AC-05, closed. AC-20, done.

[SLIDE 1: Rules for the one-pager]
- Headline numbers with last week and the budget beside each
- Outcomes and money for the manager; tokens and model mix stay in the console
- Same aggregation code as the console, so the numbers cannot disagree
- Recommendations: at most three, each with a number and an action; add the owner when you send it
- Generated, dated, committed to `reports/`; never hand-edited

Five rules. Headline numbers with comparison and budget. Outcomes and money up top. Same aggregation code as the console. Three recommendations, each with a number and an action, plus an owner when you send it. And generated, dated and committed, never hand-edited, because the moment someone edits a report by hand it stops being evidence.

[AVATAR]
Send this every Monday morning. After three weeks, the manager starts forwarding it to their manager. That's how observability gets budget.

**Recap:** `weekly_report` turns a `ReportInputs` into one page: headline numbers against last week and the budgets, SLOs with ticks and crosses, showback by tenant, feature and model, drift, incidents and at most three recommendations, using the same aggregation as the console so nothing disagrees.

**Transition:** Next, submitting the capstone and turning it into a portfolio piece that gets you interviews.

### Speaker notes: common student mistakes / Q&A

- Mistake: the report computes its own cost. Insist on `cost.total_cost`, `cost_per_session` and `rollup` shared with the console; AC-05 depends on it.
- Names as shipped in `src/northwind/report.py`: `ReportInputs`, `IncidentNote(title, started, duration_min, impact, root_cause, status)`, `weekly_report`, `default_recommendations`, `_pct`. Section headings: "Headline numbers", "SLOs", "Cost by tenant (showback)", "Cost by feature", "Cost by model", "Drift vs previous week", "Incidents", "Recommendations".
- `make report WEEK=` and the `reports/` folder are assumed Makefile conventions (the Makefile was not yet written at scripting time); the generator script builds `ReportInputs` from `LocalSpanStore.cost_records()` and `latency_samples()` plus the score records.
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

[B-ROLL: A GitHub README. Top: a Grafana screenshot. Below: "Cost per resolved session: $0.0061 (−43% vs baseline). p95: 3.4 s under provider slowdown. 18 of 20 acceptance criteria." A recruiter scrolls, stops, clicks.]

[AVATAR]
A reviewer, or a hiring manager, gives your repository about fifteen minutes. This lecture is about what they see in those fifteen minutes.

[SLIDE 1: Repository structure a reviewer can navigate]
- `README.md`: what it is, three numbers, how to run it offline in five commands, screenshots
- `ACCEPTANCE.md`: 20 criteria, PASS or FAIL, evidence link per row
- `reports/`: the generated weekly report
- `postmortems/`: at least two from Section 11, plus Project 2 if you did it
- `DIFF_NOTES.md`: three differences from the reference and what you did about each
- `deploy/`, `tests/`, `.github/workflows/`: the stack and the gate, unchanged in shape from the course

The README first. What Atlas is, in two sentences. Then three numbers before anything else: cost per resolved session and the saving against baseline, p95 under the slow-provider scenario, and your acceptance score. Then how to run it offline in five commands, because a reviewer who can't run it in five minutes won't. Then screenshots: console, Grafana, an alert firing, a red pull request.

`ACCEPTANCE.md` is the second thing they open. Twenty rows, pass or fail, and every pass links to evidence: a test name, a screenshot file, a CI run. A fail with an honest reason scores better than a pass without evidence.

Then the reports folder, the postmortems, and your diff notes.

[SLIDE 2: Numbers beat adjectives]
| Weak | Strong |
|---|---|
| "Comprehensive observability" | "Every generation, tool and retriever span carries GenAI attributes; 41 integration assertions" |
| "Significantly reduced costs" | "Cost per resolved session $0.0061, down 43% on a replayed day; caching 18%, context diet 14%, routing 11%" |
| "Robust to failures" | "p95 3.4 s with 31% fallback rate during a simulated provider slowdown; backend outage drops spans, not requests" |
| "Monitoring and alerting" | "12-panel Grafana dashboard as code; 3 owned alerts; spend anomaly fires within the first hour of the context-bloat scenario" |

Write with numbers. "Comprehensive observability" tells a reader nothing. "Every span carries GenAI attributes, forty-one integration assertions" tells them you know what the attributes are and that you tested them. "Significantly reduced costs" is marketing. "Forty-three percent on a replayed day, broken down by technique" is engineering. Every line in the right-hand column comes from something you measured in this course. Use your own numbers, not mine.

[SLIDE 3: The postmortems are the differentiator]
- Most portfolios show things that work; yours shows how you find out why things broke
- Include two postmortems from Section 11, written in your words, with the action items
- In the README: "Incident response" section, one line per incident, link to the postmortem
- Interviewers ask "tell me about a time something broke": now you have three

Here's what makes this portfolio different from a thousand "I built a RAG chatbot" repositories. The postmortems. Most portfolios show things that work. Yours shows how you find out why something broke, and what you changed so it can't break the same way. Put an "Incident response" section in the README with one line per incident and a link. When an interviewer asks "tell me about a time something broke in production", you have three stories with timelines and numbers. Say that they were simulated incidents on a replayed dataset. The method is real, and interviewers know the difference between method and luck.

[SLIDE 4: The portfolio post]
- Title with a number: "Cutting an AI agent's cost per resolved question by 43% while holding p95 under 4 s"
- Three paragraphs: the problem, what you built (with the architecture diagram), what you measured
- One incident story in four sentences
- Link to the repo; mention offline mode so anyone can run it
- No vendor bashing; credit the tools

The write-up, on GitHub, LinkedIn or your blog. A title with a number in it. Three paragraphs: the problem, what you built with the architecture diagram, what you measured. One incident story in four sentences. A link to the repo with a note that it runs offline, so anyone can try it. And credit the tools. Nobody hires the person who trashes Langfuse in public.

[SLIDE 5: Submission]
- Submit the repo link through the capstone assignment in this lecture
- Include `ACCEPTANCE.md` and the report in the submission text
- Post your three headline numbers in the Q&A thread "Capstone results"
- Rubric: acceptance score 50%, evidence quality 20%, postmortems 15%, README and write-up 15%

Submit the repository link through the assignment. Paste your acceptance summary and the report into the submission text so a reviewer sees them without cloning. And post your three headline numbers in the Q&A. The rubric weights the acceptance score at half, evidence quality at twenty percent, postmortems at fifteen and the write-up at fifteen.

[AVATAR]
One last thing. Add the domain-swap project from the next lecture before you publish the portfolio post. Two agents observed with the same stack is a much stronger story than one.

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

**Recap:** Swap the agent, keep the stack, adapt the SLIs with a reason for each, and ship a second portfolio project that proves the method transfers.

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
| Target duration | 5:00 in the curriculum (1:00 video intro, ~90 spoken words) |
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
- Six headline numbers in the weekly report

They cover the startup order and why it matters, the one-place cost rule, the quality loop from judge to drift report to dataset, what the CI gate can and cannot catch, and which six numbers belong at the top of the weekly report. If you miss the gate question, rewatch the last slide of Lecture 13.3; it comes up in interviews.

**Recap:** The quiz checks the assembly rules and the loops that make the capstone one system.

**Transition:** Section 15 is next: what you can now do, the roles that hire for it, and twelve interview questions with model answers.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "the budget gate catches provider slowdowns". It doesn't; the mock is not the provider. Point to Slide 1 of 13.3.
- Second: students list tokens and TTFT among the manager's six numbers. Outcomes and money; the rest lives in the console.
