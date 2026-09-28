# Next-Course Market Research: Where to Build in Q4 2026

> **Document purpose:** Identify AI course topics on Udemy (and adjacent platforms) that show real demand but are not yet saturated, and rank them against this instructor's two courses in production:
> 1. **Generative AI and AI Agents: Zero to Production, Build Real Apps** (broad build course)
> 2. **AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python** (quality course, documented in this repo)
>
> **Research date:** 2026-09-28
> **Method:** ~200 targeted web searches across Udemy course listings, Udemy Business / Coursera skills reports, Maven, DeepLearning.AI, Coursera, LinkedIn Learning, and third-party "best of" roundups. Student counts and ratings are as displayed in listings on the research date and should be re-verified in Udemy Marketplace Insights before committing.

---

## 1. Executive Summary

**Recommendation:** Build **"Production Voice AI Agents with Python: LiveKit, Pipecat & OpenAI Realtime (incl. testing voice agents)"** as Course 3, then **"AI Agent Observability, LLMOps & Cost Control"** as Course 4 to complete a Build, Test, Operate trilogy that cross-sells across all three student bases. **Agentic AI Certification Prep (Microsoft AB-100 / AB-620 / AI-500)** is the standalone fast-follow if a lower-effort, high-intent title is wanted.

Voice agents sit in the "proven demand, thin supply" quadrant: a no-code voice course already has 37,000 students at 4.8 stars, yet almost no code-first production course exists. Observability has moderate competition but the strongest fit, because it is the natural third step after building agents (Course 1) and testing them (Course 2).

**Warning on Course 1:** "Generative AI and AI Agents: Zero to Production" competes directly with the most crowded category on Udemy. The top three generic agent bootcamps alone hold roughly 900,000 students and reviewers have benchmarked 50+ such courses. Course 1 will not win on organic search as a generalist bootcamp; it needs a sharp production angle and should be treated as the top of the funnel that feeds Courses 2 through 4. See Section 6b.

**What to avoid:** generic "AI Agents bootcamp" courses (top three alone hold ~900,000 students; reviewers have benchmarked 50+ of them), prompt engineering/ChatGPT (2,600+ courses indexed), n8n no-code agents, general Claude Code, MCP basics, RAG basics, and AI governance/ISO 42001. These are red oceans in 2026.

**Warning on the current course:** the competitive claims in `course-differentiation.md` ("zero courses cover eval + observability", "only 2 real Udemy courses") are out of date. At least five new Udemy courses now cover DeepEval, RAGAS, Langfuse or "production LLM evaluation and observability" (see Section 6). The course is still differentiated on breadth and enterprise scenarios, but the positioning copy needs a refresh before launch.

---

## 2. Demand Signals (Platform-Level)

| Signal | Data point | Source |
|---|---|---|
| AI enrollments on Udemy | 10+ AI course enrollments per minute; AI consumption up 291% YoY | Udemy 2026 Global Learning & Skills Trends Report |
| Top net-new skill | "AI agents / agentic AI" is the #1 net-new AI skill consumed on Udemy Business | Udemy 2026 report |
| Fastest-growing technical topic | GitHub Copilot content consumption +13,534% YoY | Udemy 2026 report |
| Fastest-growing business topic | Microsoft Copilot +3,400% YoY | Udemy 2026 report |
| GenAI on Coursera | 14 enrollments/min; enterprise GenAI enrollments +234% YoY | Coursera Job Skills Report 2026 |
| Human role shift | Coursera: as workers offload whole tasks to agents, the human becomes the "expert validator of the final output" (directly supports eval/QA/observability positioning) | Coursera Job Skills Report 2026 |
| Enterprise adoption | Gartner: 40% of enterprise apps will include task-specific agents by end of 2026 (from <5% in 2025) | TechTarget / Gartner |
| Premium eval demand | Hamel Husain & Shreya Shankar's "AI Evals for Engineers & PMs" (Maven, ~$4,200): September 2026 cohort sold out; Oct 10 is the last 2026 cohort | Maven |
| New certifications | Microsoft launched agentic certs in 2026: AI-103 (Azure AI App & Agent Developer), AB-100 (Agentic AI Solution Architect), AB-620 (AI Agent Builder Associate), AI-500 (Multi-Agent AI Solutions Expert), GH-600 (GitHub Agentic AI Developer); NVIDIA NCP-AAI (Professional Agentic AI) | Udemy practice-test listings |
| Open standards | Anthropic's "Agent Skills" open standard adopted by Claude Code, GitHub Copilot, Cursor, OpenAI Codex | Udemy "Extending AI with Agent Skills 2026" listing |
| Managers learning AI | 40% YoY growth in managers pursuing AI education on Udemy | Research.com summary of Udemy data |

