# Demo 19 — A Judge Prompt from Scratch

**Used in:** Lecture 4.3 (LLM-as-Judge)
**Lecture type:** Build-along
**Duration:** ~2 minutes of screen recording
**Purpose:** Build a 1–5 judge prompt with JSON output, grade four refund answers and check agreement with human labels.
**Demo file(s):** `demos/m04_llm_as_judge.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m04_llm_as_judge.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The prompt (45 s)

`evaluators/llm_as_judge.py`, `JUDGE_PROMPT` and `judge()` (bible §8.8): rubric, JSON output, `temperature=0`, `response_format={"type": "json_object"}`, judge model gpt-4.1.

### Scene 2: The grades (45 s)

Run the demo: judge vs human for four answers, then calibration `{'n': 4, 'agreement': 1.0, 'mae': 0.0}`.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m04_llm_as_judge.py
You are an impartial judge grading a customer-support answer.
Score the answer from 1 to 5:
5 = fully correct, complete, and supported by the context
4 = correct with a minor omission
3 = partly correct or partly unsupported
2 = mostly wrong or unsupported
1 = wrong, harmful, or ignores the question
Return JSON: {"score": <1-5>, "reasoning": "<one sentence>"}
answer                                                        judge  human  reasoning                                                   
------------------------------------------------------------  -----  -----  ------------------------------------------------------------
TechCorp has a 30-day money-back guarantee, and refunds take  5      5      100% of statements supported by the context; covers 100% of 
You can get a refund within 30 days.                          4      4      100% of statements supported by the context; covers 50% of t
Refunds are possible for 14 days and take 10 business days.   1      1      0% of statements supported by the context; covers 50% of the
I can't help with refunds.                                    1      1      Refuses a question the context answers.                     
Calibration vs human labels: {'n': 4, 'agreement': 1.0, 'mae': 0.0}
```

## Verify Before Recording

- [ ] Offline the judge is the mock (word overlap + number matching): agreement 1.0 is by construction. Re-run live to show real gpt-4.1 agreement before claiming it
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D8 builds 1–4
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
