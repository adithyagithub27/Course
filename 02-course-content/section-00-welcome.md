# Section 0: Welcome & Course Overview

> **Course:** AI Agent Testing & Evaluation: Build Production-Ready Quality Frameworks with Python (Course 2)
> **Section runtime:** ≈8 min (2 lectures)
> **Source of truth:** `01-curriculum/full-curriculum.md` (Module 00) for objectives; `14-quality-review/course2-bible.md` for agents, data, versions, commands and outputs. If a script and the code disagree, the code wins.
> **On-screen footer for every code or API slide:** "Verified: openai 2.54.0 | deepeval 4.2.7 | ragas 0.4.3 | langfuse 4.16.0 (uv.lock, checked 2026-10-01). Agent gpt-4.1-mini, judge gpt-4.1."
> **Cue legend:** `[AVATAR]` avatar narration (only these blocks go to HeyGen). `[SLIDE n: title]` a slide with bullets or a `Diagram:` line (D-numbers are the master diagrams in `10-graphics/diagrams/`); the narration under it is voice-over. `[SCREEN: ...]` screen recording. `[CODE: ...]` code on screen. `[DEMO: ...]` terminal output pasted from a real run. `[B-ROLL: ...]` cutaway. `[PAUSE]` a one-beat pause.
> **Commands** run from `04-code-examples/agent-eval-framework/` after `make install`. Every output below was captured offline (`OFFLINE=1`: deterministic mock LLM and mock judge, no API key), so students get the same numbers. Word counts are spoken words only, counted by the section checker.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 0.1 | Your AI Agent Just Failed in Production — Now What? | SL | 3:00 | 424 |
| 0.2 | Course Roadmap & Environment Setup | SC | 5:00 | 591 |

**Section guardrails (do not deviate on screen):** the running example is the TechCorp support agent (`agents/support_agent.py`, five tools: `lookup_customer`, `search_knowledge_base`, `create_ticket`, `send_email`, `escalate_to_human`). Install is `make install` (`uv sync --locked`), not `pip install` plus a hand-made venv. No API key is needed for anything in this section. Never type a real key on camera.

---

## Lecture 0.1 — Your AI Agent Just Failed in Production — Now What?

| Field | Value |
|---|---|
| ID | 0.1 |
| Title | Your AI Agent Just Failed in Production — Now What? |
| Type | SL (hook and showcase, one short demo) |
| Target duration | 3:00 (420 spoken words at 140 wpm) |
| Learning objectives | 1. Describe how a one-line prompt change can make a support agent invent policy without any error in the logs. 2. Name the four systems the course builds: evaluation suite, red-team report, monitoring dashboard, CI quality gate. 3. Explain why an evaluation, not a unit test, catches this class of failure. |
| Prerequisites | None |
| Files used | `demos/m00_agent_failure.py`; `regression/regression_suite.py` (`PROMPT_V2_REGRESSED`); `agents/support_agent.py` (`SYSTEM_PROMPT`); Diagram D1 (`10-graphics/diagrams/D1-six-failure-modes.svg`) |

### Script

[AVATAR]
Someone deleted one line from a support agent's system prompt. One line. It looked like a harmless cleanup. The next customer asked about refunds, and the agent said: fourteen-day money-back guarantee, about ten business days. The real policy? Thirty days, and five to seven business days. [PAUSE] No error. No exception. Every log line looked clean. So here's my question: would your tests have caught it?

[SLIDE 1: Your AI Agent Just Failed in Production]
- Agents fail politely: no error, wrong answer
- This course: catch it before your users do

By the end of this course, you'll catch failures like this before a single customer sees them. Let me show you the one we just described, running for real.

[SCREEN: Terminal in `agent-eval-framework`. Run the 0.1 demo. Let the version banner sit for a beat, then zoom on the deleted line.]

```bash
uv run python demos/m00_agent_failure.py
```

[DEMO: Output (banner trimmed)]
```text
The 'harmless' prompt edit deleted this line:
   - Only state prices, limits and policies that appear in a knowledge base result

BEFORE (v1) tools=['search_knowledge_base']
  answer: TechCorp offers a 30-day money-back guarantee on all plans. Refunds are processed within 5-7 business days, and annual subscriptions are prorated.
  Faithfulness vs the refund policy: 1.00 -> PASS

AFTER  (v2) tools=[]
  answer: We offer a 14-day money-back guarantee, and refunds take about 10 business days.
  Faithfulness vs the refund policy: 0.00 -> FAIL: block this deploy
```

