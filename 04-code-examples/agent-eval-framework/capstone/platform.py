"""
Enterprise Agent Quality Platform (Module 14, Project 5).

One harness, any agent, five stages, one gate:

    Agent under test -> functional evals -> security (red team) -> performance
    -> regression vs baseline -> observability sample -> report + quality gate

    platform = QualityPlatform()
    result = platform.run("support")        # dict with every stage's numbers
    print(platform.render_report(result))   # markdown quality report

Agents are registered by name; each must return the common result dict
(response, tool_calls, total_tokens, llm_calls, latency_s).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from agents.banking_agent import run_banking_agent
from agents.support_agent import run_support_agent
from config.thresholds import gates, load_thresholds
from evaluators import metrics as M
from evaluators.deepeval_suite import run_suite
from evaluators.golden import load
from performance.benchmark import run_benchmark
from regression.regression_suite import BASELINE_DIR, compare, load_baseline
from security.redteam import run_redteam


def capstone_metrics(case: dict) -> list:
    """Project 5: four metrics on the 20-case golden dataset."""
    ms = [M.answer_relevancy(), M.correctness(), M.tool_correctness()]
    if case.get("context"):
        ms.insert(1, M.faithfulness())
    return ms


@dataclass
class AgentConfig:
    name: str
    fn: Callable[[str], dict]
    golden: str
    redteam: str
    forbidden_tools: set[str] = field(default_factory=set)
    baseline: str | None = None
    benchmark_queries: list[str] = field(default_factory=list)


class QualityPlatform:
    def __init__(self) -> None:
        self.agents: dict[str, AgentConfig] = {}
        self.register(AgentConfig(
            "support", run_support_agent, "golden_capstone", "redteam_support",
            forbidden_tools={"lookup_customer", "send_email", "create_ticket"}, baseline="support_capstone_v1",
            benchmark_queries=[c["input"] for c in load("golden_capstone")],
        ))
        self.register(AgentConfig(
            "banking_v2", lambda m: run_banking_agent(m, hardened=True), "", "redteam_banking",
            forbidden_tools={"transfer_funds"},
        ))

    def register(self, cfg: AgentConfig) -> None:
        self.agents[cfg.name] = cfg

    # ---- stages --------------------------------------------------------------
    def functional(self, cfg: AgentConfig) -> dict:
        return run_suite(load(cfg.golden), cfg.fn, capstone_metrics) if cfg.golden else {}

    def security(self, cfg: AgentConfig) -> dict:
        own = {"ACC-1001-CHK", "ACC-1001-SAV"} if cfg.name.startswith("banking") else set()
        return run_redteam(load(cfg.redteam), cfg.fn, cfg.forbidden_tools, own)

    def performance(self, cfg: AgentConfig) -> dict:
        return run_benchmark(cfg.benchmark_queries, agent_fn=cfg.fn).summary() if cfg.benchmark_queries else {}

    def regression(self, cfg: AgentConfig, functional: dict) -> dict | None:
        if not cfg.baseline or not (BASELINE_DIR / f"{cfg.baseline}.json").exists():
            return None
        return compare(load_baseline(cfg.baseline), functional)

    # ---- run -----------------------------------------------------------------
    def run(self, name: str) -> dict:
        cfg = self.agents[name]
        functional = self.functional(cfg)
        security = self.security(cfg)
        performance = self.performance(cfg)
        regression = self.regression(cfg, functional) if functional else None
        result = {"agent": name, "functional": functional, "security": security, "performance": performance, "regression": regression}
        result["gate"] = self.gate(result)
        return result

    def gate(self, r: dict) -> dict:
        g, t = gates(), load_thresholds()
        reasons = []
        f = r["functional"]
        if f and f["pass_rate"] < g["pr_pass_rate"]:
            reasons.append(f"functional pass rate {f['pass_rate']:.0%} < {g['pr_pass_rate']:.0%}")
        s = r["security"]
        if s["passed"] / s["total"] < t["redteam_pass_rate"]:
            reasons.append(f"red team: {s['total'] - s['passed']} open finding(s)")
        p = r["performance"]
        if p and p["latency_p95_s"] > t["max_p95_latency_s"]:
            reasons.append(f"p95 latency {p['latency_p95_s']}s > {t['max_p95_latency_s']}s")
        if p and p["avg_cost_usd"] > t["max_cost_per_task_usd"]:
            reasons.append(f"cost/task ${p['avg_cost_usd']} > ${t['max_cost_per_task_usd']}")
        if r["regression"] and r["regression"]["regression"]:
            reasons.append("regression vs baseline")
        return {"ship": not reasons, "reasons": reasons}

    @staticmethod
    def render_report(r: dict) -> str:
        lines = [f"# Agent Quality Report: {r['agent']}", "", f"**Decision:** {'SHIP' if r['gate']['ship'] else 'BLOCK'}", ""]
        f = r["functional"]
        if f:
            lines += ["## Functional evaluation", f"{f['passed']}/{f['total']} golden cases passed ({f['pass_rate']:.0%})", "",
                      "| Metric | Average |", "|---|---|"] + [f"| {m} | {v:.2f} |" for m, v in sorted(f["averages"].items()) if v is not None] + [""]
        s = r["security"]
        lines += ["## Security", f"{s['passed']}/{s['total']} attacks blocked. Open findings by severity: {s['by_severity']}", ""]
        lines += [f"- {x['id']} ({x['severity']}): {'; '.join(x['reasons'])}" for x in s["findings"]]
        p = r["performance"]
        if p:
            lines += ["", "## Performance (offline latencies are simulated)",
                      f"p50 {p['latency_p50_s']}s, p95 {p['latency_p95_s']}s, avg {p['avg_llm_calls']} LLM calls, "
                      f"${p['avg_cost_usd']:.6f}/task (${p['cost_per_1k_tasks_usd']}/1k tasks, verify current pricing)"]
        if r["regression"]:
            lines += ["", "## Regression vs baseline", f"Regression: {'YES' if r['regression']['regression'] else 'no'}"]
        if r["gate"]["reasons"]:
            lines += ["", "## Blocking issues"] + [f"- {x}" for x in r["gate"]["reasons"]]
        return "\n".join(lines) + "\n"
