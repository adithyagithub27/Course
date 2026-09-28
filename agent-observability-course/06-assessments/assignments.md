# Udemy Assignments

Entries formatted for Udemy's **Assignment** curriculum item (Curriculum → + Curriculum item → Assignment). Each entry maps one-to-one to Udemy's fields:

| Udemy field | Where it comes from below |
|---|---|
| Title | "Title" (80 characters or fewer) |
| Estimated duration | "Estimated duration" (minutes) |
| Instructions (text) | "Instructions" block |
| Instructions: downloadable resource | "Attach" line (upload the project brief exported to PDF) |
| Questions | "Questions" (up to three per assignment, as planned for this course) |
| Solutions: instructor's answer per question | "Instructor example answers" |
| Solutions: video or resource | "Solution resource" line |

| # | Lecture | Assignment | Brief |
|---|---|---|---|
| 1 | 6.9 | Project 1: The showback report | `05-projects/project-1-showback-report.md` |
| 2 | 11.6 | Project 2: Incident 4 postmortem | `05-projects/project-2-incident-postmortem.md` |
| 3 | 14.5 | Capstone: The Atlas Ops Console | `05-projects/capstone-atlas-ops.md` |
| 4 | 14.6 | Domain swap: observe a different agent | `05-projects/capstone-atlas-ops.md` (final section) |

Students submit answers as text in Udemy (links to GitHub, reports and screenshots go inside the answers). After submitting, they see the instructor's example answers and can give and receive peer feedback; the peer-review checklists at the end of each brief are written for that step. Everything can be completed offline (`OFFLINE=1`); no assignment requires API keys.

---

## Assignment 1: Project 1: The showback report

**Title:** Project 1: Build the weekly showback report finance will accept

**Estimated duration:** 300 minutes

**Instructions:**

Northwind's head of finance wants a weekly Atlas cost report by department and by what the agent was doing, with three data-backed recommendations. Produce it from a replayed week of traffic.

1. Replay the week and the previous week offline: `OFFLINE=1 uv run python -m simulator.replay --days 7 --start 2026-09-14 --seed 42 --label showback` and the same with `--start 2026-09-07 --label showback-prev`.
2. Write `projects/p1/showback.py` that reads the spans (`.atlas/spans.sqlite` or Langfuse) and produces `projects/p1/REPORT.md`, one page, with: week total and week-on-week change; cost by tenant (requests, sessions, tokens in/out, cache hit ratio, cost, cost per session, share); cost by feature (`policy_question`, `ticket`, `password_reset`, `shipment`, `escalated`, `other`); cost per resolved session overall and per tenant; the token anatomy of input (system, retrieved context, history, tool results); the ten most expensive sessions with a one-line cause each; three recommendations with projected weekly savings and trade-offs, verified by re-replaying with the change.
3. Reconcile your total with `northwind.cost.total_cost` (within 2%) and state the difference.
4. Compute your own roll-ups; use `northwind.cost` and `northwind.pricing` to check, not to replace, your work. Cached tokens must be priced at the cached rate; the escalation model at its own rate. No employee ids or names in the report.

Full requirements, acceptance criteria and rubric (100 points, pass mark 70): `05-projects/project-1-showback-report.md`.

**Attach:** `project-1-showback-report.pdf`

**Questions:**

1. Paste the link to your script and your report. What was the week's total, how close was your reconciliation with `northwind.cost`, and what explained the difference?
2. Paste your three recommendations with the projected weekly saving and the trade-off for each. Which one did you verify by re-replaying, and did the measured saving match your estimate?
3. Describe one thing in the token anatomy or the top-10 sessions that surprised you, and what you would instrument differently because of it.

**Instructor example answers:**

