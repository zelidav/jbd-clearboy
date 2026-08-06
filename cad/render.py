"""Studio glass renderer for the Clearboy hammer.

Photographic-clear-glass compositor rather than a path tracer:
  1. studio sweep background
  2. tint pass      - front faces, Beer-Lambert over the real front/back thickness
  3. density pass   - every surface, unsorted, multiplied in; each grazing crossing
                      lays down a contour line, which is exactly what reads as glass
                      in a white-sweep product shot (bore walls, chamber, funnel)
  4. specular pass  - front faces, additive softbox reflections off a procedural env
"""
import math, os, numpy as np, moderngl, trimesh
from PIL import Image, ImageDraw, ImageFont

SS = 2

VERT = """
#version 330
in vec3 in_pos; in vec3 in_norm;
uniform mat4 mvp; uniform mat4 model; uniform mat4 view;
out vec3 v_wpos; out vec3 v_wnorm; out float v_vdepth;
out vec3 v_opos; out vec3 v_onorm;
void main(){
    vec4 wp = model * vec4(in_pos,1.0);
    v_wpos = wp.xyz; v_wnorm = mat3(model)*in_norm;
    v_opos = in_pos;  v_onorm = in_norm;
    v_vdepth = -(view*wp).z;
    gl_Position = mvp * vec4(in_pos,1.0);
}"""

BACK_FRAG = """
#version 330
in vec3 v_wnorm; in float v_vdepth; out vec4 f_out;
void main(){ f_out = vec4(normalize(v_wnorm), v_vdepth); }"""

BG_VERT = """
#version 330
in vec2 in_pos; out vec2 v_uv;
void main(){ v_uv = in_pos*0.5+0.5; gl_Position = vec4(in_pos,0.0,1.0); }"""

BG_FRAG = """
#version 330
in vec2 v_uv; out vec4 f_out;
uniform vec3 c_top; uniform vec3 c_bot; uniform vec3 shadow;
void main(){
    float t = pow(clamp(v_uv.y,0.0,1.0),0.9);
    vec3 col = mix(c_bot, c_top, t);
    col = mix(col, c_bot*0.90, smoothstep(0.26,0.0,v_uv.y)*0.7);
    vec2 p = vec2((v_uv.x-shadow.x), (v_uv.y-shadow.z)*3.4);
    col *= 1.0 - 0.46*smoothstep(1.0,0.0,length(p)/max(shadow.y,1e-3));
    vec2 q = v_uv-0.5; col *= 1.0 - 0.20*dot(q,q)*2.0;
    f_out = vec4(col,1.0);
}"""

COMMON = """
uniform vec3 camPos;
float ndotv(vec3 N, vec3 P){
    vec3 V = normalize(camPos-P);
    return abs(dot(normalize(N),V));
}
vec3 envMap(vec3 d){
    float t = clamp(d.z*0.5+0.5,0.0,1.0);
    vec3 base = mix(vec3(0.24,0.25,0.27), vec3(0.97,0.98,1.0), pow(t,0.7));
    float key  = pow(max(dot(d,normalize(vec3( 0.28,-0.74, 0.61))),0.0), 9.0);
    float fill = pow(max(dot(d,normalize(vec3(-0.82,-0.30, 0.26))),0.0), 22.0);
    float rim  = pow(max(dot(d,normalize(vec3( 0.60, 0.66, 0.30))),0.0), 46.0);
    float strp = pow(max(dot(d,normalize(vec3(-0.06,-0.22, 0.97))),0.0), 320.0);
    return base + key*1.05 + vec3(0.95,0.97,1.0)*fill*0.62
                + vec3(1.0,0.96,0.90)*rim*0.75 + vec3(1.0)*strp*2.6;
}"""

