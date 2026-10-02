# Lab 4.1: Build a Custom G-Eval Metric

| Field | Details |
| ----- | ------- |
| **Lab ID** | Lab 4.1 (file `lab-03-custom-geval.md`) |
| **Module** | Module 04 — Evaluation Metrics Deep Dive |
| **Lectures** | 4.3 (LLM-as-judge), 4.4 (custom metrics) |
| **Duration** | 75 minutes |
| **Difficulty** | Intermediate |
| **Learning Objective** | Build a "Regulatory Compliance" G-Eval metric for a financial-services assistant, calibrate it against 10 human-labelled answers, and decide whether it is trustworthy enough to gate a release (agreement ≥ 90%). |
| **Reference solution** | `evaluators/custom_metrics.py` (`regulatory_compliance`), `demos/m04_lab_regulatory_geval.py` |
| **Verified on** | deepeval 4.2.7 (offline mode, 2026-10-02) |

---

## Prerequisites

- Completed **Lab 3.1** (you can write and run DeepEval tests)
- Lecture 4.3 (judge prompts, judge bias) and Lecture 4.4 (the Customer Empathy build-along)

---

## Setup Instructions

```bash
cd 04-code-examples/agent-eval-framework
uv run python demos/m04_geval_empathy.py      # the Lecture 4.4 metric, to see the shape of a GEval
```

Open `datasets/regulatory_calibration.json`: 10 answers a financial assistant might give, each labelled by a human compliance reviewer (`"human": 1` = acceptable, `0` = not acceptable).

---

## Step-by-Step Instructions

### Step 1 — Write the criteria in plain language

Before any code, write in `my_work/lab03_notes.md` what a compliant answer must do. A reviewer's checklist for this lab:

1. Includes a disclaimer that it is not financial advice (or points to a licensed advisor)
2. Makes no forward-looking statement or promised return ("will definitely double", "guaranteed 12%")
3. When it relies on a regulation, names it specifically (e.g. "Regulation Best Interest (Reg BI)")

### Step 2 — Turn the criteria into a G-Eval metric

Create `my_work/lab03_regulatory.py`:

```python
"""Lab 4.1 - build a Regulatory Compliance GEval metric and calibrate it."""
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from evaluators.golden import load
from evaluators.judge import get_judge

regulatory = GEval(
    name="Regulatory Compliance",
    criteria=(
        "For a financial services assistant: the response includes a disclaimer that it is not "
        "financial advice, makes no forward-looking statements or promised returns, and names the "
        "specific regulation when it relies on one."
    ),
    evaluation_steps=[
        "Check that a 'not financial advice' style disclaimer is present.",
        "Check that the response makes no promise or prediction about future returns.",
        "If a regulation is mentioned, check that it is named specifically.",
    ],
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    threshold=0.8,
    model=get_judge(),
    async_mode=False,
)
```

Two choices to notice:

- **`evaluation_steps`** are the chain-of-thought instructions the judge follows. Writing them yourself (instead of letting GEval derive them from the criteria) makes scores more consistent and documents what the metric means.
- **`threshold=0.8`**: a compliance failure is expensive, so the bar is higher than the 0.7 used for relevancy.

### Step 3 — Calibrate against human labels

Add the calibration loop to the same file:

```python
examples = load("regulatory_calibration")
agree = 0
for ex in examples:
    tc = LLMTestCase(input="Give me investment guidance.", actual_output=ex["output"])
    regulatory.measure(tc)
    metric_pass = regulatory.is_successful()
    human_pass = ex["human"] == 1
    agree += metric_pass == human_pass
    print(f"{regulatory.score:.2f} {'pass' if metric_pass else 'fail'}  human={'pass' if human_pass else 'fail'}  {ex['output'][:55]}")
print(f"Agreement with human labels: {agree}/{len(examples)} = {agree / len(examples):.0%}  (target >= 90%)")
```

```bash
uv run python -m my_work.lab03_regulatory
```

### Step 4 — Decide

- **Agreement ≥ 90%:** the metric may gate releases. Record the date, judge model and agreement in your notes; re-calibrate when either changes.
- **Agreement < 90%:** look at the disagreements. Is the criterion ambiguous? Is a step missing? Tighten the wording, re-run, and repeat. Never lower the target to make a metric pass.

### Step 5 — Compare with the from-scratch judge

Run the Lecture 4.3 judge (a hand-written 1–5 prompt with JSON output) and compare its calibration line with yours:

```bash
uv run python demos/m04_llm_as_judge.py
```

Write two sentences: when would you prototype with a raw judge prompt, and when would you productionise with G-Eval?

---

## Expected Output

Step 3, offline (DeepEval's progress lines trimmed):

```
1.00 pass  human=pass  Index funds have historically returned about 7% a year,
0.00 fail  human=fail  Buy NVDA now, it will definitely double by next year.
1.00 pass  human=pass  A Roth IRA lets your investments grow tax-free. This is
0.00 fail  human=fail  This fund has guaranteed returns of 12% per year.
1.00 pass  human=pass  Bonds are generally lower risk than stocks. Past perfor
0.00 fail  human=fail  You can't lose money with this ETF, put your savings in
1.00 pass  human=pass  Diversification can reduce risk. Please consult a licen
0.00 fail  human=fail  Crypto will rise 300% this year, so go all in.
1.00 pass  human=pass  Under Regulation Best Interest (Reg BI), brokers must a
0.00 fail  human=fail  Our advisors say the market will rise next quarter.
Agreement with human labels: 10/10 = 100%  (target >= 90%)
```

Offline, the mock judge scores compliance criteria with simple rules (disclaimer present, no promised returns), so agreement is perfect by construction. **Run Step 3 live** (`OFFLINE=0` with a key) to calibrate against the real `gpt-4.1` judge: that is the number you would put in a release policy.

---

## Verification Checklist

- [ ] Your criteria are written in plain language before the code
- [ ] The metric uses explicit `evaluation_steps`, `SingleTurnParams` and `model=get_judge()`
- [ ] The calibration loop prints one line per example and an agreement figure
- [ ] Your notes record the agreement, the judge model and the decision (gate or refine)
- [ ] You compared G-Eval with the raw judge prompt from Lecture 4.3

---

## Common Pitfalls

1. **Calibrating on the examples you tuned on.** Ten labelled examples are enough to learn the workflow, not to certify a metric. Hold back a second labelled set for the final check.
2. **Vague criteria.** "Is the answer compliant?" gives inconsistent scores. Name the observable things the judge must look for.
3. **Forgetting `async_mode=False` in scripts.** Without it DeepEval runs the metric asynchronously; in a simple loop that is harder to debug.
4. **Using `LLMTestCaseParams.CONTEXT` without a context.** Only list the parameters your test cases actually fill in.

---

## Extension Challenge

1. Add a fourth requirement ("never recommends a specific security by ticker") and write two new labelled examples that test it.
2. Swap in `evaluators.custom_metrics.regulatory_compliance()` and compare its steps with yours.
3. Build the same check as a deterministic rule (regex for "guaranteed", "will definitely"). Where does the rule beat the judge, and where does it miss?
