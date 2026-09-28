# Lab 1: Environment Verification

| Field | Details |
|---|---|
| **Section / lecture** | Section 2, lecture 2.5 |
| **Time estimate** | 45 minutes (plus account sign-up time if you skipped lecture 2.1) |
| **Difficulty** | Beginner |
| **Goal** | Prove that every piece of your toolchain works before you write any agent code: Python 3.11+, `uv`, the course repo, API keys, the LiveKit CLI and project, offline unit tests, model downloads and a spoken conversation with Riley in console mode. |
| **You will produce** | A completed verification checklist (bottom of this lab) that you keep for the rest of the course |

---

## Prerequisites

- Lectures 2.1 to 2.4 watched.
- Accounts created (lecture 2.1): **LiveKit Cloud** (free tier) and **OpenAI** (pay-as-you-go, $5 credit is plenty for the whole course). Deepgram and Cartesia accounts are optional in this lab because the default model strings run through **LiveKit Inference**, which is billed to your LiveKit Cloud project.
- A computer with a working microphone and speakers or headphones. Headphones are strongly recommended: laptop speakers feed Riley's voice back into your mic and cause false interruptions.
- macOS, Linux, or Windows 10/11 (WSL2 or native PowerShell both work).

---

## Step 1: Check Python and install uv

```bash
python3 --version
```

Expected: `Python 3.11.x` or newer (3.12 and 3.13 also work). On Windows use `py --version`.

Install `uv` (the course uses it for fast, reproducible installs):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a **new** terminal, then:

```bash
uv --version
```

Expected: `uv 0.x.y` (any recent version).

> **Checkpoint 1:** `python3 --version` shows 3.11+ and `uv --version` prints a version.

---

## Step 2: Clone the course repo and install dependencies

Use the repository URL from the resources of lecture 1.5.

```bash
git clone <REPO_URL> voice-agents-course
cd voice-agents-course
make install
```

`make install` runs `uv sync --extra dev`, which creates `.venv/` and installs the pinned dependencies (plus test and lint tools) from `pyproject.toml`. Later sections need extras too: `make install-all` adds the Pipecat and observability extras. Expected tail of the output:

```text
Resolved ... packages in ...
Installed ... packages in ...
 + livekit-agents==1.8.x
 ...
```

No `make` (for example, plain Windows)? Run `uv sync --extra dev` directly. No `uv` at all? Use the pip fallback (`make install PIP=1` does the same inside an active virtual environment):

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Confirm the key packages are installed at the versions the course was recorded with:

```bash
uv run python -c "import importlib.metadata as m; [print(p, m.version(p)) for p in ('livekit-agents', 'pipecat-ai', 'jiwer', 'deepeval')]"
```

Expected (patch versions may differ):

```text
livekit-agents 1.8.3
pipecat-ai 1.12.0
jiwer 3.x.x
deepeval 3.x.x
```

> **Checkpoint 2:** `livekit-agents` reports `1.8.x`. If it reports `0.x` or `1.0`-`1.7`, stop and see the troubleshooting table: much of the course code will not run on older versions.

---

## Step 3: Install the LiveKit CLI and log in

```bash
# macOS
brew install livekit-cli

# Linux
curl -sSL https://get.livekit.io/cli | bash

# Windows
winget install LiveKit.LiveKitCLI
```

Then:

```bash
lk --version
lk cloud auth
```

`lk cloud auth` opens a browser. Approve the CLI for the LiveKit Cloud project you created in lecture 2.3 (name suggestion: `maple-street-dental`).

```bash
lk project list
```

Expected: a table containing your project, marked as the default.

> **Checkpoint 3:** `lk project list` shows your project.

---

## Step 4: Create your `.env`

From the repo root, let the CLI fill in your LiveKit credentials using `.env.example` as the template:

```bash
lk app env -w -d .env
```

Open `.env` in your editor. The three LiveKit values should now be filled in:

```dotenv
LIVEKIT_URL=wss://maple-street-dental-xxxxxxxx.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Now add the keys you have. At minimum:

```dotenv
OPENAI_API_KEY=sk-...
```

Leave the model variables at their defaults for now:

```dotenv
MAPLE_PROVIDER_MODE=inference
STT_MODEL=deepgram/nova-3
LLM_MODEL=openai/gpt-4.1-mini
TTS_MODEL=cartesia/sonic-3
REALTIME_MODEL=gpt-realtime
REALTIME_VOICE=marin
```

If your CLI version rejects `-w -d`, run plain `lk app env`, copy the three `LIVEKIT_*` lines it prints, and paste them into a copy of `.env.example` saved as `.env`.

Check which variables are set without printing any secret values:

```bash
grep -E '^(LIVEKIT_URL|LIVEKIT_API_KEY|LIVEKIT_API_SECRET|OPENAI_API_KEY|STT_MODEL|LLM_MODEL|TTS_MODEL)=.+' .env | sed 's/=.*/=<set>/'
```

Expected: seven lines, each ending in `=<set>`. A missing `LIVEKIT_*` or `OPENAI_API_KEY` line means that variable is empty or misspelled. (Missing model lines are fine: `src/maple/config.py` falls back to the course defaults.)

Now ask the course's config loader what it resolved:

```bash
uv run --env-file .env python -c "from maple.config import load_settings; s = load_settings(); print(s.provider_mode, s.stt_model, s.llm_model, s.tts_model_with_voice, s.agent_name, sep='\n')"
```

Expected:

```text
inference
deepgram/nova-3
openai/gpt-4.1-mini
cartesia/sonic-3:f786b574-daa5-4673-aa0c-cbe3e8534c02
riley-receptionist
```

The TTS line includes the default Cartesia voice ID from `TTS_VOICE`. A `ConfigError` here tells you exactly which variable has a bad value.

Finally, prove the credentials work against LiveKit Cloud:

```bash
lk room list
```

Expected: an empty table (or a list of rooms) and **no** authentication error.

> **Checkpoint 4:** `.env` exists, is listed in `.gitignore` (`git check-ignore .env` prints `.env`), and `lk room list` succeeds.

---

## Step 5: Run the offline unit tests

```bash
make test
```

These tests cover the pure-Python business logic in `src/maple/` (scheduler, knowledge, PII, costs, latency, WER, config). They need no network and no keys. Expected tail:

```text
tests/unit/test_scheduler.py ........                                  [ 20%]
...
============================== NN passed in 0.9s ==============================
```

The exact count grows as the repo evolves; what matters is **0 failed, 0 errors**.

> **Checkpoint 5:** `make test` ends in `passed` with no failures.

---

## Step 6: Download local model files

Silero VAD and the turn-detector model run locally and must be downloaded once:

```bash
uv run agents/s03_hello_agent.py download-files
```

Expected: download progress lines, then the command exits with status 0. Run it again; it should finish almost instantly because the files are cached.

> **Checkpoint 6:** the second `download-files` run completes in a few seconds.

---

## Step 7: Talk to Riley in console mode

Put your headphones on.

```bash
uv run agents/s03_hello_agent.py console
```

Console mode runs the agent locally against your microphone and speakers, while still using LiveKit Inference for STT, LLM and TTS. Within a couple of seconds you should hear Riley greet you, and see a live transcript similar to:

```text
[agent] Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?
[user]  Hi, what time do you open tomorrow?
[agent] ...
```

Say three things and note how long Riley takes to answer each one (count "one-Mississippi" if you like; Section 10 measures it properly):

1. "Hi, who am I speaking with?"
2. "Are you a real person?"
3. Start a sentence, pause for one second in the middle, then finish it. Did Riley jump in during the pause?

Press `Ctrl+C` to quit.

No working microphone, or want to practise at zero cost? Two alternatives (lecture 2.7):

```bash
uv run agents/s03_hello_agent.py console --text              # type instead of talking (still uses the models)
MOCK_MODE=1 uv run agents/s03_hello_agent.py console --text  # scripted fake LLM, no API keys, no cost
```

Mock mode proves your install works; it does not prove your keys work, so still complete the spoken run when you can.

> **Checkpoint 7:** you heard Riley's greeting and had a three-turn conversation.

---

## Step 8: Record your environment

Save this to `notes/lab-01.md` in your repo. Add `notes/` to `.gitignore` if it is not already there, so personal notes never get pushed:

```bash
mkdir -p notes
{
  echo "# Lab 1 environment"
  echo "- OS: $(uname -sr 2>/dev/null || echo Windows)"
  echo "- $(python3 --version)"
  echo "- $(uv --version)"
  echo "- $(lk --version 2>&1 | head -1)"
  uv run python -c "import importlib.metadata as m; print('- livekit-agents', m.version('livekit-agents'))"
} > notes/lab-01.md
cat notes/lab-01.md
```

---

## Verification checklist

| # | Check | Command | Pass |
|---|---|---|---|
| 1 | Python 3.11+ | `python3 --version` | [ ] |
| 2 | uv installed | `uv --version` | [ ] |
| 3 | Dependencies installed, livekit-agents 1.8.x | `make install` + version one-liner | [ ] |
| 4 | LiveKit CLI authenticated | `lk project list` | [ ] |
| 5 | `.env` filled and git-ignored | `git check-ignore .env` | [ ] |
| 6 | LiveKit credentials valid | `lk room list` | [ ] |
| 7 | Offline unit tests green | `make test` | [ ] |
| 8 | Local models downloaded | `... download-files` | [ ] |
| 9 | Spoke with Riley in console mode | `... console` | [ ] |

---

## Stretch goal

First, hear where you are heading (lecture 2.6): run the finished capstone and book an appointment with it.

```bash
make console AGENT=agents/s13_capstone_receptionist.py
```

Then run the hello agent in **dev mode** and talk to it from your browser:

```bash
uv run agents/s03_hello_agent.py dev
```

Open the LiveKit Agents Playground (https://agents-playground.livekit.io), choose your LiveKit Cloud project, and connect. Compare the experience with console mode: which one had the more natural turn-taking, and why might the browser path be slower (hint: there is now a WebRTC hop between you and the agent)? Add your answer to `notes/lab-01.md`.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `uv: command not found` right after installing | Shell has not reloaded `PATH` | Open a new terminal, or `source ~/.local/bin/env` (macOS/Linux) |
| `ImportError: cannot import name 'AgentServer'` | An old `livekit-agents` is installed (pre-1.8) | `uv sync --reinstall` inside the repo; make sure you are not running a global Python (`which python` should point into `.venv`) |
| `ModuleNotFoundError: No module named 'maple'` | Running outside the project environment | Prefix commands with `uv run`, or activate `.venv` |
| `lk: command not found` | CLI not on `PATH` | Re-run the installer; on Linux check `~/.local/bin` or `/usr/local/bin` |
| `lk room list` returns 401 / invalid token | Wrong or stale `LIVEKIT_API_KEY`/`SECRET`, or `.env` has quotes/spaces | Re-run `lk app env -w -d .env`; values must not have spaces around `=` |
| Console starts but Riley never speaks | No output device selected, or TTS auth failure | Check the log for `401`/`403` from TTS; confirm your LiveKit project has Inference enabled; check OS sound output |
| Riley keeps interrupting herself | Speaker audio leaking into the microphone | Use headphones (echo cancellation in console mode is limited) |
| macOS: no transcript appears | Terminal has no microphone permission | System Settings → Privacy & Security → Microphone → enable your terminal app, then restart it |
| `download-files` hangs or fails | Corporate proxy / firewall blocks model hosts | Try another network; set `HTTPS_PROXY` if your company requires one |
| `make: command not found` on Windows | `make` is not installed | Use the raw commands (`uv sync`, `uv run pytest tests/unit`) or install make via `winget install GnuWin32.Make` |

---

## Solution notes

- There is no code to write in this lab; the "solution" is a fully ticked checklist.
- The most common failure in beta testing was running `python agents/s03_hello_agent.py` with a global interpreter instead of `uv run`, which silently used an old `livekit-agents`. Always use `uv run` (or an activated `.venv`).
- LiveKit Inference model strings (`deepgram/nova-3`, `openai/gpt-4.1-mini`, `cartesia/sonic-3`) are billed to your LiveKit Cloud project, so you do not need Deepgram or Cartesia keys until you switch to the direct provider plugins in lecture 3.5. You **do** need `OPENAI_API_KEY` for the realtime agent (Section 6) and for the LLM judges in Section 9.
- Reference files: `03-code/README.md` (setup), `03-code/.env.example`, `03-code/Makefile`, `03-code/tests/unit/`.
