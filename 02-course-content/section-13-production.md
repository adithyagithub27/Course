# Section 13: Production Monitoring & Governance

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 13 (curriculum `01-curriculum/full-curriculum.md`, Module 13, ~21 min, 3 lectures)
> **Source of truth for code, numbers and outputs:** `14-quality-review/course2-bible.md` §7 (Module 13), §8.25–8.26, §12. Every output below was captured from a real run in **offline mode**. The drift data in 13.1 is **simulated** (seed 7) and labelled so on screen. In 13.3, only the TechCorp Support row's correctness, faithfulness and relevance come from a real (offline) evaluation; every other scorecard value is an illustrative input from `monitoring/scorecard.py`.
> **Repo:** `04-code-examples/agent-eval-framework/`. Run demos with `uv run python demos/<file>`.
> **Version banner for every code slide:** `Verified: openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0 | Python 3.11+ | OFFLINE=1 runs without a key`
> **Compliance content is not legal advice.** Regulation names are examples; anything a student would act on carries "verify with your compliance team".

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 13.1 | Monitoring Agents in Production: Drift, Degradation & Alerts | Teach + demo | 7:00 | 900 |
| 13.2 | Enterprise AI Governance: Policies, Audit Trails & Compliance | Teach | 7:00 | 895 |
| 13.3 | Building an Agent Quality Scorecard for Leadership | Build-along | 7:00 | 690 |

Cue legend: see `section-10-performance.md`. Word counts are spoken words only.

---

## Lecture 13.1 — Monitoring Agents in Production: Drift, Degradation & Alerts

| Field | Value |
|---|---|
| ID | 13.1 |
| Title | Monitoring Agents in Production: Drift, Degradation & Alerts |
| Type | Teach + demo |
| Target duration | 7:00 (900 spoken words) |
| Learning objectives | 1. Name the four production signals: quality drift, cost anomalies, behaviour changes and user feedback. 2. Choose between online scoring of sampled traffic and a nightly batch evaluation. 3. Detect drift with a rolling average and two alert rules: an absolute threshold and a drop from the launch baseline. |
| Prerequisites | 12.3; 9.2 (Langfuse scores) |
| Files used | `monitoring/drift_monitor.py` (`DriftMonitor.check`, `rolling`, `simulate_weeks`, `monitor_from_rows`), `config/eval_config.yaml` (faithfulness threshold 0.8), `observability/langfuse_tracing.py` (scores via `create_score`), `demos/m13_drift_detection.py`; diagram D15 |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | langfuse 4.16.0
- Python 3.11+ | drift data in this demo is simulated

[AVATAR]
Your agent passed every gate. It shipped clean. And four weeks later, its faithfulness is twelve points lower, and no test ever failed. [PAUSE] Nobody changed the code. So what happened? And how would you know before your customers do?

[SLIDE 2: By the end of this lecture]
- Name the four production signals to watch
- Choose online scoring or nightly batch evaluation
- Detect drift with a rolling average and two alerts

Today you'll set up the last layer of the eval pyramid: production monitoring. You'll pick what to watch, decide how to score live traffic, and run a drift detector that raises an alert days before the threshold is crossed.

[SLIDE 3: The production monitoring loop]
Diagram: D15 (Production monitoring loop), builds 1 to 6: "production agent → sample requests → online evaluator → score store → dashboard + alerts → close the loop (new golden cases, regression suite)".

Here's the loop. The production agent serves real users. You sample some of those requests. An evaluator scores them, with the same metrics you use in CI. The scores land in a store. A dashboard and alerts watch the store. And when an alert fires, the failing conversations become new golden cases. So production feeds your regression suite, and the pyramid closes into a circle.

[SLIDE 4: Four signals to watch]
- Quality drift: judge scores sliding down over days
- Cost anomalies: tokens or cost per task jumping
- Behaviour changes: tool-call mix, response length, escalation rate
- User feedback: thumbs-down, complaints, repeat contacts

Four signals. Quality drift is the slow one: scores sliding a point a day. Cost anomalies are the loud one: tokens per task doubling overnight, often a loop. Behaviour changes are subtle: suddenly the agent escalates twice as often, or stops calling the knowledge base. And user feedback is the ground truth, but it arrives late and it's noisy. Which of the four would you wire up first?

