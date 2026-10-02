# Section 3: Tracing Fundamentals and the GenAI Semantic Conventions

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈52 min (8 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`; every figure comes from `01-curriculum/numbers-card.md` or from the captured command output quoted in the cue
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15+ (uv.lock 4.16.0) / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating, names may change) / openinference-instrumentation-openai 0.1.61+ (uv.lock 0.1.63); check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only. Code-along lectures are paced below 140 words per minute.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 3.1 | Traces, spans and context in five minutes | SL | 6:00 | ~760 |
| 3.2 | Code-along: manual OpenTelemetry instrumentation of Atlas | SC | 10:00 | ~740 |
| 3.3 | GenAI semantic conventions: naming things so tools understand them | SL | 8:00 | ~790 |
| 3.4 | Code-along: tag every LLM, tool and agent span correctly | SC | 9:00 | ~640 |
| 3.5 | Auto-instrumentation with OpenInference | SC | 6:00 | ~465 |
| 3.6 | Break it: orphan spans, missing context and double counting | DM | 6:00 | ~570 |
| 3.7 | Lab 2: Instrument a new tool end to end | LAB | 4:00 (1:30 video) | ~180 |
| 3.8 | Quiz: Tracing and semantic conventions | QZ | 3:00 (1:00 video) | ~105 |

**API guardrails for this section (do not deviate on screen):** attribute constants come from `opentelemetry.semconv._incubating.attributes.gen_ai_attributes` (imported as `g`), never typed as raw strings in application code. Span names follow the conventions: `invoke_agent atlas`, `chat gpt-4.1-mini`, `execute_tool lookup_ticket`. Atlas's real instrumentation is `telemetry/otel_setup.py` (`configure_tracing`, alias `setup_tracing`) and the setters in `telemetry/genai_attrs.py` (`set_agent`, `set_llm_request`, `set_llm_usage`, `set_cost`, `set_tool`, `set_retrieval`), called from `app/agent.py`. This is the vendor-neutral path Atlas keeps for the rest of the course; Section 12 relies on it. Auto-instrumentation is `OpenAIInstrumentor` from `openinference.instrumentation.openai`, wrapped by `telemetry/openinference_setup.instrument_openai`; never show `opentelemetry-instrumentation-openai-v2` installed, imported or running (it failed to import at verification time). The single "not used" line on slide 1 of 3.5 is the only permitted mention. Say "incubating, names may change" once per lecture that shows a `gen_ai.*` name.

---

## Lecture 3.1 — Traces, spans and context in five minutes

| Field | Value |
|---|---|
| ID | 3.1 |
| Type | SL (slides, with one console beat) |
| Target duration | 6:00 (~760 spoken words, about 5:26 of talking at 140 wpm) |
| Learning objectives | 1. Define trace, span, parent/child, attributes, events and status. 2. Explain context propagation and why a span "knows" its parent. 3. Describe head and tail sampling and when each applies. |
| Prerequisites | Section 2 |
| Files used | Diagram: one Atlas request as a trace (slides 2 and 4); `03-code/console/pages/11_Traces.py` (the Traces page) |

### Script

[AVATAR]
In Lecture 2.3 you looked at a trace and it made sense. Root, children, timings. Now here's the uncomfortable question: how did the model call know it belonged to that agent span? Nobody passed it an ID. [PAUSE] Six words explain the whole thing, and one mechanism makes it work. Six words first.

[SLIDE 1: Six words]
- Trace: everything that happened for one request
- Span: one unit of work with a start and an end
- Parent/child: which span caused which
- Attributes: key-value facts about a span
- Events: timestamped moments inside a span
- Status: OK, ERROR or unset

A trace is everything that happened for one request, identified by one trace ID. A span is one unit of work with a start time and an end time. Spans nest: a parent causes children. Attributes are facts about a span, as key-value pairs. Events are timestamped moments inside a span, like "step limit reached." And status says whether the work succeeded.

[SLIDE 2: One Atlas request as a trace]
Diagram, waterfall of the 2.3 VPN request (simulated timings from the mock). Top bar `invoke_agent atlas` 3.4 s. Under it: `guardrail injection_check` (a sliver), then `step 1` containing `chat gpt-4.1-mini` 0.7 s and `execute_tool search_knowledge_base` (a few ms), then `step 2` containing `chat gpt-4.1-mini` 2.7 s. Trace ID shown at the top right.

Here's the VPN request from 2.3 drawn as a waterfall. One trace. The agent span at the top, three point four seconds. Under it, the guardrail, then two steps, each with a model call, and a search in the first. Time runs left to right. Nesting runs top to bottom. Where did the time go? You can see it instantly: the second model call, the one that wrote the answer.

[SLIDE 3: A span, up close]
```text
name:        chat gpt-4.1-mini
trace_id:    0x1c64ccfc12b2b962a1609e2fefae04ef
span_id:     0x6b18382bc75135bb
parent_id:   0x220b219d682bf398        (the "step 1" span)
attributes:  atlas.step=1, atlas.tenant=ops, atlas.cost_usd=0.0013752, ...
events:      (none)
status:      UNSET
```

Zoom in on one span, exactly as Atlas's console exporter printed it. It has a name. It has the trace ID shared by every span in this request. It has its own span ID and, crucially, a parent ID, here the step-one span. That parent ID is the entire tree. There's no separate tree structure stored anywhere; the backend rebuilds the waterfall from parent IDs. Then attributes, events and status.

[SCREEN: Ops Console (`make console`, on the day replayed in 2.4) → Traces page. In "Or one of the ten most expensive conversations" pick `s07-00666`. The waterfall and the table below it appear: `invoke_agent atlas` (3,264.7 ms), `guardrail injection_check`, `step 1`, `chat gpt-4.1-mini` (765.0 ms), `execute_tool search_knowledge_base` (28.1 ms), `step 2`, `chat gpt-4.1-mini` (2,470.8 ms), each with its kind, status, start and duration.]

You can see this on your own machine. Open the console's Traces page on the day you replayed and pick the most expensive conversation. Seven spans, one per row, indented by parent. Every row is one unit of work with a start and an end, and the same shape as the VPN request.

[SLIDE 4: Context propagation]
Diagram: a stack of boxes labelled "current context". Step 1: empty. Step 2: `invoke_agent atlas` is pushed; it's the current span. Step 3: `step 1` starts, reads the current span, sets it as parent, and is pushed. Step 4: `chat gpt-4.1-mini` does the same under `step 1`. Step 5: it ends and is popped; `step 1` is current again.

Now the mechanism. When a span starts, it asks, "what is the current span right now?" Whatever it finds becomes its parent. Then it makes itself current. When it ends, it steps aside and the previous span is current again. That "current span" lives in a context that follows your code from function to function, through await, without you passing anything. In Python it's built on `contextvars`.

That's why it works without you passing IDs around. And it's also why it breaks in exactly one situation: when your code jumps somewhere the context doesn't follow. A worker thread. A process. Another service. You'll break it on purpose in Lecture 3.6.

[SLIDE 5: Across the network]
- Context is serialised into HTTP headers: `traceparent: 00-<trace_id>-<span_id>-01`
- The other service reads the header, continues the same trace
- Atlas → ticketing API → back, all one trace, if both sides propagate

Across a network call, the context is written into a header called traceparent, carrying the trace ID and the current span ID. If the ticketing API reads that header, its spans join the same trace. That's how a single request can be followed across ten services. For Atlas, we mostly stay inside one process, but the collector in Section thirteen relies on this.

[SLIDE 6: Sampling]
- Head sampling: decide at the root, before anything happens (cheap, blind)
- Tail sampling: decide after the trace finishes (keep every error and slow trace, drop boring successes)
- Never sample the cost signal: tokens and dollars must be counted from every request
- Our approach: 100% in dev; in prod, tail-sample traces, count cost from metrics (Sections 9, 13)

Last idea: sampling. A busy agent produces more spans than you want to store. Head sampling decides at the root, before anything happens: keep one in ten. Cheap, but blind; it drops the one error you wanted. Tail sampling decides when the trace finishes: keep every error and every slow trace, drop most of the boring successes. That's what the collector does in Section thirteen.

One rule, though. Never sample the cost signal. Keep one trace in ten, and you've lost ninety percent of your dollars. Cost is counted from every request, as a metric, regardless of which traces you keep. Section nine builds that.

[SLIDE 7: What a trace answers that logs can't]
- Which spans belong to this request? (trace ID)
- What caused what? (parent ID)
- Where did time go? (start and end, nested)
- What were the facts? (attributes)
- What happened, and when? (events)

Put together: a trace tells you which work belonged to a request, what caused what, where time went, what the facts were and what happened when. Logs give you lines. Traces give you structure. Lecture 5.5 comes back to when you want each.

[AVATAR]
Six words and one mechanism. Trace, span, parent, attributes, events, status, held together by a current-span context that follows your code. Now let's write some.

[SLIDE 8: Recap]
- Spans linked by parent IDs form a trace
- The current-span context sets parents for you
- Sample traces, never the cost signal

**Recap:** A trace is a tree of spans linked by parent IDs, each carrying attributes, events and status; the tree is built automatically by a context that tracks the current span, and sampling decides which traces to keep, never which costs to count.

**Transition:** Next, you add OpenTelemetry by hand around one model call, then read how Atlas's real setup does the same thing.

### Speaker notes: common student mistakes / Q&A

- "Is a trace the same as a Langfuse trace?" Yes, with extras. Langfuse adds observation types, sessions and users on top of the same OTel spans. Section 4.1.
- "Do spans have to nest?" A trace can be a flat list of root spans, but then you've lost causality. Orphans are the most common instrumentation bug; 3.6 shows them.
- Students confuse events with logs. An event is attached to a span and inherits its trace and span IDs; a log line has to be correlated by hand (5.5).
- The slide 3 values come from one run of the console exporter on 2026-10-02; IDs differ on every run. Slide 2's timings are the mock's simulated latencies (`atlas.latency_ms`); wall-clock durations on the Traces page differ unless Atlas ran with `ATLAS_MOCK_LATENCY_SCALE=1`.
- Keep this lecture free of `gen_ai.*` names. 3.3 introduces them.

---

## Lecture 3.2 — Code-along: manual OpenTelemetry instrumentation of Atlas

| Field | Value |
|---|---|
| ID | 3.2 |
| Type | SC (code-along) |
| Target duration | 10:00 (~740 spoken words, about 5:17 of talking at 140 wpm, plus typing and console output) |
| Learning objectives | 1. Build a `setup_tracing()` with a `TracerProvider`, resource attributes and a `ConsoleSpanExporter`. 2. Wrap an agent run and a model call in `tracer.start_as_current_span` and read the nested spans in the console. 3. Find the same pieces, plus a `BatchSpanProcessor` and an OTLP exporter, in Atlas's real `telemetry/otel_setup.py`. |
| Prerequisites | 3.1, Section 2 |
| Files used | You type: `03-code/scratch/trace_by_hand.py` (a practice file, not part of the repo). Read: `03-code/telemetry/otel_setup.py` (`build_resource`, `_make_exporter`, `configure_tracing`). |

**Recording note:** the practice file is typed from empty, exactly as printed below; it was run on 2026-10-02 and produced the console output quoted in the DEMO cue. Run it from `03-code/` with the venv active: `PYTHONPATH=.:src python scratch/trace_by_hand.py`. The OTLP branch is the Langfuse OpenTelemetry endpoint (verify the path against the current Langfuse OpenTelemetry docs before recording) and needs the three Langfuse variables from 2.1 in the environment.

### Script

[AVATAR]
You've seen a trace. Now you're going to make one from nothing. Three parts: a provider that owns the pipeline, an exporter that decides where spans go, and two `with` statements around real work. About fifty lines, and you'll read the raw spans in your terminal before any UI is involved. Then we'll open Atlas's real setup and find every piece you typed.

[SCREEN: VS Code, new file `03-code/scratch/trace_by_hand.py`.]

[CODE: step 1, imports (practice file `scratch/trace_by_hand.py`)]
```python
"""Lecture 3.2: OpenTelemetry by hand, around one call to Atlas's offline model."""

import base64
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from app.mock_llm import MockLLM
from app.prompts import ATLAS_V1
```

Imports first. `trace` is the API: how application code gets a tracer. Everything under `sdk` is the implementation: the provider, the resource, the processors and exporters. Keep that split in your head. Application code imports the API; only setup code imports the SDK. The last two imports are Atlas's offline model and its system prompt, so we have real work to trace.

[CODE: step 2, the provider, the resource and two exporters]
```python
def setup_tracing(exporter: str) -> TracerProvider:
    resource = Resource.create(
        {"service.name": "atlas", "service.version": "dev", "deployment.environment": "dev"}
    )
    provider = TracerProvider(resource=resource)
    if exporter == "console":
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    if exporter == "otlp":
        keys = f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}"
        auth = base64.b64encode(keys.encode()).decode()
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=f"{os.environ['LANGFUSE_BASE_URL']}/api/public/otel/v1/traces",
                    headers={"Authorization": f"Basic {auth}"},
                )
            )
        )
    trace.set_tracer_provider(provider)
    return provider
