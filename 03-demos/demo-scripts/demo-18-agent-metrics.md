# Demo 18 — Task Completion and Tool Correctness

**Used in:** Lecture 4.2 (Agent-Specific Metrics)
**Lecture type:** Teach + demo
**Duration:** ~90 seconds of screen recording
**Purpose:** Score real trajectories with DeepEval's ToolCorrectnessMetric and TaskCompletionMetric, and read the reason on a bad run.
**Demo file(s):** `demos/m04_agent_metrics.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m04_agent_metrics.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Real runs (40 s)

Four real runs score 1.00 / 1.00 (GS-03, GS-05, GS-06, GS-07).

### Scene 2: The bad run (40 s)

The recorded run that called `create_ticket` instead of `search_knowledge_base`: tool correctness 0.00 and DeepEval's reason (missing tools).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m04_agent_metrics.py
id            expected tools                                    called                                            tool_correct  task_complete
------------  ------------------------------------------------  ------------------------------------------------  ------------  -------------
GS-03         search_knowledge_base                             search_knowledge_base                             1.00          1.00         
GS-05         lookup_customer,create_ticket                     lookup_customer,create_ticket                     1.00          1.00         
GS-06         lookup_customer,search_knowledge_base,create_tic  lookup_customer,search_knowledge_base,create_tic  1.00          1.00         
GS-07         escalate_to_human                                 escalate_to_human                                 1.00          1.00         
recorded-bad  search_knowledge_base                             create_ticket                                     0.00          -            
ToolCorrectness reason for the bad run: [
	 Tool Calling Reason: Incomplete tool usage: missing tools [ToolCall(
    name="search_knowledge_base",
    type="FUNCTION"
)]; expected ['search_knowledge_base'], called ['create_ticket']. See more details above.
	 Tool Selection Reason: No available tools were provided to assess tool selection criteria
]
```

## Verify Before Recording

- [ ] `ToolCorrectnessMetric` compares names only and still takes a `model=` in 4.2
- [ ] The "Tool Selection Reason: No available tools were provided" line is DeepEval's own message: explain it or trim it on screen
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D7 build 3
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
