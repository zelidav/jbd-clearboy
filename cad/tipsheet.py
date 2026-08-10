"""Glass tip concept sheet - dimensions, and how the slot is used.

Plain clear glass, no frit, no marbles, no stones. The whole idea is the slot, so the
sheet spends its space on the dimensions and on the four steps that show what it is for.

The paper in the rolling sequence is drawn, not rendered - a rolling paper is a
translucent white sheet and the glass compositor has nothing sensible to say about it.
The tip in every step is the real render.

    python cad/tipsheet.py    -> shots/tip/*.png, shots/JBD_Glass_Tip.pdf
"""
import math, os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet
import callouts as C
from sheet import PAGE, INK, PAPER, RULE, GREY

OUT = os.path.join("shots", "tip")
PDF = os.path.join("shots", "JBD_Glass_Tip.pdf")
WAY = "clear_silver"            # plain clear - the only way this piece is offered
PAPERC = (247, 244, 236)
PAPERE = (206, 200, 186)


def _shot(size, cam, angle=0.0):
    import mockups, tip
    r = mockups.build_renderer("tip", WAY, *size)
    p = mockups.PIECES["tip"]
    kw = dict(cam_r=cam.get("cam_r", p["cam_r"]), target=cam.get("target", p["target"]),
              fov=p["fov"], elev=cam.get("elev", 3.0),
              shadow=cam.get("shadow", p["shadow"]),
              tilt=cam.get("tilt", p["tilt"]), shift=cam.get("shift", p["shift"]))
    im = r.frame(angle, **kw).convert("RGB")

    def px(pts):
        return r.project(pts, angle, cam_r=kw["cam_r"], elev=kw["elev"],
                         target=kw["target"], fov=kw["fov"], tilt=kw["tilt"],
                         shift=kw["shift"])
    return im, px


def dim_view():
    """Side elevation with the numbers on it. Witness lines come off the model through
    the same camera, so they follow the parameters rather than a ruler on a picture."""
    import tip
    P = tip.P
    W, H = 1400, 620
    im, px = _shot((W, H), dict(cam_r=86.0, target=(0, 0, 0), elev=0.0,
                                shadow=(0.5, 0.0, -9.0)), angle=0.0)
    d = ImageDraw.Draw(im)
    L, R = P["length"], P["od"] / 2
    # only the three that belong on a drawing this small - the rest reads better as a
    # column beside it than as more arrows on top of the glass
    C.dim(d, px([(0, 0, 0)])[0], px([(0, 0, L)])[0], 70, "19  overall", "above")
    C.dim(d, px([(0, R, 0)])[0], px([(0, -R, 0)])[0], 60, "ø 9", "right")
    C.dim(d, px([(0, 0, 0)])[0], px([(0, 0, P["screen_z"])])[0], 60,
          "6.5  to the screen", "below")
    C.leader(d, px([(0, -R, P["groove_z"] + 4)])[0], (-30, -170), "the slot")
    return im


def end_view():
    """Down the bore, so the screen pattern reads."""
    W, H = 900, 900
    im, px = _shot((W, H), dict(cam_r=86.0, target=(0, 0, 9.5), elev=80.0,
                                tilt=0.0, shift=None, shadow=(0.5, 0.0, -9.0)))
    return im


# ------------------------------------------------------------- rolling sequence

def _paper_flat(d, box, lean=16):
    """A rolling paper, edge on to the slot."""
    x, y, w, h = box
    pts = [(x, y + lean), (x + w, y), (x + w, y + h), (x, y + h + lean)]
    d.polygon(pts, fill=PAPERC, outline=PAPERE)
    d.line([pts[0], pts[3]], fill=(150, 40, 60), width=4)      # the edge that goes in


def _paper_on_slot(d, a, b, reach):
    """The paper leaving the slot: its leading edge sits on the slot line, and the
    sheet runs off square to it."""
    import numpy as np
    a, b = np.array(a, "f8"), np.array(b, "f8")
    u = (b - a) / max(np.hypot(*(b - a)), 1e-9)
    n = np.array([-u[1], u[0]])
    if n[0] < 0:
        n = -n
    quad = [tuple(a), tuple(b), tuple(b + n * reach), tuple(a + n * reach)]
    d.polygon(quad, fill=PAPERC, outline=PAPERE)
    d.line([tuple(a), tuple(b)], fill=(150, 40, 60), width=5)


