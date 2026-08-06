"""Turn the JB graffiti mark into polygons the CAD build can press into glass.

The artwork is flat black-on-white, so it traces cleanly: outer contours plus the
counters inside the letters, simplified enough for OCC to cut quickly and still read
as the mark. Cached to cad/stamp_art.json so a build needs no image.

    python stamp_art.py     -> cad/stamp_art.json + a preview
"""
import json, math, os, sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ART = os.path.join("assets", "jb_graffiti_icon.jpg")
CACHE = os.path.join("cad", "stamp_art.json")
PREVIEW = os.path.join("assets", "jb_graffiti_traced.png")
WIDTH = 520          # trace at this width; plenty for a 25 mm stamp
TOL = 1.6            # simplification tolerance, pixels
MIN_AREA = 45        # drop specks


def mask_from(path=ART, width=WIDTH, thr=0.30):
    """Only the black linework - the grey fills are the letter bodies, which stay
    flat. What gets pressed into the glass is the drawing, not the whole silhouette."""
    im = Image.open(path).convert("L")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    a = np.asarray(im, "f4") / 255.0
    m = a < thr
    return ndimage.binary_closing(m, np.ones((3, 3)))


NEIGHBOURS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def trace_boundary(m, start):
    """Moore-neighbour tracing: walk the boundary clockwise, keeping the backtrack
    pixel so each step resumes from where the last one left the shape."""
    h, w = m.shape
    p = start
    b = (start[0], start[1] - 1)          # just outside, to the left of the start
    contour = [p]
    for _ in range(400000):
        rel = (b[0] - p[0], b[1] - p[1])
        d0 = NEIGHBOURS.index(rel) if rel in NEIGHBOURS else 6
        step = None
        for k in range(1, 9):
            d = (d0 + k) % 8
            dy, dx = NEIGHBOURS[d]
            ny, nx = p[0] + dy, p[1] + dx
            if 0 <= ny < h and 0 <= nx < w and m[ny, nx]:
                pd = NEIGHBOURS[(d - 1) % 8]
                step = ((ny, nx), (p[0] + pd[0], p[1] + pd[1]))
                break
        if step is None:
            break
        p, b = step
        if p == start:
            break
        contour.append(p)
    return contour


def _rdp_open(pts, tol):
    """Douglas-Peucker on an open polyline."""
    if len(pts) < 3:
        return list(pts)
    P = np.asarray(pts, "f8")
    a, b = P[0], P[-1]
    ab = b - a
    n = float(np.hypot(*ab))
    if n < 1e-12:
        d = np.hypot(*(P - a).T)
    else:
        d = np.abs(ab[0] * (P[:, 1] - a[1]) - ab[1] * (P[:, 0] - a[0])) / n
    i = int(np.argmax(d))
    if d[i] > tol:
        return _rdp_open(pts[:i + 1], tol)[:-1] + _rdp_open(pts[i:], tol)
    return [pts[0], pts[-1]]


def rdp(pts, tol):
    """Closed ring: split at the point furthest from the start, simplify both halves.
    Running it on the ring whole would collapse it - the ends coincide."""
    if len(pts) < 4:
        return list(pts)
    P = np.asarray(pts, "f8")
    far = int(np.argmax(np.hypot(*(P - P[0]).T)))
    if far < 2 or far > len(pts) - 2:
        far = len(pts) // 2
    first = _rdp_open(pts[:far + 1], tol)
    second = _rdp_open(pts[far:], tol)
    return first[:-1] + second[:-1]


def rings(m):
    """(outer, holes) per ink blob, in pixel coordinates."""
    out = []
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() < MIN_AREA:
            continue
        ys, xs = np.nonzero(comp)
        y0 = int(ys.min())
        outer = trace_boundary(comp, (y0, int(xs[ys == y0].min())))
        filled = ndimage.binary_fill_holes(comp)
        holes = []
        hlab, hn = ndimage.label(filled & ~comp)
        for j in range(1, hn + 1):
            hole = hlab == j
            if hole.sum() < MIN_AREA:
                continue
            hy, hx = np.nonzero(hole)
            y0 = int(hy.min())
            holes.append(trace_boundary(hole, (y0, int(hx[hy == y0].min()))))
        out.append((outer, holes))
    return out


def normalise(traced, shape):
    """Centre on the artwork, scale so the long side spans 1.0, y up."""
    h, w = shape
    s = 1.0 / max(h, w)
    cx, cy = w / 2.0, h / 2.0

    def conv(ring):
        p = [((x - cx) * s, (cy - y) * s) for (y, x) in ring]
        return [tuple(map(float, q)) for q in rdp(p, TOL * s)]

    return [{"outer": conv(o), "holes": [conv(k) for k in hs]} for (o, hs) in traced]


def load():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)["shapes"]
    shapes = build()
    return shapes


def build():
    m = mask_from()
    shapes = normalise(rings(m), m.shape)
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump({"source": ART, "shapes": shapes}, f)
    return shapes


def preview(shapes, path=PREVIEW, size=760):
    im = Image.new("RGB", (size, size), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for sh in shapes:
        for ring, colour in [(sh["outer"], (20, 20, 20))] + \
                            [(k, (220, 40, 40)) for k in sh["holes"]]:
            p = [(size / 2 + x * size * 0.92, size / 2 - y * size * 0.92) for (x, y) in ring]
            if len(p) > 2:
                d.line(p + [p[0]], fill=colour, width=2)
    im.save(path)
    return path


if __name__ == "__main__":
    shapes = build()
    pts = sum(len(s["outer"]) + sum(len(k) for k in s["holes"]) for s in shapes)
    print("%d shapes, %d holes, %d points" %
          (len(shapes), sum(len(s["holes"]) for s in shapes), pts))
    print("preview:", preview(shapes))
