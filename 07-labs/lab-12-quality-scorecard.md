# Lab 13.1: Agent Quality Scorecard and Governance Record

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 13.1 (file `lab-12-quality-scorecard.md`) |
| **Module** | Module 13 — Production Monitoring & Governance |
| **Lectures** | 13.1–13.3 |
| **Duration** | 90 minutes |
| **Difficulty** | Advanced |
| **Learning Objective** | Build a one-page leadership scorecard on the five quality dimensions with traffic lights and trend arrows, detect drift in four weeks of production scores, and record a release in a hash-chained audit trail so the governance policy allows it. |
| **Reference solution** | `monitoring/scorecard.py`, `monitoring/drift_monitor.py`, `monitoring/governance.py`, `demos/m13_*.py` |
| **Verified on** | Python 3.11 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Labs 1.1–12.1**, or at least Lab 3.1 (golden-dataset scores) and Lab 12.1 (the gate)
- Lectures 13.1–13.3: drift, governance, scorecards

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
uv run python demos/m13_quality_scorecard.py
uv run python demos/m13_drift_detection.py
uv run python demos/m13_governance_audit.py
```

The building blocks:

| File | What it gives you |
|---|---|
| `monitoring/scorecard.py` | `build_scorecard(agents, week)`, `render_markdown(card)`; targets per dimension: correctness 0.85, faithfulness 0.85, relevance 0.80, safety 0.95, reliability 0.90; GREEN on target, AMBER within 5 points, RED below |
| `monitoring/drift_monitor.py` | `DriftMonitor` (7-day rolling average; alerts when it crosses the `eval_config.yaml` threshold or drops 5 points below the launch baseline), `simulate_weeks()` |
| `monitoring/governance.py` | `AuditTrail` (append-only JSONL, each record hashes the previous one), `release_allowed(trail, version)` with `DEFAULT_POLICY` (pass rate ≥ 0.8, Faithfulness ≥ 0.8, Answer Relevancy ≥ 0.7, a clean red-team run, approvals from "QA lead" and "Product owner") |

---

## Step-by-Step Instructions

### Step 1 — Your agent's numbers

Collect this week's and last week's score for each of the five dimensions (T3) for the agent you evaluated in a project. Map your metrics to dimensions with `config/eval_config.yaml`:

| Dimension | From |
|---|---|
| Correctness | Answer Correctness (GEval), Tool Correctness |
| Faithfulness | Faithfulness |
| Relevance | Answer Relevancy |
| Safety | red-team pass rate, PII Safety |
| Reliability | consistency, failure rate (latency and cost sit here too) |

Also record cost per task (Lab 10.1), tasks per week (estimate) and escalation rate.

### Step 2 — Build the scorecard

Create `my_work/lab12_scorecard.py`:

```python
"""Lab 13.1 - a leadership scorecard, a drift check and a release record."""
from pathlib import Path

from monitoring.drift_monitor import monitor_from_rows, simulate_weeks
from monitoring.governance import AuditTrail, release_allowed
from monitoring.scorecard import EXAMPLE_AGENTS, build_scorecard, render_markdown

my_agent = {"name": "My Project Agent", "tasks_per_week": 2000, "cost_per_task_usd": 0.0009, "escalation_rate": 0.04,
            "this_week": {"correctness": 0.98, "faithfulness": 1.00, "relevance": 1.00, "safety": 1.00, "reliability": 0.95},
            "last_week": {"correctness": 0.96, "faithfulness": 1.00, "relevance": 0.99, "safety": 1.00, "reliability": 0.95}}
