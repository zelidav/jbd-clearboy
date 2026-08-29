"""JBD presentation box - rigid board, hinged lid, magnetic clasp.

The box exists because the tube is a keepsake, and a keepsake handed over in a paper bag
is a keepsake nobody photographs. Rigid board, wrapped, with a lid hinged along one long
edge and two disc magnets in the front lip: it opens once with a click and closes the
same way, and it survives being kept.

    Board       3.5 mm rigid, wrapped inside and out
    Lid         hinged full-height along one long edge, swings clear
    Clasp       two 9 mm disc magnets in the front lip, two in the lid
    Inside      the piece, wrapped in branded tissue and sealed with a collab sticker

The whole thing is modelled around the tube where the tube already sits - base at Z 0,
axis on Z - so the glass, the cork, the decoration and the printed band are the same
meshes the standing renders use and the label projector still lands where it should. The
shot lays the assembly down with a camera tilt rather than by rotating any geometry.

There is no insert. The box is cut to the piece - just enough room for the tube and the
tissue round it - and a box that fits does not need anything holding the thing still.
That is cheaper, it is one less part to source, and there is no foam in it: foam is the
one component of a box like this that cannot go in the recycling with the rest of it.

Earlier versions had a die-cut board cradle in here. It looked like a cradle, which is
to say it looked like packaging, and the piece is not being sold on its packaging.

    python box.py out   -> out/box_shell.stl, out/box_lid.stl, out/box_foam.stl,
                           out/box_magnets.stl
"""
import math, os, sys

import cadquery as cq
import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tube

P = dict(
    board=3.5,            # rigid board thickness
    # Cut to the piece. It is 33.6 across the drip marbles and 24 across the glass, and
    # the cork tops out at 139 - so the cavity is that plus the tissue plus a finger of
    # clearance, and nothing else.
    inner_x=37.0,
    y_front=-18.5,
    y_back=18.5,
    z0=-5.0,
    z1=145.0,

    open_x=40.0,          # the mouth cut through the front board
    open_pad=3.0,         # lip left round it, top and bottom

    lid_swing=104.0,      # degrees the lid stands open in the shot

    # The notch clears the GLASS, not the marbles: the ribs are placed between the
    # drips so they never meet one. Cutting to the marbles ate the whole rib and left
    # three tabs standing at the back.
    # the sleeve stands clear of the drip marbles, which reach 16.8 from the axis
    tissue_r=17.2,
    tissue_t=0.9,
    tissue_z=(3.0, 133.0),
    insert_top=145.0,

    magnet_d=5.0,
    magnet_t=1.1,
    magnet_z=(30.0, 118.0),
)


def _dims(p):
    """Half-width, the two Y faces of the cavity, the board, and the same outside.

    Y is not symmetric about the piece and that is the point, so it is carried as two
    numbers rather than a half-depth."""
    hx = p["inner_x"] / 2
    y0, y1 = p["y_front"], p["y_back"]
    b = p["board"]
    return hx, y0, y1, b, hx + b, y0 - b, y1 + b


def _slab(x_half, y0, y1, z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .center(0, (y0 + y1) / 2)
            .box(2 * x_half, y1 - y0, z1 - z0, centered=(True, True, False)))


def shell(p=None):
    """Five sides of board. The sixth is the mouth the lid closes over."""
    p = dict(P, **(p or {}))
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    body = _slab(ox, oy0, oy1, p["z0"] - b, p["z1"] + b)
    body = body.cut(_slab(hx, y0, y1, p["z0"], p["z1"]))
    # the mouth, with a lip left all round it for the magnets to sit in
    mouth = _slab(p["open_x"] / 2, oy0 - 4, y0 + 0.1,
                  p["z0"] + p["open_pad"], p["z1"] - p["open_pad"])
    body = body.cut(mouth)
    try:
        body = body.edges("|Z").fillet(1.6)
    except Exception:
        pass
    return body


def lid(p=None):
    """One panel, hinged along the right-hand vertical edge of the mouth and left
    standing open. A lid drawn shut is a lid that proves nothing."""
    p = dict(P, **(p or {}))
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    panel = _slab(ox, oy0 - b, oy0, p["z0"] - b, p["z1"] + b)
    # hinge line: the outer corner of the mouth, so the lid clears the box as it swings
    return panel.rotate((ox, oy0, 0), (ox, oy0, 1), p["lid_swing"])


def _magnet_pair(p, y, side=-1.0):
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    r, t = p["magnet_d"] / 2, p["magnet_t"]
    out = None
    for z in p["magnet_z"]:
        # sunk into the lip rather than sitting on it: a magnet proud of the board is
        # a bead, and the first render of these read as four decorative balls
        m = (cq.Workplane("XZ", origin=(side * (hx - 4.0), y, 0))
             .center(0, z).circle(r).extrude(t))
        out = m if out is None else out.union(m)
    return out


def magnets(p=None):
    """Two in the front lip, two in the lid, on the same axis. Modelled because a
    clasp you cannot see is a clasp the box does not appear to have."""
    p = dict(P, **(p or {}))
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    inlip = _magnet_pair(p, oy0 + 0.9)
    onlid = _magnet_pair(p, oy0 - b - 0.1).rotate((ox, oy0, 0), (ox, oy0, 1),
                                                  p["lid_swing"])
    return inlip.union(onlid)


