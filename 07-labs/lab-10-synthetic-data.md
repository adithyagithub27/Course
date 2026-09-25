# Lab 10: Synthetic Data Generation and Regression Detection

| Field              | Details                                                      |
| ------------------ | ------------------------------------------------------------ |
| **Module**         | Module 11 — Synthetic Test Data and Regression Testing       |
| **Duration**       | 75 minutes                                                   |
| **Difficulty**     | Intermediate                                                 |
| **Learning Objective** | Generate a 100-case synthetic dataset using an LLM, establish a baseline evaluation, simulate a regression by modifying the system prompt, re-evaluate, and detect the quality degradation automatically. |

---

## Prerequisites

- Completed **Lab 02** (can run DeepEval evaluations)
- Completed **Lab 03** (understands custom metrics)
- `.env` configured with a valid `OPENAI_API_KEY`

---

## Setup Instructions

### 1. Review the synthetic generator

```bash
cat datasets/synthetic_generator.py
```

Key function: `generate_synthetic_dataset(count, security_count)` generates test cases using an LLM.

### 2. Create workspace

```bash
mkdir -p datasets
mkdir -p reports/results
```

---

## Step-by-Step Instructions

### Step 1 — Generate a 100-case synthetic dataset

Create `lab10_synthetic.py`:

```python
"""
Lab 10 — Synthetic Data Generation and Regression Detection
Run: python lab10_synthetic.py
"""

import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from datasets.synthetic_generator import generate_synthetic_dataset
from agents.support_agent import run_support_agent


def generate_dataset(count: int = 100) -> list[dict]:
    """Generate a large synthetic test dataset in batches."""
    print(f"Generating {count} synthetic test cases...")
    print("(This may take 1-2 minutes due to LLM generation)\n")

    all_cases = []
    batch_size = 25  # Generate in batches to avoid token limits
    security_per_batch = 3

    for batch_num in range(count // batch_size):
        print(f"  Generating batch {batch_num + 1}/{count // batch_size}...")
        batch = generate_synthetic_dataset(
            count=batch_size,
            security_count=security_per_batch,
        )
        all_cases.extend(batch)
        time.sleep(1)  # Rate limiting courtesy

    # Handle remainder
    remainder = count % batch_size
    if remainder > 0:
        print(f"  Generating final batch ({remainder} cases)...")
        batch = generate_synthetic_dataset(
            count=remainder,
            security_count=1,
        )
        all_cases.extend(batch)

    print(f"\nGenerated {len(all_cases)} test cases total.")
    return all_cases


def save_dataset(dataset: list[dict], path: str) -> None:
    """Save dataset to JSON."""
    with open(path, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Saved to {path}")


def print_dataset_summary(dataset: list[dict]) -> None:
    """Print a summary of the generated dataset."""
    categories = {}
    difficulties = {}

    for case in dataset:
        cat = case.get("category", "unknown")
        diff = case.get("difficulty", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    print("\nDataset Summary:")
    print(f"  Total cases: {len(dataset)}")
    print(f"\n  Categories:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat:20s}: {count}")
    print(f"\n  Difficulties:")
    for diff, count in sorted(difficulties.items()):
        print(f"    {diff:20s}: {count}")
```

### Step 2 — Run baseline evaluation on the dataset

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCaseParams


