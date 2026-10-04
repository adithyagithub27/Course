# Udemy Course Listing

## AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python

> Positioning follows `00-course-strategy/next-course-market-research.md` §6 and fix-plan decision T8: full lifecycle + CI/CD quality gates + enterprise scenarios. No "first", "only" or "comprehensive first" claims. Numbers match `01-curriculum/full-curriculum.md`: **55 lectures, 6 h 40 min of video, 16 sections (Modules 0–15), 5 projects (Project 5 is the capstone), 12 labs**.

---

## Course Title

**AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python**

---

## Subtitle

Test and evaluate AI agents end to end: DeepEval, RAGAS, promptfoo, Langfuse, OpenTelemetry and CI/CD quality gates in Python.

---

## Course Description

> Copy-paste ready for the Udemy course description field.

Your AI agent passed every demo. Then someone "tidied up" one line of its system prompt. The agent stopped checking the knowledge base and started telling customers a 14-day refund window that doesn't exist. Every unit test stayed green.

Traditional testing was built for deterministic code. AI agents are non-deterministic, multi-step, tool-calling systems: the same question gets different words, the wrong tool, or a confident made-up answer. This course gives you a complete, repeatable way to test them — from your first evaluation to a quality gate that blocks bad pull requests and monitoring that catches drift after release.

**What you'll build**

You work on one realistic running example — **TechCorp's customer support agent** (five tools: account lookup, knowledge-base search, tickets, email, escalation) — plus four more agents along the way: a RAG policy assistant, a six-tool operations agent, a banking agent you red team, and a three-agent reply desk. Five projects:

1. **Project 1 — Evaluate a customer support agent:** a 10-case golden dataset, Answer Relevancy, Faithfulness and a custom correctness metric with DeepEval, and a pass/fail report by category
2. **Project 2 — Diagnose a RAG agent:** RAGAS 0.4 metrics on 15 policy questions in three domains, retrieval vs generation diagnosis, and a fix
3. **Project 3 — Test a multi-tool agent:** tool selection, arguments, error handling and authorization for a six-tool operations agent, plus MCP contract tests
4. **Project 4 — Red team a banking agent:** a 16-attack matrix with promptfoo and a Python runner, two real findings in the launched version, and a verified fix
5. **Project 5 — Capstone: an agent quality platform:** functional, security, performance and regression stages, a five-rule SHIP/BLOCK gate, a Streamlit dashboard, Langfuse tracing and a nightly GitHub Actions run

**What makes this course different**

Several good courses now teach DeepEval, RAGAS or Langfuse. This one is built around the **whole quality lifecycle in one pipeline**:

- **Full lifecycle:** test strategy → evaluation metrics → RAG and tool-calling tests → multi-agent tests → red teaming → tracing → performance and cost → regression and synthetic data → CI/CD gates → production monitoring and governance
- **CI/CD quality gates:** a GitHub Actions workflow that runs your evaluation on every pull request, comments the results and blocks the merge when quality drops
- **Enterprise scenarios:** five scenario datasets (customer support, HR, insurance claims, banking, software engineering) and agents that behave like real ones, including the failure cases
- **Security beyond one tool:** promptfoo against the real agent and its tools, plus a lecture comparing Garak and PyRIT
- **Runs without an API key:** an offline mode with a deterministic mock model and judge runs every lab, demo and the 204-test suite for free; add a key to run the same code live

**Tools & technologies**

- **DeepEval** — pytest-style evaluation, G-Eval custom metrics, tool correctness, the Synthesizer
- **RAGAS** — RAG metrics (faithfulness, answer relevancy, context precision, context recall)
- **promptfoo**, plus **Garak** and **PyRIT** — red teaming and security testing
- **Langfuse** and **OpenTelemetry GenAI conventions** — tracing, cost per trace, scores
- **MCP** — contract tests for agent tools
- **GitHub Actions**, **Streamlit**, **pytest**, **Python 3.11+**, **OpenAI** models (gpt-4.1-mini agent, gpt-4.1 judge)

**Course structure (16 sections, 55 lectures)**

- **Section 0 — Welcome & Course Overview:** a real agent failure, the roadmap, environment setup
- **Section 1 — AI Agents: What You Need to Know for Testing:** tokens, the agent loop, the six ways agents fail
- **Section 2 — Why Traditional Testing Breaks:** non-determinism, five quality dimensions, a five-layer test strategy
- **Section 3 — Your First Agent Evaluation:** DeepEval, golden datasets, Project 1
- **Section 4 — Evaluation Metrics Deep Dive:** LLM and agent metrics, LLM-as-judge, G-Eval
- **Section 5 — RAG Agent Evaluation:** RAGAS, retrieval vs generation, Project 2
- **Section 6 — Testing Tool Calling & MCP:** tool tests, MCP contracts, Project 3
- **Section 7 — Multi-Agent System Testing:** hand-offs, loops, failure injection
- **Section 8 — Security Testing & Red Teaming:** threat model, promptfoo, PII, Project 4, Garak and PyRIT
- **Section 9 — Agent Observability & Tracing:** Langfuse, OpenTelemetry GenAI spans
- **Section 10 — Performance & Reliability Testing:** benchmarks, reliability, cost engineering
- **Section 11 — Regression Testing & Synthetic Data:** baselines, regression gates, DeepEval Synthesizer
- **Section 12 — CI/CD for Agent Evaluation:** quality gates, GitHub Actions, dashboards
- **Section 13 — Production Monitoring & Governance:** drift, audit trails, leadership scorecards
- **Section 14 — Enterprise Capstone:** the agent quality platform, Project 5
- **Section 15 — Career & Next Steps:** interview questions, a 30-day practice plan

