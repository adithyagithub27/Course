import pytest

from northwind.budget import (
    BudgetGuard,
    Decision,
    EwmaAnomaly,
    EWMAAnomalyDetector,
    SpendWindow,
    TenantBudget,
    hourly_anomalies,
)


def test_tenant_budget_validation():
    with pytest.raises(ValueError):
        TenantBudget("ops", 10, 5)
    with pytest.raises(ValueError):
        TenantBudget("ops", -1, 5)
    with pytest.raises(ValueError):
        TenantBudget("ops", 1, 5, window_s=0)


def test_spend_window_evicts():
    w = SpendWindow(window_s=60)
    w.add(1.0, ts=0)
    w.add(2.0, ts=30)
    assert w.total(now=59) == 3.0
    assert w.total(now=61) == 2.0  # first item (ts 0) evicted at 60
    assert w.total(now=200) == 0.0 and len(w) == 0


def test_spend_window_rejects_negative():
    with pytest.raises(ValueError):
        SpendWindow(10).add(-1, 0)


def test_guard_allow_degrade_refuse():
    g = BudgetGuard.from_caps(["ops"], soft=1.0, hard=2.0)
    assert g.decide("ops", 0).decision is Decision.ALLOW
    g.record("ops", 1.0, ts=1)
    assert g.decide("ops", 2).decision is Decision.DEGRADE
    g.record("ops", 1.0, ts=3)
    d = g.decide("ops", 4)
    assert d.decision is Decision.REFUSE and d.utilisation == pytest.approx(1.0)


def test_guard_window_resets_spend():
    g = BudgetGuard.from_caps(["hr"], soft=1.0, hard=2.0, window_s=100)
    g.record("hr", 5.0, ts=0)
    assert g.decide("hr", 50).decision is Decision.REFUSE
    assert g.decide("hr", 150).decision is Decision.ALLOW


def test_guard_unknown_tenant_without_default():
    g = BudgetGuard.from_caps(["hr"], soft=1, hard=2)
    with pytest.raises(KeyError):
        g.decide("eng", 0)


def test_guard_default_budget_and_status():
    g = BudgetGuard(default_budget=TenantBudget("*", 1, 2))
    g.record("eng", 1.5, 0)
    st = {d.tenant: d.decision for d in g.status(1)}
    assert st["eng"] is Decision.DEGRADE
    assert g.decisions == {}  # status is not a decision


def test_decision_counts_and_projection():
    g = BudgetGuard.from_caps(["ops"], soft=1, hard=2)
    g.record("ops", 0.95, 0)
    assert g.decide("ops", 1, next_cost_usd=0.1).decision is Decision.DEGRADE
    assert g.decisions["ops"]["degrade"] == 1


def test_ewma_warmup_and_anomaly():
    det = EWMAAnomalyDetector(alpha=0.3, threshold=3.0, warmup=3)
    for x in [1.0, 1.1, 0.9, 1.0, 1.05]:
        assert not det.is_anomaly(x)
        det.update(x)
    assert det.is_anomaly(10.0)
    assert det.deviation(1.0) < 3.0


def test_ewma_constant_series_infinite_deviation():
    det = EWMAAnomalyDetector(warmup=2)
    for _ in range(5):
        det.update(2.0)
    assert det.deviation(2.0) == 0.0
    assert det.is_anomaly(2.5)


def test_ewma_alpha_validation():
    with pytest.raises(ValueError):
        EWMAAnomalyDetector(alpha=0)
    assert EwmaAnomaly is EWMAAnomalyDetector


def test_hourly_anomalies_flags_spike():
    series = [1.0] * 8 + [6.0] + [1.0] * 3
    assert hourly_anomalies(series, threshold=2.0, warmup=4) == [8]


def test_hourly_anomalies_none_on_flat():
    assert hourly_anomalies([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]) == []


def test_budget_decision_as_dict():
    g = BudgetGuard.from_caps(["ops"], soft=1, hard=2)
    d = g.decide("ops", 0).as_dict()
    assert d["decision"] == "allow" and d["tenant"] == "ops" and "utilisation" in d
