"""Hand-authored neofetch-style info card.

    python scripts/make_info_card.py           # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py  # frozen frame for local previews

Edit the CONTENT block below; everything else is layout. Keep GitHub stats out
of here: the contribution graph already covers those, so the card is for the
story the numbers can't tell.
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

# ---------------------------------------------------------------- CONTENT ---
USER, HOST = "uday", "github"
ROWS = [
    # (key, value)  -- value may be a list to wrap onto continuation lines
    ("OS", "Human · builder mode"),
    ("Name", "Uday Posia (he/him)"),
    ("Role", "Power Platform & low-code builder"),
    ("Web", "lowcodestacks.com"),
    ("Now", ["Free copy-paste Power Apps components",
             "→ power-apps-components (MIT)"]),
    ("Shipping", ["Pulse KPI + Pulse Gantt:",
                  "custom visuals for Power BI"]),
    ("Building", "PPUniverse · tiffinOS · live-tryon-extension"),
    ("Automating", "LinkedIn posts with Claude + Actions"),
    ("Stack", "Power Apps · Power BI · Claude · Python"),
]
# ---------------------------------------------------------------------------

W, H = 490, 372
PAD_X, TOP = 22, 34
LINE_H, FONT = 19, 12.5
CHAR_W = FONT * 0.6
KEY_COL = 12  # chars reserved for "Highlights: "
BG, BAR, FG, DIM = "#0d1117", "#161b22", "#c9d1d9", "#8b949e"
KEY, ACCENT, USERC = "#58a6ff", "#3fb950", "#3fb950"
SWATCHES = ["#f85149", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9", "#6e7681"]
STAGGER, START = 0.12, 0.4


def main() -> None:
    lines: list[str] = []  # each is an SVG <text>/<g> fragment
    y = TOP + 26

    def add(fragment: str) -> None:
        lines.append(fragment)

    title = f'<tspan fill="{USERC}" font-weight="700">{USER}</tspan><tspan fill="{FG}">@</tspan>' \
            f'<tspan fill="{USERC}" font-weight="700">{HOST}</tspan>'
    add(f'<text x="{PAD_X}" y="{y}">{title}</text>')
    y += LINE_H
    add(f'<text x="{PAD_X}" y="{y}" fill="{DIM}">{"-" * (len(USER) + len(HOST) + 1)}</text>')
    for key, value in ROWS:
        values = value if isinstance(value, list) else [value]
        for i, v in enumerate(values):
            y += LINE_H
            k = f'<tspan fill="{KEY}" font-weight="700">{escape(key)}</tspan><tspan fill="{FG}">:</tspan>' if i == 0 else ""
            add(f'<text x="{PAD_X}" y="{y}">{k}'
                f'<tspan x="{PAD_X + KEY_COL * CHAR_W:.1f}" fill="{FG}">{escape(v)}</tspan></text>')
    y += LINE_H + 4
    sw = "".join(
        f'<rect x="{PAD_X + i * 26}" y="{y - 12}" width="22" height="13" rx="2" fill="{c}"/>'
        for i, c in enumerate(SWATCHES))
    add(f"<g>{sw}</g>")

    css = ""
    if not STATIC:
        css = (
            "<style>"
            ".l{opacity:0;transform:translateX(-8px);animation:in .45s ease-out forwards}"
            "@keyframes in{to{opacity:1;transform:translateX(0)}}"
            ".cur{animation:blink 1s steps(1) infinite}"
            "@keyframes blink{50%{opacity:0}}"
            + "".join(f".l{i}{{animation-delay:{START + i * STAGGER:.2f}s}}" for i in range(len(lines)))
            + "</style>"
        )
    body = [f'<g class="l l{i}">{frag}</g>' if not STATIC else frag for i, frag in enumerate(lines)]
    # prompt + blinking cursor under the content
    y += LINE_H + 4
    prompt = (f'<text x="{PAD_X}" y="{y}"><tspan fill="{ACCENT}">❯</tspan></text>'
              f'<rect class="cur" x="{PAD_X + 2 * CHAR_W:.1f}" y="{y - 11}" width="{CHAR_W:.1f}" height="14" fill="{FG}"/>')
    body.append(f'<g class="l l{len(lines)}">{prompt}</g>' if not STATIC else prompt)
    if not STATIC:
        css = css.replace("</style>", f".l{len(lines)}{{animation-delay:{START + len(lines) * STAGGER:.2f}s}}</style>")

    dots = "".join(f'<circle cx="{18 + i * 16}" cy="14" r="5" fill="{c}"/>'
                   for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="neofetch-style info card for {USER}">
{css}
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<path d="M0 10a10 10 0 0 1 10-10h{W - 20}a10 10 0 0 1 10 10v18H0z" fill="{BAR}"/>
{dots}
<text x="{W / 2}" y="18" text-anchor="middle" fill="{DIM}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">{USER}@{HOST}: ~ — neofetch</text>
<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace" font-size="{FONT}" xml:space="preserve">
{chr(10).join(body)}
</g>
</svg>'''
    if y > H - 8:
        print(f"warning: content ends at y={y}, taller than card height {H}; trim ROWS or raise H")
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({len(lines)} animated lines)")


if __name__ == "__main__":
    main()
