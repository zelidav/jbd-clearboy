"""Drop the rendered pieces into the Boutiq box photography, then lay it out as a PDF.

The plates arrive with placeholder glass already sitting in the tray cutouts, so the job
is to seat our own builds into those same recesses - same axis, same length, same end
facing out - and let the real fume and frit replace the rainbow stand-in.

Glass cannot be keyed off a sweep, so the pieces are rendered twice and the plate is
solved rather than masked: with the studio background B, the render is B*T + A, where T
is what the glass transmits and A what it adds. Rendering on black gives A directly;
rendering on white gives B*T + A, and B is the sweep rendered on its own - it carries a
vignette, so it has to be measured, not assumed to be 1. Compositing anywhere is then
scene*T + A, which is exactly what the studio plate does with its own background.

A piece lying flat in the tray, seen from above, is the same picture as a piece standing
up seen from the side - so the pieces are rendered standing and turned into place. That
only works where the tray is seen square on. On the three-quarter plates the tray plane
shears, and the piece is carried through the homography from the flat-lay tray instead.

    python cad/boxshot.py            -> shots/box/*.png and shots/JBD_x_Boutiq.pdf
    python cad/boxshot.py plates     -> just the composites
"""
import math, os, shutil, sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet
from sheet import PAGE, INK, PAPER, RULE, GREY

BOXES = "C:/Users/zelid/Downloads/drive-download-20260807T161544Z-1-001"
OUT = os.path.join("shots", "box")
PDF = os.path.join("shots", "JBD_x_Boutiq.pdf")

# Every placement is written against the flat-lay plate, where the tray is seen square
# on: (cx, cy, span, rot) in fractions of the frame width, rot anticlockwise in degrees.
# The render stands with its cork / hammer head at the top, so +90 lays that end to the
# left and -90 lays it to the right.
#
# The open-box plates are the same tray seen obliquely, and an oblique plane shears -
# the tray's own right angle comes out at 50 degrees - so no amount of turning the piece
# will seat it. `tray` is that plate's printed tray quad, back-left corner first,
# clockwise; the piece is laid out flat and then carried through the homography from the
# flat-lay tray onto it. `lift` then raises it off the tray floor by hand, because the
# homography places a footprint and the piece has a body standing on it.
TRAY_FLAT = ((0.1935, 0.1185), (0.8037, 0.1167), (0.8065, 0.8745), (0.1954, 0.8824))
TRAY_OPEN = ((0.3704, 0.5653), (0.5459, 0.4306), (0.8898, 0.5764), (0.6713, 0.7639))

_PINK_LAY = dict(jar=(0.690, 0.330, 0.360, 0.0), pipe=(0.504, 0.683, 0.549, -95.8))
_BLUE_LAY = dict(jar=(0.667, 0.372, 0.440, 0.0), pipe=(0.502, 0.717, 0.563, 86.5))

PLATES = [
    dict(box="Boutique_Colab_Box_Open_R3_Pink.png", way="magenta_gold", tag="Pink",
         view="Flat lay", strain="Sativa", tray=TRAY_FLAT, lift=(0.0, 0.0), **_PINK_LAY),
    dict(box="Boutique_Colab_Box_Open_R5_C3_Blue.jpg", way="teal_silver", tag="Blue",
         view="Flat lay", strain="Indica", tray=TRAY_FLAT, lift=(0.0, 0.0), **_BLUE_LAY),
    dict(box="Boutique_Colab_Box_Open_Pink.png", way="magenta_gold", tag="Pink",
         view="Open box", strain="Sativa", tray=TRAY_OPEN, lift=(-0.012, -0.016),
         **_PINK_LAY),
    dict(box="Boutique_Colab_Box_Open_R5_C2_Blue.jpg", way="teal_silver", tag="Blue",
         view="Open box", strain="Indica", tray=TRAY_OPEN, lift=(-0.012, -0.016),
         **_BLUE_LAY),
]

# render sizes - the piece framings in mockups are tuned per aspect, so scale both axes
SIZES = dict(jar=(1140, 1500), hammer=(1350, 1140))
SPIN = dict(jar=math.pi, hammer=0.0)      # yaw that turns the printed side to camera
FLAT = (0.5, 0.0, -9.0)                   # kills the sweep's own contact shadow

_BG = {}
_MATTE = {}


