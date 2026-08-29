"""The same box, three strains.

One piece of glass, one box, one tool. What changes is the sleeve printed on the box and
the card that goes in it - so a second drop is a print run rather than a new product.

These are the real box render, three times, with a different sleeve on each and the
matching card beside it. Nothing about the piece or the box is remodelled between them,
which is the entire point of the page.

    python cad/box_variants.py     -> shots/puff_box_variants.png
"""
import math, os, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mockups
import variable_art
from mockups import PUFF, brand_font, puff_mark, _tracked_text, _tracked_width, _pill

OUT = os.path.join("shots", "puff_box_variants.png")
OUT_ROW = os.path.join("shots", "puff_box_variants_row.png")
WAY = "puff_blue"


def sleeve_art(name, accent, w=2400, h=740):
    """The printed sleeve on the outside of the box, in one drop's colour.

    Same furniture as every other printed part - their mark, the cross, our name, a
    keyline - with the strain in a pill of its own colour underneath."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = int(h * 0.035)
    frame = [int(w * 0.020), m, int(w * 0.980), h - m]
    fw, fh = frame[2] - frame[0], frame[3] - frame[1]
    cx, cy = (frame[0] + frame[2]) / 2.0, (frame[1] + frame[3]) / 2.0
    d.rounded_rectangle(frame, radius=int(min(fh, fw) * 0.26),
                        outline=PUFF["gold"] + (255,), width=max(int(h * 0.016), 3))

    u = min(fh, fw * 0.34)
    room = fw * 0.78
    scale = 1.0
    for _ in range(9):
        mark = puff_mark(max(u * 0.52 * scale, 6), PUFF["paper"])
        ours = brand_font("bold", max(int(u * 0.215 * scale), 7))
        tiny = brand_font("med", max(int(u * 0.105 * scale), 6))
        cross = brand_font("heavy", max(int(u * 0.27 * scale), 7))
        jb_w = d.textlength("JEROME BAKER", font=ours)
        des_w = _tracked_width(d, "DESIGNS", tiny, u * 0.060 * scale)
        left_w, right_w = mark.width, max(jb_w, des_w)
        x_w = d.textlength("×", font=cross)
        gap = u * 0.26 * scale
        total = left_w + gap + x_w + gap + right_w
        if total <= room:
            break
        scale *= room / total

    top = cy - u * 0.18
    x = cx - total / 2
    img.paste(mark, (int(x), int(cy - u * 0.10 - mark.height / 2)), mark)
    x += left_w + gap
    d.text((x, top - u * 0.18 * scale), "×", font=cross, fill=PUFF["gold"] + (255,))
    x += x_w + gap
    d.text((x + (right_w - jb_w) / 2, top - u * 0.22 * scale), "JEROME BAKER",
           font=ours, fill=PUFF["paper"] + (255,))
    _tracked_text(d, (x + (right_w - des_w) / 2, top + u * 0.09 * scale), "DESIGNS",
                  tiny, PUFF["gold"] + (255,), u * 0.060 * scale)

    # the strain, in its own colour - the one thing that changes
    fs = u * 0.105
    for _ in range(8):
        ff = brand_font("bold", max(int(fs), 6))
        fpad, ftrack = fs * 0.62, fs * 0.34
        fwid = _tracked_width(d, name, ff, ftrack) + 2 * fpad * 1.6
        if fwid <= fw * 0.62:
            break
        fs *= (fw * 0.62) / fwid
    _pill(d, (cx - fwid / 2, cy + u * 0.285), name, ff, accent, PUFF["paper"],
          fpad, ftrack)
    return img


def render(name, accent):
    """The box still, with this drop's sleeve on it."""
    p = mockups.PIECES["box"]
    p["wrap_art"] = sleeve_art(name, accent)
    W, H = mockups.size_of("box")
    r = mockups.build_renderer("box", WAY, W, H)
    angle = mockups.SIDE + math.radians(p.get("yaw", 0.0))
    im = mockups.frame(r, "box", angle)
    p.pop("wrap_art", None)
    return im


def build(row=False):
    """row=True lays the three across for a slide; the column suits a web page."""
    os.makedirs("shots", exist_ok=True)
    drops = variable_art.DROPS
    shots = [(n, c, render(n, c)) for n, c in drops]
    cards = {n: variable_art.beauty_card(n, c) for n, c in drops}

    bw, bh = shots[0][2].size
    scale = 0.62
    bw, bh = int(bw * scale), int(bh * scale)
    ch = int(bh * 0.86)
    cw = int(cards[drops[0][0]].width * ch / cards[drops[0][0]].height)

    pad, lab = 34, 52
    if row:
        cw2 = int(bw * 0.30)
        ch2 = int(cards[drops[0][0]].height * cw2 / cards[drops[0][0]].width)
        w = pad + (bw + pad) * len(shots)
        h = pad + lab + bh + pad + ch2 + pad
        plate = Image.new("RGB", (w, h), (244, 247, 250))
        d = ImageDraw.Draw(plate)
        f = brand_font("bold", 30)
        x = pad
        for name, accent, im in shots:
            d.text((x, pad), name, font=f, fill=(34, 38, 44))
            plate.paste(im.resize((bw, bh), Image.LANCZOS), (x, pad + lab))
            card = cards[name].resize((cw2, ch2), Image.LANCZOS)
            plate.paste(card, (x + (bw - cw2) // 2, pad + lab + bh + pad), card)
            x += bw + pad
        plate.save(OUT_ROW)
        print("wrote", OUT_ROW, plate.size)
        return OUT_ROW

    w = pad * 2 + bw + cw + pad
    h = pad + (bh + lab + pad) * len(shots)
    plate = Image.new("RGB", (w, h), (244, 247, 250))
    d = ImageDraw.Draw(plate)
    f = brand_font("bold", 30)
    fs = brand_font("med", 22)

    y = pad
    for name, accent, im in shots:
        d.text((pad, y), name, font=f, fill=(34, 38, 44))
        d.text((pad + d.textlength(name, font=f) + 18, y + 8),
               "same box, same glass", font=fs, fill=(128, 134, 142))
        y += lab
        plate.paste(im.resize((bw, bh), Image.LANCZOS), (pad, y))
        card = cards[name].resize((cw, ch), Image.LANCZOS)
        plate.paste(card, (pad + bw + pad, y + (bh - ch) // 2), card)
        y += bh + pad

    plate.save(OUT)
    print("wrote", OUT, plate.size)
    return OUT


if __name__ == "__main__":
    build()
    build(row=True)
