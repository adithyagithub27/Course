# Demo 42 — Baselines and the Regression Gate

**Used in:** Lecture 11.2 (Building Regression Test Suites with Golden Datasets)
**Lecture type:** Build-along
**Duration:** ~90 seconds of screen recording
**Purpose:** Store a baseline, compare a candidate metric by metric, and gate on a 5-point tolerance.
**Demo file(s):** `demos/m11_baseline_comparison.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m11_baseline_comparison.py`; `make baseline   # re-record regression/baselines/support_v1.json (on purpose only)`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Baseline (30 s)

`support_v1.json`: pass rate 100%, averages.

### Scene 2: Compare (50 s)

Deltas all +0.000, gate ok; candidate approved. Show `compare()` (bible §8.22) and `regression_tolerance: 0.05`.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m11_baseline_comparison.py
Baseline stored: support_v1.json  pass rate 100%  {'Answer Correctness': 0.98, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
metric              baseline  candidate  delta   gate
------------------  --------  ---------  ------  ----
Answer Correctness  0.98      0.98       +0.000  ok  
Answer Relevancy    1.0       1.0        +0.000  ok  
Faithfulness        1.0       1.0        +0.000  ok  
Candidate approved: regressed=[], newly failing=[]
```

## Verify Before Recording

- [ ] Re-record a baseline only after an intended, reviewed change
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D14
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
