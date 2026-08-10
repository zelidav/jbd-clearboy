"""Joint holder cut sheets - twelve designs, six to a sheet.

Each design is a different solid, not just a different colour, so every one is rebuilt
from cad/holder.py at its own dimensions before it is rendered. That is slow and it is
the point: what is on the sheet is what the shop would make.

    python cad/cutsheet.py        -> shots/holder/*.png, shots/JBD_Joint_Holder.pdf
    python cad/cutsheet.py render  -> just the renders
"""
import os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet
from sheet import PAGE, INK, PAPER, RULE, GREY, RED

OUT = os.path.join("shots", "holder")
PDF = os.path.join("shots", "JBD_Joint_Holder.pdf")
TMP = os.path.join("out", "holder_variants")
SIZE = (1200, 520)
HANG = (620, 1000)
HANG_YAW = 1.45          # the yaw that brings the bail round into view


def build_one(name, geom):
    """Rebuild the solid and its decoration at this design's dimensions."""
    import cadquery as cq
    import holder
    os.makedirs(TMP, exist_ok=True)
    k = name
    body = os.path.join(TMP, "%s.stl" % k)
    if not os.path.exists(body):
        cq.exporters.export(holder.build(geom), body,
                            tolerance=0.03, angularTolerance=0.12)
        holder.build_marbles(geom).export(os.path.join(TMP, "%s_marbles.stl" % k))
        for i, m in enumerate(holder.build_spin(geom)):
            m.export(os.path.join(TMP, "%s_spin%d.stl" % (k, i)))
        a, b = holder.build_bling(geom)
        for tag, m in (("bling", a), ("bling2", b)):
            if len(m.faces):
                m.export(os.path.join(TMP, "%s_%s.stl" % (k, tag)))
    spin = [os.path.join(TMP, "%s_spin%d.stl" % (k, i))
            for i in range(int(geom.get("spin", 3)))]
    return dict(body=body, frit=None,
                marbles=os.path.join(TMP, "%s_marbles.stl" % k),
                spin=[q for q in spin if os.path.exists(q)],
                bling=os.path.join(TMP, "%s_bling.stl" % k),
                bling2=os.path.join(TMP, "%s_bling2.stl" % k))


def render_all():
    import mockups, holder_designs as D
    os.makedirs(OUT, exist_ok=True)
    D.register(mockups)
    made = []
    for _, group in D.GROUPS:
        for nm, _b, _f, _fr, _s, geom, _wn, _ws in group:
            k = D.key(nm)
            p = os.path.join(OUT, "%s.png" % k)
            paths = build_one(k, geom)
            if not os.path.exists(p):
                # the piece entry is the standing framing laid over; only the meshes
                # change between designs
                mockups.PIECES[k] = dict(mockups.PIECES["holder"], **paths)
                im = mockups.frame(
                    mockups.build_renderer(k, k, *SIZE), k, mockups.SIDE)
                im.save(p)
                print("rendered", k, im.size)
            made.append((k, p))
    return made


def render_hang(keys):
    """The pendant view: hung from the bail, mouthpiece up, bell down. Yawed so the
    ring reads - broadside it sits behind the tube, which is where it belongs on the
    piece and no use at all on a sheet."""
    import mockups, holder_designs as D
    D.register(mockups)
    geoms = dict((D.key(g[0]), g[5]) for _, grp in D.GROUPS for g in grp)
    out = []
    for k in keys:
        p = os.path.join(OUT, "%s_hang.png" % k)
        if not os.path.exists(p):
            paths = build_one(k, geoms[k])
            mockups.PIECES[k] = dict(mockups.PIECES["holder"], **paths)
            hk = k + "_hang"
            mockups.PIECES[hk] = dict(mockups.PIECES[k], tilt=180.0, shift=None,
                                      target=(0, 0, -geoms[k].get("length", 90) / 2.0),
                                      cam_r=380.0, size=HANG)
            q = mockups.PIECES[hk]
            im = mockups.build_renderer(hk, k, *HANG).frame(
                HANG_YAW, cam_r=q["cam_r"], target=q["target"], fov=q["fov"],
                shadow=q["shadow"], tilt=q["tilt"])
            im.save(p)
            print("rendered", hk)
        out.append((k, p))
    return out


