# Langfuse v4 Cheat Sheet

**Used in:** 2.3, 4.1-4.7, 5.2, 8.2, 8.6, 10.2, 13.1
**Scope:** only the API forms verified for the course in curriculum §6 (**langfuse 4.15**, the OpenTelemetry-based SDK).

> **APIs verified on langfuse 4.15; check the repo README for updates.** Anything not on this sheet: check the official docs for your installed version before using it. In particular, **there is no `update_current_trace` on langfuse 4.x**: trace-level `session_id`, `user_id`, `tags` and `metadata` are set with the `propagate_attributes(...)` context manager. Do **not** use v2/v3 idioms (`langfuse.trace(...)`, `langfuse_context`, `Langfuse().generation(...)`); they are not what this course teaches.

---

## 1. Import and client

```python
from langfuse import Langfuse, get_client, observe

lf = Langfuse(
    public_key=..., secret_key=..., base_url=...,      # from .env: LANGFUSE_PUBLIC_KEY / SECRET_KEY / BASE_URL
    environment="dev", release="v1.2.0",              # project-per-environment (10.3); release tags for annotations (9.3, 13.3)
    sample_rate=1.0,                                  # head sampling (4.6); lower in prod
    mask=mask_fn,                                     # PII masking function from src/northwind/pii.py (10.2)
    flush_at=..., flush_interval=...,                 # batching (4.6)
)
client = get_client()                                 # anywhere after init
```

Mental model (4.1): SDK v4 is an **OpenTelemetry exporter plus semantics**. Your OTel spans become Langfuse **observations**; Langfuse adds observation **types**, **traces**, **sessions**, **users**, **environments**, **releases**, **scores**, **prompts** and **datasets** on top.

## 2. Observations with `@observe`

```python
@observe(as_type="agent")            # also: "tool", "generation", "retriever", "guardrail", "chain", "embedding"
def run_atlas(question, *, session_id, user_id, tenant): ...

@observe(as_type="tool")
def lookup_ticket(ticket_id): ...

@observe(as_type="retriever")
def search_knowledge_base(query, k): ...
```

Or as a context manager when a decorator doesn't fit (tool loop bodies, 5.2):

```python
with client.start_as_current_observation(name="search_knowledge_base", as_type="tool", input=redacted_args) as span:
    result = ...
    span.update(output=redacted_result)
```

## 3. Updating the current observation and trace

```python
# on a generation (inside the LLM call wrapper)
client.update_current_generation(
    model="gpt-4.1-mini",
    usage_details={"input": 1200, "output": 180, "cache_read_input_tokens": 900},
    cost_details={"input": 0.00048, "output": 0.000288},        # from src/northwind/pricing.py
    completion_start_time=first_chunk_time,                     # TTFT (5.4)
    model_parameters={...},
)

# on any observation
client.update_current_span(metadata={...}, level="WARNING", status_message="tool retried")

# on the trace (session / user / tenant slicing, 4.3)
with propagate_attributes(session_id=session_id, user_id=user_id, tags=[tenant, feature], metadata={...}):
    ...  # every span opened inside carries session.id, user.id, langfuse.trace.tags
# ^ verify exact name on the installed SDK
```

Rules: `usage_details` keys are Langfuse's generic names (`input`, `output`, plus cache keys); `cost_details` is what the Ops Console and the showback sum. Set **both**; don't rely on backend-side pricing alone for a model you route to.

## 4. Scores (4.5, 8.2, 8.3)

```python
client.score_current_trace(name="resolved", value=1, data_type="BOOLEAN", comment="ticket created")
client.create_score(trace_id=trace_id, name="judge_grounded", value=0.8)        # out-of-band judge (evals/online_judge.py)
```

Score names used in the course: `resolved`, `judge_resolved`, `judge_grounded`, `judge_safe_escalation`, `feedback_thumbs`, `guardrail_injection` (boolean, 4.7).

## 5. Prompts (4.4; Incident 3)

```python
client.create_prompt(name="atlas-system", prompt=..., labels=["production"], type="text")
prompt = client.get_prompt("atlas-system", label="production", fallback=DEFAULT_PROMPT, cache_ttl_seconds=60)
```

- Labels (`production`, `staging`) are how you roll back: put the `production` label on the previous version (11.4).
- Always pass a `fallback` so a backend outage doesn't take the agent down (13.5).
- Record the prompt version on each generation so drift and incidents can be attributed (8.5, 11.4).

## 6. Datasets (4.5, 8.6)

```python
client.create_dataset(name="atlas-failures")
client.create_dataset_item(dataset_name="atlas-failures", input=..., expected_output=..., source_trace_id=trace_id)
```

Promote **masked** traces only (10.2). The dataset feeds offline evals before any prompt promotion.

## 7. Masking, sampling, blocking, shutdown (4.6, 10.2)

```python
def mask_fn(data):            # called on inputs/outputs/metadata before export
    return pii.mask(data)     # src/northwind/pii.py: emails, phones, employee ids, card numbers → hashes/placeholders

lf = Langfuse(..., mask=mask_fn, sample_rate=0.2, blocked_instrumentation_scopes=[...])
...
client.flush(); client.shutdown()      # on process exit; never block inside a request handler
```

## 8. Reading the UI (2.3, 4.3, 9.4)

| Question | Where |
|---|---|
| Why did it call that tool, with what, what came back? | Trace view → tool observation → input/output (redacted) |
| How many steps? | Trace view → count step observations |
| Where did the tokens / cost go? | Trace view → generation observations → usage and cost |
| Where did the time go? | Trace view waterfall; `completion_start_time` for TTFT |
| Which tenant / user / session? | Sessions view; filter by tag `tenant=`, by `user_id`, by `session_id` |
| Which prompt version? | Generation → linked prompt; Prompts view for labels |
| Is quality drifting? | Scores over time by tag; dashboards / saved views (9.4) |

## 9. Self-hosting (13.1)

`deploy/docker-compose.langfuse.yml` brings up Langfuse locally; **verify it against the current Langfuse compose file** before use, set the environment variables it requires, create a project, and point `LANGFUSE_BASE_URL` at it. The SDK code doesn't change.

## 10. What is not portable (12.1)

Scores, prompts, datasets, saved views and dashboards are Langfuse concepts. Traces are OpenTelemetry and travel anywhere via the collector (13.2).
