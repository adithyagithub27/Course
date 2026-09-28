# Lab 5: Add an Insurance Agent

| Field | Details |
|---|---|
| **Section / lecture** | Section 7, lecture 7.6 |
| **Time estimate** | 60 minutes |
| **Difficulty** | Intermediate |
| **Goal** | Extend Riley's handoff graph from Greeter → Booking / Billing to Greeter → Booking / Billing / **Insurance**, with pure-Python insurance rules, shared state, context carry-over, and tests that prove the routing works. |
| **You will produce** | `src/maple/insurance.py`, `tests/unit/test_insurance.py`, `agents/lab05_multi_agent.py`, `tests/agent/test_lab05_handoffs.py`, and a short routing table in `notes/lab-05.md` |

---

## Prerequisites

- Lectures 7.1 to 7.5 watched; `agents/s07_multi_agent.py` runs in console mode.
- Lab 3 done (you know what a voice-first prompt looks like).
- `OPENAI_API_KEY` set for the behaviour tests in Step 6 (`tests/agent/conftest.py` skips them cleanly without it).

## Why an Insurance agent?

"Do you take my insurance?" is the second most common call a dental front desk gets. Today the Billing agent handles it with a generic FAQ lookup, which cannot tell a Cigna PPO (in network) from a Cigna DHMO (not accepted). You will give insurance its own specialist with a real rule engine, so Billing can focus on payments and bills.

Target graph:

```text
                 ┌──────────────> BookingAgent ───┐
 GreeterAgent ───┼──────────────> BillingAgent ───┼──> back_to_front_desk ──> GreeterAgent
                 └──────────────> InsuranceAgent ─┤
                                        └─────────┴──> transfer_to_booking ──> BookingAgent
```

---

## Step 1: Write the insurance rules in pure Python

Business logic goes in `src/maple/`, never inside the agent (lecture 5.2). The rules come from the "Insurance accepted" section of `src/maple/data/faq.md`: in network with Delta Dental, Cigna, MetLife, Aetna, Guardian and United Concordia **PPO** plans; other PPO plans accepted out of network; no HMO or Medicaid plans.

Create `src/maple/insurance.py`:

```python
"""Dental insurance rules for Maple Street Dental (Lab 5).

Pure Python, like the rest of ``src/maple``: the Insurance agent's tool is a thin
wrapper around :func:`insurance_status`. The rules mirror the "Insurance accepted"
section of ``data/faq.md``.
"""

from __future__ import annotations

import re

# Carrier -> spellings callers (and STT) produce.
IN_NETWORK_CARRIERS: dict[str, tuple[str, ...]] = {
    "Delta Dental": ("delta dental", "delta"),
    "Cigna": ("cigna",),
    "MetLife": ("metlife", "met life"),
    "Aetna": ("aetna",),
    "Guardian": ("guardian",),
    "United Concordia": ("united concordia", "concordia"),
}
NOT_ACCEPTED_WORDS = ("hmo", "dhmo", "medicaid", "chip")

GUIDANCE = {
    "in_network": "The clinic is in network with this PPO plan. Say so in one sentence and offer to book.",
    "in_network_if_ppo": (
        "The clinic is in network with this company's PPO plans only. Ask whether the plan is a PPO or an HMO."
    ),
    "out_of_network": (
        "This is a PPO plan the clinic is not in network with. Say the clinic accepts it as out of network "
        "and files the claim for the patient. Do not estimate coverage."
    ),
    "not_accepted": (
        "The clinic does not accept HMO or Medicaid dental plans. Say so kindly and offer self-pay options "
        "or a transfer to the front desk."
    ),
    "unknown": (
        "You cannot tell whether this plan is accepted. Ask for the plan type, or offer to have the front "
        "desk check and call back. Never guess."
    ),
}


def _normalize(text: str) -> str:
    """Lowercase, drop dots (so "P.P.O." becomes "ppo") and turn other punctuation into spaces."""
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower().replace(".", "")).split())


def insurance_status(provider: str) -> str:
    """Classify a caller's insurance as one of the keys of :data:`GUIDANCE`."""
    text = _normalize(provider)
    words = set(text.split())
    if any(word in words for word in NOT_ACCEPTED_WORDS):
        return "not_accepted"
    carrier = any(alias in text for aliases in IN_NETWORK_CARRIERS.values() for alias in aliases)
    is_ppo = "ppo" in words
    if carrier:
        return "in_network" if is_ppo else "in_network_if_ppo"
    if is_ppo:
        return "out_of_network"
    return "unknown"
```

