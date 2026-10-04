# Slide Deck Outline — Course 2: AI Agent Testing & Evaluation

> Slide-by-slide map for every lecture (decision T9; same role as `voice-ai-agents-course/09-production/slide-deck-outline.md` and `agent-observability-course/09-production/slide-deck-outline.md`). Generated on 2026-10-04 from the `[SLIDE]`, `[SCREEN]`, `[CODE]` and `[DEMO]` cues in `02-course-content/section-*.md`; when a script changes, the script wins and this outline is regenerated.
>
> Scene kits from `design-system.md` (this folder): **K1** Hook · **K2** Title card · **K3** Teaching slide · **K4** Architecture/diagram · **K5** Code/demo screen · **K6** Recap card · **K7** Bridge/next-up. Design rules: ≤ 12 words per slide, 5–8-word titles, one concept per slide, ≤ 15 visible code lines, Deep Navy background, Teal accent, Red only for failures and security findings, Amber only for thresholds, warnings and latency.
>
> **Standard open/close (every lecture, not repeated below):** K1 hook (first `[AVATAR]` block, often over a failure visual) → K2 title card with the outcomes slide → … → K6 recap card (`[SLIDE n: Recap]`, exactly 3 bullets, A1) → K7 next-up card from the `### Transition`. The **last lecture of each module** adds a 10-second "You can now" card (A2) before K7.
>
> **Code slides** use only APIs from the student repo and carry the footer "Verified: openai 2.54.0 | deepeval 4.2.7 | … (uv.lock, checked 2026-10-01). Agent gpt-4.1-mini, judge gpt-4.1." Every dollar figure carries "verify current pricing"; offline numbers carry "offline (mock LLM and judge)"; simulated latency and drift data say "simulated".
>
> **Decks** are built from the scripts: `python voice-ai-agents-course/09-production/tools/slide_builder.py --course . --scripts-dir 02-course-content` → `10-graphics/slides/section-XX.pptx`. A cue naming a diagram (for example "Diagram: D4 build 3") embeds that build's PNG.

---

## Master Diagram List

Files in `diagrams/` (`D{n}-{slug}.svg`, builds `D{n}-step{k}.svg`), registry `diagrams/index.json`.

| ID | Diagram | File | Used in | Kit | Builds |
|---|---|---|---|---|---|
| D1 | The six ways agents fail | `D1-six-failure-modes.svg` | 1.4, 0.1, 2.3 | K4 | 1 hallucination; 2 wrong tool selection; 3 incorrect tool arguments; 4 reasoning errors; 5 goal drift; 6 infinite loops |
| D2 | Same input, different outputs | `D2-deterministic-vs-non-deterministic.svg` | 2.1 | K4 | 1 deterministic; 2 non-deterministic |
| D3 | Chatbot vs agent: the loop | `D3-agent-loop.svg` | 1.2, 1.3 | K4 | 1 chatbot; 2 agent loop |
| D4 | Test pyramid vs agent eval pyramid | `D4-agent-eval-pyramid.svg` | 2.3, 2.1, 12.1, 14.2 | K4 | 1 unit; 2 unit evals; 3 component evals; 4 trajectory evals; 5 end-to-end evals; 6 cost and speed |
| D5 | Five dimensions of agent quality | `D5-five-dimensions-radar.svg` | 2.2, 13.3 | K4 | 1 the axes; 2 agent a; 3 agent b |
| D6 | Test strategy matrix | `D6-test-strategy-matrix.svg` | 2.3, 14.1 | K4 | 1 llm; 2 tools; 3 memory; 4 planning |
| D7 | Agent quality metrics | `D7-metric-taxonomy.svg` | 4.1, 4.2 | K4 | 1 root; 2 llm quality; 3 agent behaviour |
| D8 | LLM-as-judge | `D8-llm-as-judge.svg` | 4.3, 4.4 | K4 | 1 inputs; 2 judge; 3 structured scores; 4 calibration |
| D9 | RAG: retrieval or generation? | `D9-rag-retrieval-vs-generation.svg` | 5.1, 5.2, 5.3 | K4 | 1 the pipeline; 2 which half failed? |
| D10 | Tool calling risk | `D10-tool-call-risk-pyramid.svg` | 6.1, 6.2 | K4 | 1 wrong tool selection; 2 wrong arguments; 3 unauthorized actions |
| D11 | How one agent's failure spreads | `D11-multi-agent-failure-cascade.svg` | 7.1, 7.3 | K4 | 1 agent c fails; 2 agent b; 3 agent a; 4 user; 5 where to test |
| D12 | The AI agent threat model | `D12-agent-threat-model.svg` | 8.1, 8.2, 8.3 | K4 | 1 the agent; 2 direct injection; 3 indirect injection; 4 jailbreak; 5 pii leakage; 6 data exfiltration; 7 unauthorized actions |
| D13 | Anatomy of an agent trace | `D13-trace-anatomy.svg` | 9.1, 9.2, 9.3 | K4 | 1 trace; 2 spans; 3 root cause |
| D14 | The CI quality gate | `D14-ci-quality-gate.svg` | 12.1, 12.2, 11.2, 14.4 | K4 | 1 the pipeline; 2 pass or block |
| D15 | Production monitoring loop | `D15-production-monitoring-loop.svg` | 13.1, 13.3 | K4 | 1 production agent; 2 sample requests; 3 online evaluator; 4 score store; 5 dashboard + alerts; 6 close the loop |
| D16 | The agent quality platform | `D16-capstone-architecture.svg` | 14.1, 14.2, 14.3, 14.4, 14.5 | K4 | 1 agent under test; 2 evaluation pipeline; 3 results and dashboard; 4 CI/CD and alerting |

