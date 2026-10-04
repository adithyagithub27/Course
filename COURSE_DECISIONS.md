# Course Decisions Log

> **Purpose:** Record every significant decision made during course development, including rationale, alternatives considered, and current status. This creates an audit trail so future questions about "why did we do X?" have a clear answer.
>
> **Last Updated:** 2026-10-04

---

## How to Use This Document

- Add new decisions at the bottom with the next sequential number
- Never delete a decision — mark it as `Superseded` if it changes
- Include the date, reasoning, and what alternatives were rejected
- Reference this document when revisiting past choices

---

## Decision Status Legend

| Status       | Meaning                                              |
|--------------|------------------------------------------------------|
| Approved     | Decision is final and active                         |
| Under Review | Decision is being evaluated or discussed             |
| Superseded   | Replaced by a newer decision (reference the new one) |
| Deferred     | Postponed to a later date                            |

---

## Decisions

### Decision 1: Course is Fully Standalone

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Course Architecture                                                    |
| **Decision**   | This course has zero dependency on any prior course. Students need only basic Python knowledge. |
| **Reason**     | Maximizes addressable audience. Students discovering this course via Udemy search should not feel they need to buy another course first. Standalone courses have higher conversion rates. |
| **Alternatives Considered** | |
| Soft sequel    | Reference Course 1 concepts but don't require it — rejected because it still creates perceived dependency |
| Direct sequel  | Require Course 1 as a prerequisite — rejected because it cuts the addressable market significantly |

---

### Decision 2: Primary LLM is OpenAI GPT-4o-mini

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | **Superseded** by Decision 9 (2026-10-02): `gpt-4.1-mini` agent, `gpt-4.1` judge |
| **Category**   | Technology Stack                                                       |
| **Decision**   | All course examples, labs, and projects use OpenAI GPT-4o-mini as the primary LLM. |
| **Reason**     | Cheapest frontier API model available. Most familiar to students (largest developer community). Total estimated API cost for students completing the entire course: ~$5–10. Low barrier to entry. |
| **Alternatives Considered** | |
| Multi-provider | Support OpenAI + Anthropic + Google — rejected because it adds complexity without educational value, and triples the code paths to maintain |
| Ollama-only    | Fully local/free — rejected because Ollama models underperform on evaluation tasks, and many students lack GPU hardware |

---

### Decision 3: Audience Weight is 55% Beginner / 45% Enterprise

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Audience & Positioning                                                 |
| **Decision**   | Target a 55/45 split between beginner-friendly content and enterprise-depth content. |
| **Reason**     | Maximizes Udemy enrollment (beginners drive volume) while differentiating from competitors (enterprise depth drives reviews and word-of-mouth). Beginners get a complete learning path; experienced engineers get production patterns they can't find elsewhere. |
| **Alternatives Considered** | |
| 80/20 beginner-heavy | Would lose differentiation — too similar to existing shallow courses |
| 30/70 enterprise-heavy | Would lose the Udemy beginner market — niche audience, lower enrollment |

---

### Decision 4: Build Fresh Production Pipeline

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Production                                                             |
| **Decision**   | Build an entirely new production pipeline (visual design, templates, HeyGen config, editing workflow) rather than reusing assets from Course 1. |
| **Reason**     | New visual identity creates a fresh brand for this course series. Avoids inheriting any suboptimal choices from prior production. Allows us to optimize the pipeline with lessons learned. |
| **Alternatives Considered** | |
| Reuse Course 1 pipeline | Faster but carries forward visual debt and limits creative improvement |
| Partial reuse          | Cherry-pick some templates — rejected because inconsistency looks worse than fully old or fully new |

---

### Decision 5: Hybrid GitHub Strategy

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Distribution & Marketing                                               |
| **Decision**   | Maintain a public GitHub repository with the reusable testing framework and utilities. Keep course-exclusive content (scripts, labs with solutions, project solutions) in the private production repo. |
| **Reason**     | Public repo drives organic traffic and SEO — developers discovering the framework on GitHub become course prospects. Course-exclusive content maintains enrollment value — students pay for the guided learning experience, not just the code. |
| **Alternatives Considered** | |
| Fully public   | All content on GitHub — rejected because it undermines course enrollment value |
| Fully private  | Nothing public — rejected because it loses the organic discovery and SEO channel |

---

### Decision 6: Target Runtime 8.5–9.5 Hours

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | **Superseded** by Decision 8 (2026-10-02): the curriculum as built is 55 lectures, 400 minutes (6 h 40 min) |
| **Category**   | Course Design                                                          |
| **Decision**   | Target a total course runtime of 8.5 to 9.5 hours across ~60 lectures. |
| **Reason**     | Focused and tight. Research shows courses in the 6–12 hour range have the best completion rates on Udemy. The primary competitor (DeepEval course) is 7.7 hours — we go slightly longer to cover more ground while staying competitive. Avoids bloat that kills completion rates. |
| **Alternatives Considered** | |
| 5–6 hours      | Too short to cover the full testing lifecycle with depth |
| 12–15 hours    | Risk of low completion rates; padding content to fill time |

