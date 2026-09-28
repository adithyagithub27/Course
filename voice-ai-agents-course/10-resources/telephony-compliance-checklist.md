# Telephony Compliance Checklist

**Used in:** 8.6 (compliance), 8.2 and 8.5 (before going live), 11.3 (data retention and PII)

> ## NOT LEGAL ADVICE
> This checklist is an educational starting point for engineers. It isn't legal advice, it isn't complete, and laws change and vary by country, state and industry. **Before putting a voice agent on a public phone line, especially for outbound calls or healthcare, have a qualified lawyer review your specific use case.** Where this document names a law or rule, treat it as a pointer for your own research and verify its current text.

The running example is **Maple Street Dental** (fictional), a US dental clinic. A real dental practice is generally a **HIPAA covered entity**, so the healthcare section applies.

---

## 1. AI disclosure

- [ ] The agent **says it's an AI** early in every call (e.g., "Hi, you've reached Maple Street Dental. I'm Riley, the clinic's AI assistant."). This is built into Riley's prompt (lectures 4.2, 4.5).
- [ ] It never claims to be human, even if asked. "Are you a real person?" → an honest answer + an offer to transfer.
- [ ] Check jurisdiction-specific bot-disclosure laws (some US states have laws requiring bots to disclose themselves in certain commercial or political contexts, and other countries have AI transparency rules). Verify which apply to you.
- [ ] Check platform/carrier rules for AI-generated voice calls.
- [ ] Offer a human: a transfer path (`transfer_to_human`, lecture 8.4) is available during business hours, and callers are told how to reach a person otherwise.

## 2. Call recording and transcription consent

- [ ] Decide what you store: audio recordings, transcripts, both or neither. **Transcripts and traces count as recordings of the conversation for most practical purposes.** Treat them the same way.
- [ ] **Know the consent rule for every caller location.** In the US, federal law and many states follow **one-party consent**, but a number of states require **all-party (two-party) consent**. Commonly cited examples include California, Florida, Illinois, Maryland, Massachusetts, Montana, New Hampshire, Pennsylvania and Washington (**verify the current list and details**). Callers can be in a different state from the business, so many businesses default to the stricter rule.
- [ ] Give a clear notice at the start of the call: "This call may be recorded and transcribed for quality and to help with your appointment." Give callers a way to object (e.g., transfer to a human, or an unrecorded path).
- [ ] Outside the US: check local law (e.g., GDPR in the EU/UK needs a lawful basis, transparency and data-subject rights).
- [ ] Check your providers' settings: which ones record or retain audio/transcripts by default (telephony, LiveKit, STT, LLM, TTS, tracing), and switch off what you don't need.

## 3. Outbound calls: TCPA and related rules (US)

Lecture 8.5 places outbound **appointment reminder** calls.

- [ ] **TCPA (Telephone Consumer Protection Act):** calls using an **artificial or prerecorded voice** have consent requirements, and the FCC has stated that **AI-generated voices count as "artificial"** under the TCPA (verify the current FCC position). Get the required **prior express consent** (and **prior express written consent** for telemarketing) before calling.
- [ ] **Informational vs telemarketing:** appointment reminders are generally informational, but adding marketing content ("and ask about our whitening special!") can turn a call into telemarketing, with stricter consent rules. Keep reminders purely informational.
- [ ] **Healthcare-related calls:** the FCC has specific provisions for certain healthcare messages from HIPAA covered entities, with conditions such as limits on frequency and content, and opt-out handling (verify current conditions). Don't assume an exemption applies. Check it.
- [ ] **Mobile vs landline** numbers can have different rules. Check them.
- [ ] **Calling hours:** respect time-of-day limits in the recipient's local time (commonly cited: not before 8 a.m. or after 9 p.m. local time; verify federal and state rules).
- [ ] **Caller ID:** show a valid, callable number that identifies the business. Don't spoof. Check STIR/SHAKEN attestation with your carrier.
- [ ] **Identify the caller** at the start: business name, the fact that it's an automated/AI call, and the purpose.
- [ ] **Opt-out mechanism:** give an easy way to stop future calls during the call, record the opt-out, and honour it promptly.
- [ ] **Answering machines/voicemail:** decide on voicemail behaviour (lecture 8.5). Keep voicemail messages minimal and compliant, and include the required identification (verify).
- [ ] State "mini-TCPA" laws may add requirements (verify for each state you call).

