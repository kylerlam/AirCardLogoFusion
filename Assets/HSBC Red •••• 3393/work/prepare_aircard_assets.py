#!/usr/bin/env python3
"""Prepare opaque AirCard backgrounds and flat-color lion trace sources."""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageFilter


CARD_SIZE = (1536, 969)
TRACE_WIDTH = 850
CHROMA_KEY = (0, 255, 0)

RED_PALETTE = (
    (62, 6, 9),
    (76, 7, 11),
    (113, 11, 17),
    (138, 13, 20),
    (151, 14, 22),
    (176, 17, 26),
    (214, 20, 31),
    (251, 24, 37),
    (251, 47, 52),
    (251, 70, 67),
    (250, 93, 85),
    (250, 128, 114),
    (245, 244, 241),
)

BLACK_PALETTE = (
    (29, 29, 27),
    (35, 35, 33),
    (39, 39, 37),
    (44, 44, 43),
    (50, 50, 49),
    (66, 66, 65),
    (71, 71, 70),
    (92, 91, 91),
    (102, 101, 101),
    (112, 111, 111),
    (127, 126, 126),
    (145, 144, 144),
    (216, 216, 213),
)


def flatten_and_resize(source: Path, destination: Path, matte: tuple[int, int, int]) -> None:
    image = Image.open(source).convert("RGBA")
    base = Image.new("RGBA", image.size, (*matte, 255))
    image = Image.alpha_composite(base, image).convert("RGB")
    image = image.resize(CARD_SIZE, Image.Resampling.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG", optimize=True)


def close_mask(mask: Image.Image) -> Image.Image:
    return mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))


def fill_enclosed_holes(mask: Image.Image) -> Image.Image:
    width, height = mask.size
    pixels = mask.load()
    outside = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        index = y * width + x
        if pixels[x, y] == 0 and not outside[index]:
            outside[index] = 1
            queue.append((x, y))

    for x in range(width):
        seed(x, 0)
        seed(x, height - 1)
    for y in range(height):
        seed(0, y)
        seed(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                index = ny * width + nx
                if pixels[nx, ny] == 0 and not outside[index]:
                    outside[index] = 1
                    queue.append((nx, ny))

    result = Image.new("L", (width, height), 0)
    out = result.load()
    for y in range(height):
        offset = y * width
        for x in range(width):
            if pixels[x, y] or not outside[offset + x]:
                out[x, y] = 255
    return result


def nearest_palette_index(rgb: tuple[int, int, int]) -> int:
    if min(rgb) >= 205 and max(rgb) - min(rgb) <= 38:
        return len(RED_PALETTE) - 1
    r, g, b = rgb
    return min(
        range(len(RED_PALETTE) - 1),
        key=lambda index: (r - RED_PALETTE[index][0]) ** 2
        + (g - RED_PALETTE[index][1]) ** 2
        + (b - RED_PALETTE[index][2]) ** 2,
    )


def build_trace_sources(source: Path, output_dir: Path) -> None:
    source_photo = Image.open(source).convert("RGB").crop((0, 0, *CARD_SIZE))
    photo = source_photo.crop((0, 0, TRACE_WIDTH, CARD_SIZE[1]))
    mask = Image.new("L", photo.size, 0)
    mask_pixels = mask.load()
    photo_pixels = photo.load()
    for y in range(photo.height):
        for x in range(photo.width):
            r, g, b = photo_pixels[x, y]
            if r >= 38 and r - g >= 24 and r - b >= 18:
                mask_pixels[x, y] = 255
    mask = fill_enclosed_holes(close_mask(mask))
    mask_pixels = mask.load()

    red_crop = Image.new("RGB", photo.size, CHROMA_KEY)
    black_crop = Image.new("RGB", photo.size, CHROMA_KEY)
    red_pixels, black_pixels = red_crop.load(), black_crop.load()
    for y in range(photo.height):
        for x in range(photo.width):
            if mask_pixels[x, y]:
                index = nearest_palette_index(photo_pixels[x, y])
                red_pixels[x, y] = RED_PALETTE[index]
                black_pixels[x, y] = BLACK_PALETTE[index]

    output_dir.mkdir(parents=True, exist_ok=True)
    red = Image.new("RGB", CARD_SIZE, CHROMA_KEY)
    black = Image.new("RGB", CARD_SIZE, CHROMA_KEY)
    red.paste(red_crop, (0, 0))
    black.paste(black_crop, (0, 0))
    red.save(output_dir / "lion-red-trace-source.png", optimize=True)
    black.save(output_dir / "lion-black-trace-source.png", optimize=True)
    mask.save(output_dir / "lion-mask.png", optimize=True)
    write_manifest(output_dir / "lion-red-manifest.json", "HSBC Red faceted lion", RED_PALETTE)
    write_manifest(output_dir / "lion-black-manifest.json", "HSBC VS faceted lion", BLACK_PALETTE)


def write_manifest(path: Path, title: str, palette: tuple[tuple[int, int, int], ...]) -> None:
    layers = []
    for index, color in enumerate(palette):
        hex_color = "#" + "".join(f"{value:02X}" for value in color)
        layers.append(
            {
                "id": f"facet-{index + 1:02d}",
                "fill": hex_color,
                "min": list(color),
                "max": list(color),
                "min_area": 8,
                "tolerance": 1.2,
            }
        )
    manifest = {
        "title": title,
        "card_box": [0, 0, CARD_SIZE[0], CARD_SIZE[1]],
        "regions": [
            {
                "id": "faceted-lion",
                "box": [0, 0, TRACE_WIDTH, CARD_SIZE[1]],
                "supersample": 1,
                "layers": layers,
            }
        ],
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--red-background-source", type=Path, required=True)
    parser.add_argument("--black-background-source", type=Path, required=True)
    parser.add_argument("--red-lion-source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    flatten_and_resize(
        args.red_background_source,
        args.output_dir / "background-cat-hsbc-red.png",
        (5, 63, 78),
    )
    flatten_and_resize(
        args.black_background_source,
        args.output_dir / "background-cat-hsbc-vs.png",
        (25, 25, 25),
    )
    build_trace_sources(args.red_lion_source, args.output_dir / "trace-work")


if __name__ == "__main__":
    main()
