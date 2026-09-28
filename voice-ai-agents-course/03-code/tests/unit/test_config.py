"""Unit tests for maple.config (lectures 2.2, 2.7, 3.5, 7.8)."""

from __future__ import annotations

from datetime import date

import pytest

from maple.config import (
    DEFAULT_LLM_MODEL,
    DEFAULT_STT_MODEL,
    DEFAULT_TTS_MODEL,
    ConfigError,
    Settings,
    load_settings,
    split_model,
)


def test_defaults_match_the_course() -> None:
    s = load_settings({})
    assert s.stt_model == DEFAULT_STT_MODEL == "deepgram/nova-3"
    assert s.llm_model == DEFAULT_LLM_MODEL == "openai/gpt-4.1-mini"
    assert s.tts_model == DEFAULT_TTS_MODEL == "cartesia/sonic-3"
    assert s.realtime_model == "gpt-realtime"
    assert s.realtime_voice == "marin"
    assert s.provider_mode == "inference"
    assert s.mock_mode is False
    assert s.language == "en"


def test_env_overrides() -> None:
    s = load_settings(
        {
            "STT_MODEL": "assemblyai/universal-streaming",
            "LLM_MODEL": "openai/gpt-4.1",
            "TTS_MODEL": "cartesia/sonic-2",
            "LIVEKIT_AGENT_NAME": "riley-test",
            "MAPLE_TODAY": "2026-10-05",
            "MIN_ENDPOINTING_DELAY": "0.8",
            "MAX_ENDPOINTING_DELAY": "4",
        }
    )
    assert s.stt_model == "assemblyai/universal-streaming"
    assert s.llm_model == "openai/gpt-4.1"
    assert s.agent_name == "riley-test"
    assert s.today_override == date(2026, 10, 5)
    assert (s.min_endpointing_delay, s.max_endpointing_delay) == (0.8, 4.0)


def test_blank_values_fall_back_to_defaults() -> None:
    assert load_settings({"LLM_MODEL": "   "}).llm_model == DEFAULT_LLM_MODEL


def test_settings_are_frozen() -> None:
    s = load_settings({})
    with pytest.raises(AttributeError):
        s.llm_model = "other"  # type: ignore[misc]


@pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
def test_mock_mode_truthy(value: str) -> None:
    assert load_settings({"MOCK_MODE": value}).mock_mode is True


@pytest.mark.parametrize("value", ["0", "false", "", "no"])
def test_mock_mode_falsy(value: str) -> None:
    assert load_settings({"MOCK_MODE": value}).mock_mode is False


@pytest.mark.parametrize(
    "env",
    [
        {"MAPLE_PROVIDER_MODE": "magic"},
        {"MIN_ENDPOINTING_DELAY": "fast"},
        {"MIN_ENDPOINTING_DELAY": "-1"},
        {"MIN_ENDPOINTING_DELAY": "2", "MAX_ENDPOINTING_DELAY": "1"},
        {"MAPLE_TODAY": "tomorrow"},
        {"LANGUAGE": "fr"},
    ],
)
def test_invalid_values_raise(env: dict[str, str]) -> None:
    with pytest.raises(ConfigError):
        load_settings(env)


def test_language_wiring() -> None:
    es = load_settings({"LANGUAGE": "ES"})
    assert es.language == "es"
    assert es.language_name == "Spanish"
    assert es.stt_model_with_language == "deepgram/nova-3:es"
    assert load_settings({}).stt_model_with_language == "deepgram/nova-3"


def test_tts_model_with_voice() -> None:
    s = Settings(tts_model="cartesia/sonic-3", tts_voice="abc")
    assert s.tts_model_with_voice == "cartesia/sonic-3:abc"
    assert (
        Settings(tts_model="cartesia/sonic-3:xyz", tts_voice="abc").tts_model_with_voice
        == "cartesia/sonic-3:xyz"
    )
    assert Settings(tts_voice="").tts_model_with_voice == "cartesia/sonic-3"


def test_transfer_sip_uri() -> None:
    assert Settings().transfer_sip_uri == ""
    assert Settings(transfer_phone_number="+15125550100").transfer_sip_uri == "tel:+15125550100"
    assert Settings(transfer_phone_number="sip:desk@example.com").transfer_sip_uri == "sip:desk@example.com"


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("openai/gpt-4.1-mini", ("openai", "gpt-4.1-mini")),
        ("cartesia/sonic-3:voice-id", ("cartesia", "sonic-3")),
        ("gpt-realtime", ("", "gpt-realtime")),
    ],
)
def test_split_model(model: str, expected: tuple[str, str]) -> None:
    assert split_model(model) == expected
