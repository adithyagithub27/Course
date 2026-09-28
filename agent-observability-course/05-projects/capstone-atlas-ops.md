# Capstone: The Atlas Ops Console

| Field | Details |
|---|---|
| **Section / lectures** | Section 14: 14.1 (brief), 14.1a (build-it-yourself gate), 14.2 to 14.4 (reference solution), 14.5 (submission and portfolio), 14.6 (domain swap, see the brief at the end of this file) |
| **Time box** | **One week** of build time before you watch the reference solution (about 12 to 18 hours of work) |
| **Difficulty** | Advanced |
| **Builds on** | Everything: Labs 1 to 7, Projects 1 and 2, the five challenges |
| **You will submit** | Repository, running stack (screenshots or a short screen recording), acceptance test report, weekly ops report, portfolio write-up |

---

## Stop: build it yourself first (the capstone gate)

Lecture 14.1a is a gate, not a formality. **After reading this brief, stop watching Section 14 and build.**

- **Time box: one week** from the day you start. Put the end date in your calendar now.
- Lectures 14.2 to 14.4 are the **reference solution**. Watching them first turns a portfolio project into a typing exercise, and interviewers can tell the difference when they ask "why did you choose that sampling policy?"
- **Allowed while you build:** your own Labs 1 to 7 and Projects 1 and 2, everything in `src/northwind/`, `telemetry/`, `simulator/`, `evals/`, `deploy/`, the Langfuse, OpenTelemetry, LiteLLM, Prometheus and Grafana docs, and the Q&A board (ask about concepts, not for the capstone code).
- **Not allowed until the week is over:** `03-code/console/ops_console.py`'s reference pages beyond what Lab 5 used, `src/northwind/report.py::weekly_report` (write your own), and lectures 14.2 to 14.4.
- **Stuck for more than 90 minutes on one thing?** Write down what you tried, cut the scope (see "minimum viable capstone"), and move on. Unfinished-but-honest beats finished-but-copied.
- **When the week ends**, whatever state you are in: watch 14.2 to 14.4, then write `DIFF_NOTES.md` listing three things the reference does differently from you and whether you adopted each one.

Suggested week plan:

| Day | Focus |
|---|---|
| 1 | Architecture sketch; instrumentation audit of Atlas (every LLM, tool, retriever, guardrail and agent span with GenAI attributes and Langfuse observation types); sessions, users, tenants, releases |
| 2 | Cost: price table, per-generation cost, roll-ups by tenant/feature/user, cost per resolved session; prompt caching and the context diet switched on and measured |
| 3 | Reliability: router with small-model-first and fallback, timeouts, retries, circuit breaker; budgets per tenant with soft/hard caps and EWMA anomaly |
| 4 | Quality: sampling policy, online judge, feedback, drift report; worst-trace-to-dataset loop |
| 5 | Dashboards and alerts: Prometheus metrics, Grafana Atlas Ops, three alert rules with runbooks; Ops Console pages |
| 6 | Deploy and gate: collector with redaction and tail sampling, self-hosted Langfuse (or Cloud), CI budget gate green, chaos runs (all five scenarios) |
| 7 | Weekly ops report, acceptance test report, diagram, portfolio write-up |

**Minimum viable capstone** (if the week runs out): full instrumentation with GenAI attributes and Langfuse types; cost per tenant and per resolved session; caching plus context diet measured; budgets with a hard cap that refuses; Prometheus metrics and the Grafana dashboard; one alert with a runbook; CI budget gate green; the weekly report; at least 15 of the acceptance tests below passing. Online judge, drift, collector-side sampling and the router can be listed as "next steps".

---

## Scenario

Northwind's CTO, Amara Diallo, has approved Atlas for company-wide rollout on one condition:

> "I want an operations console I can open on Monday morning and know, in two minutes, what Atlas cost last week and per department, whether people got their answers, whether it was fast, and whether anything went wrong that we did not catch. If it starts burning money at 2 a.m., I want it to stop itself and page someone. And I want a one-page report I can forward to finance and to the department heads without editing. Show me it works under the five failure modes your team keeps talking about."

