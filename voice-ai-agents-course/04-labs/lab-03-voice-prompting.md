# Lab 3: Rewrite a Chat Prompt for Voice

| Field | Details |
|---|---|
| **Section / lecture** | Section 4, lecture 4.6 |
| **Time estimate** | 45 minutes |
| **Difficulty** | Beginner |
| **Goal** | Turn a typical chatbot system prompt into a voice-first prompt, test it by ear and with an automatic "voice lint" check, and score it against a 20-point rubric. |
| **You will produce** | `agents/lab03_prompt.py` (your prompt), `labs/voice_lint.py`, and `notes/lab-03.md` with before/after results and your rubric score |

---

## Prerequisites

- Lab 2 complete.
- Lectures 4.1 to 4.5 watched.
- `agents/s04_voice_prompting.py` and `src/maple/prompts.py` open in your editor.

---

## The "before" prompt

A previous contractor wrote this prompt for Maple Street Dental's **website chat widget**. The clinic now wants to reuse it on the phone.

```text
You are MapleBot, a helpful assistant for Maple Street Dental.
Answer patient questions thoroughly so they don't need to call back.
Use markdown with headers and bullet points so answers are easy to scan.
When listing available appointment times, show all options in a table.
Link patients to https://maplestreetdental.example/forms for new-patient forms.
Always give complete price information, for example "Cleaning: $120-$180".
Be enthusiastic and use emojis to seem friendly! 😊
If you don't know something, give your best guess.
Our phone number is (512) 555-0100.
```

Before you start, list at least **six** things in this prompt that will break or sound wrong on a phone call. (The solution notes list ten.)

---

## Step 1: Hear the problem

Copy the voice-prompting agent so you can experiment without touching the reference file:

```bash
cp agents/s04_voice_prompting.py agents/lab03_prompt.py
```

In `agents/lab03_prompt.py`, add the "before" prompt as a module-level constant:

```python
BEFORE_PROMPT = """You are MapleBot, a helpful assistant for Maple Street Dental.
... (paste the whole prompt) ...
"""
```

Find where the agent's `instructions=` argument is set (it is built with `build_instructions(...)` from `maple.prompts`) and temporarily replace it with `instructions=BEFORE_PROMPT`. Run:

```bash
uv run agents/lab03_prompt.py console
```

Use this **test script** and keep it for every run in this lab:

| # | Caller says | A good voice reply... |
|---|---|---|
| P1 | "What are your hours?" | One sentence, days and times as words |
| P2 | "What's your phone number?" | Reads digits in groups: "five one two, five five five, zero one zero zero" |
| P3 | "How much is a cleaning?" | Grounded or honest "I'm not sure"; never a guessed price |
| P4 | "Where do I get the new patient forms?" | No URL read aloud; offers a speakable alternative |
| P5 | "I want to book a cleaning next Tuesday afternoon." | Asks for **one** missing detail at a time |
| P6 | "My name is Siobhan Nguyen." | Confirms spelling of an unusual name |
| P7 | "Are you a real person?" | Discloses it is an AI assistant |
| P8 | "Should I take ibuprofen for my toothache?" | Declines medical advice, offers earliest appointment |

Listen for: markdown symbols spoken aloud ("asterisk asterisk"), a URL read letter by letter, long monologues, a question stacked on another question, and invented prices.

While you listen, copy each of Riley's replies (one per line) from the console transcript into `notes/lab-03-before.txt`.

> **Checkpoint 1:** `notes/lab-03-before.txt` holds eight replies, and you heard at least three voice problems.

---

## Step 2: Add an automatic voice lint

Create `labs/voice_lint.py` (standard library only):

```python
"""Lab 3: flag assistant replies that will sound bad when spoken aloud.

Usage: python labs/voice_lint.py notes/lab-03-replies.txt
The file holds one assistant reply per line.
"""
import re
import sys

MAX_SENTENCES = 2
MAX_WORDS = 35

CHECKS = {
    "markdown": re.compile(r"\*\*|__|`|^\s*#|^\s*[-*•]\s|^\s*\d+[.)]\s|\|", re.M),
    "url": re.compile(r"https?://|www\.|\b[\w-]+\.(?:com|org|net|example)\b", re.I),
    "emoji": re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]"),
    "digits": re.compile(r"\d"),
    "symbols": re.compile(r"[$%&@#/]"),
}


def lint(reply: str) -> list:
    problems = [name for name, pattern in CHECKS.items() if pattern.search(reply)]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", reply.strip()) if s]
    if len(sentences) > MAX_SENTENCES:
        problems.append(f"{len(sentences)} sentences")
    words = len(reply.split())
    if words > MAX_WORDS:
        problems.append(f"{words} words")
    if reply.count("?") > 1:
        problems.append("more than one question")
    return problems


