# Demo 31 — Loop Detection and Failure Injection

**Used in:** Lecture 7.3 (Detecting Infinite Loops, State Corruption & Failure Propagation); Lab 7.1; reused in 10.2
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Build the runtime loop detector, then inject the four Lab 7.1 failures and verify each is detected and degrades or recovers.
**Demo file(s):** `demos/m07_loop_detector.py`, `demos/m07_lab_failure_injection.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m07_loop_detector.py`; `uv run python demos/m07_lab_failure_injection.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The detector (45 s)

`performance/reliability.py`, `LoopDetector.record()` (bible §8.14). Run `m07_loop_detector.py`: HALT at step 6.

### Scene 2: Four injections (60 s)

Run `m07_lab_failure_injection.py`: research_empty, writing_toxic, research_loop → degraded; corrupt_message → recovered. All PASS.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m07_loop_detector.py
step 1: research  find refund facts    -> ok
step 2: research  find refund facts    -> ok
step 3: writer    draft                -> ok
step 4: research  which plan?          -> ok
step 5: research  which plan?          -> ok
step 6: research  which plan?          -> HALT: 'research' repeated 3 times in a row
On a single agent's tool calls: 'search_knowledge_base' repeated 3 times in a row
```

```
$ uv run python demos/m07_lab_failure_injection.py
injected         detected           expected           status     steps  result
---------------  -----------------  -----------------  ---------  -----  ------
research_empty   empty_research     empty_research     degraded   1      PASS  
writing_toxic    unsafe_output      unsafe_output      degraded   2      PASS  
research_loop    loop_detected      loop_detected      degraded   3      PASS  
corrupt_message  corrupted_message  corrupted_message  recovered  4      PASS  
degraded = the customer gets the safe fallback; recovered = failure caught and the retry succeeded.
Fallback reply: Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will follow up with you within one business day.
```

## Verify Before Recording

- [ ] Lab 7.1 is the 3-agent Supervisor/Research/Writing system (the old 2-agent router lab is retired)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- HALT line in red; PASS column in teal
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
