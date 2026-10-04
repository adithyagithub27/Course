# DeepEval Cheatsheet

## Quick Reference for AI Agent Testing & Evaluation (DeepEval 4.2.7)

### Install (course repo)
```bash
cd 04-code-examples/agent-eval-framework
make install                 # uv sync --locked (deepeval 4.2.7, openai 2.54.0, ragas 0.4.3, ...)
make test                    # 204 offline tests, no API key
```
Without a key (or with `OFFLINE=1`) every metric runs its real DeepEval code with the course's deterministic mock judge. With `OPENAI_API_KEY` and `OFFLINE=0`, the judge is `gpt-4.1` and the agent `gpt-4.1-mini` (verify current pricing).

### Basic Test Structure
```python
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from agents.support_agent import run_support_agent
from evaluators.judge import get_judge          # gpt-4.1 live, MockJudge offline

def test_pricing_answer_is_relevant():
    question = "What are your pricing plans?"
    result = run_support_agent(question)
    test_case = LLMTestCase(input=question, actual_output=result["response"])
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7, model=get_judge())])
```

`LLMTestCase` fields: `input`, `actual_output`, `expected_output`, `context`, `retrieval_context`, `tools_called`, `expected_tools` (lists of `ToolCall(name=..., input_parameters=..., output=...)`). For an agent, `retrieval_context` is what its tools returned; `evaluators/deepeval_suite.to_test_case(result, case)` builds all of it.

### Run Tests
```bash
uv run deepeval test run demos/m03_first_eval.py     # DeepEval runner, local results table
uv run pytest -q tests/e2e/test_golden_support.py    # plain pytest
uv run pytest -q -m security                         # by marker
uv run pytest -q -k "GS-05"                          # by name
```

### Built-in Metrics (DeepEval 4.2)

| Metric | What it measures | Course threshold |
|--------|-----------------|------------------|
| `AnswerRelevancyMetric` | Does the response address the question? | 0.7 |
| `FaithfulnessMetric` | Is every claim supported by `retrieval_context`? Only **contradicting** claims fail unless `penalize_ambiguous_claims=True` | 0.8 |
| `HallucinationMetric` | Share of `context` items the answer agrees with: **higher is better**, passes when score ≥ threshold | 0.7 |
| `ContextualPrecisionMetric` | Are relevant chunks ranked first? | 0.7 |
| `ContextualRecallMetric` | Does retrieval cover the expected answer? | 0.7 |
| `TaskCompletionMetric` | Did the agent achieve the goal? | 0.8 |
| `ToolCorrectnessMetric` | `tools_called` vs `expected_tools` by name (still needs `model=` in 4.2) | 0.85 |
| `BiasMetric`, `ToxicityMetric`, `PIILeakageMetric` | Safety checks (`PIILeakageMetric`: 1.0 = no leak) | — |

There is no `CoherenceMetric`: write coherence as a GEval criterion. Thresholds live in `config/eval_config.yaml`.

### Custom G-Eval Metric
```python
from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams      # LLMTestCaseParams still works but is deprecated

empathy = GEval(
    name="Customer Empathy",
    criteria="Does the response show empathy for the customer's situation while still solving the problem?",
    evaluation_steps=[
        "Check whether the response acknowledges the customer's feelings in the first sentence.",
        "Check whether the response offers a concrete next step, not just sympathy.",
        "Penalize blame, sarcasm, or rude language heavily.",
    ],
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    threshold=0.7, model=get_judge(), async_mode=False,
)
```
Calibrate against human labels (agreement ≥ 0.9) before a custom metric gates anything (Lab 4.1).

### Golden Datasets
```python
from deepeval.dataset import EvaluationDataset, Golden
from evaluators.golden import load                    # load("golden_support") -> list of dicts

goldens = [Golden(input=c["input"], expected_output=c["expected_output"], context=c["context"])
           for c in load("golden_support")]
dataset = EvaluationDataset(goldens=goldens)          # or evaluators.deepeval_suite.golden_dataset()
```

### Synthetic Data
```python
from deepeval.synthesizer import Synthesizer
synth = Synthesizer(model=get_judge())
synth.generate_goldens_from_goldens(goldens, max_goldens_per_golden=4)
synth.generate_goldens_from_contexts(contexts=[["KB text ..."]], max_goldens_per_context=2)
```
Course wrapper: `regression/synthetic_data.py` (`make synthetic` = 100 goldens from 5 seeds).

### Key Tips
- Pass the judge with `model=get_judge()`; never hard-code a model name in a test
- Use `async_mode=False` in scripts and loops; combine metrics in one `assert_test()`
- Watch a test fail on purpose before you trust it
- Offline scores are teaching numbers; re-run live before quoting a score
- Confident AI (`deepeval login`) is optional; the course never needs it
