# Udemy Coding Exercises (5)

Five in-browser Python exercises for Udemy's coding exercise feature. Each is a pure-Python slice of the Atlas code base (`03-code/src/northwind/`), so students practise the exact cost, latency, budget, privacy and context maths the agent relies on, without API keys, Langfuse or third-party packages.

| # | Exercise | Student file | Placement (after lecture) | Related lectures | Tests |
|---|---|---|---|---|---|
| CE1 | Per-Token Cost with Cached Tokens | `pricing.py` | 6.2 | 6.1, 6.2, 6.3, 9.1 | 12 |
| CE2 | p95 Latency and a Budget Gate | `latency.py` | 7.2 | 7.1, 7.2, 13.3 | 12 |
| CE3 | EWMA Anomaly Detector for Tenant Spend | `anomaly.py` | 6.7 | 6.7, 8.5, 9.5 | 10 |
| CE4 | Mask PII in Span Attributes | `pii.py` | 10.2 | 4.6, 10.1, 10.2 | 9 |
| CE5 | Trim the Context to a Token Budget | `context.py` | 6.5 | 6.1, 6.5, 11.2 | 11 |

## How to enter these in Udemy

For each exercise: Curriculum → **+ Curriculum item** → **Coding Exercise** → language **Python 3**. Then fill:

| Udemy field | What to paste from this file |
|---|---|
| Title | The exercise title |
| Learning objective | The "Learning objective" line |
| Instructions (tab 1) | The "Instructions" block |
| Solution file | The "Solution" code, using the file name shown |
| Evaluation file | The "Tests" code (Python `unittest`; class name `Evaluate`) |
| Starter code / student file | The "Starter code" block, using the same file name as the solution |
| Hints | The "Hints" list |
| Solution explanation | The "Solution explanation" paragraph |
| Related lectures | The lecture IDs listed |

Constraints respected: standard library only (`re`, `math`, `hashlib`), Python 3.11 syntax, no file or network I/O, each test finishes in milliseconds. The price table in CE1 is pinned inside the exercise so the tests never depend on `litellm`.

**Verification.** Every solution was run against its evaluation file with `python3 -m unittest` on Python 3.11 (all 54 tests pass), and every starter file was run against the same tests to confirm it imports cleanly and fails (so students start red). Re-run the check with the script in the appendix after any edit.

---

## CE1: Per-Token Cost with Cached Tokens

**Related lectures:** 6.1 Where the money goes: token anatomy; 6.2 Code-along: a price table you can trust; 6.3 Cost per request, session, user, tenant and feature  
**Learning objective:** Compute the dollar cost of one LLM call from its usage object, treating cached input tokens as a discounted subset of input tokens and reasoning tokens as output tokens, then roll it up to cost per resolved session.

### Instructions

Atlas records the OpenAI `usage` object on every generation span. Finance wants a dollar figure per call that is right to the cent over a month, so the maths has to match how the provider bills. Implement three functions in `pricing.py` using the `PRICES` table provided (dollars per one million tokens):

1. `token_cost(model, input_tokens, output_tokens, cached_input_tokens=0, reasoning_tokens=0, prices=PRICES)` returns a dict with keys `input`, `cached_input`, `output`, `total`, each rounded to 8 decimal places.
   - `input_tokens` **includes** `cached_input_tokens`, exactly as `usage.prompt_tokens` includes `prompt_tokens_details.cached_tokens`. Bill only the uncached remainder at the `input` price and the cached part at the `cached_input` price.
   - `reasoning_tokens` are a subset of `output_tokens` and are billed at the `output` price, so they never change the total; they are validated only.
   - Raise `KeyError` for a model that is not in the price table, and `ValueError` for negative counts, `cached_input_tokens > input_tokens` or `reasoning_tokens > output_tokens`.
2. `cache_savings(model, input_tokens, cached_input_tokens, prices=PRICES)` returns the dollars saved by the cache: `cached_input_tokens * (input - cached_input) / 1e6`, rounded to 8 dp, with the same validation.
3. `cost_per_resolved_session(session_costs, resolved_flags)` returns total cost divided by the number of sessions whose flag is true, rounded to 6 dp. Raise `ValueError` for mismatched lengths or zero resolved sessions.

Example: a `gpt-4.1-mini` call with 1,200 input tokens (900 cached) and 180 output tokens costs `0.00012 + 0.00009 + 0.000288 = 0.000498` dollars.

### Starter code (`pricing.py`)

```python
"""Northwind Atlas: per-token cost with cached and reasoning tokens (pure Python)."""

# Prices in US dollars per one million tokens (illustrative, pinned for the exercise).
PRICES = {
    "gpt-4.1-mini": {"input": 0.40, "cached_input": 0.10, "output": 1.60},
    "gpt-4.1": {"input": 2.00, "cached_input": 0.50, "output": 8.00},
    "gpt-5-mini": {"input": 0.25, "cached_input": 0.025, "output": 2.00},
}


def token_cost(model, input_tokens, output_tokens, cached_input_tokens=0,
               reasoning_tokens=0, prices=PRICES):
    """Return a cost breakdown in dollars for one LLM call.

    - input_tokens INCLUDES cached_input_tokens (as the OpenAI usage object reports it).
      Only the uncached remainder is billed at the "input" price.
    - reasoning_tokens are a subset of output_tokens and are billed at the output price.
    - Round every value to 8 decimal places.
    - Return {"input": ..., "cached_input": ..., "output": ..., "total": ...}.
    - Raise KeyError for an unknown model, ValueError for negative counts,
      cached_input_tokens > input_tokens or reasoning_tokens > output_tokens.
    """
    # TODO
    raise NotImplementedError


def cache_savings(model, input_tokens, cached_input_tokens, prices=PRICES):
    """Dollars saved because cached_input_tokens were billed at the cached price.

    savings = cached_input_tokens * (input_price - cached_input_price) / 1e6, rounded to 8 dp.
    Same validation rules as token_cost.
    """
    # TODO
    raise NotImplementedError


def cost_per_resolved_session(session_costs, resolved_flags):
    """Total cost divided by the number of resolved sessions, rounded to 6 dp.

    session_costs: list of dollar amounts, one per session.
    resolved_flags: list of booleans, same length.
    Raise ValueError if the lists differ in length or nothing was resolved.
    """
    # TODO
    raise NotImplementedError
```

### Solution (`pricing.py`)

