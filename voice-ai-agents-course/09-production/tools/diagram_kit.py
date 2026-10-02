"""Small SVG authoring kit for the course master diagrams (10-graphics/design-system.md).

Each course keeps its diagram definitions in ``10-graphics/diagrams/_src/build_diagrams.py``; those scripts
place every node by hand and use this kit only for consistent styling: palette, type, 8 px rounded nodes,
2 px edges with chevron arrowheads, icons, numbered callouts and progressive build steps.

Conventions
-----------
* Canvas 1920x1080, Deep Navy background. Title band is y < 200 and lives in ``<g id="diagram-title">`` so
  slide_builder.py can hide it when the slide already has a title. Diagram content stays inside
  x 80..1840, y 210..1030.
* Build steps: wrap elements in ``with d.step(n):`` (visible from step n on) or ``with d.only(n, m):``
  (visible only in those steps). ``d.save(dir, steps=k)`` writes the master plus ``D{n}-step{i}.svg``.
"""
from __future__ import annotations

import contextlib
import html
import math
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

NAVY = "#0A1628"
NAVY_LIGHT = "#1A2742"
NAVY_MID = "#0F1E35"
TEAL = "#00D4AA"
TEAL_DIM = "#00A885"
TEAL_GLOW = "#00D4AA33"
RED = "#FF4B4B"
AMBER = "#FFB020"
GRAY = "#94A3B8"
GRAY_DARK = "#64748B"
GRAY_LIGHT = "#CBD5E1"
WHITE = "#FFFFFF"
FLOW = "#FFFFFF99"  # data flow, white 60 %

FONT = "Inter, 'Inter var', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace"

TONES = {
    "teal": (TEAL, NAVY_LIGHT),
    "neutral": (GRAY, NAVY_LIGHT),
    "white": (WHITE, NAVY_LIGHT),
    "red": (RED, NAVY_LIGHT),
    "amber": (AMBER, NAVY_LIGHT),
    "gray": (GRAY_DARK, NAVY_MID),
    "ghost": (GRAY_DARK, "none"),
}
ARROW_COLORS = {"flow": FLOW, "teal": TEAL, "red": RED, "amber": AMBER, "gray": GRAY_DARK, "white": WHITE}


# ------------------------------------------------------------------------------------------
# text measurement (Pillow + installed Inter when available, otherwise an average-width estimate)
# ------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _font_file(family: str, weight: int) -> str | None:
    if not shutil.which("fc-match"):
        return None
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", f"{family}:weight={weight_to_fc(weight)}"],
                             capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return None
    return out if out and family.split()[0].lower() in out.lower() else None


def weight_to_fc(w: int) -> int:
    return {400: 80, 500: 100, 600: 180, 700: 200}.get(w, 80)


@lru_cache(maxsize=None)
def _pil_font(family: str, weight: int, size: int):
    path = _font_file(family, weight)
    if not path:
        return None
    try:
        from PIL import ImageFont  # type: ignore

        return ImageFont.truetype(path, size)
    except Exception:
        return None


def text_width(s: str, size: float, weight: int = 400, mono: bool = False) -> float:
    fam = "JetBrains Mono" if mono else "Inter"
    f = _pil_font(fam, weight, int(round(size)))
    if f is not None:
        return float(f.getlength(s))
    ratio = 0.6 if mono else {400: 0.53, 500: 0.55, 600: 0.57, 700: 0.59}.get(weight, 0.55)
    return len(s) * size * ratio


def wrap(s: str, width: float, size: float, weight: int = 400, mono: bool = False) -> list[str]:
    words = s.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, size, weight, mono) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


