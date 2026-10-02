# Section 14 (optional): Pipecat and Choosing Your Stack

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈32 min (4 lectures). **Optional section** (curriculum v1.1): nothing later in the course depends on it.
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with the agent. Record the real audio. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only (narration plus scripted demo dialogue), not cues or code.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 14.1 | Pipecat's frame pipeline model | SL | 7:00 | ~890 |
| 14.2 | Code-along: Riley booking flow in Pipecat | SC | 12:00 | ~1,100 |
| 14.3 | LiveKit Agents vs Pipecat vs managed platforms | SL | 8:00 | ~890 |
| 14.4 | Quiz: Choosing a stack | QZ | 5:00 (1:00 video) | ~120 |

**Verification note for the editor.** Every Pipecat import in this section was checked against `pipecat-ai` 1.12.0 and matches `03-code/pipecat/s14_pipecat_bot.py`. In 1.12, `PipelineTask` and `PipelineRunner` still import but print deprecation warnings: since 1.3 they are `PipelineWorker` (`pipecat.pipeline.worker`) and `WorkerRunner` (`pipecat.workers.runner`). The curriculum table still says `PipelineTask`/`PipelineRunner`; the scripts use the new names and explain the rename, because most tutorials online still use the old ones. Service options use the `settings=Service.Settings(...)` style; passing `model=` or `voice_id=` directly is deprecated in 1.12.

---

## Lecture 14.1 — Pipecat's frame pipeline model

| Field | Value |
|---|---|
| ID | 14.1 |
| Type | SL (slides + avatar) |
| Target duration | 7:00 (~890 spoken words) |
| Learning objectives | 1. Explain frames, frame processors, transports and the direction frames flow. 2. Describe the roles of `Pipeline`, `PipelineWorker` (formerly `PipelineTask`), `WorkerRunner` (formerly `PipelineRunner`) and `LLMContext`. 3. Map each piece of the LiveKit `AgentSession` you know onto its Pipecat equivalent. |
| Prerequisites | Sections 3 and 5 (LiveKit pipeline and tools). Section is optional. |
| Files used | `pipecat/s14_pipecat_bot.py` (the pipeline list and the aggregators, shown briefly) |

### Script

[AVATAR]
For thirteen sections, we've built Riley on LiveKit Agents. It's a great framework. But it's not the only serious open-source option. The other one you'll hear about constantly is Pipecat.

Here's why this section exists. You shouldn't pick a framework because it's the one your course used. You should pick it because you understand the trade-offs. And the fastest way to understand them is to build the same thing twice.

[SLIDE 1: This section is optional]
- Nothing in Section 15 depends on it
- Short on time? Jump to 14.3, the comparison
- Choosing a stack for a real project? Watch all three

One thing first. This section is optional. Nothing in Section 15 depends on it, and your capstone is complete without it. If you're short on time, you can skip to Lecture 14.3, the comparison, which is useful even if you never write a line of Pipecat. But if you're choosing a stack for a real project, the full section is worth your thirty minutes.

So in this lecture, the mental model. Next lecture, Riley's booking flow in Pipecat. Then we compare everything, including the managed platforms.

[SLIDE 2: Pipecat in one sentence]
- An open-source Python framework for real-time voice and multimodal agents
- Created by Daily, BSD-licensed, large contributor community
- Everything is a frame, flowing through a pipeline of processors

Pipecat is an open-source Python framework for real-time voice and multimodal agents. It started at Daily, the WebRTC company, and it has a big community around it.

And its core idea fits in one sentence. Everything is a frame, flowing through a pipeline of processors.

[SLIDE 3: Frames]
- A frame is a small typed message
- Audio frames: raw caller audio, synthesized speech
- Text frames: transcriptions, LLM tokens
- Control frames: start, end, interruptions, "user started speaking"

Let's unpack that. A frame is a small, typed message. Some frames carry data. An audio frame carries twenty milliseconds or so of sound. A transcription frame carries text from the speech-to-text service. An LLM text frame carries a few tokens.

Other frames carry signals. "The user started speaking." "The user stopped speaking." "Interrupt now." "End of the pipeline." Those control frames are how Pipecat does turn-taking and barge-in.

[SLIDE 4: Processors and the pipeline]
Diagram, left to right: `transport.input()` → `stt` → `user aggregator` → `llm` → `tts` → `transport.output()` → `assistant aggregator`
- Each box is a frame processor
- Frames flow downstream (left to right) and upstream (right to left)
- A processor handles frames it knows and passes the rest along

A frame processor is a box that receives frames, does something, and pushes frames on. The speech-to-text service is a processor. It eats audio frames and emits transcription frames. The LLM service is a processor. It eats a context and emits text frames. The TTS service eats text and emits audio.

[SCREEN: `pipecat/s14_pipecat_bot.py`, scrolled to `pipeline = Pipeline([...])`: the seven boxes from the slide, as real code.]

