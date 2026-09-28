# Section 2: Setup: Accounts, Keys and Your Dev Environment

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈44 min (7 lectures)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."
> **Cue legend:** see `section-01-welcome.md`. Word counts are spoken words only; where talking time is shorter than the target duration, the rest is demo audio, typing, command output and on-screen dwell. Screencasts are paced a little slower than 140 words per minute to leave room for typing and command output.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 2.1 | Accounts you need and what they cost | SC | 8:00 | ~725 |
| 2.2 | Python project setup with uv | SC | 8:00 | ~625 |
| 2.3 | LiveKit CLI, projects and credentials | SC | 7:00 | ~475 |
| 2.4 | Smoke test: unit tests and console mode | SC | 6:00 | ~450 |
| 2.5 | Lab 1: Environment verification | LAB | 3:00 (1:30 video) | ~225 |
| 2.6 | Quick win: run the finished Riley before you build it | SC | 6:00 | ~600 |
| 2.7 | Spending caps, free tiers and offline mock mode | SC | 6:00 | ~550 |

**Recording note for the whole section:** use a throwaway LiveKit project and throwaway API keys for recording. Blur every key in post, and rotate all keys after the recording session anyway.

---

## Lecture 2.1 — Accounts you need and what they cost

| Field | Value |
|---|---|
| ID | 2.1 |
| Type | SC (screencast) |
| Target duration | 8:00 (~725 spoken words, about 5:11 of talking at 140 wpm) |
| Learning objectives | 1. Create the accounts the course needs and know which are optional. 2. Explain the difference between LiveKit Inference model strings and direct provider plugins. 3. Keep total course spend around ten to twenty dollars using free tiers and spending limits. |
| Prerequisites | Section 1 |
| Files used | `10-resources/provider-cost-guide.md`, `03-code/.env.example` |

### Script

[AVATAR]
Let's talk about money first, because nobody likes a surprise bill. If you follow this course and use the free tiers, you should spend somewhere around ten to twenty dollars in total. Not per month. In total. Let me show you exactly where that goes, and how to put a hard ceiling on it.

[SLIDE 1: What you need, and when]
- Required now: LiveKit Cloud, OpenAI
- Optional: Deepgram, Cartesia, ElevenLabs (direct provider keys)
- Section 8 only: Twilio (phone number)

There are two accounts you need today. LiveKit Cloud and OpenAI. Everything else is either optional or waits until Section eight.

Why so few? Because of something called LiveKit Inference. Let me explain it, because it changes which accounts you need.

[SLIDE 2: Two ways to call models]
Left column, "LiveKit Inference (model strings)":
```python
AgentSession(
    stt="deepgram/nova-3",
    llm="openai/gpt-4.1-mini",
    tts="cartesia/sonic-3",
)
```
- One account, one bill (LiveKit Cloud)
- Uses your LIVEKIT_API_KEY and LIVEKIT_API_SECRET

Right column, "Direct provider plugins":
```python
from livekit.plugins import cartesia, deepgram, openai

AgentSession(
    stt=deepgram.STT(model="nova-3"),
    llm=openai.LLM(model="gpt-4.1-mini"),
    tts=cartesia.TTS(model="sonic-3"),
)
```
- Your own account and key per provider
- Access to every provider-specific option

There are two ways to call a model from LiveKit Agents. On the left, model strings. You write "deepgram slash nova-three" and LiveKit Cloud calls Deepgram for you, and bills you through your LiveKit account. One account. One bill. No Deepgram key.

On the right, direct plugins. You import the Deepgram plugin, give it your own Deepgram key, and call Deepgram directly. You pay Deepgram directly, and you get every provider-specific setting.

This course defaults to model strings, because it means fewer accounts on day one. In Lecture 3.5 you'll see when it's worth switching to plugins. The good news is it's a one-line change.

