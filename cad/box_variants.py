"""One box, three sleeves.

The box is printed once and carries nothing that changes - no strain, no batch, no
potency. A paper sleeve slips over it and that is the only thing that moves between
drops, along with the sticker.

So this is one render of the box, once, with the three sleeves beside it. That is the
argument: the expensive parts are made a single time.

    python cad/box_variants.py     -> shots/puff_box_variants.png
"""
import math, os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mockups
import variable_art
from mockups import PUFF, brand_font, puff_mark, _tracked_text, _tracked_width, _pill

OUT = os.path.join("shots", "puff_box_variants.png")
OUT_ROW = os.path.join("shots", "puff_box_variants_row.png")
WAY = "puff_blue"


def render():
    """The box, once. Its print never changes, so neither does this."""
    p = mockups.PIECES["box"]
    W, H = mockups.size_of("box")
    r = mockups.build_renderer("box", WAY, W, H)
    return mockups.frame(r, "box", mockups.SIDE + math.radians(p.get("yaw", 0.0)))


def build(row=False):
    """row=True lays it out for a slide; the column suits a web page."""
    os.makedirs("shots", exist_ok=True)
    box = render()
    sleeves = [(n, variable_art.sleeve(n, c)) for n, c in variable_art.DROPS]

    pad, lab = 34, 46
    bw = 1180 if not row else 980
    bh = int(box.height * bw / box.width)
    sw = bw if not row else 900
    sh = int(sleeves[0][1].height * sw / sleeves[0][1].width)

    f = brand_font("bold", 30)
    fs = brand_font("med", 23)
    if row:
        w = pad * 3 + bw + sw
        h = max(pad + lab + bh, pad + lab + (sh + lab) * len(sleeves)) + pad
        plate = Image.new("RGB", (w, h), (244, 247, 250))
        d = ImageDraw.Draw(plate)
        d.text((pad, pad), "ONE BOX, PRINTED ONCE", font=f, fill=(34, 38, 44))
        plate.paste(box.resize((bw, bh), Image.LANCZOS), (pad, pad + lab))
        x = pad * 2 + bw
        d.text((x, pad), "THREE SLEEVES", font=f, fill=(34, 38, 44))
        y = pad + lab
        for name, im in sleeves:
            plate.paste(im.resize((sw, sh), Image.LANCZOS), (x, y), im.resize((sw, sh)))
            y += sh + lab
        plate.save(OUT_ROW)
        print("wrote", OUT_ROW, plate.size)
        return OUT_ROW

    w = pad * 2 + bw
    h = pad + lab + bh + pad + (sh + lab) * len(sleeves) + pad
    plate = Image.new("RGB", (w, h), (244, 247, 250))
    d = ImageDraw.Draw(plate)
    d.text((pad, pad), "ONE BOX, PRINTED ONCE", font=f, fill=(34, 38, 44))
    d.text((pad + d.textlength("ONE BOX, PRINTED ONCE", font=f) + 18, pad + 8),
           "nothing on it changes between drops", font=fs, fill=(128, 134, 142))
    plate.paste(box.resize((bw, bh), Image.LANCZOS), (pad, pad + lab))
    y = pad + lab + bh + pad
    for name, im in sleeves:
        d.text((pad, y), "SLEEVE  ·  %s" % name, font=f, fill=(34, 38, 44))
        r2 = im.resize((sw, sh), Image.LANCZOS)
        plate.paste(r2, (pad, y + lab), r2)
        y += sh + lab
    plate.save(OUT)
    print("wrote", OUT, plate.size)
    return OUT


if __name__ == "__main__":
    build()
    build(row=True)
