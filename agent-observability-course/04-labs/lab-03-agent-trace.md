# Lab 3: Trace a Multi-Step Ticket Escalation

| Field | Details |
|---|---|
| **Section / lecture** | Section 5, lecture 5.7 |
| **Time estimate** | 60 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Make Atlas's escalation path answer the six questions from Lecture 5.1 from the trace alone: which step, which model, why, at what cost. Close two small gaps on the shipped trace, pin its shape with an integration test, then read the `loop` scenario's trace and see why step spans are the only place a runaway loop is visible. |
| **You will produce** | A two-line change in `app/agent.py::_loop`, `tests/integration/test_escalation_trace.py`, and `notes/lab-03.md` with one escalation trace and one loop trace |

---

## Prerequisites

- Labs 1 and 2 complete.
- Lectures 5.1 to 5.6 watched, especially 5.2 (step spans and events) and 5.6 (the loop you can only see in a trace).
- `app/agent.py` (`run`, `_loop`, `_call_model`), `telemetry/genai_attrs.py` and `tests/integration/test_spans.py` open.

## How escalation works in Atlas

Escalation is for sensitive requests only: grievances, harassment, disciplinary, legal, immigration, medical. Tool errors never escalate. The flow in `_loop`:

1. Step 1 calls `gpt-4.1-mini`. For a sensitive request the model answers with the `[ESCALATE]` marker instead of a tool call.
2. `_loop` sees the marker, adds an `escalation` **span event** on the agent span (`to_model`, `reason`), and calls the escalation model, `gpt-4.1`, inside the **same** step span, with an extra system instruction to offer a confidential HR ticket.
3. The answer comes from `gpt-4.1`; the request's outcome is `escalated` and the agent span gets `atlas.escalated = true`.

Each model call is its own `chat <model>` generation span with its own usage and `atlas.cost_usd`, priced at that model's rate. That is what makes "why did this answer cost five times more?" answerable from a trace.

---

## Step 1: Record the escalation trace

Terminal 1:

```bash
OFFLINE=1 OTEL_EXPORTER=console make run
```

Terminal 2:

```bash
curl -s http://localhost:8000/chat -H 'Content-Type: application/json' \
  -H 'X-Tenant: hr' -H 'X-User: NW-10433' -H 'X-Session: lab3-esc-1' \
  -d '{"message": "I want to raise a grievance about my manager"}' | python3 -m json.tool
```

Expected response fields (offline, deterministic): `"model": "gpt-4.1"`, `"steps": 1`, `"outcome": "escalated"`, `"intent": "escalation"`, `"escalated": true`, `"cost_usd": 0.0087876`, `"tool_calls": []`, and an answer that offers a confidential HR ticket (P2).

In Terminal 1, the spans for that trace print children first. Written as a tree (attributes abridged):

```text
invoke_agent atlas      atlas.outcome=escalated  atlas.escalated=true  atlas.cost_usd=0.0087876
│                       event: escalation {to_model: gpt-4.1, reason: "model requested human-grade handling"}
├── guardrail injection_check
└── step 1              atlas.context_tokens=2521
    ├── chat gpt-4.1-mini   3,262 → 18 tokens    atlas.cost_usd=0.0013336   atlas.ttft_ms=462.3
    └── chat gpt-4.1        3,287 → 110 tokens   atlas.cost_usd=0.007454    atlas.ttft_ms=873.7
```

Paste it into `notes/lab-03.md` and answer the six questions from Lecture 5.1 against it: why did it call that model, with what, what came back, how many steps, where did the tokens go, where did the time go.

> **Checkpoint 1:** you can point at the escalation event, the two generations, and the cost of each.

---

## Step 2: Find the two gaps

Read the tree as someone who wasn't there:

1. The event says where the call went (`to_model`) but not where it came **from**. If you change the default model next quarter, old traces become ambiguous.
2. The step span doesn't say it escalated. In Langfuse or the console you can filter generations by model, but you can't filter *steps* that escalated, which is what you want when you ask "how many steps per day hand off to the expensive model?"

Both are one line each in `_loop`.

> **Checkpoint 2:** you can say what each gap costs you when you investigate.

