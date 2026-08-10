"""Twelve joint holders - six drawn feminine, six drawn masculine and iced.

A design is geometry plus a colourway, and the colourway is generated rather than
hand-tuned: give it the colour you want the glass to read and the fume you want under
it, and the Beer-Lambert absorption falls out of that. It means a new colour is one line
rather than four numbers somebody has to guess at.

Stones are their own material. A diamond is not tinted glass - almost no absorption, a
hard specular and flat facets - and an opal is the same thing with a milky body and a
warmer flash.
"""
import math

SILVER = ((1.00, 1.00, 1.00), (0.90, 0.95, 1.04),
          (0.93, 0.88, 1.08), (1.06, 0.98, 0.86))
GOLD = ((1.00, 0.99, 0.96), (1.06, 0.99, 0.84),
        (1.06, 0.88, 0.84), (0.94, 0.88, 1.06))

STONES = {
    "diamond": dict(stone=(0.0016, 0.0016, 0.0019), stone_line=(0.82, 0.86, 0.92)),
    "opal":    dict(stone=(0.0125, 0.0108, 0.0142), stone_line=(0.88, 0.80, 0.94)),
    "gold":    dict(stone=(0.0040, 0.0105, 0.0225), stone_line=(0.92, 0.82, 0.54)),
    "ruby":    dict(stone=(0.0030, 0.0240, 0.0180), stone_line=(0.92, 0.66, 0.72)),
    "ice":     dict(stone=(0.0012, 0.0013, 0.0016), stone_line=(0.86, 0.90, 0.96)),
}


def absorb(rgb, k=0.062):
    """Absorption that makes glass read as this colour. Beer-Lambert backwards: the
    channel that survives least is the one absorbed most."""
    return tuple(max(-math.log(max(c, 0.008)) * k, 0.0006) for c in rgb)


def way(body, fume="silver", frit=None, stone="diamond", name="", sub="",
        density=0.062, fume_amt=1.05):
    """One colourway in the shape build_renderer expects."""
    frit = frit or body
    s = dict(STONES[stone])
    return dict(
        body=absorb(body, density),
        frit=absorb(frit, density * 3.4),
        fume=fume_amt, fume_pow=1.05,
        fume_stops=SILVER if fume == "silver" else GOLD,
        line=absorb(body, density * 3.0),
        fline=absorb(frit, density * 3.0),
        label=(150, 32, 108), label_text=(255, 255, 255),
        wrap=(0.004, 0.004, 0.004),
        name=name, sub=sub, **s)


# body colour, fume, frit colour, stone, geometry overrides
FEMININE = [
    ("Belle Epoque", (0.98, 0.72, 0.82), "silver", (0.94, 0.55, 0.70), "diamond",
     dict(length=94, bell_od=21.5, waist_od=9.8, marbles=3),
     "Rose, silver fume", "the plain one - slim, three marbles, nothing else"),
    ("Opaline", (0.93, 0.90, 0.97), "silver", (0.88, 0.86, 0.96), "opal",
     dict(length=90, bell_od=22.5, marbles=3, bling=12, bling_r=1.9),
     "Milk opal, silver fume", "opals set round the shoulder"),
    ("Lilac Deco", (0.80, 0.68, 0.94), "gold", (0.66, 0.52, 0.88), "diamond",
     dict(length=96, bell_od=22.0, waist_od=9.6, marbles=4, marble_r=3.6),
     "Lilac, gold fume", "four smaller marbles, longer stem"),
    ("Champagne", (0.98, 0.92, 0.78), "gold", (0.95, 0.86, 0.62), "gold",
     dict(length=92, bell_od=23.0, marbles=3, bling=16),
     "Champagne, gold fume", "gold stones round the bell"),
    ("Mint Julep", (0.74, 0.96, 0.88), "silver", (0.55, 0.92, 0.84), "diamond",
     dict(length=100, bell_od=21.0, waist_od=9.4, marbles=4, marble_r=3.8),
     "Mint, silver fume", "the long one, at four inches"),
    ("Blush Ice", (0.99, 0.86, 0.90), "silver", (0.97, 0.78, 0.86), "ice",
     dict(length=90, bell_od=23.5, marbles=3, bling=30, bling_r=1.5),
     "Blush, silver fume", "paved to the waist"),
]

MASCULINE = [
    ("Onyx", (0.20, 0.19, 0.22), "gold", (0.13, 0.12, 0.15), "gold",
     dict(length=92, bell_od=25.0, waist_od=12.2, body_od=15.0, marbles=3,
          marble_r=4.8),
     "Onyx, gold fume", "heavier all through, no stones"),
    ("Gunmetal", (0.44, 0.47, 0.52), "silver", (0.30, 0.33, 0.38), "ice",
     dict(length=94, bell_od=24.5, waist_od=11.8, body_od=14.4, marbles=3,
          marble_r=5.0),
     "Gunmetal, silver fume", "three big marbles down the side"),
    ("Emerald Cut", (0.26, 0.72, 0.46), "gold", (0.16, 0.58, 0.34), "gold",
     dict(length=90, bell_od=25.0, waist_od=12.0, body_od=15.0, marbles=3,
          bling=20, bling_r=1.9),
     "Emerald, gold fume", "a course of gold round the shoulder"),
    ("Iced Out", (0.94, 0.96, 0.99), "silver", (0.86, 0.92, 0.99), "ice",
     dict(length=92, bell_od=25.5, waist_od=12.0, body_od=15.2, marbles=3,
          bling=44, bling_r=1.6),
     "Clear, heavy silver", "paved end to end"),
    ("Bussdown", (0.17, 0.16, 0.19), "gold", (0.12, 0.11, 0.13), "gold",
     dict(length=92, bell_od=26.0, waist_od=12.4, body_od=15.4, marbles=3,
          marble_r=4.6, bling=44, bling_r=1.7),
     "Black, gold fume", "black glass under a full pave of gold"),
    ("Sapphire", (0.22, 0.42, 0.92), "silver", (0.14, 0.30, 0.82), "ice",
     dict(length=94, bell_od=24.5, waist_od=11.6, body_od=14.6, marbles=4,
          bling=24, bling_r=1.8),
     "Sapphire, silver fume", "four marbles, stones at the shoulder"),
]

GROUPS = [("Feminine", FEMININE), ("Masculine and iced", MASCULINE)]


def key(name):
    return name.lower().replace(" ", "_")


def register(mockups):
    """Add every design to mockups.WAYS so build_renderer can find it by key."""
    for _, group in GROUPS:
        for nm, body, fume, frit, stone, geom, wname, wsub in group:
            mockups.WAYS[key(nm)] = way(body, fume, frit, stone, wname, wsub)
    return {key(g[0]): g[5] for _, grp in GROUPS for g in grp}
