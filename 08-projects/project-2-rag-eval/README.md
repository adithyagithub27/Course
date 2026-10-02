# Project 2: Evaluate an Enterprise RAG Agent

> **"Which half of the pipeline is broken? Prove it with numbers."**

| Detail | Value |
|--------|-------|
| **Module Reference** | Module 05 — RAG Agent Evaluation (Lecture 5.4) |
| **Difficulty** | Intermediate |
| **Estimated Time** | 45–60 minutes |
| **Prerequisites** | Project 1, Lab 5.1, Lectures 5.1–5.3 |
| **Reference solution** | `demos/m05_project2_rag_eval.py` (writes `reports/results/project2_report.md`) |
| **Verified on** | ragas 0.4.3, deepeval 4.2.7 (offline mode, 2026-10-02) |

---

## Enterprise Scenario

**TechCorp — Internal Policy Assistant** (illustrative)

TechCorp's people team launched a **Policy Assistant** for employees: ask a question about vacation, remote work, passwords, phishing, expenses or travel, and it answers from the company's policy documents with a citation. Two weeks in, the IT security lead forwards complaints: some answers say "the documents don't cover that" when they clearly do, and one answer about mileage was useless.

Leadership asks for a diagnostic report before they decide whether to buy a vector database (a retrieval fix) or switch models (a generation fix). Your job: evaluate the assistant on a 15-question golden set, per policy domain, and say which half of the pipeline fails for which questions.

---

## Learning Objectives

1. Evaluate a RAG agent with the four RAGAS 0.4 metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall
2. Build `SingleTurnSample`s (`user_input`, `response`, `retrieved_contexts`, `reference`) and an `EvaluationDataset`
3. Diagnose each failure as **retrieval**, **generation**, or **both**, and confirm the diagnosis with component isolation
4. Report scores per domain and recommend a specific fix for each failure

---

## The Agent Under Test

`agents/rag_agent.py`, the **TechCorp Policy Assistant**: 14 policy documents in three domains, plus 2 off-topic noise documents (`include_noise=True`).

| Domain | Documents (title, section) |
|---|---|
| hr | Vacation Policy 4.1, Remote Work 5.2, Sick Leave 4.3, Performance Review 6.1, Health Benefits 8.1 |
| it_security | Password and MFA IT-1, Device and Laptop IT-2, Phishing IT-3, Data Classification IT-4, VPN IT-5 |
| travel_expense | Expense 7.1, Travel Booking 7.2, Meals 7.3, Mileage 7.4 |

| Function | What it does |
|---|---|
| `retrieve_context(query, top_k=3, include_noise=False, remove_stopwords=False)` | Keyword retriever standing in for vector search: 3 × title-word overlap + content-word overlap. The shipped default counts stop words: that is a real weakness you will find |
| `generate_answer(question, contexts)` | Answers from the retrieved text and cites `(Source: Title (Section x))` |
| `run_rag_agent(question, ...)` | Both steps; returns `answer`, `retrieved_contexts`, `retrieved_ids`, `retrieved_titles`, `total_tokens`, `latency_s`, `model` |

The golden set is `datasets/golden_rag.json`: 15 questions (RAG-HR-01..05, RAG-IT-01..05, RAG-TE-01..05), each with `question`, `reference` (the correct answer), `reference_context_ids` and `domain`.

---

## Architecture

```
datasets/golden_rag.json (15)          agents/rag_agent.py
          |                     question  |
          |  -------------------------->  retrieve_context()  --> top-3 documents
          |                               generate_answer()   --> answer + citation
          v                                       |
  reference answer  ------->  SingleTurnSample(user_input, response, retrieved_contexts, reference)
                                                  |
                                     EvaluationDataset(samples=[...])
                                                  |
             +--------------------+---------------+---------------+--------------------+
             v                    v                               v                    v
       Context Precision    Context Recall                  Faithfulness        Answer Relevancy
       (retrieval)          (retrieval)                     (generation)        (generation)
             +--------------------+---------------+---------------+--------------------+
                                                  |
                                       diagnose(): retrieval | generation | both | ok
                                                  |
                          per-domain report + recommendations (project2_report.md)
```

