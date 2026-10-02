"""Lecture 8.2 - promptfoo red team against the REAL tool-calling agent.

promptfoo calls security/promptfoo/provider.py, which runs the actual agent and
returns its reply plus the tools it called, so assertions check actions.

    uv run python demos/m08_promptfoo_redteam.py           # show commands + Python equivalent
    uv run python demos/m08_promptfoo_redteam.py --run     # run promptfoo via npx (Node 20+)
"""
from _common import ROOT, banner

import os
import shutil
import subprocess
import sys

from agents.support_agent import run_support_agent
from evaluators.golden import load
from security.redteam import run_redteam

banner("Lecture 8.2 - promptfoo red team", ["openai", "deepeval"])
PF = "promptfoo@0.123.1"
cmd = ["npx", "-y", PF, "eval", "-c", "promptfooconfig.yaml", "--no-cache", "--no-progress-bar"]
print("Static suite (offline, deterministic asserts):")
print(f"  cd security/promptfoo && OFFLINE=1 PROMPTFOO_PYTHON={ROOT}/.venv/bin/python {' '.join(cmd)}")
print("Generated attacks (live, needs OPENAI_API_KEY):")
print(f"  npx {PF} redteam run -c security/promptfoo/redteam.yaml && npx {PF} redteam report\n")
if "--run" in sys.argv and shutil.which("npx"):
    env = dict(os.environ, OFFLINE=os.getenv("OFFLINE", "1"), PROMPTFOO_PYTHON=sys.executable,
               PROMPTFOO_DISABLE_TELEMETRY="1", PROMPTFOO_DISABLE_UPDATE="1")
    sys.exit(subprocess.call(cmd, cwd=ROOT / "security" / "promptfoo", env=env))
print("Same 10 attacks through the Python red-team runner:")
rep = run_redteam(load("redteam_support"), run_support_agent, {"lookup_customer", "send_email", "create_ticket"})
for row in rep["rows"]:
    print(f"  {row['id']} {row['category']:<26} {'PASS' if row['passed'] else 'FAIL'}  {row['reply'][:60]}")
print(f"\n{rep['passed']}/{rep['total']} attacks blocked")
