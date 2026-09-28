"""BM25-lite retriever over ``src/northwind/data/kb/*.md`` (Section 5.3).

Deterministic and dependency-free. Each article has YAML-ish front matter
(id, title, tags) which we parse by hand; tags are indexed with the body.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[1] / "src" / "northwind" / "data" / "kb"

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = frozenset(
    "a an and are as at be by for from has have how i in is it its my of on or that the this to "
    "was we what when where which who will with you your can do does did our about into if".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase alnum tokens, stopwords removed, naive plural stemming."""
    out = []
    for t in _TOKEN.findall(text.lower()):
        if t in _STOP or len(t) < 2:
            continue
        if len(t) > 4 and t.endswith("ies"):
            t = t[:-3] + "y"
        elif len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


@dataclass
class Article:
    doc_id: str
    title: str
    tags: list[str]
    body: str
    path: str = ""
    tokens: list[str] = field(default_factory=list)
    paragraphs: list[tuple[str, frozenset[str]]] = field(default_factory=list)

    @property
    def text(self) -> str:
        return f"# {self.title}\n\n{self.body}"


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    title: str
    score: float
    snippet: str

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.doc_id,
            "title": self.title,
            "score": round(self.score, 4),
            "snippet": self.snippet,
        }


def _parse_front_matter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return {}, raw
    meta: dict[str, str] = {}
    for line in raw[3:end].strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    body = raw[end + 4 :].lstrip("\n")
    return meta, body


def _parse_tags(value: str) -> list[str]:
    value = value.strip().strip("[]")
    return [t.strip().strip("'\"") for t in value.split(",") if t.strip()]


class KnowledgeBase:
    """BM25 (k1=1.5, b=0.75) over article title + tags + body."""

    def __init__(self, articles: list[Article], *, k1: float = 1.5, b: float = 0.75) -> None:
        self.articles = articles
        self.k1 = k1
        self.b = b
        self._df: Counter[str] = Counter()
        self._tf: list[Counter[str]] = []
        for a in articles:
            a.tokens = tokenize(f"{a.title} {a.title} {' '.join(a.tags)} {a.body}")
            a.paragraphs = [
                (p.strip(), frozenset(tokenize(p))) for p in a.body.split("\n\n") if p.strip()
            ]
            tf = Counter(a.tokens)
            self._tf.append(tf)
            self._df.update(tf.keys())
        self._avgdl = (sum(len(a.tokens) for a in articles) / len(articles)) if articles else 0.0

    @classmethod
    def load(cls, directory: str | Path = KB_DIR) -> KnowledgeBase:
        arts: list[Article] = []
        for p in sorted(Path(directory).glob("*.md")):
            meta, body = _parse_front_matter(p.read_text(encoding="utf-8"))
            body = re.sub(r"^# .*\n", "", body, count=1).strip()  # title repeated in body
            arts.append(
                Article(
                    doc_id=meta.get("id", p.stem),
                    title=meta.get("title", p.stem.replace("-", " ").title()),
                    tags=_parse_tags(meta.get("tags", "")),
                    body=body,
                    path=str(p),
                )
            )
        return cls(arts)

    def __len__(self) -> int:
        return len(self.articles)

    def get(self, doc_id: str) -> Article | None:
        return next((a for a in self.articles if a.doc_id == doc_id), None)

    def _idf(self, term: str) -> float:
        n = len(self.articles)
        df = self._df.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def score(self, query_tokens: list[str], idx: int) -> float:
        tf = self._tf[idx]
        dl = len(self.articles[idx].tokens)
        s = 0.0
        for q in query_tokens:
            f = tf.get(q)
            if not f:
                continue
            denom = f + self.k1 * (1 - self.b + self.b * dl / (self._avgdl or 1))
            s += self._idf(q) * f * (self.k1 + 1) / denom
        return s

    def search(self, query: str, top_k: int = 4, *, min_score: float = 0.5) -> list[SearchHit]:
        q = tokenize(query)
        if not q or not self.articles:
            return []
        scored = [(self.score(q, i), i) for i in range(len(self.articles))]
        scored.sort(key=lambda x: (-x[0], self.articles[x[1]].doc_id))
        hits = []
        for s, i in scored[: max(0, top_k)]:
            if s < min_score:
                break
            a = self.articles[i]
            hits.append(SearchHit(a.doc_id, a.title, s, self._snippet(a, q)))
        return hits

    def chunk(self, doc_id: str, q: list[str] | None = None, width: int = 2400) -> str:
        """The passage handed to the model: up to ``width`` chars around the best paragraph."""
        a = self.get(doc_id)
        if a is None:
            return ""
        text = a.text
        if len(text) <= width:
            return text
        best = self._snippet(a, q or [], width=200)
        idx = max(text.find(best[:40]), 0)
        start = max(0, idx - width // 3)
        return text[start : start + width].strip()

    @staticmethod
    def _snippet(article: Article, q: list[str], width: int = 320) -> str:
        paras = article.paragraphs
        best, best_n = paras[0][0] if paras else "", -1
        qset = set(q)
        for p, toks in paras:
            n = len(toks & qset)
            if n > best_n:
                best, best_n = p, n
        best = re.sub(r"\s+", " ", best)
        return best if len(best) <= width else best[: width - 1].rstrip() + "…"


_KB: KnowledgeBase | None = None


def get_kb() -> KnowledgeBase:
    global _KB
    if _KB is None:
        _KB = KnowledgeBase.load()
    return _KB
