"""Lecture 3.1 - Meet DeepEval: your first agent evaluation (pytest for AI).

    uv run deepeval test run demos/m03_first_eval.py
    uv run python demos/m03_first_eval.py
"""
from _common import banner

from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from agents.support_agent import run_support_agent
from evaluators.judge import get_judge


def test_pricing_answer_is_relevant():
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    test_case = LLMTestCase(input=question, actual_output=result["response"])
    metric = AnswerRelevancyMetric(threshold=0.7, model=get_judge())
    assert_test(test_case, [metric])


if __name__ == "__main__":
    banner("Lecture 3.1 - first eval")
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    metric = AnswerRelevancyMetric(threshold=0.7, model=get_judge(), async_mode=False)
    metric.measure(LLMTestCase(input=question, actual_output=result["response"]))
    print(f"Input : {question}\nOutput: {result['response']}")
    print(f"AnswerRelevancy = {metric.score:.2f} (threshold 0.7) -> {'PASS' if metric.is_successful() else 'FAIL'}")
    print(f"Reason: {metric.reason}")
