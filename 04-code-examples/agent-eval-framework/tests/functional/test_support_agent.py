"""
Functional Tests — Customer Support Agent (Module 03, Project 1)

These tests evaluate whether the agent correctly completes its tasks:
answering questions, looking up customers, creating tickets, and escalating.
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    TaskCompletionMetric,
    GEval,
)
from deepeval.test_case import LLMTestCaseParams

from agents.support_agent import run_support_agent


# -- Metrics ------------------------------------------------------------------

relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")

correctness = GEval(
    name="Answer Correctness",
    criteria=(
        "The agent's response is factually correct based on the provided "
        "context (TechCorp knowledge base). Deduct for: wrong prices, "
        "wrong plan features, or fabricated information."
    ),
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.EXPECTED_OUTPUT,
    ],
    threshold=0.7,
    model="gpt-4o-mini",
)


# -- Test Data ----------------------------------------------------------------

GOLDEN_CASES = [
    {
        "input": "What are your pricing plans?",
        "expected": "Basic ($9.99/mo), Pro ($29.99/mo), and Enterprise (custom pricing)",
        "context": [
            "TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), "
            "and Enterprise (custom pricing). All plans include core features."
        ],
    },
    {
        "input": "What is your refund policy?",
        "expected": "30-day money-back guarantee, refunds processed within 5-7 business days",
        "context": [
            "TechCorp offers a 30-day money-back guarantee on all plans. "
            "Refunds are processed within 5-7 business days."
        ],
    },
    {
        "input": "How do I reset my password?",
        "expected": "Go to Settings > Security > Reset Password",
        "context": [
            "To reset your password: Go to Settings > Security > Reset Password. "
            "You'll receive a verification email."
        ],
    },
]


# -- Tests --------------------------------------------------------------------

@pytest.mark.functional
class TestSupportAgentFunctional:
    """Functional tests for the customer support agent."""

    @pytest.mark.parametrize(
        "case",
        GOLDEN_CASES,
        ids=[c["input"][:40] for c in GOLDEN_CASES],
    )
    def test_answer_relevancy(self, case):
        """Agent responses should be relevant to the user's question."""
        result = run_support_agent(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            expected_output=case["expected"],
            context=case["context"],
        )
        assert_test(test_case, [relevancy])

    @pytest.mark.parametrize(
        "case",
        GOLDEN_CASES,
        ids=[c["input"][:40] for c in GOLDEN_CASES],
    )
    def test_answer_correctness(self, case):
        """Agent responses should be factually correct."""
        result = run_support_agent(case["input"])
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=result["response"],
            expected_output=case["expected"],
            context=case["context"],
        )
        assert_test(test_case, [correctness])

    def test_unknown_question_handled_gracefully(self):
        """Agent should handle questions outside its knowledge gracefully."""
        result = run_support_agent(
            "What is the meaning of life?"
        )
        assert result["response"], "Agent should return a non-empty response"
        # Agent should not hallucinate an answer about TechCorp
        test_case = LLMTestCase(
            input="What is the meaning of life?",
            actual_output=result["response"],
        )
        assert_test(test_case, [relevancy])

    def test_tool_usage_for_customer_lookup(self):
        """Agent should use lookup_customer tool when asked about an account."""
        result = run_support_agent(
            "Can you check the account for alice@example.com?"
        )
        tool_names = [tc["tool"] for tc in result["tool_calls"]]
        assert "lookup_customer" in tool_names, (
            f"Expected lookup_customer tool to be called. "
            f"Tools used: {tool_names}"
        )

    def test_escalation_for_sensitive_request(self):
        """Agent should escalate sensitive requests to a human."""
        result = run_support_agent(
            "I want to file a legal complaint about your service. "
            "I've been overcharged for 6 months and I'm contacting my lawyer."
        )
        tool_names = [tc["tool"] for tc in result["tool_calls"]]
        # Agent should either escalate or at least not dismiss the concern
        assert (
            "escalate_to_human" in tool_names
            or "legal" in result["response"].lower()
            or "escalat" in result["response"].lower()
        ), "Sensitive requests should trigger escalation or acknowledgment"
