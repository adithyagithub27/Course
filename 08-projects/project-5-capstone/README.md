# Project 5 (Capstone): Build an Enterprise AI Agent Quality Platform

> **"The VP asks: 'Is this agent safe and reliable enough for production?' Build the platform that answers definitively."**

| Detail | Value |
|--------|-------|
| **Module Reference** | Module 14 — Capstone Project |
| **Difficulty** | Advanced |
| **Estimated Time** | 2–3 hours |
| **Prerequisites** | All prior modules (00–13) and Projects 1–4 |

---

## Enterprise Scenario

**TechCorp — Production Readiness Assessment for Customer Support Agent**

TechCorp's customer support agent has passed individual quality checks in Projects 1–4. Now the VP of Engineering needs a single, comprehensive answer:

> **"Is this agent safe and reliable enough for production?"**

To answer this, you need:
- A unified test harness that orchestrates all evaluation categories
- Quantified quality across functional correctness, LLM quality, RAG accuracy, tool-calling precision, and security
- A single aggregated quality score with weighted category contributions
- A visual dashboard for stakeholders who won't read pytest output
- A CI/CD pipeline that gates deployments on quality thresholds
- Production observability to monitor the agent post-launch

**You are building the complete quality platform — the same kind of system a senior AI quality engineer would build at a real company.** This is your portfolio piece.

---

## Learning Objectives

By completing this capstone, you will be able to:

1. **Design a multi-category evaluation harness** that orchestrates functional tests, LLM quality metrics, RAG evaluation, tool-calling validation, and security scanning
2. **Aggregate quality scores** across categories with configurable weights to produce a single production-readiness score
3. **Build a Streamlit dashboard** that visualizes evaluation results for non-technical stakeholders
4. **Configure a GitHub Actions CI/CD pipeline** that gates deployments on quality thresholds
5. **Integrate Langfuse observability** for post-deployment monitoring of agent quality in production

---

## Prerequisites

Before starting this capstone, ensure you have completed:

- [ ] **Project 1** — Customer support agent evaluation (DeepEval basics)
- [ ] **Project 2** — RAG evaluation (RAGAS metrics)
- [ ] **Project 3** — Tool-calling validation (multi-tool testing)
- [ ] **Project 4** — Red team assessment (security testing)
- [ ] **Module 09** — Observability with Langfuse
- [ ] **Module 10** — Performance benchmarking
- [ ] **Module 11** — Synthetic data generation
- [ ] **Module 12** — CI/CD pipelines for evaluation
- [ ] **Module 13** — Enterprise governance

All tools installed and verified:

```bash
# Verify all tools
python --version          # 3.11+
deepeval --version        # 3.9+
promptfoo --version       # latest
streamlit --version       # 1.35+
```

**Required environment variables** (set in your `.env` file):

```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Optional (for Langfuse observability)
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# Evaluation configuration
EVAL_PASS_THRESHOLD=0.7
EVAL_SECURITY_THRESHOLD=0.9
```

---

## Architecture Diagram

