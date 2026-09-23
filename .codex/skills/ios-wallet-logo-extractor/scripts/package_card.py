#!/usr/bin/env python3
"""Validate and package a transparent card foreground into ./Assets/<card name [•••• 1234]>/."""
import argparse
import html
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path

from check_svg import check
from render_upload_png import render


def card_directory_name(name, last4):
    name = " ".join(name.strip().split())
    if not name or name in {".", ".."} or any(c in name for c in "/\\:\0\r\n"):
        raise ValueError("card name must be nonempty and contain no path separators or control characters")
    if last4 and not re.fullmatch(r"[0-9]{4}", last4):
        raise ValueError("last4 must be exactly four visible digits")
    return name + (f" •••• {last4}" if last4 else "")


def preview_html(name, background):
    title = html.escape(name)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 前景预览</title>
<style>
body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#151b24;color:#f2f5f8;font:16px/1.55 system-ui,-apple-system,sans-serif}}
main{{width:min(94vw,960px);padding:24px 0}}h1{{font-size:21px;margin:0 0 6px}}p{{margin:0 0 16px;color:#bec9d4}}
.card{{width:100%;aspect-ratio:1536/969;background:{background};border-radius:3.715%;overflow:hidden;box-shadow:0 20px 60px #0008}}
.card img{{width:100%;height:100%;display:block}}
</style></head><body><main><h1>{title}</h1><p>底色仅用于检查；SVG 和上传 PNG 保持透明。</p>
<div class="card"><img src="foreground.svg" alt="{title} 的卡面前景标识"></div>
<p>请将 upload.png 作为 Logo 图层上传，并保持居中、缩放 100%、旋转 0°、不透明度 100%。</p>
</main></body></html>'''


def clear_hidden_flags(directory):
    """macOS may retain Finder's hidden flag after a dot-prefixed temp directory is renamed."""
    if not hasattr(os, "chflags") or not hasattr(stat, "UF_HIDDEN"):
        return
    for item in (directory, *directory.iterdir()):
        flags = getattr(item.stat(), "st_flags", 0)
        if flags & stat.UF_HIDDEN:
            os.chflags(item, flags & ~stat.UF_HIDDEN)


def package(source, project_root, name, last4, preview_background):
    folder_name = card_directory_name(name, last4)
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", preview_background):
        raise ValueError("preview background must be a six-digit hex color")
    check(source)
    root = project_root.resolve()
    if not root.is_dir():
        raise ValueError(f"project directory does not exist: {root}")
    assets = root / "Assets"
    target = assets / folder_name
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing card: {target}")
    assets.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".card-", dir=assets))
    try:
        svg = temporary / "foreground.svg"
        shutil.copy2(source, svg)
        render(svg, temporary / "upload.png")
        (temporary / "preview.html").write_text(preview_html(folder_name, preview_background), encoding="utf-8")
        os.replace(temporary, target)
        clear_hidden_flags(target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    print(f"Packaged {target}")
    print("Upload upload.png as a centered Logo layer at 100% scale; the SVG is the vector master.")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="transparent vector master")
    parser.add_argument("--name", required=True, help="card name for the folder")
    parser.add_argument("--last4", help="last four visible card digits; omit if absent")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="defaults to current directory")
    parser.add_argument("--preview-background", default="#2179a8", help="six-digit hex color")
    args = parser.parse_args()
    try:
        package(args.svg, args.project_root, args.name, args.last4, args.preview_background)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
