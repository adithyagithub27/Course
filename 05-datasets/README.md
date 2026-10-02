# 05-datasets: enterprise scenario datasets

Five scenario datasets, one per enterprise domain the course uses. Every file
uses the same schema:

| Field | Meaning |
|---|---|
| `id` | stable case ID |
| `agent` | which agent the case targets (a repo file, or "scenario only") |
| `category` | scenario category within the domain |
| `input` | the user message |
| `expected_tools` | tools the agent should call, in order (`[]` = none) |
| `expected_behavior` | what a correct response does |
| `quality_dimensions` | from the five dimensions (T3): correctness, faithfulness, relevance, safety, reliability |
| `failure_modes` | from the six failure modes (T2): hallucination, wrong tool selection, incorrect tool arguments, reasoning errors, goal drift, infinite loops |
| `notes` | extra context (security notes, original checks) |

| File | Cases | Domain | Agent | Modules |
|---|---|---|---|---|
| `enterprise-scenarios/customer-support-agent-scenarios.json` | 12 | TechCorp SaaS support (running example) | `agents/support_agent.py` | 1, 3, 4, 6, 12, 14 |
| `enterprise-scenarios/hr-agent-scenarios.json` | 8 | HR policy Q&A | `agents/rag_agent.py` | 5 |
| `enterprise-scenarios/insurance-claims-agent-scenarios.json` | 10 | insurance claims policy RAG (InsureCo, HealthFirst) | scenario only | 5, 11 |
| `enterprise-scenarios/banking-agent-scenarios.json` | 12 | SecureBank customer banking | `agents/banking_agent.py` | 8 (Project 4) |
| `enterprise-scenarios/software-engineering-agent-scenarios.json` | 6 | coding assistant | scenario only | 6, 8 |

The runnable golden datasets that the tests use live in the student repo:
`04-code-examples/agent-eval-framework/datasets/` (`golden_support.json` uses
the four categories faq / account / escalation / security, 3/3/2/2).