1. Script and report: `github.com/<instructor>/agent-observability-course/tree/main/projects/p1`. Week total $246.10 (previous week $233.40, +5.4%). My total reconciled with `northwind.cost.total_cost` at $246.10 vs $246.31, a 0.09% difference, explained by two things: I priced the 41 generations whose `gen_ai.response.model` came back as `gpt-4.1-mini-2025-04-14` by normalising the date suffix to `gpt-4.1-mini` (the library does the same, so no gap there), and I rounded per generation to 8 decimal places before summing while `total_cost` sums `Decimal` values first; the residual is rounding. The report states both numbers and the price table date (2026-09-28: gpt-4.1-mini $0.40/$1.60 per 1M, cached $0.10; gpt-4.1 $2.00/$8.00, cached $0.50).
2. (a) **Prompt caching** with a stable prefix and `prompt_cache_key` per tenant: system prompt plus tool schemas are about 2,480 tokens, roughly 62% of the mean input per generation over the week, so caching them at a quarter of the price projected −22%; re-replaying with `ATLAS_PROMPT_CACHE=1` measured −23.1% ($246.10 → $189.20), cache hit ratio 64%; trade-off: none on quality (identical outputs), but savings depend on traffic keeping the prefix warm, so quiet tenants overnight see lower hit ratios. (b) **Context diet** (tool results truncated to 400 tokens, history trimmed to 3,000): tool results were 21% of input tokens and 90% of that was `lookup_ticket` JSON nobody reads; projected −14%, measured −15.7% cumulative; trade-off: judge `resolved` −0.003, and multi-turn HR conversations lose turns older than about 12 exchanges. (c) **Escalation rules tightened** so `gpt-4.1` is used only for `stale_ticket` and `payroll` intents (was also `any tool error`): gpt-4.1 handled 6.1% of generations but 19% of cost; projected −8%, measured −9.8%; trade-off: judge `resolved` −0.004, concentrated in finance. Together −41.5%, comfortably over the 25% the brief asks for. I verified all three by re-replay because the replay is deterministic and it took four minutes; the estimates were within two points each, and the caching estimate was low because tool schemas were cacheable too and I had only counted the system prompt.
3. Seven of the ten most expensive sessions were `step_limit` sessions from one intent, "where is my ticket", where the employee gave a ticket number in a format `lookup_ticket` rejected (`4471` instead of `TCK-4471`), and Atlas retried the same malformed id until the step limit. Each cost about $0.07, more than a successful escalation. I had assumed the expensive tail would be long HR conversations. Because of it I now record `northwind.tool.error_kind` (`not_found`, `malformed`, `upstream`) on tool spans so malformed-argument loops are a filter, not a discovery, and I added a recommendation outside the three: normalise ticket ids in the tool before lookup, which the reference agent now does.

**Solution resource:** Lecture 6.9 walkthrough and `03-code/src/northwind/report.py` (the reference implementation the student was asked not to use until after submitting).

---

## Assignment 2: Project 2: Incident 4 postmortem

**Title:** Project 2: Investigate Incident 4 and write the postmortem

**Estimated duration:** 300 minutes

**Instructions:**

You are on call. A cost anomaly alert fires for the `warehouse` tenant: hourly spend 3.4× baseline for three hours, projected daily spend $61 against a $40 hard cap. Requests are flat, task success and judge scores are normal, tool errors are normal, p95 is up 0.7 s but under budget. The warehouse lead mentions a new shipment-tracking FAQ rolled out yesterday. Nothing is red except money.

1. Load the dataset: `uv run python -m telemetry.local_store import incidents/incident-04-project/spans.jsonl --label incident-04`, then `make console` (or query the JSONL directly). Read `brief.md`, `metrics.csv`, `releases.txt` and `kb-changelog.md`.
2. Follow the method from lecture 11.1 using the investigation worksheet in the brief: timeline from data, blast radius, at least three hypotheses with the query for each and a verdict (keep the refuted ones), root cause in one sentence with two independent span-level proofs, why each dashboard panel stayed normal, immediate fix with the metric that confirms it, three prevention items mapped to instrumentation, budget/alert and test/gate with owner role and verification, and the cost of the incident (daily excess and monthly projection).
3. Write the blameless postmortem (about two pages) from `10-resources/postmortem-template.md`. Name systems and decisions, never people.

There is no reveal lecture for this incident; the instructor's answer appears only after you submit. Rubric (100 points, pass mark 70): `05-projects/project-2-incident-postmortem.md`.

**Attach:** `project-2-incident-postmortem.pdf`

**Questions:**

1. Paste the link to your postmortem and worksheet. State the root cause in one sentence and the two pieces of span-level evidence that support it.
2. Which hypothesis did you refute, and what query refuted it? Why did every dashboard panel except cost stay normal?
3. Paste your three prevention action items with owner role and verification. Which one would have caught this incident earliest, and how many dollars would it have saved on the day?

**Instructor example answers** (instructor only until submission):

