#!/usr/bin/env python3
"""Report dominant colors and contrast in the card area behind a vector logo."""
import argparse
import colorsys
import json
from collections import Counter
from pathlib import Path
from statistics import median

from PIL import Image


def luminance(rgb):
    linear = []
    for channel in rgb[:3]:
        value = channel / 255
        linear.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return sum(a*b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def hex_color(rgb):
    return '#%02X%02X%02X' % tuple(int(v) for v in rgb[:3])


def quantile(values, fraction):
    values = sorted(values)
    return round(values[round((len(values)-1)*fraction)], 4)


def valid_box(box, width, height, name):
    left, top, right, bottom = box
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError(f'{name} must fit within {width}x{height}')


def probe(image_path, crop_box=None, logo_box=None, view_box=None):
    image = Image.open(image_path).convert('RGB')
    crop_box = crop_box or (0, 0, image.width, image.height)
    valid_box(crop_box, image.width, image.height, 'crop')
    card = image.crop(crop_box)
    sample = card.copy()
    sample.thumbnail((420, 420))
    quantized = sample.quantize(colors=12, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    counts = Counter(quantized.tobytes())
    total = sum(counts.values())
    dominant = [
        {'hex': hex_color(palette[index*3:index*3+3]), 'share': round(count / total, 3)}
        for index, count in counts.most_common(12)
    ]
    sampled = [sample.getpixel((x, y)) for y in range(0, sample.height, 3) for x in range(0, sample.width, 3)]
    buckets = {'rose': [], 'blue': [], 'light': [], 'dark': []}
    for rgb in sampled:
        hue, saturation, value = colorsys.rgb_to_hsv(*(v/255 for v in rgb))
        degrees = hue * 360
        lightness = luminance(rgb)
        if ((degrees <= 20 or degrees >= 315) and saturation >= 0.14 and value >= 0.25):
            buckets['rose'].append(rgb)
        if 185 <= degrees <= 260 and saturation >= 0.16 and value >= 0.25:
            buckets['blue'].append(rgb)
        if lightness >= 0.7:
            buckets['light'].append(rgb)
        if lightness <= 0.05:
            buckets['dark'].append(rgb)
    accents = {
        name: {'hex': hex_color([median(pixel[i] for pixel in values) for i in range(3)]),
               'share': round(len(values) / len(sampled), 3)}
        for name, values in buckets.items() if values
    }
    result = {
        'source_size': [image.width, image.height],
        'card_crop': list(crop_box),
        'card_size': [card.width, card.height],
        'card_ratio': round(card.width/card.height, 5),
        'dominant_colors': dominant,
        'accent_samples': accents,
    }
    if logo_box:
        if not view_box:
            raise ValueError('view-box size is required with logo-box')
        x0, y0, x1, y1 = logo_box
        vw, vh = view_box
        local = (
            round(x0 * card.width / vw), round(y0 * card.height / vh),
            round(x1 * card.width / vw), round(y1 * card.height / vh),
        )
        valid_box(local, card.width, card.height, 'logo-box')
        region = card.crop(local)
        values = [luminance(region.getpixel((x,y))) for y in range(0,region.height,3) for x in range(0,region.width,3)]
        result['logo_region'] = {
            'card_pixel_box': list(local),
            'luminance_p10': quantile(values, 0.1),
            'luminance_median': quantile(values, 0.5),
            'luminance_p90': quantile(values, 0.9),
            'luminance_max': quantile(values, 1.0),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('background', type=Path)
    parser.add_argument('--crop', nargs=4, type=int, metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    parser.add_argument('--logo-box', nargs=4, type=float, metavar=('LEFT','TOP','RIGHT','BOTTOM'))
    parser.add_argument('--view-box', nargs=2, type=float, metavar=('WIDTH','HEIGHT'))
    args = parser.parse_args()
    try:
        print(json.dumps(probe(args.background, args.crop, args.logo_box, args.view_box), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')


if __name__ == '__main__':
    main()
