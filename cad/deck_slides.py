"""The slides. Copy follows the 4 August call; anything left open on that call stays on
the open-items page rather than being quietly presented as settled."""
import os, shutil

from PIL import Image, ImageDraw

import sheet
from deck import (PAGE, PINK, TEAL, BLACK, WHITE, PAPER, MUTE, OUT, SITE,
                  badge, check, eyebrow, font, foot, head, lockup, para, shot,
                  stickers)


def s01_cover():
    pg = Image.new("RGB", PAGE, BLACK)
    pg.paste(stickers(PAGE, (30, 30, 34), BLACK, 0.9), (0, 0))
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Three_Boxes_R2_C2", (980, 980))
    pg.paste(art, (PAGE[0] - art.width - 40, (PAGE[1] - art.height) // 2))
    eyebrow(d, (110, 214), "COLLECTORS BOX SET", TEAL)
    lockup(d, (110, 262), 52, WHITE)
    head(d, (110, 400), "Limited\nedition\ncollab", 92, WHITE, 760)
    para(d, (110, 770), "Hand-blown glass by Jerome Baker Designs, boxed for Boutiq. "
         "Massachusetts launch.", "b", 30, (176, 176, 180), 690)
    eyebrow(d, (110, 900), "DESIGN REVIEW  7 AUG 2026", (120, 120, 126), 20, 5)
    foot(d, 1, (90, 90, 96))
    return pg


def s02_where():
    pg = Image.new("RGB", PAGE, PINK)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 130), "WHERE WE LANDED  4 AUG CALL", WHITE)
    head(d, (110, 184), "Agreed on the call", 78, WHITE, 1400)
    cards = [("28", "ALL IN", "25 base plus the 3 royalty. Everyone aligned. Final quote "
                              "follows the locked layout."),
             ("10000", "UNITS", "All into Massachusetts. 500 committed off the launch, "
                                "three salespeople on it."),
             ("2", "SKUS", "Indica and Sativa. Hybrid is out - they are all hybridised "
                           "anyway, and it only split the run."),
             ("NOV 1", "LANDED", "Ten weeks out. Samples in hand for the buyers golf "
                                 "tournament on 27 October.")]
    x, y, w, gap = 110, 350, 400, 24
    for big, cap, body in cards:
        pg.paste(Image.new("RGB", (w, 430), WHITE), (x, y))
        dd = ImageDraw.Draw(pg)
        dd.text((x + 36, y + 50), check(big, "px"),
                font=font("px", 62 if len(big) <= 5 else 44), fill=PINK)
        eyebrow(dd, (x + 36, y + 170), cap, TEAL, 22, 5)
        para(dd, (x + 36, y + 232), body, "b", 25, BLACK, w - 72)
        x += w + gap
    foot(d, 2, (250, 200, 226))
    return pg


def s03_set():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Box_Open_R5_C3_Indica", (1000, 1000))
    pg.paste(art, (PAGE[0] - art.width - 60, (PAGE[1] - art.height) // 2))
    eyebrow(d, (110, 130), "THE SET", PINK)
    head(d, (110, 184), "Four pieces,\none box", 70, BLACK, 700)
    items = [("Flower jar", "7 g, JBD x Boutiq label, Indica or Sativa. Supplied by "
                            "Jerome Baker."),
             ("Clearboy hammer", "Hand-blown boro 3.3, 140 mm, fumed and frit-rolled "
                                 "with clear marbles."),
             ("Nug jar", "92 mm glass, 38 mm mouth, cork lid, pressed JBD mark."),
             ("Matches", "Flat-pack wood matches. Not rolling papers - the big "
                         "matchbook is the insert.")]
    y = 430
    for name, body in items:
        d.text((110, y), check(name, "h"), font=font("h", 30), fill=PINK)
        y = para(d, (110, y + 46), body, "b", 24, BLACK, 660) + 28
        d.line([(110, y - 16), (770, y - 16)], fill=(226, 226, 228), width=1)
    para(d, (110, 950), "Renders show a slim insert in the top tray - confirm it reads "
         "as the matchbook and not a pre-roll.", "b", 21, MUTE, 660)
    foot(d, 3)
    return pg


def s04_skus():
    pg = Image.new("RGB", PAGE, PAPER)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 120), "TWO SKUS", PINK)
    head(d, (110, 174), "Indica and Sativa", 66, BLACK, 1400)
    for i, (nm, tag, col) in enumerate(
            (("Boutique_Colab_Box_Open_R5_C2_Indica", "INDICA", PINK),
             ("Boutique_Colab_Box_Open_R5_C2_Sativa", "SATIVA", TEAL))):
        art = shot(nm, (660, 560))
        x = 170 + i * 830
        pg.paste(art, (x, 310))
        badge(d, (x + 10, 320 + art.height), tag, 32, fill=col, ink=WHITE)
    para(d, (170, 930), "The bulk market swings between Indica-heavy and Sativa-heavy "
         "month to month, so the set covers both and skips hybrid. Accents carry the "
         "difference. The inner box stays one tooling.", "b", 27, BLACK, 1580)
    foot(d, 4)
    return pg


