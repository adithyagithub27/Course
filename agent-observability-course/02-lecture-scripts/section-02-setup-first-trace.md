# Section 2: Setup and Your First Trace in 10 Minutes

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈38 min (6 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`; every figure comes from `01-curriculum/numbers-card.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15+ (uv.lock 4.16.0) / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating) / openinference-instrumentation-openai 0.1.61+ (uv.lock 0.1.63); check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only. Code-along lectures are paced below 140 words per minute to leave room for typing, command output and page loads.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 2.1 | Accounts, keys and spending caps | SC | 7:00 | ~635 |
| 2.2 | Project setup with uv and the Makefile | SC | 6:00 | ~555 |
| 2.3 | Quick win: one request, one trace | SC | 8:00 | ~620 |
| 2.4 | Offline mode: a full day of traffic for free | SC | 8:00 | ~760 |
| 2.5 | Lab 1: Environment and first trace | LAB | 4:00 (1:30 video) | ~195 |
| 2.6 | Quiz: Setup and tracing basics | QZ | 2:00 (1:00 video) | ~105 |

**Section guardrails (do not deviate on screen):** the Langfuse env vars are `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` (not the legacy `LANGFUSE_HOST`). The repo already ships fully instrumented in this section; students consume the trace here and take the instrumentation apart in Sections 3 to 5. Atlas reads its settings from environment variables, and nothing in the repo loads `.env` automatically, so every terminal that runs Atlas first does `set -a; source .env; set +a` (shown in 2.1). Never type an API key on camera; paste from a password manager with the terminal input hidden, or use a key you revoke before publishing.

---

## Lecture 2.1 — Accounts, keys and spending caps

| Field | Value |
|---|---|
| ID | 2.1 |
| Type | SC (screencast: browser and `.env`) |
| Target duration | 7:00 (~635 spoken words, about 4:32 of talking at 140 wpm, plus browser navigation) |
| Learning objectives | 1. Create a Langfuse Cloud project and copy its public key, secret key and base URL. 2. Create an OpenAI project with a hard monthly cap and a low soft alert. 3. Fill `.env` from `.env.example`, load it into the shell, and never commit it. |
| Prerequisites | Section 1 |
| Files used | `03-code/.env.example`, `10-resources/cost-guide.md` |

### Script

[AVATAR]
Before you write a line of code, you're going to make it impossible to have your own five-thousand-dollar weekend. Two accounts, three keys, one hard cap. Seven minutes. Ready?

[SLIDE 1: What you need]
- Langfuse Cloud project: free tier, EU or US region (or self-host in Section 13)
- OpenAI project: pay-as-you-go, with a hard cap
- `.env` filled from `.env.example`, never committed
- Expected spend for the whole course: $5-15

[SCREEN: Browser, `https://cloud.langfuse.com`. Sign up, choose a region, create an organisation and a project called `atlas-dev`. Verify the current sign-up flow before recording.]

Start with Langfuse. Sign up at cloud dot langfuse dot com. Pick a region; EU and US are both fine, and the base URL differs, so note which one you picked. Create an organisation, then a project. Call it `atlas-dev`. In Section ten we'll talk about why you want one project per environment; for now one is enough.

[SCREEN: Project settings → API Keys → Create new API key. Show the public key, blur the secret key, and the base URL field. Verify the menu path before recording.]

In project settings, create an API key. You get three values: a public key starting with `pk-lf`, a secret key starting with `sk-lf`, and the base URL for your region. Copy all three now. The secret is shown once.

[SLIDE 2: Langfuse free tier]
- A monthly allowance of observations, plenty for this course (verify current limits)
- Every span you send is one observation; a replayed day is about seventy thousand
- Default in this course: replay to the local store; send to Langfuse only when you want a trace to click
- Self-hosting (Section 13) has no allowance to watch

The free tier counts observations per month. Every span is one observation, and a replayed day of traffic is about seventy thousand of them. So the course replays to a local store by default, and sends to Langfuse only when you ask. Follow the labs as written and you won't hit the limit.