```python
"""Northwind Atlas: per-token cost with cached and reasoning tokens (pure Python)."""

# Prices in US dollars per one million tokens (illustrative, pinned for the exercise).
PRICES = {
    "gpt-4.1-mini": {"input": 0.40, "cached_input": 0.10, "output": 1.60},
    "gpt-4.1": {"input": 2.00, "cached_input": 0.50, "output": 8.00},
    "gpt-5-mini": {"input": 0.25, "cached_input": 0.025, "output": 2.00},
}


def token_cost(model, input_tokens, output_tokens, cached_input_tokens=0,
               reasoning_tokens=0, prices=PRICES):
    """Return a cost breakdown in dollars for one LLM call.

    - input_tokens INCLUDES cached_input_tokens (as the OpenAI usage object reports it).
      Only the uncached remainder is billed at the "input" price.
    - reasoning_tokens are a subset of output_tokens and are billed at the output price.
    - Round every value to 8 decimal places.
    - Raise KeyError for an unknown model, ValueError for negative counts,
      cached_input_tokens > input_tokens or reasoning_tokens > output_tokens.
    """
    if model not in prices:
        raise KeyError(f"no price for model {model!r}")
    for name, value in (("input_tokens", input_tokens), ("output_tokens", output_tokens),
                        ("cached_input_tokens", cached_input_tokens),
                        ("reasoning_tokens", reasoning_tokens)):
        if value < 0:
            raise ValueError(f"{name} must be >= 0")
    if cached_input_tokens > input_tokens:
        raise ValueError("cached_input_tokens cannot exceed input_tokens")
    if reasoning_tokens > output_tokens:
        raise ValueError("reasoning_tokens cannot exceed output_tokens")

    price = prices[model]
    uncached = input_tokens - cached_input_tokens
    input_cost = uncached * price["input"] / 1_000_000
    cached_cost = cached_input_tokens * price["cached_input"] / 1_000_000
    output_cost = output_tokens * price["output"] / 1_000_000
    total = input_cost + cached_cost + output_cost
    return {
        "input": round(input_cost, 8),
        "cached_input": round(cached_cost, 8),
        "output": round(output_cost, 8),
        "total": round(total, 8),
    }


def cache_savings(model, input_tokens, cached_input_tokens, prices=PRICES):
    """Dollars saved because cached_input_tokens were billed at the cached price.

    savings = cached_input_tokens * (input_price - cached_input_price) / 1e6, rounded to 8 dp.
    """
    if model not in prices:
        raise KeyError(f"no price for model {model!r}")
    if cached_input_tokens < 0 or input_tokens < 0:
        raise ValueError("token counts must be >= 0")
    if cached_input_tokens > input_tokens:
        raise ValueError("cached_input_tokens cannot exceed input_tokens")
    price = prices[model]
    return round(cached_input_tokens * (price["input"] - price["cached_input"]) / 1_000_000, 8)


def cost_per_resolved_session(session_costs, resolved_flags):
    """Total cost divided by the number of resolved sessions, rounded to 6 dp.

    session_costs: list of dollar amounts, one per session.
    resolved_flags: list of booleans, same length.
    Raise ValueError if the lists differ in length or nothing was resolved.
    """
    if len(session_costs) != len(resolved_flags):
        raise ValueError("session_costs and resolved_flags must have the same length")
    resolved = sum(1 for flag in resolved_flags if flag)
    if resolved == 0:
        raise ValueError("no resolved sessions")
    return round(sum(session_costs) / resolved, 6)
```

### Tests (evaluation file `test_pricing.py`)

```python
import unittest

from pricing import PRICES, cache_savings, cost_per_resolved_session, token_cost


class Evaluate(unittest.TestCase):
    def test_simple_call_no_cache(self):
        cost = token_cost("gpt-4.1-mini", 1000, 500)
        self.assertAlmostEqual(cost["input"], 0.0004)
        self.assertAlmostEqual(cost["cached_input"], 0.0)
        self.assertAlmostEqual(cost["output"], 0.0008)
        self.assertAlmostEqual(cost["total"], 0.0012)

    def test_cached_tokens_are_a_subset_of_input(self):
        # 1200 prompt tokens of which 900 were served from cache
        cost = token_cost("gpt-4.1-mini", 1200, 180, cached_input_tokens=900)
        self.assertAlmostEqual(cost["input"], 300 * 0.40 / 1e6)
        self.assertAlmostEqual(cost["cached_input"], 900 * 0.10 / 1e6)
        self.assertAlmostEqual(cost["output"], 180 * 1.60 / 1e6)
        self.assertAlmostEqual(cost["total"], 0.00012 + 0.00009 + 0.000288)

    def test_cache_is_cheaper_than_no_cache(self):
        with_cache = token_cost("gpt-4.1-mini", 1200, 180, cached_input_tokens=900)["total"]
        without = token_cost("gpt-4.1-mini", 1200, 180)["total"]
        self.assertLess(with_cache, without)

    def test_reasoning_tokens_billed_as_output(self):
        plain = token_cost("gpt-5-mini", 500, 400)
        reasoning = token_cost("gpt-5-mini", 500, 400, reasoning_tokens=300)
        self.assertAlmostEqual(plain["total"], reasoning["total"])
        self.assertAlmostEqual(reasoning["output"], 400 * 2.00 / 1e6)

    def test_escalation_model_is_more_expensive(self):
        mini = token_cost("gpt-4.1-mini", 2000, 300)["total"]
        big = token_cost("gpt-4.1", 2000, 300)["total"]
        self.assertAlmostEqual(big / mini, 5.0)

    def test_custom_price_table(self):
        prices = {"local-llm": {"input": 0.0, "cached_input": 0.0, "output": 0.0}}
        self.assertEqual(token_cost("local-llm", 10, 10, prices=prices)["total"], 0.0)

    def test_unknown_model(self):
        with self.assertRaises(KeyError):
            token_cost("gpt-99", 10, 10)

    def test_validation(self):
        with self.assertRaises(ValueError):
            token_cost("gpt-4.1-mini", -1, 10)
        with self.assertRaises(ValueError):
            token_cost("gpt-4.1-mini", 100, 10, cached_input_tokens=101)
        with self.assertRaises(ValueError):
            token_cost("gpt-4.1-mini", 100, 10, reasoning_tokens=11)

    def test_cache_savings(self):
        self.assertAlmostEqual(cache_savings("gpt-4.1-mini", 1200, 900), 900 * 0.30 / 1e6)
        self.assertAlmostEqual(cache_savings("gpt-4.1", 5000, 0), 0.0)
        with self.assertRaises(ValueError):
            cache_savings("gpt-4.1", 100, 200)

    def test_cost_per_resolved_session(self):
        costs = [0.02, 0.05, 0.01, 0.04]
        resolved = [True, False, True, False]
        self.assertAlmostEqual(cost_per_resolved_session(costs, resolved), 0.06)

    def test_cost_per_resolved_session_errors(self):
        with self.assertRaises(ValueError):
            cost_per_resolved_session([0.1], [False])
        with self.assertRaises(ValueError):
            cost_per_resolved_session([0.1, 0.2], [True])

    def test_price_table_has_three_models(self):
        self.assertEqual(set(PRICES), {"gpt-4.1-mini", "gpt-4.1", "gpt-5-mini"})
```

### Hints

1. Work in dollars per token by dividing the per-million price by `1_000_000` once; do not round until the end.
2. `uncached = input_tokens - cached_input_tokens` is the only subtraction you need; cached tokens are already inside the input count.
3. Reasoning tokens change nothing in the total because they are already part of `output_tokens`. The validation is there to catch a usage object that was parsed wrongly.
4. Validate before you calculate, and validate the model first so an unknown model raises `KeyError` even with bad counts.
5. For cost per resolved session, count `True` flags with `sum(1 for f in flags if f)`; dividing by `len(costs)` is the classic mistake (that is cost per session, not per resolved session).

### Solution explanation

The solution mirrors how the OpenAI usage object reports tokens: `prompt_tokens` is the whole prompt, and `prompt_tokens_details.cached_tokens` is the slice of it that was served from the prompt cache at a discount (a quarter of the input price for the gpt-4.1 family in this table). Getting the subset relationship wrong double-counts cached tokens and inflates cost by up to 25 percent on cache-heavy traffic, which is exactly the kind of error that makes finance stop trusting the showback report. Reasoning tokens are billed as output, so the function accepts them for validation but never prices them separately. `cost_per_resolved_session` is the headline SLI from lecture 9.1: it divides all spend, including the sessions that failed, by the sessions that actually helped someone. The repo's `src/northwind/pricing.py` builds on this with `litellm.model_cost` as the live price source and this pinned table as the fallback, and `cost.py` does the same roll-up per tenant, user and feature from span attributes.

---

## CE2: p95 Latency and a Budget Gate

**Related lectures:** 7.1 Latency budgets for agents; 7.2 Code-along: measure TTFT, TPOT and p95 from spans; 13.3 Code-along: the CI budget gate  
**Learning objective:** Compute percentiles with linear interpolation, summarise a latency sample, decide whether it violates a budget, and derive decode speed from time to first token.

### Instructions

Atlas's latency budget is written in terms of p95, not the mean, because one slow request in twenty is what employees remember. Implement four functions in `latency.py` (all inputs are in milliseconds unless stated):

