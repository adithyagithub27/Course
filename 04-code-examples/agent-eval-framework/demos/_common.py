"""Shared helpers for the lecture demos: version banner and simple tables."""

from __future__ import annotations

import importlib.metadata as md
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from config.settings import agent_model, is_offline, judge_model  # noqa: E402

PACKAGES = ["openai", "deepeval", "ragas", "langfuse", "mcp", "opentelemetry-sdk"]


def version(pkg: str) -> str:
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return "not installed"


def banner(title: str, packages: list[str] | None = None) -> None:
    """The version banner every code lecture opens with (CLAUDE.md)."""
    pkgs = packages or ["openai", "deepeval"]
    mode = "OFFLINE (mock LLM + mock judge)" if is_offline() else f"LIVE (agent {agent_model()}, judge {judge_model()})"
    print("=" * 72)
    print(title)
    print("Verified: " + " | ".join(f"{p} {version(p)}" for p in pkgs))
    print(f"Mode: {mode}")
    print("=" * 72)


def table(rows: list[dict], cols: list[str] | None = None, width: int = 28) -> None:
    if not rows:
        print("(no rows)")
        return
    cols = cols or list(rows[0].keys())
    widths = {c: min(width, max(len(c), *(len(str(r.get(c, ""))) for r in rows))) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    print("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, ""))[: widths[c]].ljust(widths[c]) for c in cols))