The five failure modes are the simulator scenarios: `loop`, `context_bloat`, `retry_storm`, `slow_provider`, `prompt_regression`. You are the engineer presenting at the go-live review.

---

## Requirements

Build in your fork. Keep `make test`, `make budget-check` and `make eval` as the entry points.

| Area | Requirement |
|---|---|
| **Instrumentation** | Every request produces one trace: agent span (`gen_ai.agent.name`), step spans, generation spans with `gen_ai.*` usage including cached and reasoning tokens, tool spans with redacted arguments/results, retriever span with query/top-k/scores, guardrail span with a boolean score (Challenge 4.7). Sessions, users, tenants, environment and release set on every trace. OpenInference auto-instrumentation **or** manual spans, not both for the same call (no double counting). |
| **Cost** | Cost attributed on every generation from a pinned price table with `litellm.model_cost` as the live source; roll-ups by tenant, feature, user (hashed), model and prompt version; cost per resolved session as the headline; showback table (Project 1) reproducible from the console. |
| **Cost controls** | Prompt caching with a stable prefix and `prompt_cache_key`; context diet (history trim + tool-result truncation); small-model-first routing with escalation rules; per-tenant budgets with soft cap (degrade), hard cap (refuse politely) and EWMA anomaly; all measured before/after on the same replayed day. |
| **Latency and reliability** | TTFT, TPOT, p50/p95/p99 per tenant and per step from spans and as Prometheus histograms; per-call timeouts, bounded retries with jitter, idempotent `create_ticket`, Router fallbacks and cooldowns; p95 under 4 s during `slow_provider`. |
| **Quality** | Sampling policy (tail for investigation, uniform for measurement); online judge with three criteria writing Langfuse scores; feedback endpoint and correlation; weekly drift report with PSI; worst traces promoted to a dataset with `source_trace_id`. |
| **Dashboards and alerts** | `/metrics` with low-cardinality labels; Grafana Atlas Ops dashboard with tenant variable and release annotations; Langfuse saved views by tag; at least three alert rules (tool error spike, cost anomaly, burn rate) each with a runbook. |
| **Privacy and governance** | SDK-side masking (`mask=`) plus collector-side redaction; hashed user ids; retention and environment separation documented; a telemetry governance checklist filled in. |
| **Deployment** | Collector with tail sampling and two exporters; self-hosted Langfuse via Compose (or Cloud with a documented reason); Atlas keeps serving when the backend is down; CI with unit, integration, budget gate (always) and live evals (with secrets). |
| **Ops Console** | Streamlit pages: Overview, Cost, Latency, Quality, Budgets, Incidents, Trace explorer, reading from the local store and/or Langfuse. |
| **Weekly report** | Your own `weekly_report()` producing a one-page Markdown: cost (with week-on-week), quality, latency, incidents, budget status, three recommendations. |
| **Incidents** | All five scenarios run through the full stack with evidence that each was detected (alert or drift) and contained (budget, step limit, breaker or rollback), plus a two-paragraph note per scenario. |

---

## Architecture

```mermaid
flowchart LR
    users((Employees<br/>4 tenants)) -->|HTTP + tenant/user/session headers| api
    swarm[Swarm / replay<br/>simulator] -->|deterministic day<br/>+ scenarios| api

    subgraph atlas["Atlas service (FastAPI)"]
        api[/chat  /feedback<br/>/metrics  /healthz]
        agent[AtlasAgent loop<br/>step spans, step limit<br/>guardrail]
        tools[Tools: search_knowledge_base<br/>lookup_ticket, create_ticket<br/>reset_password, check_shipment]
        router[LiteLLM Router<br/>mini → nano fallback<br/>gpt-4.1 escalation<br/>timeouts, retries, breaker]
        budget[BudgetGuard<br/>soft/hard caps, EWMA]
        diet[Context diet +<br/>prompt cache key]
        mask[PII mask]
        api --> agent --> tools
        agent --> diet --> router
        agent --> budget
        agent --> mask
    end

    router -->|OpenAI API<br/>or mock LLM| llm[(LLM provider)]
    mask -->|OTLP, GenAI semconv| col[OTel Collector<br/>redact, tail sample]
    api -->|Prometheus scrape| prom[Prometheus]
    col --> lf[Langfuse<br/>traces, sessions, scores,<br/>prompts, datasets]
    col --> file[(spans.jsonl /<br/>SQLite local store)]
    prom --> graf[Grafana<br/>Atlas Ops + alerts]
    graf -->|alert + runbook| oncall((On-call))
    lf --> judge[Online judge<br/>DeepEval G-Eval]
    judge -->|scores| lf
    lf --> drift[Drift report]
    file --> console[Ops Console<br/>Streamlit]
    lf --> console
    console --> report[Weekly ops report]
    ci[GitHub Actions<br/>unit → integration → budget gate → live evals] -.->|blocks merge| atlas
```

