"""Build the PUFF x JEROME BAKER page - docs/puff.html.

The PDF is the leave-behind. This is the thing you send in a message: the same argument,
but with the pieces in it that you can actually turn over. Every viewer on the page is
the same 72-position turntable the rest of the programme renders, decimated to 36 frames
and dragged by hand - no WebGL, no model download, and it works on a phone on a shop
floor with one bar of signal.

Set in Puff's system: their tube blue, the pink off their drip mark, the gold off the
grill in it, and a geometric rounded face standing in for their display type. None of
their logo files are reproduced - the lockup is set, and their artwork replaces it at
sign-off.

    python cad/puffpage.py     -> docs/puff.html
"""
import hashlib, json, os, sys

SITE = "docs"
SITE_URL = "https://zelidav.github.io/jbd-clearboy/"
SHARE = "puff_share.png"
PAGE = "puff.html"      # "" when the page is the index of its own domain
OUT = os.path.join(SITE, "puff.html")
CONTACT = "david@canismajorpartners.com"

# One finish. The piece is not a range with a Puff option in it - it is a Puff piece,
# so there is nothing to switch between and no switch on the page.
WAY = "puff_blue"

# One piece and the box it ships in. The rest of the programme has its own site; a
# partner deck that wanders into it is a deck about us rather than about the collab.
PIECES = [
    dict(id="tube_loaded", name="The piece", tag="JBD-JT-124",
         note="Opaque colour glass, silver fumed over the top of it.",
         specs=[("Overall height", "124 mm"), ("Body", "24 mm OD"),
                ("Wall", "4.5 mm, base 7 mm"), ("Bore", "15 mm - a 1 g king cone"),
                ("Glass", "approx. 79 g, boro 3.3"), ("Closure", "tapered natural cork")]),
    dict(id="box", name="In the box", tag="JBD-BX-169",
         note="Rigid board, lid hinged full height, two disc magnets in the front lip.",
         specs=[("Outside", "53 x 48 x 169 mm"), ("Board", "3.5 mm rigid, wrapped"),
                ("Clasp", "2 x 9 mm disc magnets"), ("Insert", "die-cut foam, one well"),
                ("Relief", "front-cut, lifts straight out"),
                ("Lining", "colour - the glass is seen against it")]),
]

MARKS = [
    ("Drips", "A band of gold laid on at the rim and let go. It runs, thins, and ends "
              "in a marble where it stopped. No two are the same."),
    ("Wig wag", "Stringers walked round the base while they are run up and down, "
                "stacked into chevrons - in the same pink and gold as the drips, so "
                "the two ends of the piece answer each other."),
    ("Marbles for feet", "Every drip ends in one, walked right round the piece rather "
                         "than set in a row down one side. To roll, the tube has to "
                         "climb over one - so it stops however it lands."),
    ("The JB mark", "Pressed into the glass on the face opposite the print. The piece "
                    "is signed the way a piece of glass is signed."),
    ("Weight", "4.5 mm of wall and 7 mm of base - about twice what it needs. That is "
               "not for the joint, it is so the piece survives being knocked off a "
               "counter for years."),
]

TIERS = [("Holiday drop", "10,000 / state", "20,000 units, one finish"),
         ("Strain drops", "10,000 / state", "same piece, new strain"),
         ("A year of it", "3 - 4 drops", "one occasion, then a cadence")]