[SLIDE 5: Why drift happens with no code change]
- Users change: new questions, new products, new slang
- Context changes: knowledge-base edits, new documents
- Models change: provider updates behind an alias
- Your gate only tests the questions you already wrote

Why does quality drift when nobody touched the code? You know two causes from Module 11: the knowledge base changed, or the model behind the alias changed. The third is new: your users change. They start asking about a product you launched last week, and your golden set has no questions about it. The gate keeps passing, because it only asks the questions you already wrote.

[SLIDE 6: Online or nightly?]
| | Online scoring | Nightly batch |
|---|---|---|
| What | score a sample of live requests as they happen | re-score yesterday's sampled traffic |
| Metrics | cheap ones (relevancy, a short GEval) | the full suite |
| Catches | sudden breaks within hours | slow drift, with better judges |
| Cost | grows with traffic and sample rate | fixed per night |

You have two ways to score production. Online scoring evaluates a sample of live requests as they happen. Keep the metrics cheap and the sample small, a few percent of traffic, and it catches sudden breaks within hours. A nightly batch re-scores yesterday's sample with the full suite and your best judge. Slower, but more accurate, and the bill is predictable. Most teams run both. And with Langfuse, the scores you attached with `create_score` in Lecture 9.2 already give you a store to read from.

[SLIDE 7: Two alert rules]
- Threshold: 7-day average below the policy line (faithfulness 0.8)
- Baseline drop: 7-day average more than 5 points below launch
- Rolling averages smooth out one bad day

Now detection. Daily scores are noisy, so you smooth them with a seven-day rolling average. Then two rules. The threshold rule fires when the average falls below the policy line in `eval_config.yaml`, point eight for faithfulness. The baseline-drop rule fires when the average falls more than five points below where it was at launch. Why two? Because they answer different questions. Watch.

[CODE: `monitoring/drift_monitor.py`, `check`. Highlight the two `alerts.append` lines.]

```python
def check(self) -> list[Alert]:
    alerts: list[Alert] = []
    for metric in self.series:
        thr = self.thresholds.get(metric)
        fired = set()
        for day, avg in self.rolling(metric):
            if thr is not None and avg < thr and "threshold" not in fired:
                alerts.append(Alert(day, metric, round(avg, 3), thr, "threshold"))
                fired.add("threshold")
            base = self.baseline.get(metric)
            if base is not None and avg < base - self.max_drop and "baseline_drop" not in fired:
                alerts.append(Alert(day, metric, round(avg, 3), round(base - self.max_drop, 3), "baseline_drop"))
                fired.add("baseline_drop")
    return sorted(alerts, key=lambda a: a.day)
```

Here's the whole detector. For each metric, walk the rolling averages day by day. Below the threshold? Raise one threshold alert. More than the allowed drop below the baseline? Raise one baseline-drop alert. Each kind fires once per metric, so a bad week produces one alert, not seven.

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m13_drift_detection.py
```

[DEMO: Output after the banner (offline, simulated data)]

```text
Week-by-week faithfulness (7-day rolling average, SIMULATED data, seed 7):
  2026-09-07  0.912  #####################
  2026-09-10  0.915  #####################
  2026-09-13  0.917  #####################
  2026-09-16  0.922  ######################
  2026-09-19  0.904  ####################
  2026-09-22  0.873  #################
  2026-09-25  0.842  ##############
  2026-09-28  0.798  #########