def _paper_wrap(d, cx, cy, r, a0, a1, t=26):
    """Paper part-way round, drawn as a band."""
    outer = [(cx + (r + t) * math.cos(a), cy + (r + t) * math.sin(a))
             for a in [a0 + (a1 - a0) * i / 40.0 for i in range(41)]]
    inner = [(cx + r * math.cos(a), cy + r * math.sin(a))
             for a in [a1 + (a0 - a1) * i / 40.0 for i in range(41)]]
    d.polygon(outer + inner, fill=PAPERC, outline=PAPERE)


def steps():
    """Four frames. The tip is rendered; the paper is drawn over it."""
    os.makedirs(OUT, exist_ok=True)
    W, H = 760, 560
    cam = dict(cam_r=118.0, target=(0, 0, 0), elev=10.0, shadow=(0.5, 0.34, 0.06))
    out = []

    # 1 - the slot
    im, px = _shot((W, H), cam, angle=0.0)
    d = ImageDraw.Draw(im)
    C.leader(d, px([(0, -4.5, 13.0)])[0], (60, -160), "the slot")
    out.append((im, "One", "The slot runs the length of the tube, cut in on a lean."))

    # 2 - feed the edge in
    im, px = _shot((W, H), cam, angle=0.0)
    d = ImageDraw.Draw(im)
    import tip
    # the slot runs along the axis now, so its two ends are just the ends of the run
    run = tip.P["length"] * tip.P["groove_run"] / 2.0
    ends = px([(0, -tip.P["od"] / 2, tip.P["groove_z"] - run),
               (0, -tip.P["od"] / 2, tip.P["groove_z"] + run)])
    _paper_on_slot(d, ends[0], ends[1], 300)
    C.leader(d, px([(0, -4.5, 15.0)])[0], (-30, 150), "edge into the slot")
    out.append((im, "Two", "Slip the leading edge of the paper into it. The slot holds "
                           "the paper on its own."))

    # 3 - roll it on
    im, px = _shot((W, H), cam, angle=0.9)
    d = ImageDraw.Draw(im)
    c = px([(0, 0, 9.5)])[0]
    _paper_wrap(d, c[0], c[1], 96, math.radians(-150), math.radians(60), 30)
    out.append((im, "Three", "Roll the tip. The paper winds on, and the rake starts the "
                             "wrap slightly off-square - the bias a cone wants."))

    # 4 - rolled
    im, px = _shot((W, H), cam, angle=1.6)
    d = ImageDraw.Draw(im)
    c = px([(0, 0, 9.5)])[0]
    _paper_wrap(d, c[0], c[1], 92, math.radians(-180), math.radians(180), 34)
    out.append((im, "Four", "Wound on and filled. The screen keeps it from pulling "
                            "through, and the tip washes and goes again."))

    for i, (im, n, _t) in enumerate(out):
        im.save(os.path.join(OUT, "step%d.png" % (i + 1)))
    return out


def compare_page():
    """The two ways to build it, side by side. Same job, opposite answers."""
    import mockups
    pg, d = sheet.blank()
    d.text((96, 62), "JEROME BAKER DESIGNS", font=sheet.font(True, 26), fill=INK)
    d.line([(96, 122), (PAGE[0] - 96, 122)], fill=RULE, width=2)
    d.text((96, 152), "Glass tip — two ways", font=sheet.font(True, 44), fill=INK)
    d.text((96, 212), "Same job, opposite answers. One is a tube with a slot in it. The "
           "other is all slot.", font=sheet.font(False, 24), fill=GREY)
    f = sheet.font(False, 20)
    tag = "Concept  ·  1 / 2"
    d.text((PAGE[0] - 96 - d.textlength(tag, font=f), 92), tag, font=f, fill=GREY)

    cards = [("tip", "Slotted tube",
              "A slot down the length, cut in on a seventy-degree lean so it undercuts "
              "and holds the paper. Perforated screen across the bore.",
              [("Overall", "19 mm"), ("Outside", "ø 9 mm"), ("Bore", "ø 6.4, 1.3 wall"),
               ("Screen", "seven ø 1.25 holes"), ("Slot", "0.75 wide, 0.9 deep"),
               ("Mass", "≈ 1.4 g")]),
             ("tip_spiral", "Wound coil",
              "No tube at all - rod wound open end to end. The gap between the turns is "
              "the slot, and it runs the whole piece, so the paper goes into the outer "
              "ring anywhere along it.",
              [("Overall", "19 mm"), ("Outside", "ø 9 mm"), ("Rod", "ø 1.7"),
               ("Turns", "six and a half"), ("Slot", "every turn, all the way"),
               ("Mass", "≈ 3.7 g")])]
    for i, (key, nm, body, rows) in enumerate(cards):
        x = 96 + i * 740
        p_ = os.path.join(OUT, "%s_hero.png" % key)
        if not os.path.exists(p_):
            mockups.PIECES[key] = dict(mockups.PIECES[key], size=(1100, 620))
            im = mockups.frame(mockups.build_renderer(key, WAY, 1100, 620), key,
                               mockups.SIDE)
            im.save(p_)
        art = sheet.fit(Image.open(p_).convert("RGB"), (700, 400))
        pg.paste(art, (x, 272))
        d.text((x, 700), nm, font=sheet.font(True, 32), fill=INK)
        yy = sheet.wrap(d, body, sheet.font(False, 22), 660)
        d.multiline_text((x, 748), yy[0], font=sheet.font(False, 22), fill=INK,
                         spacing=8)
        yy2 = 762 + 30 * yy[1]
        for k, v in rows:
            d.text((x, yy2), k, font=sheet.font(False, 20), fill=GREY)
            d.text((x + 220, yy2), v, font=sheet.font(True, 21), fill=INK)
            yy2 += 40
    d.line([(96, PAGE[1] - 74), (PAGE[0] - 96, PAGE[1] - 74)], fill=RULE, width=1)
    d.text((96, PAGE[1] - 60), "The coil draws freely and cannot clog, but it cannot "
           "carry a screen · the tube filters · renders, not photographs",
           font=sheet.font(False, 19), fill=GREY)
    return pg


