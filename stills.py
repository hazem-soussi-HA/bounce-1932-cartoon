"""Render individual scene frames for visual review."""
import sys
import time

import cairo
import numpy as np
from PIL import Image

from gfx import W, H, SCALE, apply_film, film_dust
import scene

TIMES = [2.0, 5.2, 6.6, 7.45, 7.8, 9.0, 10.3, 11.8, 13.5, 15.5,
         18.5, 20.0, 21.6, 22.2, 23.0, 23.85, 24.3, 25.5, 28.0, 30.0,
         31.2, 32.5, 33.5, 34.4, 35.8, 36.8, 37.3, 38.0, 42.0, 45.0,
         49.5, 51.0, 53.2, 54.0, 55.2, 56.6, 58.0, 59.5]


def render_rgb(t, grain=True):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.scale(SCALE, SCALE)
    scene.draw_frame(ctx, t)
    film_dust(ctx, int(round(t * 24)), t)
    surf.flush()
    arr = np.ndarray(shape=(H, W, 4), dtype=np.uint8,
                     buffer=surf.get_data(), strides=(surf.get_stride(), 4, 1))
    rgb = arr[:, :, 2::-1].copy()
    if grain:
        rgb = apply_film(rgb, int(round(t * 24)), t)
    return rgb


def save(t, path):
    Image.fromarray(render_rgb(t)).save(path)


def contact_sheet(times, path, cols=6, thumb_w=426):
    rows = (len(times) + cols - 1) // cols
    thumb_h = int(thumb_w * H / W)
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (20, 16, 12))
    for i, t in enumerate(times):
        im = Image.fromarray(render_rgb(t)).resize((thumb_w, thumb_h))
        sheet.paste(im, ((i % cols) * thumb_w, (i // cols) * thumb_h))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    t0 = time.time()
    args = sys.argv[1:]
    if args and args[0] == "sheet":
        contact_sheet(TIMES, "contact_sheet.png")
    elif args:
        for a in args:
            t = float(a)
            save(t, "still_%05.2f.png" % t)
            print("wrote still_%05.2f.png" % t)
    else:
        for t in TIMES:
            save(t, "still_%05.2f.png" % t)
        contact_sheet(TIMES, "contact_sheet.png")
    print("done in %.2fs" % (time.time() - t0))
