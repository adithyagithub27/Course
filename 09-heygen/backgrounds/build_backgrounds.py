#!/usr/bin/env python3
"""Build the premium HeyGen avatar backgrounds (1920x1080 PNG) from the design system.

Run:  python build_backgrounds.py        (needs Pillow)
Outputs one shared background plus one per-course accent variant. The avatar sits in the
right third of the frame (HeyGen default); the left two thirds stay clean for lower
thirds and picture-in-picture slides.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
NAVY = (10, 22, 40)        # #0A1628 Deep Navy
NAVY_MID = (15, 30, 53)    # #0F1E35
NAVY_LIGHT = (26, 39, 66)  # #1A2742
TEAL = (0, 212, 170)       # #00D4AA
AMBER = (255, 176, 32)     # #FFB020
SLATE = (148, 163, 184)    # #94A3B8

VARIANTS = {
    # name: (accent colour, accent position x-fraction, note)
    "studio-navy": (TEAL, 0.22, "shared default for all three courses"),
    "course2-testing": (TEAL, 0.22, "Course 2: teal, same as shared"),
    "course3-voice": ((0, 180, 212), 0.22, "Course 3: teal shifted toward cyan (sound/signal)"),
    "course4-observability": ((60, 200, 160), 0.22, "Course 4: teal shifted toward green (healthy signal)"),
}


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def base_gradient() -> Image.Image:
    """Diagonal gradient: slightly lighter top-left, deep navy bottom-right."""
    img = Image.new("RGB", (W, H), NAVY)
    px = img.load()
    for y in range(H):
        for x in range(0, W, 2):
            t = (x / W) * 0.55 + (y / H) * 0.45
            c = _lerp(NAVY_LIGHT, NAVY, min(1.0, t * 1.15))
            px[x, y] = c
            if x + 1 < W:
                px[x + 1, y] = c
    return img


def glow(img: Image.Image, colour, cx: float, cy: float, radius: int, strength: float) -> Image.Image:
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=tuple(int(c * strength) for c in colour))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return Image.blend(img, Image.eval(Image.composite(layer, img, Image.new("L", (W, H), 255)), lambda v: v), 0.0).copy() if False else _screen(img, layer)


def _screen(a: Image.Image, b: Image.Image) -> Image.Image:
    pa, pb = a.load(), b.load()
    out = Image.new("RGB", (W, H))
    po = out.load()
    for y in range(H):
        for x in range(W):
            r1, g1, b1 = pa[x, y]
            r2, g2, b2 = pb[x, y]
            po[x, y] = (255 - (255 - r1) * (255 - r2) // 255,
                        255 - (255 - g1) * (255 - g2) // 255,
                        255 - (255 - b1) * (255 - b2) // 255)
    return out


def subtle_grid(img: Image.Image, step: int = 96, alpha: int = 10) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for x in range(0, W, step):
        d.line((x, 0, x, H), fill=(*SLATE, alpha), width=1)
    for y in range(0, H, step):
        d.line((0, y, W, y), fill=(*SLATE, alpha), width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def vignette(img: Image.Image, strength: float = 0.55) -> Image.Image:
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-W * 0.25, -H * 0.45, W * 1.25, H * 1.45), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(260))
    dark = Image.new("RGB", (W, H), (4, 10, 20))
    return Image.composite(img, Image.blend(img, dark, strength), mask)


def build(name: str, accent, ax: float) -> Path:
    img = base_gradient()
    # Soft key light behind where the presenter stands (right third), so the avatar separates.
    img = glow(img, (40, 60, 95), W * 0.72, H * 0.55, 520, 0.9)
    # Brand accent glow, low left, out of the presenter's area.
    img = glow(img, accent, W * ax, H * 0.95, 460, 0.28)
    img = subtle_grid(img)
    img = vignette(img)
    # Thin accent rule at the bottom, the same device as the slide footers.
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 6, W, H), fill=accent)
    out = Path(__file__).with_name(f"{name}.png")
    img.save(out, optimize=True)
    return out


if __name__ == "__main__":
    for name, (accent, ax, note) in VARIANTS.items():
        p = build(name, accent, ax)
        print(f"{p.name:30} {p.stat().st_size // 1024:5d} KB  {note}")