[SCREEN: Browser, `https://platform.openai.com`. Create a project called `atlas-course`. Go to the project's billing limits (verify the current menu path). Set a hard monthly budget of $20 and an alert at $5.]

Now OpenAI. Create a project just for this course, `atlas-course`. Then, before you create a key, go to the billing limits. Set a hard monthly budget of twenty dollars and an email alert at five. If the interface has moved since I recorded this, the resource guide has the current path. [PAUSE] This one setting is your last line of defence. Everything we build in Section six is a better line of defence, but this one works even when your code is wrong.

[SCREEN: API keys → Create new secret key, scoped to the `atlas-course` project. Copy it.]

Create a key scoped to that project. Copy it.

[SLIDE 3: Why a cap and not just care]
- Section 1: $4.90 per conversation with one integer set to zero
- A cap turns a bad night into a bounded bill
- Later: budgets per tenant (6.7) and a CI budget gate (13.3), so the cap never fires

Why insist on the cap? Because in Section one, one integer set to zero cost four dollars ninety per conversation. A hard cap turns a bad night into a bounded bill. By Section thirteen you'll have per-tenant budgets and a CI gate, so the cap never actually fires. Belt, then braces.

[SCREEN: VS Code, `03-code/.env.example`. Copy to `.env`. Fill in the keys, keep `OFFLINE=1`.]

[CODE: create your `.env` (`make install` in the next lecture also does this if the file is missing)]
```bash
cp .env.example .env
```

[CODE: the lines you edit in `.env` (excerpt; values redacted)]
```bash
OFFLINE=1
OPENAI_API_KEY=sk-proj-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or http://localhost:3000 for self-hosted
OTEL_EXPORTER=none                 # console prints every span; Section 3 switches it back on
```

Copy the example to dot env and fill it in. The OpenAI key. The two Langfuse keys and the base URL for your region. Leave `OFFLINE=1`: the mock model answers, and the traces still go to Langfuse because the keys are set. And set the OpenTelemetry exporter to `none` for now, so your terminal isn't flooded with raw spans; Section three turns it back on.

The model variables are already in the file: `gpt-4.1-mini` for Atlas, `gpt-4.1` for escalation. Every model choice in this course is an env var, so a rename by the provider is a one-line fix.

[CODE: load `.env` into this terminal (repeat in every new terminal that runs Atlas)]
```bash
set -a; source .env; set +a
```

One step people miss. Atlas reads its settings from environment variables, and nothing loads dot env for you. So in every terminal where you run Atlas, source it with `set -a` first, which exports every line. Forget it, and Atlas runs with defaults and never sees your keys.

[SCREEN: Show `.gitignore` with `.env` listed. Run `git status` to confirm `.env` does not appear.]

Dot env is in the gitignore. Check with git status. If you ever see dot env in that list, stop and fix it before you commit. A leaked key with a twenty-dollar cap is annoying; a leaked key with no cap is a very bad week.

[SLIDE 4: Cost guide]
- `10-resources/cost-guide.md`: what each section costs live, and the offline path for each
- Rule of thumb: offline to learn, live for the screenshot
- Live-only moments: 2.3 (one optional request), 6.4 (a cache hit), 8.2 (a judge call), 14 (a short live run)

The cost guide in the resources folder lists what each section costs if you run it live, and the offline path for each. Only four moments in the course genuinely benefit from going live. Everything else, run offline.

[AVATAR]
Two accounts, three keys, one cap, one dot env, loaded into your shell. You're now safe to make mistakes, which is the whole point.

[SLIDE 5: Recap]
- Langfuse project: two keys and a base URL
- OpenAI project with a hard cap
- `.env` filled, sourced, never committed

**Recap:** Create a Langfuse Cloud project and copy its two keys and base URL, create an OpenAI project with a hard cap and a soft alert, fill `.env` from the example, load it with `set -a; source .env; set +a`, and never commit it.

**Transition:** Next, one command to install everything and prove the whole repo works, offline, before you spend a cent.

### Speaker notes: common student mistakes / Q&A

- Mistake: using the wrong region's base URL. Symptom: 401 on the first flush. Check the URL against the region shown in the Langfuse UI.
- Mistake: editing `.env` and expecting a running Atlas to notice. Settings load at startup from the environment; re-source `.env` and restart.
- Mistake: `LANGFUSE_HOST` from older tutorials. The settings still read it as a fallback, but `LANGFUSE_BASE_URL` is the documented v4 variable and the one in `.env.example`.
- "Can I use an existing OpenAI key?" Yes, but a project-scoped key with its own cap is safer and makes the course's spend visible on its own line.
- "I only want to self-host Langfuse." Fine: skip the cloud signup, set `LANGFUSE_BASE_URL=http://localhost:3000` after Lecture 13.1, and use offline mode with the local console until then.
- The `.env` excerpt shows only the lines students edit; the real file has every setting with a comment. The `set -a; source .env; set +a` step is needed because the repo declares `python-dotenv` but never calls it (reported to the code owner); if a later repo version loads `.env` itself, the step becomes harmless.

---

## Lecture 2.2 — Project setup with uv and the Makefile

| Field | Value |
|---|---|
| ID | 2.2 |
| Type | SC (code-along) |
| Target duration | 6:00 (~555 spoken words, about 3:58 of talking at 140 wpm, plus install and test output) |
| Learning objectives | 1. Install the project with `make install` (uv, dev extra) and add the `dashboards` extra for the console. 2. Run the offline test suite green with `make test`. 3. Start Atlas with `make run` and read `/healthz`. |
| Prerequisites | 2.1 |
| Files used | `03-code/pyproject.toml`, `03-code/Makefile`, `03-code/uv.lock`, `03-code/README.md` |

### Script

[AVATAR]
Here's a rule I wish someone had given me years ago. Never start a course, or a job, by running the interesting command. Start by running the tests. If four hundred and one tests pass on your machine, every problem you hit later is yours, and that's good news. It means you can fix it.

[SCREEN: Terminal. Clone or open the repo, `cd 03-code`.]

[CODE: get the code]
```bash
git clone <your fork of agent-observability-course>
cd agent-observability-course/03-code
```

Clone your fork and change into the code folder. All commands in this course run from `03-code`.

[SCREEN: VS Code, `pyproject.toml`. Scroll the dependencies and the extras.]

Open pyproject. The dependencies are pinned to compatible versions: langfuse four, the OpenTelemetry SDK and its OTLP exporter, the semantic conventions package, OpenInference for OpenAI, LiteLLM, OpenAI, FastAPI and the Prometheus client. Below that, four extras: `dev` for tests, linting and DeepEval, `langsmith` and `phoenix` for Section twelve, and `dashboards` for the Streamlit console. Next to it, `uv.lock` pins the exact versions I recorded with.

[SCREEN: Terminal: `make help`.]

[DEMO: `make help` lists the targets with one line each: `install`, `run`, `swarm`, `replay`, `loop-demo`, `langfuse-native`, `prompts`, `console`, `console-text`, `test`, `test-unit`, `test-integration`, `eval`, `judge`, `feedback`, `drift`, `dataset`, `budget-check`, `lint`, `format`, `incidents`, `incident`, `report`, `stack`, `langfuse-up`, `clean`, `lock`, `student-repo`.]

The Makefile is the front door. Make help lists every target with one line about what it does. Install, run, swarm, replay, console, test, and the ones later sections use. Every lecture that says "run this" uses one of these, so you never have to remember a long command.

[CODE: install]
```bash
make install
source .venv/bin/activate
```

[DEMO: `make install` runs `uv venv --python 3.11 && uv pip install -e ".[dev]"`, copies `.env.example` to `.env` only if `.env` doesn't exist yet, and ends with `Now: source .venv/bin/activate && make test`.]

Make install creates a virtual environment with uv and installs the project with its dev extra. If uv isn't installed, it falls back to plain pip. It also copies the example env file, but only if you don't have one, so your keys from the last lecture are safe. Then activate the environment.

[CODE: add the console's extra (Lecture 2.4 needs it)]
```bash
uv pip install -e ".[dev,dashboards]"
```

One addition for later: the Ops Console needs Streamlit, which lives in the `dashboards` extra. Install it now and you're done with setup.

[CODE: run the tests, offline]
```bash
make test
```

[DEMO: pytest runs unit, integration and budget-gate tests offline. Output ends with `401 passed, 1 warning in 45.24s` (the time varies by machine).]

Now the tests. Make test runs the unit suite over the pure-Python package, `src/northwind`, the integration suite, which starts the FastAPI app in offline mode and asserts on spans with an in-memory exporter, and the budget gate you'll meet in Section thirteen. No keys, no network.

[PAUSE]

Four hundred and one passed. Write that number in your build log. It's your baseline.

[SLIDE 1: What the tests just proved]
- `src/northwind`: pricing, cost, budgets, tokens, latency, SLOs, sampling, drift, PII, report
- `simulator`: personas and scenarios are deterministic under a seed
- `app` in `OFFLINE=1`: a request produces the expected spans, with the expected attributes
- You have a working OpenTelemetry pipeline before writing any of it yourself

What did that prove? That the pure-Python library works: pricing, budgets, latency maths, PII masking. That the simulator is deterministic. And that a request through the app produces exactly the spans the course expects. You have a working OpenTelemetry pipeline before you've written any of it. In Sections three to five you'll take it apart and rebuild it.

[CODE: start Atlas (load `.env` first, as in 2.1)]
```bash
set -a; source .env; set +a
make run
```

[DEMO: uvicorn starts on port 8000. Terminal 1 shows `INFO:     Uvicorn running on http://0.0.0.0:8000` and one JSON log line: `{"ts": "...", "level": "INFO", "logger": "atlas.server", "service": "atlas", "message": "atlas started", "offline": true, "exporter": "none"}`.]

Make run starts Atlas with uvicorn on port eight thousand. What is that JSON log line telling you? Offline, true: the mock model answers. Exporter, none: no raw spans in this terminal. Those two fields answer most "why don't I see anything" questions later.

[SCREEN: Second terminal.]

[CODE: health check]
```bash
curl -s localhost:8000/healthz
```

[DEMO: `{"status":"ok","offline":true,"model":"gpt-4.1-mini","prompt_version":"v1","exporters":[{"name":"local_store","exported":0,"failures":0}],"uptime_s":5.5}`]

And a health check from a second terminal. Status ok, offline true, model gpt-4.1-mini, prompt version one. And an exporters list: right now the local span store, with zero spans exported and zero failures. Section thirteen comes back to that failure counter.

[SLIDE 2: Your two-terminal layout for the course]
- Terminal 1: `make run` (leave it running; watch its logs)
- Terminal 2: `curl`, `make swarm`, `make replay`, tests
- Browser: Langfuse, and the Ops Console on port 8501

Get used to this layout. Terminal one runs Atlas and shows its logs. Terminal two is where you poke it. Browser for Langfuse and the console. You'll use this arrangement in almost every lecture.

[SLIDE 3: Recap]
- `make install`: venv, dev extra, `.env` copy
- `make test`: 401 passed, offline
- `make run` plus `/healthz`: Atlas is up

**Recap:** `make install` creates the uv environment with the dev extra, the `dashboards` extra adds the console, `make test` proves the offline stack with 401 passing tests, and `make run` starts Atlas on port 8000 with its telemetry already wired.

**Transition:** Next, the quick win: one request, one trace, and the screen the whole course is about.

### Speaker notes: common student mistakes / Q&A

- Mistake: running commands from the repo root instead of `03-code/`. `make: *** No rule to make target` means you're in the wrong folder.
- Mistake: Python older than 3.11. `uv venv --python 3.11` downloads 3.11 if it's missing; the pip fallback needs a 3.11+ `python` on your PATH.
- "I want exactly the versions from the recording." `make install` resolves the newest compatible versions; `uv sync --locked --extra dev --extra dashboards` installs exactly what `uv.lock` pins (verify the flags against your uv version).
- If a handful of integration tests fail with port-in-use errors, another `make run` is already running. Stop it and rerun.
- Windows: use WSL2 or Git Bash for `make` and `source`; the README lists the raw commands.

---

## Lecture 2.3 — Quick win: one request, one trace

| Field | Value |
|---|---|
| ID | 2.3 |
| Type | SC (code-along with browser) |
| Target duration | 8:00 (~620 spoken words, about 4:26 of talking at 140 wpm, plus request and page loads) |
| Learning objectives | 1. Send one question to Atlas with tenant, user and session headers. 2. Find the trace in Langfuse and read its observations: agent, guardrail, steps, generations and a retriever. 3. Point to usage, cost, latency and inputs/outputs on a generation and explain what each will be used for later. |
| Prerequisites | 2.2 |
| Files used | `03-code/app/server.py`, `03-code/app/agent.py`, `03-code/telemetry/langfuse_setup.py`, `03-code/telemetry/genai_attrs.py` |

**Recording note:** record offline with Langfuse keys set, so the numbers on screen match everyone's. Terminal 1: `set -a; source .env; set +a; ATLAS_MOCK_LATENCY_SCALE=1 make run`. `ATLAS_MOCK_LATENCY_SCALE=1` makes the mock sleep its simulated latency, so span durations in Langfuse look like a real model's; without it, offline spans last a few milliseconds. The response JSON below was captured on 2026-10-02 and is deterministic. If a student has no Langfuse account, the console's Traces page (Lecture 2.4) shows the same tree.

### Script

[AVATAR]
Ten minutes ago you had a clone. Now you're going to send one question to Atlas and look at a screen that shows every step it took, every token it used and what it cost. Everything else in this course explains and improves this one screen.

[SCREEN: Terminal 1: `ATLAS_MOCK_LATENCY_SCALE=1 make run` with `.env` sourced. The startup log line shows `"offline": true`.]

I'm staying offline, so your numbers will match mine exactly. The keys from 2.1 are loaded, so Langfuse receives the trace either way.

[SCREEN: Terminal 2.]

[CODE: one question]
```bash
curl -s localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant: ops' \
  -H 'X-User: NW-40213' \
  -H 'X-Session: sess-demo-1' \
  -d '{"message": "How do I connect to the VPN from home?"}'
```

One question, from a warehouse employee, about the VPN. Three headers: tenant `ops`, user `NW-40213`, which is what Northwind employee IDs look like, and session `sess-demo-1`. Remember those three; you'll find them again in the trace.

[DEMO: JSON response. Highlight `"steps": 2`, `"outcome": "resolved"`, `"usage": {"input_tokens": 9950, "output_tokens": 334, "cached_tokens": 0, "reasoning_tokens": 0}`, `"cost_usd": 0.0045144`, `"latency_ms": 3393.8`, `"tool_calls": ["search_knowledge_base"]`, and the `trace_id`.]

Back comes the answer, and more: a trace ID, two steps, the token usage, the cost in dollars and the latency in milliseconds. Nine thousand nine hundred and fifty input tokens for one question. Forty-five hundredths of a cent. Atlas reports on itself in every response. Copy that trace ID.

[SCREEN: Browser, Langfuse project `atlas-dev` → Tracing → Traces. The newest trace is at the top, named `invoke_agent atlas`. Click it.]

Now Langfuse. Tracing, traces. There it is, named `invoke_agent atlas`, a few seconds old. Open it.

[SCREEN: Trace detail. Left: the observation tree. Right: details panel. Top: latency, total cost, total tokens, session, user, tags.]

[SLIDE 1: Read a trace top to bottom]
1. Header: latency, cost, tokens, session, user, tags
2. Root: `invoke_agent atlas` (type: agent)
3. `guardrail injection_check` (type: guardrail)
4. `step 1` → `chat gpt-4.1-mini` (generation) and `execute_tool search_knowledge_base` (retriever)
5. `step 2` → `chat gpt-4.1-mini` (generation): the answer

Read it top to bottom. The header first. Total cost, the same forty-five hundredths of a cent. Tokens: nine thousand nine hundred and fifty in, three hundred and thirty-four out. Session `sess-demo-1`, user `NW-40213`, and four tags: `tenant:ops`, `feature:policy_question`, `intent:vpn` and `prompt:v1`. The three headers made it all the way here.

[SCREEN: Click the root observation `invoke_agent atlas`.]

The root is the agent observation. Its input is the question, its output is the answer. Everything below it happened in service of this one request.

[SCREEN: Click `guardrail injection_check`.]

First child: a guardrail. Before any model call, Atlas checks the message for prompt injection. Its output says flagged false. You'll build your own version of this in the Section four challenge.

[SCREEN: Expand `step 1`; click `execute_tool search_knowledge_base`.]

Then step one. Inside it, a retriever: the knowledge-base search. Input: the query. Output: four article IDs, with `KB-001`, VPN access and troubleshooting, first. A few milliseconds. In Section five you'll turn this into a quality metric: how often does retrieval come back empty?

[SCREEN: Click the step 1 generation `chat gpt-4.1-mini`. Scroll the details: model, usage (input 3,262, output 44), cost details, input and output.]

Now the first generation, the model call that decided to search. Model, gpt-4.1-mini. Usage: 3,262 tokens in, 44 out. Cost details, computed from the price table at the moment of the call, not from an invoice a month later.

[SCREEN: Expand `step 2`; click its generation. Usage: input 6,688, output 290. The bar for this generation covers most of the trace's duration.]

And the second generation, the one that wrote the answer. Six thousand six hundred and eighty-eight tokens in, two hundred and ninety out, and most of the request's time. Why is the input twice as big? [PAUSE] Because by step two the model is re-reading the three-thousand-token system prompt, the question, and the knowledge-base articles the search returned. That's what you pay for, every step. Section six is largely about making it smaller.

[SLIDE 2: Where each piece of this screen comes from]
| On screen | Set by | Rebuilt in |
|---|---|---|
| Tree of observations | OpenTelemetry spans; `langfuse.observation.type` from `telemetry/genai_attrs.py` | 3.2, 3.4 |
| Session, user, tags | `trace_attributes(...)` in `AtlasAgent.run` (wraps Langfuse `propagate_attributes`) | 4.3 |
| Usage and cost on each generation | `ga.set_llm_usage` and `ga.set_cost`; Langfuse-native: `update_current_generation` | 3.4, 4.2, 6.2 |
| Retriever query and documents | `ga.set_retrieval` | 5.3 |
| Latency per observation | span start and end times | 5.4, 7.2 |

Here's the map of where this screen comes from. The tree is OpenTelemetry spans with Langfuse observation types; you rebuild that in Section three. Session, user and tags come from the headers, through one context manager you'll study in 4.3. Usage and cost are attributes on each generation, set in 3.4 and priced properly in 6.2. Every lecture in the next four sections points at a part of this screen.

[SLIDE 3: Going live, once (optional)]
```bash
OFFLINE=0 ATLAS_MOCK_LATENCY_SCALE=0 make run     # same terminal, after sourcing .env
```
- Costs roughly half a cent with `gpt-4.1-mini` (verify current pricing)
- Token counts and the answer text will differ from the mock's
- Switch back to `OFFLINE=1` before anything else

Want a real model's trace? Start Atlas with `OFFLINE=0` for one request. It costs roughly half a cent. The numbers will differ from mine, and that's expected. Then go straight back to offline.

[AVATAR]
One request, one trace. Three headers, two steps, two model calls, one cost number computed at call time. You'll see thousands of these. Learn to read this one slowly.

[SLIDE 4: Recap]
- One `curl`, three headers, one trace
- Agent, guardrail, steps, generations, retriever
- Cost is computed per model call

**Recap:** One `curl` with tenant, user and session headers produces a Langfuse trace with an agent root, a guardrail, one step per loop iteration, generations carrying usage and cost, and a retriever; every later lecture explains or improves one part of that screen.

**Transition:** Next, a whole day of these traces, for free, in about twenty seconds.

### Speaker notes: common student mistakes / Q&A

- Trace doesn't appear: Langfuse batches spans and flushes every couple of seconds. Wait and refresh. If still nothing, check that this terminal sourced `.env` (no keys means no Langfuse client) and the base URL region.
- Mistake: forgetting to restart `make run` after editing `.env`. Settings load at startup.
- "Why is cost on the generation, not on the trace?" Cost belongs to the model call. The trace total is the sum of its generations. Section 6.3 rolls it up by session, user and tenant.
- "Why does the generation's input show only one message?" Atlas records the newest message of each call to keep traces small; the token count is the full prompt the model read.
- If a live model happens to answer the VPN question differently, use it: a nice unplanned example of non-determinism from Lecture 1.2.

---

## Lecture 2.4 — Offline mode: a full day of traffic for free

| Field | Value |
|---|---|
| ID | 2.4 |
| Type | SC (code-along with the Ops Console) |
| Target duration | 8:00 (~760 spoken words, about 5:26 of talking at 140 wpm, plus replay and console dwell) |
| Learning objectives | 1. Replay a deterministic day of traffic into the local store with `OFFLINE=1 make replay`. 2. Open the Ops Console and read its Cost, Latency, Quality, Budgets and Traces pages. 3. Explain what the mock LLM does and doesn't fake, and why the numbers are still shaped like production. |
| Prerequisites | 2.3 |
| Files used | `03-code/simulator/replay.py`, `03-code/app/mock_llm.py`, `03-code/console/ops_console.py`, `03-code/console/pages/`, `03-code/telemetry/local_store.py` |

**Recording note:** all figures below are `numbers-card.md` §1, §3 and §4, regenerated on 2026-10-02 with the Makefile defaults; the replay is deterministic. Run `make console` from a terminal where the `dashboards` extra is installed (2.2).

### Script

[AVATAR]
One trace is a story. Ten thousand traces is data. And you need data to learn observability, because the interesting questions, "which tenant is expensive," "what's our p95," "is this afternoon worse than this morning," only exist across many requests. Generating ten thousand real requests would cost money and take hours. Offline mode does it in about twenty seconds, for nothing.

[SLIDE 1: What `OFFLINE=1` swaps]
| Component | Live | Offline |
|---|---|---|
| Model calls | OpenAI API | `app/mock_llm.py`: deterministic, scenario-aware |
| Token counts | from the API response | realistic counts from the mock |
| Latency | real | simulated from realistic distributions |
| Span storage | local store, plus Langfuse when keys are set | the same |
| Prices | `src/northwind/pricing.py` | the same table |

Here's exactly what offline swaps. Model calls go to the mock instead of OpenAI. Token counts are realistic counts from the mock instead of API numbers. Latency is simulated from realistic distributions. Span storage and prices don't change: spans go to the local SQLite store, and to Langfuse if your keys are set, and prices come from the same table either way. So the dollars you see offline are real prices times realistic tokens.

[SCREEN: VS Code, `app/mock_llm.py`. Scroll to where it picks a tool call for the message's intent, and where it builds usage and latency.]

A quick look at the mock. Given the messages, it classifies the intent and decides whether to answer or call a tool, the way the real model usually does. It counts input tokens from the actual message text, generates plausible output lengths, and adds latency with a realistic tail. It's also scenario-aware: tell it a tool is down, and it keeps retrying like the model did on Friday night.

[SCREEN: Terminal 2.]

[CODE: replay a day]
```bash
OFFLINE=1 make replay
```

[DEMO: Output, after about 20 seconds:
`Replay seed=7  requests=10184  sessions=4000  spans=70560  scores=11884  feedback=1291`
`Total cost $56.2810   p95 latency 3827 ms   elapsed 20.8s`
`Cost by tenant: eng=$12.5033, finance=$11.9125, hr=$11.5908, ops=$20.2745`
`Outcomes: escalated=43, guardrail=72, resolved=10069`
`Scenarios: none=10184`
`Store: .atlas/spans.sqlite  (total spans now 70560)`]

Make replay. It walks a full simulated day, Monday the fourteenth of September, with a fixed seed. Four thousand conversations, ten thousand one hundred and eighty-four requests, seventy thousand spans, written to the local store. About twenty seconds.

Read the summary. Fifty-six dollars twenty-eight for the day. p95 latency three thousand eight hundred and twenty-seven milliseconds. Those two numbers are going to be under attack for most of this course.

[SLIDE 2: Same seed, same day]
- Defaults: `SEED=7`, `SESSIONS=4000`, day 2026-09-14
- Same seed → identical spans, costs and latencies, on any machine
- This is how a lab can say "your answer should be $56.28"
- Incidents are injected on top: `SCENARIO=loop`, `context_bloat`, `retry_storm`, `slow_provider`, `prompt_regression`, or a preset such as `cost_spike`

The seed matters. Same seed, identical day, on your machine and mine. That's how a lab can tell you your answer should be fifty-six dollars twenty-eight, and how Section eleven can hand everyone the same incident. Change the seed to get a different day; add a scenario to inject an incident.

[SCREEN: Terminal 3.]

[CODE: open the Ops Console]
```bash
make console
```

[DEMO: Streamlit opens `http://localhost:8501`. Home page: four tiles: "Cost (store) $56.28", "Requests / sessions 10,184 / 4,000", "p95 latency 3.83 s", "Judge score 0.91". The sidebar lists twelve pages: Live cost, Cost, Latency, Quality, Budgets, Traffic, Retrieval, Reliability, Safety, Alerts, Traces, Compare replays.]

Make console starts the Ops Console: the same app you watched in Lecture 1.1, reading the local store. Four tiles on the home page, and twelve pages in the sidebar. We'll look at five today.

[SCREEN: Cost page. Tiles: "Total cost $56.28", "Cost / session $0.0141", "Cost / resolved session $0.0144", "Cache hit ratio 0%". Bar charts: by tenant (ops $20.27, eng $12.50, finance $11.91, hr $11.59) and by feature (policy_question $42.91 first).]

The cost page. A cent and a half per conversation. By tenant, ops is twenty dollars twenty-seven of fifty-six twenty-eight: thirty-six percent of the spend from one department. Is that because ops asks more, or because ops questions are more expensive? [PAUSE] Hold that question; Section six answers it, and the answer is in this console. By feature, policy questions are three quarters of the bill.

[SCREEN: Scroll to "Ten most expensive conversations". Top row: `s07-00666`, finance, policy_question, 4 turns, 8 steps, $0.0362, "open trace". Click "open trace".]

At the bottom, the ten most expensive conversations of the day. The top one, a four-turn finance conversation, cost three point six cents. Each row links to its trace.

[SCREEN: Traces page opens on that conversation's first trace: a waterfall with `invoke_agent atlas`, `guardrail injection_check`, `step 1` with `chat gpt-4.1-mini` and `execute_tool search_knowledge_base`, then `step 2` with the second `chat gpt-4.1-mini`.]

And here's the waterfall. The same shape you read in Langfuse in 2.3, from the local store, without leaving the console. From "finance is expensive" to one specific conversation in two clicks.

[SCREEN: Latency page. Tiles p50 3,232 ms, p95 3,827 ms. The hourly p50/p95 chart with a flat p95 line between about 3.6 and 3.9 s, under the 4 s budget line.]

Latency. p50 three point two seconds, p95 three point eight, against a budget line at four seconds. Is there a lunchtime bump? No: by hour, p95 is flat all day. Remember that flatness: in Section eleven an incident bends it, and you'll be the one who notices.

[SCREEN: Quality page tiles: "Judge overall 0.912", "Grounded rate 98.6%", "Empty retrievals 2.6%", "Feedback 79% of 12.7%" (79 % of feedback positive; feedback on 12.7 % of requests). Then the Budgets page: ops cumulative spend climbing to $20.27 under the $25 soft and $40 hard cap lines.]

Quality already has numbers, because the replay simulates the judge you'll build in Section eight on a sample of traces: overall point nine one. Budgets shows each tenant's spend against its caps. Ops reaches about half its forty-dollar hard cap. All green today.

[SLIDE 3: When to also send to Langfuse]
```bash
OFFLINE=1 make replay LANGFUSE=1        # also export the day to your Langfuse project
```
- About seventy thousand observations against your monthly allowance
- Do it once, when a lab asks, not every time
- Everything the console shows is also available as Langfuse filters and dashboards (Section 9.4)

One more switch. Add `LANGFUSE=1` and the replay also exports to your Langfuse project, so you can slice the day with Langfuse's own filters. That's about seventy thousand observations against your monthly allowance, so do it when a lab asks, not every time.

[AVATAR]
A day of traffic, fifty-six dollars twenty-eight, thirty-six percent from ops, p95 of three point eight seconds, all in twenty seconds and for free. This is your dataset for the rest of the course. Whenever a lecture says "look at the day," this is the day.

[SLIDE 4: Recap]
- `make replay`: 10,184 requests, $56.28, seed 7
- Console: cost, latency, quality, budgets, traces
- Real prices times realistic tokens, for free

**Recap:** `OFFLINE=1 make replay` writes a deterministic day of 10,184 requests in 4,000 sessions to the local store from the mock LLM, and `make console` shows its cost, latency, quality, budgets and traces, with real prices and production-shaped numbers.

**Transition:** Now it's your turn: Lab 1 walks you through the environment checklist and your first trace screenshot.

### Speaker notes: common student mistakes / Q&A

- `make replay` sets `OFFLINE=1` by default and always writes to the local store (`.atlas/spans.sqlite`, or `STORE=`); it never calls a model. `LANGFUSE=1` only adds the upload. It clears the store first, so your 2.3 request disappears from the console; `KEEP=1` keeps existing spans.
- Mistake: console open before the replay finished. Press "Reload store" in the sidebar or restart the console.
- "Why are the numbers so specific?" Because the seed is fixed. If your totals differ from $56.28, check `SEED`, `SESSIONS`, that you didn't pass `CACHE=1`/`DIET=1`/`ROUTER=1`, and that you're on the same commit.
- "Can I make the mock use my own knowledge base?" Yes, but the day's numbers will change. Do it after the course, or on a branch.
- If Streamlit isn't installed, `make console` falls back to the text console; `make console-text` always prints it.

---

## Lecture 2.5 — Lab 1: Environment and first trace

| Field | Value |
|---|---|
| ID | 2.5 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 total (1:30 video, ~195 spoken words, about 1:24 of talking at 140 wpm) |
| Learning objectives | 1. Complete the environment checklist: tests green, Atlas healthy, offline day replayed. 2. Produce and read one trace in Langfuse. 3. Start the build log with three baseline numbers. |
| Prerequisites | 2.1 to 2.4 |
| Files used | `04-labs/lab-01-first-trace.md` |

### Script

[AVATAR]
Your first lab. It's a checklist, not a puzzle. About twenty minutes if you followed along. How fast can you get all three baseline numbers?

[SCREEN: VS Code, `04-labs/lab-01-first-trace.md`. Scroll the checklist.]

Part one is the environment: make test green, make run healthy, make replay done.

[SCREEN: Scroll to Part 2.]

Part two is your first trace: one request with your own question and headers, and a screenshot in Langfuse with a generation selected. Can you find all three headers on it?

[SCREEN: Scroll to the "Read the trace" questions.]

Then answer the lab's questions from the trace itself, under the screenshot.

[SCREEN: Scroll to the build-log section.]

Finally, start your build log with three baseline numbers: four hundred and one tests, fifty-six twenty-eight, and a p95 of three thousand eight hundred and twenty-seven milliseconds.

[SLIDE 1: You can now]
- Install, test and run Atlas offline
- Read one trace: steps, generations, cost
- Replay a day and read the console

[AVATAR]
You can now run Atlas offline, read a trace, and replay a whole day. One rule for the lab: if something fails, run it offline first. If it fails offline, it's the environment, not your key.

**Recap:** Lab 1 checks your environment, captures one trace with its headers visible, and starts your build log with three baseline numbers: 401 tests, $56.28, 3,827 ms.

**Transition:** A five-question quiz on setup and tracing basics, then Section 3: what a trace actually is, and how to build one by hand.

### Speaker notes: common student mistakes / Q&A

- Students forget to source `.env` in a new terminal and wonder why Langfuse shows nothing. The lab's first step checks it.
- A screenshot without a generation selected shows no usage. Ask for the generation view.
- If Langfuse Cloud is blocked on a corporate network, the console's Traces page is an acceptable substitute for the screenshot.

---

## Lecture 2.6 — Quiz: Setup and tracing basics

| Field | Value |
|---|---|
| ID | 2.6 |
| Type | QZ (quiz with short video intro) |
| Target duration | 2:00 total (1:00 video, ~105 spoken words, about 0:45 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of the env vars, the Make targets and what offline mode swaps. 2. Recall the observation types seen in the first trace. |
| Prerequisites | 2.1 to 2.5 |
| Files used | `06-assessments/quizzes/section-02.md` |

### Script

[AVATAR]
Five questions. Two minutes.

[SLIDE 1: Section 2 quiz: what's covered]
- Which env vars Langfuse reads, and why a hard cap
- What `make test`, `make run`, `make replay`, `make console` each do
- What `OFFLINE=1` swaps and what it keeps real
- The observations in your first trace and where cost lives
- Why the replay is seeded

One question on keys and caps. One on the Make targets. One on what offline mode swaps and what stays real. One on the first trace: agent, guardrail, retriever, generations, and which one carries cost. And one on why the replay is seeded.

If you're unsure about a "where does cost live" question, remember: cost belongs to the model call. Everything above it is a sum.

**Recap:** The quiz checks env vars, Make targets, offline mode, and how to read your first trace.

**Transition:** Next, Section 3: traces, spans and context in five minutes, then you build OpenTelemetry instrumentation by hand.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Which component is real in offline mode?" Answer: the price table. Token counts and latencies come from the mock.
- Second most missed: the base URL variable. It's `LANGFUSE_BASE_URL`.
