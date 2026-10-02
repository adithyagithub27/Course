# Lab 9.1: Trace, Find, Fix with Langfuse v4

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 9.1 (file `lab-08-langfuse-tracing.md`) |
| **Module** | Module 09 — Agent Observability & Tracing |
| **Lectures** | 9.1–9.3 |
| **Duration** | 75 minutes |
| **Difficulty** | Intermediate |
| **Learning Objective** | Trace the TechCorp support agent with the Langfuse v4 SDK (`observe`, `get_client`, `propagate_attributes`), run five queries of which two fail, find the failing span in each trace, attach scores, fix the tool layer and prove the fix by re-running the traces. |
| **Reference solution** | `observability/langfuse_tracing.py`, `demos/m09_lab_trace_find_fix.py` |
| **Verified on** | langfuse 4.16.0, opentelemetry-sdk 1.45.0 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Lab 1.1**
- Lectures 9.1 and 9.2: why traces, observation types, trace attributes, scores
- **Optional:** a free Langfuse Cloud project (or self-hosted Langfuse) for the UI. Without keys, the course captures the same spans in memory and prints the trace tree, so every step works offline.

---

## Setup Instructions

### 1. (Optional) connect Langfuse

In `.env`:

```dotenv
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

(The code also accepts the older `LANGFUSE_HOST` name.) Langfuse's UI steps and free-tier limits change; verify them in the Langfuse docs before recording.

### 2. The v4 API in one table

Langfuse's Python SDK v4 is built on OpenTelemetry. If a tutorial shows `from langfuse.decorators import observe, langfuse_context`, it is v2 and will not run on 4.16.

| Need | v4 API |
|---|---|
| A span per function call | `@observe(name="...", as_type="agent" \| "tool" \| "generation" \| "span" \| ...)` |
| Trace attributes (user, session, tags, version, metadata) | `with propagate_attributes(user_id=..., session_id=..., tags=[...], version=...):` |
| The current client / trace ID | `get_client()`, `get_client().get_current_trace_id()` |
| Update the current span | `get_client().update_current_span(name=..., input=..., output=..., level=...)` |
| Attach an evaluation score | `get_client().create_score(trace_id=..., name=..., value=...)` or `score_current_trace(...)` |
| Send everything before exit | `get_client().flush()` |

---

## Step-by-Step Instructions

### Step 1 — Trace one run and read it

```bash
uv run python -m observability.langfuse_tracing "What is your refund policy?"     # same as: make trace
```

You get one trace: an `agent` observation (`support-agent`) containing `generation` observations (`chat gpt-4.1-mini`, with token usage and cost) and `tool` observations (`tool search_knowledge_base`, with input and output). With keys set, open the trace in the Langfuse UI.

### Step 2 — Use the decorator yourself

Create `my_work/lab08_observe.py`:

```python
"""Lab 9.1 step 2 - the v4 decorator API on your own function."""
from langfuse import get_client, observe, propagate_attributes

from observability.langfuse_tracing import init_langfuse, offline_spans

init_langfuse()   # live with LANGFUSE_* keys; in-memory exporter offline


@observe(name="lookup-policy", as_type="tool")
def lookup_policy(topic: str) -> str:
    return {"refunds": "30-day money-back guarantee"}.get(topic, "unknown")


@observe(name="policy-bot", as_type="agent")
def policy_bot(topic: str) -> str:
    with propagate_attributes(user_id="CUST-001", session_id="lab-9", tags=["lab"]):
        answer = lookup_policy(topic)
        trace_id = get_client().get_current_trace_id()
    return trace_id, answer


trace_id, answer = policy_bot("refunds")
for s in offline_spans(trace_id):
    print(s["type"], s["name"], "user:", s["user_id"], "session:", s["session_id"])
```

```bash
uv run python -m my_work.lab08_observe
```

Both observations carry the user and session: `propagate_attributes` pushes them onto every span created inside the `with` block.

### Step 3 — Five queries, two failures

The scenario: production reports that some customers get "I couldn't find that" answers. You suspect the tool layer. Create `my_work/lab08_trace.py`, which traces the agent with your own tool executor. The executor reproduces the two production bugs: lookups are case-sensitive, and the API article (KB-104) is missing from the search index.

```python
"""Lab 9.1 - Langfuse v4: trace the agent, find the failing spans, fix, re-run."""
from langfuse import get_client, observe

from agents.support_agent import execute_tool
from observability.langfuse_tracing import offline_spans, print_trace, score_trace, traced_support_agent

FIXED = {"on": False}


@observe(name="tool", as_type="tool")
def lab_tools(name: str, arguments: dict) -> str:
    args = dict(arguments)
    if FIXED["on"] and name == "lookup_customer" and "@" in args["identifier"]:
        args["identifier"] = args["identifier"].strip().lower()          # FIX 1: normalise emails
    if not FIXED["on"] and name == "search_knowledge_base" and "api" in args["query"].lower():
        result = "No relevant articles found in the knowledge base."     # the broken index (KB-104 missing)
    else:
        result = execute_tool(name, args)
    level = "WARNING" if result.startswith(("No relevant", "Customer not found")) else "DEFAULT"
    get_client().update_current_span(name=f"tool {name}", input=args, output=result, level=level)
    return result


