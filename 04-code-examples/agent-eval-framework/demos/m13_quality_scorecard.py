"""Lecture 13.3 - The one-page quality scorecard for leadership: three agents,
five dimensions, traffic lights, trends, cost. The support agent's row uses
this run's offline evaluation; the other rows are illustrative inputs.

    uv run python demos/m13_quality_scorecard.py     # writes reports/results/scorecard.md
"""
from _common import banner

import copy

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import default_metrics_for, run_suite
from evaluators.golden import load
from monitoring.scorecard import EXAMPLE_AGENTS, build_scorecard, render_markdown
from reports.experiments import RESULTS

banner("Lecture 13.3 - leadership scorecard")
agents = copy.deepcopy(EXAMPLE_AGENTS)
r = run_suite(load("golden_support"), run_support_agent, default_metrics_for)
a = r["averages"]
agents[0]["this_week"].update({"correctness": a["Answer Correctness"], "faithfulness": a["Faithfulness"], "relevance": a["Answer Relevancy"]})
md = render_markdown(build_scorecard(agents, week="2026-09-28"))
(RESULTS / "scorecard.md").write_text(md + "\n")
print(md)
print("\nOperations Agent is RED on safety: open the red-team report before the next release.")
