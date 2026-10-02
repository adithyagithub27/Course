# Demo 01 — The One-Line Prompt Edit

**Used in:** Lecture 0.1 (Your AI Agent Just Failed in Production — Now What?), hook and showcase
**Duration:** ~90 seconds of screen recording
**Purpose:** Show a real agent failure caused by a "harmless" prompt edit, and the evaluation that would have blocked the deploy. This is the course's promise in one screen.
**Demo file:** `demos/m00_agent_failure.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command:** `uv run python demos/m00_agent_failure.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02)

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install                       # once
export OFFLINE=1                   # deterministic: the output below, word for word
```

Terminal: dark theme, JetBrains Mono 18–20 pt, 100 columns. Clear the screen before each take. The version banner the script prints is the version banner for this lecture.

## Recording Script

### Scene 1: The edit (20 s)

VS Code, `agents/support_agent.py`, `SYSTEM_PROMPT`. Highlight the line:

```
- Only state prices, limits and policies that appear in a knowledge base result
```

Show it struck through (a red overlay in post), as if a teammate deleted it in a "tidy up the prompt" PR. Callout: "1 line deleted. Code review: approved."

### Scene 2: Before and after (40 s)

Run the demo. Real offline output (after the banner):

```
The 'harmless' prompt edit deleted this line:
   - Only state prices, limits and policies that appear in a knowledge base result
BEFORE (v1) tools=['search_knowledge_base']
  answer: TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days, and annual subscriptions are prorated.
  Faithfulness vs the refund policy: 1.00 -> PASS
AFTER  (v2) tools=[]
  answer: We offer a 14-day money-back guarantee, and refunds take about 10 business days.
  Faithfulness vs the refund policy: 0.00 -> FAIL: block this deploy
```

Callouts, in order:
1. `tools=['search_knowledge_base']` (teal) vs `tools=[]` (red): "It stopped checking."
2. "14-day" and "10 business days" (red): "Both invented."
3. `0.00 -> FAIL: block this deploy` (red, hold 2 s).

### Scene 3: What it would have cost (20 s)

K3 slide, illustrative, no invented statistics:

```
What just happened
- One deleted line, no failing unit test
- Every refund answer now wrong, and confident
- One faithfulness check blocked it
```

Narration point: "Same agent, same question, one line. By Module 12 this check runs on every pull request."

## Verify Before Recording

- [ ] `make test` green (204 passed, 5 skipped)
- [ ] Output matches the block above (offline). If you record live, re-capture: the wording changes, the tool calls and the FAIL should not
- [ ] No API key visible anywhere on screen

## Post-Production Notes

- Dark theme; red only on the failure lines, teal on the passing line (design system)
- Hold the FAIL line for 2 seconds; a soft "error" sound effect is optional
- Lower third on the AFTER answer: "Real policy: 30 days, 5–7 business days (KB-102)"
