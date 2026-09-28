# SEO Keywords: Udemy Search and YouTube

> **All volume figures in this file are estimates, not measurements.** Volume tiers (High / Med / Low) are the author's relative judgement from topic breadth and the listings found in the market research. Before committing titles, check them in **Udemy Marketplace Insights** (search demand vs course supply), **Google Keyword Planner / Google Trends** (12 months) and **YouTube search autocomplete / YouTube Studio Research tab**. The market research's own validation list includes Marketplace Insights for "LLM observability" and "AI FinOps".

---

## 1. Primary keywords (title, subtitle, first paragraph of description)

| # | Keyword | Est. volume (estimate) | Est. competition on Udemy (estimate) | Where used |
|---|---|---|---|---|
| 1 | LLM observability | Low-Med, rising | Low (research: three courses, none large) | Title ("Observability"), description P2 |
| 2 | LLMOps | Med | Low-Med (mostly inside MLOps courses) | Title, subtitle option 8, description |
| 3 | AI agent observability / agent observability | Low, rising | Very low | Title, description P1 |
| 4 | LLM cost optimization / LLM cost | Low-Med | Low (research: 1-hour briefings) | Title ("Cost Control"), Section 6 title |
| 5 | Langfuse | Low-Med, rising | Low (three courses) | Subtitle, description, Section 4 title |
| 6 | OpenTelemetry | Med (broad, mostly non-AI) | Med overall; Low for GenAI angle | Subtitle, Section 3 title |

## 2. Secondary keywords (description body, section and lecture titles)

| # | Keyword | Est. volume (estimate) | Placement |
|---|---|---|---|
| 1 | GenAI semantic conventions / gen_ai attributes | Low (emerging) | Section 3 title, lecture 3.3 |
| 2 | LLM tracing / trace LLM agent | Low-Med | Sections 3-5 |
| 3 | AI FinOps / FinOps for GenAI | Low (emerging) | Section 6 title, description |
| 4 | token usage / token cost tracking | Low-Med | Lectures 6.1-6.3 |
| 5 | prompt caching | Low-Med | Lecture 6.4 |
| 6 | LLM routing / model routing / LiteLLM | Low-Med | Lecture 6.6 |
| 7 | LLM latency / time to first token | Low-Med | Section 7, lecture 5.4 |
| 8 | LLM-as-judge / online evaluation | Med (Course 2 overlap) | Section 8 |
| 9 | drift detection LLM | Low | Lecture 8.5 |
| 10 | SLO / SRE for AI / AI SRE | Low-Med | Section 9, lecture 15.2 |
| 11 | Prometheus Grafana | Med-High (broad) | Section 9 title |
| 12 | LangSmith / Arize Phoenix / OpenLLMetry | Low-Med each | Section 12 lecture titles |
| 13 | Datadog LLM observability | Low | Lecture 12.4 |
| 14 | incident response / postmortem | Med (broad, SRE) | Section 11 |
| 15 | PII masking / AI governance logging | Low-Med | Section 10 |
| 16 | Docker Compose Langfuse self-host | Low | Lecture 13.1 |
| 17 | CI cost gate / budget gate | Very low (our coinage) | Lecture 13.3 |

## 3. Long-tail keywords (lecture titles, YouTube titles, blog posts)

All estimated Low volume, High intent (estimates).

1. how to trace an LLM agent with OpenTelemetry
2. OpenTelemetry GenAI semantic conventions Python example
3. Langfuse tutorial Python (v4 / OpenTelemetry SDK)
4. Langfuse vs LangSmith vs Arize Phoenix
5. how much does my AI agent cost per request
6. cost per session LLM agent
7. LLM cost per tenant showback
8. reduce LLM API costs prompt caching
9. LiteLLM Router fallback example
10. LLM latency p95 time to first token
11. LLM-as-judge in production sampling
12. detect prompt regression in production
13. SLOs for AI agents
14. Grafana dashboard for LLM agent
15. Prometheus metrics LLM tokens
16. mask PII in LLM traces
17. self-host Langfuse Docker Compose
18. OTel Collector tail sampling LLM
19. AI agent incident postmortem example
20. runaway agent loop detection
21. LLMOps engineer interview questions
22. AI SRE role

## 4. YouTube keyword clusters

| Cluster | Seed terms (check autocomplete) | Video ideas (see `youtube-strategy.md`) |
|---|---|---|
| Cost | "LLM cost", "reduce OpenAI API cost", "token cost tracking" | #1, #2, #4 |
| Trace | "OpenTelemetry LLM", "Langfuse tutorial", "trace AI agent" | #3, #6 |
| Reliability | "LLM latency", "LiteLLM fallback", "LLM rate limit 429" | #7 |
| Quality | "LLM as judge production", "prompt regression" | #8 |
| Incidents | "AI agent incident", "SRE for AI" | #5 |
| Compare | "Langfuse vs LangSmith", "Arize Phoenix", "Datadog LLM observability" | #9 |
| Governance | "PII in logs LLM", "EU AI Act logging" | #10 |

## 5. Placement rules

- The title and subtitle carry primary keywords 1-6 (see `07-udemy-listing/title-and-subtitle.md`).
- The first 2 paragraphs of the description include "agent", "production", "cost", "trace" (done); "observability" and "LLMOps" are in the title directly above.
- **Section titles** in Udemy should be keyword-bearing, e.g., "Section 3: Tracing Fundamentals and the OpenTelemetry GenAI Semantic Conventions", "Section 6: Cost Engineering: Token FinOps for Agents", "Section 9: Dashboards, SLOs and Alerting with Prometheus and Grafana".
- Don't keyword-stuff. Udemy's quality review and students both penalise unreadable titles.
- Don't use competitor or platform brand names in the title in a way that implies endorsement. "Langfuse" and "OpenTelemetry" in a subtitle are descriptive; "Official Langfuse course" would not be.

## 6. Keywords to avoid (from the market research)

- "Complete", "Masterclass", "Bootcamp", "A-Z": the most common patterns among incumbent AI course titles
- "MLOps" as the lead term: the research and the curriculum both position agents as different from classic MLOps; use it only as a secondary tag
- "AI governance", "EU AI Act", "ISO 42001" as lead terms: the research lists AI governance as a saturated red ocean. Section 10 is a governance-of-telemetry lecture, not a governance course
- Year stamps in the title (they go stale)
