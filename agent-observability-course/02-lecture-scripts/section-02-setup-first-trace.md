# Section 2: Setup and Your First Trace in 10 Minutes

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈38 min (6 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating) / openinference-instrumentation-openai 0.1.61; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only. Code-along lectures are paced below 140 words per minute to leave room for typing, command output and page loads.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 2.1 | Accounts, keys and spending caps | SC | 7:00 | ~550 |
| 2.2 | Project setup with uv and the Makefile | SC | 6:00 | ~475 |
| 2.3 | Quick win: one request, one trace | SC | 8:00 | ~575 |
| 2.4 | Offline mode: a full day of traffic for free | SC | 8:00 | ~625 |
| 2.5 | Lab 1: Environment and first trace | LAB | 4:00 (1:30 video) | ~225 |
| 2.6 | Quiz: Setup and tracing basics | QZ | 2:00 (1:00 video) | ~100 |

**Section guardrails (do not deviate on screen):** the Langfuse env vars are `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` (not the legacy `LANGFUSE_HOST`). The repo already ships fully instrumented in this section; students consume the trace here and rebuild the instrumentation by hand in Sections 3 to 5. Never type an API key on camera; paste from a password manager with the terminal input hidden, or use a key you revoke before publishing.

---

## Lecture 2.1 — Accounts, keys and spending caps

| Field | Value |
|---|---|
| ID | 2.1 |
| Type | SC (screencast: browser and `.env`) |
| Target duration | 7:00 (~550 spoken words, about 3:56 of talking at 140 wpm, plus browser navigation) |
| Learning objectives | 1. Create a Langfuse Cloud project and copy its public key, secret key and base URL. 2. Create an OpenAI project with a hard monthly cap and a low soft alert. 3. Fill `.env` from `.env.example` without committing it. |
| Prerequisites | Section 1 |
| Files used | `03-code/.env.example`, `10-resources/cost-guide.md` |

### Script

[AVATAR]
Before you write a line of code, you're going to make it impossible to have your own four-thousand-dollar weekend. Two accounts, three keys, one hard cap. Seven minutes.

[SLIDE 1: What you need]
- Langfuse Cloud project: free tier, EU or US region (or self-host in Section 13)
- OpenAI project: pay-as-you-go, with a hard cap
- `.env` filled from `.env.example`, never committed
- Expected spend for the whole course: $5-15

[SCREEN: Browser, `https://cloud.langfuse.com`. Sign up, choose a region, create an organisation and a project called `atlas-dev`.]

Start with Langfuse. Sign up at cloud dot langfuse dot com. Pick a region; EU and US are both fine, and the base URL differs, so note which one you picked. Create an organisation, then a project. Call it `atlas-dev`. In Section ten we'll talk about why you want one project per environment; for now one is enough.

[SCREEN: Project settings → API Keys → Create new API key. Show the public key, blur the secret key, and the "Host" or base URL field.]

In project settings, create an API key. You get three values: a public key starting with `pk-lf`, a secret key starting with `sk-lf`, and the base URL for your region. Copy all three now. The secret is shown once.

[SLIDE 2: Langfuse free tier]
- Generous monthly allowance of observations, plenty for this course
- Every span you send is one observation; a day of replayed traffic is thousands
- Default in this course: replay to the local store; send to Langfuse only when you want a trace to click
- Self-hosting (Section 13) has no limits

The free tier counts observations per month. Every span is one observation, and a replayed day of traffic is thousands of them. So the course defaults to sending replays to the local store, and sends to Langfuse only when you ask. You'll never hit the limit if you follow the labs as written.

[SCREEN: Browser, `https://platform.openai.com`. Create a project called `atlas-course`. Go to Billing → Limits (or the current equivalent). Set a hard monthly budget of $20 and an alert at $5.]

Now OpenAI. Create a project just for this course, `atlas-course`. Then, before you create a key, go to billing limits. Set a hard monthly budget of twenty dollars and an email alert at five. If the interface has moved since I recorded this, the resource guide has the current path. [PAUSE] This one setting is your last line of defence. Everything we build in Section six is a better line of defence, but this one works even when your code is wrong.

[SCREEN: API keys → Create new secret key, scoped to the `atlas-course` project. Copy it.]

Create a key scoped to that project. Copy it.