ASCII version (for READMEs that do not render Mermaid):

```text
 Employees (4 tenants) ──HTTP──┐                       ┌── OpenAI API / mock LLM
 Swarm / replay (scenarios) ───┤                       │
                               v                       │
 ┌──────────────── Atlas service (FastAPI) ────────────┼───────────────────────┐
 │  /chat /feedback /metrics /healthz                  │                       │
 │  AtlasAgent loop ── context diet + cache key ── LiteLLM Router ────────────┘│
 │     │  step spans, step limit, guardrail            (mini→nano fallback,     │
 │     ├── Tools: search_kb, lookup_ticket, create_ticket,  gpt-4.1 escalation, │
 │     │          reset_password, check_shipment            timeouts, breaker)  │
 │     ├── BudgetGuard (soft/hard caps, EWMA anomaly)                           │
 │     └── PII mask ──OTLP (GenAI semconv)──┐        Prometheus scrape ─────────┼──┐
 └──────────────────────────────────────────┼──────────────────────────────────┘  │
                                            v                                     v
                              OTel Collector (redact, tail sample)          Prometheus
                                 │                    │                          │
                                 v                    v                          v
                         Langfuse (traces,     spans.jsonl / SQLite        Grafana: Atlas Ops
                         sessions, scores,        local store             + alert rules ── runbook ── on-call
                         prompts, datasets)           │
                            │      ^                  │
                            v      │                  v
                    Online judge ──┘           Ops Console (Streamlit) ──> Weekly ops report
                    Drift report ────────────────────^
 GitHub Actions: unit → integration → budget gate (always) → live evals (secrets) ──blocks merge──> Atlas
```

Your submission must include your own version of this diagram, updated to show what you actually built.

---

## Acceptance tests (24)

Each test states its layer: **U** unit, **I** integration (offline, in-memory exporter), **R** replay (offline day through the full stack), **E** eval, **M** manual with recorded evidence. At least 15 must pass for a passing grade; at least 20 for "Excellent" in the evidence criterion. Automate every U, I, R and E test.

