"""Drive a running Atlas server at N requests per second with seeded traffic.

    OFFLINE=1 make run                                # terminal 1
    python simulator/swarm.py --rps 5 --duration 60 --incidents cost_spike   # terminal 2

The 24-hour plan is compressed into ``--duration`` seconds; incidents keep their
relative position in the day.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import httpx  # noqa: E402

from northwind.latency import percentile  # noqa: E402
from simulator.scenarios import (  # noqa: E402
    INCIDENT_PRESETS,
    PlannedRequest,
    day_start,
    generate_day,
)


@dataclass
class SwarmStats:
    sent: int = 0
    ok: int = 0
    refused: int = 0
    errors: int = 0
    cost_usd: float = 0.0
    latencies_ms: list[float] = field(default_factory=list)
    outcomes: dict[str, int] = field(default_factory=dict)

    def render(self) -> str:
        p95 = percentile(self.latencies_ms, 95) if self.latencies_ms else 0.0
        p50 = percentile(self.latencies_ms, 50) if self.latencies_ms else 0.0
        return (
            f"sent={self.sent} ok={self.ok} refused(429)={self.refused} errors={self.errors} "
            f"cost=${self.cost_usd:.4f} p50={p50:.0f}ms p95={p95:.0f}ms outcomes={json.dumps(self.outcomes, sort_keys=True)}"
        )


def compress_plan(
    plan: list[PlannedRequest], duration_s: float
) -> list[tuple[float, PlannedRequest]]:
    """Map the 24h plan onto ``duration_s`` seconds of wall time; returns (offset_s, request)."""
    base = day_start()
    return [((r.ts - base) / 86_400 * duration_s, r) for r in plan]


async def _send(
    client: httpx.AsyncClient, req: PlannedRequest, stats: SwarmStats, sem: asyncio.Semaphore
) -> None:
    async with sem:
        body: dict[str, Any] = {"message": req.message, "session_id": req.session_id}
        if req.scenario:
            body["scenario"] = req.scenario
        headers = {"X-Tenant": req.tenant, "X-User": req.persona.user_id}
        t0 = time.perf_counter()
        try:
            resp = await client.post("/chat", json=body, headers=headers, timeout=60)
            stats.sent += 1
            stats.latencies_ms.append((time.perf_counter() - t0) * 1000)
            if resp.status_code == 200:
                data = resp.json()
                stats.ok += 1
                stats.cost_usd += float(data.get("cost_usd", 0.0))
                stats.outcomes[data.get("outcome", "?")] = (
                    stats.outcomes.get(data.get("outcome", "?"), 0) + 1
                )
            elif resp.status_code == 429:
                stats.refused += 1
            else:
                stats.errors += 1
        except httpx.HTTPError:
            stats.sent += 1
            stats.errors += 1


async def run_swarm(
    base_url: str,
    *,
    rps: float = 2.0,
    duration_s: float = 60.0,
    seed: int = 7,
    incidents: str = "none",
    concurrency: int = 16,
    sessions: int | None = None,
) -> SwarmStats:
    """Send ``rps * duration_s`` requests (plan compressed to the duration)."""
    total_requests = int(rps * duration_s)
    plan = generate_day(
        seed,
        sessions=sessions or max(1, int(total_requests / 1.6)),
        incidents=INCIDENT_PRESETS[incidents],
    )
    schedule = compress_plan(plan, duration_s)
    stats = SwarmStats()
    sem = asyncio.Semaphore(concurrency)
    started = time.perf_counter()
    async with httpx.AsyncClient(base_url=base_url) as client:
        tasks = []
        for offset, req in schedule:
            delay = offset - (time.perf_counter() - started)
            if delay > 0:
                await asyncio.sleep(delay)
            tasks.append(asyncio.create_task(_send(client, req, stats, sem)))
        await asyncio.gather(*tasks)
    return stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Swarm: drive Atlas with seeded multi-tenant traffic.")
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--rps", type=float, default=2.0)
    ap.add_argument("--duration", type=float, default=60.0, help="seconds")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--incidents", default="none", choices=sorted(INCIDENT_PRESETS))
    ap.add_argument("--concurrency", type=int, default=16)
    args = ap.parse_args(argv)
    stats = asyncio.run(
        run_swarm(
            args.url,
            rps=args.rps,
            duration_s=args.duration,
            seed=args.seed,
            incidents=args.incidents,
            concurrency=args.concurrency,
        )
    )
    print(stats.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
