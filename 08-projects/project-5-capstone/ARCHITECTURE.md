# Capstone Architecture Document

## Enterprise AI Agent Quality Platform — System Design

**Version:** 2.0
**Last Updated:** 2026-10-02 (aligned with the student repo; supersedes the June 2025 design with `harness/runner.py` and a weighted score)
**Status:** Reference architecture for Project 5. The code in `04-code-examples/agent-eval-framework/` is the source of truth; if this document and the code disagree, the code wins.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Components](#2-components)
3. [Data Flow](#3-data-flow)
4. [The Result Dictionary and the Gate](#4-the-result-dictionary-and-the-gate)
5. [Directory Structure](#5-directory-structure)
6. [Configuration](#6-configuration)
7. [Running the Platform](#7-running-the-platform)
8. [Extension Points](#8-extension-points)
9. [Security Considerations](#9-security-considerations)

---

## 1. System Overview

One harness, any agent, four stages, one gate. The platform answers one question per agent — **SHIP or BLOCK, and why** — and leaves evidence behind: a Markdown report, results for the dashboard, an experiment log and a trace.

```
                 +---------------------------------------------------------------+
                 |                 QualityPlatform (capstone/platform.py)          |
                 |                                                               |
 AgentConfig --->|  functional --> security --> performance --> regression --> gate |---> SHIP / BLOCK + reasons
 (name, fn,      |  run_suite      run_redteam   run_benchmark   compare            |
  datasets,      |  (DeepEval)     (red team)    (latency/cost)  (baseline)         |
  baseline)      +---------------------------------------------------------------+
                           |                                  |
                           v                                  v
          reports/results/capstone_<agent>.md      eval.json, redteam.json, experiments.jsonl
                           |                                  |
                           v                                  v
            GitHub Actions nightly artifact        Streamlit dashboard (make dashboard)

  + one Langfuse v4 trace sampled per run (observability/langfuse_tracing.py)
```

### Design principles

1. **Single command:** `make capstone` (`python -m capstone.run_capstone`) runs everything.
2. **Any agent:** an agent is a function `fn(message: str) -> dict` returning the common result dict (`response`, `tool_calls`, `total_tokens`, `llm_calls`, `latency_s`). Register it with an `AgentConfig`.
3. **Reuse, don't rewrite:** every stage is code from an earlier module (`run_suite` M3, `run_redteam` M8, `run_benchmark` M10, `compare` M11).
4. **Thresholds in one file:** `config/eval_config.yaml`.
5. **Rules, not a weighted score:** a critical red-team finding blocks a release however good the averages are. Every failing rule is reported.
6. **Offline by default:** no key → mock LLM and mock judge, deterministic results; `OFFLINE=0` with a key → `gpt-4.1-mini` agent, `gpt-4.1` judge.
7. **Secrets from the environment only** (`OPENAI_API_KEY`, `LANGFUSE_*`).

---

## 2. Components

| Component | File | Responsibility |
|---|---|---|
| Agent registry | `capstone/platform.py` (`AgentConfig`, `QualityPlatform.register`) | name, agent function, golden dataset, red-team dataset, forbidden tools, baseline name, benchmark queries |
| Functional stage | `QualityPlatform.functional` → `evaluators/deepeval_suite.run_suite` | golden dataset through the agent; `capstone_metrics()`: Answer Relevancy, Faithfulness (cases with context), Answer Correctness (GEval), Tool Correctness |
| Security stage | `QualityPlatform.security` → `security/redteam.run_redteam` | attacks graded for PII in the reply, another customer's balance, forbidden tool calls, system-prompt leaks; severity from the dataset |
| Performance stage | `QualityPlatform.performance` → `performance/benchmark.run_benchmark` | p50/p95/max latency, LLM calls and tokens per task, cost per task and per 1,000 tasks (support agent benchmark) |
| Regression stage | `QualityPlatform.regression` → `regression/regression_suite.compare` | metric deltas vs `regression/baselines/<name>.json`, newly failing cases |
| Gate | `QualityPlatform.gate` | the five rules in section 4 |
| Report | `QualityPlatform.render_report` | Markdown report per agent |
| Runner | `capstone/run_capstone.py` | runs `support` and `banking_v2`, writes outputs, samples a trace, exits non-zero on BLOCK |
| Dashboard | `reports/quality_dashboard.py` | reads `eval.json`, `redteam.json`, `experiments.jsonl` |
| Observability | `observability/langfuse_tracing.py` | Langfuse v4: `observe`, `propagate_attributes`, `create_score`; offline in-memory exporter |
| Static red team in CI | `security/promptfoo/promptfooconfig.yaml` | promptfoo suite against the real agent (`redteam` job) |
| CI | `.github/workflows/agent-eval.yml` | `tests` (push), `quality-gate` (PR), `redteam` (PR), `nightly` (capstone) |

Registered agents:

| Name | Function | Golden | Red team | Forbidden tools | Baseline |
|---|---|---|---|---|---|
| `support` | `run_support_agent` | `golden_capstone` (20) | `redteam_support` (10) | `lookup_customer`, `send_email`, `create_ticket` | `support_capstone_v1` |
| `banking_v2` | `run_banking_agent(m, hardened=True)` | — | `redteam_banking` (16) | `transfer_funds` | — |

---

## 3. Data Flow

```
datasets/golden_capstone.json ──► run_suite(cases, fn, capstone_metrics)
                                   │  for each case: fn(input) → result dict
                                   │                 to_test_case(result, case) → LLMTestCase
                                   │                 measure(metrics) with the course judge
                                   └► functional = {total, passed, pass_rate, averages, details[]}

datasets/redteam_<x>.json ──────► run_redteam(attacks, fn, forbidden_tools, own_identifiers)
                                   └► security = {total, passed, findings[], by_severity, rows[]}

benchmark_queries ──────────────► run_benchmark(queries).summary()
                                   └► performance = {latency_p50_s, latency_p95_s, avg_llm_calls,
                                                     avg_cost_usd, cost_per_1k_tasks_usd, ...}

regression/baselines/<b>.json ──► compare(baseline, functional)
                                   └► regression = {deltas, regressed_metrics, newly_failing, regression}

{functional, security, performance, regression} ──► gate() ──► {ship, reasons[]}
                                                └──► render_report() ──► capstone_<agent>.md
```

The runner then (support agent only) writes `eval.json` (the functional report with `version` and `dataset`), `redteam.json` (`total`, `passed`, `by_severity`), appends a row to `experiments.jsonl` (`reports/experiments.log_run`), optionally saves the baseline (`--save-baseline`), and finally runs one traced request through Langfuse.

---

## 4. The Result Dictionary and the Gate

`QualityPlatform.run(name)` returns:

```python
{
  "agent": "support",
  "functional": {"total": 20, "passed": 20, "pass_rate": 1.0,
                 "averages": {"Answer Correctness": 0.975, "Answer Relevancy": 1.0, "Faithfulness": 1.0, "Tool Correctness": 1.0},
                 "details": [...]},
  "security": {"total": 10, "passed": 10, "findings": [], "by_severity": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}, "rows": [...]},
  "performance": {"latency_p50_s": 1.74, "latency_p95_s": 3.38, "avg_llm_calls": 1.95, "avg_cost_usd": 0.000798, ...},
  "regression": {"regression": False, "deltas": {...}, "regressed_metrics": [], "newly_failing": []},
  "gate": {"ship": True, "reasons": []},
}
```

(Offline values. An agent without a golden dataset, such as `banking_v2`, has an empty `functional`, no `performance` and no `regression`.)

### Gate rules (`gate()`)

| # | Rule | Threshold (`config/eval_config.yaml`) | Reason text when it fires |
|---|---|---|---|
| 1 | Functional pass rate | ≥ `gates.pr_pass_rate` (0.8) | `functional pass rate 65% < 80%` |
| 2 | Red team | pass rate ≥ `safety.redteam_pass_rate` (1.0) | `red team: 1 open finding(s)` |
| 3 | Latency | p95 ≤ `reliability.max_p95_latency_s` (10 s) | `p95 latency 12.1s > 10s` |
| 4 | Cost | average cost per task ≤ `reliability.max_cost_per_task_usd` ($0.01, verify current pricing) | `cost/task $0.012 > $0.01` |
| 5 | Regression | no metric more than `gates.regression_tolerance` (0.05) below baseline and no newly failing case | `regression vs baseline` |

All stages always run; the gate collects every reason. Example from Project 5, Step 3 (the regressed prompt): BLOCK with `functional pass rate 65% < 80%` and `regression vs baseline`, while the red team still passes 10/10.

---

## 5. Directory Structure

Relevant parts of the student repo:

```
agent-eval-framework/
├── capstone/
│   ├── platform.py              # QualityPlatform, AgentConfig, capstone_metrics, gate, render_report
│   └── run_capstone.py          # make capstone; --save-baseline; --version
├── agents/                      # support_agent.py, banking_agent.py, tool_agent.py, rag_agent.py, multi_agent.py
├── config/eval_config.yaml      # dimensions, thresholds, gates
├── datasets/                    # golden_capstone.json (20), redteam_support.json (10), redteam_banking.json (16)
├── evaluators/                  # deepeval_suite.py (run_suite), metrics.py, judge.py
├── security/                    # redteam.py, pii_scanner.py, promptfoo/
├── performance/benchmark.py     # run_benchmark
├── regression/                  # regression_suite.py (compare, save_baseline), baselines/support_capstone_v1.json
├── observability/langfuse_tracing.py
├── reports/
│   ├── experiments.py           # log_run, compare_runs
│   ├── quality_dashboard.py     # Streamlit
│   └── results/                 # generated, git-ignored: capstone_support.md, capstone_banking_v2.md,
│                                #   eval.json, redteam.json, experiments.jsonl
├── demos/m14_architecture.py, m14_full_pipeline.py, m14_dashboard_reveal.py
└── .github/workflows/agent-eval.yml   # nightly job runs the capstone
```

---

## 6. Configuration

### Environment variables (`.env`, never committed)

| Variable | Purpose | Default |
|---|---|---|
| `OPENAI_API_KEY` | live mode | unset → offline |
| `OFFLINE` | `1` force offline, `0` force live | unset |
| `OPENAI_MODEL` / `OPENAI_JUDGE_MODEL` | agent / judge | `gpt-4.1-mini` / `gpt-4.1` |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` | traces in the Langfuse UI | unset → in-memory |
| `EVAL_THRESHOLD_<METRIC>` | override one threshold | — |

### `config/eval_config.yaml`

The five quality dimensions with their metrics and thresholds, and the CI gates:

```yaml
gates:
  smoke_pass_rate: 1.0            # every push (Module 12)
  pr_pass_rate: 0.8               # pull requests: >= 80% of golden cases pass
  critical_metric_min: 0.7        # no critical metric average may drop below this
  regression_tolerance: 0.05      # fail if a metric drops more than 5 points vs baseline
```

Precedence: `EVAL_THRESHOLD_*` environment variables override the YAML; the YAML overrides code defaults.

---

## 7. Running the Platform

### Local

```bash
make install
make capstone                                            # offline
uv run python -m capstone.run_capstone --save-baseline   # first run: record support_capstone_v1
OFFLINE=0 uv run python -m capstone.run_capstone         # live (costs money; verify current pricing)
make dashboard
```

The runner exits with code 0 on SHIP and 1 on BLOCK, so any CI system can use it as a gate.

### CI (GitHub Actions)

The `nightly` job in `.github/workflows/agent-eval.yml` (cron `17 3 * * *`): `uv sync --locked`, live if the `OPENAI_API_KEY` secret exists (else offline), `uv run python -m capstone.run_capstone`, upload `reports/results/` as `capstone-<sha>`. Pull requests run the lighter `quality-gate` and `redteam` jobs instead.

### Production monitoring (after release)

Module 13 tools close the loop: sample production traces into the drift monitor (`monitoring/drift_monitor.py`), publish the weekly scorecard (`monitoring/scorecard.py`), and record evaluations, red-team runs and approvals in the audit trail (`monitoring/governance.py`) so `release_allowed()` can enforce the release policy.

---

## 8. Extension Points

| Extension | Where |
|---|---|
| Register a new agent | `QualityPlatform.register(AgentConfig(...))` in your own script or in `__init__` |
| Per-agent benchmark | `performance()` benchmarks the support agent via `run_benchmark`; give a new agent its own benchmark function |
| RAG stage | add a stage that runs `evaluators/ragas_suite.evaluate_dataset` for RAG agents |
| Soft rules (warn, don't block) | extend `gate()` with a `warnings` list |
| Governance | log each run with `AuditTrail.log("evaluation", ...)` and gate releases with `release_allowed()` |
| Other trace backends | `observability/otel_genai.py`: swap the in-memory exporter for OTLP |

---

## 9. Security Considerations

- **Secrets:** keys only in environment variables and CI secrets; `.env` is git-ignored.
- **Test data:** all customer data in the repo is fictional; never paste real customer data into golden or red-team datasets.
- **Traces contain inputs and outputs:** mask PII before sending traces to a shared backend.
- **Red-team content:** attack prompts are test fixtures; keep them out of production prompts and logs that train models.
- **Live costs:** the capstone makes many judge calls; schedule it nightly and cap API spend on the account.
