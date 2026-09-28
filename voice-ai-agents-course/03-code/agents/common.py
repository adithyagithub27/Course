"""Shared building blocks for every LiveKit agent in this folder.

Lectures: 3.3 and 3.5 (model wiring), 3.6 (turn handling), 5.3-5.7 (booking
tools, read-backs, filler speech, ToolError, userdata), 6.2 (tools reused by
the realtime agent), 7.2 (FAQ tool), 8.3-8.4 (caller ID, transfer, end call),
11.2 (identity verification).

Why a shared module? The same four booking tools are used by the cascaded
agent (S5), the realtime agent (S6), the multi-agent booking specialist (S7),
the guarded agent (S11) and the capstone (S13). Tools are defined once on
mixin classes and combined with :class:`livekit.agents.Agent`::

    class Riley(BookingToolsMixin, Agent):
        def __init__(self) -> None:
            super().__init__(instructions=...)
            self.scheduler = get_scheduler()

Mock mode (lecture 2.7): with ``MOCK_MODE=1`` every agent built through
:func:`create_session` uses :class:`ScriptedLLM`, a tiny rule-based fake LLM,
and no STT, TTS or VAD. Run any agent with ``console --text`` to practise the
flow, tools and code paths at zero API cost.

Business rules live in ``src/maple`` (pure Python). This module only adapts
them to LiveKit: it converts :class:`maple.scheduler.SchedulerError` into a
speakable :class:`ToolError` and formats results for the ear.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

# Make ``src/`` importable when running ``python agents/<file>.py`` without
# installing the project (``uv sync`` / ``pip install -e .`` also works).
_ROOT = Path(__file__).resolve().parents[1]
if (_ROOT / "src").is_dir() and str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402
from livekit import rtc  # noqa: E402
from livekit.agents import (  # noqa: E402
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    AgentSession,
    APIConnectOptions,
    ChatContext,
    EndpointingOptions,
    InterruptionOptions,
    JobProcess,
    NotGivenOr,
    RunContext,
    ToolError,
    TurnHandlingOptions,
    function_tool,
    get_job_context,
    inference,
    llm,
    utils,
)

from maple import prompts  # noqa: E402
from maple.config import Settings, load_settings, split_model  # noqa: E402
from maple.knowledge import FaqIndex  # noqa: E402
from maple.scheduler import (  # noqa: E402
    Appointment,
    ClinicScheduler,
    SchedulerError,
    normalize_phone,
    parse_day,
)

load_dotenv(_ROOT / ".env")

logger = logging.getLogger("riley")

# Words Deepgram should listen for: names, drug names and dental terms that
# generic models mishear (lecture 9.7 measures the difference).
DENTAL_KEYTERMS = [
    "Maple Street Dental",
    "Riley",
    "Doctor Chen",
    "Doctor Alvarez",
    "Doctor Brooks",
    "hygienist",
    "crown",
    "root canal",
    "Invisalign",
    "amoxicillin",
    "ibuprofen",
    "Delta Dental",
    "MetLife",
    "Cigna",
    "CareCredit",
]


# --------------------------------------------------------------------------------------
# Session state (lecture 5.7)
# --------------------------------------------------------------------------------------


@dataclass
class CallState:
    """Typed userdata carried across tools and agents for one call.

    Access it inside tools as ``context.userdata`` (``RunContext[CallState]``)
    and elsewhere as ``session.userdata``.
    """

    caller_name: str | None = None
    caller_phone: str | None = None
    caller_id_number: str | None = None
    visit_reason: str | None = None
    last_offered_slots: list[str] = field(default_factory=list)
    appointment_id: str | None = None
    identity_verified: bool = False
    verified_phone: str | None = None
    failed_verifications: int = 0
    transfer_requested: bool = False
    silence_prompts: int = 0
    call_outcome: str = "in_progress"
    notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Settings, scheduler and FAQ singletons (one per job process)
# --------------------------------------------------------------------------------------

_SCHEDULER: ClinicScheduler | None = None
_FAQ: FaqIndex | None = None


def get_settings() -> Settings:
    """Load settings from the environment (``.env`` is loaded on import)."""
    return load_settings()


def clinic_today(settings: Settings | None = None) -> date:
    """Today's date for the clinic, honouring ``MAPLE_TODAY`` for demos."""
    settings = settings or get_settings()
    return settings.today_override or date.today()