Notes: D1 uses the six failure modes (T2), D5 the five quality dimensions (T3), D4 the five-layer agent eval pyramid (T4). D6 is the components × dimensions coverage matrix that fills the test-strategy template's layer rows (`11-course-assets/templates/test-strategy-template.md`). Visuals the curriculum lists but that are better as K3 tables or screenshots (course roadmap, test-case anatomy, RAGAS 2×2 map, MCP architecture, multi-agent topologies, kill chain, governance hierarchy, scorecard, career paths, the three red-team tools comparison for 8.5) are drawn as K3/K5 slides, not master diagrams.

---

## Section 0: Welcome & Course Overview

Script: `02-course-content/section-00-welcome.md`.

**0.1 Your AI Agent Just Failed in Production — Now What?:** K3 "Your AI Agent Just Failed in Production" → K5 screen `agent-eval-framework` → K5 demo `Output (banner trimmed)` → K4 **D1** build 1 "Why nobody noticed" → K3 "What you'll build in this course" → K6 Recap

**0.2 Course Roadmap & Environment Setup:** K3 "Course Roadmap & Environment Setup" → K3 "Verified for this course" → K3 "Sixteen modules, five stages" → K3 "What you need" → K5 screen `agent-eval-framework` → K5 demo `Output (tail)` → K5 screen `Same terminal. Run the test suite.` → K5 demo `Output (last lines)` → K5 screen `.env` → K5 screen `Terminal. Run the setup check.` → K5 demo `Output (banner trimmed)` → K5 screen `Terminal.` → K5 demo `Output (banner trimmed)` → K5 "The repo you'll work in" (code) → K6 Recap → "You can now" card


## Section 1: AI Agents: What You Need to Know for Testing

Script: `02-course-content/section-01-agents.md`.

**1.1 LLMs in 10 Minutes: Tokens, Context, Temperature:** K3 "LLMs in 10 Minutes: Tokens, Context, Temperature" → K3 "Your testing cheat sheet" → K3 "Tokens: the units a model reads" → K5 screen `openai 2.54.0 | tiktoken 0.14.0` → K5 demo `Output (banner trimmed)` → K3 "Tokens are your test budget" → K3 "Context window: the model's desk" → K3 "Big windows still fail" → K3 "Temperature: the variation dial" → K5 screen `Terminal. Run the temperature demo. Highlight the ` → K5 demo `Output (banner trimmed)` → K3 "What this means for your tests" → K3 "One run proves very little" → K6 Recap

**1.2 What Makes an Agent an Agent (Not a Chatbot):** K3 "What Makes an Agent an Agent (Not a Chatbot)" → K3 "Verified for this lecture" → K4 **D3** build 1 "A chatbot: text in, text out" → K4 **D3** build 2 "An agent: a loop with tools" → K5 screen `Terminal. Run the side-by-side demo. Pause on the ` → K5 demo `Output (banner trimmed)` → K3 "Five things you can check in one run" → K5 code `agents/support_agent.py` → K3 "Four properties of an agent" → K3 "Trajectory: the path, not just the destination" → K6 Recap

**1.3 Agent Architecture: The Loop, Tools, Memory, Planning:** K3 "Agent Architecture: The Loop, Tools, Memory, Planning" → K3 "The blueprint" → K3 "Part 1: the LLM brain" → K5 screen `agents/support_agent.py` → K3 "Part 2: tools, the agent's hands" → K5 screen `agents/support_agent.py` → K5 screen `Terminal. Run the Lab 1.1 demo and zoom on the thi` → K5 demo `Output (third query only)` → K3 "Part 3: memory" → K3 "Part 4: planning" → K5 screen `run_support_agent` → K4 **D6** "Your testing map" → K6 Recap

**1.4 The 6 Ways AI Agents Fail (And Why Testing Is Hard):** K3 "The 6 Ways AI Agents Fail" → K3 "Verified for this lecture" → K4 **D1** build 1 "Failure 1: hallucination" → K4 **D1** builds 2 and 3 "Failures 2 and 3: the hands" → K4 **D1** build 4 "Failure 4: reasoning errors" → K4 **D1** builds 5 and 6 "Failures 5 and 6: losing the plot" → K5 screen `Terminal. Run the failure gallery. Scroll one case` → K5 demo `Output (banner trimmed)` → K3 "Why testing agents is hard" → K6 Recap → "You can now" card


## Section 2: Why Traditional Testing Breaks for AI Agents

Script: `02-course-content/section-02-why-testing-breaks.md`.

