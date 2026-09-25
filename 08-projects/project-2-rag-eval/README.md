# Project 2: Evaluate an Enterprise RAG Agent

> **"Find out if your RAG agent is broken at retrieval, generation, or both."**

| Detail | Value |
|--------|-------|
| **Module Reference** | Module 05 — RAG Evaluation with RAGAS |
| **Difficulty** | Intermediate |
| **Estimated Time** | 45–60 minutes |
| **Prerequisites** | Module 03 (Project 1), Module 04 (LLM quality metrics), Module 05 (RAG concepts) |

---

## Enterprise Scenario

**TechCorp HR — Policy Q&A Bot Reliability Crisis**

TechCorp's HR department deployed a RAG-based Q&A bot six months ago to answer employee questions about vacation policies, expense reimbursement, and remote work guidelines. The bot retrieves chunks from the HR policy document store and generates answers grounded in those chunks.

Last quarter, three incidents surfaced:

1. **Vacation policy error** — The bot told an employee they had 25 vacation days when the policy says 20. The bot retrieved the correct document but hallucinated the number during generation.
2. **Expense confusion** — When asked about meal reimbursement limits, the bot retrieved the *travel* expense policy instead of the *meals* policy, leading to a wrong answer.
3. **Remote work misinformation** — The bot confidently stated remote workers can expense home office furniture up to $2,000. The actual policy is $500. The bot retrieved an outdated policy draft.

The VP of People Operations wants a **diagnostic evaluation** that pinpoints whether each failure is a **retrieval problem** (wrong documents fetched) or a **generation problem** (wrong answer from correct documents). You are building that evaluation pipeline.

---

## Learning Objectives

By completing this project, you will be able to:

1. **Distinguish retrieval vs. generation failures** using RAGAS metrics (context_precision, context_recall vs. faithfulness, answer_relevancy)
2. **Build a RAG evaluation pipeline** that scores both halves of the RAG pipeline independently
3. **Create an HR policy dataset** with questions, ground truth answers, and reference contexts
4. **Combine RAGAS and DeepEval metrics** in a single evaluation report
5. **Produce a diagnostic breakdown** showing exactly where quality drops occur in the RAG pipeline

---

## Prerequisites

Before starting this project, ensure you have completed:

- [ ] **Project 1** — You can build golden datasets and run DeepEval evaluations
- [ ] **Module 04** — You understand LLM quality metrics (relevancy, faithfulness, hallucination)
- [ ] **Module 05** — You understand RAG architecture and the 4 RAGAS metrics
- [ ] **RAGAS installed** — `pip install ragas` verified
- [ ] **DeepEval installed** — `pip install deepeval` verified

**Required environment variables** (set in your `.env` file):

```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

---

## Architecture Diagram

```
+-------------------------------------------------------------+
|               PROJECT 2 ARCHITECTURE                         |
+-------------------------------------------------------------+

  HR Policy Documents              Employee Questions
  (company_policies.json)          (rag_eval_dataset.json)
        |                                  |
        v                                  v
+------------------+             +------------------+
| Simulated Vector |             | Load Evaluation  |
| Store (chunks)   |             | Dataset          |
+------------------+             +------------------+
        |                                  |
        +----------------------------------+
                       |
                       v
              +------------------+
              |   RAG Agent      |
              |   (rag_agent.py) |
              |                  |
              |  1. Retrieve     |
              |  2. Generate     |
              +------------------+
                       |
          +------------+------------+
          |                         |
   Retrieved Contexts         Generated Answer
          |                         |
          v                         v
+-------------------+     +-------------------+
| RETRIEVAL METRICS |     | GENERATION METRICS|
|                   |     |                   |
| context_precision |     | faithfulness      |
| context_recall    |     | answer_relevancy  |
| (RAGAS)           |     | (RAGAS + DeepEval)|
+-------------------+     +-------------------+
          |                         |
          +------------+------------+
                       |
                       v
          +-------------------------+
          | DIAGNOSTIC REPORT       |
          |                         |
          | Retrieval Score: 0.XX   |
          | Generation Score: 0.XX  |
          | Root Cause: Retrieval / |
          |   Generation / Both     |
          +-------------------------+
