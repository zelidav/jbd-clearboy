"""The parts of the pack that change, drawn flat.

The glass is one print run. Everything that has to vary - the strain, the batch, the
numbers a regulator wants - lives on paper that is cheap to reprint: a beauty card over
the piece, a band round it, and a compliance sticker that goes on last.

That split is the whole reason this works at volume. One spec on the bench, one label
on the glass, and a card and a band that change per drop without touching the glass at
all.

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
CARD = (44.0, 150.0)             # the beauty card, mm - it lies over the piece
BAND = (150.0, 26.0)             # the band round the tube, laid flat
STICKER = (46.0, 30.0)           # the compliance sticker
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


def beauty_card(name, accent):
    """The card that sits over the piece in the box. Reprinted per drop; the glass is
    not."""
    w, h = mm(CARD[0]), mm(CARD[1])
    im = Image.new("RGBA", (w, h), PUFF["blue"] + (255,))
    d = ImageDraw.Draw(im)
    k = int(w * 0.055)
    d.rounded_rectangle([k, k, w - k, h - k], radius=int(w * 0.10),
                        outline=PUFF["gold"] + (255,), width=max(int(w * 0.012), 2))

    _lockup(im, d, w / 2, h * 0.075, w * 0.115, max_w=w * 0.80)

    # the strain, which is the only thing that changes
    d.rectangle([w * 0.20, h * 0.185, w * 0.80, h * 0.189], fill=PUFF["gold"] + (255,))
    f, _, _ = _fit(d, max(name.split(), key=len), "heavy", w * 0.145, w * 0.74)
    for i, word in enumerate(name.split()):
        tw = d.textlength(word, font=f)
        d.text(((w - tw) / 2, h * 0.225 + i * w * 0.165), word, font=f,
               fill=PUFF["paper"] + (255,))

    # a plate of the drop's own colour - stands in for strain artwork
    box = [w * 0.16, h * 0.44, w * 0.84, h * 0.72]
    d.rounded_rectangle(box, radius=int(w * 0.07), fill=accent + (255,))
    fa = brand_font("med", int(w * 0.058))
    t = "STRAIN ARTWORK"
    tw = _tracked_width(d, t, fa, w * 0.014)
    _tracked_text(d, ((w - tw) / 2, h * 0.565), t, fa, (255, 255, 255, 190), w * 0.014)

    lab = "HOLIDAY COLLAB"
    fs, lw, tr = _fit(d, lab, "bold", w * 0.052, w * 0.72, 0.38)
    _tracked_text(d, ((w - lw) / 2, h * 0.775), lab, fs, PUFF["paper"] + (255,), tr)
    n = "ONE GRAM  ·  HAND BLOWN GLASS"
    fn, nw, tr2 = _fit(d, n, "med", w * 0.046, w * 0.76, 0.26)
    _tracked_text(d, ((w - nw) / 2, h * 0.828), n, fn, (255, 255, 255, 205), tr2)
    return im


def band(name, accent):
    """The band round the tube, laid flat. Same job as the card, less of it."""
    w, h = mm(BAND[0]), mm(BAND[1])
    im = Image.new("RGBA", (w, h), accent + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.12), w, int(h * 0.145)], fill=PUFF["gold"] + (255,))
    d.rectangle([0, int(h * 0.855), w, int(h * 0.88)], fill=PUFF["gold"] + (255,))
    f, tw, tr = _fit(d, name, "heavy", h * 0.36, w * 0.80, 0.25)
    _tracked_text(d, ((w - tw) / 2, h * 0.30), name, f, PUFF["paper"] + (255,), tr)
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
    """The compliance sticker: batch, potency, the symbol, the warnings. It goes on
    last and it is the only thing a regulator makes you change."""
    w, h = mm(STICKER[0]), mm(STICKER[1])
    im = Image.new("RGBA", (w, h), (252, 252, 250, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=int(w * 0.05),
                        outline=(190, 194, 198, 255), width=2)
    f = brand_font("bold", int(w * 0.062))
    d.text((w * 0.07, h * 0.11), "BATCH / POTENCY", font=f, fill=(40, 44, 50))
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
    cards = [beauty_card(n, c) for n, c in DROPS]
    bands = [band(n, c) for n, c in DROPS]
    st = sticker()
    sl = seal()

    pad = mm(9)
    col_w = cards[0].width
    # width follows the number of drops shown, not a hardcoded two - adding a
    # third strain silently pushed the bands off the right of the plate
    w = (pad * (len(cards) + 2) + col_w * len(cards)
         + max(bands[0].width, st.width + mm(SEAL) + pad) + pad)
    h = pad * 2 + cards[0].height + mm(16)
    plate = Image.new("RGB", (w, h), (244, 247, 250))
    d = ImageDraw.Draw(plate)

    x = pad
    for i, c in enumerate(cards):
        plate.paste(c, (x, pad + mm(14)), c)
        f = brand_font("bold", mm(3.4))
        d.text((x, pad), "BEAUTY CARD", font=f, fill=(60, 66, 74))
        x += col_w + pad

    y = pad + mm(14)
    f = brand_font("bold", mm(3.4))
    d.text((x, pad), "BAND", font=f, fill=(60, 66, 74))
    for i, b in enumerate(bands):
        plate.paste(b, (x, y), b)
        y += b.height + pad
    d.text((x, y + mm(2)), "COMPLIANCE STICKER", font=f, fill=(60, 66, 74))
    plate.paste(st, (x, y + mm(9)), st)
    sx = x + st.width + pad
    d.text((sx, y + mm(2)), "TISSUE SEAL", font=f, fill=(60, 66, 74))
    plate.paste(sl, (sx, y + mm(9)), sl)

    note = ("The glass never changes. The card, the band, the seal and the sticker do "
            "- so a new strain is a print run, not a new piece.")
    d.text((pad, h - mm(9)), note, font=brand_font("med", mm(3.2)), fill=(110, 116, 124))
    plate.save(OUT)
    print("wrote", OUT, plate.size)
    return OUT


if __name__ == "__main__":
    build()
