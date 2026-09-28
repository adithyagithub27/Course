"""Production Riley: every feature from the course in one agent.

Lectures: 2.6 (quick win: run the finished Riley), 13.1 (capstone brief), 13.2
(assembling the production agent), 13.3 (hardening: fallbacks, timeouts, error speech),
13.4 (full test run), 13.5 (deploy, call, observe), 9.14 (LiveKit Simulations and
``on_simulation_end``).

Combines:

* Voice-first prompt with booking, knowledge, safety, escalation and security blocks (S4, S11)
* Booking tools with read-back, filler speech, ToolError, waitlist-free core flow (S5)
* FAQ lookup (S7) and a handoff to a billing specialist (S7)
* Caller ID, ``transfer_to_human`` and ``end_call`` (S8)
* Identity verification before changing existing appointments (S11)
* Input and output guardrails, PII-redacted logs (S11)
* Metrics JSONL, usage and cost per minute, optional OTel/Langfuse tracing (S10)
* Fallbacks: LiveKit Inference server-side STT/TTS fallbacks, an LLM ``FallbackAdapter``,
  per-stage ``conn_options`` timeouts and spoken error recovery (13.3)
* ``on_simulation_end``: your own pass/fail check for LiveKit Simulations (9.14)

Run::

    make console AGENT=agents/s13_capstone_receptionist.py
    MOCK_MODE=1 python agents/s13_capstone_receptionist.py console --text
    python agents/s13_capstone_receptionist.py start      # production (see deploy/Dockerfile)
"""

from __future__ import annotations

import logging
from typing import Any

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    APIConnectOptions,
    ChatContext,
    ErrorEvent,
    JobContext,
    RunContext,
    SimulationContext,
    cli,
    function_tool,
    inference,
    llm,
)
from livekit.agents.voice.agent_session import SessionConnectOptions
from s10_observed_agent import attach_observers, setup_observability
from s11_guarded_agent import GuardrailsMixin, install_pii_log_filter

