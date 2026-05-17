#!/usr/bin/env python3
"""Compose a grid composite image from all images in a folder."""
import argparse
import sys
from datetime import date
from pathlib import Path

import compose_common as cc

cc.enable_utf8_console()


def main():
    parser = argparse.ArgumentParser(description="Compose grid image report.")
    parser.add_argument("folder", help="Input folder containing images")
    parser.add_argument(
        "--output",
        default=None,
        help="Output filename (default: 成都原色每日截图_YYYY-MM-DD.jpg)",
    )
    parser.add_argument(
        "--bg", default="#000000", help="Background color (default: #000000)"
    )
    parser.add_argument(
        "--gap", type=int, default=12, help="Gap between cells in px (default: 12)"
    )
    parser.add_argument(
        "--margin", type=int, default=20, help="Outer margin in px (default: 20)"
    )
    parser.add_argument(
        "--title",
        default=None,
        help='Title text (default: "成都原色每日进度-YYYY-MM-DD")',
    )
    parser.add_argument(
        "--no-title", action="store_true", help="Disable the title band"
    )
    parser.add_argument(
        "--max-side",
        type=int,
        default=8000,
        help="Max canvas long edge in px; downscale if exceeded (default: 8000, 0 disables)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=88,
        help="JPEG quality 1-95 (default: 88)",
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        sys.stderr.write(f"Not a directory: {folder}\n")
        sys.exit(1)

    today = date.today().isoformat()
    out_name = args.output or f"成都原色每日截图_{today}.jpg"

    images = cc.collect_images(folder, exclude_names=(out_name,))
    if not images:
        sys.stderr.write(f"No supported images found in {folder}\n")
        sys.exit(1)

    if args.no_title:
        title = None
    else:
        title = args.title or f"成都原色每日进度-{today}"

    canvas = cc.compose(
        images,
        gap=args.gap,
        margin=args.margin,
        bg_color=args.bg,
        title=title,
        max_side=args.max_side,
    )

    out_path = folder / out_name
    canvas.save(out_path, "JPEG", quality=args.quality, subsampling=cc.JPEG_SUBSAMPLING)
    print(str(out_path))


if __name__ == "__main__":
    main()