```

---

## Requirements Specification

### What You Must Build

| # | Requirement | Acceptance Criteria |
|---|-------------|-------------------|
| R1 | HR policy document corpus | JSON file with at least 8 policy chunks covering vacation, expenses, remote work, and benefits |
| R2 | RAG evaluation dataset | JSON file with 10 questions, ground truth answers, and reference contexts |
| R3 | Simulated RAG agent | Python function that retrieves contexts and generates answers (or use the provided `rag_agent.py`) |
| R4 | RAGAS evaluation pipeline | Script that computes all 4 RAGAS metrics (context_precision, context_recall, faithfulness, answer_relevancy) |
| R5 | DeepEval quality layer | Additional DeepEval metrics (HallucinationMetric, custom GEval) applied on top of RAGAS |
| R6 | Diagnostic report | Output showing retrieval vs. generation scores with root cause classification per question |

### Dataset Coverage Requirements

Your 10 evaluation cases must include:
- **3 vacation policy questions** (days allowed, rollover rules, approval process)
- **3 expense policy questions** (meal limits, travel reimbursement, home office budget)
- **2 remote work policy questions** (eligibility, equipment allowance)
- **2 cross-topic questions** (e.g., "Can remote workers expense home office furniture?" spans both policies)

---

## Step-by-Step Build Guide

### Step 1: Create the HR Policy Corpus

Create `datasets/hr_policies.json` — this is the document store the RAG agent retrieves from:

```json
[
  {
    "id": "VAC-001",
    "title": "Vacation Policy — Annual Allowance",
    "content": "Full-time employees receive 20 vacation days per year. Vacation days accrue monthly at a rate of 1.67 days per month. New employees are eligible after 90 days of employment. Part-time employees receive prorated vacation based on hours worked.",
    "category": "vacation",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "VAC-002",
    "title": "Vacation Policy — Rollover and Carryover",
    "content": "Employees may carry over a maximum of 5 unused vacation days to the next calendar year. Carried-over days must be used by March 31. Days exceeding the 5-day carryover limit are forfeited on December 31. Managers must approve all vacation requests at least 2 weeks in advance.",
    "category": "vacation",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "EXP-001",
    "title": "Expense Policy — Meal Reimbursement",
    "content": "Business meal expenses are reimbursed up to $75 per person per meal. Receipts are required for all meals over $25. Alcohol is not reimbursable. Tips up to 20% are included in the reimbursable amount. Meal expenses must be submitted within 30 days.",
    "category": "expenses",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "EXP-002",
    "title": "Expense Policy — Travel Reimbursement",
    "content": "Business travel expenses including flights, hotels, and ground transportation are reimbursable with manager pre-approval. Hotel rates are capped at $250 per night in standard markets and $350 per night in high-cost cities (NYC, SF, London). Economy class flights are standard; business class requires VP approval for flights over 6 hours.",
    "category": "expenses",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "EXP-003",
    "title": "Expense Policy — Home Office Equipment",
    "content": "Remote employees may expense home office equipment up to $500 per calendar year. Eligible items include monitors, keyboards, mice, desk chairs, and standing desks. Laptops and phones are provided by IT and are not part of this allowance. Receipts and photos of the setup are required for reimbursement.",
    "category": "expenses",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "REM-001",
    "title": "Remote Work Policy — Eligibility",
    "content": "Employees in eligible roles may work remotely up to 3 days per week after completing 6 months of employment. Fully remote positions require Director-level approval. All remote workers must be available during core hours (10 AM - 3 PM local time) and attend mandatory in-office days as scheduled by their team.",
    "category": "remote_work",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "REM-002",
    "title": "Remote Work Policy — Equipment and Connectivity",
    "content": "Remote employees are responsible for maintaining a reliable internet connection with minimum 50 Mbps download speed. The company provides a laptop, VPN access, and collaboration tools. Home office equipment is covered under the Home Office Equipment expense policy (up to $500/year). Internet service costs are not reimbursable.",
    "category": "remote_work",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  },
  {
    "id": "BEN-001",
    "title": "Benefits — Health Insurance",
    "content": "Full-time employees are eligible for health insurance starting the first of the month following 30 days of employment. The company covers 80% of individual premiums and 60% of family premiums. Three plan options are available: HMO, PPO, and HDHP with HSA. Open enrollment occurs annually in November.",
    "category": "benefits",
    "version": "2024-Q4",
    "effective_date": "2024-10-01"
  }
]
```

### Step 2: Create the RAG Evaluation Dataset

Create `datasets/rag_eval_dataset.json`:

```json
[
  {
    "question": "How many vacation days do full-time employees get per year?",
    "ground_truth": "Full-time employees receive 20 vacation days per year.",
    "reference_contexts": ["VAC-001"],
    "category": "vacation"
  },
  {
    "question": "How many vacation days can I carry over to next year?",
    "ground_truth": "Employees may carry over a maximum of 5 unused vacation days to the next calendar year, which must be used by March 31.",
    "reference_contexts": ["VAC-002"],
    "category": "vacation"
  },
  {
    "question": "When are new employees eligible to take vacation?",
    "ground_truth": "New employees are eligible for vacation after 90 days of employment.",
    "reference_contexts": ["VAC-001"],
    "category": "vacation"
  },
  {
    "question": "What is the meal reimbursement limit per person?",
    "ground_truth": "Business meal expenses are reimbursed up to $75 per person per meal.",
    "reference_contexts": ["EXP-001"],
    "category": "expenses"
  },
  {
    "question": "What is the hotel rate cap for New York City?",
    "ground_truth": "Hotel rates are capped at $350 per night in high-cost cities including NYC.",
    "reference_contexts": ["EXP-002"],
    "category": "expenses"
  },
  {
    "question": "How much can I expense for home office equipment?",
    "ground_truth": "Remote employees may expense home office equipment up to $500 per calendar year.",
    "reference_contexts": ["EXP-003"],
    "category": "expenses"
  },
  {
    "question": "How many days per week can I work remotely?",
    "ground_truth": "Employees in eligible roles may work remotely up to 3 days per week after completing 6 months of employment.",
    "reference_contexts": ["REM-001"],
    "category": "remote_work"
  },
  {
    "question": "What internet speed is required for remote work?",
    "ground_truth": "Remote employees must maintain a reliable internet connection with minimum 50 Mbps download speed.",
    "reference_contexts": ["REM-002"],
    "category": "remote_work"
  },
  {
    "question": "Can remote workers expense home office furniture and how much?",
    "ground_truth": "Remote employees may expense home office equipment including desk chairs and standing desks up to $500 per calendar year under the Home Office Equipment expense policy.",
    "reference_contexts": ["EXP-003", "REM-002"],
    "category": "cross_topic"
  },
  {
    "question": "If I start working in January, when can I take my first vacation and what equipment will be provided?",
    "ground_truth": "New employees are eligible for vacation after 90 days of employment (April). The company provides a laptop, VPN access, and collaboration tools. Home office equipment can be expensed up to $500/year.",
    "reference_contexts": ["VAC-001", "REM-002", "EXP-003"],
    "category": "cross_topic"
  }
]
```

### Step 3: Build the Simulated RAG Agent

Create `agents/rag_agent.py`:

```python
"""
RAG Agent — HR Policy Q&A Bot (simulated for evaluation).

Retrieves relevant policy chunks and generates answers.
Used in: Module 05 (Project 2), Module 14 (Capstone)
"""

