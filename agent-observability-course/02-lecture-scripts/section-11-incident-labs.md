# Section 11: Incident Labs: You Are On Call

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈55 min (7 lectures, curriculum v1.0). Engagement centrepiece: three detective incidents with an explicit investigation pause before each reveal.
> **Source of truth:** `01-curriculum/curriculum.md`; incident presets in `03-code/simulator/scenarios.py::INCIDENT_PRESETS` (`cost_spike`, `latency_regression`, `quality_drift`, `mixed`); datasets in `03-code/incidents/`; templates in `10-resources/incident-template.md` and `10-resources/postmortem-template.md`; project brief `05-projects/project-2-incident-postmortem.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / langsmith 0.14; check the repo README for updates."
> **Recording note:** 11.2, 11.3 and 11.4 are each recorded as **Part A** (brief and evidence, ending on the investigation pause) and **Part B** (reveal, fix, prevention). Upload as two videos each so the pause is a natural stopping point and each file stays under ten minutes.
> **Code status at scripting time:** `simulator/scenarios.py`, `app/agent.py`, `app/prompts.py`, `app/mock_llm.py`, `src/northwind/*` and `telemetry/*` exist and the scripts match their names and mechanisms. `incidents/*/brief.md`, `solution.md` and `spans.jsonl` were not yet generated: the numbers below are the reference for generating them (`generate_day(seed=7, sessions=4000, incidents=INCIDENT_PRESETS[...])`). If the generated data differs, update the numbers here, not the story.

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with Atlas, the Ops Console or Langfuse. Record the real screen. |
| `[EVIDENCE n: ...]` | An exhibit the student can open themselves from the incident dataset. Show it, name where it lives, do not interpret it yet. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |
| `[PAUSE: investigate for 8 minutes]` | Hard stop. On-screen timer card. The student pauses the video and investigates. Part A ends here. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only (narration plus scripted demo dialogue), not cues, code, tables or slide text.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 11.1 | How to read an incident like an SRE | SL | 6:00 | ~885 |
| 11.2 | Incident 1: Monday's cost spike (Part A / Part B) | CH | 12:00 (4:00 + 8:00) | ~1,680 |
| 11.3 | Incident 2: p95 doubled after lunch (Part A / Part B) | CH | 12:00 (4:00 + 8:00) | ~1,395 |
| 11.4 | Incident 3: users are unhappy but nothing is red (Part A / Part B) | CH | 12:00 (4:00 + 8:00) | ~1,469 |
| 11.5 | Writing the postmortem | SC | 7:00 | ~730 |
| 11.6 | Project 2: Investigate a fourth incident | AS | 3:00 | ~389 |
| 11.7 | Quiz: Incident response | QZ | 3:00 (1:00 video intro) | ~114 |

**Names used in this section (match `03-code/`).** Tenants (`northwind.config.TENANTS`): `ops`, `finance`, `hr`, `eng` (`logistics-ops`, `warehouse` and `operations` are accepted aliases for `ops`, see `TENANT_ALIASES`). Settings (`src/northwind/config.py`, env in brackets): `context_diet` [`ATLAS_CONTEXT_DIET`], `retrieval_top_k` [`ATLAS_TOP_K`, default 4], `history_token_budget` [`ATLAS_HISTORY_TOKENS`, 8000], `tool_result_token_budget` [`ATLAS_TOOL_RESULT_TOKENS`, 1400], `kb_min_score` [`KB_MIN_SCORE`, 0.5], `max_steps` [`ATLAS_MAX_STEPS`, 6], `max_retries` [`ATLAS_MAX_RETRIES`, 2], `request_timeout_s` [`ATLAS_REQUEST_TIMEOUT_S`, 20], `prompt_version` [`ATLAS_PROMPT_VERSION`], `tenant_soft_cap_usd` [25], `tenant_hard_cap_usd` [40], `degraded_model` (`gpt-4.1-nano`). Agent: `app/agent.py::AtlasAgent.run`, `_call_model`, `CircuitBreaker`, `FALLBACKS`, `build_router_config`; `northwind.tokens.context_diet(messages, history_budget=, tool_result_budget=)`, `truncate_tool_result`; `northwind.budget.BudgetGuard.decide` → `Decision.ALLOW | DEGRADE | REFUSE`, `BudgetDecision.anomaly`, `EWMAAnomalyDetector`. Prompts: `app/prompts.py::PROMPT_NAME = "atlas-system"`, `ATLAS_SYSTEM_V1`, `ATLAS_SYSTEM_V2`, `V2_MARKER`; `telemetry.langfuse_setup.get_prompt_text(name, label="production", fallback=, cache_ttl_seconds=60)`, `push_prompts(PROMPTS, production_version=)`. Span attributes: `atlas.tenant`, `atlas.prompt_version`, `atlas.retrieval.top_k`, `atlas.ttft_ms`, `atlas.cost_usd`, `atlas.steps`, `atlas.retries`, `atlas.budget.decision`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`, `session.id`, `deployment.release`. Metrics (`telemetry/metrics.py`): `atlas_cost_usd_total{tenant,model,feature}`, `atlas_llm_retries_total{model,reason}`, `atlas_model_fallbacks_total`, `atlas_budget_decisions_total{tenant,decision}`, `atlas_tool_calls_total{tool,outcome}`, `atlas_ttft_seconds`, `atlas_request_latency_seconds`, `atlas_judge_score{name}`, `atlas_feedback_total`. Loading an incident: `make incident N=<n>` (imports the JSONL into a temporary store and prints the text console) or `LocalSpanStore.from_jsonl(spans_path, scores_path)` in your own script. Each incident folder holds `spans.jsonl`, `scores.jsonl`, `brief.md` and `solution.md` (incident 4's `solution.md` is instructor-only and stripped by `make student-repo`). Days: every dataset is Monday 2026-09-14 (`simulator.scenarios.DEFAULT_DATE`). Session ids follow the simulator format `s07-01843`.

**Investigation rule for students (say it in 11.1 and repeat before every pause):** open `brief.md`, load `spans.jsonl`, do not open `solution.md` until Part B.

---

## Lecture 11.1 — How to read an incident like an SRE

| Field | Value |
|---|---|
| ID | 11.1 |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (~880 spoken words) |
| Learning objectives | 1. Apply the four-step order of an incident investigation: timeline, blast radius, hypothesis, evidence. 2. Use the incident template to write down what you know, what you think and what you have proven, separately. 3. Know which Atlas signal answers which question, so you look in the right place first. |
| Prerequisites | Sections 5 to 9 (traces, cost, latency, online evals, dashboards) |
| Files used | `10-resources/incident-template.md`, `console/ops_console.py`, `incidents/` |

### Script

[B-ROLL: A phone on a desk lights up at 11:20. The alert text reads: "ATLAS budget: tenant ops reached soft cap ($25). Responses degraded." Cut to a laptop opening.]

[AVATAR]
It's eleven twenty on a Monday morning and your phone just told you that Atlas has spent twenty-five dollars for one department before lunch, when that department normally spends nine dollars in a whole day.

What do you open first?

Most engineers open the code. That's the wrong first move. In this section you're on call for three incidents, and before I hand you the first one, I want to give you the habit that separates people who find root cause in ten minutes from people who find it in three hours. The order you ask questions in.

[SLIDE 1: The four questions, in order]
1. Timeline: when did it start, and what changed near that time?
2. Blast radius: who is affected, and who is not?
3. Hypothesis: write down two or three, with a prediction each
4. Evidence: which trace, metric or score would prove or kill each one?

Four questions. Always in this order.

First, timeline. When did the symptom start, to the minute? And what changed near that moment? A deploy, a config flag, a prompt label, a provider status, a Monday. Almost every incident you'll ever see has a change within thirty minutes of the first symptom. Find the change and you've found the neighbourhood of the cause.

Second, blast radius. Who is affected? One tenant or all four? One tool or every tool? One model or both? And just as important, who is *not* affected? If three departments are fine and one is on fire, the cause lives in something only that department does, or something only that department was given.

Third, hypotheses. Plural. Write down two or three, each with a prediction. "If it's a traffic spike, requests per minute will be up." "If it's a runaway loop, steps per session will be up." Writing the prediction first stops you from seeing what you want to see.

Fourth, evidence. For each hypothesis, name the exact signal that would prove or kill it. Then go look. Only then do you open the code.

[SLIDE 2: Which signal answers which question]
| Question | Where to look | Signal |
|---|---|---|
| Is it traffic? | Ops Console, Grafana | requests per minute by tenant |
| Is it cost per request? | Ops Console cost page | cost per session, `gen_ai.usage.input_tokens` per generation |
| Is it retries? | generation spans, `/metrics` | attempts per generation, `atlas_llm_retries_total`, `atlas.retries` |
| Is it one tool? | Langfuse filter by observation name | `atlas_tool_calls_total{outcome}`, tool duration |
| Is it the model or provider? | generation spans | `atlas.ttft_ms`, `gen_ai.response.model`, model mix |
| Is it a change we made? | release, prompt and config attributes | `deployment.release`, `atlas.prompt_version`, `atlas.retrieval.top_k` |
| Is it quality? | scores | `judge_grounded`, `judge_resolved`, `user_feedback`, by prompt version |

Here's the map you'll use in every incident. Each row is a question and the one signal that answers it fastest.

Is it traffic? Requests per minute, by tenant. Two clicks in the Ops Console.

Is it cost per request? Cost per session and input tokens per generation. If cost is up and traffic is flat, the money is going into bigger requests, not more of them.

Is it retries? Attempts per generation. Every retry is a generation span with an error status, and the `atlas.retries` attribute on the root span counts them.

Is it one tool? Filter by tool name. Error outcome and duration, per tool.

Is it the model or the provider? Look at generation spans. Time to first token is the provider's fingerprint. Model mix tells you whether escalation or degradation is firing.

Is it something we changed? Every span carries the release, the prompt version and the retrieval top-k. That's why we tagged them in Sections 3, 4 and 5. This is the payoff.

And is it quality? Judge scores and thumbs, sliced by prompt version.

Notice what's not on this list. Logs. Logs are where you go once a trace has pointed at a specific span. Not before.

[SLIDE 3: The incident template]
- Status line: what is broken, for whom, since when
- Timeline table: time, event, source
- Blast radius: affected / not affected
- Hypotheses: claim, prediction, status (open / confirmed / killed)
- Evidence: exhibit, where it lives, what it shows
- Root cause and contributing factors
- Fix (now) and prevention (later)

Open `10-resources/incident-template.md`. It's a one-page markdown file with seven blocks, and you'll fill one in for each incident in this section.

The block that matters most is hypotheses. Three columns: the claim, the prediction, and the status. Open, confirmed, or killed. Killing a hypothesis is progress. Write it down and move on.

The evidence block is a list of exhibits. Each one says where it lives, so the next person can open it. "Cost page, tenant filter ops, 09:00 to 12:00" is an exhibit. "I looked at the dashboard" is not.

[SLIDE 4: How the incident labs work]
- Each incident: a dataset in `incidents/`, a `brief.md`, and a `solution.md`
- Load it: `make incident N=<n>` (imports `incidents/incident-0<n>-*/spans.jsonl` and `scores.jsonl` into a temporary store and prints the text console; `LocalSpanStore.from_jsonl(...)` for your own scripts)
- Part A gives you the brief and the exhibits, then an eight-minute pause
- Part B walks the evidence to root cause, the fix and the prevention
- Rule: do not open `solution.md` until Part B

Here's how the next three lectures work. Each incident ships as a dataset of spans and scores, a brief written the way your on-call channel would write it, and a solution file. You load the spans into the local store with one make command and open the Ops Console. Everything runs offline. No API key, no cost.

Part A of each lecture gives you the brief and shows you the exhibits, without interpreting them. Then you get an eight-minute timer. Pause the video. Fill in the template. Write your root cause in one sentence before you press play.

Part B follows the evidence with you. Root cause, fix, and a thirty-second answer to the question that matters most: what would have prevented this, and which lecture taught it?

One rule. Don't open `solution.md` before Part B. You'll learn ten times more from being wrong for eight minutes than from being right in ten seconds.

[AVATAR]
Three more things before your first page.

One. Root cause is usually two things. A change that made the system fragile, plus a trigger that pushed on it. When you find one cause, ask what made it expensive.

Two. Fix now, prevent later. Stop the bleeding first, even if the fix is a rollback or a flag flip. Prevention is for the postmortem.

Three. Write it down as you go. Your future self, forty minutes into an incident, doesn't remember what you killed at minute five.

Ready? Monday morning. Your phone is ringing.

**Recap:** Investigate in order, timeline then blast radius then hypotheses then evidence, use the signal map to look in the right place first, and write down what you know, think and have proven in the incident template.

**Transition:** Next, Incident 1: a tenant has hit its soft cap before lunch, and you have eight minutes to explain why.

### Speaker notes: common student mistakes / Q&A

- Mistake: opening code first. The Section 11 datasets are designed so the trace answers the question faster than the diff does. Say so explicitly.
- Mistake: a single hypothesis. Students who write one hypothesis tend to confirm it. Insist on two or three with predictions.
- "Where does `deployment.release` come from?" Resource attributes in `telemetry/otel_setup.py::build_resource` (Lecture 3.2) and `release=` on the Langfuse client in `init_langfuse` (Lecture 4.1). If a student's own traces lack it, that's a Lab 2 fix.
- Instructor tip: pin a Q&A thread per incident titled "Incident N: your root cause in one sentence" and ask students to post before watching Part B.

---

## Lecture 11.2 — Incident 1: Monday's cost spike (Part A and Part B)

| Field | Value |
|---|---|
| ID | 11.2 (recorded and uploaded as 11.2 Part A and 11.2 Part B) |
| Type | CH (challenge: investigate, then reveal) |
| Target duration | 12:00 total. Part A 4:00 (~510 spoken words) ending on the pause card. Part B 8:00 (~1170 spoken words). The eight-minute investigation is the student's own time. |
| Learning objectives | 1. Find the root cause of a tenant cost spike from cost curves, token counts, retry counts and one trace waterfall, without reading code first. 2. Explain how a config change (context diet off, top-k 12) and an external trigger (a provider timeout storm) compound into a cost event. 3. Apply the fix: restore the diet, cap top-k, shorten the timeout, make the breaker count timeouts, and wire the anomaly alert that would have paged earlier. |
| Prerequisites | 11.1; Sections 5, 6 and 7 |
| Files used | `incidents/incident-01-cost-spike/spans.jsonl`, `brief.md`, `solution.md`; `simulator/scenarios.py` (`INCIDENT_PRESETS["cost_spike"]`), `app/agent.py`, `app/tools.py`, `src/northwind/tokens.py`, `src/northwind/budget.py`, `console/ops_console.py` |

### Script: Part A — the page and the evidence

[B-ROLL: Ops Console cost page. Four lines from 06:00. At 09:00 one line, labelled `ops`, bends upward; at 10:00 it goes almost vertical. Red tint.]

[AVATAR]
Monday, eleven twenty. Your phone: "Budget: tenant ops reached soft cap, twenty-five dollars. Responses degraded."

Two minutes later, a message from the logistics lead: "Atlas has been slow all morning and now the answers are rubbish. Two-sentence replies that miss the point. What is going on?"

You have the trace store, the Ops Console and the brief. Let's read the brief together, then I'll show you the exhibits, and then you're on your own for eight minutes.

[SLIDE 1: On-call brief, Incident 1]
- 11:20 Monday: soft-cap alert, tenant `ops`, $25/day; the budget guard has switched that tenant to the degraded model and two articles
- On the current trend the $40 hard cap trips at about 12:40, and Atlas will refuse the tenant
- Normal Atlas spend: about $24 per day across all four tenants; `ops` about $9 per day
- Other three tenants: normal
- Deploy at 08:55 today: "retrieval recall improvements" (PR #412)
- Provider status page: "investigating elevated error rates" posted at 10:14
- Dataset: `incidents/incident-01-cost-spike/spans.jsonl`, Monday 06:00 to 12:00

Here's what the brief tells you. Atlas normally costs about twenty-four dollars a day for the whole company. Logistics-ops is normally nine. Today it hit twenty-five before lunch, and on the trend it will hit the forty-dollar hard cap at twelve forty, at which point Atlas refuses that department entirely. The other three tenants look normal. No code deploy today. The provider says it's investigating elevated error rates since ten fourteen.

The soft cap from Lecture 6.7 did what it should. It slowed the bleeding. But it also made the answers worse for a whole department, and it took until eleven twenty to fire. Your job is to explain the sixteen dollars before then, and stop the next fifteen.

[SCREEN: Terminal. `make incident N=1`. The Ops Console opens on the cost page.]

Load the dataset. One command replays the spans into the local store, one opens the console. Now the exhibits. I'm going to show you six, and I'm not going to interpret any of them. That's your job.

[EVIDENCE 1: Ops Console, cost page, cost per hour by tenant, 06:00 to 12:00]
Exhibit one. Cost per hour by tenant. Three flat lines. One line bends at nine and breaks at ten. Two bends. Remember that.

[EVIDENCE 2: Ops Console, traffic page, requests per minute by tenant, same window, with last Monday as a shadow line]
Exhibit two. Requests per minute, same window, same tenant filter. Compare ops with last Monday's shadow.

[EVIDENCE 3: Ops Console, cost page, cost per session and mean `gen_ai.usage.input_tokens` per generation, ops, hourly]
Exhibit three. Two numbers for ops, hour by hour. Cost per session. And mean input tokens per generation. Look at eight o'clock, nine o'clock and ten o'clock.

[EVIDENCE 4: Ops Console, reliability page, `atlas_tool_calls_total` error share per tool, and `atlas_llm_retries_total` by reason, all tenants]
Exhibit four. Two panels. Tool error share, per tool. And LLM retries, by reason. One of these panels does something at ten o'clock. The other doesn't.

[EVIDENCE 5: Ops Console, retrieval page, `atlas.retrieval.top_k` and retriever result size in tokens, by tenant]
Exhibit five. The retrieval page. Top-k per retriever span and the size of what came back, in tokens, split by tenant.

[EVIDENCE 6: Trace waterfall for session `s07-01843` in the console's trace view (or Langfuse if you replayed there). Two turns. Six generation spans; from 10:00 each generation shows three attempts, two red. One `search_knowledge_base` tool span per turn, one `check_shipment`.]
Exhibit six. One trace. Session `s07-01843`, a dispatcher in ops asking about a delayed shipment and then a follow-up. Two turns, six generations. Open any generation span and read `gen_ai.usage.input_tokens`. Count the attempts under it. Open the `search_knowledge_base` tool span and look at the size of the result and its `atlas.retrieval.top_k`. Then open the *second turn* and read the input tokens again.

[SLIDE 2: Your eight minutes]
- Fill in `10-resources/incident-template.md`
- Timeline: two bends, at 09:00 and 10:00. What changed at each?
- Blast radius: one tenant. What was done only to that tenant?
- At least two hypotheses with predictions. Kill the ones the exhibits kill.
- Write root cause in one sentence, and one fix you would ship before lunch
- Do not open `solution.md`

[AVATAR]
Six exhibits. All of them are in the dataset you just loaded, and you can dig deeper than I showed you. Filter by user. Sort sessions by cost. Compare Friday's spans with Monday's.

Two hints. The cost line bends twice, at nine and at ten. Two bends usually means two causes. And the brief says nothing was deployed. Deploys aren't the only way to change a system.

Fill in the template. Then write the root cause in one sentence, and one fix you'd ship before lunch.

Pause now. Eight minutes.

[PAUSE: investigate for 8 minutes]

[SCREEN: Part A ends on the timer card. Part B opens on the same card, timer at zero.]

### Script: Part B — the reveal

[AVATAR]
Time. Write your one sentence down if you haven't. Let's walk the evidence in the order from Lecture 11.1.

Timeline first. Two bends. Nine o'clock and ten o'clock.

What changed at ten is the easy one, because the provider told you. Exhibit four.

[EVIDENCE 4 again: tool error share flat for all five tools; `atlas_llm_retries_total{reason="timeout"}` jumps from near zero to about 1.4 per generation at 10:00, ops and, at a much lower rate, the other tenants]

Tool errors: flat. Every tool, all morning. If your first hypothesis was "a failing tool", the exhibit killed it, and that's fine; that's what hypotheses are for. But LLM retries, reason timeout, jump at ten o'clock. About seventy percent of model calls started timing out on their first two attempts and succeeding on the third. That's the provider incident. Twenty-second timeout, two retries, so every generation now takes forty seconds longer and is sent three times.

That's the trigger. But look at the other tenants in the same panel. They got the same timeouts at a lower rate and their cost barely moved. So why did ops explode?

Because of what happened at nine. Exhibit five.

[EVIDENCE 5 again: `atlas.retrieval.top_k` is 4 for three tenants all day; for ops it becomes 12 at 09:00. Retriever result size for ops jumps from about 400 tokens to about 8,600 tokens.]

At nine o'clock, ops retriever spans start carrying top-k twelve, while everyone else stays on four. And the result size goes from about four hundred tokens to eight thousand six hundred. That's not twelve snippets. That's twelve *whole articles*. Something turned the context diet off for one tenant and tripled its retrieval.

The eight fifty-five deploy. PR #412, "retrieval recall improvements". The knowledge base team had a real complaint: Atlas kept truncating the shipment policy article, so answers missed the exceptions. Their fix was a per-tenant change for ops: `top_k` from four to twelve, the relevance floor `KB_MIN_SCORE` dropped to zero, and, because whole articles would otherwise be truncated, the context diet switched off. Full articles, more of them, for the tenant that asks about shipments. No deploy. No review from anyone who owned the cost budget.

Blast radius answered too. One tenant, because the change was for one tenant.

Now exhibit three, because this is where the two causes meet.

[EVIDENCE 3 again: ops cost per session $0.006 at 08:00, $0.037 at 09:00, $0.13 from 10:00; mean input tokens per generation 1,900 → 11,400 at 09:00, unchanged at 10:00]

Cost per session: six tenths of a cent at eight. Three point seven cents at nine. Thirteen cents from ten. Mean input tokens per generation: nineteen hundred at eight, eleven thousand four hundred from nine, and *unchanged* at ten. The prompts didn't get bigger at ten. They got sent three times.

Open the trace.

[SCREEN: Trace `s07-01843`. Turn one: `search_knowledge_base` result about 8,600 tokens, `atlas.retrieval.top_k = 12`; generations at 10,900; 12,400; 13,100 input tokens. Turn two: generations at 21,800; 23,300; 24,000. Each generation after 10:00 shows three attempts: two ERROR spans with status "APITimeoutError after 20.0 s" and input tokens recorded, one OK.]

Turn one. The retriever returns twelve full articles, eight thousand six hundred tokens. Every generation in that turn carries them: ten thousand nine hundred, twelve thousand four hundred, thirteen thousand one hundred. Turn two, the follow-up. With the diet off there's no trimming, so the whole of turn one comes along: twenty-one thousand eight hundred, twenty-three thousand, twenty-four thousand. Under each generation, three attempts. Two timed out after twenty seconds. All three were billed for their input tokens, because the request reached the model before we gave up on it.

Let's do the arithmetic on this one session.

[SLIDE 3: One session, $0.13]
- Six generations, 105,500 input tokens in total, sent 3 times each ≈ 316,000 billed input tokens
- 316,000 × $0.40 per million (`gpt-4.1-mini`) ≈ $0.127
- Output: about 1,100 tokens × $1.60 per million ≈ $0.002
- ≈ $0.13 per session, against $0.006 normally: 20x
- Same timeouts with the diet on (history 3,000, tool results 400): about 36,000 billed tokens ≈ $0.02

Six generations, a hundred and five thousand input tokens, sent three times: three hundred and sixteen thousand billed tokens. At forty cents a million on `gpt-4.1-mini`, thirteen cents. Output is noise. Thirteen cents a session, twenty times normal, and the session took over four minutes because of the timeouts, which is why the lead said "slow all morning".

Now the line that matters. Same timeouts, same retries, with the diet on: history trimmed to eight thousand tokens, tool results to fourteen hundred. About thirty-six thousand billed tokens. Two cents. The provider storm alone was a two-cent problem. The override alone was a four-cent problem. Together, thirteen.

[SLIDE 4: Hypotheses and verdicts]
| Hypothesis | Prediction | Exhibit | Verdict |
|---|---|---|---|
| Traffic spike | requests/min up several x | 2 | Killed: up 15%, a normal Monday |
| Failing tool, retry loop | tool error share up, steps per session up | 4, 6 | Killed: tools healthy, 3 steps per turn |
| Provider timeouts, LLM retries | attempts per generation up from 10:00 | 4, 6 | Confirmed: the trigger |
| Bigger prompts | input tokens per generation up from 09:00 | 3, 5, 6 | Confirmed: the cause |
| Degraded model | `gpt-4.1-nano` share up | model mix | Confirmed from 11:20, a consequence of the soft cap |

Traffic? Killed. A failing tool? Killed, and I'm glad the dataset let you kill it, because "retry storm" made most of you look at tools first. The retries were on the model. Provider timeouts? Confirmed, trigger. Bigger prompts? Confirmed, cause. And the nano share rising at eleven twenty is the soft cap doing its job, which is also why the answers got worse.

[SLIDE 5: Root cause, one sentence]
> PR #412, deployed at 08:55, switched the context diet off and raised retrieval top-k to 12 for ops, so every generation carried 11,000+ tokens of whole articles and untrimmed history; from 10:00 a provider timeout storm made Atlas send each of those prompts three times, and the soft cap degraded the tenant at 11:20.

If your sentence had the timeouts, good. If it had the retrieval change, very good. If it had both and said which one multiplied the other, you're ready to be on call.

Now the fix. Right now, roll the retrieval settings back: `ATLAS_TOP_K=4`, `KB_MIN_SCORE=0.5`, `ATLAS_CONTEXT_DIET=1`, so ops is back on the diet with top-k four. That stops the spend within a minute and undoes the degradation once spend drops below the soft cap at midnight, or sooner if you reset the window. Then four changes for this week.

[CODE: `app/tools.py`, `app/agent.py` and `src/northwind/config.py`, the fix]
```python
# src/northwind/config.py: the diet is not a feature flag
retrieval_top_k: int = 4            # capped at 6 in ToolContext; overrides above 6 are ignored and logged
request_timeout_s: float = 8.0      # was 20.0; the step budget is 4 s, retries must not stack to 40 s

# app/tools.py: never return whole articles to the model
if ctx.full_text or ctx.scenario == "context_bloat":
    hits = [h.with_snippet(width=320) for h in hits]      # snippets only; full_text kept for the eval harness

# app/agent.py: a timeout is a breaker failure, even when the third attempt succeeds
except RETRYABLE as exc:
    self.breaker.record_failure(current)                 # was: only after all retries were exhausted
    metrics.LLM_RETRIES.labels(current, type(exc).__name__).inc()
    time.sleep(self._backoff(attempts))                  # exponential, jittered

# src/northwind/budget.py: the anomaly detector pages, not just the cap
if decision.anomaly:
    metrics.BUDGET_DECISIONS.labels(tenant, "anomaly").inc()   # alert rule: increase(...[15m]) > 0
```

One. The context diet stops being something a tenant override can switch off, and top-k is capped at six no matter what the config says. The knowledge base team's complaint is real, and the answer is a bigger snippet or a better ranking, not whole articles.

Two. The timeout goes from twenty seconds to eight. With two retries, a bad provider now costs a step twenty-four seconds at worst, not sixty.

Three. The circuit breaker from Lecture 7.4 has a threshold of three consecutive failures. Two timeouts and a success never trip it, so it never opened and the fallback model in `FALLBACKS` never got a call. Now every timeout counts. During this storm the breaker opens within a minute and calls go to the fallback, which wasn't timing out.

Four. `BudgetGuard.decide` already computes an EWMA anomaly flag on every request, from Lecture 6.7. It was never wired to a metric. Now it increments the decisions counter with `anomaly`, and an alert rule watches it. In the replay, that alert fires at ten oh nine, seventy-one minutes before the soft cap.

[SCREEN: Replay the `cost_spike` preset against the fix. Ops Console cost page: the ops line bends slightly at 10:00 and flattens. Callout: cost per session $0.021 during the storm; soft cap never reached; anomaly alert at 10:09.]

Replay the same Monday against the fix. Same override attempt, ignored above six. Same provider storm. Cost per session during the storm: two cents. The soft cap is never reached. And the page arrives at ten oh nine with the word "anomaly" in it, not at eleven twenty with the word "degraded".

[SLIDE 6: What would have prevented this]
- Lecture 6.5, context diet: a unit test that a 3-turn conversation with 12 articles stays under `history_token_budget`, and no override path
- Lecture 6.7, budgets: the EWMA anomaly flag wired to a metric and a page, 71 minutes earlier
- Lecture 7.3 and 7.4, timeouts and breakers: an 8 s timeout, and timeouts count as failures so the fallback fires
- Lecture 13.3, CI budget gate: tokens per step and cost per session checked on every change, including config

Thirty seconds on prevention. Lecture 6.5 gave you the diet. What it didn't insist on, and should have, is a test that a three-turn conversation with twelve articles stays inside the history budget, and no code path that turns the diet off per tenant. Lecture 6.7 gave you the anomaly detector; today you learned it was computing an answer nobody read. Lectures 7.3 and 7.4 gave you timeouts and the breaker; the twenty-second default was inherited, not chosen, and a breaker that only counts exhausted retries is a breaker that never opens. And Lecture 13.3 will give you a CI gate that replays the day with the proposed config and fails when tokens per step move, before an experiment reaches a tenant.

[AVATAR]
Two lessons to carry into the next incident. Config changes are deploys, even when nothing is deployed. And the trigger is rarely the root cause; ask what made it expensive.

**Recap:** A retrieval PR turned off the context diet and tripled retrieval for one tenant, a provider timeout storm sent every bloated prompt three times, and the fix is a diet that cannot be switched off, a shorter timeout, a breaker that counts timeouts and an anomaly alert per tenant.

**Transition:** Next, Incident 2: Monday afternoon, latency doubles across every tenant at once, and the obvious cause is only half the story.

### Speaker notes: common student mistakes / Q&A

- Most common wrong answer in beta: "a failing tool". The preset's `retry_storm` is LLM timeouts (`app/mock_llm.py::_maybe_fail`, `retry_storm_failures=2`), not tool errors. Exhibit four is designed to kill the tool hypothesis early.
- Second: "the provider". Push back with exhibit three: prompts got big at 09:00, an hour before the provider. Ask "why did the other tenants survive the same timeouts?"
- Dataset generation note for the code author: `INCIDENT_PRESETS["cost_spike"]` = `context_bloat` 09:00-13:00 on ops (85%, `context_diet=False`, `top_k=12`) plus `retry_storm` 10:00-12:00 (70%). The dataset must record each timed-out attempt as an ERROR generation span with its input tokens so cost triples; if the replay does not bill failed attempts, change Slide 3 to "sent three times, billed once" and recompute ($0.045 per session, the multiplier becomes latency rather than cost).
- "Why did the soft cap make answers worse?" `Decision.DEGRADE` switches to `degraded_model` (`gpt-4.1-nano`) and `top_k=2` in `AtlasAgent.run`. That's the intended trade: cheaper, worse, still answering.
- Students who replayed to Langfuse Cloud can filter by `atlas.tenant` and sort traces by cost; the same exhibits exist there.

---

## Lecture 11.3 — Incident 2: p95 doubled after lunch (Part A and Part B)

| Field | Value |
|---|---|
| ID | 11.3 (recorded and uploaded as 11.3 Part A and 11.3 Part B) |
| Type | CH (challenge: investigate, then reveal) |
| Target duration | 12:00 total. Part A 4:00 (~380 spoken words) ending on the pause card. Part B 8:00 (~1020 spoken words). |
| Learning objectives | 1. Separate a provider slowdown from a self-inflicted regression using TTFT, input tokens and the recovery curve. 2. Explain why a fallback that is configured but never triggers is the same as no fallback. 3. Apply the fix: retrieval top-k back to a measured value, a per-call timeout derived from the step budget, and a breaker that treats slowness as failure. |
| Prerequisites | 11.1, 11.2; Sections 5.3, 5.4 and 7 |
| Files used | `incidents/incident-02-latency-regression/spans.jsonl`, `brief.md`, `solution.md`; `simulator/scenarios.py` (`INCIDENT_PRESETS["latency_regression"]`), `app/knowledge.py`, `app/agent.py` (`build_router_config`, `CircuitBreaker`, `FALLBACKS`), `src/northwind/config.py`, `src/northwind/latency.py` |

### Script: Part A — the page and the evidence

[B-ROLL: Grafana panel "Atlas p95 end-to-end latency". Flat at 3.1 s all morning. At 13:00 it climbs to 6.4 s and stays. A red threshold line at 4.0 s.]

[AVATAR]
Monday, fourteen twenty. The `AtlasLatencyP95High` alert from Lecture 9.5 fires: "Atlas p95 latency above 4 s", and it has been above four seconds for fifteen minutes.

Nobody is complaining yet. In ten minutes they will be, because six-second answers from a helpdesk feel broken.

Same routine. Brief, exhibits, eight minutes.

[SLIDE 1: On-call brief, Incident 2]
- 14:20 Monday: `latency_p95` alert (p95 above 4 s for 15 minutes); p95 end-to-end 6.4 s against a 4.0 s budget; p50 2.7 s (was 1.4 s)
- All four tenants affected
- Error rate flat at 0.3%; no 429s, no timeouts, no retries
- Cost per session up 25% since 12:30
- Deploys today: `v1.8.2` at 12:30, "KB retrieval tuning" (config only, from the knowledge base team)
- Provider status page: "investigating elevated latency" posted at 13:05
- Dataset: `incidents/incident-02-latency-regression/spans.jsonl`, Monday 2026-09-14, 10:00 to 18:00

Here's the brief. p95 has more than doubled. p50 nearly doubled too. All four tenants. No errors, no rate limits, no timeouts, no retries. Cost per session is up twenty-five percent, which is odd for a latency incident. There was a config-only deploy at twelve thirty from the knowledge base team. And the provider posted "investigating elevated latency" at thirteen oh five.

You might think you already know the answer. Hold that thought, and look at the exhibits. The dataset runs to six p.m., and the end of it matters.

[SCREEN: `make incident N=2`. Ops Console latency page.]

[EVIDENCE 1: Ops Console, latency page, p50 and p95 end-to-end, 10:00 to 18:00, budget line at 4.0 s]
Exhibit one. p50 and p95, end to end, from ten to six. Note the exact minute p95 leaves the budget. And note what happens after sixteen fifty.

[EVIDENCE 2: Ops Console, latency page, span duration p95 by observation type: agent, generation, retriever, tool]
Exhibit two. The same window, broken down by span type. Agent, generation, retriever, tool. Which ones move?

[EVIDENCE 3: Ops Console, generation detail, `atlas.ttft_ms` p95 and total generation duration p95]
Exhibit three. Two generation metrics side by side. Time to first token, from Lecture 5.4. And total generation duration. Both at p95. Watch how each behaves at thirteen hundred and again at sixteen fifty.

[EVIDENCE 4: Ops Console, cost page, mean input tokens and mean output tokens per generation, hourly]
Exhibit four. Tokens per generation, input and output, by the hour. Look at twelve thirty.

[EVIDENCE 5: Trace waterfall for session `s07-02290` at 10:15 and session `s07-03118` at 13:41, side by side]
Exhibit five. Two traces for the same question, "how do I request VPN access", one at ten fifteen and one at thirteen forty-one. Open the retriever span in each and compare `atlas.retrieval.top_k` and `atlas.retrieval.hits`. Then compare the generation spans.

[EVIDENCE 6: Ops Console, reliability page, `atlas_model_fallbacks_total`, `atlas_llm_retries_total` and the breaker state]
Exhibit six. Fallbacks, retries and the circuit breaker state from Lecture 7.4. Look at the whole window.

[SLIDE 2: Your eight minutes]
- Timeline: two things happened within thirty minutes of each other. Find both.
- Blast radius: everyone, so the cause is shared. What do all tenants share?
- Predict: if this is only the provider, what should p95 do at 16:50?
- Explain the cost: why is a latency incident 25% more expensive?
- Root cause in one sentence, fix you would ship today
- Do not open `solution.md`

[AVATAR]
A hint, because this one is designed to fool you. Two things happened within thirty minutes of each other. The provider status page is one of them. If the provider were the whole story, what should the latency chart do when the provider recovers? Write that prediction down before you look.

And explain the cost. A slow provider doesn't charge you more per token. So where is the twenty-five percent coming from?

Pause now. Eight minutes.

[PAUSE: investigate for 8 minutes]

[SCREEN: Part A ends on the timer card. Part B opens on the same card, timer at zero.]

### Script: Part B — the reveal

[AVATAR]
Time. Let's walk it.

Timeline. p95 leaves the budget at thirteen hundred. Within thirty minutes of that we have a config deploy at twelve thirty and a provider status post at thirteen oh five. Two candidates. Most people pick the provider, because the provider admitted it. Let's see if the evidence agrees.

[EVIDENCE 3 again: `atlas.ttft_ms` p95 480 ms → 1,700 ms at 13:00, back to 500 ms at 16:50. Generation duration p95 2.2 s → 4.8 s at 13:00, down to 3.0 s at 16:50, not 2.2 s.]

Exhibit three. Time to first token is the provider's fingerprint. Nothing in our code runs between sending the prompt and receiving the first token. It goes from under half a second to one point seven seconds at thirteen hundred, and drops straight back at sixteen fifty when the provider recovers. So yes, the provider was slow. Three and a half times slower to start, and about half the tokens per second. Confirmed.

But look at total generation duration. It rises with TTFT, and when TTFT recovers, it only falls to three seconds. Before lunch it was two point two. Something else is making generations longer, and it didn't recover with the provider.

[EVIDENCE 1 again: p95 after 16:50 settles at 4.3 s, still above the 4.0 s budget line]

Exhibit one confirms it. After the provider recovered, p95 settled at four point three seconds. Still above budget. If you predicted "p95 returns to three point one at sixteen fifty", the chart killed that hypothesis for you. The provider was half the story.

[SLIDE 3: Hypotheses and verdicts]
| Hypothesis | Prediction | Exhibit | Verdict |
|---|---|---|---|
| Provider slowdown | TTFT up, all tenants, recovers with provider | 3 | Confirmed, but not sufficient |
| Traffic or rate limiting | 429s, queueing, one tenant | brief | Killed: no 429s, all tenants |
| Slow tool or retriever | tool or retriever span duration up | 2 | Killed: retriever p95 40 ms → 55 ms |
| Bigger prompts | input tokens per generation up from 12:30 | 4, 5 | Confirmed |
| Fallback not firing | fallback rate zero through the incident | 6 | Confirmed |

Rate limiting? Killed, no four-two-nines. A slow retriever? Killed. Exhibit two shows the retriever span barely moved, forty to fifty-five milliseconds. It's BM25 on local files. But that fifteen milliseconds is a clue, because the retriever is doing more work. Bigger prompts? Look at exhibit four.

[EVIDENCE 4 again: mean input tokens per generation 1,900 → 3,500 from 12:30; output tokens 210 → 230]

Input tokens per generation went from nineteen hundred to thirty-five hundred, and it happened at twelve thirty, not thirteen hundred. Thirty minutes before the provider slowed down. Sixteen hundred extra tokens on every generation. That's your twenty-five percent cost increase. And more input tokens means more prefill time, which is why generation duration stayed high after TTFT recovered.

Where did sixteen hundred tokens come from? Open the two traces.

[SCREEN: Retriever spans side by side. 10:15: `atlas.retrieval.top_k = 4`, `atlas.retrieval.hits = 4`, about 400 tokens of context. 13:41: `atlas.retrieval.top_k = 20`, `atlas.retrieval.hits = 20`, about 2,000 tokens of context. Footer visible.]

Ten fifteen: top-k four. Four snippets, about four hundred tokens of context. Thirteen forty-one: top-k twenty. Twenty snippets, about two thousand tokens. Sixteen extra snippets at roughly a hundred tokens each, title and score included, is sixteen hundred tokens. The arithmetic matches.

That's `v1.8.2`. The knowledge base team had a real problem: employees complained that Atlas missed the right policy document. Their fix was to raise `ATLAS_TOP_K` from four to twenty. Config only, no code, no review from anyone who owned the latency budget. And on its own, it would have pushed p95 from three point one to about four point three. Just over budget. It might have taken a day to notice. Then the provider slowed down and turned a small regression into a doubled p95.

Now exhibit six, because this is the part that should change how you configure things.

[EVIDENCE 6 again: `atlas_model_fallbacks_total` flat at zero; `atlas_llm_retries_total` zero; breaker state "closed" for every model all afternoon]

Fallbacks: zero. Retries: zero. Breaker: closed all afternoon. You configured a fallback chain in Lecture 7.4 and it never fired. Why? Look at the Router config.

[CODE: `app/agent.py::build_router_config`, as deployed]
```python
{
    "model_list": [...],                                      # gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o-mini, gpt-5-mini
    "fallbacks": [{m: [FALLBACKS[m]]} for m in models if m in FALLBACKS],
    "num_retries": settings.max_retries,                      # 2
    "timeout": settings.request_timeout_s,                    # 20.0: a 5-second generation never times out
    "allowed_fails": 3,
    "cooldown_time": 30,
}
```

A twenty-second timeout. A five-second generation is a success as far as the Router is concerned. Fallbacks trigger on errors and timeouts, and the provider produced neither. It was just slow. A fallback that only fires on errors doesn't protect a latency SLO. It protects an availability SLO. Those are different promises.

[SLIDE 4: Root cause, one sentence]
> A config change raised retrieval top-k from 4 to 20 at 12:30, adding 1,600 input tokens to every generation and pushing p95 to the edge of budget; a provider slowdown from 13:00 to 16:50 tripled TTFT on top of it; and with a 20-second timeout the Router and the breaker saw no failures, so the fallback never fired.

Two causes and a missing safety net. If your sentence had all three, excellent. If it had the provider only, go back to exhibit one and look at sixteen fifty again. That recovery curve is the most useful shape in latency debugging: whatever is left after the external cause recovers is yours.

The fix, in three parts.

[CODE: the fix, `src/northwind/config.py` and `app/agent.py`]
```python
# src/northwind/config.py
retrieval_top_k: int = 6            # measured on the KB team's query set: recall@4 0.81, recall@6 0.90, recall@20 0.91
request_timeout_s: float = 8.0      # per call; the step budget from Lecture 7.1 is 4 s plus headroom

# app/agent.py: slowness is a failure for the breaker
SLOW_CALL_S = 4.0
elapsed = clock() - t0
if elapsed > SLOW_CALL_S:
    self.breaker.record_failure(current)       # three slow calls open the circuit; next call goes to FALLBACKS[current]
    metrics.LLM_RETRIES.labels(current, "slow").inc()
```

Part one, top-k. Not back to four, because the knowledge base team's complaint was real. We ran their query set against the retriever offline. Recall at four: point eight one. Recall at six: point nine zero. Recall at twenty: point nine one. Twenty bought one point of recall for sixteen hundred tokens. Six buys nine points for two hundred. The number comes from a measurement, not a guess, and it goes in `config.py` with the measurement as a comment.

Part two, a real timeout. Eight seconds per call, against a four-second step budget with headroom. Now a truly stuck provider *is* a failure.

Part three, and this is the one Lecture 7.4 didn't teach you: slowness as failure. Any call over four seconds counts as a breaker failure. Three of those in a row open the circuit, and the next call goes to the fallback model, which wasn't slow. In the replay, the breaker opens at thirteen oh two, about thirty percent of calls go to the fallback during the slowdown, and p95 holds at three point five.

And one more, not in the code: config changes that touch tokens go through the same review as code changes. Top-k is a cost and latency setting wearing a quality costume. You saw that yesterday too.

[SCREEN: Replay Monday against the fix. p95 curve stays under 4.0 s through the provider slowdown; callout: fallback rate 30% between 13:00 and 16:50; p95 3.5 s.]

[SLIDE 5: What would have prevented this]
- Lecture 5.3, RAG spans: top-k and hits are attributes on every retriever span, so the change is visible in one filter
- Lecture 7.1, latency budgets: a per-call timeout derived from the step budget, not a default
- Lecture 7.4, fallbacks: the breaker must count slow calls, not only errors
- Lecture 13.3, CI budget gate: replaying the day with `ATLAS_TOP_K=20` fails the p95 check before it ships

Thirty seconds on prevention. Lecture 5.3 put top-k on the retriever span, which is why you could see it. Lecture 7.1 told you to derive timeouts from the budget; the twenty-second default was never chosen, it was inherited, and it hurt you on Monday too. Lecture 7.4 built the breaker; today you learned it needs to count slowness to protect a latency SLO. And the CI budget gate in Lecture 13.3 replays a day of traffic with the proposed config. Top-k twenty fails the p95 assertion on the pull request, and the knowledge base team finds out in four minutes instead of the whole company finding out at lunch.

[AVATAR]
Carry this one forward: when an external cause recovers, whatever latency is left is yours. And a fallback nobody has seen fire is a fallback you don't have.

**Recap:** A retrieval top-k change quietly added 1,600 tokens to every generation, a provider slowdown tripled TTFT on top, and a 20-second timeout meant neither the Router nor the breaker saw a failure; fix with a measured k, a real timeout and a breaker that counts slow calls.

**Transition:** Next, Incident 3, the hardest kind: every dashboard is green, and users are quietly giving up.

### Speaker notes: common student mistakes / Q&A

- Most common wrong answer: "the provider". Reward students who noticed the 12:30 token jump preceded the 13:00 latency jump by thirty minutes, and the 16:50 recovery that didn't reach baseline.
- "Why not roll back to k=4?" Because the KB team's complaint was real. The lesson is to measure recall against tokens, and to put the measurement in the code as a comment. Students who answered k=4 get partial credit; k=6 with a reason gets full.
- Dataset note for the code author: `INCIDENT_PRESETS["latency_regression"]` = `slow_provider` 13:00-17:00, all tenants, 75%, `top_k=20`. For the story the top-k change should apply to all requests from 12:30, not only to requests hit by the slowdown; either add a second `Incident` covering 12:30-24:00 with `{"top_k": 20}` and no latency effect, or narrate "the dataset applies the change from 13:00" and drop the 12:30 lead.
- Snippet size: `KnowledgeBase._snippet(width=320)` is about 80 tokens plus title and score; sixteen extra hits is roughly 1,600 tokens. Recompute if the snippet width changes.
- "Isn't an 8 s timeout too aggressive for long answers?" With streaming you would time out on TTFT instead, Lecture 5.4. The slow-call rule uses total elapsed time; say both on screen.
- `Router(timeout=, num_retries=, fallbacks=, allowed_fails=, cooldown_time=)` confirmed in the curriculum reference; `build_router_config` is pure data and testable offline.

---

## Lecture 11.4 — Incident 3: users are unhappy but nothing is red (Part A and Part B)

| Field | Value |
|---|---|
| ID | 11.4 (recorded and uploaded as 11.4 Part A and 11.4 Part B) |
| Type | CH (challenge: investigate, then reveal) |
| Target duration | 12:00 total. Part A 4:00 (~470 spoken words) ending on the pause card. Part B 8:00 (~1000 spoken words). |
| Learning objectives | 1. Diagnose a quality regression that no latency, error or cost signal shows, using judge scores, feedback and prompt version tags. 2. Read a trace for behavioural change: citations, next steps and answer length. 3. Roll back a prompt by moving the `production` label in Langfuse, then put a gate in front of label changes. |
| Prerequisites | 11.1 to 11.3; Sections 4.4, 4.5 and 8 |
| Files used | `incidents/incident-03-quality-drift/spans.jsonl`, `brief.md`, `solution.md`; `simulator/scenarios.py` (`INCIDENT_PRESETS["quality_drift"]`), `app/prompts.py`, `telemetry/langfuse_setup.py`, `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py`, `evals/to_dataset.py` |

### Script: Part A — the email and the evidence

[B-ROLL: Grafana Atlas Ops dashboard. Every panel green. The cost panel is even trending down. Cut to an email subject line: "Atlas got worse?"]

[AVATAR]
Tuesday, nine ten. No alert. No page. An email from the HR business partner.

"Hi. Since late morning yesterday Atlas has got noticeably worse. Answers are two lines, no source, and it doesn't tell people what to do next, so they're opening tickets themselves in ServiceHub. Three people asked me if it's broken. Dashboard looks fine to me though. Is something going on?"

You open the Ops dashboard. Latency, green. Error rate, green. Cost, green, and actually *down*. Nothing is red.

This is the hardest kind of incident, because the tools you'd normally trust are telling you everything is fine, and one of them is telling you things got better. Let's read the brief.

[SLIDE 1: On-call brief, Incident 3]
- Tuesday 09:10: HR business partner reports Atlas answers have been "two lines, no source, no next step" since Monday late morning; employees opening tickets themselves
- p95 3.0 s (budget 4.0 s), error rate 0.2%, cost per session down 12%: all within SLO
- ServiceHub: manually opened tickets up 40% since 11:00 (from the ticketing system, not from Atlas)
- Deploys this week: none
- Langfuse prompt `atlas-system`: version 2 created last week; label history visible in the UI
- Dataset: `incidents/incident-03-quality-drift/spans.jsonl` and `scores.jsonl`, Monday 2026-09-14, 08:00 to 17:00, includes judge scores and feedback

Nothing you'd call an alert. Latency inside budget. Errors near zero. Cost down twelve percent, which finance would call good news. No code deploys this week. But two odd facts: the ticketing system shows forty percent more manually opened tickets since eleven, and the Langfuse prompt `atlas-system` has a version two that was created on Tuesday.

This dataset is different from the first two. It includes the judge scores from Lecture 8.2 and the thumbs feedback from Lecture 8.3. Use them.

[SCREEN: `make incident N=3`. Ops Console quality page.]

[EVIDENCE 1: Ops Console, quality page, judge scores `judge_grounded` and `judge_resolved`, hourly, Monday 08:00 to 17:00]
Exhibit one. The two judge scores from Lecture 8.2. Grounded: did the answer cite and use the retrieved policy. Resolved: did the employee get what they needed, including a next step. Hourly. Find the hour where the lines bend.

[EVIDENCE 2: Ops Console, quality page, thumbs-down rate hourly and the ten most common feedback comments since 11:00]
Exhibit two. Thumbs-down rate, hourly, and the ten most common feedback comments since eleven. Read the comments.

[EVIDENCE 3: Ops Console, quality page, judge scores split by `atlas.prompt_version`]
Exhibit three. The same judge scores, but split by the prompt version each generation was linked to. You tagged this in Lecture 4.4. Two bars per score.

[EVIDENCE 4: Ops Console, cost page, mean output tokens per generation and cost per session, hourly; tools page, calls per hour by tool]
Exhibit four. Output tokens per generation and cost per session, hourly. And, on the tools page, calls per hour by tool. One of these changes shape at eleven. The other doesn't.

[EVIDENCE 5: Two traces, same question "how many days of parental leave do I get?", `s07-01120` Monday 09:20 and `s07-02875` Monday 14:05. Show the retriever span, the generation output and the `atlas.prompt_version` attribute.]
Exhibit five. Two traces for the same question, one at nine twenty and one at two oh five. In both, open the retriever span and check what it returned. Then read the final answer, word by word. Then read `atlas.prompt_version` on the root span.

[EVIDENCE 6: Langfuse prompt page for `atlas-system`: version list, labels, the diff between v1 and v2, and the label change event at Monday 11:02]
Exhibit six. The prompt page in Langfuse. Versions one and two, their labels, the diff, and the audit entry for when the `production` label moved. Read the diff line by line.

[SLIDE 2: Your eight minutes]
- Timeline: when do the scores bend, and what happened at that minute?
- Blast radius: all tenants, or mostly HR? Why might HR notice first?
- Compare the two traces: same retrieval, different answer. What sits between them?
- Why did no alert fire, and why did one metric improve?
- Root cause in one sentence, the fix (it's one API call), and the gate that stops it recurring
- Do not open `solution.md`

[AVATAR]
Two hints. First, the scores in this dataset are the alert you didn't have. Treat the judge like a metric with a timeline. Second, when two traces retrieve the same documents and answer differently, the difference is not in retrieval. Look at what sits between the retrieval and the answer.

The fix for this one is a single API call. Finding out *which* call, and why it's safe, is the exercise.

Pause now. Eight minutes.

[PAUSE: investigate for 8 minutes]

[SCREEN: Part A ends on the timer card. Part B opens on the same card, timer at zero.]

### Script: Part B — the reveal

[AVATAR]
Time. Let's walk it.

Timeline. Exhibit one.

[EVIDENCE 1 again: `judge_grounded` mean 0.91 through the 10:00 bin, then 0.72 from the 11:00 bin onward; `judge_resolved` 0.86 → 0.74. Callout on 11:00.]

Grounded runs at point nine one all morning, then drops to point seven two in the eleven o'clock bin and stays there. Resolved goes from point eight six to point seven four at the same hour. This is a step change, not a drift. Step changes have a cause with a timestamp.

What happened at eleven? No deploy. But exhibit six.

[EVIDENCE 6 again: audit entry "label `production` moved from v1 to v2, Monday 11:02, by a product manager account"]

Monday eleven oh two. The `production` label on `atlas-system` moved from version one to version two. Through the UI, by a product manager, after a tone review. No deploy, because prompts don't deploy. Atlas fetches the production label through `get_prompt_text` with a sixty-second cache, Lecture 4.4. Within a minute of that click, every Atlas response in every tenant was running on a prompt that had never been evaluated. The root spans say so: `atlas.prompt_version` flips from `langfuse:1` to `langfuse:2` at eleven oh three.

Blast radius. All four tenants, because every tenant uses the same prompt. But HR noticed first, and exhibit four tells you why.

[EVIDENCE 4 again: output tokens per generation 210 → 135 from 11:00; cost per session down 12%; tool calls per hour unchanged for all five tools]

Output tokens per generation fell from two hundred and ten to a hundred and thirty-five. That's your cost improvement: shorter answers are cheaper answers. Tool calls didn't change at all. Atlas still searched the knowledge base for every policy question, and still found the right article. It just stopped telling anyone which article, and stopped saying what to do next. HR gets the most policy questions, the kind where "which policy says so" and "here's the form" are the whole value. Their employees noticed within the hour and started opening tickets by hand. That's containment, from Lecture 9.1, dropping from seventy-eight percent to sixty-four, and nobody had put it on a dashboard.

Now the traces, because this is where you see *what* changed, not just when.

[SCREEN: Trace `s07-01120`, Monday 09:20, `atlas.prompt_version = langfuse:1`. Retriever returns `leave-policy.md`. Answer: "Northwind offers 16 weeks of paid parental leave for primary carers and 4 weeks for secondary carers. Both need at least 6 months of service. (Source: Leave Policy) Next step: submit the parental leave request form in ServiceHub at least 8 weeks before your start date." Judge: grounded 1, resolved 1.]

Nine twenty, version one. Retriever finds the leave policy. Answer: sixteen weeks primary, four weeks secondary, the service requirement, a source line, and a next step with a deadline. Judge scores it grounded and resolved.

[SCREEN: Trace `s07-02875`, Monday 14:05, `atlas.prompt_version = langfuse:2`. Retriever returns the same `leave-policy.md` chunk. Answer: "Primary carers get 16 weeks of paid parental leave and secondary carers get 4 weeks." Judge: grounded 0, resolved 0. Feedback: thumbs down, comment "ok but where is this from and what do I do now?"]

Two oh five, version two. Same question. The retriever returns the *same* article. The answer is one sentence. The numbers are right. No source. No service requirement. No next step. Judge: not grounded, because nothing in the answer points at the policy, and not resolved, because the employee still doesn't know what to do. The employee's comment says it better than the judge: "ok but where is this from and what do I do now?"

So retrieval didn't change. What sits between retrieval and answer is the system prompt. Read the diff.

[CODE: `app/prompts.py`, the diff between `ATLAS_SYSTEM_V1` and `ATLAS_SYSTEM_V2`]
```python
# v1 (kept)
"- Be concise and friendly. Use short paragraphs or a numbered list for steps."
"- Always cite the knowledge base article title you relied on, in the form (Source: <title>)."
"- End every answer with one clear next step for the employee, or the ticket id you created."

# v2 (the tone review)
"- Be brief. Prefer one or two sentences; avoid unnecessary references or repetition."
"- Only mention tickets or sources when the employee explicitly asks for them."
```

Two changes that look like copy-editing. "Be brief, one or two sentences, avoid unnecessary references." And "only mention sources or tickets when asked." Read as prose, that's a tidier prompt. Read as behaviour, it deletes the citation rule and the next-step rule, the two rules that made Atlas's answers useful rather than merely correct. Nobody ran an eval, because to the person making the change it was copy, not code.

[SLIDE 3: Hypotheses and verdicts]
| Hypothesis | Prediction | Exhibit | Verdict |
|---|---|---|---|
| Model or provider regression | scores drop for both prompt versions | 3 | Killed: v1 generations still score 0.91 / 0.86 |
| Retrieval regression | retriever returns wrong or empty chunks | 5, 4 | Killed: same article, same tool call rate |
| Prompt change | step change in scores at label move; v2 scores lower | 1, 3, 6 | Confirmed |
| HR-only data problem | only HR scores drop | 3 | Killed: all tenants; HR noticed first |

Exhibit three is the one that kills the alternatives. Split by prompt version, version one generations still score point nine one grounded right up to the moment there stopped being any. Version two scores point seven two from its first hour. Same model, same retriever, same day. Only the prompt differs. That's as clean as causality gets in production.

[SLIDE 4: Root cause, one sentence]
> Prompt version 2 of `atlas-system` received the `production` label through the UI at Monday 11:02 without an offline eval; it removed the citation and next-step rules, so grounded fell from 0.91 to 0.72, resolved from 0.86 to 0.74, containment from 78% to 64%, and every SLO on the dashboard stayed green while cost went down.

Now the fix. One call.

[CODE: rollback, a one-off script using the configured client]
```python
from telemetry.langfuse_setup import client

lf = client()
lf.update_prompt(name="atlas-system", version=1, new_labels=["production"])
# labels are unique across versions: this moves "production" from v2 back to v1
# Atlas picks it up within cache_ttl_seconds (60) on the next get_prompt_text()
```

`update_prompt`, name, version one, new labels production. Labels are unique across versions, so assigning `production` to version one removes it from version two. Atlas calls `get_prompt_text` with the production label and a sixty-second cache on every request, so within a minute every tenant is back on version one. No deploy, no restart. The same property that caused the incident makes the rollback instant.

[SCREEN: Ops Console quality page, after the rollback: `judge_grounded` returns to 0.90, `atlas.prompt_version` back to `langfuse:1`; manual ticket rate falls within the hour.]

Sixteen fifty-five. Grounded climbs back to point nine within the hour. The HR lead gets a reply that says what happened, in plain language, with a time.

But rolling back isn't the fix. The fix is making sure a label can't move without evidence again.

[CODE: `evals/to_dataset.py` and the promotion gate, sketched]
```python
# 1. Promote the failing v2 traces to a dataset (Lecture 8.6)
lf.create_dataset_item(dataset_name="atlas-failures", input=trace.input, expected_output=None,
                       source_trace_id=trace.id, metadata={"prompt_version": 2})

# 2. Promotion happens in code, never in the UI: push_prompts() labels the chosen version
def promote(version: str, min_grounded: float = 0.85) -> None:
    score = run_offline_evals(PROMPTS[version], dataset="atlas-failures")
    if score < min_grounded:
        raise SystemExit(f"atlas-system {version} scored {score:.2f} < {min_grounded}; not promoted")
    push_prompts(PROMPTS, production_version=version)        # telemetry.langfuse_setup
```

Three moves. First, promote the failing version-two traces into the `atlas-failures` dataset, Lecture 8.6. Those traces are now the regression suite for the next prompt change. Second, a `promote` function that runs the offline evals for a candidate version and refuses to move the label below point eight five grounded, then calls `push_prompts`, which already exists in `langfuse_setup.py`. Third, take label editing away from the UI for the production label. Whether that's a Langfuse role setting or a team rule, verify what your Langfuse plan supports, but the principle stands: the production label moves through a pull request, with an eval result attached.

And add the two signals that were missing from the dashboard. Judge grounded, seven-day rolling, with an SLO. And containment. Both were in `slo.py` from Lecture 9.1. Neither was on the board.

[SLIDE 5: What would have prevented this]
- Lecture 4.4, prompt labels: the label is a deploy; treat it like one
- Lecture 8.2 and 8.5, online judge and drift: an hourly drift check on `judge_grounded` pages at 12:10, not an email the next morning
- Lecture 8.6, bad trace to regression test: v2 fails the `atlas-failures` dataset before it ever gets a label
- Lecture 9.1, SLIs: judge score and containment on the dashboard, with an SLO

Thirty seconds on prevention. Lecture 4.4 taught you labels; today you learned a label change is a deploy and needs a deploy's discipline. Lectures 8.2 and 8.5 gave you the judge and the drift comparison; run it hourly instead of weekly and it pages at ten past twelve, four and a half hours before the email. Lecture 8.6 gave you the dataset that turns this incident into a test. And Lecture 9.1 named judge score and containment as SLIs. Put them on the dashboard and this stops being the incident where nothing was red.

[AVATAR]
Three incidents. A cost spike, a latency regression, a quality drift. Different symptoms, same method. Timeline, blast radius, hypotheses, evidence. Next, you learn to write it up so the fix outlives the person who found it.

**Recap:** A prompt label moved without an eval, the new version stopped citing and stopped giving next steps, judge scores and containment fell while every SLO stayed green and cost improved; roll back by moving the label, then gate promotions behind offline evals and put quality on the dashboard.

**Transition:** Next, writing the postmortem: blameless, specific, with action items that map to instrumentation, budgets and tests.

### Speaker notes: common student mistakes / Q&A

- Most common miss: students find the prompt change but propose "edit v2 to fix it" instead of rolling back first. Fix now, improve later. Editing under pressure creates version three with its own surprises.
- "Was the product manager wrong to change the prompt?" No, and this is the blameless point for 11.5. The system let a behaviour change ship through a copy-editing interface. Fix the system.
- `update_prompt(name=, version=, new_labels=)` verified on langfuse 4.15.6; labels are unique across versions and `latest` is reserved. Re-verify before recording.
- Dataset note for the code author: `INCIDENT_PRESETS["quality_drift"]` = `prompt_regression` 11:00-24:00, all tenants, `prompt_version=v2`; the mock keys off `V2_MARKER` ("avoid unnecessary references") to drop citations and next steps. Root spans must carry `atlas.prompt_version`; the judge heuristics in offline mode must score `grounded` on the presence of a `(Source: ...)` line and `resolved` on a next step.
- Restricting label edits by role: Langfuse RBAC and prompt protection features vary by plan and version. Say "verify against current Langfuse docs" on screen.
- Some students will ask why cost fell. Shorter answers; output tokens are the expensive ones per token. Good observation; it's the point of the lecture that "cheaper" was the only signal that moved on the dashboard, and it moved the wrong way.

---

## Lecture 11.5 — Writing the postmortem

| Field | Value |
|---|---|
| ID | 11.5 |
| Type | SC (screencast, writing the document live) |
| Target duration | 7:00 (~730 spoken words, plus the postmortem text read on screen) |
| Learning objectives | 1. Write a blameless postmortem using the template: impact in numbers, a sourced timeline, root cause and contributing factors, detection and response gaps. 2. Turn every lesson into an action item of one of four types: instrumentation, budget, test or process, with an owner and a date. 3. Recognise the three postmortem anti-patterns: blame, vagueness and action items nobody can verify. |
| Prerequisites | 11.2 to 11.4 |
| Files used | `10-resources/postmortem-template.md`, `incidents/incident-01-cost-spike/postmortem.md` (written live), `tests/unit/`, `src/northwind/budget.py` |

### Script

[B-ROLL: Two postmortem documents side by side. Left: "Root cause: the KB team turned off the context diet without asking." Right: "Root cause: the context diet could be disabled per tenant through config, and no test or gate checked tokens per step."]

[AVATAR]
Two postmortems for the same incident. The left one is true. The right one is useful. Only one of them prevents the next incident.

A postmortem has one job. It makes the same failure impossible, or at least loud, next time. Everything else in the document is in service of that. In this lecture we write the Incident 1 postmortem together, live, and I'll show you the three ways these documents usually go wrong.

[SLIDE 1: The postmortem template]
1. Summary: three sentences, no jargon
2. Impact: numbers, with the source of each number
3. Timeline: time, event, source; detection and resolution marked
4. Root cause and contributing factors
5. Detection: how we found out, how long it took, how we should have
6. Response: what we did, what worked, what slowed us down
7. Action items: type, owner, due date, verification
8. Lessons

Open `10-resources/postmortem-template.md`. Eight blocks. Most of them you already filled in during the investigation, in the incident template. The postmortem adds three things the investigation didn't need: impact in numbers, the detection gap, and action items with owners.

[SCREEN: VS Code, new file `incidents/incident-01-cost-spike/postmortem.md`. Type the summary.]

[CODE: summary block]
```markdown
# Postmortem: Incident 1, ops cost spike (Monday)

## Summary
Between 09:00 and 11:20 on Monday, Atlas spent $25 for the ops tenant, against a normal
$9 per day, and the budget guard then degraded that tenant's answers for the rest of the day. A
per-tenant retrieval change (PR #412) had disabled the context diet and raised retrieval to 12 whole
articles; a provider timeout storm from 10:00 then caused every oversized prompt to be sent three
times. No other tenant was affected and no data was lost.
```

Summary. Three sentences a finance manager can read. What happened, in numbers. Why, in one clause. Who was affected and who wasn't. If the summary needs the word "span", rewrite it.

[CODE: impact block]
```markdown
## Impact
| Measure | Value | Source |
|---|---|---|
| Extra spend | $22 above the normal morning; projected $40 hard cap at 12:40 if unfixed | Ops Console cost page, tenant filter, 09:00-11:20 |
| Sessions affected | ~540 sessions; cost per session $0.037 (09:00-10:00) and $0.13 (10:00-11:20), normal $0.006 | Ops Console sessions view |
| Latency | p95 for ops 3.1 s → 68 s during the timeout storm | `atlas_request_latency_seconds{tenant="ops"}` |
| Degraded answers | ops on `gpt-4.1-nano` with 2 articles from 11:20 until the fix at 11:47 | `atlas_budget_decisions_total{decision="degrade"}` |
| Upstream load | ~3x the normal request rate to the provider from this tenant | generation spans, attempts per generation |
| Other tenants | none | Ops Console cost page |
```

Impact. Every number has a source column. That's not bureaucracy. It means the next person can reproduce the number, and it means you're not guessing. Notice the third row. This was a cost incident, but users experienced it as a latency incident first. Sixty-eight-second p95. Write down every kind of impact, not just the one that paged you.

[CODE: timeline block]
```markdown
## Timeline (local time)
| Time | Event | Source |
|---|---|---|
| Mon 08:55 | deploy PR #412 "retrieval recall improvements": ops `top_k` 4 → 12, `KB_MIN_SCORE` 0, context diet off | deploy log; `atlas.retrieval.top_k` on spans |
| Mon 09:00 | cost per session for ops rises 6x; input tokens per generation 1,900 → 11,400 | Ops Console |
| Mon 10:00 | provider timeouts begin; ~70% of calls fail twice then succeed | `atlas_llm_retries_total{reason="APITimeoutError"}` |
| Mon 10:09 | (would have fired) per-tenant EWMA anomaly on spend rate | `BudgetDecision.anomaly`, not wired to a metric |
| Mon 10:14 | provider status page: "investigating elevated error rates" | status page |
| Mon 11:20 | soft cap $25 reached; tenant degraded; page sent **(detection)** | `BudgetGuard.decide` → `Decision.DEGRADE`, alert |
| Mon 11:38 | root cause identified from trace `s07-01843` and the retrieval page | investigation notes |
| Mon 11:47 | retrieval settings rolled back (`ATLAS_TOP_K=4`, `KB_MIN_SCORE=0.5`, `ATLAS_CONTEXT_DIET=1`); spend window reset; tenant restored **(resolution)** | deploy log |
| Mon 12:00 | provider timeouts end | `atlas_llm_retries_total` |
```

The timeline. Time, event, source. Mark detection and resolution explicitly, because the gap between the first symptom and detection is the number that matters most. Here: first symptom nine o'clock, detection eleven twenty. One hundred and forty minutes. And look at the ten oh nine row. I've written in the alert that *would* have fired, if the anomaly flag had been wired to anything. Writing the counterfactual into the timeline is how you justify the action item later.

[SLIDE 2: Root cause versus contributing factor]
- Root cause: the thing that, removed, means the incident does not happen
- Contributing factor: the thing that, removed, means the incident is smaller or found sooner
- Incident 1 root cause: the context diet and top-k could be overridden per tenant with no review, test or gate
- Contributing: provider timeout storm (trigger), 20 s timeout with stacked retries, breaker that ignores timeouts, anomaly flag not wired, whole-article tool results

Root cause versus contributing factor. The root cause is the thing that, if removed, means the incident doesn't happen. Here that's a retrieval change with no eval, no cost check and no gate. The provider storm is a trigger. If it hadn't happened Monday, the override alone would have cost four cents a session until someone noticed, maybe weeks later. The long timeout, the breaker that ignores timeouts, the unwired anomaly flag and the whole-article tool results are contributing factors. Each one removed makes the incident smaller or shorter, not impossible.

Get this distinction right and your action items write themselves.

[CODE: action items block]
```markdown
## Action items
| # | Action | Type | Owner | Due | Verified by |
|---|---|---|---|---|---|
| 1 | `test_context_diet_bounds_tokens`: 3 turns × 12 articles stays under `history_token_budget` | test | @agent-team | Wed | CI green on the fix branch |
| 2 | remove the per-tenant override path for `context_diet`; cap `top_k` at 6 in `ToolContext` | instrumentation | @agent-team | Wed | override attempt logged and ignored in replay |
| 3 | `search_knowledge_base` returns snippets only; `full_text` reserved for the eval harness | instrumentation | @agent-team | Wed | tool result ≤ `tool_result_token_budget` in integration test |
| 4 | `request_timeout_s` 20 → 8; `CircuitBreaker.record_failure` on every timeout | test | @agent-team | Fri | breaker opens within 60 s in `retry_storm` replay; fallback rate > 0 |
| 5 | `BudgetDecision.anomaly` → `atlas_budget_decisions_total{decision="anomaly"}` + alert rule | budget | @platform | Fri | alert fires at ~10:09 in `cost_spike` replay |
| 6 | CI budget gate asserts max input tokens per generation and cost per session | test | @platform | next sprint | Lecture 13.3 gate red on `ATLAS_CONTEXT_DIET=0` |
| 7 | config changes that affect tokens or timeouts go through PR review like code | process | @eng-manager | now | config service requires a linked PR |
```

Action items. Every row has a type, and there are only four types allowed: instrumentation, budget, test, or process. If an action item isn't one of those, it's a wish. "Be more careful with experiments" is a wish. "A test that fails when the diet is off" is an action.

Every row has an owner who is a person or a team, a date, and a "verified by" column. How will we *know* it's done? Row five says the alert must fire when we replay this exact incident. That's a test for the alert. Row six says the CI gate must go red on the setting that caused the incident. That's the strongest verification there is: the fix would have caught the past.

[SLIDE 3: Three anti-patterns]
- Blame: "the KB team turned it off." Systems let people turn things off; fix the system
- Vagueness: "improve monitoring." Name the signal, the threshold and where it pages
- Unverifiable: "add tests." Name the test and what makes it fail

Three ways postmortems go wrong.

Blame. "The knowledge base team turned off the diet." True, and useless. They had a real complaint and a lever that looked safe. The question is why a lever that changes cost by six times looked safe. Blameless doesn't mean nobody made a mistake. It means the mistake isn't the interesting part.

Vagueness. "Improve cost monitoring." Which signal? What threshold? Where does it page? Row five names all three.

Unverifiable. "Add tests around the agent loop." Which test? What input makes it fail? If you can't say what would make the test red, you haven't designed a test.

[SCREEN: Scroll the finished postmortem top to bottom in twenty seconds.]

[AVATAR]
One more habit. Read the finished postmortem as the person who caused the incident. If any sentence would make you defensive, rewrite it to be about the system. Then read it as the person who'll be on call next month. If any action item leaves them guessing, add the verification.

Your turn. Write the postmortems for Incidents 2 and 3 using the same template. Then you're ready for Project 2.

**Recap:** A postmortem states impact with sources, a timeline that marks detection and resolution, root cause separated from contributing factors, and action items typed as instrumentation, budget, test or process with an owner and a way to verify them.

**Transition:** Next, Project 2: a fourth incident, unrevealed. You investigate it alone and submit the postmortem.

### Speaker notes: common student mistakes / Q&A

- Mistake: action items without a "verified by". Insist on it in Project 2 grading. The best verification is "the fix turns red on the incident that caused it."
- Mistake: listing the trigger (provider timeouts) as root cause. Ask "if the provider had timed out with the diet on, what would it have cost?" Two cents a session.
- "How long should a postmortem be?" One to two pages. If it's longer, the timeline has too much detail or the lessons are essays.
- The 10:09 counterfactual row is a technique worth calling out: it's how you argue for an alert with data rather than opinion.

---

## Lecture 11.6 — Project 2: Investigate a fourth incident

| Field | Value |
|---|---|
| ID | 11.6 |
| Type | AS (assignment with short video brief) |
| Target duration | 3:00 (~390 spoken words); assignment itself about 2 to 4 hours |
| Learning objectives | 1. Run a full investigation on an unrevealed incident dataset with no hints. 2. Submit a postmortem that meets the template and the rubric. 3. Propose at least one action item that would have prevented or shortened the incident, with verification. |
| Prerequisites | 11.1 to 11.5 |
| Files used | `05-projects/project-2-incident-postmortem.md`, `incidents/incident-04-project/spans.jsonl` and `brief.md` (no `solution.md` in the student repo), `10-resources/incident-template.md`, `10-resources/postmortem-template.md` |

### Script

[AVATAR]
Three incidents with me. Now one without me.

Project 2 is a fourth incident dataset. It has a brief and spans. It does not have a solution file in your repo. There's no Part B. Nobody is going to walk the evidence for you.

[SLIDE 1: Project 2 brief]
- Dataset: `incidents/incident-04-project/spans.jsonl` and `brief.md`, linked from `05-projects/project-2-incident-postmortem.md`
- Load it the same way: `make incident N=4`
- Deliverable: `postmortem.md` using `10-resources/postmortem-template.md`
- Time box: 2 to 4 hours, including writing
- No `solution.md`. The Q&A thread for this project is for method questions, not answers

Here's the deal. The brief reads like the on-call channel, the way the first three did. Load the spans, open the console, and run the method from Lecture 11.1. Timeline, blast radius, hypotheses with predictions, evidence with exhibit locations. Then write the postmortem with the template from Lecture 11.5.

I'll tell you one thing about the dataset and nothing else. It has more than one cause, and they don't affect the same tenants. Every incident in this section had more than one cause. If you find one and stop, you'll have found a trigger, not the root cause.

[SLIDE 2: Rubric]
| Criterion | Weight |
|---|---|
| Timeline with sources; detection and resolution marked | 20% |
| Root cause correctly separated from contributing factors | 25% |
| Evidence: each claim points at an exhibit someone else can open | 20% |
| Action items: typed, owned, dated, verifiable; at least one "would have caught it" | 25% |
| Blameless, plain-language summary | 10% |

The rubric weights root cause and action items highest, and evidence next. A postmortem with the right root cause and no exhibits scores lower than one with a slightly wrong root cause and a clear evidence trail, because the second one can be checked and corrected. That's how it works on real teams too.

For the action items, at least one has to be the kind that would have caught this incident before it happened, with a verification that says how you'd prove it. Reread row six of the Incident 1 postmortem if you need the pattern.

[SLIDE 3: When you're stuck]
- Go back to the signal map in Lecture 11.1: which question haven't you asked?
- Compare a good trace and a bad trace for the same intent
- Check what changed: `deployment.release`, `atlas.prompt_version`, `atlas.retrieval.top_k`, config attributes on spans
- Ask a method question in the Q&A; don't ask for the answer

If you get stuck, go back to the signal map. There's usually one question you haven't asked yet. Compare a good trace and a bad trace for the same intent side by side, the way we did in Incidents 2 and 3. And check every "what changed" attribute: release, prompt version, top-k, config values on spans.

[AVATAR]
Submit the postmortem through the assignment for this lecture. And post your one-sentence root cause in the project thread after you submit, not before. Reading forty different sentences for the same incident is one of the best lessons in this course.

**Recap:** Investigate an unrevealed incident end to end and submit a postmortem that is sourced, blameless, separates root cause from contributing factors, and has verifiable action items.

**Transition:** Next, a short quiz on incident response, then Section 12, where you learn what happens to all of this if you change your observability backend.

### Speaker notes: common student mistakes / Q&A

- Do not confirm or deny root causes in the Q&A while the project is open. Answer method questions only.
- Dataset note for the code author: `INCIDENT_PRESETS["mixed"]` (`retry_storm` on finance 10:00-11:00 plus `slow_provider` for everyone 15:00-16:00) is a good basis for incident 4; keep its `solution.md` out of the student repo.
- If students report that the dataset is "too big", point them to filtering by time window first (the brief gives a window) and to the sessions-by-cost or sessions-by-latency sort.
- Peer review works well here: pair students to swap postmortems and check the "verified by" column.

---

## Lecture 11.7 — Quiz: Incident response

| Field | Value |
|---|---|
| ID | 11.7 |
| Type | QZ (6 questions, short video intro) |
| Target duration | 3:00 in the curriculum (1:00 video intro, ~100 spoken words; the quiz itself is untimed) |
| Learning objectives | 1. Check the investigation order and the signal map. 2. Check root cause versus trigger versus contributing factor. 3. Check the fix mechanics for each incident. |
| Prerequisites | 11.1 to 11.5 |
| Files used | `06-assessments/quizzes/section-11.md` |

### Script

[AVATAR]
Six questions on Section 11.

[SLIDE 1: Quiz: Incident response]
- 6 questions
- Investigation order and the signal map
- Root cause vs trigger vs contributing factor
- The three fixes: diet and timeouts, top-k and the breaker, prompt labels
- Read every explanation

They cover the order you investigate in, which signal answers which question, and the difference between a root cause, a trigger and a contributing factor. Two questions are about the fixes: what `update_prompt` with a new label actually does, and why a breaker that only counts errors never protects a latency SLO.

If you miss the root-cause question, rewatch the first two minutes of Lecture 11.5 before Project 2. It'll change your postmortem.

**Recap:** The quiz checks the investigation method and the mechanics of the three fixes.

**Transition:** Section 12 is next: what stays portable when you swap Langfuse for LangSmith, Phoenix or an enterprise APM, and what doesn't.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: the trigger versus root cause question for Incident 1 (students pick the provider timeouts). Point to Slide 2 of Lecture 11.5.
- Second most missed: "labels are unique across versions", so `update_prompt(version=1, new_labels=["production"])` removes the label from v2. Point to the rollback code in 11.4.
