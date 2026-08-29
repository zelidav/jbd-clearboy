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
import math, os, sys
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
 "holder": dict(
     body="out/holder.stl", marbles="out/holder_marbles.stl",
     spin=["out/holder_spin0.stl", "out/holder_spin1.stl", "out/holder_spin2.stl"],
     bling="out/holder_bling.stl", bling2="out/holder_bling2.stl",
     cam_r=204.0, target=(0, 0, 0), fov=17.0, shadow=(0.5, 0.40, 0.06),
     tilt=-90.0, shift=(46.0, 0.0, 0.0), size=(1200, 520), decal=None,
     name="Joint holder", note="90 mm - the bell grips any joint"),
 "tip": dict(
     body="out/tip.stl",
     cam_r=104.0, target=(0, 0, 0), fov=17.0, shadow=(0.5, 0.36, 0.08),
     tilt=-90.0, shift=(9.5, 0.0, 0.0), size=(1100, 620), decal=None,
     name="Glass tip", note="19 mm - screen inside, paper slot outside"),
 "tip_spiral": dict(
     body="out/tip_spiral.stl",
     cam_r=104.0, target=(0, 0, 0), fov=17.0, shadow=(0.5, 0.36, 0.08),
     tilt=-90.0, shift=(9.5, 0.0, 0.0), size=(1100, 620), decal=None,
     name="Glass tip, coil", note="19 mm - wound open end to end"),
 "tip_cut": dict(
     body="out/tip_cut.stl",
     cam_r=104.0, target=(0, 0, 0), fov=17.0, shadow=(0.5, 0.36, 0.08),
     tilt=-90.0, shift=(9.5, 0.0, 0.0), size=(1100, 620), decal=None,
     name="Glass tip, section", note="cut at mid length"),
 "tip_spiral_cut": dict(
     body="out/tip_spiral_cut.stl",
     cam_r=104.0, target=(0, 0, 0), fov=17.0, shadow=(0.5, 0.36, 0.08),
     tilt=-90.0, shift=(9.5, 0.0, 0.0), size=(1100, 620), decal=None,
     name="Rolled sheet, section", note="cut at mid length"),
 "pose135": dict(
     body="out/v-pose135.stl", frit="out/v-pose135_frit.stl",
     marbles="out/v-pose135_marbles.stl",
     lines_body="out/v-pose135_lines.stl", lines_frit="out/v-pose135_lines.stl",
     # posed, the piece hangs between Z 79 and 160 and off to +X, so it frames itself
     fit=True, fov=17.0, decal=None, size=(1200, 820),
     name="Hammer, posed", note="Angle 1 135 / Angle 3 30"),
 "lighter": dict(
     body="out/lighter.stl",
     wig=("out/lighter_wig_a.stl", "out/lighter_wig_b.stl"),
     fit=True, fov=17.0, decal=None, size=(820, 900),
     name="Lighter sleeve", note="58 mm · an obround socket, a standard lighter drops in"),
 "lighter_loaded": dict(
     body="out/lighter.stl",
     wig=("out/lighter_wig_a.stl", "out/lighter_wig_b.stl"),
     parts=[("out/lighter_body.stl", "plastic"), ("out/lighter_hood.stl", "metal"),
            ("out/lighter_wheel.stl", "steel")],
     fit=True, fov=17.0, decal=None, size=(760, 1020),
     name="Lighter sleeve, loaded", note="26 mm stands proud - it is struck in the sleeve"),
 "tube": dict(
     body="out/tube.stl", cork="out/tube_cork.stl",
     drips=("out/tube_drips_a.stl", "out/tube_drips_b.stl"),
     wig=("out/tube_wig_a.stl", "out/tube_wig_b.stl"),
     label="puff", decal=(34.0, 95.0, 11.0),
     stamp=(44.0, 68.0, 11.6), stamp_face=-1.0,
     fit=True, fov=17.0, size=(640, 1040),
     name="Joint tube", note="124 mm · one gram, cork-stopped, drips and a wig wag"),
 "tube_loaded": dict(
     body="out/tube.stl", cork="out/tube_cork.stl",
     drips=("out/tube_drips_a.stl", "out/tube_drips_b.stl"),
     wig=("out/tube_wig_a.stl", "out/tube_wig_b.stl"),
     parts=[("out/tube_joint.stl", "paper")],
     label="puff", decal=(34.0, 95.0, 11.0),
     stamp=(44.0, 68.0, 11.6), stamp_face=-1.0,
     fit=True, fov=17.0, size=(640, 1040),
     name="Joint tube, loaded", note="a one-gram cone sealed in glass"),
 "box": dict(
     body="out/tube.stl", cork="out/tube_cork.stl",
     drips=("out/tube_drips_a.stl", "out/tube_drips_b.stl"),
     wig=("out/tube_wig_a.stl", "out/tube_wig_b.stl"),
     # nearest first: the passes depth-test in add order, and multiply. A shell added
     # before the insert it sits behind tints the insert its own colour - which is how
     # a cream insert in a blue box came out blue.
     parts=[("out/tube_joint.stl", "paper"), ("out/box_tissue.stl", "tissue"),
            ("out/box_shell.stl", "board"), ("out/box_lid.stl", "board"),
            ("out/box_magnets.stl", "steel")],
     # the piece arrives wrapped, so what prints in this scene is the seal on the
     # sleeve - the label and the maker's mark are under the tissue
     label="seal", decal=(52.0, 90.0, 18.8), stamp=None,
     # a box only reads open in three-quarter
     yaw=38.0, decal_flip="180", lid_label=True,
     fit=True, fov=17.0, tilt=-90.0, size=(1200, 780),
     name="Presentation box", note="rigid board, hinged lid, magnetic clasp"),
 "jar": dict(
     body="out/jar.stl", frit="out/jar_frit.stl", marbles="out/jar_marbles.stl",
     cork="out/jar_cork.stl", lines_body="out/jar_lines.stl",
     lines_frit="out/jar_lines_frit.stl",
     stamp=(16.0, 44.0, 22.0),      # z0, z1, projector radius
     boutiq=(19.5, 26.5, 13.0),    # the printed sticker, low on the back face
     cam_r=455.0, target=(0, 0, 56), fov=17.0, shadow=(0.5, 0.32, 0.115),
     decal=None,
     name="Nug jar", note="92 mm \u00b7 38 mm opening \u00b7 cork lid"),
}

