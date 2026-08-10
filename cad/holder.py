"""JBD joint holder - a roaring-twenties cigarette holder, made for a joint.

The shape is the old long-stem holder: a slim tapered tube with a waist, opening into a
flared bell at the front. The bell is the working part. Inside it is a cone that runs
from a narrow throat out to a wide mouth, so a joint of any diameter in that range slides
in until it wedges - one holder takes a pinner or a fat one and grips both. Nothing to
adjust, no insert to lose.

Three marbles sit proud along one side. They are decoration, but they are also why it
does not roll off a table.

A ring at the mouthpiece takes a chain. It sits on the back face, opposite the marbles,
so hung round a neck the piece falls bell-down with the stones facing out.

There is no frit on this piece. The body carries spun linework instead - several strands
of colour wound down the tube together, which is the older trick and reads far better on
something this slim. Stones come in two materials at once so a course can be opal and
diamond rather than one or the other.

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
    marble_spread=150.0,  # degrees they wander round the tube between first and last
    bling=0,              # stones set round the bell shoulder
    bling_r=1.7,
    loop=1,               # bail at the mouthpiece - wears on a chain
    loop_r=4.0,           # ring, centre to centre of the glass
    loop_t=1.45,          # thickness of the ring itself
    loop_z=7.5,           # how far up from the mouthpiece it sits
    spin=3,               # strands of colour wound down the body
    spin_turns=6.0,
    spin_r=0.46,
    spin_from=0.10,       # the wound run stops at the shoulder - the bell is for stones
    spin_to=0.60,
    frit_from=0.68,       # kept for anything that still wants a frit band
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

    if p.get("loop"):
        # A bail at the mouthpiece, so it wears on a chain. The ring sits on the back
        # face - opposite the marbles - and its hole runs across the piece, so hung on
        # a chain it falls bell-down with the marbles and the stones facing out rather
        # than into the wearer.
        z = p["loop_z"]
        R, t = p["loop_r"], p["loop_t"]
        y = radius_at(z, p) + R - t * 0.75
        ring = cq.Solid.makeTorus(R, t, cq.Vector(0, y, z), cq.Vector(1, 0, 0))
        body = body.union(cq.Workplane(obj=ring))
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
    """Set down the piece and walked round it as they go.

    A straight row of three along one side made it read like a bugle - the valves of
    one. Spreading them round an arc breaks that line, and it works better as the
    anti-roll they are for: marbles at different clock positions stop it whichever way
    it wants to go, where a single row only stops it once."""
    p = dict(P, **(p or {}))
    n = int(p["marbles"])
    if n <= 0:
        return trimesh.Trimesh()
    r = p["marble_r"]
    z0, z1 = p["length"] * p["marble_from"], p["length"] * p["marble_to"]
    spread = math.radians(p.get("marble_spread", 150.0))
    out = []
    for i in range(n):
        t = 0.0 if n == 1 else i / (n - 1.0)
        z = z0 + (z1 - z0) * t
        # centred on the camera side so the set still reads from the front
        a = -math.pi / 2 + spread * (t - 0.5)
        rad = radius_at(z, p) + r * 0.42
        out.append(_sphere(r, (rad * math.cos(a), rad * math.sin(a), z)))
    return trimesh.util.concatenate(out)


def build_bling(p=None):
    """Stones set in courses - round the bell shoulder first, then back down the body
    as the count grows. Returns two meshes, alternating, so a course can be cut in two
    materials: opal next to diamond rather than a row of one thing."""
    p = dict(P, **(p or {}))
    n = int(p["bling"])
    if n <= 0:
        return trimesh.Trimesh(), trimesh.Trimesh()
    r = p["bling_r"]
    L, bell = p["length"], p["bell_len"]
    zs = [L - bell + 2.5, L - bell * 0.62]
    if n > 20:
        zs.append(L - bell * 0.24)          # right out on the flare
    if n > 34:
        zs.append(L - bell - 5.0)           # and a course behind the shoulder
    if n > 50:
        zs.append(L - bell - 12.0)
    per = int(math.ceil(n / float(len(zs))))
    a_side, b_side, k = [], [], 0
    for ci, z in enumerate(zs):
        rad = radius_at(z, p) + r * 0.36
        for i in range(min(per, n - k)):
            a = 2 * math.pi * i / float(per) + 0.5 * ci
            st = _stone(r * (0.82 + 0.36 * ((i + ci) % 3) / 2.0),
                        (rad * math.sin(a), rad * math.cos(a), z), seed=k)
            (a_side if (i + ci) % 2 == 0 else b_side).append(st)
            k += 1
    cat = trimesh.util.concatenate
    return (cat(a_side) if a_side else trimesh.Trimesh(),
            cat(b_side) if b_side else trimesh.Trimesh())


def build_spin(p=None):
    """Colour wound down the body. One mesh per strand, so each takes its own colour -
    that is what makes it read as a twist rather than a stripe."""
    p = dict(P, **(p or {}))
    n = int(p["spin"])
    if n <= 0:
        return []
    turns, r = p["spin_turns"], p["spin_r"]
    z0, z1 = p["length"] * p["spin_from"], p["length"] * p["spin_to"]
    steps = max(int(turns * 90), 120)
    out = []
    for si in range(n):
        beads, phase = [], 2 * math.pi * si / float(n)
        for i in range(steps + 1):
            t = i / float(steps)
            z = z0 + (z1 - z0) * t
            a = phase + 2 * math.pi * turns * t
            rad = radius_at(z, p) + r * 0.55
            beads.append(_sphere(r, (rad * math.sin(a), rad * math.cos(a), z),
                                 subdiv=1))
        out.append(trimesh.util.concatenate(beads))
    return out


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
    for i, m in enumerate(build_spin()):
        m.export(os.path.join(out, "holder_spin%d.stl" % i))
    a, b = build_bling(dict(bling=28))
    a.export(os.path.join(out, "holder_bling.stl"))
    b.export(os.path.join(out, "holder_bling2.stl"))
    print("exported")
