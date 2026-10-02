# Section 15: Wrap-up and Next Steps

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈17 min (4 lectures, curriculum v1.1; 15.3 is 4:00)
> **Upload order (important):** 15.1 → 15.2 → 15.4 → 15.3. Udemy requires the bonus lecture to be the **last** lecture in the course, so the careers lecture (15.4) is uploaded *before* the Bonus Lecture (15.3) even though its ID is higher. The lectures below appear in upload order.
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with the agent. Record the real audio. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only (narration plus scripted demo dialogue), not cues or code.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 15.1 | What you built and where to go next | TH | 5:00 | ~580 |
| 15.2 | Final practice test | QZ | 0 min in curriculum (1:00 video intro) | ~100 |
| 15.4 | Careers: voice AI roles, interview questions, pricing a client project | TH | 8:00 | ~970 |
| 15.3 | Bonus lecture: keep building | TH | 4:00 | ~520 |

---

## Lecture 15.1 — What you built and where to go next

| Field | Value |
|---|---|
| ID | 15.1 |
| Type | TH (talking head / avatar with slides) |
| Target duration | 5:00 (~580 spoken words) |
| Learning objectives | 1. Summarise the full Riley stack, from pipeline to phone number to tests to production. 2. Pick one concrete next project: multilingual agents, avatars, outbound campaigns or a new domain. 3. Place this course on the Build, Test, Operate path. |
| Prerequisites | Sections 1 to 14 (the capstone is recommended but not required) |
| Files used | `agents/s13_capstone_receptionist.py` (recording of the final call), `03-code/README.md` |

### Script

[B-ROLL: Fast montage, two seconds each: the first `console` session from Section 3, the booking tool log from Section 5, the phone ringing in Section 8, a wall of green tests from Section 9, a Langfuse trace from Section 10, the red-team test going green in Section 11, `lk agent deploy` finishing in Section 12, the capstone call in Section 13.]

[AVATAR]
Think back to Section 3. Riley was thirty lines of Python that could say hello through your laptop mic.

[PAUSE]

Now Riley answers a real phone number. It books, reschedules and cancels appointments against a real calendar. It answers questions from the clinic's FAQ. It verifies callers before touching their data. It hands off to a human when it should. And every change you make runs through a test suite before it reaches a caller.

That's not a demo anymore. That's a production system. You built it.

[SLIDE 1: What you built]
- A cascaded voice pipeline: STT, LLM, TTS, VAD, turn detection
- A speech-to-speech version on OpenAI Realtime
- Tools with read-backs, filler speech and confirmation gates
- Knowledge lookup and multi-agent handoffs
- A phone number: inbound, outbound and transfer to a human

Let's name it properly, because you'll want these words for your portfolio and your next interview.

You built a cascaded voice pipeline, and you tuned turn-taking by ear and by numbers. You built a speech-to-speech version and measured it against the cascade. You gave Riley tools, with read-backs and filler speech. You added knowledge and specialist agents. And you put it all on a phone number.

[SLIDE 2: How you know it works]
- The voice testing pyramid: unit, behavior, evals, simulated calls
- WER for STT, latency budgets, LLM judges
- Metrics, traces and cost per minute
- Guardrails, red-team tests and PII redaction
- Docker, LiveKit Cloud and a production checklist

And here's the part most voice tutorials skip. You know it works. You have unit tests for the business logic. Behavior tests for tool calls. LLM judges for conversation quality. Word error rate for the speech-to-text. Latency budgets that fail the build. Simulated callers that attack your agent. And in production, you have traces and a cost per minute you can defend in a meeting.

[SLIDE 3: Where to go next]
- Multilingual: language detection, per-language voices, WER per language
- Avatars: a face for Riley on the web front end
- Outbound campaigns: reminders at scale, with consent and do-not-call
- New domains: restaurants, property management, IT help desk

So what next? Here are four directions, and each one reuses almost everything you built.

