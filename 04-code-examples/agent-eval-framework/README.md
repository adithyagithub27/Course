# agent-eval-framework

Companion repo for the Udemy course **AI Agent Testing & Evaluation** (Course 2).
You evaluate **TechCorp's customer support agent** (and four other agents) with
DeepEval, RAGAS, promptfoo, Langfuse and OpenTelemetry, and wire it all into a
CI quality gate.

**Everything runs offline.** With no API key (or `OFFLINE=1`) the agents use a
deterministic mock LLM and every metric uses a deterministic mock judge, so the
test suite and all 61 lecture demos run for free. Set `OPENAI_API_KEY` and
`OFFLINE=0` to run the same code against `gpt-4.1-mini` (agent) and `gpt-4.1` (judge).

## Quick start

```bash
# Python 3.11+, uv (https://docs.astral.sh/uv/)
make install        # uv sync --locked
make test           # 204 offline tests (5 live tests skipped), about 10 seconds
make demos          # every demos/mXX_*.py, offline
uv run python demos/m00_verify_setup.py
```

Live (costs a few cents, verify current pricing):

```bash
export OPENAI_API_KEY=sk-...
make eval           # golden-dataset eval + quality gate + live tests
```

## Verified versions (uv.lock, checked 2026-10-01)

| Package | Version | Used for |
|---|---|---|
| openai | 2.54.0 | agents (2.x line, decision T6) |
| deepeval | 4.2.7 | metrics, GEval, Synthesizer, assert_test |
| ragas | 0.4.3 | RAG metrics (`ragas.metrics.collections`) |
| langfuse | 4.16.0 | tracing (`observe`, `get_client`, `propagate_attributes`) |
| mcp | 2.2.0 | MCP server (`MCPServer`) and client (`mcp.Client`) |
| opentelemetry-sdk / semantic-conventions | 1.45.0 / 0.66b0 | GenAI spans (`gen_ai.*`) |
| streamlit | 1.64.0 | dashboard |
| promptfoo (npm, via npx) | 0.123.1 | red teaming (Node 20+) |
| garak / pyrit (separate envs) | 0.17.0 / 1.1.0 | Lecture 8.5 |

## Make targets

| Target | What it does |
|---|---|
| `make install` | `uv sync --locked` and copy `.env.example` to `.env` |
| `make test` | offline test suite (OFFLINE=1) |
| `make demos` | run every lecture demo offline |
| `make eval` | live golden-dataset eval, quality gate, live tests |
| `make eval-offline` | the same pipeline offline |
| `make smoke` | 3-case smoke eval (CI runs it on every push) |
| `make redteam` | promptfoo static suite on the real agent + SecureBank report |
| `make redteam-banking` | promptfoo attack matrix, SecureBank v1 vs v2 |
| `make redteam-live` | promptfoo generated red team (plugins + strategies), live |
| `make garak` / `make pyrit` | Lecture 8.5 tools (installed separately) |
| `make dashboard` | Streamlit quality dashboard |
| `make trace` / `make otel` | one traced run (Langfuse v4 / OpenTelemetry GenAI) |
| `make mcp` | run the TechCorp MCP server on stdio |
| `make capstone` | the full Module 14 pipeline |
| `make baseline` | re-record `regression/baselines/support_v1.json` |
| `make synthetic` | DeepEval Synthesizer: 100 goldens from 5 seeds |
| `make requirements` | regenerate `requirements.txt` from `uv.lock` |

## Layout

```
agents/          support_agent.py (TechCorp, 5 tools) | rag_agent.py | tool_agent.py | banking_agent.py | multi_agent.py
                 llm.py (client switch) | mock_llm.py + mock_brains.py (offline LLM)
config/          settings.py (models, prices, OFFLINE) | eval_config.yaml (5 dimensions, thresholds, gates)
datasets/        golden_support.json (10) | golden_capstone.json (20) | golden_rag.json (15) | red-team sets
evaluators/      metrics.py | judge.py (MockJudge) | custom_metrics.py (GEval) | ragas_suite.py | tool_metrics.py
                 llm_as_judge.py | dimensions.py | deepeval_suite.py | golden.py
security/        promptfoo/ (provider.py targets the real agent) | garak/ | pyrit/ | pii_scanner.py | redteam.py | agent_http.py
mcp_server/      techcorp_server.py (mcp 2.2 MCPServer) | contract.py
observability/   langfuse_tracing.py (v4) | otel_genai.py
performance/     benchmark.py | cost.py | reliability.py | tokens.py
regression/      regression_suite.py | synthetic_data.py | baselines/
monitoring/      drift_monitor.py | governance.py | scorecard.py
reports/         run_eval.py | quality_gate.py | experiments.py | quality_dashboard.py
capstone/        platform.py | run_capstone.py
demos/           one file per lecture demo: mXX_slug.py
tests/           unit/ component/ trajectory/ e2e/ production/ live/   (the five-layer eval pyramid)
.github/workflows/agent-eval.yml   the CI quality gate
```

## What offline mode is (and is not)

The mock LLM follows fixed rules per agent (see `agents/mock_brains.py`), and the
mock judge answers DeepEval's and RAGAS's own prompts with word-overlap and
number-matching rules (`evaluators/judge.py`, `evaluators/heuristics.py`).
Every DeepEval and RAGAS metric class runs its real code path. Offline scores
are repeatable teaching numbers, not a substitute for a real judge: re-run
live before you quote a score as a fact. Latencies offline come from a
simulated clock.

## License

MIT
