# Udemy Course Description

## AI Agent Observability & Cost Control: LLMOps in Production

> Course 4 of the Build → Test → Deploy → Operate series. Every field matches `01-curriculum/curriculum.md`. Paste each block into the matching field in Udemy's course landing page (description) and intended learners (objectives, requirements, audience) editors. Udemy's rich-text editor accepts **bold**, *italic*, bullet lists and numbered lists. It does not render markdown headings, so section headers below are bold lines. Paste as plain text and re-apply bold in the editor if the formatting doesn't carry over.

---

## Course description (copy-paste ready, 1233 words)

<!-- BEGIN DESCRIPTION -->

**Your agent worked in the demo. Then it ran for a weekend.**

On Friday evening a tool call started failing. The agent retried, added the error to its context, and tried again. Every step made the prompt longer and the bill bigger. Nobody was watching the trace, nobody had set a budget, and nobody had written an alert. By Monday the bill had a comma in it. That scenario opens this course (with a fictional agent and a fictional bill), because it is the most common way LLM agents fail in production: not loudly, but expensively and silently.

**AI Agent Observability & Cost Control** teaches you to see what your agents do, to know what every request costs, and to catch problems before your finance team or your users do. You'll instrument an agent, attribute its cost, hold its latency, evaluate its quality on live traffic, set SLOs, and investigate incidents from traces alone.

**What you'll build: the Atlas Ops Console**

The whole course uses one running project. Atlas is the internal IT and HR helpdesk agent at Northwind Logistics, a fictional company with four departments as tenants. Atlas answers policy questions from a knowledge base, looks up and creates tickets, resets passwords after verification and checks shipment status. A deterministic traffic simulator replays a realistic day of multi-tenant load with injectable incidents (runaway loop, context bloat, retry storm, provider slowdown, prompt regression), so you always have data to look at, even without spending money.

By the end, Atlas has:

- OpenTelemetry traces that follow the GenAI semantic conventions for models, tools and agents, exported to Langfuse and to a local store
- cost attributed to every generation and rolled up per request, session, user, tenant and feature, with a weekly showback report
- prompt caching, a context diet, small-model-first routing with LiteLLM Router and per-tenant budgets, with the saving proven on the same day of traffic
- latency budgets with time-to-first-token and p95 measured, plus timeouts, retries, fallbacks and circuit breakers that hold when a provider slows down
- sampled LLM-as-judge scoring on live traces, user feedback correlated with judge scores, and week-over-week drift detection
- Prometheus metrics, a Grafana dashboard, Langfuse saved views, burn-rate and cost-anomaly alerts, and a runbook
- PII masking in the SDK and the OTel Collector, retention and tenant separation
- a self-hosted stack (Langfuse, OTel Collector, Prometheus, Grafana) in Docker Compose and a CI budget gate that fails a pull request when cost per session or p95 regresses

**What makes this course different**

- **Agents, not just LLM calls.** Most observability content stops at "log the prompt and the completion". Agents loop, call tools, escalate models and blow up context. You'll trace the tool loop step by step and read the waterfall of a runaway agent.
- **Cost is a first-class topic.** Section 6 is the longest section. You'll build a price table you can trust (with cached and reasoning tokens), compute cost per resolved session, and cut Atlas's daily cost by 40% in a challenge, then prove it in the Ops Console.
- **Portable by design.** You emit OpenTelemetry with the GenAI semantic conventions first, then point it at Langfuse. Section 12 sends the same traces to LangSmith and Arize Phoenix and compares OpenLLMetry and Datadog, so you can choose a backend instead of inheriting one.
- **Quality in production, not just in CI.** Online evaluation with DeepEval judges on sampled traffic, feedback that means something, drift reports, and a path from a bad trace back to a regression test.
- **You are on call.** Section 11 gives you three real-shaped incidents as span files and a brief. You investigate first, then watch the reveal. A fourth, unrevealed incident is your project.
- **Failure first, then the fix.** "Break it" demos show orphan spans, double counting, a loop you can only see in a trace, a slow provider during peak and a dead observability backend, each followed by the fix.
- **Build before you watch.** Challenge lectures ask you to build first and check the solution after. The capstone starts with a "build it yourself" gate, and a domain-swap project has you instrument a different agent, so you finish with two portfolio projects.

**Tools and technologies**

