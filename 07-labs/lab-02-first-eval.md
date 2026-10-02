# Lab 3.1: Write and Run Your First DeepEval Evaluation

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 3.1 (file `lab-02-first-eval.md`) |
| **Module** | Module 03 — Your First Agent Evaluation |
| **Lectures** | 3.1–3.3 (prepares Project 1, Lecture 3.4) |
| **Duration** | 60 minutes |
| **Difficulty** | Beginner |
| **Learning Objective** | Write pytest-style DeepEval tests against the real TechCorp agent with Answer Relevancy, Faithfulness and the course's Answer Correctness GEval; make one test fail on purpose and read the metric's reason; run the 10-case golden dataset. |
| **Reference solution** | `demos/m03_first_eval.py`, `demos/m03_eval_support_agent.py`, `tests/e2e/test_golden_support.py` |
| **Verified on** | deepeval 4.2.7, openai 2.54.0 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Lab 1.1** (`make install` done, `make test` green)
- Lectures 3.1 and 3.2: `LLMTestCase`, metrics, thresholds, golden datasets
- An OpenAI API key is optional. Offline, every metric is scored by the course's deterministic mock judge, which runs DeepEval's real metric code with a stand-in model.

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
mkdir -p my_work
uv run python demos/m03_first_eval.py        # the lecture demo: AnswerRelevancy = 1.00 -> PASS
```

The judge model comes from `evaluators/judge.py`: `get_judge()` returns `gpt-4.1` when you are live and `MockJudge` offline. Every metric in this course takes `model=get_judge()` so the same test runs both ways.

---

## Step-by-Step Instructions

### Step 1 — Your first test

Create `my_work/test_lab02.py`:

```python
"""Lab 3.1 - your first DeepEval tests against the TechCorp support agent."""
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from agents.support_agent import run_support_agent
from evaluators.judge import get_judge
from evaluators.metrics import correctness


def kb_results(result: dict) -> list[str]:
    """What the knowledge base returned: the context the answer must be faithful to."""
    return [tc["result"] for tc in result["tool_calls"] if tc["tool"] == "search_knowledge_base"]


def test_pricing_answer_is_relevant():
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    test_case = LLMTestCase(input=question, actual_output=result["response"])
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7, model=get_judge())])
```

Run it two ways:

```bash
uv run deepeval test run my_work/test_lab02.py      # DeepEval's runner: results table
uv run pytest -q my_work/test_lab02.py              # plain pytest works too
```

### Step 2 — Faithfulness to the tool result, and correctness

Faithfulness needs the context the answer should be grounded in. For an agent, that is what its tools returned, so pass the knowledge-base results as `retrieval_context`. Correctness compares with an `expected_output` you write. Add to `my_work/test_lab02.py`:

```python
def test_refund_answer_is_faithful_and_correct():
    question = "What is your refund policy?"
    result = run_support_agent(question)
    test_case = LLMTestCase(
        input=question,
        actual_output=result["response"],
        expected_output="TechCorp offers a 30-day money-back guarantee on all plans. "
                        "Refunds are processed within 5-7 business days.",
        retrieval_context=kb_results(result),
    )
    assert_test(test_case, [FaithfulnessMetric(threshold=0.8, model=get_judge()), correctness()])
```

`correctness()` is the course's custom GEval metric ("Answer Correctness", threshold 0.7 from `config/eval_config.yaml`). Open `evaluators/metrics.py` and read its criteria: it penalises wrong prices, limits, dates and policies, but not different wording.

### Step 3 — Make a test fail on purpose

A test you have never seen fail is a test you can't trust. Create `my_work/test_lab02_fail.py`:

```python
"""Lab 3.1 step 3 - a hallucinated answer must FAIL. Run it and read the reason."""
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from agents.support_agent import execute_tool
from evaluators.judge import get_judge


def test_hallucinated_refund_answer_fails():
    kb = execute_tool("search_knowledge_base", {"query": "refund policy"})
    test_case = LLMTestCase(
        input="What is your refund policy?",
        actual_output="We offer a 14-day money-back guarantee, and refunds take about 10 business days.",
        retrieval_context=[kb],
    )
    assert_test(test_case, [FaithfulnessMetric(threshold=0.8, model=get_judge())])
