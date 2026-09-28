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

It is Monday 2026-09-14. You are on call for Atlas. Two pages arrive in one day:

> **10:35 [PAGE] AtlasToolErrorRate** tool=`lookup_ticket`. Tool error rate above 5% for 10 minutes. Runbook: tool-errors.

> **15:20 [PAGE] AtlasLatencyP95High**. Atlas p95 latency above 4 s for 10 minutes. Runbook: latency.

What on-call sees on the Grafana dashboard and in the Ops Console:

- `atlas_tool_calls_total{tool="lookup_ticket",outcome="error"}` spikes between 10:00 and 12:00; every tenant that looks up tickets is affected.
- Several sessions in that window have many `step` spans and `atlas.steps` at or near the limit (`ATLAS_MAX_STEPS`, 6).
- Between 15:00 and 16:00, p95 latency is roughly double the morning; cost per request is up a little; tool errors are normal again.
- Nobody deployed anything.

The team lead wants **one postmortem covering both pages**, and wants to know whether they are related. You have the day's spans and scores. Find the root cause of each page, decide whether they share one, propose the fixes, and write the postmortem.

Unlike Incidents 1 to 3, there is **no reveal lecture** for this one. The instructor's solution is only visible after you submit.

---

## The dataset

```text
03-code/incidents/incident-04-project/
├── brief.md            # the two pages and the dashboard glance above
├── spans.jsonl         # Monday 2026-09-14, 00:00 to 24:00, all four tenants (ops, finance, hr, eng)
└── scores.jsonl        # judge scores (sampled) and user feedback for the same traces
```

(`solution.md` exists in the instructor repo only; `make student-repo` strips it.)

Load it into the text Ops Console, or into a store you can query:

```bash
cd 03-code
make incident N=4        # temporary store + text console: hourly cost, p95, tool errors and the alerts that would fire
```

```python
from telemetry.local_store import LocalSpanStore
d = "incidents/incident-04-project/"
store = LocalSpanStore.from_jsonl(d + "spans.jsonl", d + "scores.jsonl")
store.count(), store.tool_stats(), store.time_range()
```

`LocalSpanStore` is SQLite underneath (`spans` and `scores` tables, one row per span with `tenant`, `session_id`, `model`, `tool`, `intent`, `outcome`, token counts, `cost_usd`, `duration_ms` and the full `attributes` JSON), so `sqlite3`, pandas or DuckDB work too. All of it is offline.

---

## Requirements

Follow the method from lecture 11.1: **timeline, blast radius, hypotheses, evidence, root cause, contributing factors, fix, prevention.** Use `10-resources/incident-template.md` for the investigation and `10-resources/postmortem-template.md` for the write-up.

| ID | Requirement |
|---|---|
| R1 | **Timeline** with timestamps from the data for both pages: when `lookup_ticket` errors started and stopped, when each alert fired, when p95 started climbing and when it recovered, and any change you can find (there is no deploy). |
| R2 | **Blast radius**: which tenants, which features (intents), which users as a *count* (never ids), what share of the day's spend. |
| R3 | **At least three hypotheses**, each with the query that would confirm or refute it, and the result. Hypotheses that were refuted stay in the document; that is what makes the next investigator faster. |
| R4 | **Root cause** stated in one sentence and supported by at least two independent pieces of evidence from spans (for example: a per-step token attribute and a tool-result size distribution). |
| R5 | **Contributing factors**: what allowed the root cause to become an incident (a missing budget, a missing test, a missing attribute). |
| R6 | **Are the two pages one incident?** Decide, with evidence, whether the 10:35 page and the 15:20 page share a cause. Explain, per dashboard panel, why the morning shows tool errors but only a modest latency change and why the afternoon shows latency but no tool errors. |
| R7 | **Immediate fix** for each page (at 10:45 and at 15:30) and **the evidence you would watch** to confirm it worked, with an expected value. |
| R8 | **Prevention**: at least three action items that map to course tools (an instrumentation change, a budget or alert change, a CI gate or test), each with an owner role and a check that it was done. |
| R9 | **Cost of the incident**: dollars above baseline for each window (the morning's re-billed tool retries; the afternoon's slower, longer generations), and what one such day a week would cost in a month. |
| R10 | Blameless: no person or team is named as the cause; systems and decisions are. |

---

## Investigation worksheet

