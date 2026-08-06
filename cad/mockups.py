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
TEXT = "JBD X BOUTIQ"
SIDE = 0.0                       # yaw where the piece reads broadside to camera

PIECES = {
 "hammer": dict(
     body="out/clearboy_hammer.stl", frit="out/frit.stl", marbles="out/marbles.stl",
     cam_r=545.0, target=(0, 0, 72), fov=17.0, shadow=(0.5, 0.30, 0.055),
     decal=(20.0, 74.0, 7.0),      # z0, z1, stem radius
     lines_body="out/hammer_lines.stl", lines_frit="out/hammer_lines.stl",
     size=(900, 760),              # one frame size for the whole standing->flat sweep
     name="Clearboy hammer", note="140 mm \u00b7 hand-blown original"),
 "hammer_flat": dict(
     body="out/clearboy_hammer.stl", frit="out/frit.stl", marbles="out/marbles.stl",
     cam_r=395.0, target=(0, 0, 10), fov=17.0, shadow=(0.5, 0.46, 0.10),
     decal=(20.0, 74.0, 7.0), tilt=-90.0, shift=(70.0, 0.0, 8.0), size=(1000, 700),
     name="Hammer, laid down", note="how it sits in the case"),
 "jar": dict(
     body="out/jar.stl", frit="out/jar_frit.stl", marbles="out/jar_marbles.stl",
     cork="out/jar_cork.stl", lines_body="out/jar_lines.stl",
     lines_frit="out/jar_lines_frit.stl",
     cam_r=455.0, target=(0, 0, 56), fov=17.0, shadow=(0.5, 0.32, 0.115),
     decal=None,
     name="Nug jar", note="92 mm \u00b7 38 mm opening \u00b7 cork lid"),
}

WAYS = {
 "teal_silver": dict(
     body=(0.135, 0.040, 0.050), frit=(0.42, 0.115, 0.16),
     fume=1.05, fume_pow=1.05,
     # silver: near-white face on, then steel, violet, and a warm flash at the edge
     fume_stops=((1.00, 1.00, 1.00), (0.90, 0.95, 1.04),
                 (0.93, 0.88, 1.08), (1.06, 0.98, 0.86)),
     line=(0.02, 0.13, 0.14), fline=(0.01, 0.11, 0.12),
     label=(14, 122, 106), label_text=(255, 255, 255),
     lines="frit", wrap=(0.004, 0.004, 0.004),
     name="Bluish teal \u00b7 silver fume",
     sub="teal frit \u00b7 clear marbles \u00b7 clear linework"),
 "magenta_gold": dict(
     body=(0.040, 0.170, 0.078), frit=(0.115, 0.44, 0.21),
     fume=1.05, fume_pow=1.05,
     # gold: pale metal, then straw, rose, and violet where it turns over
     fume_stops=((1.00, 0.99, 0.96), (1.06, 0.99, 0.84),
                 (1.06, 0.88, 0.84), (0.94, 0.88, 1.06)),
     line=(0.15, 0.02, 0.10), fline=(0.13, 0.01, 0.09),
     label=(150, 32, 108), label_text=(255, 255, 255),
     lines="frit", wrap=(0.004, 0.004, 0.004),
     name="Magenta \u00b7 gold fume",
     sub="magenta frit \u00b7 clear marbles \u00b7 clear linework"),

 "clear_silver": dict(
     body=(0.0045, 0.0040, 0.0038), frit=(0.42, 0.115, 0.16),
     fume=1.35, fume_pow=0.90,
     fume_stops=((1.00, 1.00, 1.00), (0.88, 0.94, 1.06),
                 (0.92, 0.86, 1.10), (1.08, 0.98, 0.84)),
     line=(0.09, 0.11, 0.14), fline=(0.01, 0.11, 0.12),
     marble=(0.30, 0.085, 0.12), wrap=(0.30, 0.085, 0.12), lines="body",
     label=(14, 122, 106), label_text=(255, 255, 255),
     name="Clear \u00b7 heavy silver fume",
     sub="teal frit, marbles \u00b7 wrapped linework"),
 "clear_gold": dict(
     body=(0.0045, 0.0040, 0.0038), frit=(0.115, 0.44, 0.21),
     fume=1.35, fume_pow=0.90,
     fume_stops=((1.00, 0.99, 0.95), (1.08, 1.00, 0.82),
                 (1.08, 0.86, 0.82), (0.92, 0.86, 1.08)),
     line=(0.14, 0.10, 0.06), fline=(0.13, 0.01, 0.09),
     marble=(0.085, 0.34, 0.16), wrap=(0.085, 0.34, 0.16), lines="body",
     label=(150, 32, 108), label_text=(255, 255, 255),
     name="Clear \u00b7 heavy gold fume",
     sub="magenta frit, marbles \u00b7 wrapped linework"),
}