---

## 3. Saturation Map: What Exists on Udemy Today

Ratings/students are from listings on the research date.

### 3a. Saturated (do not enter)

| Topic | Evidence of saturation |
|---|---|
| **General "AI Agents" bootcamps** | Ed Donner "AI Engineer Agentic Track" 398,566 students / 4.7; 365 Careers "Intro to AI Agents" 277,438 / 4.5; Eden Marco "LangChain Agentic AI" 218,228 / 4.6; "Complete Agentic AI Bootcamp (LangGraph)" 66,526; "AI Agents & Workflows" (Schwarzmüller) 72,009; reviewers have compared 50+ agent courses and call most "outdated, framework-specific, or shallow". |
| **Prompt engineering / ChatGPT** | 2,600+ ChatGPT courses on Class Central; every major instructor has a 2026 refresh. |
| **n8n / no-code agents** | "n8n: AI Agents & Automation for Absolute Beginners" 200,000+; "n8n AI Agents, Automations & Voice Agents" 50,038 / 4.5; "AI Builder in n8n" 37,833 / 4.8; "Master n8n AI Agents" 21,386; 8+ courses in javinpaul's roundup. |
| **Claude Code (general usage)** | Academind 99,760; Eden Marco 38,442; Tom Phillips 25,899; Ankit Mistry Claude masterclass 266,000+; 10+ more listed, reviewers compared 20+. |
| **MCP basics** | Bestseller crash course, masterclass, bootcamp, "MCP for Beginners", "MCP & A2A", plus a certification practice test. Topic page exists on Udemy. |
| **RAG / LLM engineering fundamentals** | Covered inside every bootcamp above; dedicated RAG topic page; "RAG, AI Agents & GenAI 2026" 38.5 hours. |
| **AI governance / EU AI Act / ISO 42001** | 9+ courses found including AIGP prep, ISO 42001 Lead Implementer, EU AI Act Masterclass. |
| **Agentic AI for leaders / PMs / BAs** | 6+ leader courses, 6+ PM/PO courses ("Agentic AI for Product Owners" 18,211 students). Moderate-to-crowded. |

### 3b. Heating up fast (enter only with a sharp angle)

| Topic | Current supply | Note |
|---|---|---|
| **AI / LLM security & red teaming** | 8+ courses: "Prompt Injection & LLM Defense (2026)" (Promptfoo, Garak, PyRIT), "OWASP Top 10 for LLM v2026", "AI Red Teaming & LLM Hacking with Labs", "Agentic AI Security Masterclass", "AI Guardrails & Cybersecurity", "AI Security Bootcamp: Guardrails, LLM Gateways, Observability", "AI Agent Security for Vibe-Coded Agents" | Most are LLM-level or offensive-security framed. **Agent/MCP-specific security** (tool permissions, agent identity, MCP server hardening, blast radius) is still thin. |
| **Google ADK / A2A** | 6+ courses (ADK masterclass, ADK+MCP+A2A, A2A masterclass, multi-agent systems track) | Google ecosystem now covered. |
| **Playwright + AI/MCP for QA** | "Playwright + Claude AI & MCP Server 2026", "Playwright Automation Testing 2026: TypeScript, AI & MCP" (14,000+), "Gen AI for QA: Playwright, Copilot & Claude Code", "AI Browser Automation That Doesn't Suck", "Software Testing with AI Agents" | Rahul Shetty Academy (1.3M QA learners) dominates this lane. Avoid head-on. |
| **LLM observability (Langfuse)** | "LangFuse: LLM Observability, Tracing, Evaluation, Monitoring"; "LLM Observability and Cost Management: Langfuse"; "Production LLM Evaluation And Observability" (DeepEval + Langfuse) | 3 courses, none large yet. Still enterable as a sequel to the eval course, but no longer empty. |
| **Azure AI Foundry / Microsoft Foundry agents** | "Microsoft Foundry & Python: Enterprise AI Agents", "AI-103 Complete Course", "AI Agents Beginner to Pro: Azure AI Foundry Agent Service" | Covered at the tutorial level; cert-prep gap remains (see 3c). |
| **Spring AI (Java) / Semantic Kernel (.NET)** | 7 Spring AI courses; 6 Semantic Kernel courses; only 1 on Microsoft Agent Framework (the 2026 successor) | Huge enterprise audiences, moderate supply. |