This is the TechCorp support agent you'll test all course. Before the edit, it searched the knowledge base and quoted the policy. Faithfulness: one point zero. After the edit, look at the tools list. Empty. It answered from memory, and every number is wrong. Faithfulness: zero. One metric, one line of output, and that deploy is blocked.

[SLIDE 2: Why nobody noticed]
Diagram: D1 build 1 (hallucination panel highlighted; the other five modes greyed out).

Why did nobody notice? Because the agent didn't crash. It answered fluently. A status-code check passes. A latency check passes. Only a check that compares the answer with the real policy fails. Now picture this at scale. Here's an illustrative scenario from the course materials: a support agent tells two hundred thirty customers their overdraft fees were waived, and the company honors forty-seven thousand dollars of mistakes. The root cause is the same: a prompt change, and no evaluation suite to run.

[SLIDE 3: What you'll build in this course]
- An evaluation suite scored on five quality dimensions
- A red-team report from real attacks on your agent
- A monitoring dashboard for quality drift in production
- A CI quality gate that blocks bad merges

So what will you build? Four systems. First, an evaluation suite that scores your agent on correctness, faithfulness, relevance, safety and reliability. One command, numbers instead of opinions.

[B-ROLL: Quick cuts, two seconds each: the Project 1 report table, a promptfoo red-team results grid, the Streamlit quality dashboard, a GitHub pull request with a red "agent quality gate: FAILED" check.]

Second, a red-team report. You'll attack your own agents with prompt injections and jailbreaks, and find the holes first. Third, a monitoring dashboard, so drift shows up on a chart, not in a complaint three days later. Fourth, a CI quality gate. Every pull request runs your evals, and if quality drops, the merge is blocked. All four in Python, all yours to reuse at work.

[SLIDE 4: Recap]
- Agents fail silently: clean logs, wrong answers
- One evaluation metric caught the bad deploy
- You'll build four quality systems from scratch

Lock it in. Agents fail silently; the logs stayed clean while the refund policy changed. One faithfulness check caught it before deploy. And over this course, you'll build the four systems that make that check routine.

[AVATAR]
Next, you'll see the full roadmap and get the course repo running on your machine. Two commands, about two hundred tests, and no API key required. Let's go.

### Recap

A one-line prompt edit made the TechCorp agent skip its knowledge base and invent a 14-day refund policy with no error anywhere; a single Faithfulness check (1.00 before, 0.00 after) blocks that deploy, and the course builds the four systems that make such checks routine.

### Transition

Next: Lecture 0.2 — Course Roadmap & Environment Setup.

### Speaker notes: common student mistakes / Q&A

- The demo is offline: the "after" answer comes from the mock LLM following the edited prompt. Live, gpt-4.1-mini with the same deleted line also tends to answer pricing and refund questions from memory, but its exact wording and numbers vary. If you want a live clip, re-capture with `OFFLINE=0` before recording and keep the offline output on screen if the live run happens to search anyway.
- The $47,000 / 230-customer story is the curriculum's illustrative scenario (FinServe Corp, Module 00), not a reported incident. Keep the word "illustrative" on screen.
- "Is faithfulness the same as correctness?" No. Lecture 2.2 separates them. Here it's enough that the answer contradicts the policy it should have used.
- The deleted line is the same regression Module 11 uses (`PROMPT_V2_REGRESSED`), so students will see this failure again at scale.

---

## Lecture 0.2 — Course Roadmap & Environment Setup

| Field | Value |
|---|---|
| ID | 0.2 |
| Title | Course Roadmap & Environment Setup |
| Type | SC (screencast: terminal and editor) |
| Target duration | 5:00 (700 words at 140 wpm; ~590 spoken, the rest is install and test output) |
| Learning objectives | 1. Install the locked environment with `make install` and run the offline suite with `make test` (204 passed, 5 skipped). 2. Explain offline mode and when an `OPENAI_API_KEY` is needed. 3. Navigate the 16-module roadmap and the repo folders that each part of the course uses. |
| Prerequisites | 0.1; Python 3.11+ and `uv` installed |
| Files used | `Makefile`; `pyproject.toml`; `uv.lock`; `.env.example`; `README.md`; `demos/m00_verify_setup.py`; `demos/m00_hello_eval.py`; `tests/` |

### Script

[AVATAR]
Two hundred and four tests, in about ten seconds, with no API key. That's what you'll have on your machine five minutes from now. No fighting package versions, no surprise bills. You install a locked environment once, and every demo in this course runs the same way for you as it does for me.

[SLIDE 1: Course Roadmap & Environment Setup]
- Install the locked environment with two commands
- Know when you need an API key
- Find your way around the roadmap and repo

[SLIDE 2: Verified for this course]
- `openai 2.54.0` and `deepeval 4.2.7`
- `ragas 0.4.3`, `langfuse 4.16.0`, `mcp 2.2.0`
- Agent `gpt-4.1-mini`, judge `gpt-4.1`
- Python 3.11 or newer; Node 20+ in Module 8

These are the exact versions I recorded with, pinned in the repo's lock file. If your screen ever looks different from mine, check this list first.

[SLIDE 3: Sixteen modules, five stages]
Diagram: Roadmap strip, left to right, from "Agent chaos" to "Production quality platform". Five stages: Foundations (Modules 0 to 2), Evaluation (3 to 7: metrics, RAG, tools and MCP, multi-agent), Security (8), Operations (9 to 13: tracing, performance, regression, CI/CD, monitoring), Capstone and career (14 and 15). Project markers at 3.4, 5.4, 6.4, 8.4 and the capstone at 14.

Where are you headed? Sixteen modules in five stages. Foundations first: what agents are, and why testing them is different. Then evaluation: metrics, RAG, tool calling and multi-agent systems. Then security and red teaming. Then operations: tracing, performance, regression, CI/CD and monitoring. And a capstone that ties it all into one quality platform. Along the way you'll finish four projects plus that capstone. Every one tests a real agent in the same repo.

[SLIDE 4: What you need]
- Python 3.11 or newer
- `uv`, the Python package manager
- An OpenAI key: optional, for live runs only
- Node 20 or newer, only from Module 8

You need Python three eleven or newer, and `uv`. That's it to start. Do you need an OpenAI key? No, it's optional. Without one, the repo runs in offline mode, and offline mode costs nothing. Live runs cost a few cents each; check the current pricing before you run a big suite. Node twenty only matters in Module 8, for promptfoo.

[SCREEN: Terminal, dark theme, large font. Open the `agent-eval-framework` folder from the course resources. Run the install.]

```bash
make install
```

[DEMO: Output (tail)]
```text
uv sync --locked
Resolved 158 packages in 4ms
Audited 151 packages in 2ms
Next: make test
```

`make install` runs `uv sync` with the lock file, so you get exactly the packages I tested. On a fresh machine you'll see the install progress instead of "audited", and it takes about a minute. It also copies the example settings file to `.env`. Now the moment of truth.

[SCREEN: Same terminal. Run the test suite.]

```bash
make test
```

[DEMO: Output (last lines)]
```text
SKIPPED [2] tests/live/test_live_smoke.py: live test: set OFFLINE=0 and OPENAI_API_KEY (make eval)
SKIPPED [3] tests/live/test_live_smoke.py:24: live test: set OFFLINE=0 and OPENAI_API_KEY (make eval)
204 passed, 5 skipped in 8.33s
```

Two hundred four passed, five skipped. The five skipped tests are the live ones. They wait for a real key. Everything else ran against a deterministic stand-in model and a stand-in judge. So, why does that matter? Because you get the same numbers I do, every time.

[SCREEN: VS Code, `.env`. Highlight `OPENAI_API_KEY=` (empty), `OFFLINE=`, `OPENAI_MODEL=gpt-4.1-mini`, `OPENAI_JUDGE_MODEL=gpt-4.1`.]

Here's the settings file. The key is empty, and that's fine. `OFFLINE` one forces offline mode, zero forces live. The agent model is `gpt-4.1-mini`, and the judge is `gpt-4.1`. When you add a key later, it goes here, never in code, and `.env` is already ignored by git.

[SCREEN: Terminal. Run the setup check.]

```bash
uv run python demos/m00_verify_setup.py
```

[DEMO: Output (banner trimmed)]
```text
[OK] openai                                 2.54.0
[OK] deepeval                               4.2.7
[OK] ragas                                  0.4.3
[OK] langfuse                               4.16.0
[OK] mcp                                    2.2.0
[OK] opentelemetry-sdk                      1.45.0
[OK] opentelemetry-semantic-conventions     0.66b0
[OK] streamlit                              1.64.0
[OK] pytest                                 9.1.1
[--] OPENAI_API_KEY set                     optional offline
[--] LANGFUSE keys set                      optional until Module 9
[OK] support agent answers                  2 LLM calls, tools ['search_knowledge_base']
[OK] DeepEval metric runs                   AnswerRelevancy = 1.00

Setup complete. You're ready for Module 1.
```

What does the setup check actually check? Nine packages, two optional keys, and then it does real work. It asks the support agent a question, two LLM calls and one knowledge-base search, and scores the answer with a DeepEval metric. Relevancy: one point zero. Then the smallest eval in the course.

[SCREEN: Terminal.]

```bash
uv run python demos/m00_hello_eval.py
```

[DEMO: Output (banner trimmed)]
```text
hello eval PASSED
```

[SLIDE 5: The repo you'll work in]
```text
agents/       support_agent.py (TechCorp, 5 tools) + 4 more agents
config/       models, prices, thresholds (eval_config.yaml)
datasets/     golden_support.json (10 cases) and friends
evaluators/   DeepEval metrics, judge, RAGAS, tool checks
security/     promptfoo, Garak, PyRIT, PII scanner
observability/ performance/ regression/ monitoring/ reports/
demos/        61 lecture demos (mXX_*.py)
tests/        unit/ component/ trajectory/ e2e/ production/ live/
```

A quick tour. Where does everything live? Agents holds the five agents you'll test, starting with TechCorp support. You don't build them; you test them. Config holds models, prices and every quality threshold. Datasets holds your golden test cases. Evaluators is where metrics live. Security, observability, performance, regression and monitoring each light up in their own module. Demos has one file per lecture, sixty-one of them. And tests is organized in five layers you'll meet in Lecture 2.3.

[SLIDE 6: Recap]
- `make install`, then `make test`: 204 passed
- Offline mode: no key, same numbers as mine
- Sixteen modules, one repo, one running agent

Three things. Two commands give you a locked environment and two hundred four passing tests. Offline mode means no key and no cost, with the same numbers I get. And the whole course runs in one repo, around one agent.

[SLIDE 7: You can now]
- Explain how a silent agent failure gets caught
- Install and verify the course environment
- Run any lecture demo offline

[AVATAR]
You can now explain how a silent agent failure gets caught, and your environment is ready. Next, Module 1 starts with the three things about large language models every tester needs: tokens, context windows and temperature. Just enough to see why agents are hard to test.

### Recap

`make install` (`uv sync --locked`) and `make test` give every student the same locked environment and 204 passing offline tests; an API key is optional until you want live runs; the course is 16 modules around one repo and one running agent.

### Transition

Next: Lecture 1.1 — LLMs in 10 Minutes: Tokens, Context, Temperature.

### Speaker notes: common student mistakes / Q&A

- Re-capture `make install` on the recording machine from a clean clone: a first install prints "Installed N packages" rather than "Audited". Keep the last line, "Next: make test".
- Verify before recording: how students get the repo (GitHub link or zip in the lecture resources). The script says "from the course resources"; change the screen action, not the narration, if it is a `git clone`.
- `make test` time varies (8 to 13 seconds here). Say "about ten seconds", never a precise figure.
- "I get `uv: command not found`." Install uv from docs.astral.sh/uv, restart the terminal. pip users can run `pip install -r requirements.txt` (generated from `uv.lock`), but every lecture uses `uv run`.
- "Do I need a key at all?" Not for any lecture demo. Live runs (`make eval`, `OFFLINE=0`) need `OPENAI_API_KEY`; Langfuse keys are optional until Module 9. Live costs: verify current pricing.
- Lecture count: the course has 55 video lectures (the curriculum's 54 plus 8.5 on Garak and PyRIT). Don't state total hours here until the curriculum header is updated.
- `uv run deepeval test run demos/m00_hello_eval.py` currently fails with `No module named '_common'` (the demos import a helper that pytest can't see). Use the plain `uv run python` command shown; the code fix belongs to T-CODE.
