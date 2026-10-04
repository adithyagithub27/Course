# Decisions Required from Course Owner

> **Purpose:** This document lists the specific items that only the course owner can provide or approve. These are the hard blockers — production cannot proceed past certain milestones without these inputs.
>
> **Last Updated:** 2026-10-04 (Course 2; items 9–11 added after the 2026-10-01 review)

---

## Overview

There are **11 items** that require your direct input. Each has a deadline tied to the production timeline. Items are ordered by when they're needed.

---

## Decisions

### 1. Approve Visual Design System

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 7 (before graphics production begins)                          |
| **Status**   | Pending                                                            |
| **Category** | Visual Identity                                                     |
| **What**     | Review and approve the visual design system: color palette, typography, slide templates, diagram style, and code snippet styling. |
| **Why**      | All graphics, slides, and video overlays are built from this system. Changing it after production starts means re-doing all visual assets. |
| **Deliverable** | Design system document with 3+ thumbnail options will be presented for your review. You select the direction or request revisions. |

---

### 2. Personal Branding Assets

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 7 (used in course intro, thumbnail, and Udemy profile)         |
| **Status**   | Pending                                                            |
| **Category** | Branding                                                            |
| **What**     | Provide your personal branding assets: logo (if any), professional bio (2–3 sentences), and tagline or positioning statement. |
| **Why**      | These appear in the course introduction lecture, Udemy instructor profile, course thumbnail, and marketing materials. |
| **Deliverable** | Send logo file (PNG/SVG), written bio, and tagline. If no logo exists, confirm whether one should be created. |

---

### 3. Review Prototype Lectures

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 8 (before full production begins)                              |
| **Status**   | Pending                                                            |
| **Category** | Quality Gate                                                        |
| **What**     | Watch the Module 3 pilot (lectures 3.1–3.4) and provide feedback on avatar quality, pacing, visual style, and overall feel. Give explicit go/no-go for full production. |
| **Why**      | This is the last checkpoint before producing all 55 lectures. Changes after this point are exponentially more expensive. |
| **Deliverable** | Watch the prototypes, then respond with: (a) Approved as-is, (b) Approved with minor notes, or (c) Needs revision before proceeding. |

---

### 4. HeyGen Avatar

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 9 (before avatar video generation begins)                      |
| **Status**   | Pending                                                            |
| **Category** | Production — Avatar                                                 |
| **What**     | Choose the HeyGen avatar that narrates all lectures (shared by Courses 2–4). |
| **Why**      | All lecture videos are generated using this avatar. It must be selected and confirmed before any HeyGen API calls are made. |
| **Deliverable** | Select the avatar in HeyGen, set its ID as the `HEYGEN_AVATAR_ID` environment variable on the production machine (never in the repo, `CLAUDE.md`), and record the avatar's **name** in `09-heygen/avatar-config/PENDING.md`. |

---

### 5. HeyGen Voice

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 9 (before avatar video generation begins)                      |
| **Status**   | Pending                                                            |
| **Category** | Production — Avatar                                                 |
| **What**     | Choose the HeyGen voice for all narration (voice, accent, speaking style). |
| **Why**      | Voice consistency across all 55 lectures (and Courses 3–4) is critical. The voice must match the avatar and course tone. |
| **Deliverable** | Select the voice (or confirm a cloned voice is ready), set `HEYGEN_VOICE_ID` in the environment, and record the voice **name** in `09-heygen/voice-config/PENDING.md`. |

---