TINT_FRAG = """
#version 330
in vec3 v_wpos; in vec3 v_wnorm; in float v_vdepth;
out vec4 f_out;
uniform sampler2D backTex; uniform vec2 res;
uniform vec3 absorb; uniform float fume;
uniform vec3 fumeWarm; uniform vec3 fumeCool; uniform float minThick;
""" + COMMON + """
void main(){
    vec2 uv = gl_FragCoord.xy/res;
    float thick = clamp(texture(backTex,uv).w - v_vdepth, 0.0, 60.0);
    thick = max(thick, minThick);          // floor keeps thin edges from going clear
    vec3 tint = exp(-absorb*thick);
    if(fume > 0.0){
        // silver/gold fume is an interference coat: the shift follows viewing angle
        float g = pow(1.0-ndotv(v_wnorm,v_wpos), 1.8);
        tint *= mix(fumeCool, fumeWarm, g);
    }
    f_out = vec4(tint,1.0);
}"""

DENS_FRAG = """
#version 330
in vec3 v_wpos; in vec3 v_wnorm; out vec4 f_out;
uniform vec3 lineCol; uniform float kPow; uniform float kAmt;
""" + COMMON + """
void main(){
    float ndv = ndotv(v_wnorm, v_wpos);
    float dens = kAmt*pow(1.0-ndv, kPow) + 0.030*pow(1.0-ndv, 1.4);
    dens = clamp(dens, 0.0, 0.97);
    f_out = vec4(mix(vec3(1.0), lineCol, dens), 1.0);
}"""

SPEC_FRAG = """
#version 330
in vec3 v_wpos; in vec3 v_wnorm; out vec4 f_out;
uniform float specAmt;
""" + COMMON + """
void main(){
    vec3 N = normalize(v_wnorm);
    vec3 V = normalize(camPos-v_wpos);
    if(dot(N,V) < 0.0) N = -N;
    float ndv = clamp(dot(N,V),0.0,1.0);
    float F = 0.045 + 0.955*pow(1.0-ndv,5.0);
    vec3 e = envMap(normalize(reflect(-V,N)));
    vec3 hi = max(e-0.99, 0.0)*1.35 + vec3(1.0)*pow(1.0-ndv,14.0)*0.75;
    f_out = vec4(hi*specAmt*(0.35+F), 1.0);
}"""

DECAL_FRAG = """
#version 330
in vec3 v_wpos; in vec3 v_wnorm; in vec3 v_opos; in vec3 v_onorm; out vec4 f_out;
uniform sampler2D decalTex; uniform vec2 decalZ; uniform float decalR;
""" + COMMON + """
void main(){
    // object-space planar decal projector: prints on the -Y face of the stem
    vec3 ON = normalize(v_onorm);
    if(ON.y > -0.34) discard;
    if(v_opos.z < decalZ.x || v_opos.z > decalZ.y) discard;
    float halfW = decalR*0.80;
    if(abs(v_opos.x) > halfW) discard;
    float u = (v_opos.z - decalZ.x)/(decalZ.y - decalZ.x);
    float vv = (v_opos.x + halfW)/(2.0*halfW);
    vec4 dc = texture(decalTex, vec2(u, vv));
    if(dc.a < 0.05) discard;
    vec3 N = normalize(v_wnorm); vec3 V = normalize(camPos - v_wpos);
    float face = clamp(dot(N,V), 0.0, 1.0);
    if(face < 0.10) discard;
    float sh = 0.86 + 0.48*pow(max(dot(N,normalize(vec3(0.28,-0.74,0.61))),0.0),6.0);
    f_out = vec4(clamp(dc.rgb*sh,0.0,1.0), dc.a*smoothstep(0.10,0.34,face)*(-ON.y));
}"""


def load(path, smooth_angle=36.0):
    m = trimesh.load(path, force='mesh')
    m.merge_vertices()
    try:
        m = m.smoothed(angle=math.radians(smooth_angle))
    except Exception:
        pass
    return (np.asarray(m.vertices, 'f4'), np.asarray(m.vertex_normals, 'f4'),
            np.asarray(m.faces, 'i4'))


def look_at(eye, target, up=(0, 0, 1)):
    eye = np.asarray(eye, 'f4'); target = np.asarray(target, 'f4'); up = np.asarray(up, 'f4')
    f = target-eye; f /= np.linalg.norm(f)
    s = np.cross(f, up); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    M = np.eye(4, dtype='f4'); M[0, :3], M[1, :3], M[2, :3] = s, u, -f
    M[:3, 3] = -M[:3, :3] @ eye
    return M


