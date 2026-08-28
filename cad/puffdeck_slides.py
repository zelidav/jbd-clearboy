"""The pages of the PUFF x JEROME BAKER concept pack.

Eight slides, one piece, one finish. The pack is the joint tube and the box it ships
in - the rest of the programme has its own site and does not belong in a partner's deck.

The first five are the idea and the object; the last three are how the drop runs.

It is a pitch, not a working document: no internal caveats, no showing of the working,
and nothing on a page that a buyer would not care about.
"""
import os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet
from puffdeck import (PAGE, BLUE, PINK, GOLD, BLACK, WHITE, PAPER, MUTE, DEEP,
                      font, para, head, tracked, tracked_w, eyebrow, pill, lockup,
                      foot, shot, card, rule, stat, table, OUT, SITE)

def _page(bg=PAPER):
    pg = Image.new("RGB", PAGE, bg)
    return pg, ImageDraw.Draw(pg)


def _blob(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def _drips(d, x0, x1, y, depth, fill, n=11, seed=3):
    """The one gesture borrowed from Puff's own system: a run of drips off an edge.
    Drawn, not lifted - their drip artwork is theirs."""
    import random
    rng = random.Random(seed)
    span = (x1 - x0) / float(n)
    for i in range(n):
        cx = x0 + span * (i + 0.5) + rng.uniform(-span * 0.14, span * 0.14)
        w = span * rng.uniform(0.30, 0.52)
        h = max(depth * rng.uniform(0.30, 1.0), w * 1.2)
        d.rectangle([cx - w / 2, y - 4, cx + w / 2, y + h - w / 2], fill=fill)
        d.ellipse([cx - w / 2, y + h - w, cx + w / 2, y + h], fill=fill)


# --------------------------------------------------------------------------- 01
def s01_cover():
    pg, d = _page(BLACK)
    d.rectangle([0, 0, PAGE[0], 250], fill=BLUE)
    _drips(d, 60, PAGE[0] - 60, 250, 96, BLUE, n=13, seed=9)
    card(pg, d, (1210, 300), (600, 720), "tube_loaded_puff_blue", radius=30)

    lockup(d, (110, 74), 74, WHITE, BLACK)
    head(d, (110, 430), "The pre-roll\nthat comes\nin glass", 96, WHITE, 900)
    para(d, (110, 800), "A hand-blown Jerome Baker tube for the Puff one-gram - the "
         "same format, the same wordmark up the side - one holiday drop, in a vessel "
         "that outlives the joint.", "r", 27, (176, 184, 194), 780)
    x = 110
    x += pill(d, (x, 930), "CONCEPT PACK", 19, PINK, WHITE) + 14
    x += pill(d, (x, 930), "CALIFORNIA + NEW YORK", 19, GOLD, BLACK) + 14
    pill(d, (x, 930), "HOLIDAY 2026", 19, (34, 38, 44), (188, 196, 206))
    foot(d, 1, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 02
def s02_premise():
    pg, d = _page(PAPER)
    eyebrow(d, (110, 120), "THE PREMISE")
    head(d, (110, 172), "Twenty million sold.\nNothing to keep.", 62, BLACK, 1200)
    y = para(d, (110, 372), "Twenty million pre-rolls says the audience is there and "
             "that it comes back. What it has never once been handed is a reason to "
             "keep the tube - every one of them went out in printed plastic and every "
             "one of them went in the bin.", "r", 26, (58, 64, 72), 900)
    y = para(d, (110, y + 26), "This is not a proposal to change what twenty million "
             "pre-rolls ship in. It is one drop, once, at the end of the year: the "
             "same tube in hand-blown glass, paired with a strain worth the occasion, "
             "in a box worth opening.", "r", 26, (58, 64, 72), 900)
    para(d, (110, y + 34), "A pre-roll people queue for, and a piece they still have "
         "next Christmas.", "b", 27, BLACK, 900)

    # the three numbers
    d.rounded_rectangle([1080, 350, 1810, 866], radius=26, fill=WHITE)
    d.rounded_rectangle([1080, 350, 1810, 866], radius=26, outline=(226, 231, 237),
                        width=2)
    # the labels are kept to one line each: three stacked stats that each wrap to three
    # lines is a list, not a set of numbers
    stat(d, (1136, 400), "20M+", "pre-rolls sold", size=56)
    stat(d, (1136, 566), "2", "states: California and New York", size=56, sub=MUTE)
    stat(d, (1136, 732), "1", "drop a year, at gifting season", size=56)
    para(d, (1080, 894), "Volumes on puffprerolls.com, August 2026.", "m", 18, MUTE, 700)
    foot(d, 2)
    return pg


# --------------------------------------------------------------------------- 03
def s03_piece():
    pg, d = _page(WHITE)
    d.rectangle([0, 0, 660, PAGE[1]], fill=(244, 250, 254))
    card(pg, d, (70, 70), (520, 940), "tube_loaded_puff_blue",
         fill=(244, 250, 254), radius=26)

    eyebrow(d, (760, 120), "THE PIECE  ·  JBD-JT-124")
    head(d, (760, 172), "The joint tube", 66, BLACK, 1000)
    y = para(d, (760, 286), "A straight, flat-bottomed tube in boro 3.3, blown to take "
             "a one-gram king-size cone with room to shake it back out. It stands on a "
             "counter, it stops on a table, and it is finished the way a piece of glass "
             "is finished rather than the way a component is.", "r", 24, (58, 64, 72), 1010)

    rows = [("Overall height", "124 mm"), ("Body", "24 mm OD, 4.5 mm wall"),
            ("Bore", "15 mm - takes a 1 g cone"),
            ("Base", "7 mm, flat and closed"),
            ("Glass", "approx. 79 g, boro 3.3"),
            ("Colourway", "Puff Blue, silver fumed"),
            ("Closure", "tapered natural cork, 24 mm"),
            ("Print", "50 mm label band, up the axis")]
    y = table(d, (760, y + 40), rows, 1010)

    notes = [("PUFF BLUE", BLUE, "Your blue in the body, silver fumed so it flashes as "
              "the piece turns rather than sitting flat on it."),
             ("GOLD DRIPS", GOLD, "A band of gold laid on at the rim and let go. It "
              "runs, thins, and beads where it stopped. No two are the same."),
             ("PINK AND GOLD WIG WAG", PINK, "Stringers walked round the base while "
              "they are run up and down, stacked into chevrons. Pulled by hand.")]
    x, y = 760, min(y, 858)
    for name, col, txt in notes:
        d.rectangle([x, y, x + 300, y + 6], fill=col)
        d.text((x, y + 26), name, font=font("b", 20), fill=BLACK)
        para(d, (x, y + 62), txt, "r", 18, (92, 98, 106), 300, lead=1.44)
        x += 356
    foot(d, 3)
    return pg


# --------------------------------------------------------------------------- 04
def s04_why():
    pg, d = _page(BLACK)
    d.rectangle([0, 0, PAGE[0], 8], fill=BLUE)
    eyebrow(d, (110, 130), "WHY THIS GLASS", GOLD)
    head(d, (110, 182), "Not a glass tube.\nA Jerome Baker.", 66, WHITE, 1000)
    y = para(d, (110, 386), "Jerome Baker Designs has been blowing glass since the "
             "nineties. The name is the point: it is the reason a customer keeps the "
             "tube on a shelf instead of in a drawer, and the reason the second one is "
             "bought without a joint in it.", "r", 25, (172, 180, 190), 820)
    para(d, (110, y + 26), "The drips run where they run. Two tubes off the same bench "
         "are the same object and not the same piece - and at twenty thousand units "
         "that is not a limitation, it is the only thing plastic cannot copy.",
         "r", 25, (172, 180, 190), 820)

    cards = [("NO TOOLING TO AMORTISE", "Injection moulding wants fifty thousand units "
              "before the tool pays for itself. Glass has no tool - a ten thousand unit "
              "run is a normal run, and the second colourway costs nothing to add."),
             ("WORKED, NOT MOULDED", "Boro 3.3. The body is formed to spec; the wig "
              "wag, the drips, the marbles and the mark are laid on by hand, which is "
              "what a mould cannot do at any volume."),
             ("NON PLANT-TOUCHING", "The glass ships from the non-cannabis entity, so "
              "nothing about the collab touches either licence.")]
    x = 1030
    for i, (t, b) in enumerate(cards):
        yy = 300 + i * 216
        d.rounded_rectangle([x, yy, x + 780, yy + 184], radius=20, fill=(22, 26, 32))
        d.rectangle([x, yy + 24, x + 6, yy + 160], fill=(BLUE, PINK, GOLD)[i])
        d.text((x + 40, yy + 34), t, font=font("b", 24), fill=WHITE)
        para(d, (x + 40, yy + 78), b, "r", 19, (150, 158, 168), 700, lead=1.46)
    foot(d, 4, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 05
def s05_box():
    pg, d = _page(BLACK)
    d.rectangle([0, 0, PAGE[0], 8], fill=GOLD)
    card(pg, d, (930, 150), (880, 780), "box_puff_blue", radius=26)
    eyebrow(d, (110, 130), "THE BOX", GOLD)
    head(d, (110, 182), "Rigid board,\nhinged lid,\nmagnetic clasp.",
         60, WHITE, 800)
    y = para(d, (110, 430), "A keepsake handed over in a paper bag is a keepsake nobody "
             "photographs. The lid is hinged full height and closes onto two disc magnets "
             "in the front lip. It opens with a click and closes the same way.",
             "r", 23, (172, 180, 190), 740)
    rows = [("Outside", "53 x 48 x 169 mm"), ("Board", "3.5 mm rigid, wrapped"),
            ("Clasp", "2 x 9 mm disc magnets"), ("Insert", "die-cut foam, one well"),
            ("Relief", "front-cut - lifts straight out")]
    yy = y + 34
    for a, b in rows:
        d.text((110, yy), a, font=font("m", 21), fill=(126, 134, 144))
        d.text((400, yy), b, font=font("b", 21), fill=WHITE)
        yy += 56
        rule(d, yy - 18, 110, 830, (34, 38, 44), 1)
    para(d, (110, yy + 20), "The lining carries the colour. Glass is transmissive, so "
         "behind a black insert the piece reads black - the insert is what it is seen "
         "against, and it is the one part of the box that is not black.",
         "r", 20, (150, 158, 168), 740)
    foot(d, 5, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 07
def s06_drop():
    """The volume page.

    This started life as a limited-drop page - numbered pieces, one release, gone. At
    ten thousand units a state that framing is wrong twice over: nobody hand-numbers
    twenty thousand pieces, and a brand doing that volume is not running a drop, it is
    changing what its pack is made of. The mechanic is a test with a read on it.
    """
    pg, d = _page(BLACK)
    card(pg, d, (1450, 120), (370, 840), "tube_puff_blue", radius=26)
    eyebrow(d, (110, 120), "THE DROP", GOLD)
    head(d, (110, 172), "A holiday drop,\nnot a packaging\nchange.", 58, WHITE, 900)

    rows = [("When", "holiday - on shelf for the gifting weeks"),
            ("Markets", "California and New York"),
            ("Volume", "10,000 units per state - 20,000 in total"),
            ("The piece", "one finish - Puff Blue, silver fumed"),
            ("Paired with", "a strain chosen for the drop, named on the box"),
            ("Allocation", "by door count, into doors that already carry Puff"),
            ("After it", "the same piece, a new strain - a drop a quarter "
                         "if the first one lands")]
    y = 452
    for a, b in rows:
        d.text((110, y), a, font=font("m", 21), fill=(126, 134, 144))
        para(d, (400, y), b, "b", 21, WHITE, 940, lead=1.25)
        y += 56
        rule(d, y - 16, 110, 1380, (34, 38, 44), 1)
    para(d, (110, y + 16), "A limited piece with a strain on it is a reason to come "
         "in during gifting week.", "b", 22, WHITE, 1260)
    bands = [("Holiday drop", "10,000 / state"), ("Strain drops", "10,000 / state"),
             ("A year of it", "3 - 4 drops")]
    x = 110
    for a, b in bands:
        d.text((x, y + 76), a, font=font("m", 19), fill=(126, 134, 144))
        d.text((x, y + 104), b, font=font("h", 34), fill=BLUE)
        x += 420
    foot(d, 6, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 08
def s07_capacity():
    """Capacity, stated rather than argued.

    An earlier draft of this page showed its working and read like a supplier hoping it
    could cope. Twenty thousand a quarter is a normal run here; the page says that and
    moves on.
    """
    pg, d = _page(PAPER)
    eyebrow(d, (110, 118), "CAPACITY")
    head(d, (110, 170), "Capacity is not the question", 54, BLACK, 1300)
    para(d, (110, 268), "The body and the decoration are two different jobs, and both "
         "are already running. Twenty thousand pieces for a holiday window is a normal "
         "run - the line is in place, the hand-off pack is drawn, and the date is the "
         "only thing left to agree.", "r", 23, (58, 64, 72), 1050)

    split = [("THE BODY", BLUE, "Drawn boro tubing, cut to 124, base closed flat at 7 "
              "and the rim rolled. Standard tube-shop work - runs in the tens of "
              "thousands are routine, and the hand-off pack is already drawn for a "
              "factory, in English and in Chinese."),
             ("THE DECORATION", PINK, "Wig wag, drips, two marbles and the pressed "
              "mark: four passes by hand on a finished body. A staffed decorating cell "
              "does this work already - it is the part nobody can copy, and it is not "
              "the part that limits the run.")]
    x = 110
    for t, col, b in split:
        d.rounded_rectangle([x, 380, x + 830, 570], radius=20, fill=WHITE)
        d.rounded_rectangle([x, 380, x + 830, 570], radius=20,
                            outline=(228, 232, 238), width=2)
        d.rectangle([x + 30, 414, x + 36, 538], fill=col)
        d.text((x + 58, 410), t, font=font("h", 24), fill=BLACK)
        para(d, (x + 58, 452), b, "r", 18, (84, 90, 98), 740, lead=1.42)
        x += 870

    nums = [("20,000", "units in the drop - both states"),
            ("1 quarter", "from sign-off to delivered"),
            ("3 weeks", "from sign-off to samples in hand"),
            ("4 a year", "the same piece, a new strain each time")]
    x = 110
    for big, lab in nums:
        d.text((x, 664), big, font=font("h", 52), fill=BLACK)
        para(d, (x, 738), lab, "m", 19, MUTE, 380)
        x += 440
    para(d, (110, 856), "One piece and one finish keeps it simple all the way down: "
         "one spec on the bench, one label, one SKU on the shelf in both states - and "
         "the strain is the only thing that changes next time.",
         "r", 21, (58, 64, 72), 1700)
    foot(d, 7)
    return pg


# --------------------------------------------------------------------------- 10
def s08_close():
    pg, d = _page(BLUE)
    # the bar goes down first and the blue runs into it - drips drawn under a bar are
    # drips nobody sees
    d.rectangle([0, PAGE[1] - 150, PAGE[0], PAGE[1]], fill=BLACK)
    _drips(d, 40, PAGE[0] - 40, PAGE[1] - 152, 108, BLUE, n=14, seed=21)
    card(pg, d, (1330, 130), (470, 790), "tube_puff_blue", radius=28)

    lockup(d, (110, 120), 62, WHITE, BLACK)
    head(d, (110, 340), "Say yes to the\nshape of it,\nand we spec it.", 68, WHITE, 880)
    steps = [("1", "Pick the strain", "the one the drop is named for"),
             ("2", "Confirm the finish", "Puff Blue, silver fumed"),
             ("3", "Sign the lockup", "Puff's own artwork replaces the stand-in"),
             ("4", "Samples", "in hand inside three weeks")]
    y = 630
    for n, t, b in steps:
        d.ellipse([110, y, 156, y + 46], fill=BLACK)
        w = d.textlength(n, font=font("b", 22))
        d.text((133 - w / 2, y + 10), n, font=font("b", 22), fill=WHITE)
        d.text((182, y + 2), t, font=font("b", 23), fill=WHITE)
        d.text((182, y + 34), b, font=font("m", 18), fill=(214, 238, 252))
        y += 74
    d.text((110, PAGE[1] - 108), "JEROME BAKER DESIGNS", font=font("b", 22), fill=WHITE)
    d.text((110, PAGE[1] - 74), "david@canismajorpartners.com", font=font("m", 19),
           fill=(150, 200, 230))
    rt = "Puff marks shown as stand-ins, for your artwork to replace."
    d.text((PAGE[0] - 110 - d.textlength(rt, font=font("m", 17)), PAGE[1] - 74), rt,
           font=font("m", 17), fill=(120, 130, 140))
    return pg


SLIDES = [s01_cover, s02_premise, s03_piece, s04_why, s05_box,
          s06_drop, s07_capacity, s08_close]


def build():
    os.makedirs("shots", exist_ok=True)
    pages = [fn() for fn in SLIDES]
    sheet.save(pages, OUT, "PUFF x Jerome Baker - collab concept")
    if os.path.isdir("docs"):
        try:
            import shutil
            shutil.copyfile(OUT, SITE)
            print("wrote", SITE)
        except PermissionError:
            print("LOCKED, not updated:", SITE)
    return OUT


if __name__ == "__main__":
    build()
