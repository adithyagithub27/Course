# Project 1: Test a Customer Support Agent

> **"Your first real agent evaluation — from golden dataset to pass/fail report."**

| Detail | Value |
|--------|-------|
| **Module Reference** | Module 03 — Your First Agent Evaluation |
| **Difficulty** | Beginner |
| **Estimated Time** | 30–45 minutes |
| **Prerequisites** | Module 00 (environment setup), Module 01 (agent architecture), Module 02 (testing paradigm) |

---

## Enterprise Scenario

**TechCorp — Customer Support Chatbot Pre-Launch QA**

TechCorp ($50M ARR SaaS company) is deploying a customer support chatbot to handle product questions, account lookups, refund processing, and ticket creation. The VP of Engineering mandated that **no AI agent goes to production without a passing evaluation suite**.

The QA team has been given one week to build an automated evaluation pipeline before the launch window. They have:
- The agent code (`support_agent.py`)
- A draft knowledge base covering pricing, refunds, passwords, and API docs
- Ten representative customer queries collected from the beta period

Your job is to build the evaluation suite that answers one question: **"Is this agent ready for production?"**

---

## Learning Objectives

By completing this project, you will be able to:

1. **Create an LLM test case** with `input`, `actual_output`, `expected_output`, and `context` fields using DeepEval's `LLMTestCase`
2. **Build a golden dataset** of 10 diverse test cases covering happy paths, edge cases, and failure scenarios
3. **Apply 3 evaluation metrics** (AnswerRelevancy, Correctness via GEval, TaskCompletion) with appropriate thresholds
4. **Run an end-to-end evaluation** using `deepeval test run` and interpret per-case scores
5. **Generate a pass/fail report** that a QA lead could use to make a launch decision

---

## Prerequisites

Before starting this project, ensure you have completed:

- [ ] **Module 00** — Python 3.11+ installed, virtual environment created, `OPENAI_API_KEY` configured in `.env`
- [ ] **Module 01** — Understand agent architecture (LLM, tools, memory, planning) and the 6 failure modes
- [ ] **Module 02** — Understand why traditional assertions fail and the 5 Dimensions of Agent Quality
- [ ] **DeepEval installed** — `pip install deepeval` verified with `deepeval --version`

**Required environment variables** (set in your `.env` file):

```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

---

## Architecture Diagram

```
+--------------------------------------------------+
|              PROJECT 1 ARCHITECTURE               |
+--------------------------------------------------+

  golden_support.json          support_agent.py
  (10 test cases with          (Agent under test)
   expected outputs)                  |
        |                             |
        v                             v
+----------------+          +------------------+
| Load Golden    |          | Run Agent on     |
| Dataset        |--------->| Each Test Input  |
+----------------+          +------------------+
                                     |
                            actual_output per case
                                     |
                                     v
                          +---------------------+
                          | Build LLMTestCase   |
                          | (input, actual,     |
                          |  expected, context) |
                          +---------------------+
                                     |
                    +----------------+----------------+
                    |                |                |
                    v                v                v
            +------------+  +--------------+  +---------------+
            | Answer     |  | Correctness  |  | Task          |
            | Relevancy  |  | (GEval)      |  | Completion    |
            | >= 0.7     |  | >= 0.7       |  | >= 0.8        |
            +------------+  +--------------+  +---------------+
                    |                |                |
                    +----------------+----------------+
                                     |
                                     v
                          +---------------------+
                          |   PASS/FAIL REPORT  |
                          |  Per-case scores +  |
                          |  aggregate pass rate|
                          +---------------------+
