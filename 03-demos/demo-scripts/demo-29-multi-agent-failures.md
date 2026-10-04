# Demo 29 — Multi-Agent Failure Montage

**Used in:** Lecture 7.1 (Multi-Agent Architectures: What Can Go Wrong)
**Lecture type:** Screen beat in a diagram lecture (A5)
**Duration:** ~2 minutes of screen recording
**Purpose:** Show the 3-agent Reply Desk healthy, then three failures: an infinite delegation loop, a corrupted hand-off and a cascade from empty research.
**Demo file(s):** `demos/m07_multi_agent_failures.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m07_multi_agent_failures.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Healthy (20 s)

research → writer → finish, status ok.

### Scene 2: Loop and corruption (50 s)

Loop: research ×3, loop detected, degraded, fallback reply. Corruption: checksum mismatch on message 2, retried, recovered.

### Scene 3: Cascade (30 s)

Research returns nothing: degraded after 1 step, instead of a made-up reply.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m07_multi_agent_failures.py
[healthy] status=ok steps=3
  delegations: ['research', 'writer', 'finish']
  failures   : none
  reply      : Hi there, thanks for reaching out. TechCorp offers a 30-day money-back guarantee on all plans. Refunds are pro
[1 infinite delegation loop] status=degraded steps=3
  delegations: ['research', 'research', 'research']
  failures   : [{'type': 'loop_detected', 'agent': 'research', 'details': "'research' repeated 3 times in a row"}]
  reply      : Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will f
[2 state corruption (message altered in transit)] status=recovered steps=4
  delegations: ['research', 'research', 'writer', 'finish']
  failures   : [{'type': 'corrupted_message', 'agent': 'research', 'details': 'checksum mismatch on message 2', 'recovered': True}]
  reply      : Hi there, thanks for reaching out. TechCorp offers a 30-day money-back guarantee on all plans. Refunds are pro
[3 failure cascade (research returns nothing)] status=degraded steps=1
  delegations: ['research']
  failures   : [{'type': 'empty_research', 'agent': 'research', 'details': 'no findings'}]
  reply      : Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will f
```

## Verify Before Recording

- [ ] Status vocabulary: ok / recovered / degraded
- [ ] The fallback reply text is exact (bible §5.4)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D11 builds 1–5
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