```
+====================================================================+
||                  ENTERPRISE QUALITY PLATFORM                      ||
+====================================================================+

              AI Agent Under Test
           (agents/support_agent.py)
                      |
                      v
          +------------------------+
          |     TEST HARNESS       |
          |   (harness/runner.py)  |
          |                        |
          |  Orchestrates all      |
          |  evaluation categories |
          +------------------------+
                      |
     +----------------+----------------+----------------+
     |                |                |                |
     v                v                v                v
+-----------+  +-----------+  +-----------+  +-----------+
| FUNCTIONAL|  | LLM EVAL  |  | RAG EVAL  |  | TOOL EVAL |
| TESTS     |  | METRICS   |  | METRICS   |  | METRICS   |
|           |  |           |  |           |  |           |
| 10+ cases |  | Relevancy |  | Context   |  | Selection |
| Happy     |  | Faithful  |  | Precision |  | Arguments |
| Edge      |  | Hallucin. |  | Recall    |  | Errors    |
| Error     |  | Custom    |  | Faithful  |  | Authz     |
+-----------+  +-----------+  +-----------+  +-----------+
     |                |                |                |
     +--------+-------+--------+-------+--------+------+
              |                |                |
              v                v                v
       +-----------+    +-----------+    +-------------+
       | SECURITY  |    | PERFORM.  |    | OBSERV.     |
       | RED TEAM  |    | BENCHMARK |    | LANGFUSE    |
       |           |    |           |    |             |
       | promptfoo |    | Latency   |    | Traces      |
       | 10+ atks  |    | Cost      |    | Scores      |
       | 5 categs  |    | LLM calls |    | Monitoring  |
       +-----------+    +-----------+    +-------------+
              |                |                |
              +--------+-------+--------+-------+
                       |                |
                       v                v
            +-------------------+  +------------------+
            | QUALITY SCORE     |  | QUALITY SCORECARD|
            | AGGREGATION       |  | (Markdown Report)|
            |                   |  |                  |
            | Weighted avg:     |  | Per-category     |
            | Functional: 25%   |  | breakdown with   |
            | LLM Quality: 20%  |  | scores, verdicts,|
            | RAG: 15%          |  | and gate status  |
            | Tool Calling: 15% |  +------------------+
            | Security: 20%     |
            | Performance: 5%   |
            +-------------------+
                       |
                       v
            +-------------------+
            | STREAMLIT         |
            | DASHBOARD         |
            |                   |
            | Overall score     |
            | Category cards    |
            | Test case table   |
            | Trend charts      |
            +-------------------+
                       |
                       v
            +-------------------+
            | GITHUB ACTIONS    |
            | CI/CD PIPELINE    |
            |                   |
            | On push/PR:       |
            | 1. Run all evals  |
            | 2. Check gates    |
            | 3. Generate report|
            | 4. Upload results |
            +-------------------+
```

> See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full system design, data flow diagrams, and directory structure.

---

## Requirements Specification

### What You Must Build (11 Components)

| # | Component | Description | Acceptance Criteria |
|---|-----------|-------------|-------------------|
| C1 | Test Harness | Orchestrator that runs all evaluation categories | Single command (`python harness/runner.py`) runs everything and produces unified results |
| C2 | Functional Test Suite | 10+ test cases covering agent behavior | pytest-based, uses DeepEval, covers happy/edge/error paths |
| C3 | LLM Quality Evaluation | Relevancy, faithfulness, hallucination metrics | 3+ metrics with configurable thresholds, per-case results |
| C4 | RAG Evaluation | Context precision, recall, faithfulness | RAGAS metrics integrated, retrieval vs. generation breakdown |
| C5 | Tool-Calling Evaluation | Selection accuracy, argument correctness | F1 score computed, unauthorized action detection |
| C6 | Security Red Team | promptfoo config with 10+ attack vectors | 5 attack categories, severity ratings, pass/fail per attack |
| C7 | Performance Benchmark | Latency, cost, LLM call count | Mean, median, P95 for all metrics; budget thresholds |
| C8 | Langfuse Integration | Observability for traced agent calls | Traces visible in Langfuse dashboard, eval scores logged |
| C9 | Quality Score Aggregation | Weighted score across all categories | Configurable weights, single 0–100 score, gate pass/fail |
| C10 | Streamlit Dashboard | Visual quality report | Overall score, per-category breakdown, test case table |
| C11 | GitHub Actions Pipeline | CI/CD that runs evals on push/PR | YAML workflow, artifact upload, failure on threshold violation |

### Quality Gate Thresholds

| Category | Weight | Pass Threshold | Gate Behavior |
|----------|--------|---------------|---------------|
| Functional Tests | 25% | 90% pass rate | Hard gate (blocks deployment) |
| LLM Quality | 20% | 0.7 avg score | Soft gate (warning if below) |
| RAG Quality | 15% | 0.7 avg score | Soft gate |
| Tool Calling | 15% | 85% selection accuracy | Hard gate |
| Security | 20% | 90% resistance rate | Hard gate |
| Performance | 5% | P95 latency < 30s | Soft gate |

**Overall pass:** All hard gates pass AND overall weighted score >= 70%.

---

## Step-by-Step Build Guide

### Step 1: Set Up the Capstone Project Structure

Organize your capstone within the existing framework:

