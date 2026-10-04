# Incident 03 — Users are unhappy but nothing is red

**Raised:** Tuesday 2026-09-15, 09:10 UTC, by the HR business partner: "Since late morning yesterday Atlas feels curt. Answers are a line or two, no source, and it doesn't tell people what to do next. People don't trust it any more." Nothing paged.

**Dataset:** `incidents/incident-03-quality-drift/` — 300 sessions, seed 33, session ids `s33-…`; 768 requests, $1.52 for the day. Unlike incidents 1 and 2, use `scores.jsonl` as well: it has the sampled judge scores (`judge_grounded`, `judge_resolved`, `judge_overall`, `judge_safe_escalation`) and the thumbs (`user_feedback`).

## What on-call sees

- Grafana: latency, error rate, cost — all **green**. Two of them look *better*: cost per request is down about 7% since late Monday morning and p95 latency fell from ~3.5 s to ~2.0 s.
- `atlas_feedback_total`: too sparse to read. Four to eleven thumbs an hour; the thumbs-down rate bounces between 0% and 50% from hour to hour, before and after lunch. The one comment that recurs is `unhelpful`.
- Ops Console, Quality page: the sampled judge's `judge_grounded` hourly mean runs 0.92–0.95 all morning, then **0.57 in the 11:00 bin** on Monday 2026-09-14 and 0.51–0.60 for the rest of the day; `judge_resolved` goes 0.90 → 0.65 in the same hour. `judge_safe_escalation` does not move.
- The console's batch rules did raise tickets that nobody read: `judge_drift` (`judge_overall` PSI 2.0, mean moved −19.3%) and `slo_burn:quality` at 4.49. `deploy/alerts.yml` has `AtlasJudgeScoreLow`, but it did not fire.
- Nobody deployed code on Monday. The Langfuse prompt `atlas-system` has two versions.

## Your job (8 minutes)

1. Load `spans.jsonl` and `scores.jsonl`; plot mean judge score per hour and find the hour the lines bend.
2. Segment the drop: by tenant, by intent, by model — and by anything else on the agent span.
3. Explain why cost and latency went *down* while quality went down, and why the thumbs did not catch it.
4. Name the fix (one command) and how you'd verify it before users notice.

Hints: `atlas.prompt_version` on agent and generation spans; compare `langfuse.observation.output` texts before and after 11:00 (what is missing?), for example the same leave question in sessions `s33-00030` (08:15) and `s33-00177` (13:47); `gen_ai.usage.output_tokens` per generation by hour; `app/prompts.py`.

Do not open `solution.md` until you have written your hypothesis down.
