# Launch Plan: 8 Weeks

**Course:** Production Voice AI Agents with Python: Build, Test, Deploy (Course 3, Build → Test → Operate series)
**Shape:** 4 weeks pre-launch (W-4 to W-1), launch week (W0), 3 weeks post-launch (W+1 to W+3). Adjust dates to the actual publish approval date. Udemy review can take several days (verify current review times).

> **Market context (from `00-course-strategy/next-course-market-research.md` only):** a no-code voice-agent course on Udemy ("AI Builder in n8n", agents and voice agents) has 37,833 students at 4.8 stars, and "n8n AI Agents, Automations & Voice Agents" has 50,038 students. The research found only three code-first voice courses on Udemy, and none of them teaches testing or evaluating voice agents. Re-verify these figures in Udemy Marketplace Insights before quoting them publicly. Don't use them in the landing page.

---

## Goals (set your own targets)

| Metric | Where to read it | Target |
|---|---|---|
| Enrollments in the first 30 days | Instructor dashboard | `[set after Marketplace Insights check]` |
| Reviews in the first 30 days | Dashboard | `[set]` |
| Average rating | Dashboard | `[set]` |
| Refund rate | Dashboard | `[set]` |
| Section 2 completion (setup friction proxy) | Course engagement report | `[set]` |
| Q&A median response time | Q&A | < 24 h during W0-W+3 |

Targets are left blank on purpose: set them from Course 1 and Course 2 actuals rather than guessing.

---

## Timeline

### W-4: Foundations

- [ ] Finish `07-udemy-listing/` fields in Udemy; landing page in draft
- [ ] Public repo `voice-agents-course` ready: README with setup, lecture→file map, CI badge. Keep the course link to one "Learn more" line (see `cross-sell-plan.md` for rules)
- [ ] Record the promo video (`07-udemy-listing/promo-video-script.md`)
- [ ] YouTube video #1 (see `youtube-strategy.md`): "I built an AI receptionist that answers a real phone number"
- [ ] LinkedIn/X posts 1-2 (`linkedin-and-x-posts.md`)
- [ ] Recruit 10-30 **beta students** from Course 1 and Course 2 Q&A regulars and your personal network. Tell them clearly: *you'll get free access; you are not asked to leave a review; if you do review, be honest*

### W-3: Proof

- [ ] YouTube video #2: "Why your voice agent feels slow: the 800 ms latency budget"
- [ ] LinkedIn/X posts 3-4
- [ ] Publish one free resource (the latency budget worksheet or voice failure taxonomy) as a LinkedIn document post. This gives people value before you ask them for anything
- [ ] Submit the course for Udemy review if all sections are done. If not, submit at W-1 at the latest

### W-2: Beta and fixes

- [ ] Beta students go through Sections 1-3 (setup is where voice courses lose people)
- [ ] Collect friction: OS-specific mic issues, key errors, uv problems. Fix them in the repo README and pinned Q&A drafts
- [ ] YouTube video #3: "Testing a voice agent like software (LiveKit test framework)"
- [ ] LinkedIn/X posts 5-6

### W-1: Warm-up

- [ ] Course approved. Set price; draft coupons **only after verifying current coupon rules** (`07-udemy-listing/course-settings.md` §5)
- [ ] Turn on Q&A; pin the setup, costs, versions and SIP troubleshooting posts
- [ ] Prepare the Course 1 and Course 2 **promotional announcements** (count against Udemy's monthly promotional limit; verify)
- [ ] Prepare an update to the bonus lectures of Courses 1 and 2 (see `cross-sell-plan.md`)
- [ ] LinkedIn/X post 7 (teaser)

### W0: Launch week

| Day | Action |
|---|---|
| D0 | Publish. Send beta students free coupons (if not already enrolled). LinkedIn/X launch posts 8-9. YouTube community post. Update the repo README "Learn more" line |
| D1 | Promotional announcement to Course 1 students (within limits; verify) with a Best Price coupon |
| D2 | Promotional announcement to Course 2 students (if the monthly quota allows; otherwise next month) |
| D3 | Answer all Q&A. Record a 2-min "most common setup issue" fix and add it as a lecture resource or short lecture if needed |
| D4-D6 | Post 10 (demo clip of a live call + test run). Reply to every comment |
| D7 | Review: enrollments, refunds, engagement drop-off by lecture; triage fixes |

### W+1: Stabilise

- [ ] First educational announcement (the "start here" draft in `welcome-and-congratulations-messages.md`)
- [ ] Fix the top 3 friction points found in Q&A; post a changelog in the repo
- [ ] YouTube video #4 (a free preview-style tutorial from Section 9)
- [ ] LinkedIn/X post 11

### W+2: Depth

- [ ] YouTube video #5: "Cascaded vs OpenAI Realtime: same agent, same calls"
- [ ] Publish a written case study: "What broke when real people called Riley", from your own test calls, not student data
- [ ] Check the lecture-level drop-off report. If a lecture shows a sharp drop, re-cut it or add a note

### W+3: Review and plan

- [ ] 30-day check-in announcement (educational) scheduled for Day 30
- [ ] LinkedIn/X post 12 (results/learnings post, with no enrollment or revenue numbers unless you choose to share real ones)
- [ ] Compare against goals; decide on the first content update (framework version bump, Q&A-driven lecture)
- [ ] Update `competitor-watch.md`

---

## Review velocity strategy (Udemy-compliant)

Udemy prohibits incentivised or manipulated reviews. **Verify the current review and promotional guidelines before launch.** The strategy here: **earn reviews by getting students to a win early, and let Udemy's own review prompts do the asking.**

**Do**

1. **Put an early win in the first hour.** By lecture 2.6 the student is talking to the finished Riley, and by 3.3 to an agent they built themselves. Udemy prompts for a rating early in the course (timing set by Udemy), so the first hour must be the best hour. Setup (Section 2) has to be friction-free.
2. **Ask for an honest review at natural points, without pressure and without incentives:** once in the congratulations message and optionally once in a mid-course lecture outro (e.g., at the end of Section 8, after the phone call works). Example wording: *"If the course is helping, an honest review helps other engineers decide whether it fits them."*
3. **Respond to reviews** professionally, especially critical ones: thank them, fix the problem and say so in an educational announcement.
4. **Fix what reviews point to.** A fast Q&A turnaround stops the "doesn't work" 1-star reviews that setup-heavy courses attract.
5. **Beta students get free access with no strings attached.** Whether they review is up to them.

**Don't**

- Offer anything (coupons, bonus content, a shout-out, a lottery entry, a certificate or access) in exchange for a review or a particular rating
- Ask for "5 stars" or tell students how to rate
- Ask friends, family or colleagues to review without enrolling and taking the course
- Swap reviews with other instructors or join review groups
- Ask for reviews in promotional announcements, Q&A answers or direct messages in a way Udemy's rules don't allow (verify)
- Use multiple accounts, or ask students to change their review
