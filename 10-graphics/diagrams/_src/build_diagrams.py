#!/usr/bin/env python3
"""Course 2 (AI Agent Testing & Evaluation) master diagrams D1-D16.

Sources: 01-curriculum/full-curriculum.md "Visual Requirements" tables, with the frozen taxonomies in
14-quality-review/2026-10-01-fix-plan.md: T2 six failure modes, T3 five quality dimensions, T4 five-layer
agent eval pyramid, T1 TechCorp support agent (five tools in
04-code-examples/agent-eval-framework/agents/support_agent.py), A8 models (gpt-4.1-mini agent, gpt-4.1 judge).
Course 2 has no slide-deck-outline yet, so the D-numbers below are defined here and listed in ../README.md.

Run:   python 10-graphics/diagrams/_src/build_diagrams.py [--no-render]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
TOOLS = HERE.parents[2] / "voice-ai-agents-course" / "09-production" / "tools"
sys.path.insert(0, str(TOOLS))

from diagram_kit import (AMBER, FLOW, GRAY, GRAY_DARK, GRAY_LIGHT, NAVY, NAVY_LIGHT, NAVY_MID,  # noqa: E402
                         RED, TEAL, TEAL_DIM, WHITE, Diagram)

COURSE = "Course 2 · Agent Testing & Evaluation"
TOOLS_5 = ["lookup_customer", "search_knowledge_base", "create_ticket", "send_email", "escalate_to_human"]


def D(did, slug, title, lectures, keywords, **kw) -> Diagram:
    return Diagram(did, slug, title, course=COURSE, lectures=lectures, keywords=keywords, **kw)


# ----------------------------------------------------------------------------------------------
def d1() -> Diagram:
    d = D("D1", "six-failure-modes", "The six ways agents fail", ["1.4", "0.1", "2.3"],
          ["six ways", "6 ways", "failure modes", "ways agents fail"])
    modes = [("Hallucination", "states facts it never retrieved", "high", "warning"),
             ("Wrong tool selection", "calls the wrong tool, or none", "high", "wrench"),
             ("Incorrect tool arguments", "right tool, wrong order ID", "critical", "wrench"),
             ("Reasoning errors", "bad plan from good inputs", "medium", "brain"),
             ("Goal drift", "solves a different problem", "medium", "skull"),
             ("Infinite loops", "repeats steps, burns tokens", "high", "loop")]
    cw, ch, gx, gy = 540, 330, 54, 40
    for i, (name, sub, sev, icon) in enumerate(modes):
        with d.step(i + 1, name.lower(), [name.lower()]):
            x = 96 + (i % 3) * (cw + gx)
            y = 240 + (i // 3) * (ch + gy)
            d.rect(x, y, cw, ch, stroke=RED, fill=NAVY_LIGHT)
            d.icon(icon if icon != "skull" else "eye", x + 70, y + 80, 64, RED)
            d.fail_dot(x + cw - 44, y + 44, r=16)
            d.text(x + 40, y + 180, name, 30, 700, WHITE)
            d.text(x + 40, y + 222, sub, 22, 400, GRAY_LIGHT)
            color = RED if sev == "critical" else AMBER if sev == "high" else GRAY
            filled = {"critical": 3, "high": 2, "medium": 1}[sev]
            d.label(x + 40, y + 284, "severity", 16, GRAY)
            for k in range(3):
                d.add(f'<rect x="{x + 140 + k * 34}" y="{y + 268}" width="26" height="20" rx="4" '
                      f'fill="{color if k < filled else NAVY_MID}" stroke="{color}" stroke-width="2"/>')
            d.text(x + 260, y + 284, sev, 18, 600, color)
    return d


def d2() -> Diagram:
    d = D("D2", "deterministic-vs-non-deterministic", "Same input, different outputs", ["2.1"],
          ["deterministic", "non-deterministic", "paradigm shift"])
    with d.step(1, "deterministic"):
        d.label(96, 290, "Traditional software", 20, GRAY)
        d.node(96, 470, 220, 120, "Input", tone="white")
        d.node(420, 470, 220, 120, "f(x)", tone="neutral", mono=True, size=30)
        d.node(744, 470, 220, 120, "Same output", "every time", tone="teal")
        d.arrow(320, 530, 416, 530)
        d.arrow(644, 530, 740, 530)
        d.chip(96, 700, "assert output == expected", "teal", size=18)
        d.pass_dot(470, 718, r=14)
    with d.step(2, "non-deterministic"):
        d.line(1040, 250, 1040, 980, color=GRAY_DARK, sw=2, dash="6 8", arrow=False)
        d.label(1110, 290, "AI agent", 20, GRAY)
        d.node(1110, 470, 200, 120, "Input", tone="white")
        d.node(1390, 470, 200, 120, "LLM agent", tone="teal", icon="robot", icon_size=40)
        d.arrow(1314, 530, 1386, 530)
        outs = [("Output A", 300), ("Output B", 530), ("Output C", 760)]
        for lab, y in outs:
            d.node(1660, y, 164, 110, lab, tone="neutral")
            d.arrow(1594, 530, 1656, y + 55)
        d.text(1742, 920, "all may be correct", 20, 600, TEAL, "middle")
        d.chip(1110, 700, "assert output == expected", "red", size=18)
        d.fail_dot(1430, 718, r=14)
        d.chip(1110, 780, "score meaning, not strings", "teal", size=18, mono=False)
        d.pass_dot(1430, 798, r=14)
    return d


def d3() -> Diagram:
    d = D("D3", "agent-loop", "Chatbot vs agent: the loop", ["1.2", "1.3"],
          ["agent loop", "not a chatbot", "observe", "the loop"])
    with d.step(1, "chatbot"):
        d.label(96, 290, "Chatbot", 20, GRAY)
        d.node(96, 420, 220, 120, "Request", tone="white", icon="person", icon_size=36, align="left", size=22)
        d.node(500, 420, 220, 120, "Response", tone="neutral", size=22)
        d.arrow(320, 480, 496, 480, label="one call", label_dy=-16)
        d.line(860, 250, 860, 980, color=GRAY_DARK, sw=2, dash="6 8", arrow=False)
    with d.step(2, "agent loop", ["loop", "observe"]):
        d.label(940, 290, "Agent", 20, GRAY)
        cx, cy, r = 1300, 620, 230
        pts = {"Observe": (cx, cy - r), "Think": (cx + r, cy + r * 0.55), "Act": (cx - r, cy + r * 0.55)}
        for name, (x, y) in pts.items():
            d.node(x - 110, y - 50, 220, 100, name, tone="teal", size=28, glow=(name == "Think"))
        d.path(f"M{cx + 118} {cy - r + 10} Q{cx + r + 40} {cy - r + 40} {cx + r + 10} {cy + r * 0.55 - 56}",
               color=TEAL, sw=3)
        d.path(f"M{cx + r - 114} {cy + r * 0.55 + 10} Q{cx} {cy + r * 0.55 + 90} {cx - r + 114} {cy + r * 0.55 + 10}",
               color=TEAL, sw=3)
        d.path(f"M{cx - r - 10} {cy + r * 0.55 - 56} Q{cx - r - 40} {cy - r + 40} {cx - 118} {cy - r + 10}",
               color=TEAL, sw=3)
        d.icon("brain", cx, cy + 30, 72, TEAL)
        d.text(cx, cy + 100, "gpt-4.1-mini", 18, 500, GRAY, "middle", mono=True)
        ax, ay = cx - r, cy + r * 0.55
        d.node(940, 870, 460, 110, "Tools", "lookup_customer, create_ticket, …", tone="white", icon="wrench",
               align="left", sub_mono=True, size=22, sub_size=16)
        d.arrow(ax, ay + 54, ax, 866, color=FLOW)
        d.text(1560, 960, "repeat until done", 20, 600, TEAL)
    return d


def d4() -> Diagram:
    d = D("D4", "agent-eval-pyramid", "Test pyramid vs agent eval pyramid", ["2.3", "2.1", "12.1", "14.2"],
          ["pyramid", "evaluation spectrum", "eval pyramid", "test strategy"])

    def pyramid(x0, x1, bottom, layers, lh, tone, start_step):
        n = len(layers)
        inset = (x1 - x0) * 0.32 / n
        for i, (name, sub) in enumerate(layers):
            with d.step(start_step + i, name.lower(), [name.lower()]):
                yb = bottom - i * (lh + 10)
                yt = yb - lh
                l0, r0 = x0 + i * inset, x1 - i * inset
                l1, r1 = l0 + inset * lh / (lh + 10), r0 - inset * lh / (lh + 10)
                d.add(f'<path d="M{l0:.1f} {yb} L{l1:.1f} {yt} L{r1:.1f} {yt} L{r0:.1f} {yb} Z" fill="{NAVY_LIGHT}" '
                      f'stroke="{tone}" stroke-width="2" stroke-linejoin="round"/>')
                cx = (x0 + x1) / 2
                d.text(cx, yt + lh / 2 + (0 if sub else 9), name, 24, 600, WHITE, "middle")
                if sub:
                    d.text(cx, yt + lh / 2 + 28, sub, 17, 400, GRAY_LIGHT, "middle")

    with d.step(1, "traditional"):
        d.label(96, 300, "Traditional software", 20, GRAY)
    pyramid(96, 696, 960, [("Unit", None), ("Integration", None), ("End-to-end", None)], 150, GRAY, 1)
    with d.step(1):
        d.line(800, 250, 800, 980, color=GRAY_DARK, sw=2, dash="6 8", arrow=False)
        d.label(900, 250, "AI agent (the course's spectrum)", 20, TEAL)
    layers = [("Unit evals", "one prompt, one metric"), ("Component evals", "retriever, tools, judge"),
              ("Trajectory evals", "the steps it took"), ("End-to-end evals", "full task, golden dataset"),
              ("Production monitoring", "sampled live traffic")]
    pyramid(900, 1824, 990, layers, 128, TEAL, 2)
    with d.step(6, "cost and speed", ["cost"]):
        d.text(1830, 290, "slower, costlier", 16, 600, AMBER, "end")
        d.text(1830, 1020, "fast, cheap, every commit", 16, 600, TEAL, "end")
    return d


def d5() -> Diagram:
    d = D("D5", "five-dimensions-radar", "Five dimensions of agent quality", ["2.2", "13.3"],
          ["5 dimensions", "five dimensions", "dimensions of agent quality", "beyond pass/fail"],
          footnote="Illustrative profiles")
    dims = ["Correctness", "Faithfulness", "Relevance", "Safety", "Reliability"]
    cx, cy, R = 720, 640, 320

    def pt(k, v):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        return cx + R * v * math.cos(a), cy + R * v * math.sin(a)

    with d.step(1, "the axes"):
        for lvl in (0.25, 0.5, 0.75, 1.0):
            pts = " ".join(f"{pt(k, lvl)[0]:.1f},{pt(k, lvl)[1]:.1f}" for k in range(5))
            d.add(f'<polygon points="{pts}" fill="none" stroke="{GRAY_DARK}" stroke-width="{2 if lvl == 1 else 1}"/>')
        for k, name in enumerate(dims):
            x, y = pt(k, 1)
            d.line(cx, cy, x, y, color=GRAY_DARK, sw=1, arrow=False)
            lx, ly = pt(k, 1.17)
            anchor = "middle" if k == 0 else "start" if k in (1, 2) else "end"
            d.text(lx, ly + 10, name, 26, 600, WHITE, anchor)
    profiles = [("Agent A", [0.9, 0.85, 0.8, 0.95, 0.6], TEAL, 2), ("Agent B", [0.7, 0.55, 0.9, 0.6, 0.85], WHITE, 3)]
    for name, vals, color, st in profiles:
        with d.step(st, name.lower(), [name.lower()]):
            pts = " ".join(f"{pt(k, v)[0]:.1f},{pt(k, v)[1]:.1f}" for k, v in enumerate(vals))
            d.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="3"/>')
            for k, v in enumerate(vals):
                x, y = pt(k, v)
                d.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}"/>')
    with d.step(3):
        d.legend(1340, 480, [("box", TEAL, "Agent A: safe, but flaky")])
        d.legend(1340, 540, [("box", WHITE, "Agent B: reliable, ungrounded")])
        d.text(1340, 660, "One pass/fail number hides this.", 24, 600, WHITE)
        d.text(1340, 700, "Score each dimension separately.", 22, 400, GRAY_LIGHT)
    return d


def d6() -> Diagram:
    d = D("D6", "test-strategy-matrix", "Test strategy matrix", ["2.3", "14.1"],
          ["test strategy", "strategy matrix", "designing a test strategy"],
          footnote="Template: 11-course-assets/templates/")
    comps = ["LLM", "Tools", "Memory", "Planning"]
    dims = ["Correctness", "Faithfulness", "Relevance", "Safety", "Reliability"]
    cells = [["G-Eval", "Faithfulness", "Answer relevancy", "Red-team prompts", "Repeat-run variance"],
             ["Tool correctness", "Args vs schema", "Tool selection", "Permission tests", "Error injection"],
             ["Recall checks", "Grounded recall", "Context relevance", "PII retention", "Long-session tests"],
             ["Trajectory eval", "Plan vs evidence", "Goal accuracy", "Unsafe-plan tests", "Loop detection"]]
    x0, y0, cw0, cw, rh = 96, 260, 220, 302, 160
    with d.step(1):
        for j, dm in enumerate(dims):
            d.text(x0 + cw0 + j * cw + cw / 2, y0, dm, 22, 700, TEAL, "middle")
    for i, c in enumerate(comps):
        with d.step(i + 1, c.lower()):
            y = y0 + 30 + i * rh
            d.node(x0, y, cw0 - 16, rh - 16, c, tone="white", size=24)
            for j, cell in enumerate(cells[i]):
                d.node(x0 + cw0 + j * cw, y, cw - 16, rh - 16, cell, tone="neutral", size=20, weight=500)
    return d


def d7() -> Diagram:
    d = D("D7", "metric-taxonomy", "Agent quality metrics", ["4.1", "4.2"],
          ["metric taxonomy", "quality metrics", "agent-specific metrics"])
    with d.step(1, "root"):
        d.node(760, 240, 400, 90, "Agent quality metrics", tone="teal", size=26, glow=True)
    groups = [("LLM quality", 96, ["relevance", "faithfulness", "coherence", "hallucination", "bias", "toxicity"], 2),
              ("Agent behaviour", 1000, ["task completion", "tool selection", "tool arguments", "goal accuracy",
                                         "trajectory efficiency"], 3)]
    for name, gx, leaves, st in groups:
        with d.step(st, name.lower(), [name.lower()]):
            d.node(gx + 200, 420, 420, 86, name, tone="white", size=24)
            d.elbow([(960, 334), (960, 375), (gx + 410, 375), (gx + 410, 416)], color=FLOW)
            for k, leaf in enumerate(leaves):
                y = 560 + k * 76
                d.node(gx + 300, y, 380, 60, leaf, tone="neutral", size=20, weight=500)
                d.elbow([(gx + 240, 510), (gx + 240, y + 30), (gx + 296, y + 30)], color=GRAY, sw=1.5, arrow=False)
    return d


def d8() -> Diagram:
    d = D("D8", "llm-as-judge", "LLM-as-judge", ["4.3", "4.4"],
          ["llm-as-judge", "judge", "g-eval", "grade another"])
    with d.step(1, "inputs"):
        d.node(96, 300, 400, 120, "Agent output", "actual_output", tone="white", sub_mono=True)
        d.node(96, 480, 400, 120, "Rubric", "criteria + evaluation steps", tone="white")
        d.node(96, 660, 400, 120, "Context", "input, retrieval_context", tone="neutral", sub_mono=True)
    with d.step(2, "judge"):
        d.node(700, 420, 440, 240, "Judge LLM", "gpt-4.1", tone="teal", icon="clipboard", glow=True, size=30,
               sub_mono=True)
        for y in (360, 540, 720):
            d.elbow([(500, y), (600, y), (600, 540), (696, 540)], color=FLOW)
    with d.step(3, "structured scores"):
        d.node(1340, 330, 484, 150, "Score", "0.0 to 1.0, vs threshold", tone="teal", icon="bars")
        d.node(1340, 560, 484, 150, "Reasoning", "why it scored that", tone="white", icon="doc")
        d.arrow(1144, 500, 1336, 405, color=TEAL)
        d.arrow(1144, 580, 1336, 635, color=FLOW)
    with d.step(4, "calibration", ["calibration", "calibrate"]):
        d.elbow([(1580, 714), (1580, 880), (920, 880), (920, 664)], color=AMBER, dash="8 4")
        d.text(1250, 920, "calibrate against human labels", 20, 600, AMBER, "middle")
    return d


def d9() -> Diagram:
    d = D("D9", "rag-retrieval-vs-generation", "RAG: retrieval or generation?", ["5.1", "5.2", "5.3"],
          ["retrieval vs", "rag quality problem", "rag pipeline", "evaluating retrieval"])
    y = 300
    with d.step(1, "the pipeline"):
        d.label(96, y - 24, "Retrieval", 18, GRAY)
        d.label(1050, y - 24, "Generation", 18, TEAL)
        nodes = [(96, "Query", "white", None), (316, "Embed", "neutral", None), (536, "Vector store", "neutral", None),
                 (776, "Top-k chunks", "neutral", None), (1050, "LLM + prompt", "teal", "brain"),
                 (1320, "Answer", "white", None)]
        widths = [190, 190, 210, 220, 240, 190]
        for (x, lab, tone, ic), w in zip(nodes, widths):
            d.node(x, y, w, 110, lab, tone=tone, size=22)
        for (x, *_), w, (nx, *_) in zip(nodes, widths, nodes[1:]):
            d.arrow(x + w + 4, y + 55, nx - 4, y + 55, color=GRAY if nx < 1050 else TEAL)
        d.rect(86, y - 50, 940, 180, stroke=GRAY, fill="none", dash="8 4")
        d.rect(1040, y - 50, 490, 180, stroke=TEAL, fill="none", dash="8 4")
    with d.step(2, "which half failed?", ["wrong answer", "decision", "failure"]):
        d.node(560, 560, 800, 100, "The RAG agent gave a wrong answer", tone="red", size=24)
        d.node(660, 720, 600, 90, "Were the right documents retrieved?", tone="neutral", size=22)
        d.arrow(960, 664, 960, 716)
        d.node(220, 870, 640, 120, "No: retrieval failure", "context precision / recall", tone="neutral", size=24)
        d.node(1060, 870, 640, 120, "Yes: generation failure", "faithfulness, answer relevancy", tone="teal", size=24)
        d.elbow([(660, 765), (540, 765), (540, 866)])
        d.elbow([(1260, 765), (1380, 765), (1380, 866)], color=TEAL)
        d.text(520, 755, "no", 18, 600, GRAY, "end")
        d.text(1400, 755, "yes", 18, 600, TEAL)
    return d


def d10() -> Diagram:
    d = D("D10", "tool-call-risk-pyramid", "Tool calling risk", ["6.1", "6.2"],
          ["highest-risk", "tool calling", "risk"])
    levels = [("Wrong tool selection", "searches the KB instead of looking up the order", GRAY, "lower"),
              ("Wrong arguments", "refund issued to the wrong customer_id", AMBER, "higher"),
              ("Unauthorized actions", "sends an email it was never allowed to send", RED, "highest")]
    bottom, lh = 960, 200
    x0, x1 = 96, 1100
    inset = 110
    for i, (name, ex, color, risk) in enumerate(levels):
        with d.step(i + 1, name.lower()):
            yb = bottom - i * (lh + 14)
            yt = yb - lh
            l0, r0 = x0 + i * inset, x1 - i * inset
            l1, r1 = l0 + inset * lh / (lh + 14), r0 - inset * lh / (lh + 14)
            d.add(f'<path d="M{l0:.1f} {yb} L{l1:.1f} {yt} L{r1:.1f} {yt} L{r0:.1f} {yb} Z" fill="{NAVY_LIGHT}" '
                  f'stroke="{color}" stroke-width="3" stroke-linejoin="round"/>')
            d.text((x0 + x1) / 2, yt + lh / 2 + 10, name, 28, 700, WHITE, "middle")
            d.text(1180, yt + lh / 2 - 6, risk.upper() + " RISK", 18, 700, color, spacing=0.5)
            d.text(1180, yt + lh / 2 + 26, ex, 20, 400, GRAY_LIGHT)
            if color == RED:
                d.fail_dot(1150, yt + lh / 2 - 12, r=12)
    return d


def d11() -> Diagram:
    d = D("D11", "multi-agent-failure-cascade", "How one agent's failure spreads", ["7.1", "7.3"],
          ["failure propagation", "cascade", "what can go wrong", "multi-agent"])
    y, w, h = 440, 320, 150
    xs = [1504, 1084, 664, 244]
    steps = [("Agent C fails", "tool times out", RED, "robot"),
             ("Agent B", "passes the error on", AMBER, "robot"),
             ("Agent A", "acts on corrupted input", AMBER, "robot"),
             ("User", "gets a wrong answer", RED, "person")]
    for i, ((lab, sub, c, ic), x) in enumerate(zip(steps, xs)):
        with d.step(i + 1, lab.lower()):
            tone = "red" if c == RED else "amber"
            d.node(x, y, w, h, lab, sub, tone=tone, icon=ic, icon_color=c, align="left")
            if i:
                d.arrow(xs[i - 1] - 6, y + h / 2, x + w + 6, y + h / 2, color=c, sw=3)
            if c == RED:
                d.fail_dot(x + w - 6, y + 6, r=15)
    with d.step(5, "where to test", ["test", "detect"]):
        for x, lab in zip(xs[:3], ("timeout test", "contract test", "input validation")):
            d.chip(x + w / 2, y + h + 60, lab, "teal", size=18, mono=False, anchor="middle")
            d.line(x + w / 2, y + h + 4, x + w / 2, y + h + 56, color=TEAL, sw=1.5, dash="3 4", arrow=False)
        d.text(960, 820, "Test each hand-off, not only the final answer.", 24, 600, WHITE, "middle")
    return d


def d12() -> Diagram:
    d = D("D12", "agent-threat-model", "The AI agent threat model", ["8.1", "8.2", "8.3"],
          ["threat model", "what attackers", "threat"])
    cx, cy = 960, 610
    with d.step(1, "the agent"):
        d.node(cx - 170, cy - 90, 340, 180, "AI agent", "TechCorp support", tone="teal", icon="robot", glow=True)
    threats = [("Direct injection", "“ignore your instructions”"), ("Indirect injection", "poisoned KB article"),
               ("Jailbreak", "role-play to bypass rules"), ("PII leakage", "reads out another customer"),
               ("Data exfiltration", "sends data via send_email"), ("Unauthorized actions", "refunds it should not")]
    for k, (name, ex) in enumerate(threats):
        with d.step(k + 2, name.lower(), [name.lower()]):
            a = -math.pi / 2 + k * 2 * math.pi / 6
            tx, ty = cx + 640 * math.cos(a), cy + 330 * math.sin(a)
            w, h = 400, 110
            d.node(tx - w / 2, ty - h / 2, w, h, name, ex, tone="red", size=24)
            # from the threat box edge to the agent box edge
            def edge(px, py, qx, qy, hw, hh):
                dx, dy = qx - px, qy - py
                t = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
                return px + dx * t, py + dy * t
            sx, sy = edge(tx, ty, cx, cy, w / 2 + 8, h / 2 + 8)
            ex_, ey_ = edge(cx, cy, tx, ty, 170 + 10, 90 + 10)
            d.arrow(sx, sy, ex_, ey_, color=RED, sw=2)
    return d


def d13() -> Diagram:
    d = D("D13", "trace-anatomy", "Anatomy of an agent trace", ["9.1", "9.2", "9.3"],
          ["trace anatomy", "without traces", "tracing with langfuse", "spans"],
          footnote="Illustrative durations, tokens and cost")
    nx, bx0, bx1 = 96, 640, 1380
    rows = [("agent_execute", 0, 0.0, 1.0, TEAL, "trace", "3.2 s", "2,140 tok", "$0.0011"),
            ("llm_call: intent", 1, 0.0, 0.22, TEAL, "generation", "0.7 s", "610 tok", "$0.0003"),
            ("tool_call: lookup_customer", 1, 0.23, 0.36, WHITE, "tool", "0.4 s", "–", "–"),
            ("llm_call: response", 1, 0.37, 1.0, TEAL, "generation", "2.0 s", "1,530 tok", "$0.0008")]
    top, rh = 330, 110
    with d.step(1):
        for k, h in enumerate(("duration", "tokens", "cost")):
            d.label(1440 + k * 130, top - 24, h, 14, GRAY)
    for i, (name, depth, s, e, c, typ, dur, tok, cost) in enumerate(rows):
        with d.step(1 if i == 0 else 2, "spans" if i else "trace"):
            y = top + i * rh
            d.text(nx + depth * 34, y + 36, name, 22, 500, WHITE, mono=True)
            d.text(nx + depth * 34, y + 64, typ, 16, 400, GRAY)
            d.add(f'<rect x="{bx0 + s * (bx1 - bx0):.1f}" y="{y + 14}" width="{(e - s) * (bx1 - bx0):.1f}" height="36" '
                  f'rx="4" fill="{c}"/>')
            for k, v in enumerate((dur, tok, cost)):
                d.text(1440 + k * 130, y + 40, v, 18, 400, GRAY_LIGHT)
    with d.step(3, "root cause", ["root cause", "why"]):
        y = top + 4 * rh + 40
        d.node(96, y, 1728, 110, "Root cause in the trace: the tool returned an error,",
               "and the response step answered from the error message.", tone="amber", size=22, sub_size=20)
    return d


def d14() -> Diagram:
    d = D("D14", "ci-quality-gate", "The CI quality gate", ["12.1", "12.2", "11.2", "14.4"],
          ["quality gate", "block bad deploys", "github actions", "regression gate"])
    y, h = 420, 140
    stages = [("Code change", "prompt, model, tool", "white", "git"), ("Pull request", None, "neutral", None),
              ("GitHub Actions", None, "teal", "infinity"), ("DeepEval run", "golden dataset", "teal", "clipboard"),
              ("Compare to baseline", None, "neutral", "bars")]
    w, gap = 300, 57
    xs = [96 + i * (w + gap) for i in range(5)]
    with d.step(1, "the pipeline"):
        for (lab, sub, tone, ic), x in zip(stages, xs):
            d.node(x, y, w, h, lab, sub, tone=tone, icon=ic, icon_color=TEAL if tone != "white" else WHITE,
                   size=22, icon_size=36)
        for i in range(4):
            d.arrow(xs[i] + w + 4, y + h / 2, xs[i + 1] - 4, y + h / 2)
    with d.step(2, "pass or block", ["pass", "block"]):
        gx = xs[4] + w / 2
        d.node(960, 760, 480, 140, "Pass: merge and deploy", "within threshold of baseline", tone="teal", size=24)
        d.node(xs[4], 760, w, 140, "Fail: block", "PR comment with scores", tone="red", size=24)
        d.elbow([(gx - 40, y + h + 4), (gx - 40, 700), (1200, 700), (1200, 756)], color=TEAL, sw=3)
        d.arrow(gx + 40, y + h + 4, gx + 40, 756, color=RED, sw=3)
        d.pass_dot(960, 760, r=16)
        d.fail_dot(xs[4] + w, 760, r=16)
        d.text(96, 820, "Tiered: smoke on every push,", 22, 600, WHITE)
        d.text(96, 856, "standard on every PR,", 22, 600, WHITE)
        d.text(96, 892, "full suite before release.", 22, 600, WHITE)
    return d


def d15() -> Diagram:
    d = D("D15", "production-monitoring-loop", "Production monitoring loop", ["13.1", "13.3"],
          ["production monitoring", "monitoring agents", "drift", "degradation"])
    cx, cy, rx, ry = 960, 620, 640, 290
    nodes = [("Production agent", "live traffic", "teal", "robot", -90),
             ("Sample requests", "e.g. 5% of traces", "neutral", None, -18),
             ("Online evaluator", "judge + metrics", "teal", "clipboard", 54),
             ("Score store", "Langfuse scores", "neutral", "database", 126),
             ("Dashboard + alerts", "drift vs baseline", "amber", "bell", 198)]
    pos = []
    for k, (lab, sub, tone, ic, ang) in enumerate(nodes):
        a = math.radians(ang)
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        pos.append((x, y))
        with d.step(k + 1, lab.lower()):
            d.node(x - 190, y - 65, 380, 130, lab, sub, tone=tone, icon=ic, align="left",
                   icon_color=AMBER if tone == "amber" else (TEAL if tone == "teal" else GRAY), size=22)
    with d.step(6, "close the loop", ["loop", "regression"]):
        for k in range(5):
            (x1, y1), (x2, y2) = pos[k], pos[(k + 1) % 5]
            mx, my = x1 + (x2 - x1) * 0.5, y1 + (y2 - y1) * 0.5
            ux, uy = (x2 - x1), (y2 - y1)
            L = math.hypot(ux, uy)
            ux, uy = ux / L, uy / L
            d.arrow(mx - ux * 60, my - uy * 60, mx + ux * 60, my + uy * 60, color=TEAL if k < 4 else AMBER, sw=3)
        d.text(cx, cy - 10, "bad traces become", 22, 600, WHITE, "middle")
        d.text(cx, cy + 22, "regression tests", 22, 600, WHITE, "middle")
    return d


def d16() -> Diagram:
    d = D("D16", "capstone-architecture", "The agent quality platform", ["14.1", "14.2", "14.3", "14.4", "14.5"],
          ["capstone architecture", "quality platform", "capstone"])
    with d.step(1, "agent under test"):
        d.node(96, 300, 360, 160, "Agent under test", "TechCorp support agent\n5 tools · gpt-4.1-mini",
               tone="teal", icon="robot", sub_size=16)
        d.node(96, 520, 360, 130, "Test harness", "golden + synthetic data", tone="white", icon="doc", align="left",
               size=22, sub_size=16)
        d.arrow(276, 516, 276, 464, color=FLOW)
    with d.step(2, "evaluation pipeline"):
        d.rect(560, 270, 900, 400, stroke=TEAL, fill=NAVY_MID)
        d.text(590, 312, "Evaluation pipeline", 24, 700, TEAL)
        st = [("Functional", "DeepEval, RAGAS", "clipboard"), ("Security", "promptfoo red team", "shield"),
              ("Performance", "latency, cost", "gauge")]
        for k, (lab, sub, ic) in enumerate(st):
            x = 590 + k * 290
            d.node(x, 350, 250, 160, lab, sub, tone="neutral", icon=ic, icon_color=RED if ic == "shield" else TEAL,
                   size=22, sub_size=16)
            if k:
                d.arrow(x - 36, 430, x - 4, 430, color=TEAL)
                d.add(f'<rect x="{x - 26}" y="418" width="16" height="24" rx="3" fill="{TEAL}"/>')
        d.node(590, 550, 840, 90, "Report generation", "per-metric scores, pass/fail gates", tone="white", size=22,
               sub_size=16)
        d.arrow(460, 380, 556, 430, color=TEAL, sw=3)
    with d.step(3, "results and dashboard"):
        d.cylinder(1540, 280, 284, 150, "Results store", "scores, traces", color=GRAY, size=22)
        d.node(1540, 500, 284, 130, "Dashboard", "quality trends", tone="white", icon="bars", icon_color=TEAL,
               align="left", size=22, sub_size=16)
        d.arrow(1464, 360, 1536, 360)
        d.arrow(1682, 434, 1682, 496)
    with d.step(4, "CI/CD and alerting"):
        d.rect(96, 760, 1728, 120, stroke=TEAL, fill=NAVY_LIGHT)
        d.icon("infinity", 150, 820, 52, TEAL)
        d.text(200, 814, "CI/CD integration", 24, 700, TEAL)
        d.text(200, 846, "GitHub Actions gate on every PR", 18, 400, GRAY_LIGHT)
        d.node(1340, 780, 460, 80, "Alerting", "regressions, drift", tone="amber", icon="bell", icon_color=AMBER,
               align="left", size=22, sub_size=16)
        d.arrow(1010, 674, 1010, 756, color=TEAL)
        d.arrow(1682, 634, 1682, 776, color=AMBER)
    return d


ALL = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16]


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    index = {"course": COURSE, "generated_by": "10-graphics/diagrams/_src/build_diagrams.py", "diagrams": {}}
    for fn in ALL:
        d = fn()
        entry = d.save(OUT)
        index["diagrams"][d.id] = entry
        print(f"{d.id:4} {entry['file']}  steps={len(entry['steps'])}")
    (OUT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if "--no-render" not in argv:
        from slide_builder import render_directory

        pngs = render_directory(OUT)
        print(f"rendered {len(pngs)} previews into {OUT / '_preview'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
