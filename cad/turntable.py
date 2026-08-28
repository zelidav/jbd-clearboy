"""Turntable frame renderer.

Renders N evenly-spaced yaw angles about the piece's own axis, starting broadside,
using the same studio-glass compositor as the stills - so the web spinner and the
product shots are the same render.

    python turntable.py                 # every piece x every colourway, 72 frames
    python turntable.py jar 36
"""
import math, os, sys, time
import mockups
from mockups import PIECES, WAYS, SIDE

FRAMES = "frames"


def spin(piece, key, n=72, W=None, H=None, out=None, frit=True, tag=""):
    """tag names a second set of frames for the same piece and colourway - the no-frit
    revision spins the same geometry with one layer left off."""
    out = out or os.path.join(FRAMES, "%s_%s%s" % (piece, key, tag))
    os.makedirs(out, exist_ok=True)
    W, H = mockups.size_of(piece, W, H)
    r = mockups.build_renderer(piece, key, W, H, frit=frit)
    # start where the piece reads best, not at whatever yaw zero happens to be. A box
    # only reads open in three-quarter, so a spinner that starts broadside opens on the
    # back of it - and frame zero is also the poster and the still on the page.
    start = SIDE + math.radians(mockups.PIECES[piece].get("yaw", 0.0))
    t0 = time.time()
    for i in range(n):
        im = mockups.frame(r, piece, start + 2 * math.pi * i / n)
        im.save(os.path.join(out, "%03d.png" % i))
    print("  %s / %s%s: %d frames in %.1fs"
          % (piece, key, tag, n, time.time() - t0), flush=True)
    return out


TILTS = [0.0, -23.0, -45.0, -68.0, -90.0]      # standing -> laid down


def grid(piece, key, n=24, tilts=None, W=None, H=None, out=None, frit=True):
    """A roll x tilt sheet: dragging left/right rolls the piece on its own axis,
    dragging up/down tips it between laid down and standing."""
    tilts = TILTS if tilts is None else tilts
    out = out or os.path.join(FRAMES, "%s_%s" % (piece, key))
    os.makedirs(out, exist_ok=True)
    W, H = mockups.size_of(piece, W, H)
    r = mockups.build_renderer(piece, key, W, H, frit=frit)
    start = SIDE + math.radians(mockups.PIECES[piece].get("yaw", 0.0))
    t0 = time.time()
    for j, tl in enumerate(tilts):
        for i in range(n):
            im = mockups.frame(r, piece, start + 2 * math.pi * i / n, tilt=tl)
            im.save(os.path.join(out, "t%02d_r%03d.png" % (j, i)))
    print("  %s / %s: %d x %d grid in %.1fs"
          % (piece, key, len(tilts), n, time.time() - t0), flush=True)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    n = next((int(a) for a in args if a.isdigit()), 72)
    pieces = [a for a in args if a in PIECES] or list(PIECES)
    ways = [a for a in args if a in WAYS] or list(WAYS)
    for pc in pieces:
        for k in ways:
            spin(pc, k, n)
