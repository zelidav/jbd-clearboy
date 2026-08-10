"""JBD joint holder - a roaring-twenties cigarette holder, made for a joint.

The shape is the old long-stem holder: a slim tapered tube with a waist, opening into a
flared bell at the front. The bell is the working part. Inside it is a cone that runs
from a narrow throat out to a wide mouth, so a joint of any diameter in that range slides
in until it wedges - one holder takes a pinner or a fat one and grips both. Nothing to
adjust, no insert to lose.

Three marbles sit proud along one side. They are decoration, but they are also why it
does not roll off a table.

    python holder.py out   -> out/holder.stl/.step, out/holder_frit.stl,
                              out/holder_marbles.stl, out/holder_bling.stl
"""
import math, os, sys

import cadquery as cq
import numpy as np
import trimesh

# ---------------------------------------------------------------- parameters
P = dict(
    length=90.0,          # overall, 3.5 in. Three to four inches is the period range
    mouth_od=9.6,         # the lip you hold in your teeth
    mouth_bore=4.2,
    waist_od=10.4,        # slimmest point, about a fifth along
    body_od=13.2,         # where the body meets the bell shoulder
    bell_od=23.0,         # outside of the flare at the front face
    bell_id=15.0,         # the wide end of the grip cone
    throat_id=6.4,        # the narrow end - a pinner stops here
    bell_len=26.0,        # how far the flare runs back
    wall=2.2,
    rake=0.0,             # degrees the bell tips up off the mouthpiece axis
    marbles=3,
    marble_r=4.2,
    marble_from=0.30,     # first marble, as a fraction of the length
    marble_to=0.56,
    bling=0,              # stones set round the bell shoulder
    bling_r=1.7,
    frit_from=0.68,       # frit band, fractions of the length
    frit_to=1.0,
)

SEG = 96


def _profile(p):
    """Outer silhouette as (z, radius) stations, mouthpiece at z = 0."""
    L, bell_z = p["length"], p["length"] - p["bell_len"]
    return [
        (0.0, p["mouth_od"] / 2 + 0.55),          # rolled lip
        (2.4, p["mouth_od"] / 2),
        (L * 0.19, p["waist_od"] / 2),            # the waist that makes it read slim
        (bell_z * 0.72, p["waist_od"] / 2 * 1.06),
        (bell_z, p["body_od"] / 2),               # shoulder
        (bell_z + p["bell_len"] * 0.42, p["body_od"] / 2 * 1.16),
        (L - 1.6, p["bell_od"] / 2),              # the flare turns over quickly
        (L, p["bell_od"] / 2),
    ]


def _bore(p):
    """Inner silhouette. Straight bore up to the throat, then the grip cone."""
    L, bell_z = p["length"], p["length"] - p["bell_len"]
    return [
        (-1.0, p["mouth_bore"] / 2),
        (bell_z, p["mouth_bore"] / 2),
        (bell_z + 1.5, p["throat_id"] / 2),       # the step a pinner sits on
        (L + 1.0, p["bell_id"] / 2 + 1.0),
    ]


def _revolve(stations, close_at=None):
    """Revolve a (z, r) polyline about Z. Radii are clamped off the axis so OCC always
    has a face to sweep."""
    pts = [(max(r, 0.05), z) for (z, r) in stations]
    w = cq.Workplane("XZ").moveTo(0, pts[0][1])
    for r, z in pts:
        w = w.lineTo(r, z)
    w = w.lineTo(0, pts[-1][1])
    return w.close().revolve(360, (0, 0, 0), (0, 1, 0))


def build(p=None):
    p = dict(P, **(p or {}))
    body = _revolve(_profile(p))
    body = body.cut(_revolve(_bore(p)))
    # break the two edges a mouth actually touches
    try:
        body = body.edges(cq.selectors.NearestToPointSelector((0, 0, 0))).fillet(0.7)
    except Exception:
        pass
    if p["rake"]:
        # tip the bell up off the mouthpiece axis, pivoting at the shoulder
        z = p["length"] - p["bell_len"]
        body = body.rotate((0, -1, z), (0, 1, z), 0)     # placeholder pivot, see note
    return body


