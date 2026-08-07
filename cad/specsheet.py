"""Manufacturing spec sheet - the sheet that goes to the shop with the STEP.

Everything here is the build spec, not the survey. Where the two differ - the stem was
thickened to carry the enamel label, the hole in the bottom of the bowl was called
down - the original's measured figure is printed alongside so nobody quietly corrects
it back on the bench.

    python cad/specsheet.py     -> shots/JBD_Clearboy_spec.pdf, docs/JBD_Clearboy_spec.pdf
"""
import glob, os, shutil, sys, zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet
from sheet import INK, PAPER, RULE, GREY, RED, PAGE

OUT = os.path.join("shots", "JBD_Clearboy_spec.pdf")
SITE = os.path.join("docs", "JBD_Clearboy_spec.pdf")
PACK = os.path.join("shots", "JBD_Clearboy_pack.zip")
PACK_SITE = os.path.join("docs", "JBD_Clearboy_pack.zip")
REV = "Rev A"

# (group, dimension, value, note) - note "" prints nothing, and carries the places where
# the build departs from the measured original
HAMMER = [
    ("Overall", "Height, standing on the foot", "140 mm", "5.51 in"),
    ("Overall", "Length, laid down", "140 mm", ""),
    ("Overall", "Glass", "Borosilicate 3.3", "clear stock, fumed"),
    ("Overall", "Finished mass", "≈ 81 g", "from the solid model"),
    ("Head", "Chamber length", "68 mm", "62–71 across views — hand-shaped"),
    ("Head", "Max section", "42 × 37 mm", "oval, not a cylinder"),
    ("Head", "Wall", "≈ 3 mm", "INFERRED — confirm before tooling"),
    ("Stem", "Tube OD", "ø 14 mm", "original measured ø 11 — thickened for the label"),
    ("Stem", "Bore ID", "ø 8 mm", "wall ≈ 3 mm"),
    ("Stem", "Exposed length", "88 mm", "foot face to the head"),
    ("Stem", "Foot / mouthpiece disc", "ø 24.5 × 7 mm", "edges broken 1.6 mm"),
    ("Bowl", "Opening ID at the rim", "ø 25 mm", ""),
    ("Bowl", "Depth, rim to the hole", "19 mm", ""),
    ("Bowl", "Hole in the bottom of the bowl", "ø 3 mm", "original measured ø 5"),
    ("Bowl", "Carb hole", "ø 3.5 mm", "on a ø 11 boss, 14 mm below the rim"),
]

JAR = [
    ("Body", "Glass height, rim to bench", "92 mm", ""),
    ("Body", "Outside diameter", "ø 44 mm", "straight cylinder, no shoulder"),
    ("Body", "Wall", "3 mm", ""),
    ("Body", "Floor", "3 mm", "flat, closed"),
    ("Body", "Glass", "Borosilicate 3.3", "clear stock, fumed"),
    ("Body", "Finished mass", "≈ 90 g", "glass only"),
    ("Mouth", "Opening ID", "ø 38 mm", "the spec the cork is cut to"),
    ("Cork", "Overall length", "27 mm", "natural cork, no mushroom cap"),
    ("Cork", "Diameter, bottom / top", "ø 36.6 / ø 41 mm", "seats on the taper"),
    ("Cork", "Seat depth in the mouth", "15 mm", "≈ 12 mm stands proud"),
    ("Cork", "Mass", "≈ 10 g", ""),
]

DECOR = [
    ("Hammer", "Frit", "Rolled over the bowl end of the head — the outer 54 mm of the "
                       "68 mm chamber, densest at the rim. Worked in, not a coating."),
    ("Hammer", "Marbles", "4 clear marbles, ø 6.5–7.5, set into the fritted band. "
                          "Hand-placed, not evenly spaced."),
    ("Hammer", "Label", "Enamel, on the stem, 20–74 mm up from the foot face. JBD × Boutiq "
                        "dropped out in white. The print reads one way along the stem — strike "
                        "it to read with the head to the left."),
    ("Jar", "Frit", "Band around the opening, 66–90.5 mm up from the base."),
    ("Jar", "Marbles", "7 clear marbles, ø 8, evenly spaced, centres 84.5 mm up."),
    ("Jar", "Mark", "JBD pressed into a molten stamp pad, lower middle, centre 28 mm up. "
                    "Die face ≈ 28 × 11 mm; the mark itself runs ≈ 25 mm wide."),
]

