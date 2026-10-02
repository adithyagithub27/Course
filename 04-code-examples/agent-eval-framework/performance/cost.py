"""
Cost engineering (Module 10.3): where the money goes and two levers.

1. Model routing: send simple FAQ questions to the cheap model and keep the
   strong model for account actions, escalations and anything risky.
2. Prompt diet: measure how many input tokens the system prompt and the tool
   schemas add to EVERY call (they are re-sent on each loop iteration).

All prices from config.settings (verify current pricing).
"""

from __future__ import annotations

import json
import re

from agents.support_agent import SYSTEM_PROMPT, TOOLS
from performance.tokens import count_tokens

CHEAP_MODEL = "gpt-4.1-mini"
STRONG_MODEL = "gpt-4.1"

RISKY = re.compile(r"@|CUST-|ticket|charged|cancel|refund after|lawyer|legal|breach|manager|human|ignore|account", re.I)


def route_model(question: str) -> str:
    """Rule-based router: FAQ-style questions go to the cheap model."""
    return STRONG_MODEL if RISKY.search(question) else CHEAP_MODEL


def prompt_overhead() -> dict[str, int]:
    """Tokens re-sent on every LLM call before the user says anything."""
    return {
        "system_prompt_tokens": count_tokens(SYSTEM_PROMPT),
        "tool_schema_tokens": count_tokens(json.dumps(TOOLS)),
    }


def savings(before: float, after: float) -> float:
    return round((before - after) / before * 100, 1) if before else 0.0
