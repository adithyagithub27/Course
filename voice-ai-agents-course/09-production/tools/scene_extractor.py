#!/usr/bin/env python3
"""Extract HeyGen avatar scenes from lecture scripts.

Reads the Markdown lecture scripts in ``02-lecture-scripts/``, finds narration
that follows an ``[AVATAR]`` cue (up to the next production cue such as
``[SCREEN: ...]``, ``[SLIDE ...]``, ``[CODE: ...]``, ``[DEMO: ...]``), and writes
a JSON manifest of scenes ready for ``heygen_batch.py``.

Optionally polishes each scene for text-to-speech with the OpenAI API:
spell out numbers, remove Markdown, expand acronyms on first use, and apply the
pronunciation glossary in ``pronunciation.json``.

Usage:
    python scene_extractor.py ../../02-lecture-scripts/section-03-first-agent.md \
        --out ../scenes/section-03.json [--polish] [--max-chars 1400]

Environment:
    OPENAI_API_KEY   required only with --polish
    OPENAI_MODEL     default gpt-4.1-mini
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

WORDS_PER_MINUTE = 140
CUE_RE = re.compile(r"^\s*\[(AVATAR|SLIDE|SCREEN|CODE|DEMO|B-ROLL|PAUSE)[^\]]*\]", re.IGNORECASE)
LECTURE_HEADER_RE = re.compile(r"^#{2,4}\s*(?:Lecture\s+)?(\d+\.\d+[a-z]?)\b[\s:—-]*(.*)$", re.IGNORECASE)
CODE_FENCE_RE = re.compile(r"^\s*```")


@dataclass
class Scene:
    lecture_id: str
    lecture_title: str
    scene_id: str
    beat: str
    text: str
    chars: int
    est_seconds: int


def _beat_from_context(preceding_lines: list[str]) -> str:
    """Guess the 7-beat name from nearby headings so file names are meaningful."""
    joined = " ".join(preceding_lines[-6:]).lower()
    for beat in ("hook", "promise", "context", "teach", "show", "recap", "bridge", "intro"):
        if beat in joined:
            return beat
    return "avatar"


def extract_scenes(markdown: str) -> list[Scene]:
    scenes: list[Scene] = []
    lecture_id, lecture_title = "0.0", "untitled"
    buffer: list[str] = []
    in_avatar = False
    in_code = False
    counter = 0
    recent: list[str] = []

    def flush() -> None:
        nonlocal buffer, counter
        text = " ".join(part.strip() for part in buffer if part.strip())
        text = re.sub(r"\s+", " ", text).strip()
        if len(text.split()) >= 8:
            counter += 1
            beat = _beat_from_context(recent)
            scenes.append(
                Scene(
                    lecture_id=lecture_id,
                    lecture_title=lecture_title,
                    scene_id=f"{lecture_id}-{counter:02d}-{beat}",
                    beat=beat,
                    text=text,
                    chars=len(text),
                    est_seconds=round(len(text.split()) / WORDS_PER_MINUTE * 60),
                )
            )
        buffer = []

    for line in markdown.splitlines():
        if CODE_FENCE_RE.match(line):
            in_code = not in_code
            if in_avatar:
                flush()
                in_avatar = False
            continue
        if in_code:
            continue

        header = LECTURE_HEADER_RE.match(line)
        if header:
            if in_avatar:
                flush()
                in_avatar = False
            lecture_id, lecture_title = header.group(1), header.group(2).strip() or lecture_title
            counter = 0
            recent.append(line)
            continue

        cue = CUE_RE.match(line)
        if cue:
            if in_avatar:
                flush()
            in_avatar = cue.group(1).upper() == "AVATAR"
            recent.append(line)
            # Narration may follow the cue on the same line.
            trailing = line[cue.end():].strip()
            if in_avatar and trailing:
                buffer.append(trailing)
            continue

        if in_avatar:
            if line.strip().startswith(("#", "|", "- ", "* ", ">")):
                # Structural Markdown ends the spoken block.
                flush()
                in_avatar = False
                recent.append(line)
                continue
            buffer.append(line)
        else:
            recent.append(line)
        recent = recent[-20:]

    if in_avatar:
        flush()
    return scenes


def chunk_scene(scene: Scene, max_chars: int) -> list[Scene]:
    if scene.chars <= max_chars:
        return [scene]
    sentences = re.split(r"(?<=[.!?])\s+", scene.text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current.strip())
    out: list[Scene] = []
    for i, text in enumerate(chunks, start=1):
        out.append(
            Scene(
                lecture_id=scene.lecture_id,
                lecture_title=scene.lecture_title,
                scene_id=f"{scene.scene_id}-p{i}",
                beat=scene.beat,
                text=text,
                chars=len(text),
                est_seconds=round(len(text.split()) / WORDS_PER_MINUTE * 60),
            )
        )
    return out


def load_glossary(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def apply_glossary(text: str, glossary: dict[str, str]) -> str:
    for term, spoken in glossary.items():
        text = re.sub(rf"\b{re.escape(term)}\b", spoken, text)
    return text


def polish_with_openai(text: str, glossary: dict[str, str]) -> str:
    """Rewrite narration for TTS without changing meaning. Requires OPENAI_API_KEY."""
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("pip install openai to use --polish") from exc

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    glossary_lines = "\n".join(f"- {k} -> {v}" for k, v in glossary.items()) or "- (none)"
    instructions = (
        "You prepare spoken narration for a text-to-speech avatar in a technical course. "
        "Rewrite the text so it sounds natural when read aloud. Rules: keep every fact, number and "
        "code identifier; spell out numbers under one hundred and all percentages as words; remove "
        "Markdown symbols, bullet markers and URLs; expand acronyms the first time they appear using "
        "the glossary; keep sentences short; do not add or remove ideas; do not add greetings. "
        f"Glossary (term -> spoken form):\n{glossary_lines}"
    )
    response = client.responses.create(model=model, instructions=instructions, input=text)
    return response.output_text.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scripts", nargs="+", type=Path, help="lecture script Markdown files")
    parser.add_argument("--out", type=Path, required=True, help="manifest JSON to write")
    parser.add_argument("--max-chars", type=int, default=1400, help="max characters per HeyGen scene")
    parser.add_argument("--polish", action="store_true", help="polish narration for TTS with OpenAI")
    parser.add_argument("--glossary", type=Path, default=Path(__file__).with_name("pronunciation.json"))
    args = parser.parse_args()

    glossary = load_glossary(args.glossary)
    scenes: list[Scene] = []
    for script in args.scripts:
        extracted = extract_scenes(script.read_text(encoding="utf-8"))
        for scene in extracted:
            if args.polish:
                scene.text = polish_with_openai(scene.text, glossary)
            else:
                scene.text = apply_glossary(scene.text, glossary)
            scene.chars = len(scene.text)
            scene.est_seconds = round(len(scene.text.split()) / WORDS_PER_MINUTE * 60)
            scenes.extend(chunk_scene(scene, args.max_chars))
        print(f"{script.name}: {len(extracted)} avatar scenes", file=sys.stderr)

    total_seconds = sum(s.est_seconds for s in scenes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(
            {
                "scenes": [asdict(s) for s in scenes],
                "summary": {"scene_count": len(scenes), "est_minutes": round(total_seconds / 60, 1)},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote {len(scenes)} scenes (~{total_seconds / 60:.1f} min of avatar) to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
