"""Lift the Boutiq brand fonts out of the brand guide and make them loadable.

The guide embeds Urbane Rounded as bare CFF subsets, which FreeType will not open on
its own, so each one is wrapped back into an OTF with the tables a font needs to be a
font. The subsets carry A-Z, a-z, the digits and basic punctuation - enough to set a
deck, not enough to typeset a novel; anything missing falls back at draw time.

Silkscreen comes out as a whole TrueType and is written straight through.

    python cad/brandfonts.py     -> assets/fonts/*.otf
"""
import io, os, sys

GUIDE = ("C:/Users/zelid/OneDrive/Documents/Boutiq Collab/Reference/"
         "Boutiq Brand Guide 2026.pdf")
OUT = os.path.join("assets", "fonts")


def extract(pdf=GUIDE):
    """Pull every embedded font out of the guide, as it is stored."""
    import pymupdf
    os.makedirs(OUT, exist_ok=True)
    d = pymupdf.open(pdf)
    got, seen = [], set()
    for i in range(d.page_count):
        for f in d[i].get_fonts(full=True):
            if f[0] in seen:
                continue
            seen.add(f[0])
            name, ext, _, buf = d.extract_font(f[0])
            if not buf or ext == "n/a":
                continue
            p = os.path.join(OUT, "%s.%s" % (name.split("+")[-1], ext))
            with open(p, "wb") as fh:
                fh.write(buf)
            got.append(p)
    return got


