"""PII masking for telemetry.

Masks e-mail addresses, phone numbers, Northwind employee IDs (``NW-12345``) and
payment card numbers in strings, dicts and lists. With ``hash_ids=True`` the
replacement carries a short deterministic hash so analysts can still join
records without seeing the raw value.

``langfuse_mask`` has the exact signature Langfuse expects for ``Langfuse(mask=...)``.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMPLOYEE_ID_RE = re.compile(r"\bNW-\d{5}\b")
# +49 30 1234567, (555) 123-4567, 555-123-4567, +1 555 123 4567
PHONE_RE = re.compile(
    r"(?<![\w-])(?:\+?\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s.-]?\d{3,4}[\s.-]?\d{3,4}(?![\w-])"
)
CARD_RE = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
# Ticket ids and tracking ids are *not* PII and must survive masking.
_SAFE_RE = re.compile(r"\b(?:TCK|SHP)-\d{4,8}\b")


def _luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def short_hash(value: str, salt: str = "northwind", length: int = 8) -> str:
    """Deterministic short hash for joinable pseudonyms."""
    return hashlib.sha256(f"{salt}:{value}".encode()).hexdigest()[:length]


@dataclass(frozen=True)
class MaskStats:
    emails: int = 0
    phones: int = 0
    employee_ids: int = 0
    cards: int = 0

    @property
    def total(self) -> int:
        return self.emails + self.phones + self.employee_ids + self.cards


def mask_with_stats(
    text: str, *, hash_ids: bool = False, salt: str = "northwind"
) -> tuple[str, MaskStats]:
    """Mask PII in one string; returns the masked text and counts."""
    if not text:
        return text, MaskStats()
    counts = {"emails": 0, "phones": 0, "employee_ids": 0, "cards": 0}

    def tag(kind: str, raw: str) -> str:
        if hash_ids:
            return f"<{kind}:{short_hash(raw, salt)}>"
        return f"<{kind}>"

    def sub_email(m: re.Match[str]) -> str:
        counts["emails"] += 1
        return tag("EMAIL", m.group(0).lower())

    def sub_emp(m: re.Match[str]) -> str:
        counts["employee_ids"] += 1
        return tag("EMPLOYEE_ID", m.group(0))

    def sub_card(m: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", m.group(0))
        if 13 <= len(digits) <= 19 and _luhn_ok(digits):
            counts["cards"] += 1
            return tag("CARD", digits)
        return m.group(0)

    def sub_phone(m: re.Match[str]) -> str:
        raw = m.group(0)
        digits = re.sub(r"\D", "", raw)
        if len(digits) < 7 or len(digits) > 15:
            return raw
        counts["phones"] += 1
        return tag("PHONE", digits)

    out = EMAIL_RE.sub(sub_email, text)
    out = EMPLOYEE_ID_RE.sub(sub_emp, out)
    out = CARD_RE.sub(sub_card, out)
    # protect safe ids from the phone regex
    protected: dict[str, str] = {}

    def protect(m: re.Match[str]) -> str:
        key = f"\x00{len(protected)}\x00"
        protected[key] = m.group(0)
        return key

    out = _SAFE_RE.sub(protect, out)
    out = PHONE_RE.sub(sub_phone, out)
    for key, val in protected.items():
        out = out.replace(key, val)
    return out, MaskStats(**counts)


@lru_cache(maxsize=8192)
def mask_text(text: str, *, hash_ids: bool = False, salt: str = "northwind") -> str:
    """Mask e-mails, phones, employee IDs and card numbers in ``text``; returns the masked string.

    Memoised: telemetry masks the same system prompts and tool results over and over.
    """
    return mask_with_stats(text, hash_ids=hash_ids, salt=salt)[0]


def stable_hash(value: str, salt: str = "northwind", length: int = 8) -> str:
    """Alias of :func:`short_hash`: deterministic pseudonym for joins."""
    return short_hash(value, salt, length)


def mask_value(value: Any, *, hash_ids: bool = False, salt: str = "northwind") -> Any:
    """Recursively mask strings inside dicts, lists and tuples. Other types pass through."""
    if isinstance(value, str):
        return mask_text(value, hash_ids=hash_ids, salt=salt)
    if isinstance(value, dict):
        return {k: mask_value(v, hash_ids=hash_ids, salt=salt) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_value(v, hash_ids=hash_ids, salt=salt) for v in value]
    if isinstance(value, tuple):
        return tuple(mask_value(v, hash_ids=hash_ids, salt=salt) for v in value)
    return value


def langfuse_mask(*, data: Any) -> Any:
    """Drop-in for ``Langfuse(mask=langfuse_mask)``: keyword-only ``data`` argument."""
    return mask_value(data, hash_ids=True)


#: Name used in the lecture scripts for ``Langfuse(mask=mask_fn)``.
mask_fn = langfuse_mask


def make_mask(hash_ids: bool = True, salt: str = "northwind") -> Callable[..., Any]:
    """Build a Langfuse-compatible mask function with custom options."""

    def _mask(*, data: Any) -> Any:
        return mask_value(data, hash_ids=hash_ids, salt=salt)

    return _mask


def contains_pii(text: str) -> bool:
    """Cheap check used for the PII-in-output metric."""
    return mask_with_stats(text)[1].total > 0
