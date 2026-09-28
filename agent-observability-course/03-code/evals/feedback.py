"""User feedback (thumbs up/down) as scores, and its correlation with the judge (Section 8.3).

Beware survivorship bias: people who click are not a random sample of users.
``correlate`` therefore reports feedback *rates* alongside agreement.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from northwind.config import Settings  # noqa: E402
from telemetry.local_store import LocalSpanStore, ScoreRecord  # noqa: E402

REASONS: tuple[str, ...] = ("wrong_answer", "unhelpful", "too_slow", "wrong_tool", "tone", "other")


def record_feedback(
    store: LocalSpanStore,
    *,
    trace_id: str,
    thumbs: int,
    tenant: str = "",
    session_id: str = "",
    reason: str | None = None,
    comment: str | None = None,
    ts: float | None = None,
) -> ScoreRecord:
    """Store thumbs (1 / -1 / 0) as a 1.0 / 0.0 / 0.5 ``user_feedback`` score."""
    if thumbs not in (-1, 0, 1):
        raise ValueError("thumbs must be -1, 0 or 1")
    value = {1: 1.0, 0: 0.5, -1: 0.0}[thumbs]
    rec = ScoreRecord(
        trace_id,
        "user_feedback",
        value,
        "user",
        " | ".join(x for x in (reason, comment) if x),
        ts or time.time(),
        tenant,
        session_id,
    )
    store.add_score(rec)
    return rec


@dataclass
class FeedbackSummary:
    feedback_count: int = 0
    positive: int = 0
    negative: int = 0
    requests: int = 0
    joined: int = 0
    agreement: float = 0.0
    judge_mean_when_positive: float = 0.0
    judge_mean_when_negative: float = 0.0
    by_tenant: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def response_rate(self) -> float:
        return self.feedback_count / self.requests if self.requests else 0.0

    @property
    def positive_rate(self) -> float:
        return self.positive / self.feedback_count if self.feedback_count else 0.0

    def render(self) -> str:
        return (
            f"feedback={self.feedback_count} ({self.response_rate:.1%} of {self.requests} requests) "
            f"positive={self.positive_rate:.0%} joined_with_judge={self.joined} agreement={self.agreement:.0%} "
            f"judge|👍={self.judge_mean_when_positive:.2f} judge|👎={self.judge_mean_when_negative:.2f}"
        )


def correlate(
    store: LocalSpanStore, *, judge_name: str = "judge_overall", threshold: float = 0.6
) -> FeedbackSummary:
    """Join feedback with judge scores by trace id; agreement = both say good or both say bad."""
    fb = {s.trace_id: s for s in store.scores(name="user_feedback")}
    judge = {s.trace_id: s.value for s in store.scores(name=judge_name)}
    out = FeedbackSummary(requests=store.count("agent"), feedback_count=len(fb))
    pos_j, neg_j, agree = [], [], 0
    tenants: dict[str, dict[str, float]] = {}
    for tid, s in fb.items():
        t = tenants.setdefault(s.tenant or "(none)", {"feedback": 0, "positive": 0})
        t["feedback"] += 1
        if s.value >= 0.75:
            out.positive += 1
            t["positive"] += 1
        elif s.value <= 0.25:
            out.negative += 1
        j = judge.get(tid)
        if j is None:
            continue
        out.joined += 1
        good_user = s.value >= 0.75
        good_judge = j >= threshold
        if good_user == good_judge:
            agree += 1
        (pos_j if good_user else neg_j).append(j)
    out.agreement = agree / out.joined if out.joined else 0.0
    out.judge_mean_when_positive = sum(pos_j) / len(pos_j) if pos_j else 0.0
    out.judge_mean_when_negative = sum(neg_j) / len(neg_j) if neg_j else 0.0
    for v in tenants.values():
        v["positive_rate"] = round(v["positive"] / v["feedback"], 3) if v["feedback"] else 0.0
    out.by_tenant = dict(sorted(tenants.items()))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Feedback vs judge correlation from the local store.")
    ap.add_argument("--store", default=None)
    ap.add_argument(
        "--seed", type=int, default=None, help="replay a day first if the store is empty"
    )
    args = ap.parse_args(argv)
    store = LocalSpanStore(args.store or Settings.from_env().local_store_path)
    if store.count() == 0 and args.seed is not None:
        from simulator.replay import replay_day

        replay_day(args.seed, store=store)
    s = correlate(store)
    print(s.render())
    print(json.dumps(s.by_tenant, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
