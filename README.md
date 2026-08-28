# Clearboy programme — CAD, mockups, site

Reverse-engineered CAD of one hand-blown JBD "Clearboy" hammer bubbler, built from 10
photographs with a stainless rule in frame — plus a matching cork-top nug jar, both mocked
up in two fumed colourways.

**Site:** https://zelidav.github.io/jbd-clearboy/ — spinners, survey, downloads.

## The pieces

| | Clearboy hammer | Nug jar |
|---|---|---|
| Overall | 140 mm | 92 mm glass + cork lid |
| Section | head 68 long, 42 × 37 oval | straight cylinder, ø44 |
| Opening | bowl ø25, ø3 hole in the bottom of the bowl | mouth ø38, cork plug |
| Wall | ≈ 3 mm chamber (inferred) | 3 mm, flat closed bottom |
| Stem | ø14 OD / ø8 bore (thickened from the original's ø11 to carry the enamel label) | — |
| Mark | enamel label, JBD × Boutiq dropped out in white | JBD pressed into a molten stamp pad, lower middle |
| Glass | ≈ 81 g in boro 3.3 | ≈ 90 g + ≈ 10 g cork |
| Frit + marbles | bowl end, 4 clear marbles | band under the rim, 7 marbles around the opening |

Alongside them: a **joint tube** (124 mm, one gram, 4.5 mm wall so it survives a floor,
cork-stopped, drips and a wig wag, the JB mark pressed in, two marbles so it will not
roll) and its **presentation box** (rigid board, hinged lid, magnetic clasp), a **lighter sleeve** (58 mm obround socket cut to BIC's published
J26 Maxi envelope, 81 x 25 x 14), and the earlier **glass tip** and **joint holder**. The tube
and the sleeve are each rendered empty and loaded - the tube with a one-gram cone in it,
the sleeve with a lighter.

Colourways: **bluish teal / silver fume** and **magenta / gold fume**, both frit-rolled with
clear marbles.

**Wall thickness on the hammer is inferred, not measured.** Two caliper readings — rim and
stem OD — lock the whole model. Everything downstream (mass, volume, glass cost, print
scaling) moves if they come back different.

## Layout

    photos/         the 10 source shots (HI_5850–5859)
    JBD_Clearboy_dimensions.png   five-view dimensional survey
    cad/            model + render + build scripts
    out/            STEP / STL / GLB
    shots/          hero stills, box/ composites, spec/ dimensioned closeups, the PDFs
    docs/           the site GitHub Pages serves (spinner frames, mp4 loops)
    frames/         72-position turntable masters (gitignored, regenerate with turntable.py)

## Scripts

| File | Does |
|---|---|
| `cad/model.py` | Hammer solid — head lofted through 13 measured sections, hollowed, bowl funnel, stem bore, carb. STEP + STL. |
| `cad/frit.py` | Frit grains and clear marbles for the hammer, built as meshes. |
| `cad/jar.py` | Jar solid, cork lid, pressed maker's stamp, frit and rim marbles. |
| `cad/tube.py` | Joint tube - flat-bottomed 124 mm tube for a one-gram cone, cork, two anti-roll marbles, drips off the rim, wig wag at the base, and the cone itself for the loaded shot. |
| `cad/lighter.py` | Lighter sleeve - obround socket for a standard full-size lighter, finger notch through the front wall, wig wag at the base, and the lighter (shell / hood / wheel) for the loaded shot. |
| `cad/box.py` | Presentation box - shell, hinged lid shown open, disc magnets, die-cut foam insert. Modelled around the tube where the tube already sits, so the glass meshes and the label projector are reused unchanged. |
| `cad/puffdeck.py` | PUFF x Jerome Baker pitch - page furniture, Puff's palette and type. One piece, one finish: the joint tube in the `puff_blue` colourway. |
| `cad/puffdeck_slides.py` | The nine pages of that pack. |
| `cad/puffpage.py` | The interactive version of it - `docs/puff.html`, drag-to-spin, published on Pages. |
| `cad/render.py` | Studio glass compositor (moderngl): sweep → Beer-Lambert tint with fume shift → density pass → specular → enamel decal. Not a path tracer. |
| `cad/mockups.py` | Pieces, colourways, hero stills. |
| `cad/turntable.py` | 72-position turntables, broadside start, rotating on the piece's own axis. |
| `cad/encode.py` | mp4 loops, posters, WebP spinner frames. |
| `cad/glb_export.py` | GLB with `KHR_materials_transmission` / `_ior` / `_volume` so it reads as glass in three.js / model-viewer / Blender. |
| `cad/build_web.py` | Builds the site into `docs/`. |
| `cad/callouts.py` | Dimensioned closeups. Witness lines are projected from model coordinates through the render camera, so they follow the constants. |
| `cad/specsheet.py` | The manufacturing spec sheet PDF and the hand-off zip: dimensions, closeups, survey, decoration, bench process + QC. |
| `cad/boxshot.py` | Seats the pieces into the Boutiq box plates and lays them out as the leave-behind PDF. |
| `cad/sheet.py` | Page furniture shared by the two PDFs. |

## Rebuild

CadQuery has no 3.13/3.14 wheels yet, so this needs Python 3.12:

```sh
py install 3.12
python3.12 -m venv cadenv
./cadenv/Scripts/python -m pip install -r requirements.txt

./cadenv/Scripts/python cad/model.py out
./cadenv/Scripts/python cad/frit.py out
./cadenv/Scripts/python cad/jar.py out
./cadenv/Scripts/python cad/tube.py out
./cadenv/Scripts/python cad/lighter.py out
./cadenv/Scripts/python cad/box.py out
./cadenv/Scripts/python cad/glb_export.py
./cadenv/Scripts/python cad/turntable.py      # ~0.4 s/frame, 288 frames
./cadenv/Scripts/python cad/encode.py
./cadenv/Scripts/python cad/build_web.py
```

The hand-off is built on top of that:

```sh
./cadenv/Scripts/python cad/callouts.py    # dimensioned closeups -> shots/spec/
./cadenv/Scripts/python cad/specsheet.py   # spec sheet PDF + the zip, into docs/
./cadenv/Scripts/python cad/boxshot.py     # box composites + the leave-behind PDF
./cadenv/Scripts/python cad/puffdeck.py   # PUFF x JBD concept pack -> shots/ and docs/
./cadenv/Scripts/python cad/puffpage.py   # the interactive version -> docs/puff.html
```

`cad/boxshot.py` needs the Boutiq box plates; the path is at the top of the file.

Run from the repo root — paths (`out/`, `frames/`, `docs/`) are relative to it.

The renders are proposals. The original hand-blown piece stays the reference; the remodeller
on the site produces variant requests and never overwrites it.
