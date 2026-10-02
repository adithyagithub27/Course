# Section 6: Cost Engineering (signature section)

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 70 minutes (10 lectures, including one challenge, one project intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics, with four departments as tenants (`ops`, `finance`, `hr`, `eng`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Terminal font at 18 pt minimum. Every dollar figure on screen gets a callout.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on litellm 1.103 / langfuse 4.15 / openai 2.54. Prices as of 2026-09-28: verify current pricing."
> **Recording note (from the curriculum):** split 6.3 and 6.6 into Part A / Part B uploads to keep each video under ten minutes.
> **Numbers note:** every figure in this section comes from `agent-observability-course/01-curriculum/numbers-card.md` (one replayed day, `OFFLINE=1 make replay`, seed 7, 4,000 sessions, fixture day 2026-09-14). Record the [DEMO] output from your own run; it is deterministic and must match the blocks below.

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (match `03-code/`):** `northwind.pricing` (`FALLBACK_PRICES`, `ModelPrice`, `get_price`, `estimate_cost` → `CostBreakdown`, `cost_usd`), `northwind.cost` (`CostRecord`, `Rollup`, `rollup`, `cost_per_session`, `showback_table`), `northwind.report` (`weekly_report`; `make report`), `northwind.tokens` (`estimate_tokens`, `truncate_tool_result`, `trim_history`, `context_diet`), `northwind.budget` (`TenantBudget`, `BudgetGuard.decide` → `BudgetDecision`, `Decision`, `EWMAAnomalyDetector`, `hourly_anomalies`; `EwmaAnomaly` is an alias), `app.agent.AtlasAgent` (`_cache_key`, `_choose_deployment`, `build_router_config`, `RouterClient`; `ATLAS_ROUTER_MODE=1` switches router mode on), `app.prompts.prompt_cache_key`, `telemetry.metrics` (`COST`, `TOKENS`, `BUDGET_DECISIONS`, `BUDGET_SPENT`; `LLM_COST` and `BUDGET_EVENTS` are aliases), `simulator/replay.py`, the Ops Console (`make console`: pages Cost, Budgets, Compare replays). Makefile flags: `make replay CACHE=1 DIET=1 ROUTER=1 STORE=...`; each lever defaults to `0`, so plain `make replay` is the baseline.

**The numbers card for this section (a subset of `01-curriculum/numbers-card.md`; every lecture reconciles to it):**

| Item | Value |
|---|---|
| Traffic on the replayed day | 10,184 requests in 4,000 sessions; 20,130 generations (20,087 on gpt-4.1-mini, 43 on gpt-4.1) |
| One baseline request (the demo request in 6.4 and 6.5, gpt-4.1-mini) | steps of 3,259 / 6,667 input tokens = 9,926 input; 42 + 282 = 324 output |
| Cost of that request | 9,926 × $0.40/M + 324 × $1.60/M = $0.003970 + $0.000518 = **$0.00449**; input is 88% |
| Escalations | 43 requests (0.4%) escalate to gpt-4.1; the `escalation` feature costs **$0.38** of the day. No retries on the baseline day (retry storms are an incident scenario: 7.3, 11.2) |
| **Baseline day** | **$56.28**: $0.0055 per request, $0.0141 per session, $0.0144 per resolved session; about $1,700 a month, about $20,500 a year |
| Caching alone (`CACHE=1`; 49.3% of the day's input tokens served from cache) | **$37.00** (−34.3%) |
| Context diet alone (`DIET=1`) | **$41.99** (−25.4%) |
| Routing alone (`ROUTER=1`; 6,700 of 20,087 mini calls move to gpt-4.1-nano) | **$47.07** (−16.4%) |
| Caching + diet | **$22.71** (−59.6%) |
| All three | **$19.07** (−66.1%), $0.0048 per session, about $570 a month |
| Quality on the replay (every row) | judge `resolved` 0.892, `grounded` 0.943. The offline judge scores answer text, and the mock's answers do not change with the cost flags, so the scores are identical by construction; on a real model this row is the one you have to earn |
| Prices used (verify current pricing) | gpt-4.1-mini $0.40 in / $1.60 out / $0.10 cached per 1M; gpt-4.1 $2.00 / $8.00 / $0.50; gpt-4.1-nano $0.10 / $0.40 / $0.025 |

---

## Lecture 6.1: Where the money goes: token anatomy

| Field | Value |
|---|---|
| ID | 6.1 |
| Title | Where the money goes: token anatomy |
| Type | SL (slides + avatar, with one terminal beat) |
| Target duration | 7:00 (about 850 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | An agent's bill is made of six token streams, and the biggest one is the input you re-send on every step. |
| Prerequisites | Sections 2 to 5 (you can read a trace with usage on it) |
| Files used | Diagram D5 "token anatomy of one Atlas request"; `app/agent.py` (`AgentResult.generations`) |

**Learning objectives**

1. Name the six token streams that make up an agent's cost: uncached input, cached input, output, reasoning, retries and judge calls.
2. Read the OpenAI usage fields that report each stream (`prompt_tokens_details.cached_tokens`, `completion_tokens_details.reasoning_tokens`, and their Responses API equivalents).
3. Explain why a two-step agent pays for its prompt twice, and estimate the share of cost that is input.

### Script

[SCREEN: terminal, dark theme. One Atlas request, run offline, prints one line per model call.]

```bash
OFFLINE=1 OTEL_EXPORTER=none ATLAS_PROMPT_CACHE=0 ATLAS_CONTEXT_DIET=0 uv run python -c "
from app.agent import AtlasAgent
r = AtlasAgent().run('How do I reset my VPN token?', tenant='ops', user_id='NW-40213', session_id='demo')
for g in r.generations:
    print(f'step {g.step}  {g.model}  prompt={g.input_tokens}  completion={g.output_tokens}  cost=\${g.cost_usd:.6f}')
print(f'request  input={r.input_tokens}  output={r.output_tokens}  cost=\${r.cost_usd:.5f}')
"
```

[DEMO: output:]

```
step 1  gpt-4.1-mini  prompt=3259  completion=42  cost=$0.001371
step 2  gpt-4.1-mini  prompt=6667  completion=282  cost=$0.003118
request  input=9926  output=324  cost=$0.00449
```

[AVATAR]

One question. One answer. Two model calls. [PAUSE] Look at the prompt column: three thousand two hundred, then six thousand six hundred. The user typed about thirty tokens. Atlas sent the model almost ten thousand. That's the shape of every agent bill I have ever seen, and by the end of this lecture you'll be able to read it like a receipt.

[SLIDE 1: The six token streams]
- Uncached input: what you send, at full price
- Cached input: the same prefix, seen recently, at a discount
- Output: what the model writes, including tool-call arguments
- Reasoning: hidden thinking on reasoning models, billed as output
- Retries: the same step, paid again
- Judge calls: the model you pay to grade the model

[AVATAR]

Six streams. The first three are on every invoice. Uncached input is what you send at full price. Cached input is a prefix the provider has seen in the last few minutes, billed at a quarter of the price. Output is everything the model writes, and that includes the JSON arguments of a tool call. Then three streams people forget. Reasoning tokens, which reasoning models spend thinking and bill as output. Retries, where you pay for the same step twice. And judge calls, which we'll add in Section 8, where you pay a second model to grade the first one.

Here's the question for the whole section. [PAUSE] Which stream is biggest for Atlas? Let's find out with the numbers you just saw.

[SLIDE 2: One Atlas request, step by step (baseline)]

Diagram: D5 build 1, token anatomy of one request.

| Step | What is in the prompt | Input tokens | Output tokens |
|---|---|---|---|
| 1 | system prompt + 5 tool schemas (about 3,200), question (about 30) | 3,259 | 42 (tool call) |
| 2 | step 1 again + tool call + `search_knowledge_base` result, 4 passages (about 3,400) | 6,667 | 282 (answer) |
| Total | | **9,926** | **324** |

[AVATAR]

Step one. Atlas sends the system prompt and the five tool schemas. That prefix is about thirty-two hundred tokens. Plus the thirty-token question. Three thousand two hundred fifty-nine in. The model answers with a forty-two-token tool call.

Step two. Here's the part that surprises people. The model has no memory. So Atlas sends everything from step one again, plus the tool call, plus the thirty-four-hundred-token knowledge base result, four passages at the default top-k. Six thousand six hundred sixty-seven in, and finally a two-hundred-eighty-two-token answer for the user.

Add it up. Nine thousand nine hundred twenty-six input tokens. Three hundred twenty-four output. [PAUSE] The prefix alone was sent twice, and in a multi-turn session it goes again on every follow-up, with the passages riding along: thousands of tokens for thirty tokens of actual question.

[SLIDE 3: What that costs (gpt-4.1-mini, verify current pricing)]
- Input: 9,926 × $0.40 per million = $0.003970
- Output: 324 × $1.60 per million = $0.000518
- Total: $0.00449 per request (step 1 $0.001371, step 2 $0.003118)
- Input is 88% of the cost

[AVATAR]

Now the money. At forty cents per million input tokens, the input costs four tenths of a cent. Output is four times the price per token, but there's thirty times less of it, so it's a twentieth of a cent. Total: just under half a cent per request. And eighty-eight percent of it is input.

That's the answer to the question. For a tool-calling agent, the bill is input. Not the clever answer at the end. The re-sent context in the middle. Which is why the three levers in this section, caching, the context diet and routing, all attack input first.

[SLIDE 4: The full day (baseline, `make replay`, seed 7)]
- 10,184 requests, 4,000 sessions, 20,130 generations: $56.28
- Escalations: 43 requests (0.4%) move to gpt-4.1, five times the price per token: $0.38
- Retries: none on a normal day; a retry storm re-bills the whole prompt (7.3, Incident 1)
- Day: $56.28 · Request: $0.0055 · Session: $0.0141 · Month: about $1,700 · Year: about $20,500

[AVATAR]

Scale it to Atlas's replayed day. Ten thousand requests in four thousand sessions, fifty-six dollars twenty-eight. Almost all of it is gpt-4.1-mini input. The forgotten streams are small today, and that is the point: forty-three requests escalated to gpt-4.1, thirty-eight cents, five times the price per token for less than half a percent of the traffic. And no retries, because nothing failed. On the day a tool or a provider does fail, every retry re-sends the whole prompt and bills it again; that is Incident 1 in Section 11.

[B-ROLL: Ops Console, Cost page, "Cost per hour by tenant" for the replayed day: two daytime peaks, the 09:00 bar at $6.02 called out, the 02:00 bar at $0.06]

Fifty-six dollars twenty-eight a day. About a cent and a half per session. About seventeen hundred a month. [PAUSE] Not scary yet. The scary number in Section 1 was a loop: five dollars for one conversation, about forty-nine hundred for a weekend of them. This is the normal day, and normal days are where the savings live, because you can plan them.

[SLIDE 5: Where usage comes from (OpenAI, verified on openai 2.54)]
- Chat Completions: `usage.prompt_tokens`, `usage.completion_tokens`, `usage.prompt_tokens_details.cached_tokens`, `usage.completion_tokens_details.reasoning_tokens`
- Responses API: `usage.input_tokens`, `usage.output_tokens`, `usage.input_tokens_details.cached_tokens`, `usage.output_tokens_details.reasoning_tokens`
- `cached_tokens` is a subset of the input count, not an extra
- `reasoning_tokens` is a subset of the output count, billed as output

[AVATAR]

Where do the numbers come from? Every response carries a usage object. On Chat Completions it's `prompt_tokens` and `completion_tokens`, with a details object underneath. On the Responses API it's `input_tokens` and `output_tokens`. Two traps. `cached_tokens` is part of the input count, not on top of it, so cost is uncached times full price plus cached times the discount. And `reasoning_tokens` is part of the output count, billed at the output price. If you build a price function that forgets either rule, your showback report is wrong, and finance will find out before you do.

[SLIDE 6: What this section builds]
- 6.2 a price table you can trust
- 6.3 cost per request, session, user, tenant and feature
- 6.4 caching, 6.5 the context diet, 6.6 routing
- 6.7 budgets and anomaly alerts
- 6.8 challenge: cut the day by 40%

[AVATAR]

So here's the plan. First a price table you can trust, then attribution, so every one of those fifty-six dollars has a tenant and a feature on it. Then the three levers, each measured on the same day of traffic. Then budgets so it can't run away. And in 6.8 you'll take the fifty-six dollar day and cut it by forty percent yourself, before I show you my version. [PAUSE] Keep the number in your head: fifty-six twenty-eight.

[SLIDE 7: Recap]
- Six token streams make up the bill
- Every step re-sends the whole prompt
- For Atlas, input is 88% of cost

### Recap

An agent's bill is six token streams, and for a tool-calling agent about nine tenths of it is input, because every step re-sends the whole prompt.

### Transition

Next, the price table. If the prices are wrong, every number after this is wrong, so we'll pin them and test them.

### Speaker notes: common mistakes and Q&A

- **"Isn't output the expensive part?"** Per token, yes, four times. Per request, no: Atlas sends thirty times more input than output. Always look at the product, price times volume.
- **Double-counting cached tokens.** `cached_tokens` is inside `prompt_tokens`. Students who add them get a bill that is too high, and then "save" money by fixing the bug.
- **Reasoning tokens.** gpt-4.1-mini reports zero. If a student swaps in a reasoning model such as `gpt-5-mini`, the output count jumps and they need to know why.
- **Tool-call overhead.** Tool schemas are input tokens on every step. The system prompt plus five tool schemas is about 3,200 tokens per step here; fifty tools would be a bill of their own.
- **The terminal beat.** `OTEL_EXPORTER=none` keeps the console exporter from printing span JSON after the three lines. The run is deterministic; if your numbers differ, the cost flags in your shell are not `0`.
- **Prices move.** Say it on camera: verify current pricing. The math is the lesson; the constants are the moment.

---

## Lecture 6.2: Code-along: a price table you can trust

| Field | Value |
|---|---|
| ID | 6.2 |
| Title | Code-along: a price table you can trust |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 770 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Take prices from `litellm.model_cost`, pin a fallback table with a date, and put the per-token math in one tested function. |
| Prerequisites | 6.1; `uv sync` done |
| Files used | `src/northwind/pricing.py`, `tests/unit/test_pricing.py` |

**Learning objectives**

1. Read a model's prices from `litellm.model_cost` and know which keys matter: `input_cost_per_token`, `output_cost_per_token`, `cache_read_input_token_cost`.
2. Read `estimate_cost(model, input_tokens, output_tokens, cached_tokens=, reasoning_tokens=)`, and its float wrapper `cost_usd`, with correct handling of cached and reasoning tokens.
3. Pin a dated fallback table and a unit test so a price change or a missing model fails loudly instead of silently.

### Script

[AVATAR]

Here's a bug I found in a real showback report. The team hard-coded gpt-4o prices in March. In July they switched to a mini model, four times cheaper. The report kept multiplying by the old constants. For three months, finance believed the AI helpdesk cost four times what it did. [PAUSE] Nobody lied. The price table just lived in the wrong place. Let's put ours in the right place.

[SLIDE 1: Three sources of truth for prices]
- `litellm.model_cost`: a maintained JSON of hundreds of models, per-token prices
- Your pinned fallback: dated, tested, for offline mode and unknown models
- Your overrides: negotiated rates, private deployments
- Rule: one function computes cost; nothing else does arithmetic on tokens

[AVATAR]

Three sources, one function. LiteLLM ships a price table for hundreds of models, updated with the library. We read from it first. Behind it sits our own fallback: a small dictionary with a date in a comment, so offline mode and tests never depend on the network or on a library upgrade. And there's room for overrides, for negotiated rates. Everything funnels into one function, `estimate_cost`. Nothing else in the repo multiplies tokens by prices. That's the rule that would have saved that team.

[SCREEN: terminal]

Let's look at what LiteLLM knows.

```bash
uv run python -c "import litellm; c=litellm.model_cost['gpt-4.1-mini']; print({k:c[k] for k in ('input_cost_per_token','output_cost_per_token','cache_read_input_token_cost')})"
```

[DEMO: prints `{'input_cost_per_token': 4e-07, 'output_cost_per_token': 1.6e-06, 'cache_read_input_token_cost': 1e-07}`]

Four times ten to the minus seven per input token. That's forty cents per million. One point six per million out. Ten cents per million cached. Note the key name: `cache_read_input_token_cost`. Now the module.

[SCREEN: VS Code, `src/northwind/pricing.py`]

[CODE: `src/northwind/pricing.py` (excerpt)]

```python
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

    # output_per_token and cached_input_per_token follow the same pattern


#: Pinned fallback prices, USD per 1M tokens (input, output, cached input).
FALLBACK_PRICES: dict[str, ModelPrice] = {
    "gpt-4.1": _p("gpt-4.1", "2.00", "8.00", "0.50"),
    "gpt-4.1-mini": _p("gpt-4.1-mini", "0.40", "1.60", "0.10"),
    "gpt-4.1-nano": _p("gpt-4.1-nano", "0.10", "0.40", "0.025"),
    "gpt-5-mini": _p("gpt-5-mini", "0.25", "2.00", "0.025"),
    "gpt-4o-mini": _p("gpt-4o-mini", "0.15", "0.60", "0.075"),
}


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
```

Walk through it. `FALLBACK_PRICES` is per million, because that's how price pages read, with the date and the warning in the module docstring. `ModelPrice` exposes per-token properties, because that's how you multiply. `get_price` asks LiteLLM first when you pass `use_litellm=True`, which production does and the unit tests don't, because importing LiteLLM takes seconds; then it falls back to the pinned table.

[SCREEN: zoom on `get_price`; the `raise UnknownModelError(name) from exc` line gets a red callout]

[PAUSE] Notice what it does not do: it does not return zero for an unknown model. `UnknownModelError`, a `KeyError`, is the right behavior. A silent zero is how a new model runs for a month at no apparent cost.

[SCREEN: zoom on `estimate_cost`; the three lines `input_usd`, `cached_usd`, `output_usd` highlighted in turn]

`estimate_cost` is the whole lesson from last lecture, in `Decimal` so that ten thousand records sum the same way every time. Uncached input at full price. Cached input at the discount. Output at the output price. `reasoning_tokens` is a parameter so the call site is honest about it, and the breakdown reports it, but it adds nothing to the total, because it's already inside `output_tokens`. `cost_usd` is the float wrapper for when you just want the number.

[SCREEN: terminal]

Let's check it against the numbers from 6.1, and against LiteLLM's own calculator.

```bash
uv run python -c "
from northwind.pricing import cost_usd
print(cost_usd('gpt-4.1-mini', 3259, 42))
print(cost_usd('gpt-4.1-mini', 1200, 180, cached_tokens=900))
print(cost_usd('gpt-4.1', 3259, 42))
import litellm
print(litellm.cost_per_token(model='gpt-4.1-mini', prompt_tokens=1200, completion_tokens=180, cache_read_input_tokens=900))
"
```

[DEMO: output:]

```
0.0013708
0.000498
0.006854
(0.00020999999999999998, 0.000288)
```

The first line is step one of the demo request from 6.1: thirty-two fifty-nine in, forty-two out, a seventh of a cent, exactly what the agent printed. A cached example: twelve hundred in, nine hundred of them cached, one eighty out. Twelve hundred minus nine hundred is three hundred uncached at forty cents, nine hundred at ten cents, one eighty at a dollar sixty. About five hundredths of a cent. And LiteLLM agrees: `cost_per_token` returns the input part and the output part as a tuple. The long decimal is ordinary floating-point noise: twenty-one thousandths of a cent input, and the same output figure. [PAUSE] Two independent calculators, same answer. That's the moment you can trust the function.

The third line is the same step on gpt-4.1, the escalation model. Five times the mini step. Remember that for 6.6.

[CODE: `tests/unit/test_pricing.py` (excerpt: four of the sixteen tests)]

```python
from decimal import Decimal

import pytest

from northwind.pricing import FALLBACK_PRICES, UnknownModelError, estimate_cost, get_price  # (import list trimmed)


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


def test_reasoning_tokens_not_double_charged():
    plain = estimate_cost("gpt-5-mini", 100, 300)
    with_reasoning = estimate_cost("gpt-5-mini", 100, 300, reasoning_tokens=200)
    assert plain.total_usd == with_reasoning.total_usd
    assert with_reasoning.reasoning_usd == Decimal("0.00040000")


def test_unknown_model_raises():
    with pytest.raises(UnknownModelError):
        get_price("gpt-99-ultra")
```

Four of the sixteen tests in the file, and the first one is the shape check that would have saved that team: for every pinned model, cached is below input is below output, so a typo in a price fails the build. Comparing the table with LiteLLM's is the one-liner you run when you bump the library, `litellm.model_cost["gpt-4.1-mini"]["input_cost_per_token"]` against `get_price("gpt-4.1-mini").input_per_token`; the day the library ships a new price, that check goes red and someone has to look at the price page and update the date. [PAUSE] That's a price change becoming a code review instead of a surprise. The second test pins the cached-subset rule. The third pins that reasoning tokens are reported but never charged twice. The fourth pins the loud failure.

[SCREEN: terminal, `uv run pytest tests/unit/test_pricing.py -q`]

[DEMO: `27 passed` (several tests are parametrized over the five pinned models)]

[AVATAR]

One more thing about rounding. Store cost in USD as a float with eight decimals per generation, and sum before you round for display. Rounding each generation to cents and then summing ten thousand of them gives you a report that is off by dollars. We display cents; we never store them.

[SLIDE 2: Recap]
- Read prices from LiteLLM, pin a dated fallback
- One function, `estimate_cost`, does all the arithmetic
- Cached tokens are a subset of input

### Recap

Read prices from `litellm.model_cost` when you can, pin a dated fallback table with tests, and let one function, `estimate_cost`, do all the arithmetic, with cached tokens as a subset of input.

### Transition

Now that every generation can have a price, let's put a tenant, a user and a feature on each one and roll them up into the report finance actually wants.

### Speaker notes: common mistakes and Q&A

- **"Why not just use `litellm.completion_cost(response)`?"** Use it when you have a LiteLLM response object. Atlas also runs offline and computes cost from span attributes, so a pure function over token counts is the common denominator. Show both agree, as in the demo.
- **`cache_read_input_token_cost` missing for a model.** `_litellm_price` falls back to the full input price for the cached rate, which overstates cost rather than understating it. Say why that direction is the safe one.
- **Currency.** Everything is USD. If finance reports in EUR, convert at report time with a dated rate, never per generation.
- **Batch and flex tiers.** Some providers discount batch or flexible processing; that's an override, not a new function.
- **Verify current pricing.** Repeat it. The constants on screen are dated 2026-09-28.

---
## Lecture 6.3: Cost per request, session, user, tenant and feature

| Field | Value |
|---|---|
| ID | 6.3 |
| Title | Cost per request, session, user, tenant and feature |
| Type | SC (screencast code-along; upload as Part A "attribution" and Part B "the showback report") |
| Target duration | 9:00 (about 960 spoken words at ~140 wpm; remaining time is on-screen code, runs and the report) |
| One idea | Attach cost to every generation together with tenant, user, session and feature, then roll up, so the same fifty-six dollars can be sliced any way finance asks. |
| Prerequisites | 6.2; Section 4 (sessions, users, tags) |
| Files used | `src/northwind/cost.py`, `src/northwind/report.py`, `src/northwind/slo.py`, `app/agent.py`, `telemetry/genai_attrs.py`, `telemetry/metrics.py`, Ops Console Cost page (`console/pages/2_Cost.py`) |

**Learning objectives**

1. Record a `CostRecord` per generation and per request with `trace_id`, `session_id`, `user_id`, `tenant`, `feature`, `intent`, `model`, token counts and `cost_usd`.
2. Write the same numbers on the generation span as `gen_ai.usage.*`, `atlas.cost_usd` and Langfuse's `usage_details` / `cost_details` attributes (`genai_attrs.set_llm_usage`, `set_cost`), and on the Prometheus counter `atlas_cost_usd_total{tenant,model,feature}`.
3. Roll up by any dimension with `rollup`, and read the showback report's tenant and feature tables and its cost per resolved session.

### Script

[AVATAR]

Your CFO asks one question: "What does the helpdesk agent cost per department?" [PAUSE] If your answer is "fifty-six dollars a day, total," you've just told them you don't know. If your answer is a table with four rows, cost per session, and a trend, you've just been given budget for the next quarter. Same data. The difference is attribution.

[SLIDE 1: Five dimensions, one record]
- Request: one `trace_id`
- Session: one conversation, `session_id`
- User: one employee, `user_id` (the collector hashes it before export, Section 10)
- Tenant: one department, `tenant` tag
- Feature: what Atlas served, from `feature_for_intent` in `app/mock_llm.py`: `policy_question`, `ticket_lookup`, `create_ticket`, `password_reset`, `shipment_status`, `escalation`, `other` (the finer `intent` rides along)
- Every generation carries all five plus tokens and `cost_usd`

[AVATAR]

Five dimensions. Request, session, user, tenant, feature. The trick is that you don't compute five reports. You stamp all five onto every generation, once, at the moment it happens. Then any report is a group-by. Let's see the record.

[SCREEN: VS Code, `src/northwind/cost.py`]

[CODE: `src/northwind/cost.py` (excerpt)]

```python
Dimension = Literal["tenant", "session_id", "user_id", "feature", "model", "intent"]
DIMENSIONS: tuple[str, ...] = ("tenant", "session_id", "user_id", "feature", "model", "intent")


@dataclass(frozen=True)
class CostRecord:
    """One priced LLM generation (or a whole request when aggregated upstream)."""

    trace_id: str
    tenant: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: float
    session_id: str = ""
    user_id: str = ""
    feature: str = "chat"
    intent: str = "unknown"
    cached_tokens: int = 0
    reasoning_tokens: int = 0
    latency_ms: float = 0.0
    outcome: str = "resolved"
    steps: int = 1
    scenario: str | None = None

    # CostRecord.from_usage(...) builds one from token counts and prices it with estimate_cost()


def rollup(records: Iterable[CostRecord], by: str = "tenant") -> dict[str, Rollup]:
    """Group records by one dimension and aggregate."""
    if by not in DIMENSIONS:
        raise ValueError(f"unknown dimension {by!r}; choose from {DIMENSIONS}")
    out: dict[str, Rollup] = {}
    for r in records:
        key = str(getattr(r, by)) or "(none)"
        agg = out.setdefault(key, Rollup(key=key))
        agg.requests += 1
        agg.cost_usd += Decimal(str(r.cost_usd))
        agg.input_tokens += r.input_tokens
        agg.output_tokens += r.output_tokens
        agg.cached_tokens += r.cached_tokens
        if r.session_id:
            agg.sessions.add(r.session_id)
        if r.outcome == "resolved":
            agg.resolved += 1
        elif r.outcome == "escalated":
            agg.escalated += 1
        elif r.outcome in {"error", "step_limit", "refused", "timeout", "tool_error"}:
            agg.errors += 1
    return out


def cost_per_session(records: Iterable[CostRecord]) -> Decimal:
    """Average cost per distinct session across all records."""
    recs = list(records)
    sessions = {r.session_id for r in recs if r.session_id}
    if not sessions:
        return Decimal(0)
    return total_cost(recs) / len(sessions)
```

`CostRecord` is one priced generation, or one whole request when the store aggregates upstream. Tokens, model, `cost_usd`, and the dimensions: tenant, session, user, feature, intent. `CostRecord.from_usage` builds one from token counts and prices it with `estimate_cost` from 6.2, so nobody types a price and nobody stores a stale one.

[SCREEN: zoom on `rollup`; the `by not in DIMENSIONS` guard and the `agg.sessions.add` line highlighted]

`rollup` groups by any dimension in `DIMENSIONS` and returns a `Rollup` per key: requests, sessions, tokens, cost, and the derived `cost_per_request`, `cost_per_session` and `cache_hit_ratio`. `by="tenant"` gives the CFO's table. `by="feature"` or `by="intent"` tells engineering which question type to optimize first. `by="model"` tells you what the escalation model is really costing. And `by="user_id"` deserves a slide of its own.

[SLIDE 2: `rollup(records, by="user_id")` on the replayed day]
- 80 employees used Atlas on the replayed day
- The top 20 account for just over a third of the spend
- The top five are all in ops, 200 to 260 requests each, mostly policy questions
- In the local store the key is the employee ID; exported telemetry carries a hash (Section 10)
- Do this rollup in the report, from the span store. Never as a Prometheus label

[AVATAR]

Eighty employees, and the top twenty spend just over a third of the money. The top five are all dispatchers in ops, two hundred-plus requests each in one day, mostly policy questions. Not misuse. But it's a product signal: those people would rather ask Atlas than search the intranet, and you only see it at the user level. [PAUSE] Do that rollup in the report, from the span store. Never as a Prometheus label, because a label with one value per employee is a cardinality bomb. That's the rule from lecture 5.5.

Where do the records come from? The agent loop.

[SCREEN: `app/agent.py`, the generation step]

[CODE: `app/agent.py` (excerpt, inside `_call_model`)]

```python
                    inp, out, cached, reasoning = usage_numbers(usage)
                    cost = self._price(current, inp, out, cached, reasoning)
                    ga.set_llm_usage(
                        span,
                        input_tokens=inp,
                        output_tokens=out,
                        cached_tokens=cached,
                        reasoning_tokens=reasoning,
                        response_model=getattr(resp, "model", None)
                        if not stream
                        else getattr(last, "model", None),
                        finish_reasons=[finish] if finish else None,
                        ttft_s=ttft_s,
                        completion_start_time=t0 if ttft_s is None else None,
                    )
                    ga.set_cost(span, cost)
```

```python
# telemetry/genai_attrs.py
def set_cost(span: Span, cost: CostBreakdown) -> None:
    span.set_attribute(ATLAS_COST_USD, float(cost.total_usd))
    span.set_attribute(
        LF_OBS_COST,
        json.dumps(
            {
                "input": float(cost.input_usd),
                "output": float(cost.output_usd),
                "cache_read_input_tokens": float(cost.cached_usd),
                "total": float(cost.total_usd),
            }
        ),
    )
```

```python
# app/agent.py, a few lines further down in _call_model
                    metrics.record_generation(
                        tenant=tenant,
                        model=current,
                        feature=feature,
                        input_tokens=inp,
                        output_tokens=out,
                        cached_tokens=cached,
                        reasoning_tokens=reasoning,
                        cost_usd=float(cost.total_usd),
                        ttft_s=ttft_s,
                    )
```

Three destinations, one moment. `usage_numbers` reads the usage object, Chat or Responses shape, and `_price` calls `estimate_cost` once. Just above this excerpt, the generation span also gets `atlas.tenant` and `atlas.feature`, so every generation knows who it was for.

[SLIDE 3: One moment, three destinations]

| Destination | What it gets | Who reads it |
|---|---|---|
| Span attributes | `gen_ai.usage.*`, `atlas.cost_usd`, `atlas.tenant`, `atlas.feature` | the local store: console, `make report` |
| Langfuse attributes | `langfuse.observation.usage_details` and `cost_details` | the trace UI: dollars next to tokens |
| Prometheus | `atlas_cost_usd_total{tenant,model,feature}`, `atlas_tokens_total{tenant,model,kind}` | Grafana and alerts (Section 9) |

[AVATAR]

`set_llm_usage` writes the tokens as `gen_ai.usage.*` and as Langfuse's `usage_details`. `set_cost` writes the money twice over: `atlas.cost_usd`, which the local store turns into a `CostRecord` for the console and the reports, and `cost_details`, so the trace UI shows dollars next to tokens. [PAUSE] And `metrics.record_generation` increments the Prometheus counter `atlas_cost_usd_total`, for the dashboards in Section 9. Note the labels on the counter: tenant, model, feature. Never user or session.

One detail. Langfuse can compute cost itself from its own model price list when you send `usage_details`. We send `cost_details` anyway, because the number in the report must equal the number in the trace, and only our function guarantees that.

[SCREEN: terminal]

Part B. The report. Let's replay the day and run it.

```bash
OFFLINE=1 make replay        # the baseline day into .atlas/spans.sqlite (about 20 s)
make report                  # northwind.report.weekly_report over the local store, markdown to stdout
```

[DEMO: the markdown report renders. On screen, the first three sections (trimmed):]

```
## Headline numbers
| Total LLM cost | $56.28 | - |
| Requests | 10,184 | sessions: 4,000 |
| Cost per session | $0.0141 | budget $0.0500 |
| Cost per resolved session | $0.0144 | |

## Cost by tenant (showback)
| ops | 4296 | 1706 | 46,931,225 | 860,229 | 0% | 20.2745 | 0.0119 | 36.0% |
| eng | 2171 | 839 | 29,086,255 | 542,988 | 0% | 12.5033 | 0.0149 | 22.2% |
| finance | 1866 | 719 | 27,692,013 | 522,313 | 0% | 11.9125 | 0.0166 | 21.2% |
| hr | 1851 | 736 | 26,720,647 | 481,997 | 0% | 11.5908 | 0.0157 | 20.6% |

## Cost by feature
| policy_question | 6420 | 2976 | 99,440,908 | 1,960,774 | 0% | 42.9136 | 0.0144 | 76.2% |
| create_ticket | 1539 | 1194 | 15,834,501 | 204,797 | 0% | 6.6615 | 0.0056 | 11.8% |
...
```

[SLIDE 4: Showback by tenant (baseline day)]

| Tenant | Sessions | Cost | Cost per session | Share |
|---|---|---|---|---|
| ops | 1,706 | $20.27 | $0.0119 | 36.0% |
| eng | 839 | $12.50 | $0.0149 | 22.2% |
| finance | 719 | $11.91 | $0.0166 | 21.2% |
| hr | 736 | $11.59 | $0.0157 | 20.6% |
| **Total** | **4,000** | **$56.28** | **$0.0141** | |

[AVATAR]

Here's the CFO's table. Ops is thirty-six percent of the bill because it's forty-three percent of the sessions, and its cost per session is the lowest, just over a cent, because dispatchers ask short ticket and shipment questions. Finance is the most expensive per session, one point seven cents, because payroll and expense questions retrieve more policy text. [PAUSE] That spread is the interesting finding, and it's small. No department is misusing Atlas. The cost is structural. To cut it, change the agent, not the users.

Now slice the same records by feature.

[SLIDE 5: Showback by feature (baseline day)]

| Feature | Share of requests | Cost | Cost per request |
|---|---|---|---|
| policy_question | 63% | $42.91 | $0.0067 |
| create_ticket | 15% | $6.66 | $0.0043 |
| ticket_lookup | 10% | $3.21 | $0.0031 |
| shipment_status | 7% | $2.21 | $0.0031 |
| password_reset | 3% | $0.78 | $0.0028 |
| escalation | 0.4% | $0.38 | $0.0088 |
| other | 1% | $0.13 | $0.0009 |

[AVATAR]

Now it's not flat. Policy questions are sixty-three percent of requests and seventy-six percent of the cost, at two thirds of a cent each, more than double a ticket lookup or a shipment check. Why? Policy questions call `search_knowledge_base`, and that tool returns four passages, about thirty-four hundred tokens, that get re-sent on every following step and every follow-up turn. [PAUSE] That one row tells you where the context diet in 6.5 will pay off most. And the escalation row: forty-three requests, the most expensive per request by far, and still under half a dollar. Remember that for 6.6.

[SLIDE 6: The number finance accepts: cost per resolved session]
- Cost per session: total ÷ sessions = $0.0141
- Cost per resolved session: cost of resolved requests ÷ sessions with a resolved answer = $0.0144
- On the replay 10,069 of 10,184 requests end `resolved`, so the two are close
- Errors, step limits and timeouts push them apart: cost per session stays flat, cost per resolved session climbs
- Section 8 adds the judge's `resolved` score for answers that ended but didn't help

[AVATAR]

One more number, and it's the one finance accepts: cost per resolved session. The report divides the cost of resolved requests by the sessions that got a resolved answer. One point four four cents against one point four one per session, close today, because almost every replayed request resolves. [PAUSE] Why report the harsher number? Because when requests start failing, cost per session stays flat and cost per resolved session climbs. It notices when the agent gets worse. The outcome only knows about errors, step limits and timeouts, though. An answer that ended politely and helped nobody still counts as resolved. Section 8 fills that gap with the judge.

[SCREEN: Ops Console (`make console`), Cost page: the four tiles (total cost, cost per session, cost per resolved session, cache hit ratio), the tenant and feature bars, the ten most expensive conversations with "open trace" links]

The Ops Console Cost page shows the same rollups. Same records, same `rollup` function, so the console and the markdown report never disagree. And the bottom table, the ten most expensive conversations, links each one to its trace.

[SLIDE 7: Recap]
- Stamp five dimensions on every generation
- Same numbers go to spans, Langfuse and Prometheus
- Every report is a group-by

### Recap

Stamp every generation with tenant, user, session, feature, model, tokens and `cost_usd`, send the same numbers to the span store, Langfuse and Prometheus, and any report, including cost per resolved session, is a group-by.

### Transition

Attribution tells you where the money goes. Next, the first lever that brings it back: prompt caching, which cuts the day by a third without changing a single answer.

### Speaker notes: common mistakes and Q&A

- **Typing prices anywhere but `pricing.py`.** `CostRecord.from_usage` prices through `estimate_cost`; the span keeps the tokens, so a corrected price table can re-price history from `gen_ai.usage.*`.
- **Feature detection.** `run()` classifies the message (`classify_intent`) and maps it with `feature_for_intent`; anything that is not a tool request is a `policy_question`, and small talk or an injection attempt goes to `other`. The generation span and the request span both carry `atlas.feature`, which is what makes the report's feature table real.
- **Cost per session across days.** Sessions can span midnight. Attribute to the day the session started; say so in the report footer.
- **Langfuse `cost_details` keys.** Use the same keys as `usage_details` (`input`, `output`, `cache_read_input_tokens`). Verified on langfuse 4.15.
- **Escalation cost: $0.38 or $0.32?** The feature row ($0.38) is both steps of the 43 escalation requests; the console's "by model" view shows only the 43 gpt-4.1 generations. Both are right; say which one you are quoting.
- **Part A / Part B split.** Cut after slide 3 and its narration; Part B starts at `make replay`.

---

## Lecture 6.4: Prompt caching: the cheapest win

| Field | Value |
|---|---|
| ID | 6.4 |
| Title | Prompt caching: the cheapest win |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 650 spoken words at ~140 wpm; remaining time is on-screen code, runs and the before/after) |
| One idea | Put everything stable at the front of the prompt, set a `prompt_cache_key`, and the same day of traffic costs 34% less with identical answers. |
| Prerequisites | 6.3 |
| Files used | `app/agent.py`, `app/prompts.py`, Ops Console Cost page |

**Learning objectives**

1. Explain how provider-side prompt caching works: exact prefix match, 1,024-token minimum, cached input billed at a quarter price, hit rate depends on recency and routing.
2. Restructure Atlas's prompt so the stable prefix (system, tools, policy) comes first and per-request content comes last, and pass `prompt_cache_key`.
3. Measure `cached_tokens` per step and compute the before/after cost on the same replayed day.

### Script

[B-ROLL: split screen. Left, red tint, BEFORE: a request's two steps with `cached_tokens: 0, 0`. Right, green tint, AFTER: the same two steps with `cached_tokens: 3,200, 3,200`. Cost line: $0.00449 → $0.00257.]

[AVATAR]

Same question, same answer, same model. Left side, half a cent. Right side, a quarter of a cent. [PAUSE] The only difference is the order of the prompt and one parameter. This is the cheapest win in the course, and most teams haven't turned it on.

[SLIDE 1: How prompt caching works (OpenAI, verify current terms)]
- Provider caches the prefix of a prompt it has seen recently; exact match, from the start
- Minimum 1,024 tokens; hits are reported in `usage.prompt_tokens_details.cached_tokens`
- Cached input is billed at $0.10/M instead of $0.40/M on gpt-4.1-mini (a quarter of the price)
- Cache lives minutes, not hours; hit rate depends on traffic and routing
- `prompt_cache_key` routes requests with the same prefix to the same cache

[AVATAR]

The mechanism. When you send a prompt, the provider checks whether it has recently seen a prompt that starts with the same tokens. Exact match, from the first token. If the shared prefix is at least a thousand and twenty-four tokens, those tokens are served from cache, reported as `cached_tokens`, and billed at a quarter of the price. The cache lives for minutes, so it only helps when traffic is steady, which for a helpdesk it is. And `prompt_cache_key` is a hint that sends requests with the same prefix to the same cache machine, which raises your hit rate.

So the whole game is: make the front of the prompt identical across as many requests as possible.

[SLIDE 2: Order matters]
- BEFORE: `[date and tenant banner] [user question] [system rules] [tools] [policy snippets] [history]`
- One changing token at the front breaks the match for everything behind it
- AFTER: `[system rules] [tools] [policy snippets for tenant] [history] [user question]`
- Stable first, per-request last

[AVATAR]

Here's what Atlas version one did wrong, and it's what most agents do. The prompt began with a banner: today's date, the tenant, the user's name. Then the rules and tools. [PAUSE] The date changes every day. The user changes every request. One changing token at the front, and nothing behind it can ever match. The fix is a sort: stable first, per-request last.

[SCREEN: VS Code, `app/prompts.py` then `app/agent.py`]

[CODE: `app/prompts.py` and `app/agent.py` (excerpts): the key, the prompt order and the call]

```python
# app/prompts.py
def prompt_cache_key(version: str, tenant: str) -> str:
    """Stable per-prompt, per-tenant cache key (Section 6.4)."""
    return f"atlas-{version}-{tenant}"
```

```python
# app/agent.py
    def _cache_key(self, prompt_version: str, tenant: str) -> str | None:
        """``prompt_cache_key`` sent to OpenAI (None when caching is off)."""
        return prompt_cache_key(prompt_version, tenant) if self.settings.prompt_cache else None
```

```python
# app/agent.py, run(): stable first, per-request last
            messages: list[dict[str, Any]] = [{"role": "system", "content": prompt_text}]
            messages.extend(history or [])
            messages.append({"role": "user", "content": message})
```

```python
# app/agent.py, _call_model(): the call
                    kwargs: dict[str, Any] = dict(
                        model=current,
                        messages=messages,
                        tools=TOOL_SCHEMAS,
                        stream=stream,
                        scenario=scenario,
                        timeout=self.settings.request_timeout_s,
                    )
                    if cache_key:
                        kwargs["prompt_cache_key"] = cache_key
                    resp = self.llm.chat(**kwargs)
```

Three layers. The system message is the prompt version's text from `app/prompts.py`, nothing else: no date, no user name, no tenant banner. `TOOL_SCHEMAS`, the five tool definitions, is a constant, so it's part of the prefix too. The history comes next; within a session it only grows at the end, so earlier turns keep matching. Then the question, last, where it can't break anything.

The cache key is `atlas-<version>-<tenant>`. One prompt version, four tenants, four keys. [PAUSE] Never put the user or session in the key. That would give you four thousand keys a day and almost no hits. And `ATLAS_PROMPT_CACHE=0` makes `_cache_key` return `None`, which is how the baseline replay measures the world without caching.

[SCREEN: terminal]

Let's prove it. One request, two steps, print `cached_tokens` per step.

```bash
OFFLINE=1 OTEL_EXPORTER=none ATLAS_PROMPT_CACHE=1 ATLAS_CONTEXT_DIET=0 uv run python -c "
from app.agent import AtlasAgent
a = AtlasAgent()
for sid in ('warm', 'demo'):        # the first call warms the cache shard, like the previous ops request would
    r = a.run('How do I reset my VPN token?', tenant='ops', user_id='NW-40213', session_id=sid)
for g in r.generations:
    print(f'step {g.step}  prompt={g.input_tokens}  cached={g.cached_tokens}  completion={g.output_tokens}')
print(f'request cost: \${r.cost_usd:.5f}')
"
```

[DEMO: output:]

```
step 1  prompt=3259  cached=3200  completion=42
step 2  prompt=6667  cached=3200  completion=282
request cost: $0.00257
```

Step one: thirty-two hundred cached. That's the system prompt plus the tool schemas, rounded down to a cache block, hit because another ops request ran a moment ago. Step two: thirty-two hundred again, the same prefix; the thirty-four hundred tokens of fresh retrieval results can't be cached, because nobody has sent them before. [PAUSE] So this request cost forty-three percent less than the four forty-nine it cost uncached. The number you can't control is step one across requests: whether the previous request on this shard shared your prefix. On the replayed day, forty-nine percent of all input tokens come from cache.

Now the same day of traffic.

```bash
OFFLINE=1 make replay STORE=.atlas/base.sqlite            # baseline, caching off
OFFLINE=1 make replay CACHE=1 STORE=.atlas/cache.sqlite   # same seed, caching on
```

[SLIDE 3: Before and after on the same day (verify current pricing)]

| | Before | After |
|---|---|---|
| Uncached input, demo request | 9,926 | 3,526 |
| Cached input, demo request | 0 | 6,400 |
| Input cost, demo request | $0.003970 | $0.001410 + $0.000640 = $0.002050 |
| Cost per request (demo, mini) | $0.00449 | $0.00257 |
| Share of the day's input tokens served from cache | 0% | 49.3% |
| Day | $56.28 | **$37.00** |
| Saving | | **$19.28 a day, 34.3%** |

[AVATAR]

The day drops from fifty-six twenty-eight to thirty-seven dollars. Nineteen dollars twenty-eight a day, about five hundred eighty a month, thirty-four percent, with a forty-nine percent hit rate on input tokens that the replay models from the real traffic shape. [PAUSE] The answers are byte-for-byte identical, because the model saw the same tokens. Caching changes the bill, not the behavior.

[SCREEN: Ops Console (`make console STORE=.atlas/cache.sqlite`), Cost page: the "Cache hit ratio" tile reads 49%; then Compare replays with `base.sqlite` and `cache.sqlite` side by side: cost, Δ%, cache ratio]

One tile on the console's Cost page: cache hit ratio, cached tokens over all input tokens. And because both replays went to their own store, the Compare replays page puts them side by side. Watch that tile. If it falls, someone put a timestamp at the front of the prompt again. It's the cheapest regression to catch and the most common one to ship.

[SLIDE 4: Caching rules of thumb]
- Sort: stable, slow, volatile
- Key on version and tenant, never user
- Prefix under 1,024 tokens? Nothing caches; measure before you celebrate
- Hit rate lives in `cached_tokens`; put it on a dashboard
- Other providers: explicit cache blocks and different prices; same sort, different API

[AVATAR]

Rules of thumb. Sort the prompt. Key on version and tenant. Check your prefix length, because under a thousand and twenty-four tokens nothing happens at all. Dashboard the hit rate. And if you use a provider with explicit cache controls, the sorting lesson is identical; only the API and the prices differ.

[SLIDE 5: Recap]
- Stable prefix first, volatile content last
- Cache key: prompt version plus tenant
- Same day: $56.28 becomes $37.00

### Recap

Put the stable prefix first, the volatile bits last, set `prompt_cache_key` to version plus tenant, and the same day of Atlas traffic drops from $56.28 to $37.00 with identical answers.

### Transition

Caching makes re-sent tokens cheaper. The next lever makes them fewer: the context diet.

### Speaker notes: common mistakes and Q&A

- **"Why isn't the hit rate 100%?"** Step one of each request depends on another request with the same prefix having run recently on the same shard. Cache expiry, traffic lulls and routing cost you hits. 49.3% of input tokens is the measured number on the replayed day; the console shows the real one.
- **Date in the system prompt.** The most common regression. If Atlas needs today's date, put it at the end of the user message, never in `app/prompts.py`.
- **History that gets edited.** Summarising or trimming the middle of the history breaks the prefix for that session. In 6.5 `trim_history` drops whole turns from the oldest end, so the system prompt and tool schemas still match.
- **Multiple prompt versions live at once.** Two versions halve the hit rate for the day of a rollout. That's fine; say it in the runbook.
- **Prices and terms.** Cached price, minimum prefix and retention have changed before. Verify current pricing and docs before recording.

---

## Lecture 6.5: The context diet

| Field | Value |
|---|---|
| ID | 6.5 |
| Title | The context diet |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 690 spoken words at ~140 wpm; remaining time is on-screen code and the before/after) |
| One idea | Truncate tool results and trim history, measure tokens per step before and after, and cut the input bill by a quarter without hurting answers. |
| Prerequisites | 6.4 |
| Files used | `src/northwind/tokens.py`, `app/agent.py`, `src/northwind/config.py`, `tests/unit/test_tokens.py` |

**Learning objectives**

1. Estimate tokens without the network using `estimate_tokens`, and use `tiktoken` only when its encoding is already cached.
2. Apply `context_diet`, which runs `truncate_tool_result` (a JSON-aware cap with a marker) and then `trim_history` (oldest turns first, replaced by a summary line), in the agent loop.
3. Keep retrieval top-k a separate, measured knob (`ATLAS_TOP_K`, default 4) and measure tokens per step and cost per request before and after.

### Script

[AVATAR]

Thirty-four hundred tokens. That's what `search_knowledge_base` returned for "how do I reset my VPN token." Four passages, about eight hundred fifty tokens each with their metadata. The answer used one of them. [PAUSE] The other twenty-five hundred tokens rode along into the next step, at full price, and in a multi-turn session into every follow-up, saying nothing. Multiply by sixty-four hundred policy questions a day. That's the diet.

[SLIDE 1: Four places context bloats]
- History: every past turn, forever
- Tool results: whole documents when a paragraph would do
- Retrieval: top-k of 12 (Incident 1) when 4 answers the question
- Tool schemas: fifty tools when the request needs five
- Rule: measure tokens per step first; cut the biggest, re-measure

[AVATAR]

Context bloats in four places. History that never gets trimmed. Tool results pasted whole. Retrieval that returns more chunks than the answer needs. And tool schemas, which we'll leave alone today because Atlas has five. The rule is the same as for any performance work: measure per step, cut the biggest, measure again. Let's look at the helpers.

[SCREEN: VS Code, `src/northwind/tokens.py`]

[CODE: `src/northwind/tokens.py` (excerpt)]

```python
def estimate_tokens(text: str, model: str | None = None) -> int:
    """Alias of :func:`count_tokens` (name used in the lecture scripts)."""
    return count_tokens(text, model)


def truncate_tool_result(result: str, max_tokens: int = 400) -> str:
    """Tool results are the usual source of context bloat.

    JSON results stay **valid JSON**: long string fields are clipped and, if that
    is not enough, list items are dropped from the end. Plain text keeps the head
    and the tail with a marker in between.
    """
    if count_tokens(result) <= max_tokens:
        return result
    ...


def trim_history(
    messages: Sequence[Message],
    max_tokens: int,
    *,
    keep_system: bool = True,
    keep_last_n: int = 2,
    summariser: Summariser | None = summarise_placeholder,
    model: str | None = None,
) -> list[Message]:
    """Drop the oldest non-system turns until the history fits ``max_tokens``.

    The system prompt (if ``keep_system``) and the last ``keep_last_n`` messages
    are always kept. Dropped turns are replaced by one system-role summary when a
    ``summariser`` is given. Tool-call/tool-result pairs are dropped together so
    the API never sees an orphan ``tool`` message.
    """
    ...


def context_diet(
    messages: Sequence[Message],
    *,
    history_budget: int = 3000,
    tool_result_budget: int = 400,
    keep_last_n: int = 2,
) -> tuple[list[Message], dict[str, int]]:
    """Apply tool-result truncation then history trimming; return (messages, stats)."""
    before = count_message_tokens(messages)
    slimmed: list[Message] = []
    for m in messages:
        if m.get("role") == "tool" and isinstance(m.get("content"), str):
            m = {**m, "content": truncate_tool_result(m["content"], tool_result_budget)}
        slimmed.append(m)
    trimmed = trim_history(slimmed, history_budget, keep_last_n=keep_last_n)
    after = count_message_tokens(trimmed)
    return trimmed, {"tokens_before": before, "tokens_after": after, "saved": before - after}
```

Four functions. `count_tokens`, with the alias `estimate_tokens`, uses `tiktoken` only when `ATLAS_USE_TIKTOKEN=1` and the encoding is already on disk; otherwise a word-and-punctuation approximation. That's within about ten percent for English, and it never phones home, so tests and offline mode work.

[SCREEN: zoom on `truncate_tool_result` and `trim_history`; the docstring lines "JSON results stay valid JSON" and "Tool-call/tool-result pairs are dropped together" highlighted]

`truncate_tool_result` caps a result and keeps JSON valid: long string fields are clipped first, then list items are dropped from the end; plain text keeps the head and the tail with a visible marker, so the model knows it saw a cut and can ask for more. `trim_history` drops the oldest turns until the history fits its budget, always keeps the system prompt and the last two messages, drops tool-call and tool-result pairs together so the API never sees an orphan, and replaces what it dropped with one summary line. `context_diet` runs the two in that order and returns the messages plus a `saved` count. Because it cuts from the oldest end, the cached prefix from 6.4 survives.

Now wire them in.

[SCREEN: `app/agent.py` and `src/northwind/config.py`]

[CODE: `app/agent.py` (excerpts) and `src/northwind/config.py` (excerpt)]

```python
# app/agent.py, run(): before the loop
            messages: list[dict[str, Any]] = [{"role": "system", "content": prompt_text}]
            messages.extend(history or [])
            messages.append({"role": "user", "content": message})
            diet_on = s.context_diet and scenario != "context_bloat"
            if diet_on:
                messages, stats = context_diet(
                    messages,
                    history_budget=s.history_token_budget,
                    tool_result_budget=s.tool_result_token_budget,
                )
                if stats["saved"]:
                    ga.add_event(root, "context.trimmed", **stats)
```

```python
# app/agent.py, _run_tool(): every tool result, as it arrives
            if diet_on:
                content = truncate_tool_result(content, self.settings.tool_result_token_budget)
            result_tokens = approx_tokens(content)
            tspan.set_attribute("atlas.tool.result_tokens", result_tokens)
            ...
        return {"role": "tool", "tool_call_id": tc.get("id"), "content": content}, ok
```

```python
# src/northwind/config.py, Settings (env names in from_env: ATLAS_TOP_K, ATLAS_CONTEXT_DIET,
# ATLAS_HISTORY_TOKENS, ATLAS_TOOL_RESULT_TOKENS)
    retrieval_top_k: int = 4
    ...
    context_diet: bool = True
    ...
    history_token_budget: int = 8000
    tool_result_token_budget: int = 1400
```

Two budgets in config: `history_token_budget`, eight thousand tokens, and `tool_result_token_budget`, fourteen hundred, both from the environment. The diet runs once before the loop, on the history the server kept for the session, and `_run_tool` caps every tool result as it arrives and records what the model actually got as `atlas.tool.result_tokens` on the tool span. An event on the root span, `context.trimmed`, records how many tokens the diet saved, so the saving is visible per trace. The `context_bloat` scenario switches the diet off on purpose; that's how Incident 1 is built. And the Makefile's `DIET` flag is just `ATLAS_CONTEXT_DIET`.

[SCREEN: `src/northwind/tokens.py`, `summarise_placeholder` and the `summariser` parameter of `trim_history`]

One option the code leaves on a placeholder: the `summariser` callback. The default, `summarise_placeholder`, writes one line: how many messages were dropped, how many user turns, how many tool results, which topics. You can pass a function that asks gpt-4.1-mini to write a two-sentence summary instead. It gives better continuity on long sessions, and it costs a model call, about three hundred input tokens and forty out, a hundredth of a cent. On Atlas, sessions average two and a half requests, so it would fire rarely. Turn it on when your history budget trips often, and measure it like everything else.

[SLIDE 2: Three knobs the diet flag leaves alone]
- `summariser`: one placeholder line by default; an LLM summary costs a model call
- Tool schemas: Atlas sends 5; with 40, send only the routed intent's tools
- Retrieval top-k: `ATLAS_TOP_K=4`, measured separately against the grounded score
- Incident 1 is what top-k 12 with the diet off looks like

[AVATAR]

The other cut for bigger agents is tool schemas. Atlas has five tools, well under a thousand tokens. If you have forty, send the model only the tools relevant to the routed intent, and you'll save more than the diet did. [PAUSE] And retrieval top-k. It is deliberately not part of the diet flag: `ATLAS_TOP_K` stays at four, because in the replay's ground truth four passages answer the question, and the judge's grounded score in Section 8 is the number that tells you whether a lower k is safe. Incident 1 shows what twelve looks like. We'll check the quality side in a moment.

[SCREEN: terminal]

Measure it. Same request as last lecture.

```bash
OFFLINE=1 OTEL_EXPORTER=none ATLAS_PROMPT_CACHE=0 ATLAS_CONTEXT_DIET=1 uv run python -c "
from app.agent import AtlasAgent
r = AtlasAgent().run('How do I reset my VPN token?', tenant='ops', user_id='NW-40213', session_id='demo')
for g in r.generations:
    print(f'step {g.step}  prompt={g.input_tokens}  cached={g.cached_tokens}  completion={g.output_tokens}')
print(f'input {r.usage[\"input_tokens\"]}  request cost: \${r.cost_usd:.5f}')
"
```

[DEMO: output:]

```
step 1  prompt=3259  cached=0  completion=42
step 2  prompt=4602  cached=0  completion=282
input 7861  request cost: $0.00366
```

Nine thousand nine hundred twenty-six becomes seven thousand eight hundred sixty-one. Twenty-one percent fewer input tokens on this request, all of it from the tool result: thirty-four hundred tokens of articles capped to fourteen hundred, JSON still valid. The history was already under budget, so `trim_history` did nothing here; it earns its keep on turn three and four. Now the day.

[SLIDE 3: Before and after on the same day (diet only, caching off, verify current pricing)]

| | Before | After |
|---|---|---|
| Input tokens, demo request | 9,926 | 7,861 |
| Steps | 3,259 / 6,667 | 3,259 / 4,602 |
| Cost per request (demo, mini) | $0.00449 | $0.00366 |
| Input tokens, whole day | 130.4M | 94.7M (−27%) |
| Day | $56.28 | **$41.99** |
| Saving | | **$14.29 a day, 25.4%** |
| Judge "grounded" score (replay, Section 8 metric) | 0.943 | 0.943 |

[AVATAR]

Fourteen dollars twenty-nine a day, twenty-five percent, on its own. And the last row is the one that makes this responsible: the grounded score on the replay doesn't move. [PAUSE] On the mock that is by construction; on a real model it is the number you watch. If it had dropped, the tool budget was too tight and you'd raise it. That's the discipline: every token cut ships with a quality number next to it. Section 8 makes that number automatic.

[SLIDE 4: Diet plus caching]
- The two levers stack: fewer tokens, and the ones left are cheaper
- Trim from the oldest end, whole turns at a time, so the prefix still matches
- Diet + caching on the same day: $56.28 → $22.71 (−59.6%)
- Retries and escalations still at baseline rates; that's 6.6 and 6.7

[AVATAR]

And they stack. Trimming from the oldest end keeps the cached prefix intact on every step, so with caching and the diet together the day comes down to twenty-two seventy-one. Sixty percent. [PAUSE] We haven't touched the escalation model or the retries yet. That's the next two lectures.

[SCREEN: `tests/unit/test_tokens.py`, `test_truncate_tool_result_keeps_json_valid`, `test_trim_history_keeps_system_and_tail` and `test_context_diet_bounds_tokens` visible; then terminal: `uv run pytest tests/unit/test_tokens.py -q` prints `18 passed`]

The unit tests protect the diet: truncation keeps JSON valid and plain text keeps its marker, trimming keeps the system prompt and the tail, and `test_context_diet_bounds_tokens` pushes three turns of whole articles through the diet and checks the result stays near the history budget. That last one is Incident 1's action item, already written. Run them offline with everything else.

[SLIDE 5: Recap]
- Cap tool results; JSON stays valid
- Trim history from the oldest end
- Day falls 25% alone, 60% with caching

### Recap

Cap tool results at 1,400 tokens (JSON stays valid), trim history to an 8,000-token budget with a summary line, keep top-k a measured knob, and the day falls 25% on its own ($41.99) and 60% with caching ($22.71), with the grounded score unchanged.

### Transition

Every one of those tokens still goes to gpt-4.1-mini, even when the answer is a ticket status read back from a tool. Next, we route the simple requests to a smaller model and keep the bigger ones for what needs them.

### Speaker notes: common mistakes and Q&A

- **Trimming in the middle.** Deleting middle turns changes the prefix and kills the cache for the rest of the session. `trim_history` cuts from the oldest end, whole turns at a time.
- **Truncating without a marker.** The model doesn't know it saw half a document and answers confidently. The marker lets it ask `search_knowledge_base` again with a narrower query.
- **Top-k as a global.** Different features may need different k. Keep it in config (`ATLAS_TOP_K`, default 4; the budget guard's degrade mode caps it at 2); Incident 1 is what 12 looks like.
- **tiktoken and network.** `tiktoken` downloads encodings on first use. `count_tokens` only tries it with `ATLAS_USE_TIKTOKEN=1` and otherwise approximates, so CI never needs the download. Show the fallback path once.
- **The grounded score.** Comes from the Section 8 judge run on the replay. If a student asks how we know, point ahead to 8.2 and to the simulator's ground-truth labels.

---

## Lecture 6.6: Small-model-first routing with LiteLLM Router

| Field | Value |
|---|---|
| ID | 6.6 |
| Title | Small-model-first routing with LiteLLM Router |
| Type | SC (screencast code-along; upload as Part A "the Router" and Part B "the escalation rule and cost impact") |
| Target duration | 9:00 (about 750 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Send the simple intents to gpt-4.1-nano, keep gpt-4.1-mini as the default and gpt-4.1 for escalation, and cut the day by 16% with the same answers. |
| Prerequisites | 6.5; `litellm` installed |
| Files used | `app/agent.py` (router mode), `src/northwind/config.py`, `telemetry/metrics.py` |

**Learning objectives**

1. Configure a LiteLLM `Router` with a `model_list`, `fallbacks`, `num_retries`, `timeout`, `allowed_fails` and `cooldown_time` (verified kwargs on litellm 1.103).
2. Read `_choose_deployment`: an intent-based routing rule where the budget guard's degrade decision always wins, plus the `[ESCALATE]` marker as the model's own signal to move one step up.
3. Measure generations and cost per model before and after, and see every routing decision on the span (`gen_ai.request.model`) and the counter (`model` label).

### Script

[AVATAR]

Fifty-six dollars of mini. That's the baseline day: every step of every request on gpt-4.1-mini, whether it was a payroll policy question or "where is shipment SHP-88213". [PAUSE] Here's the question I want you to sit with. Did a shipment lookup, a ticket status check or a ticket creation need the mid-size model? A third of Atlas's generations are that kind of request: the answer is a tool result read back. Let's find out with a router.

[SLIDE 1: Small-model-first]
- Default: gpt-4.1-mini for every step
- Simple intents (`SIMPLE_INTENTS`: `ticket_status`, `shipment`, `create_ticket`, `smalltalk`) go to gpt-4.1-nano
- The `escalation` intent goes straight to gpt-4.1; the model can also ask for one step on gpt-4.1 with the `[ESCALATE]` marker
- The budget guard's degrade decision always wins
- Also use the Router for fallbacks (Section 7) so there's one place for model selection

[AVATAR]

Small-model-first means the cheapest model that can do the job is the default for that job, and moving up is a decision you can point at: an intent, a marker in the model's own output, or the budget guard. And you escalate one step, not the whole conversation. The router also gives us fallbacks and cooldowns, which we'll lean on in Section 7, so model selection lives in exactly one place.

[SCREEN: VS Code, `app/agent.py`, router mode]

[CODE: `app/agent.py` (excerpt): building the Router]

```python
def build_router_config(settings: Settings) -> dict[str, Any]:
    """LiteLLM Router kwargs (verified against litellm 1.103): model_list, fallbacks,
    num_retries, timeout, allowed_fails, cooldown_time. Pure data — testable offline."""
    models = sorted(
        {
            settings.model,
            settings.escalation_model,
            settings.routing_model,
            settings.degraded_model,
            "gpt-4o-mini",
        }
    )
    return {
        "model_list": [
            {
                "model_name": m,
                "litellm_params": {"model": f"openai/{m}", "api_key": settings.openai_api_key},
            }
            for m in models
        ],
        "fallbacks": [{m: [FALLBACKS[m]]} for m in models if m in FALLBACKS],
        "num_retries": settings.max_retries,
        "timeout": settings.request_timeout_s,
        "allowed_fails": settings.router_allowed_fails,
        "cooldown_time": settings.router_cooldown_s,
    }


class RouterClient:
    """LiteLLM Router mode (Section 6.6 / 7.4). Imported lazily: LiteLLM is heavy."""

    def __init__(self, settings: Settings) -> None:
        from litellm import Router

        self.router = Router(**build_router_config(settings))

    def chat(self, **kwargs: Any) -> Any:
        kwargs.pop("scenario", None)
        kwargs.pop("prompt_cache_key", None)  # not all providers accept it
        if kwargs.get("stream"):
            kwargs.setdefault("stream_options", {"include_usage": True})
        return self.router.completion(**kwargs)
```

`build_router_config` is pure data, verified against litellm one point one oh three, so it's unit-tested offline. The `model_list` names every deployment Atlas can use, all from settings: the default, gpt-4.1-mini; the escalation model, gpt-4.1; the routing model, gpt-5-mini; the degraded model, gpt-4.1-nano; and gpt-4o-mini as a cross-family fallback. Swapping any of them is an environment variable.

[SCREEN: zoom on the `fallbacks`, `num_retries`, `timeout`, `allowed_fails` and `cooldown_time` lines]

`fallbacks` comes from the `FALLBACKS` table: if gpt-4.1-mini errors out, try gpt-4o-mini. That's for outages, not for quality; we'll tune it in Section 7. Keep the two ideas apart in your head. A fallback fires when a call fails. An escalation fires when a call succeeds and we don't trust the answer. The Router knows about the first. Only our code can know about the second. Two retries, a twenty-second timeout, and after three failures a deployment cools down for thirty seconds; those last two are `ATLAS_ROUTER_ALLOWED_FAILS` and `ATLAS_ROUTER_COOLDOWN_S`. `RouterClient` puts the Router behind the same `chat()` interface as the OpenAI client and the offline mock, which is why `ATLAS_ROUTER_MODE=1` is the only switch.

Now the escalation rule, which is ours, not the router's.

[CODE: `app/agent.py` (excerpt): choosing the deployment]

```python
    def _choose_deployment(self, intent: str, *, degraded: bool = False) -> str:
        """Small-model-first routing (Section 6.6).

        Without router mode every request uses ``settings.model``. With router mode
        (``ATLAS_ROUTER_MODE=1``) simple intents go to the cheap model and sensitive
        ones to the escalation model; the budget guard's *degrade* decision always wins.
        """
        s = self.settings
        if degraded:
            return s.degraded_model
        if not s.router_mode:
            return s.model
        if intent in SIMPLE_INTENTS:
            return s.degraded_model  # gpt-4.1-nano
        if intent == "escalation":
            return s.escalation_model
        return s.model
```

```python
# app/agent.py, run()
        intent = classify_intent(message)
        ...
        model = model or self._choose_deployment(intent)
        ...
                if decision.decision is Decision.DEGRADE:
                    ga.add_event(
                        root, "budget.degraded", reason=decision.reason, model=s.degraded_model
                    )
                    model, top_k = self._choose_deployment(intent, degraded=True), min(top_k, 2)
```

Three rules, in order. If the budget guard said degrade, the degraded model, gpt-4.1-nano, full stop; the budget always wins. Without router mode, everything is `settings.model`; that's the baseline. With router mode, a simple intent goes to nano: ticket status, shipment tracking, ticket creation, small talk, the requests where the answer is a tool result read back. The `escalation` intent, an employee asking for a person, goes straight to gpt-4.1. Everything else, every policy question and every password reset, stays on mini.

[SCREEN: `app/agent.py`, `_loop`: the `content.startswith(ESCALATE_MARKER)` branch highlighted]

[PAUSE] And there's a fourth path that isn't in this function: the model itself can start its answer with `[ESCALATE]`, and the loop re-runs that step on the escalation model, records an `escalation` event and marks the result. Every routing decision ends up on the generation span as `gen_ai.request.model` and in Prometheus under the `model` label, so tomorrow you can ask: which model is costing me money, for which intent?

Part B. The cost impact.

[SCREEN: terminal]

```bash
OFFLINE=1 make replay ROUTER=1 STORE=.atlas/router.sqlite
make report STORE=.atlas/router.sqlite      # the "Cost by model" section
```

[DEMO: the replay summary line `Total cost $47.0666   p95 latency 3827 ms`, then the report's "Cost by model" table:]

```
| model | requests | sessions | tokens in | tokens out | cache hit | cost (USD) | cost/session | share |
| gpt-4.1-mini | 6744 | 3061 | 101,277,278 | 1,990,671 | 0% | 43.6960 | 0.0143 | 92.8% |
| gpt-4.1-nano | 3397 | 1933 | 28,870,597 | 411,352 | 0% | 3.0516 | 0.0016 | 6.5% |
| gpt-4.1 | 43 | 43 | 140,595 | 4,730 | 0% | 0.3190 | 0.0074 | 0.7% |
| **total** | 10184 | 4000 | 130,288,470 | 2,406,753 | | 47.0666 | | 100% |
```

[SLIDE 2: Before and after on the same day (routing only, verify current pricing)]

| | Before (everything on mini) | After (`ROUTER=1`) |
|---|---|---|
| gpt-4.1-nano generations | 0 | 6,700 (33%) |
| gpt-4.1-mini generations | 20,087 | 13,344 |
| gpt-4.1 generations (escalation) | 43 | 43 |
| Requests answered on gpt-4.1-nano (report, by model) | 0 | 3,397, $3.05 |
| Requests answered on gpt-4.1-mini | 10,141, $55.90 | 6,744, $43.70 |
| Day | $56.28 | **$47.07** |
| Saving | | **$9.21 a day, 16.4%** |

[AVATAR]

A third of the generations move to nano, at a quarter of mini's price per token. The mini line falls from fifty-five ninety to forty-three seventy, and nano adds three dollars back. Nine dollars twenty-one a day, sixteen percent. [PAUSE] Smaller than caching. But this lever is the one that changes which model answers, so it's the one that needs a quality number next to it, and the one that needs its decisions on the span.

[SLIDE 3: What went where on the replayed day]

| Intent group | Generations | Model with `ROUTER=1` |
|---|---|---|
| `ticket_status`, `shipment`, `create_ticket`, `smalltalk` (`SIMPLE_INTENTS`) | 6,700 (33%) | gpt-4.1-nano |
| policy questions (`general`, `payroll`, `leave`, `vpn`, ...) and `password_reset` | 13,344 (66%) | gpt-4.1-mini |
| `escalation` (starts on gpt-4.1, so the replay reports 0 `escalated` outcomes) | 43 (0.2%) | gpt-4.1 |

[AVATAR]

And here's why the intent is on every span. If nano's answers to shipment questions come back with a lower grounded score next week, you'll see it by intent and by model in one filter, and you move that intent back to mini with one line in `SIMPLE_INTENTS`. That's a routing decision you can defend, because it's one you can measure.

[SLIDE 4: Did quality hold?]
- Judge `resolved` on the replay: 0.892 before, 0.892 after; `grounded` 0.943 both
- 6,700 generations that used to run on mini ran on nano at the same score
- Routing moved the cheap model to where it changed nothing but the bill

[AVATAR]

Quality held. On the mock that is by construction; on a real model, this is the slide you have to earn, per intent, on the same replayed day. [PAUSE] That's the whole idea of small-model-first: not "use the cheap model," but "make each model earn its place, request by request."

[SLIDE 5: Recap]
- Simple intents go to gpt-4.1-nano
- Budget's degrade decision always wins
- Same day: $56.28 becomes $47.07

### Recap

Put every model behind a LiteLLM Router built from `build_router_config`, route by intent with `_choose_deployment` (nano for simple intents, mini by default, gpt-4.1 for escalation), and the day falls from $56.28 to $47.07 with the judge scores unchanged.

### Transition

Three levers, each measured. Now the guard rail: per-tenant budgets that degrade gracefully and an anomaly detector that pages you before finance does.

### Speaker notes: common mistakes and Q&A

- **Confidence-based escalation.** Students ask for it; a self-reported confidence field is a weak signal alone. The shipped rule is intent-based plus the model's `[ESCALATE]` marker; a confidence threshold tuned on the replay is a good capstone extension.
- **Escalating the whole conversation.** Re-running all steps on gpt-4.1 costs 5× the request, not 5× one step. The code escalates a step.
- **Router fallbacks vs escalation.** `fallbacks` fire on errors and timeouts; escalation fires on quality signals. Both change the served model on the span. The agent's own circuit-breaker fallbacks (7.4) also count in `atlas_model_fallbacks_total{from_model,to_model}`; fallbacks the LiteLLM Router makes internally show up only as the served model, so check `response.model` when you run in router mode.
- **`gpt-5-mini` in the demo.** It is `ATLAS_ROUTING_MODEL` and already in the `model_list`; route an intent to it for a routing experiment, and its reasoning tokens show up in `output_tokens_details.reasoning_tokens` and change the cost math (6.1).
- **Part A / Part B split.** Cut after the `_choose_deployment` code block.

---

## Lecture 6.7: Budgets and anomaly alerts per tenant

| Field | Value |
|---|---|
| ID | 6.7 |
| Title | Budgets and anomaly alerts per tenant |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 630 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Give every tenant a daily budget with a soft cap that degrades and a hard cap that refuses politely, and flag an abnormal request cost before the day's total gets there. |
| Prerequisites | 6.6 |
| Files used | `src/northwind/budget.py`, `app/agent.py`, `app/server.py` (`GET /budget`), `telemetry/metrics.py`, `tests/unit/test_budget.py`, Ops Console Budgets page |

**Learning objectives**

1. Describe LiteLLM's `BudgetManager` concept and why Atlas uses its own `budget.py` for per-tenant caps.
2. Read `BudgetGuard.decide(tenant, now, next_cost_usd=)`, which returns a `BudgetDecision` with `ALLOW`, `DEGRADE` or `REFUSE`, and see how `run()` wires the degraded mode into the agent.
3. Read `EWMAAnomalyDetector` and the `atlas_budget_decisions_total` counter, and watch the guard degrade and refuse on a live `make run`.

### Script

[B-ROLL: the guards-off loop from lecture 1.1: the Live cost meter climbing to $4.90 for one conversation, the steps counter at 549.]

[AVATAR]

You've seen this clip. One looping conversation, five hundred forty-nine steps, four dollars ninety. A weekend of them is about forty-nine hundred dollars. [PAUSE] Everything we've done in this section makes the normal day cheaper. None of it stops an abnormal one. A budget does. And a budget that just says "no" at midnight is a budget nobody will let you ship. So we'll build one with two levels and an early warning.

[SLIDE 1: Two caps and a detector]
- Soft cap ($25 by default, rolling 24 h): degrade. Nano model, top-k 2. Users barely notice.
- Hard cap ($40 by default): refuse politely, before any model call. "Atlas has reached the budget for your department today; please open a ticket."
- EWMA anomaly: each request's cost vs. the tenant's smoothed history; `BudgetDecision.anomaly` is true above 3 standard deviations
- Everything emits a counter: `atlas_budget_decisions_total{tenant, decision}`, plus the gauge `atlas_budget_spent_usd{tenant}`

[AVATAR]

Two caps over a rolling twenty-four hours. At the soft cap, twenty-five dollars by default, degrade: the nano model, top-k two. The tenant keeps getting service, just the economy version. At the hard cap, forty dollars, refuse, politely, before any model call, and point the user at a ticket so nobody is stranded. And separately, a detector that watches each request's cost against the tenant's own smoothed history. A loop shows up as a run of anomalous requests in the first minutes, hours before the daily cap would.

[SLIDE 2: LiteLLM `BudgetManager` (concept) vs our `budget.py`]
- `BudgetManager(project_name=...)`: `create_budget(total_budget, user, duration)`, `update_cost(...)`, `get_current_cost(user)`, `projected_cost(...)`
- Great for per-user caps on a LiteLLM gateway
- Atlas needs: per-tenant, soft and hard levels, degraded mode, anomaly detection, offline tests
- So: same idea, our own `budget.py`, about 250 lines, unit-tested

[AVATAR]

LiteLLM ships a `BudgetManager`: create a budget per user with a duration, update cost after each call, read the current and projected cost. If you run a LiteLLM gateway, use it. Atlas needs the tenant dimension, two levels, a degraded mode and a detector, so we write our own, about two hundred fifty lines with the same shape, and test them offline.

[SCREEN: VS Code, `src/northwind/budget.py`]

[CODE: `src/northwind/budget.py` (excerpt)]

```python
class Decision(StrEnum):
    """What the request path should do."""

    ALLOW = "allow"
    DEGRADE = "degrade"
    REFUSE = "refuse"


@dataclass(frozen=True)
class TenantBudget:
    """Caps in USD over a rolling window (default: 24 h)."""

    tenant: str
    soft_cap_usd: float
    hard_cap_usd: float
    window_s: int = 86_400


@dataclass
class EWMAAnomalyDetector:
    """Exponentially weighted moving average with a running variance.

    ``update(x)`` returns a z-score-like deviation; ``is_anomaly(x)`` is True when
    the deviation exceeds ``threshold`` after ``warmup`` observations.
    """

    alpha: float = 0.3
    threshold: float = 3.0
    warmup: int = 5
    mean: float | None = None
    var: float = 0.0
    n: int = 0

    def deviation(self, x: float) -> float:
        """z-like score of ``x`` against the current state without updating."""
        if self.mean is None or self.n < self.warmup:
            return 0.0
        std = math.sqrt(self.var) if self.var > 0 else 0.0
        if std == 0:
            return 0.0 if x == self.mean else math.inf
        return (x - self.mean) / std

    def update(self, x: float) -> float:
        """Fold ``x`` in and return its deviation *before* the update."""
        dev = self.deviation(x)
        if self.mean is None:
            self.mean = x
            self.var = 0.0
        else:
            diff = x - self.mean
            self.mean += self.alpha * diff
            self.var = (1 - self.alpha) * (self.var + self.alpha * diff * diff)
        self.n += 1
        return dev

    def is_anomaly(self, x: float) -> bool:
        return self.deviation(x) > self.threshold


class BudgetGuard:
    """Tracks spend per tenant and decides allow / degrade / refuse."""

    def record(self, tenant: str, usd: float, ts: float) -> float:
        """Add a spend and return its anomaly deviation (z-like)."""
        self._window(tenant).add(usd, ts)
        return self._detector(tenant).update(usd)

    def decide(self, tenant: str, now: float, *, next_cost_usd: float = 0.0) -> BudgetDecision:
        """Decide for the *next* request. ``next_cost_usd`` may pre-charge an estimate."""
        b = self.budget_for(tenant)
        spent = self.spent(tenant, now)
        projected = spent + max(next_cost_usd, 0.0)
        anomaly = self._detector(tenant).is_anomaly(next_cost_usd) if next_cost_usd else False
        if projected >= b.hard_cap_usd:
            d, reason = Decision.REFUSE, f"hard cap {b.hard_cap_usd:.2f} USD reached"
        elif projected >= b.soft_cap_usd:
            d, reason = Decision.DEGRADE, f"soft cap {b.soft_cap_usd:.2f} USD reached"
        else:
            d, reason = Decision.ALLOW, "within budget"
        self.decisions.setdefault(tenant, {}).setdefault(d.value, 0)
        self.decisions[tenant][d.value] += 1
        return BudgetDecision(tenant, d, spent, b.soft_cap_usd, b.hard_cap_usd, reason, anomaly)


#: Short name used in the lecture scripts.
EwmaAnomaly = EWMAAnomalyDetector
```

`BudgetGuard.decide` is three comparisons on the projected spend: the rolling-window total plus an estimate for the request about to run. At or above the hard cap, refuse. At or above the soft cap, degrade. Otherwise allow. The spend comes from a `SpendWindow` per tenant, a rolling sum of the cost records from 6.3, fed by `record` after every request.

[SCREEN: zoom on `EWMAAnomalyDetector.update`; the `mean` and `var` lines highlighted]

`EWMAAnomalyDetector` is an exponentially weighted moving average with a running variance. Each new cost is compared with the smoothed mean plus three smoothed standard deviations. Five observations of warm-up so it doesn't fire at startup. Alpha zero point three means it forgets in about ten observations, so a slow Tuesday doesn't make Wednesday morning look like an attack. `EwmaAnomaly` is an alias, if you prefer the short name.

Now the wiring.

[SCREEN: `app/agent.py`, `run()`]

[CODE: `app/agent.py` (excerpt): the budget guard in `run()`]

```python
            # 2. budget guard ----------------------------------------------------------------
            if self.budget_guard is not None:
                decision = self.budget_guard.decide(
                    tenant, time.time(), next_cost_usd=self.budget_guard.estimate(tenant)
                )
                result.budget_decision = decision.decision.value
                root.set_attribute(ga.ATLAS_BUDGET_DECISION, decision.decision.value)
                metrics.BUDGET_DECISIONS.labels(tenant, decision.decision.value).inc()
                metrics.BUDGET_SPENT.labels(tenant).set(decision.spent_usd)
                if decision.decision is Decision.REFUSE:
                    result.answer, result.outcome = BUDGET_REFUSAL, "refused"
                    ga.add_event(root, "budget.refused", reason=decision.reason)
                    return self._finish(root, result, tenant, started)
                if decision.decision is Decision.DEGRADE:
                    ga.add_event(
                        root, "budget.degraded", reason=decision.reason, model=s.degraded_model
                    )
                    model, top_k = self._choose_deployment(intent, degraded=True), min(top_k, 2)
                    result.model = model
```

Before the loop, right after the injection guardrail, check the budget and count the decision. The estimate for the next request is the tenant's EWMA of past requests, so the projection is honest. Refuse answers with `BUDGET_REFUSAL`, records an event on the root span and never calls the model; the server turns that outcome into a 429. Degrade switches the request to the degraded model, gpt-4.1-nano, and caps top-k at two. `BUDGET_SPENT` is a gauge of the rolling spend per tenant, so Grafana can draw the two caps as lines, and the decision is on the root span as `atlas.budget.decision`. [PAUSE] Section 9 turns the counter and the gauge into alerts. Today we just make them exist.

[SLIDE 3: Setting the budgets (from the showback, 6.3)]

| Tenant | Baseline day | After the three levers | Daily budget (1.5× after) | Soft cap (80%) |
|---|---|---|---|---|
| ops | $20.27 | $5.97 | $9.00 | $7.20 |
| eng | $12.50 | $4.32 | $6.50 | $5.20 |
| finance | $11.91 | $4.49 | $6.75 | $5.40 |
| hr | $11.59 | $4.28 | $6.40 | $5.10 |

[AVATAR]

Where do the numbers come from? From the showback. Take each tenant's normal day after the levers, and set the budget at one and a half times that. Enough headroom for a busy Monday, tight enough that a loop hits the soft cap in under an hour. The repo ships one pair for every tenant, `TENANT_SOFT_CAP_USD=25` and `TENANT_HARD_CAP_USD=40`, sized for the baseline day so the incident labs can reach them; once your levers are in, tighten them from the report. [PAUSE] Budgets you invent get ignored. Budgets derived from the report get approved.

[SCREEN: two terminals side by side. Left: Atlas with deliberately tiny caps, two cents soft, four cents hard.]

Now break it. Live, with caps small enough to hit in a minute.

```bash
# terminal 1
OFFLINE=1 OTEL_EXPORTER=none TENANT_SOFT_CAP_USD=0.02 TENANT_HARD_CAP_USD=0.04 make run
```

```bash
# terminal 2: the same question from ops, 32 times
for i in $(seq 1 32); do
  curl -s -X POST localhost:8000/chat -H 'Content-Type: application/json' -H 'X-Tenant: ops' \
       -d '{"message": "When is payroll paid?"}' \
  | python -c "import json,sys; d=json.load(sys.stdin); d=d.get('detail', d); print(d['budget_decision'], d['model'], d['outcome'], d['cost_usd'])"
done
```

[DEMO: output (rows 6 to 26 are identical to row 5 and scroll past):]

```
allow gpt-4.1-mini resolved 0.004456
allow gpt-4.1-mini resolved 0.004456
allow gpt-4.1-mini resolved 0.004456
allow gpt-4.1-mini resolved 0.004456
degrade gpt-4.1-nano resolved 0.0009513
...
degrade gpt-4.1-nano resolved 0.0009513
refuse gpt-4.1-mini refused 0.0
refuse gpt-4.1-mini refused 0.0
refuse gpt-4.1-mini refused 0.0
refuse gpt-4.1-mini refused 0.0
refuse gpt-4.1-mini refused 0.0
```

Four requests at full price, under half a cent each. Then the projected spend crosses two cents and the guard degrades: same question, gpt-4.1-nano, a tenth of a cent, still resolved. Twenty-three economy answers later, the projection crosses four cents and the guard refuses before any model call: cost zero, HTTP 429, and the answer tells the user to open a ticket. [PAUSE] Nobody in ops was stranded, and the bill stopped where you said it would.

[SCREEN: terminal 2, then the Ops Console Budgets page]

```bash
curl -s localhost:8000/metrics/ | grep -E "^atlas_budget_(decisions_total|spent_usd)"
```

[DEMO: output:]

```
atlas_budget_decisions_total{decision="allow",tenant="ops"} 4.0
atlas_budget_decisions_total{decision="degrade",tenant="ops"} 23.0
atlas_budget_decisions_total{decision="refuse",tenant="ops"} 5.0
atlas_budget_spent_usd{tenant="ops"} 0.0397039
```

Four allow, twenty-three degrade, five refuse, and the rolling spend just under four cents. Those are the series Section 9 alerts on. `GET /budget` shows the same state per tenant as JSON.

Now the detector's job, on a full day. Replay the cost spike preset and open the Budgets page.

```bash
OFFLINE=1 make replay SCENARIO=cost_spike && make console      # Budgets page, tenant ops
```

[DEMO: Ops Console Budgets page, tenant ops: the cumulative spend line against the $25 soft and $40 hard cap lines; the anomaly table lists the 15-minute bins from 09:30 to 11:00, where cost per request is more than twice the tenant's median bin.]

The console's rule is simple: a fifteen-minute bin whose cost per request is more than twice the tenant's median. Ops lights up from half past nine to eleven, the morning context bloat that Incident 1 is built on. [PAUSE] And notice what doesn't happen: the line never bends. The replay writes spans straight into the store; it never goes through `BudgetGuard`. That's your unguarded comparison: ops spends twenty-eight ninety-eight that day against a normal twenty twenty-seven. To see the guard act, you run it live, as we just did.

[SLIDE 4: Two kinds of "abnormal"]
- `BudgetDecision.anomaly`: per request, EWMA, inside the guard; attach it to the span if you want it per trace
- Console Budgets page: 15-minute bins above 2× the tenant's median cost per request
- Prometheus (9.5): `AtlasTenantCostAnomaly`, hourly spend above 2.5× the previous day's average hour
- All three answer "is this abnormal?"; the caps answer "have we spent the money?"

[AVATAR]

So there are three detectors at three speeds: per request inside the guard, per fifteen minutes on the console, per hour in Prometheus. They answer "is this abnormal?" The caps answer a different question: "have we spent the money?" Keep both. And the unit tests pin the guard's behavior without any of the theatre: `uv run pytest tests/unit/test_budget.py` runs fourteen tests in a few hundredths of a second, including allow, degrade and refuse in one test and an hourly spike flagged by `hourly_anomalies`.

[SLIDE 5: Recap]
- Soft cap degrades to the nano model
- Hard cap refuses politely, before any model call
- Every decision is a Prometheus counter


### Recap

A soft cap degrades to the nano model, a hard cap refuses politely before any model call, the EWMA detector, the console's Budgets page and a Prometheus rule each flag abnormal spend at their own speed, and every decision is a Prometheus counter waiting for an alert.

### Transition

You now have four measured tools: caching, the diet, routing and budgets. Time to use them. In the next lecture you'll cut Atlas's day by forty percent, on your own, before I show you how I did it.

### Speaker notes: common mistakes and Q&A

- **Hard cap without a fallback.** Refusing with no way forward strands users and gets the budget removed within a week. `BUDGET_REFUSAL` tells the user how to reach a human; creating the ticket automatically is a good capstone extension.
- **Budget spend from Prometheus.** Counters reset on restart; compute spend from the cost store, and use the counter for alerting only.
- **EWMA warm-up and quiet hours.** Overnight requests near zero make the morning look anomalous. The detector warms up for five observations (`warmup`); a per-hour-of-day baseline or a minimum std floor are the two standard extensions. Mention both.
- **Anomaly vs budget.** They answer different questions: "is this abnormal?" vs "have we spent the money?". Keep both.
- **The live demo.** The guard lives in the server process: restart `make run` and the rolling spend starts from zero. A refused request comes back as HTTP 429 with the full response under `detail`, which is why the loop reads `d.get('detail', d)`. `/metrics` is a mounted app, so curl `/metrics/` (with the slash) or add `-L`.
- **Why refuse at $0.0397 and not $0.04?** `decide` projects the next request's cost (the tenant's EWMA) onto the rolling spend; refusing when the projection crosses the cap is what keeps the real spend under it.
- **Coding exercise.** The Udemy in-browser exercise "EWMA anomaly" is `EWMAAnomalyDetector` with stdlib only; point students to `06-assessments/coding-exercises.md`.

---

## Lecture 6.8: Challenge: cut Atlas's daily cost by 40%

| Field | Value |
|---|---|
| ID | 6.8 |
| Title | Challenge: cut Atlas's daily cost by 40% |
| Type | CH (pause-then-solution challenge) |
| Target duration | 7:00 (about 580 spoken words at ~140 wpm; the student pause is off-video, 30 to 60 minutes) |
| One idea | Take the $56.28 replayed day below $33.77 using the levers from this section, prove it in the Ops Console, and prove quality held. |
| Prerequisites | 6.1 to 6.7 |
| Files used | `simulator/replay.py`, `src/northwind/config.py`, Ops Console Compare replays page, `05-projects/challenges.md` |

**Learning objectives**

1. Combine caching, the context diet and routing on the same replayed day and read the result from the Ops Console.
2. Prove the saving with before and after figures per tenant and per feature, and prove quality with the resolved and grounded scores.
3. Recognise that the levers stack, and that the order you apply them changes what you learn.

### Script

[AVATAR]

Here's the brief, and then I'm going to stop talking. [PAUSE] Atlas's replayed day costs fifty-six dollars twenty-eight. Get it under thirty-three seventy-seven, a forty percent cut, without the resolved score dropping more than two points. Prove it on the Ops Console with before and after. You have every tool you need from the last six lectures.

[SLIDE 1: The challenge]
- Start: `OFFLINE=1 make replay` on seed 7 → $56.28, resolved 0.892, grounded 0.943
- Target: ≤ $33.77 (−40%), resolved ≥ 0.872, grounded ≥ 0.923
- Allowed: anything in `src/northwind/config.py` and `app/`: caching, history and tool budgets, top-k, routing thresholds, budgets
- Not allowed: dropping traffic, refusing requests, changing the seed
- Deliver: a screenshot of the console's Compare replays page (one `.atlas/*.sqlite` per configuration) and one paragraph on what you changed and why
- Full spec: `05-projects/challenges.md`, Challenge 6.8

[AVATAR]

Three rules. You can change configuration and agent code. You can't make the day smaller by serving fewer requests or refusing them; the hard cap doesn't count as a saving. And you can't change the seed. Same day, cheaper.

One hint. [PAUSE] Apply one lever at a time and replay after each. The order you choose will teach you something the final number won't.

Pause the video now. Thirty to sixty minutes. Come back when the console says thirty-three seventy-seven or less.

[SLIDE 2: PAUSE. Come back with a number.]

[PAUSE: 5 seconds of the slide, then a title card "Reference solution"]

[AVATAR]

You're back. Here's how I did it, one lever at a time, in the order I'd do it in production.

[SCREEN: terminal and Ops Console side by side]

```bash
OFFLINE=1 make replay                     STORE=.atlas/base.sqlite         # baseline
OFFLINE=1 make replay CACHE=1             STORE=.atlas/cache.sqlite        # + caching
OFFLINE=1 make replay CACHE=1 DIET=1      STORE=.atlas/cache_diet.sqlite   # + context diet
OFFLINE=1 make replay CACHE=1 DIET=1 ROUTER=1 STORE=.atlas/all3.sqlite     # + routing
make console                                                               # Compare replays: pick all four stores
```

[SLIDE 3: Reference solution, one lever at a time (verify current pricing)]

| Step | Day | Saving vs baseline | Resolved | Grounded |
|---|---|---|---|---|
| Baseline | $56.28 | | 0.892 | 0.943 |
| + Caching (`CACHE=1`: `prompt_cache_key`, stable prefix) | $37.00 | −34.3% | 0.892 | 0.943 |
| + Context diet (`DIET=1`: tool results 1,400, history 8,000) | $22.71 | −59.6% | 0.892 | 0.943 |
| + Routing (`ROUTER=1`: nano for simple intents) | **$19.07** | **−66.1%** | **0.892** | 0.943 |

[AVATAR]

Caching first, because it changes nothing about the answers. Thirty-four percent, and every quality score is identical to the decimal. That's why I do it first: it's the lever with no quality risk, and it tells you how much of the remaining bill is genuinely new tokens.

Then the diet. Down to twenty-two seventy-one, sixty percent. Target passed.

[SCREEN: the Compare replays page, the `cache_diet.sqlite` row highlighted: cost, Δ%, cache ratio 68%, judge unchanged]

The grounded score didn't move, because a fourteen-hundred-token cap still holds the passage the answer needs. Push the tool budget to four hundred, or top-k to one, and the mock still answers, but a real model starts missing the exception clauses, and grounded is where you'd see it. That's the lesson the order teaches: the diet is where quality can move, so measure it there.

Then routing. Nineteen oh seven, sixty-six percent, and the scores hold, because the requests that moved to nano are the ones where the answer is a tool result read back. [PAUSE] Fifty-six dollars to nineteen. About five hundred seventy a month instead of seventeen hundred. About thirteen and a half thousand a year, on a helpdesk for four departments, with the answers as good.

[SLIDE 4: After, by tenant and by feature]

| Tenant | Before | After | | Feature | Before | After |
|---|---|---|---|---|---|---|
| ops | $20.27 | $5.97 | | policy_question | $42.91 | $17.56 |
| eng | $12.50 | $4.32 | | create_ticket | $6.66 | $0.64 |
| finance | $11.91 | $4.49 | | ticket_lookup | $3.21 | $0.30 |
| hr | $11.59 | $4.28 | | shipment_status | $2.21 | $0.19 |
| | | | | password_reset | $0.78 | $0.25 |

[AVATAR]

By tenant, everyone saved a similar share: ops the most, seventy-one percent, because dispatchers ask the simple questions that now run on nano; the other three sixty-two to sixty-five. By feature, the tool-driven requests saved the most: ticket lookups, ticket creation and shipment checks are down ninety percent, cached prefix plus nano. Policy questions saved the least, fifty-nine percent, because their cost is retrieved policy text that the diet caps but can't remove, on mini on purpose. [PAUSE] That table is your one paragraph: the saving is structural, it's largest where the request was simplest, and it cost nothing in quality.

[SLIDE 5: Common ways to hit 40% the wrong way]
- Top-k 1 or a 200-token tool budget: cost drops; on a real model, grounded drops with it
- Policy questions on nano too: more saved, and the exception clauses go missing on a real model
- A 300-token history budget: sessions lose the thread on turn 3; multi-turn resolved drops
- Tiny hard caps: the day "costs" less because sessions got refused (not allowed)
- Illustrative: the mock scores answer text, so these failures show on a real model, not on the replay

[AVATAR]

Four wrong ways to hit the number, and I've seen all of them. Starving retrieval. Putting policy questions on the smallest model. Cutting history so hard that turn three forgets turn one. And the budget trick, where the day looks cheap because sessions got refused. [PAUSE] Every one of them passes the cost test and fails the quality test, on a real model. The mock judge won't catch the first three, which is exactly why the rules forbid them instead of trusting the score. Which is why the challenge had two numbers, and why the console shows them side by side.

[AVATAR]

If you got under thirty-three seventy-seven with quality intact, post your before and after in the Q&A with the one-paragraph explanation. If you got there a different way than I did, I especially want to see it.

[SLIDE 6: Recap]
- Caching first: no quality risk
- Then the diet, where quality can move
- Then routing: $56.28 becomes $19.07

### Recap

Caching, then the diet, then routing, each measured on the same replayed day, take Atlas from $56.28 to $19.07 with resolved and grounded scores intact, and the order teaches you where quality can move.

### Transition

You've done the engineering. Now turn it into the document that gets you the budget: Project 1, the showback report.

### Speaker notes: common mistakes and Q&A

- **Stale spec.** If `05-projects/challenges.md` still shows a different seed or dollar figures, the numbers card wins: seed 7, $56.28, target $33.77.
- **Students who only cache and call it done.** 34% is short of 40% on purpose, so the challenge needs at least two levers. Say so in the solution if the Q&A shows confusion.
- **"My numbers differ slightly."** The replay is deterministic per seed; the cache hit rate is simulated by the mock LLM (`CACHE_MIN_PREFIX`, 128-token blocks in `app/mock_llm.py`) and is not a setting. A student who edits the mock has changed the world, not the agent; that must be declared. Also: `python simulator/replay.py` without the Makefile uses the `.env` defaults, where cache and diet are already on.
- **Quality scores on the replay.** They come from the offline judge (`evals/online_judge.py::OfflineJudge`) on sampled traces. Students who haven't reached Section 8 see them on the console anyway.
- **Order.** Any order reaches the same final number. The order changes the intermediate rows, which is where the learning is.

---

## Lecture 6.9: Project 1: The showback report

| Field | Value |
|---|---|
| ID | 6.9 |
| Title | Project 1: The showback report |
| Type | AS (assignment; text lecture with a short video intro) |
| Target duration | Video 3:00 (about 330 spoken words at ~140 wpm, plus slide time); project work 2 to 3 hours off-video |
| One idea | Produce the weekly cost report by tenant and feature, with cost per resolved session and three recommendations, in a form finance would accept. |
| Prerequisites | 6.1 to 6.8 |
| Files used | `05-projects/project-1-showback-report.md`, `src/northwind/report.py`, `simulator/replay.py` |

**Learning objectives**

1. Replay the day and run `make report` (`northwind.report.weekly_report`: headline numbers, SLOs, cost by tenant, by feature and by model).
2. Write three recommendations that each cite a number from the report and estimate a saving.
3. Present cost per resolved session as the headline metric.

### Script

[AVATAR]

Project one is the document that turns this section into budget. A one-page weekly showback report, the kind a finance partner reads without calling you.

[SCREEN: terminal: `OFFLINE=1 make replay` then `make report`; scroll to "Cost by feature"]

```bash
OFFLINE=1 make replay && make report
```

[DEMO: the "Cost by feature" section of the report (trimmed):]

```
| feature | requests | sessions | tokens in | tokens out | cache hit | cost (USD) | cost/session | share |
| policy_question | 6420 | 2976 | 99,440,908 | 1,960,774 | 0% | 42.9136 | 0.0144 | 76.2% |
| create_ticket | 1539 | 1194 | 15,834,501 | 204,797 | 0% | 6.6615 | 0.0056 | 11.8% |
| ticket_lookup | 1048 | 396 | 7,500,983 | 130,432 | 0% | 3.2091 | 0.0081 | 5.7% |
| shipment_status | 716 | 459 | 5,229,001 | 73,491 | 0% | 2.2092 | 0.0048 | 3.9% |
```

Replay the day with `make replay` and render the report with `make report`, which runs `weekly_report` over the local store. You get the headline numbers, the SLOs, and three showback tables: by tenant, by feature and by model. The replayed day stands in for the week, and the Makefile flags with `STORE=` give you the other configurations for the comparison rows.

[SCREEN: `05-projects/project-1-showback-report.md`: the brief and rubric.]

The report must show total cost, cost per session, cost per resolved session, and the trend across the configurations. Then three recommendations. Each one has to cite a number from your report and estimate the saving in dollars per month. "Turn on the context diet" is not a recommendation. "Policy questions are seventy-six percent of the bill; the diet replay takes the day from fifty-six twenty-eight to forty-one ninety-nine, about four hundred thirty dollars a month, with grounded unchanged at point nine four" is.

[SLIDE 1: Project 1 rubric]
- Report by tenant and by feature, with the trend across configurations: 40%
- Cost per resolved session as headline, with the resolved rate stated: 20%
- Three recommendations, each with a cited number and a monthly saving: 30%
- Prices marked with a date and "verify current pricing": 10%

[AVATAR]

The rubric's biggest points go to the recommendations, because that's the part finance can act on. And ten percent for something small: the prices in your report carry a date and the words "verify current pricing." A report that's honest about its constants is one people trust.

Post the markdown, or a screenshot of it, in the Q&A. The best ones get featured.

[SLIDE 2: You can now]
- Price every generation and trace every dollar to a tenant and feature
- Cut a day's cost 66% with caching, the diet and routing
- Cap a tenant's spend without stranding its users

### Recap

Project 1 is the weekly showback report by tenant and feature, headlined by cost per resolved session, with three numbered recommendations.

### Transition

Before you start the project, check your understanding with the Section 6 quiz.

### Speaker notes: common mistakes and Q&A

- **Recommendations without numbers.** The most common failure. Send them back to the feature table.
- **Reporting cost per session only.** Insist on cost per resolved session with the resolved rate beside it.
- **Undated prices.** Ten percent of the grade, on purpose.
- **Comparison rows.** Each configuration needs its own store (`make replay CACHE=1 STORE=.atlas/cache.sqlite`, then `make report STORE=.atlas/cache.sqlite`); without `STORE=` every replay clears `.atlas/spans.sqlite`.

---

## Lecture 6.10: Quiz: Cost engineering

| Field | Value |
|---|---|
| ID | 6.10 |
| Title | Quiz: Cost engineering |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:30 (about 170 spoken words at ~140 wpm, plus slide time) |
| One idea | Check you can compute a cost from usage fields, and choose and justify each cost lever. |
| Prerequisites | 6.1 to 6.8 |
| Files used | `06-assessments/quizzes/section-06.md` (8 questions) |

**Learning objectives**

1. Compute the cost of a generation from `prompt_tokens`, `completion_tokens` and `cached_tokens`.
2. Match a cost symptom to the right lever: caching, diet, routing or budget.

### Script

[AVATAR]

Eight questions. Two of them are arithmetic, and you'll want the price table open: forty cents, a dollar sixty, ten cents per million for gpt-4.1-mini, as of the recording date. You'll be given a usage object with cached tokens and asked for the cost, so remember which number is a subset of which. Two questions on caching: what breaks a prefix match, and what belongs in a `prompt_cache_key`. Two on the diet and routing: which lever for which symptom. And two on budgets: what the soft cap does, and what the EWMA detector compares.

[SLIDE 1: Quiz: 8 questions]
- Cost arithmetic with cached and reasoning tokens
- Caching: prefix order and cache keys
- Diet vs routing: matching symptom to lever
- Budgets: soft, hard and anomaly

[AVATAR]

One tip. When a question gives you a bill, ask first: which token stream is biggest? For an agent, it's almost always input. The answer follows from that.

Every answer links back to its lecture.

### Recap

The quiz checks that you can compute a generation's cost correctly and pick the right lever for a cost symptom.

### Transition

Cost is one half of the operating bill. Next section: latency and reliability, where the same traces tell you where the time went.

### Speaker notes: common mistakes and Q&A

- Most-missed: the cost question with `cached_tokens`. Students add cached to prompt tokens instead of subtracting.
- Second: "Which lever changes no answers?" Caching. Students often pick routing.