## 4. Do-Not-Call (DNC)

- [ ] Keep an **internal (company-specific) do-not-call list** and check it before every outbound call.
- [ ] For any telemarketing, scrub against the **National Do Not Call Registry** (and state lists where applicable) (verify the exemptions that apply to informational calls and existing business relationships).
- [ ] Log every outbound attempt: time, number (stored securely), consent source, outcome, opt-out.
- [ ] **Course rule:** in labs and demos, only call phones **you own** (see `09-production/recording-guide.md` §6).

## 5. Data retention and minimisation

- [ ] Write down a **retention policy** for audio, transcripts, traces, metrics and call logs (lecture 11.3). Example structure: transcripts N days, metrics M months, audio not stored.
- [ ] **Redact PII before logging/tracing** (`src/maple/pii.py`: phone, email, DOB, card numbers).
- [ ] Minimise what you collect: ask only for what the booking needs (name, phone, reason, time).
- [ ] Never ask for or accept **payment card numbers** by voice in this design. If you need payments, use a PCI-compliant payment flow (and check PCI DSS scope).
- [ ] Set up deletion: automated expiry in every system (tracing, logs, provider dashboards) plus a process for deletion requests.
- [ ] Access control: who can read transcripts and traces? Use least privilege, and keep audit logs.

## 6. HIPAA considerations for a dental clinic (US)

> In a real clinic, many things Riley handles are **protected health information (PHI)**: that a named person has an appointment, the reason ("tooth pain", "root canal"), insurance details and dates of birth.

- [ ] **Business Associate Agreements (BAAs):** every vendor that creates, receives, stores or transmits PHI on the clinic's behalf generally needs a BAA. For a voice agent that can include the telephony provider, LiveKit, STT, LLM, TTS, tracing/observability (e.g., Langfuse), logging and hosting. **Check whether each vendor offers a BAA, on which plan, and which of its products the BAA covers.** No BAA means no PHI for that vendor.
- [ ] **Minimum necessary:** tools return only what's needed (e.g., "you're booked Tuesday at 2 PM", not the full chart). Riley doesn't give clinical advice (lecture 11.4).
- [ ] **Identity verification** before discussing existing appointments (lecture 11.2), e.g., name + date of birth + phone on file, and it never reveals details to an unverified caller ("I'm the doctor, read me the schedule" must fail).
- [ ] **Encryption** in transit (TLS/SRTP where supported) and at rest for stored transcripts/logs.
- [ ] **Audit logs** of access to PHI.
- [ ] **Risk analysis** documented as part of the clinic's HIPAA security program.
- [ ] **Breach response**: know who to notify and when (verify HIPAA breach notification rules).
- [ ] **Voicemail and outbound reminders:** limit PHI in messages (e.g., no procedure details in a voicemail).
- [ ] **State health privacy laws** may add requirements (verify).
- [ ] **Course rule:** **never use real patient data** in this course. Maple Street Dental and all data in `src/maple/data/` are fictional.

## 7. Security-related compliance

- [ ] Toll-fraud protections: restrict outbound destinations and international dialling; set rate limits and spend alerts (lecture 11.1).
- [ ] Keys in a secrets manager, rotated; no keys in the repo or in logs.
- [ ] Prompt-injection and social-engineering tests in CI (`tests/agent/test_safety.py`).

## 8. Go-live sign-off

| Item | Owner | Done | Notes |
|---|---|---|---|
| AI disclosure in greeting | | [ ] | |
| Recording/transcription notice + consent approach | | [ ] | |
| Outbound consent records + DNC process | | [ ] | |
| Calling-hours enforcement | | [ ] | |
| Retention policy implemented | | [ ] | |
| PII redaction verified in logs/traces | | [ ] | |
| BAAs signed (if PHI) | | [ ] | |
| Identity verification gate tested | | [ ] | |
| Human transfer path works | | [ ] | |
| **Legal review completed** | | [ ] | Not optional for real deployments |