### 3c. Open lanes with proven demand (candidates)

| Topic | Demand proof | Current Udemy supply |
|---|---|---|
| **Code-first production voice AI agents** (LiveKit Agents, Pipecat, OpenAI Realtime, SIP telephony, Deepgram/Cartesia/ElevenLabs) | n8n voice-agent course 37,833 students / 4.8; "n8n Voice Agents" 50,038; LiveKit Agents 1.0 with native MCP; OpenAI Realtime API GA with SIP | Only 3 code-first courses found: "Full-Stack Voice AI Agent with LiveKit, n8n & MCP on AWS", "Production Voice AI: SIP Telephony LiveKit AWS Docker Python", "AI Voice Agents: Vapi, ElevenLabs, n8n & MCP". None teaches **testing/evaluating** voice agents. |
| **Agentic AI certification prep (full course, not just practice tests)** | Microsoft AB-100, AB-620, AI-500, GH-600 and NVIDIA NCP-AAI all launched 2026; cert searches are high-intent | AB-100, AB-620, AI-500, GH-600, NCP-AAI: **only practice-test packs** found (127 to 842 students each). AI-103 has one complete course. No full video prep course for AB-100/AB-620/AI-500. |
| **Claude Agent SDK + Agent Skills (production agents, not Claude Code usage)** | Claude Code ecosystem: 99k + 38k + 26k students on usage courses; "Extending AI with Agent Skills 2026" already 6,034 students / 4.5 as a short course | **One** dedicated Claude Agent SDK course found ("Claude Agent SDK: Build Production AI Agents in Python"); one Agent Skills course. |
| **AI agent observability + LLMOps + cost control (AI FinOps)** | Enterprise ops roles; "LLM Token Optimization" and "FinOps for GenAI" courses exist but are 1-hour briefings | 3 Langfuse courses + 3 small cost courses; nothing combines OpenTelemetry GenAI semantic conventions, Langfuse/LangSmith/Arize Phoenix, drift detection and token FinOps. |
| **Agent memory & context engineering** | DeepLearning.AI ships a dedicated agent-memory short course; Ed Donner covers "context engineering" inside his bootcamp; Maven agentic course lists "memory & context engineering" as a module | **No** dedicated Udemy course found. Emerging keyword, unproven on Udemy. |
| **Agentic AI for QA/SDET in Python** (agents that generate, run, heal and evaluate tests) | QA is the largest testing-adjacent audience; Udemy pytest consumption +388% (from existing differentiation doc) | "Agentic AI for QA Automation with Python" (1 rating), "Agentic AI for QA & SDET", "2026 Using Gen AI & AI Agent in Software Automation Testing". Thin, but adjacent to Rahul Shetty's lane. |
| **AWS Bedrock AgentCore** | AWS is the largest cloud; AgentCore covers runtime, memory, identity, gateway, observability | 2 courses found ("Amazon Bedrock AgentCore: Build & Deploy any AI Agent on AWS", "[2026] Complete AWS Bedrock GenAI Course"). |
| **Spec-driven development (English)** | Udemy reports 70,000+ professionals explored "vibe coding"; spec-driven is the 2026 counter-trend | One Spanish-language course found; none in English. |
| **AI agents for cloud infrastructure / AIOps / SRE** | Platform engineering teams adopting agents | 2-3 courses ("AI Agents for Cloud Infrastructure", "AI for SRE & DevOps: AIOps", n8n SRE bootcamp). |

