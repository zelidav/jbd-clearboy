"""Build the Clearboy site.

  docs/index.html      mockups - piece x colourway spinner, specs, remodeller
  docs/survey.html     the measured survey, bench notes, schedule
  docs/downloads.html  every file in the package
  docs/mockups_selfcontained.html   same as index with assets inlined, for sharing as one file

docs/ is what GitHub Pages serves. Run from the repo root.

    python build_web.py
"""
import base64, hashlib, json, mimetypes, os, shutil

SITE = "docs"
REPO = "zelidav/jbd-clearboy"
RAW = "https://raw.githubusercontent.com/%s/main/" % REPO
CONTACT = "david@canismajorpartners.com"
# the trigger service holds the GitHub token; the page only knows the URL and a
# throwaway key that keeps casual traffic off it
RENDER_URL = "https://jbd-clearboy-render-804083036164.us-east1.run.app/render"
RENDER_KEY = "NBvIvBZfVeFWVrIYSBqy6Sa-"

PIECES = ["hammer", "jar", "holder", "tip"]
WAYS = ["teal_silver", "magenta_gold", "clear_silver", "clear_gold"]

PIECE_META = {
    "hammer": dict(name="Clearboy hammer", code="JBD-CB-140",
                   note="140 mm, from the measured original"),
    "jar":    dict(name="Nug jar", code="JBD-NJ-92",
                   note="92 mm straight cylinder, 38 mm opening, cork lid"),
    "holder": dict(name="Joint holder", code="JBD-JH-90",
                   note="90 mm, flared bell grips any joint, marbles stop it rolling"),
    "tip":    dict(name="Glass tip", code="JBD-GT-19",
                   note="19 mm filter tip, screen across the bore, oblique paper slot"),
}
# sampled off assets/northstar_rods.jpg - what the shop can actually pull
STOCK = {
    "teal_silver":  dict(body="Mint", body_hex="#C9E8E1", rod="rod 13 (4th from bottom)",
                         accent="Mint", accent_hex="#8FC8BC",
                         fume="Silver (silver nitrate)"),
    "magenta_gold": dict(body="Pink", body_hex="#D7BFC7", rod="rod 3 (3rd from top)",
                         accent="Pink", accent_hex="#C77E96",
                         fume="Gold (gold chloride)"),
    "clear_silver": dict(body="Clear", body_hex="#F7F8FA", rod="rod 9",
                         accent="Mint", accent_hex="#8FC8BC",
                         fume="Silver, heavy"),
    "clear_gold":   dict(body="Clear", body_hex="#F7F8FA", rod="rod 9",
                         accent="Pink", accent_hex="#C77E96",
                         fume="Gold, heavy"),
}

WAY_META = {
    "teal_silver":  dict(name="Mint (rod 13)", sub="silver fume",
                         dot="linear-gradient(145deg,#E4F5EF,#C9E8E1 60%,#8FC8BC)",
                         ring="#8FC8BC"),
    "magenta_gold": dict(name="Pink (rod 3)", sub="gold fume",
                         dot="linear-gradient(145deg,#F0A0C8,#C0348A 62%,#7E1E5C)",
                         ring="#C0348A"),
    "clear_silver": dict(name="Clear, heavy silver fume", sub="teal accents, linework",
                         dot="linear-gradient(145deg,#EDF2F6,#9FB6E0 55%,#6E8CC4)",
                         ring="#8FC8BC"),
    "clear_gold": dict(name="Clear, heavy gold fume", sub="magenta accents, linework",
                       dot="linear-gradient(145deg,#FBF3E4,#E0BE7A 55%,#C08A3E)",
                       ring="#C77E96"),
}

# what the remodeller starts from, and always keeps as the ghost outline
BASE = {
 "hammer": [
   dict(k="height",  label="Overall height",   v=140,  min=110, max=180, step=1,   unit="mm"),
   dict(k="headlen", label="Head length",      v=68,   min=48,  max=95,  step=1,   unit="mm"),
   dict(k="headsec", label="Head max section", v=42,   min=30,  max=58,  step=1,   unit="mm"),
   dict(k="stemod",  label="Stem OD",          v=14,   min=10,  max=20,  step=0.5, unit="mm"),
   dict(k="stemlen", label="Stem length",      v=88,   min=60,  max=120, step=1,   unit="mm"),
   dict(k="bowlid",  label="Bowl opening",     v=25,   min=18,  max=34,  step=1,   unit="mm"),
   dict(k="footod",  label="Foot diameter",    v=24.5, min=18,  max=34,  step=0.5, unit="mm"),
   dict(k="marbles", label="Marbles",          v=4,    min=0,   max=8,   step=1,   unit=""),
   dict(k="scatter", label="Marble scatter",   v=0,    min=0,   max=40,  step=1,   unit=""),
   dict(k="lines",   label="Spiral turns",     v=13,   min=0,   max=30,  step=1,   unit="turns"),
   dict(k="linepitch", label="Drop per turn",  v=2.4,  min=1.0, max=8.0, step=0.2, unit="mm"),
 ],
 "hammer_flat": [
   dict(k="height",  label="Overall height",   v=140,  min=110, max=180, step=1,   unit="mm"),
   dict(k="headlen", label="Head length",      v=68,   min=48,  max=95,  step=1,   unit="mm"),
   dict(k="headsec", label="Head max section", v=42,   min=30,  max=58,  step=1,   unit="mm"),
   dict(k="stemod",  label="Stem OD",          v=14,   min=10,  max=20,  step=0.5, unit="mm"),
   dict(k="stemlen", label="Stem length",      v=88,   min=60,  max=120, step=1,   unit="mm"),
   dict(k="bowlid",  label="Bowl opening",     v=25,   min=18,  max=34,  step=1,   unit="mm"),
   dict(k="footod",  label="Foot diameter",    v=24.5, min=18,  max=34,  step=0.5, unit="mm"),
   dict(k="marbles", label="Marbles",          v=4,    min=0,   max=8,   step=1,   unit=""),
   dict(k="scatter", label="Marble scatter",   v=0,    min=0,   max=40,  step=1,   unit=""),
 ],
 "tip": [
   dict(k="length",      label="Overall length",  v=19,   min=14,  max=32,  step=0.5, unit="mm"),
   dict(k="od",          label="Outside diameter", v=9,   min=7,   max=15,  step=0.2, unit="mm"),
   dict(k="bore",        label="Bore",            v=6.4,  min=4,   max=12,  step=0.2, unit="mm"),
   dict(k="screen_z",    label="Screen depth in", v=6.5,  min=2,   max=16,  step=0.5, unit="mm"),
   dict(k="screen_t",    label="Screen thickness", v=1.5, min=0.8, max=3.0, step=0.1, unit="mm"),
   dict(k="screen_holes", label="Screen holes",   v=7,    min=0,   max=13,  step=1,   unit=""),
   dict(k="screen_hole_d", label="Hole diameter", v=1.25, min=0.6, max=2.6, step=0.05, unit="mm"),
   dict(k="groove_deg",  label="Slot rake",       v=68,   min=20,  max=85,  step=1,   unit="deg"),
   dict(k="groove_w",    label="Slot width",      v=0.75, min=0.4, max=2.2, step=0.05, unit="mm"),
   dict(k="groove_depth", label="Slot depth",     v=0.9,  min=0.3, max=1.2, step=0.05, unit="mm"),
   dict(k="groove_z",    label="Slot position",   v=9.5,  min=3,   max=18,  step=0.5, unit="mm"),
 ],
 "holder": [
   dict(k="length",     label="Overall length",   v=90,   min=76,  max=112, step=1,   unit="mm"),
   dict(k="bell_od",    label="Bell outside",     v=23,   min=17,  max=31,  step=0.5, unit="mm"),
   dict(k="bell_id",    label="Bell opening",     v=15,   min=10,  max=22,  step=0.5, unit="mm"),
   dict(k="throat_id",  label="Throat",           v=6.4,  min=4,   max=11,  step=0.2, unit="mm"),
   dict(k="bell_len",   label="Bell length",      v=26,   min=16,  max=40,  step=1,   unit="mm"),
   dict(k="body_od",    label="Shoulder OD",      v=13.2, min=10,  max=19,  step=0.2, unit="mm"),
   dict(k="waist_od",   label="Waist OD",         v=10.4, min=8,   max=16,  step=0.2, unit="mm"),
   dict(k="mouth_od",   label="Mouthpiece OD",    v=9.6,  min=7,   max=15,  step=0.2, unit="mm"),
   dict(k="mouth_bore", label="Mouthpiece bore",  v=4.2,  min=3,   max=7,   step=0.1, unit="mm"),
   dict(k="marbles",    label="Marbles",          v=3,    min=0,   max=6,   step=1,   unit=""),
   dict(k="marble_r",   label="Marble radius",    v=4.2,  min=2.5, max=6.5, step=0.1, unit="mm"),
   dict(k="bling",      label="Stones",           v=0,    min=0,   max=60,  step=1,   unit=""),
   dict(k="bling_r",    label="Stone radius",     v=2.2,  min=1.0, max=3.4, step=0.1, unit="mm"),
   dict(k="spin",       label="Twist strands",    v=3,    min=0,   max=6,   step=1,   unit=""),
   dict(k="spin_turns", label="Twist turns",      v=6,    min=2,   max=16,  step=1,   unit="turns"),
   dict(k="loop_r",     label="Chain ring",       v=4.0,  min=2.5, max=7.0, step=0.1, unit="mm"),
   dict(k="loop_t",     label="Ring section",     v=1.45, min=0.9, max=2.6, step=0.05, unit="mm"),
   dict(k="frit_from",  label="Frit starts at",   v=68,   min=30,  max=95,  step=1,   unit="%"),
 ],
 "jar": [
   dict(k="height",  label="Glass height",     v=92, min=70, max=130, step=1,   unit="mm"),
   dict(k="mouthid", label="Mouth opening",    v=38, min=28, max=53,  step=1,   unit="mm"),
   dict(k="wall",    label="Wall thickness",   v=3,  min=2,  max=6,   step=0.5, unit="mm"),
   dict(k="fritz",   label="Frit band depth",  v=25, min=10, max=50,  step=1,   unit="mm"),
   dict(k="corkh",   label="Cork above rim",   v=20, min=10, max=34,  step=1,   unit="mm"),
   dict(k="marbles", label="Marbles at rim",   v=7,  min=0,  max=12,  step=1,   unit=""),
   dict(k="lines",   label="Spiral turns",     v=42, min=0,  max=80,  step=1,   unit="turns"),
   dict(k="linepitch", label="Drop per turn",  v=1.9, min=0.8, max=5.0, step=0.1, unit="mm"),
 ],
}

