"""
Standard DeepEval metrics, wired to the course judge and thresholds.

    from evaluators.metrics import answer_relevancy, faithfulness, correctness
    assert_test(test_case, [answer_relevancy(), faithfulness()])

Every factory uses ``get_judge()``: gpt-4.1 live, the deterministic MockJudge
offline. Thresholds come from config/eval_config.yaml. ``async_mode=False``
keeps runs sequential and repeatable on screen.
"""

from __future__ import annotations

from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
    GEval,
    HallucinationMetric,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.test_case import SingleTurnParams

from config.thresholds import load_thresholds
from evaluators.judge import get_judge

T = load_thresholds()


def answer_relevancy(threshold: float | None = None) -> AnswerRelevancyMetric:
    return AnswerRelevancyMetric(threshold=threshold or T["answer_relevancy"], model=get_judge(), async_mode=False)


def faithfulness(threshold: float | None = None) -> FaithfulnessMetric:
    return FaithfulnessMetric(threshold=threshold or T["faithfulness"], model=get_judge(), async_mode=False)


def hallucination(threshold: float | None = None) -> HallucinationMetric:
    return HallucinationMetric(threshold=threshold or T["hallucination"], model=get_judge(), async_mode=False)


def contextual_precision(threshold: float | None = None) -> ContextualPrecisionMetric:
    return ContextualPrecisionMetric(threshold=threshold or T["context_precision"], model=get_judge(), async_mode=False)


def contextual_recall(threshold: float | None = None) -> ContextualRecallMetric:
    return ContextualRecallMetric(threshold=threshold or T["context_recall"], model=get_judge(), async_mode=False)


def task_completion(threshold: float | None = None) -> TaskCompletionMetric:
    return TaskCompletionMetric(threshold=threshold or T["task_completion"], model=get_judge(), async_mode=False)


def tool_correctness(threshold: float | None = None) -> ToolCorrectnessMetric:
    """Compares tools_called with expected_tools by name. DeepEval 4 still needs a judge
    model object (used only when you pass available_tools for an LLM tool-selection score)."""
    return ToolCorrectnessMetric(threshold=threshold or T["tool_correctness"], model=get_judge(), async_mode=False)


def correctness(threshold: float | None = None) -> GEval:
    """The course's custom correctness metric (GEval against expected_output)."""
    return GEval(
        name="Answer Correctness",
        criteria=(
            "Judge whether the actual output is factually correct when compared with the "
            "expected output. Penalize wrong prices, limits, dates or policies and invented facts. "
            "Do not penalize different wording."
        ),
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        threshold=threshold or T["answer_correctness"],
        model=get_judge(),
        async_mode=False,
    )


def project1_metrics() -> list:
    """Project 1: Answer Relevancy, Faithfulness and the custom correctness metric."""
    return [answer_relevancy(), faithfulness(), correctness()]