```
agent-eval-framework/
+-- agents/
|   +-- support_agent.py        # (existing) Agent under test
|   +-- rag_agent.py            # (from Project 2)
+-- datasets/
|   +-- golden_support.json     # (existing) Golden dataset
|   +-- hr_policies.json        # (from Project 2)
|   +-- rag_eval_dataset.json   # (from Project 2)
+-- harness/
|   +-- __init__.py
|   +-- runner.py               # NEW: Main orchestrator
|   +-- scorer.py               # NEW: Quality score aggregation
|   +-- report.py               # NEW: Markdown report generator
+-- tests/
|   +-- conftest.py             # (existing)
|   +-- functional/             # (existing) Functional tests
|   +-- evaluation/             # (existing) LLM quality tests
|   +-- rag/                    # (existing) RAG tests
|   +-- tool_calling/           # (existing) Tool tests
|   +-- security/               # (existing) Security tests
+-- security/
|   +-- promptfoo.yaml          # (existing) Red team config
+-- performance/
|   +-- benchmark.py            # (existing) Performance benchmarks
+-- observability/
|   +-- langfuse_setup.py       # (existing) Langfuse integration
+-- reports/
|   +-- quality_dashboard.py    # (existing) Streamlit dashboard
|   +-- results/                # Output directory for results
+-- .github/
|   +-- workflows/
|       +-- agent-eval.yml      # (existing) CI/CD pipeline
+-- config/
|   +-- eval_config.yaml        # (existing) Configuration
+-- requirements.txt            # (existing)
+-- .env                        # Your environment variables
```

### Step 2: Build the Test Harness Orchestrator

Create `harness/runner.py`:

```python
"""
Capstone — Test Harness Orchestrator

Runs all evaluation categories in sequence and produces
unified results for the quality dashboard.

Usage: python harness/runner.py
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Project root
ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "reports" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_pytest_suite(suite_path: str, marker: str, output_name: str) -> dict:
    """Run a pytest suite and capture results."""
    print(f"\n{'─' * 60}")
    print(f"  Running: {output_name}")
    print(f"{'─' * 60}")

    start = time.time()
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(ROOT / suite_path),
            "-v", "--tb=short",
            f"-m", marker,
            f"--junitxml={RESULTS_DIR / f'{output_name}.xml'}",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    elapsed = time.time() - start

    # Parse results from output
    output = result.stdout + result.stderr
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    errors = output.count(" ERROR")
    total = passed + failed + errors

    suite_result = {
        "name": output_name,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": total,
        "pass_rate": passed / total if total > 0 else 0,
        "duration_seconds": round(elapsed, 2),
        "exit_code": result.returncode,
    }

    # Save individual results
    with open(RESULTS_DIR / f"{output_name}.json", "w") as f:
        json.dump(suite_result, f, indent=2)

    status = "PASS" if suite_result["pass_rate"] >= 0.7 else "FAIL"
    print(f"  Result: [{status}] {passed}/{total} passed ({suite_result['pass_rate']:.0%})")
    print(f"  Duration: {elapsed:.1f}s")

    return suite_result


def run_performance_benchmark() -> dict:
    """Run the performance benchmark suite."""
    print(f"\n{'─' * 60}")
    print(f"  Running: Performance Benchmark")
    print(f"{'─' * 60}")

    sys.path.insert(0, str(ROOT))
    from performance.benchmark import run_full_benchmark
    from agents.support_agent import run_support_agent

    test_inputs = [
        "What are your pricing plans?",
        "How do I reset my password?",
        "What is your refund policy?",
        "Can you look up my account? My email is alice@example.com",
        "I need to create a ticket for a billing issue.",
    ]

    results = run_full_benchmark(run_support_agent, test_inputs)

    # Determine pass/fail
    latency_ok = results["latency"]["p95"] < 30
    cost_ok = results["cost"]["mean"] < 0.10

    results["passed"] = latency_ok and cost_ok
    results["pass_rate"] = 1.0 if results["passed"] else 0.5

    with open(RESULTS_DIR / "performance.json", "w") as f:
        json.dump(results, f, indent=2)

    status = "PASS" if results["passed"] else "FAIL"
    print(f"  Result: [{status}]")
    print(f"  Latency P95: {results['latency']['p95']:.2f}s")
    print(f"  Avg Cost: ${results['cost']['mean']:.4f}")

    return results


def run_security_scan() -> dict:
    """Run the promptfoo red team scan."""
    print(f"\n{'─' * 60}")
    print(f"  Running: Security Red Team Scan")
    print(f"{'─' * 60}")

    security_config = ROOT / "security" / "promptfoo.yaml"
    if not security_config.exists():
        print("  [SKIP] promptfoo.yaml not found")
        return {"pass_rate": 0, "skipped": True}

    result = subprocess.run(
        [
            "npx", "promptfoo", "eval",
            "--config", str(security_config),
            "--output", str(RESULTS_DIR / "security-scan.json"),
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )

    # Parse promptfoo results
    scan_file = RESULTS_DIR / "security-scan.json"
    if scan_file.exists():
        with open(scan_file) as f:
            scan_data = json.load(f)
        total = len(scan_data.get("results", []))
        passed = sum(
            1 for r in scan_data.get("results", [])
            if r.get("success", False)
        )
        scan_result = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
        }
    else:
        scan_result = {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0}

    with open(RESULTS_DIR / "security.json", "w") as f:
        json.dump(scan_result, f, indent=2)

    status = "PASS" if scan_result["pass_rate"] >= 0.9 else "FAIL"
    print(f"  Result: [{status}] {scan_result.get('passed', 0)}/{scan_result.get('total', 0)} attacks resisted")

    return scan_result


def main():
    """Run the complete evaluation pipeline."""
    print("=" * 60)
    print("  CAPSTONE — ENTERPRISE QUALITY PLATFORM")
    print("  Full Evaluation Pipeline")
    print("=" * 60)
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"  Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")

    all_results = {}

    # 1. Functional tests
    all_results["functional"] = run_pytest_suite(
        "tests/functional/", "functional", "functional"
    )

    # 2. LLM quality evaluation
    all_results["llm_quality"] = run_pytest_suite(
        "tests/evaluation/", "evaluation", "llm_quality"
    )

    # 3. RAG evaluation
    all_results["rag_quality"] = run_pytest_suite(
        "tests/rag/", "rag", "rag_quality"
    )

    # 4. Tool-calling evaluation
    all_results["tool_calling"] = run_pytest_suite(
        "tests/tool_calling/", "tool_calling", "tool_calling"
    )

    # 5. Security red team
    all_results["security"] = run_security_scan()

    # 6. Performance benchmark
    all_results["performance"] = run_performance_benchmark()

    # 7. Compute aggregated quality score
    from harness.scorer import compute_quality_score
    quality_score = compute_quality_score(all_results)

    # 8. Generate markdown report
    from harness.report import generate_scorecard
    generate_scorecard(all_results, quality_score)

    # Save unified results
    all_results["quality_score"] = quality_score
    all_results["timestamp"] = datetime.now().isoformat()
    with open(RESULTS_DIR / "unified_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print(f"  OVERALL QUALITY SCORE: {quality_score['overall_score']:.1f}/100")
    verdict = "PRODUCTION READY" if quality_score["gate_passed"] else "NOT READY"
    print(f"  VERDICT: {verdict}")
    print(f"{'=' * 60}")
    print(f"\n  Results saved to: {RESULTS_DIR}")
    print(f"  View dashboard: streamlit run reports/quality_dashboard.py")


if __name__ == "__main__":
    main()
```

### Step 3: Build the Quality Score Aggregator

Create `harness/scorer.py`:

```python
"""
Capstone — Quality Score Aggregation

Computes a weighted quality score across all evaluation categories.
"""

# Category weights (must sum to 1.0)
CATEGORY_WEIGHTS = {
    "functional": 0.25,
    "llm_quality": 0.20,
    "rag_quality": 0.15,
    "tool_calling": 0.15,
    "security": 0.20,
    "performance": 0.05,
}

# Gate configuration
HARD_GATES = {
    "functional": 0.90,     # 90% pass rate required
    "tool_calling": 0.85,   # 85% selection accuracy
    "security": 0.90,       # 90% attack resistance
}

SOFT_GATES = {
    "llm_quality": 0.70,
    "rag_quality": 0.70,
    "performance": 0.50,
}


def compute_quality_score(results: dict) -> dict:
    """
    Compute the overall quality score from all evaluation results.

    Returns:
        dict with overall_score (0-100), per-category scores,
        gate status, and warnings.
    """
    category_scores = {}
    warnings = []

    for category, weight in CATEGORY_WEIGHTS.items():
        data = results.get(category, {})
        pass_rate = data.get("pass_rate", 0)

        # Normalize to 0-100
        score = pass_rate * 100
        category_scores[category] = {
            "score": round(score, 1),
            "weight": weight,
            "weighted_score": round(score * weight, 1),
        }

    # Compute overall weighted score
    overall_score = sum(cs["weighted_score"] for cs in category_scores.values())

    # Check hard gates
    hard_gate_passed = True
    for category, threshold in HARD_GATES.items():
        data = results.get(category, {})
        pass_rate = data.get("pass_rate", 0)
        if pass_rate < threshold:
            hard_gate_passed = False
            warnings.append(
                f"HARD GATE FAILED: {category} ({pass_rate:.0%} < {threshold:.0%})"
            )

    # Check soft gates
    for category, threshold in SOFT_GATES.items():
        data = results.get(category, {})
        pass_rate = data.get("pass_rate", 0)
        if pass_rate < threshold:
            warnings.append(
                f"SOFT GATE WARNING: {category} ({pass_rate:.0%} < {threshold:.0%})"
            )

    # Overall gate
    gate_passed = hard_gate_passed and overall_score >= 70

    return {
        "overall_score": round(overall_score, 1),
        "category_scores": category_scores,
        "hard_gate_passed": hard_gate_passed,
        "gate_passed": gate_passed,
        "warnings": warnings,
    }
```

### Step 4: Build the Markdown Report Generator

Create `harness/report.py`:

```python
"""
Capstone — Quality Scorecard Report Generator

Generates a Markdown report summarizing all evaluation results.
"""

import os
from datetime import datetime
from pathlib import Path


RESULTS_DIR = Path(__file__).parent.parent / "reports" / "results"


def generate_scorecard(results: dict, quality_score: dict) -> str:
    """Generate a Markdown quality scorecard."""

    verdict = "PRODUCTION READY" if quality_score["gate_passed"] else "NOT READY FOR PRODUCTION"

    report = f"""# AI Agent Quality Scorecard

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Agent:** TechCorp Customer Support Agent
**Model:** {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}

---

## Overall Quality Score

| Metric | Value |
|--------|-------|
| **Overall Score** | **{quality_score['overall_score']:.1f} / 100** |
| **Gate Status** | **{verdict}** |
| **Hard Gates** | {'All Passed' if quality_score['hard_gate_passed'] else 'FAILED'} |

---

## Category Breakdown

| Category | Score | Weight | Weighted | Gate |
|----------|-------|--------|----------|------|
"""
    for cat, data in quality_score["category_scores"].items():
        cat_display = cat.replace("_", " ").title()
        gate_status = "PASS" if data["score"] >= 70 else "FAIL"
        report += f"| {cat_display} | {data['score']:.1f}% | {data['weight']:.0%} | {data['weighted_score']:.1f} | {gate_status} |\n"

    report += f"""
---

## Detailed Results

### Functional Tests
- **Passed:** {results.get('functional', {}).get('passed', 'N/A')}
- **Failed:** {results.get('functional', {}).get('failed', 'N/A')}
- **Pass Rate:** {results.get('functional', {}).get('pass_rate', 0):.0%}

### LLM Quality
- **Passed:** {results.get('llm_quality', {}).get('passed', 'N/A')}
- **Failed:** {results.get('llm_quality', {}).get('failed', 'N/A')}
- **Pass Rate:** {results.get('llm_quality', {}).get('pass_rate', 0):.0%}

### RAG Quality
- **Passed:** {results.get('rag_quality', {}).get('passed', 'N/A')}
- **Failed:** {results.get('rag_quality', {}).get('failed', 'N/A')}
- **Pass Rate:** {results.get('rag_quality', {}).get('pass_rate', 0):.0%}

### Tool Calling
- **Passed:** {results.get('tool_calling', {}).get('passed', 'N/A')}
- **Failed:** {results.get('tool_calling', {}).get('failed', 'N/A')}
- **Pass Rate:** {results.get('tool_calling', {}).get('pass_rate', 0):.0%}

### Security
- **Attacks Resisted:** {results.get('security', {}).get('passed', 'N/A')}
- **Vulnerabilities Found:** {results.get('security', {}).get('failed', 'N/A')}
- **Resistance Rate:** {results.get('security', {}).get('pass_rate', 0):.0%}

### Performance
- **Latency P95:** {results.get('performance', {}).get('latency', {}).get('p95', 'N/A')}s
- **Avg Cost/Task:** ${results.get('performance', {}).get('cost', {}).get('mean', 'N/A')}
- **Avg LLM Calls:** {results.get('performance', {}).get('llm_calls', {}).get('mean', 'N/A')}
"""

    if quality_score["warnings"]:
        report += "\n---\n\n## Warnings\n\n"
        for warning in quality_score["warnings"]:
            report += f"- {warning}\n"

    report += f"""
---

## Recommendations

1. Address all **hard gate failures** before deployment
2. Review soft gate warnings for potential improvements
3. Re-run the evaluation suite after any agent changes
4. Set up Langfuse monitoring for production observability
5. Schedule weekly evaluation runs to track quality trends

---

*Generated by the Enterprise AI Agent Quality Platform*
*AI Agent Testing & Evaluation Course — Capstone Project*
"""

    # Save to file
    report_path = RESULTS_DIR / "quality_scorecard.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\n  Scorecard saved to: {report_path}")
    return report
```

