# Section 15: Wrap-up and Careers

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈18 min (4 lectures, curriculum v1.0)
> **Upload order (important):** 15.1 → 15.2 → 15.3 → 15.4. Udemy requires the bonus lecture to be the **last** lecture in the course. 15.4 is the Bonus Lecture and is uploaded last, after the practice test (15.3). If any lecture is ever added to the course later, it goes *before* 15.4.
> **Source of truth:** `01-curriculum/curriculum.md`; interview questions `10-resources/interview-questions.md`; practice test `06-assessments/practice-test.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / langsmith 0.14; check the repo README for updates."
> **Production note:** No salary or rate figures anywhere in this section, on slides or in the resources. Markets differ by country and change quickly.

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only, not cues, tables or slide text.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 15.1 | What you can now do | TH | 4:00 | ~499 |
| 15.2 | Careers: LLMOps, AI platform and AI SRE roles | TH | 8:00 | ~1,169 |
| 15.3 | Final practice test | QZ | 0 min in curriculum (1:00 video intro) | ~121 |
| 15.4 | Bonus Lecture: keep operating | TH | 5:00 | ~578 |

---

## Lecture 15.1 — What you can now do

| Field | Value |
|---|---|
| ID | 15.1 |
| Type | TH (talking head / avatar with slides) |
| Target duration | 4:00 (~500 spoken words) |
| Learning objectives | 1. Recap the course by pillar: traces, cost, reliability, quality in production, operations. 2. Place this course on the Build → Test → Deploy → Operate path. 3. Choose one concrete next step for the coming week. |
| Prerequisites | Sections 1 to 14 (capstone recommended) |
| Files used | `03-code/README.md`, `reports/` (your weekly report) |

### Script

[B-ROLL: Fast montage, two seconds each: the cost meter climbing in Lecture 1.1, the first trace in Lecture 2.3, the console exporter output in Section 3, the Langfuse session view in Section 4, the compare-replays bar in Section 6, the fallback firing in Section 7, the drift report in Section 8, the Grafana dashboard in Section 9, the 10:09 counterfactual row from the Incident 1 postmortem, the red pull request in Section 13, the one-page report in Section 14.]

[AVATAR]
Think back to Lecture 1.1. An agent hit a tool error, retried in a loop, and a cost meter climbed while you watched. You couldn't see why. You couldn't stop it. You could only watch the number.

[PAUSE]

Now you can see it, in a trace, with the tokens per step written on every span. You can explain it, with a timeline and a hypothesis table. You can stop it, with a budget, a retry bound and a trimmed context. And you can make sure it never ships again, with a test that goes red in ninety seconds. That was the promise in Section 1. You kept it.

[SLIDE 1: What you can now do, by pillar]
- Traces: OpenTelemetry spans with GenAI semantic conventions for every model, tool, retriever and agent; sessions, users, tenants, releases; masked
- Cost: true cost per request, session, user, tenant and feature; a showback report finance accepts; 40%+ saved with caching, a context diet and routing; budgets per tenant
- Reliability: TTFT and p95 measured; timeouts, bounded retries, fallbacks that fire on slowness; p95 held under chaos
- Quality in production: sampled judge, feedback, drift detection, failures promoted to a regression suite
- Operations: SLIs and SLOs, dashboards and alerts as code with owners, incidents investigated from traces, postmortems, a self-hosted stack, a CI budget gate, a weekly report

Let's name it, because you'll want these words for your CV and your next interview.

Traces. You instrument any LLM agent with OpenTelemetry and the GenAI conventions, so any backend understands it. You attach sessions, users, tenants and releases, and you mask before anything leaves the process.

Cost. You compute the true cost of every request and roll it up to the number finance asks for. You cut it by more than forty percent and proved the saving by technique. You cap it per tenant and detect anomalies before the cap.

Reliability. You measure time to first token and p95, you time out, retry with bounds, fall back on slowness, and you held p95 under four seconds while the provider was failing.

Quality in production. You judge a sample of live traffic, correlate it with feedback, detect drift week over week, and turn failures into regression tests.

And operations. SLIs a manager understands, dashboards and alerts as code, three incidents investigated from traces alone, postmortems with verifiable action items, a self-hosted stack, a gate that stops bad changes with a number, and a one-page report.

[SLIDE 2: The Build → Test → Deploy → Operate path]
- Build: *Generative AI & AI Agents: Zero to Production*
- Test: *AI Agent Testing & Evaluation*
- Deploy in real time: *Production Voice AI Agents*
- Operate: this course
- All four stand alone; together they cover the lifecycle

This course is the fourth in a path: build, test, deploy, operate. You didn't need the other three to take this one. But if a part of this course felt thin, the offline eval theory in Section 8, or the agent internals in Section 5, that's where the deeper material lives. More in the bonus lecture at the very end.

[SLIDE 3: Your next 7 days]
1. Finish the capstone; get `ACCEPTANCE.md` to 14 of 20 or better
2. Send the weekly report to one real person and ask them one question about it
3. Pick one agent you or your team already run and add `genai_attrs` to its model call

Here's my challenge for the next seven days. Finish the capstone and get the acceptance report to fourteen or better. Send the weekly report to one real person, a manager, a colleague, a friend who runs a team, and ask them which number they'd want explained. Their answer will change your report. And pick one agent you or your team already run, and add GenAI attributes to its model call. One span. That's how it starts in a real company: one span, then a dashboard, then someone asks for the report.

[PAUSE]

Thank you for operating this with me. Atlas is running. Go make yours visible.

**Recap:** You can instrument, cost, harden, evaluate and operate an LLM agent in production, and the same method carries to any agent you're handed next.

**Transition:** Next, careers: the roles that hire for exactly this, and twelve interview questions with model answers.

### Speaker notes: common student mistakes / Q&A

- "Which pillar matters most in job postings?" Cost and quality in production come up most in 2026 postings; traces are assumed. Point students to the careers lecture.
- Remind students that the incident datasets and Northwind are fictional and synthetic; say so when they show the work.
- Encourage posting the weekly report screenshot in the Q&A; it's the deliverable that gets the most reactions.

---

## Lecture 15.2 — Careers: LLMOps, AI platform and AI SRE roles

| Field | Value |
|---|---|
| ID | 15.2 |
| Type | TH (talking head / avatar with slides) |
| Target duration | 8:00 (~1,060 spoken words) |
| Learning objectives | 1. Name the role titles that hire for agent observability and cost skills and what each emphasises. 2. Answer twelve common interview questions with a mechanism and a number. 3. Pitch observability to management as an ROI story with three numbers. |
| Prerequisites | Section 14 capstone (recommended) |
| Files used | `10-resources/interview-questions.md`, `reports/` (your weekly report), `ACCEPTANCE.md` |

> **Production note:** No salary or rate figures in this lecture, on slides or in the resources.

### Script

[B-ROLL: Four job postings side by side, titles highlighted: "LLMOps Engineer", "AI Platform Engineer", "AI Reliability Engineer", "Forward Deployed Engineer, AI". Cut to a highlighted line in one of them: "own cost per task and quality metrics for agents in production."]

[AVATAR]
You can now instrument, cost, harden and operate an AI agent in production. That combination is rare, and it's on job postings this year under four or five different names. This lecture: who hires for it, what they'll ask, and how to pitch it to a manager who controls a budget.

[SLIDE 1: Roles that hire for this]
- LLMOps engineer / MLOps engineer (LLM): tracing, evals in production, cost, prompt and model lifecycle
- AI platform engineer: the shared stack: gateway, observability, budgets, routing for many teams
- AI reliability engineer / SRE (AI systems): SLOs, incident response, capacity, provider risk
- AI product engineer / forward deployed engineer: ships agents and owns their metrics
- Also: FinOps analyst (AI spend), staff engineer (AI), developer productivity (AI tooling)

Job titles are messy, so search for several. "LLMOps" and "MLOps, LLM" roles focus on tracing, production evals, cost and the prompt and model lifecycle: Sections 3, 4, 6 and 8. "AI platform engineer" roles build the shared stack: the gateway, the observability pipeline, budgets and routing for many teams: Sections 6, 7, 12 and 13. "AI reliability engineer" or "SRE, AI systems" roles own SLOs, incidents, capacity and provider risk: Sections 7, 9 and 11. "AI product engineer" and "forward deployed" roles ship agents and are increasingly asked to own the metrics: Section 14. And FinOps teams now hire for AI spend specifically: Section 6.

Read the description, not the title. Look for: cost per task, evals in production, OpenTelemetry, SLOs, prompt versioning, incident.

[SLIDE 2: Your evidence]
- The capstone repo: three numbers in the README
- Two postmortems and one drift report
- A red pull request screenshot
- The weekly report
- The domain-swap project, which proves you can do it twice

Whatever the title, your evidence is the same. The capstone with three numbers up front. Postmortems. A red pull request. The weekly report. And the domain swap, which proves you can do it twice. Numbers beat adjectives: "cut cost per resolved session forty-three percent and held p95 under four seconds under a provider slowdown" is a stronger line than "experienced with LLM observability."

[SLIDE 3: Interview questions 1-4: tracing and attribution]
1. How do you trace a multi-step agent so the trace explains the tool calls?
2. What are the GenAI semantic conventions and why use them?
3. How do you attribute cost to a tenant or feature?
4. What do you never put in a trace, and how do you enforce that?

Twelve questions, with short model answers. Longer versions are in `interview-questions.md`.

One. Tracing a multi-step agent. "One agent span per request, a child span per step, a generation span per model call with token usage, and a tool span per call with arguments and a redacted result. Session and tenant as attributes. Then the trace answers why it called that tool, what came back, and where the tokens went."

Two. GenAI semantic conventions. "A standard vocabulary from OpenTelemetry for model, token usage, tool and agent attributes. Using them means any backend understands my spans, so I'm not locked in. They're still incubating, so I keep them behind one helper module."

Three. Cost attribution. "Compute cost once per generation from a price table I control, write it as a span attribute and a low-cardinality metric labelled by tenant and model, then roll up by session, user, tenant and feature. The report uses the same aggregation as the dashboard so they can't disagree."

Four. What never goes in a trace. "Raw PII and full tool payloads. I mask in the SDK with a mask function and again in the Collector, keep hashes for joins, and I have a test that sends a fake email through and asserts it comes out hashed."

[SLIDE 4: Interview questions 5-8: cost and reliability]
5. An agent's cost tripled overnight. Walk me through your investigation.
6. Name three ways to cut LLM spend and how you'd prove each saving.
7. How do you stop one tenant from burning the whole budget?
8. What does a fallback need in order to protect a latency SLO?

Five. Cost tripled overnight. "Timeline first: when, and what changed. Then blast radius: which tenant, which tool. Then two hypotheses with predictions: more requests, or bigger requests. Requests per minute versus tokens per generation tells me which. Then one trace. In the incident I worked, it was a config override that switched off context trimming, multiplied by a provider timeout storm that sent every oversized prompt three times."

Six. Three ways to cut spend. "Prompt caching with a stable prefix, measured by cached token share. A context diet: trimming history, truncating tool results, tuning retrieval k, measured by tokens per step. And small-model-first routing with escalation, measured by model mix. I prove each by replaying the same day with and without it."

Seven. One tenant burning the budget. "A per-tenant budget with a soft cap that degrades, a hard cap that refuses politely, and an anomaly detector on the spend rate so I'm paged before the cap. The cap saved the money; the anomaly alert saves the morning."

Eight. What a fallback needs. "A timeout derived from the step budget, not a default, and a circuit breaker that counts slow calls and timeouts, not only exhausted retries. Fallbacks trigger on failures; a slow provider produces none unless you define slowness as failure. And a metric for the fallback rate, because a fallback nobody has seen fire is one you don't have."

[SLIDE 5: Interview questions 9-12: quality and operations]
9. How do you know an agent got worse when latency, errors and cost all look fine?
10. How do you prevent a prompt change from regressing production?
11. What SLIs would you put on a dashboard for an AI agent, and who owns each alert?
12. How do you keep telemetry from taking down the service it observes?

Nine. Getting worse while everything looks fine. "Quality signals: a sampled LLM judge on live traffic, user feedback, and a weekly drift comparison, all sliced by prompt version. In my incident, grounded dropped from point nine one to point seven two the hour a prompt label moved, cost actually went down, and no latency or cost SLO noticed."

Ten. Preventing a prompt regression. "Treat the production label as a deploy. Promotion goes through code: run offline evals against a dataset of past failures, refuse to move the label below a threshold, and restrict UI label changes. Rollback is moving the label back, which takes a minute."

Eleven. SLIs and owners. "Task success or resolved rate, containment, tool error rate, p95 latency, cost per resolved session and a judge score. Each SLI gets an SLO and an error budget. Every alert has a named owner and a runbook, or it gets deleted."

Twelve. Telemetry safety. "Export on a background thread with a bounded queue that drops on overflow, five-second exporter timeouts, credentials in the Collector not the app, and a counter for dropped spans. I test it by killing the backend under load and asserting p95 doesn't move."

Notice the pattern. Every answer names a mechanism and a number. That's what interviewers are listening for.

[SLIDE 6: Pitching observability to management: the ROI story]
- Cost avoided: "the incident we caught at minute 20 instead of minute 112" in dollars
- Cost saved: the replay comparison, by technique, per month
- Risk reduced: the pull request that failed; the quality drift caught in an hour instead of a day
- Ask: the tool cost, the platform time, the owner, in one sentence

Now the pitch. You'll need budget for the backend, for Collector infrastructure, for time. Here's the story that gets it. Three numbers.

Cost avoided. The incident you caught at minute twenty instead of minute one hundred and twelve, in dollars, from the postmortem timeline. Cost saved. The replay comparison, by technique, multiplied out to a month. Risk reduced. The pull request that failed before it shipped, and the quality drift caught in an hour instead of a day, with the ticket volume it would have generated.

Then the ask, in one sentence: what the tool costs, how much platform time, and who owns it. Managers say yes to three numbers and one sentence. They say "let's revisit next quarter" to a twelve-slide deck.

[SLIDE 7: What not to say]
- Don't claim the incidents were real; say "simulated on a replayed dataset, method is real"
- Don't compare vendors by feature list; compare by control, cost, compliance, lock-in
- Don't quote a cost saving without the baseline and the method
- Don't promise 100% trace retention; talk about sampling policy

Four things not to say. Don't claim the course incidents were real production events; say they were simulated on a replayed dataset and the method is real. Interviewers respect that. Don't compare vendors by feature list; use the five criteria from Lecture 12.5. Don't quote a saving without a baseline and a method. And don't promise a hundred percent trace retention; talk about your sampling policy instead. Anyone who's run this at scale will nod.

[AVATAR]
Last tip. Whether it's an interview or a budget meeting, open with a screenshot. The red pull request, or the one-page report. Then talk. Most candidates have a story. You have the artefact the story is about.

**Recap:** Target LLMOps, AI platform, AI reliability and AI product roles, answer with a mechanism and a number, and pitch observability as three numbers and a one-sentence ask.

**Transition:** Next, the forty-question practice test, then one short bonus lecture to finish.

### Speaker notes: common student mistakes / Q&A

- "What should I expect to earn?" Don't give numbers in Q&A. Point to the structure of the roles and suggest they research local postings.
- Mistake: answering interview questions with tool names instead of mechanisms. "I'd use Langfuse" is not an answer to question five; the investigation order is.
- Mistake: portfolio READMEs with no numbers. Point back to Lecture 14.5, Slide 2.
- Keep `interview-questions.md` in sync with these twelve; if a question changes here, change it there.

---

## Lecture 15.3 — Final practice test

| Field | Value |
|---|---|
| ID | 15.3 |
| Type | QZ (40-question practice test with short video intro) |
| Target duration | 0 min in the curriculum runtime (1:00 video intro, ~90 spoken words; students take the test at their own pace) |
| Learning objectives | 1. Check end-to-end understanding across all fifteen sections. 2. Identify the two or three sections to revisit before a real project. |
| Prerequisites | Sections 1 to 14 |
| Files used | `06-assessments/practice-test.md` |

### Script

[AVATAR]
Last checkpoint. Forty questions, covering the whole course.

[SLIDE 1: Final practice test]
- 40 questions across all 15 sections
- Tracing and conventions, Langfuse, agent patterns, cost, latency, online evals, SLOs, governance, incidents, portability, deployment
- Read every explanation, even for answers you got right

The questions follow the order of the course. Tracing and the GenAI conventions first. Then Langfuse, agent patterns, cost engineering, latency and reliability, online evaluation, SLOs and alerting, governance, incidents, portability and deployment.

Take it in one sitting if you can. Most students need thirty to forty minutes.

When you finish, don't just look at the score. Look at where you missed. If three misses come from the same section, that's the section to rewatch before your next project.

[PAUSE]

Good luck. You're ready for this.

**Recap:** The practice test checks the full course and points you to the sections worth revisiting.

**Transition:** One more short video to finish the course: the bonus lecture.

### Speaker notes: common student mistakes / Q&A

- Most missed topics in beta: trigger versus root cause (Section 11) and what the budget gate cannot catch (Section 13). Point to Lecture 11.5 and Lecture 13.3.
- Second: "scores move with spans between backends". They don't. Lecture 12.1.
- "Can I retake it?" Yes. Udemy practice tests can be retaken and the explanations stay available.

---

## Lecture 15.4 — Bonus Lecture: keep operating

| Field | Value |
|---|---|
| ID | 15.4 (uploaded last; must remain the final lecture of the course) |
| Type | TH (talking head / avatar) |
| Target duration | 5:00 (~580 spoken words) |
| Learning objectives | 1. Know where to get help and updates after the course: the Q&A, the repo README and announcements. 2. Know which of the instructor's other courses cover related topics, and who each one is for. |
| Prerequisites | None |
| Files used | None. Links go in the lecture's resources panel. |

> **Udemy bonus-lecture rules (production notes; check the current Udemy Instructor Help Center before publishing):**
> - This must be the **last** lecture in the course, and its title should begin with "Bonus Lecture".
> - Promotion of other courses belongs **only** here, not in any other lecture, welcome message or quiz.
> - Keep it informative and low-pressure: say who each course is for; no countdown or urgency language.
> - Link only to the instructor's own Udemy courses (Udemy course links or instructor coupon links). No off-platform course sales.
> - No personal contact details for off-platform paid services, and no requests for reviews in exchange for anything.

### Script

[AVATAR]
You made it to the very end. This is a short bonus lecture. I'll cover how to keep your Atlas project current, how to get help, and, if you want to go deeper, which of my other courses fit with this one. That last part is completely optional.

[SLIDE 1: Keeping your project current]
- Observability libraries release often; the GenAI conventions are still incubating
- The repo README lists the tested versions: langfuse 4.15, opentelemetry-sdk 1.45, semconv 0.66, langsmith 0.14
- Course announcements flag breaking changes
- Pin your versions; upgrade on a branch with the budget gate running

First, updates. This field moves fast. Langfuse ships often, the OpenTelemetry GenAI conventions are still marked incubating, and attribute names may change before they stabilise. Every script in this course was checked against the versions in the README: Langfuse four fifteen, OpenTelemetry SDK one forty-five, semantic conventions zero sixty-six, LangSmith zero fourteen.

When something changes, I update the repo README first, with the tested versions and any code changes. Big changes also go out as a course announcement.

For your own project, pin your versions, as we did in `pyproject.toml`. Upgrade on a branch, with the budget gate running, and read the deprecation warnings. Here's a routine that works: once a month, read the changelogs for Langfuse, the OTel SDK and the semantic conventions. Upgrade on a branch. Run `make test` and `make budget-check`. If the numbers hold, merge, and keep the rollback ready. Twenty minutes a month keeps you off the "it broke on Friday" list, which after Section 11 you know is a real list.

[SLIDE 2: Getting help]
- Q&A: include your command, the full error and your package versions
- Search the Q&A first: most setup and Docker issues are answered there
- Share your capstone numbers and your Grafana screenshot: it helps other students

Second, help. The Q&A stays open. When you post, include three things: the exact command you ran, the full error message, and your package versions. That turns a two-day back-and-forth into a one-reply fix. Search first; most Docker Compose and Langfuse self-host questions have been answered.

And please share your capstone numbers and your dashboard screenshot. Other students learn from seeing different agents and different SLIs, and so do I. Some of the best improvements to this course came from student questions, so if something was confusing, say so. That feedback shapes the next update.

[SLIDE 3: Related courses (optional)]
- *Generative AI & AI Agents: Zero to Production*: build text agents from first principles
- *AI Agent Testing & Evaluation*: offline evals, judges, datasets and test strategy
- *Production Voice AI Agents with Python*: real-time agents, latency budgets and telephony
- Links are in the resources panel for this lecture

Third, and only if it's useful to you: this course is part of a set.

*Generative AI & AI Agents: Zero to Production* is the building course. It's for you if Section 5, the agent internals, felt fast. It covers prompting, tools, retrieval and agent design from first principles.

*AI Agent Testing & Evaluation* is the testing course. It's for you if Section 8 was your favourite, or if you own quality on your team. It goes much deeper on evaluation design, LLM judges, datasets and test strategy than we had room for here, and the dataset you built in Lecture 8.6 is exactly what it consumes.

*Production Voice AI Agents with Python* is the real-time course. It's for you if the latency budgets in Section 7 interested you, or if the domain swap in Lecture 14.6 made you want to build the voice agent you instrumented.

You don't need any of them to use what you've learned here. The links are in the resources panel for this lecture if you want to take a look.

[SLIDE 4: Thank you]
- Finish the capstone
- Send the report
- Keep the gate green

[AVATAR]
That's it. Thank you for taking this course, and for sticking with it all the way to an agent you can see, explain, cap and defend. Finish the capstone. Send the report. Keep the gate green.

I'll see you in the Q&A.

**Recap:** Keep your project current through the repo README and a monthly upgrade routine, get help in the Q&A with command, error and versions, and, optionally, go deeper with the Build, Test and Deploy courses.

**Transition:** This is the final lecture of the course. Thank you for learning with me.

### Speaker notes: common student mistakes / Q&A

- Keep this lecture free of discount countdowns, "limited time" language or repeated calls to action. Mention each course once, with who it's for.
- Put course links only in this lecture's resources panel. Use Udemy course URLs or official instructor coupon links, never off-platform checkout pages.
- If a student asks for a discount in the Q&A, share the current instructor coupon in the reply rather than adding promotion to other lectures.
- Review this lecture whenever Udemy updates its promotional guidelines, and before every major course update. If lectures are added to the course later, this one must move to stay last.
