# Atlas — AI Agent Observability & Cost Control course repo
#
# Flags (all optional):
#   SEED=7            replay/swarm seed                 SCENARIO=loop        incident preset / scenario
#   CACHE=1 DIET=1 ROUTER=1   cost levers (Section 6)  LANGFUSE=1           also push replayed traces to Langfuse
#   PROM=1            start the collector/Prometheus/Grafana stack before `make run`
#   RPS=2 DURATION=60 swarm load                       N=1                  incident number for `make incident`
#   PACE=0.1          loop-demo: sleep this fraction of the mock's simulated latency
#   DAY=2026-09-21    replay another day (default 2026-09-14)   KEEP=1  replay without clearing the store
#   STORE=path        replay/report/console against another SQLite store
#   MSG="..."         langfuse-native: the question to trace
#
# SCENARIO takes a base scenario (loop ticket_flaky context_bloat retry_storm slow_provider
# prompt_regression) or an incident preset (cost_spike latency_regression quality_drift mixed).
# replay/swarm/console accept both; `make run` injects base scenarios only (presets are time
# windows over a day, which only replay and swarm can play).
#
# Examples:  make replay SCENARIO=cost_spike     make replay CACHE=1 DIET=1 ROUTER=1
#            make run SCENARIO=slow_provider     make swarm RPS=5 DURATION=30 SCENARIO=loop
#            ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 make loop-demo

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
PACE    ?=
DAY     ?=
STORE   ?=
KEEP    ?= 0
MSG     ?= How do I connect to the VPN from home?

BASE_SCENARIOS := loop ticket_flaky context_bloat retry_storm slow_provider prompt_regression

export OFFLINE ?= 1
export PYTHONPATH := $(CURDIR):$(CURDIR)/src:$(PYTHONPATH)
export ATLAS_PROMPT_CACHE := $(CACHE)
export ATLAS_CONTEXT_DIET := $(DIET)
export ATLAS_ROUTER_MODE := $(ROUTER)
ifneq ($(STORE),)
export ATLAS_LOCAL_STORE := $(STORE)
endif

# Only a base scenario is a valid ATLAS_SCENARIO for the server; presets go to --incidents.
# Without SCENARIO, an ATLAS_SCENARIO already in the environment is passed through untouched.
ifneq ($(SCENARIO),)
export ATLAS_SCENARIO := $(filter $(BASE_SCENARIOS),$(SCENARIO))
endif

SCENARIO_FLAG = $(if $(SCENARIO),--incidents $(SCENARIO),)
LANGFUSE_FLAG = $(if $(filter 1,$(LANGFUSE)),--langfuse,)

.PHONY: help install run swarm replay console console-text test test-unit test-integration eval judge feedback \
        drift dataset budget-check lint format incidents incident report stack stack-down langfuse-up \
        langfuse-down clean student-repo loop-demo langfuse-native prompts lock

help: ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## create the venv and install with dev extras (uv; falls back to pip)
	@command -v $(UV) >/dev/null 2>&1 && ($(UV) venv --python 3.11 && $(UV) pip install -e ".[dev]") || (python -m venv .venv && .venv/bin/pip install -e ".[dev]")
	@cp -n .env.example .env 2>/dev/null || true
	@echo "Now: source .venv/bin/activate && make test"

run: ## start Atlas (uvicorn) — respects SCENARIO/CACHE/DIET/ROUTER, PROM=1 starts the metrics stack
	@if [ -n "$(SCENARIO)" ] && [ -z "$(filter $(BASE_SCENARIOS),$(SCENARIO))" ]; then \
		echo "SCENARIO=$(SCENARIO) is an incident preset; make run takes one of: $(BASE_SCENARIOS)"; \
		echo "(use 'make replay SCENARIO=$(SCENARIO)' or 'make swarm SCENARIO=$(SCENARIO)')"; exit 2; fi
	@if [ "$(PROM)" = "1" ]; then docker compose -f deploy/docker-compose.observability.yml up -d prometheus grafana otel-collector; fi
	$(PY) -m uvicorn app.server:app --host 0.0.0.0 --port $(PORT) --reload

swarm: ## drive a running Atlas with seeded traffic
	$(PY) simulator/swarm.py --url http://127.0.0.1:$(PORT) --rps $(RPS) --duration $(DURATION) --seed $(SEED) $(SCENARIO_FLAG)

replay: ## replay a full day of spans offline into the local store (and Langfuse with LANGFUSE=1)
	$(PY) simulator/replay.py --seed $(SEED) --sessions $(SESSIONS) $(if $(filter 1,$(KEEP)),,--clear) \
		$(if $(DAY),--day $(DAY),) $(SCENARIO_FLAG) $(LANGFUSE_FLAG)

loop-demo: ## one conversation through the loop scenario (ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 = guards off)
	$(PY) simulator/loop_demo.py $(if $(PACE),--pace $(PACE),)

langfuse-native: ## run one request through the Langfuse-native @observe layer (Sections 4-5) and print the trace
	$(PY) -m app.langfuse_native "$(MSG)"

prompts: ## push the v1/v2 system prompts to Langfuse (needs keys; label v1 production)
	$(PY) -m app.prompts register

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

judge: ## sampled online judge over the local store (offline heuristic unless OPENAI_API_KEY and OFFLINE=0; LANGFUSE=1 also writes scores to Langfuse)
	$(PY) evals/online_judge.py --seed $(SEED) $(if $(filter 1,$(OFFLINE)),--dry-run,) $(LANGFUSE_FLAG)

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

incident: ## load incident N into .atlas/incident-0N.sqlite, print the text console (open the UI: make console STORE=.atlas/incident-0N.sqlite)
	@$(PY) -c "import sys, glob; sys.path[:0]=['.','src']; from telemetry.local_store import LocalSpanStore; from console.ops_console import build_summary, render_text; from northwind.config import Settings; d=sorted(glob.glob('incidents/incident-0$(N)-*'))[0]; s=LocalSpanStore('.atlas/incident-0$(N).sqlite'); s.clear(); s.import_jsonl(d+'/spans.jsonl', scores_path=d+'/scores.jsonl'); print(render_text(build_summary(s, Settings.from_env()))); print('UI: make console STORE=.atlas/incident-0$(N).sqlite')"

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

lock: ## refresh uv.lock after changing pyproject.toml
	$(UV) lock

student-repo: ## copy of the repo without instructor-only files
	rm -rf ../03-code-student && cp -r . ../03-code-student && rm -f ../03-code-student/incidents/incident-04-project/solution.md && echo "../03-code-student ready"