1. Postmortem and worksheet: `github.com/<instructor>/agent-observability-course/tree/main/projects/p2`. **Root cause:** the shipment-tracking FAQ rollout sent warehouse staff to `check_shipment`, whose result handler returned the carrier's full raw manifest (about 6,200 tokens per call, previously a 90-token summary because the old FAQ only asked for status) and, because contexts over 2,500 tokens trigger the `long_context` escalation rule, most of those requests were also routed to `gpt-4.1`; so cost per request rose from oversized tool results *and* a shift in model mix, with quality unchanged because the answers were correct. **Evidence 1:** `execute_tool check_shipment` spans for warehouse: mean result length 380 characters before 09:00 on 2026-09-24 and 24,900 after (the `kb-changelog.md` entry at 08:40 the previous day added the manifest link the FAQ now tells users to ask about; `releases.txt` shows no code release). **Evidence 2:** generations by `gen_ai.request.model` per hour for warehouse: `gpt-4.1` share 4% before 09:00, 61% after, with `northwind.escalation_reason=long_context` on 96% of the escalated steps and `northwind.context_tokens` at step 2 averaging 7,400 vs 1,700 before. Cost per resolved session $0.041 → $0.066 (+61%).
2. **Refuted:** H1 "more traffic from the FAQ rollout". Query: requests per hour for warehouse, 2026-09-24 vs the previous three Wednesdays: 41/h vs 39/h, flat; and `check_shipment` calls per request 0.31 vs 0.29. The rollout changed *what* people asked, not how many asked. Also refuted H2 (retry storm): retries per request 0.02, tool error rate 1.1%, both normal. **Why nothing was red:** task success stayed at 94% because the answers were correct (the manifest contains the status); p95 rose only 0.7 s because input tokens are cheap in latency (prefill is fast) and the extra time was the larger model's slower decoding on 60% of requests, not enough to cross 4 s; tool errors were normal because the carrier API succeeded every time, just verbosely; judge scores were normal for the same reason task success was, and `grounded` slightly *improved* because the answer quoted the manifest. Only cost, which is input tokens times price per token, saw both mechanisms at once.
3. (a) **Instrumentation:** add `atlas_tool_result_tokens` histogram per tool and put `northwind.tool_result_tokens` on every tool span (owner: agent team; verified when the Grafana panel shows data and the Lab 2 test asserts the attribute). (b) **Budget/alert:** the EWMA cost anomaly per tenant already fired, but three hours after onset at the hourly grain; add a `tool_result_tokens` p95 alert per tool (> 1,500 for 10 m) and a model-mix alert (escalation share > 20% for 15 m) with runbooks (owner: platform; verified by both firing on the `context_bloat` replay). (c) **Test/gate:** `test_tool_result_under_budget` in `tests/integration/test_spans.py` asserting every tool result attribute is under `tool_result_token_budget` (400) for all five tools including `check_shipment`, which was missing from the parametrised list (owner: agent team; verified by CI). The gate would have caught it earliest: `check_shipment` was never covered by the truncation test, so the manifest bypassed the context diet, and the PR that added the manifest field to the tool would have failed on the day it merged. On 2026-09-24 the excess spend was $24.60 (warehouse $34.10 vs a $9.50 baseline for 09:00 to 18:00); the gate would have saved all of it, and about $740 a month had it gone unnoticed; the immediate fix (truncate `check_shipment` results to 400 tokens with a status-first summary, and exclude `long_context` from escalation reasons when the length comes from tool results) brought cost per resolved session back to $0.043 within the hour, confirmed by `sum(increase(atlas_cost_usd_total{tenant="warehouse"}[1h]))`.

**Solution resource:** `03-code/incidents/incident-04-project/solution.md` (instructor only; not in the student download) and the lecture 11.6 short video on grading the worksheet.

---

## Assignment 3: Capstone: The Atlas Ops Console

**Title:** Capstone: Build the Atlas Ops Console (one-week build-first gate)

**Estimated duration:** 900 minutes

**Instructions:**

Build the complete operations layer for Atlas and prove it under the five failure modes. **Stop watching Section 14 after lecture 14.1a and build for one week before the reference solution** (lectures 14.2 to 14.4).

Required (full list in the brief): complete instrumentation with GenAI attributes and Langfuse observation types including a guardrail; cost attribution with cached and escalation pricing, roll-ups and cost per resolved session; prompt caching, context diet, small-model-first routing and per-tenant budgets (soft cap degrades, hard cap refuses before any LLM call, EWMA anomaly), each measured before/after on the same replayed day; timeouts, bounded retries, idempotent writes, Router fallbacks and a circuit breaker holding p95 under 4 s during `slow_provider`; sampled online judge with three criteria and its cost reported, feedback correlation, drift report, worst-trace-to-dataset promotion; Prometheus metrics with low-cardinality labels, the Grafana Atlas Ops dashboard, three alert rules with runbooks each seen firing; SDK plus collector masking; collector with tail sampling and two exporters; self-hosted Langfuse (or documented Cloud choice); backend chaos survived; CI with a budget gate that blocks a regressing PR; a Streamlit Ops Console; your own one-page weekly ops report; five scenario notes.