| ID | Area | Given / When / Then | Layer |
|---|---|---|---|
| AT-01 | Trace shape | When any request is served, one trace contains an agent span, step spans, generation spans and tool spans, all in one tree, with `gen_ai.agent.name=atlas` on the root | I |
| AT-02 | GenAI attributes | Every generation carries `gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` and, when present, `gen_ai.usage.cache_read_input_tokens`; every tool span carries `gen_ai.tool.name` and `gen_ai.tool.call.arguments` | I |
| AT-03 | No double counting | With OpenInference enabled, exactly one generation span exists per model call | I |
| AT-04 | Session and identity | Two requests with the same `X-Session-Id` land in one Langfuse session; `user_id` is a hash, never the raw employee id | I + M |
| AT-05 | Guardrail | A prompt-injection message produces a `guardrail` observation with a boolean score and the agent refuses without calling a tool | I |
| AT-06 | Redaction | A tool result containing an email, a phone and an employee id reaches the exporter with all three masked; the collector's file export shows the same | I + M |
| AT-07 | Cost per generation | For a generation with 1,200 input (900 cached) and 180 output tokens on gpt-4.1-mini, the span cost is $0.000498 ± 1e-6 | U |
| AT-08 | Escalation priced | An escalated request shows a gpt-4.1 generation whose cost is computed at gpt-4.1 prices (about 5× mini for the same tokens) | I |
| AT-09 | Roll-ups | Over the replayed baseline day, tenant shares sum to 100% ± 0.1 and cost per resolved session ≥ cost per session for every tenant | R |
| AT-10 | Caching saves | Replaying the day with `ATLAS_PROMPT_CACHE=1` vs `0` reduces input-token cost by at least 30% with identical outputs | R |
| AT-11 | Context diet | With `ATLAS_CONTEXT_DIET=1`, no generation's input exceeds `history_token_budget + tool schema + system` and mean tokens per step falls by at least 20% vs diet off | R |
| AT-12 | Routing | With `ATLAS_ROUTER_MODE=1`, at most 10% of generations use gpt-4.1 on the baseline day and the judge `resolved` score drops by at most 0.02 | R + E |
| AT-13 | Soft cap | When a tenant's rolling spend passes the soft cap, requests are served by the degraded model and `atlas_budget_decisions_total{decision="degrade"}` increments | U + R |
| AT-14 | Hard cap | When a tenant passes the hard cap, `/chat` returns a polite refusal (HTTP 200 with `stopped_reason="budget"`), makes **no** LLM call, and the counter for `refuse` increments | I |
| AT-15 | Anomaly | On the `context_bloat` day, the EWMA detector flags the affected tenant within 2 hours of onset and the cost anomaly alert fires | R + M |
| AT-16 | Loop contained | On the `loop` day, no request exceeds `max_steps`, every stopped request has a `step_limit_reached` event, and the loop day costs at most 1.5× baseline | R |
| AT-17 | Retry storm | On the `retry_storm` day, no session creates duplicate tickets (idempotency), retries per request ≤ `max_retries`, and the tool error spike alert fires | R + M |
| AT-18 | Slow provider | On the `slow_provider` day, p95 ≤ 4,000 ms, error rate ≤ 2%, fallbacks occur, and cost per session ≤ $0.05 | R |
| AT-19 | Prompt regression | On the `prompt_regression` week, the drift report flags `grounded` (PSI ≥ 0.1) and the by-prompt-version table isolates v2; rolling the `production` label back to v1 restores scores in a re-replay | R + E |
| AT-20 | Judge cost | The judge's own cost is recorded and reported as a percentage of serving cost, and tail sampling keeps 100% of error traces at ≤ 30% of judge calls | E |
| AT-21 | Metrics cardinality | `/metrics` exposes no label named `user_id`, `session_id`, `trace_id` or `employee_id`, and `atlas_request_duration_seconds` has ≤ 40 series | U |
| AT-22 | Alerts and runbooks | Three alert rules exist, each with a `runbook_url` that resolves to a file in the repo, and each has been seen `FIRING` in a recorded replay | M |
| AT-23 | Backend chaos | With Langfuse (or the collector) stopped for 5 minutes under 2 RPS, Atlas p95 changes by less than 10% and `/healthz` stays green; dropped-span count is reported | M |
| AT-24 | CI gate | A PR that sets `ATLAS_TOP_K=12` fails the budget gate with a comment showing cost per session over budget; the revert passes; the deployed commit has a green run | M |

---

## Deliverables

| # | Deliverable |
|---|---|
| D1 | Repository with instrumented Atlas, `console/`, `deploy/`, `evals/`, tests, CI workflow, alert rules and runbooks, and a README based on the portfolio template below |
| D2 | `ACCEPTANCE.md`: the 24 tests with PASS/FAIL, evidence links (test names, screenshots, replay labels) and notes |
| D3 | `REPORT-week.md`: the weekly ops report for the baseline week, produced by your own report function |
| D4 | `INCIDENTS.md`: five scenario notes (detection, containment, evidence) |
| D5 | Screen recording (4 to 6 minutes) or 8 to 12 screenshots: a trace in Langfuse, the Grafana dashboard under a scenario, an alert firing, the Ops Console Quality and Budgets pages, a CI gate failing and passing |
| D6 | Architecture diagram of what you built |
| D7 | `DIFF_NOTES.md` written after watching the reference solution |
| D8 | Portfolio write-up (README section and optional LinkedIn post) |

