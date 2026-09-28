# Production Budget

> **All prices are estimates** from the author's general knowledge of typical plan pricing, not quotes. Vendors change plans, tiers and prices often. **Check each vendor's current pricing page before purchasing** and record the actual amount in the "Actual" column. Currency: USD. Tools already paid for in Courses 1-3 are marked "shared", and only the incremental cost counts here.

---

## 1. Tools and subscriptions

| Item | Purpose | Est. cost (estimate) | Months | Est. subtotal | Actual | Notes |
|---|---|---|---|---|---|---|
| HeyGen (paid plan with enough avatar minutes for ≈235 generated minutes) | Avatar narration | ~$30-100/mo depending on tier and minutes (estimate) | 3 | ~$90-300 | | Shared with Courses 1-3 if already subscribed. Check the minute or credit allowance vs ≈235 generated minutes (derivation in `video-generation-plan.md` §4.3); you may need a higher tier or add-on credits |
| OBS Studio | Screen recording | $0 | | $0 | | Open source |
| DaVinci Resolve (free) or CapCut | Editing | $0 (free tiers) | | $0 | | Resolve Studio is a one-off license if you need it (estimate a few hundred dollars) |
| Figma or Canva (Pro) | Diagrams D1-D12, slides, course image | ~$10-20/mo (estimate) | 3 | ~$30-60 | | Shared |
| Caption editing | Correct auto-captions (attribute names) | $0 (Udemy/Resolve/manual) | | $0 | | Script-based captions for avatar lectures |
| Stock music (licensed) | Promo + intros | ~$0-20/mo or per track (estimate) | 1-3 | ~$0-60 | | Keep licenses |
| Stock imagery (course image) | Concept assets | ~$0-30 (estimate) | | ~$0-30 | | Or build the art in Figma (recommended: the waterfall is easy to draw) |

## 2. APIs and infrastructure (for recording, testing and rehearsal)

> Production usage is higher than a student's (≈$5-15 per curriculum) because of rehearsals, retakes, judge runs and CI runs, but this course is unusually cheap to produce because **most captures use the offline replay**. Budget with **hard spend limits** on every account.

| Item | Use | Est. production usage cost (estimate) | Actual | Notes |
|---|---|---|---|---|
| OpenAI (`gpt-4.1-mini`, `gpt-4.1`, `gpt-5-mini`) | Live Atlas requests (2.3, 1.4, 6.6, 13.5), rehearsals ×3 | ~$10-40 (estimate) | | Most lectures run `OFFLINE=1`; set a ~$50 hard cap on the production project |
| OpenAI (online judge via DeepEval, 8.2, 8.7, 11.4, 14.3) | Sampled judge runs on the frozen day, rehearsals | ~$10-40 (estimate) | | Cap with `JUDGE_MAX_CALLS`; the judge cost is itself a teaching point |
| OpenAI (script polish, optional TTS, transcripts) | Production tooling | ~$5-15 (estimate; more if Option A TTS) | | See `video-generation-plan.md` §7 |
| Langfuse Cloud | Recording project, Sections 2-12 | $0 (free tier; check current limits and whether the replayed day's span volume fits the free tier's monthly allowance) | | Self-hosted in Section 13 at $0 |
| LangSmith | Section 12.2 | $0 (free tier; check) | | |
| Arize Phoenix | Section 12.3 | $0 (open source, local) | | |
| Datadog | Section 12.4 (conceptual only) | $0 | | No account needed; use public docs screenshots with attribution or draw the diagram |
| Docker Desktop / Docker Engine | Sections 9, 13 | $0 for personal use (check Docker Desktop licence terms for your situation) | | Self-hosted Langfuse + collector + Prometheus + Grafana need RAM, not money |
| GitHub Actions | CI budget gate (13.3) | $0 (public repo) | | Live eval jobs use OpenAI credits (counted above) |
| Cloud VM for a "real" self-host demo (optional) | 13.1 alternative to local Docker | ~$0-20 (estimate) | | Only if you demo on a remote host |

## 3. Other

| Item | Est. cost (estimate) | Notes |
|---|---|---|
| Microphone / headphones (if not owned) | ~$50-200 (estimate) | Shared with earlier courses if owned |
| Extra RAM or a second machine for the compose stack (if needed) | ~$0-300 (estimate) | Only if the recording machine can't run Langfuse + collector + Prometheus + Grafana with OBS |
| Beta student coupons | $0 | Free coupons (limits apply; verify) |
| Paid promotion | $0 planned | Organic launch; revisit after 60 days |
| Review of the governance lecture (10.4) by someone with compliance experience (optional but recommended) | Varies; get a quote or ask a peer | The lecture is labelled not legal advice, but a quick review of the EU AI Act statements reduces risk |

## 4. Summary (estimate ranges)

| Category | Low (estimate) | High (estimate) |
|---|---|---|
| Tools and subscriptions | ~$120 | ~$450 (excl. optional Resolve Studio license) |
| APIs and infrastructure | ~$25 | ~$135 |
| Hardware (if needed) | $0 | ~$500 |
| **Total cash outlay** | **~$145** | **~$1,085** |

The biggest cost is **instructor time** (see `production-schedule.md`), not cash. The biggest variable cost is **HeyGen minutes**. API spend is small by design because of the offline replay; the one thing that can make it large is an uncapped judge run, so cap it.

## 5. Cost controls

- [ ] Hard spend limit and billing alerts on the OpenAI production project (~$50), separate from the student-example project
- [ ] `JUDGE_MAX_CALLS` set in `evals/online_judge.py` for every recording session
- [ ] Separate recording accounts and projects (also a security control; see `recording-guide.md` §6.2)
- [ ] Use `OFFLINE=1` and the frozen replay for every capture that doesn't need a live request
- [ ] Log API spend per week in the "Actual" column
- [ ] After publishing: downgrade subscriptions, delete recording projects' traces, rotate or revoke keys