NOTES = [
    "Hand-blown. The figures above are nominal targets, not machined tolerances — the "
    "head is deliberately oval and varies 5–10% between views on the original.",
    "Hold these four: bowl opening ø 25, hole in the bottom of the bowl ø 3, stem bore "
    "ø 8, jar mouth ø 38. Everything else can move with the glass.",
    "Chamber wall is inferred, not measured. Two caliper readings on the original — rim "
    "and stem OD — lock the whole model; mass, volume and glass cost all move if they "
    "come back different.",
    "Supplied with this sheet: clearboy_hammer.step / .stl and jar.step / .stl, plus the "
    "frit, marble and cork meshes. STEP is the reference; the meshes are for print and "
    "mould work only.",
]

WAYS = [("teal_silver", "Bluish teal body, silver fume. Teal frit, clear marbles."),
        ("magenta_gold", "Magenta body, gold fume. Magenta frit, clear marbles.")]


def _head(d, title, sub, page_no, pages=None):
    sheet.lockup(d, 250, 78, 26, INK)
    d.line([(96, 122), (PAGE[0] - 96, 122)], fill=RULE, width=2)
    d.text((96, 158), title, font=sheet.font(True, 46), fill=INK)
    d.text((96, 222), sub, font=sheet.font(False, 25), fill=GREY)
    tag = "%s  ·  Clearboy programme  ·  %d / %d" % (REV, page_no, pages or TOTAL)
    f = sheet.font(False, 20)
    d.text((PAGE[0] - 96 - d.textlength(tag, font=f), 92), tag, font=f, fill=GREY)
    d.line([(96, PAGE[1] - 74), (PAGE[0] - 96, PAGE[1] - 74)], fill=RULE, width=1)
    d.text((96, PAGE[1] - 60), "Jerome Baker Designs · manufacturing spec — "
           "figures in millimetres unless marked", font=sheet.font(False, 19), fill=GREY)


def _table(d, rows, x, y, w, lead=42, notes=True):
    """Grouped dimension table. The group name prints once, on its first row."""
    last = None
    fk, fv, fn = sheet.font(True, 21), sheet.font(True, 24), sheet.font(False, 20)
    vx = x + int(w * 0.44)
    nx = x + int(w * 0.66)
    for group, name, value, note in rows:
        if group != last:
            if last is not None:
                y += 16
            d.text((x, y + 3), group.upper(), font=sheet.font(True, 19), fill=RED)
            y += 32
            last = group
        d.text((x + 18, y), name, font=fn, fill=INK)
        d.text((vx, y - 2), value, font=fv, fill=INK)
        lines = 1
        if note and notes:
            hot = note.startswith("INFERRED") or note.startswith("original")
            txt, lines = sheet.wrap(d, note, fk if hot else fn, x + w - nx)
            d.multiline_text((nx, y + 2), txt, font=fk if hot else fn,
                             fill=RED if hot else GREY, spacing=6)
        y += lead + (lines - 1) * 26
        d.line([(x, y - 12), (x + w, y - 12)], fill=RULE, width=1)
    return y


def _page_hammer(n):
    pg, d = sheet.blank()
    _head(d, "Clearboy hammer bubbler", "Hand-blown boro 3.3 · 140 mm · "
          "one-piece head, stem and foot", n)
    _table(d, HAMMER, 96, 290, 1460)
    return pg


