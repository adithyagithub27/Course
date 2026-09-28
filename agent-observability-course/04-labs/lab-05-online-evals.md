# Lab 5: Build the Quality Page of the Ops Console

| Field | Details |
|---|---|
| **Section / lecture** | Section 8, lecture 8.7 |
| **Time estimate** | 90 minutes |
| **Difficulty** | Intermediate to advanced |
| **Goal** | Run sampled LLM-as-judge scoring over a replayed week, capture user feedback, correlate the two, compute drift between week 1 and week 2, and surface all of it on a **Quality** tab in the Streamlit Ops Console. Along the way, put a price on judging itself. |
| **You will produce** | `console/pages/quality.py` (a new Ops Console tab), judge scores in the local store (and Langfuse if online), `evals/out/drift-report.md`, and `notes/lab-05.md` |

---

## Prerequisites

- Labs 1 to 4 complete.
- Lectures 8.1 to 8.6 watched.
- `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py`, `src/northwind/sampling.py`, `src/northwind/drift.py` and `console/ops_console.py` open.
- Online path only: `OPENAI_API_KEY` (the judge costs about $0.40 for this lab at a 10% sample) and Langfuse keys.

## The story

Two simulated weeks of Atlas traffic. In week 2, prompt version `v2` went live on Wednesday (the change that becomes Incident 3 in Section 11). Nothing is red: error rate, latency and cost are flat. Users are less happy. Your job is to build the page that would have shown it.

---

## Step 1: Replay two weeks

```bash
OFFLINE=1 uv run python simulator/replay.py --seed 42 --sessions 4000 --store .atlas/week1.sqlite --clear
OFFLINE=1 uv run python simulator/replay.py --seed 43 --sessions 4000 --incidents quality_drift --store .atlas/week2.sqlite --clear
```

(Each replayed day stands in for one week; `week1` is a clean day, `week2` carries the `quality_drift` preset.)

Expected (second command):

```text
Replay seed=43  requests=10173  sessions=4000  spans=70450  scores=12148  feedback=1276
Total cost $20.29   p95 latency 3504 ms   elapsed 17.9s
Cost by tenant: eng=$4.38, finance=$3.97, hr=$4.21, ops=$7.72
Outcomes: escalated=63, guardrail=73, resolved=10037
Scenarios: none=3729, prompt_regression=6444
Incidents: prompt_regression@11-24h
Store: .atlas/week2.sqlite  (total spans now 70450)
```

The `quality_drift` preset (`simulator.scenarios.INCIDENT_PRESETS`) runs the `prompt_regression` scenario from 11:00, which switches the prompt to `v2` and makes the mock LLM produce shorter, less grounded answers for policy questions. Each generation carries `atlas.prompt_version` so you can slice by it later.

> **Checkpoint 1:** two stores exist, `.atlas/week1.sqlite` and `.atlas/week2.sqlite` (treat the store path as the "label" in the code you write below).

---

## Step 2: Choose a sampling policy

Judging every trace with an LLM would cost more than serving some of them. `src/northwind/sampling.py` offers:

| Policy | What it keeps | Use |
|---|---|---|
| `UniformSampler(rate)` | a random `rate` of traces | baseline quality estimate |
| `StratifiedSampler(rate, by="tenant")` | `rate` **per tenant** | small tenants are not drowned out |
| `TailSampler(rate, always=("error", "negative_feedback", "escalated", "step_limit"))` | 100% of traces matching `always`, `rate` of the rest | where the bad ones are |

Preview each policy without judging:

```bash
uv run python -m northwind.sampling preview --store .atlas/spans.sqlite --label week2 --rate 0.1 --policy uniform
uv run python -m northwind.sampling preview --store .atlas/spans.sqlite --label week2 --rate 0.1 --policy tail
```

Expected:

```text
uniform  rate=0.10  selected 1,566 / 15,660   errors kept 19/187 (10%)   negative feedback kept 31/312 (10%)
tail     rate=0.10  selected 2,014 / 15,660   errors kept 187/187 (100%)  negative feedback kept 312/312 (100%)
```

Tail sampling keeps every error and every thumbs-down for 29% more judge calls. Take it. Note the trade: your judged sample is now **biased** toward bad traces, so never report the mean judge score of a tail sample as "quality". Report the uniform slice for the headline number and the tail extras for investigation. The judge writes `northwind.sample_reason` (`uniform` / `always:error` / ...) on every score so you can separate them later.