USES = {
    ".step": "CAD hand-off - solid B-rep for Fusion / SolidWorks / Rhino",
    ".stl": "Mesh - 3D print, mould master, wax pattern",
    ".glb": "Web / realtime - transmission, IOR 1.474, volume",
}
PARTS = {
    "_frit": "frit grains",
    "_marbles": "the clear marbles",
    "_cork": "the cork lid",
}


def files():
    """Everything sitting in out/, grouped by the piece it belongs to."""
    rows = []
    for name in sorted(os.listdir("out")) if os.path.isdir("out") else []:
        stem, ext = os.path.splitext(name)
        if ext not in USES:
            continue
        if stem.startswith("jar"):
            piece = "jar"
        elif stem.startswith("v-"):
            piece = "variant"
        else:
            piece = "hammer"
        use = USES[ext]
        for suffix, what in PARTS.items():
            if stem.endswith(suffix):
                use = "%s - %s" % (what[0].upper() + what[1:], ext.lstrip(".").upper())
        for w in WAYS:
            if stem.endswith(w):
                use = "%s, %s build" % (USES[ext], WAY_META[w]["name"].lower())
        rows.append(("out/" + name, piece, use))
    return rows


FILES = files()

def variants():
    """Re-rendered remodel requests. They are added alongside the originals,
    which are never replaced."""
    path = os.path.join(SITE, "variants.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


SPECS = {
    "hammer_flat": [["Overall height", "140", "mm"], ["Head", "68 &times; 42", "mm"],
               ["Stem OD", "14", "mm"], ["Bowl", "&empty;25", "mm"],
               ["Glass", "&asymp; 83", "g"], ["Marbles", "4", "clear"]],
    "hammer": [["Overall height", "140", "mm"], ["Head", "68 &times; 42", "mm"],
               ["Stem OD", "14", "mm"], ["Bowl", "&empty;25", "mm"],
               ["Glass", "&asymp; 83", "g"], ["Marbles", "4", "clear"]],
    "tip":    [["Overall length", "19", "mm"], ["Outside", "&empty;9", "mm"],
               ["Bore", "&empty;6.4", "mm, 1.3 wall"],
               ["Screen", "seven &empty;1.25", "holes"],
               ["Slot", "0.75 &times; 0.9", "at 68&deg;"],
               ["Glass", "&asymp; 1.4", "g, clear"]],
    "holder": [["Overall length", "90", "mm"], ["Bell", "&empty;23", "mm"],
               ["Grip cone", "&empty;6.4 &ndash; 15", "mm"],
               ["Mouthpiece", "&empty;9.6", "mm"],
               ["Glass", "&asymp; 20", "g"], ["Marbles", "3", "one side"]],
    "jar":    [["Glass height", "92", "mm"], ["Body", "&empty;44", "mm straight"],
               ["Mouth", "&empty;38", "mm"], ["Wall", "3", "mm"],
               ["Glass", "&asymp; 90", "g + cork"], ["Marbles", "7", "at the opening"]],
}


# ------------------------------------------------------------------ assets
def build_id():
    """A short stamp over everything the site serves. Any change moves it, which is
    what the ?v= on each asset rides on - browsers cache these paths hard."""
    h = hashlib.md5()
    for root in (os.path.join(SITE, "spin"), os.path.join(SITE, "video"),
                 os.path.join(SITE, "still"), "out"):
        for dirpath, _, names in os.walk(root):
            for n in sorted(names):
                f = os.path.join(dirpath, n)
                h.update(n.encode())
                h.update(str(os.path.getsize(f)).encode())
    for f in sorted(os.listdir("cad")):
        if f.endswith(".py"):
            h.update(open(os.path.join("cad", f), "rb").read())
    return h.hexdigest()[:8]


BUILD = None


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


def all_pieces():
    out = list(PIECES)
    for v in variants():
        if v["id"] not in out:
            out.append(v["id"])
    return out


def assets(inline):
    ref = data_uri if inline else (
        lambda p: os.path.relpath(p, SITE).replace("\\", "/") + "?v=" + BUILD)
    out = {}
    for pc in all_pieces():
        out[pc] = {}
        for w in WAYS:
            d = os.path.join(SITE, "spin", "%s_%s" % (pc, w))
            if not os.path.isdir(d):
                continue                      # a variant is usually rendered in one colourway
            names = [f for f in sorted(os.listdir(d)) if f.endswith(".webp")]
            from PIL import Image
            with Image.open(os.path.join(d, names[0])) as im:
                aspect = "%d/%d" % im.size          # the laid-down set is landscape
            rows = len(set(f.split("_")[0] for f in names)) if names[0].startswith("t") else 1
            out[pc][w] = {"frames": [ref(os.path.join(d, f)) for f in names],
                          "aspect": aspect, "rows": rows,
                          "cols": len(names) // max(rows, 1)}
    return out


def piece_meta():
    m = {k: dict(x) for k, x in PIECE_META.items()}
    for v in variants():
        m[v["id"]] = dict(name=v.get("label") or v["id"], code=v["id"].upper(),
                          note="variant of the " + PIECE_META[v["piece"]]["name"].lower(),
                          variant_of=v["piece"], dims=v.get("dims", {}))
    return m


def base_dims():
    b = dict(BASE)
    for v in variants():
        rows = []
        for row in BASE[v["piece"]]:
            r = dict(row)
            if row["k"] in v.get("dims", {}):
                r["v"] = v["dims"][row["k"]]
            rows.append(r)
        b[v["id"]] = rows
    return b


def piece_specs():
    sp = dict(SPECS)
    for v in variants():
        rows = [list(r) for r in SPECS[v["piece"]]]
        d = v.get("dims", {})
        for r in rows:
            key = {"Overall height": "height", "Glass height": "height",
                   "Stem OD": "stemod", "Mouth": "mouthid", "Wall": "wall",
                   "Marbles": "marbles", "Bowl": "bowlid"}.get(r[0])
            if key and key in d:
                r[1] = ("&empty;%g" % d[key]) if r[0] in ("Mouth", "Bowl") else ("%g" % d[key])
            if r[0] == "Head":
                r[1] = "%g &times; %g" % (d.get("headlen", 68), d.get("headsec", 42))
            if r[0] == "Glass":
                r[1] = "&mdash;"                      # recompute on the next full build
        sp[v["id"]] = rows
    return sp


def sizes():
    s = {}
    for path, _, _ in FILES:
        s[path] = ("%.1f MB" % (os.path.getsize(path) / 1e6)) if os.path.exists(path) else "-"
    for pc in PIECES:
        for w in WAYS:
            p = os.path.join(SITE, "video", "%s_%s.mp4" % (pc, w))
            if os.path.exists(p):
                s["video/%s_%s.mp4" % (pc, w)] = "%.1f MB" % (os.path.getsize(p) / 1e6)
    for name, _ in SPECFILES:
        p = os.path.join(SITE, name)
        s[name] = ("%.1f MB" % (os.path.getsize(p) / 1e6)) if os.path.exists(p) else "-"
    return s


CSS = r"""
:root{
  --ground:#EEF1F0; --panel:#FFFFFF; --sweep-a:#F7F8F8; --sweep-b:#DCE1E0;
  --ink:#111A18; --ink-2:#41504C; --ink-3:#6E7E79;
  --rule:#C7D0CD; --rule-soft:#DFE5E3;
  --accent:#0F7A66; --accent-soft:#DCEFEA;
  --flag:#9C5A20; --flag-soft:#F6ECE0;
  --font-display:Bahnschrift,"DIN Alternate","Arial Narrow",ui-sans-serif,sans-serif;
  --font-mono:ui-monospace,"Cascadia Mono","SFMono-Regular",Consolas,"Liberation Mono",monospace;
  --font-body:"Segoe UI",system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
}
@media (prefers-color-scheme:dark){
  :root{
    --ground:#0B100F; --panel:#131A18; --sweep-a:#1B2321; --sweep-b:#0D1312;
    --ink:#E6EDEA; --ink-2:#A9B7B2; --ink-3:#7C8C87;
    --rule:#26312E; --rule-soft:#1C2523;
    --accent:#41C9A9; --accent-soft:#12302A;
    --flag:#D79A5C; --flag-soft:#2A2117;
  }
}
:root[data-theme="dark"]{
  --ground:#0B100F; --panel:#131A18; --sweep-a:#1B2321; --sweep-b:#0D1312;
  --ink:#E6EDEA; --ink-2:#A9B7B2; --ink-3:#7C8C87;
  --rule:#26312E; --rule-soft:#1C2523;
  --accent:#41C9A9; --accent-soft:#12302A;
  --flag:#D79A5C; --flag-soft:#2A2117;
}
:root[data-theme="light"]{
  --ground:#EEF1F0; --panel:#FFFFFF; --sweep-a:#F7F8F8; --sweep-b:#DCE1E0;
  --ink:#111A18; --ink-2:#41504C; --ink-3:#6E7E79;
  --rule:#C7D0CD; --rule-soft:#DFE5E3;
  --accent:#0F7A66; --accent-soft:#DCEFEA;
  --flag:#9C5A20; --flag-soft:#F6ECE0;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--font-body);
  font-size:16px;line-height:1.62;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px}
h1,h2,h3{margin:0;text-wrap:balance}
p{margin:0}
a{color:var(--accent)}
button{font:inherit;color:inherit}

.masthead{border-bottom:1px solid var(--rule);background:var(--panel)}
.masthead .wrap{display:flex;align-items:center;gap:22px;flex-wrap:wrap;
  padding-top:13px;padding-bottom:12px}
.marque{font-family:var(--font-display);font-stretch:87.5%;font-weight:700;font-size:18px;
  letter-spacing:.06em;text-transform:uppercase;text-decoration:none;color:var(--ink)}
.marque span{color:var(--ink-3);font-weight:400}
nav{display:flex;gap:16px;margin-left:auto;font-family:var(--font-mono);font-size:11.5px;
  letter-spacing:.12em;text-transform:uppercase}
nav a{color:var(--ink-3);text-decoration:none;padding-bottom:2px;border-bottom:1px solid transparent}
nav a:hover{color:var(--ink)}
nav a[aria-current="page"]{color:var(--accent);border-bottom-color:var(--accent)}
nav a.dl{color:var(--ink);border:1px solid var(--line);border-radius:999px;
  padding:5px 11px;white-space:nowrap}
nav a.dl:hover{border-color:var(--accent);color:var(--accent)}
nav a.dl span{color:var(--ink-3);margin-left:5px}
@media (max-width:640px){nav a.dl span{display:none}}

.hero{padding:40px 0 6px}
.eyebrow{font-family:var(--font-mono);font-size:11.5px;letter-spacing:.19em;
  text-transform:uppercase;color:var(--ink-3)}
.title{font-family:var(--font-display);font-stretch:87.5%;font-weight:700;
  font-size:clamp(38px,7.4vw,74px);line-height:.95;letter-spacing:-.005em;
  text-transform:uppercase;margin:10px 0 0}
.title em{font-style:normal;color:var(--accent)}
.deck{margin-top:16px;max-width:62ch;color:var(--ink-2);font-size:17px}

section{padding:52px 0}
.sechead{display:flex;align-items:baseline;gap:14px;border-top:1px solid var(--rule);
  padding-top:12px;margin-bottom:24px}
.sechead h2{font-family:var(--font-display);font-stretch:87.5%;font-weight:700;font-size:23px;
  letter-spacing:.04em;text-transform:uppercase}
.sechead .n{font-family:var(--font-mono);font-size:11.5px;letter-spacing:.14em;color:var(--ink-3)}
.sechead .note{margin-left:auto;font-family:var(--font-mono);font-size:11.5px;
  letter-spacing:.08em;color:var(--ink-3);text-transform:uppercase}

.stagewrap{margin-top:20px;display:grid;grid-template-columns:minmax(0,620px) 1fr;
  gap:32px;align-items:start}
.sidecol{display:flex;flex-direction:column;gap:20px;padding-top:2px}
.sidecol h3{font-family:var(--font-mono);font-size:11px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--ink-3);margin-bottom:9px}
.stage{position:relative;background:
    radial-gradient(120% 80% at 50% 12%,var(--sweep-a) 0%,var(--sweep-b) 100%);
  border:1px solid var(--rule);overflow:hidden;touch-action:none;cursor:grab;
  user-select:none;--plate-ink:#5C6B66}
.stage.dragging{cursor:grabbing}
.stage .frames{position:relative;width:100%;aspect-ratio:520/684}
.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0;
  pointer-events:none;-webkit-user-drag:none}
.stage img.on{opacity:1}
.stage:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.hint{position:absolute;left:13px;bottom:11px;font-family:var(--font-mono);font-size:11px;
  letter-spacing:.12em;text-transform:uppercase;color:var(--plate-ink)}
.readout{position:absolute;right:13px;bottom:11px;font-family:var(--font-mono);font-size:11px;
  letter-spacing:.12em;color:var(--plate-ink);font-variant-numeric:tabular-nums}
@media (prefers-color-scheme:dark){
  .stage{border-color:#3A4744;box-shadow:0 0 0 1px rgba(255,255,255,.04),0 18px 46px rgba(0,0,0,.55)}
  .stage .frames{filter:brightness(.95) contrast(1.02)}
}
:root[data-theme="dark"] .stage{border-color:#3A4744;
  box-shadow:0 0 0 1px rgba(255,255,255,.04),0 18px 46px rgba(0,0,0,.55)}
:root[data-theme="dark"] .stage .frames{filter:brightness(.95) contrast(1.02)}
:root[data-theme="light"] .stage{border-color:var(--rule);box-shadow:none}
:root[data-theme="light"] .stage .frames{filter:none}

.controls{display:flex;align-items:center;gap:8px}
.controls .step{padding:9px 13px;line-height:1}
.controls .roll{min-width:96px}
.tiltnote{font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--ink-3)}
.controls input[type="range"]{flex:1;min-width:80px;margin:0;accent-color:var(--accent);
  background:transparent}
.pieces{display:flex;gap:8px;flex-wrap:wrap;margin-top:24px}
.piece{padding:9px 16px;background:var(--panel);border:1px solid var(--rule);cursor:pointer;
  font-family:var(--font-display);font-stretch:87.5%;font-size:15px;letter-spacing:.05em;
  text-transform:uppercase;color:var(--ink-2)}
.piece:hover{color:var(--ink);border-color:var(--ink-3)}
.piece[aria-pressed="true"]{color:var(--ink);border-color:var(--accent);
  box-shadow:inset 0 0 0 1px var(--accent)}
.ways{display:flex;flex-direction:column;gap:7px}
.way{display:flex;align-items:center;gap:9px;padding:8px 13px 8px 9px;background:var(--panel);
  border:1px solid var(--rule);cursor:pointer;color:var(--ink-2);text-align:left;
  font-family:var(--font-mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase}
.way:hover{border-color:var(--ink-3);color:var(--ink)}
.way[aria-pressed="true"]{border-color:var(--accent);color:var(--ink);
  box-shadow:inset 0 0 0 1px var(--accent)}
.way .dot{width:16px;height:16px;border-radius:50%;flex:0 0 auto}

.facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;
  border:1px solid var(--rule);background:var(--rule-soft)}
.fact{padding:13px 15px;background:var(--panel)}
.fact dt{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--ink-3)}
.fact dd{margin:5px 0 0;font-family:var(--font-mono);font-size:20px;font-weight:600;
  font-variant-numeric:tabular-nums;color:var(--ink)}
.fact dd small{font-size:12px;font-weight:400;color:var(--ink-3);letter-spacing:.04em}

.remodel{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.15fr);gap:1px;
  background:var(--rule-soft);border:1px solid var(--rule)}
.remodel > div{background:var(--panel);padding:22px 24px}
.sliders{display:flex;flex-direction:column;gap:13px}
.slider{display:grid;grid-template-columns:1fr auto;gap:3px 12px;align-items:center}
.slider label{font-family:var(--font-mono);font-size:11px;letter-spacing:.11em;
  text-transform:uppercase;color:var(--ink-3)}
.slider output{font-family:var(--font-mono);font-size:13px;font-variant-numeric:tabular-nums;
  color:var(--ink)}
.slider output.changed{color:var(--accent);font-weight:600}
.slider input{grid-column:1/-1;width:100%;accent-color:var(--accent)}
.drawing{background:radial-gradient(120% 80% at 50% 10%,var(--sweep-a) 0%,var(--sweep-b) 100%);
  border:1px solid var(--rule-soft);aspect-ratio:1/1;width:100%;display:block}
.legend{display:flex;gap:18px;margin-top:10px;font-family:var(--font-mono);font-size:10.5px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);flex-wrap:wrap}
.legend b{font-weight:400;color:var(--accent)}
label.field{display:block;margin-top:14px;font-family:var(--font-mono);font-size:11px;
  letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3)}
input[type="text"]{width:100%;margin-top:7px;padding:10px 13px;background:var(--ground);
  border:1px solid var(--rule);color:var(--ink);font-family:var(--font-body);font-size:15px}
textarea{width:100%;min-height:92px;margin-top:7px;padding:11px 13px;background:var(--ground);
  border:1px solid var(--rule);color:var(--ink);font-family:var(--font-body);font-size:15px;
  resize:vertical}
textarea:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.btn{padding:9px 15px;background:var(--panel);border:1px solid var(--rule);cursor:pointer;
  font-family:var(--font-mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;
  color:var(--ink-2)}
.btn:hover{border-color:var(--ink-3);color:var(--ink)}
a.btn{text-decoration:none;display:inline-block}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary:hover{filter:brightness(1.08)}
.fine{margin-top:12px;font-size:13.5px;color:var(--ink-3);max-width:60ch}
.log{margin-top:16px;border-top:1px dashed var(--rule);padding-top:12px;font-family:var(--font-mono);
  font-size:11.5px;color:var(--ink-3);display:flex;flex-direction:column;gap:6px}
.log b{color:var(--ink-2);font-weight:600}

.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:30px}
.cols p{color:var(--ink-2);max-width:64ch}
.cols p + p{margin-top:14px}
.bench{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1px;
  background:var(--rule-soft);border:1px solid var(--rule)}
.step{background:var(--panel);padding:20px 22px}
.step h3{font-family:var(--font-mono);font-size:12px;letter-spacing:.13em;text-transform:uppercase;
  color:var(--accent);display:flex;gap:10px;align-items:baseline}
.step h3 b{color:var(--ink-3);font-weight:400}
.step p{margin-top:9px;color:var(--ink-2);font-size:15px}
.step .spec{margin-top:11px;font-family:var(--font-mono);font-size:11.5px;letter-spacing:.05em;
  color:var(--ink-3);border-top:1px dashed var(--rule);padding-top:9px}
.tablewrap{overflow-x:auto;border:1px solid var(--rule);background:var(--panel)}
table{border-collapse:collapse;width:100%;min-width:620px;font-size:15px}
th,td{text-align:left;padding:11px 16px;border-bottom:1px solid var(--rule-soft)}
thead th{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--ink-3);font-weight:500;border-bottom:1px solid var(--rule);white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td.num{font-family:var(--font-mono);font-variant-numeric:tabular-nums;white-space:nowrap}
tr.group td{background:var(--accent-soft);font-family:var(--font-mono);font-size:10.5px;
  letter-spacing:.14em;text-transform:uppercase;color:var(--accent);padding:8px 16px}
.src{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink-3);white-space:nowrap}
.src.inferred{color:var(--flag)}
.files td:first-child{font-family:var(--font-mono);font-size:13px}
.files .use{color:var(--ink-2);font-size:14.5px}
.callout{margin-top:22px;border:1px solid var(--flag);background:var(--flag-soft);padding:16px 20px;
  display:flex;gap:16px;align-items:flex-start}
.callout .tag{font-family:var(--font-mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--flag);white-space:nowrap;padding-top:2px}
.callout p{color:var(--ink-2);font-size:15px;max-width:70ch}
figure{margin:0}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);background:#fff}
figcaption{margin-top:10px;font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;
  color:var(--ink-3);text-transform:uppercase}
pre{margin:20px 0 0;background:var(--panel);border:1px solid var(--rule);padding:16px 18px;
  overflow-x:auto;font-family:var(--font-mono);font-size:12.5px;line-height:1.75;color:var(--ink-2)}
pre b{color:var(--accent);font-weight:600}
footer{border-top:1px solid var(--rule);padding:24px 0 56px;color:var(--ink-3);
  font-family:var(--font-mono);font-size:11.5px;letter-spacing:.07em}
footer .wrap{display:flex;gap:18px;flex-wrap:wrap}
footer .r{margin-left:auto}
@media (max-width:900px){.remodel{grid-template-columns:minmax(0,1fr)}}
@media (max-width:860px){
  .stagewrap{grid-template-columns:minmax(0,1fr)}
  .stagecol{max-width:620px;width:100%;margin:0 auto}
}
@media (max-width:640px){
  .wrap{padding:0 18px}
  section{padding:38px 0}
  nav{gap:12px}
  .stagecol{margin:0 -18px;max-width:none}
  .stage{border-left:0;border-right:0}
  .controls{padding:0 18px}
}
"""


def shell(title, body, script="", nav="index", standalone=False):
    links = [("index.html", "Mockups", "index"), ("survey.html", "Survey", "survey"),
             ("downloads.html", "Downloads", "downloads")]
    # the spec sheet and the whole hand-off pack hang off every page, not just Downloads
    # the two newer pieces have their own sheets rather than a page each, so they hang
    # off the masthead where they can be found from anywhere
    grabs = ('<a class="dl" href="JBD_Joint_Holder.pdf" target="_blank">Joint holder'
             ' <span>PDF</span></a>'
             '<a class="dl" href="JBD_Glass_Tip.pdf" target="_blank">Glass tip'
             ' <span>PDF</span></a>'
             '<a class="dl" href="JBD_Clearboy_spec.pdf" download>Spec sheet'
             ' <span>PDF</span></a>'
             '<a class="dl" href="JBD_Clearboy_pack.zip" download>All specs'
             ' <span>ZIP</span></a>')
    navhtml = "" if standalone else "<nav>" + "".join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if k == nav else "", t)
        for (h, t, k) in links) + grabs + "</nav>"
    marque = ('<span class="marque">' if standalone else '<a class="marque" href="index.html">') + \
             'Jerome Baker Designs <span>/ New York</span>' + \
             ('</span>' if standalone else '</a>')
    return """<title>%s</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
<style>%s</style>
<header class="masthead"><div class="wrap">
  %s
  %s
</div></header>
<main><div class="wrap">
%s
</div></main>
<footer><div class="wrap">
  <span>Jerome Baker Designs &middot; Clearboy programme &middot; build __BUILD__</span>
  <span class="r">Renders are proposals &mdash; the original piece stays the reference</span>
</div></footer>
<script>
%s
</script>
""" % (title, CSS, marque, navhtml, body, script)


