# Lecture Descriptions

> One Udemy lecture description for every item in `01-curriculum/curriculum.md` (105 items: 76 video lectures, 7 labs, 5 challenges, 3 assignments/projects, 14 quizzes incl. the practice test). Paste into each lecture's **Description** field. Where the curriculum splits a long lecture into Part A / Part B uploads (6.3, 6.6, 11.2, 11.3, 11.4, 14.2, 14.3), use the same description for both parts and add "Part A:" or "Part B:" at the start; for the three incident challenges, Part A is the investigation and Part B is the reveal. Descriptions say what the student will do or learn. **No links, coupons or promotion** (Udemy rules; verify). The only exception is 15.4, the bonus lecture, and its links go in the lecture itself under Udemy's bonus-lecture rules.

> Type key: DM demo, SL slides, SC screencast, TH talking head/avatar, LAB lab, CH challenge (pause, then solution), QZ quiz/practice test, AS assignment/project.

## Section 1: Welcome: The $4,000 Weekend

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 1.1 | The $4,000 weekend: watch an agent burn money in real time | DM | 5 | Watch Atlas hit a tool error, retry in a loop and grow its context on every step while a live cost meter climbs (simulated traffic). Then watch the same run with a step limit, a budget guard and an alert. By Section 14 you'll be able to see, explain and stop this. |
| 1.2 | What LLMOps means for agents (and why MLOps tools miss it) | SL | 8 | Learn why agents are different to operate: non-deterministic, multi-step, tool-using and token-metered. You'll meet the three pillars of the course (traces, quality in production, cost) and see exactly where classic APM stops. |
| 1.3 | The observability stack you will build | SL | 7 | Tour the stack: OpenTelemetry as the wire format, Langfuse as the LLM-native backend, Prometheus and Grafana for metrics, LiteLLM for cost and routing. You'll see why emitting OpenTelemetry first keeps every backend swappable. |
| 1.4 | Meet Atlas and the swarm | SC | 7 | Meet Atlas, the IT and HR helpdesk agent for the fictional Northwind Logistics, its tools and tenants, and the traffic simulator that replays a day of load with injectable incidents. You'll see why every lab has an offline path. |
| 1.5 | Course roadmap and how to get the most out of it | SC | 6 | Tour the 15 sections and the repo README. You'll set up a build log, learn how to ask questions in Q&A so you get fast answers, and note the version banner (langfuse 4 / otel 1.45) that every code lecture carries. |
| 1.6 | Quiz: Foundations | QZ | 3 | Six questions on the three pillars, what agents add to observability, and the roles of OpenTelemetry, Langfuse, Prometheus and LiteLLM in the stack. |

## Section 2: Setup and Your First Trace in 10 Minutes

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 2.1 | Accounts, keys and spending caps | SC | 7 | Create a Langfuse Cloud project on the free tier (or plan to self-host later), an OpenAI project with a hard spending cap, and your .env. You'll see what the course costs (about $5-15; prices change) and how to keep it there. |
| 2.2 | Project setup with uv and the Makefile | SC | 6 | Install the project with uv, run the offline unit tests until they're green and start Atlas with make run. The Makefile targets you'll use all course (swarm, replay, console, eval, budget-check) are introduced here. |
| 2.3 | Quick win: one request, one trace | SC | 8 | Send one question to Atlas with curl and open the trace in Langfuse: the agent span, the retriever span, the generation with usage and cost, and the tool span. The rest of the course explains and improves this one screen. |
| 2.4 | Offline mode: a full day of traffic for free | SC | 8 | Run OFFLINE=1 make replay to fill the local store and Langfuse with a full day of spans from the deterministic mock LLM, then open the Streamlit Ops Console. You'll always have data to look at without spending money. |
| 2.5 | Lab 1: Environment and first trace | LAB | 4 | Work through the environment checklist (Python version, uv, keys, Langfuse project, offline replay) and capture a screenshot of your first trace. |
| 2.6 | Quiz: Setup and tracing basics | QZ | 2 | Five questions on spending caps, offline mode, the Makefile targets and what the first trace contains. |