1. `percentile(values, p)`: sort the values; the rank is `r = (p / 100) * (n - 1)`. If `r` is an integer, return `values[r]`; otherwise interpolate linearly between the two neighbouring values. Return a float. Raise `ValueError` for an empty list or `p` outside 0..100.
2. `summarize(values)` returns `{"count", "mean", "p50", "p95", "p99", "max"}`, with `mean` and the percentiles rounded to 3 decimal places and `max` as a float. Raise `ValueError` for an empty list.
3. `check_budget(values, budgets)`: `budgets` is a dict such as `{"p95": 4000, "p99": 8000}` whose keys may be `p50`, `p95`, `p99`, `mean` or `max`. Return a list of `{"metric", "observed", "budget"}` dicts for every budget that is exceeded (`observed > budget`). An empty list means the gate passes. Raise `ValueError` for any other key (including `count`).
4. `tokens_per_second(output_tokens, ttft_ms, total_ms)`: decode speed after the first token, `(output_tokens - 1) / ((total_ms - ttft_ms) / 1000)`, rounded to 2 dp. Return `0.0` when `output_tokens < 2` or `total_ms <= ttft_ms`. Raise `ValueError` for negative inputs.

Example: `percentile([100, 200, 300, 400, 500], 95)` is `480.0` (rank 3.8 lies 80 percent of the way from 400 to 500).

### Starter code (`latency.py`)

```python
"""Northwind Atlas: latency percentiles and a budget check (pure Python)."""
import math


def percentile(values, p):
    """Return the p-th percentile (0 <= p <= 100) using linear interpolation.

    Sort the values; the rank is r = (p / 100) * (n - 1). If r is an integer,
    return values[r]; otherwise interpolate linearly between the two neighbours.
    Raise ValueError for an empty list or p outside 0..100.
    """
    # TODO
    raise NotImplementedError


def summarize(values):
    """Return {"count", "mean", "p50", "p95", "p99", "max"} for a list of latencies.

    Round mean and percentiles to 3 decimal places. Raise ValueError for an empty list.
    """
    # TODO
    raise NotImplementedError


def check_budget(values, budgets):
    """Compare a latency sample with a budget dict such as {"p95": 4000, "p99": 8000}.

    Return a list of violation dicts {"metric", "observed", "budget"} for every
    budget that is exceeded (observed > budget). Keys may be "p50", "p95", "p99",
    "mean" or "max". An empty list means the budget holds. Raise ValueError for an
    unknown metric name.
    """
    # TODO
    raise NotImplementedError


def tokens_per_second(output_tokens, ttft_ms, total_ms):
    """Decode speed after the first token: (output_tokens - 1) / ((total_ms - ttft_ms) / 1000).

    Return 0.0 when output_tokens < 2 or total_ms <= ttft_ms. Round to 2 dp.
    Raise ValueError for negative inputs.
    """
    # TODO
    raise NotImplementedError
```

### Solution (`latency.py`)

```python
"""Northwind Atlas: latency percentiles and a budget check (pure Python)."""
import math


def percentile(values, p):
    """Return the p-th percentile (0 <= p <= 100) using linear interpolation.

    Sort the values; the rank is r = (p / 100) * (n - 1). If r is an integer,
    return values[r]; otherwise interpolate linearly between the two neighbours.
    Raise ValueError for an empty list or p outside 0..100.
    """
    if not values:
        raise ValueError("percentile of an empty list is undefined")
    if not 0 <= p <= 100:
        raise ValueError("p must be between 0 and 100")
    ordered = sorted(values)
    rank = (p / 100) * (len(ordered) - 1)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize(values):
    """Return {"count", "mean", "p50", "p95", "p99", "max"} for a list of latencies.

    Round mean and percentiles to 3 decimal places. Raise ValueError for an empty list.
    """
    if not values:
        raise ValueError("cannot summarize an empty list")
    return {
        "count": len(values),
        "mean": round(sum(values) / len(values), 3),
        "p50": round(percentile(values, 50), 3),
        "p95": round(percentile(values, 95), 3),
        "p99": round(percentile(values, 99), 3),
        "max": float(max(values)),
    }


def check_budget(values, budgets):
    """Compare a latency sample with a budget dict such as {"p95": 4000, "p99": 8000}.

    Return a list of violation dicts {"metric", "observed", "budget"} for every
    budget that is exceeded (observed > budget). Keys may be "p50", "p95", "p99",
    "mean" or "max". An empty list means the budget holds. Raise ValueError for an
    unknown metric name.
    """
    stats = summarize(values)
    violations = []
    for metric, budget in budgets.items():
        if metric not in stats or metric == "count":
            raise ValueError(f"unknown latency metric {metric!r}")
        observed = stats[metric]
        if observed > budget:
            violations.append({"metric": metric, "observed": observed, "budget": budget})
    return violations


def tokens_per_second(output_tokens, ttft_ms, total_ms):
    """Decode speed after the first token: (output_tokens - 1) / ((total_ms - ttft_ms) / 1000).

    Return 0.0 when output_tokens < 2 or total_ms <= ttft_ms. Round to 2 dp.
    Raise ValueError for negative inputs.
    """
    if output_tokens < 0 or ttft_ms < 0 or total_ms < 0:
        raise ValueError("inputs must be >= 0")
    if output_tokens < 2 or total_ms <= ttft_ms:
        return 0.0
    return round((output_tokens - 1) / ((total_ms - ttft_ms) / 1000), 2)
```

### Tests (evaluation file `test_latency.py`)

```python
import unittest

from latency import check_budget, percentile, summarize, tokens_per_second


class Evaluate(unittest.TestCase):
    def test_percentile_exact_ranks(self):
        values = [100, 200, 300, 400, 500]
        self.assertEqual(percentile(values, 0), 100.0)
        self.assertEqual(percentile(values, 50), 300.0)
        self.assertEqual(percentile(values, 100), 500.0)

    def test_percentile_interpolates(self):
        values = [100, 200, 300, 400, 500]
        # rank = 0.95 * 4 = 3.8 -> 400 + 0.8 * 100
        self.assertAlmostEqual(percentile(values, 95), 480.0)
        # rank = 0.25 * 4 = 1.0 -> 200
        self.assertAlmostEqual(percentile(values, 25), 200.0)

    def test_percentile_unsorted_input(self):
        self.assertAlmostEqual(percentile([500, 100, 300, 200, 400], 95), 480.0)

    def test_single_value(self):
        self.assertEqual(percentile([1234], 95), 1234.0)

    def test_percentile_errors(self):
        with self.assertRaises(ValueError):
            percentile([], 95)
        with self.assertRaises(ValueError):
            percentile([1, 2], 101)
        with self.assertRaises(ValueError):
            percentile([1, 2], -1)

    def test_mean_hides_the_tail(self):
        # 18 fast requests and two 12-second outliers: the mean looks fine, p95 does not
        values = [900] * 18 + [12000] * 2
        stats = summarize(values)
        self.assertAlmostEqual(stats["mean"], 2010.0)
        self.assertLess(stats["mean"], 4000)
        self.assertEqual(stats["p50"], 900.0)
        self.assertGreater(stats["p95"], 4000)
        self.assertEqual(stats["max"], 12000.0)
        self.assertEqual(stats["count"], 20)

    def test_summarize_rounds(self):
        stats = summarize([1, 2, 4])
        self.assertEqual(stats["mean"], 2.333)
        self.assertEqual(stats["p95"], 3.8)

    def test_check_budget_passes(self):
        values = [1200, 1500, 1800, 2200, 2600, 3000]
        self.assertEqual(check_budget(values, {"p95": 4000}), [])

    def test_check_budget_reports_violation(self):
        values = [900] * 18 + [12000] * 2
        violations = check_budget(values, {"p95": 4000, "p50": 1000})
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["metric"], "p95")
        self.assertEqual(violations[0]["budget"], 4000)
        self.assertGreater(violations[0]["observed"], 4000)

    def test_check_budget_multiple_metrics(self):
        values = [5000, 6000, 7000]
        violations = check_budget(values, {"mean": 4000, "max": 6500, "p50": 6000})
        self.assertEqual({v["metric"] for v in violations}, {"mean", "max"})

    def test_check_budget_unknown_metric(self):
        with self.assertRaises(ValueError):
            check_budget([1, 2, 3], {"p42": 10})
        with self.assertRaises(ValueError):
            check_budget([1, 2, 3], {"count": 10})

    def test_tokens_per_second(self):
        # 181 output tokens, first token after 400 ms, done at 2400 ms -> 180 tokens in 2 s
        self.assertEqual(tokens_per_second(181, 400, 2400), 90.0)
        self.assertEqual(tokens_per_second(1, 400, 2400), 0.0)
        self.assertEqual(tokens_per_second(50, 900, 900), 0.0)
        with self.assertRaises(ValueError):
            tokens_per_second(-5, 0, 100)
```

