"""Atlas Ops Console: cost, latency, quality, budgets and alerts over the local span store.

Two front ends over one :func:`build_summary`:

* Streamlit (``make console`` / ``streamlit run console/ops_console.py``) — optional extra ``dashboards``
* Text mode (``python console/ops_console.py --text``) — used in tests and CI logs

If the store is empty the console replays a day (``--seed``) so there is always something to look at.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from northwind.budget import Decision, TenantBudget  # noqa: E402
from northwind.config import TENANTS, Settings  # noqa: E402
from northwind.cost import rollup, rollup_nested, total_cost  # noqa: E402
from northwind.drift import compare_windows  # noqa: E402
from northwind.latency import by_group, hourly_p95, summarize  # noqa: E402
from northwind.slo import DEFAULT_SLOS, compute_slis  # noqa: E402
from telemetry.local_store import LocalSpanStore  # noqa: E402

try:  # pragma: no cover - optional dependency
    import streamlit as st

    STREAMLIT_AVAILABLE = True
except Exception:  # noqa: BLE001
    st = None  # type: ignore[assignment]
    STREAMLIT_AVAILABLE = False


def _hour(ts: float) -> int:
    return datetime.fromtimestamp(ts, tz=UTC).hour


def build_summary(store: LocalSpanStore, settings: Settings | None = None) -> dict[str, Any]:
    """Everything the console shows, as plain dicts (JSON-serialisable)."""
    settings = settings or Settings.from_env({})
    gens = store.cost_records("generation")
    reqs = store.cost_records("request")
    lat = store.latency_samples()
    judge = store.score_values("judge_overall")
    grounded = store.score_values("judge_grounded")
    fb = store.scores(name="user_feedback")
    start, end = store.time_range()
    day0 = start - (start % 86_400) if start else 0.0

    # cost -----------------------------------------------------------------------------
    # requests/sessions per tenant count chat requests (agent spans), not model calls
    by_tenant = {k: v.as_dict() for k, v in sorted(rollup(reqs, "tenant").items())}
    gen_by_tenant = rollup(gens, "tenant")
    for k, v in by_tenant.items():  # token and cache figures come from the generations
        g = gen_by_tenant.get(k)
        if g is not None:
            v["model_calls"] = g.requests
            v["cache_hit_ratio"] = round(g.cache_hit_ratio, 4)
    by_feature = {
        k: v.as_dict()
        for k, v in sorted(rollup(reqs, "feature").items(), key=lambda kv: -float(kv[1].cost_usd))
    }
    by_intent = {
        k: v.as_dict()
        for k, v in sorted(rollup(reqs, "intent").items(), key=lambda kv: -float(kv[1].cost_usd))
    }
    by_model = {k: v.as_dict() for k, v in sorted(rollup(gens, "model").items())}
    hourly_cost: dict[int, dict[str, float]] = {}
    for r in gens:
        h = _hour(r.timestamp)
        hourly_cost.setdefault(h, {})
        hourly_cost[h][r.tenant] = round(hourly_cost[h].get(r.tenant, 0.0) + r.cost_usd, 6)
    tenant_feature = {
        t: {f: v.as_dict() for f, v in d.items()}
        for t, d in rollup_nested(reqs, "tenant", "intent").items()
    }

    # latency ---------------------------------------------------------------------------
    lat_stats = summarize([s.total_ms for s in lat]).as_dict()
    ttft_stats = summarize([s.ttft_ms for s in lat if s.ttft_ms is not None]).as_dict()
    lat_by_tenant = {k: v.as_dict() for k, v in by_group(lat, "tenant").items()}
    lat_hourly = {
        int(_hour(k)): round(v, 1)
        for k, v in hourly_p95(
            [(s.start_time, s.duration_ms) for s in store.spans(kind="agent")]
        ).items()
    }

    # quality ---------------------------------------------------------------------------
    judge_hourly: dict[int, list[float]] = {}
    for sc in store.scores(name="judge_overall"):
        judge_hourly.setdefault(_hour(sc.timestamp), []).append(sc.value)
    quality = {
        "judge_overall_mean": round(sum(judge) / len(judge), 3) if judge else None,
        "judge_grounded_mean": round(sum(grounded) / len(grounded), 3) if grounded else None,
        "judge_count": len(judge),
        "judge_hourly_mean": {
            h: round(sum(v) / len(v), 3) for h, v in sorted(judge_hourly.items())
        },
        "feedback_count": len(fb),
        "feedback_positive_rate": round(sum(1 for s in fb if s.value >= 0.75) / len(fb), 3)
        if fb
        else None,
        "by_prompt_version": {},
    }
    by_pv: dict[str, list[float]] = {}
    judge_map = {s.trace_id: s.value for s in store.scores(name="judge_overall")}
    for sp in store.spans(kind="agent"):
        v = judge_map.get(sp.trace_id)
        if v is not None:
            by_pv.setdefault(str(sp.attr("atlas.prompt_version", "?")), []).append(v)
    quality["by_prompt_version"] = {
        k: {"n": len(v), "mean": round(sum(v) / len(v), 3)} for k, v in sorted(by_pv.items())
    }
    drift = None
    if judge and day0:
        split = day0 + 12 * 3600
        before = store.score_values("judge_overall", until=split)
        after = store.score_values("judge_overall", since=split)
        drift = compare_windows("judge_overall", before, after).as_dict()

    # budgets -----------------------------------------------------------------------------
    budgets = []
    for t in TENANTS:
        spent = float(by_tenant.get(t, {}).get("cost_usd", 0.0))
        b = TenantBudget(t, settings.tenant_soft_cap_usd, settings.tenant_hard_cap_usd)
        state = (
            Decision.REFUSE
            if spent >= b.hard_cap_usd
            else Decision.DEGRADE
            if spent >= b.soft_cap_usd
            else Decision.ALLOW
        )
        budgets.append(
            {
                "tenant": t,
                "spent_usd": round(spent, 4),
                "soft_cap_usd": b.soft_cap_usd,
                "hard_cap_usd": b.hard_cap_usd,
                "utilisation": round(spent / b.hard_cap_usd, 4) if b.hard_cap_usd else 0.0,
                "state": state.value,
            }
        )

    # SLOs / alerts ------------------------------------------------------------------------
    tools = store.tool_stats()
    tool_calls = sum(v["calls"] for v in tools.values())
    tool_errors = sum(v["errors"] for v in tools.values())
    snap = compute_slis(
        reqs,
        latency_budget_ms=settings.budget_p95_latency_ms,
        cost_budget_usd=settings.budget_cost_per_session_usd,
        judge_scores=judge,
        tool_calls=tool_calls,
        tool_errors=tool_errors,
    )
    slo_rows = [r for r in snap.report(DEFAULT_SLOS) if r["total"]]
    alerts: list[dict[str, str]] = []
    if lat_stats["count"] and lat_stats["p95"] > settings.budget_p95_latency_ms:
        alerts.append(
            {
                "severity": "page",
                "rule": "latency_p95",
                "detail": f"p95 {lat_stats['p95']:.0f} ms > {settings.budget_p95_latency_ms:.0f} ms",
            }
        )
    for b in budgets:
        if b["state"] != "allow":
            alerts.append(
                {
                    "severity": "ticket" if b["state"] == "degrade" else "page",
                    "rule": "tenant_budget",
                    "detail": f"{b['tenant']} at {b['utilisation']:.0%} of hard cap",
                }
            )
    if hourly_cost:
        # Cost *per request* per tenant per hour is flat through the daily load curve; a jump means
        # requests got more expensive (context bloat, retries), not that there were more of them.
        # Batch rule for the console: an hour is anomalous when its cost/request is > 2.5x the
        # tenant's median hour (hours with < 10 requests are skipped). The streaming equivalent is
        # the EWMA detector in northwind.budget (used by BudgetGuard.record).
        per_hour: dict[str, dict[int, list[float]]] = {}
        for r in reqs:
            per_hour.setdefault(r.tenant, {}).setdefault(_hour(r.timestamp), []).append(r.cost_usd)
        for t in TENANTS:
            hours = [h for h in range(24) if len(per_hour.get(t, {}).get(h, [])) >= 10]
            cpr = [sum(per_hour[t][h]) / len(per_hour[t][h]) for h in hours]
            if len(cpr) < 4:
                continue
            median = sorted(cpr)[len(cpr) // 2]
            flagged = [h for h, c in zip(hours, cpr) if c > 2.5 * median and c - median > 0.001]
            if flagged:
                when = ", ".join(f"{h:02d}:00" for h in flagged)
                alerts.append(
                    {
                        "severity": "ticket",
                        "rule": "cost_anomaly",
                        "detail": f"{t} cost per request anomalous at {when} (> 2.5x median hour)",
                    }
                )
    if drift and drift["status"] == "alert":
        alerts.append(
            {"severity": "ticket", "rule": "judge_drift", "detail": "; ".join(drift["reasons"])}
        )
    if tool_calls and tool_errors / tool_calls > 0.05:
        alerts.append(
            {
                "severity": "ticket",
                "rule": "tool_error_rate",
                "detail": f"{tool_errors}/{tool_calls} tool calls failed",
            }
        )
    for r in slo_rows:
        if r.get("burn_rate", 0) and float(r["burn_rate"]) >= 3.0:
            alerts.append(
                {
                    "severity": "page" if float(r["burn_rate"]) >= 6 else "ticket",
                    "rule": f"slo_burn:{r['sli']}",
                    "detail": f"burn rate {r['burn_rate']}",
                }
            )

    outcomes: dict[str, int] = {}
    scenarios: dict[str, int] = {}
    for r in reqs:
        outcomes[r.outcome] = outcomes.get(r.outcome, 0) + 1
        scenarios[r.scenario or "none"] = scenarios.get(r.scenario or "none", 0) + 1
    return {
        "store": store.path,
        "window": {
            "start": datetime.fromtimestamp(start, tz=UTC).isoformat() if start else None,
            "end": datetime.fromtimestamp(end, tz=UTC).isoformat() if end else None,
        },
        "requests": len(reqs),
        "sessions": len({r.session_id for r in reqs if r.session_id}),
        "generations": len(gens),
        "total_cost_usd": round(float(total_cost(gens)), 4),
        "cost_per_session_usd": round(
            float(total_cost(gens)) / max(1, len({r.session_id for r in reqs if r.session_id})), 6
        ),
        "cost_by_tenant": by_tenant,
        "cost_by_feature": by_feature,
        "cost_by_intent": by_intent,
        "cost_by_model": by_model,
        "cost_by_tenant_feature": tenant_feature,
        "hourly_cost": {h: hourly_cost.get(h, {}) for h in range(24)},
        "latency": lat_stats,
        "ttft": ttft_stats,
        "latency_by_tenant": lat_by_tenant,
        "latency_hourly_p95": lat_hourly,
        "quality": quality,
        "drift": drift,
        "budgets": budgets,
        "slos": slo_rows,
        "tools": tools,
        "outcomes": outcomes,
        "scenarios": scenarios,
        "alerts": alerts,
    }


def render_text(summary: dict[str, Any]) -> str:
    """Plain-text rendering of the summary (what ``--text`` prints)."""
    s = summary
    out: list[str] = []
    out.append("=" * 78)
    out.append(
        f"ATLAS OPS CONSOLE   store={s['store']}   window={s['window']['start']} -> {s['window']['end']}"
    )
    out.append("=" * 78)
    out.append(
        f"requests={s['requests']}  sessions={s['sessions']}  generations={s['generations']}  total_cost=${s['total_cost_usd']:.4f}  cost/session=${s['cost_per_session_usd']:.5f}"
    )
    out.append(
        f"outcomes={json.dumps(s['outcomes'], sort_keys=True)}  scenarios={json.dumps(s['scenarios'], sort_keys=True)}"
    )
    out.append("\n-- Cost by tenant ------------------------------------------------------------")
    out.append(
        f"{'tenant':10} {'requests':>8} {'sessions':>8} {'tokens_in':>10} {'cached%':>8} {'cost_usd':>10} {'$/session':>10}"
    )
    for k, v in s["cost_by_tenant"].items():
        out.append(
            f"{k:10} {v['requests']:>8} {v['sessions']:>8} {v['input_tokens']:>10,} {v['cache_hit_ratio']:>8.0%} {v['cost_usd']:>10.4f} {v['cost_per_session']:>10.5f}"
        )
    out.append("\n-- Cost by feature ------------------------------------------------------------")
    for k, v in s["cost_by_feature"].items():
        out.append(
            f"{k:16} requests={v['requests']:>5}  cost=${v['cost_usd']:.4f}  $/request={v['cost_per_request']:.5f}"
        )
    out.append("\n-- Cost by intent (top 10) ----------------------------------------------------")
    for k, v in list(s["cost_by_intent"].items())[:10]:
        out.append(
            f"{k:16} requests={v['requests']:>5}  cost=${v['cost_usd']:.4f}  $/request={v['cost_per_request']:.5f}"
        )
    out.append("\n-- Cost by model --------------------------------------------------------------")
    for k, v in s["cost_by_model"].items():
        out.append(
            f"{k:14} calls={v['requests']:>5}  in={v['input_tokens']:>9,}  out={v['output_tokens']:>8,}  cached={v['cache_hit_ratio']:.0%}  cost=${v['cost_usd']:.4f}"
        )
    out.append("\n-- Hourly cost (all tenants) ---------------------------------------------------")
    series = [sum(s["hourly_cost"][h].values()) for h in range(24)]
    peak = max(series) if series and max(series) > 0 else 1.0
    for h in range(24):
        bar = "#" * int(40 * series[h] / peak)
        out.append(f"{h:02d}:00 {series[h]:8.4f} {bar}")
    lat, ttft = s["latency"], s["ttft"]
    out.append("\n-- Latency ---------------------------------------------------------------------")
    out.append(
        f"total  p50={lat['p50']:.0f}ms  p95={lat['p95']:.0f}ms  p99={lat['p99']:.0f}ms  max={lat['max']:.0f}ms  n={lat['count']}"
    )
    if ttft["count"]:
        out.append(f"ttft   p50={ttft['p50']:.0f}ms  p95={ttft['p95']:.0f}ms  n={ttft['count']}")
    for k, v in s["latency_by_tenant"].items():
        out.append(f"  {k:10} p50={v['p50']:.0f}ms p95={v['p95']:.0f}ms n={v['count']}")
    if s["latency_hourly_p95"]:
        out.append(
            "hourly p95: "
            + " ".join(f"{h:02d}h={v:.0f}" for h, v in sorted(s["latency_hourly_p95"].items()))
        )
    q = s["quality"]
    out.append("\n-- Quality ---------------------------------------------------------------------")
    out.append(
        f"judge_overall mean={q['judge_overall_mean']} grounded mean={q['judge_grounded_mean']} n={q['judge_count']}  feedback n={q['feedback_count']} positive={q['feedback_positive_rate']}"
    )
    if q["by_prompt_version"]:
        out.append(
            "by prompt version: "
            + ", ".join(
                f"{k}: mean={v['mean']} n={v['n']}" for k, v in q["by_prompt_version"].items()
            )
        )
    if q["judge_hourly_mean"]:
        out.append(
            "hourly judge mean: "
            + " ".join(f"{h:02d}h={v:.2f}" for h, v in q["judge_hourly_mean"].items())
        )
    if s["drift"]:
        d = s["drift"]
        out.append(
            f"drift (am vs pm): status={d['status']} psi={d['psi']} mean_delta={d['mean_delta_pct']:+.1f}% reasons={d['reasons']}"
        )
    out.append("\n-- Budgets ---------------------------------------------------------------------")
    for b in s["budgets"]:
        out.append(
            f"{b['tenant']:10} spent=${b['spent_usd']:.4f}  soft=${b['soft_cap_usd']:.2f} hard=${b['hard_cap_usd']:.2f}  utilisation={b['utilisation']:.1%}  state={b['state']}"
        )
    out.append("\n-- SLOs ------------------------------------------------------------------------")
    for r in s["slos"]:
        out.append(
            f"{r['sli']:14} value={r['value']:.3f} target={r.get('target')} budget_left={r.get('error_budget_remaining')} burn={r.get('burn_rate')} {'OK' if r.get('ok') else 'BREACH'}"
        )
    out.append("\n-- Tools -----------------------------------------------------------------------")
    for k, v in sorted(s["tools"].items()):
        out.append(f"{k:22} calls={v['calls']:>5} errors={v['errors']:>4}")
    out.append("\n-- Alerts ----------------------------------------------------------------------")
    if s["alerts"]:
        for a in s["alerts"]:
            out.append(f"[{a['severity'].upper():6}] {a['rule']:18} {a['detail']}")
    else:
        out.append("no alerts")
    return "\n".join(out) + "\n"


def _load_store(path: str | None, seed: int | None, incidents: str) -> LocalSpanStore:
    from console.data import load_store

    return load_store(path, seed=seed, incidents=incidents)


PAGES: tuple[tuple[str, str], ...] = (
    ("Live cost", "the meter, steps counter, context sparkline and live alerts (1.1)"),
    ("Cost", "showback by tenant and feature, unit costs, top-10 conversations (2.4, 6.x)"),
    ("Latency", "p50/p95/p99 per hour against the 4 s budget, span and TTFT detail (7.x)"),
    ("Quality", "judge scores, grounded rate, feedback, judge-vs-user disagreements (8.x)"),
    ("Budgets", "cumulative spend per tenant against the caps, EWMA anomalies (6.7)"),
    ("Traffic", "requests per minute by tenant with last week's shadow line (11.2)"),
    ("Retrieval", "top_k, hits and result tokens by tenant (5.3, 11.2)"),
    ("Reliability", "tool error share and LLM retries by reason (11.2, 11.3)"),
    ("Safety", "injection, refusal and PII-in-output rates (8.4)"),
    ("Alerts", "batch alert rules, SLOs and budgets over the whole store"),
    ("Traces", "one conversation's waterfall (2.4, 11.x)"),
    ("Compare replays", "replays of the same day side by side (6.8, 14.2)"),
)


def streamlit_main() -> None:  # pragma: no cover - UI
    """Home page: four tiles; the pages in ``console/pages/`` appear in the sidebar."""
    assert st is not None
    from console._ui import page
    from console.data import headline

    d, _settings = page("Atlas Ops Console")
    h = headline(d)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cost (store)", f"${h['total_cost_usd']:,.2f}")
    c2.metric("Requests / sessions", f"{h['requests']:,} / {h['sessions']:,}")
    c3.metric("p95 latency", f"{h['p95_ms'] / 1000:.2f} s")
    c4.metric(
        "Judge score",
        f"{h['judge_overall_mean']:.2f}"
        if h["judge_overall_mean"] is not None
        else "not yet scored",
    )
    st.caption(f"{d.path}: {h['start']} to {h['end']}")
    st.markdown("\n".join(f"- **{name}**: {what}" for name, what in PAGES))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Atlas Ops Console")
    ap.add_argument(
        "--text",
        action="store_true",
        help="print the summaries as text instead of launching Streamlit",
    )
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    ap.add_argument("--store", default=None)
    ap.add_argument(
        "--seed", type=int, default=7, help="replay a day if the store is empty (use -1 to disable)"
    )
    ap.add_argument("--incidents", default="none")
    args = ap.parse_args(argv)
    if not args.text and not args.json:
        if STREAMLIT_AVAILABLE:
            import subprocess

            return subprocess.call([sys.executable, "-m", "streamlit", "run", __file__])
        print(
            "streamlit is not installed (pip install '.[dashboards]'); falling back to --text\n",
            file=sys.stderr,
        )
    store = _load_store(args.store, None if args.seed < 0 else args.seed, args.incidents)
    summary = build_summary(store, Settings.from_env())
    print(json.dumps(summary, indent=2, default=str) if args.json else render_text(summary))
    return 0


if __name__ == "__main__":
    if STREAMLIT_AVAILABLE and st.runtime.exists():  # type: ignore[union-attr]  # pragma: no cover
        streamlit_main()
    else:
        raise SystemExit(main())
