"""Unit tests for maple.wer, cross-checked against jiwer (lecture 9.7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from maple.wer import align, corpus_wer, normalize, wer_details, word_error_rate

DATA = Path(__file__).resolve().parents[1] / "data" / "stt_references.json"


def test_identical_is_zero() -> None:
    assert word_error_rate("book a cleaning", "book a cleaning") == 0.0


def test_counts_substitution_deletion_insertion() -> None:
    result = align(["a", "b", "c", "d"], ["a", "x", "c", "d", "e"])
    assert (result.substitutions, result.deletions, result.insertions) == (1, 0, 1)
    assert result.hits == 3
    result = align(["a", "b", "c", "d"], ["a", "c", "d"])
    assert (result.substitutions, result.deletions, result.insertions) == (0, 1, 0)


def test_wer_can_exceed_one() -> None:
    assert word_error_rate("hi", "hello there friend", normalize_text=False) == pytest.approx(3.0)


def test_empty_reference() -> None:
    assert wer_details("", "").wer == 0.0
    assert wer_details("", "extra words").wer == 1.0


def test_normalization() -> None:
    assert normalize("Dr. Chen's office, at 9:30 A.M.!") == "doctor chen's office at 9 30 am"
    assert normalize("X-ray") == "x ray"
    assert word_error_rate("Book with Dr. Chen.", "book with doctor chen") == 0.0


def test_normalization_can_be_disabled() -> None:
    # raw words: "Book"/"book", "Dr."/"doctor" and "Chen."/"chen" all count as errors
    assert word_error_rate("Book with Dr. Chen.", "book with doctor chen", normalize_text=False) == 0.75


def test_corpus_wer_is_not_mean_of_utterances() -> None:
    pairs = [("a b c d e f g h i j", "a b c d e f g h i j"), ("x", "y")]
    assert corpus_wer(pairs) == pytest.approx(1 / 11)


@pytest.mark.parametrize(
    ("ref", "hyp"),
    [
        ("I need a root canal on Thursday", "I need a root canal on Tuesday"),
        ("my insurance is Delta Dental PPO", "my insurance is delta dental"),
        ("can I see Doctor Alvarez", "can I see doctor al various please"),
        ("amoxicillin five hundred milligrams", "a moxie cillin five hundred milligrams"),
        ("cancel my appointment", ""),
    ],
)
def test_matches_jiwer_on_raw_words(ref: str, hyp: str) -> None:
    jiwer = pytest.importorskip("jiwer")
    ours = word_error_rate(ref, hyp, normalize_text=False)
    theirs = jiwer.wer(ref, hyp)
    assert ours == pytest.approx(theirs)


def test_corpus_matches_jiwer_on_reference_data() -> None:
    jiwer = pytest.importorskip("jiwer")
    items = json.loads(DATA.read_text())
    refs = [normalize(i["reference"]) for i in items]
    for system in ("baseline", "with_keyterms"):
        hyps = [normalize(i["hypotheses"][system]) for i in items]
        ours = corpus_wer(zip(refs, hyps, strict=True), normalize_text=False)
        assert ours == pytest.approx(jiwer.wer(refs, hyps))


def test_keyterms_improve_wer_on_reference_data() -> None:
    items = json.loads(DATA.read_text())
    assert len(items) >= 10
    base = corpus_wer((i["reference"], i["hypotheses"]["baseline"]) for i in items)
    boosted = corpus_wer((i["reference"], i["hypotheses"]["with_keyterms"]) for i in items)
    assert boosted < base
