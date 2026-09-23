#!/usr/bin/env python3
"""Check the fixed-size, transparent, outlined SVG overlay contract."""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EXPECTED = {"width": "85.60mm", "height": "53.98mm", "viewBox": "0 0 1536 969"}
FORBIDDEN = {"image", "text", "tspan", "textPath", "foreignObject", "script", "iframe"}
DRAWING = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "use"}


def local(value):
    return value.rsplit("}", 1)[-1]


def check(path):
    root = ET.parse(path).getroot()
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("root must be an SVG element in the SVG namespace")
    for key, expected in EXPECTED.items():
        if root.get(key) != expected:
            raise ValueError(f"{key} must be exactly {expected!r}")
    drawing_count = 0
    for node in root.iter():
        name = local(node.tag)
        if name in FORBIDDEN:
            raise ValueError(f"forbidden raster, text or active element: {name}")
        if name in DRAWING:
            drawing_count += 1
        if name == "rect":
            try:
                x, y = float(node.get("x", "0")), float(node.get("y", "0"))
                w, h = float(node.get("width", "0")), float(node.get("height", "0"))
            except ValueError:
                x = y = w = h = 0
            if x <= 0 and y <= 0 and w >= 1536 and h >= 969:
                raise ValueError("a full-canvas rectangle would hide the background")
        for key, value in node.attrib.items():
            attr = local(key).lower()
            if attr.startswith("on"):
                raise ValueError(f"event handler is not allowed: {key}")
            if attr in {"href", "src"} and not value.startswith("#"):
                raise ValueError(f"external or embedded resource: {value[:80]}")
            for url in re.findall(r"url\(\s*['\"]?([^)'\"]+)", value, re.I):
                if not url.startswith("#"):
                    raise ValueError(f"external resource: {url[:80]}")
    if not drawing_count:
        raise ValueError("SVG has no visible vector shapes")
    return drawing_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    args = parser.parse_args()
    try:
        count = check(args.svg)
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: {args.svg} ({count} vector shapes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
