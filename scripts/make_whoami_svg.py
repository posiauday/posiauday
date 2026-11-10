"""One terminal window: `$ whoami` -> ASCII portrait beside a neofetch-style card.

    python scripts/make_whoami_svg.py           # writes whoami.svg
    STATIC=1 python scripts/make_whoami_svg.py  # frozen frame for previews

Edit ROWS below. Keep GitHub stats out: the heatmap already shows those.
Needs source-prepped.png + source-mask.png (run scripts/prep_photo.py once).
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

from make_ascii_svg import grid
from theme import BAR_H, DIM, FG, GREEN, HOST, KEY, MONO, USER, prompt, window

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "whoami.svg"
STATIC = os.environ.get("STATIC") == "1"

# ---------------------------------------------------------------- CONTENT ---
ROWS = [
    ("Name", "Uday Posia (he/him)"),
    ("Role", "Power Platform & low-code builder"),
    ("Now", ["Free copy-paste Power Apps components",
             "→ power-apps-components (MIT)"]),
    ("Ships", ["Pulse KPI + Pulse Gantt,",
               "custom visuals for Power BI"]),
    ("Builds", ["PPUniverse · tiffinOS ·", "live-tryon-extension"]),
    ("Automates", "LinkedIn posts with Claude + Actions"),
    ("Stack", "Power Apps · Power BI · Claude · Python"),
    ("Web", "lowcodestacks.com"),
]
# ---------------------------------------------------------------------------

W = 860
PAD = 24
# portrait: 110 cols; glyph width 0.6em, so CHAR_W/LINE_H keeps the photo's aspect
A_FONT, A_CHAR_W, A_LINE_H = 5.5, 3.3, 5.97
INFO_X, I_FONT, I_LINE = 418, 13, 21.5
KEY_W = 10.5 * I_FONT * 0.6  # "Automates:" + gap
ROW_DUR, ROW_STAGGER, START = 0.3, 0.035, 0.5


def main() -> None:
    lines = grid()
    top = BAR_H + 52
    a_h = len(lines) * A_LINE_H
    body, defs, css = [prompt(PAD, BAR_H + 30, "whoami")], [], []

    # --- ASCII portrait, each row wiped in left -> right with a cursor
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = top + (i + 1) * A_LINE_H - 1.2
        lw = len(line) * A_CHAR_W
        t = f'<text x="{PAD}" y="{y:.1f}" xml:space="preserve">{escape(line)}</text>'
        if STATIC:
            body.append(t)
            continue
        b = START + i * ROW_STAGGER
        defs.append(f'<clipPath id="r{i}"><rect x="{PAD}" y="{y - A_LINE_H:.1f}" width="0" height="{A_LINE_H + 1:.1f}">'
                    f'<animate attributeName="width" to="{lw + 1:.1f}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                    f'</rect></clipPath>')
        body.append(f'<g clip-path="url(#r{i})">{t}</g>')
        body.append(f'<rect x="{PAD}" y="{y - A_LINE_H + 1:.1f}" width="{A_CHAR_W}" height="{A_LINE_H - 1:.1f}" fill="{GREEN}" opacity="0">'
                    f'<set attributeName="opacity" to="1" begin="{b:.2f}s"/>'
                    f'<animate attributeName="x" to="{PAD + lw:.1f}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                    f'<set attributeName="opacity" to="0" begin="{b + ROW_DUR:.2f}s"/></rect>')
    portrait = (f'<defs>{"".join(defs)}</defs><g font-family="{MONO}" font-size="{A_FONT}" fill="{FG}">'
                + "".join(body[1:]) + "</g>")

    # --- neofetch info, vertically centred on the portrait
    info = [f'<tspan fill="{GREEN}" font-weight="700">{USER}</tspan><tspan fill="{FG}">@</tspan>'
            f'<tspan fill="{GREEN}" font-weight="700">{HOST}</tspan>',
            f'<tspan fill="{DIM}">{"─" * (len(USER) + len(HOST) + 1)}</tspan>']
    for key, value in ROWS:
        for j, v in enumerate(value if isinstance(value, list) else [value]):
            k = f'<tspan fill="{KEY}" font-weight="700">{escape(key)}</tspan>' if j == 0 else ""
            info.append(f'{k}<tspan x="{INFO_X + KEY_W:.1f}" fill="{FG}">{escape(v)}</tspan>')
    block_h = (len(info) + 2) * I_LINE
    y0 = top + max(0, (a_h - block_h) / 2) + I_FONT
    out = []
    for n, frag in enumerate(info):
        y = y0 + n * I_LINE
        out.append(f'<text class="l" style="animation-delay:{START + 0.6 + n * 0.1:.2f}s" x="{INFO_X}" y="{y:.1f}">{frag}</text>')
    y = y0 + (len(info) + 0.4) * I_LINE
    sw = "".join(f'<rect x="{INFO_X + i * 27}" y="{y - 11:.1f}" width="23" height="13" rx="2" fill="{c}"/>'
                 for i, c in enumerate(["#f85149", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9", "#6e7681"]))
    out.append(f'<g class="l" style="animation-delay:{START + 0.6 + len(info) * 0.1:.2f}s">{sw}</g>')

    h = int(top + a_h + PAD)
    # final prompt with blinking cursor, bottom-right column
    py = h - PAD + 2
    out.append(f'<g class="l" style="animation-delay:{START + len(lines) * ROW_STAGGER + 0.3:.2f}s">'
               f'{prompt(INFO_X, py, "")}<rect class="cur" x="{INFO_X + 17 * I_FONT * 0.6:.1f}" y="{py - 11}" '
               f'width="{I_FONT * 0.6:.1f}" height="14" fill="{FG}"/></g>')
    info_svg = f'<g font-family="{MONO}" font-size="{I_FONT}" xml:space="preserve">{"".join(out)}</g>'

    css = "" if STATIC else (
        ".l{opacity:0;animation:in .45s ease-out forwards}"
        "@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
        ".cur{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}")
    svg = window(W, h, f"{USER}@{HOST}: ~ — zsh", body[0] + portrait + info_svg, css,
                 label="whoami: ASCII portrait and profile card for Uday Posia")
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({W}x{h}, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
