# Riley / Maple Street Dental - common commands.
# Uses uv when available; `make install PIP=1` falls back to pip in the active venv.

AGENT ?= agents/s05_booking_agent.py
PY ?= uv run python
PYTEST ?= uv run pytest

ifdef PIP
PY = python
PYTEST = python -m pytest
endif

.PHONY: help install install-all download-files console console-text mock dev start test test-agent eval \
        wer latency simulate lint format docker-build docker-run clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

install:  ## Install the project with dev tools (uv sync --extra dev)
ifdef PIP
	pip install -e ".[dev]"
else
	uv sync --extra dev
endif

install-all:  ## Install every extra (dev, pipecat, observability)
ifdef PIP
	pip install -e ".[dev,pipecat,observability]"
else
	uv sync --all-extras
endif

download-files:  ## Download VAD and turn-detector weights (once)
	$(PY) agents/s03_hello_agent.py download-files

console:  ## Talk to an agent locally: make console AGENT=agents/s13_capstone_receptionist.py
	$(PY) $(AGENT) console

console-text:  ## Type instead of talk: make console-text AGENT=...
	$(PY) $(AGENT) console --text

mock:  ## Zero-cost practice: scripted fake LLM, text I/O (make mock AGENT=...)
	MOCK_MODE=1 $(PY) $(AGENT) console --text

dev:  ## Dev mode with hot reload; connect from the Agents Playground
	$(PY) $(AGENT) dev

start:  ## Production mode
	$(PY) $(AGENT) start

test:  ## Offline unit tests (no keys needed)
	$(PYTEST) tests/unit -q

test-agent:  ## LiveKit behavior tests (live ones need OPENAI_API_KEY)
	$(PYTEST) tests/agent -q

eval:  ## DeepEval judge + WER + latency reports
	$(PYTEST) tests/evals -q
	$(PY) tests/evals/stt_wer_eval.py
	$(PY) tests/evals/latency_report.py

wer:  ## WER report (offline)
	$(PY) tests/evals/stt_wer_eval.py

latency:  ## Latency report vs budget (offline sample data by default)
	$(PY) tests/evals/latency_report.py $(FILES)

simulate:  ## Simulated callers vs Riley (needs OPENAI_API_KEY; add ARGS=--mock for free)
	$(PY) tests/evals/simulated_caller.py $(ARGS)

lint:  ## Ruff lint + format check
	uv run ruff check .
	uv run ruff format --check .

format:  ## Auto-fix lint and format
	uv run ruff check --fix .
	uv run ruff format .

docker-build:  ## Build the production image (copies deploy/.dockerignore to the context root)
	cp deploy/.dockerignore .dockerignore
	docker build -f deploy/Dockerfile -t riley-agent .

docker-run:  ## Run the image with your .env
	docker run --rm --env-file .env riley-agent

clean:  ## Remove caches and local metrics
	rm -rf .pytest_cache .ruff_cache metrics console-recordings
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
