from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import math

W,H = 2800, 2040
BG=(250,250,248); INK=(28,30,34); DIM=(198,30,46); SUB=(92,98,106)
c=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(c)
def F(sz,b=False):
    return ImageFont.truetype("C:/Windows/Fonts/"+("arialbd.ttf" if b else "arial.ttf"),sz)

class Panel:
    def __init__(self, src, box, dest, target_h):
        im=Image.open(src).crop(box)
        s=target_h/im.height
        self.s=s; self.box=box; self.dest=dest
        im=im.resize((int(im.width*s),int(im.height*s)), Image.LANCZOS)
        self.im=ImageEnhance.Contrast(im).enhance(1.14)
    def px(self,x): return self.dest[0]+(x-self.box[0])*self.s
    def py(self,y): return self.dest[1]+(y-self.box[1])*self.s
    def paste(self):
        c.paste(self.im,self.dest)
        d.rectangle([self.dest[0]-1,self.dest[1]-1,self.dest[0]+self.im.width,self.dest[1]+self.im.height],outline=(212,212,209))

def arrow(p,q,size=11):
    ang=math.atan2(q[1]-p[1],q[0]-p[0])
    for a in (ang+2.6,ang-2.6):
        d.line([q,(q[0]+size*math.cos(a),q[1]+size*math.sin(a))],fill=DIM,width=3)

def dimline(p,q,text,off=0,side='v',fs=30,flip=False):
    if side=='h':
        y=p[1]+off
        d.line([(p[0],p[1]),(p[0],y)],fill=DIM,width=2)
        d.line([(q[0],q[1]),(q[0],y)],fill=DIM,width=2)
        d.line([(p[0],y),(q[0],y)],fill=DIM,width=3)
        arrow((q[0],y),(p[0],y)); arrow((p[0],y),(q[0],y))
        f=F(fs,True); tw=d.textlength(text,font=f); cx=(p[0]+q[0])/2
        ty = y-fs-12 if not flip else y+8
        d.rectangle([cx-tw/2-8,ty-4,cx+tw/2+8,ty+fs+6],fill=BG)
        d.text((cx-tw/2,ty),text,fill=DIM,font=f)
    else:
        x=p[0]+off
        d.line([(p[0],p[1]),(x,p[1])],fill=DIM,width=2)
        d.line([(q[0],q[1]),(x,q[1])],fill=DIM,width=2)
        d.line([(x,p[1]),(x,q[1])],fill=DIM,width=3)
        arrow((x,q[1]),(x,p[1])); arrow((x,p[1]),(x,q[1]))
        f=F(fs,True); tw=d.textlength(text,font=f); cy=(p[1]+q[1])/2
        tx = x+12 if not flip else x-tw-12
        d.rectangle([tx-6,cy-fs/2-6,tx+tw+6,cy+fs/2+6],fill=BG)
        d.text((tx,cy-fs/2),text,fill=DIM,font=f)

def leader(pt,tpt,text,fs=25,anchor='l'):
    d.line([pt,tpt],fill=DIM,width=2)
    d.ellipse([pt[0]-5,pt[1]-5,pt[0]+5,pt[1]+5],fill=DIM)
    f=F(fs,True); tw=d.textlength(text,font=f)
    tx=tpt[0]+8 if anchor=='l' else tpt[0]-tw-8
    d.rectangle([tx-6,tpt[1]-fs/2-6,tx+tw+6,tpt[1]+fs/2+6],fill=BG)
    d.text((tx,tpt[1]-fs/2),text,fill=DIM,font=f)

def cap(x,y,t): d.text((x,y),t,fill=INK,font=F(29,True))

# header
d.rectangle([0,0,W,120],fill=(22,24,28))
d.text((48,24),"JEROME BAKER DESIGNS  \u00b7  \u201cCLEARBOY\u201d HAMMER  \u2014  DIMENSIONAL SURVEY",fill=(255,255,255),font=F(40,True))
d.text((48,76),"Measured photogrammetrically from the ruler-referenced photos (IMG_5850\u20135859).  All figures in millimetres, \u00b12\u20133 mm.  Hand-blown \u2014 the head is not axisymmetric.",fill=(168,174,184),font=F(22))

# 1 front elevation
p1=Panel('pics/HI_5854.jpg',(700,760,2200,3430),(400,330),1120)
p1.paste(); cap(400,196,"1  \u00b7  FRONT ELEVATION")
hT,hB,hL,hR=878,1620,855,2010; fT,fB,fL,fR=3160,3320,1275,1690; sL,sR=1385,1569
dimline((p1.px(hL),p1.py(hT)),(p1.px(hL),p1.py(fB)),"140",off=-120,side='v',flip=True,fs=36)
dimline((p1.px(hL),p1.py(hT)),(p1.px(hR),p1.py(hT)),"68",off=-62,side='h',fs=30)
dimline((p1.px(hR),p1.py(hT)),(p1.px(hR),p1.py(hB)),"42",off=54,side='v',fs=30)
dimline((p1.px(sR),p1.py(hB)),(p1.px(sR),p1.py(fT)),"88",off=160,side='v',fs=30)
dimline((p1.px(sL),p1.py(2380)),(p1.px(sR),p1.py(2380)),"\u00d811",off=-160,side='h',fs=27)
dimline((p1.px(fL),p1.py(fB)),(p1.px(fR),p1.py(fB)),"\u00d824.5",off=76,side='h',fs=28)
dimline((p1.px(fR),p1.py(fT)),(p1.px(fR),p1.py(fB)),"7",off=160,side='v',fs=27)
leader((p1.px(1800),p1.py(1240)),(p1.px(hR)+70,p1.py(1020)),"carb \u00d83.5")
d.text((400,1466),"overall 140 mm  =  5\u00bd in",fill=SUB,font=F(26,True))

