"""Redact personal data from transcripts, logs and traces.

Lecture: 11.3 (PII redaction in transcripts and logs).

Covers the identifiers a dental receptionist hears every day:

=========  ==========================================  ================
Kind       Examples                                    Replacement
=========  ==========================================  ================
EMAIL      ``ana.gomez@example.com``                   ``[EMAIL]``
CARD       ``4111 1111 1111 1111`` (Luhn-checked)      ``[CARD]``
SSN        ``123-45-6789``                             ``[SSN]``
PHONE      ``(512) 555-0142``, ``+1 512 555 0142``     ``[PHONE]``
DOB        ``born 04/12/1988``, ``DOB: April 12 1988``  ``[DOB]``
=========  ==========================================  ================

Redaction is regex based, which is fast and predictable but not perfect.
It will not catch numbers spoken as words ("five one two ..."), so ask your
STT provider for digit formatting (Deepgram ``smart_format``/``numerals``)
and treat this as one layer of defence, not the only one.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
    r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)
_NUMERIC_DATE = r"\d{1,2}[/-]\d{1,2}[/-](?:\d{4}|\d{2})"
_ISO_DATE = r"\d{4}-\d{2}-\d{2}"
_WORD_DATE = rf"{_MONTH}\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}"
_DATE_ANY = rf"(?:{_NUMERIC_DATE}|{_ISO_DATE}|{_WORD_DATE})"

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CARD_RE = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")
SSN_RE = re.compile(r"\b(?!000|666|9\d\d)\d{3}[- ](?!00)\d{2}[- ](?!0000)\d{4}\b")
PHONE_RE = re.compile(r"(?<![\w-])(?:\+?1[\s.-]?)?(?:\(\d{3}\)\s?|\d{3}[\s.-]?)\d{3}[\s.-]?\d{4}(?![\w-])")
DOB_CONTEXT_RE = re.compile(
    rf"(?P<prefix>\b(?:dob|d\.o\.b\.?|date of birth|birth ?date|birthday|born(?: on)?)\b"
    rf"(?:\s+(?:is|was))?[\s:,-]*)(?P<date>{_DATE_ANY})",
    re.IGNORECASE,
)
NUMERIC_DATE_RE = re.compile(rf"\b{_NUMERIC_DATE}\b")

REPLACEMENTS = {
    "EMAIL": "[EMAIL]",
    "CARD": "[CARD]",
    "SSN": "[SSN]",
    "PHONE": "[PHONE]",
    "DOB": "[DOB]",
}


@dataclass(frozen=True)
class PiiMatch:
    """One detected identifier."""

    kind: str
    start: int
    end: int
    text: str


def luhn_valid(number: str) -> bool:
    """Return True if the digits in ``number`` pass the Luhn checksum."""
    digits = [int(ch) for ch in number if ch.isdigit()]
    if len(digits) < 13:
        return False
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def find_pii(text: str) -> list[PiiMatch]:
    """Return non-overlapping PII matches in ``text``, ordered by position.

    Earlier detectors win when spans overlap (email, card, SSN, DOB, phone),
    so a card number is never half-redacted as a phone number.
    """
    found: list[PiiMatch] = []

    def overlaps(start: int, end: int) -> bool:
        return any(start < m.end and end > m.start for m in found)

    def add(kind: str, start: int, end: int) -> None:
        if not overlaps(start, end):
            found.append(PiiMatch(kind, start, end, text[start:end]))

    for m in EMAIL_RE.finditer(text):
        add("EMAIL", m.start(), m.end())
    for m in CARD_RE.finditer(text):
        if luhn_valid(m.group()):
            add("CARD", m.start(), m.end())
    for m in SSN_RE.finditer(text):
        add("SSN", m.start(), m.end())
    for m in DOB_CONTEXT_RE.finditer(text):
        add("DOB", m.start("date"), m.end("date"))
    for m in NUMERIC_DATE_RE.finditer(text):
        add("DOB", m.start(), m.end())
    for m in PHONE_RE.finditer(text):
        add("PHONE", m.start(), m.end())
    return sorted(found, key=lambda m: m.start)


def redact(text: str, *, kinds: Sequence[str] | None = None) -> str:
    """Replace PII in ``text`` with placeholders such as ``[PHONE]``.

    Args:
        text: Transcript or log line.
        kinds: Restrict redaction to these kinds (default: all of them).
    """
    allowed = set(kinds) if kinds is not None else set(REPLACEMENTS)
    out: list[str] = []
    cursor = 0
    for m in find_pii(text):
        if m.kind not in allowed:
            continue
        out.append(text[cursor : m.start])
        out.append(REPLACEMENTS[m.kind])
        cursor = m.end
    out.append(text[cursor:])
    return "".join(out)


def contains_pii(text: str) -> bool:
    """True if :func:`find_pii` finds anything."""
    return bool(find_pii(text))


def redact_data(value: Any) -> Any:
    """Recursively redact strings inside dicts, lists and tuples (for JSON logs)."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, Mapping):
        return {k: redact_data(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_data(v) for v in value]
    if isinstance(value, tuple):
        return tuple(redact_data(v) for v in value)
    return value


class PiiRedactingFilter(logging.Filter):
    """``logging.Filter`` that redacts PII from every record before it is emitted.

    Usage::

        handler.addFilter(PiiRedactingFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact the formatted message in place and always keep the record."""
        try:
            message = record.getMessage()
        except Exception:  # pragma: no cover - malformed log call, leave untouched
            return True
        record.msg = redact(message)
        record.args = None
        return True
