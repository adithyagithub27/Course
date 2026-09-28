# Promo Video Script

**Course:** Production Voice AI Agents with Python: Build, Test, Deploy
**Target length:** 105 seconds (hard range 90-120 s)
**Placement:** Udemy course landing page promo video
**Format:** Instructor to camera (real camera preferred, see note) + live phone-call demo + screencast + diagrams, in the design system in `10-graphics/design-system.md`

---

## Udemy promo video guidelines applied (verify current guidelines in the Teaching Center)

| Guideline (as understood) | How this script meets it |
|---|---|
| Instructor appears on camera early and introduces themselves | Shot 2 (0:08) is the instructor to camera, with name and lower third |
| Show what students will actually build and learn | Live phone call to Riley, real code, real test output, real dashboards |
| Keep it short (roughly 2 minutes or less) | 105 s |
| No external links, URLs, social handles, email addresses or phone numbers students could call | No URLs on screen. The phone number is always blurred. The repo is called "the course repo", with no GitHub URL |
| No coupons, prices or "limited time" claims | None |
| Clear audio, HD video (at least 720p; we export 1080p) | See `09-production/recording-guide.md` |
| Promo content should reflect the actual course | Every clip comes from a real lecture (listed in the shot list) |

**Avatar note:** most lectures are HeyGen avatar-narrated. For the promo, **film the instructor on a real camera for Shots 2 and 9 if at all possible.** A real face builds trust on a landing page, and Udemy's rules on AI-generated presenters and disclosure may apply (verify Udemy's current AI content policy, and see `publish-checklist.md` §9). If you use the avatar, add the on-screen disclosure noted in Shot 2.

---

## Shot list and script

| # | Time | Shot / visual | On-screen text | Voiceover (VO) / dialogue |
|---|---|---|---|---|
| 1 | 0:00-0:08 | **Cold open, live call.** Phone on the desk, speakerphone. Waveform animates on screen. Caller: "Hi, can I move my cleaning to Thursday?" Riley replies. Number and caller ID blurred. | `Live call • AI receptionist` | **Riley (agent audio):** "Sure. I can move your cleaning from Tuesday the fourteenth to Thursday the sixteenth at 2 PM. Should I go ahead?" |
| 2 | 0:08-0:18 | **Instructor to camera**, mid shot. Lower third: name + one-line credential placeholder. | `[Instructor Name]` / `[one-line credential from instructor-bio.md]` (if avatar: `Presented by an AI avatar of [Instructor Name]`) | "That's not a demo recording. That's Riley, a voice agent you'll build in Python, answering a real phone number. I'm [Instructor Name], and in this course you'll build, test and deploy it." |
| 3 | 0:18-0:30 | **The problem.** Quick red-tinted cuts (design system K1 hook): agent talking over the caller; a timeline showing a 2.4 s gap; a transcript with "Tuesday" misheard as "Thursday". | `Talks over callers` → `2+ second silences` → `Books the wrong day` | "Most voice agents look great in a demo and fall apart on real calls. They talk over people, pause for two seconds and mishear dates. And nobody catches it, because nobody tests them." |
| 4 | 0:30-0:45 | **Build.** Screencast of `agents/s03_hello_agent.py` (15 lines visible), then the voice pipeline diagram animating: mic → VAD → STT → turn detection → LLM → TTS → speaker. | `LiveKit Agents • Python` `STT → LLM → TTS` | "You'll start with a working agent in about thirty lines of Python using LiveKit Agents. Then you'll learn how the pieces fit: speech-to-text, turn detection, the LLM and text-to-speech, and how to keep the whole round trip under a second." |
| 5 | 0:45-0:58 | **Make it useful.** Split screen: `@function_tool book_appointment` code / scheduler calendar filling a slot; then the Greeter → Booking → Billing handoff diagram; then the OpenAI Realtime version. | `Tools • Handoffs • OpenAI Realtime` | "You'll give Riley tools to book, reschedule and cancel, teach it to read details back before it commits, add a knowledge base and specialist agents, and rebuild it on OpenAI's speech-to-speech model to compare." |
| 6 | 0:58-1:08 | **Make it real.** SIP call-flow diagram (phone → Twilio SIP trunk → LiveKit SIP → room → Riley), then a clip of a warm transfer to a human. | `Real phone number • Inbound • Outbound • Transfer` | "Then you'll put it on a real phone number with SIP, with inbound calls, outbound reminders and transfer to a human." |
| 7 | 1:08-1:25 | **Signature section: testing.** Terminal: `pytest tests/agent` goes green; a test asserting `is_function_call(name="book_appointment")`; the WER report; the latency report with p95 against the budget line; the simulated caller persona "impatient caller". | `Behavior tests • LLM judges • WER • Latency budgets • Simulated callers` | "This is where the course is different. You'll test Riley like software: tool-call assertions, LLM-as-judge evals, speech-recognition accuracy, latency budgets, and simulated callers that try to break it, all running in CI." |
| 8 | 1:25-1:37 | **Operate and ship.** Langfuse trace waterfall of one turn; cost-per-minute panel; `docker build` → LiveKit Cloud deploy log. | `Traces • Cost per minute • Docker • LiveKit Cloud` | "You'll trace every turn, know your cost per minute, lock down prompt injection and PII, and deploy with Docker to LiveKit Cloud." |
| 9 | 1:37-1:47 | **Instructor to camera**, close. Course title card fades in behind (K2 style). | `Production Voice AI Agents with Python` `Build • Test • Deploy` | "If you can build a chatbot, you can build this. Enroll, and within the first hour you'll be talking to Riley yourself." |