[SLIDE 3: Why a cap and not just care]
- Section 1 cost $3.90 per conversation with one integer switched off
- A cap turns a bad night into a bounded bill
- Later: budgets per tenant (6.7), CI budget gate (13.3), so the cap is never the thing that fires

Why insist on the cap? Because in Section one, one integer set to zero cost three dollars ninety per conversation. A hard cap turns a bad night into a bounded bill. By Section thirteen you'll have per-tenant budgets and a CI gate so the cap never actually fires. Belt, then braces.

[SCREEN: VS Code, `03-code/.env.example`. Copy to `.env`. Fill in the keys, keep `OFFLINE=1` for now.]

[CODE: create your `.env`]
```bash
cp .env.example .env
```

[CODE: `.env` (values redacted)]
```bash
OPENAI_API_KEY=sk-proj-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com    # or https://us.cloud.langfuse.com

OFFLINE=1                       # start offline; flip to 0 for live requests
ATLAS_MODEL=gpt-4.1-mini
ATLAS_ESCALATION_MODEL=gpt-4.1
```

Copy the example to dot env and fill it in. The OpenAI key. The two Langfuse keys and the base URL for your region. Leave `OFFLINE=1` for now. We'll flip it to zero for exactly one request in Lecture 2.3, then back.

The model variables are already set: `gpt-4.1-mini` for Atlas, `gpt-4.1` for escalation. Every model choice in this course is an env var, so a rename by the provider is a one-line fix.

[SCREEN: Show `.gitignore` with `.env` listed. Run `git status` to confirm `.env` does not appear.]

Dot env is in the gitignore. Check with git status. If you ever see dot env in that list, stop and fix it before you commit. A leaked key with a twenty-dollar cap is annoying; a leaked key with no cap is a very bad week.

[SLIDE 4: Cost guide]
- `10-resources/cost-guide.md`: what each section costs live, and the offline path for each
- Rule of thumb: offline to learn, live for the screenshot
- Live-only moments: 2.3 (one request), 6.4 (a cache hit), 8.2 (a judge call), 14 (a short live run)

The cost guide in the resources folder lists what each section costs if you run it live, and the offline path for each. There are only four moments in the course where live is genuinely worth it. Everything else, run offline.

[AVATAR]
Two accounts, three keys, one cap, one dot env. You're now safe to make mistakes, which is the whole point. Next, the code.

**Recap:** Create a Langfuse Cloud project and copy its two keys and base URL, create an OpenAI project with a hard cap and a soft alert, and fill `.env` from the example without ever committing it.

**Transition:** Next, one command to install everything and prove the whole repo works, offline, before you spend a cent.

### Speaker notes: common student mistakes / Q&A

- Mistake: using the wrong region's base URL. Symptom: 401 on the first flush. Check the URL against the region shown in the Langfuse UI.
- Mistake: `LANGFUSE_HOST` from older tutorials. The SDK still reads it as a fallback, but `LANGFUSE_BASE_URL` is the documented v4 variable and the one in `.env.example`.
- "Can I use an existing OpenAI key?" Yes, but a project-scoped key with its own cap is safer and makes the course's spend visible on its own line.
- "I only want to self-host Langfuse." Fine: skip the cloud signup, set `LANGFUSE_BASE_URL=http://localhost:3000` after Lecture 13.1, and use offline mode until then.

---

## Lecture 2.2 — Project setup with uv and the Makefile

| Field | Value |
|---|---|
| ID | 2.2 |
| Type | SC (code-along) |
| Target duration | 6:00 (~475 spoken words, about 3:24 of talking at 140 wpm, plus install and test output) |
| Learning objectives | 1. Install the project with `uv` via `make install`. 2. Run the offline test suite green with `make test`. 3. Start Atlas with `make run` and hit `/healthz`. |
| Prerequisites | 2.1 |
| Files used | `03-code/pyproject.toml`, `03-code/Makefile`, `03-code/README.md` |

### Script

[AVATAR]
Here's a rule I wish someone had given me years ago. Never start a course, or a job, by running the interesting command. Start by running the tests. If a hundred and fifty tests pass on your machine, every problem you hit later is yours, and that's a good thing. It means you can fix it.

[SCREEN: Terminal. Clone or open the repo, `cd 03-code`.]

[CODE: get the code]
```bash
git clone <your fork of agent-observability-course>
cd agent-observability-course/03-code
```

Clone your fork and change into the code folder. All commands in this course run from `03-code`.

[SCREEN: VS Code, `pyproject.toml`. Scroll the dependencies and the extras.]

