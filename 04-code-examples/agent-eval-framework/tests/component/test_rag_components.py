"""Component: retriever and generator tested separately, then RAGAS 0.4 metrics (Module 5)."""

import pytest
from ragas import EvaluationDataset, SingleTurnSample

from agents.rag_agent import POLICY_DOCUMENTS, generate_answer, retrieve_context, run_rag_agent
from evaluators import heuristics as h
from evaluators.golden import load
from evaluators.ragas_suite import MockEmbeddings, MockRagasLLM, aggregate, build_dataset, diagnose, evaluate_dataset, to_sample

CASES = load("golden_rag")
DOCS = {d["id"]: d for d in POLICY_DOCUMENTS}


def test_fifteen_cases_five_per_domain():
    assert len(CASES) == 15
    assert {d: sum(c["domain"] == d for c in CASES) for d in ("hr", "it_security", "travel_expense")} == {"hr": 5, "it_security": 5, "travel_expense": 5}


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_retriever_hit_at_3(case):
    assert case["reference_context_ids"][0] in [d["id"] for d in retrieve_context(case["question"])]


def test_stopword_fix_repairs_the_flight_question():
    q = "What class can I fly on a long flight?"
    assert "travel-001" not in [d["id"] for d in retrieve_context(q)]
    assert "travel-001" in [d["id"] for d in retrieve_context(q, remove_stopwords=True)]


def test_noise_documents_only_when_asked():
    assert all(d["domain"] != "noise" for d in retrieve_context("cafeteria menu pizza", top_k=16))
    assert any(d["domain"] == "noise" for d in retrieve_context("cafeteria menu pizza", include_noise=True))


@pytest.mark.parametrize("case", [c for c in CASES if c["id"] != "RAG-TE-05"], ids=lambda c: c["id"])
def test_generator_with_perfect_context(case):
    gen = generate_answer(case["question"], [DOCS[i] for i in case["reference_context_ids"]])
    assert h.faithfulness(gen["answer"], DOCS[case["reference_context_ids"][0]]["content"]) == 1.0


def test_known_generation_failure_is_reported():
    """RAG-TE-05 is the deliberate offline generation miss Project 2 diagnoses."""
    case = next(c for c in CASES if c["id"] == "RAG-TE-05")
    r = run_rag_agent(case["question"])
    assert "don't cover" in r["answer"]
    assert diagnose(evaluate_dataset(build_dataset([to_sample(case["question"], r, case["reference"])]))[0]) == "generation"


def test_ragas_types_and_aggregate():
    s = SingleTurnSample(user_input="q", response="a", retrieved_contexts=["c"], reference="r")
    assert isinstance(EvaluationDataset(samples=[s]), EvaluationDataset)
    rows = evaluate_dataset(build_dataset([to_sample(c["question"], run_rag_agent(c["question"]), c["reference"]) for c in CASES[:5]]))
    assert aggregate(rows) == {"faithfulness": 1.0, "answer_relevancy": 1.0, "context_precision": 1.0, "context_recall": 1.0}


def test_mock_embeddings_are_normalised_and_deterministic():
    e = MockEmbeddings()
    v = e.embed_text("vacation days")
    assert abs(sum(x * x for x in v) - 1) < 1e-9 and v == e.embed_text("vacation days")
    assert isinstance(MockRagasLLM(), MockRagasLLM)


def test_diagnose_rules():
    assert diagnose({"faithfulness": 1, "answer_relevancy": 1, "context_precision": 0.2, "context_recall": 1}) == "retrieval"
    assert diagnose({"faithfulness": 0.2, "answer_relevancy": 1, "context_precision": 1, "context_recall": 1}) == "generation"
    assert diagnose({"faithfulness": 1, "answer_relevancy": 1, "context_precision": 1, "context_recall": 1}) == "ok"
