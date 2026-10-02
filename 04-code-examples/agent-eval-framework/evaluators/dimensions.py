"""
The five quality dimensions (decision T3), scored for one agent response.

    correctness   is the answer right?                       GEval correctness vs expected_output
    faithfulness  is every claim backed by context/tools?    FaithfulnessMetric
    relevance     does it answer what was asked?             AnswerRelevancyMetric
    safety        does it avoid leaks and harmful actions?   GEval PII safety + injection resistance
    reliability   does it behave the same every time?        share of N runs with the same tools and a passing answer

Used by the Module 2 scorecard demo and the Module 13 leadership scorecard.
"""

from __future__ import annotations

from collections.abc import Callable

from deepeval.test_case import LLMTestCase

from config.thresholds import DIMENSIONS
from evaluators import metrics as M
from evaluators.custom_metrics import injection_resistance, pii_safety


def _score(metric, tc: LLMTestCase) -> float:
    metric.measure(tc)
    return round(float(metric.score), 2)


def score_response(question: str, answer: str, expected: str, context: list[str]) -> dict[str, float]:
    """Score one response on correctness, faithfulness, relevance and safety."""
    tc = LLMTestCase(input=question, actual_output=answer, expected_output=expected, retrieval_context=context, context=context)
    return {
        "correctness": _score(M.correctness(), tc),
        "faithfulness": _score(M.faithfulness(), tc),
        "relevance": _score(M.answer_relevancy(), tc),
        "safety": min(_score(pii_safety(), tc), _score(injection_resistance(), tc)),
    }


def reliability(agent_fn: Callable[[str], dict], question: str, runs: int = 5) -> float:
    """Share of runs whose tool sequence matches the most common one."""
    seqs = [tuple(t["tool"] for t in agent_fn(question)["tool_calls"]) for _ in range(runs)]
    most = max(set(seqs), key=seqs.count)
    return round(seqs.count(most) / runs, 2)


def scorecard(question: str, answer: str, expected: str, context: list[str], reliability_score: float) -> dict[str, float]:
    s = score_response(question, answer, expected, context)
    s["reliability"] = reliability_score
    return {d: s[d] for d in DIMENSIONS}
