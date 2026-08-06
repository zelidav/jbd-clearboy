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


def spiral(turns=42, pitch=1.9, minor=0.62, top=88.0, bottom=5.0, seed=7,
           per_turn=110, proud=0.0, radius=None):
    """Colour dripped onto a spinning jar: one continuous run down the body, its
    pitch drifting and its thickness swelling and thinning as the glass flows."""
    turns = max(float(turns), 0.0)
    if turns <= 0:
        return trimesh.creation.icosphere(subdivisions=1, radius=0.001)
    n = max(int(turns * per_turn), 8)
    t = np.linspace(0.0, 1.0, n)
    rng = np.random.RandomState(seed)
    theta = 2 * math.pi * turns * t + rng.uniform(0, 2 * math.pi)
    drop = turns * pitch
    z = top - drop * (t + 0.035 * np.sin(2.7 * math.pi * t + rng.uniform(0, 6))
                        + 0.018 * np.sin(6.3 * math.pi * t + rng.uniform(0, 6)))
    z = np.clip(z, bottom, top)
    r = np.clip(minor * viscosity(t, seed), minor * 0.35, minor * 1.9)
    R = (jar.OD / 2 if radius is None else radius) - r * 0.18 + proud
    path = np.column_stack([R * np.cos(theta), R * np.sin(theta), z])
    return tube_var(path, r, up=(0.0, 0.0, 1.0))


def build(groups=None, proud=0.0):
    parts = []
    for (z0, n, pitch, minor) in (groups or GROUPS):
        for i in range(n):
            major = jar.OD / 2 - minor * 0.45 + proud
            parts.append(ring(z0 + i * pitch, minor, major=major))
    return trimesh.util.concatenate(parts)


def tube_var(path, radii, sections=12, up=(1.0, 0.0, 0.0)):
    """Sweep a tube whose radius changes along the path - a dripped line swells and
    thins as the glass runs, it is never a constant cylinder."""
    P = np.asarray(path, "f8")
    R = np.asarray(radii, "f8")
    n = len(P)
    T = np.empty_like(P)
    T[1:-1] = P[2:] - P[:-2]
    T[0] = P[1] - P[0]
    T[-1] = P[-1] - P[-2]
    T /= np.maximum(np.linalg.norm(T, axis=1)[:, None], 1e-9)
    U = np.cross(T, np.asarray(up, "f8"))
    lens = np.linalg.norm(U, axis=1)[:, None]
    U = np.where(lens > 1e-6, U / np.maximum(lens, 1e-9), np.array([0.0, 0.0, 1.0]))
    V = np.cross(T, U)
    a = np.linspace(0, 2 * math.pi, sections, endpoint=False)
    ca, sa = np.cos(a)[:, None], np.sin(a)[:, None]
    verts = np.empty((n, sections, 3))
    for i in range(n):
        verts[i] = P[i] + R[i] * (ca * U[i] + sa * V[i])
    faces = []
    for i in range(n - 1):
        for k in range(sections):
            l = (k + 1) % sections
            faces.append([i * sections + k, (i + 1) * sections + k, (i + 1) * sections + l])
            faces.append([i * sections + k, (i + 1) * sections + l, i * sections + l])
    f = np.asarray(faces)
    # point the winding outwards: the renderer culls back faces, and a sweep built the
    # wrong way round vanishes when you look straight at it
    W = verts.reshape(-1, 3)
    tri = W[f[0]]
    nrm = np.cross(tri[1] - tri[0], tri[2] - tri[0])
    outward = W[f[0][0]] - P[0]
    if float(np.dot(nrm, outward)) < 0.0:
        f = f[:, ::-1]
    return trimesh.Trimesh(vertices=W, faces=f, process=False)


def viscosity(t, seed=0):
    """A smooth, non-repeating swell/thin along the run, in roughly 0.45 - 1.6."""
    rng = np.random.RandomState(seed)
    ph = rng.uniform(0, 2 * math.pi, 4)
    v = (0.55 * np.sin(5.3 * math.pi * t + ph[0]) +
         0.30 * np.sin(11.7 * math.pi * t + ph[1]) +
         0.18 * np.sin(23.1 * math.pi * t + ph[2]) +
         0.10 * np.sin(41.3 * math.pi * t + ph[3]))
    return 1.0 + 0.42 * v


