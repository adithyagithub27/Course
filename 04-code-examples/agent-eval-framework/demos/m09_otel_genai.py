"""Lecture 9.3 - OpenTelemetry GenAI semantic conventions: the same agent run as
vendor-neutral spans with official gen_ai.* attribute names.

    uv run python demos/m09_otel_genai.py
"""
from _common import banner

from observability.otel_genai import make_tracer, run_with_otel, spans_as_rows

banner("Lecture 9.3 - OpenTelemetry GenAI conventions", ["openai", "opentelemetry-sdk", "opentelemetry-semantic-conventions"])
tracer, exporter = make_tracer()
r = run_with_otel("Look up my account, alice@example.com", tracer)
print(f"Answer: {r['response']}\n")
for row in spans_as_rows(exporter):
    print(f"{row['name']}  [status {row['status']}]")
    for k, v in row["attributes"].items():
        print(f"    {k} = {str(v)[:70]}")
print("\nSwap InMemorySpanExporter for OTLPSpanExporter to ship these to Langfuse, Jaeger, Tempo or Datadog.")
