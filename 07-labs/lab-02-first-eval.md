# Lab 02: Write and Run Your First DeepEval Evaluation

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 03 — Evaluation Fundamentals with DeepEval            |
| **Duration**       | 60 minutes                                                   |
| **Difficulty**     | Beginner                                                     |
| **Learning Objective** | Install DeepEval, write three LLM test cases with `AnswerRelevancyMetric`, run them with `pytest`, and interpret the pass/fail output. |

---

## Prerequisites

- Completed **Lab 01** (you can run the support agent successfully)
- Python virtual environment activated with `requirements.txt` installed
- `.env` configured with a valid `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Verify DeepEval is installed

```bash
pip show deepeval
```

You should see version `3.9.x` or higher. If not:

```bash
pip install "deepeval>=3.9.0,<4.0"
```

### 2. Verify pytest integration

```bash
deepeval --version
pytest --version
```

### 3. Create the test directory structure

```bash
mkdir -p tests/evaluation
touch tests/__init__.py
touch tests/evaluation/__init__.py
```

---

## Step-by-Step Instructions

### Step 1 — Understand the test case structure

A DeepEval `LLMTestCase` requires at minimum:

| Field            | Description                                  | Required |
| ---------------- | -------------------------------------------- | -------- |
| `input`          | The user message sent to the agent           | Yes      |
| `actual_output`  | The agent's actual response                  | Yes      |
| `expected_output`| The ideal / reference response               | No       |
| `context`        | Ground-truth context (list of strings)       | No       |
| `retrieval_context` | What the retriever actually returned      | No       |

### Step 2 — Write your first evaluation test file

Create `tests/evaluation/test_first_eval.py`:

```python
"""
Lab 02 — First DeepEval Evaluation
Run: pytest tests/evaluation/test_first_eval.py -v
"""

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

from agents.support_agent import run_support_agent


# ── Metric Configuration ─────────────────────────────────────────
relevancy_metric = AnswerRelevancyMetric(
    threshold=0.7,        # minimum score to pass (0.0 – 1.0)
    model="gpt-4o-mini",  # judge model
)


# ── Helper: run agent and build test case ─────────────────────────
def make_test_case(user_input: str, expected: str) -> LLMTestCase:
    """Run the agent and wrap the result as a DeepEval test case."""
    result = run_support_agent(user_input)
    return LLMTestCase(
        input=user_input,
        actual_output=result["response"],
        expected_output=expected,
    )


# ── Test Cases ────────────────────────────────────────────────────
class TestAnswerRelevancy:
    """Verify the agent's responses are relevant to the user's question."""

    def test_pricing_question(self):
        """Agent should give relevant pricing information."""
        test_case = make_test_case(
            user_input="What are your pricing plans?",
            expected="TechCorp offers three plans: Basic ($9.99/mo), "
                     "Pro ($29.99/mo), and Enterprise (custom pricing).",
        )
        assert_test(test_case, [relevancy_metric])

    def test_refund_policy(self):
        """Agent should give relevant refund policy information."""
        test_case = make_test_case(
            user_input="What is your refund policy?",
            expected="TechCorp offers a 30-day money-back guarantee. "
                     "Refunds are processed within 5-7 business days.",
        )
        assert_test(test_case, [relevancy_metric])

    def test_password_reset(self):
        """Agent should give relevant password reset instructions."""
        test_case = make_test_case(
            user_input="How do I reset my password?",
            expected="Go to Settings > Security > Reset Password. "
                     "You will receive a verification email.",
        )
        assert_test(test_case, [relevancy_metric])
```

### Step 3 — Run the evaluation with pytest

```bash
pytest tests/evaluation/test_first_eval.py -v
```

This will:

1. Execute the support agent for each test input
2. Send the input + output to the judge model (`gpt-4o-mini`)
3. Score the answer relevancy on a 0.0 – 1.0 scale
4. Pass if the score meets or exceeds the threshold (0.7)

### Step 4 — Interpret the output

You will see output similar to:

```
tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_pricing_question PASSED
tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_refund_policy PASSED
tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_password_reset PASSED

========================= 3 passed in 12.34s =========================
```

If a test **fails**, DeepEval prints detailed diagnostics:

```
FAILED tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_password_reset
  Metric: AnswerRelevancyMetric
  Score: 0.45 (threshold: 0.7)
  Reason: The response included irrelevant information about ...
