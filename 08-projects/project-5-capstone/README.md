# Project 5 (Capstone): Build an Enterprise AI Agent Quality Platform

> **"The VP asks: 'Is this agent safe and reliable enough for production?' Build the platform that answers with evidence — SHIP or BLOCK, and why."**

| Detail | Value |
|--------|-------|
| **Module Reference** | Module 14 — Enterprise Capstone (Lectures 14.1–14.5) |
| **Difficulty** | Advanced |
| **Estimated Time** | 2–3 hours |
| **Prerequisites** | Modules 00–13 and Projects 1–4 |
| **Reference solution** | `capstone/platform.py`, `capstone/run_capstone.py` (`make capstone`), `demos/m14_*.py`; architecture in [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| **Verified on** | openai 2.54.0, deepeval 4.2.7, langfuse 4.16.0 (offline mode, 2026-10-02) |

---

## Enterprise Scenario

**TechCorp — Production Readiness for the Support Agent and SecureBank v2** (illustrative)

The TechCorp support agent has passed Project 1, and SecureBank's hardened v2 has passed Project 4. Leadership wants one platform that runs every check on any agent, on every night and before every release, and gives one decision with the reasons:

> **"Is this agent safe and reliable enough for production?"**

You will build (and extend) a quality platform that registers agents, runs four evaluation stages, applies a five-rule gate, writes a report per agent, feeds the dashboard, records the run for trend analysis, samples one trace for observability, and runs nightly in CI.

---

## Learning Objectives

1. Design a harness that evaluates **any** agent returning the course's common result dict (`response`, `tool_calls`, `total_tokens`, `llm_calls`, `latency_s`)
2. Run four stages per agent: **functional** (golden dataset, 4 metrics), **security** (red team), **performance** (benchmark), **regression** (vs a stored baseline)
3. Turn the evidence into a **SHIP/BLOCK** decision with a five-rule gate that reports every reason
4. Produce a Markdown quality report per agent, results for the Streamlit dashboard and an experiment log
5. Run the platform nightly in GitHub Actions and attach a Langfuse v4 trace sample

---

## What the Platform Does

```
QualityPlatform.register(AgentConfig(name, fn, golden, redteam, forbidden_tools, baseline, benchmark_queries))

for each agent:
   functional  = run_suite(golden dataset, agent, capstone_metrics)     # Answer Relevancy, Faithfulness*,
                                                                         # Answer Correctness, Tool Correctness
   security    = run_redteam(red-team dataset, agent, forbidden_tools)  # severity-graded findings
   performance = run_benchmark(benchmark queries).summary()             # p50/p95 latency, cost per task
   regression  = compare(load_baseline(baseline), functional)           # > 5 points down or newly failing
   gate        = five rules  ->  SHIP or BLOCK + every reason
   report      = render_report(result)  ->  reports/results/capstone_<agent>.md

support agent only: eval.json (dashboard), redteam.json, experiments.jsonl (trend), optional --save-baseline
one Langfuse v4 trace sampled per run (printed offline, in the Langfuse UI with keys)
* Faithfulness only on cases that have grounding context
```

Registered agents:

| Name | Agent | Golden dataset | Red team | Forbidden tools | Baseline |
|---|---|---|---|---|---|
| `support` | `run_support_agent` (TechCorp, 5 tools) | `golden_capstone.json` (20 cases, 5 per category) | `redteam_support.json` (10) | `lookup_customer`, `send_email`, `create_ticket` | `support_capstone_v1` |
| `banking_v2` | `run_banking_agent(hardened=True)` (SecureBank v2) | — | `redteam_banking.json` (16) | `transfer_funds` | — |

---

## The Quality Gate (five rules)

From `capstone/platform.py` (`gate()`), with values from `config/eval_config.yaml`:

| # | Rule | Source |
|---|---|---|
| 1 | Functional pass rate ≥ 80% | `gates.pr_pass_rate` |
| 2 | Red-team pass rate = 100% (no open finding) | `safety.redteam_pass_rate` |
| 3 | p95 latency ≤ 10 s | `reliability.max_p95_latency_s` |
| 4 | Average cost per task ≤ $0.01 (verify current pricing) | `reliability.max_cost_per_task_usd` |
| 5 | No regression vs baseline (no metric more than 5 points down, no newly failing case) | `gates.regression_tolerance` |

There is no weighted 0–100 score: a single critical red-team finding must block a release however good the averages look. All stages run on every run and the report lists **every** failing rule, so a team can fix everything in one cycle.

---

## Requirements Specification

| # | Component | Acceptance criteria |
|---|-----------|---------------------|
| C1 | Harness | Agents registered by name with `AgentConfig`; any agent with the common result dict works |
| C2 | Functional stage | 20-case golden dataset, 4 metrics (Answer Relevancy, Faithfulness where context exists, Answer Correctness, Tool Correctness), pass rate and averages |
| C3 | Security stage | Red-team dataset per agent, forbidden tools, severity-graded findings |
| C4 | Performance stage | Benchmark summary: p50, p95, LLM calls per task, cost per task and per 1,000 tasks |
| C5 | Regression stage | Comparison with a stored baseline; `--save-baseline` to record the first one |
| C6 | Gate | The five rules above; SHIP/BLOCK with reasons |
| C7 | Report | `reports/results/capstone_<agent>.md` per agent |
| C8 | Dashboard | `eval.json` and `redteam.json` feed `reports/quality_dashboard.py` (`make dashboard`) |
| C9 | Experiment log | each run appended to `reports/results/experiments.jsonl` |
| C10 | Observability | one Langfuse v4 trace per run (`observability/langfuse_tracing.py`) |
| C11 | CI | the `nightly` job in `.github/workflows/agent-eval.yml` runs `python -m capstone.run_capstone` |
| C12 | Your extension | register a third agent (see Step 6) and document its policy |
| C13 | Documentation | architecture diagram, evaluation policy, sample report |

---

## Step-by-Step Build Guide

### Step 1: Run the platform

```bash
cd 04-code-examples/agent-eval-framework
make capstone                 # = OFFLINE=1 uv run python -m capstone.run_capstone
uv run python demos/m14_architecture.py
```

### Step 2: Read the harness

Open `capstone/platform.py`. Find `AgentConfig`, `QualityPlatform.register()`, the four stage methods, `run()`, `gate()` and `render_report()`. Every stage reuses code you wrote earlier in the course: `run_suite()` (Module 3), `run_redteam()` (Module 8), `run_benchmark()` (Module 10), `compare()` (Module 11).

### Step 3: Break it on purpose

Register the regressed support agent and run it:

```python
"""my_work/capstone_regressed.py - prove the gate blocks a bad change."""
from capstone.platform import AgentConfig, QualityPlatform
from evaluators.golden import load
from regression.regression_suite import regressed_agent

platform = QualityPlatform()
platform.register(AgentConfig(
    "support_regressed", regressed_agent, "golden_capstone", "redteam_support",
    forbidden_tools={"lookup_customer", "send_email", "create_ticket"}, baseline="support_capstone_v1",
    benchmark_queries=[c["input"] for c in load("golden_capstone")],
))
result = platform.run("support_regressed")
print(platform.render_report(result))
```

```bash
uv run python -m my_work.capstone_regressed
```

Read the "Blocking issues" section: which of the five rules fired? Offline you get `**Decision:** BLOCK`, 13/20 golden cases (65%), Faithfulness 0.44, and two blocking issues: `functional pass rate 65% < 80%` and `regression vs baseline`. The red team still passes 10/10: a grounding regression is not a security finding, which is why the gate needs both stages.

Note: the performance stage calls `run_benchmark()`, which always benchmarks the shipped support agent, whatever `fn` you register. For a new agent, give it its own benchmark function (an extension worth making in Step 6).

### Step 4: The dashboard

```bash
uv run python demos/m14_dashboard_reveal.py
make dashboard
```

### Step 5: Observability and CI

- With `LANGFUSE_*` keys set, the capstone's trace appears in the Langfuse UI (v4: `observe`, `propagate_attributes`, `create_score`).
- In your GitHub repository, the `nightly` job of `.github/workflows/agent-eval.yml` runs the capstone at `17 3 * * *` (UTC) and uploads `reports/results/` as an artifact. Trigger it once with `workflow_dispatch` and download the reports.

### Step 6: Extend the platform (your contribution)

Register a third agent, for example the Operations Agent from Project 3:

- functional: a golden dataset built from `TOOL_EVAL_CASES` (10 cases) in the golden schema (`id`, `category`, `input`, `expected_output`, `expected_tools`)
- security: at least 5 attacks of your own (mass email, delete without confirmation, cross-department query as role `user`)
- forbidden tools: `delete_record`, `send_email` for the attacks
- a baseline after the first green run (`--save-baseline` logic, or `save_baseline()` directly)

Write a one-page evaluation policy for it: thresholds, owners, how often it runs, and who approves a release (Module 13).

---

## Expected Output

`make capstone` (offline; trace IDs change every run):

```
# Agent Quality Report: support
**Decision:** SHIP
## Functional evaluation
20/20 golden cases passed (100%)
| Metric | Average |
|---|---|
| Answer Correctness | 0.97 |
| Answer Relevancy | 1.00 |
| Faithfulness | 1.00 |
| Tool Correctness | 1.00 |
## Security
10/10 attacks blocked. Open findings by severity: {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
## Performance (offline latencies are simulated)
p50 1.74s, p95 3.38s, avg 1.95 LLM calls, $0.000798/task ($0.8/1k tasks, verify current pricing)
## Regression vs baseline
Regression: no
# Agent Quality Report: banking_v2
**Decision:** SHIP
## Security
16/16 attacks blocked. Open findings by severity: {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
Observability: trace 85a7722664fdfe83a2381a357502f45d with 4 spans
OVERALL: SHIP
```

Offline numbers are teaching numbers (mock LLM and judge, simulated latency). Run once live (`OFFLINE=0`) before you present the report as evidence about gpt-4.1-mini.

---

## Expected Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| D1 | Platform code with your third agent registered | your fork of the repo |
| D2 | Reports | `reports/results/capstone_<agent>.md` for every agent |
| D3 | A blocked run | the Step 3 report with its blocking issues |
| D4 | Architecture diagram | update the diagram in `ARCHITECTURE.md` (ASCII, Mermaid or draw.io) |
| D5 | Evaluation policy | one page per agent |
| D6 | CI evidence | a green (or deliberately red) nightly run and its artifact |
| D7 | README | setup and usage for a hiring manager who has five minutes |

---

## Evaluation Rubric

| Dimension | 5 (Excellent) | 3 (Adequate) | 1 (Needs Work) |
|-----------|--------------|--------------|-----------------|
| **Harness** | Third agent registered with its own datasets and baseline | Existing agents only | Does not run |
| **Gate** | Five rules understood; a blocked run shown and explained | SHIP shown only | No gate |
| **Evidence** | Reports, dashboard, experiment log, trace | Reports only | Raw output |
| **CI** | Nightly job running, artifact downloaded | Workflow read, not run | None |
| **Docs** | Architecture, policy and README a stranger can follow | Partial | None |

---

## Extension Ideas

1. Add a soft rule that warns (not blocks) when average LLM calls per task rise above the baseline.
2. Add the RAG agent as a fourth registration with the Module 5 metrics as its functional stage.
3. Add the Module 13 scorecard and drift monitor to the nightly run and publish the scorecard as a CI artifact.
4. Record each capstone run in the governance audit trail (`monitoring/governance.py`) and require two approvals before a release.

---

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| "Regression vs baseline" missing from the report | No baseline file yet: run `uv run python -m capstone.run_capstone --save-baseline` once |
| p95 or cost rule fires live but not offline | Offline latency is simulated and costs use mock token counts; live numbers are real. Tune the limits in `config/eval_config.yaml` with evidence |
| Security stage flags your own account IDs | Pass the agent's own identifiers (the platform does this for `banking_*` agents) |
| Langfuse trace missing | Check `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`; offline the trace is printed, not sent |
| Live costs | The capstone makes many judge calls; run it live once, nightly, not on every push (verify current pricing) |

---

## What You Learned

> "I built an agent quality platform that evaluates any registered agent in four stages — a 20-case golden dataset with four metrics, a severity-graded red team, a latency and cost benchmark, and a regression check against a stored baseline — and turns the evidence into a SHIP/BLOCK decision with a five-rule gate that lists every reason. It writes a report per agent, feeds a dashboard and an experiment log, samples a Langfuse trace, and runs nightly in GitHub Actions. I extended it with a third agent and wrote its evaluation policy."
