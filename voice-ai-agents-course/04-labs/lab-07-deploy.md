# Lab 7: Deploy and Call Your Agent

| Field | Details |
|---|---|
| **Section / lecture** | Section 12, lecture 12.7 |
| **Time estimate** | 90 minutes |
| **Difficulty** | Intermediate to advanced |
| **Goal** | Package Riley as a production Docker image, run it locally in production mode, deploy it to LiveKit Cloud with secrets, and reach the deployed agent from a web client and from a phone (or the Project 2 "no phone number" path). Then practise the operations you will need on a bad day: logs, status and rollback. |
| **You will produce** | A running LiveKit Cloud agent, `livekit.toml`, a filled production-readiness checklist and `notes/lab-07.md` with evidence |

---

## Prerequisites

- Lectures 12.1 to 12.6 watched.
- Docker Desktop (or Docker Engine) installed: `docker --version` prints a version.
- LiveKit CLI logged in (Lab 1) and, for the phone path, the inbound trunk and dispatch rule from Project 2.
- `make test` green. Never deploy a red build.

---

## Step 1: Read the Dockerfile before you build it

Open `deploy/Dockerfile` and find the four production choices from lecture 12.2:

| Choice | What to look for | Why |
|---|---|---|
| Multi-stage build | A builder stage that installs dependencies, and a slim final stage that copies the virtual environment | Smaller image, faster scaling |
| Models at build time | A `RUN ... download-files` line | New containers start without downloading VAD and turn-detector weights |
| Non-root user | A `USER` line with a non-root account | Limits damage if the process is compromised |
| Production command | The final `CMD` ends with `start` (not `dev` or `console`) | Production mode: no hot reload, production logging |

Note which agent file the image starts: `ARG AGENT_FILE=agents/s13_capstone_receptionist.py` feeds both the `download-files` step and the final `CMD ["sh", "-c", "exec python \"$AGENT_FILE\" start"]`. To deploy your own Project 2 or capstone agent, pass `--build-arg AGENT_FILE=agents/capstone_riley.py` instead of editing the file.

> **Checkpoint 1:** you can point to each of the four choices in the file.

---

## Step 2: Build and run the image locally

```bash
cp deploy/.dockerignore .dockerignore     # Docker only reads .dockerignore at the build-context root
docker build -f deploy/Dockerfile -t riley-agent:local .
```

(`make docker-build` runs the same two commands and tags the image `riley-agent`.) Expected: the build finishes with `naming to docker.io/library/riley-agent:local`. The `download-files` step prints model downloads the first time and is cached afterwards.

Create a production env file. It is the same as `.env` **minus** development-only settings:

```bash
grep -v -E '^(MAPLE_TODAY|MOCK_MODE|MAPLE_SIMULATED_LATENCY)=' .env > .env.production
```

`MAPLE_TODAY` in production would freeze the clinic calendar on one date, so it must never be deployed. Make sure `.env.production` is git-ignored (`git check-ignore .env.production`).

Run it in production mode, exposing the health port:

```bash
docker run --rm --name riley --env-file .env.production -p 8081:8081 riley-agent:local
```

In a second terminal:

```bash
curl -s http://localhost:8081/ ; echo
docker exec riley whoami
```

