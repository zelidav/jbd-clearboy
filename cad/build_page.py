import io, os

HEAD = """<title>Clearboy Hammer &mdash; Dimensional Survey</title>
<style>
:root{
  --paper:#F6F7F6; --plate:#FFFFFF; --ink:#14181C; --muted:#6E7A78;
  --rule:#C9CFCC; --rule-soft:#E3E7E5; --red:#C31E2C; --teal:#3E7370;
  --shadow:0 1px 2px rgba(20,24,28,.06),0 8px 28px rgba(20,24,28,.06);
}
@media (prefers-color-scheme:dark){
  :root{--paper:#0E1114; --plate:#161A1E; --ink:#E4E8E6; --muted:#93A09D;
        --rule:#2C3439; --rule-soft:#222A2E; --red:#F0616C; --teal:#6FA9A4;
        --shadow:0 1px 2px rgba(0,0,0,.5),0 10px 30px rgba(0,0,0,.35);}
}
:root[data-theme="dark"]{--paper:#0E1114; --plate:#161A1E; --ink:#E4E8E6; --muted:#93A09D;
  --rule:#2C3439; --rule-soft:#222A2E; --red:#F0616C; --teal:#6FA9A4;
  --shadow:0 1px 2px rgba(0,0,0,.5),0 10px 30px rgba(0,0,0,.35);}
:root[data-theme="light"]{--paper:#F6F7F6; --plate:#FFFFFF; --ink:#14181C; --muted:#6E7A78;
  --rule:#C9CFCC; --rule-soft:#E3E7E5; --red:#C31E2C; --teal:#3E7370;
  --shadow:0 1px 2px rgba(20,24,28,.06),0 8px 28px rgba(20,24,28,.06);}

*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:400 16px/1.6 ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;
  -webkit-font-smoothing:antialiased;padding:clamp(14px,3vw,40px)}
.sheet{max-width:1500px;margin:0 auto;border:1px solid var(--rule);
  background:var(--plate);box-shadow:var(--shadow);position:relative}
.sheet::after{content:"";position:absolute;inset:6px;border:1px solid var(--rule-soft);pointer-events:none}

.eyebrow{display:flex;flex-wrap:wrap;gap:10px 26px;align-items:baseline;
  padding:16px clamp(16px,2.4vw,32px);border-bottom:1px solid var(--rule)}
.tag{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:11.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.tag b{color:var(--red);font-weight:600}

.masthead{padding:clamp(20px,3vw,38px) clamp(16px,2.4vw,32px) clamp(14px,2vw,24px)}
h1{margin:0;font-size:clamp(28px,4.6vw,54px);line-height:1.02;letter-spacing:-.018em;
  font-weight:800;text-wrap:balance;font-stretch:condensed}
h1 .thin{font-weight:300;color:var(--muted)}
.deck{margin:14px 0 0;max-width:66ch;color:var(--muted);font-size:15.5px}

figure{margin:0;padding:0 clamp(10px,2vw,26px) clamp(14px,2vw,22px)}
.plate{display:block;width:100%;height:auto;border:1px solid var(--rule)}
figcaption{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:11.5px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding-top:10px}

.zone{display:grid;grid-template-columns:1.35fr 1fr;border-top:1px solid var(--rule)}
@media (max-width:880px){.zone{grid-template-columns:1fr}}
.col{padding:clamp(18px,2.4vw,30px) clamp(16px,2.4vw,32px)}
.col+.col{border-left:1px solid var(--rule)}
@media (max-width:880px){.col+.col{border-left:0;border-top:1px solid var(--rule)}}
h2{margin:0 0 18px;font-size:12px;letter-spacing:.2em;text-transform:uppercase;
  font-weight:700;color:var(--red)}
.tblwrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14.5px}
caption{text-align:left;font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:11px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--teal);padding:18px 0 8px;font-weight:600}
caption:first-of-type{padding-top:0}
th,td{text-align:left;padding:7px 14px 7px 0;border-bottom:1px solid var(--rule-soft);vertical-align:baseline}
th{font-weight:400;color:var(--muted)}
td{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-variant-numeric:tabular-nums;
  font-weight:600;white-space:nowrap}
td .note{font-family:inherit;font-weight:400;color:var(--muted);font-size:12.5px;white-space:normal}
.col p{margin:0 0 14px;font-size:15px;color:var(--muted)}
.col p:last-child{margin-bottom:0}
.col p strong{color:var(--ink);font-weight:600}
ul{margin:0;padding-left:18px;color:var(--muted);font-size:15px}
li{margin-bottom:9px}
li strong{color:var(--ink);font-weight:600}

.titleblock{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--rule)}
@media (max-width:700px){.titleblock{grid-template-columns:repeat(2,1fr)}}
.cell{padding:14px clamp(16px,2.4vw,32px)}
.cell+.cell{border-left:1px solid var(--rule-soft)}
@media (max-width:700px){.cell:nth-child(odd){border-left:0}
  .cell:nth-child(n+3){border-top:1px solid var(--rule-soft)}}
.cell .k{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:10.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:5px}
.cell .v{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:14px;
  font-weight:600;font-variant-numeric:tabular-nums}
</style>
"""

