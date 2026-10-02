# Agent Evaluation Framework - reproducible runner for CI.
# Installs exactly what uv.lock pins; runs the offline suite by default.
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 OFFLINE=1

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-install-project
COPY . .
RUN uv sync --locked

# Offline suite by default. For live evals: docker run -e OFFLINE=0 -e OPENAI_API_KEY ... make eval
CMD ["uv", "run", "pytest", "-q"]