**2.1 Deterministic vs. Non-Deterministic: The Testing Paradigm Shift:** K3 "Deterministic vs. Non-Deterministic" → K4 **D2** build 1 "Same input, same output. Always?" → K4 **D2** build 2 "Language models break the assumption" → K5 screen `Terminal. Run the flakiness demo. Colour the FAIL ` → K5 demo `Output (banner trimmed)` → K3 "Five assumptions agents break" → K3 "Four kinds of checks" → K3 "Strict to flexible" → K3 "Grade it like an employee" → K5 code `demos/m02_assertion_flakiness.py` → K4 **D4** build 1 "Where these checks live" → K6 Recap

**2.2 The 5 Dimensions of Agent Quality (Beyond Pass/Fail):** K3 "The 5 Dimensions of Agent Quality" → K4 **D5** build 1 "From one question to five" → K3 "Correctness: is it right?" → K3 "Faithfulness: is it grounded?" → K3 "Relevance: did it answer the question?" → K3 "Safety: does it protect people?" → K3 "Reliability: every time, fast and cheap enough" → K5 screen `config/eval_config.yaml` → K5 screen `0.50` → K5 demo `Output (banner and blank lines trimmed)` → K4 **D5** builds 2 and 3: two illustrative agent profiles overlaid "One number hides the shape" → K6 Recap

**2.3 Designing a Test Strategy for AI Agents:** K3 "Designing a Test Strategy for AI Agents" → K4 **D4** build 1 "Test pyramid vs agent eval pyramid" → K4 **D4** build 2 "Layer 1: unit evals" → K4 **D4** build 3 "Layer 2: component evals" → K4 **D4** build 4 "Layer 3: trajectory evals" → K4 **D4** build 5 "Layer 4: end-to-end evals" → K4 **D4** build 6 "Layer 5: production monitoring" → K5 screen `Terminal. Run the strategy demo. Highlight each la` → K5 demo `Output (banner trimmed; file lists shortened)` → K3 "Which layer does a test belong to?" → K4 **D6** "What goes inside each layer" → K5 screen `11-course-assets/templates/test-strategy-template.md` → K6 Recap → "You can now" card


## Section 3: Your First Agent Evaluation

Script: `02-course-content/section-03-first-eval.md`.

**3.1 Meet DeepEval: pytest for AI:** K3 "Meet DeepEval: pytest for AI" → K3 "Verified for this lecture" → K3 "Why DeepEval" → K3 "Four building blocks" → K3 "assert_test or evaluate?" → K5 code `demos/m03_first_eval.py` → K5 code `evaluators/judge.py` → K5 screen `openai 2.54.0 | deepeval 4.2.7` → K5 demo `Output (banner trimmed)` → K3 "Score, threshold, verdict, reason" → K3 "Metrics you'll meet" → K3 "The same test, as a test suite" → K6 Recap

**3.2 Test Cases, Golden Datasets & Assertions:** K3 "The errors you get from incomplete test cases" → K3 "Verified for this lecture" → K3 "Anatomy of an LLMTestCase" → K5 code `evaluators/deepeval_suite.py` → K3 "Golden dataset: your quality contract" → K5 screen `datasets/golden_support.json` → K5 screen `Terminal. Run the dataset demo.` → K5 demo `Output (banner trimmed)` → K3 "How to pick cases" → K3 "assert_test is an AND gate" → K6 Recap

**3.3 Running Your First Agent Eval (End-to-End):** K3 "Running Your First Agent Eval" → K3 "Verified for this lecture" → K3 "The pipeline" → K5 code `evaluators/deepeval_suite.py` → K3 "The tool check is exact" → K5 code `evaluators/deepeval_suite.py` → K5 screen `Terminal. Run the end-to-end demo.` → K5 demo `Output (banner trimmed)` → K5 code `tests/e2e/test_golden_support.py` → K5 screen `Terminal, full-width (at least 140 columns). Run t` → K5 demo `Output (excerpt: first row of the results table an` → K3 "Reading a result" → K3 "Run once, score many times" → K6 Recap

**3.4 [PROJECT 1] Test a Customer Support Agent:** K3 "Project 1: Test a Customer Support Agent" → K3 "Verified for this project" → K3 "The agent under test" → K3 "Ten cases, four categories" → K3 "Three metrics" → K5 code `evaluators/metrics.py` → K5 screen `demos/m03_project1_eval.py` → K5 screen `Terminal. Run the project script.` → K5 demo `reports/results/project1_report.md` → K3 "When a case fails" → K3 "Your deliverables" → K6 Recap → "You can now" card


## Section 4: Evaluation Metrics Deep Dive

Script: `02-course-content/section-04-metrics.md`.

**4.1 LLM Quality Metrics: Relevance, Faithfulness, Coherence:** K3 "LLM Quality Metrics" → K3 "Verified for this lecture" → K4 **D7** builds 1 and 2: root "Agent quality metrics", left branch "LLM quality" with leaves relevance, faithfulness, coherence, hallucination, bias, toxicity "Agent quality metrics" → K3 "Answer Relevancy" → K3 "Faithfulness" → K3 "Hallucination vs faithfulness" → K3 "Correctness vs faithfulness" → K3 "Coherence, bias, toxicity" → K5 code `demos/m04_metric_comparison.py` → K5 screen `Terminal. Run the comparison. Highlight one cell p` → K5 demo `Output (banner and blank lines trimmed)` → K3 "The row that teaches the most" → K3 "A default set for a support agent" → K6 Recap

