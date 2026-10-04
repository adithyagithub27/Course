# Marketing Positioning

## AI Agent Testing & Evaluation — Course Positioning Strategy

> Refreshed 2026-10-04 per `00-course-strategy/next-course-market-research.md` §6 and fix-plan decision T8: position on **full lifecycle + CI/CD quality gates + enterprise scenarios**. Never claim "first", "only", "nothing else exists" or "the complete" anything. Course facts: 55 lectures, 6 h 40 min, 16 sections, 5 projects (Project 5 is the capstone), 12 labs, offline mode with no API key needed.

---

## 1. Positioning Statement

**For** QA engineers, AI engineers and engineering leads **who** ship AI agents and need to prove they work, **this course** is a hands-on, production-focused program **that** takes one realistic agent through the whole quality lifecycle — test strategy, evaluation metrics, RAG and tool-calling tests, red teaming, tracing, cost, regression, CI/CD quality gates and production monitoring — with DeepEval, RAGAS, promptfoo, Langfuse and OpenTelemetry in one pipeline. **Unlike** courses that go deep on one tool or one stage, **it ends with** a quality gate that blocks a bad pull request and a capstone platform that says SHIP or BLOCK with reasons.

---

## 2. Value Proposition Canvas

### Customer Profile

#### Customer Jobs

| Job Type | Job Description |
|---|---|
| Functional | Ship AI agents that behave reliably in production |
| Functional | Catch hallucinations, wrong tool calls and regressions before users do |
| Functional | Put AI quality checks into existing CI/CD |
| Functional | Show leadership and auditors evidence of quality |
| Social | Become the person on the team who knows how to test AI |
| Emotional | Stop worrying that the next prompt edit breaks something silently |

#### Customer Pains

| Pain | Severity |
|---|---|
| Exact-match tests flake on correct answers; no clear replacement | High |
| Hallucinations found by customers, not tests | High |
| Security gaps (prompt injection, PII leakage, unauthorized tool calls) untested | High |
| No visibility into what the agent did and what it cost | High |
| Many tools, unclear which to use for what | Medium |
| Tutorials stop at "run one metric"; nothing connects to CI and production | Medium |

#### Customer Gains

| Gain | Importance |
|---|---|
| A repeatable evaluation workflow they can apply to any agent | Critical |
| A CI gate that blocks bad changes automatically | High |
| Traces and cost data that explain failures | High |
| Reusable code and templates (test strategy, scorecard) | High |
| A portfolio project for interviews | High |

---

### Value Map

| Feature | What students get |
|---|---|
| 16 sections, 55 lectures, 6 h 40 min | Progressive path from the first failure demo to the capstone |
| One running example (TechCorp support agent) + four more agents | Realistic agents with real failure cases: RAG, six-tool operations agent, banking agent, three-agent reply desk |
| 5 projects + 12 labs | Every technical section ends in code students run themselves |
| Full lifecycle in one pipeline | DeepEval, RAGAS, promptfoo (+ Garak, PyRIT), Langfuse, OpenTelemetry GenAI, MCP contract tests |
| CI/CD quality gates | GitHub Actions workflow: PR comment, merge blocked on failure, nightly capstone |
| Enterprise scenarios | Five scenario datasets (customer support, HR, insurance claims, banking, software engineering), governance and audit trail |
| Offline mode | Every lab, demo and 204 tests run without an API key, with identical numbers |

| Pain | How the course relieves it |
|---|---|
| Flaky tests | Threshold-based metrics and a five-layer test strategy (Modules 2–4) |
| Hallucinations | Faithfulness against the agent's own tool results; regression gate (Modules 3, 11, 12) |
| Security gaps | promptfoo against the real agent and tools, a 16-attack banking matrix, Garak and PyRIT (Module 8) |
| No visibility | Langfuse v4 and OpenTelemetry GenAI traces, cost per trace (Module 9) |
| Tool overload | Each tool introduced for one job, with a comparison where tools overlap |
| Nothing connects | One repo, one agent, one pipeline, from first test to nightly gate |

---

## 3. Competitive Landscape

The eval-and-observability lane on Udemy is no longer empty (research date 2026-09-28; re-verify listings in Udemy Marketplace Insights before launch):

