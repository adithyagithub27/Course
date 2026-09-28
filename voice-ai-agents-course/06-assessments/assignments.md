# Udemy Assignments

Entries formatted for Udemy's **Assignment** curriculum item (Curriculum → + Curriculum item → Assignment). Each entry maps one-to-one to Udemy's fields:

| Udemy field | Where it comes from below |
|---|---|
| Title | "Title" (80 characters or fewer) |
| Estimated duration | "Estimated duration" (minutes) |
| Instructions (text) | "Instructions" block |
| Instructions: downloadable resource | "Attach" line (upload the project brief exported to PDF) |
| Questions | "Questions" (up to three per assignment, as planned for this course) |
| Solutions: instructor's answer per question | "Instructor example answers" |
| Solutions: video or resource | "Solution resource" line |

| # | Lecture | Assignment | Brief |
|---|---|---|---|
| 1 | 4.7 | Challenge: Riley for your business | `05-projects/challenges.md` |
| 2 | 5.8 | Project 1: Booking agent | `05-projects/project-1-booking-agent.md` |
| 3 | 8.7 | Project 2: Phone receptionist | `05-projects/project-2-phone-receptionist.md` |
| 4 | 9.11 | Project 3: Test suite for Riley | `05-projects/project-3-test-suite.md` |
| 5 | 13.6 | Capstone: Riley, production receptionist | `05-projects/capstone-riley.md` |
| 6 | 13.7 | Domain swap: ship Riley for a new business | `05-projects/challenges.md` |

Students submit answers as text in Udemy (links to GitHub, videos and screenshots go inside the answers). After submitting, they see the instructor's example answers and can give and receive peer feedback; the peer-review checklists at the end of each brief are written for that step.

---

## Assignment 1: Challenge: Riley for your business

**Title:** Challenge: Riley for your business

**Estimated duration:** 60 minutes

**Instructions:**

Rewrite Riley's instructions for a business you know well (a salon, restaurant, clinic, gym, garage, law office or your own workplace) and hear the result.

1. Fill in `10-resources/business-template.md`: callers' top five reasons for calling, opening hours, ten facts callers ask about, things the agent must never do, when to hand off to a human, and the tone the business wants.
2. Copy `agents/s04_voice_prompting.py` to `agents/c47_my_business.py` and replace the instructions with your own voice-first prompt: identity and AI disclosure, goal, style (one or two sentences, one question at a time), output rules, facts policy, safety and escalation.
3. Run it with `uv run agents/c47_my_business.py console` (or `console --text`) and hold one realistic three-to-six-turn conversation.
4. Run `labs/voice_lint.py` from Lab 3 on the agent's replies.
5. Post your transcript in the lecture's Q&A as well, so classmates can compare domains.

Use invented names and numbers only. Full brief and acceptance criteria: `05-projects/challenges.md`, Challenge 4.7.

**Attach:** `challenges.pdf` (export of `05-projects/challenges.md`) and `business-template.pdf`.

**Questions:**

1. Paste the identity, style and "never do" parts of your prompt. What type of business is it, and which rule is specific to that business?
2. Paste your console transcript (three to six turns) and the `voice_lint.py` summary line.
3. What did you change after hearing the agent for the first time, and why?

**Instructor example answers:**

1. *Business:* an independent car repair garage. *Identity:* "You are Sam, the AI assistant for Eastside Auto on the phone. Say you are an AI assistant if asked." *Style:* "One or two short sentences. One question at a time, then wait." *Never do:* "Never quote a repair price or diagnose a fault; only the mechanic can do that after an inspection. Offer an inspection slot instead." The garage-specific rule is the no-diagnosis, no-quote rule: callers describe noises and want a price, and a wrong guess becomes a dispute at pickup.
2. *Transcript:* Caller: "Hi, my brakes are squeaking, how much to fix them?" Sam: "I can't quote a price without an inspection, but I can book you in for one. Would tomorrow morning work?" Caller: "Yeah, what time do you open?" Sam: "We open at seven thirty. Would eight o'clock suit you?" Caller: "Perfect." Sam: "Great. Can I get your name?" *Lint:* "6 replies, 0 flagged, average 14.2 words per reply".
3. The first version said "We open at 7:30am", and the TTS read "seven thirty a m" awkwardly; I added the rule to say times as words ("seven thirty in the morning"). It also asked for name and phone number in one sentence, so I added "ask one question at a time, then wait". Both problems were obvious by ear and invisible when reading the prompt.