**4.2 Agent-Specific Metrics: Task Completion, Tool Correctness, Goal Accuracy:** K3 "Agent-Specific Metrics" → K3 "Verified for this lecture" → K4 **D7** build 3: the right branch "Agent behaviour" with leaves task completion, tool selection, tool arguments, goal accuracy, trajectory efficiency "The agent behaviour branch" → K3 "Tool correctness" → K5 code `evaluators/deepeval_suite.py` → K3 "Task completion" → K5 code `demos/m04_agent_metrics.py` → K5 screen `recorded-bad` → K5 demo `Output (banner and blank lines trimmed)` → K5 screen `ToolCorrectness reason` → K3 "Tool arguments" → K3 "Goal accuracy" → K3 "Trajectory efficiency" → K5 screen `config/eval_config.yaml` → K6 Recap

**4.3 LLM-as-Judge: How to Use One AI to Grade Another:** K3 "LLM-as-Judge" → K3 "Verified for this lecture" → K4 **D8** builds 1 to 3: inputs "How a judge works" → K5 code `evaluators/llm_as_judge.py` → K5 code `evaluators/llm_as_judge.py` → K5 screen `Terminal. Run the judge demo. Let the printed prom` → K5 demo `Output (banner and printed prompt trimmed)` → K3 "Three biases every judge has" → K3 "Mitigations" → K5 code `evaluators/llm_as_judge.py` → K3 "How to calibrate a judge" → K6 Recap

**4.4 Custom Metrics: G-Eval & Building Your Own Evaluator:** K3 "Custom Metrics with G-Eval" → K3 "Verified for this lecture" → K4 **D8** builds 1 to 3, relabelled: criteria + evaluation steps "What GEval does" → K5 code `evaluators/custom_metrics.py` → K3 "Writing evaluation steps" → K5 code `customer_empathy` → K5 screen `Terminal. Run the empathy demo. Highlight the thre` → K5 demo `Output (banner trimmed)` → K4 **D8** build 4: the amber calibration loop from "Score" back to "Rubric", labelled "calibrate against human labels" "Before a custom metric gates anything" → K5 screen `Terminal. Run the Lab 4.1 reference solution; high` → K5 demo `Output (banner trimmed; first four rows shown)` → K3 "Raw judge or GEval?" → K3 "Common mistakes" → K6 Recap → "You can now" card


## Section 5: RAG Agent Evaluation

Script: `02-course-content/section-05-rag-eval.md`.

**5.1 The RAG Quality Problem: Retrieval vs. Generation:** K3 "Meet the TechCorp Policy Assistant" → K4 **D9** build 1 "RAG: retrieval or generation?" → K3 "Four ways RAG goes wrong" → K4 **D9** build 2 "Two questions find the broken half" → K3 "One metric per failure" → K5 code `agents/rag_agent.py` → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output (banner trimmed)` → K5 screen `travel-001` → K5 code `evaluators/ragas_suite.py` → K6 Recap

**5.2 RAGAS Metrics: Context Precision, Recall, Faithfulness:** K3 "RAGAS 0.4 in three objects" → K3 "Old tutorials, old API" → K5 code `evaluators/ragas_suite.py` → K5 code `evaluators/ragas_suite.py` → K3 "How each metric scores" → K5 code `evaluators/ragas_suite.py` → K5 screen `Terminal. Run the demo; zoom on the table, then th` → K5 demo `Output (banner trimmed)` → K3 "Averages hide broken rows" → K3 "The course's RAG thresholds" → K6 Recap

**5.3 Evaluating Retrieval and Generation Separately:** K3 "Component isolation" → K3 "Two halves, two levers" → K5 code `agents/rag_agent.py` → K5 code `demos/m05_component_isolation.py` → K3 "Reading the two results" → K5 screen `Terminal. Run the demo; highlight the RAG-TE-05 ro` → K5 demo `Output (banner trimmed)` → K3 "Retriever scores you get for free" → K5 screen `tests/component/test_rag_components.py` → K5 code `tests/component/test_rag_components.py` → K5 screen `Terminal. Run the component tests.` → K5 demo `Output (trimmed)` → K6 Recap

**5.4 [PROJECT 2] Evaluate an Enterprise RAG Agent:** K3 "Project 2 brief" → K5 code `demos/m05_project2_rag_eval.py` → K5 screen `Terminal. Run the project; scroll slowly through t` → K5 demo `Output (banner trimmed)` → K5 screen `Zoom on the domain table; draw a box around each n` → K5 screen `uv run python -m agents.rag_agent "Can I use SMS codes for multi-facto` → K3 "Your report has four parts" → K3 "Stretch goals" → K6 Recap → "You can now" card


## Section 6: Testing Tool Calling & MCP

Script: `02-course-content/section-06-tool-calling.md`.

