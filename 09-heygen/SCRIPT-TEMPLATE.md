# Script Template — AI Agent Testing & Evaluation

> Copy this template for every lecture. Fill in every field.
> Refer to `PRODUCTION-GUIDE.md` for tone rules, production rules, and the 7-beat structure.

---

## Blank Template

```
────────────────────────────────────────────────────────
LECTURE: <number> — <title>
MODULE: <module number and name>
TARGET: <mm:ss>
WORD COUNT: <target word count — 140 words per minute>
ONE IDEA: <one sentence — if you can't state it in one sentence, split the lecture>
────────────────────────────────────────────────────────

[SCENE 1 — HOOK] (0:00–0:12)
VISUAL: <what's on screen — failure screenshot, surprising stat, broken output>
SCRIPT:


[SCENE 2 — PROMISE / TITLE] (0:12–0:18)
ON-SCREEN: <lecture title>
SUBTEXT: By the end of this lecture, you'll be able to <concrete outcome>.
SCRIPT: (no voice — music sting only)


[SCENE 3 — CONTEXT] (0:18–0:xx)
VISUAL: <architecture diagram or context slide showing where this fits>
SCRIPT:


[SCENE 4 — TEACH · Point 1] (x:xx–x:xx)
SLIDE (max 12 words): <headline for the slide>
DIAGRAM DESCRIPTION: <what the diagram shows, for Figma/Canva creation>
SCRIPT:


[SCENE 5 — TEACH · Point 2] (x:xx–x:xx)
SLIDE (max 12 words): <headline for the slide>
DIAGRAM DESCRIPTION: <what the diagram shows, if applicable>
SCRIPT:


[SCENE 6 — SHOW / DEMO] (x:xx–x:xx)
SCREEN ACTION: <exactly what to show in the screen recording — commands, files, outputs>
SCRIPT (voice-over):


[SCENE 7 — RECAP] (x:xx–x:xx)
BULLET 1: <key takeaway — max 8 words>
BULLET 2: <key takeaway — max 8 words>
BULLET 3: <key takeaway — max 8 words>
SCRIPT:


[SCENE 8 — BRIDGE] (x:xx–x:xx)
NEXT-UP CARD: <next lecture title>
SCRIPT:

────────────────────────────────────────────────────────
```

---

## Checklist Before Submitting a Script

- [ ] ONE IDEA can be stated in a single sentence
- [ ] Hook opens with pain, surprise, or a provocative question — no greetings
- [ ] Promise states a concrete, measurable outcome
- [ ] Context anchors the idea in the course's bigger picture
- [ ] Teach covers 2–3 sub-points maximum
- [ ] Show includes a real demo with specific screen actions documented
- [ ] Recap has exactly 3 bullet points, each ≤8 words
- [ ] Bridge teases the next lecture by name
- [ ] Word count is within ±50 words of target
- [ ] No banned filler phrases (see PRODUCTION-GUIDE.md)
- [ ] A number or concrete example appears at least every 45 seconds of script
- [ ] No avatar segment runs longer than ~60 seconds of continuous speech without a visual change noted

---

## Gold Standard Example

> This is the quality bar. Every script should match this level of engagement, specificity, and pacing.

