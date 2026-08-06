"""JBD nug jar - straight cylinder, flat closed bottom, cork lid.

38 mm opening, 3 mm wall, so the tube runs 44 mm OD from the base to the rim. Embossed
JBD medallion on the front. Frit-rolled band under the rim with clear marbles set evenly
around it, matching the hammer.

    python jar.py out   -> out/jar.stl/.step, out/jar_frit.stl, out/jar_marbles.stl,
                           out/jar_cork.stl
"""
import math, os, sys
import cadquery as cq
import numpy as np
import trimesh

MOUTH_ID  = 38.0           # the spec: 38 mm opening
WALL      = 3.0
OD        = MOUTH_ID + 2 * WALL      # 44 - straight cylinder, no shoulder
HEIGHT    = 92.0           # glass body, rim to bench
FLOOR     = 3.0            # flat closed bottom, same wall

STAMP_Z   = 28.0           # lower middle of the jar, like the real maker's stamp
STAMP_RX  = 13.0           # the pad is a squashed gather, wider than tall
STAMP_RZ  = 9.0
STAMP_TXT = "JBD"
STAMP_SINK = 0.5           # how deep the stamp pad is pressed into the wall

FRIT_Z    = (66.0, 90.5)   # frit band around the opening
GRAINS    = 520
GRAIN_R   = (0.55, 1.25)
N_MARBLES = 7              # evenly spaced around the opening
MARBLE_R  = 4.0
MARBLE_Z  = 84.5

# a natural cork: one gently tapered plug, no mushroom cap. It seats on the taper.
CORK_H       = 27.0        # overall length of the cork
CORK_D_BOT   = 36.6        # bottom, inside the neck
CORK_D_TOP   = 41.0        # top, just proud of the rim
CORK_SEAT    = 15.0        # how far it sits down in the mouth


def build():
    body = cq.Workplane("XY").circle(OD / 2).extrude(HEIGHT)
    bore = (cq.Workplane("XY").workplane(offset=FLOOR)
              .circle(MOUTH_ID / 2).extrude(HEIGHT))
    body = body.cut(bore)
    body = body.edges("|Z or %CIRCLE").fillet(1.2)

    # maker's stamp, pressed into the wall: a shallow blob-shaped depression with
    # the letters struck deeper inside it. Nothing stands proud of the cylinder.
    body = body.cut(cq.Workplane(obj=stamp_pad()))
    face = OD / 2 - STAMP_SINK
    txt = (cq.Workplane("XZ").workplane(offset=face).center(0, STAMP_Z)
             .text(STAMP_TXT, 10.0, -1.4, kind="bold", halign="center", valign="center"))
    return body.cut(txt)


def stamp_pad(depth=7.0, wobble=0.15):
    """Irregular, molten-edged blob - a hand-pressed stamp is never a clean circle.
    Used as a cutter: it takes the outer skin off down to STAMP_SINK."""
    pts = []
    n = 72
    for i in range(n):
        t = 2 * math.pi * i / n
        k = 1.0 + wobble * math.sin(3 * t + 0.7) + 0.5 * wobble * math.sin(5 * t + 2.1)
        pts.append(cq.Vector(STAMP_RX * k * math.cos(t),
                             -(OD / 2 - STAMP_SINK),
                             STAMP_Z + STAMP_RZ * k * math.sin(t)))
    wire = cq.Wire.assembleEdges([cq.Edge.makeSpline(pts, periodic=True)])
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), cq.Vector(0, -depth, 0))


def build_cork():
    """One slightly tapered natural cork - wider at the top, softened at both ends."""
    z0 = HEIGHT - CORK_SEAT
    cork = (cq.Workplane("XY").workplane(offset=z0)
              .circle(CORK_D_BOT / 2).workplane(offset=CORK_H).circle(CORK_D_TOP / 2)
              .loft(ruled=True))
    return cork.edges(">Z").fillet(1.8)


def radius_at(z):
    return OD / 2


def surface_pt(z, theta, out=0.0):
    r = radius_at(z) + out
    return (r * math.cos(theta), r * math.sin(theta), z)


def _sphere(radius, pos, subdiv=1):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=radius)
    m.apply_translation(pos)
    return m


def build_frit(seed=11):
    rng = np.random.RandomState(seed)
    parts = []
    for _ in range(GRAINS):
        t = rng.random_sample() ** 0.8
        z = FRIT_Z[0] + (FRIT_Z[1] - FRIT_Z[0]) * t
        th = 2 * math.pi * rng.random_sample()
        r = GRAIN_R[0] + (GRAIN_R[1] - GRAIN_R[0]) * rng.random_sample() ** 1.6
        parts.append(_sphere(r, surface_pt(z, th, out=-r * (0.62 - 0.20 * t))))
    return trimesh.util.concatenate(parts)


def build_marbles():
    return trimesh.util.concatenate([
        _sphere(MARBLE_R, surface_pt(MARBLE_Z, 2 * math.pi * i / N_MARBLES,
                                     out=-MARBLE_R * 0.30), subdiv=2)
        for i in range(N_MARBLES)])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    j, c = build(), build_cork()
    print("jar glass mm^3:", round(j.val().Volume(), 1),
          "-> approx", round(j.val().Volume() * 2.23e-3, 1), "g")
    print("cork mm^3:", round(c.val().Volume(), 1),
          "-> approx", round(c.val().Volume() * 0.24e-3, 1), "g")
    cq.exporters.export(j, os.path.join(out, "jar.step"))
    cq.exporters.export(j, os.path.join(out, "jar.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    cq.exporters.export(c, os.path.join(out, "jar_cork.step"))
    cq.exporters.export(c, os.path.join(out, "jar_cork.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    build_frit().export(os.path.join(out, "jar_frit.stl"))
    build_marbles().export(os.path.join(out, "jar_marbles.stl"))
    print("straight cylinder %.0f OD x %.0f, %d grains, %d marbles, cork %.0f tall"
          % (OD, HEIGHT, GRAINS, N_MARBLES, CORK_H))
