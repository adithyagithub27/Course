"""Riley on OpenAI Realtime (speech-to-speech), reusing the same booking tools.

Lectures: 6.1 (how realtime models work), 6.2 (code-along), 6.3 (hybrid: realtime LLM
with your own TTS), 6.4 (head-to-head vs cascaded), 6.5 (lab).

Modes::

    python agents/s06_realtime_agent.py console                    # full speech-to-speech
    REALTIME_HYBRID=1 python agents/s06_realtime_agent.py console  # text out + Cartesia TTS

Needs ``OPENAI_API_KEY`` (the realtime model is used through the OpenAI plugin).
``REALTIME_MODEL`` and ``REALTIME_VOICE`` come from ``src/maple/config.py``.
In ``MOCK_MODE=1`` the realtime model is replaced by the scripted fake LLM.
"""

from __future__ import annotations

import logging
import os

from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import openai
from openai.types import realtime

from common import (
    BookingToolsMixin,
    CallState,
    build_tts,
    create_session,
    get_scheduler,
    get_settings,
)
from maple import prompts
from maple.config import Settings
from maple.scheduler import ClinicScheduler

logger = logging.getLogger("s06")


class RealtimeRiley(BookingToolsMixin, Agent):
    """Same tools and prompt as the cascaded booking agent; different model."""

    def __init__(self, *, scheduler: ClinicScheduler | None = None) -> None:
        self.scheduler = scheduler or get_scheduler()
        super().__init__(
            instructions=prompts.build_instructions(today=self.scheduler.today, booking=True),
        )

    async def on_enter(self) -> None:
        """Realtime models generate the greeting themselves (there is no separate TTS)."""
        self.session.generate_reply(
            instructions=f"Greet the caller with exactly this sentence: {prompts.GREETING}"
        )


def build_realtime_model(settings: Settings, *, hybrid: bool) -> openai.realtime.RealtimeModel:
    """Create the OpenAI Realtime model.

    ``hybrid=True`` asks the model for text only so a separate TTS voices it,
    which keeps Riley's brand voice identical across architectures (lecture 6.3).
    """
    return openai.realtime.RealtimeModel(
        model=settings.realtime_model,  # "gpt-realtime"
        voice=settings.realtime_voice,  # "marin"
        modalities=["text"] if hybrid else ["audio"],
        turn_detection=realtime.realtime_audio_input_turn_detection.SemanticVad(
            type="semantic_vad",
            eagerness="auto",
            create_response=True,
            interrupt_response=True,
        ),
    )


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start the realtime (or hybrid) agent."""
    settings = get_settings()
    hybrid = os.getenv("REALTIME_HYBRID", "0") == "1"

    if settings.mock_mode:
        session = create_session(settings, userdata=CallState())
    else:
        extra = {"tts": build_tts(settings)} if hybrid else {}
        session = AgentSession(
            llm=build_realtime_model(settings, hybrid=hybrid),
            userdata=CallState(),
            max_tool_steps=5,
            **extra,
        )
    logger.info("starting realtime Riley (hybrid=%s)", hybrid)
    await session.start(agent=RealtimeRiley(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