WAYS = {
 "teal_silver": dict(
     sticker="assets/sticker_blue.png",
     body=(0.0372, 0.0157, 0.0213), frit=(0.175, 0.0797, 0.0908),
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
     sticker="assets/sticker_pink.png",
     body=(0.0251, 0.0548, 0.0414), frit=(0.0797, 0.2122, 0.1446),
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
     sticker="assets/sticker_white.png",
     body=(0.0045, 0.0040, 0.0038), frit=(0.175, 0.0797, 0.0908),
     fume=1.35, fume_pow=0.90,
     fume_stops=((1.00, 1.00, 1.00), (0.88, 0.94, 1.06),
                 (0.92, 0.86, 1.10), (1.08, 0.98, 0.84)),
     line=(0.09, 0.11, 0.14), fline=(0.01, 0.11, 0.12),
     marble=(0.105, 0.047819999999999994, 0.05448), wrap=(0.175, 0.0797, 0.0908),
     lines="body", lines_nofrit="frit", wrapped=True,
     label=(14, 122, 106), label_text=(255, 255, 255),
     name="Clear \u00b7 heavy silver fume",
     sub="teal frit, marbles \u00b7 wrapped linework"),
 "clear_gold": dict(
     sticker="assets/sticker_pink.png",
     body=(0.0045, 0.0040, 0.0038), frit=(0.0797, 0.2122, 0.1446),
     fume=1.35, fume_pow=0.90,
     fume_stops=((1.00, 0.99, 0.95), (1.08, 1.00, 0.82),
                 (1.08, 0.86, 0.82), (0.92, 0.86, 1.08)),
     line=(0.14, 0.10, 0.06), fline=(0.13, 0.01, 0.09),
     marble=(0.047819999999999994, 0.12732, 0.08676), wrap=(0.0797, 0.2122, 0.1446),
     lines="body", lines_nofrit="frit", wrapped=True,
     label=(150, 32, 108), label_text=(255, 255, 255),
     name="Clear \u00b7 heavy gold fume",
     sub="magenta frit, marbles \u00b7 wrapped linework"),

 # The collab way. One piece, one finish - a colourway drawn for Puff rather than one
 # of ours borrowed for them: the cyan-teal that runs through everything they make,
 # silver fumed so it flashes rather than sits flat, with the drips and the wig wag
 # pulled in their purple and their gold. Three colours, all off their own pack art.
 "puff_blue": dict(
     sticker=None,
     # Opaque colour glass, not a tint. Their packaging is solid saturated colour, so
     # the body is pushed until it reads as colour rather than as a window, and the
     # silver fume goes over the top of it - fume on colour is where the flash comes
     # from, and it is the thing a photograph of plastic cannot do.
     body=(0.3050, 0.0560, 0.0335), body_min_thick=5.2, body_max_thick=12.0,
     frit=(0.066, 0.025, 0.256),                    # lime
     wig_cols=((0.097, 0.168, 0.025),               # purple
               (0.020, 0.055, 0.170)),              # gold
     fume=1.55, fume_pow=0.95,
     fume_stops=((1.00, 1.00, 1.00), (0.90, 0.95, 1.06),
                 (0.92, 0.88, 1.10), (1.06, 0.98, 0.86)),
     line=(0.02, 0.11, 0.14), fline=(0.02, 0.10, 0.05),
     wrap=(0.014, 0.077, 0.179),   # orange
     label=(0, 160, 192), label_text=(255, 255, 255),
     lines="frit",
     name="Puff teal \u00b7 silver fume",
     sub="purple and gold drips \u00b7 same at the base"),
}

MARBLE = dict(absorb=(0.004, 0.004, 0.004), line=(0.62, 0.66, 0.70))

# Everything below is not glass. The compositor is a Beer-Lambert tint over a clamped
# thickness, so an opaque body is just a large absorption held between a floor and a
# ceiling: the pair is what sets the colour, and the spec term is what sells the
# material. Absorptions here are solved for a 6-7 mm slab.
OPAQUE = {
 # The shell of a disposable lighter, graphite. It is the same in every colourway on
 # purpose: the lighter is a thing the customer already owns and drops in, so the
 # sleeve is what carries the colour. A shell tinted to match the glass made the two
 # read as one moulded object, which is the opposite of the point.
 "plastic": dict(absorb=(0.262, 0.257, 0.249), line=(0.16, 0.17, 0.19),
                 kAmt=0.44, kPow=1.9, spec=0.62, min_thick=6.5, max_thick=7.4),
 # the pressed hood over the wheel
 "metal": dict(absorb=(0.100, 0.094, 0.085), line=(0.30, 0.32, 0.35),
               kAmt=0.30, kPow=2.2, spec=2.10, min_thick=5.8, max_thick=6.6),
 # the flint wheel itself, darker and harder
 "steel": dict(absorb=(0.285, 0.277, 0.262), line=(0.24, 0.25, 0.27),
               kAmt=0.34, kPow=2.4, spec=0.60, min_thick=2.0, max_thick=2.6),
 # rolling paper: near white, matte, no contour worth speaking of
 # rolling paper: a warm off-white, matte. It is seen THROUGH the tube wall, so it
 # needs enough body and enough edge shading to read as a solid in there rather than
 # as a brighter patch of glass
 # Wrapped rigid board in Puff's blue. It was black, which is the default answer for
 # a presentation box and the wrong one here: the box is a brand surface before it is
 # a container, and it is the first thing seen.
 "board": dict(absorb=(0.4020, 0.0430, 0.0230), line=(0.04, 0.13, 0.17),
               kAmt=0.26, kPow=2.1, spec=0.24, min_thick=5.4, max_thick=6.1),
 # Die-cut board, natural kraft. The insert is the one part of a box like this that
 # usually cannot go in the recycling with the rest of it, so it is board and tissue
 # rather than foam - and kraft against a blue box is the right look anyway.
 "kraft": dict(absorb=(0.0482, 0.0725, 0.1085), line=(0.34, 0.30, 0.24),
               kAmt=0.48, kPow=1.7, spec=0.12, min_thick=7.6, max_thick=8.4),
 # Branded tissue, folded up the sides. Kept light and close to neutral: blue glass
 # absorbs red, so anything warm or dark behind it takes the piece down with it.
 "tissue": dict(absorb=(0.0070, 0.0092, 0.0140), line=(0.46, 0.42, 0.44),
                kAmt=0.30, kPow=1.9, spec=0.09, min_thick=4.6, max_thick=5.2),
 "paper": dict(absorb=(0.0396, 0.0490, 0.0793), line=(0.34, 0.32, 0.28),
               kAmt=0.70, kPow=1.30, spec=0.26, min_thick=3.4, max_thick=4.2),
}
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


