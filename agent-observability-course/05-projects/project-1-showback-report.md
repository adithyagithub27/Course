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

> "The Atlas invoice was $1,140 last month, up 38% on the month before, and nobody can tell me which department drove it. From next quarter I want a weekly report that shows cost by department and by what the agent was doing, in numbers I can put in front of department heads. And I want three things we can do about it, with the saving each one is worth. If I cannot get that, I will start charging departments a flat split, and Operations will be furious."

You are the engineer who owns Atlas's telemetry. Produce the report Ines can defend in front of four department heads, from the traces alone.

**Showback**, not chargeback: you show each department what it consumed; nobody gets an invoice yet. The report has to be trusted first.

---

## Requirements

You will build the report from a replayed week of traffic. Both paths produce the same span data:

- **Offline (recommended):** `OFFLINE=1 uv run python -m simulator.replay --days 7 --start 2026-09-14 --seed 42 --label showback`. No keys, no cost, deterministic.
- **Online:** the same replay with `OTEL_EXPORTER=langfuse` so you can cross-check totals in the Langfuse cost dashboard (the replay still makes no LLM calls; the spans carry mock usage).

Write your own script `projects/p1/showback.py` (or a notebook) that reads spans from `.atlas/spans.sqlite` (or Langfuse via the API) and produces `projects/p1/REPORT.md`. You may import from `src/northwind/` (`pricing`, `cost`, `tokens`, `budget`) but **compute the roll-ups yourself** rather than calling `report.weekly_report`; comparing yours with the reference afterwards is part of the learning.

### Functional requirements

| ID | Requirement |
|---|---|
| F1 | **Total cost for the week** computed from generation spans using your own price table (`northwind.pricing` or your own), with cached input tokens billed at the cached price and reasoning tokens as output. Show the total and the cost of the previous week (replay `--start 2026-09-07 --label showback-prev`) with the percentage change. |
| F2 | **Cost by tenant**: a table with requests, sessions, input tokens, output tokens, cache hit ratio, cost, cost per session and share of total, sorted by cost. Four rows plus a total row. |
| F3 | **Cost by feature** (intent / tool family): at minimum `policy_question` (KB only), `ticket` (`lookup_ticket`, `create_ticket`), `password_reset`, `shipment`, `escalated` (any request that used `gpt-4.1`), `other`. Same columns as F2. |
| F4 | **Cost per resolved session**, overall and per tenant, using the `northwind.outcome` attribute (`resolved`, `handed_off`, `failed`, `step_limit`). This is the headline number; explain in one sentence why it differs from cost per session. |
| F5 | **Where the tokens go**: a breakdown of input tokens into system prompt, retrieved context, conversation history and tool results (the mock and the real agent both set `northwind.prompt_breakdown` on each generation), as a percentage of input tokens and of cost. |
| F6 | **Top 10 most expensive sessions** with tenant, steps, model(s), tokens, cost and a one-line explanation of why each was expensive (loop? escalation? long history? oversized tool result?). |
| F7 | **Three recommendations** with the projected weekly saving for each, computed from the data (not guessed), and the risk or quality trade-off of each. At least one must be from the Section 6 toolkit: prompt caching, context diet, small-model-first routing, budgets. |
| F8 | **Reconciliation**: your total must be within 2% of `northwind.cost.total_cost` over the same spans, and the report must state the difference and explain it (rounding, unknown models, price table version). If you are online, also compare with the Langfuse cost dashboard total. |

### Non-functional requirements

| ID | Requirement |
|---|---|
| N1 | The report is **one page** (about 600 words plus tables). Ines will not read page two. |
| N2 | Every number is traceable to a query or a function in your script; no hand-typed numbers. |
| N3 | Prices are pinned and stated in the report ("prices as of 2026-09-28: gpt-4.1-mini $0.40 / $1.60 per 1M, cached $0.10"). |
| N4 | No PII: the report names tenants and features, never employees. If you list a session, use the session id, not the user id. |
| N5 | The script runs in under 60 seconds on the replayed week and is deterministic. |

---

## Acceptance criteria

Your submission is complete when all of these are demonstrably true:

1. `python projects/p1/showback.py --label showback --prev showback-prev` produces `REPORT.md` without errors.
2. The week total reconciles with `northwind.cost.total_cost` within 2% and the report says by how much.
3. The tenant table has four tenants plus a total, and the shares sum to 100% (±0.1).
4. The feature table covers at least the six features in F3 and the `escalated` row shows a cost per request at least 4× the `policy_question` row (the replay guarantees this).
5. Cost per resolved session is shown overall and per tenant, and is higher than cost per session everywhere (since some sessions are not resolved).
6. The token breakdown (F5) shows that system prompt plus retrieved context is more than 50% of input tokens on the baseline replay, which is the argument for caching.
7. The top 10 sessions each have a one-line cause, and at least one is a `step_limit` session.
8. Each of the three recommendations has a projected saving in dollars per week and a stated trade-off, and the three together are worth at least 25% of the weekly total.
9. Cached input tokens are billed at the cached price (a test: change the cached price to equal the input price and the total must go up).
10. No user ids or names appear in the report.

