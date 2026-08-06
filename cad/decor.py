"""Colour-matched drip work + bumps around the bowl end of the head."""
import math, os, sys
import cadquery as cq
from model import SECTIONS, SUPER_N, _interp, HEAD_X1

RIM_X = HEAD_X1 - 1.5


def surface_pt(x, theta, out=0.0):
    """Point on the head skin at station x, angle theta (0 = +Y, pi/2 = +Z)."""
    h, w, cz = _interp(x, 0.0)
    a, b = w/2.0 + out, h/2.0 + out
    ct, st = math.cos(theta), math.sin(theta)
    n = SUPER_N
    y = a*math.copysign(abs(ct)**(2.0/n), ct)
    z = b*math.copysign(abs(st)**(2.0/n), st)
    return (x, y, cz + z)


def drip(theta, length, r0=1.5, r1=2.7, tail=1.0, steps=15, start=RIM_X):
    """A single run of glass off the rim: swells as it goes, ends in a bead."""
    balls = []
    for i in range(steps + 1):
        t = i/steps
        x = start - t*length
        # radius: thin at the rim, swelling toward the bead, then the bead itself
        if t < 0.82:
            r = r0 + (r1 - r0)*(t/0.82)**1.5
        else:
            r = r1*tail*(1.0 + 0.30*math.sin((t - 0.82)/0.18*math.pi))
        p = surface_pt(x, theta, out=-r*0.34)
        balls.append((p, r))
    s = None
    for (p, r) in balls:
        b = cq.Workplane("XY").sphere(r).translate(p)
        s = b if s is None else s.union(b)
    return s


def bump(x, theta, r=1.55):
    p = surface_pt(x, theta, out=-r*0.42)
    return cq.Workplane("XY").sphere(r).translate(p)


def build():
    parts = []
    # six drips around the bowl end, uneven like hand work
    plan = [
        (math.radians(90),  23.0, 2.6, 4.0, 1.00),
        (math.radians(30),  19.0, 2.5, 3.7, 0.96),
        (math.radians(150), 21.0, 2.5, 3.8, 0.98),
        (math.radians(215), 16.0, 2.4, 3.5, 0.94),
        (math.radians(-55), 18.0, 2.5, 3.6, 0.95),
        (math.radians(270), 14.0, 2.3, 3.3, 0.92),
    ]
    for (th, L, r0, r1, tl) in plan:
        parts.append(drip(th, L, r0, r1, tl))

    # a ring of small bumps just behind the rim
    for i in range(8):
        th = 2*math.pi*i/8 + 0.42
        parts.append(bump(RIM_X - 2.0, th, 2.20 + 0.30*((i % 3) == 0)))
    # a looser scatter further down the bowl area
    for i, (xx, th, rr) in enumerate([(19.0, 0.9, 2.1), (16.0, 2.7, 2.0),
                                      (20.5, 4.4, 2.15), (15.0, 5.6, 1.9),
                                      (17.5, 3.6, 2.05)]):
        parts.append(bump(xx, th, rr))

    s = parts[0]
    for p in parts[1:]:
        s = s.union(p)
    import model
    return s.cut(model.build())   # trim everything buried inside the head


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(out, exist_ok=True)
    d = build()
    cq.exporters.export(d, os.path.join(out, "decor.stl"),
                        tolerance=0.02, angularTolerance=0.15)
    cq.exporters.export(d, os.path.join(out, "decor.step"))
    print("decor volume mm^3:", round(d.val().Volume(), 1))
