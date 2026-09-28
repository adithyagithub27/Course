"""Maple Street Dental business logic for the "Riley" voice receptionist.

Everything in this package is pure Python: no network calls, no framework
imports, and fully unit-tested. The LiveKit and Pipecat agents in
``agents/`` and ``pipecat/`` import from here so that the business rules
(clinic hours, booking, FAQ retrieval, PII redaction, cost and latency math)
can be tested offline in milliseconds.
"""

from __future__ import annotations

__all__ = [
    "config",
    "costs",
    "knowledge",
    "latency",
    "pii",
    "prompts",
    "scheduler",
    "wer",
]

__version__ = "1.0.0"
