"""Regenerate the incident datasets deterministically.

    python incidents/generate.py            # all four
    python incidents/generate.py --only 1   # one incident

Each folder gets ``spans.jsonl`` (one span per line, sorted) and ``scores.jsonl``
(judge + user feedback). Running twice produces byte-identical files.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from simulator.replay import replay_day  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402


@dataclass(frozen=True)
class IncidentSpec:
    number: int
    folder: str
    seed: int
    preset: str
    sessions: int
    judge_rate: float


INCIDENTS: tuple[IncidentSpec, ...] = (
    IncidentSpec(1, "incident-01-cost-spike", 11, "cost_spike", 300, 0.3),
    IncidentSpec(2, "incident-02-latency-regression", 22, "latency_regression", 300, 0.3),
    IncidentSpec(3, "incident-03-quality-drift", 33, "quality_drift", 300, 0.5),
    IncidentSpec(4, "incident-04-project", 44, "mixed", 300, 0.35),
)


def generate(spec: IncidentSpec, out_dir: Path = HERE) -> tuple[Path, Path, str]:
    folder = out_dir / spec.folder
    folder.mkdir(parents=True, exist_ok=True)
    store = LocalSpanStore(":memory:")
    summary, _ = replay_day(
        spec.seed,
        sessions=spec.sessions,
        incidents=spec.preset,
        store=store,
        judge_rate=spec.judge_rate,
    )
    spans = folder / "spans.jsonl"
    scores = folder / "scores.jsonl"
    store.export_jsonl(spans, scores_path=scores)
    digest = hashlib.sha256(spans.read_bytes() + scores.read_bytes()).hexdigest()[:12]
    print(
        f"[incident {spec.number}] {spec.folder}: {summary.requests} requests, {summary.spans} spans, {summary.scores} scores, sha={digest}"
    )
    return spans, scores, digest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, default=None)
    ap.add_argument("--out", default=str(HERE))
    args = ap.parse_args(argv)
    for spec in INCIDENTS:
        if args.only is None or spec.number == args.only:
            generate(spec, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
