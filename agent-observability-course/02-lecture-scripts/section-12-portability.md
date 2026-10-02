# Section 12: Portability and Alternatives

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈34 min (6 lectures, curriculum v1.0)
> **Source of truth:** `01-curriculum/curriculum.md`; decision matrix `10-resources/backend-decision-matrix.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / langsmith 0.14; check the repo README for updates."
> **Verification note:** LangSmith calls (`traceable`, `wrap_openai`, `Client.create_feedback`, `get_current_run_tree`) and the OTLP HTTP exporter (`OTLPSpanExporter(endpoint=, headers=, timeout=)`) were checked against the installed packages on 2026-09-28. The gRPC OTLP exporter is **not** installed in the course environment; every example uses HTTP/protobuf. Phoenix, OpenLLMetry and Datadog specifics are conceptual: say "verify against current docs" on screen wherever the footer says so.

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with Atlas or a backend UI. Record the real screen. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only, not cues, code, tables or slide text.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 12.1 | Vendor lock-in and the OTel escape hatch | SL | 6:00 | ~730 |
| 12.2 | Code-along: same Atlas, traced to LangSmith | SC | 8:00 | ~840 |
| 12.3 | Arize Phoenix and OpenInference | SC | 7:00 | ~620 |
| 12.4 | OpenLLMetry, Datadog and the enterprise APMs | SL | 6:00 | ~740 |
| 12.5 | Decision matrix: choosing your backend | SL | 5:00 | ~525 |
| 12.6 | Quiz: Portability | QZ | 2:00 total (1:00 video) | ~90 |

**Names used in this section (match `03-code/`).** `telemetry/otel_setup.py::configure_tracing(settings, exporter_kind=)` with `OTEL_EXPORTER` values `console | otlp | file | langfuse | none | memory`; `_make_exporter`, `SafeSpanExporter`; env `OTEL_EXPORTER_OTLP_ENDPOINT` (`Settings.otel_endpoint`). `telemetry/langsmith_setup.py::traced(name, run_type)`, `wrap_openai_if_enabled(client)`, `send_feedback(run_id, key, score, comment)`, `langsmith_enabled()`; env `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT` (plus `LANGSMITH_TRACING=true` for the SDK). `telemetry/langfuse_setup.py::trace_attributes()`, `create_score`, `get_prompt_text`, `push_prompts`. `telemetry/genai_attrs.py::set_tenant_context`, `set_llm_usage`, `set_cost`. Installed extras (`pyproject.toml`): `uv sync --extra langsmith`, `uv sync --extra phoenix`. Makefile targets: `make run`, `make stack` (which already runs Phoenix as the compose service `phoenix` on port 6006). **What the repo ships for LangSmith:** `wrap_openai_if_enabled` is wired into `app/agent.py::OpenAIChatClient` (live OpenAI only, `OFFLINE=0`); `traced()` and `send_feedback()` exist in `telemetry/langsmith_setup.py` but are **not** applied in `app/agent.py` or wired into `app/server.py`. 12.2 shows those as the student's additions. **Not in the repo:** an OpenInference mirror inside `set_llm_usage` (12.3 shows it as an optional addition).

---

## Lecture 12.1 — Vendor lock-in and the OTel escape hatch

| Field | Value |
|---|---|
| ID | 12.1 |
| Type | SL (slides + avatar, one screen beat) |
| Target duration | 6:00 (~730 spoken words) |
| Learning objectives | 1. Separate what is portable in your observability setup (spans with GenAI attributes over OTLP) from what is not (scores, prompts, datasets, dashboards, saved views). 2. Explain how the OTel Collector lets you run two backends at once during a migration. 3. Estimate the real cost of switching backends for Atlas in days, not weeks. |
| Prerequisites | Sections 3 and 4 |
| Files used | `telemetry/otel_setup.py`, `telemetry/genai_attrs.py`, `deploy/otel-collector.yaml` |

### Script

[B-ROLL: An invoice on screen. "LLM Observability Platform, annual renewal: +140% vs last year." Cut to a Slack message: "Can we move? How long would it take?"]

[AVATAR]
Your observability vendor just raised prices by a hundred and forty percent at renewal. Your manager asks how long it would take to move. What's your answer?

For most teams the honest answer is "months", because every span, every score and every dashboard is written against one vendor's SDK. For Atlas, the honest answer is about two days, and most of that is dashboards. This lecture is about why, and about what those two days actually contain.

[SLIDE 1: What you built is in layers]
- Layer 1: your code emits OpenTelemetry spans with `gen_ai.*` attributes
- Layer 2: an exporter ships them over OTLP to a backend
- Layer 3: the backend stores, indexes and displays them
- Layer 4: the backend's own features on top: scores, prompts, datasets, dashboards

Think about what you've built in layers. At the bottom, your code creates spans with OpenTelemetry and tags them with the GenAI semantic conventions from Lecture 3.3. Operation name, model, input and output tokens, tool name, agent name, conversation id.

Above that, an exporter ships those spans over OTLP, the OpenTelemetry protocol. Above that, a backend stores and displays them. And on top, each backend adds its own features. Langfuse gives you scores, prompt management, datasets and dashboards.

Here's the point. Layers one and two belong to you and to a standard. Layers three and four belong to the vendor. Switching means swapping the top two layers and leaving the bottom two alone.

[SLIDE 2: What moves for free]
- Traces, spans, attributes, events, status: yes, via OTLP
- GenAI attributes: `gen_ai.usage.*`, `gen_ai.request.model`, `gen_ai.tool.name`: yes
- Resource attributes: `service.name`, `deployment.environment`, release: yes
- Session, user and tenant: yes, if they are span attributes, not SDK-only calls
- Prometheus metrics and Grafana: unaffected, they never touched the LLM backend

What moves for free? Everything that's a span. Traces, attributes, events, status. Every `gen_ai` attribute you set in Lecture 3.4. Your resource attributes, so release and environment come along. And your Prometheus metrics and Grafana dashboards never touched the LLM backend at all, so they don't notice.

One caveat, and it matters. Session, user and tenant move for free *only* if they live as span attributes. `trace_attributes`, our wrapper around Langfuse's `propagate_attributes`, writes Langfuse's own trace fields, and tags arrive anywhere else as an opaque attribute. That's why the agent span also gets `set_tenant_context` from `genai_attrs.py`: plain `session.id`, `user.id`, `atlas.tenant` and `gen_ai.conversation.id`. Standard fields first, vendor fields second, and every backend gets the same dimensions.

[SLIDE 3: What does not move]
- Scores: judge scores, thumbs, guardrail booleans live in the backend's score store
- Prompts: versions, labels, the `production` pointer
- Datasets: `atlas-failures` and everything Lecture 8.6 promoted
- Dashboards, saved views, alert rules built in the vendor UI
- Vendor-specific SDK calls: `update_current_generation(cost_details=)`, `score_current_trace`

What doesn't move. Scores. Every judge score and every thumbs-down you wrote with `create_score` lives in Langfuse's score store, not on the span. Prompts and their labels, which you just spent Incident 3 learning to respect. Datasets. Dashboards and saved views. And any code that calls the Langfuse SDK directly, like `update_current_generation` with cost details or `score_current_trace`.

How much of Atlas is that? Let's count.

[SLIDE 4: Atlas, counted]
| Concern | Where it lives | Portable? |
|---|---|---|
| Span creation and attributes | `telemetry/otel_setup.py`, `genai_attrs.py`, `app/agent.py` | Yes |
| Cost per generation | computed in `src/northwind/pricing.py`, written by `set_cost` as `atlas.cost_usd` and as `langfuse.observation.cost_details` | Attribute yes, Langfuse cost details no |
| Sessions, users, tenants | `session.id`, `user.id`, `atlas.tenant`, `gen_ai.conversation.id` plus `langfuse.trace.tags` | Yes, via attributes |
| Scores | `evals/online_judge.py`, `app/server.py` `/feedback` via `create_score` | No: re-implement per backend |
| Prompts | `app/prompts.py` via `get_prompt_text` / `push_prompts` | No: export and re-import |
| Datasets | `evals/to_dataset.py` | No: export and re-import |
| Metrics and Grafana | `telemetry/metrics.py`, `deploy/grafana/` | Yes, untouched |

Most of Atlas is portable because we were disciplined about where things live. Cost is computed in `pricing.py`, our own code, and written as a span attribute *and* as Langfuse cost details. If Langfuse goes away, the attribute stays.

[SCREEN: Terminal in `03-code/`: `grep -rln "from telemetry.langfuse_setup import" app evals`. Output: `app/agent.py`, `app/prompts.py`, `app/server.py`, `evals/online_judge.py`, `evals/to_dataset.py`. Then `grep -n "langfuse_setup import" app/agent.py` shows only `trace_attributes`.]

Don't take my word for it. Ask the code which files import the Langfuse module. Five. One of them, `agent.py`, only uses `trace_attributes`, which is a no-op without Langfuse. The other four are the non-portable layer: prompts, the feedback endpoint, the online judge and dataset promotion. Four files, each behind a small function in `telemetry/langfuse_setup.py`. That's the two days.

[SLIDE 5: The escape hatch: the Collector]
- Atlas → OTLP → OTel Collector → exporter A (Langfuse) and exporter B (new backend)
- Run both for two weeks; compare; then remove A
- The Collector also masks, samples and batches, once, for every backend
- Full config in Lecture 13.2

And here's the escape hatch. The OpenTelemetry Collector. Instead of exporting from Atlas straight to Langfuse, export to a Collector, and let the Collector fan out to two backends at once. Langfuse and the new one, side by side, for two weeks. Compare the traces. Rebuild the dashboards while the old ones still work. Then remove the old exporter. Atlas never restarts for any of it.

The Collector also does your masking and sampling in one place, which is why it's in Section 13 as part of the production stack.

[SLIDE 6: Rules that keep you portable]
- Compute in your code, then write to the backend: cost, tokens, latency
- Set standard attributes first, vendor fields second
- Put every vendor SDK call behind one function in `telemetry/`
- Export prompts and datasets to files in your repo on a schedule
- Keep dashboards as code where the backend allows it

Six rules. Compute in your code, then write to the backend, never the other way round. Standard attributes first, vendor fields second. Every vendor call goes through one function in `telemetry/`, so switching is editing one file. Export your prompts and datasets to files in your repo on a schedule, because the day you need them is the day you're leaving. And keep dashboards as code wherever the backend allows it. Grafana does. Langfuse dashboards are UI-built today, so screenshot and document them.

[AVATAR]
In the next three lectures you'll actually do the swap. Atlas traced to LangSmith. Atlas traced to Phoenix. And a map of the enterprise APMs, for the day your company says "we already have Datadog."

[SLIDE 7: Recap]
- Spans and GenAI attributes move over OTLP
- Scores, prompts, datasets, dashboards stay behind
- Four files import the vendor module

**Recap:** Spans with GenAI attributes over OTLP move to any backend for free; scores, prompts, datasets and dashboards don't, so keep them behind small functions and export them regularly, and use the Collector to run two backends during a migration.

**Transition:** Next, the same Atlas traced to LangSmith with `traceable` and `wrap_openai`, and what changes when you get there.

### Speaker notes: common student mistakes / Q&A

- "If Langfuse is OTel-based, why aren't scores spans?" Scores are written after the span ends, often by a different process (the judge). OTel has no standard score object yet; the `gen_ai.evaluation.*` attributes exist in semconv 0.66 as incubating and could be used on a separate evaluation span. Mention as a direction, not a recipe.
- Mistake: treating "portable" as "free". Dashboards take real time to rebuild. Two days is for Atlas, which was built with these rules from Section 3.
- Students sometimes ask about Langfuse's export API for prompts and datasets. Point to the Langfuse public API docs and say "verify against current docs".

---

## Lecture 12.2 — Code-along: same Atlas, traced to LangSmith

| Field | Value |
|---|---|
| ID | 12.2 |
| Type | SC (screencast / code-along) |
| Target duration | 8:00 (~840 spoken words; the rest is screen and typing time) |
| Learning objectives | 1. Trace Atlas to LangSmith with `wrap_openai` (shipped) and `@traceable` run types (your addition), with tenant and session metadata. 2. Write thumbs feedback to a LangSmith run with `Client.create_feedback` from the `/feedback` endpoint (your addition). 3. Name the four differences from Langfuse that affect how you'd rebuild scores, sessions and prompts. |
| Prerequisites | 12.1; Sections 4.2, 4.3 and 8.3 |
| Files used | `telemetry/langsmith_setup.py`, `app/agent.py` (`OpenAIChatClient`), `app/server.py`, `.env.example` |

### Script

[B-ROLL: Two browser tabs. Left: a Langfuse trace of Atlas. Right: a LangSmith trace of the same request. Same tree shape: agent, retriever, generation, tool.]

[AVATAR]
Same request. Same Atlas. Two backends, two trees, same shape. That's the payoff of Lecture 12.1, and one part of it already ships in the repo. The rest is about twenty lines you'll add yourself, and I'll mark exactly which is which.

LangSmith is the observability platform from the LangChain team. You don't need LangChain to use it, and Atlas doesn't. We'll use two things from the `langsmith` package: a decorator called `traceable`, and a wrapper for the OpenAI client. Then feedback. Then the differences.

[SCREEN: `.env.example`, the LangSmith block. Footer visible.]

[CODE: env]
```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=atlas
```

Three environment variables. Tracing on, your API key, and a project name. `.env.example` ships the key and the project; add the tracing flag yourself. A LangSmith project is roughly a Langfuse project plus environment: use one per environment, `atlas-dev`, `atlas-prod`. Install the extra with `uv sync --extra langsmith`. Without the key, every helper in our module is a no-op and Atlas runs unchanged; that's the import guard pattern from Lecture 4.1 again.

Now the setup module.

[CODE: `telemetry/langsmith_setup.py`, part 1]
```python
from langsmith import Client, traceable
from langsmith.wrappers import wrap_openai

