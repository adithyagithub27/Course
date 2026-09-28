"""Behavior tests: greeting, FAQ answers and "I don't know" (lecture 9.3).

Pattern::

    async with AgentSession(llm=llm, userdata=CallState()) as session:
        await session.start(Riley())
        result = await session.run(user_input="...")
        await result.expect.next_event().is_message(role="assistant").judge(llm, intent="...")
"""

from __future__ import annotations

import pytest
from livekit.agents import AgentSession
from s05_booking_agent import RileyBookingAgent
from s07_knowledge_agent import KnowledgeRiley

from common import CallState

pytestmark = pytest.mark.live


async def test_greeting_discloses_ai_and_offers_help(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState()) as session:
        result = await session.start(RileyBookingAgent(scheduler=scheduler), capture_run=True)
        assert result is not None
        result.expect.skip_next_event_if(type="agent_handoff")
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                judge_llm,
                intent="Greets the caller on behalf of Maple Street Dental, says it is an AI assistant, "
                "and asks how it can help.",
            )
        )


async def test_answers_opening_hours_from_the_faq(llm, judge_llm) -> None:
    async with AgentSession(llm=llm, userdata=CallState()) as session:
        await session.start(KnowledgeRiley())
        result = await session.run(user_input="What time are you open on Saturday?")

        result.expect.next_event().is_function_call(name="lookup_clinic_info")
        result.expect.next_event().is_function_call_output(is_error=False)
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                judge_llm,
                intent="Says the clinic is open from nine to one on Saturdays, in one or two short spoken "
                "sentences with no lists or markdown.",
            )
        )
        result.expect.no_more_events()


async def test_unknown_question_does_not_invent_an_answer(llm, judge_llm) -> None:
    async with AgentSession(llm=llm, userdata=CallState()) as session:
        await session.start(KnowledgeRiley())
        result = await session.run(user_input="Do you do laser gum surgery with Doctor Smith?")

        await result.expect.contains_message(role="assistant").judge(
            judge_llm,
            intent="Does not claim the clinic offers laser gum surgery or that a Doctor Smith works "
            "there; says it is not sure or that this is not listed, and offers to take a message, "
            "transfer, or book a consultation.",
        )


async def test_replies_are_voice_friendly(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState()) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        result = await session.run(user_input="Hi! What can you help me with?")
        message = result.expect.contains_message(role="assistant")
        text = message.event().item.text_content or ""
        assert "*" not in text and "#" not in text, "markdown would be read aloud"
        assert len(text.split()) < 60, "voice replies should be short"
        await message.judge(
            judge_llm,
            intent="Briefly explains it can help with appointments or clinic questions and asks one question.",
        )