---

## 4. Ranked Recommendations

Scoring: **Demand** (evidence buyers exist), **Gap** (how few quality competitors), **Fit** (leverages both existing courses: the "build real apps" audience of Course 1 and the testing/eval brand of Course 2), **Durability** (will the topic still sell in 12 months). Each 1-5.

| Rank | Course concept | Demand | Gap | Fit | Durability | Total | Verdict |
|---|---|---|---|---|---|---|---|
| **1** | **Production Voice AI Agents with Python** (LiveKit Agents, Pipecat, OpenAI Realtime, SIP telephony, latency/interruption handling, plus a module on **testing and evaluating voice agents**) | 5 | 4 | 4 | 4 | **17** | **Build as Course 3.** Extends the "build real apps" promise of Course 1 into a modality no bootcamp covers, and reuses Course 2's eval tooling |
| **2** | **AI Agent Observability, LLMOps & Cost Control** (OpenTelemetry GenAI conventions, Langfuse + LangSmith + Arize Phoenix, drift, token FinOps, alerting) | 4 | 3 | 5 | 4 | **16** | **Build as Course 4.** Completes Build (C1), Test (C2), Operate (C4). Cross-sells to both existing student bases. Competition now exists, so lead with cost/FinOps + OTel angle |
| **3** | **Agentic AI Certification Prep: Microsoft AB-100 / AB-620 / AI-500** (full video course + labs + practice exams) | 4 | 5 | 2 | 3 | **14** | Standalone fast-follow. Highest-intent search, near-zero full-course competition, but weak brand fit and Microsoft-stack dependency |
| **4** | **Claude Agent SDK & Agent Skills: Build Production Agents** (SDK, subagents, hooks, MCP servers, Skills standard, evals of agents) | 4 | 4 | 3 | 3 | **14** | Strong market, but partly overlaps Course 1's build content; ecosystem changes monthly, plan quarterly re-records |
| **5** | **Securing AI Agents & MCP Servers** (agent identity, tool permissions, MCP server hardening, indirect prompt injection via tools, guardrails, promptfoo/PyRIT/Garak red teaming) | 5 | 2 | 4 | 4 | **15** | Demand is highest here but 8+ courses arrived in 12 months. Only viable with the agent/MCP-specific angle. Could instead be a red-team expansion of Course 2 |
| **6** | **Agentic AI for QA/SDET in Python** (agents that write, run, self-heal and evaluate tests) | 4 | 3 | 4 | 3 | **14** | Fits the Course 2 audience, but sits next to Rahul Shetty's Playwright+AI lane. Differentiate on Python + evals of test agents, not Playwright |
| 7 | **Agent Memory & Context Engineering** | 3 | 5 | 3 | 3 | 14 | Uncontested but unproven on Udemy; better as a 2-hour companion or a module added to Course 1 |
| 8 | AWS Bedrock AgentCore end-to-end | 4 | 4 | 2 | 4 | 14 | Good market, needs deep AWS credibility |
| 9 | Spec-Driven Development with AI coding agents (English) | 3 | 4 | 2 | 3 | 12 | Cheap to produce, low fit |

**Change from the first draft:** Observability moved from #4 to #2 and Certification Prep dropped from #2 to #3 once Course 1 was identified. With a build course and a test course already in hand, the operate course completes a trilogy that can be bundled and cross-promoted, which outweighs the cert course's search advantage.

### Why #1 is Voice Agents

- **Proven wallet:** buyers already pay for voice-agent content on Udemy (37,833 students at 4.8 stars for a no-code version, 50,038 for another). That is traction without saturation, because code-first courses number three and none is a bestseller.
- **Timing:** LiveKit Agents 1.0 and OpenAI Realtime GA (with SIP and remote MCP) landed within the last 12 months, so the "production" framing is fresh and defensible.
- **Brand fit:** a dedicated section on **evaluating voice agents** (turn-taking latency, interruption handling, transcription accuracy, tool-call correctness, DeepEval on transcripts, Langfuse traces) is something no competitor offers and it links directly to the existing eval course.
- **Enterprise scenarios transfer:** the banking, support and HR scenario datasets in `05-datasets/` can be reused as voice flows.