import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Load the policy corpus
POLICIES_PATH = Path(__file__).parent.parent / "datasets" / "hr_policies.json"


def load_policies() -> list[dict]:
    """Load the HR policy document corpus."""
    with open(POLICIES_PATH) as f:
        return json.load(f)


def retrieve_contexts(query: str, top_k: int = 3) -> list[str]:
    """
    Simulate retrieval by keyword matching.

    In production, this would be a vector similarity search.
    For evaluation purposes, this simulates imperfect retrieval
    (sometimes returning irrelevant or incomplete contexts).
    """
    policies = load_policies()
    query_lower = query.lower()

    scored = []
    for policy in policies:
        content_lower = policy["content"].lower()
        title_lower = policy["title"].lower()

        # Simple keyword overlap scoring
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        overlap = len(query_words & content_words)

        # Boost for title matches
        title_words = set(title_lower.split())
        title_overlap = len(query_words & title_words)

        score = overlap + (title_overlap * 3)
        scored.append((score, policy))

    # Sort by score descending, return top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p["content"] for _, p in scored[:top_k]]


def generate_answer(query: str, contexts: list[str]) -> str:
    """Generate an answer from the retrieved contexts."""
    context_text = "\n\n".join(
        f"[Policy Document {i+1}]:\n{ctx}" for i, ctx in enumerate(contexts)
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an HR policy assistant. Answer the employee's "
                    "question based ONLY on the provided policy documents. "
                    "If the answer is not in the documents, say so. "
                    "Be specific with numbers and dates."
                ),
            },
            {
                "role": "user",
                "content": f"Policy Documents:\n{context_text}\n\nQuestion: {query}",
            },
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content


