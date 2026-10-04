# AI Agent Observability & Cost Control: LLMOps in Production

Course 4 in the Build → Test → Deploy → Operate series. Complete production package for a Udemy course on tracing, cost engineering, reliability, online evaluation and incident response for LLM agents, built on OpenTelemetry, Langfuse, LiteLLM, Prometheus and Grafana.

**Running example:** Atlas, the internal IT and HR helpdesk agent at the fictional Northwind Logistics, plus a deterministic traffic simulator that replays a full day of multi-tenant load with injectable incidents. Every lab works offline.

## Why this course (from the market research)

- Completes the four-course path; cross-sells to every existing student base.
- Only three small Langfuse courses exist on Udemy; none combines the OpenTelemetry GenAI conventions, agent-specific tracing, token FinOps, online evaluation and incident response.
- "Cost per resolved session" is the number engineering managers are asked for in 2026 and almost nobody teaches how to produce it.
- Full reasoning: `../00-course-strategy/next-course-market-research.md`.

## Specs

| Field | Value |
|---|---|
| Runtime | ≈10.5 h video (627 min), 15 sections, 91 video items (76 lectures, 7 labs, 5 challenges, 3 assignments) + 13 quizzes + a practice test |
| Level | Intermediate Python (beginner-safe first three sections) |
| Stack | langfuse 4, opentelemetry-sdk 1.45, GenAI semconv 0.66, openinference, litellm, langsmith, deepeval, prometheus-client, fastapi, Docker Compose (Langfuse, OTel Collector, Prometheus, Grafana) |
| Student cost | ≈$5-15 in API usage; everything runs offline via the mock LLM |
| Deliverables | 1 GitHub repo (419 offline tests), 7 labs, 2 projects + capstone + domain swap, 5 challenges, 13 quizzes, 1 practice test, 5 coding exercises, 4 incident datasets (3 with reveals, 1 for Project 2) |

## Folder map

| Folder | Contents |
|---|---|
| `01-curriculum/` | Source of truth: sections, lectures, durations, file map, verified API reference; `numbers-card.md` holds every number the scripts may quote |
| `02-lecture-scripts/` | Narration-ready scripts with production cues |
| `03-code/` | Student repository: Atlas agent, telemetry, simulator, evals, console, incidents, deploy, tests, CI |
| `04-labs/` | Guided labs |
| `05-projects/` | Projects, challenges, capstone |
| `06-assessments/` | Quizzes, practice test, assignments, coding exercises |
| `07-udemy-listing/` | Landing page and course settings package |
| `08-marketing/` | Launch, SEO, content, cross-sell |
| `09-production/` | Recording guide, slide-deck outline, video plan, schedule, budget, QA; reuses the HeyGen and slide tools from Course 3 (`voice-ai-agents-course/09-production/tools/`) |
| `10-graphics/` | D1-D12 diagram masters (`diagrams/`) and the generated per-section slide decks (`slides/`); regenerate with `python voice-ai-agents-course/09-production/tools/slide_builder.py --course agent-observability-course` |
| `10-resources/` | Student downloads: worksheets, checklists, templates, decision matrices |

## Version note

Written against the package versions listed in `01-curriculum/curriculum.md` as installed on 2026-09-28. Re-run `make test` (419 passed) and `make budget-check` (5 passed) before recording and pin versions in `03-code/pyproject.toml`. The offline fixture day is `OFFLINE=1 make replay` with the Makefile defaults: seed 7, Monday 2026-09-14, tenants `ops`, `finance`, `hr`, `eng`, $56.28.