def langsmith_enabled() -> bool:
    return LANGSMITH_AVAILABLE and bool(os.environ.get("LANGSMITH_API_KEY"))

def wrap_openai_if_enabled(client: Any) -> Any:
    """``wrap_openai(client)`` records every OpenAI call as a LangSmith run."""
    if not langsmith_enabled():
        return client
    return wrap_openai(client)

# app/agent.py::OpenAIChatClient.__init__ already does this:
self._client = wrap_openai_if_enabled(_openai.OpenAI(api_key=api_key, timeout=timeout, max_retries=0))
```

`wrap_openai` takes a normal OpenAI client and returns one that records every completion as a run. Model, messages, output, token usage, latency. It's the equivalent of OpenInference auto-instrumentation from Lecture 3.5, but writing to LangSmith's own format instead of OTel spans. `OpenAIChatClient` in `agent.py` already wraps its client through `wrap_openai_if_enabled`. That part ships. Note what it means: it only fires on real OpenAI calls, so this lecture runs with `OFFLINE=0` and a key.

With only that, LangSmith shows a flat list of model calls, no tree. The tree needs manual runs. In Langfuse you used `@observe`. In LangSmith the equivalent is `@traceable` with a `run_type`. Our module has a `traced` helper that disappears when LangSmith is off, but the shipped agent doesn't use it. This next part is yours to add.

[CODE: `telemetry/langsmith_setup.py::traced` (shipped) and your addition to `app/agent.py` (not in the repo)]
```python
# telemetry/langsmith_setup.py (shipped)
def traced(name: str, run_type: str = "chain") -> Callable[[F], F]:
    """``@traceable`` when LangSmith is enabled, identity otherwise."""
    if not langsmith_enabled():
        return lambda fn: fn
    return traceable(name=name, run_type=run_type)