def radius_at(z, p=None):
    """Outer radius at a height, interpolated off the profile."""
    p = dict(P, **(p or {}))
    st = _profile(p)
    zs = [s[0] for s in st]
    if z <= zs[0]:
        return st[0][1]
    if z >= zs[-1]:
        return st[-1][1]
    i = max(j for j in range(len(zs)) if zs[j] <= z)
    i = min(i, len(st) - 2)
    (z0, r0), (z1, r1) = st[i], st[i + 1]
    t = 0.0 if z1 == z0 else (z - z0) / (z1 - z0)
    return r0 + (r1 - r0) * t


def _sphere(r, pos, subdiv=2):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=r)
    m.apply_translation(pos)
    return m


def _stone(r, pos, seed=0):
    """A cut stone rather than a bead: an icosahedron left unsmoothed, so it takes light
    in flat facets the way a brilliant does."""
    m = trimesh.creation.icosphere(subdivisions=0, radius=r)
    rng = np.random.RandomState(seed)
    m.apply_transform(trimesh.transformations.random_rotation_matrix(rng.rand(3)))
    m.apply_translation(pos)
    return m


def build_marbles(p=None):
    """A row down one side. Proud enough to stop it rolling, low enough to hold."""
    p = dict(P, **(p or {}))
    n = int(p["marbles"])
    if n <= 0:
        return trimesh.Trimesh()
    r = p["marble_r"]
    z0, z1 = p["length"] * p["marble_from"], p["length"] * p["marble_to"]
    out = []
    for i in range(n):
        z = z0 if n == 1 else z0 + (z1 - z0) * i / (n - 1.0)
        # on the camera side: they are the anti-roll feature and they are the
        # decoration, and neither works from behind
        y = radius_at(z, p) + r * 0.42
        out.append(_sphere(r, (0.0, -y, z)))
    return trimesh.util.concatenate(out)


def build_bling(p=None):
    """Stones set round the bell shoulder, and a second course down the waist once
    there are enough of them to need somewhere to go."""
    p = dict(P, **(p or {}))
    n = int(p["bling"])
    if n <= 0:
        return trimesh.Trimesh()
    r = p["bling_r"]
    zs = [p["length"] - p["bell_len"] + 2.0]
    if n > 14:
        zs.append(p["length"] - p["bell_len"] - 7.0)
    if n > 28:
        zs.append(p["length"] * 0.24)
    out, k = [], 0
    per = int(math.ceil(n / float(len(zs))))
    for z in zs:
        rad = radius_at(z, p) + r * 0.34
        for i in range(min(per, n - k)):
            a = 2 * math.pi * i / float(per) + 0.4 * zs.index(z)
            out.append(_stone(r, (rad * math.sin(a), rad * math.cos(a), z), seed=k))
            k += 1
    return trimesh.util.concatenate(out) if out else trimesh.Trimesh()


def build_frit(p=None, grains=620, seed=11):
    """Frit rolled over the bell, densest at the rim."""
    p = dict(P, **(p or {}))
    rng = np.random.RandomState(seed)
    z0, z1 = p["length"] * p["frit_from"], p["length"] * p["frit_to"]
    out = []
    for _ in range(grains):
        t = rng.random_sample() ** 0.55
        z = z0 + (z1 - z0) * t
        gr = 0.34 + 0.52 * rng.random_sample() ** 1.6
        a = 2 * math.pi * rng.random_sample()
        rad = radius_at(z, p) + gr * 0.30
        out.append(_sphere(gr, (rad * math.sin(a), rad * math.cos(a), z), subdiv=1))
    return trimesh.util.concatenate(out)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build()
    solid = m.val()
    print("volume mm^3:", round(solid.Volume(), 1),
          "-> glass mass approx", round(solid.Volume() * 2.23e-3, 1), "g")
    bb = solid.BoundingBox()
    print("bbox  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    cq.exporters.export(m, os.path.join(out, "holder.step"))
    cq.exporters.export(m, os.path.join(out, "holder.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    build_marbles().export(os.path.join(out, "holder_marbles.stl"))
    build_frit().export(os.path.join(out, "holder_frit.stl"))
    b = build_bling(dict(bling=18))
    b.export(os.path.join(out, "holder_bling.stl"))
    print("exported")
