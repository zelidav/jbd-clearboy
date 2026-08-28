"""Render every turntable the site serves, for every revision.

One entry point so the frames cannot drift out of step with the geometry - which is
exactly what happened to the joint holder, whose spinner and hero still were both
rendered before the piece dropped its frit bell and then sat there looking fritted on a
page that said it carried none.

    python cad/spin_all.py            # everything, 72 frames
    python cad/spin_all.py 24 revb    # one revision, coarser
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import turntable
from mockups import WAYS

# the hammer is served as a roll x tilt sheet - drag sideways to roll it, up and down
# to tip it between standing and laid down - so it is rendered as a grid, not a spin.
# Everything else is a plain turntable.
GRID = ["hammer"]
REV_A = ["hammer", "jar", "tube", "tube_loaded", "box", "lighter",
         "lighter_loaded", "holder", "tip", "tip_spiral"]
REV_B = ["hammer", "jar"]                      # the rest carry no frit either way
POSED = ["pose135"]                            # its own tab, its own spinner
# The collab pieces carry a colourway of their own, and it is not offered on anything
# else - so it is rendered for those three and nowhere near the general sweep.
COLLAB = ["tube", "tube_loaded", "box"]
COLLAB_WAY = "puff_blue"


def jobs():
    ways = [w for w in WAYS if w != COLLAB_WAY]
    out = [(pc, w, True, "") for pc in REV_A for w in ways]
    out += [(pc, COLLAB_WAY, True, "") for pc in COLLAB]
    out += [(pc, w, False, "_revb") for pc in REV_B for w in ways]
    out += [(pc, w, False, "_revb") for pc in POSED
            for w in ("magenta_gold", "teal_silver")]
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    n = next((int(a) for a in args if a.isdigit()), 72)
    only = [a for a in args if a in ("reva", "revb", "posed")]
    js = jobs()
    if only:
        pick = []
        if "reva" in only:
            pick += [j for j in js if j[3] == ""]
        if "revb" in only:
            pick += [j for j in js if j[3] == "_revb" and j[0] not in POSED]
        if "posed" in only:
            pick += [j for j in js if j[0] in POSED]
        js = pick
    t0 = time.time()
    for i, (pc, w, frit, tag) in enumerate(js):
        print("[%d/%d]" % (i + 1, len(js)), flush=True)
        out = os.path.join(turntable.FRAMES, "%s_%s%s" % (pc, w, tag))
        if os.path.isdir(out):        # never leave a grid and a spin in the same folder
            for f in os.listdir(out):
                os.remove(os.path.join(out, f))
        if pc in GRID:
            turntable.grid(pc, w, 24, frit=frit, out=out)
        else:
            turntable.spin(pc, w, n, frit=frit, tag=tag)
    print("all turntables done in %.1f min" % ((time.time() - t0) / 60.0), flush=True)
