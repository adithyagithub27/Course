from decimal import Decimal

import pytest

from northwind.cost import (
    CostRecord,
    cost_per_session,
    rollup,
    rollup_nested,
    showback_table,
    top_n,
    total_cost,
)


def rec(**kw):
    base = dict(
        trace_id="t",
        tenant="ops",
        model="gpt-4.1-mini",
        input_tokens=1000,
        output_tokens=100,
        cost_usd=0.001,
        timestamp=0.0,
        session_id="s1",
        user_id="u1",
        feature="policy_question",
        intent="vpn",
    )
    base.update(kw)
    return CostRecord(**base)


def test_from_usage_prices_record():
    r = CostRecord.from_usage(
        trace_id="t",
        tenant="hr",
        model="gpt-4.1-mini",
        input_tokens=1000,
        output_tokens=200,
        timestamp=1.0,
        session_id="s",
    )
    assert r.cost_usd == pytest.approx(0.00072) and r.total_tokens == 1200


def test_rollup_by_tenant():
    rs = [
        rec(tenant="ops", cost_usd=0.002),
        rec(tenant="ops", session_id="s2"),
        rec(tenant="hr", outcome="escalated"),
    ]
    r = rollup(rs, "tenant")
    assert (
        r["ops"].requests == 2
        and r["ops"].cost_usd == Decimal("0.003")
        and len(r["ops"].sessions) == 2
    )
    assert r["hr"].escalated == 1 and r["ops"].resolved == 2


def test_rollup_invalid_dimension():
    with pytest.raises(ValueError):
        rollup([rec()], "colour")


def test_rollup_derived_ratios():
    r = rollup([rec(cached_tokens=500), rec(cached_tokens=0, session_id="s2")], "model")[
        "gpt-4.1-mini"
    ]
    assert r.cache_hit_ratio == pytest.approx(0.25)
    assert r.cost_per_session == Decimal("0.001") and r.cost_per_request == Decimal("0.001")


def test_cost_per_resolved_none_when_no_resolved():
    r = rollup([rec(outcome="error")], "tenant")["ops"]
    assert r.cost_per_resolved is None and r.errors == 1


def test_total_and_per_session():
    rs = [
        rec(session_id="a", cost_usd=0.01),
        rec(session_id="a", cost_usd=0.01),
        rec(session_id="b", cost_usd=0.02),
    ]
    assert total_cost(rs) == Decimal("0.04")
    assert cost_per_session(rs) == Decimal("0.02")
    assert cost_per_session([]) == 0


def test_rollup_nested():
    rs = [
        rec(tenant="ops", feature="a"),
        rec(tenant="ops", feature="b"),
        rec(tenant="hr", feature="a"),
    ]
    n = rollup_nested(rs, "tenant", "feature")
    assert set(n) == {"ops", "hr"} and set(n["ops"]) == {"a", "b"}


def test_top_n():
    rs = [rec(tenant=f"t{i}", cost_usd=i / 1000) for i in range(6)]
    top = top_n(rollup(rs, "tenant"), 2)
    assert [t.key for t in top] == ["t5", "t4"]


def test_showback_table_markdown():
    md = showback_table([rec(), rec(tenant="hr", cost_usd=0.003)], "tenant")
    assert md.startswith("| tenant |") and "| hr |" in md and "**total**" in md and "100%" in md


def test_as_dict_roundtrip():
    d = rec().as_dict()
    assert d["tenant"] == "ops" and "cost_usd" in d
