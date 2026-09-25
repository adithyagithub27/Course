"""
Regression Tests — Golden Dataset Evaluation (Module 11)

Runs the complete golden dataset against the agent and checks
that quality scores remain above established thresholds.
This is the test that runs in CI/CD to catch regressions.
"""

import json
import pytest
from pathlib import Path

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

from agents.support_agent import run_support_agent


# -- Load Golden Dataset ------------------------------------------------------

GOLDEN_PATH = Path(__file__).parent.parent.parent / "datasets" / "golden_support.json"


def load_golden_cases() -> list[dict]:
    """Load the golden dataset."""
    if not GOLDEN_PATH.exists():
        pytest.skip(f"Golden dataset not found at {GOLDEN_PATH}")
    with open(GOLDEN_PATH) as f:
        return json.load(f)


GOLDEN_CASES = load_golden_cases()


# -- Metrics ------------------------------------------------------------------

relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
faithfulness = FaithfulnessMetric(threshold=0.8, model="gpt-4o-mini")


# -- Tests --------------------------------------------------------------------

@pytest.mark.regression
class TestGoldenDatasetRegression:
    """
    Regression tests using the golden dataset.

    These tests ensure that agent quality doesn't degrade
    when the prompt, model, tools, or code change.
    """

    @pytest.mark.parametrize(
        "case",
        GOLDEN_CASES,
        ids=[
            f"{c.get('category', 'unknown')}_{c['input'][:30]}"
            for c in GOLDEN_CASES
        ],
    )
    def test_answer_relevancy_regression(self, case):
        """Agent responses should remain relevant across golden dataset."""
        result = run_support_agent(case["input"])

        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            expected_output=case.get("expected_output"),
            context=case.get("context"),
            retrieval_context=case.get("context"),
        )

        assert_test(test_case, [relevancy])

    @pytest.mark.parametrize(
        "case",
        [c for c in GOLDEN_CASES if c.get("context")],
        ids=[
            f"faith_{c.get('category', 'unknown')}_{c['input'][:25]}"
            for c in GOLDEN_CASES
            if c.get("context")
        ],
    )
    def test_faithfulness_regression(self, case):
        """Agent responses should remain faithful to provided context."""
        result = run_support_agent(case["input"])

        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            retrieval_context=case["context"],
        )

        assert_test(test_case, [faithfulness])

    def test_overall_pass_rate_above_threshold(self):
        """Overall pass rate across the golden dataset should stay above 80%."""
        passed = 0
        total = len(GOLDEN_CASES)

        for case in GOLDEN_CASES:
            result = run_support_agent(case["input"])
            test_case = LLMTestCase(
                input=case["input"],
                actual_output=result["response"],
                expected_output=case.get("expected_output"),
                context=case.get("context"),
            )
            try:
                assert_test(test_case, [relevancy])
                passed += 1
            except AssertionError:
                pass

        pass_rate = passed / total if total > 0 else 0
        assert pass_rate >= 0.8, (
            f"Overall pass rate {pass_rate:.1%} is below the 80% threshold. "
            f"Passed: {passed}/{total}"
        )
