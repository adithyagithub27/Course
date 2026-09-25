# Agent Evaluation Framework

A reusable, open-source framework for testing and evaluating AI agents in production environments.

Built as the companion project for the Udemy course:
**AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python**

## What This Framework Does

```
Test Case
   |
Agent Execution
   |
Trace Collection
   |
Evaluator
   |
Metric Calculation
   |
Threshold Check
   |
Pass / Fail
   |
Report
```

## Quick Start

```bash
# Clone and install
git clone <repo-url>
cd agent-eval-framework
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY="your-key-here"

# Run the example evaluation
pytest tests/ -v
```

## Project Structure

```
agent-eval-framework/
├── agents/                 # Sample agents to test against
│   ├── __init__.py
│   ├── support_agent.py    # Customer support agent
│   ├── rag_agent.py        # RAG-based Q&A agent
│   └── tool_agent.py       # Multi-tool agent
├── tests/                  # Test suites organized by type
│   ├── functional/         # Task completion, correctness
│   ├── evaluation/         # LLM quality metrics
│   ├── rag/                # Retrieval + generation quality
│   ├── security/           # Red team, injection, PII
│   ├── tool_calling/       # Tool selection, arguments
│   └── regression/         # Golden dataset regression
├── evaluators/             # Evaluation pipeline orchestrators
│   ├── __init__.py
│   ├── deepeval_suite.py   # DeepEval-based evaluations
│   ├── ragas_suite.py      # RAGAS RAG evaluations
│   └── custom_metrics.py   # Custom G-Eval metrics
├── datasets/               # Test data and golden datasets
│   ├── golden_support.json
│   ├── golden_rag.json
│   └── synthetic_generator.py
├── metrics/                # Metric definitions and thresholds
│   ├── __init__.py
│   └── thresholds.py
├── prompts/                # Evaluation prompts
│   └── judge_prompts.py
├── security/               # Security testing configs
│   └── promptfoo.yaml
├── performance/            # Performance benchmarking
│   └── benchmark.py
├── observability/          # Tracing setup
│   ├── __init__.py
│   └── langfuse_setup.py
├── reports/                # Report generation
│   ├── quality_dashboard.py
│   └── scorecard.py
├── config/                 # Configuration
│   └── eval_config.yaml
├── utils/                  # Shared utilities
│   ├── __init__.py
│   └── helpers.py
├── .github/
│   └── workflows/
│       └── agent-eval.yml  # CI/CD pipeline
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── .env.example
└── README.md
```

## Tools Used

| Tool | Purpose |
|---|---|
| DeepEval | Primary evaluation framework (pytest-style) |
| RAGAS | RAG-specific evaluation metrics |
| promptfoo | Security red teaming and prompt testing |
| Langfuse | Observability and tracing |
| OpenTelemetry | Enterprise tracing standard |
| pytest | Test runner |
| GitHub Actions | CI/CD pipeline |
| Streamlit | Quality dashboard |

## Evaluation Categories

- **Functional**: Task completion, correctness, workflow completion
- **LLM Quality**: Relevance, faithfulness, hallucination, coherence
- **RAG Quality**: Context precision, recall, faithfulness, answer relevancy
- **Security**: Prompt injection, jailbreak, PII leakage, unauthorized actions
- **Performance**: Latency, token cost, throughput
- **Reliability**: Failure rate, retry rate, recovery rate

## License

MIT