def share_card(w=1200, h=630):
    """The image a link preview shows.

    Without one of these a shared link unfurls as a grey box, which is what a pitch
    looks like when nobody has thought about how it arrives. 1200 x 630 is what every
    unfurler wants; the piece goes on a panel of its own because the renders are shot
    on a studio sweep and would otherwise sit as a grey rectangle on the colour.
    """
    from PIL import Image, ImageDraw
    sys.path.insert(0, "cad")
    import mockups
    from mockups import PUFF, brand_font, puff_mark, _tracked_text, _tracked_width

    im = Image.new("RGB", (w, h), PUFF["blue"])
    d = ImageDraw.Draw(im)

    shot = os.path.join("shots", "tube_loaded_puff_blue.png")
    if os.path.exists(shot):
        art = Image.open(shot).convert("RGB")
        ph, pw = int(h * 0.86), int(w * 0.30)
        k = min(pw / art.width, ph / art.height)
        art = art.resize((max(int(art.width * k), 1), max(int(art.height * k), 1)),
                         Image.LANCZOS)
        px, py = int(w * 0.665), (h - art.height) // 2
        panel = Image.new("RGB", (art.width + 40, art.height + 40), (240, 246, 249))
        panel.paste(art, (20, 20))
        mask = Image.new("L", panel.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, panel.width - 1, panel.height - 1],
                                              radius=26, fill=255)
        im.paste(panel, (px, py - 20), mask)

    x0 = int(w * 0.065)
    mark = puff_mark(int(h * 0.115), PUFF["paper"])
    im.paste(mark, (x0, int(h * 0.115)), mark)
    xf = x0 + mark.width + int(h * 0.045)
    cf = brand_font("heavy", int(h * 0.055))
    d.text((xf, int(h * 0.155)), "\u00d7", font=cf, fill=PUFF["gold"])
    xf += d.textlength("\u00d7", font=cf) + int(h * 0.045)
    jf = brand_font("bold", int(h * 0.055))
    d.text((xf, int(h * 0.150)), "JEROME BAKER", font=jf, fill=PUFF["paper"])

    hf = brand_font("heavy", int(h * 0.088))
    y = int(h * 0.34)
    for line in ("THE ONLY PRE-ROLL", "THEY'LL STILL HAVE", "NEXT CHRISTMAS"):
        d.text((x0, y), line, font=hf, fill=PUFF["paper"])
        y += int(h * 0.105)

    sf = brand_font("bold", int(h * 0.032))
    t = "HOLIDAY 2026  \u00b7  CALIFORNIA + NEW YORK"
    tw = _tracked_width(d, t, sf, h * 0.012)
    _tracked_text(d, (x0, int(h * 0.80)), t, sf, PUFF["gold"], h * 0.012)
    im.save(os.path.join(SITE, SHARE))
    return os.path.join(SITE, SHARE)


def build_id():
    """A short stamp over everything the page serves.

    The spinner frames live at fixed paths, so a browser that has been on this page
    before will happily show yesterday's renders on today's page - which looks exactly
    like the page not having updated. Every asset URL carries this, and it moves
    whenever any of the frames or any of the build scripts do.
    """
    h = hashlib.md5()
    for root in (os.path.join(SITE, "spin"), os.path.join(SITE, "video")):
        for dirpath, _, names in os.walk(root):
            for n in sorted(names):
                f = os.path.join(dirpath, n)
                h.update(n.encode())
                h.update(str(os.path.getsize(f)).encode())
    for f in sorted(os.listdir("cad")):
        if f.endswith(".py"):
            h.update(open(os.path.join("cad", f), "rb").read())
    pdf = os.path.join(SITE, "PUFF_x_JBD.pdf")
    if os.path.exists(pdf):
        h.update(str(os.path.getsize(pdf)).encode())
    return h.hexdigest()[:8]


BUILD = None


def frames():
    """Every spinner the page needs, as relative URLs. A piece and colourway with no
    frames rendered is left out rather than linked and broken."""
    out = {}
    for p in PIECES:
        out[p["id"]] = {}
        d = os.path.join(SITE, "spin", "%s_%s" % (p["id"], WAY))
        if os.path.isdir(d):
            names = sorted(f for f in os.listdir(d) if f.endswith(".webp"))
            if names:
                out[p["id"]][WAY] = ["spin/%s_%s/%s?v=%s" % (p["id"], WAY, n, BUILD)
                                     for n in names]
    missing = [p["id"] for p in PIECES if not out[p["id"]]]
    if missing:
        raise SystemExit("no rendered frames for: %s - run spin_all/encode first"
                         % ", ".join(missing))
    return out