Deliver the repository, `ACCEPTANCE.md` (24 tests with PASS/FAIL and evidence; at least 15 to pass, 20 for Excellent), `REPORT-week.md`, `INCIDENTS.md`, screenshots or a short recording, your architecture diagram, `DIFF_NOTES.md` after watching the reference, and the portfolio README. Rubric (100 points, pass mark 70, distinction 90 with 22 tests): `05-projects/capstone-atlas-ops.md`.

**Attach:** `capstone-atlas-ops.pdf`

**Questions:**

1. Paste links to your repository, `ACCEPTANCE.md` and `REPORT-week.md`. How many of the 24 acceptance tests pass, and did you complete the one-week build before watching the reference solution (yes / partly / no)?
2. Pick one of the five scenarios. Show how your stack detected it (which signal, how long after onset) and how it was contained (which control), with the evidence.
3. Paste the "Decisions and trade-offs" section of your README, and one item from `DIFF_NOTES.md` where the reference solution changed your mind (or where you kept your own approach, and why).

**Instructor example answers:**

1. Repository: `github.com/<instructor>/agent-observability-course` (the `03-code/` reference). `ACCEPTANCE.md`: 23 of 24 pass. AT-12 (routing) fails in the reference at the stated tolerance: with `ATLAS_ROUTER_MODE=1` the gpt-4.1 share is 3.4% (pass) but judge `resolved` drops 0.021 rather than the 0.02 allowed; the write-up keeps the failure honest and notes the two rules (`stale_ticket`, `payroll`) that would need loosening to recover it at a 2% cost. Gate respected: yes; the reference was built from the brief before the solution lectures were recorded, and `DIFF_NOTES.md` compares it with the Lab and Challenge solutions.
2. **`prompt_regression`.** Detected by the weekly drift report (judge `grounded` PSI 0.19, answer-length PSI 0.31) and, in the same replay, by the thumbs-down-rate drift alert (1.4% → 2.0%), 36 hours after v2 was promoted; no cost, latency or error signal moved (cost fell 8%). Contained by moving the Langfuse `production` label back to `atlas-system` v1 (no deploy; picked up within `cache_ttl_seconds=60`), verified by the judge on the next simulated day: `grounded` 0.89. Evidence: `INCIDENTS.md#prompt-regression` with the drift table, the by-`prompt_version` breakdown (v1 0.90 vs v2 0.77), the Langfuse prompt history screenshot showing the label move, and the post-rollback judge run. Prevention added: offline eval on `atlas-failures` as a required check before any label move to `production`.
3. *Decisions:* (1) Manual `gen_ai.*` spans for generations rather than OpenInference auto-instrumentation, because Atlas needs step spans and escalation attributes around each call and having one source of truth per layer avoided double counting; the cost was about 60 lines of `genai_attrs` helpers. (2) Tail sampling in the collector (100% errors, 20% rest) instead of SDK head sampling, because Lab 7 showed head sampling at 20% keeps about 14 of 70 error traces; the cost is running the collector and a 10 s decision wait. (3) Fallback to `gpt-4.1-nano`, never to `gpt-4.1`: p95 3,420 ms in `slow_provider` with cost per session $0.0388, at a `grounded` cost of −0.07 during the two-hour window, documented in the runbook as expected degraded-mode behaviour. *What did not work:* an early version checked the hard cap after the first model call; AT-14 caught it (one mock call per refusal), and moving `BudgetGuard.decide()` ahead of the loop fixed it. *DIFF note:* my Quality page averaged judge scores over all judged traces; the reference filters `sample_reason == "uniform"` for headlines and uses the tail extras only for the worst-N table. I adopted it after seeing my weekly `resolved` swing by 0.04 between an incident week and a quiet week for no real reason.

**Solution resource:** Lectures 14.2 to 14.4 and `03-code/` (console, evals, deploy, tests, `src/northwind/report.py`).

---

## Assignment 4: Domain swap: observe a different agent

**Title:** Domain swap: instrument a different agent with the same stack

**Estimated duration:** 480 minutes

**Instructions:**

Prove the stack is not Atlas-specific. Choose one: (A) Riley, the voice receptionist from *Production Voice AI Agents*; (B) your own agent (must make at least one LLM call and one tool call per request and be runnable offline with a stub); (C) an open-source coding or data agent.

