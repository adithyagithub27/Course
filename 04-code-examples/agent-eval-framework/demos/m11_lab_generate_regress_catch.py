"""Lab 11.1 - Generate, baseline, regress, catch, fix: synthetic goldens from
the knowledge base, a baseline run, a broken prompt, detection, and recovery.

    uv run python demos/m11_lab_generate_regress_catch.py
"""
from _common import banner

from agents.support_agent import run_support_agent
from evaluators.deepeval_suite import run_suite
from evaluators.metrics import answer_relevancy, faithfulness
from regression.regression_suite import PROMPT_V2_REGRESSED
from regression.synthetic_data import from_knowledge_base

banner("Lab 11.1 - generate, baseline, regress, catch", ["openai", "deepeval"])
goldens = from_knowledge_base(per_context=2)
cases = [{"id": f"SYN-{i:02d}", "input": g.input, "context": g.context, "category": "synthetic"} for i, g in enumerate(goldens, 1)]
print(f"1. Generated {len(cases)} synthetic cases from {len(cases) // 2} knowledge-base articles")
metrics = lambda c: [answer_relevancy(), faithfulness()]  # noqa: E731
agent_v1 = lambda q: run_support_agent(q, temperature=0)  # noqa: E731
agent_v2 = lambda q: run_support_agent(q, temperature=0, system_prompt=PROMPT_V2_REGRESSED)  # noqa: E731
base = run_suite(cases, agent_v1, metrics)
print(f"2. Baseline:   pass rate {base['pass_rate']:.0%}  {base['averages']}")
bad = run_suite(cases, agent_v2, metrics)
print(f"3. Regressed:  pass rate {bad['pass_rate']:.0%}  {bad['averages']}")
drop = base["averages"]["Faithfulness"] - bad["averages"]["Faithfulness"]
print(f"4. Detected:   faithfulness dropped {drop:.2f} -> {'REGRESSION' if drop > 0.05 else 'no regression'}")
fixed = run_suite(cases, agent_v1, metrics)
print(f"5. Fixed:      pass rate {fixed['pass_rate']:.0%}  back to baseline: {fixed['averages'] == base['averages']}")
