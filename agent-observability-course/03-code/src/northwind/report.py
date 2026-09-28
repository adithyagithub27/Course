"""Weekly ops report (markdown) built from aggregated cost records, latency
samples, judge scores and incidents. This is the one-pager a manager reads
(Section 14.4)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date

from northwind.cost import CostRecord, cost_per_session, rollup, showback_table, total_cost
from northwind.drift import DriftResult, drift_report_markdown
from northwind.latency import LatencySample, summarize
from northwind.slo import DEFAULT_SLOS, compute_slis


@dataclass(frozen=True)
class IncidentNote:
    title: str
    started: str
    duration_min: int
    impact: str
    root_cause: str
    status: str = "resolved"


@dataclass
class ReportInputs:
    records: Sequence[CostRecord]
    latencies: Sequence[LatencySample] = ()
    judge_scores: Sequence[float] = ()
    feedback_positive: int = 0
    feedback_negative: int = 0
    incidents: Sequence[IncidentNote] = ()
    drift: Sequence[DriftResult] = ()
    previous_week_cost_usd: float | None = None
    period_start: date = date(2026, 9, 14)
    period_end: date = date(2026, 9, 20)
    latency_budget_ms: float = 4000.0
    cost_budget_usd: float = 0.05
    tool_calls: int = 0
    tool_errors: int = 0
    recommendations: list[str] = field(default_factory=list)


def _pct(a: float, b: float) -> str:
    if b == 0:
        return "n/a"
    return f"{(a - b) / b * 100:+.1f}%"


def default_recommendations(inputs: ReportInputs) -> list[str]:
    """Rule-based suggestions so the report is never empty."""
    recs: list[str] = []
    by_tenant = rollup(inputs.records, "tenant")
    if by_tenant:
        top = max(by_tenant.values(), key=lambda r: r.cost_usd)
        share = float(top.cost_usd / total_cost(inputs.records)) if inputs.records else 0.0
        if share > 0.4:
            recs.append(
                f"Tenant `{top.key}` is {share:.0%} of spend; review its budget cap and the "
                "context diet before the next billing cycle."
            )
    by_model = rollup(inputs.records, "model")
    total_in = sum(r.input_tokens for r in by_model.values())
    total_cached = sum(r.cached_tokens for r in by_model.values())
    if total_in and total_cached / total_in < 0.3:
        recs.append(
            f"Prompt cache hit ratio is {total_cached / total_in:.0%}; stabilise the prompt "
            "prefix and send `prompt_cache_key` to lift it above 50%."
        )
    if inputs.latencies:
        stats = summarize([s.total_ms for s in inputs.latencies])
        if stats.p95 > inputs.latency_budget_ms:
            recs.append(
                f"p95 latency {stats.p95:.0f} ms exceeds the {inputs.latency_budget_ms:.0f} ms "
                "budget; check provider TTFT and retrieval top-k."
            )
    if inputs.judge_scores:
        mean = sum(inputs.judge_scores) / len(inputs.judge_scores)
        if mean < 0.75:
            recs.append(
                f"Mean judge score {mean:.2f} is below 0.75; compare prompt versions and roll back if needed."
            )
    if not recs:
        recs.append("No action needed; keep the budget gate in CI and re-check next week.")
    return recs


def weekly_report(inputs: ReportInputs) -> str:
    """Render the weekly markdown report."""
    recs = list(inputs.records)
    total = total_cost(recs)
    cps = cost_per_session(recs)
    lat = summarize([s.total_ms for s in inputs.latencies]) if inputs.latencies else None
    ttfts = [s.ttft_ms for s in inputs.latencies if s.ttft_ms is not None]
    ttft = summarize(ttfts) if ttfts else None
    snap = compute_slis(
        recs,
        latency_budget_ms=inputs.latency_budget_ms,
        cost_budget_usd=inputs.cost_budget_usd,
        judge_scores=inputs.judge_scores,
        tool_calls=inputs.tool_calls,
        tool_errors=inputs.tool_errors,
    )
    lines: list[str] = []
    lines.append(f"# Atlas weekly ops report — {inputs.period_start} to {inputs.period_end}\n")
    lines.append("## Headline numbers\n")
    lines.append("| metric | value | note |")
    lines.append("|---|---:|---|")
    prev = inputs.previous_week_cost_usd
    lines.append(
        f"| Total LLM cost | ${float(total):,.2f} | "
        f"{'vs last week ' + _pct(float(total), prev) if prev is not None else '-'} |"
    )
    lines.append(
        f"| Requests | {len(recs):,} | sessions: {len({r.session_id for r in recs if r.session_id}):,} |"
    )
    lines.append(f"| Cost per session | ${float(cps):.4f} | budget ${inputs.cost_budget_usd:.4f} |")
    lines.append(f"| Cost per resolved session | ${snap.cost_per_resolved_session:.4f} | |")
    if lat:
        lines.append(
            f"| Latency p50 / p95 | {lat.p50:.0f} / {lat.p95:.0f} ms | budget p95 {inputs.latency_budget_ms:.0f} ms |"
        )
    if ttft:
        lines.append(f"| TTFT p95 | {ttft.p95:.0f} ms | |")
    if inputs.judge_scores:
        mean = sum(inputs.judge_scores) / len(inputs.judge_scores)
        lines.append(f"| Judge score (mean, n={len(inputs.judge_scores)}) | {mean:.2f} | sampled |")
    fb_total = inputs.feedback_positive + inputs.feedback_negative
    if fb_total:
        lines.append(
            f"| User feedback | {inputs.feedback_positive}👍 / {inputs.feedback_negative}👎 | "
            f"{inputs.feedback_positive / fb_total:.0%} positive |"
        )
    lines.append("")
    lines.append("## SLOs\n")
    lines.append("| SLI | value | target | error budget left | burn rate | ok |")
    lines.append("|---|---:|---:|---:|---:|:--:|")
    for row in snap.report(DEFAULT_SLOS):
        if row["total"] == 0:
            continue
        lines.append(
            f"| {row['sli']} | {row['value']:.3f} | {row.get('target', '-')} | "
            f"{row.get('error_budget_remaining', '-')} | {row.get('burn_rate', '-')} | "
            f"{'✅' if row.get('ok') else '❌'} |"
        )
    lines.append("")
    lines.append("## Cost by tenant (showback)\n")
    lines.append(showback_table(recs, "tenant"))
    lines.append("## Cost by feature\n")
    lines.append(showback_table(recs, "feature"))
    lines.append("## Cost by model\n")
    lines.append(showback_table(recs, "model"))
    if inputs.drift:
        lines.append("## Drift vs previous week\n")
        lines.append(drift_report_markdown(inputs.drift))
    lines.append("## Incidents\n")
    if inputs.incidents:
        lines.append("| incident | started | duration | impact | root cause | status |")
        lines.append("|---|---|---:|---|---|---|")
        for i in inputs.incidents:
            lines.append(
                f"| {i.title} | {i.started} | {i.duration_min} min | {i.impact} | {i.root_cause} | {i.status} |"
            )
    else:
        lines.append("No incidents this week.")
    lines.append("")
    lines.append("## Recommendations\n")
    for n, r in enumerate(inputs.recommendations or default_recommendations(inputs), 1):
        lines.append(f"{n}. {r}")
    lines.append("")
    return "\n".join(lines)