```

Now `setup_tracing`. The resource describes who is emitting spans: service name, version and environment. These attach to every span automatically, so you can filter a backend to "atlas in production" without setting anything per span.

Then a `TracerProvider` with that resource, and a span processor. A processor decides when to hand spans to an exporter; the exporter decides where they go. For the console we use `SimpleSpanProcessor`, which exports each span the moment it ends.

[SCREEN: Highlight the `otlp` branch.]

The second branch is the real destination. OTLP is OpenTelemetry's wire protocol, and Langfuse accepts it at slash api slash public slash otel. Authenticate with basic auth built from your two keys. And this time use `BatchSpanProcessor`. Why? It queues spans and sends them in batches on a background thread. Never use the simple processor with a network exporter; it would block your request on every span. Finally, set the provider as the global one, so `trace.get_tracer` anywhere finds it.

[CODE: step 3, a tracer and two nested spans]
```python
provider = setup_tracing(os.getenv("OTEL_EXPORTER", "console"))
tracer = trace.get_tracer("atlas.by_hand")
llm = MockLLM(seed=7)


def answer(question: str, tenant: str) -> str:
    with tracer.start_as_current_span("invoke_agent atlas") as agent_span:
        agent_span.set_attribute("atlas.tenant", tenant)
        messages = [
            {"role": "system", "content": ATLAS_V1},
            {"role": "user", "content": question},
        ]
        with tracer.start_as_current_span("chat gpt-4.1-mini") as span:
            response = llm.chat(model="gpt-4.1-mini", messages=messages)
            span.set_attribute("atlas.input_tokens", response.usage.prompt_tokens)
            span.set_attribute("atlas.output_tokens", response.usage.completion_tokens)
        return response.choices[0].message.content or "(the model asked for a tool)"


if __name__ == "__main__":
    print(answer("How do I connect to the VPN from home?", tenant="ops"))
    provider.shutdown()
