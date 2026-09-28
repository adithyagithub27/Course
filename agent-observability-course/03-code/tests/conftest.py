"""Shared fixtures. Everything runs offline: no keys, no network."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Never let a developer's real keys leak into the test run.
for key in list(os.environ):
    if key.startswith(("LANGFUSE_", "LANGSMITH_", "OPENAI_")):
        os.environ.pop(key, None)
os.environ["OFFLINE"] = "1"
os.environ["OTEL_EXPORTER"] = "memory"
os.environ["ATLAS_LOCAL_STORE"] = ""

from northwind.config import Settings, reload_settings  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402
from telemetry.otel_setup import (  # noqa: E402
    configure_tracing,
    get_memory_exporter,
    shutdown_tracing,
)


@pytest.fixture(scope="session", autouse=True)
def _settings_reload() -> None:
    reload_settings()


@pytest.fixture
def settings() -> Settings:
    return Settings.from_env({"OFFLINE": "1", "OTEL_EXPORTER": "memory"})


@pytest.fixture
def store() -> LocalSpanStore:
    s = LocalSpanStore(":memory:")
    yield s
    s.close()


@pytest.fixture
def tracing(settings: Settings, store: LocalSpanStore):
    """Configure tracing with the in-memory exporter + in-memory store; returns the exporter."""
    configure_tracing(settings, store=store)
    exporter = get_memory_exporter()
    assert exporter is not None
    exporter.clear()
    yield exporter
    shutdown_tracing()


@pytest.fixture
def agent(settings: Settings, tracing):
    from app.agent import AtlasAgent

    return AtlasAgent(settings)


@pytest.fixture
def replayed_store() -> LocalSpanStore:
    """A small replayed day (fast) shared by console/eval tests."""
    from simulator.replay import replay_day

    _, s = replay_day(3, sessions=60, judge_rate=0.6, feedback_rate=0.3)
    yield s
    s.close()
