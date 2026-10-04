# Incident 04 — Project 2: you are on call (no reveal)

**Alerted twice:** Monday 2026-09-14, 10:35 UTC, a ticket from `AtlasToolErrorRate` (`lookup_ticket` error rate above 5% for 10 minutes); then 15:20 UTC, a page from `AtlasLatencyP95High`. The Ops Console over the dataset shows `latency_p95` (p95 4,652 ms > 4,000 ms) and `slo_burn:tool_success` at 3.85. Two alerts in one day; the team lead wants one postmortem covering both.

**Dataset:** `incidents/incident-04-project/` — 300 sessions, seed 44, session ids `s44-…`; 741 requests, $1.66 for the day.

## What on-call sees

- `atlas_tool_calls_total{tool="lookup_ticket",outcome="error"}`: 10 errors between 10:00 and 12:00 (6 in the 10:00 hour, 4 in the 11:00 hour) and none in any other hour; the 10:00 hour's `lookup_ticket` error rate is above 50%. Every other tool is at zero all day. The errors are spread over tenants (`ops`, `finance`, `eng`), not one.
- The affected requests have more `step` spans than usual: `atlas.steps = 4` where a normal ticket lookup takes 2 (the limit is 6), and they cost about twice a normal lookup.
- Between 15:00 and 16:00, p95 latency is 8.5 s against ~3.6 s in every other hour, about 2.3x; cost per request is up a little ($0.0022 → $0.0023); tool errors are normal again; every tenant is affected.
- Nobody deployed anything.

## Your job

Produce a blameless postmortem (template: `10-resources/postmortem-template.md`) with:

1. Timeline of both alerts with evidence from `spans.jsonl` / `scores.jsonl` (span names, attributes, hours).
2. Blast radius: tenants, intents, number of sessions and users, cost impact.
3. Root cause for each alert and whether they are related.
4. Three action items that map to instrumentation, budgets or tests in this repo (name the file you would change).
5. One SLO/alert you would add or tune, with the exact threshold.

Submission: `05-projects/project-2-incident-postmortem.md`. There is no solution video for this incident; instructors grade against the hidden `solution.md`.
