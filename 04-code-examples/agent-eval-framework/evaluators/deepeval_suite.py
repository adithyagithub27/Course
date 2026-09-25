"""
DeepEval Evaluation Suite — Primary evaluation pipeline.

Demonstrates how to build a comprehensive eval suite using DeepEval
with pytest integration. Used in Modules 03, 04, and 14.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    GEval,
    TaskCompletionMetric,
    ToolCorrectnessMetric,
)
from deepeval.dataset import EvaluationDataset


def create_quality_metrics(threshold: float = 0.7) -> list:
    """Create the standard LLM quality metrics suite."""
    return [
        AnswerRelevancyMetric(threshold=threshold, model="gpt-4o-mini"),
        FaithfulnessMetric(threshold=0.8, model="gpt-4o-mini"),
        HallucinationMetric(threshold=0.3, model="gpt-4o-mini"),
    ]


def create_agent_metrics(threshold: float = 0.8) -> list:
    """Create agent-specific metrics."""
    return [
        TaskCompletionMetric(threshold=threshold, model="gpt-4o-mini"),
        ToolCorrectnessMetric(threshold=0.85, model="gpt-4o-mini"),
    ]


def create_custom_metric(
    name: str,
    criteria: str,
    threshold: float = 0.7,
) -> GEval:
    """
    Create a custom G-Eval metric for business-specific evaluation.

    Example:
        metric = create_custom_metric(
            name="Policy Compliance",
            criteria="The response correctly applies company refund policy",
        )
    """
    return GEval(
        name=name,
        criteria=criteria,
        threshold=threshold,
        model="gpt-4o-mini",
    )


def build_test_case(
    input_text: str,
    actual_output: str,
    expected_output: str | None = None,
    context: list[str] | None = None,
    retrieval_context: list[str] | None = None,
) -> LLMTestCase:
    """Build a DeepEval test case from agent execution results."""
    return LLMTestCase(
        input=input_text,
        actual_output=actual_output,
        expected_output=expected_output,
        context=context,
        retrieval_context=retrieval_context,
    )


def load_golden_dataset(path: str) -> EvaluationDataset:
    """Load a golden dataset from a JSON file for regression testing."""
    dataset = EvaluationDataset()
    dataset.add_test_cases_from_json_file(
        file_path=path,
        input_key_name="input",
        actual_output_key_name="actual_output",
        expected_output_key_name="expected_output",
        context_key_name="context",
    )
    return dataset


def run_evaluation(test_cases: list[LLMTestCase], metrics: list) -> dict:
    """
    Run a complete evaluation and return summary results.

    Returns:
        dict with keys: passed, failed, total, pass_rate, details
    """
    results = {"passed": 0, "failed": 0, "total": len(test_cases), "details": []}

    for tc in test_cases:
        case_result = {"input": tc.input, "metrics": {}}
        all_passed = True

        for metric in metrics:
            metric.measure(tc)
            case_result["metrics"][metric.__class__.__name__] = {
                "score": metric.score,
                "passed": metric.is_successful(),
                "reason": metric.reason if hasattr(metric, "reason") else None,
            }
            if not metric.is_successful():
                all_passed = False

        if all_passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        case_result["passed"] = all_passed
        results["details"].append(case_result)

    results["pass_rate"] = (
        results["passed"] / results["total"] if results["total"] > 0 else 0
    )
    return results
