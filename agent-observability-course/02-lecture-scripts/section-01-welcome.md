# Section 1: Welcome: The $4,000 Weekend

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈36 min (6 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating) / openinference-instrumentation-openai 0.1.61; check the repo README for updates."

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with Atlas, the swarm or a dashboard. Record the real output. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word counts in each header are spoken words only, not cues or code. Where talking time is shorter than the target duration, the rest is demo output, live typing, command output and on-screen dwell. Code-along lectures are paced below 140 words per minute to leave room for typing.

**Money on screen:** every dollar figure in this section comes from the offline mock LLM's realistic token counts multiplied by the real `litellm.model_cost` price table (`gpt-4.1-mini`: $0.40 per million input tokens, $1.60 per million output; `gpt-4.1`: $2.00 and $8.00). No live API calls are made while recording Section 1. Say so on screen at least once.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 1.1 | The $4,000 weekend: watch an agent burn money in real time | DM | 5:00 | ~575 |
| 1.2 | What LLMOps means for agents (and why MLOps tools miss it) | SL | 8:00 | ~775 |
| 1.3 | The observability stack you will build | SL | 7:00 | ~750 |
| 1.4 | Meet Atlas and the swarm | SC | 7:00 | ~700 |
| 1.5 | Course roadmap and how to get the most out of it | SC | 6:00 | ~550 |
| 1.6 | Quiz: Foundations | QZ | 3:00 (1:00 video) | ~125 |

---

## Lecture 1.1 — The $4,000 weekend: watch an agent burn money in real time

| Field | Value |
|---|---|
| ID | 1.1 |
| Type | DM (live demo, two runs, before/after) |
| Target duration | 5:00 (~575 spoken words, about 4:06 of talking at 140 wpm, plus dwell on the meter) |
| Learning objectives | 1. Watch an agent enter a retry loop and see cost climb step by step. 2. Name the three things that stopped it in the second run: a step limit, a budget guard and an alert. 3. State what this course promises: you will be able to see, explain and stop this. |
| Prerequisites | None |
| Files used | `03-code/simulator/scenarios.py::loop`, `03-code/console/ops_console.py`, `03-code/app/agent.py` (step limit), `03-code/src/northwind/budget.py` |

**Recording note:** three terminals and one browser tab. Terminal 1 runs Atlas, Terminal 2 runs the swarm with the `loop` scenario, the browser shows the Ops Console cost meter at `http://localhost:8501`. Record the meter climbing for real; do not speed it up. The first run uses `ATLAS_MAX_STEPS=0` (unlimited) so the loop can run; the second run uses the default guards. Tint the first run red, the second green.

### Script

[SCREEN: Ops Console, "Live cost" page. A single large number: "$0.00". Below it, a table of tenants: ops, finance, hr, eng, all at $0.00. Terminal 1 visible in a corner: `OFFLINE=1 make run` already serving Atlas on port 8000.]

Friday, 6:04 in the evening. Northwind Logistics' ticket system goes down for maintenance. Nobody tells Atlas, the helpdesk agent. Watch the number.

[SCREEN: Terminal 2.]

[CODE: start the swarm with the loop scenario, guards off]
```bash
ATLAS_MAX_STEPS=0 OFFLINE=1 make swarm SCENARIO=loop
```

[DEMO: The swarm sends one request: "Where is my ticket INC-2231?" from a warehouse employee. Terminal 1 logs a tool call to `lookup_ticket`, then `ToolError: ticketing API 503`, then another call. The Ops Console meter starts moving: $0.01, $0.03, $0.06. A "steps" counter next to it climbs: 4, 5, 6.]

One question. "Where is my ticket?" Atlas calls the ticket tool. The tool returns a 503. Atlas reads the error, decides to try again, and calls the tool again. [PAUSE] Same error.

Look at the meter. Six cents. Nine cents. Fourteen cents.

