# Demo 36 — Blind vs Traced Debugging

**Used in:** Lecture 9.1 (Why You Can't Debug an Agent Without Traces)
**Lecture type:** Teach + demo
**Duration:** ~90 seconds of screen recording
**Purpose:** Show the same failure with only the final output, then with a Langfuse trace that points at the failing span.
**Demo file(s):** `demos/m09_blind_vs_traced.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m09_blind_vs_traced.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0 | opentelemetry-sdk 1.45.0, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Blind (30 s)

"I couldn't find that in our knowledge base…": the prompt? the model? a rate limit?

### Scene 2: Traced (50 s)

The trace tree: `tool search_knowledge_base` flagged WARNING with an empty result. Root cause in one look: the tool failed, the model behaved correctly.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m09_blind_vs_traced.py
BLIND: all you have is the final output
  Q: What is your refund policy?
  A: I couldn't find that in our knowledge base, so I don't want to guess. I can create a ticket so a specialist can answer.
  Is it the prompt? the model? a rate limit? You can't tell.
TRACED: Langfuse trace eebfb4f0ffa912c4beed1e0d915dde61
agent      support-agent                   
  generation chat gpt-4.1-mini                usage={"input": 767, "output": 35}
  tool       tool search_knowledge_base       <-- WARNING
             output: No relevant articles found in the knowledge base.
  generation chat gpt-4.1-mini                usage={"input": 842, "output": 29}
Root cause in one look: search_knowledge_base returned nothing; the model behaved correctly.
(For comparison, the healthy tool returns: KB-102 (Refund policy): TechCorp offers a 30-day money-back ...)
```

## Verify Before Recording

- [ ] Trace IDs change on every run; don't read them aloud
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D13 build 3
- Split screen: blind (left, grey) vs traced (right)
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
