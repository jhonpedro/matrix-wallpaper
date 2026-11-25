# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Render a seamless looping Matrix digital rain video."""

import argparse
import math
import string
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--width", type=int, default=1920)
p.add_argument("--height", type=int, default=1080)
p.add_argument("--cell", type=int, default=24, help="glyph cell size in pixels")
p.add_argument("--fps", type=int, default=30)
p.add_argument("--seconds", type=int, default=20, help="loop length")
p.add_argument("--drops", type=int, default=2, help="drops per column")
p.add_argument("--color", default="00ff46", help="rain colour as hex RGB")
p.add_argument("--font", default="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
p.add_argument("--seed", type=int, default=1)
p.add_argument("-o", "--output", default="matrix.mp4")
a = p.parse_args()

rng = np.random.default_rng(a.seed)
L = a.fps * a.seconds
cols, rows = math.ceil(a.width / a.cell), math.ceil(a.height / a.cell)

font = ImageFont.truetype(a.font, int(a.cell * 0.8))
atlas = []
for ch in CHARS:
    img = Image.new("L", (a.cell, a.cell))
    ImageDraw.Draw(img).text((a.cell / 2, a.cell / 2), ch, fill=255, font=font, anchor="mm")
    atlas.append(np.asarray(img, np.float32) / 255)
atlas = np.stack(atlas)

# Each drop travels k full cycles per loop, so its position at frame L equals frame 0.
tail = rng.integers(8, 30, (a.drops, cols))
cycle = rows + tail + rng.integers(0, rows, (a.drops, cols))
speed = rng.integers(1, 4, (a.drops, cols)) * cycle / L
phase = rng.uniform(0, cycle)

# Each cell swaps glyph every `period` frames; periods divide L so the sequence wraps.
periods = np.array([d for d in range(6, L + 1) if L % d == 0])
period = rng.choice(periods, (rows, cols))
cell_phase = rng.integers(0, period)
glyphs = rng.integers(0, len(CHARS), (rows, cols, L // periods.min()))
rr, cc = np.indices((rows, cols))

color = np.array([int(a.color[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255
white = np.array([0.85, 1.0, 0.85], np.float32)


def render(t):
    head = np.floor((phase + speed * t) % cycle)
    d = head[:, None, :] - rr[None]
    lit = (d >= 0) & (d < tail[:, None, :])
    inten = np.where(lit, np.clip(1 - d / tail[:, None, :], 0, 1) ** 1.5, 0).max(0)
    is_head = ((d == 0) & lit).any(0)
    epoch = ((t + cell_phase) // period) % (L // period)
    g = glyphs[rr, cc, epoch]
    tint = np.where(is_head[..., None], white, color) * inten[..., None]
    px = atlas[g][..., None] * tint[:, :, None, None, :]
    img = px.transpose(0, 2, 1, 3, 4).reshape(rows * a.cell, cols * a.cell, 3)
    return (img[: a.height, : a.width] * 255).astype(np.uint8)


assert np.array_equal(render(0), render(L)), "loop is not seamless"

ff = subprocess.Popen(
    ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{a.width}x{a.height}", "-r", str(a.fps), "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
     "-movflags", "+faststart", a.output],
    stdin=subprocess.PIPE,
)
for t in range(L):
    ff.stdin.write(render(t).tobytes())
ff.stdin.close()
raise SystemExit(ff.wait())
