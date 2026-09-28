# Curriculum Review: Engagement, Value and Assessment Audit

> Reviewer stance: a senior voice-AI engineer who has also taught 10,000+ Udemy students. The goal is to find what a paying student would complain about in a 3-star review, before recording starts.
>
> Reviewed: `curriculum.md` v1.0 (15 sections, 78 lectures). Result: **v1.1 applied** (see Section 4 of this document). New lecture IDs are additive so scripts already in progress stay valid.

---

## 1. Scorecard

| Dimension | v1.0 score | Verdict | What drove the score |
|---|---|---|---|
| Time to first win | 2/5 | Weak | First code the student runs is lecture 3.3, roughly 75 minutes in. Udemy refund and drop-off decisions happen in the first 30 minutes. |
| Demo quality | 3/5 | Mixed | 10 live demos, all "happy path" except 6.4 and 11.5. Students learn voice agents from hearing failures. Almost no "break it, then fix it" moments. |
| Hands-on ratio | 4/5 | Good | 38 of 78 lectures are code-along or demo. Every build section ends in a lab or project. |
| Assignment design | 3/5 | Mixed | 3 projects + capstone is right. But labs are checklists, not challenges. No challenge asks the student to do something before seeing the solution, and nothing lets students make the project *theirs*. |
| Assessment coverage | 2/5 | Weak | Only 6 of 15 sections have a quiz. Sections 3, 4, 5, 8, 10 and 12 (the heaviest technical content) have none. |
| Capstone design | 3/5 | Mixed | 60 minutes of the instructor assembling the agent is passive. Students should build from the brief first and use the walkthrough as the reference solution. |
| Signature differentiator (Section 9) | 4/5 | Strong | The testing pyramid, tool-call assertions, judge, WER and latency budget are exactly what no competitor teaches. Two gaps: no audio-in tests, and LiveKit's built-in Simulation framework is not covered. |
| Real-world transfer | 3/5 | Mixed | Riley is a good running example, but the course never shows the student how to re-skin it for a different business. That is the number one question in Q&A on courses like this. |
| Cost anxiety | 2/5 | Weak | Cost is mentioned in 2.1 and taught in Section 10, but there is no early "spending caps, free tiers, offline mode" lecture. Fear of API bills is a leading reason students stop practising. |
| Global audience | 2/5 | Weak | No multilingual lecture. A large share of Udemy's technical audience is in India, LATAM and Europe, and "does it work in Hindi/Spanish?" will be asked in the first week. |
| Career payoff | 2/5 | Weak | No lecture on roles, interview questions or how to price a voice agent build for a client. Career and freelance outcomes are what students cite in 5-star reviews. |
| Pacing | 3/5 | Mixed | Six lectures are 12-15 minutes. Udemy engagement data favours 5-10 minute lectures. |
| Technical accuracy | 5/5 | Strong | API verified against installed livekit-agents 1.8.3 and pipecat-ai 1.12.0. Deprecated idioms excluded. |

**Overall v1.0: 3.2/5. Solid and accurate, but it teaches like a reference manual in places and would earn "great content, slow start, wish there were more exercises" reviews.**

---

## 2. What students expect from a course like this (and whether v1.0 delivers)

| Expectation | v1.0 | Fix in v1.1 |
|---|---|---|
| "Show me it working in the first 10 minutes" | Demo in 1.1 only | 1.1 rewritten as good call / failed call / fixed call; new 2.6 "Run the finished Riley before you build it" |
| "Let me hear the difference, not just see code" | Rare | A/B audio moments added to 3.9, 4.3 and 6.4 briefs |
| "Make me do it before you show me" | Absent | Four Challenge lectures (4.7, 5.9, 13.1a, 13.7) with pause-then-solution format |
| "Help me adapt this to my business/client" | Absent | 4.7 and 13.7 domain-swap challenges + `business-template.md` resource |
| "Don't let me run up a bill" | Weak | New 2.7 spending caps + offline mock mode |
| "Does it work in my language?" | Absent | New 7.8 multilingual Riley |
| "Will this get me a job or a client?" | Absent | New 15.4 careers, interviews, pricing a project |
| "Test my knowledge as I go" | 6 quizzes | 12 quizzes (one per technical section) |
| "Prove the testing is real, not a toy" | Strong | New 9.13 audio-in tests and 9.14 LiveKit Simulations |

---

## 3. Specific weaknesses found, by section

