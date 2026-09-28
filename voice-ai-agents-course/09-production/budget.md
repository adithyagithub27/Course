# Production Budget

> **All prices are estimates** from the author's general knowledge of typical plan pricing, not quotes. Vendors change plans, tiers and prices often. **Check each vendor's current pricing page before purchasing** and record the actual amount in the "Actual" column. Currency: USD. Tools already paid for in Courses 1 and 2 are marked "shared", and only the incremental cost counts here.

---

## 1. Tools and subscriptions

| Item | Purpose | Est. cost (estimate) | Months | Est. subtotal | Actual | Notes |
|---|---|---|---|---|---|---|
| HeyGen (paid plan with enough avatar minutes for ~11 h of output plus retakes) | Avatar narration | ~$30-100/mo depending on tier and minutes (estimate) | 3 | ~$90-300 | | Shared with Courses 1-2 if already subscribed. Check the minute or credit allowance vs ~700 finished minutes plus retakes; you may need a higher tier or add-on credits |
| OBS Studio | Screen recording | $0 | | $0 | | Open source |
| DaVinci Resolve (free) or CapCut | Editing | $0 (free tiers) | | $0 | | Resolve Studio is a one-off license if you need it (estimate a few hundred dollars) |
| Figma or Canva (Pro) | Diagrams, slides, course image | ~$10-20/mo (estimate) | 3 | ~$30-60 | | Shared |
| Loopback audio tool (e.g., Rogue Amoeba Loopback on macOS) | Agent/phone audio capture | $0 (BlackHole / VB-Cable / PipeWire) to a one-off license (estimate ~$100) | | $0-100 | | Free options work |
| Caption editing | Correct auto-captions | $0 (Udemy/Resolve/manual) | | $0 | | Script-based captions for avatar lectures |
| Stock music (licensed) | Promo + intros | ~$0-20/mo or per track (estimate) | 1-3 | ~$0-60 | | Keep licenses |
| Stock imagery (course image) | Concept A/C assets | ~$0-30 (estimate) | | ~$0-30 | | Or build the art in Figma |

## 2. APIs and infrastructure (for recording, testing and rehearsal)

> Production usage is much higher than a student's (~$10-20 per curriculum) because of rehearsals, retakes, the evals and simulated-caller runs, and CI runs. Budget for it with **hard spend limits** on every account.

| Item | Use | Est. production usage cost (estimate) | Actual | Notes |
|---|---|---|---|---|
| LiveKit Cloud | Rooms, agents, SIP, deploys | $0 on the free tier to low tens of dollars (estimate) | | Check free-tier minutes and whether deploy (12.3, 13.5) needs a paid plan |
| OpenAI (GPT-4.1 mini, judge LLM, `gpt-realtime`) | Cascaded LLM, evals, Section 6 realtime | ~$30-150 (estimate) | | Realtime audio is usually the most expensive line per minute; limit S6 rehearsals |
| Deepgram (STT) | STT | ~$0-30 (estimate; starter credits may cover it) | | Check the current free credit |
| Cartesia (TTS) | TTS | ~$0-30 (estimate) | | Check plan and credits |
| ElevenLabs (optional) | Alternative TTS demo | ~$0-25 (estimate) | | Only if shown |
| Twilio | Phone number + SIP trunk minutes, 2 numbers (inbound + transfer target), outbound demos | ~$10-40 (estimate) | | Number rental is monthly; release numbers after publishing if not kept |
| Langfuse | Tracing (10.3) | $0 (free cloud tier or self-host) | | |
| GitHub Actions | CI (9.10) | $0 (public repo) | | Agent tests with secrets use API credits (counted above) |
| Container host for the self-host demo (12.4) | Optional | ~$0-20 (estimate) | | Only if you demo a live self-host |

## 3. Other

| Item | Est. cost (estimate) | Notes |
|---|---|---|
| Microphone / headset (if not owned) | ~$50-200 (estimate) | A closed-back headset is essential to prevent agent echo |
| Second phone / SIM for call demos (if not owned) | ~$0-30 (estimate) | A softphone can replace it |
| Beta student coupons | $0 | Free coupons (limits apply; verify) |
| Paid promotion | $0 planned | Organic launch; revisit after 60 days |
| Legal review of the compliance lecture (optional but recommended) | Varies widely; get a quote | The compliance lecture is labelled not legal advice, but a quick review reduces risk |

## 4. Summary (estimate ranges)

| Category | Low (estimate) | High (estimate) |
|---|---|---|
| Tools and subscriptions | ~$120 | ~$550 (excl. optional Resolve Studio license) |
| APIs and infrastructure | ~$40 | ~$350 |
| Hardware (if needed) | $0 | ~$230 |
| **Total cash outlay** | **~$160** | **~$1,130** |

The biggest cost is **instructor time** (see `production-schedule.md`), not cash. The biggest variable cost is **HeyGen minutes** plus **OpenAI Realtime rehearsals**. Watch both weekly.

## 5. Cost controls

- [ ] Hard spend limits and billing alerts on OpenAI, Deepgram, Cartesia, Twilio and LiveKit (where offered)
- [ ] Separate recording accounts (also a security control; see `recording-guide.md` §6)
- [ ] Use `mock_tools` and text-session tests while developing; switch to real audio only for recording
- [ ] Log API spend per week in the "Actual" column
- [ ] After publishing: release unused phone numbers, downgrade subscriptions, rotate or revoke keys
