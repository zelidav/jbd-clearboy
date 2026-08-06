"""Re-render a remodel request as a real variant. The original is never touched.

Takes the same numbers the remodeller on the site produces, rebuilds the solid at those
dimensions, renders a 72-position turntable, encodes it, and registers the variant so the
site picks it up next time build_web runs.

    python variant.py '{"piece":"hammer","way":"teal_silver","label":"short stem",
                        "dims":{"height":126,"headlen":74,"stemod":16}}'
    python variant.py request.json

Any dimension you leave out keeps its original value. Output lands in
out/<id>.*, frames/<id>_<way>/, docs/spin/<id>_<way>/, docs/video/<id>_<way>.mp4
and docs/variants.json.
"""
import json, os, re, sys

import cadquery as cq

VARIANTS = os.path.join("docs", "variants.json")

HAMMER_BASE = dict(height=140.0, headlen=68.0, headsec=42.0, stemod=14.0,
                   bowlid=25.0, footod=24.5, stemlen=88.0, marbles=4, scatter=0,
                   lines=5, linepitch=6.0)
JAR_BASE = dict(height=92.0, mouthid=38.0, wall=3.0, fritz=25.0, corkh=20.0, marbles=7,
                lines=18, linepitch=1.9)


def slug(text, fallback):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (s or fallback)[:32]


# ---------------------------------------------------------------- hammer
def build_hammer(d, out, vid):
    import model, decor, frit
    p = dict(HAMMER_BASE); p.update(d)
    if "stemlen" in d and "height" not in d:        # stem length drives the overall height
        p["height"] = HAMMER_BASE["height"] + (p["stemlen"] - HAMMER_BASE["stemlen"])
    k_len = p["headlen"] / HAMMER_BASE["headlen"]
    k_sec = p["headsec"] / HAMMER_BASE["headsec"]
    dz = p["height"] - HAMMER_BASE["height"]

    model.SECTIONS = [(x * k_len, h * k_sec, w * k_sec, cz + dz)
                      for (x, h, w, cz) in model.SECTIONS]
    model.HEAD_X0 *= k_len
    model.HEAD_X1 *= k_len
    model.STEM_TOP += dz
    model.COLLAR_Z += dz
    model.STEM_OD = p["stemod"]
    model.BOWL_ID = p["bowlid"]
    model.FOOT_OD = p["footod"]
    model.COLLAR_OD = p["stemod"] + 3.5
    model.BOWL_DEPTH = min(model.BOWL_DEPTH * k_len, model.HEAD_X1 * 0.55 + 12)

    body = model.build()
    body_path = os.path.join(out, "%s.stl" % vid)
    cq.exporters.export(body, body_path, tolerance=0.03, angularTolerance=0.12)
    cq.exporters.export(body, os.path.join(out, "%s.step" % vid))

    # frit and marbles follow the head
    decor.RIM_X = model.HEAD_X1 - 1.5
    frit.FRIT_X1 = decor.RIM_X + 0.5
    frit.FRIT_X0 *= k_len
    n = int(p["marbles"])
    frit.MARBLES = [(x * k_len, th, r) for (x, th, r) in frit.MARBLES]

    frit_path = os.path.join(out, "%s_frit.stl" % vid)
    marb_path = os.path.join(out, "%s_marbles.stl" % vid)
    frit.build_frit().export(frit_path)
    frit.build_marbles(n=n, seed=int(p["scatter"])).export(marb_path)

    import linework
    lines_path = os.path.join(out, "%s_lines.stl" % vid)
    linework.hammer_spiral(turns=p["lines"], pitch=p["linepitch"]).export(lines_path)
    return dict(body=body_path, frit=frit_path, marbles=marb_path,
                lines_body=lines_path, lines_frit=lines_path,
                cam_r=700.0 + max(dz, 0) * 2.2, target=(0, 0, 74 + dz * 0.55),
                fov=17.0, shadow=(0.5, 0.30, 0.075), decal=(20.0, 74.0, p["stemod"] / 2))