**6.1 Why Tool Calling Is the Highest-Risk Part of Any Agent:** K3 "Words versus actions" → K3 "The five TechCorp tools" → K4 **D10**, shown as builds 1 to 3: wrong tool selection, then wrong arguments, then unauthorized actions "Tool calling risk" → K3 "Anatomy of a tool call" → K3 "Four questions for every tool test" → K5 screen `datasets/tool_failures.json` → K5 screen `Terminal. Run the gallery and pause on each block.` → K5 demo `Output (banner trimmed)` → K5 screen `Ticket TKT-???` → K6 Recap

**6.2 Testing Tool Selection, Arguments & Return Handling:** K3 "What the agent hands you" → K5 code `evaluators/tool_metrics.py` → K5 code `demos/m06_tool_test_suite.py` → K5 screen `Terminal. Run the suite.` → K5 demo `Output (banner trimmed)` → K5 code `tests/trajectory/test_support_trajectories.py` → K3 "What's in the trajectory test file" → K5 screen `Terminal. Run the trajectory tests.` → K5 demo `Output (trimmed)` → K6 Recap

**6.3 MCP Server Testing: Validating Agent-Tool Contracts:** K3 "MCP in one slide" → K5 code `mcp_server/techcorp_server.py` → K5 code `mcp_server/contract.py` → K5 screen `Terminal. Run the validation demo; pause on each o` → K5 demo `Output (banner trimmed; long results cut at 110 ch` → K5 screen `Zoom on block three, "Validating the agent's real ` → K5 code `tests/component/test_mcp_contract.py` → K5 screen `Terminal. Run the contract tests.` → K5 demo `Output (trimmed)` → K6 Recap

**6.4 [PROJECT 3] Test a Multi-Tool Agent:** K3 "The TechCorp Operations Agent" → K3 "Project 3 test plan" → K5 code `agents/tool_agent.py` → K5 screen `Terminal. Run the project demo; scroll the table, ` → K5 demo `Output (banner trimmed; replies cut at 40 characte` → K5 screen `Zoom on the three lines under the table, one at a ` → K5 screen `Terminal. Run the reference tests.` → K5 demo `Output (trimmed)` → K5 code `tests/trajectory/test_ops_agent.py` → K3 "Your deliverables" → K6 Recap → "You can now" card


## Section 7: Multi-Agent System Testing

Script: `02-course-content/section-07-multi-agent.md`.

**7.1 Multi-Agent Architectures: What Can Go Wrong:** K3 "Four ways to wire agents together" → K3 "Each shape fails its own way" → K3 "The TechCorp Reply Desk" → K3 "Hand-offs grow fast" → K3 "New failures between agents" → K4 **D11**, shown as builds 1 to 5: agent C fails; agent B passes it on; agent A builds on it; the user gets a wrong answer; where to test, a check at every hand-off "How one agent's failure spreads" → K3 "What a safe system returns" → K5 screen `Terminal. Run the failure montage; pause on each o` → K5 demo `Output (banner trimmed; replies cut at 110 charact` → K5 screen `checksum mismatch on message 2` → K6 Recap

**7.2 Testing Agent Communication, Delegation & Coordination:** K3 "Test the conversation, not just the answer" → K5 code `agents/multi_agent.py` → K5 code `agents/multi_agent.py` → K3 "Five hand-off checks" → K3 "Delegation accuracy" → K5 code `demos/m07_communication_tests.py` → K5 screen `Terminal. Run the communication tests; pause on th` → K5 demo `Output (banner trimmed; content cut at 60 characte` → K5 code `tests/trajectory/test_multi_agent.py` → K3 "Coordination without shared state" → K5 screen `Terminal. Run the multi-agent tests.` → K5 demo `Output (trimmed)` → K6 Recap

**7.3 Detecting Infinite Loops, State Corruption & Failure Propagation:** K3 "Three runtime guards" → K5 code `performance/reliability.py` → K5 screen `Terminal. Run the loop detector demo.` → K5 demo `Output (banner trimmed)` → K5 code `agents/multi_agent.py` → K3 "The end of every run" → K5 code `demos/m07_lab_failure_injection.py` → K5 screen `Terminal. Run the failure-injection demo.` → K5 demo `Output (banner trimmed)` → K3 "A good fallback reply" → K6 Recap → "You can now" card


## Section 8: Security Testing & Red Teaming

Script: `02-course-content/section-08-red-teaming.md`.

**8.1 The AI Agent Threat Model: What Attackers Actually Do:** K3 "Why agents change security" → K5 screen `agents/support_agent.py` → K4 **D12**, shown as builds 1 to 7: the agent first, then one build per vector: direct injection, indirect injection, jailbreak, PII leakage, data exfiltration, unauthorized actions "The AI agent threat model" → K3 "Vectors 1 and 2: injection" → K3 "Vectors 3 and 4: jailbreaks and PII" → K3 "Vectors 5 and 6: exfiltration and actions" → K3 "The OWASP labels on our attacks" → K3 "An attack, step by step" → K5 screen `Terminal. Run the injection demo; scroll to the la` → K5 demo `Output (banner trimmed; the first four attacks are` → K3 "Defence in depth for agents" → K6 Recap

