# Lab 5: Build the Quality Page of the Ops Console

| Field | Details |
|---|---|
| **Section / lecture** | Section 8, lecture 8.7 |
| **Time estimate** | 90 minutes |
| **Difficulty** | Intermediate to advanced |
| **Goal** | Replay two weeks of Atlas traffic (the second with the prompt regression), run the sampled judge and the feedback correlation, produce the week-over-week drift report, and build your own **Quality** page for the Ops Console from the functions in `console/data.py`. Put a price on judging itself. |
| **You will produce** | `console/pages/13_My_quality.py`, `evals/out/drift-report.md`, `.atlas/dataset.jsonl`, and `notes/lab-05.md` |

---

## Prerequisites

- Labs 1 to 4 complete.
- Lectures 8.1 to 8.6 watched.
- `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py`, `src/northwind/sampling.py`, `console/data.py` and `console/_ui.py` open. Don't open `console/pages/4_Quality.py` yet: it's the reference you compare with at the end.
- Online path only: `OPENAI_API_KEY` with a spending cap (the real judge costs a few dollars at a 10% sample) and Langfuse keys, loaded with `set -a; source .env; set +a`.

## The story

Two simulated weeks of Atlas traffic, stored as two Mondays. Week 38 is the baseline day. In week 39, prompt version `v2` gets the `production` label at 11:00 (the change that becomes Incident 3 in Section 11). Nothing is red: errors, latency and cost are flat or better. Answers are worse. Your job is to build the page that would have shown it.

---

## Step 1: Replay two weeks into one store

```bash
OFFLINE=1 make replay STORE=.atlas/weeks.sqlite
OFFLINE=1 make replay DAY=2026-09-21 SCENARIO=quality_drift KEEP=1 STORE=.atlas/weeks.sqlite
```

Expected:

```text
Replay seed=7  requests=10184  sessions=4000  spans=70560  scores=11884  feedback=1291
Total cost $56.2810   p95 latency 3827 ms   elapsed 19.9s
...
Replay seed=7  requests=10210  sessions=4000  spans=70678  scores=12312  feedback=1307
Total cost $53.6826   p95 latency 3660 ms   elapsed 18.4s
Incidents: prompt_regression@11-24h
Store: .atlas/weeks.sqlite  (total spans now 141238)
```

`KEEP=1` appends instead of clearing, and `DAY=2026-09-21` gives the second day its own session and trace ids (`s07-0921-…`). The second day is cheaper and faster: shorter answers. The replay already judged a 30% sample of each day.

> **Checkpoint 1:** one store, two days, the second one cheaper.

---

## Step 2: Read the sampling policy

Judging every trace with an LLM would cost more than serving some of them. Open `src/northwind/sampling.py`:

| Policy | What it keeps | Used by |
|---|---|---|
| `JudgeSamplingPolicy(rate=0.1)` | every escalation and every thumbs-down, a uniform `rate` of the rest, never errors (nothing to judge) | `evals/online_judge.py` (`JUDGE_SAMPLE_RATE`, default 0.1) |
| `TailSamplingPolicy(base_rate=0.1)` | every error, slow (> 4 s), expensive (> $0.05), long (> 5 steps), escalated or thumbs-down trace, `base_rate` of the rest | the same rules the Collector applies in Lecture 13.2 |

Write two sentences in your notes: why does the judge skip errors, and why must the headline quality number come from the uniform slice, not from the always-judged traces?

> **Checkpoint 2:** you can say which traces are always judged and why that biases a naive mean.

---

## Step 3: Run the judge

```bash
OFFLINE=1 make judge STORE=.atlas/weeks.sqlite
```

Expected:

```text
judge=offline-heuristic candidates=20244 sampled=1430 scored=1430 already_scored=6049 mean_overall=0.842 langfuse_writes=0 est_judge_cost=$3.0888
```

Offline, the heuristic judge scores `grounded` on the presence of a `(Source: …)` line and `resolved` on a next step, deterministically. `est_judge_cost` is what those 1,430 traces would cost with `gpt-4.1-mini` as the judge (three criteria each): about three dollars against $110 of serving for the two days. Write both numbers down; judge cost belongs on the page.

**Online path:** `OFFLINE=0 python evals/online_judge.py --store .atlas/weeks.sqlite --limit 200` uses DeepEval `GEval` (`deepeval` 4.2, `gpt-4.1-mini` as the judge) and writes `judge_*` scores to Langfuse with `create_score`. Start with `--limit` (or `JUDGE_MAX_CALLS`) so a first run costs cents, not dollars.

> **Checkpoint 3:** scores exist for both days and you know the judge cost as a share of serving cost.

---

## Step 4: Feedback and the correlation

```bash
make feedback STORE=.atlas/weeks.sqlite
```

Expected:

```text
feedback=2598 (12.7% of 20394 requests) positive=76% joined_with_judge=934 agreement=79% judge|👍=0.85 judge|👎=0.81
```

