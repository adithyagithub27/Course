# Lab 2: Instrument a New Tool End to End

| Field | Details |
|---|---|
| **Section / lecture** | Section 3, lecture 3.7 |
| **Time estimate** | 60 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Give the `check_shipment` tool a proper OpenTelemetry span with GenAI semantic-convention attributes, make sure it is a child of the agent span, redact its result, and prove all of that with an integration test that uses the in-memory exporter. |
| **You will produce** | A modified `app/tools.py`, a new test in `tests/integration/test_check_shipment_span.py`, and `notes/lab-02.md` with before/after console output |

---

## Prerequisites

- Lab 1 complete (`make test` green, you can read a span tree).
- Lectures 3.1 to 3.6 watched, especially 3.4 (tagging LLM, tool and agent spans) and 3.6 (orphan spans and double counting).
- `app/tools.py`, `telemetry/genai_attrs.py` and `tests/integration/test_spans.py` open in your editor.

## Background

Four of Atlas's five tools (`search_knowledge_base`, `lookup_ticket`, `create_ticket`, `reset_password`) are already instrumented. `check_shipment` was added late and is **not**: it runs, it works, and it is invisible in every trace. When the warehouse tenant asks "where is shipment SHP-88213?", the trace shows a generation, a mystery gap of 300 ms, and another generation. This lab closes the gap.

The conventions you will apply (incubating in `opentelemetry-semantic-conventions` 0.66b0; names may change, which is why we always go through `telemetry/genai_attrs.py` rather than typing strings):

| Attribute | Value for a tool span |
|---|---|
| span name | `execute_tool check_shipment` |
| `gen_ai.operation.name` | `execute_tool` |
| `gen_ai.tool.name` | `check_shipment` |
| `gen_ai.tool.call.id` | the `tool_call_id` from the model response |
| `gen_ai.tool.call.arguments` | JSON string of the arguments (redacted) |
| `gen_ai.tool.call.result` | JSON string of the result (redacted, truncated) |
| `gen_ai.agent.name` | `atlas` |
| span status | `ERROR` with the exception recorded when the tool fails |

---

## Step 1: See the gap

Start the server with the console exporter and ask a shipment question:

```bash
OFFLINE=1 OTEL_EXPORTER=console make run
```

```bash
curl -s http://localhost:8000/chat -H 'Content-Type: application/json' \
  -H 'X-Tenant: warehouse' -H 'X-User-Id: NW-22011' -H 'X-Session-Id: lab2-a' \
  -d '{"message": "Where is shipment SHP-88213?"}' | python3 -m json.tool
```

In the server terminal, list the span names for that trace. A quick way:

```bash
uv run python -m telemetry.local_store spans --last 1 --names
```

Expected (before):

```text
atlas.chat
├── openai.chat gpt-4.1-mini        (tool_calls: check_shipment)
└── openai.chat gpt-4.1-mini        (final answer)
```

Two generations, no tool span. The 300 ms between them is the shipment lookup running untraced. Paste this into `notes/lab-02.md` under "Before".

> **Checkpoint 1:** you can show a trace where a tool ran but no tool span exists.

---

## Step 2: Look at how an instrumented tool does it

Open `app/tools.py` and find `lookup_ticket`. The pattern is:

```python
from opentelemetry import trace
from telemetry import genai_attrs as ga

tracer = trace.get_tracer("atlas.tools")

def lookup_ticket(ticket_id: str, *, tool_call_id: str = "") -> dict:
    with tracer.start_as_current_span(ga.tool_span_name("lookup_ticket")) as span:
        ga.set_tool_attributes(span, name="lookup_ticket", call_id=tool_call_id,
                               arguments={"ticket_id": ticket_id})
        try:
            result = _ticket_store.get(ticket_id)
        except TicketNotFound as exc:
            ga.record_tool_error(span, exc)      # sets status ERROR + records exception
            raise
        ga.set_tool_result(span, result)          # redacts via northwind.pii, truncates to 400 tokens
        return result
```

Three things to notice, because they are the three mistakes from lecture 3.6:

1. `start_as_current_span` (not `start_span`) makes the tool span the current context, so anything inside it becomes a child and the span itself attaches to whatever is current: the agent span.
2. Arguments and result go through `set_tool_attributes` / `set_tool_result`, which call `northwind.pii.mask_attributes` and truncate. Never `json.dumps(result)` straight onto a span.
3. Errors set the span status to `ERROR` and record the exception before re-raising. A tool that fails silently is worse than one that is not traced at all.

> **Checkpoint 2:** you can explain, in one sentence each, why `start_as_current_span`, masking and error status are all present.

---

## Step 3: Instrument `check_shipment`

Find `check_shipment` in `app/tools.py`. It currently looks roughly like:

```python
def check_shipment(shipment_id: str, *, tool_call_id: str = "") -> dict:
    return _shipments.status(shipment_id)
```

Replace it with:

```python
def check_shipment(shipment_id: str, *, tool_call_id: str = "") -> dict:
    """Return the current status, location and ETA of a Northwind shipment."""
    with tracer.start_as_current_span(ga.tool_span_name("check_shipment")) as span:
        ga.set_tool_attributes(span, name="check_shipment", call_id=tool_call_id,
                               arguments={"shipment_id": shipment_id})
        try:
            result = _shipments.status(shipment_id)
        except ShipmentNotFound as exc:
            ga.record_tool_error(span, exc)
            raise
        span.set_attribute("northwind.shipment.status", result["status"])
        ga.set_tool_result(span, result)
        return result
```

The extra `northwind.shipment.status` attribute is a low-cardinality domain attribute (`in_transit`, `delivered`, `delayed`, `unknown`), useful for filtering in Langfuse. Do **not** add the shipment id as its own attribute: it is already in the arguments, and high-cardinality attributes belong in arguments, not in filterable fields.

Restart the server and repeat the curl from Step 1. Expected (after):

```text
atlas.chat
├── openai.chat gpt-4.1-mini        (tool_calls: check_shipment)
├── execute_tool check_shipment     312 ms   gen_ai.tool.name=check_shipment  northwind.shipment.status=in_transit
└── openai.chat gpt-4.1-mini        (final answer)
```

Print the full tool span and check the attributes:

```bash
uv run python -m telemetry.local_store spans --last 1 --name "execute_tool check_shipment"
```

```json
"attributes": {
    "gen_ai.operation.name": "execute_tool",
    "gen_ai.tool.name": "check_shipment",
    "gen_ai.tool.call.id": "call_7Yx2...",
    "gen_ai.tool.call.arguments": "{\"shipment_id\": \"SHP-88213\"}",
    "gen_ai.tool.call.result": "{\"shipment_id\": \"SHP-88213\", \"status\": \"in_transit\", \"location\": \"Rotterdam hub\", \"eta\": \"2026-09-23\", \"consignee_email\": \"[EMAIL]\"}",
    "gen_ai.agent.name": "atlas",
    "northwind.shipment.status": "in_transit"
}
```

Note `consignee_email` came back as `[EMAIL]`: `set_tool_result` masked it.

> **Checkpoint 3:** the tool span exists, is a child of `atlas.chat`, and its result is masked.

---

## Step 4: Break it on purpose (orphan span)

Temporarily change `start_as_current_span` to `tracer.start_span(...)` (and add `span.end()` before `return`). Restart, repeat the curl, and list spans:

```text
atlas.chat
├── openai.chat gpt-4.1-mini
└── openai.chat gpt-4.1-mini
execute_tool check_shipment          <- separate trace! different trace_id
```

`start_span` creates a span but does not make it current, and because the tool span is created inside the agent span it *does* get the right parent... unless the agent loop runs tools in a thread pool or `asyncio.create_task` without copying context, which Atlas does for parallel tool calls. Check `app/agent.py::_run_tools`: it uses `contextvars.copy_context().run(...)` so the tool inherits the agent span. Remove that wrapper for a moment and you get the orphan above even with `start_as_current_span`.

Revert both changes. Write two lines in your notes: which change produced the orphan and why.

> **Checkpoint 4:** you produced and then fixed an orphan span.

---

## Step 5: Write the test

Create `tests/integration/test_check_shipment_span.py`. The fixture `spans` (in `tests/integration/conftest.py`) starts the app in offline mode with an `InMemorySpanExporter` and returns the finished spans after the request.

```python
import json

from opentelemetry.trace import StatusCode

from tests.integration.conftest import chat, finished_spans, span_by_name


def test_check_shipment_has_tool_span(app_client, span_exporter):
    chat(app_client, "Where is shipment SHP-88213?", tenant="warehouse", session="t-ship-1")
    spans = finished_spans(span_exporter)

    tool = span_by_name(spans, "execute_tool check_shipment")
    agent = span_by_name(spans, "atlas.chat")

    assert tool.parent.span_id == agent.context.span_id, "tool span must be a child of the agent span"
    assert tool.context.trace_id == agent.context.trace_id
    attrs = tool.attributes
    assert attrs["gen_ai.operation.name"] == "execute_tool"
    assert attrs["gen_ai.tool.name"] == "check_shipment"
    assert attrs["gen_ai.agent.name"] == "atlas"
    assert json.loads(attrs["gen_ai.tool.call.arguments"]) == {"shipment_id": "SHP-88213"}
    result = json.loads(attrs["gen_ai.tool.call.result"])
    assert result["status"] == "in_transit"
    assert "@" not in attrs["gen_ai.tool.call.result"], "consignee email must be masked"
    assert attrs["northwind.shipment.status"] == "in_transit"
    assert tool.status.status_code == StatusCode.UNSET


def test_check_shipment_unknown_id_sets_error_status(app_client, span_exporter):
    chat(app_client, "Where is shipment SHP-00000?", tenant="warehouse", session="t-ship-2")
    spans = finished_spans(span_exporter)

    tool = span_by_name(spans, "execute_tool check_shipment")
    assert tool.status.status_code == StatusCode.ERROR
    events = [e.name for e in tool.events]
    assert "exception" in events
    # the agent should still answer (it tells the user the id was not found)
    agent = span_by_name(spans, "atlas.chat")
    assert agent.status.status_code == StatusCode.UNSET


def test_exactly_one_tool_span_per_call(app_client, span_exporter):
    """Guards against double instrumentation (lecture 3.6, mistake 3)."""
    chat(app_client, "Where is shipment SHP-88213?", tenant="warehouse", session="t-ship-3")
    spans = finished_spans(span_exporter)
    tool_spans = [s for s in spans if s.name == "execute_tool check_shipment"]
    assert len(tool_spans) == 1
```

