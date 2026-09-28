"""Tiny FAQ retriever over ``data/faq.md`` (RAG for voice, no dependencies).

Lectures: 7.1 (RAG for voice), 7.2 (FAQ lookup tool), 7.3 (when to scale up).

The FAQ is split into sections on ``##`` headings. Retrieval uses a small
BM25 implementation ("BM25-lite") with a bonus for words that appear in the
section title. For a clinic FAQ with a few dozen sections this runs in well
under a millisecond, which matters when the lookup sits inside a voice turn.

Answers are trimmed to a few sentences so the agent can speak them.

Usage::

    from maple.knowledge import FaqIndex

    index = FaqIndex.from_default()
    hits = index.search("do you take delta dental", k=2)
    hits[0].title    # "Insurance accepted"
    hits[0].answer   # first sentences of the section
"""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

STOPWORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "can",
        "could",
        "do",
        "does",
        "for",
        "from",
        "have",
        "how",
        "i",
        "if",
        "in",
        "is",
        "it",
        "its",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "please",
        "should",
        "so",
        "that",
        "the",
        "their",
        "them",
        "there",
        "they",
        "this",
        "to",
        "up",
        "us",
        "was",
        "we",
        "what",
        "when",
        "where",
        "which",
        "who",
        "will",
        "with",
        "would",
        "you",
        "your",
        "yours",
        "can't",
        "don't",
        "i'm",
        "tell",
        "know",
        "want",
        "need",
        "get",
        "about",
        "any",
        "some",
        "just",
        "like",
        "also",
        "has",
        "had",
        "got",
        "see",
        "take",
        "what's",
        "where's",
        "who's",
    ]
)

_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class FaqSection:
    """One ``##`` section of the FAQ."""

    title: str
    body: str


@dataclass(frozen=True)
class SearchResult:
    """A ranked FAQ hit."""

    title: str
    answer: str
    score: float


def _stem(token: str) -> str:
    """Very small suffix stripper so 'hours' matches 'hour' and 'cancelling' matches 'cancel'.

    It is intentionally crude: the same function runs on queries and documents,
    so consistency matters more than linguistic accuracy.
    """
    for suffix in ("ations", "ation", "ings", "ing", "ies", "es", "ed", "s"):
        if len(token) > len(suffix) + 2 and token.endswith(suffix):
            token = token[: -len(suffix)] + ("y" if suffix == "ies" else "")
            break
    if len(token) > 4 and token.endswith("e"):
        token = token[:-1]  # price -> pric, matching pricing -> pric
    if len(token) > 4 and token[-1] == token[-2] and token[-1] not in "aeiou":
        token = token[:-1]  # cancell -> cancel
    return token


# Query-side expansions for how callers actually phrase things.
SYNONYMS: dict[str, tuple[str, ...]] = {
    "cost": ("price",),
    "much": ("price",),
    "expensive": ("price",),
    "cheap": ("price",),
    "afford": ("payment", "plan"),
    "pay": ("payment",),
    "monthly": ("payment", "plan"),
    "installments": ("payment", "plan"),
    "financing": ("payment", "plan"),
    "location": ("address",),
    "located": ("address",),
    "directions": ("address",),
    "open": ("hours",),
    "close": ("hours",),
    "closed": ("hours",),
    "kid": ("children",),
    "kids": ("children",),
    "child": ("children",),
    "son": ("children",),
    "daughter": ("children",),
    "wheelchair": ("accessible",),
    "disabled": ("accessible",),
    "espanol": ("spanish",),
    "sick": ("illness",),
    "covid": ("illness",),
    "flu": ("illness",),
    "emergency": ("emergencies",),
    "hurts": ("pain",),
    "doctor": ("dentists",),
    "dentist": ("dentists",),
}