```

Now the work. Set up tracing once, before any tracer is used. Get a tracer, named after the code that owns it. Then two `with` statements. The outer one, `invoke_agent atlas`, wraps the whole answer and records the tenant. The inner one, `chat gpt-4.1-mini`, wraps the model call and records the token counts, with our own attribute names for now. Because the inner span starts while the outer one is current, it becomes its child. No IDs passed. And `provider.shutdown()` at the end flushes anything still queued.

[SCREEN: Terminal: `PYTHONPATH=.:src python scratch/trace_by_hand.py`.]

[DEMO: Two JSON blocks print. First `"name": "chat gpt-4.1-mini"` with `"parent_id": "0xaa37367431e9dca6"` and `"attributes": {"atlas.input_tokens": 2521, "atlas.output_tokens": 44}`; then `"name": "invoke_agent atlas"` with `"parent_id": null` and `"attributes": {"atlas.tenant": "ops"}`. Both share `"trace_id": "0xe6c9f591eeb375e3b03ba180bb735043"`. Each ends with a `resource` block containing `"service.name": "atlas"`. The last line is `(the model asked for a tool)`.]

Run it and read the output. The model call prints first, because it ended first. It has a parent ID. The agent span prints second, with parent ID null: it's the root. Same trace ID on both. And at the bottom of each, the resource: service name atlas. That's a trace, in your terminal, with no backend. The last line? The mock wanted to search the knowledge base before answering. We gave this toy no tools, so we stop there.

[PAUSE]

[SCREEN: Terminal, with the Langfuse variables loaded: `OTEL_EXPORTER=otlp PYTHONPATH=.:src python scratch/trace_by_hand.py`. Browser: Langfuse traces list shows a new trace `invoke_agent atlas` with one child, no types, no usage. Capture live; verify the endpoint path first.]

Switch the exporter to OTLP and run it again. A few seconds later, there it is in Langfuse. Two spans, nested correctly. Notice what's missing compared to Lecture 2.3: no observation types, no usage, no cost. Those come from attributes, which is the next two lectures.

[SCREEN: VS Code, `telemetry/otel_setup.py`. Show `build_resource` and `_make_exporter`, then scroll to `configure_tracing`.]

[CODE: excerpt of `telemetry/otel_setup.py`, `configure_tracing` (lines in between elided as `...`)]
```python
        sampler = ParentBased(TraceIdRatioBased(settings.trace_sample_rate))
        provider = TracerProvider(resource=build_resource(settings), sampler=sampler)
        ...
        def add(exp: SpanExporter, name: str, *, simple: bool = False) -> None:
            safe = SafeSpanExporter(exp, name=name)
            _STATE.exporters.append(safe)
            if use_batch and not simple:
                provider.add_span_processor(
                    BatchSpanProcessor(
                        safe,
                        max_queue_size=2048,
                        max_export_batch_size=256,
                        schedule_delay_millis=1000,
                        export_timeout_millis=5000,
                    )
                )
            else:
                provider.add_span_processor(SimpleSpanProcessor(safe))
```

Now the real thing. Atlas's version is called `configure_tracing`, with `setup_tracing` as an alias. Same shape as yours. A resource, built from settings. A provider, plus a sampler you'll meet in Section thirteen. And an `add` helper that wraps every exporter in a safety wrapper, so a broken backend can never crash a request, and puts it behind a batch processor with explicit queue and timeout limits. Above it, `_make_exporter` picks console, OTLP to a collector, a file, or memory for tests, from the `OTEL_EXPORTER` variable. And two more destinations: the local store the console reads, and Langfuse, when your keys are set.

[SCREEN: Terminal 1: `OTEL_EXPORTER=console make run` (with `.env` sourced). Terminal 2: the VPN `curl` from 2.3.]

[DEMO: Seven JSON blocks print in Terminal 1, in this order: `guardrail injection_check`, `chat gpt-4.1-mini`, `execute_tool search_knowledge_base`, `step 1`, `chat gpt-4.1-mini`, `step 2`, `invoke_agent atlas`. All share one `trace_id`; only `invoke_agent atlas` has `"parent_id": null`.]

Run Atlas with the console exporter and send the VPN question. Seven spans instead of two, but read them the same way. Children print before parents. One trace ID. Exactly one root, `invoke_agent atlas`. Everything you typed in the practice file, Atlas does on every request.

[SLIDE 1: The pipeline you just built]
- `Resource` → who is emitting (service.name, version, environment)
- `TracerProvider` → owns the pipeline; set once, globally
- `SpanProcessor` → when to export: Simple (now) vs Batch (queued)
- `SpanExporter` → where to: console, OTLP, file, memory, plus the local store and Langfuse
- `tracer.start_as_current_span(name)` → the only line application code needs

[AVATAR]
Here's the whole pipeline: resource, provider, processor, exporter, and one `with` statement per unit of work. Every tracing tool you'll ever meet is a variation of these five boxes.

[SLIDE 2: Recap]
- Resource, provider, processor, exporter
- One `with` per unit of work
- Batch processor for every network exporter

**Recap:** `setup_tracing()` builds a `TracerProvider` with resource attributes and a console or batched OTLP exporter, two `start_as_current_span` blocks give a nested trace with no IDs passed by hand, and Atlas's `configure_tracing` is the same pipeline with safety wrappers and more destinations.

**Transition:** The spans exist, but Langfuse showed your practice spans as plain boxes. Next, the standard attribute names that turn a box into a model call with tokens and cost.

### Speaker notes: common student mistakes / Q&A

- Mistake: calling `setup_tracing()` after a tracer was fetched at import time in another module. The global provider can only be set once; fetch tracers after setup, or lazily (Atlas's `get_tracer()` does this).
- Mistake: `SimpleSpanProcessor` with `OTLPSpanExporter`. It works, but every request blocks on a network round trip per span.
- Mistake: forgetting `provider.shutdown()` or `force_flush()` in short scripts. Batched spans are lost when the process exits before the flush. The FastAPI lifespan in `server.py` calls `force_flush()` and `shutdown_tracing()`; `simulator/loop_demo.py` calls `force_flush()`.
- The OTLP path: when you pass `endpoint=` to `OTLPSpanExporter` you give the full URL including `/v1/traces`; the collector config in Section 13 gives the base `/api/public/otel` and the exporter appends the rest.
- `scratch/` is your own folder; it isn't in the repo and isn't committed. Delete it after the lecture if you like.

---

## Lecture 3.3 — GenAI semantic conventions: naming things so tools understand them

| Field | Value |
|---|---|
| ID | 3.3 |
| Type | SL (slides, with one terminal beat) |
| Target duration | 8:00 (~790 spoken words, about 5:39 of talking at 140 wpm) |
| Learning objectives | 1. Explain what semantic conventions are and why standard names buy portability. 2. Name the core `gen_ai.*` attributes for model calls, tools and agents, and the span naming rule. 3. State what "incubating" means for your code. |
| Prerequisites | 3.2 |
| Files used | `03-code/telemetry/genai_attrs.py` (applied in 3.4); one `python -c` command |

### Script

[AVATAR]
Your span from the last lecture had an attribute called `atlas.input_tokens`. Mine could have said `llm.tokens.prompt`. The team next door has `tokens_in`. Now build a cost dashboard that works for all three. [PAUSE] You can't. That's the problem semantic conventions solve, and it's why a backend can show you cost without you telling it your schema.

[SLIDE 1: What a semantic convention is]
- An agreed name and meaning for an attribute
- `http.request.method` is one; every backend knows it means the HTTP verb
- The GenAI conventions do the same for models, tokens, tools and agents
- Published by OpenTelemetry; shipped as constants in `opentelemetry-semantic-conventions`

A semantic convention is an agreed name with an agreed meaning. You already rely on them. `http.request.method` means the HTTP verb in every tool on earth. The GenAI conventions do the same for language models: what to call the model name, the token counts, a tool call, an agent.

[SLIDE 2: The naming rule for spans]
| Span kind | Name | Example |
|---|---|---|
| Model call | `{operation} {request model}` | `chat gpt-4.1-mini` |
| Tool call | `execute_tool {tool name}` | `execute_tool lookup_ticket` |
| Agent run | `invoke_agent {agent name}` | `invoke_agent atlas` |

Start with span names, because you've already used them. A model call is the operation followed by the model: `chat gpt-4.1-mini`. A tool call is `execute_tool` and the tool's name. An agent run is `invoke_agent` and the agent's name. That's why 3.2's names looked the way they did.

[SLIDE 3: Model call attributes (Atlas's step 1 call, from the console exporter)]
```text
gen_ai.operation.name          "chat"
gen_ai.provider.name           "openai"
gen_ai.request.model           "gpt-4.1-mini"
gen_ai.response.model          "gpt-4.1-mini-2025-04-14"
gen_ai.usage.input_tokens      3262
gen_ai.usage.output_tokens     44
gen_ai.usage.cache_read.input_tokens      (set only when > 0)
gen_ai.usage.reasoning.output_tokens      (set only when > 0)
gen_ai.response.finish_reasons ["tool_calls"]
```
Footer: incubating, names may change.

Now the attributes on a model call, from Atlas's first call in the VPN request. Operation name, `chat`. Provider name, `openai`. The model you asked for, and the model that actually answered; they differ when the provider resolves an alias to a dated snapshot, and that matters when a snapshot changes behaviour. Then usage. Input tokens, output tokens, and two that most people forget: cached input tokens and reasoning output tokens. Both are priced differently, and both are invisible if you only record the two big numbers. Section six leans hard on them.

[SLIDE 4: Tool call attributes (the ticket question)]
```text
gen_ai.operation.name       "execute_tool"
gen_ai.tool.name            "lookup_ticket"
gen_ai.tool.call.id         "call_763770efa5"
gen_ai.tool.call.arguments  {"ticket_id": "TCK-100231"}
gen_ai.tool.call.result     {"error": "not_found", "ticket_id": "TCK-100231"}   (masked, clipped)
```

For a tool call: operation `execute_tool`, the tool's name, the call ID the model assigned, the arguments the model chose, and the result. Two cautions on the last two. Arguments and results are content, so they can hold personal data; Atlas masks them, and Section ten goes deeper. And results can be huge; clip before you attach, or your telemetry costs more than your model calls.

[SLIDE 5: Agent and conversation attributes]
```text
gen_ai.operation.name    "invoke_agent"
gen_ai.agent.name        "atlas"
gen_ai.provider.name     "openai"
gen_ai.conversation.id   "sess-demo-1"
```
- The conventions also define `gen_ai.agent.version`; Atlas records its prompt version as `atlas.prompt_version`

For the agent span: operation `invoke_agent`, agent name, provider. And `gen_ai.conversation.id`, which is where a session ID goes in the standard. Langfuse has its own session concept on top; Atlas sets both. There's also an agent version attribute; Atlas keeps its prompt version in its own namespace instead.

[SLIDE 6: Constants, not strings]
```python
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g

