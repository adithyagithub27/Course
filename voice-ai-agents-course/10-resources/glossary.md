# Glossary

**Used in:** 1.2, 1.5 and throughout. Also the reference spelling list for captions (see `09-production/qa-checklist.md`).

| Term | Meaning (in this course) | Lecture |
|---|---|---|
| **Agent** (LiveKit) | The class that holds a voice agent's instructions, tools and optional per-agent model overrides | 3.2 |
| **AgentServer** | The LiveKit Agents process that registers with LiveKit and gets dispatched into rooms | 3.1 |
| **AgentSession** | The runtime that wires STT, LLM, TTS, VAD, turn handling and userdata for one conversation | 3.2 |
| **Barge-in** | The caller interrupting the agent while it speaks (see *interruption*) | 3.6 |
| **BAA** | Business Associate Agreement: a HIPAA contract with a vendor that handles PHI | 8.6 |
| **Cascaded pipeline** | STT → LLM → TTS as separate models | 1.3 |
| **Containment rate** | Share of calls fully handled by the agent without a human | 10.5 |
| **Cost per minute** | Total provider cost of a call divided by its length | 10.4 |
| **Dispatch / dispatch rule** | How LiveKit assigns an agent to a room; for SIP, the rule that routes inbound calls to rooms/agents | 3.1, 8.2 |
| **DNC** | Do-Not-Call lists (national/state registries and your internal list) | 8.6 |
| **Endpointing** | Deciding the caller has finished speaking; controlled by min/max delay | 3.6 |
| **EOU** | End of utterance: the point the system decides a turn ended; EOU delay is a key latency metric | 9.8, 10.1 |
| **Filler speech** | Short phrases spoken while a tool runs ("One moment…") to avoid dead air | 5.5 |
| **Function tool** | A Python method the LLM can call (`@function_tool`) | 5.1 |
| **G-Eval** | An LLM-as-judge evaluation method with custom criteria (used via DeepEval) | 9.6 |
| **Golden conversation** | A reference transcript used as an eval test case | 9.6 |
| **Half-cascade / hybrid** | Realtime model producing text, spoken by your own TTS | 6.3 |
| **Handoff** | Transferring the conversation from one agent to another (a tool returns a new `Agent`) | 7.5 |
| **HIPAA** | US health privacy law; applies to covered entities like dental clinics and their business associates | 8.6 |
| **Interruption** | Caller speech that stops the agent; tuned with `InterruptionOptions` | 3.6 |
| **IVR** | Interactive Voice Response: "press 1 for…" phone menus | 1.2 |
| **LiveKit** | Open-source real-time audio/video platform (SFU, SIP) with the LiveKit Agents Python framework | 3.1 |
| **LiveKit Inference** | LiveKit's gateway that accepts model strings like `"deepgram/nova-3"` | 2.1, 3.5 |
| **LLM-as-judge** | Using an LLM to grade another model's output against an intent or rubric | 9.3, 9.6 |
| **Mock mode** | `MOCK_MODE=1` in the course repo: scripted fake LLM with text I/O for zero-cost practice | 2.7 |
| **mock_tools** | LiveKit test helper that replaces tool implementations to force specific paths | 9.5 |
| **p50 / p95** | Median and 95th-percentile values; budgets use p95 | 9.8 |
| **PHI** | Protected Health Information (HIPAA) | 8.6 |
| **Pipecat** | Open-source Python framework that builds voice agents as pipelines of frame processors | 14.1 |
| **Preemptive generation** | Starting the LLM before the turn is fully confirmed, to cut latency | 3.6 |
| **PSTN** | Public Switched Telephone Network: the ordinary phone network | 8.1 |
| **RAG (for voice)** | Retrieval-augmented generation with short, speakable, grounded answers | 7.1 |
| **Read-back** | Repeating key details to the caller before committing an action | 5.4 |
| **Realtime model / speech-to-speech (S2S)** | One model that takes audio in and produces audio out (e.g., `gpt-realtime`) | 6.1 |
| **Room / participant / track** | LiveKit's session, the people or agents in it, and their audio/video streams | 3.1 |
| **RunContext** | Object passed to tools; gives access to `userdata`, filler speech, etc. | 5.1 |
| **SFU** | Selective Forwarding Unit: the media server that routes audio between participants | 3.1 |
| **Simulated caller** | An LLM persona that calls your agent in tests | 9.9 |
| **SIP** | Session Initiation Protocol: signalling used for internet telephony | 8.1 |
| **SIP trunk** | Connection between the phone network and your SIP endpoint (here: Twilio Elastic SIP Trunking → LiveKit SIP) | 8.2 |
| **STT** | Speech-to-text (here: Deepgram `nova-3`) | 3.5 |
| **TCPA** | US Telephone Consumer Protection Act: rules for automated/artificial-voice calls | 8.6 |
| **ToolError** | Exception with a speakable message for recoverable tool failures | 5.6 |
| **TTFB** | Time to first byte, for TTS: time until the first audio arrives | 1.4 |
| **TTFT** | Time to first token, for LLMs: time until the first output token | 1.4 |
| **TTS** | Text-to-speech (here: Cartesia `sonic-3`) | 3.5 |
| **Turn detector** | Model that decides whether the caller has finished their turn (`inference.TurnDetector()`) | 3.6 |
| **userdata** | Typed per-session state shared across tools and agents | 5.7 |
| **VAD** | Voice Activity Detection: detects speech vs silence (Silero) | 3.6 |
| **Voice-to-voice latency** | Time from the caller finishing speaking to hearing the agent's first audio | 1.4 |
| **Warm vs cold transfer** | Warm: the agent introduces the caller to the human; cold: the call is passed on directly | 8.4 |
| **WebRTC** | Browser/app real-time media standard used by LiveKit for non-phone clients | 1.2 |
| **WER** | Word error rate: (substitutions + deletions + insertions) ÷ reference words | 9.7 |

### Names to spell correctly in captions

LiveKit · LiveKit Agents · Pipecat · Deepgram · Cartesia · ElevenLabs · Silero · Twilio · Langfuse · OpenTelemetry · DeepEval · jiwer · `gpt-realtime` · GPT-4.1 mini · Riley · Maple Street Dental · Vapi · Retell · Bland