def hang_page(keys, n, total):
    pg, d = sheet.blank()
    d.text((96, 62), "JEROME BAKER DESIGNS", font=sheet.font(True, 26), fill=INK)
    d.line([(96, 122), (PAGE[0] - 96, 122)], fill=RULE, width=2)
    d.text((96, 152), "Wears as a pendant", font=sheet.font(True, 44), fill=INK)
    d.text((96, 212), "A ring at the mouthpiece takes a chain. It sits on the back "
           "face, opposite the marbles, so it hangs bell-down with the stones facing "
           "out.", font=sheet.font(False, 24), fill=GREY)
    tag = "Joint holder  ·  cut sheet  ·  %d / %d" % (n, total)
    f = sheet.font(False, 20)
    d.text((PAGE[0] - 96 - d.textlength(tag, font=f), 92), tag, font=f, fill=GREY)
    import holder_designs as D
    named = dict((D.key(g[0]), g[0]) for _, grp in D.GROUPS for g in grp)
    for i, (k, path) in enumerate(render_hang(keys)):
        x = 150 + i * 470
        if os.path.exists(path):
            art = sheet.fit(Image.open(path).convert("RGB"), (420, 780))
            pg.paste(art, (x + (420 - art.width) // 2, 280))
        d.text((x, 1000), named.get(k, k), font=sheet.font(True, 26), fill=INK)
    d.line([(96, PAGE[1] - 74), (PAGE[0] - 96, PAGE[1] - 74)], fill=RULE, width=1)
    d.text((96, PAGE[1] - 60), "Ring 8 mm outside, 1.45 mm section  ·  clears a "
           "2 mm chain  ·  renders, not photographs",
           font=sheet.font(False, 19), fill=GREY)
    return pg


def _card(pg, d, box, name, sub, note, geom, path, accent):
    x, y, w, h = box
    pg.paste(Image.new("RGB", (w, h), (255, 255, 255)), (x, y))
    if os.path.exists(path):
        art = sheet.fit(Image.open(path).convert("RGB"), (w - 24, h - 150))
        pg.paste(art, (x + (w - art.width) // 2, y + 14))
    d.text((x + 20, y + h - 146), name, font=sheet.font(True, 27), fill=INK)
    d.text((x + 20, y + h - 110), sub, font=sheet.font(False, 20), fill=accent)
    d.multiline_text((x + 20, y + h - 78), sheet.wrap(
        d, note, sheet.font(False, 18), w - 44)[0],
        font=sheet.font(False, 18), fill=GREY, spacing=5)
    spec = "%d mm  ·  bell %.0f  ·  %d marbles%s" % (
        geom.get("length", 90), geom.get("bell_od", 23), geom.get("marbles", 3),
        ("  ·  %d stones" % geom["bling"]) if geom.get("bling") else "")
    d.line([(x + 20, y + h - 40), (x + w - 20, y + h - 40)], fill=(230, 230, 232))
    d.text((x + 20, y + h - 32), spec, font=sheet.font(True, 17), fill=accent)


def sheet_page(title, sub, group, n, total, accent):
    pg, d = sheet.blank()
    d.text((96, 62), "JEROME BAKER DESIGNS", font=sheet.font(True, 26),
           fill=INK)
    d.line([(96, 122), (PAGE[0] - 96, 122)], fill=RULE, width=2)
    d.text((96, 152), title, font=sheet.font(True, 44), fill=INK)
    d.text((96, 212), sub, font=sheet.font(False, 24), fill=GREY)
    tag = "Joint holder  ·  cut sheet  ·  %d / %d" % (n, total)
    f = sheet.font(False, 20)
    d.text((PAGE[0] - 96 - d.textlength(tag, font=f), 92), tag, font=f, fill=GREY)

    import holder_designs as D
    cw, ch, gap = 468, 430, 26
    for i, (nm, _b, _f, _fr, _s, geom, wn, ws) in enumerate(group):
        x = 96 + (i % 3) * (cw + gap)
        y = 268 + (i // 3) * (ch + gap)
        _card(pg, d, (x, y, cw, ch), nm, wn, ws, geom,
              os.path.join(OUT, "%s.png" % D.key(nm)), accent)
    d.line([(96, PAGE[1] - 74), (PAGE[0] - 96, PAGE[1] - 74)], fill=RULE, width=1)
    d.text((96, PAGE[1] - 60), "Every design rebuilt at its own dimensions  ·  spun linework, "
           "no frit  ·  renders, not photographs",
           font=sheet.font(False, 19), fill=GREY)
    return pg


def build():
    import holder_designs as D
    render_all()
    pages = [
        sheet_page("Joint holder", "A roaring-twenties holder for a joint. The bell "
                   "grips anything from a pinner to a fat one.", D.FEMININE, 1, 3,
                   (176, 26, 38)),
        sheet_page("Joint holder", "The same piece drawn heavier, and iced.",
                   D.MASCULINE, 2, 3, (24, 24, 26)),
    ]
    pages.append(hang_page(["belle_epoque", "bussdown", "iced_out"], 3, 3))
    for i, pg in enumerate(pages[:2]):
        pass
    sheet.save(pages, PDF, "JBD joint holder - cut sheet")
    return PDF


if __name__ == "__main__":
    if "render" in sys.argv[1:]:
        render_all()
    else:
        build()
