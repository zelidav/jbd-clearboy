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


def bands(n=18, pitch=1.9, minor=0.24, top=88.0, groups=3, gap=4.0):
    """Lay n lines up the body in `groups` bands at the given pitch. Spacing and
    density are what a maker actually varies, so they are the two knobs."""
    n = max(int(n), 0)
    if not n:
        return []
    per = max(n // max(groups, 1), 1)
    out = []
    z = top
    for g in range(groups):
        count = per if g < groups - 1 else max(n - per * (groups - 1), 1)
        z -= (count - 1) * pitch
        out.append((z, count, pitch, minor))
        z -= gap
        if z < 8.0:
            break
    return out


def build(groups=None, proud=0.0):
    parts = []
    for (z0, n, pitch, minor) in (groups or GROUPS):
        for i in range(n):
            major = jar.OD / 2 - minor * 0.45 + proud
            parts.append(ring(z0 + i * pitch, minor, major=major))
    return trimesh.util.concatenate(parts)


def hammer_rings(n=5, pitch=6.0, minor=0.55, start=None, seg=140):
    """Spun linework on the hammer: rings laid round the head while it turns. The
    head is not round, so each ring follows its own section rather than a circle."""
    import decor
    n = max(int(n), 0)
    if not n:
        return trimesh.creation.icosphere(subdivisions=1, radius=0.001)
    x0 = decor.RIM_X - 6.0 if start is None else start
    parts = []
    for i in range(n):
        x = x0 - i * pitch
        for j in range(seg):
            th = 2 * math.pi * j / seg
            p = decor.surface_pt(x, th, out=-minor * 0.45)
            m = trimesh.creation.icosphere(subdivisions=1, radius=minor)
            m.apply_translation(p)
            parts.append(m)
    return trimesh.util.concatenate(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build(bands())
    m.export(os.path.join(out, "jar_lines.stl"))
    # the frit sits about 0.5 proud, so these ride over it
    f = build(GROUPS_FRIT, proud=1.15)
    f.export(os.path.join(out, "jar_lines_frit.stl"))
    h = hammer_rings()
    h.export(os.path.join(out, "hammer_lines.stl"))
    print("linework: %d body rings, %d rings over the frit"
          % (sum(g[1] for g in GROUPS), sum(g[1] for g in GROUPS_FRIT)))
