# Project 2: Riley on the Phone

| Field | Details |
|---|---|
| **Section / lecture** | Section 8, lecture 8.7 (Udemy assignment) |
| **Estimated effort** | 3 to 6 hours (plus waiting time for number provisioning, if any) |
| **Difficulty** | Intermediate |
| **Builds on** | Project 1, lectures 7.2 and 8.1 to 8.6 |
| **Two paths** | **Path A**: real phone number (Twilio Elastic SIP trunk). **Path B**: no phone number (web client plus a direct SIP test). Both paths can earn full marks. |
| **You will submit** | Code link, a demo recording of a call, your LiveKit SIP configuration (secrets removed) and answers to three questions |

---

## Scenario

The booking pilot went well. Dana, the practice manager, now wants Riley to answer the clinic's overflow line: calls that ring more than four times at the front desk, and all calls after hours.

> "When someone calls, Riley answers, says it's the clinic's AI assistant, and handles bookings and simple questions. If the caller asks for a person, or Riley can't help, it transfers them to the front desk during opening hours. After hours it takes a message. And please, no one should have to spell out their phone number if we already have it from caller ID."

Some students cannot buy a phone number where they live, or cannot pass carrier verification in time. That is fine: Path B proves the same skills without a number.

---

## Requirements

Create `agents/p2_phone_agent.py`, starting from your Project 1 agent. You may now reuse the course mixins (`BookingToolsMixin`, `KnowledgeToolsMixin`, `TelephonyToolsMixin` from `agents/common.py`) or keep your own tools.

### Functional requirements (both paths)

| ID | Requirement |
|---|---|
| F1 | Registers with an **agent name** so it is dispatched explicitly, not to every room: uncomment `LIVEKIT_AGENT_NAME=riley-receptionist` in `.env` (`.env.example` leaves it unset for Sections 3 to 7 because named agents are not auto-dispatched to the Playground, and `dev` mode never reads `livekit.toml`). |
| F2 | The first sentence discloses that Riley is an AI assistant for Maple Street Dental. |
| F3 | Booking, rescheduling and cancelling work as in Project 1. |
| F4 | `lookup_clinic_info` answers hours, parking, insurance and pricing questions from `src/maple/data/faq.md`, and says "I'm not sure" when there is no match. |
| F5 | `transfer_to_human(reason)` transfers to the number in `TRANSFER_PHONE_NUMBER` (the destination is never chosen by the LLM). If transfer is unavailable (no SIP caller, number unset, transfer fails), Riley apologises and offers to take a message. |
| F6 | `end_call` hangs up only after Riley has said goodbye. |
| F7 | On SIP calls, Riley reads caller ID from the participant attribute `sip.phoneNumber` and asks the caller to confirm it instead of dictating ten digits. |
| F8 | Telephony tuning: minimum endpointing delay of at least 0.7 s on phone calls (see `build_turn_handling(settings, telephony=True)`), and a telephony-suited STT configuration. |

### Path A: real phone number

| ID | Requirement |
|---|---|
| A1 | A Twilio number routed through an Elastic SIP trunk whose origination URI is your LiveKit project's SIP URI. |
| A2 | A LiveKit inbound trunk for that number and a dispatch rule that sends each call to its own room (`call-` prefix) and dispatches `riley-receptionist`. |
| A3 | Transfer works to a real phone you control (Twilio trunk has call transfer / SIP REFER enabled, including PSTN transfer). |

### Path B: no phone number

| ID | Requirement |
|---|---|
| B1 | **Web client test:** the same agent (same agent name) is reached from a browser, using the React agent starter (`frontend/README.md`) or an explicit dispatch plus a room token, and completes a booking. |
| B2 | **Direct SIP test:** a LiveKit inbound trunk with username/password authentication and a made-up "number" (for example `+15550100`), called directly from a free SIP softphone (Linphone, MicroSIP or Zoiper) at `sip:+15550100@<your-project>.sip.livekit.cloud`. The dispatch rule from A2 routes it to Riley, so `sip.phoneNumber` and the SIP code paths run for real. |
| B3 | Transfer is demonstrated as the **graceful fallback** (no PSTN destination): Riley offers to take a message. Unit-test the fallback branch or show it in the recording. |

---

## Acceptance criteria

