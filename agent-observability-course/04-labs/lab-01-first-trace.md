# Lab 1: Environment and Your First Trace

| Field | Details |
|---|---|
| **Section / lecture** | Section 2, lecture 2.5 |
| **Time estimate** | 45 minutes (30 if you stay offline) |
| **Difficulty** | Beginner |
| **Goal** | Get the Atlas repo running, make the offline test suite green, send one request to Atlas and read the resulting trace end to end: agent span, retriever span, generation with token usage and cost, tool span. Then fill a day of traffic for free with the replay. |
| **You will produce** | `notes/lab-01.md` with a screenshot (or console dump) of your first trace and the answers to four reading questions |

---

## Prerequisites

- Python 3.11 or newer and [`uv`](https://docs.astral.sh/uv/) installed (`uv --version`).
- Git, `curl` and a terminal.
- Lectures 2.1 to 2.4 watched.
- Optional for the online path: a Langfuse Cloud account (free tier) and an OpenAI API key with a hard spending cap set (lecture 2.1 shows where). Everything in this lab also works with `OFFLINE=1`, which is the default in `.env.example`.

## How this lab works

Every step has two paths. The **online** path talks to OpenAI and Langfuse Cloud and costs a few cents. The **offline** path (`OFFLINE=1`) uses the deterministic mock LLM and writes spans to a local SQLite store and to your terminal. Both paths produce the same span structure; only the backend differs. If in doubt, stay offline: you can redo the online steps in five minutes once you have keys.

---

## Step 1: Clone and install

```bash
git clone https://github.com/<instructor>/agent-observability-course.git
cd agent-observability-course/03-code
make install
```

`make install` runs `uv venv --python 3.11` and `uv pip install -e ".[dev]"` (it falls back to `python -m venv` and `pip` when `uv` is missing), then copies `.env.example` to `.env` if you don't have one. The `dev` extra pulls in the course stack (`langfuse` 4.x, `opentelemetry-sdk` 1.45, `litellm` 1.103, `openai` 2.x, `fastapi`, `prometheus-client`, `streamlit`, `pytest`, `ruff`). For a byte-for-byte reproducible install, `uv sync --locked --extra dev` uses the committed `uv.lock` instead. The last line printed is:

```text
Now: source .venv/bin/activate && make test
```

Activate the venv (`source .venv/bin/activate`); every later command assumes it.

> **Checkpoint 1:** `python -c "import langfuse, opentelemetry, litellm; print('ok')"` prints `ok`.

---

## Step 2: Run the offline test suite

Nothing here needs a key. The unit tests cover `src/northwind/` (pricing, cost, budget, tokens, latency, SLO, sampling, drift, PII, report) and the integration tests start the FastAPI app in offline mode with an in-memory span exporter.

```bash
make test
```

Expected last line (about 40 seconds; the count grows if the course adds tests):

```text
401 passed, 1 warning in 41.30s
```

That is 356 unit tests, 40 integration tests and the 5 budget-gate tests, all offline.

> **Checkpoint 2:** `make test` ends in `passed` with zero failures.

---

## Step 3: Create your `.env`

```bash
cp .env.example .env
```

**Offline path (default):** leave `OFFLINE=1`, leave the Langfuse keys empty, and set `OTEL_EXPORTER=console` so spans print to your terminal. You are done with this step.

**Online path:** edit `.env`:

```dotenv
OFFLINE=0
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com   # EU region; use https://us.cloud.langfuse.com for US
LANGFUSE_TRACING_ENVIRONMENT=dev
OTEL_EXPORTER=console      # Langfuse receives spans through its own client whenever the keys are set
```

Create the Langfuse keys under **Project settings → API keys** in a new project called `atlas-dev`. Before you save the OpenAI key, open **platform.openai.com → Settings → Limits** and set a monthly budget of $10 with an email alert at $5. The whole course fits inside that.

Verify the configuration without sending anything:

```bash
PYTHONPATH=.:src python -c "from northwind.config import Settings; s=Settings.from_env(); print(f'offline={s.offline} exporter={s.otel_exporter} langfuse_enabled={s.langfuse_enabled} openai_enabled={s.openai_enabled} store={s.local_store_path}')"
```

Expected output (offline):

```text
offline=True exporter=console langfuse_enabled=False openai_enabled=False store=.atlas/spans.sqlite
```

Online, `langfuse_enabled=True` and `openai_enabled=True`. If either is `False` when you expected `True`, the key is missing or has a trailing space.

> **Checkpoint 3:** the settings dump shows the mode you intended.

---

## Step 4: Start Atlas and send one request

Terminal 1:

```bash
make run
```

Expected:

```text
python -m uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [27803]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Terminal 2:

```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant: hr' \
  -H 'X-User: NW-10433' \
  -H 'X-Session: lab1-session-1' \
  -d '{"message": "How many days of annual leave do I get?"}' | python3 -m json.tool
```

Expected response (offline wording and numbers are deterministic; `trace_id` differs every run; abridged):

```json
{
    "answer": "Here's what the policy says: ## Annual leave Full-time employees receive **28 days** of paid annual leave per calendar year, ... (Source: Annual leave, sick leave and public holidays). Next step: submit the request in Workday; your manager approves within five working days.",
    "session_id": "lab1-session-1",
    "trace_id": "2b51b0afc43d1b3952bcf5eb6933d9f5",
    "model": "gpt-4.1-mini",
    "steps": 2,
    "outcome": "resolved",
    "intent": "leave",
    "usage": {"input_tokens": 9940, "output_tokens": 315, "cached_tokens": 0, "reasoning_tokens": 0},
    "cost_usd": 0.00448,
    "latency_ms": 3333.1,
    "ttft_ms": 1325.4,
    "tool_calls": ["search_knowledge_base"],
    "budget_decision": "allow",
    "prompt_version": "v1"
}
```

(`make run` exports the Makefile defaults `CACHE=0 DIET=0`, so `cached_tokens` is 0. The latency is the mock's simulated latency.)

Keep the `trace_id`; you will look it up next. The three headers matter: `X-Tenant` becomes a trace tag and a Prometheus label, `X-User` becomes `user_id`, `X-Session` groups turns into a session. Send a second message with the same `X-Session` and notice `steps` and `usage` change.

> **Checkpoint 4:** you received a JSON answer with a `trace_id`, `usage` and `cost_usd`.

---

## Step 5: Read the trace

### Online path (Langfuse)

Open Langfuse → **Tracing → Traces** and click the newest trace (or paste the `trace_id` into the search box). You should see this tree:

```text
invoke_agent atlas                            agent        $0.00448
├── guardrail injection_check                 guardrail
├── step 1                                    span
│   ├── chat gpt-4.1-mini                     generation   3,262 → 44 tokens    $0.0013752
│   └── execute_tool search_knowledge_base    retriever
└── step 2                                    span
    └── chat gpt-4.1-mini                     generation   6,678 → 271 tokens   $0.0031048
```

Click the second generation. On the right you see **Usage** (input 6,678, output 271), **Cost** and **Model**. The cost is computed by Langfuse from its own model price table; in Section 6 you will also compute it yourself and compare.

### Offline path (console exporter)

Look at Terminal 1. With `OTEL_EXPORTER=console` every span is printed as JSON when it ends, children before parents. Find the spans that share your `trace_id` (abridged):

```text
{
    "name": "chat gpt-4.1-mini",
    "context": {"trace_id": "0x2b51b0afc43d1b3952bcf5eb6933d9f5", "span_id": "0x9da29af8f52a3039", ...},
    "parent_id": "0x880a22b68e9dd3eb",
    "attributes": {
        "gen_ai.operation.name": "chat",
        "gen_ai.request.model": "gpt-4.1-mini",
        "atlas.tenant": "hr",
        "gen_ai.usage.input_tokens": 6678,
        "gen_ai.usage.output_tokens": 271,
        "atlas.cost_usd": 0.0031048,
        ...
    },
    ...
}
```

That generation's `parent_id` is the `span_id` of `step 2`, whose own `parent_id` is the `span_id` of `invoke_agent atlas`, the root (its `parent_id` is `null`). That chain is what makes a tree. Paste the agent span and the two generation spans into `notes/lab-01.md`.

Prefer a UI even offline? Skip ahead to Step 6 and use the Ops Console's **Traces** page, which reads the same spans from `.atlas/spans.sqlite`.

> **Checkpoint 5:** you can point at the agent span, the retriever span and the generation span, and read input tokens, output tokens and cost off the generation.

---

## Step 6: A full day of traffic for free

Stop the server (Ctrl+C in Terminal 1). The replay emits a whole simulated day of multi-tenant spans from the mock LLM, without any LLM calls, into the local store (and into Langfuse too with `make replay LANGFUSE=1` when your keys are set).

```bash
OFFLINE=1 make replay
```

Expected:

```text
Replay seed=7  requests=10184  sessions=4000  spans=70560  scores=11884  feedback=1291
Total cost $56.2810   p95 latency 3827 ms   elapsed 19.8s
Cost by tenant: eng=$12.5033, finance=$11.9125, hr=$11.5908, ops=$20.2745
Outcomes: escalated=43, guardrail=72, resolved=10069
Scenarios: none=10184
Store: .atlas/spans.sqlite  (total spans now 70560)
```

Then open the Ops Console:

```bash
make console
```

Streamlit opens `http://localhost:8501`. The home page shows tiles for total cost ($56.28), requests and sessions, p95 and the judge mean; the sidebar lists the pages. **Cost** shows cost by tenant and by feature and the ten most expensive conversations, each linking to the **Traces** page, which draws the same tree as Step 5.

If you replayed with `LANGFUSE=1`, the day also appears in Langfuse. Filter **Traces** by the tag `tenant:finance` to see one tenant's day.

> **Checkpoint 6:** the Ops Console shows four tenants and a non-zero daily total.

---

## Step 7: Record your evidence

Create `notes/lab-01.md`:

```markdown
# Lab 1 evidence

- Mode used: offline / online
- `make test` result: ___ passed, ___ skipped
- First trace id: ___
- Screenshot or console dump of the trace tree: (attach)

## Reading questions
1. Which span is the parent of the generation, and how do you know? (hint: parent_id / tree position)
2. How many input tokens did the generation use, and what fraction of the cost was input vs output?
3. Which attribute tells a tool that this span was an LLM call and not a tool call?
4. In the replayed day, which tenant cost the most and what was its cost per session?
```

Reference answers for the offline path (seed 7, the Makefile default) are in the solution notes below; your online numbers will differ.

> **Checkpoint 7:** all four questions answered with numbers from your own trace.

---

## Stretch goal

Send the same question three times with the same `X-Session`, then once with a new session id. In Langfuse (**Sessions** view) or the Ops Console (**Traces** page, "Session id" box), confirm the first three turns are grouped and the fourth is not. Then look at the `gen_ai.usage.input_tokens` of the three grouped turns: they grow, because Atlas re-sends the history each turn. Write down the three numbers; you will come back to them in lecture 6.5 (the context diet).

Online only: send the same request five times in one minute and look at `gen_ai.usage.cache_read_input_tokens` on the later generations. If it is greater than zero, you have just seen prompt caching (lecture 6.4) without doing anything.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `make: command not found` (Windows) | No GNU make | Use WSL2, or run the commands from the Makefile directly (`uv run uvicorn app.server:app --port 8000`) |
| `uv sync` fails on `arize-phoenix` or `streamlit` | Optional extra failing to build on your platform | `uv sync --extra dev` for now; the dashboards extra is only needed from Step 6 |
| `make test` shows `ModuleNotFoundError: northwind` | Ran pytest outside the venv, or `PYTHONPATH` missing | Use `make test` (it exports `PYTHONPATH=.:src`), or activate `.venv` first |
| `openai_enabled=False` although the key is set | `OFFLINE=1` still set, or key has whitespace | Set `OFFLINE=0`; re-paste the key without spaces |
| `curl` returns `{"detail":"X-Tenant header is required"}` | Missing header | Add `-H 'X-Tenant: hr'` (one of `ops`, `finance`, `hr`, `eng`; `logistics-ops`, `warehouse` and `operations` are accepted aliases for `ops`) |
| `401 Unauthorized` from Langfuse in the server log | Public/secret keys swapped or from another project | Re-copy both keys; `LANGFUSE_BASE_URL` must match the region you signed up in |
| No trace in Langfuse after a successful request | Spans still buffered in the batch processor | Wait 5 seconds, refresh; the server flushes on shutdown (Ctrl+C) |
| Trace appears but the generation has no cost | Model name unknown to Langfuse's price table | Cost is still on the span as `atlas.cost_usd`; Langfuse cost shows once the model is in its table (Section 6 covers overrides) |
| `make replay` says `database is locked` | Server still running and holding the SQLite store | Stop `make run` before replaying, or set `ATLAS_LOCAL_STORE=.atlas/replay.sqlite` for the replay |
| Streamlit opens but shows "no spans" | Console pointed at a different store path | Check the "Span store" box in the sidebar, or run `make console STORE=<path>` with the path you replayed into |

---

## Solution notes

There is nothing to code in this lab; the deliverable is evidence that your environment works and that you can read a trace. Reference values for the offline path (seed 7, prompt v1, Makefile defaults so caching and the diet are off):

| Question | Reference answer |
|---|---|
| Parent of the generation | `step 2` (a step span), whose parent is `invoke_agent atlas` (the agent span, the root); the generation's `parent_id` equals the step's `span_id`, and in Langfuse it is indented under it |
| Tokens and cost split | Whole request: 9,940 input, 315 output, $0.00448. Input cost = 9,940 × $0.40/M = $0.003976 (89%), output = 315 × $1.60/M = $0.000504 (11%). Input dominates: the system prompt plus retrieved KB chunks are large and the answer is short. That ratio is why Section 6 spends two lectures on prompt caching and the context diet (prices: verify current pricing) |
| The attribute that marks an LLM call | `gen_ai.operation.name = "chat"` (the retriever has `"retrieval"`, a tool call `"execute_tool"`, the agent `"invoke_agent"`); Langfuse also shows it as observation type `generation` |
| Most expensive tenant in the replay | `ops` at $20.27 for 1,706 sessions = $0.0119 per session (36% of the day). `finance` has the highest cost per session ($0.0166 over 719 sessions). Source: `make report`, "Cost by tenant" |

Key takeaways to write in your notes:

1. A trace is a tree; `parent_id` builds the tree; the root span is the request.
2. Usage and cost live on the **generation** span, not on the request. Everything in Section 6 rolls up from there.
3. Offline mode produces real spans with realistic numbers. Whenever a later lab says "look at Langfuse", the Ops Console shows the same data from `.atlas/spans.sqlite`.

Reference implementation: `03-code/app/server.py`, `03-code/telemetry/otel_setup.py`, `03-code/simulator/replay.py`.
