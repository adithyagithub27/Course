# AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python

> A comprehensive Udemy course teaching engineers how to systematically test, evaluate, and monitor AI agents and LLM-powered applications using industry-standard tools and production-grade patterns.

---

## Course Overview

AI agents are entering production, but most teams ship without any testing or evaluation strategy. This course changes that. Students learn how to build end-to-end quality frameworks for AI agents — from unit-testing individual LLM calls to evaluating multi-step agent workflows, detecting regressions, and monitoring production systems with observability tooling.

Every concept is taught through hands-on labs and real-world projects. By the end, students have a complete, reusable testing and evaluation framework they can apply to any AI agent system.

---

## Course Specs

| Attribute              | Detail                                              |
|------------------------|-----------------------------------------------------|
| **Target Runtime**     | 8.5 – 9.5 hours                                    |
| **Total Lectures**     | ~60 lectures                                        |
| **Modules**            | 16 (M00 – M15)                                     |
| **Hands-On Projects**  | 5 projects + 1 capstone                             |
| **Skill Level**        | Beginner-friendly with enterprise depth              |
| **Audience Weight**    | 55% beginner / 45% enterprise                       |
| **Prerequisites**      | Basic Python knowledge; no ML/AI experience required |
| **Primary LLM**        | OpenAI GPT-4o-mini (~$5–10 total API cost)          |
| **Platform**           | Udemy                                               |
| **Standalone**         | Yes — no dependency on any prior course              |

---

## Technology Stack

### Core Languages & Frameworks

| Technology        | Role                                                    |
|-------------------|---------------------------------------------------------|
| **Python 3.11+**  | Primary language for all code, labs, and projects       |
| **pytest**        | Test runner and assertion framework                     |
| **Pydantic**      | Data validation and schema enforcement                  |

### AI & LLM

| Technology              | Role                                           |
|-------------------------|-------------------------------------------------|
| **OpenAI GPT-4o-mini**  | Primary LLM for all agent interactions          |
| **LangChain**           | Agent orchestration (where applicable)          |

### Testing & Evaluation Frameworks

| Technology    | Role                                                        |
|---------------|-------------------------------------------------------------|
| **DeepEval**  | LLM evaluation metrics (faithfulness, relevance, hallucination) |
| **RAGAS**     | RAG-specific evaluation (context precision, recall, noise)  |
| **promptfoo** | Prompt regression testing and red-teaming                   |

### Observability & Monitoring

| Technology          | Role                                              |
|---------------------|---------------------------------------------------|
| **Langfuse**        | LLM observability, tracing, and cost tracking     |
| **OpenTelemetry**   | Distributed tracing and telemetry standards        |

### CI/CD & Infrastructure

| Technology          | Role                                              |
|---------------------|---------------------------------------------------|
| **GitHub Actions**  | Automated test pipelines and CI/CD                |
| **Docker**          | Reproducible environments for labs and projects   |

### UI & Visualization

| Technology      | Role                                                |
|-----------------|-----------------------------------------------------|
| **Streamlit**   | Interactive dashboards for evaluation results       |

---

## Folder Structure

This repository is organized into 16 sequenced folders that mirror the production pipeline:

