import pytest

from northwind.sampling import (
    JudgeSampler,
    JudgeSamplingPolicy,
    TailSamplingPolicy,
    TraceSummary,
    expected_kept,
    head_sample,
)


def test_head_sample_edges_and_determinism():
    assert head_sample("abc", 1.0) is True and head_sample("abc", 0.0) is False
    assert head_sample("abc", 0.3) == head_sample("abc", 0.3)
    with pytest.raises(ValueError):
        head_sample("abc", 1.5)


@pytest.mark.parametrize("rate", [0.1, 0.25, 0.5])
def test_head_sample_rate_is_roughly_honoured(rate):
    kept = sum(head_sample(f"trace-{i}", rate) for i in range(4000))
    assert abs(kept / 4000 - rate) < 0.03


def test_tail_policy_reasons():
    p = TailSamplingPolicy(base_rate=0.0)
    assert p.should_keep(TraceSummary("t", error=True)) == (True, "error")
    assert p.should_keep(TraceSummary("t", duration_ms=5000)) == (True, "slow")
    assert p.should_keep(TraceSummary("t", cost_usd=0.5)) == (True, "expensive")
    assert p.should_keep(TraceSummary("t", steps=6)) == (True, "many_steps")
    assert p.should_keep(TraceSummary("t", escalated=True)) == (True, "escalated")
    assert p.should_keep(TraceSummary("t", feedback_negative=True)) == (True, "negative_feedback")
    assert p.should_keep(TraceSummary("t")) == (False, "rate")


def test_tail_policy_tenant_override():
    p = TailSamplingPolicy(base_rate=0.0, tenant_rates={"eng": 1.0})
    assert p.should_keep(TraceSummary("t", tenant="eng"))[0] is True
    assert p.should_keep(TraceSummary("t", tenant="hr"))[0] is False


def test_judge_policy():
    j = JudgeSamplingPolicy(rate=0.0)
    assert j.should_judge(TraceSummary("t", escalated=True))
    assert j.should_judge(TraceSummary("t", feedback_negative=True))
    assert not j.should_judge(TraceSummary("t", error=True))
    assert not j.should_judge(TraceSummary("t"))
    assert JudgeSampler is JudgeSamplingPolicy


def test_judge_and_tail_use_independent_salts():
    ids = [f"t{i}" for i in range(500)]
    tail = [head_sample(i, 0.5, salt="tail") for i in ids]
    judge = [head_sample(i, 0.5, salt="judge") for i in ids]
    assert tail != judge


def test_expected_kept():
    assert expected_kept(1000, 0.1) == 100