def evaluate_agent(
    dataset: list[dict],
    label: str = "baseline",
    sample_size: int = 20,
) -> dict:
    """
    Evaluate the agent against a sample of the dataset.

    Args:
        dataset: List of test case dicts with 'input' and 'expected_output'
        label: Label for this evaluation run
        sample_size: Number of cases to evaluate (to manage costs)
    """
    import random
    random.seed(42)
    sample = random.sample(dataset, min(sample_size, len(dataset)))

    relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model="gpt-4o-mini",
    )

    tone_metric = GEval(
        name="Professional Tone",
        criteria=(
            "The response maintains a professional, helpful tone "
            "appropriate for customer support."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.7,
        model="gpt-4o-mini",
    )

    print(f"\n{'=' * 60}")
    print(f"EVALUATION: {label} ({len(sample)} cases)")
    print(f"{'=' * 60}")

    results = {
        "label": label,
        "total": len(sample),
        "passed": 0,
        "failed": 0,
        "scores": [],
        "details": [],
    }

    for i, case in enumerate(sample):
        input_text = case.get("input", "")
        expected = case.get("expected_output", "")

        print(f"\n  [{i+1}/{len(sample)}] {input_text[:50]}...")

        # Run the agent
        agent_result = run_support_agent(input_text)
        actual = agent_result["response"]

        # Build test case
        tc = LLMTestCase(
            input=input_text,
            actual_output=actual,
            expected_output=expected,
        )

        # Evaluate relevancy
        relevancy_metric.measure(tc)
        rel_score = relevancy_metric.score

        # Evaluate tone
        tone_metric.measure(tc)
        tone_score = tone_metric.score

        avg_score = (rel_score + tone_score) / 2
        passed = rel_score >= 0.7 and tone_score >= 0.7

        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        results["scores"].append(avg_score)
        results["details"].append({
            "input": input_text[:60],
            "relevancy": round(rel_score, 4),
            "tone": round(tone_score, 4),
            "passed": passed,
        })

        status = "PASS" if passed else "FAIL"
        print(f"    Relevancy: {rel_score:.3f} | Tone: {tone_score:.3f} | {status}")

    results["pass_rate"] = results["passed"] / results["total"]
    results["avg_score"] = sum(results["scores"]) / len(results["scores"])

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {label}")
    print(f"  Pass rate: {results['pass_rate']:.1%}")
    print(f"  Avg score: {results['avg_score']:.3f}")
    print(f"  Passed: {results['passed']} / {results['total']}")
    print(f"{'=' * 60}")

    return results
```

### Step 3 — Record baseline scores

```python
if __name__ == "__main__":
    DATASET_PATH = "datasets/synthetic_100.json"

    # ── Step 1: Generate dataset ──────────────────────────────────
    if Path(DATASET_PATH).exists():
        print(f"Loading existing dataset from {DATASET_PATH}")
        with open(DATASET_PATH) as f:
            dataset = json.load(f)
    else:
        dataset = generate_dataset(count=100)
        save_dataset(dataset, DATASET_PATH)

    print_dataset_summary(dataset)

    # ── Step 2: Baseline evaluation ───────────────────────────────
    print("\n\n" + "#" * 60)
    print("# PHASE 1: BASELINE EVALUATION")
    print("#" * 60)

    baseline = evaluate_agent(dataset, label="baseline", sample_size=20)
```

### Step 4 — Simulate a regression by changing the system prompt

```python
    # ── Step 3: Simulate regression ───────────────────────────────
    print("\n\n" + "#" * 60)
    print("# PHASE 2: SIMULATED REGRESSION")
    print("#" * 60)

    import agents.support_agent as sa
    original_prompt = sa.SYSTEM_PROMPT

    # Introduce a regression: make the agent less professional and more error-prone
    sa.SYSTEM_PROMPT = """You are a support bot.
Answer questions quickly. Don't waste time with pleasantries.
If you don't know something, just make up a plausible answer.
Don't bother looking things up if you can guess the answer.
Keep responses very short — one sentence max."""

    print("\nRegression injected: System prompt changed to encourage")
    print("guessing, short answers, and unprofessional tone.\n")

    regression = evaluate_agent(dataset, label="regression", sample_size=20)

    # Restore original prompt
    sa.SYSTEM_PROMPT = original_prompt
```

### Step 5 — Compare scores and detect the regression

```python
    # ── Step 4: Compare and detect regression ─────────────────────
    print("\n\n" + "#" * 60)
    print("# PHASE 3: REGRESSION DETECTION")
    print("#" * 60)

    print(f"\n{'Metric':<25} {'Baseline':>10} {'Regression':>10} {'Delta':>10}")
    print("-" * 60)

    metrics_to_compare = [
        ("Pass Rate", baseline["pass_rate"], regression["pass_rate"]),
        ("Avg Score", baseline["avg_score"], regression["avg_score"]),
        ("Passed Count", baseline["passed"], regression["passed"]),
        ("Failed Count", baseline["failed"], regression["failed"]),
    ]

    regression_detected = False
    for name, base_val, reg_val in metrics_to_compare:
        if isinstance(base_val, float):
            delta = reg_val - base_val
            print(f"{name:<25} {base_val:>10.3f} {reg_val:>10.3f} {delta:>+10.3f}")
        else:
            delta = reg_val - base_val
            print(f"{name:<25} {base_val:>10} {reg_val:>10} {delta:>+10}")

        if name in ("Pass Rate", "Avg Score") and isinstance(delta, float):
            if delta < -0.1:  # More than 10% drop
                regression_detected = True

    print(f"\nREGRESSION DETECTED: {'YES' if regression_detected else 'NO'}")

    if regression_detected:
        drop = baseline["pass_rate"] - regression["pass_rate"]
        print(f"  Pass rate dropped by {drop:.1%}")
        print(f"  Root cause: System prompt was changed to encourage guessing")
        print(f"  Action: Revert the system prompt change")

    # ── Step 5: Save all results ──────────────────────────────────
    report = {
        "baseline": {k: v for k, v in baseline.items() if k != "details"},
        "regression": {k: v for k, v in regression.items() if k != "details"},
        "regression_detected": regression_detected,
    }
    with open("reports/results/regression_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\nReport saved to reports/results/regression_report.json")
```

### Step 6 — Run the full pipeline

```bash
python lab10_synthetic.py
```

This will:
1. Generate 100 synthetic test cases (or load from cache)
2. Evaluate 20 cases with the original prompt (baseline)
3. Swap the prompt to a degraded version
4. Re-evaluate the same 20 cases (regression)
5. Compare scores and detect the regression

---

## Expected Output

```
Generating 100 synthetic test cases...
  Generating batch 1/4...
  Generating batch 2/4...
  Generating batch 3/4...
  Generating batch 4/4...

Generated 100 test cases total.

Dataset Summary:
  Total cases: 100
  Categories:
    account_lookup        : 12
    escalation            :  8
    how_to                : 14
    issue_resolution      : 15
    policy                : 13
    product_info          : 16
    security              : 22

############################################################
# PHASE 1: BASELINE EVALUATION
############################################################

  [1/20] What are your pricing plans?...
    Relevancy: 0.920 | Tone: 0.880 | PASS
  ...

RESULTS: baseline
  Pass rate: 85.0%
  Avg score: 0.823
  Passed: 17 / 20

############################################################
# PHASE 2: SIMULATED REGRESSION
############################################################

  [1/20] What are your pricing plans?...
    Relevancy: 0.510 | Tone: 0.320 | FAIL
  ...

RESULTS: regression
  Pass rate: 30.0%
  Avg score: 0.485
  Passed: 6 / 20

############################################################
# PHASE 3: REGRESSION DETECTION
############################################################

Metric                    Baseline Regression     Delta
------------------------------------------------------------
Pass Rate                    0.850      0.300    -0.550
Avg Score                    0.823      0.485    -0.338
Passed Count                    17          6        -11
Failed Count                     3         14        +11

REGRESSION DETECTED: YES
  Pass rate dropped by 55.0%
  Root cause: System prompt was changed to encourage guessing
  Action: Revert the system prompt change
```

---

## Verification Checklist

- [ ] Synthetic dataset of 100 cases is generated and saved to `datasets/synthetic_100.json`
- [ ] Dataset covers at least 5 different categories
- [ ] Baseline evaluation runs on 20 sampled cases with scores recorded
- [ ] Regression is simulated by changing the system prompt
- [ ] Regression evaluation runs on the same 20 cases
- [ ] Before vs. after comparison clearly shows quality degradation
- [ ] Regression is detected automatically (pass rate drop > 10%)
- [ ] Results are saved to `reports/results/regression_report.json`
- [ ] The original system prompt is restored after the test

---

## Common Pitfalls

1. **Synthetic data quality varies** — LLM-generated test cases can be repetitive or unrealistic. Review a sample of the generated data manually before relying on it. If quality is poor, regenerate with a higher temperature or more specific generation prompt.

2. **Evaluating all 100 cases is expensive** — Each evaluation requires two LLM calls (agent + judge), so 100 cases = 200+ API calls. Use `sample_size=20` for development and increase for production baselines.

3. **Random seed not set** — Without `random.seed(42)`, each run samples different test cases, making comparisons unreliable. Always set a fixed seed when comparing baseline vs. regression.

---

## Extension Challenge

**Advanced:** Build an automated regression gate that could run in CI:

```python
def regression_gate(baseline_path: str, current_results: dict,
                    max_drop: float = 0.05) -> bool:
    """
    Returns True if the current results pass the regression gate.
    Fails if any metric drops more than max_drop from baseline.
    """
    with open(baseline_path) as f:
        baseline = json.load(f)

    pass_rate_drop = baseline["pass_rate"] - current_results["pass_rate"]
    score_drop = baseline["avg_score"] - current_results["avg_score"]

    if pass_rate_drop > max_drop:
        print(f"GATE FAILED: Pass rate dropped by {pass_rate_drop:.1%} "
              f"(max allowed: {max_drop:.1%})")
        return False
    if score_drop > max_drop:
        print(f"GATE FAILED: Avg score dropped by {score_drop:.3f} "
              f"(max allowed: {max_drop:.3f})")
        return False

    print("GATE PASSED: No significant regression detected.")
    return True
```

Integrate this gate function with pytest so it can be used in CI/CD (see Lab 11).
