"""Lecture 5.1 - RAG failure dissection: a wrong answer traced to retrieval,
then fixed in the retriever (not the prompt).

    uv run python demos/m05_rag_failure_dissection.py
"""
from _common import banner

from agents.rag_agent import run_rag_agent
from evaluators.ragas_suite import build_dataset, diagnose, evaluate_dataset, to_sample

banner("Lecture 5.1 - RAG failure dissection", ["openai", "ragas"])
q = "What class can I fly on a long flight?"
ref = "Economy class is required for flights under 6 hours; premium economy is allowed for flights of 6 hours or more."
for label, fix in (("BEFORE: naive keyword retriever", False), ("AFTER: stop words removed", True)):
    r = run_rag_agent(q, remove_stopwords=fix)
    scores = evaluate_dataset(build_dataset([to_sample(q, r, ref)]))[0]
    print(f"\n{label}")
    print(f"  retrieved: {r['retrieved_ids']}  (the answer lives in travel-001)")
    print(f"  answer   : {r['answer']}")
    print(f"  RAGAS    : {scores}")
    print(f"  diagnosis: {diagnose(scores)}")
