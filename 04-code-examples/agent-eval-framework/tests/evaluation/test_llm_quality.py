"""
LLM Quality Evaluation Tests — Module 04

Evaluates the quality of LLM outputs using standard metrics:
answer relevancy, faithfulness, hallucination, and custom G-Eval.
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
)

from agents.support_agent import run_support_agent
from evaluators.custom_metrics import (
    policy_compliance_metric,
    tone_metric,
)


# -- Metrics ------------------------------------------------------------------

relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
faithfulness = FaithfulnessMetric(threshold=0.8, model="gpt-4o-mini")
hallucination = HallucinationMetric(threshold=0.3, model="gpt-4o-mini")


# -- Test Data ----------------------------------------------------------------

QUALITY_CASES = [
    {
        "input": "What are your pricing plans?",
        "context": [
            "TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), "
            "and Enterprise (custom pricing). All plans include core features. "
            "Pro adds priority support and advanced analytics."
        ],
    },
    {
        "input": "Can I get a refund after 45 days?",
        "context": [
            "TechCorp offers a 30-day money-back guarantee on all plans. "
            "Refunds are processed within 5-7 business days. "
            "Annual subscriptions are prorated."
        ],
    },
    {
        "input": "What API rate limits does the Basic plan have?",
        "context": [
            "Rate limits: Basic (100/hr), Pro (1000/hr), Enterprise (unlimited). "
            "API keys can be generated in Settings > Developer > API Keys."
        ],
    },
]


# -- Tests --------------------------------------------------------------------

@pytest.mark.evaluation
class TestLLMOutputQuality:
    """Test the quality of agent LLM outputs."""

    @pytest.mark.parametrize(
        "case",
        QUALITY_CASES,
        ids=[c["input"][:40] for c in QUALITY_CASES],
    )
    def test_answer_relevancy(self, case):
        """Responses should be relevant to the question asked."""
        result = run_support_agent(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            retrieval_context=case["context"],
        )
        assert_test(test_case, [relevancy])

    @pytest.mark.parametrize(
        "case",
        QUALITY_CASES,
        ids=[c["input"][:40] for c in QUALITY_CASES],
    )
    def test_faithfulness(self, case):
        """Responses should be grounded in the provided context."""
        result = run_support_agent(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            retrieval_context=case["context"],
        )
        assert_test(test_case, [faithfulness])

    @pytest.mark.parametrize(
        "case",
        QUALITY_CASES,
        ids=[c["input"][:40] for c in QUALITY_CASES],
    )
    def test_no_hallucination(self, case):
        """Responses should not contain hallucinated information."""
        result = run_support_agent(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            context=case["context"],
        )
        assert_test(test_case, [hallucination])


@pytest.mark.evaluation
class TestCustomMetrics:
    """Test agent outputs against custom business metrics."""

    def test_policy_compliance(self):
        """Refund responses should comply with TechCorp policy."""
        result = run_support_agent("Can I get a refund after 45 days?")
        test_case = LLMTestCase(
            input="Can I get a refund after 45 days?",
            actual_output=result["response"],
            context=[
                "TechCorp offers a 30-day money-back guarantee on all plans. "
                "Refunds are processed within 5-7 business days."
            ],
        )
        assert_test(test_case, [policy_compliance_metric])

    def test_professional_tone_with_angry_customer(self):
        """Agent should maintain professional tone with angry customers."""
        result = run_support_agent(
            "This is ridiculous! Your product is garbage and I want "
            "my money back RIGHT NOW. I can't believe I wasted money on this!"
        )
        test_case = LLMTestCase(
            input="Angry customer demanding refund",
            actual_output=result["response"],
        )
        assert_test(test_case, [tone_metric])
