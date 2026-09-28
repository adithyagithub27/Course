# Project 2: Investigate a Fourth Incident

| Field | Details |
|---|---|
| **Section / lecture** | Section 11, lecture 11.6 (Udemy assignment) |
| **Estimated effort** | 4 to 6 hours |
| **Difficulty** | Intermediate to advanced |
| **Builds on** | Incidents 1 to 3 (lectures 11.2 to 11.4 and `05-projects/challenges.md`), lecture 11.5 (postmortems), Labs 3 to 5 |
| **You will submit** | A blameless postmortem, the queries or notebook you used, and answers to three short questions |

---

## Scenario

It is Thursday 2026-09-24, 16:10. You are on call for Atlas. This page arrives:

> **[PAGE] AtlasCostAnomaly** tenant=warehouse. Hourly spend 3.4× EWMA baseline for 3 consecutive hours. Daily spend projected $61 against a $40 hard cap. Runbook: cost-anomaly.

Ten minutes later, a Slack message from the warehouse operations lead:

> "Not sure if related but Atlas is answering shipment questions fine, people are happy with it, it just feels a bit slower since this morning. We rolled out the new shipment-tracking FAQ to the floor team yesterday, so more people are using it."

And from the Grafana dashboard, at a glance: total requests flat week on week; task success rate 94% (normal); p95 latency 2.9 s (up from 2.2 s, under the 4 s budget); tool error rate normal; judge scores normal; **cost per resolved session for `warehouse` up 60% since 09:00**; the other three tenants flat.

Nothing is red except money. You have the day's spans. Find the root cause, propose the fix, and write the postmortem.

Unlike Incidents 1 to 3, there is **no reveal lecture** for this one. The instructor's solution is only visible after you submit.

---

## The dataset

```text
03-code/incidents/incident-04-project/
├── brief.md            # the page, the Slack message and the dashboard glance above
├── spans.jsonl         # 2026-09-24 00:00 to 18:00, all four tenants, ~31,000 spans
├── metrics.csv         # per-hour Prometheus-style aggregates (requests, cost, p95, tool calls) per tenant
├── releases.txt        # release tags and prompt label changes with timestamps
└── kb-changelog.md     # knowledge base edits in the last 7 days
```

Load it into the local store and the Ops Console:

```bash
uv run python -m telemetry.local_store import incidents/incident-04-project/spans.jsonl --label incident-04
make console        # select label incident-04
```

Or query the JSONL directly with `jq`, `duckdb`, pandas or SQL through `telemetry.local_store query`. All of it is offline.

---

## Requirements

Follow the method from lecture 11.1: **timeline, blast radius, hypotheses, evidence, root cause, contributing factors, fix, prevention.** Use `10-resources/incident-template.md` for the investigation and `10-resources/postmortem-template.md` for the write-up.

| ID | Requirement |
|---|---|
| R1 | **Timeline** with timestamps from the data: when cost per resolved session started rising, when the alert fired, when (if) it plateaued, and every release or KB change in the window. |
| R2 | **Blast radius**: which tenants, which features (intents), which users as a *count* (never ids), what share of the day's spend. |
| R3 | **At least three hypotheses**, each with the query that would confirm or refute it, and the result. Hypotheses that were refuted stay in the document; that is what makes the next investigator faster. |
| R4 | **Root cause** stated in one sentence and supported by at least two independent pieces of evidence from spans (for example: a per-step token attribute and a tool-result size distribution). |
| R5 | **Contributing factors**: what allowed the root cause to become an incident (a missing budget, a missing test, a missing attribute). |
| R6 | **Why nothing was red**: explain, per dashboard panel, why task success, latency, tool errors and judge scores stayed normal while cost rose 60%. |
| R7 | **Immediate fix** you would apply at 16:30 and **the evidence you would watch** to confirm it worked, with an expected value. |
| R8 | **Prevention**: at least three action items that map to course tools (an instrumentation change, a budget or alert change, a CI gate or test), each with an owner role and a check that it was done. |
| R9 | **Cost of the incident**: dollars above baseline for the day, and the projected monthly cost if it had gone unnoticed. |
| R10 | Blameless: no person or team is named as the cause; systems and decisions are. |

---

## Investigation worksheet