INDEX_BODY = r"""
  <div class="hero">
    <div class="eyebrow">Fumed glass &middot; frit-rolled &middot; clear marbles</div>
    <h1 class="title">Mockups <em>Rev B</em></h1>
    <p class="deck">Two pieces, two colourways, spun on their own axis from a broadside start.
      Both are built off the measured survey of the original hand-blown hammer. The glass is
      rendered dense on purpose &mdash; these read as colour, not as an X-ray of the wall.</p>
  </div>

  <div class="pieces" id="pieces" role="group" aria-label="Piece"></div>

  <div class="stagewrap">
    <div class="stagecol">
      <div class="stage" id="stage" tabindex="0" role="slider"
           aria-label="Rotate the piece" aria-valuemin="0" aria-valuemax="359"
           aria-valuenow="0" aria-valuetext="0 degrees">
        <div class="frames" id="frames"></div>
        <div class="hint" id="hint">Drag to spin</div>
        <div class="readout" id="readout">000&deg;</div>
      </div>
      <div class="controls">
        <button class="btn step" id="back" type="button" aria-label="Roll back one step">&#9664;</button>
        <button class="btn primary roll" id="play" type="button">Roll</button>
        <button class="btn step" id="fwd" type="button" aria-label="Roll forward one step">&#9654;</button>
        <input id="scrub" type="range" min="0" max="35" value="0" step="1"
               aria-label="Rotation">
        <button class="btn step" id="png2" type="button">Save PNG</button>
      </div>
      <div class="controls" id="tiltrow" hidden>
        <button class="btn step" id="stand" type="button">&#9650; Stand up</button>
        <button class="btn step" id="lay" type="button">&#9660; Lay down</button>
        <span class="tiltnote" id="tiltnote">standing</span>
        <button class="btn step" id="png" type="button" style="margin-left:auto">Save PNG</button>
      </div>
    </div>
    <div class="sidecol">
      <div><h3>Colourway</h3><div class="ways" id="ways" role="group" aria-label="Colourway"></div></div>
      <div><h3 id="specs-head">Build</h3><dl class="facts" id="facts"></dl></div>
    </div>
  </div>

  <section>
    <div class="sechead"><span class="n">01</span><h2>Remodel it</h2>
      <span class="note">The original is never overwritten</span></div>
    <div class="remodel">
      <div>
        <div class="sliders" id="sliders"></div>
        <div class="actions"><button class="btn" id="reset" type="button">Reset to original</button></div>
      </div>
      <div>
        <svg class="drawing" id="drawing" viewBox="0 0 400 400"
             role="img" aria-label="Proposed profile drawn over the original"></svg>
        <div class="legend">
          <span><b>&#9473;</b> proposal</span>
          <span>&middot;&middot;&middot; original</span>
          <span id="deltaline">no changes yet</span>
        </div>
        <label class="field" for="vname">Name this variant</label>
        <input id="vname" type="text" maxlength="40" placeholder="Fat lobe, short stem">
        <label class="field" for="notes">What should change</label>
        <textarea id="notes" placeholder="Shorter stem, fatter lobe, marbles only on the carb side, colder teal, frit further down the body..."></textarea>
        <div class="actions">
          <button class="btn primary" id="render" type="button">Re-render it</button>
          <button class="btn" id="copy" type="button">Copy spec</button>
          <button class="btn" id="dl" type="button">Download request</button>
          <a class="btn" id="mail" href="#">Email it</a>
          <button class="btn" id="save" type="button">Keep on this device</button>
          <button class="btn" id="spec" type="button">Download spec</button>
        </div>
        <p class="fine" id="renderstate" hidden></p>
        <p class="fine">Re-render sends it straight to the build. It takes a couple of
          minutes; reload this page when it lands and the variant is in the piece menu under
          the name you gave it. Copy or download drops the exact request &mdash; numbers, notes and
          the one-line render command &mdash; wherever you want it. Email works too where the
          browser allows it. No accounts, no sign-in.</p>
        <p class="fine" hidden>Sending mails the numbers straight through &mdash; no accounts, no
          sign-in. The re-render comes back under the name you gave it and joins the piece
          menu at the top of this page; the original build is never replaced.</p>
        <div class="log" id="log"></div>
      </div>
    </div>
  </section>
"""