Carry over unchanged: OpenTelemetry spans with GenAI semantic conventions exported to a viewable backend with sessions, users and a tenant-like dimension; cost per generation from a pinned price table rolled up by two dimensions with the domain's cost-per-resolved-unit as headline; one hard-cap budget that refuses before spending and one anomaly detector; Prometheus metrics with low-cardinality labels and one alert with a runbook; a sampled online judge with two domain-specific criteria and its cost reported; one injected failure detected and contained.

Document what changed with `10-resources/instrumentation-template.md`: the SLIs that no longer apply and what replaces them, the unit of spend and what "degrade" means here, the PII the domain adds and how the mask changed, and two judge criteria that would be meaningless for Atlas. Deliver the repository or folder, one trace screenshot with GenAI attributes, one cost roll-up, one dashboard or console screenshot with the adapted SLIs, `INCIDENT.md`, and a half-page reflection. Self-check rubric (20 points, pass at 14): final section of `05-projects/capstone-atlas-ops.md`.

**Attach:** `capstone-atlas-ops.pdf` (the domain-swap section) and `instrumentation-template.pdf`.

**Questions:**

1. Which agent did you instrument, and what is its cost-per-resolved-unit? Paste the trace screenshot link showing `gen_ai.*` attributes and the cost roll-up table.
2. Which SLIs from Atlas did you drop or replace, and what did "degrade" mean in your domain when the soft cap was hit?
3. Describe the failure you injected: how it was detected (signal and delay), how it was contained, and one judge criterion you wrote that would be meaningless for Atlas.

**Instructor example answers:**

1. Riley, the Course 3 voice receptionist (Maple Street Dental), option A. Headline unit: **cost per completed booking call**, $0.19 on a replayed set of 60 calls, made of LLM tokens ($0.04, with 71% of prompt tokens cached because the receptionist prompt is stable), STT ($0.03), TTS ($0.09) and telephony minutes ($0.03). Trace: `docs/riley-trace.png` shows `gen_ai.operation.name=chat`, `gen_ai.request.model=gpt-4.1-mini`, usage with cached tokens, and the `find_available_slots` tool span with `gen_ai.tool.call.arguments` masked (phone number as `[PHONE]`); the agent span carries `gen_ai.agent.name=riley` and the call's `session_id` is the LiveKit room name. Roll-up: by clinic (the tenant-like dimension: two demo clinics) and by call outcome (`booked`, `rescheduled`, `faq_only`, `transferred`, `abandoned`), with `abandoned` calls at $0.11 each and 0 resolved, which is why cost per completed booking ($0.19) is 40% above cost per call ($0.135).
2. Dropped: task success as "the agent said it resolved it" (meaningless for a phone call) and tokens per step. Replaced with: booking completion rate (a booking committed and read back), voice-to-voice p95 (≤ 1,600 ms) in place of end-to-end p95, time-to-first-audio in place of TTFT, transfer rate as the containment SLI, and cost per completed booking call in place of cost per resolved session. Kept unchanged: tool error rate and judge score. "Degrade" at the soft cap: switch TTS to the cheaper voice tier and the LLM to `gpt-4.1-nano` for FAQ-only turns while keeping the booking tools on the mini model, because a cheaper voice is noticeable but harmless and a wrong booking is not; at the hard cap, Riley says the line is busy and offers the front desk number, with no LLM, STT or TTS spend beyond the fixed message.
3. Injected `slow_provider` on the LLM during a replayed lunch peak. Detected by the time-to-first-audio p95 alert (> 900 ms for 2 m) four minutes after onset, before any caller complaint in the simulated transcripts. Contained by the LLM fallback to `gpt-4.1-nano` with a 2.5 s timeout (voice cannot afford Atlas's 4 s), fallback rate 64% in the window, voice-to-voice p95 held at 1,480 ms; judge `read_back_before_commit` unchanged at 0.97, `speakability` down 0.04 (nano used a digit string once). Judge criterion meaningless for Atlas: **"Before any booking is committed, the assistant reads back name, day, date and time and receives an explicit yes"**, scored on the transcript, threshold 0.9. A text helpdesk agent never reads anything back; a phone agent that skips it books the wrong day. Judge cost: $0.21 for the 60-call set at 100% sampling, 2.3% of the calls' cost; at production volume it would run at 10% tail-weighted sampling.

**Solution resource:** Lecture 14.6 and `10-resources/instrumentation-template.md`; the Course 3 repo's `agents/s13_capstone_receptionist.py` with the Course 4 telemetry package applied (`examples/domain-swap-riley/` in the reference repository).
