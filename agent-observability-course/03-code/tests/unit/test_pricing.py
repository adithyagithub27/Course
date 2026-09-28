from decimal import Decimal

import pytest

from northwind.pricing import (
    FALLBACK_PRICES,
    UnknownModelError,
    cost_from_usage,
    cost_usd,
    estimate_cost,
    get_price,
    known_models,
    normalize_model_name,
    savings_from_cache,
)

# Golden numbers: 1,000 input + 200 output, no cache (USD). Verified against the pinned table.
GOLDEN = {
    "gpt-4.1": Decimal("0.00360000"),  # 1000*2.00/1e6 + 200*8.00/1e6
    "gpt-4.1-mini": Decimal("0.00072000"),  # 0.0004 + 0.00032
    "gpt-4.1-nano": Decimal("0.00018000"),  # 0.0001 + 0.00008
    "gpt-5-mini": Decimal("0.00065000"),  # 0.00025 + 0.0004
    "gpt-4o-mini": Decimal("0.00027000"),  # 0.00015 + 0.00012
}


@pytest.mark.parametrize("model,expected", sorted(GOLDEN.items()))
def test_golden_costs(model, expected):
    assert estimate_cost(model, 1000, 200).total_usd == expected


@pytest.mark.parametrize("model", sorted(FALLBACK_PRICES))
def test_price_table_has_cached_price_below_input(model):
    p = FALLBACK_PRICES[model]
    assert p.cached_input_per_m < p.input_per_m < p.output_per_m


def test_cached_tokens_billed_at_cached_rate():
    cb = estimate_cost("gpt-4.1-mini", 1000, 0, cached_tokens=800)
    # 200 uncached * 0.4/M + 800 cached * 0.1/M
    assert cb.input_usd == Decimal("0.00008000")
    assert cb.cached_usd == Decimal("0.00008000")
    assert cb.total_usd == Decimal("0.00016000")


def test_cached_tokens_capped_at_input():
    cb = estimate_cost("gpt-4.1-mini", 100, 0, cached_tokens=500)
    assert cb.cached_tokens == 100 and cb.input_usd == 0


def test_reasoning_tokens_not_double_charged():
    plain = estimate_cost("gpt-5-mini", 100, 300)
    with_reasoning = estimate_cost("gpt-5-mini", 100, 300, reasoning_tokens=200)
    assert plain.total_usd == with_reasoning.total_usd
    assert with_reasoning.reasoning_usd == Decimal("0.00040000")


def test_negative_tokens_rejected():
    with pytest.raises(ValueError):
        estimate_cost("gpt-4.1", -1, 0)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("openai/gpt-4.1-mini", "gpt-4.1-mini"),
        ("gpt-4.1-mini-2025-04-14", "gpt-4.1-mini"),
        ("azure/gpt-4.1-2025-04-14", "gpt-4.1"),
        ("gpt-5-mini", "gpt-5-mini"),
    ],
)
def test_normalize_model_name(raw, expected):
    assert normalize_model_name(raw) == expected


def test_dated_model_name_priced():
    assert estimate_cost("gpt-4.1-mini-2025-04-14", 1000, 200).total_usd == GOLDEN["gpt-4.1-mini"]


def test_unknown_model_raises():
    with pytest.raises(UnknownModelError):
        get_price("gpt-99-ultra")


def test_cost_usd_float_helper():
    assert cost_usd("gpt-4.1-mini", 1000, 200) == pytest.approx(0.00072)


def test_cost_from_chat_usage_object():
    from openai.types.completion_usage import CompletionUsage, PromptTokensDetails

    u = CompletionUsage(
        prompt_tokens=1000,
        completion_tokens=200,
        total_tokens=1200,
        prompt_tokens_details=PromptTokensDetails(cached_tokens=500),
    )
    cb = cost_from_usage("gpt-4.1-mini", u)
    assert cb.cached_tokens == 500 and cb.total_usd == Decimal("0.00057000")


def test_cost_from_responses_style_dict():
    cb = cost_from_usage(
        "gpt-4.1",
        {"input_tokens": 100, "output_tokens": 10, "input_tokens_details": {"cached_tokens": 50}},
    )
    assert cb.input_tokens == 100 and cb.cached_tokens == 50


def test_savings_from_cache():
    assert savings_from_cache("gpt-4.1-mini", 1000, 1000) == Decimal("0.00030000")


def test_decimal_sum_reproducible():
    parts = [estimate_cost("gpt-4.1-mini", 333, 77).total_usd for _ in range(1000)]
    assert sum(parts) == Decimal("0.00025640") * 1000


def test_known_models_sorted():
    assert known_models() == sorted(FALLBACK_PRICES)


def test_as_dict_is_json_friendly():
    d = estimate_cost("gpt-4.1", 10, 10).as_dict()
    assert isinstance(d["total_usd"], float) and d["price_source"] == "fallback"
