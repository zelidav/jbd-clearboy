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
GROUPS = [
    (20.0, 5, 2.6, 0.42),      # z start, count, pitch, thickness
    (34.0, 3, 3.4, 0.62),
    (43.0, 7, 2.1, 0.34),
    (57.0, 2, 4.0, 0.75),
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


def build(groups=None, proud=0.0):
    parts = []
    for (z0, n, pitch, minor) in (groups or GROUPS):
        for i in range(n):
            major = jar.OD / 2 - minor * 0.45 + proud
            parts.append(ring(z0 + i * pitch, minor, major=major))
    return trimesh.util.concatenate(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build()
    m.export(os.path.join(out, "jar_lines.stl"))
    # the frit sits about 0.5 proud, so these ride over it
    f = build(GROUPS_FRIT, proud=1.15)
    f.export(os.path.join(out, "jar_lines_frit.stl"))
    print("linework: %d body rings, %d rings over the frit"
          % (sum(g[1] for g in GROUPS), sum(g[1] for g in GROUPS_FRIT)))