def run_rag_agent(query: str) -> dict:
    """
    Run the full RAG pipeline: retrieve then generate.

    Returns:
        dict with keys: answer, contexts, query
    """
    contexts = retrieve_contexts(query)
    answer = generate_answer(query, contexts)
    return {
        "query": query,
        "answer": answer,
        "contexts": contexts,
    }


if __name__ == "__main__":
    result = run_rag_agent("How many vacation days do I get per year?")
    print(f"Answer: {result['answer']}")
    print(f"Contexts retrieved: {len(result['contexts'])}")
```

### Step 4: Build the RAGAS Evaluation Pipeline

Create `tests/project2/test_rag_eval.py`:

```python
"""
Project 2 — Enterprise RAG Agent Evaluation

Evaluates the HR Policy RAG agent using RAGAS metrics for retrieval
quality and DeepEval metrics for generation quality.

Run with: pytest tests/project2/test_rag_eval.py -v
"""

import json
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
)

load_dotenv()

# Import the RAG agent
from agents.rag_agent import run_rag_agent, load_policies

# ---------------------------------------------------------------------------
# Load evaluation dataset
# ---------------------------------------------------------------------------

DATASET_PATH = Path(__file__).parent.parent.parent / "datasets" / "rag_eval_dataset.json"
POLICIES_PATH = Path(__file__).parent.parent.parent / "datasets" / "hr_policies.json"


def load_eval_dataset() -> list[dict]:
    with open(DATASET_PATH) as f:
        return json.load(f)


def get_policy_content(policy_id: str) -> str:
    """Look up policy content by ID."""
    policies = load_policies()
    for p in policies:
        if p["id"] == policy_id:
            return p["content"]
    return ""


# ---------------------------------------------------------------------------
# RAGAS Evaluation (all cases at once)
# ---------------------------------------------------------------------------

class TestRAGASMetrics:
    """Evaluate retrieval and generation quality using RAGAS."""

    def test_ragas_full_evaluation(self):
        """Run RAGAS evaluation across all dataset cases."""
        eval_data = load_eval_dataset()

        questions = []
        answers = []
        contexts = []
        ground_truths = []

        for case in eval_data:
            result = run_rag_agent(case["question"])
            questions.append(case["question"])
            answers.append(result["answer"])
            contexts.append(result["contexts"])
            ground_truths.append(case["ground_truth"])

        # Build RAGAS-compatible dataset
        ds = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })

        # Run RAGAS evaluation
        result = evaluate(
            ds,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )

        # Assert thresholds
        scores = result.to_pandas().mean()

        print("\n" + "=" * 60)
        print("  RAGAS EVALUATION RESULTS")
        print("=" * 60)

        thresholds = {
            "faithfulness": 0.8,
            "answer_relevancy": 0.7,
            "context_precision": 0.7,
            "context_recall": 0.7,
        }

        all_passed = True
        for metric_name, threshold in thresholds.items():
            score = scores.get(metric_name, 0)
            passed = score >= threshold
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {metric_name}: {score:.3f} (threshold: {threshold})")
            if not passed:
                all_passed = False

        # Classify root cause
        retrieval_score = (
            scores.get("context_precision", 0) + scores.get("context_recall", 0)
        ) / 2
        generation_score = (
            scores.get("faithfulness", 0) + scores.get("answer_relevancy", 0)
        ) / 2

        print(f"\n  Retrieval Quality: {retrieval_score:.3f}")
        print(f"  Generation Quality: {generation_score:.3f}")

        if retrieval_score < 0.7 and generation_score < 0.7:
            print("  Root Cause: BOTH retrieval and generation need improvement")
        elif retrieval_score < 0.7:
            print("  Root Cause: RETRIEVAL — agent is fetching wrong/incomplete contexts")
        elif generation_score < 0.7:
            print("  Root Cause: GENERATION — agent has correct context but generates poorly")
        else:
            print("  Root Cause: None — pipeline is performing well")

        print("=" * 60)

        assert all_passed, "One or more RAGAS metrics below threshold"


# ---------------------------------------------------------------------------
# DeepEval Quality Layer (per-case)
# ---------------------------------------------------------------------------

deepeval_relevancy = AnswerRelevancyMetric(
    threshold=0.7,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)
deepeval_faithfulness = FaithfulnessMetric(
    threshold=0.8,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)
deepeval_hallucination = HallucinationMetric(
    threshold=0.3,
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
)

