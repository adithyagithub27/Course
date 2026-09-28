# LinkedIn and X Launch Posts (12)

> Schedule: posts 1-7 pre-launch (W-4 to W-1), 8-10 launch week, 11-12 post-launch. See `launch-plan.md`.
> Rules: no invented numbers. The only market figures allowed come from `00-course-strategy/next-course-market-research.md`, and they must be re-verified before posting. No personal claims without real credentials. Coupons only where current Udemy rules allow (verify). Put links in the first comment on LinkedIn (reach) and in the reply on X.
> Each post has a LinkedIn version (LI) and an X version (X, ≤ 280 chars per post or a short thread).

---

## Post 1: The problem (W-4)

**LI**
```
Your voice agent sounded great in the demo.

Then a real person called it.

- They talked over it. It kept talking.
- They said "Tuesday". It booked Thursday.
- They waited. And waited. Two seconds of silence feels like forever on a phone.

Voice is less forgiving than chat. A caller notices every pause, and a transcription error can turn into a wrong appointment in a real calendar.

I've spent the last few months building a voice agent that holds up on real phone calls. It has tests, latency budgets and a real phone number.

I'll share what I learned over the next few weeks.

#VoiceAI #AIAgents #Python #LiveKit
```
**X**
```
Your voice agent sounded great in the demo. Then a real person called.

They talked over it. It booked Thursday instead of Tuesday. It paused for 2 seconds.

Voice is less forgiving than chat. Over the next few weeks I'm sharing how to build one that holds up on real calls.
```

## Post 2: Meet Riley (W-4, with video #1)

**LI**
```
Meet Riley, an AI receptionist for a (fictional) dental clinic.

Riley:
→ answers questions from the clinic FAQ
→ books, reschedules and cancels appointments
→ reads details back before committing
→ transfers you to a human when you ask
→ runs on a real phone number

It's written in Python with LiveKit Agents, and the first version is about 30 lines.

Full walkthrough on YouTube (link in comments).

#VoiceAI #AIAgents #Python
```
**X**
```
Meet Riley: an AI receptionist for a fictional dental clinic.

Books, reschedules, cancels, reads details back, transfers to a human, and answers a real phone number.

Python + LiveKit Agents. The first version is ~30 lines. Walkthrough below.
```

## Post 3: The latency budget (W-3)

**LI**
```
Why does your voice agent feel slow?

Break the silence after the caller stops talking into parts:

1. Endpointing: deciding they've actually finished
2. STT: the final transcript
3. LLM: time to first token
4. TTS: time to first audio byte
5. Network, in both directions

People answer each other within a fraction of a second in normal conversation, so every stage needs its own budget. Aim for under a second voice-to-voice, and then measure p95, not the average.

I made a free worksheet to set your own budget (link in comments).

#VoiceAI #Latency #AIEngineering
```
**X**
```
Voice agent feels slow? Split the silence into stages:

1 Endpointing
2 STT final
3 LLM time-to-first-token
4 TTS time-to-first-byte
5 Network

Give each stage a budget. Aim for under 1 s voice-to-voice. Measure p95, not the average.

Free worksheet below.
```

## Post 4: Prompting for the ear (W-3)

**LI**
```
Chat prompts break voice agents.

Things that look fine in a chat window and sound awful on a call:
✗ Markdown and bullet lists (TTS reads the asterisks, or just stumbles)
✗ URLs ("h-t-t-p-s colon slash slash...")
✗ Long answers (and every extra sentence adds latency)
✗ "Here are 5 options:"

What works:
✓ 1-2 sentences, one question at a time
✓ Numbers and dates spelled the way a person says them
✓ A read-back before anything irreversible
✓ Saying clearly, early on, that it's an AI

Write for the ear, not the eye.

#VoiceAI #PromptEngineering
```
**X**
```
Chat prompts break voice agents.

✗ markdown, lists, URLs, long answers
✓ 1-2 sentences, one question at a time
✓ dates and numbers written the way people say them
✓ read-back before irreversible actions
✓ say it's an AI

Write for the ear, not the eye.
```

## Post 5: Testing voice agents (W-2, with video #3)

**LI**
```
How do you test a voice agent?

Most voice demos never do. Here's the pyramid I use:

1. Unit tests: pure-Python business logic (scheduler, PII redaction, cost math). No keys, milliseconds per test.
2. Behavior tests: text sessions with LiveKit's test framework. "Did it call book_appointment with the right date?"
3. Evals: LLM-as-judge on transcripts (brevity, read-backs, escalation) plus word error rate for speech-to-text.
4. Simulated callers: LLM personas (confused, impatient, attacker) that call your agent.
5. Production monitoring: p95 latency, cost per minute, transfer rate.

Levels 1-3 run in CI on every push.

#AITesting #VoiceAI #pytest
```
**X**
```
How to test a voice agent:

1 Unit: pure-Python logic, no keys
2 Behavior: text sessions, assert tool calls + args
3 Evals: LLM judge + word error rate
4 Simulated callers: AI personas try to break it
5 Prod monitoring: p95 latency, cost/min

1-3 run in CI.
```

## Post 6: Build vs buy (W-2)

