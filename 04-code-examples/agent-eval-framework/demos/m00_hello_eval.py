"""Lecture 0.2 - Environment smoke test: the smallest possible DeepEval test.

    uv run deepeval test run demos/m00_hello_eval.py     # pytest-style run
    uv run python demos/m00_hello_eval.py                # plain run
"""
from _common import banner

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from agents.support_agent import run_support_agent
from evaluators.metrics import answer_relevancy


def test_hello_eval():
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    assert_test(LLMTestCase(input=question, actual_output=result["response"]), [answer_relevancy()])


if __name__ == "__main__":
    banner("Lecture 0.2 - hello eval")
    test_hello_eval()
    print("hello eval PASSED")