def s05_lids():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 120), "LID TREATMENTS", PINK)
    head(d, (110, 174), "Three ways to close it", 66, BLACK, 1400)
    opts = [("Boutique_Colab_Box_Closed_C1_R1_Sativa", "C1",
             "Full pattern lid, black body."),
            ("Boutique_Colab_Box_Closed_C2_R1_Sativa", "C2",
             "Pattern top, black sides and sleeve."),
            ("Boutique_Colab_Box_Closed_C3_R1", "C3",
             "Black lid, lockup only. Quietest of the three.")]
    for i, (nm, tag, body) in enumerate(opts):
        art = shot(nm, (520, 440))
        x = 110 + i * 570
        pg.paste(art, (x, 300))
        badge(d, (x, 780), tag, 30, fill=BLACK, ink=WHITE)
        para(d, (x, 866), body, "b", 24, BLACK, 500)
    d.rectangle([110, 976, 1810, 980], fill=PINK)
    para(d, (110, 1004), "Emboss blind, in colour, or in foil. Foil was the preference "
         "in the room.", "b", 25, BLACK, 1700)
    foot(d, 5)
    return pg


def s06_build():
    pg = Image.new("RGB", PAGE, BLACK)
    pg.paste(stickers(PAGE, (28, 28, 32), BLACK, 0.9), (0, 0))
    d = ImageDraw.Draw(pg)
    art = shot("Boutique_Colab_Three_Boxes_R2_C1", (940, 940))
    pg.paste(art, (PAGE[0] - art.width - 50, (PAGE[1] - art.height) // 2))
    eyebrow(d, (110, 150), "CONSTRUCTION", TEAL)
    head(d, (110, 204), "Static box,\nvariable skin", 66, WHITE, 760)
    y = para(d, (110, 410), "Hard leather-look box with a leather texture and punched "
             "seams. Inner box plus an outer sleeve.", "b", 27, (196, 196, 200), 720)
    y += 44
    for k, v in (("Static", "Inner box, foam tray tooling, glass."),
                 ("Variable", "Sleeve, beauty card, the printed layer over the foam, "
                              "and the inner lining.")):
        d.text((110, y), check(k, "h"), font=font("h", 28), fill=TEAL)
        y = para(d, (110, y + 44), v, "b", 25, (210, 210, 214), 720) + 36
    para(d, (110, 910), "That split is what lets one box carry two SKUs, and lets the "
         "artwork move without retooling.", "b", 23, (150, 150, 156), 720)
    foot(d, 6, (90, 90, 96))
    return pg


def s07_glass():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 120), "THE GLASS", PINK)
    head(d, (110, 174), "Reverse-engineered\nfrom one original", 60, BLACK, 900)
    for i, (p, nm, spec) in enumerate((
            ("shots/hammer_teal_silver.png", "Clearboy hammer",
             "140 mm overall. Head 68 long, 42 x 37 oval section. Bowl 25 opening to a "
             "3 hole. Stem 14 OD on an 8 bore."),
            ("shots/jar_teal_silver.png", "Nug jar",
             "92 mm glass on a 44 straight cylinder. 38 mm mouth, tapered cork. Frit "
             "band and seven clear marbles at the rim."))):
        x = 1010 + i * 450
        if os.path.exists(p):
            art = sheet.fit(Image.open(p).convert("RGB"), (400, 450))
            pg.paste(art, (x, 180))
        d.text((x, 660), check(nm, "h"), font=font("h", 27), fill=PINK)
        para(d, (x, 706), spec, "b", 22, BLACK, 390)
    para(d, (110, 450), "Both pieces come off a solid model measured from the "
         "hand-blown original, so the shop gets STEP rather than a picture. Fumed and "
         "frit-rolled, with the linework spun on before the marbles are set.",
         "b", 27, BLACK, 800)
    pg.paste(Image.new("RGB", (800, 200), PAPER), (110, 680))
    dd = ImageDraw.Draw(pg)
    eyebrow(dd, (146, 722), "COLOUR IS NOT LOCKED", PINK, 22, 5)
    para(dd, (146, 774), "The teal shown is indicative. Jason is confirming which hues "
         "the factory can actually pull, and fuming shifts the colour again.",
         "b", 23, BLACK, 730)
    foot(d, 7)
    return pg


