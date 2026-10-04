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

Northwind's head of finance wants a weekly Atlas cost report by department and by what the agent was doing, headlined by cost per resolved session, with three recommendations that each carry a number and a saving. Produce it from the replayed day (it stands in for the week).

1. Replay the baseline day and render the reference report: `cd 03-code && OFFLINE=1 make replay && make report`. The headline is $56.28 for 4,000 sessions and 10,184 requests; the report has showback tables by tenant, by feature and by model.
2. Replay at least two lever configurations into their own stores for the trend, for example `OFFLINE=1 make replay DIET=1 STORE=.atlas/diet.sqlite` then `make report STORE=.atlas/diet.sqlite`, and the same with `CACHE=1`. Without `STORE=` every replay overwrites `.atlas/spans.sqlite`.
3. Write `projects/p1/REPORT.md`, one page: total cost, cost per session and cost per resolved session with the resolved rate; cost by tenant (`ops`, `finance`, `hr`, `eng`) and by feature (`policy_question`, `create_ticket`, `ticket_lookup`, `shipment_status`, `password_reset`, `escalation`, `other`); the trend across your stores; three recommendations, each citing a number from the report, a monthly saving and a trade-off.
4. Date your prices and mark them "verify current pricing". No employee ids or names in the report.

Full requirements and rubric (100 points, pass mark 70): `05-projects/project-1-showback-report.md`.

**Attach:** `project-1-showback-report.pdf`

**Questions:**

1. Paste your report (or a link to it). What is the day's total, the cost per resolved session and the resolved rate, and which tenant has the highest cost per session and why?
2. Paste your three recommendations, each with the cited number, the monthly saving and the trade-off. Which one did you verify with a re-replay into its own store, and what did it measure?
3. Which comparison stores did you build, and what did the trend across them tell you that the baseline alone did not?

**Instructor example answers:**

1. Report: `github.com/<instructor>/agent-observability-course/tree/main/projects/p1/REPORT.md`. The replayed day costs $56.28 for 4,000 sessions: $0.0141 per session and $0.0144 per resolved session, so about 98% of sessions resolve; the rest are guardrail refusals and the 43 escalations to a person. Finance has the highest cost per session ($0.0166) because payroll and expense questions retrieve more policy text; ops is the biggest tenant ($20.27, 36.0%) only because it has 43% of the sessions, and its cost per session is the lowest ($0.0119). No department is misusing Atlas; the cost is structural. Prices dated 2026-10-02 (gpt-4.1-mini $0.40 / $1.60 per 1M, cached $0.10; gpt-4.1 $2.00 / $8.00), verify current pricing.
2. (a) **Prompt caching**: the baseline's cache hit ratio is 0% (the report's own recommendation). `make replay CACHE=1 STORE=.atlas/cache.sqlite` measured $37.00 (−34%), about $580 a month; trade-off: none on the answers, but the saving depends on traffic keeping the prefix warm. (b) **Context diet**: `policy_question` is 76.2% of the bill ($42.91) because whole articles and untrimmed history ride along; the diet replay measured $41.99 (−25%), about $430 a month, with the offline judge unchanged; trade-off: a real model may miss exception clauses if the tool budget is cut much further, so grounded is the score to watch. (c) **Small-model-first routing** for the simple intents (`create_ticket`, `ticket_lookup`, `shipment_status`): `ROUTER=1` measured $47.07 alone and $19.07 with (a) and (b), a further $3.64 a day; trade-off: a smaller model answers a third of the generations, so track grounded by intent. Verified all three by re-replay; together the day goes from $56.28 to $19.07 (−66%).
3. Baseline, cache, diet, cache + diet ($22.71) and all three ($19.07), side by side on the Compare replays page. The trend showed that caching and the diet add almost exactly ($19.28 + $14.29 ≈ $33.57 saved together) while routing on top saves much less than alone ($3.64 vs $9.21), because there is less expensive spend left to move. Measuring in shipping order, not each against baseline, is what made the third recommendation honest.

**Solution resource:** Lecture 6.9 walkthrough and `03-code/src/northwind/report.py` (the reference implementation the student was asked not to use until after submitting).

---

## Assignment 2: Project 2: Incident 4 postmortem

**Title:** Project 2: Investigate Incident 4 and write the postmortem

**Estimated duration:** 300 minutes

**Instructions:**

You are on call on Monday 2026-09-14. Two pages arrive: at 10:35 `AtlasToolErrorRate` for `lookup_ticket` (error rate above 5% for 10 minutes; every tenant that looks up tickets is affected, and several sessions hit the step limit), and at 15:20 `AtlasLatencyP95High` (p95 roughly double the morning, cost per request up a little, tool errors normal again). Nobody deployed anything. The team lead wants one postmortem covering both pages, and an answer to whether they are related.

1. Load the dataset: `make incident N=4` (text console over `incidents/incident-04-project/spans.jsonl` and `scores.jsonl`), or `LocalSpanStore.from_jsonl(...)` in your own script. Read `brief.md`.
2. Follow the method from lecture 11.1 using the investigation worksheet in the brief: timeline from data for both pages, blast radius, at least three hypotheses with the query for each and a verdict (keep the refuted ones), root cause in one sentence per page with two independent span-level proofs each, whether the pages are related, why each dashboard panel looked the way it did in each window, immediate fixes with the metric that confirms them, three prevention items mapped to instrumentation, budget/alert and test/gate with owner role and verification, and the cost of the incident per window.
3. Write the blameless postmortem (about two pages) from `10-resources/postmortem-template.md`. Name systems and decisions, never people.

