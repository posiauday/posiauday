"""ASCII portrait engine: grid() is used by make_whoami_svg.py. Run alone for a standalone SVG.

    python scripts/make_ascii_svg.py          # writes ascii-portrait.svg
    STATIC=1 python scripts/make_ascii_svg.py # frozen frame (no animation)

Each row is revealed by a left-to-right clip wipe with a block cursor riding the
edge, staggered top to bottom. Plays once, then freezes (SMIL, fill="freeze").
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ascii-portrait.svg"

# dark (sparse) -> bright (dense): glyphs are light on a dark terminal, so dense = bright
RAMP = " .`:-=+*cs#%@"
COLS = 110
CHAR_W, LINE_H, FONT = 4.2, 7.6, 7
PAD = 18
BG, FG, CURSOR = "#0d1117", "#c9d1d9", "#3fb950"
ROW_DUR, ROW_STAGGER, START = 0.35, 0.045, 0.3
STATIC = os.environ.get("STATIC") == "1"
# Default: bright pixels -> dense glyphs (a "positive" image on the dark terminal).
# INVERT=1 flips it: dark pixels get dense glyphs (classic ink look).
INVERT = os.environ.get("INVERT", "0") == "1"
GAMMA = float(os.environ.get("GAMMA", "1.0"))


def grid(cols: int = COLS) -> list[str]:
    img = Image.open(ROOT / "source-prepped.png").convert("L")
    mask_path = ROOT / "source-mask.png"
    mask = Image.open(mask_path).convert("L") if mask_path.exists() else None
    w, h = img.size
    rows = round(cols * (h / w) * (CHAR_W / LINE_H))
    g = np.asarray(img.resize((cols, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    m = (np.asarray(mask.resize((cols, rows), Image.LANCZOS), dtype=np.float32) / 255.0
         if mask else (g < 0.97).astype(np.float32))
    # stretch contrast using only the subject's pixels
    inside = g[m >= 0.35]
    if inside.size:
        lo, hi = np.percentile(inside, [3, 97])
        g = np.clip((g - lo) / max(hi - lo, 1e-6), 0, 1)
    if INVERT:
        g = 1 - g
    g = g ** GAMMA
    lines = []
    for y in range(rows):
        chars = []
        for x in range(cols):
            if m[y, x] < 0.35:
                chars.append(" ")
                continue
            # higher value -> denser glyph; keep at least '.' inside the subject
            idx = 1 + int(g[y, x] * (len(RAMP) - 2) + 0.5)
            chars.append(RAMP[min(idx, len(RAMP) - 1)])
        lines.append("".join(chars).rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def main() -> None:
    lines = grid()
    width = PAD * 2 + COLS * CHAR_W
    height = PAD * 2 + len(lines) * LINE_H
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="ASCII portrait">',
        f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>',
        "<defs>",
    ]
    body = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = PAD + (i + 1) * LINE_H - 1.6
        lw = len(line) * CHAR_W
        begin = START + i * ROW_STAGGER
        text = (f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve">{escape(line)}</text>')
        if STATIC:
            body.append(text)
            continue
        out.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{y - LINE_H:.1f}" width="0" height="{LINE_H + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{lw + 1:.1f}" begin="{begin:.2f}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(f'<g clip-path="url(#r{i})">{text}</g>')
        body.append(
            f'<rect x="{PAD}" y="{y - LINE_H + 1.4:.1f}" width="{CHAR_W:.1f}" height="{LINE_H - 1:.1f}" '
            f'fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + lw:.1f}" begin="{begin:.2f}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.2f}s"/></rect>'
        )
    out.append("</defs>")
    out.append(
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'DejaVu Sans Mono\',monospace" '
        f'font-size="{FONT}" fill="{FG}" letter-spacing="0">'
    )
    out.extend(body)
    out.append("</g></svg>")
    OUT.write_text("\n".join(out))
    print(f"wrote {OUT.name}: {len(lines)} rows x {COLS} cols, {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
