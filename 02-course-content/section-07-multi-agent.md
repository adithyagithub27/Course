# Section 7: Multi-Agent System Testing

> **Course:** AI Agent Testing & Evaluation (DeepEval, RAGAS, promptfoo, Langfuse)
> **Module:** 07 (curriculum `01-curriculum/full-curriculum.md`, Module 07)
> **Section runtime:** 24 minutes (3 lectures; Lab 7.1 follows Lecture 7.3)
> **Running example:** the TechCorp Reply Desk, `agents/multi_agent.py`: a Supervisor, a Research Agent and a Writing Agent that pass `Message` objects with checksums. It answers the same customer questions as the TechCorp support agent, from the same knowledge base.
> **Source of truth:** `14-quality-review/course2-bible.md` and the code in `04-code-examples/agent-eval-framework/`. If this script and the code disagree, the code wins.
> **Production format:** HeyGen avatar for `[AVATAR]` blocks; OBS screen recording for `[SCREEN]`, `[CODE]` and `[DEMO]`; slides built from `[SLIDE]` cues by `slide_builder.py`. Diagrams are Course 2 masters in `10-graphics/diagrams/` (D-numbers).
> **Standing on-screen note (every code lecture, lower third, first 10 seconds):** "Verified: openai 2.54.0 | deepeval 4.2.7. Offline mode: mock LLM + mock judge."
> **Numbers:** every run here is offline (`OFFLINE=1`, deterministic mock LLM). Failures are injected on purpose with `FailureInjection`, so they reproduce exactly; the detection code is the same live.
> **Word counts** are spoken words only. Build-along lectures run below 140 words per minute to leave room for code, commands and output.

| ID | Title | Type | Target | Spoken words |
|---|---|---|---|---|
| 7.1 | Multi-Agent Architectures: What Can Go Wrong | Diagram | 8:00 | 961 |
| 7.2 | Testing Agent Communication, Delegation & Coordination | Build-along | 8:00 | 805 |
| 7.3 | Detecting Infinite Loops, State Corruption & Failure Propagation | Build-along | 8:00 | 773 |
| | **Total** | | **24:00** | **2,539** |

**Cue legend:** as in `section-05-rag-eval.md`. `[DEMO]` blocks are pasted from real runs; `[CODE]` blocks are copied from the named file.

**Code names used in this section (matched to `04-code-examples/agent-eval-framework/`):** `Supervisor`, `ResearchAgent`, `WritingAgent`, `Message`, `checksum`, `FailureInjection` (`research_empty`, `writing_toxic`, `research_loop`, `corrupt_message`), `RunResult` (`final_reply`, `status`, `steps`, `messages`, `failures`, `delegations`), `run_multi_agent`, `FALLBACK_REPLY`, `is_toxic` in `agents/multi_agent.py`; `LoopDetector`, `detect_tool_loop` in `performance/reliability.py`; tests in `tests/trajectory/test_multi_agent.py`.

---

## Lecture 7.1 — Multi-Agent Architectures: What Can Go Wrong

| Field | Value |
|---|---|
| ID | 7.1 |
| Title | Multi-Agent Architectures: What Can Go Wrong |
| Type | Diagram (slides + avatar, one terminal demo) |
| Target duration | 8:00 (about 961 spoken words, 6:52 of talking at 140 wpm) |
| Learning objectives | 1. Compare four multi-agent architectures: hierarchical, peer-to-peer, pipeline and debate. 2. Name the failures that only appear between agents: miscommunication, delegation errors, infinite delegation loops, state corruption and failure propagation. 3. Explain why a multi-agent system must degrade to a safe reply instead of passing garbage downstream. |
| Prerequisites | Module 1 (the six failure modes); Module 6 (tool calling) |
| Files used | `agents/multi_agent.py`; `demos/m07_multi_agent_failures.py`; diagram D11 (`10-graphics/diagrams/D11-multi-agent-failure-cascade.svg`, builds 1 to 5) |
| Version banner | `Verified: openai 2.54.0 | deepeval 4.2.7` |

### Script

[AVATAR]
Three agents. One customer question: "How long do refunds take?" When everything works, the answer arrives in three steps. [PAUSE] Now break one thing. The research agent keeps asking for clarification. Or a message gets altered on its way between agents. Or the knowledge base comes back empty. Each agent, tested alone, would pass. The question is what the customer sees. By the end of this lecture, you'll be able to name the failures that live between agents, and know what a safe system does when they happen.