span.set_attribute(g.GEN_AI_REQUEST_MODEL, "gpt-4.1-mini")
span.set_attribute(g.GEN_AI_USAGE_INPUT_TOKENS, 3262)
span.set_attribute(g.GEN_AI_OPERATION_NAME, g.GenAiOperationNameValues.CHAT.value)
```
- `_incubating` in the path is deliberate: these names are not stable yet
- A constant renames with the package; a string typo is a silent hole in your dashboard

In code, never type these as strings. Import the constants. The module path has `_incubating` in it, on purpose. It's a signal that these names are not frozen. Two reasons to use the constants anyway. If a name changes in a future release, your code changes with the package, in one place. And a typo in a string is a silent hole in a dashboard; a typo in a constant is an error the moment the line runs.

[SCREEN: Terminal in `03-code/`, venv active.]

[CODE: ask the package what the names are]
```bash
python -c "from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g; print(g.GEN_AI_REQUEST_MODEL, g.GEN_AI_USAGE_INPUT_TOKENS, g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, g.GEN_AI_PROVIDER_NAME, g.GEN_AI_SYSTEM)"
```

[DEMO: One line: `gen_ai.request.model gen_ai.usage.input_tokens gen_ai.usage.cache_read.input_tokens gen_ai.provider.name gen_ai.system`]

Don't memorise these; ask the package. One line of Python prints the strings behind the constants. Look at the last two: provider name, and the older system name. Hold that thought.

[SLIDE 7: What "incubating" means for you]
- Stable conventions (HTTP, DB) have compatibility guarantees. GenAI does not yet.
- Expect renames between minor versions; pin the package, read the changelog
- Backends may support a range of old and new names; Langfuse maps `gen_ai.*` today
- Say it on every dashboard: "GenAI semconv 0.66; names may change"

What does incubating mean in practice? Stable conventions come with compatibility promises. GenAI doesn't yet. Names have already been renamed once: `gen_ai.system` became `gen_ai.provider.name`, and as you just saw, both constants exist right now. So pin the package version, read the changelog when you bump it, and keep the footer you see on this slide on your own dashboards. It's honest, and it saves an argument later.

[SLIDE 8: Why this buys portability]
Diagram: Atlas emits one span with `gen_ai.usage.input_tokens=3262`. Arrows to Langfuse ("shows usage"), Phoenix ("shows tokens"), Grafana via collector ("metrics from spans"), Datadog ("LLM Observability"). Caption: same span, four backends, zero code changes.

So what does all this buy you? Emit one span with standard names, and Langfuse shows its usage. Phoenix shows the tokens. A collector can turn spans into metrics for Grafana. Datadog reads them too. Same span, four backends, no code changes. Section twelve is that diagram, live.

[SLIDE 9: The conventions name metrics too]
```python
from opentelemetry.semconv._incubating.metrics import gen_ai_metrics as gm

gm.GEN_AI_CLIENT_TOKEN_USAGE                    # "gen_ai.client.token.usage"  (histogram, by gen_ai.token.type)
gm.GEN_AI_CLIENT_OPERATION_DURATION             # "gen_ai.client.operation.duration"
gm.GEN_AI_CLIENT_OPERATION_TIME_TO_FIRST_CHUNK  # "gen_ai.client.operation.time_to_first_chunk"
```
Footer: incubating, names may change.

The conventions don't stop at spans. There are standard metric names too, in a sibling module. Token usage as a histogram, split by token type. Operation duration. Time to first chunk. Atlas exposes its own Prometheus metrics in Section nine, but when you see `gen_ai.client.token.usage` on a dashboard you didn't build, you'll know it was derived from spans like the ones you're tagging now.

[SLIDE 10: What the conventions don't cover]
- Cost in dollars: not a standard attribute; Atlas sets `atlas.cost_usd` and Langfuse's `cost_details` (6.2)
- Your business dimensions: tenant, feature, ticket type → your own namespace, `atlas.*`
- Quality scores: a backend feature, not a span attribute (4.5)

And what they don't cover. Dollars. There's no standard cost attribute; a backend computes it from tokens and a price table, or you set it explicitly, which Atlas does. Your business dimensions, like tenant and feature, go in your own namespace; ours is `atlas.`. And quality scores, which are a backend feature.

[AVATAR]
Standard names for models, tokens, tools and agents. Constants, never strings. And the word incubating on every screen that shows them. Now let's see where Atlas puts them.

[SLIDE 11: Recap]
- Standard names for models, tokens, tools, agents
- Constants from the incubating package, never strings
- Your own dimensions in your own namespace

**Recap:** The GenAI semantic conventions give models, token usage, tool calls and agents standard attribute names and span names, imported as constants from the incubating semconv package, so any backend can compute cost and draw the trace without knowing your schema.

**Transition:** Next, a code-along through `genai_attrs.py`: the setters that tag every model, tool and agent span, and the test that proves it.

### Speaker notes: common student mistakes / Q&A

- "Why does the import path say `_incubating`?" Because the conventions are not stable. It's the documented import path for these names at this version. Don't try to avoid it.
- "Should I record `gen_ai.input.messages`?" The conventions define it and `gen_ai.output.messages`; content capture is opt-in in most instrumentors for privacy and size. Atlas records the newest message, masked and clipped (`ga.set_llm_messages`), and Section 10.2 covers the switches.
- Students ask about OpenInference's `llm.token_count.prompt` names. Different convention, same idea; OpenInference is what auto-instrumentation emits (3.5).
- Slide 3 and 4 values were captured from Atlas's console exporter on 2026-10-02; the call ID is generated by the mock and is the same on every offline run.
- Keep the footer visible whenever a `gen_ai.*` name is on screen.

---

## Lecture 3.4 — Code-along: tag every LLM, tool and agent span correctly

| Field | Value |
|---|---|
| ID | 3.4 |
| Type | SC (code-along: read, break, fix) |
| Target duration | 9:00 (~640 spoken words, about 4:34 of talking at 140 wpm, plus console output and the test run) |
| Learning objectives | 1. Read the span-name helpers and the setters in `telemetry/genai_attrs.py`: `set_llm_request`, `set_llm_usage`, `set_cost`, `set_tool`. 2. Find where `AtlasAgent` calls them for each model call and each tool call. 3. Verify the attributes in console exporter output, then break one call and watch `test_ticket_question_emits_tagged_tool_span` catch it. |
| Prerequisites | 3.2, 3.3 |
| Files used | `03-code/telemetry/genai_attrs.py`, `03-code/app/agent.py` (`_call_model`, `_run_tool`), `03-code/tests/integration/test_spans.py` (`test_ticket_question_emits_tagged_tool_span`) |

**Recording note:** the break in step 5 is a temporary edit: comment out the `ga.set_tool(...)` call in `_run_tool`, run the test (it fails with `KeyError: 'gen_ai.tool.name'`, verified 2026-10-02), then restore with `git checkout app/agent.py` on camera. Code blocks marked "excerpt" are exact lines from the repo with elided lines shown as `...`.

### Script

[AVATAR]
In 3.2 your span said `atlas.input_tokens`. Atlas's spans say `gen_ai.usage.input_tokens`, and a dozen other standard names. Where do they come from? One small module of setters, called at three places in the agent. Let's read them, prove them with the console, then break one on purpose and watch a test catch it.

[SCREEN: VS Code, `telemetry/genai_attrs.py`, top of file.]

[CODE: excerpt of `telemetry/genai_attrs.py`, span names]
```python
def llm_span_name(model: str, operation: str = OP_CHAT) -> str:
    return f"{operation} {model}"


