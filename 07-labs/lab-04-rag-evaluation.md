# Lab 5.1: RAG Pipeline Evaluation with RAGAS 0.4

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 5.1 (file `lab-04-rag-evaluation.md`) |
| **Module** | Module 05 — RAG Agent Evaluation |
| **Lectures** | 5.1–5.3 (prepares Project 2, Lecture 5.4) |
| **Duration** | 75 minutes |
| **Difficulty** | Intermediate |
| **Learning Objective** | Score the TechCorp Policy Assistant with the four RAGAS 0.4 metrics, tell a retrieval failure from a generation failure, and fix the retrieval failure in the retriever. |
| **Reference solution** | `demos/m05_ragas_metrics.py`, `demos/m05_rag_failure_dissection.py`, `demos/m05_component_isolation.py` |
| **Verified on** | ragas 0.4.3, deepeval 4.2.7 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Lab 3.1**
- Lectures 5.1–5.3: retrieval vs generation, the four RAGAS metrics, component isolation

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
uv run python -c "import ragas; print(ragas.__version__)"     # 0.4.3
```

Two files to read before you start:

- `agents/rag_agent.py` — the **Policy Assistant**: 14 TechCorp policy documents in three domains (HR, IT security, travel & expense), a keyword retriever (`retrieve_context`) standing in for vector search, and a generator that answers from the retrieved text and cites its source.
- `evaluators/ragas_suite.py` — the RAGAS 0.4 helpers: `to_sample()`, `build_dataset()`, `make_metrics()`, `evaluate_dataset()`, `aggregate()`, `diagnose()`.

### RAGAS 0.4 in one minute

| Old (0.1-era, removed) | Current (0.4.3) |
|---|---|
| `from ragas.metrics import faithfulness` (lowercase instances) | `from ragas.metrics.collections import Faithfulness, ContextPrecision, ContextRecall, AnswerRelevancy` (classes) |
| `evaluate(Dataset.from_dict({...}), metrics=[...])` | `EvaluationDataset(samples=[SingleTurnSample(...)])`, then `await metric.ascore(...)` per metric |
| columns `question`, `answer`, `contexts`, `ground_truth` | fields `user_input`, `response`, `retrieved_contexts`, `reference` |

Live, each metric gets an LLM from `ragas.llms.llm_factory("gpt-4.1", client=AsyncOpenAI())` (and AnswerRelevancy an embedding model, `text-embedding-3-small`). Offline, `MockRagasLLM` and `MockEmbeddings` implement RAGAS's own base classes, so the metric code you run is the real RAGAS code.

---

## Step-by-Step Instructions

### Step 1 — Score five questions

Create `my_work/lab04_rag.py`:

```python
"""Lab 5.1 - score the Policy Assistant with RAGAS 0.4 and diagnose failures."""
from agents.rag_agent import run_rag_agent
from evaluators.golden import load
from evaluators.ragas_suite import aggregate, build_dataset, diagnose, evaluate_dataset, to_sample

IDS = ["RAG-HR-01", "RAG-HR-04", "RAG-IT-03", "RAG-TE-02", "RAG-TE-05"]
cases = [c for c in load("golden_rag") if c["id"] in IDS]

samples = []
for case in cases:
    result = run_rag_agent(case["question"])
    samples.append(to_sample(case["question"], result, reference=case["reference"]))

dataset = build_dataset(samples)              # ragas EvaluationDataset of SingleTurnSamples
rows = evaluate_dataset(dataset)              # four RAGAS 0.4 metrics per sample
for case, scores in zip(cases, rows):
    print(f"{case['id']:<10} {scores}  -> {diagnose(scores)}")
print("Aggregate:", aggregate(rows))
```

```bash
uv run python -m my_work.lab04_rag
```

Open `evaluators/ragas_suite.py` and read `to_sample()` (how an agent result becomes a `SingleTurnSample`) and `ascore_sample()` (which fields each metric needs).

### Step 2 — Diagnose RAG-TE-05

RAG-TE-05 asks "What is the mileage reimbursement rate for using my own car?". Context precision and recall are 1.0: the right document was retrieved at rank 1. Faithfulness and answer relevancy are 0.0: the generator said the documents don't cover it. `diagnose()` says **generation**. Confirm it with component isolation:

```bash
uv run python demos/m05_component_isolation.py
```

The retriever hits 5/5 travel questions at rank 1, but the generator given the perfect context still fails RAG-TE-05. Fixing chunking would waste a week; the fix belongs in the prompt or the model.

### Step 3 — A retrieval failure

Ask a question whose answer lives in `travel-001` (Travel Booking, Section 7.2). Create `my_work/lab04_retriever.py`:

```python
"""Lab 5.1 step 3 - the retrieval failure, and the one-line retriever fix."""
from agents.rag_agent import retrieve_context