CSS = """
:root{
  --blue:#00A0C0; --blue-d:#0A2352; --pink:#6050C0; --gold:#D0A010;
  --ink:#0B0D10; --ink-2:#3C434C; --ink-3:#79828E;
  --paper:#FFFFFF; --wash:#F4F7FA; --rule:#E2E8EE;
  --font:"Poppins","Segoe UI",system-ui,-apple-system,Helvetica,Arial,sans-serif;
}
@media (prefers-color-scheme:dark){
  :root{ --ink:#EEF2F6; --ink-2:#AEB8C4; --ink-3:#7B8794;
         --paper:#12161B; --wash:#0B0E12; --rule:#242C34; }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--wash);color:var(--ink);font-family:var(--font);
  font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:var(--blue-d)}
@media (prefers-color-scheme:dark){a{color:var(--blue)}}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
h1,h2,h3{margin:0;text-wrap:balance;letter-spacing:-.01em}
p{margin:0}

/* ---- lockup ---------------------------------------------------------- */
.lock{display:flex;align-items:baseline;gap:.55em;font-weight:800;line-height:1}
.lock .u{display:flex;flex-direction:column;gap:.12em;line-height:1}
.lock .u b{font-weight:800;letter-spacing:-.02em}
.lock .u i{font-style:normal;font-weight:400;font-size:.34em;letter-spacing:.12em;
  opacity:.9}
.lock .x{color:var(--gold);font-size:.72em}

/* ---- bar ------------------------------------------------------------- */
.bar{position:sticky;top:0;z-index:40;background:var(--blue);color:#fff}
.bar .wrap{display:flex;align-items:center;gap:18px;padding-top:12px;padding-bottom:12px}
.bar .lock{font-size:26px}
.bar nav{margin-left:auto;display:flex;gap:16px;font-size:13px;font-weight:600;
  letter-spacing:.04em;text-transform:uppercase}
.bar nav a{color:#fff;text-decoration:none;opacity:.82;padding-bottom:2px;
  border-bottom:2px solid transparent}
.bar nav a:hover{opacity:1;border-bottom-color:#fff}
@media(max-width:860px){.bar nav{display:none}}
.drip{height:26px;background:var(--blue);
  -webkit-mask-image:radial-gradient(circle at 10px 0,#000 9px,transparent 10px);
  mask-image:radial-gradient(circle at 10px 0,#000 9px,transparent 10px);
  -webkit-mask-size:34px 26px;mask-size:34px 26px;
  -webkit-mask-repeat:repeat-x;mask-repeat:repeat-x}

/* ---- hero ------------------------------------------------------------ */
.hero{padding:44px 0 10px}
.hero h1{font-size:clamp(38px,6.2vw,74px);font-weight:800;line-height:1.02;
  text-transform:uppercase}
.hero .sub{color:var(--ink-2);font-size:19px;margin-top:18px;max-width:56ch}
.pills{display:flex;gap:9px;flex-wrap:wrap;margin-top:20px}
.pill{border-radius:999px;padding:6px 15px;font-size:12.5px;font-weight:700;
  letter-spacing:.08em;text-transform:uppercase;color:#fff;background:var(--pink)}
.pill.g{background:var(--gold);color:#1a1408}
.pill.k{background:var(--ink);color:var(--paper)}

/* ---- viewer ---------------------------------------------------------- */
.stage{display:grid;gap:26px;grid-template-columns:minmax(320px,1.05fr) minmax(280px,.95fr);
  align-items:start;margin:30px 0 10px}
@media(max-width:900px){.stage{grid-template-columns:1fr}}
.viewer{background:var(--paper);border:1px solid var(--rule);border-radius:22px;
  overflow:hidden;position:relative}
.frameBox{position:relative;background:#EDEFF2;touch-action:pan-y;cursor:grab;
  user-select:none;-webkit-user-select:none}
.frameBox.dragging{cursor:grabbing}
/* the tube renders portrait at 640x1040; letting it fill the column pushes the
   bottom of the piece off the screen, so the frame is capped to the viewport and
   the image is centred in it rather than stretched */
.frameBox{display:flex;align-items:center;justify-content:center;min-height:340px}
.frameBox img{width:auto;max-width:100%;max-height:64vh;pointer-events:none}
.hint{position:absolute;left:50%;bottom:14px;transform:translateX(-50%);
  background:rgba(11,13,16,.72);color:#fff;font-size:12px;font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;padding:7px 14px;border-radius:999px;
  transition:opacity .35s;pointer-events:none}
.hint.gone{opacity:0}
.vbar{display:flex;align-items:center;gap:10px;padding:12px 14px;
  border-top:1px solid var(--rule);flex-wrap:wrap}
.finish{display:flex;align-items:center;gap:10px;font-size:14px;font-weight:600;
  color:var(--ink-2)}
.finish i{width:22px;height:22px;border-radius:50%;
  background:linear-gradient(145deg,#7FD4E4,#00A0C0 58%,#0A2352);
  box-shadow:0 0 0 2px var(--rule)}
.spinbtn{margin-left:auto;border:1px solid var(--rule);background:transparent;
  color:var(--ink-2);border-radius:999px;padding:6px 14px;font:inherit;font-size:13px;
  font-weight:600;cursor:pointer}
.spinbtn[aria-pressed="true"]{border-color:var(--blue);color:var(--blue-d)}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.tab{border:1px solid var(--rule);background:var(--paper);color:var(--ink-2);
  border-radius:999px;padding:8px 16px;font:inherit;font-size:14px;font-weight:600;
  cursor:pointer}
.tab[aria-selected="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.panel{background:var(--paper);border:1px solid var(--rule);border-radius:22px;
  padding:24px 26px}
.panel h2{font-size:27px;font-weight:800}
.panel .tag{font-size:12.5px;font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;color:var(--pink)}
.panel .note{color:var(--ink-2);margin-top:10px;font-size:16px}
.spec{margin-top:18px;border-top:1px solid var(--rule)}
.spec div{display:flex;justify-content:space-between;gap:16px;padding:11px 0;
  border-bottom:1px solid var(--rule);font-size:15px}
.spec span{color:var(--ink-3)}
.spec b{font-weight:700;text-align:right}

/* ---- sections -------------------------------------------------------- */
section{padding:56px 0}
section.alt{background:var(--paper);border-top:1px solid var(--rule);
  border-bottom:1px solid var(--rule)}
.eyebrow{font-size:12.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;
  color:var(--pink)}
h2.big{font-size:clamp(28px,4.2vw,46px);font-weight:800;text-transform:uppercase;
  margin-top:12px;line-height:1.08}
.lede{color:var(--ink-2);margin-top:16px;max-width:62ch;font-size:18px}
.grid3{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
  margin-top:30px}
.card{background:var(--wash);border:1px solid var(--rule);border-radius:18px;
  padding:22px 24px}
section.alt .card{background:var(--wash)}
.card h3{font-size:19px;font-weight:700}
.card p{color:var(--ink-2);font-size:15.5px;margin-top:8px}
.stats{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
  margin-top:30px}
.stat b{display:block;font-size:52px;font-weight:800;line-height:1;letter-spacing:-.02em}
.stat span{display:block;color:var(--ink-3);font-size:15px;margin-top:10px}
.marks{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  margin-top:28px}
.mark{border-left:4px solid var(--blue);padding:4px 0 4px 16px}
.mark:nth-child(2){border-color:var(--pink)}
.mark:nth-child(3){border-color:var(--gold)}
.mark:nth-child(4){border-color:var(--blue-d)}
.mark:nth-child(5){border-color:var(--ink-3)}
.mark h3{font-size:16px;font-weight:700}
.mark p{color:var(--ink-2);font-size:14.5px;margin-top:5px}
.note{color:var(--ink-3);font-size:14.5px;margin-top:18px}
.tiers{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  margin-top:28px}
.tier{background:var(--ink);color:#fff;border-radius:18px;padding:22px 24px}
.tier b{display:block;font-size:19px;font-weight:700}
.tier em{display:block;font-style:normal;font-size:40px;font-weight:800;
  color:var(--blue);margin-top:6px;line-height:1}
.tier span{display:block;color:#9AA5B1;font-size:14.5px;margin-top:8px}
.cta{background:var(--blue);color:#fff}
.cta h2.big{color:#fff}
.cta .lede{color:#E4F4FE}
.steps{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  margin-top:28px}
.step{background:rgba(0,0,0,.16);border-radius:16px;padding:18px 20px}
.step b{display:block;font-size:17px;font-weight:700}
.step span{display:block;color:#DCEFFA;font-size:14.5px;margin-top:5px}
.btns{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}
.btn{display:inline-block;background:#fff;color:var(--blue-d);border-radius:999px;
  padding:13px 24px;font-weight:700;text-decoration:none}
.btn.k{background:var(--ink);color:#fff}
footer{background:var(--ink);color:#8C97A3;padding:34px 0;font-size:14px}
footer .lock{color:#fff;font-size:22px;margin-bottom:14px}
footer a{color:#fff}
"""

