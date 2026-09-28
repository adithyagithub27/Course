# Lab 4: Hold p95 Under 4 Seconds During Chaos

| Field | Details |
|---|---|
| **Section / lecture** | Section 7, lecture 7.7 |
| **Time estimate** | 75 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Inject the `slow_provider` scenario into a replayed day, watch p95 blow through the 4,000 ms budget, then tune timeouts, retries, fallbacks and the circuit breaker until the budget gate (`make budget-check`) passes, while keeping cost per session under $0.05. Every change must be justified by a number from the spans. |
| **You will produce** | A tuned `.env.chaos`, `notes/lab-04.md` with a before/after table, and a green `make budget-check` |

---

## Prerequisites

- Labs 1 to 3 complete.
- Lectures 7.1 to 7.6 watched, especially 7.3 (timeouts and retries) and 7.4 (fallbacks and circuit breakers).
- Comfortable reading `src/northwind/latency.py` and the Router configuration in `app/agent.py`.

## The budget

From `.env.example` (read by `src/northwind/config.py` and `tests/budget/test_budget_gate.py`):

| Setting | Value | Meaning |
|---|---|---|
| `BUDGET_P95_LATENCY_MS` | 4000 | p95 end-to-end latency of `atlas.chat` over the replayed day |
| `BUDGET_COST_PER_SESSION_USD` | 0.05 | mean cost per session over the replayed day |
| `ATLAS_REQUEST_TIMEOUT_S` | 20 | per-model-call timeout |
| `ATLAS_MAX_RETRIES` | 2 | retries per model call |
| `ATLAS_ROUTER_MODE` | 0 | 1 = LiteLLM Router with fallbacks and cooldowns |

The lab is a game with two scores: p95 must go **down** below 4,000 and cost per session must **stay** below 0.05. Several obvious fixes improve one and break the other.

---

## Step 1: Baseline (no chaos)

Everything in this lab is offline. The mock LLM has realistic latency distributions per model, and the `slow_provider` scenario multiplies them for the primary provider between 12:00 and 14:00 of the simulated day.

```bash
OFFLINE=1 make replay
uv run python -m northwind.latency report --store .atlas/spans.sqlite
```

Expected:

```text
Latency report: 2,236 requests (atlas.chat)
  p50    1,120 ms     p95   2,140 ms     p99   3,380 ms     mean 1,310 ms     max 6,910 ms
  TTFT   p50 410 ms   p95 980 ms
  Budget p95 <= 4,000 ms: PASS
Cost per session: $0.0421   Budget <= $0.05: PASS
```

And the gate:

```bash
make budget-check
```

```text
tests/budget/test_budget_gate.py::test_cost_per_session_within_budget PASSED
tests/budget/test_budget_gate.py::test_p95_latency_within_budget PASSED
tests/budget/test_budget_gate.py::test_error_rate_within_budget PASSED
```

Record the baseline row in your notes table.

> **Checkpoint 1:** baseline p95 ≈ 2,100 ms, gate green.

---

## Step 2: Inject the slow provider

```bash
OFFLINE=1 ATLAS_SCENARIO=slow_provider make replay
uv run python -m northwind.latency report --store .atlas/spans.sqlite --by hour
```

Expected (abridged):

```text
Latency report: 2,236 requests
  p50    1,340 ms     p95   9,870 ms     p99  21,400 ms     mean 2,480 ms     max 41,200 ms
  Budget p95 <= 4,000 ms: FAIL (+5,870 ms)
Cost per session: $0.0468   Budget <= $0.05: PASS

By hour (p95 ms):  09: 2,090  10: 2,150  11: 2,210  12: 18,900  13: 19,600  14: 2,300  15: 2,180 ...
```

Now find *where* the time went. Compare generation spans inside and outside the window:

```bash
uv run python -m telemetry.local_store query \
  "SELECT strftime('%H', start_time) h, count(*) n,
          round(avg(duration_ms)) mean_ms,
          sum(case when status='ERROR' then 1 else 0 end) errors,
          round(avg(json_extract(attributes,'$.\"atlas.retries\"')),2) retries
   FROM spans WHERE name LIKE 'openai.chat%' GROUP BY h"
```

