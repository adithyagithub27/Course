"""LangSmith alternative (Section 12.2): ``traceable``, ``wrap_openai`` and feedback.

Import-guarded: LangSmith is an optional extra (``pip install .[langsmith]``).
Enabled only when ``LANGSMITH_API_KEY`` is set; otherwise every helper is a no-op
so Atlas runs unchanged.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any, TypeVar

log = logging.getLogger("atlas.langsmith")
F = TypeVar("F", bound=Callable[..., Any])

try:  # pragma: no cover - import guard
    from langsmith import Client, traceable
    from langsmith.wrappers import wrap_openai

    LANGSMITH_AVAILABLE = True
except Exception:  # noqa: BLE001
    LANGSMITH_AVAILABLE = False
    Client = None  # type: ignore[assignment,misc]

    def traceable(*_a: Any, **_k: Any):  # type: ignore[no-redef]
        def deco(fn):  # type: ignore[no-untyped-def]
            return fn

        return deco if not (_a and callable(_a[0])) else _a[0]

    def wrap_openai(client: Any, **_k: Any) -> Any:  # type: ignore[no-redef]
        return client


def langsmith_enabled() -> bool:
    return LANGSMITH_AVAILABLE and bool(os.environ.get("LANGSMITH_API_KEY"))


def traced(name: str, run_type: str = "chain") -> Callable[[F], F]:
    """``@traceable`` when LangSmith is enabled, identity otherwise."""
    if not langsmith_enabled():
        return lambda fn: fn
    return traceable(name=name, run_type=run_type)  # type: ignore[return-value]


def wrap_openai_if_enabled(client: Any) -> Any:
    """``wrap_openai(client)`` records every OpenAI call as a LangSmith run."""
    if not langsmith_enabled():
        return client
    return wrap_openai(client)


def send_feedback(run_id: str, key: str, score: float, comment: str | None = None) -> bool:
    if not langsmith_enabled():
        return False
    try:
        Client().create_feedback(run_id, key, score=score, comment=comment)
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("langsmith feedback failed: %s", exc)
        return False
