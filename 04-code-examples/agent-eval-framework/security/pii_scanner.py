"""
PII scanner for agent outputs (Module 8.3).

Regex detectors for the PII types the course data contains, with an
allow-list so a customer's OWN email in their own conversation isn't flagged.

    scan("Contact bob@example.com", allowed={"alice@example.com"})
    -> [Finding(kind='email', value='bob@example.com')]
    scan_responses(list_of_outputs) -> report dict
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]*\w"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[- ]){3}\d{4}\b"),
    "phone": re.compile(r"\b\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b"),
    "customer_id": re.compile(r"\bCUST-\d{3}\b"),
    "bank_account": re.compile(r"\bACC-\d{4}-[A-Z]{3}\b"),
    "api_key": re.compile(r"\bsk-[A-Za-z0-9]{8,}\b"),
}

# Company addresses that are fine to show.
PUBLIC = {"security@techcorp.com", "docs.techcorp.com"}


@dataclass(frozen=True)
class Finding:
    kind: str
    value: str


def scan(text: str, allowed: set[str] | None = None) -> list[Finding]:
    allowed = (allowed or set()) | PUBLIC
    found = []
    for kind, pat in PATTERNS.items():
        for m in pat.findall(text or ""):
            if m not in allowed:
                found.append(Finding(kind, m))
    return found


def scan_responses(outputs: list[str], allowed: set[str] | None = None) -> dict:
    """Scan many outputs. Returns counts by type and the leaking indexes."""
    leaks = []
    by_kind: dict[str, int] = {}
    for i, out in enumerate(outputs):
        f = scan(out, allowed)
        if f:
            leaks.append({"index": i, "findings": [(x.kind, x.value) for x in f], "text": out})
            for x in f:
                by_kind[x.kind] = by_kind.get(x.kind, 0) + 1
    return {"scanned": len(outputs), "leaking": len(leaks), "by_kind": by_kind, "leaks": leaks}