```text
h   n     mean_ms   errors  retries
11  412   690       0       0.00
12  438   8,410     71      1.62
13  455   8,930     84      1.71
14  420   702       0       0.01
```

Three facts: individual model calls take ~8 s instead of ~0.7 s; 16% of them error (timeouts); and each errored call is retried 1.6 times on average, **after** waiting the full 20 s timeout. A single request with two timeouts and a retry spends 60 s before failing. That is the tail.

> **Checkpoint 2:** p95 ≈ 9,900 ms, gate red, and you can name the two-hour window and the retry multiplier.

---

## Step 3: Shorten the timeout (and learn why alone it is not enough)

Create `.env.chaos` from `.env` and change:

```dotenv
ATLAS_SCENARIO=slow_provider
ATLAS_REQUEST_TIMEOUT_S=6
```

```bash
OFFLINE=1 uv run --env-file .env.chaos python -m simulator.replay
uv run python -m northwind.latency report --store .atlas/spans.sqlite
```

Expected:

```text
p95   7,120 ms   p99  13,800 ms   Budget p95 <= 4,000 ms: FAIL (+3,120 ms)
Error rate 12:00-14:00: 31%   (was 16%)
Cost per session: $0.0439
```

p95 improved because failures are faster, but the error rate doubled: calls that would have finished in 8 s are now cut off at 6 s and retried, and the retry hits the same slow provider. Cheaper, faster, and worse for users. Write that in your notes; it is the trap of lecture 7.3.

> **Checkpoint 3:** you can explain why a shorter timeout without a fallback trades latency for errors.

---

## Step 4: Turn on the Router with a fallback

```dotenv
ATLAS_ROUTER_MODE=1
ATLAS_REQUEST_TIMEOUT_S=6
ATLAS_MAX_RETRIES=1
```

Open `app/agent.py` and find the Router construction (router mode). It should read:

```python
from litellm import Router

router = Router(
    model_list=[
        {"model_name": "atlas-primary",  "litellm_params": {"model": settings.model,             # gpt-4.1-mini
                                                             "timeout": settings.request_timeout_s}},
        {"model_name": "atlas-fallback", "litellm_params": {"model": settings.degraded_model,    # gpt-4.1-nano
                                                             "timeout": settings.request_timeout_s}},
        {"model_name": "atlas-escalate", "litellm_params": {"model": settings.escalation_model}}, # gpt-4.1
    ],
    fallbacks=[{"atlas-primary": ["atlas-fallback"]}],
    num_retries=settings.max_retries,
    timeout=settings.request_timeout_s,
    allowed_fails=3,          # failures per minute before a deployment is cooled down
    cooldown_time=60,         # seconds a deployment stays out of rotation
)
```

In offline mode the mock provider honours the same knobs: `atlas-fallback` is served by a second simulated provider that is **not** slowed by the scenario. Replay again:

```bash
OFFLINE=1 uv run --env-file .env.chaos python -m simulator.replay
uv run python -m northwind.latency report --store .atlas/spans.sqlite
```

Expected:

```text
p50 1,180 ms   p95 4,610 ms   p99 7,900 ms   Budget p95 <= 4,000 ms: FAIL (+610 ms)
Fallback rate 12:00-14:00: 38%   Error rate: 2.1%
Cost per session: $0.0402
```

Big improvement: errors are back near zero and cost went *down* (nano is cheaper). But p95 is still over. Look at how a fallback request is shaped:

```bash
uv run python -m telemetry.local_store spans --where "json_extract(attributes,'$.\"northwind.fallback\"')=1" --last 1 --tree
```

```text
atlas.chat                                            7,240 ms
└── atlas.step 1
    ├── openai.chat gpt-4.1-mini   status=ERROR timeout   6,010 ms   atlas.retries=0
    └── openai.chat gpt-4.1-nano   fallback=true            1,190 ms
```

Every fallback request still pays the full 6 s timeout first. With a 38% fallback rate in the window, that is the p95.

