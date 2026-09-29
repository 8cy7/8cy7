"""Render data/contributions.json as an animated terminal-style heatmap SVG."""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

BG = "#11100E"
PANEL = "#1A1815"
BORDER = "#2E2A25"
TEXT = "#EDE6DA"
MUTED = "#8C8479"
ACCENT = "#E4572E"
LEVELS = ["#26231F", "#5A2A1C", "#8F3520", "#C44627", "#F0643A"]

CELL, GAP = 12, 3
PAD_X, TOP = 28, 92


def main() -> None:
    payload = json.loads(DATA.read_text())
    days = payload["days"]
    user = payload.get("username", "8cy7")

    first = dt.date.fromisoformat(days[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday
    weeks = ((dt.date.fromisoformat(days[-1]["date"]) - start).days // 7) + 1

    grid_w = weeks * (CELL + GAP) - GAP
    width = PAD_X * 2 + 34 + grid_w
    height = TOP + 7 * (CELL + GAP) + 62

    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    streak = best = 0
    for d in days:
        streak = streak + 1 if d["count"] > 0 else 0
        best = max(best, streak)
    busiest = max(days, key=lambda d: d["count"])

    cells, months, last_month = [], [], None
    gx = PAD_X + 34
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        w = (date - start).days // 7
        r = (date.weekday() + 1) % 7
        x, y = gx + w * (CELL + GAP), TOP + r * (CELL + GAP)
        delay = round(w * 0.028 + r * 0.012, 3)
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{LEVELS[d["level"]]}" style="animation-delay:{delay}s">'
            f'<title>{d["count"]} on {date:%b %-d, %Y}</title></rect>'
        )
        if r == 0 and date.month != last_month and date.day <= 7:
            months.append(f'<text x="{x}" y="{TOP - 10}" class="m">{date:%b}</text>')
            last_month = date.month

    day_labels = "".join(
        f'<text x="{PAD_X + 24}" y="{TOP + i * (CELL + GAP) + 10}" class="m" text-anchor="end">{t}</text>'
        for i, t in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    legend_x = width - PAD_X - 5 * (CELL + GAP) - 70
    legend_y = height - 32
    legend = (
        f'<text x="{legend_x}" y="{legend_y + 10}" class="m">less</text>'
        + "".join(
            f'<rect x="{legend_x + 32 + i * (CELL + GAP)}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
            for i, c in enumerate(LEVELS)
        )
        + f'<text x="{legend_x + 38 + 5 * (CELL + GAP)}" y="{legend_y + 10}" class="m">more</text>'
    )
    stats = (
        f'<text x="{PAD_X}" y="{legend_y + 10}" class="s">'
        f'<tspan class="hl">{total:,}</tspan> contributions'
        f'<tspan dx="18" class="hl">{active}</tspan> active days'
        f'<tspan dx="18" class="hl">{best}</tspan> day best streak'
        f'<tspan dx="18" class="hl">{busiest["count"]}</tspan> on busiest day</text>'
    )
    scan_end = gx + grid_w

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="GitHub contributions for {user}: {total} in the last year">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }}
  .t {{ fill: {MUTED}; font-size: 12px; }}
  .p {{ fill: {TEXT}; font-size: 13px; }}
  .a {{ fill: {ACCENT}; font-size: 13px; }}
  .m {{ fill: {MUTED}; font-size: 10px; }}
  .s {{ fill: {MUTED}; font-size: 11.5px; }}
  .hl {{ fill: {TEXT}; font-weight: 700; }}
  .c {{ opacity: 0; transform-box: fill-box; transform-origin: center; animation: pop .45s cubic-bezier(.2,.9,.3,1.3) forwards; }}
  .scan {{ animation: scan 2.2s ease-in-out .2s forwards; opacity: 0; }}
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes pop {{ 0% {{ opacity: 0; transform: scale(.2); }} 100% {{ opacity: 1; transform: scale(1); }} }}
  @keyframes scan {{ 0% {{ opacity: .9; transform: translateX(0); }} 90% {{ opacity: .9; }} 100% {{ opacity: 0; transform: translateX({grid_w}px); }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ animation: none; opacity: 1; }} .scan, .cur {{ animation: none; opacity: 0; }} }}
</style>
<rect width="{width}" height="{height}" rx="14" fill="{BG}"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="13.5" fill="none" stroke="{BORDER}"/>
<rect x="1" y="1" width="{width - 2}" height="34" rx="13" fill="{PANEL}"/>
<rect x="1" y="22" width="{width - 2}" height="13" fill="{PANEL}"/>
<line x1="1" y1="35" x2="{width - 1}" y2="35" stroke="{BORDER}"/>
<circle cx="22" cy="18" r="5.5" fill="#E4572E"/><circle cx="40" cy="18" r="5.5" fill="#E8A33D"/><circle cx="58" cy="18" r="5.5" fill="#6BA368"/>
<text x="{width / 2}" y="22" class="t" text-anchor="middle">{user}@github: ~</text>
<text x="{PAD_X}" y="62" class="a">$</text><text x="{PAD_X + 16}" y="62" class="p">./contributions.sh --last-year</text>
<rect class="cur" x="{PAD_X + 16 + 31 * 7.8 + 4}" y="51" width="8" height="14" fill="{ACCENT}"/>
{"".join(months)}{day_labels}
{"".join(cells)}
<rect class="scan" x="{gx - 3}" y="{TOP - 4}" width="2" height="{7 * (CELL + GAP) + 5}" fill="{ACCENT}"/>
{stats}{legend}
</svg>'''
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({weeks} weeks, {total} contributions)")


if __name__ == "__main__":
    main()
