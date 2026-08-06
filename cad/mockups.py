"""Pieces, colourways and hero stills.

Pieces
  hammer   the Clearboy hammer, thickened stem, enamel label
  jar      38 mm stash jar, 3 mm wall, embossed JBD medallion

Colourways (both fumed, both frit-rolled with clear marbles)
  teal_silver   bluish-teal body, silver fume, teal frit, clear marbles
  magenta_gold  magenta body, gold fume, magenta frit, clear marbles

Glass is rendered denser than a clear piece would be - the point of these is the
colour, not an X-ray of the wall.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
import render

OUT = "shots"
TEXT = "JEROME BAKER"
SIDE = 0.0                       # yaw where the piece reads broadside to camera

PIECES = {
 "hammer": dict(
     body="out/clearboy_hammer.stl", frit="out/frit.stl", marbles="out/marbles.stl",
     cam_r=700.0, target=(0, 0, 74), fov=17.0, shadow=(0.5, 0.30, 0.075),
     decal=(20.0, 74.0, 7.0),      # z0, z1, stem radius
     name="Clearboy hammer", note="140 mm \u00b7 hand-blown original"),
 "jar": dict(
     body="out/jar.stl", frit="out/jar_frit.stl", marbles="out/jar_marbles.stl",
     cam_r=620.0, target=(0, 0, 47), fov=17.0, shadow=(0.5, 0.34, 0.175),
     decal=None,
     name="Stash jar", note="92 mm \u00b7 38 mm opening"),
}

WAYS = {
 "teal_silver": dict(
     body=(0.135, 0.040, 0.050), frit=(0.42, 0.115, 0.16),
     fume=1.0, fume_cool=(0.80, 0.87, 1.00), fume_warm=(0.95, 0.86, 1.00),
     line=(0.02, 0.13, 0.14), fline=(0.01, 0.11, 0.12),
     label=(14, 122, 106), label_text=(255, 255, 255),
     name="Bluish teal \u00b7 silver fume",
     sub="teal frit \u00b7 clear marbles"),
 "magenta_gold": dict(
     body=(0.040, 0.170, 0.078), frit=(0.115, 0.44, 0.21),
     fume=1.0, fume_cool=(0.97, 0.80, 0.88), fume_warm=(1.00, 0.80, 0.58),
     line=(0.15, 0.02, 0.10), fline=(0.13, 0.01, 0.09),
     label=(150, 32, 108), label_text=(255, 255, 255),
     name="Magenta \u00b7 gold fume",
     sub="magenta frit \u00b7 clear marbles"),
}

MARBLE = dict(absorb=(0.004, 0.004, 0.004), line=(0.14, 0.15, 0.17))

FONT = "C:/Windows/Fonts/arialbd.ttf"


def make_label(text, fill, ink, w=2400, h=420, pad=0.13):
    """Enamel label: solid colour band, lettering dropped out in white.
    u runs up the stem, v across the face; mirrored in v so it reads correctly
    on the camera side of the tube."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = int(h * pad)
    d.rounded_rectangle([0, m, w - 1, h - m - 1], radius=int((h - 2 * m) * 0.30),
                        fill=fill + (255,))
    size = int((h - 2 * m) * 0.46)
    f = ImageFont.truetype(FONT, size)
    tw = d.textlength(text, font=f)
    if tw > w * 0.86:
        size = int(size * w * 0.86 / tw)
        f = ImageFont.truetype(FONT, size)
        tw = d.textlength(text, font=f)
    d.text(((w - tw) / 2, h / 2 - size * 0.62), text, font=f, fill=ink + (255,))
    return img.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)


def build_renderer(piece, key, W, H):
    p, c = PIECES[piece], WAYS[key]
    r = render.Renderer(W, H)
    r.add(p["body"], absorb=c["body"], fume=c["fume"],
          fume_warm=c["fume_warm"], fume_cool=c["fume_cool"],
          line=c["line"], kAmt=0.38, kPow=2.6, spec=1.0,
          decal=p["decal"] is not None, solid=True, min_thick=2.2)
    r.add(p["frit"], absorb=c["frit"], fume=0.0, line=c["fline"],
          kAmt=0.22, kPow=2.0, spec=1.25, solid=True, min_thick=3.4, smooth=0.0)
    r.add(p["marbles"], absorb=MARBLE["absorb"], fume=0.0, line=MARBLE["line"],
          kAmt=0.70, kPow=3.0, spec=1.60, smooth=60.0)
    if p["decal"]:
        z0, z1, rad = p["decal"]
        r.set_decal(make_label(TEXT, c["label"], c["label_text"]), z0, z1, rad)
    return r


def frame(r, piece, angle):
    p = PIECES[piece]
    return r.frame(angle, cam_r=p["cam_r"], target=p["target"], fov=p["fov"],
                   shadow=p["shadow"])


def shot(piece, key, angle=SIDE, W=900, H=1180, tag=""):
    os.makedirs(OUT, exist_ok=True)
    im = frame(build_renderer(piece, key, W, H), piece, angle)
    im.save(f"{OUT}/{piece}_{key}{tag}.png")
    print("wrote", piece, key + tag, im.size)
    return im


if __name__ == "__main__":
    args = sys.argv[1:]
    pieces = [a for a in args if a in PIECES] or list(PIECES)
    ways = [a for a in args if a in WAYS] or list(WAYS)
    for pc in pieces:
        for k in ways:
            shot(pc, k)
