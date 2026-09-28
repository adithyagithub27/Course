"""WER report for STT transcripts against references (lecture 9.7).

Reads ``tests/data/stt_references.json``: each item has a ``reference`` transcript and
one hypothesis per STT configuration (``baseline`` = Nova-3 without keyterms,
``with_keyterms`` = Nova-3 with the dental keyterms from ``agents/common.py``).

For every system it prints per-utterance WER and corpus WER from ``maple.wer`` and,
when installed, cross-checks the corpus number against ``jiwer`` using the same
normalisation. It also lists key-term misses (names, drugs, insurers that appear in
the reference but not in the transcript), because one missed dentist's name matters
more than five missed "the"s. Runs offline.

Usage::

    python tests/evals/stt_wer_eval.py
    python tests/evals/stt_wer_eval.py --max-wer 0.10 --system with_keyterms

Exit codes: 0 ok, 1 a system is over ``--max-wer`` or maple/jiwer disagree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from maple.wer import corpus_wer, normalize, wer_details  # noqa: E402

DEFAULT_DATA = ROOT / "tests" / "data" / "stt_references.json"

# Key terms tracked separately from overall WER (lecture 9.7 extension).
KEY_TERMS = [
    "chen",
    "alvarez",
    "brooks",
    "amoxicillin",
    "ibuprofen",
    "invisalign",
    "delta dental",
    "root canal",
    "crown",
    "metlife",
    "cigna",
    "carecredit",
    "hygienist",
]


def key_term_misses(items: list[dict], system: str) -> list[str]:
    misses = []
    for item in items:
        ref, hyp = normalize(item["reference"]), normalize(item["hypotheses"][system])
        misses += [f"{item['id']}:{t}" for t in KEY_TERMS if t in ref and t not in hyp]
    return misses


def main(argv: list[str] | None = None) -> int:
    """Print the WER report and return the process exit code."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--max-wer", type=float, default=None, help="fail if corpus WER is above this")
    parser.add_argument("--system", default=None, help="only check this system against --max-wer")
    parser.add_argument("--raw", action="store_true", help="disable normalisation")
    args = parser.parse_args(argv)

    items = json.loads(args.data.read_text(encoding="utf-8"))
    systems = sorted({name for item in items for name in item["hypotheses"]})
    use_norm = not args.raw

    try:
        import jiwer
    except ImportError:  # pragma: no cover - dev extra not installed
        jiwer = None

    exit_code = 0
    print(f"{len(items)} utterances, normalisation {'on' if use_norm else 'off'}\n")
    for system in systems:
        print(f"== {system}")
        pairs = []
        for item in items:
            ref, hyp = item["reference"], item["hypotheses"][system]
            result = wer_details(ref, hyp, normalize_text=use_norm)
            pairs.append((ref, hyp))
            flag = (
                ""
                if result.errors == 0
                else f"  S={result.substitutions} D={result.deletions} I={result.insertions}"
            )
            print(f"  {item['id']:<8} {result.wer:6.1%}  [{item.get('condition', '')}]{flag}")
        ours = corpus_wer(pairs, normalize_text=use_norm)
        line = f"  corpus WER (maple): {ours:.2%}"
        if jiwer is not None:
            refs = [normalize(r) if use_norm else r for r, _ in pairs]
            hyps = [normalize(h) if use_norm else h for _, h in pairs]
            theirs = jiwer.wer(refs, hyps)
            match = abs(ours - theirs) < 1e-9
            line += f" | jiwer: {theirs:.2%} | {'match' if match else 'MISMATCH'}"
            if not match:
                exit_code = 1
        print(line)
        misses = key_term_misses(items, system)
        print(f"  key-term misses: {len(misses)}" + (f"  ({', '.join(misses)})" if misses else "") + "\n")
        if args.max_wer is not None and (args.system in (None, system)) and ours > args.max_wer:
            print(f"FAIL: {system} corpus WER {ours:.2%} > {args.max_wer:.2%}\n")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