Open pyproject. The dependencies are pinned to major versions: langfuse four, the OpenTelemetry SDK, the semantic conventions package, OpenInference for OpenAI, LiteLLM, OpenAI, FastAPI, DeepEval, Prometheus client. Below that, four extras: `dev` for tests and linting, `langsmith` and `phoenix` for Section twelve, and `dashboards` for the Streamlit console.

[SCREEN: `Makefile`. Show the targets.]

The Makefile is the front door. `install`, `run`, `swarm`, `replay`, `console`, `test`, plus `eval`, `budget-check` and `lint` for later sections. Every lecture that says "run this" uses one of these, so you never have to remember a long command.

[CODE: install]
```bash
make install
```

[DEMO: `uv sync --all-extras` runs. Output ends with the environment resolved and installed. Takes 20-60 seconds.]

Make install wraps `uv sync` with all extras. uv is fast; on a normal connection this is under a minute. If you don't have uv yet, the README has the one-line installer for your platform.

[CODE: run the tests, offline]
```bash
make test
```

[DEMO: pytest runs unit and integration tests in offline mode. Output ends with something like `168 passed in 9.4s`.]

Now the tests. Make test runs the unit suite over the pure-Python package, `src/northwind`, and the integration suite, which starts the FastAPI app in offline mode and asserts on spans with an in-memory exporter. No keys, no network. If this is green, the whole stack works on your machine.

[PAUSE]

A hundred and sixty-eight passed. Write that number in your build log. It's your baseline.

[SLIDE 1: What the tests just proved]
- `src/northwind`: pricing, cost, budgets, tokens, latency, SLOs, sampling, drift, PII, report
- `simulator`: personas and scenarios are deterministic under a seed
- `app` in `OFFLINE=1`: a request produces the expected spans, with the expected attributes
- You have a working OTel pipeline before writing any of it yourself

What did that prove? That the pure-Python library works: pricing, budgets, latency maths, PII masking. That the simulator is deterministic. And that a request through the app produces the expected spans. You now have a working OpenTelemetry pipeline before you've written any of it. In Sections three to five you'll take it apart and rebuild it.

[CODE: start Atlas]
```bash
make run
```

[DEMO: uvicorn starts on `http://127.0.0.1:8000`. A log line shows `OFFLINE=1: using mock LLM` and `telemetry: exporter=langfuse+local`.]

Make run starts Atlas with uvicorn on port eight thousand. Read the two startup lines. Offline, using the mock LLM. Telemetry going to Langfuse and the local store. Those two lines answer most "why don't I see anything" questions later.

[SCREEN: Second terminal.]

[CODE: health check]
```bash
curl -s localhost:8000/healthz
```

[DEMO: `{"status":"ok","offline":true,"model":"gpt-4.1-mini"}`]

And a health check from a second terminal. Status ok, offline true, model gpt-4.1-mini. Atlas is up.

[SLIDE 2: Your two-terminal layout for the course]
- Terminal 1: `make run` (leave it running; watch its logs)
- Terminal 2: `curl`, `make swarm`, `make replay`, tests
- Browser: Langfuse, and the Ops Console on port 8501

Get used to this layout. Terminal one runs Atlas and shows its logs. Terminal two is where you poke it. Browser for Langfuse and the console. You'll use this arrangement in almost every lecture.

[AVATAR]
Installed, tested, running. Fifteen minutes from clone to a healthy agent, with a test suite that tells you when you break something. Now let's send it a real question and see the trace.

**Recap:** `make install` syncs the pinned environment with uv, `make test` proves the offline stack on your machine, and `make run` starts Atlas on port 8000 with its telemetry already wired.

**Transition:** Next, the quick win: one request, one trace, and the screen the whole course is about.

### Speaker notes: common student mistakes / Q&A

- Mistake: running commands from the repo root instead of `03-code/`. The Makefile lives in `03-code`; `make: *** No rule to make target` means you're in the wrong folder.
- Mistake: Python older than 3.11. `uv sync` will say so. Install 3.11 or newer; uv can manage it for you.
- If a handful of integration tests fail with port-in-use errors, another `make run` is already running. Stop it and rerun.
- Windows: use WSL2 or Git Bash for `make`; the README lists the equivalent raw commands for PowerShell.

---

## Lecture 2.3 — Quick win: one request, one trace

