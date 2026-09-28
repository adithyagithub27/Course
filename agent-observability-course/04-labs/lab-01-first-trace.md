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

`make install` runs `uv sync --all-extras`, which creates `.venv/` and installs the pinned stack (`langfuse~=4.15`, `opentelemetry-sdk~=1.45`, `litellm~=1.103`, `openai~=2.54`, `fastapi`, `prometheus-client`, plus the `dev`, `dashboards`, `langsmith` and `phoenix` extras).

Expected output ends with something like:

```text
Resolved 187 packages in 1.2s
Installed 187 packages in 4.8s
```

> **Checkpoint 1:** `uv run python -c "import langfuse, opentelemetry, litellm; print('ok')"` prints `ok`.

---

## Step 2: Run the offline test suite

Nothing here needs a key. The unit tests cover `src/northwind/` (pricing, cost, budget, tokens, latency, SLO, sampling, drift, PII, report) and the integration tests start the FastAPI app in offline mode with an in-memory span exporter.

```bash
make test
```

Expected output (counts will grow as the course evolves; what matters is the last line):

```text
tests/unit/test_pricing.py ..............................             [ 18%]
tests/unit/test_cost.py ....................                          [ 30%]
tests/unit/test_budget.py .........................                   [ 45%]
...
tests/integration/test_spans.py ..........                            [100%]
======================= 164 passed, 3 skipped in 6.41s =======================
```

The 3 skipped tests are marked `live`: they need real keys and are skipped by default.

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
OTEL_EXPORTER=langfuse
```

Create the Langfuse keys under **Project settings → API keys** in a new project called `atlas-dev`. Before you save the OpenAI key, open **platform.openai.com → Settings → Limits** and set a monthly budget of $10 with an email alert at $5. The whole course fits inside that.

Verify the configuration without sending anything:

```bash
uv run python -m northwind.config
```

Expected output (offline):

```text
Settings(offline=True, model='gpt-4.1-mini', escalation_model='gpt-4.1', otel_exporter='console',
         langfuse_enabled=False, openai_enabled=False, local_store_path='.atlas/spans.sqlite', ...)
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
INFO:     Atlas starting (offline=True, exporter=console, tenants=ops,finance,hr,eng)
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Terminal 2:

```bash
curl -s http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant: hr' \
  -H 'X-User: NW-10433' \
  -H 'X-Session: lab1-session-1' \
  -d '{"message": "How many days of parental leave do I get?"}' | python3 -m json.tool
```

Expected response (offline wording is deterministic; online wording varies):

```json
{
    "answer": "Northwind offers 16 weeks of paid parental leave for primary carers and 4 weeks for secondary carers, to be taken within 12 months of the birth or adoption. Source: leave policy.",
    "trace_id": "4f1c9a7e2b3d4c5e8f9a0b1c2d3e4f5a",
    "session_id": "lab1-session-1",
    "steps": 2,
    "usage": {"input_tokens": 1184, "output_tokens": 58, "cached_tokens": 0},
    "cost_usd": 0.000566,
    "latency_ms": 812
}
```

Keep the `trace_id`; you will look it up next. The three headers matter: `X-Tenant` becomes a trace tag and a Prometheus label, `X-User` becomes `user_id`, `X-Session` groups turns into a session. Send a second message with the same `X-Session` and notice `steps` and `usage` change.

> **Checkpoint 4:** you received a JSON answer with a `trace_id`, `usage` and `cost_usd`.

---

## Step 5: Read the trace

### Online path (Langfuse)

Open Langfuse → **Tracing → Traces** and click the newest trace (or paste the `trace_id` into the search box). You should see this tree:

```text
atlas.chat                                  agent        812 ms   $0.000566
├── search_knowledge_base                   retriever     23 ms
├── openai.chat gpt-4.1-mini                generation   640 ms   1184 → 58 tokens   $0.000566
└── (no tool span: the KB answered the question)
```

Click the generation. On the right you see **Usage** (input 1184, output 58, cached 0), **Cost** and **Model**. The cost is computed by Langfuse from its own model price table; in Section 6 you will also compute it yourself and compare.

### Offline path (console exporter)

Look at Terminal 1. With `OTEL_EXPORTER=console` every span is printed as JSON when it ends. Find the three spans that share your `trace_id`:

```text
{
    "name": "openai.chat gpt-4.1-mini",
    "context": {"trace_id": "0x4f1c9a7e2b3d4c5e8f9a0b1c2d3e4f5a", "span_id": "0x9b8a7c6d5e4f3a2b", ...},
    "parent_id": "0x1a2b3c4d5e6f7a8b",
    "kind": "SpanKind.CLIENT",
    "attributes": {
        "gen_ai.operation.name": "chat",
        "gen_ai.provider.name": "openai",
        "gen_ai.request.model": "gpt-4.1-mini",
        "gen_ai.response.model": "gpt-4.1-mini",
        "gen_ai.usage.input_tokens": 1184,
        "gen_ai.usage.output_tokens": 58,
        "gen_ai.usage.cache_read_input_tokens": 0,
        "atlas.cost_usd": 0.000566,
        "atlas.tenant": "hr"
    },
    ...
}
```

The `parent_id` of the generation and the retriever both point at the `atlas.chat` span's `span_id`: that is what makes them children in a tree. Paste the three spans into `notes/lab-01.md`.

Prefer a UI even offline? Skip ahead to Step 6 and use the Ops Console's **Trace explorer** tab, which reads the same spans from `.atlas/spans.sqlite`.

> **Checkpoint 5:** you can point at the agent span, the retriever span and the generation span, and read input tokens, output tokens and cost off the generation.