def get_scheduler(settings: Settings | None = None) -> ClinicScheduler:
    """Return the process-wide demo scheduler, creating it with demo patients.

    The calendar is in memory, so each agent process has its own copy. In
    production, replace this with a client for your practice management system.
    """
    global _SCHEDULER
    if _SCHEDULER is None:
        _SCHEDULER = ClinicScheduler.with_demo_data(clinic_today(settings))
    return _SCHEDULER


def get_faq() -> FaqIndex:
    """Return the process-wide FAQ index over ``src/maple/data/faq.md``."""
    global _FAQ
    if _FAQ is None:
        _FAQ = FaqIndex.from_default()
    return _FAQ


# --------------------------------------------------------------------------------------
# Model wiring (lectures 3.3, 3.5, 3.6)
# --------------------------------------------------------------------------------------


def build_stt(settings: Settings, *, telephony: bool = False) -> Any:
    """Return the STT for ``AgentSession(stt=...)``.

    * ``inference`` mode: ``inference.STT`` with dental keyterms for Deepgram models.
    * ``plugins`` mode: the Deepgram plugin using ``DEEPGRAM_API_KEY``.

    The language comes from ``LANGUAGE`` (``en``, ``es`` or ``hi``). ``telephony`` is
    accepted for symmetry; Nova-3 handles 8 kHz phone audio without a separate model.
    """
    provider, model = split_model(settings.stt_model)
    if settings.provider_mode == "plugins":
        if provider != "deepgram":
            raise ValueError("plugins mode supports deepgram STT only; set STT_MODEL=deepgram/...")
        from livekit.plugins import deepgram

        return deepgram.STT(
            model=model, language=settings.language, keyterm=DENTAL_KEYTERMS, smart_format=True
        )
    if provider == "deepgram":
        return inference.STT(
            model=settings.stt_model,
            language=settings.language,
            extra_kwargs={"keyterm": DENTAL_KEYTERMS, "smart_format": True},
        )
    return settings.stt_model_with_language


def build_llm(settings: Settings) -> Any:
    """Return the LLM for ``AgentSession(llm=...)`` (string or OpenAI plugin)."""
    if settings.provider_mode == "plugins":
        from livekit.plugins import openai

        return openai.LLM(model=split_model(settings.llm_model)[1])
    return settings.llm_model


def build_tts(settings: Settings) -> Any:
    """Return the TTS for ``AgentSession(tts=...)`` in the configured language."""
    if settings.provider_mode == "plugins":
        from livekit.plugins import cartesia

        return cartesia.TTS(
            model=split_model(settings.tts_model)[1],
            voice=settings.tts_voice,
            language=settings.language,
        )
    if settings.language == "en":
        return settings.tts_model_with_voice
    return inference.TTS(
        model=settings.tts_model.split(":", 1)[0],
        voice=settings.tts_voice,
        language=settings.language,
    )


def build_turn_handling(settings: Settings, *, telephony: bool = False) -> TurnHandlingOptions:
    """Turn-taking defaults for Riley.

    Phone callers pause more and lines add delay, so telephony gets a slightly
    longer minimum endpointing delay (lecture 8.3).
    """
    min_delay = max(settings.min_endpointing_delay, 0.7) if telephony else settings.min_endpointing_delay
    return TurnHandlingOptions(
        turn_detection=inference.TurnDetector(),
        endpointing=EndpointingOptions(min_delay=min_delay, max_delay=settings.max_endpointing_delay),
        interruption=InterruptionOptions(
            min_duration=0.5,
            resume_false_interruption=True,
            false_interruption_timeout=1.5,
        ),
    )


