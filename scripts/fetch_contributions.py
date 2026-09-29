"""Fetch the public contribution calendar for a GitHub user and save it as JSON."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "8cy7")
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch(username: str) -> str:
    req = urllib.request.Request(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-art)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(html: str) -> list[dict]:
    counts = {}
    for cell_id, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"\s*(\d+|No)\s+contribution", text)
        counts[cell_id] = 0 if (not m or m.group(1) == "No") else int(m.group(1))

    days = []
    for td in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        date = re.search(r'data-date="([^"]+)"', td)
        level = re.search(r'data-level="(\d)"', td)
        cid = re.search(r'id="([^"]+)"', td)
        if not date:
            continue
        days.append({
            "date": date.group(1),
            "level": int(level.group(1)) if level else 0,
            "count": counts.get(cid.group(1), 0) if cid else 0,
        })
    days.sort(key=lambda d: d["date"])
    return days


def main() -> None:
    days = parse(fetch(USERNAME))
    if not days:
        sys.exit("No contribution data found; GitHub may have changed its markup.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"username": USERNAME, "days": days}, indent=1))
    total = sum(d["count"] for d in days)
    print(f"Saved {len(days)} days, {total} contributions -> {OUT}")


if __name__ == "__main__":
    main()
