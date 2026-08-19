"""Dimensioned closeups - the detail views that go on the spec sheet.

Each view renders the real piece and then draws its dimensions over it, with the
witness lines projected from model coordinates through the same camera the render
used. Nothing here is placed by eye: move a constant in model.py or jar.py and the
arrows move with it.

    python cad/callouts.py      -> shots/spec/*.png
"""
import math, os, sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render, mockups, sheet
import model as M
import jar as J

OUT = os.path.join("shots", "spec")
FRIT = True             # Rev A rolls frit; Rev B leaves the body smooth
# the fumed builds carry the linework the shop actually lays down - 9 turns over the
# frit, not the 42-turn body spiral the clear builds wear - so they read cleanest here
WAY = "teal_silver"
INK = (20, 22, 26)
DIM = (176, 26, 38)
PAPER = (252, 251, 249)


def _renderer(piece, W, H):
    return mockups.build_renderer(piece, WAY, W, H, frit=FRIT)


def _shot(piece, W, H, cam):
    """A clean plate on near-white, plus the projector that goes with it."""
    r = _renderer(piece, W, H)
    im = r.frame(cam.get("angle", 0.0), cam_r=cam["cam_r"], target=cam["target"],
                 fov=cam["fov"], elev=cam.get("elev", 3.0),
                 bg=((0.995, 0.995, 0.993), (0.955, 0.958, 0.962)),
                 shadow=(0.5, 0.0, -9.0)).convert("RGB")

    def px(pts):
        return r.project(pts, cam.get("angle", 0.0), cam_r=cam["cam_r"],
                         elev=cam.get("elev", 3.0), target=cam["target"], fov=cam["fov"])
    return im, px


# ------------------------------------------------------------------ dimension kit

def _arrow(d, at, along, size=9):
    u = np.array(along, "f8"); u = u / max(np.hypot(*u), 1e-9)
    n = np.array([-u[1], u[0]])
    p = np.array(at, "f8")
    d.polygon([tuple(p), tuple(p + u * size + n * size * 0.36),
               tuple(p + u * size - n * size * 0.36)], fill=DIM)


def _label(d, at, text, anchor="mm", small=False):
    f = sheet.font(True, 21 if not small else 18)
    w = d.textlength(text, font=f)
    h = 22 if not small else 19
    x, y = at
    x -= w / 2 if anchor[1] == "m" else (w + 6 if anchor[1] == "r" else -6)
    y -= h / 2 if anchor[0] == "m" else (h + 4 if anchor[0] == "b" else -4)
    d.rectangle([x - 6, y - 4, x + w + 6, y + h + 2], fill=PAPER)
    d.text((x, y - 1), text, font=f, fill=DIM)


DIRS = dict(left=(-1.0, 0.0), right=(1.0, 0.0), above=(0.0, -1.0), below=(0.0, 1.0))


def dim(d, a, b, off, text, side="below", gap=9):
    """A dimension between two projected points, stood `off` px clear of the feature in
    a screen direction. Screen-space on purpose: a piece spun to face the camera can
    mirror model x, so which way is 'right' is not something model coordinates know."""
    a, b = np.array(a, "f8"), np.array(b, "f8")
    n = np.array(DIRS[side], "f8")
    at = max(a @ n, b @ n) + off
    A, B = a + n * (at - a @ n), b + n * (at - b @ n)
    for p, q in ((a, A), (b, B)):
        d.line([tuple(p + n * gap), tuple(q + n * 8)], fill=DIM, width=1)
    d.line([tuple(A), tuple(B)], fill=DIM, width=2)
    _arrow(d, A, B - A); _arrow(d, B, A - B)
    # a label wider than its own dimension would sit on the arrowheads - stand it off
    # past the far end instead, the way a short dimension is normally set
    u = (B - A) / max(np.hypot(*(B - A)), 1e-9)
    w = d.textlength(text, font=sheet.font(True, 21))
    _label(d, B + u * (w / 2 + 22) if w + 26 > np.hypot(*(B - A)) else (A + B) / 2, text)


def leader(d, at, by, text):
    """Point at a feature and set the label `by` (dx, dy) pixels away from it."""
    a = np.array(at, "f8"); b = a + np.array(by, "f8")
    d.line([tuple(a), tuple(b)], fill=DIM, width=1)
    d.ellipse([a[0] - 3, a[1] - 3, a[0] + 3, a[1] + 3], fill=DIM)
    _label(d, b, text)


