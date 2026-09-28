"""Fixtures for LiveKit behavior tests (lectures 9.3-9.5, 11.5).

Live tests talk to a real LLM through the OpenAI plugin and are skipped when
``OPENAI_API_KEY`` is not set. Tests marked ``@pytest.mark.offline`` use the
scripted mock LLM from ``agents/common.py`` and always run.

Every test gets a fresh scheduler with a fixed "today" (Monday 2026-10-05), so
dates in assertions never drift.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import date

import pytest

from maple.config import load_settings
from maple.scheduler import ClinicScheduler

TODAY = date(2026, 10, 5)  # Monday; "tomorrow" is Tuesday 2026-10-06


@pytest.fixture(autouse=True)
def _require_openai_key(request: pytest.FixtureRequest) -> None:
    """Skip live tests when no OpenAI key is configured (offline tests always run)."""
    if request.node.get_closest_marker("offline"):
        return
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set: live agent tests are skipped")


@pytest.fixture
def scheduler() -> ClinicScheduler:
    """Demo calendar (Jordan Lee, Priya Patel, Sam Rivera) anchored to TODAY."""
    return ClinicScheduler.with_demo_data(TODAY)


@pytest.fixture
async def llm() -> AsyncIterator[object]:
    """The LLM that runs the agent under test (also used as the judge).

    Uses ``JUDGE_MODEL`` (default ``gpt-4.1-mini``) through the OpenAI plugin so the
    tests only need ``OPENAI_API_KEY``, not LiveKit credentials.
    """
    from livekit.plugins import openai

    async with openai.LLM(model=load_settings().judge_model) as model:
        yield model


@pytest.fixture
async def judge_llm(llm: object) -> object:
    """Alias that makes judge calls read clearly in tests."""
    return llm
