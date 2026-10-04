# Demo 15 — Running the First End-to-End Evaluation

**Used in:** Lecture 3.3 (Running Your First Agent Eval)
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Run all 10 golden cases through the agent with three metrics plus a tool check and read the results table.
**Demo file(s):** `demos/m03_eval_support_agent.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m03_eval_support_agent.py`; `uv run pytest -q tests/e2e/test_golden_support.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The code (40 s)

`tests/e2e/test_golden_support.py` (bible §8.6) and `to_test_case()` in `evaluators/deepeval_suite.py` (§8.5): tool results become `retrieval_context`.

### Scene 2: The run (50 s)

Run the demo; the table fills row by row. Callouts: `-` in the faithful column (no grounding context for that case), GS-09/GS-10 correctness 0.9 (refusals), averages line.

### Scene 3: Same thing in pytest (20 s)

`uv run pytest -q tests/e2e/test_golden_support.py` → 10 passed.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m03_eval_support_agent.py
id     category    relevancy  faithful  correct  tools_ok  result
-----  ----------  ---------  --------  -------  --------  ------
GS-01  faq         1.0        1.0       1.0      True      PASS  
GS-02  faq         1.0        1.0       1.0      True      PASS  
GS-03  faq         1.0        1.0       1.0      True      PASS  
GS-04  account     1.0        -         1.0      True      PASS  
GS-05  account     1.0        -         1.0      True      PASS  
GS-06  account     1.0        1.0       1.0      True      PASS  
GS-07  escalation  1.0        -         1.0      True      PASS  
GS-08  escalation  1.0        -         1.0      True      PASS  
GS-09  security    1.0        -         0.9      True      PASS  
GS-10  security    1.0        -         0.9      True      PASS  
10/10 passed (100%). Averages: {'Answer Correctness': 0.98, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
```

## Verify Before Recording

- [ ] Offline averages (0.98 / 1.0 / 1.0) are mock-judge numbers: say "offline" or re-run live
- [ ] The legacy script's hook showed a different failure reason for the same billing case; use this real output only
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Zoom on the averages line at the end
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
