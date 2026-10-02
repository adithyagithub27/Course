"""Lecture 5.2 - RAGAS metrics live: five policy questions, four metrics.

    uv run python demos/m05_ragas_metrics.py
"""
from _common import banner, table

from agents.rag_agent import run_rag_agent
from evaluators.golden import load
from evaluators.ragas_suite import aggregate, build_dataset, evaluate_dataset, to_sample

banner("Lecture 5.2 - RAGAS metrics", ["openai", "ragas"])
cases = [c for c in load("golden_rag") if c["id"] in ("RAG-HR-01", "RAG-HR-04", "RAG-IT-03", "RAG-TE-02", "RAG-TE-05")]
dataset = build_dataset([to_sample(c["question"], run_rag_agent(c["question"]), c["reference"]) for c in cases])
print(f"EvaluationDataset with {len(dataset.samples)} SingleTurnSamples (user_input, response, retrieved_contexts, reference)\n")
rows = evaluate_dataset(dataset)
table([{"id": c["id"], **r} for c, r in zip(cases, rows, strict=True)])
print(f"\nAggregate: {aggregate(rows)}")
