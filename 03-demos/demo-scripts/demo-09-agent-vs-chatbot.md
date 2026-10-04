# Demo 09 — Agent vs Chatbot Side by Side

**Used in:** Lecture 1.2 (What Makes an Agent an Agent); 1.3 (Agent Architecture)
**Lecture type:** Diagram + demo
**Duration:** ~90 seconds of screen recording
**Purpose:** Show the difference between one LLM call and the agent loop on the same request: tools called, results fed back, a ticket actually created.
**Demo file(s):** `demos/m01_agent_vs_chatbot.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m01_agent_vs_chatbot.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The chatbot (25 s)

Top half of the output: one call, no tools, "I don't have access to your account".

### Scene 2: The agent loop (45 s)

Bottom half: step 1 `lookup_customer`, step 2 `create_ticket` (TKT-5001, priority high), final reply. Pair with diagram D3 build 2 (the loop). Callout on the last line: 3 LLM calls, 2 tool calls.

### Scene 3: The code behind it (20 s)

Cut to `agents/support_agent.py`, the `for _ in range(max_iterations):` loop (bible §8.1): call → tool calls → append results → repeat.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m01_agent_vs_chatbot.py
CHATBOT (one LLM call, no tools):
  I'm sorry about the trouble. I don't have access to your account or TechCorp's billing system, so I can't check the charges or open a ticket. Please contact TechCorp support with your account email.
AGENT (LLM + tools in a loop):
  step 1: lookup_customer({'identifier': 'alice@example.com'})
          -> Customer found: {"id": "CUST-001", "name": "Alice Johnson", "email": "alice@exam
  step 2: create_ticket({'customer_id': 'CUST-001', 'priority': 'high'})
          -> Ticket TKT-5001 created: Duplicate charge on Pro plan (Priority: high)
  final : Thanks, Alice. I've opened high-priority ticket TKT-5001 so our billing team can investigate the double charge and get back to you.
3 LLM calls, 2 tool calls, 2994 tokens
```

## Verify Before Recording

- [ ] Ticket numbers count up per process (TKT-5001 is the first); don't read later numbers aloud
- [ ] Token count is offline (`len//4`); say "offline" if you show it
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Use the printed steps as the build order for D3
- Highlight the tool result lines in white, the final reply in teal
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
