#!/usr/bin/env python3
"""Course 4 (AI Agent Observability & Cost Control) master diagrams D1-D12.

Specs: agent-observability-course/09-production/slide-deck-outline.md, "Master diagram list", reconciled
with the frozen decisions in 14-quality-review/2026-10-01-fix-plan.md (tenants ops/finance/hr/eng, O7) and
with the code (span names from telemetry/genai_attrs.py, collector processors from deploy/otel-collector.yaml,
alert shapes from deploy/alerts.yml). No figures are printed that are not in the code or the specs.

Run:   python agent-observability-course/10-graphics/diagrams/_src/build_diagrams.py [--no-render]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
TOOLS = HERE.parents[3] / "voice-ai-agents-course" / "09-production" / "tools"
sys.path.insert(0, str(TOOLS))

from diagram_kit import (AMBER, FLOW, GRAY, GRAY_DARK, GRAY_LIGHT, NAVY, NAVY_LIGHT, NAVY_MID,  # noqa: E402
                         RED, TEAL, TEAL_DIM, WHITE, Diagram, text_width)

COURSE = "Course 4 · Agent Observability"
TENANTS = ["ops", "finance", "hr", "eng"]  # fix plan O7


def D(did, slug, title, lectures, keywords, **kw) -> Diagram:
    return Diagram(did, slug, title, course=COURSE, lectures=lectures, keywords=keywords, **kw)


def hatch_defs(d: Diagram) -> None:
    d.add(f'<defs><pattern id="hatch-teal" width="12" height="12" patternUnits="userSpaceOnUse" '
          f'patternTransform="rotate(45)"><rect width="12" height="12" fill="{NAVY_LIGHT}"/>'
          f'<rect width="5" height="12" fill="{TEAL}"/></pattern>'
          f'<pattern id="hatch-white" width="12" height="12" patternUnits="userSpaceOnUse" '
          f'patternTransform="rotate(45)"><rect width="12" height="12" fill="{NAVY_LIGHT}"/>'
          f'<rect width="5" height="12" fill="{WHITE}" fill-opacity="0.8"/></pattern></defs>')


# ----------------------------------------------------------------------------------------------
def d1() -> Diagram:
    d = D("D1", "three-pillars", "Three pillars, one foundation", ["1.2", "15.1"],
          ["three pillars", "pillar 1", "pillar 2", "pillar 3", "share one foundation"])
    cw, gap, top, ch = 460, 74, 250, 360
    x0 = 96 + (1728 - (3 * cw + 2 * gap)) / 2
    cols = [("Traces", "what happened, step by step", "trace", "pillar 1"),
            ("Quality in production", "is it still right?", "clipboard", "pillar 2"),
            ("Cost", "who spends what, and why", "coin", "pillar 3")]
    with d.step(1, "traces"):
        d.rect(x0, 670, 3 * cw + 2 * gap, 110, stroke=TEAL, fill=NAVY_LIGHT)
        d.text(x0 + (3 * cw + 2 * gap) / 2, 716, "OpenTelemetry (wire format)", 28, 700, TEAL, "middle")
        d.text(x0 + (3 * cw + 2 * gap) / 2, 750, "every model call, tool call and step emits a span", 20, 400,
               GRAY_LIGHT, "middle")
    for i, (name, sub, icon, kw) in enumerate(cols):
        with d.step(i + 1, name.lower(), [kw]):
            x = x0 + i * (cw + gap)
            d.rect(x, top, cw, ch, stroke=TEAL, fill=NAVY_LIGHT)
            ic_color = AMBER if icon == "trace" else TEAL
            d.icon(icon, x + cw / 2, top + 90, 84, ic_color)
            if icon == "clipboard":  # judge score with a trend line
                d.add(f'<polyline points="{x + cw / 2 + 60},{top + 120} {x + cw / 2 + 90},{top + 100} '
                      f'{x + cw / 2 + 115},{top + 108} {x + cw / 2 + 145},{top + 80}" fill="none" stroke="{TEAL}" '
                      f'stroke-width="3"/>')
            d.text(x + cw / 2, top + 210, name, 30, 700, WHITE, "middle")
            d.text(x + cw / 2, top + 250, sub, 20, 400, GRAY_LIGHT, "middle")
            d.arrow(x + cw / 2, 664, x + cw / 2, top + ch + 6, color=TEAL, sw=2)
    with d.step(4, "where classic APM stops", ["classic apm", "where apm stops"]):
        y = 880
        sx = x0 + cw + gap / 2
        d.line(sx, 820, sx, 990, color=WHITE, sw=2, dash="8 6", arrow=False)
        d.text(sx, 812, "where classic APM stops", 20, 600, WHITE, "middle")
        lx = sx - 40
        for lab in reversed(("requests", "errors", "latency")):
            w = d.chip(lx, y, lab, "gray", size=20, mono=False, anchor="end")
            lx -= w + 20
        rx = sx + 40
        for lab in ("tokens", "tool calls", "steps"):
            w = d.chip(rx, y, lab, "teal", size=20, mono=False)
            rx += w + 20
        d.text(sx - 40, y + 80, "APM sees", 18, 400, GRAY, "end")
        d.text(sx + 40, y + 80, "agents also need", 18, 400, TEAL)
    return d


def d2() -> Diagram:
    d = D("D2", "architecture", "The observability stack", ["1.3", "13.4", "14.1", "13.2"],
          ["the stack", "capstone-atlas-ops", "observability stack", "architecture"])
    with d.step(1, "the stack"):
        # Atlas process
        d.rect(96, 250, 500, 450, stroke=TEAL, fill=NAVY_MID)
        d.icon("robot", 140, 296, 44, TEAL)
        d.text(176, 294, "Atlas", 28, 700, WHITE)
        d.text(176, 322, "FastAPI + agent loop", 18, 400, GRAY_LIGHT)
        d.node(126, 360, 440, 120, "LiteLLM", "price table, Router, budgets", tone="white", size=22)
        d.node(126, 510, 440, 130, "OTel SDK", "spans with gen_ai.* attributes", tone="teal", size=22,
               icon="trace", icon_color=AMBER, align="left")
        # collector
        d.rect(720, 300, 440, 300, stroke=GRAY, fill=NAVY_LIGHT)
        d.text(940, 342, "OTel Collector", 26, 700, WHITE, "middle")
        y = 368
        for lab in ("memory_limiter", "attributes/redact", "tail_sampling", "batch"):
            d.chip(940, y, lab, "teal" if lab in ("attributes/redact", "tail_sampling") else "gray", size=16,
                   anchor="middle")
            y += 52
        d.arrow(570, 575, 716, 575, color=FLOW, sw=3)
        d.text(643, 560, "OTLP", 18, 600, GRAY, "middle")
        # Langfuse + judge
        d.node(1300, 250, 524, 140, "Langfuse", "traces, scores, prompts, datasets", tone="teal",
               icon="trace", icon_color=AMBER, align="left")
        d.node(1300, 440, 524, 100, "DeepEval judge", "reads traces, writes scores", tone="white",
               icon="clipboard", icon_color=TEAL, align="left", size=22)
        d.arrow(1520, 394, 1520, 436, color=FLOW)
        d.arrow(1600, 436, 1600, 394, color=TEAL)
        d.arrow(1164, 320, 1296, 320, color=FLOW, sw=3)
        # Prometheus -> Grafana
        d.node(1300, 600, 240, 100, "Prometheus", "metrics", tone="neutral", icon="bars", icon_color=TEAL,
               align="left", size=22)
        d.node(1600, 600, 224, 100, "Grafana", "dashboards, alerts", tone="neutral", size=22)
        d.arrow(1544, 650, 1596, 650)
        d.elbow([(1164, 560), (1232, 560), (1232, 630), (1296, 630)], color=FLOW)
        d.text(1176, 546, "spanmetrics", 16, 400, GRAY, mono=True)
        d.arrow(600, 680, 1296, 680, color=FLOW, dash="6 6")
        d.text(980, 670, "/metrics scrape", 16, 400, GRAY, "middle", mono=True)
        # local store + ops console
        d.cylinder(96, 760, 240, 120, "local store", None, color=GRAY, size=20)
        d.node(400, 760, 300, 120, "Ops Console", "Streamlit · offline mode", tone="white", size=22)
        d.arrow(220, 704, 220, 756)
        d.arrow(340, 820, 396, 820)
    with d.step(2, "alternatives", ["alternatives", "portability", "once more"]):
        y = 820
        x = 800
        for lab in ("LangSmith", "Phoenix", "Datadog"):
            d.node(x, y, 300, 90, lab, tone="gray", dash="8 4", size=22, label_color=GRAY_LIGHT)
            d.elbow([(940, 604), (940, 770), (x + 150, 770), (x + 150, y - 4)], color=GRAY, dash="6 6")
            x += 340
        d.text(800, 990, "any OTLP backend can hang off the Collector", 18, 400, GRAY)
    return d


def d3() -> Diagram:
    d = D("D3", "trace-waterfall", "One agent run, as a trace", ["3.1", "5.1", "5.2", "5.6", "11.1", "1.1"],
          ["waterfall", "as a trace", "the trace we're aiming for", "trace waterfall"])
    hatch_defs(d)
    nx, bx0, bx1, dx = 96, 720, 1700, 1824
    top, rh = 262, 64
    rows = [  # name, depth, start, end, kind, type
        ("invoke_agent atlas", 0, 0.00, 1.00, "teal", "agent"),
        ("guardrail injection_check", 1, 0.00, 0.01, "white", "guardrail"),
        ("step 1", 1, 0.01, 0.38, "gray", "chain"),
        ("execute_tool search_knowledge_base", 2, 0.01, 0.04, "white", "retriever"),
        ("chat gpt-4.1-mini", 2, 0.04, 0.38, "teal", "generation"),
        ("step 2", 1, 0.39, 1.00, "gray", "chain"),
        ("execute_tool lookup_ticket", 2, 0.39, 0.46, "white", "tool"),
        ("chat gpt-4.1-mini", 2, 0.46, 1.00, "teal", "generation"),
    ]
    color = {"teal": TEAL, "white": WHITE, "gray": GRAY_DARK, "red": RED}
    with d.only(1):
        for i, (name, depth, s, e, kind, typ) in enumerate(rows):
            y = top + i * rh
            d.text(nx + depth * 26, y + 38, name, 19 if depth == 2 else 20, 500, WHITE if depth < 2 else GRAY_LIGHT,
                   mono=True)
            x0 = bx0 + s * (bx1 - bx0)
            w = max(8, (e - s) * (bx1 - bx0))
            d.add(f'<rect x="{x0:.1f}" y="{y + 14}" width="{w:.1f}" height="34" rx="4" fill="{color[kind]}" '
                  f'fill-opacity="{0.9 if kind != "white" else 0.85}"/>')
            d.text(dx, y + 38, typ, 18, 400, GRAY, "end")
        # chips on the generation and tool spans
        y = top + 4 * rh
        d.chip(bx0 + 0.05 * (bx1 - bx0), y + 15, "usage: in / out / cached", "gray", size=15)
        y = top + 6 * rh
        x = bx0 + 0.47 * (bx1 - bx0)
        w = d.chip(x, y + 15, "args {ticket_id}", "white", size=15)
        d.chip(x + w + 12, y + 15, "result [redacted]", "gray", size=15)
        d.text(nx, top + len(rows) * rh + 44, "happy path · 2 steps · names from telemetry/genai_attrs.py", 18,
               400, GRAY)
    # build 2: the loop (context bloat)
    with d.only(2, 3):
        d.text(nx, top + 38, "invoke_agent atlas", 20, 500, WHITE, mono=True)
        d.add(f'<rect x="{bx0}" y="{top + 14}" width="{bx1 - bx0}" height="34" rx="4" fill="{TEAL}"/>')
        n = 12
        lh = 48
        t = 0.0
        unit = 1.0 / sum(0.02 + 0.03 * k + 0.02 for k in range(1, n + 1))
        for k in range(1, n + 1):
            y = top + 70 + (k - 1) * lh
            g = (0.03 * k) * unit
            tl = 0.02 * unit
            q = 0.02 * unit
            d.text(nx + 26, y + 30, f"step {k}", 18, 500, GRAY_LIGHT, mono=True)
            d.text(nx + 150, y + 30, "chat → execute_tool lookup_ticket", 16, 400, GRAY, mono=True)
            xg = bx0 + (t + q) * (bx1 - bx0)
            d.add(f'<rect x="{xg:.1f}" y="{y + 10}" width="{g * (bx1 - bx0):.1f}" height="26" rx="3" fill="{TEAL_DIM}"/>')
            xt = xg + g * (bx1 - bx0)
            d.add(f'<rect x="{xt:.1f}" y="{y + 10}" width="{max(6, tl * (bx1 - bx0)):.1f}" height="26" rx="3" fill="{RED}"/>')
            t += q + g + tl
        d.fail_dot(bx1 - 14, top + 70 + 12 * lh + 26, r=13)
        d.text(bx1 - 40, top + 70 + 12 * lh + 34, "tool error ×12", 18, 600, RED, "end")
        d.text(bx0, top + 70 + n * lh + 34, "input re-sent every step: generations grow wider", 18, 400, GRAY_LIGHT)
    # build 3: incident ruler
    with d.only(3):
        ry = 230
        d.line(bx0, ry, bx1, ry, color=GRAY, sw=2, arrow=False)
        d.line(bx0, ry - 14, bx0, top + 70 + 12 * 48, color=RED, sw=2, dash="6 5", arrow=False)
        d.text(bx0 - 10, ry + 6, "T0", 22, 700, RED, "end")
        d.add(f'<path d="M{bx0 + 0.55 * (bx1 - bx0)} {ry - 14} l12 14 l-12 14 l-12 -14 Z" fill="{AMBER}"/>')
        d.text(bx0 + 0.55 * (bx1 - bx0) + 20, ry - 4, "hypothesis", 18, 600, AMBER)
        d.text(bx1, ry - 16, "blast radius →", 18, 600, RED, "end")
    return d


def d4() -> Diagram:
    d = D("D4", "langfuse-on-otel", "Langfuse on OpenTelemetry", ["4.1", "12.1"],
          ["observation types", "langfuse on otel", "what does not move", "not portable", "what moves for free"])
    with d.step(1, "OTel span to Langfuse observation"):
        d.rect(96, 300, 600, 480, stroke=GRAY, fill=NAVY_LIGHT)
        d.label(126, 344, "OpenTelemetry span", 18, GRAY)
        d.text(126, 392, "chat gpt-4.1-mini", 24, 600, WHITE, mono=True)
        attrs = ["gen_ai.operation.name", "gen_ai.request.model", "gen_ai.usage.input_tokens",
                 "gen_ai.usage.output_tokens", "gen_ai.tool.name", "trace_id · parent_id"]
        for k, a in enumerate(attrs):
            d.text(126, 452 + k * 50, a, 20, 400, TEAL if k < 5 else GRAY, mono=True)
        d.arrow(700, 540, 950, 540, color=TEAL, sw=3)
        d.text(825, 500, "SDK v4 =", 20, 600, WHITE, "middle")
        d.text(825, 590, "OTel exporter", 18, 400, GRAY_LIGHT, "middle")
        d.text(825, 616, "+ semantics", 18, 400, GRAY_LIGHT, "middle")
        # rings: trace / session / user / environment / release
        rings = ["release", "environment", "user", "session", "trace"]
        for k, r in enumerate(rings):
            pad = k * 34
            d.rect(960 + pad, 240 + pad, 864 - 2 * pad, 640 - 2 * pad, stroke=GRAY_DARK if k % 2 else GRAY,
                   fill="none", sw=1.5)
            d.text(980 + pad, 268 + pad, r, 16, 600, GRAY, mono=True)
        types = [("agent", "teal"), ("generation", "teal"), ("tool", "white"), ("retriever", "white"),
                 ("guardrail", "white"), ("chain", "gray")]
        for k, (t, tone) in enumerate(types):
            cx = 1220 + (k % 2) * 220
            cy = 440 + (k // 2) * 80
            d.chip(cx, cy, t, tone, size=20, anchor="middle")
        d.text(1392, 700, "observation types", 18, 400, GRAY, "middle")
    with d.step(2, "what is not portable", ["not portable", "does not move", "lock-in"]):
        y = 930
        x = 1100
        for lab in ("scores", "prompts", "datasets"):
            w = d.chip(x, y, lab, "gray", size=20, mono=False)
            x += w + 24
        d.bracket(1090, x - 14, y - 10, "not portable", color=RED, size=20)
        d.fail_dot(x + 20, y + 18, r=14)
        d.text(1084, y + 26, "backend-only:", 18, 400, GRAY, "end")
    return d


def d5() -> Diagram:
    d = D("D5", "token-anatomy", "Token anatomy of one request", ["6.1", "6.4", "6.5"],
          ["token streams", "token anatomy", "where the money goes"],
          footnote="Proportions from one baseline Atlas request (6.1); illustrative")
    hatch_defs(d)
    x0, x1 = 300, 1700
    by, bh = 330, 110
    inp = 0.965  # input share of tokens on the baseline request
    wi = inp * (x1 - x0)
    with d.step(1, "one request"):
        d.text(x0 - 24, by + 50, "one", 20, 600, WHITE, "end")
        d.text(x0 - 24, by + 76, "request", 20, 600, WHITE, "end")
        d.add(f'<rect x="{x0}" y="{by}" width="{wi:.1f}" height="{bh}" fill="{GRAY_DARK}"/>')
        d.add(f'<rect x="{x0 + wi:.1f}" y="{by}" width="{(x1 - x0) - wi:.1f}" height="{bh}" fill="{WHITE}"/>')
        d.text(x0 + wi - 30, by + 66, "input (uncached)", 24, 700, WHITE, "end")
        d.text(x0 + wi, by + bh + 34, "usage.prompt_tokens", 18, 400, GRAY, "end", mono=True)
        d.bracket(x0, x0 + 0.32 * (x1 - x0), by - 4, "system prompt + tool schemas, re-sent each step",
                  color=GRAY, size=18)
        # zoom on the output end
        zx, zy, zw, zh = 1140, 640, 560, 110
        d.path(f"M{x0 + wi:.1f} {by + bh} L{zx} {zy}", color=GRAY_DARK, sw=1.5, arrow=False, dash="4 4")
        d.path(f"M{x1} {by + bh} L{zx + zw} {zy}", color=GRAY_DARK, sw=1.5, arrow=False, dash="4 4")
        d.add(f'<rect x="{zx}" y="{zy}" width="{zw * 0.62:.1f}" height="{zh}" fill="{WHITE}"/>')
        d.add(f'<rect x="{zx + zw * 0.62:.1f}" y="{zy}" width="{zw * 0.38:.1f}" height="{zh}" fill="url(#hatch-white)"/>')
        d.text(zx + 20, zy + 64, "output", 24, 700, NAVY)
        d.text(zx, zy + zh + 32, "completion_tokens", 18, 400, GRAY, mono=True)
        d.text(zx + zw, zy + zh + 32, "reasoning_tokens", 18, 400, GRAY, "end", mono=True)
        d.text(zx + zw, zy + zh + 60, "reasoning: billed as output", 18, 600, WHITE, "end")
        d.text(zx - 20, zy + 64, "output, zoomed", 18, 400, GRAY, "end")
        # retries and judge
        d.text(x0 - 24, 860, "retry", 20, 600, WHITE, "end")
        d.add(f'<rect x="{x0}" y="{836}" width="{x1 - x0 - 620}" height="40" fill="{GRAY_DARK}" opacity="0.4" '
              f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="6 5"/>')
        d.text(x0 + 16, 863, "the whole prompt, paid again", 18, 500, GRAY_LIGHT)
        d.text(x0 - 24, 950, "judge", 20, 600, WHITE, "end")
        d.add(f'<rect x="{x0}" y="{926}" width="{(x1 - x0) * 0.22:.1f}" height="40" fill="{GRAY_DARK}"/>')
        d.text(x0 + (x1 - x0) * 0.22 + 16, 953, "a second model reads it all (Section 8)", 18, 400, GRAY_LIGHT)
    with d.step(2, "caching: the cached share grows", ["caching", "cache"]):
        wc = 0.64 * (x1 - x0)
        d.add(f'<rect x="{x0}" y="{by}" width="{wc:.1f}" height="{bh}" fill="url(#hatch-teal)"/>')
        d.add(f'<rect x="{x0 + 18}" y="{by + 36}" width="190" height="40" rx="6" fill="{NAVY}"/>')
        d.text(x0 + 30, by + 64, "cached input", 22, 700, TEAL)
        d.text(x0, by + bh + 34, "cached_tokens", 18, 400, TEAL, mono=True)
    with d.step(3, "context diet: input shrinks", ["context diet", "diet", "bloats"]):
        d.text(x0 - 24, by + bh + 98, "after diet", 18, 600, TEAL, "end")
        d.add(f'<rect x="{x0}" y="{by + bh + 74}" width="{0.7 * (x1 - x0):.1f}" height="36" rx="4" fill="none" '
              f'stroke="{TEAL}" stroke-width="2" stroke-dasharray="8 4"/>')
        d.text(x0 + 16, by + bh + 99, "less input per step", 18, 600, TEAL)
    return d


def d6() -> Diagram:
    d = D("D6", "cost-rollup-tree", "Rolling cost up", ["6.3", "6.9", "14.4", "14.2"],
          ["five dimensions", "rollup", "showback", "cost per resolved session"])
    nh = 66
    Y = {"total": 230, "tenant": 360, "user": 490, "session": 620, "request": 750, "generation": 880}

    def nodebox(x, y, w, label, tone="neutral", mono=False, size=20, dash=None):
        d.node(x, y, w, nh, label, tone=tone, mono=mono, size=size, dash=dash)

    gens = [(150, 0), (330, 0), (520, 1), (700, 1)]
    with d.step(1, "generations", ["generation"]):
        d.label(96, Y["generation"] - 12, "generation", 16, GRAY)
        for x, _ in gens:
            nodebox(x, Y["generation"], 160, "chat", tone="teal", mono=True)
            d.chip(x + 80, Y["generation"] + nh + 8, "cost_usd", "white", size=14, anchor="middle")
    with d.step(2, "requests"):
        d.label(96, Y["request"] - 12, "request", 16, GRAY)
        for k, x in enumerate((230, 600)):
            nodebox(x, Y["request"], 200, f"trace {k + 1}", mono=True)
        for x, r in gens:
            px = 330 if r == 0 else 700
            d.line(x + 80, Y["generation"] - 4, px, Y["request"] + nh + 2, color=FLOW, sw=1.5, arrow=False)
    with d.step(3, "sessions"):
        d.label(96, Y["session"] - 12, "session", 16, GRAY)
        nodebox(330, Y["session"], 360, "session_id", mono=True)
        for px in (330, 700):
            d.line(px, Y["request"] - 4, 510, Y["session"] + nh + 2, color=FLOW, sw=1.5, arrow=False)
        nodebox(760, Y["session"], 200, "…", tone="gray")
    with d.step(4, "users"):
        d.label(96, Y["user"] - 12, "user", 16, GRAY)
        nodebox(380, Y["user"], 260, "user_id (hashed)", mono=True, size=18)
        nodebox(700, Y["user"], 200, "…", tone="gray")
        d.line(510, Y["session"] - 4, 510, Y["user"] + nh + 2, color=FLOW, sw=1.5, arrow=False)
        d.line(860, Y["session"] - 4, 800, Y["user"] + nh + 2, color=FLOW, sw=1.5, arrow=False)
    with d.step(5, "tenants", ["tenant"]):
        d.label(96, Y["tenant"] - 12, "tenant", 16, GRAY)
        for k, t in enumerate(TENANTS):
            nodebox(260 + k * 240, Y["tenant"], 200, t, tone="white", mono=True)
        d.line(510, Y["user"] - 4, 360, Y["tenant"] + nh + 2, color=FLOW, sw=1.5, arrow=False)
        d.line(800, Y["user"] - 4, 360, Y["tenant"] + nh + 2, color=FLOW, sw=1.5, arrow=False)
        d.node(1230, Y["tenant"] - 6, 330, 78, "cost per resolved session", tone="amber", size=20)
    with d.step(6, "Northwind total"):
        d.node(490, Y["total"], 420, 76, "Northwind total", tone="teal", size=24, glow=True)
        for k in range(4):
            d.line(360 + k * 240, Y["tenant"] - 4, 700, Y["total"] + 80, color=TEAL, sw=2, arrow=False)
    with d.step(7, "the feature cut", ["feature"]):
        fx, bus_y, bus_x = 1460, 1004, 1340
        feats = ["policy_question", "ticket_lookup", "create_ticket", "password_reset", "shipment_status"]
        d.label(fx, 560, "by feature: a second roll-up", 16, GRAY)
        dash = dict(color=GRAY, sw=1.5, dash="6 6", arrow=False)
        d.line(150 + 80, bus_y, bus_x, bus_y, **dash)
        for x, _ in gens:
            d.line(x + 80, Y["generation"] + nh + 36, x + 80, bus_y, **dash)
        top_f = 590
        d.line(bus_x, bus_y, bus_x, top_f + 30, **dash)
        for k, f in enumerate(feats):
            y = top_f + k * 82
            d.node(fx, y, 364, 60, f, tone="neutral", mono=True, size=18, dash="8 4")
            d.arrow(bus_x, y + 30, fx - 4, y + 30, color=GRAY, sw=1.5, dash="6 6")
    return d


def d7() -> Diagram:
    d = D("D7", "latency-budget", "Latency budget of one request", ["7.1", "7.2", "7.4", "7.6", "5.4"],
          ["latency numbers", "latency budget", "three clocks", "ttft", "fallback"])
    x0, scale = 330, 1.0
    rows_y = [300, 380, 460]
    segs = [  # per step: (label, width px, color)
        [("queue", 30, GRAY_DARK), ("TTFT", 230, TEAL), ("TPOT × tokens", 90, TEAL_DIM), ("tool", 80, WHITE)],
        [("queue", 30, GRAY_DARK), ("TTFT", 230, TEAL), ("TPOT × tokens", 60, TEAL_DIM), ("tool", 50, WHITE)],
        [("queue", 30, GRAY_DARK), ("TTFT", 230, TEAL), ("TPOT × tokens", 220, TEAL_DIM)],
    ]
    target = x0 + 1300
    with d.step(1, "per-step budgets"):
        start = x0
        for i, (y, row) in enumerate(zip(rows_y, segs)):
            d.text(x0 - 24, y + 36, f"step {i + 1}", 20, 600, WHITE, "end")
            x = start
            for lab, w, c in row:
                d.add(f'<rect x="{x}" y="{y + 8}" width="{w}" height="44" fill="{c}" stroke="{NAVY}" stroke-width="2"/>')
                if text_width(lab, 18, 600) < w - 12:
                    d.text(x + w / 2, y + 37, lab, 18, 600, NAVY if c != GRAY_DARK else WHITE, "middle")
                x += w
            start = x
        lx = x0
        for lab, c in (("queue", GRAY_DARK), ("TTFT", TEAL), ("TPOT × tokens", TEAL_DIM), ("tool", WHITE)):
            d.add(f'<rect x="{lx}" y="232" width="28" height="20" rx="3" fill="{c}"/>')
            d.text(lx + 38, 249, lab, 18, 500, GRAY_LIGHT)
            lx += 38 + text_width(lab, 18, 500) + 36
        # end-to-end
        y = 560
        d.text(x0 - 24, y + 40, "end to end", 20, 700, WHITE, "end")
        x = x0
        for i, row in enumerate(segs):
            w = sum(s[1] for s in row)
            d.add(f'<rect x="{x}" y="{y + 8}" width="{w}" height="50" fill="{TEAL if i % 2 == 0 else TEAL_DIM}" '
                  f'stroke="{NAVY}" stroke-width="2"/>')
            d.text(x + w / 2, y + 40, f"step {i + 1}", 18, 700, NAVY, "middle")
            x += w
        d.line(target, 250, target, 900, color=AMBER, sw=3, arrow=False)
        d.text(target, 240, "example budget", 20, 600, AMBER, "middle")
    with d.step(2, "p50 vs p95", ["p95", "p50"]):
        y = 680
        d.text(x0 - 24, y + 30, "p50", 20, 600, WHITE, "end")
        d.add(f'<rect x="{x0}" y="{y + 10}" width="{target - x0 - 240}" height="28" rx="4" fill="{TEAL}"/>')
        d.pass_dot(target - 220, y + 24, r=12)
        y = 740
        d.text(x0 - 24, y + 30, "p95", 20, 600, WHITE, "end")
        d.add(f'<rect x="{x0}" y="{y + 10}" width="{target - x0}" height="28" rx="4" fill="{TEAL_DIM}"/>')
        d.add(f'<rect x="{target}" y="{y + 10}" width="150" height="28" rx="4" fill="{RED}"/>')
        d.fail_dot(target + 178, y + 24, r=12)
    with d.step(3, "fallback when the provider times out", ["fallback", "timeout", "circuit"]):
        y = 820
        d.text(x0 - 24, y + 34, "slow provider", 20, 600, WHITE, "end")
        d.add(f'<rect x="{x0}" y="{y + 10}" width="420" height="36" fill="{TEAL}" opacity="0.5"/>')
        d.line(x0 + 420, y - 2, x0 + 420, y + 58, color=AMBER, sw=3, arrow=False)
        d.text(x0 + 420, y + 82, "timeout", 18, 600, AMBER, "middle")
        d.add(f'<rect x="{x0 + 424}" y="{y + 10}" width="320" height="36" fill="none" stroke="{TEAL}" '
              f'stroke-width="2" stroke-dasharray="8 4"/>')
        d.text(x0 + 584, y + 35, "fallback model", 18, 600, TEAL, "middle")
    return d


def d8() -> Diagram:
    d = D("D8", "slo-error-budget-burn", "SLO, error budget, burn rate", ["9.1", "9.5", "11.3"],
          ["error budget", "burn rate", "burn-rate", "the slos", "six slis"],
          footnote="Illustrative curves; SLO and alert shapes from deploy/alerts.yml")
    px0, px1 = 260, 1700

    def xd(day):
        return px0 + day / 30 * (px1 - px0)

    with d.step(1, "SLI and SLO", ["sli", "slo"]):
        top, bot = 250, 520
        d.text(px0 - 20, top + 10, "task success", 18, 600, WHITE, "end")
        d.rect(px0, top, px1 - px0, bot - top, stroke=GRAY_DARK, fill="none", sw=1)

        def ys(v):  # 90..100 %
            return bot - (v - 90) / 10 * (bot - top)

        d.line(px0, ys(95), px1, ys(95), color=AMBER, sw=2, dash="8 5", arrow=False)
        d.text(px1 + 12, ys(95) + 6, "SLO 95%", 18, 600, AMBER)
        import random
        rnd = random.Random(7)
        pts = []
        for i in range(0, 61):
            day = i / 2
            v = 97.6 + rnd.uniform(-0.6, 0.6)
            if 10 <= day <= 11.5:
                v = 92.5 + rnd.uniform(-0.8, 0.8)
            pts.append(f"{xd(day):.1f},{ys(v):.1f}")
        d.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{TEAL}" stroke-width="3" stroke-linejoin="round"/>')
        d.text(xd(10.75), ys(91) + 4, "incident", 16, 600, RED, "middle")
    with d.step(2, "error budget", ["error budget"]):
        top, bot = 600, 940
        d.text(px0 - 20, top + 10, "error budget", 18, 600, WHITE, "end")
        d.text(px0 - 20, top + 34, "remaining", 18, 600, WHITE, "end")
        d.rect(px0, top, px1 - px0, bot - top, stroke=GRAY_DARK, fill="none", sw=1)
        for day in (0, 10, 20, 30):
            d.text(xd(day), bot + 30, f"day {day}", 16, 400, GRAY, "middle")

        def yb(v):  # 0..100 %
            return bot - v / 100 * (bot - top)

        d.text(px0 - 12, yb(0) + 6, "0", 16, 400, GRAY, "end")
        d.path(f"M{xd(0)} {yb(100)} L{xd(30)} {yb(40)}", color=TEAL, sw=3, arrow=False)
        d.text(xd(30) + 12, yb(40) + 6, "normal month", 16, 600, TEAL)
    with d.step(3, "fast and slow burn", ["burn"]):
        top, bot = 600, 940

        def yb(v):
            return bot - v / 100 * (bot - top)

        d.path(f"M{xd(10)} {yb(80)} L{xd(12)} {yb(0)}", color=RED, sw=3, arrow=False)
        d.fail_dot(xd(12), yb(0), r=12)
        d.text(xd(12) + 22, yb(8), "fast burn → page", 18, 700, RED)
        d.path(f"M{xd(10)} {yb(80)} L{xd(26)} {yb(0)}", color=AMBER, sw=3, arrow=False)
        d.text(xd(22), yb(30), "slow burn → ticket", 18, 700, AMBER)
        d.line(xd(10), top + 4, xd(10), bot, color=GRAY, sw=1.5, dash="4 6", arrow=False)
    return d


def d9() -> Diagram:
    d = D("D9", "incident-timeline", "Reading an incident timeline", ["11.1", "11.2", "11.3", "11.4", "11.5"],
          ["incident timeline", "the four questions", "timeline"])
    y = 660
    xs = [190, 470, 720, 960, 1200, 1440, 1700]
    marks = [("T-∞", "change", "prompt v2, top-k raised", GRAY, "above"),
             ("T0", "first symptom", "visible in traces", RED, "below"),
             ("T+", "alert", "or silent", AMBER, "above"),
             ("", "detection", "someone looks", WHITE, "below"),
             ("", "mitigation", "rollback, cap", TEAL, "above"),
             ("", "root cause", "from the spans", TEAL, "below"),
             ("", "postmortem", "", TEAL, "above")]
    with d.step(1):
        d.line(110, y, 1800, y, color=GRAY, sw=3)
        for x, (t, name, sub, c, pos) in zip(xs, marks):
            d.add(f'<circle cx="{x}" cy="{y}" r="14" fill="{NAVY}" stroke="{c}" stroke-width="4"/>')
            ly = y - 60 if pos == "above" else y + 70
            if t:
                d.text(x, ly - 34 if pos == "above" else ly - 2, t, 26, 700, c, "middle")
                ly = ly if pos == "above" else ly + 30
            d.text(x, ly, name, 22, 600, WHITE, "middle")
            if sub:
                d.text(x, ly + 28, sub, 18, 400, GRAY, "middle")
        d.chip(xs[2] - 60, y + 40, "no alert?", "red", size=16, mono=False)
        x = xs[6] - 140
        for lab in ("budget", "alert", "test"):
            w = d.chip(x, y + 40, lab, "teal", size=16, mono=False)
            x += w + 10
    with d.step(2, "blast radius", ["blast radius"]):
        d.bracket(xs[1], xs[4], 400, "blast radius: tenants affected", color=RED, size=20)
        x = xs[1] + 120
        for k, t in enumerate(TENANTS):
            w = d.chip(x, 422, t, "red" if k < 2 else "gray", size=16)
            x += w + 14
        d.text(xs[4] + 10, 454, "example", 16, 400, GRAY)
    return d


def d10() -> Diagram:
    d = D("D10", "telemetry-threat-model", "Where PII leaks in telemetry", ["10.1", "10.2"],
          ["where it goes", "threat model", "masking", "four threats"])
    r1, r2, h = 300, 660, 130
    with d.step(1, "the flow and the leaks"):
        d.node(96, r1, 300, h, "Prompt", tone="white", icon="person", align="left")
        d.chip(150, r1 + h + 14, "PII", "red", size=16, mono=False)
        d.node(500, r1, 300, h, "Tool result", tone="white", icon="wrench", align="left")
        d.chip(554, r1 + h + 14, "employee record", "red", size=16, mono=False)
        d.node(904, r1, 300, h, "Span", tone="teal", icon="trace", icon_color=AMBER, align="left")
        d.node(1308, r1, 300, h, "Exporter", "SDK / Collector", tone="neutral")
        d.arrow(400, r1 + h / 2, 496, r1 + h / 2)
        d.arrow(804, r1 + h / 2, 900, r1 + h / 2)
        d.arrow(1208, r1 + h / 2, 1304, r1 + h / 2)
        d.elbow([(1612, r1 + h / 2), (1740, r1 + h / 2), (1740, r2 + h / 2), (1612, r2 + h / 2)])
        d.node(1308, r2, 300, h, "Backend", "Langfuse", tone="neutral", icon="database", icon_color=GRAY, align="left")
        d.node(904, r2, 300, h, "Judge", "sees everything", tone="white", icon="clipboard", icon_color=TEAL,
               align="left")
        d.node(500, r2, 300, h, "Dashboards", "shared widely", tone="white", icon="bars", icon_color=TEAL,
               align="left")
        d.arrow(1304, r2 + h / 2, 1208, r2 + h / 2)
        d.arrow(900, r2 + h / 2, 804, r2 + h / 2)
    with d.only(1):
        for cx, cy in ((1054, r1), (1458, r1), (1458, r2), (1054, r2), (650, r2)):
            d.fail_dot(cx, cy, r=15)
    with d.step(2, "shields", ["masking", "mask", "shield"]):
        shields = [(1054, r1 - 40, "SDK mask="), (1458, r1 - 40, "attributes processor"),
                   (1458, r2 + h + 40, "retention"), (650, r2 + h + 40, "RBAC")]
        for cx, cy, lab in shields:
            d.icon("shield", cx, cy, 46, TEAL)
            above = cy < r1
            d.text(cx + 34, cy + 8, lab, 18, 600, TEAL, mono=(lab == "SDK mask="))
        d.fail_dot(1054, r2, r=15)
        d.text(1054, r2 + h + 48, "judge: send it masked data", 18, 400, GRAY, "middle")
    return d


def d11() -> Diagram:
    d = D("D11", "ops-dashboard", "Atlas Ops dashboard", ["9.3", "14.3"],
          ["dashboard", "row 1", "rows 2 to 4", "one panel per sli"],
          footnote="Illustrative values · simulated traffic")
    pw, ph, gx, gy = 560, 360, 24, 24
    x0, y0 = 96, 230
    panels = ["p95 latency", "cost per resolved session", "task success", "tool error rate", "judge score",
              "budget remaining"]
    import random
    rnd = random.Random(3)
    for k, title in enumerate(panels):
        with d.step(k + 1, title, [title]):
            x = x0 + (k % 3) * (pw + gx)
            y = y0 + (k // 3) * (ph + gy)
            d.rect(x, y, pw, ph, stroke=GRAY_DARK, fill=NAVY_LIGHT)
            d.text(x + 24, y + 42, title, 22, 600, GRAY_LIGHT)
            ax0, ax1, ay0, ay1 = x + 30, x + pw - 30, y + ph - 40, y + 80
            if title in ("p95 latency", "tool error rate", "judge score"):
                base = {"p95 latency": 0.45, "tool error rate": 0.3, "judge score": 0.7}[title]
                pts = []
                for i in range(30):
                    v = base + rnd.uniform(-0.08, 0.08)
                    if title == "p95 latency" and 19 <= i <= 22:
                        v = 0.85
                    if title == "judge score" and i > 20:
                        v -= 0.012 * (i - 20)
                    pts.append(f"{ax0 + i * (ax1 - ax0) / 29:.1f},{ay0 - v * (ay0 - ay1):.1f}")
                if title == "judge score":
                    d.add(f'<rect x="{ax0}" y="{ay0 - 0.8 * (ay0 - ay1):.1f}" width="{ax1 - ax0}" '
                          f'height="{0.2 * (ay0 - ay1):.1f}" fill="{TEAL}" opacity="0.12"/>')
                    d.text(ax1, ay0 - 0.82 * (ay0 - ay1), "drift band", 14, 600, TEAL, "end")
                thr = {"p95 latency": (0.7, "SLO 4 s"), "tool error rate": (0.6, "threshold")}.get(title)
                if thr:
                    ty = ay0 - thr[0] * (ay0 - ay1)
                    d.add(f'<path d="M{ax0} {ty:.1f} H{ax1}" stroke="{AMBER}" stroke-width="2" stroke-dasharray="8 4"/>')
                    d.text(ax1, ty - 8, thr[1], 14, 600, AMBER, "end")
                d.add(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{TEAL}" stroke-width="3" stroke-linejoin="round"/>')
                if title == "p95 latency":
                    for i in (19, 20, 21, 22):
                        px = ax0 + i * (ax1 - ax0) / 29
                        d.add(f'<circle cx="{px:.1f}" cy="{ay0 - 0.85 * (ay0 - ay1):.1f}" r="5" fill="{RED}"/>')
                # release annotations
                for i in (8, 20):
                    rx = ax0 + i * (ax1 - ax0) / 29
                    d.add(f'<path d="M{rx:.1f} {ay1 - 10} V{ay0}" stroke="{WHITE}" stroke-opacity="0.5" stroke-width="1.5" stroke-dasharray="4 5"/>')
                d.text(ax0 + 20 * (ax1 - ax0) / 29 + 4, ay1 - 2, "release", 13, 500, GRAY)
            elif title in ("cost per resolved session", "budget remaining"):
                vals = [0.55, 0.75, 0.68, 0.72] if title.startswith("cost") else [0.7, 0.4, 0.85, 0.15]
                bw = (ax1 - ax0) / 4 - 24
                for i, (t, v) in enumerate(zip(TENANTS, vals)):
                    bx = ax0 + i * (bw + 24) + 12
                    c = TEAL
                    if title == "budget remaining" and v < 0.2:
                        c = RED
                    d.add(f'<rect x="{bx:.1f}" y="{ay0 - v * (ay0 - ay1):.1f}" width="{bw:.1f}" height="{v * (ay0 - ay1):.1f}" rx="3" fill="{c}"/>')
                    d.text(bx + bw / 2, ay0 + 26, t, 16, 500, GRAY, "middle", mono=True)
                if title == "budget remaining":
                    cy = ay0 - 0.15 * (ay0 - ay1)
                    d.add(f'<path d="M{ax0} {cy:.1f} H{ax1}" stroke="{RED}" stroke-width="2"/>')
                    d.text(ax1, cy - 8, "hard cap", 14, 700, RED, "end")
            else:  # gauge
                cx, cy, r = x + pw / 2, y + ph - 70, 130
                d.add(f'<path d="M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="{GRAY_DARK}" stroke-width="22"/>')
                a = math.pi * (1 - 0.89)
                d.add(f'<path d="M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r * math.cos(a):.1f} {cy - r * math.sin(a):.1f}" '
                      f'fill="none" stroke="{TEAL}" stroke-width="22"/>')
                a2 = math.pi * (1 - 0.95)
                d.add(f'<path d="M{cx + (r - 20) * math.cos(a2):.1f} {cy - (r - 20) * math.sin(a2):.1f} '
                      f'L{cx + (r + 20) * math.cos(a2):.1f} {cy - (r + 20) * math.sin(a2):.1f}" stroke="{AMBER}" stroke-width="4"/>')
                d.text(cx, cy - 10, "resolved", 20, 600, WHITE, "middle")
                d.text(cx + r + 6, cy - 50, "SLO", 14, 600, AMBER)
    return d


def d12() -> Diagram:
    d = D("D12", "backend-decision-matrix", "Choosing a backend", ["12.5", "1.3"],
          ["decision matrix", "matrix, filled in", "choosing a backend"],
          footnote="Qualitative, dated 2026-09-28 (10-resources/backend-decision-matrix.md); re-check before deciding")
    cols = ["Langfuse", "LangSmith", "Phoenix", "OpenLLMetry", "Datadog"]
    rows = [("Control / self-host", ["●●●", "●○○", "●●●", "●●●", "●○○"]),
            ("Compliance control", ["●●●", "●●○", "●●●", "●●●", "●●○"]),
            ("Agent features", ["●●●", "●●●", "●●○", "●●○", "●●○"]),
            ("Cost model", ["free tier, then volume", "free tier, then traces/seats", "open source", "open source",
                            "APM add-on"]),
            ("Lock-in", ["low-medium", "medium-high", "low", "low", "medium"])]
    x = [96, 470, 740, 1010, 1280, 1550]
    top, rh = 260, 120
    with d.step(1):
        for i, c in enumerate(cols):
            d.text(x[i + 1], top, c, 24, 700, TEAL)
    for r, (name, vals) in enumerate(rows):
        with d.step(r + 1, name.lower()):
            y = top + 40 + r * rh
            d.rect(96, y, 1728, rh - 14, stroke="none", fill=NAVY_LIGHT if r % 2 == 0 else NAVY_MID, sw=0)
            d.text(x[0] + 20, y + rh / 2, name, 22, 600, WHITE)
            for i, v in enumerate(vals):
                dots = v.startswith("●")
                if dots or len(v) < 18:
                    d.text(x[i + 1], y + rh / 2, v, 26 if dots else 20, 400, TEAL if dots else WHITE)
                else:
                    a, b = v.split(", ") if ", " in v else (v[:v.rfind(" ")], v[v.rfind(" ") + 1:])
                    d.text(x[i + 1], y + rh / 2 - 12, a + ",", 18, 400, WHITE)
                    d.text(x[i + 1], y + rh / 2 + 14, b, 18, 400, WHITE)
    return d


ALL = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12]
MASTER_STEP = {"D3": 1, "D10": 2}


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    index = {"course": COURSE, "generated_by": "10-graphics/diagrams/_src/build_diagrams.py", "diagrams": {}}
    for fn in ALL:
        d = fn()
        entry = d.save(OUT, master_step=MASTER_STEP.get(d.id))
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