| Field | Value |
|---|---|
| ID | 2.3 |
| Type | SC (code-along with browser) |
| Target duration | 8:00 (~575 spoken words, about 4:06 of talking at 140 wpm, plus request and page loads) |
| Learning objectives | 1. Send one question to Atlas with tenant, user and session headers. 2. Find the trace in Langfuse and read its four observations: agent, retriever, generation, tool. 3. Point to usage, cost, latency and inputs/outputs on the generation and explain what each will be used for later. |
| Prerequisites | 2.2 |
| Files used | `03-code/app/server.py`, `03-code/telemetry/langfuse_setup.py` |

**Recording note:** this is the one live request in Section 2. Set `OFFLINE=0` in `.env`, restart `make run`, send the request, then set `OFFLINE=1` again on camera. If you must stay offline, the same trace appears in Langfuse from the mock with the mock's usage numbers; say so on screen.

### Script

[AVATAR]
Ten minutes ago you had a clone. Now you're going to send one question to Atlas and look at a screen that shows every step it took, every token it used and what it cost. Everything else in this course is about explaining and improving this one screen.

[SCREEN: VS Code, `.env`. Change `OFFLINE=1` to `OFFLINE=0`. Terminal 1: restart `make run`. Startup log now says `using OpenAI gpt-4.1-mini`.]

For this one request, go live. Set `OFFLINE=0`, restart Atlas, and confirm the startup line now says OpenAI. This request will cost about half a cent.

[SCREEN: Terminal 2.]

[CODE: one question]
```bash
curl -s localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant: ops' \
  -H 'X-User: emp-1042' \
  -H 'X-Session: sess-demo-1' \
  -d '{"message": "How do I connect to the VPN from home?"}'
```

One question, from a warehouse employee, about the VPN. Three headers: tenant `ops`, user `emp-1042`, session `sess-demo-1`. Remember those three; you'll find them again in the trace.

[DEMO: JSON response with `answer` (three sentences about the VPN client and MFA), `trace_id`, `steps: 2`, `cost_usd: 0.0041`, `latency_ms: 2830`.]

Back comes the answer, and something else: a trace ID, the step count, the cost in dollars and the latency in milliseconds. Atlas reports on itself in every response. Copy that trace ID.

[SCREEN: Browser, Langfuse project `atlas-dev` → Tracing → Traces. The newest trace is at the top, named `atlas`. Click it.]

Now Langfuse. Tracing, traces. There it is, named `atlas`, a few seconds old. Open it.

[SCREEN: Trace detail. Left: the observation tree. Right: details panel. Top: latency, total cost, total tokens, session, user, tags.]

[SLIDE 1: Read a trace top to bottom]
1. Header: latency, cost, tokens, session, user, tags
2. Root: `atlas` (type: agent)
3. Child: `search_knowledge_base` (type: retriever)
4. Child: `chat gpt-4.1-mini` (type: generation): usage, cost, model, input and output messages
5. Child: `execute_tool ...` (type: tool): arguments and result

Read it top to bottom. The header first. Latency, two point eight seconds. Cost, four tenths of a cent. Tokens, about three thousand in, a hundred and forty out. Session `sess-demo-1`, user `emp-1042`, and a tag, `tenant:ops`. The three headers made it all the way here.

[SCREEN: Click the root observation `atlas`.]

The root observation is `atlas`, and its type is agent. Its input is the question, its output is the answer. Everything below it happened in service of this one request.

[SCREEN: Click `search_knowledge_base`.]

First child, `search_knowledge_base`. Type retriever. Input: the query. Output: the top three knowledge base chunks with their scores; vpn dot md is first. Forty milliseconds. In Section five you'll turn this into a quality metric: how often does retrieval come back empty?

[SCREEN: Click the generation `chat gpt-4.1-mini`. Scroll the details: model, usage details (input, output, cache read), cost details, model parameters, input messages, output message.]

Now the generation. This is the model call. Model, gpt-4.1-mini. Usage details: input tokens, output tokens, and cached input tokens, currently zero. Cost details, computed from the price table at the time of the call, not from an invoice a month later. Two point six seconds of the two point eight total; the model is where time goes. And below, the exact messages that were sent and the exact reply.

[PAUSE]

Look at the input messages for a second. System prompt, the retrieved chunks, the user question. That is what you're paying for, every step. Section six is largely about making this smaller.

[SCREEN: Click the tool observation if present, or point to where it would sit. Show arguments and result.]

