# Incident 03 — Solution (revealed in lecture 11.4)

## Root cause

At 11:00 on Monday someone moved the `production` label of the Langfuse prompt `atlas-system` from **v1** to **v2** ("tidy-up: shorter answers"). No code was deployed, so no release marker appeared anywhere; Atlas fetches the production label through `get_prompt_text` with a 60-second cache (`cache_ttl_seconds=60`), so within a minute every tenant was on a prompt that had never been evaluated. v2 replaced *cite the knowledge-base article* and *end with a clear next step* with "Be brief. Prefer one or two sentences; avoid unnecessary references or repetition" and "Only mention tickets or sources when the employee explicitly asks for them". Answers got shorter, cheaper and faster — and stopped being grounded or actionable. The judge's `grounded` and `resolved` criteria caught it within the hour; the latency, error and cost dashboards never could, and the thumbs were too sparse to.

## Evidence in the spans and scores

| Where | What you see |
|---|---|
| `scores.jsonl`, `judge_grounded` by hour | 0.95, 0.92, 0.95 for 08:00–10:00, then **0.57 in the 11:00 bin** and 0.49–0.60 after; `judge_resolved` 0.90 → 0.65; `judge_overall` 0.92 → 0.71. A step, not a drift |
| judge scores by `atlas.prompt_version` | v1: grounded 0.938, resolved 0.887, overall 0.909 (n 141); v2: grounded 0.557, resolved 0.634, overall 0.698 (n 249). `judge_safe_escalation` 0.90 on both |
| agent spans, `atlas.prompt_version` | `v1` on all 288 requests before 11:00 (last at 10:59:53), `v2` on all 480 from 11:00:48 on — the only attribute that changes |
| `langfuse.observation.output` | `(Source: …)` in 96% of v1 answers and 0% of v2; "Next step:" in 98% of v1 and 0% of v2 |
| `gen_ai.usage.output_tokens` per generation | 115 before 11:00 → 42 after; input tokens flat at about 4,500 |
| cost and latency | cost per request $0.00206 → $0.00192 (−6.6%); p95 3.6 s → 1.9 s. Two metrics improved because the product got worse |
| sessions `s33-00030` (08:15, hr, v1) and `s33-00177` (13:47, ops, v2), "How many days of annual leave do I get?" | same article retrieved first (`top_k = 4`); v1 answers with the 28 days, the carry-over rule, a source line and a next step (grounded 0.90, resolved 0.88); v2 answers in one sentence with no source and no next step (grounded 0.41, resolved 0.58) |
| `user_feedback` | 87 thumbs for the day, 4–11 an hour, thumbs-down rate 0–50% per hour; the negative share is 29% before 11:00 and 20% after, so feedback shows no signal (the drift report even calls it +13%). The only comment is `unhelpful` |
| segment by tenant / intent / model | no difference — the drop is everywhere, which points at a shared component (the prompt). HR noticed first because policy questions are where "which policy says so" and "here's the form" are the whole value |

`python evals/drift_report.py --store .atlas/incident-03.sqlite --split-hour 11` raises three alerts: `judge_overall` PSI 4.3 (mean −23%), `judge_grounded` PSI 5.5 (−40%), `judge_resolved` PSI 6.9 (−29%); it marks `cost_per_request_usd` (−6.6%) and `latency_ms` (−40%) as *watch: distribution moved, mean improved* — the tell-tale pattern of a prompt that does less. `make incident N=3` shows the console's `judge_drift` ticket (PSI 2.003, mean −19.3%) and `slo_burn:quality` 4.49.

Why nothing paged: `AtlasJudgeScoreLow` in `deploy/alerts.yml` watches `atlas_judge_score`, a histogram the judge never writes to because it runs as a batch job over the store, so the rule can never fire.

## Fix

1. **Roll back the label, one command:** `python -m app.prompts promote --version 1` (wraps `telemetry.langfuse_setup.promote_prompt`, which calls `update_prompt(name=, version=, new_labels=["production"])`; labels are unique across versions, so v2 loses `production`). No deploy, no restart; Atlas picks it up within the 60-second cache. Offline, the same rollback is `ATLAS_PROMPT_VERSION=v1`. Fix now, improve later: do not edit v2 under pressure.
2. **Gate label changes:** promote the failing v2 traces to the `atlas-failures` dataset (`make dataset`, `evals/to_dataset.py`); prompt versions go to `staging` first and `promote` runs in CI only after the offline eval passes (refuse below 0.85 grounded). Take production label edits out of the UI where the Langfuse plan allows it (verify).
3. **Alert on quality, not only on infra:** make `AtlasJudgeScoreLow` able to fire by observing `metrics.JUDGE_SCORE` where the judge runs, or run `drift_report.py --split-hour` hourly; `judge_grounded` hourly mean < 0.75 for 2 hours → ticket. Feedback-rate alerts (`AtlasNegativeFeedbackSpike`) would not have caught this: too few thumbs.
4. Keep `atlas.prompt_version` (and the Langfuse prompt version) stamped on every generation so segmentation takes seconds.
