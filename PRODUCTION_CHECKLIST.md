# Production Checklist

> **Purpose:** A phase-by-phase checklist covering every deliverable from initial discovery through course launch. Check items off as they are completed. Do not skip phases.
>
> **Last Updated:** 2026-09-24

---

## How to Use This Checklist

1. Work through phases sequentially — each phase builds on the previous
2. Check off items (`[x]`) as they are completed
3. Add dates next to completed items for tracking
4. If a phase is blocked, note the blocker inline
5. Cross-reference with `COURSE_STATUS.md` for module-level detail

---

## Phase 1: Discovery (Weeks 1–2)

> **Goal:** Understand the market, validate the course concept, and define what makes this course unique.

### Competitor Analysis
- [ ] Identify top 10 competing courses on Udemy (AI testing, LLM evaluation)
- [ ] Analyze competitor curricula (topics covered, gaps, runtime, ratings)
- [ ] Document competitor pricing and enrollment numbers
- [ ] Identify content gaps and underserved topics
- [ ] Write competitor analysis summary document

### Tool Evaluation
- [ ] Evaluate DeepEval (features, API stability, documentation quality)
- [ ] Evaluate RAGAS (features, RAG-specific metrics, compatibility)
- [ ] Evaluate promptfoo (prompt testing, regression, red-teaming)
- [ ] Evaluate Langfuse (observability, tracing, self-hosted vs cloud)
- [ ] Evaluate OpenTelemetry (LLM instrumentation, integration points)
- [ ] Confirm all tools work together in a single Python environment
- [ ] Document tool versions to pin for the course
- [ ] Estimate total API cost for a student completing all labs

### Persona Definition
- [ ] Define primary persona (beginner Python developer entering AI)
- [ ] Define secondary persona (mid-level engineer adding AI testing to existing systems)
- [ ] Define tertiary persona (enterprise/staff engineer building quality frameworks)
- [ ] Document persona pain points, goals, and learning preferences

### Differentiation
- [ ] Write course differentiation document (why this course vs. competitors)
- [ ] Define the unique value proposition (1-sentence pitch)
- [ ] Validate positioning with 2–3 trusted reviewers

---

## Phase 2: Content Architecture (Weeks 3–5)

> **Goal:** Design the complete curriculum, define every lecture, and establish the visual system.

### Curriculum Design
- [ ] Define all 16 modules with titles and descriptions
- [ ] Break each module into individual lectures (~60 total)
- [ ] Write learning objectives for every lecture
- [ ] Define prerequisites and knowledge flow between modules
- [ ] Map lecture types (concept, demo, lab, project, recap)
- [ ] Validate pacing (target 8.5–9.5 hours total runtime)
- [ ] Assign estimated runtime per lecture

### Lab & Project Specifications
- [ ] Design 5 hands-on projects with clear deliverables
- [ ] Design capstone project (end-to-end evaluation framework)
- [ ] Write lab specifications for each guided exercise
- [ ] Define starter code vs. solution code for each lab
- [ ] Define datasets required for each lab/project
- [ ] Validate that labs build progressively in complexity

### Evaluation Metric Framework
- [ ] Define the taxonomy of evaluation metrics covered in the course
- [ ] Map which metrics are taught in which modules
- [ ] Create a metrics reference sheet (student downloadable)
- [ ] Validate metric coverage against industry best practices

### Visual Design System
- [ ] Define color palette, typography, and slide templates
- [ ] Design slide master templates (title, content, code, diagram)
- [ ] Design diagram style guide (architecture diagrams, flow charts)
- [ ] Design code snippet visual style (font, theme, highlighting)
- [ ] Create course thumbnail concept (3 options minimum)
- [ ] Get course owner approval on visual design system

---

## Phase 3: Scripts & Code (Weeks 5–8)

> **Goal:** Write every lecture script and build every code example, lab, and project.

