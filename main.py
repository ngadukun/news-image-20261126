#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Thursday 26 November 2026.

Renders a newspaper-style front page summing up the day's world news
to entry.png (724 x 1024, under the 1024 x 1024 / 1 MiB gate).

The grader runs on a stdlib-only Python image, so Pillow is vendored as
a wheel in vendor/ and unpacked by the bootstrap below before use.
No network is used at run time; the render is fully deterministic.
"""

import os
import sys
import tempfile
import zipfile


def _ensure_pil():
    """Make `import PIL` work on a stdlib-only interpreter.

    If Pillow is already importable, do nothing. Otherwise unpack the
    vendored wheel into a writable temp dir and prepend it to sys.path.
    """
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass
    here = os.path.dirname(os.path.abspath(__file__))
    vendor = os.path.join(here, "vendor")
    wheel = None
    try:
        for name in sorted(os.listdir(vendor)):
            if name.startswith("pillow-") and name.endswith(".whl"):
                wheel = os.path.join(vendor, name)
                break
    except OSError:
        wheel = None
    if wheel is None:
        raise ImportError("no vendored Pillow wheel found in vendor/")
    candidates = [tempfile.gettempdir(),
                  os.environ.get("MAKEFUN_OUTPUT_DIR", ""),
                  os.getcwd(), here]
    for base in candidates:
        if not base:
            continue
        try:
            dest = tempfile.mkdtemp(prefix="pillow-", dir=base)
            with zipfile.ZipFile(wheel) as zf:
                zf.extractall(dest)
            sys.path.insert(0, dest)
            import PIL  # noqa: F401
            return
        except Exception:
            continue
    raise ImportError("could not unpack vendored Pillow")


_ensure_pil()

from PIL import Image, ImageDraw, ImageFont  # noqa: E402


# ---------------------------------------------------------------- page setup

W, H = 724, 1024
MARGIN = 34
CW = W - 2 * MARGIN  # 656

PAPER = (248, 244, 233)
INK = (20, 20, 20)
RED = (164, 31, 31)
GREY = (90, 86, 76)
LIGHT = (232, 226, 210)
MIDGREY = (120, 116, 104)
STEEL = (70, 84, 102)
GOLD = (176, 132, 40)


def font(size):
    """Pillow's built-in scalable default font (no system font files)."""
    return ImageFont.load_default(size=size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def bold(draw, xy, text, fnt, fill=INK):
    """Fake-bold: draw the text twice, 1 px apart."""
    x, y = xy
    draw.text((x, y), text, font=fnt, fill=fill)
    draw.text((x + 1, y), text, font=fnt, fill=fill)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines = []
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = (line + " " + word).strip()
            if text_w(draw, trial, fnt) <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


def para(draw, x, y, text, fnt, width, leading, fill=INK):
    """Draw a wrapped paragraph; returns the y below it."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x, y, width, weight=1, fill=INK):
    draw.rectangle([x, y, x + width, y + weight - 1], fill=fill)
    return y + weight


def kicker(draw, x, y, label, fnt):
    draw.text((x, y), label, font=fnt, fill=RED)
    return y + 20


# ------------------------------------------------------------------- graphics

def draw_tower(draw, x, y, w, h):
    """Stylised PIF Tower silhouette with a red strike mark."""
    draw.rectangle([x, y, x + w, y + h], fill=LIGHT, outline=MIDGREY)
    # stepped tower
    tw = w * 0.42
    tx = x + (w - tw) / 2
    draw.rectangle([tx, y + h * 0.12, tx + tw, y + h], fill=STEEL)
    draw.rectangle([tx + tw * 0.18, y + h * 0.02, tx + tw * 0.82,
                    y + h * 0.12], fill=STEEL)
    # windows
    for i in range(5):
        wy = y + h * (0.22 + i * 0.15)
        draw.rectangle([tx + 4, wy, tx + tw - 4, wy + 3], fill=PAPER)
    # strike burst near the top
    cx, cy = tx + tw * 0.78, y + h * 0.30
    for dx, dy in [(0, -9), (7, -6), (9, 0), (7, 6), (0, 9),
                   (-7, 6), (-9, 0), (-7, -6)]:
        draw.line([cx, cy, cx + dx, cy + dy], fill=RED, width=2)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    # ground line + caption
    draw.line([x, y + h, x + w, y + h], fill=INK, width=1)


def draw_chip(draw, x, y, w, h):
    """Stylised AI chip with pins."""
    draw.rectangle([x, y, x + w, y + h], fill=LIGHT, outline=MIDGREY)
    cw, ch = w * 0.52, h * 0.62
    cx, cy = x + (w - cw) / 2, y + (h - ch) / 2
    draw.rectangle([cx, cy, cx + cw, cy + ch], fill=INK)
    draw.rectangle([cx + cw * 0.25, cy + ch * 0.25,
                    cx + cw * 0.75, cy + ch * 0.75], fill=GOLD)
    draw.text((cx + cw * 0.38, cy + ch * 0.40), "AI",
              font=font(13), fill=INK)
    for i in range(4):
        px = cx + 4 + i * (cw - 8) / 3
        draw.line([px, cy - 6, px, cy], fill=INK, width=2)
        draw.line([px, cy + ch, px, cy + ch + 6], fill=INK, width=2)
        py = cy + 4 + i * (ch - 8) / 3
        draw.line([cx - 6, py, cx, py], fill=INK, width=2)
        draw.line([cx + cw, py, cx + cw + 6, py], fill=INK, width=2)


def draw_mercury(draw, x, y, d):
    """Mercury: grey disc with craters, on a dark sky box."""
    draw.rectangle([x, y, x + d, y + d], fill=(24, 26, 32))
    cx, cy, r = x + d / 2, y + d / 2, d * 0.36
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 170, 158))
    for ox, oy, cr in [(-0.45, -0.3, 0.16), (0.35, -0.45, 0.12),
                       (0.5, 0.25, 0.18), (-0.2, 0.45, 0.13),
                       (0.05, -0.05, 0.10)]:
        px, py = cx + ox * r, cy + oy * r
        rr = cr * r
        draw.ellipse([px - rr, py - rr, px + rr, py + rr],
                     fill=(140, 132, 120))
    # stars
    for sx, sy in [(0.12, 0.15), (0.85, 0.12), (0.1, 0.85), (0.9, 0.8),
                   (0.5, 0.08)]:
        draw.ellipse([x + sx * d - 1, y + sy * d - 1,
                      x + sx * d + 1, y + sy * d + 1], fill=PAPER)


# -------------------------------------------------------------------- content

MASTHEAD = "THE WORLD TODAY"
DATELINE = "THURSDAY, 26 NOVEMBER 2026  |  THE DAY'S WORLD NEWS IN ONE PAGE"

LEAD_KICKER = "TRADE WAR"
LEAD_HEAD = "TRUMP UNVEILS SWEEPING NEW TARIFFS ON 14 NATIONS"
LEAD_DECK = ("Washington proposes duties of up to 35% on 14 trading partners "
             "to fight factory overcapacity, with China hit hardest and India "
             "facing up to 25%. Markets slid across Asia as the plan landed "
             "on Thanksgiving eve.")

LEFT_KICKER = "MIDDLE EAST"
LEFT_HEAD = "HOUTHIS STRIKE RIYADH TOWER AGAIN - 11 WOUNDED"
LEFT_BODY = ("A drone hit the PIF Tower, the tallest building in Riyadh, "
             "wounding 11 people, two of them Indian nationals. It is the "
             "second strike on the tower in under a week. The Houthis also "
             "claimed an attack on the Ras Tanura refinery, and Brent crude "
             "topped $94 a barrel.")

RIGHT_KICKER = "TECH"
RIGHT_HEAD = "NVIDIA ON DOWNGRADE WATCH AFTER HUANG TURMOIL"
RIGHT_BODY = ("S&P put the chipmaker's credit rating on watch after the "
              "departure and reinstatement of chief executive Jensen Huang "
              "exposed weaknesses in board oversight. Shares fell 5% as "
              "investors weighed the turmoil at the world's most valuable "
              "chip company.")

SPACE_KICKER = "SPACE"
SPACE_HEAD = "FIRST PAKISTANI ASTRONAUT BOUND FOR CHINA'S SPACE STATION"
SPACE_BODY = ("Muhammad Zeeshan Ali will fly aboard Shenzhou-24 to the "
              "Tiangong station, the first foreign astronaut to visit "
              "China's outpost in orbit.")
MERCURY_HEAD = "BEPICOLOMBO SAFELY IN MERCURY ORBIT"
MERCURY_BODY = ("The ESA-JAXA probe was captured by Mercury on 21 November "
                "after an eight-year journey, despite a software glitch "
                "cutting its thruster burn short. Its two orbiters separate "
                "on 9-10 December.")

TICKER = ("MARKETS  -  BRENT $94.61 UP 3.5%   |   WTI $83.53   |   "
          "TAIWAN SHARES DOWN 1,927 PTS   |   SENSEX DOWN 1,484")

BRIEFS = [
    ("PARADE POSTPONED - ",
     "Macy's 100th Thanksgiving Day Parade in New York is put back to "
     "Saturday as a major storm bears down, the first weather "
     "postponement in its history."),
    ("CAIRO TANKER FIRE KILLS 30 - ",
     "A fuel tanker crash ignited a huge fire on a highway around the "
     "Egyptian capital, killing at least 30 people."),
    ("GUKESH HELD TO DRAW - ",
     "World Chess Championship Game 2 ends in a 20-move draw against "
     "Javokhir Sindarov in the London System."),
]

FOOTER = ("Sources: Reuters, ESA, USTR, AP  -  Compiled Thursday 26 November 2026  -  "
          "THE WORLD TODAY")


# --------------------------------------------------------------------- render

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)
    d.rectangle([13, 13, W - 14, H - 14], outline=INK, width=1)

    y = 30
    # masthead
    f_mast = font(58)
    mw = text_w(d, MASTHEAD, f_mast)
    bold(d, ((W - mw) / 2, y), MASTHEAD, f_mast)
    y += 62
    f_date = font(14)
    dw = text_w(d, DATELINE, f_date)
    d.text(((W - dw) / 2, y), DATELINE, font=f_date, fill=GREY)
    y += 24
    rule(d, MARGIN, y, CW, 3)
    y += 6
    rule(d, MARGIN, y, CW, 1)
    y += 12

    # ---- lead story
    y = kicker(d, MARGIN, y, LEAD_KICKER, font(15))
    f_head = font(33)
    for line in wrap(d, LEAD_HEAD, f_head, CW):
        bold(d, (MARGIN, y), line, f_head)
        y += 40
    y += 4
    y = para(d, MARGIN, y, LEAD_DECK, font(16), CW, 21)
    y += 8
    rule(d, MARGIN, y, CW, 2)
    y += 10

    # ---- two-column row
    col_w = (CW - 24) // 2
    lx, rx = MARGIN, MARGIN + col_w + 24
    row_top = y
    # left column
    ly = kicker(d, lx, row_top, LEFT_KICKER, font(14))
    f_ch = font(21)
    for line in wrap(d, LEFT_HEAD, f_ch, col_w):
        bold(d, (lx, ly), line, f_ch)
        ly += 26
    ly += 3
    ly = para(d, lx, ly, LEFT_BODY, font(14), col_w, 19)
    ly += 6
    draw_tower(d, lx, ly, col_w, 46)
    # right column
    ry = kicker(d, rx, row_top, RIGHT_KICKER, font(14))
    for line in wrap(d, RIGHT_HEAD, f_ch, col_w):
        bold(d, (rx, ry), line, f_ch)
        ry += 26
    ry += 3
    ry = para(d, rx, ry, RIGHT_BODY, font(14), col_w, 19)
    ry += 6
    draw_chip(d, rx, ry, col_w, 46)

    y = max(ly, ry) + 46 + 10
    rule(d, MARGIN, y, CW, 2)
    y += 12

    # ---- space band
    y = kicker(d, MARGIN, y, SPACE_KICKER, font(14))
    band_top = y
    text_wd = CW - 150
    f_sh = font(20)
    for line in wrap(d, SPACE_HEAD, f_sh, text_wd):
        bold(d, (MARGIN, y), line, f_sh)
        y += 25
    y += 3
    y = para(d, MARGIN, y, SPACE_BODY, font(14), text_wd, 19)
    y += 8
    f_mh = font(17)
    for line in wrap(d, MERCURY_HEAD, f_mh, text_wd):
        bold(d, (MARGIN, y), line, f_mh)
        y += 22
    y += 2
    y = para(d, MARGIN, y, MERCURY_BODY, font(14), text_wd, 19)
    draw_mercury(d, W - MARGIN - 132, band_top - 2, 132)
    d.text((W - MARGIN - 132, band_top + 136),
           "MERCURY, 21 NOV 2026", font=font(11), fill=GREY)

    y = max(y, band_top + 154) + 8
    rule(d, MARGIN, y, CW, 2)
    y += 8

    # ---- markets ticker (shrink the font until the line fits the page)
    d.rectangle([MARGIN, y, MARGIN + CW, y + 34], fill=INK)
    f_tick = None
    for size in (14, 13, 12, 11):
        f_tick = font(size)
        if text_w(d, TICKER, f_tick) <= CW - 16:
            break
    tw = text_w(d, TICKER, f_tick)
    d.text(((W - tw) / 2, y + 10), TICKER, font=f_tick, fill=PAPER)
    y += 34 + 8

    # ---- briefs
    f_bl = font(14)
    for lead, body in BRIEFS:
        x = MARGIN
        bold(d, (x, y), lead, f_bl)
        x += text_w(d, lead, f_bl)
        y = para(d, x, y, body, f_bl, MARGIN + CW - x, 18)
        y += 3
    y += 2
    rule(d, MARGIN, y, CW, 1)
    y += 8

    # ---- footer
    f_ft = font(11)
    fw = text_w(d, FOOTER, f_ft)
    d.text(((W - fw) / 2, y), FOOTER, font=f_ft, fill=GREY)

    return img


def _save(img):
    """Save entry.png, trying each writable location in turn."""
    targets = []
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    if outdir:
        targets.append(os.path.join(outdir, "entry.png"))
    targets.append(os.path.join(os.getcwd(), "entry.png"))
    here = os.path.dirname(os.path.abspath(__file__))
    targets.append(os.path.join(here, "entry.png"))
    targets.append(os.path.join(tempfile.gettempdir(), "entry.png"))
    last = None
    for path in targets:
        try:
            img.save(path, format="PNG")
            return path
        except Exception as exc:  # noqa: BLE001 - try next location
            last = exc
    raise last


def main():
    img = render()
    path = _save(img)
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
