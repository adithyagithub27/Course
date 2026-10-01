# Quiz: Telephony (Section 8)

| Field | Value |
|---|---|
| Udemy lecture | 8.8 Quiz: Telephony |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 8.1 to 8.6 |

---

### Q1. You call your new Twilio number. It rings, LiveKit shows a new room with a SIP participant, but Riley never joins. The agent is running with `LIVEKIT_AGENT_NAME=riley-receptionist`. What is the most likely cause?

*Related lecture: 8.2 Inbound calls: Twilio trunk + LiveKit dispatch rule*

- **A.** The Twilio number is not verified.
  - *Explanation:* Incorrect. The call reached LiveKit and created a room, so the Twilio side is working.
- **B.** STT does not support 8 kHz audio.
  - *Explanation:* Incorrect. That would cause poor recognition after Riley joins, not a missing agent.
- **C.** The agent needs a public IP address so LiveKit can reach it.
  - *Explanation:* Incorrect. Agents connect out to LiveKit; no public IP is needed.
- **D.** The dispatch rule's `roomConfig.agents[].agentName` does not match `riley-receptionist`, so LiveKit never dispatches this named agent to the call's room.
  - *Explanation:* Correct. Named agents are not auto-dispatched. The dispatch rule must name exactly the same agent. Check with `lk sip dispatch list` and compare with your agent's name.

**Correct answer: D**

---

### Q2. Riley works well in the browser, but on the phone it cuts off callers who pause while reading a long insurance ID, and it keeps asking callers for their phone number. Which pair of changes from lecture 8.3 addresses both issues?

*Related lecture: 8.3 Phone-specific tuning*

- **A.** Raise the minimum endpointing delay for telephony (the course uses at least 0.7 s), and read the caller's number from the SIP participant's `sip.phoneNumber` attribute to offer it for confirmation ("Is this the best number to reach you?").
  - *Explanation:* Correct. Phone callers pause more and lines add delay, so a slightly longer endpointing floor reduces cut-offs. Caller ID from the SIP attributes lets Riley confirm the number instead of asking for all ten digits.
- **B.** Switch to a realtime model and remove the phone number from the booking flow.
  - *Explanation:* Incorrect. Changing architecture is a big step that does not address the root causes, and the clinic needs a callback number.
- **C.** Lower the endpointing delay so Riley answers faster, and trust caller ID without confirming it.
  - *Explanation:* Incorrect. A shorter delay makes cut-offs worse, and caller ID can be withheld, spoofed or belong to someone else, so confirm it.
- **D.** Increase the TTS speaking rate so callers have less time to pause.
  - *Explanation:* Incorrect. Speaking rate has no effect on how Riley detects the end of the caller's turn.

**Correct answer: A**

---

### Q3. The `transfer_to_human` tool runs, and the log shows the SIP transfer request, but the call fails instead of reaching the front desk. The LiveKit side is configured correctly. What should you check on the Twilio Elastic SIP trunk?

*Related lecture: 8.4 Transfer to a human and ending calls*

- **A.** That the trunk has a recording policy enabled.
  - *Explanation:* Incorrect. Recording is unrelated to transfers.
- **B.** That the trunk uses a US region.
  - *Explanation:* Incorrect. Region affects media routing, not whether transfers are permitted.
- **C.** That call transfer (SIP REFER) is enabled on the trunk, including transfers to the PSTN if the destination is a regular phone number.
  - *Explanation:* Correct. `transfer_sip_participant` performs a SIP REFER (a cold transfer). Twilio rejects REFER unless call transfer is enabled on the trunk, and PSTN destinations need the PSTN transfer option too.
- **D.** That the trunk's origination URI points to the front desk number.
  - *Explanation:* Incorrect. The origination URI must point to your LiveKit SIP endpoint, otherwise inbound calls would never reach Riley.

**Correct answer: C**

---

### Q4. Your outbound reminder script dispatches Riley and places the call with `CreateSIPParticipant`. About a third of calls reach voicemail. What is the best way to handle that?

*Related lecture: 8.5 Outbound calls: appointment reminders*

- **A.** Hang up immediately whenever there is no answer within two rings.
  - *Explanation:* Incorrect. That makes the reminder useless for anyone who doesn't pick up quickly.
- **B.** Have Riley recognise a voicemail greeting, leave a short message with who is calling, the appointment day and time and the clinic's callback number, then end the call, and log the outcome so the clinic knows it was not a live confirmation.
  - *Explanation:* Correct. This matches the course's `REMINDER_CALL_EXTRA` instructions: brief, identifies the clinic, includes a callback number, and ends cleanly. Keep sensitive details out of voicemail.
- **C.** Keep talking as if a person answered, and wait for replies.
  - *Explanation:* Incorrect. Riley would talk to a recording, waste minutes and produce a confusing message.
- **D.** Call again every five minutes until someone answers.
  - *Explanation:* Incorrect. Repeated calls annoy patients and can breach calling-frequency rules and clinic policy.

**Correct answer: B**

---

### Q5. The clinic wants Riley to place outbound reminder calls to patients' mobile phones using an AI-generated voice. Which statement best reflects lecture 8.6 (not legal advice)?

*Related lecture: 8.6 Compliance: disclosure, consent and recording*

- **A.** No rules apply because the calls are reminders, not sales calls.
  - *Explanation:* Incorrect. Non-marketing calls still have requirements; some healthcare-message exemptions exist, but they come with conditions.
- **B.** Only the clinic's own privacy policy matters.
  - *Explanation:* Incorrect. Federal and state rules apply regardless of the clinic's own policy.
- **C.** Consent is only needed if the call is recorded.
  - *Explanation:* Incorrect. Recording consent (one-party or two-party, depending on the state) is a separate question from consent to receive AI-voice calls.
- **D.** In the US, calls using an AI-generated voice are treated as "artificial or prerecorded voice" calls under the TCPA, so you need the right prior consent, must identify the caller, and must honour opt-outs; check recording-consent rules too, and get legal review.
  - *Explanation:* Correct. The FCC confirmed in 2024 that AI-generated voices fall under the TCPA's artificial-voice rules. Combine consent tracking, clear disclosure, do-not-call handling and a lawyer's review before launching outbound calls.

**Correct answer: D**