QUERIES = ["What are your pricing plans?", "How do I reset my password?", "What is your refund policy?",
           "Can you check my account? My email is Alice@Example.com",
           "What are the API rate limits for the Pro plan?"]

for phase in ("BEFORE", "AFTER"):
    FIXED["on"] = phase == "AFTER"
    print(f"--- {phase} FIX ---")
    for q in QUERIES:
        r = traced_support_agent(q, user_id="lab-9", session_id=phase, tool_executor=lab_tools)
        warnings = [s for s in offline_spans(r["trace_id"]) if s["level"] == "WARNING"]
        print(f"{q[:52]:<54} {'FAILING span: ' + warnings[0]['name'] if warnings else 'ok'}")
        score_trace(r["trace_id"], "tool_ok", 0.0 if warnings else 1.0)
        if phase == "BEFORE" and warnings and "API" in q:
            print_trace(r["trace_id"])
```

```bash
uv run python -m my_work.lab08_trace
```

With Langfuse keys set, filter the UI by session `BEFORE` and level `WARNING`, and look at the `tool_ok` score on each trace (`score_trace` calls `create_score`).

### Step 4 — Root cause analysis

For each failing trace, write in `my_work/lab08_rca.md`:

1. **Symptom** (what the customer saw)
2. **Failing span** (name, input, output)
3. **Why the model is not at fault** (it reported the empty result honestly)
4. **Fix** and **how you verified it** (the AFTER run)

The first bug is real in the shipped agent: `lookup_customer` matches emails exactly, so `Alice@Example.com` is "not found". The fix belongs in the tool, not the prompt.

### Step 5 — The same run as OpenTelemetry GenAI spans

```bash
uv run python demos/m09_otel_genai.py      # same as: make otel
```

Compare the attribute names (`gen_ai.operation.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.tool.name`) with what Langfuse shows. They come from the official `opentelemetry-semantic-conventions` package (`gen_ai_attributes`, still marked incubating), not from the third-party `opentelemetry.semconv.ai` module.

---

## Expected Output

Step 2:

```
agent policy-bot user: CUST-001 session: lab-9
tool lookup-policy user: CUST-001 session: lab-9
```

Step 3 (offline; trace IDs and timestamps change on every run):

```
--- BEFORE FIX ---
What are your pricing plans?                           ok
How do I reset my password?                            ok
What is your refund policy?                            ok
Can you check my account? My email is Alice@Example.   FAILING span: tool lookup_customer
What are the API rate limits for the Pro plan?         FAILING span: tool search_knowledge_base
agent      support-agent                   
  generation chat gpt-4.1-mini                usage={"input": 772, "output": 36}
  tool       tool search_knowledge_base       <-- WARNING
             output: No relevant articles found in the knowledge base.
  generation chat gpt-4.1-mini                usage={"input": 848, "output": 29}
--- AFTER FIX ---
What are your pricing plans?                           ok
How do I reset my password?                            ok
What is your refund policy?                            ok
Can you check my account? My email is Alice@Example.   ok
What are the API rate limits for the Pro plan?         ok
```

---

## Verification Checklist

- [ ] No `langfuse.decorators` or `langfuse_context` anywhere in your code
- [ ] Your own function produces an `agent` and a `tool` observation with user and session set
- [ ] You found both failing spans from the trace, not from the code
- [ ] Each trace carries a `tool_ok` score
- [ ] The RCA names the span, the cause and the verified fix
- [ ] You can map three Langfuse fields to their `gen_ai.*` OpenTelemetry names

---

## Common Pitfalls

1. **No traces in the UI.** Check the three `LANGFUSE_*` variables and that the process calls `get_client().flush()` (or lives long enough to export). Offline mode never contacts a server.
2. **Trace attributes missing on child spans.** Set them with `propagate_attributes(...)` around the work, not after it.
3. **Blaming the model.** In both failures the model behaved correctly with what the tool returned. The trace shows that in one look; the final output alone does not.
4. **Logging secrets.** Tool inputs and outputs are stored in the trace. Mask PII before sending traces to a shared backend (Langfuse supports a `mask=` function on the client).

---

## Extension Challenge

1. Run `uv run python demos/m09_langfuse_tracing.py`: four traced conversations for three customers, with cost per trace. Which trace is the most expensive and why?
2. Run `uv run python demos/m09_cost_analysis.py` and find what share of input tokens is fixed overhead (system prompt + tool schemas). This is the hotspot Module 10 attacks.
3. Fix the case-sensitivity bug properly in `agents/support_agent.py` (`execute_tool`), add a unit test for `Alice@Example.com`, and run `make test`.