def s08_open():
    pg = Image.new("RGB", PAGE, TEAL)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 130), "OPEN ITEMS", BLACK)
    head(d, (110, 184), "What has to close next", 66, BLACK, 1500)
    items = [("Pattern", "The art on these renders is the Jerome Baker New York Drop 1, "
                         "used to mock up size and shape. It is not locked. Boutiq "
                         "pixel and Game Boy artwork replaces it."),
             ("Glass colour", "Jason to come back with the hues the factory can actually "
                              "make. The tray and the jar then follow that colour."),
             ("Boutiq mark", "The lid carries the Boston mark. High-resolution logo pack "
                             "needed before artwork goes final."),
             ("Insert", "Confirm the slim tray item is the flat-pack matchbook.")]
    y = 350
    for k, v in items:
        pg.paste(Image.new("RGB", (1700, 4), BLACK), (110, y - 22))
        d.text((110, y), check(k, "h"), font=font("h", 32), fill=BLACK)
        para(d, (530, y - 2), v, "b", 26, BLACK, 1280)
        y += 160
    foot(d, 8, (10, 100, 98))
    return pg


def s09_timeline():
    pg = Image.new("RGB", PAGE, WHITE)
    d = ImageDraw.Draw(pg)
    eyebrow(d, (110, 120), "TIMELINE", PINK)
    head(d, (110, 174), "Ten weeks, working back", 66, BLACK, 1500)
    steps = [("1 WK", "Final design", "Layout locked, artwork swapped, final quote."),
             ("8 WKS", "Production", "Made and landed in Massachusetts."),
             ("1 WK", "Slack", "For the surprises that always come."),
             ("27 OCT", "Samples", "Full-size mock-ups at the buyers golf tournament, "
                                   "air-shipped. Pre-sale opens."),
             ("1 NOV", "Launch", "On shelf ahead of Black Friday.")]
    x, y, w = 110, 430, 342
    for i, (when, what, body) in enumerate(steps):
        col = PINK if i < 3 else TEAL
        d.rectangle([x, y, x + w - 32, y + 8], fill=col)
        d.text((x, y + 46), check(when, "px"), font=font("px", 32), fill=col)
        d.text((x, y + 116), check(what, "h"), font=font("h", 29), fill=BLACK)
        para(d, (x, y + 164), body, "b", 23, BLACK, w - 46)
        x += w
    para(d, (110, 800), "Eight weeks of production is the long pole, and the design "
         "lock is what starts that clock. Pattern and colour are the critical path, "
         "not the tooling.", "b", 27, BLACK, 1600)
    foot(d, 9)
    return pg


def s10_close():
    pg = Image.new("RGB", PAGE, BLACK)
    pg.paste(stickers(PAGE, (32, 32, 36), BLACK, 0.9), (0, 0))
    d = ImageDraw.Draw(pg)
    lockup(d, (110, 372), 64, WHITE)
    head(d, (110, 530), "Lets level up", 90, WHITE, 1400)
    para(d, (110, 720), "Send the Boutiq artwork and the Boston logo pack and the "
         "layout can be locked this week.", "b", 30, (186, 186, 190), 900)
    eyebrow(d, (110, 890), "JEROME BAKER DESIGNS  BOUTIQ  2026", (110, 110, 116), 20, 5)
    foot(d, 10, (90, 90, 96))
    return pg


SLIDES = [s01_cover, s02_where, s03_set, s04_skus, s05_lids,
          s06_build, s07_glass, s08_open, s09_timeline, s10_close]


def build():
    os.makedirs("shots", exist_ok=True)
    pages = [fn() for fn in SLIDES]
    sheet.save(pages, OUT, "JBD x Boutiq - collector box review")
    if os.path.isdir("docs"):
        try:
            shutil.copyfile(OUT, SITE)
            print("wrote", SITE)
        except PermissionError:
            print("LOCKED, not updated:", SITE)
    return OUT
