#!/usr/bin/env python3
"""Shared helpers for the compose-daily-image-report skill."""
import math
import sys
from pathlib import Path

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ImportError:
    sys.stderr.write(
        "Missing dependency: Pillow. Install with: py -3 -m pip install pillow\n"
    )
    sys.exit(2)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

CJK_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]

DEFAULT_OUTPUT_PREFIX = "成都原色每日截图_"

TITLE_FONT_MIN = 60
TITLE_FONT_MAX = 220
TITLE_FONT_WIDTH_DIVISOR = 22

JPEG_SUBSAMPLING = 2


def enable_utf8_console():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def load_cjk_font(size: int):
    for path in CJK_FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def pick_text_color(bg_color: str) -> str:
    try:
        r, g, b = ImageColor.getrgb(bg_color)[:3]
    except ValueError:
        return "#FFFFFF"
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#FFFFFF" if luminance < 128 else "#000000"


def collect_images(folder: Path, exclude_names=()):
    exclude_set = set(exclude_names)
    files = [
        p for p in folder.iterdir()
        if p.is_file()
        and p.suffix.lower() in IMAGE_EXTS
        and not p.name.startswith(DEFAULT_OUTPUT_PREFIX)
        and not p.name.startswith("daily_report_")
        and p.name not in exclude_set
    ]
    files.sort(key=lambda p: p.stat().st_mtime)
    return files


def compose(
    image_paths,
    *,
    gap: int,
    margin: int,
    bg_color: str,
    title: str | None,
    max_side: int,
):
    """Build a grid composite at final output size.

    Each input is resized to its on-canvas target before pasting, so peak
    memory is bounded by the final canvas (not the sum of full-resolution
    inputs).
    """
    n = len(image_paths)
    if n == 0:
        raise ValueError("no images")

    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    images = [Image.open(p) for p in image_paths]
    sizes = [im.size for im in images]

    col_widths_full = [0] * cols
    row_heights_full = [0] * rows
    for i, (w, h) in enumerate(sizes):
        r, c = divmod(i, cols)
        if w > col_widths_full[c]:
            col_widths_full[c] = w
        if h > row_heights_full[r]:
            row_heights_full[r] = h

    grid_w_full = 2 * margin + sum(col_widths_full) + (cols - 1) * gap
    grid_h_full = 2 * margin + sum(row_heights_full) + (rows - 1) * gap

    if max_side > 0:
        scale = min(1.0, max_side / max(grid_w_full, grid_h_full))
    else:
        scale = 1.0

    if scale < 1.0:
        sc_col_widths = [max(1, int(round(w * scale))) for w in col_widths_full]
        sc_row_heights = [max(1, int(round(h * scale))) for h in row_heights_full]
        sc_gap = max(1, int(round(gap * scale)))
        sc_margin = max(1, int(round(margin * scale)))
    else:
        sc_col_widths = col_widths_full
        sc_row_heights = row_heights_full
        sc_gap = gap
        sc_margin = margin

    grid_w = 2 * sc_margin + sum(sc_col_widths) + (cols - 1) * sc_gap
    grid_h = 2 * sc_margin + sum(sc_row_heights) + (rows - 1) * sc_gap

    title_band = 0
    title_font = None
    title_bbox = None
    if title:
        font_size = max(
            TITLE_FONT_MIN,
            min(TITLE_FONT_MAX, grid_w // TITLE_FONT_WIDTH_DIVISOR),
        )
        title_font = load_cjk_font(font_size)
        title_bbox = title_font.getbbox(title)
        text_h = title_bbox[3] - title_bbox[1]
        title_band = sc_margin + text_h + sc_gap * 2

    canvas = Image.new("RGB", (grid_w, title_band + grid_h), bg_color)

    if title:
        draw = ImageDraw.Draw(canvas)
        text_w = title_bbox[2] - title_bbox[0]
        tx = (grid_w - text_w) // 2 - title_bbox[0]
        ty = sc_margin - title_bbox[1]
        draw.text((tx, ty), title, font=title_font, fill=pick_text_color(bg_color))

    y = title_band + sc_margin
    for r in range(rows):
        x = sc_margin
        for c in range(cols):
            i = r * cols + c
            if i < n:
                img = images[i]
                orig_w, orig_h = sizes[i]
                target_w = max(1, int(round(orig_w * scale)))
                target_h = max(1, int(round(orig_h * scale)))
                if (target_w, target_h) != img.size:
                    placed = img.resize((target_w, target_h), Image.LANCZOS)
                else:
                    placed = img
                cx = x + (sc_col_widths[c] - target_w) // 2
                cy = y + (sc_row_heights[r] - target_h) // 2
                if placed.mode in ("RGBA", "LA"):
                    canvas.paste(placed, (cx, cy), placed)
                elif placed.mode == "RGB":
                    canvas.paste(placed, (cx, cy))
                else:
                    canvas.paste(placed.convert("RGB"), (cx, cy))
                img.close()
            x += sc_col_widths[c] + sc_gap
        y += sc_row_heights[r] + sc_gap

    return canvas