def make_stamp_decal(w=1400, h=900, size=0.62):
    """The JB mark as a hazy patch in the surface rather than a drawn outline: a
    sandblasted-looking bloom with a soft shadow under it, so it sits in the glass
    with some depth instead of floating on top."""
    import stamp_art
    from PIL import ImageFilter
    def poly(p):
        return [(w * (0.5 + q[1] * size * (h / float(w)) * 1.9),
                 h * (0.5 - q[0] * size)) for q in p]

    fill = Image.new("L", (w, h), 0)
    fd = ImageDraw.Draw(fill)
    line = Image.new("L", (w, h), 0)
    ld = ImageDraw.Draw(line)
    for sh in stamp_art.load():
        if len(sh["outer"]) > 2:
            fd.polygon(poly(sh["outer"]), fill=255)
        for k in sh["holes"]:
            if len(k) > 2:
                fd.polygon(poly(k), fill=0)
        for ring in [sh["outer"]] + sh["holes"]:
            if len(ring) > 2:
                pts = poly(ring)
                ld.line(pts + [pts[0]], fill=255, width=max(int(h * 0.012), 4))

    haze = fill.filter(ImageFilter.GaussianBlur(h * 0.020))
    edge = line.filter(ImageFilter.GaussianBlur(h * 0.006))
    shade = fill.filter(ImageFilter.GaussianBlur(h * 0.030))

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # a soft dark bed, offset down, reads as depth in the wall
    img.paste(Image.new("RGBA", (w, h), (24, 30, 34, 255)),
              (0, int(h * 0.012)), shade.point(lambda v: int(v * 0.30)))
    # the frosted face of the mark
    img.paste(Image.new("RGBA", (w, h), (236, 242, 246, 255)), (0, 0),
              haze.point(lambda v: int(v * 0.34)))
    # just enough edge to keep it legible
    img.paste(Image.new("RGBA", (w, h), (54, 62, 68, 255)), (0, 0),
              edge.point(lambda v: int(v * 0.42)))
    return img.transpose(Image.FLIP_TOP_BOTTOM)


def load_sticker(path):
    """The printed sticker art, oriented for the stem projector."""
    im = Image.open(path).convert("RGBA")
    return im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)


def make_jar_sticker(path):
    """The same printed sticker the pipes carry, turned to read round the jar."""
    im = Image.open(path).convert("RGBA").rotate(90, expand=True)
    return im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT)


# ------------------------------------------------------- the Puff collab label
# Puff's colours, sampled properly this time - across ten pieces of their pack and
# collection art rather than off one product photo. The backbone is a cyan-teal, not a
# sky blue, and the range rotates green, purple, orange, red and gold by strain. An
# earlier pass here read the hot pink off their drip mark and made the whole thing look
# like somebody else's collab; the pink is one mark, not the system.
PUFF = dict(blue=(0, 160, 192),          # #00A0C0 - the most-used colour they own
            navy=(10, 35, 82),           # the deep end of the same family
            gold=(208, 160, 16),         # #D0A010
            purple=(96, 80, 192),        # #6050C0
            green=(14, 158, 90),
            orange=(224, 128, 80),
            pink=(232, 80, 144),         # kept for their drip mark only
            ink=(11, 13, 16), paper=(255, 255, 255))

MARK = os.path.join("assets", "puff_mark.png")
_MARK = {}


def puff_mark(h, colour=(255, 255, 255)):
    """Their wordmark, as supplied, at the height asked for.

    Set rather than drawn was always a compromise - PUFF is a display face with
    pill-shaped terminals and no font matches it. This is their own file, scaled by
    height and never stretched, recoloured through its own alpha so it can sit on a
    coloured ground. It already carries 'pre-rolls' and the registered mark, so the
    lockup is their artwork plus our name, not two typesettings.
    """
    key = (int(h), colour)
    if key not in _MARK:
        src = Image.open(MARK).convert("RGBA")
        w = max(int(round(src.width * float(h) / src.height)), 1)
        src = src.resize((w, max(int(h), 1)), Image.LANCZOS)
        solid = Image.new("RGBA", src.size, tuple(colour) + (255,))
        solid.putalpha(src.getchannel("A"))
        _MARK[key] = solid
    return _MARK[key]


BRAND_FONTS = {"heavy": "assets/fonts/Poppins-ExtraBold.ttf",
               "bold": "assets/fonts/Poppins-Bold.ttf",
               "med": "assets/fonts/Poppins-Medium.ttf",
               "round": "assets/fonts/VarelaRound-Regular.ttf"}
_BF = {}


