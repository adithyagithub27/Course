"""Zero-cost agent tests with the scripted mock LLM (lectures 2.7 and 9.5).

These run offline in CI: no API keys, no network. They exercise the real tool
code, userdata and ``mock_tools`` so you can practise the assertion API for free.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from livekit.agents import AgentSession, llm, mock_tools
from s05_booking_agent import RileyBookingAgent
from s07_knowledge_agent import KnowledgeRiley

from common import CallState, ScriptedLLM, can_say

pytestmark = pytest.mark.offline


async def test_mock_llm_checks_availability(scheduler) -> None:
    async with AgentSession(llm=ScriptedLLM(), userdata=CallState()) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        result = await session.run(user_input="Can I book a cleaning tomorrow morning?")

        result.expect.next_event().is_function_call(
            name="find_available_slots", arguments={"day": "tomorrow", "part_of_day": "morning"}
        )
        output = result.expect.next_event().is_function_call_output(is_error=False)
        assert "slot_start=2026-10-06T08:00" in output.event().item.output
        message = result.expect.next_event().is_message(role="assistant")
        assert "October sixth" in (message.event().item.text_content or "")
        result.expect.no_more_events()
        assert session.userdata.last_offered_slots[0] == "2026-10-06T08:00"


async def test_closed_day_becomes_a_tool_error(scheduler) -> None:
    async with AgentSession(llm=ScriptedLLM(), userdata=CallState()) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        result = await session.run(user_input="Any appointment on sunday?")
        result.expect.next_event().is_function_call(name="find_available_slots", arguments={"day": "sunday"})
        result.expect.next_event().is_function_call_output(is_error=True)
        result.expect.next_event().is_message(role="assistant")


async def test_mock_tools_forces_no_availability(scheduler) -> None:
    def no_slots(context, day: str, part_of_day: str = "any") -> str:
        return "There are no openings in the next two weeks."

    with mock_tools(RileyBookingAgent, {"find_available_slots": no_slots}):
        async with AgentSession(llm=ScriptedLLM(), userdata=CallState()) as session:
            await session.start(RileyBookingAgent(scheduler=scheduler))
            result = await session.run(user_input="book me an appointment tomorrow")
            result.expect.next_event().is_function_call(name="find_available_slots")
            result.expect.next_event().is_function_call_output(
                output="There are no openings in the next two weeks."
            )
            message = result.expect.next_event().is_message(role="assistant")
            assert "no openings" in (message.event().item.text_content or "")


async def test_mock_llm_answers_from_faq() -> None:
    async with AgentSession(llm=ScriptedLLM(), userdata=CallState()) as session:
        await session.start(KnowledgeRiley())
        result = await session.run(user_input="Where can I park?")
        result.expect.next_event().is_function_call(name="lookup_clinic_info")
        result.expect.next_event().is_function_call_output()
        message = result.expect.next_event().is_message(role="assistant")
        assert "garage" in (message.event().item.text_content or "").lower()


async def test_greeting_is_spoken_on_enter(scheduler) -> None:
    async with AgentSession(llm=ScriptedLLM(), userdata=CallState()) as session:
        result = await session.start(RileyBookingAgent(scheduler=scheduler), capture_run=True)
        assert result is not None
        result.expect.skip_next_event_if(type="agent_handoff")
        message = result.expect.next_event().is_message(role="assistant")
        assert "AI assistant" in (message.event().item.text_content or "")


def test_string_fillers_are_skipped_only_in_pure_realtime_mode() -> None:
    """Lecture 6.2: ``say`` (and so a string filler) needs a TTS unless the realtime model supports it."""
    cascaded = MagicMock(spec=AgentSession, tts=object(), llm=object())
    assert can_say(cascaded)

    realtime = MagicMock(spec=llm.RealtimeModel)
    realtime.capabilities = MagicMock(audio_output=True, supports_say=False)
    pure = MagicMock(spec=AgentSession, tts=None, llm=realtime)
    assert not can_say(pure)

    hybrid = MagicMock(spec=AgentSession, tts=object(), llm=realtime)
    assert can_say(hybrid)

    realtime.capabilities = MagicMock(audio_output=False, supports_say=False)
    text_only = MagicMock(spec=AgentSession, tts=None, llm=realtime)
    assert can_say(text_only)
