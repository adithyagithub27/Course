# Quiz: Setup and Tracing Basics (Section 2)

| Field | Value |
|---|---|
| Udemy lecture | 2.6 Quiz: Setup and tracing basics |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 2.1 to 2.5 |

---

### Q1. Before saving an OpenAI key in `.env`, lecture 2.1 asks you to configure something in the OpenAI dashboard. What, and why does the course insist on it?

*Related lecture: 2.1 Accounts, keys and spending caps*

- **A.** Create one key per lab, so usage can be attributed per lab.
  - *Explanation:* Incorrect. Attribution in this course is done from spans, not keys. One project key is enough.
- **B.** Upgrade to a paid tier so rate limits do not interfere with the swarm.
  - *Explanation:* Incorrect. The swarm runs offline against the mock LLM; it never needs real rate-limit headroom.
- **C.** Enable two-factor authentication, because keys are often stolen.
  - *Explanation:* Incorrect. Good practice, but not what the lecture requires. The risk being managed is spend, not account takeover.
- **D.** Set a monthly budget limit (a hard cap) with an email alert below it, because the course's own subject is agents that can spend money unexpectedly, and a cap turns a mistake into a bounded one.
  - *Explanation:* Correct. A hard cap around $20 with an alert at $5 covers the whole course (expected spend is $5 to $15) and guarantees that a bug in your loop costs at most the cap. It is the personal version of the per-tenant hard cap Atlas gets in Section 6.

**Correct answer: D**

---

### Q2. You run `make test` in a fresh clone with no `.env` at all and no API keys. What should happen, and why?

*Related lecture: 2.2 Project setup with uv and the Makefile*

- **A.** It passes (419 tests in the shipped repo), because `OFFLINE=1` is the default, the unit tests cover pure-Python modules in `src/northwind/`, and the integration tests run the FastAPI app against the mock LLM with an in-memory span exporter.
  - *Explanation:* Correct. Designing the test suite to be green without keys is deliberate: it makes the CI budget gate in Section 13 possible and gives students an immediate first win.
- **B.** It passes only if Docker is running, because tests need Langfuse.
  - *Explanation:* Incorrect. No test needs Langfuse or Docker. Self-hosting arrives in Section 13 and even then tests stay independent of it.
- **C.** It hangs waiting for network access to download `tiktoken` encodings.
  - *Explanation:* Incorrect. `tokens.py` falls back to an approximate counter when the encoding is not cached, precisely so nothing needs the network.
- **D.** It fails immediately with an authentication error, because the tests call OpenAI.
  - *Explanation:* Incorrect. The unit and integration suites run in offline mode by default and never call a provider.

**Correct answer: A**

---

### Q3. Your first trace in Langfuse is named `invoke_agent atlas`. Under it are `step 1` (with a `chat gpt-4.1-mini` generation and an `execute_tool search_knowledge_base` retriever) and `step 2` (with a second `chat gpt-4.1-mini` generation). Where in this trace do the token usage and the cost live?

*Related lecture: 2.3 Quick win: one request, one trace*

- **A.** On the `search_knowledge_base` span, because retrieval determines how many tokens go into the prompt.
  - *Explanation:* Incorrect. Retrieval influences the prompt size, but the retriever span records query, top-k and scores, not token usage.
- **B.** On the generation span, as `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` (and cached tokens when present) with the cost computed from them; every cost report in the course rolls up from generation spans.
  - *Explanation:* Correct. Usage comes back from the provider per model call, so it is attached to the generation observation. Roll-ups by trace, session, user or tenant are aggregations over generation spans.
- **C.** Nowhere in the trace; cost is only on the OpenAI invoice.
  - *Explanation:* Incorrect. The point of the course is that cost is attributed inside the trace, per call, in near real time.
- **D.** On the root `invoke_agent atlas` span, because that is the request.
  - *Explanation:* Incorrect. The root span carries request-level attributes (tenant, user, session) and Langfuse may show a rolled-up total there, but usage is recorded where the tokens were consumed.

**Correct answer: B**

---

### Q4. `OFFLINE=1 make replay` finishes in about 20 seconds and reports 4,000 sessions, 10,184 requests and $56.28 of cost for Monday 2026-09-14. Where did that $56.28 come from, and how much did the replay actually cost you?

*Related lecture: 2.4 Offline mode: a full day of traffic for free*

- **A.** The number is random and changes on every run.
  - *Explanation:* Incorrect. The replay is seeded (seed 7, the Makefile default), so the same seed produces the same spans and the same total every time. That determinism is what makes before/after comparisons in Section 6 trustworthy.
- **B.** The replay called OpenAI 10,184 times at a discount; you were billed about $56.
  - *Explanation:* Incorrect. The replay makes no LLM calls at all.
- **C.** The $56.28 is the cost that the mock LLM's realistic token counts *would* have incurred at the pinned price table, computed by the same pricing code Atlas uses in production; the replay cost you nothing.
  - *Explanation:* Correct. The mock emits usage figures drawn from realistic distributions per intent and scenario; `pricing.py` prices them exactly as it would price real usage. You get real cost arithmetic on synthetic traffic for free.
- **D.** The $56.28 is Langfuse's ingestion fee for the day's 70,560 spans.
  - *Explanation:* Incorrect. Langfuse Cloud's free tier covers the course, and ingestion cost is not what the replay reports.

**Correct answer: C**

---

### Q5. You send two `curl` requests to Atlas with the same `X-User` and different `X-Session` values, then two more with the same `X-Session`. How does Langfuse group them?

*Related lecture: 2.5 Lab 1: Environment and first trace*

- **A.** Four sessions, because each HTTP request is a separate session.
  - *Explanation:* Incorrect. Each request is a separate *trace*; sessions are the explicit grouping of traces by `session_id`.
- **B.** They cannot be grouped, because Langfuse groups only by trace id.
  - *Explanation:* Incorrect. Sessions and users are first-class in Langfuse, and Lab 1's stretch goal shows history growing across turns of one session.
- **C.** All four are one session, because they come from the same user.
  - *Explanation:* Incorrect. A user can have many sessions; sessions are keyed by `session_id`, not by user.
- **D.** Three sessions: two single-turn sessions for the first two requests, and one two-turn session for the last two, all attributed to the same user in the Users view.
  - *Explanation:* Correct. `X-Session` becomes the trace's `session_id`, and traces sharing it are shown together in the Sessions view; `X-User` becomes `user_id`, which groups sessions under a user. Tenant is a tag/metadata on each trace.

**Correct answer: D**