SURVEY_BODY = r"""
  <div class="hero">
    <div class="eyebrow">Hand-blown original &rarr; measured &rarr; parametric solid</div>
    <h1 class="title">The <em>Survey</em></h1>
    <p class="deck">Ten photographs with a stainless rule in frame, resolved into a dimensioned
      survey and rebuilt as a watertight CAD solid. Every mockup is downstream of these numbers.</p>
  </div>

  <section>
    <div class="sechead"><span class="n">01</span><h2>How this piece gets made</h2>
      <span class="note">Bench notes</span></div>
    <div class="bench">
      <div class="step">
        <h3>Stock <b>&mdash; borosilicate 3.3</b></h3>
        <p>Everything here is COE&nbsp;33 boro: 3.3&nbsp;&times;&nbsp;10<sup>&minus;6</sup>/K
        expansion, which is what lets a piece take a lighter and a cold sink without checking.
        The original stem came straight off stock tube &mdash; 11&nbsp;OD, 8&nbsp;ID. The mockups
        run it out to &empty;14 so the enamel label has something to sit on.</p>
        <div class="spec">density 2.23 g/cm&sup3; &middot; working &asymp; 1250&nbsp;&deg;C &middot; softening &asymp; 820&nbsp;&deg;C</div>
      </div>
      <div class="step">
        <h3>Head <b>&mdash; blown and shaped</b></h3>
        <p>The chamber starts as a length of heavy tube, closed at one end, heated to a gather and
        blown out against the shape the maker wants. Marvered, waisted, worked until the lobe reads
        full and the bowl end tapers. Hand-shaped means slightly oval, always.</p>
        <div class="spec">42 &times; 37 section &middot; 68 long &middot; wall &asymp; 3 mm (inferred)</div>
      </div>
      <div class="step">
        <h3>Bowl <b>&mdash; pushed in from the rim</b></h3>
        <p>The funnel is pushed into the hot chamber wall rather than added on &mdash; the technique
        the Eugene scene traces back to Bob&nbsp;Snodgrass, and the reason a bowl like this has no
        seam. It necks from &empty;25 at the rim down to a &empty;5 throat.</p>
        <div class="spec">&empty;25 rim &rarr; &empty;5 throat &middot; 18&ndash;20 deep</div>
      </div>
      <div class="step">
        <h3>Frit <b>&mdash; rolled, not painted</b></h3>
        <p>The hot end is rolled through crushed colour on the marver so the grains stick and melt
        in, leaving a granular band that catches light differently from the body. The marbles go on
        over it, pressed in while everything is still soft.</p>
        <div class="spec">band &asymp; 25 mm &middot; grains 0.6&ndash;1.3 mm &middot; 4 marbles on the hammer, 7 at the jar rim</div>
      </div>
      <div class="step">
        <h3>Fume <b>&mdash; silver and gold vapour</b></h3>
        <p>Silver reads blue-violet, gold reads pink-amber. Both go on as a coat a few atoms thick,
        which is why the colour moves with the angle you hold it at &mdash; and why it keeps moving
        with use. These renders are the day-one state, not year two.</p>
        <div class="spec">silver &rarr; blue / violet &middot; gold &rarr; pink / amber</div>
      </div>
      <div class="step">
        <h3>Anneal <b>&mdash; the part that decides</b></h3>
        <p>Off the torch it goes straight into the kiln: soak near the annealing point to let the
        stress out, then a slow ramp down through the strain point. Rush it and a piece with a
        3&nbsp;mm chamber wall against a 7&nbsp;mm foot cracks weeks later, at rest.</p>
        <div class="spec">anneal &asymp; 560&nbsp;&deg;C &middot; strain &asymp; 518&nbsp;&deg;C &middot; slow ramp</div>
      </div>
    </div>
  </section>

  <section>
    <div class="sechead"><span class="n">02</span><h2>Measured schedule</h2>
      <span class="note">mm &middot; &plusmn;2&ndash;3 unless noted</span></div>
    <div class="tablewrap"><table>
      <thead><tr><th>Feature</th><th>Original</th><th>Source</th><th>Note</th></tr></thead>
      <tbody>
        <tr class="group"><td colspan="4">Overall</td></tr>
        <tr><td>Height, standing on the foot</td><td class="num">140</td>
            <td class="src">Rule-referenced</td><td>5.51 in</td></tr>
        <tr><td>Head (chamber) length</td><td class="num">68</td>
            <td class="src">Range 62&ndash;71</td><td>Varies by view &mdash; hand-shaped</td></tr>
        <tr><td>Head max section</td><td class="num">42 &times; 37</td>
            <td class="src">Measured</td><td>Oval, not round</td></tr>
        <tr class="group"><td colspan="4">Stem &amp; foot</td></tr>
        <tr><td>Stem tube OD</td><td class="num">&empty;11</td>
            <td class="src">Measured</td><td>Mockups run &empty;14 for the label</td></tr>
        <tr><td>Stem bore ID</td><td class="num">&empty;8</td>
            <td class="src">Measured</td><td>1.5 mm wall on the original</td></tr>
        <tr><td>Exposed stem length</td><td class="num">88</td>
            <td class="src">Measured</td><td>Collar to foot</td></tr>
        <tr><td>Foot / mouthpiece disc</td><td class="num">&empty;24.5 &times; 7</td>
            <td class="src">Measured</td><td>Flared and flattened</td></tr>
        <tr class="group"><td colspan="4">Bowl &amp; carb</td></tr>
        <tr><td>Bowl opening at rim</td><td class="num">&empty;25</td><td class="src">Measured</td><td></td></tr>
        <tr><td>Bowl throat / drop hole</td><td class="num">&empty;5</td><td class="src">Measured</td><td></td></tr>
        <tr><td>Bowl depth to throat</td><td class="num">18&ndash;20</td><td class="src">Measured</td><td></td></tr>
        <tr><td>Carb hole &middot; boss &middot; position</td><td class="num">&empty;3.5 &middot; &empty;11 &middot; 14</td>
            <td class="src">Measured</td><td>14 below the rim</td></tr>
        <tr class="group"><td colspan="4">Wall</td></tr>
        <tr><td>Chamber wall</td><td class="num">&asymp; 3</td>
            <td class="src inferred">Inferred</td><td>Not measurable from photos</td></tr>
        <tr><td>Rim thickness</td><td class="num">4&ndash;5</td>
            <td class="src inferred">Inferred</td><td>Read off the rim highlight</td></tr>
      </tbody>
    </table></div>
    <div class="callout"><span class="tag">Before tooling</span>
      <p>Wall thickness is the one group that was never measured &mdash; it was read off highlights
      and reasoned from the form. Two caliper readings, on the rim and on the stem OD, lock the
      entire model. Everything downstream of those numbers (mass, volume, glass cost, print
      scaling) moves if they come back different.</p></div>
  </section>

  <section>
    <div class="sechead"><span class="n">03</span><h2>The survey sheet</h2>
      <span class="note">Five set-ups &middot; four cross-checks</span></div>
    <figure>
      <img src="dims.jpg?v=__BUILD__" alt="Five-view dimensional survey of the Clearboy hammer with a measured schedule">
      <figcaption>Scale set from the stainless rule in IMG_5855&ndash;5859, resolved to &plusmn;0.5 px/mm and corrected for stand-off parallax</figcaption>
    </figure>
  </section>
"""