| # | Criterion | Path A evidence | Path B evidence |
|---|---|---|---|
| 1 | Riley answers within 2 seconds of pickup and discloses it is an AI | Phone call recording | Softphone recording |
| 2 | Only one agent joins each call, and only the named agent | `lk room list` / LiveKit dashboard screenshot | Same |
| 3 | Caller ID is offered back for confirmation | Recording | Softphone recording (softphone's user part appears as the number) |
| 4 | A full booking completes on the call | Recording | Web client recording **and** softphone recording |
| 5 | An FAQ answer ("Where do I park?") is grounded in the FAQ and one or two sentences long | Recording | Recording |
| 6 | An unknown question ("Do you do Botox?") gets "I'm not sure" plus an offer of a person or message | Recording | Recording |
| 7 | "Can I talk to a person?" leads to a spoken heads-up, then a transfer | Transfer reaches your phone | Graceful take-a-message fallback |
| 8 | The call ends cleanly with a goodbye and `end_call` | Recording + log | Recording + log |
| 9 | No secrets in the repo; SIP JSON files committed with credentials replaced by placeholders | Repo | Repo |
| 10 | Endpointing on phone calls is at least 0.7 s minimum delay | Code | Code |

---

## Setup reference

### LiveKit SIP configuration (both paths)

These JSON files are **not shipped** in `03-code/`. You create them yourself in a `telephony/` folder at the repo root while following lecture 8.2 (`inbound-trunk.json`, `dispatch-rule.json`); lecture 8.5 adds `outbound-trunk.json`. If you skipped those lectures, create them from the examples below.

`telephony/inbound-trunk.json` (Path A: use your Twilio number; Path B: add auth and a made-up number):

```json
{
  "trunk": {
    "name": "Maple Street Dental inbound",
    "numbers": ["+1XXXXXXXXXX"],
    "krispEnabled": true
  }
}
```

Path B variant:

```json
{
  "trunk": {
    "name": "Maple Street Dental softphone test",
    "numbers": ["+15550100"],
    "authUsername": "riley-test",
    "authPassword": "<choose-a-long-password>"
  }
}
```

`telephony/dispatch-rule.json` (the trunk ID comes from the `lk sip inbound create` output and starts with `ST_`):

```json
{
  "dispatch_rule": {
    "name": "Riley inbound",
    "trunk_ids": ["ST_REPLACE_WITH_YOUR_TRUNK_ID"],
    "rule": { "dispatchRuleIndividual": { "roomPrefix": "call-" } },
    "roomConfig": { "agents": [ { "agentName": "riley-receptionist" } ] }
  }
}
```

```bash
lk sip inbound create telephony/inbound-trunk.json
lk sip dispatch create telephony/dispatch-rule.json
lk sip inbound list
lk sip dispatch list
uv run agents/p2_phone_agent.py dev
```

Your project's SIP URI is shown in the LiveKit Cloud dashboard under the project's settings (it looks like `sip:xxxxxxxx.sip.livekit.cloud`).

### Path A: Twilio

1. Buy a voice-capable number (a trial account works; trial calls play a short Twilio message first).
2. Create an **Elastic SIP trunk**. Under **Origination**, add your LiveKit SIP URI.
3. Under the trunk's **Numbers**, attach your number.
4. Under **General**, enable **Call Transfer (SIP REFER)** and **PSTN transfer** so `transfer_to_human` can reach a real phone.
5. Set `TRANSFER_PHONE_NUMBER=+1YYYYYYYYYY` (your mobile) in `.env`.

### Path B: softphone

1. Install Linphone, MicroSIP or Zoiper.
2. Add an account with username `riley-test`, the password from your trunk JSON, and domain `xxxxxxxx.sip.livekit.cloud`. If your softphone insists on registering, turn registration off; you only need outbound calls. If UDP 5060 is blocked on your network, switch the transport to TCP.
3. Dial `+15550100` (the softphone sends it to your LiveKit SIP domain).
4. For the web client, follow `frontend/README.md`, making sure the starter dispatches `riley-receptionist`. Alternatively, create a dispatch and a token by hand:

```bash
lk dispatch create --new-room --agent-name riley-receptionist
lk token create --join --room <room-name-from-previous-output> --identity tester --valid-for 1h
```

Then join that room from the Agents Playground or LiveKit Meet using your project URL and the token.

---

## Deliverables

| # | Deliverable |
|---|---|
| D1 | `agents/p2_phone_agent.py` |
| D2 | `telephony/inbound-trunk.json` and `telephony/dispatch-rule.json` (from lecture 8.2) with secrets replaced by placeholders |
| D3 | Demo recording (4 to 6 minutes) covering acceptance criteria 1 and 3 to 8. Path B: include both the web client and the softphone call |
| D4 | `projects/p2/NOTES.md`: your path (A or B), the call flow diagram in one line (for example `Caller → Twilio → LiveKit SIP → room call-XXXX → riley-receptionist`), and the tuning values you chose with a sentence of justification |

---

## Grading rubric (100 points)

| Criterion | Excellent | Good | Needs work |
|---|---|---|---|
| **Call routing** (20) | 18-20: Named agent dispatched by rule to a per-call room; exactly one agent per call; config committed without secrets | 12-17: Works, but config is undocumented or rooms are shared between calls | 0-11: Agent joins every room, or calls are not answered |
| **Telephony UX** (20) | 18-20: Disclosure in first sentence; caller ID confirmed; endpointing tuned for phone; no cut-offs in the demo | 12-17: One of these is missing or rough | 0-11: Callers are cut off or asked to dictate known numbers |
| **Booking and FAQ on the call** (20) | 18-20: Full booking and grounded FAQ answers; honest "I'm not sure" | 12-17: Works with minor issues (long answers, one unnecessary question) | 0-11: Booking fails or FAQ answers are invented |
| **Transfer and hang-up** (20) | 18-20: Path A transfer reaches a phone after a spoken heads-up; Path B fallback is graceful and tested; `end_call` after goodbye | 12-17: Transfer or fallback works but without a heads-up, or hang-up is abrupt | 0-11: Transfer destination chosen by the LLM, or failures leave the caller in silence |
| **Evidence and notes** (20) | 18-20: Recording covers every required criterion; notes justify tuning with observations | 12-17: Recording misses one criterion or notes are generic | 0-11: No working recording |

**Pass mark:** 70/100. Path A and Path B are graded on the same scale.

---

## Hints

1. Test in the browser first. If booking does not work on the web, it will not work on the phone.
2. Most "agent never joins" problems are an agent-name mismatch between `LIVEKIT_AGENT_NAME` and the dispatch rule, or `LIVEKIT_AGENT_NAME` still commented out in `.env`. Run `lk sip dispatch list` and compare character by character with the name in the agent's start-up log.
3. Most "transfer fails" problems on Path A are SIP REFER or PSTN transfer not enabled on the Twilio trunk.
4. `caller_number()` and `find_sip_participant()` in `agents/common.py` show how to read `sip.phoneNumber` and find the phone participant.
5. Tell the caller what is happening before transferring ("I'm transferring you to the front desk now"), then wait for playout (`context.wait_for_playout()`) so the sentence is not cut off.
6. Twilio trial accounts can only call verified numbers and play a trial message on inbound calls. That is expected; mention it in your notes.
7. If you record calls, say so in the greeting and check your local consent rules (lecture 8.6).

---

## Submission (Udemy assignment)

Submit through the **Project 2: Phone receptionist** assignment in lecture 8.7. The full Udemy entry, including the instructor's example answers, is in `06-assessments/assignments.md`.

**Assignment questions:**

1. Which path did you take (A or B)? Paste your code and recording links and your call flow in one line.
2. Paste your dispatch rule (secrets removed) and explain how it makes sure only Riley, and only one Riley, joins each call.
3. What did you change for phone audio compared with the browser (endpointing, STT, prompts), and what did you observe that made you change it?

**Instructor example solution (what a strong submission looks like):** The reference is `agents/s08_telephony_agent.py`, which combines the booking, knowledge and telephony mixins, uses `build_turn_handling(settings, telephony=True)` (minimum endpointing 0.7 s), waits for the caller with `ctx.wait_for_participant()`, reads caller ID with `caller_number(participant)` when the participant is a SIP participant, passes it to `PhoneRiley(caller_id=...)` so the prompt offers it back, and transfers to `settings.transfer_sip_uri` through `TelephonyToolsMixin`. The example Path A demo shows a Twilio call answered in about 1.5 s with an AI disclosure, Riley offering the caller-ID number back ("Is five one two, five five five, zero one six one the best number for you?"), a completed booking, a parking FAQ answer, and a transfer to the instructor's mobile after "Can I speak to someone?". The example Path B demo shows the same booking from the React starter, then a Linphone call to `+15550100` in which "Do you do Botox?" gets "I'm not sure" and "Can I talk to a person?" gets the take-a-message fallback because no PSTN transfer destination exists.

---

## Peer-review checklist

- [ ] The recording shows the call being answered with an AI disclosure in the first sentence.
- [ ] Exactly one agent joins the call, and it is the named agent.
- [ ] Caller ID is used (offered back for confirmation) on SIP calls.
- [ ] A booking completes on the call without the caller repeating information.
- [ ] FAQ answers are short and match `faq.md`; unknown questions get an honest "I'm not sure".
- [ ] Transfer (Path A) or the graceful fallback (Path B) happens after a spoken heads-up.
- [ ] The call ends with a goodbye, not silence.
- [ ] SIP JSON files are committed without passwords or real personal numbers.
- [ ] Endpointing for phone calls is tuned and justified in the notes.
- [ ] One thing I would copy from this submission: ______
- [ ] One suggestion: ______