def tube(path, radius, sections=12, up=(1.0, 0.0, 0.0)):
    """A closed tube swept along a path - a laid-on line is continuous glass, not a
    row of beads."""
    P = np.asarray(path, "f8")
    n = len(P)
    T = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    T /= np.linalg.norm(T, axis=1)[:, None]
    upv = np.asarray(up, "f8")
    U = np.cross(T, upv)
    lens = np.linalg.norm(U, axis=1)[:, None]
    U = np.where(lens > 1e-6, U / np.maximum(lens, 1e-9), np.array([0.0, 0.0, 1.0]))
    V = np.cross(T, U)
    a = np.linspace(0, 2 * math.pi, sections, endpoint=False)
    verts = np.empty((n, sections, 3))
    for i in range(n):
        verts[i] = P[i] + radius * (np.cos(a)[:, None] * U[i] + np.sin(a)[:, None] * V[i])
    faces = []
    for i in range(n):
        j = (i + 1) % n
        for k in range(sections):
            l = (k + 1) % sections
            faces.append([i * sections + k, j * sections + k, j * sections + l])
            faces.append([i * sections + k, j * sections + l, i * sections + l])
    return trimesh.Trimesh(vertices=verts.reshape(-1, 3), faces=np.asarray(faces),
                           process=False)


def hammer_spiral(turns=13, pitch=2.4, minor=0.55, seed=3, per_turn=120, foot=True):
    """The same dripped run on the hammer: down the head while it spins, then a short
    run round the foot. The head is not round, so the path follows its sections."""
    import decor
    turns = max(float(turns), 0.0)
    parts = []
    if turns > 0:
        n = max(int(turns * per_turn), 8)
        t = np.linspace(0.0, 1.0, n)
        rng = np.random.RandomState(seed)
        theta = 2 * math.pi * turns * t
        x0 = decor.RIM_X - 1.5
        x = x0 - turns * pitch * (t + 0.04 * np.sin(3.1 * math.pi * t + rng.uniform(0, 6)))
        x = np.clip(x, -33.0, x0)
        r = np.clip(minor * viscosity(t, seed), minor * 0.35, minor * 1.9)
        path = [decor.surface_pt(float(x[i]), float(theta[i]), out=-float(r[i]) * 0.18)
                for i in range(n)]
        parts.append(tube_var(path, r, up=(1.0, 0.0, 0.0)))
    if foot and turns > 0:
        n = 460
        t = np.linspace(0.0, 1.0, n)
        rng = np.random.RandomState(seed + 1)
        theta = 2 * math.pi * 3.0 * t
        z = 7.6 - 6.0 * t
        r = np.clip(minor * viscosity(t, seed + 1), minor * 0.4, minor * 1.7)
        rad = 12.25 - r * 0.2
        path = np.column_stack([rad * np.cos(theta), rad * np.sin(theta), z])
        parts.append(tube_var(path, r, up=(0.0, 0.0, 1.0)))
    if not parts:
        return trimesh.creation.icosphere(subdivisions=1, radius=0.001)
    return trimesh.util.concatenate(parts)


def hammer_rings(n=20, pitch=2.4, minor=0.24, start=None, seg=170, seed=3, foot=True):
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
            x -= pitch * rng.uniform(0.55, 1.85)
            if rng.random_sample() < 0.16:
                x -= pitch * rng.uniform(1.0, 2.2)
            if x < -34.0:
                break
            r = minor * rng.uniform(0.62, 1.55)
            path = [decor.surface_pt(x, 2 * math.pi * j / seg, out=-r * 0.45)
                    for j in range(seg)]
            parts.append(tube(path, r, up=(1.0, 0.0, 0.0)))
    if foot and n:
        for k in range(max(n // 4, 3)):
            z = 1.4 + k * 1.7 * rng.uniform(0.7, 1.5)
            if z > 8.5:
                break
            r = minor * rng.uniform(0.6, 1.3)
            rad = 12.25 - r * 0.5
            path = [(rad * math.cos(2 * math.pi * j / seg),
                     rad * math.sin(2 * math.pi * j / seg), z) for j in range(seg)]
            parts.append(tube(path, r, up=(0.0, 0.0, 1.0)))
    if not parts:
        return trimesh.creation.icosphere(subdivisions=1, radius=0.001)
    return trimesh.util.concatenate(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = spiral()
    m.export(os.path.join(out, "jar_lines.stl"))
    # the frit sits about 0.5 proud, so these ride over it
    f = spiral(turns=9, pitch=2.4, minor=0.55, top=90.0, bottom=66.0, seed=12,
               proud=1.15)              # over the frit, for the coloured builds
    f.export(os.path.join(out, "jar_lines_frit.stl"))
    h = hammer_spiral()
    h.export(os.path.join(out, "hammer_lines.stl"))
    print("linework: %d body rings, %d rings over the frit"
          % (sum(g[1] for g in GROUPS), sum(g[1] for g in GROUPS_FRIT)))
