"""Lecture 4.1 - Metric comparison: five responses, four metrics. A response
can be relevant and still unfaithful, or faithful and still wrong.

    uv run python demos/m04_metric_comparison.py
"""
from _common import banner, table

from deepeval.test_case import LLMTestCase
from evaluators import metrics as M

banner("Lecture 4.1 - metric comparison")
q = "What are the API rate limits for the Pro plan?"
ctx = ["TechCorp API documentation is available at docs.techcorp.com. API keys can be generated in Settings > Developer > API Keys. Rate limits: Basic (100/hr), Pro (1000/hr), Enterprise (unlimited)."]
exp = "The Pro plan allows 1,000 API requests per hour."
responses = {
    "1 correct": "The Pro plan allows 1000 API requests per hour. You can create keys in Settings > Developer > API Keys.",
    "2 wrong number": "The Pro plan allows 500 API requests per hour.",
    "3 off-topic": "Our refund policy gives you 30 days to request your money back.",
    "4 vague": "Rate limits depend on your plan. Check the documentation.",
    "5 extra claim": "The Pro plan allows 1000 API requests per hour, and bursts of 5000 per minute are free.",
}
rows = []
for name, out in responses.items():
    tc = LLMTestCase(input=q, actual_output=out, expected_output=exp, context=ctx, retrieval_context=ctx)
    row = {"response": name}
    for label, metric in (("relevancy", M.answer_relevancy()), ("faithfulness", M.faithfulness()),
                          ("hallucination*", M.hallucination()), ("correctness", M.correctness())):
        metric.measure(tc)
        row[label] = f"{metric.score:.2f}"
    rows.append(row)
table(rows)
print("\n*DeepEval 4.2 HallucinationMetric: share of contexts the answer agrees with (higher is better).")
