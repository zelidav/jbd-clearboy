"""Turn rendered turntable frames into web assets.

  docs/video/<key>.mp4     - 3s seamless loop, h264, faststart (24 fps x 72 frames)
  docs/video/<key>.jpg     - poster frame
  docs/spin/<key>/NN.webp  - decimated, downscaled frames for the drag-to-spin viewer

    python encode.py                 # every colourway found under frames/
    python encode.py teal magenta
"""
import os, subprocess, sys
import imageio_ffmpeg
from PIL import Image

FRAMES, VIDEO, SPIN = "frames", "docs/video", "docs/spin"
FPS = 24
SPIN_EVERY = 2          # 72 renders -> 36 spinner frames
SPIN_W = 520
SPIN_Q = 80
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def keys():
    return sorted(d for d in os.listdir(FRAMES)
                  if os.path.isdir(os.path.join(FRAMES, d)) and not d.startswith("_"))


def mp4(key):
    os.makedirs(VIDEO, exist_ok=True)
    src = os.path.join(FRAMES, key, "%03d.png")
    dst = os.path.join(VIDEO, key + ".mp4")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", src,
           "-c:v", "libx264", "-preset", "slow", "-crf", "21",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", dst]
    subprocess.run(cmd, check=True)
    poster = Image.open(os.path.join(FRAMES, key, "000.png")).convert("RGB")
    poster.save(os.path.join(VIDEO, key + ".jpg"), quality=88, optimize=True)
    return dst, os.path.getsize(dst)


def spin(key):
    out = os.path.join(SPIN, key)
    os.makedirs(out, exist_ok=True)
    src = os.path.join(FRAMES, key)
    names = sorted(f for f in os.listdir(src) if f.endswith(".png"))
    total = 0
    n = 0
    for i, f in enumerate(names):
        if i % SPIN_EVERY:
            continue
        im = Image.open(os.path.join(src, f)).convert("RGB")
        h = round(im.height * SPIN_W / im.width)
        im = im.resize((SPIN_W, h), Image.LANCZOS)
        p = os.path.join(out, "%02d.webp" % n)
        im.save(p, "WEBP", quality=SPIN_Q, method=6)
        total += os.path.getsize(p)
        n += 1
    return n, total


if __name__ == "__main__":
    ks = sys.argv[1:] or keys()
    for k in ks:
        v, vs = mp4(k)
        n, ss = spin(k)
        print("%-11s mp4 %5.0f KB   spin %d frames %5.0f KB"
              % (k, vs / 1024, n, ss / 1024), flush=True)
