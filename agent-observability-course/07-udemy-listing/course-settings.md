# Course Settings

> Values to enter in Udemy's course management screens (Course landing page → Basic info, Pricing, Promotions, Course messages, Settings). **Udemy changes menu names, category trees, price tiers and coupon rules from time to time. Every item marked "verify" must be checked in the instructor dashboard and the Udemy Teaching Center before you rely on it.**

---

## 1. Basic info

| Field | Value | Notes |
|---|---|---|
| Language | English (US) | |
| Level | **Intermediate Level** | Curriculum: intermediate (basic Python and one LLM API call before). Sections 1-3 are beginner-safe, but "All Levels" would set the wrong expectation for people who have never called an LLM API and invite low-rating reviews. |
| Category | **Development** | |
| Subcategory | **Data Science** (first choice). Check whether an AI-specific subcategory exists and pick it if so | Udemy files most LLM and agent courses under Development → Data Science. If the dropdown shows a newer AI subcategory, compare where the three Langfuse courses named in the market research sit and follow them (verify). A "Software Engineering" or "DevOps" placement is defensible for an observability course but would put it next to Kubernetes courses rather than AI courses; prefer the AI neighbourhood because that is where the series students already are. |
| Primary topic ("What is primarily taught") | **LLMOps** if the picker offers it; otherwise **AI Agents** | The market research confirms an "AI Agents" topic page exists (`udemy.com/topic/ai-agents/`). Type "LLMOps", "observability", "Langfuse" and "OpenTelemetry" into the picker and record which topics exist and how many courses each has. Pick the most specific topic with real course volume (verify). |
| Course image | See `course-image-brief.md` | 750×422 |
| Promo video | See `promo-video-script.md` | |
| Instructor profile | See `instructor-bio.md` | |

## 2. Caption languages

| Language | Source | Action |
|---|---|---|
| English | Udemy auto-generated captions (verify availability for your account) | **Review and correct them.** Auto-captions get domain terms wrong: Langfuse, OpenTelemetry, OTel, OTLP, OpenInference, LiteLLM, DeepEval, Prometheus, Grafana, TTFT, TPOT, p95, SLI, SLO, EWMA, PSI, semconv, `gen_ai.*`, Atlas, Northwind. HeyGen lectures can use the script as the caption source, which is more accurate than ASR. |
| Spanish, Portuguese (BR), German, French, Japanese, Hindi and others | Udemy machine-translated captions, if offered for your course (verify) | Turn on whatever Udemy offers once the English captions are corrected, because translation quality depends on the English source. Don't pay for human translation until enrollment data shows non-English demand. |

## 3. Topics / tags (10+)

Udemy uses "What is primarily taught" plus the topics it infers from course content. Where the course management screen offers topic/keyword fields (verify current UI), enter these in priority order:

1. LLMOps
2. AI Agents
3. LLM Observability
4. OpenTelemetry
5. Langfuse
6. AI FinOps / LLM cost optimization
7. MLOps
8. Site Reliability Engineering (SRE)
9. Prometheus
10. Grafana
11. LangSmith
12. LLM Evaluation
13. Python
14. Docker

Use the same terms in section titles and lecture titles so Udemy's search index sees them in the curriculum as well as the description (e.g., "Section 6: Cost Engineering: Token FinOps for Agents", "Section 9: Dashboards, SLOs and Alerting with Prometheus and Grafana").

## 4. Price