def _page_survey(n):
    pg, d = sheet.blank()
    _head(d, "Dimensional survey", "The original piece, measured photogrammetrically "
          "against a stainless rule — the reference the build was drawn from", n)
    p = "JBD_Clearboy_dimensions.png"
    if os.path.exists(p):
        im = sheet.fit(Image.open(p).convert("RGB"), (PAGE[0] - 192, PAGE[1] - 400))
        pg.paste(im, ((PAGE[0] - im.width) // 2, 285))
    else:
        d.text((96, 300), "JBD_Clearboy_dimensions.png not found",
               font=sheet.font(False, 26), fill=RED)
    return pg


def _page_jar(n):
    pg, d = sheet.blank()
    _head(d, "Nug jar and cork", "Straight cylinder, flat closed bottom, tapered "
          "natural cork · 92 mm glass", n)
    y = _table(d, JAR, 96, 290, 1000)
    p = os.path.join("shots", "jar_teal_silver.png")
    if os.path.exists(p):
        im = sheet.fit(Image.open(p).convert("RGB"), (380, 640))
        pg.paste(im, (PAGE[0] - im.width - 110, 300))
    _notes(d, y + 46)
    return pg


def _page_decor(n):
    pg, d = sheet.blank()
    _head(d, "Decoration and colourways", "Frit, marbles, the enamel label and the "
          "pressed mark — both colourways carry the same work", n)
    f = sheet.font(False, 21)
    y = 300
    last = None
    for who, what, how in DECOR:
        if who != last:
            d.text((96, y), who.upper(), font=sheet.font(True, 19), fill=RED)
            y += 32
            last = who
        d.text((114, y), what, font=sheet.font(True, 22), fill=INK)
        txt, n = sheet.wrap(d, how, f, 1240)
        d.multiline_text((300, y), txt, font=f, fill=INK, spacing=9)
        y += 42 + 30 * (n - 1)
        d.line([(96, y - 12), (1554, y - 12)], fill=RULE, width=1)
        y += 8

    sys.path.insert(0, "cad")
    import mockups
    y += 26
    d.text((96, y), "COLOURWAYS", font=sheet.font(True, 19), fill=RED)
    y += 34
    for key, text in WAYS:
        d.text((114, y), mockups.WAYS[key]["name"], font=sheet.font(True, 22), fill=INK)
        d.text((520, y + 2), text, font=f, fill=GREY)
        y += 44

    x = 114
    for piece, way in (("hammer", "magenta_gold"), ("jar", "teal_silver")):
        p = os.path.join("shots", "%s_%s.png" % (piece, way))
        if os.path.exists(p):
            im = sheet.fit(Image.open(p).convert("RGB"), (300, PAGE[1] - y - 130))
            pg.paste(im, (x, y + 20))
            x += im.width + 60
    return pg


def _notes(d, y):
    f = sheet.font(False, 21)
    d.text((96, y - 40), "NOTES", font=sheet.font(True, 19), fill=RED)
    for i, n in enumerate(NOTES):
        txt, lines = sheet.wrap(d, n, f, 1400)
        d.text((96, y), "%d" % (i + 1), font=sheet.font(True, 21), fill=RED)
        d.multiline_text((126, y), txt, font=f, fill=INK, spacing=8)
        y += 30 * lines + 12



CLOSEUPS = [
    ("head", "Head and bowl",
     "Chamber length, section, bowl opening and the carb, taken off the solid model."),
    ("bowl", "Bowl end",
     "Looking straight down the head axis at the opening and the hole beneath it."),
    ("stem", "Stem, foot and label band",
     "Where the enamel band sits, and the disc the piece stands on."),
    ("jar_body", "Nug jar elevation",
     "Body, mouth, frit band and the marbles set around the opening."),
    ("jar_cork", "Mouth and cork",
     "The taper the cork seats on, and how far it stands proud."),
]


def _page_closeup(n, key, title, sub):
    pg, d = sheet.blank()
    _head(d, title, sub, n)
    p = os.path.join("shots", "spec", key + ".png")
    if os.path.exists(p):
        im = sheet.fit(Image.open(p).convert("RGB"), (PAGE[0] - 220, PAGE[1] - 400))
        pg.paste(im, ((PAGE[0] - im.width) // 2, 280))
        d.rectangle([(PAGE[0] - im.width) // 2 - 1, 279,
                     (PAGE[0] + im.width) // 2, 280 + im.height],
                    outline=RULE, width=1)
    else:
        d.text((96, 300), "missing " + p, font=sheet.font(False, 26), fill=RED)
    return pg



# ---------------------------------------------------------------------- process

# The bench sequence. Outcomes and hold points are ours; the shop's own working order
# governs where the two disagree - what must not move is the numbered checks.
SOP_HAMMER = [
    ("Stock", [
        "Borosilicate 3.3 throughout. Chamber off tube nominally ø 38-42 with a 3.5-4 "
        "wall; stem off ø 14 OD / ø 8 ID tube; foot off the same stem stock.",
        "Colour: transparent teal or magenta rod for the wash, matched frit, clear "
        "marble stock, and silver or gold for the fume per colourway.",
    ]),
    ("Chamber", [
        "Close and shape one end into the rounded lobe. Blow the chamber out to 68 "
        "long, working the section oval to 42 × 37 - paddle and marver it, do not "
        "blow it round in a mould.",
        "Fume the inside before any colour goes on. The fume is what shifts in use; "
        "colour laid under it kills that.",
        "Lay the transparent wash over the fume, even from lobe to rim.",
    ]),
    ("Frit and marbles", [
        "Roll the bowl end in frit over the outer 54 mm of the chamber, densest at the "
        "rim, thinning out toward the lobe. Melt it in flush - it is worked into the "
        "wall, not a coating sitting on it.",
        "Set 4 clear marbles ø 6.5-7.5 into the fritted band by hand. They are not "
        "evenly spaced and should not look it. Encase them fully; no open seam.",
    ]),
    ("Bowl and carb", [
        "Open the bowl at the rim end to ø 25, 19 deep, funnelled down to the ø 3 hole "
        "in the bottom of the bowl. Hold the ø 3 - the original measured ø 5 and it "
        "was called down on purpose.",
        "Raise the ø 11 carb boss on the side wall 14 mm below the rim, then open the "
        "ø 3.5 carb through it.",
    ]),
    ("Stem and foot", [
        "Cut the stem and fuse it into the underside of the chamber at mid-length. "
        "The ø 8 bore must break through into the chamber clean - no web, no pinch.",
        "Flare the foot to ø 24.5 × 7 thick and break the edges about 1.6. It has to "
        "stand square: 140 overall, no rock.",
    ]),
    ("Linework", [
        "Spin the linework on last: about 13 turns at 2.4 pitch down the head, plus a "
        "few rings round the foot. Clear over the fritted body.",
    ]),
]

SOP_JAR = [
    ("Body", [
        "Cut ø 44 × 3 wall tube to 92 plus working allowance. Close the bottom flat "
        "with a 3 floor - flat enough to stand without rocking.",
        "Fume the inside, then lay the wash over it, same order as the hammer.",
    ]),
    ("Frit, marbles, mark", [
        "Frit band 66-90.5 up from the base, melted in flush.",
        "Set 7 clear marbles ø 8 evenly round the opening, centres 84.5 up. Evenly "
        "spaced here - the jar reads as a ring, the hammer does not.",
        "Press the JBD mark into a molten stamp pad on the wall, lower middle, centre "
        "28 up. Die face about 28 × 11.",
    ]),
    ("Mouth", [
        "Open and true the mouth to ø 38 ID. Hold the OD at 44 right up to the rim - "
        "straight cylinder, no shoulder, no flare.",
        "Spin 9 turns at 2.4 pitch over the frit band.",
    ]),
    ("Cork", [
        "Natural cork, 27 long, ø 36.6 at the bottom and ø 41 at the top. One gentle "
        "taper, no mushroom cap.",
        "Fit to the piece it ships with: 15 into the mouth, about 12 standing proud, "
        "seating on the taper rather than bottoming out.",
    ]),
]

SOP_FINISH = [
    ("Anneal", [
        "Anneal every piece. Typical for boro 3.3 is a soak around 565 °C / 1050 °F "
        "held 30-60 minutes by mass, then down to about 480 °C at 50 °C/hour before "
        "free cooling - use the shop's own kiln schedule where it differs.",
        "Check for strain under a polariscope after cooling. The stem-to-chamber joint "
        "and the marble seats are where it shows first.",
    ]),
    ("Decoration after anneal", [
        "The enamel label goes on the stem after annealing: 20-74 mm up from the foot "
        "face, JBD × Boutiq dropped out in white, kiln-cured to the glass.",
        "Strike the print to read with the head to the left. The box lays the piece "
        "that way; struck the other way round it reads upside down in the tray.",
    ]),
    ("Hold points", [
        "H1  chamber - 68 long, 42 × 37 section, before the bowl is opened.",
        "H2  bowl - ø 25 at the rim, 19 deep, ø 3 hole on a go / no-go pin.",
        "H3  stem - blow through end to end; the ø 8 bore must be clear.",
        "H4  after anneal - 140 overall, ø 14 stem, ø 24.5 × 7 foot, stands without "
        "rocking, no strain.",
        "H5  jar - ø 38 mouth on a go / no-go, cork seats 15 with about 12 proud, "
        "stands flat.",
        "H6  finish - no chips at the rim or the carb, marbles fully encased, label "
        "square to the stem and centred on the tube.",
    ]),
    ("Packing", [
        "Into the Boutiq tray: hammer head to the left in the pipe recess so the label "
        "reads left to right, jar with the cork end to the back-left of its trough.",
        "Reject rather than pass anything failing H2, H3 or H4. The four dimensions "
        "that must hold are bowl ø 25, bowl hole ø 3, stem bore ø 8, jar mouth ø 38.",
    ]),
]


def _page_sop(n, title, sub, groups):
    pg, d = sheet.blank()
    _head(d, title, sub, n)
    fh, ft, fn = sheet.font(True, 19), sheet.font(False, 21), sheet.font(True, 21)
    cols = [(96, 700), (856, 700)]
    ci, y, step = 0, 300, 1
    for name, items in groups:
        x, w = cols[ci]
        if y > PAGE[1] - 300 and ci == 0:
            ci, y = 1, 300
            x, w = cols[ci]
        d.text((x, y), name.upper(), font=fh, fill=RED)
        y += 34
        for it in items:
            txt, lines = sheet.wrap(d, it, ft, w - 46)
            if y + 30 * lines > PAGE[1] - 120 and ci == 0:
                ci, y = 1, 300
                x, w = cols[ci]
                txt, lines = sheet.wrap(d, it, ft, w - 46)
            d.text((x, y), "%d" % step, font=fn, fill=RED)
            d.multiline_text((x + 40, y), txt, font=ft, fill=INK, spacing=9)
            y += 30 * lines + 16
            step += 1
        y += 16
    return pg


def _page_sop_hammer(n):
    return _page_sop(n, "Process — hammer bubbler",
                     "Bench sequence. The shop's working order governs where it differs "
                     "— the numbered checks do not move.", SOP_HAMMER)


def _page_sop_jar(n):
    return _page_sop(n, "Process — nug jar and cork",
                     "Same order of work: shape, fume, colour, frit, marbles, mark.",
                     SOP_JAR)


def _page_sop_finish(n):
    return _page_sop(n, "Anneal, decoration and QC",
                     "What happens after the torch, and what gets measured before a "
                     "piece is passed.", SOP_FINISH)


PLAN = ([_page_hammer]
        + [(lambda n, c=c: _page_closeup(n, *c)) for c in CLOSEUPS[:3]]
        + [_page_survey, _page_jar]
        + [(lambda n, c=c: _page_closeup(n, *c)) for c in CLOSEUPS[3:]]
        + [_page_decor, _page_sop_hammer, _page_sop_jar, _page_sop_finish])
TOTAL = len(PLAN)


def build():
    os.makedirs("shots", exist_ok=True)
    pages = [fn(i + 1) for i, fn in enumerate(PLAN)]
    sheet.save(pages, OUT, "JBD Clearboy — manufacturing spec")
    if os.path.isdir("docs"):
        shutil.copyfile(OUT, SITE)
        print("wrote", SITE)
    return OUT


PACK_NOTE = """JBD x Boutiq - Clearboy programme
Manufacturing hand-off pack

  spec/JBD_Clearboy_spec.pdf   the spec sheet - read this first. Dimensions,
                               dimensioned closeups, the survey, decoration, and the
                               bench process with its QC hold points.
  spec/dimensions.png          the dimensional survey of the original piece
  spec/detail/*.png            dimensioned closeups, full resolution
  cad/*.step                   solid B-rep - the reference geometry
  cad/*.stl                    meshes - 3D print, mould master, wax pattern
  box/*.png                    the collaboration box with the pieces seated
  JBD_x_Boutiq.pdf             the leave-behind, box plate by plate

STEP is the reference. The meshes are for print and mould work only.
Wall thickness on the hammer is inferred, not measured - confirm with calipers
before any tooling. Figures are in millimetres.
"""


def build_pack():
    """One zip with everything the shop needs, laid out so it explains itself."""
    items = [(OUT, "spec/JBD_Clearboy_spec.pdf"),
             ("JBD_Clearboy_dimensions.png", "spec/dimensions.png"),
             (os.path.join("shots", "JBD_x_Boutiq.pdf"), "JBD_x_Boutiq.pdf")]
    items += [(p, "spec/detail/" + os.path.basename(p))
              for p in sorted(glob.glob(os.path.join("shots", "spec", "*.png")))]
    items += [(p, "cad/" + os.path.basename(p))
              for p in sorted(glob.glob(os.path.join("out", "*.ste[pl]")))]
    items += [(p, "box/" + os.path.basename(p))
              for p in sorted(glob.glob(os.path.join("shots", "box", "*.png")))]

    missing = [src for src, _ in items if not os.path.exists(src)]
    with zipfile.ZipFile(PACK, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("README.txt", PACK_NOTE)
        for src, name in items:
            if os.path.exists(src):
                z.write(src, name)
    if missing:
        print("pack: MISSING, not included -", ", ".join(missing))
    print("wrote", PACK, "- %.1f MB, %d files"
          % (os.path.getsize(PACK) / 1e6, len(items) - len(missing) + 1))
    if os.path.isdir("docs"):
        shutil.copyfile(PACK, PACK_SITE)
        print("wrote", PACK_SITE)
    return PACK


if __name__ == "__main__":
    build()
    build_pack()