def brand_font(kind, size):
    k = (kind, int(size))
    if k not in _BF:
        _BF[k] = ImageFont.truetype(BRAND_FONTS[kind], int(size))
    return _BF[k]


def _pill(d, xy, text, font, fill, ink, pad, track=0.0):
    """A small filled pill with letterspaced type in it - where the plain facts go."""
    x, y = xy
    tw = _tracked_width(d, text, font, track)
    bb = font.getbbox(text)
    hh = (bb[3] - bb[1]) + 2 * pad
    d.rounded_rectangle([x, y - hh / 2, x + tw + 2 * pad * 1.6, y + hh / 2],
                        radius=hh / 2, fill=fill + (255,))
    _tracked_text(d, (x + pad * 1.6, y - hh / 2 + pad - bb[1]), text, font,
                  ink + (255,), track)
    return tw + 2 * pad * 1.6


def make_puff_label(w=2600, h=915):
    """PUFF x JEROME BAKER, printed up the tube.

    Two houses, one lockup: their wordmark set in the geometric rounded face their own
    is drawn in, ours in the same family a weight down, and the cross in the gold off
    their grill. Under it, the plain facts in a pill in the pink of their drip mark.

    The lockup gets the full width of the band and is shrunk until it fits it - nothing
    here is set at one size and hoped for. This art is projected onto a curved wall at
    58 mm long, so anything that overruns crashes into the edge of the piece.

    The band is inset from the projector so glass shows past it, and it sits between the
    wig wag and the drips rather than over either. Final artwork is Puff's to approve;
    this is the lockup at the right size, in the right colours, in the right place.
    """
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # the band is inset from the projector on both axes: pushed to the edge, the
    # art wraps round the shoulder of the tube and the ends go out of sight
    m = int(h * 0.115)
    band = [int(w * 0.035), m, int(w * 0.965), h - m]
    bw, bh = band[2] - band[0], band[3] - band[1]
    cy = (band[1] + band[3]) / 2
    d.rounded_rectangle(band, radius=int(min(bh, bw) * 0.30),
                        fill=PUFF["blue"] + (255,))
    k = int(h * 0.045)
    d.rounded_rectangle([band[0] + k, band[1] + k, band[2] - k, band[3] - k],
                        radius=int(min(bh, bw) * 0.25), outline=PUFF["gold"] + (255,),
                        width=max(int(h * 0.013), 3))

    # type is sized off the band's short side, so a long thin band and a stubby one set
    # at the same optical weight
    u = min(bh, bw * 0.40)
    room = bw * 0.80

    scale = 1.0
    for _ in range(9):
        big = brand_font("heavy", max(int(u * 0.34 * scale), 8))
        sub = brand_font("round", max(int(u * 0.125 * scale), 6))
        ours = brand_font("bold", max(int(u * 0.215 * scale), 7))
        tiny = brand_font("med", max(int(u * 0.105 * scale), 6))
        cross = brand_font("heavy", max(int(u * 0.27 * scale), 7))
        puff_w = d.textlength("PUFF", font=big)
        pre_w = _tracked_width(d, "pre-rolls", sub, u * 0.024 * scale)
        jb_w = d.textlength("JEROME BAKER", font=ours)
        des_w = _tracked_width(d, "DESIGNS", tiny, u * 0.060 * scale)
        left_w, right_w = max(puff_w, pre_w), max(jb_w, des_w)
        x_w = d.textlength("\u00d7", font=cross)
        gap = u * 0.26 * scale
        total = left_w + gap + x_w + gap + right_w
        if total <= room:
            break
        scale *= room / total

    top = cy - u * 0.14
    x = (band[0] + band[2] - total) / 2
    d.text((x + (left_w - puff_w) / 2, top - u * 0.30 * scale), "PUFF", font=big,
           fill=PUFF["paper"] + (255,))
    _tracked_text(d, (x + (left_w - pre_w) / 2, top + u * 0.09 * scale), "pre-rolls",
                  sub, PUFF["paper"] + (255,), u * 0.024 * scale)
    x += left_w + gap
    d.text((x, top - u * 0.18 * scale), "\u00d7", font=cross,
           fill=PUFF["gold"] + (255,))
    x += x_w + gap
    d.text((x + (right_w - jb_w) / 2, top - u * 0.22 * scale), "JEROME BAKER",
           font=ours, fill=PUFF["paper"] + (255,))
    _tracked_text(d, (x + (right_w - des_w) / 2, top + u * 0.09 * scale), "DESIGNS",
                  tiny, PUFF["paper"] + (255,), u * 0.060 * scale)

    # the plain facts, in one pill under the lockup
    fact = "1 GRAM  \u00b7  HAND BLOWN GLASS"
    fs = max(int(u * 0.095), 7)
    fpad, ftrack = u * 0.062, u * 0.030
    ff = brand_font("bold", fs)
    fw = _tracked_width(d, fact, ff, ftrack) + 2 * fpad * 1.6
    _pill(d, ((band[0] + band[2] - fw) / 2, cy + u * 0.335), fact, ff, PUFF["orange"],
          PUFF["paper"], fpad, ftrack)

    # No flip. The projector's u already runs the way the piece does - up the tube -
    # and its v the way the art does, so a label that reads left to right on the sheet
    # reads bottom to top on the glass. The stem label flips because the piece it is
    # printed on is held the other way up.
    return img


_ART = {}


def _art(fn):
    """Artwork built once. The composites run per frame now, and regenerating a
    2400 px plate seventy-two times a turntable is pure waste."""
    if fn.__name__ not in _ART:
        _ART[fn.__name__] = fn()
    return _ART[fn.__name__]


def _flip(art, mode):
    """Laying the assembly down with a camera tilt reverses the handedness of the
    projected face, so a print that reads correctly on a standing piece comes out
    mirrored. The art is flipped for that view rather than the piece re-modelled."""
    if not mode:
        return art
    if mode in ("lr", "180"):
        art = art.transpose(Image.FLIP_LEFT_RIGHT)
    if mode in ("tb", "180"):
        art = art.transpose(Image.FLIP_TOP_BOTTOM)
    return art


