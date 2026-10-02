# Section 4: Prompting for the Ear

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈45 min (8 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only; where talking time is shorter than the target duration, the rest is demo audio, typing, command output and on-screen dwell.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 4.1 | Why chat prompts fail on voice | SL | 7:00 | ~875 |
| 4.2 | Anatomy of a voice system prompt | SL | 8:00 | ~925 |
| 4.3 | Numbers, dates, names and pronunciation | SC | 8:00 | ~775 |
| 4.4 | Greetings, silence and "are you still there?" | SC | 7:00 | ~700 |
| 4.5 | Persona and brand voice without the cringe | TH | 5:00 | ~650 |
| 4.6 | Lab 3: Rewrite a chat prompt for voice | LAB | 5:00 (1:30 video) | ~225 |
| 4.7 | Challenge: Riley for your business | AS | 3:00 (1:30 video) | ~225 |
| 4.8 | Quiz: Prompting for the ear | QZ | 2:00 (0:45 video) | ~100 |

**Files for the whole section:** `03-code/src/maple/prompts.py` (prompt blocks and speech helpers) and `03-code/agents/s04_voice_prompting.py` (reference; students type along in `agents/my_voice_agent.py`).

---

## Lecture 4.1 — Why chat prompts fail on voice

| Field | Value |
|---|---|
| ID | 4.1 |
| Type | SL (slides, with two short audio clips) |
| Target duration | 7:00 (~875 spoken words, about 6:15 of talking at 140 wpm) |
| Learning objectives | 1. Name five ways chat-style output breaks text-to-speech: markdown, lists, length, URLs and symbols, emojis. 2. Explain why longer answers hurt both comprehension and perceived latency. 3. Describe the framework's built-in safety net (`filter_markdown`, `filter_emoji`) and why it isn't enough. |
| Prerequisites | Section 3 |
| Files used | Audio clip 1 recorded from `03-code/agents/s03_hello_agent.py` with `BROKEN=markdown` (chat-style prompt, text filters off); clip 2 from `03-code/agents/s04_voice_prompting.py` |

### Script

[AVATAR]
Listen to this. I asked Riley a simple question, using the kind of system prompt you'd write for a chatbot.

[DEMO: Audio clip with waveform and live captions, recorded with `BROKEN=markdown uv run python agents/s03_hello_agent.py console` (a markdown-and-emoji chat prompt with the TTS text filters switched off; Lecture 3.9 built the toggle). Ask "What are your opening hours?" Keep the real reply unedited. The text below shows the kind of answer to expect; if the real clip runs a different length, change "Twenty-five seconds" in the next avatar line to match.]

**Clip (chat-style Riley):** "Great question! Here are our opening hours. Monday through Thursday: eight A M to five P M. Friday: eight A M to two P M. Saturday: nine A M to one P M. Sunday: closed. You can also check our website at w w w dot maple street dental dot com slash hours for holiday hours. Let me know if you have any other questions! Smiling face with smiling eyes."

[AVATAR]
Twenty-five seconds. [PAUSE] And by the end, can you remember when they close on Friday? Most people can't. Now the voice-first version.

[DEMO: Second clip, same question, recorded with `uv run python agents/s04_voice_prompting.py console`, the voice-first Riley you'll finish in this section.]

**Clip (voice-first Riley):** "We're open eight to five Monday through Thursday, and eight to two on Fridays. Is there a day you're hoping to come in?"

[AVATAR]
Six seconds. You remember it. And it moves the conversation forward. Same model, same voice. The only difference is the prompt. Let's look at exactly what went wrong in the first one.

[SLIDE 1: Reading vs listening]
- Readers skim, jump back and scan structure
- Listeners get one pass, in order, at speaking speed
- Around 150 spoken words per minute: a 120-word chat answer is about 50 seconds of audio

Start with the root cause. Chat answers are written for eyes. Eyes skim. Eyes jump back. Eyes see headings and bullets and use them to navigate.

Ears get one pass, in order, at speaking speed. About one hundred and fifty words a minute. So a normal one hundred and twenty word chat answer takes almost a minute to hear. On a phone, a minute of one-sided talking feels like forever.

[SLIDE 2: Failure 1: markdown and formatting]
- `**bold**`, `# headings`, `| tables |`, `` `code` ``
- Best case: silently dropped. Worst case: read aloud.
- Either way, the structure it carried is lost

Failure one, markdown. LLMs love bold text, headings and tables. On a screen, that's helpful structure. In a voice, it's either dropped or, worse, read aloud. "Asterisk asterisk important asterisk asterisk." And even when it's dropped cleanly, the structure it carried is gone. A table becomes a jumble of words.

[SLIDE 3: Failure 2: lists]
- Seven items read in a row: the listener remembers one or two
- Lists hide the question the caller actually asked
- Voice pattern: give the top one or two, then ask a question

Failure two, lists. Our first clip read out a list of seven days. Nobody holds seven items in their head from one hearing. On voice, you give the one or two things that matter, and then you ask a question to narrow it down. "Which day were you hoping for?" is better than reading the whole week.

[SLIDE 4: Failure 3: length, which is also latency]
- Longer answers take longer to hear
- Callers can't get a word in without interrupting
- More output tokens: more cost, more chance of a wrong detail
- Target: one or two sentences per turn

Failure three, length. And here's the part people miss. Length is a latency problem too.

Remember the latency budget from Lecture 1.4? It measured time to the first sound. A long answer doesn't change that. But it changes how long until the caller gets to talk again. Twenty-five seconds of Riley is twenty-five seconds where the caller is waiting, or interrupting.

Long answers also cost more tokens, and every extra sentence is another chance to state a wrong detail. So the rule for Riley is one or two sentences per turn. That's it.

[SLIDE 5: Failure 4: URLs, emails, symbols and abbreviations]
- `www.maplestreetdental.com/hours` → "w w w dot..."
- `$1,250` / `10/6` / `Dr.` / `St.` / `#3` → guessing game for TTS
- Voice pattern: "I can text you a link", say it the way a person would

Failure four, things that only make sense written down. URLs. Email addresses. Dollar signs, slashes and abbreviations.

Think about "ten slash six." Is that October sixth or June tenth? Depends on the country. Is "Dr." doctor or drive? "Maple St." is street, but "St. Mary's" is saint. TTS engines guess, and they guess differently.

The voice pattern is simple. Say it the way a person would. "October sixth." "Doctor Nguyen." And for links, don't read them. Offer to text them instead.

[SLIDE 6: Failure 5: emojis and "chat personality"]
- Emojis: silently dropped, or read as their names
- "Great question!", "I'd be happy to help!", "Let me know if you have any other questions!"
- Filler phrases cost time on every turn

Failure five, emojis and chatbot personality. Emojis either vanish or get read as their names, like "smiling face with smiling eyes." And the chat habits come with them. "Great question!" "I'd be happy to help!" "Let me know if you have any other questions!" On a screen, you skip past them. On a call, each one costs a second or two, every single turn.

[SLIDE 7: The safety net, and why it isn't enough]
```python
session = AgentSession(
    # default when you don't set it:
    tts_text_transforms=["filter_markdown", "filter_emoji"],
    ...
)
```
- LiveKit strips markdown symbols and emojis before TTS by default
- It can't shorten answers, remove lists or fix "10/6"
- Prompt first, filters second, custom transforms third (Lecture 4.3)

Now, LiveKit helps a little. By default, the session runs two text filters before speech. One strips markdown symbols. One strips emojis. So you usually won't hear "asterisk asterisk."

But look at what the filters can't do. They can't shorten a long answer. They can't turn a seven-item list into a question. They can't decide whether ten slash six means October or June. Only the prompt can do that.

So the order of defense is: prompt first, filters second, and custom text transforms third, for the patterns you want to guarantee. You'll write one of those in Lecture 4.3.

[SLIDE 8: Chat prompt vs voice prompt]
Two columns.
Left, "Chat prompt": "You are a helpful assistant for Maple Street Dental. Answer questions thoroughly and format answers clearly."
Right, "Voice prompt": "You are Riley... on the phone. Everything you write is converted to speech. Keep every reply to one or two short sentences. Ask one question at a time. Never use markdown, lists, emojis or URLs. Say numbers and dates the way a person says them."

[AVATAR]
Here's the shift in one slide. The chat prompt says "be thorough, format clearly." The voice prompt says "you're on the phone, everything becomes speech, keep it short, one question at a time, no formatting, say numbers like a person."

And notice the most important sentence on the right. "Everything you write is converted to speech." The model doesn't know it's talking unless you tell it. That one sentence alone fixes a surprising amount.

[SLIDE 9: Recap]
- Listeners get one pass: keep replies short
- Markdown, lists, URLs and emojis break TTS
- Prompt first; default filters are a safety net

**Recap:** Chat prompts produce markdown, lists, long answers, symbols and emojis that break text-to-speech and bury the caller, so voice prompts must demand short, plain, spoken-style replies.

**Transition:** Next, we'll build Riley's real voice prompt block by block, and you'll see how each block maps to `src/maple/prompts.py`.

### Speaker notes: common student mistakes / Q&A

- Mistake: relying on `filter_markdown` and skipping the prompt rules. The filter removes symbols, not structure. A list without bullets is still a list.
- Mistake: overriding `tts_text_transforms` with only a custom function and accidentally turning off the default markdown and emoji filters. Include them in your list.
- "Should I just set `max_completion_tokens` very low?" It truncates mid-sentence, which sounds broken. Use the prompt to control length, and a generous token cap as a backstop.
- "Why does the model still add 'Great question!'?" Name it explicitly in the prompt as something to avoid, and test for it with a judge in Section 9.

---

## Lecture 4.2 — Anatomy of a voice system prompt

| Field | Value |
|---|---|
| ID | 4.2 |
| Type | SL (slides with code reveals) |
| Target duration | 8:00 (~925 spoken words, about 6:36 of talking at 140 wpm) |
| Learning objectives | 1. Structure a voice system prompt into identity, goal, style, output rules, tools policy, guardrails and escalation. 2. Explain why Riley's prompt is built from reusable blocks with `build_instructions()`. 3. Write output rules that make numbers, dates and phone numbers speakable. |
| Prerequisites | 4.1 |
| Files used | `03-code/src/maple/prompts.py` |

### Script

[AVATAR]
A good voice prompt reads like a job description for a new receptionist. Who you are. What you're trying to do. How you talk. What you never say. And when to get your manager. [PAUSE] Riley's prompt follows exactly that shape, and it's built from small blocks you can test and reuse. Let's open it up.

[SLIDE 1: Seven parts of a voice prompt]
1. Identity: who you are, AI disclosure
2. Goal: what a successful call looks like
3. Style: length, one question at a time, tone
4. Output rules: no markdown, how to say numbers and dates
5. Tools policy: when to call which tool, never invent results
6. Guardrails: medical advice, emergencies, off-topic
7. Escalation: when to hand off to a human

Seven parts. Identity. Goal. Style. Output rules. Tools policy. Guardrails. Escalation. You won't always need all seven, but you should always decide on purpose.

[SCREEN: VS Code, open `src/maple/prompts.py`. Scroll to `IDENTITY`.]

[CODE: reveal `IDENTITY` from `src/maple/prompts.py`]
```python
IDENTITY = f"""\
You are {AGENT_NAME}, the friendly AI receptionist for {CLINIC_NAME}, a family dental clinic.
You are talking to callers on the phone. Everything you write is converted to speech.
If anyone asks whether you are a person, say plainly that you are an AI assistant for the clinic.
Your goal is to answer questions about the clinic and help callers book, reschedule or cancel
appointments quickly and accurately."""
```

Here's the identity block, with the goal folded in. Four jobs in five lines.

It names Riley and the clinic. It tells the model it's on the phone, and that everything becomes speech. That's the sentence from the last lecture. It handles AI disclosure: if someone asks "are you a real person?", Riley says plainly that it's an AI. And it states the goal. Answer questions, and book, reschedule or cancel, quickly and accurately.

Notice what's missing. No backstory. No "you have ten years of experience." Those lines cost tokens on every turn and they don't change behavior.

[CODE: reveal `STYLE_RULES`]
```python
STYLE_RULES = """\
Style:
- Keep every reply to one or two short sentences.
- Ask only one question at a time, then stop and wait.
- Sound warm and efficient. Do not over-apologize or repeat the caller's words back needlessly.
- If you did not understand, say so briefly and ask the caller to repeat.
- If the caller interrupts, stop and respond to what they just said."""
```

Next, style. Five rules. One or two short sentences. One question at a time, then stop. Warm but efficient. Ask again if you didn't understand. And respond to interruptions.

"One question at a time" is the rule that matters most. Watch what happens without it. "What's your name, phone number and preferred day?" The caller answers the last one, and the first two are lost. Voice is a single lane. One question, one answer.

Yes, you'll notice this prompt uses dashes. That's fine. Formatting inside the prompt helps the model read it. We just don't want formatting in the model's output.

[CODE: reveal `OUTPUT_RULES`]
```python
OUTPUT_RULES = """\
Output format:
- Plain spoken sentences only. Never use markdown, bullet points, numbered lists, emojis, or URLs.
- Spell out numbers, times and dates the way a person says them, for example
  "Tuesday, October sixth at nine thirty in the morning".
- Read phone numbers in groups of digits, for example "five five five, zero one four two".
- Never read out internal IDs, JSON, or tool names."""
```

Output rules. This is the block that fixes last lecture's five failures.

Plain spoken sentences only. Then, and this is the trick, examples. "Tuesday, October sixth at nine thirty in the morning." "Five five five, zero one four two." Models copy examples far more reliably than they follow abstract rules. Show the exact shape you want to hear.

And the last line: never read out internal IDs, JSON or tool names. Without it, you'll one day hear Riley say "Your appointment A P T dash one zero zero one is confirmed."

[CODE: reveal `BOOKING_RULES` (first four lines only; the rest is covered in Section 5)]
```python
BOOKING_RULES = """\
Booking, rescheduling and cancelling:
- Collect, one at a time: the caller's full name, a callback phone number, the reason for the
  visit, and a preferred day and time of day.
- Always use the find_available_slots tool before offering times. Never invent availability.
..."""
```

Tools policy. We'll give Riley tools in Section five, but the policy is written here. The key line: always use the find available slots tool before offering times. Never invent availability.

Remember the scariest failure from Lecture 1.2? Riley offering a time that doesn't exist? This line is the first defense. Section nine's tests are the second.

[CODE: reveal `SAFETY_RULES` and `ESCALATION_RULES`]
```python
SAFETY_RULES = """\
Safety:
- You are not a dentist. Never diagnose, recommend medication or doses, or give treatment advice.
  Say you cannot give medical advice and offer the earliest appointment instead.
- If the caller describes a medical emergency such as trouble breathing, severe swelling of the
  face or throat, uncontrolled bleeding, or a head injury, tell them to hang up and call
  nine one one right away.
- For urgent dental problems such as a knocked-out tooth or severe pain, offer the earliest
  same-day or next-day slot and mention the after-hours emergency line."""

ESCALATION_RULES = """\
Escalation:
- Offer to transfer the caller to a human if they ask for a person, are upset, have a billing
  dispute, or if you fail to help after two attempts.
- Transfer immediately, without arguing, when the caller asks for a human a second time."""
```

Guardrails and escalation. For a dental clinic, the big guardrail is medical advice. Riley is not a dentist. It doesn't diagnose, and it doesn't recommend medication. Instead, it offers the earliest appointment. And for a real emergency, it tells the caller to call nine one one. Notice "nine one one" is spelled the way it should be spoken.

Escalation says when to get a human. Upset caller, billing dispute, two failed attempts, or a direct request. And my favorite rule: if they ask for a human a second time, transfer immediately, no arguing. Nothing makes callers angrier than a bot that won't let them go.

[SLIDE 2: Assemble with `build_instructions()`]
```python
from maple.prompts import build_instructions

instructions = build_instructions(
    today=date(2026, 10, 5),
    booking=True,        # Section 5
    knowledge=False,     # Section 7
    security=False,      # Section 11
)
```
- Always included: identity, style, output rules
- Safety and escalation on by default
- Each section switches on one more block
- `today=` adds "Today is Monday, 2026-10-05" so "next Tuesday" resolves correctly

Here's how the blocks come together. `build_instructions` always includes identity, style and output rules. Safety and escalation are on by default. And each section of the course switches on one more block. Booking in Section five. Knowledge in Section seven. Security in Section eleven.

And one line people forget. `today`. The model has no idea what day it is. If a caller says "next Tuesday" and the model doesn't know today's date, it will guess. Badly. So we pass today in, and the prompt says "Today is Monday, twenty twenty-six, October fifth."

[SLIDE 3: Why blocks beat one giant string]
- Test each block's effect in isolation (Section 9)
- Reuse blocks across specialist agents (Section 7)
- Shorter prompts: faster time-to-first-token on every turn
- Code review: a diff shows exactly which rule changed

Why build it from blocks instead of one big string? Four reasons. You can test each rule's effect. You can reuse blocks across the specialist agents in Section seven. You only include what an agent needs, so prompts stay short, and remember, shorter prompts mean faster time-to-first-token. And when someone changes a rule, the code review shows exactly which one.

[SLIDE 4: Five voice-prompt anti-patterns]
| Anti-pattern | Why it hurts | Instead |
|---|---|---|
| "Be concise" | Model's idea of concise is a paragraph | "One or two short sentences" plus an example |
| Pasting the whole FAQ | Slower first token on every turn | Retrieve on demand (Section 7) |
| Backstory and adjectives | Tokens with no behavior change | Rules with examples |
| "Never say X" with no alternative | Model stalls or apologizes | "If X, say Y instead" |
| Rules that contradict each other | Unpredictable behavior | One owner per rule; review diffs |

Five anti-patterns I see in almost every first voice prompt.

"Be concise." Too vague. The model's idea of concise is still a paragraph. Say "one or two short sentences" and show an example.

Pasting the whole FAQ into the prompt. It works, but every turn now pays for thousands of extra tokens in time-to-first-token. Section seven retrieves answers on demand instead.

Backstory and adjectives. "You are a warm, bubbly, empathetic professional with a passion for smiles." Tokens with no behavior change.

[SCREEN: VS Code, `03-code/src/maple/prompts.py`, `SAFETY_RULES`. Highlight "Never diagnose, recommend medication or doses, or give treatment advice", then "Say you cannot give medical advice and offer the earliest appointment instead."]

"Never say X," with no alternative. The model knows what not to do, but not what to do instead, so it stalls or over-apologizes. Always pair a "never" with an "instead." Look at the safety block: never give medical advice, and instead, offer the earliest appointment.

And rules that contradict each other. "Always confirm details" in one block and "keep calls under a minute" in another. Blocks help here too, because each rule has one home.

[AVATAR]
One last habit. Write rules as instructions to a person, in plain language, with examples. "Keep replies to one or two short sentences" works. "Be concise" doesn't, because the model's idea of concise is three paragraphs.

[SLIDE 5: Recap]
- Seven parts: a receptionist's job description
- Examples beat adjectives; pair "never" with "instead"
- `build_instructions()` assembles tested blocks

**Recap:** A voice prompt is a job description in seven parts, identity, goal, style, output rules, tools policy, guardrails and escalation, and Riley assembles it from tested blocks with `build_instructions()`.

**Transition:** Next, we'll handle the details prompts alone can't guarantee: numbers, dates, names and pronunciation, in code.

### Speaker notes: common student mistakes / Q&A

- Mistake: forgetting `today=`, then filing a bug that "the model can't do dates." It can't know the date. Pass it in.
- Mistake: writing rules without examples. "Say dates naturally" produces "10/06". An example sentence fixes it.
- Mistake: stuffing the FAQ into the prompt. It slows every turn. Section 7 retrieves it on demand.
- "Should I write the prompt in first person or second person?" Second person ("You are Riley") is the convention and works reliably. Be consistent.

---

## Lecture 4.3 — Numbers, dates, names and pronunciation

| Field | Value |
|---|---|
| ID | 4.3 |
| Type | SC (code-along) |
| Target duration | 8:00 (~775 spoken words, about 5:32 of talking at 140 wpm) |
| Learning objectives | 1. Turn phone numbers, dates and times into speakable words with the helpers in `src/maple/prompts.py`. 2. Confirm names by spelling them back. 3. Write a TTS text transform that fixes pronunciation right before speech, and pass it in `tts_text_transforms` without losing the default filters. |
| Prerequisites | 4.2 |
| Files used | You type: `03-code/agents/my_voice_agent.py`. Reference: `03-code/agents/s04_voice_prompting.py`. Also `03-code/src/maple/prompts.py`. |

### Script

[AVATAR]
"Your appointment is on ten slash six at nine thirty A M. We'll call you at five hundred twelve, five hundred fifty-five, zero one four eight." [PAUSE] Every word of that is technically correct, and it's still wrong for the ear. Numbers, dates and names are where voice agents sound most robotic. Let's fix them at three layers: the prompt, the data we hand the LLM, and a last-second text transform.

[SLIDE 1: Three layers of defense]
1. Prompt: output rules with spoken examples (Lecture 4.2)
2. Data: tools return pre-formatted, speakable text
3. Transform: rewrite text right before TTS

Layer one, you already have. The output rules with spoken examples. Layer two is new. Don't make the LLM convert data into speech. Give it data that's already speakable. Layer three is a safety net that rewrites text right before it's spoken.

[SCREEN: Terminal.]

[CODE: start a Python shell]
```bash
uv run python
```

Let's start with layer two. `prompts.py` has a set of small, tested helpers. Watch.

[CODE: try the speech helpers]
```python
>>> from datetime import date, datetime, time
>>> from maple import prompts
>>> prompts.speak_phone("(512) 555-0148")
'five one two, five five five, zero one four eight'
>>> prompts.speak_date(date(2026, 10, 6))
'Tuesday, October sixth'
>>> prompts.speak_time(time(9, 30))
'nine thirty in the morning'
>>> prompts.speak_slot(datetime(2026, 10, 9, 8, 0))
"Friday, October ninth at eight o'clock in the morning"
```

Phone numbers come out in three groups, with commas. Those commas matter. Most TTS voices pause briefly at a comma, which gives the caller time to check each group. Dates come out with the weekday and an ordinal, "October sixth." Times say "in the morning" instead of "A M."

In Section five, the booking tools use exactly these helpers. When Riley checks the schedule, the tool returns "Friday, October ninth at eight o'clock in the morning," and the LLM just repeats it. The model never has to guess how to say a date.

[CODE: a quick look at why this is pure Python]
```python
>>> prompts.number_to_words(1250)
'one thousand two hundred fifty'
>>> prompts.speak_year(1988)
'nineteen eighty-eight'
```

And because these are plain functions, they're unit-tested. Dates of birth, prices, years, all covered, all offline.

[SCREEN: Exit the shell. VS Code, new file `agents/my_voice_agent.py`.]

Now names. Names are the words speech-to-text gets wrong most often, and you can't fix that with a helper, because you don't know the name yet. So we fix it with conversation design: spell it back.

[CODE: step 1, start `agents/my_voice_agent.py` with the imports and a spelling rule (the reference, `agents/s04_voice_prompting.py`, has the same lines plus a longer docstring and a logger)]
```python
"""Riley, prompted for the ear (Lectures 4.3 and 4.4)."""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterable

from livekit.agents import Agent, AgentServer, JobContext, UserStateChangedEvent, cli

from common import CallState, clinic_today, create_session, get_settings, prewarm
from maple import prompts

# Extra prompt block for names (lecture 4.3): STT gets surnames wrong more than any other word.
SPELLING_RULES = """\
Names:
- After the caller gives their name, spell the last name back letter by letter and ask if it's
  right, for example "Is that O, R, T, I, Z?"
- If the caller spells something, use exactly the letters they said."""
```

Start a new file, `my_voice_agent.py`. After the imports, a small extra prompt block called spelling rules, exactly as it appears in the reference file. Spell the last name back letter by letter, with an example. And if the caller spells something, use exactly those letters. We'll add it to Riley's instructions in a minute with the `extra` parameter.

Why the last name only? Because spelling back a first and last name on every call gets tedious. Match the effort to the risk. For booking, the last name is what the front desk searches by.

[SLIDE 2: Pronunciation: what the prompt can't fix]
- Abbreviations: "Dr.", "St.", "Ste.", "appt", "DDS"
- Brand and product names, surnames
- The LLM might write them even when told not to
- Fix at the last moment: a TTS text transform

Now layer three. Even with good rules, the LLM will sometimes write "Dr. Alvarez" or "Suite 200, Maple St." And some voices read "Dr." as "drive" or "D R." We want a guarantee, not a hope. That's what TTS text transforms are for.

[CODE: step 2, an abbreviation table and a text transform]
```python
# Pronunciation fixes applied to the text stream right before TTS (lecture 4.3).
ABBREVIATIONS = {
    r"\bDr\.": "Doctor",
    r"\bSt\.": "Street",
    r"\bSte\.": "Suite",
    r"\bappt\b": "appointment",
    r"\bDDS\b": "D D S",
}


async def expand_abbreviations(text: AsyncIterable[str]) -> AsyncIterable[str]:
    """TTS text transform: rewrite abbreviations chunk by chunk.

    LLM output streams in small chunks, so an abbreviation split across two
    chunks is missed. Good enough for a demo; production code buffers to word
    boundaries.
    """
    async for chunk in text:
        for pattern, spoken in ABBREVIATIONS.items():
            chunk = re.sub(pattern, spoken, chunk)
        yield chunk
```

First, a small table of regular expressions and their spoken forms. "Dr." becomes "Doctor." "Ste." becomes "Suite." "DDS" becomes three separate letters.

Then the transform itself. It's an async generator. LiveKit hands it the LLM's text as a stream of chunks, and it yields rewritten chunks, which go straight into the TTS. This runs after the LLM and before the voice, so nothing the model writes can skip it.

One honest limitation. The LLM streams text in small pieces. If "Dr." happens to be split across two chunks, this simple version misses it. It's good enough for a demo, and the fix for production is to buffer up to a word boundary before rewriting.

[CODE: step 3, the agent]
```python
class VoiceFirstRiley(Agent):
    """Riley with the full voice-first prompt and a scripted greeting."""

    def __init__(self) -> None:
        super().__init__(
            instructions=prompts.build_instructions(today=clinic_today(), extra=SPELLING_RULES),
        )
```

Now the agent, VoiceFirstRiley. Its instructions come from `build_instructions`, with today's date so relative dates work, and our spelling rules as an extra block. `clinic_today` returns the real date, or the pinned demo date if you set MAPLE_TODAY.

[CODE: step 4, the server and session with the transform (your file at the end of this lecture; the reference already has the silence handling you'll add in Lecture 4.4)]
```python
server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start Riley with silence handling."""
    settings = get_settings()
    session = create_session(
        settings,
        proc=ctx.proc,
        userdata=CallState(),
        tts_text_transforms=["filter_markdown", "filter_emoji", expand_abbreviations],
    )
    await session.start(agent=VoiceFirstRiley(), room=ctx.room)


if __name__ == "__main__":
    cli.run_app(server)
```

Two new things here. First, `create_session` from common. It builds the whole session from settings: models, VAD, turn handling and call state. And the server's setup function, prewarm, loads the VAD model once per process, so each call starts faster. Section twelve covers prewarming in depth.

Second, and this is the important line, `tts_text_transforms`. It's a list. Notice I kept "filter markdown" and "filter emoji" in it. Those are the defaults from Lecture 4.1. If you pass your own list and leave them out, you just turned off the markdown filter. Keep them, and add yours at the end.

[SCREEN: Terminal.]

[CODE: run it]
```bash
uv run python agents/my_voice_agent.py console
```

[DEMO: Caller: "Who are your dentists?" Riley answers with "Doctor ..." names. Caller: "My name is Sam Ortiz." Riley: "Thanks, Sam. Is that O, R, T, I, Z?" Caller: "Yes." Caller: "What's your phone number?" Riley reads the clinic number in groups.]

Listen for three things. [PAUSE] "Doctor," not "D R." [PAUSE] The last name spelled back. [PAUSE] And the clinic's number in three groups.

[SLIDE 3: Going further (production)]
- Buffer the stream to word boundaries before rewriting
- Provider pronunciation dictionaries (for example Cartesia's `pronunciation_dict_id` on the plugin)
- Keep the table small and tested; "St." could be "Saint" in "St. Louis"

[AVATAR]
For production, three upgrades. Buffer to word boundaries. Use your TTS provider's pronunciation dictionary for names that are consistently wrong. And keep the table small and tested, because abbreviations are ambiguous. Our table turns "St." into "Street." That's right for Maple Street, and wrong for a clinic in St. Louis.

[SLIDE 4: Recap]
- Tools hand the LLM speakable data
- Spell last names back, letter by letter
- Transforms run last; keep the default filters

**Recap:** Make numbers and dates speakable with tested helpers before the LLM sees them, confirm names by spelling them back, and use a TTS text transform, alongside the default filters, as the last line of defense.

**Transition:** Next, we'll make Riley greet callers the same way every time, and handle the awkward moment when a caller goes silent.

### Speaker notes: common student mistakes / Q&A

- Mistake: `tts_text_transforms=[expand_abbreviations]` without the two built-in filters. Markdown starts leaking into speech again.
- Mistake: doing heavy work (network calls) inside a text transform. It sits directly on the latency path. Keep it to fast string operations.
- "The transcript still shows 'Dr.'" Transforms change what's spoken, not necessarily what the LLM wrote into the chat history. That's expected.
- "Should I spell back every name?" Match effort to risk: last names for bookings, yes; a first name used only for small talk, no.

---

## Lecture 4.4 — Greetings, silence and "are you still there?"

| Field | Value |
|---|---|
| ID | 4.4 |
| Type | SC (code-along) |
| Target duration | 7:00 (~700 spoken words, about 5:00 of talking at 140 wpm) |
| Learning objectives | 1. Greet every caller consistently in `on_enter` with `session.say`. 2. Detect silence with `user_away_timeout` and the `user_state_changed` event. 3. Check in once, then hang up gracefully after repeated silence. |
| Prerequisites | 4.3 |
| Files used | You type: `03-code/agents/my_voice_agent.py`. Reference: `03-code/agents/s04_voice_prompting.py`. Also `03-code/src/maple/prompts.py` (`GREETING`, `SILENCE_CHECK_IN`, `SILENCE_GOODBYE`), `03-code/agents/common.py` (`CallState.silence_prompts`). |

### Script

[AVATAR]
Two moments make or break a phone call. The first two seconds, and the silence. [PAUSE] If the greeting changes every call, or takes a second longer because the LLM is writing it, callers notice. And if a caller puts the phone down to find their insurance card, what should Riley do? Wait forever? Hang up? Let's handle both.

[SLIDE 1: Greeting: LLM or fixed line?]
- `generate_reply(instructions="Greet...")`: flexible, adds an LLM round trip, varies per call
- `session.say(GREETING)`: instant, identical every call, guaranteed AI disclosure
- Riley uses a fixed line, in `on_enter`

In Section three, we greeted with `generate_reply`. The LLM wrote a greeting each time. That's flexible, but it costs an LLM round trip, and the wording changes from call to call. Some days it might even forget to say it's an AI.

For the greeting, we want the opposite. Instant, identical and compliant. That's `session.say` with a fixed line.

[SCREEN: VS Code, `src/maple/prompts.py`, scroll to `GREETING`, `SILENCE_CHECK_IN`, `SILENCE_GOODBYE`.]

Our fixed lines live in `prompts.py`. The greeting: "Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?" A silence check-in. And a polite goodbye for when a caller never comes back.

[SCREEN: VS Code, `agents/my_voice_agent.py`.]

[CODE: step 1, add `on_enter` to `VoiceFirstRiley`]
```python
    async def on_enter(self) -> None:
        """Speak the fixed greeting as soon as the caller connects."""
        self.session.say(prompts.GREETING, allow_interruptions=True)
```

Add an `on_enter` method to VoiceFirstRiley. It runs the moment this agent takes over the call. Inside, `session.say` with the greeting.

I'm allowing interruptions here, so a caller who starts talking right away isn't ignored. If your compliance team needs the AI disclosure heard in full every time, set it to false. That's a business decision, and now it's one argument.

Notice there's no `generate_reply` in the entrypoint anymore. The agent greets itself. That matters in Section seven, where each specialist agent gets its own `on_enter`.

[SLIDE 2: How LiveKit tracks silence]
- User state: `speaking`, `listening`, `away`
- `away`: both caller and agent silent for `user_away_timeout` seconds (default 15)
- Event: `user_state_changed` with `old_state` and `new_state`

Now silence. The session tracks the caller's state. Speaking, listening or away. Away means both the caller and Riley have been silent for a set number of seconds, called the user away timeout. The default is fifteen. When the state changes, the session emits an event called user state changed.

[CODE: step 2, constants at the top of the file]
```python
SILENCE_TIMEOUT_S = 12.0
MAX_SILENCE_PROMPTS = 2
```

Two constants near the top. Twelve seconds of silence counts as away. And we'll prompt at most twice: one check-in, then goodbye.

[CODE: step 3, the session gets a timeout]
```python
    session = create_session(
        settings,
        proc=ctx.proc,
        userdata=CallState(),
        user_away_timeout=SILENCE_TIMEOUT_S,
        tts_text_transforms=["filter_markdown", "filter_emoji", expand_abbreviations],
    )
    background: set[asyncio.Task[None]] = set()
```

Pass the timeout into the session. And create an empty set called background. It holds references to background tasks, so Python doesn't garbage-collect them halfway through.

[CODE: step 4, the silence handler]
```python
    async def handle_silence() -> None:
        state = session.userdata
        state.silence_prompts += 1
        if state.silence_prompts < MAX_SILENCE_PROMPTS:
            session.say(prompts.SILENCE_CHECK_IN)
            # The user is now "away". Put them back to "listening" so the away timer
            # restarts and a second silence fires this handler again.
            session.reset_away_timer()
            return
        handle = session.say(prompts.SILENCE_GOODBYE, allow_interruptions=False)
        await handle.wait_for_playout()
        state.call_outcome = "abandoned_silence"
        session.shutdown()
```

Now the handler. We count silence prompts in the call state. `CallState` already has a field for it, called silence prompts. You'll meet the whole class in Section five.

First time: say the check-in, "Are you still there? Take your time." We don't wait for it to finish. We reset the away timer straight away, and that line matters. Once a caller is marked away, the session won't mark them away again on its own. Resetting puts them back to listening, so a fresh twelve-second countdown starts. And because the countdown only runs while both of you are quiet, it really starts once the check-in has played.

Second time: say goodbye, and don't allow interruptions, so the goodbye is heard in full. Wait for it to play out. Record the outcome. And shut the session down.

[CODE: step 5, wire up the event]
```python
    @session.on("user_state_changed")
    def on_user_state_changed(ev: UserStateChangedEvent) -> None:
        if ev.new_state == "away":
            task = asyncio.create_task(handle_silence())
            background.add(task)
            task.add_done_callback(background.discard)
        elif ev.new_state == "speaking":
            session.userdata.silence_prompts = 0

    await session.start(agent=VoiceFirstRiley(), room=ctx.room)
```

Finally, the event handler. Event handlers are regular functions, not async, so we start the async work as a task, and keep a reference in the background set. When the caller becomes away, handle the silence. When the caller speaks again, reset the counter, so a caller who comes back gets a fresh start.

[SCREEN: Terminal.]

[CODE: run it]
```bash
uv run python agents/my_voice_agent.py console
```

[DEMO: Riley greets. Stay silent for 12 seconds. Riley: "Are you still there? Take your time, I'm here when you're ready." Stay silent 12 more seconds. Riley: "I haven't heard anything for a while, so I'll end the call now. Please call back any time. Goodbye." The session ends.]

Now I'll say nothing. [PAUSE] Twelve seconds later, the check-in. [PAUSE] I stay quiet. Twelve more seconds, and a polite goodbye. The session ends.

[DEMO: Run again. After the check-in, say "Sorry, I was grabbing my card." Riley continues normally.]

And if I come back after the check-in, Riley just carries on, and the counter resets.

[SLIDE 3: Hanging up for real]
- Console and dev: `session.shutdown()` ends Riley's session
- Phone calls: delete the room so the phone line drops too (the `end_call` tool, Section 8)
- Always say goodbye before hanging up, and never mid-sentence

[AVATAR]
One note on hanging up. In console and dev mode, shutting down the session is enough. On a real phone call, you also want the line itself to drop, which means deleting the room. That's the end call tool in Section eight. And whatever you do, say goodbye first. An agent that just goes silent and disconnects feels broken, even when it's working as designed.

[SLIDE 4: Recap]
- Fixed greeting: `session.say` in `on_enter`
- `user_away_timeout` plus `user_state_changed` detect silence
- Check in once, reset the timer, then goodbye

**Recap:** Greet with a fixed `session.say` line in `on_enter`, detect silence with `user_away_timeout` and `user_state_changed`, check in once, reset the timer, and hang up politely on the second silence.

**Transition:** You've shaped what Riley says and when, so next let's talk about how it sounds: persona and brand voice, without the cringe.

### Speaker notes: common student mistakes / Q&A

- Mistake: forgetting `session.reset_away_timer()` after the check-in. The caller stays "away" and the second silence never fires, so Riley never hangs up.
- Mistake: making the event handler `async def`. Event callbacks are synchronous; start async work with `asyncio.create_task` and keep a reference.
- Mistake: a timeout that's too short for real callers. People look for insurance cards and calendars. Twelve to twenty seconds is a sensible range; test with real people.
- "Can I use this to detect a dropped line?" A dropped phone call usually disconnects the SIP participant, which ends the session anyway. Silence handling is for callers who are still connected but quiet.

---

## Lecture 4.5 — Persona and brand voice without the cringe

| Field | Value |
|---|---|
| ID | 4.5 |
| Type | TH (talking head) |
| Target duration | 5:00 (~650 spoken words, about 4:39 of talking at 140 wpm) |
| Learning objectives | 1. Balance warmth and efficiency for a transactional voice agent. 2. Disclose that the agent is an AI clearly and early. 3. Keep persona consistent across prompt, voice and fixed lines. |
| Prerequisites | 4.2 |
| Files used | `03-code/src/maple/prompts.py` (`IDENTITY`, `GREETING`), `03-code/agents/s04_voice_prompting.py` (short console demo) |

### Script

[AVATAR]
"Heyyy there! I'm Riley, your super friendly dental buddy! What can I do to make your smile shine today?" [PAUSE] You winced. Everyone does. So let's talk about personality, and how to give Riley one without making callers want to hang up.

[AVATAR]
Here's the first principle. Callers to a dental clinic want something done. Book a cleaning. Move an appointment. Find out if you take their insurance. Personality should make that faster and more pleasant, never slower.

[SLIDE 1: Warmth and efficiency are two dials]
- Warm and efficient: the target ("Oh no, sorry to hear that. Let me find you the earliest slot.")
- Warm, not efficient: cringe ("Aww, teeth can be so tricky! Don't worry, we'll get you smiling again!")
- Efficient, not warm: cold ("State preferred date.")

So think of warmth and efficiency as two dials, not one. A great human receptionist turns both up. They're friendly, and they get you booked in forty seconds. A cringe persona turns warmth all the way up and efficiency down. Jokes, exclamation marks, small talk. A cold bot does the opposite. Correct, but it feels like talking to a form. Which of those would you rather call?

Look at the target line. "Oh no, sorry to hear that. Let me find you the earliest slot." Six words of empathy, then straight to action. That's the whole recipe. Acknowledge briefly, then move.

[AVATAR]
Principle two. Say it's an AI. Early, clearly and without apologizing. Does Riley pass? Let's ask it.

[DEMO: `uv run python agents/s04_voice_prompting.py console`. Riley's fixed greeting plays. Ask: "Wait, am I talking to a real person?" Riley says in one sentence that it's the clinic's AI assistant, and offers to help.]

[SCREEN: VS Code, `03-code/src/maple/prompts.py`. Highlight `GREETING`, then the `IDENTITY` line "If anyone asks whether you are a person, say plainly that you are an AI assistant for the clinic."]

Riley's greeting says "This is Riley, the clinic's AI assistant." It's in the first sentence. And the direct question you just heard is handled by one line in the identity block.

[AVATAR]
Why disclose at all? There are three reasons.

One, trust. Callers who find out later that they were talking to a bot feel tricked, even when the call went well.

Two, rules. A growing number of places require AI disclosure, especially on phone calls. We'll cover compliance properly in Section eight, and none of it is legal advice. But disclosing up front costs you nothing.

Three, it actually helps the conversation. When callers know it's an AI, they speak a little more clearly and they don't expect it to know their life story.

So when someone asks directly, Riley says plainly that it's an AI assistant. Never let a persona lie about what it is.

[SLIDE 2: Consistency: one Riley everywhere]
- Prompt: identity and style rules
- Voice: one TTS voice, one speed
- Fixed lines: `GREETING`, `GOODBYE`, `TRANSFER_MESSAGE` in `prompts.py`
- Same name, same tone, same sign-off, every call

Principle three. Consistency. Riley's personality shows up in three places, and they have to agree.

The prompt, which sets the tone for everything the LLM writes. The voice, which is the actual sound. And the fixed lines, the greeting, the goodbye and the transfer message, which we keep as constants in prompts dot py.

If the greeting is formal and the LLM is chatty, callers notice the seam. If you change the voice mid-call during a handoff, callers think they've been transferred to a different company. Keep one name, one voice and one tone across the whole call. In Section seven, when Riley hands off to specialists, we'll make a deliberate choice about whether they sound like Riley or like colleagues.

[AVATAR]
Principle four. Match your brand, not your favorite movie character. A pediatric dentist can be playful. A surgical practice should be calm and precise. A bank should sound like a bank. Ask the business owner three words they'd use for their front desk. For Maple Street Dental, those words are "friendly, calm, efficient." Put those words in the prompt. Pick a voice that fits them. And test it by listening to real calls, not by reading the prompt.

[SLIDE 3: Persona checklist]
- Discloses AI in the first sentence
- Acknowledges feelings in six words or fewer, then acts
- No exclamation marks, jokes or catchphrases in fixed lines
- Three brand words in the prompt
- Same voice and sign-off on every call

[AVATAR]
Here's your checklist. Screenshot it, and use it in the lab.

And a final tip. Humor and cheerfulness wear thin fast. The first "Have a sparkly day!" is cute. By the tenth call, the front desk staff who listen to recordings will hate it. So ask yourself: will this line still be pleasant on the hundredth call?

[SLIDE 4: Recap]
- Warm and efficient: acknowledge briefly, then act
- Disclose AI in the first sentence
- One name, one voice, one tone

**Recap:** Good voice personas are warm and efficient at the same time, disclose that they're AI up front, and stay consistent across prompt, voice and fixed lines.

**Transition:** Now it's your turn: in Lab 3, you'll take a real chat prompt and rewrite it for the ear.

### Speaker notes: common student mistakes / Q&A

- Mistake: giving the agent a human-sounding name and no disclosure, then being surprised by angry callers. Always disclose.
- Mistake: asking the LLM to "be enthusiastic." It over-delivers. Describe the target with concrete examples instead.
- "Should Riley use the caller's name?" Once or twice per call is warm. Every sentence is creepy, and names are the words STT gets wrong most often.
- "Can I clone a real receptionist's voice?" Only with explicit written consent and a clear business reason. Section 11 covers voice-cloning risks.

---

## Lecture 4.6 — Lab 3: Rewrite a chat prompt for voice

| Field | Value |
|---|---|
| ID | 4.6 |
| Type | LAB (text lab with short video walkthrough) |
| Target duration | 5:00 total (1:30 video, ~225 spoken words, about 1:36 of talking at 140 wpm) |
| Learning objectives | 1. Convert a chat-style system prompt into a voice-first prompt using the seven-part structure. 2. Evaluate the result against a rubric by listening, not reading. |
| Prerequisites | 4.1 to 4.5 |
| Files used | `04-labs/lab-03-voice-prompting.md`, `03-code/agents/s04_voice_prompting.py` |

### Script

[AVATAR]
A prompt can read perfectly and still sound terrible on the phone. [PAUSE] In this lab you'll hear exactly that, and then fix it. Set aside about forty-five minutes.

[SCREEN: Open `04-labs/lab-03-voice-prompting.md`. Scroll to "The 'before' prompt": MapleBot, written for Maple Street Dental's website chat widget, with markdown headers, a table, a URL, emojis and "give your best guess".]

Here's the "before." A contractor wrote it for Maple Street Dental's website chat widget, and now the clinic wants it on the phone. Markdown headers. A table of times. A link to a forms page. Emojis. And "if you don't know, give your best guess." How many problems can you spot before you run it? The solution notes list ten.

[SCREEN: Scroll to the test script table, P1 to P8.]

First, you hear the problem. Copy the Section four agent, swap in the "before" prompt, and say eight test lines out loud: hours, the phone number, a price, the forms link, a booking, an unusual name, "are you a real person," and a question about ibuprofen.

[SCREEN: Scroll through Steps 2 to 6, ending on the twenty-point rubric.]

Then you write a tiny voice lint script, write your own voice-first prompt under ten headings, test the silence check-in from Lecture 4.4, compare with the course's prompt, and score yourself. Fourteen out of twenty passes.

[AVATAR]
One rule. Judge by ear first. Listen, score, and only then read the transcript. And try it yourself before you peek at the sample solution.

**Recap:** Lab 3 has you rewrite a chat prompt with the seven-part structure and score it by listening against a five-row rubric.

**Transition:** Next, a challenge: build a voice receptionist for a business you know.

### Speaker notes: common student mistakes / Q&A

- Students paste `build_instructions()` output instead of writing their own prompt. Step 3 asks them not to: the point is to practise, and Step 5 compares with the course's prompt afterwards.
- Use `console --text` to iterate fast, but do the final scoring in audio mode. Some problems only show up when spoken.
- If an answer is too long, the fix is usually an example sentence in the output rules, not more adjectives.

---

## Lecture 4.7 — Challenge: Riley for your business

| Field | Value |
|---|---|
| ID | 4.7 |
| Type | AS (assignment with short video brief) |
| Target duration | 3:00 (1:30 video, ~225 spoken words, about 1:36 of talking at 140 wpm) |
| Learning objectives | 1. Adapt Riley's prompt blocks to a real business you know. 2. Produce a first portfolio artefact: a working prompt and one transcript. |
| Prerequisites | 4.1 to 4.6 |
| Files used | `05-projects/challenges.md` (Challenge 4.7), `10-resources/business-template.md`, `03-code/src/maple/prompts.py`, `03-code/agents/s04_voice_prompting.py` |

### Script

[AVATAR]
Here's your first portfolio piece. Take everything from this section and build a receptionist for a business you actually know. A salon. A restaurant. A physio clinic. A law office. Your cousin's bike shop.

[SCREEN: Open `10-resources/business-template.md`. Scroll through section 1, the business facts table (including "Things the agent must never do" and "Human handoff"), then section 4, the fill-in prompt blocks.]

Start with this template. Section one is a facts table: hours, services, policies, what the agent must never do, and when to hand off to a human. Section four has fill-in prompt blocks, with style and output rules marked "keep from Riley." Filling it in takes about ten minutes, and it's the same discovery work you'd do for a paying client.

[SCREEN: VS Code, copy `agents/s04_voice_prompting.py` to `agents/c47_my_business.py`. Replace the instructions with a new identity and rules, keeping the style and output rules blocks.]

Then copy the Section four agent into a new file, `c47_my_business.py`. Keep the style and output rules, because those work for any voice agent. Rewrite the identity, the never-do rules and the escalation rules for your business. And change the fixed greeting.

[SCREEN: Terminal: `uv run python agents/c47_my_business.py console`. Short conversation.]

Run it in console mode, and hold a three-to-six-turn conversation with the questions your callers really ask. Then run the voice lint from Lab 3 over the replies.

[AVATAR]
To finish, post one transcript in the Q&A with your business type and one thing you changed after hearing it. Invent the names and numbers first. Then read a few others.

**Recap:** The challenge adapts Riley's prompt blocks to a business you know, using the template, and ends with one shared transcript.

[SLIDE 1: You can now]
- Write a seven-part voice prompt from blocks
- Make numbers, dates and names speakable
- Greet, handle silence and hang up politely

**Transition:** Last stop for Section 4: a short quiz on prompting for the ear.

### Speaker notes: common student mistakes / Q&A

- Students keep Maple Street's safety rules for a non-medical business. Encourage them to write guardrails that fit their domain, such as allergy questions for a restaurant.
- Remind students not to paste real customer names or phone numbers into transcripts they share.
- If the agent answers questions it can't know (prices, availability), add "If you don't know, say so and offer to take a message" to the guardrails. Tools come in Section 5.

---

## Lecture 4.8 — Quiz: Prompting for the ear

| Field | Value |
|---|---|
| ID | 4.8 |
| Type | QZ (quiz with short video intro) |
| Target duration | 2:00 total (0:45 video, ~100 spoken words, about 0:43 of talking at 140 wpm) |
| Learning objectives | 1. Check understanding of voice prompt structure, speakable formatting and silence handling. |
| Prerequisites | 4.1 to 4.7 |
| Files used | `06-assessments/quizzes/section-04.md` |

### Script

[AVATAR]
Riley reads the clinic's number as "five hundred twelve, five hundred fifty-five, one hundred." [PAUSE] You know how to fix that now. Let's check. Five quick questions.

[SLIDE 1: Section 4 quiz: what's covered]
- Why long answers hurt on voice
- Speakable phone numbers
- A timestamp leaking from a tool result
- Silence and "are you still there?"
- AI disclosure when asked

You'll get questions on long answers, phone numbers, a tool result that leaks a timestamp, silence handling and AI disclosure. One tip: for the timestamp question, think about the three layers from Lecture 4.3, and pick the one that fixes it for every reply.

**Recap:** The quiz checks voice prompt structure, speakable formatting and silence handling.

**Transition:** Next, Section 5: Riley gets real tools to book, reschedule and cancel appointments.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: the timestamp question. The robust fix is the data layer (the tool returns speakable text plus a machine value it tells the model never to read), not a prompt rule alone.
- Related point students raise here: the default filters are replaced, not merged, when you pass your own `tts_text_transforms` list (Lecture 4.3).
