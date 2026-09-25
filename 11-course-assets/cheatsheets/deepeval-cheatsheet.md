# DeepEval Cheatsheet

## Quick Reference for AI Agent Testing & Evaluation Course

### Installation
```bash
pip install deepeval
```

### Basic Test Structure
```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

def test_my_agent():
    test_case = LLMTestCase(
        input="user question",
        actual_output="agent response",
        expected_output="ideal response",       # optional
        context=["source context"],              # optional
        retrieval_context=["retrieved docs"],     # optional
    )
    metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
    assert_test(test_case, [metric])
```

### Run Tests
```bash
pytest tests/ -v                          # All tests
pytest tests/ -v -m functional            # By marker
pytest tests/ -v -k "test_pricing"        # By name
deepeval test run tests/                  # DeepEval CLI
```

### Built-in Metrics (Most Used)

| Metric | What It Measures | Typical Threshold |
|--------|-----------------|-------------------|
| `AnswerRelevancyMetric` | Is the response relevant to the question? | 0.7 |
| `FaithfulnessMetric` | Is the response grounded in context? | 0.8 |
| `HallucinationMetric` | Does the response contain fabricated info? | 0.3 (lower=better) |
| `ContextualPrecisionMetric` | Is retrieved context relevant? | 0.7 |
| `ContextualRecallMetric` | Does context cover the reference? | 0.7 |
| `TaskCompletionMetric` | Did the agent complete its task? | 0.8 |
| `ToolCorrectnessMetric` | Did the agent use the right tools? | 0.85 |

### Custom G-Eval Metric
```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

custom = GEval(
    name="Policy Compliance",
    criteria="The response correctly applies the company refund policy...",
    evaluation_params=[
        LLMTestCaseParams.INPUT,
        LLMTestCaseParams.ACTUAL_OUTPUT,
        LLMTestCaseParams.CONTEXT,
    ],
    threshold=0.7,
    model="gpt-4o-mini",
)
```

### Loading a Golden Dataset
```python
from deepeval.dataset import EvaluationDataset

dataset = EvaluationDataset()
dataset.add_test_cases_from_json_file(
    file_path="datasets/golden_support.json",
    input_key_name="input",
    actual_output_key_name="actual_output",
    expected_output_key_name="expected_output",
    context_key_name="context",
)
```

### Key Tips
- Always set `model="gpt-4o-mini"` for cost efficiency
- Use `threshold` to define pass/fail criteria
- Combine multiple metrics in one `assert_test()` call
- Run `deepeval login` to sync results to DeepEval cloud (optional)
- Use pytest markers to organize test categories
