# Section 6: Cost Engineering (signature section)

> **Course:** AI Agent Observability & Cost Control: LLMOps in Production with OpenTelemetry & Langfuse
> **Section runtime:** about 70 minutes (10 lectures, including one challenge, one project intro and one quiz intro)
> **Running example:** Atlas, the IT and HR helpdesk agent at Northwind Logistics, with four departments as tenants (`operations`, `warehouse`, `finance`, `sales`)
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues. Terminal font at 18 pt minimum. Every dollar figure on screen gets a callout.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on litellm 1.103 / langfuse 4.15 / openai 2.54. Prices as of 2026-09-28: verify current pricing."
> **Recording note (from the curriculum):** split 6.3 and 6.6 into Part A / Part B uploads to keep each video under ten minutes.

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (to match `03-code/`):** `northwind.pricing` (`FALLBACK_PRICES`, `get_price`, `cost_usd`), `northwind.cost` (`CostRecord`, `rollup`, `showback`), `northwind.tokens` (`estimate_tokens`, `trim_history`, `truncate_tool_result`), `northwind.budget` (`TenantBudget`, `BudgetGuard`, `Decision`, `EwmaAnomaly`), `app.agent.AtlasAgent` (`mode="direct"` or `mode="router"`, `prompt_cache_key`), `telemetry.metrics` (`LLM_COST`, `LLM_TOKENS`, `BUDGET_EVENTS`), `simulator/replay.py`, `console/ops_console.py`. If the repo names differ when you record, the repo wins; update the on-screen code, not the numbers.

**The numbers card (one set of figures for the whole section; every lecture reconciles to it):**

| Item | Value |
|---|---|
| Traffic on the replayed day | 10,000 requests in 4,000 sessions, 3 LLM steps per request on average |
| Baseline tokens per request (gpt-4.1-mini) | steps of 2,480 / 4,040 / 4,220 input tokens = 10,740 input; 60 + 60 + 220 = 340 output |
| Baseline cost per request (mini only) | 10,740 × $0.40/M + 340 × $1.60/M = $0.004296 + $0.000544 = **$0.00484** |
| Retries | 4% of steps re-issued: 1,200 generations, **$2.05** |
| Escalations | 10% of requests re-run the final step on gpt-4.1 (4,220 in / 300 out): 1,000 × $0.01084 = **$10.84** |
| **Baseline day** | $48.40 + $2.05 + $10.84 = **$61.29**, so $0.0153 per session, about $1,840 a month, about $22,400 a year |
| Caching alone (70% hit rate) | **$39.58** (−35%) |
| Context diet alone | **$46.79** (−24%) |
| Routing alone | **$52.42** (−15%) |
| All three | **$24.86** (−59%), $0.0062 per session, about $750 a month |
| Prices used (verify current pricing) | gpt-4.1-mini $0.40 in / $1.60 out / $0.10 cached per 1M; gpt-4.1 $2.00 / $8.00 / $0.50 |

---

## Lecture 6.1: Where the money goes: token anatomy

| Field | Value |
|---|---|
| ID | 6.1 |
| Title | Where the money goes: token anatomy |
| Type | SL (slides + avatar) |
| Target duration | 7:00 (about 760 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | An agent's bill is made of six token streams, and the biggest one is the input you re-send on every step. |
| Prerequisites | Sections 2 to 5 (you can read a trace with usage on it) |
| Files used | Diagram "token anatomy of one Atlas request"; `console/ops_console.py` cost page |

**Learning objectives**

1. Name the six token streams that make up an agent's cost: uncached input, cached input, output, reasoning, retries and judge calls.
2. Read the OpenAI usage fields that report each stream (`prompt_tokens_details.cached_tokens`, `completion_tokens_details.reasoning_tokens`, and their Responses API equivalents).
3. Explain why a three-step agent pays for its prompt three times, and estimate the share of cost that is input.

### Script

[B-ROLL: the Ops Console cost page. A single Atlas request expands into three generation rows. The input column reads 2,480, then 4,040, then 4,220. A running total at the bottom ticks up to $0.0048.]

[AVATAR]

One question. One answer. Three model calls. [PAUSE] Look at the input column: two thousand four hundred, then four thousand, then four thousand two hundred. The user typed eighty tokens. Atlas sent the model ten thousand seven hundred. That's the shape of every agent bill I have ever seen, and by the end of this lecture you'll be able to read it like a receipt.

[SLIDE 1: The six token streams]
- Uncached input: what you send, at full price
- Cached input: the same prefix, seen recently, at a discount
- Output: what the model writes, including tool-call arguments
- Reasoning: hidden thinking on reasoning models, billed as output
- Retries: the same step, paid again
- Judge calls: the model you pay to grade the model

[AVATAR]

Six streams. The first three are on every invoice. Uncached input is what you send at full price. Cached input is a prefix the provider has seen in the last few minutes, billed at a quarter of the price. Output is everything the model writes, and that includes the JSON arguments of a tool call. Then three streams people forget. Reasoning tokens, which reasoning models spend thinking and bill as output. Retries, where you pay for the same step twice. And judge calls, which we'll add in Section 8, where you pay a second model to grade the first one.

Here's the question for the whole section. [PAUSE] Which stream is biggest for Atlas? Let's find out with real numbers.

[SLIDE 2: One Atlas request, step by step (baseline)]

| Step | What is in the prompt | Input tokens | Output tokens |
|---|---|---|---|
| 1 | system + tools + policy (1,800), history (600), question (80) | 2,480 | 60 (tool call) |
| 2 | step 1 again + tool call + `search_knowledge_base` result (1,500) | 4,040 | 60 (tool call) |
| 3 | step 2 again + `lookup_ticket` result (120) | 4,220 | 220 (answer) |
| Total | | **10,740** | **340** |

[AVATAR]

Step one. Atlas sends the system prompt, the five tool schemas and the policy snippets. That prefix is about eighteen hundred tokens. Plus six hundred tokens of conversation history and the eighty-token question. Two thousand four hundred eighty in. The model answers with a sixty-token tool call.

Step two. Here's the part that surprises people. The model has no memory. So Atlas sends everything from step one again, plus the tool call, plus the fifteen-hundred-token knowledge base result. Four thousand and forty in.

Step three. Everything again, plus a small ticket lookup. Four thousand two hundred twenty in, and finally a two-hundred-twenty-token answer for the user.

Add it up. Ten thousand seven hundred forty input tokens. Three hundred forty output. [PAUSE] The prefix alone was sent three times: fifty-four hundred tokens for eighteen hundred tokens of actual content.

[SLIDE 3: What that costs (gpt-4.1-mini, verify current pricing)]
- Input: 10,740 × $0.40 per million = $0.004296
- Output: 340 × $1.60 per million = $0.000544
- Total: $0.00484 per request
- Input is 89% of the cost
- 10,000 requests a day: $48.40 a day before retries and escalations

[AVATAR]

Now the money. At forty cents per million input tokens, the input costs four tenths of a cent. Output is four times the price per token, but there's thirty times less of it, so it's a twentieth of a cent. Total: just under half a cent per request. And eighty-nine percent of it is input.

That's the answer to the question. For a tool-calling agent, the bill is input. Not the clever answer at the end. The re-sent context in the middle. Which is why the three levers in this section, caching, the context diet and routing, all attack input first.

[SLIDE 4: The full day (baseline)]
- 10,000 requests, 4,000 sessions, 3 steps each: $48.40
- Retries: 4% of steps run twice, 1,200 extra generations: $2.05
- Escalations: 10% of requests re-run the final step on gpt-4.1: $10.84
- Day: $61.29 · Session: $0.0153 · Month: about $1,840 · Year: about $22,400

[AVATAR]

Scale it to Atlas's replayed day. Ten thousand requests, forty-eight dollars forty. Then the forgotten streams. Four percent of steps get retried after a tool error, and each retry re-sends the whole four-thousand-token prompt: two dollars. And one in ten requests escalates the final step to gpt-4.1, which is five times the price per token. That's ten dollars eighty-four, more than a sixth of the bill, from a tenth of the traffic.

Sixty-one dollars twenty-nine a day. A cent and a half per session. About eighteen hundred a month. [PAUSE] Not scary yet. Section one's four-thousand-dollar weekend was a loop. This is the normal day, and normal days are where the savings live, because you can plan them.

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

So here's the plan. First a price table you can trust, then attribution, so every one of those sixty-one dollars has a tenant and a feature on it. Then the three levers, each measured on the same day of traffic. Then budgets so it can't run away. And in 6.8 you'll take the sixty-one dollar day and cut it by forty percent yourself, before I show you my version. [PAUSE] Keep the number in your head: sixty-one twenty-nine.

### Recap

An agent's bill is six token streams, and for a tool-calling agent about nine tenths of it is input, because every step re-sends the whole prompt.

### Transition

Next, the price table. If the prices are wrong, every number after this is wrong, so we'll pin them and test them.

### Speaker notes: common mistakes and Q&A

- **"Isn't output the expensive part?"** Per token, yes, four times. Per request, no: Atlas sends thirty times more input than output. Always look at the product, price times volume.
- **Double-counting cached tokens.** `cached_tokens` is inside `prompt_tokens`. Students who add them get a bill that is too high, and then "save" money by fixing the bug.
- **Reasoning tokens.** gpt-4.1-mini reports zero. If a student swaps in a reasoning model such as `gpt-5-mini`, the output count jumps and they need to know why.
- **Tool-call overhead.** Tool schemas are input tokens on every step. Five tools cost about 600 tokens per step here; fifty tools would be a bill of their own.
- **Prices move.** Say it on camera: verify current pricing. The math is the lesson; the constants are the moment.

---

## Lecture 6.2: Code-along: a price table you can trust

| Field | Value |
|---|---|
| ID | 6.2 |
| Title | Code-along: a price table you can trust |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 650 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Take prices from `litellm.model_cost`, pin a fallback table with a date, and put the per-token math in one tested function. |
| Prerequisites | 6.1; `uv sync` done |
| Files used | `src/northwind/pricing.py`, `tests/unit/test_pricing.py` |

**Learning objectives**

1. Read a model's prices from `litellm.model_cost` and know which keys matter: `input_cost_per_token`, `output_cost_per_token`, `cache_read_input_token_cost`.
2. Write `cost_usd(model, input_tokens, output_tokens, cached_tokens)` with correct handling of cached and reasoning tokens.
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

Three sources, one function. LiteLLM ships a price table for hundreds of models, updated with the library. We read from it first. Behind it sits our own fallback: a small dictionary with a date in a comment, so offline mode and tests never depend on the network or on a library upgrade. And there's room for overrides, for negotiated rates. Everything funnels into one function, `cost_usd`. Nothing else in the repo multiplies tokens by prices. That's the rule that would have saved that team.

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
from dataclasses import dataclass

# USD per 1M tokens. Pinned 2026-09-28. VERIFY CURRENT PRICING before you trust a report.
FALLBACK_PRICES: dict[str, dict[str, float]] = {
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60, "cached_input": 0.10},
    "gpt-4.1":      {"input": 2.00, "output": 8.00, "cached_input": 0.50},
    "gpt-5-mini":   {"input": 0.25, "output": 2.00, "cached_input": 0.025},
}


