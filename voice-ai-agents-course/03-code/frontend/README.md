# A web front end for Riley (lecture 12.5)

Riley does not need a custom UI to be tested: `console` mode and the LiveKit Agents
Playground cover development. For a real website, use LiveKit's open-source
**React agent starter** (Next.js). It already contains a token server, microphone
handling, live transcripts and an audio visualiser.

## 1. Create the app

```bash
# with the LiveKit CLI (lecture 2.3)
lk app create --template agent-starter-react riley-web
cd riley-web
```

Or clone it from GitHub (`livekit-examples/agent-starter-react`).

## 2. Configure

Create `.env.local` in `riley-web/` with the **same project** your agent uses:

```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
```

`lk app env -w` writes this file for you. Keep the secret server side: the starter's
`/api/connection-details` route mints short-lived participant tokens, and the browser
never sees your API secret.

Branding: change the title, logo, accent colour and start button text ("Call Maple Street
Dental") in the starter's app config file (`app-config.ts` at the time of writing).

## 3. Named agents

- If Riley runs **without** `LIVEKIT_AGENT_NAME` (Sections 3-7), LiveKit dispatches it
  automatically to every new room, and the starter works as is.
- If Riley runs **with** an agent name (Section 8 onward and in production), the room must
  request that agent explicitly. Set the agent name in the starter's config (the
  `agentName` setting) so the token it mints includes an agent dispatch for
  `riley-receptionist`. Check the starter's README for the exact field in your version.

## 4. Run

```bash
# terminal 1: the agent
python agents/s13_capstone_receptionist.py dev

# terminal 2: the web app
pnpm install
pnpm dev        # open http://localhost:3000 and press the call button
```

## 5. Deploy

Deploy the Next.js app anywhere that runs Node (Vercel, Netlify, Render, a container).
Set the three `LIVEKIT_*` variables in the host's secret settings. The agent is deployed
separately (lecture 12.3, `deploy/Dockerfile`); both only need to point at the same
LiveKit project.

## Checklist before sharing the link

- The page says clearly that callers are talking to an AI assistant.
- Microphone permission prompt is explained ("We need your microphone to talk to Riley").
- Rate limiting on `/api/connection-details` (every token costs agent minutes).
- A fallback phone number for people who cannot use the web call.