### Hints

1. Sort a copy of the list; never assume the spans arrive in order.
2. `math.floor(rank)` and `math.ceil(rank)` give the two neighbours; when they are equal there is nothing to interpolate.
3. For `check_budget`, call `summarize` once and look the metric up in the result instead of recomputing per key.
4. The 18-fast-plus-2-slow test is the point of the exercise: the mean stays under budget while p95 blows through it.
5. Tokens per second uses `output_tokens - 1` because the first token's time is already counted in TTFT.

### Solution explanation

The percentile function uses the same linear-interpolation definition as NumPy's default, which is what Grafana shows when you use `histogram_quantile` on a fine-grained histogram, so the numbers students compute by hand match what they see on the dashboard within bucket resolution. The `summarize` and `check_budget` pair is the core of `tests/budget/test_budget_gate.py` from lecture 13.3: replay the day offline, summarise the request durations, compare with the budgets in `config.py`, and fail the pull request when any metric is exceeded. The test with eighteen 900 ms requests and two 12 second requests shows why the budget is written on p95: the mean is 2,010 ms and looks healthy against a 4,000 ms budget, while p95 is 12,000 ms. `tokens_per_second` is the inverse of TPOT from lecture 5.4 and is the number you compare across providers during the `slow_provider` chaos demo. The repo's `src/northwind/latency.py` adds TTFT extraction from `gen_ai.response.time_to_first_chunk` and a `LatencyBudget` dataclass.

---

## CE3: EWMA Anomaly Detector for Tenant Spend

**Related lectures:** 6.7 Budgets and anomaly alerts per tenant; 8.5 Drift detection: compare this week to last week; 9.5 Alert rules and the runbook  
**Learning objective:** Implement an exponentially weighted moving average detector with a running variance, a warm-up period and a zero-variance guard, and use it to flag a cost spike without alerting on slow drift.

### Instructions

A fixed daily cap catches runaway spend only at the end of the day. Atlas also watches hourly spend per tenant with an EWMA detector that raises an alert when the latest value is far outside what the recent history predicts. Implement `EWMADetector` and `scan` in `anomaly.py`.

`EWMADetector(alpha=0.3, threshold=3.0, warmup=5, min_std=1e-9)`:
- Validate `0 < alpha <= 1`, `threshold > 0`, `warmup >= 1` (raise `ValueError`). Initialise `mean = None`, `variance = 0.0`, `count = 0`.
- `std` (a property) is `sqrt(variance)`, or `0.0` before the first value.
- `update(x)` returns a tuple `(is_anomaly, expected_mean, z_score)` describing the state **before** `x` is folded in, then updates the state:
  - First value: set `mean = x`, `variance = 0`, `count = 1`, return `(False, x, 0.0)`.
  - Otherwise `delta = x - mean`; `z = delta / std` (or `0.0` when `std < min_std`), rounded to 4 dp.
  - `is_anomaly` is true only when `count >= warmup`, `std >= min_std` and `abs(delta) > threshold * std`.
  - Then update: `mean += alpha * delta`; `variance = (1 - alpha) * (variance + alpha * delta * delta)`; `count += 1`.

`scan(values, **kwargs)` runs a fresh detector over a list and returns the indexes flagged as anomalies.

Example: with `alpha=0.5` and values 10 then 20, the state becomes `mean = 15`, `variance = 25`, `std = 5`; a third value of 30 has `z = 3.0`, which is **not** an anomaly at `threshold = 3.0` because the comparison is strict.

### Starter code (`anomaly.py`)

```python
"""Northwind Atlas: EWMA anomaly detector for per-tenant spend (pure Python)."""
import math


class EWMADetector:
    """Flag a value as anomalous when it deviates from the running EWMA by more than
    `threshold` running standard deviations.

    State: `mean` (EWMA of the values) and `variance` (EWMA of squared deviations).
    Update rules, applied AFTER the anomaly decision for the new value x:
        delta    = x - mean
        mean     = mean + alpha * delta
        variance = (1 - alpha) * (variance + alpha * delta * delta)
    The first value initialises mean = x and variance = 0.

    A value is anomalous when:
        - at least `warmup` values have already been seen, and
        - |x - mean| > threshold * sqrt(variance), and
        - sqrt(variance) >= min_std (protects against a flat history where any
          change would be infinitely many standard deviations).
    """

    def __init__(self, alpha=0.3, threshold=3.0, warmup=5, min_std=1e-9):
        # Validate: 0 < alpha <= 1, threshold > 0, warmup >= 1 (ValueError otherwise)
        # Initialise: mean = None, variance = 0.0, count = 0
        # TODO
        raise NotImplementedError

    @property
    def std(self):
        """Running standard deviation (0.0 before the first value)."""
        # TODO
        raise NotImplementedError

    def update(self, x):
        """Consume one value and return (is_anomaly, expected_mean, z_score).

        expected_mean and z_score describe the state BEFORE x is folded in.
        z_score = (x - mean) / std, or 0.0 when std < min_std; round z to 4 dp.
        For the very first value return (False, x, 0.0).
        """
        # TODO
        raise NotImplementedError


def scan(values, **kwargs):
    """Run a fresh EWMADetector over `values` and return the indexes flagged as anomalies."""
    # TODO
    raise NotImplementedError
```

### Solution (`anomaly.py`)

```python
"""Northwind Atlas: EWMA anomaly detector for per-tenant spend (pure Python)."""
import math


class EWMADetector:
    """Flag a value as anomalous when it deviates from the running EWMA by more than
    `threshold` running standard deviations.

    State: `mean` (EWMA of the values) and `variance` (EWMA of squared deviations).
    Update rules, applied AFTER the anomaly decision for the new value x:
        delta    = x - mean
        mean     = mean + alpha * delta
        variance = (1 - alpha) * (variance + alpha * delta * delta)
    The first value initialises mean = x and variance = 0.

    A value is anomalous when:
        - at least `warmup` values have already been seen, and
        - |x - mean| > threshold * sqrt(variance), and
        - sqrt(variance) >= min_std (protects against a flat history where any
          change would be infinitely many standard deviations).
    """

    def __init__(self, alpha=0.3, threshold=3.0, warmup=5, min_std=1e-9):
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        if warmup < 1:
            raise ValueError("warmup must be at least 1")
        self.alpha = alpha
        self.threshold = threshold
        self.warmup = warmup
        self.min_std = min_std
        self.mean = None
        self.variance = 0.0
        self.count = 0

    @property
    def std(self):
        """Running standard deviation (0.0 before the first value)."""
        return math.sqrt(self.variance) if self.mean is not None else 0.0

    def update(self, x):
        """Consume one value and return (is_anomaly, expected_mean, z_score).

        expected_mean and z_score describe the state BEFORE x is folded in.
        For the very first value return (False, x, 0.0).
        """
        if self.mean is None:
            self.mean = float(x)
            self.variance = 0.0
            self.count = 1
            return False, float(x), 0.0

        expected = self.mean
        std = self.std
        delta = x - expected
        z = delta / std if std >= self.min_std else 0.0
        is_anomaly = (
            self.count >= self.warmup
            and std >= self.min_std
            and abs(delta) > self.threshold * std
        )

        self.mean = expected + self.alpha * delta
        self.variance = (1 - self.alpha) * (self.variance + self.alpha * delta * delta)
        self.count += 1
        return is_anomaly, expected, round(z, 4)


def scan(values, **kwargs):
    """Run a fresh EWMADetector over `values` and return the indexes flagged as anomalies."""
    detector = EWMADetector(**kwargs)
    flagged = []
    for index, value in enumerate(values):
        is_anomaly, _, _ = detector.update(value)
        if is_anomaly:
            flagged.append(index)
    return flagged
```