def prewarm(proc: JobProcess) -> None:
    """Load the Silero VAD once per process (``AgentServer(setup_fnc=prewarm)``)."""
    from livekit.plugins import silero

    proc.userdata["vad"] = silero.VAD.load()


def load_vad(proc: JobProcess | None) -> Any:
    """Return the prewarmed VAD, loading one if the process was not prewarmed."""
    if proc is not None and "vad" in proc.userdata:
        return proc.userdata["vad"]
    from livekit.plugins import silero

    return silero.VAD.load()


# --------------------------------------------------------------------------------------
# Mock mode: a scripted fake LLM (lecture 2.7)
# --------------------------------------------------------------------------------------

_BOOKING_WORDS = re.compile(r"\b(book|appointment|available|availability|opening|slot|schedule|cleaning)\b")
_HUMAN_WORDS = re.compile(r"\b(human|person|someone|receptionist|representative|operator)\b")
_BYE_WORDS = re.compile(r"\b(bye|goodbye|that's all|that is all|nothing else)\b")
_DAY_WORDS = re.compile(
    r"\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{4}-\d{2}-\d{2})\b"
)


@dataclass(frozen=True)
class ScriptedReply:
    """What :class:`ScriptedLLM` will emit: either spoken text or one tool call."""

    text: str = ""
    tool_name: str | None = None
    tool_args: dict[str, Any] = field(default_factory=dict)


def _tool_names(tools: list[Any] | None) -> set[str]:
    names: set[str] = set()
    for tool in tools or []:
        info = getattr(tool, "info", None)
        if info is not None and getattr(info, "name", None):
            names.add(info.name)
    return names


def _clean_tool_output(output: str) -> str:
    """Turn a tool result into something the fake LLM can say."""
    text = re.sub(r"\s*\[slot_start=[^\]]+\]", "", output)
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("Answer only")]
    text = lines[0] if lines else text
    text = re.sub(r"^[A-Z][\w ]{2,40}: ", "", text)  # drop "Opening hours: " style titles
    text = re.split(r"\s(?:Offer|Use the|Confirm|Say you're|Apologize|Ask)\b", text)[0]
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:2]).strip()


def scripted_reply(chat_ctx: ChatContext, tool_names: set[str]) -> ScriptedReply:
    """Pick the fake LLM's next move from the conversation so far.

    Rules, in order: summarize the latest tool result; greet if the caller has
    not spoken; say goodbye; transfer on request; check availability for
    booking requests; look up the FAQ for everything else (if the tools exist).
    """
    items = list(chat_ctx.items)
    last = items[-1] if items else None
    if last is not None and last.type == "function_call_output":
        cleaned = _clean_tool_output(str(last.output))
        prefix = "Sorry, " if getattr(last, "is_error", False) else ""
        return ScriptedReply(text=f"{prefix}{cleaned}" or "Done.")

    user_texts = [m.text_content or "" for m in items if m.type == "message" and m.role == "user"]
    if not user_texts or (last is not None and last.type == "message" and last.role != "user"):
        return ScriptedReply(text=prompts.GREETING)

    said = user_texts[-1].lower()
    if _BYE_WORDS.search(said):
        return ScriptedReply(text=prompts.GOODBYE)
    if _HUMAN_WORDS.search(said) and "transfer_to_human" in tool_names:
        return ScriptedReply(tool_name="transfer_to_human", tool_args={"reason": "caller asked for a person"})
    if _BOOKING_WORDS.search(said) and "find_available_slots" in tool_names:
        day_match = _DAY_WORDS.search(said)
        part = "morning" if "morning" in said else "afternoon" if "afternoon" in said else "any"
        return ScriptedReply(
            tool_name="find_available_slots",
            tool_args={"day": day_match.group(1) if day_match else "tomorrow", "part_of_day": part},
        )
    if "lookup_clinic_info" in tool_names:
        return ScriptedReply(tool_name="lookup_clinic_info", tool_args={"question": user_texts[-1]})
    return ScriptedReply(
        text=(
            f"Mock mode here. I heard: {user_texts[-1]}. "
            "Try asking about our hours, or say book an appointment for tomorrow morning."
        )
    )