def persp(fovy, aspect, zn, zf):
    t = 1.0/math.tan(math.radians(fovy)/2)
    M = np.zeros((4, 4), 'f4')
    M[0, 0] = t/aspect; M[1, 1] = t
    M[2, 2] = (zf+zn)/(zn-zf); M[2, 3] = 2*zf*zn/(zn-zf); M[3, 2] = -1
    return M


def rotz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], 'f4')


def make_decal(text, w=2400, h=300, color=(250, 250, 250), band=0.30):
    """u along the stem, v around it. Text sits in a band on one side."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    path = "C:/Windows/Fonts/arialbd.ttf"
    size = int(h*band*1.35)
    f = ImageFont.truetype(path, size)
    tw = d.textlength(text, font=f)
    if tw > w*0.88:
        size = int(size*w*0.88/tw); f = ImageFont.truetype(path, size)
        tw = d.textlength(text, font=f)
    d.text(((w-tw)/2, h*0.5-size*0.60), text, font=f, fill=color+(255,))
    return img


class Renderer:
    def __init__(self, W, H):
        self.W, self.H = W*SS, H*SS
        self.ctx = ctx = moderngl.create_standalone_context(require=330)
        self.progs = {}
        for k, fs in (('back', BACK_FRAG), ('tint', TINT_FRAG), ('dens', DENS_FRAG),
                      ('spec', SPEC_FRAG), ('decal', DECAL_FRAG)):
            self.progs[k] = ctx.program(vertex_shader=VERT, fragment_shader=fs)
        self.bg_prog = ctx.program(vertex_shader=BG_VERT, fragment_shader=BG_FRAG)
        quad = np.array([-1, -1, 3, -1, -1, 3], 'f4')
        self.quad = ctx.vertex_array(self.bg_prog, [(ctx.buffer(quad), '2f', 'in_pos')])
        self.bg_tex = ctx.texture((self.W, self.H), 3, dtype='f2')
        self.bg_fbo = ctx.framebuffer([self.bg_tex])
        self.back_tex = ctx.texture((self.W, self.H), 4, dtype='f4')
        self.back_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.back_fbo = ctx.framebuffer([self.back_tex],
                                        ctx.depth_texture((self.W, self.H)))
        self.main_tex = ctx.texture((self.W, self.H), 3, dtype='f2')
        self.main_fbo = ctx.framebuffer([self.main_tex],
                                        ctx.depth_renderbuffer((self.W, self.H)))
        self.objs = []
        self.decal = None

    def add(self, path, absorb=(0, 0, 0), fume=0.0, line=(0.10, 0.11, 0.13),
            kAmt=0.80, kPow=3.4, spec=1.0, decal=False, solid=False, min_thick=0.0,
            fume_warm=(1.00, 0.83, 0.58), fume_cool=(0.74, 0.83, 1.00), smooth=36.0):
        """solid=True depth-tests the density pass, so only the surface facing the
        camera draws contour - the piece stops reading as an X-ray of its own walls."""
        v, n, f = load(path, smooth)
        vbo = self.ctx.buffer(np.hstack([v, n]).astype('f4').tobytes())
        ibo = self.ctx.buffer(f.astype('i4').tobytes())
        vaos = {k: self.ctx.vertex_array(p, [(vbo, '3f 3f', 'in_pos', 'in_norm')], ibo)
                for k, p in self.progs.items()}
        self.objs.append(dict(vaos=vaos, absorb=absorb, fume=fume, line=line,
                              kAmt=kAmt, kPow=kPow, spec=spec, decal=decal,
                              solid=solid, min_thick=min_thick,
                              fume_warm=fume_warm, fume_cool=fume_cool))

    def set_decal(self, img, z0, z1, r):
        t = self.ctx.texture(img.size, 4, img.tobytes())
        t.filter = (moderngl.LINEAR, moderngl.LINEAR)
        t.repeat_x = False; t.repeat_y = True
        self.decal = (t, z0, z1, r)

    def _mats(self, angle, cam_r, elev, target, fov):
        el = math.radians(elev)
        eye = np.array([0.0, -cam_r*math.cos(el), target[2]+cam_r*math.sin(el)], 'f4')
        view = look_at(eye, target)
        proj = persp(fov, self.W/self.H, 10.0, 5000.0)
        model = rotz(angle)
        return eye, model, view, proj @ view @ model

    def frame(self, angle, cam_r=780.0, elev=5.0, target=(0, 0, 74), fov=17.0,
              bg=((0.965, 0.968, 0.973), (0.795, 0.808, 0.822)), shadow=(0.5, 0.30, 0.075)):
        ctx = self.ctx
        eye, model, view, mvp = self._mats(angle, cam_r, elev, target, fov)

        def setmats(p):
            p['mvp'].write(mvp.T.astype('f4').tobytes())
            p['model'].write(model.T.astype('f4').tobytes())
            p['view'].write(view.T.astype('f4').tobytes())
            if 'camPos' in p: p['camPos'].value = tuple(float(x) for x in eye)

        # 1 background
        self.bg_fbo.use(); ctx.disable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
        self.bg_prog['c_top'].value = bg[0]; self.bg_prog['c_bot'].value = bg[1]
        self.bg_prog['shadow'].value = shadow
        self.quad.render(moderngl.TRIANGLES)

        # 2 back-face depth for thickness
        self.back_fbo.use(); ctx.clear(0, 0, 1, 1e5)
        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE); ctx.cull_face = 'front'
        setmats(self.progs['back'])
        for o in self.objs: o['vaos']['back'].render(moderngl.TRIANGLES)

        # 3 composite
        self.main_fbo.use(); ctx.clear(0, 0, 0, 1)
        ctx.disable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
        self.bg_prog['c_top'].value = bg[0]; self.bg_prog['c_bot'].value = bg[1]
        self.quad.render(moderngl.TRIANGLES)

        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.ZERO, moderngl.SRC_COLOR)      # multiply

        # 3a tint (front faces, depth on)
        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE); ctx.cull_face = 'back'
        p = self.progs['tint']; setmats(p)
        self.back_tex.use(1); p['backTex'].value = 1; p['res'].value = (self.W, self.H)
        for o in self.objs:
            p['absorb'].value = o['absorb']; p['fume'].value = o['fume']
            p['fumeWarm'].value = o['fume_warm']; p['fumeCool'].value = o['fume_cool']
            p['minThick'].value = o['min_thick']
            o['vaos']['tint'].render(moderngl.TRIANGLES)

        # 3b density - every surface for see-through glass, front only for solid colour
        p = self.progs['dens']; setmats(p); ctx.depth_func = '<='
        for o in self.objs:
            if o['solid']:
                ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE); ctx.cull_face = 'back'
            else:
                ctx.disable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
            p['lineCol'].value = o['line']; p['kAmt'].value = o['kAmt']
            p['kPow'].value = o['kPow']
            o['vaos']['dens'].render(moderngl.TRIANGLES)

        # 3c specular (front faces, additive)
        ctx.blend_func = (moderngl.ONE, moderngl.ONE)
        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE); ctx.cull_face = 'back'
        ctx.depth_func = '<='
        p = self.progs['spec']; setmats(p)
        for o in self.objs:
            p['specAmt'].value = o['spec']
            o['vaos']['spec'].render(moderngl.TRIANGLES)

        # 3d enamel print
        if self.decal:
            ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)
            t, z0, z1, r = self.decal
            p = self.progs['decal']; setmats(p)
            t.use(3); p['decalTex'].value = 3
            p['decalZ'].value = (z0, z1); p['decalR'].value = r
            for o in self.objs:
                if o['decal']: o['vaos']['decal'].render(moderngl.TRIANGLES)

        ctx.disable(moderngl.BLEND)
        img = np.frombuffer(self.main_fbo.read(components=3, dtype='f2'), 'f2') \
                .reshape(self.H, self.W, 3).astype('f4')
        img = np.clip(np.nan_to_num(img, nan=0.0), 0, 1)
        out = Image.fromarray((img*255+0.5).astype('u1')).transpose(Image.FLIP_TOP_BOTTOM)
        return out.resize((self.W//SS, self.H//SS), Image.LANCZOS) if SS > 1 else out