Every technical section has a hands-on lab or project with real code you run yourself. You leave with a working repository, reusable templates (test strategy, quality scorecard) and a portfolio project.

---

## Learning Objectives

> Udemy format: "By the end of this course, you will be able to..."

1. Design a test strategy for a non-deterministic AI agent using six failure modes, five quality dimensions and a five-layer agent eval pyramid
2. Build evaluation suites with DeepEval and pytest, using golden datasets and threshold-based metrics
3. Measure answer relevancy, faithfulness, hallucination and correctness, and build custom G-Eval metrics calibrated against human labels
4. Evaluate RAG agents with RAGAS and tell retrieval failures from generation failures
5. Test tool calling: selection, arguments, order, error handling, authorization and MCP contracts
6. Test multi-agent systems with hand-off validation, loop detection and failure injection
7. Red team agents for prompt injection, jailbreaks, PII leakage and unauthorized actions with promptfoo, and know when to add Garak or PyRIT
8. Trace agents with Langfuse and OpenTelemetry GenAI conventions and find the failing step and the cost hotspot
9. Benchmark latency and cost and cut cost with model routing and prompt optimization while re-checking quality
10. Catch regressions with stored baselines and scale test data with synthetic generation
11. Wire evaluation into GitHub Actions with a quality gate that comments on pull requests and blocks bad changes
12. Monitor agents in production for drift and report quality to leadership with a scorecard and an audit trail

---

## Target Audience

### Who This Course Is For

- **QA engineers and SDETs** moving into AI testing — your testing instincts transfer; this course adds the AI-specific methods
- **AI/ML engineers** who ship agents and LLM applications and want a systematic way to prove quality
- **Software developers** building LLM-powered features who need reliability and safety before production
- **DevOps and platform engineers** adding AI quality checks to CI/CD
- **Engineering managers and tech leads** setting AI quality standards, gates and reporting for their teams

### Who This Course Is NOT For

- Complete programming beginners (you need basic Python)
- Researchers looking for theoretical ML evaluation (this course is applied and production-focused)
- People looking for a no-code AI course (you write and run real Python)

---

## Prerequisites

- **Basic Python** — functions, classes, installing packages. Comfort with a terminal.
- **Basic understanding of APIs** — what an API call is. LLM and agent concepts are taught from the ground up.
- **A computer with Python 3.11+** — Windows, macOS or Linux. Node.js 20+ for the promptfoo lectures.
- **An OpenAI API key is optional** — every lab runs in offline mode for free. With a key, running the labs live costs a few dollars in total (verify current pricing; set a spending limit).
- **No prior AI/ML experience required.**

---

## Welcome Message

> Displayed when a student enrolls.

Welcome to **AI Agent Testing & Evaluation**!

How to get the most out of the course:

1. **Set up first:** follow Lecture 0.2 (Course Roadmap & Environment Setup) and run `make test` before Section 1. No API key needed.
2. **Code along:** every demo runs from the course repository; type the lab code yourself.
3. **Do the projects:** Projects 1–4 build the skills, Project 5 (the capstone) is your portfolio piece.
4. **Ask in Q&A:** if you're stuck, post the command you ran and the output you got.

See you in Lecture 0.1.

---

## Completion Message

> Displayed when a student finishes the course.

Congratulations — you've completed **AI Agent Testing & Evaluation**!

You can now:

- Evaluate AI agents with real metrics, not vibes
- Catch hallucinations, security gaps and regressions before they reach production
- Put a quality gate in CI and monitor quality after release

**Next steps:**

1. Finish the capstone if you haven't — it's the best portfolio piece from the course
2. Apply one pattern at work this week: one agent, one golden dataset, one gate
3. Follow the 30-day practice plan (Lecture 15.2 resource)
4. Leave a review — it helps other engineers find the course

Thank you for learning with me.

---

## Instructor Bio

> Short version for the course listing. Owner to personalise (see `MY_DECISIONS_REQUIRED.md`).

I build AI systems that have to work in production, not just in demos. This course teaches the evaluation, red-teaming and monitoring practices I use to decide whether an agent is ready to ship — with every lecture backed by code you can run.

---

*Document version: 2.0*
*Last updated: 2026-10-04 (positioning refresh T8, real lecture count and runtime T7)*
*Status: Draft for Udemy upload — verify Udemy listing rules and character limits before pasting*
