"""JBD 'Clearboy' hammer - parametric solid model.
Units: mm.  Origin: centre of the foot's bottom face.  Z up (standing on the foot).
Head axis runs along X: closed lobe at -X, bowl at +X.
Dimensions per the photogrammetric survey (JBD_Clearboy_dimensions.png).
"""
import math, cadquery as cq
from cadquery import Vector

# ---------------------------------------------------------------- parameters
TOTAL_H      = 140.0
FOOT_OD      = 24.5
FOOT_T       = 7.0
STEM_OD      = 14.0         # thickened from the survey's 11.0 to carry the enamel label
STEM_ID      = 8.0
COLLAR_OD    = 17.5
COLLAR_H     = 9.0
WALL         = 3.0          # chamber wall
BOWL_ID      = 25.0         # opening at the rim
BOWL_THROAT  = 3.0          # the hole in the bottom of the bowl
BOWL_DEPTH   = 19.0
CARB_D       = 3.5
CARB_BOSS_D  = 11.0
CARB_FROM_RIM= 14.0
HEAD_X0      = -36.0        # closed end
HEAD_X1      =  32.0        # bowl rim face   (length 68)
STEM_TOP     = 112.0        # where the stem disappears into the head
# The pose, as three angles measured on the piece:
#   Angle 3  HEAD_FROM_VERT - the head axis off the vertical datum. 90 lies it flat,
#            which is the original hammer.
#   Angle 1  STEM_TO_HEAD   - the included angle at the joint between the head axis and
#            the stem, taken on the upper side. Angle 2 is its supplement and needs no
#            parameter of its own: 180 less this.
STEM_ANGLE   = 0.0          # rake from vertical, degrees. Derived from the two above
HEAD_FROM_VERT = 90.0       # Angle 3
STEM_TO_HEAD = 90.0         # Angle 1
COLLAR_Z     = 100.5        # top of the upper collar

# head sections: (x, height Z, width Y, centre Z)
SECTIONS = [
    (-36.0, 33.0, 30.0, 119.2),
    (-34.0, 38.5, 34.6, 119.0),
    (-30.0, 42.0, 37.0, 118.8),
    (-24.0, 41.4, 36.6, 118.8),
    (-18.0, 39.6, 35.4, 118.7),
    (-12.0, 36.0, 33.0, 118.4),
    ( -6.0, 31.6, 30.2, 118.1),
    (  0.0, 29.4, 28.9, 118.2),
    (  6.0, 28.4, 28.3, 118.7),
    ( 14.0, 28.0, 28.0, 119.2),
    ( 22.0, 28.2, 28.2, 119.0),
    ( 28.5, 29.2, 29.2, 118.7),
    ( 32.0, 29.4, 29.4, 118.6),
]
SUPER_N = 2.25              # superellipse exponent -> soft rounded-rectangle section


def superellipse(x, h, w, cz, n=SUPER_N, pts=72):
    """Closed spline wire on the YZ plane at station x."""
    a, b = w / 2.0, h / 2.0
    p = []
    for i in range(pts):
        t = 2 * math.pi * i / pts
        ct, st = math.cos(t), math.sin(t)
        y = a * math.copysign(abs(ct) ** (2.0 / n), ct)
        z = b * math.copysign(abs(st) ** (2.0 / n), st)
        p.append(Vector(x, y, cz + z))
    e = cq.Edge.makeSpline([cq.Vector(v) for v in p], periodic=True)
    return cq.Wire.assembleEdges([e])


def head_loft(scale_h=1.0, scale_w=1.0, inset=0.0, x0=None, x1=None):
    """Loft through the sections, optionally shrunk by `inset` mm all round."""
    secs = []
    for (x, h, w, cz) in SECTIONS:
        if x0 is not None and x < x0: continue
        if x1 is not None and x > x1: continue
        secs.append((x, max(h * scale_h - 2 * inset, 0.6),
                        max(w * scale_w - 2 * inset, 0.6), cz))
    if x0 is not None and secs and secs[0][0] > x0 + 1e-6:
        h, w, cz = _interp(x0, inset); secs.insert(0, (x0, h, w, cz))
    if x1 is not None and secs and secs[-1][0] < x1 - 1e-6:
        h, w, cz = _interp(x1, inset); secs.append((x1, h, w, cz))
    wires = [superellipse(*s) for s in secs]
    return cq.Solid.makeLoft(wires, ruled=False)


def _interp(x, inset):
    xs = [s[0] for s in SECTIONS]
    if x <= xs[0]:  s0 = s1 = SECTIONS[0];  t = 0
    elif x >= xs[-1]: s0 = s1 = SECTIONS[-1]; t = 0
    else:
        i = max(j for j in range(len(xs)) if xs[j] <= x)
        i = min(i, len(xs) - 2)
        s0, s1 = SECTIONS[i], SECTIONS[i + 1]
        t = (x - s0[0]) / (s1[0] - s0[0])
    h = s0[1] + (s1[1] - s0[1]) * t
    w = s0[2] + (s1[2] - s0[2]) * t
    cz = s0[3] + (s1[3] - s0[3]) * t
    return max(h - 2 * inset, 0.6), max(w - 2 * inset, 0.6), cz


