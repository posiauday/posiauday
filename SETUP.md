# Animated GitHub profile — setup notes

This is the special `posiauday/posiauday` repo: its README renders at the top of github.com/posiauday.

## What's in the kit

| File | What it is | Regenerate when |
|---|---|---|
| `contrib-heatmap.svg` | 53-week contribution graph, boxes slide in diagonally | Daily, by GitHub Actions |
| `ascii-portrait.svg` | Your avatar as monochrome ASCII that types itself row by row | You change your photo |
| `info-card.svg` | neofetch-style card that prints line by line | You change your details |
| `README.md` | Terminal-style layout that places the three SVGs | — |
| `.github/workflows/update-profile-art.yml` | Daily cron that refreshes the heatmap | — |
| `preview.html` | Open locally to see the README layout with animations (git-ignored) | — |

The heatmap is refreshed daily (~06:17 UTC), on every push to `main`, and on demand from
**Actions → Update profile art → Run workflow**. If a run fails to push, set
Settings → Actions → General → Workflow permissions to **Read and write permissions**.

## Editing

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt

# info card: edit ROWS at the top of the script, then
python scripts/make_info_card.py

# new photo
python scripts/prep_photo.py my-photo.jpg     # transparent PNG works best; rembg used if installed
python scripts/make_ascii_svg.py              # INVERT=1 for the "ink" look

# heatmap by hand (the workflow does this daily)
python scripts/fetch_contributions.py && python scripts/render_heatmap_svg.py
```

Any script accepts `STATIC=1` to output a frozen frame for previews.

## GitHub gotchas

- Inline `style=` is stripped from READMEs; only `<br>` gives vertical space.
- `<h1>`/`<h2>` add a full-width rule; the layout uses `<h3>`.
- No JavaScript. All motion lives inside the SVGs (SMIL + CSS keyframes), which GitHub plays in `<img>`.
- Widths line up: heatmap `860` = portrait `370` + card `490`.
