# Production Voice AI Agents with Python: Build, Test, Deploy

Course 3 in the Build → Test → Operate series. Complete production package for a Udemy course on building, testing and deploying real-time voice AI agents with LiveKit Agents, OpenAI Realtime and Pipecat.

**Running example:** Riley, the AI receptionist for the fictional Maple Street Dental. Riley answers questions, books, reschedules and cancels appointments, transfers to a human, and runs on a real phone number.

## Why this course (summary of the market research)

- A no-code voice-agent course on Udemy has 37,833 students at 4.8 stars, proving demand.
- Only three code-first production voice courses exist, none is a bestseller, and none teaches how to **test and evaluate** voice agents.
- LiveKit Agents 1.x and OpenAI Realtime (with SIP) matured in the last 12 months, so "production" framing is fresh.
- Full reasoning: `../00-course-strategy/next-course-market-research.md`.

## Specs

| Field | Value |
|---|---|
| Runtime | ≈10.5 h video, 15 sections, 78 lectures |
| Level | Intermediate Python (beginner-safe first three sections) |
| Stack | Python 3.11+, livekit-agents 1.8, pipecat-ai 1.12, OpenAI, Deepgram, Cartesia, Twilio SIP, DeepEval, jiwer, OpenTelemetry, Langfuse, Docker, GitHub Actions |
| Student cost | ≈$10-20 in API usage using free tiers |
| Deliverables | 1 GitHub repo, 7 labs, 3 projects + capstone, 6 quizzes, 1 practice test, 5 coding exercises |

## Folder map

| Folder | Contents |
|---|---|
| `01-curriculum/` | **Source of truth**: sections, lectures, durations, objectives, file map, verified API reference |
| `02-lecture-scripts/` | Narration-ready scripts for every lecture, with on-screen cues |
| `03-code/` | Student code repository (agents, pure-Python business logic, tests, evals, deploy, CI) |
| `04-labs/` | Guided labs |
| `05-projects/` | Project briefs, rubrics and the capstone |
| `06-assessments/` | Section quizzes, 40-question practice test, assignments, Udemy coding exercises |
| `07-udemy-listing/` | Everything the Udemy course landing page and course settings require |
| `08-marketing/` | Launch plan, SEO keywords, YouTube and LinkedIn content, cross-sell plan |
| `09-production/` | Recording guide, slide outline, production schedule, budget, QA checklist |
| `10-resources/` | Downloadable cheat sheets, worksheets, checklists and decision matrices |

## Status

| Workstream | Status |
|---|---|
| Curriculum | Done |
| Lecture scripts | See `02-lecture-scripts/` |
| Code repo | See `03-code/README.md` (unit tests run offline) |
| Labs, projects, assessments | See folders |
| Udemy listing | See `07-udemy-listing/` |
| Recording | Not started |

## Version note

All code and scripts were written against `livekit-agents` 1.8.3 and `pipecat-ai` 1.12.0 as installed on 2026-09-28. Voice frameworks move fast. Re-run `make test` and the agent smoke tests before recording, and pin versions in `03-code/pyproject.toml`.
