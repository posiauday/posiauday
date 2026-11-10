"""Shared look for every profile SVG: one terminal-window style everywhere."""
from xml.sax.saxutils import escape

BG, BAR, BORDER = "#0d1117", "#161b22", "#30363d"
FG, DIM, KEY, GREEN, NEON = "#c9d1d9", "#8b949e", "#58a6ff", "#3fb950", "#69f0a0"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
USER, HOST = "uday", "github"
BAR_H = 30


def prompt(x: float, y: float, cmd: str, size: float = 13) -> str:
    """`uday@github ~ $ cmd` the way a shell prints it."""
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}">'
            f'<tspan fill="{GREEN}" font-weight="700">{USER}@{HOST}</tspan>'
            f'<tspan fill="{KEY}" font-weight="700"> ~</tspan>'
            f'<tspan fill="{FG}"> $ {escape(cmd)}</tspan></text>')


def window(w: int, h: int, title: str, body: str, css: str = "", label: str = "") -> str:
    dots = "".join(f'<circle cx="{20 + i * 18}" cy="{BAR_H / 2}" r="5.5" fill="{c}"/>'
                   for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label or title)}">
{f"<style>{css}</style>" if css else ""}
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M.5 10.5a10 10 0 0 1 10-10h{w - 21}a10 10 0 0 1 10 10v{BAR_H - 10}h-{w - 1}z" fill="{BAR}"/>
<line x1=".5" y1="{BAR_H + .5}" x2="{w - .5}" y2="{BAR_H + .5}" stroke="{BORDER}"/>
{dots}
<text x="{w / 2}" y="{BAR_H / 2 + 4}" text-anchor="middle" fill="{DIM}" font-family="{MONO}" font-size="11.5">{escape(title)}</text>
{body}
</svg>'''