Copy this into `projects/p2/INVESTIGATION.md` and fill it in as you go. Reviewers grade the worksheet as well as the postmortem, because the method is the skill.

```markdown
# Incident 4 investigation

## 1. Timeline (from data, not from memory)
| Time | Source | Event |
|---|---|---|
| | metrics.csv | first hour where warehouse cost/resolved session > 1.3× 08:00 value |
| | releases.txt | |
| | kb-changelog.md | |
| | alert | AtlasCostAnomaly fired |

## 2. Blast radius
- Tenants affected:               Share of daily spend:
- Features/intents affected:      Requests affected (count):
- Distinct users affected (count only):
- Did quality or latency budgets breach? (yes/no, numbers)

## 3. Hypotheses
| # | Hypothesis | Query / evidence I will look at | Result | Verdict |
|---|---|---|---|---|
| H1 | More traffic (the FAQ rollout) | requests per hour, warehouse vs others | | |
| H2 | Retry storm / tool errors | tool error rate, retries per request | | |
| H3 | Context bloat (history or tool results) | `northwind.context_tokens` per step; tool result size distribution | | |
| H4 | Model mix changed (escalation / routing) | generations by `gen_ai.request.model` per hour | | |
| H5 | Prompt or KB change | `northwind.prompt_version`, releases.txt, kb-changelog.md | | |
| H6 | (your own) | | | |

## 4. Root cause (one sentence)

## 5. Evidence (at least two independent)
1.
2.

## 6. Why nothing was red
| Panel | Why it stayed normal |
|---|---|
| Task success | |
| p95 latency | |
| Tool error rate | |
| Judge scores | |

## 7. Immediate fix and the number I will watch

## 8. Cost of the incident
- Above-baseline spend on 2026-09-24:
- Projected monthly if unnoticed:
```

Suggested queries (adapt to your tooling):

```sql
-- per-hour cost and cost per resolved session for one tenant
SELECT hour, tenant, sum(cost_usd) cost, sum(cost_usd)/sum(resolved) cost_per_resolved
FROM request_view WHERE tenant='warehouse' GROUP BY hour, tenant;

-- model mix per hour
SELECT hour, json_extract(attributes,'$."gen_ai.request.model"') model, count(*)
FROM spans WHERE name LIKE 'openai.chat%' AND tenant='warehouse' GROUP BY hour, model;

-- tool result size distribution by tool, before vs after 09:00
SELECT json_extract(attributes,'$."gen_ai.tool.name"') tool,
       CASE WHEN start_time < '2026-09-24T09:00' THEN 'before' ELSE 'after' END period,
       avg(length(json_extract(attributes,'$."gen_ai.tool.call.result"'))) avg_chars,
       max(length(json_extract(attributes,'$."gen_ai.tool.call.result"'))) max_chars
FROM spans WHERE name LIKE 'execute_tool%' AND tenant='warehouse' GROUP BY tool, period;

-- context tokens per step
SELECT json_extract(attributes,'$."northwind.step"') step,
       avg(json_extract(attributes,'$."northwind.context_tokens"')) ctx
FROM spans WHERE name LIKE 'atlas.step%' AND tenant='warehouse' AND start_time >= '2026-09-24T09:00'
GROUP BY step;
```

---

## Acceptance criteria

1. The timeline has at least five timestamped rows sourced from the dataset, including the alert and every release/KB change in the window.
2. Blast radius names the tenant(s), the feature(s), a request count and a user count, and states whether any latency or quality budget breached.
3. At least three hypotheses are documented with their query and a verdict; at least one is refuted with evidence.
4. The root cause is one sentence, and two independent span-level facts support it.
5. The "why nothing was red" table has an entry for all four panels, each consistent with the data.
6. The immediate fix names a concrete setting or code change and the metric plus expected value that confirms it.
7. Three prevention items map to course tools (instrumentation, budget/alert, test/gate), each with an owner role and a verification.
8. The incident cost and the projected monthly cost are computed from the data.
9. The document is blameless.
10. The investigation worksheet is included and filled in.

---

## Deliverables

