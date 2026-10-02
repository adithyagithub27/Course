# Lab 11.1: Generate, Baseline, Regress, Catch

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 11.1 (file `lab-10-synthetic-data.md`) |
| **Module** | Module 11 — Regression Testing & Synthetic Data |
| **Lectures** | 11.1–11.3 |
| **Duration** | 75 minutes |
| **Difficulty** | Intermediate |
| **Learning Objective** | Generate synthetic test cases with DeepEval's `Synthesizer`, record a baseline, simulate a one-line prompt regression, catch it with a baseline comparison, fix it and confirm the scores return to baseline. |
| **Reference solution** | `regression/synthetic_data.py`, `regression/regression_suite.py`, `demos/m11_lab_generate_regress_catch.py` |
| **Verified on** | deepeval 4.2.7, openai 2.54.0 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Lab 3.1** (golden datasets, `run_suite`) and **Lab 4.1** (custom metrics)
- Lectures 11.1–11.3: causes of regression, baselines and tolerances, the Synthesizer

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
uv run python demos/m11_regression_simulation.py     # the regression you will reproduce
```

Read `regression/synthetic_data.py`. The course's synthesizer is DeepEval's own:

```python
STYLING = StylingConfig(
    scenario="Customers of TechCorp, a SaaS company, contacting support by chat",
    task="Answer questions about plans, billing, refunds, passwords and the API",
    input_format="Short, informal customer messages in English",
    expected_output_format="One to three sentences, grounded in the knowledge base",
)
```

| Function | DeepEval call | Use |
|---|---|---|
| `from_seeds(per_seed)` | `generate_goldens_from_goldens(seed_goldens(), max_goldens_per_golden=per_seed)` | expand the 5 seeds in `datasets/synthetic_seeds.json` (`per_seed=20` gives 100) |
| `from_knowledge_base(per_context)` | `generate_goldens_from_contexts(contexts=[[article], ...], max_goldens_per_context=per_context)` | questions grounded in the 5 knowledge-base articles |
| `from_policies(per_context)` | same, over the 14 policy documents | for the RAG agent |
| `quality_report(goldens)` | — | count, duplicates, length, vocabulary |

> Offline, the mock judge fills the Synthesizer's templates, so questions are formulaic ("Can you explain the refund policy for my team? ..."). Live, gpt-4.1 writes varied ones. Never present offline synthetic questions as typical LLM output.

---

## Step-by-Step Instructions

### Step 1 — Generate

Create `my_work/lab10_synth.py`:

```python
"""Lab 11.1 - generate, baseline, regress, catch, fix."""
from agents.support_agent import SYSTEM_PROMPT, run_support_agent
from evaluators.deepeval_suite import run_suite
from evaluators.metrics import answer_relevancy, faithfulness
from regression.regression_suite import compare
from regression.synthetic_data import from_knowledge_base, quality_report

# 1. Generate: DeepEval Synthesizer over the 5 knowledge-base articles
goldens = from_knowledge_base(per_context=2)
print("1. generated:", quality_report(goldens))
cases = [{"id": f"SYN-{i:02d}", "category": "synthetic", "input": g.input, "context": g.context}
         for i, g in enumerate(goldens, 1)]
metrics = lambda case: [answer_relevancy(), faithfulness()]  # noqa: E731
```

Print three of the generated `goldens` and read them. Would a real TechCorp customer ask these? Keep notes: human review of a sample is part of the process.

### Step 2 — Baseline

```python
RULE = "- Only state prices, limits and policies that appear in a knowledge base result\n"
def agent(prompt):  # temperature=0 so every run of the same version is identical
    return lambda q: run_support_agent(q, temperature=0, system_prompt=prompt)

base = run_suite(cases, agent(SYSTEM_PROMPT), metrics)
baseline = {"averages": base["averages"], "pass_rate": base["pass_rate"],
            "cases": {d["id"]: d["passed"] for d in base["details"]}}