- **OpenTelemetry SDK 1.45** and the **GenAI semantic conventions 0.66** (incubating): traces, resource attributes, exporters, the OTel Collector
- **Langfuse 4** (OpenTelemetry-based SDK): observations, sessions, users, prompts, scores, datasets, masking, dashboards
- **OpenInference** auto-instrumentation for OpenAI
- **LiteLLM**: price tables, `cost_per_token`, Router with fallbacks, budgets
- **OpenAI** models (`gpt-4.1-mini` for Atlas, `gpt-4.1` for escalation, `gpt-5-mini` in routing demos), all set through environment variables
- **DeepEval** G-Eval as the online judge
- **Prometheus + Grafana**, **FastAPI**, **Streamlit** (the local Ops Console), **Docker Compose**, **GitHub Actions**
- **LangSmith** and **Arize Phoenix** for the portability section; OpenLLMetry and Datadog LLM Observability conceptually

**How the course is organized**

- **Foundations (Sections 1-3):** the $4,000 weekend, what LLMOps means for agents, setup with spending caps, your first trace in ten minutes, offline mode, and OpenTelemetry with the GenAI semantic conventions
- **See everything (Sections 4-5):** the Langfuse deep dive (observation types, sessions, prompts, scores, datasets, masking) and agent observability patterns (tool loops, RAG spans, streaming, logs vs traces vs metrics)
- **Control cost and latency (Sections 6-7):** token anatomy, price tables, showback, caching, the context diet, routing, budgets and anomaly alerts, then latency budgets, retries, fallbacks, circuit breakers and a chaos demo
- **Operate (Sections 8-11):** online evaluation and drift, SLIs, SLOs, dashboards and alerts, telemetry privacy and governance, and the incident labs
- **Choose and ship (Sections 12-15):** portability and alternatives, self-hosting and CI budget gates, the capstone Atlas Ops Console, a domain-swap project, and a careers lecture on LLMOps, AI platform and AI SRE roles with interview questions

**What you get:** about 10.5 hours of video across 15 sections, a complete GitHub code repository with 401 offline tests, 7 guided labs, 5 build-it-yourself challenges, 2 projects plus a capstone and a domain-swap project, 13 section quizzes, a 40-question practice test, 5 in-browser coding exercises, 4 incident datasets (three with reveal lectures, one you investigate alone), and downloadable cheat sheets, templates and checklists: cost guide, latency budget worksheet, runbook, incident and postmortem templates, telemetry governance checklist, backend decision matrix, production checklist, instrumentation template, GenAI semantic conventions cheat sheet, Langfuse cheat sheet, interview questions, glossary and troubleshooting guide.

**Part of a series.** This is Course 4 in a Build → Test → Deploy → Operate series with *Generative AI & AI Agents: Zero to Production*, *AI Agent Testing & Evaluation* and *Production Voice AI Agents with Python*. It stands on its own, and you don't need the other courses. Where it helps, it points to the testing course for offline evals and to the voice course for latency budgets.

The code targets langfuse 4 and opentelemetry-sdk 1.45. The GenAI semantic conventions are incubating and attribute names may change; the repository README tracks version updates.

Plan on spending about $5-15 in API usage for the whole course: the Langfuse Cloud free tier (or self-host), OpenAI pay-as-you-go with a hard cap, and open-source tools for everything else (prices change; check each provider). Every lab has an offline path, and `OFFLINE=1` runs a full day of traffic through a deterministic mock LLM at zero cost.

If you can call an LLM from Python, this course teaches you to run agents in production without surprises on the bill, the latency chart or the quality report.

<!-- END DESCRIPTION -->

**Description checks**

- Word count: **1233** (Udemy asks for at least 200 words; our target was 300+). Verify the current minimum in the editor.
- Primary keywords appear in the first two paragraphs: *agent*, *production*, *cost*, *trace*, *LLMOps* (title), *observability* (title). Tool keywords appear early in the body: *OpenTelemetry*, *Langfuse*, *LiteLLM*, *Prometheus*, *Grafana*.
- The "$4,000 weekend" is labelled as a fictional scenario in the first paragraph.
- The description has no external links, no coupon codes and no off-platform contact details. Udemy's promotional rules don't allow them in the landing page (verify current policy).
- The description makes no market, competitor or salary claims. The careers lecture (15.2) also has no salary figures.
- Counts match the curriculum: ~10.5 h video (627 min), 15 sections, 7 labs, 5 challenges, 2 projects + capstone + domain swap, 13 quizzes, 40-question practice test, 5 coding exercises, 4 incident datasets. The lecture count (91 video items) is not quoted here because Part A/B splits change what Udemy displays (see `publish-checklist.md` §0).

