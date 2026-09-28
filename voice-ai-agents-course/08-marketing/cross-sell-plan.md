# Cross-Sell Plan: Build → Test → Operate

> How students move between the instructor's courses, and how to promote across them **within Udemy's rules**. All Udemy policy statements here reflect the author's understanding. **Verify the current promotional, bonus-lecture, announcement and coupon rules in the Teaching Center before acting.**

---

## 1. The series

| # | Course | Role | Status |
|---|---|---|---|
| 1 | Generative AI & AI Agents: Zero to Production, Build Real Apps | **Build**: broad, top of funnel | In production (launch Q4 2026 per the research roadmap) |
| 2 | AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python | **Test**: quality and evals | In production (launch Q4 2026) |
| 3 | **Production Voice AI Agents with Python: Build, Test, Deploy** | **Build + Test for voice**: specialised | This course (Q1 2027 in the research roadmap) |
| 4 | AI Agent Observability, LLMOps & Cost Control (planned) | **Operate** | Planned Q2 2027 (research rank #2) |

The market research calls Course 1 the top of the funnel. It's in the most crowded category and should earn more from cross-sells than from organic ranking. Course 3 sits in a "proven demand, thin supply" lane and can also be an **entry point** for new students who then move to Courses 2 and 4.

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
│ "AI Agent Testing & Eval" │     │ "Production Voice AI"     │      "voice AI agents", "LiveKit"
└─────────────┬─────────────┘     └─────────────┬─────────────┘
              │                                 │
              └───────────────┬─────────────────┘
                              ▼
               ┌───────────────────────────────┐
               │ Course 4: Operate (planned)   │
               │ Observability, LLMOps, FinOps │
               └───────────────────────────────┘
```

| Path | Trigger | Message |
|---|---|---|
| C1 → C3 | Student finishes C1's agent sections | "You've built agents that chat. Make one that answers the phone." |
| C1 → C2 | Student finishes C1 | "You've built it. Now prove it works." |
| C2 → C3 | Student finishes C2's LLM-judge / tool-calling sections | "Apply the same testing discipline to voice: WER, latency budgets, simulated callers." |
| C3 → C2 | Student finishes C3 Section 9 | "Section 9 was one section. Course 2 goes deeper: RAGAS, promptfoo red teaming, CI quality gates." |
| C3 → C1 | New-to-agents students who found C3 through search | "Want broader agent foundations (RAG, tools, deploy) for text apps? Course 1." |
| C2/C3 → C4 | Course 4 launch | "Operate: tracing, cost control and drift across all your agents." |

## 3. Where promotion is allowed (verify each)

| Location | Allowed? (as understood; verify) | Our use |
|---|---|---|
| **Bonus lecture** (the last lecture of a course, labelled bonus) | Yes. Udemy allows promoting other courses with coupons here, with limits on off-platform links and lead capture | 15.3 in Course 3. Add or update equivalent bonus lectures in Courses 1 and 2 to mention Course 3 |
| **Promotional announcements** | Yes, with a monthly cap (historically ~2/month; verify) and formatting rules | Launch announcements to C1 and C2 students (see `launch-plan.md` W0) |
| **Educational announcements** | Educational only; no promotion | Launch "start here", updates, 30-day check-in |
| Lecture videos, lecture descriptions, captions, quizzes, resources | No promotional content | A plain factual mention like "Course 2 covers RAGAS in depth" may still count as promotion. **Don't do it.** Keep it only in the bonus lecture |
| Welcome and congratulations messages | No links or promotion | The congrats message only says the bonus lecture covers next steps |
| Q&A and direct messages | No promotion | Answer the question; don't mention courses |
| Instructor profile | Profile and social links in the dedicated fields | Standard |
| Off-Udemy (YouTube, LinkedIn, X, repo README, newsletter) | Your own channels | Coupon links, series page |

## 4. Bonus lecture placement

- **Course 3, lecture 15.3 "Bonus lecture":** a 3-5 min talking-head/avatar lecture plus a text resource listing:
  - Course 2 (*AI Agent Testing & Evaluation*) with a custom-price coupon: framed as "go deeper on evals"
  - Course 1 (*Generative AI & AI Agents: Zero to Production*): "broader agent foundations"
  - Course 4 when it launches (update the lecture then)
  - Community / newsletter link **only if current bonus-lecture rules allow it** (Udemy has restricted off-platform lead-generation links; verify)
- **Courses 1 and 2:** update their bonus lectures at Course 3 launch to add Course 3 with a coupon. Keep each bonus lecture's list short and relevant.
- Refresh coupons in bonus lectures monthly, or use the longest-lived coupon type the rules allow. An expired coupon in a bonus lecture is a bad student experience.

## 5. "Bundle" ideas

Udemy's marketplace doesn't offer instructor-built bundles or multi-course discounts the way some platforms do (verify; this may change). Workable alternatives:

| Idea | How | Notes |
|---|---|---|
| **Series coupon rotation** | Each month, one course in the series gets a custom-price coupon promoted in the other courses' promotional announcements | Stays within monthly announcement caps |
| **"Voice + Test" pairing** | Promote C2 to C3 students who finish Section 9, and C3 to C2 students who finish the tool-calling sections | The most natural pair: both are production-quality courses |
| **Series landing page off Udemy** | A simple page (personal site or GitHub Pages) showing the Build → Test → Operate path, with each course's coupon link | Your own site, your own rules |
| **Udemy Business** | Every course is eligible for Udemy Business if accepted (verify program terms). Series coherence helps companies assign a learning path | Out of your control, but good course quality helps |
| **Consistent pricing** | Same price tier for C2 and C3 | Keeps coupon messaging simple |

## 6. Measurement

| Metric | How |
|---|---|
| Cross-enrollments | A distinct coupon code per placement (bonus lecture C1, bonus lecture C2, promo announcement, YouTube), tracked in the coupon sheet |
| Bonus lecture reach | Lecture views for the bonus lectures (course engagement report) |
| Series overlap | Dashboard student overlap, if Udemy reports it (verify) |

Review these each month and put the money and effort into the path that converts best.
