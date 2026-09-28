"""Unit tests for maple.knowledge (lectures 7.1-7.3)."""

from __future__ import annotations

import time

import pytest

from maple.knowledge import FaqIndex, FaqSection, parse_faq, shorten, tokenize


@pytest.fixture(scope="module")
def index() -> FaqIndex:
    return FaqIndex.from_default()


def test_default_faq_has_expected_sections(index: FaqIndex) -> None:
    titles = {s.title for s in index.sections}
    assert len(index.sections) >= 15
    for required in [
        "Opening hours",
        "Parking",
        "Insurance accepted",
        "Cancellation policy",
        "Dental emergencies",
    ]:
        assert required in titles


@pytest.mark.parametrize(
    ("question", "expected_title"),
    [
        ("what time do you open on saturday", "Opening hours"),
        ("are you open on sunday", "Opening hours"),
        ("where can I park my car", "Parking"),
        ("where are you located", "Address and directions"),
        ("do you take Delta Dental insurance", "Insurance accepted"),
        ("I need to cancel, is there a fee", "Cancellation policy"),
        ("my tooth got knocked out", "Dental emergencies"),
        ("how much is a crown", "Pricing ranges"),
        ("can I pay monthly", "Payment options and payment plans"),
        ("do you see kids", "Children and families"),
        ("is the office wheelchair accessible", "Accessibility"),
        ("do you speak spanish", "Languages spoken"),
        ("I have the flu, should I still come", "Illness and COVID policy"),
        ("what forms do new patients fill out", "New patient forms"),
        ("will you remind me about my appointment", "Appointment reminders"),
    ],
)
def test_top_hit(index: FaqIndex, question: str, expected_title: str) -> None:
    hits = index.search(question, k=1)
    assert hits, f"no hit for {question!r}"
    assert hits[0].title == expected_title


@pytest.mark.parametrize(
    "question", ["can you help me with my taxes", "tell me a joke", "what's the weather like"]
)
def test_off_topic_returns_nothing(index: FaqIndex, question: str) -> None:
    assert index.search(question) == []
    assert index.answer(question) == "NO_MATCH"


def test_results_are_ranked_and_limited(index: FaqIndex) -> None:
    hits = index.search("insurance payment price", k=3)
    assert 1 <= len(hits) <= 3
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)


def test_answers_are_short_and_speakable(index: FaqIndex) -> None:
    for section in index.sections:
        hits = index.search(section.title, k=1)
        assert hits, section.title
        answer = hits[0].answer
        assert len(answer) <= 450
        assert "*" not in answer and "#" not in answer and "http" not in answer


def test_answer_formats_title_and_text(index: FaqIndex) -> None:
    text = index.answer("parking", k=1)
    assert text.startswith("Parking: ")


def test_parse_faq_ignores_preamble_and_empty_sections() -> None:
    md = "# Title\nintro text\n\n## One\nFirst body.\n\n## Empty\n\n## Two\nSecond\nbody."
    sections = parse_faq(md)
    assert sections == [FaqSection("One", "First body."), FaqSection("Two", "Second body.")]


def test_tokenize_stems_and_drops_stopwords() -> None:
    assert tokenize("The hours are cancelling") == tokenize("hour cancel")
    assert "the" not in tokenize("the clinic")


def test_shorten_limits_sentences() -> None:
    text = "One. Two. Three. Four."
    assert shorten(text, max_sentences=2) == "One. Two."


def test_empty_index_rejected() -> None:
    with pytest.raises(ValueError):
        FaqIndex([])


def test_search_is_fast_enough_for_a_voice_turn(index: FaqIndex) -> None:
    start = time.perf_counter()
    for _ in range(100):
        index.search("do you take delta dental insurance")
    per_query_ms = (time.perf_counter() - start) * 1000 / 100
    assert per_query_ms < 20