@dataclass(frozen=True)
class Price:
    """USD per single token."""
    input: float
    output: float
    cached_input: float


def get_price(model: str, *, prefer_litellm: bool = True) -> Price:
    if prefer_litellm:
        try:
            import litellm
            row = litellm.model_cost[model]
            return Price(
                input=row["input_cost_per_token"],
                output=row["output_cost_per_token"],
                cached_input=row.get("cache_read_input_token_cost", row["input_cost_per_token"]),
            )
        except (ImportError, KeyError):
            pass
    p = FALLBACK_PRICES[model]  # KeyError on purpose: an unknown model must fail loudly
    return Price(p["input"] / 1e6, p["output"] / 1e6, p["cached_input"] / 1e6)


def cost_usd(model: str, input_tokens: int, output_tokens: int,
             cached_tokens: int = 0, reasoning_tokens: int = 0) -> float:
    """Cost of one generation. cached_tokens is a subset of input_tokens;
    reasoning_tokens is a subset of output_tokens and is billed as output."""
    p = get_price(model)
    uncached = max(input_tokens - cached_tokens, 0)
    usd = uncached * p.input + cached_tokens * p.cached_input + output_tokens * p.output
    return round(usd, 8)
```

Walk through it. `FALLBACK_PRICES` is per million, because that's how price pages read, with the date and the warning in the comment. `Price` is per token, because that's how you multiply. `get_price` tries LiteLLM first, and if the model isn't there, falls back. [PAUSE] Notice what it does not do: it does not return zero for an unknown model. A `KeyError` is the right behavior. A silent zero is how a new model runs for a month at no apparent cost.

`cost_usd` is the whole lesson from last lecture in four lines. Uncached input at full price. Cached input at the discount. Output at the output price. `reasoning_tokens` is a parameter so the call site is honest about it, but it adds nothing, because it's already inside `output_tokens`.

[SCREEN: terminal]

Let's check it against the numbers from 6.1, and against LiteLLM's own calculator.

```bash
uv run python -c "
from northwind.pricing import cost_usd
print(cost_usd('gpt-4.1-mini', 2480, 60))
print(cost_usd('gpt-4.1-mini', 1200, 180, cached_tokens=900))
print(cost_usd('gpt-4.1', 4220, 300))
import litellm
print(litellm.cost_per_token(model='gpt-4.1-mini', prompt_tokens=1200, completion_tokens=180, cache_read_input_tokens=900))
"
```

[DEMO: prints `0.001088`, `0.000858`, `0.01084`, then `(0.00021, 0.000288)`]

Step one of the Atlas request: a tenth of a cent. A cached example: twelve hundred in, nine hundred of them cached, one eighty out. Twelve hundred minus nine hundred is three hundred uncached at forty cents, nine hundred at ten cents, one eighty at a dollar sixty. Eighty-six thousandths of a cent. And LiteLLM agrees: `cost_per_token` returns the input part and the output part as a tuple. Twenty-one thousandths of a cent input, and the same output figure. [PAUSE] Two independent calculators, same answer. That's the moment you can trust the function.

The third line is the escalation step from 6.1: four thousand two hundred twenty into gpt-4.1, three hundred out. One point zero eight cents. Ten times the mini step. Remember that for 6.6.

[CODE: `tests/unit/test_pricing.py` (excerpt)]

```python
import pytest
from northwind.pricing import FALLBACK_PRICES, cost_usd, get_price


def test_fallback_matches_litellm_within_tolerance():
    litellm = pytest.importorskip("litellm")
    for model, p in FALLBACK_PRICES.items():
        row = litellm.model_cost[model]
        assert row["input_cost_per_token"] == pytest.approx(p["input"] / 1e6, rel=0.01)
        assert row["output_cost_per_token"] == pytest.approx(p["output"] / 1e6, rel=0.01)


def test_cached_tokens_are_a_subset_of_input():
    full = cost_usd("gpt-4.1-mini", 1200, 180)
    cached = cost_usd("gpt-4.1-mini", 1200, 180, cached_tokens=900)
    assert cached < full
    assert cached == pytest.approx(300 * 0.40e-6 + 900 * 0.10e-6 + 180 * 1.60e-6)


def test_unknown_model_fails_loudly():
    with pytest.raises(KeyError):
        get_price("gpt-imaginary")
```

Three tests, and the first one is the one that would have saved that team. It compares our pinned table to LiteLLM's on every test run. The day the library ships a new price, this test goes red, and someone has to look at the price page and update the date. [PAUSE] That's a price change becoming a code review instead of a surprise. The second test pins the cached-subset rule. The third pins the loud failure.

[SCREEN: terminal, `uv run pytest tests/unit/test_pricing.py -q`]

[DEMO: 3 passed]

[AVATAR]

One more thing about rounding. Store cost in USD as a float with eight decimals per generation, and sum before you round for display. Rounding each generation to cents and then summing ten thousand of them gives you a report that is off by dollars. We display cents; we never store them.

### Recap

Read prices from `litellm.model_cost`, pin a dated fallback table with a test that compares the two, and let one function, `cost_usd`, do all the arithmetic, with cached tokens as a subset of input.

### Transition

Now that every generation can have a price, let's put a tenant, a user and a feature on each one and roll them up into the report finance actually wants.

### Speaker notes: common mistakes and Q&A

- **"Why not just use `litellm.completion_cost(response)`?"** Use it when you have a LiteLLM response object. Atlas also runs offline and computes cost from span attributes, so a pure function over token counts is the common denominator. Show both agree, as in the demo.
- **`cache_read_input_token_cost` missing for a model.** The `.get` falls back to full price, which overstates cost rather than understating it. Say why that direction is the safe one.
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
| Target duration | 9:00 (about 720 spoken words at ~140 wpm; remaining time is on-screen code, runs and the report) |
| One idea | Attach cost to every generation together with tenant, user, session and feature, then roll up, so the same sixty-one dollars can be sliced any way finance asks. |
| Prerequisites | 6.2; Section 4 (sessions, users, tags) |
| Files used | `src/northwind/cost.py`, `src/northwind/report.py`, `app/agent.py`, `telemetry/langfuse_setup.py`, `console/ops_console.py` |

**Learning objectives**

1. Record a `CostRecord` per generation with `trace_id`, `session_id`, `user_id`, `tenant`, `feature`, `model`, token counts and `usd`.
2. Push the same numbers to Langfuse with `update_current_generation(usage_details=..., cost_details=...)`.
3. Roll up by any dimension with `rollup`, and produce the showback table with cost per resolved session.

### Script

[AVATAR]

Your CFO asks one question: "What does the helpdesk agent cost per department?" [PAUSE] If your answer is "sixty-one dollars a day, total," you've just told them you don't know. If your answer is a table with four rows, cost per session, and a trend, you've just been given budget for the next quarter. Same data. The difference is attribution.

[SLIDE 1: Five dimensions, one record]
- Request: one `trace_id`
- Session: one conversation, `session_id`
- User: one employee, `user_id` (hashed in telemetry, Section 10)
- Tenant: one department, `tenant` tag
- Feature: the intent Atlas served: `policy_question`, `ticket_lookup`, `create_ticket`, `password_reset`, `shipment_status`
- Every generation carries all five plus tokens and `usd`

[AVATAR]

Five dimensions. Request, session, user, tenant, feature. The trick is that you don't compute five reports. You stamp all five onto every generation, once, at the moment it happens. Then any report is a group-by. Let's see the record.

[SCREEN: VS Code, `src/northwind/cost.py`]

[CODE: `src/northwind/cost.py` (excerpt)]

```python
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Iterable

