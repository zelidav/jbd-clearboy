"""JBD joint tube - a flat-bottomed glass tube for a single one-gram pre-roll.

The whole industry ships its best joint in a plastic doob tube. It is the cheapest part
of the package and the only part the customer keeps, which is exactly backwards. This is
that tube in hand-blown boro: same job, same one-gram cone, and it lives on the shelf
afterwards instead of in the bin.

Nothing clever in the section - a straight cylinder, 15 mm bore, closed flat so it
stands on a counter - but it is drawn heavy on purpose. The wall is 4.5 mm and the base
is 7, which is roughly twice what a tube this size needs to hold anything. It is not
holding anything: it is surviving being knocked off a counter onto a floor, over and
over, for years. That takes the piece to about 80 g, and the weight is half of why it
feels worth keeping. A one-gram king-size cone is about 109 mm long and 12 mm at the
head, so the bore takes it with room to shake it back out, and the tube runs 124 so the
cork seats clear above the twist rather than on it.

The base carries a wig wag - stringers of colour walked round the tube while they are
run up and down, so they stack into nested chevrons. It is the oldest pattern on the
bench and it belongs at the bottom, where the glass is thickest and it will not fight
the label. Alternate stringers are pulled in two colours, which is what a wig wag is.

Above it the decoration is drips. A band of colour is laid on at the rim and let go: it sags and
runs down the outside in teardrops of its own length, each ending in a bead where it
stopped. Nothing about it is drawn twice the same, which is the point - it is the one
piece of decoration that proves a human stood there and let it happen.

Two marbles, set proud on one side, are the whole anti-roll. Laid down it beds on the
two of them and the far wall - three points - and to roll it has to climb over a stone,
which it will not do on a table. They are set a few degrees apart round the clock rather
than in one straight line: a straight row is one hinge, and a tube will pivot on a hinge.

    python tube.py out   -> out/tube.stl/.step, out/tube_cork.stl,
                            out/tube_marbles.stl, out/tube_drips.stl,
                            out/tube_wig_a.stl, out/tube_wig_b.stl, out/tube_joint.stl
"""
import math, os, sys

import cadquery as cq
import numpy as np
import trimesh

P = dict(
    bore=15.0,            # a one-gram cone is 12 mm at the head - this shakes back out
    wall=4.5,              # heavy. This is a tube that gets dropped on a floor
    height=124.0,         # glass, rim to bench - a 109 cone with the cork clear of it
    floor=7.0,            # flat closed bottom - it stands on it and it lands on it
    lip=1.1,              # rolled rim

    marbles=2,
    marble_r=4.6,
    marble_z=(40.0, 86.0),   # up the tube, low enough that it beds flat
    marble_spread=26.0,      # degrees between the two, so it is a bed and not a hinge

    cork_h=24.0,
    cork_seat=9.0,        # how far down the bore it goes - it must clear the joint
    cork_d_bot=14.4,
    cork_d_top=18.6,

    drips=6,              # runs hanging off the rim band
    drip_r=1.55,          # the band, and the top of each run
    drip_bead=2.10,       # the bead a run ends in where it stopped moving
    drip_min=7.0,         # shortest run
    drip_max=24.0,        # longest - it has to stop clear of the print
    collar_z=4.2,         # how far below the rim the band sits
    drip_seed=7,

    wig=5,                # stringers in the wig wag
    wig_r=0.44,
    wig_z=(4.0, 19.0),    # the band it occupies, up from the bench
    wig_lobes=9,          # chevrons round the tube
    wig_amp=3.5,          # how far each stringer is run up and down
)

# Where the printed label sits on the wall. It runs up the tube, the way the plastic one
# it replaces carries its wordmark along the axis - and it gets the middle of the piece
# to itself: the wig wag stops below it and the drips stop above it. A drip running over
# a label is a drip that was applied after the label, which is not the order anything
# happens in.
LABEL_Z = (48.0, 98.0)

# The maker's mark, pressed into the wall below the print - the same JB stamp the nug
# jar carries, on the same face, so the piece is signed where a piece of glass is
# signed rather than on a sticker that comes off.
STAMP_Z = (23.0, 43.0)


def od(p=None):
    p = dict(P, **(p or {}))
    return p["bore"] + 2 * p["wall"]


