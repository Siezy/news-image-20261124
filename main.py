#!/usr/bin/env python3
"""news-image-20261124: sum up Tuesday 24 November 2026 in one image.

Draws a 1024x1024 newspaper-style infographic with pure-stdlib Python
(no network, no fonts on disk: a 5x7 bitmap font is defined below) and
writes it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

All seven stories were verified as having happened, or first been
reported, on Tuesday 24 November 2026 (Reuters, AP, Xinhua, gov.uk).
The Shenzhou-24 item is the CREW UNVEILING on 24 Nov; the launch is
25 Nov, so the image never says "launched".
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (30, 48, 88)
GOLD = (201, 162, 39)
RED = (180, 35, 24)
TEAL = (14, 124, 123)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
LINE = (180, 172, 150)
GREY = (90, 86, 76)
BLUE = (31, 93, 168)
ORANGE = (214, 106, 24)
GREEN = (46, 125, 50)
PURPLE = (106, 62, 158)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 columns, '#' = ink. Uppercase + digits + punctuation.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "(": ("   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"),
    ")": ("##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ###", "#  ##"),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "*": ("     ", "#   #", " # # ", "#####", " # # ", "#   #", "     "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg[0] for _ in range(0))  # placeholder
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def border(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)
        self.circle(cx, cy, r - t, PAPER)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        """Scanline fill of a simple polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.rect(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, c)

    def char(self, x, y, ch, scale, c):
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    self.rect(x + col * scale, y + row * scale, scale, scale, c)

    def text(self, x, y, s, scale, c):
        # The bitmap font holds uppercase glyphs only; normalise here so
        # mixed-case story text renders instead of falling back to "?".
        s = s.upper()
        for ch in s:
            self.char(x, y, ch, scale, c)
            x += 6 * scale

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def para(self, x, y, s, scale, c, max_w, leading=None):
        """Draw wrapped paragraph; returns y after the last line."""
        if leading is None:
            leading = 7 * scale + 6
        for line in wrap_text(s, scale, max_w):
            self.text(x, y, line, scale, c)
            y += leading
        return y


# ---------------------------------------------------------------- PNG encode
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- icons
# Small pictograms, drawn with the same primitives. Each takes the
# top-left corner of a square box and its size.

