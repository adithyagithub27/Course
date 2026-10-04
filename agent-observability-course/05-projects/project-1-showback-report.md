# Project 1: The Showback Report

| Field | Details |
|---|---|
| **Section / lecture** | Section 6, lecture 6.9 (Udemy assignment) |
| **Estimated effort** | 4 to 6 hours |
| **Difficulty** | Intermediate |
| **Builds on** | Labs 1 to 3, lectures 6.1 to 6.8, Coding exercises CE1 and CE5 |
| **You will submit** | A one-page weekly cost report (Markdown or PDF), the script that produced it, and answers to three short questions |

---

## Scenario

Northwind Logistics runs Atlas for four departments. Finance has been paying one OpenAI invoice for six months and has started asking questions. The head of finance, Ines Okafor, sent this to the platform team:

> "The Atlas invoice was $1,700 last month, up 38% on the month before, and nobody can tell me which department drove it. From next quarter I want a weekly report that shows cost by department and by what the agent was doing, in numbers I can put in front of department heads. And I want three things we can do about it, with the saving each one is worth. If I cannot get that, I will start charging departments a flat split, and Operations will be furious."

You are the engineer who owns Atlas's telemetry. Produce the report Ines can defend in front of four department heads, from the traces alone.

**Showback**, not chargeback: you show each department what it consumed; nobody gets an invoice yet. The report has to be trusted first.

---

## Requirements

You build the report from the replayed day (Decision O1: `OFFLINE=1 make replay` with the Makefile defaults, seed 7, 4,000 sessions, fixture day Monday 2026-09-14, tenants `ops`, `finance`, `hr`, `eng`). The replayed day stands in for the week; the report's title still says "weekly" because that is the cadence finance will get.

```bash
cd 03-code
OFFLINE=1 make replay                     # baseline day into .atlas/spans.sqlite (about 20 s)
make report                               # northwind.report.weekly_report, Markdown to stdout
```

Expected headline (offline, deterministic; prices "verify current pricing"):

```text
| Total LLM cost | $56.28 | - |
| Requests | 10,184 | sessions: 4,000 |
| Cost per session | $0.0141 | budget $0.0500 |
| Cost per resolved session | $0.0144 | |
| Latency p50 / p95 | 3232 / 3827 ms | budget p95 4000 ms |
```

and three showback tables: **by tenant** (ops $20.27, 36.0%; eng $12.50, 22.2%; finance $11.91, 21.2%; hr $11.59, 20.6%), **by feature** (policy_question $42.91, 76.2%; create_ticket $6.66; ticket_lookup $3.21; shipment_status $2.21; password_reset $0.78; escalation $0.38; other $0.13) and **by model** (gpt-4.1-mini $55.90, gpt-4.1 $0.38 for the 43 escalations).

For the comparison rows, replay each configuration into its own store; without `STORE=` every replay clears `.atlas/spans.sqlite`:

```bash
OFFLINE=1 make replay DIET=1 STORE=.atlas/diet.sqlite && make report STORE=.atlas/diet.sqlite
OFFLINE=1 make replay CACHE=1 STORE=.atlas/cache.sqlite && make report STORE=.atlas/cache.sqlite
```

