"""Audio-in evaluation: real caller recordings through the STT, scored with WER (lecture 9.13).

Text tests never hear accents, phone noise or crosstalk. This script feeds WAV files
from ``tests/data/audio/`` through the Deepgram STT plugin (the same model family Riley
uses), compares each transcript with its reference and fails if WER is too high.
Optionally it replays each transcript through Riley in a text session so you can see
whether a mishearing changes the behaviour (``--behavior``).

Files (see ``tests/data/audio/README.md``)::

    tests/data/audio/book_tuesday_texas.wav
    tests/data/audio/book_tuesday_texas.txt     # the exact words spoken

Usage::

    python tests/evals/audio_in_eval.py                    # needs DEEPGRAM_API_KEY
    python tests/evals/audio_in_eval.py --max-wer 0.15 --keyterms
    python tests/evals/audio_in_eval.py --behavior         # also needs OPENAI_API_KEY

Exit codes: 0 pass (or skipped: no WAVs or no key), 1 WER above threshold.
Note: ``AgentSession.run(..., input_modality="audio")`` only labels the input as
audio for the agent; it does not synthesise or transcribe audio, which is why this
script calls the STT directly.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "agents"))

from maple.config import load_settings, split_model  # noqa: E402
from maple.wer import corpus_wer, wer_details  # noqa: E402

AUDIO_DIR = ROOT / "tests" / "data" / "audio"


def find_samples(directory: Path) -> list[tuple[Path, str]]:
    """Return ``(wav_path, reference_text)`` pairs that have a matching ``.txt``."""
    pairs = []
    for wav in sorted(directory.glob("*.wav")):
        ref = wav.with_suffix(".txt")
        if ref.exists():
            pairs.append((wav, ref.read_text(encoding="utf-8").strip()))
        else:
            print(f"warning: {wav.name} has no {ref.name}; skipped")
    return pairs


async def transcribe_all(samples: list[tuple[Path, str]], *, keyterms: bool) -> list[str]:
    """Transcribe each WAV with ``deepgram.STT.recognize`` (batch, not streaming)."""
    import aiohttp
    from livekit.agents.utils.audio import audio_frames_from_file
    from livekit.plugins import deepgram

    from common import DENTAL_KEYTERMS

    settings = load_settings()
    model = split_model(settings.stt_model)[1]
    results = []
    async with aiohttp.ClientSession() as http:
        extra = {"keyterm": DENTAL_KEYTERMS} if keyterms else {}
        stt = deepgram.STT(
            model=model, language=settings.language, smart_format=True, http_session=http, **extra
        )
        for wav, _ in samples:
            frames = [f async for f in audio_frames_from_file(str(wav), sample_rate=16000)]
            event = await stt.recognize(buffer=frames)
            text = event.alternatives[0].text if event.alternatives else ""
            results.append(text)
    return results


async def replay_through_riley(transcripts: list[str]) -> None:
    """Send each transcript to Riley (text session) and print the reply."""
    from livekit.agents import AgentSession
    from livekit.plugins import openai
    from s05_booking_agent import RileyBookingAgent

    from common import CallState
    from maple.scheduler import ClinicScheduler

    settings = load_settings()
    async with openai.LLM(model=split_model(settings.llm_model)[1]) as llm:
        for text in transcripts:
            async with AgentSession(llm=llm, userdata=CallState()) as session:
                await session.start(RileyBookingAgent(scheduler=ClinicScheduler.with_demo_data()))
                result = await session.run(user_input=text)
                replies = [
                    getattr(ev.item, "text_content", None)
                    for ev in result.events
                    if getattr(ev.item, "role", None) == "assistant"
                ]
                print(f"  heard: {text}\n  riley: {' '.join(r for r in replies if r)}\n")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dir", type=Path, default=AUDIO_DIR)
    parser.add_argument("--max-wer", type=float, default=0.15)
    parser.add_argument("--keyterms", action="store_true", help="boost dental keyterms")
    parser.add_argument("--behavior", action="store_true", help="replay transcripts through Riley")
    args = parser.parse_args(argv)

    samples = find_samples(args.dir)
    if not samples:
        print(f"SKIP: no .wav/.txt pairs in {args.dir} (see tests/data/audio/README.md)")
        return 0
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("SKIP: DEEPGRAM_API_KEY not set")
        return 0

    hypotheses = asyncio.run(transcribe_all(samples, keyterms=args.keyterms))
    for (wav, ref), hyp in zip(samples, hypotheses, strict=True):
        result = wer_details(ref, hyp)
        print(f"{wav.name:<36} WER {result.wer:6.1%}\n  ref: {ref}\n  hyp: {hyp}")
    overall = corpus_wer((ref, hyp) for (_, ref), hyp in zip(samples, hypotheses, strict=True))
    print(f"\nCorpus WER: {overall:.2%} (threshold {args.max_wer:.0%})")

    if args.behavior:
        if os.getenv("OPENAI_API_KEY"):
            asyncio.run(replay_through_riley(hypotheses))
        else:
            print("SKIP behaviour replay: OPENAI_API_KEY not set")

    return 1 if overall > args.max_wer else 0


if __name__ == "__main__":
    sys.exit(main())