BODY = """
<div class="sheet">
  <div class="eyebrow">
    <span class="tag"><b>JBD</b> &nbsp;Jerome Baker Designs</span>
    <span class="tag">Sheet 1 of 1</span>
    <span class="tag">Units: millimetres</span>
    <span class="tag">Tolerance &plusmn;2&ndash;3</span>
    <span class="tag">Source: IMG_5850&ndash;5859</span>
  </div>

  <div class="masthead">
    <h1>&ldquo;Clearboy&rdquo; Hammer<br><span class="thin">Dimensional Survey</span></h1>
    <p class="deck">Every measurement below was read off the stainless rule that appears in five of the
    ten reference photographs, then cross-checked between independent set-ups and corrected for
    stand-off parallax. This is the geometry the 3D model gets cut from &mdash; sticker deleted.</p>
  </div>

  <figure>
    <img class="plate" src="data:image/jpeg;base64,__B64__" alt="Annotated five-view dimensional survey of the clear glass hammer pipe with a measured schedule">
    <figcaption>Plate 1 &mdash; five views, dimensioned. Red figures are millimetres.</figcaption>
  </figure>

  <div class="zone">
    <div class="col">
      <h2>Measured schedule</h2>
      <div class="tblwrap">
      <table>
        <caption>Overall</caption>
        <tbody>
          <tr><th scope="row">Height standing on foot</th><td>140 <span class="note">(5.51 in)</span></td></tr>
          <tr><th scope="row">Length laid down</th><td>140</td></tr>
          <tr><th scope="row">Head (chamber) length</th><td>68 <span class="note">62&ndash;71 across views</span></td></tr>
          <tr><th scope="row">Head maximum section</th><td>42 &times; 37 <span class="note">oval, hand-shaped</span></td></tr>
        </tbody>
        <caption>Stem &amp; foot</caption>
        <tbody>
          <tr><th scope="row">Stem tube OD</th><td>&Oslash;11</td></tr>
          <tr><th scope="row">Stem bore ID</th><td>&Oslash;8 <span class="note">wall &asymp; 1.6</span></td></tr>
          <tr><th scope="row">Exposed stem length</th><td>88</td></tr>
          <tr><th scope="row">Foot / mouthpiece disc</th><td>&Oslash;24.5 &times; 7</td></tr>
        </tbody>
        <caption>Bowl &amp; carb</caption>
        <tbody>
          <tr><th scope="row">Bowl opening ID at rim</th><td>&Oslash;25</td></tr>
          <tr><th scope="row">Bowl throat / drop hole</th><td>&Oslash;5</td></tr>
          <tr><th scope="row">Bowl depth to throat</th><td>18&ndash;20</td></tr>
          <tr><th scope="row">Carb hole</th><td>&Oslash;3.5</td></tr>
          <tr><th scope="row">Carb boss (raised ring)</th><td>&Oslash;11</td></tr>
          <tr><th scope="row">Carb centre below rim</th><td>14</td></tr>
        </tbody>
      </table>
      </div>
    </div>

    <div class="col">
      <h2>How it was measured</h2>
      <p>Scale came from the millimetre graduations on the stainless rule, resolved by intensity
      profile to about half a pixel per millimetre &mdash; between <strong>13.0 and 19.0 px/mm</strong>
      depending on the set-up.</p>
      <p>Four set-ups were reconciled against each other. The flat-lay shots agree to within 1&nbsp;%
      on stem length; the standing shot reads roughly 5&nbsp;% short because the rule sits at a
      different stand-off than the piece, so it was weighted down.</p>

      <h2 style="margin-top:26px">Read before you model</h2>
      <ul>
        <li><strong>The head is not a cylinder.</strong> It is hand-blown, slightly oval and waisted,
        which is why its length reads 62&ndash;71 depending on which way you look at it. Loft it;
        don&rsquo;t revolve it.</li>
        <li><strong>Head length and section are the soft numbers.</strong> Everything on the stem and
        foot is tight; the head varies 5&ndash;10&nbsp;% between views.</li>
        <li><strong>The JBD sticker is not geometry.</strong> It is deleted in the model &mdash; the
        surface under it is plain clear glass.</li>
        <li><strong>Wall thickness is inferred,</strong> not directly measured. The rim reads thick
        (4&ndash;5&nbsp;mm); the body is nearer 3&nbsp;mm.</li>
      </ul>
    </div>
  </div>

  <div class="titleblock">
    <div class="cell"><span class="k">Piece</span><span class="v">Clearboy Hammer</span></div>
    <div class="cell"><span class="k">Material</span><span class="v">Clear borosilicate</span></div>
    <div class="cell"><span class="k">Method</span><span class="v">Photogrammetric</span></div>
    <div class="cell"><span class="k">Status</span><span class="v">For review</span></div>
  </div>
</div>
"""

b64 = open('img_b64.txt').read().strip()
out = HEAD + BODY.replace('__B64__', b64)
open('clearboy_dims.html', 'w', encoding='utf-8').write(out)
print(os.path.getsize('clearboy_dims.html'))
