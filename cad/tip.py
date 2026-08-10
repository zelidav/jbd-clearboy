"""JBD glass tip - a reusable filter tip for a joint.

Nineteen millimetres of 9 mm tube with a perforated screen across the bore, so it filters
and it does not collapse the way a rolled card crutch does.

The idea is the slot. A rolling paper is a nuisance to start against a smooth tip: you are
holding paper, tobacco and a slippery cylinder and trying to get the first wrap to bite.
So the outside carries a slot that runs the length of the tube, parallel to the axis. The
cut into it is what is oblique: the blade goes in raked seventy degrees off the radius, so
the slot leans and undercuts, and the paper it takes does not fall straight back out. A
radial nick of the same depth would.

It has to be long enough to be worth anything: three millimetres of paper goes into it.
That is length along the slot, not depth into the wall - raked at seventy-eight degrees
the radial bite is only six tenths, which is why the tube is drawn thick-walled at two
millimetres. The bore stays sealed. A slot that broke through would pull smoke past the
screen and would be a weak line to anneal across.

And it runs the full length and out both ends. The paper is held along its whole edge or
it is not held.

    python tip.py out   -> out/tip.stl/.step, out/tip_screen.stl
"""
import math, os, sys

import cadquery as cq
import numpy as np
import trimesh

P = dict(
    length=19.0,          # 0.75 in
    od=9.0,
    bore=5.0,             # 2.0 wall - thick, so the slot can be long enough to grip
    lip=0.5,              # the ends are rolled, not cut square

    screen_z=6.5,         # how far in the screen sits, from the mouth end
    screen_t=1.5,
    screen_holes=7,
    screen_hole_d=1.25,
    screen_ring=2.05,     # radius the outer ring of holes sits on

    groove_rake=78.0,     # off the radius. 0 is a plain radial nick, 78 well over
    groove_w=0.75,        # slot width - a paper is nothing, the finger is the limit
    groove_depth=3.0,     # how far the paper goes IN, measured along the slot. Two to
                          # four is what actually holds; the radial bite is this times
                          # cos(rake), so at 78 degrees 3 mm of grip is 0.6 into the wall
    groove_run=1.3,       # >1: the slot breaks out both ends. It has to - the
                          # paper is held along its whole edge or it is not held
    groove_z=9.5,         # centre of the run
    cut=0.0,              # >0 keeps this fraction of the length - a section view
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
    """The slot runs along the tube, parallel to the axis. What is oblique is the cut
    itself: the blade goes in raked well off the radius rather than straight at the
    centre, so the slot leans and undercuts. That lean is what holds the paper - a
    radial nick of the same depth would let it fall straight back out."""
    w, d = p["groove_w"], p["groove_depth"]
    run = p["length"] * p["groove_run"]
    rake = math.radians(p["groove_rake"])
    reach = p["od"] * 3.0
    # thin in X (the slot width), long in Y (the direction it drives in), long in Z
    blade = cq.Workplane("XY").box(w, reach, run, centered=(True, True, True))
    # spin it about its OWN centre, not about a line it does not sit on, then walk it
    # back along its own axis so exactly `d` of it ends up inside the wall
    # -rake, so the slab's thin face becomes the slot wall and its long axis becomes
    # the direction the blade drives in
    blade = blade.rotate((0, 0, 0), (0, 0, 1), -p["groove_rake"])
    u = (math.sin(rake), math.cos(rake))          # inward, leaned off the radius
    back = reach / 2.0 - d
    return blade.translate((-u[0] * back, -p["od"] / 2 - u[1] * back, p["groove_z"]))


def _section(body, p, span):
    """Trim to the front of the piece so the cut face shows the wall, the slot and
    what is sitting in it."""
    keep = span * p["cut"]
    box = (cq.Workplane("XY").workplane(offset=keep)
           .box(span * 4, span * 4, span * 4, centered=(True, True, False)))
    return body.cut(box)


def build(p=None):
    p = dict(P, **(p or {}))
    body = _tube(p).union(_screen(p))
    if p["groove_depth"] > 0:
        body = body.cut(_groove_cutter(p))
    if p.get("cut"):
        body = _section(body, p, p["length"])
    return body


def build_screen_mesh(p=None):
    """The screen on its own, so the render can give it its own material - it wants to
    read as glass with holes in it, not as part of the wall."""
    p = dict(P, **(p or {}))
    import tempfile
    f = os.path.join(tempfile.gettempdir(), "jbd_tip_screen.stl")
    cq.exporters.export(_screen(p), f, tolerance=0.02, angularTolerance=0.1)
    return trimesh.load(f)


# ---------------------------------------------------------------- the coil

S = dict(
    length=19.0,          # 0.75 in - what one cut length of the rolled stock gives
    od=9.0,               # outside of the roll
    sheet=0.80,           # thickness of the sheet being rolled
    gap=0.55,             # air left between one wrap and the next
    core=1.10,            # the hole left in the middle
    steps=520,            # how finely the spiral is walked
    cut=0.0,
)


def build_spiral(p=None):
    """The other way to do it: not a tube at all, and not a coil of rod.

    Take a thin sheet of glass, roll it into a 9 mm cylinder the way you would roll a
    poster, and cut the stock into three-quarter-inch lengths. The section is an
    archimedean spiral - one continuous ribbon wound round itself with air between the
    wraps.

    Two things fall out of that. The gap between wraps is a channel that runs the whole
    length, so it draws through the spiral rather than down one bore, and the free edge
    of the sheet leaves an opening at the outer ring that runs the full length too -
    that opening is the paper slot, and it is the same slot everywhere along the piece
    rather than one groove you have to find.

    It also cuts cheaply: the roll is drawn as stock and chopped, so a length of it is
    many tips."""
    p = dict(S, **(p or {}))
    t, g = p["sheet"], p["gap"]
    r0, r1 = p["core"], p["od"] / 2.0 - t
    pitch = t + g                                   # radius gained per turn
    turns = max((r1 - r0) / pitch, 0.6)
    n = int(p["steps"])
    th = [2 * math.pi * turns * i / float(n) for i in range(n + 1)]

    def at(a, off):
        r = r0 + pitch * a / (2 * math.pi) + off
        return (r * math.cos(a), r * math.sin(a))

    inner = [at(a, 0.0) for a in th]
    outer = [at(a, t) for a in reversed(th)]
    ring = (cq.Workplane("XY").polyline(inner + outer).close()
            .extrude(p["length"]))
    if p.get("cut"):
        ring = _section(ring, p, p["length"])
    return ring


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
    c = build_spiral()
    cv = c.val().Volume()
    print("spiral volume mm^3:", round(cv, 1),
          "-> glass mass approx", round(cv * 2.23e-3, 2), "g")
    cq.exporters.export(c, os.path.join(out, "tip_spiral.step"))
    cq.exporters.export(c, os.path.join(out, "tip_spiral.stl"),
                        tolerance=0.02, angularTolerance=0.1)
    print("exported")
