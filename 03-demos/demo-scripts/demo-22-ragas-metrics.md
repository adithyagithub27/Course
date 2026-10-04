# Demo 22 — RAGAS 0.4 Metrics Live

**Used in:** Lecture 5.2 (RAGAS Metrics)
**Lecture type:** Demo
**Duration:** ~2 minutes of screen recording
**Purpose:** Score five policy questions with the four RAGAS 0.4 metrics on the current API (`SingleTurnSample`, `EvaluationDataset`, metric classes).
**Demo file(s):** `demos/m05_ragas_metrics.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m05_ragas_metrics.py`
**Verified:** openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: The API (50 s)

`evaluators/ragas_suite.py`: `make_metrics()` with classes from `ragas.metrics.collections`, `ascore_sample()` with `await metric.ascore(...)` (bible §8.9); `to_sample()` with `reference` (not `ground_truth`).

### Scene 2: The scores (50 s)

Run the demo: four perfect rows, RAG-TE-05 faithfulness 0.0 / relevancy 0.0 with precision and recall 1.0: a generation failure.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m05_ragas_metrics.py
EvaluationDataset with 5 SingleTurnSamples (user_input, response, retrieved_contexts, reference)
id         faithfulness  answer_relevancy  context_precision  context_recall
---------  ------------  ----------------  -----------------  --------------
RAG-HR-01  1.0           1.0               1.0                1.0           
RAG-HR-04  1.0           1.0               1.0                1.0           
RAG-IT-03  1.0           1.0               1.0                1.0           
RAG-TE-02  1.0           1.0               1.0                1.0           
RAG-TE-05  0.0           0.0               1.0                1.0           
Aggregate: {'faithfulness': 0.8, 'answer_relevancy': 0.8, 'context_precision': 1.0, 'context_recall': 1.0}
```

## Verify Before Recording

- [ ] No 0.1-era code on screen (`from ragas.metrics import faithfulness`, `evaluate(Dataset.from_dict(...))`)
- [ ] Live RAGAS uses `llm_factory("gpt-4.1", client=AsyncOpenAI())` and `text-embedding-3-small`: verify cost before a live take
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Version banner corner note: ragas 0.4.3
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
