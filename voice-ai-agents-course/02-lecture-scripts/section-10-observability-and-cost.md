# Section 10: Observability, Latency and Cost

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** about 47 minutes (7 lectures)
> **Running example:** Riley, the AI receptionist for Maple Street Dental
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
> **Version note (show on screen in 10.2):** In livekit-agents 1.8, the `metrics_collected` event still works (it logs a deprecation notice) and is what we export to JSONL for per-stage detail. Totals and cost come from `session.usage`; per-turn latency from `ChatMessage.metrics`. Do not teach `metrics.UsageCollector` (deprecated); mention it once only so students recognise it in old tutorials.

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (matched to `03-code/`):** `agents/s10_observed_agent.py`: `setup_observability`, `MetricsExporter`, `attach_observers`, `ObservedRiley`; `src/maple/costs.py`: `PriceTable`, `DEFAULT_PRICES`, `PHONE_PRICES`, `UsageNumbers`, `cost_breakdown`, `usage_from_model_usage`, `typical_cascaded_usage`, `typical_realtime_usage`; `src/maple/latency.py`; `CallState.call_outcome` from `agents/common.py`. On screen, the agent is "Riley".

---

## Lecture 10.1: What to measure on every call

| Field | Value |
|---|---|
| ID | 10.1 |
| Title | What to measure on every call |
| Type | SL (slides + avatar) |
| Target duration | 7:00 (about 730 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Measure every call on three levels: pipeline timing, model usage, and business outcome. |
| Prerequisites | Section 9 (latency budget, failure taxonomy) |
| Files used | None (conceptual). Diagram: "one turn, timed" (caller stops → EOU → LLM TTFT → TTS TTFB → Riley speaks). |

**Learning objectives**

1. List the per-turn timing metrics LiveKit reports (EOU delay, transcription delay, LLM TTFT, TTS TTFB) and what each one tells you.
2. List the usage metrics that drive cost (STT audio seconds, LLM tokens, TTS characters, realtime audio tokens).
3. Define per-call outcome metrics (booked, transferred, completed, failed tool calls, interruptions) and why they matter more than any timing number.

### Script

[AVATAR]

Last Tuesday, Riley's dashboard was all green. Latency fine. Error rate zero. [PAUSE] And the clinic manager called to say three patients had complained that "the robot kept hanging up on them." The metrics we had were real. They just weren't the metrics that mattered. In this section, we'll measure Riley properly, on three levels, starting with what to collect on every single call.

[SLIDE 1: Three levels of measurement]
- Pipeline timing: how fast each stage is, per turn
- Usage: how much of each model each call consumes (the cost drivers)
- Outcome: what actually happened on the call

[AVATAR]

Three levels. Timing tells you how the call felt. Usage tells you what it cost. Outcome tells you whether it worked. Most teams collect the first, estimate the second, and forget the third.

[SLIDE 2: One turn, timed]
- `end_of_utterance_delay`: caller stops → turn declared over (VAD, endpointing, turn detector)
- `transcription_delay`: caller stops → final transcript
- LLM `ttft`: request → first token (plus `prompt_tokens`, `completion_tokens`)
- TTS `ttfb`: first text → first audio byte (plus `characters_count`)
- Per-turn `e2e_latency` on each assistant message (`ChatMessage.metrics`)

[B-ROLL: animated timeline of one turn. Caller waveform ends; a bracket labelled "EOU delay 560 ms"; then "LLM TTFT 470 ms"; then "TTS TTFB 170 ms"; Riley's waveform starts. Total brace: "about 1.2 s".]

[AVATAR]

Here's one turn, timed. The caller stops speaking. The end-of-utterance delay is how long Riley waits before deciding the caller is done. That's VAD, endpointing and the turn detector together. On a phone line it's often the biggest single piece. The transcription delay is when the final transcript arrives. Then the LLM's time to first token, and the TTS's time to first byte. Add those up and you get voice-to-voice latency, the silence the caller actually hears.

LiveKit reports all of these for you. In Section 9 we turned them into a budget. In this section we'll collect them on every call, not just in tests.

[SLIDE 3: Usage: the cost drivers]
- STT: audio seconds sent
- LLM: prompt tokens (and cached tokens), completion tokens
- TTS: characters synthesized
- Realtime models: audio input and output tokens
- Plus: call minutes (platform) and telephony minutes

[AVATAR]

Usage is the second level. Each provider bills on its own unit. Speech-to-text bills audio seconds. The LLM bills tokens, and cached prompt tokens are much cheaper. Text-to-speech bills characters. A realtime model bills audio tokens, which are expensive. And on top of that, you pay per minute for the agent platform and the phone line. If you don't capture usage per call, you can't answer the question from lecture 10.4: "what does one minute of Riley cost?"

[SLIDE 4: Outcome: what happened on the call]
- `call_outcome`: booked, rescheduled, cancelled, waitlisted, transferred, completed, error
- Tool calls: count, failures (`ToolError`), and tool latency
- Interruptions and false interruptions
- Transfers requested vs completed; calls that ended in silence
- Call duration

[AVATAR]

The third level is the one most dashboards miss. What happened? Riley already records a `call_outcome` in `CallState`: booked, cancelled, transferred, completed, error. Add tool calls and tool failures. Add interruptions, because a caller who interrupts five times is a caller who's frustrated. Add transfers requested versus transfers completed. And calls that ended in silence. [PAUSE] Our "robot kept hanging up" complaint? That showed up in outcomes: a spike in calls ending in `end_call` less than twenty seconds in. Timing was fine. The outcome wasn't.

[SLIDE 5: Where each metric comes from]
- `metrics_collected` events: EOU, STT, LLM, TTS, VAD metrics, per stage (still works in 1.8; we export these)
- `ChatMessage.metrics`: per-turn latency (newer)
- `session.usage.model_usage`: usage per model and provider (newer)
- `CallState`: outcome, transfers, notes (your code)
- OpenTelemetry spans: the story of each turn (lecture 10.3)

[AVATAR]

And here's where each one comes from in LiveKit Agents 1.8. The `metrics_collected` event, which we used in Section 9, still works. Newer versions add per-turn metrics on each chat message, and usage per model on `session.usage`. Outcomes come from your own `CallState`. And traces come from OpenTelemetry. Next lecture, we wire up all of them.

[SLIDE 6: One call, one record]
- `call_summary`: room, call seconds, model usage, cost components, cost per minute, outcome
- Plus every per-stage metric line for that call
- Plus events worth counting: `agent_false_interruption`, `user_state_changed` (away), `function_tools_executed`
- One file per call: easy to find, easy to aggregate

[AVATAR]

Here's what "measure every call" becomes in practice: one record per call. A summary line with the room name, how long the call lasted, usage per model, the cost of each component, the cost per minute, and the outcome. Above it, every per-stage metric for that call. That's what we'll build in the next lecture.

And a few session events are worth counting too. LiveKit emits `agent_false_interruption` when Riley paused for what turned out not to be a real interruption, like a cough. A spike means your interruption settings are too sensitive for phone lines. `user_state_changed` tells you when a caller went quiet for a long time, which often means confusion. And `function_tools_executed` tells you which tools ran on each turn.

[PAUSE]

Last thought for this lecture. Decide now which three numbers you'd look at if you only had one minute a day. For Maple Street Dental, mine are p95 voice-to-voice latency, cost per minute, and the share of calls that ended booked or answered without a human. Everything else is there for when one of those three looks wrong.

[AVATAR]

A question I often get: "Isn't all this measurement expensive?" Not really. The metrics are already computed by LiveKit. Writing a few lines of JSON per turn costs almost nothing, and the traces are sent in the background. The expensive part is not having the data on the day a patient complains, and having to guess. [PAUSE] Collect everything numeric by default. Be careful with content, like transcripts, which we'll handle in Section 11.

Here's what "everything numeric" means for Riley. Per turn: four timings and two token counts. Per call: usage per model, cost, duration and outcome. Per day: those rolled up into the five dashboard numbers you'll meet in lecture 10.5. That's it. It fits on one slide, and it answers almost every question anyone will ask you about Riley in production.

### Recap

Measure every call on three levels: per-turn pipeline timing, per-model usage, and the business outcome recorded in `CallState`.

### Transition

Next, we'll collect metrics and usage from a live Riley and write them to a file on every call.

### Speaker notes: common mistakes and Q&A

- **Only measuring averages**: repeat the Section 9 lesson. p95 per stage.
- **No outcome field**: without `call_outcome`, you can't compute containment or transfer rate (10.5).
- **Logging transcripts as "metrics"**: transcripts are PII; keep metrics numeric, and handle transcripts with the redaction rules in Section 11.
- **"Which API should I use?"**: new code should prefer `session.usage` and `ChatMessage.metrics`; `metrics_collected` remains useful for per-stage detail and older examples.

---

## Lecture 10.2: Collecting metrics and usage

| Field | Value |
|---|---|
| ID | 10.2 |
| Title | Collecting metrics and usage |
| Type | SC (screencast code-along) |
| Target duration | 9:00 (about 720 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Attach observers to the session, not the agent: log and export every metric, record per-turn latency, and write a usage and cost summary when the call ends. |
| Prerequisites | 10.1 |
| Files used | `agents/s10_observed_agent.py`, `src/maple/costs.py`, `.env` (`METRICS_DIR`) |

**Learning objectives**

1. Handle `@session.on("metrics_collected")` with `metrics.log_metrics` and export each metric to JSONL.
2. Read per-turn latency from `ChatMessage.metrics` via `conversation_item_added`.
3. Register a shutdown callback that turns `session.usage` into a cost summary.

### Script

[AVATAR]

Here's a design choice that will save you pain. [PAUSE] Observability wraps the session, not the agent. Riley's class doesn't change at all in this lecture. We attach observers to the `AgentSession`, so the same function works for the booking agent, the phone agent, the multi-agent team and the capstone.

[SCREEN: VS Code, `agents/s10_observed_agent.py`, scroll to `ObservedRiley`. Lower third with the API-verified note.]

Open `agents/s10_observed_agent.py`. Look at `ObservedRiley` first. It's just booking tools plus the FAQ tool, with the normal instructions and greeting. Its docstring says it all: "observability wraps the session, not the agent." Everything interesting is in one function, `attach_observers`. Let's build it up.

[CODE: step 1: a JSONL exporter]

```python
class MetricsExporter:
    """Append metrics as JSON lines, one file per room."""

    def __init__(self, directory: str | Path, room_name: str) -> None:
        self.path = Path(directory) / f"{room_name}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, record: dict[str, Any]) -> None:
        """Write one record (a dict that is JSON serialisable)."""
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")

    def write_metrics(self, agent_metrics: metrics.AgentMetrics, room: str) -> None:
        """Serialise a LiveKit metrics object (``type`` field included)."""
        record = agent_metrics.model_dump(mode="json")
        record["room"] = room
        self.write(record)
```

First, somewhere to put the numbers. `MetricsExporter` appends JSON lines to one file per room, in the folder from `METRICS_DIR`, which defaults to `metrics`. One file per call makes it easy to find a bad call later, and it's exactly the format `tests/evals/latency_report.py` reads. LiveKit's metric objects are Pydantic models, so `model_dump(mode="json")` gives us a plain dictionary, including the `type` field.

[CODE: step 2: metrics events]

```python
def attach_observers(session: AgentSession[CallState], ctx: JobContext, *, realtime: bool = False) -> None:
    """Wire metrics export, per-turn latency logs and the shutdown cost summary."""
    settings = get_settings()
    exporter = MetricsExporter(settings.metrics_dir, ctx.room.name)
    started = time.monotonic()

    @session.on("metrics_collected")
    def on_metrics(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        exporter.write_metrics(ev.metrics, ctx.room.name)
```

Now the first observer. Every time the session measures something, it emits `metrics_collected` with a `MetricsCollectedEvent`. `ev.metrics` is one object: EOU metrics, STT, LLM, TTS or VAD. We do two things with it. `metrics.log_metrics` prints a readable log line, which is great in development. And the exporter writes it to the call's file.

[CODE: step 3: per-turn latency, the newer way]

```python
    @session.on("conversation_item_added")
    def on_item(ev: ConversationItemAddedEvent) -> None:
        item = ev.item
        if getattr(item, "role", None) == "assistant":
            report = item.metrics  # modern per-turn metrics
            if "e2e_latency" in report:
                logger.info("turn latency e2e=%.0f ms", report["e2e_latency"] * 1000)
```

Second observer, the newer API. Every time a message is added to the conversation, we get `conversation_item_added`. For Riley's messages, `item.metrics` is a per-turn report with keys like `end_of_turn_delay`, `llm_node_ttft`, `tts_node_ttfb` and `e2e_latency`, the whole voice-to-voice time for that turn. We log it. One line per turn, and you can see Riley's responsiveness scroll by during a call.

[CODE: step 4: usage and cost at shutdown]

```python
    async def log_usage() -> None:
        call_seconds = time.monotonic() - started
        model_usage = [u.model_dump() for u in session.usage.model_usage]
        usage = usage_from_model_usage(model_usage, call_seconds, realtime=realtime)
        report = cost_breakdown(usage)
        logger.info("call cost report\n%s", report.format())
        exporter.write(
            {
                "type": "call_summary",
                "room": ctx.room.name,
                "call_seconds": round(call_seconds, 2),
                "model_usage": model_usage,
                "cost_components": dict(report.components),
                "cost_total": round(report.total, 6),
                "cost_per_minute": round(report.per_minute, 6),
                "outcome": session.userdata.call_outcome,
            }
        )

    ctx.add_shutdown_callback(log_usage)
```

Third, what the call cost. `ctx.add_shutdown_callback` registers a function that runs when the call ends. Inside it, `session.usage.model_usage` is a list with one entry per model and provider: LLM tokens, STT audio seconds, TTS characters. `usage_from_model_usage` from `src/maple/costs.py` turns that into our own `UsageNumbers`, and `cost_breakdown` prices it. We log the report, and write one final `call_summary` line to the file: duration, raw usage, cost per component, cost per minute, and the call outcome from `CallState`. [PAUSE] Timing, usage and outcome, all three levels from last lecture, in one file per call.

[AVATAR]

One note for when you read older LiveKit tutorials. Many of them total usage with a helper called `metrics.UsageCollector`. In livekit-agents 1.8 it's deprecated, and it adds everything up without separating models and providers. We don't use it. `session.usage` is the replacement, and it's what our shutdown callback reads.

[CODE: step 5: the entrypoint]

```python
@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start Riley with metrics, usage and tracing attached."""
    setup_observability()
    ctx.log_context_fields = {"room": ctx.room.name}
    session = create_session(get_settings(), proc=ctx.proc, userdata=CallState(), max_tool_steps=5)
    attach_observers(session, ctx)
    await session.start(agent=ObservedRiley(), room=ctx.room)
```

The entrypoint wires it together. `setup_observability` is next lecture's tracing. `ctx.log_context_fields` stamps the room name on every log line, so logs, metrics files and traces share one key. Then the usual session, then `attach_observers`, then start.

Run a call.

[SCREEN: terminal]

```bash
uv run agents/s10_observed_agent.py console
```

[DEMO: book a cleaning in console mode, ask about parking, say goodbye. The terminal shows `metrics_collected` log lines (EOU, LLM, TTS) and `turn latency e2e=... ms` lines. Press Ctrl+C to end; the "call cost report" prints with stt/llm/tts/platform lines and "per minute". Then `ls metrics/` and `tail -n 3 metrics/<room>.jsonl`, ending with the `call_summary` record including `"outcome": "booked"`.]

Watch the log. Metric lines for each stage, and one `turn latency` line per reply. When I end the call, the cost report prints: STT, LLM, TTS and platform, the total, and cost per minute. And in the `metrics` folder, one file for this call. The last line is the summary, and the outcome says "booked."

[AVATAR]

That file is now the raw material for three things: the latency report from Section 9, the cost analysis in lecture 10.4, and the call-quality report in Lab 6.

[AVATAR]

Why write to local files instead of straight into a monitoring service? Three reasons. First, files work everywhere: on your laptop, in CI, in a container, with no account needed. Second, they're the same format our Section 9 reports read, so tests and production share one pipeline. Third, when you do add a monitoring service, it's a small change: ship the same records to it, or replace `MetricsExporter.write` with an HTTP call.

In production, one more habit. Don't let the observability code break the call. If the disk is full or a write fails, the caller should never notice. [PAUSE] Keep handlers small and fast, never block on network calls inside a metrics event, and do the slow work, like pricing and summarising, once, in the shutdown callback, after the caller has hung up.

[AVATAR]

Let's connect this back to Section 9. The files this agent writes are exactly what `tests/evals/latency_report.py` reads. So the loop is closed: record real calls with `ObservedRiley`, drop a representative file into `tests/data`, and CI checks every future change against real-world timing. [PAUSE] Production data becomes test data, which is the healthiest relationship those two can have.

### Recap

`attach_observers` logs and exports every `metrics_collected` event, logs per-turn `e2e_latency` from `ChatMessage.metrics`, and writes a usage-and-cost `call_summary` from `session.usage` when the call ends.

### Transition

Numbers tell you something is slow. Traces tell you why. Next, OpenTelemetry and Langfuse.

### Speaker notes: common mistakes and Q&A

- **No metrics file**: `METRICS_DIR` points somewhere unwritable, or the agent crashed before the first metric. Check the path in the startup log.
- **Shutdown callback never runs in console**: end the call with Ctrl+C once and wait; killing the process twice skips callbacks.
- **Deprecation warnings**: `metrics_collected` logs a deprecation notice in 1.8 but still works; we use it only for the per-stage JSONL export. Totals come from `session.usage`.
- **Realtime usage priced as text**: pass `realtime=True` to `attach_observers` for the realtime agent, so audio tokens get realtime prices.

---

## Lecture 10.3: Tracing with OpenTelemetry and Langfuse

| Field | Value |
|---|---|
| ID | 10.3 |
| Title | Tracing with OpenTelemetry and Langfuse |
| Type | SC (screencast code-along) |
| Target duration | 10:00 (about 830 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Point LiveKit's built-in OpenTelemetry spans at Langfuse, and every call becomes a readable trace of turns, LLM requests and tool calls, with PII kept out by default. |
| Prerequisites | 10.2; a Langfuse account (cloud free tier or self-hosted); `uv sync --extra observability` |
| Files used | `agents/s10_observed_agent.py` (`setup_observability`), `.env` (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`) |

**Learning objectives**

1. Configure an OTLP exporter to Langfuse with `set_tracer_provider(...)` from `livekit.agents.telemetry`.
2. Read a call trace: session, user turns, agent turns, LLM requests, function tool spans and TTS.
3. Decide what conversational content reaches your tracing backend with `allow_pii`, and link traces to logs and metrics by room name.

### Script

[AVATAR]

The latency report says one turn in twenty is slow. Which turn? What was Riley doing? Was it the LLM, a tool, or a long prompt? [PAUSE] Metrics can't tell you. Traces can. A trace is the story of one call, broken into timed steps you can open and inspect. LiveKit Agents already creates those steps using OpenTelemetry, the open standard for traces. All we have to do is send them somewhere. We'll use Langfuse, an open-source LLM observability tool.

[SLIDE 1: What LiveKit traces for you]
- `agent_session`: the whole call
- `user_turn` / `agent_turn`: each side of the conversation
- `eou_detection`, `llm_node`, `llm_request`, `function_tool`, `tts_node`, `tts_request`
- Attributes: model names, token counts, timings, tool arguments (when allowed)
- Span names can change between versions; check your trace viewer

[AVATAR]

Here's what you get for free. A span for the whole session. Spans for each user turn and agent turn. Inside those, end-of-utterance detection, the LLM node and the actual LLM request, every function tool call, and the TTS work. Each span carries attributes: model names, token counts, timings, and, if you allow it, the text and tool arguments.

[SCREEN: Langfuse cloud → Settings → API keys → create key pair. Copy public and secret keys.]

First, Langfuse keys. In Langfuse, open your project's settings and create an API key pair. You get a public key and a secret key. Put them in `.env`.

[CODE: `.env` (add)]

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

And install the observability extra, which brings in the OpenTelemetry SDK and OTLP exporter.

```bash
uv sync --extra observability
```

[SCREEN: `agents/s10_observed_agent.py`, `setup_observability`]

[CODE: `setup_observability`, step 1: pointing OTLP at Langfuse]

```python
def setup_observability(service_name: str = "riley") -> str | None:
    """Configure an OpenTelemetry tracer provider if Langfuse or OTLP env vars are set."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    backend: str | None = None
    if public_key and secret_key:
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
        auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{host}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic%20{auth}"
        backend = "langfuse"
    elif os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"):
        backend = "otlp"
    if backend is None:
        return None
```

Langfuse accepts OpenTelemetry traces at `/api/public/otel` on your Langfuse host, authenticated with HTTP basic auth: your public key and secret key, joined with a colon and base64-encoded. We set the two standard OpenTelemetry environment variables, the endpoint and the headers, and the exporter picks them up. The `%20` is a URL-encoded space, which the OTLP headers format expects. If there are no Langfuse keys but a generic OTLP endpoint is set, we use that instead, so the same code works with Grafana, Honeycomb or any other OpenTelemetry backend. And if neither is set, tracing is off and the agent runs normally.

[CODE: step 2: the tracer provider]

```python
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning("tracing env vars set but OpenTelemetry is not installed: uv sync --extra observability")
        return None

    from livekit.agents.telemetry import set_tracer_provider

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    # allow_pii=False keeps transcripts out of spans; flip only if your retention policy allows.
    set_tracer_provider(provider, metadata={"clinic": "maple-street-dental"}, allow_pii=False)
    logger.info("tracing enabled via %s", backend)
    return backend
```

Standard OpenTelemetry setup. A `TracerProvider` named after our service. A `BatchSpanProcessor`, which sends spans in the background in batches, so tracing never slows down a turn. An `OTLPSpanExporter` over HTTP, which reads the environment variables we just set.

Then the LiveKit-specific line: `set_tracer_provider` from `livekit.agents.telemetry`. It tells LiveKit Agents to send its spans through our provider. Two arguments matter. `metadata` adds attributes to every span, here the clinic name. And `allow_pii`. [PAUSE] With `allow_pii=False`, LiveKit strips conversational content, tool payloads and other user data from spans before they reach Langfuse, and keeps the timings, models and token counts. For a dental clinic, that's the right default. Patients say their names, birthdays and symptoms out loud. If your data-retention policy and your vendor agreement with Langfuse allow transcripts in traces, you can flip it to `True` and see full conversations. That's a policy decision, not a coding one, and we'll come back to it in Section 11.

We call `setup_observability()` at the top of the entrypoint, as you saw last lecture. Run a call.

```bash
uv run agents/s10_observed_agent.py console
```

[DEMO: a call: ask about parking, then book a cleaning. End the call. Switch to Langfuse → Traces. Open the newest trace: a tree with `agent_session` at the top; nested `user_turn`, `agent_turn`, `llm_node` / `llm_request` with model `gpt-4.1-mini` and token counts; a `function_tool` span for `lookup_clinic_info`, then for `find_available_slots` and `book_appointment`; `tts_node` spans. Click the slowest `agent_turn` and show its timing bar.]

The startup log says "tracing enabled via langfuse." After the call, open Langfuse. Here's the trace. At the top, the whole session. Inside, each turn. Open this agent turn: the LLM request, with the model and the token counts. The `function_tool` span for `lookup_clinic_info`. Here's the booking turn: `find_available_slots`, then `book_appointment`.

Now the question we started with. Which turn was slow? [PAUSE] Sort by duration. This one. Open it. The LLM request took most of it, and look at the prompt token count: nearly four thousand. It's the turn after the FAQ lookup, when the conversation plus the retrieved section made the prompt big. That's a concrete fix: trim what the tool returns. Metrics said "slow." The trace said "why."

[SLIDE 2: Linking traces, logs and metrics]
- One key everywhere: the room name (`call-...`)
- `ctx.log_context_fields = {"room": ctx.room.name}` on every log line
- Metrics file: `metrics/<room>.jsonl`
- Trace attributes: add `metadata={...}` for search (clinic, environment)
- With `allow_pii=False`, use the room name to find a transcript in your own, access-controlled store

[AVATAR]

Last piece: linking. When the clinic manager says "a patient called at 2:14 and Riley was weird," you need to jump from that call to its trace, logs and metrics. Use one key everywhere: the room name. It's on every log line through `log_context_fields`, it's the metrics file name, and it's on the trace. And because we keep transcripts out of traces, the room name is also how an authorized person finds the transcript in your own, access-controlled store.

If you've taken *AI Agent Testing & Evaluation*, you've used Langfuse there for scoring traces. The same idea applies here: you can attach evaluation scores from Section 9, like a DeepEval metric, to production traces. It's optional, and a great next step.

[AVATAR]

A quick tour of how I actually use traces day to day. I don't browse them. I search them. When the latency report flags a slow hour, I filter traces to that hour and sort by duration. When a tool starts failing, I filter for `function_tool` spans with errors. When the clinic reports a strange call, I search by room name. [PAUSE] Traces are an index into your calls. You go to them with a question, and they give you the one call that answers it.

[AVATAR]

And if you don't want Langfuse, you don't need to change any code. Point `OTEL_EXPORTER_OTLP_ENDPOINT` at any OpenTelemetry-compatible backend, like Grafana Tempo, Honeycomb or Datadog, and `setup_observability` sends spans there instead. [PAUSE] That's the value of an open standard: the tracing code you write today outlives whichever vendor you pick.

### Recap

`setup_observability` points OpenTelemetry at Langfuse and calls `set_tracer_provider(..., allow_pii=False)`, so every call becomes a trace of turns, LLM requests and tool calls, linked to logs and metrics by room name.

### Transition

We know how fast Riley is and why. Next, the number your boss will actually ask for: what does a minute of Riley cost?

### Speaker notes: common mistakes and Q&A

- **No traces appear**: the observability extra isn't installed (look for the warning), keys are wrong, or the host is wrong for your Langfuse region. Check the startup log line "tracing enabled via langfuse".
- **Traces appear late**: `BatchSpanProcessor` sends in batches; wait a few seconds after the call ends.
- **Turning on `allow_pii=True` for debugging and forgetting it**: make it an explicit environment setting, off in production unless your policy says otherwise.
- **Self-hosted Langfuse**: set `LANGFUSE_HOST` to your instance; the OTLP path is the same.
- **Span names**: they can change between releases; rely on the tree structure and attributes, not hard-coded names, in any automation.

---

## Lecture 10.4: Cost per minute: the number your boss will ask for

| Field | Value |
|---|---|
| ID | 10.4 |
| Title | Cost per minute: the number your boss will ask for |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 720 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | Cost per minute is usage times a price table divided by call minutes, and the breakdown shows where the money goes and how cascaded and realtime scale differently. |
| Prerequisites | 10.2; 6.4 (architecture comparison) |
| Files used | `src/maple/costs.py`, `tests/unit/test_costs.py`, `metrics/*.jsonl` (`call_summary` records) |

**Learning objectives**

1. Compute cost per minute from `UsageNumbers` and a `PriceTable` with `cost_breakdown`, and keep prices out of code.
2. Identify the largest cost component for cascaded and realtime Riley.
3. Explain why realtime cost per minute grows with call length while cascaded stays nearly flat.

### Script

[AVATAR]

"So what does Riley cost per minute?" [PAUSE] If you answer "it depends," you've lost the meeting. If you answer "six and a half cents a minute on the web, about seven point seven on the phone, and seventy percent of that is text-to-speech," you've won it. Let's build the calculator that gives you that answer.

[SLIDE 1: The formula]
- Cost = Σ (usage × unit price) for STT, LLM, TTS, realtime, platform, telephony
- Cost per minute = total ÷ call minutes
- Usage comes from `session.usage` (lecture 10.2)
- Prices come from YOUR invoices: every default is a placeholder

[AVATAR]

The formula is simple. For each component, usage times its unit price. Add them up. Divide by call minutes. The hard parts are getting accurate usage, which we did last lecture, and getting accurate prices. Which brings me to the most important warning in this lecture.

[SCREEN: `src/maple/costs.py`, the module docstring warning and `PRICES_LAST_CHECKED`.]

Every price in `DEFAULT_PRICES` is a placeholder. It says so in capital letters at the top of `src/maple/costs.py`, and in `PRICES_LAST_CHECKED`. Providers change prices constantly, and LiveKit Inference, direct provider plugins and enterprise contracts all differ. Copy the table, fill it in from your own invoices, and pass it in.

[CODE: `src/maple/costs.py`, `PriceTable` (highlight)]

```python
@dataclass(frozen=True)
class PriceTable:
    """Unit prices in US dollars. All values are placeholders; see module docstring."""

    stt_per_minute: float = 0.0077
    llm_input_per_million: float = 0.40
    llm_cached_input_per_million: float = 0.10
    llm_output_per_million: float = 1.60
    tts_per_million_chars: float = 50.0
    realtime_audio_input_per_million: float = 32.0
    realtime_audio_output_per_million: float = 64.0
    realtime_text_input_per_million: float = 4.0
    realtime_text_output_per_million: float = 16.0
    realtime_cached_input_per_million: float = 0.40
    platform_per_minute: float = 0.01
    telephony_per_minute: float = 0.0


DEFAULT_PRICES = PriceTable()
PHONE_PRICES = PriceTable(telephony_per_minute=0.0125)
```

Each field is a unit price in the unit the provider bills. STT per audio minute. LLM per million tokens, with cached input much cheaper. TTS per million characters. Realtime audio per million tokens, and look at the size of those two numbers compared with text. Platform per minute. Telephony per minute, zero for web calls, and about one and a quarter cents in `PHONE_PRICES`.

[CODE: `cost_breakdown` (the LLM line, highlight)]

```python
    components = {
        "stt": usage.stt_audio_seconds / 60.0 * prices.stt_per_minute,
        "llm": (
            uncached * prices.llm_input_per_million
            + usage.llm_cached_input_tokens * prices.llm_cached_input_per_million
            + usage.llm_output_tokens * prices.llm_output_per_million
        )
        / per_m,
        "tts": usage.tts_characters * prices.tts_per_million_chars / per_m,
        ...
        "platform": minutes * prices.platform_per_minute,
        "telephony": minutes * prices.telephony_per_minute,
    }
    return CostBreakdown(components={k: round(v, 6) for k, v in components.items()}, call_minutes=minutes)
```

`cost_breakdown` is exactly the formula. The one subtle line is the LLM: uncached prompt tokens at full price, cached ones at the cached price, plus output. It returns a `CostBreakdown` with each component, the total, cost per minute, and `largest_component()`, which answers "where does the money go?"

Let's use it. First, a real call from last lecture's metrics file.

[CODE: a quick script in the terminal]

```python
import json
from pathlib import Path

from maple.costs import PHONE_PRICES, cost_breakdown, usage_from_model_usage

path = next(Path("metrics").glob("*.jsonl"))                       # one call from lecture 10.2
summary = json.loads(path.read_text(encoding="utf-8").splitlines()[-1])  # the call_summary line
usage = usage_from_model_usage(summary["model_usage"], summary["call_seconds"])
print(cost_breakdown(usage).format())
print("as a phone call:", round(cost_breakdown(usage, PHONE_PRICES).per_minute, 4))
```

[DEMO: `uv run python` with the snippet; prints the component table for the recorded call and its per-minute cost, plus the phone-priced number.]

That's one real call. Now the bigger question: how do cascaded and realtime compare, and how does call length change things? `costs.py` includes two helpers with typical usage for a receptionist call, so we can compare shapes without making a hundred calls.

[CODE: comparing architectures]

```python
from maple.costs import cost_breakdown, typical_cascaded_usage, typical_realtime_usage

for minutes in (1, 3, 10):
    cascaded = cost_breakdown(typical_cascaded_usage(minutes))
    realtime = cost_breakdown(typical_realtime_usage(minutes))
    print(f"{minutes:>2} min  cascaded {cascaded.per_minute * 100:5.2f} c/min ({cascaded.largest_component()})"
          f"   realtime {realtime.per_minute * 100:5.2f} c/min ({realtime.largest_component()})")

print(cost_breakdown(typical_cascaded_usage(3)).format())
```

[DEMO: output:
```
 1 min  cascaded  6.35 c/min (tts)   realtime 12.97 c/min (realtime)
 3 min  cascaded  6.46 c/min (tts)   realtime 16.23 c/min (realtime)
10 min  cascaded  6.84 c/min (tts)   realtime 27.67 c/min (realtime)
stt            $0.0115
llm            $0.0173
tts            $0.1350
realtime       $0.0000
platform       $0.0300
telephony      $0.0000
total          $0.1938
per minute     $0.0646  (3.00 min)
```
]

Read the numbers. With these placeholder prices, a three-minute cascaded call costs about six and a half cents a minute. [PAUSE] And the biggest line isn't the LLM. It's text-to-speech: thirteen and a half cents of the nineteen-cent call. That surprises almost everyone. The LLM, `gpt-4.1-mini` with prompt caching, is under two cents for the whole call. So if the clinic wants Riley cheaper, the first conversation is with the TTS provider, or about shorter replies, not about the LLM.

Now realtime. About thirteen cents a minute for a one-minute call, sixteen for three minutes, and nearly twenty-eight for ten minutes. It grows, because every turn re-sends the conversation history as audio tokens. Cascaded barely moves, from six point three five to six point eight four. That's the shape I promised in lecture 6.4, now as numbers you can put in a spreadsheet.

[SLIDE 2: What moves the number]
- Shorter replies: fewer TTS characters (the biggest cascaded lever)
- Prompt caching: keep the system prompt stable so it caches
- Smaller prompts: trim tool results and old history
- Phone adds telephony per minute (about 1.25 cents in `PHONE_PRICES`)
- Realtime: keep calls short, or use the hybrid; compare with your own prices

[AVATAR]

What moves the number? Shorter replies, which also make Riley sound better on the phone. A stable system prompt, so it caches. Trimming tool results, which we found in the trace last lecture. And for Maple Street Dental's twelve hundred minutes a day, the difference between six and a half and sixteen cents is about a hundred and fourteen dollars a day. Roughly three thousand four hundred a month. That's why the architecture decision in Section 6 mattered.

[SLIDE 3: Presenting cost to a non-engineer]
- One number: cost per minute, web and phone
- One sentence: where the money goes ("70 percent is the voice")
- One comparison: cost of a human-answered minute
- One lever: what you'd change to reduce it, and the trade-off

[AVATAR]

Finally, how to present this to the person who asked. Give them one number: cost per minute, for web and for phone. One sentence about where the money goes. One comparison they already understand. A front-desk person costs the clinic something like thirty to fifty cents per minute of phone time when you include wages and overhead, so seven or eight cents is a very different conversation. And one lever: "If we shorten Riley's replies by a third, cost drops by about a fifth, and callers probably prefer it." [PAUSE] That's a two-minute conversation that ends with a decision, which is the whole point of measuring.

[AVATAR]

One more sanity check before you share numbers: reconcile with your invoices. At the end of the month, add up the `cost_total` of every `call_summary` line and compare it with what your providers actually billed. If they're within ten or fifteen percent, your price table is right. If not, something's missing: a platform fee, a minimum charge, or a model you forgot to price. [PAUSE] Do it once a month, and your cost-per-minute number becomes one people trust.

### Recap

Cost per minute is usage times your own price table divided by call minutes; for cascaded Riley, TTS is the biggest line, and realtime cost per minute grows with call length.

### Transition

Now let's turn these numbers into dashboards and alerts that tell you when something's wrong.

### Speaker notes: common mistakes and Q&A

- **Quoting placeholder prices**: always update `PriceTable` from invoices before sharing numbers. Put the date in `PRICES_LAST_CHECKED`.
- **Dividing by talk time instead of call time**: cost per minute uses wall-clock call minutes (`call_seconds`), including silence.
- **Forgetting telephony and platform**: web-call numbers understate phone costs. Use `PHONE_PRICES` or your own table.
- **Realtime usage priced as text**: pass `realtime=True` to `usage_from_model_usage` for speech-to-speech calls.
- **Coding exercise**: the cost-per-minute Udemy coding exercise has students implement a simplified `cost_breakdown`.

---

## Lecture 10.5: Dashboards and alerts that matter

| Field | Value |
|---|---|
| ID | 10.5 |
| Title | Dashboards and alerts that matter |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 640 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | A voice agent dashboard needs five numbers, p95 latency, cost per minute, transfer rate, containment rate and failed tool calls, each with an alert threshold and an owner. |
| Prerequisites | 10.1 to 10.4 |
| Files used | None (conceptual). Mock dashboard graphic. |

**Learning objectives**

1. Define containment rate and transfer rate from `call_outcome` and explain what healthy ranges look like for a receptionist.
2. Choose alert thresholds for p95 latency, cost per minute and failed tool calls, and avoid alert fatigue.
3. Connect each alert to a first diagnostic step using the traces and test suite from earlier lectures.

### Script

[AVATAR]

I've seen voice-agent dashboards with forty charts. Nobody looks at them. [PAUSE] Here's the dashboard I'd give Maple Street Dental. Five numbers. Each one has a threshold, an alert, and a first thing to check when it fires.

[SLIDE 1: The five numbers]
1. p95 voice-to-voice latency (per hour)
2. Cost per minute (per day)
3. Transfer rate (per day)
4. Containment rate (per day)
5. Failed tool calls (per hour)

[B-ROLL: mock dashboard with five big tiles: "p95 latency 1.47 s", "Cost/min 7.7¢", "Transfers 14%", "Contained 71%", "Tool failures 0.4%", each with a small sparkline.]

[AVATAR]

Number one, p95 voice-to-voice latency, per hour. Not the average. The ninety-fifth percentile, the same number our Section 9 budget checks. For Riley on the phone: alert if it's over one point six seconds for thirty minutes. First check: open the slowest traces and see which stage grew. Usually it's the LLM provider having a bad hour, or a prompt that got bigger.

Number two, cost per minute, per day, from the `call_summary` records. Alert if it's twenty percent above your baseline for a day. First check: the largest component. A prompt change that doubled the reply length shows up here before it shows up on the invoice.

[SLIDE 2: Outcome rates]
- Containment rate = calls resolved without a human ÷ all calls (booked, rescheduled, cancelled, answered)
- Transfer rate = transferred ÷ all calls
- Healthy receptionist range (illustrative): containment 60 to 80 percent, transfers 10 to 25 percent
- Both too high or too low is a signal

[AVATAR]

Numbers three and four come from `call_outcome`. Transfer rate is the share of calls handed to a human. Containment rate is the share resolved without one: booked, rescheduled, cancelled, or question answered.

Here's the subtle part. [PAUSE] Both directions are bad. If transfers jump from fifteen to forty percent, Riley is failing at something. Open the transcripts of transferred calls. If transfers drop to near zero, that's also suspicious. Maybe Riley stopped offering humans when she should, which is the "missed escalation" failure from lecture 9.1. The illustrative healthy range for a receptionist is something like sixty to eighty percent containment, and ten to twenty-five percent transfers. Your clinic will set its own.

Number five, failed tool calls per hour: any `ToolError` or exception in a tool. Alert at about two percent of tool calls. First check: the scheduler backend. If your practice-management system is down, this is the first number that moves, and it's how you learn before the patients tell you.

[SLIDE 3: Alert hygiene]
- Every alert has a threshold, a time window, and an owner
- Every alert links to a runbook step and a trace search
- Page a human only for things that hurt callers now (latency, tool failures)
- Everything else goes to a daily report
- Review thresholds monthly; delete alerts nobody acts on

[AVATAR]

Some alert hygiene. Every alert has a threshold, a time window, and an owner. Every alert links to its first diagnostic step: a trace search, or a test to run. Only page a human for things that hurt callers right now, like latency and tool failures. Cost and outcome rates go in a daily report. And once a month, delete any alert nobody acted on. An ignored alert is worse than no alert.

[SLIDE 4: From alert to fix]
- Alert fires → trace shows the stage → reproduce with a behavior test (9.3) or simulated caller (9.9)
- Fix → the new test stays in the suite → CI (9.10) prevents the regression
- Production is the top of the testing pyramid

[AVATAR]

And here's how it all connects. An alert fires. The trace shows the stage that broke. You reproduce it with a behavior test or a simulated caller. You fix it. The new test stays in the suite, and CI makes sure it never comes back. Production monitoring isn't separate from testing. It's the top of the pyramid.

[SLIDE 5: A weekly review, 15 minutes]
- Read the five numbers for the week, and their trend
- Listen to three calls: one transferred, one contained, one slow
- Pick one fix, add one test for it
- Review alert thresholds once a month

[AVATAR]

Dashboards only help if someone looks at them. So here's the ritual I recommend: fifteen minutes, once a week. Read the five numbers and their trend. Then listen to three calls: one that was transferred, one that Riley handled alone, and the slowest one. You'll learn more from those three recordings than from any chart. Then pick one fix, and add one test for it, so the fix sticks. [PAUSE] Once a month, review your alert thresholds. In a quarter, that's twelve fixes, twelve new tests, and a Riley that's measurably better than the one you launched.

[AVATAR]

Let me show you how the five numbers told a real story at a clinic like Maple Street Dental. One Monday, containment dropped from seventy-two to fifty-eight percent, and transfers doubled. Latency and cost were normal. The failed-tool-call tile was flat. [PAUSE] So nothing was broken, technically. Listening to three transferred calls explained it: the clinic had changed its insurance list over the weekend, the FAQ hadn't been updated, and callers asking about the new plan got "I'm not sure" and asked for a person. One FAQ edit, one new golden conversation, and containment was back the next day. No single chart would have told that story. The five together did.

### Recap

Watch five numbers, p95 latency, cost per minute, transfer rate, containment rate and failed tool calls, each with a threshold, an owner and a first diagnostic step.

### Transition

Time to build it yourself: Lab 6, a call-quality report from ten real calls.

### Speaker notes: common mistakes and Q&A

- **Averages on the dashboard**: use p95 latency and rates per time window.
- **No `call_outcome` for dropped calls**: calls that end abruptly may keep "in_progress"; count those separately, they're often the real problem.
- **Healthy ranges are illustrative**: every business sets its own targets after a few weeks of data.
- **Tools for dashboards**: Langfuse, Grafana, Datadog or a simple daily script over `metrics/*.jsonl` all work; start with the script (Lab 6).

---

## Lecture 10.6: Lab 6: Build a call-quality report

| Field | Value |
|---|---|
| ID | 10.6 |
| Title | Lab 6: Build a call-quality report |
| Type | LAB (guided lab; video intro/walkthrough) |
| Target duration | Video 2:00 (about 220 spoken words at ~140 wpm, plus slide and pause time); lab work about 45 minutes off-video |
| One idea | Turn ten real calls into a one-page report with latency, cost and outcomes. |
| Prerequisites | 10.1 to 10.5 |
| Files used | `04-labs/lab-06-observability.md`, `agents/s10_observed_agent.py`, `labs/lab06_report.py` (created in the lab), `tests/evals/latency_report.py` |

**Learning objectives**

1. Run ten scripted calls through the observed agent and collect their metrics files.
2. Produce a latency, cost and outcome report, and check it against the budget.
3. Write a one-page summary with three findings and one alert you'd set up.

### Script

[AVATAR]

This lab turns everything in Section 10 into one page you could hand to a clinic manager.

[SCREEN: `04-labs/lab-06-observability.md`: steps 1 to 6.]

Open `04-labs/lab-06-observability.md`. Step one installs the observability extra and, optionally, your Langfuse keys. Step two is a short tour of what the observed agent records. Step three: run ten calls with `uv run agents/s10_observed_agent.py console`, using the call list in the lab. A couple of them use `MAPLE_SIMULATED_LATENCY=1.5`, so you'll see a slow backend in your data. That's on purpose.

Step four, you'll write `labs/lab06_report.py`, a short script that reads every file in `metrics/` and prints latency percentiles, cost per minute and outcomes. Then check the same files against the budget with `uv run python tests/evals/latency_report.py metrics/*.jsonl`. Step five: open the traces for your slowest call and find the stage that caused it.

[SLIDE 1: Your one-page report]
- Headline numbers: p95 latency, cost per minute, containment, transfers
- Three findings, each with evidence (a number, a trace, or a transcript)
- One alert you'd set up, with threshold and first diagnostic step
- One next experiment

[AVATAR]

Step six is the deliverable: one page. Headline numbers. Three findings with evidence. One alert. One experiment you'd run next. Keep it to one page. That constraint is the skill.

[AVATAR]

A word on the slow calls. When you open their traces in step five, don't stop at "the tool was slow." Look at what Riley did while it was slow: did the filler speech play, and did the caller interrupt? That's the difference between a slow backend and a bad experience, and it's exactly the kind of finding that belongs in your report.

### Recap

Lab 6 turns ten calls into a latency, cost and outcome report with findings you can defend.

### Transition

Then take the short quiz to wrap up Section 10.

### Speaker notes: common mistakes and Q&A

- **Report finds no files**: different `METRICS_DIR`; pass the directory explicitly.
- **All calls look identical**: they skipped the `MAPLE_SIMULATED_LATENCY` calls; the slow calls are the interesting ones.
- **Cost looks wildly off**: placeholder prices, or realtime usage priced as text.

---

## Lecture 10.7: Quiz: Observability and cost

| Field | Value |
|---|---|
| ID | 10.7 |
| Title | Quiz: Observability and cost |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 100 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Check you can choose metrics, read a trace, and compute and explain cost per minute. |
| Prerequisites | 10.1 to 10.6 |
| Files used | `06-assessments/quizzes/section-10.md` (5 questions) |

**Learning objectives**

1. Recall where each metric comes from and which LiveKit APIs are current in 1.8.
2. Apply the cost formula and the dashboard thresholds to short scenarios.

### Script

[AVATAR]

Five questions. One asks which stage to investigate from a latency table. One asks what `allow_pii=False` keeps out of your traces. One gives you usage numbers and a price table and asks for the cost per minute. One asks why realtime cost per minute grows with call length. And one asks what a sudden drop in transfer rate might mean.

[SLIDE 1: Quiz: 5 questions]
- Metrics and traces
- Cost per minute
- Dashboards and alerts

[AVATAR]

For the cost question, write the formula down first: usage times unit price, summed, divided by call minutes. Then plug in the numbers.

Each answer links back to its lecture. About five minutes, and a calculator helps for one question.

### Recap

The quiz checks that you can measure, trace and price a voice agent, and know which numbers deserve alerts.

### Transition

Next up is Section 11, where we harden Riley against prompt injection, PII leakage and unsafe tool use.

### Speaker notes: common mistakes and Q&A

- Most-missed: "Transfer rate dropped to 1 percent: good news?" Answer: not necessarily; check for missed escalations.
- Students often divide cost by talk time; the formula uses call minutes.
