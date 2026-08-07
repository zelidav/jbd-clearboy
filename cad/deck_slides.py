"""The slides. Customer-facing: the glass and the case, and nothing about what it costs,
how many are being made, or what is still being settled internally."""
import os, shutil

from PIL import Image, ImageDraw

import sheet
from deck import (PAGE, PINK, TEAL, BLACK, WHITE, PAPER, MUTE, OUT, SITE,
                  check, eyebrow, font, foot, head, lockup, para, shot, tag,
                  stickers)


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
        para(d, (290, y - 2), v, "b", 24, BLACK, 520)
        y += 64
    foot(d, 2)
    return pg


def s03_series():
    pg = Image.new("RGB", PAGE, PAPER)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 120), "THE SERIES", PINK)
    head(d, (110, 174), "One case, two sleeves", 66, BLACK, 1500)
    for i, (nm, label, col) in enumerate(
            (("Boutique_Colab_Box_Closed_C2_R1_Indica", "TEAL", TEAL),
             ("Boutique_Colab_Box_Closed_C2_R1_Sativa", "MAGENTA", PINK))):
        art = shot(nm, (700, 540))
        x = 150 + i * 830
        pg.paste(art, (x, 300))
        tag(d, (x + 10, 312 + art.height), label, 30, fill=col)
    para(d, (150, 920), "The case does not change. The printed sleeve does, and that is "
         "what makes the set collectable - two colourways to a series, each one "
         "numbered, with the glass inside matched to the sleeve it ships in.",
         "b", 27, BLACK, 1620)
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


def s05_hammer():
    pg = Image.new("RGB", PAGE, BLACK)
    pg.paste(stickers(PAGE, (28, 28, 32), BLACK, 0.9), (0, 0))
    d = ImageDraw.Draw(pg)
    for i, p in enumerate(("shots/hammer_teal_silver.png",
                           "shots/hammer_magenta_gold.png")):
        if os.path.exists(p):
            art = sheet.fit(Image.open(p).convert("RGB"), (450, 700))
            pg.paste(art, (960 + i * 480, 200))
    eyebrow(d, (110, 190), "THE PIECE", TEAL)
    head(d, (110, 244), "Clearboy\nhammer bubbler", 58, WHITE, 760)
    y = para(d, (110, 440), "Worked from one hand-blown original. Silver or gold fume "
             "under a transparent wash, frit rolled into the bowl end, and clear "
             "marbles set into the band by hand.", "b", 27, (196, 196, 200), 740)
    y += 40
    for k, v in (("Length", "140 mm, standing on its own foot."),
                 ("Chamber", "68 mm, shaped oval rather than blown round."),
                 ("Glass", "Borosilicate, thick-walled, no seams.")):
        d.text((110, y), check(k, "h"), font=font("h", 25), fill=TEAL)
        para(d, (300, y - 2), v, "b", 24, (210, 210, 214), 540)
        y += 62
    foot(d, 5, (90, 90, 96))
    return pg


def s06_jar():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    for i, p in enumerate(("shots/jar_teal_silver.png", "shots/jar_magenta_gold.png")):
        if os.path.exists(p):
            art = sheet.fit(Image.open(p).convert("RGB"), (420, 690))
            pg.paste(art, (990 + i * 450, 210))
    eyebrow(d, (110, 190), "THE PIECE", PINK)
    head(d, (110, 244), "Nug jar\nand cork", 58, BLACK, 760)
    y = para(d, (110, 430), "A straight cylinder in the same glass, closed with a "
             "tapered natural cork. A band of frit under the rim, seven clear marbles "
             "around the opening, and the JBD mark pressed into the wall.",
             "b", 27, BLACK, 780)
    y += 40
    for k, v in (("Height", "92 mm of glass, plus the cork."),
                 ("Mouth", "Wide enough to reach into, corked to keep it fresh."),
                 ("Mark", "Pressed into the glass while it is still molten.")):
        d.text((110, y), check(k, "h"), font=font("h", 25), fill=PINK)
        para(d, (300, y - 2), v, "b", 24, BLACK, 560)
        y += 62
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
    eyebrow(d, (110, 860), "JEROME BAKER DESIGNS  BOUTIQ", (110, 110, 116), 20, 5)
    foot(d, 9, (90, 90, 96))
    return pg


SLIDES = [s01_cover, s02_box, s03_series, s04_inside,
          s05_hammer, s06_jar, s07_ways, s08_timeline, s09_close]


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
