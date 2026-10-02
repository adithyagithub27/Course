"""
Production quality drift monitor (Module 13.1).

Production traffic is sampled, scored by the judge, and fed to the monitor.
The monitor keeps a rolling average per metric and alerts when it crosses the
threshold, or drops too far below the launch baseline.

    mon = DriftMonitor(window=7)
    mon.record(day, "faithfulness", 0.91)
    mon.check() -> list[Alert]

``simulate_weeks`` produces 4 weeks of daily scores with a slow faithfulness
decline from day 15 (a silent model update). It is SIMULATED data with a fixed
seed, labelled as such, for the demo and the tests.
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from config.thresholds import load_thresholds


@dataclass
class Alert:
    day: str
    metric: str
    rolling_avg: float
    threshold: float
    kind: str  # "threshold" | "baseline_drop"

    def __str__(self) -> str:
        return f"[{self.day}] ALERT {self.metric}: 7-day avg {self.rolling_avg:.3f} ({self.kind}, limit {self.threshold:.3f})"


class DriftMonitor:
    def __init__(self, window: int = 7, max_drop: float = 0.05, thresholds: dict | None = None) -> None:
        self.window = window
        self.max_drop = max_drop
        self.thresholds = thresholds or load_thresholds()
        self.series: dict[str, list[tuple[str, float]]] = defaultdict(list)
        self.baseline: dict[str, float] = {}

    def record(self, day: str, metric: str, value: float) -> None:
        self.series[metric].append((day, value))
        if metric not in self.baseline and len(self.series[metric]) == self.window:
            self.baseline[metric] = sum(v for _, v in self.series[metric]) / self.window

    def rolling(self, metric: str) -> list[tuple[str, float]]:
        vals = self.series[metric]
        out = []
        for i in range(self.window - 1, len(vals)):
            chunk = [v for _, v in vals[i - self.window + 1 : i + 1]]
            out.append((vals[i][0], sum(chunk) / len(chunk)))
        return out

    def check(self) -> list[Alert]:
        alerts: list[Alert] = []
        for metric in self.series:
            thr = self.thresholds.get(metric)
            fired = set()
            for day, avg in self.rolling(metric):
                if thr is not None and avg < thr and "threshold" not in fired:
                    alerts.append(Alert(day, metric, round(avg, 3), thr, "threshold"))
                    fired.add("threshold")
                base = self.baseline.get(metric)
                if base is not None and avg < base - self.max_drop and "baseline_drop" not in fired:
                    alerts.append(Alert(day, metric, round(avg, 3), round(base - self.max_drop, 3), "baseline_drop"))
                    fired.add("baseline_drop")
        return sorted(alerts, key=lambda a: a.day)


def simulate_weeks(start: date = date(2026, 9, 1), days: int = 28, seed: int = 7) -> list[dict]:
    """SIMULATED daily judge averages: faithfulness slowly degrades from day 15."""
    rng = random.Random(seed)
    rows = []
    for d in range(days):
        decline = max(0, d - 14) * 0.012
        rows.append({
            "day": (start + timedelta(days=d)).isoformat(),
            "faithfulness": round(min(1.0, 0.92 - decline + rng.uniform(-0.02, 0.02)), 3),
            "answer_relevancy": round(0.90 + rng.uniform(-0.02, 0.02), 3),
            "task_completion": round(0.88 - decline / 2 + rng.uniform(-0.02, 0.02), 3),
        })
    return rows


def monitor_from_rows(rows: list[dict]) -> DriftMonitor:
    mon = DriftMonitor()
    for r in rows:
        for k, v in r.items():
            if k != "day":
                mon.record(r["day"], k, v)
    return mon