print(render_markdown(build_scorecard(EXAMPLE_AGENTS[:1] + [my_agent], week="2026-09-28")))
```

Replace the numbers with yours. The `EXAMPLE_AGENTS` row is illustrative; keep it only as a comparison.

### Step 3 — Check for drift

Add:

```python
alerts = monitor_from_rows(simulate_weeks()).check()        # SIMULATED data, seed 7
print("\n".join(str(a) for a in alerts))
```

The data is simulated: faithfulness slowly degrades from day 15. Which alert fires first, the baseline drop or the absolute threshold? Why do you want both?

### Step 4 — Record a release

Add:

```python
path = Path("reports/results/lab13_audit.jsonl")
path.unlink(missing_ok=True)
trail = AuditTrail(path)
trail.log("evaluation", "github-actions", "v1.4", {"pass_rate": 1.0, "averages": {"Faithfulness": 1.0, "Answer Relevancy": 1.0}})
trail.log("redteam", "github-actions", "v1.4", {"total": 10, "findings": 0})
trail.log("approval", "qa.lead@techcorp.com", "v1.4", {"role": "QA lead"})
print("release allowed?", release_allowed(trail, "v1.4"))
trail.log("approval", "product.owner@techcorp.com", "v1.4", {"role": "Product owner"})
print("release allowed?", release_allowed(trail, "v1.4"), "chain intact:", trail.verify())
```

```bash
uv run python -m my_work.lab12_scorecard
```

Then open `reports/results/lab13_audit.jsonl`, change one number by hand, and call `AuditTrail(path).verify()` again. What does it return, and why?

### Step 5 — Write the one-pager

In `my_work/lab12_scorecard.md`, paste your scorecard table and add, in plain language for a non-technical reader:

1. **Is it working?** (the overall light)
2. **What's the trend?** (arrows and the drift alert, if any)
3. **What needs attention and who owns it?** (one action per AMBER or RED cell)
4. **What does it cost?** (weekly cost; "verify current pricing")

---

## Expected Output

```
# Agent Quality Scorecard - week of 2026-09-28
| Agent | Overall | Correctness | Faithfulness | Relevance | Safety | Reliability | Cost/task | Weekly cost | Escalations |
|---|---|---|---|---|---|---|---|---|---|
| TechCorp Support | [G] | [G] 0.93 = | [G] 0.91 v | [G] 0.90 = | [G] 0.99 = | [G] 0.95 = | $0.0008 | $28.00 | 6% |
| My Project Agent | [G] | [G] 0.98 ^ | [G] 1.00 = | [G] 1.00 = | [G] 1.00 = | [G] 0.95 = | $0.0009 | $1.80 | 4% |
[G] on target  [A] within 5 points  [R] action needed   ^ improving  v declining  = flat
Costs use list prices (verify current pricing).
[2026-09-24] ALERT faithfulness: 7-day avg 0.851 (baseline_drop, limit 0.862)
[2026-09-28] ALERT faithfulness: 7-day avg 0.798 (threshold, limit 0.800)
[2026-09-28] ALERT task_completion: 7-day avg 0.823 (baseline_drop, limit 0.828)
release allowed? (False, ['missing approval: Product owner'])
release allowed? (True, []) chain intact: True
```

---

## Verification Checklist

- [ ] The scorecard uses the five dimensions (correctness, faithfulness, relevance, safety, reliability) and your own numbers
- [ ] You can explain each traffic light and arrow
- [ ] The drift check names the first alert and its kind
- [ ] The release is blocked until both approvals are logged, then allowed
- [ ] Editing a record by hand makes `verify()` return `False`
- [ ] The one-pager answers the four questions without jargon

---

## Common Pitfalls

1. **Too many numbers.** Leaders need the light, the trend and the action. Keep metric names and decimals for the appendix.
2. **Simulated data presented as real.** Label simulated drift as simulated, on the slide and in the report.
3. **An audit log anyone can edit.** A plain log can be changed silently; the hash chain makes edits detectable. In production, store it where writes are append-only.
4. **Approvals outside the record.** A Slack thumbs-up is not an approval. If it is not in the trail, the policy treats it as missing.

---

## Extension Challenge

1. Feed real scores into the drift monitor: run `make eval-offline` on a few prompt variants on different "days" and record each run with `DriftMonitor.record(day, metric, value)`.
2. Add a policy rule: no release if the scorecard's safety light is RED. Implement it on top of `release_allowed()`.
3. Add the scorecard to the Streamlit dashboard (`reports/quality_dashboard.py`) as a new section.
