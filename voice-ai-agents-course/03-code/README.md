# voice-agents-course

Student code for **Production Voice AI Agents with Python: Build, Test, Deploy**.

You will build **Riley**, the AI phone receptionist for *Maple Street Dental* (a fictional
clinic). Riley answers questions, books, reschedules and cancels appointments, transfers
callers to a human, and runs on a real phone number, with a test suite and dashboards to
prove it works.

> **Version note.** APIs verified on **livekit-agents 1.8.3** and **pipecat-ai 1.12.0**
> (September 2026). Older tutorials that use `WorkerOptions(entrypoint_fnc=...)`,
> `room_input_options=`, `MultilingualModel()` from `livekit.plugins.turn_detector`, or
> Pipecat's `openai_llm_context` module will not work with these versions. If a newer
> release breaks something, check this README and the course Q&A first.

---

## Quick start

```bash
git clone <your fork> voice-agents-course && cd voice-agents-course
cp .env.example .env              # fill in keys (see "Accounts" below)
make install                      # uv sync --extra dev   (or: make install PIP=1)
make test                         # offline unit tests, no keys needed
make download-files               # VAD + turn-detector weights, once
make console AGENT=agents/s03_hello_agent.py        # talk to Riley through your mic
```

No keys yet? Practise for free with the scripted mock LLM (lecture 2.7):

```bash
make mock AGENT=agents/s05_booking_agent.py         # MOCK_MODE=1 ... console --text
```

Hear the finished product first (lecture 2.6):

```bash
make console AGENT=agents/s13_capstone_receptionist.py
```