And a tool observation, when Atlas calls one. Type tool, with the arguments the model chose and the result the tool returned. For a VPN question there's often no tool call; ask about a ticket and you'll see `lookup_ticket` here with its arguments.

[SLIDE 2: Where each piece of this screen comes from]
| On screen | Set by | Rebuilt in |
|---|---|---|
| Tree of observations | OpenTelemetry spans with Langfuse types | Section 3, 4 |
| Session, user, tags | `propagate_attributes(...)` from the request headers | 4.3 |
| Usage and cost on the generation | `update_current_generation(usage_details=, cost_details=)` | 4.2, 6.2 |
| Retriever output and scores | retriever observation | 5.3 |
| Latency per observation | span start and end times | 5.4, 7.2 |

Here's the map of where this screen comes from. The tree is OpenTelemetry spans with Langfuse observation types; you rebuild that in Sections three and four. Session, user and tags come from the headers, via a Langfuse call you'll write in 4.3. Usage and cost are set on the generation in 4.2 and priced properly in 6.2. Every lecture in the next four sections points at a part of this screen.

[SCREEN: VS Code, `.env`. Set `OFFLINE=1` again. Restart `make run`.]

Now flip back to offline and restart. Total live spend so far, about half a cent.

[AVATAR]
One request, one trace. Four observations, three headers, one cost number computed at call time. You'll see thousands of these. Learn to read this one slowly.

**Recap:** One `curl` with tenant, user and session headers produces a Langfuse trace with an agent root, a retriever, a generation carrying usage and cost, and a tool observation; every later lecture explains or improves one part of that screen.

**Transition:** Next, a whole day of these traces, for free, in about forty seconds.

### Speaker notes: common student mistakes / Q&A

- Trace doesn't appear: Langfuse batches spans and flushes on an interval. Wait a few seconds and refresh. If still nothing, check the startup log for `exporter=langfuse` and the base URL region.
- Mistake: forgetting to restart `make run` after editing `.env`. Settings load at startup.
- "Why is cost on the generation, not on the trace?" Cost belongs to the model call. The trace total is the sum of its generations. Section 6.3 rolls it up by session, user and tenant.
- If the live model happens to call `lookup_ticket` for the VPN question, use it: it's a nice unplanned example of non-determinism from Lecture 1.2.

---

## Lecture 2.4 — Offline mode: a full day of traffic for free

| Field | Value |
|---|---|
| ID | 2.4 |
| Type | SC (code-along with the Ops Console) |
| Target duration | 8:00 (~625 spoken words, about 4:28 of talking at 140 wpm, plus replay and console dwell) |
| Learning objectives | 1. Replay a deterministic day of traffic into the local store with `OFFLINE=1 make replay`. 2. Open the Ops Console and read its four pages: cost, latency, quality, budgets. 3. Explain what the mock LLM does and doesn't fake, and why the numbers are still shaped like production. |
| Prerequisites | 2.3 |
| Files used | `03-code/simulator/replay.py`, `03-code/app/mock_llm.py`, `03-code/console/ops_console.py`, `03-code/telemetry/local_store.py` |

### Script

[AVATAR]
One trace is a story. A thousand traces is data. And you need data to learn observability, because the interesting questions, "which tenant is expensive," "what's our p95," "is Tuesday worse than Monday," only exist across many requests. Generating a thousand real requests would cost money and take an hour. Offline mode does it in forty seconds for nothing.

[SLIDE 1: What `OFFLINE=1` swaps]
| Component | Live | Offline |
|---|---|---|
| Model calls | OpenAI API | `app/mock_llm.py`: deterministic, scenario-aware |
| Token counts | from the API response | realistic estimates from the mock |
| Latency | real | sampled from realistic distributions |
| Span storage | Langfuse | `telemetry/local_store.py` (SQLite + JSONL), and Langfuse if asked |
| Prices | `litellm.model_cost` | the same table |

Here's exactly what offline swaps. Model calls go to the mock instead of OpenAI. Token counts are realistic estimates instead of API numbers. Latency is sampled from realistic distributions. Spans go to a local SQLite store instead of, or as well as, Langfuse. And prices come from the same table either way. So the dollars you see offline are real prices times realistic tokens.