- **S1.** 38 minutes of talking before any hands-on. Fixed by turning 1.1 into a three-call demo (works, fails, fixed) so the value of the whole course is heard in minute two.
- **S2.** Setup is unavoidable but has no reward at the end. 2.6 gives the student a working phone-quality agent to talk to before writing code. 2.7 removes cost fear and adds an offline mock mode so students can practise for free.
- **S3.** 3.6/3.7 explain turn-taking but never let the student hear the failure modes. 3.9 "Break it" demo: agent talking over the caller, endpointing too short (cuts off), too long (awkward pause), STT on accents, TTS reading markdown symbols aloud.
- **S4.** Prompt rewriting lab is good. Missing: a student-owned artefact. 4.7 challenge: rewrite Riley's prompt for the student's own business and post it to Q&A.
- **S5.** Strong build section. Missing a do-it-yourself moment: 5.9 challenge adds a waitlist tool with a solution reveal.
- **S6.** Good. 6.4 brief now requires side-by-side audio, not just numbers.
- **S7.** Missing multilingual (7.8).
- **S8.** Excellent coverage, no quiz. 8.8 added.
- **S9.** Best section. Added 9.13 (audio-in tests through STT) and 9.14 (LiveKit Simulation framework: scenarios, simulator verdicts, `on_simulation_end`). Both flagged "verify availability" because Simulation is a LiveKit Cloud feature.
- **S10.** No quiz (10.7 added). Otherwise strong: cost per minute is the number hiring managers ask for.
- **S11.** Good. Red-team demo already present.
- **S12.** No quiz (12.9 added) and no chaos moment. 12.8 kills a provider mid-call to show fallbacks working.
- **S13.** Restructured as student-first: 13.1a "Build it yourself first" gate, then the instructor walkthrough is the reference solution. 13.7 domain-swap portfolio project.
- **S14.** Fine as an optional comparison. Marked optional.
- **S15.** 15.4 careers and client pricing added.

Pacing note for recording: split 5.3, 7.5, 8.2, 9.3, 13.2 and 13.5 into Part A / Part B at record time (same script, two uploads). Udemy lets you keep the IDs as "5.3a / 5.3b".

---

## 4. Changes applied in curriculum v1.1

| New ID | Lecture | Type | Min | Why |
|---|---|---|---|---|
| 1.1 (revised brief) | Meet Riley: one call that works, one that fails, one that's fixed | DM | 5 | Hook with contrast |
| 2.6 | Quick win: run the finished Riley before you build it | SC | 6 | First success in Section 2 |
| 2.7 | Spending caps, free tiers and offline mock mode | SC | 6 | Remove cost fear |
| 3.9 | Break it: five ways your first agent fails, and what each sounds like | DM | 7 | Learn from failure |
| 3.10 | Quiz: First agent and turn-taking | QZ | 3 | Coverage |
| 4.7 | Challenge: Riley for your business | AS | 3 | Ownership, portfolio |
| 4.8 | Quiz: Prompting for the ear | QZ | 2 | Coverage |
| 5.9 | Challenge: add a waitlist tool (pause, then solution) | CE | 6 | Do before shown |
| 5.10 | Quiz: Tools | QZ | 2 | Coverage |
| 7.8 | Multilingual Riley: Spanish and Hindi callers | SC | 8 | Global audience |
| 8.8 | Quiz: Telephony | QZ | 2 | Coverage |
| 9.13 | Audio-in tests: real caller audio through the pipeline | SC | 7 | Test what production hears |
| 9.14 | LiveKit Simulations: scenario-based caller testing at scale | DM | 6 | Platform-native evals |
| 10.7 | Quiz: Observability and cost | QZ | 2 | Coverage |
| 12.8 | Chaos demo: kill a provider mid-call | DM | 5 | Prove fallbacks |
| 12.9 | Quiz: Deployment | QZ | 2 | Coverage |
| 13.1a | Build it yourself first: capstone gate | TH | 3 | Active capstone |
| 13.7 | Domain swap: ship Riley for a restaurant, salon or law office | AS | 4 | Portfolio + transfer |
| 15.4 | Careers: voice AI roles, interview questions, pricing a client project | TH | 8 | Career payoff |

Net effect: 97 lectures, ≈12.2 h including quizzes (≈11.3 h video). 12 quizzes, 7 labs, 3 projects + capstone, 4 challenges, 5 coding exercises. New resources: `troubleshooting.md`, `business-template.md`, `voice-agent-readiness-scorecard.md`, `interview-questions.md`.

---

## 5. Engagement mechanics to bake into production (not lecture content)

1. **Section-end "You can now..." card.** Ten-second slide at the end of each section listing three concrete abilities. Students screenshot these.
2. **Build log.** Ask students to keep a `BUILD_LOG.md` in their repo and post one line per section in Q&A. Creates accountability and gives you review-worthy engagement.
3. **Hear-it moments.** Every time a setting changes turn-taking or voice, play before and after audio. Voice courses live or die on this.
4. **Failure-first demos.** Start build sections with the broken version for 30 seconds.
5. **Q&A seeding.** Post the five most likely questions per section yourself on launch day with answers. Udemy ranks courses with active Q&A higher.
6. **Announce version pins.** Voice frameworks change monthly. Put "verified on livekit-agents 1.8 / pipecat-ai 1.12" on the first slide of every code lecture and keep a pinned Q&A thread for breaking changes. This single habit prevents most 1-star reviews on fast-moving topics.

---

## 6. Remaining risks the owner should decide on

- **Telephony cost and friction.** Twilio trials and number verification differ by country. Provide a "no phone number" path through every telephony lab (LiveKit SIP test or web-only) so students outside the US are not blocked.
- **Provider drift.** Model names (`gpt-4.1-mini`, `nova-3`, `sonic-3`) will change during the course's life. All names live in `src/maple/config.py` and env vars so a one-line repo update fixes every lecture. Budget a quarterly refresh.
- **LiveKit Simulations availability.** Verify it is enabled on the free tier before recording 9.14, otherwise record it as a demo-only lecture.
