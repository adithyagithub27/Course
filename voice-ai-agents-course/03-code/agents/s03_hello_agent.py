"""Hello Riley: your first cascaded voice agent (STT -> LLM -> TTS).

Lectures: 2.2 (download-files), 2.4 (smoke test), 2.7 (MOCK_MODE), 3.3 (code-along),
3.4 (dev mode and the Agents Playground), 3.5 (providers), 3.6-3.7 (turn-taking),
3.9 (break it: five failure demos).

Run it::

    python agents/s03_hello_agent.py download-files   # once: VAD + turn-detector weights
    python agents/s03_hello_agent.py console          # talk through your laptop mic
    python agents/s03_hello_agent.py console --text   # type instead of talking
    python agents/s03_hello_agent.py dev              # connect from the Agents Playground
    MOCK_MODE=1 python agents/s03_hello_agent.py console --text   # zero-cost, no API keys

Lecture 3.9 failure demos. Set ``BROKEN`` to hear each failure, then unset it
to hear the fix::

    BROKEN=short_endpointing  caller gets cut off mid-sentence
    BROKEN=long_endpointing   awkward silence after every answer
    BROKEN=no_interruptions   Riley talks over the caller
    BROKEN=markdown           TTS reads asterisks, hashes and emojis aloud
    BROKEN=wrong_stt          older general STT without keyterms: names and accents misheard

Model strings come from ``src/maple/config.py`` (``STT_MODEL``, ``LLM_MODEL``,
``TTS_MODEL``, ``TTS_VOICE``). APIs verified on livekit-agents 1.8.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    EndpointingOptions,
    InterruptionOptions,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
)
from livekit.plugins import silero

from common import ScriptedLLM, get_settings
from maple.prompts import HELLO_INSTRUCTIONS

logger = logging.getLogger("s03")

BROKEN_CASES = ("short_endpointing", "long_endpointing", "no_interruptions", "markdown", "wrong_stt")

MARKDOWN_PROMPT = (
    "Format every answer as markdown: use a **bold** heading, bullet points with * or -, "
    "and add a friendly emoji or two."
)


def broken_overrides(case: str) -> dict[str, Any]:
    """Return the settings that reproduce one lecture 3.9 failure.

    Keys: ``endpointing``, ``interruption``, ``turn_detection``, ``instructions_extra``,
    ``tts_text_transforms``, ``stt``. Only the keys a case changes are present.
    """
    if case == "short_endpointing":
        # VAD-only turn detection with a tiny silence window: any breath ends the turn.
        return {
            "turn_detection": "vad",
            "endpointing": EndpointingOptions(min_delay=0.05, max_delay=0.3),
        }
    if case == "long_endpointing":
        return {"endpointing": EndpointingOptions(min_delay=2.5, max_delay=6.0)}
    if case == "no_interruptions":
        return {"interruption": InterruptionOptions(enabled=False)}
    if case == "markdown":
        # Ask for markdown AND switch off the filter that normally strips it before TTS.
        return {"instructions_extra": MARKDOWN_PROMPT, "tts_text_transforms": None}
    if case == "wrong_stt":
        return {"stt": "deepgram/nova-2"}
    raise ValueError(f"Unknown BROKEN case {case!r}. Choose one of: {', '.join(BROKEN_CASES)}")


class HelloRiley(Agent):
    """Riley with instructions only: no tools yet."""

    def __init__(self, extra_instructions: str = "") -> None:
        instructions = HELLO_INSTRUCTIONS
        if extra_instructions:
            instructions += "\n\n" + extra_instructions
        super().__init__(instructions=instructions)


server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Called once per room (per call). Builds the pipeline and starts Riley."""
    settings = get_settings()

    if settings.mock_mode:  # lecture 2.7: zero-cost practice with `console --text`
        session: AgentSession = AgentSession(llm=ScriptedLLM())
        await session.start(agent=HelloRiley(), room=ctx.room)
        await session.generate_reply(instructions="Greet the caller.")
        return

    case = os.getenv("BROKEN", "").strip().lower()
    broken = broken_overrides(case) if case else {}
    if case:
        logger.warning("BROKEN=%s: this agent is deliberately misconfigured (lecture 3.9)", case)

    session = AgentSession(
        stt=broken.get("stt", settings.stt_model),  # "deepgram/nova-3"
        llm=settings.llm_model,  # "openai/gpt-4.1-mini"
        tts=settings.tts_model_with_voice,  # "cartesia/sonic-3:<voice>"
        vad=silero.VAD.load(),
        turn_handling=TurnHandlingOptions(
            turn_detection=broken.get("turn_detection", inference.TurnDetector()),
            endpointing=broken.get(
                "endpointing",
                EndpointingOptions(
                    min_delay=settings.min_endpointing_delay,
                    max_delay=settings.max_endpointing_delay,
                ),
            ),
            interruption=broken.get("interruption", InterruptionOptions(min_duration=0.5)),
        ),
        **({"tts_text_transforms": None} if "tts_text_transforms" in broken else {}),
    )

    await session.start(
        agent=HelloRiley(extra_instructions=broken.get("instructions_extra", "")),
        room=ctx.room,
    )
    await session.generate_reply(
        instructions="Greet the caller as Riley from Maple Street Dental and ask how you can help."
    )


if __name__ == "__main__":
    cli.run_app(server)