## Section 3: Tracing Fundamentals and the GenAI Semantic Conventions

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 3.1 | Traces, spans and context in five minutes | SL | 6 | Learn the vocabulary: trace, span, parent and child, attributes, events, status, context propagation and sampling. Everything later in the course is built from these pieces. |
| 3.2 | Code-along: manual OpenTelemetry instrumentation of Atlas | SC | 10 | Code along to set up a TracerProvider with resource attributes (service.name, deployment.environment), open spans with start_as_current_span, and export first to the console and then over OTLP. |
| 3.3 | GenAI semantic conventions: naming things so tools understand them | SL | 8 | Learn the gen_ai.* attributes for operations, models, token usage (including cache reads), tool calls, agents and conversations, and why using them buys you portability. The conventions are incubating, and you'll learn how to handle renames. |
| 3.4 | Code-along: tag every LLM, tool and agent span correctly | SC | 9 | Apply the genai_attrs helpers in the agent loop and the tools so every LLM, tool and agent span carries the right attributes, then verify the output in the console exporter. |
| 3.5 | Auto-instrumentation with OpenInference | SC | 6 | Add OpenInference's OpenAI instrumentor with one call and see what you get for free, then learn when manual spans still matter. You'll also hear why the course uses OpenInference rather than the otel-contrib OpenAI instrumentor. |
| 3.6 | Break it: orphan spans, missing context and double counting | DM | 6 | See three broken traces and fix each one: an async task that lost its context, a tool span outside the agent span, and an instrumentor applied twice. Each fix becomes an integration test. |
| 3.7 | Lab 2: Instrument a new tool end to end | LAB | 4 | Add spans with correct GenAI attributes to the check_shipment tool and assert them in a test using the in-memory exporter. |
| 3.8 | Quiz: Tracing and semantic conventions | QZ | 3 | Six questions on spans and context, the gen_ai.* attributes and auto- versus manual instrumentation. |

## Section 4: Langfuse Deep Dive

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 4.1 | How Langfuse sits on OpenTelemetry | SL | 6 | Understand Langfuse SDK v4 as an OpenTelemetry exporter plus semantics: observation types (agent, tool, generation, retriever, guardrail, chain), traces, sessions, users, environments and releases. |
| 4.2 | Code-along: @observe and observation types | SC | 9 | Code along with the @observe decorator and its observation types, get_client(), update_current_generation for model, usage and cost details, and propagate_attributes for session, user, tags and metadata. |
| 4.3 | Sessions, users, tenants and tags: slicing production | SC | 7 | Map Northwind's departments to tags and metadata, employees to user_id and conversations to session_id, then filter production traffic by each in the Langfuse UI. |
| 4.4 | Prompt management and versions | SC | 8 | Create prompts with labels (production, staging), fetch them with a fallback and a cache, and link generations to prompt versions. This lecture sets up Incident 3. |
| 4.5 | Scores, datasets and the feedback loop | SC | 8 | Score traces from code, create scores by trace id, and promote traces into dataset items. You'll see how production traffic becomes your next regression suite. |
| 4.6 | Masking, sampling and cost of observability itself | SC | 6 | Add a mask function, set a sample rate, block noisy instrumentation scopes and flush and shut down cleanly. You'll learn what observability itself costs and how to keep it in check. |
| 4.7 | Challenge: add a guardrail observation | CH | 6 | Pause the video and wrap the injection check as a guardrail observation with a boolean score from the spec on screen, then compare your version with the solution and the two common mistakes. |
| 4.8 | Quiz: Langfuse | QZ | 5 | Eight questions on observation types, sessions and users, prompt labels, scores, datasets and masking. |

