"""Generate the visuals for the Cairn hub in the Cairn brand palette.

Shared with Cairn Memory (same palette, pebbles, hero and terminal layout); only the
words, the terminal transcript and the diagram differ. Run: python make_assets.py assets

Every animation plays once and ends on a readable frame; motion is dropped for
readers who ask for reduced motion, and the resting state is the visible one.
Light cards to match the logo, which is drawn on white; the terminal stays dark.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import sys

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

# brand, sampled from the Cairn logo
INK = "#111827"        # wordmark
BLUE = "#0A6CFF"
SKY = "#6CCBFF"
DEEP = "#16255C"
DIM = "#5B6B85"
CARD = "#FFFFFF"
CARD2 = "#F6F9FF"
EDGE = "#DCE5F5"
GREEN = "#16A34A"
AMBER = "#D97706"
# terminal
T_BG, T_BAR, T_TEXT, T_DIM = "#0F172A", "#1E293B", "#E2E8F0", "#94A3B8"
T_BLUE, T_GREEN, T_RED, T_AMBER = "#60A5FA", "#4ADE80", "#F87171", "#FBBF24"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

# The three pebbles of the mark, in the logo's own 1254px coordinate space.
PEBBLES = [
    ("bottom", "M252,915 C255,840 360,770 520,735 C660,705 820,700 920,745 "
               "C1000,780 1015,900 960,985 C900,1045 700,1045 560,1042 C400,1040 250,1010 252,915 Z",
     [("0", "#12204F"), ("0.55", "#1B3A8C"), ("1", "#2366E0")], (0, 1, 1, 0)),
    ("middle", "M315,660 C310,560 390,508 520,506 C650,504 820,520 880,570 "
               "C930,615 880,690 760,720 C650,748 520,760 430,748 C360,740 318,705 315,660 Z",
     [("0", "#1E90FF"), ("1", "#0050E6")], (0, 0, 1, 1)),
    ("top", "M440,430 C430,360 560,270 700,248 C790,235 820,320 790,390 "
            "C760,460 690,500 590,500 C500,500 445,470 440,430 Z",
     [("0", "#7DD6FF"), ("1", "#0A74FF")], (0.6, 0, 0.4, 1)),
]


def hero() -> str:
    defs, stones = [], []
    for i, (name, d, stops, (x1, y1, x2, y2)) in enumerate(PEBBLES):
        s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
        defs.append(f'<linearGradient id="g{name}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')
        stones.append(f'<g class="drop" style="animation-delay:{0.15 + i * 0.35:.2f}s">'
                      f'<path d="{d}" fill="url(#g{name})"/></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 400" width="1280" height="400" role="img" aria-label="Three stones stack into a cairn: a claim with an enforcer stays true; a claim with only an author rots">
<style>
.drop {{ animation: drop .7s cubic-bezier(.2,.9,.3,1.25) both; }}
@keyframes drop {{ from {{ transform: translateY(-900px); opacity: 0; }} 60% {{ opacity: 1; }} to {{ transform: none; opacity: 1; }} }}
.glow {{ animation: glow 3.4s ease-in-out 1.6s infinite; }}
@keyframes glow {{ 0%,100% {{ opacity: 0; }} 50% {{ opacity: .45; }} }}
.fade {{ animation: fade .9s ease-out both; }}
@keyframes fade {{ from {{ opacity: 0; transform: translateX(-14px); }} to {{ opacity: 1; transform: none; }} }}
{REDUCED}
</style>
<defs>{''.join(defs)}<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter></defs>
<rect x="1" y="1" width="1278" height="398" rx="28" fill="{CARD}" stroke="{EDGE}" stroke-width="2"/>
<g transform="translate(40 -40) scale(0.4)">
  <ellipse class="glow" cx="620" cy="380" rx="220" ry="120" fill="{SKY}" opacity="0" filter="url(#blur)"/>
  {''.join(stones)}
</g>
<g class="fade" style="animation-delay:1.2s">
  <text x="480" y="170" font-family="{SANS}" font-size="46" font-weight="700" fill="{INK}">A claim with an enforcer</text>
  <text x="480" y="226" font-family="{SANS}" font-size="46" font-weight="700" fill="{BLUE}">stays true.</text>
</g>
<g class="fade" style="animation-delay:1.6s">
  <text x="482" y="282" font-family="{SANS}" font-size="22" fill="{DIM}">A claim with only an author rots. Three Claude Code plugins that check</text>
  <text x="482" y="314" font-family="{SANS}" font-size="22" fill="{DIM}">what agents remember, what AI products show, and what agents say they did.</text>
</g>
</svg>
"""