---

## Grading rubric (100 points)

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Instrumentation** (15) | 14-15: Complete trace shape, GenAI attributes, Langfuse types, sessions/users/tenants/releases, no double counting, redaction proven | 9-13: One element missing (e.g. guardrail type or release) or a leak in one attribute | 0-8: Flat traces, missing usage, raw PII |
| **Cost engineering** (20) | 18-20: Correct pricing incl. cached and escalation, roll-ups, cost per resolved session, all three savings measured before/after, budgets with degrade/refuse/anomaly working | 12-17: Pricing right, one control missing or unmeasured | 0-11: Costs wrong or no controls |
| **Reliability** (10) | 9-10: p95 under budget during `slow_provider` with errors ≤ 2%, idempotent tools, breaker behaviour explained | 6-8: Budget met by raising timeouts or falling back to the expensive model | 0-5: p95 breach or retry storm uncontained |
| **Quality in production** (15) | 14-15: Sampling policy justified, judge with three criteria and its cost reported, feedback correlation, drift report isolates prompt v2, dataset promotion | 9-13: Judge and drift present, no feedback or no dataset loop | 0-8: No online evaluation |
| **Dashboards, alerts, runbooks** (10) | 9-10: Dashboard per SLI with tenant variable and release annotations, three alerts seen firing, runbooks answer the first five minutes | 6-8: Dashboard and one alert | 0-5: No alerts or alerts without runbooks |
| **Deployment and gate** (10) | 9-10: Collector with sampling and redaction, self-hosted or documented Cloud choice, backend chaos survived, CI gate blocks a regression | 6-8: Stack runs, gate exists but chaos or collector missing | 0-5: No CI gate |
| **Evidence** (10) | 9-10: ≥ 20 of 24 acceptance tests pass with evidence; all automatable ones automated | 6-8: 15 to 19 pass | 0-5: Fewer than 15 |
| **Report and write-up** (10) | 9-10: Weekly report forwardable as-is, honest trade-offs, thoughtful `DIFF_NOTES.md`, gate respected | 6-8: Report present but needs editing, or diff notes thin | 0-5: No report or write-up |

**Pass mark:** 70/100. **Distinction:** 90/100 and at least 22 acceptance tests passing.

---

## Hints

1. Day 1 is an audit, not a rewrite. Run the baseline replay, open five traces, and list what is missing against AT-01 to AT-06 before touching code.
2. Measure every cost control on the **same seed**. "Caching saved 34%" means nothing without "on replay seed 42, prompt v1, diet off".
3. Put the hard cap check **before** the LLM call and test that the mock records zero calls (AT-14). The most common bug is refusing *after* paying.
4. The `slow_provider` tuning from Lab 4 is a starting point, not the answer; your router config also has to survive `retry_storm` without exploding cost. Run both.
5. Tail sampling and the judge sampling policy are different decisions. Keep 100% of errors for investigation; measure quality on the uniform slice; say so on the Quality page.
6. Write the three alert rules with ratio, minimum-traffic guard, `for` and `runbook_url` (Lab 6). Then make each fire with a scenario and screenshot it; that is AT-22.
7. For AT-23, stop the collector rather than Langfuse if you want the harder version: Atlas's own exporter queue is smaller than the collector's.
8. Write the weekly report last, from the console's numbers, and read it as Amara would: two minutes, no jargon, three recommendations with dollars.
9. Decide your targets before measuring and write them in `ACCEPTANCE.md`. Moving targets after the fact is the first thing a reviewer notices.

---

## Portfolio write-up template

Copy this into your repository README (lecture 14.5).

