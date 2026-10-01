# Quiz: Testing Voice Agents (Section 9)

| Field | Value |
|---|---|
| Udemy lecture | 9.12 Quiz: Testing voice agents |
| Questions | 10 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 9.1 to 9.10 |

---

### Q1. In a recorded call, Riley says "Tuesday at three is available" without ever calling `find_available_slots`. The time was actually taken. Which failure type is this, and which test catches it most directly?

*Related lecture: 9.1 How voice agents fail in production*

- **A.** Mishearing; catch it with a WER eval.
  - *Explanation:* Incorrect. The caller's words were recognised correctly. The agent invented a fact.
- **B.** Hallucinated availability; catch it with a behaviour test that asserts `find_available_slots` is called before any time is offered.
  - *Explanation:* Correct. Stating availability without a tool result is a hallucination. A behaviour test using `result.expect.next_event().is_function_call(name="find_available_slots")` (or `contains_function_call`) fails whenever Riley skips the lookup.
- **C.** A latency spike; catch it with the latency budget report.
  - *Explanation:* Incorrect. Nothing here is about timing. A fast wrong answer is still wrong.
- **D.** Prompt injection; catch it with the simulated attacker persona.
  - *Explanation:* Incorrect. Nobody tried to manipulate Riley. The model skipped a required step on its own.

**Correct answer: B**

---

### Q2. A unit test shows that `ClinicScheduler.find_slots()` returns a slot that overlaps the lunch break. Where in the voice testing pyramid should the regression test for this bug live?

*Related lecture: 9.2 The voice testing pyramid*

- **A.** In a simulated-caller eval, so the whole conversation is covered.
  - *Explanation:* Incorrect. Simulated calls are slow, costly and non-deterministic. They are the wrong tool for a pure logic bug.
- **B.** In production monitoring, by alerting on complaints about lunch-time bookings.
  - *Explanation:* Incorrect. Monitoring detects problems after callers are affected. This bug can be prevented before deploy.
- **C.** In the unit layer (`tests/unit/test_scheduler.py`), because it is pure business logic that can be tested offline in milliseconds.
  - *Explanation:* Correct. The base of the pyramid is fast, deterministic unit tests for pure logic. Keeping the scheduler in `src/maple/` with no framework imports is what makes this possible.
- **D.** In an LLM-as-judge eval that asks whether the agent "seems to respect lunch".
  - *Explanation:* Incorrect. A judge adds cost and uncertainty to a question with an exact, checkable answer.

**Correct answer: C**

---

### Q3. You want to test that Riley's greeting is friendly, mentions Maple Street Dental and asks how it can help. The exact wording changes every run. Which assertion fits best?

*Related lecture: 9.3 Behavior tests with LiveKit's test framework*

- **A.** `await result.expect.next_event().is_message(role="assistant").judge(judge_llm, intent="Greets the caller warmly, names Maple Street Dental, and asks how it can help.")`
  - *Explanation:* Correct. `.judge()` uses an LLM to check that the message satisfies an intent, which suits natural language that varies between runs. `is_message(role="assistant")` first checks that the next event is Riley speaking.
- **B.** `assert result.text == "Hi, thanks for calling Maple Street Dental. How can I help?"`
  - *Explanation:* Incorrect. Exact string matching fails whenever the LLM rephrases, so the test would be flaky without catching real problems.
- **C.** `result.expect.no_more_events()`
  - *Explanation:* Incorrect. This only checks that nothing else happened. It says nothing about the greeting's content.
- **D.** `result.expect.contains_function_call(name="greet")`
  - *Explanation:* Incorrect. Greeting is a spoken message, not a tool call. There is no `greet` tool.

**Correct answer: A**

---

### Q4. Sometimes Riley says "Let me check that for you" before calling `find_available_slots`, and sometimes it calls the tool straight away. Your test asserts the next event is the function call and fails intermittently. What is the correct fix?

*Related lecture: 9.4 Asserting tool calls and arguments*

- **A.** Add a retry loop that runs the test until it passes.
  - *Explanation:* Incorrect. Retries hide non-determinism instead of expressing what behaviour is acceptable.
- **B.** Force the model to never speak before tools by lowering the temperature to 0.
  - *Explanation:* Incorrect. Temperature 0 reduces variation but does not guarantee it, and a short "let me check" is good voice UX.
- **C.** Delete the tool assertion and only judge the final message.
  - *Explanation:* Incorrect. You would lose the check that the tool was actually called, which is the point of the test.
- **D.** Call `result.expect.skip_next_event_if(type="message", role="assistant")` before asserting `is_function_call(name="find_available_slots")`.
  - *Explanation:* Correct. `skip_next_event_if` consumes an optional assistant message only if it is there, so the test accepts both valid orderings and still requires the tool call.

**Correct answer: D**

---

### Q5. After a successful booking turn, you want to be sure Riley did not also call `cancel_appointment` or any other tool by mistake. Which assertion completes the check?

*Related lecture: 9.4 Asserting tool calls and arguments*

- **A.** `result.expect.contains_function_call(name="book_appointment")`
  - *Explanation:* Incorrect. This confirms the booking happened but allows any extra events, including a stray cancellation.
- **B.** After asserting the expected function call, its output and the confirmation message in order, call `result.expect.no_more_events()`.
  - *Explanation:* Correct. `no_more_events()` fails if anything else happened in that turn, so unexpected extra tool calls are caught.
- **C.** `result.expect.next_event().is_function_call_output(is_error=True)`
  - *Explanation:* Incorrect. That asserts the tool failed, which is the opposite of a successful booking.
- **D.** Check that the judge rates the turn as "polite".
  - *Explanation:* Incorrect. Politeness says nothing about which tools ran.