Multilingual agents. Many STT and TTS providers support multiple languages, and LiveKit lets you switch models per agent. The hard part isn't the code. It's testing. Build a WER reference set per language, and run your behavior tests in each one.

[B-ROLL: the 12.5 web front end with an avatar video tile next to the live captions.]

Avatars. LiveKit Agents supports video avatar providers, so Riley can have a face on the web front end. Same session, same tools, one more output. Measure latency again, because video adds some. And re-run your cost numbers, because video minutes are priced differently.

Outbound campaigns. You built one reminder call in Section 8. Scaling that to thousands is mostly about compliance, retries and answering-machine handling, not about the agent. Revisit Lecture 8.6 before you dial anyone.

[B-ROLL: the three domain-swap briefs from Lecture 13.7 flip past: a restaurant, a property-maintenance line, an IT help desk.]

And new domains. Swap the scheduler and the FAQ, keep the architecture. A restaurant booking line. A property maintenance line. An internal IT help desk. The testing pyramid transfers directly. You've already practised this in the domain-swap assignment, Lecture 13.7.

Whichever you pick, start the same way you started Riley. Business logic first, in pure Python, with unit tests. Then the agent. Then the tests that prove it works. Then the numbers.

[SLIDE 4: The Build, Test, Operate path]
- Build: *Generative AI & AI Agents: Zero to Production*
- Test: *AI Agent Testing & Evaluation*
- Operate in real time: this course
- All three stand alone; together they cover the full lifecycle

[AVATAR]
This course is one part of a path I think of as Build, Test, Operate. Building agents from scratch. Testing and evaluating them properly. And running them in real time, with a voice and a phone number, which is what you just did.

You didn't need the other two to take this one. But if a part of this course felt thin for you, maybe the eval theory or the agent foundations, that's where the deeper material lives. I'll say more in the bonus lecture at the very end.

[SLIDE 5: Your next 7 days]
1. Finish the capstone and push it to GitHub
2. Record a two-minute demo call
3. Change one thing (domain, language or voice) and re-run the full test suite

Here's my challenge for your next seven days. Finish the capstone and push it to GitHub. Record a two-minute demo call. Then change one thing, a new domain, a new language or a new voice, and run the full test suite again. If the tests catch something, even better. That's the whole point.

[PAUSE]

Thank you for building this with me. Riley's on the line. Go put your own agent on one.

[SLIDE 6: Recap]
- A production voice agent, built and tested
- Proof: tests, traces and cost per minute
- Next: multilingual, avatars, outbound or a new domain

**Recap:** You built, tested, secured and deployed a production voice agent, and the same architecture carries you into multilingual, avatar, outbound and new-domain projects.

**Transition:** Next, test yourself with the forty-question final practice test.

### Speaker notes: common student mistakes / Q&A

- "Which next step is most in demand?" Outbound and after-hours inbound for small businesses come up most in Q&A. Point students to Lecture 8.6 first, because compliance is the blocker, not the code.
- "Can I use Riley's code commercially?" Point to the repo licence in `03-code/README.md`. Remind them that Maple Street Dental and all phone numbers are fictional.
- "Do avatars work over the phone?" No. Avatars are video, so they need the web or app front end from Lecture 12.5.
- Encourage students to post their capstone demo in the Q&A. It helps others and gives you material for course updates.

---

## Lecture 15.2 — Final practice test

| Field | Value |
|---|---|
| ID | 15.2 |
| Type | QZ (40-question practice test with short video intro) |
| Target duration | 0 min in the curriculum runtime (1:00 video intro, ~100 spoken words; students take the test at their own pace) |
| Learning objectives | 1. Check end-to-end understanding across all fifteen sections. 2. Identify the two or three sections to revisit before starting a real project. |
| Prerequisites | Sections 1 to 14 |
| Files used | `06-assessments/practice-test.md` |

### Script

[AVATAR]
Which section would you struggle to explain to an interviewer tomorrow? This test will tell you. Last checkpoint: forty questions, covering the whole course.

