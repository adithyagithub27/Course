# Lab 3: Trace a Multi-Step Ticket Escalation

| Field | Details |
|---|---|
| **Section / lecture** | Section 5, lecture 5.7 |
| **Time estimate** | 75 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Make Atlas's escalation path fully legible in a trace: one span per agent step, the escalation to `gpt-4.1` as a child generation with its own usage and cost, the step limit as a span event, tool arguments and results redacted, and a test that pins the whole shape down. Then watch the `loop` scenario and see why step spans are the only place a runaway loop is visible. |
| **You will produce** | Changes to `app/agent.py`, a test in `tests/integration/test_escalation_trace.py`, and `notes/lab-03.md` with a trace waterfall (screenshot or text) of one escalation and one loop |

---

## Prerequisites

- Labs 1 and 2 complete.
- Lectures 5.1 to 5.6 watched, especially 5.2 (step spans) and 5.6 (the loop you can only see in a trace).
- `app/agent.py`, `telemetry/genai_attrs.py`, `telemetry/langfuse_setup.py` open.

## The scenario

An HR employee asks: *"My payslip for August is missing and TCK-4471 has been open for two weeks, can you escalate it?"* Atlas has to:

1. Call `lookup_ticket("TCK-4471")`: it exists, priority `P3`, no update for 14 days.
2. Decide the case is complex (a stale ticket plus a payroll issue), and **escalate the model** from `gpt-4.1-mini` to `gpt-4.1` for the reasoning step.
3. Call `create_ticket(...)` to open a `P2` escalation linked to TCK-4471.
4. Answer the user.

That is at least three model steps and two tool calls. Today's trace shows four generations and two tool spans in a flat list under `atlas.chat`, with no way to tell which generation belonged to which step, or that step 2 used the expensive model.

---

## Step 1: Record the "before" waterfall

```bash
OFFLINE=1 OTEL_EXPORTER=console make run
```

```bash
curl -s http://localhost:8000/chat -H 'Content-Type: application/json' \
  -H 'X-Tenant: hr' -H 'X-User-Id: NW-10433' -H 'X-Session-Id: lab3-esc-1' \
  -d '{"message": "My payslip for August is missing and TCK-4471 has been open for two weeks, can you escalate it?"}' \
  | python3 -m json.tool
```

Expected response fields: `"steps": 3`, `"escalated": true`, `"model_used": ["gpt-4.1-mini", "gpt-4.1", "gpt-4.1-mini"]`, `"cost_usd"` around `0.0061` (the gpt-4.1 step dominates).

```bash
uv run python -m telemetry.local_store spans --last 1 --tree
```

Before:

```text
atlas.chat  (hr / NW-10433 / lab3-esc-1)                                 2,940 ms  $0.00612
├── openai.chat gpt-4.1-mini        1,210 → 41 tok                         620 ms
├── execute_tool lookup_ticket                                              48 ms
├── openai.chat gpt-4.1             1,690 → 212 tok                       1,480 ms
├── execute_tool create_ticket                                              61 ms
└── openai.chat gpt-4.1-mini        2,010 → 96 tok                         690 ms
```

Flat. Which generation decided to escalate? Why? You cannot tell.

> **Checkpoint 1:** you have the flat waterfall in your notes.

---

## Step 2: Add step spans

Open `app/agent.py` and find the tool loop in `AtlasAgent.run` (roughly):

```python
for step in range(1, self.settings.max_steps + 1):
    response = self._call_model(messages, model=self._pick_model(step, messages))
    if not response.tool_calls:
        break
    messages += self._run_tools(response.tool_calls)
```

Wrap each iteration in a step span and annotate it:

```python
from opentelemetry import trace
from telemetry import genai_attrs as ga

tracer = trace.get_tracer("atlas.agent")

for step in range(1, self.settings.max_steps + 1):
    with tracer.start_as_current_span(f"atlas.step {step}") as step_span:
        step_span.set_attribute("northwind.step", step)
        step_span.set_attribute("northwind.context_tokens", self.tokens.count_messages(messages))

        model = self._pick_model(step, messages)
        if model != self.settings.model:
            step_span.set_attribute("northwind.escalated", True)
            step_span.set_attribute("northwind.escalation_reason", self._escalation_reason)

        response = self._call_model(messages, model=model)     # creates the generation span (child)
        step_span.set_attribute("northwind.tool_calls", len(response.tool_calls or []))

        if not response.tool_calls:
            break
        messages += self._run_tools(response.tool_calls)        # creates tool spans (children)
else:
    # loop exhausted without a final answer
    current = trace.get_current_span()
    current.add_event("step_limit_reached", {"max_steps": self.settings.max_steps,
                                            "context_tokens": self.tokens.count_messages(messages)})
    current.set_status(trace.StatusCode.ERROR, "step limit reached")
    answer = self._graceful_stop_message()
```

