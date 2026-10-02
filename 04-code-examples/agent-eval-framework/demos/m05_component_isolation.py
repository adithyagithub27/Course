"""Lecture 5.3 - Evaluate retrieval and generation separately: test the
retriever alone (hit rate), then the generator with perfect context.

    uv run python demos/m05_component_isolation.py
"""
from _common import banner, table

from agents.rag_agent import POLICY_DOCUMENTS, generate_answer, retrieve_context
from evaluators import heuristics as h
from evaluators.golden import load

banner("Lecture 5.3 - component isolation", ["openai", "ragas"])
docs = {d["id"]: d for d in POLICY_DOCUMENTS}
rows = []
for c in load("golden_rag")[10:]:
    got = [d["id"] for d in retrieve_context(c["question"])]
    hit = c["reference_context_ids"][0] in got
    gen = generate_answer(c["question"], [docs[i] for i in c["reference_context_ids"]])  # perfect context
    correct = h.correctness(gen["answer"], c["reference"])
    rows.append({"id": c["id"], "retriever_hit@3": "yes" if hit else "NO", "rank": (got.index(c["reference_context_ids"][0]) + 1) if hit else "-",
                 "generator_correct(perfect ctx)": f"{correct:.2f}", "fix": "generator" if hit and correct < 0.7 else ("retriever" if not hit else "-")})
table(rows, width=32)
print("\nRetriever misses -> fix chunking/ranking. Generator wrong with perfect context -> fix the prompt or model.")