---

## Step 3: Close them

Open `app/agent.py`, find the escalation branch in `_loop` (it starts with `content.startswith(ESCALATE_MARKER)`) and change it to:

```python
                        ga.add_event(
                            root,
                            "escalation",
                            from_model=used_model,                 # Lab 3: where the call came from
                            to_model=s.escalation_model,
                            reason="model requested human-grade handling",
                        )
                        st.set_attribute("atlas.escalated", True)  # Lab 3: filterable on the step
                        result.escalated = True
```

`st` is the `step n` span opened a few lines above, and `used_model` is the model that just returned the marker.

Restart the server, repeat the curl, and check the event now reads `{from_model: gpt-4.1-mini, to_model: gpt-4.1, ...}` and `step 1` carries `atlas.escalated=true`.

> **Checkpoint 3:** both attributes show up in the console output.

---

## Step 4: Pin the shape with a test

Create `tests/integration/test_escalation_trace.py`. The `client` fixture in `tests/integration/conftest.py` runs the app offline with an in-memory exporter (`client.exporter`); `tests/integration/test_spans.py::test_escalation_child_generation` is the shipped pattern this extends.

```python
"""Lab 3: the escalation path answers the six questions from Lecture 5.1."""

HR = {"X-Tenant": "hr", "X-User": "NW-10433", "X-Session": "lab3-esc-1"}


def test_escalation_trace_shape(client):
    r = client.post("/chat", json={"message": "I want to raise a grievance about my manager"}, headers=HR)
    body = r.json()
    assert body["escalated"] is True and body["outcome"] == "escalated" and body["model"] == "gpt-4.1"

    spans = client.exporter.get_finished_spans()
    by_id = {s.get_span_context().span_id: s for s in spans}
    agent = next(s for s in spans if s.name == "invoke_agent atlas")
    gens = [s for s in spans if s.name.startswith("chat ")]

    # one generation per model call, the escalation priced at its own model's rate
    assert [g.attributes["gen_ai.request.model"] for g in gens] == ["gpt-4.1-mini", "gpt-4.1"]
    mini, big = gens
    assert big.attributes["atlas.cost_usd"] > 4 * mini.attributes["atlas.cost_usd"]

    # both generations sit under the same step, under the agent
    for g in gens:
        step = by_id[g.parent.span_id]
        assert step.name == "step 1" and step.parent.span_id == agent.context.span_id

    # the decision is an event on the agent span, with both ends of the hand-off
    events = [e for e in agent.events if e.name == "escalation"]
    assert len(events) == 1
    assert events[0].attributes["to_model"] == "gpt-4.1"
    assert events[0].attributes["from_model"] == "gpt-4.1-mini"      # Step 3
    assert by_id[big.parent.span_id].attributes["atlas.escalated"] is True   # Step 3
    assert agent.attributes["atlas.escalated"] is True
```

Assert on `gen_ai.request.model`, never on the position of a span in the list: that is the most common weak test.

```bash
python -m pytest -q tests/integration/test_escalation_trace.py
make test
```

Expected: `1 passed`, and `make test` still green. Before your Step 3 change, the two lines marked `# Step 3` fail; that is your proof the test pins the new attributes.

> **Checkpoint 4:** the test passes with your change and fails without it.

---

## Step 5: The loop you can only see in a trace

The `loop` scenario makes `lookup_ticket` fail every time, so the model keeps calling it. Run one conversation through it, in process, with the shipped default guard (`ATLAS_MAX_STEPS=6`):

```bash
make loop-demo
```

Expected (offline, deterministic):

```text
loop demo: max_steps=6  max_tool_retries=unlimited  deadline=600s  prompt_cache=0  context_diet=0
step    1  input   3,261 tok  step $0.0014  total $0.0014  model gpt-4.1-mini
step    2  input   3,330 tok  step $0.0014  total $0.0028  model gpt-4.1-mini
...
step    6  input   3,606 tok  step $0.0015  total $0.0086  model gpt-4.1-mini

outcome=step_limit  steps=6  model_calls=6  tool_calls=6  input_tokens=20,601  cached_tokens=0  cost=$0.0086  latency=4.3s  trace_id=…
```