Chain those boxes in a list, and you have a pipeline. Here's Riley's pipeline. Transport input, STT, user aggregator, LLM, TTS, transport output, assistant aggregator.

Frames flow both ways. Most go downstream, left to right. Some go upstream. For example, when the caller interrupts, a signal travels back so the TTS stops talking.

And each processor only handles the frames it cares about. Everything else passes straight through. That's what makes it easy to drop a custom processor anywhere in the chain.

[SLIDE 5: Transports]
- Transport = how audio gets in and out
- WebRTC in the browser (SmallWebRTC, Daily), LiveKit rooms, telephony WebSockets (Twilio, Telnyx, Plivo, Exotel)
- `transport.input()` starts the pipeline, `transport.output()` ends it

The first and last boxes are the transport. The transport is how audio gets in and out. Pipecat supports several. Peer-to-peer WebRTC for local development. Daily rooms. LiveKit rooms. And telephony providers over WebSockets, like Twilio.

That's one big design difference from LiveKit Agents. In LiveKit, the transport is LiveKit. In Pipecat, the transport is a plug-in.

[SLIDE 6: Context and aggregators]
- `LLMContext`: the conversation history and the tools
- User aggregator: collects transcription frames into a user message
- Assistant aggregator: collects spoken text into an assistant message
- `LLMContextAggregatorPair(context)` gives you both

Now, the conversation memory. Pipecat keeps it in an `LLMContext` object. It holds the messages and the tools.

Two processors keep that context up to date. The user aggregator sits after STT. It collects transcription frames until the caller finishes their turn, then adds one user message and triggers the LLM. The assistant aggregator sits at the very end. It collects what Riley actually said and adds that as the assistant message.

[B-ROLL: an interrupted reply. Riley's sentence is cut at "nine thirty or"; only the spoken words drop into the assistant aggregator's box, and the rest fades out.]

Why at the very end? Because if the caller interrupts, only the words that were actually spoken should go into history. Same idea as LiveKit truncating an interrupted reply.

And there's one more benefit of frames that's easy to miss. Because everything flows as frames, you can observe everything. Pipecat has observers that watch frames go by without changing them. That's how its metrics and tracing work: time to first byte, token usage, turn timing. The same numbers we collected in Section 10, from a different angle.

[CODE: from `pipecat/s14_pipecat_bot.py`]
```python
    context = LLMContext(tools=TOOLS)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )
```

You create both with one line. `LLMContextAggregatorPair`, passing in the context. In Pipecat 1.12, these live in `pipecat.processors.aggregators.llm_response_universal`. They're called universal because they work with any LLM service.

[SLIDE 7: Worker and runner]
- `Pipeline([...])`: the list of processors
- `PipelineWorker(pipeline, params=PipelineParams(...))`: runs one conversation
- `WorkerRunner()`: add the worker, `run()` it, handles signals and shutdown
- Older names (pre-1.3): `PipelineTask` and `PipelineRunner`. They still work in 1.12, with deprecation warnings

Three objects run the show. `Pipeline` is the list of processors. `PipelineWorker` runs one conversation through that pipeline. It takes `PipelineParams` for things like metrics. And `WorkerRunner` manages the lifecycle, like stopping cleanly on Control-C.

A quick warning, because you will hit this. Almost every Pipecat tutorial online says `PipelineTask` and `PipelineRunner`. Those were the names before version 1.3. In 1.12 they still work, but you get deprecation warnings. We'll use the new names.

[SLIDE 8: LiveKit to Pipecat translation]
| LiveKit Agents | Pipecat |
|---|---|
| `AgentSession(stt, llm, tts, vad)` | `Pipeline([...])` + services |
| `Agent(instructions=...)` | `system_instruction` in LLM settings + `LLMContext` |
| `@function_tool` | `FunctionSchema` + `llm.register_function(...)` |
| `RunContext` | `FunctionCallParams` |
| `session.generate_reply()` | queue an `LLMRunFrame` |
| `AgentServer` + `cli.run_app` | `bot()` + `pipecat.runner.run.main()`, `WorkerRunner` |
| `llm_node` / `tts_node` override | a custom frame processor |

Here's the translation table you'll want next to you in the code-along.

An `AgentSession` becomes a pipeline plus services. An `Agent`'s instructions become the LLM's system instruction. A `@function_tool` becomes a `FunctionSchema` plus a registered handler function. `RunContext` becomes `FunctionCallParams`. Generating a reply becomes queuing an `LLMRunFrame`. And the agent server becomes a `bot` function, started by Pipecat's development runner.

Notice the last row. In LiveKit, we overrode `llm_node` in Section 11 to guard Riley's output. In Pipecat, you'd write a small frame processor and put it between the LLM and TTS. Different shape, same idea.

[AVATAR]
So here's the mental model to take into the next lecture. LiveKit gives you an agent and a session, and you customize through hooks. Pipecat gives you the pipeline itself, and you customize by adding boxes. Neither is better. They're different levels of abstraction. Let's feel the difference by typing it.

