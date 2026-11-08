"""Render BOUNCE! (1932) to a 60-second MP4 with soundtrack.

Usage:
    python3 render.py                 # full 1440-frame render
    python3 render.py --frames 48     # quick pipe/codec test
"""

import argparse
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import cairo
import numpy as np

from gfx import W, H, SCALE, apply_film, film_dust
import scene

FPS = 24
TOTAL = 1440  # 60.000 s


def render_rgb(fi):
    """Render one frame to a contiguous RGB uint8 array."""
    t = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.scale(SCALE, SCALE)
    scene.draw_frame(ctx, t)
    film_dust(ctx, fi, t)
    surf.flush()
    arr = np.ndarray(
        shape=(H, W, 4),
        dtype=np.uint8,
        buffer=surf.get_data(),
        strides=(surf.get_stride(), 4, 1),
    )
    rgb = arr[:, :, 2::-1].copy()  # cairo RGB24 is BGRA in memory
    return apply_film(rgb, fi, t)


def render_bytes(fi):
    return render_rgb(fi).tobytes()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="BOUNCE_1932.mp4")
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 4))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=TOTAL)
    ap.add_argument("--frames", type=int, default=None,
                    help="render only the first N frames (test mode)")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--audio", default="soundtrack.wav")
    args = ap.parse_args()

    start = args.start
    end = args.end if args.frames is None else min(args.end, start + args.frames)
    n = end - start

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", args.audio,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf),
        "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        args.out,
    ]

    print(f"rendering {n} frames ({n / FPS:.2f}s) with {args.workers} workers -> {args.out}")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    written = 0
    try:
        with Pool(args.workers) as pool:
            for data in pool.imap(render_bytes, range(start, end), chunksize=2):
                proc.stdin.write(data)
                written += 1
                if written % 48 == 0 or written == n:
                    el = time.time() - t0
                    rate = written / max(el, 1e-6)
                    eta = (n - written) / max(rate, 1e-6)
                    print(f"  {written}/{n} frames  {rate:.2f} fps  "
                          f"elapsed {el:5.1f}s  eta {eta:5.1f}s", flush=True)
        proc.stdin.close()
    except BaseException:
        proc.kill()
        proc.wait()
        raise

    rc = proc.wait()
    if rc != 0:
        sys.exit(f"ffmpeg failed with exit code {rc}")
    print(f"done in {time.time() - t0:.1f}s -> {args.out}")


if __name__ == "__main__":
    main()