# app/agent.py (your addition: two decorators on methods that exist)
from telemetry.langsmith_setup import traced

class AtlasAgent:
    @traced("atlas", run_type="chain")
    def run(self, message: str, *, tenant: str, user_id: str = "anonymous", ...) -> AgentResult: ...

    @traced("execute_tool", run_type="tool")
    def _run_tool(self, tc: dict[str, Any], *, step: int, ...) -> tuple[dict[str, Any], bool]: ...

# call-time metadata, so the root run carries tenant and session (app/server.py, your addition):
agent.run(message, tenant=tenant, user_id=user_id, session_id=session_id,
          langsmith_extra={"metadata": {"tenant": tenant, "session_id": session_id, "user_id": user_id}})
```

`traced` checks for the key when the module is imported, so set `LANGSMITH_API_KEY` before Atlas starts.

Run types. LangSmith has seven: `chain`, `llm`, `tool`, `retriever`, `embedding`, `prompt` and `parser`. Notice what's missing compared with Langfuse. There's no `agent` type and no `guardrail` type. The agent loop is a `chain`. A guardrail is a `tool` or a `chain` with a tag. That's the first difference, and it matters when you filter.

[SLIDE 1: LangSmith run types]
- `chain`, `llm`, `tool`, `retriever`, `embedding`, `prompt`, `parser`
- No `agent`, no `guardrail`
- Metadata at call time: `langsmith_extra={"metadata": {...}}`

Metadata goes in at call time through `langsmith_extra`, which every `traceable` function accepts. Tenant, session and user land on the root run. LangSmith groups runs into a thread when metadata carries a `session_id`, `thread_id` or `conversation_id` key, so this is how sessions come back. Verify the exact key names against the current LangSmith docs; they've changed before.

Nesting is automatic. Any `traceable` function called inside another becomes a child run, and every wrapped OpenAI call inside becomes an `llm` child. Same shape as Langfuse, one level shallower: retrieval shows up as a tool run, because we decorated `_run_tool`, not the retriever.

[SCREEN: With the two decorators added: `OFFLINE=0 LANGSMITH_TRACING=true LANGSMITH_API_KEY=... make run`, then `curl` the VPN question with `X-Tenant` and `X-User` headers. Switch to LangSmith, open the trace.]

[DEMO: LangSmith trace view. Root `atlas` chain with metadata panel showing tenant, session_id, user_id. Children: `ChatOpenAI` llm runs with token counts and cost, and an `execute_tool` tool run for `search_knowledge_base`. Verify the exact run names in the current LangSmith UI before recording.]

Run Atlas with the key set, send one question, open the trace. Root run, `atlas`, with our metadata. Under it, the model calls with tokens and LangSmith's own cost estimate, and the tool run. Same shape as Lecture 2.3, different UI.

Now feedback. In Langfuse, thumbs became `create_score` on a trace id. In LangSmith, they become `create_feedback` on a run id.

[CODE: `telemetry/langsmith_setup.py::send_feedback` (shipped) and the `/feedback` wiring (your addition to `app/server.py`)]
```python
# telemetry/langsmith_setup.py (shipped)
def send_feedback(run_id: str, key: str, score: float, comment: str | None = None) -> bool:
    if not langsmith_enabled():
        return False
    try:
        Client().create_feedback(run_id, key, score=score, comment=comment)
        return True
    except Exception as exc:
        log.warning("langsmith feedback failed: %s", exc)
        return False

