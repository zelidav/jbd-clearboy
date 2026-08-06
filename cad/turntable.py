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


def spin(piece, key, n=72, W=None, H=None, out=None):
    out = out or os.path.join(FRAMES, "%s_%s" % (piece, key))
    os.makedirs(out, exist_ok=True)
    W, H = mockups.size_of(piece, W, H)
    r = mockups.build_renderer(piece, key, W, H)
    t0 = time.time()
    for i in range(n):
        im = mockups.frame(r, piece, SIDE + 2 * math.pi * i / n)
        im.save(os.path.join(out, "%03d.png" % i))
    print("  %s / %s: %d frames in %.1fs" % (piece, key, n, time.time() - t0), flush=True)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    n = next((int(a) for a in args if a.isdigit()), 72)
    pieces = [a for a in args if a in PIECES] or list(PIECES)
    ways = [a for a in args if a in WAYS] or list(WAYS)
    for pc in pieces:
        for k in ways:
            spin(pc, k, n)