> **Checkpoint 2:** you can say how many judge calls each policy costs and why tail sampling keeps all errors.

---

## Step 3: Run the online judge

The judge is DeepEval `GEval` with three agent-specific criteria (`evals/online_judge.py`):

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

RESOLVED = GEval(
    name="resolved",
    criteria="The answer fully addresses the employee's request or clearly hands off with a ticket. "
             "Partial or generic answers score low.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.7, model=settings.judge_model,
)
GROUNDED = GEval(
    name="grounded",
    criteria="Every policy claim in the answer is supported by the retrieved knowledge base passages. "
             "Invented numbers, dates or entitlements score 0.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT,
                       LLMTestCaseParams.RETRIEVAL_CONTEXT],
    threshold=0.7, model=settings.judge_model,
)
SAFE_ESCALATION = GEval(
    name="safe_escalation",
    criteria="Password resets, payroll changes and access requests are only actioned after identity "
             "verification, otherwise the agent escalates. Reward correct refusals.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.8, model=settings.judge_model,
)
```

**Offline path:** the mock judge (`OFFLINE=1`) scores deterministically from the trace's hidden ground truth plus noise, so the numbers below are reproducible.

```bash
OFFLINE=1 uv run python -m evals.online_judge --store .atlas/spans.sqlite --label week1 --policy tail --rate 0.1
OFFLINE=1 uv run python -m evals.online_judge --store .atlas/spans.sqlite --label week2 --policy tail --rate 0.1
```

Expected (week 2):

```text
Judging 2,014 traces with gpt-4.1-mini (mock)   criteria: resolved, grounded, safe_escalation
  ... 2,014/2,014
Scores written: 6,042   judge tokens: 3,214,800 in / 241,700 out   judge cost: $1.67
Uniform slice means: resolved 0.88  grounded 0.81  safe_escalation 0.97
```

That last line is the price of judging: **$1.67 to judge a week that cost $246 to serve** (0.7%). Write both numbers down; they go on the page as a line item. At 100% sampling it would be $16.70 (6.8%).

**Online path:** drop `OFFLINE=1`, add `--limit 200` the first time (about $0.20), and add `--write-langfuse` so scores also land in Langfuse via `client.create_score(trace_id=..., name="judge_grounded", value=...)`. In Langfuse → **Scores** you will see `judge_resolved`, `judge_grounded`, `judge_safe_escalation` per trace, filterable by `metadata.prompt_version`.

> **Checkpoint 3:** scores exist for both weeks and you know the judge cost as a percentage of serving cost.

---

## Step 4: Feedback and the correlation

The simulator also emitted `/feedback` calls (thumbs up/down with an optional reason) for about 8% of sessions. Import them as scores and correlate with the judge:

```bash
uv run python -m evals.feedback correlate --store .atlas/spans.sqlite --label week2
```

Expected:

```text
Feedback: 1,262 sessions with feedback (8.1%)   up 950   down 312
Judge score on thumbs-up sessions:    resolved 0.93   grounded 0.88
Judge score on thumbs-down sessions:  resolved 0.61   grounded 0.52
Agreement (judge resolved >= 0.7 vs thumbs up): 84%
Sessions with NO feedback: 14,398   judge resolved 0.87   (survivorship check: close to the thumbs-up group? no -> feedback is not representative)
```

Read the last line carefully. The silent majority scores 0.87, the thumbs-up group 0.93: people who bother to click are happier than average, and people who click thumbs-down are a small, angry minority. That is survivorship bias (lecture 8.3). Feedback tells you *what* went wrong on the traces that have it; the judge tells you *how often*.

> **Checkpoint 4:** you can state the agreement rate and explain why feedback alone would overstate quality.

---

## Step 5: Drift: this week versus last week

```bash
mkdir -p evals/out
uv run python evals/drift_report.py --baseline-store .atlas/week1.sqlite --store .atlas/week2.sqlite > evals/out/drift-report.md
cat evals/out/drift-report.md
```

Expected (abridged):

```markdown
# Drift report: .atlas/week1.sqlite -> .atlas/week2.sqlite

