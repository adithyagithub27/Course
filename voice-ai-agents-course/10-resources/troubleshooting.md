# Troubleshooting Guide

**Used in:** 2.2-2.6 (setup and smoke tests), 8.2 and 8.7 (phone numbers). Pin a copy in Q&A.

> Before posting in Q&A, run through the matching section below. If you're still stuck, post: **lecture number, OS, Python version (`python --version`), the command you ran, and the full error text** (with keys removed).

**Fast isolation trick:** if something fails, run the agent in **text mode** first:

```bash
MOCK_MODE=1 python agents/s03_hello_agent.py console --text   # no keys, no audio
python agents/s03_hello_agent.py console --text               # real models, no audio
```

If text mode works, the problem is **audio** (mic/speakers, section 2). If it fails, the problem is **keys, network or install** (sections 3-5).

---

## 1. Install and Python

| Symptom | Likely cause | Fix |
|---|---|---|
| `uv: command not found` | uv not installed or not on PATH | Install uv (see its docs), restart the terminal; or use the pip fallback from lecture 2.2 |
| Errors about Python version / syntax errors in packages | Python older than 3.11 | Install Python 3.11+; `uv python install 3.11` or your OS package manager; recreate the venv |
| `ModuleNotFoundError: livekit` | Running outside the project environment | `uv run ...` or activate `.venv`; re-run `make install` |
| `make: command not found` (Windows) | No make on Windows | Use WSL, install make (e.g., via a package manager), or run the underlying commands from the Makefile directly |
| Unit tests fail right after install | Wrong directory or partial install | Run from the repo root; `make install` again; check the output of `make test` for the first failure |

## 2. Microphone and audio (console mode)

### macOS
- **System Settings → Privacy & Security → Microphone**: enable the app you run Python from (Terminal, iTerm, VS Code, PyCharm). **Restart that app** afterwards.
- If you never got a permission prompt, reset it by removing and re-adding the app, then run console mode again.
- Check the input device in **System Settings → Sound → Input** and that the level meter moves.

### Windows (native)
- **Settings → Privacy & security → Microphone**: turn on *Microphone access*, *Let apps access your microphone* and **Let desktop apps access your microphone**.
- **Settings → System → Sound → Input**: select the right device; check the level meter.
- Close other apps holding the mic (Teams, Zoom, Discord).

### Windows (WSL)
- Microphone access from WSL depends on your Windows/WSL version and audio setup (WSLg provides an audio bridge on recent versions; verify for your setup). It's often unreliable.
- **Recommended:** keep the code in WSL but talk to Riley through the **browser**: run `python agents/s03_hello_agent.py dev` and connect from the **Agents Playground** (lecture 3.4). The browser handles the mic.
- Or run console mode from **native Windows Python**, or use `console --text`.

### Linux
- Check devices: `arecord -l` (ALSA) or `pactl list short sources` (PulseAudio/PipeWire).
- Pick the right input in your sound settings or `pavucontrol`; make sure it's not muted.
- Containers and remote SSH sessions usually have no mic: use `dev` + Playground instead.

### All platforms
| Symptom | Fix |
|---|---|
| Riley keeps interrupting itself / hears its own voice | **Use headphones.** Speakers feed the agent's voice back into the mic |
| Riley never responds | Check the mic level; speak for longer; check the logs for STT transcripts; try `console --text` to isolate the problem |
| Riley cuts you off | Endpointing too short for your speech pace. See lecture 3.6/3.7 (`EndpointingOptions(min_delay=...)`) |
| Choppy or robotic audio | CPU overloaded (close apps), Bluetooth headset in "headset" mode (use wired), or an unstable network |
| No sound from Riley | Output device selection; volume; check the logs for TTS errors (key/credits) |

## 3. API keys and accounts