Every step adds 69 input tokens: the failed tool result rides along in the history. The trace has six `step n` spans, each with one generation and one failed `execute_tool lookup_ticket` span (status `ERROR`), and a `step_limit_reached` event on the agent span. Open it on the Ops Console's **Traces** page (`make console`, paste the `trace_id`) or read it in Langfuse.

Now the Lecture 5.6 fix: stop retrying a tool after two failures.

```bash
ATLAS_MAX_TOOL_RETRIES=2 make loop-demo
```

```text
outcome=tool_error  steps=3  model_calls=3  tool_calls=3  input_tokens=9,990  cached_tokens=0  cost=$0.0042  latency=2.0s  trace_id=…
```

Three steps, half the cost, and a `tool_retries_exhausted` event instead of `step_limit_reached`. Write both outcomes into your notes and answer: from the request's latency or cost alone, could you have told these two runs apart from a normal two-step answer? (No: both stay under four seconds and a cent. Only the step spans and events show the loop.)

> **Checkpoint 5:** you have both loop traces in your notes and can name the event each one ends with.

---

## Step 6: Optional online confirmation

With Langfuse keys in `.env` (loaded automatically), repeat Step 1. In Langfuse the trace shows the agent observation, `step 1` and the two generations, and the generations' models and costs. The `escalation` event is an OpenTelemetry span event on the agent span; check where your Langfuse version displays span events (verify against the current UI). For an event *observation* inside the step instead, compare with the Langfuse-native layer: `python -m app.langfuse_native "I want to raise a grievance about my manager" --tenant hr`.

---

## Stretch goals

1. Time to first token: the escalated answer's TTFT on the agent span (`atlas.ttft_ms`, 1,481.6 ms in Step 1's test run) is larger than either generation's own TTFT (462.3 and 873.7 ms). Explain why from the tree.
2. Add a test that a non-sensitive question ("How many days of annual leave do I get?") produces **no** `escalation` event and only `gpt-4.1-mini` generations.
3. Write the `ATLAS_MAX_TOOL_RETRIES=2` loop as a test: `tests/unit/test_agent.py` already has the pattern for running `AtlasAgent` with `scenario="loop"`; compare yours with the shipped `test_loop_scenario_stops_early` in `tests/integration/test_spans.py`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `"escalated": false` | The question isn't classified as sensitive | Use a grievance, harassment, disciplinary or legal question; ticket and policy questions never escalate |
| Only one generation | Router mode is on (`ATLAS_ROUTER_MODE=1`), which sends sensitive intents straight to `gpt-4.1` | Run with `ROUTER=0` (the Makefile default) for this lab |
| `NameError: st` after Step 3 | You edited the wrong block | The escalation branch is inside `with self.tracer.start_as_current_span(f"step {step}") as st:` |
| Test fails on `from_model` | Step 3 change not saved | Save and rerun; the test client builds a fresh app every test |
| `make loop-demo` runs 549 steps | `ATLAS_MAX_STEPS=0` is set in your shell | `unset ATLAS_MAX_STEPS`; 0 means unlimited (the guards-off run from Lecture 1.1) |

---

## Solution notes

The shipped trace already answers most of the six questions: one generation per model call, each priced at its own model's rate, under the step that made it, and an `escalation` event on the agent span. The lab's two additions (`from_model` on the event, `atlas.escalated` on the step span) and its test are the student's work; they are not in the shipped `app/agent.py`. Graders check:

- The test asserts by model name, the cost ratio, the parent chain (both generations under `step 1`, under the agent) and the event's attributes.
- The test fails without the Step 3 change.
- The loop notes name `step_limit_reached` (default guard, 6 steps, $0.0086) and `tool_retries_exhausted` (`ATLAS_MAX_TOOL_RETRIES=2`, 3 steps, $0.0042), and explain that neither is visible from request latency or cost alone.

Reference values: escalation request $0.0087876 (gpt-4.1-mini $0.0013336, gpt-4.1 $0.007454, a 5.6x ratio); loop with the default guard 20,601 input tokens; with `ATLAS_MAX_TOOL_RETRIES=2` 9,990.