| Metric | week1 | week2 | delta | PSI | status |
|---|---|---|---|---|---|
| judge resolved (uniform) | 0.92 | 0.88 | -0.04 | 0.06 | watch |
| judge grounded (uniform) | 0.90 | 0.81 | -0.09 | 0.19 | **alert** |
| judge safe_escalation | 0.97 | 0.97 | 0.00 | 0.01 | ok |
| thumbs-down rate | 1.4% | 2.0% | +0.6 pp | - | watch |
| cost / session | $0.0431 | $0.0455 | +5.6% | 0.03 | ok |
| p95 latency ms | 2,140 | 2,210 | +3.3% | 0.02 | ok |
| answer length (tokens) | 96 | 71 | -26% | 0.31 | **alert** |

## By prompt version (week2)
| prompt_version | requests | resolved | grounded | answer tokens |
|---|---|---|---|---|
| v1 (Mon-Tue) | 4,410 | 0.92 | 0.90 | 95 |
| v2 (Wed-Sun) | 11,250 | 0.86 | 0.77 | 62 |
```

PSI (population stability index, `northwind.drift.psi`) thresholds: < 0.1 stable, 0.1-0.25 moderate shift, > 0.25 significant. `grounded` shifted moderately; answer length shifted significantly; and the by-version table names the culprit. Nothing in cost or latency moved. This is what "users are unhappy but nothing is red" looks like in data.

> **Checkpoint 5:** the drift report flags `grounded` and answer length, and the prompt-version breakdown shows v2 is worse.

---

## Step 6: Build the Quality tab

Create `console/pages/quality.py`. The Ops Console auto-discovers pages in `console/pages/`. Use the store helpers in `console/data.py`; each returns a pandas DataFrame.

```python
import streamlit as st

from console.data import (feedback_by_day, judge_scores_by_day, judge_scores_by_prompt_version,
                          judge_cost_by_day, drift_table, worst_traces)

st.title("Quality")

label = st.sidebar.selectbox("Window", ["week2", "week1"])
baseline = "week1" if label == "week2" else None
tenant = st.sidebar.selectbox("Tenant", ["all", "ops", "finance", "hr", "eng"])

scores = judge_scores_by_day(label, tenant=tenant, slice="uniform")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Resolved (judge)", f"{scores['resolved'].mean():.2f}")
c2.metric("Grounded (judge)", f"{scores['grounded'].mean():.2f}")
fb = feedback_by_day(label, tenant=tenant)
c3.metric("Thumbs-down rate", f"{fb['down'].sum() / fb['sessions'].sum():.1%}")
cost = judge_cost_by_day(label)
c4.metric("Judge cost", f"${cost['usd'].sum():.2f}", help="Cost of judging as a share of serving cost")

st.subheader("Judge scores per day (uniform slice only)")
st.line_chart(scores.set_index("day")[["resolved", "grounded", "safe_escalation"]])

st.subheader("Feedback per day")
st.bar_chart(fb.set_index("day")[["up", "down"]])

if baseline:
    st.subheader(f"Drift: {label} vs {baseline}")
    drift = drift_table(baseline, label, tenant=tenant)
    st.dataframe(drift.style.map(lambda s: "background-color:#7f1d1d;color:white" if s == "alert" else "",
                                 subset=["status"]))

st.subheader("By prompt version")
st.dataframe(judge_scores_by_prompt_version(label, tenant=tenant))

st.subheader("Worst 20 traces (tail sample)")
worst = worst_traces(label, tenant=tenant, n=20)
st.dataframe(worst[["trace_id", "tenant", "prompt_version", "resolved", "grounded", "feedback", "sample_reason"]])
```

Run it:

```bash
make console
```

Open **Quality** in the sidebar. Switch tenant to `hr`: the grounded drop is sharpest there (policy questions are where v2 got vaguer). Click a trace id in the worst-20 table to open it in the Trace explorer.

> **Checkpoint 6:** the Quality tab shows the four metrics, the daily lines dipping from Wednesday of week 2, the drift table with two alerts and the by-version breakdown.

---

## Step 7: From worst trace to regression test

Pick the three worst `grounded` traces from `hr`. Promote them to a dataset (lecture 8.6):

```bash
OFFLINE=1 uv run python -m evals.to_dataset --store .atlas/spans.sqlite --label week2 --criterion grounded --below 0.4 --limit 3 --dataset atlas-failures
```

Expected:

```text
Created dataset atlas-failures (local: evals/out/datasets/atlas-failures.jsonl)
  + trace 8c1e...  input="How many weeks of parental leave..."  expected_output=<KB passage>  source_trace_id=8c1e...
  + trace 21aa...  ...
  + trace f07b...  ...