| Symptom | Likely cause | Fix |
|---|---|---|
| `KeyError`/"missing environment variable" at startup | `.env` not created or not in the repo root | `cp .env.example .env` and fill it in; run from the repo root |
| LiveKit connection errors (401/unauthorized, can't connect) | Wrong `LIVEKIT_URL` / `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET`, or keys from a different project | Re-run the credentials step from lecture 2.3 (the `lk` CLI can write them for you); make sure the URL is your project's `wss://` URL |
| OpenAI `401` | Invalid key | Regenerate the key; no quotes or spaces in `.env` |
| OpenAI `429` / insufficient quota | No credit or a rate limit | Add billing/credit; check your usage limits; wait and retry for rate limits |
| Deepgram / Cartesia `401`/`403` | Key missing or wrong, or credits used up | Check the dashboard; regenerate the key; check the free credit |
| Works with plugins but not Inference strings (or the reverse) | Using `"deepgram/nova-3"` (LiveKit Inference, billed via LiveKit) vs direct plugins (your provider key) | See lecture 2.1/3.5; make sure the matching credentials are set |
| Model not found | A provider renamed a model | Set the model env var (`STT_MODEL`, `LLM_MODEL`, `TTS_MODEL`, `REALTIME_MODEL`) to the current name; check the repo README for updates |
| Agent tests are all skipped | No `OPENAI_API_KEY` | Expected: agent tests auto-skip without a key. Unit tests still run |

**Never paste keys into Q&A.** If you did by accident, revoke the key immediately.

## 4. `download-files`

| Symptom | Fix |
|---|---|
| Fails or hangs | Check your network/proxy/firewall; retry; make sure you're in the project environment |
| "Model not found" for VAD/turn detector at runtime | You skipped it: run `python agents/s03_hello_agent.py download-files` once |
| Works locally, fails in Docker | Run `download-files` during the image build (lecture 12.2) |
| Disk space errors | Free space; the model files are cached. Clear old caches if needed |

## 5. Console, dev and Playground

| Symptom | Fix |
|---|---|
| `console` works but Playground shows nothing | Run `dev` (not `console`) and connect the Playground to the same LiveKit project |
| Agent never joins the room | Check the worker logs for registration errors; the agent name must match your dispatch setup (`LIVEKIT_AGENT_NAME` / `livekit.toml`) |
| Hot reload not picking up changes | Save the file in the watched directory; restart `dev` |
| Two agents answer | Two workers are running (e.g., `dev` in two terminals). Stop one |

## 6. Phone numbers, Twilio and SIP (Section 8)

### Getting a number
- **Availability and rules vary by country.** Some countries require **regulatory documents** (address, business or ID proof) before you can buy a local number, and some number types aren't available in every country (check Twilio's current per-country requirements).
- **Trial accounts** have restrictions. Typically you can only call **verified** phone numbers, and calls may include a trial message (check the current trial terms).
- **Verify your own phone number** in Twilio before testing outbound calls or transfers to it on a trial account.
- **Can't get a number in your country?** Use the **no-phone-number path** in Project 2 (8.7): test through the web client and LiveKit's SIP testing options instead. You can finish the course without a phone number.

### Calls
| Symptom | Likely cause | Fix |
|---|---|---|
| Call rings out or fails immediately | Trunk not pointing at LiveKit SIP, or the inbound trunk isn't configured | Recheck the trunk origination URI and the LiveKit inbound trunk (8.2) |
| Call connects but no agent | Dispatch rule missing, or the agent name doesn't match | Check the dispatch rule and `LIVEKIT_AGENT_NAME` / `livekit.toml` |
| Agent answers but misunderstands a lot | 8 kHz phone audio | Telephony-suited STT and longer endpointing (8.3) |
| Transfer fails | Transfer target wrong or not allowed; trial restrictions | Use a verified number; check the `tel:` format; check the provider supports the transfer method (8.4) |
| Outbound call blocked | Geo permissions, trial limits, unverified destination | Enable the destination country in the provider's geo permissions (only what you need); verify the number |
| Unexpected charges | Leaked number or keys; loops | Spend alerts; restrict outbound; rotate keys (see `telephony-compliance-checklist.md` §7) |

## 7. Tests and CI

| Symptom | Fix |
|---|---|
| Agent tests flaky | LLM non-determinism: use `mock_tools` for deterministic paths (9.5); make the judge's `intent` specific; pin the model |
| WER numbers differ from the video | Different STT model/version or reference text normalisation; check `src/maple/wer.py` normalisation |
| CI agent jobs skipped | Expected without secrets; add repo secrets to enable them (9.10) |

Still stuck? Post in Q&A with the details listed at the top.
