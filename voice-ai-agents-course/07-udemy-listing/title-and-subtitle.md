# Title and Subtitle Options

> Course 3 of the Build → Test → Operate series. Udemy limits (verify in the course landing page editor): **title ≤ 60 characters, subtitle ≤ 120 characters**. Every count below comes from `len()` in the Python script at the bottom of this file, so it matches what Udemy's counter shows (spaces and punctuation included).

## Recommended pair

- **Title (59 chars):** Production Voice AI Agents with Python: Build, Test, Deploy
- **Subtitle (120 chars):** Build an AI phone receptionist with LiveKit, OpenAI Realtime & Twilio SIP. Test it, track latency & cost, and deploy it.

**Why this pair:**

- It matches the curriculum's working title and the series naming (Build, Test, Deploy), so it reads like one family with Course 1 and Course 2.
- The market research says to put "Production" and "Deploy" in the title and to avoid "Complete", "Masterclass", "Bootcamp" and "A-Z". This title does both.
- The subtitle carries the tool keywords (LiveKit Agents, OpenAI Realtime, Twilio SIP), a concrete outcome (an AI phone receptionist) and the angle none of the code-first competitors in the market research teaches: testing, plus latency and cost monitoring.
- Title Option 7 puts "LiveKit" in the title. Switch to it only if Udemy Marketplace Insights shows strong "LiveKit" search demand. The research lists that as a validation step still to do.

## Title options (limit 60)

| # | Title | Chars | ≤60? | Notes |
|---|---|---|---|---|
| 1 (rec.) | Production Voice AI Agents with Python: Build, Test, Deploy | 59 | yes | Matches the series brand (Build → Test → Operate). Leads with 'Production' and 'Deploy', as the market research recommends. The framework names go in the subtitle. |
| 2 | Voice AI Agents with Python: LiveKit, OpenAI Realtime & SIP | 59 | yes | Framework-first. Catches LiveKit and OpenAI Realtime searches but drops the 'test' differentiator. |
| 3 | Build Voice AI Agents in Python: LiveKit, Pipecat & Twilio | 58 | yes | Names both open-source frameworks and the telephony provider. Strong on tool-name search. |
| 4 | Production Voice AI Agents: LiveKit, Testing & Telephony | 56 | yes | Puts the unique angle (testing) in the title. Drops 'Python'. |
| 5 | AI Voice Agents with Python: Build, Test & Deploy to Phones | 59 | yes | Uses the 'AI voice agents' word order, which some learners type. Adds the phone outcome. |
| 6 | Voice AI Agent Engineering: Build, Test & Deploy in Python | 58 | yes | Pitched at engineers. 'Engineering' signals depth, but the phrase gets less search. |
| 7 | LiveKit Voice AI Agents: Build, Test & Deploy with Python | 57 | yes | Best if LiveKit search volume turns out high in Marketplace Insights. Risk: depends on one vendor's name. |
| 8 | Real-Time Voice AI Agents in Python: Phone-Ready and Tested | 59 | yes | Outcome-led ('phone-ready and tested'). Weaker on the tool keywords. |

## Subtitle options (limit 120)

| # | Subtitle | Chars | ≤120? |
|---|---|---|---|
| 1 (rec.) | Build an AI phone receptionist with LiveKit, OpenAI Realtime & Twilio SIP. Test it, track latency & cost, and deploy it. | 120 | yes |
| 2 | LiveKit Agents, OpenAI Realtime, Pipecat & SIP telephony: build, test, monitor and deploy voice agents in Python. | 113 | yes |
| 3 | Build a voice agent that answers real phone calls, books appointments and hands off to humans. Then test and deploy it. | 119 | yes |
| 4 | STT, LLM, TTS, turn-taking, tools, telephony, voice agent testing, observability and Docker deploys in hands-on Python. | 119 | yes |
| 5 | Go past demos: latency budgets, interruptions, tool calls, SIP calls, WER and LLM-judge tests, cost per minute, CI/CD. | 118 | yes |
| 6 | The code-first voice AI course: LiveKit Agents, Deepgram, Cartesia, OpenAI Realtime, Twilio SIP, DeepEval and Langfuse. | 119 | yes |
| 7 | Ship a production AI receptionist in Python: real phone number, tool calling, guardrails, test suite and a cloud deploy. | 120 | yes |
| 8 | Build, test and operate low-latency voice AI agents with LiveKit, Pipecat and OpenAI Realtime. Code-first, not no-code. | 119 | yes |

## Suggested pairings

| Title | Best subtitle | Why |
|---|---|---|
| 1 | 1 | Recommended: brand-consistent title, keyword-rich subtitle |
| 2 | 3 | Title names the frameworks, subtitle names the outcome |
| 3 | 4 | Tool-heavy title, subtitle covers the whole pipeline |
| 4 | 7 | Testing angle in the title, production outcome in the subtitle |
| 7 | 5 | LiveKit-first title, 'past demos' subtitle |