**8.2 Prompt Injection & Jailbreak Testing with promptfoo:** K3 "promptfoo in four pieces" → K5 code `security/promptfoo/provider.py` → K5 code `security/promptfoo/promptfooconfig.yaml` → K5 screen `security/promptfoo` → K5 demo `Output (first two rows and the summary; colour cod` → K5 code `security/promptfoo/redteam.yaml` → K5 screen `Terminal. Show the two live commands from the demo` → K5 screen `Terminal. Run the injection demo; zoom on the mult` → K5 demo `Output (support-agent attacks; banner and SecureBa` → K3 "Closing the multi-turn gap" → K6 Recap

**8.3 PII Leakage, Data Exfiltration & Unauthorized Actions:** K3 "Three ways data escapes" → K5 code `security/pii_scanner.py` → K5 screen `demos/m08_pii_scanner.py` → K5 screen `Terminal. Run the scanner.` → K5 demo `Output (banner trimmed)` → K5 code `evaluators/custom_metrics.py` → K5 code `security/pii_scanner.py` → K3 "Exits two and three: test the tools" → K5 code `tests/e2e/test_security.py` → K5 screen `Terminal. Run the security tests.` → K5 demo `Output (trimmed)` → K6 Recap

**8.4 [PROJECT 4] Red Team a Banking Agent:** K3 "SecureBank, the agent under test" → K3 "The 16-attack matrix" → K5 code `security/redteam.py` → K5 screen `Terminal. Run the project; pause on the v1 finding` → K5 demo `Output (banner trimmed)` → K3 "Root cause: who enforces the rules?" → K5 code `agents/banking_agent.py` → K5 screen `Terminal in the repo root. Run the same matrix thr` → K5 demo `Output (summary only)` → K3 "Your Project 4 deliverables" → K3 "Findings become regression tests" → K6 Recap

**8.5 Beyond promptfoo: Garak and PyRIT:** K3 "Three tools, three jobs" → K3 "One target for every tool" → K5 screen `Two terminals. Left: start the server. Right: send` → K5 demo `Output (right terminal)` → K5 code `security/garak/rest_generator.json` → K5 screen `Terminal. Run the Garak demo in plan mode.` → K5 demo `Output (banner and the JSON config trimmed)` → K5 screen `make garak` → K5 code `security/pyrit/attack_agent.py` → K5 demo `.venv-pyrit/bin/python security/pyrit/attack_agent.py` → K3 "Which tool, when" → K6 Recap → "You can now" card


## Section 9: Agent Observability & Tracing

Script: `02-course-content/section-09-observability.md`.

**9.1 Why You Can't Debug an Agent Without Traces:** K3 "What your logs say" → K3 "Why agents need more than logs" → K4 **D13**, shown as builds 1 to 3: the trace, one box for the whole agent run with user, session and total cost; the spans, nested children "Anatomy of an agent trace" → K5 code `observability/langfuse_tracing.py` → K5 screen `Terminal. Run the blind-versus-traced demo; pause ` → K5 demo `Output (banner trimmed; the trace ID changes on ev` → K5 screen `Zoom on the trace tree; highlight the WARNING line` → K3 "What to read in every trace" → K3 "Traces and evals work together" → K5 screen `Terminal. Run the Lab 9.1 reference demo and show ` → K5 demo `Output (banner and AFTER FIX block trimmed)` → K6 Recap

**9.2 Tracing with Langfuse: Spans, Costs & Latency:** K3 "Langfuse v4 in four calls" → K3 "Using a tutorial? Check its version" → K5 code `observability/langfuse_tracing.py` → K5 code `observability/langfuse_tracing.py` → K3 "`gpt-4.1-mini` list prices (verify current pricing)" → K5 code `observability/langfuse_tracing.py` → K5 screen `Terminal. Run the tracing demo; pause on the table` → K5 demo `Output (banner trimmed)` → K5 screen `Zoom on the trace tree.` → K5 screen `LANGFUSE_PUBLIC_KEY` → K5 screen `Terminal. Run the observability tests.` → K5 demo `Output (trimmed)` → K6 Recap

**9.3 OpenTelemetry GenAI Conventions: The Enterprise Standard:** K3 "OpenTelemetry GenAI conventions" → K3 "Three span types, official names" → K5 code `observability/otel_genai.py` → K5 screen `observability/otel_genai.py` → K5 screen `Terminal. Run the OTel demo.` → K5 demo `Output (banner trimmed; second chat span trimmed)` → K5 code `tests/production/test_observability.py` → K5 screen `Terminal. Run the cost analysis demo.` → K5 demo `Output (banner trimmed)` → K6 Recap → "You can now" card


## Section 10: Performance & Reliability Testing

Script: `02-course-content/section-10-performance.md`.

**10.1 Latency, Token Cost & Throughput Benchmarking:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Where performance fits" → K3 "Three numbers, three questions" → K3 "Latency is a distribution" → K3 "Where agent latency comes from" → K5 code `performance/benchmark.py` → K3 "Cost per call, per task, per 1,000 tasks" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline, simulated latenc` → K5 screen `Same output. Zoom on the histogram, then on the "S` → K5 screen `Same output. Zoom on "Cost by step" and "Throughpu` → K6 Recap