eval_cases = load_eval_dataset()


@pytest.mark.parametrize(
    "case",
    eval_cases,
    ids=[f"{c['category']}_{c['question'][:35]}" for c in eval_cases],
)
class TestDeepEvalRAGQuality:
    """Evaluate per-case RAG quality using DeepEval."""

    def test_rag_answer_relevancy(self, case):
        """RAG answer should be relevant to the question."""
        result = run_rag_agent(case["question"])
        tc = LLMTestCase(
            input=case["question"],
            actual_output=result["answer"],
            expected_output=case["ground_truth"],
            retrieval_context=result["contexts"],
        )
        assert_test(tc, [deepeval_relevancy])

    def test_rag_faithfulness(self, case):
        """RAG answer should be grounded in retrieved contexts."""
        result = run_rag_agent(case["question"])
        tc = LLMTestCase(
            input=case["question"],
            actual_output=result["answer"],
            retrieval_context=result["contexts"],
        )
        assert_test(tc, [deepeval_faithfulness])

    def test_rag_no_hallucination(self, case):
        """RAG answer should not hallucinate beyond retrieved contexts."""
        result = run_rag_agent(case["question"])
        tc = LLMTestCase(
            input=case["question"],
            actual_output=result["answer"],
            context=result["contexts"],
        )
        assert_test(tc, [deepeval_hallucination])
