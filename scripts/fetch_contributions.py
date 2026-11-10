"""Scrape the public contribution calendar (no token needed) into data/contributions.json.

    python scripts/fetch_contributions.py            # real data for USERNAME
    python scripts/fetch_contributions.py --sample   # fake data, for offline previews only

GitHub serves the same HTML fragment the profile page uses at
https://github.com/users/<username>/contributions.
"""
import json
import random
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
USERNAME = "posiauday"


def fetch_days() -> list[dict]:
    import requests
    from bs4 import BeautifulSoup

    url = f"https://github.com/users/{USERNAME}/contributions"
    r = requests.get(url, headers={"User-Agent": "profile-heatmap/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        text = tips.get(td.get("id"), "")
        m = re.match(r"([\d,]+) contributions?", text)
        count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": td["data-date"], "count": count, "level": int(td.get("data-level", 0))})
    if not days:
        raise SystemExit("no contribution cells found; GitHub may have changed its markup")
    return sorted(days, key=lambda d: d["date"])


def sample_days() -> list[dict]:
    rng = random.Random(42)
    end = date.today()
    start = end - timedelta(days=364 + (end.weekday() + 1) % 7)
    days, d = [], start
    while d <= end:
        busy = 0.75 if d.weekday() < 5 else 0.35
        count = 0 if rng.random() > busy else int(rng.expovariate(1 / 6)) + 1
        days.append({"date": d.isoformat(), "count": count})
        d += timedelta(days=1)
    nz = sorted(x["count"] for x in days if x["count"])
    q = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)]
    for x in days:
        c = x["count"]
        x["level"] = 0 if c == 0 else 1 + sum(c > t for t in q)
    return days


def stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["count"]:
            current += 1
        elif i == 0:  # today not counted yet is fine
            continue
        else:
            break
    best = max(days, key=lambda d: d["count"])
    months = defaultdict(int)
    for d in days:
        months[d["date"][:7]] += d["count"]
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "active_days": sum(1 for d in days if d["count"]),
        "monthly": dict(months),
    }


def main() -> None:
    sample = "--sample" in sys.argv
    days = sample_days() if sample else fetch_days()
    data = {
        "username": USERNAME,
        "sample": sample,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "stats": stats(days),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    s = data["stats"]
    print(f"wrote {OUT.relative_to(ROOT)}: {len(days)} days, {s['total']} contributions"
          f"{' (SAMPLE DATA)' if sample else ''}")


if __name__ == "__main__":
    main()
