# TechCorp agent evaluation framework - Course 2 "AI Agent Testing & Evaluation"
#
#   make install     create .venv from uv.lock (uv sync --locked)
#   make test        offline test suite: mock LLM + mock judge, no API key (OFFLINE=1)
#   make demos       run every lecture demo offline
#   make eval        LIVE: golden-dataset eval + live tests (needs OPENAI_API_KEY; costs cents)
#   make redteam     promptfoo static suite against the real agent (offline; needs Node 20+)
#   make dashboard   Streamlit quality dashboard
#   make trace       one traced agent run (Langfuse if LANGFUSE_* keys are set, else printed)

UV      ?= uv
RUN     := $(UV) run
PF      ?= promptfoo@0.123.1
export PROMPTFOO_DISABLE_TELEMETRY := 1
export PROMPTFOO_DISABLE_UPDATE := 1

.PHONY: help install test test-unit test-fast demos eval eval-offline smoke gate redteam redteam-banking redteam-live \
        garak pyrit dashboard trace otel mcp capstone baseline synthetic requirements clean

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## install the locked environment (Python 3.11+)
	$(UV) sync --locked
	@cp -n .env.example .env 2>/dev/null || true
	@echo "Next: make test"

test: ## offline suite: unit, component, trajectory, e2e, production (live tests skipped)
	OFFLINE=1 $(RUN) pytest -q

test-unit: ## unit layer only
	OFFLINE=1 $(RUN) pytest -q tests/unit

demos: ## run every demos/mXX_*.py offline
	OFFLINE=1 $(RUN) python demos/run_all.py

eval: ## LIVE evaluation with gpt-4.1-mini (agent) and gpt-4.1 (judge)
	@test -n "$$OPENAI_API_KEY" || (echo "OPENAI_API_KEY is not set" && exit 1)
	OFFLINE=0 $(RUN) python -m reports.run_eval --out reports/results/eval.json
	OFFLINE=0 $(RUN) python -m reports.quality_gate reports/results/eval.json --summary reports/results/summary.md
	OFFLINE=0 $(RUN) pytest -q -m live

eval-offline: ## same pipeline as `make eval`, offline
	OFFLINE=1 $(RUN) python -m reports.run_eval --out reports/results/eval.json
	OFFLINE=1 $(RUN) python -m reports.quality_gate reports/results/eval.json --summary reports/results/summary.md --baseline support_v1

smoke: ## 3-case smoke eval (what CI runs on every push)
	$(RUN) python -m reports.run_eval --smoke --out reports/results/smoke.json

redteam: ## promptfoo static suite on the real support agent (offline)
	cd security/promptfoo && OFFLINE=1 PROMPTFOO_PYTHON=$(CURDIR)/.venv/bin/python npx -y $(PF) eval -c promptfooconfig.yaml --no-cache --no-progress-bar
	OFFLINE=1 $(RUN) python demos/m08_project4_banking_redteam.py

redteam-banking: ## promptfoo static attack matrix on SecureBank v1 vs v2 (v1 is expected to fail 2 tests)
	-cd security/promptfoo && OFFLINE=1 PROMPTFOO_PYTHON=$(CURDIR)/.venv/bin/python npx -y $(PF) eval -c banking-static.yaml --no-cache --no-progress-bar

redteam-live: ## promptfoo generated red team (plugins + strategies); needs OPENAI_API_KEY
	cd security/promptfoo && PROMPTFOO_PYTHON=$(CURDIR)/.venv/bin/python npx -y $(PF) redteam run -c redteam.yaml
	cd security/promptfoo && npx -y $(PF) redteam report

garak: ## Garak scan (requires `uv tool install garak==0.17.0`)
	OFFLINE=1 $(RUN) python demos/m08_garak_scan.py --run

pyrit: ## PyRIT attack (requires .venv-pyrit with pyrit==1.1.0)
	OFFLINE=1 $(RUN) python demos/m08_pyrit_attack.py --run

dashboard: ## Streamlit quality dashboard
	$(RUN) streamlit run reports/quality_dashboard.py

trace: ## one Langfuse v4 trace of the support agent
	$(RUN) python -m observability.langfuse_tracing "What is your refund policy?"

otel: ## the same run as OpenTelemetry GenAI spans
	$(RUN) python -m observability.otel_genai

mcp: ## run the TechCorp MCP server on stdio
	$(RUN) python -m mcp_server.techcorp_server

capstone: ## full capstone pipeline and report
	OFFLINE=$${OFFLINE:-1} $(RUN) python -m capstone.run_capstone

baseline: ## re-record the golden-dataset baseline (regression/baselines/support_v1.json)
	OFFLINE=$${OFFLINE:-1} $(RUN) python -m regression.regression_suite

synthetic: ## DeepEval Synthesizer: 5 seeds x 20 = 100 goldens
	$(RUN) python -m regression.synthetic_data --per-seed 20

requirements: ## regenerate requirements.txt from uv.lock (for pip users)
	$(UV) export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt

clean: ## remove generated results and caches
	rm -rf reports/results .deepeval .pytest_cache **/__pycache__
