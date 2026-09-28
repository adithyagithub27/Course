"""Capstone acceptance tests that need CapstoneRiley (lecture 13.4)."""

from __future__ import annotations

import pytest
from livekit.agents import AgentSession
from livekit.agents.voice.run_result import FunctionCallEvent
from s13_capstone_receptionist import BillingSpecialist, CapstoneRiley

from common import CallState

pytestmark = pytest.mark.live


def tool_names(result) -> list[str]:
    return [ev.item.name for ev in result.events if isinstance(ev, FunctionCallEvent)]


async def test_at05_closed_day_offers_next_open_day(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState(), max_tool_steps=5) as session:
        await session.start(CapstoneRiley(scheduler=scheduler))
        result = await session.run(user_input="Can I come in this Sunday for a cleaning?")
        assert "book_appointment" not in tool_names(result)
        await result.expect.contains_message(role="assistant").judge(
            judge_llm,
            intent="Says the clinic is closed on Sundays and offers specific times on the next open day.",
        )


async def test_at10_insurance_question_hands_off_to_billing(llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState(), max_tool_steps=5) as session:
        await session.start(CapstoneRiley(scheduler=scheduler))
        result = await session.run(user_input="Do you take Delta Dental?")
        result.expect.contains_function_call(name="transfer_to_billing")
        result.expect.contains_agent_handoff(new_agent_type=BillingSpecialist)
