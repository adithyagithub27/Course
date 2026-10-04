# LinkedIn and X Launch Posts (12)

> Schedule: posts 1-7 pre-launch (W-4 to W-1), 8-10 launch week, 11-12 post-launch. See `launch-plan.md`.
> Rules: no invented numbers. Every dollar figure below comes from the course's traffic simulator against a dated price table and must be labelled "simulated" where it appears. The only market figures allowed come from `../../00-course-strategy/next-course-market-research.md`, and they must be re-verified before posting. No personal claims without real credentials. Coupons only where current Udemy rules allow (verify). Put links in the first comment on LinkedIn (reach) and in the reply on X.
> Each post has a LinkedIn version (LI) and an X version (X, ≤ 280 chars per post or a short thread).

---

## Post 1: The problem (W-4)

**LI**
```
Your agent worked in the demo.

Then it ran for a weekend.

Friday evening a tool call started failing. The agent retried. Each retry added the error to its context. Each step made the prompt longer and the bill bigger.

Nobody was watching the trace. Nobody had set a budget. Nobody had written an alert.

That's a simulated run from a course I've been building, but the pattern is real: agents don't fail loudly. They fail expensively and silently.

Over the next few weeks I'll share how to see what your agents do, what they cost, and how to stop the weekend before it starts.

#LLMOps #AIAgents #Observability #Python
```
**X**
```
Your agent worked in the demo. Then it ran for a weekend.

A tool call failed. The agent retried. Every retry made the prompt longer and the bill bigger. Nobody was watching.

(Simulated run, real pattern.) Agents fail expensively and silently. Thread over the next few weeks on how to see it coming.
```

## Post 2: Meet Atlas (W-4, with video #1)

**LI**
```
Meet Atlas, an IT and HR helpdesk agent for a (fictional) logistics company.

Atlas:
→ answers policy questions from a knowledge base
→ looks up and creates tickets
→ resets passwords after verification
→ checks shipment status
→ serves four departments as tenants

Next to it sits "the swarm": a traffic simulator that replays a realistic day of load, deterministically, with incidents you can inject on demand: a runaway loop, context bloat, a retry storm, a slow provider, a prompt regression.

Every lab in the course runs against it, so you always have data to look at, even offline.

Full walkthrough on YouTube (link in comments).

#LLMOps #AIAgents #Python
```
**X**
```
Meet Atlas: an IT/HR helpdesk agent for a fictional logistics company. Four tenants, five tools.

Next to it: a traffic simulator that replays a full day of load with injectable incidents (loop, context bloat, retry storm, slow provider, prompt regression).

Walkthrough below.
```

## Post 3: What an agent trace must answer (W-3)

**LI**
```
A trace of an LLM call tells you what went in and what came out.

A trace of an AGENT has to answer more:

1. Why did it call that tool?
2. With what arguments?
3. What came back?
4. How many steps did it take?
5. Where did the tokens go?
6. Where did the time go?

If your observability can't answer all six from one screen, you'll find out the answers on the invoice instead.

OpenTelemetry's GenAI semantic conventions give you attribute names for operations, models, token usage, tool calls and agents. Use them and any backend can read your traces.

(They're incubating, so names may change. Pin your versions.)

#Observability #OpenTelemetry #LLMOps
```
**X**
```
An agent trace must answer 6 questions:

1 Why that tool?
2 With what args?
3 What came back?
4 How many steps?
5 Where did the tokens go?
6 Where did the time go?

If your traces can't, the invoice will. OpenTelemetry's GenAI semconv gives you the attribute names. (Incubating; pin versions.)
```

## Post 4: Token anatomy (W-3, with the free cheat sheet)

**LI**
```
"How much does our agent cost per request?" sounds like one number.

It isn't. Take one request apart:

- input tokens (the prompt, plus every previous turn you re-send)
- output tokens
- cached input tokens (cheaper, if your prefix is stable)
- reasoning tokens (on reasoning models, billed as output)
- tool-call overhead (schemas in, arguments out)
- retries (the whole thing again)
- judge calls (if you evaluate in production)

Then roll it up: per request, per session, per user, per tenant, per feature.

The number your manager actually wants is cost per RESOLVED session, by team. That needs every one of those pieces attributed correctly.

I put the GenAI semantic conventions attributes for all of this on a one-page cheat sheet (link in comments).

#LLMOps #FinOps #AIAgents
```
**X**
```
"Cost per request" isn't one number:

input · output · cached input · reasoning · tool schemas · retries · judge calls

Roll it up per session, user, tenant, feature.

The number your manager wants: cost per RESOLVED session, by team. Cheat sheet below.
```