[SLIDE 1: Four ways to wire agents together]
- Hierarchical: a supervisor delegates to workers
- Peer-to-peer: agents message each other freely
- Pipeline: each agent hands off to the next
- Debate: agents critique each other's answers
Footer: Verified: openai 2.54.0 | deepeval 4.2.7. Offline mode: mock LLM + mock judge.

There are four common ways to wire agents together. Hierarchical: a supervisor hands work to specialist workers and decides when the job is done. Peer-to-peer: agents message each other directly. Pipeline: a fixed chain, each agent passing its output to the next. And debate: two or more agents critique each other until they agree.

Frameworks like LangGraph, CrewAI and AutoGen can build all four. The testing questions are the same whichever one you use.

[SLIDE 2: Each shape fails its own way]
- Peer-to-peer: circular delegation
- Pipeline: errors flow downstream
- Debate: endless argument, or agreeing on wrong
- Hierarchy: one bad router, many wrong jobs

Each shape has a favourite way to fail. Which one have you built? [PAUSE] Peer-to-peer systems love circular delegation: A asks B, B asks A. Pipelines pass errors downstream, because each stage trusts the one before it. Debates can argue forever, or agree on something wrong. And hierarchies put everything on the supervisor: if it routes badly, every worker does the wrong job well.

[SLIDE 3: The TechCorp Reply Desk]
- Supervisor: picks research, writer or finish
- Research Agent: searches the knowledge base
- Writing Agent: drafts the customer reply
- Every hand-off is a checksummed `Message`

Our system is hierarchical. The TechCorp Reply Desk has three agents. The supervisor is a model call that returns JSON: who works next, research, writer or finish, and an instruction. The research agent searches the knowledge base and replies with findings. The writing agent turns those findings into a polite reply.

Agents never call each other directly. Every hand-off is a message object with a sender, a receiver, the content and a checksum. That design choice is what makes the system testable. Can you guess why? [PAUSE] Because every hand-off becomes a record you can inspect and assert on.

[SLIDE 4: Hand-offs grow fast]
- 3 agents, everyone talks: 6 directed hand-offs
- Supervisor in the middle: 4 directed hand-offs
- Each hand-off is a place to fail

Here's the math that makes multi-agent testing harder. With three agents where anyone can message anyone, there are six directed hand-offs to test. Route everything through a supervisor, and there are four. Add a fourth agent to a free-for-all, and how many is it? Twelve. Fewer paths means fewer places for a message to go wrong, which is a big reason the hierarchical pattern is popular in production.

[SLIDE 5: New failures between agents]
- Miscommunication: a message missing what the next agent needs
- Delegation error: the wrong worker gets the task
- Infinite delegation: work bounces back and forth
- State corruption: data altered or stale in transit
- Failure propagation: one bad output poisons the rest

Every single-agent failure mode from Module 1 still applies to each agent. But five new ones appear between them. Miscommunication: a message that's well formed but missing what the next agent needs. Delegation errors: the supervisor sends a task to the wrong worker. That's wrong tool selection, one level up. Infinite delegation: work bouncing between agents forever. That's failure mode six, infinite loops, at the system level.

State corruption: data altered in transit, or one agent acting on a value another agent already changed. Picture agent A reading a balance of one hundred dollars, agent B updating it to fifty, and agent A acting on the stale hundred. And the most dangerous one: failure propagation.