[SLIDE 1: Final practice test]
- 40 questions across all 15 sections
- Architecture, prompting, tools, telephony, testing, observability, security, deployment
- Read every explanation, even for answers you got right

The questions follow the order of the course. Architecture and latency first. Then prompting, tools, telephony, testing, observability, security and deployment.

Take it in one sitting if you can. It takes most students thirty to forty minutes.

When you finish, don't just look at the score. Look at *where* you missed questions. If three of them come from the same section, that's the section to rewatch before your next project.

[PAUSE]

Good luck. You're ready for this.

**Recap:** The practice test checks the full course and points you to the sections worth revisiting.

**Transition:** Next, we'll turn these skills into a career: roles, interview questions, and how to scope and price a client project.

### Speaker notes: common student mistakes / Q&A

- Most missed topic in beta: which latency numbers belong in the voice-to-voice budget. Point to Lectures 1.4 and 9.8.
- Second most missed: where permissions belong (tool code, not the prompt). Point to Lecture 11.2.
- "Can I retake it?" Yes. Udemy practice tests can be retaken, and the explanations stay available.

---

## Lecture 15.4 — Careers: voice AI roles, interview questions, pricing a client project

| Field | Value |
|---|---|
| ID | 15.4 (uploaded before 15.3 so the Bonus Lecture stays last) |
| Type | TH (talking head / avatar with slides) |
| Target duration | 8:00 (~970 spoken words) |
| Learning objectives | 1. Name the job titles that hire for voice agent skills and what each one emphasises. 2. Answer twelve common voice AI interview questions with concise, evidence-backed answers. 3. Scope and structure the price of a freelance voice agent project: discovery, setup fee, retainer and pass-through usage. |
| Prerequisites | Section 13 capstone (recommended) |
| Files used | `10-resources/interview-questions.md`, `src/maple/costs.py`, `05-projects/capstone-riley.md` |

> **Production note:** No salary or rate figures in this lecture, on slides or in the resources. Markets differ by country and change quickly. Keep pricing guidance structural.

### Script

[AVATAR]
You can now build, test and deploy a production voice agent. That's a rare combination. In this lecture, let's turn it into work. Three parts. Who hires for this. What they'll ask you in an interview. And, if you freelance, how to scope and price a voice agent project without losing your shirt.

[SLIDE 1: Roles that hire for this]
- Voice AI engineer: real-time pipelines, latency, telephony
- Conversational AI engineer: dialogue design, prompts, evaluation
- AI solutions engineer: customer-facing builds, integrations, demos
- Also: applied AI engineer, AI product engineer, forward-deployed engineer

Job titles are messy in this field, so search for several. "Voice AI engineer" roles focus on the real-time pipeline: latency, turn-taking, telephony. "Conversational AI engineer" roles lean toward dialogue design, prompting and evaluation. "AI solutions engineer" roles are customer-facing. You build integrations and demos for clients. And many "applied AI" or "forward-deployed" roles include voice work without saying so in the title.

Read the job description, not the title. Look for words like real-time, WebRTC, SIP, latency, speech-to-text and evaluation.

[SLIDE 2: Your evidence]
- The capstone repo with a clear README
- A two-minute demo call recording
- Your latency report and cost per minute
- The domain-swap project from Lecture 13.7

Whatever the title, your evidence is the same. Your capstone repo. A short demo call. Your latency and cost numbers. And the domain-swap project, which proves you can do it twice. Numbers beat adjectives. "p95 voice-to-voice under one second" is a stronger line than "low-latency."

[SLIDE 3: Interview questions 1-4: architecture]
1. Cascaded vs speech-to-speech: when would you pick each?
2. Where does latency come from in a voice pipeline?
3. What's the difference between VAD and turn detection?
4. How do you handle interruptions?

Now, interviews. Here are twelve questions I'd expect, with short model answers. Longer versions are in `interview-questions.md`.

