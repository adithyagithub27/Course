# syntax=docker/dockerfile:1.7
# Production image for Riley (lecture 12.2).
#
# Build from the repo root (the build context must contain src/ and agents/):
#   cp deploy/.dockerignore .dockerignore      # Docker only reads .dockerignore at the context root
#   docker build -f deploy/Dockerfile -t riley-agent .
#   docker run --rm --env-file .env riley-agent
# `make docker-build` does both steps.
#
# Stages:
#   builder  - installs dependencies into /app/.venv with uv (compilers available here only)
#   runtime  - slim image, non-root user, model weights downloaded at build time

ARG PYTHON_VERSION=3.11
ARG AGENT_FILE=agents/s13_capstone_receptionist.py

# ---------------------------------------------------------------- builder
FROM python:${PYTHON_VERSION}-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# 1) dependencies only (cached until pyproject.toml or uv.lock changes)
#    --locked installs exactly the versions in the committed uv.lock and fails if it is stale.
COPY pyproject.toml README.md uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --extra observability

# 2) the project itself
COPY src ./src
COPY agents ./agents
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --extra observability

# pip alternative (no uv):
#   RUN python -m venv /app/.venv && /app/.venv/bin/pip install ".[observability]"

# ---------------------------------------------------------------- runtime
FROM python:${PYTHON_VERSION}-slim AS runtime
ARG AGENT_FILE

RUN useradd --create-home --uid 10001 riley
WORKDIR /app
COPY --from=builder --chown=riley:riley /app /app

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    AGENT_FILE=${AGENT_FILE}

USER riley

# Download VAD / turn-detector weights into the image so cold starts don't hit the network.
RUN python ${AGENT_FILE} download-files

# Agent name for telephony/explicit dispatch: pass -e LIVEKIT_AGENT_NAME=riley-receptionist
# (LiveKit Cloud deployments inject it for you).

# Health check / metrics port used by `start` (AgentServer default 8081).
EXPOSE 8081

CMD ["sh", "-c", "exec python \"$AGENT_FILE\" start"]