from common import (
    DENTAL_KEYTERMS,
    BookingToolsMixin,
    CallState,
    KnowledgeToolsMixin,
    TelephonyToolsMixin,
    VerificationToolsMixin,
    build_llm,
    build_stt,
    build_tts,
    caller_number,
    clinic_today,
    create_session,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.config import Settings
from maple.scheduler import ClinicScheduler

logger = logging.getLogger("s13.capstone")

CAPSTONE_EXTRA = """\
Capstone rules:
- New bookings do not need identity verification. Rescheduling, cancelling or hearing about an
  existing appointment does: use verify_caller first.
- For insurance, payment plans or bills, hand off with transfer_to_billing.
- Before transferring to a human say one short sentence, then call transfer_to_human.
- When the caller is finished, say goodbye in one sentence, then call end_call."""

CONN_OPTIONS = SessionConnectOptions(
    stt_conn_options=APIConnectOptions(max_retry=2, retry_interval=1.0, timeout=8.0),
    llm_conn_options=APIConnectOptions(max_retry=1, retry_interval=0.5, timeout=10.0),
    tts_conn_options=APIConnectOptions(max_retry=2, retry_interval=1.0, timeout=8.0),
    max_unrecoverable_errors=3,
)


def build_resilient_models(settings: Settings) -> dict[str, Any]:
    """STT, LLM and TTS with fallbacks (lecture 13.3).

    * STT and TTS: LiveKit Inference ``fallback=`` runs the backup provider server side.
    * LLM: ``llm.FallbackAdapter`` tries the primary, then the fallback model, client side.

    ``plugins`` mode has no server-side fallback, so it returns the plain models.
    """
    if settings.provider_mode == "plugins":
        return {
            "stt": build_stt(settings, telephony=True),
            "llm": build_llm(settings),
            "tts": build_tts(settings),
        }
    stt_kwargs: dict[str, Any] = {}
    if settings.stt_model.startswith("deepgram/"):
        stt_kwargs["extra_kwargs"] = {"keyterm": DENTAL_KEYTERMS, "smart_format": True}
    return {
        "stt": inference.STT(
            model=settings.stt_model,
            language=settings.language,
            fallback=[settings.fallback_stt_model],
            **stt_kwargs,
        ),
        "llm": llm.FallbackAdapter(
            [inference.LLM(settings.llm_model), inference.LLM(settings.fallback_llm_model)],
            attempt_timeout=5.0,
        ),
        "tts": inference.TTS(
            model=settings.tts_model.split(":", 1)[0],
            voice=settings.tts_voice,
            language=settings.language,
            fallback=[settings.fallback_tts_model],
        ),
    }


class CapstoneRiley(
    GuardrailsMixin,
    BookingToolsMixin,
    VerificationToolsMixin,
    KnowledgeToolsMixin,
    TelephonyToolsMixin,
    Agent,
):
    """The production receptionist."""

    require_verification = True

    def __init__(
        self,
        *,
        caller_id: str | None = None,
        scheduler: ClinicScheduler | None = None,
        chat_ctx: ChatContext | None = None,
        greet: bool = True,
    ) -> None:
        self.scheduler = scheduler or get_scheduler()
        self.simulated_latency = get_settings().simulated_backend_latency
        self.greet = greet
        caller_line = (
            f"\nCaller ID shows {prompts.speak_phone(caller_id)}; confirm it before using it."
            if caller_id
            else ""
        )
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today,
                booking=True,
                knowledge=True,
                security=True,
                language=get_settings().language,
                extra=CAPSTONE_EXTRA + caller_line,
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Greet new callers; welcome back callers returning from billing."""
        if self.greet:
            self.session.say(prompts.GREETINGS.get(get_settings().language, prompts.GREETING))
        else:
            self.session.generate_reply(instructions="Ask if there is anything else you can help with.")

    @function_tool
    async def transfer_to_billing(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Hand the caller to the billing specialist for insurance, payment plans, prices or bills."""
        context.userdata.notes.append("handoff: riley -> billing")
        ctx = self.chat_ctx.copy(exclude_instructions=True).truncate(max_items=12)
        return BillingSpecialist(chat_ctx=ctx), "Transferring to the billing specialist."


class BillingSpecialist(GuardrailsMixin, KnowledgeToolsMixin, TelephonyToolsMixin, Agent):
    """Billing questions only; hands back to Riley when done."""

    def __init__(self, *, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(),
                knowledge=True,
                security=True,
                language=get_settings().language,
                extra=prompts.BILLING_SPECIALIST_EXTRA,
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Continue the billing question without re-asking."""
        self.session.generate_reply(instructions="Say you can help with billing and answer the question.")

    @function_tool
    async def back_to_riley(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Return to the main receptionist when billing questions are done."""
        context.userdata.notes.append("handoff: billing -> riley")
        ctx = self.chat_ctx.copy(exclude_instructions=True).truncate(max_items=12)
        return CapstoneRiley(chat_ctx=ctx, greet=False), "Returning to Riley."


async def on_simulation_end(sim: SimulationContext) -> None:
    """Record our own verdict for a LiveKit Simulation run (lecture 9.14).

    Scenario ``userdata`` may contain ``{"expected_outcome": "booked"}``; the run fails if
    the call ended with a different ``CallState.call_outcome``. The simulator's LLM verdict
    still stands; ``sim.fail()`` can only veto a pass, never rescue a failure.
    """
    expected = sim.userdata().get("expected_outcome")
    try:
        state: CallState = sim.job_context.primary_session.userdata
        outcome = state.call_outcome
    except (RuntimeError, ValueError):
        outcome = "unknown"
    verdict = sim.simulator_verdict
    logger.info(
        "simulation finished",
        extra={
            "scenario": sim.scenario.label,
            "simulator_success": verdict.success,
            "simulator_reason": verdict.reason,
            "outcome": outcome,
        },
    )
    if expected and outcome != expected:
        sim.fail(f"expected call outcome {expected!r} but got {outcome!r}")


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session(on_simulation_end=on_simulation_end)
async def entrypoint(ctx: JobContext) -> None:
    """Production entrypoint: telemetry, caller ID, resilient models, guardrails."""
    settings = get_settings()
    install_pii_log_filter()
    setup_observability(service_name="riley-capstone")

    caller_id = None
    if not ctx.is_fake_job():  # console mode has no real room or caller
        await ctx.connect()
        participant = await ctx.wait_for_participant()
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            caller_id = caller_number(participant)
    state = CallState(caller_id_number=caller_id)

    if settings.mock_mode:
        session: AgentSession[CallState] = create_session(settings, userdata=state)
    else:
        models = build_resilient_models(settings)
        session = create_session(
            settings,
            proc=ctx.proc,
            userdata=state,
            telephony=caller_id is not None,
            stt=models["stt"],
            llm_model=models["llm"],
            tts=models["tts"],
            conn_options=CONN_OPTIONS,
            max_tool_steps=5,
            preemptive_generation=True,
        )

    @session.on("error")
    def on_error(ev: ErrorEvent) -> None:
        if getattr(ev.error, "recoverable", True):
            return
        logger.error("unrecoverable %s error", type(ev.source).__name__)
        session.userdata.call_outcome = "error"
        session.say(prompts.ERROR_SPEECH, allow_interruptions=False)

    attach_observers(session, ctx)
    await session.start(agent=CapstoneRiley(caller_id=caller_id), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
