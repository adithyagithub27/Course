"""Word error rate (WER) in pure Python.

Lecture: 9.7 (measuring STT accuracy with WER).

WER = (substitutions + deletions + insertions) / words in the reference.

We compute it with a word-level Levenshtein alignment and cross-check the
result against ``jiwer`` in ``tests/unit/test_wer.py`` and
``tests/evals/stt_wer_eval.py``.

Normalisation matters more than the algorithm: "Dr." vs "doctor" or
"9:30" vs "nine thirty" are formatting differences, not recognition errors.
:func:`normalize` lowercases, strips punctuation and applies a small,
explicit replacement table. Keep your normalisation identical for every
provider you compare.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

DEFAULT_REPLACEMENTS: Mapping[str, str] = {
    "dr": "doctor",
    "st": "street",
    "appt": "appointment",
    "ok": "okay",
    "o'clock": "oclock",
    "a.m.": "am",
    "p.m.": "pm",
}

_PUNCT = re.compile(r"[^\w\s']")


@dataclass(frozen=True)
class WerResult:
    """Alignment counts and the resulting error rate."""

    substitutions: int
    deletions: int
    insertions: int
    hits: int
    reference_words: int

    @property
    def errors(self) -> int:
        """Total edit operations."""
        return self.substitutions + self.deletions + self.insertions

    @property
    def wer(self) -> float:
        """Word error rate. An empty reference gives 0.0 (or 1.0 if anything was inserted)."""
        if self.reference_words == 0:
            return 0.0 if self.insertions == 0 else 1.0
        return self.errors / self.reference_words


def normalize(text: str, replacements: Mapping[str, str] | None = None) -> str:
    """Lowercase, apply word replacements, drop punctuation and collapse spaces.

    Hyphens become spaces so "x-ray" and "x ray" compare equal. Apostrophes
    inside words are kept ("don't").
    """
    table = DEFAULT_REPLACEMENTS if replacements is None else replacements
    lowered = text.lower().replace("-", " ")
    words = []
    for word in lowered.split():
        for candidate in (word, word.rstrip("!?,;:"), word.rstrip(".,!?;:")):
            if candidate in table:
                word = table[candidate]
                break
        words.append(word)
    cleaned = _PUNCT.sub(" ", " ".join(words))
    cleaned = " ".join(w.strip("'") for w in cleaned.split())
    return " ".join(cleaned.split())


def align(reference: list[str], hypothesis: list[str]) -> WerResult:
    """Word-level Levenshtein alignment with substitution/deletion/insertion counts."""
    rows, cols = len(reference) + 1, len(hypothesis) + 1
    # dist[i][j] = (cost, subs, dels, ins) for reference[:i] vs hypothesis[:j]
    dist: list[list[tuple[int, int, int, int]]] = [[(0, 0, 0, 0)] * cols for _ in range(rows)]
    for i in range(1, rows):
        dist[i][0] = (i, 0, i, 0)
    for j in range(1, cols):
        dist[0][j] = (j, 0, 0, j)
    for i in range(1, rows):
        for j in range(1, cols):
            if reference[i - 1] == hypothesis[j - 1]:
                dist[i][j] = dist[i - 1][j - 1]
                continue
            c, s, d, n = dist[i - 1][j - 1]
            sub = (c + 1, s + 1, d, n)
            c, s, d, n = dist[i - 1][j]
            dele = (c + 1, s, d + 1, n)
            c, s, d, n = dist[i][j - 1]
            ins = (c + 1, s, d, n + 1)
            dist[i][j] = min(sub, dele, ins, key=lambda t: (t[0], t[1] == 0))
    _cost, subs, dels, ins = dist[-1][-1]
    hits = len(reference) - subs - dels
    return WerResult(subs, dels, ins, hits, len(reference))


def wer_details(reference: str, hypothesis: str, *, normalize_text: bool = True) -> WerResult:
    """Return the full :class:`WerResult` for one reference/hypothesis pair."""
    if normalize_text:
        reference, hypothesis = normalize(reference), normalize(hypothesis)
    return align(reference.split(), hypothesis.split())


def word_error_rate(reference: str, hypothesis: str, *, normalize_text: bool = True) -> float:
    """Return WER for one pair. ``normalize_text=False`` compares raw whitespace-split words."""
    return wer_details(reference, hypothesis, normalize_text=normalize_text).wer


def corpus_wer(pairs: Iterable[tuple[str, str]], *, normalize_text: bool = True) -> float:
    """Corpus-level WER: total errors divided by total reference words.

    This is what ``jiwer.wer(list_of_refs, list_of_hyps)`` reports, and it is
    not the same as averaging per-utterance WER.
    """
    errors = 0
    words = 0
    for reference, hypothesis in pairs:
        result = wer_details(reference, hypothesis, normalize_text=normalize_text)
        errors += result.errors
        words += result.reference_words
    return errors / words if words else 0.0
