# Quiz: Deployment (Section 12)

| Field | Value |
|---|---|
| Udemy lecture | 12.9 Quiz: Deployment |
| Questions | 5 |
| Format | Multiple choice, 4 options, 1 correct; every option has its own explanation (paste each into Udemy's per-answer "Explanation" field) |
| Covers | Lectures 12.1 to 12.4, 12.6, 12.8 |

---

### Q1. The first call after each deploy has a noticeably slow start, while later calls are fine. Profiling shows the Silero VAD model loading inside the entrypoint. What is the fix?

*Related lecture: 12.1 Agent server architecture and scaling*

- **A.** Load the VAD in a prewarm function passed as `AgentServer(setup_fnc=prewarm)`, store it in `proc.userdata`, and reuse it in the entrypoint.
  - *Explanation:* Correct. Prewarm runs when a job process starts, before a call is assigned. Combined with idle processes, callers never wait for model loading. The course's `prewarm()` and `load_vad()` helpers in `agents/common.py` do exactly this.
- **B.** Load the VAD at the end of each call so it is ready for the next.
  - *Explanation:* Incorrect. Each job runs in a process that may not handle the next call, and loading at the end delays shutdown.
- **C.** Remove VAD to save load time.
  - *Explanation:* Incorrect. VAD is needed for turn-taking and interruptions.
- **D.** Increase the container's CPU so loading is faster.
  - *Explanation:* Incorrect. It may help a little but still puts load time in the caller's path. Prewarming removes it.

**Correct answer: A**

---

### Q2. During a busy Monday morning, some calls wait several seconds before Riley joins, even though CPU is only at 50% on each container. Which settings are most relevant?

*Related lecture: 12.1 Agent server architecture and scaling*

- **A.** `max_tool_steps` and `user_away_timeout`.
  - *Explanation:* Incorrect. These control in-call behaviour, not how quickly a call is picked up.
- **B.** `num_idle_processes` (how many warm processes wait for new jobs) and `load_threshold` (the load at which a server stops accepting jobs), together with autoscaling on load.
  - *Explanation:* Correct. If there are not enough warm processes, new jobs wait for a process to start and prewarm. Tuning idle processes and the load threshold, and scaling out before servers saturate, removes the join delay.
- **C.** `MIN_ENDPOINTING_DELAY` and `MAX_ENDPOINTING_DELAY`.
  - *Explanation:* Incorrect. Endpointing affects turn-taking during the call, not how long a new call waits for an agent.
- **D.** The TTS voice and speaking rate.
  - *Explanation:* Incorrect. TTS only starts after the agent has joined.

**Correct answer: B**

---

### Q3. Which Dockerfile choice from lecture 12.2 is correct for a production Riley image?

*Related lecture: 12.2 Dockerising the agent*

- **A.** Run `download-files` when each container starts, so the image stays small.
  - *Explanation:* Incorrect. Downloading models at start-up slows scaling, and it fails if the model host is unreachable.
- **B.** Run the agent as root with the `dev` command so hot reload works in production.
  - *Explanation:* Incorrect. `dev` is for development (hot reload, verbose logging), and running as root widens the blast radius of any compromise.
- **C.** Copy `.env` into the image so secrets are always available.
  - *Explanation:* Incorrect. Secrets baked into an image leak to anyone who can pull it. Inject them at deploy time instead.
- **D.** Run `download-files` at build time, use a multi-stage build, run as a non-root user, and start with the `start` command.
  - *Explanation:* Correct. Models are baked into the image, the final image is lean, the process has minimal privileges, and `start` is the production mode.

**Correct answer: D**

---

### Q4. Your security team asks which inbound firewall ports must be opened so LiveKit Cloud can reach a self-hosted Riley agent on your Kubernetes cluster. What is the correct answer?

*Related lecture: 12.4 Self-hosting option*

- **A.** None for LiveKit itself: the agent server opens an outbound WebSocket connection to LiveKit and receives jobs over it. Only expose the health-check port to your own orchestrator.
  - *Explanation:* Correct. Agents dial out. This is why they can run on any container host behind NAT, and why the health endpoint is the only port your platform needs for liveness checks.
- **B.** Port 5060 for SIP.
  - *Explanation:* Incorrect. SIP terminates at LiveKit's SIP service, not at your agent.
- **C.** A UDP port range for WebRTC media.
  - *Explanation:* Incorrect. Media ports belong to the LiveKit server (the SFU). A self-hosted agent talking to LiveKit Cloud does not accept inbound media connections.
- **D.** Port 443 inbound so LiveKit can post webhooks to start calls.
  - *Explanation:* Incorrect. Jobs arrive over the agent's existing outbound connection, not by webhook.

**Correct answer: A**

---

### Q5. In the chaos demo, the TTS provider's key is revoked mid-call. With the course's production settings, what should the caller experience?

*Related lecture: 12.8 Chaos demo: kill a provider mid-call*

- **A.** Riley keeps "speaking", but the caller hears silence until they hang up.
  - *Explanation:* Incorrect. That is the failure mode without fallbacks, and the reason this demo exists.
- **B.** The call drops immediately with no explanation.
  - *Explanation:* Incorrect. Abrupt drops are what fallback providers and spoken error recovery are designed to prevent.
- **C.** The fallback TTS provider takes over (for example the configured `FALLBACK_TTS_MODEL`), possibly with a different voice, and if everything fails Riley recovers with error speech and a transfer or callback offer.
  - *Explanation:* Correct. Provider fallback lists and error speech (`prompts.ERROR_SPEECH`) turn an outage into a small voice change or a graceful hand-off instead of a dead line.
- **D.** Riley switches to reading the text in the caller's app.
  - *Explanation:* Incorrect. Phone callers have no text channel, and nothing in the course implements this.

**Correct answer: C**
