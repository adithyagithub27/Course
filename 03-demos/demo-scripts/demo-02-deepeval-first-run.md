# Demo 02 — First DeepEval Run

**Used in:** Lecture 3.1 (Meet DeepEval: pytest for AI); also Lab 3.1
**Duration:** ~3 minutes of screen recording
**Purpose:** Show how little code a real DeepEval test of the real agent needs, watch it pass, make it fail, and read the reason.
**Demo file:** `demos/m03_first_eval.py`
**Commands:** `uv run python demos/m03_first_eval.py` and `uv run deepeval test run demos/m03_first_eval.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02)

## Setup

```bash
cd 04-code-examples/agent-eval-framework
export OFFLINE=1
```

Split screen: VS Code left (`demos/m03_first_eval.py`), terminal right.

## Recording Script

### Scene 1: The test (60 s)

Show the test function (exact code from the file):

```python
def test_pricing_answer_is_relevant():
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    test_case = LLMTestCase(input=question, actual_output=result["response"])
    metric = AnswerRelevancyMetric(threshold=0.7, model=get_judge())
    assert_test(test_case, [metric])
```

Highlight in order: `run_support_agent` (the real TechCorp agent), `LLMTestCase`, `AnswerRelevancyMetric(threshold=0.7, ...)`, `model=get_judge()` (gpt-4.1 live, the deterministic mock judge offline), `assert_test`.

Narration point: "One agent call, one test case, one metric, one assert."

### Scene 2: Run it (30 s)

```bash
uv run python demos/m03_first_eval.py
```

Real offline output:

```
Input : What are your pricing plans?
Output: There are three TechCorp plans: Basic ($9.99/mo), Pro ($29.99/mo) and Enterprise (custom pricing). Core features come with all of them, and Pro adds priority support plus advanced analytics.
AnswerRelevancy = 1.00 (threshold 0.7) -> PASS
Reason: Scored offline by the deterministic mock judge (word overlap and number matching).
```

Then the pytest-style runner:

```bash
uv run deepeval test run demos/m03_first_eval.py
```

Show DeepEval's local results table and the summary line "Pass Rate: 100.0% | Passed: 1 | Failed: 0".

### Scene 3: Make it fail (60 s)

In a scratch copy (`my_work/test_first_fail.py`), keep the metric and replace the agent's answer with an off-topic one:

```python
test_case = LLMTestCase(input=question, actual_output="Our office is closed on public holidays.")
```

Run `uv run deepeval test run my_work/test_first_fail.py`. Show FAILED in red and the metric's reason in the results table.

Narration point: "It didn't just say fail. It told you why. Live, gpt-4.1 writes that reason."

### Scene 4: Two metrics (30 s)

Show the Lab 3.1 version with Faithfulness against the knowledge-base result:

```python
assert_test(test_case, [FaithfulnessMetric(threshold=0.8, model=get_judge()), correctness()])
```

## Verify Before Recording

- [ ] Re-run Scene 3 and capture the exact reason text you show (offline it is the mock judge's reason; live it is gpt-4.1's)
- [ ] `deepeval test run` works from the repo root (`pyproject.toml` sets `pythonpath = [".", "demos"]`)
- [ ] Don't show "50+ metrics" or other counts without checking DeepEval's current docs (verify)

## Post-Production Notes

- Slow the typing on `metric = ...` and `assert_test`
- PASS in teal, FAILED in red; zoom on the reason column
- Lower third on Scene 2: "Offline mode: deterministic mock judge. Add an API key for live gpt-4.1 scores."