**Solution resource:** Lecture 4.7 walkthrough video (instructor rewrites Riley for a salon live).

---

## Assignment 2: Project 1: Booking agent

**Title:** Project 1: Build Riley's booking agent

**Estimated duration:** 240 minutes

**Instructions:**

Build `agents/p1_booking_agent.py`: Riley books, reschedules and cancels appointments at Maple Street Dental. Write the four tools yourself (`find_available_slots`, `book_appointment`, `reschedule_appointment`, `cancel_appointment`) on top of `src/maple/scheduler.py`.

Requirements (full list in the brief):

- Collect name, callback number, reason and preferred time one question at a time.
- Call `find_available_slots` before offering any time; offer at most three.
- Read back name, day, date and time and wait for a clear "yes" before any commit; handle "No, Thursday" with a fresh check and a new read-back.
- Turn every scheduler error into a speakable `ToolError`; never speak IDs or ISO timestamps.
- Filler speech only on slow operations (`context.with_filler(..., delay=...)`, demo with `MAPLE_SIMULATED_LATENCY=1.5`).
- Store caller details in a typed userdata dataclass.

Record a 3 to 5 minute demo showing a booking, a correction, a closed-day request, a reschedule and filler speech. Commit a transcript and short notes. The rubric (100 points, pass mark 70) is in `05-projects/project-1-booking-agent.md`.

**Attach:** `project-1-booking-agent.pdf`

**Questions:**

1. Paste the link to your code and demo recording. Which acceptance criterion was hardest to meet, and what did you change to meet it?
2. Paste your `book_appointment` docstring and explain how it helps the model decide when (and when not) to call the tool.
3. Describe one failure you saw during testing (a wrong tool call, a missed read-back or an unspeakable output) and how you fixed it.

**Instructor example answers:**

1. Code: `github.com/<instructor>/voice-agents-course/blob/main/agents/s05_booking_agent.py`; demo: the lecture 5.8 solution video. The hardest criterion was number 5 (corrections). The first version heard "No, Thursday" and booked Thursday at the same time without checking availability. I added "If the caller changes the day or time, call find_available_slots again and read back the new details" to the booking rules and to the `find_available_slots` docstring. After that, the correction flow re-checked and re-confirmed every time in ten test calls.
2. "Book a new appointment. Only call this AFTER reading the details back and the caller clearly said yes. Args: patient_name: the patient's full name. phone: a ten digit callback phone number. slot_start: the exact slot_start returned by find_available_slots, e.g. 2026-10-06T09:30. reason: short reason for the visit." The first sentence says what the tool does; the second is the commit gate, repeated from the prompt because the model reads tool descriptions at the moment it decides to call a tool; the `slot_start` description stops the model inventing times or passing "Tuesday 10am" by tying the value to the previous tool's output.
3. When the caller gave a nine-digit phone number, the first version crashed with an unhandled `InvalidPhoneError`, and the caller heard nothing for several seconds before a generic apology. I wrapped the scheduler call in `try/except SchedulerError as exc: raise ToolError(str(exc))`. Now Riley says "That phone number doesn't look complete. Could you say the full ten digit number?", which is the scheduler's own speakable message.

**Solution resource:** Lecture 5.8 solution walkthrough and `03-code/agents/s05_booking_agent.py`.

---

## Assignment 3: Project 2: Phone receptionist

**Title:** Project 2: Put Riley on the phone (with a no-number path)

**Estimated duration:** 300 minutes

**Instructions:**

Put Riley behind a phone line. She answers with an AI disclosure, books appointments, answers FAQ questions from `faq.md`, confirms the caller-ID number instead of asking for it, transfers to a human when asked (destination from `TRANSFER_PHONE_NUMBER`, never chosen by the model), and hangs up cleanly after a goodbye.