### 6. Final Course Title Selection

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 12 (before Udemy upload and marketing launch)                  |
| **Status**   | Pending                                                            |
| **Category** | Marketing & Positioning                                             |
| **What**     | Select the final course title from a shortlist of SEO-optimized options. The title appears on Udemy, in marketing, and on the thumbnail. |
| **Why**      | The title is the single most important factor in Udemy search discoverability. It must balance keyword optimization with clarity and appeal. |
| **Deliverable** | Shortlist with SEO analysis: `13-marketing/course-title-options.md` (recommended #1, as used in `12-udemy/course-description.md`). Confirm or pick another. |

---

### 7. Pricing Strategy

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 12 (before course goes live)                                   |
| **Status**   | Pending                                                            |
| **Category** | Business                                                            |
| **What**     | Decide on pricing approach: Udemy's free pricing tier vs. paid tier. If paid, confirm the base price. Define launch coupon strategy (discount percentage, duration, quantity). |
| **Why**      | Pricing affects positioning, perceived value, and launch strategy. Coupon strategy drives initial enrollment velocity, which impacts Udemy's algorithm ranking. |
| **Deliverable** | Confirm: (a) Paid or free, (b) Base price if paid, (c) Launch coupon discount % and duration, (d) Whether to create affiliate/referral coupons. |

---

### 8. Final Publish Approval

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Week 12 (final gate before going live)                              |
| **Status**   | Pending                                                            |
| **Category** | Launch Gate                                                         |
| **What**     | After all QA is complete and the course is fully uploaded to Udemy, give the final approval to press "Publish." |
| **Why**      | This is the point of no return. Once published, the course is live and students begin enrolling. Any issues discovered post-publish require updates, not prevention. |
| **Deliverable** | Review the complete course on Udemy (preview mode), confirm everything looks correct, and give written approval to publish. |

---

### 9. OpenAI SDK: stay on 2.x or move to 3.x

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Before recording Module 1 (code on screen shows the SDK version)    |
| **Status**   | Pending — current default: stay on 2.x                              |
| **Category** | Technology Stack                                                    |
| **What**     | The student repo pins `openai~=2.54` (fix-plan T6, same as Course 4). PyPI also has the 3.x line (3.22.1 on 2026-10-01). |
| **Why**      | Staying on 2.x matches Course 4 and the verified lock file; moving to 3.x keeps the course current longer but means re-running all 204 tests and 61 demos, re-capturing outputs and updating every version banner and script line that names 2.54.0. |
| **Deliverable** | Confirm "stay on 2.x for launch" (recommended) or "move to 3.x" (then the code package upgrades, re-verifies and the docs re-capture). |

---

### 10. Garak in Lecture 8.5: run it with torch, or show it as configuration only

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Before recording Module 8                                           |
| **Status**   | Pending                                                             |
| **Category** | Content / Production                                                |
| **What**     | Garak 0.17.0 is configured (`security/garak/rest_generator.json`, `make garak`) but was **not run** in the build environment: it pulls torch (about 2 GB) and conflicts with RAGAS's `datasets`, so it installs as a separate uv tool. PyRIT and promptfoo were run for real. |
| **Why**      | Lecture 8.5 should show a real Garak report; no pass rate may be invented. |
| **Deliverable** | Either (a) approve installing Garak with torch on the recording machine and capturing a real scan for 8.5 and its demo spec (`03-demos/demo-scripts/demo-35-garak-pyrit.md`), or (b) keep Garak as "configuration and command only" and say so on screen. |

---

### 11. Live re-capture of offline (mock) numbers

| Field        | Detail                                                              |
|--------------|---------------------------------------------------------------------|
| **Needed By**| Before recording each module                                        |
| **Status**   | Pending                                                             |
| **Category** | Content accuracy / Budget                                           |
| **What**     | Every number in scripts, labs, projects and demo specs comes from **offline mode** (deterministic mock LLM and mock judge; simulated latency; token counts `len/4` where tiktoken's encoding wasn't available). They are labelled offline. Decide whether to re-run key demos live (`OFFLINE=0`, gpt-4.1-mini agent, gpt-4.1 judge) and show live numbers instead. |
| **Why**      | Offline numbers are reproducible for students but are not facts about GPT models (e.g. routing "keeps quality" by construction offline; Garak not run). Live re-capture costs a few dollars (verify current pricing) and makes numbers vary between takes. |
| **Deliverable** | Choose per module: (a) record offline and label it (cheapest, reproducible), or (b) re-capture live for the lectures that state model scores, latency or cost (recommended at least for 1.1 tokens, 9.2 traces, 10.1/10.3 cost and latency, 11.3 synthetic data, 12.2 the live PR gate). Also provide an API key with a spending limit for the recording machine. |

---

## Timeline Summary

```
Week 7  ──► Approve Visual Design System
         ──► Provide Personal Branding Assets

Week 8  ──► Review Prototype Lectures (go/no-go)

Week 9  ──► Provide HeyGen Avatar ID
         ──► Provide HeyGen Voice ID

Module 1 ─► OpenAI SDK line (2.x vs 3.x)
Module 8 ─► Garak with torch or configuration only
Per module ► Live re-capture of offline numbers

Week 12 ──► Select Final Course Title
         ──► Decide Pricing Strategy
         ──► Give Final Publish Approval
```

---

## Status Tracker

| # | Decision                        | Needed By | Status  |
|---|---------------------------------|-----------|---------|
| 1 | Approve visual design system    | Week 7    | Pending |
| 2 | Personal branding assets        | Week 7    | Pending |
| 3 | Review prototype lectures       | Week 8    | Pending |
| 4 | HeyGen Avatar ID                | Week 9    | Pending |
| 5 | HeyGen Voice ID                 | Week 9    | Pending |
| 6 | Final course title selection    | Week 12   | Pending |
| 7 | Pricing strategy                | Week 12   | Pending |
| 8 | Final publish approval          | Week 12   | Pending |
| 9 | OpenAI SDK 2.x vs 3.x           | Before Module 1 recording | Pending (default 2.x) |
| 10 | Garak run with torch            | Before Module 8 recording | Pending |
| 11 | Live re-capture of mock numbers | Per module | Pending |

---

*Nothing else is needed from the course owner — all other work is handled by the production team and AI assistant.*
