#!/usr/bin/env python3
"""Generate icon.ico for the compose-daily-image-report executable.

Design: 3x3 grid of colored tiles on a charcoal background, matching the
visual metaphor of the daily-report grid output.
"""
from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 256
BG = (22, 22, 24, 255)
MARGIN = 26
GAP = 10
COLS = ROWS = 3
RADIUS = 12

TILE_COLORS = [
    (92, 168, 240),
    (246, 177, 107),
    (138, 209, 140),
    (232, 118, 172),
    (174, 154, 238),
    (240, 206, 112),
    (118, 206, 198),
    (222, 120, 118),
    (180, 180, 190),
]


def make_icon(out: Path):
    img = Image.new("RGBA", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    bg_pad = 8
    draw.rounded_rectangle(
        [bg_pad, bg_pad, SIZE - bg_pad, SIZE - bg_pad],
        radius=28,
        fill=(30, 30, 34, 255),
    )

    avail = SIZE - 2 * MARGIN - (COLS - 1) * GAP
    tile = avail // COLS

    for r in range(ROWS):
        for c in range(COLS):
            x = MARGIN + c * (tile + GAP)
            y = MARGIN + r * (tile + GAP)
            color = TILE_COLORS[r * COLS + c]
            draw.rounded_rectangle(
                [x, y, x + tile, y + tile],
                radius=RADIUS,
                fill=color,
            )

    img.save(
        out,
        format="ICO",
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )


if __name__ == "__main__":
    out = Path(__file__).parent / "icon.ico"
    make_icon(out)
    print(f"Generated: {out}")
