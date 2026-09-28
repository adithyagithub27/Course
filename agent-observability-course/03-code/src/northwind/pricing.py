"""Price table and per-token cost math.

Two sources, in order of preference:

1. ``litellm.model_cost`` when LiteLLM is importable *and* lists the model
   (kept current by the LiteLLM project).
2. :data:`FALLBACK_PRICES`, a pinned table checked against the OpenAI price
   list on 2026-09-28. Prices are USD per **1 million** tokens.

Billing semantics (OpenAI Chat Completions):

* ``prompt_tokens`` *includes* ``prompt_tokens_details.cached_tokens``; cached
  tokens are billed at the cached-input price, the remainder at the input price.
* ``completion_tokens`` *includes* ``completion_tokens_details.reasoning_tokens``;
  reasoning tokens are billed at the output price. We report them separately in
  the breakdown but never charge them twice.

All arithmetic is done in :class:`decimal.Decimal` and rounded to 8 decimal
places so that summing millions of records is reproducible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache

MILLION = Decimal(1_000_000)
QUANT = Decimal("0.00000001")  # 8 dp


@dataclass(frozen=True)
class ModelPrice:
    """USD per 1M tokens for one model."""

    model: str
    input_per_m: Decimal
    output_per_m: Decimal
    cached_input_per_m: Decimal
    source: str = "fallback"

    @property
    def input_per_token(self) -> Decimal:
        return self.input_per_m / MILLION

    @property
    def output_per_token(self) -> Decimal:
        return self.output_per_m / MILLION

    @property
    def cached_input_per_token(self) -> Decimal:
        return self.cached_input_per_m / MILLION


def _p(model: str, inp: str, out: str, cached: str) -> ModelPrice:
    return ModelPrice(model, Decimal(inp), Decimal(out), Decimal(cached), "fallback")


#: Pinned fallback prices, USD per 1M tokens (input, output, cached input).
FALLBACK_PRICES: dict[str, ModelPrice] = {
    "gpt-4.1": _p("gpt-4.1", "2.00", "8.00", "0.50"),
    "gpt-4.1-mini": _p("gpt-4.1-mini", "0.40", "1.60", "0.10"),
    "gpt-4.1-nano": _p("gpt-4.1-nano", "0.10", "0.40", "0.025"),
    "gpt-5-mini": _p("gpt-5-mini", "0.25", "2.00", "0.025"),
    "gpt-4o-mini": _p("gpt-4o-mini", "0.15", "0.60", "0.075"),
}

_DATE_SUFFIX = re.compile(r"-\d{4}-\d{2}-\d{2}$")


class UnknownModelError(KeyError):
    """Raised when neither LiteLLM nor the fallback table knows a model."""


def normalize_model_name(model: str) -> str:
    """Strip provider prefixes and date suffixes: ``openai/gpt-4.1-mini-2025-04-14`` -> ``gpt-4.1-mini``."""
    name = model.strip()
    if "/" in name:
        name = name.rsplit("/", 1)[1]
    name = _DATE_SUFFIX.sub("", name)
    return name


def _litellm_price(model: str) -> ModelPrice | None:
    """Look the model up in ``litellm.model_cost`` if LiteLLM is importable."""
    try:  # pragma: no cover - depends on optional heavy import
        import litellm  # type: ignore
    except Exception:  # noqa: BLE001
        return None
    info = litellm.model_cost.get(model)
    if not info or "input_cost_per_token" not in info or "output_cost_per_token" not in info:
        return None
    inp = Decimal(str(info["input_cost_per_token"])) * MILLION
    out = Decimal(str(info["output_cost_per_token"])) * MILLION
    cached_raw = info.get("cache_read_input_token_cost")
    cached = Decimal(str(cached_raw)) * MILLION if cached_raw is not None else inp
    return ModelPrice(model, inp, out, cached, source="litellm")


@lru_cache(maxsize=256)
def get_price(model: str, *, use_litellm: bool = False) -> ModelPrice:
    """Return the price for ``model``.

    ``use_litellm`` is False by default because importing LiteLLM takes seconds
    and needs no network; enable it in production, keep it off in unit tests.
    """
    name = normalize_model_name(model)
    if use_litellm:
        found = _litellm_price(name)
        if found is not None:
            return found
    try:
        return FALLBACK_PRICES[name]
    except KeyError as exc:
        raise UnknownModelError(name) from exc


def known_models() -> list[str]:
    """Models in the pinned table."""
    return sorted(FALLBACK_PRICES)


@dataclass(frozen=True)
class CostBreakdown:
    """Cost of one generation split by token class (USD, Decimal, 8 dp)."""

    model: str
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    reasoning_tokens: int
    input_usd: Decimal
    cached_usd: Decimal
    output_usd: Decimal
    total_usd: Decimal
    price_source: str

    @property
    def reasoning_usd(self) -> Decimal:
        """Share of ``output_usd`` attributable to reasoning tokens (informational)."""
        if self.output_tokens == 0:
            return Decimal(0)
        return _q(self.output_usd * Decimal(self.reasoning_tokens) / Decimal(self.output_tokens))

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "cached_tokens": self.cached_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "input_usd": float(self.input_usd),
            "cached_usd": float(self.cached_usd),
            "output_usd": float(self.output_usd),
            "total_usd": float(self.total_usd),
            "price_source": self.price_source,
        }


def _q(value: Decimal) -> Decimal:
    return value.quantize(QUANT, rounding=ROUND_HALF_UP)


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    *,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0,
    use_litellm: bool = False,
    price: ModelPrice | None = None,
) -> CostBreakdown:
    """Compute the cost of one generation.

    Args:
        model: model name as reported by the API (``gpt-4.1-mini-2025-04-14`` is fine).
        input_tokens: total prompt tokens **including** cached tokens.
        output_tokens: total completion tokens **including** reasoning tokens.
        cached_tokens: ``prompt_tokens_details.cached_tokens``.
        reasoning_tokens: ``completion_tokens_details.reasoning_tokens``.
        use_litellm: consult ``litellm.model_cost`` first.
        price: explicit price override (skips lookup).
    """
    if input_tokens < 0 or output_tokens < 0 or cached_tokens < 0 or reasoning_tokens < 0:
        raise ValueError("token counts must be non-negative")
    cached_tokens = min(cached_tokens, input_tokens)
    reasoning_tokens = min(reasoning_tokens, output_tokens)
    p = price or get_price(model, use_litellm=use_litellm)
    uncached = input_tokens - cached_tokens
    input_usd = _q(Decimal(uncached) * p.input_per_token)
    cached_usd = _q(Decimal(cached_tokens) * p.cached_input_per_token)
    output_usd = _q(Decimal(output_tokens) * p.output_per_token)
    total = _q(input_usd + cached_usd + output_usd)
    return CostBreakdown(
        model=p.model,
        input_tokens=input_tokens,
        cached_tokens=cached_tokens,
        output_tokens=output_tokens,
        reasoning_tokens=reasoning_tokens,
        input_usd=input_usd,
        cached_usd=cached_usd,
        output_usd=output_usd,
        total_usd=total,
        price_source=p.source,
    )


def cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    *,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0,
) -> float:
    """Convenience: total cost as a float."""
    return float(
        estimate_cost(
            model,
            input_tokens,
            output_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
        ).total_usd
    )


def cost_from_usage(model: str, usage: object) -> CostBreakdown:
    """Compute cost from an OpenAI ``CompletionUsage``-like object (duck-typed).

    Accepts Chat (``prompt_tokens``/``completion_tokens``) or Responses
    (``input_tokens``/``output_tokens``) shapes, plus the ``*_details`` objects.
    """

    def _get(obj: object, *names: str, default: int = 0) -> int:
        for n in names:
            v = getattr(obj, n, None) if not isinstance(obj, dict) else obj.get(n)
            if v is not None:
                return int(v)
        return default

    def _sub(obj: object, name: str) -> object:
        return getattr(obj, name, None) if not isinstance(obj, dict) else obj.get(name)

    inp = _get(usage, "prompt_tokens", "input_tokens")
    out = _get(usage, "completion_tokens", "output_tokens")
    in_details = _sub(usage, "prompt_tokens_details") or _sub(usage, "input_tokens_details")
    out_details = _sub(usage, "completion_tokens_details") or _sub(usage, "output_tokens_details")
    cached = _get(in_details, "cached_tokens") if in_details is not None else 0
    reasoning = _get(out_details, "reasoning_tokens") if out_details is not None else 0
    return estimate_cost(model, inp, out, cached_tokens=cached, reasoning_tokens=reasoning)


def savings_from_cache(model: str, input_tokens: int, cached_tokens: int) -> Decimal:
    """USD saved by the cached share of ``input_tokens`` vs. paying full input price."""
    p = get_price(model)
    cached_tokens = min(cached_tokens, input_tokens)
    return _q(Decimal(cached_tokens) * (p.input_per_token - p.cached_input_per_token))