There is no reveal lecture for this incident; the instructor's answer appears only after you submit. Rubric (100 points, pass mark 70): `05-projects/project-2-incident-postmortem.md`.

**Attach:** `project-2-incident-postmortem.pdf`

**Questions:**

1. Paste the link to your postmortem and worksheet. State the root cause of each page in one sentence, say whether they are related, and give the span-level evidence that supports each.
2. Which hypothesis did you refute, and what query refuted it? Why did the afternoon page show no tool errors, and why did the morning page barely move p95?
3. Paste your three prevention action items with owner role and verification. Which one would have caught the morning page earliest, and how many dollars would it have saved on the day?

**Instructor example answers** (instructor only until submission):

1. Postmortem and worksheet: `github.com/<instructor>/agent-observability-course/tree/main/projects/p2`. **Root cause, page 1 (10:00-12:00, every tenant):** the ticket service became flaky (two timeouts, then success); `lookup_ticket` returned `{"error": "ticket_service_timeout", "retry": true}`, the model obliged and re-called the tool, and with `ATLAS_MAX_TOOL_RETRIES=0` (unlimited) nothing stopped it except success on the third call, so affected requests show three `execute_tool lookup_ticket` spans (two `ERROR`, one `OK`), four steps, and three to four times the tokens and cost of a normal ticket lookup. **Root cause, page 2 (15:00-16:00, every tenant):** a provider slowdown on about half of the model calls: TTFT ×3.5 and tokens per second halved for the same model and similar token counts, so p95 roughly doubled while cost per request rose only slightly (the affected mix skews to longer answers). **They are unrelated.** **Evidence 1 (page 1):** tool spans with `gen_ai.tool.name="lookup_ticket"` and `error.type="ticket_service_timeout"`, three per trace between 10:00 and 12:00 versus one before, and `atlas.steps` at 4 (or the limit) on the same traces. **Evidence 2 (page 2):** `gen_ai.response.time_to_first_chunk` / `atlas.ttft_ms` on generation spans by hour, ×3.5 from 15:00 with `gen_ai.usage.input_tokens` and `gen_ai.request.model` unchanged, and `lookup_ticket` error share back at baseline.
2. **Refuted:** H6 "the two pages share one cause". Query: for the afternoon's slow traces (agent spans with `duration_ms` over the budget between 15:00 and 16:00), the share that call `lookup_ticket` and its error share are at the day's baseline, and TTFT is high across every intent and tenant; for the morning window, TTFT per generation is normal. Also refuted H1 (more traffic): requests per hour per tenant follow the normal Monday shape. **Why the panels looked the way they did:** in the morning, tool errors were the signal, latency moved only modestly because each individual model call was fast, just repeated, and cost per request rose sharply for ticket lookups because every retry re-sent the whole prompt; in the afternoon, tools were fine, the time went into the model's first token and decode, and cost per request rose only a little because slower is not more tokens. Judge scores stayed normal in both windows because the eventual answers were correct.
3. (a) **Instrumentation:** `atlas.retries` and `atlas.steps` are already on the spans; add a per-tool retry counter (`atlas_tool_retries_total{tool}`) next to `atlas_tool_calls_total` in `telemetry/metrics.py` (owner: agent team; verified when the Grafana panel shows data). (b) **Budget/alert:** `AtlasToolErrorRate` fired, but ten minutes after the error share crossed 5%: tighten `for:` to 5 minutes and add a `tool_success` SLO (99%) with a 1-hour burn-rate page at 14.4 in `deploy/alerts.yml`; add a TTFT p95 alert per model on `atlas_ttft_seconds` (1.5 s for 10 minutes) so provider slowness is named as such (owner: platform; verified by both firing on `make run PROM=1 SCENARIO=ticket_flaky` / `SCENARIO=slow_provider` with `make swarm`). (c) **Test/gate:** set `ATLAS_MAX_TOOL_RETRIES=2` and surface the tool error to the user (lecture 5.6, `app/agent.py`), with `test_tool_retries_are_bounded` in `tests/unit/test_agent.py` asserting at most three `execute_tool` spans for the `ticket_flaky` scenario, and a `BUDGET_GATE_INCIDENTS=mixed` run of `tests/budget/test_budget_gate.py` in CI (owner: agent team; verified by CI). The retry bound would have caught the morning page earliest: it turns a four-step, triple-billed ticket lookup back into a normal one, so the excess is the extra two generations on every affected request, roughly two thirds of the `atlas.cost_usd` on `lookup_ticket` traces between 10:00 and 12:00 (compute the dollar figure from `spans.jsonl`; the grading key does). For the afternoon, the fix is the circuit breaker and `FALLBACKS` in `app/agent.py` (or the Router's `cooldown_time`) plus a tighter `ATLAS_REQUEST_TIMEOUT_S`, confirmed by `atlas_model_fallbacks_total` rising while p95 stays under 4 s.

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
