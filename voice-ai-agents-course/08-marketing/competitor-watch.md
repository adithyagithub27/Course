# Competitor Watch: Voice AI Agents

> Source: `00-course-strategy/next-course-market-research.md` (research date 2026-09-28). Student counts and ratings are **as shown on the listings on the research date**. Re-verify them in Udemy and in Marketplace Insights before using any of them. Update this file monthly. Don't copy competitor content. Watch for positioning, updates and gaps only.

---

## 1. Direct competitors: code-first voice courses on Udemy

The research found **only three** code-first voice courses, none a bestseller, and **none teaching testing or evaluation of voice agents**.

| Course | URL (from research) | Research notes | What to monitor |
|---|---|---|---|
| Full-Stack Voice AI Agent with LiveKit, n8n & MCP on AWS | https://www.udemy.com/course/full-stack-voice-ai-agent-with-livekit-n8n-and-mcp-on-aws/ | Code-first, uses LiveKit; mixes in n8n and MCP; AWS deploy | Student count, rating, last-updated date, LiveKit version used (1.x vs 0.x APIs), whether a testing section is added, price and coupon patterns |
| Production Voice AI: SIP Telephony LiveKit AWS Docker Python | https://www.udemy.com/course/livekit-voice-ai-agent/ | Closest to our positioning ("Production", SIP, LiveKit, Docker, Python) | **Highest priority.** Title changes, curriculum additions (testing, observability, Pipecat, OpenAI Realtime), review themes, bestseller badge, update cadence |
| AI Voice Agents: Vapi, ElevenLabs, n8n & MCP | https://www.udemy.com/course/ai-voice-agents-automation-with-vapi-elevenlabs-n8n-mcp/ | Platform-based (Vapi, ElevenLabs) with n8n | Whether it moves toward code; which platforms it adds; audience overlap from review text |

## 2. Adjacent competitors: no-code voice (proof of demand)

| Course | Research data (listing, 2026-09-28) | Why it matters | Monitor |
|---|---|---|---|
| AI Builder in n8n (agents and voice agents), https://www.udemy.com/course/ai-builder-with-n8n-create-agents-voice-agents/ | 37,833 students / 4.8 | Proves learners pay for voice-agent content | Growth rate; review themes that hint at "hit the limits of no-code" (our audience) |
| n8n AI Agents, Automations & Voice Agents, https://www.udemy.com/course/n8n-course/ | 50,038 students / 4.5 | Large no-code audience that includes voice | Same |

## 3. Platform and ecosystem "competitors" (free content)

Voice platforms and frameworks publish free docs, examples and tutorials, and these shape what students expect.

| Source | Type | Monitor |
|---|---|---|
| LiveKit Agents docs, examples and releases | Framework (our primary) | **Breaking API changes** (we pin 1.8.x), new testing or telephony features, deprecations of anything used in curriculum §6 |
| Pipecat docs and releases | Framework (Section 14) | API changes vs 1.12 (e.g., context/aggregator modules), new runner patterns |
| OpenAI Realtime API (`gpt-realtime`) | Model/API (Section 6) | Model renames, SIP and session-limit changes, pricing changes (affects `provider-cost-guide.md` and 10.4) |
| Vapi, Retell, ElevenLabs Agents, Bland | Managed platforms (14.3 build-vs-buy) | New features that shift the build-vs-buy matrix (testing/simulation features, compliance offerings, pricing model changes) |
| Deepgram, Cartesia, ElevenLabs, Twilio | Providers | Model names (`nova-3`, `sonic-3`), free tier changes (affect the student budget of ~$10-20), SIP trunk setup UI changes (affect 8.2 screencasts) |
| DeepLearning.AI / Coursera / Maven | Other platforms | Research: evals and agent courses exist at short-course depth; watch for a dedicated voice-agent short course |
| "Voice AI agents production 2026" comparison article (reactify-solutions.com, from research sources) | Third-party content | New entrants and framing |

## 4. Monthly monitoring checklist

- [ ] Search Udemy for: "voice AI agent", "voice agent", "LiveKit", "Pipecat", "OpenAI Realtime", "AI phone agent", "AI receptionist", "Vapi", "Retell". Record new courses in the table below
- [ ] For the three direct competitors: student count, rating, review count, last updated, price, bestseller/highest-rated badge
- [ ] Read the 10 newest reviews of each direct competitor. Note complaints (outdated APIs, missing telephony, no tests) that our course already addresses. Use them for positioning, never for naming competitors in copy
- [ ] Check Marketplace Insights for "voice AI agents" and "LiveKit" (demand vs supply trend)
- [ ] Check LiveKit Agents and Pipecat release notes. If anything in curriculum §6 changes, open an update ticket
- [ ] Check provider pricing pages; update `10-resources/provider-cost-guide.md` if the student budget changes

## 5. Log

| Date | Course / source | Change observed | Our response |
|---|---|---|---|
| 2026-09-28 | All | Baseline from market research | Positioning: code-first + testing + phone + cost; avoid "first/only" claims |
| | | | |

## 6. Positioning guardrails

- Don't claim to be "the first" or "the only" course that teaches something. The research warns that competitive claims go stale quickly, as happened with Course 2's differentiation doc. Say what the course **does** instead ("a full section on testing voice agents").
- Don't name competitors in Udemy copy or course videos.
- If a direct competitor adds a testing section, lead with the **depth** of Section 9 (pyramid, tool-call assertions, WER, latency budgets, simulated callers, CI) and the link to Course 2.
