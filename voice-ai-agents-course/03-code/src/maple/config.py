"""Environment-driven configuration for every Riley agent.

Lectures: 2.2 (project setup), 3.5 (choosing providers), 12.6 (production readiness).

All model identifiers live here so you can swap providers, or survive a model
rename, by editing ``.env`` instead of code. Defaults match the course:

* STT ``deepgram/nova-3``
* LLM ``openai/gpt-4.1-mini``
* TTS ``cartesia/sonic-3``
* Realtime ``gpt-realtime`` with the ``marin`` voice

Model strings use the LiveKit Inference ``provider/model`` format. When
``MAPLE_PROVIDER_MODE=plugins`` the agents build provider plugins instead and
use the part after the slash as the plugin's model name.

Usage::

    from maple.config import load_settings

    settings = load_settings()          # reads os.environ
    settings.llm_model                  # "openai/gpt-4.1-mini"
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Literal

ProviderMode = Literal["inference", "plugins"]
Language = Literal["en", "es", "hi"]

SUPPORTED_LANGUAGES: dict[str, str] = {"en": "English", "es": "Spanish", "hi": "Hindi"}
_TRUTHY = {"1", "true", "yes", "on"}

DEFAULT_STT_MODEL = "deepgram/nova-3"
DEFAULT_LLM_MODEL = "openai/gpt-4.1-mini"
DEFAULT_FALLBACK_LLM_MODEL = "google/gemini-2.5-flash"
DEFAULT_FALLBACK_STT_MODEL = "assemblyai/universal-streaming"
DEFAULT_FALLBACK_TTS_MODEL = "deepgram/aura-2"
DEFAULT_TTS_MODEL = "cartesia/sonic-3"
# Cartesia "Katie" style friendly female voice. Replace with any voice ID from
# the Cartesia voice library.
DEFAULT_TTS_VOICE = "f786b574-daa5-4673-aa0c-cbe3e8534c02"
DEFAULT_REALTIME_MODEL = "gpt-realtime"
DEFAULT_REALTIME_VOICE = "marin"
DEFAULT_JUDGE_MODEL = "gpt-4.1-mini"
DEFAULT_AGENT_NAME = "riley-receptionist"
DEFAULT_TIMEZONE = "America/Chicago"


class ConfigError(ValueError):
    """Raised when an environment variable holds an invalid value."""


@dataclass(frozen=True)
class Settings:
    """Immutable, fully-resolved configuration for one process.

    Attributes:
        stt_model: Speech-to-text model string (``STT_MODEL``).
        llm_model: Chat LLM model string (``LLM_MODEL``).
        fallback_llm_model: Second LLM tried when the first fails (``FALLBACK_LLM_MODEL``).
        fallback_stt_model: Server-side STT fallback in LiveKit Inference (``FALLBACK_STT_MODEL``).
        fallback_tts_model: Server-side TTS fallback in LiveKit Inference (``FALLBACK_TTS_MODEL``).
        tts_model: Text-to-speech model string (``TTS_MODEL``).
        tts_voice: Voice identifier for the TTS provider (``TTS_VOICE``).
        realtime_model: OpenAI Realtime model name (``REALTIME_MODEL``).
        realtime_voice: OpenAI Realtime voice (``REALTIME_VOICE``).
        judge_model: OpenAI model used by tests as the LLM judge (``JUDGE_MODEL``).
        provider_mode: ``"inference"`` (LiveKit Inference strings) or ``"plugins"``
            (direct provider plugins with your own API keys) (``MAPLE_PROVIDER_MODE``).
        agent_name: Name used for explicit dispatch and telephony (``LIVEKIT_AGENT_NAME``).
        transfer_phone_number: Where ``transfer_to_human`` sends callers (``TRANSFER_PHONE_NUMBER``).
        sip_outbound_trunk_id: LiveKit outbound trunk for reminder calls (``SIP_OUTBOUND_TRUNK_ID``).
        clinic_timezone: IANA time zone of the clinic (``CLINIC_TIMEZONE``).
        today_override: Fixed "today" for deterministic demos and tests (``MAPLE_TODAY``, ISO date).
        min_endpointing_delay: Seconds of silence before a turn may end (``MIN_ENDPOINTING_DELAY``).
        max_endpointing_delay: Upper bound the turn detector may wait (``MAX_ENDPOINTING_DELAY``).
        metrics_dir: Directory where observed agents write JSONL metrics (``METRICS_DIR``).
        mock_mode: Run agents with a scripted fake LLM and no STT/TTS, for zero-cost practice
            with ``console --text`` (``MOCK_MODE=1``).
        language: Conversation language: ``en``, ``es`` or ``hi`` (``LANGUAGE``). Drives the STT
            language, the TTS language and the prompt language in ``s07_knowledge_agent.py``.
        simulated_backend_latency: Seconds each booking tool sleeps to mimic a slow practice
            management system, so you can hear filler speech (``MAPLE_SIMULATED_LATENCY``).
    """

    stt_model: str = DEFAULT_STT_MODEL
    llm_model: str = DEFAULT_LLM_MODEL
    fallback_llm_model: str = DEFAULT_FALLBACK_LLM_MODEL
    fallback_stt_model: str = DEFAULT_FALLBACK_STT_MODEL
    fallback_tts_model: str = DEFAULT_FALLBACK_TTS_MODEL
    tts_model: str = DEFAULT_TTS_MODEL
    tts_voice: str = DEFAULT_TTS_VOICE
    realtime_model: str = DEFAULT_REALTIME_MODEL
    realtime_voice: str = DEFAULT_REALTIME_VOICE
    judge_model: str = DEFAULT_JUDGE_MODEL
    provider_mode: ProviderMode = "inference"
    agent_name: str = DEFAULT_AGENT_NAME
    transfer_phone_number: str = ""
    sip_outbound_trunk_id: str = ""
    clinic_timezone: str = DEFAULT_TIMEZONE
    today_override: date | None = None
    min_endpointing_delay: float = 0.5
    max_endpointing_delay: float = 3.0
    metrics_dir: str = "metrics"
    simulated_backend_latency: float = 0.0
    mock_mode: bool = False
    language: Language = "en"

    @property
    def tts_model_with_voice(self) -> str:
        """Return the LiveKit Inference TTS string including the voice suffix.

        LiveKit Inference accepts ``"provider/model:voice"``, for example
        ``"cartesia/sonic-3:f786b574-..."``.
        """
        if not self.tts_voice or ":" in self.tts_model:
            return self.tts_model
        return f"{self.tts_model}:{self.tts_voice}"

    @property
    def language_name(self) -> str:
        """English name of :attr:`language`, e.g. ``"Spanish"``."""
        return SUPPORTED_LANGUAGES[self.language]

    @property
    def stt_model_with_language(self) -> str:
        """STT model string with a ``:language`` suffix for non-English calls.

        LiveKit Inference accepts ``"deepgram/nova-3:es"``. English keeps the
        plain model string.
        """
        if self.language == "en" or ":" in self.stt_model:
            return self.stt_model
        return f"{self.stt_model}:{self.language}"

    @property
    def transfer_sip_uri(self) -> str:
        """Return the transfer target as a ``tel:`` URI ("" when unset)."""
        number = self.transfer_phone_number.strip()
        if not number:
            return ""
        if number.startswith(("tel:", "sip:")):
            return number
        return f"tel:{number}"


def split_model(model: str) -> tuple[str, str]:
    """Split ``"provider/model"`` into ``("provider", "model")``.

    A string without a slash is returned with an empty provider. A trailing
    ``:voice`` or ``:language`` suffix is dropped from the model part.

    >>> split_model("openai/gpt-4.1-mini")
    ('openai', 'gpt-4.1-mini')
    >>> split_model("cartesia/sonic-3:abc")
    ('cartesia', 'sonic-3')
    """
    provider, _, name = model.partition("/")
    if not name:
        provider, name = "", provider
    name = name.split(":", 1)[0]
    return provider, name


def _get(env: Mapping[str, str], key: str, default: str) -> str:
    value = env.get(key)
    if value is None or value.strip() == "":
        return default
    return value.strip()


def _get_float(env: Mapping[str, str], key: str, default: float) -> float:
    raw = env.get(key)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{key} must be a number, got {raw!r}") from exc
    if value < 0:
        raise ConfigError(f"{key} must be >= 0, got {value}")
    return value


def _get_date(env: Mapping[str, str], key: str) -> date | None:
    raw = env.get(key)
    if raw is None or raw.strip() == "":
        return None
    try:
        return date.fromisoformat(raw.strip())
    except ValueError as exc:
        raise ConfigError(f"{key} must be an ISO date like 2026-10-05, got {raw!r}") from exc


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build :class:`Settings` from environment variables.

    Args:
        env: Mapping to read from. Defaults to ``os.environ``. Tests pass a dict.

    Returns:
        A frozen :class:`Settings` instance.

    Raises:
        ConfigError: If a value cannot be parsed or is out of range.
    """
    source: Mapping[str, str] = os.environ if env is None else env

    mode = _get(source, "MAPLE_PROVIDER_MODE", "inference").lower()
    if mode not in ("inference", "plugins"):
        raise ConfigError(f"MAPLE_PROVIDER_MODE must be 'inference' or 'plugins', got {mode!r}")

    min_delay = _get_float(source, "MIN_ENDPOINTING_DELAY", 0.5)
    max_delay = _get_float(source, "MAX_ENDPOINTING_DELAY", 3.0)
    if max_delay < min_delay:
        raise ConfigError(
            f"MAX_ENDPOINTING_DELAY ({max_delay}) must be >= MIN_ENDPOINTING_DELAY ({min_delay})"
        )

    language = _get(source, "LANGUAGE", "en").lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ConfigError(f"LANGUAGE must be one of {sorted(SUPPORTED_LANGUAGES)}, got {language!r}")

    return Settings(
        stt_model=_get(source, "STT_MODEL", DEFAULT_STT_MODEL),
        llm_model=_get(source, "LLM_MODEL", DEFAULT_LLM_MODEL),
        fallback_llm_model=_get(source, "FALLBACK_LLM_MODEL", DEFAULT_FALLBACK_LLM_MODEL),
        fallback_stt_model=_get(source, "FALLBACK_STT_MODEL", DEFAULT_FALLBACK_STT_MODEL),
        fallback_tts_model=_get(source, "FALLBACK_TTS_MODEL", DEFAULT_FALLBACK_TTS_MODEL),
        tts_model=_get(source, "TTS_MODEL", DEFAULT_TTS_MODEL),
        tts_voice=_get(source, "TTS_VOICE", DEFAULT_TTS_VOICE),
        realtime_model=_get(source, "REALTIME_MODEL", DEFAULT_REALTIME_MODEL),
        realtime_voice=_get(source, "REALTIME_VOICE", DEFAULT_REALTIME_VOICE),
        judge_model=_get(source, "JUDGE_MODEL", DEFAULT_JUDGE_MODEL),
        provider_mode=mode,  # type: ignore[arg-type]
        agent_name=_get(source, "LIVEKIT_AGENT_NAME", DEFAULT_AGENT_NAME),
        transfer_phone_number=_get(source, "TRANSFER_PHONE_NUMBER", ""),
        sip_outbound_trunk_id=_get(source, "SIP_OUTBOUND_TRUNK_ID", ""),
        clinic_timezone=_get(source, "CLINIC_TIMEZONE", DEFAULT_TIMEZONE),
        today_override=_get_date(source, "MAPLE_TODAY"),
        min_endpointing_delay=min_delay,
        max_endpointing_delay=max_delay,
        metrics_dir=_get(source, "METRICS_DIR", "metrics"),
        simulated_backend_latency=_get_float(source, "MAPLE_SIMULATED_LATENCY", 0.0),
        mock_mode=_get(source, "MOCK_MODE", "0").lower() in _TRUTHY,
        language=language,  # type: ignore[arg-type]
    )
