"""Chaos demo (lecture 12.8): take the primary LLM down mid-call and watch the fallback.

Recording helper that wraps the capstone without changing it.

    uv run python agents/s12_chaos_demo.py dev                         # with fallback
    CHAOS_NO_FALLBACK=1 uv run python agents/s12_chaos_demo.py dev     # without fallback

Mid-call, in another terminal:

    touch /tmp/riley-kill-llm      # primary LLM starts failing
    rm /tmp/riley-kill-llm         # primary LLM recovers

Needs MAPLE_PROVIDER_MODE=inference (the default).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import s13_capstone_receptionist as capstone
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    AgentServer,
    APIConnectionError,
    APIConnectOptions,
    JobContext,
    cli,
    inference,
    llm,
)
from livekit.agents.types import NOT_GIVEN, NotGivenOr

from common import prewarm
from maple.config import Settings

KILL_FILE = Path("/tmp/riley-kill-llm")


class _FailingStream(llm.LLMStream):
    async def _run(self) -> None:
        raise APIConnectionError("chaos: primary LLM is down")


class ChaosLLM(llm.LLM):
    """Wraps a real LLM and fails every request while the kill file exists."""

    def __init__(self, inner: llm.LLM) -> None:
        super().__init__()
        self._inner = inner

    @property
    def model(self) -> str:
        return self._inner.model

    @property
    def provider(self) -> str:
        return self._inner.provider

    def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        tools: list[Any] | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        parallel_tool_calls: NotGivenOr[bool] = NOT_GIVEN,
        tool_choice: NotGivenOr[Any] = NOT_GIVEN,
        extra_kwargs: NotGivenOr[dict[str, Any]] = NOT_GIVEN,
    ) -> llm.LLMStream:
        if KILL_FILE.exists():
            return _FailingStream(self, chat_ctx=chat_ctx, tools=tools or [], conn_options=conn_options)
        return self._inner.chat(
            chat_ctx=chat_ctx,
            tools=tools,
            conn_options=conn_options,
            parallel_tool_calls=parallel_tool_calls,
            tool_choice=tool_choice,
            extra_kwargs=extra_kwargs,
        )


server = AgentServer(setup_fnc=prewarm)


@server.rtc_session()
async def entrypoint(ctx: JobContext) -> None:
    """Run the capstone entrypoint with a killable primary LLM (patched inside the job process)."""
    build_original = capstone.build_resilient_models

    def build_with_chaos(settings: Settings) -> dict[str, Any]:
        models = build_original(settings)
        primary = ChaosLLM(inference.LLM(settings.llm_model))
        if os.getenv("CHAOS_NO_FALLBACK") == "1":
            models["llm"] = primary
        else:
            models["llm"] = llm.FallbackAdapter(
                [primary, inference.LLM(settings.fallback_llm_model)], attempt_timeout=5.0
            )
        return models

    capstone.build_resilient_models = build_with_chaos
    await capstone.entrypoint(ctx)


if __name__ == "__main__":
    cli.run_app(server)
