"""Generate the profile README assets (SVG, dark + light).

- banner-{dark,light}.svg   : "IACOPO PRAI" drawn in contribution-graph squares, lighting up left to right, then a looping wave
- toolbox-{dark,light}.svg  : tool chips styled like GitHub labels

Run: python3 tools/build_assets.py  (needs Pillow)
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

THEMES = {
    "dark": {
        "bg": "#0d1117", "empty": "#161b22", "lv": ["#0e4429", "#006d32", "#26a641", "#39d353"],
        "text": "#e6edf3", "muted": "#7d8590", "border": "#30363d", "chip": "#161b22",
    },
    "light": {
        "bg": "#ffffff", "empty": "#ebedf0", "lv": ["#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "text": "#1f2328", "muted": "#59636e", "border": "#d1d9e0", "chip": "#f6f8fa",
    },
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

# 3x5 pixel font
GLYPHS = {
    "I": ["111", "010", "010", "010", "111"],
    "A": ["010", "101", "111", "101", "101"],
    "C": ["111", "100", "100", "100", "111"],
    "O": ["111", "101", "101", "101", "111"],
    "P": ["111", "101", "111", "100", "100"],
    "R": ["110", "101", "110", "101", "101"],
    " ": ["0", "0", "0", "0", "0"],
}


def word_columns(word):
    cols = []
    for ch in word:
        g = GLYPHS[ch]
        for x in range(len(g[0])):
            cols.append([row[x] for row in g])
        cols.append(["0"] * 5)
    return cols[:-1]


def banner(theme):
    t = THEMES[theme]
    W_CELLS, H_CELLS = 53, 7
    cell, gap = 18, 4
    pad_x, pad_y = 56, 40
    grid_w = W_CELLS * (cell + gap) - gap
    width = grid_w + 2 * pad_x
    height = 300
    cols = word_columns("IACOPO PRAI")
    off = (W_CELLS - len(cols)) // 2
    # deterministic shade per lit cell (so the word looks like real activity)
    shades = [2, 3, 3, 2, 1, 3, 2, 3, 1, 2]
    rects, n = [], 0
    for x in range(W_CELLS):
        for y in range(H_CELLS):
            cx, cy = x - off, y - 1
            px = pad_x + x * (cell + gap)
            py = pad_y + y * (cell + gap)
            lit = 0 <= cx < len(cols) and 0 <= cy < 5 and cols[cx][cy] == "1"
            if lit:
                lvl = shades[(x * 7 + y * 3) % len(shades)]
                delay = 0.25 + cx * 0.045 + y * 0.02
                # after the intro, a diagonal wave keeps breathing through the letters (on the wrapping <g>,
                # so it multiplies with the pop-in opacity instead of overriding it)
                wave = 2.8 + cx * 0.07 + y * 0.05
                rects.append(
                    f'<g class="w" style="animation-delay:{wave:.2f}s"><rect class="on" x="{px}" y="{py}" '
                    f'width="{cell}" height="{cell}" rx="4" fill="{t["lv"][lvl]}" style="animation-delay:{delay:.2f}s"/></g>'
                )
                n += 1
            rects.append(
                f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="4" fill="{t["empty"]}"/>'
            )
    # empty cells first, lit cells on top
    empties = [r for r in rects if 'class="on"' not in r]
    lits = [r for r in rects if 'class="on"' in r]
    ty = pad_y + H_CELLS * (cell + gap) + 52
    legend_x = width - pad_x
    leg = []
    lx = legend_x - 5 * 16 - 34
    leg.append(f'<text x="{lx - 8}" y="{ty - 4}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{t["muted"]}">less</text>')
    for i, c in enumerate([t["empty"]] + t["lv"]):
        leg.append(f'<rect x="{lx + i * 16}" y="{ty - 15}" width="12" height="12" rx="3" fill="{c}"/>')
    leg.append(f'<text x="{lx + 5 * 16 + 4}" y="{ty - 4}" font-family="{MONO}" font-size="13" fill="{t["muted"]}">more</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="IACOPO PRAI — business student who builds with AI">
<style>
.on{{opacity:0;animation:pop .45s cubic-bezier(.2,.8,.2,1.2) forwards}}
@keyframes pop{{0%{{opacity:0;transform:scale(.4)}}100%{{opacity:1;transform:scale(1)}}}}
.on{{transform-box:fill-box;transform-origin:center}}
.w{{animation:wave 3.2s ease-in-out infinite}}
@keyframes wave{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.tag{{opacity:0;animation:fade .8s ease forwards;animation-delay:2.4s}}
@keyframes fade{{to{{opacity:1}}}}
@media (prefers-reduced-motion: reduce){{.on,.tag,.w{{animation:none;opacity:1}}}}
</style>
<rect width="100%" height="100%" rx="12" fill="{t["bg"]}"/>
{"".join(empties)}
{"".join(lits)}
<g class="tag">
<text x="{pad_x}" y="{ty}" font-family="{FONT}" font-size="28" font-weight="600" fill="{t["text"]}">Business student who builds with AI <tspan fill="{t["muted"]}" font-weight="400">· H-FARM College – Ca' Foscari</tspan></text>
{"".join(leg)}
</g>
</svg>'''
    (OUT / f"banner-{theme}.svg").write_text(svg)
    return n


def toolbox(theme):
    t = THEMES[theme]
    tools = ["Claude Code", "Vite", "GSAP", "Lenis", "Git", "Python"]
    # approximate text width for a 15px system font
    from PIL import ImageFont
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    widths = [int(f.getlength(s)) + 40 for s in tools]
    gap = 10
    total = sum(widths) + gap * (len(tools) - 1)
    h = 34
    x = 0
    parts = []
    for s, w in zip(tools, widths):
        dot = t["lv"][3]
        parts.append(
            f'<g transform="translate({x},0)"><rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="17" fill="{t["chip"]}" stroke="{t["border"]}"/>'
            f'<circle cx="16" cy="17" r="4.5" fill="{dot}"/>'
            f'<text x="28" y="22" font-family="{FONT}" font-size="15" font-weight="500" fill="{t["text"]}">{s}</text></g>'
        )
        x += w + gap
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="{h}" viewBox="0 0 {total} {h}" role="img" aria-label="Toolbox: {", ".join(tools)}">
{"".join(parts)}
</svg>'''
    (OUT / f"toolbox-{theme}.svg").write_text(svg)


if __name__ == "__main__":
    for th in THEMES:
        banner(th)
        toolbox(th)
    print("ok")
