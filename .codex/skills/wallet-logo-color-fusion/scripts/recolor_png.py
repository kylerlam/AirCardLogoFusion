#!/usr/bin/env python3
"""Recolor an approved transparent PNG without changing any alpha values."""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image


def rgb(value):
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise ValueError('colors must use #RRGGBB')
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def interpolate(left, right, fraction):
    return tuple(round(a + (b - a) * fraction) for a, b in zip(left, right))


def recolor(source, output, colors):
    if source.resolve() == output.resolve():
        raise ValueError('output must differ from source')
    image = Image.open(source).convert('RGBA')
    alpha = image.getchannel('A')
    if alpha.getextrema()[0] == 255:
        raise ValueError('source must have transparent pixels')
    box = alpha.getbbox()
    if box is None:
        raise ValueError('source has no visible logo')
    palette = [rgb(value) for value in colors]
    result = Image.new('RGBA', image.size, (0, 0, 0, 0))
    source_alpha = alpha.load()
    pixels = result.load()
    left, top, right, bottom = box
    width = max(1, right - left - 1)
    for x in range(left, right):
        position = (x - left) / width
        if position <= 0.5:
            color = interpolate(palette[0], palette[1], position * 2)
        else:
            color = interpolate(palette[1], palette[2], (position - 0.5) * 2)
        for y in range(top, bottom):
            opacity = source_alpha[x, y]
            if opacity:
                pixels[x, y] = (*color, opacity)
    if result.getchannel('A').tobytes() != alpha.tobytes():
        raise AssertionError('alpha channel changed')
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)
    print(f'Created {output} ({image.width}x{image.height}; alpha unchanged)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--colors', nargs=3, required=True, metavar=('LEFT', 'MIDDLE', 'RIGHT'))
    args = parser.parse_args()
    try:
        recolor(args.source, args.output, args.colors)
    except (OSError, ValueError, AssertionError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')


if __name__ == '__main__':
    sys.exit(main())