# ------------------------------------------------------------------------------------------
# icons (48 x 48 unit box, stroke-based)
# ------------------------------------------------------------------------------------------
def _icon_body(name: str, color: str) -> str:
    st = f'fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'
    fl = f'fill="{color}"'
    if name == "person":
        return f'<circle cx="24" cy="15" r="8" {st}/><path d="M8 43 C8 31 15 27 24 27 C33 27 40 31 40 43" {st}/>'
    if name == "robot":
        return (f'<rect x="9" y="15" width="30" height="24" rx="7" {st}/><circle cx="19" cy="27" r="3.2" {fl}/>'
                f'<circle cx="29" cy="27" r="3.2" {fl}/><path d="M24 15 V8" {st}/><circle cx="24" cy="6.5" r="2.6" {fl}/>'
                f'<path d="M5 24 V31 M43 24 V31" {st}/>')
    if name == "brain":
        pts = [(9, 14), (9, 34), (24, 8), (24, 24), (24, 40), (39, 16), (39, 32)]
        edges = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (3, 5), (3, 6), (4, 6), (0, 4), (2, 6)]
        lines = "".join(f'<path d="M{pts[a][0]} {pts[a][1]} L{pts[b][0]} {pts[b][1]}" fill="none" stroke="{color}" '
                        f'stroke-width="1.6" stroke-opacity="0.7"/>' for a, b in edges)
        dots = "".join(f'<circle cx="{x}" cy="{y}" r="4" {fl}/>' for x, y in pts)
        return lines + dots
    if name == "wrench":
        return (f'<path d="M37.5 9.5 A9 9 0 1 0 38.5 22.5" {st} stroke-width="4"/>'
                f'<path d="M26 22 L9 39" {st} stroke-width="6"/>')
    if name == "database":
        return (f'<ellipse cx="24" cy="11" rx="15" ry="5.5" {st}/><path d="M9 11 V37 A15 5.5 0 0 0 39 37 V11" {st}/>'
                f'<path d="M9 24 A15 5.5 0 0 0 39 24" {st}/>')
    if name == "shield":
        return f'<path d="M24 5 L40 11 V23 C40 33 33 40 24 44 C15 40 8 33 8 23 V11 Z" {st}/><path d="M17 24 L22 29 L31 19" {st}/>'
    if name == "clipboard":
        return (f'<rect x="10" y="9" width="28" height="35" rx="4" {st}/><rect x="18" y="5" width="12" height="7" rx="2" {st}/>'
                f'<path d="M17 28 L22 33 L32 21" {st}/>')
    if name == "trace":
        return (f'<rect x="5" y="9" width="22" height="7" rx="2" {fl}/><rect x="13" y="20.5" width="24" height="7" rx="2" {fl}/>'
                f'<rect x="22" y="32" width="20" height="7" rx="2" {fl}/>')
    if name == "infinity":
        return f'<path d="M24 24 C18 13 5 13 5 24 C5 35 18 35 24 24 C30 13 43 13 43 24 C43 35 30 35 24 24 Z" {st}/>'
    if name == "bars":
        return (f'<rect x="7" y="27" width="8" height="15" rx="1.5" {fl}/><rect x="20" y="17" width="8" height="25" rx="1.5" {fl}/>'
                f'<rect x="33" y="8" width="8" height="34" rx="1.5" {fl}/>')
    if name == "phone":
        return (f'<rect x="14" y="4" width="20" height="40" rx="4" {st}/><path d="M21 38 H27" {st}/>')
    if name == "wave":
        hs = [8, 18, 30, 20, 34, 16, 24, 10]
        return "".join(f'<path d="M{5 + i * 5.4:.1f} {24 - h / 2} V{24 + h / 2}" {st}/>' for i, h in enumerate(hs))
    if name == "gauge":
        return (f'<path d="M7 34 A17 17 0 0 1 41 34" {st}/><path d="M24 34 L33 21" {st}/><circle cx="24" cy="34" r="3" {fl}/>')
    if name == "server":
        return (f'<rect x="7" y="8" width="34" height="13" rx="3" {st}/><rect x="7" y="27" width="34" height="13" rx="3" {st}/>'
                f'<circle cx="14" cy="14.5" r="2" {fl}/><circle cx="14" cy="33.5" r="2" {fl}/>')
    if name == "cloud":
        return f'<path d="M14 37 H36 A8 8 0 0 0 36 21 A11 11 0 0 0 15 19 A9 9 0 0 0 14 37 Z" {st}/>'
    if name == "doc":
        return (f'<path d="M12 5 H29 L37 13 V43 H12 Z" {st}/><path d="M18 21 H31 M18 28 H31 M18 35 H26" {st}/>')
    if name == "clock":
        return f'<circle cx="24" cy="24" r="17" {st}/><path d="M24 14 V24 L31 29" {st}/>'
    if name == "bell":
        return (f'<path d="M12 35 V23 A12 12 0 0 1 36 23 V35 L39 38 H9 Z" {st}/><path d="M20 42 A4 4 0 0 0 28 42" {st}/>')
    if name == "lock":
        return f'<rect x="10" y="21" width="28" height="21" rx="4" {st}/><path d="M16 21 V15 A8 8 0 0 1 32 15 V21" {st}/>'
    if name == "eye":
        return f'<path d="M4 24 C11 13 37 13 44 24 C37 35 11 35 4 24 Z" {st}/><circle cx="24" cy="24" r="5" {fl}/>'
    if name == "check":
        return f'<path d="M9 25 L20 35 L39 13" {st} stroke-width="4.5"/>'
    if name == "cross":
        return f'<path d="M12 12 L36 36 M36 12 L12 36" {st} stroke-width="4.5"/>'
    if name == "warning":
        return f'<path d="M24 6 L44 41 H4 Z" {st}/><path d="M24 19 V29" {st}/><circle cx="24" cy="35" r="2.2" {fl}/>'
    if name == "coin":
        return f'<circle cx="24" cy="24" r="17" {st}/><path d="M29 17 H21.5 A3.5 3.5 0 0 0 21.5 24 H26.5 A3.5 3.5 0 0 1 26.5 31 H18 M24 13 V35" {st}/>'
    if name == "loop":
        return f'<path d="M38 17 A16 16 0 1 0 40 28" {st}/><path d="M39 8 V18 H29" {st}/>'
    if name == "git":
        return (f'<circle cx="14" cy="11" r="4.5" {st}/><circle cx="14" cy="37" r="4.5" {st}/><circle cx="34" cy="20" r="4.5" {st}/>'
                f'<path d="M14 15.5 V32.5 M14 28 C14 22 34 28 34 24.5" {st}/>')
    if name == "skull":
        return (f'<path d="M10 22 A14 14 0 0 1 38 22 V31 H33 V38 H15 V31 H10 Z" {st}/><circle cx="18" cy="23" r="3.5" {fl}/>'
                f'<circle cx="30" cy="23" r="3.5" {fl}/>')
    raise KeyError(name)


