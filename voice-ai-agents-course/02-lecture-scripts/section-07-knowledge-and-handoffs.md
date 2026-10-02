# Section 7: Knowledge and Multi-Agent Handoffs

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** about 56 minutes (8 lectures)
> **Running example:** Riley, the AI receptionist for Maple Street Dental
> **Production format:** HeyGen avatar for [AVATAR] segments; OBS screencast for [SCREEN], [CODE] and [DEMO] segments; slides built from the [SLIDE] cues.
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."

**Cue legend:** [AVATAR] avatar on camera · [SLIDE n: title] full-screen slide with the listed bullets · [SCREEN: ...] OBS recording · [CODE: ...] code on screen, exact code in the fenced block · [DEMO: ...] live run with audio · [B-ROLL] cutaway · [PAUSE] one-beat pause.

**Code names used in this section (matched to `03-code/`):** `KnowledgeRiley` (`agents/s07_knowledge_agent.py`, `KNOWLEDGE_MODE=tool|prefetch`, `LANGUAGE=en|es|hi`); `GreeterAgent`, `BookingAgent`, `BillingAgent`, `carry_over` (`agents/s07_multi_agent.py`); handoff tools `transfer_to_booking`, `transfer_to_billing`, `back_to_front_desk`; `KnowledgeToolsMixin.lookup_clinic_info`, `get_faq`, `BookingToolsMixin`, `CallState` (with `notes`), `create_session`, `build_stt`, `build_tts` (`agents/common.py`); `FaqIndex` / `SearchResult(title, answer, score)` (`src/maple/knowledge.py`); `build_instructions`, `GREETINGS`, `language_block`, `GREETER_EXTRA`, `BOOKING_SPECIALIST_EXTRA`, `BILLING_SPECIALIST_EXTRA` (`src/maple/prompts.py`). On screen, every agent is "Riley".
---

## Lecture 7.1: RAG for voice: short, speakable, grounded