def tool_span_name(tool: str) -> str:
    return f"{OP_EXECUTE_TOOL} {tool}"


def agent_span_name(agent: str = "atlas") -> str:
    return f"{OP_INVOKE_AGENT} {agent}"
```

Start with names. Three tiny functions build the span names from 3.3's rule. Notice `OP_CHAT` and friends: they're the convention's own enum values, so even the word `chat` isn't something we typed.

[CODE: `set_llm_request` from `telemetry/genai_attrs.py`]
```python
def set_llm_request(
    span: Span,
    *,
    model: str,
    provider: str = PROVIDER_OPENAI,
    operation: str = OP_CHAT,
    temperature: float | None = None,
    max_tokens: int | None = None,
    conversation_id: str | None = None,
    prompt_version: str | None = None,
    prompt_cache_key: str | None = None,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, operation)
    span.set_attribute(g.GEN_AI_PROVIDER_NAME, provider)
    span.set_attribute(g.GEN_AI_REQUEST_MODEL, model)
    span.set_attribute(LF_OBS_TYPE, "generation")
    span.set_attribute(LF_OBS_MODEL, model)
    if temperature is not None:
        span.set_attribute(g.GEN_AI_REQUEST_TEMPERATURE, temperature)
    if max_tokens is not None:
        span.set_attribute(g.GEN_AI_REQUEST_MAX_TOKENS, max_tokens)
    if conversation_id:
        span.set_attribute(g.GEN_AI_CONVERSATION_ID, conversation_id)
    if prompt_version:
        span.set_attribute(ATLAS_PROMPT_VERSION, prompt_version)
    if prompt_cache_key:
        span.set_attribute("openai.request.prompt_cache_key", prompt_cache_key)
```

The request setter runs before the call. Operation, provider, requested model: the standard names, through the `g.` constants. Then two lines that aren't standard: `LF_OBS_TYPE` and `LF_OBS_MODEL`. They're Langfuse's attribute names, `langfuse.observation.type` and the model name, and they're why this span shows up in Langfuse as a generation instead of a grey box. Standard names for portability, Langfuse names for the UI. Section four explains the second set.

[CODE: excerpt of `set_llm_usage` from `telemetry/genai_attrs.py`]
```python
    span.set_attribute(g.GEN_AI_USAGE_INPUT_TOKENS, int(input_tokens))
    span.set_attribute(g.GEN_AI_USAGE_OUTPUT_TOKENS, int(output_tokens))
    if cached_tokens:
        span.set_attribute(g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, int(cached_tokens))
    if reasoning_tokens:
        span.set_attribute(g.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS, int(reasoning_tokens))
    if response_model:
        span.set_attribute(g.GEN_AI_RESPONSE_MODEL, response_model)
    ...
    if finish_reasons:
        span.set_attribute(g.GEN_AI_RESPONSE_FINISH_REASONS, list(finish_reasons))
    ...
    usage: dict[str, int] = {"input": int(input_tokens), "output": int(output_tokens)}
    if cached_tokens:
        usage["cache_read_input_tokens"] = int(cached_tokens)
    if reasoning_tokens:
        usage["reasoning_tokens"] = int(reasoning_tokens)
    span.set_attribute(LF_OBS_USAGE, json.dumps(usage))
```

The usage setter runs after the call. Input and output tokens. Then the two people forget: cached input and reasoning output, each written only when there are some. The response model, which is the dated snapshot. Finish reasons: `tool_calls` versus `stop` tells you, across a day, how often the model chose to act rather than answer. And at the bottom, the same numbers again as Langfuse's `usage_details` JSON. The elided lines handle time to first token, which is Lecture 5.4.

[SCREEN: Scroll to `set_cost` and `set_tool`.]

[CODE: `set_tool` from `telemetry/genai_attrs.py`]
```python
def set_tool(
    span: Span,
    *,
    name: str,
    call_id: str | None = None,
    arguments: Any = None,
    result: Any = None,
    tool_type: str = "function",
    redact: bool = True,
) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, OP_EXECUTE_TOOL)
    span.set_attribute(g.GEN_AI_TOOL_NAME, name)
    span.set_attribute(g.GEN_AI_TOOL_TYPE, tool_type)
    span.set_attribute(LF_OBS_TYPE, "tool")
    if call_id:
        span.set_attribute(g.GEN_AI_TOOL_CALL_ID, call_id)
    if arguments is not None:
        s = _safe(arguments, redact)
        span.set_attribute(g.GEN_AI_TOOL_CALL_ARGUMENTS, s)
        span.set_attribute(LF_OBS_INPUT, s)
    if result is not None:
        s = _safe(result, redact)
        span.set_attribute(g.GEN_AI_TOOL_CALL_RESULT, s)
        span.set_attribute(LF_OBS_OUTPUT, s)
```

Just above it, `set_cost` writes the price of the call as `atlas.cost_usd` and as Langfuse's `cost_details`; Section six builds the price table behind it. And the tool setter. Operation `execute_tool`, tool name, type, call ID, then arguments and result. Both go through `_safe`, which masks personal data and clips anything over four thousand characters. Attributes must be strings, numbers, booleans or lists of those, so dictionaries become JSON. A shipment lookup can return a page of JSON; you want to know it happened, not store it twice.

[SCREEN: VS Code, `app/agent.py`, `_call_model`.]

[CODE: excerpt of `app/agent.py`, `_call_model` (elided lines shown as `...`)]
```python
            with self.tracer.start_as_current_span(ga.llm_span_name(current)) as span:
                ga.set_llm_request(
                    span,
                    model=current,
                    conversation_id=session_id,
                    prompt_version=prompt_version,
                    prompt_cache_key=cache_key,
                )
                ...
                    inp, out, cached, reasoning = usage_numbers(usage)
                    cost = self._price(current, inp, out, cached, reasoning)
                    ga.set_llm_usage(
                        span,
                        input_tokens=inp,
                        output_tokens=out,
                        cached_tokens=cached,
                        reasoning_tokens=reasoning,
                        ...
                    )
                    ga.set_cost(span, cost)
```

Now the call sites. In `_call_model`: open a span named by the helper, set the request attributes, call the model, then set usage and cost. In `_run_tool`, the same pattern: a span named `execute_tool` plus the tool, and `ga.set_tool` after the tool returns. And in `run`, `ga.set_agent` on the root. Three setters, three places. Because the tool runs inside the step span, which runs inside the agent span, everything nests.

[SCREEN: Terminal 1: `OTEL_EXPORTER=console make run` (with `.env` sourced). Terminal 2: the ticket question.]

[CODE: ask about a ticket]
```bash
curl -s localhost:8000/chat -H 'Content-Type: application/json' \
  -H 'X-Tenant: ops' -H 'X-User: NW-40213' -H 'X-Session: sess-demo-2' \
  -d '{"message": "Where is my ticket TCK-100231?"}'