JS = r"""
(function(){
  var FR = window.__FRAMES__, PIECES = window.__PIECES__;
  var piece = PIECES[0].id, way = window.__WAY__, idx = 0, spinning = true;
  var box = document.getElementById('frameBox');
  var img = document.getElementById('frameImg');
  var hint = document.getElementById('hint');
  var cache = {};

  function set(list){
    // preload once per set, so a drag never shows a blank frame
    var k = list[0];
    if(!cache[k]){ cache[k] = list.map(function(u){ var i=new Image(); i.src=u; return i; }); }
  }
  function ways(){ return FR[piece] || {}; }
  function list(){
    var w = ways();
    return w[way] || w[Object.keys(w)[0]] || [];
  }
  function draw(){
    var l = list();
    if(!l.length) return;
    idx = ((idx % l.length) + l.length) % l.length;
    img.src = l[idx];
  }
  function pick(p){
    piece = p; idx = 0; set(list()); draw();
    var d = PIECES.filter(function(x){ return x.id === p; })[0];
    document.getElementById('pName').textContent = d.name;
    document.getElementById('pTag').textContent = d.tag;
    document.getElementById('pNote').textContent = d.note;
    document.getElementById('pSpec').innerHTML = d.specs.map(function(r){
      return '<div><span>' + r[0] + '</span><b>' + r[1] + '</b></div>'; }).join('');
    [].forEach.call(document.querySelectorAll('.tab[data-piece]'), function(b){
      b.setAttribute('aria-selected', b.dataset.piece === p ? 'true' : 'false'); });
  }

  [].forEach.call(document.querySelectorAll('.tab[data-piece]'), function(b){
    b.addEventListener('click', function(){ pick(b.dataset.piece); }); });

  // drag to spin. One frame per 7 px of travel reads as 1:1 on a phone and a mouse.
  var down = false, lastX = 0, moved = 0;
  function start(x){ down = true; lastX = x; moved = 0; box.classList.add('dragging'); }
  function move(x){
    if(!down) return;
    var dx = x - lastX;
    if(Math.abs(dx) < 7) return;
    var step = Math.trunc(dx / 7);
    idx -= step; lastX = x; moved += Math.abs(dx);
    if(moved > 24){ stop(); hint.classList.add('gone'); }
    draw();
  }
  function end(){ down = false; box.classList.remove('dragging'); }
  box.addEventListener('mousedown', function(e){ start(e.clientX); e.preventDefault(); });
  window.addEventListener('mousemove', function(e){ move(e.clientX); });
  window.addEventListener('mouseup', end);
  box.addEventListener('touchstart', function(e){ start(e.touches[0].clientX); },
                       {passive:true});
  box.addEventListener('touchmove', function(e){ move(e.touches[0].clientX); },
                       {passive:true});
  box.addEventListener('touchend', end);

  var timer = null;
  function go(){ if(timer) return; timer = setInterval(function(){ idx += 1; draw(); }, 90); }
  function stop(){ if(timer){ clearInterval(timer); timer = null; }
    spinning = false;
    document.getElementById('spinBtn').setAttribute('aria-pressed','false'); }
  document.getElementById('spinBtn').addEventListener('click', function(){
    if(timer){ stop(); }
    else { spinning = true; this.setAttribute('aria-pressed','true'); go(); }
  });

  pick(piece); go();
  // only autoplay while it is on screen - a spinner running in a background tab is
  // thirty image decodes a second for nobody
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!spinning) return;
        if(e.isIntersecting){ go(); } else if(timer){ clearInterval(timer); timer = null; }
      });
    }, {threshold:.15}).observe(box);
  }
})();
"""


