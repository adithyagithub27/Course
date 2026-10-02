"""Project 2 / Lecture 5.4 - Evaluate the enterprise RAG agent: 15 golden
questions (5 per policy domain), RAGAS metrics, per-domain diagnosis.

    uv run python demos/m05_project2_rag_eval.py   # writes reports/results/project2_report.md
"""
from _common import banner, table

from agents.rag_agent import run_rag_agent
from evaluators.golden import load
from evaluators.ragas_suite import aggregate, build_dataset, diagnose, evaluate_dataset, to_sample
from reports.experiments import RESULTS

banner("Project 2 - enterprise RAG evaluation", ["openai", "ragas"])
cases = load("golden_rag")
rows = evaluate_dataset(build_dataset([to_sample(c["question"], run_rag_agent(c["question"]), c["reference"]) for c in cases]))
table([{"id": c["id"], **r, "diagnosis": diagnose(r)} for c, r in zip(cases, rows, strict=True)])
lines = ["# Project 2 - RAG diagnostic report", "", "| Domain | faithfulness | answer_relevancy | context_precision | context_recall | diagnosis |", "|---|---|---|---|---|---|"]
for dom in ("hr", "it_security", "travel_expense"):
    agg = aggregate([r for c, r in zip(cases, rows, strict=True) if c["domain"] == dom])
    lines.append(f"| {dom} | {agg['faithfulness']} | {agg['answer_relevancy']} | {agg['context_precision']} | {agg['context_recall']} | {diagnose(agg)} |")
md = "\n".join(lines) + "\n"
(RESULTS / "project2_report.md").parent.mkdir(parents=True, exist_ok=True)
(RESULTS / "project2_report.md").write_text(md)
print("\n" + md)
print(f"Overall: {aggregate(rows)}")