Launch baseline: 0.912; threshold from eval_config.yaml: 0.8
[2026-09-24] ALERT faithfulness: 7-day avg 0.851 (baseline_drop, limit 0.862)
[2026-09-28] ALERT faithfulness: 7-day avg 0.798 (threshold, limit 0.800)
[2026-09-28] ALERT task_completion: 7-day avg 0.823 (baseline_drop, limit 0.828)
```

Four weeks of simulated daily scores. Launch baseline: point nine one two. For two weeks, it's flat. Then it slides: point nine oh four, point eight seven three, point eight four two, and finally point seven nine eight.

[SCREEN: Same output. Zoom on the first alert, then the second, with the dates highlighted in Amber.]

Now the alerts. On September twenty-fourth, the baseline-drop rule fires: average point eight five one, more than five points below launch. The threshold rule only fires on the twenty-eighth, when the average finally crosses point eight. The relative rule saw it four days earlier. Four days of customers getting worse answers. That's why you want both rules.

[AVATAR]
And look at the third alert. Task completion also slid, on the same day. When two metrics move together, look for a shared cause, like a knowledge-base change or a model update that week. That's your first question in the incident review.

[SLIDE 8: Same detector, other signals]
- Cost per task: baseline $0.0008 (Lecture 10.1), alert at 2× (verify current pricing)
- LLM calls per task: alert above 6 (the loop guard)
- Escalation rate: alert on a jump from your weekly norm
- Tool mix: alert when `search_knowledge_base` share falls

The detector doesn't care what the number means. Feed it cost per task, and you'll catch cost anomalies: our benchmark baseline was about eight hundredths of a cent, so double that is worth an alert. Feed it LLM calls per task, and anything above six means the loop guard is working too hard. Feed it the escalation rate, or the share of answers that searched the knowledge base. Remember the regression from Module 11? Its first production symptom would be exactly that: fewer searches.

[SLIDE 9: When an alert fires]
1. What changed this week? Deploys, knowledge-base edits, model updates
2. Pull the lowest-scoring traces in Langfuse
3. Turn the worst conversations into golden cases
4. Fix, then prove it with the regression suite

And when an alert fires, follow four steps. One: what changed this week? Check the audit trail, the knowledge-base history and the provider's changelog. Two: pull the lowest-scoring traces in Langfuse and read them. Three: turn the worst conversations into golden cases. Four: fix it, and prove the fix with the regression suite. Step three is the one teams skip, and it's the one that stops the same drift from coming back.

[SLIDE 10: Recap]
- Watch quality, cost, behaviour and user feedback
- Score samples online; run the full suite nightly
- Two alerts: threshold and drop from baseline

Watch four signals. Score a sample online, and the full suite nightly. And alert on two rules: below the threshold, and too far below launch. The second one buys you days.

### Recap

Production monitoring scores sampled live traffic, smooths it with a 7-day rolling average, and alerts on both an absolute threshold and a drop from the launch baseline; in the simulated run the baseline rule fired four days earlier.

### Transition

When an alert fires, someone will ask: which version was live, who approved it, and what did its evaluation say? Lecture 13.2 answers that with governance and an audit trail.

### Speaker notes: common student mistakes / Q&A

- **Simulated data, said on screen.** `simulate_weeks()` generates four weeks of daily scores with seed 7 (bible §12 fact 8). Never present it as real production data.
- **Hook number:** "twelve points" is 0.912 → 0.798 (11.4 points, rounded); say "about eleven points" if you prefer exactness.
- **Max drop** is 0.05 in the demo (0.912 − 0.05 = 0.862 limit). The task-completion baseline is not printed; its limit is 0.828.
- **Feeding real scores:** read scores from Langfuse (Lecture 9.2 attaches them with `create_score`) or from your nightly batch reports; the monitor takes rows of `(day, metric, value)`-style data via `monitor_from_rows`.
- **Sample rate:** "a few percent" is a starting point, not a rule; set it from your traffic and budget (verify current pricing for judge calls).

---

## Lecture 13.2 — Enterprise AI Governance: Policies, Audit Trails & Compliance

| Field | Value |
|---|---|
| ID | 13.2 |
| Title | Enterprise AI Governance: Policies, Audit Trails & Compliance |
| Type | Teach (with one demo) |
| Target duration | 7:00 (895 spoken words) |
| Learning objectives | 1. Write an evaluation policy as code: metrics, thresholds, frequency and owner. 2. Explain how a hash-chained audit trail makes tampering visible, and gate a release on required approvals. 3. List what a model card and a compliance mapping must contain for an agent. |
| Prerequisites | 13.1; 12.1 (gates) |
| Files used | `config/eval_config.yaml`, `monitoring/governance.py` (`AuditTrail.log`, `verify`, `release_allowed`), `demos/m13_governance_audit.py`, `agents/support_agent.py` (system prompt, known multi-turn identity gap from Lecture 8.2) |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Not legal advice: verify with your compliance team

[AVATAR]
It's an incident review. The agent leaked a customer's balance. The first question isn't "why?". It's "who approved this version, and what did its tests say?" [PAUSE] Silence. Someone scrolls through Slack. Someone else thinks it was Tuesday. Can your team answer that question in one minute?

[SLIDE 2: By the end of this lecture]
- Write an evaluation policy as code
- Keep a tamper-evident audit trail and a release gate
- Know what goes in a model card and a compliance map

Today you'll set up the paperwork that makes all your testing count, without the paperwork. A policy as code. An audit trail you can trust. And a release gate that needs the right approvals.

[SLIDE 3: Four parts of agent governance]
Diagram: four stacked Teal blocks, bottom to top: "Evaluation policy (what we test, thresholds, who owns it)", "Audit trail (every eval, red-team run, approval, deployment)", "Model card (what the agent does and doesn't do)", "Compliance map (which rules apply, and the evidence)". An arrow on the right labelled "evidence flows up".

Governance has four parts. A policy that says what you test and who owns it. An audit trail that records every evaluation, red-team run, approval and deployment. A model card that says what the agent does and doesn't do. And a compliance map that links each regulation to the evidence. Each layer feeds the one above.

[SLIDE 4: The evaluation policy is a file you already have]
- Metrics and thresholds: `config/eval_config.yaml`
- Gates and tolerance: the `gates` block
- Frequency: the workflow triggers (push, PR, nightly)
- Owner: a named person in CODEOWNERS (your addition)

Good news: your evaluation policy already exists. It's `eval_config.yaml`. Five dimensions, each with metrics and thresholds. A `gates` block that says what blocks a merge. The workflow file says how often it runs. The one thing missing is an owner. Add the config file to your CODEOWNERS file, so changing a threshold needs approval from a named person. A threshold nobody owns will drift down, one "temporary" change at a time.

[SLIDE 5: An audit trail that can't be quietly edited]
Diagram: five records in a row, each a card with "event, actor, version, data" and two small fields "prev_hash" and "hash". Arrows link each card's hash to the next card's prev_hash. The first card's prev_hash shows "000…0". A red pencil icon on card 1 breaks every arrow after it.

An audit trail is a list of events. Evaluation ran. Red team ran. Someone approved. Release deployed. The trick is making it tamper-evident. Each record stores a hash of its own contents, plus the hash of the record before it. Change one old record, and its hash no longer matches what the next record remembers. The chain breaks, and you can prove it.

[CODE: `monitoring/governance.py`, `AuditTrail.log`. Highlight the `prev_hash` line and the `sha256` line.]

```python
def log(self, event: str, actor: str, agent_version: str, data: dict | None = None, ts: str | None = None) -> dict:
    prev = self.records()
    rec = {
        "seq": len(prev) + 1,
        "ts": ts or datetime.now(UTC).isoformat(timespec="seconds"),
        "event": event, "actor": actor, "agent_version": agent_version, "data": data or {},
        "prev_hash": prev[-1]["hash"] if prev else "0" * 64,
    }
    rec["hash"] = hashlib.sha256(json.dumps({k: v for k, v in rec.items() if k != "hash"}, sort_keys=True).encode()).hexdigest()
    with self.path.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec
```

Here's the code. Every record gets a sequence number, a timestamp, the event, the actor, the agent version and the data. The previous record's hash goes in. Then a SHA-256 hash over everything. It's appended as one JSON line. Twelve lines of Python, and no blockchain required.

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m13_governance_audit.py
```

[DEMO: Output after the banner (offline)]

```text
(False, ['missing approval: Product owner'])
#1 2026-09-28T10:02:00+00:00 evaluation  github-actions             {"pass_rate": 1.0, "averages": {"Faithfulness": 1.  hash 3cde262af4
#2 2026-09-28T10:09:00+00:00 redteam     github-actions             {"total": 10, "findings": 0}  hash 01962c2bbf
#3 2026-09-28T14:30:00+00:00 approval    maria.lopez@techcorp.com   {"role": "QA lead"}  hash 427222e35d
#4 2026-09-29T09:15:00+00:00 approval    sam.chen@techcorp.com      {"role": "Product owner"}  hash 1890e1649d
#5 2026-09-29T09:40:00+00:00 deployment  release-bot                {"environment": "production"}  hash 4d5b3ad7f5

Release allowed for v1.3: (True, [])
Chain intact: True
After someone edits record #1 by hand -> chain intact: False
```

Read it as the release story of version one point three. CI ran the evaluation, pass rate one hundred percent. CI ran the red team, ten attacks, zero findings. The QA lead approved. At that moment, the release gate said no: missing approval, product owner. Next morning, the product owner approved, and the release bot deployed.

[SCREEN: Same output. Zoom on the last two lines.]

Then the demo does something sneaky. It edits record one by hand, changing the pass rate from one point oh to point six. The chain check fails immediately. Nobody can quietly rewrite what the evaluation said after an incident.

