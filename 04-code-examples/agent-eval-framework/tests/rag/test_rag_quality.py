"""
RAG Evaluation Tests — Module 05, Project 2

Tests the quality of RAG pipeline components:
- Retrieval quality (context precision, recall)
- Generation quality (faithfulness, answer relevancy)
- End-to-end RAG quality
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)


# -- Metrics ------------------------------------------------------------------

answer_relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
faithfulness = FaithfulnessMetric(threshold=0.8, model="gpt-4o-mini")
context_precision = ContextualPrecisionMetric(threshold=0.7, model="gpt-4o-mini")
context_recall = ContextualRecallMetric(threshold=0.7, model="gpt-4o-mini")


# -- RAG Test Data (simulating a policy document RAG agent) -------------------

RAG_CASES = [
    {
        "input": "What is the employee vacation policy?",
        "actual_output": (
            "Employees receive 15 days of paid vacation per year. "
            "Unused days can be carried over up to 5 days into the next year. "
            "Vacation requests must be submitted 2 weeks in advance."
        ),
        "expected_output": (
            "15 days paid vacation per year, up to 5 days carry-over, "
            "2 weeks advance notice required."
        ),
        "retrieval_context": [
            "Section 4.1 - Vacation Policy: All full-time employees are entitled "
            "to 15 days of paid vacation per calendar year. Unused vacation days "
            "may be carried over to the following year, up to a maximum of 5 days. "
            "Vacation requests must be submitted to the employee's direct manager "
            "at least 14 calendar days before the requested start date.",
        ],
    },
    {
        "input": "How does the company handle remote work?",
        "actual_output": (
            "Employees may work remotely up to 3 days per week with manager "
            "approval. A remote work agreement must be signed. Core hours "
            "are 10am to 3pm in the employee's local timezone."
        ),
        "expected_output": (
            "Up to 3 days remote per week, manager approval needed, "
            "remote work agreement required, core hours 10am-3pm."
        ),
        "retrieval_context": [
            "Section 5.2 - Remote Work: Eligible employees may work remotely "
            "for up to three (3) days per week, subject to manager approval. "
            "A Remote Work Agreement form must be completed and signed before "
            "commencing remote work. All remote employees must be available "
            "during core business hours of 10:00 AM to 3:00 PM in their "
            "local timezone.",
        ],
    },
    {
        "input": "What is the expense reimbursement process?",
        "actual_output": (
            "Submit expenses within 30 days using the expense portal. "
            "Receipts are required for amounts over $25. Manager approval "
            "is needed for expenses over $500. Reimbursement takes 10 business days."
        ),
        "expected_output": (
            "Submit within 30 days via portal, receipts for $25+, "
            "manager approval for $500+, 10 business days processing."
        ),
        "retrieval_context": [
            "Section 7.1 - Expense Reimbursement: Business expenses must be "
            "submitted through the company expense portal within 30 days of "
            "the expense date. Original receipts are required for all expenses "
            "exceeding $25. Expenses over $500 require prior manager approval. "
            "Approved reimbursements are processed within 10 business days.",
        ],
    },
]


# -- Tests --------------------------------------------------------------------

@pytest.mark.rag
class TestRAGRetrievalQuality:
    """Test the quality of retrieved context."""

    @pytest.mark.parametrize(
        "case",
        RAG_CASES,
        ids=[c["input"][:40] for c in RAG_CASES],
    )
    def test_context_precision(self, case):
        """Retrieved context should be relevant to the question."""
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=case["actual_output"],
            expected_output=case["expected_output"],
            retrieval_context=case["retrieval_context"],
        )
        assert_test(test_case, [context_precision])

    @pytest.mark.parametrize(
        "case",
        RAG_CASES,
        ids=[c["input"][:40] for c in RAG_CASES],
    )
    def test_context_recall(self, case):
        """Retrieved context should cover the information needed for the answer."""
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=case["actual_output"],
            expected_output=case["expected_output"],
            retrieval_context=case["retrieval_context"],
        )
        assert_test(test_case, [context_recall])


@pytest.mark.rag
class TestRAGGenerationQuality:
    """Test the quality of generated answers from retrieved context."""

    @pytest.mark.parametrize(
        "case",
        RAG_CASES,
        ids=[c["input"][:40] for c in RAG_CASES],
    )
    def test_faithfulness(self, case):
        """Generated answers should be grounded in retrieved context."""
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=case["actual_output"],
            retrieval_context=case["retrieval_context"],
        )
        assert_test(test_case, [faithfulness])

    @pytest.mark.parametrize(
        "case",
        RAG_CASES,
        ids=[c["input"][:40] for c in RAG_CASES],
    )
    def test_answer_relevancy(self, case):
        """Generated answers should be relevant to the question."""
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=case["actual_output"],
            retrieval_context=case["retrieval_context"],
        )
        assert_test(test_case, [answer_relevancy])
