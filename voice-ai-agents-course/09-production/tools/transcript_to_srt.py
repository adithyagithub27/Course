#!/usr/bin/env python3
"""Convert agent conversation events (JSONL) into an SRT caption file.

The input is a transcript you export yourself (for example from the
``conversation_item_added`` events of an ``AgentSession``): one JSON object per
line with at least: ``t`` (seconds since call start, float),
``role`` ("user" or "assistant") and ``text``. Optional ``end`` gives the end time;
otherwise the caption lasts until the next line or a reading-speed estimate.
Note: the course agents do not write this file; ``agents/s10_observed_agent.py``
writes per-turn *metrics* JSONL, which is a different format.

Usage:
    python transcript_to_srt.py call.jsonl --out call.srt --agent-name Riley --user-name Caller
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

READING_WPS = 3.0  # words per second used when no end time is present


def fmt(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--agent-name", default="Riley")
    parser.add_argument("--user-name", default="Caller")
    parser.add_argument("--offset", type=float, default=0.0, help="seconds to add to every timestamp")
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.events.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [r for r in rows if r.get("text")]
    rows.sort(key=lambda r: float(r.get("t", 0)))

    out: list[str] = []
    for i, row in enumerate(rows, start=1):
        start = float(row["t"]) + args.offset
        if row.get("end") is not None:
            end = float(row["end"]) + args.offset
        else:
            est = max(1.2, len(str(row["text"]).split()) / READING_WPS)
            nxt = float(rows[i]["t"]) + args.offset if i < len(rows) else start + est
            end = min(start + est, nxt - 0.05) if nxt > start else start + est
        speaker = args.agent_name if row.get("role") == "assistant" else args.user_name
        out.append(f"{i}\n{fmt(start)} --> {fmt(end)}\n{speaker}: {row['text']}\n")

    args.out.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {len(out)} captions to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