### Without uv

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python agents/s03_hello_agent.py download-files
python agents/s03_hello_agent.py console
```

Every agent file supports the same commands:

| Command | What it does |
|---|---|
| `console` | Talk locally through your microphone and speakers. `console --text` to type. |
| `dev` | Register with LiveKit Cloud, hot reload; connect from the Agents Playground or web starter. |
| `start` | Production mode (used by the Docker image). |
| `connect` | Join a specific room. |
| `download-files` | Pre-download model weights. |

---

## Accounts and cost

| Service | Used for | Free tier / typical student spend |
|---|---|---|
| LiveKit Cloud | Rooms, agent hosting, LiveKit Inference (STT/LLM/TTS), SIP | Free tier covers the course labs |
| OpenAI | LLM for tests and evals, Realtime (Section 6), Pipecat | Pay as you go; ~$3-8 for the course |
| Deepgram | STT in `plugins` mode, audio-in eval, Pipecat | Starter credit |
| Cartesia | TTS in `plugins` mode, Pipecat | Starter credit |
| Twilio | Phone number + Elastic SIP trunk (Section 8) | Trial credit |

Budget for the whole course: **about $10-20**. Set spending caps before you start
(lecture 2.7). Rough per-minute costs for Riley, from `src/maple/costs.py`
(placeholder prices, update them from your invoices):

```python
from maple.costs import cost_per_minute, typical_cascaded_usage, typical_realtime_usage
cost_per_minute(typical_cascaded_usage(3))   # ~ $0.06 / min cascaded (web call)
cost_per_minute(typical_realtime_usage(3))   # ~ $0.16 / min realtime (speech-to-speech)
```

Zero-cost options: `MOCK_MODE=1`, `make test`, `python tests/evals/stt_wer_eval.py`,
`python tests/evals/latency_report.py`, `python tests/evals/simulated_caller.py --mock`.

### Two ways to reach models

- `MAPLE_PROVIDER_MODE=inference` (default): model strings such as `deepgram/nova-3`,
  `openai/gpt-4.1-mini`, `cartesia/sonic-3` go through **LiveKit Inference** and bill to your
  LiveKit project. Only `LIVEKIT_*` keys are needed to run agents.
- `MAPLE_PROVIDER_MODE=plugins`: direct provider plugins with your own `OPENAI_API_KEY`,
  `DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`.

All model names live in `src/maple/config.py` and can be changed in `.env`.

---

## Repository layout

```
src/maple/        pure-Python business logic (no network, fully unit-tested)
agents/           LiveKit agents, one file per section; agents/common.py holds shared tools
pipecat/          the same booking flow in Pipecat (Section 14)
tests/unit/       offline unit tests for src/maple
tests/agent/      LiveKit behavior tests (live ones need OPENAI_API_KEY; mock-LLM ones run offline)
tests/evals/      DeepEval judge, WER, latency, simulated callers, audio-in eval
tests/data/       golden conversations, STT references, sample metrics, audio/README.md
deploy/           Dockerfile and .dockerignore
frontend/         how to put a web UI in front of Riley
```

## Lecture → file map

| Lectures | File(s) |
|---|---|
| 1.5, 2.2, 2.4 | `README.md`, `Makefile`, `pyproject.toml`, `.env.example`, `tests/unit/` |
| 2.6 | `agents/s13_capstone_receptionist.py` (`make console AGENT=...`) |
| 2.7 | `MOCK_MODE` in `src/maple/config.py`, `ScriptedLLM` in `agents/common.py` |
| 3.3-3.7 | `agents/s03_hello_agent.py`, `src/maple/config.py` |
| 3.9 | `agents/s03_hello_agent.py` with `BROKEN=short_endpointing \| long_endpointing \| no_interruptions \| markdown \| wrong_stt` |
| 4.2-4.5 | `src/maple/prompts.py`, `agents/s04_voice_prompting.py` |
| 5.2 | `src/maple/scheduler.py`, `tests/unit/test_scheduler.py` |
| 5.3-5.7 | `agents/s05_booking_agent.py`, `agents/common.py` (`BookingToolsMixin`, `CallState`) |
| 5.9 | `join_waitlist` in `agents/s05_booking_agent.py`, `ClinicScheduler.add_to_waitlist` |
| 6.2-6.4 | `agents/s06_realtime_agent.py` (`REALTIME_HYBRID=1` for 6.3) |
| 7.1-7.3 | `src/maple/knowledge.py`, `src/maple/data/faq.md`, `agents/s07_knowledge_agent.py` |
| 7.5-7.6 | `agents/s07_multi_agent.py` |
| 7.8 | `agents/s07_knowledge_agent.py` with `LANGUAGE=es` or `LANGUAGE=hi` (`FOLLOW_CALLER_LANGUAGE=1` for mid-call switching) |
| 8.2-8.4 | `agents/s08_telephony_agent.py`, `livekit.toml.example` |
| 8.5 | `agents/s08_outbound_call.py` (`dispatch` sub-command) |
| 9.3 | `tests/agent/test_greeting.py`, `tests/agent/conftest.py` |
| 9.4-9.5 | `tests/agent/test_booking_flows.py`, `tests/agent/test_mock_mode.py` |
| 9.6 | `tests/evals/test_conversation_quality.py`, `tests/data/golden_conversations.json` |
| 9.7 | `tests/evals/stt_wer_eval.py`, `src/maple/wer.py`, `tests/data/stt_references.json` |
| 9.8 | `tests/evals/latency_report.py`, `src/maple/latency.py`, `tests/data/sample_metrics.jsonl` |
| 9.9 | `tests/evals/simulated_caller.py` |
| 9.10 | `.github/workflows/ci.yml` |
| 9.13 | `tests/evals/audio_in_eval.py`, `tests/data/audio/README.md` |
| 9.14 | `on_simulation_end` in `agents/s13_capstone_receptionist.py` |
| 10.2-10.4 | `agents/s10_observed_agent.py`, `src/maple/costs.py` |
| 11.2-11.4 | `agents/s11_guarded_agent.py`, `src/maple/pii.py` |
| 11.5 | `tests/agent/test_safety.py`, `simulated_caller.py --persona injection_attacker` |
| 12.2 | `deploy/Dockerfile`, `deploy/.dockerignore` |
| 12.5 | `frontend/README.md` |
| 12.8 | `agents/s12_chaos_demo.py` (kill switch: `touch /tmp/riley-kill-llm`) |
| 13.x | `agents/s13_capstone_receptionist.py`, whole `tests/` tree |
| 13.4 | `tests/agent/test_capstone.py` |
| 14.2 | `pipecat/s14_pipecat_bot.py` |

## Names you will see in the lectures

| Kind | Names |
|---|---|
| Agent classes | `HelloRiley` (s03), `VoiceFirstRiley` (s04), `RileyBookingAgent` (s05), `RealtimeRiley` (s06), `KnowledgeRiley` (s07), `GreeterAgent` / `BookingAgent` / `BillingAgent` (s07 multi), `PhoneRiley` (s08), `ReminderRiley` (s08 outbound), `ObservedRiley` (s10), `GuardedRiley` (s11), `CapstoneRiley` / `BillingSpecialist` (s13) |
| Tools | `find_available_slots`, `book_appointment`, `reschedule_appointment`, `cancel_appointment`, `join_waitlist`, `lookup_clinic_info`, `verify_caller`, `get_my_appointments`, `transfer_to_human`, `end_call`, `transfer_to_booking`, `transfer_to_billing`, `back_to_front_desk`, `back_to_riley` |
| Userdata | `CallState` fields: `caller_name`, `caller_phone`, `caller_id_number`, `visit_reason`, `last_offered_slots`, `appointment_id`, `identity_verified`, `verified_phone`, `failed_verifications`, `transfer_requested`, `silence_prompts`, `call_outcome`, `notes` |
| Helpers | `create_session()`, `build_stt()`, `build_llm()`, `build_tts()`, `build_turn_handling()`, `prewarm()`, `get_scheduler()`, `get_settings()`, `ScriptedLLM` |

Demo patients (from `ClinicScheduler.with_demo_data`): Jordan Lee (512) 555-0142, DOB 1988-04-12;
Priya Patel (512) 555-0177, DOB 1990-11-02; Sam Rivera (512) 555-0123, DOB 1975-07-30.
With `MAPLE_TODAY=2026-10-05` (a Monday) their appointments are Tue Oct 6 10:00,
Wed Oct 7 9:00 and Thu Oct 8 11:00.

---

## Testing

```bash
make test          # tests/unit: 200+ offline tests
make test-agent    # tests/agent: mock-LLM tests always, live tests with OPENAI_API_KEY
make eval          # DeepEval judge (needs key) + WER + latency reports
make latency FILES="metrics/*.jsonl"   # your own calls, exported by s10_observed_agent.py
make simulate ARGS=--mock              # simulated callers, zero cost
```

## Telephony (Section 8)

1. Buy a Twilio number and create an Elastic SIP trunk pointing at your LiveKit SIP URI.
2. `lk sip inbound create` for the number, then `lk sip dispatch create` with a rule that
   dispatches agent `riley-receptionist` into a new room per call.
3. Set `LIVEKIT_AGENT_NAME=riley-receptionist` and `TRANSFER_PHONE_NUMBER` in `.env`.
4. `python agents/s08_telephony_agent.py dev` and call the number.
5. Outbound reminders: `lk sip outbound create` → set `SIP_OUTBOUND_TRUNK_ID`, run the agent with
   `LIVEKIT_AGENT_NAME=riley-outbound`, then
   `python agents/s08_outbound_call.py dispatch --agent-name riley-outbound --to +1... --name "Jordan Lee"`.

## Deploy (Section 12)

```bash
make docker-build          # copies deploy/.dockerignore to the root, builds deploy/Dockerfile
docker run --rm --env-file .env -e LIVEKIT_AGENT_NAME=riley-receptionist riley-agent
```

The image runs `agents/s13_capstone_receptionist.py start` as a non-root user, with model
weights downloaded at build time. Override with `--build-arg AGENT_FILE=agents/s05_booking_agent.py`.
For LiveKit Cloud use `lk agent create` / `lk agent deploy` (lecture 12.3).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: maple` | Run from the repo root after `make install`, or `pip install -e .`. Agents add `src/` to the path themselves. |
| `OSError: PortAudio library not found` | `console` needs PortAudio even with `--text`: `brew install portaudio` (macOS) or `sudo apt install libportaudio2` (Debian/Ubuntu). |
| Console is silent / no mic | Check OS microphone permission for your terminal; `console --list-devices`, then `--input-device`. |
| Agent never joins the Playground room | You set `LIVEKIT_AGENT_NAME`: named agents are not auto-dispatched. Unset it for Sections 3-7 or dispatch explicitly. |
| `livekit.toml` name ignored in `dev` | By design in 1.8: only `start` reads it. Use `LIVEKIT_AGENT_NAME` in dev. |
| `401` / `invalid API key` | `.env` not loaded or wrong project: `lk app env`, and check `LIVEKIT_URL` matches the keys. |
| Turn detector download error | Run `download-files` once with network access (the Docker image does this at build time). |
| Riley cuts callers off | Raise `MIN_ENDPOINTING_DELAY` (0.7-0.8 on phones); compare with `BROKEN=short_endpointing`. |
| Long silences before replies | Check `python tests/evals/latency_report.py metrics/*.jsonl`; usually LLM TTFT or long prompts. |
| TTS reads "asterisk" | Markdown leaked: keep `OUTPUT_RULES` in the prompt and the default `tts_text_transforms`. |
| `metrics_collected is deprecated` warning | Expected in 1.8; `s10_observed_agent.py` explains the `session.usage` replacement. |
| Pipecat `PipelineTask`/`PipelineRunner` deprecation | 1.12 renamed them `PipelineWorker` / `WorkerRunner`; `pipecat/s14_pipecat_bot.py` uses the new names. |
| Live tests skipped | Set `OPENAI_API_KEY`. Offline tests are marked `offline` and always run. |
| Dates in demos look "wrong" | `MAPLE_TODAY=2026-10-05` pins the calendar for recordings; delete it for real dates. |

Not legal advice: before putting Riley on a public number, read the compliance checklist
from lecture 8.6 (AI disclosure, recording consent, TCPA for outbound calls).
