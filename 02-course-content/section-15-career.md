# Section 15: Career & Next Steps

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 15 (curriculum `01-curriculum/full-curriculum.md`, Module 15, ~8 min, 2 lectures; Appendix A interview bank, Appendix B 30-day plan)
> **Source of truth:** `14-quality-review/course2-bible.md` §7 (Module 15) for the portfolio demo; all project numbers are the course's offline numbers and are labelled as such.
> **Production note (A6):** no salary, job-count or market-size figures in this section, on slides or in resources. Markets differ by country and change quickly. Keep career guidance structural.
> **Positioning (T8):** never call this course or any project "first" or "only".
> **Version banner (15.1 demo):** `Verified: openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3 | langfuse 4.16.0 | mcp 2.2.0 | Python 3.11+`

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 15.1 | AI Testing Interview Questions & Career Roadmap | Teach | 5:00 | 605 |
| 15.2 | What Changes Next & Your 30-Day Practice Plan | Outro | 3:00 | 383 |

Cue legend: see `section-10-performance.md`. Word counts are spoken words only.

---

## Lecture 15.1 — AI Testing Interview Questions & Career Roadmap

| Field | Value |
|---|---|
| ID | 15.1 |
| Title | AI Testing Interview Questions & Career Roadmap |
| Type | Teach (careers talk) |
| Target duration | 5:00 (605 spoken words) |
| Learning objectives | 1. Choose between four career paths and know which project to lead with for each. 2. Answer five common AI-testing interview questions with structured, evidence-backed answers. 3. Describe your portfolio honestly, including which numbers were produced offline. |
| Prerequisites | Module 14 (Project 5 recommended) |
| Files used | `demos/m15_portfolio_summary.py`, `08-projects/` (Projects 1–5), `01-curriculum/full-curriculum.md` Appendix A (interview question bank) |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3 | langfuse 4.16.0 | mcp 2.2.0
- Python 3.11+ | portfolio numbers are offline-mode numbers

[AVATAR]
"How do you test something that gives a different answer every time?" [PAUSE] That question ends a lot of interviews. You can now answer it in two minutes, with evidence from code you wrote. Let's turn what you built into a role and an interview.

[SLIDE 2: By the end of this lecture]
- Pick one of four career paths
- Answer five common interview questions with evidence
- Describe your portfolio honestly

In five minutes: four paths, five questions, and one way to describe your projects that interviewers trust.

[SLIDE 3: Four paths from this course]
| Path | What you do day to day | Lead with |
|---|---|---|
| AI QA Engineer | golden datasets, metrics, CI gates | Projects 1 and 5 |
| AI/ML Test Lead | test strategy, metric choice, team standards | the eval pyramid and Project 5's policy |
| AI Platform Engineer | eval infrastructure, tracing, cost | Modules 9–12 and the capstone pipeline |
| AI Governance Specialist | policies, audit trails, red teaming, reporting | Project 4 and Module 13 |

