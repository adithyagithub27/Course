# Demo 44 — Drift Detection

**Used in:** Lecture 13.1 (Monitoring Agents in Production)
**Lecture type:** Teach + demo
**Duration:** ~90 seconds of screen recording
**Purpose:** Watch a 7-day rolling average of faithfulness drift over four weeks and fire a baseline-drop alert before the threshold alert.
**Demo file(s):** `demos/m13_drift_detection.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m13_drift_detection.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The trend (40 s)

Eight rolling-average points with bars; launch baseline 0.912.

### Scene 2: The alerts (40 s)

Baseline drop on 2026-09-24 (0.851), threshold on 2026-09-28 (0.798 < 0.8). Show `DriftMonitor.check()` (bible §8.25).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m13_drift_detection.py
Week-by-week faithfulness (7-day rolling average, SIMULATED data, seed 7):
  2026-09-07  0.912  #####################
  2026-09-10  0.915  #####################
  2026-09-13  0.917  #####################
  2026-09-16  0.922  ######################
  2026-09-19  0.904  ####################
  2026-09-22  0.873  #################
  2026-09-25  0.842  ##############
  2026-09-28  0.798  #########
Launch baseline: 0.912; threshold from eval_config.yaml: 0.8
[2026-09-24] ALERT faithfulness: 7-day avg 0.851 (baseline_drop, limit 0.862)
[2026-09-28] ALERT faithfulness: 7-day avg 0.798 (threshold, limit 0.800)
[2026-09-28] ALERT task_completion: 7-day avg 0.823 (baseline_drop, limit 0.828)
```

## Verify Before Recording

- [ ] **Label the data SIMULATED (seed 7)** on screen (bible §12.8)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D15
- Threshold line amber, baseline line grey
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