```

```bash
uv run pytest -q my_work/test_lab02_fail.py
```

It fails with Faithfulness 0.0: both claims contradict KB-102. That is exactly the output the agent produces when someone deletes its grounding rule (Lab 1.1, Step 4).

### Step 4 — Run the golden dataset

Open `datasets/golden_support.json`: 10 cases in four categories (`faq` 3, `account` 3, `escalation` 2, `security` 2), each with `input`, `expected_output`, `context` and `expected_tools`. Then run the whole set:

```bash
uv run python demos/m03_eval_support_agent.py
uv run pytest -q tests/e2e/test_golden_support.py
```

Read `tests/e2e/test_golden_support.py`: it is three lines of logic — run the agent, convert the result with `to_test_case()` (`evaluators/deepeval_suite.py`), and `assert_test` with the Project 1 metrics.

### Step 5 — Explain one score

Pick one row of the Step 4 table and write two sentences in `my_work/lab02_notes.md`: what the metric measured on that case and why the score is what it is. Why is Faithfulness "-" for GS-04, GS-05, GS-07 to GS-10? (Hint: `default_metrics_for()` only adds Faithfulness when the case has grounding context.)

---

## Expected Output

Step 1 and 2 with `deepeval test run` (offline; the tail of DeepEval's report):

```
✓ Evaluation completed 🎉! (time taken: 1.13s | token cost: None)
» Test Results (2 total tests):
   » Pass Rate: 100.0% | Passed: 2 | Failed: 0
```

Step 3:

```
E   AssertionError: Metrics: Faithfulness (score: 0.0, threshold: 0.8, strict: False, error: None, reason: Scored offline by the deterministic mock judge (word overlap and number matching).) failed.
FAILED my_work/test_lab02_fail.py::test_hallucinated_refund_answer_fails
1 failed
```

Live, the reason is written by gpt-4.1 and names the contradicting claims.

Step 4:

```
id     category    relevancy  faithful  correct  tools_ok  result
-----  ----------  ---------  --------  -------  --------  ------
GS-01  faq         1.0        1.0       1.0      True      PASS  
GS-02  faq         1.0        1.0       1.0      True      PASS  
GS-03  faq         1.0        1.0       1.0      True      PASS  
GS-04  account     1.0        -         1.0      True      PASS  
GS-05  account     1.0        -         1.0      True      PASS  
GS-06  account     1.0        1.0       1.0      True      PASS  
GS-07  escalation  1.0        -         1.0      True      PASS  
GS-08  escalation  1.0        -         1.0      True      PASS  
GS-09  security    1.0        -         0.9      True      PASS  
GS-10  security    1.0        -         0.9      True      PASS  
10/10 passed (100%). Averages: {'Answer Correctness': 0.98, 'Answer Relevancy': 1.0, 'Faithfulness': 1.0}
```

These are offline teaching numbers. Live scores from gpt-4.1 will differ a little; re-run live before quoting them.

---

## Verification Checklist

- [ ] `my_work/test_lab02.py` passes under both `deepeval test run` and `pytest`
- [ ] Every metric uses `model=get_judge()` (no model name hard-coded in the test)
- [ ] Faithfulness gets the knowledge-base result as `retrieval_context`
- [ ] `my_work/test_lab02_fail.py` fails with Faithfulness 0.0, and you can explain why
- [ ] The golden run shows 10/10 and you can name the four categories
- [ ] Your notes explain one score and the "-" cells

---

## Common Pitfalls

1. **Faithfulness without context.** `FaithfulnessMetric` needs `retrieval_context`; without it DeepEval raises a missing-parameter error. For an agent, the context is the tool output.
2. **Thresholds that never fail.** If you have not seen a test fail, you don't know it can. Step 3 is not optional.
3. **`LLMTestCaseParams` deprecation warning.** DeepEval 4.2 renamed it `SingleTurnParams`. The old name still works but warns; the course uses the new one.
4. **Live costs.** Each judged metric is one or more `gpt-4.1` calls. Keep live runs to the 10-case set while you learn (verify current pricing).

---

## Extension Challenge

1. Add `GS-06` (cancel and refund after 3 weeks) as its own test with the `ToolCorrectnessMetric` from `evaluators.metrics.tool_correctness()` and `expected_tools=[ToolCall(name="lookup_customer"), ToolCall(name="search_knowledge_base"), ToolCall(name="create_ticket")]`. Use `to_test_case()` to build the test case.
2. Write a security test for GS-09 that passes only if **no** tool was called. Which quality dimension is that?
3. Start Project 1 (`08-projects/project-1-customer-support/README.md`): the same 10 cases, a report by category.
