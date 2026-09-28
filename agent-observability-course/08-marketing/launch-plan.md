# Launch Plan: 8 Weeks

**Course:** AI Agent Observability & Cost Control: LLMOps in Production (Course 4, Build → Test → Deploy → Operate series)
**Shape:** 4 weeks pre-launch (W-4 to W-1), launch week (W0), 3 weeks post-launch (W+1 to W+3). Adjust dates to the actual publish approval date. Udemy review can take several days (verify current review times). The research roadmap places this launch in **Q2 2027**, after Course 3.

> **Market context (from `../../00-course-strategy/next-course-market-research.md` only):** the research found three Langfuse/observability courses on Udemy ("LangFuse: LLM Observability, Tracing, Evaluation, Monitoring", "LLM Observability and Cost Management: Langfuse, Monitoring", "Production LLM Evaluation And Observability") and says "none large yet". It also found "LLM Token Optimization" and "FinOps for GenAI" courses that "are 1-hour briefings", and states that nothing on Udemy "combines OpenTelemetry GenAI semantic conventions, Langfuse/LangSmith/Arize Phoenix, drift detection and token FinOps". The research's own advice: "competition now exists, so lead with cost/FinOps + OTel angle". Re-verify all of this in Udemy Marketplace Insights before quoting it publicly. Don't use it in the landing page.

---

## Goals (set your own targets)

| Metric | Where to read it | Target |
|---|---|---|
| Enrollments in the first 30 days | Instructor dashboard | `[set after Marketplace Insights check]` |
| Reviews in the first 30 days | Dashboard | `[set]` |
| Average rating | Dashboard | `[set]` |
| Refund rate | Dashboard | `[set]` |
| Section 2 completion (setup friction proxy) | Course engagement report | `[set]` |
| Section 11 start rate (did students reach the incident labs?) | Course engagement report | `[set]` |
| Cross-enrollments from Courses 1-3 | Coupon sheet | `[set]` |
| Q&A median response time | Q&A | < 24 h during W0-W+3 |

Targets are left blank on purpose: set them from Course 1, 2 and 3 actuals rather than guessing. Course 4 is the first course with three existing student bases to draw on, so the cross-enrollment target matters more than for the earlier launches.

---

## Timeline

### W-4: Foundations

- [ ] Finish `07-udemy-listing/` fields in Udemy; landing page in draft
- [ ] Public repo `agent-observability-course` ready: README with setup, lecture→file map, offline mode, CI badge (the budget gate itself is a talking point). Keep the course link to one "Learn more" line (see `cross-sell-plan.md` for rules)
- [ ] Record the promo video (`07-udemy-listing/promo-video-script.md`)
- [ ] YouTube video #1 (see `youtube-strategy.md`): "I watched an AI agent burn $4,000 in a weekend (simulated). Here's the trace."
- [ ] LinkedIn/X posts 1-2 (`linkedin-and-x-posts.md`)
- [ ] Recruit 10-30 **beta students** from Course 1, 2 and 3 Q&A regulars and your personal network. Prioritise people who run an agent in production today. Tell them clearly: *you'll get free access; you are not asked to leave a review; if you do review, be honest*

### W-3: Proof

- [ ] YouTube video #2: "Cost per resolved session: the one number your manager wants from your agent"
- [ ] LinkedIn/X posts 3-4
- [ ] Publish one free resource (the latency budget worksheet or the GenAI semantic conventions cheat sheet) as a LinkedIn document post. Value before the ask
- [ ] Submit the course for Udemy review if all sections are done. If not, submit at W-1 at the latest

### W-2: Beta and fixes

- [ ] Beta students go through Sections 1-3 (setup is where this course can lose people: uv, Langfuse keys, the first OTLP export)
- [ ] Collect friction: OS-specific uv problems, Langfuse region and key confusion, `OFFLINE=1` misunderstandings, Docker on Apple Silicon. Fix them in the repo README and pinned Q&A drafts
- [ ] Ask two beta students to attempt Incident 1 blind and time them; adjust the 8-minute investigation window if needed
- [ ] YouTube video #3: "Instrument any LLM agent with OpenTelemetry in 15 minutes (GenAI semantic conventions)"
- [ ] LinkedIn/X posts 5-6

### W-1: Warm-up