DOWNLOADS_BODY = r"""
  <div class="hero">
    <div class="eyebrow">Everything in the package</div>
    <h1 class="title">Down<em>loads</em></h1>
    <p class="deck">CAD, meshes, web-ready glass models and the turntable loops. STEP is what you
      send a shop; GLB is what you drop into a web page or a deck.</p>
  </div>

  <section>
    <div class="sechead"><span class="n">01</span><h2>Spec sheet</h2>
      <span class="note">What goes to the shop</span></div>
    <div class="tablewrap"><table class="files">
      <thead><tr><th>File</th><th>Size</th><th>What it's for</th></tr></thead>
      <tbody id="specrows"></tbody>
    </table></div>
  </section>

  <section>
    <div class="sechead"><span class="n">02</span><h2>Geometry</h2>
      <span class="note">STEP &middot; STL &middot; GLB</span></div>
    <div class="tablewrap"><table class="files">
      <thead><tr><th>File</th><th>Piece</th><th>Size</th><th>What it's for</th></tr></thead>
      <tbody id="filerows"></tbody>
    </table></div>
  </section>

  <section>
    <div class="sechead"><span class="n">03</span><h2>Stills</h2>
      <span class="note">Full resolution, straight off the renderer</span></div>
    <div class="tablewrap"><table class="files">
      <thead><tr><th>File</th><th>Piece &middot; colourway</th></tr></thead>
      <tbody id="stillrows"></tbody>
    </table></div>
  </section>

  <section>
    <div class="sechead"><span class="n">04</span><h2>Turntable loops</h2>
      <span class="note">72 frames &middot; 24 fps &middot; seamless</span></div>
    <div class="tablewrap"><table class="files">
      <thead><tr><th>File</th><th>Size</th><th>Piece &middot; colourway</th></tr></thead>
      <tbody id="videorows"></tbody>
    </table></div>
  </section>

  <section>
    <div class="sechead"><span class="n">05</span><h2>Rebuild from source</h2>
      <span class="note">Python 3.12</span></div>
    <pre>
<b># CadQuery has no 3.13/3.14 wheels yet</b>
py install 3.12
python3.12 -m venv cadenv && ./cadenv/Scripts/python -m pip install -r requirements.txt

./cadenv/Scripts/python cad/model.py out      <b># hammer solid -> STEP + STL</b>
./cadenv/Scripts/python cad/frit.py out       <b># frit grains + marbles</b>
./cadenv/Scripts/python cad/jar.py out        <b># jar, its frit and its marbles</b>
./cadenv/Scripts/python cad/glb_export.py     <b># GLB with glass materials</b>
./cadenv/Scripts/python cad/turntable.py      <b># 72-frame turntables</b>
./cadenv/Scripts/python cad/encode.py         <b># mp4 loops + spinner frames</b>
./cadenv/Scripts/python cad/build_web.py      <b># this site</b>
</pre>
  </section>
"""

