#!/usr/bin/env python3
"""Merge checked AirCard SVG layers without changing their coordinates."""

from __future__ import annotations

import argparse
import copy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from check_svg import check


NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def merge(inputs: list[Path], output: Path, title: str) -> None:
    root = ET.Element(
        f"{{{NS}}}svg",
        {"width": "85.60mm", "height": "53.98mm", "viewBox": "0 0 1536 969"},
    )
    ET.SubElement(root, f"{{{NS}}}title").text = title
    ET.SubElement(root, f"{{{NS}}}desc").text = (
        "Reusable vector card identifiers and visible masked card number; transparent AirCard canvas."
    )
    for path in inputs:
        check(path)
        source = ET.parse(path).getroot()
        for node in source:
            if node.tag == f"{{{NS}}}g":
                root.append(copy.deepcopy(node))
    ET.indent(root, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    check(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        merge(args.inputs, args.output, args.title)
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