```
────────────────────────────────────────────────────────
LECTURE: 1.4 — The 6 Ways AI Agents Fail (And Why Testing Is Hard)
MODULE: 1 — Why AI Agent Testing Matters
TARGET: 6:00
WORD COUNT: ~840
ONE IDEA: AI agents fail in six distinct patterns that traditional testing completely misses.
────────────────────────────────────────────────────────

[SCENE 1 — HOOK] (0:00–0:15)
VISUAL: Screen recording — a customer-service chatbot confidently telling a user
they can return a laptop "within 400 days" instead of 14 days. Red circle around
the hallucinated number. The user replies "Great, thanks!" — believing every word.
SCRIPT:
This chatbot just told a customer they have four hundred days to return a laptop.
The real policy? Fourteen days. The customer believed it. Support never caught it.
And the worst part — every unit test on this agent was passing green.

[SCENE 2 — PROMISE / TITLE] (0:15–0:20)
ON-SCREEN: The 6 Ways AI Agents Fail (And Why Testing Is Hard)
SUBTEXT: By the end of this lecture, you'll be able to name the six failure
modes of AI agents and explain why standard software tests miss each one.
SCRIPT: (no voice — music sting only)

[SCENE 3 — CONTEXT] (0:20–0:55)
VISUAL: Course roadmap diagram. Module 1 highlighted. An arrow from "Failure Modes"
pointing forward to Modules 3–7 with labels: "You'll build defenses against every
one of these."
SCRIPT:
You're in Module 1 — the foundation. Before you can test anything, you need to
know what breaks. This lecture gives you the failure taxonomy. Every testing
technique you'll learn in Modules 3 through 7 maps back to one of these six
patterns. Think of this as your field guide to everything that goes wrong.

[SCENE 4 — TEACH · Point 1: Failures 1–3] (0:55–2:25)
SLIDE (max 12 words): Failure Modes 1–3: Wrong Answer, Wrong Action, Wrong Source
DIAGRAM DESCRIPTION: Three-column layout. Each column has an icon, the failure name,
and a one-line real example beneath it.
  Column 1 — "Hallucination" — brain icon with sparks — "Invents a return policy
  that doesn't exist"
  Column 2 — "Wrong Tool Call" — wrench icon with X — "Calls delete instead of
  archive on a user's files"
  Column 3 — "Grounding Failure" — broken chain icon — "Ignores retrieved docs,
  answers from training data instead"
SCRIPT:
Failure number one — hallucination. The agent generates something that sounds
right but is factually wrong. That return-policy example? Classic hallucination.
The model had no grounding, so it invented a number. Your users can't tell the
difference between a real answer and a confident lie.

Failure number two — wrong tool call. The agent picks the wrong action. Imagine
a file-management agent. A user says "clean up my old drafts." The agent calls
a delete function instead of archive. The data is gone. The reasoning looked
fine in the logs. The action was catastrophic.

Failure number three — grounding failure. You gave the agent a retrieval system.
It retrieved the right documents. And then it ignored them. It answered from its
training data instead of the context you provided. This one is subtle — the
retrieval pipeline looks healthy, but the generation step throws it all away.
Seventy percent of RAG failures fall into this category.

[SCENE 5 — TEACH · Point 2: Failures 4–6] (2:25–3:55)
SLIDE (max 12 words): Failure Modes 4–6: Loops, Drift, Boundary Violations
DIAGRAM DESCRIPTION: Three-column layout continuing the pattern.
  Column 4 — "Infinite Loop" — circular arrow icon — "Agent retries the same
  failing step 47 times"
  Column 5 — "Goal Drift" — wandering path icon — "Starts on billing, ends
  debugging unrelated code"
  Column 6 — "Boundary Violation" — shield with crack — "Shares PII, ignores
  role restrictions, bypasses guardrails"
SCRIPT:
Failure number four — infinite loops. The agent hits an error, retries, hits
the same error, retries again. Forty-seven times. Your token bill spikes. The
user stares at a spinner. Nothing useful happens. Multi-step agents are
especially prone to this — one bad tool response and the retry logic spirals.

Failure number five — goal drift. The agent starts on track. A user asks about
a billing charge. Three steps in, the agent is debugging an unrelated API
endpoint because one retrieval result mentioned it. By step eight, it's
summarizing documentation the user never asked about. Each individual step
looked reasonable. The trajectory as a whole made no sense.

Failure number six — boundary violations. The agent leaks PII in a response.
It ignores its system prompt restrictions. It executes a tool it was never
supposed to touch. These failures don't just break your product — they break
trust, compliance, and sometimes the law.

[SCENE 6 — SHOW / DEMO] (3:55–5:10)
SCREEN ACTION: Show a real agent trace in a terminal or trace viewer. The trace
shows a 5-step agent run. Step 1 — correct retrieval. Step 2 — correct reasoning.
Step 3 — wrong tool call (highlight in red). Step 4 — agent retries with the same
wrong tool. Step 5 — agent returns a hallucinated answer. Annotate each step on
screen as the voiceover walks through it.
SCRIPT (voice-over):
Let's look at a real trace. This is a five-step agent run from a support bot.

Step one — the agent retrieves the right knowledge-base article. So far, so good.
Step two — it reasons about the user's question correctly. Still on track.
Step three — here's where it breaks. It calls the order-cancellation endpoint
instead of the order-status endpoint. That's failure mode two — wrong tool call.
Step four — it notices something went wrong, retries — and calls the same wrong
endpoint again. Now we've added failure mode four — a loop.
Step five — backed into a corner, it gives up on the tool and just generates an
answer. That answer is a hallucination. Failure mode one.

Three failure modes in a single run. And here's the key insight: a unit test on
step one would pass. A unit test on step two would pass. You'd only catch this
by testing the full trajectory. That's why agent testing is fundamentally different
from testing traditional software.

[SCENE 7 — RECAP] (5:10–5:45)
BULLET 1: Six failure modes — know them all
BULLET 2: Failures compound across steps
BULLET 3: Unit tests miss trajectory-level failures
SCRIPT:
Here's what to lock in. First — there are six distinct ways agents fail:
hallucination, wrong tool call, grounding failure, infinite loops, goal drift,
and boundary violations. Second — these failures compound. One bad step triggers
another. A real agent run can hit three failure modes in five steps. Third —
traditional unit tests miss all of this. You need trajectory-level testing. And
that's exactly what this course teaches you to build.

[SCENE 8 — BRIDGE] (5:45–6:00)
NEXT-UP CARD: 1.5 — Traditional Testing vs. Agent Testing: What Changes
SCRIPT:
Next up — you'll see exactly how agent testing differs from the traditional
testing you already know. Same principles, completely different execution. See
you there.

────────────────────────────────────────────────────────
```

### Why This Script Works

| Quality Marker | Where It Appears |
|---|---|
| **Hook with pain** | Chatbot hallucination — real, visceral, specific |
| **No greeting** | Opens mid-action, not "Hi guys" |
| **Payoff before theory** | "400 days" disaster shown before any taxonomy |
| **Numbers every 45s** | "400 days," "14 days," "70%," "47 times," "three failure modes in five steps" |
| **Questions to camera** | Implicit via demo walkthrough: "here's where it breaks" |
| **Short sentences** | Average sentence length ~12 words |
| **One idea** | Six failure modes — single taxonomy, single concept |
| **Demo proves the concept** | Trace walkthrough shows failures compounding live |
| **Recap = 3 bullets** | Exactly three, each ≤8 words |
| **Bridge names next lecture** | Teases 1.5 by title |
| **~840 words** | Fits the 6-minute target at 140 wpm |