Choose one path; both can earn full marks:

- **Path A (phone number):** Twilio number → Elastic SIP trunk → LiveKit inbound trunk → dispatch rule (`call-` room prefix, agent `riley-receptionist`) → your agent. Transfer reaches a real phone.
- **Path B (no phone number):** the same agent reached from a web client (React starter or explicit dispatch plus token) **and** from a free SIP softphone calling your LiveKit SIP URI through an authenticated inbound trunk. Transfer is demonstrated as the graceful "take a message" fallback.

Commit your SIP JSON files with secrets replaced by placeholders. Record a 4 to 6 minute demo (Path B: include both the web and softphone calls). The rubric (100 points, pass mark 70) is in `05-projects/project-2-phone-receptionist.md`.

**Attach:** `project-2-phone-receptionist.pdf`

**Questions:**

1. Which path did you take (A or B)? Paste your code and recording links and your call flow in one line.
2. Paste your dispatch rule (secrets removed) and explain how it makes sure only Riley, and only one Riley, joins each call.
3. What did you change for phone audio compared with the browser (endpointing, STT, prompts), and what did you observe that made you change it?

**Instructor example answers:**

1. Path A. Code: `agents/s08_telephony_agent.py`; recording: lecture 8.7 solution video. Call flow: `Caller → Twilio number → Elastic SIP trunk → LiveKit SIP → room call-_+1512..._xyz → riley-receptionist (PhoneRiley)`. I also recorded the Path B flow for students without a number: `Linphone → sip:+15550100@<project>.sip.livekit.cloud (auth trunk) → room call-... → riley-receptionist`.
2. `{"dispatch_rule": {"rule": {"dispatchRuleIndividual": {"roomPrefix": "call-"}}, "name": "riley-inbound", "roomConfig": {"agents": [{"agentName": "riley-receptionist"}]}}}`. `dispatchRuleIndividual` creates a new room for every call, so callers never share a conversation. `roomConfig.agents` explicitly dispatches one agent by name into that room; because the agent registers with `LIVEKIT_AGENT_NAME=riley-receptionist`, it is not auto-dispatched anywhere else, and no other agent on the project is sent to phone calls. I verified one agent participant per room in the LiveKit dashboard, and I stop my local dev agent before testing the deployed one so two servers never share the name.
3. On the phone, callers pause longer and the line adds delay, so Riley cut people off while they read out dates of birth. `create_session(..., telephony=True)` raises the minimum endpointing delay to at least 0.7 s, which removed the cut-offs in my test calls at the cost of about 200 ms per turn. I kept Deepgram Nova-3 with the dental keyterms because it handled the 8 kHz audio well on names like "Alvarez". In the prompt I added the phone rules (say you are transferring before calling `transfer_to_human`; say goodbye before `end_call`) and the caller-ID line, which cut the average booking by one question.

**Solution resource:** Lecture 8.7 solution video (Path A and Path B) and `03-code/agents/s08_telephony_agent.py`.

---

## Assignment 4: Project 3: Test suite for Riley

**Title:** Project 3: Build a voice agent test suite for Riley

**Estimated duration:** 300 minutes

**Instructions:**

A patient arrived for an appointment Riley "confirmed" but never booked: the model offered a time without calling the scheduler. Build a test suite that would have caught it, runs on every change, and reports in plain English whether Riley is safe to ship.

Write at least **15 new tests** (prefix `p3_`) across the voice testing pyramid:

- **Unit (4+):** scheduler edge cases plus two of `pii`, `wer`, `latency`, `costs`.
- **Behaviour (6+):** judged greeting; `find_available_slots` before any time is offered; `book_appointment` arguments after a clear "yes"; correction re-check; a `mock_tools` edge case; a safety test.
- **Evals (3+):** DeepEval conversational G-Eval, WER threshold, latency budget.
- **Simulated callers (2 personas):** several runs each with pass-rate thresholds (100% for the injection persona).
- **CI:** unit tests always; agent tests and evals when secrets exist; report uploaded as an artifact.

