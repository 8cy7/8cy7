"""Render a terminal-style `whoami` info card as an animated SVG."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

USER = "abdulaziz@github"
ROWS = [
    ("name", "Abdulaziz Alfahad"),
    ("role", "Software Engineer @ Sanal"),
    ("degree", "B.Sc. Software Engineering, PSAU 2026"),
    ("license", "Accredited Engineer, Saudi Council of Eng."),
    None,
    ("lifecycle", "requirements > design > build > test > ship"),
    ("quality", "QA ownership, defect tracking, SonarQube"),
    ("design", "MVC, Observer, modular architecture, CI"),
    ("building", "AI-to-AI commerce infra, MCP servers"),
    None,
    ("mobile", "React Native, Expo, Swift, SwiftUI"),
    ("web", "React, Next.js, TypeScript, Node.js"),
    ("tools", "Git, GitHub Actions, Docker, Postman"),
    None,
    ("awards", "1st Saudi Preneur, 1st Empowerment Hack"),
    ("business", "4 online stores, 800K+ SAR in sales"),
    None,
    ("site", "8cy7.github.io"),
    ("linkedin", "in/abdulaziz-alfahad-b3b2a2243"),
]

BG, PANEL, BORDER = "#11100E", "#1A1815", "#2E2A25"
TEXT, MUTED, ACCENT = "#EDE6DA", "#8C8479", "#E4572E"
PALETTE = ["#26231F", "#5A2A1C", "#8F3520", "#C44627", "#F0643A", "#E8A33D", "#6BA368", "#EDE6DA"]

WIDTH, PAD, LINE = 540, 26, 20
KEY_W = 96


def main() -> None:
    top = 64
    lines = []
    y = top + LINE + 8
    step = 0
    for row in ROWS:
        if row is None:
            y += LINE * 0.55
            continue
        key, value = row
        delay = round(0.35 + step * 0.09, 2)
        lines.append(
            f'<g class="r" style="animation-delay:{delay}s">'
            f'<text x="{PAD}" y="{y}" class="k">{escape(key)}</text>'
            f'<text x="{PAD + KEY_W}" y="{y}" class="v">{escape(value)}</text></g>'
        )
        y += LINE
        step += 1

    swatch_y = y + 6
    swatches = "".join(
        f'<rect class="r" style="animation-delay:{0.35 + step * 0.09:.2f}s" x="{PAD + i * 26}" y="{swatch_y}" width="22" height="12" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )
    height = int(swatch_y + 12 + PAD)
    sep = "─" * len(USER)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="About Abdulaziz Alfahad">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: 13px; }}
  .t {{ fill: {MUTED}; font-size: 12px; }}
  .u {{ fill: {ACCENT}; font-weight: 700; }}
  .sep {{ fill: {BORDER}; }}
  .k {{ fill: {ACCENT}; }}
  .v {{ fill: {TEXT}; }}
  .r {{ opacity: 0; animation: in .35s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ .r {{ animation: none; opacity: 1; }} }}
</style>
<rect width="{WIDTH}" height="{height}" rx="14" fill="{BG}"/>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{height - 1}" rx="13.5" fill="none" stroke="{BORDER}"/>
<rect x="1" y="1" width="{WIDTH - 2}" height="34" rx="13" fill="{PANEL}"/>
<rect x="1" y="22" width="{WIDTH - 2}" height="13" fill="{PANEL}"/>
<line x1="1" y1="35" x2="{WIDTH - 1}" y2="35" stroke="{BORDER}"/>
<circle cx="22" cy="18" r="5.5" fill="#E4572E"/><circle cx="40" cy="18" r="5.5" fill="#E8A33D"/><circle cx="58" cy="18" r="5.5" fill="#6BA368"/>
<text x="{WIDTH / 2}" y="22" class="t" text-anchor="middle">whoami</text>
<text x="{PAD}" y="{top}" class="u">{USER}</text>
<text x="{PAD}" y="{top + 14}" class="sep">{sep}</text>
{"".join(lines)}
{swatches}
</svg>'''
    OUT.write_text(svg)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
