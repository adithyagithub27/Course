"""The Friday loop, one conversation at a time (Lectures 1.1 and 5.6).

Runs the ``loop`` scenario (the ticket API answers every ``lookup_ticket`` with a retryable
error) for one question and prints cost, context size and steps as the loop runs. Spans go to
the local store, so the Ops Console "Live cost" page (``make console``) shows the meter climbing.

    make loop-demo                                                  # guards on (defaults)
    ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 make loop-demo       # guards off: runs to the deadline
    ATLAS_MAX_TOOL_RETRIES=2 make loop-demo                         # the 5.6 fix
    ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 PACE=0.1 make loop-demo   # sleep 10% of mock latency

With ``--url`` the question is POSTed to a running Atlas instead (start the server with the
guard variables you want: ``ATLAS_MAX_STEPS=0 ATLAS_MAX_TOOL_RETRIES=0 OFFLINE=1 make run``).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from northwind.config import Settings  # noqa: E402

QUESTION = "Where is my ticket TCK-100231?"
TENANT = "ops"
USER = "NW-40213"


def run_in_process(
    settings: Settings,
    *,
    message: str = QUESTION,
    tenant: str = TENANT,
    user_id: str = USER,
    session_id: str | None = None,
    store_path: str | None = None,
    every: int = 25,
    out: Any = sys.stdout,
) -> Any:
    """Run one ``loop`` conversation through the real agent; returns the ``AgentResult``."""
    from app.agent import AtlasAgent
    from telemetry.local_store import LocalSpanStore
    from telemetry.otel_setup import configure_tracing, force_flush

    store = LocalSpanStore(store_path) if store_path else None
    configure_tracing(settings, exporter_kind="none", store=store)
    agent = AtlasAgent(settings)
    printer = _StepPrinter(every=every, out=out)
    agent.on_step = printer  # type: ignore[attr-defined]
    result = agent.run(
        message,
        tenant=tenant,
        user_id=user_id,
        session_id=session_id or f"loop-demo-{int(time.time())}",
        scenario="loop",
    )
    force_flush()
    printer.final(result)
    return result


class _StepPrinter:
    """Callback the agent calls after every step: (step, context_tokens, result)."""

    def __init__(self, *, every: int, out: Any) -> None:
        self.every = max(1, every)
        self.out = out

    def __call__(self, step: int, context_tokens: int, result: Any) -> None:
        if step <= 10 or step % self.every == 0:
            g = result.generations[-1]
            cost = sum(x.cost_usd for x in result.generations)
            print(
                f"step {step:>4}  input {g.input_tokens:>7,} tok  step ${g.cost_usd:.4f}  "
                f"total ${cost:.4f}  model {g.model}",
                file=self.out,
                flush=True,
            )

    def final(self, r: Any) -> None:
        print(
            f"\noutcome={r.outcome}  steps={r.steps}  model_calls={r.model_calls}  "
            f"tool_calls={len(r.tool_calls)}  input_tokens={r.input_tokens:,}  "
            f"cached_tokens={r.cached_tokens:,}  cost=${r.cost_usd:.4f}  "
            f"latency={r.latency_ms / 1000:.1f}s  trace_id={r.trace_id}",
            file=self.out,
        )
        print(f"answer: {r.answer}", file=self.out)


def run_over_http(url: str, *, message: str = QUESTION, tenant: str = TENANT) -> dict[str, Any]:
    import httpx

    resp = httpx.post(
        url.rstrip("/") + "/chat",
        json={
            "message": message,
            "scenario": "loop",
            "session_id": f"loop-demo-{int(time.time())}",
        },
        headers={"X-Tenant": tenant, "X-User": USER},
        timeout=None,
    )
    data = resp.json()
    print(json.dumps(data, indent=2))
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="One conversation through the loop scenario.")
    ap.add_argument("--message", default=QUESTION)
    ap.add_argument("--tenant", default=TENANT)
    ap.add_argument("--url", default=None, help="POST to a running Atlas instead of in-process")
    ap.add_argument(
        "--pace",
        type=float,
        default=None,
        help="sleep this fraction of the simulated model latency (default ATLAS_MOCK_LATENCY_SCALE)",
    )
    ap.add_argument("--every", type=int, default=25, help="print every Nth step after step 10")
    ap.add_argument("--store", default=None, help="span store (default ATLAS_LOCAL_STORE)")
    args = ap.parse_args(argv)
    if args.url:
        run_over_http(args.url, message=args.message, tenant=args.tenant)
        return 0
    settings = Settings.from_env()
    overrides: dict[str, Any] = {"offline": True}
    if args.pace is not None:
        overrides["mock_latency_scale"] = args.pace
    settings = settings.with_overrides(**overrides)
    print(
        f"loop demo: max_steps={settings.max_steps or 'unlimited'}  "
        f"max_tool_retries={settings.max_tool_retries or 'unlimited'}  "
        f"deadline={settings.request_deadline_s:g}s  prompt_cache={int(settings.prompt_cache)}  "
        f"context_diet={int(settings.context_diet)}"
    )
    run_in_process(
        settings,
        message=args.message,
        tenant=args.tenant,
        store_path=args.store or settings.local_store_path or None,
        every=args.every,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