> **Checkpoint 1:** `uv run python -c "from maple.insurance import insurance_status; print(insurance_status('Cigna DHMO'))"` prints `not_accepted`.

---

## Step 2: Unit-test the rules

Create `tests/unit/test_insurance.py`:

```python
import pytest

from maple.insurance import GUIDANCE, insurance_status


@pytest.mark.parametrize(
    "said, expected",
    [
        ("Delta Dental PPO", "in_network"),
        ("It's MetLife P.P.O.", "in_network"),
        ("met life ppo", "in_network"),
        ("Cigna", "in_network_if_ppo"),
        ("Cigna DHMO", "not_accepted"),
        ("Texas Medicaid", "not_accepted"),
        ("Humana PPO", "out_of_network"),
        ("Humana", "unknown"),
        ("", "unknown"),
    ],
)
def test_insurance_status(said, expected):
    assert insurance_status(said) == expected


def test_every_status_has_speakable_guidance():
    for status in ("in_network", "in_network_if_ppo", "out_of_network", "not_accepted", "unknown"):
        assert status in GUIDANCE
        assert "http" not in GUIDANCE[status] and "*" not in GUIDANCE[status]
```

```bash
uv run pytest tests/unit/test_insurance.py -v
```

Expected: `10 passed` (nine parametrised cases plus the guidance test).

> **Checkpoint 2:** the unit tests pass, and `make test` is still green.

---

## Step 3: Copy the multi-agent file and add state

```bash
cp agents/s07_multi_agent.py agents/lab05_multi_agent.py
```

In `agents/lab05_multi_agent.py`, extend the shared userdata without touching `agents/common.py`:

```python
from dataclasses import dataclass

from maple.insurance import GUIDANCE, insurance_status


@dataclass
class LabCallState(CallState):
    """CallState plus what the Insurance agent learns."""

    insurance_provider: str | None = None
    insurance_status: str | None = None
```

Change the entrypoint to use it: `userdata=LabCallState()`.

Note what you are **not** storing: member IDs or group numbers. The agent does not need them to answer "do you take my plan?", and not collecting data is the easiest way to protect it (Section 11).

---

## Step 4: Add the Insurance agent

Add the prompt text and the class below the `BillingAgent` class:

```python
INSURANCE_SPECIALIST_EXTRA = """\
Your role in this call: insurance specialist. You answer whether the clinic accepts the caller's
dental insurance. As soon as the caller names their insurance company, call check_insurance and
follow its guidance. Never estimate what a plan will pay; the front desk can check benefits.
Do not ask for member IDs or group numbers. When the caller wants to book, hand off to booking."""


class InsuranceAgent(KnowledgeToolsMixin, Agent):
    """Insurance specialist: accepted plans, in and out of network."""

    def __init__(self, *, chat_ctx: ChatContext | None = None) -> None:
        super().__init__(
            instructions=prompts.build_instructions(
                today=clinic_today(), knowledge=True, extra=INSURANCE_SPECIALIST_EXTRA
            ),
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        """Continue the insurance question without making the caller repeat it."""
        self.session.generate_reply(
            instructions="In one short sentence, say you can help with insurance. If the caller already "
            "named their insurance, check it now; otherwise ask which insurance company and plan they have."
        )

    @function_tool
    async def check_insurance(self, context: RunContext[LabCallState], provider: str) -> str:
        """Check whether the clinic accepts the caller's dental insurance. Call this as soon as the
        caller names their insurance company.

        Args:
            provider: The insurance company and plan type as the caller said it, for example
                "Delta Dental PPO" or "Cigna".
        """
        status = insurance_status(provider)
        context.userdata.insurance_provider = provider
        context.userdata.insurance_status = status
        return GUIDANCE[status]

    @function_tool
    async def transfer_to_booking(self, context: RunContext[LabCallState]) -> tuple[Agent, str]:
        """Hand the caller to the booking specialist when they want to book, reschedule or cancel."""
        context.userdata.notes.append("handoff: insurance -> booking")
        return BookingAgent(chat_ctx=carry_over(self)), "Transferring to the booking specialist."

    @function_tool
    async def back_to_front_desk(self, context: RunContext[LabCallState]) -> tuple[Agent, str]:
        """Return to the front desk when the caller has no more insurance questions."""
        context.userdata.notes.append("handoff: insurance -> greeter")
        return GreeterAgent(chat_ctx=carry_over(self)), "Returning to the front desk."
```

