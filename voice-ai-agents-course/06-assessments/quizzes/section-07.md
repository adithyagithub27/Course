# Quiz: Knowledge and Handoffs (Section 7)

| Field | Value |
|---|---|
| Udemy lecture | 7.7 Quiz: Knowledge and handoffs |
| Questions | 6 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 7.1 to 7.5 |

---

### Q1. You are choosing between two ways to give Riley the clinic FAQ: (1) a `lookup_clinic_info` tool the LLM calls when needed, or (2) retrieving FAQ passages in `on_user_turn_completed` and injecting them before every LLM call. What is the main latency trade-off?

*Related lecture: 7.1 RAG for voice: short, speakable, grounded*

- **A.** The tool approach costs an extra LLM round trip (decide to call the tool, then answer) but only on FAQ turns; pre-turn injection adds retrieval time to every turn but avoids the extra round trip.
  - *Explanation:* Correct. With a tool, the model first emits a tool call, the tool runs, and the model generates again, so FAQ answers take roughly one extra LLM step. Injection runs retrieval on every turn, including "yes, Tuesday works", but the answer comes from a single generation. Which is faster overall depends on how many turns are FAQ questions and how fast retrieval is.
- **B.** There is no difference; both run exactly the same steps.
  - *Explanation:* Incorrect. The number and timing of LLM calls differ, which is the whole trade-off.
- **C.** Pre-turn injection is always slower because it requires a vector database.
  - *Explanation:* Incorrect. Injection can use any retriever, including the course's in-memory keyword/BM25-lite index, which takes milliseconds.
- **D.** The tool approach is always slower because tools run on a separate server.
  - *Explanation:* Incorrect. Tools run in the agent process. Their extra cost is the additional LLM step, not the location.

**Correct answer: A**

---

### Q2. A caller asks, "Do you do dental implants?" The FAQ says the clinic refers patients to specialists for implants. Another caller asks, "Do you offer Botox?" and the FAQ lookup returns no match. How should Riley handle the second question?

*Related lecture: 7.2 Code-along: FAQ lookup tool*

- **A.** Answer "yes" because most modern clinics offer it.
  - *Explanation:* Incorrect. That is a hallucination. Riley would be making a claim the clinic never made.
- **B.** Say she isn't sure, and offer to take a message or transfer the caller to the front desk.
  - *Explanation:* Correct. Grounding instructions tell Riley to answer only from what `lookup_clinic_info` returns, and to say "I'm not sure" and offer a human when nothing relevant comes back. In the course code, `FaqIndex.answer()` returns `"NO_MATCH"` so the prompt can handle this case explicitly.
- **C.** Read out the full list of services so the caller can decide.
  - *Explanation:* Incorrect. A long spoken list is poor voice UX and still does not answer the question.
- **D.** Say "no", because it is not in the FAQ.
  - *Explanation:* Incorrect. Absence from a short FAQ is not proof the clinic doesn't offer it. Saying "no" is also an ungrounded claim.

**Correct answer: B**

---

### Q3. The clinic's FAQ has 16 short sections. A teammate proposes a hosted vector database with an embedding model to "make retrieval production-grade". What is the best response?

*Related lecture: 7.3 Scaling knowledge: vector stores and latency*

- **A.** Agree; every RAG system needs a vector database.
  - *Explanation:* Incorrect. Vector search helps with large or semantically varied corpora. It is not required for a small, stable FAQ.
- **B.** Agree, but only if you also move the FAQ into the system prompt.
  - *Explanation:* Incorrect. That mixes two approaches and still adds embedding latency.
- **C.** Keep the in-memory keyword/BM25-lite index for now: it answers in milliseconds with no network hop; move to embeddings when the knowledge base grows or keyword recall measurably fails.
  - *Explanation:* Correct. In a voice agent every network hop adds to response time. For 16 sections, a local keyword index is fast, deterministic and testable. Measure recall on real questions and upgrade when the data says so.
- **D.** Remove retrieval and let the LLM answer from its own knowledge.
  - *Explanation:* Incorrect. The LLM knows nothing about this clinic's hours, prices or insurance and would hallucinate them.

**Correct answer: C**

---

### Q4. Riley's single prompt has grown to 3,000 words with 14 tools covering booking, billing, insurance and FAQs. Testing shows more wrong tool choices and slower first tokens. What is the strongest argument for splitting into specialist agents?

*Related lecture: 7.4 Why split one agent into several*

- **A.** Multiple agents always cost less.
  - *Explanation:* Incorrect. Handoffs can add turns and repeated context. Cost is not the main reason to split.
- **B.** LiveKit limits each agent to five tools.
  - *Explanation:* Incorrect. There is no such limit. The problem is model confusion, not a framework cap.
- **C.** Specialists let each agent use a different voice, which callers prefer.
  - *Explanation:* Incorrect. Different voices are possible but often confuse callers. It is not the core reason to split.
- **D.** Each specialist gets a shorter prompt and only the tools it needs, which reduces tool confusion and prompt tokens per turn, and makes each part easier to test.
  - *Explanation:* Correct. Smaller, focused prompts and tool sets improve tool selection accuracy and time to first token, and let you write targeted tests per specialist. The trade-off is handoff complexity, which you manage with shared state.

**Correct answer: D**

---

### Q5. In `s07_multi_agent.py`, how does the Greeter hand a caller to the Booking specialist?

*Related lecture: 7.5 Code-along: Greeter → Booking → Billing*

- **A.** A `@function_tool` on the Greeter returns a new `BookingAgent` instance (optionally with a short message), and the session switches to that agent.
  - *Explanation:* Correct. In LiveKit Agents, a tool that returns another `Agent` triggers a handoff. The new agent's `on_enter` runs, and state in the session's `userdata` is still available.
- **B.** The Greeter calls `session.start()` again with the Booking agent.
  - *Explanation:* Incorrect. `start()` begins a session once. Handoffs happen inside a running session.
- **C.** The Greeter dials a second LiveKit room where the Booking agent waits.
  - *Explanation:* Incorrect. All agents in the flow share the same room and session. No new room or call is created.
- **D.** The Greeter sets `userdata.current_agent = "booking"` and the framework reads it.
  - *Explanation:* Incorrect. Userdata is your own state; the framework does not route based on it.

**Correct answer: A**

---

### Q6. After a handoff from the Greeter to the Billing specialist, the Billing agent asks the caller for their name again, even though they gave it to the Greeter. Which fix addresses this properly?

*Related lecture: 7.5 Code-along: Greeter → Booking → Billing*

- **A.** Tell callers at the start that they may need to repeat themselves.
  - *Explanation:* Incorrect. That describes the problem instead of fixing it.
- **B.** Use one agent class for everything to avoid handoffs.
  - *Explanation:* Incorrect. That throws away the benefits of specialists (Q4). The issue is missing context, which has a direct fix.
- **C.** Store the caller's name in the shared `userdata` when the Greeter learns it, and pass the conversation so far into the new agent (its `chat_ctx`) so the specialist can see what was already said.
  - *Explanation:* Correct. `userdata` lives on the session, so every agent's tools can read it, and carrying over the chat context lets the new agent's LLM see the earlier turns. Together they stop specialists from re-asking.
- **D.** Increase the Billing agent's temperature so it infers the name.
  - *Explanation:* Incorrect. Temperature changes randomness, not access to information the agent never received.

**Correct answer: C**
