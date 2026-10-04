# Course 2 Demo Recording Specs

> One spec per demo or build-along lecture, each tied to a real file in `04-code-examples/agent-eval-framework/demos/` and to its real offline output (`14-quality-review/course2-bible.md` §7). Specs 01–06 are hand-written; 07–50 follow the same format: header, setup, scenes with timings, real output, verify-before-recording checklist, post-production notes.
>
> Run any demo with `uv run python demos/<file>` from the student repo root (`make demos` runs all 61 offline). Offline numbers are teaching numbers from the deterministic mock LLM and judge; re-capture live (`OFFLINE=0`) before presenting a score as a fact about a GPT model. Every price on screen carries "verify current pricing".

| Spec | Lecture(s) | Demo | Demo file(s) |
|---|---|---|---|
| [`demo-01-agent-failure.md`](demo-scripts/demo-01-agent-failure.md) | 0.1 | The One-Line Prompt Edit | `m00_agent_failure.py` |
| [`demo-07-setup-check.md`](demo-scripts/demo-07-setup-check.md) | 0.2 | Environment Smoke Test | `m00_verify_setup.py`, `m00_hello_eval.py` |
| [`demo-08-tokens-and-temperature.md`](demo-scripts/demo-08-tokens-and-temperature.md) | 1.1 | Tokens, Cost per Call and Temperature | `m01_token_demo.py`, `m01_temperature_demo.py` |
| [`demo-09-agent-vs-chatbot.md`](demo-scripts/demo-09-agent-vs-chatbot.md) | 1.2 | Agent vs Chatbot Side by Side | `m01_agent_vs_chatbot.py` |
| [`demo-10-failure-gallery.md`](demo-scripts/demo-10-failure-gallery.md) | 1.4 | The Six Failure Modes, One Run Each | `m01_failure_gallery.py` |
| [`demo-11-assertion-flakiness.md`](demo-scripts/demo-11-assertion-flakiness.md) | 2.1 | Why Exact-Match Assertions Flake | `m02_assertion_flakiness.py` |
| [`demo-12-five-dimensions.md`](demo-scripts/demo-12-five-dimensions.md) | 2.2 | One Answer, Five Dimensions | `m02_five_dimensions.py` |
| [`demo-13-test-strategy.md`](demo-scripts/demo-13-test-strategy.md) | 2.3 | The Five-Layer Pyramid in the Repo | `m02_test_strategy.py` |
| [`demo-02-deepeval-first-run.md`](demo-scripts/demo-02-deepeval-first-run.md) | 3.1; Lab 3.1 | First DeepEval Run | `m03_first_eval.py` |
| [`demo-14-golden-dataset.md`](demo-scripts/demo-14-golden-dataset.md) | 3.2 | Building the Golden Dataset | `m03_golden_dataset.py` |
| [`demo-15-eval-support-agent.md`](demo-scripts/demo-15-eval-support-agent.md) | 3.3 | Running the First End-to-End Evaluation | `m03_eval_support_agent.py` |
| [`demo-16-project1-report.md`](demo-scripts/demo-16-project1-report.md) | 3.4 | Project 1 Report | `m03_project1_eval.py` |
| [`demo-17-metric-comparison.md`](demo-scripts/demo-17-metric-comparison.md) | 4.1 | Same Answers, Different Metrics | `m04_metric_comparison.py` |
| [`demo-18-agent-metrics.md`](demo-scripts/demo-18-agent-metrics.md) | 4.2 | Task Completion and Tool Correctness | `m04_agent_metrics.py` |
| [`demo-19-llm-as-judge.md`](demo-scripts/demo-19-llm-as-judge.md) | 4.3 | A Judge Prompt from Scratch | `m04_llm_as_judge.py` |
| [`demo-20-custom-geval.md`](demo-scripts/demo-20-custom-geval.md) | 4.4 | Building Custom G-Eval Metrics | `m04_geval_empathy.py`, `m04_lab_regulatory_geval.py` |
| [`demo-21-rag-failure-dissection.md`](demo-scripts/demo-21-rag-failure-dissection.md) | 5.1 | RAG Failure Dissection | `m05_rag_failure_dissection.py` |
| [`demo-22-ragas-metrics.md`](demo-scripts/demo-22-ragas-metrics.md) | 5.2 | RAGAS 0.4 Metrics Live | `m05_ragas_metrics.py` |
| [`demo-23-component-isolation.md`](demo-scripts/demo-23-component-isolation.md) | 5.3 | Retriever vs Generator in Isolation | `m05_component_isolation.py` |
| [`demo-24-project2-rag-report.md`](demo-scripts/demo-24-project2-rag-report.md) | 5.4 | Project 2 RAG Diagnostic Report | `m05_project2_rag_eval.py` |
| [`demo-25-tool-failure-gallery.md`](demo-scripts/demo-25-tool-failure-gallery.md) | 6.1 | Four Tool-Call Failures | `m06_tool_failure_gallery.py` |
| [`demo-26-tool-test-suite.md`](demo-scripts/demo-26-tool-test-suite.md) | 6.2 | A Five-Case Tool Test Suite | `m06_tool_test_suite.py` |
| [`demo-27-mcp-server-validation.md`](demo-scripts/demo-27-mcp-server-validation.md) | 6.3 | MCP Server Contract Tests | `m06_mcp_server_validation.py` |
| [`demo-28-project3-ops-agent.md`](demo-scripts/demo-28-project3-ops-agent.md) | 6.4 | Project 3: The Operations Agent | `m06_project3_tool_agent.py` |
| [`demo-29-multi-agent-failures.md`](demo-scripts/demo-29-multi-agent-failures.md) | 7.1 | Multi-Agent Failure Montage | `m07_multi_agent_failures.py` |
| [`demo-30-communication-tests.md`](demo-scripts/demo-30-communication-tests.md) | 7.2 | Testing Agent Hand-offs | `m07_communication_tests.py` |
| [`demo-31-loop-detector.md`](demo-scripts/demo-31-loop-detector.md) | 7.3 | Loop Detection and Failure Injection | `m07_loop_detector.py`, `m07_lab_failure_injection.py` |
| [`demo-32-prompt-injection-live.md`](demo-scripts/demo-32-prompt-injection-live.md) | 8.1 | Five Prompt Injections, Live | `m08_prompt_injection_live.py` |
| [`demo-03-promptfoo-red-team.md`](demo-scripts/demo-03-promptfoo-red-team.md) | 8.2; Lab 8.1 | promptfoo Red Team on the Real Agent | `m08_promptfoo_redteam.py`, `m08_prompt_injection_live.py` |
| [`demo-33-pii-scanner.md`](demo-scripts/demo-33-pii-scanner.md) | 8.3 | PII Leakage Scanner | `m08_pii_scanner.py` |
| [`demo-34-project4-banking.md`](demo-scripts/demo-34-project4-banking.md) | 8.4 | Project 4: SecureBank v1 vs v2 | `m08_project4_banking_redteam.py` |
| [`demo-35-garak-pyrit.md`](demo-scripts/demo-35-garak-pyrit.md) | 8.5 | Beyond promptfoo: Garak and PyRIT | `m08_garak_scan.py`, `m08_pyrit_attack.py` |
| [`demo-36-blind-vs-traced.md`](demo-scripts/demo-36-blind-vs-traced.md) | 9.1 | Blind vs Traced Debugging | `m09_blind_vs_traced.py` |
| [`demo-04-langfuse-trace.md`](demo-scripts/demo-04-langfuse-trace.md) | 9.2; Lab 9.1 | Langfuse v4 Agent Trace | `m09_langfuse_tracing.py` |
| [`demo-37-cost-and-otel.md`](demo-scripts/demo-37-cost-and-otel.md) | 9.3 | Cost per Trace and OpenTelemetry GenAI Spans | `m09_cost_analysis.py`, `m09_otel_genai.py` |
| [`demo-38-benchmark.md`](demo-scripts/demo-38-benchmark.md) | 10.1 | Benchmarking Latency and Cost | `m10_benchmark.py` |
| [`demo-39-reliability.md`](demo-scripts/demo-39-reliability.md) | 10.2 | Failure Rate, Retry, Timeout and Loops | `m10_reliability.py` |
| [`demo-40-cost-engineering.md`](demo-scripts/demo-40-cost-engineering.md) | 10.3 | Prompt Diet and Model Routing | `m10_cost_hotspots.py`, `m10_model_routing.py` |
| [`demo-41-regression-simulation.md`](demo-scripts/demo-41-regression-simulation.md) | 11.1 | One Deleted Line, Caught | `m11_regression_simulation.py` |
| [`demo-42-baseline-comparison.md`](demo-scripts/demo-42-baseline-comparison.md) | 11.2 | Baselines and the Regression Gate | `m11_baseline_comparison.py` |
| [`demo-43-synthetic-data.md`](demo-scripts/demo-43-synthetic-data.md) | 11.3 | DeepEval Synthesizer at Scale | `m11_synthetic_data.py`, `m11_lab_generate_regress_catch.py` |
| [`demo-05-cicd-pipeline.md`](demo-scripts/demo-05-cicd-pipeline.md) | 12.1, 12.2; Lab 12.1 | The CI Quality Gate on a Pull Request | `m12_quality_gate.py` |
| [`demo-06-quality-dashboard.md`](demo-scripts/demo-06-quality-dashboard.md) | 12.3 | Experiment Comparison and the Quality Dashboard | `m12_experiment_comparison.py`, `m12_quality_dashboard.py` |
| [`demo-44-drift-detection.md`](demo-scripts/demo-44-drift-detection.md) | 13.1 | Drift Detection | `m13_drift_detection.py` |
| [`demo-45-governance-audit.md`](demo-scripts/demo-45-governance-audit.md) | 13.2 | Hash-Chained Audit Trail and Release Gate | `m13_governance_audit.py` |
| [`demo-46-quality-scorecard.md`](demo-scripts/demo-46-quality-scorecard.md) | 13.3 | The Leadership Scorecard | `m13_quality_scorecard.py` |
| [`demo-47-capstone-architecture.md`](demo-scripts/demo-47-capstone-architecture.md) | 14.1 | Capstone Architecture Walkthrough | `m14_architecture.py` |
| [`demo-48-capstone-pipeline.md`](demo-scripts/demo-48-capstone-pipeline.md) | 14.2–14.4 | The Full Capstone Pipeline | `m14_full_pipeline.py` |
| [`demo-49-dashboard-reveal.md`](demo-scripts/demo-49-dashboard-reveal.md) | 14.5 | Ship It: the Dashboard Reveal | `m14_dashboard_reveal.py` |
| [`demo-50-portfolio-summary.md`](demo-scripts/demo-50-portfolio-summary.md) | 15.1 | Your Portfolio in Five Lines | `m15_portfolio_summary.py` |

## Coverage

Every lecture of type Demo, Build-along or "+ demo" in `01-curriculum/full-curriculum.md` has a spec, and so do the slide/teach lectures that get a screen beat under fix-plan decision A5. Lectures without a spec of their own: 12.1 (uses demo 05's local gate run), 14.2–14.4 (share demo 48), 15.2 (outro, no demo).

Lab reference demos are covered inside the matching spec: `m01_lab_run_agent.py` (Lab 1.1, see `07-labs/lab-01-first-agent-run.md`), `m07_lab_failure_injection.py` (demo 31), `m09_lab_trace_find_fix.py` (Lab 9.1, see `07-labs/lab-08-langfuse-tracing.md`), `m11_lab_generate_regress_catch.py` (demo 43), `m04_lab_regulatory_geval.py` (demo 20).