### Why #2 is Certification Prep

- Certification searches convert at the highest rate on Udemy and the practice-test-only competitors (127 to 842 students each) show the funnel is already forming.
- No full video prep course exists for AB-100, AB-620 or AI-500. First mover on a Microsoft cert title typically holds the bestseller badge for years.
- Risk: Microsoft may revise exam objectives; budget a refresh every six months.

---

## 5. Cross-Platform View (Coursera, DeepLearning.AI, Maven, LinkedIn Learning)

| Platform | What is covered | Implication for Udemy |
|---|---|---|
| **Coursera** | Specializations: "Agentic AI Engineering" (includes AI system evaluation), "AI Agents with Model Context Protocol", "Agentic AI Protocols (MCP, A2A, ACP)", "Full Stack Agentic AI", "Vibe Coding for Developers" | Protocols and general agent engineering are covered at university-partner quality. Do not compete on MCP/A2A fundamentals. |
| **DeepLearning.AI** | Short courses on agentic AI (Andrew Ng), **agent evaluation**, and **agent memory/persistence** | Evals and memory are being taught free at short-course depth. A Udemy course must be longer and project-based to justify the price. |
| **Maven** | "AI Evals for Engineers & PMs" ($4,200, sold out), "Agentic AI for PMs & Engineers (featuring Claude)" with memory/context engineering, evals, guardrails, cost/latency modules; "AI Engineering Bootcamp" | Premium buyers exist for evals, context engineering and cost/latency. Udemy can undercut at 1/100th the price. |
| **LinkedIn Learning** | "Work Smarter with AI Agents" path; technical paths on LangGraph, LlamaIndex, MCP, A2A, workflow automation | Business-side agent literacy is covered. |
| **Rahul Shetty Academy** | Remade "Testing AI Systems with DeepEval" in June 2026; runs an "AI Testing Learning Path" (LLM, RAG, Agents, ISTQB) | The QA-to-AI-testing lane has a strong incumbent. Voice, observability, and certification lanes do not. |

---

## 6. Competitive Update for the Existing Course (AI Agent Testing & Evaluation)

The differentiation doc claims only two real Udemy courses exist and none cover the full lifecycle. As of September 2026 the following also exist:

| Course (Udemy) | Overlap with our course |
|---|---|
| Testing AI Systems with DeepEval: AI Agents, Chatbots & RAG (Rahul Shetty, remade June 2026) | DeepEval, golden datasets, synthetic data, safety testing, agent evaluation |
| AI Agents, RAG & LLM Evals for Beginners: DeepEval & RAGAS (with Ollama) | DeepEval + RAGAS + HF Evaluate, positioned for "AI QA Engineers" |
| Production LLM Evaluation And Observability | DeepEval + Langfuse, agentic RAG chatbot, pre- and post-production |
| LangFuse: LLM Observability, Tracing, Evaluation, Monitoring | Langfuse module |
| LLM Observability and Cost Management: Langfuse, Monitoring | Observability + cost |
| Build & Test AI Agents, ChatBot, RAG with Ollama & Local LLMs | Testing agents with LangChain v1 |
| Production AI Agents with LangChain + LangGraph [2026] | Includes "security, testing, LangSmith observability" sections |
| Prompt Injection & LLM Defense (2026) | Automates red teaming with Promptfoo, Garak, PyRIT |

**Still unique to our course:** promptfoo + DeepEval + RAGAS + Langfuse + OpenTelemetry in one pipeline, CI/CD quality gates in GitHub Actions, five enterprise scenario datasets, Streamlit quality dashboard capstone, tool-calling correctness tests.

**Action items:**
1. Rewrite the "Supply Side" table in `course-differentiation.md` to list the eight competitors above and reposition on **full lifecycle + CI/CD gates + enterprise scenarios**, not "first" or "only".
2. Consider adding **Garak and PyRIT** alongside promptfoo in the red-teaming module, since the newest security competitor teaches all three.
3. Add a lecture on **evaluating agents against OpenTelemetry GenAI semantic conventions**, which no competitor mentions and which bridges to recommendation #2 (Observability).

