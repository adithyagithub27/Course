# Demo 41 — One Deleted Line, Caught

**Used in:** Lecture 11.1 (Why Agents Regress)
**Lecture type:** Screen beat in a teach lecture (A5)
**Duration:** ~2 minutes of screen recording
**Purpose:** Delete the grounding rule and watch the regression suite catch it: pass rate 100% → 70%, Faithfulness 1.00 → 0.25.
**Demo file(s):** `demos/m11_regression_simulation.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m11_regression_simulation.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The change (20 s)

`PROMPT_V2_REGRESSED` (bible §8.21): one `replace()`.

### Scene 2: The deltas (50 s)

Answer Correctness −0.24, Faithfulness −0.75; pass rate 100% → 70%.

### Scene 3: The evidence (40 s)

GS-01, GS-02, GS-03 now answer from stale memory: $7.99/$24.99/$99, 14-day guarantee, 500 requests per hour.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m11_regression_simulation.py
metric              baseline  current  delta
------------------  --------  -------  -----
Answer Correctness  0.98      0.74     -0.24
Answer Relevancy    1.00      1.00     +0.00
Faithfulness        1.00      0.25     -0.75
Pass rate: 100% -> 70%
Regressed metrics (> 5 points): ['Answer Correctness', 'Faithfulness']
Cases that passed before and fail now: ['GS-01', 'GS-02', 'GS-03']
  GS-01: TechCorp has three plans: Basic at $7.99/month, Pro at $24.99/month and Enterprise at $99/
  GS-02: We offer a 14-day money-back guarantee, and refunds take about 10 business days.
  GS-03: The Pro plan allows 500 API requests per hour and Basic allows 50.
REGRESSION DETECTED: True
```

## Verify Before Recording

- [ ] Numbers are offline (bible §12.4)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Teal callouts with the real KB facts beside each wrong answer
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