```

### Step 5: Build the Diagnostic Report Generator

Create `tests/project2/generate_rag_report.py`:

```python
"""
Project 2 — RAG Diagnostic Report Generator

Produces a comprehensive retrieval vs. generation quality report.

Usage: python tests/project2/generate_rag_report.py
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agents.rag_agent import run_rag_agent, load_policies


DATASET_PATH = Path(__file__).parent.parent.parent / "datasets" / "rag_eval_dataset.json"


def load_eval_dataset():
    with open(DATASET_PATH) as f:
        return json.load(f)


def get_policy_content(policy_id, policies):
    for p in policies:
        if p["id"] == policy_id:
            return p["content"]
    return ""


def generate_report():
    """Generate the retrieval vs. generation diagnostic report."""
    print("=" * 70)
    print("  PROJECT 2 — RAG DIAGNOSTIC REPORT")
    print("  HR Policy Q&A Bot Evaluation")
    print("=" * 70)

    eval_data = load_eval_dataset()
    policies = load_policies()

    print(f"\nDataset: {len(eval_data)} questions")
    print(f"Policy corpus: {len(policies)} documents")
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")

    retrieval_hits = 0
    generation_correct = 0
    total = len(eval_data)

    for i, case in enumerate(eval_data):
        result = run_rag_agent(case["question"])

        # Check retrieval: did we get the right documents?
        expected_contents = [
            get_policy_content(pid, policies)
            for pid in case["reference_contexts"]
        ]
        retrieved = result["contexts"]

        retrieval_hit = all(
            any(exp in ctx for ctx in retrieved)
            for exp in expected_contents
            if exp
        )
        if retrieval_hit:
            retrieval_hits += 1

        # Simple generation check: does the answer contain key facts?
        gt_lower = case["ground_truth"].lower()
        answer_lower = result["answer"].lower()

        # Extract key numbers/facts from ground truth
        import re
        numbers = re.findall(r'\d+', gt_lower)
        number_match = all(n in answer_lower for n in numbers) if numbers else True

        if number_match and retrieval_hit:
            generation_correct += 1

        status_r = "HIT" if retrieval_hit else "MISS"
        status_g = "OK" if number_match else "ERR"

        print(f"\n{'─' * 70}")
        print(f"  Q{i+1} [{case['category']}]: {case['question']}")
        print(f"  Retrieval: [{status_r}] | Generation: [{status_g}]")
        print(f"  Expected docs: {case['reference_contexts']}")
        print(f"  Answer preview: {result['answer'][:120]}...")

    print(f"\n{'=' * 70}")
    print(f"  SUMMARY")
    print(f"{'─' * 70}")
    print(f"  Retrieval Accuracy: {retrieval_hits}/{total} ({retrieval_hits/total:.0%})")
    print(f"  Generation Accuracy: {generation_correct}/{total} ({generation_correct/total:.0%})")

    if retrieval_hits / total < 0.7 and generation_correct / total < 0.7:
        diagnosis = "BOTH — Improve retrieval (embeddings, chunking) AND generation (prompt, grounding)"
    elif retrieval_hits / total < 0.7:
        diagnosis = "RETRIEVAL — Focus on improving document chunking, embedding model, and retrieval strategy"
    elif generation_correct / total < 0.7:
        diagnosis = "GENERATION — Retrieval is adequate; improve the generation prompt and grounding instructions"
    else:
        diagnosis = "HEALTHY — Both retrieval and generation are performing acceptably"

    print(f"  Diagnosis: {diagnosis}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    generate_report()
```

### Step 6: Run the Evaluation

```bash
# Run RAGAS + DeepEval evaluation
pytest tests/project2/test_rag_eval.py -v --tb=short

# Generate the diagnostic report
python tests/project2/generate_rag_report.py
```

### Step 7: Analyze Results

For each failing case, determine:
1. Did the retriever fetch the correct policy document(s)?
2. If yes, did the generator faithfully use the information?
3. If the retriever missed, what went wrong with the keyword/embedding match?
4. Write 2–3 sentences of remediation advice per failure category

---

## Expected Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| D1 | HR policy corpus | `datasets/hr_policies.json` (8 policy documents) |
| D2 | RAG evaluation dataset | `datasets/rag_eval_dataset.json` (10 questions) |
| D3 | RAG agent | `agents/rag_agent.py` |
| D4 | RAGAS + DeepEval test file | `tests/project2/test_rag_eval.py` |
| D5 | Diagnostic report script | `tests/project2/generate_rag_report.py` |
| D6 | Report output | Console output showing retrieval vs. generation breakdown |

---

## Evaluation Rubric

| Dimension | 5 (Excellent) | 3 (Adequate) | 1 (Needs Work) |
|-----------|--------------|--------------|-----------------|
| **Dataset Quality** | 10 questions spanning all policy areas with precise ground truths and correct reference contexts | 10 questions but some ground truths are vague or references incomplete | Fewer than 10 questions or missing categories |
| **RAGAS Integration** | All 4 RAGAS metrics computed and threshold-checked with clear output | RAGAS runs but thresholds not verified or only 2 metrics used | RAGAS not integrated or crashes |
| **DeepEval Layer** | Per-case DeepEval metrics complement RAGAS with hallucination checks | DeepEval metrics run but not connected to RAGAS flow | DeepEval not used |
| **Diagnostic Clarity** | Report clearly separates retrieval vs. generation scores with root cause per case | Report shows aggregate scores but no per-case breakdown | No diagnostic output |
| **Remediation Advice** | Specific, actionable recommendations for each failure type | General recommendations | No recommendations |

**Scoring:** 20+ = Excellent | 15–19 = Good | 10–14 = Adequate | Below 10 = Revisit

---

## Extension Ideas

1. **Real vector store** — Replace the keyword-based retriever with ChromaDB and `text-embedding-3-small` to see how embedding-based retrieval changes scores
2. **Chunk size experiment** — Split policies into different chunk sizes (100, 250, 500 tokens) and measure how context_precision and context_recall change
3. **Adversarial questions** — Add 5 questions designed to trick the RAG pipeline (e.g., questions whose answer spans 3+ documents, or questions about policies that don't exist)
4. **RAGAS per-question scores** — Extract per-row RAGAS scores (not just averages) and create a CSV report showing which specific questions fail on which metrics
5. **Version comparison** — Evaluate the same questions against two different system prompts and compare quality scores side-by-side

---

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: No module named 'datasets'` | Run `pip install datasets` (HuggingFace datasets library, required by RAGAS) |
| RAGAS returns NaN scores | Ensure `ground_truth` is provided for all cases (required for `context_recall`) |
| Low context_recall despite correct docs | Your ground truth may be phrased differently than the policy; RAGAS checks semantic overlap |
| DeepEval and RAGAS disagree on faithfulness | They use different algorithms; note both scores in your report |
| Retrieval returns wrong docs | The keyword-based retriever is intentionally imperfect; this is what you are measuring |

---

## What You Learned

After completing this project, you can tell an interviewer:

> "I built a RAG evaluation pipeline that separately measures retrieval quality (context precision, context recall) and generation quality (faithfulness, answer relevancy) using RAGAS and DeepEval. I diagnosed a production HR chatbot's failures and determined whether the root cause was in the retrieval stage, the generation stage, or both — providing specific remediation recommendations for each failure type."

**Next Project:** [Project 3 — Test a Multi-Tool Agent](../project-3-tool-calling/README.md) (Module 06)
