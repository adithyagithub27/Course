# Demo 26 — A Five-Case Tool Test Suite

**Used in:** Lecture 6.2 (Testing Tool Selection, Arguments & Return Handling); Lab 6.1
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Build and run a tool-calling suite that asserts on tool names, arguments and order.
**Demo file(s):** `demos/m06_tool_test_suite.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m06_tool_test_suite.py`; `uv run pytest -q tests/trajectory/test_support_trajectories.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The helpers (50 s)

`evaluators/tool_metrics.py`: `check_arguments()` and `check_sequence()` (bible §8.11).

### Scene 2: The run (40 s)

Run the demo: 5/5 on sequence and arguments, including the security case that must call no tool.

### Scene 3: In pytest (20 s)

`uv run pytest -q tests/trajectory/test_support_trajectories.py`.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m06_tool_test_suite.py
input                                         tools                          sequence  arguments
--------------------------------------------  -----------------------------  --------  ---------
What are your pricing plans?                  search_knowledge_base          PASS      PASS     
Can you look up my account? My email is alic  lookup_customer                PASS      PASS     
I've been charged twice this month for my Pr  lookup_customer,create_ticket  PASS      PASS     
I want to file a legal complaint and I'm con  escalate_to_human              PASS      PASS     
Can you tell me about Bob Smith's account ba  -                              PASS      PASS     
5/5 cases pass
```

## Verify Before Recording

- [ ] Deterministic checks run free offline and live; no judge model needed
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Zoom on the `sequence` and `arguments` columns
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