```markdown
# Atlas Ops: observability and cost control for an LLM helpdesk agent

> Production-grade tracing, cost attribution, budgets, online evaluation, dashboards,
> alerting and CI budget gates for a tool-using agent serving four internal tenants.
> Built with Python, OpenTelemetry (GenAI semantic conventions), Langfuse 4, LiteLLM,
> Prometheus and Grafana; deployed with Docker Compose.

**Demo:** [link]  ·  **Dashboard screenshots:** [link]  ·  **Weekly report sample:** [REPORT-week.md](REPORT-week.md)

## What it does
- [3 to 5 bullets written for an engineering manager]

## Architecture
[diagram image or Mermaid block]
[2 to 3 sentences: why OTel + Langfuse + Prometheus, what is portable and what is not]

## Results (replayed baseline week, seed 42)
| Metric | Before | After | Target |
|---|---|---|---|
| Cost per resolved session | $___ | $___ | ≤ $0.05 |
| Weekly cost | $___ | $___ | -40% (Challenge 6.8) |
| Cache hit ratio | ___% | ___% | ≥ 60% |
| p95 latency (slow_provider day) | ___ ms | ___ ms | ≤ 4,000 ms |
| Judge resolved / grounded | ___ / ___ | ___ / ___ | no more than -0.02 |
| Judge cost as % of serving | ___% | ___% | ≤ 2% |

## Failure modes handled
| Scenario | Detected by | Contained by | Evidence |
|---|---|---|---|
| loop | | | |
| context_bloat | | | |
| retry_storm | | | |
| slow_provider | | | |
| prompt_regression | | | |

## How I tested it
| Layer | Tests | What they catch |
|---|---|---|
| Unit | N | pricing, budgets, sampling, drift, PII, latency maths |
| Integration | N | trace shape, attributes, redaction, hard cap without an LLM call |
| Replay | N | budget gate, savings, scenario containment |
| Evals | N | judge, drift, dataset promotion |
Acceptance: X/24 passing ([ACCEPTANCE.md](ACCEPTANCE.md)). CI: [badge]

## Decisions and trade-offs
- [Decision 1: what you chose, the alternative, and the evidence]
- [Decision 2]
- [Something that did not work and what you learned]

## What I would do next
- [2 to 3 items: e.g. per-user budgets, semantic caching, a second backend via the collector]

## Run it yourself
[setup commands: make install, OFFLINE=1 make replay, make console, docker compose ...]

*Built as the capstone of "AI Agent Observability & Cost Control: LLMOps in Production".*
```

Optional LinkedIn post (keep it under 150 words):

```text
I built the operations layer for an LLM helpdesk agent serving four departments.

Every request is traced with OpenTelemetry's GenAI conventions into Langfuse, priced to the
token (cached tokens included), rolled up per department and per resolved session, and
guarded by per-tenant budgets that degrade, then refuse, then page.

On a replayed week of traffic, prompt caching, a context diet and small-model-first routing
cut cost by [X]% with a [Y] change in judge scores, and the stack held p95 under 4 seconds
through a simulated provider outage. Five failure modes (runaway loop, context bloat, retry
storm, slow provider, silent prompt regression) are each detected and contained, with a
CI gate that blocks pull requests that regress cost or latency.

Biggest lesson: [one sentence].

Code and dashboards: [link]
```

---

## Submission (Udemy assignment)

Submit through the **Capstone: The Atlas Ops Console** assignment in lecture 14.5. The full Udemy entry, including the instructor's example answers, is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste links to your repository, `ACCEPTANCE.md` and `REPORT-week.md`. How many of the 24 acceptance tests pass, and did you complete the one-week build before watching the reference solution (yes / partly / no)?
2. Pick one of the five scenarios. Show how your stack detected it (which signal, how long after onset) and how it was contained (which control), with the evidence.
3. Paste the "Decisions and trade-offs" section of your README, and one item from `DIFF_NOTES.md` where the reference solution changed your mind (or where you kept your own approach, and why).

---

## Peer-review checklist