INDEX_JS = r"""
const ASSETS = __ASSETS__, META = __META__, BASE = __BASE__, SPECS = __SPECS__;
const CONTACT = "__CONTACT__", REPO = "__REPO__";
const RENDER_URL = "__RENDER_URL__", RENDER_KEY = "__RENDER_KEY__";
const STOCK = __STOCK__, BUILD = "__BUILD__";
const SITE = "https://zelidav.github.io/jbd-clearboy/";
const PIECES = Object.keys(META.pieces), WAYS = Object.keys(META.ways);
const MID = "·", DEG = "°", ARROW = "→";

const framesEl = document.getElementById("frames"), stage = document.getElementById("stage");
const readout = document.getElementById("readout");
let piece = PIECES[0], way = WAYS[0], idx = 0, N = 0, row = 0, ROWS = 1;
const layers = {};

function mount(pc, w){
  const box = document.createElement("div");
  box.style.cssText = "position:absolute;inset:0;display:none";
  const imgs = ASSETS[pc][w].frames.map((src, i) => {
    const im = new Image();
    im.src = src; im.alt = ""; im.decoding = "async"; im.draggable = false;
    im.loading = i < 4 ? "eager" : "lazy";
    box.appendChild(im); return im;
  });
  framesEl.appendChild(box);
  layers[pc + "/" + w] = {box: box, imgs: imgs};
  N = imgs.length;
}
PIECES.forEach(function(pc){
  WAYS.forEach(function(w){ if(ASSETS[pc] && ASSETS[pc][w]) mount(pc, w); });
});
function waysFor(pc){ return WAYS.filter(function(w){ return ASSETS[pc] && ASSETS[pc][w]; }); }

function show(i, r){
  idx = ((i % N) + N) % N;
  if(r !== undefined) row = Math.max(0, Math.min(ROWS - 1, r));
  const active = row * N + idx;
  if(typeof paintTilt === "function") paintTilt();
  layers[piece + "/" + way].imgs.forEach(function(im, k){ im.classList.toggle("on", k === active); });
  const deg = Math.round(idx * 360 / N);
  readout.textContent = String(deg).padStart(3, "0") + DEG;
  stage.setAttribute("aria-valuenow", deg);
  stage.setAttribute("aria-valuetext", deg + " degrees");
}

function select(pc, w){
  const avail = waysFor(pc);
  if(avail.indexOf(w) < 0) w = avail[0];
  piece = pc; way = w;
  const a = ASSETS[pc][w];
  ROWS = a.rows || 1;
  N = a.cols || a.frames.length;
  row = 0;
  Object.keys(layers).forEach(function(k){ layers[k].box.style.display = "none"; });
  layers[pc + "/" + w].box.style.display = "block";
  framesEl.style.aspectRatio = a.aspect || "520/684";
  document.getElementById("hint").textContent =
    ROWS > 1 ? "Drag \u2194 to spin, \u2195 to tip it over" : "Drag to spin";
  document.getElementById("tiltrow").hidden = ROWS < 2;
  document.getElementById("png").hidden = ROWS < 2;
  document.getElementById("png2").hidden = ROWS >= 2;
  paintTilt();
  document.querySelectorAll(".piece").forEach(function(b){
    b.setAttribute("aria-pressed", String(b.dataset.k === pc)); });
  document.querySelectorAll(".way").forEach(function(b){
    const ok = avail.indexOf(b.dataset.k) >= 0;
    b.disabled = !ok;
    b.style.opacity = ok ? "1" : ".4";
    b.setAttribute("aria-pressed", String(b.dataset.k === w)); });
  document.getElementById("specs-head").textContent = META.pieces[pc].name;
  document.getElementById("facts").innerHTML = SPECS[pc].map(function(f){
    return '<div class="fact"><dt>' + f[0] + '</dt><dd>' + f[1] +
           '<small> ' + f[2] + '</small></dd></div>'; }).join("");
  buildSliders();
  show(idx);
}

const piecesEl = document.getElementById("pieces"), waysEl = document.getElementById("ways");
PIECES.forEach(function(pc){
  const b = document.createElement("button");
  b.className = "piece"; b.type = "button"; b.dataset.k = pc;
  b.setAttribute("aria-pressed", "false");
  b.textContent = META.pieces[pc].name;
  b.onclick = function(){ stopSpin(); select(pc, way); };
  piecesEl.appendChild(b);
});
WAYS.forEach(function(w){
  const m = META.ways[w];
  const b = document.createElement("button");
  b.className = "way"; b.type = "button"; b.dataset.k = w;
  b.setAttribute("aria-pressed", "false");
  b.innerHTML = '<span class="dot" style="background:' + m.dot + ';box-shadow:0 0 0 2px ' +
    m.ring + ' inset,inset -3px -3px 6px rgba(0,0,0,.22)"></span>' + m.name + ' ' + MID + ' ' + m.sub;
  b.onclick = function(){ stopSpin(); select(piece, w); };
  waysEl.appendChild(b);
});

const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
let timer = null, last = 0;
function tick(t){ if(t - last > 90){ show(idx + 1); last = t; } timer = requestAnimationFrame(tick); }
function stopSpin(){
  if(timer){ cancelAnimationFrame(timer); timer = null; }
  const b = document.getElementById("play");
  if(b) b.textContent = "Roll";
}
function startSpin(){
  if(timer) return;
  last = 0; timer = requestAnimationFrame(tick);
  document.getElementById("play").textContent = "Pause";
}
document.getElementById("play").onclick = function(){ timer ? stopSpin() : startSpin(); };
document.getElementById("back").onclick = function(){ stopSpin(); show(idx - 1); };
document.getElementById("fwd").onclick = function(){ stopSpin(); show(idx + 1); };
document.getElementById("scrub").addEventListener("input", function(e){
  stopSpin(); show(parseInt(e.target.value, 10));
});
function savePng(){
  const img = layers[piece + "/" + way].imgs[row * N + idx];
  const c = document.createElement("canvas");
  c.width = img.naturalWidth || 520;
  c.height = img.naturalHeight || 684;
  c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
  const name = piece + "_" + way + "_" +
    String(Math.round(idx * 360 / N)).padStart(3, "0") + "deg.png";
  c.toBlob(function(b){
    const a = document.createElement("a");
    a.href = URL.createObjectURL(b);
    a.download = name;
    a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); }, 3000);
  });
}
document.getElementById("png").onclick = savePng;
document.getElementById("png2").onclick = savePng;

function paintTilt(){
  const n = document.getElementById("tiltnote");
  if(!n || ROWS < 2) return;
  n.textContent = row === 0 ? "standing"
                : row === ROWS - 1 ? "laid down"
                : "tipped " + Math.round(row * 90 / (ROWS - 1)) + "\u00B0";
  document.getElementById("stand").disabled = row === 0;
  document.getElementById("lay").disabled = row === ROWS - 1;
}
document.getElementById("stand").onclick = function(){ stopSpin(); show(idx, row - 1); };
document.getElementById("lay").onclick = function(){ stopSpin(); show(idx, row + 1); };

let dragging = false, x0 = 0, y0 = 0, i0 = 0, r0 = 0;
stage.addEventListener("pointerdown", function(e){
  stopSpin(); dragging = true; x0 = e.clientX; y0 = e.clientY; i0 = idx; r0 = row;
  stage.classList.add("dragging"); stage.setPointerCapture(e.pointerId); e.preventDefault();
});
stage.addEventListener("pointermove", function(e){
  if(!dragging) return;
  const per = Math.max(stage.clientWidth / N, 6);
  if(ROWS > 1){
    // left/right rolls the piece on its own axis, up/down tips it upright
    const perY = Math.max(stage.clientHeight / (ROWS * 2.2), 14);
    show(i0 - Math.round((e.clientX - x0) / per),
         r0 + Math.round((e.clientY - y0) / perY));
  } else {
    show(i0 - Math.round((e.clientX - x0) / per));
  }
});
["pointerup", "pointercancel", "lostpointercapture"].forEach(function(ev){
  stage.addEventListener(ev, function(){ dragging = false; stage.classList.remove("dragging"); });
});
stage.addEventListener("dragstart", function(e){ e.preventDefault(); });
stage.addEventListener("keydown", function(e){
  if(e.key === "ArrowLeft"){ stopSpin(); show(idx - 1); e.preventDefault(); }
  if(e.key === "ArrowRight"){ stopSpin(); show(idx + 1); e.preventDefault(); }
  if(e.key === "ArrowUp"){ stopSpin(); show(idx, row + 1); e.preventDefault(); }
  if(e.key === "ArrowDown"){ stopSpin(); show(idx, row - 1); e.preventDefault(); }
});

/* ---- remodeller ---- */
const slidersEl = document.getElementById("sliders"), draw = document.getElementById("drawing");
let cur = {};

function link(k, v){
  const inp = document.getElementById("s_" + k), out = document.getElementById("o_" + k);
  if(!inp) return;
  cur[k] = v; inp.value = v;
  const row = BASE[piece].filter(function(s){ return s.k === k; })[0];
  out.textContent = v + (row && row.unit ? " " + row.unit : "");
  out.classList.toggle("changed", !row || v !== row.v);
}

function baseOf(){ const o = {}; BASE[piece].forEach(function(s){ o[s.k] = s.v; }); return o; }

function buildSliders(){
  cur = baseOf();
  slidersEl.innerHTML = "";
  BASE[piece].forEach(function(s){
    const row = document.createElement("div");
    row.className = "slider";
    row.innerHTML = '<label for="s_' + s.k + '">' + s.label + '</label>' +
      '<output id="o_' + s.k + '">' + s.v + (s.unit ? " " + s.unit : "") + '</output>' +
      '<input id="s_' + s.k + '" type="range" min="' + s.min + '" max="' + s.max +
      '" step="' + s.step + '" value="' + s.v + '">';
    slidersEl.appendChild(row);
    const inp = row.querySelector("input"), out = row.querySelector("output");
    inp.addEventListener("input", function(){
      cur[s.k] = parseFloat(inp.value);
      out.textContent = cur[s.k] + (s.unit ? " " + s.unit : "");
      out.classList.toggle("changed", cur[s.k] !== s.v);
      if(s.k === "stemlen") link("height", 140 + (cur.stemlen - 88));
      if(s.k === "height")  link("stemlen", 88 + (cur.height - 140));
      render();
    });
  });
  render();
}

function outline(pc, d){
  if(pc === "hammer"){
    const h = d.height, hl = d.headlen, hs = d.headsec,
          st = d.stemod / 2, ft = d.footod / 2, foot = 7,
          top = h, bot = h - hs, lobe = -hl * 0.48, nose = hl * 0.52;
    return {seg: [
      ["M", -ft, 0], ["L", ft, 0], ["L", ft, foot], ["L", st, foot + 3],
      ["L", st, bot + 4], ["L", hl * 0.26, bot + 1],
      ["Q", nose, bot, nose, bot + hs * 0.30],
      ["L", nose, top - hs * 0.16], ["Q", nose, top, hl * 0.30, top],
      ["L", -hl * 0.24, top], ["Q", lobe, top, lobe, top - hs * 0.32],
      ["L", lobe, bot + hs * 0.32], ["Q", lobe, bot, -hl * 0.22, bot + 1],
      ["L", -st, bot + 4], ["L", -st, foot + 3], ["L", -ft, foot], ["Z"]],
      marks: [{x: nose - d.bowlid * 0.34, y: h - hs * 0.5, r: d.bowlid / 2}],
      h: h, w: Math.max(hl, d.footod)};
  }
  const h = d.height, br = d.mouthid / 2 + d.wall, ck = d.corkh,
        cr = br * 1.05, pr = d.mouthid / 2 - 0.4;
  return {seg: [
    ["M", -br * 0.94, 0], ["L", br * 0.94, 0], ["Q", br, 0, br, 2],
    ["L", br, h], ["L", -br, h], ["L", -br, 2], ["Q", -br, 0, -br * 0.94, 0], ["Z"],
    ["M", -pr, h - 6], ["L", pr, h - 6], ["L", pr, h + ck * 0.55],
    ["L", cr, h + ck * 0.55], ["L", cr, h + ck], ["L", -cr, h + ck],
    ["L", -cr, h + ck * 0.55], ["L", -pr, h + ck * 0.55], ["Z"]],
    marks: [], h: h + ck, w: Math.max(2 * cr, 2 * br), frit: [h - d.fritz, h]};
}

function toPath(o, s, cx, cy){
  return o.seg.map(function(g){
    if(g[0] === "Z") return "Z";
    const pts = [];
    for(let i = 1; i < g.length; i += 2)
      pts.push((cx + g[i] * s).toFixed(1) + "," + (cy - g[i + 1] * s).toFixed(1));
    return g[0] + pts.join(" ");
  }).join(" ");
}

function render(){
  const b = baseOf(), o = outline(piece, cur), ob = outline(piece, b);
  const span = Math.max(o.h, ob.h, o.w, ob.w, 1) * 1.16;
  const s = 350 / span, cx = 200, cy = 378;
  const css = getComputedStyle(document.body);
  const accent = css.getPropertyValue("--accent").trim();
  const ghost = css.getPropertyValue("--ink-3").trim();
  let svg = '<path d="' + toPath(ob, s, cx, cy) + '" fill="none" stroke="' + ghost +
            '" stroke-width="1" stroke-dasharray="3 3" opacity=".9"></path>';
  svg += '<path d="' + toPath(o, s, cx, cy) + '" fill="' + accent +
         '" fill-opacity=".10" stroke="' + accent + '" stroke-width="1.6"></path>';
  o.marks.forEach(function(m){
    svg += '<circle cx="' + (cx + m.x * s).toFixed(1) + '" cy="' + (cy - m.y * s).toFixed(1) +
           '" r="' + (m.r * s / 2).toFixed(1) + '" fill="none" stroke="' + accent +
           '" stroke-width="1.2" opacity=".75"></circle>';
  });
  if(o.frit){
    svg += '<line x1="' + (cx - o.w * s / 2 - 14).toFixed(1) + '" y1="' + (cy - o.frit[0] * s).toFixed(1) +
           '" x2="' + (cx - o.w * s / 2 - 14).toFixed(1) + '" y2="' + (cy - o.frit[1] * s).toFixed(1) +
           '" stroke="' + accent + '" stroke-width="3" opacity=".55"></line>';
  }
  const n = Math.round(cur.marbles || 0);
  for(let i = 0; i < n; i++){
    const t = n === 1 ? 0.5 : i / (n - 1);
    const mx = piece === "hammer" ? (cur.headlen * (0.06 + 0.36 * t)) : (-o.w / 2 + o.w * t);
    const my = piece === "hammer" ? (cur.height - cur.headsec * 0.74)
                                  : (cur.height - cur.fritz * 0.42);
    svg += '<circle cx="' + (cx + mx * s).toFixed(1) + '" cy="' + (cy - my * s).toFixed(1) +
           '" r="' + (3.4 * s).toFixed(1) + '" fill="none" stroke="' + accent +
           '" stroke-width="1" opacity=".5"></circle>';
  }
  draw.innerHTML = svg;
  const d = deltas();
  document.getElementById("deltaline").textContent = d.length
    ? d.length + " change" + (d.length > 1 ? "s" : "") + " from the original"
    : "no changes yet";
}

function deltas(){
  const b = baseOf();
  return BASE[piece].filter(function(s){ return cur[s.k] !== b[s.k]; })
    .map(function(s){ return s.label + ": " + b[s.k] + " " + ARROW + " " + cur[s.k] +
                             (s.unit ? " " + s.unit : ""); });
}

function requestJson(){
  const dims = {};
  BASE[piece].forEach(function(s){ if(cur[s.k] !== s.v) dims[s.k] = cur[s.k]; });
  const meta = META.pieces[piece];
  return {piece: meta.variant_of || piece, way: way,
          label: (document.getElementById("notes").value.trim().split("\n")[0] || "")
                 .slice(0, 40) || (meta.name + " variant"),
          notes: document.getElementById("notes").value.trim(),
          dims: dims};
}

function specText(){
  const lines = ["JBD remodel request",
    "Piece: " + META.pieces[piece].name + " (" + META.pieces[piece].code + ")",
    "Colourway: " + META.ways[way].name + " " + MID + " " + META.ways[way].sub, ""];
  const d = deltas();
  lines.push(d.length ? "Dimension changes:" : "Dimension changes: none");
  d.forEach(function(x){ lines.push("  - " + x); });
  const n = document.getElementById("notes").value.trim();
  if(n){ lines.push("", "Notes:", n); }
  lines.push("", "The original build stays as-is - this is a variant request.");
  return lines.join("\n");
}

function flash(id, text){
  const b = document.getElementById(id), old = b.textContent;
  b.textContent = text; setTimeout(function(){ b.textContent = old; }, 1400);
}
function loadLog(){
  try { return JSON.parse(localStorage.getItem("jbd_remodel") || "[]"); } catch(e){ return []; }
}
function paintLog(){
  const all = loadLog(), el = document.getElementById("log");
  if(!all.length){ el.innerHTML = ""; return; }
  el.innerHTML = "<b>Saved on this device " + MID + " " + all.length + "</b>" +
    all.slice(0, 4).map(function(r){
      return "<span>" + r.when + " " + MID + " " + META.pieces[r.piece].name + " " + MID + " " +
             r.changes + " dimension change(s)</span>"; }).join("");
}

document.getElementById("reset").onclick = function(){
  document.getElementById("notes").value = "";
  document.getElementById("vname").value = "";
  buildSliders();
};
document.getElementById("copy").onclick = function(){
  navigator.clipboard.writeText(specText())
    .then(function(){ flash("copy", "Copied"); })
    .catch(function(){ flash("copy", "Select and copy"); });
};
function refreshMail(){
  document.getElementById("mail").href = "mailto:" + CONTACT + "?subject=" +
    encodeURIComponent("JBD remodel request - " + META.pieces[piece].name) +
    "&body=" + encodeURIComponent(specText());
}
document.getElementById("mail").addEventListener("mousedown", refreshMail);
document.getElementById("mail").addEventListener("focus", refreshMail);
document.getElementById("dl").onclick = function(){
  const blob = new Blob([JSON.stringify(requestJson(), null, 1)],
                        {type: "application/json"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = (requestJson().label || "remodel").replace(/[^a-z0-9]+/gi, "-") + ".json";
  a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); }, 2000);
  flash("dl", "Downloaded");
};
document.getElementById("render").onclick = function(){
  const btn = document.getElementById("render"), note = document.getElementById("renderstate");
  const req = requestJson();
  if(!RENDER_URL){          // the shareable single file cannot call out - send them across
    note.hidden = false;
    note.innerHTML = 'This copy is a single offline file, so it cannot reach the build. ' +
      'Copy the spec, or open <a href="' + SITE + '">the live page</a> and re-render there.';
    return;
  }
  btn.disabled = true; btn.textContent = "Sending";
  note.hidden = false; note.textContent = "Sending " + req.label + " to the build...";
  fetch(RENDER_URL, {method: "POST",
                     headers: {"content-type": "application/json",
                               "X-Render-Key": RENDER_KEY},
                     body: JSON.stringify(req)})
    .then(function(r){ return r.json().then(function(j){ return {ok: r.ok, j: j}; }); })
    .then(function(res){
      if(res.ok && res.j.ok){
        btn.textContent = "Sent";
        note.textContent = '"' + req.label + '" is building. Give it a couple of minutes, ' +
          'then reload - it will be in the piece menu.';
      } else {
        btn.textContent = "Re-render it"; btn.disabled = false;
        note.textContent = "Build did not take it: " + (res.j.error || "unknown error") +
          ". Copy the spec and send it across instead.";
      }
    })
    .catch(function(){
      btn.textContent = "Re-render it"; btn.disabled = false;
      note.textContent = "Could not reach the build service. Copy the spec and send it across.";
    });
};
function specSheet(){
  const meta = META.pieces[piece], m = META.ways[way], st = STOCK[way] || {};
  const dims = {};
  BASE[piece].forEach(function(s){ dims[s.k] = {v: cur[s.k], label: s.label, unit: s.unit}; });
  const L = [];
  L.push("JEROME BAKER DESIGNS - MANUFACTURING SPEC");
  L.push("=========================================");
  L.push("Piece:      " + meta.name + "  (" + meta.code + ")");
  L.push("Colourway:  " + m.name + " " + MID + " " + m.sub);
  L.push("Build:      " + BUILD);
  L.push("");
  L.push("GLASS");
  L.push("  Stock:        borosilicate 3.3 (COE 33), density 2.23 g/cm3");
  L.push("  Body colour:  " + (st.body || "-") + "   " + (st.body_hex || "") +
         "   [" + (st.rod || "see swatch") + "]");
  L.push("  Accent:       " + (st.accent || "-") + "   " + (st.accent_hex || "") +
         "   (frit, marbles, linework)");
  L.push("  Fume:         " + (st.fume || "-"));
  L.push("");
  L.push("DIMENSIONS (mm unless noted)");
  Object.keys(dims).forEach(function(k){
    const d = dims[k];
    L.push("  " + (d.label + "                    ").slice(0, 22) + String(d.v) +
           (d.unit ? " " + d.unit : ""));
  });
  L.push("");
  L.push("SURFACE WORK");
  if(piece === "jar" || (meta.variant_of || piece) === "jar"){
    L.push("  Frit:        rolled band under the rim, grains 0.55-1.25 mm");
    L.push("  Marbles:     " + (cur.marbles || 0) + " clear, set evenly round the opening");
    L.push("  Linework:    dripped spiral, " + (cur.lines || 0) + " turns at " +
           (cur.linepitch || 0) + " mm drop per turn, thickness varying 0.35-1.9x");
    L.push("  Mark:        JB graffiti stamp, pressed lower middle, approx 25 mm wide");
    L.push("  Closure:     natural cork, tapered, seats 15 mm into a 38 mm mouth");
  } else {
    L.push("  Frit:        rolled over the whole bowl end and the foot");
    L.push("  Marbles:     " + (cur.marbles || 0) + " clear over the frit" +
           (cur.scatter ? " (scatter seed " + cur.scatter + ")" : " (hand-placed set)"));
    L.push("  Linework:    dripped spiral, " + (cur.lines || 0) + " turns at " +
           (cur.linepitch || 0) + " mm drop per turn, plus a run round the foot");
    L.push("  Label:       JBD x Boutiq enamel, white dropout, on the stem");
  }
  L.push("");
  L.push("PROCESS NOTES");
  L.push("  Head/body blown from heavy tube, shaped by hand - not axisymmetric.");
  L.push("  Bowl pushed in from the rim, no seam.");
  L.push("  Frit rolled on the marver while hot; marbles pressed in after.");
  L.push("  Linework dripped onto the piece while it spins - pitch and weight vary.");
  L.push("  Fume laid on last, before the final flash.");
  L.push("  Anneal: soak near 560 C, ramp slowly through the strain point (~518 C).");
  L.push("");
  L.push("TOLERANCES");
  L.push("  Rule-referenced dimensions  +/- 2-3 mm (hand-blown).");
  L.push("  Wall thickness is INFERRED, not measured - confirm with calipers on the");
  L.push("  rim and the stem OD before tooling. Mass, volume and glass cost move with it.");
  L.push("");
  L.push("FILES");
  L.push("  STEP / STL / GLB per piece and colourway: " +
         "https://github.com/" + REPO);
  L.push("  Site: https://zelidav.github.io/jbd-clearboy/");
  return L.join("\n");
}

document.getElementById("spec").onclick = function(){
  const blob = new Blob([specSheet()], {type: "text/plain"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "JBD_" + piece + "_" + way + "_spec.txt";
  a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); }, 3000);
  flash("spec", "Downloaded");
};

document.getElementById("save").onclick = function(){
  const all = loadLog();
  all.unshift({piece: piece, way: way, spec: specText(), changes: deltas().length,
               when: new Date().toISOString().slice(0, 16).replace("T", " ")});
  localStorage.setItem("jbd_remodel", JSON.stringify(all.slice(0, 20)));
  paintLog(); flash("save", "Saved");
};

select(PIECES[0], WAYS[0]);
paintLog();
if(!reduced) startSpin();
"""

