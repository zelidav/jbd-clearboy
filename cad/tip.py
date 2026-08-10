"""JBD glass tip - a reusable filter tip for a joint.

Nineteen millimetres of 9 mm tube with a perforated screen across the bore, so it filters
and it does not collapse the way a rolled card crutch does.

The idea is the slot. A rolling paper is a nuisance to start against a smooth tip: you are
holding paper, tobacco and a slippery cylinder and trying to get the first wrap to bite.
So the outside carries a groove cut at a very oblique angle - almost along the tube rather
than around it. The leading edge of the paper slips into that groove, the groove holds it,
and rolling the tip winds the paper on. Because the groove is raked rather than square to
the axis, the first wrap starts slightly off-square, which is exactly the bias a cone
wants.

    python tip.py out   -> out/tip.stl/.step, out/tip_screen.stl
"""
import math, os, sys

import cadquery as cq
import numpy as np
import trimesh

P = dict(
    length=19.0,          # 0.75 in
    od=9.0,
    bore=6.4,             # 1.3 wall
    lip=0.5,              # the ends are rolled, not cut square

    screen_z=6.5,         # how far in the screen sits, from the mouth end
    screen_t=1.5,
    screen_holes=7,
    screen_hole_d=1.25,
    screen_ring=2.05,     # radius the outer ring of holes sits on

    groove_deg=68.0,      # from the tube axis. High is oblique, 90 would be a ring
    groove_w=0.75,        # slot width - a paper is nothing, the finger is the limit
    groove_depth=1.9,     # past the wall, so the paper tucks through and is held
    groove_z=9.5,         # where the slot crosses the axis
)


def _tube(p):
    body = cq.Workplane("XY").circle(p["od"] / 2).extrude(p["length"])
    body = body.cut(cq.Workplane("XY").workplane(offset=-1)
                    .circle(p["bore"] / 2).extrude(p["length"] + 2))
    if p["lip"]:
        body = body.edges("%CIRCLE").fillet(p["lip"])
    return body


def _screen(p):
    """A disc across the bore with a ring of holes and one in the middle - the classic
    screen pattern, and the one that does not choke."""
    d = (cq.Workplane("XY").workplane(offset=p["screen_z"])
         .circle(p["bore"] / 2 + 0.15).extrude(p["screen_t"]))
    n = int(p["screen_holes"])
    r = p["screen_hole_d"] / 2
    holes = []
    if n > 0:
        holes.append((0.0, 0.0))
        for i in range(n - 1):
            a = 2 * math.pi * i / float(n - 1)
            holes.append((p["screen_ring"] * math.cos(a), p["screen_ring"] * math.sin(a)))
    for (x, y) in holes:
        d = d.cut(cq.Workplane("XY").workplane(offset=p["screen_z"] - 1)
                  .center(x, y).circle(r).extrude(p["screen_t"] + 2))
    return d


def _groove_cutter(p):
    """The slot, as the tool that makes it: a channel `groove_w` wide and `groove_depth`
    deep, run diagonally across the face of the tube.

    groove_deg is measured off the tube axis, so 0 would be a slot straight down the
    length and 90 a ring right round it. Sixty-eight is the oblique the paper wants -
    long enough to take an edge, raked enough to start the wrap off-square."""
    w, d = p["groove_w"], p["groove_depth"]
    reach = p["length"] * 2.6
    # long in X, w across the slot, and 2d through the wall so it is centred on the
    # surface and cuts exactly `d` in
    blade = cq.Workplane("XY").box(reach, 2 * d, w, centered=(True, True, True))
    blade = blade.rotate((0, 0, 0), (0, 1, 0), p["groove_deg"])
    return blade.translate((0, -p["od"] / 2, p["groove_z"]))


def build(p=None):
    p = dict(P, **(p or {}))
    body = _tube(p).union(_screen(p))
    if p["groove_depth"] > 0:
        body = body.cut(_groove_cutter(p))
    return body


def build_screen_mesh(p=None):
    """The screen on its own, so the render can give it its own material - it wants to
    read as glass with holes in it, not as part of the wall."""
    p = dict(P, **(p or {}))
    import tempfile
    f = os.path.join(tempfile.gettempdir(), "jbd_tip_screen.stl")
    cq.exporters.export(_screen(p), f, tolerance=0.02, angularTolerance=0.1)
    return trimesh.load(f)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build()
    solid = m.val()
    print("volume mm^3:", round(solid.Volume(), 1),
          "-> glass mass approx", round(solid.Volume() * 2.23e-3, 2), "g")
    bb = solid.BoundingBox()
    print("bbox  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    cq.exporters.export(m, os.path.join(out, "tip.step"))
    cq.exporters.export(m, os.path.join(out, "tip.stl"),
                        tolerance=0.02, angularTolerance=0.1)
    print("exported")
