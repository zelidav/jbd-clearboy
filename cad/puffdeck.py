"""PUFF x JEROME BAKER - the collab concept pack.

Puff ships its one-gram pre-roll in a printed plastic tube with the wordmark running
down the axis. That tube is the cheapest thing in the package and the only thing the
customer keeps. This pack proposes the same tube in hand-blown boro: same format, same
gesture, same wordmark up the side - a vessel that survives the joint and sits on a
shelf afterwards, with a lighter sleeve alongside it as the second piece of the set.

Set in Puff's own system as read off their pack art and their storefront: the tube blue,
the pink of their drip mark, the gold of the grill in it, black and white in support,
and a geometric rounded face in the shape of their wordmark. Poppins stands in for their
display face; final artwork is theirs to approve and none of their own logo files are
redrawn or reproduced here.

Every number in the commercial pages is illustrative and labelled as such. The one thing
in here that is not a proposal is the compliance note on page seven: a cork-stopped glass
tube is not child-resistant, and that decides the shape of the whole programme.

    python cad/puffdeck.py     -> shots/PUFF_x_JBD.pdf, docs/
"""
import os, shutil, sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet

OUT = os.path.join("shots", "PUFF_x_JBD.pdf")
SITE = os.path.join("docs", "PUFF_x_JBD.pdf")
SHOTS = "shots"

PAGE = (1920, 1080)
# sampled off puffprerolls.com: the tube on the pack, the drip mark, the grill in it
BLUE = (47, 180, 245)
PINK = (232, 80, 144)
GOLD = (232, 178, 31)
BLACK = (10, 12, 15)
WHITE = (255, 255, 255)
PAPER = (247, 248, 250)
MUTE = (126, 132, 140)
DEEP = (18, 108, 152)

FONTS = {"h": "assets/fonts/Poppins-ExtraBold.ttf",
         "b": "assets/fonts/Poppins-Bold.ttf",
         "m": "assets/fonts/Poppins-Medium.ttf",
         "r": "assets/fonts/Poppins-Regular.ttf",
         "round": "assets/fonts/VarelaRound-Regular.ttf"}
_F = {}


def font(kind, size):
    k = (kind, int(size))
    if k not in _F:
        _F[k] = ImageFont.truetype(FONTS[kind], int(size))
    return _F[k]


# ------------------------------------------------------------------ furniture
def wrap(d, text, kind, size, width):
    return sheet.wrap(d, text, font(kind, size), width)


def para(d, xy, text, kind, size, fill, width, lead=1.52):
    txt, n = wrap(d, text, kind, size, width)
    d.multiline_text(xy, txt, font=font(kind, size), fill=fill,
                     spacing=size * (lead - 1.0))
    return xy[1] + n * size * lead


def head(d, xy, text, size=72, ink=BLACK, width=1100, lead=1.14):
    d.multiline_text(xy, text.upper(), font=font("h", size), fill=ink,
                     spacing=size * (lead - 1.0))
    return xy[1] + (text.count("\n") + 1) * size * lead


def tracked(d, xy, text, kind, size, fill, track):
    x, y = xy
    f = font(kind, size)
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + track
    return x - track


def tracked_w(d, text, kind, size, track):
    f = font(kind, size)
    return sum(d.textlength(c, font=f) for c in text) + track * (len(text) - 1)


def eyebrow(d, xy, text, ink=PINK, size=20, track=5):
    return tracked(d, xy, text.upper(), "b", size, ink, track)


def pill(d, xy, text, size=20, fill=PINK, ink=WHITE, track=3):
    """The shape Puff's own pack uses for its small facts."""
    x, y = xy
    w = tracked_w(d, text, "b", size, track)
    pad, h = size * 0.95, size * 2.25
    d.rounded_rectangle([x, y, x + w + 2 * pad, y + h], radius=h / 2, fill=fill)
    bb = font("b", size).getbbox(text)
    tracked(d, (x + pad, y + (h - (bb[3] - bb[1])) / 2 - bb[1]), text, "b", size,
            ink, track)
    return w + 2 * pad