def icon_plane(cv, x, y, s, c):
    # simple jet seen from the side, nose to the right
    cv.poly([(x, y + s // 2), (x + s // 4, y + s // 3),
             (x + int(s * 0.85), y + s // 2), (x + s // 4, y + int(s * 0.66))], c)
    cv.poly([(x + int(s * 0.45), y + s // 2), (x + int(s * 0.62), y + int(s * 0.1)),
             (x + int(s * 0.72), y + int(s * 0.15)), (x + int(s * 0.6), y + s // 2)], c)
    cv.poly([(x + int(s * 0.5), y + s // 2), (x + int(s * 0.62), y + int(s * 0.9)),
             (x + int(s * 0.72), y + int(s * 0.85)), (x + int(s * 0.62), y + s // 2)], c)
    cv.poly([(x + int(s * 0.12), y + s // 2), (x, y + int(s * 0.12)),
             (x + int(s * 0.1), y + int(s * 0.18)), (x + int(s * 0.25), y + s // 2)], c)


def icon_burst(cv, x, y, s, c):
    # explosion starburst
    cx, cy = x + s // 2, y + s // 2
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = s // 2 if i % 2 == 0 else s // 5
        pts.append((int(cx + r * math.cos(ang)), int(cy + r * math.sin(ang))))
    cv.poly(pts, c)
    cv.circle(cx, cy, s // 8, WHITE)


def icon_building(cv, x, y, s, c):
    # damaged building: block + zigzag crack
    cv.rect(x + s // 5, y + s // 4, int(s * 0.6), int(s * 0.75), c)
    cv.rect(x + s // 5, y + s // 4, int(s * 0.6), s // 10, NAVY2)
    for r in range(3):
        for col in range(3):
            cv.rect(x + s // 5 + 6 + col * int(s * 0.18),
                    y + int(s * 0.42) + r * int(s * 0.18),
                    int(s * 0.09), int(s * 0.09), PAPER)
    cv.line(x + int(s * 0.45), y + s // 4, x + int(s * 0.6), y + int(s * 0.55),
            WHITE, 3)
    cv.line(x + int(s * 0.6), y + int(s * 0.55), x + int(s * 0.48), y + int(s * 0.8),
            WHITE, 3)


def icon_document(cv, x, y, s, c):
    # sanction order: sheet + seal
    cv.rect(x + s // 5, y + s // 8, int(s * 0.55), int(s * 0.75), WHITE)
    cv.border(x + s // 5, y + s // 8, int(s * 0.55), int(s * 0.75), c, 3)
    for r in range(3):
        cv.rect(x + int(s * 0.3), y + int(s * 0.25) + r * int(s * 0.16),
                int(s * 0.35), s // 18, c)
    cv.circle(x + int(s * 0.72), y + int(s * 0.72), s // 6, RED)
    cv.circle(x + int(s * 0.72), y + int(s * 0.72), s // 12, WHITE)


def icon_rocket(cv, x, y, s, c):
    # rocket climbing, flame below
    cv.poly([(x + s // 2, y), (x + int(s * 0.68), y + int(s * 0.35)),
             (x + int(s * 0.62), y + int(s * 0.62)), (x + int(s * 0.38), y + int(s * 0.62)),
             (x + int(s * 0.32), y + int(s * 0.35))], c)
    cv.circle(x + s // 2, y + int(s * 0.32), s // 10, WHITE)
    cv.poly([(x + int(s * 0.38), y + int(s * 0.6)), (x + int(s * 0.2), y + int(s * 0.85)),
             (x + int(s * 0.4), y + int(s * 0.75))], c)
    cv.poly([(x + int(s * 0.62), y + int(s * 0.6)), (x + int(s * 0.8), y + int(s * 0.85)),
             (x + int(s * 0.6), y + int(s * 0.75))], c)
    cv.poly([(x + int(s * 0.44), y + int(s * 0.62)), (x + s // 2, y + int(s * 0.95)),
             (x + int(s * 0.56), y + int(s * 0.62))], GOLD)


def icon_flame(cv, x, y, s, c):
    # flame teardrop
    cv.poly([(x + s // 2, y), (x + int(s * 0.8), y + int(s * 0.45)),
             (x + int(s * 0.85), y + int(s * 0.7)), (x + int(s * 0.65), y + s),
             (x + int(s * 0.35), y + s), (x + int(s * 0.15), y + int(s * 0.7)),
             (x + int(s * 0.2), y + int(s * 0.45))], c)
    cv.poly([(x + s // 2, y + int(s * 0.45)), (x + int(s * 0.62), y + int(s * 0.65)),
             (x + s // 2, y + int(s * 0.85)), (x + int(s * 0.38), y + int(s * 0.65))], GOLD)


def icon_school(cv, x, y, s, c):
    # schoolhouse: roof + block + door + windows
    cv.poly([(x, y + int(s * 0.35)), (x + s // 2, y + s // 8),
             (x + s, y + int(s * 0.35))], c)
    cv.rect(x + int(s * 0.12), y + int(s * 0.35), int(s * 0.76), int(s * 0.65), c)
    cv.rect(x + int(s * 0.42), y + int(s * 0.68), int(s * 0.16), int(s * 0.32), PAPER)
    cv.rect(x + int(s * 0.2), y + int(s * 0.45), int(s * 0.14), int(s * 0.14), PAPER)
    cv.rect(x + int(s * 0.66), y + int(s * 0.45), int(s * 0.14), int(s * 0.14), PAPER)


ICONS = {
    "plane": icon_plane,
    "burst": icon_burst,
    "building": icon_building,
    "document": icon_document,
    "rocket": icon_rocket,
    "flame": icon_flame,
    "school": icon_school,
}

# ---------------------------------------------------------------- stories
# (tag, tag colour, headline, fact, icon, accent colour)
LEAD = (
    "UKRAINE WAR - TALKS", RED,
    "LUKASHENKO OFFERS TO FLY WITH ZELENSKYY TO MOSCOW",
    "Belarus leader says he would guarantee Zelenskyy's safety at Kremlin "
    "talks. Zelenskyy answers: bring Putin to Kyiv instead.",
    "plane", NAVY2,
)

STORIES = [
    ("UKRAINE", RED,
     "RUSSIAN STRIKE HITS ZAPORIZHZHIA",
     "Overnight attack on homes kills 2 and wounds 40, including 4 children.",
     "burst", RED),
    ("GAZA", ORANGE,
     "ISRAELI STRIKES KILL 6 IN GAZA",
     "Strikes hit Khan Younis and the Netzarim corridor despite the October "
     "2025 ceasefire.",
     "building", ORANGE),
    ("YEMEN - UK", BLUE,
     "BRITAIN SANCTIONS THE HOUTHIS",
     "Asset freeze on Ansar Allah and 4 senior officials over abuses and "
     "Red Sea attacks.",
     "document", BLUE),
    ("SPACE - CHINA", PURPLE,
     "CHINA UNVEILS SHENZHOU-24 CREW",
     "Pakistani pilot Muhammad Zeeshan Ali is the first foreign astronaut to "
     "visit Tiangong. Launch set for Wednesday.",
     "rocket", PURPLE),
    ("VIETNAM", TEAL,
     "HANOI HOT POT BLAST KILLS 6",
     "Suspected gas leak levels a hot pot eatery in Dong Da. More than a "
     "dozen hurt.",
     "flame", TEAL),
    ("SERBIA", GREEN,
     "TEEN HELD AFTER SCHOOL SHOOTING",
     "A 17-year-old fired a rifle at a technical school in Kragujevac. "
     "Two staff hurt.",
     "school", GREEN),
]


# ---------------------------------------------------------------- layout
def draw_tag(cv, x, y, label, bg):
    w = text_width(label, 2) + 20
    cv.rect(x, y, w, 26, bg)
    cv.text(x + 10, y + 6, label, 2, WHITE)
    return w


def draw_lead(cv, x, y, w, h):
    tag, tagc, head, fact, icon, accent = LEAD
    cv.rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, LINE, 2)
    cv.rect(x, y, 8, h, accent)
    ix, iy, isize = x + 28, y + (h - 96) // 2, 96
    cv.circle(ix + isize // 2, iy + isize // 2, 62, accent)
    cv.circle(ix + isize // 2, iy + isize // 2, 56, PAPER)
    ICONS[icon](cv, ix + 10, iy + 10, isize - 20, accent)
    tx = x + 168
    draw_tag(cv, tx, y + 18, tag, tagc)
    hy = y + 56
    for line in wrap_text(head, 3, w - 196):
        cv.text(tx, hy, line, 3, INK)
        hy += 27
    cv.para(tx, hy + 6, fact, 2, GREY, w - 196, leading=20)


def draw_card(cv, x, y, w, h, story):
    tag, tagc, head, fact, icon, accent = story
    cv.rect(x, y, w, h, CARD)
    cv.border(x, y, w, h, LINE, 2)
    cv.rect(x, y, w, 6, accent)
    draw_tag(cv, x + 16, y + 18, tag, tagc)
    # icon top-right in a tinted disc
    isize = 56
    ix, iy = x + w - isize - 16, y + 14
    cv.circle(ix + isize // 2, iy + isize // 2, 34, accent)
    cv.circle(ix + isize // 2, iy + isize // 2, 30, PAPER)
    ICONS[icon](cv, ix + 8, iy + 8, isize - 16, accent)
    hy = y + 56
    for line in wrap_text(head, 3, w - 104):  # keep clear of the icon disc
        cv.text(x + 16, hy, line, 3, INK)
        hy += 27
    cv.para(x + 16, hy + 4, fact, 2, GREY, w - 32, leading=20)


def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 6, GOLD)
    cv.text_center(W // 2, 18, "THE WORLD IN ONE DAY", 2, GOLD)
    cv.text_center(W // 2, 46, "24 NOVEMBER 2026", 6, WHITE)
    cv.text_center(W // 2, 112, "TUESDAY - SEVEN STORIES FROM AROUND THE GLOBE", 2,
                   (200, 205, 220))

    # lead story
    draw_lead(cv, 28, 170, W - 56, 158)

    # grid: 2 cols x 3 rows
    gx, gy = 28, 344
    cw = (W - 56 - 16) // 2
    ch = 196
    for i, story in enumerate(STORIES):
        cx = gx + (i % 2) * (cw + 16)
        cy = gy + (i // 2) * (ch + 14)
        draw_card(cv, cx, cy, cw, ch, story)

    # footer
    fy = 962
    cv.rect(0, fy, W, H - fy, NAVY)
    cv.text_center(W // 2, fy + 12,
                   "ALL EVENTS HAPPENED OR WERE FIRST REPORTED ON 24 NOVEMBER 2026",
                   2, WHITE)
    cv.text_center(W // 2, fy + 38, "SOURCES: REUTERS - AP - XINHUA - GOV.UK",
                   2, GOLD)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    size = write_png(cv, os.path.join(out_dir, "entry.png"))
    print(f"wrote entry.png: {W}x{H}, {size} bytes")


if __name__ == "__main__":
    main()