[SCREEN: Zoom on the console's "context size" sparkline, which is climbing in a straight line.]

Here is why it accelerates. Every failed call is appended to the conversation. The error message, the tool arguments, the model's reasoning about retrying. Step one sent about two thousand tokens to the model. Step ten sends thirteen thousand. Step twenty sends twenty-four thousand. Every retry pays for every previous retry again.

[DEMO: Meter passes $0.50 around step 14. Terminal 1 log shows "escalating to gpt-4.1 after repeated tool errors".]

And there is a second multiplier. Atlas has a rule: if the small model keeps failing, escalate to the big one. Sensible, in a normal conversation. Here it means every one of those twenty-thousand-token retries now costs five times as much.

[DEMO: Let it run until the meter reads about $0.96 and steps reads 22, then press Ctrl+C in Terminal 2.]

I'll stop it there. Twenty-two steps. Ninety-six cents. For one question that was never answered. Left alone, this conversation runs until the HTTP client times out at ten minutes, around step sixty, at three dollars and ninety cents.

[SLIDE 1: The weekend, in numbers]
- Ticket system down: Friday 18:04 to Monday 07:30
- Employees asking about tickets: about 1,000 conversations
- Cost per stuck conversation: ≈ $3.90
- Total: ≈ $3,900. Nobody noticed until the Monday invoice email.

Now multiply. About a thousand employees asked about a ticket over that weekend. Each conversation looped to the timeout. Three dollars ninety, a thousand times. Roughly four thousand dollars, for zero resolved tickets, and nobody knew until Monday morning.

[PAUSE]

None of this is exotic. The tool failed, the agent was persistent, and no one was watching. That is the default behaviour of an agent loop.

[AVATAR]
Now let's run exactly the same outage against the same agent, with three things switched on. A step limit. A budget guard per tenant. And an alert.

[SCREEN: Terminal 2. Same command without the override.]

[CODE: the same scenario, guards on]
```bash
OFFLINE=1 make swarm SCENARIO=loop
```

[DEMO: Same request. Terminal 1 logs `lookup_ticket` 503 twice, then "step limit 8 reached, surfacing error to user". Atlas replies: "The ticketing system isn't responding right now. I've noted your ticket INC-2231 and will retry in the background. You'll get an email when it's back." Meter stops at $0.04. The console's "Alerts" panel shows one line: "tool_error_rate lookup_ticket 100% over 60 s (ops)".]

Same question, same broken tool. This time Atlas tries, tries once more, and at step eight it stops and tells the employee the truth. Four cents. [PAUSE] The alerts panel fired on the tool error rate within a minute, so an on-call engineer would have known Friday at 6:05, not Monday at 9.

[SLIDE 2: Before and after]
| | Friday run | Guarded run |
|---|---|---|
| Steps | 60 (timeout) | 8 (limit) |
| Cost per conversation | $3.90 | $0.04 |
| Weekend cost | ≈ $3,900 | ≈ $40 |
| Time to detection | 63 hours | 1 minute |
| Employee experience | silence, then timeout | honest answer in 6 s |

Three ninety versus four cents. Sixty-three hours versus one minute. And the guarded version is a better product, because the employee got an honest answer in six seconds instead of a spinner.

[AVATAR]
Here's what I want you to notice. The fix was not clever. A step limit is one integer. A budget guard is a comparison. An alert is a threshold. What was missing was the ability to see what the agent was doing, in tokens and dollars, while it was doing it.

That is this course. By Section fourteen you will have instrumented Atlas with OpenTelemetry, traced every step in Langfuse, priced every token, set budgets per department, measured latency and quality on live traffic, and built the console you just watched. And in Section eleven, you'll be handed three incidents like this one and asked to find the root cause from traces alone.

One more thing. Everything you just saw ran offline. No API key, no money spent. The token counts came from a deterministic mock, the prices came from the real price table. You'll be able to reproduce it in Lecture 2.4.

**Recap:** An agent that retries a failing tool grows its context every step and can burn dollars per conversation; a step limit, a budget guard and an alert turned $3,900 into $40 and sixty-three hours into one minute.

**Transition:** Next, why the tools you already have for monitoring software mostly miss this, and what LLMOps for agents actually means.

### Speaker notes: common student mistakes / Q&A

- "Was this a real invoice?" The scenario is fictional and the numbers are computed offline, but the shape is common: failing tool plus persistent agent plus escalation rule. Say so if asked; do not present it as a real company's bill.
- If the meter does not move during recording, the console is probably reading an empty local store. Check that `OFFLINE=1` is set in Terminal 1 too, so spans go to the local store the console reads.
- Students sometimes ask why the small model was escalated. The rule "retry with a bigger model on failure" is a real pattern people ship. It becomes routing in Section 6.6, with a cost ceiling.
- Do not explain traces, spans or Langfuse here. This lecture is only the hook and the promise.

---

## Lecture 1.2 — What LLMOps means for agents (and why MLOps tools miss it)

| Field | Value |
|---|---|
| ID | 1.2 |
| Type | SL (slides) |
| Target duration | 8:00 (~775 spoken words, about 5:32 of talking at 140 wpm) |
| Learning objectives | 1. Name the four properties that make agents different to monitor: non-deterministic, multi-step, tool-using, token-metered. 2. Describe the three pillars of agent observability: traces, quality in production, cost. 3. Explain where classic APM and classic MLOps stop and why. |
| Prerequisites | 1.1 |
| Files used | Diagram: three pillars (slides 4 and 8) |

### Script

[AVATAR]
Northwind already had monitoring. Datadog on the servers. Uptime checks on the API. Every dashboard was green all weekend. [PAUSE] Green, while the agent spent four thousand dollars. So the question isn't "did they have observability." It's "observability of what?" Let's work out exactly what an agent needs watched, and why the tools you already own don't do it.

[SLIDE 1: What Northwind's dashboards showed on Friday night]
- HTTP 200 rate: 100%
- p95 response time: within budget (requests timed out cleanly at 10 min)
- CPU, memory, error logs: normal
- OpenAI billing page: updates once a day

Every request returned. The servers were bored. The one number that mattered, dollars per conversation, wasn't on any screen, because the billing page updates daily and nothing in the app knew what a token cost.

[SLIDE 2: Four things that make agents different]
- Non-deterministic: the same input takes different paths
- Multi-step: one request becomes 3, 8 or 60 model calls
- Tool-using: the model decides which functions run, with what arguments
- Token-metered: cost is a function of what the model saw, not of request count

Four properties. First, agents are non-deterministic. The same question can take a different path on Tuesday than it did on Monday, so a passing test yesterday tells you little about production today.

Second, multi-step. A web request is one request. An agent request is a loop. Three steps if things go well. Sixty if they don't. Your request count stays flat while your model calls go up twenty times.

Third, tool use. The model decides which of your functions to call and with which arguments. That decision is invisible to the tool itself and to your HTTP logs.

Fourth, token-metered. Cost is not "requests times price." It's every token the model read and wrote, and the model reads the whole history every step. That is why the meter in the last lecture accelerated instead of climbing in a straight line.

[SLIDE 3: Where classic APM stops]
Diagram: a trace waterfall for `POST /chat`. One big bar, 9.8 s, status 200. Inside it, a grey box labelled "???" spanning 9.6 s. Callout: "60 model calls, 59 tool errors, 480k tokens, $3.90, all inside this box."

Classic application performance monitoring sees this. One span for the HTTP request. Nine point eight seconds, status two hundred. Everything interesting happened inside that grey box, and APM has no vocabulary for it. It doesn't know what a model call is, what a tool call is, or what a token costs.

[SLIDE 4: Where classic MLOps stops]
- Built for models you train: feature drift, model registry, batch scoring
- Assumes one prediction per request and a fixed schema
- Cost model: GPU hours, not tokens per conversation
- No concept of a tool call or a multi-step plan

MLOps tools have the opposite gap. They were built for models you train and deploy yourself. Feature drift, model registries, batch scoring jobs. Valuable, and mostly irrelevant here. You didn't train the model. You call it. And your "prediction" is a sixty-step conversation, not a row of numbers.

[PAUSE]

So what do we need instead? Three things.

[SLIDE 5: Pillar 1: Traces]
- Every request becomes a tree: agent → steps → model calls and tool calls
- Each node carries: inputs, outputs, tokens, latency, errors
- Answers: what did it do, in what order, and why?

Pillar one, traces. Every request becomes a tree. The agent at the root, each step below it, and under each step the model call and any tool calls, with their inputs, outputs, token counts and timings. A trace answers the question APM couldn't: what exactly happened inside the grey box?

[SLIDE 6: Pillar 2: Quality in production]
- Did the user get what they needed? Resolved, grounded, safe
- Measured on live traffic: sampled LLM-as-judge, user feedback, drift vs last week
- Answers: is it getting better or worse, and where?

Pillar two, quality in production. Traces tell you what happened. They don't tell you whether it was any good. For that you sample live conversations and score them: was the question resolved, was the answer grounded in the knowledge base, was the escalation appropriate. You collect thumbs up and down. And you compare this week to last week, because quality drifts silently when a prompt changes or a provider updates a model.

[SLIDE 7: Pillar 3: Cost]
- Price every token on every model call: input, output, cached, reasoning
- Roll up by request, session, user, tenant, feature
- Budgets and anomaly alerts, not a monthly invoice
- Answers: who is spending what, on which feature, and is it normal?

Pillar three, cost. Price every token at the moment it's used. Roll it up by session, by user, by department, by feature. Set budgets. Alert on anomalies. The goal is that a four-thousand-dollar weekend becomes a Slack message at 6:05 on Friday.

[SLIDE 8: The three pillars share one foundation]
Diagram: three columns, Traces, Quality, Cost, standing on one base labelled "Instrumented agent: every model call, tool call and step emits a span with GenAI attributes". Arrows from the base into each column.

Here's the important part. All three pillars stand on one foundation: an instrumented agent. If every model call, tool call and step emits a span with the right attributes, then traces are just those spans arranged as a tree, cost is those spans multiplied by a price table, and quality scores are attached to those same spans. Instrument once, get all three. That's why Sections two through five are about instrumentation before we touch cost or quality.

[SLIDE 9: A definition you can say out loud]
LLMOps for agents = running LLM-powered, multi-step, tool-using systems in production with traces, quality measurement and cost control, so you can see, explain and stop what they do.

If someone asks what LLMOps means, here's a definition that fits in one breath. Running LLM-powered, multi-step, tool-using systems in production, with traces, quality measurement and cost control, so you can see, explain and stop what they do.

[SLIDE 10: What this looks like on Monday morning]
- APM: "All systems operational"
- LLMOps: "ops tenant spent 40× its daily budget on 1,012 conversations that all called lookup_ticket and all failed at the same tool. Root cause: ticketing API 503 from 18:04 Friday."

Same weekend, two Monday mornings. With APM alone, "all systems operational." With the three pillars, a sentence with a tenant, a count, a tool name, a root cause and a timestamp. You'll write that exact sentence yourself in Section eleven.

[AVATAR]
So, keep the four properties in mind: non-deterministic, multi-step, tool-using, token-metered. Every technique in this course exists because of one of those four. And keep the three pillars: traces, quality, cost. Every lecture belongs to one of them.

**Recap:** Agents are non-deterministic, multi-step, tool-using and token-metered, which is why APM and MLOps tools show green while an agent burns money; you need traces, quality in production and cost, all built on one instrumented agent.

**Transition:** Next, the specific tools you'll use for each pillar, and why the stack is built so you can swap any of them.

### Speaker notes: common student mistakes / Q&A

- "Isn't this just logging?" Logs are one signal. A log line can't tell you that a tool call belonged to step 14 of a conversation that cost $3.90. Traces carry structure; Lecture 5.5 compares logs, traces and metrics.
- "Can't I just set a hard spending cap at OpenAI?" Yes, and you should (Lecture 2.1). A cap stops the bleeding for the whole account; it doesn't tell you which tenant or tool caused it, and it takes the whole product down instead of one feature.
- Students from an MLOps background may object that drift detection exists in their tools. Agree, then point out the unit of analysis is different: a conversation with tool calls, not a feature vector.
- Do not name specific competitor pricing here. Section 12 covers the vendor landscape.

---

## Lecture 1.3 — The observability stack you will build

| Field | Value |
|---|---|
| ID | 1.3 |
| Type | SL (slides) |
| Target duration | 7:00 (~750 spoken words, about 5:21 of talking at 140 wpm) |
| Learning objectives | 1. Name the role of each component: OpenTelemetry as the wire format, Langfuse as the LLM-native backend, Prometheus and Grafana for metrics, LiteLLM for prices and routing. 2. Explain the portability argument: emit OTel once, point it at any backend. 3. Know which parts are open source and what the student spend is. |
| Prerequisites | 1.2 |
| Files used | Diagram: architecture (slides 2 and 7); `03-code/telemetry/` (mentioned, not opened) |

### Script

[AVATAR]
Here's a trap people fall into in their first week of LLM observability. They pick a vendor, sprinkle its SDK through the code, and six months later the vendor doubles its price or gets acquired. Now the SDK is in four hundred places. [PAUSE] We're going to build a stack where that can't happen to you. Every component has one job, and the one in the middle is a standard, not a product.

[SLIDE 1: One agent, four questions]
- What did it do? → traces
- What did it cost? → prices × tokens
- Is it healthy right now? → metrics and alerts
- Is it any good? → scores

Four questions we need answered about Atlas. What did it do. What did it cost. Is it healthy right now. Is it any good. Each one gets a tool, and the tools talk to each other through a standard.

[SLIDE 2: The stack]
Diagram, built progressively:
1. Centre: "Atlas (FastAPI + agent loop)".
2. Below it: "OpenTelemetry SDK: spans with GenAI semantic conventions". Label: "the wire format".
3. Right: arrow from OTel to "Langfuse: traces, sessions, prompts, scores, datasets". Label: "LLM-native backend".
4. Left: arrow from Atlas to "Prometheus → Grafana: counters, histograms, alerts". Label: "metrics".
5. Inside Atlas: a small box "LiteLLM: price table, Router, budgets". Label: "cost and routing".
6. Bottom: "Ops Console (Streamlit) over a local store" with the label "offline mode".

Let's build the picture. In the middle, Atlas. It's a FastAPI service with a tool-calling loop inside.

Underneath Atlas, OpenTelemetry. Every step, model call and tool call becomes an OpenTelemetry span, and every span carries attributes from the GenAI semantic conventions. That means the model name, the token counts, the tool name and arguments all have standard names that any backend understands. OpenTelemetry is the wire format. It's a standard, maintained by the CNCF, used by every major backend.

To the right, Langfuse. This is where spans go to become traces you can click through. Langfuse also holds things OpenTelemetry has no concept of: sessions and users, prompt versions, quality scores and datasets. Version four of its Python SDK is itself built on OpenTelemetry, so the two fit together with almost no glue. You'll see that in Section four.

To the left, Prometheus and Grafana. Traces are for individual requests. When you want "tool error rate over the last five minutes" or "cost per hour by tenant," you want metrics. Atlas exposes them at slash metrics, Prometheus scrapes them, Grafana draws them and fires alerts. That's Section nine.

Inside Atlas, LiteLLM. We use it for two things. Its price table, which knows what a million tokens of each model cost, and its Router, which lets Atlas try a small model first and fall back to a bigger one or another provider. Sections six and seven.

And at the bottom, the Ops Console. A small Streamlit app over a local SQLite store. It's what you watched in Lecture 1.1, and it's how every lab works without spending money.

[SLIDE 3: Why OpenTelemetry in the middle]
- Emit once, in a standard format
- Point it at Langfuse today, Phoenix or Datadog tomorrow, or two at once
- The GenAI semantic conventions give tokens, models and tools standard names
- Your instrumentation code has zero vendor imports

Now the portability argument. Because Atlas emits OpenTelemetry, the instrumentation code has zero vendor imports. If you want to try Arize Phoenix next quarter, you change an exporter endpoint. If your company mandates Datadog, same thing. If you want Langfuse and a collector feeding Grafana at the same time, an OpenTelemetry Collector fans out to both. Section twelve does exactly this: same Atlas, traced to three backends, with a one-line change each time.

[SLIDE 4: What is not portable]
- Scores, prompts, datasets, dashboards live in the backend
- Choose the backend for those features; the traces will follow you anywhere
- Keep vendor SDK calls in one module: `telemetry/langfuse_setup.py`

Be honest about what isn't portable. Scores, prompt versions, datasets and dashboards live in the backend. That's fine. Choose your backend for those features, and know the traces themselves will follow you anywhere. And keep the vendor-specific calls in one module. In our repo that's telemetry slash langfuse setup. When the day comes to switch, you edit one file, not four hundred.

[SLIDE 5: Open source and cost]
| Component | Licence | What you pay |
|---|---|---|
| OpenTelemetry | Apache 2.0 | nothing |
| Langfuse | MIT (self-host) or Cloud free tier | nothing for this course |
| Prometheus, Grafana | Apache 2.0 / AGPL | nothing |
| LiteLLM | MIT | nothing |
| OpenAI API | pay as you go | ≈ $5-15 across the whole course, with a hard cap |

Everything in the stack is open source. Langfuse has a free cloud tier that's plenty for this course, and in Section thirteen you'll self-host it with Docker Compose. The only thing you pay for is the OpenAI API, and with offline mode and a hard cap, that's five to fifteen dollars for the entire course.

[SLIDE 6: Alternatives you'll meet]
- LangSmith (Section 12.2): same Atlas, `traceable` and `wrap_openai`
- Arize Phoenix (12.3): OTLP endpoint swap, OpenInference conventions
- OpenLLMetry, Datadog LLM Observability (12.4): when you already have an APM
- Decision matrix in 12.5

You'll also meet the alternatives, hands on, in Section twelve. LangSmith, Arize Phoenix, OpenLLMetry and Datadog's LLM observability. Not to sell you on one, but so you can make the decision with a matrix instead of a gut feeling.

[SLIDE 7: The stack, once more, with sections]
Diagram from slide 2, each box labelled with the sections that build it: OTel (3), Langfuse (4, 5, 8), LiteLLM (6, 7), Prometheus/Grafana (9), Console (2, 14), Collector and Compose (13), alternatives (12).

Here's the same diagram with section numbers. Section three builds the OpenTelemetry layer. Four, five and eight build out Langfuse. Six and seven are LiteLLM for cost and reliability. Nine is metrics and dashboards. Thirteen deploys it all. Fourteen assembles it into the capstone.

[AVATAR]
Four tools, one standard in the middle. If you remember one thing from this lecture: emit OpenTelemetry once, with the GenAI conventions, and every backend decision becomes reversible.

**Recap:** OpenTelemetry is the wire format, Langfuse is the LLM-native backend for traces, prompts and scores, Prometheus and Grafana handle metrics and alerts, LiteLLM handles prices and routing, and because the middle is a standard, every vendor choice is reversible.

**Transition:** Time to meet the agent that will emit all of this: Atlas, and the swarm that keeps it busy.

### Speaker notes: common student mistakes / Q&A

- "Why not just use the Langfuse SDK everywhere?" You will use it, in one module. The point is that the spans it emits are OpenTelemetry spans, so the rest of the code doesn't know or care.
- "Do I need Docker for this section?" No. Docker appears in Section 13. Everything before that runs with Python and, optionally, Langfuse Cloud.
- "What about Anthropic, Gemini, local models?" The GenAI conventions and LiteLLM are provider-agnostic. Atlas defaults to OpenAI models via env vars in `src/northwind/config.py`; swapping the provider is a config change plus a price-table entry.
- Do not open code in this lecture. The repo tour is 1.4.

---

## Lecture 1.4 — Meet Atlas and the swarm

| Field | Value |
|---|---|
| ID | 1.4 |
| Type | SC (screencast tour, no typing) |
| Target duration | 7:00 (~700 spoken words, about 5:00 of talking at 140 wpm, plus scrolling and dwell) |
| Learning objectives | 1. Describe what Atlas does: knowledge base answers, ticket lookup and creation, verified password resets, shipment checks, for four department tenants. 2. Locate the agent loop, tools, server and simulator in the repo. 3. Explain what the swarm and offline mode are for and why every lab has an offline path. |
| Prerequisites | 1.3 |
| Files used | `03-code/app/agent.py`, `03-code/app/tools.py`, `03-code/app/server.py`, `03-code/app/mock_llm.py`, `03-code/simulator/personas.py`, `03-code/simulator/scenarios.py`, `03-code/simulator/swarm.py`, `03-code/simulator/replay.py`, `03-code/src/northwind/data/kb/` |

### Script

[AVATAR]
You can't learn observability on a toy. A single prompt with one model call has nothing to observe. So this course gives you a real-shaped agent, a company for it to serve, and a day of traffic to serve them with. Let me introduce all three.

[SLIDE 1: Northwind Logistics]
- Fictional freight company, about 2,000 employees
- Four departments as tenants: `ops`, `finance`, `hr`, `eng`
- Atlas: the internal IT and HR helpdesk agent
- Served over HTTP so traffic can be generated

Northwind Logistics is a fictional freight company with about two thousand employees in four departments: operations, finance, HR and engineering. Those four departments are our tenants. Each one gets its own budget, its own tags and its own line in every report.

Atlas is their internal helpdesk agent. Employees ask it about the VPN, laptop policy, leave, expenses, payroll dates. It looks up and creates tickets. It resets passwords, after verifying who you are. And because it's a logistics company, it checks shipment status.

[SCREEN: VS Code, repo `03-code/` open. Expand `app/`.]

Let's look at the code. Everything about the agent lives in the app folder.

[SCREEN: Open `app/agent.py`. Scroll to the `AtlasAgent` class and its `run` method. Highlight the `while` loop, the `max_steps` check and the escalation branch.]

Agent dot py holds the `AtlasAgent` class. At its heart is a loop. Build the messages, call the model, and if the model asked for a tool, run the tool, append the result and go around again. Two things to notice now, because you'll instrument them in Section five. There's a step limit, `max_steps`, which was switched off in the Friday run. And there's an escalation branch that swaps in the bigger model.

[SCREEN: Open `app/tools.py`. Scroll through the five function definitions.]

Tools dot py has the five tools. `search_knowledge_base`, which runs a small BM25 retriever over markdown files. `lookup_ticket` and `create_ticket`, which talk to a fake ticketing system that can be told to fail. `reset_password`, which insists on a verification step first. And `check_shipment`. Five tools is enough to be interesting and few enough to keep in your head.

[SCREEN: Open `src/northwind/data/kb/`. Show the list of markdown files: vpn.md, laptop-policy.md, leave.md, expenses.md, security.md, onboarding.md, payroll-dates.md.]

The knowledge base is seven markdown files. Real enough that retrieval quality is measurable, small enough to read in ten minutes.

[SCREEN: Open `app/server.py`. Highlight the `POST /chat` route and the header handling for tenant, user and session.]

Server dot py wraps the agent in FastAPI. One route matters most: post slash chat. Every request carries three headers, tenant, user and session. Those three headers become the three most important dimensions in every trace and every cost report. There's also slash feedback for thumbs up and down, slash metrics for Prometheus, and slash healthz.

[SLIDE 2: Why an agent over HTTP?]
- Traffic can be generated, replayed and load-tested
- Tenant, user and session arrive as headers, exactly as in production
- Observability is about what happens under load, not in a notebook

Why HTTP? Because observability is about what happens under load, not in a notebook. Serving Atlas over HTTP means we can generate traffic, replay it, and break it on purpose.

[SCREEN: Expand `simulator/`. Open `simulator/personas.py`, scroll through a few persona entries.]

Which brings us to the swarm. Personas dot py defines employees: a department, a set of likely questions, and a misbehaviour rate. Some personas ramble. About two percent try prompt injection, because in a company of two thousand, some people will.

[SCREEN: Open `simulator/scenarios.py`. Highlight the list of scenario names: `loop`, `context_bloat`, `retry_storm`, `slow_provider`, `prompt_regression`.]

Scenarios dot py defines a normal day of traffic, and five incidents you can inject into it. `loop`, which you saw. `context_bloat`. `retry_storm`. `slow_provider`. And `prompt_regression`. Each one is the seed of an incident lab in Section eleven.

[SCREEN: Open `simulator/swarm.py` briefly, then `simulator/replay.py`.]

Swarm dot py drives the FastAPI app at a configurable rate, with a fixed random seed, so a run is reproducible. Replay dot py is the shortcut: it emits the whole day of spans directly, with no HTTP and no model calls, in about forty seconds.

[SCREEN: Open `app/mock_llm.py`. Highlight the usage and latency generation.]

And the piece that makes all of this free: mock LLM dot py. When `OFFLINE=1` is set, Atlas calls this instead of OpenAI. It's deterministic, it picks tool calls the way the real model would for each persona, and it returns realistic token counts and latencies, so the traces, costs and p95s you see are shaped like production.

[SLIDE 3: Every lab has an offline path]
- `OFFLINE=1`: mock LLM, local span store, Ops Console
- Same code path, same spans, same dashboards, zero spend
- Live mode: set `OPENAI_API_KEY`, point at Langfuse Cloud, run a few real requests
- Recommended: offline for exploration, live for the screenshot

Every lab in this course works offline. Same code, same spans, same dashboards, zero dollars. Use offline to explore and break things freely. Switch to live mode when you want a real trace in Langfuse Cloud for your screenshot. That's how you keep the whole course under fifteen dollars.

[AVATAR]
Atlas, four tenants, five tools, a swarm with five injectable incidents, and a mock that makes it all free. Everything you observe from here on comes from this system.

**Recap:** Atlas is a FastAPI-served tool-calling agent for Northwind's four departments, the swarm replays a realistic day with injectable incidents, and `OFFLINE=1` swaps in a deterministic mock so every lab runs for free.

**Transition:** Next, the roadmap for the fifteen sections, and three habits that will get you the most out of them.

### Speaker notes: common student mistakes / Q&A

- Students sometimes try to "improve" the mock LLM to be smarter. Its job is to be deterministic and realistic in shape, not clever. Keep it boring.
- "Can I use my own agent instead of Atlas?" Yes, and Lecture 14.6 is exactly that. Follow along with Atlas first so the incidents line up.
- The five scenario names are referenced by exact string in the Makefile, the incident data and Section 11. Do not rename them.
- If `app/agent.py` has changed at recording time, match the class and method names on screen to the file; the narration only relies on `AtlasAgent`, the loop, `max_steps` and escalation.

---

## Lecture 1.5 — Course roadmap and how to get the most out of it

| Field | Value |
|---|---|
| ID | 1.5 |
| Type | SC (screencast, README and slides) |
| Target duration | 6:00 (~550 spoken words, about 3:56 of talking at 140 wpm, plus README scrolling) |
| Learning objectives | 1. Map the fifteen sections onto the three pillars and the operate loop. 2. Adopt the build-log habit and know how to use Q&A. 3. Check the version banner against the installed packages before reporting a problem. |
| Prerequisites | 1.4 |
| Files used | `03-code/README.md` |

### Script

[AVATAR]
Eleven hours of video is a lot. People who finish courses like this do two things differently from people who don't. They know where they are on the map, and they keep a log. Let me give you the map and the log.

[SLIDE 1: Fifteen sections, three pillars]
| Pillar | Sections |
|---|---|
| Foundation: instrument the agent | 2 Setup · 3 OpenTelemetry · 4 Langfuse · 5 Agent patterns |
| Cost and reliability | 6 Cost engineering · 7 Latency and reliability |
| Quality and operations | 8 Online evaluation · 9 Dashboards, SLOs, alerts · 10 Governance |
| Prove it | 11 Incident labs · 12 Portability · 13 Deploy and CI · 14 Capstone · 15 Careers |

Here's the map. Sections two to five are the foundation: you instrument Atlas until every step, model call and tool call is a span with the right names, and you can read a trace fluently. Sections six and seven are money and time: pricing, caching, routing, budgets, then latency budgets, retries and fallbacks. Eight, nine and ten are quality and operations: judging live traffic, dashboards, SLOs, alerts and the privacy of your own telemetry. Then you prove it. Three incident investigations in eleven, alternative backends in twelve, deployment and CI gates in thirteen, and the capstone in fourteen.

[SLIDE 2: The first win is in Section 2]
- Lecture 2.3: one `curl`, one trace in Langfuse, about ten minutes from clone
- Lecture 2.4: a full day of traffic, offline, in the Ops Console
- Everything after that is explaining and improving those two screens

Your first win comes early. By the end of Lecture 2.3 you'll have a real trace in Langfuse from a real request. By 2.4 you'll have a full day of traffic in the console. Every lecture after that is explaining and improving those two screens.

[SLIDE 3: The signature section and the centrepiece]
- Section 6, Cost engineering: 70 minutes, ends with a challenge to cut Atlas's daily bill by 40%
- Section 11, Incident labs: you're on call; three incidents, eight minutes each to find root cause before the reveal

Two sections to look forward to. Section six is the deepest: seventy minutes on cost, ending with a challenge to cut Atlas's daily bill by forty percent and prove it. And Section eleven is where the course pays off. You get the spans and a brief. You have eight minutes. Then the reveal.

[SCREEN: VS Code, `03-code/README.md`. Scroll from the top: setup, run commands, lecture-to-file map, offline mode.]

The README is your companion. Setup at the top. Then the Make targets: install, run, swarm, replay, console, test. Then a table mapping every lecture to the files it touches, so when you come back to Section seven in two weeks you know exactly where to look.

[SCREEN: Scroll to the version banner near the top of the README.]

And this banner. langfuse four, opentelemetry SDK one forty-five, semantic conventions zero sixty-six, openinference. These libraries move fast. The Langfuse SDK went from version two to version four in about a year and changed its whole API on the way. So before you report that something on screen doesn't match your machine, check the banner, check your installed versions, and check the README's updates section. Nine times out of ten, that's the answer.

[SLIDE 4: The build log habit]
- One markdown file: `BUILD-LOG.md` in your fork
- After every lecture, three lines: what I ran, what I saw, one number
- Example: "2.4 replayed the day offline. 1,184 traces. ops tenant is 41% of cost. Why?"
- By Section 14 it's your capstone write-up and your portfolio story

Now the habit. Keep a build log. One markdown file in your fork. After every lecture, three lines: what you ran, what you saw, and one number that surprised you. "Replayed the day. Eleven hundred traces. Ops is forty-one percent of cost, why?" Those questions become your incident investigations, and by Section fourteen the log is most of your capstone write-up.

[SLIDE 5: Getting help]
- Q&A: paste the command, the error, and your version banner
- Offline first: if it fails offline, it's not your API key
- Section 11 briefs and Project 2 are spoiler-free zones; ask without revealing root cause
- Update notes live in the repo README, not in re-recorded videos

When you're stuck, use the Q&A, and include three things: the command, the error, and your version banner. Try it offline first. If it fails offline, your API key isn't the problem. And in Section eleven, please keep the Q&A spoiler-free. Ask about method, not the answer.

[AVATAR]
Map, first win, build log, versions. Now let's check what you've picked up in this section with a short quiz.

**Recap:** Sections 2-5 instrument the agent, 6-7 control cost and latency, 8-10 measure quality and run operations, and 11-14 prove it; keep a three-line build log after every lecture and check the version banner before you ask.

**Transition:** Six quick questions on the foundations, then Section 2 gets your keys, your repo and your first trace.

### Speaker notes: common student mistakes / Q&A

- Students who skip 2.4 (offline replay) struggle in Sections 6 and 11 because they have no data. Emphasise it.
- "Do I need to finish Course 2 (Testing & Evaluation) first?" No. Cross-links are marked; Section 8.6 is the only place we lean on it, and it's self-contained.
- The version banner in the README is the single source of truth for versions; update it, not the videos, when packages move.

---

## Lecture 1.6 — Quiz: Foundations

| Field | Value |
|---|---|
| ID | 1.6 |
| Type | QZ (quiz with short video intro) |
| Target duration | 3:00 total (1:00 video, ~125 spoken words, about 0:54 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of why agents need their own observability and what the three pillars are. 2. Recall the role of each stack component and what offline mode does. |
| Prerequisites | 1.1 to 1.5 |
| Files used | `06-assessments/quizzes/section-01.md` |

### Script

[AVATAR]
Six questions on the foundations. About three minutes.

[SLIDE 1: Section 1 quiz: what's covered]
- Why the Friday run got more expensive every step
- The four properties of agents and the three pillars
- Which component does what: OTel, Langfuse, Prometheus/Grafana, LiteLLM
- What is and isn't portable
- What `OFFLINE=1` changes

You'll see one question on why the loop's cost accelerated rather than climbing in a straight line, two on the four properties and three pillars, one matching each stack component to its job, one on what stays portable when you switch backends, and one on offline mode.

Tip: when a question asks "which tool," ask yourself which of the four questions it answers. What did it do, what did it cost, is it healthy, is it good.

Every answer has an explanation and points to a lecture. Miss one, rewatch that lecture. Section two assumes all of it.

**Recap:** The quiz checks the loop's cost mechanics, the pillars, the stack roles and offline mode.

**Transition:** Next, Section 2: accounts, keys, a spending cap, and your first trace in about ten minutes.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Why did the cost accelerate?" Answer: the model re-reads the whole growing history every step, so input tokens per step grow, and the escalation multiplied the price.
- Second most missed: "Which of these is portable across backends?" Answer: the spans and their GenAI attributes; not scores, prompts or dashboards.
