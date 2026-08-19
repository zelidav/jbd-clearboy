# -*- coding: utf-8 -*-
"""Rev B strings for the manufacturing spec sheet - the build with no frit.

Same shape as the Rev A data in specsheet.py, so the layout code does not care which
revision it is setting. Only the blocks that mention frit are restated here; everything
else - dimensions, decals, BOM, anneal and QC - is shared, because none of it moves.

Rev B is not Rev A with a step deleted. Taking the frit off changes what the linework
and the marbles sit on: on Rev A both land on a rolled, grainy band and read against it,
on Rev B they land on smooth fumed glass and are the only texture on the piece. The
band heights are kept anyway - they are where the decoration belongs on this shape,
frit or no frit.
"""

DECOR = [
    ("Hammer", "Body", "No frit. The bowl end is left smooth - transparent wash over "
                       "the fume, worked flat to the rim. The fume is the whole surface "
                       "on this build, so any cloud or scorch in it shows."),
    ("Hammer", "Linework", "About 13 turns at 2.4 pitch over the head, plus rings at the "
                           "foot. Clear over the fumed body. Laid down before the "
                           "marbles, so it runs behind them."),
    ("Hammer", "Marbles", "4 clear marbles, ø 6.5–7.5, set on the bowl end over the "
                          "linework, within the outer 54 mm of the chamber. "
                          "Hand-placed, not evenly spaced."),
    ("Hammer", "Label", "Enamel, on the stem, 20–74 mm up from the foot face. JBD × Boutiq "
                        "dropped out in white. The print reads one way along the stem — strike "
                        "it to read with the head to the left."),
    ("Jar", "Body", "No frit. Straight fumed wall from base to rim, no band."),
    ("Jar", "Linework", "9 turns at 2.4 pitch round the opening, 66–90.5 mm up from the "
                        "base, laid down before the marbles."),
    ("Jar", "Marbles", "7 clear marbles, ø 8, evenly spaced, centres 84.5 mm up, set "
                       "over the linework."),
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
    "Rev B carries no frit. With the grain gone the fume and the wash are the entire "
    "surface, so the even lay called for in the process pages is a pass / fail item "
    "here rather than a preference.",
    "Supplied with this sheet: clearboy_hammer.step / .stl and jar.step / .stl, plus the "
    "marble and cork meshes. STEP is the reference; the meshes are for print and "
    "mould work only.",
]

WAYS = [("teal_silver", "Bluish teal body, silver fume. No frit, clear marbles."),
        ("magenta_gold", "Magenta body, gold fume. No frit, clear marbles.")]

# only the two that name frit are restated - the rest come from Rev A
PAGES = {
    "decor": ("Decoration and colourways",
              "Linework, marbles, the enamel label and the pressed mark — both "
              "colourways carry the same work, and neither carries frit"),
    "sop_jar": ("Process — nug jar and cork",
                "Same order of work: shape, fume, colour, linework, marbles, mark."),
}

CLOSEUPS = {
    "jar_body": ("Nug jar elevation",
                 "Body, mouth and the marbles set around the opening."),
}

SOP_HAMMER = [
    ("Stock", [
        "Borosilicate 3.3 throughout. Chamber off tube nominally ø 38-42 with a 3.5-4 "
        "wall; stem off ø 14 OD / ø 8 ID tube; foot off the same stem stock.",
        "Colour: transparent teal or magenta rod for the wash, clear marble stock, and "
        "silver or gold for the fume per colourway. No frit on this revision - do not "
        "substitute one in to cover an uneven wash.",
    ]),
    ("Chamber", [
        "Close and shape one end into the rounded lobe. Blow the chamber out to 68 "
        "long, working the section oval to 42 × 37 - paddle and marver it, do not "
        "blow it round in a mould.",
        "Fume the inside before any colour goes on. The fume is what shifts in use; "
        "colour laid under it kills that.",
        "Lay the transparent wash over the fume, even from lobe to rim. Nothing goes "
        "over this surface on Rev B, so an uneven lay stays visible on the finished "
        "piece - it is a reject, not something to roll frit over.",
    ]),
    ("Linework", [
        "Spin the linework straight onto the fumed body, about 13 turns at 2.4 pitch "
        "over the head, plus a few rings round the foot.",
        "Melt it in flush. On Rev A the frit hides a proud line; here it does not, so "
        "run a hand over the piece before it goes to the kiln.",
    ]),
    ("Marbles", [
        "Set 4 clear marbles ø 6.5-7.5 by hand on the bowl end, within the outer 54 of "
        "the chamber, on top of the linework - the lines run behind them, not across "
        "them.",
        "They are not evenly spaced and should not look it. Encase them fully; no "
        "open seam.",
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
]

SOP_JAR = [
    ("Body", [
        "Cut ø 44 × 3 wall tube to 92 plus working allowance. Close the bottom flat "
        "with a 3 floor - flat enough to stand without rocking.",
        "Fume the inside, then lay the wash over it, same order as the hammer. Even "
        "from base to rim - the wall is left bare on this revision.",
    ]),
    ("Linework", [
        "Spin 9 turns at 2.4 pitch round the opening, 66-90.5 up from the base - the "
        "height the frit band occupies on Rev A. Lines go down before any marble is "
        "set.",
    ]),
    ("Marbles and mark", [
        "Set 7 clear marbles ø 8 evenly round the opening, centres 84.5 up, over the "
        "linework. Evenly spaced here - the jar reads as a ring, the hammer does not.",
        "Press the JBD mark into a molten stamp pad on the wall, lower middle, centre "
        "28 up. Die face about 28 × 11.",
    ]),
    ("Mouth", [
        "Open and true the mouth to ø 38 ID. Hold the OD at 44 right up to the rim - "
        "straight cylinder, no shoulder, no flare.",
    ]),
    ("Cork", [
        "Natural cork, 27 long, ø 36.6 at the bottom and ø 41 at the top. One gentle "
        "taper, no mushroom cap.",
        "Fit to the piece it ships with: 15 into the mouth, about 12 standing proud, "
        "seating on the taper rather than bottoming out.",
    ]),
]
