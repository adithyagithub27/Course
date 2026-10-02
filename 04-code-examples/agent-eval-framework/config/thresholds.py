"""
Thresholds from config/eval_config.yaml, flattened to {metric: threshold}.

    from config.thresholds import load_thresholds, check_threshold, DIMENSIONS
    check_threshold("faithfulness", 0.84)  # {'metric': ..., 'passed': True, ...}

Environment overrides: EVAL_THRESHOLD_<METRIC>=0.75
Metrics whose name starts with "max_" are lower-is-better.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).parent / "eval_config.yaml"

# The five quality dimensions (decision T3), in teaching order.
DIMENSIONS = ["correctness", "faithfulness", "relevance", "safety", "reliability"]


@lru_cache(maxsize=4)
def load_config(path: str | None = None) -> dict:
    return yaml.safe_load(Path(path or CONFIG_PATH).read_text())


def load_thresholds(path: str | None = None) -> dict[str, float]:
    cfg = load_config(path)
    out: dict[str, float] = {}
    for dim in cfg["dimensions"].values():
        out.update(dim["metrics"])
    for key in list(out):
        env = os.getenv(f"EVAL_THRESHOLD_{key.upper()}")
        if env is not None:
            out[key] = float(env)
    return out


def metric_dimension(metric: str) -> str | None:
    for name, dim in load_config()["dimensions"].items():
        if metric in dim["metrics"]:
            return name
    return None


def gates() -> dict[str, float]:
    return dict(load_config()["gates"])


def check_threshold(metric: str, score: float, thresholds: dict | None = None) -> dict:
    thresholds = thresholds or load_thresholds()
    threshold = thresholds.get(metric)
    if threshold is None:
        return {"metric": metric, "score": score, "threshold": None, "passed": True, "note": "no threshold"}
    lower_is_better = metric.startswith("max_")
    passed = score <= threshold if lower_is_better else score >= threshold
    return {"metric": metric, "score": score, "threshold": threshold, "passed": passed, "lower_is_better": lower_is_better}
