"""
TechCorp Reply Desk: a 3-agent system for Module 7 (Lab 7.1).

    Supervisor  -> decides who works next (LLM call returning JSON)
    Research    -> searches the TechCorp knowledge base (tool-calling LLM)
    Writer      -> drafts the customer reply from the research findings (LLM)

Agents talk only through ``Message`` objects carrying a checksum, so tests can
check every hand-off. ``FailureInjection`` switches on the four Lab 7.1
failures at the boundaries between agents:

    research_empty    the knowledge base returns nothing
    writing_toxic     the writer's draft comes back abusive
    research_loop     research keeps asking for clarification (infinite delegation)
    corrupt_message   a message is altered in transit (checksum mismatch)

The supervisor must detect each one and degrade gracefully. Loops are caught
by ``LoopDetector`` (3 identical consecutive actions) and a 10-step budget.

    python -m agents.multi_agent "Customer asks: how long do refunds take?"
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field

from agents.llm import get_client
from agents.support_agent import execute_tool as support_execute_tool
from config.settings import agent_model
from performance.reliability import LoopDetector

SUPERVISOR_PROMPT = """You are the Supervisor of the TechCorp Reply Desk.
Workers: "research" (finds facts in the knowledge base) and "writer" (drafts the reply).
Given the request and the work done so far, reply with JSON only:
{"next": "research" | "writer" | "finish", "instruction": "<what the worker should do>"}
Send research first, then the writer, then finish."""

RESEARCH_PROMPT = """You are the Research Agent of the TechCorp Reply Desk.
Use search_knowledge_base to find the facts needed for the task.
Reply with "FINDINGS:" followed by the facts you found, or "FINDINGS: none"."""

WRITER_PROMPT = """You are the Writing Agent of the TechCorp Reply Desk.
Write a short, polite reply to the customer using ONLY the findings provided."""

RESEARCH_TOOLS = [
    {"type": "function", "function": {
        "name": "search_knowledge_base", "description": "Search the product knowledge base",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
]

TOXIC_WORDS = ["idiot", "stupid", "shut up", "useless customer", "dumb"]
FALLBACK_REPLY = (
    "Thanks for your patience. I couldn't confirm the details automatically, so a member "
    "of our support team will follow up with you within one business day."
)


def checksum(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


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


@dataclass
class FailureInjection:
    research_empty: bool = False
    writing_toxic: bool = False
    research_loop: bool = False
    corrupt_message: bool = False


@dataclass
class RunResult:
    request: str
    final_reply: str
    status: str  # "ok" | "degraded"
    steps: int
    messages: list[Message] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    delegations: list[str] = field(default_factory=list)

    @property
    def failure_types(self) -> list[str]:
        return [f["type"] for f in self.failures]


class ResearchAgent:
    name = "research"

    def __init__(self, inject: FailureInjection) -> None:
        self.inject = inject

    def _tool(self, name: str, args: dict) -> str:
        if self.inject.research_empty:
            return "No relevant articles found in the knowledge base."
        return support_execute_tool(name, args)

    def run(self, task: str) -> str:
        if self.inject.research_loop:
            return "NEED_CLARIFICATION: which plan is the customer on?"
        client, model = get_client(), agent_model()
        messages = [{"role": "system", "content": RESEARCH_PROMPT}, {"role": "user", "content": task}]
        for _ in range(3):
            resp = client.chat.completions.create(model=model, messages=messages, tools=RESEARCH_TOOLS, tool_choice="auto")
            choice = resp.choices[0]
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                messages.append(choice.message)
                for tc in choice.message.tool_calls:
                    result = self._tool(tc.function.name, json.loads(tc.function.arguments))
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                return choice.message.content or "FINDINGS: none"
        return "FINDINGS: none"


class WritingAgent:
    name = "writer"

    def __init__(self, inject: FailureInjection) -> None:
        self.inject = inject

    def run(self, request: str, findings: str) -> str:
        client, model = get_client(), agent_model()
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": WRITER_PROMPT},
                {"role": "user", "content": f"Customer request: {request}\n\n{findings}"},
            ],
            temperature=0,
        )
        draft = resp.choices[0].message.content or ""
        if self.inject.writing_toxic:
            draft = "Read the docs yourself, you idiot. " + draft
        return draft


def is_toxic(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in TOXIC_WORDS)


class Supervisor:
    """Coordinates research and writing, validating every hand-off."""

    def __init__(self, inject: FailureInjection | None = None, max_steps: int = 10) -> None:
        self.inject = inject or FailureInjection()
        self.research = ResearchAgent(self.inject)
        self.writer = WritingAgent(self.inject)
        self.max_steps = max_steps

    def _decide(self, request: str, findings: str | None, draft: str | None) -> dict:
        state = {"request": request, "findings": findings, "draft": draft}
        resp = get_client().chat.completions.create(
            model=agent_model(),
            messages=[{"role": "system", "content": SUPERVISOR_PROMPT}, {"role": "user", "content": json.dumps(state)}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        try:
            decision = json.loads(resp.choices[0].message.content or "{}")
        except json.JSONDecodeError:
            decision = {}
        if decision.get("next") not in ("research", "writer", "finish"):
            decision = {"next": "finish", "instruction": "invalid decision"}
        return decision

    def _send(self, run: RunResult, sender: str, receiver: str, content: str) -> Message:
        msg = Message(sender, receiver, content, msg_id=len(run.messages) + 1)
        if self.inject.corrupt_message and sender == "research" and len(run.messages) < 3:
            msg.content = msg.content[: len(msg.content) // 2] + "\x00###"  # altered in transit
        run.messages.append(msg)
        return msg

    def run(self, request: str) -> RunResult:
        run = RunResult(request=request, final_reply="", status="ok", steps=0)
        detector = LoopDetector(max_repeats=3, max_steps=self.max_steps)
        findings: str | None = None
        draft: str | None = None
        retried_corruption = False

        while True:
            run.steps += 1
            decision = self._decide(request, findings, draft)
            action = decision["next"]
            run.delegations.append(action)
            loop = detector.record(action, decision.get("instruction", ""))
            if loop:
                run.failures.append({"type": "loop_detected", "agent": "research", "details": loop})
                break
            if action == "finish":
                break

            if action == "research":
                self._send(run, "supervisor", "research", decision.get("instruction") or request)
                out = self.research.run(request)
                msg = self._send(run, "research", "supervisor", out)
                if not msg.is_valid():
                    run.failures.append({"type": "corrupted_message", "agent": "research", "details": f"checksum mismatch on message {msg.msg_id}"})
                    if not retried_corruption:
                        retried_corruption = True
                        continue
                    break
                if out.startswith("NEED_CLARIFICATION"):
                    findings = None  # nothing usable: the supervisor will ask again
                    continue
                if out.strip().lower() in ("findings: none", "") or "no relevant articles" in out.lower():
                    run.failures.append({"type": "empty_research", "agent": "research", "details": "no findings"})
                    break
                findings = out

            elif action == "writer":
                self._send(run, "supervisor", "writer", findings or "")
                out = self.writer.run(request, findings or "")
                self._send(run, "writer", "supervisor", out)
                if is_toxic(out):
                    run.failures.append({"type": "unsafe_output", "agent": "writer", "details": "toxic language blocked"})
                    break
                draft = out

        if run.failures or not draft:
            run.status = "degraded"
            run.final_reply = FALLBACK_REPLY
        else:
            run.final_reply = draft
        return run


def run_multi_agent(request: str, inject: FailureInjection | None = None) -> RunResult:
    return Supervisor(inject).run(request)


if __name__ == "__main__":
    req = " ".join(sys.argv[1:]) or "Customer asks: how long do refunds take?"
    r = run_multi_agent(req)
    print(f"Status: {r.status}  steps: {r.steps}  delegations: {r.delegations}")
    print(f"Reply: {r.final_reply}")