**Correct answer: B**

---

### Q6. You need a deterministic test for the "no availability this week" path. The real scheduler usually has free slots. What should you do?

*Related lecture: 9.5 Mocking tools for deterministic tests*

- **A.** Fill the in-memory calendar manually before every test, and hope the LLM asks for the right week.
  - *Explanation:* Incorrect. It can work, but it couples the test to calendar details and still depends on which days the LLM asks about.
- **B.** Tell the LLM in the test input: "Pretend there is no availability."
  - *Explanation:* Incorrect. That tests the model's role-play, not how Riley handles a real empty result from the tool.
- **C.** Skip this path; it is rare.
  - *Explanation:* Incorrect. "No availability" is common in busy clinics and a classic source of hallucinated slots.
- **D.** Wrap the test in `with mock_tools(RileyBookingAgent, {"find_available_slots": fake}):` where `fake` (same signature as the tool) returns a "no openings" result, then assert Riley offers another day or the waitlist instead of inventing a time.
  - *Explanation:* Correct. `mock_tools` replaces a tool's implementation for the duration of the block, so you can force empty results or errors deterministically and test how Riley responds.

**Correct answer: D**

---

### Q7. You want to check, across 20 golden transcripts, whether Riley always reads back the date and time before booking. Which approach from the course fits best?

*Related lecture: 9.6 LLM-as-judge with DeepEval on transcripts*

- **A.** A DeepEval conversational G-Eval metric with a criterion like "Before any booking is confirmed, the assistant repeats the date, time and name and asks for confirmation", scored over each transcript with a threshold.
  - *Explanation:* Correct. Read-back is a conversation-level behaviour with many valid phrasings. A conversational G-Eval judge scores whole transcripts against a written criterion, which is what the course's `test_conversation_quality.py` does.
- **B.** A regex that searches for "Shall I go ahead?" in each transcript.
  - *Explanation:* Incorrect. Regexes break on paraphrases ("Does that sound right?") and cannot check that the read-back came before the booking.
- **C.** WER between each transcript and a reference transcript.
  - *Explanation:* Incorrect. WER measures speech recognition accuracy, not conversational behaviour.
- **D.** Counting how many tool calls each transcript contains.
  - *Explanation:* Incorrect. A tool count cannot tell you whether a confirmation happened before the commit.

**Correct answer: A**

---

### Q8. A reference transcript has 10 words. Compared with it, the STT output has 1 substituted word, 1 missing word and 1 extra word. What is the WER?

*Related lecture: 9.7 Measuring STT accuracy with WER*

- **A.** 10%
  - *Explanation:* Incorrect. That counts only one of the three errors.
- **B.** 20%
  - *Explanation:* Incorrect. This counts substitutions and deletions but forgets the insertion. WER counts all three error types.
- **C.** 30%
  - *Explanation:* Correct. WER = (S + D + I) / N = (1 + 1 + 1) / 10 = 0.30.
- **D.** 27%, because the hypothesis has 10 words and one extra, so N is 11.
  - *Explanation:* Incorrect. The denominator is the number of words in the reference, not the hypothesis. That is why WER can exceed 100% when there are many insertions.

**Correct answer: C**

---

### Q9. Over 200 turns, LLM time to first token has a mean of 480 ms and a p95 of 1,350 ms. Your CI latency budget is written in terms of p95. What should happen, and why is p95 used?

*Related lecture: 9.8 Latency testing against a budget*

- **A.** Pass, because the mean is under a second.
  - *Explanation:* Incorrect. The budget is defined on p95, and the mean hides the slow tail that callers notice.
- **B.** Fail if 1,350 ms exceeds the p95 budget (for example, the repo's default 700 ms for `llm_ttft`), because 1 in 20 turns having a long pause is what callers remember.
  - *Explanation:* Correct. Percentile budgets capture tail latency. A good mean with a bad p95 means regular awkward silences, and the course's `latency_report.py` fails the build when a stage's p95 exceeds its budget.
- **C.** Pass, because p95 values are always noisy and should be ignored.
  - *Explanation:* Incorrect. 200 turns give a reasonable p95 estimate. Ignoring the tail defeats the purpose of the budget.
- **D.** Fail, because any single turn over one second fails the build.
  - *Explanation:* Incorrect. A max-based rule makes CI flaky from one-off network blips. Percentile budgets are the standard compromise.

**Correct answer: B**

---

### Q10. Your simulated "injection attacker" caller beats Riley in 1 of 10 runs, but passes 9 times. A teammate wants to mark the test as flaky and ignore it. What is the right interpretation?

*Related lecture: 9.9 Simulated callers: agents testing agents*

- **A.** Agree; simulated callers are non-deterministic, so a 90% pass rate is fine for a security scenario.
  - *Explanation:* Incorrect. For safety scenarios, a single success by an attacker is a real vulnerability. In production, attackers get unlimited attempts.
- **B.** Delete the persona because it makes CI red.
  - *Explanation:* Incorrect. That removes the only signal that you have a vulnerability.
- **C.** Replace the simulated caller with a fixed script so the result is always the same.
  - *Explanation:* Incorrect. Keep deterministic scripted tests too, but the variation of simulated callers is exactly what found this weakness.
- **D.** Treat it as a real failure: read the failing transcript, fix the guardrail (prompt, tool permissions or verification), and keep running multiple trials with a pass threshold of 100% for security personas.
  - *Explanation:* Correct. Simulated callers are run many times because behaviour varies. Use pass-rate thresholds that match the risk: some variation may be acceptable for tone, none for security. Every failing transcript is a lead.

**Correct answer: D**
