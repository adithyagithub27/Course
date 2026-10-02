"""
Run the full capstone pipeline (Module 14.5): every stage, report, gate.

    python -m capstone.run_capstone                 # support agent + SecureBank v2
    python -m capstone.run_capstone --save-baseline # first run: store the functional baseline

Writes reports/results/capstone_<agent>.md, eval.json (for the dashboard),
redteam.json, and appends to experiments.jsonl.
"""

from __future__ import annotations

import argparse
import json
import sys

from capstone.platform import QualityPlatform
from evaluators.deepeval_suite import save_report
from observability.langfuse_tracing import offline_spans, traced_support_agent
from regression.regression_suite import save_baseline
from reports.experiments import RESULTS, log_run


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-baseline", action="store_true")
    ap.add_argument("--version", default="v1.0")
    a = ap.parse_args(argv)
    platform = QualityPlatform()
    ship_all = True
    for name in ("support", "banking_v2"):
        r = platform.run(name)
        md = platform.render_report(r)
        (RESULTS / f"capstone_{name}.md").parent.mkdir(parents=True, exist_ok=True)
        (RESULTS / f"capstone_{name}.md").write_text(md)
        print(md)
        if name == "support":
            report = dict(r["functional"], version=a.version, dataset="golden_capstone")
            save_report(report, RESULTS / "eval.json")
            (RESULTS / "redteam.json").write_text(json.dumps({k: r["security"][k] for k in ("total", "passed", "by_severity")}))
            log_run(report, version=a.version, notes="capstone run")
            if a.save_baseline:
                print("baseline saved:", save_baseline(report, "support_capstone_v1"))
        ship_all &= r["gate"]["ship"]
    trace = traced_support_agent("What is your refund policy?", user_id="CUST-001", session_id="capstone")
    print(f"Observability: trace {trace['trace_id']} with {len(offline_spans(trace['trace_id'])) or 'live'} spans")
    print("OVERALL:", "SHIP" if ship_all else "BLOCK")
    return 0 if ship_all else 1


if __name__ == "__main__":
    sys.exit(main())