MARBLE = dict(absorb=(0.004, 0.004, 0.004), line=(0.14, 0.15, 0.17))
# cork is not glass: a thickness floor plus heavy absorption gives it a flat, matte body
CORK = dict(absorb=(0.0225, 0.0430, 0.0790), line=(0.42, 0.33, 0.22),
            min_thick=6.0, max_thick=8.5, kAmt=0.50, kPow=1.9, spec=0.16)

def _font_path():
    """Arial Bold on the workstation, DejaVu on a Linux runner."""
    for c in ("C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
        if os.path.exists(c):
            return c
    raise RuntimeError("no bold sans font found - install DejaVu or Liberation")


FONT = _font_path()


def _tracked_text(d, xy, text, font, fill, track):
    """Letterspaced text - the Boutiq mark is set wide."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track
    return x - track


def _tracked_width(d, text, font, track):
    return sum(d.textlength(ch, font=font) for ch in text) + track * (len(text) - 1)


def draw_boutiq(d, x, cy, h, ink):
    """The Boutiq mark: letterspaced BOUTIQ knocked out of a framed badge.
    Drawn at the supplied height, never stretched - width follows from the type."""
    stroke = max(int(h * 0.085), 3)
    pad_x, pad_y = h * 0.34, h * 0.30
    f = ImageFont.truetype(FONT, int(h * 0.62))
    track = h * 0.14
    tw = _tracked_width(d, "BOUTIQ", f, track)
    w = tw + 2 * pad_x
    box = [x, cy - h / 2, x + w, cy + h / 2]
    d.rounded_rectangle(box, radius=int(h * 0.16), outline=ink + (255,), width=stroke)
    _tracked_text(d, (x + pad_x, cy - h * 0.62 * 0.66), "BOUTIQ", f, ink + (255,), track)
    return w


def make_label(text, fill, ink, w=2400, h=420, pad=0.13):
    """Enamel label: solid colour band, JBD x Boutiq dropped out in white.
    u runs up the stem, v across the face; mirrored in v so it reads correctly
    on the camera side of the tube."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = int(h * pad)
    band_h = h - 2 * m
    d.rounded_rectangle([0, m, w - 1, h - m - 1], radius=int(band_h * 0.30),
                        fill=fill + (255,))
    cy = h / 2
    size = int(band_h * 0.46)
    f = ImageFont.truetype(FONT, size)
    gap = size * 0.55
    jbd_w = d.textlength("JBD", font=f)
    x_w = d.textlength("×", font=f)
    badge_h = band_h * 0.60
    # measure the badge before laying anything down, so the lockup centres properly
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    fb = ImageFont.truetype(FONT, int(badge_h * 0.62))
    badge_w = _tracked_width(probe, "BOUTIQ", fb, badge_h * 0.14) + 2 * (badge_h * 0.34)
    total = jbd_w + gap + x_w + gap + badge_w
    if total > w * 0.88:
        k = w * 0.88 / total
        size = int(size * k); badge_h *= k; gap *= k
        f = ImageFont.truetype(FONT, size)
        fb = ImageFont.truetype(FONT, int(badge_h * 0.62))
        jbd_w = d.textlength("JBD", font=f); x_w = d.textlength("×", font=f)
        badge_w = _tracked_width(probe, "BOUTIQ", fb, badge_h * 0.14) + 2 * (badge_h * 0.34)
        total = jbd_w + gap + x_w + gap + badge_w
    x = (w - total) / 2
    d.text((x, cy - size * 0.62), "JBD", font=f, fill=ink + (255,))
    x += jbd_w + gap
    d.text((x, cy - size * 0.62), "×", font=f, fill=ink + (255,))
    x += x_w + gap
    draw_boutiq(d, x, cy, badge_h, ink)
    return img.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)