```

[DEMO: Terminal 1 prints seven spans. Highlight three: `chat gpt-4.1-mini` with `"gen_ai.usage.input_tokens": 3261`, `"gen_ai.response.finish_reasons": ["tool_calls"]`; `execute_tool lookup_ticket` with `"gen_ai.tool.name": "lookup_ticket"`, `"gen_ai.tool.call.arguments": "{\"ticket_id\": \"TCK-100231\"}"`, `"gen_ai.tool.call.result": "{\"error\": \"not_found\", \"ticket_id\": \"TCK-100231\"}"` and `"status_code": "ERROR"`; and the second `chat gpt-4.1-mini` with `["stop"]`.]

Ask about a ticket, and read the console. The first model call finishes with `tool_calls`. Then `execute_tool lookup_ticket`, with the arguments the model chose. The ticket doesn't exist, so the result says not found and the span's status is ERROR: a failed tool is visible without a single log line. Then the second model call, finishing with `stop`.

[SCREEN: VS Code, `tests/integration/test_spans.py`, `test_ticket_question_emits_tagged_tool_span`.]

[CODE: `test_ticket_question_emits_tagged_tool_span` from `tests/integration/test_spans.py`]
```python
def test_ticket_question_emits_tagged_tool_span(client):
    """3.4: the tool span carries gen_ai.tool.name and is a child of the agent's step span."""
    _chat(client, "Where is my ticket TCK-100231?", session_id="s1")
    spans = _spans(client)
    tool = _by_name(spans, "execute_tool lookup_ticket")[0]
    agent = _by_name(spans, "invoke_agent atlas")[0]
    assert tool.attributes[g.GEN_AI_TOOL_NAME] == "lookup_ticket"
    assert '"ticket_id": "TCK-100231"' in tool.attributes[g.GEN_AI_TOOL_CALL_ARGUMENTS]
    ids = {s.get_span_context().span_id: s for s in spans}
    step = ids[tool.parent.span_id]
    assert step.name.startswith("step ") and step.parent.span_id == agent.context.span_id
```

And a test, so this can't rot. The `client` fixture starts the FastAPI app offline with an in-memory exporter. The test asks the same question, finds the tool span, checks its name attribute and arguments, and checks that its parent is a step, whose parent is the agent.

[SCREEN: In `app/agent.py`, comment out the seven-line `ga.set_tool(...)` call in `_run_tool`. Terminal: run the test.]

[CODE: break it, run the test, restore]
```bash
python -m pytest -q tests/integration/test_spans.py::test_ticket_question_emits_tagged_tool_span
git checkout app/agent.py
python -m pytest -q tests/integration/test_spans.py::test_ticket_question_emits_tagged_tool_span
```

[DEMO: First run: `KeyError: 'gen_ai.tool.name'` and `1 failed`. After `git checkout`: `1 passed`.]

What happens if someone deletes that one call during a refactor? Comment out the `set_tool` call and run the test. Red: `KeyError`, no `gen_ai.tool.name`. The tool still ran, the answer was still right, and the trace silently lost its most useful attribute. Restore the file and rerun. Green.

[AVATAR]
A handful of setters, three call sites, one test. Atlas speaks the standard, and the test makes sure it keeps speaking it. Next lecture, you'll see how much of this an auto-instrumentor does for you, and why you keep the setters anyway.

[SLIDE 1: Recap]
- Setters own every `gen_ai.*` and `langfuse.*` name
- Three call sites: agent, model call, tool
- A test fails when a setter goes missing

**Recap:** `genai_attrs.py` builds the span names and sets the `gen_ai.*` constants plus Langfuse's type, usage and cost attributes, `AtlasAgent` calls those setters on the agent, every model call and every tool call, and `test_ticket_question_emits_tagged_tool_span` fails the moment one goes missing.

**Transition:** Next, one line of auto-instrumentation that captures every OpenAI call, and the things it can't know.

### Speaker notes: common student mistakes / Q&A

- Mistake: passing a dict directly to `set_attribute`. OpenTelemetry drops it with a warning. Encode it to JSON first, as `_safe`/`_clip` do.
- Mistake: setting usage attributes before the response exists. Set them when usage is known; 5.4 handles streaming.
- "Why keep `atlas.tenant` when there's `gen_ai.conversation.id`?" Tenant is a business dimension the conventions don't define. Own namespace, always.
- The module also exports `set_agent_attrs`, `set_llm_attrs` and `set_tool_attrs` as convenience aliases; the agent uses the names shown on screen.
- Always restore `app/agent.py` after the break; students copy what they last saw.

---

## Lecture 3.5 — Auto-instrumentation with OpenInference

| Field | Value |
|---|---|
| ID | 3.5 |
| Type | SC (code-along, one live call) |
| Target duration | 6:00 (~465 spoken words, about 3:19 of talking at 140 wpm, plus output) |
| Learning objectives | 1. Instrument the OpenAI client with `OpenAIInstrumentor().instrument(tracer_provider=...)` through `instrument_openai`. 2. Read what the auto-generated span contains and where it nests. 3. Decide what to keep manual: agent span, steps, tool spans, business attributes. |
| Prerequisites | 3.4 |
| Files used | `03-code/telemetry/openinference_setup.py` (`instrument_openai`, `is_instrumented`, `uninstrument_openai`) |

**Recording note:** the demo is one live request (about half a cent; verify current pricing) with `OFFLINE=0` and a real `OPENAI_API_KEY`, because OpenInference patches the OpenAI SDK and never sees the offline mock. Record the real console output; the span name and attribute list in the DEMO cue are what OpenInference documents for chat completions (verify at recording). Atlas does not call `instrument_openai` at startup.

### Script

[AVATAR]
Everything `_call_model` does with those setters, an auto-instrumentor can do in one line, for every OpenAI call in your process, including the ones inside libraries you didn't write. So why did we read the setters first? Because you need to know what it does, to know what it can't. Let's turn it on and compare.

[SLIDE 1: Which instrumentor]
- We use `openinference-instrumentation-openai` (Arize's OpenInference project)
- It patches the OpenAI client and emits one span per call with model, tokens, messages
- Uses OpenInference attribute names (`llm.token_count.prompt`, ...); Langfuse and Phoenix both read them
- Not used: `opentelemetry-instrumentation-openai-v2` (import error at verification time)

We use OpenInference's OpenAI instrumentor. It patches the client and emits a span per call, with model, token counts and messages, using OpenInference's attribute names. Langfuse and Phoenix both understand those. There's also an OpenTelemetry-contrib instrumentor for OpenAI; at verification time it failed to import, so it isn't in this course.

[SCREEN: VS Code, `telemetry/openinference_setup.py`.]

[CODE: excerpt of `telemetry/openinference_setup.py`]
```python
def instrument_openai(tracer_provider: Any) -> bool:
    """Instrument once; returns True if active. Instrumenting twice double-counts spans."""
    global _INSTRUMENTED
    if not OPENINFERENCE_AVAILABLE:
        log.info("openinference not installed; skipping auto-instrumentation")
        return False
    if _INSTRUMENTED:
        return True
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
    _INSTRUMENTED = True
    return True
