"""JBD stash jar - 38 mm opening, 3 mm wall, embossed JBD stamp.

Same glass programme as the hammer: fumed body, frit-rolled shoulder, clear marbles
set evenly around the rim.

    python jar.py out   -> out/jar.stl/.step, out/jar_frit.stl, out/jar_marbles.stl
"""
import math, os, sys
import cadquery as cq
import numpy as np
import trimesh

MOUTH_ID = 38.0            # the spec: 38 mm opening
WALL     = 3.0
NECK_OD  = MOUTH_ID + 2 * WALL
BODY_OD  = 66.0
HEIGHT   = 92.0

# outer profile: (z, outer radius)
PROFILE = [
    (0.0,  30.0), (3.0,  32.6), (8.0,  33.0), (52.0, 33.0), (63.0, 32.4),
    (70.0, 30.2), (76.0, 26.6), (80.5, 23.6), (84.0, NECK_OD / 2),
    (88.0, NECK_OD / 2), (90.0, NECK_OD / 2 + 1.1), (92.0, NECK_OD / 2 + 1.1),
]

STAMP_Z   = 30.0           # centre of the embossed medallion
STAMP_R   = 15.0           # medallion radius
STAMP_TXT = "JBD"

FRIT_Z    = (62.0, 89.0)   # frit band: shoulder up over the neck
GRAINS    = 620
GRAIN_R   = (0.55, 1.25)
N_MARBLES = 7              # evenly spaced around the rim
MARBLE_R  = 4.0
MARBLE_Z  = 79.0


def radius_at(z):
    zs = [p[0] for p in PROFILE]
    if z <= zs[0]:  return PROFILE[0][1]
    if z >= zs[-1]: return PROFILE[-1][1]
    i = max(j for j in range(len(zs)) if zs[j] <= z)
    i = min(i, len(PROFILE) - 2)
    (z0, r0), (z1, r1) = PROFILE[i], PROFILE[i + 1]
    return r0 + (r1 - r0) * (z - z0) / (z1 - z0)


def build():
    # loft through the profile circles
    wires = [cq.Wire.makeCircle(r, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
             for (z, r) in PROFILE]
    body = cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=False))

    # cavity: same profile pulled in by the wall, open at the top
    inner = [(max(z - WALL, 0.0), max(r - WALL, 0.5)) for (z, r) in PROFILE if z >= WALL]
    inner = [(WALL, radius_at(WALL) - WALL)] + inner
    iw = [cq.Wire.makeCircle(r, cq.Vector(0, 0, z), cq.Vector(0, 0, 1))
          for (z, r) in inner]
    cavity = cq.Workplane(obj=cq.Solid.makeLoft(iw, ruled=False))
    # extend the cavity out of the top so the mouth is genuinely open
    cavity = cavity.union(cq.Workplane("XY").circle(MOUTH_ID / 2)
                          .extrude(12.0).translate((0, 0, HEIGHT - 10.0)))
    body = body.cut(cavity)

    # embossed medallion + JBD, on the front (-Y) face
    rs = radius_at(STAMP_Z)
    pad = (cq.Workplane("XZ").workplane(offset=rs - 1.4).center(0, STAMP_Z)
             .circle(STAMP_R).extrude(-3.2))
    body = body.union(pad)
    txt = (cq.Workplane("XZ").workplane(offset=rs + 1.8).center(0, STAMP_Z)
             .text(STAMP_TXT, 13.0, -1.6, kind="bold",
                   halign="center", valign="center"))
    body = body.union(txt)
    return body


def _sphere(radius, pos, subdiv=1):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=radius)
    m.apply_translation(pos)
    return m


def surface_pt(z, theta, out=0.0):
    r = radius_at(z) + out
    return (r * math.cos(theta), r * math.sin(theta), z)


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
    j = build()
    solid = j.val()
    print("jar volume mm^3:", round(solid.Volume(), 1),
          "-> glass approx", round(solid.Volume() * 2.23e-3, 1), "g")
    bb = solid.BoundingBox()
    print("bbox X %.1f..%.1f Z %.1f..%.1f" % (bb.xmin, bb.xmax, bb.zmin, bb.zmax))
    cq.exporters.export(j, os.path.join(out, "jar.step"))
    cq.exporters.export(j, os.path.join(out, "jar.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    f, m = build_frit(), build_marbles()
    f.export(os.path.join(out, "jar_frit.stl"))
    m.export(os.path.join(out, "jar_marbles.stl"))
    print("frit %d grains, %d marbles" % (GRAINS, N_MARBLES))
