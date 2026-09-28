#!/usr/bin/env python3
"""Batch-generate HeyGen avatar videos from a scene manifest.

Two subcommands:

    generate  Submit one HeyGen video per scene. Skips scenes that already have a
              video_id in the status file, so it is safe to re-run.
    poll      Check status for every submitted scene and download finished MP4s.

Usage:
    export HEYGEN_API_KEY=...  HEYGEN_AVATAR_ID=...  HEYGEN_VOICE_ID=...
    python heygen_batch.py generate ../scenes/section-03.json
    python heygen_batch.py poll     ../scenes/section-03.json --download-dir ../generated/S03

Endpoints used (verify against the current HeyGen API reference before the first
batch; the script prints every URL it calls):
    POST https://api.heygen.com/v2/video/generate
    GET  https://api.heygen.com/v1/video_status.get?video_id=...

Environment:
    HEYGEN_API_KEY        required
    HEYGEN_AVATAR_ID      required for generate
    HEYGEN_VOICE_ID       required for generate
    HEYGEN_AVATAR_STYLE   default "normal"
    HEYGEN_BACKGROUND     default "#0f172a" (solid colour)
    HEYGEN_SPEED          default "1.0"
    HEYGEN_BASE_URL       default https://api.heygen.com
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

BASE_URL = os.environ.get("HEYGEN_BASE_URL", "https://api.heygen.com")
GENERATE_URL = f"{BASE_URL}/v2/video/generate"
STATUS_URL = f"{BASE_URL}/v1/video_status.get"


def _headers() -> dict[str, str]:
    key = os.environ.get("HEYGEN_API_KEY")
    if not key:
        raise SystemExit("HEYGEN_API_KEY is not set")
    return {"X-Api-Key": key, "Content-Type": "application/json", "Accept": "application/json"}


def _status_path(manifest: Path) -> Path:
    return manifest.with_suffix(".status.json")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_payload(scene: dict) -> dict:
    return {
        "title": scene["scene_id"],
        "caption": False,
        "dimension": {"width": 1920, "height": 1080},
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": os.environ["HEYGEN_AVATAR_ID"],
                    "avatar_style": os.environ.get("HEYGEN_AVATAR_STYLE", "normal"),
                },
                "voice": {
                    "type": "text",
                    "input_text": scene["text"],
                    "voice_id": os.environ["HEYGEN_VOICE_ID"],
                    "speed": float(os.environ.get("HEYGEN_SPEED", "1.0")),
                },
                "background": {"type": "color", "value": os.environ.get("HEYGEN_BACKGROUND", "#0f172a")},
            }
        ],
    }


def cmd_generate(args: argparse.Namespace) -> int:
    for var in ("HEYGEN_AVATAR_ID", "HEYGEN_VOICE_ID"):
        if not os.environ.get(var):
            raise SystemExit(f"{var} is not set")
    manifest = _load(args.manifest)
    status = _load(_status_path(args.manifest))
    scenes = manifest.get("scenes", [])
    if args.limit:
        scenes = scenes[: args.limit]

    submitted = 0
    for scene in scenes:
        sid = scene["scene_id"]
        if status.get(sid, {}).get("video_id"):
            continue
        if scene["chars"] > args.max_chars:
            print(f"SKIP {sid}: {scene['chars']} chars exceeds --max-chars {args.max_chars}", file=sys.stderr)
            continue
        payload = build_payload(scene)
        if args.dry_run:
            print(f"DRY RUN POST {GENERATE_URL} for {sid} ({scene['chars']} chars)")
            continue
        print(f"POST {GENERATE_URL} for {sid} ({scene['chars']} chars, ~{scene['est_seconds']}s)")
        resp = requests.post(GENERATE_URL, headers=_headers(), json=payload, timeout=60)
        if resp.status_code != 200:
            print(f"  error {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
            status[sid] = {"error": resp.text[:300], "submitted_at": time.time()}
        else:
            data = resp.json().get("data", {})
            status[sid] = {"video_id": data.get("video_id"), "submitted_at": time.time(), "state": "submitted"}
            submitted += 1
        _save(_status_path(args.manifest), status)
        time.sleep(args.sleep)
    print(f"submitted {submitted} scenes; status in {_status_path(args.manifest)}")
    return 0


def cmd_poll(args: argparse.Namespace) -> int:
    status = _load(_status_path(args.manifest))
    if not status:
        raise SystemExit("nothing submitted yet; run generate first")
    args.download_dir.mkdir(parents=True, exist_ok=True)

    pending = True
    while pending:
        pending = False
        for sid, entry in status.items():
            video_id = entry.get("video_id")
            if not video_id or entry.get("state") == "downloaded":
                continue
            resp = requests.get(STATUS_URL, headers=_headers(), params={"video_id": video_id}, timeout=60)
            if resp.status_code != 200:
                print(f"{sid}: status error {resp.status_code}", file=sys.stderr)
                pending = True
                continue
            data = resp.json().get("data", {})
            state = data.get("status")
            entry["state"] = state
            if state == "completed" and data.get("video_url"):
                target = args.download_dir / f"{sid}.mp4"
                with requests.get(data["video_url"], stream=True, timeout=300) as dl:
                    dl.raise_for_status()
                    with target.open("wb") as fh:
                        for chunk in dl.iter_content(chunk_size=1 << 20):
                            fh.write(chunk)
                entry["state"] = "downloaded"
                entry["file"] = str(target)
                entry["duration"] = data.get("duration")
                print(f"{sid}: downloaded -> {target}")
            elif state == "failed":
                entry["error"] = json.dumps(data.get("error"))[:300]
                print(f"{sid}: FAILED {entry['error']}", file=sys.stderr)
            else:
                pending = True
                print(f"{sid}: {state}")
            _save(_status_path(args.manifest), status)
        if pending and args.wait:
            time.sleep(args.interval)
        elif pending:
            break

    done = sum(1 for e in status.values() if e.get("state") == "downloaded")
    failed = sum(1 for e in status.values() if e.get("state") == "failed" or e.get("error"))
    print(f"{done} downloaded, {failed} failed, {len(status) - done - failed} in progress")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="submit scenes to HeyGen")
    gen.add_argument("manifest", type=Path)
    gen.add_argument("--limit", type=int, default=0, help="only submit the first N scenes (pilot)")
    gen.add_argument("--max-chars", type=int, default=1400)
    gen.add_argument("--sleep", type=float, default=1.0, help="seconds between submissions")
    gen.add_argument("--dry-run", action="store_true")
    gen.set_defaults(func=cmd_generate)

    poll = sub.add_parser("poll", help="check status and download finished videos")
    poll.add_argument("manifest", type=Path)
    poll.add_argument("--download-dir", type=Path, required=True)
    poll.add_argument("--wait", action="store_true", help="keep polling until everything finishes")
    poll.add_argument("--interval", type=int, default=30)
    poll.set_defaults(func=cmd_poll)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