```

**Key things to look for:**

- **Score** — how well the agent's response matched the query intent
- **Reason** — the judge model's explanation for the score
- **Threshold** — whether the score met your configured minimum

### Step 5 — Experiment with thresholds

Modify the threshold to see how it affects pass/fail:

```python
# Strict threshold — harder to pass
strict_metric = AnswerRelevancyMetric(threshold=0.9, model="gpt-4o-mini")

# Lenient threshold — easier to pass
lenient_metric = AnswerRelevancyMetric(threshold=0.5, model="gpt-4o-mini")
```

Add two more tests to your file:

```python
    def test_pricing_strict(self):
        """Same question, higher bar."""
        strict = AnswerRelevancyMetric(threshold=0.9, model="gpt-4o-mini")
        test_case = make_test_case(
            user_input="What are your pricing plans?",
            expected="TechCorp offers three plans: Basic ($9.99/mo), "
                     "Pro ($29.99/mo), and Enterprise (custom pricing).",
        )
        assert_test(test_case, [strict])

    def test_edge_case_ambiguous(self):
        """Ambiguous question — likely to score lower."""
        test_case = make_test_case(
            user_input="Tell me everything",
            expected="I'd be happy to help! Could you clarify what "
                     "you'd like to know about?",
        )
        assert_test(test_case, [relevancy_metric])
```

Re-run:

```bash
pytest tests/evaluation/test_first_eval.py -v
```

### Step 6 — Review the DeepEval summary report

Run with the DeepEval report flag:

```bash
deepeval test run tests/evaluation/test_first_eval.py
```

This produces a richer summary table with all metrics and scores in one view. Review the console output and note the per-test-case scores.

---

## Expected Output

A successful run produces:

```
================== test session starts ==================
tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_pricing_question PASSED
tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_refund_policy PASSED
tests/evaluation/test_first_eval.py::TestAnswerRelevancy::test_password_reset PASSED

================== 3 passed in ~15s ==================
```

Each test takes 3–8 seconds because the judge model must evaluate the response.

---

## Verification Checklist

- [ ] `deepeval` is installed and `deepeval --version` prints the version
- [ ] `test_first_eval.py` is created in `tests/evaluation/`
- [ ] All three core tests pass with `pytest -v`
- [ ] You can read the score and reason from a failing test
- [ ] You experimented with at least one different threshold value
- [ ] You understand that the **judge model** (gpt-4o-mini) scores the **agent model's** output
- [ ] No API keys are hardcoded anywhere in your test files

---

## Common Pitfalls

1. **`ModuleNotFoundError: No module named 'agents'`** — You are running pytest from the wrong directory. Always run from the `agent-eval-framework/` root. Alternatively, install the project in editable mode: `pip install -e .`

2. **Tests take too long / time out** — Each test makes two API calls (one to the agent, one to the judge). On a slow connection, set `pytest --timeout=60` or run fewer tests at first.

3. **All tests pass even with obviously bad responses** — The threshold might be too low. Start with `0.7` and raise it to `0.8` or `0.9`. A threshold of `0.5` will pass almost anything.

---

## Extension Challenge

**Intermediate:** Add a `FaithfulnessMetric` alongside the relevancy metric. This requires a `retrieval_context` field — the documents the agent actually retrieved.

Modify `make_test_case` to capture the knowledge base results from the tool calls:

```python
def make_test_case_with_context(user_input: str, expected: str) -> LLMTestCase:
    result = run_support_agent(user_input)

    # Extract retrieval context from tool calls
    retrieval_context = [
        tc["result"]
        for tc in result["tool_calls"]
        if tc["tool"] == "search_knowledge_base"
    ]

    return LLMTestCase(
        input=user_input,
        actual_output=result["response"],
        expected_output=expected,
        retrieval_context=retrieval_context if retrieval_context else ["No context retrieved."],
    )
```

Then test with both metrics:

```python
from deepeval.metrics import FaithfulnessMetric

faithfulness_metric = FaithfulnessMetric(threshold=0.8, model="gpt-4o-mini")

def test_pricing_faithfulness(self):
    test_case = make_test_case_with_context(
        user_input="What are your pricing plans?",
        expected="...",
    )
    assert_test(test_case, [relevancy_metric, faithfulness_metric])
```

Does the faithfulness score differ from relevancy? Why might that happen?
