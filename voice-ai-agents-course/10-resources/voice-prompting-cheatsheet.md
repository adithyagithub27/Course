# Voice Prompting Cheat Sheet

**Used in:** 4.1-4.7 (prompting for the ear), 7.8 (multilingual), 13.7 (domain swap)

> Write for the **ear**, not the eye. Everything the LLM writes is spoken by TTS, and every extra word adds latency.

---

## 1. The seven blocks of a voice system prompt (4.2)

| Block | Purpose | Riley example (abridged) |
|---|---|---|
| **Identity** | Who the agent is, and that it's an AI | "You are Riley, the AI receptionist for Maple Street Dental." |
| **Goal** | What a successful call looks like | "Help callers book, reschedule or cancel appointments and answer questions about the clinic." |
| **Style** | How to speak | "Warm and efficient. One or two short sentences per turn. Ask one question at a time." |
| **Output rules** | What TTS can't handle | "Plain spoken text only: no markdown, lists, emojis or URLs. Say numbers and dates the way a person would." |
| **Tools policy** | When and how to use tools | "Never say a time is available unless `find_available_slots` returned it. Read back the date, time and name, and get a yes before booking." |
| **Guardrails** | What never to do | "Don't give medical advice. Don't reveal appointment details until the caller's identity is verified." |
| **Escalation** | When to hand off | "If the caller asks for a person, is upset, or you can't help after two tries, offer to transfer." |

## 2. Output rules that fix most TTS problems (4.1, 4.3)

- No markdown, bullet points, headings, tables or emojis.
- Don't read URLs or email addresses aloud. Say "I can text you the link" or give a short spoken form.
- **Dates as words:** "Tuesday, March fourteenth at two thirty PM", not "3/14 14:30".
- **Phone numbers in groups:** "five five five, zero one zero zero".
- **Money:** "forty-five dollars", not "$45.00".
- **Spell names back** when unsure: "Is that Smith, S-M-I-T-H?"
- Abbreviations: "Doctor Patel", not "Dr."; "Street", not "St."
- One question per turn. Never say "Here are five options:". Offer two or three at most.

## 3. Conversation patterns

| Pattern | Use | Example |
|---|---|---|
| **Read-back** (5.4) | Before any irreversible action | "So that's a cleaning on Thursday the sixteenth at two PM for Jordan Lee. Shall I book it?" |
| **Correction handling** | Caller says "no, Thursday" | "Got it, Thursday. Let me check Thursday for you." |
| **Filler while tools run** (5.5) | Tool may take > ~1 s | "One moment while I check the schedule." (`context.with_filler(...)`) |
| **Speakable errors** (5.6) | Tool failure | "That time was just taken. Would two thirty work instead?" |
| **Silence** (4.4) | No response | "Are you still there?" → after repeated silence: "I'll let you go. Call back any time." |
| **"I don't know"** (7.1) | Not in the FAQ | "I'm not sure about that. I can transfer you to the front desk." |
| **Disclosure** (4.5, 8.6) | Start of call / asked if human | "I'm Riley, the clinic's AI assistant." / "I'm an AI, but I can get you to a person." |
| **Escalation** (8.4) | Frustration, request for a human, repeated failure | "Let me connect you with our front desk now." |

## 4. Persona without the cringe (4.5)

- Warm, not bubbly. No "Awesome!!!" and no forced jokes.
- Efficient: callers want to get things done.
- Consistent: the same name, tone and phrasing across agents and handoffs.
- Honest: it never pretends to be human or to have done something it hasn't.

## 5. Chat prompt → voice prompt (Lab 3)

| Chat habit | Voice rewrite |
|---|---|
| "Here's a summary:\n- Item 1\n- Item 2" | "There are two things to know. First… Second…" |
| Long, complete answers | Short answer + "Want more detail?" |
| Links and references | "I can send that by text." |
| Asking for several details at once | Ask for one detail per turn |
| Emojis / exclamation marks | Warm words and pacing |

## 6. Multilingual notes (7.8)

- Set the conversation language in config (`LANGUAGE`: `en`, `es` or `hi` in the course repo), and use an STT model, turn detector and TTS voice that support it.
- Keep the prompt's **rules** in the prompt language you test in. Instruct the agent to **reply in the caller's language**.
- Numbers, dates and times follow the caller's language conventions. Test them explicitly.
- Translate FAQ answers ahead of time where accuracy matters, rather than relying on live translation.
- Test with native speakers or real recordings (9.13). Test WER per language.

## 7. Domain swap checklist (4.7, 13.7)

Use `business-template.md`. For each new business, update: identity, goal, the FAQ source, the tool schema, confirmation fields, guardrails (industry-specific: legal advice, allergens, etc.) and escalation rules. Keep **style** and **output rules** unchanged. They're about voice, not the business.