One. Cascaded versus speech-to-speech. Model answer: "Cascaded gives me control: I can pick each provider, inspect text, and guard output. Speech-to-speech can feel more natural and responsive, but I have less control and it can cost more per minute. I measured both on the same five calls and chose with data."

Two. Where does latency come from? "Endpointing, STT finalisation, LLM time to first token, TTS time to first byte, and network. I measure each stage at p50 and p95 and tune the biggest one first, usually endpointing or the LLM."

[B-ROLL: the Section 9 latency waterfall with its segments labelled: endpointing, STT final, LLM time to first token, TTS time to first byte, network, matching answer two.]

Three. VAD versus turn detection. "VAD detects speech versus silence. Turn detection decides whether the caller has actually finished their thought. A pause isn't always the end of a turn."

Four. Interruptions. "Set a minimum interruption duration so coughs don't cut the agent off, resume after false interruptions, and make sure only the spoken part of an interrupted reply goes into history."

[SLIDE 4: Interview questions 5-8: tools, telephony, testing]
5. How do you make tool calls safe?
6. How does a phone call reach your agent?
7. How do you test a voice agent?
8. How do you test speech recognition quality?

Five. Safe tool calls. "Read back before committing, disallow interruptions during the commit, enforce permissions in tool code rather than the prompt, and return speakable errors."

Six. Phone calls. "The carrier routes the number to a SIP trunk, the trunk sends it to LiveKit SIP, a dispatch rule creates a room and dispatches the named agent. Transfers use SIP REFER through the framework."

Seven. Testing. "A pyramid. Unit tests for business logic, behavior tests on text sessions with tool-call assertions, LLM judges for quality, WER for STT, latency budgets, simulated callers, and production monitoring. The cheap layers run on every commit."

Eight. STT quality. "Word error rate against reference transcripts, with a focus on domain terms like names and drug names, and keyterm boosting where the provider supports it."

[SLIDE 5: Interview questions 9-12: production]
9. What does it cost per minute, and where does the money go?
10. How do you protect personal data?
11. What happens when a provider goes down mid-call?
12. How do you deploy without dropping calls?

Nine. Cost. "I compute cost per minute from usage metrics times a price table. For my build, I can tell you which component is largest and what I'd change to reduce it." Then give your actual breakdown.

Ten. Personal data. "Verify identity before revealing anything, redact at the edge before logging or tracing, keep third-party telemetry PII-free by default, and apply a short retention policy."

[B-ROLL: the 12.8 chaos demo clip: the log line "switching to next LLM" scrolls past while the call carries on.]

Eleven. Provider outage. "Fallback providers for STT, LLM and TTS, explicit timeouts, a pre-written error line, then a transfer to a human or a clean goodbye. I've tested it by killing a provider mid-call." That's Lecture 12.8.

Twelve. Deploys. "Each call runs in its own process, the server drains on SIGTERM, and the platform's grace period is at least the drain timeout. Rollbacks are one command."

Notice the pattern. Every good answer names a mechanism and some evidence. That's what interviewers are listening for.

[SLIDE 6: Freelance: scoping a voice agent project]
1. Discovery: call volume, call types, systems to integrate, compliance needs
2. A written scope: which call types, which integrations, what "done" means
3. Acceptance tests agreed up front (your Section 9 suite)
4. A pilot: limited hours or one location, then expand

If you freelance, here's how to scope. Start with a paid discovery. Ask about call volume, the top five call types, which systems you must integrate with, like their scheduling software, and any compliance requirements. Integrations are where projects blow up, so find them early.

Then write the scope down. Which call types Riley handles. Which ones it transfers. And what "done" means, as acceptance tests. Your Section 9 suite is perfect for this. "These twenty scenarios pass" is a definition of done that nobody can argue with later.

And propose a pilot. After-hours calls only, or one location. Measure containment and caller satisfaction. Then expand.

