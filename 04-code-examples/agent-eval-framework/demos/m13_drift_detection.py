"""Lecture 13.1 - Drift detection: four weeks of (SIMULATED) daily judge scores,
a 7-day rolling average, and alerts when it crosses the threshold or falls
5 points below the launch baseline.

    uv run python demos/m13_drift_detection.py
"""
from _common import banner

from monitoring.drift_monitor import monitor_from_rows, simulate_weeks

banner("Lecture 13.1 - drift detection")
rows = simulate_weeks()
mon = monitor_from_rows(rows)
print("Week-by-week faithfulness (7-day rolling average, SIMULATED data, seed 7):")
for day, avg in mon.rolling("faithfulness")[::3]:
    print(f"  {day}  {avg:.3f}  {'#' * int((avg - 0.7) * 100)}")
print(f"\nLaunch baseline: {mon.baseline['faithfulness']:.3f}; threshold from eval_config.yaml: {mon.thresholds['faithfulness']}")
for alert in mon.check():
    print(alert)
