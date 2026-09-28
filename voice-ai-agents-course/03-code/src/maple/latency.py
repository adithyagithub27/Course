"""Latency budgets, percentiles and budget-violation reports.

Lectures: 1.4 (the latency budget), 9.8 (latency testing), 10.1 and 10.5 (what to measure).

A voice turn is only as fast as its slowest stage. We track four stages from
LiveKit's metrics plus an estimated voice-to-voice total:

===============  ==================================================  =========================
Stage            Meaning                                             LiveKit metric field
===============  ==================================================  =========================
``eou_delay``    end of user speech -> turn declared complete        ``eou_metrics.end_of_utterance_delay``
``stt_final``    end of user speech -> final transcript              ``eou_metrics.transcription_delay``
``llm_ttft``     LLM request -> first token                          ``llm_metrics.ttft``
``tts_ttfb``     first text -> first audio byte                      ``tts_metrics.ttfb``
``voice_to_voice`` eou_delay + llm_ttft + tts_ttfb for one turn      (joined on ``speech_id``)
===============  ==================================================  =========================

Percentiles use linear interpolation between closest ranks, the same method
as ``numpy.percentile``'s default, implemented without numpy.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

STAGES = ("eou_delay", "stt_final", "llm_ttft", "tts_ttfb", "voice_to_voice")


@dataclass(frozen=True)
class LatencyBudget:
    """Per-stage budget in milliseconds, checked at ``percentile``.

    The defaults target a sub-1.5-second p95 voice-to-voice time for a
    cascaded pipeline on a phone call, with the median closer to 800 ms.
    Tighten them as your stack improves.
    """

    eou_delay: float = 700.0
    stt_final: float = 500.0
    llm_ttft: float = 700.0
    tts_ttfb: float = 300.0
    voice_to_voice: float = 1600.0
    percentile: float = 95.0

    def as_dict(self) -> dict[str, float]:
        """Return ``{stage: budget_ms}`` for every stage."""
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "percentile"}


@dataclass(frozen=True)
class Stats:
    """Summary statistics in milliseconds."""

    count: int
    mean: float
    p50: float
    p90: float
    p95: float
    max: float


@dataclass(frozen=True)
class Violation:
    """A stage whose percentile exceeded its budget."""

    stage: str
    percentile: float
    observed_ms: float
    budget_ms: float

    @property
    def over_by_ms(self) -> float:
        """How far over budget the stage is."""
        return self.observed_ms - self.budget_ms

    def __str__(self) -> str:
        return (
            f"{self.stage}: p{self.percentile:g}={self.observed_ms:.0f} ms "
            f"exceeds budget {self.budget_ms:.0f} ms by {self.over_by_ms:.0f} ms"
        )


def percentile(values: Sequence[float], p: float) -> float:
    """Return the ``p``-th percentile (0-100) with linear interpolation.

    Raises:
        ValueError: If ``values`` is empty or ``p`` is outside 0-100.
    """
    if not values:
        raise ValueError("percentile() of empty sequence")
    if not 0 <= p <= 100:
        raise ValueError(f"p must be between 0 and 100, got {p}")
    ordered = sorted(values)
    rank = (len(ordered) - 1) * p / 100.0
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return float(ordered[low])
    fraction = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction


def summarize(values: Sequence[float]) -> Stats:
    """Return count, mean, p50, p90, p95 and max of ``values`` (milliseconds)."""
    if not values:
        raise ValueError("summarize() needs at least one value")
    return Stats(
        count=len(values),
        mean=sum(values) / len(values),
        p50=percentile(values, 50),
        p90=percentile(values, 90),
        p95=percentile(values, 95),
        max=float(max(values)),
    )


def check_budget(
    samples: Mapping[str, Sequence[float]],
    budget: LatencyBudget | None = None,
) -> list[Violation]:
    """Compare each stage's percentile with its budget.

    Stages without samples are skipped. Returns an empty list when everything
    is within budget.
    """
    budget = budget or LatencyBudget()
    violations: list[Violation] = []
    for stage, limit in budget.as_dict().items():
        values = samples.get(stage)
        if not values:
            continue
        observed = percentile(values, budget.percentile)
        if observed > limit:
            violations.append(Violation(stage, budget.percentile, observed, limit))
    return violations


def samples_from_metrics(records: Iterable[Mapping[str, Any]]) -> dict[str, list[float]]:
    """Turn exported LiveKit metrics records into per-stage samples in milliseconds.

    Each record is a dict as written by ``agents/s10_observed_agent.py``
    (``metrics.model_dump()`` plus an optional ``"type"`` field). Values in the
    records are seconds; the output is milliseconds. ``voice_to_voice`` is
    computed for every ``speech_id`` that has EOU, LLM and TTS records.
    Negative sentinel values (LiveKit uses -1 for "not measured") are skipped.
    """
    samples: dict[str, list[float]] = defaultdict(list)
    per_turn: dict[str, dict[str, float]] = defaultdict(dict)

    def keep(stage: str, seconds: Any, speech_id: Any) -> None:
        if seconds is None:
            return
        value = float(seconds)
        if value < 0:
            return
        ms = value * 1000.0
        samples[stage].append(ms)
        if speech_id and stage in ("eou_delay", "llm_ttft", "tts_ttfb"):
            per_turn[str(speech_id)].setdefault(stage, ms)

    for record in records:
        kind = record.get("type")
        speech_id = record.get("speech_id")
        if kind == "eou_metrics":
            keep("eou_delay", record.get("end_of_utterance_delay"), speech_id)
            keep("stt_final", record.get("transcription_delay"), speech_id)
        elif kind == "llm_metrics":
            keep("llm_ttft", record.get("ttft"), speech_id)
        elif kind == "tts_metrics":
            keep("tts_ttfb", record.get("ttfb"), speech_id)
        elif kind == "realtime_model_metrics":
            keep("llm_ttft", record.get("ttft"), speech_id)

    for stages in per_turn.values():
        if {"eou_delay", "llm_ttft", "tts_ttfb"} <= stages.keys():
            samples["voice_to_voice"].append(stages["eou_delay"] + stages["llm_ttft"] + stages["tts_ttfb"])
    return dict(samples)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSON-lines file, skipping blank lines."""
    records: list[dict[str, Any]] = []
    with Path(path).open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return records


def format_report(samples: Mapping[str, Sequence[float]], budget: LatencyBudget | None = None) -> str:
    """Return a fixed-width table of p50/p90/p95 per stage against the budget."""
    budget = budget or LatencyBudget()
    limits = budget.as_dict()
    header = f"{'stage':<16}{'n':>5}{'p50':>9}{'p90':>9}{'p95':>9}{'budget':>9}  status"
    lines = [header, "-" * len(header)]
    for stage in STAGES:
        values = samples.get(stage)
        if not values:
            continue
        s = summarize(values)
        observed = percentile(values, budget.percentile)
        status = "OK" if observed <= limits[stage] else "OVER"
        lines.append(
            f"{stage:<16}{s.count:>5}{s.p50:>9.0f}{s.p90:>9.0f}{s.p95:>9.0f}{limits[stage]:>9.0f}  {status}"
        )
    return "\n".join(lines)