def make_box_label(w=2200, h=980):
    """The collab lockup for the inside of the lid, drawn to sit on the board itself.

    No panel behind it: on a blue box the mark reads as foil stamped into the board,
    which is what this would actually be. White and gold only - the pink is already
    doing work on the glass and a third colour up here would fight it."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2.0, h / 2.0
    room = w * 0.86

    # the lockup is measured and shrunk until it fits the plate. The first version of
    # this was set at a fixed size and ran off both ends of the lid - PUFF lost its P
    # and JEROME BAKER lost its ER, which is not a thing to hand a partner
    scale = 1.0
    for _ in range(9):
        u = h * scale
        big = brand_font("heavy", max(int(u * 0.30), 8))
        sub = brand_font("round", max(int(u * 0.105), 6))
        ours = brand_font("bold", max(int(u * 0.185), 7))
        tiny = brand_font("med", max(int(u * 0.085), 6))
        cross = brand_font("heavy", max(int(u * 0.23), 7))
        puff_w = d.textlength("PUFF", font=big)
        pre_w = _tracked_width(d, "pre-rolls", sub, u * 0.020)
        jb_w = d.textlength("JEROME BAKER", font=ours)
        des_w = _tracked_width(d, "DESIGNS", tiny, u * 0.050)
        left_w, right_w = max(puff_w, pre_w), max(jb_w, des_w)
        x_w = d.textlength("×", font=cross)
        gap = u * 0.20
        total = left_w + gap + x_w + gap + right_w
        if total <= room:
            break
        scale *= room / total

    x = cx - total / 2
    top = cy - u * 0.10
    d.text((x + (left_w - puff_w) / 2, top - u * 0.27), "PUFF", font=big,
           fill=PUFF["paper"] + (255,))
    _tracked_text(d, (x + (left_w - pre_w) / 2, top + u * 0.07), "pre-rolls", sub,
                  PUFF["paper"] + (255,), u * 0.020)
    x += left_w + gap
    d.text((x, top - u * 0.16), "×", font=cross, fill=PUFF["gold"] + (255,))
    x += x_w + gap
    d.text((x + (right_w - jb_w) / 2, top - u * 0.19), "JEROME BAKER", font=ours,
           fill=PUFF["paper"] + (255,))
    _tracked_text(d, (x + (right_w - des_w) / 2, top + u * 0.07), "DESIGNS", tiny,
                  PUFF["paper"] + (255,), u * 0.050)

    # a gold hairline and the occasion under it
    rw = total * 0.86
    d.rectangle([cx - rw / 2, cy + u * 0.245, cx + rw / 2, cy + u * 0.253],
                fill=PUFF["gold"] + (255,))
    line = "HOLIDAY COLLAB  ·  HAND BLOWN GLASS"
    ls = u * 0.070
    for _ in range(7):
        lf = brand_font("bold", max(int(ls), 6))
        lw = _tracked_width(d, line, lf, ls * 0.43)
        if lw <= room:
            break
        ls *= room / lw
    _tracked_text(d, (cx - lw / 2, cy + u * 0.300), line, lf,
                  PUFF["paper"] + (255,), ls * 0.43)
    return img


def _persp_coeffs(dst, src):
    """Solve the eight coefficients PIL wants for a perspective warp.

    PIL maps OUTPUT pixels back to INPUT, so the system is written that way round:
    give it where each corner of the artwork lands on the canvas and it returns the
    inverse map."""
    import numpy as np
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return tuple(np.linalg.solve(np.array(A, "f8"), np.array(B, "f8")))


def make_seal(w=1267, h=1000):
    """The sticker that closes the tissue. Round, their mark, nothing else.

    Transparent outside the disc, because it is projected onto the sleeve and the
    tissue has to show round it."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2.0, h / 2.0
    rr = min(w, h) * 0.30
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=PUFF["blue"] + (255,))
    k = rr * 0.10
    d.ellipse([cx - rr + k, cy - rr + k, cx + rr - k, cy + rr - k],
              outline=PUFF["gold"] + (255,), width=max(int(rr * 0.045), 3))

    u = rr
    scale = 1.0
    for _ in range(9):
        mark = puff_mark(max(u * 0.42 * scale, 6), PUFF["paper"])
        ours = brand_font("bold", max(int(u * 0.155 * scale), 6))
        if mark.width <= rr * 1.15 and d.textlength("JEROME BAKER",
                                                    font=ours) <= rr * 1.30:
            break
        scale *= 0.9
    img.paste(mark, (int(cx - mark.width / 2), int(cy - u * 0.46)), mark)
    jb = "JEROME BAKER"
    jw = d.textlength(jb, font=ours)
    d.text((cx - jw / 2, cy + u * 0.06), jb, font=ours, fill=PUFF["paper"] + (255,))
    f, lw, tr = _fit_track(d, "HOLIDAY COLLAB", "bold", u * 0.115, rr * 1.30, 0.30)
    _tracked_text(d, (cx - lw / 2, cy + u * 0.34), "HOLIDAY COLLAB", f,
                  PUFF["gold"] + (255,), tr)
    return img


def _fit_track(d, text, kind, size, max_w, track=0.0):
    for _ in range(9):
        f = brand_font(kind, max(int(size), 5))
        w = _tracked_width(d, text, f, size * track)
        if w <= max_w:
            return f, w, size * track
        size *= max_w / w
    return f, w, size * track


