"""
Leadership quality scorecard (Module 13.3): one page, three agents,
traffic lights, trend arrows, cost and business impact.

    card = build_scorecard(agent_snapshots)
    print(render_markdown(card))

Input per agent: this week's and last week's metric averages, cost per task,
volume, escalation rate. The five quality dimensions (T3) are the rows.
"""

from __future__ import annotations

from datetime import date

from config.thresholds import DIMENSIONS

GREEN, AMBER, RED = "GREEN", "AMBER", "RED"


def light(value: float, target: float, amber_margin: float = 0.05) -> str:
    if value >= target:
        return GREEN
    return AMBER if value >= target - amber_margin else RED


def arrow(now: float, before: float, eps: float = 0.01) -> str:
    return "up" if now > before + eps else "down" if now < before - eps else "flat"


TARGETS = {"correctness": 0.85, "faithfulness": 0.85, "relevance": 0.80, "safety": 0.95, "reliability": 0.90}


def build_scorecard(agents: list[dict], week: str | None = None) -> dict:
    rows = []
    for a in agents:
        dims = {}
        for d in DIMENSIONS:
            now, before = a["this_week"][d], a["last_week"][d]
            dims[d] = {"value": now, "light": light(now, TARGETS[d]), "trend": arrow(now, before)}
        lights = [v["light"] for v in dims.values()]
        overall = RED if RED in lights else AMBER if AMBER in lights else GREEN
        rows.append({
            "agent": a["name"], "overall": overall, "dimensions": dims,
            "cost_per_task_usd": a["cost_per_task_usd"], "tasks_per_week": a["tasks_per_week"],
            "weekly_cost_usd": round(a["cost_per_task_usd"] * a["tasks_per_week"], 2),
            "escalation_rate": a["escalation_rate"],
        })
    return {"week": week or date.today().isoformat(), "agents": rows}


def render_markdown(card: dict) -> str:
    sym = {GREEN: "[G]", AMBER: "[A]", RED: "[R]"}
    arr = {"up": "^", "down": "v", "flat": "="}
    lines = [f"# Agent Quality Scorecard - week of {card['week']}", "",
             "| Agent | Overall | " + " | ".join(d.capitalize() for d in DIMENSIONS) + " | Cost/task | Weekly cost | Escalations |",
             "|---|---|" + "---|" * len(DIMENSIONS) + "---|---|---|"]
    for r in card["agents"]:
        cells = [f"{sym[v['light']]} {v['value']:.2f} {arr[v['trend']]}" for v in r["dimensions"].values()]
        lines.append(f"| {r['agent']} | {sym[r['overall']]} | " + " | ".join(cells)
                     + f" | ${r['cost_per_task_usd']:.4f} | ${r['weekly_cost_usd']:,.2f} | {r['escalation_rate']:.0%} |")
    lines += ["", "[G] on target  [A] within 5 points  [R] action needed   ^ improving  v declining  = flat",
              "Costs use list prices (verify current pricing)."]
    return "\n".join(lines)


# Example input for the demo: the three course agents. Values are illustrative
# except where the demo replaces them with a real offline run.
EXAMPLE_AGENTS = [
    {"name": "TechCorp Support", "tasks_per_week": 35000, "cost_per_task_usd": 0.0008, "escalation_rate": 0.06,
     "this_week": {"correctness": 0.93, "faithfulness": 0.91, "relevance": 0.90, "safety": 0.99, "reliability": 0.95},
     "last_week": {"correctness": 0.92, "faithfulness": 0.93, "relevance": 0.90, "safety": 0.99, "reliability": 0.94}},
    {"name": "Policy Assistant (RAG)", "tasks_per_week": 4200, "cost_per_task_usd": 0.0006, "escalation_rate": 0.02,
     "this_week": {"correctness": 0.84, "faithfulness": 0.93, "relevance": 0.87, "safety": 0.98, "reliability": 0.93},
     "last_week": {"correctness": 0.86, "faithfulness": 0.94, "relevance": 0.88, "safety": 0.98, "reliability": 0.93}},
    {"name": "Operations Agent", "tasks_per_week": 1500, "cost_per_task_usd": 0.0012, "escalation_rate": 0.0,
     "this_week": {"correctness": 0.88, "faithfulness": 0.90, "relevance": 0.85, "safety": 0.89, "reliability": 0.91},
     "last_week": {"correctness": 0.87, "faithfulness": 0.90, "relevance": 0.84, "safety": 0.96, "reliability": 0.92}},
]