[SLIDE 6: Limits of a hash chain]
- Detects edits to past records
- Does not stop someone deleting the newest records
- Ship records to append-only storage (write-once bucket, log service)

To be honest about the limits: a hash chain detects edits, but someone with write access could delete the last few records, or rebuild the whole chain. So in production, also ship each record somewhere append-only, like a write-once storage bucket or your log platform. The chain proves integrity. The storage protects it.

[SLIDE 7: Who may approve a release]
- 2 required approvals for v1.3: QA lead and Product owner
- The author of a prompt change cannot approve it
- Automated evidence first: evaluation and red team before any human

Who approves? In the demo, a release needs two roles: the QA lead and the product owner. That's a policy decision, and it belongs in writing. Add one more rule: the person who wrote a prompt change can't be the one who approves it. And let the machines go first. Evaluation and red-team results land in the trail before any human signs, so approvers sign evidence, not vibes. How many approvals does a prompt change need at your company today? For many teams, the honest answer is zero.

[SLIDE 8: Model card for an agent]
- Purpose and users; what it must never do
- Tools and data it can reach (5 tools, customer records)
- Evaluation results and the dataset versions behind them
- Known limitations: identity not re-verified across turns

A model card for an agent is a one-page fact sheet. What it's for, and who uses it. What it must never do. Which tools and data it can reach: for TechCorp, five tools and customer records. The latest evaluation results, with dataset versions. And known limitations, written down honestly. Remember the gap you found in Lecture 8.2? The agent doesn't re-verify identity across turns. That belongs on the card until it's fixed. Update the card with every release, and link it from the audit record, so the version in production and the card describing it always match. One page, ten minutes per release.

[SLIDE 9: Compliance mapping (verify with your compliance team)]
| Rule (examples) | Question it asks | Evidence you already produce |
|---|---|---|
| GDPR | Is personal data protected? | PII scanner, red-team PII cases |
| EU AI Act | Was the system tested and documented? | audit trail, model card, eval reports |
| SOX / financial controls | Who approved the change? | approvals in the audit trail |
| HIPAA (health data) | Is health data exposed? | PII scanner, access tests |

Finally, compliance mapping. Which rules apply depends on your industry and country, so verify with your compliance team. This isn't legal advice. But the pattern is always the same: each rule asks a question, and you answer with evidence you already produce. Data protection asks about personal data: your PII scanner and red-team results. Change-control rules ask who approved: your audit trail. Which of these does your company already ask you for?

[B-ROLL: A Langfuse trace view (from Lecture 9.2) with the `lookup_customer` tool output expanded, showing "Alice Johnson" and "alice@example.com". A Teal "redact" bar slides over the name and email.]

One warning that connects governance back to Module 9. Your traces are evidence, and your traces contain personal data. Every `lookup_customer` span holds a name, an email and a balance. So the same rules apply to your observability store: who can read it, how long you keep it, and whether you redact before you store. Run the Module 8 PII scanner over a sample of traces, not just over answers.

[SLIDE 10: Recap]
- Policy as code, with a named owner
- Hash-chained audit trail plus a release gate
- Model card and compliance map built from evidence

Your policy is code, with an owner. Your audit trail is hash-chained, and releases need the right approvals. And your model card and compliance map are built from evidence you already have.

### Recap

Governance turns your tests into evidence: a policy in `eval_config.yaml`, a hash-chained audit trail with a release gate, and a model card and compliance map that cite real results.

### Transition

Leadership won't read an audit trail. They want one page. In Lecture 13.3, you'll build the agent quality scorecard.

### Speaker notes: common student mistakes / Q&A

- **Not legal advice.** Keep the compliance table to "examples" and "verify with your compliance team" on screen. Do not state what a regulation requires in detail; it changes and differs by jurisdiction.
- **The demo is deterministic:** timestamps are passed in, so hashes (`3cde262af4`, ...) are the same on every run. In real use, timestamps come from the clock and hashes differ.
- **`release_allowed`** returns `(allowed, reasons)`; in the demo it reports the missing Product owner approval until record #4 is logged.
- **CODEOWNERS** is not in the repo; it is a suggested addition for students' own repos.
- The curriculum's GlobalHealth Pharma scenario is not used: its figures and the FDA quote are unsourced (A6).

---