---

## Step 6: A full day of traffic for free

Stop the server (Ctrl+C in Terminal 1). The replay emits a whole simulated day of multi-tenant spans from the mock LLM, without any LLM calls, into the local store (and into Langfuse if `OTEL_EXPORTER=langfuse`).

```bash
OFFLINE=1 make replay
```

Expected:

```text
Replay seed=7  requests=10184  sessions=4000  spans=70560  scores=11884  feedback=1291
Total cost $56.70   p95 latency 3827 ms   elapsed 19.5s
Cost by tenant: eng=$12.60, finance=$12.00, hr=$11.67, ops=$20.43
Outcomes: escalated=43, guardrail=72, resolved=10069
Scenarios: none=10184
Store: .atlas/spans.sqlite  (total spans now 70560)
```

Then open the Ops Console:

```bash
make console
```

Streamlit opens `http://localhost:8501`. The **Overview** tab shows cost per tenant, requests per hour and p95 latency for the replayed day; the **Trace explorer** tab lets you click into any trace and see the same tree as Step 5.

If you are on the online path with `OTEL_EXPORTER=langfuse`, the replay also appears in Langfuse under the environment `dev` with the tag `replay`. Filter **Traces** by `tags = replay` and `metadata.tenant = finance` to see one tenant's day.

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

Reference answers for the offline replay with seed 42 are in the solution notes below; your online numbers will differ.

> **Checkpoint 7:** all four questions answered with numbers from your own trace.

---

## Stretch goal

Send the same question three times with the same `X-Session`, then once with a new session id. In Langfuse (**Sessions** view) or the Ops Console (**Sessions** tab), confirm the first three turns are grouped and the fourth is not. Then look at the `gen_ai.usage.input_tokens` of the three grouped turns: they grow, because Atlas re-sends the history each turn. Write down the three numbers; you will come back to them in lecture 6.5 (the context diet).

Online only: send the same request five times in one minute and look at `gen_ai.usage.cache_read_input_tokens` on the later generations. If it is greater than zero, you have just seen prompt caching (lecture 6.4) without doing anything.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `make: command not found` (Windows) | No GNU make | Use WSL2, or run the commands from the Makefile directly (`uv run uvicorn app.server:app --port 8000`) |
| `uv sync` fails on `arize-phoenix` or `streamlit` | Optional extra failing to build on your platform | `uv sync --extra dev` for now; the dashboards extra is only needed from Step 6 |
| `make test` shows `ModuleNotFoundError: northwind` | Ran pytest outside `uv run`, or `pythonpath` missing | Use `make test` or `uv run pytest`; check `[tool.pytest.ini_options] pythonpath = [".", "src"]` |
| `openai_enabled=False` although the key is set | `OFFLINE=1` still set, or key has whitespace | Set `OFFLINE=0`; re-paste the key without spaces |
| `curl` returns `{"detail":"X-Tenant header required"}` | Missing header | Add `-H 'X-Tenant: hr'` (one of `ops`, `finance`, `hr`, `eng`; `logistics-ops`, `warehouse` and `operations` are accepted aliases for `ops`) |
| `401 Unauthorized` from Langfuse in the server log | Public/secret keys swapped or from another project | Re-copy both keys; `LANGFUSE_BASE_URL` must match the region you signed up in |
| No trace in Langfuse after a successful request | Spans still buffered in the batch processor | Wait 5 seconds, refresh; the server flushes on shutdown (Ctrl+C) |
| Trace appears but the generation has no cost | Model name unknown to Langfuse's price table | Cost is still on the span as `atlas.cost_usd`; Langfuse cost shows once the model is in its table (Section 6 covers overrides) |
| `make replay` says `database is locked` | Server still running and holding the SQLite store | Stop `make run` before replaying, or set `ATLAS_LOCAL_STORE=.atlas/replay.sqlite` for the replay |
| Streamlit opens but shows "no spans" | Console pointed at a different store path | Check `ATLAS_LOCAL_STORE` is the same in both commands |

---

## Solution notes

There is nothing to code in this lab; the deliverable is evidence that your environment works and that you can read a trace. Reference values for the offline path (seed 42, prompt v1):

| Question | Reference answer |
|---|---|
| Parent of the generation | `atlas.chat` (the agent span); the generation's `parent_id` equals its `span_id`, and in Langfuse it is indented under it |
| Tokens and cost split | 1184 input, 58 output; input cost = 1184 × $0.40/M = $0.000474 (84%), output = 58 × $1.60/M = $0.000093 (16%). Input dominates: the system prompt plus retrieved KB chunks are large and the answer is short. That ratio is why Section 6 spends two lectures on prompt caching and the context diet |
| The attribute that marks an LLM call | `gen_ai.operation.name = "chat"` (a tool call has `"execute_tool"`, an agent invocation `"invoke_agent"`); Langfuse also shows it as observation type `generation` |
| Most expensive tenant in the replay | `hr` at $11.02 for 256 sessions = $0.0430 per session; `finance` has the highest cost per session ($0.0466) because finance questions hit `lookup_ticket` more often, which adds a step |

Key takeaways to write in your notes:

1. A trace is a tree; `parent_id` builds the tree; the root span is the request.
2. Usage and cost live on the **generation** span, not on the request. Everything in Section 6 rolls up from there.
3. Offline mode produces real spans with realistic numbers. Whenever a later lab says "look at Langfuse", the Ops Console shows the same data from `.atlas/spans.sqlite`.

Reference implementation: `03-code/app/server.py`, `03-code/telemetry/otel_setup.py`, `03-code/simulator/replay.py`.
