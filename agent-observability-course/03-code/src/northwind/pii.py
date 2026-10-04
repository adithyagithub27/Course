"""PII masking for telemetry.

Masks e-mail addresses, phone numbers, Northwind employee IDs (``NW-12345``) and
payment card numbers in strings, dicts and lists. With ``hash_ids=True`` the
replacement carries a short deterministic hash so analysts can still join
records without seeing the raw value.

The hash is a **keyed HMAC-SHA256** (Section 10.2). An unkeyed or salted SHA-256 of a
five-digit employee ID is a lookup table: anyone can hash all 100,000 IDs in a fraction
of a second. The key comes from ``ATLAS_PII_HASH_KEY`` (generate one with
``python -c "import secrets; print(secrets.token_hex(32))"``). Without it the code falls
back to :data:`DEMO_PII_HASH_KEY`, which is public (it is in this file), so the hash is
then no stronger than the old salted one; a warning is logged once when the demo key is
used outside ``OFFLINE=1``. Rotating the key breaks historical joins: plan for it.

``langfuse_mask`` has the exact signature Langfuse expects for ``Langfuse(mask=...)``.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
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

#: Format examples that the knowledge base, the system prompt and the tool schemas print
#: ("employee ID (format NW-12345)") plus the mock's placeholder. They are still masked in
#: telemetry, but :func:`contains_pii` does not count them as PII in an answer. No persona
#: in the simulator uses them; a real employee holding one of these IDs would not be counted.
EXAMPLE_IDS: frozenset[str] = frozenset({"NW-12345", "NW-00000"})

#: Fallback HMAC key for offline runs and tests. NOT A SECRET: set ATLAS_PII_HASH_KEY.
DEMO_PII_HASH_KEY = "atlas-demo-pii-key-not-a-secret"
PII_HASH_KEY_ENV = "ATLAS_PII_HASH_KEY"

log = logging.getLogger("atlas.pii")
_warned_demo_key = False


def pii_hash_key() -> bytes:
    """The HMAC key: ``ATLAS_PII_HASH_KEY`` if set, else the demo key (warns once if not offline)."""
    global _warned_demo_key
    key = os.environ.get(PII_HASH_KEY_ENV, "").strip()
    if key:
        return key.encode()
    offline = os.environ.get("OFFLINE", "1").strip().lower() in {"1", "true", "yes", "on", ""}
    if not offline and not _warned_demo_key:
        _warned_demo_key = True
        log.warning(
            "%s is not set: PII pseudonyms use the public demo key and can be reversed by "
            "brute force. Set a secret key (see .env.example).",
            PII_HASH_KEY_ENV,
        )
    return DEMO_PII_HASH_KEY.encode()


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


def short_hash(
    value: str, salt: str = "northwind", length: int = 8, *, key: bytes | None = None
) -> str:
    """Deterministic short pseudonym for joins: HMAC-SHA256 keyed with ``ATLAS_PII_HASH_KEY``.

    ``salt`` is a domain label (different salts give unrelated pseudonyms for the same value);
    the secrecy comes from the key, never from the salt."""
    k = pii_hash_key() if key is None else key
    return hmac.new(k, f"{salt}:{value}".encode(), hashlib.sha256).hexdigest()[:length]


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
    text: str, *, hash_ids: bool = False, salt: str = "northwind", key: bytes | None = None
) -> tuple[str, MaskStats]:
    """Mask PII in one string; returns the masked text and counts."""
    if not text:
        return text, MaskStats()
    counts = {"emails": 0, "phones": 0, "employee_ids": 0, "cards": 0}
    hkey = (pii_hash_key() if key is None else key) if hash_ids else b""

    def tag(kind: str, raw: str) -> str:
        if hash_ids:
            return f"<{kind}:{short_hash(raw, salt, key=hkey)}>"
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
def _mask_text_cached(text: str, hash_ids: bool, salt: str, key: bytes) -> str:
    return mask_with_stats(text, hash_ids=hash_ids, salt=salt, key=key)[0]


def mask_text(text: str, *, hash_ids: bool = False, salt: str = "northwind") -> str:
    """Mask e-mails, phones, employee IDs and card numbers in ``text``; returns the masked string.

    Memoised (per key): telemetry masks the same system prompts and tool results over and over.
    """
    return _mask_text_cached(text, hash_ids, salt, pii_hash_key() if hash_ids else b"")


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
    """Cheap check used for the PII-in-output metric.

    Documented format examples (:data:`EXAMPLE_IDS`, e.g. "format NW-12345") are not counted:
    an answer that repeats the KB's own example is not leaking anyone's data."""
    if not text:
        return False
    for example in EXAMPLE_IDS:
        text = re.sub(rf"\b{re.escape(example)}\b", " ", text)
    return mask_with_stats(text)[1].total > 0
