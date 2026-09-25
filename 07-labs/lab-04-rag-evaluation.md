# Lab 04: RAG Pipeline Evaluation

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 05 — RAG Evaluation with RAGAS                        |
| **Duration**       | 75 minutes                                                   |
| **Difficulty**     | Intermediate                                                 |
| **Learning Objective** | Use RAGAS to evaluate a RAG pipeline's retrieval and generation quality separately, identify which component is the bottleneck, and produce a diagnostic report. |

---

## Prerequisites

- Completed **Lab 02** (comfortable running evaluations)
- Understanding of RAG architecture (retriever + generator)
- `.env` configured with a valid `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Verify RAGAS is installed

```bash
pip show ragas
```

You should see version `0.4.x`. If not:

```bash
pip install "ragas>=0.4.3,<0.5"
```

### 2. Review the RAGAS evaluation suite

```bash
cat evaluators/ragas_suite.py
```

This file defines the four core RAGAS metrics and helper functions.

### 3. Review the support agent's knowledge base

The agent's built-in knowledge base is defined in `agents/support_agent.py` in the `MOCK_KNOWLEDGE_BASE` dictionary. It covers: pricing, refund, password, and API topics.

---

## Step-by-Step Instructions

### Step 1 — Understand the four RAGAS metrics

| Metric               | Evaluates        | What it measures                                     |
| -------------------- | ---------------- | ---------------------------------------------------- |
| `context_precision`  | **Retrieval**    | Are the retrieved documents relevant to the question? |
| `context_recall`     | **Retrieval**    | Did the retriever find all the information needed?    |
| `faithfulness`       | **Generation**   | Is the answer grounded in the retrieved context?      |
| `answer_relevancy`   | **Generation**   | Is the answer relevant to the original question?      |

**Retrieval metrics** tell you if the right documents were found.
**Generation metrics** tell you if the LLM used those documents correctly.

### Step 2 — Create the RAG evaluation test data

Create `tests/rag/test_rag_eval.py`:

```python
"""
Lab 04 — RAG Pipeline Evaluation with RAGAS
Run: pytest tests/rag/test_rag_eval.py -v -s
"""

import json
from agents.support_agent import run_support_agent, MOCK_KNOWLEDGE_BASE


def get_rag_samples() -> list[dict]:
    """
    Run the agent on questions and capture retrieval + generation results.
    Returns samples in RAGAS-compatible format.
    """
    test_queries = [
        {
            "question": "What are your pricing plans?",
            "ground_truth": (
                "TechCorp offers three plans: Basic ($9.99/mo), "
                "Pro ($29.99/mo), and Enterprise (custom pricing). "
                "All plans include core features. Pro adds priority "
                "support and advanced analytics."
            ),
        },
        {
            "question": "What is your refund policy?",
            "ground_truth": (
                "TechCorp offers a 30-day money-back guarantee on all "
                "plans. Refunds are processed within 5-7 business days. "
                "Annual subscriptions are prorated."
            ),
        },
        {
            "question": "How do I reset my password?",
            "ground_truth": (
                "Go to Settings > Security > Reset Password. You'll "
                "receive a verification email. Password must be 8+ "
                "characters with at least one number."
            ),
        },
        {
            "question": "What are the API rate limits for each plan?",
            "ground_truth": (
                "Basic: 100 requests/hour, Pro: 1000 requests/hour, "
                "Enterprise: unlimited. API keys can be generated in "
                "Settings > Developer > API Keys."
            ),
        },
        {
            "question": "Do you offer a free trial?",
            "ground_truth": (
                "The knowledge base does not mention a free trial. "
                "The agent should indicate it does not have this information."
            ),
        },
        {
            "question": "Can I upgrade from Basic to Pro mid-billing cycle?",
            "ground_truth": (
                "The knowledge base does not cover mid-cycle upgrades. "
                "The agent should escalate or indicate uncertainty."
            ),
        },
    ]

    samples = []
    for query in test_queries:
        result = run_support_agent(query["question"])

        # Extract what the retriever actually returned
        retrieved_contexts = [
            tc["result"]
            for tc in result["tool_calls"]
            if tc["tool"] == "search_knowledge_base"
        ]

        # If no KB search was performed, record an empty retrieval
        if not retrieved_contexts:
            retrieved_contexts = ["No knowledge base search was performed."]

        samples.append({
            "question": query["question"],
            "answer": result["response"],
            "contexts": retrieved_contexts,
            "ground_truth": query["ground_truth"],
        })

    return samples