[SLIDE 9: Recap]
- Everything is a frame, flowing through processors
- Transports are plug-ins at both ends of the pipeline
- `PipelineWorker` and `WorkerRunner` replace Task and Runner

**Recap:** Pipecat moves typed frames through a pipeline of processors, with a transport at each end, an `LLMContext` for memory, and a worker and runner to execute it.

**Transition:** Next, we'll rebuild Riley's booking flow in Pipecat 1.12, line by line.

### Speaker notes: common student mistakes / Q&A

- "Is Pipecat tied to Daily?" No. Daily created it and offers hosting, but the transports are pluggable, including LiveKit rooms and Twilio WebSockets.
- Students copy old tutorials that import from `pipecat.processors.aggregators.openai_llm_context`. That module is gone. Use `LLMContext` and the universal aggregators.
- Order matters. If the assistant aggregator goes before `transport.output()`, interrupted text lands in history as if it was spoken.
- "Why does my copy print `PipelineTask is deprecated`?" You're following an older tutorial. Use `PipelineWorker` and `WorkerRunner`, as in the repo.
- "Should I learn both?" Learn the concepts of both. Build production on one, so your tests and runbooks stay in one place.

---

## Lecture 14.2 — Code-along: Riley booking flow in Pipecat

| Field | Value |
|---|---|
| ID | 14.2 |
| Type | SC (screencast / code-along) |
| Target duration | 12:00 (~1,100 spoken words; the rest is screen, typing and demo time) |
| Learning objectives | 1. Build a Pipecat 1.12 bot with Deepgram STT, OpenAI LLM, Cartesia TTS and Silero VAD. 2. Define tools with `FunctionSchema` and `ToolsSchema`, and handle them with `FunctionCallParams` and `result_callback`. 3. Run the bot with the Pipecat development runner and talk to it in the browser. |
| Prerequisites | 14.1; 5.2 (the scheduler). Section is optional. |
| Files used | `pipecat/s14_pipecat_bot.py`, `src/maple/scheduler.py`, `src/maple/prompts.py`, `src/maple/config.py`, `.env` |

### Script

[AVATAR]
Same clinic. Same scheduler. Same prompt. Different framework. By the end of this lecture, you'll talk to a Pipecat version of Riley in your browser, and it'll book a real slot in our clinic calendar.

We'll build the booking core: find slots, book, reschedule and cancel. No handoffs, no guardrails. That's enough to see every moving part.