# 2 plan
p2=Panel('pics/HI_5859.jpg',(880,330,2520,1290),(1180,320),560)
p2.paste(); cap(1180,266,"2  \u00b7  PLAN / TOP VIEW")
dimline((p2.px(955),p2.py(420)),(p2.px(2395),p2.py(420)),"68\u201371",off=-56,side='h',fs=28)
dimline((p2.px(2395),p2.py(420)),(p2.px(2395),p2.py(1185)),"37",off=52,side='v',fs=28)
leader((p2.px(1560),p2.py(520)),(p2.px(1000),p2.py(1120)),"JBD sticker \u2014 deleted in the 3D model",fs=23)

# 5 head profile
p5=Panel('pics/HI_5850.jpg',(240,860,1160,2010),(2230,320),640)
p5.paste(); cap(2230,266,"3  \u00b7  HEAD PROFILE")
dimline((p5.px(330),p5.py(935)),(p5.px(330),p5.py(1930)),"62\u201368",off=-46,side='v',flip=True,fs=28)
dimline((p5.px(330),p5.py(1930)),(p5.px(1040),p5.py(1930)),"42",off=96,side='h',flip=True,fs=28)
leader((p5.px(690),p5.py(1170)),(p5.px(420),p5.py(1780)),"carb, 14 mm below rim",fs=23)

# 3 bowl end
p3=Panel('pics/HI_5856.jpg',(940,1620,1660,2300),(1180,1090),450)
p3.paste(); cap(1180,1036,"4  \u00b7  BOWL END (on head axis)")
dimline((p3.px(1008),p3.py(2255)),(p3.px(1508),p3.py(2255)),"\u00d836",off=62,side='h',fs=28)
dimline((p3.px(1104),p3.py(1780)),(p3.px(1450),p3.py(1780)),"bowl \u00d825",off=-180,side='h',fs=26)
leader((p3.px(1255),p3.py(1955)),(p3.px(1008)-30,p3.py(2140)),"throat \u00d85",fs=23,anchor='r')
leader((p3.px(1560),p3.py(1980)),(p3.px(1560)+16,p3.py(1700)),"carb boss \u00d811",fs=23)

# 4 mouthpiece
p4=Panel('pics/HI_5853.jpg',(1150,1640,1920,2260),(1900,1090),450)
p4.paste(); cap(1900,1036,"5  \u00b7  MOUTHPIECE / FOOT")
dimline((p4.px(1270),p4.py(2180)),(p4.px(1800),p4.py(2180)),"\u00d824.5",off=62,side='h',fs=28)
dimline((p4.px(1395),p4.py(1880)),(p4.px(1660),p4.py(1880)),"bore \u00d88",off=-120,side='h',flip=False,fs=26)

# ---- spec table ----
TY=1660
d.line([(60,TY-34),(W-60,TY-34)],fill=(200,200,197),width=2)
d.text((60,TY-92),"MEASURED SCHEDULE",fill=INK,font=F(30,True))
cols=[
 ("OVERALL",[("Overall height, standing on foot","140 mm  (5.51 in)"),
             ("Overall length, laid down","140 mm"),
             ("Head (chamber) length","68 mm  (62\u201371 range across views)"),
             ("Head max section","42 \u00d7 37 mm  (oval, hand-shaped)")]),
 ("STEM & FOOT",[("Stem tube OD","11 mm"),
             ("Stem bore ID","8 mm  (wall \u2248 1.6 mm)"),
             ("Exposed stem length","88 mm"),
             ("Foot / mouthpiece disc","\u00d824.5 \u00d7 7 mm thick")]),
 ("BOWL & CARB",[("Bowl opening ID at rim","25 mm"),
             ("Bowl throat / drop hole","5 mm"),
             ("Bowl depth to throat","18\u201320 mm"),
             ("Carb hole \u00b7 boss \u00b7 position","\u00d83.5 \u00b7 \u00d811 \u00b7 14 mm below rim")]),
]
x0=60
for title,rows in cols:
    d.text((x0,TY),title,fill=DIM,font=F(26,True))
    y=TY+48
    for k,v in rows:
        d.text((x0,y),k,fill=SUB,font=F(24))
        d.text((x0+470,y),v,fill=INK,font=F(24,True))
        y+=48
    x0+=930
note1="Method: scale set from the stainless rule in IMG_5855–5859 (mm graduations resolved to ±0.5 px/mm), cross-checked across four independent set-ups and corrected for stand-off parallax."
note2="Head length and section vary 5–10% between views because the piece is hand-blown and slightly oval — treat the head as a shaped solid, not a cylinder. Confirm with calipers before any tooling."
d.text((60,TY+270),note1,fill=SUB,font=F(21))
d.text((60,TY+302),note2,fill=SUB,font=F(21))
c.save('JBD_Clearboy_dimensions.png')
print("ok")