**Recommendation: list at the same tier as Courses 2 and 3 (the tier nearest USD 99.99-119.99 in Udemy's current price tier list; verify the tiers available to you).**

Reasoning:

- **Udemy's sitewide sales set most actual purchase prices.** When you opt in to Udemy's promotions (verify current program terms), the list price mostly acts as an anchor for the "% off" badge. A very low list price shrinks that badge and gains little.
- **The course is specialised and production-level.** It has ~10.5 h of video in 15 sections, a full repo with 419 offline tests, 7 labs, 5 challenges, 2 projects, a capstone, a domain swap, 13 quizzes, a practice test, 5 coding exercises and 4 incident datasets. It aims at working engineers and engineering managers, not casual learners.
- **The series should have consistent prices.** Price Course 4 in the same tier as Courses 2 and 3, so cross-sell coupons and "bundle-like" offers stay simple (see `08-marketing/cross-sell-plan.md`).
- **The buyer is often reimbursed.** Observability and cost control are budget-owner topics; many students will expense this course or take it through Udemy Business. Pricing it like a hobby course undersells it.
- **There's room to test.** The research names three Langfuse/observability courses on Udemy and says none is large yet. Record their current list and sale prices in `08-marketing/competitor-watch.md` before launch. Don't price off numbers we haven't checked.
- **What not to do:** don't make the course free. Udemy limits free courses (historically to under 2 hours of video, with no Q&A or messaging for students; verify), so a free course can't host this content.

Revisit the price after 60 days using conversion rate and refund rate from the instructor dashboard.

## 5. Launch coupon plan

> **Verify current Udemy coupon rules before creating any coupon.** Coupon types, validity windows, redemption caps, monthly limits and the "best price" definition have all changed over time. The descriptions below reflect Udemy's published instructor coupon system as the author understood it. Use them as a planning outline, not as policy.

### Coupon types (as understood; verify)

| Type | What it does (as understood) | Typical constraints to verify |
|---|---|---|
| **Best Price** | Sets the course to the lowest price Udemy allows for that market at that moment | Fixed validity window; limit on active coupons |
| **Custom Price** | You set a price between Udemy's minimum and the list price | Price floor; validity window can be set within limits; monthly creation cap |
| **Free** | Free enrollment through the coupon link | Hard redemption cap per coupon and a short validity window; monthly cap on free coupons. Students enrolled free may be weighted differently in some rankings or have restricted review/Q&A behaviour (verify) |

Also check: whether coupons can be created in the first days after publishing, how many coupons can be active at once, and how instructor-coupon sales count in the revenue share (instructor-referred sales historically earn a higher share; verify current terms).

### Plan

| When | Coupon | Audience | Purpose |
|---|---|---|---|
| Soft launch (Days 0-3) | **Free**, capped at Udemy's limit | Beta reviewers from the Course 1, 2 and 3 student lists, plus personal network. **No review is requested in exchange** | Get real students through Sections 1-3 early to find setup friction (Langfuse keys, Docker, uv), and let natural first reviews appear |
| Launch week (Days 3-10) | **Best Price** | Course 1, 2 and 3 students (via promotional announcement per the rules below), LinkedIn, X, YouTube | Early enrollments at the lowest price |
| Weeks 2-4 | **Custom Price** (series price) | In-course bonus lectures of Courses 1-3; YouTube descriptions | Ongoing cross-sell at a stable price |
| Monthly after | Best Price or Custom Price, rotated | Newsletter, YouTube, conference talks, the series landing page | Instructor-referred sales between Udemy's sitewide sales |

Rules for ourselves:

- Never use coupons to buy reviews or tie them to reviews.
- Never post coupons in Q&A or direct messages, and follow Udemy's rules on where coupons may appear (verify).
- Track every coupon code in a sheet: code, type, dates, channel, redemptions and resulting reviews (for learning, not for incentives).

## 6. Course messages and communication settings

| Setting | Recommendation | Why |
|---|---|---|
| Q&A | **On.** Aim to answer within 24-48 hours during launch weeks | Setup involves Langfuse keys, OpenAI caps, uv, Docker Compose and the OTel Collector, and people will get stuck. Quick answers stop 1-star "it doesn't work" reviews. Q&A must stay free of promotional content (verify rules). |
| Q&A pinned posts | Pin posts for: "Setup checklist and common errors (Section 2)", "API keys, spending caps and offline mode", "Version pins (langfuse 4 / otel 1.45 / semconv 0.66) and breaking changes", "Docker Compose and self-hosting troubleshooting (Section 13)", "Incident labs: how to post a hypothesis without spoiling the reveal" | Heads off the most common questions; the incident-lab post protects the pause-then-reveal format |
| Direct messages | **On**, with a note in the welcome message pointing technical questions to Q&A so answers help everyone | Udemy doesn't allow promotional content in direct messages (verify) |
| Welcome message | See `welcome-and-congratulations-messages.md` | |
| Congratulations message | See `welcome-and-congratulations-messages.md` | |
| Announcements | Educational and promotional announcements within Udemy's monthly limits. See `welcome-and-congratulations-messages.md` | |
| Course-level Q&A features | Turn on any available "featured questions" / "Q&A notifications" | |
| Auto-generated course content (Udemy AI features) | Review anything Udemy auto-generates, such as AI summaries or AI assistant answers, if it applies to the course (verify) | Keeps its information about the stack accurate, especially the incubating GenAI attribute names |

## 7. Practice test, quizzes and coding exercises (course-level settings)

| Item | Setting |
|---|---|
| Section quizzes | 13 quizzes (S1-S12 and S14; Section 13 and Section 15 have none). Show explanations on every answer |
| Practice test | 1 × 40 questions (lecture 15.3). Set a pass mark (suggest 70%) and a time limit (suggest 60 min). Randomize question order if the option exists (verify) |
| Coding exercises | 5 pure-Python exercises (per-token cost, percentile latency, EWMA anomaly, PII masking, context trimming). They must run offline in Udemy's in-browser runner with **no network calls and no third-party packages** (no `litellm`, no `tiktoken`). Check which Python version and packages Udemy's runner supports (verify) |
| Assignments | Project 1 (6.9 showback report), Project 2 (11.6 fourth incident postmortem), the capstone (14.1/14.5) and the domain swap (14.6), as Udemy "Assignments" with instructor example answers. Project 2's example answer is the unrevealed incident's solution; release it only through the assignment feedback flow, not as a public resource |
| Challenges 4.7, 6.8, 11.2, 11.3, 11.4 (CH) | Video lectures with a pause card, **not** Udemy coding exercises (they need `langfuse`, the local store and the replayed spans, which the in-browser runner can't provide; verify runner limits) |
| Free preview | 1.1 (the $4,000 weekend) as the primary free preview. Also consider 1.2, 2.3 (quick win) and 6.1 (token anatomy). Udemy allows a limited share of free preview content (verify) |