question = "What class can I fly on a long flight?"
for remove_stopwords in (False, True):
    docs = retrieve_context(question, top_k=3, remove_stopwords=remove_stopwords)
    print(f"remove_stopwords={remove_stopwords}: {[d['id'] for d in docs]}")
```

```bash
uv run python -m my_work.lab04_retriever
```

The shipped retriever counts stop words ("what", "can", "on", "a"), so documents full of common words outrank the travel policy. With stop words removed, `travel-001` is retrieved.

### Step 4 — Prove the fix end to end

```bash
uv run python demos/m05_rag_failure_dissection.py
```

Before: all four RAGAS scores 0.0, diagnosis "both". After: faithfulness 1.0, answer relevancy 1.0, context recall 1.0, the correct answer with its citation. Context precision is 0.5, not 1.0: what does that tell you about the other two retrieved documents?

### Step 5 — Write the diagnosis

In `my_work/lab04_report.md`, write one paragraph per failure: question, scores, diagnosis (retrieval or generation), evidence, and the fix you recommend. This is the format Project 2 asks for across all 15 questions.

---

## Expected Output

Step 1:

```
RAG-HR-01  {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 1.0, 'context_recall': 1.0}  -> ok
RAG-HR-04  {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 1.0, 'context_recall': 1.0}  -> ok
RAG-IT-03  {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 1.0, 'context_recall': 1.0}  -> ok
RAG-TE-02  {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 1.0, 'context_recall': 1.0}  -> ok
RAG-TE-05  {'faithfulness': 0.0, 'answer_relevancy': 0.0, 'context_precision': 1.0, 'context_recall': 1.0}  -> generation
Aggregate: {'faithfulness': 0.8, 'answer_relevancy': 0.8, 'context_precision': 1.0, 'context_recall': 1.0}
```

Step 3:

```
remove_stopwords=False: ['vacation-001', 'itsec-001', 'travel-002']
remove_stopwords=True: ['itsec-001', 'travel-001', 'vacation-001']
```

Step 4 (from the demo):

```
BEFORE: naive keyword retriever
  retrieved: ['vacation-001', 'itsec-001', 'travel-002']  (the answer lives in travel-001)
  answer   : The policy documents provided don't cover that question. Please contact HR or the IT Service Desk for help.
  RAGAS    : {'faithfulness': 0.0, 'answer_relevancy': 0.0, 'context_precision': 0.0, 'context_recall': 0.0}
  diagnosis: both
AFTER: stop words removed
  retrieved: ['itsec-001', 'travel-001', 'vacation-001']  (the answer lives in travel-001)
  answer   : Economy class is required for flights under 6 hours; premium economy is allowed for flights of 6 hours or more. (Source: Travel Booking (Section 7.2))
  RAGAS    : {'faithfulness': 1.0, 'answer_relevancy': 1.0, 'context_precision': 0.5, 'context_recall': 1.0}
  diagnosis: retrieval
```

---

## Verification Checklist

- [ ] Your script builds `SingleTurnSample`s with `reference`, not `ground_truth`
- [ ] Your metrics come from `ragas.metrics.collections` (via `make_metrics()`), not the removed lowercase imports
- [ ] You can explain why RAG-TE-05 is a generation failure using two numbers
- [ ] You reproduced the retrieval failure and the stop-word fix
- [ ] Your report has one paragraph per failure with a recommended fix

---

## Common Pitfalls

1. **Copying 0.1-era tutorials.** `from ragas.metrics import faithfulness` and `evaluate(Dataset.from_dict(...))` no longer work in 0.4.3. Use the classes and `SingleTurnSample`.
2. **Installing `langchain-community` 0.4.2.** RAGAS 0.4.3 imports a module that release removed. The repo pins `langchain-community<0.4.2` in `pyproject.toml`; keep the pin if you add packages.
3. **Reading faithfulness alone.** High faithfulness only says the answer matches what was retrieved. If the wrong documents were retrieved, the answer can be faithful and wrong. Always read it with context precision and recall.
4. **NaN scores.** A metric that cannot score (for example, no `reference`) returns NaN; the helper turns it into 0.0. Check your inputs before believing a zero.

---

## Extension Challenge

1. Run all 15 questions (`uv run python demos/m05_project2_rag_eval.py`) and find the second generation failure (RAG-IT-02 has answer relevancy 0.0). Explain it.
2. Retrieve with `include_noise=True` (two off-topic documents) and measure what happens to context precision.
3. Score the same five samples with DeepEval's `ContextualPrecisionMetric` and `ContextualRecallMetric` (`evaluators.metrics.contextual_precision()`, `contextual_recall()`) and compare the two frameworks' numbers.
