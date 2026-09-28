# Section 12: Deploying to Production

> **Course:** Production Voice AI Agents with Python: Build, Test, Deploy
> **Section runtime:** ≈57 min (9 lectures, curriculum v1.1)
> **Source of truth:** `01-curriculum/curriculum.md`
> **On-screen footer for every code or API slide:** "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."

## How to read these scripts

| Cue | Meaning |
|---|---|
| `[AVATAR]` | HeyGen avatar on camera. Keep each avatar block under about sixty seconds of speech. |
| `[SLIDE n: title]` | Full-screen slide. Bullets listed under the cue are the exact slide text. |
| `[SCREEN: ...]` | OBS screen recording. Voice-over continues over the recording. |
| `[CODE: ...]` | Code typed live or revealed line by line. Fenced block is the exact text. |
| `[DEMO: ...]` | Live interaction with the agent. Record the real audio. |
| `[B-ROLL: ...]` | Cutaway footage or motion graphic. |
| `[PAUSE]` | One beat of silence (about one second). Leave room for the edit. |

Pacing: narration is written at about 140 spoken words per minute. Word targets in each header count spoken words only (narration plus scripted demo dialogue), not cues or code.

| ID | Title | Type | Target | Spoken words (target) |
|---|---|---|---|---|
| 12.1 | Agent server architecture and scaling | SL | 8:00 | ~950 |
| 12.2 | Dockerising the agent | SC | 8:00 | ~810 |
| 12.3 | Deploy to LiveKit Cloud | SC | 10:00 | ~790 |
| 12.4 | Self-hosting option | SL | 6:00 | ~690 |
| 12.5 | A web front end for Riley | SC | 8:00 | ~630 |
| 12.6 | Production readiness checklist | SL | 6:00 | ~630 |
| 12.7 | Lab 7: Deploy and call your agent | LAB | 4:00 | ~320 |
| 12.8 | Chaos demo: kill a provider mid-call | DM | 5:00 | ~490 |
| 12.9 | Quiz: Deployment | QZ | 2:00 (0:45 video) | ~70 |

**Verification notes for the editor.**
- `AgentServer` options in 12.1 were checked by introspecting `livekit-agents` 1.8.3: `setup_fnc`, `num_idle_processes` (dev 0, production defaults to the CPU count), `load_threshold` (dev disabled, production 0.7), `job_memory_warn_mb` (1000), `job_memory_limit_mb` (0 = off), `drain_timeout` (3600 s), `port` (dev random, production 8081). The health server answers `GET /` with `OK` (or 503) and `GET /worker` with JSON.
- The agent CLI commands are `console | dev | start | connect | download-files`. `start --help` shows `--log-level`, `--url`, `--api-key`, `--api-secret` and `--drain-timeout`.
- **Every `lk agent ...` command in 12.3, 12.7 and 12.8, and the front-end starter commands in 12.5, are marked "verify in current docs".** The LiveKit CLI changes faster than the SDK. Re-run each command before recording and update the on-screen text if flags changed.
- Agent name resolution (checked in `livekit-agents` 1.8.3): `LIVEKIT_AGENT_NAME` is read in every mode; `[agent] name` in `livekit.toml` is used only by `start`, and only when the env var is unset. `dev` never reads `livekit.toml`.
- The fallback model strings in `.env.example` (`FALLBACK_LLM_MODEL`, `FALLBACK_STT_MODEL`, `FALLBACK_TTS_MODEL`) are **unverified** against LiveKit Inference's current model list. Check before recording 12.8.
- Code on screen matches `03-code/` (`deploy/Dockerfile`, `deploy/.dockerignore`, `livekit.toml.example`, `frontend/README.md`, `agents/common.py`). The chaos helper `agents/s12_chaos_demo.py` in 12.8 is new and must be added to the repo before publishing.

---

## Lecture 12.1 — Agent server architecture and scaling

| Field | Value |
|---|---|
| ID | 12.1 |
| Type | SL (slides + avatar) |
| Target duration | 8:00 (~950 spoken words) |
| Learning objectives | 1. Explain how an `AgentServer` registers with LiveKit, receives jobs and runs each call in its own process. 2. Configure prewarming, idle processes, load threshold, memory limits and draining for production. 3. Describe what happens to live calls during a deploy. |
| Prerequisites | 3.1 (rooms, participants, dispatch), 3.3 (`AgentServer` + `cli.run_app`) |
| Files used | `agents/common.py` (`prewarm`, `load_vad`), `agents/s13_capstone_receptionist.py` (`AgentServer(setup_fnc=prewarm)`) |

### Script

[AVATAR]
Here's a question that sounds simple. What happens when two hundred people call Maple Street Dental at nine A M on a Monday?

On your laptop, Riley handled one call at a time, and you were the only caller. In production, calls arrive in bursts. Some last twenty seconds. Some last twenty minutes. And you'll deploy new versions while calls are live.

This lecture is the mental model for all of that. How the agent server works, and the handful of settings that decide whether your deploys are boring or terrifying.

[SLIDE 1: The agent server, one diagram]
Diagram: LiveKit (Cloud or self-hosted) ⇄ WebSocket ⇄ Agent server (main process) → job processes (one per call) + idle warm processes
- The server connects out to LiveKit over a WebSocket
- LiveKit sends a job request when a room needs an agent
- Each accepted job runs in its own process

Let's go back to the picture from Section 3. When you run `python agent.py start`, you start an agent server. The server opens a WebSocket out to LiveKit and registers. "I'm here. I can run the agent called riley-receptionist."

When a caller joins a room that needs Riley, LiveKit sends a job request to one of the registered servers. The server accepts it and runs your entrypoint function for that one call.

And here's the key detail. Each job runs in its own process. If one call crashes, or leaks memory, or gets stuck in a slow tool, the other calls on that server are unaffected. That isolation is a big reason agent servers are reliable.

[SLIDE 2: Cold starts and prewarming]
- Starting a process and loading models takes time
- The caller hears silence while that happens
- `setup_fnc` runs once per process, before any call arrives
- `num_idle_processes` keeps warm processes ready

Now, starting a process isn't free. Python has to import your code, and the VAD model has to load into memory. If that happens after the caller connects, the caller hears silence. A second of dead air at the start of a call feels broken.

So we do two things. First, prewarming. `setup_fnc` is a function that runs once per process, before any call arrives. We use it to load Silero VAD.

[CODE: prewarm in `agents/common.py`]
```python
def prewarm(proc: JobProcess) -> None:
    """Load the Silero VAD once per process (``AgentServer(setup_fnc=prewarm)``)."""
    from livekit.plugins import silero

    proc.userdata["vad"] = silero.VAD.load()


def load_vad(proc: JobProcess | None) -> Any:
    """Return the prewarmed VAD, loading one if the process was not prewarmed."""
    if proc is not None and "vad" in proc.userdata:
        return proc.userdata["vad"]
    from livekit.plugins import silero

    return silero.VAD.load()
```

The loaded model goes into `proc.userdata`, a dictionary that lives as long as the process. Then in the entrypoint, `load_vad(ctx.proc)` picks it up instantly. And there's a fallback, so the same code works in console mode where nothing was prewarmed.

Second, idle processes. `num_idle_processes` is how many warm processes the server keeps ready. When a call arrives, it gets one that's already prewarmed. In production mode, the default is the number of CPU cores. In dev mode, it's zero, so your laptop stays quiet.

[SLIDE 3: Load and the load threshold]
- The server reports its load to LiveKit continuously
- Default load = CPU usage of the machine
- Above `load_threshold`, the server stops accepting new jobs
- Production default: 0.7 (70%). Dev: disabled

How does LiveKit decide which server gets the next call? Load. Each server reports a load number between zero and one. By default, that's CPU usage.

`load_threshold` is the line. Above it, the server marks itself unavailable, and new calls go to other servers. The production default is point seven. That leaves thirty percent headroom, so calls already running don't stutter when a new one starts. Voice is real-time. A CPU at a hundred percent means choppy audio for everyone on that machine.

If CPU isn't the right signal for your agent, you can pass your own `load_fnc`. For example, a count of active calls divided by a maximum you measured.