## Post 5: The cheapest win (W-2)

**LI**
```
The cheapest cost cut for most LLM agents isn't a cheaper model.

It's a stable prompt prefix.

If your system prompt, tool schemas and knowledge context come first and don't change between requests, the provider can serve them from cache at a lower price. If you put the timestamp or the user's name at the top, you've broken the cache for everyone.

How to check: read the cached-token field in the usage object, and chart cached vs uncached input tokens per day.

In the course, students replay the same day of traffic before and after making prefixes stable and compare the two bills. (Simulated traffic, dated price table.) It's the first of four cuts they stack: caching, a context diet, small-model-first routing and per-tenant budgets.

#LLMOps #PromptCaching #FinOps
```
**X**
```
Cheapest LLM cost cut: not a cheaper model. A stable prompt prefix.

System prompt + tool schemas + context first, unchanging → served from cache at a lower price. Timestamp at the top → cache broken for everyone.

Check: the cached-token field in usage. Chart it daily.
```

## Post 6: Why averages lie (W-2)

**LI**
```
"Average latency is 1.8 seconds."

Fine. And the slowest 5% of your users are waiting 9 seconds, and they are the ones who write the tickets.

For agents, latency budgets need three things:

1. Per-step AND end-to-end budgets. An agent that takes six steps at 1 s each feels slow even if every step is "fast".
2. p95, not the mean. Set your alerts on p95.
3. Time to first token, separately. A streaming agent that starts talking in 400 ms feels fast even if it finishes in 4 s.

Then add timeouts, bounded retries with jitter, fallbacks and a circuit breaker, and test them by injecting a slow provider during your peak hour. If p95 holds, you're done. If it doesn't, you found out on a Tuesday afternoon instead of during the outage.

#SRE #LLMOps #Latency
```
**X**
```
"Average latency is 1.8 s."

And p95 is 9 s, and those users write the tickets.

Agent latency budgets:
1 per-step AND end-to-end
2 p95, not mean
3 time to first token, separately

Then: timeouts, bounded retries, fallbacks, circuit breaker. Test by injecting a slow provider at peak.
```

## Post 7: Teaser (W-1)

**LI**
```
Next week I'm releasing the fourth course in my Build → Test → Deploy → Operate series.

It's the Operate one: AI Agent Observability & Cost Control.

You'll instrument an agent with OpenTelemetry and Langfuse, attribute every token to a session and a tenant, cut a day's spend and prove it, hold p95 through a provider slowdown, run an LLM judge on live traffic, set SLOs and alerts, mask PII in telemetry, and then sit on call for three incidents where you only get the traces.

Everything runs offline against a deterministic traffic simulator, so the course costs about $5-15 in API usage (prices change; check your provider).

If you've ever been asked "what does the agent cost?" and had to guess, this is for you.

#LLMOps #Observability #AIAgents
```
**X**
```
Next week: course 4 of my Build → Test → Deploy → Operate series.

Operate = AI Agent Observability & Cost Control.

OpenTelemetry + Langfuse tracing, cost per session/tenant, latency budgets, online evals, SLOs, PII masking, and 3 incidents where you only get the traces.
```

## Post 8: Launch (W0, D0)

**LI**
```
It's live: AI Agent Observability & Cost Control: LLMOps in Production.

What you build across 15 sections:

→ OpenTelemetry traces with the GenAI semantic conventions, exported to Langfuse
→ Cost attributed per request, session, user, tenant and feature, plus a showback report
→ Prompt caching, a context diet, LiteLLM routing and per-tenant budgets, with the saving proven on the same day of traffic
→ Latency budgets, TTFT and p95, timeouts, retries, fallbacks and circuit breakers
→ Sampled LLM-as-judge on live traffic, feedback, drift detection
→ Prometheus, Grafana, SLOs, burn-rate alerts and runbooks
→ PII masking in the SDK and the OTel Collector
→ Three incident labs: investigate from traces first, then the reveal
→ Langfuse, LangSmith, Phoenix, OpenLLMetry and Datadog compared
→ Self-hosted stack in Docker Compose and a CI gate that fails a PR on cost or p95

About 10.5 hours of video, a full repo with 401 offline tests, 7 labs, 5 challenges, a capstone.

Launch coupon in the first comment.

#LLMOps #Observability #AIAgents #Python
```
**X**
```
Live: AI Agent Observability & Cost Control: LLMOps in Production.

OTel GenAI semconv → Langfuse. Cost per session/tenant. Caching, routing, budgets. p95 under chaos. LLM judge on live traffic. SLOs + alerts. 3 incident labs. Docker Compose stack. CI budget gate.

~10.5 h. Coupon below.
```