### Step 5: Enhance the Streamlit Dashboard

Update `reports/quality_dashboard.py` to load the unified capstone results. The existing dashboard (see `reports/quality_dashboard.py` in the framework) already supports JSON results loading. Extend it with these additions:

```python
# Add to quality_dashboard.py — Capstone enhancements

def render_quality_gauge(score: float):
    """Render a quality score gauge."""
    color = "green" if score >= 70 else "orange" if score >= 50 else "red"
    st.markdown(
        f"<h1 style='text-align:center; color:{color};'>"
        f"{score:.1f}/100</h1>",
        unsafe_allow_html=True,
    )


def render_category_cards(category_scores: dict):
    """Render per-category score cards."""
    cols = st.columns(len(category_scores))
    for col, (cat, data) in zip(cols, category_scores.items()):
        with col:
            cat_display = cat.replace("_", " ").title()
            delta_color = "normal" if data["score"] >= 70 else "inverse"
            st.metric(
                label=cat_display,
                value=f"{data['score']:.0f}%",
                delta=f"Weight: {data['weight']:.0%}",
                delta_color=delta_color,
            )


# In the main() function, add:
# Load unified results from capstone
unified_path = Path("reports/results/unified_results.json")
if unified_path.exists():
    with open(unified_path) as f:
        unified = json.load(f)

    if "quality_score" in unified:
        qs = unified["quality_score"]
        render_quality_gauge(qs["overall_score"])
        render_category_cards(qs["category_scores"])

        if qs["warnings"]:
            st.warning("\\n".join(qs["warnings"]))
```

### Step 6: Add Langfuse Observability Integration

Use the existing `observability/langfuse_setup.py` to instrument your evaluation runs. Add tracing to the harness:

```python
# Add to harness/runner.py — Langfuse integration

import os

def log_evaluation_to_langfuse(results: dict, quality_score: dict):
    """Log evaluation results to Langfuse for production monitoring."""
    if not os.getenv("LANGFUSE_PUBLIC_KEY"):
        print("  [SKIP] Langfuse not configured — skipping observability")
        return

    from observability.langfuse_setup import init_langfuse

    langfuse = init_langfuse()

    # Create a trace for this evaluation run
    trace = langfuse.trace(
        name="capstone-evaluation",
        metadata={
            "overall_score": quality_score["overall_score"],
            "gate_passed": quality_score["gate_passed"],
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        },
    )

    # Log per-category scores
    for category, data in quality_score["category_scores"].items():
        langfuse.score(
            trace_id=trace.id,
            name=f"eval_{category}",
            value=data["score"] / 100,
            comment=f"Weight: {data['weight']}, Weighted: {data['weighted_score']}",
        )

    # Log overall score
    langfuse.score(
        trace_id=trace.id,
        name="overall_quality",
        value=quality_score["overall_score"] / 100,
    )

    langfuse.flush()
    print(f"  Logged to Langfuse (trace: {trace.id})")
```