> **Checkpoint 4:** fallback works, errors are near zero, p95 ≈ 4,600 ms.

---

## Step 5: Let the circuit breaker do its job

The Router already cools down a deployment after `allowed_fails` failures per minute. Check whether it is firing:

```bash
uv run python -m telemetry.local_store query \
  "SELECT count(*) FROM spans WHERE name='router.cooldown' "
```

If the answer is `0`, look at `allowed_fails=3` against the traffic: in the slow window the primary fails about 4 times per minute, so the breaker opens late and closes again (half-open probe) as soon as one call succeeds, then re-opens. Tune:

```dotenv
ATLAS_REQUEST_TIMEOUT_S=4
ATLAS_ROUTER_ALLOWED_FAILS=2
ATLAS_ROUTER_COOLDOWN_S=120
```

(`config.py` exposes these as `router_allowed_fails` and `router_cooldown_s`; if your checkout does not have them yet, pass them directly to `Router(...)`.)

```bash
OFFLINE=1 uv run --env-file .env.chaos python -m simulator.replay
uv run python -m northwind.latency report --store .atlas/spans.sqlite
make budget-check
```

Expected:

```text
p50 1,160 ms   p95 3,420 ms   p99 5,100 ms   Budget p95 <= 4,000 ms: PASS
Fallback rate 12:00-14:00: 71%   Error rate: 0.9%   Cooldown events: 14
Cost per session: $0.0388   Budget <= $0.05: PASS
```

```text
tests/budget/test_budget_gate.py::test_cost_per_session_within_budget PASSED
tests/budget/test_budget_gate.py::test_p95_latency_within_budget PASSED
tests/budget/test_budget_gate.py::test_error_rate_within_budget PASSED
```

While the breaker is open, requests go **straight** to the fallback without paying the timeout, so the tail collapses. The fallback rate went *up* (71%): that is the breaker doing its job, not a problem.

> **Checkpoint 5:** gate green under chaos with p95 ≈ 3,400 ms and cost per session ≈ $0.039.

---

## Step 6: Check what you traded away

Fast and cheap is not the whole story. Two more numbers before you declare victory:

1. **Quality.** `gpt-4.1-nano` answers 71% of the requests in the slow window. Run the offline judge on that window (the mock judge scores nano answers lower on `grounded`):

   ```bash
   OFFLINE=1 uv run python -m evals.online_judge --store .atlas/spans.sqlite --from 12:00 --to 14:00 --sample 1.0
   ```

   Expected: mean `resolved` 0.86 in the window vs 0.93 outside. Acceptable for two hours of degraded mode; not acceptable as a permanent state. Write it down.

2. **Escalations.** Check that `atlas-escalate` (gpt-4.1) is *not* in the fallback chain. If your tuning made the escalation model a fallback for the primary, cost per session would still pass here but would triple on a real outage with real prompts. Confirm with the query from Step 2 that `gpt-4.1` call counts did not change between baseline and chaos.

> **Checkpoint 6:** you have the judge score delta and confirmed gpt-4.1 usage is unchanged.

---

## Step 7: Write it up

`notes/lab-04.md`:

```markdown
# Lab 4: chaos tuning

| Run | timeout_s | retries | router | allowed_fails / cooldown | p95 ms | p99 ms | error % (12-14) | fallback % | cost/session | gate |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline | 20 | 2 | off | - | | | | | | PASS |
| Chaos | 20 | 2 | off | - | | | | | | FAIL |
| Short timeout | 6 | 2 | off | - | | | | | | FAIL |
| Fallback | 6 | 1 | on | 3 / 60 | | | | | | FAIL |
| Breaker tuned | 4 | 1 | on | 2 / 120 | | | | | | PASS |

## What I would ship
- Settings:
- Why each one (one line, with the number that justified it):
- What degrades during an outage and for how long:
- The alert I would add so a human knows the breaker is open:
```

> **Checkpoint 7:** every row has numbers and every setting has a reason.

---

## Stretch goal

