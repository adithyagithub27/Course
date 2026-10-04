# Incident Investigation Template

**Used in:** 11.1 (how to read an incident like an SRE), 11.2-11.4 (the three incident labs), 11.6 (Project 2: the fourth incident)

> Use this in the eight minutes before the reveal. The order matters: **timeline → blast radius → hypothesis → evidence → root cause**. Write things down as you go; the incident labs are graded (by you) on the quality of the reasoning, not on guessing the answer. Copy the template into `incidents/<name>/investigation.md` in your repo for each incident.

---

## Template

```markdown
# Incident: <short name>            Investigator: <you>     Started: <time>

## 0. The brief (copy it here verbatim)
<Paste incidents/<name>/brief.md: the timestamp, the symptom, what is and isn't alerting.>

## 1. Timeline (fill first; facts only, no theories)
| Time | What happened / what was observed | Source (span, metric, annotation, log) |
|---|---|---|
| T-? | Last known-good state (a normal session; note its cost, steps, p95, judge score) | |
| T-? | Any change: deploy, prompt label switch, config, top-k, model rename, traffic pattern | release annotations, prompt versions, git log |
| T0 | First bad trace (the earliest trace showing the symptom) | Langfuse filter + sort by time |
| T+ | Alert fired (or: nothing fired; write "silent") | Grafana alert history |
| T+ | Detection (how did anyone notice?) | |
| now | Current state | |

## 2. Blast radius
- Tenants affected: <ops | finance | hr | eng | all>   (Langfuse tag filter `tenant=`; Grafana tenant variable)
- Features affected: <policy_question | create_ticket | ticket_lookup | shipment_status | password_reset | escalation | other | all>
- Sessions affected so far: <count>   Users: <count>
- Is it per-session (same sessions, worse) or volume (more sessions)? <answer, with the metric you used>
- Is it getting worse, stable, or recovering? <trend>

## 3. Symptom summary (one sentence, numbers included)
<e.g., "Cost per resolved session for tenant `ops` is 6.2× the 7-day baseline since 08:02, other tenants normal, task success unchanged.">

## 4. Hypotheses (write at least two before opening a single trace)
| # | Hypothesis | What I'd expect to see in the traces if true | What would rule it out |
|---|---|---|---|
| H1 | | | |
| H2 | | | |
| H3 | | | |

## 5. Evidence (one trace at a time)
| Trace / session id | What I looked at | Observation | Supports / rules out |
|---|---|---|---|
| | steps count, tool errors, context growth per step, retries, fallbacks, model used, prompt version, judge score | | |
| | | | |

Ops Console pages used: <Cost / Latency / Quality / Budgets / Alerts>
Langfuse views used: <sessions by tag, sort by cost / latency / score, prompt versions, dataset>
Grafana panels used: <p95, cost per resolved session, tool error rate, fallback rate, judge score>

## 6. Root cause (the thing that, had it been different, would have prevented the incident)
<One or two sentences. Distinguish trigger (what started it) from cause (why the system let it hurt).>

## 7. Contributing factors
- <e.g., no per-tenant budget; no alert on step count; prompt promoted without an eval run; top-k change had no release annotation>

## 8. Mitigation applied (or proposed)
<What stops the bleeding now. Link to the runbook step.>

## 9. What I got wrong on the way (the red herrings)
<Which hypothesis you chased first and what evidence killed it. This is the most useful section for learning.>

## 10. Time spent: <minutes>     Confidence in root cause: <low | medium | high>, because <reason>
```

---

## Reading order cheats (lecture 11.1)

1. **Timeline before traces.** Opening a random trace first anchors you on whatever you see in it. Get T0 and any change events first.
2. **Blast radius tells you where to look.** One tenant → something tenant-specific (their traffic, their budget, their knowledge base). All tenants → a shared change (prompt, model, provider, top-k).
3. **Compare a bad trace with a good one from before T0**, side by side. Differences jump out: steps, context size per step, model, prompt version, retries.
4. **Where did the tokens go? Where did the time go?** Those two questions (5.1) resolve most agent incidents. Context growing per step is a loop or bloat; TTFT growing is a provider or a prompt-length problem; tool duration growing is a dependency problem.
5. **"Nothing is red" is a clue**, not an absence of clues. If cost and latency are normal and users are unhappy, look at quality signals: judge scores, feedback, refusal rate, prompt version (Incident 3).
6. **Write the hypothesis before the fix.** A fix that works for the wrong reason will come back.

## Anti-patterns

- Restarting things before writing down the timeline.
- Fixing the trigger (a slow provider) and not the cause (no fallback, no timeout).
- Declaring root cause from one trace.
- Blaming a person or a model. The postmortem (`postmortem-template.md`) is blameless: systems let mistakes hurt.
