# Demo 49 — Ship It: the Dashboard Reveal

**Used in:** Lecture 14.5 ([PROJECT 5 — CAPSTONE] Ship the Platform)
**Lecture type:** Build-along
**Duration:** ~90 seconds of screen recording
**Purpose:** The "ship it" moment: the capstone results in the dashboard, gate PASS, red team clean.
**Demo file(s):** `demos/m14_dashboard_reveal.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m14_dashboard_reveal.py`; `make capstone   # run first: the reveal reads its results`; `make dashboard`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0 | opentelemetry-sdk 1.45.0, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Text summary (30 s)

Gate PASS, 100%, 5/5 per category, red team 10/10.

### Scene 2: Streamlit (50 s)

`make dashboard`: the same numbers as tiles, tables and the trend chart.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m14_dashboard_reveal.py
Gate: PASS | pass rate 100% | {'Answer Correctness': 0.975, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0, 'Tool Correctness': 1.0}
  faq          5/5
  account      5/5
  escalation   5/5
  security     5/5
Red team: {'total': 10, 'passed': 10, 'by_severity': {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}}
Runs in history: ['v1.0']
The 'ship it' moment: make dashboard
```

## Verify Before Recording

- [ ] Run `make capstone` immediately before (the reveal reads `reports/results/`)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- A short music sting on the PASS tile
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
