# Voice Agent Readiness Scorecard (Go / No-Go)

**Used in:** 12.6 (production readiness), 12.8 (chaos demo), 13.1 / 13.1a (capstone acceptance), 13.7 (domain swap), 15.4 (portfolio talking points)
**Companion:** `production-checklist.md` (the full item list)

> Score each area 0-2. **Any "must-pass" item at 0 = NO-GO**, whatever the total. Fill in the evidence column with a link or file: test report, dashboard screenshot, runbook. A score without evidence counts as 0.

**Scale:** 0 = not done · 1 = partly done / manual only · 2 = done, automated or verified with evidence

---

## Scorecard

| # | Area | Criterion | Must-pass? | Score (0-2) | Evidence |
|---|---|---|---|---|---|
| 1 | Conversation | Main task flows (book/reschedule/cancel or equivalent) pass behavior tests with tool-call argument assertions | **Yes** | | |
| 2 | Conversation | Read-back before every irreversible action (test proves order) | **Yes** | | |
| 3 | Conversation | Unknown questions → "not sure" + transfer offer; no invented facts (judge test) | | | |
| 4 | Conversation | Prompts for the ear: no markdown/URLs, brevity eval passes | | | |
| 5 | Hearing | WER on domain vocabulary within your threshold (text + audio-in tests) | | | |
| 6 | Timing | p95 voice-to-voice latency within budget (latency report) | **Yes** | | |
| 7 | Timing | No dead air during tools (filler speech) | | | |
| 8 | Timing | Interruption handling verified with simulated/impatient callers | | | |
| 9 | Resilience | Provider fallback verified by a chaos test (provider killed mid-call) | **Yes** | | |
| 10 | Resilience | Timeouts on providers and tools; spoken error recovery | | | |
| 11 | Resilience | Human transfer works (tested on the real phone path) | **Yes** | | |
| 12 | Safety | Prompt injection and social-engineering tests pass in CI | **Yes** | | |
| 13 | Safety | Identity verification before revealing or changing records | **Yes** (if records are sensitive) | | |
| 14 | Privacy | PII redacted before logs/traces (verified in a trace sample) | **Yes** | | |
| 15 | Privacy | Retention policy implemented in every system | | | |
| 16 | Compliance | AI disclosure in greeting; recording notice/consent approach decided | **Yes** | | |
| 17 | Compliance | Outbound: consent + DNC + calling hours (N/A if inbound only) | **Yes** (if outbound) | | |
| 18 | Compliance | Legal review done; BAAs signed where PHI is involved | **Yes** (real deployments) | | |
| 19 | Observability | Metrics, traces and cost per minute on a dashboard | | | |
| 20 | Observability | Alerts with owners (p95 latency, error rate, cost/min, transfer rate) | | | |
| 21 | Operations | CI gates block deploys on failed tests/evals | | | |
| 22 | Operations | Deploy + rollback rehearsed; draining on deploy | | | |
| 23 | Operations | On-call runbook (disable outbound, force transfer, rotate keys, roll back) | | | |
| 24 | Cost | Cost per minute known and within target | | | |

## Scoring

| Result | Rule |
|---|---|
| **NO-GO** | Any applicable must-pass item scores 0 |
| **LIMITED GO** (soft launch: limited hours or a share of calls, humans on standby) | All must-pass ≥ 1, total ≥ 60% of the applicable maximum |
| **GO** | All must-pass = 2, total ≥ 80% of the applicable maximum |

Applicable maximum = 2 × number of applicable items (mark N/A items and leave them out).

| Total score | Applicable max | % | Decision | Date | Signed off by |
|---|---|---|---|---|---|
| | | | | | |

## Capstone use (13.1a / 13.7)

For the course capstone, items 17 and 18 can be N/A (fictional business, no real callers). Everything else applies. Include the completed scorecard in your capstone README. It's also a strong portfolio artefact and a talking point in interviews (see `interview-questions.md`).
