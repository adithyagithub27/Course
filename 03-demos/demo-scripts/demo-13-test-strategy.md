# Demo 13 — The Five-Layer Pyramid in the Repo

**Used in:** Lecture 2.3 (Designing a Test Strategy for AI Agents)
**Lecture type:** Teach + template
**Duration:** ~90 seconds of screen recording
**Purpose:** Show that the five-layer agent eval pyramid (T4) is how the course repo is organised, then fill one row of the test-strategy template.
**Demo file(s):** `demos/m02_test_strategy.py` (student repo `04-code-examples/agent-eval-framework/`)
**Command(s):** `uv run python demos/m02_test_strategy.py`; `uv run pytest -q tests/unit  # repeat per layer to show the counts 44 / 63 / 54 / 32 / 11`
**Verified:** openai 2.54.0 | deepeval 4.2.7, offline mode (2026-10-02). The demo prints this version banner first; it doubles as the lecture's on-screen banner.

## Setup

```bash
cd 04-code-examples/agent-eval-framework
make install          # once
export OFFLINE=1      # deterministic: reproduces the output below exactly
```

Terminal: dark theme, JetBrains Mono 18–20 pt, about 110 columns. Clear the screen before each take.

## Recording Script

### Scene 1: Layers as folders (45 s)

Run the demo: five layers, their folders, file names and when each runs.

### Scene 2: The template (45 s)

VS Code, `11-course-assets/templates/test-strategy-template.md`: the coverage matrix (components × dimensions) and the strategy table with the five layers as rows. Fill the trajectory row for TechCorp: tool selection and order on GS-05 and GS-06, ToolCorrectness 0.85, every PR, agent team.

## Real Output (offline)

Captured from a real run (`OFFLINE=1`, mock LLM and mock judge); the version banner is omitted. Live runs (`OFFLINE=0` with an API key) word things differently: re-capture before recording live.

```
$ uv run python demos/m02_test_strategy.py
1 unit evals             tests/unit          6 files  every commit, ~free
                         deterministic checks on tools, parsers, guards
                           - test_config.py
                           - test_heuristics.py
                           - test_mock_llm.py
                           - test_ops_and_banking_tools.py
                           - test_pii_reliability_tools.py
                           - test_support_tools.py
2 component evals        tests/component     5 files  every commit, cents
                         one piece at a time: retriever, generator, judge, MCP contract
                           - test_custom_metrics_and_judge.py
                           - test_judge_metrics.py
                           - test_mcp_contract.py
                           - test_rag_components.py
                           - test_synthetic_data.py
3 trajectory evals       tests/trajectory    3 files  every PR
                         the agent's steps: tool choice, arguments, order, loops
                           - test_multi_agent.py
                           - test_ops_agent.py
                           - test_support_trajectories.py
4 end-to-end evals       tests/e2e           4 files  every PR / nightly
                         golden datasets scored by LLM-judge metrics; red team
                           - test_golden_support.py
                           - test_promptfoo_provider.py
                           - test_regression_and_gate.py
                           - test_security.py
5 production monitoring  tests/production    2 files  continuous
                         drift, scorecards, audit trail on live traffic
                           - test_monitoring.py
                           - test_observability.py
```

## Verify Before Recording

- [ ] Per-layer test counts (44/63/54/32/11 = 204) change when tests are added: re-count with `pytest --collect-only -q tests/<layer>` before recording
- [ ] The template file shows the five layer rows (rewritten 2026-10-02)
- [ ] `make test` is green and the run above reproduces on the recording machine
- [ ] Every price on screen carries "verify current pricing"; no API key visible

## Post-Production Notes

- Pair with D4 builds 2–6 and D6
- Failures in Alert Red, passes in Electric Teal, thresholds and latency in Warm Amber (`10-graphics/design-system.md`)
