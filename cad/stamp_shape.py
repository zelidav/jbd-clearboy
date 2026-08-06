"""Trace the real stamp's outline out of the photograph.

assets/jbd_stamp_photo.png is a specular shot of the pressed mark - the lettering is
unreadable in it, but the outline of the pressed area is. This segments that blob off
the background and turns it into a closed profile the CAD build can press into the jar
wall, so the die face is the real shape rather than an invented one.

    python stamp_shape.py            -> cad/stamp_outline.json + a preview PNG
"""
import json, math, os, sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PHOTO = os.path.join("assets", "jbd_stamp_photo.png")
CACHE = os.path.join("cad", "stamp_outline.json")
PREVIEW = os.path.join("assets", "jbd_stamp_outline.png")
RAYS = 128


def mask_from(photo=PHOTO, q=0.62):
    """The glass around the mark reads warm; the pressed area does not. Split on that,
    then smooth hard - we want the silhouette of the press, not every reflection in it."""
    from scipy import ndimage
    im = Image.open(photo).convert("RGB").filter(ImageFilter.MedianFilter(7))
    a = np.asarray(im, dtype="f4") / 255.0
    warmth = (a[..., 0] + a[..., 1]) / 2.0 - a[..., 2]
    m = warmth < float(np.quantile(warmth, q))
    m = ndimage.binary_closing(m, np.ones((15, 15)))
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, np.ones((11, 11)))
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    return ndimage.binary_fill_holes(m)


def outline(m, rays=RAYS):
    """Radial trace from the centroid: robust on a blob, and closed by construction."""
    ys, xs = np.nonzero(m)
    cy, cx = ys.mean(), xs.mean()
    h, w = m.shape
    reach = math.hypot(h, w)
    pts = []
    for i in range(rays):
        t = 2 * math.pi * i / rays
        dx, dy = math.cos(t), math.sin(t)
        last = 0.0
        r = 2.0
        while r < reach:
            x, y = int(round(cx + dx * r)), int(round(cy + dy * r))
            if 0 <= x < w and 0 <= y < h and m[y, x]:
                last = r
            r += 1.0
        pts.append(last)
    pts = np.asarray(pts)
    # smooth the ray lengths so the spline does not chase pixel noise
    k = np.array([1, 2, 4, 6, 7, 6, 4, 2, 1], dtype="f4"); k /= k.sum()
    pad = len(k) // 2
    pts = np.convolve(np.concatenate([pts[-pad:], pts, pts[:pad]]), k, "valid")
    pts = pts / pts.max()
    return [(float(math.cos(2 * math.pi * i / rays) * r),
             float(math.sin(2 * math.pi * i / rays) * r)) for i, r in enumerate(pts)]


def load(rays=RAYS):
    """Unit-radius outline, x right, y up. Cached so the CAD build needs no image."""
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)["points"]
    pts = outline(mask_from(), rays)
    save(pts)
    return pts


def save(pts):
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump({"source": PHOTO, "points": pts}, f)


def preview(pts, photo=PHOTO, path=PREVIEW):
    im = Image.open(photo).convert("RGB")
    w, h = im.size
    d = ImageDraw.Draw(im)
    sx, sy = w / 2.0, h / 2.0
    poly = [(sx + x * sx * 0.98, sy - y * sy * 0.98) for (x, y) in pts]
    d.line(poly + [poly[0]], fill=(255, 40, 40), width=4)
    im.save(path)
    return path


if __name__ == "__main__":
    pts = outline(mask_from())
    save(pts)
    print("traced %d points -> %s" % (len(pts), CACHE))
    print("preview:", preview(pts))
