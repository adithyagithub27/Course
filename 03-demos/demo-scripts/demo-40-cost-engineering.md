# Demo 40 — Prompt Diet and Model Routing

**Used in:** Lecture 10.3 (Cost Engineering: Finding the 80/20 of Agent Spend)
**Lecture type:** Build-along
**Duration:** ~2.5 minutes of screen recording
**Purpose:** Attack the cost hotspot two ways: a prompt diet on FAQ traffic (−42.8%) and model routing (−29.1%), then re-check quality.
**Demo file(s):** `demos/m10_cost_hotspots.py`, `demos/m10_model_routing.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m10_cost_hotspots.py`; `uv run python demos/m10_model_routing.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The hotspot (30 s)

255 + 481 tokens re-sent on every call; tool schemas are about 65% of it.

### Scene 2: Prompt diet (40 s)

FAQ traffic with only the KB tool: 6,596 → 3,285 input tokens, −42.8%.

### Scene 3: Routing (50 s)

`route_model()` (bible §8.20): 8/20 queries to gpt-4.1-mini, $4.06 → $2.88 per 1,000 tasks, −29.1%; quality re-check 10/10.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m10_cost_hotspots.py
Fixed overhead re-sent on every call: {'system_prompt_tokens': 255, 'tool_schema_tokens': 481}
FAQ traffic, all 5 tool schemas : 6596 input tokens, $0.003107
FAQ traffic, only the KB tool    : 3285 input tokens, $0.001776
Prompt diet saves 42.8% on FAQ traffic (verify current pricing).
```

```
$ uv run python demos/m10_model_routing.py
setup                         cost/task  per 1k tasks
----------------------------  ---------  ------------
all gpt-4.1                   0.004057   4.06        
routed (FAQ -> gpt-4.1-mini)  0.002878   2.88        
8/20 queries routed to gpt-4.1-mini; saving 29.1%
Quality check with routing: 10/10 golden cases pass, averages {'Answer Correctness': 0.97, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
Offline the mock answers the same for every model, so quality is equal by construction: re-run live to verify.
```

## Verify Before Recording

- [ ] **Say it:** offline the mock answers the same for every model, so equal quality is by construction; re-run live to verify (bible §12.2)
- [ ] Never say "50%": routing alone is 29.1%, combine levers for more
- [ ] Prices: verify current pricing
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Before/after bars: red (all gpt-4.1) vs teal (routed)
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
