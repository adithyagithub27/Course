"""OpenInference auto-instrumentation for the OpenAI SDK (Section 3.5).

``OpenAIInstrumentor().instrument(tracer_provider=provider)`` wraps every
``client.chat.completions.create`` call in a span with OpenInference attributes
(``llm.token_count.prompt``, ``llm.model_name`` ...). Note: the otel-contrib
``opentelemetry-instrumentation-openai-v2`` package failed to import at
verification time, so the course uses OpenInference.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("atlas.openinference")
_INSTRUMENTED = False

try:  # pragma: no cover - import guard
    from openinference.instrumentation.openai import OpenAIInstrumentor

    OPENINFERENCE_AVAILABLE = True
except Exception:  # noqa: BLE001
    OPENINFERENCE_AVAILABLE = False
    OpenAIInstrumentor = None  # type: ignore[assignment,misc]


def instrument_openai(tracer_provider: Any) -> bool:
    """Instrument once; returns True if active. Instrumenting twice double-counts spans."""
    global _INSTRUMENTED
    if not OPENINFERENCE_AVAILABLE:
        log.info("openinference not installed; skipping auto-instrumentation")
        return False
    if _INSTRUMENTED:
        return True
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
    _INSTRUMENTED = True
    return True


def setup_openinference(provider: Any) -> bool:
    """Alias of :func:`instrument_openai` (the name used in the lecture scripts)."""
    return instrument_openai(provider)


def uninstrument_openai() -> None:
    global _INSTRUMENTED
    if OPENINFERENCE_AVAILABLE and _INSTRUMENTED:
        OpenAIInstrumentor().uninstrument()
    _INSTRUMENTED = False


def is_instrumented() -> bool:
    return _INSTRUMENTED
