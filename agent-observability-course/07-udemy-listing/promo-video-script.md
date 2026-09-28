# Promo Video Script

**Course:** AI Agent Observability & Cost Control: LLMOps in Production
**Target length:** 105 seconds (hard range 90-120 s)
**Placement:** Udemy course landing page promo video
**Format:** Instructor to camera (real camera preferred, see note) + live cost-meter demo + trace waterfall + dashboard screencast + diagrams, in the design system in `../../10-graphics/design-system.md`

---

## Udemy promo video guidelines applied (verify current guidelines in the Teaching Center)

| Guideline (as understood) | How this script meets it |
|---|---|
| Instructor appears on camera early and introduces themselves | Shot 2 (0:10) is the instructor to camera, with name and lower third |
| Show what students will actually build and learn | Live cost meter, a real Langfuse trace, real Grafana panels, the CI gate failing and passing |
| Keep it short (roughly 2 minutes or less) | 105 s |
| No external links, URLs, social handles, email addresses or phone numbers | No URLs on screen. Langfuse and Grafana UIs are shown with the browser address bar cropped. The repo is called "the course repo", with no GitHub URL |
| No coupons, prices or "limited time" claims | None. The only dollar figure is the fictional demo bill, labelled as a simulation |
| Clear audio, HD video (at least 720p; we export 1080p) | See `09-production/recording-guide.md` |
| Promo content should reflect the actual course | Every clip comes from a real lecture (listed in the shot list) |

**Avatar note:** most lectures are HeyGen avatar-narrated. For the promo, **film the instructor on a real camera for Shots 2 and 9 if at all possible.** A real face builds trust on a landing page, and Udemy's rules on AI-generated presenters and disclosure may apply (verify Udemy's current AI content policy, and see `publish-checklist.md` §9). If you use the avatar, add the on-screen disclosure noted in Shot 2.

**Fiction note:** the "$4,000" in Shot 1 is the simulated bill from lecture 1.1's `loop` scenario against a price table. Label it `Simulated traffic` on screen. Never present it as a real invoice.

---

## Shot list and script

| # | Time | Shot / visual | On-screen text | Voiceover (VO) / dialogue |
|---|---|---|---|---|
| 1 | 0:00-0:10 | **Cold open, the cost meter.** Ops Console cost panel, dark theme. A counter climbs: $12… $180… $1,400… $4,000. Behind it, a trace waterfall with the same tool span repeating in red. | `Friday 18:02 → Monday 08:15` / `Simulated traffic` | **VO:** "Friday evening, one tool call fails. The agent retries. Every retry makes the prompt longer. Nobody is watching. By Monday morning the bill looks like this." |
| 2 | 0:10-0:20 | **Instructor to camera**, mid shot. Lower third: name + one-line credential placeholder. | `[Instructor Name]` / `[one-line credential from instructor-bio.md]` (if avatar: `Presented by an AI avatar of [Instructor Name]`) | "That run is simulated, but the pattern is real, and I've seen versions of it more than once. I'm [Instructor Name]. This course teaches you to see what your agents do, know what every request costs, and stop the weekend before it starts." |
| 3 | 0:20-0:32 | **The problem.** Quick red-tinted cuts (K1 hook): a flat "requests per minute" APM chart that shows nothing wrong; a p95 latency line doubling after lunch; a judge-score line sliding down while every dashboard is green. | `Your APM sees requests` → `Not tokens, tools or steps` → `Nothing is red. Users are unhappy.` | "Classic monitoring sees requests and errors. It doesn't see tokens, tool calls, agent steps or a prompt that quietly got worse. Agents fail expensively and silently." |
| 4 | 0:32-0:47 | **Trace it.** Screencast: `curl` a question to Atlas; cut to the Langfuse trace: agent span → retriever → generation with usage and cost → tool span. Then the GenAI attributes panel (`gen_ai.operation.name`, `gen_ai.usage.input_tokens`). | `OpenTelemetry • GenAI semantic conventions • Langfuse` | "You'll instrument Atlas, an IT and HR helpdesk agent, with OpenTelemetry and the GenAI semantic conventions, and read every step in Langfuse: which tool it called, with what, what came back, and where the tokens went." |
| 5 | 0:47-1:02 | **Cost it.** Split screen: token anatomy diagram (input, output, cached, reasoning) / the showback report by tenant; then the Ops Console before/after bars from the 40% challenge. | `Cost per request • session • tenant • feature` `Caching • Context diet • Routing • Budgets` | "Then you'll put a price on every generation and roll it up by session, user and tenant into a report finance accepts. You'll add prompt caching, a context diet, small-model-first routing and per-tenant budgets, and prove the saving on the same day of traffic." |
| 6 | 1:02-1:14 | **Hold it.** Chaos demo: `slow_provider` injected; p95 line climbs, then the fallback rate rises and p95 recovers. A Grafana panel with the SLO line and burn rate. | `Latency budgets • Fallbacks • Circuit breakers • SLOs` | "You'll set latency budgets, measure time to first token and p95, and add timeouts, retries and fallbacks that hold when a provider slows down during peak." |
| 7 | 1:14-1:28 | **Signature section: you are on call.** The incident brief card for Incident 1; a student-style investigation in the Ops Console; then the reveal: a context-bloat curve on one tenant plus a retry storm. Cut to the postmortem template. | `Incident labs • Investigate first • Then the reveal` | "This is where the course is different. Section 11 hands you three real-shaped incidents as traces and a brief. You investigate first. Then you see the reveal, write the postmortem, and turn it into a budget, an alert and a test." |
| 8 | 1:28-1:38 | **Ship it.** `docker compose up` for Langfuse, the OTel Collector, Prometheus and Grafana; then a GitHub Actions run: the budget gate fails a PR in red, then passes in green after a fix. | `Docker Compose • OTel Collector • CI budget gate` | "You'll self-host the whole stack with Docker Compose, and add a CI gate that fails a pull request when cost per session or p95 regresses." |
| 9 | 1:38-1:47 | **Instructor to camera**, close. Course title card fades in behind (K2 style). | `AI Agent Observability & Cost Control` `LLMOps in Production` | "If you can call an LLM from Python, you can do this. Enroll, and within the first hour you'll have your first trace on screen." |