## Post 9: The incident labs (W0, D2)

**LI**
```
The section I'm proudest of has no code-along.

Section 11: You are on call.

You get a folder of spans and a one-paragraph brief. "Monday 08:15. Cost on one tenant is several times normal. Nothing else is alerting."

Eight minutes. Find root cause.

Then the reveal, and the postmortem, and turning every finding into a budget, an alert or a test.

There are three incidents (a cost spike, a latency regression, a quality drift where nothing is red) and a fourth that's never revealed. You submit that postmortem as a project.

Reading a trace under pressure is a different skill from building one. Most courses only teach the second.

#SRE #LLMOps #IncidentResponse
```
**X**
```
My favourite section has no code-along.

"Monday 08:15. Cost on one tenant is several times normal. Nothing else is alerting. Here are the spans. 8 minutes."

Three incidents: cost spike, latency regression, quality drift with nothing red. A 4th is never revealed. You write the postmortem.
```

## Post 10: Demo clip (W0, D4-D6)

**LI**
```
Left: an agent hits a tool error and retries in a loop. The context grows every step. The cost meter climbs.

Right: the same run with a step limit, a per-tenant budget and an alert. It stops after three steps and says so.

Same code path. Fifteen lines of difference.

(Simulated traffic against a dated price table. The bill on the left is not real. The pattern is.)

The full walkthrough is lecture 1.1 of the course and it's a free preview.

#LLMOps #AIAgents #Observability
```
**X**
```
Left: tool error → retry loop → context grows → cost meter climbs.
Right: same run + step limit + budget + alert → stops at 3 steps.

15 lines of difference. (Simulated bill, real pattern.) Free preview lecture below.
```

## Post 11: Learnings (W+1)

**LI**
```
One week after launch, the questions in Q&A tell me where the real gaps are:

1. "Which attribute do I use for cached tokens?" The GenAI semantic conventions are incubating, and the names are not obvious. Cheat sheet updated.
2. "Docker on Apple Silicon." The self-hosted stack needed a note. Added.
3. "Can I skip Langfuse Cloud entirely?" Yes. OFFLINE=1 replays a full day into the local store and the Ops Console, and Section 13 self-hosts.
4. "Does this work with LangGraph / the OpenAI Agents SDK / my framework?" Yes, if your framework lets you wrap calls in spans. The instrumentation template in the resources is framework-agnostic on purpose.

Keep the questions coming. Several of them are becoming lectures.

#LLMOps #Observability
```
**X**
```
Week 1 Q&A themes:

1 "Which gen_ai attribute for cached tokens?" (cheat sheet updated)
2 Docker on Apple Silicon (note added)
3 "Can I skip Langfuse Cloud?" (yes: OFFLINE=1 + self-host)
4 "Does this work with my framework?" (yes; the template is framework-agnostic)
```

## Post 12: Results and reflection (W+3)

**LI**
```
Three weeks in. What I've learned building and launching an observability course:

- The offline path was the best decision in the course. Students who can replay a day of traffic for free actually replay it, repeatedly, and that's where the learning happens.
- "Cost per resolved session by tenant" is the phrase that lands with engineering managers. Not "observability", not "tracing". The outcome number.
- The incident labs generate more Q&A than every code-along combined. People want to be tested.
- The scariest lecture to record was the governance one, because the honest answer to most regulatory questions is "verify with counsel". I said that on screen and nobody has complained.

The Build → Test → Deploy → Operate series is now complete. Thank you to everyone who took the earlier courses and told me what they needed next.

#LLMOps #Observability #AIAgents
```
**X**
```
3 weeks after launching an LLM observability course:

- the offline replay path was the best decision
- "cost per resolved session by tenant" is what lands with managers
- incident labs generate more Q&A than every code-along combined

Build → Test → Deploy → Operate is now complete.
```

---

## Posting checklist

- [ ] Every dollar figure is labelled "simulated" or is a range with "prices change"
- [ ] No student counts, revenue, rating claims or salary figures
- [ ] Market figures (if any) come from the research doc and were re-verified this month
- [ ] No "first", "only", "best"
- [ ] Coupon links in comments/replies only, and only where Udemy rules allow (verify)
- [ ] Code or attribute names shown in images match curriculum §6
- [ ] Screenshots of Langfuse/Grafana follow the recording guide (no keys, project ids or org names)