- [ ] Course approved. Set price; draft coupons **only after verifying current coupon rules** (`07-udemy-listing/course-settings.md` §5)
- [ ] Turn on Q&A; pin the setup, costs and offline mode, version pins, Docker and incident-lab posts
- [ ] Prepare the Course 1, 2 and 3 **promotional announcements** (count against Udemy's monthly promotional limit per course; verify). Course 3's Section 10 (observability) students and Course 2's students are the warmest
- [ ] Prepare updates to the bonus lectures of Courses 1, 2 and 3 (see `cross-sell-plan.md`)
- [ ] LinkedIn/X post 7 (teaser)

### W0: Launch week

| Day | Action |
|---|---|
| D0 | Publish. Send beta students free coupons (if not already enrolled). LinkedIn/X launch posts 8-9. YouTube community post. Update the repo README "Learn more" line |
| D1 | Promotional announcement to Course 2 students (the testing course; online evals is the natural bridge) with a Best Price coupon |
| D2 | Promotional announcement to Course 3 students (their Section 10 pointed at this course) |
| D3 | Promotional announcement to Course 1 students if each course's monthly quota allows; otherwise next month. Answer all Q&A |
| D4-D6 | Post 10 (demo clip: the cost meter climbing, then the fixed run). Reply to every comment |
| D7 | Review: enrollments, refunds, engagement drop-off by lecture; triage fixes |

### W+1: Stabilise

- [ ] First educational announcement (the "start here" draft in `07-udemy-listing/welcome-and-congratulations-messages.md`)
- [ ] Fix the top 3 friction points found in Q&A; post a changelog in the repo
- [ ] YouTube video #4 (a free preview-style tutorial from Section 6)
- [ ] LinkedIn/X post 11

### W+2: Depth

- [ ] YouTube video #5: "Three incidents from traces alone: can you find root cause before the reveal?"
- [ ] Publish a written case study: "What the simulator taught me about agent cost", from the course's own replays, not student data
- [ ] Check the lecture-level drop-off report. If a lecture shows a sharp drop, re-cut it or add a note. Watch 3.2 (the longest manual instrumentation code-along) and 13.1 (Docker) in particular

### W+3: Review and plan

- [ ] 30-day check-in announcement (educational) scheduled for Day 30
- [ ] LinkedIn/X post 12 (results/learnings post, with no enrollment or revenue numbers unless you choose to share real ones)
- [ ] Compare against goals; decide on the first content update (semconv attribute renames, langfuse minor bump, Q&A-driven lecture)
- [ ] Update `competitor-watch.md`

---

## Review velocity strategy (Udemy-compliant)

Udemy prohibits incentivised or manipulated reviews. **Verify the current review and promotional guidelines before launch.** The strategy here: **earn reviews by getting students to a win early, and let Udemy's own review prompts do the asking.**

**Do**

1. **Put an early win in the first hour.** By lecture 2.3 the student has a real trace on screen, and by 2.4 a full day of traffic in the Ops Console without spending money. Udemy prompts for a rating early in the course (timing set by Udemy), so the first hour must be the best hour. Setup (Section 2) has to be friction-free.
2. **Ask for an honest review at natural points, without pressure and without incentives:** once in the congratulations message and optionally once in a mid-course lecture outro (e.g., at the end of Section 6, after the 40% challenge). Example wording: *"If the course is helping, an honest review helps other engineers decide whether it fits them."*
3. **Respond to reviews** professionally, especially critical ones: thank them, fix the problem and say so in an educational announcement.
4. **Fix what reviews point to.** A fast Q&A turnaround stops the "doesn't work" 1-star reviews that setup-heavy courses attract. Docker and self-hosting (Section 13) are the most likely source; the offline path is the mitigation.
5. **Beta students get free access with no strings attached.** Whether they review is up to them.

**Don't**

- Offer anything (coupons, bonus content, a shout-out, a lottery entry, a certificate or access) in exchange for a review or a particular rating
- Ask for "5 stars" or tell students how to rate
- Ask friends, family or colleagues to review without enrolling and taking the course
- Swap reviews with other instructors or join review groups
- Ask for reviews in promotional announcements, Q&A answers or direct messages in a way Udemy's rules don't allow (verify)
- Use multiple accounts, or ask students to change their review