[SLIDE 4: Memory limits]
- `job_memory_warn_mb`: log a warning above this (default 1000 MB)
- `job_memory_limit_mb`: kill the job above this (default 0, off)
- One runaway call shouldn't take down the container

Memory next. `job_memory_warn_mb` logs a warning when one call's process gets big. The default is a thousand megabytes. `job_memory_limit_mb` is the hard stop. Above it, that call's process is killed. The default is zero, meaning off.

Should you turn it on? In production, yes. A killed call is bad. A whole container running out of memory and taking twenty calls with it is much worse. Measure a normal call first, then set the limit comfortably above it.

[SLIDE 5: Draining: deploys without dropped calls]
- On SIGTERM, the server stops taking new jobs
- Active calls continue until they end, or `drain_timeout` passes
- Default `drain_timeout`: 3600 seconds (one hour)
- Your platform must wait at least that long before force-killing

And now the setting that makes deploys boring. Draining.

When you deploy, the old container gets a SIGTERM signal. A LiveKit agent server doesn't just die. It stops accepting new calls, and waits for active calls to finish. New calls go to the new version. Old calls finish on the old one. Nobody gets hung up on.

`drain_timeout` is how long it waits. The default is one hour. After that, remaining calls are closed. For a dental receptionist, calls rarely pass ten minutes, so thirty minutes is plenty.

There's one catch, and it bites everyone once. Your container platform also has a timeout. Kubernetes, for example, force-kills a pod after its grace period. If that's thirty seconds, your nice one-hour drain becomes a thirty-second drain. We'll fix that in Lecture 12.4.

[SLIDE 6: Putting it together]
[CODE: production server options]
```python
from common import prewarm

server = AgentServer(
    setup_fnc=prewarm,
    num_idle_processes=2,
    load_threshold=0.7,
    job_memory_warn_mb=700,
    job_memory_limit_mb=1000,
    drain_timeout=1800,
    port=8081,
)
```

In the repo, every agent uses `AgentServer(setup_fnc=prewarm)` and relies on the production defaults. Here's how it looks when you set them explicitly, which I recommend once you've measured real calls. Prewarm with our function. Two idle processes. Load threshold point seven. Warn at seven hundred megabytes, kill at a thousand. Drain for thirty minutes. And the health check on port eighty eighty-one, which is also the production default.

These numbers are starting points, not rules. You'll tune them with real traffic. Watch two things in your first week. The memory warning in your logs, which tells you if the limit is too tight. And how often a server reports itself full, which tells you whether to add replicas or lower the idle process count.

[SLIDE 7: dev vs start]
| | `dev` | `start` |
|---|---|---|
| Hot reload | Yes | No |
| Idle processes | 0 | CPU count |
| Load threshold | Off | 0.7 |
| Health port | Random | 8081 |
| Log level | DEBUG | INFO |

Last slide. All those defaults depend on how you launch. `dev` is for your laptop. Hot reload, no idle processes, no load limit, debug logs. `start` is for production. No reload, warm processes, a load limit, the health check on eighty eighty-one, and info-level logs.

So in your Dockerfile, the command is always `start`. We'll write that Dockerfile next.

[AVATAR]
So, back to two hundred callers at nine A M. Each call gets its own process. Warm processes absorb the first burst. The load threshold spreads the rest across servers. Memory limits contain any runaway call. And when you deploy at nine fifteen, draining lets every conversation finish. That's the architecture.

**Recap:** An agent server runs each call in its own prewarmed process, sheds load above a threshold, caps memory per call, and drains active calls on shutdown.

**Transition:** Next, we'll package Riley into a production Docker image that runs `start` as a non-root user.

### Speaker notes: common student mistakes / Q&A

- Mistake: loading the VAD model inside the entrypoint. That adds the load time to every call. Load it in `setup_fnc` and read it from `ctx.proc.userdata`.
- "Why does my laptop never accept a second call in `start` mode?" The load threshold. A busy laptop CPU can sit above 0.7. Use `dev` locally.
- "Can I use threads instead of processes?" `job_executor_type` supports a thread executor, but you lose crash and memory isolation. Keep processes in production.
- The `num_idle_processes` default in production equals your CPU count. On a large VM that's a lot of warm memory. Set it explicitly.

---

## Lecture 12.2 — Dockerising the agent

| Field | Value |
|---|---|
| ID | 12.2 |
| Type | SC (screencast / code-along) |
| Target duration | 8:00 (~810 spoken words; the rest is screen, typing and demo time) |
| Learning objectives | 1. Read and build a multi-stage Dockerfile that uses uv in the builder and ships a slim runtime image. 2. Download model files at build time, run as a non-root user, and start with an `exec`'d `start` command so draining works. 3. Build, run and health-check the container locally. |
| Prerequisites | 12.1; 2.2 (uv project setup) |
| Files used | `deploy/Dockerfile`, `deploy/.dockerignore`, `pyproject.toml`, `uv.lock`, `Makefile` (`docker-build`, `docker-run`) |

### Script

[AVATAR]
"It works on my machine" is not a deployment strategy. In this lecture, we'll package Riley into a container image that runs the same way on your laptop, in LiveKit Cloud and on any container host.

We have four goals. A small image. No model downloads during a call. No root user. And a start command that lets the server drain properly.