from northwind.pricing import cost_usd


@dataclass(frozen=True)
class CostRecord:
    trace_id: str
    session_id: str
    user_id: str          # hashed employee id
    tenant: str           # operations | warehouse | finance | sales
    feature: str          # policy_question | ticket_lookup | create_ticket | password_reset | shipment_status
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
    step: int = 0
    resolved: bool | None = None   # filled in later by feedback or the judge

    @property
    def usd(self) -> float:
        return cost_usd(self.model, self.input_tokens, self.output_tokens, self.cached_tokens)


def rollup(records: Iterable[CostRecord], by: str) -> dict[str, dict[str, float]]:
    """Sum usd and tokens grouped by one field, e.g. by='tenant'."""
    out: dict[str, dict[str, float]] = defaultdict(lambda: {"usd": 0.0, "input": 0, "output": 0, "cached": 0, "generations": 0})
    for r in records:
        key = getattr(r, by)
        row = out[key]
        row["usd"] += r.usd
        row["input"] += r.input_tokens
        row["output"] += r.output_tokens
        row["cached"] += r.cached_tokens
        row["generations"] += 1
    return dict(out)


def cost_per_session(records: Iterable[CostRecord]) -> dict[str, float]:
    sessions: dict[str, float] = defaultdict(float)
    for r in records:
        sessions[r.session_id] += r.usd
    return dict(sessions)
```

`CostRecord` is one generation. Tokens, model, and the five dimensions. `usd` is a property, so the price function from 6.2 runs on read and nobody stores a stale number. `rollup` groups by any field name. `by="tenant"` gives the CFO's table. `by="feature"` tells engineering which intent to optimize first. `by="model"` tells you what the escalation model is really costing.

And `by="user_id"`. That one deserves a word. The user id here is a keyed hash, which Section 10 explains, so the report can say "twenty employees account for eighteen percent of spend" without naming anyone. That's a real finding on the replayed day: a handful of people in operations use Atlas as a shipment tracker, forty times a day each. Not misuse. But it's a feature request for a cheaper `check_shipment` path, and you only see it at the user level. [PAUSE] Do that rollup in the report, from the span store. Never as a Prometheus label.

Where do the records come from? The agent loop.

[SCREEN: `app/agent.py`, the generation step]

[CODE: `app/agent.py` (excerpt, inside the step loop)]

```python
usage = response.usage
cached = getattr(getattr(usage, "prompt_tokens_details", None), "cached_tokens", 0) or 0
record = CostRecord(
    trace_id=lf.get_current_trace_id() or "", session_id=ctx.session_id, user_id=ctx.user_hash,
    tenant=ctx.tenant, feature=ctx.feature, model=response.model,
    input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens,
    cached_tokens=cached, step=step,
)
self.cost_sink.append(record)           # local store in OFFLINE mode, otherwise the exporter

lf.update_current_generation(
    model=response.model,
    usage_details={"input": usage.prompt_tokens, "output": usage.completion_tokens,
                   "cache_read_input_tokens": cached},
    cost_details={"input": cost_usd(response.model, usage.prompt_tokens - cached, 0),
                  "output": cost_usd(response.model, 0, usage.completion_tokens),
                  "cache_read_input_tokens": cached * get_price(response.model).cached_input},
)
LLM_COST.labels(model=response.model, tenant=ctx.tenant, feature=ctx.feature).inc(record.usd)
```

Three destinations, one moment. The `CostRecord` goes to our store for reports. The same numbers go to Langfuse through `update_current_generation`, with `usage_details` and `cost_details`, so the trace UI shows dollars next to tokens. [PAUSE] And a Prometheus counter, `LLM_COST`, gets the increment, for the dashboards in Section 9. Note the labels on the counter: model, tenant, feature. Never user or session. Those have thousands of values, and Prometheus would fall over. That's the cardinality rule from lecture 5.5.

One detail. Langfuse can compute cost itself from its own model price list when you send `usage_details`. We send `cost_details` anyway, because the number in the report must equal the number in the trace, and only our function guarantees that.

[SCREEN: terminal]

Part B. The report. Let's replay the day and run it.

```bash
OFFLINE=1 make replay
uv run python -m northwind.report --day 2026-09-22 --by tenant --by feature
```

[DEMO: the markdown report renders. Tenant table, then feature table, as below.]

[SLIDE 2: Showback by tenant (baseline day)]

| Tenant | Sessions | Cost | Cost per session | Share |
|---|---|---|---|---|
| operations | 1,600 | $24.52 | $0.0153 | 40% |
| warehouse | 1,200 | $18.39 | $0.0153 | 30% |
| finance | 720 | $11.03 | $0.0153 | 18% |
| sales | 480 | $7.36 | $0.0153 | 12% |
| **Total** | **4,000** | **$61.29** | **$0.0153** | |

[AVATAR]

Here's the CFO's table. Operations is forty percent of the bill because it's forty percent of the sessions. Cost per session is flat across tenants, a cent and a half. [PAUSE] That flatness is the interesting finding. It means no department is misusing Atlas. The cost is structural. To cut it, change the agent, not the users.

Now slice the same records by feature.

[SLIDE 3: Showback by feature (baseline day)]

| Feature | Share of requests | Cost | Cost per request |
|---|---|---|---|
| policy_question | 45% | $35.15 | $0.0078 |
| ticket_lookup | 20% | $8.75 | $0.0044 |
| create_ticket | 12% | $8.25 | $0.0069 |
| password_reset | 13% | $4.47 | $0.0034 |
| shipment_status | 10% | $4.69 | $0.0047 |

[AVATAR]

Now it's not flat. Policy questions are forty-five percent of requests and fifty-seven percent of the cost, at almost eight tenths of a cent each, more than double a password reset. Why? Policy questions call `search_knowledge_base`, and that tool returns fifteen hundred tokens of retrieved text that gets re-sent on every following step. [PAUSE] That one row tells you where the context diet in 6.5 will pay off most.

[SLIDE 4: The number finance accepts: cost per resolved session]
- Cost per session: total ÷ sessions = $0.0153
- Resolved rate (feedback or judge, Section 8): 82%
- Cost per resolved session: $61.29 ÷ 3,280 = $0.0187
- Compare with a human ticket: minutes of an agent's time
- Report cost per *resolved* session; cost per session hides failures

[AVATAR]

One more number, and it's the one this whole course is named for in the market research: cost per resolved session. Divide the day's cost by the sessions that actually got resolved, not all sessions. Eighty-two percent resolved means the real unit cost is not a cent and a half, it's one point nine cents. [PAUSE] Why report the harsher number? Because when quality drops, cost per session stays flat and cost per resolved session climbs. It's the only cost metric that notices when the agent gets worse. In Section 8 we'll fill in `resolved` from feedback and the judge; today the replay uses the simulator's ground truth.

[SCREEN: `console/ops_console.py`, cost page: tenant bars, feature bars, cost-per-resolved-session tile]

The Ops Console shows the same rollups live. Same records, same function, so the console and the markdown report never disagree.

### Recap

Stamp every generation with tenant, user, session, feature, model, tokens and `usd`, send the same numbers to Langfuse and Prometheus, and any report, including cost per resolved session, is a group-by.

### Transition

Attribution tells you where the money goes. Next, the first lever that brings it back: prompt caching, which cuts the input bill by a third without changing a single answer.

### Speaker notes: common mistakes and Q&A

- **Storing `usd` instead of computing it.** If prices change or a bug is fixed, stored numbers are wrong forever. Compute on read from tokens; cache only for display.
- **Feature detection.** `ctx.feature` is Atlas's routed intent, set by the first tool chosen (or by the classifier in `app/agent.py`). Unknown intents go to `other`, never to the biggest bucket.
- **Cost per session across days.** Sessions can span midnight. Attribute to the day the session started; say so in the report footer.
- **Langfuse `cost_details` keys.** Use the same keys as `usage_details` (`input`, `output`, `cache_read_input_tokens`). Verified on langfuse 4.15.
- **Part A / Part B split.** Cut after the `app/agent.py` code block; Part B starts at `make replay`.

---

## Lecture 6.4: Prompt caching: the cheapest win

| Field | Value |
|---|---|
| ID | 6.4 |
| Title | Prompt caching: the cheapest win |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 650 spoken words at ~140 wpm; remaining time is on-screen code, runs and the before/after) |
| One idea | Put everything stable at the front of the prompt, set a `prompt_cache_key`, and the same day of traffic costs 35% less with identical answers. |
| Prerequisites | 6.3 |
| Files used | `app/agent.py`, `app/prompts.py`, `console/ops_console.py` |

**Learning objectives**

1. Explain how provider-side prompt caching works: exact prefix match, 1,024-token minimum, cached input billed at a quarter price, hit rate depends on recency and routing.
2. Restructure Atlas's prompt so the stable prefix (system, tools, policy) comes first and per-request content comes last, and pass `prompt_cache_key`.
3. Measure `cached_tokens` per step and compute the before/after cost on the same replayed day.

### Script

[B-ROLL: split screen. Left, red tint, BEFORE: a request's three steps with `cached_tokens: 0, 0, 0`. Right, green tint, AFTER: the same three steps with `cached_tokens: 1,792, 2,432, 4,032`. Cost line: $0.00484 → $0.00236.]

[AVATAR]

Same question, same answer, same model. Left side, half a cent. Right side, a third of a cent. [PAUSE] The only difference is the order of the prompt and one parameter. This is the cheapest win in the course, and most teams haven't turned it on.

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

[CODE: `app/agent.py` (excerpt): building the prompt and the call]

```python
def _build_messages(self, ctx: RequestContext, history: list[dict]) -> list[dict]:
    # 1. stable prefix: identical for every request of this tenant on this prompt version
    system = self.prompt.compile(tenant_policy=self.policy_for(ctx.tenant))  # rules + policy, no date, no user
    messages = [{"role": "system", "content": system}]
    # 2. slowly changing: conversation history
    messages += history
    # 3. per-request: the question, with the volatile bits at the very end
    messages.append({"role": "user", "content": f"{ctx.question}\n\n[context: today={ctx.today}, user={ctx.display_name}]"})
    return messages


