# Demo 39 — Failure Rate, Retry, Timeout and Loops

**Used in:** Lecture 10.2 (Reliability)
**Lecture type:** Build-along
**Duration:** ~90 seconds of screen recording
**Purpose:** Measure failure rate and tool-sequence consistency over 25 runs, and show retry, timeout and loop detection.
**Demo file(s):** `demos/m10_reliability.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m10_reliability.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: 25 runs (30 s)

Failure rate 0%, loops 0, consistency 100%: `measure_reliability()`.

### Scene 2: Retry, timeout, loop (50 s)

`with_retry()` succeeds after 2 retries; `call_with_timeout()` raises at 0.1 s; `detect_tool_loop()` flags the repeated search.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m10_reliability.py
25 runs: failure rate 0%, loops 0, tool-sequence consistency 100%
Retry: succeeded after 2 retries -> Here's your account: Bob Smith, Basic plan, status active, balance $29
Timeout: agent call exceeded 0.1s
Loop detection: 'search_knowledge_base' repeated 3 times in a row
```

## Verify Before Recording

- [ ] Consistency is part of the Reliability dimension (threshold 0.7 in `eval_config.yaml`)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- One callout per line
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
