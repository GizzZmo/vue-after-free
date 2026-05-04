#!/usr/bin/env python3
"""
Generate composite UI preview screenshots from existing game assets.

Composites the main menu, success, and failure screens so that CI can
produce representative screenshots without requiring a real PS4.

requirements:
    Pillow

pip install Pillow
"""

import os
import sys
from typing import Callable
from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../src/download0/img")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/screenshots")

SCREEN_W = 1920
SCREEN_H = 1080

# ── helpers ──────────────────────────────────────────────────────────────────

def load(rel: str) -> Image.Image | None:
    path = os.path.join(ASSETS, rel)
    if not os.path.exists(path):
        print(f"Warning: asset not found: {path}", file=sys.stderr)
        return None
    return Image.open(path).convert("RGBA")


def paste(canvas: Image.Image, img: Image.Image, x: int, y: int,
          w: int | None = None, h: int | None = None) -> None:
    if w and h:
        img = img.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(img, (x, y))


def bold_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ── composite builders ───────────────────────────────────────────────────────

def _draw_button(canvas: Image.Image, x: int, y: int, w: int, h: int,
                 label: str, selected: bool = False) -> None:
    """Draw a simple rounded-rect button with label text."""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fill = (80, 120, 200, 210) if selected else (40, 40, 60, 180)
    outline = (180, 220, 255, 255) if selected else (100, 100, 140, 200)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12,
                           fill=fill, outline=outline, width=2)
    canvas.alpha_composite(overlay)

    draw2 = ImageDraw.Draw(canvas)
    font = bold_font(36 if selected else 32)
    bbox = draw2.textbbox((0, 0), label, font=font)
    tx = x + (w - (bbox[2] - bbox[0])) // 2
    ty = y + (h - (bbox[3] - bbox[1])) // 2
    color = (255, 255, 255, 255) if selected else (200, 200, 220, 255)
    draw2.text((tx - bbox[0], ty - bbox[1]), label, font=font, fill=color)


def main_menu() -> Image.Image:
    canvas = Image.new("RGBA", (SCREEN_W, SCREEN_H), (10, 10, 20, 255))

    bg = load("multiview_bg_VAF.png")
    if bg:
        paste(canvas, bg, 0, 0, SCREEN_W, SCREEN_H)

    logo = load("logo.png")
    if logo:
        lw, lh = 600, 338
        paste(canvas, logo, SCREEN_W // 2 - lw // 2, 50, lw, lh)

    menu_items = ["Jailbreak", "Payload Menu", "Config"]
    start_y, spacing = 450, 120
    btn_w, btn_h = 400, 80
    btn_x = SCREEN_W // 2 - btn_w // 2

    for i, label in enumerate(menu_items):
        _draw_button(canvas, btn_x, start_y + i * spacing, btn_w, btn_h,
                     label, selected=(i == 0))

    return canvas


def success_screen() -> Image.Image:
    canvas = Image.new("RGBA", (SCREEN_W, SCREEN_H), (10, 10, 20, 255))

    bg = load("bg-success.png")
    if bg:
        paste(canvas, bg, 0, 0, SCREEN_W, SCREEN_H)

    return canvas


def fail_screen() -> Image.Image:
    canvas = Image.new("RGBA", (SCREEN_W, SCREEN_H), (10, 10, 20, 255))

    bg = load("bg-fail.jpg")
    if bg:
        paste(canvas, bg, 0, 0, SCREEN_W, SCREEN_H)

    return canvas


# ── entry point ──────────────────────────────────────────────────────────────

SCREENS: list[tuple[str, Callable[[], Image.Image]]] = [
    ("main_menu.png", main_menu),
    ("success.png", success_screen),
    ("fail.png", fail_screen),
]


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    for filename, builder in SCREENS:
        img = builder()
        out_path = os.path.join(OUT_DIR, filename)
        img.convert("RGB").save(out_path, "PNG", optimize=True)
        print(f"Saved: {out_path}")

    print(f"\nAll screenshots written to: {OUT_DIR}")


if __name__ == "__main__":
    main()
