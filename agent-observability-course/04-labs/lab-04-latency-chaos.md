# Lab 4: Hold p95 Under 4 Seconds During Chaos

| Field | Details |
|---|---|
| **Section / lecture** | Section 7, lecture 7.7 |
| **Time estimate** | 75 minutes (45 if you skip the optional online part) |
| **Difficulty** | Intermediate |
| **Goal** | Reproduce the `slow_provider` day, read it from three charts, measure what your own levers buy against it, prove the timeout-breaker-fallback mechanism offline, and (optionally, with a real provider) tune `ATLAS_REQUEST_TIMEOUT_S`, `ATLAS_MAX_RETRIES` and the Router knobs. Every changed setting gets one line of justification from the latency budget worksheet. |
| **You will produce** | `.env.chaos` (from `.env.chaos.example`), `notes/lab-04.md` with a before/after table and the worksheet rows, screenshots of the Latency and Reliability pages |

---

## Prerequisites

- Labs 1 to 3 complete.
- Lectures 7.1 to 7.6 watched, especially 7.3 (timeouts and retries), 7.4 (fallbacks and circuit breakers) and 7.6 (the chaos demo).
- `10-resources/latency-budget-worksheet.md` open.

## What runs where (read this first)

Offline, the mock LLM stamps every call with a *simulated* latency and the replay records it. The `slow_provider` scenario multiplies time to first token by 3.5 and halves tokens per second for 75% of requests between 13:00 and 17:00. The mock **never times out a slow call**: it ignores `timeout=`. So offline you can reproduce the incident, measure your own levers (the context diet, routing) and prove the breaker mechanism with a stalling fake provider, but `ATLAS_REQUEST_TIMEOUT_S`, `ATLAS_MAX_RETRIES` and the Router knobs only change behaviour against a real provider (`OFFLINE=0`). `.env.chaos.example` says the same in its header.

Two Makefile habits to remember: the Makefile exports `CACHE`, `DIET` and `ROUTER` (default 0), so set the levers with `DIET=1` on the `make` line, not with `ATLAS_CONTEXT_DIET=1` in your shell. And Atlas doesn't read `.env` by itself: load a file with `set -a; source .env.chaos; set +a`.

---

## Step 1: Baseline

```bash
OFFLINE=1 make replay STORE=.atlas/base.sqlite
make budget-check PYTEST_ADDOPTS=-s
```

Expected (the replay's summary line and the gate's three printed lines):

```text
Total cost $56.2810   p95 latency 3827 ms   elapsed 19.8s
cost/session $0.01454 (budget $0.05) total $4.36 over 300 sessions
p95 3822 ms (budget 4000 ms) over 781 requests
max input tokens/generation 17,992 (budget 24,000) trace …
5 passed
```

Record the baseline row: p95 3,827 ms on the full day, 3,822 ms on the gate's 300-session replay, cost per session $0.0141.

> **Checkpoint 1:** baseline recorded, gate green.

---

## Step 2: Inject the slow provider

```bash
OFFLINE=1 make replay SCENARIO=slow_provider STORE=.atlas/slow.sqlite
BUDGET_GATE_INCIDENTS=slow_provider make budget-check PYTEST_ADDOPTS=-s
```

Expected:

```text
Total cost $55.8560   p95 latency 8877 ms   elapsed …
Incidents: slow_provider@13-17h
...
p95 8755 ms (budget 4000 ms) over 747 requests
FAILED tests/budget/test_budget_gate.py::test_p95_latency_within_budget
```

Open the console on that store (`make console STORE=.atlas/slow.sqlite`) and take three screenshots:

- **Latency** page: hourly p95 flat around 3.8 s, then about 9.2 to 9.4 s from 13:00 to 17:00, against the 4 s budget line. "Generation detail": TTFT p95 roughly triples in the window.
- **Reliability** page: "No failed LLM attempts in this store." Not one.
- **Cost** page: cost per hour by tenant looks like any other afternoon. The day costs $55.86, slightly *less* than baseline.

Write one sentence in your notes: why does a slow provider produce no retries and no fallbacks? (Nothing failed. The 20-second timeout never fires on a six-second call, and fallbacks fire on failures.)

> **Checkpoint 2:** p95 8,877 ms on the day, gate red on p95, and you can explain the flat Reliability page.

---

## Step 3: What your own levers buy

```bash
BUDGET_GATE_INCIDENTS=slow_provider make budget-check PYTEST_ADDOPTS=-s DIET=1
BUDGET_GATE_INCIDENTS=slow_provider make budget-check PYTEST_ADDOPTS=-s ROUTER=1
BUDGET_GATE_INCIDENTS=slow_provider make budget-check PYTEST_ADDOPTS=-s ATLAS_REQUEST_TIMEOUT_S=4
```