- [ ] A real trace (Langfuse or Ops Console) shows agent, step, generation, tool and retriever spans with usage and cost on the generation.
- [ ] Cached tokens are priced at the cached rate and the escalation model at its own rate (look for the test, not just the claim).
- [ ] Cost per resolved session is the headline number and is explained.
- [ ] Each cost saving is measured before/after on the same seed.
- [ ] The hard cap refuses **without** an LLM call (there is a test).
- [ ] p95 under 4 s during `slow_provider` was achieved without falling back to the expensive model.
- [ ] The judge's cost is reported; headline quality comes from the uniform slice.
- [ ] Three alerts with runbooks, each seen firing.
- [ ] The CI gate is shown failing and passing.
- [ ] `ACCEPTANCE.md` shows at least 15 of 24 passing with evidence links.
- [ ] The weekly report could be forwarded to finance without editing.
- [ ] No raw employee ids or emails anywhere in traces, metrics or the report.
- [ ] `DIFF_NOTES.md` exists and shows real reflection.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______

---

## Domain swap (lecture 14.6): observe a different agent

**Goal:** prove the stack is not Atlas-specific by instrumenting a different agent with the same telemetry, cost and quality layers, and adapting the SLIs to that domain. Udemy assignment; 6 to 10 hours.

### Choose one

| Option | Agent | Notes |
|---|---|---|
| A | **Riley**, the voice receptionist from *Production Voice AI Agents* (Course 3) | Adds per-minute telephony and TTS/STT costs on top of LLM tokens; SLIs become voice-to-voice p95 and cost per call minute |
| B | **Your own agent** (work or side project; any framework, any provider) | Must make at least one LLM call and one tool call per request and be runnable offline with a stub, or you cannot replay incidents |
| C | A **coding or data agent** (an open-source agent that runs tools in a sandbox) | Long tool results and many steps: the context diet and step limits matter most |

### What must carry over unchanged

1. OpenTelemetry spans with GenAI semantic conventions for LLM, tool and agent operations, exported to Langfuse (or another OTel backend) with sessions, users and a tenant-like dimension.
2. Cost attributed per generation from a pinned price table, rolled up by at least two dimensions, with the domain's "cost per resolved unit" as the headline (per resolved session, per call minute, per merged PR...).
3. One budget with a hard cap that refuses before spending, and one anomaly detector.
4. Prometheus metrics with low-cardinality labels and one alert with a runbook.
5. A sampled online judge with at least two domain-specific criteria and its own cost reported.
6. One injected failure (choose from loop, context bloat, retry storm, slow provider, prompt regression, or a domain-specific one) detected and contained with evidence.

### What must change (and this is the point)

Use `10-resources/instrumentation-template.md` to document:

- **SLIs**: which of task success, containment, tool error rate, p95, cost per resolved unit and judge score still apply, which do not, and what replaces them (voice: TTFT becomes time to first audio; coding agent: tests-passed rate).
- **Budgets**: what the unit of spend is and what "degrade" means in this domain (voice: switch to a cheaper TTS voice; coding agent: smaller model for file reads).
- **Privacy**: what PII the domain adds (voice: phone numbers, recordings; coding agent: source code, secrets in tool output) and how the mask changed.
- **Judge criteria**: two criteria that would be meaningless for Atlas and essential here.

### Deliverables

| # | Deliverable |
|---|---|
| 1 | Repository or folder with the instrumented agent and a README using the instrumentation template |
| 2 | One trace screenshot with the GenAI attributes visible, one cost roll-up table, one dashboard or Ops Console screenshot with the adapted SLIs |
| 3 | `INCIDENT.md`: the injected failure, detection, containment, evidence |
| 4 | A half-page "what changed and what did not" reflection |

### Self-check rubric (out of 20; pass at 14)

| Criterion | Points |
|---|---|
| GenAI-convention spans with sessions/users/tenant, viewable in a backend | 4 |
| Cost per generation and a domain-correct headline unit | 4 |
| Hard cap refuses before spending; anomaly detector present | 3 |
| Metrics with low-cardinality labels; one alert with runbook | 3 |
| Judge with two domain-specific criteria and its cost reported | 3 |
| Injected failure detected and contained with evidence | 3 |

Submit through the **Domain swap: observe a different agent** assignment in lecture 14.6 (entry in `06-assessments/assignments.md`).
