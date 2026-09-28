"""Unit tests for maple.costs (lectures 6.4, 10.4)."""

from __future__ import annotations

import pytest

from maple.costs import (
    DEFAULT_PRICES,
    PHONE_PRICES,
    PriceTable,
    UsageNumbers,
    cost_breakdown,
    cost_per_minute,
    typical_cascaded_usage,
    typical_realtime_usage,
    usage_from_model_usage,
)

SIMPLE_PRICES = PriceTable(
    stt_per_minute=0.01,
    llm_input_per_million=1.0,
    llm_cached_input_per_million=0.5,
    llm_output_per_million=2.0,
    tts_per_million_chars=10.0,
    realtime_audio_input_per_million=40.0,
    realtime_audio_output_per_million=80.0,
    realtime_text_input_per_million=4.0,
    realtime_text_output_per_million=16.0,
    realtime_cached_input_per_million=1.0,
    platform_per_minute=0.01,
    telephony_per_minute=0.0,
)


def test_cascaded_breakdown_by_hand() -> None:
    usage = UsageNumbers(
        call_seconds=120,
        stt_audio_seconds=60,
        llm_input_tokens=1_000_000,
        llm_cached_input_tokens=500_000,
        llm_output_tokens=100_000,
        tts_characters=100_000,
    )
    report = cost_breakdown(usage, SIMPLE_PRICES)
    assert report.components["stt"] == pytest.approx(0.01)
    assert report.components["llm"] == pytest.approx(0.5 + 0.25 + 0.2)
    assert report.components["tts"] == pytest.approx(1.0)
    assert report.components["platform"] == pytest.approx(0.02)
    assert report.total == pytest.approx(0.01 + 0.95 + 1.0 + 0.02)
    assert report.per_minute == pytest.approx(report.total / 2)
    assert report.largest_component() == "tts"


def test_realtime_breakdown_by_hand() -> None:
    usage = UsageNumbers(
        call_seconds=60,
        realtime_audio_input_tokens=100_000,
        realtime_cached_input_tokens=50_000,
        realtime_audio_output_tokens=10_000,
        realtime_text_input_tokens=100_000,
        realtime_text_output_tokens=1_000,
    )
    report = cost_breakdown(usage, SIMPLE_PRICES)
    expected = (50_000 * 40 + 50_000 * 1 + 10_000 * 80 + 100_000 * 4 + 1_000 * 16) / 1_000_000
    assert report.components["realtime"] == pytest.approx(expected)
    assert report.components["llm"] == 0


def test_zero_length_call() -> None:
    report = cost_breakdown(UsageNumbers(call_seconds=0))
    assert report.total == 0 and report.per_minute == 0


def test_telephony_adds_per_minute_cost() -> None:
    usage = typical_cascaded_usage(3)
    web = cost_per_minute(usage, DEFAULT_PRICES)
    phone = cost_per_minute(usage, PHONE_PRICES)
    assert phone - web == pytest.approx(PHONE_PRICES.telephony_per_minute)


def test_typical_realtime_costs_more_than_cascaded_per_minute() -> None:
    cascaded = cost_per_minute(typical_cascaded_usage(5))
    realtime = cost_per_minute(typical_realtime_usage(5))
    assert 0 < cascaded < realtime


def test_negative_usage_rejected() -> None:
    with pytest.raises(ValueError):
        UsageNumbers(call_seconds=-1)
    with pytest.raises(ValueError):
        UsageNumbers(call_seconds=10, llm_input_tokens=10, llm_cached_input_tokens=20)


def test_usage_addition() -> None:
    total = UsageNumbers(call_seconds=60, tts_characters=10) + UsageNumbers(call_seconds=30, tts_characters=5)
    assert total.call_seconds == 90 and total.tts_characters == 15


def test_usage_from_livekit_model_usage() -> None:
    model_usage = [
        {
            "type": "llm_usage",
            "provider": "openai",
            "model": "gpt-4.1-mini",
            "input_tokens": 5000,
            "input_cached_tokens": 1000,
            "output_tokens": 300,
        },
        {"type": "stt_usage", "provider": "deepgram", "model": "nova-3", "audio_duration": 42.5},
        {"type": "tts_usage", "provider": "cartesia", "model": "sonic-3", "characters_count": 900},
        {"type": "eot_usage", "provider": "livekit", "model": "turn-detector", "total_requests": 12},
    ]
    usage = usage_from_model_usage(model_usage, call_seconds=90)
    assert usage.llm_input_tokens == 5000
    assert usage.llm_cached_input_tokens == 1000
    assert usage.llm_output_tokens == 300
    assert usage.stt_audio_seconds == 42.5
    assert usage.tts_characters == 900


def test_usage_from_realtime_model_usage() -> None:
    model_usage = [
        {
            "type": "llm_usage",
            "input_audio_tokens": 800,
            "output_audio_tokens": 400,
            "input_text_tokens": 2000,
            "output_text_tokens": 50,
            "input_cached_tokens": 100,
        },
    ]
    usage = usage_from_model_usage(model_usage, call_seconds=60, realtime=True)
    assert usage.realtime_audio_input_tokens == 800
    assert usage.realtime_audio_output_tokens == 400
    assert usage.llm_input_tokens == 0


def test_format_contains_every_component() -> None:
    text = cost_breakdown(typical_cascaded_usage(2)).format()
    for name in ["stt", "llm", "tts", "realtime", "platform", "telephony", "total", "per minute"]:
        assert name in text
