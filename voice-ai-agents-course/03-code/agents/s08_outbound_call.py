"""Outbound appointment-reminder calls: explicit dispatch + outbound SIP participant.

Lecture: 8.5 (outbound calls: appointment reminders); compliance notes in 8.6.

This file has two halves:

1. **The agent** (``console | dev | start``). When dispatched with metadata such as
   ``{"phone_number": "+15125550142", "patient_name": "Jordan Lee"}`` it dials the
   patient with ``CreateSIPParticipantRequest`` through your outbound trunk, waits until
   they answer, then runs the reminder conversation.
2. **The dispatcher** (``dispatch`` sub-command). It asks LiveKit to start the agent
   in a new room with ``CreateAgentDispatchRequest``::

       # terminal 1: the agent must run with an agent name for explicit dispatch
       LIVEKIT_AGENT_NAME=riley-outbound python agents/s08_outbound_call.py dev
       # terminal 2: place the call
       python agents/s08_outbound_call.py dispatch --agent-name riley-outbound \\
           --to +15125550142 --name "Jordan Lee"

Needs ``SIP_OUTBOUND_TRUNK_ID`` (from ``lk sip outbound create``) and LiveKit
credentials. Only call numbers that consented to reminder calls (TCPA; lecture 8.6).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import uuid
from typing import Any

from livekit import api
from livekit.agents import Agent, AgentServer, JobContext, cli

from common import (
    BookingToolsMixin,
    CallState,
    TelephonyToolsMixin,
    create_session,
    describe_appointment,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.scheduler import SchedulerError, normalize_phone

logger = logging.getLogger("s08.outbound")


class ReminderRiley(BookingToolsMixin, TelephonyToolsMixin, Agent):
    """Riley placing a reminder call about one appointment."""

    def __init__(self, *, patient_name: str, appointment_summary: str) -> None:
        self.scheduler = get_scheduler()
        context = f"\nYou are calling {patient_name} about this appointment: {appointment_summary}."
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today,
                booking=True,
                extra=prompts.REMINDER_CALL_EXTRA + context,
            ),
        )


def parse_metadata(raw: str) -> dict[str, Any]:
    """Parse dispatch metadata JSON; an empty string gives an empty dict."""
    if not raw:
        return {}
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("dispatch metadata must be a JSON object")
    return data


def appointment_summary(phone: str) -> str:
    """Speakable summary of the patient's next appointment (or a generic line)."""
    try:
        appt = get_scheduler().upcoming_for_phone(phone)
    except SchedulerError:
        appt = None
    return describe_appointment(appt) if appt else "their upcoming visit at Maple Street Dental"


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Dial the patient from dispatch metadata, then start the reminder conversation."""
    settings = get_settings()
    meta = parse_metadata(ctx.job.metadata)
    phone = meta.get("phone_number", "")
    patient = meta.get("patient_name", "the patient")

    agent = ReminderRiley(patient_name=patient, appointment_summary=appointment_summary(phone))
    session = create_session(settings, proc=ctx.proc, userdata=CallState(caller_phone=phone), telephony=True)

    if not phone:  # console / playground test: no call to place
        await session.start(agent=agent, room=ctx.room)
        await session.generate_reply(instructions="Start the reminder call.")
        return
    if not settings.sip_outbound_trunk_id:
        logger.error("SIP_OUTBOUND_TRUNK_ID is not set; cannot place outbound calls")
        ctx.shutdown(reason="missing outbound trunk")
        return

    # Start the session first so Riley is listening the moment the patient answers.
    await session.start(agent=agent, room=ctx.room)
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=settings.sip_outbound_trunk_id,
                sip_call_to=phone,
                participant_identity=f"patient-{normalize_phone(phone)}",
                participant_name=patient,
                wait_until_answered=True,
            )
        )
    except api.TwirpError as exc:
        logger.error(
            "outbound call failed: %s (SIP status %s)",
            exc.message,
            exc.metadata.get("sip_status_code"),
        )
        ctx.shutdown(reason="outbound call failed")
        return
    # Answered. Let the patient say "hello" first on real calls; this nudge speaks
    # first if they stay silent. Voicemail handling is described in the prompt.
    await session.generate_reply(
        instructions="The patient answered. Introduce yourself and the reason for the call."
    )


async def dispatch_call(agent_name: str, to: str, name: str) -> str:
    """Create an explicit agent dispatch in a fresh room. Returns the room name."""
    room = f"reminder-{uuid.uuid4().hex[:8]}"
    lkapi = api.LiveKitAPI()  # reads LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
    try:
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room,
                metadata=json.dumps({"phone_number": to, "patient_name": name}),
            )
        )
        logger.info("created dispatch %s in room %s", dispatch.id, room)
    finally:
        await lkapi.aclose()
    return room


def _dispatch_cli(argv: list[str]) -> None:
    settings = get_settings()
    parser = argparse.ArgumentParser(prog="s08_outbound_call.py dispatch")
    parser.add_argument("--to", required=True, help="E.164 number to call, e.g. +15125550142")
    parser.add_argument("--name", default="there", help="Patient name for the greeting")
    parser.add_argument(
        "--agent-name",
        default=settings.agent_name,
        help="Must match the LIVEKIT_AGENT_NAME the agent worker runs with",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    room = asyncio.run(dispatch_call(args.agent_name, args.to, args.name))
    print(f"Dispatched {args.agent_name} to room {room}; the agent will dial {args.to}.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "dispatch":
        _dispatch_cli(sys.argv[2:])
    else:
        cli.run_app(server)
