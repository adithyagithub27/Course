"""Riley's booking flow rebuilt in Pipecat 1.12, for comparison with LiveKit Agents.

Lectures: 14.1 (Pipecat's frame pipeline model), 14.2 (code-along), 14.3 (choosing a stack).

Same business logic (``src/maple``), different framework:

====================  ===========================================  =================================
Concept               LiveKit Agents 1.8                           Pipecat 1.12
====================  ===========================================  =================================
Runtime               ``AgentSession``                             ``Pipeline`` + ``PipelineWorker``
Process host          ``AgentServer`` + ``cli.run_app``            ``WorkerRunner`` + ``pipecat.runner``
Conversation memory   ``ChatContext`` (managed for you)            ``LLMContext`` + aggregator pair
Tools                 ``@function_tool`` methods                   ``FunctionSchema`` + ``register_function``
Turn taking           VAD + ``inference.TurnDetector()``           ``LLMUserAggregatorParams(vad_analyzer=...)``
====================  ===========================================  =================================

Version note: ``PipelineTask`` and ``PipelineRunner`` still import in 1.12 but are
deprecated aliases since 1.3. This file uses their replacements, ``PipelineWorker``
(``pipecat.pipeline.worker``) and ``WorkerRunner`` (``pipecat.workers.runner``).

Install and run (needs ``DEEPGRAM_API_KEY``, ``OPENAI_API_KEY``, ``CARTESIA_API_KEY``)::

    uv sync --extra pipecat
    python pipecat/s14_pipecat_bot.py            # open http://localhost:7860/client
    python pipecat/s14_pipecat_bot.py -t twilio -x <your-ngrok-host>   # phone
"""

from __future__ import annotations

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


# --------------------------------------------------------------------------------------
# Tool schemas (what the LLM sees)
# --------------------------------------------------------------------------------------

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


# --------------------------------------------------------------------------------------
# Tool logic: plain functions over the shared scheduler (easy to unit test)
# --------------------------------------------------------------------------------------


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


def reschedule_result(scheduler: ClinicScheduler, args: dict[str, Any]) -> dict[str, Any]:
    """Move the caller's next appointment."""
    try:
        current = scheduler.upcoming_for_phone(args["phone"])
        if current is None:
            return {"error": "I couldn't find an upcoming appointment under that number."}
        moved = scheduler.reschedule(current.id, args["new_slot_start"])
    except SchedulerError as exc:
        return {"error": str(exc)}
    return {"rescheduled": prompts.speak_slot(moved.start)}


def cancel_result(scheduler: ClinicScheduler, args: dict[str, Any]) -> dict[str, Any]:
    """Cancel the caller's next appointment."""
    try:
        current = scheduler.upcoming_for_phone(args["phone"])
        if current is None:
            return {"error": "I couldn't find an upcoming appointment under that number."}
        late = scheduler.is_late_cancellation(current)
        scheduler.cancel(current.id)
    except SchedulerError as exc:
        return {"error": str(exc)}
    return {"cancelled": prompts.speak_slot(current.start), "late_cancellation_fee_may_apply": late}


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


# --------------------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------------------

TRANSPORT_PARAMS = {
    "webrtc": lambda: TransportParams(audio_in_enabled=True, audio_out_enabled=True),
    "twilio": lambda: FastAPIWebsocketParams(audio_in_enabled=True, audio_out_enabled=True),
}


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


async def bot(runner_args: RunnerArguments) -> None:
    """Entry point discovered by ``pipecat.runner.run.main``."""
    transport = await create_transport(runner_args, TRANSPORT_PARAMS)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