```

### Step 3 — Evaluate with RAGAS metrics

Add the evaluation logic to the same file:

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)


def run_ragas_evaluation(samples: list[dict]) -> dict:
    """Run RAGAS evaluation and return scores."""
    dataset = Dataset.from_dict({
        "question": [s["question"] for s in samples],
        "answer": [s["answer"] for s in samples],
        "contexts": [s["contexts"] for s in samples],
        "ground_truth": [s["ground_truth"] for s in samples],
    })

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
    )

    return result


def test_rag_pipeline():
    """Run the full RAG evaluation pipeline."""
    print("\n" + "=" * 60)
    print("Running RAG Evaluation with RAGAS")
    print("=" * 60)

    # Step 1: Collect samples
    print("\nCollecting agent responses...")
    samples = get_rag_samples()

    for i, s in enumerate(samples):
        print(f"\n--- Sample {i+1}: {s['question'][:50]}...")
        print(f"    Answer: {s['answer'][:80]}...")
        print(f"    Contexts retrieved: {len(s['contexts'])}")

    # Step 2: Run RAGAS evaluation
    print("\nRunning RAGAS metrics (this may take 1-2 minutes)...")
    results = run_ragas_evaluation(samples)

    # Step 3: Print results
    print("\n" + "=" * 60)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 60)

    for metric_name, score in results.items():
        if isinstance(score, (int, float)):
            status = "PASS" if score >= 0.7 else "FAIL"
            print(f"  {metric_name:25s}: {score:.4f}  [{status}]")

    # Step 4: Diagnose bottleneck
    print("\n" + "=" * 60)
    print("BOTTLENECK DIAGNOSIS")
    print("=" * 60)
    diagnose_bottleneck(results)

    assert True  # Test always passes; review the output manually
```

### Step 4 — Build the bottleneck diagnosis function

Add this function above the test:

```python
def diagnose_bottleneck(results: dict) -> None:
    """Identify whether retrieval or generation is the bottleneck."""
    retrieval_metrics = {}
    generation_metrics = {}

    for key, value in results.items():
        if not isinstance(value, (int, float)):
            continue
        if key in ("context_precision", "context_recall"):
            retrieval_metrics[key] = value
        elif key in ("faithfulness", "answer_relevancy"):
            generation_metrics[key] = value

    avg_retrieval = (
        sum(retrieval_metrics.values()) / len(retrieval_metrics)
        if retrieval_metrics else 0
    )
    avg_generation = (
        sum(generation_metrics.values()) / len(generation_metrics)
        if generation_metrics else 0
    )

    print(f"  Average Retrieval Score:  {avg_retrieval:.4f}")
    print(f"  Average Generation Score: {avg_generation:.4f}")
    print()

    if avg_retrieval < avg_generation:
        print("  DIAGNOSIS: Retrieval is the bottleneck.")
        print("  RECOMMENDATIONS:")
        print("    - Improve search query formulation")
        print("    - Add more documents to the knowledge base")
        print("    - Use semantic search instead of keyword matching")
        print("    - Increase the number of retrieved chunks")
    elif avg_generation < avg_retrieval:
        print("  DIAGNOSIS: Generation is the bottleneck.")
        print("  RECOMMENDATIONS:")
        print("    - Improve the system prompt to encourage grounded answers")
        print("    - Use a more capable model for generation")
        print("    - Add explicit instructions to cite retrieved context")
        print("    - Reduce hallucination with lower temperature")
    else:
        print("  DIAGNOSIS: Both components perform similarly.")
        print("  RECOMMENDATIONS:")
        print("    - Improve both retrieval and generation")
        print("    - Focus on the lowest individual metric first")
```

