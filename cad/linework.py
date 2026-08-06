"""Wrapped linework - the banded rings on the classic JB jar.

Fine colour lines laid on while the piece turns on the lathe, so they sit as thin
raised rings around the body: a few groups, unevenly spaced, some heavier than
others. Built as meshes; nothing here is a machined feature.

    python linework.py out    -> out/jar_lines.stl
"""
import math, os, sys
import numpy as np
import trimesh

import jar

# (centre z, minor radius) - grouped the way a maker actually lays them down
# matched to assets/jb_jar_linework.png: fine lines, tight pitch, grouped in bands
# the lines sit on the upper half, the way they do on the reference jar - the lower
# body stays clear so the maker's stamp has somewhere to live
GROUPS = [
    (46.0, 5, 1.9, 0.26),      # z start, count, pitch, thickness
    (57.0, 9, 1.7, 0.22),
    (74.0, 4, 2.2, 0.30),
]


def ring(z, minor, major=None, sections=96, minor_sections=10):
    major = jar.OD / 2 - minor * 0.45 if major is None else major
    m = trimesh.creation.torus(major_radius=major, minor_radius=minor,
                               major_sections=sections, minor_sections=minor_sections)
    m.apply_translation([0.0, 0.0, z])
    return m


# over the frit band, for the coloured builds: clear lines laid over the colour
GROUPS_FRIT = [
    (67.0, 4, 2.4, 0.46),
    (77.0, 6, 2.0, 0.38),
    (88.0, 2, 2.2, 0.55),
]


def bands(n=26, pitch=1.9, minor=0.24, top=88.0, bottom=6.0, seed=5):
    """n lines down the whole body at roughly the given pitch, jittered: a lathe line
    is never evenly spaced and never quite the same weight twice."""
    n = max(int(n), 0)
    if not n:
        return []
    rng = np.random.RandomState(seed)
    span = max(top - bottom, 1.0)
    out = []
    z = top
    for i in range(n):
        step = pitch * rng.uniform(0.55, 1.85)          # uneven spacing
        if rng.random_sample() < 0.16:
            step *= rng.uniform(2.0, 3.4)              # the odd gap between groups
        z -= step
        if z < bottom:
            z = bottom + (span * rng.random_sample() * 0.12)
        out.append((z, 1, pitch, minor * rng.uniform(0.62, 1.55)))   # uneven weight
    return out


def build(groups=None, proud=0.0):
    parts = []
    for (z0, n, pitch, minor) in (groups or GROUPS):
        for i in range(n):
            major = jar.OD / 2 - minor * 0.45 + proud
            parts.append(ring(z0 + i * pitch, minor, major=major))
    return trimesh.util.concatenate(parts)


def hammer_rings(n=9, pitch=5.0, minor=0.5, start=None, seg=150, seed=3, foot=True):
    """Spun linework on the hammer: rings laid round the head while it turns, plus a
    few round the foot. The head is not round, so each ring follows its own section.
    Spacing and weight are jittered - it is hand work."""
    import decor
    n = max(int(n), 0)
    parts = []
    rng = np.random.RandomState(seed)
    if n:
        x = (decor.RIM_X - 3.0) if start is None else start
        for i in range(n):
            x -= pitch * rng.uniform(0.6, 1.7)
            if x < -34.0:
                break
            r = minor * rng.uniform(0.62, 1.5)
            for j in range(seg):
                th = 2 * math.pi * j / seg
                m = trimesh.creation.icosphere(subdivisions=1, radius=r)
                m.apply_translation(decor.surface_pt(x, th, out=-r * 0.45))
                parts.append(m)
    if foot and n:
        for k in range(max(n // 3, 2)):
            z = 1.6 + k * 2.1 * rng.uniform(0.8, 1.4)
            if z > 8.5:
                break
            r = minor * rng.uniform(0.6, 1.3)
            rad = 12.25 - r * 0.5
            for j in range(seg):
                th = 2 * math.pi * j / seg
                m = trimesh.creation.icosphere(subdivisions=1, radius=r)
                m.apply_translation((rad * math.cos(th), rad * math.sin(th), z))
                parts.append(m)
    if not parts:
        return trimesh.creation.icosphere(subdivisions=1, radius=0.001)
    return trimesh.util.concatenate(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build(bands())
    m.export(os.path.join(out, "jar_lines.stl"))
    # the frit sits about 0.5 proud, so these ride over it
    f = build(GROUPS_FRIT, proud=1.15)   # over the frit, for the coloured builds
    f.export(os.path.join(out, "jar_lines_frit.stl"))
    h = hammer_rings()
    h.export(os.path.join(out, "hammer_lines.stl"))
    print("linework: %d body rings, %d rings over the frit"
          % (sum(g[1] for g in GROUPS), sum(g[1] for g in GROUPS_FRIT)))
