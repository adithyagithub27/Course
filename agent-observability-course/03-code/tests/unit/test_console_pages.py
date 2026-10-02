"""Every Ops Console page renders without an exception (Streamlit's AppTest, no browser)."""

from __future__ import annotations

from pathlib import Path

import pytest

st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from simulator.replay import replay_day  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402

CONSOLE = Path(__file__).resolve().parents[2] / "console"
PAGES = sorted((CONSOLE / "pages").glob("*.py"), key=lambda p: int(p.stem.split("_")[0]))


@pytest.fixture(scope="module")
def store_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("console") / "spans.sqlite"
    replay_day(3, sessions=60, store=LocalSpanStore(path), judge_rate=0.6, feedback_rate=0.4)
    return str(path)


def test_pages_are_discovered():
    names = [p.stem.split("_", 1)[1] for p in PAGES]
    assert names == [
        "Live_cost",
        "Cost",
        "Latency",
        "Quality",
        "Budgets",
        "Traffic",
        "Retrieval",
        "Reliability",
        "Safety",
        "Alerts",
        "Traces",
        "Compare_replays",
    ]


@pytest.mark.parametrize("page", [CONSOLE / "ops_console.py", *PAGES], ids=lambda p: p.stem)
def test_page_renders(page, store_path, monkeypatch):
    monkeypatch.setenv("ATLAS_LOCAL_STORE", store_path)
    at = AppTest.from_file(str(page), default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    assert at.title and at.title[0].value
