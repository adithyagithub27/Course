"""
RAGAS Evaluation Suite — RAG-specific evaluation pipeline.

Demonstrates how to evaluate RAG pipelines using the RAGAS framework.
Used in Module 05 (Project 2).
"""

import asyncio
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)


RAG_METRICS = [
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
]

RAG_THRESHOLDS = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.7,
    "context_precision": 0.7,
    "context_recall": 0.7,
}


def prepare_ragas_dataset(samples: list[dict]) -> dict:
    """
    Prepare data in RAGAS-expected format.

    Each sample should have:
    - question: str
    - answer: str
    - contexts: list[str]
    - ground_truth: str (optional, needed for context_recall)
    """
    return {
        "question": [s["question"] for s in samples],
        "answer": [s["answer"] for s in samples],
        "contexts": [s["contexts"] for s in samples],
        "ground_truth": [s.get("ground_truth", "") for s in samples],
    }


def check_thresholds(scores: dict, thresholds: dict | None = None) -> dict:
    """
    Check evaluation scores against thresholds.

    Returns dict with pass/fail per metric and overall.
    """
    if thresholds is None:
        thresholds = RAG_THRESHOLDS

    results = {}
    all_passed = True

    for metric_name, threshold in thresholds.items():
        score = scores.get(metric_name, 0)
        passed = score >= threshold
        results[metric_name] = {
            "score": score,
            "threshold": threshold,
            "passed": passed,
        }
        if not passed:
            all_passed = False

    results["overall_passed"] = all_passed
    return results