Read the last two numbers carefully. The judge scores thumbs-up traces 0.85 and thumbs-down traces 0.81: barely different. Thumbs are noisy, and every replayed comment is just `unhelpful`. Now look at who clicks at all: on the Quality page later, "Feedback rate by session length" shows one-turn sessions rate 12% of the time and two-turn sessions 23%. People who stay longer click more. That's the survivorship and selection problem from Lecture 8.3: feedback tells you *which* traces to read, the judge tells you *how often* things go wrong.

> **Checkpoint 4:** you can state the agreement rate and explain why feedback alone would mislead.

---

## Step 5: Drift, this week versus last week

```bash
mkdir -p evals/out
python -m evals.drift_report --store .atlas/weeks.sqlite --prev 2026-W38 --curr 2026-W39 --out evals/out/drift-report.md
```

Expected (abridged):

```markdown
# Drift report: 2026-W38 -> 2026-W39

**3 alert(s)**: judge_overall, judge_grounded, judge_resolved

| metric | status | baseline mean | current mean | Δ mean | Δ p95 | PSI | reasons |
|---|---|---:|---:|---:|---:|---:|---|
| judge_overall | alert | 0.912 | 0.785 | -13.9% | -0.6% | 1.981 | psi 1.981 >= 0.25 |
| judge_grounded | alert | 0.943 | 0.720 | -23.7% | -1.0% | 2.013 | psi 2.013 >= 0.25; mean moved -23.7% |
| judge_resolved | alert | 0.892 | 0.737 | -17.5% | -0.4% | 3.678 | psi 3.678 >= 0.25; mean moved -17.5% |
| cost_per_request_usd | ok | 0.006 | 0.005 | -4.9% | -2.5% | 0.077 | - |
| latency_ms | watch | 2867.360 | 2126.060 | -25.9% | -4.4% | 1.231 | psi 1.231 >= 0.25 (distribution moved, mean improved) |
| steps | ok | 1.979 | 1.978 | -0.1% | +0.0% | 0.000 | - |
| user_feedback | ok | 0.787 | 0.726 | -7.7% | +0.0% | 0.020 | - |
```

PSI (`northwind.drift.psi`): below 0.1 stable, 0.1 to 0.25 a moderate shift, above 0.25 significant. All three judge scores alert. Cost and latency moved the *good* way. User feedback moved, but not enough to alert. This is what "users are unhappy but nothing is red" looks like in data.

> **Checkpoint 5:** the drift report alerts on all three judge scores and calls latency an improvement.

---

## Step 6: Build the page

The console discovers pages automatically: any file in `console/pages/` appears in the sidebar, ordered by its number prefix. Every page starts with `page(title)` from `console/_ui.py`, which returns a `StoreData` snapshot of the store in the sidebar box plus the settings. The functions in `console/data.py` take that snapshot and return plain lists of dicts that `st.dataframe` and the chart calls accept directly.

Create `console/pages/13_My_quality.py`:

```python
"""Lab 5: my Quality page. Judge scores, prompt versions, feedback and disagreements."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[2]),
    str(Path(__file__).resolve().parents[2] / "src"),
]

import streamlit as st  # noqa: E402

from console._ui import page  # noqa: E402
from console.data import (  # noqa: E402
    disagreements,
    feedback_by_session_length,
    feedback_hourly,
    judge_by_prompt_version,
    judge_feedback_agreement,
    judge_hourly,
    quality_summary,
)

d, settings = page("My quality")
q = quality_summary(d)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Grounded (judge mean)", q["judge_means"].get("grounded", "n/a"), help=f"n={q['judged']}")
c2.metric("Resolved (judge mean)", q["judge_means"].get("resolved", "n/a"))
c3.metric("Feedback rate", f"{q['feedback_rate']:.1%}")
agree = judge_feedback_agreement(d)
c4.metric("Judge vs user agreement", f"{agree['rate']:.0%}" if agree["rate"] is not None else "n/a",
          help=f"{agree['overlap']} traces with both")

st.subheader("Judge scores per hour")
st.line_chart(judge_hourly(d), x="hour", y="mean", color="score")

st.subheader("By prompt version")
st.dataframe(judge_by_prompt_version(d), hide_index=True)

left, right = st.columns(2)
left.subheader("Thumbs-down rate per hour")
left.line_chart(feedback_hourly(d), x="hour", y="thumbs_down_rate")
right.subheader("Feedback rate by session length")
right.bar_chart(feedback_by_session_length(d), x="turns", y="feedback_rate")

st.subheader("Judge and user disagree")
rows = disagreements(d)
for r in rows:
    r["open"] = f"./Traces?trace={r['trace_id']}"
st.dataframe(rows, hide_index=True,
             column_config={"open": st.column_config.LinkColumn("trace", display_text="open trace")})
```

Run it on your store:

```bash
make console STORE=.atlas/weeks.sqlite
```

