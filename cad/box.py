"""JBD presentation box - rigid board, hinged lid, magnetic clasp.

The box exists because the tube is a keepsake, and a keepsake handed over in a paper bag
is a keepsake nobody photographs. Rigid board, wrapped, with a lid hinged along one long
edge and two disc magnets in the front lip: it opens once with a click and closes the
same way, and it survives being kept.

    Board       3.5 mm rigid, wrapped inside and out
    Lid         hinged full-height along one long edge, swings clear
    Clasp       two 9 mm disc magnets in the front lip, two in the lid
    Insert      die-cut foam, one well, front-relieved so the piece lifts straight out

The whole thing is modelled around the tube where the tube already sits - base at Z 0,
axis on Z - so the glass, the cork, the decoration and the printed band are the same
meshes the standing renders use and the label projector still lands where it should. The
shot lays the assembly down with a camera tilt rather than by rotating any geometry.

The insert is a trough, not a bore, and the cavity is deliberately not centred on the
piece. The tube is thirty-one millimetres across the drip marbles, so a cavity centred
on it leaves no foam underneath and the first render of this looked straight through the
insert to the back of the shell. The cavity is offset back instead: the trough is cut
from the face the lid closes on, and there is a real bed of foam under the piece and a
shoulder either side of it.

The trough is a stadium rather than a half-round for the same reason - wide enough to
clear the marbles, close on the other axis, which also stops the tube turning in the box
and facing its label at the lid.

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
    inner_x=46.0,         # cavity, across the marbles
    y_front=-18.0,        # cavity, towards the lid. The piece is on the axis at y 0,
    y_back=24.0,          # so these are not symmetric - the bed is the difference
    z0=-14.0,             # cavity floor, relative to the tube's own base
    z1=148.0,             # cavity ceiling - the cork tops out at 139

    open_x=40.0,          # the mouth cut through the front board
    open_pad=3.0,         # lip left round it, top and bottom

    lid_swing=104.0,      # degrees the lid stands open in the shot

    well_x=34.0,          # the trough, across the marbles
    well_floor=16.0,      # how far back the trough is cut to - the rest is the bed
    foam_top=148.0,

    magnet_d=7.0,
    magnet_t=1.5,
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


def foam(p=None):
    """Die-cut foam: a block filling the cavity with one trough cut into it.

    The trough is cut from the face the lid closes on, down to well_floor - so the
    piece drops in, the foam under it is a real bed rather than a skin, and there is a
    shoulder of foam either side that the eye reads as an insert instead of a hole."""
    p = dict(P, **(p or {}))
    hx, y0, y1, b, ox, oy0, oy1 = _dims(p)
    block = _slab(hx - 0.2, y0 + 0.2, y1 - 0.2, p["z0"], p["foam_top"])
    wx = p["well_x"]
    trough = (cq.Workplane("XY").workplane(offset=p["z0"] + 6.0)
              .center(0, (y0 - 6 + p["well_floor"]) / 2)
              .slot2D(max(wx - (p["well_floor"] - y0 + 6), 0.01)
                      + (p["well_floor"] - y0 + 6), p["well_floor"] - y0 + 6, 0)
              .extrude(p["foam_top"] - p["z0"]))
    return block.cut(trough)


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
                     ("box_foam", foam()), ("box_magnets", magnets())):
        cq.exporters.export(wp, os.path.join(out, name + ".stl"),
                            tolerance=0.05, angularTolerance=0.2)
        print("  wrote", name)
    cq.exporters.export(shell(), os.path.join(out, "box_shell.step"))
    print("exported")
