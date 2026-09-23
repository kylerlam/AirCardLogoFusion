#!/usr/bin/env python3
"""Recolor an existing vector mark with a three-color gradient and optional contrast backing."""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def positive_box(value):
    parts = [float(item) for item in value.split(',')]
    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
        raise ValueError('plate-box must be x,y,width,height with positive size')
    return parts


SHAPES = {f'{{{NS}}}{name}' for name in ('path','rect','circle','ellipse','polygon','polyline')}


def fuse(source, output, shape_id, colors, edge, edge_width, plate_box, plate_color,
         plate_opacity, gradient_box, profile):
    if any(not re.fullmatch(r'#[0-9a-fA-F]{6}', color) for color in (*colors, edge, plate_color)):
        raise ValueError('colors must use #RRGGBB')
    if edge_width < 0 or not 0 <= plate_opacity <= 1:
        raise ValueError('invalid edge width or plate opacity')
    tree = ET.parse(source)
    root = tree.getroot()
    if root.tag != f'{{{NS}}}svg':
        raise ValueError('source must have an SVG root')
    if any(node.tag in {f'{{{NS}}}{name}' for name in ('image','text','script','foreignObject')} for node in root.iter()):
        raise ValueError('source must be self-contained vector artwork')
    matches = [node for node in root.iter() if node.get('id') == shape_id]
    if len(matches) != 1 or matches[0].tag not in SHAPES | {f'{{{NS}}}g'}:
        raise ValueError(f'shape-id must identify one vector shape or group: {shape_id}')
    selected = matches[0]
    shapes = [node for node in selected.iter() if node.tag in SHAPES and node.get('fill') != 'none']
    if not shapes:
        raise ValueError(f'no filled vector shapes in: {shape_id}')
    if selected.tag == f'{{{NS}}}g' and not gradient_box:
        raise ValueError('gradient-box is required when shape-id identifies a group')
    box = root.get('viewBox', '').split()
    if len(box) != 4 or float(box[2]) <= 0 or float(box[3]) <= 0:
        raise ValueError('source needs a positive four-number viewBox')
    if profile in {'aircard', 'ratio'} and abs(float(box[2])/float(box[3]) - 85.60/53.98) > 0.01:
        raise ValueError('full-card overlay needs a card-ratio source viewBox')
    if profile == 'aircard':
        # Site-specific natural dimensions align a full-card Logo layer at 100% scale.
        root.set('width', '1536')
        root.set('height', '969')
    defs = root.find(f'{{{NS}}}defs')
    if defs is None:
        defs = ET.Element(f'{{{NS}}}defs')
        root.insert(0, defs)
    if any(node.get('id') in {'fusion-gradient','fusion-soft-plate'} for node in root.iter()):
        raise ValueError('source already uses a reserved fusion id')
    gradient_attrs = {'id':'fusion-gradient','x1':'0%','y1':'0%','x2':'100%','y2':'0%'}
    if gradient_box:
        gx, gy, gw, gh = positive_box(gradient_box)
        gradient_attrs.update({'gradientUnits':'userSpaceOnUse', 'x1':str(gx), 'y1':str(gy), 'x2':str(gx+gw), 'y2':str(gy)})
    gradient = ET.SubElement(defs, f'{{{NS}}}linearGradient', gradient_attrs)
    for offset, color in zip(('0%','50%','100%'), colors):
        ET.SubElement(gradient, f'{{{NS}}}stop', {'offset':offset,'stop-color':color})
    if plate_box:
        x,y,w,h = positive_box(plate_box)
        filtr = ET.SubElement(defs, f'{{{NS}}}filter', {
            'id':'fusion-soft-plate','filterUnits':'userSpaceOnUse',
            'x':str(x-40),'y':str(y-40),'width':str(w+80),'height':str(h+80),
        })
        ET.SubElement(filtr, f'{{{NS}}}feGaussianBlur', {'stdDeviation':'10'})
        plate = ET.Element(f'{{{NS}}}rect', {
            'id':'fusion-local-plate','x':str(x),'y':str(y),'width':str(w),'height':str(h),
            'rx':'24','fill':plate_color,'opacity':str(plate_opacity),'filter':'url(#fusion-soft-plate)',
        })
        root.insert(1, plate)
    for shape in shapes:
        shape.set('fill', 'url(#fusion-gradient)')
        if edge_width:
            shape.set('stroke', edge)
            shape.set('stroke-width', str(edge_width))
            shape.set('stroke-opacity', '0.8')
            shape.set('stroke-linejoin', 'round')
            shape.set('paint-order', 'stroke fill')
    if profile == 'ratio':
        if float(box[0]) != 0 or float(box[1]) != 0:
            raise ValueError('ratio profile currently requires a viewBox starting at 0,0')
        factor = min(8560/float(box[2]), 5398/float(box[3]))
        offset_x = (8560 - float(box[2])*factor)/2
        offset_y = (5398 - float(box[3])*factor)/2
        wrapper = ET.Element(f'{{{NS}}}g', {
            'transform':f'translate({offset_x:.10f} {offset_y:.10f}) scale({factor:.10f})'
        })
        for child in list(root):
            if child.tag not in {f'{{{NS}}}defs', f'{{{NS}}}title', f'{{{NS}}}desc'}:
                root.remove(child)
                wrapper.append(child)
        root.append(wrapper)
        root.set('viewBox', '0 0 8560 5398')
        root.set('width', '85.60mm')
        root.set('height', '53.98mm')
    ET.indent(tree, space='  ')
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding='utf-8', xml_declaration=True)
    print(f'Created {output} (SVG, {profile} profile)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--shape-id', required=True)
    parser.add_argument('--colors', nargs=3, required=True, metavar=('LEFT','MIDDLE','RIGHT'))
    parser.add_argument('--edge', default='#101722')
    parser.add_argument('--edge-width', type=float, default=0)
    parser.add_argument('--plate-box', help='optional x,y,width,height in source SVG coordinates')
    parser.add_argument('--gradient-box', help='x,y,width,height covering a multi-shape logo in source SVG coordinates')
    parser.add_argument('--plate-color', default='#111827')
    parser.add_argument('--plate-opacity', type=float, default=0.22)
    parser.add_argument('--profile', choices=('generic','ratio','aircard'), default='generic')
    args = parser.parse_args()
    try:
        fuse(args.source, args.output, args.shape_id, args.colors, args.edge, args.edge_width,
             args.plate_box, args.plate_color, args.plate_opacity, args.gradient_box, args.profile)
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