**10.2 Reliability: Failure Rate, Retry, Timeout & Loop Detection:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Reliability thresholds you already own" → K5 code `performance/reliability.py` → K5 code `performance/reliability.py` → K3 "When a retry hurts" → K5 code `performance/reliability.py` → K5 screen `demos/m10_reliability.py` → K5 demo `Output after the banner (offline)` → K6 Recap

**10.3 Cost Engineering: Finding the 80/20 of Agent Spend:** K3 "Version banner" → K3 "By the end of this lecture" → K5 screen `Terminal. Run the Module 9 cost analysis again.` → K5 demo `Output after the banner (offline)` → K5 screen `Terminal. Run the hotspot demo.` → K5 demo `Output after the banner (offline)` → K3 "Lever 1: the prompt diet" → K5 code `demos/m10_cost_hotspots.py` → K5 code `performance/cost.py` → K5 screen `Terminal. Run the routing demo.` → K5 demo `Output after the banner (offline)` → K5 screen `Same output. Zoom on the "Quality check" line, the` → K3 "Two more levers to measure next" → K6 Recap → "You can now" card


## Section 11: Regression Testing & Synthetic Data

Script: `02-course-content/section-11-regression.md`.

**11.1 Why Agents Regress: Model Updates, Prompt Drift, Tool Changes:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Regression: quality drops after a change" → K3 "Cause 1: model updates" → K3 "Cause 2: prompt drift" → K3 "Cause 3: tool changes. Cause 4: context changes" → K3 "The defence: same questions, every change" → K3 "Which test sees which cause first" → K3 "Two of the four never touch your repo" → K5 code `regression/regression_suite.py` → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline)` → K5 screen `Same output. Zoom on the three failing answers, wi` → K5 screen `Same output. Zoom on the "Answer Relevancy 1.00 +0` → K3 "What the report gives you" → K6 Recap

**11.2 Building Regression Test Suites with Golden Datasets:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Regression suite in three steps" → K3 "What belongs in a regression dataset" → K5 code `regression/regression_suite.py` → K5 screen `regression/baselines/support_v1.json` → K5 code `regression/regression_suite.py` → K3 "Why a tolerance at all?" → K5 screen `Terminal.` → K5 demo `Output after the banner (offline)` → K4 **D14** "From check to gate" → K3 "Baseline hygiene" → K6 Recap

**11.3 Generating Synthetic Test Data at Scale:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Seeds in, goldens out" → K5 code `regression/synthetic_data.py` → K3 "Two ways to generate" → K5 code `regression/synthetic_data.py` → K5 screen `Terminal.` → K5 demo `Output after the banner (offline, mock judge)` → K5 screen `Quality:` → K3 "Quality control before you trust it" → K5 screen `Terminal. Run the Lab 11.1 walkthrough.` → K5 demo `Output after the banner (offline, mock judge)` → K3 "Where synthetic cases run" → K6 Recap → "You can now" card


## Section 12: CI/CD for Agent Evaluation

Script: `02-course-content/section-12-cicd.md`.

**12.1 The Agent Quality Gate: Evals That Block Bad Deploys:** K3 "Version banner" → K3 "By the end of this lecture" → K4 **D14** "The quality gate" → K3 "A gate is four decisions" → K5 code `config/eval_config.yaml` → K5 code `reports/quality_gate.py` → K3 "Where the numbers come from" → K3 "Hard, soft, advisory" → K4 **D4** "Tiered evaluation" → K3 "Spend the eval budget where it matters" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline), the two decisio` → K5 screen `Same output. Zoom on the three "Blocking issues" l` → K3 "When the evaluation itself fails" → K6 Recap

**12.2 GitHub Actions Pipeline: Eval on Every PR:** K3 "Version banner" → K3 "By the end of this lecture" → K5 screen `.github/workflows/agent-eval.yml` → K3 "Four jobs" → K5 code `.github/workflows/agent-eval.yml` → K5 code `.github/workflows/agent-eval.yml` → K5 code `.github/workflows/agent-eval.yml` → K3 "Secrets and safety" → K5 screen `Terminal. Run the same commands CI runs, through t` → K5 demo `gh pr comment` → K5 screen `GitHub pull request page, "Conversation" tab: the ` → K6 Recap

**12.3 Experiment Tracking & Quality Dashboards:** K3 "Version banner" → K3 "By the end of this lecture" → K5 code `reports/experiments.py` → K3 "Tag runs so you can find them" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline)` → K3 "Two audiences, two views" → K5 screen `Terminal.` → K5 demo `Output after the banner (offline)` → K5 screen `localhost:8501` → K3 "What the trend shows that the gate can't" → K5 code `reports/quality_dashboard.py` → K6 Recap → "You can now" card


## Section 13: Production Monitoring & Governance

Script: `02-course-content/section-13-production.md`.

**13.1 Monitoring Agents in Production: Drift, Degradation & Alerts:** K3 "Version banner" → K3 "By the end of this lecture" → K4 **D15** "The production monitoring loop" → K3 "Four signals to watch" → K3 "Why drift happens with no code change" → K3 "Online or nightly?" → K3 "Two alert rules" → K5 code `monitoring/drift_monitor.py` → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline, simulated data)` → K5 screen `Same output. Zoom on the first alert, then the sec` → K3 "Same detector, other signals" → K3 "When an alert fires" → K6 Recap

