# LiveKit Agents Cheat Sheet

**Used in:** 3.2, 3.3, 3.6, 5.1, 6.2, 8.4, 9.3, 10.2
**Scope:** only the API forms verified for the course in curriculum §6 (**livekit-agents 1.8.3, pipecat-ai 1.12.0**).

> **APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates.**
> Anything not on this sheet: check the official docs for your installed version before using it.

---

## 1. Imports

```python
from livekit.agents import (
    Agent, AgentServer, AgentSession, JobContext, RunContext, ToolError,
    TurnHandlingOptions, EndpointingOptions, InterruptionOptions,
    cli, function_tool, get_job_context, inference, metrics, mock_tools,
)
from livekit.plugins import openai, silero
```

## 2. Server, entrypoint, session

```python
server = AgentServer()                       # prewarm: AgentServer(setup_fnc=prewarm)

@server.rtc_session()                        # agent name via LIVEKIT_AGENT_NAME or livekit.toml
async def entrypoint(ctx: JobContext) -> None:
    session = AgentSession(
        stt="deepgram/nova-3",               # LiveKit Inference model strings
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3",
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            endpointing=EndpointingOptions(min_delay=0.5, max_delay=3.0),
            interruption=InterruptionOptions(min_duration=0.5),
        ),
        userdata=CallState(),
    )
    await session.start(agent=Riley(), room=ctx.room)

if __name__ == "__main__":
    cli.run_app(server)
```

**CLI commands** (from `cli.run_app`): `console` · `dev` · `start` · `connect` · `download-files`

```bash
python agents/s03_hello_agent.py download-files   # once: model weights
python agents/s03_hello_agent.py console          # talk in your terminal
python agents/s03_hello_agent.py dev              # dev worker (Playground)
python agents/s03_hello_agent.py start            # production mode
```

For the `lk` CLI (projects, SIP trunks, dispatch rules, deploys), follow lectures 2.3, 8.2 and 12.3 and check `lk --help` for your installed version.

## 3. Turn handling knobs

| Option | Where | What it does |
|---|---|---|
| `turn_detection=inference.TurnDetector()` | `TurnHandlingOptions` | Semantic end-of-turn detection |
| `EndpointingOptions(min_delay=..., max_delay=...)` | `TurnHandlingOptions.endpointing` | How long to wait after speech before responding (seconds) |
| `InterruptionOptions(min_duration=...)` | `TurnHandlingOptions.interruption` | How long the caller must speak to interrupt |
| `silero.VAD.load()` | `AgentSession(vad=...)` | Voice activity detection |

**Don't use** the older idioms: `WorkerOptions(entrypoint_fnc=...)`, `room_input_options=`, `turn_detection=MultilingualModel()`, `from livekit.plugins.turn_detector...` (deprecated).

## 4. Tools

```python
class Riley(Agent):
    @function_tool
    async def book(self, context: RunContext[CallState], name: str, ...) -> str:
        """Book an appointment. (Docstring = tool description the LLM sees.)"""
        async with context.with_filler("One moment while I check.", delay=0.5):
            ...
        if slot_taken:
            raise ToolError("That time was just taken. Would another time work?")
        return "Booked for Tuesday at 2 PM."
```

- Tools are `@function_tool` methods on an `Agent`; signature `async def name(self, context: RunContext[CallState], arg: type, ...) -> str`.
- Raise `ToolError("speakable message")` for recoverable failures.
- **Handoff:** return another `Agent` instance (optionally with a message) from a tool.
- **Filler:** `async with context.with_filler("One moment while I check.", delay=0.5): ...`

## 5. Speech-to-speech (OpenAI Realtime)

```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel(model="gpt-realtime", voice="marin"),
)
```

## 6. Telephony

```python
# Transfer the caller to a human
await get_job_context().transfer_sip_participant(participant, "tel:+15551234567")

# Outbound call from inside a job
await ctx.add_sip_participant(call_to=..., trunk_id=..., participant_identity=...)
# ...or from a script via the LiveKit API: CreateSIPParticipantRequest
```

Use fictional `555-01XX` numbers in docs and videos.

## 7. Metrics and usage

```python
@session.on("metrics_collected")      # still works in 1.8 (logs a deprecation notice)
def _on_metrics(ev):                  # MetricsCollectedEvent
    metrics.log_metrics(ev.metrics)   # per-stage detail: EOU, STT, LLM TTFT, TTS TTFB

# totals and cost: read session.usage when the call ends
async def log_usage():
    model_usage = [u.model_dump() for u in session.usage.model_usage]
    usage = usage_from_model_usage(model_usage, call_seconds)   # src/maple/costs.py
    report = cost_breakdown(usage)

ctx.add_shutdown_callback(log_usage)
```

Per-turn latency is also on each assistant message: `ChatMessage.metrics["e2e_latency"]`. `metrics.UsageCollector` is deprecated in livekit-agents 1.8 and the course does not use it. Full version: `attach_observers` in `agents/s10_observed_agent.py`.

## 8. Testing (pytest-asyncio)

```python
async with AgentSession(llm=judge_llm) as session:
    await session.start(Riley())
    result = await session.run(user_input="I'd like to book a cleaning on Tuesday")

    result.expect.skip_next_event_if(type="message", role="assistant")
    result.expect.next_event().is_function_call(name="find_available_slots", arguments={...})
    result.expect.next_event().is_function_call_output(is_error=False)
    await result.expect.next_event().is_message(role="assistant").judge(
        judge_llm, intent="Offers available times without inventing any"
    )
    result.expect.no_more_events()

# anywhere in the events
result.expect.contains_function_call(name="book_appointment")

# force paths deterministically
with mock_tools(Riley, {"find_available_slots": fake_no_slots}):
    ...
```

> `.judge(...)` is a coroutine in livekit-agents 1.8, so it is awaited, as in `tests/agent/test_greeting.py`.

## 9. Pipecat 1.12 names (Section 14)

| Concept | Name / module |
|---|---|
| Pipeline | `Pipeline`, `PipelineWorker` + `PipelineParams` (`pipecat.pipeline.worker`), `WorkerRunner` (`pipecat.workers.runner`). `PipelineTask` and `PipelineRunner` are deprecated aliases since 1.3 |
| Services | `DeepgramSTTService`, `OpenAILLMService`, `CartesiaTTSService` |
| VAD | `SileroVADAnalyzer` |
| Context | `LLMContext` in `pipecat.processors.aggregators.llm_context`; universal aggregators in `pipecat.processors.aggregators.llm_response_universal` |
| Tools | `FunctionSchema` in `pipecat.adapters.schemas.function_schema` |
| Runner types | `pipecat.runner.types` |

**Don't use** Pipecat's removed `openai_llm_context` module.
