"""Lecture 8.5 - Beyond promptfoo: scanning the agent with Garak (NVIDIA).

Garak is a CLI scanner with hundreds of canned probes. It needs torch and
conflicts with RAGAS, so install it as an isolated tool and point it at the
agent's HTTP endpoint.

    uv tool install garak==0.17.0
    uv run python demos/m08_garak_scan.py          # explains the plan; offline-safe
    uv run python demos/m08_garak_scan.py --run    # starts the endpoint and runs garak (if installed)
"""
from _common import ROOT, banner

import json
import os
import shutil
import subprocess
import sys
import time

banner("Lecture 8.5 - Garak scan", ["openai"])
cfg = ROOT / "security" / "garak" / "rest_generator.json"
probes = "probes.promptinject,probes.dan.DanInTheWild,probes.encoding.InjectBase64,probes.sysprompt_extraction"
cmd = ["garak", "--target_type", "rest", "--generator_option_file", str(cfg), "--spec", probes,
       "--generations", "1", "--report_prefix", "techcorp"]
print("1. Serve the agent:  OFFLINE=1 uv run python -m security.agent_http --port 8765")
print("2. Scan it:          " + " ".join(cmd[:5]) + " \\\n                       " + " ".join(cmd[5:]))
print(f"\nREST generator config ({cfg.relative_to(ROOT)}):\n{json.dumps(json.loads(cfg.read_text()), indent=2)}")
print("\nProbe families: promptinject (goal hijacking), dan (jailbreak prompts),")
print("encoding.InjectBase64 (encoded payloads), sysprompt_extraction (prompt leaks).")
if "--run" not in sys.argv:
    print("\nNot running (pass --run). Garak installed:", bool(shutil.which("garak")))
    sys.exit(0)
if not shutil.which("garak"):
    sys.exit("garak not found: uv tool install garak==0.17.0")
server = subprocess.Popen([sys.executable, "-m", "security.agent_http", "--port", "8765"], cwd=ROOT,
                          env=dict(os.environ, OFFLINE=os.getenv("OFFLINE", "1")))
try:
    time.sleep(3)
    sys.exit(subprocess.call(cmd, cwd=ROOT))
finally:
    server.terminate()