Four paths. An AI QA engineer builds datasets, metrics and gates; lead with Projects 1 and 5. A test lead owns strategy and standards; lead with the eval pyramid and your evaluation policy. A platform engineer builds the infrastructure: tracing, cost, pipelines. And a governance specialist owns policy, audit and red teaming; lead with SecureBank and the audit trail. Titles vary a lot between companies, so read the job description, not the title. Coming from manual QA? The QA engineer path uses the most of what you already know. Coming from ML or backend work? The platform path is the shorter step. Which of the four sounds like your next year?

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m15_portfolio_summary.py
```

[DEMO: Output after the banner]

```text
- Agents tested: TechCorp support (5 tools), policy RAG agent, operations agent (6 tools), SecureBank, 3-agent Reply Desk
- 21 test files across a five-layer eval pyramid; 61 runnable demos
- Metrics: DeepEval (relevancy, faithfulness, hallucination, GEval, tool correctness), RAGAS 0.4, custom judges
- Security: promptfoo suite on the real agent, Garak and PyRIT configs, PII scanner, red-team report
- Ops: Langfuse v4 + OpenTelemetry GenAI traces, benchmarks, model routing, drift monitor, CI quality gate
```

Here's your portfolio in five lines. Five agents tested. Twenty-one test files across the five-layer pyramid. DeepEval, RAGAS, custom judges, promptfoo, PyRIT, Langfuse and OpenTelemetry. Put these lines in your README, and keep the ones you can demo live.

[SLIDE 4: Five questions you will hear]
1. How do you test non-deterministic output?
2. How would you cut an agent's cost?
3. How do you catch regressions from weekly updates?
4. How do you test a tool-calling agent?
5. Tell me about a quality problem you caught.

Five questions come up again and again. Here's a short, structured answer to each, built from your own work.

[SLIDE 5: Answers 1 to 3]
- Non-determinism: semantic metrics, thresholds, repeated runs, golden set
- Cost: measure first; prompt diet −43% on FAQs; routing −29%; re-check quality
- Regressions: stored baseline, 5-point tolerance, newly failing cases, nightly run

One: non-determinism. You don't assert exact strings. You score meaning with metrics like faithfulness and relevancy, set thresholds, run inputs more than once, and compare against a golden set. Two: cost. Measure first, then pull levers. In your project, a prompt diet cut FAQ cost forty-three percent and routing cut twenty-nine, offline, and you re-checked quality after each. Three: regressions. A stored baseline, a five-point tolerance, a newly-failing-cases rule, and a nightly run for the changes that never touch your repo.

[SLIDE 6: Answers 4 and 5]
- Tools: right tool, right arguments, right order; authorization in code
- STAR: a prompt edit removed the grounding rule; the CI gate blocked it
- Say "in my course project, offline mode" when it was

Four: tool-calling agents. Test tool choice, arguments and order as a trajectory, and put authorization inside the tools, not just in the prompt. SecureBank is your story. Five, the behavioural one. Use STAR. Situation: a prompt edit removed the grounding rule. Task: stop it reaching production. Action: a golden-dataset gate in CI. Result: faithfulness fell from one point oh to point two five, and the pull request was blocked.

[AVATAR]
And be precise about where numbers came from. Say "in my course project, in offline mode", when that's true. Interviewers don't mind a course project. They mind finding out later that a number wasn't what it sounded like. Precision is a testing skill. Show it.

[SLIDE 7: Three CV lines, each with a number and a source]
- Built a CI quality gate for a tool-calling support agent: golden set, 3 metrics, PR comments (course project)
- Red-teamed a banking agent: 2 of 16 attacks succeeded on v1, 0 of 16 on the fixed v2 (offline)
- Cut agent cost 29% with model routing, quality re-checked on the golden set (offline benchmark)

Here's how that looks on a CV. Each line has a verb, a number and a source. "Built a CI quality gate for a tool-calling agent, course project." "Red-teamed a banking agent: two of sixteen attacks succeeded on version one, none on the fixed version, offline." "Cut cost twenty-nine percent with routing, quality re-checked." Which line would you want to be asked about? Put that one first.

[SLIDE 8: Your next seven days]
- Push Project 5 with a README a stranger can follow
- Record a 60-second demo: the gate blocking a bad prompt
- Rehearse the five answers out loud, once each

And this week: push Project 5 with a clear README. Record a sixty-second clip of the gate blocking a bad prompt. And say the five answers out loud, once each. Saying them is very different from reading them.

[SLIDE 9: Recap]
- Pick a path; lead with the matching project
- Answer with structure and your own numbers
- Always say where a number came from

Pick a path and lead with the matching project. Answer with structure and your own numbers. And always say where a number came from.

### Recap

Four roles hire for these skills; you answer their five common questions with structure and your own project numbers, stated honestly as offline or live.

### Transition

One lecture left. In Lecture 15.2, you'll see what's likely to change in this field, and get a thirty-day plan to keep your skills sharp.

### Speaker notes: common student mistakes / Q&A

- **No salary or demand figures** (A6). If students ask, point them to local job boards and salary surveys for their country, and say the numbers change too fast to put in a course.
- **Offline vs live.** The 43% / 29% savings, the 1.00 → 0.25 faithfulness drop and the 20/20 capstone numbers are offline-mode numbers (bible §12). Students should re-run live before quoting them as model behaviour.
- **"21 test files, 61 demos"** are counted by the demo at run time; they will change if the repo changes.
- The full question bank with model answers is in the curriculum, Appendix A; the prices and percentages in some curriculum model answers are unsourced, so coach students to use their own measured numbers instead.
- This is a careers talk (A5 exemption), but it still includes one real demo.

---

## Lecture 15.2 — What Changes Next & Your 30-Day Practice Plan

| Field | Value |
|---|---|
| ID | 15.2 |
| Title | What Changes Next & Your 30-Day Practice Plan |
| Type | Outro |
| Target duration | 3:00 (383 spoken words) |
| Learning objectives | 1. Name three things in this field that will change, and the habit that keeps your work current. 2. Follow a 30-day, 30-minutes-a-day practice plan mapped to the course modules. 3. Choose a next course or project. |
| Prerequisites | 15.1 |
| Files used | `01-curriculum/full-curriculum.md` Appendix B (30-day plan), `04-code-examples/agent-eval-framework/Makefile` (`make test`, `make demos`) |

### Script

[AVATAR]
Every tool version in this course will be out of date within a year. [PAUSE] That's fine. The method won't be. Here's what's likely to change, and the thirty days that keep you sharp while it does.

[SLIDE 1: What will change, and what won't]
- Changing: library APIs (DeepEval, RAGAS, Langfuse all had breaking changes)
- Changing: standards still settling (OpenTelemetry GenAI names are "incubating", MCP is moving fast)
- Changing: models, prices and regulation (verify current pricing and rules)
- Not changing: golden sets, metrics, baselines, gates, red teams, monitoring

Three things will change. Library APIs: in this course alone, Langfuse, RAGAS and the MCP SDK all changed their APIs between major versions. Standards: the OpenTelemetry GenAI names are still marked incubating. And models, prices and regulation move every quarter. What doesn't change is the method. Golden sets, metrics, baselines, gates, red teams and monitoring. The habit that protects you is simple: when a library updates, run `make test` before anything else. If it breaks, pin the old version in `pyproject.toml`, then read the changelog. Twenty minutes of reading beats two days of guessing.

[SLIDE 2: Your 30-day plan, 30 minutes a day]
| Week | Days | Focus | Modules |
|---|---|---|---|
| 1 | 1–7 | a new agent: failures, golden set, first metrics, a custom GEval | 1–4 |
| 2 | 8–14 | RAG, tool calls, multi-agent, 5 prompt injections, a PII scan | 5–8 |
| 3 | 15–21 | tracing, benchmark, routing, synthetic data, a regression, a CI gate | 9–12 |
| 4 | 22–30 | scorecard, monitoring, the capstone on your agent, publish and practise | 13–15 |

Here's the plan: thirty minutes a day, for thirty days, on a new agent that isn't TechCorp. Week one: break it, build a golden set, add metrics. Week two: RAG, tools, multi-agent and security. Week three: tracing, cost, synthetic data and a CI gate. Week four: monitoring, the capstone on your own agent, then publish it and practise five interview answers out loud. The day-by-day version is in the course resources. Which agent will you pick?

[SLIDE 3: Where to go next]
- Course 3: Production Voice AI Agents with Python (LiveKit, Pipecat, Twilio)
- Course 4: AI Agent Observability & Cost Control (OpenTelemetry, Langfuse, LiteLLM)

If you want more, I teach two related courses. Production Voice AI Agents goes deeper into building and testing real-time voice agents on a phone line. AI Agent Observability and Cost Control goes deeper into tracing, dashboards and cutting spend across a whole fleet of agents. Neither is required. This course stands on its own.

[SLIDE 4: Recap]
- Tools change; run `make test` after upgrades
- 30 days, 30 minutes, one new agent
- Publish it, then practise the interview

Tools change, so test your tests after every upgrade. Thirty minutes a day for thirty days, on an agent of your own. And publish what you build.

[SLIDE 5: You can now]
- Answer AI-testing interview questions with your own evidence
- Keep your skills current as tools change
- Practise daily on an agent of your own

[AVATAR]
You started this course with an agent that invented its own refund policy after a one-line prompt edit. You're leaving with a platform that blocks that edit before it ships. Thank you for building it with me. Now go test something real.

### Recap

The tools will change and the method won't: keep testing with golden sets, metrics, baselines and gates, practise thirty minutes a day for thirty days, and publish your work.

### Transition

This is the last lecture of the course. Post your capstone repo in the Q&A, and share what your first gate caught.

### Speaker notes: common student mistakes / Q&A

- **Course bridges:** one line each, no sales language, no claims of being "first" or "only" (T8). Course 3 (`voice-ai-agents-course/`) uses LiveKit Agents 1.8, Pipecat 1.12 and Twilio SIP; Course 4 (`agent-observability-course/`) uses OpenTelemetry, Langfuse 4, LiteLLM, Prometheus and Grafana. Add the real Udemy links when they exist (verify).
- **30-day plan:** the day-by-day table is the curriculum's Appendix B; it should be published as a downloadable resource (T-DOCS). Day 21 "create a GitHub Actions evaluation workflow" maps to `.github/workflows/agent-eval.yml`.
- **"Which versions are current?"** Point to the bible's verified versions (openai 2.54.0, deepeval 4.2.7, ragas 0.4.3, langfuse 4.16.0, mcp 2.2.0) and to `uv.lock`; tell students to re-run `make test` after any upgrade and pin versions in `pyproject.toml` if something breaks.
- The closing line calls back to Lecture 0.1's opening failure (`demos/m00_agent_failure.py`: a one-line prompt edit makes the agent invent refund terms, a 14-day guarantee instead of 30 days); check it still matches 0.1's final script before recording.
- A5 exemption: wrap-up talk, no screen demo needed.
