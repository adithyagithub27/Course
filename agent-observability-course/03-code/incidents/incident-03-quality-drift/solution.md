# Incident 03 — Solution (revealed in lecture 11.4)

## Root cause

At 11:00 someone moved the `production` label of the Langfuse prompt `atlas-system` from **v1** to **v2** ("tidy-up: shorter answers"). No code was deployed, so no release marker appeared anywhere. v2 dropped two instructions: *cite the knowledge-base article* and *end with a clear next step*, and told the model to "avoid unnecessary references". Answers got shorter and cheaper — and stopped being grounded or actionable. The judge's `grounded` and `resolved` criteria caught it within the hour; the latency and error dashboards never could.

## Evidence in the spans and scores

| Where | What you see |
|---|---|
| `scores.jsonl`, `judge_grounded` / `judge_overall` by hour | mean ~0.9 before 11:00, ~0.6–0.75 after |
| agent spans, `atlas.prompt_version` | `v1` before 11:00, `v2` after — the only attribute that changes |
| `langfuse.observation.output` after 11:00 | no `(Source: …)`, no "Next step:" |
| `gen_ai.usage.output_tokens` | lower after 11:00 → cost down |
| `user_feedback` scores | negative share rises in the afternoon, lagging the judge by 1–2 hours |
| segment by tenant / intent / model | no difference — the drop is everywhere, which points at a shared component (the prompt) |

`python evals/drift_report.py` on the dataset flags `judge_overall`, `judge_grounded` and `judge_resolved` as `alert` and `cost_per_request_usd` as an *improvement* — the tell-tale pattern of a prompt that does less.

## Fix

1. Roll back the label: in Langfuse move `production` back to v1 (or locally `ATLAS_PROMPT_VERSION=v1`). No deploy needed; the client's prompt cache refreshes within `cache_ttl_seconds`.
2. Gate label changes: prompt versions go to `staging` first and must pass the Course-2 style offline eval on the `atlas-failures` dataset (`evals/to_dataset.py`) before `production`.
3. Alert on quality, not only on infra: `judge_grounded` hourly mean < 0.75 for 2 hours → ticket; negative feedback rate > 2× baseline → ticket.
4. Stamp `atlas.prompt_version` (and the Langfuse prompt version) on every generation so segmentation takes seconds.