**LI**
```
Should you build a voice agent in code, or use Vapi / Retell / ElevenLabs Agents / Bland?

An honest answer: managed platforms are great for getting live fast.

You'll want code (LiveKit Agents or Pipecat) when you need:
- control over every stage of the pipeline and its latency
- your own test suite in CI
- data-residency or compliance control
- cost visibility per minute, per stage
- no lock-in when a provider changes pricing or models

I compare all of them on control, cost, compliance and lock-in in the course's final technical section.

#VoiceAI #BuildVsBuy
```
**X**
```
Build a voice agent in code, or use Vapi/Retell/ElevenLabs/Bland?

Platforms: fastest to go live.
Code (LiveKit/Pipecat): control over each stage, tests in CI, compliance control, per-stage cost visibility, no lock-in.

Pick based on what you'll need in 6 months.
```

## Post 7: Teaser (W-1)

**LI**
```
Next week I'm launching Course 3 in my Build → Test → Operate series:

"Production Voice AI Agents with Python: Build, Test, Deploy"

→ LiveKit Agents, OpenAI Realtime, Pipecat
→ A real phone number with SIP: inbound, outbound, transfer to a human
→ A full section on testing voice agents
→ Latency, cost per minute, tracing, security
→ Docker + LiveKit Cloud deploy

If you took Course 1 (build) or Course 2 (test), this is the voice sequel. It also stands on its own.

#VoiceAI #AIAgents #Udemy
```
**X**
```
Next week: "Production Voice AI Agents with Python: Build, Test, Deploy"

LiveKit Agents, OpenAI Realtime, Pipecat, Twilio SIP, a full testing section, latency + cost monitoring, Docker deploy.

Course 3 of my Build → Test → Operate series.
```

## Post 8: Launch (D0)

**LI**
```
It's live: "Production Voice AI Agents with Python: Build, Test, Deploy"

You'll build Riley, an AI receptionist that:
✓ answers a real phone number
✓ books, reschedules and cancels with read-backs
✓ hands off to specialist agents and to humans
✓ has behavior tests, LLM-judge evals, WER, latency budgets and simulated callers in CI
✓ reports cost per minute and traces every turn
✓ runs in Docker on LiveKit Cloud

~11.3 hours of video. A full repo. 7 labs, 4 build-it-yourself challenges, 3 projects + a capstone, 12 quizzes.

Who it's for: Python developers who've built a chatbot and now need it to talk, listen and answer the phone.

Link (with launch pricing) in the comments.

#VoiceAI #AIAgents #Python #LiveKit #Udemy
```
**X**
```
It's live: Production Voice AI Agents with Python.

Build an AI receptionist that answers a real phone number. Then test it (tool-call assertions, LLM judges, WER, latency budgets, simulated callers), monitor cost/min and deploy it.

~11.3 h, full repo, labs + capstone. Link below.
```

## Post 9: Why I made it (D0-D1)

**LI**
```
Why a voice agents course, and why now?

When I looked at Udemy, no-code voice-agent courses clearly had an audience. One n8n-based course with voice agents has tens of thousands of students and a 4.8 rating [re-verify the current numbers before posting].

But code-first, production-level voice courses were rare. I found three, and none taught you how to test a voice agent.

That's the gap I wanted to fill. It's the same idea as my testing course, applied to agents that talk.

#VoiceAI #AITesting
```
*(Keep the figures vague or quote them exactly as they appear in the market research, after re-verifying on the listing. Don't round them up.)*

**X**
```
Why a voice agents course?

No-code voice courses clearly have an audience. Code-first production ones are rare, and none I found teaches how to TEST a voice agent.

So I built the one I wanted: build, test, deploy.
```

## Post 10: Demo clip (D4-D6)

**LI**
```
60 seconds: I call Riley, ask to move my appointment, change my mind halfway through, then ask for a human.

Then I run the test that proves it handled the change correctly:

result.expect.next_event().is_function_call(name="reschedule_appointment", ...)

Green. ✓

This is what "production" means to me: it works on the call, and a test proves it keeps working.

(video attached)

#VoiceAI #Testing
```
**X**
```
I call my AI receptionist, change my mind mid-sentence, then ask for a human.

Then the test proves it rescheduled correctly:
is_function_call(name="reschedule_appointment")

✓ green. Video below.
```

## Post 11: Lesson learned (W+1)

**LI**
```
The most common problem so far from students building voice agents isn't the LLM.

It's setup: microphone permissions, API keys in the wrong .env, Python versions.

So Section 2 has a lab that checks all of it before you write a line of agent code, and the unit tests run with zero API keys.

The first hour of a technical course should end with the student talking to something they built. The rest of the course builds on that.

#Teaching #VoiceAI #DeveloperExperience
```
*(Only post this if it's true from your Q&A. Otherwise swap in the real top issue.)*

**X**
```
The most common problem building voice agents so far isn't the LLM. It's setup: mic permissions, keys, Python versions.

So: a setup lab before any agent code, and unit tests that run with zero API keys. The first hour should end with you talking to your own agent.
```

## Post 12: 30-day reflection (W+3)

**LI**
```
One month after launching my voice agents course, here's what I've learned from the Q&A:

1. [Real learning #1 from Q&A, e.g., "Turn-taking tuning is the thing people underestimate most."]
2. [Real learning #2]
3. [Real learning #3]

What I'm adding next: [the actual first update].

If you're building voice agents at work, what's your hardest problem right now: latency, testing, telephony or cost?

#VoiceAI #AIAgents
```
**X**
```
1 month of teaching voice agents. What I've learned from students:

1 [real learning]
2 [real learning]
3 [real learning]

Next update: [real update].

What's your hardest voice-agent problem: latency, testing, telephony or cost?
```