Expected: the health endpoint answers with HTTP 200, and `whoami` prints `riley` (the image's non-root user), not `root`. The container log shows the agent server registering with LiveKit (a "registered worker" line with your agent name).

Now talk to the container from the browser, exactly as in Project 2's web path (Agents Playground, the React starter in `frontend/README.md`, or an explicit dispatch plus token). Book an appointment to prove the image works end to end, then stop the container with `Ctrl+C`.

> **Checkpoint 2:** a booking succeeded against the local container, and the health check returned 200.

---

## Step 3: Deploy to LiveKit Cloud

LiveKit Cloud builds your image from a `Dockerfile` in the directory you deploy from. Copy the deploy files to the repo root (skip this if the repo README says a root copy already exists):

```bash
cp deploy/Dockerfile Dockerfile
cp deploy/.dockerignore .dockerignore
```

Create the agent with your production secrets. LiveKit Cloud injects `LIVEKIT_URL`, `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET` automatically, so remove them from the secrets you upload, and make sure the agent name your dispatch rule uses is set:

```bash
grep -v -E '^LIVEKIT_(URL|API_KEY|API_SECRET)=' .env.production > .env.cloud
grep -q '^LIVEKIT_AGENT_NAME=' .env.cloud || echo 'LIVEKIT_AGENT_NAME=riley-receptionist' >> .env.cloud
lk agent create --secrets-file .env.cloud
```

The root `Dockerfile` still starts `agents/s13_capstone_receptionist.py`; to deploy your own agent, change the `ARG AGENT_FILE=` default in that root copy before running the command. The CLI builds the image remotely, deploys it, and writes a `livekit.toml` with your agent's ID. Commit `livekit.toml` (it contains no secrets); do not commit `.env.cloud`.

Check it:

```bash
lk agent status
lk agent logs
```

Expected: status shows the agent running with at least one instance, and the logs show the worker registering with the agent name `riley-receptionist` (from `LIVEKIT_AGENT_NAME`; `start` falls back to the `[agent] name` in `livekit.toml` when the variable is unset, see `livekit.toml.example`).

**Important:** stop any local `dev` or Docker copy of Riley now. Two agent servers registered with the same name share the calls between them, which makes debugging very confusing.

> **Checkpoint 3:** `lk agent status` shows a running deployment, and nothing else is registered under your agent name.

---

## Step 4: Call the deployed agent from the web

Use the React agent starter from `frontend/README.md` (lecture 12.5), configured with your LiveKit project URL and the agent name `riley-receptionist`, or the manual route:

```bash
lk dispatch create --new-room --agent-name riley-receptionist
lk token create --join --room <room-name-from-previous-output> --identity web-tester --valid-for 1h
```

Join the room with the token (Agents Playground or LiveKit Meet, pointed at your project URL). Riley should greet you within about two seconds. Book an appointment and ask one FAQ question.

While you talk, run `lk agent logs` in another terminal and watch the turns arrive.

> **Checkpoint 4:** a web booking succeeded against the **cloud** deployment (confirm in `lk agent logs`, not your local terminal).

---

## Step 5: Call the deployed agent by phone

**Path A (phone number):** your Project 2 dispatch rule already names `riley-receptionist`, so nothing changes on the SIP side. Call your Twilio number. Ask to book, then ask for a person to test `transfer_to_human` (make sure `TRANSFER_PHONE_NUMBER` is in the uploaded secrets).

**Path B (no phone number):** call `+15550100` from your softphone as in Project 2, and verify the graceful "take a message" fallback when you ask for a person.

Record in `notes/lab-07.md`: time from pickup to greeting, whether the caller ID was offered back, and the outcome.

> **Checkpoint 5:** a phone (or softphone) call to the deployed agent completed a booking.

---

## Step 6: Practise a bad day: update, logs and rollback

1. Make a harmless, audible change: in your agent's greeting, add "You're speaking with the new Riley." Commit it.
2. Deploy the change:

```bash
lk agent deploy
lk agent status
```

3. Call once to hear the new greeting.
4. Pretend the release is broken and roll back:

```bash
lk agent rollback
lk agent status
```

5. Call again and confirm the old greeting is back. Note how long the rollback took from command to working call.
6. Rotate a secret without a code change (for example, set `TRANSFER_PHONE_NUMBER` to a different number):

```bash
lk agent update-secrets --secrets-file .env.cloud
```

> **Checkpoint 6:** you performed a deploy, a rollback and a secret update, and recorded the rollback time.

---

## Step 7: Production-readiness checklist

Copy into `notes/lab-07.md` and tick only what you have evidence for (lecture 12.6):

| # | Item | Evidence |
|---|---|---|
| 1 | Image runs as non-root | `docker exec ... whoami` output |
| 2 | Models downloaded at build time | Dockerfile line |
| 3 | Production `start` command | Dockerfile `CMD` |
| 4 | Health check responds | `curl` output |
| 5 | No dev-only env vars in production (`MAPLE_TODAY`, `MOCK_MODE`, `MAPLE_SIMULATED_LATENCY`) | `.env.cloud` reviewed |
| 6 | Secrets only in the secret store, never in the image or repo | `git check-ignore`, `docker history` shows no `.env` |
| 7 | Fallback models configured (`FALLBACK_LLM_MODEL`, `FALLBACK_STT_MODEL`, `FALLBACK_TTS_MODEL`) | Secrets or defaults |
| 8 | Spoken error recovery path exists (`prompts.ERROR_SPEECH`) | Code reference |
| 9 | Prewarm configured (`AgentServer(setup_fnc=prewarm)`) | Code reference |
| 10 | Rollback tested, with time recorded | Step 6 |
| 11 | Logs reachable (`lk agent logs`) and metrics exported | Step 3 / Lab 6 |
| 12 | Only one agent server registered per agent name per environment | Step 3 |
| 13 | On-call runbook has "how to roll back" and "how to disable phone routing" | `10-resources/production-checklist.md` |

---

## Stretch goal

Run the chaos drill from lecture 12.8 on the **local container** (never on a line real callers use): start `riley-agent:local` with a deliberately broken primary TTS (for example `TTS_MODEL=cartesia/not-a-real-model` in a copy of `.env.production`), place a web call, and record what the caller hears. With fallbacks configured you should hear the fallback voice (from `FALLBACK_TTS_MODEL`) or Riley's spoken error message and a transfer offer, not silence. Then write two lines for your runbook: how you would detect this in production (which metric or log line) and what you would do first.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `docker build` fails at `download-files` | No network in the build, or a proxy blocks the model host | Build on another network, or configure Docker's proxy settings |
| Container exits immediately with an auth error | `.env.production` missing `LIVEKIT_*` for the local run | Local runs need `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`; only the cloud secrets file drops them |
| `curl localhost:8081` fails | Port not published, or a different health port configured in your release | Keep `-p 8081:8081`; check the container log for the port the health server bound to |
| `lk agent create` cannot find a Dockerfile | Dockerfile only in `deploy/` | Copy it to the directory you deploy from (Step 3) |
| Cloud agent runs but never gets calls | Local `dev` agent still registered with the same name and taking the calls, or agent name mismatch | Stop local agents; compare `lk agent logs` agent name with the dispatch rule (`lk sip dispatch list`) |
| Calendar shows the same "today" every day | `MAPLE_TODAY` was uploaded as a secret | Remove it and `lk agent update-secrets` |
| Transfer fails only in the cloud | `TRANSFER_PHONE_NUMBER` not in the uploaded secrets | Add it to `.env.cloud` and update secrets |
| Rollback seems to do nothing | Calls still reaching a local agent | Same as "never gets calls": stop local agents |
| Image is several GB | Single-stage build or dev dependencies in the final stage | Use the multi-stage `deploy/Dockerfile`; check `.dockerignore` excludes `.venv`, `metrics/`, `.git` |

---

## Solution notes

- A good submission shows: a non-root, multi-stage image with models baked in and a `start` command; a successful local booking; a cloud deployment verified through `lk agent logs`; a web and a phone (or Path B) call; a deploy, rollback and secret update; and a checklist where every tick has evidence.
- Typical numbers from the course's runs: image around 1 to 2 GB (most of it is the turn-detector and VAD weights plus Python dependencies), greeting within 1.5 to 2.5 seconds of pickup when prewarmed idle processes are available, and a rollback that restores the previous version within a couple of minutes.
- The two mistakes that cost students the most time in beta testing were a local `dev` agent still registered under the same name (calls randomly went to the laptop) and `MAPLE_TODAY` uploaded as a production secret (the calendar never moved).
- Self-hosting instead of LiveKit Cloud (lecture 12.4) is equally valid: run the same image on Render, Fly.io, ECS or Kubernetes with the three `LIVEKIT_*` variables, no inbound ports except the health check, and autoscaling on load.

Reference files: `03-code/deploy/Dockerfile`, `03-code/deploy/.dockerignore`, `03-code/livekit.toml.example`, `03-code/frontend/README.md`, `03-code/agents/s13_capstone_receptionist.py`, `10-resources/production-checklist.md`.
