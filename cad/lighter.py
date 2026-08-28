"""JBD lighter sleeve - a glass jacket for a standard full-size lighter.

The lighter everyone owns is a disposable: a thin plastic shell that reads cheap on a
table, disappears into a couch, and gets handed off and never comes back. The sleeve is
the answer to all three. It is a hand-blown glass socket the lighter drops into, so the
thing you set down next to the piece is glass, it is heavy enough to stay put, and it is
yours in a way a shared lighter never is.

The socket is an obround - a stadium section, flat-ish on the two faces, round on the
two ends - because that is the section of the lighter. A round bore would let it spin
and rattle; this one holds the flint wheel square to your thumb so the lighter can be
struck without taking it out. It is drawn a shade over the lighter on both axes, enough
that a warm hand still gets it in.

The sleeve is deliberately short. Twenty-five millimetres of lighter stand proud - the
hood, the wheel and the button - so it is used in the sleeve rather than unpacked from
it. A finger notch is cut through the front so it can be pushed out from below when it
does run dry.

Flat base, so it stands. An obround does not roll, which is why this one carries no
marbles - the section is already the anti-roll. The decoration is a wig wag round the
base, the same band the joint tube wears, so the two read as one set.

    python lighter.py out   -> out/lighter.stl/.step, out/lighter_wig_a.stl,
                               out/lighter_wig_b.stl, out/lighter_body.stl,
                               out/lighter_hood.stl, out/lighter_wheel.stl
"""
import math, os, sys

import cadquery as cq
import numpy as np
import trimesh

# ------------------------------------------------------------- the lighter itself
# A full-size disposable, measured off the one on the bench: 81 mm overall, an obround
# section 23.4 across the faces by 12.2 deep at the base, drafted in a little towards
# the shoulder, then a pressed metal hood over the wheel and the jet.
L = dict(
    body_h=67.5,          # plastic, base to shoulder
    base_w=23.4, base_d=12.2,
    top_w=21.6, top_d=11.4,
    hood_h=9.5,           # the pressed shroud
    hood_w=17.0, hood_d=10.4,
    wheel_r=4.6,          # the flint wheel, across the hood
    wheel_t=3.4,
    total=81.0,
)

# ----------------------------------------------------------------- the sleeve
P = dict(
    clear=1.1,            # slip fit on each axis - a warm hand still gets it in
    wall=3.0,
    floor=3.4,
    depth=55.0,           # how far the lighter goes in. 81 - 55 = 26 standing proud
    lip=0.9,              # the rim is rolled, not cut square
    notch_w=10.5,         # finger notch through the front face
    notch_h=17.0,         # how far down from the rim it runs
    # A wrap read as a cage in front of a section this flat - the strand crosses the
    # face rather than running round it, and every crossing lands twice. The sleeve
    # wears a wig wag at the base instead, which is the same band the joint tube wears.
    spin=0,               # strands of colour wound up the sleeve
    spin_turns=1.7,
    spin_r=0.44,
    spin_from=0.14,
    spin_to=0.92,

    wig=5,                # stringers in the wig wag at the base
    wig_r=0.42,
    wig_z=(6.0, 23.0),
    wig_lobes=8,
    wig_amp=4.0,
)

SEG = 96


def _stadium(w, d):
    """An obround of overall width w and depth d, as a cadquery 2-D slot."""
    return dict(length=max(w - d, 0.01), diameter=d)


def _slot(wp, w, d):
    s = _stadium(w, d)
    return wp.slot2D(s["length"] + s["diameter"], s["diameter"], 0)


def cavity(p):
    """The socket, sized off the lighter plus the slip fit. It is drawn as the lighter's
    own taper run straight through, so the walls touch the shell along its whole length
    rather than only at the base."""
    c = p["clear"]
    z0 = p["floor"]
    lo = _slot(cq.Workplane("XY").workplane(offset=z0),
               L["base_w"] + c, L["base_d"] + c)
    # the socket mouth follows the lighter's own draft, so it grips top and bottom
    k = p["depth"] / L["body_h"]
    tw = L["base_w"] + (L["top_w"] - L["base_w"]) * k + c
    td = L["base_d"] + (L["top_d"] - L["base_d"]) * k + c
    return lo.workplane(offset=p["depth"] + 2).slot2D(
        max(tw - td, 0.01) + td, td, 0).loft(ruled=True)