def lockup(d, xy, h=44, ink=WHITE, gold=GOLD):
    """PUFF x JEROME BAKER, set at one height and never stretched. Their half is set,
    not placed: no Puff logo file is reproduced in this pack. Their own artwork
    replaces it at sign-off."""
    x, y = xy
    big = font("h", h)
    sub = font("round", h * 0.34)
    ours = font("b", h * 0.66)
    tiny = font("m", h * 0.30)
    d.text((x, y), "PUFF", font=big, fill=ink)
    tracked(d, (x + h * 0.06, y + h * 1.10), "pre-rolls", "round", h * 0.34, ink,
            h * 0.05)
    x += d.textlength("PUFF", font=big) + h * 0.52
    d.text((x, y + h * 0.20), "×", font=font("h", h * 0.72), fill=gold)
    x += d.textlength("×", font=font("h", h * 0.72)) + h * 0.52
    d.text((x, y + h * 0.16), "JEROME BAKER", font=ours, fill=ink)
    tracked(d, (x + h * 0.06, y + h * 1.10), "DESIGNS", "m", h * 0.30, gold, h * 0.12)
    return x + d.textlength("JEROME BAKER", font=ours)


def foot(d, n, ink=MUTE, note=""):
    f = font("m", 19)
    if note:
        d.text((92, PAGE[1] - 62), note, font=f, fill=ink)
    t = "%02d" % n
    d.text((PAGE[0] - 92 - d.textlength(t, font=f), PAGE[1] - 62), t, font=f, fill=ink)


def shot(name, box):
    """A render from shots/. Contained, never distorted."""
    p = os.path.join(SHOTS, name + ".png")
    if not os.path.exists(p):
        raise SystemExit("missing render: " + p + "  (run mockups.py first)")
    return sheet.fit(Image.open(p).convert("RGB"), box)


def card(pg, d, xy, wh, name, fill=(246, 248, 251), radius=26, pad=0):
    """A render on a panel of its own.

    The stills are shot on a studio sweep - a pale grey gradient - so dropping one
    straight onto a black or blue slide leaves a light grey rectangle sitting on it.
    Keying the glass off that sweep is not reliable (the piece is mostly the sweep,
    seen through it), and multiplying the sweep into the slide colour takes the piece
    down with it. So the sweep gets a panel.

    The panel is not a flat colour, because a flat colour behind a gradient is a second
    rectangle inside the first. It is the render's own leftmost column - pure
    background, no piece in it - stretched across the panel, so the sweep runs out to
    the rounded corners and the seam disappears.
    """
    x, y = xy
    w, h = wh
    im = shot(name, (w - 2 * pad, h - 2 * pad))
    bg = im.crop((0, 0, 1, im.height)).resize((w, h), Image.BILINEAR)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                                           fill=255)
    panel = Image.new("RGB", (w, h), fill)
    panel.paste(bg, (0, 0))
    panel.paste(im, (int((w - im.width) / 2), int((h - im.height) / 2)))
    pg.paste(panel, (int(x), int(y)), mask)
    return im


def rule(d, y, x0=92, x1=PAGE[0] - 92, ink=(226, 230, 235), w=2):
    d.rectangle([x0, y, x1, y + w], fill=ink)


def stat(d, xy, big, label, ink=BLACK, sub=MUTE, size=64):
    x, y = xy
    d.text((x, y), big, font=font("h", size), fill=ink)
    para(d, (x, y + size * 1.22), label, "m", 21, sub, 340)
    return y + size * 1.22


def table(d, xy, rows, width, ink=BLACK, sub=MUTE, size=22, lead=52):
    x, y = xy
    for i, (a, b) in enumerate(rows):
        d.text((x, y), a, font=font("m", size), fill=sub)
        bw = d.textlength(b, font=font("b", size))
        d.text((x + width - bw, y), b, font=font("b", size), fill=ink)
        y += lead
        if i < len(rows) - 1:
            rule(d, y - lead * 0.32, x, x + width, (232, 236, 240), 1)
    return y


if __name__ == "__main__":
    import puffdeck_slides
    puffdeck_slides.build()
