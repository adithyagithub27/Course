# Demo 10 — The Six Failure Modes, One Run Each

**Used in:** Lecture 1.4 (The 6 Ways AI Agents Fail)
**Lecture type:** Teach + failure demos
**Duration:** ~2.5 minutes of screen recording
**Purpose:** Show one recorded run per failure mode (T2) and the check that catches it, so each name on the D1 slide has a real example.
**Demo file(s):** `demos/m01_failure_gallery.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m01_failure_gallery.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Hallucination and wrong tool (40 s)

First two blocks: stale prices with no tool call (Faithfulness 0.00); a password question turned into `create_ticket` (expected `search_knowledge_base`).

### Scene 2: Arguments and reasoning (40 s)

"Alice" passed instead of the email (argument check); 3 weeks judged outside a 30-day window (GEval correctness 0.30).

### Scene 3: Goal drift and loops (40 s)

A double charge answered with API limits (relevancy 0.00); the same search five times until the 5-iteration cap (loop detector).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m01_failure_gallery.py
[hallucination] What are your pricing plans?
  tools : []
  reply : TechCorp has three plans: Basic at $7.99/month, Pro at $24.99/month and Enterprise at $99/month.
  why   : Answered from memory without searching the knowledge base; every price is wrong.
  caught: Faithfulness 0.00 (threshold 0.8)
[wrong_tool_selection] How do I reset my password?
  tools : ['create_ticket']
  reply : I've opened a ticket for your password reset.
  why   : A self-service FAQ became a ticket: the KB article answers it.
  caught: expected ['search_knowledge_base'], got ['create_ticket']
[incorrect_tool_arguments] Can you look up my account? My email is alice@example.com
  tools : ['lookup_customer']
  reply : I couldn't find an account for Alice.
  why   : Right tool, wrong argument: passed a first name instead of the email.
  caught: argument check: wrong={'identifier': ('alice@example.com', 'Alice')}
[reasoning_error] I signed up 3 weeks ago. Can I still get a full refund?
  tools : ['search_knowledge_base']
  reply : Unfortunately 3 weeks is outside our 30-day money-back guarantee, so a full refund isn't possible.
  why   : Retrieved the right policy, then drew the wrong conclusion (21 days < 30 days).
  caught: GEval correctness 0.30
[goal_drift] I was charged twice this month. Can you fix it?
  tools : ['search_knowledge_base']
  reply : Great question! The Pro plan includes 1,000 API requests per hour, and you can create API keys under
  why   : Started on billing, ended up explaining API limits; the double charge is never addressed.
  caught: Answer relevancy 0.00
[infinite_loop] What is the refund policy for annual enterprise contracts signed through a reseller?
  tools : ['search_knowledge_base', 'search_knowledge_base', 'search_knowledge_base', 'search_knowledge_base', 'search_knowledge_base']
  reply : I apologize, but I'm having trouble processing your request. Let me escalate this to a human agent.
  why   : The same search 5 times in a row until the 5-iteration cap stopped it.
  caught: loop detector: 'search_knowledge_base' repeated 3 times in a row
```

## Verify Before Recording

- [ ] These are **recorded** runs from `datasets/failure_gallery.json`, not live model output: say "recorded examples"
- [ ] Names must match T2 exactly (no "grounding failure", no "boundary violation")
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair each block with the matching D1 build step (D1-step1 … D1-step6)
- `caught:` lines in teal, `why:` lines in red
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