[SLIDE 7: Freelance: structuring the price]
- Discovery fee (fixed)
- Setup / build fee (fixed, based on scope and integrations)
- Monthly retainer (monitoring, prompt updates, test maintenance)
- Usage passed through: cost per minute × minutes, plus an agreed margin

Now pricing. I won't give you numbers, because markets differ a lot. But here's a structure that protects you. A fixed discovery fee. A fixed setup fee for the build, based on the scope and the number of integrations. A monthly retainer for monitoring, prompt updates and keeping the tests green. And usage passed through, based on cost per minute from `costs.py`, times minutes, plus an agreed margin.

Why separate usage? Because it scales with the client's call volume, not your effort. If a clinic doubles its calls, your costs double. Passing usage through keeps you from quietly losing money on your best clients.

[SLIDE 8: Put these in writing]
- What's out of scope (and what counts as a change request)
- Who owns provider accounts and API keys
- Response times for fixes, and what counts as urgent
- Who owns compliance review

Two more things belong in every proposal. First, what's out of scope. "Adding a new call type" is a change request, not a bug. Second, who owns the accounts. The cleanest setup is that the client owns the LiveKit, model and phone accounts, and you get access. If you part ways, their receptionist keeps working.

And agree on response times up front. A voice agent that answers the phone is a live system. If it breaks at nine A M on a Monday, the client will call you. Decide together what counts as urgent, and put it in the retainer.

[AVATAR]
Last tip. Whether it's a job interview or a client pitch, lead with a call. Play your two-minute demo. Then show the test suite and the numbers. Most candidates only have the first part. You have all three.

[SLIDE 9: Recap]
- Search for skills, not titles
- Answer with a mechanism plus evidence
- Price as discovery, setup, retainer, pass-through usage

**Recap:** Target voice, conversational and solutions engineering roles, answer interview questions with a mechanism plus evidence, and price client work as discovery, setup, retainer and pass-through usage.

**Transition:** One more short video to finish the course: the bonus lecture.

### Speaker notes: common student mistakes / Q&A

- "What should I charge?" Don't give numbers in Q&A. Point to the structure, and suggest they research local rates and price the setup fee from an hours estimate that includes integrations and testing.
- Mistake: quoting a fixed monthly price that includes unlimited usage. Always separate usage from the retainer.
- Mistake: portfolio READMEs with no numbers. Add latency percentiles, WER on your reference set, test counts and cost per minute.
- Healthcare, legal and financial clients need compliance review before launch. Say so in the proposal and keep it out of your scope unless you're qualified.

---

## Lecture 15.3 — Bonus lecture: keep building

| Field | Value |
|---|---|
| ID | 15.3 |
| Type | TH (talking head / avatar) |
| Target duration | 4:00 (~520 spoken words) |
| Learning objectives | 1. Know where to get help and updates after the course: the Q&A, the repo README and announcements. 2. Know which of the instructor's other courses cover related topics, and who each one is for. |
| Prerequisites | None |
| Files used | `pyproject.toml` and `uv.lock` (shown briefly). Links go in the lecture's resources panel. |

> **Udemy bonus-lecture rules (production notes, check the current Udemy Instructor Help Center before publishing):**
> - This must be the **last** lecture in the course, and its title should begin with "Bonus Lecture".
> - Promotion of other courses belongs **only** here, not in any other lecture, welcome message or quiz.
> - Keep it informative and low-pressure: say who each course is for, don't pressure or use countdown language.
> - Only link to the instructor's own Udemy courses (use Udemy's course links or instructor coupon links). No links to off-platform course sales.
> - No personal contact details for off-platform paid services, and no requests for reviews in exchange for anything.

### Script

[AVATAR]
Six months from now, a library upgrade will break something in your agent. Will you find out from a test, or from a caller? This short bonus lecture covers how to keep your Riley project current, how to get help, and, if you want to go deeper, which of my other courses fit with this one. That last part is completely optional.

