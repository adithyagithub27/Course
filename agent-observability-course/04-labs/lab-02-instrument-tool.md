# Lab 2: Instrument a New Tool End to End

| Field | Details |
|---|---|
| **Section / lecture** | Section 3, lecture 3.7 |
| **Time estimate** | 45 to 60 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Prove that `check_shipment`, Atlas's newest tool, produces a correct `execute_tool` span (GenAI attributes, arguments, redacted result, parent step under the agent), pin that with an integration test, and close one real gap: the span has no low-cardinality domain attribute you can filter on. |
| **You will produce** | `tests/integration/test_check_shipment_span.py` (three tests), a three-line change in `app/agent.py::_run_tool`, and `notes/lab-02.md` with before/after console output |

---

## Prerequisites

- Lab 1 complete (`make test` green, you can read a span tree).
- Lectures 3.1 to 3.6 watched, especially 3.3 (the GenAI conventions), 3.4 (tagging tool spans) and 3.6 (orphan spans and double counting).
- `app/tools.py`, `app/agent.py`, `telemetry/genai_attrs.py` and `tests/integration/test_spans.py` open in your editor.

## Background

Every tool call in Atlas runs inside one place: `AtlasAgent._run_tool` in `app/agent.py`. It opens an `execute_tool <name>` span, calls the tool, and sets the GenAI attributes through `ga.set_tool` (operation `execute_tool`, `gen_ai.tool.name`, call id, arguments and result, both passed through the PII mask). It adds `atlas.tenant` and `atlas.tool.result_tokens`, and on a failed tool it sets status `ERROR` and `error.type`. The retriever gets extra attributes (`atlas.retrieval.top_k`, `hits`, scores) from `ga.set_retrieval`.

So `check_shipment(tracking_id)` is already traced. What nobody has done is **prove** it: no test pins its span name, its `tracking_id` argument or its parent, so a refactor could silently break it and every shipment question would vanish from cost and latency views. And the span has one real gap: the shipment's status (`created`, `in_transit`, `at_hub`, `out_for_delivery`, `delivered`, `exception`) is buried in a JSON string, so you can't filter "all exception shipments" in Langfuse or the console.

The conventions you will check (incubating in `opentelemetry-semantic-conventions` 0.66b0; names may change, which is why application code uses the constants in `gen_ai_attributes`, imported as `g`):

| Attribute | Value on the `check_shipment` span |
|---|---|
| span name | `execute_tool check_shipment` |
| `gen_ai.operation.name` | `execute_tool` |
| `gen_ai.tool.name` | `check_shipment` |
| `gen_ai.tool.call.id` | the tool call id from the model response |
| `gen_ai.tool.call.arguments` | `{"tracking_id": "SHP-4471120"}` (masked) |
| `gen_ai.tool.call.result` | the tool's JSON result (masked) |
| `atlas.tenant`, `atlas.tool.result_tokens` | Atlas's own attributes |
| parent | a `step n` span, whose parent is `invoke_agent atlas` |

---

## Step 1: See the span

Terminal 1, the console exporter on (Atlas loads `.env` itself; variables set in your shell win):

```bash
OFFLINE=1 OTEL_EXPORTER=console make run
```

Terminal 2:

```bash
curl -s http://localhost:8000/chat -H 'Content-Type: application/json' \
  -H 'X-Tenant: ops' -H 'X-User: NW-22011' -H 'X-Session: lab2-a' \
  -d '{"message": "Where is shipment SHP-4471120?"}' | python3 -m json.tool
```

The answer (offline, deterministic):

```text
Shipment SHP-4471120 is **created** at the Hamburg hub, ETA 2026-09-20. (Source: Internal shipment tracking and delivery exceptions). Next step: no action needed; I can check again later.
```

In Terminal 1, find the span named `execute_tool check_shipment` (abridged):

```text
{
    "name": "execute_tool check_shipment",
    "parent_id": "0x…",                     <- the span_id of "step 1"
    "attributes": {
        "atlas.tenant": "ops",
        "gen_ai.operation.name": "execute_tool",
        "gen_ai.tool.name": "check_shipment",
        "gen_ai.tool.type": "function",
        "gen_ai.tool.call.id": "call_…",
        "gen_ai.tool.call.arguments": "{\"tracking_id\": \"SHP-4471120\"}",
        "gen_ai.tool.call.result": "{\"tracking_id\": \"SHP-4471120\", \"status\": \"created\", \"hub\": \"Hamburg\", \"eta\": \"2026-09-20\", \"exception_reason\": null}",
        "atlas.tool.result_tokens": …
    },
    ...
}
```

Check it against the table above, then follow the `parent_id`: it points at `step 1`, and `step 1`'s parent is `invoke_agent atlas`. Paste the span into `notes/lab-02.md` under "Before".

> **Checkpoint 1:** you can name the span, its tool name, its argument and its parent chain.

---

## Step 2: Read where the span is made

Open `app/agent.py` and find `_run_tool`. The pattern:

```python
with self.tracer.start_as_current_span(ga.tool_span_name(name)) as tspan:
    tspan.set_attribute(ga.ATLAS_TENANT, tool_ctx.tenant)
    try:
        tres = execute_tool(name, args, tool_ctx)
        content, ok = tres.content, tres.ok
        ga.set_tool(tspan, name=name, call_id=tc.get("id"),
                    arguments=args if self.capture_content else None,
                    result=content if self.capture_content else None)
        if name == "search_knowledge_base" and ok:
            ...
            ga.set_retrieval(tspan, query=..., top_k=used_k, hits=hits, scores=..., doc_ids=...)
        if not ok:
            tspan.set_attribute("error.type", err_type)
            tspan.set_status(otel_trace.Status(otel_trace.StatusCode.ERROR, err_type))
    ...
    tspan.set_attribute("atlas.tool.result_tokens", result_tokens)
```

Three things to notice, because they are the three mistakes from Lecture 3.6:

1. `start_as_current_span` (not `start_span`) makes the tool span the current context, so it attaches to whatever is current: the step span inside the agent span.
2. Arguments and results go through `ga.set_tool`, which runs them through the PII mask before they reach the span. Never `json.dumps(result)` straight onto a span.
3. A failed tool sets status `ERROR` and an `error.type`. A tool that fails silently is worse than one that is not traced at all.

> **Checkpoint 2:** you can explain, in one sentence each, why `start_as_current_span`, masking and error status are all present.

---

## Step 3: Pin it with a test

Create `tests/integration/test_check_shipment_span.py`. The `client` fixture in `tests/integration/conftest.py` starts the app offline with an in-memory exporter (`client.exporter`).

```python
"""Lab 2: prove check_shipment's span is right (and stays right)."""

import json

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g
from opentelemetry.trace import StatusCode

OPS = {"X-Tenant": "ops", "X-User": "NW-22011"}


def _chat(client, message, **body):
    r = client.post("/chat", json={"message": message, **body}, headers=OPS)
    assert r.status_code == 200, r.text
    return r.json()


def _by_name(spans, prefix):
    return [s for s in spans if s.name.startswith(prefix)]


def test_check_shipment_emits_tagged_tool_span(client):
    _chat(client, "Where is shipment SHP-4471120?", session_id="lab2-1")
    spans = client.exporter.get_finished_spans()
    tools = _by_name(spans, "execute_tool check_shipment")
    assert len(tools) == 1, "exactly one tool span per call (no double instrumentation)"
    tool = tools[0]
    agent = _by_name(spans, "invoke_agent atlas")[0]
    attrs = tool.attributes
    assert attrs[g.GEN_AI_OPERATION_NAME] == "execute_tool"
    assert attrs[g.GEN_AI_TOOL_NAME] == "check_shipment"
    assert json.loads(attrs[g.GEN_AI_TOOL_CALL_ARGUMENTS]) == {"tracking_id": "SHP-4471120"}
    result = json.loads(attrs[g.GEN_AI_TOOL_CALL_RESULT])
    assert result["tracking_id"] == "SHP-4471120" and result["status"]
    assert attrs["atlas.tenant"] == "ops"
    assert attrs["atlas.tool.result_tokens"] > 0
    by_id = {s.get_span_context().span_id: s for s in spans}
    step = by_id[tool.parent.span_id]
    assert step.name.startswith("step ") and step.parent.span_id == agent.context.span_id
    assert tool.context.trace_id == agent.context.trace_id
    assert tool.status.status_code == StatusCode.UNSET
```

Run it, then the whole suite:

```bash
python -m pytest -q tests/integration/test_check_shipment_span.py
make test
```

Expected: `1 passed` for the new file, and `make test` still green (`402 passed` with your test added).

> **Checkpoint 3:** the new test passes, and you have made it fail once on purpose (change the expected tracking id) to see the assertion message.

---

## Step 4: Close the gap: a filterable status

The shipment status lives only inside `gen_ai.tool.call.result`, a JSON string. Add one low-cardinality attribute in `_run_tool`, right after the `search_knowledge_base` block:

```python
                if name == "check_shipment" and ok:   # Lab 2: filterable shipment status
                    tspan.set_attribute("atlas.shipment.status", str(tres.data.get("status")))
```

Six possible values, so it is safe to filter and group on. Do **not** add the tracking id as its own attribute: it is already in the arguments, and high-cardinality values belong in arguments, not in filterable fields (Lecture 5.5).

Now add the test that pins it:

```python
def test_check_shipment_status_is_filterable(client):
    _chat(client, "Where is shipment SHP-4471120?", session_id="lab2-2")
    tool = _by_name(client.exporter.get_finished_spans(), "execute_tool check_shipment")[0]
    assert tool.attributes["atlas.shipment.status"] in {
        "created", "in_transit", "at_hub", "out_for_delivery", "delivered", "exception"
    }
```