def lid_label_quad(p=None, frac_x=0.74, half_z=62.0):
    """The four corners of the printed area on the inside of the lid, in model space.

    The lid is a flat panel and the renderer's decal projector is a cylinder about Z, so
    there is no way to print on it in the shader. These corners are handed to the
    renderer's own camera instead and the artwork is warped onto them afterwards - the
    same projection the dimensioned callouts use, so the label sits exactly where the
    lid is rather than approximately.

    Returned top-of-frame first, going round the way the artwork reads."""
    p = dict(P, **(p or {}))
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    zc = ((p["z0"] - b) + (p["z1"] + b)) / 2.0
    a = math.radians(p["lid_swing"])
    ca, sa = math.cos(a), math.sin(a)

    def pt(x, z):
        dx = x - ox
        return (ox + dx * ca, oy0 + dx * sa, z)

    xh = ox * frac_x
    # top-left, top-right, bottom-right, bottom-left AS THE ARTWORK READS once the
    # assembly is laid down for the shot: the artwork's long axis runs along Z, and the
    # lid is seen from its inside, which is what puts +Z on the left.
    return [pt(-xh, zc + half_z), pt(-xh, zc - half_z),
            pt(xh, zc - half_z), pt(xh, zc + half_z)]


def outer_faces(p=None, inset=0.86):
    """The closed outer faces of the base, as four model-space corners each.

    The mouth is not in here - it is a hole, and printing across a hole is not a thing.
    Corners run so the artwork's long axis follows the long axis of the face; which of
    these is actually facing the camera is decided at render time rather than guessed,
    so the print lands on whichever panel the shot is showing.

    Returned as a dict so the caller can say which one it used."""
    p = dict(P, **(p or {}))
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    zl, zh = p["z0"] - b, p["z1"] + b
    zc, zr = (zl + zh) / 2.0, (zh - zl) / 2.0 * inset
    yc, yr = (oy0 + oy1) / 2.0, (oy1 - oy0) / 2.0 * inset
    xr = ox * inset
    return {
        # the two long sides: artwork runs along Z, across Y
        "side_-x": [(-ox, yc - yr, zc + zr), (-ox, yc - yr, zc - zr),
                    (-ox, yc + yr, zc - zr), (-ox, yc + yr, zc + zr)],
        "side_+x": [(ox, yc - yr, zc + zr), (ox, yc - yr, zc - zr),
                    (ox, yc + yr, zc - zr), (ox, yc + yr, zc + zr)],
        # the back, opposite the mouth: artwork runs along Z, across X
        "back":    [(-xr, oy1, zc + zr), (-xr, oy1, zc - zr),
                    (xr, oy1, zc - zr), (xr, oy1, zc + zr)],
        # the two ends: artwork runs along X, across Y
        "end_low": [(-xr, yc - yr, zl), (xr, yc - yr, zl),
                    (xr, yc + yr, zl), (-xr, yc + yr, zl)],
        "end_high": [(-xr, yc - yr, zh), (xr, yc - yr, zh),
                     (xr, yc + yr, zh), (-xr, yc + yr, zh)],
    }


def face_normal(name, p=None):
    """Outward normal of one of those faces."""
    return {"side_-x": (-1, 0, 0), "side_+x": (1, 0, 0), "back": (0, 1, 0),
            "end_low": (0, 0, -1), "end_high": (0, 0, 1)}[name]


def tissue(p=None):
    """The tissue, wrapped round the piece - not lining the box.

    An earlier version of this was a liner folded up the sides, which is a different
    thing entirely: you open the box and the glass is just lying there. Wrapped, the
    box opens on a sealed parcel, and the piece is something you get to rather than
    something you are handed.

    A straight sleeve standing clear of the drip marbles. The seal that closes it is
    printed on, through the same projector the label uses."""
    p = dict(P, **(p or {}))
    r_in = p["tissue_r"]
    r_out = r_in + p["tissue_t"]
    z0, z1 = p["tissue_z"]
    outer = (cq.Workplane("XY").workplane(offset=z0).circle(r_out)
             .extrude(z1 - z0))
    return outer.cut(cq.Workplane("XY").workplane(offset=z0 - 1).circle(r_in)
                     .extrude(z1 - z0 + 2))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    p = dict(P)
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    print("box outside  %.0f x %.0f x %.0f mm"
          % (2 * ox, (oy1 - oy0) + b, (p["z1"] - p["z0"]) + 2 * b))
    print("tube it holds  %.0f OD x %.0f, cork to %.0f"
          % (tube.od(), tube.P["height"], tube.P["height"] + tube.P["cork_h"]
             - tube.P["cork_seat"]))
    for name, wp in (("box_shell", shell()), ("box_lid", lid()),
                     ("box_tissue", tissue()), ("box_magnets", magnets())):
        cq.exporters.export(wp, os.path.join(out, name + ".stl"),
                            tolerance=0.05, angularTolerance=0.2)
        print("  wrote", name)
    cq.exporters.export(shell(), os.path.join(out, "box_shell.step"))
    print("exported")