## Lecture 13.3 — Building an Agent Quality Scorecard for Leadership

| Field | Value |
|---|---|
| ID | 13.3 |
| Title | Building an Agent Quality Scorecard for Leadership |
| Type | Build-along |
| Target duration | 7:00 (690 spoken words; the rest is reading the scorecard) |
| Learning objectives | 1. Answer leadership's three questions (is it working, which way is it going, what does it cost) on one page. 2. Build a traffic-light scorecard over the five quality dimensions for several agents. 3. Present a red cell as a decision, not a data dump. |
| Prerequisites | 13.2; 2.2 (five dimensions) |
| Files used | `monitoring/scorecard.py` (`EXAMPLE_AGENTS`, `build_scorecard`, `render_markdown`), `demos/m13_quality_scorecard.py`, `reports/results/scorecard.md` (generated); diagram D5 |

### Script

[SLIDE 1: Version banner]
- Verified: openai 2.54.0 | deepeval 4.2.7 | Python 3.11+
- Support row from a real offline eval; other rows illustrative

[AVATAR]
You have dashboards, traces, audit trails and a hundred metrics. Your VP has ninety seconds between meetings. [PAUSE] What do you show them? If the answer is "the dashboard", they'll nod, and decide on gut feeling anyway.

[SLIDE 2: By the end of this lecture]
- Answer leadership's three questions on one page
- Build a traffic-light scorecard for three agents
- Turn a red cell into a decision

Today you'll build a one-page scorecard that answers leadership's questions in under a minute, for three TechCorp agents, using the five quality dimensions you've used since Module 2.

[SLIDE 3: Three questions leadership asks]
- Is it working? One status per agent: green, amber, red
- Which way is it going? A trend arrow per dimension
- What does it cost? Cost per task, weekly cost, escalation rate

Leadership asks three questions. Is it working? So every agent gets one status: green, amber or red. Which way is it going? So every dimension gets a trend arrow. And what does it cost? So the page shows cost per task, weekly cost and the escalation rate, which is a cost too, because every escalation is a person's time.

[SLIDE 4: Five dimensions, one row per agent]
Diagram: D5 (Five dimensions of agent quality), build 1: the five axes Correctness, Faithfulness, Relevance, Safety, Reliability. Beside it, the same five names as column headers of a table with three empty rows: "TechCorp Support", "Policy Assistant (RAG)", "Operations Agent".

The columns are the five dimensions you know: correctness, faithfulness, relevance, safety and reliability. The rows are your agents. Here, three TechCorp agents: the support agent, the policy assistant from Module 5, and the operations agent from Module 6.

