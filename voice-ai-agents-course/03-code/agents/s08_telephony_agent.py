"""Phone-ready Riley: inbound SIP calls, caller ID, transfer to a human, end call.

Lectures: 8.2 (inbound calls: Twilio trunk + LiveKit dispatch rule), 8.3 (phone-specific
tuning and caller ID), 8.4 (transfer to a human and ending calls), 8.7 (project 2).

Telephony setup (see README "Telephony"):

1. Set ``LIVEKIT_AGENT_NAME`` (or ``[agent] name`` in ``livekit.toml`` for ``start``);
   your dispatch rule must name the same agent.
2. Set ``TRANSFER_PHONE_NUMBER`` (E.164, e.g. ``+15125550100``) for ``transfer_to_human``.
3. ``python agents/s08_telephony_agent.py dev`` and call your Twilio number.

Tools: booking tools + ``lookup_clinic_info`` + ``transfer_to_human`` + ``end_call``
(all in ``agents/common.py``). In console mode there is no SIP participant, so
``transfer_to_human`` raises a ToolError and Riley offers to take a message instead.
"""

from __future__ import annotations

import logging

from livekit import rtc
from livekit.agents import Agent, AgentServer, JobContext, cli

from common import (
    BookingToolsMixin,
    CallState,
    KnowledgeToolsMixin,
    TelephonyToolsMixin,
    caller_number,
    create_session,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.scheduler import ClinicScheduler

logger = logging.getLogger("s08.telephony")

PHONE_RULES = """\
Phone calls:
- Callers are on a phone line; audio may be noisy. If you are unsure what you heard, ask again.
- Before transferring, say one short sentence such as "I'm transferring you to the front desk now",
  then call transfer_to_human.
- When the caller is finished, say goodbye in one sentence, then call end_call."""


class PhoneRiley(BookingToolsMixin, KnowledgeToolsMixin, TelephonyToolsMixin, Agent):
    """Riley for phone calls.

    Args:
        caller_id: Caller's number from SIP attributes, used to skip asking for it.
        scheduler: Calendar (defaults to the demo scheduler).
    """

    def __init__(self, *, caller_id: str | None = None, scheduler: ClinicScheduler | None = None) -> None:
        self.scheduler = scheduler or get_scheduler()
        caller_line = ""
        if caller_id:
            caller_line = (
                f"\nCaller ID shows {prompts.speak_phone(caller_id)}. Ask whether this is the best "
                "number to reach them instead of asking for a number from scratch."
            )
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today,
                booking=True,
                knowledge=True,
                extra=PHONE_RULES + caller_line,
            ),
        )

    async def on_enter(self) -> None:
        """Answer the phone immediately with the disclosure greeting."""
        self.session.say(prompts.GREETING)


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Wait for the caller, read caller ID, then start Riley."""
    settings = get_settings()
    caller_id = None
    if not ctx.is_fake_job():  # console mode has no real room or caller
        await ctx.connect()
        participant = await ctx.wait_for_participant()
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            caller_id = caller_number(participant)
            logger.info(
                "inbound call",
                extra={"trunk_number": participant.attributes.get("sip.trunkPhoneNumber")},
            )

    state = CallState(caller_id_number=caller_id)
    session = create_session(settings, proc=ctx.proc, userdata=state, telephony=True, max_tool_steps=5)
    await session.start(agent=PhoneRiley(caller_id=caller_id), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
