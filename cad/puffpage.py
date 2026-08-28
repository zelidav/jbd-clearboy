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
import json, os, sys

SITE = "docs"
OUT = os.path.join(SITE, "puff.html")
CONTACT = "david@canismajorpartners.com"

WAYS = [
    ("teal_silver", "Mint, silver fume", "rod 13 &middot; silver nitrate",
     "linear-gradient(145deg,#E4F5EF,#C9E8E1 60%,#8FC8BC)"),
    ("magenta_gold", "Pink, gold fume", "rod 3 &middot; gold chloride",
     "linear-gradient(145deg,#F0A0C8,#C0348A 62%,#7E1E5C)"),
    ("clear_silver", "Clear, heavy silver", "teal accents &middot; wrapped",
     "linear-gradient(145deg,#EDF2F6,#9FB6E0 55%,#6E8CC4)"),
    ("clear_gold", "Clear, heavy gold", "magenta accents &middot; wrapped",
     "linear-gradient(145deg,#FBF3E4,#E0BE7A 55%,#C08A3E)"),
]

PIECES = [
    dict(id="tube_loaded", name="The tube, loaded", tag="JBD-JT-124",
         note="A one-gram cone, sealed under cork.",
         specs=[("Overall height", "124 mm"), ("Body", "24 mm OD"),
                ("Wall", "4.5 mm, base 7 mm"), ("Bore", "15 mm - a 1 g king cone"),
                ("Glass", "approx. 79 g, boro 3.3"), ("Closure", "tapered natural cork")]),
    dict(id="tube", name="The tube, empty", tag="JBD-JT-124",
         note="What it is once the joint is gone - which is the whole point.",
         specs=[("Overall height", "124 mm"), ("Body", "24 mm OD"),
                ("Wall", "4.5 mm, base 7 mm"), ("Decoration", "wig wag, drips, 2 marbles"),
                ("Mark", "JB pressed into the wall"), ("Print", "50 mm band, up the axis")]),
    dict(id="box", name="In the box", tag="JBD-BX-169",
         note="Rigid board, lid hinged full height, two disc magnets in the front lip.",
         specs=[("Outside", "53 x 48 x 169 mm"), ("Board", "3.5 mm rigid, wrapped"),
                ("Clasp", "2 x 9 mm disc magnets"), ("Insert", "die-cut foam, one well"),
                ("Relief", "front-cut, lifts straight out"),
                ("Lining", "colour - the glass is seen against it")]),
    dict(id="lighter_loaded", name="Lighter sleeve", tag="JBD-LS-58",
         note="A glass jacket for the lighter everyone already owns.",
         specs=[("Overall height", "58 mm"), ("Section", "30 x 19 mm obround"),
                ("Socket", "24.5 x 13.3 mm"), ("Glass", "approx. 29 g"),
                ("Proud", "26 mm of lighter"), ("Notch", "through the front wall")]),
]

MARKS = [
    ("Drips", "A band of colour laid on at the rim and let go. It runs, thins, and beads "
              "where it stopped. No two are the same."),
    ("Wig wag", "Stringers walked round the base while they are run up and down, stacked "
                "into chevrons. Two colours, pulled by hand."),
    ("Two marbles", "Set proud on one side, a few degrees apart. Laid down it beds on "
                    "both and will not roll off a bench."),
    ("The JB mark", "Pressed into the wall under the print. The piece is signed where a "
                    "piece of glass is signed, not on a sticker."),
    ("Heavy wall", "4.5 mm of wall and 7 mm of base - about twice what it needs to hold "
                   "anything. It is not holding anything; it is surviving the floor."),
]

ROUTES = [
    ("A", "Glass inside a CR outer", "#2FB4F5",
     "The loaded tube ships inside a child-resistant carton or pouch. The customer "
     "opens the pack and keeps the glass.",
     "Highest cost per unit, cleanest story. Route to test first."),
    ("B", "Glass sold empty, alongside", "#E85090",
     "The pre-roll ships in the existing compliant pack; the tube sells as an empty "
     "vessel at the same counter, in the same artwork.",
     "Fastest to market. No packaging approval. Loses the unboxing."),
    ("C", "CR closure on the glass", "#E8B21F",
     "A certified push-and-turn closure replacing the cork. Real, and used on glass "
     "tubes today - but it is a tooled part and it has to be tested.",
     "Longest lead time. The endgame, not the launch."),
]