def outer(p):
    """The outside is the socket walked out by the wall, so the glass is even all round
    and the sleeve keeps the section of the thing it holds."""
    c, w = p["clear"], p["wall"]
    h = p["floor"] + p["depth"]
    bw, bd = L["base_w"] + c + 2 * w, L["base_d"] + c + 2 * w
    k = p["depth"] / L["body_h"]
    tw = L["base_w"] + (L["top_w"] - L["base_w"]) * k + c + 2 * w
    td = L["base_d"] + (L["top_d"] - L["base_d"]) * k + c + 2 * w
    lo = _slot(cq.Workplane("XY"), bw, bd)
    return lo.workplane(offset=h).slot2D(max(tw - td, 0.01) + td, td, 0).loft(ruled=True)


def _notch(p):
    """A finger notch through the front wall. It runs down from the rim so a thumb
    reaches the shell and pushes it up - a closed sleeve this deep would need shaking
    out, and glass is not a thing to shake.

    Through the FRONT WALL, not through the piece. The cutter is parked outside the
    front face and driven back just past the inside of that wall, so the back and the
    two ends are untouched and the sleeve still grips."""
    h = p["floor"] + p["depth"]
    w = p["notch_w"]
    oy = half_at(h, p)[1]                       # outside half-depth at the rim
    iy = (L["base_d"] + p["clear"]) / 2         # inside half-depth
    y1 = -(iy - 0.8)                            # stop just inside the cavity wall
    y0 = -(oy + 2.0)                            # start clear of the outside
    d = y1 - y0
    box = (cq.Workplane("XY").workplane(offset=h - p["notch_h"])
           .center(0, y0 + d / 2)
           .box(w, d, p["notch_h"] + 6.0, centered=(True, True, False)))
    # round the bottom of the notch - no corner for a crack to start from
    cyl = (cq.Workplane("XZ").workplane(offset=-y0)
           .center(0, h - p["notch_h"]).circle(w / 2).extrude(d))
    return box.union(cyl)


def build(p=None):
    p = dict(P, **(p or {}))
    body = outer(p).cut(cavity(p))
    body = body.cut(_notch(p))
    if p["lip"]:
        try:
            body = body.edges(">Z").fillet(p["lip"])
        except Exception:
            pass
    try:
        body = body.edges("<Z").fillet(1.6)          # the base it stands on
    except Exception:
        pass
    return body


def height(p=None):
    p = dict(P, **(p or {}))
    return p["floor"] + p["depth"]


def half_at(z, p=None):
    """Half-width and half-depth of the outside at a height - what the spun linework
    and anything else set on the surface rides on."""
    p = dict(P, **(p or {}))
    c, w = p["clear"], p["wall"]
    h = height(p)
    t = min(max(z / h, 0.0), 1.0) * (p["depth"] / L["body_h"])
    bw, bd = L["base_w"] + c + 2 * w, L["base_d"] + c + 2 * w
    return (bw + (L["top_w"] - L["base_w"]) * t) / 2, (bd + (L["top_d"] - L["base_d"]) * t) / 2


def surface_pt(z, theta, out=0.0, p=None):
    """A point on the obround surface at angle theta. The stadium is walked as a
    superellipse - close enough at this aspect, and it never kinks at the joins."""
    a, b = half_at(z, p)
    n = 3.1                                       # squareness of the section
    ca, sa = math.cos(theta), math.sin(theta)
    r = ((abs(ca) / (a + out)) ** n + (abs(sa) / (b + out)) ** n) ** (-1.0 / n)
    return (r * ca, r * sa, z)


def _sphere(r, pos, subdiv=1):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=r)
    m.apply_translation(pos)
    return m


def build_spin(p=None):
    """Colour wound up the sleeve, one mesh per strand so each takes its own - the
    same spinwork the joint holder wears, walked round an obround instead of a tube."""
    p = dict(P, **(p or {}))
    n = int(p["spin"])
    if n <= 0:
        return []
    h = height(p)
    z0, z1 = h * p["spin_from"], h * p["spin_to"]
    turns, r = p["spin_turns"], p["spin_r"]
    steps = max(int(turns * 150), 200)
    out = []
    for si in range(n):
        beads, phase = [], 2 * math.pi * si / float(n)
        for i in range(steps + 1):
            t = i / float(steps)
            z = z0 + (z1 - z0) * t
            a = phase + 2 * math.pi * turns * t
            beads.append(_sphere(r, surface_pt(z, a, out=r * 0.22, p=p)))
        out.append(trimesh.util.concatenate(beads))
    return out


