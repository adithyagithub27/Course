"""Run every demo offline and report which ones fail (make demos).

    uv run python demos/run_all.py            # all
    uv run python demos/run_all.py m08        # only Module 8
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
prefix = sys.argv[1] if len(sys.argv) > 1 else "m"
files = sorted(p for p in HERE.glob(f"{prefix}*.py") if p.name[1:3].isdigit())
env = dict(os.environ, OFFLINE=os.getenv("OFFLINE", "1"))
failed = []
for f in files:
    t0 = time.time()
    r = subprocess.run([sys.executable, str(f)], cwd=HERE.parent, env=env, capture_output=True, text=True, timeout=900)
    status = "ok" if r.returncode == 0 else f"FAIL ({r.returncode})"
    print(f"{status:<10} {time.time() - t0:5.1f}s  demos/{f.name}")
    if r.returncode:
        failed.append(f.name)
        print(r.stderr[-1500:])
print(f"\n{len(files) - len(failed)}/{len(files)} demos ran cleanly")
sys.exit(1 if failed else 0)
