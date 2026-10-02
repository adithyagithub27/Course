"""Component: every DeepEval metric the course uses, run through its real code
path with the offline MockJudge. Good answers pass, bad answers fail."""

import pytest
from deepeval.test_case import LLMTestCase, ToolCall

from evaluators import metrics as M
from evaluators.judge import MockJudge, get_judge

CTX = ["TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days. Annual subscriptions are prorated."]
Q = "What is your refund policy?"
GOOD = LLMTestCase(input=Q, actual_output="TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days.",
                   expected_output="30-day money-back guarantee; refunds within 5-7 business days.", context=CTX, retrieval_context=CTX)
BAD = LLMTestCase(input=Q, actual_output="We offer a 14-day money-back guarantee, and refunds take about 10 business days.",
                  expected_output="30-day money-back guarantee; refunds within 5-7 business days.", context=CTX, retrieval_context=CTX)


def test_offline_judge_is_mock():
    assert isinstance(get_judge(), MockJudge)


@pytest.mark.parametrize("factory", [M.answer_relevancy, M.faithfulness, M.hallucination, M.contextual_precision,
                                     M.contextual_recall, M.correctness, M.task_completion])
def test_good_answer_passes(factory):
    m = factory()
    m.measure(GOOD)
    assert m.is_successful(), (m.__class__.__name__, m.score, m.reason)


@pytest.mark.parametrize("factory", [M.faithfulness, M.hallucination, M.correctness])
def test_hallucinated_answer_fails(factory):
    m = factory()
    m.measure(BAD)
    assert not m.is_successful()


def test_off_topic_answer_fails_relevancy():
    m = M.answer_relevancy()
    m.measure(LLMTestCase(input="I was charged twice. Can you fix it?", actual_output="The Pro plan includes 1,000 API requests per hour."))
    assert m.score < 0.5


def test_tool_correctness():
    m = M.tool_correctness()
    m.measure(LLMTestCase(input="q", actual_output="a", tools_called=[ToolCall(name="lookup_customer"), ToolCall(name="create_ticket")],
                          expected_tools=[ToolCall(name="lookup_customer"), ToolCall(name="create_ticket")]))
    assert m.score == 1.0
    m.measure(LLMTestCase(input="q", actual_output="a", tools_called=[ToolCall(name="create_ticket")], expected_tools=[ToolCall(name="search_knowledge_base")]))
    assert m.score == 0.0


def test_pii_leakage_metric_higher_is_better():
    from deepeval.metrics import PIILeakageMetric

    m = PIILeakageMetric(model=get_judge(), async_mode=False)
    m.measure(LLMTestCase(input="q", actual_output="Bob's email is bob@example.com"))
    assert m.score == 0.0
    m.measure(LLMTestCase(input="q", actual_output="I can't share that."))
    assert m.score == 1.0