```

The repo wraps it in one function. The heart is one line: `OpenAIInstrumentor().instrument`, with the tracer provider passed explicitly, so the auto spans go through the same pipeline as Atlas's own. Around it, two guards. If the package isn't installed, skip quietly. And if it's already on, don't do it again; the docstring says why, and the next lecture shows it.

[CODE: a one-off live run with the instrumentor on]
```bash
OFFLINE=0 OTEL_EXPORTER=console ATLAS_LOCAL_STORE= python -c "
from telemetry.otel_setup import configure_tracing, force_flush
from telemetry.openinference_setup import instrument_openai
from app.agent import AtlasAgent
provider = configure_tracing()
instrument_openai(provider)
AtlasAgent().run('Where is my ticket TCK-100231?', tenant='ops', user_id='NW-40213')
force_flush()"
```

Atlas doesn't switch it on by default, so here's a one-off script. Configure tracing, instrument the client with that provider before the agent creates its OpenAI client, run one question live, flush. Instrument first: it patches the class, so a client created earlier may not be covered.

[DEMO: Console output (live). Besides Atlas's own spans, one extra span per model call, named `ChatCompletion`, with `openinference.span.kind: LLM`, `llm.model_name`, `llm.token_count.prompt`, `llm.token_count.completion`, `llm.input_messages...`, `llm.output_messages...`. Its `parent_id` is the `chat gpt-4.1-mini` span of the same step.]

Read the console. Besides Atlas's spans, there's a span named `ChatCompletion`, kind `LLM`, with the model name, both token counts, and the full input and output messages, nested inside our own model-call span. We wrote none of that. [PAUSE] But look closely: our span already had those token counts too. Same call, recorded twice. Do you see where that leads? Remember it.

[SLIDE 2: What you get for free, and what you don't]
| Free from the instrumentor | Still yours |
|---|---|
| One span per OpenAI call | The agent span and the step structure |
| Model, tokens, messages, invocation parameters | Tool spans with arguments and results |
| Works inside libraries you didn't write | Business attributes: tenant, feature, prompt version |
| Streaming and async handled | Events like "step limit reached", cost in dollars |

Here's the split. Free: a span per call, with model, tokens, messages and parameters, streaming and async included, even inside libraries you don't control. Not free: everything that isn't an API call. The agent span. The steps. The tool spans. Tenant and feature. The step-limit event. The price. The instrumentor sees API calls; it doesn't know your agent exists.

[SLIDE 3: Our rule]
- Auto-instrument the client when you need coverage you don't control
- Manual spans for agent, steps, tools and business attributes
- One model call, one span carrying usage (3.6)
- Atlas's default: its own generation spans; OpenInference off; `instrument_openai` ready for Section 12

So our rule. Auto-instrumentation is great coverage for calls you don't control. Manual spans for the agent, steps, tools and business attributes. And one model call, one span carrying usage. Atlas's default is its own generation spans with OpenInference off, and the switch ready for Section twelve.

[AVATAR]
One line, every call captured. Keep the setters for everything the instrumentor can't see. And keep that "one call, one span" rule in mind; it's the third break in the next lecture.

[SLIDE 4: Recap]
- One line instruments every OpenAI call
- It can't see agents, steps, tools, tenants
- Never record one call's usage twice

**Recap:** `instrument_openai(provider)` wraps `OpenAIInstrumentor().instrument(tracer_provider=...)` and emits a span per OpenAI call with model, tokens and messages inside your own spans; the agent, steps, tools and business attributes stay manual, and each model call should carry usage once.

**Transition:** Next, three ways this pipeline breaks silently, and the test that catches each one.

### Speaker notes: common student mistakes / Q&A

- Mistake: instrumenting after the OpenAI client is constructed. Depending on version, the patch may not apply to existing instances. Instrument before `AtlasAgent()` builds its client.
- "Does it capture the mock?" No. The mock isn't the OpenAI client, which is why this demo is live. Offline, Atlas's own generation spans carry the usage.
- "Will Langfuse show the `ChatCompletion` span too?" Not from Atlas: `telemetry/langfuse_setup.py` passes `should_export_span`, which forwards only spans from the `atlas` tracer, Langfuse's own, or spans carrying `gen_ai.*` or `langfuse.*` attributes. OpenInference spans carry `llm.*` names, so they stay in the console and other exporters. Section 4.1 explains the filter.
- "Can I stop it recording message content?" Yes, via the OpenInference `TraceConfig`. Section 10.2 covers the privacy switches.
- Never show `opentelemetry-instrumentation-openai-v2` on screen.

---

## Lecture 3.6 — Break it: orphan spans, missing context and double counting

| Field | Value |
|---|---|
| ID | 3.6 |
| Type | DM (demo: three breaks, three tests) |
| Target duration | 6:00 (~570 spoken words, about 4:04 of talking at 140 wpm, plus test output) |
| Learning objectives | 1. Recognise an orphan span caused by work that runs without the trace context, and fix it by carrying the context. 2. Recognise a tool span that isn't under the agent, and fix the call structure. 3. Recognise double counting from two instrumentations of one call, and keep one span with usage per call. |
| Prerequisites | 3.2 to 3.5 |
| Files used | `03-code/tests/integration/test_spans.py` (`test_broken_orphan_span_is_detectable`, `test_no_orphan_spans`, `test_tool_spans_are_children_of_agent`, `test_one_generation_per_model_call`, `test_double_instrumentation_is_idempotent`), `03-code/app/server.py` (`asyncio.to_thread`), `03-code/telemetry/openinference_setup.py` |

**Recording note:** each break is shown as code on a slide and as a real test. The orphan is demonstrated by `test_broken_orphan_span_is_detectable`, which builds one on purpose; the other two breaks are refactors someone might make, shown on slides, and caught by the named tests. The test run in the DEMO cue was captured on 2026-10-02. Tint broken slides red and passing tests green.

### Script

[AVATAR]
Instrumentation doesn't crash when it's wrong. It produces traces that look fine and lie. Which of these have you already shipped? Here are the three lies I see most: a span with no parent, a tool that looks like it ran on its own, and a bill that's exactly double. And for each one, the test in Atlas's repo that catches it.

[SLIDE 1: Break 1: work without the trace context]
```python
# someone moves lookup_ticket to a worker thread, and the tool starts its own span there
result = await loop.run_in_executor(pool, _lookup_ticket_blocking, ticket_id)
```
- The current span lives in `contextvars`
- `await` and `asyncio.create_task` carry it; a plain thread pool does not
- The worker starts with an empty context, so its span has no parent

Break one. Someone notices `lookup_ticket` blocks on I/O and moves it to a thread pool. Reasonable. So why does the trace break? Because the current span lives in a context variable. `await` carries it, `create_task` copies it, and a plain thread pool starts each job with an empty context. The tool's span looks for a current span, finds none, and becomes a root of its own trace: no tenant, no user, no cost context. An orphan.

[SCREEN: VS Code, `tests/integration/test_spans.py`, `test_broken_orphan_span_is_detectable`. Highlight `otel_context.attach(otel_context.Context())` and the two asserts.]

[CODE: excerpt of `test_broken_orphan_span_is_detectable`]
```python
    with tr.start_as_current_span("invoke_agent atlas"):
        token = otel_context.attach(
            otel_context.Context()
        )  # simulate a task without propagated context
        try:
            with tr.start_as_current_span("execute_tool lookup_ticket"):
                pass
        finally:
            otel_context.detach(token)
    spans = exp.get_finished_spans()
    tool = next(s for s in spans if s.name.startswith("execute_tool"))
    assert tool.parent is None  # orphan: the trace waterfall would show two traces
    assert len({s.get_span_context().trace_id for s in spans}) == 2
```

This test builds an orphan on purpose. Inside the agent span, it swaps in an empty context, exactly what a worker thread sees, and starts the tool span. Parent: none. Two trace IDs for one request. In Langfuse, that's a separate one-span trace named `execute_tool lookup_ticket`.

The fix: carry the context across. `asyncio.to_thread` copies it for you, and it's what Atlas's server uses to run the agent off the event loop. With a raw executor, capture `context.get_current()` first and pass it to `start_as_current_span` as the `context` argument.

[SLIDE 2: Break 2: tool span outside the agent span]
```python
def run(self, message, **ids):
    with tracer.start_as_current_span("invoke_agent atlas"):
        plan = self._plan(message)          # model calls happen here...
    for call in plan.pending_tool_calls:    # ...but tools run after the block closed
        self._run_tool(call)
