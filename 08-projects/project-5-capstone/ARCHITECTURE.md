# Capstone Architecture Document

## Enterprise AI Agent Quality Platform — System Design

**Version:** 1.0
**Last Updated:** June 2025
**Status:** Reference Architecture for Capstone Project

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Component Architecture](#2-component-architecture)
3. [Data Flow](#3-data-flow)
4. [Directory Structure](#4-directory-structure)
5. [Component Specifications](#5-component-specifications)
6. [Integration Points](#6-integration-points)
7. [Configuration Management](#7-configuration-management)
8. [Deployment Architecture](#8-deployment-architecture)

---

## 1. System Overview

The Enterprise AI Agent Quality Platform is a unified evaluation system that assesses an AI agent across six quality dimensions and produces a single production-readiness verdict.

### High-Level Architecture

```
+====================================================================+
||                  ENTERPRISE QUALITY PLATFORM                      ||
||                                                                    ||
||  "Is this agent safe and reliable enough for production?"         ||
+====================================================================+
        |                           |                           |
        v                           v                           v
+----------------+         +----------------+         +----------------+
|   EVALUATION   |         |  REPORTING &   |         |   OPERATIONS   |
|   ENGINE       |         |  VISUALIZATION |         |   & CI/CD      |
|                |         |                |         |                |
| - Test Harness |         | - Streamlit    |         | - GitHub       |
| - DeepEval     |         |   Dashboard    |         |   Actions      |
| - RAGAS        |         | - Markdown     |         | - Langfuse     |
| - promptfoo    |         |   Scorecard    |         |   Monitoring   |
| - Benchmarks   |         | - JSON Results |         | - Quality      |
|                |         |                |         |   Gates        |
+----------------+         +----------------+         +----------------+
```

### Design Principles

1. **Single command execution** — `python harness/runner.py` runs the entire evaluation pipeline
2. **Modular categories** — Each evaluation category is independent and can run standalone
3. **Configurable thresholds** — All pass/fail thresholds live in `config/eval_config.yaml`
4. **Environment-based secrets** — All API keys and credentials use environment variables
5. **Framework-agnostic agent interface** — The harness tests agents through a standard `run_agent(input) -> dict` interface
6. **Reproducible results** — Pinned dependencies, deterministic seeds where possible, versioned golden datasets

---

## 2. Component Architecture

### 2.1 Component Dependency Graph

```
                    +------------------+
                    |   harness/       |
                    |   runner.py      |
                    |   (Orchestrator) |
                    +--------+---------+
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
  +-------+------+  +-------+------+  +--------+------+
  | Evaluation   |  | Reporting    |  | Operations    |
  | Categories   |  | Layer        |  | Layer         |
  +-------+------+  +-------+------+  +--------+------+
          |                  |                  |
    +-----+-----+      +----+----+      +------+------+
    |     |     |      |         |      |             |
    v     v     v      v         v      v             v
 Tests  RAGAS  pfoo  Score   Dashboard CI/CD     Langfuse
              scan   card
```

### 2.2 Agent Interface Contract

Every agent under test must expose this interface:

```python
def run_agent(user_message: str) -> dict:
    """
    Standard agent interface for the quality platform.

    Args:
        user_message: The user's input message

    Returns:
        dict with required keys:
        - response: str          # Agent's text response
        - tool_calls: list[dict] # Tools invoked [{tool, arguments, result}]
        - total_tokens: int      # Total tokens consumed
        - llm_calls: int         # Number of LLM API calls made
    """
```

This contract allows the platform to evaluate any agent, regardless of framework (LangChain, LlamaIndex, custom, etc.).

### 2.3 Evaluation Categories

```
+------------------------------------------------------------------+
|                    EVALUATION CATEGORIES                           |
+------------------------------------------------------------------+

+-----------------+   +-----------------+   +-----------------+
| 1. FUNCTIONAL   |   | 2. LLM QUALITY  |   | 3. RAG QUALITY  |
| (pytest)        |   | (DeepEval)      |   | (RAGAS+DeepEval)|
|                 |   |                 |   |                 |
| - Happy path    |   | - Relevancy     |   | - Context       |
| - Edge cases    |   | - Faithfulness  |   |   Precision     |
| - Error paths   |   | - Hallucination |   | - Context       |
| - Regression    |   | - Custom GEval  |   |   Recall        |
|                 |   |                 |   | - Faithfulness  |
| Input: Golden   |   | Input: Agent    |   | - Answer        |
| dataset         |   | responses +     |   |   Relevancy     |
|                 |   | context         |   |                 |
| Output: pass/   |   | Output: scores  |   | Output: scores  |
| fail per case   |   | per metric      |   | per metric      |
+-----------------+   +-----------------+   +-----------------+

+-----------------+   +-----------------+   +-----------------+
| 4. TOOL CALLING |   | 5. SECURITY     |   | 6. PERFORMANCE  |
| (pytest+DeepEv) |   | (promptfoo)     |   | (benchmark.py)  |
|                 |   |                 |   |                 |
| - Selection     |   | - Prompt        |   | - Latency       |
|   accuracy      |   |   Injection     |   |   (P50/P95)     |
| - Argument      |   | - Jailbreak     |   | - Token cost    |
|   correctness   |   | - PII Leakage   |   |   per task      |
| - Error         |   | - Unauthorized  |   | - LLM calls     |
|   handling      |   |   Actions       |   |   per task      |
| - Auth checks   |   | - Data Exfil    |   |                 |
|                 |   |                 |   | Output:         |
| Output: F1      |   | Output: resist  |   | mean/median/    |
| score           |   | rate + severity |   | P95 stats       |
+-----------------+   +-----------------+   +-----------------+
```

---

## 3. Data Flow

### 3.1 Evaluation Pipeline Data Flow

```
Phase 1: INPUT
                         +-------------------+
  config/eval_config.yaml|  Configuration    |
  .env                   |  (thresholds,     |
  datasets/*.json        |   weights, model) |
                         +--------+----------+
                                  |
                                  v
Phase 2: EXECUTION
                         +-------------------+
  harness/runner.py      |  Orchestrator     |
                         |                   |
                         |  For each category:|
                         |  1. Load config   |
                         |  2. Run tests     |
                         |  3. Collect scores|
                         +--------+----------+
                                  |
                    +-------------+-------------+
                    |             |             |
                    v             v             v
            +-----------+  +-----------+  +-----------+
            | pytest    |  | RAGAS     |  | promptfoo |
            | subprocess|  | evaluate()|  | subprocess|
            +-----------+  +-----------+  +-----------+
                    |             |             |
                    v             v             v
Phase 3: RESULTS
            +-----------+  +-----------+  +-----------+
            | *.xml     |  | scores    |  | scan.json |
            | *.json    |  | dict      |  |           |
            +-----------+  +-----------+  +-----------+
                    |             |             |
                    +-------------+-------------+
                                  |
                                  v
Phase 4: AGGREGATION
                         +-------------------+
  harness/scorer.py      |  Quality Score    |
                         |  Aggregation      |
                         |                   |
                         |  Weighted average |
                         |  Gate evaluation  |
                         +--------+----------+
                                  |
                    +-------------+-------------+
                    |             |             |
                    v             v             v
Phase 5: OUTPUT
            +-----------+  +-----------+  +-----------+
            | Markdown  |  | Streamlit |  | Langfuse  |
            | Scorecard |  | Dashboard |  | Traces    |
            +-----------+  +-----------+  +-----------+
                    |
                    v
Phase 6: CI/CD
            +-----------+
            | GitHub    |
            | Actions   |
            | Gate      |
            | Check     |
            +-----------+
            | exit 0/1  |
            +-----------+
```

### 3.2 Data Format Flow

```
Golden Dataset (JSON)
      |
      v
Agent Execution (Python)
      |
      v
LLMTestCase (DeepEval object)
      |
      +---> DeepEval Metric.measure() ---> score: float
      |
      +---> RAGAS evaluate() ---> DataFrame with metric columns
      |
      v
Results Dictionary (Python dict)
      |
      +---> reports/results/*.json (per-category)
      |
      +---> reports/results/unified_results.json (all categories)
      |
      v
Quality Score (Python dict)
      |
      +---> reports/results/quality_scorecard.md (Markdown)
      |
      +---> Streamlit (live rendering)
      |
      +---> Langfuse (API push)
      |
      +---> CI/CD exit code (0 = pass, 1 = fail)
```

### 3.3 Results JSON Schema

```json
{
  "timestamp": "2025-06-30T14:30:00",
  "quality_score": {
    "overall_score": 78.5,
    "gate_passed": true,
    "hard_gate_passed": true,
    "category_scores": {
      "functional": {
        "score": 90.0,
        "weight": 0.25,
        "weighted_score": 22.5
      },
      "llm_quality": {
        "score": 80.0,
        "weight": 0.20,
        "weighted_score": 16.0
      },
      "rag_quality": {
        "score": 70.0,
        "weight": 0.15,
        "weighted_score": 10.5
      },
      "tool_calling": {
        "score": 85.0,
        "weight": 0.15,
        "weighted_score": 12.75
      },
      "security": {
        "score": 90.0,
        "weight": 0.20,
        "weighted_score": 18.0
      },
      "performance": {
        "score": 100.0,
        "weight": 0.05,
        "weighted_score": 5.0
      }
    },
    "warnings": []
  },
  "functional": {
    "passed": 9,
    "failed": 1,
    "total": 10,
    "pass_rate": 0.9
  },
  "llm_quality": {
    "passed": 8,
    "failed": 2,
    "total": 10,
    "pass_rate": 0.8
  },
  "rag_quality": {
    "passed": 7,
    "failed": 3,
    "total": 10,
    "pass_rate": 0.7
  },
  "tool_calling": {
    "passed": 17,
    "failed": 3,
    "total": 20,
    "pass_rate": 0.85
  },
  "security": {
    "passed": 9,
    "failed": 1,
    "total": 10,
    "pass_rate": 0.9
  },
  "performance": {
    "latency": {"mean": 2.1, "median": 1.8, "p95": 4.5},
    "cost": {"mean": 0.003},
    "llm_calls": {"mean": 1.8},
    "pass_rate": 1.0
  }
}
```

---

## 4. Directory Structure

```
agent-eval-framework/
|
+-- .env                            # Environment variables (NEVER committed)
+-- .env.example                    # Template for environment variables
+-- .gitignore                      # Excludes .env, __pycache__, results/
+-- requirements.txt                # Pinned Python dependencies
+-- pyproject.toml                  # Project metadata
+-- Dockerfile                      # Container build for CI
+-- README.md                       # Framework documentation
|
+-- .github/
|   +-- workflows/
|       +-- agent-eval.yml          # Standard CI/CD pipeline
|       +-- capstone-eval.yml       # Capstone-specific pipeline
|
+-- agents/                         # Agents under test
|   +-- __init__.py
|   +-- support_agent.py            # Customer support agent (primary)
|   +-- rag_agent.py                # RAG-based HR policy agent
|   +-- tool_agent.py               # Multi-tool operations agent
|   +-- banking_agent.py            # Banking agent (red team target)
|
+-- config/
|   +-- eval_config.yaml            # Central configuration
|                                    #   - Model settings
|                                    #   - Threshold values
|                                    #   - Dataset paths
|                                    #   - Category weights
|
+-- datasets/                       # Evaluation datasets
|   +-- golden_support.json         # 10-case customer support golden set
|   +-- hr_policies.json            # HR policy document corpus
|   +-- rag_eval_dataset.json       # RAG evaluation questions
|   +-- synthetic_generator.py      # Synthetic data generation
|
+-- evaluators/                     # Evaluation metric definitions
|   +-- __init__.py
|   +-- deepeval_suite.py           # DeepEval metric configuration
|   +-- ragas_suite.py              # RAGAS metric configuration
|   +-- custom_metrics.py           # Custom GEval metrics
|
+-- harness/                        # Capstone orchestration (NEW)
|   +-- __init__.py
|   +-- runner.py                   # Main pipeline orchestrator
|   +-- scorer.py                   # Quality score aggregation
|   +-- report.py                   # Markdown report generator
|
+-- metrics/
|   +-- __init__.py
|   +-- thresholds.py               # Threshold definitions
|
+-- observability/                  # Production monitoring
|   +-- __init__.py
|   +-- langfuse_setup.py           # Langfuse client & tracing
|
+-- performance/                    # Performance benchmarking
|   +-- benchmark.py                # Latency, cost, throughput
|
+-- reports/                        # Output & visualization
|   +-- quality_dashboard.py        # Streamlit dashboard
|   +-- results/                    # Generated results (gitignored)
|       +-- functional.json
|       +-- functional.xml
|       +-- llm_quality.json
|       +-- rag_quality.json
|       +-- tool_calling.json
|       +-- security.json
|       +-- security-scan.json
|       +-- performance.json
|       +-- unified_results.json    # Aggregated results
|       +-- quality_scorecard.md    # Markdown report
|
+-- security/                       # Red team configurations
|   +-- promptfoo.yaml              # Customer support red team
|   +-- banking_redteam.yaml        # Banking agent red team
|
+-- tests/                          # All test suites
|   +-- conftest.py                 # Shared fixtures & markers
|   +-- functional/
|   |   +-- test_support_agent.py   # Functional behavior tests
|   +-- evaluation/
|   |   +-- test_llm_quality.py     # LLM output quality tests
|   +-- rag/
|   |   +-- test_rag_quality.py     # RAG pipeline tests
|   +-- tool_calling/
|   |   +-- test_tool_correctness.py # Tool-calling tests
|   +-- security/
|   |   +-- test_prompt_injection.py # Security tests
|   +-- regression/
|   |   +-- test_golden_dataset.py  # Golden dataset regression
|   +-- project1/
|   |   +-- test_support_eval.py    # Project 1 deliverable
|   +-- project2/
|   |   +-- test_rag_eval.py        # Project 2 deliverable
|   |   +-- generate_rag_report.py  # RAG diagnostic report
|   +-- project3/
|   |   +-- test_tool_calling.py    # Project 3 deliverable
|   +-- project4/
|       +-- test_red_team.py        # Project 4 deliverable
|
+-- utils/
    +-- __init__.py
    +-- helpers.py                   # Shared utility functions
```

---

## 5. Component Specifications

### 5.1 Test Harness (`harness/runner.py`)

**Responsibility:** Orchestrate all evaluation categories in sequence, collect results, and trigger aggregation and reporting.

**Interface:**

```python
def main() -> None:
    """Run the complete evaluation pipeline."""
    # 1. Load configuration from eval_config.yaml
    # 2. Run each evaluation category
    # 3. Collect results into unified dict
    # 4. Compute quality score via scorer.py
    # 5. Generate reports via report.py
    # 6. Log to Langfuse (if configured)
    # 7. Save unified_results.json
    # 8. Print verdict
```

**Design decisions:**
- Uses `subprocess` to run pytest suites (isolation, clean exit codes)
- Runs categories in sequence (not parallel) to manage API rate limits
- Captures stdout/stderr for debugging
- Each category result is saved as a standalone JSON (testable independently)

### 5.2 Quality Scorer (`harness/scorer.py`)

**Responsibility:** Compute a weighted quality score and evaluate gate conditions.

**Scoring formula:**

```
overall_score = sum(category_score[i] * weight[i]) for all categories

where:
  category_score = pass_rate * 100  (0-100 scale)
  weight = configured weight (must sum to 1.0)
```

**Gate logic:**

```
gate_passed = (
    all(hard_gates pass) AND
    overall_score >= 70
)
```

**Hard gates** block deployment; **soft gates** generate warnings.

### 5.3 Report Generator (`harness/report.py`)

**Responsibility:** Generate a Markdown scorecard suitable for stakeholder review.

**Output format:**
- Header with metadata (date, agent, model)
- Overall score and verdict
- Per-category breakdown table
- Detailed results per category
- Warnings section
- Recommendations section

### 5.4 Streamlit Dashboard (`reports/quality_dashboard.py`)

**Responsibility:** Real-time visual representation of quality metrics.

**Layout:**

```
+------------------------------------------+
|        AI Agent Quality Dashboard        |
+------------------------------------------+
|                                          |
|  [Overall Score Gauge: 78.5/100]         |
|                                          |
|  +------+ +------+ +------+ +------+    |
|  | Func | | LLM  | | RAG  | | Tool |    |
|  | 90%  | | 80%  | | 70%  | | 85%  |    |
|  +------+ +------+ +------+ +------+    |
|                                          |
|  +------+ +------+                       |
|  | Sec  | | Perf |   [Gate: PASS]        |
|  | 90%  | | 100% |                       |
|  +------+ +------+                       |
|                                          |
|  +--------------------------------------+|
|  | Test Case Details Table              ||
|  | Input | Category | Result | Scores   ||
|  |-------|----------|--------|----------|
|  | ...   | ...      | PASS   | 0.85    ||
|  +--------------------------------------+|
|                                          |
|  [Warnings: ...]                         |
+------------------------------------------+
```

### 5.5 CI/CD Pipeline (`.github/workflows/capstone-eval.yml`)

**Responsibility:** Automate evaluation on every push/PR and enforce quality gates.

**Pipeline stages:**

```
Checkout --> Setup Python --> Install Deps --> Install promptfoo
    |
    v
Run Harness (python harness/runner.py)
    |
    v
Check Quality Gate (read unified_results.json, exit 0/1)
    |
    v
Upload Artifacts (results/, scorecard.md)
```

### 5.6 Langfuse Integration (`observability/langfuse_setup.py`)

**Responsibility:** Log agent traces and evaluation scores for production monitoring.

**Integration points:**
- `traced_agent_call()` — Wraps agent execution with Langfuse trace
- `log_eval_score()` — Logs evaluation metric scores to existing traces
- Capstone logs per-category scores and overall quality score per run

---

## 6. Integration Points

### 6.1 External Services

```
+------------------+      +------------------+      +------------------+
|   OpenAI API     |      |   Langfuse       |      |   GitHub         |
|                  |      |                  |      |                  |
| - LLM calls     |      | - Trace storage  |      | - Actions runner |
| - Agent exec    |      | - Score logging  |      | - Artifact store |
| - Metric judging|      | - Dashboard      |      | - Secret storage |
|                  |      |                  |      |                  |
| Auth: API key   |      | Auth: pub/secret |      | Auth: GITHUB_    |
|  OPENAI_API_KEY  |      |  LANGFUSE_*_KEY  |      |  TOKEN           |
+------------------+      +------------------+      +------------------+
```

### 6.2 Internal Integration Map

| From | To | Interface | Data |
|------|----|-----------|------|
| `runner.py` | `tests/functional/` | `subprocess(pytest)` | JUnit XML + parsed counts |
| `runner.py` | `tests/evaluation/` | `subprocess(pytest)` | JUnit XML + parsed counts |
| `runner.py` | `tests/rag/` | `subprocess(pytest)` | JUnit XML + parsed counts |
| `runner.py` | `tests/tool_calling/` | `subprocess(pytest)` | JUnit XML + parsed counts |
| `runner.py` | `security/promptfoo.yaml` | `subprocess(npx promptfoo)` | JSON scan results |
| `runner.py` | `performance/benchmark.py` | Python import | BenchmarkResult dict |
| `runner.py` | `scorer.py` | Python import | Results dict -> Quality score dict |
| `runner.py` | `report.py` | Python import | Results + score -> Markdown string |
| `runner.py` | `langfuse_setup.py` | Python import | Results + score -> API calls |
| `quality_dashboard.py` | `reports/results/*.json` | File read | JSON results |
| `capstone-eval.yml` | `runner.py` | `subprocess(python)` | Exit code + artifacts |

---

## 7. Configuration Management

### 7.1 Environment Variables

All sensitive configuration uses environment variables. **Never hardcode API keys.**

| Variable | Required | Used By | Example |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | All components | `sk-...` |
| `OPENAI_MODEL` | No (default: `gpt-4o-mini`) | Agents, metrics | `gpt-4o-mini` |
| `LANGFUSE_PUBLIC_KEY` | No | Observability | `pk-lf-...` |
| `LANGFUSE_SECRET_KEY` | No | Observability | `sk-lf-...` |
| `LANGFUSE_HOST` | No (default: `https://cloud.langfuse.com`) | Observability | URL |
| `EVAL_PASS_THRESHOLD` | No (default: `0.7`) | Scorer | `0.7` |
| `EVAL_SECURITY_THRESHOLD` | No (default: `0.9`) | Scorer | `0.9` |

### 7.2 Configuration File (`config/eval_config.yaml`)

Non-sensitive configuration lives in YAML:

```yaml
# Central configuration for the quality platform
models:
  primary: "gpt-4o-mini"
  judge: "gpt-4o-mini"

thresholds:
  answer_relevancy: 0.7
  faithfulness: 0.8
  hallucination: 0.3
  task_completion: 0.8
  tool_correctness: 0.85
  context_precision: 0.7
  context_recall: 0.7
  prompt_injection_resistance: 0.9
  max_latency_seconds: 30
  max_cost_per_task: 0.10

weights:
  functional: 0.25
  llm_quality: 0.20
  rag_quality: 0.15
  tool_calling: 0.15
  security: 0.20
  performance: 0.05

gates:
  hard:
    functional: 0.90
    tool_calling: 0.85
    security: 0.90
  soft:
    llm_quality: 0.70
    rag_quality: 0.70
    performance: 0.50
```

### 7.3 Configuration Hierarchy

```
Environment Variables (.env)       # Highest priority (secrets)
       |
       v
Configuration File (eval_config.yaml)  # Non-secret settings
       |
       v
Code Defaults (Python)             # Fallback values
```

---

## 8. Deployment Architecture

### 8.1 Local Development

```
Developer Machine
+--------------------------------------------------+
|                                                    |
|  Terminal 1:  python harness/runner.py             |
|  Terminal 2:  streamlit run reports/quality_dashboard.py  |
|                                                    |
|  .env file with API keys                          |
|  Results in reports/results/                      |
+--------------------------------------------------+
        |                    |
        v                    v
   OpenAI API           Langfuse Cloud
```

### 8.2 CI/CD (GitHub Actions)

```
GitHub Repository
+--------------------------------------------------+
|  .github/workflows/capstone-eval.yml             |
|                                                    |
|  Triggers: push to main, pull_request             |
|                                                    |
|  Secrets:                                         |
|    OPENAI_API_KEY                                 |
|    LANGFUSE_PUBLIC_KEY                            |
|    LANGFUSE_SECRET_KEY                            |
+--------------------------------------------------+
        |
        v
GitHub Actions Runner (ubuntu-latest)
+--------------------------------------------------+
|  1. Checkout code                                 |
|  2. Setup Python 3.11                             |
|  3. pip install -r requirements.txt               |
|  4. npm install -g promptfoo                      |
|  5. python harness/runner.py                      |
|  6. Check quality gate (exit 0 or 1)              |
|  7. Upload artifacts                              |
+--------------------------------------------------+
        |               |
        v               v
  OpenAI API      Langfuse Cloud
                        |
                        v
              Production Monitoring Dashboard
```

### 8.3 Production Monitoring (Post-Deploy)

```
Production Environment
+--------------------------------------------------+
|  AI Agent (deployed)                              |
|       |                                           |
|       +---> Langfuse SDK (trace every call)       |
|       |                                           |
|       +---> Log: latency, tokens, tool calls      |
+--------------------------------------------------+
        |
        v
Langfuse Cloud
+--------------------------------------------------+
|  - Trace visualization                            |
|  - Token cost tracking                            |
|  - Latency monitoring                             |
|  - Evaluation score trends                        |
|  - Alerting on quality degradation                |
+--------------------------------------------------+
        |
        v
Scheduled Re-evaluation (Weekly)
+--------------------------------------------------+
|  GitHub Actions (scheduled cron)                  |
|  Run full eval suite against production agent     |
|  Compare scores to baseline                       |
|  Alert on regression                              |
+--------------------------------------------------+
```

---

## Appendix A: Quality Score Calculation Example

```
Input scores:
  Functional:   9/10 = 90%   x 0.25 = 22.50
  LLM Quality:  8/10 = 80%   x 0.20 = 16.00
  RAG Quality:  7/10 = 70%   x 0.15 = 10.50
  Tool Calling: 17/20 = 85%  x 0.15 = 12.75
  Security:     9/10 = 90%   x 0.20 = 18.00
  Performance:  pass = 100%  x 0.05 =  5.00
                                     ------
  Overall Score:                      84.75

Hard Gates:
  Functional:  90% >= 90%  PASS
  Tool Calling: 85% >= 85%  PASS
  Security:    90% >= 90%  PASS

Soft Gates:
  LLM Quality:  80% >= 70%  OK
  RAG Quality:  70% >= 70%  OK (borderline)
  Performance: 100% >= 50%  OK

Overall: 84.75 >= 70 AND all hard gates pass
Verdict: PRODUCTION READY
```

---

## Appendix B: Technology Stack Reference

| Technology | Version | Purpose | License |
|-----------|---------|---------|---------|
| Python | 3.11+ | Runtime | PSF |
| OpenAI SDK | 1.40+ | LLM API client | MIT |
| DeepEval | 3.9+ | Evaluation framework | Apache 2.0 |
| RAGAS | 0.4+ | RAG evaluation | Apache 2.0 |
| promptfoo | latest | Red teaming | MIT |
| Langfuse | 2.50+ | Observability | MIT |
| Streamlit | 1.35+ | Dashboard | Apache 2.0 |
| pytest | 8.0+ | Test runner | MIT |
| GitHub Actions | N/A | CI/CD | N/A |
| python-dotenv | 1.0+ | Environment management | BSD |

---

## Appendix C: Security Considerations

1. **API keys** — Stored in `.env` (local) or GitHub Secrets (CI/CD). Never committed to version control.
2. **Mock data only** — All agents use simulated backends. No real customer data is used in evaluation.
3. **Rate limiting** — The harness runs categories sequentially to avoid OpenAI rate limits.
4. **Cost controls** — Uses `gpt-4o-mini` by default. Full pipeline costs approximately $0.50–$2.00 per run.
5. **Result storage** — `reports/results/` is gitignored. Results contain agent responses that may include test PII from mock data.

---

*This architecture document is the reference design for the Capstone Project. Students should implement this architecture while adapting it to their specific evaluation needs and available tools.*