[SCREEN: VS Code, `deploy/.dockerignore`. Footer: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."]

Start with what we *don't* copy. The `.dockerignore`.

[CODE: `deploy/.dockerignore`]
```text
# Copy to the repo root before building: cp deploy/.dockerignore .dockerignore
.git
.github
.venv
venv
**/__pycache__
**/*.pyc
.pytest_cache
.ruff_cache
.mypy_cache
.env
.env.*
!.env.example
metrics
console-recordings
tests
frontend
pipecat
deploy
*.md
!README.md
.deepeval
```

The most important lines are `.env` and `.env.*`. Never bake your `.env` into an image. Anyone who can pull the image can read every key inside it. Secrets come in at runtime. The exclamation mark line keeps the harmless example file.

`livekit.toml` is excluded too. The agent's name will come from an environment variable instead, which we'll set as a secret in the next lecture.

The rest keeps the image small. No virtual environment from your laptop, no git history, no tests, no front end, no Pipecat.

One Docker detail, and it's in the first line of the file. Docker only reads `.dockerignore` from the root of the build context. Ours lives in `deploy/`, so it gets copied to the repo root before a build.

Now the Dockerfile. Two stages. Here's the top, and the builder.

[CODE: `deploy/Dockerfile`, header and builder stage]
```dockerfile
# syntax=docker/dockerfile:1.7
# Production image for Riley (lecture 12.2).
#
# Build from the repo root (the build context must contain src/ and agents/):
#   cp deploy/.dockerignore .dockerignore      # Docker only reads .dockerignore at the context root
#   docker build -f deploy/Dockerfile -t riley-agent .
#   docker run --rm --env-file .env riley-agent
# `make docker-build` does both steps.
#
# Stages:
#   builder  - installs dependencies into /app/.venv with uv (compilers available here only)
#   runtime  - slim image, non-root user, model weights downloaded at build time

ARG PYTHON_VERSION=3.11
ARG AGENT_FILE=agents/s13_capstone_receptionist.py

# ---------------------------------------------------------------- builder
FROM python:${PYTHON_VERSION}-slim AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# 1) dependencies only (cached until pyproject.toml changes)
#    For reproducible builds commit uv.lock, add `COPY uv.lock ./` and use `uv sync --locked`.
COPY pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --extra observability

# 2) the project itself
COPY src ./src
COPY agents ./agents
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra observability

# pip alternative (no uv):
#   RUN python -m venv /app/.venv && /app/.venv/bin/pip install ".[observability]"
```

Two build arguments at the top. The Python version, and `AGENT_FILE`, which defaults to the capstone. You can point it at any agent file.

The builder starts from the official slim Python image, and installs compilers. Some dependencies build native code, and the compilers stay in this stage only. They never ship.

Then we copy the `uv` binary straight out of uv's official image. That's a neat trick. No install script, just one file.

Look at the order of the copies. First, only `pyproject.toml`, the README and the lock file. Then we install dependencies, without our own project. Then we copy our code, `src` and `agents`, and sync again. Why split it? Docker caches each step. Dependencies change rarely. Code changes constantly. With this order, a code change rebuilds in seconds, not minutes.

`uv.loc[k]` with square brackets is a small glob trick. It copies the lock file if it exists, and doesn't fail if it doesn't. Commit your `uv.lock`, so production gets exactly the versions you tested.

We install the `observability` extra, so OpenTelemetry is available for Langfuse tracing. Dev tools like pytest are a separate extra, so they're left out.

And `--mount=type=cache` keeps uv's download cache between builds on your machine. That needs BuildKit, which is the default in current Docker.

[CODE: `deploy/Dockerfile`, runtime stage]
```dockerfile
# ---------------------------------------------------------------- runtime
FROM python:${PYTHON_VERSION}-slim AS runtime
ARG AGENT_FILE

RUN useradd --create-home --uid 10001 riley
WORKDIR /app
COPY --from=builder --chown=riley:riley /app /app

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    AGENT_FILE=${AGENT_FILE}

USER riley

# Download VAD / turn-detector weights into the image so cold starts don't hit the network.
RUN python ${AGENT_FILE} download-files

# Agent name for telephony/explicit dispatch: pass -e LIVEKIT_AGENT_NAME=riley-receptionist
# (LiveKit Cloud deployments inject it for you).

# Health check / metrics port used by `start` (AgentServer default 8081).
EXPOSE 8081

CMD ["sh", "-c", "exec python \"$AGENT_FILE\" start"]
```

Stage two is what actually ships. A plain slim Python image. No uv, no compilers. We copy only the finished app folder from the builder.

Then a non-root user called `riley`. If someone ever finds a hole in a dependency, they land in a container as an unprivileged user, not as root.

Next, `download-files`. That's one of the five agent CLI commands. It downloads the model weights your plugins need, like Silero VAD and the turn detector's local model, into the image. We run it *after* switching to the `riley` user, so the files land in `riley`'s cache, where the agent will look for them. Without this line, the first call on every new container would wait for a download.

Port eighty eighty-one is the health check, the production default from Lecture 12.1.

And the last line. The command is `start`, production mode. Notice the `exec`. We use a shell so the environment variable expands. But `exec` replaces the shell with Python. That matters, because when the platform sends SIGTERM to stop the container, it has to reach Python. Otherwise the shell swallows it, and all that draining from the last lecture never happens.

[SCREEN: Terminal, repo root.]

Build it. Since we haven't built the capstone yet, point it at the Section 11 guarded agent.

```bash
cp deploy/.dockerignore .dockerignore
docker build -f deploy/Dockerfile \
  --build-arg AGENT_FILE=agents/s11_guarded_agent.py \
  -t riley-agent .
```

For the capstone default, `make docker-build` runs the same two steps.

[SCREEN: Build output. Highlight the `download-files` step and the final image size.]

The first build takes a few minutes. Watch the `download-files` step. That's the model download happening once, at build time.

Now run it. The keys come from your `.env` file at runtime, not from the image. And we publish port eighty eighty-one so we can check health from the laptop.

```bash
docker run --rm --env-file .env -p 8081:8081 riley-agent
```

[SCREEN: Logs show the server starting in production mode and registering with LiveKit.]

The log says it registered with LiveKit. In a second terminal, check health.

```bash
curl http://localhost:8081/
curl http://localhost:8081/worker
```

[SCREEN: `OK`, then a JSON blob with `agent_name`, `active_jobs` and `worker_load`.]

"OK" from the health endpoint. And `/worker` shows the agent name, active jobs, and current load. That's the same load number LiveKit uses to route calls.

Finally, prove draining works. Set `LIVEKIT_AGENT_NAME` in your `.env`, start a call to that agent from the Agents Playground, then stop the container while you're talking.

```bash
docker stop --time 60 $(docker ps -q --filter ancestor=riley-agent)
```

[SCREEN: Logs show the server draining, the call continuing, then a clean exit when the call ends.]

The server logs that it's draining. Your call keeps going. When you hang up, the container exits cleanly. That's `exec` doing its job. And `--time 60` is Docker's grace period. It's the same setting you'll meet again in Lecture 12.4.

**Recap:** A two-stage build with uv, model files downloaded at build time as a non-root user, and an `exec`'d `start` command give you a small image that drains calls on shutdown.

**Transition:** Next, we'll deploy that image to LiveKit Cloud and manage secrets, logs and rollbacks.

### Speaker notes: common student mistakes / Q&A

- Mistake: `CMD python agent.py start` in shell form, without `exec`. SIGTERM goes to the shell, the agent never drains, and calls drop on every deploy.
- Mistake: running `download-files` before `USER riley`. The files land in root's cache and the agent downloads them again at runtime.
- Mistake: forgetting to copy `.dockerignore` to the repo root. Your `.env` ends up inside the image. If that happened, rotate every key and rebuild.
- Apple Silicon users deploying to x86 hosts should build with `docker build --platform linux/amd64 ...`.
- `console` mode doesn't work inside the container: there's no microphone or speaker. The image is for `start`. On your laptop, `console` also needs the PortAudio library (`brew install portaudio` on macOS, `sudo apt install portaudio19-dev` on Debian/Ubuntu); use `make console-text` if audio won't work.
- Some platforms want a Docker `HEALTHCHECK` instruction. You can add one that requests `http://localhost:8081/`, but most orchestrators (Kubernetes, ECS) use their own probes instead.

---

## Lecture 12.3 — Deploy to LiveKit Cloud

| Field | Value |
|---|---|
| ID | 12.3 |
| Type | SC (screencast / code-along) |
| Target duration | 10:00 (~790 spoken words; the rest is screen, typing and demo time) |
| Learning objectives | 1. Create and deploy an agent on LiveKit Cloud with the `lk agent` CLI. 2. Manage secrets, read build and runtime logs, and roll back a bad version. 3. Verify the deployed agent with a real session. |
| Prerequisites | 12.2; 2.3 (`lk` CLI and `lk cloud auth`) |
| Files used | `deploy/Dockerfile`, `livekit.toml.example` → `livekit.toml`, `.env.production` (not committed) |

> **Every `lk agent` command in this lecture: verify in current docs** (docs.livekit.io, "Deploying to LiveKit Cloud"). Run `lk agent --help` before recording and match flags on screen.

### Script

[AVATAR]
You have a container. Now you need somewhere to run it. In this lecture, we'll deploy Riley to LiveKit Cloud's managed agent hosting. You push code, LiveKit builds the image, runs it, scales it, and routes calls to it. You never touch a server.

In Lecture 12.4, we'll cover running the same image on your own infrastructure. But this is the fastest path, and it's the one we'll use for the capstone.

[SLIDE 1: What LiveKit Cloud does for you]
- Builds your Dockerfile in the cloud
- Runs and scales agent servers near your LiveKit project
- Injects `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- Rolling deploys with draining, logs, versions and rollback

Here's what you get. LiveKit Cloud builds your Dockerfile. It runs your agent servers close to your LiveKit project. It injects the LiveKit URL and keys automatically. So you don't put those in your secrets. And it does rolling deploys with draining, plus logs, version history and rollback.

[SCREEN: Terminal, repo root. Footer: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates." and "lk agent commands: verify in current docs".]

First, make sure the CLI is logged in to the right project. We set this up in Lecture 2.3.

```bash
lk cloud auth
lk project list
```

Pick the Maple Street Dental project if you have several.

Step two. The config file. Copy the example.

```bash
cp livekit.toml.example livekit.toml
```

[CODE: `livekit.toml` (from `livekit.toml.example`)]
```toml
# Copy to livekit.toml (lecture 8.2 and 12.3).
#
# `lk agent create` writes this file for LiveKit Cloud deployments. The agent name
# below is what telephony dispatch rules and explicit dispatch target.
#
# Notes (livekit-agents 1.8):
# - `start` reads [agent] name from ./livekit.toml when LIVEKIT_AGENT_NAME is not set.
# - `dev` never reads it (dev workers stay out of the deployed pool); set
#   LIVEKIT_AGENT_NAME in .env to test named dispatch locally.
# - Passing agent_name= to @server.rtc_session() still works but is deprecated.

[project]
subdomain = "your-project-subdomain"

[agent]
name = "riley-receptionist"
# id = "CA_xxxxxxxxxxxx"   # filled in by `lk agent create`
```

Two sections. The project subdomain is the first part of your LiveKit URL. And the agent name. That's the name telephony dispatch rules and the web front end will ask for. When you create the agent, the CLI fills in the agent ID line. Commit `livekit.toml` after that, so every deploy targets the same agent.

Read the notes at the top, because they explain a gotcha. `start` reads the agent name from this file only when `LIVEKIT_AGENT_NAME` isn't set. `dev` never reads it. And our `.dockerignore` keeps `livekit.toml` out of the image. So inside the container, the name must come from an environment variable. We'll set it as a secret.

Step three. Secrets. Create a production env file, and keep it out of git.

[CODE: `.env.production` (never committed)]
```bash
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...
LIVEKIT_AGENT_NAME=riley-receptionist
TRANSFER_PHONE_NUMBER=+15125550100
STT_MODEL=deepgram/nova-3
LLM_MODEL=openai/gpt-4.1-mini
TTS_MODEL=cartesia/sonic-3
```

Only what the agent needs. The agent name, because `livekit.toml` isn't in the image. Provider keys, if you're using plugins mode. Model settings. The transfer number. Notice what's missing. No LiveKit URL or keys. LiveKit Cloud injects those. If you use LiveKit Inference for the models, you may not need the provider keys at all.

Step four. The Dockerfile. The cloud build looks for a Dockerfile at the root of the directory you deploy from. Ours lives in `deploy/`, so copy it up.

```bash
cp deploy/Dockerfile Dockerfile
cp deploy/.dockerignore .dockerignore
```

Step five. Create the agent. This registers it, uploads your code, builds and deploys the first version.

```bash
lk agent create --secrets-file .env.production
```

[SCREEN: CLI output: build logs streaming, then "deployed" with an agent ID. Show `livekit.toml` now containing an `id` line.]

It uploads the code, builds the image in the cloud, and deploys. You'll see the same build steps you saw locally, including `download-files`. When it finishes, look at `livekit.toml`. There's now an agent ID in it.

The first build is usually the slowest. When the cloud builder can reuse cached layers, like your local Docker does, a code-only change ships faster. That's one more reason the Dockerfile copies dependencies before code.

Step six. Check it's running.

```bash
lk agent status
```

[SCREEN: Status output showing the agent, its version, region and running state.]

Running, one version, and the region it's in.

[SCREEN: Browser: LiveKit Agents Playground connected to the project, with the agent name set to `riley-receptionist`. Click Connect.]

Now a real session. Open the Agents Playground for your project, set the agent name, and connect.

[DEMO: Playground session with the deployed agent.]

**Riley:** Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?

**You:** What time do you open on Saturday?

**Riley:** We're open Saturdays from nine in the morning until one in the afternoon. Would you like to book a visit?

That's Riley, running in the cloud. My laptop isn't involved anymore.

Step seven. Logs.

```bash
lk agent logs
```

[SCREEN: Runtime logs from the call just made: job received, session started, tool calls, redacted transcript lines.]

These are the runtime logs from the call I just made. Job received. Session started. The `lookup_clinic_info` tool call. And notice the transcript lines are redacted, thanks to Section 11. These logs now live on someone else's infrastructure, which is exactly why we redacted them.

If a build fails, the build logs are separate. There's a flag for that, so check `lk agent logs --help`.

Step eight. Ship a change. Let's make a small, visible one.

[CODE: shortened greeting in `src/maple/prompts.py` (demo change)]
```python
GREETING = (
    "Maple Street Dental, this is Riley, the clinic's AI assistant. "
    "How can I help?"
)
```

Shorten the greeting in `prompts.py`. Then deploy.

```bash
lk agent deploy
```

[SCREEN: Build and rollout output. Then `lk agent status` showing the new version active.]

That builds a new version and rolls it out. Old servers drain. New calls go to the new version. Nobody on an active call gets dropped.

Step nine. Rollback. Say the new version has a bug. Maybe the clinic manager says the short greeting sounds abrupt.

```bash
lk agent versions
lk agent rollback
```

[SCREEN: Version list, then rollback confirmation, then status showing the previous version active.]

List the versions. Roll back. The previous version is live again in about the time it takes to start a container, because the image is already built. No rebuild. No panic.

Step ten. Secrets change. When you rotate a key, update the secrets without changing code.

```bash
lk agent update-secrets --secrets-file .env.production
```

That restarts the agent with the new values, with the same draining behavior.

[SLIDE 2: The deploy loop]
1. `uv run pytest` passes locally (and in CI)
2. `lk agent deploy`
3. `lk agent status` and one test call
4. Watch logs and metrics for 15 minutes
5. `lk agent rollback` if anything looks wrong

[AVATAR]
Here's the loop to make a habit. Tests pass. Deploy. Check status and make one real call. Watch logs and your Section 10 dashboards for fifteen minutes. And if anything looks off, roll back first and debug second. Rolling back is cheap. Debugging in production while callers wait is not.

**Recap:** `lk agent create` registers and deploys from your Dockerfile, `deploy` ships new versions with draining, and `logs`, `versions`, `rollback` and `update-secrets` cover day-two operations.

**Transition:** Next, we'll look at running the same container on your own infrastructure, for teams that need to self-host.

### Speaker notes: common student mistakes / Q&A

- Mistake: putting `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` in the secrets file. LiveKit Cloud injects them. Duplicates can point the agent at the wrong project.
- Mistake: committing `.env.production`. Add it to `.gitignore` before creating it. If it was committed, rotate every key in it.
- "My agent deployed but never answers." Check the agent name. With an agent name set, LiveKit uses explicit dispatch, so the playground, front end or SIP dispatch rule must request `riley-receptionist`.
- CLI subcommands and flags change between `lk` releases. If a command on screen fails, run `lk agent --help` and check the LiveKit deployment docs; the repo README tracks the current commands.

---

## Lecture 12.4 — Self-hosting option

| Field | Value |
|---|---|
| ID | 12.4 |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (~690 spoken words) |
| Learning objectives | 1. List the requirements for self-hosting an agent server on any container platform. 2. Configure health checks, graceful shutdown and autoscaling correctly. 3. Decide when self-hosting is worth the operational cost. |
| Prerequisites | 12.1, 12.2 |
| Files used | `deploy/Dockerfile` |

### Script

[AVATAR]
Maybe your company runs everything on Kubernetes. Maybe your compliance team wants the agent in your own cloud account. Or maybe you want to use your existing platform, like Render, Fly.io or AWS ECS. The good news: the image you built in Lecture 12.2 runs anywhere containers run. You just need to get five things right.

[SLIDE 1: Five requirements]
1. Outbound network access to LiveKit and your model providers
2. Secrets as environment variables
3. A health check on port 8081
4. A shutdown grace period at least as long as `drain_timeout`
5. Autoscaling on CPU, with headroom

Here they are. Outbound network. Secrets. Health checks. Graceful shutdown. And autoscaling. Let's take them one at a time.

[SLIDE 2: Networking: outbound only]
- The agent server dials out to LiveKit over a secure WebSocket
- Media flows through LiveKit, not through a public port on your container
- No inbound ports needed, except the health check for your platform
- Allow outbound HTTPS to STT, LLM and TTS providers

Networking is simpler than people expect. The agent server connects out to LiveKit. It doesn't need a public IP or an open inbound port for calls. The audio comes through LiveKit's infrastructure.

So the only inbound port is the health check, and only your platform needs to reach it. Outbound, you need LiveKit, plus your model providers. If your company locks down egress, give the network team that list.

One more networking detail. If you use LiveKit Inference, the model traffic goes to LiveKit too, so the egress list gets shorter. If you use provider plugins with your own keys, every provider's API host goes on the list. Either way, test from inside the real network before launch day, not from your laptop.

[SLIDE 3: Secrets and config]
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (you set these when self-hosting)
- Provider keys and model settings from `.env.production`
- Use your platform's secret store, never the image

When you self-host, *you* set the LiveKit URL and keys, unlike LiveKit Cloud. The server reads them from environment variables. Put everything in your platform's secret store. Every platform has one. Kubernetes has secrets. ECS reads from a secrets manager. Render and Fly.io have their own secret settings.

And plan rotation now. When a key rotates, you update the secret and restart the containers. Because the servers drain, a rolling restart is safe during business hours.

[SLIDE 4: Health checks]
- `GET /` on port 8081 → `200 OK` when connected, `503` when not
- `GET /worker` → JSON with agent name, active jobs and load
- Use `/` for liveness; alert on repeated failures

Health checks. In production mode, the agent server listens on port eighty eighty-one. `GET` slash returns "OK" when things are healthy, and a 503 if the server can't reach LiveKit or its inference process died. That's exactly what a liveness probe wants.

`GET` slash worker returns JSON with active jobs and load. That's great for dashboards.

If you already run Prometheus, `AgentServer` also has a `prometheus_port` option that exposes metrics for scraping. Combine that with the call-level metrics from Section 10, and your on-call engineer sees both the servers and the conversations.

[SLIDE 5: Graceful shutdown: the setting that bites everyone]
[CODE: Kubernetes pod spec excerpt]
```yaml
spec:
  terminationGracePeriodSeconds: 1800   # >= drain_timeout in AgentServer
  containers:
    - name: riley
      image: registry.example.com/riley-agent:1.4.0
      ports:
        - containerPort: 8081
      livenessProbe:
        httpGet:
          path: /
          port: 8081
        periodSeconds: 30
      resources:
        requests:
          cpu: "2"
          memory: 4Gi
```

Here's the one that bites everyone. Remember draining from Lecture 12.1? We set `drain_timeout` to eighteen hundred seconds. But Kubernetes, by default, gives a pod thirty seconds after SIGTERM, then kills it. So in a default setup, every deploy drops every call that's longer than thirty seconds.

The fix is one line. `terminationGracePeriodSeconds`, set to at least your drain timeout. Every platform has an equivalent. On ECS it's the stop timeout. On other hosts, look for "shutdown grace period" or "kill timeout." Check the maximum each platform allows. Some cap it much lower than thirty minutes, and that might decide which platform you use.

And the resource numbers in this example? Placeholders. Measure a real call, then size.

[SLIDE 6: Autoscaling]
- Scale on CPU: it's what `load_threshold` uses
- Target below 0.7 so new containers start before servers refuse jobs
- Keep a minimum of 2 replicas for redundancy
- Scale-in triggers draining: that's fine, if the grace period is right

Autoscaling. The simplest good setup is to scale on CPU. That's the same signal the agent server uses for its load threshold. Set your autoscaler's target a bit below point seven, say point five or point six. That way, new containers start before existing servers begin refusing calls.

Keep at least two replicas. One crashed container shouldn't mean nobody answers the phone. And if your callers are spread out, run replicas in the region closest to your LiveKit project and your model providers. Every network hop is latency the caller hears.

Remember the idle processes from Lecture 12.1, too. Each replica keeps warm processes, and each one holds a VAD model in memory. More replicas with fewer idle processes each is usually cheaper than a few huge machines.

And when the autoscaler scales in, it sends SIGTERM. That triggers draining, which is exactly what you want, as long as your grace period is right.

[SLIDE 7: Self-host or managed?]
| Self-host when... | Use LiveKit Cloud agents when... |
|---|---|
| Compliance requires your own account or region | You want the fastest path to production |
| You already run a container platform well | You don't have a platform team |
| You need custom networking or sidecars | Rollbacks and scaling should be one command |

[AVATAR]
So which should you choose? Self-host when compliance needs it, when you already run a platform well, or when you need custom networking. Otherwise, managed hosting is less work, and the work it saves is the boring, risky kind. Either way, it's the same image and the same code.

**Recap:** Self-hosting needs outbound networking, secrets, a health check on 8081, a grace period at least as long as `drain_timeout`, and CPU-based autoscaling with headroom.

**Transition:** Next, we'll give Riley a web front end so people can talk to it from a browser.

### Speaker notes: common student mistakes / Q&A

- Mistake: putting the agent behind a load balancer and expecting calls to flow through it. Calls come through LiveKit. Only the health check needs a port.
- Mistake: scaling on memory. Voice agents are usually CPU-bound. Watch both, scale on CPU.
- "Can I run the LiveKit server itself too?" Yes, LiveKit server is open source. That's a larger operational job (media ports, TURN, scaling) and outside this course.
- Serverless platforms that freeze or kill idle containers are a poor fit. Agent servers hold a long-lived WebSocket and need to drain.

---

## Lecture 12.5 — A web front end for Riley

| Field | Value |
|---|---|
| ID | 12.5 |
| Type | SC (screencast / code-along) |
| Target duration | 8:00 (~630 spoken words; the rest is screen, typing and demo time) |
| Learning objectives | 1. Run the LiveKit React agent starter against your LiveKit project. 2. Explain what the token server does and why it must run on a server. 3. Dispatch the named agent (`riley-receptionist`) from the front end. |
| Prerequisites | 12.3 (deployed agent); Node.js 18+ and pnpm installed |
| Files used | `frontend/README.md`, the starter's `.env.local` and `app-config.ts` |

> **Front-end starter commands: verify in current docs.** The starter repo's name, template command, env variable names and config file change more often than the agent SDK. Check `frontend/README.md` and the starter's own README before recording.

### Script

[AVATAR]
Phones are great. But lots of clinics want a "talk to us" button on their website too. In this lecture, we'll put a voice widget in a browser, connected to the Riley you just deployed. And we'll do it without writing a front end from scratch.

[SLIDE 1: Three pieces]
Diagram: Browser (React app) → Token server (your backend) → LiveKit room ← Riley (deployed agent)
- The browser needs a short-lived access token to join a room
- Only a server may mint tokens, because it needs your API secret
- The token can ask LiveKit to dispatch a named agent into the room

There are three pieces. The browser app. A token server. And the agent you already deployed.

The browser can't join a LiveKit room without an access token. A token is signed with your API secret, and your secret must never reach the browser. So a small backend mints tokens. The browser asks the backend, "can I have a token?", and the backend decides.

And here's the detail that matters for us. Riley has an agent name, which means explicit dispatch. LiveKit won't send Riley into a room unless someone asks. The token can do that asking.

[SCREEN: Terminal. Footer: "front-end starter commands: verify in current docs".]

We'll use LiveKit's React agent starter. It's a Next.js app with a voice UI, captions and a built-in token route. Create it from the template.

```bash
lk app create --template agent-starter-react riley-web
cd riley-web
```

If that command has changed, the starter is also on GitHub, at `livekit-examples/agent-starter-react`, and you can clone it directly. Our `frontend/README.md` has both options.

[SCREEN: `.env.local` in the editor.]

The app needs your project URL and keys in `.env.local`. `lk app env -w` writes that file for you. These stay on the server side of the Next.js app, in the starter's `/api/connection-details` route. Never put the secret in a variable that starts with `NEXT_PUBLIC`, because those are sent to the browser.

[CODE: `.env.local`]
```bash
LIVEKIT_URL=wss://<your-project-subdomain>.livekit.cloud
LIVEKIT_API_KEY=<your-api-key>
LIVEKIT_API_SECRET=<your-api-secret>
```

Now, the agent name. The starter has an app config file, `app-config.ts` at the time of writing, with an `agentName` setting. Set it to `riley-receptionist`. Check the starter's README if the field has moved in your version.

[SCREEN: `app-config.ts`, `agentName` set to `"riley-receptionist"`. Also show the title, accent color and start button text ("Call Maple Street Dental") changed.]

While we're here, change the title, the accent color and the start button text. Thirty seconds of branding makes a demo feel real.

So what does the token route actually do? Let me show you the same logic in Python, because it's short, and you'll need it if your backend isn't Next.js.

[CODE: equivalent token minting in Python with `livekit-api` (illustration; not a file in the repo)]
```python
import os
import uuid

from livekit import api


def create_token_for_riley() -> tuple[str, str]:
    room_name = f"maple-web-{uuid.uuid4().hex[:8]}"
    token = (
        api.AccessToken(os.environ["LIVEKIT_API_KEY"], os.environ["LIVEKIT_API_SECRET"])
        .with_identity(f"web-caller-{uuid.uuid4().hex[:6]}")
        .with_name("Web caller")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .with_room_config(
            api.RoomConfiguration(agents=[api.RoomAgentDispatch(agent_name="riley-receptionist")])
        )
    )
    return room_name, token.to_jwt()
```

Walk through it. A fresh room name for each visitor, so every conversation is private. A random identity. A grant that lets this person join only that one room. And the key line: a room configuration that dispatches `riley-receptionist` when the room is created. That's how Riley knows to join.

The token is signed with your secret, and it expires by default. The browser gets a token, never the secret.

[SCREEN: Terminal.]

Install and run.

```bash
pnpm install
pnpm dev
```

[SCREEN: Browser at `http://localhost:3000`. Click "Start call". Allow the microphone.]

Open localhost three thousand, and start a call.

[DEMO: Browser session with the deployed agent. Captions visible.]

**Riley:** Thanks for calling Maple Street Dental. This is Riley, the clinic's AI assistant. How can I help you today?

**You:** Do you take Delta Dental?

**Riley:** Yes, we're in network with Delta Dental. Would you like to book an appointment?

**You:** Not today, thanks.

**Riley:** No problem. Thanks for calling Maple Street Dental. Have a great day.

[SCREEN: Point at the live captions, then at `lk agent logs` in a second terminal showing the new job.]

Captions show both sides. They come from the transcription stream. And in the agent logs, there's the new job from a web room, served by the deployed agent.

Notice one difference from the phone. On the web, there's no SIP participant, so there's no caller ID, and `transfer_to_human` can't transfer. It tells Riley to apologise and offer to take a message instead. That's the graceful fallback from Section 8, and it's exactly what a web caller should hear.

[SLIDE 2: Before you put this on a real website]
- Rate-limit the token route (per IP and per day)
- Add bot protection if the page is public
- Set a maximum call length in the agent
- Deploy the front end (any Next.js host) with secrets in its environment

[AVATAR]
Before this goes on a real clinic website, a few guardrails. Anyone who can load the page can start a call, and every call costs money. So rate-limit the token route. Add bot protection if it's public. Keep a maximum call length in the agent. And deploy the Next.js app to any host that supports it, with the secrets in the host's environment.

**Recap:** The React starter plus a server-side token route that dispatches `riley-receptionist` puts your deployed agent in any browser, without exposing your API secret.

**Transition:** Next, the production readiness checklist, so you know Riley is ready before real callers arrive.

### Speaker notes: common student mistakes / Q&A

- "The UI connects but Riley never joins." The agent name in the front end doesn't match `LIVEKIT_AGENT_NAME`, or the agent isn't deployed. Check `lk agent status` and the `/worker` output for the name.
- Mistake: minting tokens in the browser with the secret in a `NEXT_PUBLIC_` variable. Rotate the secret immediately if this happened.
- Mistake: reusing one room name for everyone. Visitors end up in each other's calls. Generate a room per session.
- Browser mic permissions need HTTPS on real domains. `localhost` is the only exception.

---

## Lecture 12.6 — Production readiness checklist

| Field | Value |
|---|---|
| ID | 12.6 |
| Type | SL (slides + avatar) |
| Target duration | 6:00 (~630 spoken words) |
| Learning objectives | 1. Apply a production readiness checklist covering resilience, observability, security, operations and compliance. 2. Define what Riley says and does when a provider fails. 3. Write the first page of an on-call runbook. |
| Prerequisites | Sections 9 to 11; 12.1 to 12.5 |
| Files used | `10-resources/production-checklist.md`, `src/maple/prompts.py` (`ERROR_SPEECH`) |

### Script

[AVATAR]
Here's a scenario. It's Tuesday at ten A M. Your TTS provider has an outage. Riley can hear callers, understand them, and even book appointments. But it can't speak. Callers hear silence, and hang up.

Was that avoidable? Mostly, yes. This lecture is the checklist that catches it, and about twenty other things, before real callers find them.

[SLIDE 1: Five areas]
1. Resilience
2. Observability
3. Security and privacy
4. Operations
5. Compliance

The full checklist is in `10-resources/production-checklist.md`. It has five areas. Let's walk through the items that matter most in each.

[SLIDE 2: Resilience]
- Fallback models for STT, LLM and TTS
- Timeouts and retries on every provider (`conn_options`)
- Spoken error recovery: a pre-written line and a transfer
- Graceful degradation: if booking is down, take a message
- Maximum call length and silence handling

Resilience first. Every provider fails eventually. So each of the three models needs a fallback. A second LLM. A second STT. A second TTS. We'll wire those up in the capstone, Lecture 13.3.

Every provider call needs a timeout. The defaults in LiveKit are three retries, two seconds apart, with a ten-second timeout. That's reasonable for a web app. On a phone call, three retries two seconds apart is six seconds of silence. Choose them on purpose, against your latency budget.

When something breaks mid-call, Riley needs a line to say. It's already in our prompts module. "Sorry, I'm having a technical problem on my end. Let me connect you with someone at the front desk." Pre-written, tested, and it ends in a transfer, not a dead end.

And graceful degradation. If the booking system is down, Riley shouldn't pretend. It should take a message and promise a callback. A limited Riley is much better than a silent one.

[SLIDE 3: Observability]
- Metrics exported: latency (p50/p95), cost per minute, tool errors
- Traces for every call, with PII redaction
- Alerts: p95 latency, error rate, transfer rate, spend
- Call outcomes recorded: booked, transferred, abandoned

Observability. You built all of this in Section 10. The checklist question is simply: is it turned on in production? Metrics exported. Traces flowing. PII redacted. And alerts on p95 latency, error rate, transfer rate and spend. An alert nobody receives doesn't count, so check it routes to a person.

And record every call's outcome: booked, rescheduled, transferred, abandoned, error. The capstone stores this in `CallState` as `call_outcome`. Outcomes are how you'll answer the clinic's real question, which isn't "how fast is it?" but "is it actually handling our calls?"

[SLIDE 4: Security and privacy]
- Secrets only in the platform's secret store; rotation plan
- `verify_caller` required before revealing or changing appointments
- Transfer target fixed in config; international dialing off on the trunk
- Safety tests (Section 11) passing in CI
- Retention settings applied at every provider

Security and privacy. This is Section 11 as a checklist. Secrets in a secret store, with a plan to rotate them. Verification before any appointment is revealed or changed. A fixed transfer target, and international dialing disabled on the trunk. Safety tests passing in CI. And retention settings applied at every provider, not just in your own logs.

[SLIDE 5: Operations]
- Pinned dependency versions and a lock file
- Tested rollback (you've actually run it)
- Draining verified (grace period ≥ `drain_timeout`)
- Load tested at 2× expected peak
- An on-call runbook

Operations. Pin versions, and keep the lock file. Voice libraries release often, and an unplanned upgrade on a Friday is how outages start. Rollback: tested, meaning you've actually run it, not just read about it. Draining: verified with a real call during a deploy. Load: tested at twice your expected peak, with simulated callers in parallel, while you watch the load number on `/worker`. And a runbook.

[SLIDE 6: Runbook, page one]
| Symptom | First check | First action |
|---|---|---|
| Riley silent | TTS provider status, error logs | Roll back or switch TTS fallback |
| Slow replies | p95 by stage (EOU, LLM TTFT, TTS TTFB) | Switch LLM to fallback, check region |
| Not answering calls | `lk agent status`, `/worker`, dispatch rule | Roll back last deploy |
| Wrong bookings | Tool-call traces, scheduler logs | Disable booking tool, take messages |
| Cost spike | Cost per minute, call counts, call length | Check for loops or abuse, rate-limit |

Here's page one of Riley's runbook. Five symptoms. For each, the first thing to check, and the first thing to do.

Notice every first action is fast and reversible. Roll back. Switch to a fallback. Disable a tool. The runbook is for three A M, when nobody should be debugging. Stabilise first. Investigate in the morning.

[SLIDE 7: Compliance]
- AI disclosure in the greeting
- Recording consent where required
- Outbound calling rules (consent, calling hours, do-not-call)
- Data processing agreements with providers
- Not legal advice: involve your compliance owner

And compliance, from Lecture 8.6. AI disclosure in the greeting. Riley does this. Recording consent where your jurisdiction requires it. Outbound rules if you make reminder calls. And agreements with your providers covering the data they process. This is engineering guidance, not legal advice. Every real deployment needs someone who owns compliance.

[AVATAR]
Back to Tuesday at ten. With this checklist done, here's what happens instead. The TTS provider fails. The fallback TTS takes over within a turn or two. The error rate alert fires. You check the runbook, see the provider status page, and do nothing, because the system already handled it. That's what production-ready means. Not that nothing breaks. That breaking is boring.

**Recap:** Production-ready means fallbacks and spoken recovery, observability with alerts, Section 11 security in CI, tested rollbacks and draining, a runbook, and compliance owned by someone.

**Transition:** Now it's your turn: in Lab 7, you'll deploy Riley and call it from the web and a phone.

### Speaker notes: common student mistakes / Q&A

- Mistake: fallbacks configured but never tested. Test each one by setting an invalid key for the primary provider in a staging deploy.
- Mistake: a runbook that says "investigate". The first action must be concrete, fast and reversible.
- "What's a good p95 target?" Revisit your budget from Lecture 1.4 and the measurements from 9.8. Use your own numbers, not someone else's.
- Load tests cost real API money. Run them in short bursts and cap spend with provider limits.

---

## Lecture 12.7 — Lab 7: Deploy and call your agent

| Field | Value |
|---|---|
| ID | 12.7 |
| Type | LAB (text lab with short video walkthrough) |
| Target duration | 4:00 video (~320 spoken words); lab itself ~45-60 minutes |
| Learning objectives | 1. Deploy your own agent to LiveKit Cloud and reach it from the web front end. 2. Point your Section 8 phone number at the deployed agent. 3. Prove draining and rollback work, and record evidence. |
| Prerequisites | 12.2, 12.3, 12.5; Section 8 phone number (optional but recommended) |
| Files used | `04-labs/lab-07-deploy.md`, `deploy/Dockerfile`, `livekit.toml`, `frontend/README.md` |

### Script

[AVATAR]
Time to do it yourself. This lab takes most people forty-five minutes to an hour. By the end, your Riley will be live in the cloud, reachable from a browser and from a phone.

[SLIDE 1: Lab 7 steps]
1. Build and run the image locally; `curl :8081/` returns OK
2. `lk agent create`, then one test call in the playground
3. Run the web starter with agent name `riley-receptionist`
4. Call your Section 8 number: the dispatch rule reaches the deployed agent
5. Change the greeting, `lk agent deploy`, then `lk agent rollback`
6. Stop a container mid-call and confirm the call continues

Six steps. Let me show you the two that trip people up.

[SCREEN: Terminal. Local dev agent running in one pane, deployed agent in the cloud.]

The first one is step four, the phone number. In Section 8, your dispatch rule sent calls to the agent name. If your laptop is still running `dev` with the same agent name, calls might go to your laptop instead of the cloud. Both are registered, and LiveKit picks one.

So stop your local agent before testing the phone, or give it a different name in your local `.env`, like `riley-dev`. Remember, `LIVEKIT_AGENT_NAME` is read in every mode, while `livekit.toml` is only read by `start`. Then check the logs.

```bash
lk agent logs
```

[SCREEN: Logs show a job from a SIP participant, with the caller number redacted.]

There's the phone call, handled in the cloud, with the caller's number redacted.

The second tricky step is six, draining. With LiveKit Cloud, a new deploy is the easiest way to see it. Start a call, run `lk agent deploy`, and keep talking. Your call should continue on the old version while the new one rolls out. Then make a new call, and you should hear the new greeting.

[SLIDE 2: What to submit]
- `lk agent status` output showing your agent running
- A screenshot of a web call with captions
- The log line of a phone call handled by the deployed agent
- One sentence: what happened to your call during the deploy

[AVATAR]
For evidence, collect four things. Status output. A screenshot of a web call. The log line from a phone call. And one sentence describing what happened to your call during the deploy.

If you don't have a phone number, because a Twilio trial isn't available where you live, do steps one to three and five to six, and note it in your submission. The web path proves the deployment. The phone path proves the dispatch rule.

If you get stuck, the lab file has a troubleshooting table. The most common fix is the agent name. Check it in `livekit.toml`, the secrets file, the front end config and the dispatch rule. All four have to match.

**Recap:** In Lab 7, you deploy Riley, reach it by web and phone, and prove that deploys and rollbacks don't drop calls.

**Transition:** Next, the chaos demo: we'll take down a provider in the middle of a live call and watch what happens.

### Speaker notes: common student mistakes / Q&A

- Most common failure: agent name mismatch across `livekit.toml`, secrets, front end and SIP dispatch rule.
- Second most common: a local `dev` agent with the same name stealing calls. Stop it, or use a different `LIVEKIT_AGENT_NAME` locally, like `riley-dev`.
- Students on a Twilio trial can only call verified numbers. That's a trial limit, not a bug.
- If the cloud build fails at the `uv sync` step, the lock file is probably out of date. Run `uv lock` locally and commit `uv.lock`.
- Local testing before deploying: `make console AGENT=...` needs PortAudio for your mic and speakers. If it fails with an audio device error, install PortAudio or use `make console-text`. See `10-resources/troubleshooting.md`.

---

## Lecture 12.8 — Chaos demo: kill a provider mid-call

| Field | Value |
|---|---|
| ID | 12.8 |
| Type | DM (live demo) |
| Target duration | 5:00 (~490 spoken words; the rest is screen, typing and demo time) |
| Learning objectives | 1. Watch the capstone's LLM `FallbackAdapter` take over when the primary provider fails mid-call. 2. See spoken error recovery when there is no fallback. 3. Explain why a silent TTS failure is the worst case, and how the capstone guards against it. |
| Prerequisites | 12.6 (production checklist); read the `build_resilient_models` function in `agents/s13_capstone_receptionist.py` |
| Files used | `agents/s13_capstone_receptionist.py`, `agents/s12_chaos_demo.py` (recording helper, shown below) |

> **Recording notes.**
> - Run in `MAPLE_PROVIDER_MODE=inference` (the default). In that mode STT and TTS fall back server side in LiveKit Inference, and the LLM falls back client side through `llm.FallbackAdapter`.
> - You can't revoke LiveKit Inference keys per provider mid-call, so Part A and B use a kill switch: `agents/s12_chaos_demo.py` wraps the capstone's primary LLM and fails every request while `/tmp/riley-kill-llm` exists. It changes nothing in the capstone. **Add this file to `03-code/agents/` before publishing** so students can repeat the demo.
> - Part C (real key revocation) is optional B-roll: in `MAPLE_PROVIDER_MODE=plugins`, the capstone has no fallbacks. Create a throwaway Cartesia key for the recording, delete it mid-call, then rotate.

### Script

[AVATAR]
In Lecture 12.6, I promised that production-ready means breaking is boring. Let's test that promise. We're going to take down a provider in the middle of a live call. Once with fallbacks. Once without. And you'll hear the difference.

[SCREEN: `agents/s13_capstone_receptionist.py`, `build_resilient_models`. Footer: "APIs verified on livekit-agents 1.8 / pipecat-ai 1.12; check the repo README for updates."]

Quick reminder of what the capstone does. Speech-to-text and text-to-speech use LiveKit Inference's server-side fallback. The LLM uses `llm.FallbackAdapter`, with our primary model first and a fallback model second, and a five-second attempt timeout.

To break things on demand, I use a small helper. It doesn't change the capstone at all.

[CODE: `agents/s12_chaos_demo.py`]
```python
"""Chaos demo (lecture 12.8): take the primary LLM down mid-call and watch the fallback.

Recording helper that wraps the capstone without changing it.

    uv run python agents/s12_chaos_demo.py dev                         # with fallback
    CHAOS_NO_FALLBACK=1 uv run python agents/s12_chaos_demo.py dev     # without fallback

Mid-call, in another terminal:

    touch /tmp/riley-kill-llm      # primary LLM starts failing
    rm /tmp/riley-kill-llm         # primary LLM recovers

Needs MAPLE_PROVIDER_MODE=inference (the default).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import s13_capstone_receptionist as capstone
from common import prewarm
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    AgentServer,
    APIConnectionError,
    APIConnectOptions,
    JobContext,
    cli,
    inference,
    llm,
)
from livekit.agents.types import NOT_GIVEN, NotGivenOr

from maple.config import Settings

KILL_FILE = Path("/tmp/riley-kill-llm")


class _FailingStream(llm.LLMStream):
    async def _run(self) -> None:
        raise APIConnectionError("chaos: primary LLM is down")


class ChaosLLM(llm.LLM):
    """Wraps a real LLM and fails every request while the kill file exists."""

    def __init__(self, inner: llm.LLM) -> None:
        super().__init__()
        self._inner = inner

    @property
    def model(self) -> str:
        return self._inner.model

    @property
    def provider(self) -> str:
        return self._inner.provider

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[Any] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[Any] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> llm.LLMStream:
        if KILL_FILE.exists():
            return _FailingStream(self, chat_ctx=chat_ctx, tools=tools or [], conn_options=conn_options)
        return self._inner.chat(
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
            parallel_tool_calls=parallel_tool_calls,
            tool_choice=tool_choice,
            extra_kwargs=extra_kwargs,
        )


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Run the capstone entrypoint with a killable primary LLM (patched inside the job process)."""
    build_original = capstone.build_resilient_models

    def build_with_chaos(settings: Settings) -> dict[str, Any]:
        models = build_original(settings)
        primary = ChaosLLM(inference.LLM(settings.llm_model))
        if os.getenv("CHAOS_NO_FALLBACK") == "1":
            models["llm"] = primary
        else:
            models["llm"] = llm.FallbackAdapter(
                [primary, inference.LLM(settings.fallback_llm_model)], attempt_timeout=5.0
            )
        return models

    capstone.build_resilient_models = build_with_chaos
    await capstone.entrypoint(ctx)


if __name__ == "__main__":
    cli.run_app(server)
```

`ChaosLLM` wraps a real LLM. While a file called `/tmp/riley-kill-llm` exists, every request fails with a connection error, exactly like a provider outage. Delete the file, and it works again. The entrypoint swaps this killable LLM into the capstone's models, inside the job process, and then runs the normal capstone entrypoint. Set `CHAOS_NO_FALLBACK` and there's no backup at all.

**Part A: with fallbacks.**

[SCREEN: Split screen. Left: Agents Playground connected to the agent. Right top: terminal running the agent. Right bottom: a second terminal for the kill switch.]

```bash
uv run python agents/s12_chaos_demo.py dev
```

[DEMO: Live call.]

**You:** Hi, what time do you open tomorrow?

**Riley:** We open at eight tomorrow morning. Would you like to book an appointment?

Normal. Now, kill the primary LLM.

```bash
touch /tmp/riley-kill-llm
```

**You:** Yes, a cleaning tomorrow afternoon, please.

**Riley:** One moment while I check the schedule. I have one o'clock, one thirty or two o'clock tomorrow afternoon. Which works best?

[SCREEN: Highlight the agent log: `ChaosLLM failed, switching to next LLM: chaos: primary LLM is down`.]

Did you hear anything wrong? I didn't. But look at the log. "Failed, switching to next LLM." The primary died, the adapter switched to the fallback model, and the caller got a normal answer. The only cost was a short extra pause on that one turn.

Now bring the primary back.

```bash
rm /tmp/riley-kill-llm
```

[SCREEN: Log line: `llm.FallbackAdapter, ... recovered`.]

The adapter keeps checking the failed provider in the background. When it recovers, it switches back. No restart, no deploy.

**Part B: without fallbacks.**

```bash
CHAOS_NO_FALLBACK=1 uv run python agents/s12_chaos_demo.py dev
```

Same call, but this time there's nothing to fall back to.

```bash
touch /tmp/riley-kill-llm
```

**You:** Can I book a cleaning tomorrow afternoon?

[PAUSE]

**Riley:** Sorry, I'm having a technical problem on my end. Let me connect you with someone at the front desk.

[SCREEN: Log shows the LLM retrying, then an unrecoverable LLM error, then the error speech.]

A pause while the session retries. Then the pre-written error line from `prompts.py`. That's the capstone's `error` handler: when an error is unrecoverable, it speaks `ERROR_SPEECH`, without the LLM. It's not graceful, but the caller isn't left in silence.

[B-ROLL: Part C clip, 20 seconds. Plugins mode, no fallbacks. The Cartesia key is deleted in the provider dashboard mid-call. The caller asks a question. Silence. The caller says "Hello? Hello?" and hangs up. Log shows repeated TTS errors.]

**Part C: the worst case.**

[AVATAR]
And here's the nightmare from Lecture 12.6. This clip is plugins mode, with no fallbacks, and I deleted the TTS key mid-call. Riley still hears the caller. It still thinks. It even tries to say the error line. But it has no voice. Silence, then a hang-up.

That's why TTS gets a fallback before anything else. An agent that can't think can still apologise. An agent that can't speak can't do anything.

[SLIDE 1: What the chaos demo proves]
| Failure | With fallbacks | Without |
|---|---|---|
| LLM down | Fallback model answers; brief pause | Error line spoken |
| TTS down | Backup voice speaks | Silence |
| Recovery | Automatic, no redeploy | Restart needed |

Here's the summary. With fallbacks, an LLM outage costs one slow turn. Without them, it costs the call. And a TTS outage without a fallback is silence.

Run this drill on your own agent before every major release. It takes five minutes, and it's the only way to know your fallbacks actually work.

**Recap:** Kill a provider on purpose: with fallbacks the call continues, without them you get an error line at best and silence at worst.

**Transition:** Lock in the deployment section with a five-question quiz.

### Speaker notes: common student mistakes / Q&A

- "The fallback took five seconds." That's `attempt_timeout=5.0` on a provider that hangs instead of failing fast. A hard failure, like our kill switch, switches almost immediately. Tune the timeout to your latency budget.
- The fallback voice sounds different from the primary. Pick a fallback voice that's close, and tell the clinic in advance.
- In the capstone, `ERROR_SPEECH` promises a transfer, but the `error` handler only speaks the line. A good extension is to call the same transfer helper used by `transfer_to_human` after the line finishes.
- Students on `MAPLE_PROVIDER_MODE=plugins` won't get STT or TTS fallbacks from the capstone. They can wrap their plugin instances in `stt.FallbackAdapter` and `tts.FallbackAdapter` themselves.

---

## Lecture 12.9 — Quiz: Deployment

| Field | Value |
|---|---|
| ID | 12.9 |
| Type | QZ (quiz with short video intro) |
| Target duration | 2:00 total (0:45 video intro, ~70 spoken words; the rest is quiz time) |
| Learning objectives | 1. Check understanding of agent server scaling, Docker packaging, draining and fallbacks. 2. Identify any Section 12 lecture to rewatch before the capstone. |
| Prerequisites | 12.1 to 12.8 |
| Files used | `06-assessments/quizzes/section-12.md` |

### Script

[AVATAR]
Five quick questions before the capstone.

[SLIDE 1: Section 12 quiz: what's covered]
- Idle processes, load threshold and memory limits
- Why `exec` and `start` matter in the Dockerfile
- Draining and the platform grace period
- Fallbacks and spoken error recovery

You'll see questions on the agent server settings, the Dockerfile's start command, draining, and what you saw in the chaos demo.

One tip. If a question asks why calls dropped during a deploy, there are two usual suspects. The signal never reached Python, or the platform killed the container before the drain finished.

[PAUSE]

Read the explanations for anything you miss.

**Recap:** The quiz checks scaling, packaging, draining and fallbacks before you assemble the capstone.

**Transition:** Next up, Section 13: the capstone, starting with the brief and the architecture.

### Speaker notes: common student mistakes / Q&A

- Most missed in beta: the production default for `load_threshold` (0.7) versus dev (disabled). Point to Lecture 12.1, slide 7.
- Second most missed: thinking LiveKit Cloud needs `LIVEKIT_API_KEY` in the secrets file. It injects it. Point to Lecture 12.3.
- "Can I retake it?" Yes, as many times as you like.