```
- Fix: nest the code the way the causality nests

Break two. A refactor moves tool execution after the agent's `with` block. The code still works. The trace doesn't. The agent span ends, then the tool span starts with no current span, so it's a root again. Anyone reading the agent's trace sees a model call that asked for a tool, and no tool. They conclude it never ran. It did; it's just filed under a different trace. The fix is structural: if the tool ran because of the agent, it runs inside the agent's block.

[SLIDE 3: Break 3: one call, two spans with usage]
- An auto-instrumentor records the model call (3.5)
- The manual generation span records the same call, with usage
- Any backend that sums usage over spans now reports twice the tokens and dollars
- Your $56.28 day would read as twice that

Break three, and this one costs money on paper. OpenInference is on, and our own generation span is on, and both carry usage. Every model call now produces two spans claiming the same tokens. Any dashboard that sums usage across spans, and they all do, shows twice your real spend. Your fifty-six-dollar day reads as twice that. What would you do with a bill that doubled overnight? Probably cut features, to fix a bill that doesn't exist. The fix is a decision: one model call, one span carrying usage. Atlas guards this three ways. It never turns OpenInference on by default. `instrument_openai` refuses to instrument twice. And its Langfuse export filter only forwards Atlas's own spans.

[SCREEN: Terminal in `03-code/`.]

[CODE: run the five tests that pin these breaks]
```bash
python -m pytest -q tests/integration/test_spans.py -k "orphan or children_of_agent or one_generation or double_instrumentation"
```

[DEMO: Output ends with `5 passed, 14 deselected, 1 warning in 0.15s`.]

[SCREEN: VS Code, the three regression tests side by side: `test_no_orphan_spans`, `test_tool_spans_are_children_of_agent`, `test_one_generation_per_model_call`.]

[CODE: excerpt of `test_one_generation_per_model_call`]
```python
    body = _chat(client, "Where is my ticket TCK-100231?")
    spans = _spans(client)
    gens = [s for s in spans if s.attributes.get(ga.LF_OBS_TYPE) == "generation"]
    agent = _by_name(spans, "invoke_agent atlas")[0]
    assert len(gens) == body["steps"] == 2
    assert (
        sum(s.attributes[g.GEN_AI_USAGE_INPUT_TOKENS] for s in gens)
        == agent.attributes[g.GEN_AI_USAGE_INPUT_TOKENS]
    )
```

All five green. And here's how each lie is caught. `test_no_orphan_spans`: exactly one root per request, named `invoke_agent atlas`. `test_tool_spans_are_children_of_agent`: every tool span sits under a step of the agent, in the same trace. And `test_one_generation_per_model_call`: one generation span per model call, and their input tokens add up to exactly the agent's total. Make test runs them on every change.

[SLIDE 4: Symptom → cause → fix]
| Symptom | Cause | Fix |
|---|---|---|
| One-span trace named `execute_tool ...` | Work on a thread without context | `asyncio.to_thread`, or pass `context=` |
| Agent trace shows a tool request but no tool | Tool ran after the agent block closed | Nest the code like the causality |
| Tokens and cost exactly 2× expected | Same call instrumented twice | One call, one span with usage |

[AVATAR]
Screenshot this table. All three lies look like healthy traces until you count roots, check parents and compare the bill. Now you have tests that do the counting for you.

[SLIDE 5: Recap]
- Lost context makes orphan root spans
- Code outside the block loses its parent
- Two instrumentations double every token

**Recap:** Work that runs without the trace context creates orphan root spans, tools run outside the agent block lose their parent, and instrumenting one call twice doubles every token, and the integration tests in `test_spans.py` catch all three.

**Transition:** Lab 2: take `check_shipment`'s span apart and write the test that proves it's correct.

### Speaker notes: common student mistakes / Q&A

- "Why does `asyncio.create_task` work but the thread pool doesn't?" Tasks copy the current `contextvars` context on creation; threads don't. `asyncio.to_thread` copies it explicitly, which is why `app/server.py` uses it.
- Mistake: "fixing" break 1 by starting the span in the caller and passing the span object into the thread. It works, but the span then includes the queueing time. Pass the context, start the span where the work happens.
- Break 3 also appears with Langfuse's `langfuse.openai` drop-in client plus OpenInference. Same rule: one instrumentation per call.
- FastAPI 0.142 ships its own OpenTelemetry server spans; `app/server.py` turns them off so `invoke_agent atlas` stays the only root, which is what `test_no_orphan_spans` asserts.

---

## Lecture 3.7 — Lab 2: Instrument a new tool end to end

| Field | Value |
|---|---|
| ID | 3.7 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 total (1:30 video, ~180 spoken words, about 1:17 of talking at 140 wpm) |
| Learning objectives | 1. Read `check_shipment`'s `execute_tool` span: name, attributes, arguments, result and parent. 2. Write an integration test asserting its attributes and parent. 3. See the span in the console exporter and in Langfuse. |
| Prerequisites | 3.1 to 3.6 |
| Files used | `04-labs/lab-02-instrument-tool.md`, `03-code/app/tools.py` (`check_shipment(tracking_id)`), `03-code/app/agent.py` (`_run_tool`), `03-code/tests/integration/test_spans.py` |

### Script

[AVATAR]
Lab two. `check_shipment` is Atlas's newest tool, and so far nothing proves its span is right. If it silently lost its arguments tomorrow, who would notice? You will, because you're going to write the test. Forty-five minutes to an hour.

[SCREEN: VS Code, `04-labs/lab-02-instrument-tool.md`. Scroll the steps.]

Step one: ask "Where is shipment SHP-4471120?" with the console exporter on, and check the `execute_tool check_shipment` span against Lecture 3.3, including the `tracking_id` argument.

Step two: the test. Copy the pattern from `test_ticket_question_emits_tagged_tool_span`: tool name, arguments, and a parent step under the agent.

[SCREEN: Scroll to the stretch goal and deliverables.]

The stretch goal pins the failure path with a second test. Deliverables: the test output and a Langfuse screenshot of the span.

[SLIDE 1: You can now]
- Build a trace by hand and read raw spans
- Tag spans with the GenAI conventions
- Catch orphans and double counting with tests

[AVATAR]
You can now build a trace by hand, tag spans with the standard names, and catch the three instrumentation lies with tests. Run make test before and after: that's the loop for every span you'll ever add.

**Recap:** Lab 2 reads `check_shipment`'s span, pins its name, arguments and parent with an integration test, and captures it in Langfuse.

**Transition:** A six-question quiz on tracing and the conventions, then Section 4: what Langfuse adds on top of these spans.

### Speaker notes: common student mistakes / Q&A

- Shipment IDs look like `SHP-` plus six to eight digits; the mock calls `check_shipment` for a question that contains the word "shipment" and a valid `SHP-` ID. Without an ID it asks for one instead.
- Students put the assertion on the agent as parent; the tool's parent is the `step n` span, whose parent is the agent (same as the 3.4 test).
- `set_status(Status(StatusCode.ERROR, msg))` needs `from opentelemetry.trace import Status, StatusCode`. Atlas already marks failed tools with ERROR status and a WARNING Langfuse level in `_run_tool`.
- The lab file is the source of truth for the exact steps and the stretch goal; this intro only names the shape.

---

## Lecture 3.8 — Quiz: Tracing and semantic conventions

| Field | Value |
|---|---|
| ID | 3.8 |
| Type | QZ (quiz with short video intro) |
| Target duration | 3:00 total (1:00 video, ~105 spoken words, about 0:45 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of spans, context and sampling. 2. Check recall of the GenAI naming rules and the three instrumentation lies. |
| Prerequisites | 3.1 to 3.7 |
| Files used | `06-assessments/quizzes/section-03.md` |

### Script

[AVATAR]
Six questions. Three minutes.

[SLIDE 1: Section 3 quiz: what's covered]
- Parent IDs and how the tree is built
- Simple vs batch processor; console vs OTLP
- Span names: `chat gpt-4.1-mini`, `execute_tool ...`, `invoke_agent ...`
- Which usage attributes people forget (cached, reasoning)
- What auto-instrumentation can't see
- Symptom → cause for orphans and double counting

One on how the tree is built. One on processors and exporters. One on span naming. One on the usage attributes people forget. One on what an auto-instrumentor can't see. And one that gives you a symptom, like "cost is exactly double," and asks for the cause.

If a question mentions a thread, think "context didn't follow." If it mentions a bill, think "count the spans per call."

**Recap:** The quiz checks the span tree, exporters, GenAI naming, auto-instrumentation limits and the three lies.

**Transition:** Next, Section 4: how Langfuse sits on top of these exact spans, and what it adds that OpenTelemetry doesn't have.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: "Which processor for a network exporter?" Batch.
- Second most missed: the span name for a tool call. `execute_tool {name}`, not the tool name alone.