# Each principle, and the check in each plugin that enforces it (None: not that plugin's job).
MATRIX = [
    ("1", "Enforce, or don't assert", "walk test: every pointer resolves", "published numbers must re-run", "proof words need proof"),
    ("2", "A test that never imports its subject can't fail for the right reason", None, "evals that can't fail", "tests that miss the change"),
    ("3", "Readers need writers", "a memory no index reads", "a score input nothing writes", "wired, and nothing calls it"),
    ("4", "Swallow, don't silence", None, "failures that become a believable 0", None),
    ("5", "One derivation, two callers", "generated views check invariants", None, None),
    ("6", "Check the instrument, not only the code", "--self-test: 22 checks", "--self-test: 11 checks", "--self-test: 19 checks"),
    ("7", "Name what would dissolve the explanation", "memory is a claim about the past", "name what disproves the verdict", "name what disproves the verdict"),
    ("8", "Don't cry wolf", "FAIL only for breaches", "HIGH / MEDIUM / INFO levels", "guards built from honest commits"),
    ("9", "Check what a metric is defined over", None, "can it see the main failure?", None),
    ("10", "Name the narrowest verifying command", "status memories carry a re-check", "the query that settles it", "the command that settles it"),
]


def matrix() -> str:
    cols = [("Cairn Memory", BLUE), ("Cairn Signals", SKY), ("Cairn Verify", AMBER)]
    x0, pw, cw, top, rh = 40, 440, 262, 150, 62
    out = []
    for i, (name, col) in enumerate(cols):
        x = x0 + pw + i * cw
        out.append(f'<rect x="{x}" y="{top - 58}" width="{cw - 16}" height="5" rx="2.5" fill="{col}"/>'
                   f'<text x="{x}" y="{top - 26}" font-family="{SANS}" font-size="20" font-weight="700" fill="{INK}">{name}</text>')
    for r, (num, principle, *cells) in enumerate(MATRIX):
        y = top + r * rh
        if r % 2 == 0:
            out.append(f'<rect x="{x0 - 12}" y="{y - 4}" width="{pw + 3 * cw}" height="{rh - 6}" rx="12" fill="{CARD}"/>')
        words, line, lines = principle.split(), "", []
        for w in words:
            if len(line) + len(w) + 1 > 40:
                lines.append(line); line = w
            else:
                line = (line + " " + w).strip()
        lines.append(line)
        out.append(f'<text x="{x0}" y="{y + 24}" font-family="{MONO}" font-size="15" font-weight="700" fill="{BLUE}">{num}</text>')
        for k, ln in enumerate(lines[:2]):
            out.append(f'<text x="{x0 + 34}" y="{y + 24 + k * 20}" font-family="{SANS}" font-size="16" font-weight="600" fill="{INK}">{escape(ln)}</text>')
        for i, cell in enumerate(cells):
            x = x0 + pw + i * cw
            if cell:
                out.append(f'<circle cx="{x + 8}" cy="{y + 19}" r="6" fill="{cols[i][1]}"/>'
                           f'<text x="{x + 22}" y="{y + 24}" font-family="{SANS}" font-size="14" fill="{DIM}">{escape(cell)}</text>')
            else:
                out.append(f'<text x="{x + 2}" y="{y + 24}" font-family="{SANS}" font-size="14" fill="{EDGE}">—</text>')
    h = top + len(MATRIX) * rh + 30
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 {h}" width="1280" height="{h}" role="img" aria-label="Ten principles, and the check in each Cairn plugin that enforces it">
<rect x="1" y="1" width="1278" height="{h - 2}" rx="28" fill="{CARD2}" stroke="{EDGE}" stroke-width="2"/>
<text x="40" y="52" font-family="{SANS}" font-size="15" font-weight="700" letter-spacing="2" fill="{BLUE}">ONE SET OF PRINCIPLES, THREE PLUGINS THAT ENFORCE THEM</text>
{''.join(out)}
</svg>
"""


for name, fn in [("hero.svg", hero), ("principles.svg", matrix)]:
    (OUT / name).write_text(fn(), encoding="utf-8")
    print(name, len((OUT / name).read_bytes()), "bytes")