DOWNLOADS_JS = r"""
const FILES = __FILES__, SIZES = __SIZES__, RAW = "__RAW__", VIDEOS = __VIDEOS__;
const STILLS = __STILLS__, BUILD = "__BUILD__", SPECFILES = __SPECFILES__;
document.getElementById("specrows").innerHTML = SPECFILES.map(function(f){
  return "<tr><td><a href='" + f[0] + "' download>" + f[0] + "</a></td>" +
    "<td class='num'>" + (SIZES[f[0]] || "-") + "</td>" +
    "<td class='use'>" + f[1] + "</td></tr>"; }).join("");
document.getElementById("filerows").innerHTML = FILES.map(function(f){
  return "<tr><td><a href='" + RAW + f[0] + "'>" + f[0].replace("out/", "") + "</a></td>" +
    "<td class='num'>" + f[1] + "</td><td class='num'>" + (SIZES[f[0]] || "-") +
    "</td><td class='use'>" + f[2] + "</td></tr>"; }).join("");
document.getElementById("stillrows").innerHTML = STILLS.map(function(v){
  return "<tr><td><a href='still/" + v[0] + "?v=" + BUILD + "'>" + v[0] + "</a></td>" +
    "<td class='use'>" + v[1] + "</td></tr>"; }).join("");
document.getElementById("videorows").innerHTML = VIDEOS.map(function(v){
  return "<tr><td><a href='video/" + v[0] + "?v=" + BUILD + "'>" + v[0] + "</a></td>" +
    "<td class='num'>" + (SIZES["video/" + v[0]] || "-") + "</td>" +
    "<td class='use'>" + v[1] + "</td></tr>"; }).join("");
"""


