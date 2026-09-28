# LLMOps, AI Platform and AI SRE Interview Questions

**Used in:** 15.2 (Careers: LLMOps, AI platform and AI SRE roles)

> 12 questions that tend to come up for roles such as *LLMOps engineer*, *AI platform engineer*, *AI SRE*, *AI infrastructure engineer* and *ML/AI engineer with production ownership*, with model answers built from what you did in this course. **No salary figures.** Compensation varies by location, level and company, so research it for your own market. Adapt each answer with **your own numbers** from your capstone (cost per resolved session by tenant, p95, judge scores, the saving you proved), and say whether they came from the offline replay or live traffic.

---

### 1. What's different about observing an LLM agent compared with a normal service?

**Model answer:** A normal service is a request with a status code and a latency. An agent is a run made of steps: several LLM calls, tool calls and retrievals, each with its own cost in tokens, and the run can loop. Classic APM sees the request and the error rate; it doesn't see that step seven re-sent 40k tokens of history or that a tool failed and the agent retried twelve times. So I instrument at the step level with OpenTelemetry and the GenAI semantic conventions (model, token usage including cached and reasoning tokens, tool name, arguments and result, agent and conversation ids) and I treat three things as first-class signals: traces, quality in production and cost. In the course I built this for a helpdesk agent and could answer, from one trace, why it called a tool, with what, what came back, how many steps it took, and where the tokens and the time went.

### 2. How would you tell me what our agent costs, and what would you do with that number?

**Model answer:** I'd attach cost to every generation from a price table I trust (LiteLLM's model cost data with a dated fallback, handling cached input and reasoning tokens correctly), then roll it up per request, session, user, tenant and feature using trace attributes. The number leadership wants is **cost per resolved session by team**, so I also need a "resolved" flag on every run. Then I'd produce a weekly showback that finance accepts, and use it to find the biggest lever: usually re-sent history and retries, not output. In my capstone the showback was [your figures, simulated or live, with the price-table date], and the top recommendation was [yours].

### 3. Give me four ways to cut LLM spend, and tell me how you'd prove each one worked.

**Model answer:** Prompt caching with stable prefixes and a cache key; a context diet (trim history, truncate tool results, summarise, tune retrieval top-k); small-model-first routing with escalation to a larger model on complexity or low confidence; and per-tenant budgets with soft caps that degrade and hard caps that refuse politely. To prove them, I replay the same day of traffic before and after each change and compare cost per session in the dashboard, so the comparison isn't confounded by traffic. In the course challenge I cut a replayed day's cost by about 40% that way and could show which cut contributed what.

### 4. Averages say our agent is fast. Users say it's slow. What's going on and what do you do?

**Model answer:** Averages hide the tail, and agents have long tails because steps add up and retries and fallbacks add whole calls. I'd look at p95 and p99 end-to-end, at time to first token separately (what the user actually feels on a streaming agent), and at steps per request. Then I'd set a latency budget per step and end-to-end, add per-call timeouts, bounded retries with jitter, fallback models with a circuit breaker, and per-tenant concurrency limits, and I'd test it by injecting a slow provider during peak and checking p95 holds. I'd alert on p95 and on fallback rate, not on the mean.

### 5. How do you know the agent is still good in production, when your evals passed before release?

**Model answer:** Offline evals test yesterday's distribution. Production drifts: new intents, prompt and model changes, provider changes. So I run a sampled LLM-as-judge on live traces with agent-specific criteria (resolved, grounded, safe escalation), write the scores back next to the trace, capture user feedback and check it correlates with the judge (watching for survivorship bias in who bothers to rate), track guardrail metrics as time series, and run a weekly drift report comparing score, cost and latency windows. The judge has a cost, so it's sampled and capped and reported as its own line. When something fails, the bad trace becomes a dataset item and a regression test before the next prompt version ships.

### 6. Define SLIs and an SLO for an internal helpdesk agent.

**Model answer:** SLIs: task success (the agent resolved the request without a human), containment, tool error rate, p95 end-to-end latency, cost per resolved session, and judge score. An SLO is a target on one of them over a window, e.g., "95% of sessions resolved within budget over 30 days", which gives an error budget; I alert on burn rate with a fast window for paging and a slow window for tickets rather than on the raw SLI. Cost gets its own anomaly alert per tenant against an EWMA baseline. Every alert has a runbook and an owner, or it's a dashboard panel, not an alert.