1. Add the per-tenant concurrency limit from lecture 7.5: `ATLAS_TENANT_MAX_INFLIGHT=8`. Replay with `slow_provider` and check that `finance` (the noisiest tenant in the window) is shed with `429` while other tenants keep their p95.
2. Make `create_ticket` idempotent with an idempotency key derived from `(session_id, step, arguments hash)`, then run `ATLAS_SCENARIO=retry_storm` and assert with a query that no session created two tickets with the same key. Retries that create duplicate tickets are a cost event *and* a data quality event.
3. Use the shipped counter `atlas_model_fallbacks_total{from_model,to_model}` and add a gauge `atlas_circuit_open{model}` in `telemetry/metrics.py` (fed from `CircuitBreaker.state`). You will alert on them in Lab 6.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Chaos replay shows the same p95 as baseline | `ATLAS_SCENARIO` not picked up | The replay reads `.env` first; pass `--env-file .env.chaos` or export the variable in the shell |
| `Router` import error | `litellm` not installed or router mode off | `uv sync`; set `ATLAS_ROUTER_MODE=1` |
| Fallback never fires | Fallbacks keyed by the wrong name | `fallbacks=[{"atlas-primary": ["atlas-fallback"]}]` uses `model_name`s, not the underlying model ids |
| Error rate goes *up* after adding the router | `num_retries` on the Router plus retries in your own code | Remove your own retry loop; let the Router own retries and fallbacks |
| Cooldown events stay at 0 | `allowed_fails` too high for the failure rate, or cooldown too short | Lower `allowed_fails`, lengthen `cooldown_time`; count `router.cooldown` spans |
| Cost per session fails after tuning | Escalation model used as fallback | Fallback to `degraded_model` (nano), never to `escalation_model` |
| `make budget-check` passes but the report says FAIL | Gate and report reading different stores | Both default to `ATLAS_LOCAL_STORE`; make sure the replay wrote where the gate reads |
| p95 differs slightly from the numbers here | Different seed | Use `--seed 42`; the shape of the results matters more than the exact values |

---

## Solution notes

Reference settings (`03-code/.env.chaos.example`) and the reasoning:

| Setting | Value | Justified by |
|---|---|---|
| `ATLAS_REQUEST_TIMEOUT_S` | 4 | Baseline p99 of a single model call is 3.4 s; a 4 s timeout cuts off only genuinely stuck calls |
| `ATLAS_MAX_RETRIES` | 1 | A second retry against a slow provider doubles tail latency and produced the retry storm's cost |
| `ATLAS_ROUTER_MODE` | 1 with `atlas-primary → atlas-fallback (nano)` | Errors 16% → 0.9%; cost down because nano is cheaper |
| `allowed_fails` / `cooldown_time` | 2 / 120 s | Breaker opens within the first minute of the slowdown and stays open long enough to skip the timeout on most requests |
| Escalation model | never a fallback | Keeps cost per session flat under outage |

Reference results (seed 42): p95 3,420 ms, p99 5,100 ms, error 0.9%, fallback 71% in window, cost per session $0.0388, judge `resolved` 0.86 in window vs 0.93 outside.

Common weak solutions and why they lose points:

- **Timeout only** (Step 3): passes nothing, doubles errors. Fast failure is still failure.
- **Retries up to 5**: p95 explodes and the retry storm becomes a cost incident. Retries are for transient blips, not for a provider that is slow for two hours.
- **Fallback to gpt-4.1**: passes the p95 gate, fails cost in any realistic outage, and hides the outage behind a better model so nobody investigates.
- **Budget raised to 10 s**: the gate exists to protect users; moving the goalposts is not tuning.

Key takeaways:

1. p95 is dominated by *how long you wait before giving up* multiplied by *how often you have to*. Timeouts set the first factor; breakers set the second.
2. Every reliability knob has a cost and a quality shadow. Report all three or you are not done.
3. The fallback rate going up is the system working. Alert on the breaker being open for too long, not on fallbacks happening.

Reference implementation: `03-code/app/agent.py` (router mode), `03-code/src/northwind/latency.py`, `03-code/tests/budget/test_budget_gate.py`.
