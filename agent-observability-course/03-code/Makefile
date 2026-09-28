# Atlas — AI Agent Observability & Cost Control course repo
#
# Flags (all optional):
#   SEED=7            replay/swarm seed                 SCENARIO=loop        incident preset / scenario
#   CACHE=1 DIET=1 ROUTER=1   cost levers (Section 6)  LANGFUSE=1           also push replayed traces to Langfuse
#   PROM=1            start the collector/Prometheus/Grafana stack before `make run`
#   RPS=2 DURATION=60 swarm load                       N=1                  incident number for `make incident`
#
# Examples:  make replay SCENARIO=cost_spike     make replay CACHE=1 DIET=1 ROUTER=1
#            make run SCENARIO=slow_provider     make swarm RPS=5 DURATION=30 SCENARIO=loop

PY      ?= python
UV      ?= uv
SEED    ?= 7
SESSIONS ?= 4000
SCENARIO ?=
CACHE   ?= 0
DIET    ?= 0
ROUTER  ?= 0
LANGFUSE ?= 0
PROM    ?= 0
RPS     ?= 2
DURATION ?= 60
N       ?= 1
PORT    ?= 8000

export OFFLINE ?= 1
export PYTHONPATH := $(CURDIR):$(CURDIR)/src:$(PYTHONPATH)
export ATLAS_PROMPT_CACHE := $(CACHE)
export ATLAS_CONTEXT_DIET := $(DIET)
export ATLAS_ROUTER_MODE := $(ROUTER)
export ATLAS_SCENARIO := $(SCENARIO)

SCENARIO_FLAG = $(if $(SCENARIO),--incidents $(SCENARIO),)
LANGFUSE_FLAG = $(if $(filter 1,$(LANGFUSE)),--langfuse,)

.PHONY: help install run swarm replay console test test-unit test-integration eval judge feedback drift dataset \
        budget-check lint format incidents incident report stack stack-down langfuse-up langfuse-down clean student-repo

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## create the venv and install with dev extras (uv; falls back to pip)
	@command -v $(UV) >/dev/null 2>&1 && ($(UV) venv --python 3.11 && $(UV) pip install -e ".[dev]") || (python -m venv .venv && .venv/bin/pip install -e ".[dev]")
	@cp -n .env.example .env 2>/dev/null || true
	@echo "Now: source .venv/bin/activate && make test"

run: ## start Atlas (uvicorn) — respects SCENARIO/CACHE/DIET/ROUTER, PROM=1 starts the metrics stack
	@if [ "$(PROM)" = "1" ]; then docker compose -f deploy/docker-compose.observability.yml up -d prometheus grafana otel-collector; fi
	$(PY) -m uvicorn app.server:app --host 0.0.0.0 --port $(PORT) --reload

swarm: ## drive a running Atlas with seeded traffic
	$(PY) simulator/swarm.py --url http://127.0.0.1:$(PORT) --rps $(RPS) --duration $(DURATION) --seed $(SEED) $(SCENARIO_FLAG)

replay: ## replay a full day of spans offline into the local store (and Langfuse with LANGFUSE=1)
	$(PY) simulator/replay.py --seed $(SEED) --sessions $(SESSIONS) --clear $(SCENARIO_FLAG) $(LANGFUSE_FLAG)

console: ## open the Ops Console (Streamlit if installed, else text)
	$(PY) console/ops_console.py --seed $(SEED) $(if $(SCENARIO),--incidents $(SCENARIO),)

console-text: ## text-mode Ops Console
	$(PY) console/ops_console.py --text --seed $(SEED) $(if $(SCENARIO),--incidents $(SCENARIO),)

test: ## all tests offline (unit + integration + budget gate)
	$(PY) -m pytest -q

test-unit: ## unit tests only
	$(PY) -m pytest -q tests/unit

test-integration: ## integration tests only
	$(PY) -m pytest -q tests/integration

eval: judge ## alias for judge

judge: ## sampled online judge over the local store (offline heuristic unless OPENAI_API_KEY and OFFLINE=0)
	$(PY) evals/online_judge.py --seed $(SEED) $(if $(filter 1,$(OFFLINE)),--dry-run,)

feedback: ## feedback vs judge correlation
	$(PY) evals/feedback.py --seed $(SEED)

drift: ## weekly drift report (synthetic if the store is empty)
	$(PY) evals/drift_report.py --seed $(SEED)

dataset: ## promote bad traces to a dataset (JSONL, and Langfuse with LANGFUSE=1)
	$(PY) evals/to_dataset.py --seed $(SEED) $(LANGFUSE_FLAG)

budget-check: ## CI budget gate: replay the day and assert cost/session and p95 budgets
	$(PY) -m pytest -q tests/budget

lint: ## ruff check + format check
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

format: ## ruff format
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

incidents: ## regenerate incidents/*/spans.jsonl deterministically
	$(PY) incidents/generate.py

incident: ## load incident N into a temp store and open the text console (make incident N=2)
	@$(PY) -c "import sys; sys.path[:0]=['.','src']; from telemetry.local_store import LocalSpanStore; from console.ops_console import build_summary, render_text; from northwind.config import Settings; import glob; d=sorted(glob.glob('incidents/incident-0$(N)-*'))[0]; s=LocalSpanStore.from_jsonl(d+'/spans.jsonl', d+'/scores.jsonl'); print(render_text(build_summary(s, Settings.from_env())))"

report: ## weekly markdown ops report from the local store
	@$(PY) -c "import sys; sys.path[:0]=['.','src']; from telemetry.local_store import LocalSpanStore; from northwind.report import weekly_report, ReportInputs; from northwind.config import Settings; s=LocalSpanStore(Settings.from_env().local_store_path); print(weekly_report(ReportInputs(records=s.cost_records('request'), latencies=s.latency_samples(), judge_scores=s.score_values('judge_overall'), feedback_positive=sum(1 for x in s.scores(name='user_feedback') if x.value>=0.75), feedback_negative=sum(1 for x in s.scores(name='user_feedback') if x.value<=0.25))))"

stack: ## OTel collector + Prometheus + Grafana (+ Atlas) via docker compose
	docker compose -f deploy/docker-compose.observability.yml up -d --build

stack-down:
	docker compose -f deploy/docker-compose.observability.yml down

langfuse-up: ## self-hosted Langfuse
	docker compose -f deploy/docker-compose.langfuse.yml up -d

langfuse-down:
	docker compose -f deploy/docker-compose.langfuse.yml down

clean: ## remove local store, caches
	rm -rf .atlas .pytest_cache .ruff_cache **/__pycache__

student-repo: ## copy of the repo without instructor-only files
	rm -rf ../03-code-student && cp -r . ../03-code-student && rm -f ../03-code-student/incidents/incident-04-project/solution.md && echo "../03-code-student ready"
