"""Observed Riley: metrics, usage, cost per minute and tracing.

Lectures: 9.8 (export metrics for latency tests), 10.1 (what to measure), 10.2
(collecting metrics and usage), 10.3 (OpenTelemetry and Langfuse), 10.4 (cost per
minute), 10.6 (lab: call-quality report).

What it records for every call:

* Every ``metrics_collected`` event (EOU, STT, LLM, TTS, VAD) appended as one JSON line
  to ``$METRICS_DIR/<room>.jsonl``. ``tests/evals/latency_report.py`` reads these files.
* Per-turn latency from ``ChatMessage.metrics`` via ``conversation_item_added``.
* At shutdown: usage per model (``session.usage``) turned into dollars with
  ``maple.costs``, written as a ``call_summary`` line and logged.

Version note (livekit-agents 1.8): ``metrics_collected`` and ``metrics.UsageCollector``
still work but log deprecation warnings. The replacements are ``session.usage`` /
the ``session_usage_updated`` event for usage and ``ChatMessage.metrics`` for per-turn
latency. This file shows both so older tutorials still make sense.

Tracing (optional, enabled only when the env vars are set):

* Langfuse: ``LANGFUSE_PUBLIC_KEY``, ``LANGFUSE_SECRET_KEY``, ``LANGFUSE_HOST``.
* Any OTLP backend: ``OTEL_EXPORTER_OTLP_ENDPOINT`` (and ``OTEL_EXPORTER_OTLP_HEADERS``).

Requires the ``observability`` extra: ``uv sync --extra observability``.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    ConversationItemAddedEvent,
    JobContext,
    MetricsCollectedEvent,
    cli,
    metrics,
)

from common import (
    BookingToolsMixin,
    CallState,
    KnowledgeToolsMixin,
    create_session,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.costs import cost_breakdown, usage_from_model_usage

logger = logging.getLogger("s10.observed")


def setup_observability(service_name: str = "riley") -> str | None:
    """Configure an OpenTelemetry tracer provider if Langfuse or OTLP env vars are set.

    Returns the backend name ("langfuse" or "otlp"), or None when tracing is off.
    OpenTelemetry packages are imported lazily so the agent runs without them.
    """
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    backend: str | None = None
    if public_key and secret_key:
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
        auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{host}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic%20{auth}"
        backend = "langfuse"
    elif os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"):
        backend = "otlp"
    if backend is None:
        return None

    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning(
            "tracing env vars set but OpenTelemetry is not installed: uv sync --extra observability"
        )
        return None

    from livekit.agents.telemetry import set_tracer_provider

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    # allow_pii=False keeps transcripts out of spans; flip only if your retention policy allows.
    set_tracer_provider(provider, metadata={"clinic": "maple-street-dental"}, allow_pii=False)
    logger.info("tracing enabled via %s", backend)
    return backend


class MetricsExporter:
    """Append metrics as JSON lines, one file per room."""

    def __init__(self, directory: str | Path, room_name: str) -> None:
        self.path = Path(directory) / f"{room_name}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, record: dict[str, Any]) -> None:
        """Write one record (a dict that is JSON serialisable)."""
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")

    def write_metrics(self, agent_metrics: metrics.AgentMetrics, room: str) -> None:
        """Serialise a LiveKit metrics object (``type`` field included)."""
        record = agent_metrics.model_dump(mode="json")
        record["room"] = room
        self.write(record)


def attach_observers(session: AgentSession[CallState], ctx: JobContext, *, realtime: bool = False) -> None:
    """Wire metrics export, per-turn latency logs and the shutdown cost summary."""
    settings = get_settings()
    exporter = MetricsExporter(settings.metrics_dir, ctx.room.name)
    started = time.monotonic()

    @session.on("metrics_collected")
    def on_metrics(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        exporter.write_metrics(ev.metrics, ctx.room.name)

    @session.on("conversation_item_added")
    def on_item(ev: ConversationItemAddedEvent) -> None:
        item = ev.item
        if getattr(item, "role", None) == "assistant":
            report = item.metrics  # modern per-turn metrics
            if "e2e_latency" in report:
                logger.info("turn latency e2e=%.0f ms", report["e2e_latency"] * 1000)

    async def log_usage() -> None:
        call_seconds = time.monotonic() - started
        model_usage = [u.model_dump() for u in session.usage.model_usage]
        usage = usage_from_model_usage(model_usage, call_seconds, realtime=realtime)
        report = cost_breakdown(usage)
        logger.info("call cost report\n%s", report.format())
        exporter.write(
            {
                "type": "call_summary",
                "room": ctx.room.name,
                "call_seconds": round(call_seconds, 2),
                "model_usage": model_usage,
                "cost_components": dict(report.components),
                "cost_total": round(report.total, 6),
                "cost_per_minute": round(report.per_minute, 6),
                "outcome": session.userdata.call_outcome,
            }
        )

    ctx.add_shutdown_callback(log_usage)


class ObservedRiley(BookingToolsMixin, KnowledgeToolsMixin, Agent):
    """The booking + FAQ agent, unchanged: observability wraps the session, not the agent."""

    def __init__(self) -> None:
        self.scheduler = get_scheduler()
        super().__init__(
            instructions=prompts.build_instructions(today=self.scheduler.today, booking=True, knowledge=True),
        )

    async def on_enter(self) -> None:
        """Greet the caller."""
        self.session.say(prompts.GREETING)


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start Riley with metrics, usage and tracing attached."""
    setup_observability()
    ctx.log_context_fields = {"room": ctx.room.name}
    session = create_session(get_settings(), proc=ctx.proc, userdata=CallState(), max_tool_steps=5)
    attach_observers(session, ctx)
    await session.start(agent=ObservedRiley(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
