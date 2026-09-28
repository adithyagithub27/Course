# Title and Subtitle Options

> Course 4 of the Build → Test → Deploy → Operate series. Udemy limits (verify in the course landing page editor): **title ≤ 60 characters, subtitle ≤ 120 characters**. Every count below comes from `len()` in the Python script at the bottom of this file, so it matches what Udemy's counter shows (spaces and punctuation included). Brief rule applied: the words **"Observability"** and **"Cost"** appear in every title.

## Recommended pair

- **Title (59 chars):** AI Agent Observability & Cost Control: LLMOps in Production
- **Subtitle (119 chars):** Trace, measure and cut the cost of LLM agents with OpenTelemetry, Langfuse, LiteLLM, Prometheus and Grafana. In Python.

**Why this pair:**

- It matches the curriculum's working title (minus the tool names, which move to the subtitle) and reads as the "Operate" step of the series next to *Zero to Production*, *Testing & Evaluation* and *Production Voice AI Agents*.
- The market research says the observability lane now has three small Langfuse courses, so the advice is to "lead with cost/FinOps + OTel angle". "Cost Control" is in the title, "OpenTelemetry" leads the subtitle.
- "LLMOps in Production" carries the job-title keyword (LLMOps) and the "Production" word the research recommends, and avoids "Complete", "Masterclass", "Bootcamp" and "A-Z".
- The subtitle lists the five tools students search for (OpenTelemetry, Langfuse, LiteLLM, Prometheus, Grafana) and ends with "In Python" so no-code learners self-select out.
- Title Option 7 puts "Langfuse" first. Switch to it only if Udemy Marketplace Insights shows strong "Langfuse" search demand relative to "LLM observability" and "LLMOps". The research lists Marketplace Insights checks for "LLM observability" and "AI FinOps" as validation steps still to do.

## Title options (limit 60; must contain "Observability" and "Cost")

| # | Title | Chars | ≤60? | Notes |
|---|---|---|---|---|
| 1 (rec.) | AI Agent Observability & Cost Control: LLMOps in Production | 59 | yes | Series-consistent, leads with the two differentiators (agents, cost), carries "LLMOps" and "Production". |
| 2 | LLM Agent Observability & Cost Control with OpenTelemetry | 57 | yes | Puts OpenTelemetry in the title. Good if OTel search is strong; drops "Production" and "LLMOps". |
| 3 | AI Agent Observability & Cost: Langfuse, OTel and LLMOps | 56 | yes | Tool-name heavy. "OTel" is jargon some searchers won't type. |
| 4 | Observability & Cost Control for AI Agents: LLMOps in Python | 60 | yes | Leads with the topic keyword, adds "Python". Exactly at the limit; no room for edits. |
| 5 | Production LLMOps: AI Agent Observability & Cost Engineering | 60 | yes | "Cost Engineering" is the Section 6 name and sounds senior; less common as a search phrase than "cost control". |
| 6 | AI Agent Observability & Cost Control: Trace, Measure, Save | 59 | yes | Outcome verbs in the tail, mirroring Course 3's "Build, Test, Deploy". Drops "LLMOps". |
| 7 | Langfuse & OpenTelemetry: AI Agent Observability & Cost | 55 | yes | Best if Marketplace Insights shows "Langfuse" as a high-demand term. Risk: depends on one vendor's name. |
| 8 | Operate AI Agents: Observability, Cost Control & Incidents | 58 | yes | Names the series step ("Operate") and the engagement centrepiece (incident labs). "Operate" is not a search term. |

## Subtitle options (limit 120)

| # | Subtitle | Chars | ≤120? |
|---|---|---|---|
| 1 (rec.) | Trace, measure and cut the cost of LLM agents with OpenTelemetry, Langfuse, LiteLLM, Prometheus and Grafana. In Python. | 119 | yes |
| 2 | OpenTelemetry GenAI conventions, Langfuse tracing, token FinOps, latency budgets, online evals, SLOs and incident labs. | 119 | yes |
| 3 | Instrument any LLM agent, cost per session and tenant, cut spend with caching and routing, set SLOs, solve incidents. | 117 | yes |
| 4 | Cost per request, session and tenant. p95 latency. LLM-as-judge on live traffic. Grafana dashboards. CI budget gates. | 117 | yes |
| 5 | Stop the $4,000 weekend: trace every step, attribute every token, route to cheaper models and alert before finance does. | 120 | yes |
| 6 | The Operate course for LLM agents: tracing, token FinOps, reliability, online evals, dashboards, governance, incidents. | 119 | yes |
| 7 | Build the observability stack for an AI helpdesk agent: Langfuse, OTel Collector, Prometheus, Grafana and LiteLLM. | 114 | yes |
| 8 | Hands-on LLMOps in Python: OpenTelemetry + Langfuse tracing, cost showback, prompt caching, routing, SLOs, postmortems. | 119 | yes |

## Suggested pairings

