"""Frit-rolled bowl end + clear marbles, as meshes.

The bowl end of a hot piece is rolled in crushed colour (frit), so the surface goes
granular rather than smooth; a few clear marbles are then pressed into that band.
Both are built straight as meshes - hundreds of grains through an OCC boolean would
take hours and buys nothing, since neither is a machined feature.

    python frit.py out    -> out/frit.stl, out/marbles.stl
"""
import math, os, sys
import numpy as np
import trimesh

from decor import surface_pt, RIM_X

FRIT_X0 = 6.0             # frit band runs from here forward to the rim
FRIT_X1 = RIM_X + 0.5
GRAINS = 520
GRAIN_R = (0.55, 1.25)

MARBLES = [               # (x station, theta, radius)
    (24.0, math.radians(90),  3.8),
    (20.5, math.radians(205), 3.5),
    (26.0, math.radians(325), 3.3),
    (15.5, math.radians(20),  3.2),
]


def _sphere(radius, pos, subdiv=1):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=radius)
    m.apply_translation(pos)
    return m


def build_frit(seed=7):
    rng = np.random.RandomState(seed)
    parts = []
    for _ in range(GRAINS):
        x = FRIT_X0 + (FRIT_X1 - FRIT_X0) * rng.random_sample() ** 0.85
        th = 2 * math.pi * rng.random_sample()
        r = GRAIN_R[0] + (GRAIN_R[1] - GRAIN_R[0]) * rng.random_sample() ** 1.6
        # grains sit half-buried in the skin, denser and prouder toward the rim
        t = (x - FRIT_X0) / (FRIT_X1 - FRIT_X0)
        out = -r * (0.62 - 0.22 * t)
        parts.append(_sphere(r, surface_pt(x, th, out=out)))
    return trimesh.util.concatenate(parts)


def build_marbles():
    return trimesh.util.concatenate(
        [_sphere(r, surface_pt(x, th, out=-r * 0.22), subdiv=2) for (x, th, r) in MARBLES])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    f, m = build_frit(), build_marbles()
    f.export(os.path.join(out, "frit.stl"))
    m.export(os.path.join(out, "marbles.stl"))
    print("frit %d grains / %d faces   marbles %d / %d faces"
          % (GRAINS, len(f.faces), len(MARBLES), len(m.faces)))