def build_index(inline):
    js = (INDEX_JS
          .replace("__ASSETS__", json.dumps(assets(inline)))
          .replace("__META__", json.dumps({"pieces": piece_meta(), "ways": WAY_META}))
          .replace("__BASE__", json.dumps(base_dims()))
          .replace("__SPECS__", json.dumps(piece_specs()))
          .replace("__REPO__", REPO)
          .replace("__CONTACT__", CONTACT)
          .replace("__RENDER_URL__", "" if inline else RENDER_URL)
          .replace("__RENDER_KEY__", RENDER_KEY)
          .replace("__STOCK__", json.dumps(STOCK)))
    return shell("Mockups &middot; Clearboy programme | Jerome Baker Designs",
                 INDEX_BODY, js, "index", standalone=inline)


def stills():
    """Copy the hero stills into the site and list them."""
    src, dst = "shots", os.path.join(SITE, "still")
    os.makedirs(dst, exist_ok=True)
    rows = []
    for pc in PIECES:
        for w in WAYS:
            name = "%s_%s.png" % (pc, w)
            if os.path.exists(os.path.join(src, name)):
                shutil.copyfile(os.path.join(src, name), os.path.join(dst, name))
                rows.append((name, "%s / %s %s" % (PIECE_META[pc]["name"],
                                                   WAY_META[w]["name"], WAY_META[w]["sub"])))
    return rows


SPECFILES = [
    ("JBD_Clearboy_spec.pdf",
     "Manufacturing spec - dimensions, dimensioned closeups, decoration and the survey"),
    ("JBD_Joint_Holder.pdf",
     "Joint holder - twelve designs on cut sheets, and how it wears as a pendant"),
    ("JBD_Glass_Tip.pdf",
     "Glass tip - dimensions, the screen, and the slot in use"),
    ("JBD_Clearboy_spec_ZH.pdf",
     "Manufacturing spec, Chinese - the same sheet for the glass shop"),
    ("JBD_Clearboy_pack.zip",
     "The whole hand-off - spec sheet, STEP / STL, closeups, survey and the box plates"),
    ("JBD_x_Boutiq_Deck.pdf",
     "Boutiq review deck - the set, the SKUs, the lids, open items and the timeline"),
    ("JBD_x_Boutiq.pdf", "The collaboration box, plate by plate - the leave-behind"),
]


def build_downloads():
    vids = [("%s_%s.mp4" % (pc, w),
             "%s / %s %s" % (PIECE_META[pc]["name"], WAY_META[w]["name"], WAY_META[w]["sub"]))
            for pc in PIECES for w in WAYS]
    js = (DOWNLOADS_JS
          .replace("__FILES__", json.dumps(FILES))
          .replace("__SIZES__", json.dumps(sizes()))
          .replace("__RAW__", RAW)
          .replace("__VIDEOS__", json.dumps(vids))
          .replace("__STILLS__", json.dumps(stills()))
          .replace("__SPECFILES__", json.dumps(SPECFILES)))
    return shell("Downloads | Jerome Baker Designs", DOWNLOADS_BODY, js, "downloads")


def write(name, html):
    html = html.replace("__BUILD__", BUILD)
    p = os.path.join(SITE, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %-32s %.2f MB" % (p, os.path.getsize(p) / 1e6))


if __name__ == "__main__":
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(os.path.join(SITE, "still"), exist_ok=True)
    BUILD = build_id()
    print("build", BUILD)
    dims = os.path.join(SITE, "dims.jpg")
    if os.path.exists("JBD_Clearboy_dimensions.png") and not os.path.exists(dims):
        from PIL import Image
        im = Image.open("JBD_Clearboy_dimensions.png").convert("RGB")
        w = 1500
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(
            dims, quality=86, optimize=True)
    write("index.html", build_index(False))
    write("survey.html", shell("Survey | Jerome Baker Designs", SURVEY_BODY, "", "survey"))
    write("downloads.html", build_downloads())
    write("mockups_selfcontained.html", build_index(True))