[SCREEN: VS Code, `app/mock_llm.py`. Scroll to where it picks a tool call based on the persona's intent, and where it computes usage from message length.]

A quick look at the mock. Given the messages and the persona's intent, it decides whether to answer or call a tool, the way the real model usually does. It estimates input tokens from the message text, generates plausible output lengths, and adds latency drawn from a distribution with a realistic tail. It's also scenario-aware: tell it a tool is down, and it retries like the real model did on Friday night.

[SCREEN: Terminal 2.]

[CODE: replay a day]
```bash
OFFLINE=1 make replay
```

[DEMO: Progress output: `seed=20260928 personas=412 conversations=1184 ... writing spans to .local/atlas.sqlite ... done in 38.2s`. Summary table: conversations 1,184; generations 3,902; tool calls 2,117; total cost $6.42; p95 latency 4.1 s.]

Make replay. It walks a full simulated working day, seven in the morning to seven at night, with a fixed seed. Four hundred and twelve personas, eleven hundred and eighty-four conversations, thirty-nine hundred model calls. It writes every span to the local store. Thirty-eight seconds.

Read the summary. Six dollars forty-two for the day. p95 latency four point one seconds. Those two numbers are going to be under attack for most of this course.

[SLIDE 2: Same seed, same day]
- `seed=20260928` by default; change it with `SEED=`
- Same seed → identical spans, costs and latencies, on any machine
- This is how labs can say "your answer should be $6.42"
- Incidents are injected on top: `SCENARIO=loop`, `context_bloat`, `retry_storm`, `slow_provider`, `prompt_regression`

The seed matters. Same seed, identical day, on your machine and mine. That's how a lab can tell you your answer should be six dollars forty-two, and how Section eleven can hand everyone the same incident. Change the seed to get a different day; add a scenario to inject an incident.

[SCREEN: Terminal 3.]

[CODE: open the Ops Console]
```bash
make console
```

[DEMO: Streamlit opens `http://localhost:8501`. Landing page: four tiles: Cost today $6.42, Conversations 1,184, p95 4.1 s, Judge score "not yet scored". Sidebar: Cost, Latency, Quality, Budgets, Alerts, Traces.]

Make console starts the Ops Console. This is the same app from Lecture 1.1, reading the local store.

[SCREEN: Cost page. Bar chart of cost by tenant: ops $2.63, eng $1.71, hr $1.19, finance $0.89. Below: cost by feature: knowledge_base, tickets, password_reset, shipments. A table of the ten most expensive conversations.]

The cost page. By tenant, ops is two sixty-three of six forty-two. Forty-one percent of the spend from one department. Is that because ops asks more, or because ops questions are more expensive? Hold that question; you'll answer it in Section six. Below, cost by feature, and the ten most expensive conversations of the day, each linking to its trace.

[SCREEN: Latency page. Histogram with p50, p95, p99 lines; a per-hour line chart showing a lunchtime bump.]

Latency. p50 one point nine seconds, p95 four point one, p99 seven point three. And by hour, a bump around one in the afternoon. That's the shape Section seven investigates.

[SCREEN: Quality page: mostly empty, "no scores yet". Budgets page: four tenants, each with a daily budget bar, all green.]

Quality is empty, because nothing has judged these conversations yet. Section eight fills it. Budgets shows each tenant against its daily allowance; all green today.

[SCREEN: Traces page. Pick one conversation; a simple waterfall of its spans opens.]

And traces. A simple waterfall, so you can go from "ops is expensive" to one specific conversation without leaving the console.

[SLIDE 3: When to also send to Langfuse]
```bash
OFFLINE=1 make replay LANGFUSE=1        # also export the day to your Langfuse project
```
- Thousands of observations against your monthly allowance
- Do it once, when a lab asks, not every time
- Everything the console shows is also available as Langfuse filters and dashboards (Section 9.4)

One more switch. Add `LANGFUSE=1` and the replay also exports to your Langfuse project, so you can slice the day with Langfuse's own filters. It's thousands of observations against your monthly allowance, so do it when a lab asks, not every time.

[AVATAR]
A day of traffic, six dollars forty-two, forty-one percent from ops, p95 of four point one seconds, all in forty seconds and for free. This is your dataset for the next twelve sections. Whenever a lecture says "look at the day," this is the day.

**Recap:** `OFFLINE=1 make replay` writes a deterministic day of 1,184 conversations to the local store from the mock LLM, and `make console` shows its cost, latency, quality and budgets, with the same prices and shapes as production.

**Transition:** Now it's your turn: Lab 1 walks you through the environment checklist and your first trace screenshot.

### Speaker notes: common student mistakes / Q&A

- Mistake: running `make replay` without `OFFLINE=1`. Replay never calls a model, but the flag also selects the local store; without it, spans go only to Langfuse and the console is empty.
- Mistake: console open before replay finished. Streamlit caches the store; press R to rerun, or restart the console.
- "Why are the numbers so specific?" Because the seed is fixed. If your totals differ from $6.42, check the seed and that you're on the same commit of the mock.
- "Can I make the mock use my own knowledge base?" Yes, but the day's numbers will change. Do it after the course, or on a branch.

---

## Lecture 2.5 — Lab 1: Environment and first trace

| Field | Value |
|---|---|
| ID | 2.5 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 total (1:30 video, ~225 spoken words, about 1:36 of talking at 140 wpm) |
| Learning objectives | 1. Complete the environment checklist: tests green, Atlas healthy, offline day replayed. 2. Produce and read one live trace in Langfuse. 3. Start the build log with three baseline numbers. |
| Prerequisites | 2.1 to 2.4 |
| Files used | `04-labs/lab-01-first-trace.md` |

### Script

[AVATAR]
Your first lab. It's a checklist, not a puzzle. About twenty minutes if you followed along, less if everything already works.

[SCREEN: VS Code, `04-labs/lab-01-first-trace.md`. Scroll the checklist.]

Part one is the environment. Make test green, with the number of tests passing. Make run healthy, with the health check output. Make replay done, with the day's total cost.

[SCREEN: Scroll to Part 2.]

Part two is your first trace. One live request with your own question, your own tenant and user headers. Then a screenshot of the trace in Langfuse with the generation selected, so usage and cost are visible. Circle the session, the user and the tag.

[SCREEN: Scroll to the "Read the trace" questions.]

Then four questions to answer from the trace. How many observations. Which one took the most time. How many input tokens the generation used. What the total cost was. Write the answers under the screenshot.

[SCREEN: Scroll to the build-log section.]

Finally, start your build log with three baseline numbers: tests passing, the day's cost, and the day's p95. You'll compare every later section against these.

[AVATAR]
One rule: if something fails, run it offline first. If it fails offline, it's the environment, not your key. Post the command, the error and your version banner in Q&A.

**Recap:** Lab 1 checks your environment, captures one live trace with headers visible, and starts your build log with three baseline numbers.

**Transition:** A five-question quiz on setup and tracing basics, then Section 3: what a trace actually is, and how to build one by hand.

### Speaker notes: common student mistakes / Q&A

- Students forget to switch `OFFLINE` back to 1 after the live request and wonder why later labs cost money. The lab checklist has an explicit "flip back" step.
- Screenshot without the generation selected shows no usage. Ask for the generation view.
- If Langfuse Cloud is blocked on a corporate network, the offline trace in the console's Traces page is an acceptable substitute for the screenshot.

---

## Lecture 2.6 — Quiz: Setup and tracing basics

| Field | Value |
|---|---|
| ID | 2.6 |
| Type | QZ (quiz with short video intro) |
| Target duration | 2:00 total (1:00 video, ~100 spoken words, about 0:43 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of the env vars, the Make targets and what offline mode swaps. 2. Recall the four observation types seen in the first trace. |
| Prerequisites | 2.1 to 2.5 |
| Files used | `06-assessments/quizzes/section-02.md` |

### Script

[AVATAR]
Five questions. Two minutes.

[SLIDE 1: Section 2 quiz: what's covered]
- Which env vars Langfuse reads, and why a hard cap
- What `make test`, `make run`, `make replay`, `make console` each do
- What `OFFLINE=1` swaps and what it keeps real
- The four observations in your first trace and where cost lives
- Why the seed matters

One question on keys and caps. One on the Make targets. One on what offline mode swaps and what stays real. One on the first trace: agent, retriever, generation, tool, and which one carries cost. And one on why the replay is seeded.

If you're unsure about a "where does cost live" question, remember: cost belongs to the model call. Everything above it is a sum.

**Recap:** The quiz checks env vars, Make targets, offline mode, and how to read your first trace.

**Transition:** Next, Section 3: traces, spans and context in five minutes, then you build Atlas's OpenTelemetry instrumentation from scratch.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Which component is real in offline mode?" Answer: the price table. Token counts and latencies are realistic estimates.
- Second most missed: the base URL variable. It's `LANGFUSE_BASE_URL`.
