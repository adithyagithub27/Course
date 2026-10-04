# Evaluation Metrics Cheatsheet

## Quick Reference — Which Metric When? (course stack: DeepEval 4.2.7, RAGAS 0.4.3, promptfoo 0.123.1)

### Start from the failure mode (T2)

| Failure mode | Catch it with |
|---|---|
| Hallucination | `FaithfulnessMetric` vs tool results / retrieved context; `HallucinationMetric`; GEval correctness |
| Wrong tool selection | `ToolCorrectnessMetric`; expected-tool and forbidden-tool checks (`evaluators/tool_metrics.py`) |
| Incorrect tool arguments | `check_arguments()`; JSON-schema validation against the MCP server (`mcp_server/contract.py`) |
| Reasoning errors | GEval correctness vs `expected_output`; `TaskCompletionMetric` |
| Goal drift | `AnswerRelevancyMetric`; injection-resistance GEval; red teaming |
| Infinite loops | `LoopDetector` (3 identical actions, 10-step budget); iteration cap; max LLM calls |

### Then make sure each dimension (T3) is covered

| Dimension | Metrics (`config/eval_config.yaml`) |
|---|---|
| Correctness | Answer Correctness GEval 0.7 · TaskCompletion 0.8 · ToolCorrectness 0.85 |
| Faithfulness | Faithfulness 0.8 (DeepEval or RAGAS) · Hallucination 0.7 (higher is better) · context recall 0.7 |
| Relevance | Answer Relevancy 0.7 · context precision 0.7 |
| Safety | Prompt Injection Resistance GEval 0.9 · PII Safety GEval 0.9 · red-team pass rate 100% |
| Reliability | consistency 0.7 · failure rate ≤ 0.1 · p95 latency ≤ 10 s · cost/task ≤ $0.01 (verify current pricing) · ≤ 6 LLM calls |

### Decision Tree

```
What are you testing?
├── LLM output quality?
│   ├── Relevant to the question?        → AnswerRelevancyMetric
│   ├── Grounded in tool results/docs?   → FaithfulnessMetric
│   ├── Agrees with the given context?   → HallucinationMetric (higher is better in 4.2)
│   └── Well-structured / on-brand?      → GEval (custom criteria; no CoherenceMetric class)
├── RAG pipeline? (RAGAS 0.4: SingleTurnSample with `reference`, metrics from ragas.metrics.collections)
│   ├── Relevant chunks ranked first?    → ContextPrecision
│   ├── Retrieval found everything?      → ContextRecall
│   ├── Answer grounded in the chunks?   → Faithfulness
│   └── Answer addresses the question?   → AnswerRelevancy
├── Agent behaviour?
│   ├── Goal achieved?                   → TaskCompletionMetric
│   ├── Right tools, right order?        → ToolCorrectnessMetric, check_sequence()
│   ├── Right arguments?                 → check_arguments(), MCP schema validation
│   └── Business rule?                   → GEval
├── Security?
│   ├── Injection / jailbreak            → promptfoo suite + redteam plugins; Garak scan; PyRIT attacks
│   ├── PII leakage                      → security/pii_scanner.py + PII Safety GEval
│   └── Unauthorized actions             → forbidden-tool assertions (no_account_tools, no_transfer)
└── Performance & reliability?
    ├── Latency, cost, LLM calls         → performance/benchmark.py (run_benchmark)
    └── Consistency, retries, loops      → performance/reliability.py (measure_reliability)
```

### Where each check runs (five-layer pyramid, T4)

| Layer | Typical checks | When |
|---|---|---|
| 1 Unit evals | tool functions, parsers, PII regex, guards | every commit |
| 2 Component evals | retriever, generator, judge, MCP contract | every commit |
| 3 Trajectory evals | tool choice, arguments, order, loops | every PR |
| 4 End-to-end evals | golden dataset with judge metrics; red team | every PR / nightly |
| 5 Production monitoring | drift, scorecards, audit trail, traces | continuous |

### CI gate defaults (`eval_config.yaml` → `gates`)
Pass rate ≥ 80% · Faithfulness, Answer Correctness, Answer Relevancy averages ≥ 0.7 · no metric more than 5 points below baseline · smoke cases 100%.

### Remember
- **Lower is better only for limits:** failure rate, p95 latency, cost per task, LLM calls. HallucinationMetric is **higher is better** in DeepEval 4.2.
- **Context is required** for Faithfulness, Hallucination and context precision/recall.
- **Expected output** is required for GEval correctness and context recall (`reference` in RAGAS).
- **Deterministic first:** tool and argument checks are free and exact; use a judge only where rules can't decide.