## Section 5: Agent Observability Patterns

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 5.1 | What an agent trace must answer | SL | 6 | Learn the six questions an agent trace must answer: why it called that tool, with what, what came back, how many steps it took, where the tokens went and where the time went. |
| 5.2 | Code-along: tracing the tool loop step by step | SC | 9 | Add step spans, tool spans with redacted arguments and results, a step-limit event and the escalation model as a child generation, so a whole agent run reads as one waterfall. |
| 5.3 | RAG spans: retrieval quality is a production metric | SC | 7 | Instrument the retriever with query, top-k and scores, track the empty-result rate and add a grounding flag, so retrieval quality shows up in production, not just in offline evals. |
| 5.4 | Streaming: time to first token and tokens per second | SC | 7 | Measure time to first token and time per output token from stream events, record the time-to-first-chunk attribute and Langfuse's completion start time, and see why streaming changes what "latency" means. |
| 5.5 | Logs vs traces vs metrics for agents | SL | 6 | Learn when to write a structured log with a trace id, when to emit a metric instead of a span, and how to avoid cardinality traps such as putting a user id in a Prometheus label. |
| 5.6 | Break it: the loop you can only see in a trace | DM | 6 | Inject the loop scenario, read the waterfall to find the runaway step, then add a step limit and surface the error, and watch the same run stop where it should. |
| 5.7 | Lab 3: Trace a multi-step ticket escalation | LAB | 4 | Add spans and a test for the escalation path, where Atlas hands a hard question to the larger model. |
| 5.8 | Quiz: Agent patterns | QZ | 3 | Six questions on step spans, RAG spans, streaming metrics and logs versus traces versus metrics. |

## Section 6: Cost Engineering

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 6.1 | Where the money goes: token anatomy | SL | 7 | Take a request's cost apart: input, output, cached input and reasoning tokens, tool-call overhead, retries and judge calls. You'll learn which OpenAI usage fields report each one. |
| 6.2 | Code-along: a price table you can trust | SC | 8 | Build a price table from LiteLLM's model cost data with a pinned, dated fallback, compute cost per token including cache reads, and handle per-model overrides, currency and rounding. |
| 6.3 | Cost per request, session, user, tenant and feature | SC | 9 | Attach cost to every generation, roll it up by tags into cost per request, session, user, tenant and feature, and generate the showback report finance will accept. |
| 6.4 | Prompt caching: the cheapest win | SC | 8 | Make prompt prefixes stable, set a prompt cache key, measure cached tokens and compare before-and-after cost on the same day of traffic. |
| 6.5 | The context diet | SC | 8 | Trim history, truncate tool results, summarise and tune retrieval top-k, then measure tokens per step before and after to prove the diet worked. |
| 6.6 | Small-model-first routing with LiteLLM Router | SC | 9 | Configure a LiteLLM Router with a small default model and escalation to a larger one on confidence or complexity, add fallbacks, and measure the cost impact on the replayed day. |
| 6.7 | Budgets and anomaly alerts per tenant | SC | 8 | Give every tenant a soft cap that degrades and a hard cap that refuses politely, detect anomalies with EWMA, and expose budget hits as a Prometheus counter. |
| 6.8 | Challenge: cut Atlas's daily cost by 40% | CH | 7 | Pause the video and cut the replayed day's cost by 40% with caching, the context diet and routing, and prove it in the Ops Console. Then compare your approach with the reference solution. |
| 6.9 | Project 1: The showback report | AS | 3 | Produce a weekly cost report by tenant and feature with three concrete recommendations, in the format a finance team would accept. |
| 6.10 | Quiz: Cost engineering | QZ | 3 | Eight questions on token anatomy, price tables, cost rollups, caching, routing and budgets. |

