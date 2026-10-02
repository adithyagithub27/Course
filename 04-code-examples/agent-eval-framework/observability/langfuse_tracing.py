"""
Langfuse v4 tracing for the TechCorp support agent (Module 9.2, Lab 9.1).

Langfuse 4 is built on OpenTelemetry. The API this course uses:

    from langfuse import Langfuse, get_client, observe, propagate_attributes
    @observe(name="support-agent", as_type="agent")       # a span per call
    with propagate_attributes(user_id=..., session_id=..., tags=[...], version=...):
        ...                                                # trace-level attributes
    get_client().start_as_current_observation(name=..., as_type="generation", model=...)
    get_client().create_score(trace_id=..., name=..., value=...)   # attach an eval score
    get_client().flush()

(There is no ``langfuse.decorators``, ``langfuse_context`` or
``update_current_trace`` in v4; trace attributes come from propagate_attributes.)

Live: set LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_BASE_URL and
traces appear in the Langfuse UI. Offline (no keys): spans go to an in-memory
OpenTelemetry exporter so the demo prints the same trace in the terminal.

    python -m observability.langfuse_tracing "What is your refund policy?"
"""

from __future__ import annotations

import os
import sys
from typing import Any

from langfuse import Langfuse, get_client, observe, propagate_attributes
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agents.llm import get_client as get_llm_client
from agents.support_agent import execute_tool, run_support_agent
from config.settings import cost_usd, langfuse_configured

_STATE: dict[str, Any] = {"client": None, "exporter": None}
LOCAL_SCORES: list[dict] = []  # offline record of create_score calls


def init_langfuse() -> Langfuse:
    """Create the Langfuse client once. Offline: capture spans in memory."""
    if _STATE["client"] is not None:
        return _STATE["client"]
    if langfuse_configured():
        client = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            base_url=os.getenv("LANGFUSE_BASE_URL", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")),
            environment=os.getenv("LANGFUSE_ENVIRONMENT", "development"),
        )
    else:
        exporter = InMemorySpanExporter()
        client = Langfuse(
            public_key="pk-lf-offline",
            secret_key="sk-lf-offline",
            base_url="http://127.0.0.1:9",  # never contacted: spans go to the in-memory exporter
            span_exporter=exporter,
            flush_at=1,
        )
        _STATE["exporter"] = exporter
    _STATE["client"] = client
    return client


class TracedOpenAI:
    """Wraps the OpenAI client so every chat call becomes a Langfuse generation."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.chat = self
        self.completions = self

    def create(self, **kwargs: Any) -> Any:
        model = kwargs.get("model", "")
        with get_client().start_as_current_observation(
            name=f"chat {model}", as_type="generation", model=model, input=kwargs.get("messages")
        ) as gen:
            resp = self._inner.chat.completions.create(**kwargs)
            usage = resp.usage
            msg = resp.choices[0].message
            out = msg.content or [tc.function.name for tc in (msg.tool_calls or [])]
            gen.update(
                output=out,
                usage_details={"input": usage.prompt_tokens, "output": usage.completion_tokens},
                cost_details={"total": cost_usd(model, usage.prompt_tokens, usage.completion_tokens)},
            )
            return resp


@observe(name="tool", as_type="tool")
def traced_tool(name: str, arguments: dict) -> str:
    get_client().update_current_span(name=f"tool {name}", input=arguments)
    result = execute_tool(name, arguments)
    level = "WARNING" if result.startswith(("No relevant", "Customer not found")) else "DEFAULT"
    get_client().update_current_span(output=result, level=level)
    return result


def traced_support_agent(question: str, *, user_id: str = "anonymous", session_id: str | None = None,
                         version: str = "v1", tool_executor: Any = None) -> dict:
    """Run the support agent inside one Langfuse trace (initialise the client first)."""
    init_langfuse()
    return _traced_run(question, user_id=user_id, session_id=session_id, version=version, tool_executor=tool_executor)


@observe(name="support-agent", as_type="agent")
def _traced_run(question: str, *, user_id: str, session_id: str | None, version: str, tool_executor: Any) -> dict:
    with propagate_attributes(user_id=user_id, session_id=session_id, tags=["techcorp", "support"],
                              version=version, metadata={"agent": "support"}):
        result = run_support_agent(question, client=TracedOpenAI(get_llm_client()),
                                   tool_executor=tool_executor or traced_tool)
        result["trace_id"] = get_client().get_current_trace_id()
    return result


def score_trace(trace_id: str, name: str, value: float, comment: str | None = None) -> None:
    """Attach an evaluation score to a trace (Langfuse create_score)."""
    if langfuse_configured():
        get_client().create_score(trace_id=trace_id, name=name, value=value, comment=comment, data_type="NUMERIC")
    else:
        LOCAL_SCORES.append({"trace_id": trace_id, "name": name, "value": value, "comment": comment})


def offline_spans(trace_id: str | None = None) -> list[dict]:
    """Spans captured offline, oldest first, as plain dicts."""
    exporter = _STATE["exporter"]
    if exporter is None:
        return []
    init_langfuse().flush()
    rows = []
    for s in exporter.get_finished_spans():
        if trace_id and format(s.context.trace_id, "032x") != trace_id:
            continue
        a = s.attributes or {}
        rows.append({
            "name": s.name,
            "type": a.get("langfuse.observation.type", "span"),
            "start": s.start_time, "duration_ms": round((s.end_time - s.start_time) / 1e6, 2),
            "level": a.get("langfuse.observation.level", "DEFAULT"),
            "usage": a.get("langfuse.observation.usage_details"),
            "cost": a.get("langfuse.observation.cost_details"),
            "output": str(a.get("langfuse.observation.output", ""))[:80],
            "user_id": a.get("user.id"), "session_id": a.get("session.id"),
            "parent": s.parent.span_id if s.parent else None, "span_id": s.context.span_id,
        })
    rows.sort(key=lambda r: r["start"])
    return rows


def print_trace(trace_id: str) -> None:
    spans = offline_spans(trace_id)
    depth: dict[int, int] = {}
    for s in spans:
        d = depth.get(s["parent"], -1) + 1 if s["parent"] else 0
        depth[s["span_id"]] = d
        extra = f" usage={s['usage']}" if s["usage"] else ""
        flag = " <-- WARNING" if s["level"] == "WARNING" else ""
        print(f"{'  ' * d}{s['type']:<10} {s['name']:<32}{extra}{flag}")
        if s["type"] == "tool":
            print(f"{'  ' * d}           output: {s['output']}")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is your refund policy?"
    r = traced_support_agent(q, user_id="CUST-001", session_id="demo-session")
    print(f"Answer: {r['response']}\nTrace id: {r['trace_id']}")
    if not langfuse_configured():
        print_trace(r["trace_id"])
    get_client().flush()