[CODE: `demos/m13_quality_scorecard.py`, the lines that feed the support agent's real evaluation into the scorecard.]

```python
agents = copy.deepcopy(EXAMPLE_AGENTS)
r = run_suite(load("golden_support"), run_support_agent, default_metrics_for)
a = r["averages"]
agents[0]["this_week"].update({"correctness": a["Answer Correctness"], "faithfulness": a["Faithfulness"], "relevance": a["Answer Relevancy"]})
md = render_markdown(build_scorecard(agents, week="2026-09-28"))
(RESULTS / "scorecard.md").write_text(md + "\n")
```

Here's the build. Start from example inputs for the three agents. Then run the real golden evaluation for the support agent, and overwrite its correctness, faithfulness and relevance with this week's averages. `build_scorecard` computes lights and arrows. `render_markdown` writes one table to `reports/results/scorecard.md`. In your project, every row comes from real runs. Here, two rows are illustrative so you can see amber and red.

[SLIDE 5: Where every number on the page comes from]
| Column | Source in your pipeline |
|---|---|
| Correctness, Faithfulness, Relevance | nightly golden evaluation (Module 12) |
| Safety | red-team pass rate and safety GEvals (Module 8) |
| Reliability | `measure_reliability` and benchmark p95 (Module 10) |
| Cost/task, weekly cost | benchmark or Langfuse costs (Modules 9 and 10) |
| Escalations | share of conversations calling `escalate_to_human` |

Before you send this to anyone, know where every number comes from. Correctness, faithfulness and relevance come from the nightly golden run. Safety comes from the red-team pass rate and the safety GEvals. Reliability comes from your Module 10 checks. Cost comes from the benchmark or from Langfuse. And escalations are simply the share of conversations that called `escalate_to_human`. If a VP asks "where's that number from?", you answer in one sentence. Could you do that for every cell today?

[SCREEN: Terminal in `04-code-examples/agent-eval-framework`.]

```bash
uv run python demos/m13_quality_scorecard.py
```

[DEMO: Output after the banner (offline; Support row partly real, other rows illustrative)]

```text
# Agent Quality Scorecard - week of 2026-09-28
| Agent | Overall | Correctness | Faithfulness | Relevance | Safety | Reliability | Cost/task | Weekly cost | Escalations |
|---|---|---|---|---|---|---|---|---|---|
| TechCorp Support | [G] | [G] 0.98 ^ | [G] 1.00 ^ | [G] 1.00 ^ | [G] 0.99 = | [G] 0.95 = | $0.0008 | $28.00 | 6% |
| Policy Assistant (RAG) | [A] | [A] 0.84 v | [G] 0.93 = | [G] 0.87 = | [G] 0.98 = | [G] 0.93 = | $0.0006 | $2.52 | 2% |
| Operations Agent | [R] | [G] 0.88 = | [G] 0.90 = | [G] 0.85 = | [R] 0.89 v | [G] 0.91 = | $0.0012 | $1.80 | 0% |
[G] on target  [A] within 5 points  [R] action needed   ^ improving  v declining  = flat
Costs use list prices (verify current pricing).

Operations Agent is RED on safety: open the red-team report before the next release.
```

Here's the page. Read it the way a VP would, from the left. Support: green. Policy assistant: amber. Operations agent: red. That took two seconds.

[SCREEN: Same output. Highlight the Policy Assistant correctness cell, then the Operations Agent safety cell.]

Why amber? Correctness is point eight four, and the arrow points down. It's within five points of its target line, and declining. That's a "watch this" signal. Why red? Safety is point eight nine, just under its target, and it's trending down. And the overall status takes the worst cell, because one unsafe dimension sinks the whole agent. Should a cheaper, faster agent ever turn green if safety is red?

[SLIDE 6: Present a red cell as a decision]
- What: Operations Agent safety 0.89, below target, declining
- So what: safety decides whether this agent may ship
- Now what: review the red-team report before the next release

Never present a red cell as a number. Present it as a decision. What happened: safety is point eight nine, below target, and falling. So what: safety is the dimension that decides whether this agent may ship at all. Now what: the team reviews the red-team report before the next release. Three sentences. That's the whole conversation.

[AVATAR]
Send this page every week, at the same time, in the same format. Consistency is the feature. After a month, your leadership will glance at the colours, read the one red line, and move on. That's the goal: quality decisions made in ninety seconds, on evidence.

[SLIDE 7: Recap]
- Three questions: working, trending, costing
- Five dimensions, traffic lights, trend arrows
- Every red cell gets what, so what, now what

Three questions: is it working, which way is it going, what does it cost. Five dimensions with lights and arrows. And every red cell comes with a decision.

[SLIDE 8: You can now]
- Detect drift with two alert rules
- Keep a tamper-evident audit trail and release gate
- Build a one-page leadership scorecard

You can now monitor agents in production, govern their releases with evidence, and report their quality on one page.

### Recap

A leadership scorecard puts five dimensions, traffic lights, trend arrows and cost for every agent on one page, and turns each red cell into a what, so what, now what.

### Transition

You've built every piece of an agent quality platform, one module at a time. Module 14 puts them together into a single platform. Next, Lecture 14.1: the capstone architecture and requirements.

### Speaker notes: common student mistakes / Q&A

- **What is real on the page:** only the TechCorp Support row's Correctness, Faithfulness and Relevance come from the offline evaluation in this run. Safety, Reliability, cost, weekly cost, escalations and the other two rows are illustrative inputs (`EXAMPLE_AGENTS`). Say so on camera (the version banner slide does) and in the student brief.
- **Targets:** the legend printed by the code is "[G] on target, [A] within 5 points, [R] action needed". Check the per-dimension targets in `monitoring/scorecard.py` before recording and do not quote a target number on camera that you have not checked there (the GEval safety thresholds in `config/eval_config.yaml` are 0.9).
- **Costs** use list prices from `config/settings.py` (verify current pricing).
- **Student assignment (curriculum 13.3):** build the scorecard for your own Project 1–4 agent with every value from real runs.
- The curriculum's business-impact figures ("12% drop in escalation rate", "$45K/month") are unsourced and are not used (A6).
