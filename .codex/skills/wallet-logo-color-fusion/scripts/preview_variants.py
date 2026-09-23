#!/usr/bin/env python3
"""Create a browser comparison of SVG overlays on a referenced card background."""
import argparse
import html
import shutil
from pathlib import Path

from PIL import Image


def create(background, crop, variants, output):
    with Image.open(background) as image:
        iw, ih = image.size
    left, top, right, bottom = crop or (0, 0, iw, ih)
    if not (0 <= left < right <= iw and 0 <= top < bottom <= ih):
        raise ValueError('crop must fit within background image')
    cw, ch = right-left, bottom-top
    output.parent.mkdir(parents=True, exist_ok=True)
    background_target = output.parent / f'background-reference{background.suffix.lower()}'
    if background.resolve() != background_target.resolve():
        shutil.copy2(background, background_target)
    for variant in variants:
        if variant.parent.resolve() != output.parent.resolve():
            raise ValueError('put SVG variants in the preview output directory')
        if not variant.is_file():
            raise FileNotFoundError(variant)
    panels = []
    for variant in variants:
        name = html.escape(variant.stem)
        filename = html.escape(variant.name, quote=True)
        panels.append(f'''<section><h2>{name}</h2><div class="card">
<img class="background" src="{html.escape(background_target.name,quote=True)}" alt="">
<img class="overlay" src="{filename}" alt="{name} logo overlay"></div></section>''')
    markup = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Logo 背景融合对比</title><style>
body{{margin:0;padding:24px;background:#11141d;color:#f4f4f8;font:16px/1.5 system-ui,-apple-system,sans-serif}}
h1{{margin:0 0 8px;font-size:24px}}p{{color:#c7c8d2;margin:0 0 24px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(92vw,620px),1fr));gap:24px}}
h2{{font-size:17px;font-weight:600}}.card{{position:relative;width:100%;aspect-ratio:{cw}/{ch};overflow:hidden;border-radius:3.7%;background:#151923}}
.card img{{position:absolute;display:block}}.background{{width:{iw/cw*100:.6f}%;height:{ih/ch*100:.6f}%;left:{-left/cw*100:.6f}%;top:{-top/ch*100:.6f}%}}
.overlay{{inset:0;width:100%;height:100%}}
</style></head><body><h1>Logo 背景融合对比</h1><p>原背景只作预览；下面叠加的是可直接上传的 SVG。</p>
<div class="grid">{''.join(panels)}</div></body></html>'''
    output.write_text(markup, encoding='utf-8')
    print(f'Created {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('background', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('variants', nargs='+', type=Path)
    parser.add_argument('--crop', nargs=4, type=int, metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    args = parser.parse_args()
    try:
        create(args.background, args.crop, args.variants, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')


if __name__ == '__main__':
    main()
