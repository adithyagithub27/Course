"""
One place that decides which LLM client the agents talk to.

    from agents.llm import get_client, clock

* Live (OFFLINE=0 and OPENAI_API_KEY set): a real ``openai.OpenAI()`` client.
* Offline (OFFLINE=1, or no key): ``MockOpenAI``, a deterministic stand-in with
  the same ``client.chat.completions.create(...)`` surface. It returns real
  ``openai`` response objects, so agent code is identical in both modes.

``clock`` measures latency. Live it is the wall clock; offline it is a virtual
clock the mock advances by a simulated, deterministic latency per call, so
benchmark numbers are repeatable on any laptop.
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Any

from config.settings import is_offline


class _WallClock:
    def now(self) -> float:
        return time.perf_counter()


class VirtualClock:
    """A clock that only moves when the mock LLM says time has passed."""

    def __init__(self) -> None:
        self._t = 0.0

    def now(self) -> float:
        return self._t

    def advance(self, seconds: float) -> None:
        self._t += seconds


_WALL = _WallClock()
_VIRTUAL = VirtualClock()


class _Clock:
    """Delegates to the wall clock live and to the virtual clock offline."""

    def now(self) -> float:
        return (_VIRTUAL if is_offline() else _WALL).now()


clock = _Clock()


@lru_cache(maxsize=2)
def _client(offline: bool) -> Any:
    if offline:
        from agents.mock_llm import MockOpenAI

        return MockOpenAI(clock=_VIRTUAL)
    from openai import OpenAI

    return OpenAI()


def get_client() -> Any:
    """Return the OpenAI client for the current mode (cached per mode)."""
    return _client(is_offline())


def get_async_client() -> Any:
    """Async client for libraries that need one (RAGAS). Live only."""
    from openai import AsyncOpenAI

    return AsyncOpenAI()
