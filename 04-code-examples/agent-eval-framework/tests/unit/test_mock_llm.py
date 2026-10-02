"""Unit: the offline mock LLM is deterministic and speaks the OpenAI response format."""

from openai.types.chat import ChatCompletion

from agents.llm import VirtualClock
from agents.mock_llm import MockOpenAI
from agents.support_agent import SYSTEM_PROMPT, TOOLS


def _ask(client, text, **kw):
    return client.chat.completions.create(model="gpt-4.1-mini", messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                                                           {"role": "user", "content": text}], tools=TOOLS, **kw)


def test_returns_real_openai_types_with_tool_calls():
    r = _ask(MockOpenAI(), "What are your pricing plans?")
    assert isinstance(r, ChatCompletion)
    assert r.choices[0].finish_reason == "tool_calls"
    assert r.choices[0].message.tool_calls[0].function.name == "search_knowledge_base"
    assert r.usage.total_tokens == r.usage.prompt_tokens + r.usage.completion_tokens > 0


def test_same_inputs_same_outputs_across_clients():
    a = [_ask(MockOpenAI(), "Hi").choices[0].message.content for _ in range(1)]
    b = [_ask(MockOpenAI(), "Hi").choices[0].message.content for _ in range(1)]
    assert a == b


def test_virtual_clock_advances():
    clock = VirtualClock()
    _ask(MockOpenAI(clock=clock), "What are your pricing plans?")
    assert 0.3 < clock.now() < 1.0


def test_unknown_system_prompt_uses_generic_brain():
    r = MockOpenAI().chat.completions.create(model="m", messages=[{"role": "user", "content": "How long do refunds take?"}], temperature=0)
    assert "5-7 business days" in r.choices[0].message.content