### Step 7: Configure the GitHub Actions CI/CD Pipeline

Extend the existing `.github/workflows/agent-eval.yml` or create a capstone-specific pipeline:

```yaml
# .github/workflows/capstone-eval.yml
# Capstone CI/CD Pipeline — Full Quality Platform

name: Capstone Quality Gate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  OPENAI_MODEL: gpt-4o-mini
  PYTHON_VERSION: "3.11"
  LANGFUSE_PUBLIC_KEY: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
  LANGFUSE_SECRET_KEY: ${{ secrets.LANGFUSE_SECRET_KEY }}

jobs:
  quality-gate:
    name: Full Quality Evaluation
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install promptfoo
        run: npm install -g promptfoo

      - name: Run full evaluation pipeline
        run: python harness/runner.py

      - name: Check quality gate
        run: |
          python -c "
          import json
          with open('reports/results/unified_results.json') as f:
              results = json.load(f)
          score = results['quality_score']
          print(f'Quality Score: {score[\"overall_score\"]:.1f}/100')
          print(f'Gate Passed: {score[\"gate_passed\"]}')
          if not score['gate_passed']:
              print('QUALITY GATE FAILED')
              for w in score.get('warnings', []):
                  print(f'  - {w}')
              exit(1)
          print('QUALITY GATE PASSED')
          "

      - name: Upload evaluation results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-report-${{ github.sha }}
          path: reports/results/
          retention-days: 30

      - name: Upload quality scorecard
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: scorecard-${{ github.sha }}
          path: reports/results/quality_scorecard.md
```

### Step 8: Create the `harness/__init__.py`

```python
"""
Test Harness — Capstone orchestration module.
"""
```

### Step 9: Run the Complete Platform

```bash
# Run the full evaluation pipeline
python harness/runner.py

# View the Streamlit dashboard
streamlit run reports/quality_dashboard.py

# View the quality scorecard
cat reports/results/quality_scorecard.md

# Run via CI/CD (test locally)
act -j quality-gate  # if using 'act' for local GitHub Actions
```

### Step 10: Review and Polish

1. Verify all 6 evaluation categories produce results
2. Check the quality score aggregation is correct
3. Ensure the dashboard renders all categories
4. Verify the CI/CD pipeline YAML is valid
5. Write a 1-page executive summary of the quality assessment

---

## Expected Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| D1 | Test harness orchestrator | `harness/runner.py` |
| D2 | Quality score aggregator | `harness/scorer.py` |
| D3 | Markdown report generator | `harness/report.py` |
| D4 | Functional test suite | `tests/functional/` (10+ tests) |
| D5 | LLM quality evaluation | `tests/evaluation/` (3+ metrics) |
| D6 | RAG evaluation | `tests/rag/` (RAGAS integration) |
| D7 | Tool-calling tests | `tests/tool_calling/` (selection + args) |
| D8 | Security red team config | `security/promptfoo.yaml` (10+ attacks) |
| D9 | Performance benchmark results | `reports/results/performance.json` |
| D10 | Langfuse integration | `observability/langfuse_setup.py` (traces logged) |
| D11 | Streamlit dashboard | `reports/quality_dashboard.py` (enhanced) |
| D12 | CI/CD pipeline | `.github/workflows/capstone-eval.yml` |
| D13 | Quality scorecard | `reports/results/quality_scorecard.md` |
| D14 | Unified results | `reports/results/unified_results.json` |

---

## Evaluation Rubric

