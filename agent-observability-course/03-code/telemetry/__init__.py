"""Telemetry wiring for Atlas: OpenTelemetry, Langfuse, OpenInference, LangSmith,
Prometheus metrics, JSON logs and the local span store used in offline mode."""

import sys as _sys
from pathlib import Path as _Path

_SRC = _Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in _sys.path:  # allow running from a checkout without `pip install -e .`
    _sys.path.insert(0, str(_SRC))
