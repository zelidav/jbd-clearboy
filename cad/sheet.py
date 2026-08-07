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


CJK = {
    True: ("C:/Windows/Fonts/msyhbd.ttc",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
           "/System/Library/Fonts/PingFang.ttc"),
    False: ("C:/Windows/Fonts/msyh.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/PingFang.ttc"),
}
_FACE = _FONTS


def use_cjk(on=True):
    """Swap the whole sheet onto a CJK face. It sets Latin correctly too, so the mixed
    lines a spec sheet is full of - 140 mm, boro 3.3 - stay in one face."""
    global _FACE
    _FACE = CJK if on else _FONTS


def font(bold, size):
    for c in _FACE[bool(bold)]:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    raise RuntimeError("no font found for the current face")


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


def _tokens(text):
    """Split into things a line may break between. Chinese has no spaces, so every han
    character is its own break opportunity; Latin runs stay whole."""
    out, run = [], ""
    for c in text:
        han = "　" <= c <= "鿿" or "＀" <= c <= "￯"
        if han or c == " ":
            if run:
                out.append(run); run = ""
            if han:
                out.append(c)
            else:
                out.append(" ")
        else:
            run += c
    if run:
        out.append(run)
    return out


def wrap(d, text, f, width):
    """Greedy wrap to a pixel width. Returns (text, line count)."""
    out, line = [], ""
    for tok in _tokens(text):
        if tok == " ":
            if line:
                line += " "
            continue
        trial = line + tok
        if line.strip() and d.textlength(trial, font=f) > width:
            out.append(line.rstrip()); line = tok
        else:
            line = trial
    out.append(line.rstrip())
    return "\n".join(out), len(out)


def blank(bg=PAPER):
    pg = Image.new("RGB", PAGE, bg)
    return pg, ImageDraw.Draw(pg)


def save(pages, path, title):
    pages[0].save(path, save_all=True, append_images=pages[1:], resolution=DPI,
                  title=title)
    print("wrote", path, "\u2014", len(pages), "pages")
    return path