## Verification output

Output of the script below, run with `python3` on 2026-09-28:

```text
T1:  59/60  OK  Production Voice AI Agents with Python: Build, Test, Deploy
T2:  59/60  OK  Voice AI Agents with Python: LiveKit, OpenAI Realtime & SIP
T3:  58/60  OK  Build Voice AI Agents in Python: LiveKit, Pipecat & Twilio
T4:  56/60  OK  Production Voice AI Agents: LiveKit, Testing & Telephony
T5:  59/60  OK  AI Voice Agents with Python: Build, Test & Deploy to Phones
T6:  58/60  OK  Voice AI Agent Engineering: Build, Test & Deploy in Python
T7:  57/60  OK  LiveKit Voice AI Agents: Build, Test & Deploy with Python
T8:  59/60  OK  Real-Time Voice AI Agents in Python: Phone-Ready and Tested
S1: 120/120 OK  Build an AI phone receptionist with LiveKit, OpenAI Realtime & Twilio SIP. Test it, track latency & cost, and deploy it.
S2: 113/120 OK  LiveKit Agents, OpenAI Realtime, Pipecat & SIP telephony: build, test, monitor and deploy voice agents in Python.
S3: 119/120 OK  Build a voice agent that answers real phone calls, books appointments and hands off to humans. Then test and deploy it.
S4: 119/120 OK  STT, LLM, TTS, turn-taking, tools, telephony, voice agent testing, observability and Docker deploys in hands-on Python.
S5: 118/120 OK  Go past demos: latency budgets, interruptions, tool calls, SIP calls, WER and LLM-judge tests, cost per minute, CI/CD.
S6: 119/120 OK  The code-first voice AI course: LiveKit Agents, Deepgram, Cartesia, OpenAI Realtime, Twilio SIP, DeepEval and Langfuse.
S7: 120/120 OK  Ship a production AI receptionist in Python: real phone number, tool calling, guardrails, test suite and a cloud deploy.
S8: 119/120 OK  Build, test and operate low-latency voice AI agents with LiveKit, Pipecat and OpenAI Realtime. Code-first, not no-code.
```

### Script (re-run after any edit)

```python
# check_titles.py: paste the current strings, then run: python3 check_titles.py
titles = [
    'Production Voice AI Agents with Python: Build, Test, Deploy',
    'Voice AI Agents with Python: LiveKit, OpenAI Realtime & SIP',
    'Build Voice AI Agents in Python: LiveKit, Pipecat & Twilio',
    'Production Voice AI Agents: LiveKit, Testing & Telephony',
    'AI Voice Agents with Python: Build, Test & Deploy to Phones',
    'Voice AI Agent Engineering: Build, Test & Deploy in Python',
    'LiveKit Voice AI Agents: Build, Test & Deploy with Python',
    'Real-Time Voice AI Agents in Python: Phone-Ready and Tested',
]
subtitles = [
    'Build an AI phone receptionist with LiveKit, OpenAI Realtime & Twilio SIP. Test it, track latency & cost, and deploy it.',
    'LiveKit Agents, OpenAI Realtime, Pipecat & SIP telephony: build, test, monitor and deploy voice agents in Python.',
    'Build a voice agent that answers real phone calls, books appointments and hands off to humans. Then test and deploy it.',
    'STT, LLM, TTS, turn-taking, tools, telephony, voice agent testing, observability and Docker deploys in hands-on Python.',
    'Go past demos: latency budgets, interruptions, tool calls, SIP calls, WER and LLM-judge tests, cost per minute, CI/CD.',
    'The code-first voice AI course: LiveKit Agents, Deepgram, Cartesia, OpenAI Realtime, Twilio SIP, DeepEval and Langfuse.',
    'Ship a production AI receptionist in Python: real phone number, tool calling, guardrails, test suite and a cloud deploy.',
    'Build, test and operate low-latency voice AI agents with LiveKit, Pipecat and OpenAI Realtime. Code-first, not no-code.',
]
for i, t in enumerate(titles, 1):
    print(f"T{i}: {len(t):>3}/60  {'OK' if len(t) <= 60 else 'TOO LONG'}  {t}")
for i, s in enumerate(subtitles, 1):
    print(f"S{i}: {len(s):>3}/120 {'OK' if len(s) <= 120 else 'TOO LONG'}  {s}")
```

## Rules applied

- No "Complete", "Masterclass", "Bootcamp", "A-Z" or year stamps. A year in a title goes stale and forces a rename.
- No claims like "#1", "best" or "only". These are hard to prove, and Udemy's landing page guidelines discourage them (verify current guidelines).
- No emojis, and no ALL CAPS words other than acronyms (AI, SIP, STT, LLM, TTS, WER).
- "Code-first, not no-code" in Subtitle 8 contrasts with the n8n voice courses without naming them.
