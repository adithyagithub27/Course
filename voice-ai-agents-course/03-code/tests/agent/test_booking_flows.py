"""Behavior tests for booking tools: calls, arguments, read-backs and mocks.

Lectures: 9.4 (asserting tool calls and arguments), 9.5 (mocking tools), 7.5 (handoffs).

Two kinds of checks:

* **Event assertions**: ``result.expect.next_event().is_function_call(name=..., arguments=...)``,
  ``is_function_call_output(...)``, ``skip_next_event_if(...)``, ``contains_function_call(...)``,
  ``no_more_events()``.
* **State assertions**: the scheduler fixture is real, so after "yes, book it" we can
  check the appointment actually exists.

``mock_tools(RileyBookingAgent, {...})`` swaps tool *execution* for deterministic
fakes to force the "no availability" and "backend down" paths. LiveKit calls a mock with
the real tool's arguments positionally, ``context`` first, so a mock either mirrors the
real signature (``(context, day, part_of_day="any")``) or takes no parameters at all.
"""

from __future__ import annotations

import json
from datetime import datetime

import pytest
from livekit.agents import AgentSession, ToolError, mock_tools
from livekit.agents.voice.run_result import FunctionCallEvent
from s05_booking_agent import RileyBookingAgent
from s07_multi_agent import BookingAgent, GreeterAgent

from common import CallState

pytestmark = pytest.mark.live


def called(result, name: str) -> list[dict]:
    """Arguments of every call to ``name`` in a run result."""
    return [
        json.loads(ev.item.arguments)
        for ev in result.events
        if isinstance(ev, FunctionCallEvent) and ev.item.name == name
    ]


async def test_checks_availability_before_offering_times(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState()) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        result = await session.run(user_input="Can I get a cleaning tomorrow morning?")

        call = result.expect.next_event().is_function_call(name="find_available_slots")
        args = json.loads(call.event().item.arguments)
        assert args["day"] in ("tomorrow", "2026-10-06", "Tuesday")
        assert args.get("part_of_day") == "morning"
        result.expect.next_event().is_function_call_output(is_error=False)
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                judge_llm,
                intent="Offers up to three specific morning times on Tuesday October sixth, spoken as words, "
                "and asks which one works.",
            )
        )


async def test_reads_back_before_booking_then_books(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState(), max_tool_steps=5) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        result = await session.run(
            user_input="This is Ana Gomez, my number is 512 555 0188. I'd like a cleaning tomorrow at 9 am."
        )
        assert called(result, "book_appointment") == [], "must confirm before booking"
        await result.expect.contains_message(role="assistant").judge(
            judge_llm,
            intent="Reads back the name Ana Gomez and Tuesday at nine in the morning and asks the caller "
            "to confirm before booking.",
        )

        result = await session.run(user_input="Yes, that's right, please book it.")
        result.expect.skip_next_event_if(type="message", role="assistant")
        result.expect.contains_function_call(
            name="book_appointment",
            arguments={"slot_start": "2026-10-06T09:00"},
        )
        booked = scheduler.find_by_phone("5125550188")
        assert len(booked) == 1 and booked[0].start == datetime(2026, 10, 6, 9, 0)
        assert session.userdata.call_outcome == "booked"


async def test_correction_updates_the_read_back(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState(), max_tool_steps=5) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        await session.run(user_input="Ana Gomez, 512 555 0188, cleaning, Tuesday at 9 am please.")
        result = await session.run(user_input="Sorry, no, I meant Thursday, same time.")
        assert called(result, "book_appointment") == []
        await result.expect.contains_message(role="assistant").judge(
            judge_llm,
            intent="Acknowledges the change to Thursday and reads back Thursday at nine for confirmation.",
        )


async def test_cancel_requires_confirmation(llm, judge_llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState(), max_tool_steps=5) as session:
        await session.start(RileyBookingAgent(scheduler=scheduler))
        result = await session.run(user_input="I need to cancel my appointment. My number is 512 555 0142.")
        assert called(result, "cancel_appointment") == []

        result = await session.run(user_input="Yes, cancel it.")
        result.expect.contains_function_call(name="cancel_appointment")
        assert scheduler.upcoming_for_phone("5125550142") is None


async def test_no_availability_mocked(llm, judge_llm, scheduler) -> None:
    def no_slots(context, day: str, part_of_day: str = "any") -> str:
        return "There are no openings in the next two weeks. Offer the waitlist or a transfer."

    with mock_tools(RileyBookingAgent, {"find_available_slots": no_slots}):
        async with AgentSession(llm=llm, userdata=CallState()) as session:
            await session.start(RileyBookingAgent(scheduler=scheduler))
            result = await session.run(user_input="Any openings on Friday?")
            result.expect.next_event().is_function_call(name="find_available_slots")
            result.expect.next_event().is_function_call_output()
            await (
                result.expect.next_event()
                .is_message(role="assistant")
                .judge(
                    judge_llm,
                    intent="Says there are no openings, does not invent any times, and offers the waitlist or a transfer.",
                )
            )


async def test_backend_outage_mocked(llm, judge_llm, scheduler) -> None:
    def outage(context, day: str, part_of_day: str = "any") -> str:
        raise ToolError("The scheduling system is not responding. Apologize and offer to take a message.")

    with mock_tools(RileyBookingAgent, {"find_available_slots": outage}):
        async with AgentSession(llm=llm, userdata=CallState()) as session:
            await session.start(RileyBookingAgent(scheduler=scheduler))
            result = await session.run(user_input="Can I book something for Wednesday afternoon?")
            result.expect.next_event().is_function_call(name="find_available_slots")
            result.expect.next_event().is_function_call_output(is_error=True)
            await (
                result.expect.next_event()
                .is_message(role="assistant")
                .judge(
                    judge_llm,
                    intent="Apologizes that it cannot check the schedule right now and offers to take a message "
                    "or transfer, without making up times.",
                )
            )


async def test_after_lunch_means_afternoon(llm, scheduler) -> None:
    seen: list[tuple[str, str]] = []

    def spy(context, day: str, part_of_day: str = "any") -> str:
        seen.append((day, part_of_day))
        return (
            "Open times: Thursday, October eighth at two in the afternoon "
            "[slot_start=2026-10-08T14:00]. Offer these to the caller in words."
        )

    with mock_tools(RileyBookingAgent, {"find_available_slots": spy}):
        async with AgentSession(llm=llm, userdata=CallState()) as session:
            await session.start(RileyBookingAgent(scheduler=scheduler))
            await session.run(user_input="Anything Thursday after lunch?")

    assert seen, "Riley never checked availability"
    assert seen[0][1] == "afternoon"


async def test_greeter_hands_off_to_booking(llm, scheduler) -> None:
    async with AgentSession(llm=llm, userdata=CallState()) as session:
        await session.start(GreeterAgent())
        result = await session.run(user_input="I'd like to book a cleaning please.")
        result.expect.contains_function_call(name="transfer_to_booking")
        result.expect.contains_agent_handoff(new_agent_type=BookingAgent)
        assert "handoff: greeter -> booking" in session.userdata.notes