def build_wigwag(p=None):
    """The same band the joint tube carries, walked round an obround.

    Stringers run up and down as they go round, so the peaks stack into chevrons. Two
    meshes, alternate stringers in each, so it is pulled in two colours - which is what
    makes it a wig wag rather than a wavy line."""
    p = dict(P, **(p or {}))
    n = int(p["wig"])
    if n <= 0:
        return trimesh.Trimesh(), trimesh.Trimesh()
    r = p["wig_r"]
    z0, z1 = p["wig_z"]
    amp, lobes = p["wig_amp"], float(p["wig_lobes"])
    span = (z1 - z0) - 2 * amp
    steps = int(lobes * 52)
    a_side, b_side = [], []
    for i in range(n):
        base = z0 + amp + (span * i / (n - 1.0) if n > 1 else span / 2)
        chain = []
        for k in range(steps + 1):
            th = 2 * math.pi * k / steps
            z = base + amp * math.sin(lobes * th)
            chain.append(_sphere(r, surface_pt(z, th, out=r * 0.22, p=p), subdiv=1))
        (a_side if i % 2 == 0 else b_side).append(trimesh.util.concatenate(chain))
    cat = trimesh.util.concatenate
    return (cat(a_side) if a_side else trimesh.Trimesh(),
            cat(b_side) if b_side else trimesh.Trimesh())


# ------------------------------------------------------- the lighter, for the shot
def build_lighter(z0=None, p=None):
    """The disposable itself, so the sleeve can be shown loaded as well as empty.
    Returns (shell, hood, wheel) - three solids, because they are three materials:
    coloured plastic, pressed metal, and the knurled flint wheel."""
    p = dict(P, **(p or {}))
    z0 = p["floor"] + 0.4 if z0 is None else z0     # it sits on the socket floor
    shell = (_slot(cq.Workplane("XY").workplane(offset=z0), L["base_w"], L["base_d"])
             .workplane(offset=L["body_h"])
             .slot2D(max(L["top_w"] - L["top_d"], 0.01) + L["top_d"], L["top_d"], 0)
             .loft(ruled=True))
    try:
        shell = shell.edges("<Z").fillet(1.2)
    except Exception:
        pass

    hz = z0 + L["body_h"]
    hood = (_slot(cq.Workplane("XY").workplane(offset=hz), L["hood_w"], L["hood_d"])
            .extrude(L["hood_h"]))
    try:
        hood = hood.edges(">Z").fillet(1.4)
    except Exception:
        pass
    # the wheel sits across the hood, its axis on Y, standing a little proud of the top
    wheel = cq.Workplane("XZ", origin=(0, L["hood_d"] / 2 + 0.6, 0)).center(
        0, hz + L["hood_h"] - L["wheel_r"] * 0.55).circle(L["wheel_r"]).extrude(
        -(L["hood_d"] + 1.2))
    hood = hood.cut(wheel.faces().shell(0.0) if False else wheel)
    return shell, hood, wheel


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    m = build()
    solid = m.val()
    print("sleeve volume mm^3:", round(solid.Volume(), 1),
          "-> glass mass approx", round(solid.Volume() * 2.23e-3, 1), "g")
    bb = solid.BoundingBox()
    print("bbox  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    cq.exporters.export(m, os.path.join(out, "lighter.step"))
    cq.exporters.export(m, os.path.join(out, "lighter.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    for i, s in enumerate(build_spin()):
        s.export(os.path.join(out, "lighter_spin%d.stl" % i))
    wa, wb = build_wigwag()
    wa.export(os.path.join(out, "lighter_wig_a.stl"))
    wb.export(os.path.join(out, "lighter_wig_b.stl"))
    shell, hood, wheel = build_lighter()
    cq.exporters.export(shell, os.path.join(out, "lighter_body.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    cq.exporters.export(hood, os.path.join(out, "lighter_hood.stl"),
                        tolerance=0.03, angularTolerance=0.12)
    cq.exporters.export(wheel, os.path.join(out, "lighter_wheel.stl"),
                        tolerance=0.02, angularTolerance=0.10)
    print("sleeve %.1f tall, %.0f mm of lighter proud"
          % (height(), L["total"] - P["depth"]))
    print("exported")