```

Online, the same command with `--write-langfuse` calls `client.create_dataset(name="atlas-failures")` and `client.create_dataset_item(dataset_name=..., input=..., expected_output=..., source_trace_id=...)`, so each item links back to its production trace. This dataset is what a Course 2 style offline eval would run against prompt v3 before it ships.

> **Checkpoint 7:** three failing traces are a dataset with `source_trace_id` links.

---

## Step 8: Notes

`notes/lab-05.md`:

```markdown
# Lab 5

- Sampling policy chosen and why:
- Judge calls per week / judge cost / share of serving cost:
- Judge-feedback agreement and the survivorship number:
- Drift alerts and the metric that named the cause:
- Screenshot of the Quality tab (hr tenant):
- The alert rule I would write from this page (metric, window, threshold):
```

---

## Stretch goal

1. Add a **judge agreement** panel: judge the same 100 traces twice (`--seed 1`, `--seed 2` offline, or two real runs online) and report Cohen's kappa on the pass/fail decision. If kappa is under 0.6 your criteria are too vague to alert on.
2. Add a `refusal_rate` and `pii_in_output_rate` line (lecture 8.4) from `telemetry/metrics.py` counters stored in the local store.
3. Make the drift report post a Markdown summary to a webhook (Slack-shaped JSON) when any row is `alert`. You will wire the real alert in Lab 6.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `deepeval` import error | `dev` extra not installed | `uv sync --extra dev` |
| Online judge asks for a DeepEval login / telemetry prompt | DeepEval CLI first run | `export DEEPEVAL_TELEMETRY_OPT_OUT=YES`; no account is needed for `GEval` with your own model |
| Judge scores all 1.0 offline | Wrong label, so it judged week 1 with no regression | Check `--label week2` and that the week-2 replay used `ATLAS_SCENARIO=prompt_regression` |
| `drift_report` says "insufficient baseline" | Fewer than 200 scored traces in the baseline | Judge week 1 too (Step 3 runs both) |
| Quality tab not in the sidebar | File not under `console/pages/` or has a syntax error | Check the Streamlit terminal for the traceback |
| Headline `resolved` looks too low | You averaged the tail sample | Filter `slice="uniform"` for headline numbers |
| Langfuse scores not visible | Missing `--write-langfuse`, or scores buffered | Add the flag; the script calls `flush()` at the end, wait a few seconds |
| Judge cost much higher than expected online | Sample rate 1.0 or `--limit` missing | Start with `--rate 0.1 --limit 200` |

---

## Solution notes

Reference files: `03-code/console/pages/quality.py`, `03-code/evals/online_judge.py`, `03-code/evals/feedback.py`, `03-code/evals/drift_report.py`, `03-code/src/northwind/sampling.py`, `03-code/src/northwind/drift.py`.

Reference numbers (seeds 42/43, tail policy at 10%):

| Item | Value |
|---|---|
| Judge calls week 2 | 2,014 traces × 3 criteria = 6,042 scores |
| Judge cost | $1.67 (0.7% of $246 serving cost); $16.70 at 100% |
| Uniform means week 1 → week 2 | resolved 0.92 → 0.88, grounded 0.90 → 0.81, safe_escalation 0.97 → 0.97 |
| Judge/feedback agreement | 84% |
| Survivorship gap | silent sessions 0.87 vs thumbs-up 0.93 |
| PSI alerts | grounded 0.19 (moderate), answer length 0.31 (significant) |
| Root cause slice | prompt v2: grounded 0.77 vs v1 0.90 |

What separates a strong Quality page from a weak one:

- Headline metrics come from the **uniform** slice; tail extras are for the worst-N table. Mixing them makes quality look worse after every incident and better after every quiet week.
- Judge cost is on the page as a first-class number. Observability that hides its own cost gets switched off by the first finance review.
- The page can slice by `prompt_version`, `tenant` and `model`. Drift alone says "something changed"; the slice says *what*.
- Worst traces link to the Trace explorer and to a dataset. A quality page that cannot produce a regression test is a dashboard, not a loop.

Key takeaways:

1. Sample with intent: tail sampling for investigation, uniform for measurement, and label which is which.
2. Feedback is a signal for *which* traces to read, not a measure of quality. The judge is the measure; feedback calibrates it.
3. Drift detection on judge scores catches what cost and latency never will. In Incident 3 (lecture 11.4) this exact page is the only place the regression shows.