| Field | Value |
|---|---|
| ID | 7.1 |
| Title | RAG for voice: short, speakable, grounded |
| Type | SL (slides + avatar) |
| Target duration | 7:00 (about 790 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Retrieval for a voice agent must be fast, return a spoken-length answer, and say "I don't know" instead of guessing. |
| Prerequisites | Section 4 (prompting for the ear), Section 5 (tools) |
| Files used | `src/maple/data/faq.md` (shown), `src/maple/prompts.py` (`KNOWLEDGE_RULES`) |

**Learning objectives**

1. Compare retrieval as a tool with pre-turn injection via `on_user_turn_completed`, including their latency costs.
2. Apply three voice rules to retrieved content: short, speakable, grounded.
3. Design "I don't know" behavior that hands off rather than hallucinates.

### Script

[AVATAR]

A caller asks Riley, "Do you take my Medicaid dental plan?" [PAUSE] Riley says, "Yes, we accept all major insurance plans." Sounds great. Except Maple Street Dental doesn't accept Medicaid or HMO dental plans. The caller books, shows up, and gets a bill for three hundred and forty dollars. That's not a model problem. That's a knowledge problem. Riley answered from what a language model thinks dental clinics usually do, not from what this clinic actually does.

In this section, we fix that with retrieval. But retrieval for voice isn't the same as retrieval for a chatbot.

[SLIDE 1: Chat RAG vs voice RAG]
- Chat: retrieve 5 chunks, write 3 paragraphs, add links
- Voice: retrieve 1 or 2 chunks, speak 1 or 2 sentences, no links
- Chat: a 2-second retrieval is fine
- Voice: every 100 ms of retrieval is dead air on the phone

[AVATAR]

In a chatbot, you retrieve five chunks, write three paragraphs and paste a link to the policy page. Nobody minds waiting two seconds, because there's a spinner. On a phone call, there's no spinner. There's silence. And after about a second of silence, callers start saying "Hello?" So voice RAG has three rules. Short. Speakable. Grounded.

[SLIDE 2: Rule 1: Short]
- Retrieve 1 or 2 small chunks, not 5 big ones
- Answer in 1 or 2 sentences
- Offer more: "Would you like the details on payment plans?"
- Long answers mean long TTS time and more interruptions

[AVATAR]

Short first. Retrieve one or two small chunks. Answer in one or two sentences. If there's more, offer it. "We accept most PPO plans. Would you like me to check yours specifically?" Long answers aren't just boring on the phone. They cost you. More output tokens, more TTS characters, and more chances for the caller to interrupt halfway through.

[SLIDE 3: Rule 2: Speakable]
- Store FAQ content the way a person would say it
- No tables, no bullet lists, no URLs in answers
- "$120 to $180" → "between a hundred twenty and a hundred eighty dollars"
- The prompt still converts, but clean sources convert better

[AVATAR]

Speakable. Your knowledge base was probably written for a website. It has tables, bullet points and links. None of that survives text-to-speech. Riley's prompt already says "no markdown, spell out numbers." That's the `OUTPUT_RULES` block in `prompts.py`. But the cleaner the source, the less the model has to rewrite on the fly. For Maple Street Dental, I wrote `faq.md` in short, plain paragraphs, one topic per heading.

[SCREEN: `src/maple/data/faq.md`, scroll through headings: Opening hours, Parking, Insurance accepted, Cancellation policy, Dental emergencies, Pricing ranges, Payment options and payment plans]

Here it is. Hours. Parking. Insurance. Cancellation policy. Each section is a few sentences a receptionist could read out loud.

[SLIDE 4: Rule 3: Grounded]
- Answer only from retrieved text
- Nothing relevant found → say so, then offer a message or a transfer
- Never guess prices, insurance coverage or clinical facts
- Grounding is a test target in Section 9

[AVATAR]

Grounded. This is the one that would have saved our Medicaid caller. Riley must answer only from what retrieval returns. If retrieval returns nothing useful, Riley says, "I'm not sure about that one. Would you like me to take a message for the front desk?" [PAUSE] "I don't know" is a feature. On a clinic phone line, a confident wrong answer about insurance is worse than no answer at all. And in Section 9, we'll write tests that fail if Riley ever invents a price.

[SLIDE 5: Two ways to wire retrieval]
- Retrieval as a tool: the LLM decides when to call `lookup_clinic_info`
- Pre-turn injection: `on_user_turn_completed` retrieves on every turn, adds context before the LLM runs
- Tool: no cost on turns that don't need it, but an extra LLM round trip when it does
- Injection: no extra round trip, but adds latency and tokens to every turn

[AVATAR]

Now the architecture question. There are two ways to wire retrieval into a LiveKit agent.

Option one: retrieval as a tool. You give Riley a `lookup_clinic_info` function tool. When the caller asks a clinic question, the model decides to call it, reads the result, and answers. The cost is an extra model round trip, maybe three to five hundred milliseconds. The upside is that on "I'd like to book a cleaning," nothing gets retrieved at all.

Option two: pre-turn injection. LiveKit agents have a hook called `on_user_turn_completed`. It runs after the caller finishes speaking and before the model generates a reply. You retrieve right there and add the results to the context for this turn.

[CODE: slide-size snippet, pre-turn injection (from `KnowledgeRiley` in `agents/s07_knowledge_agent.py`)]

```python
    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        """Pre-turn injection (lecture 7.1): add the best FAQ hit to this turn's context."""
        if not self.prefetch:
            return
        question = new_message.text_content or ""
        hits = get_faq().search(question, k=1)
        if hits:
            turn_ctx.add_message(
                role="assistant",
                content=f"Clinic information that may help answer the caller: {hits[0].answer}",
            )
```

[AVATAR]

No extra round trip. But you pay the retrieval time and the extra tokens on every single turn, including "yes," "no," and "Tuesday."

[SLIDE 6: Which one for Riley?]
- Small FAQ, fast keyword retriever, most turns are about booking → tool
- Large knowledge base, most turns are questions → injection (with a fast retriever)
- You can do both: inject cheap context, keep a tool for deep lookups
- Measure it: lecture 9.8 latency budget

[AVATAR]

So which one should Riley use? Most of Riley's turns are about booking. Clinic questions come up maybe one turn in five. So we'll use the tool approach, and the prompt will say exactly when to call it. If you're building an agent where almost every turn is a question, like a product support line, injection often wins. And you'll know for sure when you measure it against the latency budget in lecture 9.8.

[SLIDE 7: What "I don't know" should sound like]
- Bad: silence, or "I'm sorry, I cannot assist with that request."
- Bad: a confident guess ("Yes, we take all plans.")
- Good: "I'm not sure about that one. I can take a message for the front desk, or transfer you."
- Good answers are short: at about 150 spoken words a minute, a 60-word answer is 24 seconds of talking

[AVATAR]

One more slide. What should Riley actually say when the FAQ has nothing? This is the moment where voice agents feel either trustworthy or robotic. Silence is the worst answer. A canned "I cannot assist with that request" is the second worst. It sounds like a phone tree. The best answer admits the gap in plain words and offers a next step: a message for the front desk, or a transfer. That keeps the caller moving.

[B-ROLL: Two timer bars side by side: a sixty-word answer filling 24 seconds, and a two-sentence answer filling about 8 seconds, with a caller's "Hello?" bubble popping up halfway through the long one.]

And keep the numbers in mind. People speak at roughly a hundred and fifty words a minute, and TTS voices are similar. A sixty-word answer takes about twenty-four seconds to say. [PAUSE] On a phone, twenty-four seconds of one-way talking feels like forever, and it gives the caller plenty of time to interrupt. One or two sentences is about eight seconds. That's the target.

[SLIDE 8: "Can't the model just remember the FAQ?"]
- It has never seen this clinic's FAQ
- Without retrieval it copies what other clinics do
- Grounding: "right, or honestly unsure"

[AVATAR]

A question I get a lot: "Can't the model just remember the FAQ from its training?" No, and it's the core reason for this whole section. The model has never seen Maple Street Dental's parking garage or its list of insurance plans. When it answers without retrieval, it's pattern-matching from thousands of other clinics. Sometimes it's right. That's the dangerous part. [PAUSE] Grounding turns "sometimes right" into "right, or honestly unsure."

### Recap

[SLIDE 9: Recap]
- Short: one or two chunks, one or two sentences
- Speakable: clean sources, no tables or links
- Grounded: answer only from what was found

Voice RAG retrieves a little, speaks a little, answers only from what it found, and says "I don't know" when it found nothing.

### Transition

Next, we'll build Riley's retriever and its `lookup_clinic_info` tool, and make it admit when it doesn't know.

### Speaker notes: common mistakes and Q&A

- **"Why not stuff the whole FAQ into the system prompt?"** For a two-page FAQ that can work, but every turn pays for those tokens, answers get longer, and it doesn't scale. The tool pattern also gives you a measurable grounding test.
- **Injected context as `role="system"`**: some students add mid-conversation system messages. `role="assistant"` context notes, as in LiveKit's examples, are less disruptive for most models; either way, keep them short.
- **Web-formatted sources**: tables and links in the FAQ lead to Riley reading "pipe, pipe, dash" or URLs. Clean the source first.
- **Latency of `on_user_turn_completed`**: it blocks the reply. A slow vector search there adds directly to every turn's delay.

---

## Lecture 7.2: Code-along: FAQ lookup tool

| Field | Value |
|---|---|
| ID | 7.2 |
| Title | Code-along: FAQ lookup tool |
| Type | SC (screencast code-along) |
| Target duration | 10:00 (about 950 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | A tiny, dependency-free retriever plus one well-described tool gives Riley grounded, speakable answers. |
| Prerequisites | 7.1, Section 5 |
| Files used | `src/maple/knowledge.py`, `src/maple/data/faq.md`, `tests/unit/test_knowledge.py`, `agents/common.py` (`KnowledgeToolsMixin`, `get_faq`), `agents/s07_knowledge_agent.py` |

**Learning objectives**

1. Explain how `src/maple/knowledge.py` splits `faq.md` into sections and ranks them with BM25-lite and a title boost.
2. Implement the `lookup_clinic_info` function tool with a relevance threshold and a speakable "no match" result.
3. Verify grounded answers and "I'm not sure" behavior in console mode, in both tool and prefetch modes.

### Script

[AVATAR]

Ask Riley today whether the clinic takes Delta Dental, and it will guess. [PAUSE] Confidently. By the end of this lecture, it will answer from the clinic's own FAQ, or say it isn't sure. We'll do it in two layers, the same way we did the scheduler in Section 5. First, a pure-Python retriever with unit tests and no network. Then a thin tool that lets Riley call it.

[SCREEN: VS Code, `src/maple/knowledge.py`. Lower third with the API-verified note.]

Open `src/maple/knowledge.py`. It's already in the repo, so I'll walk through it rather than type it.

It does three things. One: it loads `data/faq.md` and splits it into sections, one per `##` heading. "Insurance accepted" is a section. "Parking" is a section. Small sections are what we want for voice.

[SCREEN: Scroll to `tokenize`, `_stem` and `FaqIndex.score`. Highlight the `title_boost` line.]

Two: it scores each section against the caller's question. It lowercases, strips punctuation, drops filler words like "the" and "do", trims simple word endings so "hours" matches "hour", and then uses a BM25-style score. BM25 is a classic search formula. It rewards sections that contain the rare words in your question, like "Delta" or "parking", more than common ones. It also gives a small bonus when a question word appears in the section title. No embeddings. No vector database. No API key.

[SCREEN: Scroll to `shorten`, then to `search` and `answer`.]

Three: it returns the top matches with a score, and trims each answer to at most three sentences, so it's already close to speakable.

[CODE: `src/maple/knowledge.py`, the public surface (simplified: bodies, docstrings and the `from_markdown`/`from_file` constructors left out; comments added)]

```python
@dataclass(frozen=True)
class SearchResult:
    title: str      # "Insurance accepted"
    answer: str     # first sentences of the section, trimmed for speech
    score: float


class FaqIndex:
    @classmethod
    def from_default(cls) -> FaqIndex: ...          # loads the packaged maple/data/faq.md

    def search(self, query: str, k: int = 2, *, min_score: float = 1.5,
               max_sentences: int = 3) -> list[SearchResult]: ...

    def answer(self, query: str, k: int = 2) -> str:
        """Return a single speakable string for a tool response, or "NO_MATCH"."""
```

Notice `min_score`. Anything scoring below one point five is dropped, so an off-topic question returns an empty list. And `answer` wraps `search` for tools: it joins the top sections into one string, or returns the exact text `NO_MATCH` when nothing is relevant. That's the grounding rule from lecture 7.1, built into the retriever.

Why so simple? Because Maple Street Dental's FAQ is about two pages. A keyword retriever over two pages answers in well under a millisecond. An embedding call to a hosted API takes fifty to two hundred milliseconds before the search even starts. For a small knowledge base, simple is faster and more predictable. Lecture 7.3 covers when to upgrade.

Let's prove it works before any agent touches it.

[SCREEN: terminal]

```bash
uv run pytest tests/unit/test_knowledge.py -q
```

[DEMO: tests pass in about 0.1 seconds.]

All green, in about a tenth of a second. Those tests check things like "a question about parking returns the parking section first" and "an off-topic question returns nothing." Grounding, enforced in plain Python.

Now the tool. Like the booking tools, it lives in `agents/common.py`, on a mixin, so every Riley from here on can reuse it.

[CODE: `agents/common.py`, `get_faq` and `KnowledgeToolsMixin` (excerpt; `...` marks code left out)]

```python
_FAQ: FaqIndex | None = None
...

def get_faq() -> FaqIndex:
    """Return the process-wide FAQ index over ``src/maple/data/faq.md``."""
    global _FAQ
    if _FAQ is None:
        _FAQ = FaqIndex.from_default()
    return _FAQ

...

class KnowledgeToolsMixin:
    """Adds ``lookup_clinic_info`` backed by :class:`maple.knowledge.FaqIndex`."""

    @function_tool
    async def lookup_clinic_info(self, context: RunContext[CallState], question: str) -> str:
        """Look up clinic facts: hours, address, parking, insurance, prices, payment plans,
        policies, services, accessibility, languages and emergencies.

        Args:
            question: The caller's question in plain words.
        """
        answer = get_faq().answer(question, k=2)
        if answer == "NO_MATCH":
            # The FAQ-miss log (lectures 7.2-7.3): questions the FAQ could not answer.
            # Redacted because callers sometimes say names or numbers (Section 11).
            logger.info("faq_miss: %s", redact(question))
            return (
                "No matching clinic information. Say you're not sure and offer to take a message "
                "or transfer the caller to the front desk."
            )
        return f"Answer only from this, in one or two sentences:\n{answer}"
```

Let's read this carefully, because every line is a voice decision.

`get_faq` builds the index once per process and reuses it. Building it inside the tool would re-read and re-index the file on every question.

[SCREEN: Highlight the docstring's topic list.]

The docstring. The model reads it to decide when to call the tool. So it lists the topics explicitly: hours, address, parking, insurance, prices. Vague descriptions like "gets info" lead to tools that never get called.

The `question` argument. We ask for the caller's question in plain words, not keywords. Models are bad at guessing keywords for your retriever. They're good at passing the question along.

`k=2`. Two sections at most. Short.

[SCREEN: Highlight the `NO_MATCH` branch: the `faq_miss` log line, then the two returned instructions.]

The no-match path. We don't return an empty string. We return an instruction the model can act on: say you're not sure, offer a message or a transfer. An empty tool result is an invitation to improvise. [PAUSE] And a hit comes back with its own instruction attached: "Answer only from this, in one or two sentences." The tool result reinforces the prompt.

One more line on a miss: the tool logs the question as `faq_miss`, with any names or numbers redacted. That's your FAQ-miss log. Which questions did the FAQ fail? Lecture 7.3 uses exactly that to decide when keyword search stops being enough.

The prompt side is already done. `build_instructions(knowledge=True)` adds the `KNOWLEDGE_RULES` block from `prompts.py`: call `lookup_clinic_info` for clinic questions, answer only from what it returns, and never guess prices or coverage.

[SCREEN: `agents/s07_knowledge_agent.py`]

Now the agent file.

[CODE: `agents/s07_knowledge_agent.py`, the agent]

```python
class KnowledgeRiley(KnowledgeToolsMixin, Agent):
    """Riley with the ``lookup_clinic_info`` tool.

    Args:
        language: ``en``, ``es`` or ``hi``.
        prefetch: Inject FAQ context before each LLM turn instead of relying on the tool.
        extra: Extra prompt text, e.g. ``FOLLOW_CALLER_RULES`` (lecture 7.8).
    """

    def __init__(self, *, language: str = "en", prefetch: bool = False, extra: str = "") -> None:
        self.language = language
        self.prefetch = prefetch
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, language=language, extra=extra
            ),
        )

    async def on_enter(self) -> None:
        """Greet in the caller's language."""
        self.session.say(prompts.GREETINGS.get(self.language, prompts.GREETING))

    async def on_user_turn_completed(self, turn_ctx: ChatContext, new_message: ChatMessage) -> None:
        """Pre-turn injection (lecture 7.1): add the best FAQ hit to this turn's context."""
        if not self.prefetch:
            return
        question = new_message.text_content or ""
        hits = get_faq().search(question, k=1)
        if hits:
            turn_ctx.add_message(
                role="assistant",
                content=f"Clinic information that may help answer the caller: {hits[0].answer}",
            )
```

`KnowledgeRiley` mixes in only `KnowledgeToolsMixin`. It's deliberately a knowledge-only agent, so you can see retrieval on its own. In Section 8, `PhoneRiley` combines booking, knowledge and telephony tools in one class.

It supports both wiring styles from lecture 7.1. By default, the tool style: the model decides when to call `lookup_clinic_info`. With `prefetch=True`, `on_user_turn_completed` runs after every caller turn, searches for the single best section, and adds it to this turn's context before the LLM runs. The `language` and `extra` arguments are for lecture 7.8; ignore them for now.

[CODE: the entrypoint (excerpt: the code after `return` is the lecture 7.8 extension)]

```python
@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start the knowledge agent in the configured language."""
    settings = get_settings()
    prefetch = os.getenv("KNOWLEDGE_MODE", "tool").lower() == "prefetch"
    follow = os.getenv("FOLLOW_CALLER_LANGUAGE", "0") == "1"
    logger.info("language=%s prefetch=%s follow_caller_language=%s", settings.language, prefetch, follow)
    if not follow:
        session = create_session(settings, proc=ctx.proc, userdata=CallState())
        await session.start(
            agent=KnowledgeRiley(language=settings.language, prefetch=prefetch), room=ctx.room
        )
        return
    ...
```

`KNOWLEDGE_MODE` picks the style: `tool` or `prefetch`. `create_session` builds the same cascaded pipeline as every other agent. The `follow` flag is lecture 7.8's, so leave it off for now. Run it.

[SCREEN: terminal]

```bash
uv run python agents/s07_knowledge_agent.py console
```

[DEMO: Ask "Where do I park?" Riley calls `lookup_clinic_info`, answers in one sentence about the free Maple Commons garage behind the building, with validation. Ask "Do you take Delta Dental?" Riley answers from the "Insurance accepted" section: in network. Ask "What about Medicaid?" Riley says the clinic doesn't accept Medicaid dental plans. Ask "Do you do Botox?" Riley says it's not sure and offers to take a message, and the log shows a `faq_miss` line.]

"Where do I park?" Watch the log. There's the tool call, with the question in the caller's words. And the answer is one sentence: the free garage behind the building, validated for two hours. Perfect for the phone.

"Do you take Delta Dental?" Yes, in network, straight from the FAQ. "What about Medicaid?" [PAUSE] No. That's the answer our opening caller from lecture 7.1 needed, and it came from the clinic's own words, not from general knowledge.

And the important one. "Do you do Botox?" Nothing in the FAQ scores above the threshold, the tool returns its no-match instruction, and Riley says it's not sure and offers to take a message. And there's the `faq_miss` line in the log. That's grounding working.

Now try prefetch mode.

```bash
KNOWLEDGE_MODE=prefetch uv run python agents/s07_knowledge_agent.py console
```

[DEMO: ask "What time do you close on Friday?" No tool call appears in the log; Riley answers "two in the afternoon" directly, noticeably faster.]

Same question, no tool call in the log, and the answer lands a little sooner, because there's no extra model round trip. The trade-off from lecture 7.1, in action.

[AVATAR]

Two layers again. A retriever you can unit-test in a tenth of a second, and a tool whose docstring, argument and "no match" message are all written for a voice conversation.

### Recap

[SLIDE 1: Recap]
- A pure-Python retriever, unit-tested, no network
- One well-described tool: `lookup_clinic_info`
- No match: say "not sure", log the miss

`FaqIndex` finds the best one or two FAQ sections with no network calls, and `lookup_clinic_info` on `KnowledgeToolsMixin` turns them into grounded, speakable answers or an honest "I'm not sure."

### Transition

Two pages of FAQ is easy. Next, let's talk about what changes when the knowledge base is two thousand pages.

### Speaker notes: common mistakes and Q&A

- **Tool never called**: the docstring is vague ("Get information"). List topics explicitly and keep the rule in the prompt.
- **Empty string on a miss**: the model improvises. Always return an explicit no-match instruction.
- **Index built inside the tool**: re-reads and re-indexes the file every call. Use `get_faq()` (built once per process).
- **Lowering `min_score` to 0 so "everything gets an answer"**: that's how off-topic questions get confidently wrong answers. Tune it with the unit tests, not by feel.
- **"Why can't KnowledgeRiley book?"** By design: one concept per file. `PhoneRiley` (Section 8) and `ObservedRiley` (Section 10) combine the mixins.

---

## Lecture 7.3: Scaling knowledge: vector stores and latency

| Field | Value |
|---|---|
| ID | 7.3 |
| Title | Scaling knowledge: vector stores and latency |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 690 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Upgrade to embeddings and a vector store only when the knowledge base demands it, and hide the added latency with caching and pre-fetch. |
| Prerequisites | 7.1, 7.2 |
| Files used | `03-code/src/maple/knowledge.py` (timed with `timeit`), the `faq_miss` log line from `lookup_clinic_info` (7.2) |

**Learning objectives**

1. Decide when a keyword retriever is no longer enough and a vector store is justified.
2. Break down retrieval latency (embedding, search, rerank) against the voice latency budget.
3. Apply caching, pre-fetch on turn completion, and filler speech to hide retrieval time.

### Script

[AVATAR]

Here's a question I get a lot. "Shouldn't Riley be using a vector database?" [PAUSE] My honest answer: not yet. And maybe never. Let's talk about when you actually need one, and what it costs you in milliseconds.

[SLIDE 1: Signs you've outgrown keyword search]
- Hundreds of documents, not a two-page FAQ
- Callers use different words from your docs: "cleaning" vs "prophylaxis", "numbing" vs "local anesthetic"
- Multiple locations, providers or insurance plans with overlapping text
- Your FAQ-miss log is full of questions the docs actually answer

[AVATAR]

Here are the signs. You have hundreds of documents, not two pages. Callers use different words from your docs. A caller says "numbing shot," and your document says "local anesthetic." Keyword search misses that. Embeddings catch it, because they match meaning, not spelling. And the best signal of all: your "faq miss" log from the last lecture is full of questions your documents actually answer. That's the data that justifies the upgrade.

[SLIDE 2: Where retrieval time goes]
- Embed the question: 50 to 200 ms (hosted API), 5 to 20 ms (local model)
- Vector search: 5 to 50 ms (in-memory or managed)
- Optional rerank: 100 to 300 ms
- Budget reminder: whole turn should be under about 1,000 ms

[AVATAR]

Now the cost. A hosted embedding API call takes somewhere between fifty and two hundred milliseconds. The vector search itself is usually fast, five to fifty. If you add a reranker, that's another hundred to three hundred. So a fancy retrieval stack can eat four hundred milliseconds. Remember lecture 1.4. Our whole turn budget is about a second. Retrieval can't take half of it.

[SCREEN: Terminal in the course repo. Time the course's keyword retriever on one question.]

```bash
uv run python -m timeit -s "from maple.knowledge import FaqIndex; i = FaqIndex.from_default()" "i.search('where do I park')"
```

[DEMO: Output, for example `5000 loops, best of 5: 70.6 usec per loop`. Your number will differ.]

Now compare our own retriever. About seventy microseconds per search on my laptop. That's under a tenth of a millisecond. So what does an upgrade really cost? Every number on that slide, on every single lookup.

[SLIDE 3: Hiding retrieval latency]
- Cache: frequent questions (hours, parking) answered from a warm cache
- Pre-fetch: start retrieval in `on_user_turn_completed`, before the LLM runs
- Filler: `context.with_filler("Let me check that for you.", delay=0.5)`
- Prewarm: load indexes and models once per process with `setup_fnc`

[AVATAR]

Four ways to hide it. First, cache. On a clinic line, maybe twenty questions make up eighty percent of calls. Hours. Parking. Insurance. Cache those answers and skip retrieval entirely.

Second, pre-fetch. Start retrieval in `on_user_turn_completed`, the hook from lecture 7.1, as soon as the caller stops talking. The LLM hasn't even started yet, so the search runs in parallel with thinking time you'd spend anyway.

Third, filler speech. You already know this one from lecture 5.5. If a lookup takes more than half a second, Riley says "Let me check that for you," and the silence disappears.

Fourth, prewarm. Load your index and any local embedding model once, when the agent process starts, using the `setup_fnc` on `AgentServer`. Never load them inside a call.

[SLIDE 4: Keeping answers speakable at scale]
- Chunk by topic, 100 to 300 words, not by fixed character count
- Store a "spoken summary" field per chunk
- Include metadata filters: location, provider, plan
- Always keep the NO_MATCH path and the miss log

[AVATAR]

And don't lose the voice rules as you scale. Chunk by topic, not by fixed character count. A great trick is to store a short spoken summary alongside each chunk, written for the ear. The tool returns the summary first. Use metadata filters so the Downtown location's hours never leak into the Northside answer. And keep the "no match" path and the miss log. They matter even more when the knowledge base is too big to read yourself.

[SLIDE 5: Decision for Riley]
- Two-page FAQ → keyword retriever stays
- Re-evaluate when: more than 50 documents, or FAQ misses above 10% of lookups
- Swap is invisible to the agent: same `lookup_clinic_info` signature

[AVATAR]

For Riley, the keyword retriever stays. So what would change my mind? I've written down when we'd revisit it: more than fifty documents, or FAQ misses above ten percent of lookups. And here's the nice part of the design. If we swap in a vector store later, the tool's name and signature don't change. The agent doesn't know. The tests from Section 9 keep passing, or they tell us exactly what broke.

[SLIDE 6: A worked example]
- Maple Street Dental opens 4 more locations: 300 documents, per-location hours and dentists
- Keyword FAQ misses rise to 18 percent of lookups
- Option: local embedding model (prewarmed) + in-memory vector index + metadata filter by location
- Measured budget: embed 12 ms + search 6 ms + no rerank = about 20 ms per lookup

[AVATAR]

Let's make it concrete. Imagine Maple Street Dental grows to five locations. The knowledge base goes from two pages to three hundred documents: different hours, different dentists, different parking. And our miss log shows eighteen percent of lookups finding nothing, even though the answers exist. That's our signal.

[B-ROLL: Diagram builds left to right: caller question → local embedding model (prewarmed) → in-memory vector index → "location = Northside" filter → top chunk → `lookup_clinic_info` result. Timing labels appear: 12 ms, 6 ms, no rerank.]

So we'd upgrade, carefully. A small local embedding model, loaded once in `prewarm`, so there's no network hop. An in-memory vector index, because three hundred documents fit easily in memory. A metadata filter on location, so the Northside caller never hears Downtown's hours. And no reranker, because we measured and didn't need one. [PAUSE] About twenty milliseconds per lookup, measured, not guessed. The tool keeps its name, `lookup_clinic_info`, and its tests from Section 9 tell us whether answers got better or worse. That's what "upgrade when the data says so" looks like.

[SLIDE 7: Vector search always returns something]
- Keyword search for "Botox": no match (good)
- Vector search: the nearest section, with a low score
- Keep a similarity threshold and the no-match path

[AVATAR]

And one caution about vector search specifically: it always returns something. A keyword search for "Botox" in our FAQ returns nothing, which is exactly what we want. A vector search returns the closest section, maybe "Services offered," with a low similarity score. [PAUSE] So when you upgrade, keep a similarity threshold and keep the no-match path. Otherwise the upgrade quietly brings back the hallucinations that retrieval was supposed to remove.

### Recap

[SLIDE 8: Recap]
- Upgrade when your data and miss logs say so
- Retrieval time comes out of the turn budget
- Hide it: cache, pre-fetch, filler, prewarm

Move to embeddings and a vector store when your data and miss logs say so, and protect the latency budget with caching, pre-fetch, filler and prewarm.

### Transition

So far, one agent does everything. Next, we'll look at why and when to split Riley into a team of specialists.

### Speaker notes: common mistakes and Q&A

- **Choosing a vector DB first, measuring never.** Ask for the miss rate and latency numbers before approving the upgrade.
- **Embedding the whole conversation instead of the question.** Embed the latest caller turn (optionally with one prior turn), not the full transcript.
- **Loading an embedding model per call.** It can add seconds. Use `AgentServer(setup_fnc=prewarm)` and store it on `proc.userdata`.
- **Caching answers that change**, like holiday hours. Put a short TTL on cached answers.

---

## Lecture 7.4: Why split one agent into several

| Field | Value |
|---|---|
| ID | 7.4 |
| Title | Why split one agent into several |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (about 670 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Split an agent when prompt size, tool confusion or distinct personas hurt quality, and accept the cost of handoff latency and shared state. |
| Prerequisites | 7.2 |
| Files used | Diagram: Greeter → Booking / Billing handoff graph. `03-code/src/maple/prompts.py` (`build_instructions`, prompt-size check). |

**Learning objectives**

1. Identify three signals that a single voice agent should be split: prompt size, tool confusion and persona conflict.
2. Weigh the costs of handoffs: extra turns, lost context and harder testing.
3. Sketch Riley's Greeter → Booking → Billing handoff graph with shared userdata.

### Script

[AVATAR]

Riley now has six tools and a system prompt that's grown a lot since Section 3. Booking rules. Knowledge rules. Safety rules. Escalation rules. [PAUSE] Every time we add a feature, the prompt grows and every call pays for it. At some point, one agent doing everything becomes one agent doing everything slightly worse.

[SLIDE 1: Three signals it's time to split]
- Prompt size: instructions over roughly 1,500 to 2,000 tokens, slower first token
- Tool confusion: wrong tool picked when tools overlap (for example "reschedule" vs "cancel" vs "billing dispute")
- Persona conflict: one agent asked to be both quick and chatty, strict and flexible

[AVATAR]

Signal one: prompt size. Every turn sends the whole system prompt to the model. More tokens means a slower first token and a higher bill. When your instructions pass about fifteen hundred to two thousand tokens, you'll usually see it in the metrics.

[SCREEN: Terminal in the course repo. Measure Riley's biggest prompt so far, with every block switched on.]

```bash
uv run python -c "from maple.prompts import build_instructions; p = build_instructions(booking=True, knowledge=True, security=True); print(len(p.split()), 'words,', len(p), 'characters')"
```

[DEMO: Output]
```text
671 words, 3976 characters
```

So where's Riley today? With every block on, including the security rules from Section eleven, about six hundred and seventy words. That's well under fifteen hundred tokens. By prompt size alone, Riley doesn't need to split yet.

Signal two: tool confusion. With ten tools that sound alike, models pick the wrong one more often. A caller says "I need to sort out my appointment payment," and the model reaches for `reschedule_appointment`. Fewer tools per agent means fewer wrong picks.

Signal three: persona conflict. The greeter should be quick and warm. The billing specialist should be careful and precise about money. Asking one prompt to be both makes it mediocre at each.

[SLIDE 2: What a handoff costs you]
- A tool call and a new agent's `on_enter`: often 300 to 800 ms of extra silence
- Context loss unless you pass chat history
- State must live somewhere shared: `userdata`
- More paths to test (Section 9: `is_agent_handoff`)

[AVATAR]

Now the costs, because splitting isn't free. A handoff is a tool call, followed by the new agent starting up and speaking. That can add three to eight hundred milliseconds of silence. If you don't pass the conversation history, the new agent asks "How can I help you?" and the caller has to repeat themselves. That's the fastest way to make a caller hate your system. [PAUSE] Anything the next agent needs, like the caller's name, must live in shared state. And every handoff is a new path you have to test.

[SLIDE 3: Riley's team]
- GreeterAgent: greets, answers FAQ, routes (tools: `lookup_clinic_info`, hand-offs)
- BookingAgent: book, reschedule, cancel (4 booking tools)
- BillingAgent: insurance, payments, prices (FAQ tool, transfer for balances)
- Shared: `CallState` userdata: name, phone, appointment, handoff history

[B-ROLL: animated graph. Greeter in the center, arrows to Booking and Billing, and arrows back to Greeter. A "CallState" box underneath all three with a dotted line to each.]

[AVATAR]

Here's the team we'll build. The Greeter says hello, answers quick FAQ questions, and routes. The Booking agent owns the four appointment tools. The Billing agent handles insurance, payments and prices. Each agent can hand back to the Greeter. And all three share one `CallState` object, so a name collected by the Greeter is already known to Booking.

[SLIDE 4: Handoff vs one agent: decision checklist]
- Under 6 tools and one persona → keep one agent
- Distinct domains with separate tools → split
- Need different models or voices per step → split (per-agent `llm`, `tts` overrides)
- Latency-critical, single-purpose call → keep one agent

[AVATAR]

A simple checklist. Fewer than about six tools and one persona? Keep one agent. Distinct domains with their own tools? Split. Need a different model or voice for one step, like a cheaper model for the greeter? Split, because each LiveKit `Agent` can override the session's `llm` and `tts`. And for a short, latency-critical call that does one thing, keep one agent.

To be honest, Riley doesn't need to split for prompt size; you just measured that. We're splitting it partly because it's a pattern you'll need on bigger projects, and partly because the billing domain is growing. And in Section 9, the tests will tell us whether it was worth it.

[SLIDE 5: Alternatives to splitting]
- Update the tool list mid-call: `Agent.update_tools(...)`
- Update the instructions mid-call: `Agent.update_instructions(...)`
- Modular prompts: `build_instructions(booking=..., knowledge=...)` only includes what's needed
- Split only when these stop being enough

[AVATAR]

Before you split, know that there are lighter options. A LiveKit `Agent` can change its own tools during a call with `update_tools`, and its own instructions with `update_instructions`. So one agent can start with just the FAQ tool and gain the booking tools once the caller says "appointment." And our `build_instructions` function already builds Riley's prompt from blocks, so an agent that doesn't book doesn't pay for the booking rules.

Those techniques keep one agent small without the cost of handoffs. [PAUSE] Split when the personas really differ, when you want different models or voices per step, or when the prompt is still too big after trimming. Splitting is a choice, not a default, and in Section 9 we'll write tests that tell us whether it paid off.

[SLIDE 6: Tools by persona: a quick test]
- List every tool and the persona that uses it
- One persona owns them all: one agent
- Clean groups: a team; a messy split: modular prompts

[AVATAR]

Here's a quick way to decide for your own agent. Write down every tool, and next to each one, the persona that should use it. If one persona owns all the tools, you have one agent. If the list splits cleanly into two or three groups, with different tones and different rules, you have a team. [PAUSE] If it splits messily, with tools that everyone needs, keep one agent and use modular prompts. Messy splits create more handoffs than they save.

### Recap

[SLIDE 7: Recap]
- Split for prompt size, tool confusion or personas
- Handoffs cost silence, context and tests
- Try `update_tools` and modular prompts first

Split a voice agent when prompt size, tool confusion or conflicting personas hurt quality, and pay for it with fast handoffs, shared userdata and carried-over context.

### Transition

Next, let's build Riley's team: Greeter, Booking and Billing, with handoffs that don't make callers repeat themselves.

### Speaker notes: common mistakes and Q&A

- **Splitting too early.** Two agents with two tools each are harder to test than one agent with four tools.
- **Similar tool names.** The repo uses `transfer_to_booking` / `transfer_to_billing` for AI specialists and `transfer_to_human` (Section 8) for a person. Distinct docstrings keep them apart; test the routing (9.4).
- **"Can each agent have a different voice?"** Yes, pass `tts=` to that `Agent`. But for one clinic, a single consistent voice usually sounds more trustworthy.
- **Token numbers are rules of thumb.** Measure TTFT with Section 10's metrics before and after splitting.

---

## Lecture 7.5: Code-along: Greeter → Booking → Billing

| Field | Value |
|---|---|
| ID | 7.5 |
| Title | Code-along: Greeter → Booking → Billing |
| Type | SC (screencast code-along) |
| Target duration | 12:00 (about 950 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | A tool that returns another `Agent` performs a handoff; shared userdata and a copied chat context keep the caller from repeating themselves. |
| Prerequisites | 7.2, 7.4 |
| Files used | `agents/s07_multi_agent.py`, `agents/common.py` (`BookingToolsMixin`, `KnowledgeToolsMixin`, `CallState`, `create_session`), `src/maple/prompts.py` (`GREETER_EXTRA`, `BOOKING_SPECIALIST_EXTRA`, `BILLING_SPECIALIST_EXTRA`) |

**Learning objectives**

1. Implement handoff tools that return another `Agent` instance, with a message, and the recent chat context.
2. Use per-agent `on_enter` to greet once, pick up mid-conversation, and welcome callers back.
3. Share caller details and a handoff trail across agents with the `CallState` userdata.

### Script

[AVATAR]

"Sorry, can I have your name again?" [PAUSE] Nothing makes a transferred caller hang up faster. By the end of this lecture, a caller will reach the Greeter, get handed to Booking, book a cleaning, go back to the front desk, get handed to Billing to ask about insurance, and never repeat their name once.

[SCREEN: VS Code, `agents/s07_multi_agent.py`. Lower third with the API-verified note.]

Open `agents/s07_multi_agent.py`. Imports first.

[CODE: step 1: imports]

```python
from __future__ import annotations

from livekit.agents import Agent, AgentServer, ChatContext, JobContext, RunContext, cli, function_tool

from common import (
    BookingToolsMixin,
    CallState,
    KnowledgeToolsMixin,
    clinic_today,
    create_session,
    get_scheduler,
    get_settings,
    prewarm,
)
from maple import prompts
from maple.scheduler import ClinicScheduler
```

We reuse a lot. `BookingToolsMixin` gives the booking specialist its four tools. `KnowledgeToolsMixin` gives the greeter and billing specialist the FAQ tool. `CallState` is the shared userdata. And the three role descriptions are already written in `prompts.py`: `GREETER_EXTRA`, `BOOKING_SPECIALIST_EXTRA` and `BILLING_SPECIALIST_EXTRA`.

Now the one detail that makes or breaks handoffs: context.

[CODE: step 2: carrying the conversation over]

```python
MAX_CARRIED_ITEMS = 12


def carry_over(agent: Agent) -> ChatContext:
    """Copy the recent conversation for the next agent, without the old instructions."""
    return agent.chat_ctx.copy(exclude_instructions=True).truncate(max_items=MAX_CARRIED_ITEMS)
```

When we switch agents, we pass the conversation so far, with two edits. `exclude_instructions=True` drops the previous agent's system prompt, because the new agent brings its own. And `truncate(max_items=12)` keeps only the last twelve items. The specialist needs to know what the caller just asked. It doesn't need the whole call, and every extra item costs tokens and time on every turn.

Now the Greeter.

[CODE: step 3: GreeterAgent]

```python
class GreeterAgent(KnowledgeToolsMixin, Agent):
    """Front desk: answers simple questions and routes to specialists."""

    def __init__(self, *, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, extra=prompts.GREETER_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Greet on the first visit; welcome back when returning from a specialist."""
        if self.chat_ctx.items:
            self.session.generate_reply(instructions="Ask if there is anything else you can help with.")
        else:
            self.session.say(prompts.GREETING)

    @function_tool
    async def transfer_to_booking(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Hand the caller to the booking specialist for new appointments, rescheduling or
        cancellations."""
        context.userdata.notes.append("handoff: greeter -> booking")
        return BookingAgent(chat_ctx=carry_over(self)), "Transferring to the booking specialist."

    @function_tool
    async def transfer_to_billing(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Hand the caller to the billing specialist for insurance, payment plans, prices or
        bills."""
        context.userdata.notes.append("handoff: greeter -> billing")
        return BillingAgent(chat_ctx=carry_over(self)), "Transferring to the billing specialist."
```

Three things to notice.

[SCREEN: Highlight `GreeterAgent.on_enter` and its `if self.chat_ctx.items:` branch.]

First, `on_enter`. Every LiveKit `Agent` gets this hook when it becomes the active agent. The Greeter checks whether it already has conversation items. If not, it's the start of the call, so it says the fixed greeting with the AI disclosure. If yes, the caller has come back from a specialist, so it just asks if there's anything else. No second "Thanks for calling Maple Street Dental."

[SCREEN: Highlight `return BookingAgent(chat_ctx=carry_over(self)), "Transferring to the booking specialist."`]

Second, the handoff tools. The whole trick is the return value. [PAUSE] When a function tool returns an `Agent`, LiveKit switches the session to that agent. That's the handoff. Here we return a tuple: the new agent, plus a short message. The message becomes the tool's result in the conversation history, so the specialist can see why it was called. You can also return the agent on its own when there's nothing to say.

[SCREEN: Highlight the two handoff docstrings, side by side.]

Third, the names. `transfer_to_booking` and `transfer_to_billing` move the caller between AI specialists. In Section 8 we'll add `transfer_to_human`, which moves the caller to a real person on the phone. The docstrings are what keep them apart: "booking specialist" and "billing specialist" versus "a person at the front desk." When tools share a verb, the docstrings have to do the work.

We also append a note to `context.userdata.notes`: "handoff: greeter -> booking." `notes` is a list on `CallState`. It's handy in logs now, and in Section 9 we'll assert on it.

Now the Booking agent. This is where reuse pays off.

[CODE: step 4: BookingAgent]

```python
class BookingAgent(BookingToolsMixin, Agent):
    """Booking specialist with the four booking tools."""

    def __init__(
        self, *, chat_ctx: ChatContext | None = None, scheduler: ClinicScheduler | None = None
    ) -> None:
        self.scheduler = scheduler or get_scheduler()
        super().__init__(
            instructions=prompts.build_instructions(
                today=self.scheduler.today, booking=True, extra=prompts.BOOKING_SPECIALIST_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Pick up where the greeter left off, using what we already know."""
        name = self.session.userdata.caller_name
        hint = f" The caller's name is {name}." if name else ""
        self.session.generate_reply(
            instructions="Briefly say you can help with appointments and continue the request "
            f"without asking again for anything the caller already said.{hint}"
        )

    @function_tool
    async def back_to_front_desk(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Return to the front desk when the caller has no more appointment questions."""
        context.userdata.notes.append("handoff: booking -> greeter")
        return GreeterAgent(chat_ctx=carry_over(self)), "Returning to the front desk."
```

`BookingAgent` mixes in `BookingToolsMixin`, so it has `find_available_slots`, `book_appointment`, `reschedule_appointment` and `cancel_appointment` for free, with the same scheduler as Section 5. We only change the instructions and add a way back.

Look at `on_enter`: "continue the request without asking again for anything the caller already said." That instruction, plus the carried-over chat context, is what stops the "Can I have your name?" déjà vu. And if `CallState` already has the caller's name, we add it as a hint.

Billing next.

[CODE: step 5: BillingAgent]

```python
class BillingAgent(KnowledgeToolsMixin, Agent):
    """Billing specialist: insurance, payment options and price ranges from the FAQ."""

    def __init__(self, *, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, extra=prompts.BILLING_SPECIALIST_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Acknowledge the billing question and continue."""
        self.session.generate_reply(
            instructions="Briefly say you can help with insurance and payments, then answer the "
            "caller's question."
        )

    @function_tool
    async def back_to_front_desk(self, context: RunContext[CallState]) -> tuple[Agent, str]:
        """Return to the front desk when the caller has no more billing questions."""
        context.userdata.notes.append("handoff: billing -> greeter")
        return GreeterAgent(chat_ctx=carry_over(self)), "Returning to the front desk."
```

Billing has the FAQ tool and a way back. Its prompt, `BILLING_SPECIALIST_EXTRA`, says it can explain insurance, payment options and typical price ranges, but can't see account balances, so it offers a transfer for those. And Billing has no booking tools at all, so it can't accidentally book anything. That's least privilege, which we'll come back to in Section 11.

Finally, the entrypoint.

[CODE: step 6: entrypoint]

```python
server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Start with the greeter; handoffs happen inside tools."""
    session = create_session(get_settings(), proc=ctx.proc, userdata=CallState(), max_tool_steps=5)
    await session.start(agent=GreeterAgent(), room=ctx.room)
```

One session. One `CallState`. The call starts with the Greeter. Handoffs happen inside tools. Let's run it.

[SCREEN: terminal]

```bash
uv run python agents/s07_multi_agent.py console
```

[DEMO: Full call. 1) Riley greets. 2) Caller: "Hi, I'm Priya Shah, I'd like to book a cleaning tomorrow morning." Log: `transfer_to_booking`. 3) Booking agent: "Happy to help with that, Priya. I have eight, eight thirty or nine tomorrow morning..." (no re-asking the name). 4) Choose nine, give the number 512 555 0199, confirm the read-back; `book_appointment` fires. 5) Caller: "Great. Also, do you take Aetna?" Booking calls `back_to_front_desk`; the Greeter calls `transfer_to_billing`. 6) Billing answers from the "Insurance accepted" section: in network. 7) Caller says bye.]

Listen for three things. [PAUSE] The Booking agent says "Happy to help with that, Priya." It didn't ask her name again. That's the carried-over context. The read-back and booking work exactly as in Section 5, because they're the same tools. And when Priya asks about insurance, the call goes back through the front desk to Billing, which answers from the FAQ: Aetna is in network.

[SCREEN: terminal log scrolled back, highlight the tool calls `transfer_to_booking`, `back_to_front_desk`, `transfer_to_billing`.]

Scroll back through the log and you can see the path: greeter, booking, greeter, billing. The same trail is in `CallState.notes`. In Section 9 we'll assert on it with `result.expect.contains_agent_handoff(new_agent_type=BookingAgent)`.

[AVATAR]

One more thing to check: latency. Each handoff added a short pause while the new agent started speaking. On my machine it was about half a second. That's the cost we discussed in lecture 7.4. It's acceptable here. If it weren't, we'd shorten the specialists' `on_enter` instructions, or merge agents back together.

[SLIDE 1: What happens during a handoff]
1. Greeter's LLM calls `transfer_to_booking`
2. The tool appends a note to `CallState` and returns `(BookingAgent(...), "Transferring to the booking specialist.")`
3. LiveKit makes `BookingAgent` the active agent; the message is recorded as the tool result
4. `BookingAgent.on_enter` runs and generates the first specialist reply
5. Same session, same room, same `CallState`: the caller hears one continuous call

[AVATAR]

Let's slow down and replay one handoff step by step, because it's easy to wave hands here. The Greeter's model decides the caller wants an appointment, and calls `transfer_to_booking`. The tool runs: it writes a note into `CallState`, builds a `BookingAgent` with the recent conversation, and returns it with a short message. LiveKit sees an agent in the return value and swaps the active agent. The message becomes the tool's result in the history. Then `BookingAgent.on_enter` runs, and its `generate_reply` produces the first thing the caller hears from the specialist.

[B-ROLL: The handoff as an animation. The "Greeter" card slides out and the "Booking" card slides in; the room, the audio line and the `CallState` folder underneath stay perfectly still.]

What doesn't change is just as important. [PAUSE] It's the same session, the same room, the same audio connection, and the same `CallState` object. The caller never hears a click or a hold tone. From their side, Riley just got more specific. That's why one voice for every specialist is usually right for a small clinic: the team is an implementation detail, not something the caller should notice.

[SLIDE 2: A different model per specialist?]
- Each `Agent` can take its own `llm=`, `tts=` or `stt=`
- Small, fast model to route; stronger model for money
- Two models means two prompts and two test suites

[AVATAR]

A question from students every time: "Could the specialists use a different LLM?" Yes. Each `Agent` can take its own `llm=`, `tts=` or `stt=`, overriding the session's. A common pattern is a small, fast model for the Greeter, which mostly routes, and a stronger model for Billing, where mistakes about money are expensive. [PAUSE] Measure before you do it, though. Two models means two sets of prompts to tune and two sets of tests to keep green.

### Recap

[SLIDE 3: Recap]
- A tool that returns an `Agent` hands off
- `carry_over` passes recent context, not instructions
- `CallState` carries the facts across agents

A function tool that returns an `Agent` (with an optional message) performs the handoff, `carry_over` passes the recent conversation without the old instructions, and `CallState` carries the facts.

### Transition

In the lab, you'll add a fourth specialist, an Insurance agent, to the team.

### Speaker notes: common mistakes and Q&A

- **Caller has to repeat everything**: `chat_ctx` not passed to the new agent. Always construct specialists with `chat_ctx=carry_over(self)`.
- **Double greeting**: the Greeter's `on_enter` always says the full greeting. Check for existing conversation items first, as `GreeterAgent` does.
- **Wrong specialist picked**: overlapping docstrings. Make each handoff docstring name its topics explicitly, and keep them distinct from `transfer_to_human`.
- **Circular references**: `GreeterAgent` creates `BookingAgent`, which creates `GreeterAgent`. That's fine in Python, because the names are resolved when the tool runs, not when the class is defined.

---

## Lecture 7.6: Lab 5: Add an Insurance agent

| Field | Value |
|---|---|
| ID | 7.6 |
| Title | Lab 5: Add an Insurance agent |
| Type | LAB (guided lab; video intro/walkthrough) |
| Target duration | Video 2:00 (about 210 spoken words at ~140 wpm, plus slide and pause time); lab work about 60 minutes off-video |
| One idea | Extend the handoff graph with a new specialist, backed by tested pure-Python rules, without breaking existing routes. |
| Prerequisites | 7.5 |
| Files used | `04-labs/lab-05-handoffs.md`, `src/maple/insurance.py` and `tests/unit/test_insurance.py` (you create them), `agents/lab05_multi_agent.py` (your copy of `s07_multi_agent.py`), `tests/agent/test_lab05_handoffs.py` |

**Learning objectives**

1. Write insurance rules as pure Python with unit tests before any agent code.
2. Add an `InsuranceAgent` with a `check_insurance` tool, and route to it with `transfer_to_insurance`.
3. Prove the new routes with behavior tests using `contains_function_call` and `contains_agent_handoff`.

### Script

[AVATAR]

Maple Street Dental's insurance questions now make up a quarter of their calls, and the answers are getting specific: which plans are in network, which aren't, and what callers actually say. "Delta." "Delta Dental PPO." "Cigna DHMO." Your job: give Riley an Insurance specialist. Plan about an hour.

[SCREEN: `04-labs/lab-05-handoffs.md`: the routing diagram, then Steps 1 to 7.]

Open `04-labs/lab-05-handoffs.md`. You'll follow the same pattern as the whole course: logic first, agent second, tests always.

Steps one and two: write `src/maple/insurance.py`, with an `insurance_status` function that maps the way callers say a carrier to "in network," "out of network" or "not accepted," and unit-test it. The first checkpoint is a one-liner: "Cigna DHMO" must come back "not accepted."

Steps three to five: copy the multi-agent file to `agents/lab05_multi_agent.py`, add an `InsuranceAgent` with a `check_insurance` tool, route to it from the Greeter with a new `transfer_to_insurance` tool, and narrow Billing's docstring to payments and bills. Insurance can hand callers on to Booking when they're ready.

Step six: prove the routing with behavior tests, using `contains_function_call` and `contains_agent_handoff`, the same assertions you'll meet properly in Section 9. Step seven: a small routing table of which caller phrases go where.

[AVATAR]

Tip: write the docstrings first. Billing and Insurance overlap, so the docstrings are what tell the model which one to pick. That's exactly the tool-confusion problem from lecture 7.4.

### Recap

The lab adds a tested Insurance specialist to the handoff graph and proves the new routes with behavior tests.

### Transition

When your Insurance agent is working, take the short quiz on knowledge and handoffs.

### Speaker notes: common mistakes and Q&A

- **Billing and Insurance both claim "insurance" questions**: Billing's docstring should say payments, bills and payment plans; Insurance's should say coverage and in-network plans.
- **Forgetting a route back**: every specialist needs a way back to the front desk or on to Booking, or the caller gets stuck.
- **STT spellings**: callers (and the STT) say "Delta," "Delta Dental" and "delta dennis." Put the spellings in `insurance.py`, not in the prompt.

---

## Lecture 7.7: Quiz: Knowledge and handoffs

| Field | Value |
|---|---|
| ID | 7.7 |
| Title | Quiz: Knowledge and handoffs |
| Type | QZ (quiz; short video intro) |
| Target duration | Video 1:00 (about 120 spoken words at ~140 wpm, plus slide and pause time) |
| One idea | Check you can design grounded voice retrieval and safe handoffs. |
| Prerequisites | 7.1 to 7.6 |
| Files used | `06-assessments/quizzes/section-07.md` (6 questions) |

**Learning objectives**

1. Recall retrieval wiring options and the "no match" pattern.
2. Apply handoff mechanics: returning an `Agent`, carrying context and sharing userdata.

### Script

[AVATAR]

A caller asks about Botox, and your FAQ has nothing. What should Riley say? [PAUSE] If you answered instantly, you're ready. Six questions this time. Two on voice RAG: a tool versus pre-turn injection, and what to do when the lookup finds nothing. One on scaling: whether a sixteen-section FAQ needs a vector database. One on when to split an agent. And two on handoffs: how the Greeter hands off, and why a caller might end up repeating their name.

[SLIDE 1: Quiz: 6 questions]
- Voice RAG patterns and "no match"
- Scaling and when to split
- Handoff mechanics and shared state

[AVATAR]

One tip: for the handoff questions, picture the tool's return value. If a tool returns an agent, the session switches. Everything else follows from that one rule.

Each answer links back to its lecture. It'll take about five minutes.

### Recap

The quiz checks grounded retrieval design and multi-agent handoff mechanics.

### Transition

One more lecture in this section: Riley learns to speak Spanish and Hindi.

### Speaker notes: common mistakes and Q&A

- Most-missed: "What does a tool return to hand off?" Answer: an `Agent` instance (optionally with a message); a bare agent means no extra reply from the old agent.
- Students often pick "vector database" for any knowledge question. The quiz rewards "measure first".

---

## Lecture 7.8: Multilingual Riley: Spanish and Hindi callers

| Field | Value |
|---|---|
| ID | 7.8 |
| Title | Multilingual Riley: Spanish and Hindi callers |
| Type | SC (screencast code-along) |
| Target duration | 8:00 (about 860 spoken words at ~140 wpm; remaining time is on-screen code, runs and demo audio) |
| One idea | A multilingual voice agent needs the language set in four places (STT, turn detection, TTS, prompt), plus a plan for callers who switch mid-call and a test plan per language. |
| Prerequisites | 7.2 (FAQ tool); Section 3 (turn detection) |
| Files used | `agents/s07_knowledge_agent.py` (`LANGUAGE` env; `FOLLOW_CALLER_LANGUAGE=1`, `follow_caller_language`, `FOLLOW_CALLER_RULES`), `agents/common.py` (`build_stt`, `build_tts`), `src/maple/config.py` (`SUPPORTED_LANGUAGES`, `settings.language`), `src/maple/prompts.py` (`language_block`, `GREETINGS`) |

**Learning objectives**

1. Drive STT language, TTS language and voice, greeting and prompt language from one `LANGUAGE` setting.
2. Explain how LiveKit's turn detector handles Spanish and Hindi, and how English FAQ answers get translated.
3. Detect a language switch mid-call from `user_input_transcribed` and update the TTS language, and list what to test differently per language.

### Script

[AVATAR]

About one in five of Maple Street Dental's callers would rather speak Spanish. A growing group prefers Hindi. [PAUSE] Right now, Riley answers them in English, with an English speech model that turns "quiero una limpieza" into "Kiro, oona limp, Isa." Let's fix that. Multilingual isn't one switch. It's four settings that have to agree.

[SLIDE 1: Four places a language lives]
- STT: which language to transcribe (`es`, `hi`, or `multi`)
- Turn detection: when a Spanish or Hindi speaker has finished
- TTS: language and a voice that sounds native
- Prompt: reply language, greeting, and translating English tool results

[AVATAR]

Here they are. The speech-to-text model has to know the language, or it transcribes Spanish as garbled English. The turn detector has to know when a Spanish or Hindi speaker has finished a sentence. The text-to-speech model needs the language, and ideally a voice that sounds native. And the prompt has to tell the LLM which language to answer in, including when the FAQ tool hands back English text. Miss any one of the four, and the call falls apart.

[SCREEN: `src/maple/config.py`, highlight `SUPPORTED_LANGUAGES` and the `language` field.]

In our repo, all four come from one environment variable, `LANGUAGE`. Open `src/maple/config.py`. `SUPPORTED_LANGUAGES` lists English, Spanish and Hindi. `load_settings` validates `LANGUAGE` against it, so a typo like "sp" fails at startup instead of mid-call.

[CODE: `src/maple/config.py` (excerpt, highlight)]

```python
SUPPORTED_LANGUAGES: dict[str, str] = {"en": "English", "es": "Spanish", "hi": "Hindi"}
...
@dataclass(frozen=True)
class Settings:
    ...
    language: Language = "en"
```
(`...` marks lines left out. `load_settings` reads it from `LANGUAGE`.)

[SCREEN: `agents/common.py`, `build_stt` and `build_tts`.]

Now the speech models. Both builders in `agents/common.py` read the language.

[CODE: `agents/common.py` (excerpts, highlight)]

```python
    if provider == "deepgram":
        return inference.STT(
            model=settings.stt_model,
            language=settings.language,
            extra_kwargs={"keyterm": DENTAL_KEYTERMS, "smart_format": True},
        )
```

```python
def build_tts(settings: Settings) -> Any:
    """Return the TTS for ``AgentSession(tts=...)`` in the configured language."""
    ...
    if settings.language == "en":
        return settings.tts_model_with_voice
    return inference.TTS(
        model=settings.tts_model.split(":", 1)[0],
        voice=settings.tts_voice,
        language=settings.language,
    )
```

Speech-to-text is Deepgram Nova-3 through LiveKit Inference, with `language` set to `es` or `hi`. Text-to-speech is Cartesia Sonic-3, which is multilingual, with the language set too. One practical note: Sonic-3 can speak Spanish and Hindi with Riley's English voice, but a voice designed for the language sounds far more natural. So for a Spanish line, set `TTS_VOICE` to a Spanish voice ID from the Cartesia library.

What about turn detection? [PAUSE] Nothing to change. LiveKit's `inference.TurnDetector` is multilingual. It keeps separate thresholds per language, including Spanish and Hindi, and it uses the language the STT reports. That's why the STT language matters twice.

[SCREEN: `src/maple/prompts.py`, scroll to `GREETINGS` and `language_block`.]

Now the prompt. `prompts.py` has a `GREETINGS` dictionary, with the AI-disclosure greeting in each language. And `language_block`, which `build_instructions` appends for non-English calls. For Spanish, it tells Riley to speak Spanish for the whole call, translate tool results, which come back in English, into natural spoken Spanish, and never translate names, phone numbers or the clinic name. For Hindi it adds one practical line: use simple conversational Hindi, and common English words like "appointment" and "insurance" are fine. That's how many people in India actually talk about dental visits, and it keeps the TTS from stumbling over formal vocabulary.

[SCREEN: `src/maple/data/faq.md`: one English file, scrolled past a few sections.]

That's our FAQ strategy, too. We don't maintain three FAQ files. The retriever searches the English FAQ, and the LLM translates the one or two sentences it speaks. For a two-page FAQ, that's accurate enough. For medical or legal wording, you'd review translations by hand and store them.

[CODE: `agents/s07_knowledge_agent.py` (the language lines, highlight)]

```python
    def __init__(self, *, language: str = "en", prefetch: bool = False, extra: str = "") -> None:
        self.language = language
        self.prefetch = prefetch
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, language=language, extra=extra
            ),
        )

    async def on_enter(self) -> None:
        """Greet in the caller's language."""
        self.session.say(prompts.GREETINGS.get(self.language, prompts.GREETING))
```

And the agent from lecture 7.2 already passes `language` into `build_instructions` and greets from `GREETINGS`. So one environment variable changes all four places. Run the Spanish line.

[SCREEN: terminal]

```bash
LANGUAGE=es uv run python agents/s07_knowledge_agent.py console
```

[DEMO: Riley greets in Spanish. Speak Spanish: "Hola, ¿a qué hora cierran los viernes?" Riley calls `lookup_clinic_info` and answers in Spanish: open until two on Fridays. Then: "¿Y dónde puedo estacionar?" Show the tool call argument in the log.]

Riley greets in Spanish, with the AI disclosure. "¿A qué hora cierran los viernes?" Riley looks it up and answers in Spanish: open until two on Fridays.

Now watch the tool call for the parking question. [PAUSE] On this run, the model passed the question to `lookup_clinic_info` in English: "where can I park." That's lucky, not guaranteed. Our FAQ index is a keyword index over English text. If the model passes "¿dónde puedo estacionar?" as is, no English words match, and Riley honestly says it isn't sure. The fix is one line in the prompt: "pass FAQ questions to the tool in English." The follow-the-caller setup you'll see in a minute already has that line. Keep it in mind any time your knowledge base has only one language.

Hindi works the same way.

```bash
LANGUAGE=hi uv run python agents/s07_knowledge_agent.py console
```

[DEMO: Hindi greeting from `GREETINGS["hi"]`. Ask in Hindi about Saturday hours; Riley answers in simple Hindi.]

[SLIDE 2: Callers who switch languages mid-call]
- Fixed-language lines (`LANGUAGE=es` or `hi`) are simplest and most robust
- For an English line that should follow the caller: STT in `multi` mode
- Each final transcript carries a language code (`ev.language`, e.g. "es-419")
- On a change, update the TTS language; `FOLLOW_CALLER_RULES` tells the LLM to switch
- In the repo: `FOLLOW_CALLER_LANGUAGE=1`

[AVATAR]

By default the repo runs one language per line, which is what I'd deploy for a dedicated Spanish number. But what about a caller on the English line who says, "Perdón, ¿podemos hablar en español?" The reference file already handles that, behind one switch.

[SCREEN: VS Code, `agents/s07_knowledge_agent.py`, scrolled to `follow_caller_language`.]

[CODE: `agents/s07_knowledge_agent.py`, the mid-call language switch]

```python
def follow_caller_language(session: AgentSession[CallState], *, initial: str = "en") -> None:
    """Switch the TTS language when the caller changes language mid-call (lecture 7.8).

    Needs an STT that reports a language on final transcripts (Deepgram ``multi`` does).
    The LLM switches because ``FOLLOW_CALLER_RULES`` tells it to.
    """
    current = {"language": initial}

    @session.on("user_input_transcribed")
    def _follow_caller_language(ev: UserInputTranscribedEvent) -> None:
        if not ev.is_final or ev.language is None:
            return
        spoken = str(ev.language).split("-", 1)[0]  # "es-419" -> "es"
        if spoken in ("en", "es", "hi") and spoken != current["language"]:
            logger.info("caller switched language: %s -> %s", current["language"], spoken)
            current["language"] = spoken
            if session.tts is not None:
                session.tts.update_options(language=spoken)
```

Every final transcript event carries a language code, like "es-419" for Latin American Spanish. The code is a plain string, so we keep the part before the dash. When it changes, we log it and update the TTS language with `update_options`.

[SCREEN: Scroll to the end of `entrypoint`, the `FOLLOW_CALLER_LANGUAGE` branch, then up to `FOLLOW_CALLER_RULES` near the top of the file.]

[CODE: the entrypoint's `FOLLOW_CALLER_LANGUAGE=1` branch (excerpt)]

```python
    # Lecture 7.8 extension: code-switching STT, TTS follows the caller, prompt starts in English.
    session = create_session(
        settings,
        proc=ctx.proc,
        userdata=CallState(),
        stt=inference.STT(model=settings.stt_model, language="multi"),
        tts=inference.TTS(model=settings.tts_model.split(":", 1)[0], voice=settings.tts_voice, language="en"),
    )
    follow_caller_language(session, initial="en")
    await session.start(
        agent=KnowledgeRiley(language="en", prefetch=prefetch, extra=FOLLOW_CALLER_RULES), room=ctx.room
    )
```

Here's the branch that uses it. The STT runs in Deepgram's `multi` mode, which handles callers who switch languages, even mid-sentence. The TTS starts in English. And the agent gets one extra prompt block, `FOLLOW_CALLER_RULES`: start in English, switch with the caller, translate tool results, and pass FAQ questions to the tool in English. That last line fixes the parking problem you just saw.

[SCREEN: terminal]

```bash
FOLLOW_CALLER_LANGUAGE=1 uv run python agents/s07_knowledge_agent.py console
```

[DEMO: Start in English: "Hi, what time do you close on Friday?" Riley answers in English. Then: "Perdón, ¿podemos hablar en español?" The log shows `caller switched language: en -> es`, and Riley's next reply is in Spanish. Ask "¿Dónde puedo estacionar?" and show the `lookup_clinic_info` argument in English.]

There's the log line: caller switched language, English to Spanish. One warning. Check that your STT actually reports a language before relying on this. Some models and modes don't.

[SLIDE 3: What to test differently per language]
- WER per language, with native-speaker reference transcripts (9.7)
- Behavior tests per language: judge intent "responds in Spanish and states Friday hours" (9.3)
- Numbers and dates: "el jueves quince a las diez" must become the right ISO date
- Keyterms and names: keyterm support differs by language and provider
- Latency per language: measure p95 separately (9.8)

[AVATAR]

[AVATAR]

Finally, testing. Everything in Section 9 applies, once per language. Word error rate, with reference transcripts from native speakers, because English speakers reading Spanish scripts give you optimistic numbers. Behavior tests with judge intents like "responds in Spanish and states the Friday hours." Dates and numbers, which is where multilingual agents break most often. Keyterm support, which differs by language. And latency per language, because not every model is equally fast in every language. There's already one Spanish-caller conversation in the Section 9 golden set.

### Recap

[SLIDE 4: Recap]
- One `LANGUAGE` setting drives all four places
- English FAQ, translated by the LLM
- `FOLLOW_CALLER_LANGUAGE=1` follows mid-call switches

One `LANGUAGE` setting drives STT, TTS, greeting and prompt, the turn detector adapts per language, and `FOLLOW_CALLER_LANGUAGE=1` switches on the repo's `follow_caller_language` handler for callers who switch mid-call.

[SLIDE 5: You can now]
- Ground answers in a FAQ, or say "not sure"
- Hand callers between specialist agents
- Serve Spanish and Hindi callers

### Transition

Next up is Section 8, where Riley gets a real phone number, takes inbound calls, makes reminder calls and transfers callers to a human.

### Speaker notes: common mistakes and Q&A

- **STT left in English**: Spanish comes out as nonsense English words, and the LLM "answers" nonsense. Always set `LANGUAGE` (or `multi`).
- **Wrong voice**: an English voice speaking Hindi sounds accented. Pick a native voice per language with `TTS_VOICE`.
- **Spanish query, English index**: the keyword FAQ index only matches English words. Tell the model to pass FAQ questions in English, or translate the FAQ.
- **`ev.language` is `None`**: some STT models or modes don't report language; mid-call switching then can't work, so run separate numbers per language.
- **`ev.language.language` raises `AttributeError`**: `ev.language` is a `LanguageCode`, a `str` subclass. Use `str(ev.language).split("-", 1)[0]`, as the repo does.
- **Translating names and numbers**: the language block says not to, but test it. "Maple Street Dental" should never become "Clínica Dental Calle Arce."