## 6b. Saturation Risk for Course 1 (Generative AI and AI Agents: Zero to Production)

Course 1 is a generalist build course, which is the most crowded category on the platform.

| Direct competitor | Students | Rating | Framing |
|---|---|---|---|
| AI Engineer Agentic Track: The Complete Agent & MCP Course (Ed Donner) | 398,566 | 4.7 | 8 projects, 5 frameworks, 30 days |
| Intro to AI Agents and Agentic AI (365 Careers) | 277,438 | 4.5 | Beginner, business + build |
| LangChain: Agentic AI Engineering with LangChain & LangGraph (Eden Marco) | 218,228 | 4.6 | Framework deep dive |
| Machine Learning, Data Science & AI Engineering with Python | 247,465 | n/a | Broad AI engineering |
| AI Engineer Bootcamp 2026: LLMs, RAG, AI Agents & Vector DBs | 100,000+ | 4.6 | 30 hours, full pipeline |
| AI Agents & Workflows: The Practical Guide (Schwarzmüller) | 72,009 | n/a | Python + TypeScript |
| Complete Agentic AI Bootcamp with LangGraph and LangChain | 66,526 | n/a | Bootcamp |
| The Agentic AI Engineering Masterclass 2026 (Ryan Ahmed) | 30,209 | 4.5 | Multi-framework |
| Production AI Agents with LangChain + LangGraph [2026] | n/a | n/a | Explicitly "production-first": security, testing, LangSmith, FastAPI, Docker |
| AI Engineer Production Track: Deploy LLMs & Agents at Scale | 9,456 | 4.8 | Cloud deploy, Terraform, CI/CD, cost |

Reviewer consensus across 20+, 30+ and 50+ course roundups: most agent bootcamps are "outdated, framework-specific with no broader context, or just plain shallow". That is the opening, but only if Course 1 is visibly different in its title and first three lectures.

**What "Zero to Production" must mean to stand out:**

- **One stack, shipped.** Competitors tour five frameworks. Course 1 should pick one (for example OpenAI Agents SDK or LangGraph) and take a single app all the way to a deployed, monitored URL: FastAPI, Docker, a cloud deploy, auth, rate limits, cost caps.
- **Quality built in from lecture one.** Evals, tracing and a CI check appear early and are reused throughout. No top-ten bootcamp does this, and it is the bridge to Course 2.
- **Cost and latency as first-class topics.** Only the "Production Track" course above covers LLM cost management, and it has under 10,000 students. This is the cheapest differentiator to add.
- **Real apps, not demos.** Lead with the deployed artifacts (a support agent with escalation, a document agent with RAG, a tool-calling ops agent) and reuse the enterprise scenario datasets from `05-datasets/`.
- **Title keywords.** Include "Production", "Deploy" and the chosen framework in the title. Avoid "Complete", "Masterclass", "Bootcamp" and "A-Z", which are the most common patterns among the incumbents.

**Portfolio role:** Course 1 is the top of the funnel. Expect it to earn more from cross-sells into Courses 2, 3 and 4 than from its own organic ranking. Plan the end-of-course lecture and the completion message around that hand-off.

---

## 7. Suggested 12-Month Roadmap