Copy this into `projects/p2/INVESTIGATION.md` and fill it in as you go. Reviewers grade the worksheet as well as the postmortem, because the method is the skill.

```markdown
# Incident 4 investigation

## 1. Timeline (from data, not from memory)
| Time | Source | Event |
|---|---|---|
| | spans.jsonl | first hour where `lookup_ticket` error share > 5% |
| | alert | AtlasToolErrorRate fired (10:35) |
| | spans.jsonl | `lookup_ticket` error share back to baseline |
| | spans.jsonl | first hour where p95 > 4 s |
| | alert | AtlasLatencyP95High fired (15:20) |
| | spans.jsonl | p95 back under 4 s |

## 2. Blast radius
- Tenants affected (per page):      Share of daily spend:
- Intents affected (per page):      Requests affected (count):
- Distinct users and sessions affected (count only):
- Did quality or latency budgets breach? (yes/no, numbers)

## 3. Hypotheses
| # | Hypothesis | Query / evidence I will look at | Result | Verdict |
|---|---|---|---|---|
| H1 | More traffic | requests per hour, per tenant | | |
| H2 | Tool retry storm | `execute_tool lookup_ticket` spans per trace, `error.type`, `atlas.steps` on the agent span | | |
| H3 | Context bloat (history or tool results) | `atlas.context_tokens` per step; `gen_ai.usage.input_tokens` per generation | | |
| H4 | Model mix changed (escalation / routing) | generations by `gen_ai.request.model` per hour | | |
| H5 | Provider slowdown | `gen_ai.response.time_to_first_chunk` / `atlas.ttft_ms` per hour, output tokens per second | | |
| H6 | The two pages share one cause | do the afternoon's slow traces call `lookup_ticket`? is the morning's TTFT normal? | | |
| H7 | (your own) | | | |

## 4. Root cause (one sentence per page, and whether they are related)

## 5. Evidence (at least two independent, per page)
1.
2.

## 6. Why each panel looked the way it did
| Panel | 10:00-12:00 | 15:00-16:00 |
|---|---|---|
| Tool error rate | | |
| p95 latency | | |
| Cost per request | | |
| Judge scores | | |

## 7. Immediate fixes and the numbers I will watch

## 8. Cost of the incident
- Above-baseline spend 10:00-12:00:
- Above-baseline spend 15:00-16:00:
- One such day a week, per month:
```

Suggested queries (Python against the store; adapt to pandas or SQL if you prefer):

```python
from collections import Counter, defaultdict
from datetime import UTC, datetime
from northwind.latency import percentile

hour = lambda s: datetime.fromtimestamp(s.start_time, tz=UTC).hour

# tool calls and errors per hour and tool
calls, errors = Counter(), Counter()
for s in store.spans(kind="tool"):
    key = (hour(s), s.attr("gen_ai.tool.name"))
    calls[key] += 1
    if s.status == "ERROR":
        errors[key] += 1

# lookup_ticket calls per trace, and steps per request, in the morning window
per_trace = Counter(s.trace_id for s in store.spans(kind="tool") if s.attr("gen_ai.tool.name") == "lookup_ticket")
steps = {a.trace_id: a.attr("atlas.steps") for a in store.spans(kind="agent")}

# p95 end-to-end latency and TTFT per hour
lat, ttft = defaultdict(list), defaultdict(list)
for a in store.spans(kind="agent"):
    lat[hour(a)].append(a.duration_ms)
for g in store.spans(kind="generation"):
    if g.attr("atlas.ttft_ms") is not None:
        ttft[hour(g)].append(g.attr("atlas.ttft_ms"))
p95_by_hour = {h: percentile(v, 95) for h, v in sorted(lat.items())}

# judge scores by hour
by_hour = defaultdict(list)
for sc in store.scores(name="judge_overall"):
    by_hour[datetime.fromtimestamp(sc.timestamp, tz=UTC).hour].append(sc.value)
```

---

## Acceptance criteria

