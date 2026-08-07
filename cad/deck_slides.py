"""The slides. Aimed at sign-off: the case, the sleeves, the glass, the numbers and the
schedule - and none of the commercial terms or open internal questions."""
import os, shutil

from PIL import Image, ImageDraw

import sheet
from deck import (PAGE, PINK, TEAL, BLACK, WHITE, PAPER, MUTE, OUT, SITE,
                  check, eyebrow, font, foot, head, lockup, para, shot, tag,
                  stickers)

HAMMER = [("Overall length", "140 MM"),
          ("Chamber", "68 X 42 X 37"),
          ("Stem", "14 OD / 8 BORE"),
          ("Bowl", "25 OPENING / 3 HOLE"),
          ("Carb", "3.5 ON AN 11 BOSS"),
          ("Foot", "24.5 X 7"),
          ("Mass", "APPROX 81 G")]

JAR = [("Glass height", "92 MM"),
       ("Body", "44 OD / 3 WALL"),
       ("Mouth", "38 OPENING"),
       ("Cork", "27 LONG / SEATS 15"),
       ("Marbles", "SEVEN AT THE RIM"),
       ("Mass", "APPROX 90 G")]


def s01_cover():
    pg = Image.new("RGB", PAGE, BLACK)
    pg.paste(stickers(PAGE, (30, 30, 34), BLACK, 0.9), (0, 0))
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Three_Boxes_R2_C2", (980, 980))
    pg.paste(art, (PAGE[0] - art.width - 40, (PAGE[1] - art.height) // 2))
    eyebrow(d, (110, 228), "LIMITED EDITION", TEAL)
    lockup(pg, d, (110, 268), 52, WHITE)
    head(d, (110, 414), "The\ncollectors\nbox set", 92, WHITE, 760)
    para(d, (110, 784), "Hand-blown glass by Jerome Baker Designs, in a stitched "
         "leatherette case.", "b", 30, (176, 176, 180), 680)
    foot(d, 1, (90, 90, 96))
    return pg


def s02_box():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Box_Closed_C3_R1", (960, 960))
    pg.paste(art, (PAGE[0] - art.width - 40, (PAGE[1] - art.height) // 2))
    eyebrow(d, (110, 150), "THE CASE", PINK)
    head(d, (110, 204), "Black leatherette,\nstitched and\nnumbered", 60, BLACK, 740)
    y = para(d, (110, 486), "A hard case with a leather grain, punched seams and a "
             "hinged lid. The mark is struck into the lid itself.", "b", 27, BLACK, 690)
    y += 44
    for k, v in (("Finish", "Blind emboss, colour emboss or foil."),
                 ("Lid", "Hinged, with the lockup on the face."),
                 ("Edition", "Numbered on the side panel."),
                 ("After", "Keeps its job once the glass comes out.")):
        d.text((110, y), check(k, "h"), font=font("h", 25), fill=PINK)
        y = max(para(d, (290, y - 2), v, "b", 24, BLACK, 520), y + 44) + 20
    foot(d, 2)
    return pg


def s03_series():
    pg = Image.new("RGB", PAGE, PAPER)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 116), "THE SERIES", PINK)
    head(d, (110, 168), "One case, two sleeves", 62, BLACK, 1500)
    for i, (nm, label, col) in enumerate(
            (("Boutique_Colab_Box_Closed_C2_R1_Indica", "TEAL", TEAL),
             ("Boutique_Colab_Box_Closed_C2_R1_Sativa", "MAGENTA", PINK))):
        art = shot(nm, (680, 500))
        x = 150 + i * 830
        pg.paste(art, (x, 276))
        tag(d, (x + 10, 286 + art.height), label, 30, fill=col)
    d.text((1180, 860), "10K", font=font("px", 92), fill=PINK)
    eyebrow(d, (1180, 976), "OF EACH SLEEVE", BLACK, 22, 5)
    para(d, (150, 862), "The case does not change. The printed sleeve does, and that is "
         "what makes it a series - two colourways, ten thousand of each, every one "
         "numbered on the side panel.", "b", 27, BLACK, 960)
    foot(d, 3)
    return pg


def s04_inside():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Box_Open_R5_C3_Indica", (1020, 1020))
    pg.paste(art, (PAGE[0] - art.width - 50, (PAGE[1] - art.height) // 2))
    eyebrow(d, (110, 140), "INSIDE", PINK)
    head(d, (110, 194), "Cut to fit,\npiece by piece", 62, BLACK, 700)
    items = [("Hammer bubbler", "Hand-blown boro, fumed and frit-rolled, set with "
                                "clear marbles."),
             ("Nug jar", "Thick-walled glass with a tapered cork and a pressed "
                         "JBD mark."),
             ("Flower jar", "Labelled and sealed, in the colourway of the set."),
             ("Matches", "Flat-pack wood matches.")]
    y = 430
    for name, body in items:
        d.text((110, y), check(name, "h"), font=font("h", 28), fill=PINK)
        y = para(d, (110, y + 44), body, "b", 24, BLACK, 640) + 26
        d.line([(110, y - 16), (750, y - 16)], fill=(226, 226, 228), width=1)
    para(d, (110, 900), "Every piece sits in its own cut recess, so the set travels and "
         "displays the way it was packed.", "b", 24, BLACK, 640)
    foot(d, 4)
    return pg


def s05_glass():
    """All four builds together - both pieces, both colourways. On paper rather than
    black, because the renders carry their own light sweep and would otherwise read as
    cards floating on a dark slide."""
    pg = Image.new("RGB", PAGE, PAPER)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 116), "THE GLASS", PINK)
    head(d, (110, 168), "Two pieces, two colourways", 62, BLACK, 1600)
    shots = [("shots/hammer_teal_silver.png", "HAMMER", TEAL),
             ("shots/jar_teal_silver.png", "NUG JAR", TEAL),
             ("shots/hammer_magenta_gold.png", "HAMMER", PINK),
             ("shots/jar_magenta_gold.png", "NUG JAR", PINK)]
    for i, (p, label, col) in enumerate(shots):
        x = 130 + i * 430
        if os.path.exists(p):
            art = sheet.fit(Image.open(p).convert("RGB"), (400, 560))
            pg.paste(art, (x + (400 - art.width) // 2, 300))
        tag(d, (x + 20, 890), label, 26, fill=col)
    para(d, (130, 990), "Every piece is fumed, frit-rolled and set with clear marbles by "
         "hand, and finished with the enamel band or the pressed mark.",
         "b", 25, BLACK, 1660)
    foot(d, 5)
    return pg


def s06_specs():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 116), "SPECIFICATION", PINK)
    head(d, (110, 168), "Built off a measured model", 62, BLACK, 1600)
    for i, (title, rows, col) in enumerate((("Clearboy hammer bubbler", HAMMER, PINK),
                                            ("Nug jar and cork", JAR, TEAL))):
        x = 110 + i * 500
        d.text((x, 300), check(title, "h"), font=font("h", 28), fill=col)
        y = 352
        for k, v in rows:
            d.text((x, y), check(k, "b"), font=font("b", 23), fill=MUTE)
            d.text((x, y + 30), check(v, "px"), font=font("px", 25), fill=BLACK)
            y += 76
            d.line([(x, y - 22), (x + 400, y - 22)], fill=(228, 228, 230), width=1)
    x = 1090
    for p, box, at in (("shots/spec/head.png", (540, 380), (x, 290)),
                       ("shots/spec/jar_body.png", (240, 400), (x + 570, 290))):
        if os.path.exists(p):
            art = sheet.fit(Image.open(p).convert("RGB"), box)
            pg.paste(art, at)
            d.rectangle([at[0] - 1, at[1] - 1, at[0] + art.width, at[1] + art.height],
                        outline=(224, 224, 226), width=1)
    para(d, (110, 966), "Dimensions in millimetres, taken off the solid model the shop "
         "builds from. Hand-blown, so each piece sits within a tolerance rather than "
         "on the number.", "b", 25, BLACK, 1400)
    foot(d, 6)
    return pg


def s07_ways():
    pg = Image.new("RGB", PAGE, TEAL)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 130), "COLOURWAYS", BLACK)
    head(d, (110, 184), "Fumed, so no two match", 62, BLACK, 1500)
    art = shot("Boutique_Colab_Box_Open_R5_C1_Sativa", (700, 700))
    pg.paste(art, (PAGE[0] - art.width - 110, 310))
    y = para(d, (110, 360), "Fume is metal laid onto hot glass. It sits under the "
             "colour and shifts as the piece is used, so the surface keeps moving "
             "between silver, violet and a warm edge.", "b", 28, BLACK, 880)
    y += 40
    for k, v in (("Teal and silver", "Bluish teal body, silver fume, teal frit."),
                 ("Magenta and gold", "Magenta body, gold fume, magenta frit.")):
        d.text((110, y), check(k, "h"), font=font("h", 30), fill=BLACK)
        para(d, (110, y + 48), v, "b", 25, BLACK, 860)
        y += 124
    para(d, (110, 930), "Renders shown. Every piece is worked by hand, so the fume and "
         "the marbles fall differently on each one.", "b", 23, (12, 92, 90), 880)
    foot(d, 7, (10, 100, 98))
    return pg