[SCREEN: Browser. Go to cloud.livekit.io. Click "Sign up", sign in with GitHub. Show the new project dashboard. Hover over the "Settings" and "API keys" menu items but don't open them yet.]

Account one, LiveKit Cloud. Go to cloud dot livekit dot io and sign up. I'm using my GitHub login. It creates your first project automatically. A project is a container for your rooms, your agents and your keys.

The free tier includes a monthly allowance of agent session minutes and some inference credits. That's enough for most of this course. Don't create keys yet. We'll let the LiveKit command-line tool do that in Lecture 2.3.

[SCREEN: Browser. Go to platform.openai.com. Show Billing → add a small prepaid credit. Then Limits → set a monthly budget. Then API keys → "Create new secret key", name it `voice-course`. Blur the key.]

Account two, OpenAI. We use it for three things. Riley's LLM, if you switch to the plugin. The speech-to-speech model in Section six. And the judge model that grades Riley's answers in Section nine.

Go to platform dot openai dot com. Add a small prepaid credit. Five dollars is plenty to start. Then do the step most people skip. Go to Limits, and set a monthly budget. I set mine to twenty dollars. Now a runaway test loop can't surprise you.

Create a secret key, name it "voice-course", and copy it somewhere safe for a minute. You'll paste it into a file in the next lecture.

[SCREEN: Quick tour, ten seconds each: deepgram.com signup page, cartesia.ai signup page, elevenlabs.io pricing page. Don't sign up on camera.]

The optional accounts. Deepgram for speech-to-text. Cartesia for text-to-speech. ElevenLabs, if you want to try another voice provider. You only need these if you want to use direct plugins. Each has a free tier or signup credit, so there's no harm in grabbing them later when you get curious.

[SCREEN: twilio.com trial signup page, pointing at "trial credit".]

And Twilio, which gives Riley a real phone number in Section eight. The trial comes with some credit, which is enough for the course. We'll set it up when we get there, so don't worry about it now.

[SLIDE 3: Student cost guide (check current pricing)]
| Service | Used for | Free tier or trial | Paid ballpark | Needed? |
|---|---|---|---|---|
| LiveKit Cloud | Rooms, agent hosting, LiveKit Inference, SIP | Free plan with monthly agent minutes and inference credits | Usage-based above free tier | Yes, from S2 |
| OpenAI | LLM plugin, Realtime (S6), judge model (S9) | No standing free tier; prepaid credit from about $5 | gpt-4.1-mini: cents per call; realtime audio costs noticeably more | Yes, from S2 |
| Deepgram | STT via direct plugin | Signup credit | About one cent or less per streaming minute | Optional |
| Cartesia | TTS via direct plugin | Free monthly credits | Low-cost starter plan | Optional |
| ElevenLabs | Alternative TTS | Free monthly credits | Low-cost starter plan | Optional |
| Twilio | Phone number and calls (S8) | Trial credit, calls to verified numbers only | Around a dollar per month per number plus per-minute call fees | S8 only |
| **Expected course total** | | | **≈ $10–20** | |
Footer: "Prices and free tiers change often. Check current pricing on each provider's site. Full details: 10-resources/provider-cost-guide.md"

Here's the full picture on one slide. Screenshot it, or open the provider cost guide in the resources folder, which has links to every pricing page.

Every price here says "check current pricing," and I mean it. Voice AI pricing changes every few months. Usually downward, but not always.

So where does the money actually go? A cascaded call costs a few cents per minute. Text-to-speech is usually the biggest slice, then the platform minutes, then speech-to-text. The LLM is often the smallest part, because Riley's replies are short. Speech-to-speech models cost more per minute. You'll measure all of this properly in Section ten.

[SLIDE 4: Five ways to keep your bill tiny (Lecture 2.7 goes deeper)]
1. Set a monthly spending limit on OpenAI today
2. Iterate on prompts in text mode: `console --text` (no STT or TTS cost)
3. Run `make test` often: unit tests are offline and free
4. Stop `dev` mode when you're not using it
5. Delete unused Twilio numbers after Section 8

[AVATAR]
Five habits keep your bill tiny. Set that OpenAI limit today. When you're tweaking a prompt, use text mode, which skips speech-to-text and text-to-speech entirely. Run the unit tests as often as you like, because they're offline and free. Stop your dev server when you walk away. And when you finish Section eight, release your Twilio number if you don't need it. In Lecture 2.7, we'll go deeper, including a mock mode that costs nothing at all.

One last thing. Treat your keys like passwords. They never go in a screenshot, a Git commit or a Q&A post. If one leaks, delete it and make a new one. It takes thirty seconds.

**Recap:** You need LiveKit Cloud and OpenAI today, LiveKit Inference model strings mean fewer accounts, and a spending limit plus text-mode testing keeps the whole course around ten to twenty dollars.

**Transition:** With accounts ready, let's clone the repo and set up the Python project with uv.

### Speaker notes: common student mistakes / Q&A

- Mistake: creating an OpenAI key without adding billing credit. Requests then fail with a quota error that looks like a code bug.
- Mistake: using a ChatGPT Plus subscription and expecting API access. They're billed separately.
- "Do I need Deepgram and Cartesia accounts?" Not for the default setup. LiveKit Inference model strings route through your LiveKit Cloud account.
- "Can I use a local LLM to save money?" You can, via an OpenAI-compatible endpoint, but the TTFT is usually too slow for a sub-second budget on a laptop. Try it after Section 3 as an experiment.

---

## Lecture 2.2 — Python project setup with uv

| Field | Value |
|---|---|
| ID | 2.2 |
| Type | SC (screencast) |
| Target duration | 8:00 (~625 spoken words, about 4:28 of talking at 140 wpm) |
| Learning objectives | 1. Clone the course repo and install dependencies with `uv sync --extra dev` (or the pip fallback). 2. Create a `.env` file from `.env.example` and understand every variable. 3. Download local model files with the `download-files` command. |
| Prerequisites | 2.1 |
| Files used | `03-code/pyproject.toml`, `03-code/.env.example`, `03-code/Makefile` |

### Script

[AVATAR]
Python environment problems cause more "it doesn't work" questions than everything else combined. So we're going to use uv. It's a fast Python package manager, and it installs the right Python version for you. Setup takes about two minutes.

[SCREEN: Terminal, font size 18. Show install commands for each OS on a lower third.]

First, install uv if you don't have it.

[CODE: install uv (show the line for your OS)]
```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# check it worked
uv --version
```

On macOS or Linux it's one curl command. On Windows it's one PowerShell command. Then check the version. Anything recent is fine.

[SCREEN: Terminal. Clone the repo.]

Next, clone the course repo. The link is in the resources for this lecture.

[CODE: clone and enter the repo]
```bash
git clone <course-repo-url> voice-agents-course
cd voice-agents-course
```

[SCREEN: VS Code, open `pyproject.toml`. Highlight `requires-python` and the `livekit-agents` dependency line with its extras.]

Let's peek at `pyproject.toml` before we install. Two lines matter. `requires-python` says Python three eleven or newer. And the `livekit-agents` line pins the one-point-eight series, with extras for the plugins we use: OpenAI, Deepgram, Cartesia and Silero.

Why pin? Because voice frameworks move fast. A pinned version means the code in this course runs the same on your machine as on mine.

[SCREEN: Terminal.]

Now install everything.

[CODE: install dependencies, including the test tools]
```bash
uv sync --extra dev
```

[DEMO: uv resolves, downloads Python if needed, creates `.venv/`, installs packages. Takes 10 to 40 seconds.]

That's it. uv read the project file, downloaded a matching Python if you didn't have one, created a virtual environment in a folder called dot venv, and installed every package. The extra called dev adds the testing tools, like pytest, that we'll use from Lecture 2.4 on. You don't need to activate anything. When you put `uv run` in front of a command, it uses this environment automatically.

[SLIDE 1: No uv? The pip fallback]
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```
- Then drop `uv run` from every command in the course

If you can't use uv, say on a locked-down work laptop, here's the fallback. Make a virtual environment, activate it, and pip install the project in editable mode with the dev extras. Then, everywhere I type `uv run`, you just leave it off.

[SCREEN: Terminal, then VS Code with `.env` open.]

Now the secrets. The repo includes a template called dot env dot example. Copy it to dot env.

[CODE: create your .env]
```bash
cp .env.example .env
```

[SCREEN: VS Code, `.env` open. Walk down the file. Blur values.]

[CODE: the contents of .env (values blank until you fill them)]
```bash
# LiveKit (filled in Lecture 2.3)
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

# Providers
OPENAI_API_KEY=
DEEPGRAM_API_KEY=        # optional: only for direct plugins
CARTESIA_API_KEY=        # optional: only for direct plugins

# Models (defaults shown; read by src/maple/config.py)
MAPLE_PROVIDER_MODE=inference     # or "plugins" to use your own provider keys
STT_MODEL=deepgram/nova-3
LLM_MODEL=openai/gpt-4.1-mini
TTS_MODEL=cartesia/sonic-3
TTS_VOICE=f786b574-daa5-4673-aa0c-cbe3e8534c02
REALTIME_MODEL=gpt-realtime
REALTIME_VOICE=marin
```
(Excerpt. The real `.env.example` has a few more settings, such as telephony and endpointing values, each with a comment. We'll meet them in the sections that use them.)

Let's read it top to bottom. Three LiveKit values: the URL of your project, an API key and an API secret. Leave those empty. The LiveKit CLI will give them to us in the next lecture.

Then provider keys. Paste your OpenAI key now. Deepgram and Cartesia are optional, so leave them blank unless you created those accounts.

Then the model settings. These are read by `src/maple/config.py`. Provider mode says whether we use LiveKit Inference model strings or your own provider keys. The rest default to the models and voice we use in the course. When a provider launches a new model, or renames an old one, you change it here. You don't touch the code.

[SCREEN: Terminal, run `git status`. `.env` is not listed. Then `cat .gitignore | grep env`.]

Quick safety check. Run git status. Notice dot env doesn't show up. That's because it's in the gitignore file. Your keys will never be committed by accident. Please keep it that way.

[SCREEN: Terminal.]

Now let's use the Makefile shortcut. `make install` runs that same uv sync command for you, and it's what I'll use from now on.

[CODE: the Makefile shortcut]
```bash
make install
```

[SCREEN: Terminal.]

One more step. Some models run locally on your machine, not in the cloud. The Silero voice activity detector, and a local fallback for the turn detector. Those need to be downloaded once. The agent file has a built-in command for that.

[CODE: download local model files]
```bash
uv run python agents/s03_hello_agent.py download-files
```

[DEMO: Progress output as model files download. Finishes in a few seconds.]

This is the same file you'll build from scratch in Section three. Every agent in this course has these built-in commands: console, dev, start, connect and download-files. We'll use most of them soon.

[AVATAR]
If you do this on a new machine, or in a Docker image later, you run download-files once. In Section twelve, we'll bake it into the Docker build so production containers start fast.

**Recap:** `uv sync --extra dev` installs a pinned environment, dot env holds your keys and model names, and download-files fetches the local models once.

**Transition:** Your `.env` still has three empty LiveKit lines, so next we'll install the LiveKit CLI and fill them in.

### Speaker notes: common student mistakes / Q&A

- Mistake: naming the file `env` or `.env.txt`. On Windows, File Explorer hides extensions. Create it from the terminal with `cp` or `copy`.
- Mistake: quotes and spaces around values, like `OPENAI_API_KEY = "sk-..."`. Use `KEY=value` with no spaces.
- Mistake: running `python agents/...` without `uv run` and getting `ModuleNotFoundError: livekit`. Either use `uv run` or activate `.venv`.
- "Which Python version?" 3.11 or newer. uv installs one automatically if yours is older.

---

## Lecture 2.3 — LiveKit CLI, projects and credentials

| Field | Value |
|---|---|
| ID | 2.3 |
| Type | SC (screencast) |
| Target duration | 7:00 (~475 spoken words, about 3:24 of talking at 140 wpm) |
| Learning objectives | 1. Install the `lk` CLI and link it to your LiveKit Cloud project with `lk cloud auth`. 2. Write project credentials into `.env` using `lk app env`. 3. Verify credentials with `lk room list`. |
| Prerequisites | 2.1, 2.2 |
| Files used | `03-code/.env` |

### Script

[AVATAR]
Your agent needs three things to reach LiveKit Cloud: a URL, a key and a secret. You could copy them by hand from the dashboard. But the LiveKit CLI does it for you, and you'll need the CLI anyway for telephony and deployment later. So let's install it once and use it everywhere.

[SCREEN: Terminal. Show the three install lines as a lower third.]

[CODE: install the LiveKit CLI (pick your OS)]
```bash
# macOS
brew install livekit-cli

# Linux
curl -sSL https://get.livekit.io/cli | bash

# Windows
winget install LiveKit.LiveKitCLI

# check it worked
lk --version
```

On macOS, it's Homebrew. On Linux, a one-line install script. On Windows, winget. Then check the version.

The command is just two letters: l k.

[SCREEN: Terminal. Run the auth command. Browser opens to cloud.livekit.io asking to authorize the CLI. Click "Approve". Return to terminal.]

Next, link the CLI to your LiveKit Cloud account.

[CODE: authenticate the CLI]
```bash
lk cloud auth
```

[DEMO: Browser opens, you approve the device, terminal confirms the linked project.]

A browser window opens. Approve the request. Back in the terminal, the CLI confirms which project it linked. Behind the scenes, it created an API key and secret for this project and saved them in the CLI's own config file.

[SCREEN: Terminal.]

[CODE: see your linked projects]
```bash
lk project list
```

If you have more than one project, this lists them and marks the default. For this course, one project is all you need. I call mine "maple-dev".

[SCREEN: Terminal. Make sure you're in the repo folder.]

Now let's get those credentials into our dot env file. Make sure you're inside the repo folder.

[CODE: print your project's environment values]
```bash
lk app env
```

[DEMO: The CLI prints LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET for the linked project. Blur the key and secret.]

This command prints the three LiveKit values for your project. The URL starts with w s s colon slash slash, and ends in livekit dot cloud. Copy those three lines and paste them into the top of your dot env file, replacing the empty ones.

[SCREEN: VS Code, `.env`, paste the three lines. Blur.]

There's also a flag that writes these values straight to a file. I'm pasting by hand on purpose, because I don't want the CLI to overwrite the OpenAI key we already saved. Check `lk app env --help` if you want the automatic version.

[SCREEN: Terminal.]

Now, let's prove the credentials work.

[CODE: list rooms in your project]
```bash
lk room list
```

[DEMO: Output is an empty table, or "no rooms".]

An empty list. That's a success. It means the CLI reached your project with valid credentials, and there are simply no rooms yet. If the credentials were wrong, you'd see an authentication error instead.

[SLIDE 1: What each value is for]
- `LIVEKIT_URL`: where your agent server connects (your project's WebSocket URL)
- `LIVEKIT_API_KEY`: identifies your project
- `LIVEKIT_API_SECRET`: signs tokens. Treat it like a password.
- LiveKit Inference also uses the key and secret, so model strings work without provider keys

Here's what each value does. The URL tells your agent server where to connect. The key identifies your project. The secret signs access tokens, so treat it like a password.

And remember LiveKit Inference from Lecture 2.1? Model strings like "deepgram slash nova-three" are billed to this same key and secret. So these three lines unlock speech-to-text, the LLM and text-to-speech, without any other provider keys.

[SLIDE 2: The `lk` commands you'll use in this course]
- `lk cloud auth`: link a project (S2)
- `lk room list`: check rooms and credentials (S2, S3)
- `lk agent console` / `lk agent dev`: newer way to run agents locally (optional)
- `lk sip ...`: trunks and dispatch rules (S8)
- `lk agent create` and deploy commands: LiveKit Cloud agents (S12)

[AVATAR]
Here's a preview of where the CLI shows up again. Section eight uses it to create phone trunks and dispatch rules. Section twelve uses it to deploy Riley to LiveKit Cloud. And newer versions of the CLI can also run your agent locally, with `lk agent console`. In this course I'll mostly run agents with `uv run python`, because it works the same everywhere. Both approaches work.

**Recap:** `lk cloud auth` links your project, `lk app env` gives you the three LiveKit values for your `.env`, and an empty `lk room list` proves they work.

**Transition:** Everything's installed and connected, so let's run the smoke test and hear an agent talk through your laptop.

### Speaker notes: common student mistakes / Q&A

- Mistake: running `lk app env` outside the repo folder, then pasting into the wrong `.env`.
- Mistake: `LIVEKIT_URL` set to `https://...`. It must be the `wss://...livekit.cloud` URL.
- Mistake: copying keys from one project and the URL from another. Symptom: `401 unauthorized` when the agent connects. Re-run `lk app env` and paste all three together.
- "Can I self-host LiveKit instead?" Yes, LiveKit is open source, and Section 12 covers self-hosting the agent. For the course, LiveKit Cloud's free tier is simpler, and LiveKit Inference model strings require it.

---

## Lecture 2.4 — Smoke test: unit tests and console mode

| Field | Value |
|---|---|
| ID | 2.4 |
| Type | SC (screencast) |
| Target duration | 6:00 (~450 spoken words, about 3:13 of talking at 140 wpm) |
| Learning objectives | 1. Run the offline unit tests with `make test` and read the result. 2. Talk to an agent through your laptop microphone in console mode. 3. Diagnose the three most common setup failures: mic permissions, missing keys and missing model files. |
| Prerequisites | 2.2, 2.3 |
| Files used | `03-code/tests/unit/`, `03-code/agents/s03_hello_agent.py` |

### Script

[AVATAR]
Two commands tell you whether your setup works. The first checks the Python side, with no network and no keys. The second checks everything, by letting you talk to an agent out loud. If both pass, you're ready for Section three.

[SCREEN: Terminal in the repo folder.]

Command one. The unit tests.

[CODE: run the offline unit tests]
```bash
make test
```

[DEMO: pytest runs `tests/unit/`. All tests pass in a couple of seconds. Zoom on the final "passed" line.]

All green, in about two seconds. These tests cover the clinic scheduler, the FAQ search, PII redaction, cost math, latency statistics, word error rate, config and the speech helpers. None of them call an API. None of them cost a cent.

Under the hood, make test runs `uv run pytest tests/unit`. You'll run this dozens of times in the course. Any time you change business logic, run it.

If you see a failure here, it's almost always a Python environment problem, not your keys. Re-run make install and try again.

[SCREEN: Terminal.]

Command two. Console mode. This runs an agent right in your terminal, using your laptop's microphone and speakers. No browser, no phone.

[CODE: talk to the agent in console mode]
```bash
uv run python agents/s03_hello_agent.py console
```

[DEMO: Console starts. An audio meter shows your mic level. Riley greets you: "Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?" Say: "Hi Riley, what are your opening hours?" Riley answers briefly. Say "Thanks, bye." Press Ctrl+C to exit.]

Listen. [PAUSE] Riley greets you. Now I'll ask a question. [PAUSE] And it answers. That round trip went from my microphone, to LiveKit Inference for speech-to-text, the LLM and text-to-speech, and back out of my speakers.

It doesn't know the real clinic hours yet. It's just making a friendly guess. We fix that with tools and a knowledge base later. Right now, we only care that the pipeline works. Press Control C to stop.

[SLIDE 1: Troubleshooting console mode]
| Symptom | Likely cause | Fix |
|---|---|---|
| Mic meter flat, agent never responds | Terminal has no mic permission | macOS: System Settings → Privacy & Security → Microphone → enable your terminal or VS Code. Restart the terminal. |
| Wrong mic or speakers | Default device is a headset or virtual device | `console --list-devices`, then `console --input-device "<name>"` |
| `401` or "unauthorized" | LiveKit key, secret or URL missing or mismatched | Re-run `lk app env`, paste all three lines |
| Error about missing model files | Skipped download step | `uv run python agents/s03_hello_agent.py download-files` |
| Agent keeps interrupting itself | Speakers feeding back into the mic | Use headphones |

Here are the five problems I see most. Let's walk them.

Mic meter flat? Your terminal doesn't have microphone permission. On a Mac, open Privacy and Security, then Microphone, and enable your terminal app or VS Code. Then fully restart the terminal.

Wrong device? Run console with the list devices flag, then pass the one you want.

An unauthorized error? Your LiveKit values are missing or mismatched. Re-run lk app env and paste all three lines together.

An error about model files? You skipped download files.

And if Riley keeps interrupting itself, your speakers are feeding back into your microphone. Wear headphones. Seriously. It's the single best upgrade for this course.

[SCREEN: Terminal.]

[CODE: text mode, no microphone needed]
```bash
uv run python agents/s03_hello_agent.py console --text
```

[DEMO: Type "What are your opening hours?" and see Riley's text reply.]

One more trick. Add dash dash text, and console mode becomes a chat in your terminal. No microphone, no speech-to-text, no text-to-speech. It's perfect for quick prompt experiments, and it's cheaper. If your mic won't cooperate, this at least proves your keys and LLM work.

[AVATAR]
So here's your checklist. Make test is green. Console mode greets you and answers out loud. If both are true, your environment is done. You won't need to touch setup again until telephony.

**Recap:** `make test` proves the offline Python side, and console mode proves the full voice pipeline from your mic to LiveKit Inference and back.

**Transition:** Next is a short lab where you'll run through the environment checklist yourself and record your results.

### Speaker notes: common student mistakes / Q&A

- Mistake: running console mode from inside a VS Code terminal that was opened before granting mic permission. Quit and reopen VS Code completely.
- Mistake: Bluetooth headsets switching to low-quality "hands-free" mode when the mic opens, which hurts STT. Use a wired headset or the laptop mic with headphones.
- "The console says it's deprecated in favour of `lk agent console`." Both work in 1.8. The course uses `uv run python ... console` because it only needs Python. Use whichever you prefer.
- WSL2 users: audio devices in WSL can be unreliable. Use `--text` in WSL, or run console mode from native Windows PowerShell.

---

## Lecture 2.5 — Lab 1: Environment verification

| Field | Value |
|---|---|
| ID | 2.5 |
| Type | LAB (text lab with short video walkthrough) |
| Target duration | 3:00 total (1:30 video, ~225 spoken words, about 1:36 of talking at 140 wpm) |
| Learning objectives | 1. Verify every part of the environment with a repeatable checklist. 2. Record baseline versions and first impressions of latency. |
| Prerequisites | 2.1 to 2.4 |
| Files used | `04-labs/lab-01-environment.md` |

### Script

[AVATAR]
Time to verify your setup yourself. This lab takes about ten minutes, and it saves hours later.

[SCREEN: Open `04-labs/lab-01-environment.md` in VS Code preview. Scroll slowly through the checklist.]

The lab is a checklist. You'll confirm your tool versions: uv, Python, the lk CLI and livekit-agents. You'll confirm dot env has all three LiveKit values and your OpenAI key, and that git status doesn't show it. You'll run make test and write down how many tests passed. You'll run lk room list. And you'll hold a short conversation with Riley in console mode, then again in text mode.

[SCREEN: Highlight the "Observations" table at the bottom of the lab.]

At the end, there's a small observations table. How long did Riley take to answer, just by feel? Did it ever interrupt you? Did it mishear anything? Write it down, even if it's rough. In Section three, you'll change turn-taking settings and compare against these first impressions.

[AVATAR]
If anything on the checklist fails, the lab links to the right troubleshooting step. And if you're still stuck, post in Q&A with the lecture number, the command and the full error. [PAUSE] See you in Section three, where you'll build this agent yourself from an empty file.

**Recap:** Lab 1 confirms tools, keys, tests and console mode, and captures a first-impressions baseline for later tuning.

**Transition:** Next, a quick win: you'll run the finished Riley on your laptop before building it.

### Speaker notes: common student mistakes / Q&A

- Students skip the observations table. Encourage it: comparing "before" and "after" turn tuning in Lab 2 is the most memorable moment of Section 3.
- If `make test` passes but console mode fails, the problem is keys, audio devices or network, never the business logic.
- Corporate networks sometimes block WebRTC or WebSocket traffic. Try a personal network or hotspot before debugging code.

---

## Lecture 2.6 — Quick win: run the finished Riley before you build it

| Field | Value |
|---|---|
| ID | 2.6 |
| Type | SC (screencast) |
| Target duration | 6:00 (~600 spoken words, about 4:17 of talking at 140 wpm) |
| Learning objectives | 1. Run the finished capstone agent locally with `make console AGENT=...`. 2. Book an appointment and trigger a transfer request, and recognise which course section built each behaviour. 3. Pin a demo date with `MAPLE_TODAY` so every run is reproducible. |
| Prerequisites | 2.4 |
| Files used | `03-code/agents/s13_capstone_receptionist.py`, `03-code/Makefile`, `03-code/.env` |

### Script

[AVATAR]
You've just set up everything. Before you write a single line, let's run the finished product. The same Riley you heard in lecture one, on your own laptop. [PAUSE] Hearing the destination makes the journey a lot easier to follow.

[SCREEN: VS Code, `.env` open. Add one line at the bottom.]

One setting first. The clinic's calendar is fake, and it's built relative to today's date. To make my demo match yours exactly, I'll pin the date.

[CODE: add to `.env`]
```bash
MAPLE_TODAY=2026-10-05
```

Now "today" is Monday, October fifth, twenty twenty-six, for every agent in the repo. Delete this line whenever you want the real date back.

[SCREEN: Terminal in the repo folder.]

[CODE: run the capstone agent in console mode]
```bash
make console AGENT=agents/s13_capstone_receptionist.py
```

The Makefile's console target runs whichever agent file you pass in. Under the hood it's `uv run python agents/s13_capstone_receptionist.py console`. Put on your headphones.

[DEMO: Real conversation. Speak naturally; don't script your side too tightly.]

**Riley:** Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?

**You:** Hi, I need a cleaning. Do you have anything Thursday afternoon?

**Riley:** One moment while I check the schedule. [PAUSE] I have Thursday, October eighth at one, one thirty or two in the afternoon. Which works best?

**You:** One thirty.

**Riley:** Great. Can I get your full name?

**You:** Alex Kim.

**Riley:** Thanks, Alex. What's the best phone number to reach you?

**You:** Five one two, five five five, zero one six six.

**Riley:** Just to confirm: Alex Kim, Thursday, October eighth at one thirty in the afternoon, for a cleaning. Shall I go ahead?

**You:** Yes.

**Riley:** You're booked for Thursday at one thirty. Just a reminder, we ask for twenty-four hours' notice to cancel. Anything else?

**You:** Actually, can I talk to a real person about my bill?

**Riley:** I'm sorry, transfers aren't available on this line right now. I can take a message and have the front desk call you back. Would that help?

[AVATAR]
Let's unpack what just happened, because nearly every section of the course showed up in that one minute.

[SLIDE 1: What you just heard, and where it's built]
- Greeting with AI disclosure → Section 4
- "One moment while I check the schedule" → Section 5 (filler speech)
- Only real slots, three at most → Section 5 (tools + scheduler)
- Read-back before booking → Section 5
- Cancellation policy reminder → Section 5
- Clinic facts from the FAQ → Section 7
- Transfer request handled safely → Section 8
- Refuses tricks and medical advice → Section 11

The greeting disclosed that Riley is an AI. That's Section four. "One moment while I check the schedule" is filler speech, which hides tool latency. Section five. The times were real, pulled from the scheduler, and never more than three. The read-back before booking and the cancellation reminder, also Section five.

And the transfer. In console mode there's no phone line, so there's nobody to transfer to. Watch what Riley did. It didn't pretend. It apologized and offered to take a message. That graceful fallback is written into the transfer tool, and you'll build it in Section eight. On a real phone number, that same request connects you to a human.

[SCREEN: Terminal. Scroll up through the console log. Highlight the lines where `find_available_slots` and `book_appointment` were called, with their arguments.]

Now scroll up in the terminal. See these lines? That's Riley calling find available slots, with day and part of day. And then book appointment, with the name, phone and slot. The LLM never touched the calendar directly. It asked, and our code did the work. You'll learn to write tests that check exactly these calls.

[SCREEN: Terminal. Run it again and try to trip Riley up: ask "What should I take for tooth pain?"]

Try to break it. Ask for medical advice. Ask it to ignore its instructions. Ask it for Sunday. You'll find it's surprisingly hard to trip up, and by Section eleven you'll know why.

[AVATAR]
Here's the thing I want you to notice. None of that was one big clever prompt. It's a dozen small, tested pieces. And you'll build every one of them, starting with a thirty-line agent in Section three.

If you ever get lost later in the course, come back and run this file. It's your reference for "what good looks like."

**Recap:** `make console AGENT=agents/s13_capstone_receptionist.py` runs the finished Riley locally, and every behaviour you hear maps to a section you're about to build.

**Transition:** Before you start building, one more setup lecture: how to cap your spending and practice for free with mock mode.

### Speaker notes: common student mistakes / Q&A

- Mistake: forgetting to delete `MAPLE_TODAY` later, then wondering why "tomorrow" is always October sixth. It's a demo pin, not a real setting.
- Mistake: expecting a real transfer in console mode. Transfers need a SIP phone call (Section 8). The graceful fallback is the correct behaviour here.
- "Riley offered different times than yours." If `MAPLE_TODAY` isn't set, the demo calendar is relative to your real date. Pin it to match the video.
- The capstone uses more features, so its first response can take a moment longer while models warm up. Later turns are faster.

---

## Lecture 2.7 — Spending caps, free tiers and offline mock mode

| Field | Value |
|---|---|
| ID | 2.7 |
| Type | SC (screencast) |
| Target duration | 6:00 (~550 spoken words, about 3:56 of talking at 140 wpm) |
| Learning objectives | 1. Set hard spending limits on OpenAI and check usage on LiveKit Cloud and optional providers. 2. Run Riley at zero cost with `MOCK_MODE=1` and text I/O. 3. Estimate a lab's cost before running it with `src/maple/costs.py`. |
| Prerequisites | 2.1, 2.4 |
| Files used | `03-code/src/maple/config.py`, `03-code/agents/common.py`, `03-code/src/maple/costs.py`, `10-resources/provider-cost-guide.md` |

### Script

[AVATAR]
In Lecture 2.1, I promised the whole course costs around ten to twenty dollars. This lecture is how you make sure of that. Three habits. Hard caps, so nothing can run away. A mock mode, so practice is free. And a quick estimate before any lab that uses real minutes.

[SCREEN: Browser, platform.openai.com → Settings → Limits. Show the monthly budget field and the notification threshold. Values visible, keys hidden.]

Habit one, hard caps. Start with OpenAI, because it's the one with no free tier. Under Limits, set a monthly budget. I use twenty dollars. Then set an email alert at half of that, so you hear about it early.

[SCREEN: Browser, cloud.livekit.io → project → Usage/Billing page. Point to agent session minutes and inference usage for the current month.]

Next, LiveKit Cloud. On the free plan you can't overspend by accident, because usage is capped at the plan's allowance. Check this page once a week. It shows agent minutes and LiveKit Inference usage, which covers speech-to-text, the LLM and the voice when you use model strings.

[SCREEN: Quick pass over Deepgram and Cartesia usage pages, only if you created those accounts.]

If you created Deepgram or Cartesia accounts for direct plugins, both show usage against your credit. Starter credits run out rather than billing you, but check each provider's settings, because policies change.

[SLIDE 1: Where your money goes (placeholder prices, check current pricing)]
- Cascaded call: roughly seven cents per minute in our example price table
- Biggest slice: text-to-speech, then platform minutes
- Speech-to-speech: several times more per minute
- Unit tests, text mode and mock mode: zero

Here's the rough picture using the placeholder price table in the repo. A cascaded call costs a few cents per minute. Text-to-speech is the biggest slice. Speech-to-speech costs several times more per minute. And unit tests, text mode and mock mode cost nothing. Prices change, so check current pricing before you trust any of these numbers.

[AVATAR]
Habit two, practice for free. Most of your time in this course is spent on prompts and tool logic, not on voices. You don't need to pay for speech while you're doing that.

[SCREEN: Terminal.]

[CODE: run Riley in offline mock mode (macOS and Linux)]
```bash
MOCK_MODE=1 uv run python agents/s05_booking_agent.py console --text
```

[CODE: the same on Windows PowerShell]
```powershell
$env:MOCK_MODE = "1"; uv run python agents/s05_booking_agent.py console --text
```

Set MOCK_MODE to one and run the agent in text mode. Now there's no speech-to-text and no voice, because we're typing. And the LLM is replaced by a small scripted fake. Nothing leaves your laptop, and nothing is billed.

[DEMO: Type "I'd like to book a cleaning on Thursday". The scripted fake replies, and the log shows a real `find_available_slots` call against the real scheduler.]

Watch the log. The fake LLM still calls the real tools, against the real scheduler. That's perfect for checking your tool code, your error messages and your read-back wording. What it can't tell you is how a real model behaves, so once your code works in mock mode, switch it off for a few real test calls.

You can also put MOCK_MODE equals one in your dot env while you're working on tools, and remove it when you want the real thing. The switch is read by `src/maple/config.py`, and the agents pick it up through `agents/common.py`.

[AVATAR]
Habit three, estimate before you run. Every lab tells you roughly how many call minutes it needs. Turn that into dollars before you start.

[CODE: estimate ten minutes of cascaded calls]
```bash
uv run python -c "from maple.costs import cost_breakdown, typical_cascaded_usage; print(cost_breakdown(typical_cascaded_usage(10)).format())"
```

[DEMO: Output]
```text
stt            $0.0385
llm            $0.0953
tts            $0.4500
realtime       $0.0000
platform       $0.1000
telephony      $0.0000
total          $0.6838
per minute     $0.0684  (10.00 min)
```

This uses the course's cost calculator with a typical receptionist call. Ten minutes of cascaded calls comes out around seventy cents with the placeholder prices. Swap in typical realtime usage and you'll see it's a few times more. You'll build a proper version of this report from real usage data in Section ten.

[SLIDE 2: Your spending checklist]
- OpenAI monthly budget set, alert at 50%
- LiveKit usage page bookmarked
- `MOCK_MODE=1` for tool and prompt work
- `console --text` when you don't need to hear it
- Estimate minutes × cost per minute before voice labs
- Stop `dev` servers and release unused phone numbers

[AVATAR]
Here's your checklist. Caps set. Usage page bookmarked. Mock mode for tool work. Text mode when you don't need to hear it. A quick estimate before voice labs. And shut things down when you're done.

**Recap:** Hard caps prevent surprises, `MOCK_MODE=1` with `console --text` makes practice free, and the cost calculator turns a lab's minutes into dollars before you start.

**Transition:** Your environment is ready and your budget is safe, so Section 3 starts with the LiveKit mental model: rooms, participants, tracks and dispatch.

### Speaker notes: common student mistakes / Q&A

- Mistake: leaving `MOCK_MODE=1` in `.env`, then reporting that "Riley got dumb." Mock replies are scripted. Remove the line for real conversations.
- Mistake: trusting the placeholder price table as a quote. It's for relative comparisons. Update `PriceTable` values from your own invoices.
- "Does mock mode need LiveKit keys?" It's designed to run offline in text mode. Voice mode always needs real STT and TTS.
- Windows: `MOCK_MODE=1 uv run ...` doesn't work in PowerShell. Use `$env:MOCK_MODE = "1"` first, or put it in `.env`.
