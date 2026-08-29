"""The two parts of the pack that change, drawn flat.

Two, and only two. The glass is one spec, the box is one print run, and neither carries
a strain name, a batch number or a potency figure. Everything variable lives on a paper
sleeve and a sticker - the two cheapest things in the pack to reprint.

That is what makes the drop repeatable. A new strain is a new sleeve and a new sticker;
the glass and the board are untouched, so the second drop costs a fraction of the first
and can be decided late.

Flat plates, not renders. These are artwork mockups - what goes on the card, at the
right proportions - not a photograph of one.

    python cad/variable_art.py     -> shots/puff_variable.png
"""
import os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mockups
from mockups import (PUFF, brand_font, puff_mark, _tracked_text,
                     _tracked_width, _pill)

OUT = os.path.join("shots", "puff_variable.png")

# Puff's own strain names, off their storefront - the point of the page is that these
# are the only thing that changes
DROPS = [("GRAPE DRINK", (96, 80, 192)), ("ORANGE TREE", (224, 128, 80)),
         ("OG KUSH", (14, 158, 90))]

SCALE = 5.6                      # px per mm on the plate
SLEEVE = (170.0, 46.0)           # the sleeve round the box, laid flat
STICKER = (46.0, 30.0)           # the strain and potency sticker
SEAL = 30.0                      # the seal that closes the tissue, dia


def mm(v):
    return int(round(v * SCALE))


def _fit(d, text, kind, size, max_w, track=0.0):
    """Shrink a tracked string until it fits. Everything on these plates is set to a
    width that is not negotiable - a card is 44 mm wide whatever the strain is called."""
    for _ in range(9):
        f = brand_font(kind, max(int(size), 5))
        w = _tracked_width(d, text, f, size * track)
        if w <= max_w:
            return f, w, size * track
        size *= max_w / w
    return f, w, size * track


def _lockup(im, d, cx, y, h, ink=PUFF["paper"], gold=PUFF["gold"], max_w=None):
    """Their mark, a cross, our name. Their half is their own file rather than a
    typesetting of it - PUFF is a display face nothing else matches."""
    for _ in range(9):
        mark = puff_mark(max(h * 1.55, 6), ink)
        ours = brand_font("bold", max(int(h * 0.62), 4))
        cross = brand_font("heavy", max(int(h * 0.78), 4))
        total = (mark.width + d.textlength("×", font=cross)
                 + d.textlength("JEROME BAKER", font=ours) + h * 0.84)
        if max_w is None or total <= max_w:
            break
        h *= max_w / total
    xw = d.textlength("×", font=cross)
    x = cx - total / 2
    im.paste(mark, (int(x), int(y - mark.height * 0.16)), mark)
    x += mark.width + h * 0.42
    d.text((x, y + h * 0.10), "×", font=cross, fill=gold + (255,))
    x += xw + h * 0.42
    d.text((x, y + h * 0.14), "JEROME BAKER", font=ours, fill=ink + (255,))


def sleeve(name, accent):
    """The sleeve round the box, laid flat.

    The strain's colour is the sleeve's colour, which is the cheapest possible way to
    make one box look like a different product."""
    w, h = mm(SLEEVE[0]), mm(SLEEVE[1])
    im = Image.new("RGBA", (w, h), accent + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.10), w, int(h * 0.125)], fill=PUFF["gold"] + (255,))
    d.rectangle([0, int(h * 0.875), w, int(h * 0.90)], fill=PUFF["gold"] + (255,))
    _lockup(im, d, w * 0.30, h * 0.34, h * 0.145, max_w=w * 0.44)
    f, tw, tr = _fit(d, name, "heavy", h * 0.30, w * 0.36, 0.22)
    _tracked_text(d, (w * 0.94 - tw, h * 0.36), name, f,
                  PUFF["paper"] + (255,), tr)
    return im


def seal():
    """The sticker that closes the tissue round the piece.

    It is the first thing a hand touches and the last thing between them and the glass,
    so it carries the lockup and nothing else."""
    d0 = mm(SEAL)
    im = Image.new("RGBA", (d0, d0), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, d0 - 1, d0 - 1], fill=PUFF["blue"] + (255,))
    k = int(d0 * 0.085)
    d.ellipse([k, k, d0 - 1 - k, d0 - 1 - k], outline=PUFF["gold"] + (255,),
              width=max(int(d0 * 0.022), 2))
    _lockup(im, d, d0 / 2, d0 * 0.34, d0 * 0.13, max_w=d0 * 0.66)
    f, w, tr = _fit(d, "HOLIDAY COLLAB", "bold", d0 * 0.075, d0 * 0.60, 0.30)
    _tracked_text(d, ((d0 - w) / 2, d0 * 0.58), "HOLIDAY COLLAB", f,
                  PUFF["paper"] + (255,), tr)
    return im


def sticker():
    """Strain and potency. The one part a regulator makes you change, and the one that
    can be printed the week it is packed rather than the quarter before."""
    w, h = mm(STICKER[0]), mm(STICKER[1])
    im = Image.new("RGBA", (w, h), (252, 252, 250, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=int(w * 0.05),
                        outline=(190, 194, 198, 255), width=2)
    f = brand_font("bold", int(w * 0.062))
    d.text((w * 0.07, h * 0.11), "STRAIN / POTENCY", font=f, fill=(40, 44, 50))
    fs = brand_font("med", int(w * 0.052))
    for i, t in enumerate(("Lot 0000  ·  Packaged 00/00/26",
                           "Total THC 00.0%  ·  Net wt 1 g",
                           "Government warning, licence no.")):
        d.text((w * 0.07, h * 0.32 + i * h * 0.19), t, font=fs, fill=(96, 102, 110))
    # the symbol sits in the corner the copy stops short of
    d.rectangle([w * 0.845, h * 0.10, w * 0.945, h * 0.30], outline=(150, 40, 40),
                width=2)
    d.text((w * 0.876, h * 0.125), "!", font=brand_font("heavy", int(w * 0.058)),
           fill=(150, 40, 40))
    return im


def build():
    os.makedirs("shots", exist_ok=True)
    sleeves = [(n, sleeve(n, c)) for n, c in DROPS]
    st, sl = sticker(), seal()

    pad = mm(9)
    w = pad * 2 + sleeves[0][1].width
    h = pad + (sleeves[0][1].height + mm(13)) * len(sleeves) + mm(13) + st.height + pad
    plate = Image.new("RGB", (w, h), (244, 247, 250))
    d = ImageDraw.Draw(plate)
    f = brand_font("bold", mm(3.4))

    y = pad
    for name, im in sleeves:
        d.text((pad, y), "SLEEVE  \u00b7  %s" % name, font=f, fill=(60, 66, 74))
        plate.paste(im, (pad, y + mm(5)), im)
        y += im.height + mm(13)

    d.text((pad, y), "STRAIN / POTENCY STICKER", font=f, fill=(60, 66, 74))
    plate.paste(st, (pad, y + mm(5)), st)
    d.text((pad + st.width + pad, y), "TISSUE SEAL", font=f, fill=(60, 66, 74))
    plate.paste(sl, (pad + st.width + pad, y + mm(5)), sl)

    note = "The glass and the box never change. Only these do."
    d.text((pad, h - mm(6)), note, font=brand_font("med", mm(3.2)), fill=(110, 116, 124))
    plate.save(OUT)
    print("wrote", OUT, plate.size)
    return OUT


if __name__ == "__main__":
    build()