def _cache_key(self, ctx: RequestContext) -> str:
    # same key => same cache shard. Version + tenant, never user or session.
    return f"atlas:{self.prompt.version}:{ctx.tenant}"


response = self.client.chat.completions.create(
    model=self.model,
    messages=self._build_messages(ctx, history),
    tools=self.tool_schemas,                 # tools are part of the prefix and are cached too
    prompt_cache_key=self._cache_key(ctx),
)
```

Three layers. The system message is compiled from the prompt version and the tenant's policy snippets, nothing else. No date, no name. The history comes next; within a session it only grows at the end, so earlier turns keep matching. Then the question, with the date and the user's name tucked at the very end, where they can't break anything.

The cache key is version plus tenant. Four tenants, one prompt version, four keys. [PAUSE] Never put the user or session in the key. That would give you four thousand keys a day and almost no hits.

And notice: `tools=` is part of the prefix. Five tool schemas, about six hundred tokens, cached along with the system message.

[SCREEN: terminal]

Let's prove it. One request, three steps, print `cached_tokens` per step.

```bash
uv run python -m app.agent --tenant operations --question "How do I reset my VPN token?" --show-usage
```

[DEMO: output:]

```
step 1  prompt=2480  cached=1792  completion=60   tool=search_knowledge_base
step 2  prompt=4040  cached=2432  completion=60   tool=lookup_ticket
step 3  prompt=4220  cached=4032  completion=220
request cost: $0.00236  (uncached would be $0.00484)
```

Step one: seventeen hundred ninety-two cached. That's the eighteen-hundred-token prefix, rounded down to a cache block, hit because another operations request ran a moment ago. Step two: twenty-four hundred cached, which is all of step one's prompt. Step three: four thousand cached, all of step two. [PAUSE] Within one request the hit rate is nearly perfect, because steps are seconds apart, so this request cost less than half. The number you can't control is step one across requests, and that's why the day-level planning figure is a seventy percent hit rate, not ninety-five.

Now the same day of traffic.

```bash
OFFLINE=1 make replay          # baseline, caching off
OFFLINE=1 CACHE=1 make replay  # same seed, caching on
```

[SLIDE 3: Before and after on the same day (verify current pricing)]

| | Before | After (70% hit rate) |
|---|---|---|
| Uncached input per request | 10,740 | 4,916 |
| Cached input per request | 0 | 5,824 |
| Input cost per request | $0.004296 | $0.001966 + $0.000582 = $0.002548 |
| Cost per request (mini) | $0.00484 | $0.00309 |
| Day (incl. retries and escalations, both cached) | $61.29 | **$39.58** |
| Saving | | **$21.71 a day, 35%** |

[AVATAR]

The day drops from sixty-one twenty-nine to thirty-nine fifty-eight. Twenty-one dollars seventy-one a day, six hundred fifty a month, thirty-five percent, with a seventy percent hit rate that the replay models from real traffic shape. [PAUSE] The answers are byte-for-byte identical, because the model saw the same tokens. Caching changes the bill, not the behavior.

[SCREEN: Ops Console, cost page: new tile "cache hit rate 70%", cached tokens series]

One new tile on the console: cache hit rate, cached tokens over uncached. Watch it. If it falls, someone put a timestamp at the front of the prompt again. It's the cheapest regression to catch and the most common one to ship.

[SLIDE 4: Caching rules of thumb]
- Sort: stable, slow, volatile
- Key on version and tenant, never user
- Prefix under 1,024 tokens? Nothing caches; measure before you celebrate
- Hit rate lives in `cached_tokens`; put it on a dashboard
- Other providers: explicit cache blocks and different prices; same sort, different API

[AVATAR]

Rules of thumb. Sort the prompt. Key on version and tenant. Check your prefix length, because under a thousand and twenty-four tokens nothing happens at all. Dashboard the hit rate. And if you use a provider with explicit cache controls, the sorting lesson is identical; only the API and the prices differ.

### Recap

Put the stable prefix first, the volatile bits last, set `prompt_cache_key` to version plus tenant, and the same day of Atlas traffic drops from $61.29 to $39.58 with identical answers.

### Transition

Caching makes re-sent tokens cheaper. The next lever makes them fewer: the context diet.

### Speaker notes: common mistakes and Q&A

- **"Why isn't the hit rate 100%?"** Step one of each request depends on another request with the same prefix having run recently on the same shard. Cache expiry, traffic lulls and routing cost you hits. 70% is a realistic planning number; the console shows the real one.
- **Date in the system prompt.** The most common regression. If Atlas needs today's date, put it at the end of the user message, as in the code.
- **History that gets edited.** Summarising or trimming the middle of the history breaks the prefix for that session. In 6.5 we trim from the front in blocks, on turn boundaries, so most steps still match.
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
| One idea | Trim history, truncate tool results and lower retrieval top-k, measure tokens per step before and after, and cut the input bill by a quarter without hurting answers. |
| Prerequisites | 6.4 |
| Files used | `src/northwind/tokens.py`, `app/agent.py`, `app/knowledge.py`, `tests/unit/test_tokens.py` |

**Learning objectives**

1. Estimate tokens without the network using `estimate_tokens`, and use `tiktoken` only when its encoding is already cached.
2. Apply `trim_history` (keep the last N turns plus a summary) and `truncate_tool_result` (hard cap with a marker) in the agent loop.
3. Lower retrieval top-k from 5 to 3 and measure tokens per step and cost per request before and after.

### Script

[AVATAR]

Fifteen hundred tokens. That's what `search_knowledge_base` returned for "how do I reset my VPN token." Five chunks, three hundred tokens each. The answer used one of them. [PAUSE] The other twelve hundred tokens rode along for two more steps, at full price, saying nothing. Multiply by forty-five hundred policy questions a day. That's the diet.

[SLIDE 1: Four places context bloats]
- History: every past turn, forever
- Tool results: whole documents when a paragraph would do
- Retrieval: top-k of 5 when 3 answers 96% of questions
- Tool schemas: fifty tools when the request needs five
- Rule: measure tokens per step first; cut the biggest, re-measure

[AVATAR]

Context bloats in four places. History that never gets trimmed. Tool results pasted whole. Retrieval that returns more chunks than the answer needs. And tool schemas, which we'll leave alone today because Atlas has five. The rule is the same as for any performance work: measure per step, cut the biggest, measure again. Let's look at the helpers.

[SCREEN: VS Code, `src/northwind/tokens.py`]

[CODE: `src/northwind/tokens.py` (excerpt)]

```python
def estimate_tokens(text: str, model: str = "gpt-4.1-mini") -> int:
    """Token count without network: tiktoken if its encoding is already on disk, else ~4 chars per token."""
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)  # raises if the encoding is not cached locally
        return len(enc.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def truncate_tool_result(text: str, max_tokens: int = 600) -> str:
    """Hard cap on a tool result, with a visible marker so the model knows it is looking at a cut."""
    if estimate_tokens(text) <= max_tokens:
        return text
    keep_chars = max_tokens * 4
    return text[:keep_chars].rsplit("\n", 1)[0] + f"\n[... truncated to {max_tokens} tokens; ask for more if needed]"


def trim_history(messages: list[dict], *, keep_last_turns: int = 4, max_tokens: int = 1_200,
                 summarize: Callable[[list[dict]], str] | None = None) -> list[dict]:
    """Keep the last N user/assistant turns whole; replace older turns with one summary line.
    Cuts on turn boundaries from the front so the cached prefix survives as long as possible."""
    if estimate_tokens(json.dumps(messages)) <= max_tokens:
        return messages
    turns = split_into_turns(messages)
    old, recent = turns[:-keep_last_turns], turns[-keep_last_turns:]
    summary = summarize(flatten(old)) if summarize else f"[earlier: {len(old)} turns about {topics(old)}]"
    return [{"role": "system", "content": f"Conversation so far: {summary}"}] + flatten(recent)
```

Three functions. `estimate_tokens` uses `tiktoken` if the encoding is already on disk, otherwise four characters per token. That approximation is within ten percent for English, and it never phones home, so tests and offline mode work. `truncate_tool_result` caps a result and adds a visible marker, so the model knows it saw a cut and can ask for more. `trim_history` keeps the last four turns whole and replaces older ones with a summary line. It cuts on turn boundaries from the front, so the cached prefix from 6.4 survives most steps.

Now wire them in.

[SCREEN: `app/agent.py` and `app/knowledge.py`]

[CODE: `app/agent.py` (excerpt) and `app/knowledge.py` (excerpt)]

```python
# app/agent.py, in the step loop
history = trim_history(history, keep_last_turns=self.cfg.keep_last_turns, max_tokens=self.cfg.history_budget)
...
result = tool(**args)
result = truncate_tool_result(result, max_tokens=self.cfg.tool_result_budget)   # default 600
messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

# app/knowledge.py
def search_knowledge_base(query: str, k: int = settings.retrieval_top_k) -> str:   # default was 5; now 3
    hits = retriever.search(query, k=k)
    return "\n\n".join(f"[{h.doc}] {h.text[:800]}" for h in hits)               # ~200 tokens per chunk
```

Two budgets in config: `history_budget`, twelve hundred tokens, and `tool_result_budget`, six hundred. And in the knowledge tool, top-k drops from five to three, and each chunk is capped at about two hundred tokens.

One option I left off by default: the `summarize=` callback. You can pass a function that asks gpt-4.1-mini to write a two-sentence summary of the old turns instead of the placeholder line. It gives better continuity on long sessions, and it costs a model call, about three hundred input tokens and forty out, a hundredth of a cent. On Atlas, sessions average two and a half turns, so it would fire on fewer than one request in twenty. Turn it on when your history budget trips often, and measure it like everything else. [PAUSE] The other cut for bigger agents is tool schemas. Atlas has five tools, six hundred tokens. If you have forty, send the model only the tools relevant to the routed intent, and you'll save more than the diet did. [PAUSE] Why three? Because in the replay's ground truth, the right chunk is in the top three for ninety-six percent of policy questions. The two extra chunks were insurance that cost twelve hundred tokens per step and paid out four percent of the time. We'll check the quality side in a moment.

[SCREEN: terminal]

Measure it. Same request as last lecture.

```bash
uv run python -m app.agent --tenant operations --question "How do I reset my VPN token?" --show-usage --diet
```

[DEMO: output:]

```
step 1  prompt=2130  completion=60   (history 600 -> 250)
step 2  prompt=2790  completion=60   (tool result 1500 -> 600)
step 3  prompt=2970  completion=220
input 7890 (was 10740)  request cost: $0.00370 (was $0.00484)
```

Ten thousand seven hundred forty becomes seven thousand eight hundred ninety. Twenty-seven percent fewer input tokens per request, from two changes that took eight lines. Now the day.

[SLIDE 2: Before and after on the same day (diet only, caching off, verify current pricing)]

| | Before | After |
|---|---|---|
| Input tokens per request | 10,740 | 7,890 |
| Steps | 2,480 / 4,040 / 4,220 | 2,130 / 2,790 / 2,970 |
| Cost per request (mini) | $0.00484 | $0.00370 |
| Day (incl. retries and escalations) | $61.29 | **$46.79** |
| Saving | | **$14.50 a day, 24%** |
| Judge "grounded" score (replay, Section 8 metric) | 0.91 | 0.90 |

[AVATAR]

Fourteen dollars fifty a day, twenty-four percent, on its own. And the last row is the one that makes this responsible: the grounded score on the replay barely moves, ninety-one to ninety. [PAUSE] If it had dropped to eighty, top-k three would have been a bad trade, and you'd go back to four. That's the discipline: every token cut ships with a quality number next to it. Section 8 makes that number automatic.

[SLIDE 3: Diet plus caching]
- The two levers stack: fewer tokens, and the ones left are cheaper
- Trim from the front on turn boundaries, so the prefix still matches
- Diet + caching on the same day: $61.29 → $29.22 (−52%)
- Retries and escalations still at baseline rates; that's 6.6 and 6.7

[AVATAR]

And they stack. Trimming from the front on turn boundaries keeps the cached prefix intact on most steps, so with caching and the diet together the day comes down to twenty-nine twenty-two. Fifty-two percent. [PAUSE] We haven't touched the escalation model or the retries yet. That's the next two lectures.

[SCREEN: `tests/unit/test_tokens.py`, three tests visible]

Three unit tests protect the diet: truncation keeps the marker, trimming keeps the last four turns whole, and the estimator is within ten percent of tiktoken when tiktoken is cached. Run them offline with everything else.

### Recap

Trim history to the last few turns plus a summary, cap tool results at 600 tokens with a marker, drop retrieval top-k from 5 to 3, and the day falls 24% on its own and 52% with caching, with the grounded score unchanged.

### Transition

The remaining cost is concentrated in one place: the ten percent of requests that escalate to gpt-4.1. Next, we route to the small model first and escalate only when we must.

### Speaker notes: common mistakes and Q&A

- **Trimming in the middle.** Deleting middle turns changes the prefix and kills the cache for the rest of the session. Cut from the front, on turn boundaries.
- **Truncating without a marker.** The model doesn't know it saw half a document and answers confidently. The marker lets it ask `search_knowledge_base` again with a narrower query.
- **Top-k as a global.** Different features may need different k. Keep it in config per tool; the default here is 3.
- **tiktoken and network.** `tiktoken` downloads encodings on first use. `estimate_tokens` falls back to the approximation, so CI never needs the download. Show the fallback path once.
- **The grounded score.** Comes from the Section 8 judge run on the replay. If a student asks how we know, point ahead to 8.2 and to the simulator's ground-truth labels.

---

## Lecture 6.6: Small-model-first routing with LiteLLM Router

| Field | Value |
|---|---|
| ID | 6.6 |
| Title | Small-model-first routing with LiteLLM Router |
| Type | SC (screencast code-along; upload as Part A "the Router" and Part B "the escalation rule and cost impact") |
| Target duration | 9:00 (about 750 spoken words at ~140 wpm; remaining time is on-screen code and runs) |
| One idea | Run every request on gpt-4.1-mini, escalate to gpt-4.1 only on a measurable signal, and cut the escalation bill from $10.84 to about $3 a day. |
| Prerequisites | 6.5; `litellm` installed |
| Files used | `app/agent.py` (router mode), `src/northwind/config.py`, `telemetry/metrics.py` |

**Learning objectives**

1. Configure a LiteLLM `Router` with a `model_list`, `fallbacks`, `num_retries`, `timeout`, `allowed_fails` and `cooldown_time` (verified kwargs on litellm 1.103).
2. Implement an escalation rule based on signals you can log: low confidence, repeated tool failure, a sensitive feature, or a step budget exceeded.
3. Measure escalation rate and cost per model before and after, and log every escalation with a reason.

### Script

[AVATAR]

Ten dollars eighty-four. That's what the escalation model cost on the baseline day. One in ten requests, and the final step alone costs a cent, ten times a mini step. [PAUSE] Here's the question I want you to sit with. Did all thousand of those requests need the big model? Or did someone write `if feature == "create_ticket": use gpt-4.1` in March because it felt safer? Let's find out with a router.

[SLIDE 1: Small-model-first]
- Default: gpt-4.1-mini for every step
- Escalate to gpt-4.1 only on a signal: low self-reported confidence, a tool failing twice, a sensitive feature, step budget exceeded
- Escalate the *step*, not the whole request
- Log the reason on the span; count it in Prometheus
- Also use the Router for fallbacks (Section 7) so there's one place for model selection

[AVATAR]

Small-model-first means the default is always the cheap model, and moving up costs you a logged reason. Not a feature name. A signal from this request. And you escalate one step, not the whole conversation. The router also gives us fallbacks and cooldowns, which we'll lean on in Section 7, so model selection lives in exactly one place.

[SCREEN: VS Code, `app/agent.py`, router mode]

[CODE: `app/agent.py` (excerpt): building the Router]

```python
from litellm import Router


def build_router(cfg: Settings) -> Router:
    return Router(
        model_list=[
            {"model_name": "atlas-default",
             "litellm_params": {"model": cfg.default_model, "api_key": cfg.openai_api_key}},   # gpt-4.1-mini
            {"model_name": "atlas-strong",
             "litellm_params": {"model": cfg.escalation_model, "api_key": cfg.openai_api_key}},  # gpt-4.1
        ],
        fallbacks=[{"atlas-default": ["atlas-strong"]}],   # only on errors, not on quality (Section 7)
        num_retries=2,
        timeout=cfg.llm_timeout_s,        # 20 s per call
        allowed_fails=3,
        cooldown_time=30,
    )
```

The `model_list` gives each deployment a logical name. `atlas-default` is gpt-4.1-mini, `atlas-strong` is gpt-4.1, both from config, so swapping models is an environment variable. `fallbacks` says: if `atlas-default` errors out, try `atlas-strong`. That's for outages, not for quality; we'll tune it in Section 7. Keep the two ideas apart in your head. A fallback fires when a call fails. An escalation fires when a call succeeds and we don't trust the answer. The Router knows about the first. Only our code can know about the second. Two retries, a twenty-second timeout, and after three failures a deployment cools down for thirty seconds. All of these are verified kwargs on litellm one point one oh three.

Now the escalation rule, which is ours, not the router's.

[CODE: `app/agent.py` (excerpt): choosing the deployment per step]

```python
def _choose_deployment(self, ctx: RequestContext, state: StepState) -> tuple[str, str | None]:
    """Return (deployment_name, escalation_reason)."""
    if state.tool_failures >= 2:
        return "atlas-strong", "tool_failed_twice"
    if state.step >= self.cfg.escalate_after_step:            # default 4
        return "atlas-strong", "step_budget"
    if ctx.feature == "password_reset" and state.about_to_call("reset_password"):
        return "atlas-strong", "sensitive_action"
    if state.last_confidence is not None and state.last_confidence < self.cfg.min_confidence:  # 0.6
        return "atlas-strong", "low_confidence"
    return "atlas-default", None


deployment, reason = self._choose_deployment(ctx, state)
if reason:
    lf.update_current_span(level="WARNING", status_message=f"escalated: {reason}",
                           metadata={"escalation_reason": reason, "from": "atlas-default", "to": deployment})
    ESCALATIONS.labels(reason=reason, tenant=ctx.tenant).inc()

response = self.router.completion(model=deployment, messages=messages, tools=self.tool_schemas,
                                  prompt_cache_key=self._cache_key(ctx))
```

Four signals, in order of confidence. A tool failed twice: the small model is stuck, escalate. Step four or later: the small model is wandering, escalate. About to reset a password: a sensitive action where the extra cent is cheap insurance. And low confidence: Atlas's final answer includes a self-reported confidence field in its structured output, and below zero point six we redo that step on the strong model.

Where does that confidence number come from? Atlas answers through a JSON schema with three fields: the answer text, a refusal flag, and `confidence` from zero to one, with the instruction to score low when the retrieved context didn't contain the answer. It's a weak signal on its own; models are optimistic. But it's cheap, it's on every request, and on the replay it correlates with the judge's grounded score at about point six. That's good enough to be the last check in the list, and not good enough to be the first. [PAUSE] Tune the threshold on the replay, not by feel: at zero point six, three percent of requests escalate; at zero point seven, nine percent, and the resolved gain flattens. Zero point six is where the curve bends. [PAUSE] Every escalation writes a reason onto the span, marks it as a warning, and increments a counter with the reason as a label. So tomorrow you can ask: which reason is costing me money?

Part B. The cost impact.

[SCREEN: terminal]

```bash
OFFLINE=1 ROUTER=1 make replay
uv run python -m northwind.report --day 2026-09-22 --by model --escalations
```

[DEMO: output table, then escalation reasons]

[SLIDE 2: Before and after on the same day (routing only, verify current pricing)]

| | Before (rule: feature-based) | After (signal-based) |
|---|---|---|
| Requests escalated | 1,000 (10%) | 300 (3%) |
| gpt-4.1 cost | $10.84 | $3.25 |
| Retried generations | 1,200 (4% of steps) | 450 (1.5%, bounded retries) |
| Retry cost | $2.05 | $0.77 |
| Day | $61.29 | **$52.42** |
| Saving | | **$8.87 a day, 15%** |

[AVATAR]

Escalations drop from a thousand a day to three hundred. Not zero. Three hundred requests had a real signal. The gpt-4.1 line falls from ten eighty-four to three twenty-five. And because the router's bounded retries replaced the agent's old retry-until-it-works loop, retried generations fall by more than half too. Eight dollars eighty-seven a day, fifteen percent. [PAUSE] Smaller than caching. But this lever is the one that protects quality, because it sends the hard cases up instead of hoping.

[SLIDE 3: Escalation reasons on the replayed day]

| Reason | Count | Share |
|---|---|---|
| low_confidence | 141 | 47% |
| sensitive_action | 96 | 32% |
| tool_failed_twice | 48 | 16% |
| step_budget | 15 | 5% |

[AVATAR]

And here's why the reason label matters. Half the escalations are low confidence, and most of those are policy questions where retrieval came back thin. That's a retrieval problem wearing a model-cost costume. Fix the knowledge base article, and the escalation disappears. You only know that because the reason is on the span.

[SLIDE 4: Did quality hold?]
- Judge "resolved" on the replay: 0.82 before, 0.83 after
- 700 requests that used to get gpt-4.1 got mini and resolved at the same rate
- The 300 that escalated resolved at 0.88, up from 0.79 for the same requests on mini alone
- Routing moved the expensive model to where it changed the outcome

[AVATAR]

Quality held. Resolved rate went from eighty-two to eighty-three percent. And for the three hundred requests that did escalate, resolved went up nine points. The big model is now spent where it changes the outcome, instead of on a feature name. [PAUSE] That's the whole idea of small-model-first: not "use the cheap model," but "make the expensive one earn its place, request by request."

### Recap

Put both models behind a LiteLLM Router, default every step to gpt-4.1-mini, escalate one step at a time on a logged signal, and the escalation bill falls from $10.84 to $3.25 a day with resolved rate unchanged.

### Transition

Three levers, each measured. Now the guard rail: per-tenant budgets that degrade gracefully and an anomaly detector that pages you before finance does.

### Speaker notes: common mistakes and Q&A

- **Self-reported confidence.** It's a weak signal alone; that's why it's last in the list and combined with a threshold you tune on the replay. Say so; students over-trust it.
- **Escalating the whole conversation.** Re-running all steps on gpt-4.1 costs 5× the request, not 5× one step. The code escalates a step.
- **Router fallbacks vs escalation.** `fallbacks` fire on errors and timeouts; escalation fires on quality signals. Both end up on `atlas-strong` but for different reasons, and both are logged with different labels.
- **`gpt-5-mini` in the demo.** Add it as a third deployment for a routing experiment; its reasoning tokens show up in `output_tokens_details.reasoning_tokens` and change the cost math (6.1).
- **Part A / Part B split.** Cut after the `_choose_deployment` code block.

---

## Lecture 6.7: Budgets and anomaly alerts per tenant

| Field | Value |
|---|---|
| ID | 6.7 |
| Title | Budgets and anomaly alerts per tenant |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 630 spoken words at ~140 wpm; remaining time is on-screen code and the demo) |
| One idea | Give every tenant a daily budget with a soft cap that degrades and a hard cap that refuses politely, and an EWMA detector that flags a spend spike within minutes. |
| Prerequisites | 6.6 |
| Files used | `src/northwind/budget.py`, `app/server.py`, `telemetry/metrics.py`, `tests/unit/test_budget.py` |

**Learning objectives**

1. Describe LiteLLM's `BudgetManager` concept and why Atlas uses its own `budget.py` for per-tenant caps.
2. Implement `BudgetGuard.check(tenant, spend_today)` returning `OK`, `DEGRADE` or `REFUSE`, and wire the degraded mode into the agent.
3. Implement `EwmaAnomaly` and emit a Prometheus counter for budget events, so a spike is visible before the day's total is.

### Script

[B-ROLL: the $4,000 weekend clip from lecture 1.1: the cost meter climbing.]

[AVATAR]

You've seen this clip. A loop, a weekend, four thousand dollars. [PAUSE] Everything we've done in this section makes the normal day cheaper. None of it stops an abnormal one. A budget does. And a budget that just says "no" at midnight is a budget nobody will let you ship. So we'll build one with two levels and an early warning.

[SLIDE 1: Two caps and a detector]
- Soft cap (80% of daily budget): degrade. Mini only, no escalation, top-k 2, shorter answers. Users barely notice.
- Hard cap (100%): refuse politely. "Atlas is over budget for your department today; a ticket has been created."
- EWMA anomaly: spend per 5-minute window vs. its smoothed history; flag at 3 standard deviations
- Everything emits a counter: `atlas_budget_events_total{tenant, action}`

[AVATAR]

Two caps. At eighty percent of the day's budget, degrade: turn off escalation, lower retrieval, ask for shorter answers. The tenant keeps getting service, just the economy version. At a hundred percent, refuse, politely, and still create a ticket so nobody is stranded. And separately, a detector that watches spend per five-minute window against its own smoothed history. A loop shows up as a spike in the first window, hours before the daily cap would.

[SLIDE 2: LiteLLM `BudgetManager` (concept) vs our `budget.py`]
- `BudgetManager(project_name=...)`: `create_budget(total_budget, user, duration)`, `update_cost(...)`, `get_current_cost(user)`, `projected_cost(...)`
- Great for per-user caps on a LiteLLM gateway
- Atlas needs: per-tenant, soft and hard levels, degraded mode, anomaly detection, offline tests
- So: same idea, our own 80 lines, unit-tested

[AVATAR]

LiteLLM ships a `BudgetManager`: create a budget per user with a duration, update cost after each call, read the current and projected cost. If you run a LiteLLM gateway, use it. Atlas needs the tenant dimension, two levels, a degraded mode and a detector, so we write our own eighty lines with the same shape, and test them offline.

[SCREEN: VS Code, `src/northwind/budget.py`]

[CODE: `src/northwind/budget.py` (excerpt)]

```python
from dataclasses import dataclass, field
from enum import Enum
import math


class Decision(str, Enum):
    OK = "ok"
    DEGRADE = "degrade"
    REFUSE = "refuse"


@dataclass(frozen=True)
class TenantBudget:
    daily_usd: float
    soft_ratio: float = 0.80


class BudgetGuard:
    def __init__(self, budgets: dict[str, TenantBudget]) -> None:
        self.budgets = budgets

    def check(self, tenant: str, spend_today_usd: float) -> Decision:
        b = self.budgets[tenant]
        if spend_today_usd >= b.daily_usd:
            return Decision.REFUSE
        if spend_today_usd >= b.daily_usd * b.soft_ratio:
            return Decision.DEGRADE
        return Decision.OK


@dataclass
class EwmaAnomaly:
    """Flags a window whose value is more than k smoothed standard deviations above the smoothed mean."""
    alpha: float = 0.3
    k: float = 3.0
    warmup: int = 6
    mean: float = 0.0
    var: float = 0.0
    n: int = field(default=0)

    def observe(self, x: float) -> bool:
        if self.n < self.warmup:
            self.mean += (x - self.mean) / (self.n + 1)
            self.n += 1
            return False
        std = math.sqrt(self.var) if self.var > 0 else max(self.mean * 0.1, 1e-9)
        is_anomaly = x > self.mean + self.k * std
        diff = x - self.mean
        self.mean += self.alpha * diff
        self.var = (1 - self.alpha) * (self.var + self.alpha * diff * diff)
        self.n += 1
        return is_anomaly
```

`BudgetGuard.check` is three comparisons. Spend at or above the daily budget, refuse. At or above eighty percent, degrade. Otherwise fine. The spend comes from the cost records in 6.3, summed for the tenant since midnight. [PAUSE] `EwmaAnomaly` is an exponentially weighted moving average with a moving variance. Each five-minute window's spend is compared with the smoothed mean plus three smoothed standard deviations. Six windows of warm-up so it doesn't fire at startup. Alpha zero point three means it forgets in about ten windows, so a slow Tuesday doesn't make Wednesday morning look like an attack.

Now the wiring.

[SCREEN: `app/server.py`]

[CODE: `app/server.py` (excerpt)]

```python
decision = budget_guard.check(tenant, cost_store.spend_today(tenant))
BUDGET_EVENTS.labels(tenant=tenant, action=decision.value).inc()

if decision is Decision.REFUSE:
    ticket = tools.create_ticket(subject=f"Atlas over budget: {tenant}", body=req.question, priority="normal")
    return ChatResponse(answer=f"Atlas has reached today's budget for {tenant}. I've opened ticket {ticket.id} "
                               f"so a colleague can help.", degraded=True)

mode = AgentMode.ECONOMY if decision is Decision.DEGRADE else AgentMode.NORMAL   # economy: no escalation, k=2, max_output=120
answer = agent.run(req, mode=mode)

if anomaly[tenant].observe(cost_store.spend_last_window(tenant, minutes=5)):
    ANOMALIES.labels(tenant=tenant).inc()
    log.warning("cost anomaly", extra={"tenant": tenant, "window_usd": ..., "trace_id": ...})
```

Before the agent runs, check the budget and count the decision. Refuse creates a ticket and answers honestly. Degrade switches the agent to economy mode: mini only, top-k two, a hundred-twenty-token answer cap. And after the request, feed the tenant's last five-minute spend to its detector; a hit increments a counter and writes a warning log with the trace id. [PAUSE] Section 9 turns those two counters into alerts. Today we just make them exist.

[SLIDE 3: Setting the budgets (from the showback, 6.3)]

| Tenant | Baseline day | After the three levers | Daily budget (1.5× after) | Soft cap |
|---|---|---|---|---|
| operations | $24.52 | $9.94 | $15.00 | $12.00 |
| warehouse | $18.39 | $7.46 | $11.00 | $8.80 |
| finance | $11.03 | $4.47 | $7.00 | $5.60 |
| sales | $7.36 | $2.98 | $4.50 | $3.60 |

[AVATAR]

Where do the numbers come from? From the showback. Take each tenant's normal day after the levers, and set the budget at one and a half times that. Enough headroom for a busy Monday, tight enough that a loop hits the soft cap in under an hour. [PAUSE] Budgets you invent get ignored. Budgets derived from the report get approved.

[SCREEN: terminal]

Now break it.

```bash
OFFLINE=1 make replay SCENARIO=retry_storm TENANT=operations
```

[DEMO: Ops Console budgets page. Operations spend line rises steeply at 10:05. At 10:10 the anomaly marker fires (window spend $1.42 vs smoothed mean $0.21). At 10:47 the soft cap triggers: `budget_events{action="degrade"}` climbs; the line flattens. Hard cap is never reached. Alongside: a tenant without the guard for comparison, reaching $12 by 11:00 and $19 by noon.]

The retry storm scenario: a tool starts failing for operations, and every request retries. Ten oh five, spend accelerates. Ten ten, one window later, the detector fires: a dollar forty-two in five minutes against a smoothed twenty-one cents. That's your page. Ten forty-seven, the soft cap. Economy mode kicks in and the line bends. The hard cap never fires, and nobody in operations got refused. [PAUSE] Without the guard, the same storm is at nineteen dollars by noon on a nine-dollar day, and still climbing.

Unguarded, that storm roughly quadruples the tenant's hourly spend for as long as the tool keeps failing. With the guard, the detector spoke five minutes in, and the soft cap capped the damage. Cheap insurance.

### Recap

A soft cap degrades to economy mode, a hard cap refuses politely with a ticket, an EWMA detector flags a spend spike within one five-minute window, and every decision is a Prometheus counter waiting for an alert.

### Transition

You now have four measured tools: caching, the diet, routing and budgets. Time to use them. In the next lecture you'll cut Atlas's day by forty percent, on your own, before I show you how I did it.

### Speaker notes: common mistakes and Q&A

- **Hard cap without a fallback.** Refusing with no ticket strands users and gets the budget removed within a week. Always create the ticket.
- **Budget spend from Prometheus.** Counters reset on restart; compute spend from the cost store, and use the counter for alerting only.
- **EWMA warm-up and quiet hours.** Overnight windows near zero make the morning look anomalous. Either use a per-hour-of-day baseline or a minimum std floor (the code uses 10% of mean). Mention both.
- **Anomaly vs budget.** They answer different questions: "is this abnormal?" vs "have we spent the money?". Keep both.
- **Coding exercise.** The Udemy in-browser exercise "EWMA anomaly" is this class with stdlib only; point students to `06-assessments/coding-exercises.md`.

---

## Lecture 6.8: Challenge: cut Atlas's daily cost by 40%

| Field | Value |
|---|---|
| ID | 6.8 |
| Title | Challenge: cut Atlas's daily cost by 40% |
| Type | CH (pause-then-solution challenge) |
| Target duration | 7:00 (about 580 spoken words at ~140 wpm; the student pause is off-video, 30 to 60 minutes) |
| One idea | Take the $61.29 replayed day below $36.77 using the levers from this section, prove it in the Ops Console, and prove quality held. |
| Prerequisites | 6.1 to 6.7 |
| Files used | `simulator/replay.py`, `src/northwind/config.py`, `console/ops_console.py`, `05-projects/challenges.md` |

**Learning objectives**

1. Combine caching, the context diet and routing on the same replayed day and read the result from the Ops Console.
2. Prove the saving with before and after figures per tenant and per feature, and prove quality with the resolved and grounded scores.
3. Recognise that the levers stack, and that the order you apply them changes what you learn.

### Script

[AVATAR]

Here's the brief, and then I'm going to stop talking. [PAUSE] Atlas's replayed day costs sixty-one dollars twenty-nine. Get it under thirty-six seventy-seven, a forty percent cut, without the resolved score dropping more than two points. Prove it on the Ops Console with before and after. You have every tool you need from the last six lectures.

[SLIDE 1: The challenge]
- Start: `OFFLINE=1 make replay` on seed 2026-09-22 → $61.29, resolved 0.82, grounded 0.91
- Target: ≤ $36.77 (−40%), resolved ≥ 0.80, grounded ≥ 0.89
- Allowed: anything in `src/northwind/config.py` and `app/`: caching, history and tool budgets, top-k, routing thresholds, budgets
- Not allowed: dropping traffic, refusing requests, changing the seed
- Deliver: a before/after screenshot of the console cost page and one paragraph on what you changed and why
- Full spec: `05-projects/challenges.md`, Challenge 2

[AVATAR]

Three rules. You can change configuration and agent code. You can't make the day smaller by serving fewer requests or refusing them; the hard cap doesn't count as a saving. And you can't change the seed. Same day, cheaper.

One hint. [PAUSE] Apply one lever at a time and replay after each. The order you choose will teach you something the final number won't.

Pause the video now. Thirty to sixty minutes. Come back when the console says thirty-six or less.

[SLIDE 2: PAUSE. Come back with a number.]

[PAUSE: 5 seconds of the slide, then a title card "Reference solution"]

[AVATAR]

You're back. Here's how I did it, one lever at a time, in the order I'd do it in production.

[SCREEN: terminal and Ops Console side by side]

```bash
OFFLINE=1 make replay                       # baseline
OFFLINE=1 CACHE=1 make replay               # + caching
OFFLINE=1 CACHE=1 DIET=1 make replay        # + context diet
OFFLINE=1 CACHE=1 DIET=1 ROUTER=1 make replay   # + routing
```

[SLIDE 3: Reference solution, one lever at a time (verify current pricing)]

| Step | Day | Saving vs baseline | Resolved | Grounded |
|---|---|---|---|---|
| Baseline | $61.29 | | 0.82 | 0.91 |
| + Caching (`prompt_cache_key`, sorted prompt) | $39.58 | −35% | 0.82 | 0.91 |
| + Context diet (history 1,200, tool 600, k=3) | $29.22 | −52% | 0.82 | 0.90 |
| + Routing (signal-based escalation, bounded retries) | **$24.86** | **−59%** | **0.83** | 0.90 |

[AVATAR]

Caching first, because it changes nothing about the answers. Thirty-five percent, and every quality score is identical to the decimal. That's why I do it first: it's the lever with no quality risk, and it tells you how much of the remaining bill is genuinely new tokens.

Then the diet. Down to twenty-nine twenty-two, fifty-two percent. Target passed. Grounded dropped one point, from ninety-one to ninety, because top-k three misses the right chunk on four percent of policy questions. Within the two-point rule. If you set k to two, you'd have seen grounded fall to eighty-six and you'd have put it back. That's the lesson the order teaches: the diet is where quality can move, so measure it there.

Then routing. Twenty-four eighty-six, fifty-nine percent, and resolved actually goes up a point, because the three hundred hard requests now get the strong model on purpose. [PAUSE] Sixty-one dollars to twenty-five. About seven hundred fifty a month instead of eighteen hundred. Thirteen thousand a year, on a helpdesk for four departments, with the answers as good or better.

[SLIDE 4: After, by tenant and by feature]

| Tenant | Before | After | | Feature | Before | After |
|---|---|---|---|---|---|---|
| operations | $24.52 | $9.94 | | policy_question | $35.15 | $12.30 |
| warehouse | $18.39 | $7.46 | | ticket_lookup | $8.75 | $3.85 |
| finance | $11.03 | $4.47 | | create_ticket | $8.25 | $3.71 |
| sales | $7.36 | $2.98 | | password_reset | $4.47 | $3.10 |
| | | | | shipment_status | $4.69 | $1.90 |

[AVATAR]

By tenant, everyone saved the same share, which is what you'd expect from structural changes. By feature, policy questions saved the most, sixty-five percent, because they carried the biggest tool results. Password resets saved the least, thirty-one percent, because they were already lean and now escalate to gpt-4.1 on purpose as a sensitive action. [PAUSE] That table is your one paragraph: the saving is structural, it's largest where the context was largest, and it cost nothing in quality.

[SLIDE 5: Common ways to hit 40% the wrong way]
- Top-k 1 or tool budget 200: cost drops, grounded drops to the low 80s
- Escalation off entirely: $3.25 saved, resolved drops 3 points on the hard cases
- History budget 300: sessions lose the thread on turn 3; resolved drops for multi-turn
- Hard cap at $30: the day "costs" $30 and 2,000 users get refused

[AVATAR]

Four wrong ways to hit the number, and I've seen all of them. Starving retrieval. Turning escalation off. Cutting history so hard that turn three forgets turn one. And the budget trick, where the day costs thirty dollars because two thousand people got a refusal. [PAUSE] Every one of them passes the cost test and fails the quality test. Which is why the challenge had two numbers, and why the console shows them side by side.

[AVATAR]

If you got under thirty-six seventy-seven with quality intact, post your before and after in the Q&A with the one-paragraph explanation. If you got there a different way than I did, I especially want to see it.

### Recap

Caching, then the diet, then routing, each measured on the same replayed day, take Atlas from $61.29 to $24.86 with resolved and grounded scores intact, and the order teaches you where quality can move.

### Transition

You've done the engineering. Now turn it into the document that gets you the budget: Project 1, the showback report.

### Speaker notes: common mistakes and Q&A

- **Students who only cache and call it done.** 35% is short of 40% on purpose, so the challenge needs at least two levers. Say so in the solution if the Q&A shows confusion.
- **"My numbers differ slightly."** The replay is deterministic per seed, but the cache hit rate is simulated at 70%. If they changed `CACHE_HIT_RATE` in config, the numbers move. That's allowed, but it must be declared.
- **Quality scores on the replay.** They come from the simulator's ground truth and the Section 8 judge on sampled traces. Students who haven't reached Section 8 see them on the console anyway.
- **Order.** Any order reaches the same final number. The order changes the intermediate rows, which is where the learning is.

---

## Lecture 6.9: Project 1: The showback report

| Field | Value |
|---|---|
| ID | 6.9 |
| Title | Project 1: The showback report |
| Type | AS (assignment; text lecture with a short video intro) |
| Target duration | Video 3:00 (about 220 spoken words at ~140 wpm, plus slide time); project work 2 to 3 hours off-video |
| One idea | Produce the weekly cost report by tenant and feature, with cost per resolved session and three recommendations, in a form finance would accept. |
| Prerequisites | 6.1 to 6.8 |
| Files used | `05-projects/project-1-showback-report.md`, `src/northwind/report.py`, `simulator/replay.py` |

**Learning objectives**

1. Generate a seven-day replay and run `report.py` by tenant and by feature.
2. Write three recommendations that each cite a number from the report and estimate a saving.
3. Present cost per resolved session as the headline metric.

### Script

[AVATAR]

Project one is the document that turns this section into budget. A one-page weekly showback report, the kind a finance partner reads without calling you.

[SCREEN: `05-projects/project-1-showback-report.md`: the brief and rubric.]

Replay seven days with `make replay DAYS=7`. Run `report.py` by tenant and by feature. The report must show total cost, cost per session, cost per resolved session, and the trend across the week. Then three recommendations. Each one has to cite a number from your report and estimate the saving in dollars per month. "Enable caching for the sales tenant" is not a recommendation. "Sales has a 41% cache hit rate against 72% elsewhere because its policy prefix is 940 tokens, under the minimum; padding it to 1,100 tokens would save about $11 a month" is.

[SLIDE 1: Project 1 rubric]
- Report by tenant and by feature, seven days, with trend: 40%
- Cost per resolved session as headline, with the resolved rate stated: 20%
- Three recommendations, each with a cited number and a monthly saving: 30%
- Prices marked with a date and "verify current pricing": 10%

[AVATAR]

The rubric's biggest points go to the recommendations, because that's the part finance can act on. And ten percent for something small: the prices in your report carry a date and the words "verify current pricing." A report that's honest about its constants is one people trust.

Post the markdown, or a screenshot of it, in the Q&A. The best ones get featured.

### Recap

Project 1 is the weekly showback report by tenant and feature, headlined by cost per resolved session, with three numbered recommendations.

### Transition

Before you start the project, check your understanding with the Section 6 quiz.

### Speaker notes: common mistakes and Q&A

- **Recommendations without numbers.** The most common failure. Send them back to the feature table.
- **Reporting cost per session only.** Insist on cost per resolved session with the resolved rate beside it.
- **Undated prices.** Ten percent of the grade, on purpose.

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