def build():
    os.makedirs(OUT, exist_ok=True)
    dv = dim_view(); dv.save(os.path.join(OUT, "dims.png"))
    ev = end_view(); ev.save(os.path.join(OUT, "end.png"))
    st = steps()

    pg, d = sheet.blank()
    d.text((96, 62), "JEROME BAKER DESIGNS", font=sheet.font(True, 26), fill=INK)
    d.line([(96, 122), (PAGE[0] - 96, 122)], fill=RULE, width=2)
    d.text((96, 152), "Glass tip", font=sheet.font(True, 44), fill=INK)
    d.text((96, 212), "19 mm of clear 9 mm tube. Perforated screen across the bore, and "
           "a straight slot cut at a long oblique to start the roll.",
           font=sheet.font(False, 24), fill=GREY)
    f = sheet.font(False, 20)
    tag = "Concept  ·  2 / 2"
    d.text((PAGE[0] - 96 - d.textlength(tag, font=f), 92), tag, font=f, fill=GREY)

    art = sheet.fit(dv, (960, 470))
    pg.paste(art, (80, 278))
    art2 = sheet.fit(ev, (290, 290))
    pg.paste(art2, (1058, 292))
    d.text((1058, 596), "Down the bore", font=sheet.font(True, 20), fill=INK)
    d.text((1058, 622), "seven holes, one centre", font=sheet.font(False, 19),
           fill=GREY)

    import tip
    P = tip.P
    rows = [("Overall length", "19 mm"), ("Outside diameter", "9 mm"),
            ("Bore / wall", "6.4 / 1.3 mm"),
            ("Screen", "1.5 thick, 6.5 in"),
            ("Screen holes", "seven ø 1.25"),
            ("Slot", "0.75 wide, 0.9 deep"),
            ("Slot rake", "68° off the axis"),
            ("Glass", "clear boro 3.3, ≈ 1.4 g")]
    yy = 292
    for k, v in rows:
        d.text((1382, yy), k, font=sheet.font(False, 20), fill=GREY)
        txt, n = sheet.wrap(d, v, sheet.font(True, 21), 172)
        d.multiline_text((1382, yy + 22), txt, font=sheet.font(True, 21),
                         fill=INK, spacing=4)
        yy += 30 + 25 * n

    y = 800
    d.text((96, y - 44), "ROLLING", font=sheet.font(True, 19), fill=C.DIM)
    cw = 356
    for i, (im, n, txt) in enumerate(st):
        x = 96 + i * (cw + 10)
        a = sheet.fit(im, (cw, 250))
        pg.paste(a, (x, y))
        d.text((x, y + 262), n, font=sheet.font(True, 22), fill=C.DIM)
        d.multiline_text((x, y + 294), sheet.wrap(d, txt, sheet.font(False, 19),
                                                  cw - 12)[0],
                         font=sheet.font(False, 19), fill=INK, spacing=6)
    d.line([(96, PAGE[1] - 74), (PAGE[0] - 96, PAGE[1] - 74)], fill=RULE, width=1)
    d.text((96, PAGE[1] - 60), "Clear borosilicate only · no frit, no marbles, no "
           "stones · renders, not photographs",
           font=sheet.font(False, 19), fill=GREY)
    sheet.save([compare_page(), pg], PDF, "JBD glass tip - concept")
    return PDF


if __name__ == "__main__":
    build()