[SLIDE 6: How one agent's failure spreads]
Diagram: D11, shown as builds 1 to 5: agent C fails; agent B passes it on; agent A builds on it; the user gets a wrong answer; where to test, a check at every hand-off.

Here's propagation, step by step. Agent C fails, say an empty search. Agent B doesn't notice and passes on whatever it got. Agent A, the writer, does its job beautifully, on top of nothing. And the user receives a confident, polished, wrong answer.

Where would you put the check? [PAUSE] The last build shows it: at every hand-off. The error should stop where it started. Here's an illustrative case, made up but realistic. A design-review system needs three approvals. One reviewer agent times out. The supervisor sees two approvals and no denial, and reports "approved". A missing "no" is not a "yes".

[SLIDE 7: What a safe system returns]
- ok: everything worked
- recovered: a failure was caught and retried successfully
- degraded: the customer gets a safe fallback reply

So what should a system do when a hand-off fails? The Reply Desk reports one of three statuses. "Ok" means everything worked. "Recovered" means something failed, it was caught, and a retry worked. "Degraded" means the system gave up safely and sent a fallback: a member of the support team will follow up within one business day. Never garbage. Which status would you rather see in a dashboard at 3 a.m.? [PAUSE] Degraded is fine. Garbage marked "ok" is the nightmare.

[SCREEN: Terminal. Run the failure montage; pause on each of the four blocks.]

```bash
uv run python demos/m07_multi_agent_failures.py
```

[DEMO: Output (banner trimmed; replies cut at 110 characters by the demo)]
```text
[healthy] status=ok steps=3
  delegations: ['research', 'writer', 'finish']
  failures   : none
  reply      : Hi there, thanks for reaching out. TechCorp offers a 30-day money-back guarantee on all plans. Refunds are pro

[1 infinite delegation loop] status=degraded steps=3
  delegations: ['research', 'research', 'research']
  failures   : [{'type': 'loop_detected', 'agent': 'research', 'details': "'research' repeated 3 times in a row"}]
  reply      : Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will f

[2 state corruption (message altered in transit)] status=recovered steps=4
  delegations: ['research', 'research', 'writer', 'finish']
  failures   : [{'type': 'corrupted_message', 'agent': 'research', 'details': 'checksum mismatch on message 2', 'recovered': True}]
  reply      : Hi there, thanks for reaching out. TechCorp offers a 30-day money-back guarantee on all plans. Refunds are pro

[3 failure cascade (research returns nothing)] status=degraded steps=1
  delegations: ['research']
  failures   : [{'type': 'empty_research', 'agent': 'research', 'details': 'no findings'}]
  reply      : Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will f
```

The healthy run: research, writer, finish. Three steps, status ok, and the reply quotes the 30-day guarantee.

Failure one, the loop. The research agent keeps asking which plan the customer is on, so the supervisor keeps sending research. After three identical delegations in a row, the loop detector stops it. Status degraded, fallback reply. Three steps, not three hundred.

[SCREEN: Zoom on blocks 2 and 3; highlight `checksum mismatch on message 2` and `status=degraded steps=1`.]

Failure two, corruption. Message two, research to supervisor, arrived altered: its checksum didn't match. The supervisor caught it, asked research again, and the retry was clean. Status recovered, and the customer still got the right answer.

Failure three, the cascade that didn't happen. The knowledge base returned nothing. Instead of handing an empty finding to the writer, the supervisor stopped after one step and sent the fallback. The writer never got the chance to write something confident about nothing.

[AVATAR]
Notice what this demo didn't test: whether each agent is individually good. You did that in Modules 3 to 6, and you still need it. Multi-agent tests sit on top. They ask whether the system stays safe when one of its parts misbehaves. Count the outcomes: one ok, one recovered, two degraded, and zero garbage replies. What would your own multi-agent system score on that count today?

[SLIDE 8: Recap]
- Agents fail between each other, too
- Loops, corruption and cascades need system tests
- Degrade to a safe reply, never garbage

### Recap

Multi-agent systems add five failures that live between agents: miscommunication, delegation errors, infinite delegation, state corruption and failure propagation. A safe system checks every hand-off, stops errors where they start, and reports ok, recovered or degraded instead of passing garbage to the customer.

### Transition

In Lecture 7.2, you'll write the tests that check every one of those hand-offs: who talks to whom, in what order, intact, and with the right content.

### Speaker notes: common student mistakes / Q&A

- **Offline and injected.** The three failures are switched on with `FailureInjection`; they are deterministic by design. The detection code (loop detector, checksum, empty-findings check) is the same live. Re-capture live before recording only if you want a live healthy run on screen.
- **State corruption, two kinds.** The code models corruption as a message altered in transit (checksum mismatch). The curriculum's stale-read example (balance 100 vs 50) is taught conceptually on slide 4; it needs version numbers or compare-and-set on shared state, which the Reply Desk does not have because its agents share no mutable state. Do not claim the demo shows a stale read.
- **The design-review example** is illustrative (adapted from the curriculum's AutoDesk scenario). Do not quote its "72% delegation accuracy", "47 LLM calls" or "$12" as facts (A6).
- **Hand-off arithmetic:** directed pairs in a full mesh of n agents = n × (n − 1): 6 for three agents, 12 for four. Hub-and-spoke with one supervisor and w workers = 2w: 4 for two workers.
- **"Which framework does the Reply Desk use?"** None: plain Python and the OpenAI SDK, so the hand-offs are visible. The same tests apply to LangGraph, CrewAI or AutoGen if you can capture each hand-off.

---

## Lecture 7.2 — Testing Agent Communication, Delegation & Coordination

| Field | Value |
|---|---|
| ID | 7.2 |
| Title | Testing Agent Communication, Delegation & Coordination |
| Type | Build-along |
| Target duration | 8:00 (about 805 spoken words, 5:45 of talking at 140 wpm; the rest is code and output) |
| Learning objectives | 1. Make hand-offs testable with a message object that carries sender, receiver and a checksum. 2. Write five hand-off checks: delegation order, message integrity, routing topology, content flow and step budget. 3. Parse a supervisor's routing decision defensively so an invalid decision fails safe. |
| Prerequisites | 7.1 |
| Files used | `agents/multi_agent.py` (`Message`, `checksum`, `Supervisor._decide`); `demos/m07_communication_tests.py`; `tests/trajectory/test_multi_agent.py` |
| Version banner | `Verified: openai 2.54.0 | deepeval 4.2.7` |

### Script

[AVATAR]
The final reply looks perfect. Three plans, the right prices. Pro at twenty-nine ninety-nine. [PAUSE] But did the writer actually use the research? Or did it remember the prices from somewhere and get lucky? Unless you test the hand-offs, you can't tell. By the end of this lecture, you'll be able to check every message between agents: who sent it, who got it, in what order, intact, and with the right content.

[SLIDE 1: Test the conversation, not just the answer]
- Final reply: what the customer sees
- Messages: how the agents got there
- Most multi-agent bugs hide in the messages
Footer: Verified: openai 2.54.0 | deepeval 4.2.7. Offline mode: mock LLM + mock judge.

In Module 3, you graded an agent's final answer. That's still necessary here, but it isn't enough. A multi-agent system has an internal conversation, and that's where most of its bugs hide. So the first job is to capture that conversation in a form you can assert on.

[CODE: `agents/multi_agent.py`, `Message`]
```python
@dataclass
class Message:
    """A hand-off between agents."""

    sender: str
    receiver: str
    content: str
    msg_id: int
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            self.checksum = checksum(self.content)

    def is_valid(self) -> bool:
        return bool(self.content) and checksum(self.content) == self.checksum

    def to_dict(self) -> dict:
        return {"id": self.msg_id, "from": self.sender, "to": self.receiver, "content": self.content, "valid": self.is_valid()}
```

Here's the message. Five fields: sender, receiver, content, an ID and a checksum. The checksum is the first twelve hex characters of a SHA-256 hash of the content, computed when the message is created.

`is_valid` checks two things. The content isn't empty, and it still matches its checksum. If anything changes the content after it was sent, a bug, a truncation, a bad serializer, validation fails. Why not just compare strings? [PAUSE] Because the receiver doesn't have the original to compare against. The checksum travels with the message.

[CODE: `agents/multi_agent.py`, `Supervisor._decide` (defensive parsing)]
```python
        try:
            decision = json.loads(resp.choices[0].message.content or "{}")
        except json.JSONDecodeError:
            decision = {}
        if decision.get("next") not in ("research", "writer", "finish"):
            decision = {"next": "finish", "instruction": "invalid decision"}
        return decision
```

The supervisor's decision is a model call in JSON mode. Models usually return valid JSON, but "usually" isn't a test strategy. So the code parses defensively. If the JSON is broken, or "next" isn't one of the three allowed workers, the decision becomes "finish". With no draft yet, finishing means the fallback reply. An invalid decision fails safe instead of crashing, or worse, sending work to a worker that doesn't exist.

[SLIDE 2: Five hand-off checks]
- Delegation: research before the writer
- Integrity: every message passes its checksum
- Topology: workers only talk to the supervisor
- Content flow: the writer used the findings
- Budget: finished within 10 steps

Now the tests. Five checks, one for each way a hand-off can go wrong.

Delegation: research must come before the writer. A writer with no research is a hallucination waiting to happen. Integrity: every message passes its checksum. Topology: workers only ever talk to the supervisor, never to each other. That keeps us at four hand-off paths, not six.

Content flow is the clever one. How do you prove the writer used the research? Check that a fact only the research could supply shows up in the reply. Here, that's the Pro price, twenty-nine ninety-nine. And budget: the whole run finishes within ten steps.

[SLIDE 3: Delegation accuracy]
- Table: request and the expected first worker
- Run each request; record the supervisor's choice
- Score accuracy, like tool selection in 6.2

What about delegation accuracy, when a supervisor has several specialists to choose from? Say billing and technical support. Test it exactly like tool selection in Lecture 6.2: a table of requests, each with the worker it should go to first, and an accuracy number across the table. A supervisor choosing a worker is an agent choosing a tool, one level up.

[CODE: `demos/m07_communication_tests.py`, the five checks]
```python
r = run_multi_agent("Customer asks: what are your pricing plans?")
table([m.to_dict() | {"content": m.content[:60]} for m in r.messages], width=60)
checks = {
    "research is called before the writer": r.delegations[:2] == ["research", "writer"],
    "every message passes its checksum": all(m.is_valid() for m in r.messages),
    "workers only talk to the supervisor": all("supervisor" in (m.sender, m.receiver) for m in r.messages),
    "writer used the research findings": "$29.99" in r.final_reply,
    "finished within the step budget": r.steps <= 10,
}
```

Here they are in code. Each check is one line, and each reads like the slide. Notice that none of them needs a judge model. The run result already holds the delegations, the messages and the step count.

[SCREEN: Terminal. Run the communication tests; pause on the message table, then the five PASS lines.]

```bash
uv run python demos/m07_communication_tests.py
```

[DEMO: Output (banner trimmed; content cut at 60 characters by the demo)]
```text
id  from        to          content                                                       valid
--  ----------  ----------  ------------------------------------------------------------  -----
1   supervisor  research    Find the facts needed to answer: Customer asks: what are you  True
2   research    supervisor  FINDINGS: KB-101 (Plans and pricing): TechCorp offers three   True
3   supervisor  writer      FINDINGS: KB-101 (Plans and pricing): TechCorp offers three   True
4   writer      supervisor  Hi there, thanks for reaching out. TechCorp offers three pla  True

[PASS] research is called before the writer
[PASS] every message passes its checksum
[PASS] workers only talk to the supervisor
[PASS] writer used the research findings
[PASS] finished within the step budget

Final reply: Hi there, thanks for reaching out. TechCorp offers three plans: Basic ($9.99/mo), Pro ($29.99/mo), and Enterprise (custom pricing). All plans include core features. Pro adds priority support and advanced analytics. Let us know if there's anything else we can help with. Best regards, TechCorp Support
```

Read the table as a conversation. Message one: the supervisor asks research to find the facts. Message two: research returns findings from KB-101, plans and pricing. Message three: the supervisor forwards those findings to the writer. Why route them through the supervisor instead of straight to the writer? So one place sees, and checks, every hand-off. Message four: the writer's draft goes back to the supervisor. Four messages, all valid, and every one has the supervisor on one end.

All five checks pass, and the final reply carries the three prices from KB-101: nine ninety-nine, twenty-nine ninety-nine and custom pricing for Enterprise.

[CODE: `tests/trajectory/test_multi_agent.py`, the healthy-run test]
```python
@pytest.mark.multi_agent
def test_healthy_run_delegates_research_then_writer():
    r = run_multi_agent("Customer asks: what are your pricing plans?")
    assert r.status == "ok" and r.delegations == ["research", "writer", "finish"]
    assert [(m.sender, m.receiver) for m in r.messages] == [("supervisor", "research"), ("research", "supervisor"),
                                                            ("supervisor", "writer"), ("writer", "supervisor")]
    assert all(m.is_valid() for m in r.messages)
    assert "$29.99" in r.final_reply
```

[SLIDE 4: Coordination without shared state]
- Agents share nothing mutable
- All state travels inside messages
- No locks, no races, nothing stale

One more design choice to notice: coordination. The Reply Desk's agents share no mutable state. Everything one agent knows reaches the next inside a message. That means no locks to test and no race conditions. If your agents do share a database or a scratchpad, you'll need tests for concurrent writes, which Lecture 7.3 touches on.

In the test suite, the same idea is even stricter. It asserts the exact sequence of sender and receiver pairs. If someone adds a shortcut that lets research talk straight to the writer, this test fails on the next pull request. What else would you add? A test that feeds the supervisor broken JSON and asserts a safe finish is a good first exercise.

[SCREEN: Terminal. Run the multi-agent tests.]

```bash
uv run pytest -q tests/trajectory/test_multi_agent.py
```

[DEMO: Output (trimmed)]
```text
.......                                                                  [100%]
7 passed in 0.04s
```

Seven tests: the healthy run, four injected failures, a toxic-text test and a checksum test. You'll meet the injected ones in the next lecture.

[SLIDE 5: Recap]
- Test hand-offs, not just the final reply
- Check order, integrity, topology and content flow
- Parse routing decisions defensively

### Recap

Capture every hand-off as a message with a sender, a receiver and a checksum, and you can test a multi-agent system's internal conversation: research before writing, every message intact, workers talking only to the supervisor, research facts reaching the reply, and a step budget. Invalid routing decisions fail safe.

### Transition

Healthy runs are the easy part. In Lecture 7.3, you'll break the Reply Desk on purpose, with loops, corrupted messages and empty research, and prove it degrades safely every time.

### Speaker notes: common student mistakes / Q&A

- **Offline.** The supervisor's JSON decisions come from the mock LLM, which follows `SUPERVISOR_PROMPT` ("research first, then the writer, then finish"). Re-capture live before recording if you show a live run; live decisions should match, and if they don't, that's a delegation failure your tests catch.
- **"Is a 12-character SHA-256 prefix secure?"** It is an integrity check against accidental changes, not a security control. For tamper resistance across services, sign messages (HMAC) instead.
- **Content-flow checks** need a fact that only the research could supply. Pick one per test request (a price, a limit, a KB ID) and assert it appears in the reply; for open-ended replies, use a GEval faithfulness check against the findings.
- **Exercise for students:** a test that patches `Supervisor._decide`'s model reply with invalid JSON and asserts `status == "degraded"` and the fallback reply. Not in the repo; it is the suggested extension.
- **Timing** (`0.04s`) varies by machine; the count (7) is stable.

---

## Lecture 7.3 — Detecting Infinite Loops, State Corruption & Failure Propagation

| Field | Value |
|---|---|
| ID | 7.3 |
| Title | Detecting Infinite Loops, State Corruption & Failure Propagation |
| Type | Build-along |
| Target duration | 8:00 (about 773 spoken words, 5:31 of talking at 140 wpm; the rest is code and output) |
| Learning objectives | 1. Build a runtime loop detector that halts after three identical consecutive actions or a ten-step budget. 2. Detect and recover from a corrupted hand-off with a checksum and one retry. 3. Use failure injection to prove each failure is detected and the system degrades to a safe fallback. |
| Prerequisites | 7.2 |
| Files used | `performance/reliability.py` (`LoopDetector`, `detect_tool_loop`); `agents/multi_agent.py` (`Supervisor.run`, `FailureInjection`, `FALLBACK_REPLY`); `demos/m07_loop_detector.py`; `demos/m07_lab_failure_injection.py`; `tests/trajectory/test_multi_agent.py` |
| Version banner | `Verified: openai 2.54.0 | deepeval 4.2.7` |

### Script

[AVATAR]
Step four: research. Step five: research. Step six: research. [PAUSE] Halt. Without that halt, an agent loop doesn't fail loudly. It just keeps calling the model, and keeps billing you, until something times out. By the end of this lecture, you'll be able to stop loops, catch corrupted hand-offs, and prove with injected failures that your multi-agent system always ends in a safe place.

[SLIDE 1: Three runtime guards]
- Loop detector: 3 identical actions, or 10 steps
- Checksum: corrupted message, retry once
- Hand-off checks: empty or unsafe output stops the run
Footer: Verified: openai 2.54.0 | deepeval 4.2.7. Offline mode: mock LLM + mock judge.

This lecture is about guards that run in production, inside the system, not just in your test suite. Three of them. A loop detector. A checksum with one retry. And hand-off checks that stop the run when a worker returns nothing usable, or something unsafe. Then you'll prove each guard works by breaking the system on purpose.

[CODE: `performance/reliability.py`, `LoopDetector`]
```python
class LoopDetector:
    """Flags an agent that repeats itself or runs past its step budget.

    ``record`` returns a reason string when a loop is detected, else None.
    """

    def __init__(self, max_repeats: int = 3, max_steps: int = 10) -> None:
        self.max_repeats = max_repeats
        self.max_steps = max_steps
        self.history: list[tuple[str, str]] = []

    def record(self, action: str, detail: str = "") -> str | None:
        self.history.append((action, detail))
        if len(self.history) > self.max_steps:
            return f"step budget exceeded ({self.max_steps} steps)"
        tail = self.history[-self.max_repeats :]
        if len(tail) == self.max_repeats and len(set(tail)) == 1:
            return f"'{action}' repeated {self.max_repeats} times in a row"
        return None
```

Here's the whole loop detector. You record every action, with a detail string. Two rules. If the history passes ten steps, the step budget is exceeded. And if the last three entries are identical, action and detail both, that's a loop.

Why compare the detail too? [PAUSE] Because research twice with two different questions is progress. Research three times with the same question is a loop. And why keep the step budget as well? Because a loop can alternate, research, writer, research, writer, and never repeat three times in a row. The budget catches what the pattern misses.

[SCREEN: Terminal. Run the loop detector demo.]

```bash
uv run python demos/m07_loop_detector.py
```

[DEMO: Output (banner trimmed)]
```text
step 1: research  find refund facts    -> ok
step 2: research  find refund facts    -> ok
step 3: writer    draft                -> ok
step 4: research  which plan?          -> ok
step 5: research  which plan?          -> ok
step 6: research  which plan?          -> HALT: 'research' repeated 3 times in a row

On a single agent's tool calls: 'search_knowledge_base' repeated 3 times in a row
```

Steps one and two repeat, but only twice, and then the writer runs. Fine. Steps four, five and six are identical: halt at six. The last line reuses the same detector on a single agent's tool calls: four identical knowledge base searches, flagged on the third. One class guards both the system and each agent inside it. The single support agent has a backstop of its own, too: a hard cap of five model calls per request.

[CODE: `agents/multi_agent.py`, `Supervisor.run` (the corruption and empty-findings guards)]
```python
                msg = self._send(run, "research", "supervisor", out)
                if not msg.is_valid():
                    run.failures.append({"type": "corrupted_message", "agent": "research", "details": f"checksum mismatch on message {msg.msg_id}"})
                    if not retried_corruption:
                        retried_corruption = True
                        run.failures[-1]["recovered"] = True  # provisional: the retry must succeed
                        continue
                    run.failures[-1]["recovered"] = False
                    break
                if out.startswith("NEED_CLARIFICATION"):
                    findings = None  # nothing usable: the supervisor will ask again
                    continue
                if out.strip().lower() in ("findings: none", "") or "no relevant articles" in out.lower():
                    run.failures.append({"type": "empty_research", "agent": "research", "details": "no findings"})
                    break
```

Now the supervisor's guards, all in one place. A message that fails its checksum is recorded as a failure, and the supervisor retries once. Why only once? Because one corruption can be a glitch, but two in a row means something systematic. A second corruption breaks the run. A request for clarification sends the supervisor back around, which is exactly what the loop detector watches. And empty findings stop the run immediately. That last one is the cascade breaker: the writer never sees an empty finding, so it can't dress one up.

[SLIDE 2: The end of every run]
- Any unrecovered failure: degraded, fallback reply
- No draft at all: degraded, fallback reply
- Failures all recovered: recovered, real reply
- No failures: ok, real reply

At the end of every run, one rule decides the outcome. Any unrecovered failure, or no draft at all, means degraded and the fallback reply. Failures that were all recovered means recovered, with the real reply. No failures means ok. There's no path where garbage reaches the customer marked as success. How would you prove that? [PAUSE] Inject every failure and check.

[CODE: `demos/m07_lab_failure_injection.py`, the injection loop]
```python
EXPECT = {"research_empty": "empty_research", "writing_toxic": "unsafe_output",
          "research_loop": "loop_detected", "corrupt_message": "corrupted_message"}
rows = []
for flag, expected in EXPECT.items():
    r = run_multi_agent("Customer asks: how do I reset my password?", FailureInjection(**{flag: True}))
```

`FailureInjection` has four switches, one per Lab 7.1 failure. Research returns empty. The writer's draft comes back abusive. Research loops. A message is corrupted. For each one, you assert two things: the right failure was detected, and the run ended degraded or recovered.

[SCREEN: Terminal. Run the failure-injection demo.]

```bash
uv run python demos/m07_lab_failure_injection.py
```

[DEMO: Output (banner trimmed)]
```text
injected         detected           expected           status     steps  result
---------------  -----------------  -----------------  ---------  -----  ------
research_empty   empty_research     empty_research     degraded   1      PASS
writing_toxic    unsafe_output      unsafe_output      degraded   2      PASS
research_loop    loop_detected      loop_detected      degraded   3      PASS
corrupt_message  corrupted_message  corrupted_message  recovered  4      PASS

degraded = the customer gets the safe fallback; recovered = failure caught and the retry succeeded.
Fallback reply: Thanks for your patience. I couldn't confirm the details automatically, so a member of our support team will follow up with you within one business day.
```

Four injections, four detections, four passes. Empty research: stopped after one step. Toxic writer: caught after two, and the abusive draft never left the building. The loop: three steps. Corruption: recovered in four, with the real password-reset answer.

Look at the steps column. The worst case is four steps, well under the budget of ten. That's what bounded failure looks like.

[SLIDE 3: A good fallback reply]
- Honest: says it couldn't confirm the details
- Sets an expectation: one business day
- Invents nothing: no prices, no policies
- Logged: the failure type travels with the run

And look at the fallback itself. Is it a good reply? It's honest: it says the system couldn't confirm the details. It sets an expectation: a person follows up within one business day. It invents nothing. And the failure type is recorded in the run result, so it shows up in your traces in Module 9. A fallback is a product decision as much as an engineering one, so write it with your support team.

[AVATAR]
These same four injections are parametrized tests in the suite you ran in 7.2, so they run on every pull request. And they're your next assignment. In Lab 7.1, you'll inject each failure yourself, confirm detection, and then try to break the guards. Then add a fifth failure of your own. What would it be? [PAUSE] A writer that ignores the findings is a good one. Make the system catch it.

[SLIDE 4: Recap]
- Halt on 3 repeats or 10 steps
- Checksum hand-offs; retry once, then degrade
- Inject every failure; assert a safe ending

### Recap

Runtime guards keep multi-agent failures bounded: a loop detector that halts on three identical actions or ten steps, checksums with one retry for corrupted hand-offs, and hand-off checks that stop on empty or unsafe output. Failure injection proves each one ends degraded or recovered, never in garbage.

[SLIDE 5: You can now]
- Name the failures between agents
- Test hand-offs for order and integrity
- Inject failures and verify safe degradation

### Transition

Do Lab 7.1 now, while the Reply Desk is fresh. Then, in Lecture 8.1, the failures stop being accidents: you'll meet the attackers who try to cause them on purpose.

### Speaker notes: common student mistakes / Q&A

- **Offline and injected.** All failures here are injected with `FailureInjection` and reproduce exactly; the guards are the same code live. Re-capture live before recording only if you want a live healthy run on screen.
- **Toxic-output detection** in the code is a small keyword list (`TOXIC_WORDS`, `is_toxic`) so it runs offline. In production, use a moderation model or a GEval safety metric; say this if students ask.
- **Stale-state corruption** (agent A acting on a value agent B changed) is not modelled in the Reply Desk, which has no shared mutable state. If a student's system shares state, the test is: version every write and assert that a write based on an old version is rejected.
- **The single-agent cap**: `run_support_agent(max_iterations=5)` stops after five LLM calls with an escalation reply; `tests/trajectory/test_support_trajectories.py::test_iteration_cap_stops_runaway_loops` proves it. Lecture 10.2 reuses `LoopDetector` for reliability.
- **Lab 7.1** reference output is `demos/m07_lab_failure_injection.py`. The old 2-agent router/specialist lab (`07-labs/lab-06`) is superseded by the 3-agent Reply Desk (T-DOCS owns the lab rewrite).
