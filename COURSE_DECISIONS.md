# Course Decisions Log

> **Purpose:** Record every significant decision made during course development, including rationale, alternatives considered, and current status. This creates an audit trail so future questions about "why did we do X?" have a clear answer.
>
> **Last Updated:** 2026-09-24

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
| **Status**     | Approved                                                               |
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
| **Status**     | Approved                                                               |
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
