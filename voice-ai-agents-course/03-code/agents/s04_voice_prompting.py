"""Prompting for the ear: voice-first instructions, greeting and silence handling.

Lectures: 4.2 (anatomy of a voice prompt), 4.3 (numbers, dates, names and
pronunciation), 4.4 (greetings, silence and "are you still there?"), 4.5 (persona and
AI disclosure), 4.7 (challenge: Riley for your business).

What this file adds on top of s03:

* Instructions assembled from the reusable blocks in ``src/maple/prompts.py``, plus a
  ``SPELLING_RULES`` block that spells last names back letter by letter (lecture 4.3).
* A deterministic greeting in ``on_enter`` with ``session.say`` (no LLM round trip).
* A TTS text transform that expands abbreviations such as "Dr." before speech.
* ``user_away_timeout`` + the ``user_state_changed`` event: check in once, call
  ``session.reset_away_timer()`` so the timer restarts, then hang up politely after the
  second silence.

Run::

    python agents/s04_voice_prompting.py console
    MOCK_MODE=1 python agents/s04_voice_prompting.py console --text
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import AsyncIterable

from livekit.agents import Agent, AgentServer, JobContext, UserStateChangedEvent, cli

from common import CallState, clinic_today, create_session, get_settings, prewarm
from maple import prompts

logger = logging.getLogger("s04")

SILENCE_TIMEOUT_S = 12.0
MAX_SILENCE_PROMPTS = 2

# Extra prompt block for names (lecture 4.3): STT gets surnames wrong more than any other word.
SPELLING_RULES = """\
Names:
- After the caller gives their name, spell the last name back letter by letter and ask if it's
  right, for example "Is that O, R, T, I, Z?"
- If the caller spells something, use exactly the letters they said."""

# Pronunciation fixes applied to the text stream right before TTS (lecture 4.3).
ABBREVIATIONS = {
    r"\bDr\.": "Doctor",
    r"\bSt\.": "Street",
    r"\bSte\.": "Suite",
    r"\bappt\b": "appointment",
    r"\bDDS\b": "D D S",
}


async def expand_abbreviations(text: AsyncIterable[str]) -> AsyncIterable[str]:
    """TTS text transform: rewrite abbreviations chunk by chunk.

    LLM output streams in small chunks, so an abbreviation split across two
    chunks is missed. Good enough for a demo; production code buffers to word
    boundaries.
    """
    async for chunk in text:
        for pattern, spoken in ABBREVIATIONS.items():
            chunk = re.sub(pattern, spoken, chunk)
        yield chunk


class VoiceFirstRiley(Agent):
    """Riley with the full voice-first prompt and a scripted greeting."""

    def __init__(self) -> None:
        super().__init__(
            instructions=prompts.build_instructions(today=clinic_today(), extra=SPELLING_RULES),
        )

    async def on_enter(self) -> None:
        """Speak the fixed greeting as soon as the caller connects."""
        self.session.say(prompts.GREETING, allow_interruptions=True)


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start Riley with silence handling."""
    settings = get_settings()
    session = create_session(
        settings,
        proc=ctx.proc,
        userdata=CallState(),
        user_away_timeout=SILENCE_TIMEOUT_S,
        tts_text_transforms=["filter_markdown", "filter_emoji", expand_abbreviations],
    )
    background: set[asyncio.Task[None]] = set()

    async def handle_silence() -> None:
        state = session.userdata
        state.silence_prompts += 1
        if state.silence_prompts < MAX_SILENCE_PROMPTS:
            session.say(prompts.SILENCE_CHECK_IN)
            # The user is now "away". Put them back to "listening" so the away timer
            # restarts and a second silence fires this handler again.
            session.reset_away_timer()
            return
        handle = session.say(prompts.SILENCE_GOODBYE, allow_interruptions=False)
        await handle.wait_for_playout()
        state.call_outcome = "abandoned_silence"
        session.shutdown()

    @session.on("user_state_changed")
    def on_user_state_changed(ev: UserStateChangedEvent) -> None:
        if ev.new_state == "away":
            task = asyncio.create_task(handle_silence())
            background.add(task)
            task.add_done_callback(background.discard)
        elif ev.new_state == "speaking":
            session.userdata.silence_prompts = 0

    await session.start(agent=VoiceFirstRiley(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
