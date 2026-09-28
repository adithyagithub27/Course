"""Langfuse v4 (OpenTelemetry-based) wiring.

Verified against langfuse 4.15:

* ``Langfuse(public_key=, secret_key=, base_url=, environment=, release=, sample_rate=,
  mask=, blocked_instrumentation_scopes=, tracer_provider=, should_export_span=)``
* ``observe(as_type=...)`` with types generation | embedding | span | agent | tool |
  chain | retriever | evaluator | guardrail
* ``get_client()`` then ``start_as_current_observation(name=, as_type=, input=)``,
  ``update_current_generation(model=, usage_details=, cost_details=, completion_start_time=)``,
  ``update_current_span(...)``, ``score_current_trace(...)``, ``create_score(...)``,
  ``create_prompt / get_prompt``, ``create_dataset / create_dataset_item(source_trace_id=)``,
  ``flush()``, ``shutdown()``.
* **There is no ``update_current_trace`` in v4.** Trace-level ``session_id``, ``user_id``,
  ``tags`` and ``metadata`` are set with the ``propagate_attributes(...)`` context manager,
  which stamps them on the current span and every child. The raw span attributes are
  ``session.id``, ``user.id``, ``langfuse.trace.tags`` and ``langfuse.trace.metadata``.
* By default Langfuse only exports spans it created or spans carrying ``gen_ai.*``
  attributes. We pass ``should_export_span`` so every span from the ``atlas`` tracer
  is exported (guardrail and step spans have no ``gen_ai.*`` attribute).

Everything is guarded: without keys every helper is a no-op.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from typing import Any

from northwind.config import Settings, get_settings
from northwind.pii import langfuse_mask

log = logging.getLogger("atlas.langfuse")

_CLIENT: Any = None
_ENABLED = False

try:  # pragma: no cover - import guard
    from langfuse import Langfuse, get_client, observe, propagate_attributes

    LANGFUSE_AVAILABLE = True
except Exception:  # noqa: BLE001
    LANGFUSE_AVAILABLE = False
    Langfuse = None  # type: ignore[assignment]

    def observe(*_a: Any, **_k: Any):  # type: ignore[no-redef]
        def deco(fn):  # type: ignore[no-untyped-def]
            return fn

        return deco if not _a or not callable(_a[0]) else _a[0]

    def get_client(*_a: Any, **_k: Any) -> Any:  # type: ignore[no-redef]
        return None

    def propagate_attributes(**_k: Any):  # type: ignore[no-redef]
        return nullcontext()


def _should_export(span: Any) -> bool:
    """Export our own spans and anything that looks GenAI-shaped."""
    scope = getattr(getattr(span, "instrumentation_scope", None), "name", "") or ""
    if scope.startswith("atlas") or scope.startswith("langfuse"):
        return True
    attrs = getattr(span, "attributes", None) or {}
    return any(str(k).startswith("gen_ai") or str(k).startswith("langfuse") for k in attrs)


def init_langfuse(settings: Settings | None = None, *, tracer_provider: Any = None) -> Any:
    """Create the Langfuse client if keys are configured; return it (or None)."""
    global _CLIENT, _ENABLED
    settings = settings or get_settings()
    if not LANGFUSE_AVAILABLE or not settings.langfuse_enabled:
        _ENABLED = False
        _CLIENT = None
        return None
    _CLIENT = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        base_url=settings.langfuse_base_url,
        environment=settings.langfuse_environment,
        release=settings.langfuse_release,
        sample_rate=settings.langfuse_sample_rate,
        mask=langfuse_mask,
        blocked_instrumentation_scopes=["httpx", "urllib3", "sqlite3"],
        tracer_provider=tracer_provider,
        should_export_span=_should_export,
        flush_at=50,
        flush_interval=2.0,
    )
    _ENABLED = True
    return _CLIENT


def setup_langfuse(provider: Any = None, settings: Settings | None = None) -> Any:
    """Alias of :func:`init_langfuse`: attach Langfuse's span processor to ``provider``."""
    return init_langfuse(settings, tracer_provider=provider)


def langfuse_enabled() -> bool:
    return _ENABLED and _CLIENT is not None


def client() -> Any:
    """The configured client, or None when disabled."""
    return _CLIENT if langfuse_enabled() else None


@contextmanager
def trace_attributes(
    *,
    session_id: str | None = None,
    user_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    trace_name: str | None = None,
) -> Iterator[None]:
    """v4 replacement for ``update_current_trace``; no-op when Langfuse is disabled."""
    if not langfuse_enabled():
        yield
        return
    with propagate_attributes(
        session_id=session_id, user_id=user_id, tags=tags, metadata=metadata, trace_name=trace_name
    ):
        yield


def score_current_trace(
    name: str, value: float | str, *, comment: str | None = None, data_type: str | None = None
) -> None:
    c = client()
    if c is None:
        return
    try:
        c.score_current_trace(name=name, value=value, comment=comment, data_type=data_type)
    except Exception as exc:  # noqa: BLE001
        log.warning("score_current_trace failed: %s", exc)


def create_score(
    trace_id: str,
    name: str,
    value: float | str,
    *,
    comment: str | None = None,
    data_type: str | None = None,
) -> bool:
    c = client()
    if c is None:
        return False
    try:
        c.create_score(
            trace_id=trace_id, name=name, value=value, comment=comment, data_type=data_type
        )
        return True
    except Exception as exc:  # noqa: BLE001
        log.warning("create_score failed: %s", exc)
        return False


def get_prompt_text(
    name: str, *, label: str = "production", fallback: str, cache_ttl_seconds: int = 60
) -> tuple[str, int | None]:
    """Fetch a text prompt with a local fallback; returns (text, version or None)."""
    c = client()
    if c is None:
        return fallback, None
    try:
        p = c.get_prompt(name, label=label, fallback=fallback, cache_ttl_seconds=cache_ttl_seconds)
        return p.prompt, getattr(p, "version", None)
    except Exception as exc:  # noqa: BLE001
        log.warning("get_prompt failed, using fallback: %s", exc)
        return fallback, None


def push_prompts(
    prompts: dict[str, str], *, name: str = "atlas-system", production_version: str = "v1"
) -> int:
    """Create prompt versions in Langfuse; label the chosen one ``production`` (Section 4.4)."""
    c = client()
    if c is None:
        return 0
    n = 0
    for version, text in prompts.items():
        labels = ["production"] if version == production_version else ["staging"]
        c.create_prompt(name=name, prompt=text, labels=labels, type="text", tags=[version])
        n += 1
    return n


def flush() -> None:
    c = client()
    if c is not None:
        try:
            c.flush()
        except Exception:  # noqa: BLE001
            pass


def shutdown() -> None:
    global _CLIENT, _ENABLED
    c = client()
    if c is not None:
        try:
            c.shutdown()
        except Exception:  # noqa: BLE001
            pass
    _CLIENT = None
    _ENABLED = False


__all__ = [
    "LANGFUSE_AVAILABLE",
    "client",
    "create_score",
    "flush",
    "get_client",
    "get_prompt_text",
    "init_langfuse",
    "langfuse_enabled",
    "observe",
    "propagate_attributes",
    "push_prompts",
    "score_current_trace",
    "setup_langfuse",
    "shutdown",
    "trace_attributes",
]