## Section 7: Latency and Reliability

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 7.1 | Latency budgets for agents | SL | 7 | Set a per-step and an end-to-end latency budget, understand p50 versus p95 versus p99, and see why averages lie. Download the latency budget worksheet you'll fill in during Lab 4. |
| 7.2 | Code-along: measure TTFT, TPOT and p95 from spans | SC | 8 | Aggregate time to first token, time per output token and percentiles from the local store, expose Prometheus histograms and build the Ops Console's latency page. |
| 7.3 | Timeouts, retries and backoff done right | SC | 8 | Add per-call timeouts, bounded retries with jitter and idempotency for tool calls, and see why a retry storm is a cost event as much as a latency event. |
| 7.4 | Fallbacks and circuit breakers with the Router | SC | 8 | Configure model and provider fallback lists, cooldowns and half-open probes in the LiteLLM Router, and decide what to log when a fallback fires. |
| 7.5 | Rate limits, queues and graceful degradation | SL | 6 | Handle 429s, set per-tenant concurrency, shed low-priority traffic and write degraded-mode messages that users can live with. |
| 7.6 | Chaos demo: slow provider during peak | DM | 7 | Inject the slow_provider scenario and watch p95, the fallback rate and cost move. Then tune timeouts and fallbacks and re-run until the budget holds. |
| 7.7 | Lab 4: Hold p95 under 4 seconds during chaos | LAB | 4 | Tune timeouts and fallbacks during the slow-provider scenario until the budget gate passes. |
| 7.8 | Quiz: Latency and reliability | QZ | 2 | Six questions on percentiles, TTFT and TPOT, retries and backoff, fallbacks and degradation. |

## Section 8: Quality in Production: Online Evaluation and Drift

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 8.1 | Offline evals are not enough | SL | 6 | Learn why passing evals before release doesn't protect you: distribution shift, new intents, prompt and model changes and silent regressions. You'll define what "quality in production" means for Atlas. |
| 8.2 | Code-along: sampled LLM-as-judge on live traces | SC | 9 | Sample live traces with a policy, judge them with DeepEval G-Eval on agent-specific criteria (resolved, grounded, safe escalation) and write the scores back to Langfuse, with the cost of judging as its own line item. |
| 8.3 | Capturing user feedback that means something | SC | 7 | Add a feedback endpoint with thumbs and reasons, correlate feedback with judge scores and learn how to avoid survivorship bias in what users bother to rate. |
| 8.4 | Guardrail and safety metrics | SC | 6 | Turn injection attempts, refusal rate and PII-in-output rate into time series so safety has a chart, not just a log line. |
| 8.5 | Drift detection: compare this week to last week | SC | 8 | Compare score, cost and latency windows week over week with a PSI-lite measure, set alert thresholds and generate the weekly drift report. |
| 8.6 | From bad trace to regression test | SC | 6 | Promote failing traces to a Langfuse dataset and run offline evals against new prompt versions, closing the loop from production back to your test suite. |
| 8.7 | Lab 5: Build the quality page of the Ops Console | LAB | 5 | Add judge scores, feedback and drift indicators for a replayed week to the Ops Console. |
| 8.8 | Quiz: Online evaluation | QZ | 5 | Eight questions on sampling, LLM-as-judge in production, feedback, safety metrics and drift. |

## Section 9: Dashboards, SLOs and Alerting

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 9.1 | SLIs for agents that leadership understands | SL | 8 | Define SLIs for an agent: task success, containment, tool error rate, p95 latency, cost per resolved session and judge score. Then set SLOs, error budgets and burn rates on them. |
| 9.2 | Code-along: Prometheus metrics from Atlas | SC | 8 | Expose a metrics endpoint with counters and histograms under low-cardinality labels and scrape it with the Docker Compose observability stack. |
| 9.3 | Grafana: the Atlas Ops dashboard | SC | 9 | Import the Atlas Ops dashboard, build a panel per SLI, add a tenant variable and annotate releases, so a manager can read the state of Atlas in one screen. |
| 9.4 | Langfuse dashboards and saved views | DM | 5 | Build cost and score views by tag, use the session explorer and share saved views with stakeholders. |
| 9.5 | Alert rules and the runbook | SC | 7 | Write burn-rate, cost-anomaly and tool-error-spike alerts, fill in the runbook template for each, and apply rules that prevent alert fatigue. |
| 9.6 | Lab 6: Ship the dashboard and one alert | LAB | 3 | Bring the Compose stack up, get the dashboard live and make one alert fire during a replay. |
| 9.7 | Quiz: SLOs and alerting | QZ | 2 | Six questions on SLIs and SLOs, error budgets, Prometheus labels, Grafana panels and alert design. |