def wrap_cff(path):
    """A bare CFF plus the minimum sfnt tables around it: head, hhea, hmtx, maxp,
    cmap, name, OS/2, post. Metrics come out of the CFF itself."""
    from fontTools.ttLib import TTFont, newTable
    from fontTools.cffLib import CFFFontSet
    from fontTools import agl

    with open(path, "rb") as fh:
        data = fh.read()
    cff = CFFFontSet()
    cff.decompile(io.BytesIO(data), None)
    top = cff[cff.fontNames[0]]
    order = [".notdef"] + [g for g in top.CharStrings.keys() if g != ".notdef"]

    font = TTFont(sfntVersion="OTTO")
    font.setGlyphOrder(order)
    font["CFF "] = newTable("CFF ")
    font["CFF "].cff = cff

    from fontTools.pens.basePen import NullPen

    upm = int(1.0 / (top.FontMatrix[0] or 0.001) + 0.5)
    ymin, ymax, widths = 0, 0, {}
    for g in order:
        cs = top.CharStrings[g]
        # a charstring only carries a width when it differs from the default, and it is
        # the outline extractor that resolves that against nominalWidthX - decompile on
        # its own leaves .width None, which silently collapses the whole font to one
        # advance and stacks every letter on the one before it
        cs.draw(NullPen())
        b = cs.calcBounds(top.CharStrings) or (0, 0, 0, 0)
        widths[g] = (int(cs.width), int(b[0]))
        ymin, ymax = min(ymin, int(b[1])), max(ymax, int(b[3]))

    head = font["head"] = newTable("head")
    head.tableVersion, head.fontRevision = 1.0, 1.0
    head.checkSumAdjustment = head.magicNumber = 0
    head.magicNumber = 0x5F0F3CF5
    head.flags, head.unitsPerEm = 3, upm
    head.created = head.modified = 0
    head.xMin, head.yMin, head.xMax, head.yMax = 0, ymin, upm, ymax
    head.macStyle = head.lowestRecPPEM = 0
    head.lowestRecPPEM = 6
    head.fontDirectionHint, head.indexToLocFormat, head.glyphDataFormat = 2, 0, 0

    hhea = font["hhea"] = newTable("hhea")
    hhea.tableVersion = 0x00010000
    hhea.ascent, hhea.descent, hhea.lineGap = int(upm * 0.80), int(-upm * 0.20), 0
    hhea.advanceWidthMax = max(w for w, _ in widths.values())
    hhea.minLeftSideBearing = hhea.minRightSideBearing = 0
    hhea.xMaxExtent = hhea.advanceWidthMax
    hhea.caretSlopeRise, hhea.caretSlopeRun, hhea.caretOffset = 1, 0, 0
    hhea.reserved0 = hhea.reserved1 = hhea.reserved2 = hhea.reserved3 = 0
    hhea.metricDataFormat, hhea.numberOfHMetrics = 0, len(order)

    font["hmtx"] = newTable("hmtx")
    font["hmtx"].metrics = widths

    maxp = font["maxp"] = newTable("maxp")
    maxp.tableVersion, maxp.numGlyphs = 0x00005000, len(order)

    cmap = {}
    for g in order:
        u = agl.toUnicode(g)
        if len(u) == 1:
            cmap.setdefault(ord(u), g)
    font["cmap"] = newTable("cmap")
    font["cmap"].tableVersion = 0
    sub = newTable("cmap").__class__.__mro__ and None
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
    t4 = CmapSubtable.newSubtable(4)
    t4.platformID, t4.platEncID, t4.language, t4.cmap = 3, 1, 0, cmap
    font["cmap"].tables = [t4]

    stem = os.path.splitext(os.path.basename(path))[0]
    name = font["name"] = newTable("name")
    name.names = []
    fam, sub_ = stem.split("-", 1) if "-" in stem else (stem, "Regular")
    for nid, val in ((1, fam), (2, sub_), (4, stem), (6, stem)):
        name.setName(val, nid, 3, 1, 0x409)

    os2 = font["OS/2"] = newTable("OS/2")
    os2.version = 4
    os2.xAvgCharWidth = int(sum(w for w, _ in widths.values()) / max(len(widths), 1))
    os2.usWeightClass = 600 if "Demi" in stem or "Bold" in stem else 300
    os2.usWidthClass, os2.fsType = 5, 0
    for k in ("ySubscriptXSize", "ySubscriptYSize", "ySubscriptXOffset",
              "ySubscriptYOffset", "ySuperscriptXSize", "ySuperscriptYSize",
              "ySuperscriptXOffset", "ySuperscriptYOffset", "yStrikeoutSize",
              "yStrikeoutPosition"):
        setattr(os2, k, 0)
    os2.sFamilyClass = 0
    os2.panose = newTable("OS/2").__class__ and __import__(
        "fontTools.ttLib.tables.O_S_2f_2", fromlist=["Panose"]).Panose()
    os2.ulUnicodeRange1 = os2.ulUnicodeRange2 = 0
    os2.ulUnicodeRange3 = os2.ulUnicodeRange4 = 0
    os2.achVendID = "NONE"
    os2.fsSelection = 0x40
    os2.usFirstCharIndex = min(cmap) if cmap else 0
    os2.usLastCharIndex = max(cmap) if cmap else 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = hhea.ascent, hhea.descent, 0
    os2.usWinAscent, os2.usWinDescent = hhea.ascent, -hhea.descent
    os2.ulCodePageRange1 = os2.ulCodePageRange2 = 1
    os2.sxHeight, os2.sCapHeight = int(upm * 0.5), int(upm * 0.7)
    os2.usDefaultChar = os2.usBreakChar = 0
    os2.usBreakChar = 32
    os2.usMaxContext = 0

    post = font["post"] = newTable("post")
    post.formatType, post.italicAngle = 3.0, 0
    post.underlinePosition, post.underlineThickness = -int(upm * 0.1), int(upm * 0.05)
    post.isFixedPitch = post.minMemType42 = post.maxMemType42 = 0
    post.minMemType1 = post.maxMemType1 = 0

    out = os.path.splitext(path)[0] + ".otf"
    font.save(out)
    return out


if __name__ == "__main__":
    for p in extract():
        print("extracted", p)
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".cff"):
            try:
                print("wrapped  ", wrap_cff(os.path.join(OUT, f)))
            except Exception as e:
                print("FAILED   ", f, "-", e)