Thresholds (`evaluators/ragas_suite.py`, `RAG_THRESHOLDS`, aligned with `config/eval_config.yaml`): faithfulness 0.8, answer relevancy 0.7, context precision 0.7, context recall 0.7.

---

## Requirements Specification

| # | Requirement | Acceptance criteria |
|---|-------------|---------------------|
| R1 | Dataset | All 15 golden questions, plus at least 3 of your own (one per domain) with a `reference` answer |
| R2 | RAGAS 0.4 pipeline | Samples are `SingleTurnSample`s with `reference` (not `ground_truth`); metrics are the classes from `ragas.metrics.collections` (via `make_metrics()`) |
| R3 | Diagnosis | Every question gets a diagnosis (`ok`, `retrieval`, `generation`, `both`) |
| R4 | Component isolation | For every failure, test the retriever alone (is the reference document in the top 3?) and the generator alone (perfect context) |
| R5 | Report | Per-domain averages, overall averages, failing questions with evidence, and one recommendation per failure |

---

## Step-by-Step Build Guide

### Step 1: Run the reference evaluation

```bash
uv run python demos/m05_project2_rag_eval.py
```

Read the table and find the two failing questions.

### Step 2: Write your own evaluation script

Create `my_work/project2_rag_eval.py`:

```python
"""Project 2 - RAGAS 0.4 evaluation of the Policy Assistant, with per-domain diagnosis."""
from collections import defaultdict

from agents.rag_agent import run_rag_agent
from evaluators.golden import load
from evaluators.ragas_suite import aggregate, build_dataset, diagnose, evaluate_dataset, to_sample

cases = load("golden_rag")                    # + your own cases
samples = [to_sample(c["question"], run_rag_agent(c["question"]), reference=c["reference"]) for c in cases]
rows = evaluate_dataset(build_dataset(samples))

by_domain = defaultdict(list)
for case, scores in zip(cases, rows):
    by_domain[case["domain"]].append(scores)
    print(f"{case['id']:<10} {scores}  {diagnose(scores)}")
for domain, domain_rows in by_domain.items():
    print(domain, aggregate(domain_rows))
print("overall", aggregate(rows))
```

```bash
uv run python -m my_work.project2_rag_eval
```

### Step 3: Isolate the components

```bash
uv run python demos/m05_component_isolation.py
```

For each failing question, check (a) whether `reference_context_ids[0]` is in `run_rag_agent(q)["retrieved_ids"]` and at what rank, and (b) whether `generate_answer(q, [the reference document])` is correct. Record both.

### Step 4: Try the retrieval fix

Re-run with `retrieve_context(..., remove_stopwords=True)` (the Lecture 5.1 fix) and with `include_noise=True`. Which scores move, and for which domain?

### Step 5: Write the report

In `reports/results/project2_report.md` (or your own file): the per-domain table, the overall averages, each failing question with scores, diagnosis, evidence from Step 3 and a recommended fix. End with a one-paragraph answer to leadership: vector database or model change?

---

## Expected Output

The reference run (offline):

```
id         faithfulness  answer_relevancy  context_precision  context_recall  diagnosis 
---------  ------------  ----------------  -----------------  --------------  ----------
RAG-HR-01  1.0           1.0               1.0                1.0             ok        
RAG-HR-02  1.0           1.0               1.0                1.0             ok        
RAG-HR-03  1.0           1.0               1.0                1.0             ok        
RAG-HR-04  1.0           1.0               1.0                1.0             ok        
RAG-HR-05  1.0           1.0               1.0                1.0             ok        
RAG-IT-01  1.0           1.0               1.0                1.0             ok        
RAG-IT-02  1.0           0.0               1.0                1.0             generation
RAG-IT-03  1.0           1.0               1.0                1.0             ok        
RAG-IT-04  1.0           1.0               1.0                1.0             ok        
RAG-IT-05  1.0           1.0               1.0                1.0             ok        
RAG-TE-01  1.0           1.0               0.833              1.0             ok        
RAG-TE-02  1.0           1.0               1.0                1.0             ok        
RAG-TE-03  1.0           1.0               1.0                1.0             ok        
RAG-TE-04  1.0           1.0               0.833              1.0             ok        
RAG-TE-05  0.0           0.0               1.0                1.0             generation
# Project 2 - RAG diagnostic report
| Domain | faithfulness | answer_relevancy | context_precision | context_recall | diagnosis |
|---|---|---|---|---|---|
| hr | 1.0 | 1.0 | 1.0 | 1.0 | ok |
| it_security | 1.0 | 0.8 | 1.0 | 1.0 | ok |
| travel_expense | 0.8 | 0.8 | 0.933 | 1.0 | ok |
Overall: {'faithfulness': 0.933, 'answer_relevancy': 0.867, 'context_precision': 0.978, 'context_recall': 1.0}
```

