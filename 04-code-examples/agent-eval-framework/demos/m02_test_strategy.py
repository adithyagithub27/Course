"""Lecture 2.3 - The five-layer agent eval pyramid (decision T4), mapped to this repo.

    uv run python demos/m02_test_strategy.py
"""
from _common import ROOT, banner

banner("Lecture 2.3 - test strategy: the agent eval pyramid")
LAYERS = [
    ("1 unit evals", "tests/unit", "deterministic checks on tools, parsers, guards", "every commit, ~free"),
    ("2 component evals", "tests/component", "one piece at a time: retriever, generator, judge, MCP contract", "every commit, cents"),
    ("3 trajectory evals", "tests/trajectory", "the agent's steps: tool choice, arguments, order, loops", "every PR"),
    ("4 end-to-end evals", "tests/e2e", "golden datasets scored by LLM-judge metrics; red team", "every PR / nightly"),
    ("5 production monitoring", "tests/production", "drift, scorecards, audit trail on live traffic", "continuous"),
]
for name, folder, what, when in LAYERS:
    files = sorted((ROOT / folder).glob("test_*.py"))
    print(f"{name:<24} {folder:<18} {len(files):>2} files  {when}")
    print(f"{'':<24} {what}")
    for f in files:
        print(f"{'':<27}- {f.name}")
