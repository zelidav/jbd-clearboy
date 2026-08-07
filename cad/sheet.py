"""Page furniture shared by the leave-behind and the manufacturing spec sheet.

Letter landscape at 150 dpi, drawn with Pillow and saved straight to PDF - no layout
engine, and no dependency the renderer does not already have.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

PAGE = (1650, 1275)                       # 11 x 8.5 in at 150 dpi
DPI = 150.0
INK = (24, 24, 26)
PAPER = (250, 249, 247)
RULE = (198, 195, 190)
GREY = (108, 106, 104)
RED = (168, 34, 46)

_FONTS = {
    True: ("C:/Windows/Fonts/arialbd.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
           "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    False: ("C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf"),
}


def font(bold, size):
    for c in _FONTS[bool(bold)]:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    raise RuntimeError("no sans font found - install DejaVu or Liberation")


def lockup(d, cx, cy, h, ink):
    """JBD x BOUTIQ, centred on cx, drawn at the height asked for and never stretched."""
    sys.path.insert(0, "cad")
    import mockups
    f = font(True, int(h))
    gap = h * 0.55
    jw, xw = d.textlength("JBD", font=f), d.textlength("\u00d7", font=f)
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    bh = h * 1.15
    bw = mockups._tracked_width(probe, "BOUTIQ", font(True, int(bh * 0.62)),
                                bh * 0.14) + 2 * (bh * 0.34)
    x = cx - (jw + gap + xw + gap + bw) / 2
    d.text((x, cy - h * 0.62), "JBD", font=f, fill=ink)
    x += jw + gap
    d.text((x, cy - h * 0.62), "\u00d7", font=f, fill=ink)
    x += xw + gap
    mockups.draw_boutiq(d, x, cy, bh, ink)


def fit(im, box):
    """Contain, never distort."""
    k = min(box[0] / im.width, box[1] / im.height)
    return im.resize((max(int(im.width * k), 1), max(int(im.height * k), 1)),
                     Image.LANCZOS)


def wrap(d, text, f, width):
    """Greedy wrap to a pixel width. Returns (text, line count)."""
    out, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if line and d.textlength(trial, font=f) > width:
            out.append(line); line = word
        else:
            line = trial
    out.append(line)
    return "\n".join(out), len(out)


def blank(bg=PAPER):
    pg = Image.new("RGB", PAGE, bg)
    return pg, ImageDraw.Draw(pg)


def save(pages, path, title):
    pages[0].save(path, save_all=True, append_images=pages[1:], resolution=DPI,
                  title=title)
    print("wrote", path, "\u2014", len(pages), "pages")
    return path