def caption(d, size, title, sub):
    d.text((26, 20), title, font=sheet.font(True, 26), fill=INK)
    d.text((26, 56), sub, font=sheet.font(False, 20), fill=(112, 110, 108))
    d.line([(26, 88), (size[0] - 26, 88)], fill=(206, 203, 199), width=1)


# ------------------------------------------------------------------------- views

CZ = M._interp(0, 0)[2]                       # head centre height
RIM = M.HEAD_X1                               # bowl rim face, on the head axis
THROAT = M.HEAD_X1 - M.BOWL_DEPTH
CARB_X = M.HEAD_X1 - M.CARB_FROM_RIM
CARB_Z = M._interp(CARB_X, 0.0)[2]


def head():
    W, H = 1500, 1050
    im, px = _shot("hammer", W, H, dict(cam_r=400.0, target=(0, 0, CZ), fov=17.0,
                                        elev=0.0))
    d = ImageDraw.Draw(im)
    caption(d, (W, H), "Head and bowl", "Broadside. The chamber is a shaped solid, not "
            "a cylinder — the section is oval and varies along the axis.")
    hh = 42.0                                  # the max section, at x = -30
    dim(d, px([(M.HEAD_X0, 0, CZ + hh / 2)])[0], px([(RIM, 0, CZ + hh / 2)])[0],
        90, "68  chamber length", "above")
    dim(d, px([(-30.0, 0, CZ + hh / 2)])[0], px([(-30.0, 0, CZ - hh / 2)])[0],
        120, "42  max section", "left")
    leader(d, px([(RIM, 0, CZ + M.BOWL_ID / 2 - 1)])[0], (150, -150),
           "bowl ø 25 at the rim")
    leader(d, px([(CARB_X, 0, CARB_Z + 11.0)])[0], (-30, -190),
           "carb ø 3.5 · ø 11 boss")
    dim(d, px([(CARB_X, 0, CZ - hh / 2)])[0], px([(RIM, 0, CZ - hh / 2)])[0],
        70, "14  carb below the rim", "below")
    dim(d, px([(THROAT, 0, CZ - hh / 2)])[0], px([(RIM, 0, CZ - hh / 2)])[0],
        150, "19  bowl depth", "below")
    return im, "head"


def bowl():
    W, H = 1100, 1100
    # look straight down the head axis: spin the piece so the bowl faces the camera
    im, px = _shot("hammer", W, H, dict(cam_r=300.0, target=(0, 0, CZ + 2), fov=17.0,
                                        angle=-math.pi / 2, elev=0.0))
    d = ImageDraw.Draw(im)
    caption(d, (W, H), "Bowl end, on the head axis",
            "The hole in the bottom of the bowl is called down to ø 3. The original "
            "measured ø 5 — do not correct it back.")
    a, b = px([(RIM, 0, CZ + M.BOWL_ID / 2), (RIM, 0, CZ - M.BOWL_ID / 2)])
    dim(d, a, b, 250, "ø 25  opening at the rim", "right")
    a, b = px([(THROAT, 0, CZ + M.BOWL_THROAT / 2),
               (THROAT, 0, CZ - M.BOWL_THROAT / 2)])
    leader(d, (a + b) / 2, (-190, 210), "ø 3  hole in the bottom of the bowl")
    return im, "bowl"


def stem():
    W, H = 1100, 1400
    im, px = _shot("hammer", W, H, dict(cam_r=580.0, target=(0, 0, 66.0), fov=17.0,
                                        elev=0.0))
    d = ImageDraw.Draw(im)
    caption(d, (W, H), "Stem, foot and label band",
            "Stem thickened from the original ø 11 so the enamel band has a flat to "
            "sit on. The bore runs the full length.")
    dim(d, px([(-M.STEM_OD / 2, 0, 88)])[0], px([(M.STEM_OD / 2, 0, 88)])[0],
        44, "ø 14 OD", "above")
    leader(d, px([(0, 0, 80)])[0], (150, -30), "ø 8 bore")
    dim(d, px([(-M.FOOT_OD / 2, 0, 0)])[0], px([(M.FOOT_OD / 2, 0, 0)])[0],
        90, "ø 24.5 foot", "below")
    dim(d, px([(M.FOOT_OD / 2, 0, M.FOOT_T)])[0], px([(M.FOOT_OD / 2, 0, 0)])[0],
        56, "7", "right")
    z0, z1, _ = mockups.PIECES["hammer"]["decal"]
    dim(d, px([(0, 0, z1)])[0], px([(0, 0, z0)])[0],
        150, "label band  20–74", "left")
    dim(d, px([(0, 0, M.FOOT_T + 88.0)])[0],
        px([(0, 0, M.FOOT_T)])[0], 180, "88  exposed stem", "right")
    return im, "stem"