def _joint():
    return (0.0, 0.0, _interp(0, 0)[2])


def _pose(shape, deg):
    """Turn a part about the joint, in the plane the piece is drawn in."""
    if not deg:
        return shape
    j = _joint()
    return shape.rotate((j[0], j[1] - 1, j[2]), (j[0], j[1] + 1, j[2]), deg)


def angles():
    """The three the sketch marks, from the two parameters that set them."""
    return dict(angle1=STEM_TO_HEAD, angle2=180.0 - STEM_TO_HEAD,
                angle3=HEAD_FROM_VERT)


def build():
    """Head and stem are posed independently about the joint, so the piece can be
    laid out by the angles you would measure on it rather than by one rake number.

    The head is modelled with its axis along X and the stem up Z - flat and upright,
    which is Angle 3 = 90 and Angle 1 = 90, the original hammer. Anything else is those
    two parts turned about the joint before they are joined."""
    head_turn = -(90.0 - HEAD_FROM_VERT)          # bowl end lifts as Angle 3 closes
    stem_turn = STEM_ANGLE or (head_turn + (90.0 - STEM_TO_HEAD))
    czb = _interp(0, 0)[2]

    # ---- the head, complete in its own frame ----------------------------
    head = cq.Workplane(obj=head_loft())
    cx = HEAD_X1 - CARB_FROM_RIM
    _, wq, czq = _interp(cx, 0.0)
    yw = wq / 2.0
    boss = (cq.Workplane("XZ").workplane(offset=-(yw - 1.2))
              .center(cx, czq).sphere(CARB_BOSS_D / 2 * 0.86))
    head = head.union(boss)

    r_out_top, r_out_bot = BOWL_ID / 2 + 1.6, BOWL_THROAT / 2 + 1.9
    xr, xt = HEAD_X1 - 1.0, HEAD_X1 - BOWL_DEPTH
    funnel = (cq.Workplane("YZ").workplane(offset=xt)
                .circle(r_out_bot).workplane(offset=(xr - xt)).circle(r_out_top)
                .loft(ruled=False).translate((0, 0, czb)))

    chamber = cq.Workplane(obj=head_loft(inset=WALL, x0=HEAD_X0 + WALL, x1=29.0))
    # bowl bore: cone Ø25 -> Ø3, then the throat down into the chamber
    bore = (cq.Workplane("YZ").workplane(offset=xt)
              .circle(BOWL_THROAT / 2).workplane(offset=(HEAD_X1 + 2 - xt))
              .circle(BOWL_ID / 2).loft(ruled=False).translate((0, 0, czb)))
    throat = (cq.Workplane("YZ").workplane(offset=xt - 8.0)
                .circle(BOWL_THROAT / 2).extrude(9.0).translate((0, 0, czb)))
    carb = (cq.Workplane("XZ").workplane(offset=-40).center(cx, czq)
              .circle(CARB_D / 2).extrude(80))

    # ---- stem and foot ---------------------------------------------------
    stem = (cq.Workplane("XY").circle(STEM_OD / 2).extrude(STEM_TOP)
              .translate((0, 0, 3.0)))
    foot = (cq.Workplane("XY").circle(FOOT_OD / 2).extrude(FOOT_T)
              .edges("|Z or %CIRCLE").fillet(1.6))
    sbore = cq.Workplane("XY").circle(STEM_ID / 2).extrude(STEM_TOP)

    # ---- pose, then join -------------------------------------------------
    head = _pose(head, head_turn)
    chamber, funnel, bore, throat, carb = (
        _pose(x, head_turn) for x in (chamber, funnel, bore, throat, carb))
    stem, foot, sbore = (_pose(x, stem_turn) for x in (stem, foot, sbore))

    body = head.union(stem).union(foot)
    # the chamber is cut after the join, so it opens the stem into the head - that is
    # what connects the two bores. The funnel goes on after that cut, or the chamber
    # hollows out the very cone the funnel is there to make.
    body = body.cut(chamber).union(funnel).cut(bore).cut(throat)
    body = body.cut(sbore).cut(carb)
    return body


if __name__ == "__main__":
    import sys, os
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build()
    solid = m.val()
    print("volume mm^3:", round(solid.Volume(), 1),
          "-> glass mass approx", round(solid.Volume() * 2.23e-3, 1), "g")
    bb = solid.BoundingBox()
    print("bbox  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    a = angles()
    print("angles  1 = %.0f   2 = %.0f   3 = %.0f"
          % (a["angle1"], a["angle2"], a["angle3"]))
    cq.exporters.export(m, os.path.join(out, "clearboy_hammer.step"))
    cq.exporters.export(m, os.path.join(out, "clearboy_hammer.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    print("exported")
