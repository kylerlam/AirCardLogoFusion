#!/usr/bin/env python3
"""Render a fixed Wallet SVG master as a transparent 1536x969 upload PNG."""

import argparse
import base64
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

from check_svg import check

WIDTH, HEIGHT = 1536, 969
CHROME_MAC = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')


def chrome_binary():
    for candidate in (shutil.which('google-chrome'), shutil.which('chromium'), CHROME_MAC):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise RuntimeError('Chrome/Chromium is required to render this SVG; do not install it just for validation')


def validate_png(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n') or data[12:16] != b'IHDR':
        raise ValueError('renderer did not return a PNG')
    width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data[16:29])
    if (width, height, depth, color, compression, filtering, interlace) != (WIDTH, HEIGHT, 8, 6, 0, 0, 0):
        raise ValueError('PNG must be 1536x969, 8-bit, non-interlaced RGBA')
    parts, offset = [], 8
    while offset + 12 <= len(data):
        length = int.from_bytes(data[offset:offset+4], 'big')
        kind = data[offset+4:offset+8]
        if kind == b'IDAT':
            parts.append(data[offset+8:offset+8+length])
        offset += length + 12
        if kind == b'IEND':
            break
    if not parts:
        raise ValueError('PNG is missing image data')
    first_scanline = zlib.decompress(b''.join(parts))
    if first_scanline[4] != 0:
        raise ValueError('top-left pixel is opaque; expected a transparent overlay')


def render(svg, png):
    check(svg)
    encoded = base64.b64encode(svg.read_bytes()).decode('ascii')
    html = (
        '<!doctype html><html><body><pre id="result">WAIT</pre>'
        '<img id="logo" src="data:image/svg+xml;base64,' + encoded + '">'
        '<script>const img=document.getElementById("logo");'
        'img.onload=()=>{const c=document.createElement("canvas");'
        'c.width=1536;c.height=969;c.getContext("2d").drawImage(img,0,0,1536,969);'
        'document.getElementById("result").textContent=c.toDataURL("image/png")};'
        'img.onerror=()=>document.getElementById("result").textContent="ERROR";'
        '</script></body></html>'
    )
    with tempfile.TemporaryDirectory(prefix='wallet-svg-') as temporary:
        page = Path(temporary) / 'render.html'
        page.write_text(html, encoding='utf-8')
        command = [chrome_binary(), '--headless', '--disable-gpu',
                   '--disable-background-networking', '--no-first-run',
                   '--virtual-time-budget=3000', '--user-data-dir=' + str(Path(temporary) / 'profile'),
                   '--dump-dom', page.as_uri()]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=12, check=True)
        except subprocess.TimeoutExpired as exc:
            # Some Chrome builds keep background processes alive after --dump-dom
            # has emitted the complete page. subprocess.run terminates them on
            # timeout; the captured DOM is usable if it contains PNG data.
            if not exc.stdout or b'data:image/png;base64,' not in exc.stdout:
                raise RuntimeError('Chrome timed out before producing PNG pixels') from exc
            output = exc.stdout
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or b'').decode('utf-8', 'replace')[-500:]
            raise RuntimeError(f'Chrome exited {exc.returncode}: {details}') from exc
        else:
            output = result.stdout
    match = re.search(rb'data:image/png;base64,([A-Za-z0-9+/=]+)', output)
    if not match:
        raise RuntimeError('Chrome did not return PNG pixels')
    data = base64.b64decode(match.group(1), validate=True)
    validate_png(data)
    png.parent.mkdir(parents=True, exist_ok=True)
    png.write_bytes(data)
    print(f'Created {png} ({WIDTH}x{HEIGHT}, transparent RGBA)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('svg', type=Path)
    parser.add_argument('png', type=Path)
    args = parser.parse_args()
    try:
        render(args.svg, args.png)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