---

### Decision 7: 12+ Week Premium Production Timeline

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-09-24                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Project Management                                                     |
| **Decision**   | Allocate a minimum of 12 weeks for end-to-end production, from strategy through launch. |
| **Reason**     | Allows thorough research, multiple review cycles, iteration on prototype lectures, and polish. Rushed courses result in lower ratings and more student complaints. A 12+ week timeline supports the "premium quality" positioning. |
| **Alternatives Considered** | |
| 4–6 week sprint | Possible but sacrifices quality, QA depth, and iteration cycles |
| 20+ weeks       | Diminishing returns; risks losing momentum and market timing |

---

### Decision 8: Real Runtime — 55 Lectures, 6 h 40 min (supersedes Decision 6)

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-10-02                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Course Design                                                          |
| **Decision**   | The course is the curriculum's 54 lectures plus Lecture 8.5 "Beyond promptfoo: Garak and PyRIT": **55 lectures, 400 minutes of lectures (6 h 40 min)**. Every claim (README, curriculum header, Udemy copy, marketing) uses these numbers. |
| **Reason**     | The 2026-10-01 review summed the lecture tables: 54 lectures, 392 minutes, against "~60 lectures, 8.5–9.5 hours" in the marketing. Promising 2 hours that don't exist would hurt reviews. Fix-plan decision T7. |
| **Alternatives Considered** | |
| Add ~2 h of lectures | Rejected for now: padding hurts completion; candidate additions are listed in the review if the owner wants them later |
| Keep the old claim | Rejected: misleading on the Udemy listing |

---

### Decision 9: Models — gpt-4.1-mini Agent, gpt-4.1 Judge (supersedes Decision 2)

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-10-02                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Technology Stack                                                       |
| **Decision**   | Default chat model `gpt-4.1-mini`, judge `gpt-4.1` (or `gpt-4.1-mini` where cost matters), embeddings `text-embedding-3-small`. Every price on screen carries "verify current pricing". Same across Courses 2–4. |
| **Reason**     | Fix-plan decision A8; aligns the three courses. An offline mode (Decision 10, T6) means students need no key at all to follow the course. |
| **Alternatives Considered** | |
| Stay on gpt-4o-mini | Rejected: older model family, inconsistent with Courses 3 and 4 |
| GPT-5 family | Deferred: re-evaluate at the next yearly refresh |

---

### Decision 10: Adopt the 2026-10-01 Fix Plan (T1–T9) for Course 2

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | 2026-10-02                                                             |
| **Status**     | Approved                                                               |
| **Category**   | Course Architecture / Production                                       |
| **Decision**   | Course 2 follows the frozen decisions in `14-quality-review/2026-10-01-fix-plan.md` (and the all-course decisions A1–A10): **T1** one running example, the TechCorp support agent (TechGear retired); **T2** six failure modes (hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift, infinite loops); **T3** five quality dimensions (correctness, faithfulness, relevance, safety, reliability); **T4** the five-layer agent eval pyramid and one test-strategy template; **T5** scripts in `02-course-content/section-XX-slug.md` in the Course 3/4 cue format (legacy `09-heygen/scripts/` removed); **T6** stack: Python 3.11+, openai 2.x, deepeval 4.x, ragas 0.4.x, langfuse 4.x, promptfoo current, offline mode with mock LLM and judge; **T7** 55 lectures incl. 8.5 (Decision 8); **T8** positioning on full lifecycle + CI/CD gates + enterprise scenarios, never "first" or "only"; **T9** no `scene-plans/`/`visual-specs/`, a `10-graphics/slide-deck-outline.md` instead. |
| **Reason**     | The review found three versions of each taxonomy, two running examples, a stale stack and an unparseable script format. Freezing the decisions let parallel work stay consistent. When a fix needs a decision not listed, the code is right unless it has a bug. |
| **Alternatives Considered** | See the fix plan and `14-quality-review/2026-10-01-course2-agent-testing-review.md` §(d) |

---

## Template for New Decisions

```markdown
### Decision N: [Title]

| Field          | Detail                                                                 |
|----------------|------------------------------------------------------------------------|
| **Date**       | YYYY-MM-DD                                                             |
| **Status**     | Approved / Under Review / Superseded / Deferred                        |
| **Category**   | [Category]                                                             |
| **Decision**   | [What was decided]                                                     |
| **Reason**     | [Why this was chosen]                                                  |
| **Alternatives Considered** | |
| [Alt 1]        | [Why rejected] |
| [Alt 2]        | [Why rejected] |
```

---

*Add new decisions as they arise. Never delete — only supersede.*