def expand_query(text: str) -> list[str]:
    """Tokenize a caller question and add synonym tokens."""
    raw = _TOKEN.findall(text.lower())
    tokens = [_stem(t) for t in raw if len(t) > 1 and t not in STOPWORDS]
    for word in raw:
        for extra in SYNONYMS.get(word, ()):
            tokens.append(_stem(extra))
    return tokens


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords and stem."""
    return [_stem(t) for t in _TOKEN.findall(text.lower()) if len(t) > 1 and t not in STOPWORDS]


def parse_faq(markdown: str) -> list[FaqSection]:
    """Split FAQ markdown into sections on ``## `` headings.

    Text before the first ``##`` heading (the document title and intro) is ignored.
    """
    sections: list[FaqSection] = []
    title: str | None = None
    lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if title is not None:
                sections.append(FaqSection(title, " ".join(" ".join(lines).split())))
            title, lines = line[3:].strip(), []
        elif title is not None:
            lines.append(line.strip())
    if title is not None:
        sections.append(FaqSection(title, " ".join(" ".join(lines).split())))
    return [s for s in sections if s.body]


def shorten(text: str, max_sentences: int = 3, max_chars: int = 400) -> str:
    """Keep the first few sentences so the answer is short enough to speak."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    out: list[str] = []
    for sentence in sentences[:max_sentences]:
        if out and len(" ".join([*out, sentence])) > max_chars:
            break
        out.append(sentence)
    return " ".join(out)


class FaqIndex:
    """BM25-lite index over FAQ sections.

    Args:
        sections: Parsed FAQ sections.
        k1: BM25 term-frequency saturation.
        b: BM25 length normalisation.
        title_boost: Extra weight for query terms that appear in the title.
    """

    def __init__(
        self,
        sections: Iterable[FaqSection],
        *,
        k1: float = 1.5,
        b: float = 0.75,
        title_boost: float = 1.5,
    ) -> None:
        self.sections = list(sections)
        if not self.sections:
            raise ValueError("FaqIndex needs at least one section")
        self.k1 = k1
        self.b = b
        self.title_boost = title_boost
        self._doc_tokens = [tokenize(f"{s.title} {s.body}") for s in self.sections]
        self._title_tokens = [set(tokenize(s.title)) for s in self.sections]
        self._tf = [Counter(tokens) for tokens in self._doc_tokens]
        self._avg_len = sum(len(t) for t in self._doc_tokens) / len(self._doc_tokens)
        df: Counter[str] = Counter()
        for tokens in self._doc_tokens:
            df.update(set(tokens))
        n = len(self.sections)
        self._idf = {term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()}

    @classmethod
    def from_markdown(cls, markdown: str, **kwargs: float) -> FaqIndex:
        """Build an index from FAQ markdown text."""
        return cls(parse_faq(markdown), **kwargs)

    @classmethod
    def from_file(cls, path: str | Path, **kwargs: float) -> FaqIndex:
        """Build an index from a markdown file on disk."""
        return cls.from_markdown(Path(path).read_text(encoding="utf-8"), **kwargs)

    @classmethod
    def from_default(cls) -> FaqIndex:
        """Build an index from the packaged ``maple/data/faq.md``."""
        text = resources.files("maple").joinpath("data/faq.md").read_text(encoding="utf-8")
        return cls.from_markdown(text)

    def score(self, query: str, index: int) -> float:
        """BM25 score of section ``index`` for ``query`` (0.0 when nothing matches)."""
        terms = expand_query(query)
        tf = self._tf[index]
        length = len(self._doc_tokens[index])
        total = 0.0
        for term in set(terms):
            freq = tf.get(term, 0)
            if freq == 0:
                continue
            idf = self._idf.get(term, 0.0)
            denom = freq + self.k1 * (1 - self.b + self.b * length / self._avg_len)
            weight = idf * (freq * (self.k1 + 1)) / denom
            if term in self._title_tokens[index]:
                weight *= self.title_boost
            total += weight
        return total

    def search(
        self,
        query: str,
        k: int = 2,
        *,
        min_score: float = 1.5,
        max_sentences: int = 3,
    ) -> list[SearchResult]:
        """Return up to ``k`` best sections for ``query``.

        Args:
            query: The caller's question in plain words.
            k: Maximum number of results.
            min_score: Hits scoring below this are dropped, so off-topic
                questions return an empty list (and the agent says "I'm not sure").
            max_sentences: Sentences kept in each answer.
        """
        scored = [(self.score(query, i), i) for i in range(len(self.sections))]
        scored = [(s, i) for s, i in scored if s >= min_score]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [
            SearchResult(
                title=self.sections[i].title,
                answer=shorten(self.sections[i].body, max_sentences=max_sentences),
                score=round(s, 4),
            )
            for s, i in scored[:k]
        ]

    def answer(self, query: str, k: int = 2) -> str:
        """Return a single speakable string for a tool response.

        Returns ``"NO_MATCH"`` when nothing relevant is found so the prompt can
        instruct the model to say it does not know.
        """
        hits = self.search(query, k=k)
        if not hits:
            return "NO_MATCH"
        return "\n".join(f"{h.title}: {h.answer}" for h in hits)