## Section 10: Privacy, Security and Governance of Telemetry

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 10.1 | Your traces are a data breach waiting to happen | SL | 6 | Build a threat model for telemetry: prompts contain PII, tool results contain records and judges see everything. You'll decide what must never reach a trace. |
| 10.2 | Code-along: masking in the SDK and the collector | SC | 8 | Mask PII with a Langfuse mask function and with OTel Collector attribute processors, redact tool results and keep hashes so you can still join records. |
| 10.3 | Retention, access and tenant separation | SL | 6 | Set retention windows, use a project per environment, apply role-based access and choose between tenant tags and separate projects. |
| 10.4 | Regulatory logging obligations (not legal advice) | TH | 6 | Get an engineer's overview of record-keeping expectations such as the EU AI Act's requirements for high-risk systems, audit trails, and what to keep versus never log. This is not legal advice; verify with counsel. |
| 10.5 | Quiz: Governance | QZ | 6 | Six questions on the telemetry threat model, masking, retention, access and tenant separation. |

## Section 11: Incident Labs: You Are On Call

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 11.1 | How to read an incident like an SRE | SL | 6 | Learn the investigation order: timeline first, then blast radius, then hypothesis, then evidence in traces. Download the incident template you'll use for the next three lectures. |
| 11.2 | Incident 1: Monday's cost spike (investigate, then reveal) | CH | 12 | Open the incident-01 spans and brief and take eight minutes to find the root cause before the reveal walkthrough. Part A is the investigation; Part B is the reveal. |
| 11.3 | Incident 2: p95 doubled after lunch | CH | 12 | Investigate a latency regression from spans alone, then watch the reveal and fix it with a fallback and a retrieval change. Part A is the investigation; Part B is the reveal. |
| 11.4 | Incident 3: users are unhappy but nothing is red | CH | 12 | Investigate a quality drift that no dashboard flagged, then watch the reveal and roll back using prompt labels. Part A is the investigation; Part B is the reveal. |
| 11.5 | Writing the postmortem | SC | 7 | Write a blameless postmortem with the template, and turn each finding into an action item that maps to instrumentation, a budget or a test. |
| 11.6 | Project 2: Investigate a fourth incident | AS | 3 | Investigate an unrevealed incident dataset from the spans alone and submit a postmortem. |
| 11.7 | Quiz: Incident response | QZ | 3 | Six questions on investigation order, the three incidents' root causes and postmortem action items. |

## Section 12: Portability and Alternatives

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 12.1 | Vendor lock-in and the OTel escape hatch | SL | 6 | Learn what stays portable when you emit OpenTelemetry with the GenAI conventions (traces) and what doesn't (scores, prompts, datasets), and plan for both. |
| 12.2 | Code-along: same Atlas, traced to LangSmith | SC | 8 | Trace the same Atlas to LangSmith with traceable and wrap_openai, send feedback through its API, and note what differs from Langfuse. |
| 12.3 | Arize Phoenix and OpenInference | SC | 7 | Point the OTLP exporter at Arize Phoenix and compare OpenInference conventions with the GenAI conventions you've been using. |
| 12.4 | OpenLLMetry, Datadog and the enterprise APMs | SL | 6 | Decide what to do when your company already has an APM: what OpenLLMetry adds, what LLM observability add-ons cost in principle, and how hybrid setups work. |
| 12.5 | Decision matrix: choosing your backend | SL | 5 | Score backends on control, cost, compliance, features and lock-in using the decision matrix, and write a one-page decision record. |
| 12.6 | Quiz: Portability | QZ | 2 | Five questions on what is and isn't portable, LangSmith and Phoenix setup, and backend selection criteria. |

