# Atlas helpdesk agent — production-ish image (uvicorn, non-root, no dev extras)
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN useradd --create-home --uid 10001 atlas
COPY pyproject.toml README.md ./
COPY src ./src
COPY app ./app
COPY telemetry ./telemetry
COPY simulator ./simulator
COPY evals ./evals
RUN pip install --upgrade pip && pip install .
USER atlas
ENV OFFLINE=1 OTEL_EXPORTER=otlp OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces \
    ATLAS_LOCAL_STORE=/tmp/atlas/spans.sqlite
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).status==200 else 1)"
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