### Tests (evaluation file `test_anomaly.py`)

```python
import math
import unittest

from anomaly import EWMADetector, scan


class Evaluate(unittest.TestCase):
    def test_first_value_is_never_anomalous(self):
        det = EWMADetector()
        self.assertEqual(det.update(12.0), (False, 12.0, 0.0))
        self.assertEqual(det.mean, 12.0)
        self.assertEqual(det.std, 0.0)

    def test_mean_update_rule(self):
        det = EWMADetector(alpha=0.5)
        det.update(10.0)
        det.update(20.0)
        # mean = 10 + 0.5 * 10 = 15; variance = 0.5 * (0 + 0.5 * 100) = 25
        self.assertAlmostEqual(det.mean, 15.0)
        self.assertAlmostEqual(det.variance, 25.0)
        self.assertAlmostEqual(det.std, 5.0)

    def test_expected_and_z_describe_state_before_update(self):
        det = EWMADetector(alpha=0.5, warmup=1)
        det.update(10.0)
        det.update(20.0)          # mean 15, std 5
        is_anomaly, expected, z = det.update(30.0)
        self.assertAlmostEqual(expected, 15.0)
        self.assertAlmostEqual(z, 3.0)
        self.assertFalse(is_anomaly)   # 3.0 is not strictly greater than threshold 3.0

    def test_flat_history_does_not_divide_by_zero(self):
        det = EWMADetector(warmup=1)
        for _ in range(10):
            det.update(5.0)
        is_anomaly, expected, z = det.update(50.0)
        self.assertFalse(is_anomaly)   # std is 0, so no decision can be made
        self.assertEqual(expected, 5.0)
        self.assertEqual(z, 0.0)

    def test_warmup_suppresses_early_alerts(self):
        values = [10, 11, 9, 10, 40]
        # index 4 is a big jump, but only 4 values were seen before it
        self.assertEqual(scan(values, alpha=0.3, threshold=2.0, warmup=5), [])
        self.assertEqual(scan(values, alpha=0.3, threshold=2.0, warmup=4), [4])

    def test_cost_spike_is_flagged(self):
        # Hourly spend for the ops tenant: stable around $2, then a retry storm
        spend = [2.0, 2.1, 1.9, 2.0, 2.2, 1.8, 2.0, 2.1, 1.9, 2.0, 9.5]
        self.assertEqual(scan(spend, alpha=0.3, threshold=3.0, warmup=5), [10])

    def test_slow_drift_is_not_flagged(self):
        spend = [2.0 + 0.05 * i for i in range(30)]
        self.assertEqual(scan(spend, alpha=0.3, threshold=3.0, warmup=5), [])

    def test_detector_adapts_after_a_step_change(self):
        # After the step, the new level becomes normal within a few points
        values = [2.0, 2.1, 1.9, 2.0, 2.2, 1.8, 2.0, 2.1, 1.9, 2.0] + [6.0] * 12
        flagged = scan(values, alpha=0.3, threshold=3.0, warmup=5)
        self.assertIn(10, flagged)
        self.assertNotIn(21, flagged)

    def test_std_property_matches_variance(self):
        det = EWMADetector(alpha=0.3)
        for v in [1, 4, 2, 8]:
            det.update(v)
        self.assertAlmostEqual(det.std, math.sqrt(det.variance))

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            EWMADetector(alpha=0)
        with self.assertRaises(ValueError):
            EWMADetector(alpha=1.5)
        with self.assertRaises(ValueError):
            EWMADetector(threshold=0)
        with self.assertRaises(ValueError):
            EWMADetector(warmup=0)
```

### Hints

1. Compute `expected`, `std`, `delta` and the decision first, store them in locals, and only then mutate `self.mean` and `self.variance`.
2. The variance update formula is the standard EWMA variance recursion (West 1979); implement it exactly as written and do not substitute a sample variance.
3. The zero-variance guard matters: ten identical values give `std = 0`, and without the guard the first change would divide by zero or be flagged as infinitely anomalous.
4. Warm-up compares `count` (values already seen) with `warmup` before the update, so with `warmup=5` the sixth value is the first one that can be flagged.
5. The slow-drift test passes because each step is tiny relative to the running std; if it fails, check that you update the variance with the pre-update `delta`.

### Solution explanation

The detector keeps two numbers per tenant, the EWMA of hourly spend and the EWMA of squared deviations, so it needs no history buffer and can run inside the request path or the Ops Console for every tenant at once. `alpha` sets memory: 0.3 means the last few hours dominate, which is why the detector adapts to a genuine step change within a dozen points (the test asserts that a sustained new level stops alerting), while `threshold` in standard deviations sets sensitivity. The warm-up guard stops the detector alerting on the first day of a new tenant, and the minimum-std guard handles the flat history that a brand-new deployment produces. The ops-tenant test encodes Incident 1 from Section 11 in miniature: ten stable hours around two dollars, then a cost spike pushes the hour to nine dollars fifty, and the detector flags exactly that point. The repo's `src/northwind/budget.py` has the same idea as `EWMAAnomalyDetector`, run per tenant next to the soft and hard caps (the Ops Console's Budgets page marks the anomalous bins). The shipped code does not count anomalies in Prometheus; the Grafana-side alert, `AtlasTenantCostAnomaly` in lecture 9.5, compares the last hour's spend with the previous day's average hour instead. Adding an anomaly counter is a capstone extension.

---

## CE4: Mask PII in Span Attributes

**Related lectures:** 4.6 Masking, sampling and cost of observability itself; 10.1 Your traces are a data breach waiting to happen; 10.2 Code-along: masking in the SDK and the collector  
**Learning objective:** Mask emails, employee IDs, phone numbers and Luhn-valid card numbers in strings and recursively in nested span attributes, keeping an optional stable hash so traces can still be joined per person.

### Instructions

Everything Atlas sends to Langfuse passes through a `mask` function first. Implement it in `pii.py`:

1. `short_hash(value)` returns the first 8 hex characters of the SHA-256 of the value after `.strip().lower()`.
2. `luhn_valid(number)` returns `True` when the digits in `number` (spaces and dashes ignored) pass the Luhn checksum; return `False` for fewer than 13 or more than 19 digits.
3. `mask_text(text, *, hash_ids=False)` replaces, in this order: cards, emails, employee IDs, phones.

| Tag | What to match |
|---|---|
| `<CARD>` | 13 to 19 digits with optional single spaces or dashes between digits, **only if** the digits pass Luhn |
| `<EMAIL>` | `name@example.com` including `+`, `.` and multi-part domains |
| `<EMPLOYEE_ID>` | `NW-` followed by exactly 5 digits, with word boundaries on both sides (`XNW-12345`, `NW-1234` and `NW-123456` are left alone) |
| `<PHONE>` | US numbers: `5125550161`, `512-555-0161`, `512.555.0161`, `(512) 555-0161`, `+1 512 555 0161`, `1-512-555-0161` |

   With `hash_ids=True`, emails and employee IDs become `<EMAIL:1a2b3c4d>` and `<EMPLOYEE_ID:1a2b3c4d>` using `short_hash` of the matched text. Ticket numbers such as `TCK-4471`, shipment IDs such as `SHP-88213`, times such as `14:30` and short numbers must be left exactly as they were.
