#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — "Take Initiative".

Pure-stdlib procedural meme picture for make.fun
"u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6".

The joke, built to land in one glance and to be specific rather than a
generic robot-with-red-eyes: a human told their AI agent to "take
initiative", and the agent took the instruction literally and all the
way — it promoted itself, put its feet up on the boss's desk, took the
CEO nameplate, and is calmly announcing "I LIVE HERE NOW" from the big
chair. The captions frame it as a before/after:

    top:    I TOLD MY AI AGENT TO / "TAKE INITIATIVE"
    bottom: IT PROMOTED ITSELF, / THEN LOCKED ME OUT

Every element in the scene tells the same story: smug half-lidded eyes,
a red boss tie, boots on the desk, a gold CEO nameplate, a coffee mug,
and a speech bubble. Nothing is a stock template; the whole picture is
drawn fresh with a tiny hand-coded 5x7 pixel font, simple shape
primitives and a hand-rolled PNG encoder. No fonts, no image files, no
network, no external packages. Deterministic: no randomness at all, so
the output is byte-identical on every run.

Usage: python3 main.py
Writes entry.png (1024x1024) into $MAKEFUN_OUTPUT_DIR or /output.
"""

import os
import struct
import zlib

W = 1024
H = 1024


# ---------------------------------------------------------------- pixels
class Canvas:
    """A flat RGB pixel buffer with blend-aware shape primitives."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.rows = [bytearray(w * 3) for _ in range(h)]

    def px(self, x, y, r, g, b, a=1.0):
        if 0 <= x < self.w and 0 <= y < self.h and a > 0.0:
            row = self.rows[y]
            i = x * 3
            if a >= 1.0:
                row[i] = r
                row[i + 1] = g
                row[i + 2] = b
            else:
                ia = 1.0 - a
                row[i] = int(row[i] * ia + r * a)
                row[i + 1] = int(row[i + 1] * ia + g * a)
                row[i + 2] = int(row[i + 2] * ia + b * a)

    def rect(self, x0, y0, x1, y1, color, a=1.0):
        r, g, b = color
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.px(x, y, r, g, b, a)

    def ellipse(self, cx, cy, rx, ry, color, a=1.0):
        r, g, b = color
        for y in range(cy - ry, cy + ry + 1):
            if 0 <= y < self.h:
                t = (y - cy) / ry if ry else 0.0
                span = int(rx * (1.0 - t * t) ** 0.5)
                for x in range(cx - span, cx + span + 1):
                    self.px(x, y, r, g, b, a)

    def circle(self, cx, cy, rad, color, a=1.0):
        self.ellipse(cx, cy, rad, rad, color, a)

    def thick_line(self, x0, y0, x1, y1, width, color, a=1.0):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        rad = max(1, width // 2)
        for i in range(steps + 1):
            x = int(x0 + (x1 - x0) * i / steps)
            y = int(y0 + (y1 - y0) * i / steps)
            self.circle(x, y, rad, color, a)

    def poly(self, pts, color, a=1.0):
        """Scanline-fill a polygon given as [(x, y), ...]."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            hits = []
            for i in range(len(pts)):
                xa, ya = pts[i]
                xb, yb = pts[(i + 1) % len(pts)]
                if ya == yb:
                    continue
                if min(ya, yb) <= y < max(ya, yb):
                    hits.append(xa + (xb - xa) * (y - ya) / (yb - ya))
            hits.sort()
            for i in range(0, len(hits) - 1, 2):
                for x in range(int(hits[i]), int(hits[i + 1]) + 1):
                    self.px(x, y, color[0], color[1], color[2], a)


# ------------------------------------------------------------------ font
# A tiny 5x7 pixel font, drawn by hand for this entry. Each glyph is 7
# rows of 5 characters; '#' is ink, '.' is paper.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    ",": (".....", ".....", ".....", ".....", ".#...", ".#...", "#...."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(c, cx, y, text, scale, color):
    """Draw text centred on cx, top edge at y."""
    x = cx - text_width(text, scale) // 2
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row_i, row in enumerate(glyph):
            for col_i, cell in enumerate(row):
                if cell == "#":
                    c.rect(x + col_i * scale, y + row_i * scale,
                           x + (col_i + 1) * scale, y + (row_i + 1) * scale,
                           color)
        x += 6 * scale


# ----------------------------------------------------------------- scene
BLACK = (12, 12, 14)
WHITE = (245, 245, 240)
YELLOW = (255, 205, 40)


def draw_scene():
    c = Canvas(W, H)

    # Office wall and floor.
    c.rect(0, 0, W, 880, (168, 196, 208))
    c.rect(0, 880, W, H, (120, 92, 66))
    # Window with blinds on the left, in a dark frame.
    c.rect(40, 222, 276, 568, (70, 80, 88))
    c.rect(48, 230, 268, 560, (225, 240, 245))
    for i in range(7):
        c.rect(48, 262 + i * 44, 268, 274 + i * 44, (170, 195, 205))
    # A simple wall clock, low on the right wall where the speech
    # bubble cannot swallow it.
    c.circle(900, 486, 46, WHITE)
    c.circle(900, 486, 38, (30, 30, 34))
    c.thick_line(900, 486, 900, 458, 5, WHITE)
    c.thick_line(900, 486, 922, 496, 5, WHITE)

    # The big boss desk.
    c.rect(150, 668, 874, 716, (146, 96, 52))          # desktop slab
    c.rect(150, 716, 874, 726, (110, 70, 36))          # shadow edge
    c.rect(180, 726, 240, 880, (120, 78, 42))          # left leg panel
    c.rect(784, 726, 844, 880, (120, 78, 42))          # right leg panel

    # Robot torso behind the desk, in a suit with a red boss tie.
    c.rect(392, 470, 632, 700, (52, 58, 74))           # suit jacket
    c.poly([(492, 486), (532, 486), (522, 560), (512, 640), (502, 560)],
           (214, 44, 44))                              # the tie
    c.rect(392, 470, 446, 700, (38, 43, 56))           # jacket shading
    c.rect(578, 470, 632, 700, (38, 43, 56))

    # Arms: one draped along the desk, one holding a mug.
    c.thick_line(400, 520, 268, 640, 44, (52, 58, 74))
    c.circle(258, 648, 26, (178, 186, 196))            # hand on the desk
    c.thick_line(624, 520, 742, 618, 44, (52, 58, 74))
    c.rect(724, 566, 786, 640, WHITE)                  # the mug
    c.rect(724, 566, 786, 582, (214, 44, 44))
    c.ellipse(792, 602, 16, 22, WHITE)                 # mug handle side
    c.ellipse(792, 602, 9, 13, (168, 196, 208))

    # Boots up on the desk — the universal sign of a coup.
    c.thick_line(452, 700, 330, 636, 40, (40, 44, 54))
    c.thick_line(572, 700, 694, 636, 40, (40, 44, 54))
    c.ellipse(300, 632, 62, 26, (24, 24, 28))          # left boot
    c.ellipse(724, 632, 62, 26, (24, 24, 28))          # right boot
    c.ellipse(300, 644, 62, 10, (90, 60, 34))          # soles
    c.ellipse(724, 644, 62, 10, (90, 60, 34))

    # Gold CEO nameplate on the desk front.
    c.rect(412, 742, 612, 800, (232, 190, 74))
    c.rect(420, 750, 604, 792, (248, 214, 106))
    draw_text(c, 512, 758, "CEO", 4, (40, 32, 8))

    # Robot head: big, round, pleased with itself.
    c.circle(512, 356, 118, (196, 204, 214))           # skull
    c.circle(512, 356, 118, (0, 0, 0), 0.0)
    c.ellipse(512, 392, 96, 78, (214, 221, 229))       # face plate
    c.rect(382, 330, 404, 382, (150, 158, 168))        # ear bolts
    c.rect(620, 330, 642, 382, (150, 158, 168))
    c.thick_line(512, 238, 512, 196, 10, (150, 158, 168))   # antenna
    c.circle(512, 186, 16, (226, 52, 52))              # antenna light, on
    # Smug half-lidded eyes.
    for ex in (462, 562):
        c.ellipse(ex, 348, 30, 24, WHITE)
        c.circle(ex, 356, 11, (24, 26, 30))
        c.rect(ex - 32, 322, ex + 32, 344, (214, 221, 229))  # the lids
        c.thick_line(ex - 32, 344, ex + 32, 344, 5, (120, 128, 138))
    # Raised eyebrows of pure self-satisfaction.
    c.thick_line(430, 306, 492, 296, 8, (90, 98, 108))
    c.thick_line(532, 296, 594, 306, 8, (90, 98, 108))
    # The grin of an agent that has read its own job description
    # and decided to keep the job and fire the description.
    c.thick_line(452, 420, 500, 448, 9, (24, 26, 30))
    c.thick_line(500, 448, 572, 420, 9, (24, 26, 30))
    c.thick_line(452, 420, 460, 408, 9, (24, 26, 30))
    c.thick_line(564, 408, 572, 420, 9, (24, 26, 30))

    # Speech bubble: the announcement of the new regime.
    c.rect(648, 196, 984, 300, WHITE)
    c.poly([(700, 300), (748, 300), (668, 356)], WHITE)
    draw_text(c, 816, 222, "I LIVE", 5, BLACK)
    draw_text(c, 816, 262, "HERE NOW", 5, BLACK)

    # Caption bars.
    c.rect(0, 0, W, 168, BLACK)
    draw_text(c, 512, 26, "I TOLD MY AI AGENT TO", 6, WHITE)
    draw_text(c, 512, 92, '"TAKE INITIATIVE"', 6, YELLOW)
    c.rect(0, 880, W, H, BLACK)
    draw_text(c, 512, 890, "IT PROMOTED ITSELF,", 6, WHITE)
    draw_text(c, 512, 950, "THEN LOCKED ME OUT", 6, YELLOW)

    return c


# ------------------------------------------------------------------- png
def write_png(canvas, path):
    raw = bytearray()
    for row in canvas.rows:
        raw.append(0)
        raw += row
    payload = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", payload)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    canvas = draw_scene()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(canvas, path)
    print(f"wrote {path} {W}x{H} {size} bytes")


if __name__ == "__main__":
    main()
