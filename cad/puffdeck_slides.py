"""The pages of the PUFF x JEROME BAKER concept pack.

Ten slides. The first six are the idea and the object, page seven is the constraint that
shapes the programme, and the last three are how it would actually run.

Nothing commercial in here is a quote. The pricing page shows how a number is built and
what moves it, and says so on the page - a deck that invents a supplier price is worse
than a deck with none.
"""
import os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheet
from puffdeck import (PAGE, BLUE, PINK, GOLD, BLACK, WHITE, PAPER, MUTE, DEEP,
                      font, para, head, tracked, tracked_w, eyebrow, pill, lockup,
                      foot, shot, card, rule, stat, table, OUT, SITE)

ILLUSTRATIVE = "Figures on this page are illustrative arithmetic, not a quote."


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
    card(pg, d, (1210, 300), (600, 720), "tube_loaded_teal_silver", radius=30)

    lockup(d, (110, 74), 74, WHITE, BLACK)
    head(d, (110, 430), "The pre-roll\nthat comes\nin glass", 96, WHITE, 900)
    para(d, (110, 800), "A hand-blown Jerome Baker tube for the Puff one-gram - the "
         "same format, the same wordmark up the side, in a vessel that outlives the "
         "joint.", "r", 27, (176, 184, 194), 780)
    x = 110
    x += pill(d, (x, 930), "CONCEPT PACK", 19, PINK, WHITE) + 14
    x += pill(d, (x, 930), "CALIFORNIA + NEW YORK", 19, GOLD, BLACK) + 14
    pill(d, (x, 930), "AUGUST 2026", 19, (34, 38, 44), (188, 196, 206))
    foot(d, 1, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 02
def s02_premise():
    pg, d = _page(PAPER)
    eyebrow(d, (110, 120), "THE PREMISE")
    head(d, (110, 172), "Twenty million pre-rolls.\nTwenty million plastic tubes.",
         62, BLACK, 1200)
    y = para(d, (110, 372), "Puff has sold more than twenty million pre-rolls. Every "
             "one of them went out in a printed plastic tube - the cheapest component "
             "in the package, and the only component the customer still has an hour "
             "later.", "r", 26, (58, 64, 72), 900)
    y = para(d, (110, y + 26), "That tube already does the brand's hardest work. It "
             "carries the wordmark down its own axis, it sits on the counter, it comes "
             "out at the table. It is a brand asset that gets thrown away because of "
             "what it is made of - and nothing else about it needs to change.",
             "r", 26, (58, 64, 72), 900)
    para(d, (110, y + 34), "Make that one part glass and the pre-roll stops being "
         "packaging and starts being a keepsake with a joint in it.", "b", 27, BLACK, 900)

    # the three numbers
    d.rounded_rectangle([1080, 350, 1810, 800], radius=26, fill=WHITE)
    d.rounded_rectangle([1080, 350, 1810, 800], radius=26, outline=(226, 231, 237),
                        width=2)
    stat(d, (1136, 396), "20M+", "pre-rolls sold, on Puff's own count", size=56)
    stat(d, (1136, 546), "2", "states they are legally sold in today - California and "
         "New York", size=56)
    stat(d, (1136, 700), "0", "of those tubes kept", size=56)
    para(d, (1080, 830), "Sources: puffprerolls.com, August 2026.", "m", 18, MUTE, 700)
    foot(d, 2)
    return pg


# --------------------------------------------------------------------------- 03
def s03_piece():
    pg, d = _page(WHITE)
    d.rectangle([0, 0, 660, PAGE[1]], fill=(244, 250, 254))
    card(pg, d, (70, 70), (520, 940), "tube_loaded_magenta_gold",
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
            ("Closure", "tapered natural cork, 24 mm"),
            ("Decoration", "wig wag, drips, JB imprint"),
            ("Print", "50 mm label band, up the axis")]
    y = table(d, (760, y + 40), rows, 1010)

    notes = [("TWO MARBLES", PINK, "Set proud on one side, a few degrees apart. Laid "
              "down it beds on both and will not roll off a bench."),
             ("WIG WAG", BLUE, "Stringers walked round the base while they are run up "
              "and down, stacked into chevrons. Two colours, pulled by hand."),
             ("DRIPS", GOLD, "A band of colour laid on at the rim and let go. No two "
              "runs are the same, which is the proof a person made it.")]
    x, y = 760, min(y, 858)
    for name, col, txt in notes:
        d.rectangle([x, y, x + 300, y + 6], fill=col)
        d.text((x, y + 26), name, font=font("b", 20), fill=BLACK)
        para(d, (x, y + 62), txt, "r", 18, (92, 98, 106), 300, lead=1.44)
        x += 356
    foot(d, 3, note="Renders are proposals; the hand-blown original stays the reference.")
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
    para(d, (110, y + 26), "Every piece is worked by hand on a torch in New York. The "
         "drips run where they run. Two tubes off the same bench are the same object "
         "and not the same piece - and that is what a limited drop is actually selling.",
         "r", 25, (172, 180, 190), 820)

    cards = [("HAND BLOWN", "Boro 3.3, torch-worked and annealed. No moulds, no "
              "injection tooling, no minimum of fifty thousand."),
             ("MADE IN NEW YORK", "One of the two states Puff already sells in. The "
              "glass does not cross a border to get to the New York shelf."),
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
def s05_set():
    pg, d = _page(PAPER)
    eyebrow(d, (110, 120), "THE SET")
    head(d, (110, 172), "The tube is the drop.\nThe rest is the reorder.", 60, BLACK, 1200)
    para(d, (110, 348), "One piece launches a collab. A set keeps it selling after the "
         "flower is gone - and Jerome Baker already has the other pieces drawn, "
         "modelled and specified.", "r", 25, (58, 64, 72), 1000)

    card(pg, d, (1250, 300), (560, 580), "lighter_loaded_teal_silver",
         fill=WHITE, radius=20)
    d.rounded_rectangle([1250, 896, 1810, 972], radius=18, fill=WHITE)
    d.text((1284, 918), "Lighter sleeve  ·  JBD-LS-58", font=font("b", 22),
           fill=BLACK)

    items = [("JOINT TUBE", "JBD-JT-124", "124 mm  ·  one gram  ·  cork", BLUE,
              "The hero. Ships with the pre-roll or sells empty."),
             ("LIGHTER SLEEVE", "JBD-LS-58", "58 mm  ·  obround socket", PINK,
              "A glass jacket for the lighter everyone already owns. It is struck in "
              "the sleeve - 26 mm stands proud."),
             ("GLASS TIP", "JBD-GT-19", "19 mm  ·  screen inside", GOLD,
              "Reusable filter tip with a slot to start the roll against. Already "
              "specified in the programme."),
             ("JOINT HOLDER", "JBD-JH-90", "90 mm  ·  grips any joint", DEEP,
              "A cigarette holder made for a joint. The bell takes a pinner or a fat "
              "one and grips both.")]
    y = 470
    for name, code, dims, col, txt in items:
        d.rounded_rectangle([110, y, 1180, y + 118], radius=18, fill=WHITE)
        d.rectangle([110, y + 24, 118, y + 94], fill=col)
        d.text((156, y + 24), name, font=font("b", 24), fill=BLACK)
        d.text((156, y + 62), dims, font=font("m", 19), fill=MUTE)
        # the code is right-aligned in its own column - the copy stops short of it
        para(d, (596, y + 26), txt, "r", 19, (84, 90, 98), 404, lead=1.42)
        cw = d.textlength(code, font=font("m", 18))
        d.text((1180 - 30 - cw, y + 24), code, font=font("m", 18), fill=(178, 184, 192))
        y += 134
    foot(d, 5)
    return pg



# ------------------------------------------------------------------------ 05b
def s06_box():
    pg, d = _page(BLACK)
    d.rectangle([0, 0, PAGE[0], 8], fill=GOLD)
    card(pg, d, (930, 150), (880, 780), "box_teal_silver", radius=26)
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
    foot(d, 6, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 06
def s06_ways():
    pg, d = _page(WHITE)
    eyebrow(d, (110, 110), "COLOURWAYS")
    head(d, (110, 162), "Four ways, one form", 60, BLACK, 1200)
    para(d, (110, 272), "Every way is fumed - real silver or gold laid on the hot "
         "glass, which is why the colour shifts as the piece turns rather than sitting "
         "flat on it. Puff picks one per state, or one per strain.", "r", 23,
         (58, 64, 72), 1100)

    ways = [("tube_teal_silver", "Mint, silver fume", "rod 13  ·  silver nitrate",
             (201, 232, 225)),
            ("tube_magenta_gold", "Pink, gold fume", "rod 3  ·  gold chloride",
             (215, 191, 199)),
            ("tube_clear_silver", "Clear, heavy silver", "teal accents  ·  wrapped",
             (237, 242, 246)),
            ("tube_clear_gold", "Clear, heavy gold", "magenta accents  ·  wrapped",
             (251, 243, 228))]
    x = 128
    for name, title, sub, swatch in ways:
        d.rounded_rectangle([x, 380, x + 388, 980], radius=22, fill=(248, 249, 251))
        card(pg, d, (x + 20, 396), (348, 440), name, fill=(248, 249, 251), radius=18)
        d.ellipse([x + 34, 862, x + 74, 902], fill=swatch,
                  outline=(210, 216, 222), width=2)
        d.text((x + 90, 858), title, font=font("b", 21), fill=BLACK)
        d.text((x + 90, 888), sub, font=font("m", 17), fill=MUTE)
        x += 416
    foot(d, 7)
    return pg


# --------------------------------------------------------------------------- 07
def s07_compliance():
    pg, d = _page(PAPER)
    d.rectangle([0, 0, PAGE[0], 10], fill=GOLD)
    eyebrow(d, (110, 120), "THE CONSTRAINT", (168, 118, 12))
    head(d, (110, 172), "A cork-stopped tube\nis not child-resistant.", 60, BLACK, 1200)
    y = para(d, (110, 372), "California and New York both require cannabis pre-rolls to "
             "reach the customer in child-resistant packaging. A glass tube with a cork "
             "in it is not that, and no amount of design makes it that. This decides "
             "the shape of the programme, so it is on page seven rather than in a "
             "footnote.", "r", 25, (58, 64, 72), 980)

    opts = [("ROUTE A", "Glass inside a CR outer", BLUE,
             "The loaded tube ships inside a child-resistant carton or pouch. The "
             "customer opens the pack, keeps the glass. Highest cost per unit, "
             "cleanest story, and the pre-roll is still the thing being bought.",
             "Adds an outer to the BOM. Route to test first."),
            ("ROUTE B", "Glass sold empty, alongside", PINK,
             "The pre-roll ships in Puff's existing compliant pack; the tube is sold "
             "as an empty vessel at the same counter, in the same artwork. No "
             "packaging approval needed and it can ship to states Puff is not in yet.",
             "Fastest to market. Loses the unboxing."),
            ("ROUTE C", "CR closure on the glass", GOLD,
             "A certified push-and-turn closure replacing the cork. Real, and used on "
             "glass tubes today - but it is a tooled part, it has to be tested to the "
             "standard, and it changes the top of the piece.",
             "Longest lead time. The endgame, not the launch.")]
    x = 110
    for tag, title, col, body, note in opts:
        d.rounded_rectangle([x, 640, x + 546, 950], radius=20, fill=WHITE)
        d.rounded_rectangle([x, 640, x + 546, 950], radius=20,
                            outline=(228, 232, 238), width=2)
        pill(d, (x + 32, 672), tag, 17, col, WHITE if col != GOLD else BLACK)
        d.text((x + 32, 736), title, font=font("b", 23), fill=BLACK)
        yy = para(d, (x + 32, 780), body, "r", 18, (84, 90, 98), 482, lead=1.44)
        para(d, (x + 32, yy + 12), note, "b", 18, col if col != GOLD else (168, 118, 12),
             482, lead=1.4)
        x += 578
    para(d, (110, 986), "Recommendation: launch on Route B in both states while Route A "
         "is packed and tested, and keep Route C on the roadmap. Not legal advice - "
         "Puff's own compliance team signs the final pack.", "m", 19, MUTE, 1700)
    foot(d, 8)
    return pg


# --------------------------------------------------------------------------- 08
def s08_drop():
    pg, d = _page(BLACK)
    card(pg, d, (1420, 150), (400, 800), "tube_clear_gold", radius=28)
    eyebrow(d, (110, 120), "THE DROP", GOLD)
    head(d, (110, 172), "One release,\ntwo states,\nnumbered.", 66, WHITE, 900)

    rows = [("Markets", "California and New York"),
            ("Format", "Numbered limited run, per state"),
            ("Allocation", "Split by door count, not evenly"),
            ("Sell-in", "Doors that already carry Puff, first"),
            ("Window", "One drop, then it is gone"),
            ("Re-order", "Empty tubes and the sleeve, ongoing"),
            ("Budtender", "JBD runs a training and rewards programme; "
                          "Puff's SKU rides on it")]
    y = 452
    for a, b in rows:
        d.text((110, y), a, font=font("m", 22), fill=(126, 134, 144))
        d.text((430, y), b, font=font("b", 22), fill=WHITE)
        y += 62
        rule(d, y - 20, 110, 1330, (34, 38, 44), 1)
    para(d, (110, y + 26), "Numbering is the whole mechanic: a piece with a number on it "
         "is a thing to come back for, and a drop that sells out is a drop the second "
         "one is pre-ordered.", "r", 22, (150, 158, 168), 1180)
    foot(d, 9, (96, 102, 112))
    return pg


# --------------------------------------------------------------------------- 09
def s09_money():
    pg, d = _page(WHITE)
    eyebrow(d, (110, 118), "HOW THE NUMBER IS BUILT")
    head(d, (110, 170), "What moves the price", 58, BLACK, 1200)
    para(d, (110, 274), "There is no quote in this pack, because a quote before the "
         "final spec is a number that gets renegotiated. What is fixed is what the "
         "number is made of, and which levers move it.", "r", 23, (58, 64, 72), 1050)

    drivers = [("GLASS WEIGHT", "79 g on the tube as drawn - it is deliberately "
                "heavy, to survive a floor. Wall and height are the two sliders that "
                "move it, and they move cost linearly."),
               ("DECORATION PASSES", "Wig wag, drips, marbles and the pressed mark are "
                "four separate trips to the torch. Dropping one is the cheapest saving "
                "on the page."),
               ("ANNEAL AND YIELD", "Hand-blown glass has a scrap rate. It falls with "
                "run length, which is why tier three is not tier one times ten."),
               ("PRINT", "One-colour on the band is cheapest; the four-colour lockup "
                "as drawn is a second pass."),
               ("CLOSURE", "Cork is pennies. A certified CR closure is not, and it is "
                "tooled."),
               ("OUTER", "Route A only. Route B has no outer at all.")]
    y = 400
    for i, (t, b) in enumerate(drivers):
        x = 110 + (i % 2) * 560
        yy = y + (i // 2) * 186
        d.rounded_rectangle([x, yy, x + 512, yy + 158], radius=18, fill=(247, 249, 251))
        d.text((x + 30, yy + 24), t, font=font("b", 21), fill=BLACK)
        para(d, (x + 30, yy + 60), b, "r", 18, (84, 90, 98), 452, lead=1.44)

    d.rounded_rectangle([1250, 400, 1810, 940], radius=22, fill=BLACK)
    d.text((1288, 436), "TIERS TO PRICE AGAINST", font=font("b", 21), fill=GOLD)
    tiers = [("Pilot", "500 units", "one colourway, one state"),
             ("Drop", "2,500 units", "two colourways, both states"),
             ("Programme", "10,000 units+", "rolling, four ways")]
    yy = 486
    for name, qty, note in tiers:
        d.text((1288, yy), name, font=font("b", 26), fill=WHITE)
        d.text((1288, yy + 38), qty, font=font("h", 30), fill=BLUE)
        d.text((1288, yy + 82), note, font=font("m", 18), fill=(140, 148, 158))
        yy += 118
    para(d, (1288, 852), "Quote against a chosen tier and route, within five working "
         "days of spec sign-off.", "m", 17, (150, 158, 168), 490, lead=1.4)
    para(d, (110, 970), ILLUSTRATIVE + "  Tier volumes are the bands to quote against, "
         "not a commitment.", "m", 19, MUTE, 1700)
    foot(d, 10)
    return pg


# --------------------------------------------------------------------------- 10
def s10_close():
    pg, d = _page(BLUE)
    # the bar goes down first and the blue runs into it - drips drawn under a bar are
    # drips nobody sees
    d.rectangle([0, PAGE[1] - 150, PAGE[0], PAGE[1]], fill=BLACK)
    _drips(d, 40, PAGE[0] - 40, PAGE[1] - 152, 108, BLUE, n=14, seed=21)
    card(pg, d, (1330, 130), (470, 790), "tube_teal_silver", radius=28)

    lockup(d, (110, 120), 62, WHITE, BLACK)
    head(d, (110, 340), "Say yes to the\nshape of it,\nand we spec it.", 68, WHITE, 880)
    steps = [("1", "Pick a route", "B to launch, A packed behind it"),
             ("2", "Pick a way", "one colourway per state, or per strain"),
             ("3", "Sign the lockup", "Puff's own artwork replaces the stand-in"),
             ("4", "Quote", "against a tier, five working days")]
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
    rt = "Concept pack - not an offer. Puff marks shown as stand-ins for approval."
    d.text((PAGE[0] - 110 - d.textlength(rt, font=font("m", 17)), PAGE[1] - 74), rt,
           font=font("m", 17), fill=(120, 130, 140))
    return pg


SLIDES = [s01_cover, s02_premise, s03_piece, s04_why, s05_set, s06_box,
          s06_ways, s07_compliance, s08_drop, s09_money, s10_close]


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