**Total: ~107 s on the shot clock.** VO word count is 258 words (counted from the captions below), which is about 111 s at the PRODUCTION-GUIDE rate of ~140 wpm. That fits the 90-120 s window. If the cut runs over 120 s, trim Shot 5 first.

---

## Captions (SRT-ready text)

Upload corrected captions for the promo. Don't rely on auto-captions for product names.

```text
1  00:00:00,500 --> 00:00:07,500  Sure. I can move your cleaning from Tuesday the fourteenth to Thursday the sixteenth at 2 PM. Should I go ahead?
2  00:00:08,000 --> 00:00:18,000  That's not a demo recording. That's Riley, a voice agent you'll build in Python, answering a real phone number. I'm [Instructor Name], and in this course you'll build, test and deploy it.
3  00:00:18,000 --> 00:00:30,000  Most voice agents look great in a demo and fall apart on real calls. They talk over people, pause for two seconds and mishear dates. And nobody catches it, because nobody tests them.
4  00:00:30,000 --> 00:00:45,000  You'll start with a working agent in about thirty lines of Python using LiveKit Agents. Then you'll learn how the pieces fit: speech-to-text, turn detection, the LLM and text-to-speech, and how to keep the whole round trip under a second.
5  00:00:45,000 --> 00:00:58,000  You'll give Riley tools to book, reschedule and cancel, teach it to read details back before it commits, add a knowledge base and specialist agents, and rebuild it on OpenAI's speech-to-speech model to compare.
6  00:00:58,000 --> 00:01:08,000  Then you'll put it on a real phone number with SIP, with inbound calls, outbound reminders and transfer to a human.
7  00:01:08,000 --> 00:01:25,000  This is where the course is different. You'll test Riley like software: tool-call assertions, LLM-as-judge evals, speech-recognition accuracy, latency budgets, and simulated callers that try to break it, all running in CI.
8  00:01:25,000 --> 00:01:37,000  You'll trace every turn, know your cost per minute, lock down prompt injection and PII, and deploy with Docker to LiveKit Cloud.
9  00:01:37,000 --> 00:01:47,000  If you can build a chatbot, you can build this. Enroll, and within the first hour you'll be talking to Riley yourself.
```

Split lines longer than ~42 characters into two caption lines in the SRT editor. Keep each caption on screen for at least 1 second.

---

## Production notes

- **Shot 1 must be real.** Record an actual call to the deployed capstone (lecture 13.5 setup). Follow the safe-recording steps in `09-production/recording-guide.md` §6: a dedicated recording number, caller ID blurred, no keys on screen.
- **Audio:** mix VO at -16 LUFS integrated; music bed at about -24 LUFS; duck the music under Riley's call audio. Phone audio is 8 kHz and will sound thinner, which is authentic. Don't "enhance" it into something the course won't deliver.
- **Visual change every 5-8 s.** No static frame longer than 8 s.
- **Design system:** Deep Navy `#0A1628` backgrounds, Electric Teal `#00D4AA` accents, Alert Red `#FF4B4B` only in Shot 3 (failures), Inter and JetBrains Mono.
- **Code on screen:** only APIs from curriculum §6 (verified on livekit-agents 1.8). Show the corner note "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12".
- **No claims** of "best", "only" or "#1", no student counts, no salary claims.
- **Export:** 1920×1080, H.264, 30 fps, AAC 48 kHz.
