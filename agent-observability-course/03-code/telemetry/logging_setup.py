"""Structured JSON logs correlated with the active trace.

Every record carries ``trace_id`` and ``span_id`` when a span is active, so a log
line in Loki/CloudWatch links to the trace in Langfuse/Jaeger.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

from northwind.pii import mask_text

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    """One JSON object per line; extra kwargs become fields; PII masked in ``message``."""

    def __init__(self, *, service: str = "atlas", mask_pii: bool = True) -> None:
        super().__init__()
        self.service = service
        self.mask_pii = mask_pii

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if self.mask_pii:
            msg = mask_text(msg, hash_ids=True)
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "service": self.service,
            "message": msg,
        }
        span = trace.get_current_span()
        ctx = span.get_span_context() if span is not None else None
        if ctx is not None and ctx.is_valid:
            payload["trace_id"] = f"{ctx.trace_id:032x}"
            payload["span_id"] = f"{ctx.span_id:016x}"
        for k, v in record.__dict__.items():
            if k not in _RESERVED and not k.startswith("_"):
                payload[k] = v if isinstance(v, (str, int, float, bool)) or v is None else str(v)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(
    level: str = "INFO", *, stream: Any = None, service: str = "atlas"
) -> logging.Logger:
    """Install the JSON formatter on the ``atlas`` logger (idempotent)."""
    logger = logging.getLogger("atlas")
    logger.setLevel(level.upper())
    logger.propagate = False
    for h in list(logger.handlers):
        logger.removeHandler(h)
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter(service=service))
    logger.addHandler(handler)
    # keep third-party chatter down
    for noisy in ("httpx", "httpcore", "langfuse", "litellm", "LiteLLM", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logger


def get_logger(name: str = "atlas") -> logging.Logger:
    return logging.getLogger(name if name.startswith("atlas") else f"atlas.{name}")
