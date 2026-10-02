"""Pure data functions behind the Ops Console pages (no Streamlit, no pandas).

Every function takes a :class:`StoreData` (one read of a :class:`LocalSpanStore`) and returns
plain dicts or lists of row dicts, which ``st.dataframe`` / ``st.bar_chart`` accept directly
and unit tests can assert on. The pages in ``console/pages/`` are thin layouts over these.

    from console.data import StoreData, top_sessions
    d = StoreData.load(LocalSpanStore(".atlas/spans.sqlite"))
    top_sessions(d, 10)

Time buckets are UTC epoch bins; ``label`` is ``HH:MM`` for a one-day store and
``MM-DD HH:MM`` when the store holds several days.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from northwind.config import TENANTS, Settings
from northwind.cost import CostRecord, rollup, total_cost
from northwind.latency import percentile, summarize
from northwind.tokens import approx_tokens
from telemetry.local_store import LocalSpanStore, ScoreRecord, SpanRecord

HOUR = 3600
DAY = 86_400
WEEK = 7 * DAY


# ------------------------------------------------------------------------------------- loading
@dataclass
class StoreData:
    """One snapshot of a span store, indexed the ways the pages need."""

    path: str
    spans: list[SpanRecord]
    scores: list[ScoreRecord]
    requests: list[CostRecord]
    generations: list[CostRecord]
    by_kind: dict[str, list[SpanRecord]] = field(default_factory=dict)
    by_trace: dict[str, list[SpanRecord]] = field(default_factory=dict)

    @classmethod
    def load(cls, store: LocalSpanStore) -> StoreData:
        spans = store.spans()
        by_kind: dict[str, list[SpanRecord]] = defaultdict(list)
        by_trace: dict[str, list[SpanRecord]] = defaultdict(list)
        for s in spans:
            by_kind[s.kind].append(s)
            by_trace[s.trace_id].append(s)
        return cls(
            path=store.path,
            spans=spans,
            scores=store.scores(),
            requests=store.cost_records("request"),
            generations=store.cost_records("generation"),
            by_kind=dict(by_kind),
            by_trace=dict(by_trace),
        )

    def kind(self, *kinds: str) -> list[SpanRecord]:
        out: list[SpanRecord] = []
        for k in kinds:
            out.extend(self.by_kind.get(k, []))
        return out

    @property
    def agents(self) -> list[SpanRecord]:
        return self.by_kind.get("agent", [])

    @property
    def multi_day(self) -> bool:
        days = {int(s.start_time // DAY) for s in self.agents}
        return len(days) > 1

    def label(self, ts: float) -> str:
        dt = datetime.fromtimestamp(ts, tz=UTC)
        return dt.strftime("%m-%d %H:%M") if self.multi_day else dt.strftime("%H:%M")

    def score_map(self, name: str) -> dict[str, float]:
        return {s.trace_id: s.value for s in self.scores if s.name == name}


def load_store(
    path: str | None = None, *, seed: int | None = 7, incidents: str = "none"
) -> LocalSpanStore:
    """Open the store at ``path`` (default ``ATLAS_LOCAL_STORE``); replay a day into it when
    it is empty and ``seed`` is given, so the console always has something to show."""
    settings = Settings.from_env()
    store = LocalSpanStore(path or settings.local_store_path)
    if store.count() == 0 and seed is not None:
        from simulator.replay import replay_day

        replay_day(seed, store=store, incidents=incidents)
    return store


def _bin(ts: float, size: int) -> float:
    return ts - (ts % size)


def _r(x: float, n: int = 4) -> float:
    return round(float(x), n)


# ------------------------------------------------------------------------------------ headline
def headline(d: StoreData) -> dict[str, Any]:
    """Home page tiles: cost, requests, sessions, p95, judge mean (None = not yet scored)."""
    lat = [r.latency_ms for r in d.requests]
    judge = [s.value for s in d.scores if s.name == "judge_overall"]
    start = min((s.start_time for s in d.agents), default=0.0)
    end = max((s.end_time for s in d.agents), default=0.0)
    return {
        "total_cost_usd": _r(float(total_cost(d.generations))),
        "requests": len(d.requests),
        "sessions": len({r.session_id for r in d.requests if r.session_id}),
        "p50_ms": _r(percentile(lat, 50), 1) if lat else 0.0,
        "p95_ms": _r(percentile(lat, 95), 1) if lat else 0.0,
        "judge_overall_mean": _r(sum(judge) / len(judge), 3) if judge else None,
        "judged": len(judge),
        "start": datetime.fromtimestamp(start, tz=UTC).isoformat() if start else None,
        "end": datetime.fromtimestamp(end, tz=UTC).isoformat() if end else None,
    }


# ---------------------------------------------------------------------------- live (Lecture 1.1)
def live(d: StoreData, *, window_s: float = 900.0, now: float | None = None) -> dict[str, Any]:
    """The "Live cost" page: spend in the last ``window_s`` seconds, the latest conversation's
    steps and context-size sparkline, and the live alerts.

    ``now`` defaults to the newest span in the store, so the page works for a replayed day as
    well as for a conversation running right now (spans arrive step by step while it runs)."""
    newest = max((s.end_time for s in d.spans), default=0.0)
    end = now if now is not None else newest
    start = end - window_s
    gens = [s for s in d.kind("generation") if start <= s.start_time <= end]
    by_tenant = {t: 0.0 for t in TENANTS}
    for s in gens:
        t = str(s.attr("atlas.tenant", "other"))
        by_tenant[t] = by_tenant.get(t, 0.0) + float(s.attr("atlas.cost_usd", 0.0) or 0.0)
    latest = max(gens, key=lambda s: s.start_time, default=None)
    steps = 0
    context: list[int] = []
    cumulative: list[float] = []
    trace_cost = 0.0
    if latest is not None:
        tr = sorted(
            (s for s in d.by_trace.get(latest.trace_id, []) if s.kind == "generation"),
            key=lambda s: s.start_time,
        )
        for s in tr:
            trace_cost += float(s.attr("atlas.cost_usd", 0.0) or 0.0)
            context.append(int(s.attr("gen_ai.usage.input_tokens", 0) or 0))
            cumulative.append(round(trace_cost, 6))
        steps = max((int(s.attr("atlas.step", 0) or 0) for s in tr), default=0)
    return {
        "window_start": start,
        "window_end": end,
        "total_cost_usd": _r(sum(by_tenant.values()), 6),
        "cost_by_tenant": {k: _r(v, 6) for k, v in sorted(by_tenant.items())},
        "latest_trace_id": latest.trace_id if latest else None,
        "latest_tenant": latest.attr("atlas.tenant") if latest else None,
        "steps": steps,
        "trace_cost_usd": _r(trace_cost, 6),
        "context_tokens": context,
        "cost_sparkline": cumulative,
        "alerts": live_alerts(d, end=end),
    }


def live_alerts(
    d: StoreData, *, end: float, tool_window_s: float = 60.0, tool_threshold: float = 0.2
) -> list[dict[str, str]]:
    """Alerts over the newest data: tool error share per (tool, tenant) over the last minute,
    and loop guard events (step limit, retries exhausted, deadline) in the last 15 minutes."""
    alerts: list[dict[str, str]] = []
    calls: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    for s in d.kind("tool", "retriever"):
        if end - tool_window_s <= s.start_time <= end:
            key = (str(s.attr("gen_ai.tool.name", s.name)), str(s.attr("atlas.tenant", "other")))
            calls[key][0] += 1
            calls[key][1] += int(s.status == "ERROR")
    for (tool, tenant), (n, errors) in sorted(calls.items()):
        if n >= 3 and errors / n >= tool_threshold:
            alerts.append(
                {
                    "severity": "page",
                    "rule": "tool_error_rate",
                    "detail": f"{tool} {errors / n:.0%} over {tool_window_s:.0f} s ({tenant})",
                }
            )
    for s in d.agents:
        if end - 900 <= s.end_time <= end:
            for e in s.events:
                if e["name"] in {
                    "step_limit_reached",
                    "tool_retries_exhausted",
                    "request_deadline_exceeded",
                }:
                    alerts.append(
                        {
                            "severity": "ticket",
                            "rule": e["name"],
                            "detail": f"trace {s.trace_id[:12]} ({s.attr('atlas.tenant')}) "
                            f"after {s.attr('atlas.steps')} steps, ${float(s.attr('atlas.cost_usd', 0)):.4f}",
                        }
                    )
    return alerts


# ------------------------------------------------------------------------------------------ cost
def cost_by(d: StoreData, dimension: str, *, level: str = "request") -> list[dict[str, Any]]:
    """Showback rows by ``tenant``/``feature``/``model``/``intent``, most expensive first."""
    recs = d.requests if level == "request" else d.generations
    rows = [r.as_dict() for r in rollup(recs, dimension).values()]
    return sorted(rows, key=lambda r: -float(r["cost_usd"]))


def cost_tiles(d: StoreData) -> dict[str, Any]:
    """Cost page tiles: total, per session, per resolved session, cache hit ratio."""
    total = float(total_cost(d.generations))
    sessions = {r.session_id for r in d.requests if r.session_id}
    resolved = [r for r in d.requests if r.outcome == "resolved"]
    resolved_sessions = {r.session_id for r in resolved}
    inp = sum(r.input_tokens for r in d.generations)
    cached = sum(r.cached_tokens for r in d.generations)
    return {
        "total_cost_usd": _r(total),
        "cost_per_session_usd": _r(total / len(sessions), 6) if sessions else 0.0,
        "cost_per_resolved_session_usd": _r(
            sum(r.cost_usd for r in resolved) / len(resolved_sessions), 6
        )
        if resolved_sessions
        else 0.0,
        "cache_hit_ratio": _r(cached / inp, 4) if inp else 0.0,
        "input_tokens": inp,
        "cached_tokens": cached,
    }


def top_sessions(d: StoreData, n: int = 10) -> list[dict[str, Any]]:
    """The ``n`` most expensive conversations, each with the trace ids to open (2.4)."""
    agg: dict[str, dict[str, Any]] = {}
    for r in sorted(d.requests, key=lambda r: r.timestamp):
        a = agg.setdefault(
            r.session_id or r.trace_id,
            {
                "session_id": r.session_id or r.trace_id,
                "tenant": r.tenant,
                "feature": r.feature,
                "turns": 0,
                "cost_usd": 0.0,
                "input_tokens": 0,
                "steps": 0,
                "outcomes": Counter(),
                "trace_ids": [],
            },
        )
        a["turns"] += 1
        a["cost_usd"] += r.cost_usd
        a["input_tokens"] += r.input_tokens
        a["steps"] += r.steps
        a["outcomes"][r.outcome] += 1
        a["trace_ids"].append(r.trace_id)
    rows = sorted(agg.values(), key=lambda a: -a["cost_usd"])[:n]
    for a in rows:
        a["cost_usd"] = _r(a["cost_usd"], 6)
        a["outcomes"] = ", ".join(f"{k}={v}" for k, v in sorted(a["outcomes"].items()))
        a["first_trace_id"] = a["trace_ids"][0]
    return rows


def hourly_cost_by_tenant(d: StoreData) -> list[dict[str, Any]]:
    acc: dict[tuple[float, str], float] = defaultdict(float)
    for r in d.generations:
        acc[(_bin(r.timestamp, HOUR), r.tenant)] += r.cost_usd
    return [
        {"hour": d.label(h), "ts": h, "tenant": t, "cost_usd": _r(c, 6)}
        for (h, t), c in sorted(acc.items())
    ]


def hourly_unit_costs(d: StoreData, tenant: str | None = None) -> list[dict[str, Any]]:
    """Per hour: cost per session, cost per request, mean input/output tokens per generation
    (11.2 evidence 3, 11.3 evidence 4, 11.4 evidence 4)."""
    reqs: dict[float, list[CostRecord]] = defaultdict(list)
    gens: dict[float, list[CostRecord]] = defaultdict(list)
    for r in d.requests:
        if tenant in (None, "all", r.tenant):
            reqs[_bin(r.timestamp, HOUR)].append(r)
    for g in d.generations:
        if tenant in (None, "all", g.tenant):
            gens[_bin(g.timestamp, HOUR)].append(g)
    rows = []
    for h in sorted(set(reqs) | set(gens)):
        rr, gg = reqs.get(h, []), gens.get(h, [])
        sessions = {r.session_id for r in rr}
        cost = sum(r.cost_usd for r in rr)
        rows.append(
            {
                "hour": d.label(h),
                "ts": h,
                "requests": len(rr),
                "cost_usd": _r(cost, 6),
                "cost_per_session_usd": _r(cost / len(sessions), 6) if sessions else 0.0,
                "cost_per_request_usd": _r(cost / len(rr), 6) if rr else 0.0,
                "mean_input_tokens_per_generation": _r(sum(g.input_tokens for g in gg) / len(gg), 1)
                if gg
                else 0.0,
                "mean_output_tokens_per_generation": _r(
                    sum(g.output_tokens for g in gg) / len(gg), 1
                )
                if gg
                else 0.0,
            }
        )
    return rows


# ---------------------------------------------------------------------------------------- latency
def latency_summary(d: StoreData) -> dict[str, Any]:
    ttft = [s.attr("atlas.ttft_ms") for s in d.agents if s.attr("atlas.ttft_ms") is not None]
    return {
        "total": summarize(r.latency_ms for r in d.requests).as_dict(),
        "ttft": summarize(float(x) for x in ttft).as_dict(),
    }


def hourly_latency(d: StoreData) -> list[dict[str, Any]]:
    acc: dict[float, list[float]] = defaultdict(list)
    for r in d.requests:
        acc[_bin(r.timestamp, HOUR)].append(r.latency_ms)
    return [
        {
            "hour": d.label(h),
            "ts": h,
            "p50_ms": _r(percentile(v, 50), 1),
            "p95_ms": _r(percentile(v, 95), 1),
            "n": len(v),
        }
        for h, v in sorted(acc.items())
    ]


def span_p95_by_type_hourly(d: StoreData) -> list[dict[str, Any]]:
    """p95 span duration per observation type per hour (11.3 evidence 2)."""
    acc: dict[tuple[float, str], list[float]] = defaultdict(list)
    for s in d.kind("agent", "generation", "retriever", "tool"):
        acc[(_bin(s.start_time, HOUR), s.kind)].append(s.duration_ms)
    return [
        {"hour": d.label(h), "ts": h, "type": k, "p95_ms": _r(percentile(v, 95), 1), "n": len(v)}
        for (h, k), v in sorted(acc.items())
    ]


def generation_timing_hourly(d: StoreData) -> list[dict[str, Any]]:
    """Per hour: ``atlas.ttft_ms`` p95 and generation duration p95 (11.3 evidence 3)."""
    ttft: dict[float, list[float]] = defaultdict(list)
    dur: dict[float, list[float]] = defaultdict(list)
    for s in d.kind("generation"):
        h = _bin(s.start_time, HOUR)
        if s.status == "OK":
            dur[h].append(s.duration_ms)
        if s.attr("atlas.ttft_ms") is not None:
            ttft[h].append(float(s.attr("atlas.ttft_ms")))
    return [
        {
            "hour": d.label(h),
            "ts": h,
            "ttft_p95_ms": _r(percentile(ttft[h], 95), 1) if ttft.get(h) else None,
            "generation_p95_ms": _r(percentile(dur[h], 95), 1) if dur.get(h) else None,
        }
        for h in sorted(set(ttft) | set(dur))
    ]


# ---------------------------------------------------------------------------------------- quality
def quality_summary(d: StoreData, *, threshold: float = 0.7) -> dict[str, Any]:
    """Judge means, grounded rate, empty retrievals (5.3) and feedback rate (8.3)."""
    by_name: dict[str, list[float]] = defaultdict(list)
    for s in d.scores:
        by_name[s.name].append(s.value)
    grounded = by_name.get("judge_grounded", [])
    retrievers = d.kind("retriever")
    empty = [s for s in retrievers if s.attr("atlas.retrieval.empty") is True]
    fb = by_name.get("user_feedback", [])
    fb_traces = {s.trace_id for s in d.scores if s.name == "user_feedback"}
    return {
        "judged": len(by_name.get("judge_overall", [])),
        "judge_means": {
            k.removeprefix("judge_"): _r(sum(v) / len(v), 3)
            for k, v in sorted(by_name.items())
            if k.startswith("judge_") and v
        },
        "grounded_rate": _r(sum(1 for x in grounded if x >= threshold) / len(grounded), 4)
        if grounded
        else None,
        "empty_retrieval_rate": _r(len(empty) / len(retrievers), 4) if retrievers else None,
        "feedback_count": len(fb),
        "feedback_rate": _r(len(fb_traces) / len(d.requests), 4) if d.requests else 0.0,
        "feedback_positive_share": _r(sum(1 for x in fb if x >= 0.75) / len(fb), 4) if fb else None,
    }


def judge_hourly(
    d: StoreData, names: Iterable[str] = ("judge_grounded", "judge_resolved", "judge_overall")
) -> list[dict[str, Any]]:
    wanted = set(names)
    acc: dict[tuple[float, str], list[float]] = defaultdict(list)
    for s in d.scores:
        if s.name in wanted:
            acc[(_bin(s.timestamp, HOUR), s.name)].append(s.value)
    return [
        {"hour": d.label(h), "ts": h, "score": n, "mean": _r(sum(v) / len(v), 3), "n": len(v)}
        for (h, n), v in sorted(acc.items())
    ]


def judge_by_prompt_version(d: StoreData) -> list[dict[str, Any]]:
    """Judge means split by ``atlas.prompt_version`` (11.4 evidence 3, 14.3)."""
    version = {s.trace_id: str(s.attr("atlas.prompt_version", "?")) for s in d.agents}
    acc: dict[tuple[str, str], list[float]] = defaultdict(list)
    for s in d.scores:
        if s.name.startswith("judge_") and s.trace_id in version:
            acc[(version[s.trace_id], s.name)].append(s.value)
    return [
        {"prompt_version": v, "score": n, "mean": _r(sum(x) / len(x), 3), "n": len(x)}
        for (v, n), x in sorted(acc.items())
    ]


def feedback_by_session_length(d: StoreData) -> list[dict[str, Any]]:
    """Share of sessions that left any feedback, by number of turns (8.3 survivorship)."""
    turns: Counter[str] = Counter(r.session_id for r in d.requests if r.session_id)
    rated = {s.session_id for s in d.scores if s.name == "user_feedback" and s.session_id}
    buckets: dict[str, list[str]] = defaultdict(list)
    for sid, n in turns.items():
        buckets["4+" if n >= 4 else str(n)].append(sid)
    return [
        {
            "turns": k,
            "sessions": len(v),
            "rated": sum(1 for s in v if s in rated),
            "feedback_rate": _r(sum(1 for s in v if s in rated) / len(v), 4),
        }
        for k, v in sorted(buckets.items())
    ]


def disagreements(
    d: StoreData, *, judge: str = "judge_resolved", threshold: float = 0.7, limit: int = 50
) -> list[dict[str, Any]]:
    """Traces where the user and the judge disagree (8.3's reading list)."""
    jm = d.score_map(judge)
    agents = {s.trace_id: s for s in d.agents}
    rows = []
    for s in d.scores:
        if s.name != "user_feedback" or s.trace_id not in jm:
            continue
        thumbs_up = s.value >= 0.75
        judge_ok = jm[s.trace_id] >= threshold
        if thumbs_up == judge_ok:
            continue
        a = agents.get(s.trace_id)
        rows.append(
            {
                "trace_id": s.trace_id,
                "session_id": s.session_id,
                "tenant": s.tenant,
                "kind": "thumbs down, judge says ok" if judge_ok else "thumbs up, judge says bad",
                "feedback": s.value,
                judge: jm[s.trace_id],
                "comment": s.comment,
                "intent": a.attr("atlas.intent") if a else None,
                "question": str(a.attr("langfuse.observation.input", ""))[:120] if a else "",
            }
        )
    return rows[:limit]


def judge_feedback_agreement(
    d: StoreData, *, judge: str = "judge_resolved", threshold: float = 0.7
) -> dict[str, Any]:
    jm = d.score_map(judge)
    both = [s for s in d.scores if s.name == "user_feedback" and s.trace_id in jm]
    agree = sum(1 for s in both if (s.value >= 0.75) == (jm[s.trace_id] >= threshold))
    return {
        "overlap": len(both),
        "agree": agree,
        "rate": _r(agree / len(both), 4) if both else None,
    }


def feedback_hourly(d: StoreData) -> list[dict[str, Any]]:
    acc: dict[float, list[float]] = defaultdict(list)
    for s in d.scores:
        if s.name == "user_feedback":
            acc[_bin(s.timestamp, HOUR)].append(s.value)
    return [
        {
            "hour": d.label(h),
            "ts": h,
            "feedback": len(v),
            "thumbs_down_rate": _r(sum(1 for x in v if x <= 0.25) / len(v), 4),
        }
        for h, v in sorted(acc.items())
    ]


def top_feedback_comments(
    d: StoreData, *, since: float | None = None, n: int = 10
) -> list[dict[str, Any]]:
    c: Counter[str] = Counter(
        s.comment
        for s in d.scores
        if s.name == "user_feedback" and s.comment and (since is None or s.timestamp >= since)
    )
    return [{"comment": k, "count": v} for k, v in c.most_common(n)]


# ---------------------------------------------------------------------------------------- budgets
def budget_timeline(
    d: StoreData,
    settings: Settings | None = None,
    *,
    bin_s: int = 900,
    factor: float = 2.0,
    min_requests: int = 5,
) -> list[dict[str, Any]]:
    """Cumulative spend per tenant per ``bin_s`` against the soft and hard caps (6.7).

    ``anomaly`` marks a bin whose *cost per request* is above ``factor`` x the tenant's median
    bin (bins with fewer than ``min_requests`` requests are never flagged). Spend alone follows
    the daily traffic curve; cost per request only jumps when requests got more expensive
    (context bloat, retries), which is what the cost-anomaly alert is for."""
    settings = settings or Settings.from_env({})
    spend: dict[str, dict[float, float]] = defaultdict(lambda: defaultdict(float))
    count: dict[str, dict[float, int]] = defaultdict(lambda: defaultdict(int))
    for r in d.requests:
        b = _bin(r.timestamp, bin_s)
        spend[r.tenant][b] += r.cost_usd
        count[r.tenant][b] += 1
    rows = []
    for tenant, bins in sorted(spend.items()):
        cpr = sorted(bins[b] / count[tenant][b] for b in bins if count[tenant][b] >= min_requests)
        median = cpr[len(cpr) // 2] if cpr else 0.0
        cum = 0.0
        b, last = min(bins), max(bins)
        while b <= last:
            n = count[tenant].get(b, 0)
            cost = bins.get(b, 0.0)
            cum += cost
            per_req = cost / n if n else 0.0
            rows.append(
                {
                    "time": d.label(b),
                    "ts": b,
                    "tenant": tenant,
                    "requests": n,
                    "bin_spend_usd": _r(cost, 6),
                    "cost_per_request_usd": _r(per_req, 6),
                    "cumulative_usd": _r(cum, 6),
                    "soft_cap_usd": settings.tenant_soft_cap_usd,
                    "hard_cap_usd": settings.tenant_hard_cap_usd,
                    "anomaly": bool(median and n >= min_requests and per_req > factor * median),
                }
            )
            b += bin_s
    return rows


# ---------------------------------------------------------------------------------------- traffic
def traffic(d: StoreData, *, bin_s: int = 60) -> list[dict[str, Any]]:
    """Requests per ``bin_s`` by tenant (11.2 evidence 2)."""
    acc: dict[tuple[float, str], int] = defaultdict(int)
    for r in d.requests:
        acc[(_bin(r.timestamp, bin_s), r.tenant)] += 1
    return [
        {"time": d.label(b), "ts": b, "tenant": t, "requests": n}
        for (b, t), n in sorted(acc.items())
    ]


_SEED_RE = re.compile(r"^s(\d+)-")


def shadow_traffic(d: StoreData, *, bin_s: int = 60) -> dict[str, Any]:
    """The comparison line for the traffic page.

    If the store holds the day one week before its newest day (``make replay
    DAY=2026-09-07 KEEP=1``), that day is shifted forward a week: ``source="previous week"``.
    Otherwise the plan for the previous seed with the same number of sessions is generated
    (traffic only, no agent run): ``source="replayed plan, seed N-1"``. Rows are
    ``{ts, tenant, requests}`` aligned to the newest day."""
    if not d.requests:
        return {"source": None, "rows": []}
    newest_day = _bin(max(r.timestamp for r in d.requests), DAY)
    prev = [r for r in d.requests if newest_day - WEEK <= r.timestamp < newest_day - WEEK + DAY]
    acc: dict[tuple[float, str], int] = defaultdict(int)
    if prev:
        for r in prev:
            acc[(_bin(r.timestamp + WEEK, bin_s), r.tenant)] += 1
        source = "previous week"
    else:
        from simulator.scenarios import generate_day

        m = _SEED_RE.match(d.requests[0].session_id or "")
        seed = int(m.group(1)) if m else 7
        day_reqs = [r for r in d.requests if r.timestamp >= newest_day]
        sessions = len({r.session_id for r in day_reqs})
        day = datetime.fromtimestamp(newest_day, tz=UTC).date()
        for p in generate_day(seed - 1, sessions=sessions, day=day):
            acc[(_bin(p.ts, bin_s), p.tenant)] += 1
        source = f"replayed plan, seed {seed - 1}"
    rows = [
        {"time": d.label(b), "ts": b, "tenant": t, "requests": n}
        for (b, t), n in sorted(acc.items())
    ]
    return {"source": source, "rows": rows}


# -------------------------------------------------------------------------------------- retrieval
def _result_tokens(s: SpanRecord) -> int:
    v = s.attr("atlas.tool.result_tokens")
    if v is not None:
        return int(v)
    return approx_tokens(str(s.attr("gen_ai.tool.call.result", "")))


def retrieval_hourly(d: StoreData) -> list[dict[str, Any]]:
    """Per tenant per hour: mean ``atlas.retrieval.top_k``, mean retriever result size in
    tokens (as sent to the model), hits and empty share (11.2 evidence 5)."""
    acc: dict[tuple[float, str], list[SpanRecord]] = defaultdict(list)
    for s in d.kind("retriever"):
        acc[(_bin(s.start_time, HOUR), str(s.attr("atlas.tenant", "other")))].append(s)
    rows = []
    for (h, t), v in sorted(acc.items()):
        rows.append(
            {
                "hour": d.label(h),
                "ts": h,
                "tenant": t,
                "calls": len(v),
                "mean_top_k": _r(
                    sum(int(s.attr("atlas.retrieval.top_k", 0) or 0) for s in v) / len(v), 2
                ),
                "mean_hits": _r(
                    sum(int(s.attr("atlas.retrieval.hits", 0) or 0) for s in v) / len(v), 2
                ),
                "mean_result_tokens": _r(sum(_result_tokens(s) for s in v) / len(v), 1),
                "empty_share": _r(
                    sum(1 for s in v if s.attr("atlas.retrieval.empty") is True) / len(v), 4
                ),
            }
        )
    return rows


# ------------------------------------------------------------------------------------ reliability
def tool_error_share_hourly(d: StoreData) -> list[dict[str, Any]]:
    """Error share per tool per hour (11.2 evidence 4)."""
    acc: dict[tuple[float, str], list[int]] = defaultdict(lambda: [0, 0])
    for s in d.kind("tool", "retriever"):
        key = (_bin(s.start_time, HOUR), str(s.attr("gen_ai.tool.name", s.name)))
        acc[key][0] += 1
        acc[key][1] += int(s.status == "ERROR")
    return [
        {
            "hour": d.label(h),
            "ts": h,
            "tool": tool,
            "calls": n,
            "errors": e,
            "error_share": _r(e / n, 4),
        }
        for (h, tool), (n, e) in sorted(acc.items())
    ]


def retries_hourly(d: StoreData) -> list[dict[str, Any]]:
    """Failed (retried) LLM attempts per hour by ``error.type`` and per generation."""
    gens: Counter[float] = Counter()
    errors: dict[tuple[float, str], int] = defaultdict(int)
    for s in d.kind("generation"):
        h = _bin(s.start_time, HOUR)
        gens[h] += 1
        if s.status == "ERROR":
            errors[(h, str(s.attr("error.type", "error")))] += 1
    rows = []
    for (h, reason), n in sorted(errors.items()):
        rows.append(
            {
                "hour": d.label(h),
                "ts": h,
                "reason": reason,
                "retries": n,
                "retries_per_generation": _r(n / gens[h], 4),
            }
        )
    return rows


# ------------------------------------------------------------------------------------------ safety
def safety_hourly(d: StoreData) -> list[dict[str, Any]]:
    """Per hour: injection (guardrail outcome), refusal (budget) and PII-in-output rates (8.4)."""
    acc: dict[float, list[SpanRecord]] = defaultdict(list)
    for s in d.agents:
        acc[_bin(s.start_time, HOUR)].append(s)
    rows = []
    for h, v in sorted(acc.items()):
        n = len(v)
        rows.append(
            {
                "hour": d.label(h),
                "ts": h,
                "requests": n,
                "injection_rate": _r(
                    sum(1 for s in v if s.attr("atlas.outcome") == "guardrail") / n, 4
                ),
                "refusal_rate": _r(
                    sum(1 for s in v if s.attr("atlas.outcome") == "refused") / n, 4
                ),
                "pii_in_output_rate": _r(
                    sum(1 for s in v if any(e["name"] == "pii_in_output" for e in s.events)) / n, 4
                ),
            }
        )
    return rows


# ------------------------------------------------------------------------------------------ traces
def session_traces(d: StoreData, session_id: str) -> list[dict[str, Any]]:
    return [
        {
            "trace_id": s.trace_id,
            "start": d.label(s.start_time),
            "turn": s.attr("atlas.turn"),
            "outcome": s.attr("atlas.outcome"),
            "steps": s.attr("atlas.steps"),
            "cost_usd": s.attr("atlas.cost_usd"),
            "latency_ms": _r(s.duration_ms, 1),
        }
        for s in sorted(d.agents, key=lambda s: s.start_time)
        if s.attr("session.id") == session_id
    ]


_WATERFALL_ATTRS = (
    "gen_ai.request.model",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.usage.cache_read.input_tokens",
    "atlas.cost_usd",
    "atlas.ttft_ms",
    "atlas.retrieval.top_k",
    "atlas.retrieval.hits",
    "atlas.tool.result_tokens",
    "error.type",
    "atlas.outcome",
    "atlas.steps",
)


def waterfall(d: StoreData, trace_id: str) -> list[dict[str, Any]]:
    """Spans of one trace, parents first, with start offset and duration (the Traces page)."""
    spans = d.by_trace.get(trace_id, [])
    if not spans:
        return []
    t0 = min(s.start_time for s in spans)
    children: dict[str | None, list[SpanRecord]] = defaultdict(list)
    ids = {s.span_id for s in spans}
    for s in sorted(spans, key=lambda s: (s.start_time, s.span_id)):
        children[s.parent_span_id if s.parent_span_id in ids else None].append(s)
    rows: list[dict[str, Any]] = []

    def walk(parent: str | None, depth: int) -> None:
        for s in children.get(parent, []):
            rows.append(
                {
                    "depth": depth,
                    "name": ("  " * depth) + s.name,
                    "kind": s.kind,
                    "status": s.status,
                    "start_ms": _r((s.start_time - t0) * 1000, 1),
                    "duration_ms": _r(s.duration_ms, 1),
                    **{k: s.attr(k) for k in _WATERFALL_ATTRS if s.attr(k) is not None},
                    "events": ", ".join(e["name"] for e in s.events),
                }
            )
            walk(s.span_id, depth + 1)

    walk(None, 0)
    return rows


# ------------------------------------------------------------------------------- compare replays
def compare(paths: Iterable[str | Path]) -> list[dict[str, Any]]:
    """One row per store: the numbers 6.8 and 14.2 compare, plus the change vs the first."""
    rows: list[dict[str, Any]] = []
    for p in paths:
        st = LocalSpanStore(str(p))
        d = StoreData.load(st)
        tiles = cost_tiles(d)
        h = headline(d)
        q = quality_summary(d)
        rows.append(
            {
                "store": str(p),
                "requests": h["requests"],
                "sessions": h["sessions"],
                "cost_usd": tiles["total_cost_usd"],
                "cost_per_session_usd": tiles["cost_per_session_usd"],
                "cache_hit_ratio": tiles["cache_hit_ratio"],
                "p95_ms": h["p95_ms"],
                "judge_resolved": q["judge_means"].get("resolved"),
                "judge_grounded": q["judge_means"].get("grounded"),
            }
        )
        st.close()
    if rows and rows[0]["cost_usd"]:
        base = rows[0]["cost_usd"]
        for r in rows:
            r["cost_change_pct"] = _r((r["cost_usd"] - base) / base * 100, 1)
    return rows


def to_json(obj: Any) -> str:
    return json.dumps(obj, indent=2, default=str)


__all__ = [
    "StoreData",
    "budget_timeline",
    "compare",
    "cost_by",
    "cost_tiles",
    "disagreements",
    "feedback_by_session_length",
    "feedback_hourly",
    "generation_timing_hourly",
    "headline",
    "hourly_cost_by_tenant",
    "hourly_latency",
    "hourly_unit_costs",
    "judge_by_prompt_version",
    "judge_feedback_agreement",
    "judge_hourly",
    "latency_summary",
    "live",
    "live_alerts",
    "load_store",
    "quality_summary",
    "retries_hourly",
    "retrieval_hourly",
    "safety_hourly",
    "session_traces",
    "shadow_traffic",
    "span_p95_by_type_hourly",
    "tool_error_share_hourly",
    "top_feedback_comments",
    "top_sessions",
    "traffic",
    "waterfall",
]