`carry_over()` (already in the file) copies the recent conversation without the previous agent's instructions, so the specialist sees what the caller said but follows its own rules.

---

## Step 5: Re-route the Greeter and narrow Billing

The Greeter's routing lives in its prompt **and** its tools. Update both.

1. Add routing text near the top of the file:

```python
LAB_GREETER_EXTRA = """\
Your role in this call: front desk greeter.
Find out what the caller needs. Hand off to the booking specialist for appointments, to the
insurance specialist for whether their dental insurance is accepted, and to the billing specialist
for payments, payment plans, prices and bills. Answer simple clinic questions yourself with
lookup_clinic_info."""

LAB_BILLING_EXTRA = """\
Your role in this call: billing specialist. You explain payment options, payment plans and typical
price ranges using lookup_clinic_info. Insurance acceptance questions belong to the insurance
specialist: hand back to the front desk for those. You cannot see account balances; offer a
transfer to the billing office for balance questions or disputes."""
```

2. In `GreeterAgent.__init__`, change `extra=prompts.GREETER_EXTRA` to `extra=LAB_GREETER_EXTRA`. In `BillingAgent.__init__`, change `extra=prompts.BILLING_SPECIALIST_EXTRA` to `extra=LAB_BILLING_EXTRA`.

3. Add a tool to `GreeterAgent`, and tighten the billing tool's description so the two do not overlap:

```python
    @function_tool
    async def transfer_to_insurance(self, context: RunContext[LabCallState]) -> tuple[Agent, str]:
        """Hand the caller to the insurance specialist when they ask whether the clinic takes their
        dental insurance, or whether a plan is in network."""
        context.userdata.notes.append("handoff: greeter -> insurance")
        return InsuranceAgent(chat_ctx=carry_over(self)), "Transferring to the insurance specialist."

    @function_tool
    async def transfer_to_billing(self, context: RunContext[LabCallState]) -> tuple[Agent, str]:
        """Hand the caller to the billing specialist for payments, payment plans, prices or bills.
        Not for insurance acceptance questions."""
        context.userdata.notes.append("handoff: greeter -> billing")
        return BillingAgent(chat_ctx=carry_over(self)), "Transferring to the billing specialist."
```

Try it:

```bash
uv run agents/lab05_multi_agent.py console
```

Script:

1. "Hi, do you take Cigna?" → Insurance agent; asks PPO or HMO.
2. "It's a PPO." → in network; offers to book.
3. "Great, can I book a cleaning Thursday morning?" → Booking agent, without re-asking what you want.
4. "Actually, how much is a filling without insurance?" → back to the front desk, then Billing.

Watch the log for the tool calls (`transfer_to_insurance`, `check_insurance`, `transfer_to_booking`, ...).

> **Checkpoint 3:** all four steps route correctly, and no agent asks for information the caller already gave.

---

## Step 6: Prove the routing with behaviour tests

Create `tests/agent/test_lab05_handoffs.py`:

```python
"""Lab 5: routing tests for the Insurance specialist.

Uses the `llm` fixture from tests/agent/conftest.py; live tests skip without OPENAI_API_KEY.
pyproject.toml puts agents/ on the import path, so the lab file imports directly.
"""
from lab05_multi_agent import BillingAgent, GreeterAgent, InsuranceAgent, LabCallState
from livekit.agents import AgentSession


async def test_insurance_question_goes_to_insurance_specialist(llm) -> None:
    async with AgentSession(llm=llm, userdata=LabCallState()) as session:
        await session.start(GreeterAgent())
        result = await session.run(user_input="Hi, do you take Delta Dental?")
        result.expect.contains_function_call(name="transfer_to_insurance")
        result.expect.contains_agent_handoff(new_agent_type=InsuranceAgent)
        assert "handoff: greeter -> insurance" in session.userdata.notes


async def test_plan_type_is_checked_and_stored(llm) -> None:
    async with AgentSession(llm=llm, userdata=LabCallState()) as session:
        await session.start(InsuranceAgent())
        await session.run(user_input="I have a Delta Dental PPO plan. Are you in network?")
        assert session.userdata.insurance_status == "in_network"


async def test_payment_plan_question_still_goes_to_billing(llm) -> None:
    async with AgentSession(llm=llm, userdata=LabCallState()) as session:
        await session.start(GreeterAgent())
        result = await session.run(user_input="Do you offer payment plans for a crown?")
        result.expect.contains_function_call(name="transfer_to_billing")
        result.expect.contains_agent_handoff(new_agent_type=BillingAgent)
```

