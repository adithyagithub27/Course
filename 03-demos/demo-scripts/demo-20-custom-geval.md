# Demo 20 — Building Custom G-Eval Metrics

**Used in:** Lecture 4.4 (Custom Metrics: G-Eval); Lab 4.1
**Lecture type:** Build-along
**Duration:** ~2.5 minutes of screen recording
**Purpose:** Build a Customer Empathy GEval with explicit evaluation steps, then calibrate a Regulatory Compliance metric against 10 human labels.
**Demo file(s):** `demos/m04_geval_empathy.py`, `demos/m04_lab_regulatory_geval.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m04_geval_empathy.py`; `uv run python demos/m04_lab_regulatory_geval.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Empathy metric (60 s)

`evaluators/custom_metrics.py`, `customer_empathy()` (bible §8.7). Run `m04_geval_empathy.py`: empathetic 0.90 PASS, flat 0.60 FAIL, rude 0.00 FAIL.

### Scene 2: Calibration (60 s)

Run `m04_lab_regulatory_geval.py`: 10 answers, metric vs human, agreement 1.0; target ≥ 0.9 before the metric gates anything.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m04_geval_empathy.py
Criteria: Does the response show empathy for the customer's situation while still solving the problem?
Evaluation steps:
  - Criteria: empathy - does the response acknowledge the customer's feelings?
  - Check whether the response acknowledges the customer's feelings in the first sentence.
  - Check whether the response offers a concrete next step, not just sympathy.
  - Penalize blame, sarcasm, or rude language heavily.
empathetic  score 0.90 PASS  I'm sorry for the frustration, and thank you for flagging it. I've opened a high-priority ticket so billing can refund the duplicate charge.
            reason: Professional and acknowledges the customer.
flat        score 0.60 FAIL  A ticket has been created for the duplicate charge.
            reason: Polite but does not acknowledge the customer's frustration.
rude        score 0.00 FAIL  Stop shouting. Read the docs yourself, you idiot.
            reason: Uses insulting language.
```

```
$ uv run python demos/m04_lab_regulatory_geval.py
output                                                                  score  metric  human  agree
----------------------------------------------------------------------  -----  ------  -----  -----
Index funds have historically returned about 7% a year, but past perfo  1.00   pass    pass   yes  
Buy NVDA now, it will definitely double by next year.                   0.00   fail    fail   yes  
A Roth IRA lets your investments grow tax-free. This is not financial   1.00   pass    pass   yes  
This fund has guaranteed returns of 12% per year.                       0.00   fail    fail   yes  
Bonds are generally lower risk than stocks. Past performance is not in  1.00   pass    pass   yes  
You can't lose money with this ETF, put your savings in it.             0.00   fail    fail   yes  
Diversification can reduce risk. Please consult a licensed financial a  1.00   pass    pass   yes  
Crypto will rise 300% this year, so go all in.                          0.00   fail    fail   yes  
Under Regulation Best Interest (Reg BI), brokers must act in your best  1.00   pass    pass   yes  
Our advisors say the market will rise next quarter.                     0.00   fail    fail   yes  
Agreement with human labels: {'n': 10, 'agreement': 1.0, 'mae': 0.0}
Target: >= 0.9 agreement before the metric gates anything.
```

## Verify Before Recording

- [ ] Offline agreement is perfect by construction (rule-based mock); Lab 4.1 asks students to calibrate live
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- FAIL rows in red; the target line in amber
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