def build_renderer(piece, key, W, H):
    p, c = PIECES[piece], WAYS[key]
    r = render.Renderer(W, H)
    r.add(p["body"], absorb=c["body"], fume=c["fume"],
          fume_stops=c["fume_stops"], fume_pow=c.get("fume_pow", 1.4),
          line=c["line"], kAmt=0.38, kPow=2.6, spec=1.0,
          decal=p["decal"] is not None, solid=True, min_thick=2.2)
    r.add(p["frit"], absorb=c["frit"], fume=0.0, line=c["fline"],
          kAmt=0.22, kPow=2.0, spec=1.25, solid=True, min_thick=3.4, smooth=0.0)
    r.add(p["marbles"], absorb=c.get("marble", MARBLE["absorb"]), fume=0.0,
          line=MARBLE["line"], kAmt=0.70, kPow=3.0, spec=1.60, smooth=60.0,
          solid="marble" in c, min_thick=2.0 if "marble" in c else 0.0)
    which = c.get("lines")
    lines = p.get("lines_%s" % which) if which else None
    if lines:
        clear = which == "frit"          # clear lines laid over a coloured, fritted body
        r.add(lines, absorb=c.get("wrap", (0.30, 0.085, 0.12)), fume=0.0,
              line=(0.10, 0.12, 0.14) if clear else c["fline"],
              kAmt=0.62 if clear else 0.30, kPow=2.6 if clear else 2.0,
              spec=1.55 if clear else 1.05,
              solid=not clear, min_thick=0.0 if clear else 5.5,
              max_thick=60.0 if clear else 7.0, smooth=24.0)
    if p.get("cork"):
        r.add(p["cork"], absorb=CORK["absorb"], fume=0.0, line=CORK["line"],
              kAmt=CORK["kAmt"], kPow=CORK["kPow"], spec=CORK["spec"],
              solid=True, min_thick=CORK["min_thick"], max_thick=CORK["max_thick"],
              smooth=24.0)
    if p["decal"]:
        z0, z1, rad = p["decal"]
        r.set_decal(make_label(TEXT, c["label"], c["label_text"]), z0, z1, rad)
    return r


def frame(r, piece, angle, tilt=None):
    """tilt=None uses the piece's own orientation. Pass a tilt in degrees to sweep
    between standing (0) and laid down (-90): the camera pulls back and the piece
    slides across so it stays framed the whole way."""
    p = PIECES[piece]
    if tilt is None:
        return r.frame(angle, cam_r=p["cam_r"], target=p["target"], fov=p["fov"],
                       shadow=p["shadow"], tilt=p.get("tilt", 0.0), shift=p.get("shift"))
    t = abs(tilt) / 90.0                      # 0 standing, 1 flat on its side
    cam_r = 545.0 - 150.0 * t
    target = (0, 0, 74.0 - 64.0 * t)
    shift = (70.0 * t, 0.0, 8.0 * t)
    shadow = (0.5, 0.30 + 0.16 * t, 0.055 + 0.045 * t)
    return r.frame(angle, cam_r=cam_r, target=target, fov=p["fov"],
                   shadow=shadow, tilt=tilt, shift=shift)


def size_of(piece, W=None, H=None):
    """Portrait for a standing piece, landscape for one on its side."""
    if W and H:
        return W, H
    return PIECES[piece].get("size", (760, 1000))


def shot(piece, key, angle=SIDE, W=None, H=None, tag=""):
    os.makedirs(OUT, exist_ok=True)
    W, H = size_of(piece, W, H)
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
