# Demo 47 — Capstone Architecture Walkthrough

**Used in:** Lecture 14.1 (Capstone Architecture & Requirements)
**Lecture type:** Teach + diagram
**Duration:** ~90 seconds of screen recording
**Purpose:** Show the capstone's stages, registered agents, gates and reliability limits as the code defines them.
**Demo file(s):** `demos/m14_architecture.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m14_architecture.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0 | opentelemetry-sdk 1.45.0, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Stages (30 s)

functional → security → performance → regression → results → dashboard → gate.

### Scene 2: Agents and gates (50 s)

`support` and `banking_v2` with their datasets and forbidden tools; gates and limits from `eval_config.yaml`. Cut to `QualityPlatform.gate()` (bible §8.27).

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m14_architecture.py
Agent under test -> Test harness -> [functional -> security -> performance -> regression]
                 -> Results store (reports/results) -> Dashboard -> CI/CD gate
agent 'support': golden=golden_capstone redteam=redteam_support forbidden_tools=['create_ticket', 'lookup_customer', 'send_email'] baseline=support_capstone_v1
agent 'banking_v2': golden=- redteam=redteam_banking forbidden_tools=['transfer_funds'] baseline=None
Gates: {'smoke_pass_rate': 1.0, 'pr_pass_rate': 0.8, 'critical_metric_min': 0.7, 'regression_tolerance': 0.05}
Reliability limits: p95 <= 10s, cost <= $0.01/task, red team pass rate 100%
```

## Verify Before Recording

- [ ] Five-rule SHIP/BLOCK gate; no weighted 0–100 score (the old project brief is retired)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D16 builds 1–4
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
