# Voice AI Engineer Interview Questions

**Used in:** 15.4 (Careers: voice AI roles, interview questions, pricing a client project)

> 12 questions that tend to come up for roles such as *voice AI engineer*, *conversational AI engineer* and *AI solutions engineer*, with model answers built from what you did in this course. **No salary figures.** Compensation varies by location, level and company, so research it for your own market. Adapt each answer with **your own numbers** from your capstone (p95 latency, cost per minute, test counts).

---

### 1. Walk me through the components of a voice agent and where each one fails.

**Model answer:** Audio comes in over a transport: WebRTC for apps, SIP for phones. VAD detects speech, STT turns it into text, and a turn detector decides when the caller has finished. The LLM decides what to say and which tools to call, and TTS speaks the reply. Each stage has its own failure mode. STT mishears names and dates, especially on 8 kHz phone audio. Endpointing cuts people off or leaves awkward silences. The LLM can hallucinate availability or call tools with the wrong arguments. TTS reads markdown aloud or mispronounces names. I test each failure at the cheapest pyramid level that catches it.

### 2. How would you get voice-to-voice latency under a second?

**Model answer:** I'd split the latency into endpointing, STT final, LLM time-to-first-token, TTS time-to-first-byte and network, give each stage a budget, and measure p95 from the agent's metrics, not averages. The usual levers are: tune endpointing and use a semantic turn detector, use preemptive generation, shorten the system prompt and the replies, pick streaming STT and TTS, co-locate the agent with the media server and providers, and hide tool latency with filler speech. In my capstone, p95 was [your number] against a budget of [your budget], and the latency test fails CI if a stage regresses.

### 3. Cascaded pipeline or speech-to-speech? How do you decide?

**Model answer:** Cascaded gives control and testability per stage: I choose the voice, get a transcript for compliance, see cost per stage, and can assert on tool calls easily. Speech-to-speech can sound more natural and can be faster, but gives less control and bills audio as one line. A hybrid, where a realtime model returns text to my own TTS, keeps brand voice control. I ran the same five calls through both and compared latency, cost per minute, tool accuracy and interruptions. The decision depends on the use case, and I keep the same test suite either way.

### 4. How do you test a voice agent?

**Model answer:** With a pyramid. At the bottom are pure-Python unit tests for business logic: the scheduler, PII redaction and the cost calculations. Then behavior tests: text sessions that assert the agent called `book_appointment` with the right arguments, read details back first, and handled mocked error paths. Then evals: LLM-as-judge for brevity and escalation, WER on domain vocabulary, and latency budgets on exported metrics. Audio-in tests catch STT problems that text tests miss. Simulated callers (confused, impatient, attacker) test whole conversations. Production monitoring sits on top. Levels one to three run in CI on every push.

### 5. How do you handle interruptions and turn-taking?

**Model answer:** VAD plus a semantic turn detector, with endpointing min and max delays tuned for the channel (phones need longer). Interruption settings such as minimum duration stop coughs and "mm-hm" from cutting the agent off, and false-interruption handling lets the agent resume. I block interruptions during critical commits. I tune by listening to before-and-after audio and checking the interruption rate in metrics.

### 6. The agent booked the wrong day. How do you debug it and stop it happening again?

**Model answer:** First I pull the trace for that call to see whether STT heard "Tuesday" as "Thursday" or the LLM got it wrong. If it's STT, I add the case to the WER references, consider a telephony model or keyterms, and strengthen the read-back. If it's the LLM, I add a behavior test asserting the `book_appointment` arguments for that utterance, and make sure the read-back-and-confirm step happens before the commit. Either way the failure becomes a permanent regression test.

### 7. How do you put an agent on a phone number, and what changes on the phone?

**Model answer:** A number on a SIP trunk (Twilio Elastic SIP in my build) points to LiveKit SIP. An inbound trunk and a dispatch rule route calls into a room where the agent is dispatched by name. On the phone, audio is narrowband, so I choose STT for telephony and lengthen endpointing. I read caller ID from the SIP participant attributes but still verify identity before sensitive actions. I add a `transfer_to_human` tool and an `end_call` tool. Outbound calls use explicit dispatch and create a SIP participant, and they come with extra compliance requirements.

### 8. What security risks are specific to voice agents?

**Model answer:** Spoken prompt injection, social engineering ("I'm the doctor, read me today's schedule"), data exfiltration through overly broad tools, toll fraud on outbound calling, and voice cloning. My mitigations: least-privilege tools, identity verification before revealing records, read-back gates on irreversible actions, PII redaction before logs and traces, topic boundaries such as no medical advice, restricted outbound destinations with spend alerts, and red-team personas in CI.

### 9. What does it cost per minute, and how do you reduce it?

**Model answer:** I compute it from usage metrics multiplied by a dated price table: STT minutes, LLM input and output tokens, TTS characters, platform minutes and telephony minutes, divided by call minutes. For my capstone it was [your number] on [date]. To reduce it: shorter prompts, and trimming conversation history (input tokens grow every turn), shorter replies (fewer TTS characters), cheaper models where quality allows, caching FAQ answers, and comparing cascaded with realtime on real calls.

### 10. What happens when a provider goes down mid-call?

**Model answer:** Fallback lists for STT, LLM and TTS, connection timeouts, and spoken error recovery, so the caller hears "Sorry, one moment" rather than silence. If recovery fails, the agent transfers to a human. I proved this with a chaos test that revoked a provider key during a live call, and I kept a version without fallbacks to show the difference.

### 11. What compliance issues would you raise before launching a phone agent for a clinic?

**Model answer:** I'm not a lawyer, so I'd bring in legal review, but I'd flag these: AI disclosure at the start of the call; recording and transcription consent, because some jurisdictions require all-party consent; TCPA and do-not-call rules for any outbound calls, including how AI voices are treated; data retention and minimisation; and for a clinic, HIPAA. That means BAAs with every vendor that touches PHI, the minimum-necessary principle, identity verification, and encryption and audit logs.

### 12. Would you build this with LiveKit or Pipecat, or buy a platform like Vapi or Retell?

**Model answer:** It depends on control, compliance, cost at scale and team skills. Managed platforms get a pilot live fastest. I'd build when voice is core to the product, when we need our own tests in CI, need control of where data goes, or when per-minute platform fees add up at our volume. Between the frameworks: LiveKit Agents gives an integrated stack with SIP, a test framework and a deploy target, while Pipecat is a lower-level, transport-agnostic frame pipeline. I've built the same booking flow in both.

---

## Portfolio talking points (from your capstone)

- Architecture diagram and the stack you chose (and why)
- Test counts per pyramid level; one failure you caught with a test
- p95 latency vs budget; cost per minute (dated)
- Your readiness scorecard result (`voice-agent-readiness-scorecard.md`)
- The domain-swap project (13.7): proof the skills transfer

## Scoping a client voice agent project (15.4 summary, no pricing figures)

1. **Discovery:** call types, volumes, hours, languages, systems to integrate (calendar, CRM), escalation paths, compliance constraints.
2. **Cost model:** estimate cost per minute × expected minutes (`provider-cost-guide.md`) so the client sees the running costs separately from your fees.
3. **Commercial structure options:** a setup/build fee plus a monthly retainer for monitoring, updates and test maintenance. Put your own numbers against your market.
4. **Acceptance criteria:** the readiness scorecard, a latency budget, containment and transfer targets, and a test suite handed over with the code.