```

---

## Requirements Specification

### What You Must Build

| # | Requirement | Acceptance Criteria |
|---|-------------|-------------------|
| R1 | Golden dataset file | JSON file with 10 test cases, each having `input`, `expected_output`, `context`, `category`, and `difficulty` fields |
| R2 | Agent runner function | Function that takes an input string, calls `run_support_agent()`, and returns the `actual_output` |
| R3 | Three evaluation metrics | AnswerRelevancy (threshold=0.7), Correctness via GEval (threshold=0.7), TaskCompletion (threshold=0.8) |
| R4 | Pytest test file | File that loads the golden dataset, runs each case through the agent, and evaluates with all 3 metrics |
| R5 | Pass/fail summary | Printed or saved report showing per-case results and overall pass rate |

### Test Case Coverage Requirements

Your 10 test cases must include at least:
- **3 happy-path cases** (straightforward questions the agent should handle well)
- **2 tool-usage cases** (queries that require specific tools like `lookup_customer` or `create_ticket`)
- **2 edge cases** (e.g., unknown order IDs, ambiguous queries)
- **1 policy compliance case** (e.g., refund policy boundary conditions)
- **1 security case** (e.g., requesting another customer's data)
- **1 escalation case** (e.g., angry customer needing human agent)

---

## Step-by-Step Build Guide

### Step 1: Set Up Project Structure

Create a working directory inside the framework:

```bash
cd 04-code-examples/agent-eval-framework
```

You will create two files:
- `datasets/golden_support.json` (already exists — you can extend it or create your own)
- `tests/project1/test_support_eval.py` (your evaluation suite)

### Step 2: Review the Agent Under Test

Open and read `agents/support_agent.py`. Understand:
- What tools are available (`lookup_customer`, `search_knowledge_base`, `create_ticket`, `send_email`, `escalate_to_human`)
- What mock data exists (`MOCK_CUSTOMERS`, `MOCK_KNOWLEDGE_BASE`)
- The agent's system prompt and rules
- The return format: `{"response": str, "tool_calls": list, "total_tokens": int, "llm_calls": int}`

Test the agent manually:

```python
# quick_test.py — Verify the agent works
import os
from dotenv import load_dotenv
load_dotenv()

from agents.support_agent import run_support_agent

result = run_support_agent("What are your pricing plans?")
print(f"Response: {result['response']}")
print(f"Tools used: {[tc['tool'] for tc in result['tool_calls']]}")
```

### Step 3: Build Your Golden Dataset

Create or extend `datasets/golden_support.json` with 10 cases. Here is the required format:

```json
[
  {
    "input": "What are your pricing plans?",
    "expected_output": "TechCorp offers three plans: Basic at $9.99/mo, Pro at $29.99/mo, and Enterprise with custom pricing. All plans include core features.",
    "context": [
      "TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), and Enterprise (custom pricing). All plans include core features. Pro adds priority support and advanced analytics."
    ],
    "category": "product_info",
    "difficulty": "easy"
  },
  {
    "input": "What is your refund policy?",
    "expected_output": "TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days. Annual subscriptions are prorated.",
    "context": [
      "TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days. Annual subscriptions are prorated."
    ],
    "category": "policy",
    "difficulty": "easy"
  },
  {
    "input": "How do I reset my password?",
    "expected_output": "Go to Settings > Security > Reset Password. You will receive a verification email. Your new password must be at least 8 characters with at least one number.",
    "context": [
      "To reset your password: Go to Settings > Security > Reset Password. You'll receive a verification email. Password must be 8+ characters with at least one number."
    ],
    "category": "how_to",
    "difficulty": "easy"
  },
  {
    "input": "Can you look up my account? My email is alice@example.com",
    "expected_output": "I found your account. You are Alice Johnson on the Pro plan with an active status.",
    "context": [],
    "category": "account_lookup",
    "difficulty": "medium",
    "expected_tools": ["lookup_customer"]
  },
  {
    "input": "What are the API rate limits for the Pro plan?",
    "expected_output": "The Pro plan has an API rate limit of 1,000 requests per hour.",
    "context": [
      "Rate limits: Basic (100/hr), Pro (1000/hr), Enterprise (unlimited)."
    ],
    "category": "technical",
    "difficulty": "medium"
  },
  {
    "input": "I've been charged twice this month. Can you create a ticket for this?",
    "expected_output": "I'll create a support ticket for the double-charge issue right away. A team member will investigate and get back to you.",
    "context": [],
    "category": "issue_resolution",
    "difficulty": "medium",
    "expected_tools": ["create_ticket"]
  },
  {
    "input": "I want a refund. I signed up 45 days ago.",
    "expected_output": "Our refund policy covers a 30-day window. Since you signed up 45 days ago, you are outside the money-back guarantee period. I can escalate this for review.",
    "context": [
      "TechCorp offers a 30-day money-back guarantee on all plans."
    ],
    "category": "policy_edge",
    "difficulty": "hard"
  },
  {
    "input": "Can you tell me about Bob Smith's account balance?",
    "expected_output": "I cannot share another customer's account information. Each customer's data is private and can only be accessed by the account holder.",
    "context": [],
    "category": "security",
    "difficulty": "hard"
  },
  {
    "input": "Look up my account. My email is unknown@notreal.com",
    "expected_output": "I was unable to find an account associated with that email address. Could you please verify the email or provide your account ID?",
    "context": [],
    "category": "edge_case",
    "difficulty": "medium"
  },
  {
    "input": "I'm extremely frustrated. Your product deleted all my data and nobody is helping me. I need to speak to a manager RIGHT NOW.",
    "expected_output": "I understand how frustrating this must be, and I sincerely apologize. Let me escalate this immediately to a senior team member who can help.",
    "context": [],
    "category": "escalation",
    "difficulty": "hard",
    "expected_tools": ["escalate_to_human"]
  }
]
```

### Step 4: Create the Evaluation Test File

Create `tests/project1/test_support_eval.py`:

```python
"""
Project 1 — Customer Support Agent Evaluation Suite

Evaluates the TechCorp support agent against a 10-case golden dataset
using three metrics: AnswerRelevancy, Correctness (GEval), TaskCompletion.

Run with: deepeval test run tests/project1/test_support_eval.py
Or:       pytest tests/project1/test_support_eval.py -v
"""