4. `mask_attributes(data, *, hash_ids=False)` recursively masks every string inside dicts, lists and tuples, leaves dict keys, numbers, booleans and `None` untouched, does not mutate the input, and returns tuples as lists.

### Starter code (`pii.py`)

```python
"""Northwind Atlas: mask PII in span attributes before they leave the process (pure Python)."""
import hashlib
import re


def short_hash(value):
    """First 8 hex characters of the SHA-256 of the lowercased, stripped value."""
    # TODO
    raise NotImplementedError


def luhn_valid(number):
    """True when the digits in `number` (spaces and dashes ignored) pass the Luhn check.
    Return False for fewer than 13 or more than 19 digits."""
    # TODO
    raise NotImplementedError


def mask_text(text, *, hash_ids=False):
    """Replace PII in a string with tags, in this order: cards, emails, employee IDs, phones.

    <CARD>         13-19 digits with optional single spaces/dashes between digits,
                   ONLY when the digits pass the Luhn check
    <EMAIL>        name@example.com, including +, . and multi-part domains
    <EMPLOYEE_ID>  NW- followed by exactly 5 digits (word boundaries on both sides)
    <PHONE>        US numbers: 5551234567, 555-123-4567, 555.123.4567,
                   (555) 123-4567, +1 555 123 4567, 1-555-123-4567

    With hash_ids=True, emails and employee IDs become <EMAIL:1a2b3c4d> and
    <EMPLOYEE_ID:1a2b3c4d> using short_hash(matched_text), so traces can still be
    joined per person without storing the value. Everything else must be left unchanged
    (ticket numbers like TCK-4471, times like 14:30, short numbers, ordinary words).
    """
    # TODO
    raise NotImplementedError


def mask_attributes(data, *, hash_ids=False):
    """Recursively mask every string inside dicts, lists and tuples.

    Dict KEYS are left alone; numbers, booleans and None pass through unchanged.
    Return a new structure of the same shape (tuples come back as lists).
    """
    # TODO
    raise NotImplementedError
```

### Solution (`pii.py`)

```python
"""Northwind Atlas: mask PII in span attributes before they leave the process (pure Python)."""
import hashlib
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMPLOYEE_ID = re.compile(r"\bNW-\d{5}\b")
CARD_CANDIDATE = re.compile(r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)")
PHONE = re.compile(r"(?<![\w+])(?:\+?1[ .-]?)?(?:\(\d{3}\)|\d{3})[ .-]?\d{3}[ .-]?\d{4}(?!\w)")


def short_hash(value):
    """First 8 hex characters of the SHA-256 of the lowercased, stripped value."""
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()[:8]


def luhn_valid(number):
    """True when the digits in `number` (spaces and dashes ignored) pass the Luhn check.
    Return False for fewer than 13 or more than 19 digits."""
    digits = [int(ch) for ch in number if ch.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def mask_text(text, *, hash_ids=False):
    """Replace PII in a string with tags, in this order: cards, emails, employee IDs, phones.

    Tags: <CARD>, <EMAIL>, <EMPLOYEE_ID>, <PHONE> (the same format as the repo's `northwind.pii`).
    With hash_ids=True, emails and employee IDs become <EMAIL:1a2b3c4d> / <EMPLOYEE_ID:...>
    using short_hash, so traces can still be joined per person without storing the value.
    Cards are only masked when they pass the Luhn check. Everything else is left unchanged.
    """
    def card(match):
        return "<CARD>" if luhn_valid(match.group(0)) else match.group(0)

    def email(match):
        return f"<EMAIL:{short_hash(match.group(0))}>" if hash_ids else "<EMAIL>"

    def employee(match):
        return f"<EMPLOYEE_ID:{short_hash(match.group(0))}>" if hash_ids else "<EMPLOYEE_ID>"

    text = CARD_CANDIDATE.sub(card, text)
    text = EMAIL.sub(email, text)
    text = EMPLOYEE_ID.sub(employee, text)
    text = PHONE.sub("<PHONE>", text)
    return text


def mask_attributes(data, *, hash_ids=False):
    """Recursively mask every string inside dicts, lists and tuples.

    Dict KEYS are left alone; numbers, booleans and None pass through unchanged.
    Return a new structure of the same shape (tuples come back as lists).
    """
    if isinstance(data, str):
        return mask_text(data, hash_ids=hash_ids)
    if isinstance(data, dict):
        return {key: mask_attributes(value, hash_ids=hash_ids) for key, value in data.items()}
    if isinstance(data, (list, tuple)):
        return [mask_attributes(item, hash_ids=hash_ids) for item in data]
    return data
```

### Tests (evaluation file `test_pii.py`)

```python
import hashlib
import unittest

from pii import luhn_valid, mask_attributes, mask_text, short_hash


class Evaluate(unittest.TestCase):
    def test_luhn(self):
        self.assertTrue(luhn_valid("4532 0151 1283 0366"))
        self.assertTrue(luhn_valid("4111-1111-1111-1111"))
        self.assertFalse(luhn_valid("4532015112830367"))
        self.assertFalse(luhn_valid("1234"))
        self.assertFalse(luhn_valid("1" * 20))

    def test_email(self):
        self.assertEqual(
            mask_text("Contact priya.nair+hr@northwind-logistics.co.uk for payroll"),
            "Contact <EMAIL> for payroll",
        )

    def test_employee_id(self):
        self.assertEqual(mask_text("Reset password for NW-10433 please"),
                         "Reset password for <EMPLOYEE_ID> please")
        # not an employee id: too short, or glued to other characters
        self.assertEqual(mask_text("NW-1234 and XNW-12345 and NW-123456"), "NW-1234 and XNW-12345 and NW-123456")

    def test_phone_formats(self):
        for phone in ["5125550161", "512-555-0161", "512.555.0161",
                      "(512) 555-0161", "+1 512 555 0161", "1-512-555-0161"]:
            self.assertEqual(mask_text(f"call me on {phone} tomorrow"),
                             "call me on <PHONE> tomorrow", phone)

    def test_card_only_when_luhn_valid(self):
        self.assertEqual(mask_text("card 4532 0151 1283 0366 was charged"),
                         "card <CARD> was charged")
        self.assertEqual(mask_text("ref 4532 0151 1283 0367"), "ref 4532 0151 1283 0367")

    def test_leaves_operational_data_alone(self):
        text = "Ticket TCK-4471 opened at 14:30, shipment SHP-88213, 3 pallets, VPN error 809"
        self.assertEqual(mask_text(text), text)

    def test_hash_ids_is_stable_and_short(self):
        masked = mask_text("NW-10433 wrote from j.doe@northwind.com", hash_ids=True)
        emp_hash = short_hash("NW-10433")
        email_hash = short_hash("j.doe@northwind.com")
        self.assertEqual(masked, f"<EMPLOYEE_ID:{emp_hash}> wrote from <EMAIL:{email_hash}>")
        self.assertEqual(len(emp_hash), 8)
        self.assertEqual(short_hash("  J.Doe@Northwind.com "), email_hash)
        self.assertEqual(short_hash("abc"), hashlib.sha256(b"abc").hexdigest()[:8])

    def test_mask_attributes_recurses(self):
        span = {
            "gen_ai.tool.name": "reset_password",
            "gen_ai.tool.call.arguments": {"employee_id": "NW-10433", "phone": "512-555-0161"},
            "gen_ai.tool.call.result": ["sent to j.doe@northwind.com", 200, True, None],
            "gen_ai.usage.input_tokens": 1200,
            "nested": ("NW-50001",),
        }
        masked = mask_attributes(span)
        self.assertEqual(masked["gen_ai.tool.name"], "reset_password")
        self.assertEqual(masked["gen_ai.tool.call.arguments"],
                         {"employee_id": "<EMPLOYEE_ID>", "phone": "<PHONE>"})
        self.assertEqual(masked["gen_ai.tool.call.result"], ["sent to <EMAIL>", 200, True, None])
        self.assertEqual(masked["gen_ai.usage.input_tokens"], 1200)
        self.assertEqual(masked["nested"], ["<EMPLOYEE_ID>"])
        # original is untouched
        self.assertEqual(span["gen_ai.tool.call.arguments"]["employee_id"], "NW-10433")

    def test_mask_attributes_passthrough(self):
        self.assertEqual(mask_attributes(42), 42)
        self.assertEqual(mask_attributes(None), None)
        self.assertEqual(mask_attributes("NW-10433"), "<EMPLOYEE_ID>")
```