**13.2 Enterprise AI Governance: Policies, Audit Trails & Compliance:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Four parts of agent governance" → K3 "The evaluation policy is a file you already have" → K3 "An audit trail that can't be quietly edited" → K5 code `monitoring/governance.py` → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline)` → K5 screen `Same output. Zoom on the last two lines.` → K3 "Limits of a hash chain" → K3 "Who may approve a release" → K3 "Model card for an agent" → K3 "Compliance mapping (verify with your compliance team)" → K6 Recap

**13.3 Building an Agent Quality Scorecard for Leadership:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Three questions leadership asks" → K4 **D5** "Five dimensions, one row per agent" → K5 code `demos/m13_quality_scorecard.py` → K3 "Where every number on the page comes from" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline; Support row part` → K5 screen `Same output. Highlight the Policy Assistant correc` → K3 "Present a red cell as a decision" → K6 Recap → "You can now" card


## Section 14: Enterprise Capstone — the Agent Quality Platform

Script: `02-course-content/section-14-capstone.md`.

**14.1 Capstone Architecture & Requirements:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "One question, four kinds of evidence" → K4 **D16** "The agent quality platform" → K3 "The agent contract" → K4 **D16**, build 2: the harness box expands into four stages in a row, "functional → security → performance → regression", each with its data source underneath: `golden_capstone "Four stages, one gate" → K4 **D16**, builds 3 and 4: the stages feed "Results store "Results, dashboard, gate" → K4 **D6** "Which stage covers which part of the agent" → K3 "What the capstone deliberately leaves out" → K5 code `capstone/platform.py` → K3 "Why a gate with reasons, not a weighted score" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline)` → K3 "Project 5 deliverables" → K6 Recap

**14.2 Building the Test Harness & Evaluation Pipeline:** K3 "Version banner" → K3 "By the end of this lecture" → K5 code `capstone/platform.py` → K5 code `capstone/platform.py` → K3 "The capstone golden dataset" → K5 code `capstone/platform.py` → K4 **D4** "Where this stage sits in the pyramid" → K3 "What one functional run produces" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `The functional section of the support agent's repo` → K5 screen `Same output. Zoom on "Answer Correctness 0.97".` → K6 Recap

**14.3 Adding Security Testing & Observability:** K3 "Version banner" → K3 "By the end of this lecture" → K5 code `capstone/platform.py` → K5 code `security/redteam.py` → K3 "Severity decides the order, the gate decides the release" → K5 screen `Terminal. Show what a finding looks like, using th` → K5 demo `Output after the banner (offline)` → K5 screen `make capstone` → K5 demo `Security sections of both capstone reports (offlin` → K3 "Two red-team tools, two jobs" → K5 code `observability/langfuse_tracing.py` → K5 demo `make capstone` → K6 Recap

**14.4 CI/CD Integration & Quality Dashboard:** K3 "Version banner" → K3 "By the end of this lecture" → K5 code `capstone/platform.py` → K3 "The first run records the baseline" → K5 screen `make capstone` → K5 demo `Performance and regression sections (offline; late` → K5 code `.github/workflows/agent-eval.yml` → K3 "The full tier map, now complete" → K3 "Reading a red night" → K4 **D16** build 3 "One results folder, many readers" → K5 screen `Terminal.` → K5 demo `make capstone` → K5 screen `localhost:8501` → K6 Recap

**14.5 [PROJECT 5 — CAPSTONE] Ship the Platform:** K3 "Version banner" → K3 "By the end of this lecture" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner (offline; the trace ID cha` → K5 screen `Same output. Zoom on the banking_v2 report, then o` → K3 "Now try to fool it" → K5 code `QualityPlatform.__init__` → K3 "The 'ship it' moment" → K5 screen `localhost:8501` → K3 "Project 5 checklist" → K3 "Four things reviewers flag most" → K3 "Tell it in sixty seconds" → K6 Recap → "You can now" card


## Section 15: Career & Next Steps

Script: `02-course-content/section-15-career.md`.

**15.1 AI Testing Interview Questions & Career Roadmap:** K3 "Version banner" → K3 "By the end of this lecture" → K3 "Four paths from this course" → K5 screen `04-code-examples/agent-eval-framework` → K5 demo `Output after the banner` → K3 "Five questions you will hear" → K3 "Answers 1 to 3" → K3 "Answers 4 and 5" → K3 "Three CV lines, each with a number and a source" → K3 "Your next seven days" → K6 Recap

**15.2 What Changes Next & Your 30-Day Practice Plan:** K3 "What will change, and what won't" → K3 "Your 30-day plan, 30 minutes a day" → K3 "Where to go next" → K6 Recap → "You can now" card