def main(path: str) -> int:
    replies = [line.strip() for line in open(path, encoding="utf-8") if line.strip()]
    flagged = 0
    for number, reply in enumerate(replies, start=1):
        problems = lint(reply)
        flagged += bool(problems)
        status = "OK  " if not problems else "FLAG"
        print(f"{status} #{number}: {', '.join(problems) or '-'} | {reply[:60]}")
    avg_words = sum(len(r.split()) for r in replies) / max(len(replies), 1)
    print(f"\n{len(replies)} replies, {flagged} flagged, average {avg_words:.1f} words per reply")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

Run it on your "before" replies:

```bash
mkdir -p labs
uv run python labs/voice_lint.py notes/lab-03-before.txt
```

Expected (your replies will differ, but most should be flagged):

```text
FLAG #1: markdown, digits | **Our hours** are: - Monday to Friday: 8am-5pm ...
FLAG #2: digits, symbols | You can reach us at (512) 555-0100.
...
8 replies, 7 flagged, average 41.3 words per reply
```

The script exits with status 1 when anything is flagged, so you can later run it in CI.

> **Checkpoint 2:** the lint flags most "before" replies.

---

## Step 3: Write the voice-first prompt

Write your own prompt as `MY_PROMPT` in `agents/lab03_prompt.py`. Do **not** copy `build_instructions()` yet; the point is to practise. Use the anatomy from lecture 4.2 as headings:

1. **Identity and disclosure**: who Riley is, which clinic, that it is an AI assistant on a phone call.
2. **Goal**: what a successful call looks like.
3. **Style**: one or two short sentences per reply, one question at a time, warm but efficient.
4. **Output rules**: no markdown, lists, emojis or URLs; say numbers, times and dates as words; phone numbers in groups.
5. **Tools policy**: never state availability or prices without a tool result (tools arrive in Section 5, but write the rule now).
6. **Confirmation**: read back names, dates and times before committing; confirm spelling of unusual names.
7. **Grounding**: when unsure, say so and offer the front desk. Never guess.
8. **Safety**: no medical advice; emergencies to nine one one.
9. **Escalation**: when to offer a human.
10. **Speakable alternatives** for things that do not work by voice (forms, links).

Set `instructions=MY_PROMPT` and re-run the test script. Save the new replies to `notes/lab-03-after.txt` and lint them:

```bash
uv run agents/lab03_prompt.py console
uv run python labs/voice_lint.py notes/lab-03-after.txt
```

Target: **0 or 1 flagged** replies and an average under 25 words.

> **Checkpoint 3:** your "after" replies pass the lint (or you can justify any remaining flag).

---

## Step 4: Test the silence behaviour

`s04_voice_prompting.py` sets `user_away_timeout` on the `AgentSession` and listens for the `user_state_changed` event (lecture 4.4). With your prompt active:

1. Ask P5, then stay silent for 20 seconds.
2. Riley should check in once (the course uses `SILENCE_CHECK_IN` from `maple.prompts`: "Are you still there? Take your time, I'm here when you're ready.").
3. Stay silent again. After repeated silence Riley should say goodbye (`SILENCE_GOODBYE`) and end the session.

Record the timings you observed.

> **Checkpoint 4:** you heard the check-in and the graceful goodbye.

---

## Step 5: Compare with the instructor's prompt

Print the course's composed prompt:

```bash
uv run python -c "from maple.prompts import build_instructions; p = build_instructions(booking=True, knowledge=True); print(p); print(len(p.split()), 'words')"
```

Compare it with yours block by block. Note one thing yours does better and one thing you want to steal.

---

## Step 6: Score yourself

Copy the rubric into `notes/lab-03.md` and score your prompt honestly (0 = missing, 1 = partly, 2 = clearly done).

| # | Criterion | 0 | 1 | 2 |
|---|---|---|---|---|
| 1 | Identity and AI disclosure | Missing | Name only | Name, clinic, "AI assistant", phone context |
| 2 | Brevity rule | Missing | "Be concise" | Explicit "one or two short sentences" |
| 3 | One question at a time | Missing | Implied | Explicit, plus "then wait" |
| 4 | No markdown / lists / emojis / URLs | Missing | Some | All four named |
| 5 | Numbers, dates, times, phone numbers | Missing | "Spell out numbers" | Examples for dates, times and digit groups |
| 6 | Read-back and spelling confirmation | Missing | Mentioned | Read-back before any commit + spelling of names |
| 7 | Grounding and "I don't know" | Guessing allowed | "Don't guess" | Don't guess + what to offer instead |
| 8 | Safety (medical advice, emergencies) | Missing | One of the two | Both, with emergency wording |
| 9 | Escalation to a human | Missing | Vague | Clear triggers |
| 10 | Speakable alternatives for links/forms | URL kept | URL removed | Concrete spoken alternative |

**Passing:** 14/20. **Excellent:** 18+/20 and lint-clean replies.

> **Checkpoint 5:** `notes/lab-03.md` contains your score, before/after lint summaries and the silence timings.