def _bg(W, H, elev):
    """The sweep on its own. Same vignette the piece was rendered against, and the
    divisor that turns the white pass back into a transmission."""
    key = (W, H, elev)
    if key not in _BG:
        sys.path.insert(0, "cad")
        import render
        r = render.Renderer(W, H)
        im = r.frame(0.0, elev=elev, bg=((1.0, 1.0, 1.0), (1.0, 1.0, 1.0)), shadow=FLAT)
        _BG[key] = np.maximum(np.asarray(im, "f4") / 255, 1e-3)
    return _BG[key]


def matte(piece, way, turn=0, elev=0.0):
    """Transmission and additive passes for one piece, cropped to its own silhouette."""
    key = (piece, way, turn, elev)
    if key in _MATTE:
        return _MATTE[key]
    sys.path.insert(0, "cad")
    import mockups
    W, H = SIZES[piece]
    r = mockups.build_renderer(piece, way, W, H, decal_turn=turn)
    p = mockups.PIECES[piece]
    kw = dict(cam_r=p["cam_r"], target=p["target"], fov=p["fov"], elev=elev, shadow=FLAT)
    a = SPIN[piece]
    on_black = np.asarray(r.frame(a, bg=((0.0,) * 3, (0.0,) * 3), **kw), "f4") / 255
    on_white = np.asarray(r.frame(a, bg=((1.0,) * 3, (1.0,) * 3), **kw), "f4") / 255
    tint = np.clip((on_white - on_black) / _bg(W, H, elev), 0, 1)
    add = np.clip(on_black, 0, 1)
    # clear glass transmits almost everything, so coverage is where the piece is at all,
    # not how much it darkens - anything the two passes disagree about is the piece
    hit = (1.0 - tint.min(axis=2) > 0.012) | (add.max(axis=2) > 0.012)
    hit = ndimage.binary_fill_holes(ndimage.binary_closing(hit, np.ones((7, 7))))
    ys, xs = np.nonzero(hit)
    if len(ys):
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        tint, add, hit = tint[y0:y1, x0:x1], add[y0:y1, x0:x1], hit[y0:y1, x0:x1]
    _MATTE[key] = (tint, add, np.repeat(hit[..., None].astype("f4"), 3, 2))
    return _MATTE[key]


def _to_im(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype("u1"), "RGB")


def _turn(arr, size, rot, fill):
    """Scale then turn, padding with the value that means 'nothing here' - white for a
    transmission, black for an addition."""
    im = _to_im(arr).resize(size, Image.LANCZOS)
    if rot % 360:
        im = im.rotate(rot, Image.BICUBIC, expand=True, fillcolor=fill)
    return np.asarray(im, "f4") / 255


def _stamp(size, passes, cx, cy, span, rot):
    """Lay one piece into full-frame transmission / additive / coverage passes."""
    W, H = size
    tint, add, hit = passes
    th = max(int(W * span), 4)
    tw = max(int(round(tint.shape[1] * th / tint.shape[0])), 4)
    t = _turn(tint, (tw, th), rot, (255, 255, 255))
    d = _turn(add, (tw, th), rot, (0, 0, 0))
    a = _turn(hit, (tw, th), rot, (0, 0, 0))
    rh, rw = t.shape[:2]
    x, y = int(W * cx - rw / 2), int(H * cy - rh / 2)

    T = np.ones((H, W, 3), "f4"); D = np.zeros((H, W, 3), "f4"); A = np.zeros_like(D)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + rw, W), min(y + rh, H)
    if x1 > x0 and y1 > y0:
        sx, sy = x0 - x, y0 - y
        cut = (slice(sy, sy + y1 - y0), slice(sx, sx + x1 - x0))
        put = (slice(y0, y1), slice(x0, x1))
        T[put], D[put], A[put] = t[cut], d[cut], a[cut]
    return T, D, A, th


def homography(src, dst):
    """The plane map taking one quad onto another, corners in the same order."""
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, V = np.linalg.svd(np.array(A, "f8"))
    return (V[-1] / V[-1][-1]).reshape(3, 3)


def _through(arrs, Hm, cvals):
    """Carry the passes through a plane map, each padded with its own 'nothing here'."""
    h, w = arrs[0].shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    q = np.linalg.inv(Hm) @ np.stack([xx.ravel(), yy.ravel(), np.ones(xx.size)])
    co = [(q[1] / q[2]).reshape(h, w), (q[0] / q[2]).reshape(h, w)]
    return [np.stack([ndimage.map_coordinates(a[..., c], co, order=1, cval=cv)
                      for c in range(3)], -1) for a, cv in zip(arrs, cvals)]


