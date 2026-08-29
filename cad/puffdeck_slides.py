"""The pages of the PUFF x JEROME BAKER concept pack.

Nine slides, one piece, one finish. The pack is the joint tube and the box it ships
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
    head(d, (110, 400), "The only pre-roll\nthey'll still have\nnext Christmas", 72, WHITE, 940)
    para(d, (110, 800), "A hand-blown Jerome Baker tube for the Puff one-gram - the "
         "wordmark up the side - one holiday drop, in a piece they keep using long "
         "after the joint is gone.", "r", 27, (176, 184, 194), 780)
    x = 110
    x += pill(d, (x, 930), "CONCEPT PACK", 19, PINK, WHITE) + 14
    x += pill(d, (x, 930), "CALIFORNIA + NEW YORK", 19, GOLD, BLACK) + 14
    pill(d, (x, 930), "HOLIDAY 2026", 19, (34, 38, 44), (188, 196, 206))
    foot(d, 1, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 02
def s02_premise():
    """The premise page.

    An earlier draft of this argued against plastic - twenty million tubes, all of them
    binned. Wrong fight. Nobody buys a premium object because the cheap one is bad; they
    buy it because they want it. This page is about what the piece is worth having, and
    about the thing that happens after the joint is gone, which is where the brand
    actually gets paid.
    """
    pg, d = _page(PAPER)
    eyebrow(d, (110, 120), "THE IDEA")
    head(d, (110, 172), "Twenty million thrown away.\nTwenty thousand kept forever.",
         56, BLACK, 1300)
    y = para(d, "", "", "r", 26, (0, 0, 0), 900) if False else para(
        d, (110, 372), "Twenty million pre-rolls have gone out, and twenty million "
        "tubes have gone in the bin with them. That is the volume, and it is exactly "
        "why the opposite of it is worth doing once a year.", "r", 26, (58, 64, 72), 900)
    y = para(d, (110, y + 26), "Twenty thousand pieces that nobody throws away. From "
             "the day it is opened it is where they keep a joint - any joint, one of "
             "yours, one from somewhere else, one they rolled themselves - and every "
             "time they take one out, they are holding your name.",
             "r", 26, (58, 64, 72), 900)
    para(d, (110, y + 34), "You paid for that placement once, at Christmas, and it "
         "keeps working all year.", "b", 27, BLACK, 900)

    d.rounded_rectangle([1080, 350, 1810, 866], radius=26, fill=WHITE)
    d.rounded_rectangle([1080, 350, 1810, 866], radius=26, outline=(226, 231, 237),
                        width=2)
    stat(d, (1136, 400), "20M+", "sold, and binned with their tubes", size=56)
    stat(d, (1136, 566), "20,000", "in the drop, and kept", size=56)
    stat(d, (1136, 732), "3-4", "drops a year the same piece carries", size=56)
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
    y = para(d, (760, 286), "Hand-blown, heavy in the hand, and finished the way a "
             "piece of glass is finished. It takes a one-gram cone with room to shake "
             "it back out, it stands on a counter, and it will not roll off a table.",
             "r", 24, (58, 64, 72), 1010)

    rows = [("Overall height", "124 mm"), ("Body", "24 mm OD, 4.5 mm wall"),
            ("Bore", "15 mm - takes a 1 g cone"),
            ("Base", "7 mm, flat and closed"),
            ("Glass", "approx. 79 g, boro 3.3"),
            ("Finish", "Puff Blue, silver fumed"),
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
    y = para(d, (110, 430), "The lid is hinged full height and closes onto two disc "
             "magnets. It opens with a click, and it is the kind of box people keep "
             "things in afterwards rather than flatten and bin.",
             "r", 23, (172, 180, 190), 740)
    rows = [("Outside", "44 x 48 x 157 mm"), ("Board", "3.5 mm rigid, wrapped"),
            ("Clasp", "2 x 9 mm disc magnets"),
            ("Inside", "tissue wrap, sticker seal"),
            ("No insert", "the box is cut to the piece")]
    yy = y + 34
    for a, b in rows:
        d.text((110, yy), a, font=font("m", 21), fill=(126, 134, 144))
        d.text((400, yy), b, font=font("b", 21), fill=WHITE)
        yy += 56
        rule(d, yy - 18, 110, 830, (34, 38, 44), 1)
    para(d, (110, yy + 20), "No insert and no foam. The box is cut to the piece, the "
         "piece is wrapped in branded tissue and closed with a seal, and a box that "
         "fits does not need anything holding the thing still.",
         "r", 20, (150, 158, 168), 740)
    foot(d, 5, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 06
def s06_variable():
    """What changes per drop, and what does not.

    The piece is not tied to one strain, and it should not be: the glass is one print
    run and everything that has to vary lives on paper. That is what makes a second
    drop cheap, and it is what keeps the regulator off the glass.
    """
    pg, d = _page(WHITE)
    eyebrow(d, (110, 110), "WHAT CHANGES")
    head(d, (110, 162), "One piece. Any strain.", 58, BLACK, 1200)
    para(d, (110, 268), "The glass is not tied to a strain, and nothing a regulator "
         "can move is printed on it. Paper does all of that.",
         "r", 23, (58, 64, 72), 1080)

    art = shot("puff_variable", (1150, 660))
    pg.paste(art, (110, 356))

    items = [("THE BEAUTY CARD", BLUE, "Sits over the piece in the box. Strain, "
              "artwork, whatever the drop is called. New card, new drop."),
             ("THE BAND", PINK, "Round the tube, off in one motion. The cheapest thing "
              "in the pack to change and the first thing seen."),
             ("THE STICKER", GOLD, "Batch, potency, dates, warnings. It goes on last, "
              "so nothing a regulator asks for ever touches the glass.")]
    y = 360
    for t, col, b in items:
        d.rounded_rectangle([1310, y, 1810, y + 190], radius=18, fill=(247, 249, 251))
        d.rectangle([1342, y + 30, 1348, y + 150], fill=col)
        d.text((1374, y + 26), t, font=font("b", 21), fill=BLACK)
        para(d, (1374, y + 62), b, "r", 18, (84, 90, 98), 400, lead=1.44)
        y += 212
    foot(d, 6)
    return pg


# --------------------------------------------------------------------------- 07
def s07_drop():
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
            ("Paired with", "whatever strain the drop is - it is on the card"),
            ("Allocation", "by door count, into doors that already carry Puff"),
            ("After it", "same piece, new card - a drop a quarter if the "
                         "first one lands")]
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
    foot(d, 7, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 08
def s08_capacity():
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
    foot(d, 8)
    return pg


# --------------------------------------------------------------------------- 09
def s09_close():
    """The close.

    This used to be a four-step checklist - pick a strain, confirm the finish, sign the
    lockup, then quote. Every one of those is a decision, and a page of decisions is a
    page of reasons to come back to it later. There is one decision here, and everything
    that would have been a decision happens on a sample instead.
    """
    pg, d = _page(BLUE)
    d.rectangle([0, PAGE[1] - 150, PAGE[0], PAGE[1]], fill=BLACK)
    _drips(d, 40, PAGE[0] - 40, PAGE[1] - 152, 108, BLUE, n=14, seed=21)
    card(pg, d, (1330, 130), (470, 790), "tube_puff_blue", radius=28)

    lockup(d, (110, 120), 62, WHITE, BLACK)
    head(d, (110, 340), "Say go, and you\nhold one in\nthree weeks.", 68, WHITE, 900)
    para(d, (110, 604), "Everything else happens on the sample rather than on paper. "
         "Strain, finish, artwork - you will want changes and they are easier to make "
         "with the piece in your hand than in a meeting about it.",
         "r", 25, (224, 244, 254), 880)
    para(d, (110, 730), "There is nothing to specify to start. Say go.", "b", 28,
         WHITE, 880)

    d.text((110, PAGE[1] - 108), "JEROME BAKER DESIGNS", font=font("b", 22), fill=WHITE)
    d.text((110, PAGE[1] - 74), "david@canismajorpartners.com", font=font("m", 19),
           fill=(150, 200, 230))
    rt = "Puff marks shown as stand-ins, for your artwork to replace."
    d.text((PAGE[0] - 110 - d.textlength(rt, font=font("m", 17)), PAGE[1] - 74), rt,
           font=font("m", 17), fill=(120, 130, 140))
    return pg


SLIDES = [s01_cover, s02_premise, s03_piece, s04_why, s05_box,
          s06_variable, s07_drop, s08_capacity, s09_close]


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