Expected p95 lines:

| Run | p95 (gate, 300 sessions) | Cost per session |
|---|---:|---:|
| slow_provider | 8,755 ms | $0.0138 |
| + `DIET=1` | 8,343 ms | $0.0103 |
| + `ROUTER=1` | 8,755 ms | $0.0118 |
| + `ATLAS_REQUEST_TIMEOUT_S=4` | 8,755 ms | $0.0138 |

The diet buys about 400 ms, because shorter prompts start faster. Routing changes cost, not p95: the slowest requests are long policy answers that stay on `gpt-4.1-mini`. And the timeout changes nothing offline, because the mock ignores it. Milliseconds, not seconds. Record all four rows.

> **Checkpoint 3:** you can say which lever moved p95, by how much, and why the timeout didn't.

---

## Step 4: The mechanism that buys seconds, offline

A timeout only helps if it turns a stall into an error, and the error only helps if the breaker then sends the step somewhere the slowness isn't. Prove the mechanism with the stalling provider from Lecture 7.4:

```bash
OFFLINE=1 OTEL_EXPORTER=none ATLAS_PROMPT_CACHE=0 ATLAS_CONTEXT_DIET=0 PYTHONPATH=.:src python -c "
import logging; logging.disable(logging.WARNING)
import httpx, openai
from app.agent import AtlasAgent
from app.mock_llm import MockLLM

class StallingProvider(MockLLM):
    '''gpt-4.1-mini never answers within the timeout; every other model does.'''
    def chat(self, *, model, **kw):
        if model == 'gpt-4.1-mini':
            raise openai.APITimeoutError(request=httpx.Request('POST', 'https://api.openai.com/v1/chat/completions'))
        return super().chat(model=model, **kw)

a = AtlasAgent(llm=StallingProvider(seed=7))
for i in range(3):
    r = a.run('When is payroll paid?', tenant='hr')
    print(i + 1, r.outcome, r.model, f'retries={r.retries} fallbacks={r.fallbacks} cost=\${r.cost_usd:.5f}')
print('breaker:', a.breaker.state('gpt-4.1-mini'))
"
```

Expected:

```text
1 error gpt-4.1-mini retries=3 fallbacks=0 cost=$0.00302
2 resolved gpt-4o-mini retries=0 fallbacks=2 cost=$0.00167
3 resolved gpt-4o-mini retries=0 fallbacks=2 cost=$0.00167
breaker: open
```

The first request pays for the lesson: three timed-out attempts, all billed. They open the circuit (three consecutive failures), and every later step goes to `FALLBACKS["gpt-4.1-mini"]`, which is `gpt-4o-mini`. Then pin it:

```bash
python -m pytest -q tests/unit/test_agent.py -k "slow_provider or fallback"
```

Expected: `2 passed`.

> **Checkpoint 4:** you can explain the three numbers in request 1 and why requests 2 and 3 never touch `gpt-4.1-mini`.

---

## Step 5 (optional, real provider): tune the timeout

Only with an OpenAI key **and a hard spending cap** (Lecture 2.1; $10 a month is plenty). The real provider is not slow on demand, so the experiment here is the one 7.6 warned about: a timeout that's too tight.

```bash
cp .env.chaos.example .env.chaos
# edit .env.chaos: OFFLINE=0, ATLAS_SCENARIO= (empty), ATLAS_REQUEST_TIMEOUT_S=1, keep ATLAS_ROUTER_MODE=1
set -a; source .env; source .env.chaos; set +a
make run                                  # terminal 1
make swarm RPS=1 DURATION=60              # terminal 2: about 60 real requests
curl -sL localhost:8000/metrics | grep -E '^atlas_llm_retries_total|^atlas_model_fallbacks_total'
```

With a one-second timeout, healthy calls start timing out: retries and fallbacks appear, the swarm's `cost=` summary goes up and p95 barely moves. Now set `ATLAS_REQUEST_TIMEOUT_S` from the worksheet (about twice your slowest normal call; Lecture 7.3 lands near 6 s), restart, and run the swarm again. Record both runs. Real-provider numbers vary by region and hour: record yours, not mine.

> **Checkpoint 5 (optional):** two online rows: too tight, and worksheet-derived.

---

## Step 6: Write it up

`notes/lab-04.md`:

```markdown
# Lab 4: chaos tuning

| Run | Where | Settings | p95 ms | Cost/session | Retries / fallbacks | Gate |
|---|---|---|---:|---:|---|---|
| Baseline | offline | defaults | 3,822 | $0.0145 | 0 / 0 | PASS |
| slow_provider | offline | defaults | 8,755 | $0.0138 | 0 / 0 | FAIL |
| + diet | offline | DIET=1 | 8,343 | $0.0103 | 0 / 0 | FAIL |
| + router | offline | ROUTER=1 | 8,755 | $0.0118 | 0 / 0 | FAIL |
| Stalling provider | offline script | breaker 3 / fallback gpt-4o-mini | n/a | $0.00167 after open | 3 / 2 | n/a |
| Too-tight timeout | online (optional) | TIMEOUT_S=1 | | | | |
| Worksheet timeout | online (optional) | TIMEOUT_S=… | | | | |

## What I would ship, and why (one line per setting, citing a worksheet row)
- ATLAS_REQUEST_TIMEOUT_S =
- ATLAS_MAX_RETRIES =
- ATLAS_ROUTER_ALLOWED_FAILS / ATLAS_ROUTER_COOLDOWN_S =
- ATLAS_TENANT_MAX_INFLIGHT =
- Where the fallback goes (a model or provider the slowness isn't):
- The alert that tells a human the breaker is open:
```

> **Checkpoint 6:** every row has numbers and every setting has a reason.

---

## Stretch goals

1. Per-tenant queues (Lecture 7.5): `make run`, then `make swarm RPS=5 DURATION=30` from two terminals at once. Watch `atlas_requests_shed_total{tenant}` and `atlas_queue_wait_seconds` on `curl -sL localhost:8000/metrics`. Which tenant is shed first with the default `ATLAS_TENANT_MAX_INFLIGHT=ops=13,eng=7,finance=6,hr=6,other=2`, and why?
2. Make `create_ticket` idempotent with a key derived from `(session_id, step, arguments hash)`, then replay `SCENARIO=retry_storm` and check that no session creates two tickets with the same key.
3. Add a gauge `atlas_circuit_open{model}` in `telemetry/metrics.py`, fed from `CircuitBreaker.state`, next to the shipped `atlas_model_fallbacks_total`. It is not in the repo; you'll alert on it in Lab 6.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `DIET=1` changes nothing | You set `ATLAS_CONTEXT_DIET=1` in the shell; the Makefile overrides it with `DIET` | Put `DIET=1` on the `make` line |
| Timeout or Router settings change nothing offline | Expected: the mock ignores `timeout=` and never fails a slow call | Use Step 4 offline; Step 5 needs `OFFLINE=0` |
| `.env.chaos` settings ignored | Atlas doesn't load env files | `set -a; source .env.chaos; set +a` in the same shell |
| `make budget-check` passes under chaos | `BUDGET_GATE_INCIDENTS` not set on the same line | `BUDGET_GATE_INCIDENTS=slow_provider make budget-check` |
| `curl localhost:8000/metrics` prints nothing | `/metrics` redirects to `/metrics/` | `curl -sL` |
| Online cost climbs during Step 5 | The tight timeout bills every timed-out attempt's input | That's the lesson; stop the swarm and raise the timeout |

---

## Solution notes

The offline rows are deterministic and are the graded part:

| Run | p95 (gate) | Cost/session |
|---|---:|---:|
| Baseline | 3,822 ms | $0.0145 |
| slow_provider | 8,755 ms | $0.0138 |
| + diet | 8,343 ms | $0.0103 |
| + router | 8,755 ms | $0.0118 |

Full day (`make replay SCENARIO=slow_provider`): p95 8,877 ms, $55.86. The reference `.env.chaos.example` values are a starting point for a real provider (timeout 4 s, one retry, Router on, `allowed_fails` 2, cooldown 120 s, eight in-flight slots per tenant), not a guaranteed pass.

What good answers say:

1. A slow provider is a silent incident: p95 red, retries, fallbacks and cost flat. Nothing fails, so nothing falls back.
2. Your own levers buy milliseconds (the diet, about 400 ms at p95 here). Seconds come from a timeout that turns a stall into an error, plus a fallback somewhere the slowness isn't. The stalling-provider run shows the mechanism; its first request pays for the lesson.
3. A timeout that's too tight is its own incident: healthy calls time out, every attempt is billed, p95 barely moves.
4. The offline gate stays red under `slow_provider`, and that's correct: the gate checks what your change controls, not what the provider does.

Common weak solutions: raising `BUDGET_P95_LATENCY_MS` (moving the goalposts), falling back to `gpt-4.1` (passes latency on a real outage, fails cost), and more retries (more waiting when nothing errors; more billed attempts when it does).

Reference implementation: `03-code/app/agent.py` (`_call_model`, `CircuitBreaker`, `FALLBACKS`, `build_router_config`), `03-code/.env.chaos.example`, `03-code/tests/unit/test_agent.py`, `03-code/tests/budget/test_budget_gate.py`.