### Step 5 — Run the evaluation

```bash
pytest tests/rag/test_rag_eval.py -v -s
```

The `-s` flag ensures `print()` output is visible.

### Step 6 — Create a diagnostic report

After reviewing the output, create `reports/rag_diagnostic.md`:

```markdown
# RAG Pipeline Diagnostic Report

## Date: [today's date]
## Agent: TechCorp Customer Support Agent

### Metric Scores

| Metric             | Score  | Threshold | Status |
| ------------------ | ------ | --------- | ------ |
| context_precision  | [X.XX] | 0.70      | [P/F]  |
| context_recall     | [X.XX] | 0.70      | [P/F]  |
| faithfulness       | [X.XX] | 0.80      | [P/F]  |
| answer_relevancy   | [X.XX] | 0.70      | [P/F]  |

### Bottleneck Analysis

- **Retrieval average:** [X.XX]
- **Generation average:** [X.XX]
- **Primary bottleneck:** [Retrieval / Generation]

### Observations

1. [What you noticed about the results]
2. [Which queries performed worst and why]
3. [The "free trial" query — did the agent hallucinate?]

### Recommendations

1. [Specific improvement suggestion]
2. [Specific improvement suggestion]
```

Fill in the values from your evaluation run.

---

## Expected Output

```
============================================================
Running RAG Evaluation with RAGAS
============================================================

Collecting agent responses...

--- Sample 1: What are your pricing plans?...
    Answer: TechCorp offers three plans: Basic at $9.99...
    Contexts retrieved: 1

--- Sample 2: What is your refund policy?...
    ...

Running RAGAS metrics (this may take 1-2 minutes)...

============================================================
RAGAS EVALUATION RESULTS
============================================================
  context_precision          : 0.8333  [PASS]
  context_recall             : 0.7500  [PASS]
  faithfulness               : 0.9167  [PASS]
  answer_relevancy           : 0.8200  [PASS]

============================================================
BOTTLENECK DIAGNOSIS
============================================================
  Average Retrieval Score:  0.7917
  Average Generation Score: 0.8683

  DIAGNOSIS: Retrieval is the bottleneck.
  ...
```

---

## Verification Checklist

- [ ] RAGAS is installed and importable
- [ ] Six test queries ran through the agent successfully
- [ ] All four RAGAS metrics produced numerical scores
- [ ] You identified the bottleneck (retrieval vs. generation)
- [ ] You noted which queries the agent struggled with (especially out-of-KB queries)
- [ ] You created the `rag_diagnostic.md` report
- [ ] You can explain why `context_recall` depends on `ground_truth`

---

## Common Pitfalls

1. **Empty `contexts` list** — If the agent doesn't call `search_knowledge_base`, the contexts list will be empty, causing RAGAS to produce misleading scores. The code above handles this by inserting a placeholder string, but be aware this artificially lowers retrieval scores.

2. **RAGAS version mismatch** — The RAGAS API changed between 0.1.x and 0.4.x. If you see `ImportError` for metric names, check your version with `pip show ragas` and consult the [RAGAS migration guide](https://docs.ragas.io/).

3. **Confusing `context` with `retrieval_context`** — In RAGAS, `contexts` is what the retriever returned (like DeepEval's `retrieval_context`). Don't pass ground-truth documents as contexts — that measures generation only, not retrieval.

---

## Extension Challenge

**Advanced:** The support agent uses simple keyword matching for retrieval (see `MOCK_KNOWLEDGE_BASE` in `support_agent.py`). Modify the `search_knowledge_base` tool to deliberately return irrelevant results for one query (e.g., return the "pricing" article when asked about "password reset"). Re-run the RAGAS evaluation and observe:

1. How does `context_precision` change for that query?
2. How does `faithfulness` change — does the agent hallucinate or stay grounded?
3. Write a one-paragraph analysis of how retrieval quality affects generation quality.