Reference totals for the same day: caching $37.00, diet $41.99, routing $47.07, caching + diet $22.71, all three $19.07 (the Ops Console's **Compare replays** page shows them side by side).

You may submit the `make report` output edited into a one-pager, or write your own script (`projects/p1/showback.py`) over the local store using `northwind.cost` (`CostRecord`, `rollup`, `total_cost`, `cost_per_session`, `showback_table`). Either way, the numbers must come from the store, not from this brief.

### Functional requirements

| ID | Requirement |
|---|---|
| F1 | **Headline**: total cost, requests, sessions, cost per session and **cost per resolved session**, with the resolved rate stated beside it (outcomes come from the `atlas.outcome` attribute: `resolved`, `escalated`, `guardrail`, `step_limit`, `refused`, `error` ...). Explain in one sentence why cost per resolved session is higher than cost per session. |
| F2 | **Cost by tenant**: requests, sessions, tokens in and out, cache hit, cost, cost per session and share, sorted by cost, with a total row. |
| F3 | **Cost by feature** (the `atlas.feature` attribute on the request): policy_question, create_ticket, ticket_lookup, shipment_status, password_reset, escalation, other. Same columns as F2. |
| F4 | **Trend across configurations**: at least the baseline and two lever stores (for example diet and caching), each as total cost and cost per resolved session. |
| F5 | **Three recommendations**, each citing a number from your report and estimating the saving in dollars per month (a replayed day × 30 is fine if you say so), with the quality trade-off (the judge's grounded or resolved mean from the same store). |
| F6 | **Prices** stated with a date and the words "verify current pricing". |

### Non-functional requirements

| ID | Requirement |
|---|---|
| N1 | One page (about 600 words plus tables). |
| N2 | Every number traceable to `make report`, the console, or a function in your script; no hand-typed numbers. |
| N3 | No PII: tenants and features, never employees. If you cite a session, use the session id. |
| N4 | Deterministic: rerunning the commands reproduces the numbers. |

---

## Acceptance criteria

1. The report's total matches `make report` on the same store (offline baseline: $56.28) and the tenant shares sum to 100% (±0.1).
2. The tenant table has four tenants (`ops`, `finance`, `hr`, `eng`) plus a total; the feature table has the seven features in F3.
3. Cost per resolved session is shown with the resolved rate and is higher than cost per session.
4. At least two comparison stores appear in the trend, each replayed with its own `STORE=`.
5. Each recommendation cites a number, a monthly saving and a trade-off. Example of the bar: "Policy questions are 76% of the bill; the diet replay takes the day from $56.28 to $41.99, about $430 a month, with grounded unchanged."
6. Prices are dated and marked "verify current pricing".
7. No user ids or names appear.

---

## Deliverables

| # | Deliverable | Format |
|---|---|---|
| D1 | `projects/p1/REPORT.md` (and optionally a PDF export) | One page |
| D2 | The commands or script that produced it | Code or a shell snippet |
| D3 | A screenshot of your tenant table next to the Ops Console **Cost** page (`make console`) showing the same total | Image |

---

## Grading rubric (100 points)

Matches the rubric slide in lecture 6.9.

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Report by tenant and feature, with the trend across configurations** (40) | 36-40: Tenant and feature tables complete and reconciled with `make report`; two or more comparison stores, each replayed with its own `STORE=` | 24-35: Tables present, trend thin or one store reused | 0-23: Only a tenant total, or numbers that do not reconcile |
| **Cost per resolved session as the headline** (20) | 18-20: Headline, resolved rate stated, gap to cost per session explained | 12-17: Present but no resolved rate or explanation | 0-11: Missing or computed as cost per session |
| **Three recommendations** (30) | 27-30: Each cites a number and a monthly saving, with a trade-off; at least one verified by a re-replay | 18-26: Savings estimated but not verified, or trade-offs missing | 0-17: Generic advice without numbers |
| **Prices dated and marked "verify current pricing"** (10) | 10: Dated and flagged | 5: Dated but not flagged | 0: Undated |

**Pass mark:** 70/100.

---

## Hints

1. Each lever needs its own store. `make replay CACHE=1` without `STORE=` overwrites your baseline.
2. The Makefile exports `CACHE`, `DIET` and `ROUTER` (default 0), which override `ATLAS_*` variables in your shell; pass the levers on the `make` line.
3. Ops is the biggest tenant because it has the most sessions, not because it misuses Atlas: its cost per session is the lowest. Say so before anyone asks for a flat split.
4. The baseline's only recommendation from `make report` is the cache one (hit ratio 0%). The other two are yours; the feature table is where to look.
5. Write the headline first: "Atlas cost $X on a normal day; ops is Y% because it has Z% of the sessions; three changes save $W a month."

---

## Submission (Udemy assignment)

Submit through the **Project 1: The showback report** assignment in lecture 6.9. The full Udemy entry, including the instructor's example answers, is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste your report (or a link to it). What is the day's total, the cost per resolved session and the resolved rate, and which tenant has the highest cost per session and why?
2. Paste your three recommendations, each with the cited number, the monthly saving and the trade-off. Which one did you verify with a re-replay into its own store, and what did it measure?
3. Which comparison stores did you build, and what did the trend across them tell you that the baseline alone did not?

---

## Peer-review checklist

- [ ] The report fits on one page and opens with a headline sentence a non-engineer understands.
- [ ] The total matches `make report` on the same store; tenant shares sum to 100%; there is a total row.
- [ ] The feature table has all seven features, with `escalation` priced at gpt-4.1's rate.
- [ ] Cost per resolved session is the headline, with the resolved rate beside it.
- [ ] The trend uses at least two lever stores, each replayed with its own `STORE=`.
- [ ] Each recommendation has a cited number, a monthly saving and a trade-off; at least one was measured by re-replay.
- [ ] Prices are dated and marked "verify current pricing".
- [ ] No employee names or ids anywhere in the report.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