**Total: ~107 s on the shot clock.** VO word count is about 300 words (counted from the captions below), which is about 128 s at a strict 140 wpm; the promo reads at a slightly brisker ~170 wpm, which lands at ~105 s. If the cut runs over 120 s, trim Shot 5 first (drop the second sentence), then Shot 3.

---

## Captions (SRT-ready text)

Upload corrected captions for the promo. Don't rely on auto-captions for product names.

```text
1  00:00:00,500 --> 00:00:10,000  Friday evening, one tool call fails. The agent retries. Every retry makes the prompt longer. Nobody is watching. By Monday morning the bill looks like this.
2  00:00:10,000 --> 00:00:20,000  That run is simulated, but the pattern is real, and I've seen versions of it more than once. I'm [Instructor Name]. This course teaches you to see what your agents do, know what every request costs, and stop the weekend before it starts.
3  00:00:20,000 --> 00:00:32,000  Classic monitoring sees requests and errors. It doesn't see tokens, tool calls, agent steps or a prompt that quietly got worse. Agents fail expensively and silently.
4  00:00:32,000 --> 00:00:47,000  You'll instrument Atlas, an IT and HR helpdesk agent, with OpenTelemetry and the GenAI semantic conventions, and read every step in Langfuse: which tool it called, with what, what came back, and where the tokens went.
5  00:00:47,000 --> 00:01:02,000  Then you'll put a price on every generation and roll it up by session, user and tenant into a report finance accepts. You'll add prompt caching, a context diet, small-model-first routing and per-tenant budgets, and prove the saving on the same day of traffic.
6  00:01:02,000 --> 00:01:14,000  You'll set latency budgets, measure time to first token and p95, and add timeouts, retries and fallbacks that hold when a provider slows down during peak.
7  00:01:14,000 --> 00:01:28,000  This is where the course is different. Section 11 hands you three real-shaped incidents as traces and a brief. You investigate first. Then you see the reveal, write the postmortem, and turn it into a budget, an alert and a test.
8  00:01:28,000 --> 00:01:38,000  You'll self-host the whole stack with Docker Compose, and add a CI gate that fails a pull request when cost per session or p95 regresses.
9  00:01:38,000 --> 00:01:47,000  If you can call an LLM from Python, you can do this. Enroll, and within the first hour you'll have your first trace on screen.
```

Split lines longer than ~42 characters into two caption lines in the SRT editor. Keep each caption on screen for at least 1 second.

---

## Production notes

- **Shot 1 must come from a real replay.** Run `OFFLINE=1 make replay` with the `loop` scenario (lecture 1.1 setup) and screen-record the Ops Console cost panel at readable zoom (see `09-production/recording-guide.md` §6, the dashboard capture track). Speed the counter up in the edit rather than faking the numbers; keep the `Simulated traffic` label on screen for the whole shot.
- **Shot 4 and 6 UIs:** Langfuse and Grafana at 125-150% browser zoom, address bar cropped, project names and keys redacted per the recording guide. The trace shown must be the one from lecture 2.3, so the promo matches what students see in their first hour.
- **Shot 8 CI run:** use the course repo's own Actions history (a deliberately failing PR from lecture 13.3, then the fix). Blur any organisation or user names that aren't the course repo.
- **Audio:** mix VO at -16 LUFS integrated; music bed at about -24 LUFS; no music under Shot 1 (the climbing counter needs a single soft tick, not a bed).
- **Visual change every 5-8 s.** No static frame longer than 8 s.
- **Design system:** Deep Navy `#0A1628` backgrounds, Electric Teal `#00D4AA` accents, Alert Red `#FF4B4B` only in Shots 1, 3 and the failing gate in Shot 8, Warm Amber `#FFB020` for SLO lines and latency markers, Inter and JetBrains Mono.
- **Code and attributes on screen:** only API forms and attribute names from curriculum §6 (verified on langfuse 4 / opentelemetry-sdk 1.45 / semconv 0.66). Show the corner note "APIs verified on langfuse 4 / otel 1.45; GenAI conventions incubating".
- **No claims** of "best", "only", "first" or "#1", no student counts, no salary claims, no real invoices.
- **Export:** 1920×1080, H.264, 30 fps, AAC 48 kHz.
