# Incident 03 — Users are unhappy but nothing is red

**Raised:** Tuesday 2026-09-15, 09:10 UTC, by the HR business partner: "Atlas answers feel curt and people don't trust them any more." Nothing paged.

## What on-call sees

- Grafana: latency, error rate, cost — all **green**. Cost is actually down ~10%.
- `atlas_feedback_total{outcome="negative"}` doubled in the afternoon of Monday 2026-09-14.
- Langfuse scores: the sampled judge's `judge_grounded` mean dropped from ~0.9 to ~0.6 at about 11:00 Monday; `judge_resolved` is down too.
- The weekly drift report shows `judge_overall` PSI above 0.25.
- Nobody deployed code on Monday.

## Your job (8 minutes)

1. Load `spans.jsonl` and `scores.jsonl`; plot mean judge score per hour.
2. Segment the drop: by tenant, by intent, by model — and by anything else on the agent span.
3. Explain why cost went *down* while quality went down.
4. Name the fix and how you'd verify it before users notice.

Hints: `atlas.prompt_version` on agent and generation spans; compare `langfuse.observation.output` texts before and after 11:00 (what is missing?); `app/prompts.py`.
