"""Promote bad production traces to a dataset (Section 8.6 / 4.5).

Selection: judge overall below ``--threshold`` or negative user feedback. Items
are written to ``.atlas/dataset.jsonl`` and, when Langfuse is configured, to a
Langfuse dataset via ``create_dataset`` + ``create_dataset_item(source_trace_id=...)``
so the offline evals of Course 2 can run against new prompt versions.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from northwind.config import Settings  # noqa: E402
from northwind.pii import mask_text  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402

DATASET_NAME = "atlas-failures"


@dataclass(frozen=True)
class DatasetItem:
    input: dict[str, Any]
    expected_output: str | None
    metadata: dict[str, Any]
    source_trace_id: str


def select_bad_traces(
    store: LocalSpanStore, *, threshold: float = 0.6, limit: int = 100
) -> list[DatasetItem]:
    judge = {s.trace_id: s.value for s in store.scores(name="judge_overall")}
    fb = {s.trace_id: s.value for s in store.scores(name="user_feedback")}
    items: list[DatasetItem] = []
    for span in store.spans(kind="agent"):
        j = judge.get(span.trace_id)
        f = fb.get(span.trace_id)
        reasons = []
        if j is not None and j < threshold:
            reasons.append(f"judge_overall={j:.2f}")
        if f is not None and f <= 0.25:
            reasons.append("negative_feedback")
        if span.attr("atlas.outcome") in {"step_limit", "error", "timeout"}:
            reasons.append(str(span.attr("atlas.outcome")))
        if not reasons:
            continue
        q = mask_text(str(span.attr("langfuse.observation.input", "")), hash_ids=True)
        a = mask_text(str(span.attr("langfuse.observation.output", "")), hash_ids=True)
        items.append(
            DatasetItem(
                input={
                    "message": q,
                    "tenant": span.attr("atlas.tenant"),
                    "intent": span.attr("atlas.intent"),
                },
                expected_output=None,
                metadata={
                    "reasons": reasons,
                    "actual_output": a,
                    "prompt_version": span.attr("atlas.prompt_version"),
                    "outcome": span.attr("atlas.outcome"),
                    "judge_overall": j,
                    "user_feedback": f,
                },
                source_trace_id=span.trace_id,
            )
        )
        if len(items) >= limit:
            break
    return items


def write_jsonl(items: list[DatasetItem], path: str | Path) -> int:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(asdict(it), ensure_ascii=False, sort_keys=True) + "\n")
    return len(items)


def push_to_langfuse(items: list[DatasetItem], *, dataset_name: str = DATASET_NAME) -> int:
    from telemetry.langfuse_setup import client, init_langfuse

    lf = client() or init_langfuse(Settings.from_env())
    if lf is None:
        return 0
    try:
        lf.create_dataset(
            name=dataset_name,
            description="Atlas production failures promoted for regression testing",
        )
    except Exception:  # noqa: BLE001 - already exists
        pass
    n = 0
    for it in items:
        lf.create_dataset_item(
            dataset_name=dataset_name,
            input=it.input,
            expected_output=it.expected_output,
            metadata=it.metadata,
            source_trace_id=it.source_trace_id,
        )
        n += 1
    lf.flush()
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Promote bad traces to a dataset.")
    ap.add_argument("--store", default=None)
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", default=".atlas/dataset.jsonl")
    ap.add_argument("--langfuse", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args(argv)
    store = LocalSpanStore(args.store or Settings.from_env().local_store_path)
    if store.count() == 0 and args.seed is not None:
        from simulator.replay import replay_day

        replay_day(args.seed, store=store, incidents="quality_drift")
    items = select_bad_traces(store, threshold=args.threshold, limit=args.limit)
    n = write_jsonl(items, args.out)
    pushed = push_to_langfuse(items) if args.langfuse else 0
    print(f"selected={len(items)} written={n} -> {args.out} langfuse_items={pushed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