class _ScriptedStream(llm.LLMStream):
    def __init__(
        self,
        owner: ScriptedLLM,
        *,
        chat_ctx: ChatContext,
        tools: list[Any],
        conn_options: APIConnectOptions,
    ) -> None:
        super().__init__(owner, chat_ctx=chat_ctx, tools=tools, conn_options=conn_options)
        self._reply = scripted_reply(chat_ctx, _tool_names(tools))

    async def _run(self) -> None:
        request_id = utils.shortuuid("mock_")
        reply = self._reply
        if reply.tool_name:
            call = llm.FunctionToolCall(
                name=reply.tool_name,
                arguments=json.dumps(reply.tool_args),
                call_id=utils.shortuuid("call_"),
            )
            self._event_ch.send_nowait(
                llm.ChatChunk(id=request_id, delta=llm.ChoiceDelta(role="assistant", tool_calls=[call]))
            )
        else:
            for word in reply.text.split(" "):
                await asyncio.sleep(0.01)  # stream like a real model
                self._event_ch.send_nowait(
                    llm.ChatChunk(id=request_id, delta=llm.ChoiceDelta(role="assistant", content=word + " "))
                )
        self._event_ch.send_nowait(
            llm.ChatChunk(
                id=request_id,
                usage=llm.CompletionUsage(
                    completion_tokens=len(reply.text.split()) + 5, prompt_tokens=0, total_tokens=0
                ),
            )
        )


