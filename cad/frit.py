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

FRIT_X0 = -22.0            # the whole bowl end, not just the lip
FRIT_X1 = RIM_X + 0.5
GRAINS = 2600
GRAIN_R = (0.50, 1.30)

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
        x = FRIT_X0 + (FRIT_X1 - FRIT_X0) * rng.random_sample() ** 0.62
        th = 2 * math.pi * rng.random_sample()
        r = GRAIN_R[0] + (GRAIN_R[1] - GRAIN_R[0]) * rng.random_sample() ** 1.6
        # grains sit half-buried in the skin, denser and prouder toward the rim
        t = (x - FRIT_X0) / (FRIT_X1 - FRIT_X0)
        out = -r * (0.60 - 0.24 * t)
        parts.append(_sphere(r, surface_pt(x, th, out=out)))
    return trimesh.util.concatenate(parts)


MARBLE_N = len(MARBLES)
MARBLE_SEED = 0          # 0 keeps the hand-placed set; anything else re-scatters


def marble_plan(n=None, seed=None):
    """seed 0 = the placements above. Any other seed scatters n marbles over the
    frit band, which is what a maker does anyway - no two pieces land the same."""
    n = MARBLE_N if n is None else int(n)
    seed = MARBLE_SEED if seed is None else int(seed)
    if not seed:
        return MARBLES[:n]
    rng = np.random.RandomState(seed)
    x0, x1 = FRIT_X1 - 26.0, FRIT_X1 - 4.0
    plan = []
    for i in range(n):
        # spread them round the bowl, then jitter so it never reads as a pattern
        th = 2 * math.pi * ((i + 0.5) / max(n, 1)) + rng.uniform(-0.55, 0.55)
        x = rng.uniform(x0, x1)
        plan.append((x, th, rng.uniform(3.3, 4.2)))
    return plan


def build_marbles(n=None, seed=None):
    plan = marble_plan(n, seed) or [(0.0, 0.0, 0.001)]
    return trimesh.util.concatenate(
        [_sphere(r, surface_pt(x, th, out=-r * 0.20), subdiv=2) for (x, th, r) in plan])


FOOT_Z = (0.5, 9.0)        # the foot disc and the first of the stem
FOOT_R = 12.25             # FOOT_OD / 2
FOOT_GRAINS = 420


def build_foot_frit(seed=13):
    """The foot gets rolled in the same colour, so the piece reads as a pair of ends."""
    rng = np.random.RandomState(seed)
    parts = []
    for _ in range(FOOT_GRAINS):
        t = rng.random_sample()
        z = FOOT_Z[0] + (FOOT_Z[1] - FOOT_Z[0]) * t
        th = 2 * math.pi * rng.random_sample()
        r = GRAIN_R[0] + (GRAIN_R[1] - GRAIN_R[0]) * rng.random_sample() ** 1.6
        rad = (FOOT_R if z < 7.0 else 7.0) - r * 0.55
        parts.append(_sphere(r, (rad * math.cos(th), rad * math.sin(th), z)))
    return trimesh.util.concatenate(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    f = trimesh.util.concatenate([build_frit(), build_foot_frit()])
    m = build_marbles()
    f.export(os.path.join(out, "frit.stl"))
    m.export(os.path.join(out, "marbles.stl"))
    print("frit %d grains / %d faces   marbles %d / %d faces"
          % (GRAINS, len(f.faces), len(MARBLES), len(m.faces)))
