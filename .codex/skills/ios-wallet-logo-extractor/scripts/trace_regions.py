#!/usr/bin/env python3
"""Trace high-contrast screenshot regions to genuine SVG paths using a small JSON color manifest."""
import argparse
import json
import math
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from PIL import Image
from check_svg import check

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
WIDTH, HEIGHT = 1536, 969


def matches(rgb, rule):
    lo, hi = rule.get("min", [0, 0, 0]), rule.get("max", [255, 255, 255])
    if not all(lo[i] <= rgb[i] <= hi[i] for i in range(3)):
        return False
    channels = dict(zip("rgb", rgb))
    for key, limit in rule.get("diff_min", {}).items():
        a, b = key.split("-")
        if channels[a] - channels[b] < limit:
            return False
    for key, limit in rule.get("diff_max", {}).items():
        a, b = key.split("-")
        if channels[a] - channels[b] > limit:
            return False
    return True


def filtered_components(mask, min_area):
    remaining = set(mask)
    kept = set()
    while remaining:
        start = remaining.pop()
        group = {start}
        stack = [start]
        while stack:
            x, y = stack.pop()
            for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if point in remaining:
                    remaining.remove(point)
                    group.add(point)
                    stack.append(point)
        if len(group) >= min_area:
            kept.update(group)
    return kept


def polygon_loops(mask):
    outgoing = defaultdict(list)
    unused = set()
    for x, y in mask:
        sides = (
            ((x, y - 1), (x, y), (x + 1, y)),
            ((x + 1, y), (x + 1, y), (x + 1, y + 1)),
            ((x, y + 1), (x + 1, y + 1), (x, y + 1)),
            ((x - 1, y), (x, y + 1), (x, y)),
        )
        for neighbor, start, end in sides:
            if neighbor not in mask:
                edge = (start, end)
                unused.add(edge)
                outgoing[start].append(edge)
    directions = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
    loops = []
    while unused:
        edge = next(iter(unused))
        origin = edge[0]
        points = [origin]
        while True:
            unused.remove(edge)
            start, end = edge
            points.append(end)
            if end == origin:
                break
            choices = [item for item in outgoing[end] if item in unused]
            if not choices:
                raise ValueError("open boundary while tracing color mask")
            current = directions[(end[0] - start[0], end[1] - start[1])]
            def rank(item):
                target = item[1]
                next_dir = directions[(target[0] - end[0], target[1] - end[1])]
                turn = (next_dir - current) % 4
                return {1: 0, 0: 1, 3: 2, 2: 3}[turn]
            edge = min(choices, key=rank)
        cycle = points[:-1]
        corner = []
        for i, point in enumerate(cycle):
            previous, following = cycle[i-1], cycle[(i+1) % len(cycle)]
            a = (point[0] - previous[0], point[1] - previous[1])
            b = (following[0] - point[0], following[1] - point[1])
            if a[0] * b[1] != a[1] * b[0]:
                corner.append(point)
        if len(corner) >= 3:
            loops.append(corner)
    return loops


def distance(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == dy == 0:
        return math.dist(point, a)
    return abs(dy * point[0] - dx * point[1] + b[0] * a[1] - b[1] * a[0]) / math.hypot(dx, dy)


def rdp(points, tolerance):
    if len(points) <= 2:
        return points
    first, last = points[0], points[-1]
    index = max(range(1, len(points)-1), key=lambda i: distance(points[i], first, last))
    if distance(points[index], first, last) <= tolerance:
        return [first, last]
    return rdp(points[:index+1], tolerance)[:-1] + rdp(points[index:], tolerance)


def simplify_loop(loop, tolerance):
    if len(loop) < 8 or tolerance <= 0:
        return loop
    anchor = max(range(1, len(loop)), key=lambda i: math.dist(loop[i], loop[0]))
    one = rdp(loop[:anchor+1], tolerance)
    two = rdp(loop[anchor:] + [loop[0]], tolerance)
    result = one[:-1] + two[:-1]
    return result if len(result) >= 3 else loop


def trace(image_path, manifest_path, output):
    config = json.loads(manifest_path.read_text(encoding="utf-8"))
    card = config["card_box"]
    if len(card) != 4 or card[2] <= card[0] or card[3] <= card[1]:
        raise ValueError("card_box must be [left, top, right, bottom]")
    photo = Image.open(image_path).convert("RGB")
    if not (0 <= card[0] < card[2] <= photo.width and 0 <= card[1] < card[3] <= photo.height):
        raise ValueError("card_box extends beyond the screenshot")
    sx, sy = WIDTH / (card[2]-card[0]), HEIGHT / (card[3]-card[1])
    root = ET.Element(f"{{{NS}}}svg", {"width": "85.60mm", "height": "53.98mm", "viewBox": "0 0 1536 969"})
    ET.SubElement(root, f"{{{NS}}}title").text = config.get("title", "Wallet card foreground")
    ET.SubElement(root, f"{{{NS}}}desc").text = "Screenshot-derived vector marks; transparent card canvas. Background art and Wallet UI omitted."
    count = 0
    for region in config["regions"]:
        box = region["box"]
        if len(box) != 4 or box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError(f"bad box for {region['id']}")
        scale = int(region.get("supersample", 3))
        if scale < 1 or scale > 4:
            raise ValueError("supersample must be 1..4")
        crop = photo.crop(tuple(box))
        resized = crop.resize((crop.width*scale, crop.height*scale), Image.Resampling.BICUBIC)
        pixels = resized.load()
        group = ET.SubElement(root, f"{{{NS}}}g", {"id": region["id"]})
        for layer in region["layers"]:
            mask = {(x,y) for y in range(resized.height) for x in range(resized.width) if matches(pixels[x,y], layer)}
            mask = filtered_components(mask, int(layer.get("min_area", 4)))
            if not mask:
                raise ValueError(f"no visible pixels for {region['id']}/{layer['id']}")
            loops = polygon_loops(mask)
            commands = []
            for loop in loops:
                loop = simplify_loop(loop, float(layer.get("tolerance", 0.8)))
                coords = [((box[0]+x/scale-card[0])*sx, (box[1]+y/scale-card[1])*sy) for x,y in loop]
                commands.append("M" + " L".join(f"{x:.2f},{y:.2f}" for x,y in coords) + " Z")
            ET.SubElement(group, f"{{{NS}}}path", {"id":layer["id"], "fill":layer["fill"], "fill-rule":"evenodd", "d":" ".join(commands)})
            count += 1
            print(f"{region['id']}/{layer['id']}: {len(mask)} mask pixels, {len(loops)} contours")
    ET.indent(root, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    check(output)
    print(f"Created {output} ({count} vector color layers)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        trace(args.image, args.manifest, args.output)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