---

## What you'll learn (Udemy limit: 160 characters each, 4 minimum; verify)

| # | Objective | Chars |
|---|---|---|
| 1 | Instrument any LLM agent with OpenTelemetry traces that follow the GenAI semantic conventions for models, tools and agents | 122 |
| 2 | Use Langfuse to trace sessions, users and tenants, manage prompt versions, score outputs and build datasets from production traffic | 131 |
| 3 | Calculate the true cost of every request, session, user, tenant and feature, and produce a showback report your finance team accepts | 132 |
| 4 | Cut LLM spend with prompt caching, context diets, small-model-first routing and per-tenant budgets, and prove the savings with data | 131 |
| 5 | Set latency budgets, measure time to first token and p95, and add timeouts, retries, fallbacks and circuit breakers that hold under outages | 139 |
| 6 | Run online evaluation on live traffic with sampled LLM-as-judge scoring, user feedback and drift detection | 106 |
| 7 | Define SLIs and SLOs for agents, build Grafana and Langfuse dashboards, and write alert rules and runbooks | 106 |
| 8 | Mask PII in telemetry, set retention, separate tenants and understand logging obligations (not legal advice) | 108 |
| 9 | Investigate real-shaped incidents (cost spike, latency regression, quality drift) from traces alone and find the root cause | 123 |
| 10 | Deploy a self-hosted observability stack with Docker Compose and gate pull requests on cost and latency budgets in CI | 117 |

These are the curriculum's 10 learning outcomes, lightly edited to fit the limit and to add the "not legal advice" flag on objective 8. Paste one per field, without trailing periods.

## Requirements

- Basic Python: functions, decorators, dictionaries, virtual environments (uv or pip), running scripts from a terminal
- You have made at least one LLM API call before (any provider). Sections 1-3 are beginner-safe
- A computer (Windows, macOS or Linux) with Docker Desktop or Docker Engine for Sections 9 and 13 (everything else runs without Docker)
- A free Langfuse Cloud account (or self-host in Section 13) and an OpenAI account with a hard spending cap (Section 2 walks through each)
- About $5-15 of API usage for the whole course (prices change; check each provider). Every lab has an offline path at zero cost
- No prior observability, SRE or Kubernetes experience needed. No Grafana or Prometheus experience needed

## Who this course is for

- Python developers who have shipped an LLM agent or chatbot and now need to answer "what does it cost?", "why is it slow?" and "is it still good?"
- AI engineers and ML engineers moving into LLMOps, AI platform or AI SRE roles
- Backend and platform engineers who own an APM stack (Prometheus, Grafana, Datadog, OpenTelemetry) and are being asked to cover LLM workloads
- Engineering managers and tech leads who need cost per resolved session, SLOs and an incident process for their agents, and want to understand what their team should build
- Students of the instructor's courses *Generative AI & AI Agents: Zero to Production*, *AI Agent Testing & Evaluation* or *Production Voice AI Agents with Python* who want the operate sequel (none is required)
- FinOps and cloud-cost practitioners extending their practice to token spend (Sections 1-3 and 6 are the core for you; the rest is optional depth)

## Who this course is NOT for

> Udemy has no separate "not for" field. Use these as the last lines of the description or in the FAQ-style closing paragraph if you want them public, or keep them for the promo and marketing copy.

- Complete beginners to programming. You need to be comfortable reading and running Python
- People looking for a no-code dashboard product tour. Every section is Python code, YAML and real dashboards you configure yourself
- Anyone wanting to train or fine-tune models. We observe and operate hosted models; we don't train them
- Anyone looking for legal advice on logging or AI regulation. The governance lecture is a practical checklist, not legal counsel
- Anyone wanting a vendor certification course for Datadog, LangSmith or another commercial product. Those are covered for comparison, not for certification

## Verification output

```text
Objective  1: 122/160 OK
Objective  2: 131/160 OK
Objective  3: 132/160 OK
Objective  4: 131/160 OK
Objective  5: 139/160 OK
Objective  6: 106/160 OK
Objective  7: 106/160 OK
Objective  8: 108/160 OK
Objective  9: 123/160 OK
Objective 10: 117/160 OK
Description words: 1233 (target >= 300) OK
```

Re-check after edits with: `python3 -c "import re,sys; t=open(sys.argv[1]).read(); d=t.split('<!-- BEGIN DESCRIPTION -->')[1].split('<!-- END DESCRIPTION -->')[0]; print(len(re.findall(r'\S+', d)))" course-description.md`
