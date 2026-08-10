"""Twelve joint holders - six drawn feminine, six drawn heavier and iced.

A design is geometry plus a colourway, and the colourway is generated rather than
hand-tuned: give it the colour you want the glass to read and the fume you want under
it, and the Beer-Lambert absorption falls out of that. A new colour is one line rather
than four numbers somebody has to guess at.

No frit anywhere. The body carries spun linework instead - several strands of colour
wound down the tube together, each strand its own material, which is what makes it read
as a twist rather than a stripe.

Stones are their own material and there are two of them on every piece, alternating
round each course: opal beside diamond rather than a row of one thing. A diamond is not
tinted glass - almost no absorption, a hard specular, and flat facets.
"""
import math

SILVER = ((1.00, 1.00, 1.00), (0.90, 0.95, 1.04),
          (0.93, 0.88, 1.08), (1.06, 0.98, 0.86))
GOLD = ((1.00, 0.99, 0.96), (1.06, 0.99, 0.84),
        (1.06, 0.88, 0.84), (0.94, 0.88, 1.06))

STONES = {
    "diamond": ((0.0016, 0.0016, 0.0019), (0.82, 0.86, 0.92)),
    "ice":     ((0.0012, 0.0013, 0.0016), (0.86, 0.90, 0.96)),
    "opal":    ((0.0125, 0.0108, 0.0142), (0.88, 0.80, 0.94)),
    "fireopal": ((0.0090, 0.0165, 0.0250), (0.94, 0.78, 0.62)),
    "gold":    ((0.0040, 0.0105, 0.0225), (0.92, 0.82, 0.54)),
    "ruby":    ((0.0030, 0.0240, 0.0180), (0.92, 0.66, 0.72)),
    "emerald": ((0.0210, 0.0040, 0.0150), (0.66, 0.92, 0.76)),
    "sapphire": ((0.0250, 0.0130, 0.0030), (0.68, 0.78, 0.96)),
}


def absorb(rgb, k=0.062):
    """Absorption that makes glass read as this colour. Beer-Lambert backwards: the
    channel that survives least is the one absorbed most."""
    return tuple(max(-math.log(max(c, 0.008)) * k, 0.0006) for c in rgb)


def way(body, fume, stones, spin_cols, name="", sub="", density=0.062):
    """One colourway in the shape build_renderer expects."""
    a, b = stones
    sa, la = STONES[a]
    sb, lb = STONES[b]
    return dict(
        body=absorb(body, density),
        frit=absorb(body, density * 3.4),           # unused - no frit on this piece
        fume=1.05, fume_pow=1.05,
        fume_stops=SILVER if fume == "silver" else GOLD,
        line=absorb(body, density * 3.0),
        fline=absorb(body, density * 3.0),
        label=(150, 32, 108), label_text=(255, 255, 255),
        wrap=(0.004, 0.004, 0.004),
        stone=sa, stone_line=la, stone2=sb, stone2_line=lb,
        spin_cols=[absorb(c, density * 2.6) for c in spin_cols],
        name=name, sub=sub)


# name, body, fume, (stone A, stone B), spin strand colours, geometry, way name, note
FEMININE = [
    ("Belle Epoque", (0.98, 0.72, 0.82), "silver", ("diamond", "opal"),
     [(1.0, 0.62, 0.76), (1.0, 0.97, 0.99), (0.99, 0.86, 0.60)],
     dict(length=94, bell_od=21.5, waist_od=9.8, marbles=3, bling=30, bling_r=2.2,
          spin=3, spin_turns=7),
     "Rose, silver fume", "rose and gold twist, opal and diamond"),

    ("Opaline", (0.93, 0.90, 0.97), "silver", ("opal", "ice"),
     [(0.98, 0.94, 1.0), (0.86, 0.94, 1.0), (1.0, 0.90, 0.94)],
     dict(length=90, bell_od=22.5, marbles=3, bling=38, bling_r=2.2,
          spin=4, spin_turns=5),
     "Milk opal, silver fume", "four pale strands, opals throughout"),

    ("Lilac Deco", (0.80, 0.68, 0.94), "gold", ("diamond", "sapphire"),
     [(0.72, 0.56, 0.96), (1.0, 0.98, 0.94), (0.60, 0.86, 0.98)],
     dict(length=96, bell_od=22.0, waist_od=9.6, marbles=4, marble_r=3.6,
          bling=34, bling_r=2.2, spin=3, spin_turns=9),
     "Lilac, gold fume", "tight twelve-turn twist"),

    ("Champagne", (0.98, 0.92, 0.78), "gold", ("gold", "fireopal"),
     [(1.0, 0.90, 0.60), (1.0, 0.99, 0.94), (0.98, 0.74, 0.52)],
     dict(length=92, bell_od=23.0, marbles=3, bling=42, bling_r=2.2,
          spin=3, spin_turns=6),
     "Champagne, gold fume", "gold and fire opal, paved to the waist"),

    ("Mint Julep", (0.74, 0.96, 0.88), "silver", ("ice", "opal"),
     [(0.52, 0.94, 0.84), (1.0, 0.99, 0.99), (0.72, 0.86, 1.0)],
     dict(length=100, bell_od=21.0, waist_od=9.4, marbles=4, marble_r=3.8,
          bling=32, bling_r=2.2, spin=4, spin_turns=8),
     "Mint, silver fume", "the long one, at four inches"),

    ("Blush Ice", (0.99, 0.86, 0.90), "silver", ("ice", "diamond"),
     [(1.0, 0.78, 0.86), (1.0, 1.0, 1.0), (0.90, 0.92, 1.0)],
     dict(length=90, bell_od=23.5, marbles=3, bling=56, bling_r=2.2,
          spin=3, spin_turns=7),
     "Blush, silver fume", "paved end to end"),
]