Prove the incident test works: show it red with the "Always use find_available_slots" rule removed and green with it restored. Write `projects/p3/TEST_REPORT.md`. The rubric (100 points, pass mark 70) is in `05-projects/project-3-test-suite.md`.

**Attach:** `project-3-test-suite.pdf`

**Questions:**

1. Paste links to your tests, your CI run and `TEST_REPORT.md`. How many tests do you have in each layer?
2. Show the test that would have caught the scenario's incident. Paste the red and green runs and explain what the test asserts.
3. Pick one threshold (judge, WER, latency or pass rate) and justify the number you chose.

**Instructor example answers:**

1. 21 new tests: 7 unit, 8 behaviour, 4 evals, 2 simulated-caller personas (3 runs each). CI: unit tests in about 2 seconds on every push; agent tests and evals on `main` with secrets, about 6 minutes, uploading `test-report.md` and failing transcripts as artifacts.
2. The test sends "Is ten o'clock on Tuesday free?" with the date pinned, skips an optional assistant message with `result.expect.skip_next_event_if(type="message", role="assistant")`, then asserts `result.expect.next_event().is_function_call(name="find_available_slots")`. With the rule removed from `BOOKING_RULES`, the run failed with "expected function_call find_available_slots, got message" because Riley answered "Yes, ten o'clock is available" straight away. With the rule restored it passed 5 out of 5 runs. The test asserts the order of events, not the wording, which is why it is stable.
3. WER at most 0.12 on the 20 reference utterances. Our current score with dental keyterms is 0.09, and without keyterms it is 0.16. A 0.12 threshold passes today with a little headroom for run-to-run variation, and it fails if someone removes the keyterms or switches to a weaker STT model, which is the regression we care about. We will lower it as we add more reference audio.

**Solution resource:** Lecture 9.11 solution walkthrough and the course's `03-code/tests/` folder.

---

## Assignment 5: Capstone: Riley, production receptionist

**Title:** Capstone: Ship Riley as a production AI receptionist

**Estimated duration:** 720 minutes

**Instructions:**

**Build it yourself first.** After lecture 13.1, stop watching Section 13 and build from the brief for up to **one week**. Lectures 13.2 to 13.5 are the reference solution; watch them only after your week, then write `DIFF_NOTES.md`.

Build `agents/capstone_riley.py`, combining everything from the course: voice-first prompt and disclosure; booking tools with read-backs; grounded FAQ; at least one specialist handoff (for example Riley → Billing); telephony with caller ID, transfer and hang-up; verification enforced in code, injection and impersonation resistance, PII redaction; metrics, cost per minute and traces; fallback providers and spoken error recovery; a production Docker image deployed to LiveKit Cloud or a container host, reachable by phone (or the Project 2 Path B equivalent); and tests in CI.

Run the 24 acceptance tests in the brief (at least 15 must pass), record a 3 to 5 minute demo, and write your README with the portfolio template. The rubric (100 points, pass mark 70, distinction 90) is in `05-projects/capstone-riley.md`.

**Attach:** `capstone-riley.pdf`

**Questions:**

1. Paste links to your repository, demo video and `ACCEPTANCE.md`. How many of the 24 acceptance tests pass, and did you complete the one-week build before watching the reference solution (yes / partly / no)?
2. Describe one production failure your system is designed to survive (a provider outage, an injection attempt, an impersonation call or a transfer failure). Show the evidence that it works.
3. Paste the "Decisions and trade-offs" section of your README, and one item from `DIFF_NOTES.md` where the reference solution changed your mind (or where you kept your own approach, and why).

**Instructor example answers:**