Two details worth getting right:

- `northwind.context_tokens` on every step is what makes context growth visible per step (lecture 6.5 and Incident 1).
- The step-limit event goes on the **agent** span, not on a step span, because it describes the request outcome. It is an event, not an attribute, because it has a timestamp and happens at most once.

Restart and re-run the curl. After:

```text
atlas.chat                                                                  2,960 ms  $0.00612
├── atlas.step 1   context_tokens=1,180  tool_calls=1                        690 ms
│   ├── openai.chat gpt-4.1-mini        1,210 → 41 tok                       620 ms
│   └── execute_tool lookup_ticket                                            48 ms
├── atlas.step 2   context_tokens=1,650  escalated=true  reason=stale_ticket 1,560 ms
│   ├── openai.chat gpt-4.1             1,690 → 212 tok   $0.00508           1,480 ms
│   └── execute_tool create_ticket                                            61 ms
└── atlas.step 3   context_tokens=1,990  tool_calls=0                         700 ms
    └── openai.chat gpt-4.1-mini        2,010 → 96 tok                        690 ms
```

Now the waterfall answers all six questions from lecture 5.1: which tool, with what, what came back, how many steps, where the tokens went (context grows 1,180 → 1,650 → 1,990), where the time went (step 2, the escalation).

> **Checkpoint 2:** three step spans, the escalation flagged on step 2, the gpt-4.1 generation nested under it.

---

## Step 3: Make the escalation generation carry its own cost

Click (or print) the `openai.chat gpt-4.1` span. It must have its own `gen_ai.request.model = gpt-4.1`, its own usage and its own `northwind.cost_usd`. If your `_call_model` sets the model attribute from `self.settings.model` instead of the `model` argument, the escalation is billed as a mini call, which understates cost by roughly 5×. Check:

```bash
uv run python -m telemetry.local_store spans --last 1 --name "openai.chat gpt-4.1" \
  | jq '.attributes | {model: ."gen_ai.request.model", inp: ."gen_ai.usage.input_tokens", out: ."gen_ai.usage.output_tokens", cost: ."northwind.cost_usd"}'
```

Expected:

```json
{"model": "gpt-4.1", "inp": 1690, "out": 212, "cost": 0.005076}
```

Sanity check by hand: 1,690 × $2.00/M + 212 × $8.00/M = $0.00338 + $0.001696 = $0.005076. If you are using the Langfuse path, also call `update_current_generation(model=model, usage_details=..., cost_details=...)` inside `_call_model` so Langfuse's cost view agrees with yours (lecture 4.2).

> **Checkpoint 3:** the escalation generation reports `gpt-4.1` and a cost about 5× the mini steps.

---

## Step 4: Redaction on the escalation path

`create_ticket` receives the user's description, which in HR cases often contains an employee id and sometimes a bank detail. Print the tool span:

```bash
uv run python -m telemetry.local_store spans --last 1 --name "execute_tool create_ticket" | jq '.attributes."gen_ai.tool.call.arguments"'
```

Expected: the arguments contain `"employee_id": "[EMPLOYEE_ID]"` and no raw `NW-` id. If you see `NW-10433`, the tool bypasses `ga.set_tool_attributes`. Fix it the same way as in Lab 2.

> **Checkpoint 4:** no raw employee id in any span of the escalation trace.

---

## Step 5: The loop you can only see in a trace

Stop the server and run one request with the `loop` scenario. The mock LLM keeps calling `lookup_ticket` with a malformed id and never produces a final answer:

```bash
OFFLINE=1 OTEL_EXPORTER=console ATLAS_SCENARIO=loop ATLAS_MAX_STEPS=6 make run
```

```bash
curl -s http://localhost:8000/chat -H 'Content-Type: application/json' \
  -H 'X-Tenant: finance' -H 'X-User-Id: NW-33091' -H 'X-Session-Id: lab3-loop-1' \
  -d '{"message": "What is the status of ticket 4471?"}' | python3 -m json.tool
```

Expected response: `"steps": 6`, `"stopped_reason": "step_limit"`, answer is the graceful stop message ("I was not able to complete this; I have logged it for the helpdesk team."). Cost around `$0.0092` for a question that should cost `$0.0006`.

```bash
uv run python -m telemetry.local_store spans --last 1 --tree
```

