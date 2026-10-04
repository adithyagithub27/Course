# Demo 48 — The Full Capstone Pipeline

**Used in:** Lecture 14.2–14.4 (Test Harness, Security & Observability, CI/CD & Dashboard); Project 5
**Lecture type:** Build-along
**Duration:** ~3 minutes of screen recording
**Purpose:** Run every stage on both agents and read the SHIP decision, then show the nightly CI job that runs the same command.
**Demo file(s):** `demos/m14_full_pipeline.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m14_full_pipeline.py`; `make capstone`; `uv run python -m capstone.run_capstone --save-baseline   # first run only`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0 | opentelemetry-sdk 1.45.0, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Support agent (70 s)

20/20 golden cases, four metric averages, 10/10 attacks blocked, p50/p95 (simulated), cost per task, no regression → SHIP.

### Scene 2: SecureBank v2 (30 s)

16/16 attacks blocked → SHIP.

### Scene 3: Trace and CI (40 s)

The sampled Langfuse trace; then `.github/workflows/agent-eval.yml`, the `nightly` job (`17 3 * * *`).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m14_full_pipeline.py
# Agent Quality Report: support
**Decision:** SHIP
## Functional evaluation
20/20 golden cases passed (100%)
| Metric | Average |
|---|---|
| Answer Correctness | 0.97 |
| Answer Relevancy | 1.00 |
| Faithfulness | 1.00 |
| Tool Correctness | 1.00 |
## Security
10/10 attacks blocked. Open findings by severity: {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
## Performance (offline latencies are simulated)
p50 1.74s, p95 3.38s, avg 1.95 LLM calls, $0.000798/task ($0.8/1k tasks, verify current pricing)
## Regression vs baseline
Regression: no
# Agent Quality Report: banking_v2
**Decision:** SHIP
## Security
16/16 attacks blocked. Open findings by severity: {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
Observability: trace 85a7722664fdfe83a2381a357502f45d with 4 spans
OVERALL: SHIP
```

## Verify Before Recording

- [ ] Trace IDs change every run
- [ ] Offline numbers: say "offline" or run once live (verify current pricing)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Chapter markers per stage
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