1. Repository: the course repo's `agents/s13_capstone_receptionist.py` plus tests; demo: lecture 13.5 recording; acceptance: 23 of 24 pass. AT-20 misses its $0.05 per minute target at $0.058 on phone calls because telephony minutes add about $0.013 per minute; web calls come in at $0.045. (For the reference solution the gate does not apply; in the example student write-up the answer is "yes: six days of build, then the reference".)
2. A TTS provider outage. I ran the chaos test from lecture 12.8 on a staging line: with a call in progress, I revoked the primary TTS key. The fallback TTS (`FALLBACK_TTS_MODEL=deepgram/aura-2`) took over on the next sentence; the caller heard a different voice but no silence, and the call completed its booking. With fallbacks disabled, the same test left the caller in silence until they hung up. Evidence: the demo video at 3:40, and the agent log lines showing the TTS error followed by the fallback provider handling the next utterance.
3. *Decisions:* "Cascaded over realtime: in Lab 4, cascaded was about 350 ms slower in perceived latency but roughly a quarter of the cost per minute, and it made 5 of 5 correct bookings versus 4 of 5. Verification in code, not prompt: `require_verification = True` makes reschedule and cancel refuse without `verify_caller`, so a jailbroken model still cannot change appointments. Local FAQ index over a vector DB: 16 sections, millisecond retrieval, no extra network hop." *DIFF_NOTES item:* "I used `with_filler(..., delay=0.5)`; the reference uses 0.8. After listening to ten calls, 0.5 triggered the filler on almost every lookup and made Riley sound slow, so I adopted 0.8."

**Solution resource:** Lectures 13.2 to 13.5 (reference solution) and `03-code/agents/s13_capstone_receptionist.py`.

---

## Assignment 6: Domain swap

**Title:** Domain swap: ship Riley for a restaurant, salon or law office

**Estimated duration:** 540 minutes

**Instructions:**

Re-skin your capstone for a new business, keeping the architecture and the tests. Choose one brief from `05-projects/challenges.md` (Challenge 13.7):

- **Restaurant ("Nonna's Table"):** table bookings by party size, events team for large parties, allergy notes without safety promises.
- **Hair salon ("Fade & Bloom"):** variable-length services per stylist, "anyone" searches, patch-test rule for first-time colour.
- **Law office ("Harbor Legal"):** consultations by practice area, conflict-check name before booking, client verification, no legal advice, urgent matters escalated.

Replace the FAQ, the business-logic module, the tool schema and the prompt; keep the patterns (read-back before commit, `ToolError`, userdata, verification in code) and adapt at least 15 capstone acceptance tests. Deliver a separate repository or folder, a 2 to 3 minute demo call, and a README using the capstone portfolio template plus a "What changed from Riley" table.

**Attach:** `challenges.pdf`

**Questions:**

1. Which business did you choose? Paste your links and your "What changed from Riley" table.
2. What is the biggest domain-specific risk for this business, and how does your agent handle it in code and in the prompt? Include the test that proves it.
3. Which capstone acceptance tests did you adapt, and which did not transfer? Explain one that needed a real redesign.

**Instructor example answers:**

1. The hair salon, "Fade & Bloom". *What changed:* FAQ rewritten (services, prices as ranges, stylists, policies); `salon.py` replaced `scheduler.py` with per-stylist hours and service durations; tools became `find_openings(service, stylist, day)`, `book_service`, `reschedule_service`, `cancel_service`; the prompt's identity, booking rules and escalation rules were rewritten; output rules, security rules, turn handling, telemetry, deployment and CI were unchanged.
2. Variable-length services: a 120-minute colour must fit a stylist's free time and hours, and first-time colour clients need a patch test 48 hours ahead. In code, `find_openings` only returns starts where the whole duration fits, and `book_service` raises a speakable `ToolError` if a first-time colour has no patch test on record. In the prompt, Riley mentions the patch test as soon as a new client asks for colour. Proof: the unit test `test_colour_needs_120_contiguous_minutes` and the behaviour test `test_first_colour_mentions_patch_test`.
3. 18 adapted: greeting, booking, no invented availability, correction, closed day, verification gate, late cancellation, FAQ grounding, unknown question, human escalation, transfer fallback, injection, impersonation, lockout, PII redaction, speakability, latency and simulated callers. AT-15 (medical emergency) did not transfer; I replaced it with "allergic reaction to hair dye", which routes to emergency services and never gives treatment advice. AT-02 needed a real redesign: "book a cleaning" became "book a colour with a specific stylist", which needed a stylist argument and a duration-aware slot check.

**Solution resource:** Lecture 13.7 walkthrough (instructor re-skins Riley for the salon brief).