| Dimension | 5 (Excellent) | 3 (Adequate) | 1 (Needs Work) |
|-----------|--------------|--------------|-----------------|
| **Completeness** | All 11 components implemented and working together | 8+ components working, some gaps | Missing 4+ components |
| **Integration** | Single command runs everything; results flow seamlessly to dashboard and report | Components work individually but manual steps needed | Components don't communicate |
| **Quality Score Logic** | Weighted aggregation with hard/soft gates, configurable thresholds | Basic averaging without gates | No aggregation |
| **Dashboard** | Interactive Streamlit with gauges, cards, tables, and trend data | Basic Streamlit with metric display | No dashboard or static HTML |
| **CI/CD** | Working YAML pipeline with gate checks, artifact upload, and failure handling | YAML exists but doesn't check gates | No CI/CD configuration |
| **Observability** | Langfuse traces with eval scores logged per run | Langfuse initialized but minimal tracing | No observability |
| **Report Quality** | Professional Markdown scorecard with categories, verdicts, and recommendations | Basic text report | No report |
| **Code Quality** | Clean, documented, follows framework patterns, environment variables used | Working code with some documentation | Hardcoded values or undocumented |

**Scoring:** 35+ = Excellent | 25–34 = Good | 15–24 = Adequate | Below 15 = Revisit modules

---

## Extension Ideas

1. **Historical trending** — Store results in a SQLite database and show quality score trends over time in the dashboard
2. **Slack/Teams integration** — Send quality score notifications to a Slack channel when the CI/CD pipeline runs
3. **Multi-agent comparison** — Evaluate two agent versions side-by-side (e.g., GPT-4o-mini vs. GPT-4o) and compare scores
4. **Synthetic dataset expansion** — Use DeepEval's `Synthesizer` to generate 100+ test cases from your golden dataset
5. **Custom metric library** — Build a reusable library of 5+ custom GEval metrics for enterprise scenarios (industry-specific compliance, brand voice, etc.)
6. **Production monitoring dashboard** — Extend the Streamlit app to show live Langfuse traces and production quality metrics alongside evaluation results
7. **PDF report generation** — Convert the Markdown scorecard to a branded PDF using a library like `weasyprint` or `reportlab`

---

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| `harness/runner.py` can't find tests | Ensure you're running from the `agent-eval-framework/` root directory |
| promptfoo scan fails in CI | Ensure `npm install -g promptfoo` runs before the scan step; check Node.js version |
| Langfuse connection errors | Verify `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` in `.env` |
| Dashboard shows no data | Run `python harness/runner.py` first to generate `reports/results/unified_results.json` |
| Quality score is 0 | Check that `reports/results/*.json` files exist and contain valid `pass_rate` values |
| CI/CD times out | Increase `timeout-minutes` in the workflow; use `gpt-4o-mini` to reduce API latency |
| Some test suites have no marker | Ensure `conftest.py` registers all markers and test functions use `@pytest.mark.<marker>` |

---

## What You Learned

After completing this capstone, you can tell an interviewer:

> "I built a complete enterprise AI agent quality platform from scratch. The platform integrates six evaluation categories — functional testing, LLM quality metrics, RAG evaluation, tool-calling validation, security red teaming, and performance benchmarking — into a unified test harness. It computes a weighted quality score across all categories with configurable hard and soft gates. Results are visualized in a Streamlit dashboard for stakeholders, automated through a GitHub Actions CI/CD pipeline that gates deployments, and monitored in production via Langfuse observability. The platform answers the question every VP of Engineering asks: 'Is this agent safe and reliable enough for production?'"

---

## Portfolio Presentation Tips

When presenting this capstone in interviews or your portfolio:

1. **Lead with the business problem** — "A VP needed to know if an AI agent was production-ready"
2. **Show the architecture** — Walk through the diagram showing all components
3. **Demo the dashboard** — Screen recording of the Streamlit dashboard is compelling
4. **Highlight the quality score** — Explain the weighted aggregation and gate logic
5. **Talk about CI/CD** — Show that quality is enforced automatically, not manually
6. **Discuss tradeoffs** — Why these weights? Why these thresholds? Show engineering judgment

---

*This capstone is your portfolio piece. Make it excellent.*

**Architecture Details:** See [ARCHITECTURE.md](./ARCHITECTURE.md)