## Section 13: Deploying the Stack and CI Budget Gates

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 13.1 | Self-hosting Langfuse with Docker Compose | SC | 9 | Bring up self-hosted Langfuse with Docker Compose, configure the environment, create a first project and point Atlas at it. Verify the compose file against the current Langfuse release. |
| 13.2 | OTel Collector as the traffic cop | SC | 7 | Configure receivers, attribute and tail-sampling processors, and exporters to two backends at once, so the collector becomes the single place your telemetry policy lives. |
| 13.3 | Code-along: the CI budget gate | SC | 9 | Write the budget gate test that replays the day offline and fails the pull request if cost per session or p95 regress, wire it into GitHub Actions and tag releases in Langfuse. |
| 13.4 | Production readiness checklist for observability | SL | 6 | Walk the production checklist: sampling in prod, exporter back-pressure, secrets, dashboards as code and alert ownership. |
| 13.5 | Chaos demo: kill the observability backend | DM | 5 | Take Langfuse down and check that Atlas still serves: exporter timeouts, queue limits and the rule that you drop telemetry, never requests. |
| 13.6 | Lab 7: Self-hosted stack end to end | LAB | 4 | Run Langfuse, the OTel Collector and Grafana locally and get the CI gate green. |

## Section 14: Capstone: The Atlas Ops Console

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 14.1 | Capstone brief and acceptance criteria | SL | 6 | Read the capstone brief: a fully instrumented Atlas with budgets, routing, an online judge, dashboards, alerts, a CI gate and a weekly report, with acceptance criteria for each. |
| 14.1a | Build it yourself first: the capstone gate | TH | 3 | Stop here and build the capstone from the brief for one week before watching the reference solution. |
| 14.2 | Reference solution part A: instrumentation and cost | SC | 12 | Assemble the reference solution's telemetry, pricing, budgets and routing, and compare each decision with your own build. |
| 14.3 | Reference solution part B: quality, dashboards, alerts, CI | SC | 12 | Assemble the online judge, drift reports, Grafana dashboard, alert rules and budget gate, and compare with your own build. |
| 14.4 | The weekly ops report your manager reads | SC | 8 | Generate a one-page weekly markdown report covering cost, quality, latency, incidents and recommendations from aggregated spans. |
| 14.5 | Capstone submission and portfolio | TH | 5 | Package your repo, dashboard screenshots, weekly report and postmortems for GitHub and LinkedIn, and learn how to present them. |
| 14.6 | Domain swap: observe a different agent | AS | 4 | Instrument a different agent (a voice agent or your own) with the same stack using the instrumentation template, and adapt the SLIs to its domain. |
| 14.7 | Quiz: Capstone review | QZ | 5 | Six questions that check the capstone's components and the reasoning behind the reference solution's choices. |

## Section 15: Wrap-up and Careers

| ID | Lecture | Type | Min | Description |
|---|---|---|---|---|
| 15.1 | What you can now do | TH | 4 | Recap what you can now do, pillar by pillar, and where this course sits in the Build, Test, Deploy, Operate path. |
| 15.2 | Careers: LLMOps, AI platform and AI SRE roles | TH | 8 | Learn the role titles this course prepares you for, work through 12 interview questions with model answers and learn how to pitch observability to management with an ROI story. No salary figures. |
| 15.3 | Final practice test | QZ | 0 | Forty questions across every technical section, with explanations and related lectures for each answer. |
| 15.4 | Bonus lecture | TH | 5 | Where to go next: the instructor's other courses and community, within Udemy's bonus-lecture rules. |
