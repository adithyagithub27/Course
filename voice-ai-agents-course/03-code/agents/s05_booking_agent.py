"""Riley books, reschedules and cancels appointments with function tools.

Lectures: 5.1 (how function tools work), 5.3 (check availability and book), 5.4
(confirmation and read-back), 5.5 (filler speech while tools run), 5.6 (reschedule,
cancel and ToolError), 5.7 (typed userdata), 5.8 (project 1), 5.9 (challenge solution:
``join_waitlist``).

Tools (defined once in ``agents/common.py`` on ``BookingToolsMixin``):

* ``find_available_slots(day, part_of_day)``
* ``book_appointment(patient_name, phone, slot_start, reason)``
* ``reschedule_appointment(phone, new_slot_start)``
* ``cancel_appointment(phone)``
* ``join_waitlist(patient_name, phone, preferred_day)``  (this file, lecture 5.9)

Session state lives in the ``CallState`` dataclass (``context.userdata``).
Try ``MAPLE_SIMULATED_LATENCY=2`` to hear the filler speech.

Run::

    python agents/s05_booking_agent.py console
    MOCK_MODE=1 python agents/s05_booking_agent.py console --text
"""

from __future__ import annotations

from livekit.agents import Agent, AgentServer, JobContext, RunContext, ToolError, cli, function_tool

from common import (
    BookingToolsMixin,
    CallState,
    create_session,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.scheduler import ClinicScheduler, SchedulerError

WAITLIST_RULES = """\
Waitlist:
- If no time works for the caller, offer the waitlist for their preferred day.
- Read back the name, phone number and day before calling join_waitlist."""


class RileyBookingAgent(BookingToolsMixin, Agent):
    """Riley with booking tools.

    Args:
        scheduler: Calendar to use. Defaults to the process-wide demo scheduler;
            tests pass their own with a fixed "today".
    """

    def __init__(self, *, scheduler: ClinicScheduler | None = None) -> None:
        self.scheduler = scheduler or get_scheduler()
        self.simulated_latency = get_settings().simulated_backend_latency
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today, booking=True, extra=WAITLIST_RULES
            ),
        )

    async def on_enter(self) -> None:
        """Greet with the fixed line so every call starts the same way."""
        self.session.say(prompts.GREETING)

    # ---- Lecture 5.9 challenge solution ------------------------------------------------
    # The three common mistakes: a vague description (the LLM never calls it), no read-back
    # (wrong phone number saved), and forgetting ToolError (a crash instead of a retry).

    @function_tool
    async def join_waitlist(
        self,
        context: RunContext[CallState],
        patient_name: str,
        phone: str,
        preferred_day: str,
    ) -> str:
        """Put the caller on the waitlist for a day with no suitable openings. Only call this
        after reading back the name, phone number and day and the caller said yes.

        Args:
            patient_name: The patient's full name.
            phone: A ten digit callback phone number.
            preferred_day: The day they want, as an ISO date such as 2026-10-06 or a weekday name.
        """
        try:
            entry = self.scheduler.add_to_waitlist(patient_name, phone, preferred_day)
            position = self.scheduler.waitlist_position(entry.id)
        except SchedulerError as exc:
            raise ToolError(str(exc)) from exc
        context.userdata.caller_name = entry.patient_name
        context.userdata.caller_phone = entry.phone
        context.userdata.call_outcome = "waitlisted"
        return (
            f"Added to the waitlist for {prompts.speak_date(entry.preferred_day)}, "
            f"position {position}. Tell the caller we will text them if a slot opens."
        )


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start the booking agent with typed userdata."""
    session = create_session(
        get_settings(),
        proc=ctx.proc,
        userdata=CallState(),
        max_tool_steps=5,  # find -> book can take several tool rounds in one turn
    )
    await session.start(agent=RileyBookingAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