### Lecture Scripts
- [ ] Write scripts for Module 01 (Introduction & Course Setup)
- [ ] Write scripts for Module 02 (Why AI Agents Need Testing)
- [ ] Write scripts for Module 03 (Testing Fundamentals for AI)
- [ ] Write scripts for Module 04 (LLM Output Evaluation Basics)
- [ ] Write scripts for Module 05 (DeepEval Framework Deep Dive)
- [ ] Write scripts for Module 06 (RAG Evaluation with RAGAS)
- [ ] Write scripts for Module 07 (Prompt Regression Testing)
- [ ] Write scripts for Module 08 (Agent Workflow Testing)
- [ ] Write scripts for Module 09 (Observability & Monitoring)
- [ ] Write scripts for Module 10 (CI/CD for AI Agents)
- [ ] Write scripts for Module 11 (Red-Teaming & Safety Testing)
- [ ] Write scripts for Module 12 (Production Monitoring Dashboards)
- [ ] Write scripts for Module 13 (Capstone Project)
- [ ] Write scripts for Module 14 (Advanced Topics & What's Next)
- [ ] Review all scripts for consistency, tone, and pacing
- [ ] Proofread all scripts (grammar, clarity, accuracy)

### Code Development
- [ ] Build all code examples for each module
- [ ] Build all lab starter templates
- [ ] Build all lab solution code
- [ ] Build all 5 project codebases
- [ ] Build capstone project codebase
- [ ] Write requirements.txt / pyproject.toml with pinned versions
- [ ] Write setup instructions (README per project)
- [ ] Test all code on clean Python 3.11+ environment
- [ ] Test all code on Windows, macOS, and Linux (or document platform notes)

### Datasets
- [ ] Create or source datasets for each lab
- [ ] Create or source datasets for each project
- [ ] Validate dataset quality and appropriateness
- [ ] Document dataset licenses and attribution

### Lab Validation
- [ ] Complete every lab end-to-end as a student would
- [ ] Time each lab (target completion times)
- [ ] Identify and resolve any ambiguities in lab instructions
- [ ] Verify all expected outputs match documentation

---

## Phase 4: Prototype (Weeks 8–9)

> **Goal:** Produce 3–4 representative lectures to validate the full production pipeline before committing to all 60.

### Prototype Lectures
- [ ] Select 3–4 representative lectures (1 concept, 1 demo, 1 lab walkthrough)
- [ ] Generate HeyGen avatar video for each prototype lecture
- [ ] Record screen captures for demo/lab lectures
- [ ] Create graphics and slides for prototype lectures
- [ ] Assemble prototype lectures in CapCut (avatar + screen + graphics)
- [ ] Add captions/subtitles to prototype lectures
- [ ] Export prototype lectures at final quality settings

### Prototype Review
- [ ] Course owner reviews all prototype lectures
- [ ] Document feedback on avatar quality, pacing, visuals
- [ ] Identify adjustments needed before full production
- [ ] Get explicit go/no-go approval for full production
- [ ] Incorporate feedback and re-export if needed

---

## Phase 5: Full Production (Weeks 9–11)

> **Goal:** Produce all ~60 lectures using the validated pipeline.

### HeyGen Avatar Videos
- [ ] Generate avatar videos for all Module 01 lectures
- [ ] Generate avatar videos for all Module 02 lectures
- [ ] Generate avatar videos for all Module 03 lectures
- [ ] Generate avatar videos for all Module 04 lectures
- [ ] Generate avatar videos for all Module 05 lectures
- [ ] Generate avatar videos for all Module 06 lectures
- [ ] Generate avatar videos for all Module 07 lectures
- [ ] Generate avatar videos for all Module 08 lectures
- [ ] Generate avatar videos for all Module 09 lectures
- [ ] Generate avatar videos for all Module 10 lectures
- [ ] Generate avatar videos for all Module 11 lectures
- [ ] Generate avatar videos for all Module 12 lectures
- [ ] Generate avatar videos for all Module 13 lectures
- [ ] Generate avatar videos for all Module 14 lectures
- [ ] QA check all avatar videos (lip sync, audio quality, no artifacts)

### Screen Recordings
- [ ] Record all live coding demos
- [ ] Record all terminal/CLI demonstrations
- [ ] Record all dashboard/UI walkthroughs
- [ ] Verify screen recordings are clear at 1080p
- [ ] Add zoom/highlight annotations where needed

### Graphics & Slides
- [ ] Create all slide decks for concept lectures
- [ ] Create all architecture diagrams
- [ ] Create all flow charts and process diagrams
- [ ] Create all evaluation metric visualizations
- [ ] Ensure all graphics follow the visual design system

### Video Assembly
- [ ] Assemble all lectures in CapCut (avatar + screen + graphics)
- [ ] Add captions/subtitles to all lectures
- [ ] Add intro/outro bumpers to each lecture
- [ ] Normalize audio levels across all lectures
- [ ] Export all lectures at final quality (1080p, high bitrate)

---

## Phase 6: Quality Assurance (Week 11)

> **Goal:** Systematic review of every lecture and asset before upload.

### Technical QA
- [ ] Verify all code shown in videos matches the repository code
- [ ] Verify all terminal outputs shown are accurate and reproducible
- [ ] Verify all API calls use correct endpoints and models
- [ ] Check for any hardcoded API keys or secrets in videos
- [ ] Confirm all package versions mentioned are correct
- [ ] Test all GitHub repository links

### Educational QA
- [ ] Verify each lecture delivers on its stated learning objectives
- [ ] Check for logical flow between consecutive lectures
- [ ] Verify no prerequisite knowledge is assumed without being taught
- [ ] Confirm all jargon and acronyms are defined on first use
- [ ] Check that difficulty progression is smooth (no sudden jumps)
- [ ] Verify recap lectures accurately summarize their modules

### Visual QA
- [ ] Check all text is readable at 720p (minimum Udemy resolution)
- [ ] Verify code font size is legible in all screen recordings
- [ ] Check for visual consistency across all lectures
- [ ] Verify captions are accurate and properly timed
- [ ] Check thumbnail at multiple sizes (search result, course page, mobile)

### Enterprise QA
- [ ] Verify enterprise patterns are realistic (not toy examples)
- [ ] Check that CI/CD examples follow industry best practices
- [ ] Verify observability setup matches production conventions
- [ ] Confirm security best practices are followed (secrets management, etc.)

---

## Phase 7: Launch (Week 12+)

> **Goal:** Upload to Udemy, configure the course, and execute the launch plan.

### Udemy Upload
- [ ] Upload all lecture videos to Udemy
- [ ] Organize lectures into sections matching the 16-module structure
- [ ] Set lecture order and mark preview-eligible lectures
- [ ] Upload course thumbnail
- [ ] Upload promotional video / trailer

### Course Configuration
- [ ] Write final course title
- [ ] Write course subtitle
- [ ] Write course description (long-form, SEO-optimized)
- [ ] Add all relevant tags and categories
- [ ] Configure target student description
- [ ] Configure prerequisites list
- [ ] Configure "What you'll learn" bullet points (max impact)

### Supplementary Content
- [ ] Create and attach quizzes for key modules
- [ ] Create and attach practice tests (if applicable)
- [ ] Upload downloadable resources (cheat sheets, templates, configs)
- [ ] Add external resource links (GitHub repo, documentation)
- [ ] Write welcome message (auto-sent to new students)
- [ ] Write completion message

### Marketing & Launch
- [ ] Finalize coupon strategy (launch discount, affiliate codes)
- [ ] Prepare social media announcement posts
- [ ] Prepare email announcement (if applicable)
- [ ] Schedule launch date
- [ ] Execute launch communications
- [ ] Monitor first 48 hours for issues

### Post-Launch
- [ ] Monitor Q&A section daily for first 2 weeks
- [ ] Track enrollment numbers and conversion rates
- [ ] Collect and respond to initial reviews
- [ ] Document any content fixes needed based on student feedback
- [ ] Plan first content update (if needed)

---

## Completion Summary

| Phase                  | Total Items | Completed | Remaining |
|------------------------|-------------|-----------|-----------|
| Phase 1: Discovery     | 22          | 0         | 22        |
| Phase 2: Architecture  | 25          | 0         | 25        |
| Phase 3: Scripts & Code| 33          | 0         | 33        |
| Phase 4: Prototype     | 12          | 0         | 12        |
| Phase 5: Production    | 24          | 0         | 24        |
| Phase 6: QA            | 22          | 0         | 22        |
| Phase 7: Launch        | 25          | 0         | 25        |
| **Total**              | **163**     | **0**     | **163**   |

---

*Check items off as they are completed. Update the Completion Summary table periodically.*