```text
atlas.chat   status=ERROR "step limit reached"   event: step_limit_reached{max_steps=6, context_tokens=6,410}
├── atlas.step 1   context_tokens=1,150   ├── gpt-4.1-mini 1,180→38   ├── lookup_ticket ERROR TicketNotFound("4471")
├── atlas.step 2   context_tokens=1,720   ├── gpt-4.1-mini 1,750→39   ├── lookup_ticket ERROR
├── atlas.step 3   context_tokens=2,290   ...
├── atlas.step 4   context_tokens=2,860
├── atlas.step 5   context_tokens=3,430
└── atlas.step 6   context_tokens=4,000
```

Read it like an SRE: every step adds about 570 tokens (the previous error plus the model's retry), so input tokens grow linearly per step and total cost grows quadratically in the number of steps. Without `ATLAS_MAX_STEPS` this is the $4,000 weekend from lecture 1.1. Without step spans it is "the request was slow and expensive" with no explanation.

Now run the same request with `ATLAS_MAX_STEPS=3` and compare cost. Then write down the number of steps at which the cumulative cost of the loop exceeds the cost of a successful escalation (Step 1): the answer is in the solution notes.

> **Checkpoint 5:** you can point at the step where context crossed 3,000 tokens and at the `step_limit_reached` event.

---

## Step 6: Pin it down with a test

Create `tests/integration/test_escalation_trace.py`:

```python
import json

from opentelemetry.trace import StatusCode

from tests.integration.conftest import chat, children_of, finished_spans, span_by_name

ESCALATION_QUESTION = (
    "My payslip for August is missing and TCK-4471 has been open for two weeks, can you escalate it?"
)


def test_escalation_trace_shape(app_client, span_exporter):
    body = chat(app_client, ESCALATION_QUESTION, tenant="hr", user="NW-10433", session="t-esc-1")
    assert body["escalated"] is True
    spans = finished_spans(span_exporter)

    agent = span_by_name(spans, "atlas.chat")
    steps = sorted((s for s in spans if s.name.startswith("atlas.step ")),
                   key=lambda s: s.attributes["northwind.step"])
    assert [s.attributes["northwind.step"] for s in steps] == [1, 2, 3]
    assert all(s.parent.span_id == agent.context.span_id for s in steps)

    # context grows monotonically step to step
    ctx = [s.attributes["northwind.context_tokens"] for s in steps]
    assert ctx == sorted(ctx) and ctx[0] < ctx[-1]

    # escalation happens exactly once, on step 2, and the expensive generation is its child
    escalated = [s for s in steps if s.attributes.get("northwind.escalated")]
    assert len(escalated) == 1 and escalated[0].attributes["northwind.step"] == 2
    gens = [c for c in children_of(spans, escalated[0]) if c.attributes.get("gen_ai.operation.name") == "chat"]
    assert len(gens) == 1
    big = gens[0]
    assert big.attributes["gen_ai.request.model"] == "gpt-4.1"
    assert big.attributes["gen_ai.usage.input_tokens"] > 0
    assert big.attributes["northwind.cost_usd"] > 0.003   # gpt-4.1 pricing, not mini

    # tools sit under their step, not directly under the agent
    lookup = span_by_name(spans, "execute_tool lookup_ticket")
    create = span_by_name(spans, "execute_tool create_ticket")
    assert lookup.parent.span_id == steps[0].context.span_id
    assert create.parent.span_id == steps[1].context.span_id

    # redaction on the escalation path
    assert "NW-" not in create.attributes["gen_ai.tool.call.arguments"]
    assert json.loads(create.attributes["gen_ai.tool.call.arguments"])["linked_ticket"] == "TCK-4471"

    assert agent.status.status_code == StatusCode.UNSET
    assert "step_limit_reached" not in [e.name for e in agent.events]


def test_loop_hits_step_limit_and_is_visible(app_client_factory, span_exporter):
    client = app_client_factory(scenario="loop", max_steps=4)
    body = chat(client, "What is the status of ticket 4471?", tenant="finance", session="t-loop-1")
    assert body["steps"] == 4 and body["stopped_reason"] == "step_limit"
    spans = finished_spans(span_exporter)

    agent = span_by_name(spans, "atlas.chat")
    assert agent.status.status_code == StatusCode.ERROR
    event = next(e for e in agent.events if e.name == "step_limit_reached")
    assert event.attributes["max_steps"] == 4

    steps = [s for s in spans if s.name.startswith("atlas.step ")]
    assert len(steps) == 4
    tool_errors = [s for s in spans if s.name == "execute_tool lookup_ticket"
                   and s.status.status_code == StatusCode.ERROR]
    assert len(tool_errors) == 4
```

```bash
uv run pytest tests/integration/test_escalation_trace.py -v && make test
```

Expected: both tests `PASSED`, full suite still green.

> **Checkpoint 6:** the trace shape is enforced by a test; if someone flattens the waterfall again, CI catches it.

---

## Step 7: Optional online confirmation

Set `OTEL_EXPORTER=langfuse`, restart, replay the escalation request. In Langfuse the step spans appear as **chain**-type observations (Langfuse maps generic spans to spans; to make them chains explicitly, use `@observe(as_type="chain")` or `start_as_current_observation(as_type="chain")` from `telemetry/langfuse_setup.py`). The gpt-4.1 generation shows its own cost; the trace total should be about $0.0061. Screenshot the waterfall for your notes.

---

## Stretch goal

1. Add `northwind.step_latency_ms` and compute, from the local store, the p95 latency of step 2 across a replayed day (`OFFLINE=1 make replay`, then a SQL query against `.atlas/spans.sqlite`). Escalated steps should be the slow tail.
2. Change `_pick_model` so escalation also fires when `context_tokens > 2,500`. Re-run the loop scenario: what happens to cost? (It gets much worse: the loop now escalates to the expensive model. This is exactly what Incident 4 in Project 2 looks like, so remember the feeling.)
3. Emit `gen_ai.client.token.usage` as an OTel metric in addition to the span attribute, with attributes `gen_ai.request.model` and `gen_ai.token.type` (input/output) only.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Steps appear but generations are still direct children of `atlas.chat` | `_call_model` is called before entering the step span, or uses a stored parent context | Move the call inside the `with` block; do not pass an explicit `context=` |
| Only one `atlas.step` span for a 3-step request | Span created outside the `for` loop | The `with` must be inside the loop body |
| Escalation cost equals mini cost | Model attribute set from settings, not from the `model` argument | Set `gen_ai.request.model` and compute cost from the model actually called; check `gen_ai.response.model` too |
| `step_limit_reached` event missing in the loop test | Event added on the step span, or `for ... else` never reached because you `break` after the last step | Add the event on the agent span; ensure the `else` branch runs when the loop is exhausted |
| Agent status `ERROR` on a normal escalation | You set `ERROR` whenever a tool raised | A tool error is recorded on the tool span; the agent status is about the request outcome |
| Loop test: `stopped_reason` missing from the response | Server response model not updated | Add `stopped_reason: str | None` to `ChatResponse` in `app/server.py` |
| `context_tokens` not monotonic in the test | The context diet (`ATLAS_CONTEXT_DIET=1`) trimmed history between steps | Expected in later sections; for this lab the test fixture sets `context_diet=False` (check `app_client` fixture) |

---

## Solution notes

The reference implementation is `03-code/app/agent.py` (`AtlasAgent.run`, `_pick_model`, `_run_tools`) and the reference tests are `03-code/tests/integration/test_spans.py::TestEscalation` and `::TestLoopScenario`.

What a good solution looks like:

| Element | Reference behaviour |
|---|---|
| Step spans | `atlas.step N`, children of `atlas.chat`, with `northwind.step`, `northwind.context_tokens`, `northwind.tool_calls` |
| Escalation | `northwind.escalated=true` and `northwind.escalation_reason` on the step; the `gpt-4.1` generation is that step's child with its own usage and cost |
| Step limit | `step_limit_reached` event plus `ERROR` status on the agent span; a graceful answer to the user; `stopped_reason="step_limit"` in the response |
| Redaction | All tool arguments and results via `genai_attrs` helpers |
| Test | Asserts shape (parentage), monotonic context growth, single escalation on step 2, model and cost on the big generation, redaction, and the loop's event and error count |

Loop arithmetic (seed 42): steps cost about $0.00058, $0.00081, $0.00104, $0.00127, $0.00150, $0.00173 (each step re-sends a longer context), so the cumulative cost passes the $0.0061 of a *successful* escalation between step 6 and step 7. With `max_steps=6` the loop costs $0.0069, more than the most expensive legitimate request Atlas makes, for zero value. That comparison is the argument for a step limit that you will reuse in Project 1's recommendations.

Key takeaways:

1. Step spans turn "the agent was slow and expensive" into "step 2 escalated because of a stale ticket and cost 83% of the request".
2. The escalation model must carry its own model name and cost on its own generation span, or every cost report in Section 6 is wrong by a factor of five on exactly the requests that matter.
3. Context growth per step is the earliest visible symptom of a loop and of context bloat. Put it on the span.
