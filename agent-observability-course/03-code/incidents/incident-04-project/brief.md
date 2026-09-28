# Incident 04 — Project 2: you are on call (no reveal)

**Paged:** Monday 2026-09-14, 10:35 UTC by `tool_error_rate`; again at 15:20 UTC by `latency_p95`. Two pages in one day; the team lead wants one postmortem covering both.

## What on-call sees

- `atlas_tool_calls_total{tool="lookup_ticket",outcome="error"}` spikes between 10:00 and 12:00; every tenant that looks up tickets is affected.
- Several sessions in that window have many `step` spans and `atlas.steps` at or near the limit.
- Between 15:00 and 16:00, p95 latency is roughly double the morning; cost per request is up a little; tool errors are normal again.
- Nobody deployed anything.

## Your job

Produce a blameless postmortem (template: `10-resources/postmortem-template.md`) with:

1. Timeline of both pages with evidence from `spans.jsonl` / `scores.jsonl` (span names, attributes, hours).
2. Blast radius: tenants, intents, number of sessions and users, cost impact.
3. Root cause for each page and whether they are related.
4. Three action items that map to instrumentation, budgets or tests in this repo (name the file you would change).
5. One SLO/alert you would add or tune, with the exact threshold.

Submission: `05-projects/project-2-incident-postmortem.md`. There is no solution video for this incident; instructors grade against the hidden `solution.md`.