Run:

```bash
uv run pytest tests/agent/test_lab05_handoffs.py -v
```

Expected: `3 passed` with a key, `3 skipped` without one. Run it three times; routing tests should be stable. If one flips, the tool descriptions still overlap (see troubleshooting).

> **Checkpoint 4:** the three behaviour tests pass three runs in a row.

---

## Step 7: Record the routing table

In `notes/lab-05.md`, write the routing table you designed. One row per caller intent:

| Caller says | Expected agent | Tool that routes it | Tested? |
|---|---|---|---|
| "Do you take Cigna?" | Insurance | `transfer_to_insurance` | yes |
| "Do you have payment plans?" | Billing | `transfer_to_billing` | yes |
| "Can I book a cleaning?" | Booking | `transfer_to_booking` | |
| "What are your hours?" | Greeter (no handoff) | `lookup_clinic_info` | |
| "My insurance is in network, can I book?" (in Insurance) | Booking | `transfer_to_booking` | |

Add at least two rows of your own, including one ambiguous request (for example "How much will my insurance pay for a crown?") and the agent you decided should own it.

---

## Stretch goal

Callers switch topics fast. Make the Insurance agent robust to "Also, can I pay in instalments?" without bouncing through the Greeter: add a direct `transfer_to_billing` tool on `InsuranceAgent`, then write a test that a two-topic turn ("Do you take Aetna PPO, and do you do payment plans?") ends in the right place with both questions answered. Decide, and write down, whether direct specialist-to-specialist handoffs make your graph easier or harder to reason about.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Insurance questions still go to Billing | Old `GREETER_EXTRA` still in use, or `transfer_to_billing` still mentions insurance | Use `LAB_GREETER_EXTRA`; remove "insurance" from the billing tool's docstring |
| The Insurance agent asks "Which insurance do you have?" after the caller already said it | Chat context not carried over | Pass `chat_ctx=carry_over(self)` in every handoff tool |
| `AttributeError: 'CallState' object has no attribute 'insurance_status'` | Entrypoint still creates `CallState()` | Use `userdata=LabCallState()` in the entrypoint **and** in tests |
| `ModuleNotFoundError: lab05_multi_agent` in tests | Running pytest from outside the repo root, so `pyproject.toml`'s `pythonpath = ["src", "agents"]` is not applied | Run `uv run pytest ...` from the repo root |
| `contains_agent_handoff` fails but the log shows the handoff | The handoff happened in a later turn, or to a different agent class | Print `result.events` to see what happened in this turn; check the `new_agent_type` class you imported is the one the tool returns |
| Riley reads "in network if PPO" literally | Returned guidance treated as a script | Guidance strings are instructions for the model; keep "Say so in one sentence" style wording |
| "Delta" matches something unrelated | Loose alias | Acceptable for a lab; in production match against the full plan list from your clearinghouse |

---

## Solution notes

- **Design principle:** each specialist owns one kind of question, and tool descriptions say both what they cover and what they do **not** cover. Overlapping descriptions ("insurance" in both Billing and Insurance) are the most common cause of flaky routing.
- **Where the logic lives:** `insurance_status()` is pure Python and unit-tested; the agent tool is a three-line wrapper. The same function could serve a web chatbot or the Pipecat version.
- **State:** `LabCallState` extends `CallState`, so every existing tool and agent keeps working. The Insurance agent stores provider and status, not member IDs.
- **Handoff mechanics:** tools return `(AgentInstance, "message")`; `carry_over()` copies recent conversation without the old instructions; each agent's `on_enter` continues the conversation instead of re-greeting.
- **Expected test results:** unit tests 10/10; behaviour tests 3/3, stable over repeated runs once descriptions are disjoint.
- Reference implementation of the pattern: `03-code/agents/s07_multi_agent.py` (`GreeterAgent`, `BookingAgent`, `BillingAgent`, `carry_over`). The insurance rules above were verified against the FAQ in `03-code/src/maple/data/faq.md`.
