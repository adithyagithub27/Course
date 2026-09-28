# Cross-Sell Plan: Build → Test → Deploy → Operate

> How students move between the instructor's four courses, and how to promote across them **within Udemy's rules**. All Udemy policy statements here reflect the author's understanding. **Verify the current promotional, bonus-lecture, announcement and coupon rules in the Teaching Center before acting.**

---

## 1. The series

| # | Course | Role | Status |
|---|---|---|---|
| 1 | Generative AI & AI Agents: Zero to Production, Build Real Apps | **Build**: broad, top of funnel | In production (launch Q4 2026 per the research roadmap) |
| 2 | AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python | **Test**: quality and evals | In production (launch Q4 2026) |
| 3 | Production Voice AI Agents with Python: Build, Test, Deploy | **Build + Test + Deploy for voice**: specialised | Q1 2027 in the research roadmap |
| 4 | **AI Agent Observability & Cost Control: LLMOps in Production** | **Operate** | This course (Q2 2027 in the research roadmap, rank #2) |

The market research calls Course 1 the top of the funnel and says Course 4 "completes Build (C1), Test (C2), Operate (C4)" and "cross-sells to both existing student bases". Course 4 is the only course in the series that every other course points forward to: Course 1 students need to run what they built, Course 2 students need online evals after offline evals, and Course 3's Section 10 (observability, latency and cost) is a one-section preview of this whole course. It is also an **entry point** for engineers who arrive from SRE or FinOps rather than from AI.

## 2. Funnel paths

```
                ┌───────────────────────────────┐
  Udemy search  │ Course 1: Build (broad)       │  largest audience
  ────────────► │ "Zero to Production"          │
                └──────────────┬────────────────┘
                               │ bonus lecture + promo announcement
              ┌────────────────┴────────────────┐
              ▼                                 ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│ Course 2: Test            │◄───►│ Course 3: Voice           │  ◄── Udemy search
│ "AI Agent Testing & Eval" │     │ "Production Voice AI"     │      "voice AI agents"
└─────────────┬─────────────┘     └─────────────┬─────────────┘
              │  online evals                   │  Section 10 preview,
              │  after offline evals            │  domain-swap project
              └───────────────┬─────────────────┘
                              ▼
               ┌───────────────────────────────┐
               │ Course 4: Operate (this one)  │  ◄── Udemy search
               │ Observability, LLMOps, Cost   │      "LLM observability",
               └───────────────┬───────────────┘      "LLMOps", "Langfuse"
                               │ 14.6 domain swap, 15.4 bonus
                               ▼
                 back to C2 (deeper evals) or C3 (observe the voice agent)
```

| Path | Trigger | Message |
|---|---|---|
| C1 → C4 | Student finishes C1's deploy sections | "You've shipped an agent. Now find out what it costs and when it breaks." |
| C2 → C4 | Student finishes C2's LLM-judge / CI gate sections | "Offline evals pass. Production drifts anyway. Course 4 runs the judge on live traffic and gates PRs on cost and latency." |
| C3 → C4 | Student finishes C3 Section 10 (observability, latency, cost) | "Section 10 was one section. Course 4 is the whole operate discipline: tracing, showback, SLOs, incidents." |
| C4 → C2 | Student finishes C4 Section 8 (online evals) or 8.6 (bad trace → regression test) | "You promoted a bad trace to a dataset. Course 2 teaches the offline eval suite that runs against it." |
| C4 → C3 | Student reaches 14.6 (domain swap names the voice agent) | "Instrument a voice agent with the same stack. Course 3 builds the agent; 14.6 observes it." |
| C4 → C1 | New-to-agents students who found C4 through SRE or FinOps search | "Want to build the agent you're now observing? Course 1." |

## 3. Where promotion is allowed (verify each)

| Location | Allowed? (as understood; verify) | Our use |
|---|---|---|
| **Bonus lecture** (the last lecture of a course, labelled bonus) | Yes. Udemy allows promoting other courses with coupons here, with limits on off-platform links and lead capture | 15.4 in Course 4. Update the bonus lectures in Courses 1, 2 and 3 to add Course 4 |
| **Promotional announcements** | Yes, with a monthly cap per course (historically ~2/month; verify) and formatting rules | Launch announcements to C1, C2 and C3 students (see `launch-plan.md` W0) |
| **Educational announcements** | Educational only; no promotion | Launch "start here", updates, 30-day check-in |
| Lecture videos, lecture descriptions, captions, quizzes, resources | No promotional content | The curriculum's factual cross-links (4.5 and 8.6 "bridge to Course 2", 7.1 "link to Course 3 voice budgets", 14.6 "the Course 3 voice agent") must stay **one-line, factual, link-free and coupon-free**. If a reviewer could read them as promotion, move them to 15.4. **Don't** add any others |
| Welcome and congratulations messages | No links or promotion | The congrats message only says the bonus lecture covers next steps |
| Q&A and direct messages | No promotion | Answer the question; don't mention courses |
| Instructor profile | Profile and social links in the dedicated fields | Standard |
| Off-Udemy (YouTube, LinkedIn, X, repo README, newsletter, series landing page) | Your own channels | Coupon links, series page |

## 4. Bonus lecture placement

- **Course 4, lecture 15.4 "Bonus lecture":** a 3-5 min talking-head/avatar lecture plus a text resource listing:
  - Course 2 (*AI Agent Testing & Evaluation*) with a custom-price coupon: framed as "the offline evals your datasets from 8.6 feed"
  - Course 3 (*Production Voice AI Agents with Python*): "the agent 14.6 asks you to observe"
  - Course 1 (*Generative AI & AI Agents: Zero to Production*): "broader agent foundations if you came here from SRE or FinOps"
  - Community / newsletter link **only if current bonus-lecture rules allow it** (Udemy has restricted off-platform lead-generation links; verify)
- **Courses 1, 2 and 3:** update their bonus lectures at Course 4 launch to add Course 4 with a coupon. Course 3's 15.3 already says "Course 4 when it launches (update the lecture then)". Keep each bonus lecture's list short and relevant.
- Refresh coupons in bonus lectures monthly, or use the longest-lived coupon type the rules allow. An expired coupon in a bonus lecture is a bad student experience.

## 5. Four-course funnel and "bundle" ideas

Udemy's marketplace doesn't offer instructor-built bundles or multi-course discounts the way some platforms do (verify; this may change). Workable alternatives:

| Idea | How | Notes |
|---|---|---|
| **Series coupon rotation** | Each month, one course in the series gets a custom-price coupon promoted in the other three courses' promotional announcements | Stays within monthly announcement caps; with four courses, each course is "featured" once a quarter |
| **"Test + Operate" pairing** | Promote C2 to C4 students who finish Section 8, and C4 to C2 students who finish the CI quality-gate sections | The most natural pair: both are production-quality courses, and 8.6 literally hands a dataset from one to the other |
| **"Voice + Operate" pairing** | Promote C4 to C3 students who finish Section 10, and C3 to C4 students who reach 14.6 | The domain-swap project is the bridge |
| **Series landing page off Udemy** | A simple page (personal site or GitHub Pages) showing the Build → Test → Deploy → Operate path with each course's coupon link, and a suggested order (1 → 2 → 4, with 3 as the voice branch) | Your own site, your own rules |
| **Udemy Business** | Every course is eligible for Udemy Business if accepted (verify program terms). A four-course path with a clear Build → Test → Deploy → Operate story is easier for a company to assign as a learning path than four unrelated courses | Out of your control, but good course quality and consistent naming help |
| **Consistent pricing** | Same price tier for C2, C3 and C4 | Keeps coupon messaging simple |
| **Shared running examples** | Course 4's domain swap (14.6) instruments Course 3's Riley; Course 4's 8.6 feeds Course 2's eval pipeline | Content-level bundling that needs no Udemy feature |

## 6. Measurement

| Metric | How |
|---|---|
| Cross-enrollments | A distinct coupon code per placement (bonus lecture C1, C2, C3; promo announcement per course; YouTube), tracked in the coupon sheet |
| Bonus lecture reach | Lecture views for the bonus lectures (course engagement report) |
| Series overlap | Dashboard student overlap, if Udemy reports it (verify) |
| Path performance | Which of the three inbound paths (C1, C2, C3) converts best in the first 90 days; the research predicts C2 and C3 are warmer |

Review these each month and put the money and effort into the path that converts best.
