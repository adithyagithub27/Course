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