| Title | Best subtitle | Why |
|---|---|---|
| 1 | 1 | Recommended: brand-consistent title, tool-keyword subtitle |
| 2 | 3 | OTel in the title, outcomes in the subtitle |
| 4 | 4 | Topic-first title, metric-first subtitle for engineering managers |
| 6 | 5 | Verb title, story subtitle ("the $4,000 weekend" is lecture 1.1's hook) |
| 7 | 8 | Langfuse-first title, hands-on subtitle |
| 8 | 2 | "Operate" title, curriculum-keyword subtitle |

## Verification output

Output of the script below, run with `python3` on 2026-09-28:

```text
T1:  59/60  OK  AI Agent Observability & Cost Control: LLMOps in Production
T2:  57/60  OK  LLM Agent Observability & Cost Control with OpenTelemetry
T3:  56/60  OK  AI Agent Observability & Cost: Langfuse, OTel and LLMOps
T4:  60/60  OK  Observability & Cost Control for AI Agents: LLMOps in Python
T5:  60/60  OK  Production LLMOps: AI Agent Observability & Cost Engineering
T6:  59/60  OK  AI Agent Observability & Cost Control: Trace, Measure, Save
T7:  55/60  OK  Langfuse & OpenTelemetry: AI Agent Observability & Cost
T8:  58/60  OK  Operate AI Agents: Observability, Cost Control & Incidents
S1: 119/120 OK  Trace, measure and cut the cost of LLM agents with OpenTelemetry, Langfuse, LiteLLM, Prometheus and Grafana. In Python.
S2: 119/120 OK  OpenTelemetry GenAI conventions, Langfuse tracing, token FinOps, latency budgets, online evals, SLOs and incident labs.
S3: 117/120 OK  Instrument any LLM agent, cost per session and tenant, cut spend with caching and routing, set SLOs, solve incidents.
S4: 117/120 OK  Cost per request, session and tenant. p95 latency. LLM-as-judge on live traffic. Grafana dashboards. CI budget gates.
S5: 120/120 OK  Stop the $4,000 weekend: trace every step, attribute every token, route to cheaper models and alert before finance does.
S6: 119/120 OK  The Operate course for LLM agents: tracing, token FinOps, reliability, online evals, dashboards, governance, incidents.
S7: 114/120 OK  Build the observability stack for an AI helpdesk agent: Langfuse, OTel Collector, Prometheus, Grafana and LiteLLM.
S8: 119/120 OK  Hands-on LLMOps in Python: OpenTelemetry + Langfuse tracing, cost showback, prompt caching, routing, SLOs, postmortems.
```

### Script (re-run after any edit)

```python
# check_titles.py: paste the current strings, then run: python3 check_titles.py
titles = [
    'AI Agent Observability & Cost Control: LLMOps in Production',
    'LLM Agent Observability & Cost Control with OpenTelemetry',
    'AI Agent Observability & Cost: Langfuse, OTel and LLMOps',
    'Observability & Cost Control for AI Agents: LLMOps in Python',
    'Production LLMOps: AI Agent Observability & Cost Engineering',
    'AI Agent Observability & Cost Control: Trace, Measure, Save',
    'Langfuse & OpenTelemetry: AI Agent Observability & Cost',
    'Operate AI Agents: Observability, Cost Control & Incidents',
]
subtitles = [
    'Trace, measure and cut the cost of LLM agents with OpenTelemetry, Langfuse, LiteLLM, Prometheus and Grafana. In Python.',
    'OpenTelemetry GenAI conventions, Langfuse tracing, token FinOps, latency budgets, online evals, SLOs and incident labs.',
    'Instrument any LLM agent, cost per session and tenant, cut spend with caching and routing, set SLOs, solve incidents.',
    'Cost per request, session and tenant. p95 latency. LLM-as-judge on live traffic. Grafana dashboards. CI budget gates.',
    'Stop the $4,000 weekend: trace every step, attribute every token, route to cheaper models and alert before finance does.',
    'The Operate course for LLM agents: tracing, token FinOps, reliability, online evals, dashboards, governance, incidents.',
    'Build the observability stack for an AI helpdesk agent: Langfuse, OTel Collector, Prometheus, Grafana and LiteLLM.',
    'Hands-on LLMOps in Python: OpenTelemetry + Langfuse tracing, cost showback, prompt caching, routing, SLOs, postmortems.',
]
for i, t in enumerate(titles, 1):
    ok = len(t) <= 60 and 'Observability' in t and 'Cost' in t
    print(f"T{i}: {len(t):>3}/60  {'OK' if ok else 'FIX'}  {t}")
for i, s in enumerate(subtitles, 1):
    print(f"S{i}: {len(s):>3}/120 {'OK' if len(s) <= 120 else 'TOO LONG'}  {s}")
```

## Rules applied

- No "Complete", "Masterclass", "Bootcamp", "A-Z" or year stamps. A year in a title goes stale and forces a rename.
- No claims like "#1", "best", "first" or "only". The research warns these go stale (it happened to Course 2's differentiation doc), and Udemy's landing page guidelines discourage them (verify current guidelines).
- No emojis, and no ALL CAPS words other than acronyms (AI, LLM, SLO, CI, OTel).
- "$4,000 weekend" in Subtitle 5 refers to lecture 1.1's fictional demo scenario, not a real bill. If it's used, the landing page must make that clear in the first paragraph.
- Third-party names (Langfuse, OpenTelemetry, Prometheus, Grafana, LiteLLM) are used descriptively. No logos on the course image (see `course-image-brief.md`).