# ---------------------------------------------------------------- jar
def build_jar(d, out, vid):
    import jar
    p = dict(JAR_BASE); p.update(d)
    jar.HEIGHT = p["height"]
    jar.MOUTH_ID = p["mouthid"]
    jar.WALL = p["wall"]
    jar.OD = jar.MOUTH_ID + 2 * jar.WALL
    jar.FRIT_Z = (p["height"] - p["fritz"], p["height"] - 1.5)
    jar.MARBLE_Z = p["height"] - 7.5
    jar.N_MARBLES = int(p["marbles"]) or 1
    jar.MARBLE_R = 4.0 if p["marbles"] else 0.001
    jar.STAMP_Z = p["height"] * 0.30
    jar.CAP_H = max(p["corkh"] - 12.0, 4.0)
    jar.CORK_D_BOT = jar.MOUTH_ID - 1.0
    jar.CORK_D_TOP = jar.MOUTH_ID + 1.6
    jar.CAP_D = jar.OD + 2.0

    body = jar.build()
    body_path = os.path.join(out, "%s.stl" % vid)
    cq.exporters.export(body, body_path, tolerance=0.03, angularTolerance=0.12)
    cq.exporters.export(body, os.path.join(out, "%s.step" % vid))
    cork_path = os.path.join(out, "%s_cork.stl" % vid)
    cq.exporters.export(jar.build_cork(), cork_path, tolerance=0.03, angularTolerance=0.12)
    frit_path = os.path.join(out, "%s_frit.stl" % vid)
    marb_path = os.path.join(out, "%s_marbles.stl" % vid)
    jar.build_frit().export(frit_path)
    jar.build_marbles().export(marb_path)

    import linework
    body_lines = os.path.join(out, "%s_lines.stl" % vid)
    frit_lines = os.path.join(out, "%s_lines_frit.stl" % vid)
    linework.spiral(turns=p["lines"], pitch=p["linepitch"],
                    top=p["height"] - 4.0).export(body_lines)
    linework.spiral(turns=9, pitch=2.4, minor=0.30, top=p["height"] - 2.0,
                    bottom=p["height"] - 26.0, seed=12, proud=1.15).export(frit_lines)
    top = p["height"] + p["corkh"]
    return dict(body=body_path, frit=frit_path, marbles=marb_path, cork=cork_path,
                lines_body=body_lines, lines_frit=frit_lines,
                cam_r=650.0 + max(top - 112.0, 0) * 2.4, target=(0, 0, top * 0.51),
                fov=17.0, shadow=(0.5, 0.32, 0.130), decal=None)


BUILDERS = {"hammer": build_hammer, "jar": build_jar}


def run(req, frames_n=72):
    piece = req.get("piece", "hammer")
    way = req.get("way", "teal_silver")
    dims = {k: float(v) for k, v in (req.get("dims") or {}).items()}
    vid = "v-" + slug(req.get("label"), piece + "-variant")
    os.makedirs("out", exist_ok=True)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mockups, turntable, encode, render          # noqa: E402

    spec = BUILDERS[piece](dims, "out", vid)
    spec["name"] = req.get("label") or (piece + " variant")
    spec["note"] = req.get("notes", "")
    mockups.PIECES[vid] = spec                          # registered, original untouched

    turntable.spin(vid, way, frames_n)
    mockups.shot(vid, way)
    encode.mp4("%s_%s" % (vid, way))
    encode.spin("%s_%s" % (vid, way))

    reg = []
    if os.path.exists(VARIANTS):
        with open(VARIANTS, encoding="utf-8") as f:
            reg = json.load(f)
    reg = [r for r in reg if not (r["id"] == vid and r["way"] == way)]
    reg.append(dict(id=vid, way=way, piece=piece, label=spec["name"],
                    notes=spec["note"], dims=dims))
    os.makedirs("docs", exist_ok=True)
    with open(VARIANTS, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=1)
    print("variant %s (%s) rendered and registered" % (vid, way))
    return vid


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    arg = sys.argv[1]
    if os.path.exists(arg):
        with open(arg, encoding="utf-8") as f:
            req = json.load(f)
    else:
        req = json.loads(arg)
    run(req)
