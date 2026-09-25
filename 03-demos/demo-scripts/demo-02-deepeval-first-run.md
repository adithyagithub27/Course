# Demo 02 — First DeepEval Run

**Used in:** Lecture 3.1 (Meet DeepEval)
**Duration:** ~3 minutes of screen recording
**Purpose:** Show how easy it is to write and run a DeepEval test

## Setup

```bash
cd agent-eval-framework
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

## Recording Script

### Scene 1: Write the Test (60s)

Open VS Code / terminal editor. Type out (or show pre-written):

```python
# my_first_eval.py
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

from agents.support_agent import run_support_agent


def test_pricing_question():
    """Agent should give a relevant answer about pricing."""
    result = run_support_agent("What are your pricing plans?")

    test_case = LLMTestCase(
        input="What are your pricing plans?",
        actual_output=result["response"],
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model="gpt-4o-mini",
    )

    assert_test(test_case, [metric])
```

Narration point: "Six imports. One function. One metric. That's it."

### Scene 2: Run It (30s)

```bash
pytest my_first_eval.py -v
```

Show the output:
- DeepEval banner
- Test discovery
- Running... (progress indicator)
- Score: 0.92 (above 0.7 threshold)
- PASSED in green

### Scene 3: Make It Fail (60s)

Modify the test to use a stricter threshold:

```python
metric = AnswerRelevancyMetric(
    threshold=0.99,  # Unrealistically high
    model="gpt-4o-mini",
)
```

Run again:
```bash
pytest my_first_eval.py -v
```

Show:
- Score: 0.92 (below 0.99 threshold)
- FAILED in red
- DeepEval's reason output explaining WHY it scored 0.92

Narration: "The metric didn't just say 'fail.' It told you WHY. That's the power of LLM-as-judge evaluation."

### Scene 4: Add Multiple Metrics (30s)

```python
from deepeval.metrics import FaithfulnessMetric

# Add faithfulness check
faithfulness = FaithfulnessMetric(threshold=0.8, model="gpt-4o-mini")
assert_test(test_case, [relevancy, faithfulness])
```

Run and show both metrics evaluated in one test.

## Post-Production Notes
- Use dark IDE theme with syntax highlighting
- Terminal output should use the course color scheme where possible
- Slow down typing for key moments (metric creation, assert_test call)
- Split screen: code on left, terminal on right during the run