Open **My quality** in the sidebar. Expected tiles for the two-week store: grounded 0.829, resolved 0.812, feedback rate 12.7%, agreement 67% (this page's agreement uses the judge's `resolved` ≥ 0.7 against the thumbs, over every trace that has both, so it differs from `make feedback`'s 79%; write down which definition you report). "By prompt version" shows v1 grounded 0.941 (n 5,117) against v2 0.586 (n 2,362). Because the store spans two days, hour labels read `09-14 11:00`, `09-21 11:00` and so on; find the step on the 21st at 11:00.

Then open the shipped **Quality** page (`console/pages/4_Quality.py`) and compare. Write `DIFF_NOTES`-style: one thing the reference shows that yours doesn't, one thing yours shows better.

> **Checkpoint 6:** your page shows the four tiles, the hourly lines dropping at 11:00 on the 21st, the by-version table and the disagreement table with links into the Traces page.

---

## Step 7: From worst trace to regression test

```bash
python evals/to_dataset.py --store .atlas/weeks.sqlite --threshold 0.6 --limit 5
```

Expected:

```text
selected=5 written=5 -> .atlas/dataset.jsonl langfuse_items=0
```

Each item has the masked input, tenant, intent, `prompt_version` and `source_trace_id`. Online, add `--langfuse` (or `make dataset LANGFUSE=1`) and the items land in the `atlas-failures` dataset with `create_dataset_item(..., source_trace_id=...)`, each linked to its production trace. That dataset is what a Course 2 style offline eval runs against the next prompt version before it gets a label.

> **Checkpoint 7:** five failing traces in `.atlas/dataset.jsonl`, each with a `source_trace_id`.

---

## Step 8: Notes

`notes/lab-05.md`:

```markdown
# Lab 5

- Sampling: what is always judged, what is sampled, and which slice the headline uses:
- Judge traces / judge cost / share of serving cost:
- Judge-feedback agreement (both definitions) and what session length does to feedback:
- Drift alerts, and the metric that named the cause:
- Screenshot of my Quality page, and my diff against the reference page:
- The alert rule I would write from this page (metric, window, threshold), and why `AtlasJudgeScoreLow` in deploy/alerts.yml can't fire as shipped:
```

---

## Stretch goals

1. Add a judge-cost tile: count the `judge_overall` scores in the store and multiply by the per-trace estimate `evals/online_judge.py` uses (`3 * (1200 * 0.4e-6 + 150 * 1.6e-6)`). Label it "estimate".
2. Add the Safety series from Lecture 8.4: `console.data.safety_hourly(d)` gives injection, refusal and PII-in-output rates per hour.
3. Make the drift report post a Slack-shaped JSON payload to a webhook when any row is `alert`. You'll wire a real alert in Lab 6.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| My page isn't in the sidebar | File not under `console/pages/`, or a syntax error | Check the terminal running `make console` for the traceback |
| The page shows the baseline day only | You replayed the second day without `KEEP=1`, which cleared the store | Re-run Step 1 exactly |
| `make judge` scores 0 traces | Everything eligible is already scored (the judge is deterministic per trace) | Expected on a second run; `already_scored` tells you how many |
| Drift report: "synthetic" data | `--store` missing, so it compared a synthetic pair | Pass `--store .atlas/weeks.sqlite` |
| `deepeval` asks for a login or telemetry consent online | DeepEval first run | `export DEEPEVAL_TELEMETRY_OPT_OUT=YES`; no account is needed for `GEval` with your own model |
| Online judge cost higher than expected | No cap | `--limit 200` or `JUDGE_MAX_CALLS=200` |

---

## Solution notes

Reference page: `03-code/console/pages/4_Quality.py` (judge tiles, grounded and empty-retrieval rates, judge per hour, by prompt version, feedback by session length, thumbs-down per hour, the clickable disagreement table, top comments). Reference functions: `console/data.py`. Reference evals: `evals/online_judge.py`, `evals/feedback.py`, `evals/drift_report.py`, `evals/to_dataset.py`.

Reference numbers (two-week store from Step 1, offline):

| Item | Value |
|---|---|
| Judge run | 1,430 traces sampled and scored on top of 6,049 already scored; mean overall 0.842; est. cost $3.09 |
| Feedback | 2,598 events, 12.7% of 20,394 requests, 76% positive; judge on 👍 0.85, on 👎 0.81 |
| Agreement | 79% (`make feedback`), 67% (`judge_feedback_agreement`, resolved ≥ 0.7) |
| Drift W38 → W39 | three judge alerts; grounded 0.943 → 0.720 (PSI 2.0); cost −4.9%; latency improved |
| By prompt version | v1 grounded 0.941 (n 5,117); v2 0.586 (n 2,362) |

What separates a strong page from a weak one:

- The headline comes from the uniform slice; always-judged traces are for the worst-N table.
- Judge cost is on the page or in the notes as a first-class number.
- The page slices by `prompt_version`; drift alone says "something changed", the slice says *what*.
- Disagreements link to the Traces page and to a dataset. A quality page that can't produce a regression test is a dashboard, not a loop.
