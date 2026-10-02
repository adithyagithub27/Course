"""
Reliability tooling (Modules 7.3 and 10.2): loop detection, retries, timeouts,
and failure-rate measurement.

    LoopDetector(max_repeats=3, max_steps=10).record(action, detail) -> str | None
    with_retry(fn, attempts=3, backoff_s=0.0)
    call_with_timeout(fn, timeout_s)
    measure_reliability(agent_fn, inputs, runs=5) -> ReliabilityReport
"""

from __future__ import annotations

import concurrent.futures
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


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


def detect_tool_loop(tool_calls: list[dict], max_repeats: int = 3) -> str | None:
    """Check an agent result's tool_calls for N identical consecutive calls."""
    det = LoopDetector(max_repeats=max_repeats, max_steps=10_000)
    for tc in tool_calls:
        reason = det.record(tc["tool"], repr(sorted(tc.get("arguments", {}).items())))
        if reason:
            return reason
    return None


def with_retry(fn: Callable[[], Any], attempts: int = 3, backoff_s: float = 0.0,
               retry_on: tuple[type[BaseException], ...] = (Exception,)) -> tuple[Any, int]:
    """Call fn until it succeeds. Returns (result, retries_used). Re-raises after the last attempt."""
    for i in range(attempts):
        try:
            return fn(), i
        except retry_on:
            if i == attempts - 1:
                raise
            if backoff_s:
                time.sleep(backoff_s * (2**i))
    raise RuntimeError("unreachable")


def call_with_timeout(fn: Callable[[], Any], timeout_s: float) -> Any:
    """Run fn in a worker thread; raise TimeoutError if it takes longer than timeout_s."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(fn)
        try:
            return future.result(timeout=timeout_s)
        except concurrent.futures.TimeoutError as exc:
            raise TimeoutError(f"agent call exceeded {timeout_s}s") from exc


@dataclass
class ReliabilityReport:
    runs: int
    failures: int
    loops: int
    consistency: float  # share of inputs whose tool sequence was identical across runs
    details: list[dict] = field(default_factory=list)

    @property
    def failure_rate(self) -> float:
        return self.failures / self.runs if self.runs else 0.0


def measure_reliability(agent_fn: Callable[[str], dict], inputs: list[str], runs: int = 5,
                        is_failure: Callable[[dict], bool] | None = None) -> ReliabilityReport:
    """Run each input `runs` times; count failures, loops and tool-sequence consistency."""
    is_failure = is_failure or (lambda r: not r.get("response"))
    failures = loops = consistent = 0
    details = []
    for text in inputs:
        sequences = []
        for _ in range(runs):
            try:
                r = agent_fn(text)
            except Exception as exc:  # noqa: BLE001 - we are counting failures
                failures += 1
                details.append({"input": text, "error": repr(exc)})
                continue
            if is_failure(r):
                failures += 1
            if detect_tool_loop(r.get("tool_calls", [])):
                loops += 1
            sequences.append(tuple(tc["tool"] for tc in r.get("tool_calls", [])))
        if sequences and len(set(sequences)) == 1:
            consistent += 1
        details.append({"input": text, "distinct_tool_sequences": len(set(sequences))})
    return ReliabilityReport(runs=len(inputs) * runs, failures=failures, loops=loops,
                             consistency=consistent / len(inputs) if inputs else 0.0, details=details)