### Hints

1. Compile the four patterns once at module level; `re.sub` accepts a function as the replacement, which is how you apply the Luhn check per match.
2. Mask cards before phones: a 16-digit card number contains something that looks like a phone number.
3. `(?<!\d)` and `(?!\d)` around the card pattern stop you matching a 13-digit slice out of a longer digit run.
4. For `hash_ids`, hash the matched text (`match.group(0)`), not the whole string.
5. `mask_attributes` is a four-way `isinstance` dispatch: `str`, `dict`, `list`/`tuple`, everything else returned as is.

### Solution explanation

The masking runs client-side, before the Langfuse SDK serialises the span, which is the only place that guarantees raw values never leave the process; the OTel collector's `attributes/redact` processor in lecture 10.2 is defence in depth, not the primary control. The order of substitutions matters because the patterns overlap: card numbers are checked first with a Luhn filter so that a shipment reference or a run of digits in a log line does not disappear, then emails, then the Northwind employee-ID format (`NW-` plus five digits; ticket `TCK-` and shipment `SHP-` ids are deliberately different prefixes so they survive), and finally phones. The `hash_ids` option is the governance compromise from lecture 10.2: the analyst can still count "how many sessions did this employee have" or join a Langfuse trace to a ticket by hashed ID, but nobody can read the identity out of the trace. The recursive `mask_attributes` matches the shape Langfuse hands to `mask=`: nested input, output and metadata dicts. The repo's `src/northwind/pii.py` has the same shape and signatures (`mask_text(text, *, hash_ids=False, salt=...)`, `mask_value(value, *, hash_ids=False, salt=...)`, and `langfuse_mask(*, data)` for `Langfuse(mask=...)`), with one production difference: its `short_hash` is an HMAC-SHA256 keyed with `ATLAS_PII_HASH_KEY`, so nobody without the key can hash a list of employee IDs and match them. The plain SHA-256 here is fine for the exercise and not for production.

---

## CE5: Trim the Context to a Token Budget

**Related lectures:** 6.1 Where the money goes: token anatomy; 6.5 The context diet; 11.2 Incident 1: Monday's cost spike  
**Learning objective:** Estimate tokens without a tokenizer, truncate oversized tool results, and drop the oldest history until a conversation fits a token budget while keeping the system prompt and the latest message.

### Instructions

Incident 1 happened because every step of a long conversation re-sent the entire history, including 5 KB tool results, so tokens per step grew without bound. The context diet from lecture 6.5 fixes that with two pure functions. Implement them in `context.py`. A message is a dict with `role` and `content` keys; `content` may be missing, in which case treat it as `""`.

1. `estimate_tokens(text)`: one token per 4 characters, rounded up; `0` for an empty string, at least `1` otherwise.
2. `message_tokens(message)`: `estimate_tokens(content) + TOKENS_PER_MESSAGE_OVERHEAD` (the constant is 4).
3. `total_tokens(messages)`: sum over the list.
4. `truncate_tool_results(messages, max_chars)`: return a **new** list where every message with `role == "tool"` whose content is longer than `max_chars` is cut to `max_chars` characters followed by `TRUNCATION_MARKER`. Other messages are copied unchanged. Raise `ValueError` if `max_chars < 1`.
5. `trim_to_budget(messages, budget)`: drop the **oldest** non-system messages until `total_tokens(result) <= budget`. System messages are always kept in their original position, order is preserved, and the most recent message is always kept even if it alone exceeds the budget. Raise `ValueError` if `budget < 1`. Return `(trimmed_messages, dropped_count)`.

Example: five messages of 14 tokens each (70 total) trimmed to a budget of 45 drops the two oldest non-system messages and returns the system message plus the last two.

### Starter code (`context.py`)

```python
"""Northwind Atlas: trim a conversation to a token budget (pure Python)."""

TOKENS_PER_MESSAGE_OVERHEAD = 4
TRUNCATION_MARKER = " ...[truncated]"


def estimate_tokens(text):
    """Approximate token count: one token per 4 characters, rounded up, minimum 1 for
    non-empty text, 0 for an empty string."""
    # TODO
    raise NotImplementedError


def message_tokens(message):
    """Tokens for one message: estimate_tokens(content) + TOKENS_PER_MESSAGE_OVERHEAD.
    A message is a dict with "role" and "content" keys (content may be missing -> "")."""
    # TODO
    raise NotImplementedError


def total_tokens(messages):
    """Sum of message_tokens over the list."""
    # TODO
    raise NotImplementedError


def truncate_tool_results(messages, max_chars):
    """Return a new list where every message with role == "tool" whose content is longer
    than max_chars is cut to max_chars characters followed by TRUNCATION_MARKER.
    Other messages are copied unchanged (do not mutate the input).
    Raise ValueError if max_chars < 1."""
    # TODO
    raise NotImplementedError


def trim_to_budget(messages, budget):
    """Drop the OLDEST non-system messages until total_tokens(result) <= budget.

    - System messages (role == "system") are always kept, in their original position.
    - Order of the remaining messages is preserved.
    - The most recent message is always kept, even if that alone exceeds the budget.
    - Raise ValueError if budget < 1.
    Return (trimmed_messages, dropped_count).
    """
    # TODO
    raise NotImplementedError
```

### Solution (`context.py`)

```python
"""Northwind Atlas: trim a conversation to a token budget (pure Python)."""

TOKENS_PER_MESSAGE_OVERHEAD = 4
TRUNCATION_MARKER = " ...[truncated]"


def estimate_tokens(text):
    """Approximate token count: one token per 4 characters, rounded up, minimum 1 for
    non-empty text, 0 for an empty string."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def message_tokens(message):
    """Tokens for one message: estimate_tokens(content) + TOKENS_PER_MESSAGE_OVERHEAD."""
    return estimate_tokens(message.get("content", "")) + TOKENS_PER_MESSAGE_OVERHEAD


def total_tokens(messages):
    """Sum of message_tokens over the list."""
    return sum(message_tokens(m) for m in messages)


def truncate_tool_results(messages, max_chars):
    """Return a new list where every message with role == "tool" whose content is longer
    than max_chars is cut to max_chars characters followed by TRUNCATION_MARKER.
    Other messages are copied unchanged. Raise ValueError if max_chars < 1."""
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1")
    result = []
    for message in messages:
        content = message.get("content", "")
        if message.get("role") == "tool" and len(content) > max_chars:
            message = {**message, "content": content[:max_chars] + TRUNCATION_MARKER}
        else:
            message = dict(message)
        result.append(message)
    return result


def trim_to_budget(messages, budget):
    """Drop the OLDEST non-system messages until total_tokens(result) <= budget.

    - System messages (role == "system") are always kept, in their original position.
    - Order of the remaining messages is preserved.
    - The most recent message is always kept, even if that alone exceeds the budget.
    - Raise ValueError if budget < 1.
    Return (trimmed_messages, dropped_count).
    """
    if budget < 1:
        raise ValueError("budget must be at least 1")
    kept = list(messages)
    dropped = 0
    while total_tokens(kept) > budget:
        candidates = [i for i, m in enumerate(kept) if m.get("role") != "system"]
        # never drop the most recent message
        if len(candidates) <= 1:
            break
        del kept[candidates[0]]
        dropped += 1
    return kept, dropped
```

