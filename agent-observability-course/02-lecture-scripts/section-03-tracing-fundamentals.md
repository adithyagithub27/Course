# Section 3: Tracing Fundamentals and the GenAI Semantic Conventions

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** ≈52 min (8 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on langfuse 4.15 / opentelemetry-sdk 1.45 / semconv 0.66b0 (GenAI attributes are incubating, names may change) / openinference-instrumentation-openai 0.1.61; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only. Code-along lectures are paced below 140 words per minute.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 3.1 | Traces, spans and context in five minutes | SL | 6:00 | ~650 |
| 3.2 | Code-along: manual OpenTelemetry instrumentation of Atlas | SC | 10:00 | ~625 |
| 3.3 | GenAI semantic conventions: naming things so tools understand them | SL | 8:00 | ~750 |
| 3.4 | Code-along: tag every LLM, tool and agent span correctly | SC | 9:00 | ~450 |
| 3.5 | Auto-instrumentation with OpenInference | SC | 6:00 | ~400 |
| 3.6 | Break it: orphan spans, missing context and double counting | DM | 6:00 | ~575 |
| 3.7 | Lab 2: Instrument a new tool end to end | LAB | 4:00 (1:30 video) | ~225 |
| 3.8 | Quiz: Tracing and semantic conventions | QZ | 3:00 (1:00 video) | ~100 |

**API guardrails for this section (do not deviate on screen):** attribute constants come from `opentelemetry.semconv._incubating.attributes.gen_ai_attributes` (imported as `g`), never typed as raw strings in application code. Span names follow the conventions: `invoke_agent atlas`, `chat gpt-4.1-mini`, `execute_tool lookup_ticket`. Auto-instrumentation is `OpenAIInstrumentor` from `openinference.instrumentation.openai`; never show `opentelemetry-instrumentation-openai-v2` installed, imported or running (it failed to import at verification time). The single "not used" line on slide 1 of 3.5 is the only permitted mention. Say "incubating, names may change" once per lecture that shows a `gen_ai.*` name.

---

## Lecture 3.1 — Traces, spans and context in five minutes

| Field | Value |
|---|---|
| ID | 3.1 |
| Type | SL (slides) |
| Target duration | 6:00 (~650 spoken words, about 4:39 of talking at 140 wpm) |
| Learning objectives | 1. Define trace, span, parent/child, attributes, events and status. 2. Explain context propagation and why a span "knows" its parent. 3. Describe head and tail sampling and when each applies. |
| Prerequisites | Section 2 |
| Files used | Diagram: one Atlas request as a trace (slides 2, 4, 6) |

### Script

[AVATAR]
In Lecture 2.3 you looked at a trace and it made sense. Root, children, timings. Now here's the uncomfortable question: how did the tool span know it belonged to that agent span? Nobody passed it an ID. [PAUSE] Six words explain the whole thing, and one mechanism makes it work. Let's do the six words first.

[SLIDE 1: Six words]
- Trace: everything that happened for one request
- Span: one unit of work with a start and an end
- Parent/child: which span caused which
- Attributes: key-value facts about a span
- Events: timestamped moments inside a span
- Status: OK, ERROR or unset

A trace is everything that happened for one request, identified by one trace ID. A span is one unit of work with a start time and an end time. Spans nest: a parent causes children. Attributes are facts about a span, as key-value pairs. Events are timestamped moments inside a span, like "step limit reached at 14:02:07." And status says whether the work succeeded.

[SLIDE 2: One Atlas request as a trace]
Diagram, waterfall. Top bar `invoke_agent atlas` 2.8 s. Under it, `search_knowledge_base` 40 ms, then `chat gpt-4.1-mini` 2.6 s, then `execute_tool lookup_ticket` 120 ms, then a second `chat gpt-4.1-mini` 0.9 s. Trace ID shown at the top right.

Here's the VPN request from 2.3 drawn as a waterfall. One trace. The agent span at the top, two point eight seconds. Under it, the retriever, a model call, a tool call, another model call. Time runs left to right. Nesting runs top to bottom. You can see instantly that the first model call is where the time went.

[SLIDE 3: A span, up close]
```text
name:        chat gpt-4.1-mini
trace_id:    0xc8e0b7a1c432fda1dd0b3d28692756c3
span_id:     0x21c0b128c8a0a5b9
parent_id:   0xa25f5e46855e69ba
start/end:   14:02:04.619 → 14:02:07.220
attributes:  gen_ai.request.model=gpt-4.1-mini, gen_ai.usage.input_tokens=3012, ...
events:      (none)
status:      UNSET
```

Zoom in on one span. It has a name. It has the trace ID shared by every span in this request. It has its own span ID and, crucially, a parent ID. That parent ID is the entire tree. There's no separate tree structure stored anywhere; the backend rebuilds the waterfall from parent IDs. Then attributes, events and status.

[SLIDE 4: Context propagation]
Diagram: a stack of boxes labelled "current context". Step 1: empty. Step 2: `invoke_agent atlas` is pushed; it's the current span. Step 3: `chat gpt-4.1-mini` starts, reads the current span, sets it as parent, and is pushed. Step 4: it ends and is popped; `invoke_agent atlas` is current again.

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

One rule, though. Never sample the cost signal. If you keep one trace in ten, you've lost ninety percent of your dollars. Cost is counted from every request, as a metric, regardless of what traces you keep. Section nine builds that.

[SLIDE 7: What a trace answers that logs can't]
- Which spans belong to this request? (trace ID)
- What caused what? (parent ID)
- Where did time go? (start and end, nested)
- What were the facts? (attributes)
- What happened at 14:02:07? (events)

Put together: a trace tells you which work belonged to a request, what caused what, where time went, what the facts were and what happened when. Logs give you lines. Traces give you structure. Lecture 5.5 comes back to when you want each.

[AVATAR]
Six words and one mechanism. Trace, span, parent, attributes, events, status, held together by a current-span context that follows your code. Now let's write it.

**Recap:** A trace is a tree of spans linked by parent IDs, each carrying attributes, events and status; the tree is built automatically by a context that tracks the current span, and sampling decides which traces to keep, never which costs to count.

**Transition:** Next, you strip Atlas back to plain Python and add OpenTelemetry by hand, span by span.

### Speaker notes: common student mistakes / Q&A

- "Is a trace the same as a Langfuse trace?" Yes, with extras. Langfuse adds observation types, sessions and users on top of the same OTel spans. Section 4.1.
- "Do spans have to nest?" A trace can be a flat list of root spans, but then you've lost causality. Orphans are the most common instrumentation bug; 3.6 shows them.
- Students confuse events with logs. An event is attached to a span and inherits its trace and span IDs; a log line has to be correlated by hand (5.5).
- Keep this lecture free of `gen_ai.*` names. 3.3 introduces them.

---

## Lecture 3.2 — Code-along: manual OpenTelemetry instrumentation of Atlas

| Field | Value |
|---|---|
| ID | 3.2 |
| Type | SC (code-along) |
| Target duration | 10:00 (~625 spoken words, about 4:28 of talking at 140 wpm, plus typing and console output) |
| Learning objectives | 1. Build `setup_tracing()` with a `TracerProvider`, resource attributes and a `ConsoleSpanExporter`. 2. Wrap the agent run and the model call in `tracer.start_as_current_span` and read the nested spans in the console. 3. Switch to an OTLP exporter pointed at Langfuse with a `BatchSpanProcessor`. |
| Prerequisites | 3.1, Section 2 |
| Files used | You type: `03-code/telemetry/otel_setup.py`, edits to `03-code/app/agent.py`. Reference: the same files in the repo (reset with `git checkout` if you want to type from scratch). |

**Recording note:** start from a copy of `otel_setup.py` reduced to imports, so every line on screen is typed. The repo version has extra branches for `file` and `langfuse` exporters; mention, don't type.

### Script

[AVATAR]
You've seen the trace. Now you're going to make one from nothing. Three parts: a provider that owns the pipeline, an exporter that decides where spans go, and two `with` statements in the agent. About forty lines, and you'll read the raw spans in your terminal before any UI is involved.

[SCREEN: VS Code, `telemetry/otel_setup.py`, reduced to imports.]

[CODE: step 1, imports]
```python
"""OpenTelemetry setup for Atlas (Lecture 3.2)."""

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
```

Imports first. `trace` is the API: how application code gets a tracer. Everything under `sdk` is the implementation: the provider, the resource, the processors and exporters. Keep that split in your head. Application code imports the API; only setup code imports the SDK.

[CODE: step 2, the resource]
```python
def _resource() -> Resource:
    return Resource.create(
        {
            "service.name": "atlas",
            "service.version": os.getenv("ATLAS_VERSION", "dev"),
            "deployment.environment": os.getenv("DEPLOYMENT_ENV", "dev"),
        }
    )
```

The resource describes who is emitting spans. Service name, version and environment. These attach to every span automatically, so you can filter a backend to "atlas in production" without setting anything per span. In Section thirteen, `service.version` becomes the release tag you annotate dashboards with.

[CODE: step 3, the provider and the console exporter]
```python
def setup_tracing(exporter: str | None = None) -> TracerProvider:
    exporter = exporter or os.getenv("OTEL_EXPORTER", "console")
    provider = TracerProvider(resource=_resource())

    if exporter == "console":
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return provider
```

Now `setup_tracing`. Create a `TracerProvider` with our resource. Add a span processor. A processor decides when to hand spans to an exporter; the exporter decides where they go. For the console we use `SimpleSpanProcessor`, which exports each span the moment it ends. Then set it as the global provider, so `trace.get_tracer` anywhere in the app finds it.

[SCREEN: VS Code, `app/agent.py`. Top of file and the `run` method of `AtlasAgent`.]

[CODE: step 4, get a tracer and wrap the run]
```python
from opentelemetry import trace

tracer = trace.get_tracer("northwind.atlas")


class AtlasAgent:
    ...

    def run(self, message: str, *, tenant: str, user_id: str, session_id: str) -> AgentResult:
        with tracer.start_as_current_span("invoke_agent atlas") as agent_span:
            agent_span.set_attribute("northwind.tenant", tenant)
            result = self._loop(message)
            agent_span.set_attribute("atlas.steps", result.steps)
            return result
```

Over in the agent. Get a tracer once at module level, named after the code that owns it. Then, in `run`, one `with` statement around the whole loop. The span is named `invoke_agent atlas`; that name follows a convention you'll meet next lecture. Inside, set an attribute for the tenant, run the loop, and record how many steps it took. When the `with` block exits, the span ends, and if the loop raised, the span records the exception and sets error status for you.

[CODE: step 5, wrap the model call]
```python
    def _call_model(self, messages: list[dict]) -> ModelResponse:
        with tracer.start_as_current_span(f"chat {self.model}") as span:
            response = self.client.chat.completions.create(model=self.model, messages=messages, tools=self.tool_specs)
            span.set_attribute("atlas.input_tokens", response.usage.prompt_tokens)
            span.set_attribute("atlas.output_tokens", response.usage.completion_tokens)
            return response
```

And one more around the model call. Named `chat` plus the model. Because this runs inside `run`, the current span is the agent span, so this becomes its child. No IDs passed. For now the token attributes have our own names; next lecture they get standard ones.

[SCREEN: `app/server.py`, startup. Add `setup_tracing()` at import time or in the lifespan.]

[CODE: step 6, call it at startup]
```python
from telemetry.otel_setup import setup_tracing

setup_tracing()  # before the agent is created
```

Call `setup_tracing` once, at startup, before any tracer is used. Order matters: a tracer fetched before the provider is set is a no-op tracer forever.

[SCREEN: Terminal 1: `OTEL_EXPORTER=console OFFLINE=1 make run`. Terminal 2: the curl from Lecture 2.3.]

[DEMO: Two JSON blocks print in Terminal 1. First `chat gpt-4.1-mini` with a `parent_id`, then `invoke_agent atlas` with `"parent_id": null`. Both share the same `trace_id`. The resource block shows `service.name: atlas`.]

Run with the console exporter and send the VPN question. Two spans print as JSON. Read them. The model call prints first, because it ended first. It has a parent ID. The agent span prints second, with parent ID null; it's the root. Same trace ID on both. And at the bottom of each, the resource: service name atlas. That's a trace, in your terminal, with no backend.

[PAUSE]

[CODE: step 7, OTLP to Langfuse]
```python
import base64
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    if exporter == "otlp":
        auth = base64.b64encode(
            f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()
        ).decode()
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=f"{os.environ['LANGFUSE_BASE_URL']}/api/public/otel/v1/traces",
                    headers={"Authorization": f"Basic {auth}"},
                )
            )
        )
```

Now the real destination. Add an `otlp` branch. OTLP is OpenTelemetry's wire protocol, and Langfuse accepts it at slash api slash public slash otel. Authenticate with basic auth built from your two keys. And this time use `BatchSpanProcessor`, which queues spans and sends them in batches on a background thread. Never use the simple processor with a network exporter; it would block your request on every span.

[SCREEN: Terminal 1: `OTEL_EXPORTER=otlp OFFLINE=1 make run`. Send the curl. Browser: Langfuse traces list shows a new trace `invoke_agent atlas` with one child.]

[DEMO: The trace appears in Langfuse after a few seconds, with two plain spans, no types, no usage yet.]

Switch the exporter to OTLP and send the question again. A few seconds later, there it is in Langfuse. Two spans, nested correctly. Notice what's missing compared to Lecture 2.3: no observation types, no usage, no cost. Those come from attributes, which is the next two lectures.

[SLIDE 1: The pipeline you just built]
- `Resource` → who is emitting (service.name, version, environment)
- `TracerProvider` → owns the pipeline; set once, globally
- `SpanProcessor` → when to export: Simple (now) vs Batch (queued)
- `SpanExporter` → where to: Console, OTLP, later file and Langfuse SDK
- `tracer.start_as_current_span(name)` → the only line application code needs

[AVATAR]
Here's the whole pipeline on one slide. Resource, provider, processor, exporter, and one `with` statement in the application. Every other tracing tool you'll ever meet is a variation of these five boxes.

**Recap:** `setup_tracing()` builds a `TracerProvider` with resource attributes and either a console or a batched OTLP exporter, and two `start_as_current_span` blocks in `AtlasAgent` give you a nested trace with no IDs passed by hand.

**Transition:** The spans exist, but Langfuse shows them as plain boxes. Next, the standard attribute names that turn a box into a model call with tokens and cost.

### Speaker notes: common student mistakes / Q&A

- Mistake: calling `setup_tracing()` after `tracer = trace.get_tracer(...)` ran at import time in another module. Symptom: no spans at all. Fix: call setup first, or fetch the tracer lazily.
- Mistake: `SimpleSpanProcessor` with `OTLPSpanExporter`. It works, but every request blocks on a network round trip per span.
- Mistake: forgetting `provider.shutdown()` or `force_flush()` in short scripts. Batched spans are lost when the process exits before the flush. The FastAPI lifespan in `server.py` calls shutdown; `simulator/replay.py` calls `force_flush()` at the end.
- "Why the `_incubating` warning in some imports later?" The GenAI conventions are not stable yet. It's expected; 3.3 explains.
- The OTLP endpoint path for Langfuse is documented in the Langfuse OpenTelemetry docs; if it has changed at recording time, update the on-screen line and the repo together.

---

## Lecture 3.3 — GenAI semantic conventions: naming things so tools understand them

| Field | Value |
|---|---|
| ID | 3.3 |
| Type | SL (slides) |
| Target duration | 8:00 (~750 spoken words, about 5:21 of talking at 140 wpm) |
| Learning objectives | 1. Explain what semantic conventions are and why standard names buy portability. 2. Name the core `gen_ai.*` attributes for model calls, tools and agents, and the span naming rule. 3. State what "incubating" means for your code. |
| Prerequisites | 3.2 |
| Files used | `03-code/telemetry/genai_attrs.py` (shown on one slide, typed in 3.4) |

### Script

[AVATAR]
Your span from the last lecture had an attribute called `atlas.input_tokens`. Mine had `llm.tokens.prompt`. The team next door has `tokens_in`. Now build a cost dashboard that works for all three. [PAUSE] You can't. That's the problem semantic conventions solve, and it's why a vendor can show you cost without you telling it your schema.

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

[SLIDE 3: Model call attributes]
```text
gen_ai.operation.name          "chat"
gen_ai.provider.name           "openai"
gen_ai.request.model           "gpt-4.1-mini"
gen_ai.response.model          "gpt-4.1-mini-2025-04-14"
gen_ai.usage.input_tokens      3012
gen_ai.usage.output_tokens     142
gen_ai.usage.cache_read.input_tokens     0
gen_ai.usage.reasoning.output_tokens     0
gen_ai.response.finish_reasons ["tool_calls"]
```
Footer: incubating, names may change.

Now the attributes on a model call. Operation name, `chat`. Provider name, `openai`. The model you asked for, and the model that actually answered; they differ when the provider resolves an alias to a dated snapshot, and that matters when a snapshot changes behaviour. Then usage. Input tokens, output tokens, and two that most people forget: cached input tokens and reasoning output tokens. Both are priced differently, and both are invisible if you only record the two big numbers. Section six leans hard on those two.

[SLIDE 4: Tool call attributes]
```text
gen_ai.operation.name       "execute_tool"
gen_ai.tool.name            "lookup_ticket"
gen_ai.tool.call.id         "call_8f2..."
gen_ai.tool.call.arguments  {"ticket_id": "INC-2231"}
gen_ai.tool.call.result     {"status": "open", ...}   (redacted, truncated)
```

For a tool call: operation `execute_tool`, the tool's name, the call ID the model assigned, the arguments the model chose, and the result. Two cautions on the last two. Arguments and results are content, so they can hold personal data; you'll mask them in Section ten. And results can be huge; truncate before you attach, or your telemetry costs more than your model calls.

[SLIDE 5: Agent and conversation attributes]
```text
gen_ai.operation.name    "invoke_agent"
gen_ai.agent.name        "atlas"
gen_ai.agent.version     "v1"     (your prompt or code version)
gen_ai.conversation.id   "sess-demo-1"
```

For the agent span: operation `invoke_agent`, agent name, and an agent version, which is a useful place to put your prompt version. And `gen_ai.conversation.id`, which is where a session ID goes in the standard. Langfuse has its own session concept on top; you'll set both in Section four.

[SLIDE 6: Constants, not strings]
```python
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g

span.set_attribute(g.GEN_AI_REQUEST_MODEL, "gpt-4.1-mini")
span.set_attribute(g.GEN_AI_USAGE_INPUT_TOKENS, 3012)
span.set_attribute(g.GEN_AI_OPERATION_NAME, g.GenAiOperationNameValues.CHAT.value)
```
- `_incubating` in the path is deliberate: these names are not stable yet
- A constant renames with the package; a string typo is a silent hole in your dashboard

In code, never type these as strings. Import the constants. The module path has `_incubating` in it, on purpose. It's a signal that these names are not frozen. Two reasons to use the constants anyway. If a name changes in a future release, your code changes with the package, in one place. And a typo in a string is a silent hole in a dashboard; a typo in a constant is an error at import time.

[SLIDE 7: What "incubating" means for you]
- Stable conventions (HTTP, DB) have compatibility guarantees. GenAI does not yet.
- Expect renames between minor versions; pin the package, read the changelog
- Backends may support a range of old and new names; Langfuse maps `gen_ai.*` today
- Say it on every dashboard: "GenAI semconv 0.66; names may change"

What does incubating mean in practice? Stable conventions come with compatibility promises. GenAI doesn't yet. Names have already been renamed once; `gen_ai.system` became `gen_ai.provider.name`, for instance, and both constants exist right now. So pin the package version, read the changelog when you bump it, and keep the footer you see on this slide on your own dashboards. It's honest, and it saves an argument later.

[SLIDE 8: Why this buys portability]
Diagram: Atlas emits one span with `gen_ai.usage.input_tokens=3012`. Arrows to Langfuse ("shows usage, computes cost"), Phoenix ("shows tokens"), Grafana via collector ("gen_ai.client.token.usage metric"), Datadog ("LLM Observability"). Caption: same span, four backends, zero code changes.

Here's the payoff. Emit one span with standard names, and Langfuse shows usage and computes cost from it. Phoenix shows the tokens. A collector can turn them into the standard metric `gen_ai.client.token.usage` for Grafana. Datadog reads them too. Same span, four backends, no code changes. Section twelve is that diagram, live.

[SLIDE 9: The conventions name metrics too]
```python
from opentelemetry.semconv._incubating.metrics import gen_ai_metrics as gm

gm.GEN_AI_CLIENT_TOKEN_USAGE                    # "gen_ai.client.token.usage"  (histogram, by gen_ai.token.type)
gm.GEN_AI_CLIENT_OPERATION_DURATION             # "gen_ai.client.operation.duration"
gm.GEN_AI_CLIENT_OPERATION_TIME_TO_FIRST_CHUNK  # "gen_ai.client.operation.time_to_first_chunk"
```
Footer: incubating, names may change.

The conventions don't stop at spans. There are standard metric names too, in a sibling module. Token usage as a histogram, split by token type. Operation duration. Time to first chunk. You won't emit these by hand; the collector in Section thirteen derives them from your spans, and Section nine's Grafana dashboard reads them. But when you see `gen_ai.client.token.usage` on a dashboard you didn't build, you'll know it came from the same spans you're tagging now.

[SLIDE 10: What the conventions don't cover]
- Cost in dollars: not a standard attribute; Langfuse computes it or you set `cost_details` (4.2)
- Your business dimensions: tenant, feature, ticket type → your own namespace, e.g. `northwind.tenant`
- Quality scores: backend feature, not a span attribute (4.5)

And what they don't cover. Dollars. There's no standard cost attribute; the backend computes it from tokens and a price table, or you set it explicitly, which you'll do in 4.2. Your business dimensions, like tenant and feature. Those go in your own namespace; ours is `northwind.`. And quality scores, which are a backend feature.

[AVATAR]
So: standard names for models, tokens, tools and agents. Constants, never strings. And the word incubating on every screen that shows them. Now let's put them on Atlas's spans.

**Recap:** The GenAI semantic conventions give models, token usage, tool calls and agents standard attribute names and span names, imported as constants from the incubating semconv package, so any backend can compute cost and draw the trace without knowing your schema.

**Transition:** Next, a code-along: helpers in `genai_attrs.py` that tag every model, tool and agent span in one line each.

### Speaker notes: common student mistakes / Q&A

- "Why does the import path say `_incubating`?" Because the conventions are not stable. It's the officially documented import path for these names at this version. Don't try to avoid it.
- "Should I record `gen_ai.input.messages`?" The conventions define it and `gen_ai.output.messages`, but full message content is opt-in in most instrumentors for privacy and size reasons. We record content via Langfuse input/output with masking (4.6, 10.2), not as raw span attributes.
- Students ask about OpenInference's `llm.token_count.prompt` names. Different convention, same idea; OpenInference is what auto-instrumentation emits (3.5) and Langfuse understands both.
- Keep the footer visible whenever a `gen_ai.*` name is on screen.

---

## Lecture 3.4 — Code-along: tag every LLM, tool and agent span correctly

| Field | Value |
|---|---|
| ID | 3.4 |
| Type | SC (code-along) |
| Target duration | 9:00 (~450 spoken words, about 3:13 of talking at 140 wpm, plus typing and console output) |
| Learning objectives | 1. Write three helpers in `telemetry/genai_attrs.py`: `set_agent_attrs`, `set_llm_attrs`, `set_tool_attrs`. 2. Apply them in `AtlasAgent` for the agent span, each model call and each tool call. 3. Verify the attributes in console exporter output and in a test. |
| Prerequisites | 3.2, 3.3 |
| Files used | You type: `03-code/telemetry/genai_attrs.py`, edits to `03-code/app/agent.py`. Reference: repo versions. Test: `03-code/tests/integration/test_spans.py`. |

### Script

[AVATAR]
Three helpers, three call sites, and Atlas's spans go from "boxes with timings" to "model calls with usage, tool calls with arguments, an agent with a conversation ID." Let's type them.

[SCREEN: VS Code, new file `telemetry/genai_attrs.py`.]

[CODE: step 1, imports and the agent helper]
```python
"""Set gen_ai.* attributes per semconv 0.66 (incubating; names may change)."""

import json
from typing import Any

from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as g
from opentelemetry.trace import Span

MAX_CONTENT_CHARS = 2000


def set_agent_attrs(span: Span, *, name: str, conversation_id: str, version: str = "v1") -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, g.GenAiOperationNameValues.INVOKE_AGENT.value)
    span.set_attribute(g.GEN_AI_AGENT_NAME, name)
    span.set_attribute(g.GEN_AI_AGENT_VERSION, version)
    span.set_attribute(g.GEN_AI_CONVERSATION_ID, conversation_id)
```

Import the constants module as `g`; you'll type `g.` a lot. One constant for truncation. Then the agent helper. Operation name from the enum, so even the value `invoke_agent` isn't a string you typed. Agent name, agent version, conversation ID.

[CODE: step 2, the model call helper]
```python
def set_llm_attrs(span: Span, *, request_model: str, response: Any, provider: str = "openai") -> None:
    usage = response.usage
    span.set_attribute(g.GEN_AI_OPERATION_NAME, g.GenAiOperationNameValues.CHAT.value)
    span.set_attribute(g.GEN_AI_PROVIDER_NAME, provider)
    span.set_attribute(g.GEN_AI_REQUEST_MODEL, request_model)
    span.set_attribute(g.GEN_AI_RESPONSE_MODEL, response.model)
    span.set_attribute(g.GEN_AI_USAGE_INPUT_TOKENS, usage.prompt_tokens)
    span.set_attribute(g.GEN_AI_USAGE_OUTPUT_TOKENS, usage.completion_tokens)

    details = getattr(usage, "prompt_tokens_details", None)
    if details and details.cached_tokens:
        span.set_attribute(g.GEN_AI_USAGE_CACHE_READ_INPUT_TOKENS, details.cached_tokens)
    out_details = getattr(usage, "completion_tokens_details", None)
    if out_details and out_details.reasoning_tokens:
        span.set_attribute(g.GEN_AI_USAGE_REASONING_OUTPUT_TOKENS, out_details.reasoning_tokens)

    span.set_attribute(g.GEN_AI_RESPONSE_FINISH_REASONS, [c.finish_reason for c in response.choices])
```

The model call helper takes the request model and the raw response. Operation `chat`, provider, request model, and the response model from the API, which is the dated snapshot. Then the two headline usage numbers.

Then the two people forget. On the Chat Completions API, cached tokens live at `usage.prompt_tokens_details.cached_tokens`, and reasoning tokens at `usage.completion_tokens_details.reasoning_tokens`. Both are optional, so guard them. The mock returns them too, so offline traces have the same shape.

Finish reasons last. `tool_calls` versus `stop` tells you, across a day, how often the model chose to act rather than answer.

[CODE: step 3, the tool helper]
```python
def _clip(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text if len(text) <= MAX_CONTENT_CHARS else text[:MAX_CONTENT_CHARS] + "...[truncated]"


def set_tool_attrs(span: Span, *, name: str, call_id: str, arguments: Any, result: Any = None) -> None:
    span.set_attribute(g.GEN_AI_OPERATION_NAME, g.GenAiOperationNameValues.EXECUTE_TOOL.value)
    span.set_attribute(g.GEN_AI_TOOL_NAME, name)
    span.set_attribute(g.GEN_AI_TOOL_CALL_ID, call_id)
    span.set_attribute(g.GEN_AI_TOOL_CALL_ARGUMENTS, _clip(arguments))
    if result is not None:
        span.set_attribute(g.GEN_AI_TOOL_CALL_RESULT, _clip(result))
```

The tool helper. Operation `execute_tool`, tool name, call ID, then arguments and result, both passed through `_clip`. Attributes must be strings, numbers, booleans or lists of those, so dictionaries are JSON-encoded, and anything over two thousand characters is cut. The tool result for a shipment lookup can be a page of JSON; you want to know it happened, not store it twice.

[SCREEN: VS Code, `app/agent.py`. The three call sites.]

[CODE: step 4, apply in the agent]
```python
from telemetry.genai_attrs import set_agent_attrs, set_llm_attrs, set_tool_attrs

    def run(self, message, *, tenant, user_id, session_id):
        with tracer.start_as_current_span("invoke_agent atlas") as agent_span:
            set_agent_attrs(agent_span, name="atlas", conversation_id=session_id)
            agent_span.set_attribute("northwind.tenant", tenant)
            ...

    def _call_model(self, messages):
        with tracer.start_as_current_span(f"chat {self.model}") as span:
            response = self.client.chat.completions.create(model=self.model, messages=messages, tools=self.tool_specs)
            set_llm_attrs(span, request_model=self.model, response=response)
            return response

    def _run_tool(self, call):
        with tracer.start_as_current_span(f"execute_tool {call.function.name}") as span:
            args = json.loads(call.function.arguments)
            result = self.tools[call.function.name](**args)
            set_tool_attrs(span, name=call.function.name, call_id=call.id, arguments=args, result=result)
            return result
```

Now the three call sites. In `run`, the agent helper, keeping our own `northwind.tenant` alongside it. In `_call_model`, the LLM helper replaces the two `atlas.` attributes from 3.2. And a new span in `_run_tool`, named `execute_tool` plus the tool name, with the tool helper after the tool returns. Because `_run_tool` is called from inside the agent's `with` block, it nests correctly.

[SCREEN: Terminal 1: `OTEL_EXPORTER=console OFFLINE=1 make run`. Terminal 2: curl "Where is my ticket INC-2231?" with the three headers.]

[DEMO: Console prints four spans: `chat gpt-4.1-mini` (finish_reasons tool_calls), `execute_tool lookup_ticket` with `gen_ai.tool.call.arguments: {"ticket_id": "INC-2231"}`, a second `chat gpt-4.1-mini`, and `invoke_agent atlas` with `gen_ai.conversation.id: sess-demo-1`.]

Ask about a ticket this time, and read the console. Four spans. The first model call finishes with `tool_calls`. Then `execute_tool lookup_ticket`, with the arguments the model chose. A second model call, finishing with `stop`. And the agent span with the conversation ID. Every attribute has a `gen_ai.` name.

[SCREEN: `tests/integration/test_spans.py`. Show the test that asserts `GEN_AI_TOOL_NAME == "lookup_ticket"` on the tool span and that its parent is the agent span, using `InMemorySpanExporter`.]

[CODE: the assertion in `tests/integration/test_spans.py`]
```python
def test_ticket_question_emits_tagged_tool_span(atlas_offline, spans):
    atlas_offline.run("Where is my ticket INC-2231?", tenant="ops", user_id="emp-1042", session_id="s1")
    tool = next(s for s in spans.get_finished_spans() if s.name == "execute_tool lookup_ticket")
    agent = next(s for s in spans.get_finished_spans() if s.name == "invoke_agent atlas")
    assert tool.attributes[g.GEN_AI_TOOL_NAME] == "lookup_ticket"
    assert tool.parent.span_id == agent.context.span_id
```

And a test, so this can't rot. The fixture installs an in-memory exporter. The test runs the agent offline, finds the tool span, and asserts its name attribute and its parent. Lab 2 has you write the same test for `check_shipment`.

[AVATAR]
Three helpers, three call sites, one test. Atlas now speaks the standard. Next lecture, you'll see how much of this an auto-instrumentor does for you, and why you still keep the helpers.

**Recap:** `set_agent_attrs`, `set_llm_attrs` and `set_tool_attrs` put the `gen_ai.*` constants on the agent, model and tool spans, including cached and reasoning tokens and clipped tool arguments, and an integration test with an in-memory exporter pins the result.

**Transition:** Next, one line of auto-instrumentation that captures every OpenAI call, and the three things it can't know.

### Speaker notes: common student mistakes / Q&A

- Mistake: passing a dict directly to `set_attribute`. OTel drops it with a warning. Always JSON-encode via `_clip`.
- Mistake: setting usage attributes before the response exists (e.g. in a streaming path). Set them when usage is known; 5.4 handles streaming.
- "Why keep `northwind.tenant` when there's `gen_ai.conversation.id`?" Tenant is a business dimension the conventions don't define. Own namespace, always.
- If the repo's helper names differ at recording time, match the file and mention the change in the README; the narration depends only on there being one helper per span kind.

---

## Lecture 3.5 — Auto-instrumentation with OpenInference

| Field | Value |
|---|---|
| ID | 3.5 |
| Type | SC (code-along) |
| Target duration | 6:00 (~400 spoken words, about 2:51 of talking at 140 wpm, plus output) |
| Learning objectives | 1. Instrument the OpenAI client with `OpenAIInstrumentor().instrument(tracer_provider=...)`. 2. Read what the auto-generated span contains and how it nests under your manual spans. 3. Decide what to keep manual: agent span, tool spans, business attributes. |
| Prerequisites | 3.4 |
| Files used | You type: `03-code/telemetry/openinference_setup.py`. Reference: repo version. |

### Script

[AVATAR]
Everything you typed in `_call_model` last lecture, an auto-instrumentor can do in one line, for every OpenAI call in your process, including the ones in libraries you didn't write. So why did I make you type it? Because you need to know what it does, to know what it can't. Let's add it and compare.

[SLIDE 1: Which instrumentor]
- We use `openinference-instrumentation-openai` (Arize's OpenInference project)
- It patches the OpenAI client and emits one span per call with model, tokens, messages
- Uses OpenInference attribute names (`llm.token_count.prompt`, ...); Langfuse and Phoenix both read them
- Not used: `opentelemetry-instrumentation-openai-v2` (import error at verification time)

We use OpenInference's OpenAI instrumentor. It patches the client and emits a span per call, with model, token counts and messages, using OpenInference's attribute names. Langfuse and Phoenix both understand those. There's also an OpenTelemetry-contrib instrumentor for OpenAI; at verification time it failed to import, so it isn't in this course.

[SCREEN: VS Code, new file `telemetry/openinference_setup.py`.]

[CODE: the setup]
```python
"""Auto-instrument the OpenAI client with OpenInference (Lecture 3.5)."""

from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.sdk.trace import TracerProvider


def setup_openinference(provider: TracerProvider) -> None:
    OpenAIInstrumentor().instrument(tracer_provider=provider)
```

One function. Pass the provider you built in `setup_tracing`, so the auto spans go through the same pipeline as yours. Without that argument it uses the global provider, which is the same thing here, but be explicit; in tests you'll pass a different one.

[CODE: call it after tracing is set up]
```python
provider = setup_tracing()
setup_openinference(provider)
```

Call it right after `setup_tracing`, and before the OpenAI client is created. It patches the class, so a client made earlier may not be covered.

[SCREEN: Temporarily comment out the `with tracer.start_as_current_span(f"chat ...")` block in `_call_model` so only the raw API call remains. Terminal: console exporter, `OFFLINE=0` for this one request. Send the ticket question.]

[DEMO: Console prints a span named `ChatCompletion` with `openinference.span.kind: LLM`, `llm.model_name`, `llm.token_count.prompt`, `llm.token_count.completion`, `llm.input_messages...`, `llm.output_messages...`, nested under `invoke_agent atlas`.]

To see it clearly, I've commented out our manual model span for a moment, and gone live for one request. Look: a span named `ChatCompletion`, kind `LLM`, with the model name, both token counts, and the full input and output messages, nested under our agent span. We wrote none of that.

[SLIDE 2: What you get for free, and what you don't]
| Free from the instrumentor | Still yours |
|---|---|
| One span per OpenAI call | The agent span and the step structure |
| Model, tokens, messages, invocation parameters | Tool spans with arguments and results |
| Works inside libraries you didn't write | Business attributes: tenant, feature, prompt version |
| Streaming and async handled | Events like "step limit reached", error surfacing |

Here's the split. Free: a span per call, with model, tokens, messages and parameters, streaming and async included, even inside libraries you don't control. Not free: everything that isn't an API call. The agent span. The tool spans. Tenant and feature. The step-limit event. The instrumentor sees HTTP calls; it doesn't know your agent exists.

[SLIDE 3: Our rule]
- Auto-instrument the model client: never miss a call
- Manual spans for agent, steps, tools and business attributes
- Do not also wrap the same call manually as a generation: one call, one span (3.6)
- In Section 4, Langfuse's `@observe(as_type="generation")` replaces the manual model span where we need `usage_details` and `cost_details`

So our rule. Auto-instrument the client, so you never miss a call, including retries inside the SDK. Keep manual spans for the agent, steps, tools and business attributes. And never wrap the same call twice; one model call, one span. Next lecture shows what happens when you break that rule.

[SCREEN: Restore the manual span block in `_call_model` but keep it in mind for 3.6.]

[AVATAR]
One line, every call captured. Keep the helpers for everything the instrumentor can't see. And keep a note of that "one call, one span" rule; it's the third break in the next lecture.

**Recap:** `OpenAIInstrumentor().instrument(tracer_provider=provider)` emits a span per OpenAI call with model, tokens and messages under your agent span; the agent, tools and business attributes stay manual, and each model call should be recorded once.

**Transition:** Next, three ways this pipeline breaks silently, and the fix for each.

### Speaker notes: common student mistakes / Q&A

- Mistake: instrumenting after the OpenAI client is constructed. Depending on version, the patch may not apply to existing instances. Instrument at startup, before `AtlasAgent` is built.
- "Does it capture the mock?" No. The mock isn't the OpenAI client. Offline, our manual generation span (from Section 4) carries the usage; the tests cover both paths.
- "Can I stop it recording message content?" Yes, via the OpenInference `TraceConfig` (hide inputs/outputs). Section 10.2 covers the privacy switches; keep it out of this lecture.
- Never show `opentelemetry-instrumentation-openai-v2` on screen.

---

## Lecture 3.6 — Break it: orphan spans, missing context and double counting

| Field | Value |
|---|---|
| ID | 3.6 |
| Type | DM (live demo, three before/after pairs) |
| Target duration | 6:00 (~575 spoken words, about 4:06 of talking at 140 wpm, plus console output) |
| Learning objectives | 1. Recognise an orphan span caused by work on a thread without the trace context, and fix it by passing the context. 2. Recognise a tool span that isn't under the agent span, and fix the call structure. 3. Recognise double counting from two instrumentations of one call, and fix it by recording each call once. |
| Prerequisites | 3.2 to 3.5 |
| Files used | `03-code/tests/integration/test_spans.py` (the three regression tests), `03-code/app/agent.py`, `03-code/app/tools.py` |

**Recording note:** each break is a small, labelled edit made live, run with the console exporter, then reverted. Tint the broken console output red and the fixed output green. Keep the three regression tests visible at the end so students see how each break is caught.

### Script

[AVATAR]
Instrumentation doesn't crash when it's wrong. It produces traces that look fine and lie. Here are the three lies I see most, each in about ninety seconds: a span with no parent, a tool that looks like it ran on its own, and a bill that's exactly double.

[SLIDE 1: Break 1: background work without context]
```python
# app/tools.py: lookup_ticket is blocking I/O, so someone moved it to a thread pool
result = await loop.run_in_executor(pool, _lookup_ticket_blocking, ticket_id)
```

Break one. Someone noticed `lookup_ticket` blocks on I/O and moved it to a thread pool. Reasonable. The tool creates its own span inside that function.

[SCREEN: Terminal: console exporter, send the ticket question.]

[DEMO: Console shows `execute_tool lookup_ticket` with `"parent_id": null` and a different `trace_id` from `invoke_agent atlas`.]

Read the tool span. Parent ID null. And look at the trace ID: different from the agent's. This span is a root of its own trace. In Langfuse it shows up as a separate one-span trace named `execute_tool lookup_ticket`, with no tenant, no user, no cost context. An orphan.

[SLIDE 2: Why: context doesn't cross threads]
- The current span lives in `contextvars`
- `await` and `asyncio.create_task` copy it; a `ThreadPoolExecutor` does not
- The worker thread starts with an empty context, so the new span has no parent

Why? The current span lives in a context variable. `await` carries it, `create_task` copies it, but a plain thread pool starts each job with an empty context. The tool span looks for a current span, finds none, and becomes a root.

[CODE: fix 1, carry the context]
```python
from opentelemetry import context as otel_context

ctx = otel_context.get_current()
result = await loop.run_in_executor(pool, _lookup_ticket_blocking, ticket_id, ctx)

def _lookup_ticket_blocking(ticket_id: str, ctx) -> dict:
    with tracer.start_as_current_span("execute_tool lookup_ticket", context=ctx) as span:
        ...
```

The fix: capture the context before you hand off, and pass it in. `start_as_current_span` accepts a `context` argument, and the span parents itself there. `asyncio.to_thread` also copies the context for you, which is the neater fix when you can use it.

[DEMO: Rerun. Tool span now has the agent's `parent_id` and the same `trace_id`.]

Same trace ID, parent set. Adopted.

[SLIDE 3: Break 2: tool span outside the agent span]
```python
def run(self, message, **ids):
    with tracer.start_as_current_span("invoke_agent atlas") as agent_span:
        plan = self._loop(message)          # model calls happen here...
    for call in plan.pending_tool_calls:    # ...but tools run after the block closed
        self._run_tool(call)
```

Break two. A refactor moved tool execution after the agent's `with` block. The code still works. The trace doesn't.

[DEMO: Console shows `invoke_agent atlas` ending before `execute_tool lookup_ticket` starts; the tool span's `parent_id` is null. In Langfuse: the agent trace has no tool child, and a separate tool trace appears.]

The agent span ends. Then the tool span starts, with no current span, so it's a root again. In Langfuse, the agent trace shows a model call that asked for a tool, and no tool. Anyone reading that trace concludes the tool never ran. It did; it's just filed under a different trace.

[CODE: fix 2, structure follows causality]
```python
    with tracer.start_as_current_span("invoke_agent atlas") as agent_span:
        plan = self._loop(message)
        for call in plan.pending_tool_calls:
            self._run_tool(call)
```

The fix is structural. If the tool ran because of the agent, it runs inside the agent's block. Make the code nest the way the causality nests.

[DEMO: Rerun. Tool span nested under the agent span again.]

[SLIDE 4: Break 3: instrumenting the same call twice]
- OpenInference instruments the client (3.5)
- `_call_model` still wraps the call in a manual span with usage attributes (3.4)
- Result: two spans per model call, each with 3,012 input tokens

Break three, and this one costs money on paper. OpenInference is on. Our manual model span from 3.4 is also on, and it also records usage. So every model call produces two spans, each claiming three thousand input tokens.

[SCREEN: Ops Console cost page after a small swarm run with both on. Day's cost reads $12.84 instead of $6.42.]

[DEMO: Console cost tile shows exactly double.]

Run a short swarm and look at the console. Twelve dollars eighty-four. Exactly double six forty-two. Any cost dashboard that sums usage across spans, and they all do, now shows twice your real spend. You'd cut features to fix a bill that doesn't exist.

[CODE: fix 3, one call, one span]
```python
# choose one:
# (a) keep OpenInference; drop usage attributes from the manual span, or drop the manual span
# (b) keep the manual generation span (Section 4 needs it for cost_details); do not instrument the client
```

The fix is a decision, not code: one model call, one span carrying usage. Either keep the auto-instrumentor and stop recording usage manually, or keep the manual generation span, which Section four needs for explicit cost, and don't instrument the client. Atlas takes the second path by default, with OpenInference available behind a flag for Section twelve.

[SCREEN: `tests/integration/test_spans.py`. Show the three tests: `test_no_orphan_spans`, `test_tool_spans_are_children_of_agent`, `test_one_generation_per_model_call`.]

[CODE: the regression tests]
```python
def test_no_orphan_spans(spans):
    roots = [s for s in spans.get_finished_spans() if s.parent is None]
    assert [s.name for s in roots] == ["invoke_agent atlas"]

def test_one_generation_per_model_call(atlas_offline, spans):
    result = atlas_offline.run("Where is my ticket INC-2231?", tenant="ops", user_id="u", session_id="s")
    gens = [s for s in spans.get_finished_spans() if s.name.startswith("chat ")]
    assert len(gens) == result.model_calls
```

And all three lies are caught by tests. Exactly one root span, named `invoke_agent atlas`. Every tool span's parent is the agent. And the number of generation spans equals the number of model calls the agent reports. Make test runs these on every change.

[SLIDE 5: Symptom → cause → fix]
| Symptom | Cause | Fix |
|---|---|---|
| One-span trace named `execute_tool ...` | Work on a thread without context | Pass `context=`, or `asyncio.to_thread` |
| Agent trace shows a tool request but no tool | Tool ran after the agent block closed | Nest the code like the causality |
| Cost exactly 2× expected | Same call instrumented twice | One call, one span with usage |

[AVATAR]
Screenshot this table. All three lies look like healthy traces until you count roots, check parents and compare the bill. Now you have tests that do the counting for you.

**Recap:** Thread hand-offs without context create orphan root spans, tools run outside the agent block lose their parent, and instrumenting one call twice doubles every token, and three integration tests catch all of them.

**Transition:** Lab 2: instrument `check_shipment` end to end, and write the test that proves its span is correct.

### Speaker notes: common student mistakes / Q&A

- "Why does `asyncio.create_task` work but the thread pool doesn't?" Tasks copy the current `contextvars` context on creation; threads don't. `asyncio.to_thread` copies it explicitly, which is why it also works.
- Mistake: "fixing" break 1 by starting the span in the caller and passing the span object into the thread. It works, but the span then spans the queueing time too. Pass the context, start the span where the work happens.
- Break 3 also appears with Langfuse's `langfuse.openai` drop-in client plus OpenInference. Same rule: one instrumentation per call.
- Revert every break on camera. Students copy what they last saw.

---

## Lecture 3.7 — Lab 2: Instrument a new tool end to end

| Field | Value |
|---|---|
| ID | 3.7 |
| Type | LAB (guided lab with short video intro) |
| Target duration | 4:00 total (1:30 video, ~225 spoken words, about 1:36 of talking at 140 wpm) |
| Learning objectives | 1. Add a correctly named and tagged span to `check_shipment`, including clipped arguments and result. 2. Write an integration test asserting its attributes and parent. 3. See the span in the console exporter and in Langfuse. |
| Prerequisites | 3.1 to 3.6 |
| Files used | `04-labs/lab-02-instrument-tool.md`, `03-code/app/tools.py`, `03-code/tests/integration/test_spans.py` |

### Script

[AVATAR]
Lab two. `check_shipment` is the one tool that isn't instrumented yet. You're going to fix that, prove it with a test, and see it in Langfuse. Thirty to forty-five minutes.

[SCREEN: VS Code, `04-labs/lab-02-instrument-tool.md`. Scroll the steps.]

Step one: the span. Name it `execute_tool check_shipment`, use `set_tool_attrs` with the tracking number as arguments and the clipped result. Make sure it's created where the tool runs, inside the agent's block.

Step two: the test. Copy the pattern from `test_ticket_question_emits_tagged_tool_span`. Ask Atlas "Where is shipment NW-88213?" offline, find the span, assert the tool name attribute, assert the parent is the agent span, and assert the result attribute is under two thousand characters.

[SCREEN: Scroll to the stretch goal.]

Stretch goal: the shipment API sometimes returns a not-found error. Make the span's status ERROR with the message when it does, and add a second test for it.

[SCREEN: Scroll to the deliverables.]

Deliverables: the test output, and a screenshot of the trace in Langfuse with the `check_shipment` span selected and its arguments visible.

[AVATAR]
Run make test before and after. Before, your new test fails. After, everything's green, including the three anti-lie tests from the last lecture. That's the loop for every span you'll ever add.

**Recap:** Lab 2 adds a tagged `execute_tool check_shipment` span, a test that pins its attributes and parent, and a trace screenshot.

**Transition:** A six-question quiz on tracing and the conventions, then Section 4: what Langfuse adds on top of these spans.

### Speaker notes: common student mistakes / Q&A

- Students put the span inside `tools.py` but call the tool from outside the agent's `with` block. The orphan test catches it; point them to Break 2.
- `set_status(Status(StatusCode.ERROR, msg))` needs `from opentelemetry.trace import Status, StatusCode`. Raising inside the `with` block also sets error status automatically.
- If the mock never chooses `check_shipment` for their question, use the exact question from the lab; the mock keys on the word "shipment" and an `NW-` tracking number.

---

## Lecture 3.8 — Quiz: Tracing and semantic conventions

| Field | Value |
|---|---|
| ID | 3.8 |
| Type | QZ (quiz with short video intro) |
| Target duration | 3:00 total (1:00 video, ~100 spoken words, about 0:43 of talking at 140 wpm) |
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