def lockup(size, ink="#fff", gold="var(--gold)"):
    return ('<span class="lock" style="font-size:%s">'
            '<span class="u"><b>PUFF</b><i>pre-rolls</i></span>'
            '<span class="x">&times;</span>'
            '<span class="u"><b>JEROME BAKER</b><i>designs</i></span></span>' % size)


FAVICON = ('<link rel="icon" href="data:image/svg+xml,'
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='7' fill='%2300A0C0'/%3E"
           "%3Crect x='13' y='5' width='6' height='22' rx='3' fill='%23fff'/%3E"
           "%3Ccircle cx='16' cy='24' r='3' fill='%236050C0'/%3E%3C/svg%3E\">")


REDIRECT = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>PUFF &times; Jerome Baker</title>
<link rel="canonical" href="%(to)s">
<meta http-equiv="refresh" content="0; url=%(to)s">
<meta name="robots" content="noindex">
<style>
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:#00A0C0;color:#fff;font:16px/1.6 "Poppins","Segoe UI",system-ui,sans-serif;
  text-align:center;padding:24px}
a{color:#fff}
</style>
<div>
  <p style="font-size:22px;font-weight:700;margin:0 0 10px">This has moved.</p>
  <p style="margin:0">
    <a href="%(to)s">%(to)s</a>
  </p>
</div>
<script>location.replace("%(to)s");</script>
</html>
"""


def write_redirect(to="https://puffxjb.cannacrypted.com/"):
    """Leave a forwarder where the page used to live.

    GitHub Pages cannot serve a 301, so this is the next best thing: a canonical link
    for anything that reads the page, a meta refresh for anything that does not run
    JavaScript, and a replace() so the old URL does not sit in the back button."""
    path = os.path.join(SITE, "puff.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(REDIRECT % {"to": to})
    print("wrote redirect", path, "->", to)
    return path


def export(dest, url):
    """Write the page and everything it needs into a standalone site directory.

    The page is served from its own subdomain rather than as one file inside the
    Clearboy programme, so it needs its own copy of the frames it spins. Paths in the
    page are already relative, so the only thing that changes is where they are rooted
    and what the absolute URL in the share tags points at.
    """
    import shutil
    global SITE_URL, PAGE
    was, SITE_URL = SITE_URL, url
    was_page, PAGE = PAGE, ""
    try:
        os.makedirs(dest, exist_ok=True)
        html = build(write=False)
        with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        for p in PIECES:                       # only the spinners this page uses
            src = os.path.join(SITE, "spin", "%s_%s" % (p["id"], WAY))
            if os.path.isdir(src):
                dst = os.path.join(dest, "spin", "%s_%s" % (p["id"], WAY))
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst)
        for name in (SHARE, "puff_variable.png", "puff_box_variants.png",
                     "PUFF_x_JBD.pdf"):
            src = os.path.join(SITE, name)
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(dest, name))
        with open(os.path.join(dest, "CNAME"), "w", encoding="utf-8") as f:
            f.write(url.split("//")[-1].strip("/") + "\n")
        open(os.path.join(dest, ".nojekyll"), "w").close()
        print("exported to", dest)
    finally:
        SITE_URL, PAGE = was, was_page
    return dest


def build(write=True):
    global BUILD
    BUILD = build_id()
    share_card()
    fr = frames()
    tabs = "".join(
        '<button class="tab" data-piece="%s" aria-selected="%s">%s</button>'
        % (p["id"], "true" if i == 0 else "false", p["name"])
        for i, p in enumerate(PIECES))
    marks = "".join('<div class="mark"><h3>%s</h3><p>%s</p></div>' % (t, b)
                    for t, b in MARKS)
    tiers = "".join('<div class="tier"><b>%s</b><em>%s</em><span>%s</span></div>'
                    % t for t in TIERS)

    html = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>PUFF &times; Jerome Baker &mdash; the only pre-roll they'll still have next Christmas</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="A holiday collab drop: the Puff one-gram in a \
hand-blown Jerome Baker tube, paired with a strain, in a box worth opening.">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate">
<meta property="og:type" content="website">
<meta property="og:title" content="PUFF &times; Jerome Baker">
<meta property="og:description" content="The only pre-roll they'll still have next Christmas. A holiday collab drop: the Puff one-gram in a hand-blown Jerome Baker tube.">
<meta property="og:url" content="%(site)s%(page)s">
<meta property="og:image" content="%(site)s%(share)s?v=%(build)s">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="PUFF &times; Jerome Baker">
<meta name="twitter:description" content="The only pre-roll they'll still have next Christmas.">
<meta name="twitter:image" content="%(site)s%(share)s?v=%(build)s">
%(favicon)s
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>%(css)s</style>

<header class="bar">
  <div class="wrap">
    %(lock)s
    <nav>
      <a href="#piece">The piece</a>
      <a href="#box">The box</a>
      <a href="#variable">What changes</a>
      <a href="#drop">The drop</a>
      <a href="PUFF_x_JBD.pdf?v=%(build)s">PDF</a>
    </nav>
  </div>
</header>
<div class="drip"></div>

<div class="wrap hero" id="piece">
  <h1>The only pre-roll<br>they&rsquo;ll still have<br>next Christmas</h1>
  <p class="sub">One holiday drop: the Puff one-gram in a hand-blown Jerome Baker tube,
  in a box worth opening. Same format, same wordmark up the side &mdash; in a piece they
  keep using long after the joint is gone.</p>
  <div class="pills">
    <span class="pill">Concept pack</span>
    <span class="pill g">California + New York</span>
    <span class="pill k">Holiday 2026</span>
  </div>

  <div class="stage">
    <div>
      <div class="tabs">%(tabs)s</div>
      <div class="viewer">
        <div class="frameBox" id="frameBox">
          <img id="frameImg" alt="Turntable render of the piece" draggable="false">
          <div class="hint" id="hint">Drag to turn</div>
        </div>
        <div class="vbar">
          <span class="finish"><i></i>Puff Teal &middot; silver fumed</span>
          <button class="spinbtn" id="spinBtn" aria-pressed="true">Auto-turn</button>
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="tag" id="pTag"></div>
      <h2 id="pName"></h2>
      <p class="note" id="pNote"></p>
      <div class="spec" id="pSpec"></div>
    </div>
  </div>
</div>

<section>
  <div class="wrap">
    <div class="eyebrow">What is on the glass</div>
    <h2 class="big">Five things, all of them by hand</h2>
    <p class="lede">Every one of these is a separate trip to the torch, which is why two
    tubes off the same bench are the same object and not the same piece. That is what a
    limited drop is actually selling.</p>
    <div class="marks">%(marks)s</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="eyebrow">Why now</div>
    <h2 class="big">The timing is<br>the whole thing</h2>
    <p class="lede">You have the reach and the doors. We have been blowing glass since
    the nineties and a name people collect. Put those together in the one week of the
    year when people are buying an object instead of a price, and it is not a hard sell
    to anybody &mdash; small, finite, and easy to walk away from if it is not for
    you.</p>
    <div class="grid3">
      <div class="card"><h3>The reach</h3><p>Twenty million pre-rolls and the doors that
      go with them. Nothing we make gets in front of that many people on its
      own.</p></div>
      <div class="card"><h3>The momentum</h3><p>Jerome Baker is opening doors in New
      York quickly right now. A drop across both states rides that in one of the two
      markets you are already in.</p></div>
      <div class="card"><h3>The window</h3><p>Holiday is the one stretch of the year
      when the question is what to give somebody, not what something costs. That is the
      whole reason this piece works.</p></div>
    </div>
  </div>
</section>

<section class="alt" id="box">
  <div class="wrap">
    <div class="eyebrow">The box</div>
    <h2 class="big">Rigid board, hinged lid,<br>magnetic clasp</h2>
    <p class="lede">The lid is hinged full height and closes onto two disc magnets. It
    opens with a click, and it is the kind of box people keep things in afterwards
    rather than flatten and bin. Switch the viewer above to <b>In the box</b> to turn
    it over.</p>
    <div class="grid3">
      <div class="card"><h3>Tissue and a seal, no insert</h3><p>The piece is wrapped in
      branded tissue and closed with a sticker seal. No foam, no cradle &mdash; a box
      cut to the piece does not need anything holding it still, and there is nothing in
      it that cannot go in the recycling with the box.</p></div>
      <div class="card"><h3>Cut to the piece</h3><p>44 &times; 48 &times; 157 mm. Just
      enough room for the tube and the tissue round it, which is cheaper to make, cheaper
      to ship and better to open.</p></div>
      <div class="card"><h3>Your mark inside the lid</h3><p>The collab lockup sits on
      the board itself, foil-stamped rather than printed on a panel &mdash; the first
      thing seen when it opens. 53 &times; 52 &times; 169 mm, 3.5 mm board, wrapped
      inside and out.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="eyebrow">The idea</div>
    <h2 class="big">Twenty million thrown away.<br>Twenty thousand kept forever.</h2>
    <p class="lede">Twenty million pre-rolls have gone out, and twenty million tubes have
    gone in the bin with them. That is the volume &mdash; and it is exactly why the
    opposite of it is worth doing once a year. Twenty thousand pieces that nobody throws
    away. From the day it is opened it is where they keep a joint: any joint, one of
    yours, one from somewhere else, one they rolled themselves. Every time they take one
    out, they are holding your name. You paid for that placement once, at Christmas, and
    it keeps working all year.</p>
    <div class="stats">
      <div class="stat"><b>20M+</b><span>sold, and binned with their tubes</span></div>
      <div class="stat"><b>20,000</b><span>in the drop, and kept</span></div>
      <div class="stat"><b>79 g</b><span>of glass. The weight is half of why it feels
        worth keeping</span></div>
      <div class="stat"><b>3&ndash;4</b><span>drops a year the same piece
        carries</span></div>
    </div>
  </div>
</section>

<section class="alt" id="variable">
  <div class="wrap">
    <div class="eyebrow">What changes</div>
    <h2 class="big">One box. Any strain.</h2>
    <p class="lede">Nothing that changes is printed on the glass or the box. Two pieces
    of paper carry all of it &mdash; which means a second drop is a sleeve and a
    sticker, not a new product.</p>
    <p style="margin-top:26px"><img src="puff_box_variants.png?v=%(build)s"
      alt="The same box and the same glass with three different sleeves and cards"
      style="border-radius:16px;border:1px solid var(--rule)"></p>
    <p style="margin-top:22px"><img src="puff_variable.png?v=%(build)s"
      alt="Beauty card, band, tissue seal and compliance sticker, flat, in two strain variants"
      style="border-radius:16px;border:1px solid var(--rule)"></p>
    <div class="grid3">
      <div class="card"><h3>The box</h3><p>Printed once. No strain on it, no batch, no
      potency &mdash; so one run of board covers every drop there will ever be.</p></div>
      <div class="card"><h3>The sleeve</h3><p>Slips over it. The strain and its colour,
      and the only thing that has to be reprinted to make a new drop.</p></div>
      <div class="card"><h3>The sticker</h3><p>Strain and potency, printed the week it
      is packed rather than the quarter before. The tissue seal closes the wrap.</p></div>
    </div>
  </div>
</section>

<section id="drop">
  <div class="wrap">
    <div class="eyebrow">The drop</div>
    <h2 class="big">A holiday drop,<br>not a packaging change.</h2>
    <p class="lede">On shelf for the gifting weeks, in California and New York, ten
    thousand a state. One piece, one finish, paired with a strain chosen for the drop
    and named on the box &mdash; allocated by door count into doors that already carry
    Puff. After it: the same piece, a new strain, a drop a quarter if the first one
    lands.</p>
    <div class="tiers">%(tiers)s</div>
    <p class="note">Capacity is in place for all three bands. The body and the
    decoration run as two jobs and the line is in place. Samples in hand inside three
    weeks of sign-off.</p>
  </div>
</section>

<section class="cta">
  <div class="wrap">
    <h2 class="big">Say go, and you hold one<br>in three weeks</h2>
    <p class="lede">You already know the work, so there is nothing here to prove on
    paper. Strain, finish, artwork &mdash; you will want changes, and they are easier to
    make with the piece in your hand than in a meeting about it. Nothing to specify to
    start.</p>
    <div class="btns">
      <a class="btn" href="mailto:%(contact)s?subject=PUFF%%20x%%20Jerome%%20Baker">Say go</a>
      <a class="btn k" href="PUFF_x_JBD.pdf?v=%(build)s">Download the pack (PDF)</a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    %(flock)s
    <p>Puff wordmark used as supplied.</p>
    <p style="margin-top:10px">Jerome Baker Designs &middot;
      <a href="mailto:%(contact)s">%(contact)s</a> &middot;
      <a href="./">the rest of the programme</a></p>
  </div>
</footer>

<script>
window.__FRAMES__ = %(frames)s;
window.__PIECES__ = %(pieces)s;
window.__WAY__ = "%(way)s";
</script>
<script>%(js)s</script>
</html>
""" % dict(css=CSS, js=JS, tabs=tabs, marks=marks,
           tiers=tiers, contact=CONTACT,
           lock=lockup("26px"), flock=lockup("22px"), favicon=FAVICON,
           way=WAY, build=BUILD, site=SITE_URL, share=SHARE, page=PAGE,
           frames=json.dumps(fr, separators=(",", ":")),
           pieces=json.dumps(PIECES, separators=(",", ":")))

    if not write:
        return html
    os.makedirs(SITE, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", OUT, "-", round(len(html) / 1024.0, 1), "KB", "build", BUILD)
    return OUT


if __name__ == "__main__":
    if "--redirect" in sys.argv:
        write_redirect()
        raise SystemExit(0)
    build()
    if "--export" in sys.argv:
        export(sys.argv[sys.argv.index("--export") + 1],
               "https://puffxjb.cannacrypted.com/")