def jar_body():
    W, H = 1100, 1400
    top = J.HEIGHT - J.CORK_SEAT + J.CORK_H
    im, px = _shot("jar", W, H, dict(cam_r=560.0, target=(0, 0, top / 2), fov=17.0,
                                     elev=0.0, angle=math.pi))
    d = ImageDraw.Draw(im)
    caption(d, (W, H), "Nug jar", "Straight cylinder, flat closed bottom. The frit band "
            "and its marbles sit under the rim." if FRIT else
            "Straight cylinder, flat closed bottom. No frit - the linework and its "
            "marbles sit under the rim.")
    dim(d, px([(-J.OD / 2, 0, 0)])[0], px([(J.OD / 2, 0, 0)])[0], 90,
        "ø 44 OD", "below")
    dim(d, px([(0, 0, J.HEIGHT)])[0], px([(0, 0, 0)])[0], 240,
        "92  glass height", "left")
    dim(d, px([(-J.MOUTH_ID / 2, 0, J.HEIGHT)])[0],
        px([(J.MOUTH_ID / 2, 0, J.HEIGHT)])[0], 190, "ø 38 mouth", "above")
    # same band either way - on Rev B the linework occupies the height the frit had
    dim(d, px([(0, 0, J.FRIT_Z[1])])[0], px([(0, 0, J.FRIT_Z[0])])[0],
        240, "frit  66–90.5" if FRIT else "linework  66–90.5", "right")
    leader(d, px([(0, -J.OD / 2, J.MARBLE_Z)])[0], (-190, -120), "7 × ø 8 marbles")
    leader(d, px([(0, -J.OD / 2, J.STAMP_Z)])[0], (0, 150), "JBD pressed mark")
    return im, "jar_body"


def jar_cork():
    W, H = 1200, 900
    top = J.HEIGHT - J.CORK_SEAT + J.CORK_H
    z0 = J.HEIGHT - J.CORK_SEAT
    im, px = _shot("jar", W, H, dict(cam_r=330.0, target=(0, 0, (z0 + top) / 2 - 2),
                                     fov=17.0, elev=0.0, angle=math.pi))
    d = ImageDraw.Draw(im)
    caption(d, (W, H), "Mouth and cork",
            "One gently tapered plug, no mushroom cap. It seats on the taper, about "
            "12 mm standing proud.")
    dim(d, px([(-J.CORK_D_TOP / 2, 0, top)])[0], px([(J.CORK_D_TOP / 2, 0, top)])[0],
        70, "ø 41 top", "above")
    dim(d, px([(0, 0, top)])[0], px([(0, 0, z0)])[0],
        250, "27  cork length", "right")
    dim(d, px([(0, 0, J.HEIGHT)])[0], px([(0, 0, z0)])[0],
        250, "15  seat", "left")
    leader(d, px([(0, -J.CORK_D_BOT / 2, z0 + 2)])[0], (-40, 190),
           "ø 36.6 cork bottom")
    leader(d, px([(J.OD / 2, 0, J.HEIGHT)])[0], (-150, 210), "rim · ø 38 ID")
    return im, "jar_cork"


VIEWS = [head, bowl, stem, jar_body, jar_cork]


def build(out=None, frit=True):
    global OUT, FRIT
    OUT, FRIT = out or OUT, frit
    os.makedirs(OUT, exist_ok=True)
    made = []
    for fn in VIEWS:
        im, name = fn()
        p = os.path.join(OUT, name + ".png")
        im.save(p)
        made.append(p)
        print("wrote", p, im.size)
    return made


if __name__ == "__main__":
    build()
