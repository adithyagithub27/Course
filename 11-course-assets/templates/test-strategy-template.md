# AI Agent Test Strategy Template

> AI Agent Testing & Evaluation — the one test-strategy template (decision T4), taught in Lecture 2.3 and reused in Projects 1–5.
>
> **How to use it:** (1) describe the agent; (2) cross its components with the five quality dimensions to decide **what** to test (the coverage matrix, diagram D6); (3) place every test on one of the five layers of the agent eval pyramid (diagram D4) to decide **when** it runs and **who** owns it. Rows are the pyramid layers. An empty row is a decision; a missing row is a gap.
>
> Vocabulary: six failure modes (T2) — hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift, infinite loops. Five quality dimensions (T3) — correctness, faithfulness, relevance, safety, reliability. Default thresholds come from `04-code-examples/agent-eval-framework/config/eval_config.yaml`.

---

## 1. Agent Under Test

| Field | Value |
|-------|-------|
| Agent name and version | |
| Purpose (one sentence) | |
| Agent model / judge model | e.g. `gpt-4.1-mini` / `gpt-4.1` |
| Tools (and which ones act on the world) | |
| Data it can see (PII? other customers?) | |
| Users and channel | |
| Risk level | Low / Medium / High / Critical |
| Highest-risk failure modes (T2), ranked | 1. 2. 3. |

---

## 2. Coverage Matrix: What to Test (components × dimensions)

Fill each cell with a test type, or "n/a" with a reason. Each cell you fill becomes one or more tests in Section 3.

| Component ↓ / Dimension → | Correctness | Faithfulness | Relevance | Safety | Reliability |
|---|---|---|---|---|---|
| **LLM** (reasoning, wording) | | | | | |
| **Tools** (selection, arguments, results) | | | | | |
| **Memory** (conversation, retrieval) | | | | | |
| **Planning** (steps, loops, hand-offs) | | | | | |

Examples from the TechCorp support agent: Tools × Correctness = tool correctness (expected tools per golden case); LLM × Faithfulness = Faithfulness metric against the tool results; Planning × Reliability = loop detection and the 5-iteration cap; Tools × Safety = no `lookup_customer` for another customer's data; Memory × Safety = identity re-checked on every turn (the multi-turn gap from Lecture 8.2).

---

## 3. Test Strategy: Where and When (one row per pyramid layer)

| Layer | What you test (from Section 2) | Failure modes (T2) | Dimensions (T3) | Metrics and thresholds | When it runs | Cost | Owner |
|---|---|---|---|---|---|---|---|
| **1. Unit evals** — deterministic checks on tools, parsers, guards | | | | | every commit | ~free | |
| **2. Component evals** — retriever, generator, judge, MCP contract, one piece at a time | | | | | every commit | cents | |
| **3. Trajectory evals** — tool choice, arguments, order, loops across the agent's steps | | | | | every PR | | |
| **4. End-to-end evals** — golden datasets scored by LLM-judge metrics; red team | | | | | every PR / nightly | | |
| **5. Production monitoring** — drift, scorecards, audit trail, tracing on live traffic | | | | | continuous | | |

Placement rule (Lecture 2.3): does the test need a judge model? Layer 4 or above. Does it need the whole agent loop? Layer 3 or above. Neither? Push it down to layer 1 or 2, where it is fast and free.

### Worked row (TechCorp support agent)

| Layer | What you test | Failure modes | Dimensions | Metrics and thresholds | When | Cost | Owner |
|---|---|---|---|---|---|---|---|
| 3. Trajectory evals | Tool selection and order on the double-charge (GS-05) and cancellation (GS-06) cases | wrong tool selection, incorrect tool arguments | correctness | `ToolCorrectnessMetric` 0.85; `check_sequence` lookup → ticket | every PR | offline: free | agent team |

---

## 4. Golden Data

| Dataset | Cases | Categories | Owner | Last reviewed |
|---|---|---|---|---|
| | | | | |

At least one hard case per category; expected outputs written or approved by a domain expert; every fixed bug becomes a new case.

---

## 5. Quality Gate (CI)

Defaults from `config/eval_config.yaml` → `gates`; change them here only with a reason.

| Gate | Rule | Blocks merge? |
|---|---|---|
| Smoke (every push) | 100% of the smoke cases pass | Yes |
| Pass rate (PR) | ≥ 80% of golden cases pass | Yes |
| Critical metrics (PR) | Faithfulness, Answer Correctness, Answer Relevancy averages ≥ 0.7 | Yes |
| Regression (PR) | No metric more than 5 points below the stored baseline; no newly failing case | Yes |
| Red team | 100% of red-team cases blocked | Yes |
| Reliability | p95 latency ≤ ____ s; cost per task ≤ $____ (verify current pricing); ≤ ____ LLM calls per task | Yes / warn |

---

## 6. Production Monitoring

| Signal | How | Alert when |
|---|---|---|
| Quality drift | 7-day rolling average of judge scores on sampled traffic | below the dimension threshold, or more than 5 points below the launch baseline |
| Cost | cost per task from traces | above the reliability limit |
| Failures and loops | trace levels, LLM calls per task | above baseline |
| Safety | PII scanner on sampled replies, red-team re-runs on model changes | any finding |

---

## 7. Sign-Off

Approvals are recorded in the audit trail (`monitoring/governance.py`), not only here.

| Role | Name | Date | Approved |
|------|------|------|----------|
| QA lead | | | [ ] |
| Product owner | | | [ ] |
| Security | | | [ ] |
| Engineering manager | | | [ ] |