def s08_timeline():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 120), "TIMELINE", PINK)
    head(d, (110, 174), "From sign-off to shelf", 66, BLACK, 1500)
    steps = [("SIGN OFF", "This week", "Design approved as shown, artwork goes final."),
             ("EIGHT WEEKS", "Production", "Glass blown, cases made, sets packed and "
                                           "shipped."),
             ("27 OCT", "Samples", "Full-size sets in hand, air-shipped, ahead of the "
                                   "buyers tournament."),
             ("1 NOV", "On shelf", "In store for the holiday run.")]
    x, y, w = 110, 400, 430
    for i, (when, sub, body) in enumerate(steps):
        col = PINK if i < 2 else TEAL
        d.rectangle([x, y, x + w - 40, y + 8], fill=col)
        d.text((x, y + 48), check(when, "px"), font=font("px", 30), fill=col)
        d.text((x, y + 116), check(sub, "h"), font=font("h", 32), fill=BLACK)
        para(d, (x, y + 170), body, "b", 24, BLACK, w - 60)
        x += w
    para(d, (110, 760), "Eight weeks of production is the long pole, and it does not "
         "start until the design is locked. Sign-off is what puts the set on shelf for "
         "the holidays.", "b", 27, BLACK, 1600)
    foot(d, 8)
    return pg


