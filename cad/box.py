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

The foam well is not a plain bore. The marbles stand proud of the wall by four
millimetres a side, so a well cut to the glass would not take the piece at all - it is
cut as a stadium, wide enough across the marbles and close on the other axis, which is
also what stops the tube turning in the box and facing its label at the lid.

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
    inner_y=38.0,         # cavity, front to back
    z0=-14.0,             # cavity floor, relative to the tube's own base
    z1=148.0,             # cavity ceiling - the cork tops out at 139

    open_x=40.0,          # the mouth cut through the front board
    open_pad=3.0,         # lip left round it, top and bottom

    lid_swing=104.0,      # degrees the lid stands open in the shot

    well_x=38.0,          # foam well, across the marbles
    well_y=30.0,          # foam well, front to back
    well_y0=1.0,          # the well sits a shade back, so the front relief is even
    relief_x=19.0,        # the front is cut away to this half-width - lift it straight out
    foam_top=148.0,

    magnet_d=7.0,
    magnet_t=1.5,
    magnet_z=(30.0, 118.0),
)


def _dims(p):
    hx, hy = p["inner_x"] / 2, p["inner_y"] / 2
    b = p["board"]
    return hx, hy, b, hx + b, hy + b


def shell(p=None):
    """Five sides of board. The sixth is the mouth the lid closes over."""
    p = dict(P, **(p or {}))
    hx, hy, b, ox, oy = _dims(p)
    body = (cq.Workplane("XY").workplane(offset=p["z0"] - b)
            .box(2 * ox, 2 * oy, (p["z1"] - p["z0"]) + 2 * b,
                 centered=(True, True, False)))
    body = body.cut(cq.Workplane("XY").workplane(offset=p["z0"])
                    .box(2 * hx, 2 * hy, p["z1"] - p["z0"], centered=(True, True, False)))
    # the mouth, with a lip left all round it for the magnets to sit in
    mouth = (cq.Workplane("XY").workplane(offset=p["z0"] + p["open_pad"])
             .center(0, -oy - 2)
             .box(p["open_x"], 2 * b + 6,
                  (p["z1"] - p["z0"]) - 2 * p["open_pad"], centered=(True, True, False)))
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
    hx, hy, b, ox, oy = _dims(p)
    panel = (cq.Workplane("XY").workplane(offset=p["z0"] - b)
             .center(0, -oy - b / 2)
             .box(2 * ox, b, (p["z1"] - p["z0"]) + 2 * b, centered=(True, True, False)))
    # hinge line: the outer corner of the mouth, so the lid clears the box as it swings
    return panel.rotate((ox, -oy, 0), (ox, -oy, 1), p["lid_swing"])


def _magnet_pair(p, y, side=-1.0):
    hx, hy, b, ox, oy = _dims(p)
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
    hx, hy, b, ox, oy = _dims(p)
    inlip = _magnet_pair(p, -oy - b + 0.9)
    onlid = _magnet_pair(p, -oy - b - 0.1).rotate((ox, -oy, 0), (ox, -oy, 1),
                                                 p["lid_swing"])
    return inlip.union(onlid)


def foam(p=None):
    """Die-cut foam, one well, relieved at the front so the piece comes straight out
    rather than being fished for."""
    p = dict(P, **(p or {}))
    hx, hy, b, ox, oy = _dims(p)
    block = (cq.Workplane("XY").workplane(offset=p["z0"])
             .box(2 * hx - 0.4, 2 * hy - 0.4, p["foam_top"] - p["z0"],
                  centered=(True, True, False)))
    wx, wy = p["well_x"], p["well_y"]
    well = (cq.Workplane("XY").workplane(offset=p["z0"] + 6.0)
            .center(0, p["well_y0"])
            .slot2D(max(wx - wy, 0.01) + wy, wy, 0)
            .extrude(p["foam_top"] - p["z0"]))
    block = block.cut(well)
    relief = (cq.Workplane("XY").workplane(offset=p["z0"] + 6.0)
              .center(0, -hy - 4)
              .box(2 * p["relief_x"], 2 * (hy + 4) - (wy / 2 - p["well_y0"]) + 0.5,
                   p["foam_top"] - p["z0"], centered=(True, True, False)))
    block = block.cut(relief)
    return block


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    p = dict(P)
    hx, hy, b, ox, oy = _dims(p)
    print("box outside  %.0f x %.0f x %.0f mm"
          % (2 * ox, 2 * oy + b, (p["z1"] - p["z0"]) + 2 * b))
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