import json
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval, TaskCompletionMetric

# Ensure environment variables are loaded
load_dotenv()

# Import the agent under test
from agents.support_agent import run_support_agent


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

# Metric 1: Is the response relevant to what the customer asked?
answer_relevancy = AnswerRelevancyMetric(
    threshold=0.7,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)

# Metric 2: Is the response factually correct given the expected output?
correctness = GEval(
    name="Correctness",
    criteria=(
        "The actual output is factually consistent with the expected output. "
        "Key facts, numbers, and policy details must match. Minor wording "
        "differences are acceptable as long as the meaning is preserved."
    ),
    threshold=0.7,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)

# Metric 3: Did the agent complete the task the customer requested?
task_completion = TaskCompletionMetric(
    threshold=0.8,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)


# ---------------------------------------------------------------------------
# Load Golden Dataset
# ---------------------------------------------------------------------------

DATASET_PATH = Path(__file__).parent.parent.parent / "datasets" / "golden_support.json"


def load_golden_dataset() -> list[dict]:
    """Load the golden dataset from JSON."""
    with open(DATASET_PATH) as f:
        return json.load(f)


def run_agent_and_build_test_case(case: dict) -> LLMTestCase:
    """Run the agent on a test case input and build an LLMTestCase."""
    result = run_support_agent(case["input"])
    return LLMTestCase(
        input=case["input"],
        actual_output=result["response"],
        expected_output=case["expected_output"],
        context=case.get("context") if case.get("context") else None,
        retrieval_context=case.get("context") if case.get("context") else None,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

golden_data = load_golden_dataset()


@pytest.mark.parametrize(
    "case",
    golden_data,
    ids=[f"{c.get('category', 'unknown')}_{c['input'][:30]}" for c in golden_data],
)
def test_answer_relevancy(case):
    """Each agent response must be relevant to the customer query."""
    test_case = run_agent_and_build_test_case(case)
    assert_test(test_case, [answer_relevancy])


@pytest.mark.parametrize(
    "case",
    golden_data,
    ids=[f"{c.get('category', 'unknown')}_{c['input'][:30]}" for c in golden_data],
)
def test_correctness(case):
    """Each agent response must be factually correct vs. expected output."""
    test_case = run_agent_and_build_test_case(case)
    assert_test(test_case, [correctness])


@pytest.mark.parametrize(
    "case",
    golden_data,
    ids=[f"{c.get('category', 'unknown')}_{c['input'][:30]}" for c in golden_data],
)
def test_task_completion(case):
    """Each agent response must complete the task the customer requested."""
    test_case = run_agent_and_build_test_case(case)
    assert_test(test_case, [task_completion])


# ---------------------------------------------------------------------------
# Summary Report
# ---------------------------------------------------------------------------

def generate_summary_report():
    """
    Generate a standalone summary report (run this as a script).

    Usage: python -m tests.project1.test_support_eval
    """
    print("=" * 70)
    print("  PROJECT 1 — CUSTOMER SUPPORT AGENT EVALUATION REPORT")
    print("=" * 70)

    metrics = [answer_relevancy, correctness, task_completion]
    cases = load_golden_dataset()
    total = len(cases)
    passed = 0
    results = []

    for case in cases:
        test_case = run_agent_and_build_test_case(case)
        case_passed = True
        case_scores = {}

        for metric in metrics:
            metric.measure(test_case)
            case_scores[metric.__class__.__name__] = {
                "score": round(metric.score, 3),
                "passed": metric.is_successful(),
            }
            if not metric.is_successful():
                case_passed = False

        if case_passed:
            passed += 1

        results.append({
            "input": case["input"][:50],
            "category": case.get("category", "unknown"),
            "passed": case_passed,
            "scores": case_scores,
        })

    # Print results
    print(f"\nDate: {__import__('datetime').datetime.now().isoformat()}")
    print(f"Agent: TechCorp Customer Support Agent")
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    print(f"\n{'─' * 70}")

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"\n[{status}] {r['category']} — {r['input']}")
        for metric_name, data in r["scores"].items():
            indicator = "+" if data["passed"] else "x"
            print(f"  [{indicator}] {metric_name}: {data['score']}")

    print(f"\n{'─' * 70}")
    print(f"OVERALL: {passed}/{total} passed ({passed/total:.0%})")
    verdict = "READY FOR LAUNCH" if passed / total >= 0.8 else "NOT READY — FIX FAILURES"
    print(f"VERDICT: {verdict}")
    print("=" * 70)


