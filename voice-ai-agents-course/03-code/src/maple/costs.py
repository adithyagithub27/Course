"""Cost-per-minute calculator for voice calls.

Lectures: 2.1 (what it costs), 6.4 (cascaded vs realtime), 10.4 (cost per minute).

.. warning::
   Every price in :data:`DEFAULT_PRICES` is a **PLACEHOLDER** taken from public
   list prices around mid-2026 and rounded. Providers change prices often and
   LiveKit Inference, direct plugins and enterprise contracts all differ.
   Copy the table, update it from your own invoices, and pass it in.

Usage::

    from maple.costs import UsageNumbers, cost_breakdown

    usage = UsageNumbers(call_seconds=180, stt_audio_seconds=95,
                         llm_input_tokens=24_000, llm_output_tokens=900,
                         tts_characters=2_100)
    report = cost_breakdown(usage)
    report.per_minute      # dollars per call minute
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

PRICES_LAST_CHECKED = "2026-09 (PLACEHOLDER - update from your provider invoices)"


@dataclass(frozen=True)
class PriceTable:
    """Unit prices in US dollars. All values are placeholders; see module docstring.

    Attributes:
        stt_per_minute: Streaming STT per audio minute (e.g. Deepgram Nova-3).
        llm_input_per_million: LLM input tokens per million (e.g. gpt-4.1-mini).
        llm_cached_input_per_million: Cached LLM input tokens per million.
        llm_output_per_million: LLM output tokens per million.
        tts_per_million_chars: TTS characters per million (e.g. Cartesia Sonic).
        realtime_audio_input_per_million: Realtime model audio input tokens per million.
        realtime_audio_output_per_million: Realtime model audio output tokens per million.
        realtime_text_input_per_million: Realtime model text input tokens per million.
        realtime_text_output_per_million: Realtime model text output tokens per million.
        realtime_cached_input_per_million: Realtime cached input tokens per million.
        platform_per_minute: Agent hosting / session minutes (e.g. LiveKit Cloud).
        telephony_per_minute: PSTN + SIP trunk per minute (0 for web calls).
    """

    stt_per_minute: float = 0.0077
    llm_input_per_million: float = 0.40
    llm_cached_input_per_million: float = 0.10
    llm_output_per_million: float = 1.60
    tts_per_million_chars: float = 50.0
    realtime_audio_input_per_million: float = 32.0
    realtime_audio_output_per_million: float = 64.0
    realtime_text_input_per_million: float = 4.0
    realtime_text_output_per_million: float = 16.0
    realtime_cached_input_per_million: float = 0.40
    platform_per_minute: float = 0.01
    telephony_per_minute: float = 0.0


DEFAULT_PRICES = PriceTable()
PHONE_PRICES = PriceTable(telephony_per_minute=0.0125)


@dataclass(frozen=True)
class UsageNumbers:
    """Usage for one call (or many calls summed together).

    Attributes:
        call_seconds: Wall-clock call duration. The denominator for cost per minute.
        stt_audio_seconds: Audio sent to STT.
        llm_input_tokens: LLM prompt tokens (including cached ones).
        llm_cached_input_tokens: Portion of ``llm_input_tokens`` served from cache.
        llm_output_tokens: LLM completion tokens.
        tts_characters: Characters sent to TTS.
        realtime_audio_input_tokens: Realtime model audio input tokens.
        realtime_audio_output_tokens: Realtime model audio output tokens.
        realtime_text_input_tokens: Realtime model text input tokens.
        realtime_text_output_tokens: Realtime model text output tokens.
        realtime_cached_input_tokens: Realtime cached input tokens (any modality).
    """

    call_seconds: float
    stt_audio_seconds: float = 0.0
    llm_input_tokens: int = 0
    llm_cached_input_tokens: int = 0
    llm_output_tokens: int = 0
    tts_characters: int = 0
    realtime_audio_input_tokens: int = 0
    realtime_audio_output_tokens: int = 0
    realtime_text_input_tokens: int = 0
    realtime_text_output_tokens: int = 0
    realtime_cached_input_tokens: int = 0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if value < 0:
                raise ValueError(f"{name} must be >= 0, got {value}")
        if self.llm_cached_input_tokens > self.llm_input_tokens:
            raise ValueError("llm_cached_input_tokens cannot exceed llm_input_tokens")

    def __add__(self, other: UsageNumbers) -> UsageNumbers:
        return UsageNumbers(**{k: getattr(self, k) + getattr(other, k) for k in self.__dict__})


@dataclass(frozen=True)
class CostBreakdown:
    """Dollar cost per component plus totals."""

    components: Mapping[str, float] = field(default_factory=dict)
    call_minutes: float = 0.0

    @property
    def total(self) -> float:
        """Total cost in dollars."""
        return sum(self.components.values())

    @property
    def per_minute(self) -> float:
        """Total cost divided by call minutes (0 for an empty call)."""
        return self.total / self.call_minutes if self.call_minutes > 0 else 0.0

    def largest_component(self) -> str:
        """Name of the most expensive component (where the money goes)."""
        return max(self.components, key=lambda k: self.components[k]) if self.components else ""

    def format(self) -> str:
        """Human-readable multi-line report."""
        lines = [f"{name:<14} ${value:,.4f}" for name, value in self.components.items()]
        lines.append(f"{'total':<14} ${self.total:,.4f}")
        lines.append(f"{'per minute':<14} ${self.per_minute:,.4f}  ({self.call_minutes:.2f} min)")
        return "\n".join(lines)


def cost_breakdown(usage: UsageNumbers, prices: PriceTable = DEFAULT_PRICES) -> CostBreakdown:
    """Compute dollar cost for ``usage`` with ``prices``.

    Components with zero usage are still listed (as 0.0) so reports line up.
    """
    minutes = usage.call_seconds / 60.0
    uncached = usage.llm_input_tokens - usage.llm_cached_input_tokens
    per_m = 1_000_000
    realtime_uncached_audio = max(usage.realtime_audio_input_tokens - usage.realtime_cached_input_tokens, 0)
    components = {
        "stt": usage.stt_audio_seconds / 60.0 * prices.stt_per_minute,
        "llm": (
            uncached * prices.llm_input_per_million
            + usage.llm_cached_input_tokens * prices.llm_cached_input_per_million
            + usage.llm_output_tokens * prices.llm_output_per_million
        )
        / per_m,
        "tts": usage.tts_characters * prices.tts_per_million_chars / per_m,
        "realtime": (
            realtime_uncached_audio * prices.realtime_audio_input_per_million
            + usage.realtime_cached_input_tokens * prices.realtime_cached_input_per_million
            + usage.realtime_audio_output_tokens * prices.realtime_audio_output_per_million
            + usage.realtime_text_input_tokens * prices.realtime_text_input_per_million
            + usage.realtime_text_output_tokens * prices.realtime_text_output_per_million
        )
        / per_m,
        "platform": minutes * prices.platform_per_minute,
        "telephony": minutes * prices.telephony_per_minute,
    }
    return CostBreakdown(components={k: round(v, 6) for k, v in components.items()}, call_minutes=minutes)


def cost_per_minute(usage: UsageNumbers, prices: PriceTable = DEFAULT_PRICES) -> float:
    """Shortcut for ``cost_breakdown(usage, prices).per_minute``."""
    return cost_breakdown(usage, prices).per_minute


def usage_from_model_usage(
    model_usage: Iterable[Mapping[str, Any]],
    call_seconds: float,
    *,
    realtime: bool = False,
) -> UsageNumbers:
    """Convert LiveKit ``session.usage.model_usage`` entries into :class:`UsageNumbers`.

    Pass each entry as a dict (``entry.model_dump()``). Entries are identified
    by their ``type`` field: ``llm_usage``, ``stt_usage`` or ``tts_usage``.
    Other types (turn detection, interruption) are ignored.

    Args:
        model_usage: Iterable of usage dicts.
        call_seconds: Call duration used for per-minute math.
        realtime: Treat ``llm_usage`` entries as a speech-to-speech model, so
            audio and text tokens are priced with realtime rates.
    """
    totals: dict[str, float] = {
        "stt_audio_seconds": 0.0,
        "llm_input_tokens": 0,
        "llm_cached_input_tokens": 0,
        "llm_output_tokens": 0,
        "tts_characters": 0,
        "realtime_audio_input_tokens": 0,
        "realtime_audio_output_tokens": 0,
        "realtime_text_input_tokens": 0,
        "realtime_text_output_tokens": 0,
        "realtime_cached_input_tokens": 0,
    }
    for entry in model_usage:
        kind = entry.get("type")
        if kind == "stt_usage":
            totals["stt_audio_seconds"] += float(entry.get("audio_duration", 0.0))
        elif kind == "tts_usage":
            totals["tts_characters"] += int(entry.get("characters_count", 0))
        elif kind == "llm_usage" and realtime:
            totals["realtime_audio_input_tokens"] += int(entry.get("input_audio_tokens", 0))
            totals["realtime_audio_output_tokens"] += int(entry.get("output_audio_tokens", 0))
            totals["realtime_text_input_tokens"] += int(entry.get("input_text_tokens", 0))
            totals["realtime_text_output_tokens"] += int(entry.get("output_text_tokens", 0))
            totals["realtime_cached_input_tokens"] += int(entry.get("input_cached_tokens", 0))
        elif kind == "llm_usage":
            totals["llm_input_tokens"] += int(entry.get("input_tokens", 0))
            totals["llm_cached_input_tokens"] += int(entry.get("input_cached_tokens", 0))
            totals["llm_output_tokens"] += int(entry.get("output_tokens", 0))
    return UsageNumbers(call_seconds=call_seconds, **totals)  # type: ignore[arg-type]


def typical_cascaded_usage(minutes: float) -> UsageNumbers:
    """Rough usage for a cascaded receptionist call of ``minutes`` minutes.

    Assumes the caller speaks ~50% of the time, ~6 turns per minute, a ~2,500
    token prompt that grows with history, ~40 output tokens per turn and ~150
    spoken characters per turn. Good enough for back-of-envelope comparisons.
    """
    turns = max(1, round(6 * minutes))
    avg_prompt = 2_500 + 60 * turns  # history grows through the call
    return UsageNumbers(
        call_seconds=minutes * 60,
        stt_audio_seconds=minutes * 60 * 0.5,
        llm_input_tokens=turns * avg_prompt,
        llm_cached_input_tokens=int(turns * avg_prompt * 0.5),
        llm_output_tokens=turns * 40,
        tts_characters=turns * 150,
    )


def typical_realtime_usage(minutes: float) -> UsageNumbers:
    """Rough usage for a speech-to-speech (realtime) call of ``minutes`` minutes.

    Assumes ~600 audio tokens per minute of caller audio and ~1,000 per minute
    of generated audio, with the whole conversation re-sent as input each turn.
    """
    turns = max(1, round(6 * minutes))
    caller_audio_tokens_per_turn = 50
    agent_audio_tokens_per_turn = 85
    history_audio = sum(
        (caller_audio_tokens_per_turn + agent_audio_tokens_per_turn) * t for t in range(turns)
    )
    audio_in = turns * caller_audio_tokens_per_turn + history_audio
    return UsageNumbers(
        call_seconds=minutes * 60,
        realtime_audio_input_tokens=audio_in,
        realtime_cached_input_tokens=int(history_audio * 0.8),
        realtime_audio_output_tokens=turns * agent_audio_tokens_per_turn,
        realtime_text_input_tokens=turns * 2_500,
        realtime_text_output_tokens=turns * 40,
    )