```
AI-Agent-Testing-Evaluation/
│
├── 00-course-strategy/        # Market research, differentiation, audience personas
├── 01-curriculum/             # Module outlines, lecture objectives, pacing plans
├── 02-course-content/         # Lecture scripts (one per lecture, final narration-ready)
├── 03-demos/                  # Live demo scripts and screen recording plans
├── 04-code-examples/          # Standalone code snippets shown during lectures
├── 05-datasets/               # Sample data for labs and projects
├── 06-evaluation-frameworks/  # Reusable evaluation configs, metric definitions
├── 07-labs/                   # Guided lab exercises (step-by-step)
├── 08-projects/               # End-to-end projects (5 projects + capstone)
├── 09-heygen/                 # HeyGen avatar configs, video generation assets
├── 10-graphics/               # Slides, diagrams, visual design system
├── 11-course-assets/          # Downloadable resources, cheat sheets, templates
├── 12-udemy/                  # Udemy metadata: title, description, tags, pricing
├── 13-marketing/              # Launch strategy, SEO, social media, coupons
├── 14-quality-review/         # QA checklists, review feedback, iteration logs
├── 15-release/                # Final exports, release notes, post-launch tracking
│
├── README.md                  # This file
├── COURSE_STATUS.md           # Module-by-module production status tracker
├── COURSE_DECISIONS.md        # Decision log with rationale
├── PRODUCTION_CHECKLIST.md    # Phase-by-phase production checklist
├── MY_DECISIONS_REQUIRED.md   # Items requiring course owner input
└── CHANGELOG.md               # Version history of project changes
```

---

## How to Navigate This Project

### If you're starting fresh:
1. Read `00-course-strategy/` for market context and differentiation
2. Review `01-curriculum/` for the full module and lecture breakdown
3. Check `COURSE_STATUS.md` to see what's been completed

### If you're building content:
1. Write scripts in `02-course-content/` (one file per lecture)
2. Build corresponding code in `04-code-examples/` and `07-labs/`
3. Update `COURSE_STATUS.md` after completing each deliverable

### If you're in production:
1. Follow `PRODUCTION_CHECKLIST.md` phase by phase
2. Track HeyGen video generation in `09-heygen/`
3. Run QA passes using checklists in `14-quality-review/`

### If you're preparing to launch:
1. Finalize Udemy metadata in `12-udemy/`
2. Execute marketing plan from `13-marketing/`
3. Stage final assets in `15-release/`

---

## Quick Links

| Document                                            | Purpose                                  |
|-----------------------------------------------------|------------------------------------------|
| [COURSE_STATUS.md](COURSE_STATUS.md)                | Track progress across all modules        |
| [COURSE_DECISIONS.md](COURSE_DECISIONS.md)          | Review architectural and strategic decisions |
| [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)  | Phase-by-phase production checklist      |
| [MY_DECISIONS_REQUIRED.md](MY_DECISIONS_REQUIRED.md)| Items needing course owner approval      |
| [CHANGELOG.md](CHANGELOG.md)                        | Project version history                  |

---

## Production Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTENT CREATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Script Writing ──► HeyGen Avatar Video ──► Screen Recordings     │
│        │                    │                       │               │
│        │                    ▼                       │               │
│        │              OBS Studio                    │               │
│        │            (capture/edit)                   │               │
│        │                    │                       │               │
│        ▼                    ▼                       ▼               │
│   ┌─────────────────────────────────────────────┐                  │
│   │              CapCut Assembly                 │                  │
│   │   (avatar + screen + graphics + captions)    │                  │
│   └──────────────────────┬──────────────────────┘                  │
│                          │                                          │
│                          ▼                                          │
│                   Final QA Review                                   │
│                          │                                          │
│                          ▼                                          │
│                  Udemy Upload & Publish                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Tools in the Pipeline

| Stage              | Tool         | Purpose                                       |
|--------------------|--------------|------------------------------------------------|
| Avatar Video       | **HeyGen**   | AI avatar narration from lecture scripts       |
| Screen Capture     | **OBS Studio** | Record live coding demos and terminal sessions |
| Video Assembly     | **CapCut**   | Combine avatar, screen recordings, graphics    |
| Quality Review     | Manual + Checklists | Technical, educational, and visual QA  |
| Publishing         | **Udemy**    | Final upload, metadata, and course launch      |

---

## License

This repository contains proprietary course production materials. All content, scripts, code examples, and course assets are copyrighted. The public-facing framework components (evaluation utilities, testing patterns) are shared under MIT License where explicitly noted. Course-exclusive content is not licensed for redistribution.

---

*Built with care for engineers who believe AI agents deserve the same testing rigor as any production software.*