| # | Deliverable | Format |
|---|---|---|
| D1 | `projects/p2/INVESTIGATION.md`: the filled worksheet | Markdown |
| D2 | `projects/p2/POSTMORTEM.md`: the blameless postmortem from `10-resources/postmortem-template.md` (about two pages) | Markdown |
| D3 | `projects/p2/queries/` or a notebook: every query or script behind a number in D1/D2 | Code |
| D4 | Two screenshots or charts: the metric that shows the incident, and the span-level evidence for the root cause | Images |

---

## Grading rubric (100 points)

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Method** (20) | 18-20: Timeline from data, blast radius quantified, hypotheses with queries and verdicts including a refuted one | 12-17: Method followed but a hypothesis lacks its query or the timeline has guessed times | 0-11: Jumped to a conclusion; no worksheet |
| **Root cause and evidence** (25) | 23-25: Correct root cause in one sentence with two independent span-level proofs | 15-22: Correct cause but evidence is aggregate only (metrics.csv) or single-source | 0-14: Wrong cause, or a symptom presented as the cause |
| **Why nothing was red** (10) | 9-10: All four panels explained correctly with numbers | 6-8: Three of four | 0-5: Missing or hand-waved |
| **Fix and verification** (15) | 14-15: Concrete change, the metric to watch, expected value, and a rollback condition | 9-13: Concrete change, vague verification | 0-8: "Optimise the prompt" |
| **Prevention** (15) | 14-15: Three items mapped to instrumentation, budget/alert and test/gate, each with owner role and check | 9-13: Three items but not mapped or unverifiable | 0-8: Fewer than three or generic |
| **Cost of incident** (5) | 5: Daily excess and monthly projection computed | 3-4: One of the two | 0-2: Missing |
| **Writing** (10) | 9-10: Blameless, two pages, a reader who was not there understands it in five minutes | 6-8: Slightly long or one blaming phrase | 0-5: Names people; unreadable |

**Pass mark:** 70/100.

---

## Hints

1. Read `metrics.csv` first and find the hour the slope changes. Then and only then open the spans for that hour and the hour before. Comparing "before" and "after" is the whole game.
2. A cost rise with flat request counts means cost **per request** rose. Cost per request is tokens × price, so either tokens per request rose or the price per token rose (model mix). Check both; they are not mutually exclusive.
3. Tokens per request rise for three reasons in this course: more steps, longer history, or bigger tool results. Step spans (`northwind.context_tokens`) and tool spans (result length) separate them.
4. Anything that changed yesterday is a suspect, but correlation is not cause. The Slack message contains two suspects; test both.
5. The "why nothing was red" section is not filler. If p95 rose only 0.7 s while cost rose 60%, that tells you something about *where* the tokens were (input tokens are cheap in latency and expensive in dollars).
6. Prevention items must be checkable. "Add a test" is not checkable; "add `test_tool_result_under_budget` in `tests/integration/test_spans.py` asserting every tool result attribute is under `tool_result_token_budget`, owner: agent team, verified by CI" is.
7. For the cost of the incident: baseline is the same tenant's mean cost per resolved session over the previous week (there is a `baseline.csv` inside `metrics.csv`'s header comment), times resolved sessions on the day.

---

## Submission (Udemy assignment)

Submit through the **Project 2: Incident 4 postmortem** assignment in lecture 11.6. The full Udemy entry, including the instructor's example answers (visible after you submit), is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste the link to your postmortem and worksheet. State the root cause in one sentence and the two pieces of span-level evidence that support it.
2. Which hypothesis did you refute, and what query refuted it? Why did every dashboard panel except cost stay normal?
3. Paste your three prevention action items with owner role and verification. Which one would have caught this incident earliest, and how many dollars would it have saved on the day?

---

## Peer-review checklist

- [ ] Timeline rows carry timestamps from the dataset, including the alert and the changes in `releases.txt` / `kb-changelog.md`.
- [ ] Blast radius includes a request count and a user count, never user ids.
- [ ] At least one hypothesis is refuted with a query result.
- [ ] Root cause is one sentence and is a cause, not a symptom ("cost went up" is a symptom).
- [ ] Two independent span-level facts support the root cause.
- [ ] "Why nothing was red" covers task success, latency, tool errors and judge scores.
- [ ] The immediate fix names a setting or code path and the metric that confirms it.
- [ ] Prevention items map to instrumentation, budget/alert and test/gate, with owner role and check.
- [ ] Incident cost and monthly projection are computed.
- [ ] No person or team is blamed.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