Two generation failures: RAG-TE-05 (mileage: the right document is retrieved at rank 1, but the generator says the documents don't cover it; a paraphrase gap) and RAG-IT-02 (answer relevancy 0.0). Domain averages can say "ok" while a question inside fails: always read the per-question rows. Offline scores come from the deterministic mock judge; re-run live before quoting them.

---

## Expected Deliverables

| # | Deliverable | Location |
|---|-------------|----------|
| D1 | Evaluation script | `my_work/project2_rag_eval.py` |
| D2 | Your added cases | `my_work/golden_rag_extra.json` |
| D3 | Component isolation evidence | notes or output for each failure |
| D4 | Diagnostic report | `reports/results/project2_report.md` or your own Markdown file |

---

## Evaluation Rubric

| Dimension | 5 (Excellent) | 3 (Adequate) | 1 (Needs Work) |
|-----------|--------------|--------------|-----------------|
| **RAGAS usage** | Current 0.4 API (`SingleTurnSample`, `reference`, metric classes) | Works but mixes in deprecated patterns | 0.1-era API, does not run |
| **Diagnosis** | Every failure diagnosed and confirmed by isolation | Diagnosis from scores only | No diagnosis |
| **Domain view** | Per-domain table plus per-question failures | Overall averages only | No aggregation |
| **Recommendations** | One concrete fix per failure, tied to the evidence | Generic advice | None |
| **Your cases** | 3+ new cases that test a real weakness (noise, stop words, paraphrase) | Cases added but trivial | None |

---

## Extension Ideas

1. Score the same samples with DeepEval's `ContextualPrecisionMetric` / `ContextualRecallMetric` (`evaluators.metrics.contextual_precision()`, `contextual_recall()`) and compare with RAGAS.
2. Generate 20 synthetic policy questions with `regression.synthetic_data.from_policies()` (Module 11) and run them through this pipeline.
3. Replace the keyword retriever with an embedding retriever of your choice and show the before/after table.

---

## Common Issues & Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: cannot import name 'faithfulness' from 'ragas.metrics'` | That is the 0.1-era API, removed in 0.4.3. Use `from ragas.metrics.collections import Faithfulness` (or the course's `make_metrics()`) |
| `ground_truth` field errors | The 0.4 field is `reference` |
| `langchain_community` import error inside RAGAS | Keep the `langchain-community<0.4.2` constraint from `pyproject.toml` |
| NaN scores | A metric could not score (missing `reference` or empty contexts); the helper turns NaN into 0.0, so check your inputs |
| Live run is slow | RAGAS makes several judge calls per metric; run offline while developing (verify current pricing for live runs) |

---

## What You Learned

> "I evaluated an internal policy RAG assistant with RAGAS 0.4 on 15 golden questions across three domains. I separated retrieval from generation with context precision and recall versus faithfulness and answer relevancy, confirmed each diagnosis by testing the retriever and generator in isolation, and recommended fixes per failure — a retrieval fix for one class of questions and a generation fix for another — instead of a blanket 'buy a vector database'."

**Next project:** [Project 3 — Test a Multi-Tool Agent](../project-3-tool-calling/README.md) (Module 06)