print(f"2. baseline:  pass rate {base['pass_rate']:.0%}  {base['averages']}")
```

The baseline is not 100%: synthetic questions find cases the hand-written golden set does not. That is their value. The baseline records where you are, so the gate can tell you when you get worse.

### Step 3 — Regress and catch

```python
bad = run_suite(cases, agent(SYSTEM_PROMPT.replace(RULE, "")), metrics)
diff = compare(baseline, bad)
print(f"3. regressed: pass rate {bad['pass_rate']:.0%}  {bad['averages']}")
print(f"4. caught:    regression={diff['regression']} metrics={diff['regressed_metrics']} newly failing={diff['newly_failing']}")
```

`compare()` (`regression/regression_suite.py`) flags a metric that drops more than `regression_tolerance` (0.05, from `config/eval_config.yaml`) and every case that passed in the baseline and fails now.

### Step 4 — Fix and confirm

```python
fixed = run_suite(cases, agent(SYSTEM_PROMPT), metrics)
print(f"5. fixed:     pass rate {fixed['pass_rate']:.0%}  regression={compare(baseline, fixed)['regression']}")
```

```bash
uv run python -m my_work.lab10_synth
```

### Step 5 — Scale up

```bash
make synthetic        # 5 seeds x 20 = 100 goldens, saved to reports/results/synthetic_goldens.json
```

Open the file. Before adding any of these to `datasets/`, review a sample, drop duplicates and near-duplicates, and write expected outputs you trust.

---

## Expected Output

```
1. generated: {'count': 10, 'unique': 10, 'duplicate_rate': 0.0, 'avg_words': 17.1, 'distinct_content_words': 35, 'with_expected_output': 10}
2. baseline:  pass rate 80%  {'Answer Relevancy': 0.9, 'Faithfulness': 1.0}
3. regressed: pass rate 60%  {'Answer Relevancy': 0.8, 'Faithfulness': 0.8}
4. caught:    regression=True metrics=['Answer Relevancy', 'Faithfulness'] newly failing=['SYN-02', 'SYN-08']
5. fixed:     pass rate 80%  regression=False
```

On the hand-written golden dataset the same one-line edit is even more visible (`demos/m11_regression_simulation.py`): pass rate 100% → 70%, Faithfulness 1.00 → 0.25, Answer Correctness 0.98 → 0.74, and GS-01, GS-02, GS-03 fail.

---

## Verification Checklist

- [ ] Goldens come from DeepEval's `Synthesizer` (`generate_goldens_from_contexts` or `generate_goldens_from_goldens`), not a hand-rolled JSON prompt
- [ ] You reviewed a sample of the generated questions and noted problems
- [ ] The baseline is stored before the change
- [ ] The regression is caught by `compare()` with the configured tolerance, and you can name the newly failing cases
- [ ] After the fix, `regression=False`
- [ ] Runs use `temperature=0` so the same version gives the same scores

---

## Common Pitfalls

1. **Comparing runs with randomness on.** At the default temperature, two runs of the same version can differ. Use `temperature=0` for regression comparisons, or compare averages over several runs.
2. **Treating synthetic data as ground truth.** Generated expected outputs can be wrong. They widen coverage; the hand-written golden set stays the authority.
3. **A baseline that moves.** Re-record a baseline (`make baseline`) only on purpose, after a reviewed, intended change, never to make a failing gate pass.
4. **Tolerance too loose or too tight.** 5 points catches this regression; a 20-point tolerance would let it ship. Tune with the data you have.

---

## Extension Challenge

1. Generate 20 questions from the policy documents (`from_policies(per_context=2)`) and run them through the RAG agent with the Module 5 metrics.
2. Live only: generate with gpt-4.1 and compare `quality_report()` with the offline run (unique count, vocabulary).
3. Use `EvaluationDataset(goldens=...)` (`regression.synthetic_data.as_dataset`) and push it to a dataset store of your choice, keyed by agent version.
