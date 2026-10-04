# AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python

> Production package for **Course 2** of this repository: a hands-on Udemy course on testing, evaluating and monitoring AI agents across the whole quality lifecycle — evaluation metrics, RAG and tool-calling tests, red teaming, tracing, cost, regression, CI/CD quality gates and production monitoring.
>
> This repository also holds **Course 3** (`voice-ai-agents-course/`, Production Voice AI Agents) and **Course 4** (`agent-observability-course/`, AI Agent Observability & Cost Control). Start with `CLAUDE.md` for the repo-wide guide.

---

## Course Overview

Students work on one realistic running example — the **TechCorp customer support agent** (OpenAI tool calling, five tools) — plus a RAG policy assistant, a six-tool operations agent, a banking agent they red team, and a three-agent reply desk. Every concept is backed by code in the student repo `04-code-examples/agent-eval-framework/`, and every lab, demo and test runs **offline** (deterministic mock LLM and mock judge) without an API key.

---

## Course Specs

| Attribute | Detail |
|---|---|
| **Runtime** | 400 minutes of lectures = **6 h 40 min** |
| **Lectures** | **55** (16 modules, M00–M15; includes Lecture 8.5 "Beyond promptfoo: Garak and PyRIT") |
| **Projects** | 5 (Project 5 is the capstone) |
| **Labs** | 12 lab guides + Thought Exercise 2.1 |
| **Quizzes** | 14 |
| **Skill level** | Beginner-friendly with enterprise depth |
| **Prerequisites** | Basic Python; no ML/AI experience required |
| **Models** | `gpt-4.1-mini` (agent), `gpt-4.1` (judge) — optional; offline mode needs no key (live runs: a few dollars in total, verify current pricing) |
| **Platform** | Udemy |
| **Standalone** | Yes — no dependency on any other course |

Source of truth for lecture IDs, titles and durations: `01-curriculum/full-curriculum.md`.

---

## Technology Stack (verified in `uv.lock`, 2026-10-01)

| Area | Technology | Version |
|---|---|---|
| Language and tooling | Python, uv, pytest | 3.11+, current, 9.1.1 |
| LLM SDK | OpenAI Python SDK | 2.54.0 (2.x line) |
| Evaluation | DeepEval (metrics, G-Eval, Synthesizer) | 4.2.7 |
| RAG evaluation | RAGAS | 0.4.3 |
| Tool contracts | MCP Python SDK | 2.2.0 |
| Red teaming | promptfoo (via `npx`, Node 20+); Garak; PyRIT | 0.123.1; 0.17.0; 1.1.0 |
| Observability | Langfuse (v4 SDK); OpenTelemetry SDK + GenAI semantic conventions | 4.16.0; 1.45.0 / 0.66b0 |
| Dashboard | Streamlit | 1.64.0 |
| CI/CD | GitHub Actions (`.github/workflows/agent-eval.yml` in the student repo) | — |

LangChain is not used by the course code (it arrives only as a transitive dependency of RAGAS).

---

## Folder Structure

```
Course/
│
├── 00-course-strategy/        # Differentiation and positioning; market research for all courses
├── 01-curriculum/             # full-curriculum.md — the source of truth (55 lectures, 16 modules)
├── 02-course-content/         # Lecture scripts, one file per module: section-00-welcome.md … section-15-career.md
├── 03-demos/                  # Screencast specs (README.md index + demo-scripts/demo-NN-*.md) with real output
├── 04-code-examples/          # Student repo: agent-eval-framework/ (make install, make test, make demos)
├── 05-datasets/               # Five enterprise scenario datasets
├── 06-evaluation-frameworks/  # Metric definitions and evaluation reference
├── 07-labs/                   # 12 lab guides (Lab 1.1 … Lab 13.1)
├── 08-projects/               # Projects 1–5 (Project 5 = capstone, with ARCHITECTURE.md)
├── 09-heygen/                 # PRODUCTION-GUIDE.md, SCRIPT-TEMPLATE.md, avatar/voice config
├── 10-graphics/               # design-system.md (shared), slide-deck-outline.md, diagrams/ D1–D16
├── 11-course-assets/          # Cheat sheets and templates (test strategy, scorecard, 30-day plan)
├── 12-udemy/                  # Udemy listing copy
├── 13-marketing/              # Positioning, titles, SEO, launch, social, video
├── 14-quality-review/         # Review reports, fix plan, course2-bible.md (code facts for writers)
│                              # (15-release/ is planned for final exports; not created yet)
├── voice-ai-agents-course/    # Course 3 (and the shared production tools in 09-production/tools/)
├── agent-observability-course/# Course 4
│
├── CLAUDE.md                  # Repo-wide guide for contributors and agents
├── README.md                  # This file
├── COURSE_STATUS.md           # Module-by-module status (Course 2)
├── COURSE_DECISIONS.md        # Decision log
├── PRODUCTION_CHECKLIST.md    # Phase-by-phase checklist
├── MY_DECISIONS_REQUIRED.md   # Open decisions for the course owner
├── BUILD_LOG.md               # One line per exported lecture (all courses)
└── CHANGELOG.md               # Version history
```

---

## How to Navigate This Project

**Starting fresh:** read `01-curriculum/full-curriculum.md`, then `COURSE_STATUS.md`, then run the student repo:

```bash
cd 04-code-examples/agent-eval-framework
make install        # uv sync --locked
make test           # 204 passed, 5 skipped (live) — offline, no key
make demos          # all 61 lecture demos, offline
```

**Writing or fixing scripts:** scripts are in `02-course-content/section-XX-slug.md` in the format of `09-heygen/SCRIPT-TEMPLATE.md`. Code facts (files, commands, outputs, versions) come from `14-quality-review/course2-bible.md`; if a script and the code disagree, the code wins.

**In production:** follow `09-heygen/PRODUCTION-GUIDE.md` and `PRODUCTION_CHECKLIST.md` one module at a time; record screencasts from `03-demos/`; build decks with `python voice-ai-agents-course/09-production/tools/slide_builder.py --course . --scripts-dir 02-course-content`; log each exported lecture in `BUILD_LOG.md`.

**Preparing to launch:** `12-udemy/course-description.md`, then `13-marketing/`. Open owner decisions: `MY_DECISIONS_REQUIRED.md`.

---

## Production Pipeline

```
02-course-content scripts ──► scene_extractor.py ──► heygen_batch.py ──► avatar clips (HeyGen)
          │                                                                      │
          ├──► slide_builder.py ──► slides/section-XX.pptx (+ diagrams D1–D16)   │
          │                                                                      ▼
          └──► 03-demos specs ──► OBS screencasts ──────────────────► CapCut / DaVinci assembly
                                                                                 │
                                                                     QA ──► Udemy ──► BUILD_LOG.md
```

| Stage | Tool |
|---|---|
| Avatar narration | HeyGen (`[AVATAR]` blocks only) |
| Screen capture | OBS Studio |
| Slides and diagrams | `slide_builder.py`, `10-graphics/diagrams/_src/build_diagrams.py` |
| Assembly | CapCut or DaVinci Resolve |
| Publishing | Udemy |

---

## License

Proprietary course production materials. The student repo `04-code-examples/agent-eval-framework/` is MIT-licensed (see its README); other content is not licensed for redistribution.
