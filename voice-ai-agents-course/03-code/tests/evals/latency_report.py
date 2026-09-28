"""Latency report: p50/p90/p95 per stage from exported metrics vs the budget (lecture 9.8).

Reads JSON-lines metrics written by ``agents/s10_observed_agent.py`` (one file per
call in ``$METRICS_DIR``) or the bundled ``tests/data/sample_metrics.jsonl``.

Usage::

    python tests/evals/latency_report.py                       # sample data
    python tests/evals/latency_report.py metrics/*.jsonl       # your own calls
    python tests/evals/latency_report.py --voice-to-voice 800  # tighter budget: fails

Exit codes: 0 all stages within budget, 1 at least one violation, 2 no data.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from maple.latency import (  # noqa: E402
    LatencyBudget,
    check_budget,
    format_report,
    load_jsonl,
    samples_from_metrics,
)

DEFAULT_FILE = ROOT / "tests" / "data" / "sample_metrics.jsonl"


def main(argv: list[str] | None = None) -> int:
    """Print the report and return the exit code."""
    defaults = LatencyBudget()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("files", nargs="*", type=Path, default=[DEFAULT_FILE])
    parser.add_argument("--percentile", type=float, default=defaults.percentile)
    parser.add_argument("--eou", type=float, default=defaults.eou_delay, help="eou_delay budget (ms)")
    parser.add_argument("--stt", type=float, default=defaults.stt_final, help="stt_final budget (ms)")
    parser.add_argument("--llm-ttft", type=float, default=defaults.llm_ttft)
    parser.add_argument("--tts-ttfb", type=float, default=defaults.tts_ttfb)
    parser.add_argument("--voice-to-voice", type=float, default=defaults.voice_to_voice)
    args = parser.parse_args(argv)

    budget = LatencyBudget(
        eou_delay=args.eou,
        stt_final=args.stt,
        llm_ttft=args.llm_ttft,
        tts_ttfb=args.tts_ttfb,
        voice_to_voice=args.voice_to_voice,
        percentile=args.percentile,
    )
    records = []
    for path in args.files:
        records.extend(load_jsonl(path))
    samples = samples_from_metrics(records)
    if not samples:
        print("No latency metrics found in", ", ".join(str(p) for p in args.files))
        return 2

    print(f"Files: {', '.join(p.name for p in args.files)}  ({len(records)} records)")
    print(f"Budget checked at p{budget.percentile:g} (milliseconds)\n")
    print(format_report(samples, budget))

    violations = check_budget(samples, budget)
    print()
    if violations:
        for v in violations:
            print("FAIL", v)
        return 1
    print("PASS: every stage is within budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
