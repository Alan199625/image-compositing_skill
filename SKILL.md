---
name: compose-daily-image-report
description: 将指定文件夹内的所有图片按文件修改时间排序，自动以近似正方形的网格排列合成为一张大图，用作日报图。保持每张图片原始尺寸，默认黑色背景加间隙。当用户提到「合成日报图 / 生成日报图 / 拼接图片 / 把图片拼成一张 / merge images into grid / image grid report」时触发。
---

# Compose Daily Image Report

将用户指定文件夹内的图片按文件修改时间排序后，合成为一张网格大图，保存在同一文件夹内。默认黑色背景带间隙。

## 触发场景

用户给出一个装有图片的文件夹，并要求：

- 合成日报图 / 生成日报图片
- 拼接图片 / 把这堆图片拼成一张 / 合成一张大图
- merge / combine / stitch images into a grid

## 用户需要提供的输入

一个文件夹的绝对路径。如果用户没给，先向用户询问路径再执行。

## 执行方式

从本 skill 目录调用（Windows 使用 `py -3`，*nix 用 `python3`）：

```bash
py -3 scripts/compose_grid.py "<folder>"
```

可选参数：

- `--output NAME`：输出文件名（默认 `成都原色每日截图_YYYY-MM-DD.jpg`）
- `--bg COLOR`：背景色，支持 hex 或颜色名（默认 `#000000`）
- `--gap PX`：格子间隙（默认 `12`）
- `--margin PX`：整图外边距（默认 `20`）
- `--title TEXT`：标题文字（默认 `成都原色每日进度-YYYY-MM-DD`，YYYY-MM-DD 为运行当天）
- `--no-title`：不渲染标题
- `--max-side PX`：画布最长边上限，超出按比例缩小（默认 `8000`，传 `0` 关闭）
- `--quality N`：JPEG 质量 1–95（默认 `88`）

脚本成功后会把生成的绝对路径打印到 stdout。

## 固定行为

- 排序：文件修改时间升序（`st_mtime`）
- 布局：`cols = ceil(sqrt(n))`，`rows = ceil(n/cols)`，最后一行不足位置保留背景色
- 单元格尺寸：该列最大宽 × 该行最大高
- 图片在单元格内居中，**不缩放**，保留原始尺寸
- 标题：默认顶部居中渲染「成都原色每日进度-YYYY-MM-DD」，在 downscale 之后再渲染，字号按最终画布宽度自动缩放（60–220px），颜色依背景明暗自动取白/黑
- 支持格式：`.jpg .jpeg .png .webp .bmp`
- 输入过滤：自动跳过以 `成都原色每日截图_` 或 `daily_report_` 开头的文件（避免把之前生成的日报图当成输入）
- 尺寸保护：合成完成后若最长边超过 `--max-side`（默认 8000px），整体按比例缩小到上限，保证主流平台（微信/钉钉/飞书/浏览器/Office）能打开
- 输出：JPEG（quality=88, optimize=True），保存到输入文件夹内

## 依赖

需要 Python 3 + Pillow。若脚本提示 Pillow 未安装，告知用户执行：

```bash
py -3 -m pip install pillow
```

## 错误处理

- 文件夹不存在：告诉用户路径找不到，确认是否拼写错误
- 文件夹内没图片：告知用户，并询问是否要换一个子目录
- Pillow 未安装：提示用户安装命令（见上）
