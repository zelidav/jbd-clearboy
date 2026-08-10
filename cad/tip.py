"""JBD glass tip - a reusable filter tip for a joint.

Nineteen millimetres of 9 mm tube with a perforated screen across the bore, so it filters
and it does not collapse the way a rolled card crutch does.

The idea is the slot. A rolling paper is a nuisance to start against a smooth tip: you are
holding paper, tobacco and a slippery cylinder and trying to get the first wrap to bite.
So the outside carries a slot that runs the length of the tube, parallel to the axis. The
cut into it is what is oblique: the blade goes in raked seventy degrees off the radius, so
the slot leans and undercuts, and the paper it takes does not fall straight back out. A
radial nick of the same depth would.

Shallow, too. Nought point nine into a one point three wall leaves the bore sealed - a
slot that broke through would pull smoke past the screen, and would be a weak line to
anneal across.

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

    groove_rake=70.0,     # off the radius. 0 is a plain radial nick, 70 nearly tangent
    groove_w=0.75,        # slot width - a paper is nothing, the finger is the limit
    groove_depth=0.9,     # into the 1.3 wall, not through it - the bore stays sealed
    groove_run=0.72,      # how much of the length the slot runs, as a fraction
    groove_z=9.5,         # centre of the run
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


# ---------------------------------------------------------------- the coil

S = dict(
    length=19.0,
    od=9.0,               # outside of the coil
    rod=1.7,              # the section of glass being wound
    turns=6.5,
    end_rings=1.0,        # a closed ring at each end so it does not splay
)


def build_spiral(p=None):
    """The other way to do it: no tube at all, just a length of rod wound into a coil
    that is open end to end.

    The gap between the turns is the slot, and it runs the whole piece - the paper goes
    into the outer ring of the spiral anywhere along it rather than hunting for the one
    slot. Lighter, draws freely because it is all gap, and there is nothing to clog.
    What it gives up is the screen: a coil cannot carry one, so it is a grip and a heat
    break rather than a filter.

    Wound as a mesh. Sweeping a circle along an OCC helix came back inside out - a
    negative volume - and a coil is a swept tube, which is a thing a mesh does honestly.
    No STEP for this one until the sweep is sound."""
    p = dict(S, **(p or {}))
    r = (p["od"] - p["rod"]) / 2.0
    rod = p["rod"] / 2.0
    turns = max(p["turns"], 0.5)
    steps = int(turns * 96)
    z0, z1 = rod, p["length"] - rod
    beads = []
    for i in range(steps + 1):
        t = i / float(steps)
        a = 2 * math.pi * turns * t
        beads.append(_bead(rod, (r * math.cos(a), r * math.sin(a), z0 + (z1 - z0) * t)))
    if p["end_rings"]:
        for z in (z0, z1):
            ring = trimesh.creation.torus(r, rod, major_sections=96, minor_sections=16)
            ring.apply_translation((0, 0, z))
            beads.append(ring)
    return trimesh.util.concatenate(beads)


def _bead(r, pos):
    m = trimesh.creation.icosphere(subdivisions=2, radius=r)
    m.apply_translation(pos)
    return m


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
    print("spiral volume mm^3:", round(c.volume, 1),
          "-> approx", round(c.volume * 2.23e-3, 2), "g  (mesh only, no STEP yet)")
    c.export(os.path.join(out, "tip_spiral.stl"))
    print("exported")
