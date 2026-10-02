"""OpenTelemetry provider, resource attributes, exporter selection and safe shutdown.

Exporter kinds (``OTEL_EXPORTER``):

* ``console``  — ConsoleSpanExporter, for Section 3 demos
* ``otlp``     — OTLP/HTTP to a collector, Phoenix or any OTLP backend
* ``file``     — JSON lines in ``.atlas/spans.jsonl``
* ``langfuse`` — Langfuse's own processor attached to this provider
* ``memory``   — InMemorySpanExporter, for tests
* ``none``     — no exporter

In every mode spans are **also** written to the local SQLite store (when a
path is configured) so the Ops Console works. Every exporter is wrapped in
:class:`SafeSpanExporter`: a broken backend can drop telemetry but can never
raise into a request, and ``BatchSpanProcessor`` bounds queue size and export
time (Section 13.5, "kill the observability backend").
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry.semconv._incubating.attributes import deployment_attributes as dep
from opentelemetry.semconv.resource import ResourceAttributes as RA

from northwind.config import Settings, get_settings
from telemetry.local_store import JsonlSpanExporter, LocalSpanStore, LocalStoreSpanExporter

log = logging.getLogger("atlas.telemetry")

TRACER_NAME = "atlas"


def _count_failure(name: str) -> None:
    """``atlas_telemetry_export_failures_total{name}`` (Lecture 13.5, alert AtlasTelemetryExportFailures)."""
    try:
        from telemetry.metrics import EXPORTER_FAILURES

        EXPORTER_FAILURES.labels(name).inc()
    except Exception:  # noqa: BLE001 - metrics must never break exporting
        pass


class SafeSpanExporter(SpanExporter):
    """Wrap any exporter so failures are counted, logged once and never raised."""

    def __init__(self, inner: SpanExporter, *, name: str = "exporter") -> None:
        self.inner = inner
        self.name = name
        self.failures = 0
        self.exported = 0
        self._warned = False

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            result = self.inner.export(spans)
        except Exception as exc:  # noqa: BLE001
            self.failures += 1
            _count_failure(self.name)
            if not self._warned:
                log.warning("telemetry exporter %s failed (%s); dropping spans", self.name, exc)
                self._warned = True
            return SpanExportResult.FAILURE
        if result == SpanExportResult.SUCCESS:
            self.exported += len(spans)
        else:
            self.failures += 1
            _count_failure(self.name)
        return result

    def shutdown(self) -> None:
        try:
            self.inner.shutdown()
        except Exception:  # noqa: BLE001
            pass

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        try:
            return bool(self.inner.force_flush(timeout_millis))
        except Exception:  # noqa: BLE001
            return False


class FailingSpanExporter(SpanExporter):
    """Test double: raises or times out like a dead backend."""

    def __init__(self, *, raise_exc: bool = True, delay_s: float = 0.0) -> None:
        self.raise_exc = raise_exc
        self.delay_s = delay_s
        self.calls = 0

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        self.calls += 1
        if self.delay_s:
            time.sleep(self.delay_s)
        if self.raise_exc:
            raise ConnectionError("observability backend is down")
        return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        return None

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return True


@dataclass
class TracingState:
    provider: TracerProvider | None = None
    settings: Settings | None = None
    memory_exporter: InMemorySpanExporter | None = None
    store: LocalSpanStore | None = None
    exporters: list[SafeSpanExporter] = field(default_factory=list)
    langfuse_client: Any = None


_STATE = TracingState()
_LOCK = threading.Lock()
_GLOBAL_SET = False


def build_resource(settings: Settings) -> Resource:
    """service.name, service.version, deployment.environment(.name)."""
    return Resource.create(
        {
            RA.SERVICE_NAME: settings.service_name,
            RA.SERVICE_VERSION: settings.langfuse_release,
            RA.DEPLOYMENT_ENVIRONMENT: settings.deployment_environment,
            dep.DEPLOYMENT_ENVIRONMENT_NAME: settings.deployment_environment,
            "atlas.offline": settings.offline,
        }
    )


def _make_exporter(kind: str, settings: Settings) -> SpanExporter | None:
    if kind == "console":
        return ConsoleSpanExporter()
    if kind == "otlp":
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        return OTLPSpanExporter(endpoint=settings.otel_endpoint, timeout=5)
    if kind == "file":
        path = Path(settings.local_store_path).with_suffix(".jsonl")
        return JsonlSpanExporter(path)
    if kind == "memory":
        return InMemorySpanExporter()
    return None  # none, langfuse (handled separately)


def configure_tracing(
    settings: Settings | None = None,
    *,
    exporter_kind: str | None = None,
    store: LocalSpanStore | None = None,
    extra_exporter: SpanExporter | None = None,
    batch: bool | None = None,
    set_global: bool = True,
) -> TracerProvider:
    """Build (or rebuild) the Atlas TracerProvider.

    Args:
        settings: defaults to :func:`northwind.config.get_settings`.
        exporter_kind: override ``settings.otel_exporter``.
        store: a :class:`LocalSpanStore` to mirror spans into (tests pass ``:memory:``).
        extra_exporter: any additional exporter (e.g. a test double).
        batch: use BatchSpanProcessor (default) or SimpleSpanProcessor (tests).
        set_global: also install as the global OTel provider (first call only).
    """
    global _GLOBAL_SET
    settings = settings or get_settings()
    kind = (exporter_kind or settings.otel_exporter).lower()
    use_batch = (kind not in {"memory"}) if batch is None else batch
    with _LOCK:
        shutdown_tracing()
        sampler = ParentBased(TraceIdRatioBased(settings.trace_sample_rate))
        provider = TracerProvider(resource=build_resource(settings), sampler=sampler)
        _STATE.provider = provider
        _STATE.settings = settings
        _STATE.exporters = []
        _STATE.memory_exporter = None

        def add(exp: SpanExporter, name: str, *, simple: bool = False) -> None:
            safe = SafeSpanExporter(exp, name=name)
            _STATE.exporters.append(safe)
            if use_batch and not simple:
                provider.add_span_processor(
                    BatchSpanProcessor(
                        safe,
                        max_queue_size=2048,
                        max_export_batch_size=256,
                        schedule_delay_millis=1000,
                        export_timeout_millis=5000,
                    )
                )
            else:
                provider.add_span_processor(SimpleSpanProcessor(safe))

        main = _make_exporter(kind, settings)
        if isinstance(main, InMemorySpanExporter):
            _STATE.memory_exporter = main
        if main is not None:
            add(main, kind, simple=(kind == "memory"))
        if extra_exporter is not None:
            add(extra_exporter, "extra")

        # Local store mirror (offline mode + Ops Console)
        if store is None and settings.local_store_path and kind != "memory":
            store = LocalSpanStore(settings.local_store_path)
        _STATE.store = store
        if store is not None:
            add(LocalStoreSpanExporter(store), "local_store", simple=not use_batch)

        if kind == "langfuse" or settings.langfuse_enabled:
            try:
                from telemetry.langfuse_setup import init_langfuse

                _STATE.langfuse_client = init_langfuse(settings, tracer_provider=provider)
            except Exception as exc:  # noqa: BLE001
                log.warning("Langfuse not initialised: %s", exc)

        if set_global and not _GLOBAL_SET:
            trace.set_tracer_provider(provider)
            _GLOBAL_SET = True
    return provider


def setup_tracing(settings: Settings | None = None, **kwargs: Any) -> TracerProvider:
    """Alias of :func:`configure_tracing` (the name used in the lecture scripts)."""
    return configure_tracing(settings, **kwargs)


def get_provider() -> TracerProvider:
    if _STATE.provider is None:
        configure_tracing()
    assert _STATE.provider is not None
    return _STATE.provider


def get_tracer(name: str = TRACER_NAME) -> trace.Tracer:
    """Tracer bound to *our* provider (not the global one) so tests can swap exporters."""
    return get_provider().get_tracer(name, "1.0.0")


def get_memory_exporter() -> InMemorySpanExporter | None:
    return _STATE.memory_exporter


def get_store() -> LocalSpanStore | None:
    return _STATE.store


def get_langfuse_client() -> Any:
    return _STATE.langfuse_client


def exporter_health() -> list[dict[str, Any]]:
    return [
        {"name": e.name, "exported": e.exported, "failures": e.failures} for e in _STATE.exporters
    ]


def force_flush(timeout_ms: int = 5000) -> bool:
    if _STATE.provider is None:
        return True
    ok = _STATE.provider.force_flush(timeout_ms)
    if _STATE.langfuse_client is not None:
        try:
            _STATE.langfuse_client.flush()
        except Exception:  # noqa: BLE001
            pass
    return ok


def shutdown_tracing(timeout_ms: int = 5000) -> None:
    """Flush and shut down. Bounded by ``timeout_ms``; never raises."""
    provider = _STATE.provider
    if provider is None:
        return
    try:
        provider.force_flush(timeout_ms)
        provider.shutdown()
    except Exception as exc:  # noqa: BLE001
        log.warning("tracing shutdown error ignored: %s", exc)
    if _STATE.langfuse_client is not None:
        try:
            _STATE.langfuse_client.shutdown()
        except Exception:  # noqa: BLE001
            pass
    _STATE.provider = None
    _STATE.langfuse_client = None
    _STATE.memory_exporter = None


def current_trace_id() -> str | None:
    """Hex trace id of the active span, or None."""
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx is None or not ctx.is_valid:
        return None
    return f"{ctx.trace_id:032x}"
