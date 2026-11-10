"""Render data/contributions.json as a terminal window: last 26 weeks + stats panel.

    python scripts/render_heatmap_svg.py            # writes contrib-heatmap.svg
    STATIC=1 python scripts/render_heatmap_svg.py   # frozen frame

The full-year calendar already sits under every profile, so this one zooms in on
recent weeks and puts the numbers that matter beside it. Boxes slide in along
diagonals once on load, then freeze (CSS keyframes, no loop).
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

from theme import BAR_H, DIM, FG, GREEN, MONO, NEON, prompt, window

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

WEEKS = 26
# none -> brightest (level 5 is a neon top end for the busiest ~2% of days)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", NEON]
W = 860
CELL, GAP = 15, 4
PITCH = CELL + GAP
LEFT, PAD = 58, 24
PANEL_X = LEFT + WEEKS * PITCH + 34


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days, st = data["days"], data["stats"]
    nz = sorted(d["count"] for d in days if d["count"])
    neon = nz[int(len(nz) * 0.98)] if len(nz) >= 20 else None

    last = date.fromisoformat(days[-1]["date"])
    start = last - timedelta(days=(last.weekday() + 1) % 7) - timedelta(weeks=WEEKS - 1)  # a Sunday
    by_date = {d["date"]: d for d in days}
    top = BAR_H + 74
    cells, months, max_diag = [], {}, 0
    for wk in range(WEEKS):
        for row in range(7):
            dt = start + timedelta(weeks=wk, days=row)
            if dt > last:
                continue
            d = by_date.get(dt.isoformat(), {"count": 0, "level": 0})
            if dt.day <= 7 and row == 0 and wk <= WEEKS - 2:
                months[wk] = dt.strftime("%b")
            level = d["level"]
            if neon is not None and d["count"] >= neon > 0:
                level = 5
            diag = wk + row
            max_diag = max(max_diag, diag)
            title = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {dt:%b %-d, %Y}'
            cells.append(f'<rect class="c d{diag}" x="{LEFT + wk * PITCH}" y="{top + row * PITCH}" '
                         f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[level]}"><title>{title}</title></rect>')

    grid_bottom = top + 7 * PITCH - GAP
    labels = [f'<text x="{LEFT + wk * PITCH}" y="{top - 10}">{m}</text>' for wk, m in months.items()]
    labels += [f'<text x="{LEFT - 10}" y="{top + r * PITCH + CELL - 3}" text-anchor="end">{n}</text>'
               for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))]
    fy = grid_bottom + 30
    labels.append(f'<text x="{LEFT}" y="{fy}">last {WEEKS} weeks</text>')
    lx = LEFT + WEEKS * PITCH - 6 * 15 - 36
    labels.append(f'<text x="{lx - 8}" y="{fy}" text-anchor="end">Less</text>')
    labels += [f'<rect x="{lx + i * 15}" y="{fy - 10}" width="11" height="11" rx="2.5" fill="{c}"/>'
               for i, c in enumerate(PALETTE)]
    labels.append(f'<text x="{lx + 6 * 15 + 4}" y="{fy}">More</text>')

    best = st["best_day"]
    stats = [
        (f'{st["total"]:,}', "contributions"),
        (f'{st["active_days"]}', "active days"),
        (f'{st["longest_streak"]}d', "longest streak"),
        (f'{best["count"]}', f'best day, {date.fromisoformat(best["date"]):%b %-d}'),
    ]
    panel = [f'<text x="{PANEL_X}" y="{top - 10}" font-size="11" fill="{DIM}">past 12 months</text>',
             f'<line x1="{PANEL_X - 18}" y1="{top - 22}" x2="{PANEL_X - 18}" y2="{fy + 4}" stroke="#30363d"/>']
    for i, (num, lab) in enumerate(stats):
        cx, cy = PANEL_X + (i % 2) * 132, top + 4 + (i // 2) * 74
        panel.append(f'<g class="s" style="animation-delay:{1.2 + i * 0.15:.2f}s">'
                     f'<text x="{cx}" y="{cy + 22}" font-size="28" font-weight="700" fill="{NEON if i == 0 else FG}">{num}</text>'
                     f'<text x="{cx}" y="{cy + 44}" font-size="11.5" fill="{DIM}">{lab}</text></g>')
    if data.get("sample"):
        panel.append(f'<text x="{PANEL_X}" y="{fy}" font-size="11" fill="#f85149">SAMPLE DATA</text>')
    elif st["current_streak"]:
        panel.append(f'<text class="s" x="{PANEL_X}" y="{fy}" font-size="11.5" fill="{GREEN}">● '
                     f'{st["current_streak"]}-day streak running</text>')

    h = int(fy + PAD)
    css = ""
    if not STATIC:
        step = 1.1 / max(max_diag, 1)
        css = (".c{opacity:0;transform-box:fill-box;transform-origin:center;"
               "animation:drop .4s cubic-bezier(.2,.7,.3,1) forwards}"
               "@keyframes drop{from{opacity:0;transform:translateY(-7px) scale(.6)}to{opacity:1;transform:none}}"
               ".s{opacity:0;animation:fade .5s ease-out forwards;animation-delay:1.4s}@keyframes fade{to{opacity:1}}"
               + "".join(f".d{k}{{animation-delay:{0.25 + k * step:.3f}s}}" for k in range(max_diag + 1)))
    body = (prompt(PAD, BAR_H + 30, f"./contributions.sh --weeks {WEEKS}")
            + f'<g font-family="{MONO}" font-size="11" fill="{DIM}">{"".join(labels)}</g>'
            + f'<g>{"".join(cells)}</g>'
            + f'<g font-family="{MONO}">{"".join(panel)}</g>')
    OUT.write_text(window(W, h, "uday@github: ~ — contributions", body, css,
                          label=f'{st["total"]:,} contributions in the last year'))
    print(f"wrote {OUT.name} ({W}x{h}, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
