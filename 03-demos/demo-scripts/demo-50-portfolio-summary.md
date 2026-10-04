# Demo 50 — Your Portfolio in Five Lines

**Used in:** Lecture 15.1 (AI Testing Interview Questions & Career Roadmap)
**Lecture type:** Screen beat in a teach lecture (A5)
**Duration:** ~60 seconds of screen recording
**Purpose:** Turn what students built into resume lines and a STAR answer for interviews.
**Demo file(s):** `demos/m15_portfolio_summary.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m15_portfolio_summary.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Resume lines (30 s)

Five lines: agents tested, test files and demos, metrics, security, ops.

### Scene 2: STAR (30 s)

The STAR example: the prompt edit that invented refund terms, blocked by the CI regression gate (Faithfulness 1.00 → 0.25).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m15_portfolio_summary.py
- Agents tested: TechCorp support (5 tools), policy RAG agent, operations agent (6 tools), SecureBank, 3-agent Reply Desk
- 21 test files across a five-layer eval pyramid; 61 runnable demos
- Metrics: DeepEval (relevancy, faithfulness, hallucination, GEval, tool correctness), RAGAS 0.4, custom judges
- Security: promptfoo suite on the real agent, Garak and PyRIT configs, PII scanner, red-team report
- Ops: Langfuse v4 + OpenTelemetry GenAI traces, benchmarks, model routing, drift monitor, CI quality gate
STAR example: 'Situation: a prompt edit made our agent invent refund terms. Task: stop it reaching
production. Action: golden-dataset regression gate in CI. Result: faithfulness drop from 1.00 to 0.25 blocked the PR.'
```

## Verify Before Recording

- [ ] "21 test files" and "61 runnable demos" come from the repo; re-count if files were added
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Keep it on screen long enough to read (10 s per block)
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