Restart the server, repeat the curl from Step 1 and paste the new span under "After" in your notes: it now carries `"atlas.shipment.status": "created"`.

> **Checkpoint 4:** the span carries `atlas.shipment.status`, and the second test passes.

---

## Step 5: The failure path

The mock only calls `check_shipment` when the message contains a valid tracking id (`SHP-` plus six to eight digits), so the failure path is easiest to pin one level down, on the tool itself:

```python
from app.tools import check_shipment, default_context


def test_invalid_tracking_id_is_a_failed_tool_result():
    r = check_shipment(default_context(), "SHP-12")
    assert r.ok is False
    assert json.loads(r.content) == {"error": "invalid_tracking_id", "tracking_id": "SHP-12"}
```

`_run_tool` turns `ok=False` into status `ERROR` with `error.type = invalid_tracking_id` on the span; Lecture 3.6's `test_tool_spans_are_children_of_agent` and the failed-tool handling in `test_spans.py` cover that mapping for every tool.

```bash
python -m pytest -q tests/integration/test_check_shipment_span.py
```

Expected: `3 passed`.

> **Checkpoint 5:** three tests pass and `make test` is still green.

---

## Step 6: See it in a UI

**Online (Langfuse):** with your Langfuse keys in `.env` (loaded automatically), restart and repeat the curl. In Langfuse the tool is an observation of type **tool** named `execute_tool check_shipment`, with **Input** = the arguments and **Output** = the masked result, under a `step 1` span.

**Offline (Ops Console):** stop the server, then `make console STORE=.atlas/spans.sqlite`. On the **Traces** page, type `lab2-a` into "Session id": the waterfall lists `execute_tool check_shipment` under `step 1`, with its status and `atlas.tool.result_tokens` in the table. (Offline server spans have millisecond durations; start the server with `ATLAS_MOCK_LATENCY_SCALE=1` if you want a waterfall with realistic bar lengths.)

Take a screenshot for your notes.

> **Checkpoint 6:** the tool span shows as a tool in a UI.

---

## Stretch goals

1. Add an `add_event` on the tool span when the status is `exception`, with `{"exception_reason": ...}` (`ga.add_event(tspan, "shipment.exception", reason=...)`). Events are timestamped and searchable and add no cardinality.
2. Look at `atlas_tool_calls_total{tool, outcome}` and `atlas_tool_latency_seconds{tool}` on `/metrics` (`curl -s localhost:8000/metrics | grep check_shipment`). Notice what is *not* a label: tracking id, user id.
3. Write a test that the `check_shipment` span's `gen_ai.tool.call.result` never contains an `@`: send a message that puts an email in the question and check the masked arguments.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No `execute_tool check_shipment` span | The message has no valid tracking id, so the mock never calls the tool | Use `SHP-` plus six to eight digits, for example `SHP-4471120` |
| Tool span has no parent (`parent_id: null`) | You wrapped a tool call outside `_run_tool`, or used `start_span` instead of `start_as_current_span` | Revert; every tool call goes through `_run_tool` |
| Two `execute_tool check_shipment` spans per call | You instrumented inside `app/tools.py` too | Instrument in one place only: `_run_tool` |
| `gen_ai.tool.call.result` contains a raw email | Bypassed `ga.set_tool` with `span.set_attribute` | Always go through the `genai_attrs` helpers; they mask |
| Test fails: `status_code == StatusCode.OK` expected UNSET | You called `span.set_status(StatusCode.OK)` on success | Leave success as UNSET; set status only on error |
| `KeyError` on `atlas.shipment.status` | Step 4 change not saved, or the server not restarted for the curl | The test client builds a fresh app, so tests see the change immediately; the curl needs a restart (or `make run`'s `--reload`) |
| Console exporter output interleaves with uvicorn logs | Both write to stdout | `OTEL_EXPORTER=file` writes to `.atlas/spans.jsonl` instead |

---

## Solution notes

The reference for the span itself is `03-code/app/agent.py::_run_tool`; the closest shipped test is `tests/integration/test_spans.py::test_ticket_question_emits_tagged_tool_span`, which pins the same shape for `lookup_ticket`. The lab's three tests and the `atlas.shipment.status` line are the student's work; they are not in the shipped repo. Things graders should check:

- The test asserts the span name, `gen_ai.tool.name`, the `tracking_id` argument, the parent chain (step under agent, same trace) and single instrumentation. Asserting only "a span named check_shipment exists" is the most common weak test.
- The new attribute is low-cardinality (six values) and set only on success.
- The failure path is pinned (`invalid_tracking_id`), and the student can explain how `_run_tool` maps `ok=False` to `ERROR` status.

Why this matters beyond the lab: every cost, latency and quality view in Sections 6 to 9 is a query over span attributes. A tool span that silently changes shape is a step you cannot bill, time or filter. In Incident 2 (Lecture 11.3) the red herring is cleared in one click because retriever spans carry `atlas.retrieval.top_k`; `atlas.shipment.status` gives shipment questions the same kind of handle.