def s09_close():
    pg = Image.new("RGB", PAGE, BLACK)
    pg.paste(stickers(PAGE, (32, 32, 36), BLACK, 0.9), (0, 0))
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Three_Boxes_R2_C1", (740, 740))
    pg.paste(art, (PAGE[0] - art.width - 90, (PAGE[1] - art.height) // 2))
    lockup(pg, d, (110, 396), 60, WHITE)
    head(d, (110, 580), "Ready for\nyour sign-off", 72, WHITE, 800)
    para(d, (110, 776), "Approve the design as shown and artwork goes final "
         "this week.", "b", 30, (186, 186, 190), 700)
    eyebrow(d, (110, 890), "JEROME BAKER DESIGNS  BOUTIQ", (110, 110, 116), 20, 5)
    foot(d, 9, (90, 90, 96))
    return pg


SLIDES = [s01_cover, s02_box, s03_series, s04_inside, s05_glass,
          s06_specs, s07_ways, s08_timeline, s09_close]


def build():
    os.makedirs("shots", exist_ok=True)
    pages = [fn() for fn in SLIDES]
    sheet.save(pages, OUT, "JBD x Boutiq - collector box set")
    if os.path.isdir("docs"):
        try:
            shutil.copyfile(OUT, SITE)
            print("wrote", SITE)
        except PermissionError:
            print("LOCKED, not updated:", SITE)
    return OUT