Run only these tests first, then the whole suite:

```bash
uv run pytest tests/integration/test_check_shipment_span.py -v
make test
```

Expected:

```text
tests/integration/test_check_shipment_span.py::test_check_shipment_has_tool_span PASSED
tests/integration/test_check_shipment_span.py::test_check_shipment_unknown_id_sets_error_status PASSED
tests/integration/test_check_shipment_span.py::test_exactly_one_tool_span_per_call PASSED
```

The mock LLM is scenario-aware: `SHP-00000` is a fixture id that `_shipments.status` always rejects with `ShipmentNotFound`, which is why the error test is deterministic offline.

> **Checkpoint 5:** three new tests pass and `make test` is still green.

---

## Step 6: Confirm in Langfuse (online) or the Ops Console (offline)

**Online:** set `OTEL_EXPORTER=langfuse`, restart, run the curl. In Langfuse the tool appears as an observation of type **tool** named `execute_tool check_shipment` with **Input** = the arguments and **Output** = the masked result. Langfuse maps `gen_ai.tool.*` attributes to its tool observation type automatically because the Langfuse SDK v4 sits on OpenTelemetry (lecture 4.1).

**Offline:** `make console` → **Trace explorer** → newest trace. The tool row is coloured as a tool and shows the same input/output.

Take a screenshot for your notes.

> **Checkpoint 6:** the tool span shows as a tool observation in a UI.

---

## Stretch goal

1. Add an `add_event` on the tool span when the shipment is `delayed`, with attributes `{"delay_days": n}`. Events are cheap, timestamped and searchable, and they do not increase span cardinality.
2. Record the tool's duration as a Prometheus histogram observation in `telemetry/metrics.py` (`atlas_tool_duration_seconds{tool="check_shipment", status="ok|error"}`). Notice what you may *not* put in the label set: shipment id, user id, tenant id is fine (four values).
3. Write a test that asserts the tool result attribute is at most `settings.tool_result_token_budget` tokens long even when `_shipments.status` returns a 6 KB manifest. Use the `context_bloat` scenario: `ATLAS_SCENARIO=context_bloat` makes the mock return oversized results.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Tool span has no parent (`parent_id: None`) | Span created outside the agent context, or context not propagated into a thread/task | Use `start_as_current_span`; check `_run_tools` copies context (`contextvars.copy_context()`) |
| Two `execute_tool check_shipment` spans per call | Instrumented both in `tools.py` and in the agent loop's tool dispatcher | Instrument in one place only; the dispatcher in `agent.py` should not wrap tools that trace themselves |
| `gen_ai.tool.call.result` contains a raw email | Bypassed `set_tool_result` with `span.set_attribute` | Always go through `genai_attrs` helpers; they mask and truncate |
| `AttributeError: module 'gen_ai_attributes' has no attribute GEN_AI_TOOL_CALL_ARGUMENTS` | Older `opentelemetry-semantic-conventions` | `uv sync` to get `>=0.66b0`; the tool attributes are incubating and only exist from 0.56 onwards |
| Test fails: `status_code == StatusCode.OK` expected UNSET | You called `span.set_status(StatusCode.OK)` on success | Leave success as UNSET; OTel convention is to set status only on error (or explicitly OK by the application owner, which we do not do) |
| `span_by_name` raises `KeyError` | Span name typo or spans not flushed | Names are `execute_tool <tool>`; `finished_spans()` calls `force_flush()` for you, so check the name |
| Console exporter output interleaves with uvicorn logs | Both write to stdout | `OTEL_EXPORTER=file` writes to `.atlas/spans.jsonl` instead; `jq` it |

---

## Solution notes

The complete instrumented tool is in `03-code/app/tools.py` and the reference test is `03-code/tests/integration/test_spans.py::TestCheckShipment` (the lab test is a subset of it). Things graders and you should check:

- The span is created with `start_as_current_span` and is a child of `atlas.chat` in the same trace.
- Attributes are set only through `genai_attrs` helpers; the result is masked (`[EMAIL]`) and truncated to `tool_result_token_budget`.
- Errors record the exception and set `ERROR` status, and the agent span does **not** inherit that error: a failed tool is a normal event for an agent, and the agent's status reflects whether the *request* failed.
- The test asserts parentage, attributes, masking, error status and single-instrumentation. Asserting only "a span named check_shipment exists" is the most common weak test.

Why this matters beyond the lab: every cost, latency and quality view in Sections 6 to 9 is a query over span attributes. A tool without a span is a step you cannot bill, cannot time and cannot blame. In Incident 2 (lecture 11.3) the latency regression is only visible because tool spans exist to compare against.