TIERS = [("Pilot", "500", "one colourway, one state"),
         ("Drop", "2,500", "two colourways, both states"),
         ("Programme", "10,000+", "rolling, four ways")]


def frames():
    """Every spinner the page needs, as relative URLs. A piece and colourway with no
    frames rendered is left out rather than linked and broken."""
    out = {}
    for p in PIECES:
        out[p["id"]] = {}
        for key, _, _, _ in WAYS:
            d = os.path.join(SITE, "spin", "%s_%s" % (p["id"], key))
            if not os.path.isdir(d):
                continue
            names = sorted(f for f in os.listdir(d) if f.endswith(".webp"))
            if names:
                out[p["id"]][key] = ["spin/%s_%s/%s" % (p["id"], key, n) for n in names]
    missing = [p["id"] for p in PIECES if not out[p["id"]]]
    if missing:
        raise SystemExit("no rendered frames for: %s - run spin_all/encode first"
                         % ", ".join(missing))
    return out


CSS = """
:root{
  --blue:#2FB4F5; --blue-d:#127BB0; --pink:#E85090; --gold:#E8B21F;
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
.ways{display:flex;gap:8px}
.way{width:30px;height:30px;border-radius:50%;border:2px solid var(--rule);
  cursor:pointer;padding:0}
.way[aria-pressed="true"]{border-color:var(--blue);box-shadow:0 0 0 3px rgba(47,180,245,.24)}
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
.routeBody{background:var(--wash);border:1px solid var(--rule);border-radius:18px;
  padding:24px 26px;margin-top:16px}
.routeBody h3{font-size:22px;font-weight:800}
.routeBody p{color:var(--ink-2);margin-top:10px}
.routeBody .verdict{margin-top:14px;font-weight:700}
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
  var piece = PIECES[0].id, way = "teal_silver", idx = 0, spinning = true;
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
    // a colourway with nothing rendered for this piece should not look available
    [].forEach.call(document.querySelectorAll('.way'), function(b){
      var ok = !!ways()[b.dataset.way];
      b.style.display = ok ? '' : 'none';
    });
  }
  function pickWay(w){
    way = w; set(list()); draw();
    [].forEach.call(document.querySelectorAll('.way'), function(b){
      b.setAttribute('aria-pressed', b.dataset.way === w ? 'true' : 'false'); });
  }

  [].forEach.call(document.querySelectorAll('.tab[data-piece]'), function(b){
    b.addEventListener('click', function(){ pick(b.dataset.piece); }); });
  [].forEach.call(document.querySelectorAll('.way'), function(b){
    b.addEventListener('click', function(){ pickWay(b.dataset.way); }); });

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

  // routes
  [].forEach.call(document.querySelectorAll('.tab[data-route]'), function(b){
    b.addEventListener('click', function(){
      [].forEach.call(document.querySelectorAll('.tab[data-route]'), function(o){
        o.setAttribute('aria-selected', o === b ? 'true' : 'false'); });
      [].forEach.call(document.querySelectorAll('.routeBody'), function(o){
        o.hidden = o.dataset.route !== b.dataset.route; });
    });
  });

  pick(piece); pickWay(way); go();
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
           "%3Crect width='32' height='32' rx='7' fill='%232FB4F5'/%3E"
           "%3Crect x='13' y='5' width='6' height='22' rx='3' fill='%23fff'/%3E"
           "%3Ccircle cx='16' cy='24' r='3' fill='%23E85090'/%3E%3C/svg%3E\">")


def build():
    fr = frames()
    tabs = "".join(
        '<button class="tab" data-piece="%s" aria-selected="%s">%s</button>'
        % (p["id"], "true" if i == 0 else "false", p["name"])
        for i, p in enumerate(PIECES))
    dots = "".join(
        '<button class="way" data-way="%s" title="%s" aria-pressed="%s" '
        'style="background:%s"></button>'
        % (k, n, "true" if k == "teal_silver" else "false", g)
        for k, n, s, g in WAYS)
    marks = "".join('<div class="mark"><h3>%s</h3><p>%s</p></div>' % (t, b)
                    for t, b in MARKS)
    rtabs = "".join(
        '<button class="tab" data-route="%s" aria-selected="%s">Route %s</button>'
        % (r[0], "true" if i == 0 else "false", r[0]) for i, r in enumerate(ROUTES))
    rbodies = "".join(
        '<div class="routeBody" data-route="%s"%s><h3 style="color:%s">%s</h3>'
        '<p>%s</p><p class="verdict" style="color:%s">%s</p></div>'
        % (r[0], "" if i == 0 else " hidden", r[2], r[1], r[3], r[2], r[4])
        for i, r in enumerate(ROUTES))
    tiers = "".join('<div class="tier"><b>%s</b><em>%s</em><span>%s</span></div>'
                    % t for t in TIERS)

    html = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>PUFF &times; Jerome Baker &mdash; the pre-roll that comes in glass</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="A hand-blown Jerome Baker tube for the Puff one-gram \
pre-roll. Concept pack: the piece, the set, the box, the compliance routes and the drop.">
<meta name="robots" content="noindex">
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
      <a href="#routes">Compliance</a>
      <a href="#drop">The drop</a>
      <a href="PUFF_x_JBD.pdf">PDF</a>
    </nav>
  </div>
</header>
<div class="drip"></div>

<div class="wrap hero" id="piece">
  <h1>The pre-roll<br>that comes in glass</h1>
  <p class="sub">Puff has sold more than twenty million pre-rolls, and every one went out
  in a printed plastic tube &mdash; the cheapest component in the package, and the only
  one the customer still has an hour later. This is that tube in hand-blown boro.</p>
  <div class="pills">
    <span class="pill">Concept pack</span>
    <span class="pill g">California + New York</span>
    <span class="pill k">Drag the piece to turn it</span>
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
          <div class="ways">%(dots)s</div>
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
    <p class="lede">None of this is a mould. Every one of these is a separate trip to the
    torch, which is why two tubes off the same bench are the same object and not the same
    piece &mdash; and that is what a limited drop is actually selling.</p>
    <div class="marks">%(marks)s</div>
  </div>
</section>

<section class="alt" id="box">
  <div class="wrap">
    <div class="eyebrow">The box</div>
    <h2 class="big">Rigid board, hinged lid,<br>magnetic clasp</h2>
    <p class="lede">A keepsake handed over in a paper bag is a keepsake nobody
    photographs. The lid is hinged full height and closes onto two disc magnets in the
    front lip; the insert is die-cut foam with one well, relieved at the front so the
    piece lifts straight out. Switch the viewer above to <b>In the box</b> to turn it
    over.</p>
    <div class="grid3">
      <div class="card"><h3>The insert carries the colour</h3><p>Glass is transmissive:
      behind a black insert the piece reads black. The lining is the one part of the box
      that is coloured, because it is what the piece is seen against.</p></div>
      <div class="card"><h3>The well is not a bore</h3><p>The marbles stand four
      millimetres proud of the wall, so the well is cut as a stadium &mdash; wide across
      the marbles, close on the other axis. That is also what stops the tube turning and
      facing its label at the lid.</p></div>
      <div class="card"><h3>It survives being kept</h3><p>53 &times; 48 &times; 169 mm,
      3.5 mm board, wrapped inside and out. It opens with a click and closes the same
      way.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="eyebrow">The premise</div>
    <h2 class="big">Twenty million pre-rolls.<br>Twenty million plastic tubes.</h2>
    <p class="lede">That tube already does the brand&rsquo;s hardest work &mdash; it
    carries the wordmark down its own axis, it sits on the counter, it comes out at the
    table. It gets thrown away because of what it is made of, and nothing else about it
    needs to change.</p>
    <div class="stats">
      <div class="stat"><b>20M+</b><span>pre-rolls sold, on Puff&rsquo;s own count</span></div>
      <div class="stat"><b>2</b><span>states they are legally sold in today &mdash;
        California and New York</span></div>
      <div class="stat"><b>79 g</b><span>of boro in the tube. The weight is half of why
        it feels worth keeping</span></div>
      <div class="stat"><b>0</b><span>of those plastic tubes kept</span></div>
    </div>
    <p class="note">Source: puffprerolls.com, August 2026.</p>
  </div>
</section>

<section class="alt" id="routes">
  <div class="wrap">
    <div class="eyebrow" style="color:#B8860B">The constraint</div>
    <h2 class="big">A cork-stopped tube<br>is not child-resistant</h2>
    <p class="lede">California and New York both require cannabis pre-rolls to reach the
    customer in child-resistant packaging. A glass tube with a cork in it is not that, and
    no amount of design makes it that. It decides the shape of the programme, so it is
    here rather than in a footnote.</p>
    <div class="tabs" style="margin-top:26px">%(rtabs)s</div>
    %(rbodies)s
    <p class="note"><b>Recommendation:</b> launch on Route B in both states while Route A
    is packed and tested, and keep Route C on the roadmap. Not legal advice &mdash;
    Puff&rsquo;s own compliance team signs the final pack.</p>
  </div>
</section>

<section id="drop">
  <div class="wrap">
    <div class="eyebrow">The drop</div>
    <h2 class="big">One release, two states, numbered</h2>
    <p class="lede">Numbering is the mechanic: a piece with a number on it is a thing to
    come back for, and a drop that sells out is a drop the second one is pre-ordered
    against. Allocation splits by door count, not evenly, and doors that already carry
    Puff go first.</p>
    <div class="tiers">%(tiers)s</div>
    <p class="note">Tier volumes are the bands to quote against, not a commitment. There
    is no price on this page on purpose: a quote before the final spec is a number that
    gets renegotiated. What moves it is glass weight, how many decoration passes stay in,
    anneal yield, the print, the closure and whether there is an outer.</p>
  </div>
</section>

<section class="cta">
  <div class="wrap">
    <h2 class="big">Say yes to the shape of it,<br>and we spec it</h2>
    <p class="lede">Four decisions and this becomes a quote and a sample.</p>
    <div class="steps">
      <div class="step"><b>1 &nbsp;Pick a route</b><span>B to launch, A packed behind it</span></div>
      <div class="step"><b>2 &nbsp;Pick a way</b><span>one colourway per state, or per strain</span></div>
      <div class="step"><b>3 &nbsp;Sign the lockup</b><span>Puff&rsquo;s own artwork replaces the stand-in</span></div>
      <div class="step"><b>4 &nbsp;Quote</b><span>against a tier, five working days</span></div>
    </div>
    <div class="btns">
      <a class="btn" href="mailto:%(contact)s?subject=PUFF%%20x%%20Jerome%%20Baker">Start the spec</a>
      <a class="btn k" href="PUFF_x_JBD.pdf">Download the pack (PDF)</a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    %(flock)s
    <p>Concept pack &mdash; not an offer. Renders are proposals; the hand-blown original
    stays the reference. Puff marks are set as stand-ins and shown for approval; no Puff
    artwork is reproduced here.</p>
    <p style="margin-top:10px">Jerome Baker Designs &middot;
      <a href="mailto:%(contact)s">%(contact)s</a> &middot;
      <a href="./">the rest of the programme</a></p>
  </div>
</footer>

<script>
window.__FRAMES__ = %(frames)s;
window.__PIECES__ = %(pieces)s;
</script>
<script>%(js)s</script>
</html>
""" % dict(css=CSS, js=JS, tabs=tabs, dots=dots, marks=marks, rtabs=rtabs,
           rbodies=rbodies, tiers=tiers, contact=CONTACT,
           lock=lockup("26px"), flock=lockup("22px"), favicon=FAVICON,
           frames=json.dumps(fr, separators=(",", ":")),
           pieces=json.dumps(PIECES, separators=(",", ":")))

    os.makedirs(SITE, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", OUT, "-", round(len(html) / 1024.0, 1), "KB")
    return OUT


if __name__ == "__main__":
    build()
