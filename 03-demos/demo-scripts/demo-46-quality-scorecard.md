# Demo 46 — The Leadership Scorecard

**Used in:** Lecture 13.3 (Building an Agent Quality Scorecard for Leadership); Lab 13.1
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Build a one-page scorecard for three agents on the five dimensions with traffic lights, trends, cost and escalations.
**Demo file(s):** `demos/m13_quality_scorecard.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m13_quality_scorecard.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The table (60 s)

Three agents; TechCorp Support green; Policy Assistant amber on correctness; Operations Agent red on safety.

### Scene 2: The action (30 s)

Last line: "Operations Agent is RED on safety: open the red-team report before the next release."

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m13_quality_scorecard.py
# Agent Quality Scorecard - week of 2026-09-28
| Agent | Overall | Correctness | Faithfulness | Relevance | Safety | Reliability | Cost/task | Weekly cost | Escalations |
|---|---|---|---|---|---|---|---|---|---|
| TechCorp Support | [G] | [G] 0.98 ^ | [G] 1.00 ^ | [G] 1.00 ^ | [G] 0.99 = | [G] 0.95 = | $0.0008 | $28.00 | 6% |
| Policy Assistant (RAG) | [A] | [A] 0.84 v | [G] 0.93 = | [G] 0.87 = | [G] 0.98 = | [G] 0.93 = | $0.0006 | $2.52 | 2% |
| Operations Agent | [R] | [G] 0.88 = | [G] 0.90 = | [G] 0.85 = | [R] 0.89 v | [G] 0.91 = | $0.0012 | $1.80 | 0% |
[G] on target  [A] within 5 points  [R] action needed   ^ improving  v declining  = flat
Costs use list prices (verify current pricing).
Operations Agent is RED on safety: open the red-team report before the next release.
```

## Verify Before Recording

- [ ] Agent values are illustrative except where replaced by a real offline run (`monitoring/scorecard.py`, `EXAMPLE_AGENTS`)
- [ ] Costs: verify current pricing
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Render the Markdown table with real colour chips
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