1. The timeline has at least six timestamped rows sourced from the dataset, including both alerts and the start and end of each window.
2. Blast radius names the tenant(s), the feature(s), a request count and a user count, and states whether any latency or quality budget breached.
3. At least three hypotheses are documented with their query and a verdict; at least one is refuted with evidence.
4. The root cause is one sentence, and two independent span-level facts support it.
5. The "why each panel looked the way it did" table has an entry for all four panels in both windows, and the document states whether the two pages are related, consistent with the data.
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
| **Root cause and evidence** (25) | 23-25: Correct root cause for each page in one sentence, the relation between the pages decided, with two independent span-level proofs each | 15-22: Correct causes but evidence is aggregate only (console output) or single-source | 0-14: Wrong cause, the two pages treated as one without evidence, or a symptom presented as the cause |
| **Panels and the relation between the pages** (10) | 9-10: All four panels explained for both windows with numbers | 6-8: Three of four | 0-5: Missing or hand-waved |
| **Fix and verification** (15) | 14-15: Concrete change, the metric to watch, expected value, and a rollback condition | 9-13: Concrete change, vague verification | 0-8: "Optimise the prompt" |
| **Prevention** (15) | 14-15: Three items mapped to instrumentation, budget/alert and test/gate, each with owner role and check | 9-13: Three items but not mapped or unverifiable | 0-8: Fewer than three or generic |
| **Cost of incident** (5) | 5: Daily excess and monthly projection computed | 3-4: One of the two | 0-2: Missing |
| **Writing** (10) | 9-10: Blameless, two pages, a reader who was not there understands it in five minutes | 6-8: Slightly long or one blaming phrase | 0-5: Names people; unreadable |

**Pass mark:** 70/100.

---

## Hints

1. Run `make incident N=4` first: the text console prints hourly cost, p95 and tool errors and the alerts that would fire. Find the two windows. Then and only then open the spans for each window and the hour before it. Comparing "before" and "after" is the whole game.
2. A tool error rate spike with flat request counts means something per request changed. Count `execute_tool lookup_ticket` spans per trace and read `error.type` and `gen_ai.tool.call.result` on the failed ones; then read `atlas.steps` on the agent span. What does Atlas do after a tool error, and what stops it (`ATLAS_MAX_TOOL_RETRIES`, lecture 5.6)?
3. A p95 rise with normal tool errors and only a slightly higher cost per request points at the model calls: compare `gen_ai.response.time_to_first_chunk` / `atlas.ttft_ms` and output tokens per second before and after 15:00, for the same model and similar token counts. Slower is not more tokens.
4. "Related" is a hypothesis, not a fact. Two pages on one day feel like one incident; test it with the data: do the afternoon's slow traces involve `lookup_ticket`? Is the morning's TTFT normal?
5. Prevention items must be checkable. "Add a test" is not checkable; "set `ATLAS_MAX_TOOL_RETRIES=2` and add `test_tool_retries_are_bounded` in `tests/unit/test_agent.py` asserting at most three `execute_tool` spans for the `ticket_flaky` scenario, owner: agent team, verified by CI" is.
6. For the cost of the incident: baseline is the same tenant and intent outside the window. A tool retry re-bills the whole prompt, so count the extra generations and their `gen_ai.usage.input_tokens`; for the afternoon, compare `atlas.cost_usd` per request with the morning's for the same intents.
7. Blameless: "the model kept retrying" is a system behaviour with a missing bound, not a character flaw.

---

## Submission (Udemy assignment)

Submit through the **Project 2: Incident 4 postmortem** assignment in lecture 11.6. The full Udemy entry, including the instructor's example answers (visible after you submit), is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Paste the link to your postmortem and worksheet. State the root cause of each page in one sentence, say whether they are related, and give the span-level evidence that supports each.
2. Which hypothesis did you refute, and what query refuted it? Why did the afternoon page show no tool errors, and why did the morning page barely move p95?
3. Paste your three prevention action items with owner role and verification. Which one would have caught the morning page earliest, and how many dollars would it have saved on the day?

---

## Peer-review checklist

- [ ] Timeline rows carry timestamps from the dataset, including both alerts and the start and end of each window.
- [ ] Blast radius includes a request count and a user count, never user ids.
- [ ] At least one hypothesis is refuted with a query result.
- [ ] Each page has a one-sentence root cause that is a cause, not a symptom ("tool errors went up" is a symptom), and the relation between the pages is decided with evidence.
- [ ] Two independent span-level facts support the root cause.
- [ ] The panel table covers tool errors, latency, cost per request and judge scores for both windows.
- [ ] The immediate fix names a setting or code path and the metric that confirms it.
- [ ] Prevention items map to instrumentation, budget/alert and test/gate, with owner role and check.
- [ ] Incident cost and monthly projection are computed.
- [ ] No person or team is blamed.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
