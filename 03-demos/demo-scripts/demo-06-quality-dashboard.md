# Demo 06 — Experiment Comparison and the Quality Dashboard

**Used in:** Lecture 12.3 (Experiment Tracking & Quality Dashboards)
**Duration:** ~2 minutes of screen recording
**Purpose:** Compare two agent versions run by run, then show the Streamlit dashboard leadership and the team will actually look at.
**Demo files:** `reports/experiments.py`, `reports/quality_dashboard.py`, `demos/m12_experiment_comparison.py`, `demos/m12_quality_dashboard.py`
**Commands:** `uv run python demos/m12_experiment_comparison.py`; `uv run python demos/m12_quality_dashboard.py`; `make dashboard`
**Verified:** streamlit 1.64.0, deepeval 4.2.7, offline mode (2026-10-02)

## Setup

```bash
cd 04-code-examples/agent-eval-framework
export OFFLINE=1
uv run python demos/m12_quality_dashboard.py      # writes fresh reports/results/eval.json
```

Browser at 1920×1080, Streamlit dark theme matched to the design system.

## Recording Script

### Scene 1: Two versions side by side (40 s)

```bash
uv run python demos/m12_experiment_comparison.py
```

Real offline output:

```
Pass rate: v1.2 70% -> v1.3 100% (+30%)
  Answer Correctness   +0.240
  Answer Relevancy     +0.000
  Faithfulness         +0.750
Improved: ['Answer Correctness', 'Faithfulness']  Regressed: []
```

Callout: v1.2 is the regressed prompt, v1.3 restores the grounding rule. `reports/experiments.py` appends each run to `reports/results/experiments.jsonl`.

### Scene 2: The text dashboard (20 s)

```bash
uv run python demos/m12_quality_dashboard.py
```

```
Quality gate: PASS   pass rate 100% (10/10)
  Answer Correctness   0.98
  Answer Relevancy     1.00
  Faithfulness         1.00
  faq          3/3
  account      3/3
  escalation   2/2
  security     2/2
```

### Scene 3: Streamlit (60 s)

```bash
make dashboard        # uv run streamlit run reports/quality_dashboard.py
```

Walk the page top-down ("TechCorp Agent Quality Dashboard"): four tiles (Quality gate, Pass rate, Faithfulness, Answer relevancy) → "By category" table → "Trend across versions" line chart (from `experiments.jsonl`) → "Security (red team)" line (when `redteam.json` exists, after `make capstone`) → "Case details" table with per-case metric scores and tools. One callout per panel.

## Verify Before Recording

- [ ] `reports/results/` has fresh `eval.json` and at least two runs in `experiments.jsonl` (run the comparison demo first)
- [ ] Offline numbers labelled "offline" on screen; re-run live if you present them as model scores
- [ ] The dashboard is the course's own Streamlit app; Confident AI is not used

## Post-Production Notes

- Gate PASS in teal; any metric under threshold in red, threshold lines in amber
- Keep the browser zoom so every number is readable at 1080p
