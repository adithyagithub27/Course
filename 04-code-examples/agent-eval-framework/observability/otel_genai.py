"""
OpenTelemetry GenAI semantic conventions for the support agent (Module 9.3).

Uses the official attribute names from the ``opentelemetry-semantic-conventions``
package (0.66b0). The GenAI conventions are still "incubating", so they live
under ``opentelemetry.semconv._incubating`` and names can change between
releases:

    from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as GenAI
    GenAI.GEN_AI_OPERATION_NAME      == "gen_ai.operation.name"
    GenAI.GEN_AI_PROVIDER_NAME       == "gen_ai.provider.name"
    GenAI.GEN_AI_REQUEST_MODEL       == "gen_ai.request.model"
    GenAI.GEN_AI_USAGE_INPUT_TOKENS  == "gen_ai.usage.input_tokens"
    GenAI.GEN_AI_TOOL_NAME           == "gen_ai.tool.name"

Span names follow the spec: "invoke_agent {agent}", "chat {model}",
"execute_tool {tool}". Any OTLP backend (Langfuse, Jaeger, Datadog, Grafana
Tempo) can read these spans.

    python -m observability.otel_genai "Look up my account, alice@example.com"
"""

from __future__ import annotations

import json
import sys
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes as GenAI
from opentelemetry.trace import Status, StatusCode

from agents.llm import get_client
from agents.support_agent import execute_tool, run_support_agent

AGENT_NAME = "techcorp-support"


def make_tracer(exporter: Any = None) -> tuple[trace.Tracer, InMemorySpanExporter]:
    """A tracer that writes to an in-memory exporter (swap in OTLPSpanExporter for a backend)."""
    exporter = exporter or InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "techcorp-support-agent"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider.get_tracer("techcorp.agent"), exporter


class OTelOpenAI:
    """Wraps the OpenAI client: one 'chat {model}' span per call with gen_ai.* attributes."""

    def __init__(self, inner: Any, tracer: trace.Tracer) -> None:
        self._inner, self._tracer = inner, tracer
        self.chat = self
        self.completions = self

    def create(self, **kwargs: Any) -> Any:
        model = kwargs.get("model", "")
        with self._tracer.start_as_current_span(f"chat {model}", kind=trace.SpanKind.CLIENT) as span:
            span.set_attribute(GenAI.GEN_AI_OPERATION_NAME, GenAI.GenAiOperationNameValues.CHAT.value)
            span.set_attribute(GenAI.GEN_AI_PROVIDER_NAME, GenAI.GenAiProviderNameValues.OPENAI.value)
            span.set_attribute(GenAI.GEN_AI_REQUEST_MODEL, model)
            if kwargs.get("temperature") is not None:
                span.set_attribute(GenAI.GEN_AI_REQUEST_TEMPERATURE, kwargs["temperature"])
            resp = self._inner.chat.completions.create(**kwargs)
            span.set_attribute(GenAI.GEN_AI_RESPONSE_MODEL, resp.model)
            span.set_attribute(GenAI.GEN_AI_RESPONSE_ID, resp.id)
            span.set_attribute(GenAI.GEN_AI_RESPONSE_FINISH_REASONS, [c.finish_reason for c in resp.choices])
            span.set_attribute(GenAI.GEN_AI_USAGE_INPUT_TOKENS, resp.usage.prompt_tokens)
            span.set_attribute(GenAI.GEN_AI_USAGE_OUTPUT_TOKENS, resp.usage.completion_tokens)
            return resp


def make_tool_executor(tracer: trace.Tracer):
    def run(name: str, arguments: dict) -> str:
        with tracer.start_as_current_span(f"execute_tool {name}", kind=trace.SpanKind.INTERNAL) as span:
            span.set_attribute(GenAI.GEN_AI_OPERATION_NAME, GenAI.GenAiOperationNameValues.EXECUTE_TOOL.value)
            span.set_attribute(GenAI.GEN_AI_TOOL_NAME, name)
            span.set_attribute(GenAI.GEN_AI_TOOL_TYPE, "function")
            span.set_attribute(GenAI.GEN_AI_TOOL_CALL_ARGUMENTS, json.dumps(arguments))
            result = execute_tool(name, arguments)
            span.set_attribute(GenAI.GEN_AI_TOOL_CALL_RESULT, result[:500])
            if result.startswith(("No relevant", "Customer not found")):
                span.set_status(Status(StatusCode.ERROR, "empty tool result"))
            return result

    return run


def run_with_otel(question: str, tracer: trace.Tracer, conversation_id: str = "conv-001") -> dict:
    with tracer.start_as_current_span(f"invoke_agent {AGENT_NAME}") as span:
        span.set_attribute(GenAI.GEN_AI_OPERATION_NAME, GenAI.GenAiOperationNameValues.INVOKE_AGENT.value)
        span.set_attribute(GenAI.GEN_AI_AGENT_NAME, AGENT_NAME)
        span.set_attribute(GenAI.GEN_AI_CONVERSATION_ID, conversation_id)
        result = run_support_agent(question, client=OTelOpenAI(get_client(), tracer), tool_executor=make_tool_executor(tracer))
        return result


def spans_as_rows(exporter: InMemorySpanExporter) -> list[dict]:
    rows = [{"name": s.name, "start": s.start_time, "attributes": {k: v for k, v in (s.attributes or {}).items() if k.startswith("gen_ai.")},
             "status": s.status.status_code.name} for s in exporter.get_finished_spans()]
    return sorted(rows, key=lambda r: r["start"])


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Look up my account, alice@example.com"
    tracer, exporter = make_tracer()
    r = run_with_otel(q, tracer)
    print(f"Answer: {r['response']}\n")
    for row in spans_as_rows(exporter):
        print(f"{row['name']}  [{row['status']}]")
        for k, v in row["attributes"].items():
            print(f"    {k} = {str(v)[:70]}")