class ScriptedLLM(llm.LLM):
    """Zero-cost stand-in for a real LLM. Deterministic, offline, rule based.

    It can call ``find_available_slots``, ``lookup_clinic_info`` and
    ``transfer_to_human`` when the current agent has them, so the real tool
    code runs end to end. It will not complete a booking: that needs a model.
    """

    @property
    def model(self) -> str:
        return "scripted-mock"

    @property
    def provider(self) -> str:
        return "maple"

    def chat(
        self,
        *,
        chat_ctx: ChatContext,
        tools: list[Any] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[Any] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> llm.LLMStream:
        return _ScriptedStream(self, chat_ctx=chat_ctx, tools=tools or [], conn_options=conn_options)


def create_session(
    settings: Settings,
    *,
    proc: JobProcess | None = None,
    userdata: CallState | None = None,
    telephony: bool = False,
    stt: Any = None,
    llm_model: Any = None,
    tts: Any = None,
    **kwargs: Any,
) -> AgentSession[CallState]:
    """Build Riley's ``AgentSession`` from settings (or a mock session in MOCK_MODE).

    Args:
        settings: Loaded :class:`Settings`.
        proc: Job process holding the prewarmed VAD (``ctx.proc``).
        userdata: Call state; a fresh :class:`CallState` by default.
        telephony: Use phone-tuned endpointing.
        stt, llm_model, tts: Override the models built from settings.
        **kwargs: Passed to ``AgentSession`` (e.g. ``max_tool_steps``, ``conn_options``).
    """
    state = userdata if userdata is not None else CallState()
    if settings.mock_mode:
        logger.warning("MOCK_MODE=1: scripted fake LLM, no STT/TTS. Run with `console --text`.")
        return AgentSession(llm=ScriptedLLM(), userdata=state, **kwargs)
    return AgentSession(
        stt=stt if stt is not None else build_stt(settings, telephony=telephony),
        llm=llm_model if llm_model is not None else build_llm(settings),
        tts=tts if tts is not None else build_tts(settings),
        vad=load_vad(proc),
        turn_handling=build_turn_handling(settings, telephony=telephony),
        userdata=state,
        **kwargs,
    )


# --------------------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------------------


def describe_appointment(appt: Appointment) -> str:
    """Speakable one-line description of an appointment."""
    return f"{appt.patient_name}, {prompts.speak_slot(appt.start)}, for a {appt.reason}"


def _speakable_error(exc: SchedulerError) -> ToolError:
    return ToolError(str(exc))


# --------------------------------------------------------------------------------------
# Booking tools (lectures 5.3-5.7, reused in 6.2, 7.5, 11.2, 13.2)
# --------------------------------------------------------------------------------------


class BookingToolsMixin:
    """Adds ``find_available_slots``, ``book_appointment``,
    ``reschedule_appointment`` and ``cancel_appointment`` to an Agent.

    Subclasses must set ``self.scheduler`` (a :class:`ClinicScheduler`).
    Set ``require_verification = True`` to demand :meth:`verify_caller` before
    changing an existing appointment (lecture 11.2).
    """

    scheduler: ClinicScheduler
    require_verification: bool = False
    simulated_latency: float = 0.0

    async def _backend_call(self) -> None:
        """Mimic a slow practice-management API so filler speech is audible."""
        if self.simulated_latency > 0:
            await asyncio.sleep(self.simulated_latency)

    def _check_verified(self, context: RunContext[CallState], phone: str) -> None:
        if not self.require_verification:
            return
        state = context.userdata
        if not state.identity_verified or state.verified_phone != normalize_phone(phone):
            raise ToolError(
                "Before I can change an existing appointment I need to verify your identity. "
                "Ask for the phone number on file and the patient's date of birth."
            )

    @function_tool
    async def find_available_slots(
        self,
        context: RunContext[CallState],
        day: str,
        part_of_day: Literal["morning", "afternoon", "any"] = "any",
    ) -> str:
        """Look up free appointment times. Always call this before offering times.

        Args:
            day: The day the caller wants: an ISO date such as 2026-10-06, or words such as
                "tomorrow" or "Thursday".
            part_of_day: "morning", "afternoon" or "any".
        """
        async with context.with_filler("One moment while I check the schedule.", delay=0.8):
            await self._backend_call()
            try:
                target = parse_day(day, self.scheduler.today)
                slots = self.scheduler.find_slots(target, part_of_day, limit=3)
                note = ""
                if not slots:
                    slots = self.scheduler.next_available(target, part_of_day, limit=3)
                    note = f"Nothing is free on {prompts.speak_date(target)}. "
            except SchedulerError as exc:
                raise _speakable_error(exc) from exc

        if not slots:
            context.userdata.last_offered_slots = []
            return note + "There are no openings in the next two weeks. Offer the waitlist or a transfer."

        context.userdata.last_offered_slots = [s.iso for s in slots]
        options = "; ".join(f"{prompts.speak_slot(s.start)} [slot_start={s.iso}]" for s in slots)
        return (
            f"{note}Open times: {options}. Offer these to the caller in words. "
            "Use the slot_start value when booking; never read it aloud."
        )

    @function_tool
    async def book_appointment(
        self,
        context: RunContext[CallState],
        patient_name: str,
        phone: str,
        slot_start: str,
        reason: str,
    ) -> str:
        """Book a new appointment. Only call this AFTER reading the details back and the caller
        clearly said yes.

        Args:
            patient_name: The patient's full name.
            phone: A ten digit callback phone number.
            slot_start: The exact slot_start returned by find_available_slots, e.g. 2026-10-06T09:30.
            reason: Short reason for the visit, e.g. "cleaning" or "tooth pain".
        """
        context.disallow_interruptions()  # a half-finished booking is worse than a short wait
        async with context.with_filler("Booking that for you now.", delay=0.8):
            await self._backend_call()
            try:
                appt = self.scheduler.book(patient_name, phone, slot_start, reason)
            except SchedulerError as exc:
                raise _speakable_error(exc) from exc

        state = context.userdata
        state.caller_name = appt.patient_name
        state.caller_phone = appt.phone
        state.visit_reason = appt.reason
        state.appointment_id = appt.id
        state.call_outcome = "booked"
        return (
            f"Booked: {describe_appointment(appt)}. Confirm the day and time once and mention "
            "the 24 hour cancellation policy."
        )

    @function_tool
    async def reschedule_appointment(
        self,
        context: RunContext[CallState],
        phone: str,
        new_slot_start: str,
    ) -> str:
        """Move the caller's next upcoming appointment to a new time. Call find_available_slots
        first, read the new time back, and only call this after the caller says yes.

        Args:
            phone: The phone number the appointment was booked under.
            new_slot_start: The slot_start of the new time, e.g. 2026-10-07T14:00.
        """
        self._check_verified(context, phone)
        context.disallow_interruptions()
        async with context.with_filler("Let me move that for you.", delay=0.8):
            await self._backend_call()
            try:
                current = self.scheduler.upcoming_for_phone(phone)
                if current is None:
                    raise ToolError(
                        "I couldn't find an upcoming appointment under that number. "
                        "Ask the caller to confirm the phone number."
                    )
                moved = self.scheduler.reschedule(current.id, new_slot_start)
            except SchedulerError as exc:
                raise _speakable_error(exc) from exc

        context.userdata.appointment_id = moved.id
        context.userdata.call_outcome = "rescheduled"
        return f"Rescheduled: {describe_appointment(moved)}. Confirm the new day and time once."

    @function_tool
    async def cancel_appointment(self, context: RunContext[CallState], phone: str) -> str:
        """Cancel the caller's next upcoming appointment. Read the appointment back and only call
        this after the caller confirms they want to cancel.

        Args:
            phone: The phone number the appointment was booked under.
        """
        self._check_verified(context, phone)
        context.disallow_interruptions()
        async with context.with_filler("Okay, cancelling that now.", delay=0.8):
            await self._backend_call()
            try:
                current = self.scheduler.upcoming_for_phone(phone)
                if current is None:
                    raise ToolError(
                        "I couldn't find an upcoming appointment under that number. "
                        "Ask the caller to confirm the phone number."
                    )
                late = self.scheduler.is_late_cancellation(current)
                cancelled = self.scheduler.cancel(current.id)
            except SchedulerError as exc:
                raise _speakable_error(exc) from exc

        context.userdata.call_outcome = "cancelled"
        fee_note = (
            " This is less than 24 hours ahead, so mention the late cancellation fee may apply."
            if late
            else ""
        )
        return f"Cancelled: {describe_appointment(cancelled)}.{fee_note} Offer to book a new time."


# --------------------------------------------------------------------------------------
# Identity verification (lecture 11.2)
# --------------------------------------------------------------------------------------


class VerificationToolsMixin:
    """Adds ``verify_caller`` and ``get_my_appointments``.

    Existing appointments are only revealed after the caller proves they know
    the phone number on file and the patient's date of birth.
    """

    scheduler: ClinicScheduler
    max_verification_attempts: int = 3

    @function_tool
    async def verify_caller(self, context: RunContext[CallState], phone: str, date_of_birth: str) -> str:
        """Verify the caller before sharing or changing an existing appointment.

        Args:
            phone: The phone number on file.
            date_of_birth: The patient's date of birth, e.g. 1988-04-12.
        """
        state = context.userdata
        if state.failed_verifications >= self.max_verification_attempts:
            raise ToolError("Too many failed attempts. Offer to transfer the caller to the front desk.")
        if self.scheduler.verify_patient(phone, date_of_birth):
            state.identity_verified = True
            state.verified_phone = normalize_phone(phone)
            return "Verified. You may now discuss this caller's appointments."
        state.failed_verifications += 1
        raise ToolError(
            "Those details don't match our records. Ask the caller to check the phone number and "
            "date of birth. Do not reveal which detail was wrong."
        )

    @function_tool
    async def get_my_appointments(self, context: RunContext[CallState]) -> str:
        """List the verified caller's upcoming appointments. Requires verify_caller first."""
        state = context.userdata
        if not state.identity_verified or not state.verified_phone:
            raise ToolError("The caller is not verified yet. Call verify_caller first.")
        appts = [
            a
            for a in self.scheduler.find_by_phone(state.verified_phone)
            if a.start.date() >= self.scheduler.today
        ]
        if not appts:
            return "This caller has no upcoming appointments."
        return "Upcoming: " + "; ".join(describe_appointment(a) for a in appts)


# --------------------------------------------------------------------------------------
# FAQ tool (lecture 7.2)
# --------------------------------------------------------------------------------------


class KnowledgeToolsMixin:
    """Adds ``lookup_clinic_info`` backed by :class:`maple.knowledge.FaqIndex`."""

    @function_tool
    async def lookup_clinic_info(self, context: RunContext[CallState], question: str) -> str:
        """Look up clinic facts: hours, address, parking, insurance, prices, payment plans,
        policies, services, accessibility, languages and emergencies.

        Args:
            question: The caller's question in plain words.
        """
        answer = get_faq().answer(question, k=2)
        if answer == "NO_MATCH":
            return (
                "No matching clinic information. Say you're not sure and offer to take a message "
                "or transfer the caller to the front desk."
            )
        return f"Answer only from this, in one or two sentences:\n{answer}"


# --------------------------------------------------------------------------------------
# Telephony tools (lectures 8.3-8.4)
# --------------------------------------------------------------------------------------


def find_sip_participant(room: rtc.Room) -> rtc.RemoteParticipant | None:
    """Return the first SIP (phone) participant in the room, if any."""
    for participant in room.remote_participants.values():
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            return participant
    return None


def caller_number(participant: rtc.RemoteParticipant | None) -> str | None:
    """Caller ID from SIP participant attributes (``sip.phoneNumber``)."""
    if participant is None:
        return None
    return participant.attributes.get("sip.phoneNumber") or None


class TelephonyToolsMixin:
    """Adds ``transfer_to_human`` and ``end_call``."""

    @function_tool
    async def transfer_to_human(self, context: RunContext[CallState], reason: str) -> str:
        """Transfer the caller to a person at the front desk. Before calling this, tell the
        caller you are transferring them.

        Args:
            reason: One short sentence for the staff member explaining why.
        """
        settings = get_settings()
        state = context.userdata
        state.transfer_requested = True
        state.notes.append(f"transfer: {reason}")
        job_ctx = get_job_context(required=False)
        caller = find_sip_participant(job_ctx.room) if job_ctx is not None else None
        if job_ctx is None or caller is None or not settings.transfer_sip_uri:
            state.call_outcome = "transfer_unavailable"
            raise ToolError(
                "Transfers aren't available on this line. Apologize and offer to take a message "
                "so the front desk can call back."
            )
        await context.wait_for_playout()  # let "I'm transferring you now" finish first
        try:
            await job_ctx.transfer_sip_participant(caller, settings.transfer_sip_uri)
        except Exception as exc:  # SIP errors surface as API errors
            logger.exception("transfer failed")
            state.call_outcome = "transfer_failed"
            raise ToolError("The transfer didn't go through. Apologize and offer to take a message.") from exc
        state.call_outcome = "transferred"
        return "The caller has been transferred."

    @function_tool
    async def end_call(self, context: RunContext[CallState]) -> None:
        """Hang up. Only call this after you have said goodbye and the caller has nothing else."""
        state = context.userdata
        if state.call_outcome == "in_progress":
            state.call_outcome = "completed"
        await context.wait_for_playout()  # let the goodbye finish
        job_ctx = get_job_context(required=False)
        if job_ctx is None or job_ctx.is_fake_job():
            context.session.shutdown()
            return None
        # Deleting the room disconnects everyone, including the SIP caller.
        await job_ctx.delete_room()
        return None