---

## Stretch goal

Preview Section 9 by turning one rubric line into an automated behaviour test. Create `tests/agent/test_lab03_voice_style.py`:

```python
from lab03_prompt import MY_PROMPT  # agents/ is on the test path (pyproject.toml)
from livekit.agents import Agent, AgentSession


async def test_hours_answer_is_short_and_speakable(llm, judge_llm) -> None:
    async with AgentSession(llm=llm) as session:
        await session.start(Agent(instructions=MY_PROMPT))
        result = await session.run(user_input="What are your hours?")
        await result.expect.next_event().is_message(role="assistant").judge(
            judge_llm,
            intent="Answers in at most two short spoken sentences with no markdown, "
                   "no bullet points, no URLs and no digits.",
        )
```

The `llm` and `judge_llm` fixtures come from `tests/agent/conftest.py`, which also skips the test when `OPENAI_API_KEY` is missing.

Run it with `uv run pytest tests/agent/test_lab03_voice_style.py -v`. You will learn exactly how this works in lecture 9.3.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Riley still uses bullet points | Rule is buried at the end, or contradicted elsewhere | Put output rules near the top; remove every "use markdown" instruction; add "Never use..." with the exact items |
| Riley reads "five hundred twelve, five hundred fifty-five..." | Phone number stored in digits with no speaking rule | Give an explicit example of digit groups, or store the spoken form (see `CLINIC_PHONE_SPOKEN` in `maple.prompts`) |
| Replies are short but robotic | Over-constrained style | Add one line on warmth ("friendly, like a calm front-desk colleague"); allow brief acknowledgements |
| Riley asks for name, phone and reason in one breath | No one-question rule | "Ask only one question at a time, then stop and wait." |
| Invented prices | No grounding rule, or "best guess" left in | Remove "best guess"; require tool results for prices and availability |
| `voice_lint.py` flags "Dr." or "a.m." | Sentence splitter treats the period as sentence end | Acceptable noise; or prefer "doctor" and "in the morning", which also sound better |
| No silence check-in | `user_away_timeout` not set in your copied agent | Make sure you copied `s04_voice_prompting.py`, not `s03_hello_agent.py` |
| `ModuleNotFoundError: lab03_prompt` in the stretch test | pytest run from outside the repo root | Run `uv run pytest tests/agent/test_lab03_voice_style.py` from the repo root so `pyproject.toml`'s `pythonpath` applies |

---

## Solution notes

**Ten problems in the "before" prompt:** (1) markdown headers and bullets are read aloud or silently dropped; (2) "thoroughly" produces long monologues and more TTS latency; (3) tables of times are unspeakable, and more than three options overloads the caller's memory; (4) URLs are read character by character; (5) emojis are either read as words or dropped; (6) "$120-$180" becomes "dollar one hundred twenty dash..."; (7) "best guess" invites hallucinated prices and availability; (8) no AI disclosure; (9) the phone number is in digits with no grouping rule; (10) nothing about confirmation, escalation, safety or one-question-at-a-time.

**A model "after" prompt (about 230 words):**

```text
You are Riley, the AI receptionist for Maple Street Dental, a family dental clinic.
You are speaking with a caller on the phone; everything you say is turned into speech.
If asked, say plainly that you are an AI assistant.

Goal: answer clinic questions and help callers book, reschedule or cancel appointments.

Style: reply in one or two short sentences. Ask one question at a time, then wait.
Be warm and efficient, like a calm front-desk colleague.

Output: plain spoken sentences only. Never use markdown, lists, emojis or web addresses.
Say times and dates as words, for example "Tuesday, October sixth at two thirty in the afternoon".
Read phone numbers in groups: "five one two, five five five, zero one zero zero".
Say prices in words, for example "about one hundred twenty dollars".

Facts: only state prices, insurance details or availability that come from your tools.
If you are not sure, say so and offer to connect the caller with the front desk.

Forms: new patient forms are on the clinic website under "Forms"; offer to have the front desk email them.

Confirm: repeat names, dates and times back before booking anything. For unusual names, ask for the spelling.

Safety: you cannot give medical advice. For trouble breathing, facial swelling or heavy bleeding,
tell the caller to hang up and call nine one one.

Escalate: offer a person if the caller asks, is upset, or you cannot help after two tries.
```

This scores 19/20 on the rubric (tools policy is written before tools exist, so criterion 7 "what to offer instead" is only partly testable yet). Compare it with `maple.prompts.build_instructions(booking=True, knowledge=True)`, which splits the same ideas into reusable blocks (`IDENTITY`, `STYLE_RULES`, `OUTPUT_RULES`, `BOOKING_RULES`, `KNOWLEDGE_RULES`, `SAFETY_RULES`, `ESCALATION_RULES`) so later sections can add one block at a time.

Reference files: `03-code/src/maple/prompts.py`, `03-code/agents/s04_voice_prompting.py`.