def place(scene, passes, spec, key, shadow=0.44):
    """Seat the piece: clear the placeholder glass out of the cutout, drop a contact
    shadow round the silhouette, then take the plate through the transmission and add
    the reflections back on top."""
    W, H = scene.size
    cx, cy, span, rot = spec[key]
    T, D, A, th = _stamp((W, H), passes, cx, cy, span, rot)

    if tuple(spec["tray"]) != TRAY_FLAT:
        s = np.array(TRAY_FLAT) * (W, H)
        d = (np.array(spec["tray"]) + spec["lift"]) * (W, H)
        T, D, A = _through((T, D, A), homography(s, d), (1.0, 0.0, 0.0))

    S = np.asarray(scene.convert("RGB"), "f4") / 255
    cover = np.clip(A[..., 0], 0, 1)

    # the plates ship with a rainbow stand-in already in the cutout, and a coloured
    # piece laid over it would read as that rainbow tinted. Under the footprint - and a
    # little past it, to catch the stand-in's own edges - it is taken down to its own
    # luminance and softened, so what shows through our glass is the foam bed rather
    # than somebody else's colourway.
    grow = max(int(th * 0.012), 3)
    bed = np.clip(ndimage.gaussian_filter(
        ndimage.grey_dilation(cover, size=(grow, grow)), th * 0.008), 0, 1)[..., None]
    lum = (S * (0.30, 0.59, 0.11)).sum(axis=2)
    lum = 0.35 * lum + 0.65 * ndimage.gaussian_filter(lum, th * 0.035)
    S = S * (1 - bed) + lum[..., None] * bed

    # contact: the piece's own silhouette, blurred and dropped down-right a little
    off = max(int(th * 0.012), 2)
    sh = ndimage.gaussian_filter(np.roll(cover, (off, off), (0, 1)), th * 0.020)
    S *= (1.0 - shadow * np.clip(sh - cover, 0, 1))[..., None]

    return _to_im(S * T + D).convert("RGBA")


def build_plates():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for spec in PLATES:
        src = os.path.join(BOXES, spec["box"])
        if not os.path.exists(src):
            raise SystemExit("missing box plate: " + src)
        scene = Image.open(src).convert("RGBA")
        for piece, key in (("jar", "jar"), ("hammer", "pipe")):
            # the print runs one way along the stem, so a case that lays the head to
            # the right gets the label struck the other way round rather than upside down
            turn = 180 if piece == "hammer" and spec[key][3] < 0 else 0
            scene = place(scene, matte(piece, spec["way"], turn), spec, key)
        name = os.path.splitext(spec["box"])[0] + "_with_glass.png"
        path = os.path.join(OUT, name)
        scene.convert("RGB").save(path)
        made.append(path)
        print("wrote", name)
    return made


# ---------------------------------------------------------------- the leave-behind

SPEC = [
    ("", "Clearboy hammer", "Nug jar"),
    ("Overall", "140 mm", "92 mm glass + cork lid"),
    ("Section", "head 68 long, 42 × 37 oval", "straight cylinder, ø 44"),
    ("Opening", "bowl ø 25, ø 3 hole", "mouth ø 38, cork plug"),
    ("Wall", "≈ 3 mm chamber (inferred)", "3 mm, flat closed bottom"),
    ("Stem", "ø 14 OD / ø 8 bore", "—"),
    ("Mark", "enamel label, dropped out white", "JBD pressed into a stamp pad"),
    ("Glass", "≈ 81 g in boro 3.3", "≈ 90 g + ≈ 10 g cork"),
    ("Frit", "bowl end, 4 clear marbles", "band under the rim, 7 marbles"),
]