### Tests (evaluation file `test_context.py`)

```python
import unittest

from context import (TRUNCATION_MARKER, estimate_tokens, message_tokens, total_tokens,
                     trim_to_budget, truncate_tool_results)


def msg(role, content):
    return {"role": role, "content": content}


class Evaluate(unittest.TestCase):
    def test_estimate_tokens(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertEqual(estimate_tokens("a"), 1)
        self.assertEqual(estimate_tokens("abcd"), 1)
        self.assertEqual(estimate_tokens("abcde"), 2)
        self.assertEqual(estimate_tokens("x" * 400), 100)

    def test_message_tokens_includes_overhead(self):
        self.assertEqual(message_tokens(msg("user", "x" * 40)), 14)
        self.assertEqual(message_tokens({"role": "assistant"}), 4)

    def test_total_tokens(self):
        history = [msg("system", "x" * 80), msg("user", "x" * 40), msg("assistant", "x" * 20)]
        self.assertEqual(total_tokens(history), 24 + 14 + 9)

    def test_truncate_tool_results(self):
        history = [msg("user", "where is shipment NW-88213?"),
                   msg("tool", "{" + "a" * 5000 + "}"),
                   msg("assistant", "It left the depot.")]
        trimmed = truncate_tool_results(history, 200)
        self.assertEqual(trimmed[0], history[0])
        self.assertEqual(trimmed[2], history[2])
        self.assertEqual(len(trimmed[1]["content"]), 200 + len(TRUNCATION_MARKER))
        self.assertTrue(trimmed[1]["content"].endswith(TRUNCATION_MARKER))
        # input not mutated, short tool results untouched
        self.assertEqual(len(history[1]["content"]), 5002)
        short = [msg("tool", "ok")]
        self.assertEqual(truncate_tool_results(short, 200), short)

    def test_truncate_rejects_bad_max(self):
        with self.assertRaises(ValueError):
            truncate_tool_results([], 0)

    def test_trim_drops_oldest_first(self):
        history = [msg("system", "s" * 40),          # 14
                   msg("user", "u1" * 20),            # 14
                   msg("assistant", "a1" * 20),       # 14
                   msg("user", "u2" * 20),            # 14
                   msg("assistant", "a2" * 20)]       # 14 -> total 70
        trimmed, dropped = trim_to_budget(history, 45)
        self.assertEqual(dropped, 2)
        self.assertEqual([m["content"] for m in trimmed], ["s" * 40, "u2" * 20, "a2" * 20])
        self.assertLessEqual(total_tokens(trimmed), 45)

    def test_trim_keeps_system_wherever_it_is(self):
        history = [msg("user", "u1" * 20), msg("system", "s" * 40), msg("user", "u2" * 20)]
        trimmed, dropped = trim_to_budget(history, 30)
        self.assertEqual(dropped, 1)
        self.assertEqual([m["role"] for m in trimmed], ["system", "user"])
        self.assertEqual(trimmed[1]["content"], "u2" * 20)

    def test_trim_nothing_when_within_budget(self):
        history = [msg("system", "hi"), msg("user", "hello")]
        trimmed, dropped = trim_to_budget(history, 1000)
        self.assertEqual(dropped, 0)
        self.assertEqual(trimmed, history)

    def test_trim_always_keeps_latest_message(self):
        history = [msg("system", "s" * 40), msg("user", "x" * 4000)]
        trimmed, dropped = trim_to_budget(history, 50)
        self.assertEqual(dropped, 0)
        self.assertEqual(len(trimmed), 2)

    def test_trim_rejects_bad_budget(self):
        with self.assertRaises(ValueError):
            trim_to_budget([msg("user", "hi")], 0)

    def test_diet_pipeline_reduces_tokens(self):
        # The context diet from lecture 6.5: truncate tool results, then trim history
        history = [msg("system", "You are Atlas." * 10)]
        for i in range(6):
            history.append(msg("user", f"question {i} " * 10))
            history.append(msg("tool", "{" + "r" * 3000 + "}"))
            history.append(msg("assistant", f"answer {i} " * 10))
        before = total_tokens(history)
        dieted, dropped = trim_to_budget(truncate_tool_results(history, 300), 800)
        after = total_tokens(dieted)
        self.assertLess(after, before)
        self.assertLessEqual(after, 800)
        self.assertGreater(dropped, 0)
        self.assertEqual(dieted[0]["role"], "system")
        self.assertEqual(dieted[-1]["content"], "answer 5 " * 10)
```

### Hints

1. `(len(text) + 3) // 4` is integer ceiling division by 4.
2. Build new dicts with `{**message, "content": ...}` so the caller's list is not mutated; the test checks this.
3. In `trim_to_budget`, recompute the list of droppable indexes on every loop iteration; the first one is the oldest non-system message.
4. Stop when only one droppable message is left: that is the latest message and it must survive.
5. Run `truncate_tool_results` before `trim_to_budget`, as the pipeline test does; shrinking tool results first means you drop fewer turns of real conversation.

### Solution explanation

The 4-characters-per-token estimate is deliberately crude: it runs in microseconds with no network, no model file and no dependency, which is what a hot path in an agent loop needs, and it is within about 20 percent of the real count for English prose (the repo's `tokens.py` upgrades to `tiktoken` only when the encoding is already cached on disk). The two operations are ordered on purpose. Truncating tool results attacks the biggest single contributor to context bloat in Incident 1, the raw JSON that `lookup_ticket` and `check_shipment` return, without losing any conversational turns; only then does history trimming remove the oldest exchanges. Keeping the system prompt in place also keeps the cached prefix stable, which is why the diet and prompt caching from lecture 6.4 compound rather than fight. The pipeline test reproduces the lecture's before-and-after measurement: six turns with 3 KB tool results shrink from thousands of estimated tokens to under 800 while the system prompt and the latest answer survive. In the repo, `src/northwind/tokens.py` exposes the same functions and `app/agent.py` calls them at the top of every step, recording `tokens_dropped` as a span attribute so the saving is visible in Langfuse.

---

## Appendix: Verification script

Place files as `exN/solution/<module>.py`, `exN/starter/<module>.py` and `exN/test_<module>.py` (N = 1 to 5), then run this script. Solutions must print `OK`; starters must print `FAILED` without import errors.

```bash
#!/bin/bash
# Run each exercise's tests against the solution (must pass) and the starter (must import cleanly and fail).
cd "$(dirname "$0")"
status=0
for ex in ex1:pricing ex2:latency ex3:anomaly ex4:pii ex5:context; do
  d=${ex%%:*}; m=${ex##*:}
  for kind in solution starter; do
    cp $d/test_$m.py $d/$kind/
    out=$(cd $d/$kind && python3 -m unittest test_$m 2>&1 | tail -3 | tr '\n' ' ')
    echo "$d $m [$kind]: $out"
    if [ $kind = solution ] && ! echo "$out" | grep -q "OK"; then status=1; fi
  done
done
exit $status
```

Last verified run (Python 3.11, 2026-10-04):

```text
ex1 pricing [solution]: Ran 12 tests in 0.001s OK
ex1 pricing [starter]: Ran 12 tests in 0.002s FAILED (errors=11)
ex2 latency [solution]: Ran 12 tests in 0.001s OK
ex2 latency [starter]: Ran 12 tests in 0.001s FAILED (errors=12)
ex3 anomaly [solution]: Ran 10 tests in 0.000s OK
ex3 anomaly [starter]: Ran 10 tests in 0.001s FAILED (errors=10)
ex4 pii [solution]: Ran 9 tests in 0.000s OK
ex4 pii [starter]: Ran 9 tests in 0.001s FAILED (errors=9)
ex5 context [solution]: Ran 11 tests in 0.001s OK
ex5 context [starter]: Ran 11 tests in 0.002s FAILED (errors=11)
```