def build(p=None):
    p = dict(P, **(p or {}))
    body = cq.Workplane("XY").circle(od(p) / 2).extrude(p["height"])
    bore = (cq.Workplane("XY").workplane(offset=p["floor"])
            .circle(p["bore"] / 2).extrude(p["height"]))
    body = body.cut(bore)
    try:
        body = body.edges("%CIRCLE").fillet(p["lip"])
    except Exception:
        pass
    return body


def build_cork(p=None):
    """One gently tapered natural cork, the same plug the nug jar wears, drawn down to
    this bore. It seats on the taper - no mushroom cap to snap off in a pocket."""
    p = dict(P, **(p or {}))
    z0 = p["height"] - p["cork_seat"]
    cork = (cq.Workplane("XY").workplane(offset=z0)
            .circle(p["cork_d_bot"] / 2)
            .workplane(offset=p["cork_h"]).circle(p["cork_d_top"] / 2)
            .loft(ruled=True))
    try:
        cork = cork.edges(">Z").fillet(1.5)
    except Exception:
        pass
    return cork


def surface_pt(z, theta, out=0.0, p=None):
    r = od(p) / 2 + out
    return (r * math.cos(theta), r * math.sin(theta), z)


def _sphere(r, pos, subdiv=2):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=r)
    m.apply_translation(pos)
    return m


def build_marbles(p=None):
    """Set proud on one side. Proud is the point - a marble sunk flush into the wall is
    decoration, and this one is a foot."""
    p = dict(P, **(p or {}))
    n = int(p["marbles"])
    if n <= 0:
        return trimesh.Trimesh()
    r = p["marble_r"]
    zs = p["marble_z"]
    spread = math.radians(p["marble_spread"])
    out = []
    for i in range(n):
        t = 0.0 if n == 1 else i / (n - 1.0)
        z = zs[0] + (zs[-1] - zs[0]) * t
        # A quarter turn off the print face. Two things had to be true at once: a
        # marble standing proud through a label is a label that will not stick, and a
        # foot you cannot see is a foot nobody believes in. On the side it clears the
        # print and it still reads - broadside, the two of them break the silhouette.
        a = spread * (t - 0.5)
        out.append(_sphere(r, surface_pt(z, a, out=r * 0.40, p=p)))
    return trimesh.util.concatenate(out)


def build_drips(p=None):
    """The band at the rim, and what runs out of it.

    A drip is not a stripe: it is thick where it left the band, thins as gravity pulls
    it, and thickens again into a bead at the bottom where it cooled and stopped. Each
    run gets its own length off one seed, so a colourway is repeatable on the bench and
    no two runs on a piece are the same.

    Returns one mesh - the band and every run - so the whole drip takes a single colour,
    which is how it is actually applied."""
    p = dict(P, **(p or {}))
    n = int(p["drips"])
    r = p["drip_r"]
    top = p["height"] - p["collar_z"]
    parts = []

    # the band: one course of colour laid right round the rim
    steps = 132
    for i in range(steps):
        a = 2 * math.pi * i / steps
        parts.append(_sphere(r, surface_pt(top, a, out=r * 0.42, p=p), subdiv=1))
    if n <= 0:
        return trimesh.util.concatenate(parts)

    rng = np.random.RandomState(int(p["drip_seed"]))
    for i in range(n):
        # walked round the piece rather than dropped at random, so no two runs fuse
        a = 2 * math.pi * i / n + rng.uniform(-0.28, 0.28)
        run = p["drip_min"] + (p["drip_max"] - p["drip_min"]) * rng.random_sample() ** 1.35
        beads = max(int(run / 0.55), 24)
        for k in range(beads + 1):
            t = k / float(beads)
            z = top - run * t
            # thick at the band, drawn thin by the fall, and heavy again at the end
            gr = r * (1.0 - 0.42 * t ** 0.75)
            if t > 0.86:
                u = (t - 0.86) / 0.14
                gr = gr + (p["drip_bead"] - gr) * math.sin(u * math.pi / 2) ** 1.4
            # a run wanders a little as it falls - glass does not fall plumb
            aa = a + 0.055 * math.sin(t * 2.4 + i)
            parts.append(_sphere(gr, surface_pt(z, aa, out=gr * 0.40, p=p), subdiv=1))
    return trimesh.util.concatenate(parts)