[SCREEN: Terminal, repo root. Footer: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."]

First, dependencies. Pipecat is an optional extra in our `pyproject.toml`, so the LiveKit sections never had to install it.

```bash
uv sync --extra pipecat
```

That pulls in `pipecat-ai` 1.12 with its provider extras. Pipecat talks to providers directly, not through LiveKit Inference, so your `.env` needs `DEEPGRAM_API_KEY`, `OPENAI_API_KEY` and `CARTESIA_API_KEY`.

[SCREEN: `pipecat/s14_pipecat_bot.py`, the module docstring with the comparison table.]

Open `pipecat/s14_pipecat_bot.py`. The docstring at the top is the translation table from the last lecture. Keep it on screen while we go.

Step one. Imports. There are quite a few, so let me group them.

[CODE: imports and setup]
```python
import os
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402
from loguru import logger  # noqa: E402
from pipecat.adapters.schemas.function_schema import FunctionSchema  # noqa: E402
from pipecat.adapters.schemas.tools_schema import ToolsSchema  # noqa: E402
from pipecat.audio.vad.silero import SileroVADAnalyzer  # noqa: E402
from pipecat.frames.frames import LLMRunFrame  # noqa: E402
from pipecat.pipeline.pipeline import Pipeline  # noqa: E402
from pipecat.pipeline.worker import PipelineParams, PipelineWorker  # noqa: E402
from pipecat.processors.aggregators.llm_context import LLMContext  # noqa: E402
from pipecat.processors.aggregators.llm_response_universal import (  # noqa: E402
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments  # noqa: E402
from pipecat.runner.utils import create_transport  # noqa: E402
from pipecat.services.cartesia.tts import CartesiaTTSService  # noqa: E402
from pipecat.services.deepgram.stt import DeepgramSTTService  # noqa: E402
from pipecat.services.llm_service import FunctionCallParams  # noqa: E402
from pipecat.services.openai.llm import OpenAILLMService  # noqa: E402
from pipecat.transports.base_transport import BaseTransport, TransportParams  # noqa: E402
from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams  # noqa: E402
from pipecat.workers.runner import WorkerRunner  # noqa: E402

from maple import prompts  # noqa: E402
from maple.config import load_settings, split_model  # noqa: E402
from maple.scheduler import ClinicScheduler, SchedulerError  # noqa: E402

load_dotenv(_ROOT / ".env", override=True)

KEYTERMS = ["Maple Street Dental", "Riley", "hygienist", "crown", "root canal"]
```

The path line at the top makes `src` importable when you run the file directly. Then Pipecat, in groups: schemas, VAD, frames, pipeline and worker, context and aggregators, runner helpers, the three services, transports and `WorkerRunner`. Remember the 1.3 renames from last lecture: `PipelineWorker` and `WorkerRunner` are the current names.

At the bottom, our own code. `prompts`, `load_settings` and the `ClinicScheduler`. Plus a short list of keyterms for Deepgram, the same idea as Lecture 8.3. That's the payoff of keeping business logic in `src/maple`. It moves between frameworks untouched.

Step two. Tool schemas. This is what the LLM sees.

[CODE: tool schemas]
```python
FIND_SLOTS = FunctionSchema(
    name="find_available_slots",
    description="Look up free appointment times. Always call this before offering times.",
    properties={
        "day": {
            "type": "string",
            "description": 'ISO date such as 2026-10-06, or words such as "tomorrow" or "Thursday".',
        },
        "part_of_day": {"type": "string", "enum": ["morning", "afternoon", "any"]},
    },
    required=["day"],
)
BOOK = FunctionSchema(
    name="book_appointment",
    description="Book a new appointment. Only call after reading the details back and the caller said yes.",
    properties={
        "patient_name": {"type": "string", "description": "The patient's full name."},
        "phone": {"type": "string", "description": "Ten digit callback number."},
        "slot_start": {"type": "string", "description": "slot_start from find_available_slots."},
        "reason": {"type": "string", "description": "Short reason, e.g. cleaning."},
    },
    required=["patient_name", "phone", "slot_start", "reason"],
)
RESCHEDULE = FunctionSchema(
    name="reschedule_appointment",
    description="Move the caller's next appointment to a new slot after they confirm.",
    properties={
        "phone": {"type": "string", "description": "Phone number the appointment is under."},
        "new_slot_start": {"type": "string", "description": "slot_start of the new time."},
    },
    required=["phone", "new_slot_start"],
)
CANCEL = FunctionSchema(
    name="cancel_appointment",
    description="Cancel the caller's next appointment after they confirm.",
    properties={"phone": {"type": "string", "description": "Phone number the appointment is under."}},
    required=["phone"],
)
TOOLS = ToolsSchema(standard_tools=[FIND_SLOTS, BOOK, RESCHEDULE, CANCEL])
```

Here's the first big difference from LiveKit. In LiveKit, `@function_tool` read the Python signature and the docstring and built this schema for us. In Pipecat, we write it explicitly. A name. A description. Properties in JSON Schema. And the required list.

More typing, but you see exactly what the model sees. And notice we kept the same tool names and argument names as the LiveKit version: `find_available_slots`, `slot_start`, and so on. That means our Section 9 transcripts, tests and judges still make sense.

`ToolsSchema` wraps the list. It's provider-neutral, so the same schemas work with other LLM services.

Step three. The tool logic.

[CODE: tool logic (two of the four functions)]
```python
def find_slots_result(scheduler: ClinicScheduler, args: dict[str, Any]) -> dict[str, Any]:
    """Return offered slots, or the next available ones, or a speakable error."""
    try:
        slots = scheduler.find_slots(args["day"], args.get("part_of_day", "any"), limit=3)
        if not slots:
            slots = scheduler.next_available(args["day"], args.get("part_of_day", "any"), limit=3)
    except SchedulerError as exc:
        return {"error": str(exc)}
    return {"slots": [{"spoken": prompts.speak_slot(s.start), "slot_start": s.iso} for s in slots]}


def book_result(scheduler: ClinicScheduler, args: dict[str, Any]) -> dict[str, Any]:
    """Book and return a speakable confirmation, or a speakable error."""
    try:
        appt = scheduler.book(args["patient_name"], args["phone"], args["slot_start"], args["reason"])
    except SchedulerError as exc:
        return {"error": str(exc)}
    return {"booked": f"{appt.patient_name}, {prompts.speak_slot(appt.start)}"}
```

Plain Python functions: the scheduler and the arguments in, a dictionary out. No Pipecat in sight, so you can unit test them without a pipeline.

Look at the error handling. In LiveKit, we raised `ToolError` with a speakable message. Here, we return an `error` field instead. Our scheduler's exception messages were written to be spoken aloud, so the LLM can pass them straight to the caller.

And each slot comes back twice: a spoken version, "Tuesday, October sixth at nine thirty in the morning," and a machine version for booking. Same voice-first trick from Section 4.

Now we connect those functions to the LLM.

[CODE: `register_tools`]
```python
def register_tools(llm: OpenAILLMService, scheduler: ClinicScheduler) -> None:
    """Register one Pipecat handler per tool. Each handler reports via ``result_callback``."""
    handlers = {
        "find_available_slots": find_slots_result,
        "book_appointment": book_result,
        "reschedule_appointment": reschedule_result,
        "cancel_appointment": cancel_result,
    }
    for name, fn in handlers.items():

        async def handler(params: FunctionCallParams, fn: Any = fn) -> None:
            result = fn(scheduler, dict(params.arguments))
            logger.info(f"{params.function_name} -> {result}")
            await params.result_callback(result)

        llm.register_function(name, handler)
```

`register_tools` loops over tool names and functions and defines a small async handler for each. The handler gets `FunctionCallParams`, calls our plain function with `params.arguments`, logs the result, and hands it back through `params.result_callback`. In Pipecat, you don't return a tool result. You call the callback.

One Python detail. See `fn: Any = fn` in the handler's signature? That captures the current function at definition time. Without it, every handler in the loop would call the *last* function, `cancel_result`. That's a classic Python closure bug, and it would make every tool cancel appointments. Not a bug you want in a dental clinic.

Step four. Transport options.

[CODE: transport params]
```python
TRANSPORT_PARAMS = {
    "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True),
    "twilio": lambda: FastAPIWebsocketParams(audio_in_enabled=True, audio_out_enabled=True),
}
```

The development runner can serve several transports. Browser WebRTC for development. And Twilio's media-stream WebSocket for phone calls. We'll use WebRTC today.

Step five. The pipeline itself.

[CODE: `run_bot`, part 1: calendar, services, tools]
```python
async def run_bot(transport: BaseTransport, runner_args: RunnerArguments) -> None:
    """Build STT -> LLM -> TTS with tools and run it until the caller leaves."""
    settings = load_settings()
    scheduler = ClinicScheduler.with_demo_data(settings.today_override)

    stt = DeepgramSTTService(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        settings=DeepgramSTTService.Settings(model=split_model(settings.stt_model)[1], keyterm=KEYTERMS),
    )
    llm = OpenAILLMService(
        api_key=os.environ["OPENAI_API_KEY"],
        settings=OpenAILLMService.Settings(
            model=split_model(settings.llm_model)[1],
            system_instruction=prompts.build_instructions(today=scheduler.today, booking=True),
        ),
    )
    tts = CartesiaTTSService(
        api_key=os.environ["CARTESIA_API_KEY"],
        settings=CartesiaTTSService.Settings(
            model=split_model(settings.tts_model)[1], voice=settings.tts_voice
        ),
    )
    register_tools(llm, scheduler)
```

First, the calendar, with the same demo patients as the LiveKit version.

Then three services. Each takes an API key and a `Settings` object, the current Pipecat pattern; passing `model=` directly is deprecated in 1.12. `split_model` turns our LiveKit-style "deepgram slash nova three" into just "nova three". Deepgram also gets our keyterms, so "Maple Street Dental" and "root canal" come through correctly.

The system instruction comes from the same `build_instructions` function the LiveKit agents use, with the booking rules switched on. Then we register the tools.

[CODE: `run_bot`, part 2: context, pipeline, worker, runner]
```python
    context = LLMContext(tools=TOOLS)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(vad_analyzer=SileroVADAnalyzer()),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )
    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
    )
    runner = WorkerRunner(handle_sigint=runner_args.handle_sigint)
    await runner.add_workers(worker)
```

The context holds our tools. `LLMContextAggregatorPair` gives us the user and assistant aggregators. And in 1.12, VAD goes on the user aggregator's params: Silero decides when the caller is speaking, and the aggregator decides when the turn is over.

Then the pipeline. Read it out loud with me. Transport in. STT. User aggregator. LLM. TTS. Transport out. Assistant aggregator. That's the whole voice loop, in seven lines, in order.

The worker runs that pipeline, with metrics on. Those metrics give you time to first byte for each service, the same numbers we tracked in Section 10. And the `WorkerRunner` manages the worker's lifecycle.

[CODE: `run_bot`, part 3: events]
```python
    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport: BaseTransport, client: Any) -> None:
        logger.info("caller connected")
        context.add_message({"role": "developer", "content": f"Greet the caller with: {prompts.GREETING}"})
        await worker.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport: BaseTransport, client: Any) -> None:
        logger.info("caller disconnected")
        await runner.cancel()

    await runner.run()
```

Two event handlers. When the browser connects, we add an instruction to the context, "greet the caller with" our standard greeting, and queue an `LLMRunFrame`. That frame tells the LLM to run now, so Riley speaks first. It's the Pipecat version of `on_enter`. When the browser disconnects, we cancel the runner, so nothing keeps running and billing.

Then `runner.run` blocks until the conversation ends.

[CODE: entry point]
```python
async def bot(runner_args: RunnerArguments) -> None:
    """Entry point discovered by ``pipecat.runner.run.main``."""
    transport = await create_transport(runner_args, TRANSPORT_PARAMS)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
```

Finally, the entry point. The development runner looks for a function called `bot`. It builds the transport the client asked for, and hands it to `run_bot`. And `main`, from `pipecat.runner.run`, starts a small web server that calls `bot` for each new connection.

[SCREEN: Terminal.]
```bash
uv run python pipecat/s14_pipecat_bot.py
```

[SCREEN: Log shows the runner starting on `http://localhost:7860`. Open `http://localhost:7860/client` in the browser. Click Connect. Allow the microphone.]

The runner prints a local address. Open slash client in your browser, click connect, and allow the microphone.

[DEMO: Browser session with the Pipecat bot. `MAPLE_TODAY=2026-10-05` in `.env`, so "tomorrow" is Tuesday, October sixth.]

**Riley:** Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?

**You:** I'd like a cleaning tomorrow afternoon.

**Riley:** Sure. Tomorrow afternoon I have one o'clock, one thirty or two o'clock. Which works best?

**You:** One thirty. I'm Ana Gomez, five one two, five five five, zero one eight eight.

**Riley:** Thanks, Ana. Just to confirm: a cleaning on Tuesday, October sixth at one thirty in the afternoon, and we'll reach you at five one two, five five five, zero one eight eight. Shall I go ahead?

**You:** Yes, please.

**Riley:** You're booked for Tuesday at one thirty. Just so you know, we ask for twenty-four hours' notice to cancel. Anything else?

[SCREEN: Terminal log. Highlight the `find_available_slots -> {...}` and `book_appointment -> {...}` lines, and a metrics line with TTFB values.]

In the logs, there's the slot lookup, the booking, and the metrics with time to first byte for each service.

And if you want to try the phone, the docstring has the Twilio command. It needs a public tunnel like ngrok, so check the Pipecat docs for the current setup.

[AVATAR]
So that's Riley in Pipecat. About two hundred and sixty lines, including four tools, and it reused all of our business logic. Here's what I want you to notice. The pipeline is right there in your code. Every box is visible, and you can put a new one anywhere. In LiveKit, the session owned that loop, and we customized it through hooks. Keep that difference in mind for the next lecture.

[SLIDE 1: Recap]
- Explicit `FunctionSchema`s plus handlers that call back
- Seven processors in one visible pipeline list
- Same `src/maple` business logic, unchanged

**Recap:** A Pipecat bot is services plus explicit tool schemas plus a pipeline list, run by a `PipelineWorker` and a `WorkerRunner` under the development runner, and our `src/maple` logic carries over unchanged.

**Transition:** Next, we'll put LiveKit Agents, Pipecat and the managed platforms side by side, and build a decision matrix.

### Speaker notes: common student mistakes / Q&A

- Mistake: defining handlers in a loop without the `fn=fn` default argument. Every tool then runs the last function in the loop. Show the bug live if time allows; it sticks.
- Mistake: the schema name and the `register_function` name differ by one character. The model calls the tool and nothing answers. Keep names in one dictionary, as `register_tools` does.
- Mistake: forgetting `await params.result_callback(...)` on a code path. The LLM waits for a result that never arrives.
- "Where did VAD go? Old examples put it on the transport." In Pipecat 1.12, pass `vad_analyzer` in `LLMUserAggregatorParams`. Transport-level VAD examples online are from older versions.

---

## Lecture 14.3 — LiveKit Agents vs Pipecat vs managed platforms

| Field | Value |
|---|---|
| ID | 14.3 |
| Type | SL (slides + avatar) |
| Target duration | 8:00 (~890 spoken words) |
| Learning objectives | 1. Compare LiveKit Agents, Pipecat and managed platforms (Vapi, Retell, ElevenLabs Agents, Bland) on control, cost, compliance and lock-in. 2. Use a build-vs-buy decision matrix for a real project. 3. Explain how the testing and observability skills from this course transfer to any option. |
| Prerequisites | 14.1, 14.2; Sections 9 and 10 |
| Files used | `10-resources/architecture-decision-matrix.md`; `tests/agent/test_greeting.py` and `src/maple/costs.py` (shown briefly) |

> **Claims policy for this lecture.** Platform prices, compliance offerings and feature lists change often. Keep all statements qualitative. Before recording, check each vendor's current pricing and compliance pages and add a dated on-screen note: "Vendor details checked on <date>; verify before deciding." Do not show specific per-minute prices.

### Script

[AVATAR]
A clinic owner asks you a simple question. "Should we build this, or just sign up for one of those voice AI platforms?"

That's a great question. And "it depends" is not a great answer. So let's build a better one.

[SLIDE 1: Three ways to ship a voice agent]
- Framework on your infrastructure: LiveKit Agents or Pipecat, self-hosted
- Framework with managed hosting: LiveKit Cloud, Pipecat Cloud
- Managed voice platform: Vapi, Retell, ElevenLabs Agents, Bland

There are really three ways to ship a voice agent.

One. An open-source framework on your own infrastructure. LiveKit Agents or Pipecat, running in your containers.

Two. The same frameworks, with managed hosting from the framework vendor. That's what we did with LiveKit Cloud in Section 12. Pipecat has a similar hosted option.

Three. A managed voice platform. Vapi, Retell, ElevenLabs Agents, Bland, and others. You configure an agent through a dashboard or an API, and they run the whole pipeline.

[SLIDE 2: LiveKit Agents vs Pipecat]
| | LiveKit Agents | Pipecat |
|---|---|---|
| Abstraction | Agent + session; customize via hooks and nodes | Explicit pipeline; customize by adding processors |
| Transport | LiveKit rooms (WebRTC) and LiveKit SIP | Pluggable: WebRTC, Daily, LiveKit, telephony WebSockets |
| Tools | `@function_tool` from signatures | Explicit `FunctionSchema` + handlers |
| Testing | Built-in text-session test framework | Bring more of your own harness |
| Scaling | Agent server with dispatch and load balancing | Your process model or Pipecat Cloud |
| Languages | Python and Node.js | Python |

Let's start with the two frameworks. You've now built Riley in both.

Abstraction. LiveKit gives you an agent and a session. You customize through hooks, like `on_user_turn_completed` and `llm_node`. Pipecat gives you the pipeline itself. You customize by adding processors.

Transport. LiveKit is built on LiveKit's own WebRTC infrastructure, with SIP for phones. Pipecat treats transport as a plug-in. That matters if you're already on a specific telephony or WebRTC provider.

Tools. LiveKit builds schemas from your Python signatures. Pipecat has you write them explicitly.

[SCREEN: `tests/agent/test_greeting.py`, the `session.run(user_input=...)` line and the `.judge(...)` call: the built-in harness this whole course relied on.]

Testing. This one mattered a lot in this course. LiveKit's built-in test framework gave us `session.run`, `expect` and judges in Section 9. With Pipecat, you'll build more of that harness yourself.

And scaling. LiveKit's agent server handles dispatch and load balancing across workers, which we used in Section 12. With Pipecat, you design the process model, or use their hosted service.

[SLIDE 3: Managed platforms: what you get]
- Fastest path to a first working call
- Dashboard configuration, built-in phone numbers and analytics
- Hosting, scaling and provider integrations handled for you
- Often a no-code or low-code editor for non-engineers

Now the managed platforms. Here's what they do really well. Speed. You can have a working phone agent in an afternoon. They handle hosting, scaling, phone numbers and provider integrations. Many have dashboards where a non-engineer can edit the prompt. For a small business validating an idea, that's powerful.

They're not all the same, either. Some started as developer APIs, and expect you to call them from code. Some lean toward no-code builders for business users. Some grew out of a speech company, so their own voices and speech models are the centre of the product. Before you compare prices, figure out which kind you need.

[SLIDE 4: Managed platforms: what you give up]
- Control: less access to the pipeline internals and turn-taking
- Cost: usually a platform fee on top of model and telephony costs
- Compliance: depends on the vendor's certifications, contracts and data handling
- Lock-in: prompts, tools and call flows live in their format

And here's what you trade. Four things.

Control. You get the knobs they expose. If you need a custom guardrail in the middle of the pipeline, like our streaming output check from Section 11, you may not be able to add it.

[SCREEN: terminal in `03-code`, the 10.4 snippet: `print(cost_breakdown(typical_cascaded_usage(3)).format())` ends in `per minute $0.0646  (3.00 min)`. The build-side number to put next to any platform quote.]

Cost. Most platforms charge a platform fee per minute, on top of the model and telephony costs. At low volume, that's usually worth it for the time saved. At high volume, it can become the biggest line on your bill. Run the numbers with your own call volumes. Our `costs.py` from Section 10 is a good starting point for the build side.

Compliance. If you handle health or payment data, you need to know where audio and transcripts go, how long they're kept, and what contracts the vendor will sign, like a HIPAA business associate agreement in the US. Some vendors offer this. Check the current terms. With a framework, you control that answer yourself, but you also own the work.

[B-ROLL: the `src/maple/` folder icon slides from a "LiveKit Agents" box into a "Pipecat" box, unchanged; a third "Platform" box shows the same logic re-typed into a web form.]

Lock-in. On a platform, your prompts, tools and flows live in their format. Moving means rebuilding. With a framework, they live in your repo, and our `src/maple` logic moved from LiveKit to Pipecat without a single change.

[SLIDE 5: Questions to ask any vendor]
- Can I bring my own STT, LLM and TTS providers?
- Can I call my own APIs as tools, with timeouts I control?
- Where are audio and transcripts stored, and for how long?
- Can I export prompts, tools, transcripts and metrics?
- Can I test it automatically, before changes go live?

If you're evaluating a platform, here are five questions to ask. Can I bring my own models? Can I call my own APIs as tools, with my own timeouts? Where is audio stored, and for how long? Can I export everything, including transcripts and metrics? And can I test changes automatically before they go live?

The last one matters most for this course. If a platform can't run your tests, you're back to "click around and hope."

[SLIDE 6: Build vs buy decision matrix]
| Criterion | Framework, self-hosted | Framework, managed hosting | Managed platform |
|---|---|---|---|
| Time to first call | Slowest | Medium | Fastest |
| Pipeline control | Full | Full | Limited to exposed options |
| Cost at low volume | Engineering time dominates | Engineering time dominates | Usually lowest total |
| Cost at high volume | Usually lowest per minute | Low to medium | Platform fee adds up |
| Compliance control | You own it all | Shared with the host | Depends on the vendor |
| Lock-in | Lowest | Low | Highest |
| Testing depth | Anything you build | Anything you build | Limited to what the platform exposes |

Here's the whole thing as a matrix. It's in the resources folder as `architecture-decision-matrix.md`, so you can fill it in for your own project.

Read it row by row. Time to first call favors platforms. Control favors frameworks. Cost flips with volume. Low volume, platforms usually win, because engineering time is expensive. High volume, frameworks usually win, because there's no platform fee. Compliance and lock-in both favor owning the code.

[SLIDE 7: Three quick scenarios]
- Solo dental clinic, 20 calls a day: start with a managed platform, measure, revisit
- Dental group with 40 clinics and a compliance team: framework + managed hosting
- Voice AI startup selling to many clinics: framework, with deep testing as your moat

Let's try three scenarios.

A single dental clinic, twenty calls a day. Start with a managed platform. Validate that callers actually like it. Measure containment and cost. Revisit in six months.

A dental group with forty clinics and a compliance team. A framework with managed hosting. They need control over data, custom integrations with their practice management system, and predictable costs at volume.

A startup selling voice receptionists to many clinics. A framework, no question. Their product *is* the pipeline. And their testing suite is their moat. Everything you built in Section 9 becomes a competitive advantage.

[AVATAR]
And here's the most important point in this lecture. Whatever you choose, the skills from this course transfer. Voice prompting transfers. Read-backs and confirmation gates transfer. Latency budgets, WER, LLM judges, simulated callers, cost per minute. All of it. Even on a managed platform, you can run simulated callers against its phone number and judge the transcripts.

The framework is a choice. The discipline is what makes it production.

[SLIDE 8: Recap]
- Frameworks: control, low lock-in, your compliance
- Platforms: fastest start, platform fee, less control
- Decide with a matrix and your real volumes

**Recap:** Frameworks trade speed for control, low lock-in and compliance ownership; managed platforms trade control for speed; pick with a matrix and your real call volumes, and keep testing either way.

[SLIDE 9: You can now]
- Explain Pipecat's frames, processors and transports
- Port a LiveKit agent's tools and pipeline to Pipecat
- Choose build or buy with a decision matrix

**Transition:** Lock in these trade-offs with the Section 14 quiz.

### Speaker notes: common student mistakes / Q&A

- "Which platform is cheapest?" Don't answer with numbers in Q&A; prices change monthly. Point to the matrix and ask for their call volume and average call length.
- Mistake: comparing platform per-minute prices against only the LLM cost of a framework. Include STT, TTS, telephony, hosting and engineering time on the framework side.
- "Can I start on a platform and move later?" Yes, and it's a good strategy. Keep your prompts, FAQ and test transcripts in your own repo from day one, so the move is a rebuild, not a rediscovery.
- Compliance statements in this lecture are general engineering guidance, not legal advice. Students in regulated industries should involve their compliance team.

---

## Lecture 14.4 — Quiz: Choosing a stack

| Field | Value |
|---|---|
| ID | 14.4 |
| Type | QZ (quiz with short video intro) |
| Target duration | 5:00 total (1:00 video intro, ~120 spoken words; the rest is quiz time) |
| Learning objectives | 1. Check understanding of Pipecat's pipeline model and its LiveKit equivalents. 2. Apply the build-vs-buy matrix to short scenarios. |
| Prerequisites | 14.1 to 14.3 |
| Files used | `06-assessments/quizzes/section-14.md` |

### Script

[AVATAR]
Twenty calls a day, or twenty thousand? That one number can flip your whole stack decision. Six questions to lock in this section.

[SLIDE 1: Section 14 quiz: what's covered]
- Frames, processors, transports and aggregators
- LiveKit to Pipecat translation
- Control, cost, compliance and lock-in trade-offs
- Build-vs-buy scenarios

Two questions are about Pipecat's model: what a frame is, and where the aggregators go in the pipeline. Two are translations from LiveKit to Pipecat. And two are short scenarios where you pick a stack.

A tip for the scenarios. Look for the one detail that decides it. Call volume. A compliance requirement. Or how much the team needs to customize the pipeline.

[SCREEN: `pipecat/s14_pipecat_bot.py`, the `Pipeline([...])` list, with `assistant_aggregator` last, after `transport.output()`.]

And for the aggregator question, here's the real pipeline. Note which box comes last.

[PAUSE]

Read the explanations. They're short, and they point back to the right lecture.

**Recap:** The quiz checks Pipecat's pipeline model and your build-vs-buy reasoning.

**Transition:** Next, Section 15: what you built, and where to go from here.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: the position of the assistant aggregator (after `transport.output()`). Point to Lecture 14.1, slide 6 ("Context and aggregators").
- Second most missed: assuming managed platforms are always cheaper. Point to the cost-at-volume rows of the matrix.
- "Can I retake it?" Yes, as many times as you like.