# app/server.py (your addition): ChatResponse and FeedbackRequest each gain `run_id: str | None = None`
from langsmith.run_helpers import get_current_run_tree
rt = get_current_run_tree()                      # inside the traced run
run_id = str(rt.id) if rt else None

# /feedback already calls create_score(body.trace_id, "user_feedback", ...) for Langfuse; add:
if body.run_id:
    send_feedback(body.run_id, "user_feedback", score=body.score, comment=body.comment)
```

`create_feedback` takes the run id, a key, a score and an optional comment. The key is your score name, `user_feedback`, `judge_grounded`, whatever you used in Langfuse. The shipped `/feedback` body is a trace id, a score of minus one, zero or one, an optional reason and an optional comment, from Lecture 8.3. Add one optional field, `run_id`, to it and to the chat response, and the front end sends it back with the thumbs.

[SCREEN: `curl -X POST localhost:8000/feedback -d '{"trace_id": "...", "run_id": "...", "score": -1, "reason": "unhelpful"}'`. LangSmith run page shows feedback `user_feedback: -1`.]

Post a thumbs-down. The run page shows it. And the judge in `online_judge.py` would call the same function with `key="judge_grounded"` and a float. One function swapped, the rest of Section 8 unchanged.

[SLIDE 2: Four differences that change your code]
| Langfuse | LangSmith | What you rebuild |
|---|---|---|
| Observation types incl. `agent`, `guardrail` | Run types: `chain`, `llm`, `tool`, `retriever`, `embedding`, `prompt`, `parser` | Filters and dashboards keyed on type |
| `create_score(trace_id, name, value)` | `create_feedback(run_id, key, score)` | One function in `evals/` |
| Sessions, users, tags via `trace_attributes()` | Metadata keys via `langsmith_extra`; threads via `session_id` metadata | Metadata mapping, one place |
| Prompt labels (`production`) | LangSmith Prompt Hub with commits and tags | `get_prompt_text` wrapper and the promotion gate |

Four differences that touch code. Types: no `agent` or `guardrail`, so your type-based filters change. Scores become feedback, one function. Sessions become metadata, one mapping. And prompts. LangSmith has a prompt hub with commits and tags; Langfuse has versions and labels. Same idea, different API, so your `get_prompt_text` wrapper and the promotion gate from Incident 3 get reimplemented.

Two more differences that don't touch code but touch your wallet and your data. LangSmith is a hosted service with a self-host option on enterprise plans; Langfuse self-hosts on the free tier, which is Section 13. And LangSmith is not OTel-native in the way Langfuse 4 is. It accepts OTLP and can emit OTel, but its primary path is its own run format. Verify both against the current pricing and docs pages before you decide anything.

[AVATAR]
Total code to trace Atlas to LangSmith: one module of about sixty lines that already ships, two decorators in `agent.py`, and one optional field on two request models. Everything in `src/northwind` didn't notice. That's what Lecture 12.1 promised.

[SLIDE 3: Recap]
- `wrap_openai` ships; decorators are yours
- `create_feedback` replaces `create_score`
- Types, feedback, sessions, prompts differ

**Recap:** `wrap_openai` records model calls, `@traceable(run_type=)` records agent, tool and retriever runs with tenant and session metadata, `create_feedback` replaces `create_score`, and the four differences that matter are types, feedback, sessions and prompts.

**Transition:** Next, Arize Phoenix: no SDK swap at all, just point the OTLP exporter somewhere else, and meet a second set of semantic conventions.

### Speaker notes: common student mistakes / Q&A

- Verified on langsmith 0.14.1: `traceable(run_type=, name=, tags=, metadata=)`, `langsmith_extra={"metadata": ...}` as a call-time kwarg, `wrap_openai(client)`, `Client.create_feedback(run_id, key, score=, comment=)`, `get_current_run_tree()` returning a `RunTree` with `.id` and `.metadata`. Run types from `RunTypeEnum`: tool, chain, llm, retriever, embedding, prompt, parser.
- The repo's `telemetry/langsmith_setup.py` gates on `LANGSMITH_API_KEY` only; the SDK itself also honours `LANGSMITH_TRACING`. Set both in `.env` to avoid a silent no-op.
- Shipped vs added, say it on screen: `wrap_openai_if_enabled` (wired in `OpenAIChatClient`), `traced`, `send_feedback` and `langsmith_enabled` ship in `telemetry/langsmith_setup.py`. The `@traced` decorators on `AtlasAgent.run` and `_run_tool`, the `run_id` field on `ChatResponse` and `FeedbackRequest`, and the `send_feedback` call in `/feedback` are the student's additions and are **not** in the repo. The shipped `server.py` sends feedback to Langfuse via `create_score`. Show the diff, not a rewrite.
- `wrap_openai` only records live OpenAI calls; with `OFFLINE=1` the mock LLM is used and LangSmith sees only the decorated runs.
- "Can I send OTel spans to LangSmith instead?" It accepts OTLP; the mapping from `gen_ai.*` attributes to LangSmith fields should be verified against current docs. This lecture teaches the native path because that's what the LangSmith UI expects.
- Never show a real `lsv2_` key on screen. Use the placeholder.

---

## Lecture 12.3 — Arize Phoenix and OpenInference

| Field | Value |
|---|---|
| ID | 12.3 |
| Type | SC (screencast / code-along) |
| Target duration | 7:00 (~620 spoken words; the rest is screen time) |
| Learning objectives | 1. Send Atlas traces to a locally running Phoenix by changing only the OTLP exporter endpoint. 2. Explain the relationship between OpenInference conventions and the OTel GenAI conventions, and why a span can carry both. 3. Decide when Phoenix's open-source, local-first model is the right fit. |
| Prerequisites | 12.1; Sections 3.2, 3.3 and 3.5 |
| Files used | `telemetry/otel_setup.py` (`_make_exporter`, `SafeSpanExporter`), `telemetry/openinference_setup.py`, `telemetry/genai_attrs.py` (`set_llm_usage`), `.env.example` |

### Script

[B-ROLL: Browser on `localhost:6006`, the Phoenix UI, empty. A terminal sets two environment variables and starts Atlas; one curl later a trace appears.]

[AVATAR]
No new SDK. No new decorator. Two environment variables change, and Atlas traces land in a different tool. If Lecture 12.1 was the theory of portability, this is the demonstration.

Arize Phoenix is an open-source observability tool from Arize. It runs locally in one container, stores traces, and has evals and dataset features. What matters for this lecture is that Phoenix speaks OTLP natively. It is an OpenTelemetry backend.

[SCREEN: Terminal.]

[CODE: run Phoenix, one of two ways]
```bash
# if the observability stack is already up (make stack), Phoenix is running: compose service `phoenix`
docker compose -f deploy/docker-compose.observability.yml ps phoenix

