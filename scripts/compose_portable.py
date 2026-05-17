#!/usr/bin/env python3
"""Portable daily-report composer.

Double-click the .exe (or .py) to compose all images in the same folder into
a grid report. Or drag a folder onto the .exe to target that folder.
"""
import sys
import traceback
from datetime import date
from pathlib import Path

import compose_common as cc

cc.enable_utf8_console()

GAP = 12
MARGIN = 20
BG_COLOR = "#000000"
TITLE_PREFIX = "成都原色每日进度-"
MAX_SIDE = 8000
JPEG_QUALITY = 88


def get_default_folder() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def pause():
    try:
        input("按 Enter 关闭窗口...")
    except (EOFError, KeyboardInterrupt):
        pass


def run():
    args = [a for a in sys.argv[1:] if a.strip()]
    if args:
        folder = Path(args[0]).expanduser().resolve()
    else:
        folder = get_default_folder()

    print(f"目标文件夹: {folder}")

    if not folder.is_dir():
        print(f"错误: 不是一个文件夹: {folder}")
        sys.exit(1)

    today = date.today().isoformat()
    out_name = f"成都原色每日截图_{today}.jpg"

    images = cc.collect_images(folder, exclude_names=(out_name,))
    if not images:
        print(f"错误: 文件夹内没有图片 ({'/'.join(sorted(cc.IMAGE_EXTS))})")
        sys.exit(1)

    print(f"找到 {len(images)} 张图片，开始合成...")
    title = f"{TITLE_PREFIX}{today}"

    canvas = cc.compose(
        images,
        gap=GAP,
        margin=MARGIN,
        bg_color=BG_COLOR,
        title=title,
        max_side=MAX_SIDE,
    )
    out_path = folder / out_name
    canvas.save(out_path, "JPEG", quality=JPEG_QUALITY, subsampling=cc.JPEG_SUBSAMPLING)
    print(f"已生成: {out_path}")


def main():
    try:
        run()
    except SystemExit:
        pause()
        raise
    except Exception:
        traceback.print_exc()
        pause()
        sys.exit(1)
    pause()


if __name__ == "__main__":
    main()