| Course (Udemy) | Overlap | How this course differs |
|---|---|---|
| Testing AI Systems with DeepEval: AI Agents, Chatbots & RAG (Rahul Shetty, remade June 2026) | DeepEval, golden datasets, synthetic data, safety, agent evaluation | Adds RAGAS, red teaming against tools, tracing, cost, CI gates and a capstone platform |
| AI Agents, RAG & LLM Evals for Beginners: DeepEval & RAGAS (with Ollama) | DeepEval + RAGAS + HF Evaluate | Adds security, observability, CI/CD and production monitoring |
| Production LLM Evaluation And Observability | DeepEval + Langfuse, agentic RAG chatbot, pre/post-production | Adds tool-calling and MCP tests, multi-agent tests, red teaming, CI gates, enterprise scenarios |
| LangFuse: LLM Observability, Tracing, Evaluation, Monitoring | Langfuse | Langfuse is one module here, connected to evaluation and CI |
| LLM Observability and Cost Management: Langfuse, Monitoring | Observability + cost | Cost engineering is one module; adds evaluation and security |
| Build & Test AI Agents, ChatBot, RAG with Ollama & Local LLMs | Testing agents with LangChain v1 | Framework-agnostic agents (plain OpenAI tool calling); full lifecycle |
| Production AI Agents with LangChain + LangGraph [2026] | Security, testing, LangSmith sections | Testing is the whole course, not a section |
| Prompt Injection & LLM Defense (2026) | promptfoo, Garak, PyRIT | Red teaming is one module, tied to agent tools and CI |

Off-platform: Maven's "AI Evals for Engineers & PMs" (about $4,200 per cohort, research §2) and free DeepLearning.AI short courses cover evaluation in depth or briefly; this course is self-paced, project-based and connects evaluation to CI and production.

**Where we compete:** breadth across the lifecycle in one pipeline, CI/CD quality gates, enterprise scenarios, a tool-calling agent tested at the trajectory level, and an offline mode that makes every lab free. **Where competitors are stronger:** Rahul Shetty's audience and QA brand; dedicated security courses go deeper on offensive techniques; single-tool courses go deeper on that tool.

---

## 4. Key Messaging Pillars

### Pillar 1: "Test the trajectory, not just the answer"
An agent can say the right thing and do the wrong thing. The course tests tool choice, arguments, order and loops, not only text.
*Proof:* the six failure modes gallery (Lecture 1.4); trajectory tests and MCP contracts (Module 6).

### Pillar 2: "One deleted line, caught in CI"
The running story: a prompt edit makes the agent invent refund terms; a faithfulness check in the CI gate blocks the pull request.
*Proof:* Lecture 0.1 demo; regression demo (pass rate 100% → 70%, Faithfulness 1.00 → 0.25, offline); the PR comment in Lecture 12.2.

### Pillar 3: "The whole lifecycle, one pipeline"
From the first DeepEval test to drift alerts and an audit trail, in one repo with one agent.
*Proof:* the capstone's SHIP/BLOCK gate across functional, security, performance and regression stages.

### Pillar 4: "Enterprise scenarios, free to run"
Banking, insurance, HR, support and engineering scenarios; a red-team matrix with real findings; and an offline mode so every lab runs without an API key.
*Proof:* Project 4 (two findings in the launched SecureBank, verified fix); `05-datasets/enterprise-scenarios/`.

---

## 5. Price Positioning

Udemy list and sale prices are set by the owner and by Udemy promotions (see `MY_DECISIONS_REQUIRED.md`; verify current Udemy pricing rules). Messaging:

- **Self-paced and affordable** compared with cohort courses (Maven's evals cohort is about $4,200, research §2) — state the comparison factually; no "x-times value" multipliers.
- **Total cost transparency:** "No API key needed for the labs. Running them live costs a few dollars in total (verify current pricing)."
- **Udemy's refund policy** applies (verify the current policy wording before quoting it).

Avoid: salary claims, "pays for itself 1,000x", invented incident costs.

---

## 6. Positioning Summary

### One-line positioning

> **Test and evaluate AI agents across the whole lifecycle — metrics, red teaming, tracing and CI/CD quality gates — on realistic enterprise agents, in Python.**

### Elevator pitch (30 seconds)

> One harmless-looking prompt edit can make an agent invent your refund policy, and every unit test stays green. This course shows you how to catch that and everything like it: evaluation with DeepEval and RAGAS, tool-calling and multi-agent tests, red teaming with promptfoo, Garak and PyRIT, tracing with Langfuse and OpenTelemetry, cost and regression checks, and a GitHub Actions gate that blocks the bad pull request. You build five projects on realistic agents and finish with a quality platform that says SHIP or BLOCK — and every lab runs free, without an API key.

### Tagline options

1. "Test your agents before your users do."
2. "Stop shipping agents on vibes. Ship on evidence."
3. "From first eval to CI gate, in one pipeline."
4. "Your agent said the right thing. Did it do the right thing?"

---

*Document version: 2.0*
*Last updated: 2026-10-04*
*Status: Active — guides all marketing communications*
