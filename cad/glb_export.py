"""Export the pieces to web-ready GLBs with real glass materials.

trimesh writes a plain metallic-roughness GLB; we then patch the JSON chunk to add
KHR_materials_transmission / _ior / _volume so the piece renders as transmissive
glass in three.js, model-viewer, Babylon, Blender. Viewers that don't know the
extensions fall back to the blended base colour.

    python glb_export.py                       # every piece x every colourway
    python glb_export.py jar teal_silver
"""
import json, math, os, struct, sys
import trimesh

from mockups import PIECES, WAYS

OUT = "out"

# per-colourway GLB appearance: base colour, attenuation colour, attenuation distance mm
GLASS = {
    "teal_silver":  dict(body=(0.30, 0.72, 0.72), frit=(0.10, 0.50, 0.47),
                         atten=(0.32, 0.78, 0.76), dist=13.0),
    "magenta_gold": dict(body=(0.82, 0.30, 0.62), frit=(0.60, 0.10, 0.42),
                         atten=(0.86, 0.30, 0.62), dist=13.0),
}
MARBLE_COLOUR = (0.94, 0.96, 0.97)
CORK_COLOUR = (0.78, 0.63, 0.42)      # opaque - the cork is not glass


def load(path, smooth_angle=36.0):
    m = trimesh.load(path, force="mesh")
    m.merge_vertices()
    try:
        m = m.smoothed(angle=math.radians(smooth_angle))
    except Exception:
        pass
    return m


def build_scene(piece, colour):
    """Y-up, centred, in metres - the glTF convention."""
    p = PIECES[piece]
    T = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])
    T[:3, :3] *= 0.001
    scene = trimesh.Scene()
    parts = [("body", p["body"], colour["body"]),
             ("frit", p["frit"], colour["frit"]),
             ("marbles", p["marbles"], MARBLE_COLOUR)]
    if p.get("cork"):
        parts.append(("cork", p["cork"], CORK_COLOUR))
    for name, path, c in parts:
        mesh = load(path)
        mesh.apply_transform(T)
        mesh.visual = trimesh.visual.TextureVisuals(
            material=trimesh.visual.material.PBRMaterial(
                name=name, baseColorFactor=[c[0], c[1], c[2], 1.0],
                metallicFactor=0.0, roughnessFactor=0.06, doubleSided=False))
        scene.add_geometry(mesh, geom_name=name, node_name=name)
    b = scene.bounds
    mid = (b[0] + b[1]) / 2.0
    for nm in list(scene.graph.nodes_geometry):
        M, _ = scene.graph[nm]
        M = M.copy(); M[:3, 3] -= mid
        scene.graph.update(frame_to=nm, matrix=M)
    return scene


def patch_glass(glb_bytes, colour):
    magic, ver, total = struct.unpack("<III", glb_bytes[:12])
    off, chunks = 12, []
    while off < total:
        clen, ctype = struct.unpack("<II", glb_bytes[off:off + 8])
        chunks.append([ctype, glb_bytes[off + 8:off + 8 + clen]])
        off += 8 + clen
    j = json.loads(chunks[0][1].decode("utf-8"))

    exts = ["KHR_materials_transmission", "KHR_materials_ior", "KHR_materials_volume"]
    j["extensionsUsed"] = sorted(set(j.get("extensionsUsed", [])) | set(exts))

    for m in j.get("materials", []):
        name = (m.get("name") or "")
        if name.startswith("cork"):
            m["alphaMode"] = "OPAQUE"
            m["pbrMetallicRoughness"]["roughnessFactor"] = 0.85
            continue                                   # cork stays a plain matte solid
        marble = name.startswith("marbles")
        thick = 0.0035 if name.startswith("body") else 0.0025
        m["alphaMode"] = "OPAQUE"
        m["doubleSided"] = False
        m["extensions"] = {
            "KHR_materials_transmission": {"transmissionFactor": 1.0},
            "KHR_materials_ior": {"ior": 1.474},              # borosilicate
            "KHR_materials_volume": {
                "thicknessFactor": thick,
                "attenuationDistance": (0.25 if marble else colour["dist"] / 1000.0),
                "attenuationColor": [0.97, 0.98, 0.99] if marble
                                    else list(colour["atten"]),
            },
        }

    blob = json.dumps(j, separators=(",", ":")).encode("utf-8")
    blob += b" " * ((4 - len(blob) % 4) % 4)
    chunks[0][1] = blob
    body = b"".join(struct.pack("<II", len(c[1]), c[0]) + c[1] for c in chunks)
    return struct.pack("<III", magic, ver, 12 + len(body)) + body


def export(piece, key):
    colour = GLASS[key]
    raw = trimesh.exchange.gltf.export_glb(build_scene(piece, colour),
                                           include_normals=True)
    path = os.path.join(OUT, "%s_%s.glb" % (piece, key))
    with open(path, "wb") as f:
        f.write(patch_glass(raw, colour))
    print("wrote %s  %.2f MB" % (path, os.path.getsize(path) / 1e6))
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    args = sys.argv[1:]
    pieces = [a for a in args if a in PIECES] or list(PIECES)
    ways = [a for a in args if a in WAYS] or list(WAYS)
    for pc in pieces:
        for k in ways:
            export(pc, k)
