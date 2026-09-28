"""Unit tests for maple.pii (lecture 11.3)."""

from __future__ import annotations

import logging

import pytest

from maple.pii import PiiRedactingFilter, contains_pii, find_pii, luhn_valid, redact, redact_data


@pytest.mark.parametrize(
    "phone",
    ["(512) 555-0142", "512-555-0142", "512.555.0142", "+1 512 555 0142", "5125550142", "1-512-555-0142"],
)
def test_phone_formats(phone: str) -> None:
    assert redact(f"call me on {phone} please") == "call me on [PHONE] please"


def test_email() -> None:
    assert redact("email ana.gomez+test@example.co.uk now") == "email [EMAIL] now"


def test_valid_card_redacted_invalid_left_alone() -> None:
    assert redact("card 4111 1111 1111 1111 ok") == "card [CARD] ok"
    assert redact("card 4111-1111-1111-1111") == "card [CARD]"
    assert "[CARD]" not in redact("order 1234 5678 9012 3456")  # fails Luhn


def test_ssn() -> None:
    assert redact("my social is 123-45-6789") == "my social is [SSN]"
    assert "[SSN]" not in redact("code 000-12-3456")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("DOB: 04/12/1988", "DOB: [DOB]"),
        ("my date of birth is April 12, 1988", "my date of birth is [DOB]"),
        ("I was born on 1988-04-12", "I was born on [DOB]"),
        ("birthday is March 3rd 1990.", "birthday is [DOB]."),
        ("seen on 10/06/2026", "seen on [DOB]"),  # numeric dates are always treated as sensitive
    ],
)
def test_dates_of_birth(text: str, expected: str) -> None:
    assert redact(text) == expected


def test_plain_appointment_words_untouched() -> None:
    text = "Your cleaning is on Tuesday, October sixth at nine thirty."
    assert redact(text) == text
    assert not contains_pii(text)


def test_multiple_kinds_in_one_line() -> None:
    text = "Jordan, 512-555-0142, jordan@example.com, DOB 04/12/1988, card 4111111111111111"
    assert redact(text) == "Jordan, [PHONE], [EMAIL], DOB [DOB], card [CARD]"
    kinds = [m.kind for m in find_pii(text)]
    assert kinds == ["PHONE", "EMAIL", "DOB", "CARD"]


def test_card_not_misread_as_phone() -> None:
    assert redact("4111 1111 1111 1111") == "[CARD]"


def test_restrict_kinds() -> None:
    text = "512-555-0142 and ana@example.com"
    assert redact(text, kinds=["EMAIL"]) == "512-555-0142 and [EMAIL]"


def test_luhn() -> None:
    assert luhn_valid("4111111111111111")
    assert luhn_valid("5500 0000 0000 0004")
    assert not luhn_valid("4111111111111112")
    assert not luhn_valid("1234")


def test_redact_data_recurses() -> None:
    data = {"caller": "512-555-0142", "turns": ["email a@b.com", ("x", 3)], "count": 2}
    assert redact_data(data) == {"caller": "[PHONE]", "turns": ["email [EMAIL]", ("x", 3)], "count": 2}


def test_logging_filter(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("pii-test")
    handler_filter = PiiRedactingFilter()
    logger.addFilter(handler_filter)
    try:
        with caplog.at_level(logging.INFO, logger="pii-test"):
            logger.info("caller said %s", "my number is 512-555-0142")
        assert "512-555-0142" not in caplog.text
        assert "[PHONE]" in caplog.text
    finally:
        logger.removeFilter(handler_filter)
