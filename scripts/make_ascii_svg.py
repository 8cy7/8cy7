"""Turn a portrait photo into an animated ASCII-art SVG.

Usage: python scripts/make_ascii_svg.py path/to/photo.jpg [height]
Optional: pip install rembg  (removes the background for a cleaner result)
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageFilter, ImageOps

OUT = Path(__file__).resolve().parent.parent / "ascii-portrait.svg"

TARGET_HEIGHT = int(sys.argv[2]) if len(sys.argv) > 2 else 444  # match info-card.svg
CHAR_W, CHAR_H, FONT = 4.2, 6.9, 7.0
RAMP = ".'`^,:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
BG, BORDER, PANEL, MUTED = "#11100E", "#2E2A25", "#1A1815", "#8C8479"
LIGHT, MID, DEEP = (237, 230, 218), (240, 100, 58), (143, 53, 32)


def load(path: str) -> Image.Image:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img).convert("RGBA")
    if img.getchannel("A").getextrema()[0] == 255:  # no transparency yet
        try:
            from rembg import new_session, remove
            img = remove(img, session=new_session("u2net_human_seg"))
        except Exception:
            pass
    bbox = img.getchannel("A").getbbox()
    return img.crop(bbox) if bbox else img


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    img = load(sys.argv[1])
    pad, top = 22, 50
    rows = int((TARGET_HEIGHT - top - pad) / CHAR_H)
    cols = int(rows * img.width / img.height * (CHAR_H / CHAR_W))
    small = img.resize((cols, rows), Image.LANCZOS)
    alpha = small.getchannel("A")
    gray = ImageOps.equalize(small.convert("L"), mask=alpha.point(lambda a: 255 if a > 128 else 0))
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.2, percent=160, threshold=2))

    width = int(pad * 2 + cols * CHAR_W)
    height = int(top + rows * CHAR_H + pad)
    lines = []
    for y in range(rows):
        spans, last = [], None
        for x in range(cols):
            a = alpha.getpixel((x, y)) / 255
            v = gray.getpixel((x, y)) / 255
            if a < 0.35:
                ch, col = " ", None
            else:
                ch = RAMP[int(v * (len(RAMP) - 1))]
                col = mix(DEEP, MID, v * 2) if v < 0.5 else mix(MID, LIGHT, (v - 0.5) * 2)
            if spans and col == last:
                spans[-1][1] += ch
            else:
                spans.append([col, ch])
                last = col
        body = "".join(
            f'<tspan fill="{c or BG}">{escape(t)}</tspan>' for c, t in spans
        )
        delay = round(0.2 + y * 0.025, 3)
        lines.append(
            f'<text x="{pad}" y="{top + (y + 1) * CHAR_H:.1f}" class="l" style="animation-delay:{delay}s" xml:space="preserve">{body}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="ASCII portrait of Abdulaziz Alfahad">
<style>
  .l {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; font-size: {FONT}px; opacity: 0; animation: in .4s ease-out forwards; }}
  .t {{ fill: {MUTED}; font-family: ui-monospace, Menlo, monospace; font-size: 12px; }}
  @keyframes in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @media (prefers-reduced-motion: reduce) {{ .l {{ animation: none; opacity: 1; }} }}
</style>
<rect width="{width}" height="{height}" rx="14" fill="{BG}"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="13.5" fill="none" stroke="{BORDER}"/>
<rect x="1" y="1" width="{width - 2}" height="34" rx="13" fill="{PANEL}"/>
<rect x="1" y="22" width="{width - 2}" height="13" fill="{PANEL}"/>
<line x1="1" y1="35" x2="{width - 1}" y2="35" stroke="{BORDER}"/>
<circle cx="22" cy="18" r="5.5" fill="#E4572E"/><circle cx="40" cy="18" r="5.5" fill="#E8A33D"/><circle cx="58" cy="18" r="5.5" fill="#6BA368"/>
<text x="{width / 2}" y="22" class="t" text-anchor="middle">portrait.txt</text>
{"".join(lines)}
</svg>'''
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({cols}x{rows})")


if __name__ == "__main__":
    main()
