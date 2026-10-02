#!/usr/bin/env python3
"""Course 3 (Production Voice AI Agents) master diagrams D1-D16.

Specs: voice-ai-agents-course/09-production/slide-deck-outline.md, "Master diagram list".
Run:   python voice-ai-agents-course/10-graphics/diagrams/_src/build_diagrams.py [--no-render]
Writes D{n}-{slug}.svg (+ D{n}-step{k}.svg build steps) and index.json next to this folder, then renders
PNG previews into ../_preview/ (git-ignored) with slide_builder.py's renderer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
TOOLS = HERE.parents[2] / "09-production" / "tools"
sys.path.insert(0, str(TOOLS))

from diagram_kit import (AMBER, FLOW, GRAY, GRAY_DARK, GRAY_LIGHT, NAVY, NAVY_LIGHT, NAVY_MID,  # noqa: E402
                         RED, TEAL, TEAL_DIM, WHITE, Diagram, text_width)

COURSE = "Course 3 · Voice AI Agents"


def D(did, slug, title, lectures, keywords, spec="", **kw) -> Diagram:
    return Diagram(did, slug, title, course=COURSE, lectures=lectures, keywords=keywords, spec=spec, **kw)


# ----------------------------------------------------------------------------------------------
def d1() -> Diagram:
    d = D("D1", "voice-pipeline", "The voice pipeline", ["1.2", "3.1", "13.1"],
          ["voice pipeline", "seven components", "where each fails"])
    names = [("Caller", None, "white", "person"), ("Transport", "WebRTC / SIP", "neutral", None),
             ("VAD", "Is someone\nspeaking?", "neutral", None), ("STT", "Speech to\ntext", "neutral", None),
             ("Turn\ndetection", "Are they\ndone?", "neutral", None), ("LLM", "Decide what\nto say", "teal", "brain"),
             ("TTS", "Text to\nspeech", "neutral", None), ("Transport", "WebRTC / SIP", "neutral", None),
             ("Caller", None, "white", "person")]
    w, gap, y, h = 152, 45, 400, 200
    xs = [96 + i * (w + gap) for i in range(9)]
    with d.step(1, "the components"):
        for i, (lab, sub, tone, icon) in enumerate(names):
            d.node(xs[i], y, w, h, lab, sub, tone=tone, icon=icon, icon_size=40)
        for i in range(8):
            d.arrow(xs[i] + w + 4, y + h / 2, xs[i + 1] - 4, y + h / 2)
        # Tools under the LLM
        lx = xs[5]
        d.node(lx, 760, w, 150, "Tools", None, tone="white", icon="wrench")
        d.line(lx + w / 2, y + h + 6, lx + w / 2, 754, sw=2, start_arrow=True)
        d.text(lx + w / 2 + 16, 690, "act on the world", 18, 400, GRAY, "start")
    with d.step(2, "where each fails", ["where each fails", "fails", "failure"]):
        fails = {2: "misses quiet\nspeech", 3: "mishears\nnames", 4: "cuts caller\noff", 5: "invents\navailability",
                 6: "reads symbols\naloud"}
        for i, cap in fails.items():
            cx = xs[i] + w / 2
            d.fail_dot(cx, y)
            for k, ln in enumerate(cap.split("\n")):
                d.text(cx, y - 70 + k * 23, ln, 18, 400, GRAY, "middle")
        tx = xs[5]
        d.fail_dot(tx + w, 760)
        d.lines(tx + w + 26, 820, ["wrong", "arguments"], 18, 400, GRAY)
    return d


def d2() -> Diagram:
    d = D("D2", "cascaded-vs-s2s-vs-hybrid", "Three architectures", ["1.3", "6.1", "6.3", "6.4"],
          ["cascaded", "speech-to-speech", "half-cascade", "hybrid pipeline", "two ways to build riley",
           "three architectures"])
    rows = [290, 530, 770]
    h = 120

    def ends(y):
        d.node(96, y, 150, h, "Audio in", None, tone="white", icon="wave", icon_size=34, align="left")
        d.node(1110, y, 150, h, "Audio out", None, tone="white", icon="wave", icon_size=34, align="left")

    def ends_simple(y):
        d.node(96, y, 150, h, "Audio in", tone="white")
        d.node(1110, y, 150, h, "Audio out", tone="white")

    with d.step(1, "cascaded", ["cascaded"]):
        y = rows[0]
        d.label(96, y - 22, "Cascaded", 18, GRAY)
        ends_simple(y)
        bx = [330, 560, 790]
        for x, lab, tone, ic in ((bx[0], "STT", "neutral", None), (bx[1], "LLM", "teal", "brain"),
                                 (bx[2], "TTS", "neutral", None)):
            d.node(x, y, 170, h, lab, tone=tone)
        d.arrow(250, y + h / 2, bx[0] - 4, y + h / 2)
        d.arrow(bx[0] + 174, y + h / 2, bx[1] - 4, y + h / 2, label="text")
        d.arrow(bx[1] + 174, y + h / 2, bx[2] - 4, y + h / 2, label="text")
        d.arrow(bx[2] + 174, y + h / 2, 1106, y + h / 2)
    with d.step(2, "speech-to-speech", ["speech-to-speech", "realtime model (hears", "audio in, audio out"]):
        y = rows[1]
        d.label(96, y - 22, "Speech-to-speech", 18, GRAY)
        ends_simple(y)
        d.node(330, y, 630, h, "Realtime model", "hears, thinks, speaks", tone="teal", glow=True)
        d.arrow(250, y + h / 2, 326, y + h / 2)
        d.arrow(964, y + h / 2, 1106, y + h / 2)
    with d.step(3, "half-cascade", ["half-cascade", "hybrid", "text output only"]):
        y = rows[2]
        d.label(96, y - 22, "Half-cascade (hybrid)", 18, GRAY)
        ends_simple(y)
        d.node(330, y, 400, h, "Realtime model", "text out", tone="teal")
        d.node(790, y, 170, h, "Your TTS", tone="white")
        d.arrow(250, y + h / 2, 326, y + h / 2)
        d.arrow(734, y + h / 2, 786, y + h / 2, label="text")
        d.arrow(964, y + h / 2, 1106, y + h / 2)
    with d.step(4, "trade-offs", ["comparison", "head-to-head", "trade-off"]):
        tx, ty, cw = 1334, 320, [170, 100, 100, 100]
        d.rect(tx - 20, ty - 60, sum(cw) + 40, 640, stroke=GRAY_DARK, fill=NAVY_MID)
        heads = ["", "Cascaded", "S2S", "Hybrid"]
        x = tx
        for i, hd in enumerate(heads):
            if hd:
                d.text(x + cw[i] / 2, ty, hd, 18, 600, TEAL, "middle")
            x += cw[i]
        rows_t = [("Control", 3, 1, 2), ("Cost visibility", 3, 1, 2), ("Latency", 2, 3, 2),
                  ("Voice choice", 3, 1, 3), ("Tool reliability", 3, 2, 2)]
        for r, (name, *vals) in enumerate(rows_t):
            yy = ty + 70 + r * 92
            d.add(f'<path d="M{tx} {yy - 44} H{tx + sum(cw)}" stroke="{GRAY_DARK}" stroke-width="1" opacity="0.6"/>')
            d.text(tx, yy, name, 20, 500, WHITE)
            x = tx + cw[0]
            for i, v in enumerate(vals):
                dots = "●" * v + "○" * (3 - v)
                d.text(x + cw[i + 1] / 2, yy, dots, 20, 400, TEAL, "middle")
                x += cw[i + 1]
        d.text(tx, ty + 70 + 5 * 92 - 20, "●●● stronger · qualitative, no benchmarks", 16, 400, GRAY)
    return d


def d2_zoom(out: Path) -> dict:
    """6.1 variant: speech-to-speech row alone, zoomed, with the transcription side channel."""
    d = D("D2", "zoom-speech-to-speech", "Audio in, audio out", ["6.1"], [])
    y = 430
    d.node(140, y, 240, 160, "Audio in", tone="white", icon="wave")
    d.node(560, y, 800, 160, "Realtime model", "hears, thinks, speaks", tone="teal", glow=True, size=30, sub_size=22)
    d.node(1540, y, 240, 160, "Audio out", tone="white", icon="wave")
    d.arrow(384, y + 80, 556, y + 80, sw=3, color=TEAL)
    d.arrow(1364, y + 80, 1536, y + 80, sw=3, color=TEAL)
    d.node(860, 760, 260, 110, "Transcript", "for logs, not reasoning", tone="neutral", size=24)
    d.elbow([(260, y + 164), (260, 815), (856, 815)], color=GRAY, dash="8 4")
    d.text(300, 800, "transcription side channel", 18, 400, GRAY)
    fn = "D2-step5.svg"
    (out / fn).write_text(d.svg(), encoding="utf-8")
    return {"file": fn, "label": "6.1 zoom: speech-to-speech with transcript side channel",
            "keywords": ["audio in, audio out", "where the transcript comes from", "side channel"]}


def d3() -> Diagram:
    d = D("D3", "latency-budget-waterfall", "Where the time goes", ["1.4", "9.8", "10.1", "13.5"],
          ["where the time goes", "latency budget", "voice-to-voice", "ttft", "ttfb", "one turn, timed"],
          footnote="Example numbers for illustration")
    x0, x1 = 260, 1700
    px = (x1 - x0) / 1200
    ay = 800
    with d.step(1, "the axis"):
        d.line(x0, ay, x1 + 30, ay, color=GRAY, sw=2)
        for t in range(0, 1201, 200):
            x = x0 + t * px
            d.line(x, ay, x, ay + 12, color=GRAY, sw=2, arrow=False)
            d.text(x, ay + 42, f"{t:,} ms" if t else "0", 18, 400, GRAY, "middle")
        d.text(x0, ay + 82, "caller stops speaking", 20, 600, WHITE, "middle")
    segs = [("Network in", 40), ("Endpointing", 250), ("STT final", 80), ("LLM TTFT", 280), ("TTS TTFB", 110),
            ("Network out", 40)]
    by, bh = 500, 110
    with d.step(2, "the stages"):
        x = x0
        for i, (name, ms) in enumerate(segs):
            w = ms * px
            fill = TEAL if i % 2 == 0 else TEAL_DIM
            d.add(f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{fill}" stroke="{NAVY}" stroke-width="2"/>')
            cx = x + w / 2
            wide = w > 110
            # labels above (staggered for narrow segments), values below
            ly = by - 26
            if i == len(segs) - 1:  # last narrow segment: label to the right of the target line
                d.path(f"M{cx} {by - 4} V{by - 34} H{cx + 40}", color=GRAY_DARK, sw=1.5, arrow=False)
                d.text(cx + 46, by - 28, name, 20, 600, WHITE, "start")
            else:
                if not wide:
                    d.line(cx, by - 4, cx, ly + 8, color=GRAY_DARK, sw=1.5, arrow=False)
                d.text(cx, ly, name, 20, 600, WHITE, "middle")
            if wide:
                d.text(cx, by + bh / 2 + 9, f"{ms} ms", 22, 700, NAVY, "middle")
            else:
                d.text(cx, by + bh + 32, f"{ms}", 20, 600, TEAL, "middle")
            x += w
        end = x0 + 800 * px
        d.line(end, by + bh + 50, end, ay - 6, color=FLOW, sw=2, dash="4 4", arrow=False)
        d.text(end + 14, ay - 40, "caller hears first audio", 20, 600, WHITE, "start")
    with d.step(3, "the target", ["target", "budget"]):
        tx = x0 + 800 * px
        d.line(tx, 400, tx, by + bh + 40, color=AMBER, sw=3, arrow=False)
        d.text(tx, 386, "example target · 800 ms", 20, 600, AMBER, "middle")
    with d.step(4, "slow turn (p95)", ["p95", "slow turn", "measure p95"]):
        sy = 672
        w_ok = 800 * px
        w_bad = 330 * px
        d.add(f'<rect x="{x0}" y="{sy}" width="{w_ok:.1f}" height="26" rx="4" fill="{TEAL_DIM}"/>')
        d.add(f'<rect x="{x0 + w_ok:.1f}" y="{sy}" width="{w_bad:.1f}" height="26" rx="4" fill="{RED}"/>')
        d.fail_dot(x0 + w_ok + w_bad + 30, sy + 13, r=13)
        d.text(x0 - 16, sy + 20, "slow turn (p95)", 18, 600, WHITE, "end")
        d.text(x0 - 16, by + bh / 2 + 7, "typical turn", 18, 600, WHITE, "end")
    return d


def d4() -> Diagram:
    d = D("D4", "turn-taking-timeline", "One turn, on a timeline", ["3.6", "3.7", "4.4"],
          ["timeline of one turn", "turn-taking", "one turn, on a timeline", "endpointing", "turn detector",
           "interruption", "preemptive"])
    L = 300  # track start
    cy, vy, ry = 270, 362, 700  # caller lane, VAD row, Riley lane
    lane_h = 64
    with d.step(1, "caller speech and VAD"):
        d.text(96, cy + 42, "Caller", 24, 600, WHITE)
        d.text(96, vy + 22, "VAD", 18, 600, GRAY)
        d.text(96, ry + 42, "Riley", 24, 600, TEAL)
        d.add(f'<path d="M{L} {cy + lane_h + 2} H1830" stroke="{GRAY_DARK}" stroke-width="1" opacity="0.5"/>')
        d.add(f'<path d="M{L} {ry + lane_h + 2} H1830" stroke="{GRAY_DARK}" stroke-width="1" opacity="0.5"/>')
        d.node(L, cy, 420, lane_h, "“I'd like to book for…”", tone="white", size=20, weight=500)
        d.node(880, cy, 360, lane_h, "“…Thursday morning.”", tone="white", size=20, weight=500)
        d.bracket(724, 876, cy - 4, "400 ms pause", color=GRAY, size=18)
        for x0, x1, speech in ((L, 720, True), (720, 880, False), (880, 1240, True), (1240, 1830, False)):
            fill = WHITE if speech else NAVY_LIGHT
            d.add(f'<rect x="{x0}" y="{vy}" width="{x1 - x0 - 4}" height="30" rx="4" fill="{fill}" '
                  f'fill-opacity="{0.85 if speech else 1}" stroke="{GRAY_DARK}" stroke-width="1"/>')
            d.text((x0 + x1) / 2, vy + 21, "speech" if speech else "silence", 16, 600, NAVY if speech else GRAY,
                   "middle")
        d.line(L, 930, 1840, 930, color=GRAY, sw=2)
        d.text(1840, 965, "time", 18, 400, GRAY, "end")
    with d.step(2, "turn detection and end-of-utterance delay", ["turn detector", "endpointing", "min_delay"]):
        d.node(610, 420, 380, 84, "Turn detector: unlikely finished", "→ keep waiting", tone="neutral", size=20,
               sub_size=18)
        d.line(800, 416, 800, 398, color=GRAY, sw=2)
        d.node(1250, 420, 380, 84, "Turn detector: likely finished", "→ wait min_delay", tone="teal", size=20,
               sub_size=18, sub_mono=False)
        d.line(1262, 416, 1250, 398, color=TEAL, sw=2)
        # min/max delay brackets, then the end-of-utterance delay
        d.bracket(1240, 1640, 572, "", color=GRAY_DARK, up=True)
        d.bracket(1240, 1330, 572, "", color=GRAY, up=True)
        d.text(1250, 550, "min_delay", 16, 600, GRAY, mono=True)
        d.text(1640, 550, "max_delay", 16, 600, GRAY, "end", mono=True)
        d.bracket(1240, 1420, 640, "end-of-utterance delay", color=AMBER, up=True, size=18)
        d.line(1420, 646, 1420, ry - 6, color=AMBER, sw=2, dash="6 5", arrow=False)
        d.text(1428, ry - 16, "end of turn", 16, 600, AMBER)
    with d.step(3, "Riley answers"):
        d.node(1424, ry, 400, lane_h, "Riley speaks", tone="teal", size=20, align="left")
    with d.step(4, "interruptions", ["interruption", "min_duration", "false interruption"]):
        d.node(1560, cy, 200, lane_h, "“no, wait”", tone="white", size=20, weight=500)
        d.bracket(1560, 1610, cy - 4, "min_duration", color=GRAY, up=True, size=16)
        d.add(f'<rect x="1616" y="{ry - 6}" width="214" height="{lane_h + 12}" fill="{NAVY}"/>')
        d.add(f'<rect x="1424" y="{ry}" width="188" height="{lane_h}" rx="8" fill="none" stroke="{TEAL}" stroke-width="2"/>')
        d.add(f'<rect x="1622" y="{ry}" width="200" height="{lane_h}" rx="8" fill="none" stroke="{TEAL}" '
              f'stroke-width="2" stroke-dasharray="8 4"/>')
        d.pass_dot(1612, ry + lane_h / 2, r=13)
        d.text(1424, ry + lane_h + 34, "✓ agent stops", 18, 600, TEAL)
        d.text(1830, ry + lane_h + 34, "false interruption → resume", 18, 400, GRAY, "end")
    with d.step(5, "preemptive generation", ["preemptive"]):
        d.add(f'<rect x="1300" y="{ry + lane_h + 64}" width="300" height="36" rx="6" fill="none" stroke="{TEAL}" '
              f'stroke-width="2" stroke-dasharray="8 4"/>')
        d.text(1290, ry + lane_h + 89, "preemptive generation", 18, 600, TEAL, "end")
        d.line(1300, ry + lane_h + 62, 1300, ry + lane_h + 4, color=TEAL, sw=1.5, dash="4 4", arrow=False)
    return d


def d5() -> Diagram:
    d = D("D5", "livekit-mental-model", "Rooms, participants, tracks, dispatch", ["3.1", "12.1"],
          ["sfu", "into the room", "livekit mental model", "rooms, participants", "dispatch"])
    sx, sy, sw_, sh = 720, 240, 520, 740
    lanes = [330, 550, 770]
    with d.step(1, "SFU, room and participants"):
        d.rect(sx, sy, sw_, sh, stroke=GRAY, fill=NAVY_LIGHT)
        d.text(sx + sw_ / 2, sy + 44, "LiveKit server (SFU)", 26, 600, WHITE, "middle")
        d.rect(sx + 30, sy + 76, sw_ - 60, sh - 106, stroke=GRAY, fill=NAVY_MID, dash="8 4")
        d.text(sx + 54, sy + 112, "Room", 22, 600, GRAY_LIGHT)
        parts = [("Caller's browser", "white", "person", "caller"), ("Phone via SIP", "white", "phone", "SIP caller"),
                 ("Riley (agent)", "teal", "robot", "Riley")]
        for y, (lab, tone, ic, inner) in zip(lanes, parts):
            d.node(1500, y, 324, 130, lab, None, tone=tone, icon=ic, align="left", size=22)
            d.node(sx + 70, y + 35, sw_ - 140, 60, "participant: " + inner, tone=tone, size=20, weight=500)
            # publish (device -> SFU) and subscribe (SFU -> device)
            d.arrow(1496, y + 45, sx + sw_ - 66, y + 45, color=FLOW)
            d.arrow(sx + sw_ - 66, y + 85, 1496, y + 85, color=FLOW)
        d.text(1376, 296, "publish / subscribe", 18, 400, GRAY, "middle")
    with d.step(2, "tracks", ["tracks", "track"]):
        for y, chip in zip(lanes, ("mic track", "mic track", "Riley's audio track")):
            d.chip(1376, y + 26, chip, "white", size=16, mono=False, anchor="middle")
        d.chip(1376, lanes[2] + 104, "transcript (text)", "gray", size=16, mono=False, anchor="middle")
    with d.step(3, "dispatch", ["dispatch", "agent server", "gets into the room", "entrypoint"]):
        d.node(96, 300, 380, 150, "Agent server", "AgentServer", tone="teal", icon="server", align="left",
               sub_mono=True)
        d.arrow(480, 350, sx - 6, 350, color=TEAL, sw=3)
        d.text(598, 334, "WebSocket: I'm available", 18, 500, TEAL, "middle")
        d.arrow(sx - 6, 410, 480, 410, color=FLOW, dash="8 4")
        d.text(598, 440, "dispatch job", 18, 500, GRAY, "middle")
        d.node(96, 600, 380, 170, "Job process", "@server.rtc_session()\nJobContext → AgentSession",
               tone="teal", sub_mono=True, sub_size=17)
        d.line(286, 454, 286, 596, color=FLOW, sw=2)
        for n, (bx, by) in enumerate(((96, 300), (1500, lanes[0]), (690, 410), (96, 600), (1500, lanes[2])), start=1):
            d.badge(bx, by, n, r=18)
    with d.step(4, "the job is the agent participant", ["job process"]):
        d.elbow([(286, 774), (286, 1010), (1662, 1010), (1662, 904)], color=TEAL, sw=3)
        d.text(980, 998, "the job process is Riley in the room", 18, 600, TEAL, "middle")
    return d


def d6() -> Diagram:
    d = D("D6", "sip-call-flow", "The call path", ["8.1", "8.2", "8.4", "8.5"],
          ["call path", "sip trunk", "pstn", "inbound call", "outbound call", "transfer"])
    w, h, y1 = 236, 130, 300
    xs = [96 + i * (w + 62.4) for i in range(6)]
    with d.step(1, "inbound"):
        d.label(96, y1 - 24, "Inbound", 18, GRAY)
        nodes = [("Caller's phone", "+1 555 01XX", "white", "phone"), ("PSTN", "phone network", "neutral", None),
                 ("Twilio Elastic\nSIP trunk", None, "neutral", None),
                 ("LiveKit SIP", "inbound trunk +\ndispatch rule", "neutral", None),
                 ("Room call-…", None, "ghost", None), ("Riley", "riley-receptionist", "teal", "robot")]
        for i, (lab, sub, tone, ic) in enumerate(nodes):
            d.node(xs[i], y1, w, h, lab, sub, tone=tone, dash="8 4" if tone == "ghost" else None,
                   sub_mono=(i in (0, 5)), size=22, sub_size=17)
        for i in range(5):
            d.arrow(xs[i] + w + 4, y1 + h / 2, xs[i + 1] - 4, y1 + h / 2)
        d.text(xs[2] + w / 2, y1 + h + 32, "8 kHz narrowband audio", 18, 400, GRAY, "middle")
    y2 = 560
    with d.step(2, "transfer", ["transfer", "cold vs warm"]):
        d.label(96, y2 - 24, "Transfer", 18, GRAY)
        d.node(xs[0], y2, w, h, "Front desk phone", "+1 555 01XX", tone="white", icon=None, sub_mono=True, size=22,
               sub_size=17)
        d.elbow([(xs[5] + w / 2, y1 + h + 4), (xs[5] + w / 2, y2 + h / 2), (xs[0] + w + 6, y2 + h / 2)],
                color=TEAL, sw=3)
        for i in (3, 2):
            d.line(xs[i] + w / 2, y1 + h + (48 if i == 2 else 6), xs[i] + w / 2, y2 + h / 2 - 10, color=TEAL,
                   sw=1.5, dash="3 5", arrow=False)
            d.add(f'<circle cx="{xs[i] + w / 2}" cy="{y2 + h / 2}" r="7" fill="{TEAL}"/>')
            d.text(xs[i] + w / 2, y2 + h / 2 + 36, ["", "", "via Twilio", "via LiveKit SIP"][i], 16, 400, GRAY,
                   "middle")
        d.text(xs[4] + w / 2 + 40, y2 + h / 2 - 16, "transfer_sip_participant", 18, 500, TEAL, "middle", mono=True)
    y3 = 820
    with d.step(3, "outbound", ["outbound"]):
        d.label(96, y3 - 24, "Outbound", 18, GRAY)
        nodes3 = [("s08_outbound_call.py", None, "white"), ("LiveKit API", "create SIP participant", "neutral"),
                  ("Outbound trunk", None, "neutral"), ("PSTN", None, "neutral"), ("Patient's phone", "+1 555 01XX", "white")]
        w3, g3 = 300, (1728 - 5 * 300) / 4
        x3 = [96 + i * (w3 + g3) for i in range(5)]
        for i, (lab, sub, tone) in enumerate(nodes3):
            d.node(x3[i], y3, w3, 120, lab, sub, tone=tone, mono=(i == 0), size=20 if i == 0 else 22, sub_size=17,
                   sub_mono=(i == 4))
        for i in range(4):
            d.arrow(x3[i] + w3 + 4, y3 + 60, x3[i + 1] - 4, y3 + 60, color=TEAL, dash="8 4")
    return d


def d7() -> Diagram:
    d = D("D7", "handoff-graph", "Riley's team", ["7.4", "7.5", "7.6"],
          ["riley's team", "handoff graph", "during a handoff", "handoff"])
    gx, gy, gw, gh = 240, 430, 400, 150
    with d.step(1, "the agents"):
        d.node(gx, gy, gw, gh, "GreeterAgent", "greets, answers FAQ, routes", tone="teal", icon="robot",
               glow=True)
        bx = 1080
        d.node(bx, 240, 400, 130, "BookingAgent", "book, reschedule, cancel", tone="teal", icon="robot",
               align="left")
        d.node(bx, 470, 400, 130, "BillingAgent", "insurance, payments, prices", tone="teal", icon="robot",
               align="left")
        d.arrow(gx + gw + 6, gy + 40, bx - 6, 290, color=TEAL, sw=3)
        d.text(800, 336, "handoff", 18, 600, TEAL, "middle")
        d.arrow(gx + gw + 6, gy + 90, bx - 6, 520, color=TEAL, sw=3)
        d.arrow(bx - 6, 340, gx + gw + 6, gy + 62, color=FLOW, sw=1.5)
        d.arrow(bx - 6, 560, gx + gw + 6, gy + 112, color=FLOW, sw=1.5)
        d.text(860, 585, "back to Greeter", 16, 400, GRAY, "middle")
    with d.step(2, "shared userdata", ["callstate", "userdata", "shared"]):
        d.cylinder(240, 860, 1440, 130, "CallState (userdata)", "name, phone, appointment, handoff history",
                   color=GRAY, size=24)
        dot = dict(color=GRAY, sw=2, dash="2 6", arrow=False)
        d.line(gx + gw / 2, gy + gh + 4, gx + gw / 2, 852, **dot)
        d.line(1484, 305, 1600, 305, **dot)
        d.line(1484, 535, 1600, 535, **dot)
        d.line(1600, 305, 1600, 852, **dot)
    with d.step(3, "Lab 5: InsuranceAgent", ["insurance", "lab 5"]):
        d.node(1080, 690, 400, 120, "InsuranceAgent", "Lab 5", tone="teal", dash="8 4", icon="robot",
               align="left")
        d.arrow(gx + gw + 6, gy + 130, 1074, 740, color=TEAL, dash="8 4", sw=2)
        d.line(1484, 750, 1600, 750, color=GRAY, sw=2, dash="2 6", arrow=False)
    return d


def d8() -> Diagram:
    d = D("D8", "voice-testing-pyramid", "The voice testing pyramid", ["9.2", "13.4"],
          ["testing pyramid", "riley's pyramid", "test pyramid"])
    layers = [("Unit tests", "pure Python, no network", "tests/unit/"),
              ("Behavior tests", "text sessions, real LLM", "tests/agent/"),
              ("Evals", "LLM judges, WER, latency budgets", "tests/evals/"),
              ("Simulated calls", "LLM caller vs Riley; LiveKit Simulations", None),
              ("Production monitoring", "metrics, traces, alerts", None)]
    badges = [("fastest", "$", "no", "always"), ("fast", "$$", "yes", "when secrets exist"),
              ("slower", "$$", "yes", "when secrets exist"), ("slow", "$$$", "yes", "scheduled"),
              ("live", "$$$", "yes", "in production")]
    base_l, base_r, lh, gap, bottom = 96, 1176, 124, 10, 990
    inset = 60
    cols = [1260, 1400, 1520, 1670]
    with d.step(1):
        for i, hd in enumerate(("Speed", "Cost", "Needs keys?", "Runs in CI?")):
            d.label(cols[i], 300, hd, 16, GRAY)
    for i, (name, sub, folder) in enumerate(layers):
        with d.step(i + 1, name.lower(), [name.lower()]):
            yb = bottom - i * (lh + gap)
            yt = yb - lh
            l0, r0 = base_l + i * inset, base_r - i * inset
            l1, r1 = l0 + inset * (lh / (lh + gap)), r0 - inset * (lh / (lh + gap))
            d.add(f'<path d="M{l0} {yb} L{l1:.1f} {yt} L{r1:.1f} {yt} L{r0} {yb} Z" fill="{NAVY_LIGHT}" '
                  f'stroke="{TEAL}" stroke-width="2" stroke-linejoin="round"/>')
            cx = (base_l + base_r) / 2
            d.text(cx, yt + 46, f"{i + 1}  {name}", 24, 600, WHITE, "middle")
            d.text(cx, yt + 76, sub, 18, 400, GRAY_LIGHT, "middle")
            if folder:
                d.text(cx, yt + 104, folder, 18, 400, TEAL, "middle", mono=True)
            sp, cost, keys, ci = badges[i]
            ym = yt + lh / 2 + 7
            for j, v in enumerate((sp, cost, keys, ci)):
                d.text(cols[j], ym, v, 18, 400, GRAY)
    with d.step(6, "13.4 overlay: all layers pass", ["run order", "progress", "passes"]):
        for i in range(5):
            yb = bottom - i * (lh + gap)
            r0 = base_r - i * inset
            r1 = r0 - inset * (lh / (lh + gap))
            d.pass_dot((r0 + r1) / 2 - 46, yb - lh / 2, r=15)
    return d


def d9() -> Diagram:
    d = D("D9", "failure-test-map", "Failure → test map", ["9.1", "11.1"],
          ["failure → test map", "failure map", "eight ways voice agents fail"])
    rows = [("Mishearing", "WER eval, audio-in tests", "9.7, 9.13"),
            ("Wrong turn-taking", "EOU delay budget, audio simulations", "9.8, 9.14"),
            ("Talking over callers", "interruption tests (audio), monitoring", "9.14, 10.5"),
            ("Hallucinated availability", "tool-order assertion + mocks", "9.4, 9.5"),
            ("Wrong tool arguments", "argument assertions + state checks", "9.4"),
            ("Missed escalation", "behavior test + judge + simulated caller", "9.4, 9.6, 9.9"),
            ("Latency spikes", "p95 budget in CI", "9.8"),
            ("Prompt injection", "simulated attacker, safety tests", "9.9, 11.5")]
    x = [96, 700, 1560]
    top, rh = 250, 88
    with d.step(1):
        for xx, hd in zip(x, ("Failure", "Primary test", "Lecture")):
            d.label(xx + (70 if xx == 96 else 50 if xx < 1500 else 0), top, hd, 18, GRAY)
        d.add(f'<path d="M96 {top + 22} H1824" stroke="{GRAY_DARK}" stroke-width="2"/>')
    for i, (f, t, lec) in enumerate(rows):
        with d.step(i + 1, f.lower()):
            y = top + 30 + i * rh
            d.rect(96, y + 8, 1728, rh - 12, stroke="none", fill=NAVY_LIGHT if i % 2 == 0 else NAVY_MID, sw=0)
            cy = y + rh / 2 + 2
            d.fail_dot(x[0] + 38, cy, r=13)
            d.text(x[0] + 70, cy + 9, f, 24, 600, WHITE)
            d.pass_dot(x[1] + 20, cy, r=13)
            d.text(x[1] + 50, cy + 8, t, 22, 400, WHITE)
            d.text(x[2], cy + 8, lec, 22, 400, GRAY)
    return d


def d10() -> Diagram:
    d = D("D10", "observability-dashboard", "The five numbers", ["10.5", "10.6", "13.5"],
          ["five numbers", "dashboard", "your one-page report"], footnote="Illustrative values")
    # (label, value, period, series, (axis min, axis max))
    tiles = [("p95 latency", "1.47 s", "per hour", [1.32, 1.38, 1.30, 1.45, 1.36, 1.41, 1.50, 1.39, 1.44, 1.47], (1.0, 1.8)),
             ("Cost/min", "7.7¢", "per day", [7.9, 8.1, 7.8, 7.6, 7.9, 7.7, 7.5, 7.8, 7.6, 7.7], (6.5, 9.0)),
             ("Transfers", "14%", "per day", [15, 17, 14, 16, 13, 15, 14, 16, 13, 14], (8, 22)),
             ("Contained", "71%", "per day", [64, 66, 65, 68, 67, 69, 68, 70, 69, 71], (55, 78)),
             ("Tool failures", "0.4%", "per hour", [0.5, 0.3, 0.6, 0.4, 0.3, 0.5, 0.4, 0.6, 0.3, 0.4], (0, 1.5))]
    tw, gap, ty, th = 320, 32, 390, 400
    for i, (lab, val, per, series, (lo, hi)) in enumerate(tiles):
        with d.step(i + 1, lab.lower()):
            x = 96 + i * (tw + gap)
            d.rect(x, ty, tw, th, stroke=GRAY_DARK, fill=NAVY_LIGHT)
            d.text(x + 28, ty + 52, lab, 22, 600, GRAY_LIGHT)
            d.text(x + 28, ty + 82, per, 16, 400, GRAY)
            d.text(x + 28, ty + 176, val, 64, 700, WHITE)
            sx0, sx1, sy0, sy1 = x + 28, x + tw - 28, ty + 360, ty + 230
            pts = " ".join(f"{sx0 + k * (sx1 - sx0) / (len(series) - 1):.1f},"
                           f"{sy0 - (v - lo) / (hi - lo) * (sy0 - sy1):.1f}" for k, v in enumerate(series))
            d.add(f'<polyline points="{pts}" fill="none" stroke="{TEAL}" stroke-width="3" stroke-linejoin="round"/>')
            if i == 0:
                thy = sy0 - (1.6 - lo) / (hi - lo) * (sy0 - sy1)
                d.add(f'<path d="M{sx0} {thy:.1f} H{sx1}" stroke="{AMBER}" stroke-width="2" stroke-dasharray="8 4"/>')
                d.text(sx1, thy - 10, "1.6 s", 16, 600, AMBER, "end")
    with d.step(6, "alert", ["alert"]):
        x = 96
        d.rect(x, ty, tw, th, stroke=RED, fill="none", sw=3)
        d.fail_dot(x + tw - 34, ty + 40, r=15)
        d.chip(x, ty + th + 30, "ALERT: > 1.6 s for 30 min", "amber", size=18, mono=False)
    return d


def d11() -> Diagram:
    d = D("D11", "trace-anatomy", "One call, as a trace", ["10.3"],
          ["traces for you", "trace anatomy", "as a trace", "waterfall"], footnote="Illustrative timings")
    nx, bx0, bx1, dx = 96, 560, 1640, 1824
    # seconds from call start; the axis shows the first 15 s of a 2 min 10 s call
    spans = [  # (name, depth, start, end, kind, step)
        ("agent_session", 0, 0.0, 15.0, "gray", 1),
        ("user_turn", 1, 0.2, 3.3, "teal", 1),
        ("agent_turn", 1, 3.4, 8.2, "teal", 1),
        ("eou_detection", 2, 3.4, 3.7, "teal", 2),
        ("llm_node", 2, 3.7, 4.6, "teal", 2),
        ("llm_request", 3, 3.7, 4.5, "teal", 2),
        ("function_tool", 2, 4.6, 6.8, "amber", 2),
        ("tts_node", 2, 6.8, 7.9, "teal", 2),
        ("tts_request", 3, 6.8, 7.2, "teal", 2),
        ("user_turn", 1, 8.4, 11.0, "teal", 1),
        ("agent_turn", 1, 11.1, 14.1, "teal", 1),
    ]
    span_s = 15.0
    top, rh = 262, 60
    px = (bx1 - bx0) / span_s
    with d.step(1):
        for t in range(0, 16, 5):
            x = bx0 + t * px
            d.add(f'<path d="M{x:.1f} {top - 6} V{top + len(spans) * rh}" stroke="{GRAY_DARK}" stroke-width="1" '
                  f'stroke-dasharray="2 6" opacity="0.7"/>')
            d.text(x, top - 16, f"{t} s", 16, 400, GRAY, "middle")
    for i, (name, depth, s0, e0, kind, step) in enumerate(spans):
        with d.step(step):
            y = top + i * rh
            d.text(nx + depth * 28, y + 36, name, 20, 500, WHITE if depth < 2 else GRAY_LIGHT, mono=True)
            color = {"gray": GRAY_DARK, "teal": TEAL, "amber": AMBER}[kind]
            x0 = bx0 + s0 * px
            w = max(8, (e0 - s0) * px)
            d.add(f'<rect x="{x0:.1f}" y="{y + 14}" width="{w:.1f}" height="30" rx="4" fill="{color}"/>')
            dur = "2 min 10 s" if i == 0 else f"{e0 - s0:.1f} s"
            d.text(dx, y + 36, dur, 18, 400, GRAY, "end")
            if i == 0:
                d.text(bx1 + 6, y + 37, "→", 20, 600, GRAY)
    with d.step(2):
        d.text(nx + 2 * 28 + 210, top + 6 * rh + 36, "find_available_slots", 18, 400, AMBER, mono=True)
    with d.step(3, "slowest span", ["slowest"]):
        y = top + 6 * rh
        x_end = bx0 + 6.8 * px
        d.arrow(x_end + 130, y + 29, x_end + 12, y + 29, color=AMBER, sw=2)
        d.text(x_end + 140, y + 37, "slowest span", 22, 700, AMBER)
    with d.step(1):
        d.text(nx, top + len(spans) * rh + 40, "room name call-… links trace, logs and metrics", 18, 400, GRAY)
    return d


def d12() -> Diagram:
    d = D("D12", "threat-model", "Five threats, layered defences", ["11.1"],
          ["threat model", "layered model", "five threats"])
    my, mh = 470, 140
    with d.step(1, "spoken injection", ["spoken prompt injection", "injection"]):
        d.node(96, my, 250, mh, "Caller", "anyone with the number", tone="red", icon="person", icon_color=RED)
        d.node(470, my, 190, mh, "STT", tone="neutral")
        d.node(800, my, 260, mh, "Riley (LLM)", tone="teal", icon="brain")
        d.node(1300, my, 200, mh, "Tools", tone="white", icon="wrench")
        d.cylinder(1600, my - 10, 224, mh + 20, "Scheduler", "patient data", color=GRAY, size=22)
        d.arrow(350, my + mh / 2, 466, my + mh / 2)
        d.arrow(664, my + mh / 2, 796, my + mh / 2)
        d.arrow(1064, my + mh / 2, 1296, my + mh / 2)
        d.arrow(1504, my + mh / 2, 1596, my + mh / 2)
        # the shield line at the tool boundary
        d.line(1180, 300, 1180, 840, color=RED, sw=3, dash="10 6", arrow=False)
        d.icon("shield", 1180, 270, 52, RED)
        d.chip(408, my - 64, "1 spoken injection", "red", size=18, mono=False, anchor="middle")
        d.line(408, my - 30, 408, my + mh / 2 - 6, color=RED, sw=1.5, dash="3 4", arrow=False)
    with d.step(2, "social engineering", ["social engineering"]):
        d.chip(730, my - 64, "2 social engineering", "red", size=18, mono=False, anchor="middle")
        d.line(730, my - 30, 730, my + mh / 2 - 6, color=RED, sw=1.5, dash="3 4", arrow=False)
    with d.step(3, "exfiltration via tools", ["exfiltration"]):
        d.chip(1180, my + mh + 30, "3 exfiltration via tools", "red", size=18, mono=False, anchor="middle")
    with d.step(4, "toll fraud", ["toll fraud"]):
        d.node(1300, 790, 260, 110, "Transfer / dial", tone="white")
        d.arrow(1400, my + mh + 4, 1400, 786)
        d.chip(1418, 684, "4 toll fraud", "red", size=18, mono=False)
    with d.step(5, "voice cloning", ["voice cloning", "impersonation"]):
        d.chip(221, my + mh + 30, "5 voice cloning", "red", size=18, mono=False, anchor="middle")
    with d.step(6, "defences", ["defence", "defense", "where each layer", "layered"]):
        cy = 300
        for k, lab in enumerate(("identity check in code", "least-privilege tools", "allow-listed transfer target")):
            d.chip(1220, cy - 40 + k * 52, lab, "teal", size=18, mono=False)
        d.node(800, 830, 260, 110, "Logs and traces", tone="neutral")
        d.node(820, 690, 220, 64, "PII redaction", tone="teal", size=20)
        d.line(930, my + mh + 4, 930, 684, color=FLOW)
        d.line(930, 758, 930, 826, color=TEAL)
    return d


def d13() -> Diagram:
    d = D("D13", "agent-server-scaling", "The agent server", ["12.1", "12.4"],
          ["agent server", "job process", "draining", "load threshold", "prewarm"])
    with d.step(1, "jobs and warm processes"):
        d.node(96, 260, 330, 140, "LiveKit", "Cloud or self-hosted", tone="neutral", icon="cloud", align="left")
        d.node(700, 260, 520, 140, "Agent server", "main process", tone="teal", icon="server", align="left",
               glow=True)
        d.arrow(430, 310, 696, 310, color=FLOW, both=True)
        d.text(563, 296, "WebSocket (outbound)", 18, 500, GRAY, "middle")
        d.arrow(430, 370, 696, 370, color=FLOW, dash="8 4")
        d.text(480, 400, "new job", 18, 500, GRAY, "middle")
        bw, gap, by = 320, 32, 520
        xs = [96 + i * (bw + gap) for i in range(5)]
        for i, x in enumerate(xs):
            if i < 3:
                d.node(x, by, bw, 130, "job process", "one call", tone="teal", icon="phone", align="left", size=22)
            else:
                d.node(x, by, bw, 130, "idle warm process", "setup_fnc (prewarm)", tone="gray", sub_mono=True,
                       size=22, sub_size=16)
            d.line(960, 404, x + bw / 2, by - 6, color=FLOW, sw=1.5)
        d.text(xs[3] + bw + gap / 2, by + 170, "num_idle_processes", 18, 500, GRAY, "middle", mono=True)
    with d.step(2, "load threshold", ["load", "threshold"]):
        cx, cy, r = 280, 900, 120
        d.add(f'<path d="M{cx - r} {cy} A{r} {r} 0 0 1 {cx + r} {cy}" fill="none" stroke="{GRAY_DARK}" stroke-width="16"/>')
        ang = 3.14159 * (1 - 0.7)
        import math
        ex, ey = cx + r * math.cos(ang), cy - r * math.sin(ang)
        d.add(f'<path d="M{cx - r} {cy} A{r} {r} 0 0 1 {ex:.1f} {ey:.1f}" fill="none" stroke="{TEAL}" stroke-width="16"/>')
        d.add(f'<path d="M{cx + (r - 26) * math.cos(ang):.1f} {cy - (r - 26) * math.sin(ang):.1f} L{cx + (r + 26) * math.cos(ang):.1f} '
              f'{cy - (r + 26) * math.sin(ang):.1f}" stroke="{AMBER}" stroke-width="4"/>')
        d.text(cx, cy - 20, "load", 22, 600, WHITE, "middle")
        d.text(ex + 34, ey - 26, "0.7  load_threshold", 18, 600, AMBER, mono=True)
        d.text(cx + r + 30, cy - 4, "past it: stops accepting new jobs", 18, 400, GRAY)
    with d.step(3, "memory warning", ["memory"]):
        d.chip(96 + 352 + 10, 520 + 150, "job_memory_warn_mb 1000 MB", "amber", size=16)
    with d.step(4, "draining on deploy", ["draining", "sigterm", "deploy"]):
        d.add(f'<path d="M548 356 L584 384 M584 356 L548 384" stroke="{GRAY}" stroke-width="4" stroke-linecap="round"/>')
        d.node(1060, 820, 764, 130, "SIGTERM → draining", "live calls finish, no new jobs", tone="amber", size=26)
        d.text(1442, 990, "drain_timeout 3600 s", 18, 500, GRAY, "middle", mono=True)
    return d


def d14() -> Diagram:
    d = D("D14", "capstone-architecture", "Riley in production", ["13.1", "13.2"],
          ["capstone-riley", "riley in production", "capstone architecture"])
    with d.step(1, "callers"):
        d.node(96, 240, 330, 76, "Phone", tone="white", icon="phone", icon_size=34, align="left", size=22)
        d.node(96, 350, 330, 76, "Twilio SIP trunk", tone="neutral", size=22)
        d.node(96, 460, 330, 110, "LiveKit SIP +\ndispatch rule", "riley-receptionist", tone="neutral",
               sub_mono=True, size=22, sub_size=16)
        d.node(96, 640, 330, 76, "Web user", tone="white", icon="person", icon_size=34, align="left", size=22)
        d.node(96, 750, 330, 76, "WebRTC", tone="neutral", size=22)
        for a, b in ((316, 350), (426, 460)):
            d.arrow(261, a + 4, 261, b - 4)
        d.arrow(261, 716 + 4, 261, 750 - 4)
        d.node(500, 520, 150, 120, "Room", tone="ghost", dash="8 4", size=22)
        d.arrow(430, 515, 496, 560)
        d.arrow(430, 788, 496, 610)
    with d.step(2, "agent server"):
        d.rect(720, 230, 640, 540, stroke=TEAL, fill=NAVY_MID)
        d.text(745, 272, "Agent server (Docker, start)", 22, 600, TEAL)
        d.rect(745, 300, 590, 100, stroke=GRAY, fill=NAVY_LIGHT)
        d.text(765, 338, "AgentSession", 20, 600, WHITE, mono=True)
        d.text(765, 370, "VAD + turn detector + STT → LLM → TTS", 17, 400, GRAY_LIGHT)
        d.text(1315, 338, "fallbacks + conn_options", 16, 400, GRAY, "end", mono=True)
        d.arrow(654, 580, 716, 580, color=TEAL, sw=3)
    with d.step(3, "agents and tools"):
        d.node(745, 440, 280, 110, "Riley", "front desk + booking,\nguardrails", tone="teal", size=22, sub_size=16)
        d.node(1060, 440, 275, 110, "Billing specialist", tone="teal", size=20)
        d.arrow(1029, 495, 1056, 495, color=TEAL, both=True)
        d.cylinder(745, 600, 590, 100, "CallState", None, color=GRAY, size=22)
        d.line(885, 554, 885, 596, color=GRAY, dash="2 6", arrow=False)
        d.line(1197, 554, 1197, 596, color=GRAY, dash="2 6", arrow=False)
        d.node(1440, 240, 384, 76, "Tools", tone="white", icon="wrench", icon_size=34, align="left", size=22)
        d.cylinder(1440, 350, 384, 130, "src/maple", "scheduler, knowledge, pii, costs", color=GRAY, size=22)
        d.node(1440, 520, 384, 100, "Transfer → front desk", "config number only", tone="white", size=20)
        d.arrow(1364, 280, 1436, 280)
        d.arrow(1632, 320, 1632, 346)
        d.arrow(1364, 570, 1436, 570)
    with d.step(4, "telemetry"):
        d.node(1440, 640, 384, 170, "Telemetry", "metrics JSONL, usage and cost,\nOpenTelemetry → Langfuse\n(redacted)",
               tone="amber", icon="trace", icon_color=AMBER, size=22, sub_size=16, align="left", icon_size=36)
        d.arrow(1364, 725, 1436, 725, color=AMBER)
    with d.step(5, "CI"):
        d.rect(96, 880, 1728, 110, stroke=TEAL, fill=NAVY_LIGHT)
        d.icon("infinity", 150, 935, 52, TEAL)
        d.text(200, 930, "CI", 24, 700, TEAL)
        d.text(200, 962, "gates every deploy", 16, 400, GRAY)
        stages = ["unit", "behavior", "evals", "simulated callers"]
        x = 420
        for k, st in enumerate(stages):
            w = d.chip(x, 914, st, "teal", size=20, mono=False)
            end = x + w
            if k < 3:
                d.arrow(end + 8, 932, end + 60, 932, color=TEAL)
            x += w + 70
        d.arrow(end + 8, 932, 1620, 932, color=TEAL)
        d.text(1630, 940, "deploy", 22, 600, WHITE)
    return d


def d15() -> Diagram:
    d = D("D15", "pipecat-frame-pipeline", "Frames through a pipeline", ["14.1", "14.2"],
          ["processors and the pipeline", "frame", "pipecat", "pipeline"],
          footnote="1.12 names; older tutorials: PipelineTask, PipelineRunner")
    procs = [("transport\n.input()", None, "neutral"), ("stt", "DeepgramSTTService", "neutral"),
             ("user\naggregator", None, "neutral"), ("llm", "OpenAILLMService", "teal"),
             ("tts", "CartesiaTTSService", "neutral"), ("transport\n.output()", None, "neutral"),
             ("assistant\naggregator", None, "neutral")]
    w, gap, y, h = 180, 52, 520, 140
    x0 = 96 + (1728 - (7 * w + 6 * gap)) / 2
    xs = [x0 + i * (w + gap) for i in range(7)]
    with d.step(1, "processors"):
        for i, (lab, sub, tone) in enumerate(procs):
            d.node(xs[i], y, w, h, lab, sub, tone=tone, mono=True, size=20, sub_mono=True, sub_size=14)
        for i in range(6):
            d.arrow(xs[i] + w + 4, y + h / 2, xs[i + 1] - 4, y + h / 2)
    with d.step(2, "frames", ["frames", "frame"]):
        chips = ["AudioRawFrame", "TranscriptionFrame", "LLM context", "TextFrame", "TTSAudioRawFrame"]
        for i, c in enumerate(chips):
            mx = xs[i] + w + gap / 2
            cy = y - 62 if i % 2 == 0 else y - 112
            d.chip(mx, cy, c, "white" if c != "LLM context" else "teal", size=16, mono=True, anchor="middle")
            d.line(mx, cy + 30, mx, y + h / 2 - 8, color=GRAY_DARK, sw=1.5, dash="3 4", arrow=False)
        d.cylinder(xs[2] + w / 2 - 20, 750, xs[6] - xs[2] + 40, 84, "LLMContext", None, color=GRAY, size=20)
        d.line(xs[2] + w / 2, y + h + 4, xs[2] + w / 2, 746, color=GRAY, dash="2 6", arrow=False)
        d.line(xs[6] + w / 2, y + h + 4, xs[6] + w / 2, 746, color=GRAY, dash="2 6", arrow=False)
    with d.step(3, "containers", ["pipelineworker", "workerrunner", "worker and runner"]):
        L, Rr = xs[0], xs[6] + w
        d.rect(L - 24, 350, Rr - L + 48, 340, stroke=TEAL, fill="none", dash="8 4")
        d.text(L - 8, 340, "Pipeline", 20, 600, TEAL, mono=True)
        d.rect(L - 50, 290, Rr - L + 100, 580, stroke=GRAY, fill="none")
        d.text(L - 34, 280, "PipelineWorker (PipelineParams)", 20, 600, GRAY_LIGHT, mono=True)
        d.rect(L - 76, 230, Rr - L + 152, 690, stroke=GRAY_DARK, fill="none")
        d.text(L - 60, 220, "WorkerRunner", 20, 600, GRAY, mono=True)
    return d


def d16() -> Diagram:
    d = D("D16", "build-vs-buy-matrix", "Build vs buy", ["14.3"], ["build vs buy"])
    cols = ["Framework, self-hosted", "Framework, managed hosting", "Managed platform"]
    rows = [("Time to first call", "Slowest", "Medium", "Fastest"),
            ("Pipeline control", "Full", "Full", "Limited to exposed options"),
            ("Cost at low volume", "Engineering time dominates", "Engineering time dominates", "Usually lowest total"),
            ("Cost at high volume", "Usually lowest per minute", "Low to medium", "Platform fee adds up"),
            ("Compliance control", "You own it all", "Shared with the host", "Depends on the vendor"),
            ("Lock-in", "Lowest", "Low", "Highest"),
            ("Testing depth", "Anything you build", "Anything you build", "Limited to what the platform exposes")]
    x = [96, 420, 900, 1370]
    top, rh = 240, 86
    with d.step(1):
        for i, c in enumerate(cols):
            d.text(x[i + 1], top, c, 22, 700, TEAL)
        d.text(x[1], top + 30, "LiveKit Agents, Pipecat", 17, 400, GRAY)
        d.text(x[2], top + 30, "LiveKit Agents, Pipecat", 17, 400, GRAY)
        d.text(x[3], top + 30, "Vapi, Retell, ElevenLabs Agents, Bland", 17, 400, GRAY)
    for r, (name, *vals) in enumerate(rows):
        with d.step(r + 1, name.lower()):
            y = top + 60 + r * rh
            d.rect(96, y, 1728, rh - 10, stroke="none", fill=NAVY_LIGHT if r % 2 == 0 else NAVY_MID, sw=0)
            d.text(x[0] + 20, y + rh / 2 + 3, name, 21, 600, WHITE)
            for i, v in enumerate(vals):
                lines = [v] if text_width(v, 20) < 440 else [v[: v.rfind(" ", 0, 28)], v[v.rfind(" ", 0, 28) + 1:]]
                for k, ln in enumerate(lines):
                    d.text(x[i + 1], y + rh / 2 + 3 - (len(lines) - 1) * 12 + k * 24, ln, 20, 400, WHITE)
    return d


ALL = [d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12, d13, d14, d15, d16]


def main(argv: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    index = {"course": COURSE, "generated_by": "10-graphics/diagrams/_src/build_diagrams.py", "diagrams": {}}
    for fn in ALL:
        d = fn()
        entry = d.save(OUT)
        if d.id == "D2":
            entry["steps"]["5"] = d2_zoom(OUT)
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