# the heavier six run as a near-parallel tube: waist, shoulder and mouthpiece within a
# millimetre of each other, so it reads cylindrical rather than tapered
MASCULINE = [
    ("Onyx", (0.20, 0.19, 0.22), "gold", ("gold", "diamond"),
     [(1.0, 0.86, 0.46), (0.30, 0.29, 0.33), (1.0, 0.99, 0.96)],
     dict(length=92, bell_od=25.0, waist_od=14.6, body_od=15.0, mouth_od=14.0,
          mouth_bore=5.4, bell_len=22, marbles=3, marble_r=4.8, bling=40,
          bling_r=2.2, spin=3, spin_turns=5),
     "Onyx, gold fume", "straight barrel, gold twist"),

    ("Gunmetal", (0.44, 0.47, 0.52), "silver", ("ice", "diamond"),
     [(0.38, 0.41, 0.47), (0.96, 0.98, 1.0), (0.70, 0.76, 0.84)],
     dict(length=94, bell_od=24.5, waist_od=14.2, body_od=14.6, mouth_od=13.6,
          mouth_bore=5.2, bell_len=22, marbles=3, marble_r=5.0, bling=44,
          bling_r=2.2, spin=3, spin_turns=4),
     "Gunmetal, silver fume", "parallel tube, three big marbles"),

    ("Emerald Cut", (0.26, 0.72, 0.46), "gold", ("emerald", "gold"),
     [(0.16, 0.66, 0.38), (1.0, 0.88, 0.50), (0.96, 0.99, 0.94)],
     dict(length=90, bell_od=25.0, waist_od=14.8, body_od=15.2, mouth_od=14.2,
          mouth_bore=5.4, bell_len=21, marbles=3, marble_r=4.8, bling=48,
          bling_r=2.4, spin=3, spin_turns=6),
     "Emerald, gold fume", "emerald and gold, four courses"),

    ("Iced Out", (0.94, 0.96, 0.99), "silver", ("ice", "diamond"),
     [(0.92, 0.96, 1.0), (1.0, 1.0, 1.0), (0.84, 0.90, 0.98)],
     dict(length=92, bell_od=25.5, waist_od=14.6, body_od=15.2, mouth_od=14.0,
          mouth_bore=5.4, bell_len=22, marbles=3, marble_r=4.8, bling=64,
          bling_r=2.2, spin=3, spin_turns=5),
     "Clear, heavy silver", "paved every course, end to end"),

    ("Bussdown", (0.17, 0.16, 0.19), "gold", ("gold", "fireopal"),
     [(1.0, 0.84, 0.42), (0.26, 0.25, 0.29), (1.0, 0.74, 0.50)],
     dict(length=92, bell_od=26.0, waist_od=15.0, body_od=15.4, mouth_od=14.4,
          mouth_bore=5.6, bell_len=22, marbles=3, marble_r=4.6, bling=64,
          bling_r=2.2, spin=4, spin_turns=5),
     "Black, gold fume", "black glass under a full pave of gold and fire opal"),

    ("Sapphire", (0.22, 0.42, 0.92), "silver", ("sapphire", "ice"),
     [(0.16, 0.36, 0.94), (0.96, 0.99, 1.0), (0.54, 0.74, 1.0)],
     dict(length=94, bell_od=24.5, waist_od=14.2, body_od=14.8, mouth_od=13.8,
          mouth_bore=5.2, bell_len=22, marbles=4, marble_r=4.6, bling=52,
          bling_r=2.2, spin=3, spin_turns=7),
     "Sapphire, silver fume", "sapphire and ice, four marbles"),
]

GROUPS = [("Feminine", FEMININE), ("Heavier and iced", MASCULINE)]


def key(name):
    return name.lower().replace(" ", "_")


def register(mockups):
    """Add every design to mockups.WAYS so build_renderer can find it by key."""
    for _, group in GROUPS:
        for nm, body, fume, stones, spin, geom, wname, wsub in group:
            mockups.WAYS[key(nm)] = way(body, fume, stones, spin, wname, wsub)
    return {key(g[0]): g[5] for _, grp in GROUPS for g in grp}
