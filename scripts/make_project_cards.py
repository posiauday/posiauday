"""Clickable project cards (one SVG per repo) with live stars/forks.

    python scripts/make_project_cards.py     # writes card-<repo>.svg

Reads the public GitHub API (uses GITHUB_TOKEN if set, as in Actions). If the API
is unreachable it falls back to the last good numbers in data/repos.json.
"""
import json
import os
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

from theme import BAR_H, DIM, FG, KEY, MONO, window

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "repos.json"
OWNER = "posiauday"
# repo -> optional overrides (description shown on the card, language label/colour)
REPOS = {
    "power-apps-components": {"lang": ("Power Apps", "#b464d4"),
                              "desc": "Free copy-paste Power Apps components from LowCodeStacks. MIT licensed."},
    "linkedin-automation": {"desc": "Daily LinkedIn posts on autopilot with Claude, DALL·E and GitHub Actions."},
}
LANG_COLORS = {"Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a"}
W, H = 420, 150


def fetch() -> dict:
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    try:
        import requests
        headers = {"Accept": "application/vnd.github+json"}
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
        for name in REPOS:
            r = requests.get(f"https://api.github.com/repos/{OWNER}/{name}", headers=headers, timeout=20)
            r.raise_for_status()
            j = r.json()
            cache[name] = {k: j[k] for k in ("description", "stargazers_count", "forks_count", "language")}
        CACHE.write_text(json.dumps(cache, indent=1))
    except Exception as e:  # keep the last good numbers
        print(f"GitHub API unavailable ({e.__class__.__name__}); using {CACHE.name}")
    return cache


def card(name: str, info: dict, extra: dict) -> str:
    desc = extra.get("desc") or info.get("description") or ""
    lines = textwrap.wrap(desc, 46)[:2]
    lang, color = extra.get("lang") or (info.get("language"), LANG_COLORS.get(info.get("language"), DIM))
    y = BAR_H + 30
    body = [f'<text x="20" y="{y}" font-size="15" font-weight="700" fill="{KEY}">{escape(name)}/</text>']
    body += [f'<text x="20" y="{y + 26 + i * 19}" font-size="12.5" fill="{FG}">{escape(t)}</text>'
             for i, t in enumerate(lines)]
    fy = H - 16
    x = 20
    foot = []
    if lang:
        foot.append(f'<circle cx="{x + 5}" cy="{fy - 4}" r="5" fill="{color}"/>'
                    f'<text x="{x + 15}" y="{fy}">{escape(lang)}</text>')
        x += 15 + len(lang) * 7.2 + 18
    foot.append(f'<text x="{x}" y="{fy}">★ {info.get("stargazers_count", 0)}</text>')
    x += 60
    foot.append(f'<text x="{x}" y="{fy}">⑂ {info.get("forks_count", 0)}</text>')
    foot.append(f'<text x="{W - 20}" y="{fy}" text-anchor="end" fill="{KEY}">open →</text>')
    svg_body = (f'<g font-family="{MONO}">{"".join(body)}</g>'
                f'<g font-family="{MONO}" font-size="12" fill="{DIM}">{"".join(foot)}</g>')
    return window(W, H, f"~/{name}", svg_body, label=f"{name}: {desc}")


def main() -> None:
    data = fetch()
    for name, extra in REPOS.items():
        out = ROOT / f"card-{name}.svg"
        out.write_text(card(name, data.get(name, {}), extra))
        print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
