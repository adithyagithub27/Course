"""
Single source of truth for model names, prices and the OFFLINE switch.

Decision A8: the default chat model is gpt-4.1-mini and the judge model is
gpt-4.1. Both can be overridden with environment variables, so a lecture can
say "set OPENAI_MODEL" and every agent, metric and demo follows.

OFFLINE=1 (the default when no OPENAI_API_KEY is set) swaps the OpenAI client
for a deterministic mock LLM and the judge for a deterministic mock judge, so
`make test` and every demo run without an API key or network.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- Models (A8) --------------------------------------------------------------
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_JUDGE_MODEL = "gpt-4.1"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def agent_model() -> str:
    """Model the agents under test use (env: OPENAI_MODEL)."""
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


def judge_model() -> str:
    """Model that grades the agents (env: OPENAI_JUDGE_MODEL)."""
    return os.getenv("OPENAI_JUDGE_MODEL", DEFAULT_JUDGE_MODEL)


def embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


def is_offline() -> bool:
    """True when the mock LLM and mock judge should be used.

    OFFLINE=1 forces offline, OFFLINE=0 forces live. When OFFLINE is unset we
    go offline if there is no OPENAI_API_KEY, so nothing ever fails for lack
    of a key.
    """
    flag = os.getenv("OFFLINE")
    if flag is not None and flag.strip() != "":
        return flag.strip().lower() not in ("0", "false", "no")
    return not os.getenv("OPENAI_API_KEY")


# --- Prices (USD per 1M tokens) ------------------------------------------------
# VERIFY CURRENT PRICING before quoting on screen: https://openai.com/api/pricing
# Values checked 2026-10-01 against the Course 4 pricing table.
PRICES_PER_1M: dict[str, dict[str, float]] = {
    "gpt-4.1": {"input": 2.00, "cached_input": 0.50, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "cached_input": 0.10, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "cached_input": 0.025, "output": 0.40},
}


def price_for(model: str) -> dict[str, float]:
    """Price row for a model name; dated snapshots map to their family."""
    name = model.split("/")[-1]
    for key in sorted(PRICES_PER_1M, key=len, reverse=True):
        if name.startswith(key):
            return PRICES_PER_1M[key]
    return PRICES_PER_1M[DEFAULT_MODEL]


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Dollar cost of one call (verify current pricing)."""
    p = price_for(model)
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000


# --- Langfuse ------------------------------------------------------------------
def langfuse_configured() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
