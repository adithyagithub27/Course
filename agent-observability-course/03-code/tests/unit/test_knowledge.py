import pytest

from app.knowledge import KB_DIR, KnowledgeBase, get_kb, tokenize


def test_kb_loads_all_articles():
    kb = get_kb()
    assert len(kb) >= 12
    ids = [a.doc_id for a in kb.articles]
    assert len(set(ids)) == len(ids) and all(i.startswith("KB-") for i in ids)
    assert all(a.title and a.tags and len(a.body) > 800 for a in kb.articles)


@pytest.mark.parametrize(
    "query,doc",
    [
        ("vpn gateway unreachable", "KB-001"),
        ("reset my password locked out", "KB-002"),
        ("laptop replacement asset tag", "KB-003"),
        ("annual leave carry over", "KB-004"),
        ("hotel limit expenses", "KB-005"),
        ("phishing email report", "KB-006"),
        ("new joiner first day", "KB-007"),
        ("payroll payslip date", "KB-008"),
        ("work from abroad hybrid", "KB-009"),
        ("tableau licence", "KB-010"),
        ("shipment exception customs", "KB-011"),
        ("ticket priority sla", "KB-012"),
        ("pension contribution bike lease", "KB-013"),
        ("forklift licence near miss", "KB-014"),
    ],
)
def test_top_hit_is_right_article(query, doc):
    assert get_kb().search(query, top_k=1)[0].doc_id == doc


def test_search_respects_top_k_and_min_score():
    kb = get_kb()
    assert len(kb.search("leave", top_k=3)) <= 3
    assert kb.search("xyzzy quux", top_k=4) == []
    assert kb.search("", top_k=4) == []
    assert len(kb.search("leave", top_k=20, min_score=0.0)) == len(kb)


def test_tokenize_stems_and_drops_stopwords():
    assert tokenize("The policies of the laptops") == ["policy", "laptop"]


def test_snippet_and_chunk():
    kb = get_kb()
    hit = kb.search("hotel limit")[0]
    assert "160" in hit.snippet and len(hit.snippet) <= 330
    chunk = kb.chunk(hit.doc_id, tokenize("hotel limit"))
    assert 800 < len(chunk) <= 2400 and kb.chunk("nope") == ""


def test_empty_kb_dir(tmp_path):
    kb = KnowledgeBase.load(tmp_path)
    assert len(kb) == 0 and kb.search("anything") == []


def test_kb_dir_exists():
    assert KB_DIR.exists() and any(KB_DIR.glob("*.md"))
