"""Unit tests for maple.prompts (lectures 4.2-4.5, 7.8)."""

from __future__ import annotations

import re
from datetime import date, datetime, time

import pytest

from maple import prompts


def test_instructions_include_core_blocks() -> None:
    text = prompts.build_instructions(today=date(2026, 10, 5), booking=True, knowledge=True, security=True)
    assert "Riley" in text and "Maple Street Dental" in text
    assert "AI assistant" in text  # disclosure
    assert "one question at a time" in text
    assert "Never use markdown" in text
    assert "read the details" in text  # read-back before booking
    assert "nine one one" in text  # emergencies
    assert "cannot give medical advice" in text
    assert "Today is Monday, 2026-10-05" in text
    assert "verify_caller" in text


def test_blocks_are_optional() -> None:
    minimal = prompts.build_instructions(safety=False, escalation=False)
    assert "Booking, rescheduling" not in minimal
    assert "Safety:" not in minimal
    assert "Escalation:" not in minimal


def test_prompts_contain_no_markdown_formatting() -> None:
    text = prompts.build_instructions(today=date(2026, 10, 5), booking=True, knowledge=True, security=True)
    assert "**" not in text and "#" not in text


def test_greeting_discloses_ai_and_is_short() -> None:
    assert "AI assistant" in prompts.GREETING
    assert len(prompts.GREETING.split()) < 30


def test_language_blocks() -> None:
    assert "Spanish" in prompts.language_block("es")
    assert "Hindi" in prompts.language_block("hi")
    assert "Spanish" in prompts.build_instructions(language="es")
    assert set(prompts.GREETINGS) == {"en", "es", "hi"}
    with pytest.raises(ValueError):
        prompts.language_block("fr")


@pytest.mark.parametrize(
    ("n", "words"),
    [
        (0, "zero"),
        (7, "seven"),
        (13, "thirteen"),
        (20, "twenty"),
        (42, "forty-two"),
        (100, "one hundred"),
        (250, "two hundred fifty"),
        (1500, "one thousand five hundred"),
    ],
)
def test_number_to_words(n: int, words: str) -> None:
    assert prompts.number_to_words(n) == words


@pytest.mark.parametrize(
    ("n", "words"),
    [
        (1, "first"),
        (2, "second"),
        (3, "third"),
        (5, "fifth"),
        (12, "twelfth"),
        (20, "twentieth"),
        (21, "twenty-first"),
        (30, "thirtieth"),
        (31, "thirty-first"),
    ],
)
def test_ordinal_words(n: int, words: str) -> None:
    assert prompts.ordinal_words(n) == words


@pytest.mark.parametrize(
    ("t", "spoken"),
    [
        (time(9, 0), "nine o'clock in the morning"),
        (time(9, 30), "nine thirty in the morning"),
        (time(9, 5), "nine oh five in the morning"),
        (time(12, 0), "noon"),
        (time(14, 30), "two thirty in the afternoon"),
        (time(17, 15), "five fifteen in the evening"),
    ],
)
def test_speak_time(t: time, spoken: str) -> None:
    assert prompts.speak_time(t) == spoken


def test_speak_date_and_slot() -> None:
    assert prompts.speak_date(date(2026, 10, 6)) == "Tuesday, October sixth"
    assert (
        prompts.speak_date(date(2026, 10, 6), include_year=True)
        == "Tuesday, October sixth, twenty twenty-six"
    )
    assert (
        prompts.speak_slot(datetime(2026, 10, 6, 9, 30))
        == "Tuesday, October sixth at nine thirty in the morning"
    )


def test_speak_year() -> None:
    assert prompts.speak_year(1988) == "nineteen eighty-eight"
    assert prompts.speak_year(2005) == "two thousand five"
    assert prompts.speak_year(1900) == "nineteen hundred"
    assert prompts.speak_year(1905) == "nineteen oh five"


def test_speak_phone() -> None:
    assert prompts.speak_phone("(512) 555-0142") == "five one two, five five five, zero one four two"
    assert prompts.speak_phone("+1 512 555 0142") == "five one two, five five five, zero one four two"
    assert prompts.speak_phone("911") == "nine one one"


def test_spoken_helpers_output_has_no_digits() -> None:
    spoken = prompts.speak_slot(datetime(2026, 12, 31, 16, 45)) + prompts.speak_phone("5125550142")
    assert not re.search(r"\d", spoken)