# ------------------------------------------------------------------------------------------
# Diagram
# ------------------------------------------------------------------------------------------
class Diagram:
    def __init__(self, did: str, slug: str, title: str, subtitle: str = "", course: str = "",
                 lectures: list[str] | None = None, keywords: list[str] | None = None, spec: str = "",
                 title_size: int = 40, footnote: str = "") -> None:
        self.id = did
        self.slug = slug
        self.title = title
        self.subtitle = subtitle
        self.course = course
        self.lectures = lectures or []
        self.keywords = keywords or []
        self.spec = spec
        self.title_size = title_size
        self.footnote = footnote
        self.items: list[tuple[tuple, str]] = []  # (visibility, svg)
        self._vis: tuple = ("from", 1)
        self.step_keywords: dict[int, list[str]] = {}
        self.step_labels: dict[int, str] = {}
        self.warnings: list[str] = []

    # visibility --------------------------------------------------------------------------
    @contextlib.contextmanager
    def step(self, n: int, label: str = "", keywords: list[str] | None = None):
        prev = self._vis
        self._vis = ("from", n)
        if label:
            self.step_labels[n] = label
        if keywords:
            self.step_keywords[n] = keywords
        try:
            yield
        finally:
            self._vis = prev

    @contextlib.contextmanager
    def only(self, *steps: int):
        prev = self._vis
        self._vis = ("only", tuple(steps))
        try:
            yield
        finally:
            self._vis = prev

    def add(self, svg: str) -> None:
        self.items.append((self._vis, svg))

    # primitives ---------------------------------------------------------------------------
    def rect(self, x, y, w, h, stroke=GRAY_DARK, fill=NAVY_LIGHT, sw=2, rx=8, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}{o}/>')

    def glow(self, x, y, w, h, color=TEAL_GLOW, spread=10, rx=14):
        self.add(f'<rect x="{x - spread / 2}" y="{y - spread / 2}" width="{w + spread}" height="{h + spread}" '
                 f'rx="{rx}" fill="none" stroke="{color}" stroke-width="{spread}"/>')

    def text(self, x, y, s, size=24, weight=400, color=WHITE, anchor="start", mono=False, italic=False,
             spacing=None, opacity=None):
        fam = MONO if mono else FONT
        it = ' font-style="italic"' if italic else ""
        ls = f' letter-spacing="{spacing}"' if spacing is not None else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
                 f'fill="{color}" text-anchor="{anchor}"{it}{ls}{o}>{esc(s)}</text>')

    def lines(self, x, y, lines, size=24, weight=400, color=WHITE, anchor="start", mono=False, lh=1.3):
        for i, s in enumerate(lines):
            self.text(x, y + i * size * lh, s, size, weight, color, anchor, mono)

    def label(self, x, y, s, size=18, color=GRAY, anchor="start", weight=600):
        """All-caps label with +0.5 px tracking."""
        self.text(x, y, s.upper(), size, weight, color, anchor, spacing=0.5)

    def line(self, x1, y1, x2, y2, color=FLOW, sw=2, dash=None, arrow=True, start_arrow=False):
        self.path(f"M{x1} {y1} L{x2} {y2}", color, sw, dash, arrow, start_arrow)

    def path(self, d, color=FLOW, sw=2, dash=None, arrow=True, start_arrow=False, fill="none"):
        key = next((k for k, v in ARROW_COLORS.items() if v == color), "flow")
        m = f' marker-end="url(#arr-{key})"' if arrow else ""
        ms = f' marker-start="url(#arr-{key})"' if start_arrow else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{da}{m}{ms}/>')

    def arrow(self, x1, y1, x2, y2, color=FLOW, sw=2, dash=None, label=None, label_pos=0.5, label_dy=-12,
              label_color=GRAY, label_size=18, label_mono=False, both=False):
        self.line(x1, y1, x2, y2, color, sw, dash, True, both)
        if label:
            lx = x1 + (x2 - x1) * label_pos
            ly = y1 + (y2 - y1) * label_pos + label_dy
            self.text(lx, ly, label, label_size, 500, label_color, "middle", mono=label_mono)

    def elbow(self, pts, color=FLOW, sw=2, dash=None, arrow=True, radius=12):
        """Orthogonal polyline with rounded corners."""
        d = f"M{pts[0][0]} {pts[0][1]}"
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
            l1 = math.hypot(x1 - x0, y1 - y0)
            l2 = math.hypot(x2 - x1, y2 - y1)
            r = min(radius, l1 / 2, l2 / 2)
            ax = x1 - (x1 - x0) / l1 * r
            ay = y1 - (y1 - y0) / l1 * r
            bx = x1 + (x2 - x1) / l2 * r
            by = y1 + (y2 - y1) / l2 * r
            d += f" L{ax:.1f} {ay:.1f} Q{x1} {y1} {bx:.1f} {by:.1f}"
        d += f" L{pts[-1][0]} {pts[-1][1]}"
        self.path(d, color, sw, dash, arrow)

    def icon(self, name, cx, cy, size=48, color=WHITE):
        s = size / 48
        self.add(f'<g transform="translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.3f})">'
                 f'{_icon_body(name, color)}</g>')

    def node(self, x, y, w, h, label, sub=None, tone="neutral", icon=None, icon_color=None, size=24, sub_size=18,
             weight=600, glow=False, dash=None, sw=2, mono=False, sub_mono=False, align="center", sub_color=GRAY_LIGHT,
             label_color=WHITE, icon_size=44):
        stroke, fill = TONES[tone]
        if glow:
            self.glow(x, y, w, h)
        self.rect(x, y, w, h, stroke=stroke, fill=fill, sw=sw, dash=dash)
        label_lines = label.split("\n") if label else []
        sub_lines = sub.split("\n") if sub else []
        if icon and align == "center" and h >= 120:
            # icon on top, text below
            block = icon_size + 12 + len(label_lines) * size * 1.2 + (len(sub_lines) * sub_size * 1.3 + 6 if sub_lines else 0)
            top = y + (h - block) / 2
            self.icon(icon, x + w / 2, top + icon_size / 2, icon_size, icon_color or stroke_or_white(stroke))
            ty = top + icon_size + 12 + size * 0.95
            tx = x + w / 2
            anchor = "middle"
        elif icon:
            self.icon(icon, x + 22 + icon_size / 2, y + h / 2, icon_size, icon_color or stroke_or_white(stroke))
            block = len(label_lines) * size * 1.2 + (len(sub_lines) * sub_size * 1.3 + 4 if sub_lines else 0)
            ty = y + (h - block) / 2 + size * 0.95
            tx = x + 22 + icon_size + 16
            anchor = "start"
            self._check_fit(label_lines, size, weight, mono, w - (icon_size + 60), label)
        else:
            block = len(label_lines) * size * 1.2 + (len(sub_lines) * sub_size * 1.3 + 6 if sub_lines else 0)
            ty = y + (h - block) / 2 + size * 0.95
            tx = x + w / 2 if align == "center" else x + 22
            anchor = "middle" if align == "center" else "start"
        if not (icon and align != "center"):
            self._check_fit(label_lines, size, weight, mono, w - 28, label)
        for i, ln in enumerate(label_lines):
            self.text(tx, ty + i * size * 1.2, ln, size, weight, label_color, anchor, mono=mono)
        sy = ty + (len(label_lines) - 1) * size * 1.2 + sub_size * 1.45 + 2
        for i, ln in enumerate(sub_lines):
            self._check_fit([ln], sub_size, 400, sub_mono, w - 28 if not (icon and align != "center") else w - (icon_size + 60), sub)
            self.text(tx, sy + i * sub_size * 1.3, ln, sub_size, 400, sub_color, anchor, mono=sub_mono)
        if label_lines or sub_lines:
            bottom = sy + (len(sub_lines) - 1) * sub_size * 1.3 if sub_lines else ty + (len(label_lines) - 1) * size * 1.2
            if bottom > y + h - 4:
                self.warnings.append(f"{self.id}: text overflows node height: {label!r}")

    def _check_fit(self, lines, size, weight, mono, avail, label):
        for ln in lines:
            if text_width(ln, size, weight, mono) > avail:
                self.warnings.append(f"{self.id}: '{ln}' ({text_width(ln, size, weight, mono):.0f}px) > {avail:.0f}px")

    def chip(self, x, y, s, tone="teal", size=18, mono=True, h=None, pad=14, filled=False, anchor="start"):
        """Pill chip; returns its width."""
        color = {"teal": TEAL, "red": RED, "amber": AMBER, "gray": GRAY, "white": WHITE}[tone]
        w = text_width(s, size, 500, mono) + 2 * pad
        h = h or size * 1.8
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        fill = color if filled else NAVY_MID
        self.add(f'<rect x="{x0:.1f}" y="{y}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{fill}" '
                 f'stroke="{color}" stroke-width="2"/>')
        self.text(x0 + w / 2, y + h / 2 + size * 0.36, s, size, 500, NAVY if filled else color, "middle", mono=mono)
        return w

    def badge(self, cx, cy, n, r=20, color=TEAL):
        """Numbered callout circle (K4)."""
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')
        self.text(cx, cy + r * 0.38, str(n), int(r * 1.05), 700, NAVY, "middle")

    def fail_dot(self, cx, cy, r=14):
        """Red failure badge with a cross glyph (never colour alone)."""
        k = r * 0.42
        self.add(f'<g><circle cx="{cx}" cy="{cy}" r="{r + 6}" fill="#FF4B4B33"/><circle cx="{cx}" cy="{cy}" r="{r}" fill="{RED}"/>'
                 f'<path d="M{cx - k:.1f} {cy - k:.1f} L{cx + k:.1f} {cy + k:.1f} M{cx + k:.1f} {cy - k:.1f} L{cx - k:.1f} {cy + k:.1f}" '
                 f'stroke="{NAVY}" stroke-width="3.2" stroke-linecap="round"/></g>')

    def pass_dot(self, cx, cy, r=14):
        """Teal pass badge with a check glyph."""
        self.add(f'<g><circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEAL}"/>'
                 f'<path d="M{cx - r * 0.45:.1f} {cy + r * 0.02:.1f} L{cx - r * 0.1:.1f} {cy + r * 0.38:.1f} L{cx + r * 0.48:.1f} {cy - r * 0.36:.1f}" '
                 f'fill="none" stroke="{NAVY}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></g>')

    def cylinder(self, x, y, w, h, label, sub=None, color=GRAY, size=24):
        ry = 14
        self.add(f'<path d="M{x} {y + ry} V{y + h - ry} A{w / 2} {ry} 0 0 0 {x + w} {y + h - ry} V{y + ry}" '
                 f'fill="{NAVY_LIGHT}" stroke="{color}" stroke-width="2"/>')
        self.add(f'<ellipse cx="{x + w / 2}" cy="{y + ry}" rx="{w / 2}" ry="{ry}" fill="{NAVY_MID}" stroke="{color}" stroke-width="2"/>')
        cy = y + ry + (h - ry) / 2 + size * 0.35 - (size * 0.6 if sub else 0)
        self.text(x + w / 2, cy, label, size, 600, WHITE, "middle")
        if sub:
            self.text(x + w / 2, cy + size * 1.25, sub, int(size * 0.8), 400, GRAY_LIGHT, "middle")
        self._check_fit([label], size, 600, False, w - 20, label)

    def bracket(self, x1, x2, y, label, color=AMBER, up=True, size=20):
        dy = -12 if up else 12
        self.path(f"M{x1} {y} V{y + dy} H{x2} V{y}", color, 2, arrow=False)
        self.text((x1 + x2) / 2, y + dy + (-10 if up else 26), label, size, 600, color, "middle")

    def legend(self, x, y, entries, size=18):
        """entries: list of (kind, color, text) with kind in {'line','dash','box','dot'}."""
        cx = x
        for kind, color, label in entries:
            if kind == "line":
                self.add(f'<path d="M{cx} {y} H{cx + 36}" stroke="{color}" stroke-width="3"/>')
            elif kind == "dash":
                self.add(f'<path d="M{cx} {y} H{cx + 36}" stroke="{color}" stroke-width="3" stroke-dasharray="8 6"/>')
            elif kind == "box":
                self.add(f'<rect x="{cx}" y="{y - 10}" width="36" height="20" rx="4" fill="{NAVY_LIGHT}" stroke="{color}" stroke-width="2"/>')
            elif kind == "dot":
                self.add(f'<circle cx="{cx + 18}" cy="{y}" r="9" fill="{color}"/>')
            self.text(cx + 48, y + size * 0.35, label, size, 400, GRAY_LIGHT)
            cx += 48 + text_width(label, size) + 40

    # output -------------------------------------------------------------------------------
    def _visible(self, vis, step):
        kind, arg = vis
        if step is None:
            return True if kind == "from" else False
        if kind == "from":
            return step >= arg
        return step in arg

    def svg(self, step: int | None = None, max_step: int = 1) -> str:
        """Master (step=None): every cumulative build group, each as <g id="build-n">.
        Step file (step=k): only what is visible at build k."""
        defs = "".join(
            f'<marker id="arr-{k}" viewBox="0 0 16 16" markerWidth="16" markerHeight="16" refX="12" refY="8" '
            f'orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M3 2.5 L12.5 8 L3 13.5" fill="none" '
            f'stroke="{v}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></marker>'
            for k, v in ARROW_COLORS.items())
        groups: dict[str, list[str]] = {}
        order: list[str] = []
        for vis, frag in self.items:
            kind, arg = vis
            if step is None:
                if kind != "from":
                    continue
                gid = f"build-{arg}"
            else:
                if not self._visible(vis, step):
                    continue
                gid = f"build-{arg}" if kind == "from" else f"build-{step}-only"
            if gid not in groups:
                groups[gid] = []
                order.append(gid)
            groups[gid].append(frag)

        def gkey(g: str) -> tuple:
            n = int(g.split("-")[1])
            return (n, g.endswith("only"))

        body = "\n".join(f'<g id="{g}">\n' + "\n".join(groups[g]) + "\n</g>" for g in sorted(order, key=gkey))
        step_txt = ""
        if step is not None and max_step > 1:
            lab = self.step_labels.get(step, "")
            step_txt = f" · build {step}/{max_step}" + (f": {lab}" if lab else "")
        ts = self.title_size
        title = (
            f'<g id="diagram-title">'
            f'<rect x="96" y="{112 - ts * 1.05:.0f}" width="8" height="{ts * 1.3:.0f}" rx="2" fill="{TEAL}"/>'
            f'<text x="124" y="112" font-family="{FONT}" font-size="{ts}" font-weight="700" fill="{WHITE}">{esc(self.title)}</text>'
            + (f'<text x="124" y="{112 + ts * 1.05:.0f}" font-family="{FONT}" font-size="22" font-weight="400" fill="{GRAY}">{esc(self.subtitle)}</text>'
               if self.subtitle else "")
            + f'<text x="1824" y="1054" font-family="{FONT}" font-size="16" font-weight="500" fill="{GRAY_DARK}" '
              f'text-anchor="end" letter-spacing="0.5">{esc((self.course + " · " if self.course else "") + self.id + step_txt)}</text>'
            + '</g>'
        )
        if self.footnote:
            title += (f'\n<g id="diagram-footnote"><text x="96" y="1054" font-family="{FONT}" font-size="18" '
                      f'font-weight="400" fill="{GRAY}">{esc(self.footnote)}</text></g>')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="1920" height="1080" '
            f'role="img" aria-labelledby="t-{self.id}">\n'
            f'<title id="t-{self.id}">{esc(self.id + ": " + self.title)}</title>\n'
            f'<defs>{defs}</defs>\n'
            f'<rect width="1920" height="1080" fill="{NAVY}"/>\n{title}\n{body}\n</svg>\n'
        )

    def max_step(self) -> int:
        steps = [arg for (kind, arg), _ in self.items if kind == "from"]
        only = [s for (kind, arg), _ in self.items if kind == "only" for s in arg]
        return max(steps + only + [1])

    def save(self, outdir: Path, master_step: int | None = None, export_steps: bool = True) -> dict:
        outdir.mkdir(parents=True, exist_ok=True)
        ms = self.max_step()
        master = f"{self.id}-{self.slug}.svg"
        (outdir / master).write_text(self.svg(step=master_step, max_step=ms) if master_step else self.svg(None, ms),
                                     encoding="utf-8")
        for w in self.warnings:
            print("  warn:", w)
        entry = {"id": self.id, "title": self.title, "file": master, "lectures": self.lectures,
                 "keywords": self.keywords, "spec": self.spec, "steps": {}}
        if export_steps and ms > 1:
            for s in range(1, ms + 1):
                fn = f"{self.id}-step{s}.svg"
                (outdir / fn).write_text(self.svg(step=s, max_step=ms), encoding="utf-8")
                entry["steps"][str(s)] = {"file": fn, "label": self.step_labels.get(s, ""),
                                          "keywords": self.step_keywords.get(s, [])}
        return entry


def stroke_or_white(stroke: str) -> str:
    return WHITE if stroke in (GRAY_DARK,) else stroke
