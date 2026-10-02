"""Lecture 14.5 - Dashboard reveal: what the capstone dashboard shows.

    uv run python demos/m14_dashboard_reveal.py   # after make capstone
    make dashboard
"""
from _common import banner

import json

from reports.experiments import RESULTS, runs
from reports.quality_dashboard import category_table, gate_status, load_latest

banner("Lecture 14.5 - dashboard reveal", ["streamlit"])
r = load_latest()
print(f"Gate: {gate_status(r)} | pass rate {r['pass_rate']:.0%} | {r['averages']}")
for row in category_table(r):
    print(f"  {row['category']:<12} {row['passed']}/{row['cases']}")
red = RESULTS / "redteam.json"
if red.exists():
    print(f"Red team: {json.loads(red.read_text())}")
print(f"Runs in history: {[h['version'] for h in runs()]}")
print("\nThe 'ship it' moment: make dashboard")