def make_box_wrap(w=2400, h=740):
    """The print on the outside of the box, in the sticker's own system.

    Same furniture as the label on the glass - gold keyline, the lockup, the plain
    facts in a pink pill - with the blue field left off, because the board is already
    the blue field. Anything else would be a blue sticker on a blue box."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = int(h * 0.10)
    frame = [int(w * 0.020), m, int(w * 0.980), h - m]
    fw, fh = frame[2] - frame[0], frame[3] - frame[1]
    cx, cy = (frame[0] + frame[2]) / 2.0, (frame[1] + frame[3]) / 2.0
    d.rounded_rectangle(frame, radius=int(min(fh, fw) * 0.26),
                        outline=PUFF["gold"] + (255,), width=max(int(h * 0.016), 3))

    u = min(fh, fw * 0.34)
    room = fw * 0.80
    scale = 1.0
    for _ in range(9):
        mark = puff_mark(max(u * 0.52 * scale, 6), PUFF["paper"])
        ours = brand_font("bold", max(int(u * 0.215 * scale), 7))
        tiny = brand_font("med", max(int(u * 0.105 * scale), 6))
        cross = brand_font("heavy", max(int(u * 0.27 * scale), 7))
        jb_w = d.textlength("JEROME BAKER", font=ours)
        des_w = _tracked_width(d, "DESIGNS", tiny, u * 0.060 * scale)
        left_w, right_w = mark.width, max(jb_w, des_w)
        x_w = d.textlength("\u00d7", font=cross)
        gap = u * 0.26 * scale
        total = left_w + gap + x_w + gap + right_w
        if total <= room:
            break
        scale *= room / total

    top = cy - u * 0.16
    x = cx - total / 2
    img.paste(mark, (int(x), int(cy - u * 0.06 - mark.height / 2)), mark)
    x += left_w + gap
    d.text((x, top - u * 0.18 * scale), "\u00d7", font=cross,
           fill=PUFF["gold"] + (255,))
    x += x_w + gap
    d.text((x + (right_w - jb_w) / 2, top - u * 0.22 * scale), "JEROME BAKER",
           font=ours, fill=PUFF["paper"] + (255,))
    _tracked_text(d, (x + (right_w - des_w) / 2, top + u * 0.09 * scale), "DESIGNS",
                  tiny, PUFF["paper"] + (255,), u * 0.060 * scale)

    fact = "HOLIDAY COLLAB  \u00b7  1 GRAM  \u00b7  HAND BLOWN GLASS"
    fs = max(int(u * 0.095), 7)
    fpad, ftrack = u * 0.062, u * 0.030
    ff = brand_font("bold", fs)
    fwid = _tracked_width(d, fact, ff, ftrack) + 2 * fpad * 1.6
    _pill(d, (cx - fwid / 2, cy + u * 0.335), fact, ff, PUFF["orange"], PUFF["paper"],
          fpad, ftrack)
    return img


def _warp_onto(im, art, px):
    """Warp artwork onto four projected corners, un-mirroring it if the face is being
    seen the other way round.

    A quad given top-left first reads correctly only when its projected winding comes
    out positive in image coordinates; when it does not, the panel is being viewed from
    the side that flips it, and swapping the two pairs of corners is the fix. Doing it
    from the winding rather than by eye means the print stays right if the camera moves.
    """
    import numpy as np
    q = [tuple(v) for v in px]
    x = np.array([v[0] for v in q]); y = np.array([v[1] for v in q])
    area = 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))
    if area < 0:
        q = [q[1], q[0], q[3], q[2]]
    src = [(0, 0), (art.width, 0), (art.width, art.height), (0, art.height)]
    warped = art.transform(im.size, Image.PERSPECTIVE, _persp_coeffs(q, src),
                           Image.BICUBIC)
    im = im.convert("RGB")
    im.paste(warped, (0, 0), warped)
    return im


def place_box_wrap(im, r, angle, kw, art=None):
    """Print the outside of the box on whichever panel the shot is actually showing."""
    import numpy as np
    import box as boxmod
    art = make_box_wrap() if art is None else art
    eye, model, _, _ = r._mats(angle, kw["cam_r"], kw.get("elev", 5.0), kw["target"],
                               kw["fov"], kw.get("tilt", 0.0), kw.get("shift"))
    faces = boxmod.outer_faces()
    best, best_area, best_px = None, 0.0, None
    for name, corners in faces.items():
        n = np.asarray(boxmod.face_normal(name), "f8")
        c = np.asarray(corners, "f8").mean(axis=0)
        wn = model[:3, :3] @ n
        wc = model[:3, :3] @ c + model[:3, 3]
        if float(np.dot(wn, np.asarray(eye, "f8") - wc)) <= 0:
            continue                      # facing away - nothing to print on
        px = r.project(np.asarray(corners, "f8"), angle=angle,
                       **{k: v for k, v in kw.items() if k != "shadow"})
        x, y = px[:, 0], px[:, 1]
        a = abs(0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)))
        if a > best_area:
            best, best_area, best_px = name, a, px
    if best is None:
        return im
    return _warp_onto(im, art, best_px)


def place_lid_label(im, r, angle, kw, art=None):
    """Warp the collab lockup onto the inside of the lid, where the lid actually is."""
    import numpy as np
    import box as boxmod
    art = make_box_label() if art is None else art
    quad = np.asarray(boxmod.lid_label_quad(), "f8")
    px = r.project(quad, angle=angle, **{k: v for k, v in kw.items()
                                         if k != "shadow"})
    return _warp_onto(im, art, px)


def build_renderer(piece, key, W, H, decal_turn=0, frit=True):
    """decal_turn=180 prints the stem label the other way along the stem, for a piece
    laid in a case with its head at the other end.

    frit=False leaves the rolled grain off - a smooth fumed body, marbles and linework
    only. The frit mesh is the only layer dropped; nothing else moves."""
    p, c = PIECES[piece], WAYS[key]
    r = render.Renderer(W, H)
    # Whatever is in the shot that is not glass goes down FIRST - a lighter in its
    # sleeve, a joint in its tube. Every pass depth-tests in the order things were
    # added, so a solid added after the shell it sits inside is written off behind the
    # shell's own front face and never appears. Added first, it lays down its depth,
    # the glass in front of it passes, and the tint multiplies over it - which is the
    # right answer anyway: it is being seen through the wall.
    for path, mat in p.get("parts") or ():
        if not os.path.exists(path):
            continue
        m = OPAQUE[mat]
        r.add(path,
              absorb=(c.get("plastic") if mat == "plastic" else None) or m["absorb"],
              fume=0.0, line=m["line"], kAmt=m["kAmt"], kPow=m["kPow"], spec=m["spec"],
              solid=True, opaque=True, decal=(mat == "tissue"),
              min_thick=m["min_thick"], max_thick=m["max_thick"],
              smooth=36.0, role="opaque")
    r.add(p["body"], absorb=c["body"], fume=c["fume"],
          fume_stops=c["fume_stops"], fume_pow=c.get("fume_pow", 1.4),
          line=c["line"], kAmt=0.38, kPow=2.6, spec=1.0,
          decal=(p["decal"] is not None) or (p.get("stamp") is not None),
          solid=True, min_thick=c.get("body_min_thick", 2.2),
          max_thick=c.get("body_max_thick", 60.0), role="body")
    # the holder wears spun linework instead, so frit is optional now
    if p.get("frit") and frit:
        r.add(p["frit"], absorb=c["frit"], fume=0.0, line=c["fline"],
              kAmt=0.22, kPow=2.0, spec=1.25, solid=True, min_thick=3.4, smooth=0.0,
              role="frit")
    # a clear marble has to catch light to be seen at all, while a tinted one only
    # needs a whisper - too much and the far side rings through the body
    tinted = "marble" in c
    if p.get("marbles"):
        r.add(p["marbles"], absorb=c.get("marble", MARBLE["absorb"]), fume=0.0,
              line=(0.52, 0.56, 0.60) if not tinted else MARBLE["line"],
              kAmt=0.10 if tinted else 0.26, kPow=5.0 if tinted else 3.8,
              spec=1.30 if tinted else 1.85, smooth=60.0, lens=0.055,
              solid=tinted, min_thick=0.8 if tinted else 0.0, role="marbles")
    # two separate decisions that used to be one switch: which mesh the lines are spun
    # on, and what the lines are made of. The clear builds wrap coloured linework and
    # the fumed builds lay clear lines - that does not change when the frit comes off,
    # but the coverage does. Without a frit band to sit against, the jar's full-height
    # spiral is the only thing on the glass and reads as far too much work, so the
    # no-frit builds spin the same short band the fumed ones wear.
    which = c.get("lines")
    if not frit and c.get("lines_nofrit"):
        which = c["lines_nofrit"]
    lines = p.get("lines_%s" % which) if which else None
    if lines:
        clear = not c.get("wrapped", False)
        r.add(lines, absorb=c.get("wrap", (0.30, 0.085, 0.12)), fume=0.0,
              line=(0.10, 0.12, 0.14) if clear else c["fline"],
              kAmt=0.62 if clear else 0.30, kPow=2.6 if clear else 2.0,
              spec=1.55 if clear else 1.05,
              solid=not clear, min_thick=0.0 if clear else 5.5,
              max_thick=60.0 if clear else 7.0, smooth=24.0, role="lines")
    for i, sp in enumerate(p.get("spin") or []):
        if os.path.exists(sp):
            cols = c.get("spin_cols") or [c["body"]]
            r.add(sp, absorb=cols[i % len(cols)], fume=0.0,
                  line=(0.10, 0.12, 0.14), kAmt=0.55, kPow=2.6, spec=1.5,
                  solid=True, min_thick=1.6, max_thick=30.0, smooth=24.0,
                  role="lines")
    # Drips and wig wag are the same two colours, alternating - one pair of courses at
    # the rim and one at the base, so the piece reads as one decision rather than two.
    # Both take the linework role: they stand on the surface and have to pass behind
    # anything set proud of it.
    # drips and wig wag take a pair of colours each. They used to share one pair,
    # which is fine on a two-colour brand and wrong on one that runs four at once.
    pairs = ((p.get("drips"), (c["frit"], c.get("wrap", c["frit"]))),
             (p.get("wig"), c.get("wig_cols") or (c["frit"], c.get("wrap", c["frit"]))))
    for meshes, cols in pairs:
        for i, m in enumerate(meshes or ()):
            if not os.path.exists(m):
                continue
            r.add(m, absorb=cols[i % len(cols)],
                  fume=0.0, line=c["fline"] if i == 0 else c["line"],
                  kAmt=0.36, kPow=2.05, spec=1.32, solid=True,
                  min_thick=1.4, max_thick=9.0, smooth=24.0, role="lines")
    for tag, mat in (("bling", "stone"), ("bling2", "stone2")):
        q = p.get(tag)
        if q and os.path.exists(q):
            r.add(q, absorb=c.get(mat, (0.0022, 0.0020, 0.0026)), fume=0.0,
                  line=c.get(mat + "_line", (0.72, 0.76, 0.82)),
                  kAmt=0.09, kPow=6.5, spec=2.8, smooth=0.0, lens=0.03,
                  solid=False, min_thick=0.0, role="bling")
    if p.get("cork"):
        r.add(p["cork"], absorb=CORK["absorb"], fume=0.0, line=CORK["line"],
              kAmt=CORK["kAmt"], kPow=CORK["kPow"], spec=CORK["spec"],
              solid=True, min_thick=CORK["min_thick"], max_thick=CORK["max_thick"],
              smooth=24.0, role="cork")
    if p["decal"]:
        z0, z1, rad = p["decal"]
        if p.get("label") == "seal":
            art = _art(make_seal)
        elif p.get("label") == "puff":
            art = make_puff_label()
        else:
            art = c.get("sticker")
            art = (load_sticker(art) if art
                   else make_label(TEXT, c["label"], c["label_text"]))
        if decal_turn:
            art = art.rotate(decal_turn, expand=True)
        # Laying the assembly down with a camera tilt reverses the handedness of the
        # projected face, so a print that reads correctly standing comes out mirrored.
        # The art is flipped for that view rather than the piece being re-modelled.
        art = _flip(art, p.get("decal_flip"))
        r.set_decal(art, z0, z1, rad, face=p.get("decal_face", 1.0))
        # a piece can carry both: the print, and the maker's mark under it. The jar
        # only ever wanted one, which is why these used to be the same branch
        if p.get("stamp"):
            s0, s1, srad = p["stamp"]
            # the print and the maker's mark sit on opposite faces of the piece, so
            # neither is read through the other and the tube has two sides worth turning
            mk = _flip(make_stamp_decal(1100, 900), p.get("decal_flip"))
            r.set_decal(mk, s0, s1, srad,
                        face=p.get("stamp_face", p.get("decal_face", 1.0)))
    elif p.get("stamp"):
        z0, z1, rad = p["stamp"]
        r.set_decal(make_stamp_decal(), z0, z1, rad)              # JB mark, front
        if p.get("boutiq"):
            b0, b1, brad = p["boutiq"]
            art = c.get("sticker")
            if art:
                r.set_decal(make_jar_sticker(art), b0, b1, brad, face=-1.0)
    return r


def fit(r, angle=SIDE, fov=17.0, tilt=0.0, shift=None, pad=0.14, elev=5.0):
    """Frame the camera on whatever was actually added, and put the contact shadow
    under it.

    A hand-set cam_r/target/shadow is only right for the geometry it was measured on.
    Pose the piece - swing the head up, rake the stem - and the solid moves off Z 0,
    so the piece drifts in frame and the shadow stays behind on the floor, which is
    what made the raked hammer read as floating. This measures instead.

    Measured broadside, whatever angle is being drawn: these pieces are long in X and
    spin about Z, so SIDE is where they are widest, and one frame for the whole
    turntable is what keeps a spinner from breathing as it turns."""
    import numpy as np
    if r.bbox is None:
        raise RuntimeError("nothing added to the renderer - nothing to frame")
    lo, hi = r.bbox
    corners = np.array([[x, y, z] for x in (lo[0], hi[0])
                        for y in (lo[1], hi[1]) for z in (lo[2], hi[2])], "f8")
    m = render.roty(math.radians(tilt)) @ render.rotz(angle)
    world = (m[:3, :3] @ corners.T).T + m[:3, 3] + np.asarray(shift or (0, 0, 0), "f8")
    cx, cz = world[:, 0].mean(), (world[:, 2].min() + world[:, 2].max()) / 2
    target = (float(cx), 0.0, float(cz))

    W, H = r.W / render.SS, r.H / render.SS
    def spread(cam_r):
        px = r.project(corners, angle=angle, cam_r=cam_r, elev=elev, target=target,
                       fov=fov, tilt=tilt, shift=shift)
        return px, max(np.ptp(px[:, 0]) / W, np.ptp(px[:, 1]) / H)
    # the projected size falls off as 1/cam_r, so one measurement sets the scale and
    # a couple of passes settle the perspective term
    cam_r = max(float(np.linalg.norm(hi - lo)) * 3.0, 60.0)
    for _ in range(6):
        px, got = spread(cam_r)
        cam_r *= got / (1.0 - pad)
    px, _ = spread(cam_r)

    # the pool goes under the part that is actually lowest, not under the centroid -
    # a posed piece rests on one end and the shadow belongs there
    low = int(px[:, 1].argmax())
    bottom = 1.0 - px[low, 1] / H              # uv runs up from the frame floor
    wide = np.ptp(px[:, 0]) / W
    shadow = (float((px[low, 0] * 0.65 + px[:, 0].mean() * 0.35) / W),
              float(min(max(wide * 0.62, 0.12), 0.45)), float(max(bottom, 0.02)))
    return dict(cam_r=float(cam_r), target=target, fov=fov, shadow=shadow,
                tilt=tilt, shift=shift)


def frame(r, piece, angle, tilt=None, want_kw=False):
    """tilt=None uses the piece's own orientation. Pass a tilt in degrees to sweep
    between standing (0) and laid down (-90): the camera pulls back and the piece
    slides across so it stays framed the whole way."""
    p = PIECES[piece]
    if tilt is None:
        if p.get("fit"):                  # posed geometry frames itself - see fit()
            kw = fit(r, SIDE, p["fov"], p.get("tilt", 0.0), p.get("shift"),
                     p.get("pad", 0.14))
            im = r.frame(angle, **kw)
            if p.get("lid_label"):
                im = place_lid_label(im, r, angle, kw, _art(make_box_label))
                # a piece may carry its own sleeve art - that is how the same box
                # is shown with a different strain on it without re-modelling it
                im = place_box_wrap(im, r, angle, kw,
                                    p.get("wrap_art") or _art(make_box_wrap))
            return (im, kw) if want_kw else im
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


def shot(piece, key, angle=None, W=None, H=None, tag="", frit=True):
    os.makedirs(OUT, exist_ok=True)
    if angle is None:
        # a box only reads open in three-quarter; a bottle only reads broadside
        angle = SIDE + math.radians(PIECES[piece].get("yaw", 0.0))
    W, H = size_of(piece, W, H)
    r = build_renderer(piece, key, W, H, frit=frit)
    im = frame(r, piece, angle)
    im.save(f"{OUT}/{piece}_{key}{tag}.png")
    print("wrote", piece, key + tag, im.size)
    return im


if __name__ == "__main__":
    args = sys.argv[1:]
    frit = "nofrit" not in args                  # nofrit -> smooth body, marbles only
    pieces = [a for a in args if a in PIECES] or list(PIECES)
    ways = [a for a in args if a in WAYS] or list(WAYS)
    for pc in pieces:
        for k in ways:
            shot(pc, k, frit=frit)