---

## Deliverables

| # | Deliverable | Format |
|---|---|---|
| D1 | `projects/p1/showback.py` (or notebook) | Code in your fork |
| D2 | `projects/p1/REPORT.md` (and optionally a PDF export) | One page |
| D3 | `projects/p1/NOTES.md`: how you reconciled, what surprised you, what you would automate | Half a page |
| D4 | A screenshot of the tenant table next to the Ops Console **Cost** tab (or the Langfuse cost dashboard) showing the same total | Image |

---

## Grading rubric (100 points)

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Cost maths** (20) | 18-20: Correct price table, cached and reasoning tokens handled, escalation model priced separately, reconciles within 2% with the difference explained | 12-17: Reconciles but one of cached/reasoning/escalation is wrong or unexplained | 0-11: Off by more than 5%, or cost computed from a single average price |
| **Attribution** (20) | 18-20: Tenant and feature tables complete, shares sum to 100%, features derived from span attributes with the rule stated | 12-17: Tables present but a feature is missing or the rule for `escalated`/`other` is unclear | 0-11: Only a tenant total, or features guessed |
| **Cost per resolved session** (10) | 9-10: Correct, per tenant, with the one-sentence explanation of the gap to cost per session | 6-8: Present but overall only, or explanation missing | 0-5: Missing or computed as cost per session |
| **Token anatomy and top sessions** (15) | 14-15: Breakdown adds up, top 10 each have a specific cause read from the trace | 9-13: Breakdown present, causes generic ("many tokens") | 0-8: Missing |
| **Recommendations** (20) | 18-20: Three data-backed savings with dollars and trade-offs, totalling ≥25%, at least one verified by re-replaying with the change | 12-17: Three recommendations with estimated savings but no verification or thin trade-offs | 0-11: Generic advice without numbers |
| **Report quality** (10) | 9-10: One page, readable by finance, prices pinned, no PII, every number traceable | 6-8: Slightly long, or one untraceable number | 0-5: Multi-page dump of tables, or PII present |
| **Notes and reflection** (5) | 5: Reconciliation story and a real surprise | 3-4: Present but thin | 0-2: Missing |

**Pass mark:** 70/100.

---

## Hints

1. Start from `CostRecord.from_usage(...)` per generation span, then `rollup(records, by="tenant")` and `rollup(records, by="feature")` from `northwind.cost` to check your own numbers. If yours and theirs differ, the difference is usually the escalation model or cached tokens.
2. The `feature` for a request is on the **agent** span (`northwind.feature`), not on the generation. Join generation cost up to its root span by `trace_id`.
3. `escalated` should take precedence: a ticket request that escalated belongs in `escalated`, otherwise the escalation row understates and the ticket row overstates. State the rule in the report.
4. For the recommendations, do not estimate; **re-replay** the week with the change and diff the totals: `ATLAS_PROMPT_CACHE=1` vs `0`, `ATLAS_CONTEXT_DIET=1` vs `0`, `ATLAS_ROUTER_MODE=1`, `ATLAS_MAX_STEPS=4`. The replay is deterministic, so the diff is the saving. Lecture 6.8's challenge is the same trick.
5. Quality trade-offs need a number too: run the offline judge (`evals.online_judge`) on the before and after replays and quote the `resolved` delta.
6. `showback_table()` in `northwind.cost` produces a Markdown table in the shape finance is used to; use it as a formatting reference, not as your implementation.
7. Write the report headline first: "Atlas cost $X this week, up Y%; HR drove Z% of the increase; we can save $W with three changes." Everything else supports that sentence.

---

## Submission (Udemy assignment)

Submit through the **Project 1: The showback report** assignment in lecture 6.9. The full Udemy entry, including the instructor's example answers, is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste the link to your script and your report. What was the week's total, how close was your reconciliation with `northwind.cost`, and what explained the difference?
2. Paste your three recommendations with the projected weekly saving and the trade-off for each. Which one did you verify by re-replaying, and did the measured saving match your estimate?
3. Describe one thing in the token anatomy or the top-10 sessions that surprised you, and what you would instrument differently because of it.

---

## Peer-review checklist

- [ ] The report fits on one page and opens with a headline sentence a non-engineer understands.
- [ ] Prices are pinned with a date; cached tokens are billed at the cached price.
- [ ] Tenant shares sum to 100%; there is a total row.
- [ ] The `escalated` feature is priced separately and the rule for it is stated.
- [ ] Cost per resolved session is present and higher than cost per session.
- [ ] The token breakdown supports the caching recommendation with a percentage.
- [ ] Each top-10 session has a specific cause, not "many tokens".
- [ ] Each recommendation has a dollar saving, a trade-off, and at least one was measured by re-replay.
- [ ] Reconciliation difference is stated and explained.
- [ ] No employee names or ids anywhere in the report.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