# otherwise, standalone (never both: they fight over port 6006)
docker run -p 6006:6006 arizephoenix/phoenix:version-20.18.0   # same tag as the compose file; verify
# UI on http://localhost:6006, OTLP HTTP at http://localhost:6006/v1/traces
```

One container. The UI is on port six thousand and six, and the same port accepts OTLP over HTTP at `/v1/traces`. One warning: the observability stack from Section 13 already runs Phoenix on that port. If `make stack` is up, use its Phoenix; a second container will fail to bind the port. Verify the image tag against the current Phoenix docs on screen.

Now Atlas. Remember `configure_tracing` from Lecture 3.2 and the exporter it builds.

[CODE: `telemetry/otel_setup.py`, the OTLP branch, as shipped]
```python
def _make_exporter(kind: str, settings: Settings) -> SpanExporter | None:
    ...
    if kind == "otlp":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        return OTLPSpanExporter(endpoint=settings.otel_endpoint, timeout=5)

# configure_tracing: every exporter is wrapped so a dead backend never raises into a request
safe = SafeSpanExporter(exp, name=name)
provider.add_span_processor(BatchSpanProcessor(safe, max_queue_size=2048, max_export_batch_size=256,
                                               schedule_delay_millis=1000, export_timeout_millis=5000))
```

This is the code you already have. The HTTP protobuf exporter, endpoint from settings, a five-second timeout, wrapped in `SafeSpanExporter` and a batch processor. We use the HTTP exporter throughout the course because the gRPC exporter isn't installed in the course environment, and HTTP goes through proxies more easily.

[CODE: env]
```bash
OTEL_EXPORTER=otlp
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:6006/v1/traces
```

Exporter kind set to `otlp`, endpoint set to Phoenix. No headers, because local Phoenix has no auth by default. That's the whole change.

[SCREEN: `OTEL_EXPORTER=otlp OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:6006/v1/traces make run`, curl the VPN question, switch to Phoenix.]

[DEMO: Phoenix trace view. Root span `invoke_agent atlas`, children `guardrail injection_check`, `step 1` with `chat gpt-4.1-mini` and `execute_tool search_knowledge_base`, `step 2` with `chat gpt-4.1-mini`. Attributes panel on a generation shows `gen_ai.usage.input_tokens`, `gen_ai.request.model`, `atlas.tenant`, `atlas.cost_usd`. Verify how the current Phoenix UI renders `gen_ai.*` token counts before recording.]

Run Atlas, one question, open Phoenix. There's the trace. Root, guardrail, two steps, two generations and the retriever. Open a generation span's attributes and look closely, because there are two vocabularies in this world, and right now you're looking at one of them.

[SLIDE 1: Two conventions on one span]
| Concept | OTel GenAI (semconv 0.66, incubating) | OpenInference |
|---|---|---|
| Kind of span | `gen_ai.operation.name = chat` | `openinference.span.kind = LLM` |
| Model | `gen_ai.request.model` | `llm.model_name` |
| Input tokens | `gen_ai.usage.input_tokens` | `llm.token_count.prompt` |
| Output tokens | `gen_ai.usage.output_tokens` | `llm.token_count.completion` |
| Tool name | `gen_ai.tool.name` | `tool.name` |
| Retrieval docs | `gen_ai.retrieval.documents` (new) | `retrieval.documents.*.document.content` |

Two conventions. The OTel GenAI semantic conventions, which `genai_attrs.py` sets on every span, Lecture 3.4. And OpenInference, which the `OpenAIInstrumentor` from Lecture 3.5 emits automatically on the spans it creates. OpenInference is Arize's convention, older than the OTel one, and it's what Phoenix's UI reads to render token counts, prompts and retrieval documents.

Why both? Because the OTel GenAI conventions are still incubating. Names may change. OpenInference is stable and Phoenix understands it today. Langfuse reads both. So Atlas emits both, and the cost is a few extra attributes per span. When the GenAI conventions stabilise and every backend reads them, you drop OpenInference. Not before.

[CODE: an optional addition to `telemetry/genai_attrs.py::set_llm_usage` (not in the repo)]
```python
# OpenInference mirror, so Phoenix's token and model columns fill for Atlas's own spans
span.set_attribute("openinference.span.kind", "LLM")
span.set_attribute("llm.model_name", model)
span.set_attribute("llm.token_count.prompt", input_tokens)
span.set_attribute("llm.token_count.completion", output_tokens)
```

This is not in the repo; it's an optional four lines you can add to `set_llm_usage`. Auto-instrumented spans from `OpenAIInstrumentor` already carry OpenInference. Atlas's own generation spans, including every offline mock call, carry only the GenAI attributes. If your Phoenix version doesn't show token counts for them, these four lines fix it. Add a unit test that asserts both names, so the mirror never drifts.

[SCREEN: Phoenix, project view. Token counts and latency per trace. Click into the evals tab briefly.]

Phoenix gives you token counts, latency, a session view keyed on `session.id`, which Atlas already sets, and its own evals and datasets, which overlap with Langfuse's. Same non-portable layer, different vendor.

[SLIDE 2: When Phoenix fits]
- Local-first: one container, no account, good for laptops and air-gapped environments
- Open source with a hosted option (Arize AX) for teams
- Strong on RAG and retrieval debugging; OpenInference is its native tongue
- Weaker fit if you need prompt management with labels the way Incident 3 used them; verify current features
- Best paired with the Collector: Langfuse for prompts and scores, Phoenix for local debugging

When does Phoenix fit? When you want local first: one container, no account, works on a plane. When you're doing heavy RAG debugging, because retrieval documents render beautifully. And as a second backend during development, fed by the Collector, while Langfuse stays the system of record for prompts and scores. Verify its current prompt and score features before you make it your only backend; they've been growing fast.

[AVATAR]
Add up what you changed today: two environment variables, plus four optional attribute lines. That's the escape hatch working. Next, the tools you'll meet when your company already has an APM.

[SLIDE 3: Recap]
- Phoenix is just another OTLP endpoint
- One Phoenix on port 6006, never two
- Mirror OpenInference only if you need it

**Recap:** Phoenix is an OTLP backend, so pointing the exporter at it is the whole migration; it reads OpenInference conventions natively, so you can mirror those next to the incubating GenAI attributes if your Phoenix version needs them, and you run one Phoenix, not two.

**Transition:** Next, OpenLLMetry, Datadog and the enterprise APMs, and how to live in a hybrid setup without instrumenting twice.

### Speaker notes: common student mistakes / Q&A

- "Why not just use OpenInference everywhere?" Because the OTel GenAI conventions are the emerging standard across vendors and the Collector ecosystem. Dual-write is a bridge, not a destination. Say "incubating, names may change" on screen for the `gen_ai.*` column.
- Verified: `OTLPSpanExporter(endpoint=, headers=, timeout=)` from `opentelemetry.exporter.otlp.proto.http.trace_exporter`; the gRPC exporter module is not installed. `GEN_AI_RETRIEVAL_DOCUMENTS` exists in semconv 0.66b0 as incubating. `_make_exporter` and `SafeSpanExporter` are in the shipped `otel_setup.py`.
- Phoenix image tag, ports and the `/v1/traces` path: verify against current docs on the day of recording.
- Mistake: students run Phoenix and Langfuse both on the OTLP exporter and wonder which one gets the spans. Answer: whichever endpoint the env var names, until Lecture 13.2 adds the Collector for fan-out.
- Port conflict: `deploy/docker-compose.observability.yml` already runs `arizephoenix/phoenix:version-20.18.0` on 6006, and the Collector's `otlphttp/phoenix` exporter sends to it. A standalone `docker run -p 6006:6006` while the stack is up fails with "port is already allocated". Use one or the other.
- The OpenInference mirror is not in `genai_attrs.py`. Present it as optional; do not show it as shipped code.

---

## Lecture 12.4 — OpenLLMetry, Datadog and the enterprise APMs

| Field | Value |
|---|---|
| ID | 12.4 |
| Type | SL (slides + avatar, two screen beats) |
| Target duration | 6:00 (~740 spoken words) |
| Learning objectives | 1. Place OpenLLMetry, Datadog LLM Observability and the other APM add-ons in the same layer model as Langfuse, LangSmith and Phoenix. 2. Estimate the cost model of LLM observability inside an APM (per span, per ingested GB, per host) and what it does to your sampling decisions. 3. Design a hybrid: APM for infrastructure and paging, an LLM-native tool for prompts, scores and datasets, connected by the Collector. |
| Prerequisites | 12.1 to 12.3 |
| Files used | `deploy/otel-collector.yaml` (preview of Lecture 13.2) |

### Script

[B-ROLL: A Datadog-style infrastructure dashboard, hundreds of hosts. Zoom into one service tile labelled "atlas". A speech bubble: "Can't the LLM stuff just go in here?"]

[AVATAR]
"We already have Datadog. Can't the LLM stuff just go in there?"

You will hear this sentence, or one with New Relic, Dynatrace, Grafana Cloud or Splunk in it. And the answer is "partly, yes, and here's what you lose and what it costs." This lecture gives you that answer.

[SLIDE 1: Two more families]
- OpenLLMetry (Traceloop): an open-source SDK that emits OTel spans with GenAI attributes from many LLM libraries; ships to any OTLP backend
- APM add-ons: Datadog LLM Observability, New Relic AI Monitoring, Dynatrace, Grafana Cloud, Splunk; LLM views inside the APM you already pay for
- Both sit in the same layers as everything else: instrumentation at the bottom, storage and features at the top

Two families you haven't met. First, OpenLLMetry. It's an open-source instrumentation SDK from Traceloop. You call one init function and it patches OpenAI, Anthropic, popular vector stores and frameworks to emit OpenTelemetry spans with GenAI attributes. It's the auto-instrumentation layer, like OpenInference, but with a different set of integrations. Where the spans go is up to you: any OTLP backend, or Traceloop's own hosted product.

Second, the APM add-ons. Every major APM now has an LLM observability product. Datadog LLM Observability, New Relic AI Monitoring, Dynatrace, Grafana Cloud's offering, Splunk. Their pitch is the sentence you just heard: one vendor, one bill, one login, the LLM traces next to the database traces.

[SLIDE 2: What the APMs do well]
- Correlation: the LLM span next to the HTTP span, the database span and the host metrics
- Paging: the on-call rotation, escalation policies and runbooks already live there
- Compliance: retention, access control and audit already approved by security
- Cost visibility per service across the whole company

Give the APMs their due. Correlation is real: when Atlas is slow, seeing the LLM span, the ticketing API call and the host CPU on one screen is exactly what Incident 2 needed. Paging is already there, with the rotation and escalation policies your company has argued about for years. Security has already approved the retention and access model. And finance already reads cost per service from it.

[SLIDE 3: What you lose or pay for]
- Prompt management with labels: usually missing or thin; verify per vendor
- Scores and datasets: present in some, shallow in most; the eval loop from Section 8 lives elsewhere
- Cost model: per span, per ingested GB or per host; agent traces are large (prompts, tool results)
- Sampling pressure: keeping 100% of LLM spans in an APM can cost more than the LLM calls

What you lose or pay for. Prompt management with labels, the thing Incident 3 turned on, is usually missing or thin. Scores and datasets exist in some, but the eval loop from Section 8 is where LLM-native tools are years ahead. Verify feature by feature; this moves monthly.

[B-ROLL: An APM invoice line item, "LLM spans ingested: 2.1 billion", next to the LLM provider's bill for the same month; the observability line is the larger of the two. Illustrative, not a real invoice.]

And the cost model. APMs price per span, per ingested gigabyte or per host. Agent traces are big. A single Atlas step carries the full prompt, the retrieved chunks and the tool result. How big depends on whether you capture prompt and result text. At company scale, keeping a hundred percent of LLM spans in an APM can cost more than the LLM calls they describe. So the first conversation with the APM team is about sampling, and you already know the answer from Lecture 4.6: head sample by session, tail sample errors and slow traces at a hundred percent.

[SLIDE 4: OpenLLMetry in one line]
```python
from traceloop.sdk import Traceloop
Traceloop.init(app_name="atlas", disable_batch=False)   # verify against current docs
```
- Emits OTel spans with `gen_ai.*` attributes to `OTEL_EXPORTER_OTLP_ENDPOINT`
- Overlaps with OpenInference for OpenAI; pick one auto-instrumentor, not both (Lecture 3.6 double counting)

OpenLLMetry in one line: `Traceloop.init` with an app name, and it emits spans to whatever OTLP endpoint your environment names. Verify the exact call against the current docs; it's shown here for shape. One warning from Lecture 3.6: it overlaps with OpenInference for the OpenAI client. Run both and you double-count every generation. Pick one auto-instrumentor.

[SLIDE 5: The hybrid, with the Collector]
- Atlas → OTLP → Collector
- Exporter 1 → APM: sampled spans, metrics, everything infrastructure and paging needs
- Exporter 2 → Langfuse (or Phoenix): full LLM spans for prompts, scores, datasets
- Collector processors: masking once, tail sampling per destination
- One instrumentation, two audiences

[SCREEN: `deploy/otel-collector.yaml`, the `service.pipelines.traces` block: `exporters: [otlphttp/langfuse, otlphttp/phoenix, debug, spanmetrics]`. Highlight the two `otlphttp` lines.]

Which brings us to the pattern that answers the original question. A hybrid. The Collector config in the repo already exports every trace to two backends, Langfuse and Phoenix. Swap one of them for your APM's OTLP endpoint and you have it. Atlas emits once, to the Collector. The Collector sends sampled spans and metrics to the APM, where paging and correlation live. And it sends full LLM spans to Langfuse or Phoenix, where prompts, scores and datasets live. Masking happens once, in the Collector. Sampling can differ per destination: ten percent to the APM to control the bill, a hundred percent of errors and slow traces to both.

One instrumentation, two audiences. The platform team gets their single pane. You get your eval loop. Nobody instruments twice.

[SLIDE 6: How to have the conversation]
- Ask the APM team for the LLM add-on's price per span or per GB, and their retention default
- Bring your span size and daily span count from the Ops Console
- Propose the hybrid with the Collector config from Lecture 13.2
- Agree what pages from the APM and what is investigated in the LLM tool

[SCREEN: Terminal: `OFFLINE=1 make replay` ends with `Store: .atlas/spans.sqlite (total spans now 70560)`. Then `python -c "import sqlite3; print(sqlite3.connect('.atlas/spans.sqlite').execute('select count(*), round(avg(length(attributes))) from spans').fetchone())"` prints `(70560, 582.0)`.]

How to have the conversation. Ask for the price per span or per gigabyte and the retention default. Bring your own numbers. Atlas's replayed day is seventy thousand five hundred and sixty spans, averaging about six hundred bytes of attributes each in the local store: roughly forty megabytes a day before any prompt text. That's the number the APM team prices. Propose the hybrid, with the Collector config you'll build in Lecture 13.2 as the concrete artefact. And agree on the split: latency, errors and cost page from the APM; quality and prompt investigations happen in the LLM tool.

[AVATAR]
You now know every family of backend: LLM-native, open-source local-first, instrumentation SDKs and APM add-ons. Next, a five-minute decision matrix, so you can choose one in a meeting and defend it.

[SLIDE 7: Recap]
- APMs win correlation, paging, compliance
- LLM tools win prompts, evals, datasets
- One Collector, two exporters: the hybrid

**Recap:** APM add-ons win on correlation, paging and compliance and lose on prompts, evals and cost per span; OpenLLMetry is another OTel instrumentation layer; the hybrid via the Collector gives the platform team one pane and you the eval loop.

**Transition:** Next, the decision matrix: control, cost, compliance, features and lock-in on one page.

### Speaker notes: common student mistakes / Q&A

- The span figures (70,560 spans, about 580 bytes of attributes per span in the SQLite store) are from the baseline `OFFLINE=1 make replay`; recompute if the replay changes. The store keeps attributes as JSON; wire size over OTLP differs (verify with the Collector's own metrics on :8888).
- Everything vendor-specific in this lecture is conceptual and dated. Say "verify against current docs and pricing" on Slides 3 and 4, and check the Traceloop init signature before recording.
- "Datadog also does prompt tracking now." Features move monthly. The teaching point is the layer model and the cost model, not a feature list.
- Mistake: running OpenInference and OpenLLMetry together. Point back to Lecture 3.6, "instrumenting twice".
- Some students work at companies where the APM is mandated. The hybrid is their answer; make sure they know the Collector config in 13.2 is the deliverable to bring to that meeting.

---

## Lecture 12.5 — Decision matrix: choosing your backend

| Field | Value |
|---|---|
| ID | 12.5 |
| Type | SL (slides + avatar, one screen beat) |
| Target duration | 5:00 (~525 spoken words) |
| Learning objectives | 1. Score backend options on five criteria: control, cost, compliance, features and lock-in. 2. Recognise the three situations that decide the answer before the matrix does. 3. Fill in `backend-decision-matrix.md` for your own organisation. |
| Prerequisites | 12.1 to 12.4 |
| Files used | `10-resources/backend-decision-matrix.md` |

### Script

[B-ROLL: A meeting room whiteboard with "Langfuse vs LangSmith vs Datadog???" and three question marks. Cut to the same board with a filled-in five-row table.]

[AVATAR]
You'll be asked to choose. Maybe this month. And the worst way to choose is by feature list, because every vendor's list is longer than yours next quarter. Choose on five criteria that don't change, and know the three situations where the decision is made before you open the matrix.

[SLIDE 1: Five criteria]
1. Control: can you self-host, and who owns the data?
2. Cost: pricing unit (span, GB, seat, host), free tier, and what 100% LLM sampling costs
3. Compliance: data residency, retention control, masking before egress, audit trail
4. Features: tracing, sessions, prompts with labels, scores, datasets, dashboards, alerting
5. Lock-in: OTLP in, export out, how many files change if you leave

Five criteria. Control: can you self-host, and who owns the data? Cost: what's the pricing unit, and what does it cost to keep everything? Compliance: residency, retention, masking before the data leaves your network, and an audit trail for changes like prompt labels. Features: the list, but weighted by what you actually use from Sections 4 through 9. And lock-in: does it accept OTLP, can you export, and how many files change if you leave? For Atlas, you know that last number: four.

[SCREEN: VS Code, `10-resources/backend-decision-matrix.md` open beside the terminal; the terminal reruns `grep -rln "from telemetry.langfuse_setup import" app evals` from Lecture 12.1 and the lock-in row is filled in with "4 files (prompts, /feedback, judge, dataset)".]

Put the grep from Lecture 12.1 straight into the lock-in row. Measured, not estimated.

[SLIDE 2: The matrix, filled in for Atlas]
| | Langfuse | LangSmith | Phoenix | APM add-on |
|---|---|---|---|---|
| Control | Self-host on free tier, or cloud | Cloud; self-host on enterprise | Self-host, one container; cloud option | Vendor cloud, mostly |
| Cost | Free tier, then per-unit; self-host is infra only | Per seat plus per trace tiers | Free OSS; hosted paid | Per span / GB / host; can dominate |
| Compliance | Self-host = full residency; masking in SDK | Vendor-hosted; check region | Self-host = full residency | Usually strong; already approved |
| Features | Prompts with labels, scores, datasets, sessions, dashboards | Strong tracing, evals, prompt hub, threads | Strong RAG debugging, evals, datasets; prompts growing | Correlation, paging; prompts and evals thin |
| Lock-in | OTLP in; scores and prompts vendor-side | Native format; OTLP accepted | OTLP in; OpenInference native | Proprietary agent or OTLP; expensive to leave |
| Atlas fit | Default in this course | Strong alternative for LangChain shops | Local dev and RAG debugging | Hybrid via Collector |

Here's the matrix filled in for Atlas, as of recording. Every cell is dated the moment I say it, so the resource file has a "verified on" line for you to update.

Langfuse: self-hostable on the free tier, OTel-native, has everything Sections 4 through 9 used. It's the course default for those reasons, not because it's perfect. LangSmith: excellent tracing and evals, a natural fit if your team already lives in LangChain, hosted first. Phoenix: the local-first choice and the best RAG debugger. And the APM add-on: strong where APMs are strong, and the place where the hybrid earns its keep.

[SLIDE 3: Three situations that decide first]
- Regulated data and no vendor egress allowed → self-host: Langfuse or Phoenix, masking in SDK and Collector
- Company mandates the APM → hybrid: APM for paging, LLM-native tool for prompts and evals
- Small team, no platform engineers → hosted: Langfuse Cloud or LangSmith; do not run ClickHouse at 2 a.m.

Three situations decide the answer before the matrix does.

One. Regulated data, and your security team says no telemetry leaves the network. Then you self-host. Langfuse or Phoenix, with masking in the SDK from Lecture 4.6 and in the Collector from Lecture 10.2. The matrix only picks between those two.

Two. Your company mandates the APM. Then the answer is the hybrid from Lecture 12.4, and the matrix picks the LLM-native side of it.

Three. Small team, no platform engineers. Then hosted. Langfuse Cloud or LangSmith. Self-hosting means running Postgres, ClickHouse and Redis, and someone owns that at two in the morning. If that someone is also the only person who can fix Atlas, don't.

[SLIDE 4: Fill in your own]
- `10-resources/backend-decision-matrix.md`: the five rows, blank columns, a "verified on" date
- Weight the criteria for your organisation before scoring
- Score, then write one paragraph: the decision and the two things that would change it

Open `backend-decision-matrix.md`. Same five rows, blank columns, a "verified on" date at the top. Before you score anything, weight the criteria for your organisation. A bank weights compliance at forty percent. A startup weights cost and speed. Then score, and write one paragraph: the decision, and the two things that would change it. "We chose Langfuse self-hosted; we'd revisit if the APM's LLM product gained prompt labels, or if we lost our platform engineer."

[AVATAR]
That paragraph is what your manager wants. Not the matrix. The matrix is how you got there, and it's what you show when someone asks "did you consider X?"

[SLIDE 5: Recap]
- Weight five criteria before scoring
- Regulation, APM mandate, team size decide first
- One paragraph: decision plus two triggers

**Recap:** Score backends on control, cost, compliance, features and lock-in, check first whether regulation, an APM mandate or team size has already decided, and write the decision as one paragraph with the two things that would change it.

[SLIDE 6: You can now]
- Separate portable telemetry from vendor features
- Trace Atlas to LangSmith or Phoenix
- Choose and defend a backend in one paragraph

**Transition:** A short quiz on portability, then Section 13, where you self-host the whole stack and gate pull requests on cost and latency.

### Speaker notes: common student mistakes / Q&A

- Every cell in Slide 2 must carry a "verified on" date in the resource file. Re-check pricing pages and self-host options before recording and at each course update.
- Mistake: scoring features first. Insist on weighting criteria first; it changes the answer.
- "Which one do you personally use?" Answer with the situation, not the brand: self-hosted Langfuse for Atlas because the course needs a free, self-hostable, OTel-native default with prompts and scores.

---

## Lecture 12.6 — Quiz: Portability

| Field | Value |
|---|---|
| ID | 12.6 |
| Type | QZ (5 questions, short video intro) |
| Target duration | 2:00 total (1:00 video, ~90 spoken words, about 0:39 of talking at 140 wpm; the quiz itself is untimed) |
| Learning objectives | 1. Check what is and is not portable across backends. 2. Check the LangSmith and Phoenix mechanics. 3. Check the hybrid pattern and the decision criteria. |
| Prerequisites | 12.1 to 12.5 |
| Files used | `06-assessments/quizzes/section-12.md` |

### Script

[AVATAR]
Five questions on Section 12.

[SLIDE 1: Quiz: Portability]
- 5 questions
- What moves over OTLP and what does not
- `traceable` run types and `create_feedback`
- OpenInference vs GenAI conventions
- The hybrid with the Collector

They check what moves over OTLP and what stays behind, the LangSmith run types and feedback call, the two conventions Phoenix reads, and where the Collector sits in a hybrid. One question asks you to count how many Atlas files change when you swap backends. You know that number.

**Recap:** The quiz checks portability boundaries and the mechanics of the two alternative backends.

**Transition:** Section 13 is next: self-host Langfuse, put the Collector in front, and make CI fail when cost or latency regress.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "scores move with the spans". They don't. Point to Slide 3 of Lecture 12.1.
- Second: "LangSmith has an `agent` run type". It doesn't; the agent loop is a `chain`.
