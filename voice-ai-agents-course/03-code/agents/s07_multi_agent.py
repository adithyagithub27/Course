"""Greeter -> Booking -> Billing: specialist agents with handoffs and shared userdata.

Lectures: 7.4 (why split one agent into several), 7.5 (code-along: handoffs),
7.6 (lab: add an Insurance agent).

How handoffs work in LiveKit Agents 1.8: a ``@function_tool`` returns another
``Agent`` instance (optionally as ``(agent, "message for the LLM")``). The session
switches to it, calls its ``on_enter``, and keeps the same ``userdata`` (``CallState``).
Each specialist receives a copy of the conversation so the caller never repeats
themselves.

Run::

    python agents/s07_multi_agent.py console
"""

from __future__ import annotations

from livekit.agents import Agent, AgentServer, ChatContext, JobContext, RunContext, cli, function_tool

from common import (
    BookingToolsMixin,
    CallState,
    KnowledgeToolsMixin,
    clinic_today,
    create_session,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.scheduler import ClinicScheduler

MAX_CARRIED_ITEMS = 12


def carry_over(agent: Agent) -> ChatContext:
    """Copy the recent conversation for the next agent, without the old instructions."""
    return agent.chat_ctx.copy(exclude_instructions=True).truncate(max_items=MAX_CARRIED_ITEMS)


class GreeterAgent(KnowledgeToolsMixin, Agent):
    """Front desk: answers simple questions and routes to specialists."""

    def __init__(self, *, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, extra=prompts.GREETER_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Greet on the first visit; welcome back when returning from a specialist."""
        if self.chat_ctx.items:
            self.session.generate_reply(instructions="Ask if there is anything else you can help with.")
        else:
            self.session.say(prompts.GREETING)

    @function_tool
    async def transfer_to_booking(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Hand the caller to the booking specialist for new appointments, rescheduling or
        cancellations."""
        context.userdata.notes.append("handoff: greeter -> booking")
        return BookingAgent(chat_ctx=carry_over(self)), "Transferring to the booking specialist."

    @function_tool
    async def transfer_to_billing(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Hand the caller to the billing specialist for insurance, payment plans, prices or
        bills."""
        context.userdata.notes.append("handoff: greeter -> billing")
        return BillingAgent(chat_ctx=carry_over(self)), "Transferring to the billing specialist."


class BookingAgent(BookingToolsMixin, Agent):
    """Booking specialist with the four booking tools."""

    def __init__(
        self, *, chat_ctx: ChatContext | None = None, scheduler: ClinicScheduler | None = None
    ) -> None:
        self.scheduler = scheduler or get_scheduler()
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today, booking=True, extra=prompts.BOOKING_SPECIALIST_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Pick up where the greeter left off, using what we already know."""
        name = self.session.userdata.caller_name
        hint = f" The caller's name is {name}." if name else ""
        self.session.generate_reply(
            instructions="Briefly say you can help with appointments and continue the request "
            f"without asking again for anything the caller already said.{hint}"
        )

    @function_tool
    async def back_to_front_desk(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Return to the front desk when the caller has no more appointment questions."""
        context.userdata.notes.append("handoff: booking -> greeter")
        return GreeterAgent(chat_ctx=carry_over(self)), "Returning to the front desk."


class BillingAgent(KnowledgeToolsMixin, Agent):
    """Billing specialist: insurance, payment options and price ranges from the FAQ."""

    def __init__(self, *, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, extra=prompts.BILLING_SPECIALIST_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Acknowledge the billing question and continue."""
        self.session.generate_reply(
            instructions="Briefly say you can help with insurance and payments, then answer the "
            "caller's question."
        )

    @function_tool
    async def back_to_front_desk(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Return to the front desk when the caller has no more billing questions."""
        context.userdata.notes.append("handoff: billing -> greeter")
        return GreeterAgent(chat_ctx=carry_over(self)), "Returning to the front desk."


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start with the greeter; handoffs happen inside tools."""
    session = create_session(get_settings(), proc=ctx.proc, userdata=CallState(), max_tool_steps=5)
    await session.start(agent=GreeterAgent(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
