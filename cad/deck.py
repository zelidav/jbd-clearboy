"""JBD x Boutiq collector's box - the review deck, set in Boutiq's own brand system.

Colour, type and furniture come from the Boutiq Brand Guide 2026: Boutiq Pink #DA1984
carrying the deck, Boutiq Teal #12CFCA on the accents, black and white in support, and
the sticker pile behind the section breaks. Urbane Rounded sets the headings and body,
Silkscreen sets every number, eyebrow and badge - which is also how the brand handles
its own wordmarks, and conveniently the one face here with a full character set.

Content follows the 4 August call: 25 + 3 at 28 all in, 10,000 units into Massachusetts,
Indica and Sativa with no hybrid, November 1. Nothing is claimed as settled that was
left open on that call - the pattern swap, the glass colour and the Boston logo pack
all sit on the open-items page, where they belong.

    python cad/deck.py     -> shots/JBD_x_Boutiq_Deck.pdf, docs/
"""
import os, shutil, sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet

SHOTS = "C:/Users/zelid/Downloads"
OUT = os.path.join("shots", "JBD_x_Boutiq_Deck.pdf")
SITE = os.path.join("docs", "JBD_x_Boutiq_Deck.pdf")
PATTERN = os.path.join("assets", "boutiq_stickers.png")

PAGE = (1920, 1080)
PINK = (218, 25, 132)
TEAL = (18, 207, 202)
BLACK = (12, 12, 14)
WHITE = (255, 255, 255)
PAPER = (243, 243, 243)
MUTE = (122, 122, 126)

FONTS = {"h": "assets/fonts/UrbaneRounded-DemiBold.otf",
         "b": "assets/fonts/UrbaneRounded-Light.otf",
         "px": "assets/fonts/Silkscreen-Regular.ttf"}
_COV, _F = {}, {}


def font(kind, size):
    k = (kind, int(size))
    if k not in _F:
        _F[k] = ImageFont.truetype(FONTS[kind], int(size))
    return _F[k]


def _cov(kind):
    """What the face can actually set. The Urbane weights come out of the brand guide
    as subsets, so a stray glyph would draw as a box - better to hear about it."""
    if kind not in _COV:
        from fontTools.ttLib import TTFont
        _COV[kind] = set(TTFont(FONTS[kind]).getBestCmap())
    return _COV[kind]


def check(text, kind):
    miss = sorted({c for c in text if ord(c) not in _cov(kind) and c not in "\n"})
    if miss:
        raise SystemExit("%s cannot set %r in: %.60s" % (FONTS[kind], "".join(miss), text))
    return text


# ------------------------------------------------------------------- furniture

def stickers(size, ink, bg, amount=1.0):
    """The Boutiq sticker pile, recoloured. It ships as black art on white, so its own
    darkness is the mask and the two colours are ours."""
    w, h = size
    src = Image.open(PATTERN).convert("L")
    k = max(w / src.width, h / src.height)
    src = src.resize((max(int(src.width * k), w), max(int(src.height * k), h)),
                     Image.LANCZOS).crop((0, 0, w, h))
    mask = src.point(lambda v: int((255 - v) * amount))
    out = Image.new("RGB", size, bg)
    out.paste(Image.new("RGB", size, ink), (0, 0), mask)
    return out


