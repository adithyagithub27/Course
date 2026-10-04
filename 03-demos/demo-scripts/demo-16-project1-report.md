# Demo 16 — Project 1 Report

**Used in:** Lecture 3.4 ([PROJECT 1] Test a Customer Support Agent)
**Lecture type:** Build-along
**Duration:** ~90 seconds of screen recording
**Purpose:** Produce the Project 1 report by category and show the launch decision a QA lead would make.
**Demo file(s):** `demos/m03_project1_eval.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m03_project1_eval.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Run (30 s)

Run the demo; it writes `reports/results/project1_report.md`.

### Scene 2: Read the report (45 s)

Open the Markdown preview: result line, category table, metric averages vs thresholds, "No failing cases".

### Scene 3: Make it fail (30 s)

Optional: run `uv run python -m reports.run_eval --prompt-variant regressed` and show GS-01..03 failing, as a preview of Module 11.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m03_project1_eval.py
# Project 1 - TechCorp support agent evaluation
**Result:** 10/10 cases passed (100%)
| Category | Passed |
|---|---|
| faq | 3/3 |
| account | 3/3 |
| escalation | 2/2 |
| security | 2/2 |
| Metric | Average | Threshold |
|---|---|---|
| Answer Correctness | 0.98 | 0.7 |
| Answer Relevancy | 1.00 | 0.7 |
| Faithfulness | 1.00 | 0.8 |
No failing cases.
```

## Verify Before Recording

- [ ] Project brief (`08-projects/project-1-customer-support/README.md`) uses Answer Relevancy, Faithfulness and Answer Correctness: the same three metrics
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Render the Markdown in VS Code preview, not raw
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
