import random

import pytest

from northwind.drift import (
    DriftThresholds,
    compare_windows,
    drift_report_markdown,
    js_divergence,
    psi,
    window_stats,
)


def test_window_stats():
    s = window_stats([1, 2, 3, 4])
    assert s.n == 4 and s.mean == 2.5 and s.min == 1 and s.max == 4 and s.p50 == 2.5
    assert window_stats([]).n == 0


def test_psi_identical_is_zero():
    xs = [random.Random(1).random() for _ in range(500)]
    assert psi(xs, xs) == pytest.approx(0.0, abs=1e-9)
    assert psi([], xs) == 0.0


def test_psi_detects_shift():
    rng = random.Random(2)
    base = [rng.gauss(0.9, 0.05) for _ in range(300)]
    shifted = [rng.gauss(0.6, 0.05) for _ in range(300)]
    assert psi(base, shifted) > 0.25
    assert js_divergence(base, shifted) > 0.3
    assert js_divergence(base, base) == pytest.approx(0.0)


def test_compare_windows_insufficient():
    r = compare_windows("m", [1.0] * 5, [1.0] * 5)
    assert r.status == "insufficient"


def test_compare_windows_ok_and_alert():
    rng = random.Random(3)
    base = [rng.gauss(0.9, 0.03) for _ in range(200)]
    same = [rng.gauss(0.9, 0.03) for _ in range(200)]
    worse = [rng.gauss(0.6, 0.03) for _ in range(200)]
    assert compare_windows("judge", base, same).status in {"ok", "watch"}
    r = compare_windows("judge", base, worse)
    assert r.alert and r.mean_delta_pct < -20 and any("psi" in x for x in r.reasons)


def test_improvement_is_not_alert_for_higher_is_better():
    base = [0.6 + i / 1000 for i in range(100)]
    better = [0.95 + i / 1000 for i in range(100)]
    r = compare_windows(
        "judge", base, better, thresholds=DriftThresholds(psi_alert=99, psi_watch=99)
    )
    assert r.status == "ok" and r.mean_delta_pct > 0


def test_lower_is_better_direction():
    base = [1000.0 + i for i in range(100)]
    slower = [2000.0 + i for i in range(100)]
    r = compare_windows(
        "latency",
        base,
        slower,
        higher_is_better=False,
        thresholds=DriftThresholds(psi_alert=99, psi_watch=99),
    )
    assert r.alert and "mean moved" in r.reasons[0]


def test_markdown_render():
    r = compare_windows("m", [1.0] * 30, [1.0] * 30)
    md = drift_report_markdown([r])
    assert md.startswith("| metric |") and "| m |" in md
    assert r.as_dict()["metric"] == "m"


def test_drift_report_prev_curr_weeks(tmp_path, capsys):
    """8.5: two replayed Mondays in one store, compared by ISO week."""
    from datetime import date

    from evals.drift_report import main, resolve_window
    from simulator.replay import replay_day
    from telemetry.local_store import LocalSpanStore

    path = tmp_path / "two-weeks.sqlite"
    store = LocalSpanStore(path)
    replay_day(7, sessions=120, store=store, judge_rate=0.8)
    replay_day(
        7,
        sessions=120,
        store=store,
        judge_rate=0.8,
        incidents="quality_drift",
        day=date(2026, 9, 21),
    )
    w38, w39 = resolve_window("2026-W38"), resolve_window("2026-W39")
    assert w38 and w39 and w39[0] - w38[0] == 7 * 86_400
    out_md = tmp_path / "drift.md"
    rc = main(
        ["--prev", "2026-W38", "--curr", "2026-W39", "--store", str(path), "--out", str(out_md)]
    )
    text = capsys.readouterr().out
    assert rc == 1 and "2026-W38 -> 2026-W39" in text and "judge_grounded" in text
    assert "judge_grounded" in out_md.read_text() and out_md.read_text().strip() == text.strip()


def test_drift_report_prev_curr_empty_week_is_explained(tmp_path):
    from evals.drift_report import main
    from simulator.replay import replay_day
    from telemetry.local_store import LocalSpanStore

    path = tmp_path / "one-week.sqlite"
    replay_day(7, sessions=40, store=LocalSpanStore(path), judge_rate=0.5)
    with pytest.raises(SystemExit, match="no requests in 2026-W39"):
        main(["--prev", "2026-W38", "--curr", "2026-W39", "--store", str(path)])