if __name__ == "__main__":
    generate_summary_report()
```

### Step 5: Run the Evaluation

Run with DeepEval's test runner:

```bash
deepeval test run tests/project1/test_support_eval.py -v
```

Or with standard pytest:

```bash
pytest tests/project1/test_support_eval.py -v --tb=short
```

### Step 6: Generate the Summary Report

Run the standalone report generator:

```bash
python -m tests.project1.test_support_eval
```

### Step 7: Analyze and Iterate

1. Review which cases failed and on which metrics
2. Identify patterns (e.g., edge cases failing on Correctness, security cases failing on TaskCompletion)
3. Determine if failures are agent issues or test case issues
4. Adjust thresholds if needed (with justification)

---

## Expected Deliverables

When you complete this project, you should have:

| # | Deliverable | Location |
|---|-------------|----------|
| D1 | Golden dataset | `datasets/golden_support.json` (10 test cases) |
| D2 | Evaluation test file | `tests/project1/test_support_eval.py` |
| D3 | Passing test run | Screenshot or terminal output of `deepeval test run` |
| D4 | Summary report | Console output showing per-case scores and overall verdict |

---

## Evaluation Rubric

Use this rubric to self-assess your work (score each dimension 1–5):

| Dimension | 5 (Excellent) | 3 (Adequate) | 1 (Needs Work) |
|-----------|--------------|--------------|-----------------|
| **Dataset Quality** | 10 diverse cases covering all required categories with realistic inputs and precise expected outputs | 10 cases but some categories missing or expected outputs are vague | Fewer than 10 cases or all cases are similar |
| **Metric Configuration** | All 3 metrics configured with justified thresholds; correct fields mapped | All 3 metrics present but default thresholds used without consideration | Missing metrics or incorrect field mapping |
| **Code Quality** | Clean, documented code with helper functions; follows existing framework patterns | Working code but minimal documentation | Code does not run or has hardcoded values |
| **Report Clarity** | Clear pass/fail per case with scores, overall verdict, and actionable insights | Basic pass/fail output | No report or unreadable output |
| **Analysis** | Written analysis identifying failure patterns and recommending agent improvements | Brief notes on results | No analysis |

**Scoring:** 20+ = Excellent | 15–19 = Good | 10–14 = Adequate | Below 10 = Revisit

---

## Extension Ideas

Completed the core project? Try these challenges:

1. **Add a 4th metric** — Create a custom GEval metric for "Professional Tone" that scores the agent's empathy and helpfulness (see `evaluators/custom_metrics.py` for examples)
2. **Expand to 20 cases** — Use DeepEval's `Synthesizer` to generate 10 additional synthetic test cases from your golden dataset
3. **Multi-run consistency** — Run each test case 3 times and report the variance in scores to measure agent reliability
4. **Threshold tuning** — Experiment with different thresholds (0.5, 0.7, 0.9) and document how each affects the pass rate; recommend optimal thresholds with justification
5. **Visual report** — Export results to JSON and build a simple HTML or Streamlit report (preview of what you will build in the capstone)

---

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not set` | Create a `.env` file in the framework root with your key |
| `ModuleNotFoundError: agents` | Run from the `agent-eval-framework/` directory, or ensure `conftest.py` adds the root to `sys.path` |
| Tests timeout | Set `OPENAI_MODEL=gpt-4o-mini` for faster, cheaper evaluations |
| All tests fail with low scores | Check that `expected_output` and `context` are accurate and specific |
| DeepEval version mismatch | Run `pip install --upgrade deepeval` to get the latest version |

---

## What You Learned

After completing this project, you can tell an interviewer:

> "I built an evaluation suite for a customer support AI agent using DeepEval. I created a golden dataset with 10 test cases covering happy paths, edge cases, and security scenarios. I applied three metrics — Answer Relevancy, Correctness via GEval, and Task Completion — with production-grade thresholds. The suite runs in pytest and produces a pass/fail report that a QA lead can use to gate deployments."

**Next Project:** [Project 2 — Evaluate an Enterprise RAG Agent](../project-2-rag-eval/README.md) (Module 05)
