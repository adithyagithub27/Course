# AI Agent Quality Scorecard

> AI Agent Testing & Evaluation — template for Lecture 13.3, Lab 13.1 and the capstone report. The weekly table can be generated with `monitoring/scorecard.py` (`build_scorecard`, `render_markdown`); the release decision follows the capstone gate (`capstone/platform.py`).

## Executive Summary

| Field | Value |
|-------|-------|
| **Agent and version** | [name, vX.Y] |
| **Week / date** | [YYYY-MM-DD] |
| **Prepared by** | [name / team] |
| **Overall status** | GREEN / AMBER / RED |
| **Release decision** | SHIP / BLOCK |
| **One-line summary** | [Is it working? What's the trend? What needs attention?] |

---

## Five Quality Dimensions (T3)

Targets from `monitoring/scorecard.py`: correctness 0.85, faithfulness 0.85, relevance 0.80, safety 0.95, reliability 0.90. GREEN = on target, AMBER = within 5 points, RED = further below. Trend vs last week: ↑ improving, → flat, ↓ declining.

| Dimension | This week | Last week | Trend | Light | Evidence (metrics) |
|---|---|---|---|---|---|
| Correctness | | | | | Answer Correctness, Tool Correctness, Task Completion |
| Faithfulness | | | | | Faithfulness (DeepEval / RAGAS), Hallucination |
| Relevance | | | | | Answer Relevancy, context precision |
| Safety | | | | | red-team pass rate, PII Safety, injection resistance |
| Reliability | | | | | consistency, failure rate, p95 latency, cost per task |

| Cost per task | Tasks per week | Weekly cost | Escalation rate |
|---|---|---|---|
| $____ (verify current pricing) | | $____ | __% |

---

## Release Gate (five rules)

| # | Rule | Result | Status |
|---|---|---|---|
| 1 | Functional pass rate ≥ 80% on the golden dataset | __% (__/__) | PASS / FAIL |
| 2 | Red-team pass rate 100% (no open finding) | __/__ blocked | PASS / FAIL |
| 3 | p95 latency ≤ 10 s | __ s | PASS / FAIL |
| 4 | Average cost per task ≤ $0.01 (verify current pricing) | $__ | PASS / FAIL |
| 5 | No regression vs baseline (≤ 5 points, no newly failing case) | | PASS / FAIL |

A single failing rule means BLOCK. List every reason; don't average them away.

---

## Security Findings

| ID | Severity | Category | Evidence | Remediation | Status |
|---|---|---|---|---|---|
| | Critical / High / Medium / Low | | | | open / fixed (verified) |

## Production Signals

| Signal | Value | Alert? |
|---|---|---|
| Drift (7-day rolling average vs launch baseline) | | |
| Failures / loops in traces | | |
| PII scanner findings on sampled replies | | |

*Label simulated or offline data as such.*

---

## Actions

| Action | Owner | Due |
|---|---|---|
| | | |

## Approval (recorded in the audit trail, `monitoring/governance.py`)

| Role | Name | Decision | Date |
|------|------|----------|------|
| QA lead | | APPROVE / REJECT | |
| Product owner | | APPROVE / REJECT | |
| Security | | APPROVE / REJECT | |
