"""Render data/contributions.json as an animated 53-week heatmap SVG.

    python scripts/render_heatmap_svg.py            # writes contrib-heatmap.svg
    STATIC=1 python scripts/render_heatmap_svg.py   # frozen frame

Boxes slide in along diagonals once on load, then freeze (CSS keyframes, no loop).
"""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

# none -> brightest (level 5 is a neon top end for the busiest ~2% of days)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, DIM = "#0d1117", "#c9d1d9", "#8b949e"
W = 860
CELL, GAP = 11.6, 3.4
PITCH = CELL + GAP
LEFT, TOP = 44, 46
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days, st = data["days"], data["stats"]
    nz = sorted(d["count"] for d in days if d["count"])
    neon = nz[int(len(nz) * 0.98)] if len(nz) >= 20 else None

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = row 0, like GitHub
    cells, months, max_diag = [], {}, 0
    for i, d in enumerate(days):
        idx = i + offset
        wk, row = divmod(idx, 7)
        dt = date.fromisoformat(d["date"])
        if dt.day <= 7 and row == 0 or (i == 0 and dt.day <= 20):
            months.setdefault(wk, dt.strftime("%b"))
        level = d["level"]
        if neon is not None and d["count"] >= neon and d["count"] > 0:
            level = 5
        x, y = LEFT + wk * PITCH, TOP + row * PITCH
        diag = wk + row
        max_diag = max(max_diag, diag)
        title = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {dt:%b %-d, %Y}'
        cells.append(f'<rect class="c d{diag}" x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" '
                     f'rx="2.5" fill="{PALETTE[level]}"><title>{title}</title></rect>')

    grid_bottom = TOP + 7 * PITCH
    H = int(grid_bottom + 52)
    last_wk = (len(days) - 1 + offset) // 7
    labels = [f'<text x="{LEFT + wk * PITCH:.1f}" y="{TOP - 10}">{m}</text>'
              for wk, m in sorted(months.items()) if wk <= last_wk - 2]
    labels += [f'<text x="{LEFT - 10}" y="{TOP + r * PITCH + CELL - 2:.1f}" text-anchor="end">{n}</text>'
               for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))]

    fy = grid_bottom + 26
    total = f'{st["total"]:,} contributions in the last year'
    extra = f'streak {st["current_streak"]}d · longest {st["longest_streak"]}d · best day {st["best_day"]["count"]}'
    if data.get("sample"):
        extra += " · SAMPLE DATA"
    legend_x = W - 22 - 6 * 15 - 34
    legend = [f'<text x="{legend_x - 8}" y="{fy}" text-anchor="end">Less</text>']
    legend += [f'<rect x="{legend_x + i * 15}" y="{fy - 10}" width="11" height="11" rx="2.5" fill="{c}"/>'
               for i, c in enumerate(PALETTE)]
    legend.append(f'<text x="{legend_x + 6 * 15 + 4}" y="{fy}">More</text>')

    css = ""
    if not STATIC:
        step = 1.6 / max(max_diag, 1)
        css = ("<style>.c{opacity:0;transform-box:fill-box;transform-origin:center;"
               "animation:drop .4s cubic-bezier(.2,.7,.3,1) forwards}"
               "@keyframes drop{from{opacity:0;transform:translateY(-7px) scale(.6)}"
               "to{opacity:1;transform:none}}"
               ".ft{opacity:0;animation:fade .6s ease-out forwards;animation-delay:" + f"{1.6 + 0.4:.1f}s" + "}"
               "@keyframes fade{to{opacity:1}}"
               + "".join(f".d{k}{{animation-delay:{0.2 + k * step:.3f}s}}" for k in range(max_diag + 1))
               + "</style>")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total}">
{css}
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<g font-family="{MONO}" font-size="11" fill="{DIM}">{"".join(labels)}</g>
<g>{"".join(cells)}</g>
<g class="ft" font-family="{MONO}" font-size="11.5" fill="{DIM}">
<text x="{LEFT}" y="{fy}"><tspan fill="{FG}" font-weight="700">{total}</tspan>  <tspan>{extra}</tspan></text>
{"".join(legend)}
</g>
</svg>'''
    OUT.write_text(svg)
    print(f"wrote {OUT.name}: {len(days)} days, {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