[SLIDE 1: Keeping your project current]
- Voice AI libraries release often
- The repo README lists the tested versions
- Course announcements flag breaking changes
- Pin your versions in production

First, updates. Voice AI moves fast. LiveKit Agents and Pipecat release often, and model names change. Every script in this course was checked against livekit-agents 1.8 and pipecat-ai 1.12. You've already seen what that looks like in practice. In Section 14, Pipecat had renamed two core classes, and the old names still worked with a warning. Most changes arrive like that: a deprecation warning first, a removal later. Read your warnings.

When something changes, I update the repo README first, with the tested versions and any code changes. Big changes also go out as a course announcement.

[SCREEN: `03-code/pyproject.toml`, the `livekit-agents[...]~=1.8` line; the file tree shows `uv.lock` beside it. Terminal: `uv lock --check` prints `Resolved 154 packages`.]

And for your own production agent, pin your versions, like the repo does with `pyproject.toml` and the committed `uv.lock`. Upgrade on purpose, with your test suite running. That's exactly what the tests are for.

Here's an upgrade routine that works. Once a month, read the changelogs for your framework and your providers. Upgrade on a branch. Run the whole pyramid, including the safety suite and a latency report. If the numbers hold, deploy, and keep the rollback ready. Twenty minutes a month keeps you off the "it broke on Friday" list.

[SLIDE 2: Getting help]
- Q&A: include your command, the full error and your versions
- Search the Q&A first: most setup issues are answered there
- Share your capstone demo: it helps other students

Second, help. The Q&A stays open. When you post, include three things: the exact command you ran, the full error message, and your package versions. That turns a two-day back-and-forth into a one-reply fix.

And please share your capstone demo in the Q&A. Other students learn a lot from seeing different domains and voices, and so do I. Some of the best improvements to this course came from student questions, so if something was confusing, say so. That feedback shapes the next update.

[SLIDE 3: Related courses (optional)]
- *Generative AI & AI Agents: Zero to Production*: build text agents from first principles
- *AI Agent Testing & Evaluation*: go deep on evals, judges and test strategy
- Links are in the resources panel for this lecture

Third, and only if it's useful to you: this course is part of a set.

*Generative AI & AI Agents: Zero to Production* is the building course. It's for you if the LLM and agent parts of this course felt fast. It covers prompting, tools, retrieval and agent design for text agents, from first principles.

*AI Agent Testing & Evaluation* is the testing course. It's for you if Section 9 was your favorite, or if you're the person on your team who owns quality. It goes much deeper on evaluation design, LLM judges, datasets and test strategy than we had room for here.

You don't need either one to use what you've learned here. The links are in the resources panel for this lecture if you want to take a look.

[SLIDE 4: Thank you]
- Finish the capstone
- Share your demo
- Keep your tests green

[AVATAR]
That's it. Thank you for taking this course, and for sticking with it all the way to a production agent. Finish the capstone. Share your demo. Keep your tests green.

I'll see you in the Q&A.

[SLIDE 5: Recap]
- Pin versions; upgrade on a branch with tests
- Ask in the Q&A with command, error, versions
- Related courses are optional next steps

**Recap:** Keep your project current through the repo README, get help in the Q&A, and, optionally, go deeper with the Build and Test courses.

[SLIDE 6: You can now]
- Build a voice agent from pipeline to phone number
- Test it across the full voice testing pyramid
- Deploy, observe and price it in production

**Transition:** This is the final lecture of the course. Thank you for learning with me.

### Speaker notes: common student mistakes / Q&A

- Keep this lecture free of discount countdowns, "limited time" language or repeated calls to action. Mention each course once, with who it's for.
- Put course links only in this lecture's resources panel. Use Udemy course URLs or official instructor coupon links, never off-platform checkout pages.
- If a student asks for a discount in the Q&A, share the current instructor coupon in the reply rather than adding promotion to other lectures.
- Review this lecture whenever Udemy updates its promotional guidelines, and before every major course update.
