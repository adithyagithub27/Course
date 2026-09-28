# Course Settings

> Values to enter in Udemy's course management screens (Course landing page → Basic info, Pricing, Promotions, Course messages, Settings). **Udemy changes menu names, category trees, price tiers and coupon rules from time to time. Every item marked "verify" must be checked in the instructor dashboard and the Udemy Teaching Center before you rely on it.**

---

## 1. Basic info

| Field | Value | Notes |
|---|---|---|
| Language | English (US) | |
| Level | **Intermediate Level** | Curriculum: intermediate (basic Python and async/await). Sections 1-3 are beginner-safe, but "All Levels" would set the wrong expectation and invite low-rating reviews from true beginners. |
| Category | **Development** | |
| Subcategory | **Data Science** (first choice). Check whether an AI-specific subcategory exists and pick it if so | Udemy files most LLM and agent courses under Development → Data Science. If the dropdown shows a newer AI subcategory, compare where the top voice-agent and AI-agent courses in the market research sit and follow them (verify). |
| Primary topic ("What is primarily taught") | **AI Agents** (first choice). Alternatives: "Voice AI" or "Conversational AI" if they exist in the topic picker | The market research confirms an "AI Agents" topic page exists (`udemy.com/topic/ai-agents/`). Type "voice" into the picker to see whether a voice-specific topic exists, and pick the most specific topic that has real course volume (verify). |
| Course image | See `course-image-brief.md` | 750×422 |
| Promo video | See `promo-video-script.md` | |
| Instructor profile | See `instructor-bio.md` | |

## 2. Caption languages

| Language | Source | Action |
|---|---|---|
| English | Udemy auto-generated captions (verify availability for your account) | **Review and correct them.** Auto-captions get domain terms wrong: LiveKit, Pipecat, Deepgram, Cartesia, Silero, SIP, TTFT, TTFB, WER, `gpt-realtime`, Riley, Maple Street. HeyGen lectures can use the script as the caption source, which is more accurate than ASR. |
| Spanish, Portuguese (BR), German, French, Japanese and others | Udemy machine-translated captions, if offered for your course (verify) | Turn on whatever Udemy offers once the English captions are corrected, because translation quality depends on the English source. Don't pay for human translation until enrollment data shows non-English demand. |

## 3. Topics / tags (10+)

Udemy uses "What is primarily taught" plus the topics it infers from course content. Where the course management screen offers topic/keyword fields (verify current UI), enter these in priority order:

1. AI Agents
2. Voice AI
3. Voice Agents
4. Conversational AI
5. LiveKit
6. OpenAI Realtime API
7. Pipecat
8. Speech Recognition (STT)
9. Text-to-Speech (TTS)
10. Twilio / SIP Telephony
11. LLM Evaluation / AI Agent Testing
12. LLM Observability (Langfuse, OpenTelemetry)
13. Python
14. Docker

Use the same terms in section titles and lecture titles so Udemy's search index sees them in the curriculum as well as the description.

## 4. Price

**Recommendation: list at a mid-to-upper tier (the tier nearest USD 99.99-119.99 in Udemy's current price tier list; verify the tiers available to you).**

Reasoning:

- **Udemy's sitewide sales set most actual purchase prices.** When you opt in to Udemy's promotions (verify current program terms), the list price mostly acts as an anchor for the "% off" badge. A very low list price shrinks that badge and gains little.
- **The course is specialised and production-level.** It has ~11.3 h of video in 97 lectures, a full repo, labs, challenges, projects, a capstone, 12 quizzes, a practice test and coding exercises. It aims at working engineers, not casual learners, and pricing it like a beginner course undersells it.
- **The series should have consistent prices.** Price Course 3 in the same tier as Course 2 (*AI Agent Testing & Evaluation*), so cross-sell coupons and "bundle-like" offers stay simple (see `08-marketing/cross-sell-plan.md`).
- **There's room to test.** The research lists only three code-first voice courses and none is a bestseller. Record their current list and sale prices in `08-marketing/competitor-watch.md` before launch. Don't price off numbers we haven't checked.
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
| Soft launch (Days 0-3) | **Free**, capped at Udemy's limit | Beta reviewers from the Course 1 and Course 2 student lists, plus personal network. **No review is requested in exchange** | Get real students through Sections 1-3 early to find setup friction, and let natural first reviews appear |
| Launch week (Days 3-10) | **Best Price** | Course 1 and Course 2 students (via educational announcement per the rules below), LinkedIn, X, YouTube | Early enrollments at the lowest price |
| Weeks 2-4 | **Custom Price** (series price) | In-course bonus lecture of Courses 1 and 2; YouTube descriptions | Ongoing cross-sell at a stable price |
| Monthly after | Best Price or Custom Price, rotated | Newsletter, YouTube, conference talks | Instructor-referred sales between Udemy's sitewide sales |

Rules for ourselves:

- Never use coupons to buy reviews or tie them to reviews.
- Never post coupons in Q&A or direct messages, and follow Udemy's rules on where coupons may appear (verify).
- Track every coupon code in a sheet: code, type, dates, channel, redemptions and resulting reviews (for learning, not for incentives).

## 6. Course messages and communication settings

| Setting | Recommendation | Why |
|---|---|---|
| Q&A | **On.** Aim to answer within 24-48 hours during launch weeks | Voice setup involves API keys, mic permissions, SIP and Docker, and people will get stuck. Quick answers stop 1-star "it doesn't work" reviews. Q&A must stay free of promotional content (verify rules). |
| Q&A pinned posts | Pin posts for: "Setup checklist and common errors (Section 2)", "API keys and costs", "Version updates (livekit-agents / pipecat-ai)", "Phone number and SIP troubleshooting" | Heads off the most common questions |
| Direct messages | **On**, with a note in the welcome message pointing technical questions to Q&A so answers help everyone | Udemy doesn't allow promotional content in direct messages (verify) |
| Welcome message | See `welcome-and-congratulations-messages.md` | |
| Congratulations message | See `welcome-and-congratulations-messages.md` | |
| Announcements | Educational and promotional announcements within Udemy's monthly limits. See `welcome-and-congratulations-messages.md` | |
| Course-level Q&A features | Turn on any available "featured questions" / "Q&A notifications" | |
| Auto-generated course content (Udemy AI features) | Review anything Udemy auto-generates, such as AI summaries or AI assistant answers, if it applies to the course (verify) | Keeps its information about the stack accurate |

## 7. Practice test, quizzes and coding exercises (course-level settings)

| Item | Setting |
|---|---|
| Section quizzes | 12 quizzes (S1, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S14). Show explanations on every answer |
| Practice test | 1 × 40 questions (lecture 15.2). Set a pass mark (suggest 70%) and a time limit (suggest 60 min). Randomize question order if the option exists (verify) |
| Coding exercises | 5 pure-Python exercises (scheduler, WER, PII, latency percentile, cost/min). They must run offline in Udemy's in-browser runner with **no network calls and no third-party packages**. Check which Python version and packages Udemy's runner supports (verify) |
| Assignments | 4.7 challenge, 3 projects (5.8, 8.7, 9.11), 13.7 domain swap, plus the capstone, as Udemy "Assignments" with instructor example answers. Project 3 (9.11) is text-only |
| Challenge 5.9 (CE) | Video lecture with a pause card, **not** a Udemy coding exercise (it needs `livekit-agents`, which the in-browser runner can't install; verify runner limits) |
