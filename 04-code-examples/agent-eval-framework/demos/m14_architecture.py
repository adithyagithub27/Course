"""Lecture 14.1 - Capstone architecture: the platform's stages and registered agents.

    uv run python demos/m14_architecture.py
"""
from _common import banner

from capstone.platform import QualityPlatform
from config.thresholds import gates, load_thresholds

banner("Lecture 14.1 - capstone architecture", ["openai", "deepeval", "ragas", "langfuse"])
print("Agent under test -> Test harness -> [functional -> security -> performance -> regression]")
print("                 -> Results store (reports/results) -> Dashboard -> CI/CD gate\n")
p = QualityPlatform()
for name, cfg in p.agents.items():
    print(f"agent '{name}': golden={cfg.golden or '-'} redteam={cfg.redteam} forbidden_tools={sorted(cfg.forbidden_tools)} baseline={cfg.baseline}")
t = load_thresholds()
print(f"\nGates: {gates()}")
print(f"Reliability limits: p95 <= {t['max_p95_latency_s']}s, cost <= ${t['max_cost_per_task_usd']}/task, red team pass rate {t['redteam_pass_rate']:.0%}")