def pixel_rect(d, box, fill=None, outline=None, unit=6, width=0):
    """A rounded rectangle with the corners stepped rather than curved - the shape the
    brand puts round its wordmarks."""
    x0, y0, x1, y1 = box
    u = unit
    d.rectangle([x0 + u, y0, x1 - u, y1], fill=fill)
    d.rectangle([x0, y0 + u, x1, y1 - u], fill=fill)
    d.rectangle([x0 + u // 2, y0 + u // 2, x1 - u // 2, y1 - u // 2], fill=fill)
    if outline:
        for (a, b, c, e) in ((x0 + u, y0, x1 - u, y0 + width),
                             (x0 + u, y1 - width, x1 - u, y1),
                             (x0, y0 + u, x0 + width, y1 - u),
                             (x1 - width, y0 + u, x1, y1 - u),
                             (x0 + u // 2, y0 + u // 2, x0 + u, y0 + u // 2 + width),
                             (x0 + u // 2, y0 + u // 2, x0 + u // 2 + width, y0 + u),
                             (x1 - u, y0 + u // 2, x1 - u // 2, y0 + u // 2 + width),
                             (x1 - u // 2 - width, y0 + u // 2, x1 - u // 2, y0 + u),
                             (x0 + u // 2, y1 - u // 2 - width, x0 + u, y1 - u // 2),
                             (x0 + u // 2, y1 - u, x0 + u // 2 + width, y1 - u // 2),
                             (x1 - u, y1 - u // 2 - width, x1 - u // 2, y1 - u // 2),
                             (x1 - u // 2 - width, y1 - u, x1 - u // 2, y1 - u // 2)):
            d.rectangle([a, b, c, e], fill=outline)


def badge(d, xy, text, h=34, fill=None, ink=WHITE, track=None):
    """Pixel badge - Silkscreen, letterspaced, in a stepped frame."""
    x, y = xy
    f = font("px", h)
    track = h * 0.22 if track is None else track
    w = sum(d.textlength(c, font=f) for c in text) + track * (len(text) - 1)
    pad = h * 0.62
    box = [x, y, x + w + 2 * pad, y + h * 1.9]
    u = max(int(h * 0.20), 4)
    if fill is not None:
        pixel_rect(d, box, fill=fill, unit=u)
        pixel_rect(d, box, outline=ink, unit=u, width=max(int(h * 0.09), 3))
    else:
        pixel_rect(d, box, outline=ink, unit=u, width=max(int(h * 0.09), 3))
    cx = x + pad
    for c in text:
        d.text((cx, y + h * 0.52), c, font=f, fill=ink)
        cx += d.textlength(c, font=f) + track
    return box[2] - box[0]


def lockup(d, xy, h=44, ink=WHITE):
    """JBD x BOUTIQ, the way the lid carries it."""
    x, y = xy
    f = font("px", h)
    d.text((x, y + h * 0.52), "JBD", font=f, fill=ink)
    x += d.textlength("JBD", font=f) + h * 0.7
    d.text((x, y + h * 0.52), "x", font=f, fill=ink)
    x += d.textlength("x", font=f) + h * 0.7
    return x + badge(d, (x, y), "BOUTIQ", h, ink=ink)


def shot(name, box):
    p = os.path.join(SHOTS, name + ".jpg")
    if not os.path.exists(p):
        raise SystemExit("missing render: " + p)
    return sheet.fit(Image.open(p).convert("RGB"), box)


def wrap(d, text, kind, size, width):
    return sheet.wrap(d, check(text, kind), font(kind, size), width)


def para(d, xy, text, kind, size, fill, width, lead=1.5):
    txt, n = wrap(d, text, kind, size, width)
    d.multiline_text(xy, txt, font=font(kind, size), fill=fill,
                     spacing=size * (lead - 1.0))
    return xy[1] + n * size * lead


def foot(d, n, ink=MUTE, total=10):
    f = font("px", 22)
    t = "/%02d" % n
    d.text((PAGE[0] - 80 - d.textlength(t, font=f), PAGE[1] - 74), t, font=f, fill=ink)


def eyebrow(d, xy, text, ink=PINK, size=24, track=6):
    x, y = xy
    f = font("px", size)
    for c in check(text, "px"):
        d.text((x, y), c, font=f, fill=ink)
        x += d.textlength(c, font=f) + track
    return x


def head(d, xy, text, size=76, ink=BLACK, width=1000):
    return para(d, xy, text.upper(), "h", size, ink, width, lead=1.16)


if __name__ == "__main__":
    import deck_slides
    deck_slides.build()