def build_wigwag(p=None):
    """Stringers walked round the base while they are run up and down.

    Every stringer carries the same wave, so the peaks line up into chevrons stacked one
    inside the next - a wig wag, the pattern you get from a cane pulled back and forth
    before it is wrapped. Returned as two meshes, alternate stringers in each, so it is
    laid in two colours the way it is on the bench."""
    p = dict(P, **(p or {}))
    n = int(p["wig"])
    if n <= 0:
        return trimesh.Trimesh(), trimesh.Trimesh()
    r = p["wig_r"]
    z0, z1 = p["wig_z"]
    amp, lobes = p["wig_amp"], float(p["wig_lobes"])
    # the band has to hold the wave without the top or bottom stringer breaking out
    span = (z1 - z0) - 2 * amp
    steps = int(lobes * 46)
    a_side, b_side = [], []
    for i in range(n):
        base = z0 + amp + (span * i / (n - 1.0) if n > 1 else span / 2)
        chain = []
        for k in range(steps + 1):
            th = 2 * math.pi * k / steps
            z = base + amp * math.sin(lobes * th)
            chain.append(_sphere(r, surface_pt(z, th, out=r * 0.30, p=p), subdiv=1))
        (a_side if i % 2 == 0 else b_side).append(trimesh.util.concatenate(chain))
    cat = trimesh.util.concatenate
    return (cat(a_side) if a_side else trimesh.Trimesh(),
            cat(b_side) if b_side else trimesh.Trimesh())


# ------------------------------------------------------------------- the joint
J = dict(
    length=109.0,         # a king-size cone, one gram
    crutch_d=7.6,         # the paper tip you hold
    crutch_l=19.0,
    head_d=12.2,          # the packed end
    tip_l=7.0,            # the twist at the top
)


def build_joint(p=None, j=None):
    """A one-gram cone, so the tube can be shown loaded. Not glass - it renders as
    paper: a straight crutch, the cone opening out over it, and a twist at the top."""
    p = dict(P, **(p or {}))
    j = dict(J, **(j or {}))
    z0 = p["floor"] + 0.6
    body = j["length"] - j["tip_l"]
    cone = (cq.Workplane("XY").workplane(offset=z0).circle(j["crutch_d"] / 2)
            .workplane(offset=j["crutch_l"]).circle(j["crutch_d"] / 2)
            .loft(ruled=True))
    cone = cone.union(
        cq.Workplane("XY").workplane(offset=z0 + j["crutch_l"]).circle(j["crutch_d"] / 2)
        .workplane(offset=body - j["crutch_l"]).circle(j["head_d"] / 2).loft(ruled=True))
    # the twist: the head pinched back down to almost nothing
    cone = cone.union(
        cq.Workplane("XY").workplane(offset=z0 + body).circle(j["head_d"] / 2)
        .workplane(offset=j["tip_l"]).circle(0.9).loft(ruled=True))
    try:
        cone = cone.edges("<Z").fillet(0.8)
    except Exception:
        pass
    return cone


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    t, c = build(), build_cork()
    print("tube glass mm^3:", round(t.val().Volume(), 1),
          "-> approx", round(t.val().Volume() * 2.23e-3, 1), "g")
    print("cork mm^3:", round(c.val().Volume(), 1),
          "-> approx", round(c.val().Volume() * 0.24e-3, 1), "g")
    bb = t.val().BoundingBox()
    print("bbox  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    cq.exporters.export(t, os.path.join(out, "tube.step"))
    cq.exporters.export(t, os.path.join(out, "tube.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    cq.exporters.export(c, os.path.join(out, "tube_cork.step"))
    cq.exporters.export(c, os.path.join(out, "tube_cork.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    j = build_joint()
    cq.exporters.export(j, os.path.join(out, "tube_joint.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    build_marbles().export(os.path.join(out, "tube_marbles.stl"))
    build_drips().export(os.path.join(out, "tube_drips.stl"))
    wa, wb = build_wigwag()
    wa.export(os.path.join(out, "tube_wig_a.stl"))
    wb.export(os.path.join(out, "tube_wig_b.stl"))
    print("tube %.0f OD x %.0f, bore %.0f, %d marbles, %d drips, %d-line wig wag, "
          "cork %.0f tall" % (od(), P["height"], P["bore"], P["marbles"], P["drips"],
                              P["wig"], P["cork_h"]))