### 7. Walk me through investigating a cost spike from traces alone.

**Model answer:** Timeline first: when was the first bad trace, and what changed before it (deploy, prompt label, config, traffic)? Then blast radius: which tenants and features, and is it per-session or volume? Then I write two or three hypotheses before opening a trace, and I compare a bad session with a good one from before the spike: steps, context size per step, retries, model, prompt version. In the course's first incident the pattern was a tool failing for one tenant, no step limit and no budget, so retries looped and the context grew every step. The fix was a step limit, per-tenant caps and bounded retries; the postmortem actions were an alert on steps per session, a cost anomaly alert and a CI gate on cost per session.

### 8. Users are unhappy but every dashboard is green. Where do you look?

**Model answer:** Quality signals, not operational ones. If cost, latency and error rates are normal, something changed in what the agent says. I'd check the prompt version on recent generations, judge scores and feedback over time by tenant, refusal rate, and whether a prompt label was promoted without an eval run. In the course's third incident, prompt v2 went to production without evals, judge scores drifted, and nothing was red because nothing was measuring quality. The fix was a label rollback; the actions were an online judge, prompt version on every generation and an eval gate before promotion.

### 9. How do you keep PII out of your traces, and why does it matter more for agents?

**Model answer:** Agents put user prompts, tool results and retrieved records into the trace, and an online judge sends samples to a third party, so a trace is a copy of your data in another system. I mask in the SDK before export (emails, phones, ids, card numbers → hashes or placeholders so joins still work), mask again in the OTel Collector as defence in depth, redact tool results to what an investigation needs, never put user ids on metric labels, set retention per signal, use a project per environment with role-based access, and give stakeholders dashboards rather than trace access. For regulatory record-keeping I'd bring in counsel; there are obligations that require logging as much as there are rules that limit it, and the answer depends on the use case.

### 10. Why OpenTelemetry instead of just using a vendor's SDK?

**Model answer:** Because traces emitted with OpenTelemetry and the GenAI semantic conventions can go to any backend through the collector: in the course I sent the same agent's traces to Langfuse, LangSmith and Arize Phoenix by changing one exporter line, and I could route to an existing APM like Datadog alongside. What doesn't move is the vendor's model of scores, prompts, datasets and dashboards, so I plan for that. The trade-off is that the GenAI conventions are still incubating and attribute names can change, so I pin versions and use the constants rather than strings.

### 11. What happens to the agent when your observability backend goes down?

**Model answer:** Nothing, if it's built right. The exporter has a bounded queue and a timeout, telemetry is dropped rather than requests, prompt fetches have a fallback, and the judge and drift jobs run out of band. I test it by stopping the backend during a load replay and checking the health endpoint and the request error rate stay flat while an export-failure metric climbs. Telemetry that can take the product down isn't observability, it's a dependency.

### 12. How would you stop a regression in cost or latency from shipping?

**Model answer:** A CI budget gate. The course repo has a deterministic offline replay of a day of traffic against a mock model with realistic usage and latencies; a test replays it on every pull request and fails if cost per session or p95 regresses beyond the budget. It runs without API keys, so it always runs. Live evals run only when secrets are present. Release tags go to the tracing backend so dashboards get annotations. The offline replay is the single most valuable piece of infrastructure in the whole setup, because it makes cost and latency testable.

---

## Portfolio talking points (from your capstone)

- The architecture diagram (OTel → collector → Langfuse + Prometheus/Grafana) and why you chose that backend (decision record from `backend-decision-matrix.md`)
- Your showback report: cost per resolved session by tenant, with the price-table date and "simulated" or "live" labelled
- The saving you proved and how you proved it (same replay, before/after)
- p95 before and after the chaos demo; the fallback rate
- Your three postmortems (and the fourth from Project 2), with action items mapped to instrumentation, budgets and tests
- The CI budget gate failing a deliberately bad PR
- The domain-swap project (14.6): proof the stack transfers to a different agent

## Pitching observability to management (15.2 summary, no figures)

1. **Lead with the number they're already asked for:** cost per resolved session by team, and whether it's going up or down.
2. **Frame the work as risk reduction with a story:** the weekend cost spike nobody saw (simulated in the course, common in practice), what it would have cost at your traffic, and the three controls that stop it (step limit, budget, alert).
3. **Show the before/after from a replay,** not a projection.
4. **Ask for the smallest first step:** instrumentation and a dashboard, then budgets, then the CI gate. Each step pays for the next.
