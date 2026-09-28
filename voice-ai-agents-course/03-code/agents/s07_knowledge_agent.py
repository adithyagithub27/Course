"""Riley answers clinic questions from the FAQ (RAG for voice), in English, Spanish or Hindi.

Lectures: 7.1 (RAG for voice: tool vs pre-turn injection), 7.2 (FAQ lookup tool),
7.3 (scaling knowledge), 7.8 (multilingual Riley).

Two retrieval styles:

* ``KNOWLEDGE_MODE=tool`` (default): the LLM calls ``lookup_clinic_info`` when it needs
  facts. Flexible; costs one extra LLM round trip.
* ``KNOWLEDGE_MODE=prefetch``: ``on_user_turn_completed`` retrieves before the LLM runs
  and injects the best FAQ section into the turn. Faster; retrieves on every turn.

Languages (``LANGUAGE`` env, see ``src/maple/config.py``)::

    LANGUAGE=es python agents/s07_knowledge_agent.py console   # Spanish STT, TTS and prompt
    LANGUAGE=hi python agents/s07_knowledge_agent.py console   # Hindi

The STT gets the language code (``deepgram/nova-3`` with ``language="es"``), the TTS
speaks it (Cartesia Sonic-3 is multilingual), ``inference.TurnDetector()`` supports
en/es/hi, and the prompt tells Riley to translate English FAQ answers.

Optional extension from lecture 7.8, for callers who switch language mid-call::

    FOLLOW_CALLER_LANGUAGE=1 python agents/s07_knowledge_agent.py console

The STT runs in Deepgram's code-switching ``multi`` mode, every final transcript
carries a language code, and ``follow_caller_language`` updates the TTS language when
it changes. The prompt already tells Riley to switch with the caller.
"""

from __future__ import annotations

import logging
import os

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    ChatContext,
    ChatMessage,
    JobContext,
    UserInputTranscribedEvent,
    cli,
    inference,
)

from common import (
    CallState,
    KnowledgeToolsMixin,
    clinic_today,
    create_session,
    get_faq,
    get_settings,
    prewarm,
)
from maple import prompts

logger = logging.getLogger("s07.knowledge")


class KnowledgeRiley(KnowledgeToolsMixin, Agent):
    """Riley with the ``lookup_clinic_info`` tool.

    Args:
        language: ``en``, ``es`` or ``hi``.
        prefetch: Inject FAQ context before each LLM turn instead of relying on the tool.
    """

    def __init__(self, *, language: str = "en", prefetch: bool = False) -> None:
        self.language = language
        self.prefetch = prefetch
        super().__init__(
            instructions=prompts.build_instructions(today=clinic_today(), knowledge=True, language=language),
        )

    async def on_enter(self) -> None:
        """Greet in the caller's language."""
        self.session.say(prompts.GREETINGS.get(self.language, prompts.GREETING))

    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        """Pre-turn injection (lecture 7.1): add the best FAQ hit to this turn's context."""
        if not self.prefetch:
            return
        question = new_message.text_content or ""
        hits = get_faq().search(question, k=1)
        if hits:
            turn_ctx.add_message(
                role="assistant",
                content=f"Clinic information that may help answer the caller: {hits[0].answer}",
            )


def follow_caller_language(session: AgentSession[CallState], *, initial: str = "en") -> None:
    """Switch the TTS language when the caller changes language mid-call (lecture 7.8).

    Needs an STT that reports a language on final transcripts (Deepgram ``multi`` does).
    The LLM switches on its own: the language block says "if the caller switches, switch
    with them".
    """
    current = {"language": initial}

    @session.on("user_input_transcribed")
    def _follow_caller_language(ev: UserInputTranscribedEvent) -> None:
        if not ev.is_final or ev.language is None:
            return
        spoken = str(ev.language).split("-", 1)[0]  # "es-419" -> "es"
        if spoken in ("en", "es", "hi") and spoken != current["language"]:
            logger.info("caller switched language: %s -> %s", current["language"], spoken)
            current["language"] = spoken
            if session.tts is not None:
                session.tts.update_options(language=spoken)


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start the knowledge agent in the configured language."""
    settings = get_settings()
    prefetch = os.getenv("KNOWLEDGE_MODE", "tool").lower() == "prefetch"
    follow = os.getenv("FOLLOW_CALLER_LANGUAGE", "0") == "1"
    logger.info("language=%s prefetch=%s follow_caller_language=%s", settings.language, prefetch, follow)
    if not follow:
        session = create_session(settings, proc=ctx.proc, userdata=CallState())
        await session.start(
            agent=KnowledgeRiley(language=settings.language, prefetch=prefetch), room=ctx.room
        )
        return

    # Lecture 7.8 extension: code-switching STT, TTS follows the caller, prompt starts in English.
    session = create_session(
        settings,
        proc=ctx.proc,
        userdata=CallState(),
        stt=inference.STT(model=settings.stt_model, language="multi"),
        tts=inference.TTS(model=settings.tts_model.split(":", 1)[0], voice=settings.tts_voice, language="en"),
    )
    follow_caller_language(session, initial="en")
    await session.start(agent=KnowledgeRiley(language="en", prefetch=prefetch), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
