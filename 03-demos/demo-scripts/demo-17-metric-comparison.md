# Demo 17 — Same Answers, Different Metrics

**Used in:** Lecture 4.1 (LLM Quality Metrics)
**Lecture type:** Teach + demo
**Duration:** ~90 seconds of screen recording
**Purpose:** Run five answers through four metrics and show how scores diverge, including DeepEval 4.2's higher-is-better HallucinationMetric.
**Demo file(s):** `demos/m04_metric_comparison.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m04_metric_comparison.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The table (50 s)

Run the demo. Callouts: "5 extra claim" relevancy 1.00 but faithfulness 0.00; "3 off-topic" faithfulness 1.00 but relevancy 0.00; "2 wrong number" correctness 0.50.

### Scene 2: Hallucination footnote (30 s)

Zoom on the footnote: in DeepEval 4.2 HallucinationMetric is the share of contexts the answer agrees with, higher is better.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m04_metric_comparison.py
response        relevancy  faithfulness  hallucination*  correctness
--------------  ---------  ------------  --------------  -----------
1 correct       1.00       1.00          1.00            1.00       
2 wrong number  1.00       1.00          1.00            0.50       
3 off-topic     0.00       1.00          1.00            0.10       
4 vague         0.50       1.00          1.00            0.20       
5 extra claim   1.00       0.00          0.00            1.00       
*DeepEval 4.2 HallucinationMetric: share of contexts the answer agrees with (higher is better).
```

## Verify Before Recording

- [ ] Never say "hallucination: lower is better, threshold 0.3" (that was the old behaviour)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D7 build 2
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