| Quarter | Release | Rationale |
|---|---|---|
| Q4 2026 | Launch **Course 1: GenAI & AI Agents: Zero to Production** with the sharpened production angle (Section 6b) and **Course 2: AI Agent Testing & Evaluation** with refreshed positioning (Section 6) | Both already in production; launch C1 first so it feeds C2 |
| Q1 2027 | **Course 3: Production Voice AI Agents with Python** (rank #1) | Proven demand, thin supply, extends "build real apps" and reuses eval tooling |
| Q2 2027 | **Course 4: AI Agent Observability, LLMOps & Cost Control** (rank #2) | Completes Build, Test, Operate; bundle and cross-promote all four |
| Q3 2027 | **Agentic AI Certification Prep (AB-100 / AB-620 / AI-500)** (rank #3) if the certs are still current | First-mover on cert titles; high-intent search |
| Backlog | Claude Agent SDK & Skills; Securing Agents & MCP; Agent Memory & Context Engineering | Re-check saturation each quarter before committing |

---

## 8. Validation Steps Before Committing (owner to do)

1. Open **Udemy Marketplace Insights** for: "voice AI agents", "LiveKit", "AB-100", "AB-620", "AI-500", "Claude Agent SDK", "LLM observability", "AI FinOps". Record demand, competition and median revenue.
2. Check Google Trends (12 months) for "LiveKit agents", "OpenAI Realtime API", "AB-100 exam", "agentic AI certification".
3. Confirm Microsoft exam objective versions and any announced retirement dates for AB-100/AB-620/AI-500.
4. Post a one-question poll to Course 1 students: "Which would you buy next?" with the top four options.

---

## Sources

Platform reports
- Udemy Business, 2026 Global Learning & Skills Trends Report: https://business.udemy.com/2026-global-learning-skills-trends-report/
- Udemy press release, "AI Meets EQ": https://about.udemy.com/press-releases/2026-global-learning-skills-trends-report/
- Udemy Business, Top AI Workplace Skills 2026: https://business.udemy.com/resources/top-ai-skills-2026/
- Coursera Job Skills Report 2026: https://blog.coursera.org/introducing-courseras-job-skills-report-2026-the-most-critical-skills-the-worlds-learners-need-this-year/
- Udemy "Vibe Coding" series press release: https://www.businesswire.com/news/home/20250723155319/en/Udemy-Supercharges-AI-Upskilling-With-New-Vibe-Coding-Series
- TechTarget, in-demand AI skills (Gartner forecast): https://techtarget.com/searchcio/tip/In-demand-AI-skills
- Research.com, Best Udemy AI Courses for Agentic AI: https://research.com/online-courses/artificial-intelligence/best-udemy-ai-courses-for-agentic-ai

Saturation evidence (Udemy listings)
- AI Engineer Agentic Track (Ed Donner): https://www.udemy.com/course/the-complete-agentic-ai-engineering-course/
- Intro to AI Agents and Agentic AI (365 Careers): https://www.udemy.com/course/intro-to-ai-agents-and-agentic-ai/
- LangChain Agentic AI Engineering (Eden Marco): https://www.udemy.com/course/langchain/
- AI Agents & Workflows (Schwarzmüller): https://www.udemy.com/course/ai-agents-workflows-the-practical-guide/
- Udemy AI Agents topic page: https://www.udemy.com/topic/ai-agents/
- Udemy MCP topic page: https://www.udemy.com/topic/model-context-protocol-mcp/
- Udemy Claude Code topic page: https://www.udemy.com/topic/claude-code/
- n8n Voice Agents (no-code): https://www.udemy.com/course/n8n-course/
- AI Builder: Agents, Voice Agents in n8n: https://www.udemy.com/course/ai-builder-with-n8n-create-agents-voice-agents/
- Soma, "I Tried 50+ AI Agents Courses on Udemy": https://medium.com/javarevisited/i-tried-50-ai-agents-agentic-ai-courses-on-udemy-here-are-my-top-6-recommendations-for-2026-a73158ce0875
- Class Central, ChatGPT course count: https://www.classcentral.com/report/best-chatgpt-courses/

Open-lane evidence (Udemy listings)
- Full-Stack Voice AI Agent with LiveKit, n8n & MCP on AWS: https://www.udemy.com/course/full-stack-voice-ai-agent-with-livekit-n8n-and-mcp-on-aws/
- Production Voice AI: SIP Telephony LiveKit: https://www.udemy.com/course/livekit-voice-ai-agent/
- AI Voice Agents: Vapi, ElevenLabs, n8n & MCP: https://www.udemy.com/course/ai-voice-agents-automation-with-vapi-elevenlabs-n8n-mcp/
- Voice AI production comparison 2026: https://www.reactify-solutions.com/articles/voice-ai-agents-production-2026
- AB-100 Practice Tests: https://www.udemy.com/course/ab-100-practice-tests-feb-2026-agentic-ai-solution-architect/
- AB-620 Practice Tests: https://www.udemy.com/course/ab-620-practice-tests-2026-ai-agent-builder-associate/
- AI-500 Practice Tests: https://www.udemy.com/course/ai-500-practice-tests-2026-multi-agent-ai-solutions-expert/
- GH-600 Exam Prep: https://www.udemy.com/course/new-gh-600-github-agentic-ai-developer-exam-prep-2026/
- NCP-AAI Mock Exams: https://www.udemy.com/course/professional-agentic-ai-ncp-aai-exams/
- AI-103 Complete Course: https://www.udemy.com/course/ai-103-azure-ai-app-and-agent-developer-complete-course/
- Claude Agent SDK: Build Production AI Agents in Python: https://www.udemy.com/course/claude-agent-sdk-build-production-ai-agents-in-python/
- Extending AI with Agent Skills 2026: https://www.udemy.com/course/ai-agent-skills/
- LangFuse: LLM Observability: https://www.udemy.com/course/langfuse-for-llmops/
- LLM Observability and Cost Management: https://www.udemy.com/course/llm-observability-cost/
- FinOps for Generative AI: https://www.udemy.com/course/finops-for-genai/
- LLM Token Optimization: https://www.udemy.com/course/llm-token-optimization-enterprise-cost-performance/
- Amazon Bedrock AgentCore: https://www.udemy.com/course/amazon-bedrock-agentcore-build-ai-agents-on-aws-hands-on/
- Microsoft Foundry & Python: Enterprise AI Agents on Azure: https://www.udemy.com/course/azure-ai-agents-microsoft-foundry-python/
- Agentic AI for QA Automation with Python: https://www.udemy.com/course/agentic-ai-fundamentals-creating-autonomous-agents/
- AI Agents for Cloud Infrastructure: https://www.udemy.com/course/ai-agents-for-cloud-infrastructure/

Security lane
- Prompt Injection & LLM Defense (2026): https://www.udemy.com/course/prompt-injection-llm-defense-2026/
- OWASP Top 10 for LLM Applications v2026: https://www.udemy.com/course/owasp-top-10-for-llm-applications-2025/
- The Agentic AI Security Masterclass: https://www.udemy.com/course/the-agentic-ai-security-masterclass/
- AI Agent Security for Vibe-Coded Agents: https://www.udemy.com/course/agent-security/
- AI Security Bootcamp: Guardrails, LLM Gateways, Observability: https://www.udemy.com/course/ai-security-bootcamp-guardrailsllm-gatewaysobservability/

Competitors to the existing eval course
- Testing AI Systems with DeepEval (Rahul Shetty): https://www.udemy.com/course/rag-llm-evaluation-ai-test/
- Rahul Shetty AI Testing Learning Path: https://rahulshettyacademy.com/ai-testing-learning-path
- AI Agents, RAG & LLM Evals for Beginners: DeepEval & RAGAS: https://www.udemy.com/course/ai-testing-deepeval-ragas-ollama/
- Production LLM Evaluation And Observability (listing mirror): https://www.psdly.co.uk/udemy-production-llm-evaluation-and-observability
- Build & Test AI Agents with Ollama & Local LLMs: https://www.udemy.com/course/build-ai-agent-chatbot-rag-langchain-local-llm/
- Production AI Agents with LangChain + LangGraph [2026]: https://www.udemy.com/course/production-ai-agents/

Other platforms
- Maven, AI Evals for Engineers & PMs: https://maven.com/parlance-labs/evals
- Maven, Agentic AI for PMs & Engineers: https://maven.com/marily-nika/ai-agent-certification
- Coursera, Agentic AI Engineering: https://www.coursera.org/specializations/agentic-ai-engineering
- Coursera, Agentic AI Protocols (MCP, A2A, ACP): https://www.coursera.org/learn/agentic-ai-protocols-mcp-a2a-acp
- Coursera, AI Agents with Model Context Protocol: https://www.coursera.org/specializations/ai-agents-model-context-protocol
- DeepLearning.AI short courses: https://www.deeplearning.ai/courses?types=short_course
- Scrimba, Best AI Agent Courses 2026: https://scrimba.com/articles/best-courses-to-learn-ai-agents-and-agentic-ai-in-2026/