def _cover_page():
    W, H = PAGE
    pg = Image.new("RGB", PAGE, INK)
    d = ImageDraw.Draw(pg)
    art = sheet.fit(Image.open(os.path.join(
        OUT, "Boutique_Colab_Box_Open_Pink_with_glass.png")).convert("RGB"), (660, 760))
    pg.paste(art, (W - art.width - 90, (H - art.height) // 2))
    col = W - art.width - 90 - 150 - 60            # room the text column actually has
    sheet.lockup(d, 150 + col / 2, 300, 66, (245, 243, 240))
    d.line([(150, 396), (150 + col, 396)], fill=(92, 90, 92), width=2)
    d.text((150, 446), "The Clearboy\nprogramme", font=sheet.font(True, 58),
           fill=(245, 243, 240), spacing=14)
    d.multiline_text((150, 606), sheet.wrap(
        d, "Collaboration box — hammer bubbler and nug jar, in bluish teal / "
           "silver fume and magenta / gold fume.", sheet.font(False, 28), col)[0],
        font=sheet.font(False, 28), fill=(176, 174, 176), spacing=12)
    d.multiline_text((150, 762), sheet.wrap(
        d, "Reverse-engineered from one hand-blown original. Renders are proposals "
           "— the original stays the reference.", sheet.font(False, 24), col)[0],
        font=sheet.font(False, 24), fill=(132, 130, 132), spacing=12)
    d.text((150, H - 130), "Jerome Baker Designs", font=sheet.font(True, 24),
           fill=(150, 148, 150))
    return pg


def _plate_page(spec):
    W, H = PAGE
    pg = Image.new("RGB", PAGE, PAPER)
    d = ImageDraw.Draw(pg)
    art = sheet.fit(Image.open(os.path.join(
        OUT, os.path.splitext(spec["box"])[0] + "_with_glass.png")).convert("RGB"),
        (950, H - 200))
    pg.paste(art, (W - art.width - 80, (H - art.height) // 2))

    sys.path.insert(0, "cad")
    import mockups
    way = mockups.WAYS[spec["way"]]
    x, col = 100, W - 950 - 80 - 100 - 60
    sheet.lockup(d, x + 130, 110, 30, INK)
    d.multiline_text((x, 196), sheet.wrap(d, way["name"], sheet.font(True, 42), col)[0],
                     font=sheet.font(True, 42), fill=INK, spacing=10)
    d.multiline_text((x, 320), sheet.wrap(d, way["sub"], sheet.font(False, 24), col)[0],
                     font=sheet.font(False, 24), fill=GREY, spacing=8)
    d.line([(x, 400), (x + col, 400)], fill=RULE, width=2)
    rows = [("Colourway", spec["tag"]), ("View", spec["view"]),
            ("Flower", spec["strain"]),
            ("Contents", "hammer bubbler, nug jar,\nflower jar, pre-roll")]
    y = 440
    for k, v in rows:
        d.text((x, y), k.upper(), font=sheet.font(True, 19), fill=GREY)
        d.multiline_text((x, y + 28), v, font=sheet.font(False, 25), fill=INK,
                         spacing=9)
        y += 84 + 32 * v.count("\n")
    d.text((x, H - 170), "Glass shown is rendered,\nnot photographed.",
           font=sheet.font(False, 21), fill=GREY, spacing=8)
    return pg


def _spec_page():
    W, H = PAGE
    pg = Image.new("RGB", PAGE, PAPER)
    d = ImageDraw.Draw(pg)
    sheet.lockup(d, W // 2, 110, 32, INK)
    d.text((110, 190), "The pieces", font=sheet.font(True, 52), fill=INK)

    y = 300
    for i, (k, a, b) in enumerate(SPEC):
        bold = i == 0
        d.text((110, y), k, font=sheet.font(True, 22), fill=GREY)
        d.text((470, y - 2), a, font=sheet.font(bold, 26), fill=INK)
        d.text((950, y - 2), b, font=sheet.font(bold, 26), fill=INK)
        y += 54
        d.line([(110, y - 14), (W - 110, y - 14)], fill=RULE, width=1)

    for i, (piece, way) in enumerate((("hammer", "magenta_gold"),
                                      ("jar", "teal_silver"))):
        p = os.path.join("shots", "%s_%s.png" % (piece, way))
        if os.path.exists(p):
            im = sheet.fit(Image.open(p).convert("RGB"), (330, 330))
            pg.paste(im, (170 + i * 420, H - im.height - 130))

    d.text((1050, H - 300),
           "Wall thickness on the hammer is inferred,\n"
           "not measured. Two caliper readings \u2014 rim\n"
           "and stem OD \u2014 lock the whole model;\n"
           "mass, volume and glass cost all move if\n"
           "they come back different.",
           font=sheet.font(False, 24), fill=GREY, spacing=12)
    return pg


def build_pdf():
    pages = [_cover_page()] + [_plate_page(s) for s in PLATES] + [_spec_page()]
    pages[0].save(PDF, save_all=True, append_images=pages[1:], resolution=150.0,
                  title="JBD \u00d7 Boutiq \u2014 Clearboy programme")
    print("wrote", PDF, "\u2014", len(pages), "pages")
    if os.path.isdir("docs"):
        shutil.copyfile(PDF, os.path.join("docs", os.path.basename(PDF)))
        print("wrote", os.path.join("docs", os.path.basename(PDF)))
    return PDF


if __name__ == "__main__":
    what = sys.argv[1:] or ["plates", "pdf"]
    if "plates" in what:
        build_plates()
    if "pdf" in what:
        build_pdf()
