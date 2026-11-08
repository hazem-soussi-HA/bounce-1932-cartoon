"""Drawing helpers, palette and film-print effects for BOUNCE! (1932)."""

import math
import random

import cairo
import numpy as np

# ---- geometry ------------------------------------------------------------
DW, DH = 960, 720          # design resolution (all art is drawn in this space)
W, H = 1280, 960           # actual render resolution (4:3, 1.333x)
SCALE = W / DW
TAU = math.tau
KAPPA = 0.5522847498307936

# ---- palette -------------------------------------------------------------
INK      = (0x17/255, 0x13/255, 0x10/255)
INK_SOFT = (0x3a/255, 0x31/255, 0x27/255)
CREAM    = (0xf6/255, 0xea/255, 0xcb/255)
CREAM_2  = (0xec/255, 0xdc/255, 0xb6/255)
PAPER    = (0xe9/255, 0xd9/255, 0xb0/255)
WALL     = (0xd9/255, 0xc4/255, 0x9b/255)
WALL_2   = (0xcf/255, 0xb8/255, 0x8c/255)
FLOOR    = (0x9d/255, 0x70/255, 0x46/255)
FLOOR_2  = (0x83/255, 0x58/255, 0x35/255)
RED      = (0xb5/255, 0x41/255, 0x2d/255)
RED_2    = (0x8b/255, 0x2d/255, 0x21/255)
GOLD     = (0xca/255, 0x9b/255, 0x4b/255)
GOLD_2   = (0xa9/255, 0x77/255, 0x31/255)
OLIVE    = (0x6b/255, 0x71/255, 0x45/255)
OLIVE_2  = (0x4c/255, 0x52/255, 0x30/255)
WHITE    = (0xfb/255, 0xf4/255, 0xdf/255)
DUST     = (0xd8/255, 0xc5/255, 0x9f/255)
BLACK    = (0.031, 0.024, 0.020)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, u):
    return a + (b - a) * u


def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0))
    return t * t * (3 - 2 * t)


def ease_out_cubic(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in_cubic(u):
    u = clamp(u)
    return u ** 3


def ease_in_out(u):
    u = clamp(u)
    return 3 * u * u - 2 * u * u * u


def ease_out_back(u, s=1.70158):
    u = clamp(u) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def pulse(t, start, dur):
    """0 -> 1 -> 0 over [start, start+dur]."""
    if t < start or t > start + dur:
        return 0.0
    return math.sin(math.pi * (t - start) / dur)


def lerp_angle(a, b, u):
    while b - a > math.pi:
        b -= TAU
    while b - a < -math.pi:
        b += TAU
    return a + (b - a) * u


# ---- colour / paint ------------------------------------------------------
def set_src(ctx, c, alpha=1.0):
    if len(c) == 4:
        ctx.set_source_rgba(c[0], c[1], c[2], c[3] * alpha)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], alpha)


def rect(ctx, x, y, w, h, fill=None, stroke=None, lw=2.0, alpha=1.0, rot=0.0):
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.restore()
    if fill is not None:
        set_src(ctx, fill, alpha)
        if stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke is not None:
        set_src(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.new_path()


def rrect(ctx, x, y, w, h, r, fill=None, stroke=None, lw=2.0, alpha=1.0):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()
    if fill is not None:
        set_src(ctx, fill, alpha)
        if stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke is not None:
        set_src(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.new_path()


def ellipse_path(ctx, cx, cy, rx, ry, rot=0.0):
    ca, sa = math.cos(rot), math.sin(rot)

    def tp(x, y):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)

    p0 = tp(rx, 0)
    p1 = tp(0, ry)
    p2 = tp(-rx, 0)
    p3 = tp(0, -ry)
    c01a = tp(rx, ry * KAPPA)
    c01b = tp(rx * KAPPA, ry)
    c12a = tp(-rx * KAPPA, ry)
    c12b = tp(-rx, ry * KAPPA)
    c23a = tp(-rx, -ry * KAPPA)
    c23b = tp(-rx * KAPPA, -ry)
    c30a = tp(rx * KAPPA, -ry)
    c30b = tp(rx, -ry * KAPPA)
    ctx.move_to(*p0)
    ctx.curve_to(*c01a, *c01b, *p1)
    ctx.curve_to(*c12a, *c12b, *p2)
    ctx.curve_to(*c23a, *c23b, *p3)
    ctx.curve_to(*c30a, *c30b, *p0)
    ctx.close_path()


def ellipse(ctx, cx, cy, rx, ry, fill=None, stroke=None, lw=2.0, alpha=1.0, rot=0.0):
    ellipse_path(ctx, cx, cy, rx, ry, rot)
    if fill is not None:
        set_src(ctx, fill, alpha)
        if stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke is not None:
        set_src(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.new_path()


def circle(ctx, cx, cy, r, fill=None, stroke=None, lw=2.0, alpha=1.0):
    ellipse(ctx, cx, cy, r, r, fill, stroke, lw, alpha)


def poly_path(ctx, pts, close=True):
    if not pts:
        return
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def poly(ctx, pts, fill=None, stroke=None, lw=2.0, alpha=1.0, close=True):
    poly_path(ctx, pts, close)
    if fill is not None:
        set_src(ctx, fill, alpha)
        if stroke is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke is not None:
        set_src(ctx, stroke, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.new_path()


def stroke(ctx, pts, color, lw=2.0, alpha=1.0, cap=cairo.LINE_CAP_ROUND,
           join=cairo.LINE_JOIN_ROUND, close=False):
    if not pts:
        return
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.set_line_join(join)
    set_src(ctx, color, alpha)
    ctx.stroke()
    ctx.new_path()


def curve_stroke(ctx, pts, color, lw=2.0, alpha=1.0,
                 cap=cairo.LINE_CAP_ROUND):
    """pts = [start, c1, c2, end, c1, c2, end...]"""
    if len(pts) < 2:
        return
    ctx.move_to(*pts[0])
    i = 1
    while i + 2 < len(pts):
        ctx.curve_to(*pts[i], *pts[i + 1], *pts[i + 2])
        i += 3
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    set_src(ctx, color, alpha)
    ctx.stroke()
    ctx.new_path()


def filled_polygon_curve(ctx, start, curves, fill, stroke_c=None, lw=2.0, alpha=1.0):
    """curves = [(c1,c2,p), ...]; closes the path automatically."""
    ctx.move_to(*start)
    for c1, c2, p in curves:
        ctx.curve_to(*c1, *c2, *p)
    ctx.close_path()
    if fill is not None:
        set_src(ctx, fill, alpha)
        if stroke_c is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke_c is not None:
        set_src(ctx, stroke_c, alpha)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
    ctx.new_path()


def quad_points(p0, p1, p2, n=20):
    out = []
    for i in range(n + 1):
        u = i / n
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
        out.append((x, y))
    return out


def cubic_points(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        u = i / n
        v = 1 - u
        x = v ** 3 * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u ** 3 * p3[0]
        y = v ** 3 * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u ** 3 * p3[1]
        out.append((x, y))
    return out


def hose(ctx, p0, p3, bend=(0, 0), width=8, color=INK, alpha=1.0):
    """Rubber-hose limb: a quadratic curve from p0 to p3 bowed by bend."""
    mx = (p0[0] + p3[0]) / 2 + bend[0]
    my = (p0[1] + p3[1]) / 2 + bend[1]
    pts = quad_points(p0, (mx, my), p3, 22)
    stroke(ctx, pts, color, width, alpha)
    return pts[-1]


# ---- text ---------------------------------------------------------------
def _char_widths(ctx, s):
    return [ctx.text_extents(ch).x_advance for ch in s]


def text(ctx, s, x, y, size, family="C059", color=INK,
         weight=cairo.FONT_WEIGHT_BOLD, slant=cairo.FONT_SLANT_NORMAL,
         align="center", tracking=0.0, alpha=1.0):
    """Draw text; y is the baseline. Returns total width."""
    ctx.save()
    ctx.select_font_face(family, slant, weight)
    ctx.set_font_size(size)
    if not s:
        ctx.restore()
        return 0.0
    if abs(tracking) < 1e-6:
        ext = ctx.text_extents(s)
        total = ext.width
        if align == "center":
            px = x - ext.width / 2 - ext.x_bearing
        elif align == "right":
            px = x - ext.width - ext.x_bearing
        else:
            px = x
        ctx.move_to(px, y)
        set_src(ctx, color, alpha)
        ctx.show_text(s)
    else:
        widths = _char_widths(ctx, s)
        total = sum(widths) + tracking * max(0, len(s) - 1)
        if align == "center":
            px = x - total / 2
        elif align == "right":
            px = x - total
        else:
            px = x
        set_src(ctx, color, alpha)
        for ch, w in zip(s, widths):
            if ch != " ":
                ctx.move_to(px, y)
                ctx.show_text(ch)
            px += w + tracking
    ctx.restore()
    return total


def text_width(ctx, s, size, family="C059", weight=cairo.FONT_WEIGHT_BOLD,
               tracking=0.0, slant=cairo.FONT_SLANT_NORMAL):
    ctx.save()
    ctx.select_font_face(family, slant, weight)
    ctx.set_font_size(size)
    if abs(tracking) < 1e-6:
        w = ctx.text_extents(s).width
    else:
        w = sum(_char_widths(ctx, s)) + tracking * max(0, len(s) - 1)
    ctx.restore()
    return w


def layout_words(ctx, sentence, cx, y, size, family="C059", color=INK,
                 weight=cairo.FONT_WEIGHT_BOLD, tracking=0.0,
                 space_extra=0.0):
    """Draw a centered sentence and return [(word, x_center, width)]."""
    words = sentence.split(" ")
    ctx.save()
    ctx.select_font_face(family, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    space_w = ctx.text_extents(" ").x_advance + space_extra
    widths = []
    for w in words:
        if abs(tracking) < 1e-6:
            widths.append(ctx.text_extents(w).width)
        else:
            widths.append(sum(_char_widths(ctx, w)) + tracking * max(0, len(w) - 1))
    ctx.restore()
    total = sum(widths) + space_w * (len(words) - 1)
    px = cx - total / 2
    out = []
    for w, wd in zip(words, widths):
        text(ctx, w, px, y, size, family, color=color, align="left",
             weight=weight, tracking=tracking)
        out.append((w, px + wd / 2, wd))
        px += wd + space_w
    return out


# ---- decorative bits -----------------------------------------------------
def star_path(ctx, cx, cy, r1, r2=None, n=5, rot=-math.pi / 2):
    r2 = r2 or r1 * 0.45
    pts = []
    for i in range(n * 2):
        ang = rot + i * math.pi / n
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    poly_path(ctx, pts)


def star(ctx, cx, cy, r1, r2=None, n=5, rot=-math.pi / 2,
         fill=CREAM, stroke_c=None, lw=2.0, alpha=1.0):
    star_path(ctx, cx, cy, r1, r2, n, rot)
    if fill is not None:
        set_src(ctx, fill, alpha)
        if stroke_c is not None:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if stroke_c is not None:
        set_src(ctx, stroke_c, alpha)
        ctx.set_line_width(lw)
        ctx.stroke()
    ctx.new_path()


def sparkle(ctx, cx, cy, r, color=CREAM, alpha=1.0, lw=2.0):
    pts = [(cx - r, cy), (cx, cy), (cx, cy - r)]
    stroke(ctx, pts, color, lw, alpha)
    pts = [(cx, cy), (cx + r, cy), (cx, cy + r)]
    stroke(ctx, pts, color, lw, alpha)


def note(ctx, cx, cy, s, color=INK, alpha=1.0, rot=0.0, kind="eighth"):
    """A hand-drawn musical note, size s = head width."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ellipse(ctx, 0, 0, s * 0.55, s * 0.4, fill=color, alpha=alpha, rot=-0.35)
    stroke(ctx, [(s * 0.45, -s * 0.1), (s * 0.45, -s * 2.4)], color, s * 0.14, alpha)
    if kind in ("eighth", "beamed"):
        ctx.move_to(s * 0.45, -s * 2.4)
        ctx.curve_to(s * 0.45, -s * 2.0, s * 1.35, -s * 2.0, s * 1.15, -s * 1.25)
        ctx.curve_to(s * 1.1, -s * 1.7, s * 0.8, -s * 1.8, s * 0.45, -s * 1.65)
        set_src(ctx, color, alpha)
        ctx.set_line_width(s * 0.18)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        ctx.new_path()
    if kind == "double":
        ellipse(ctx, s * 1.45, -s * 0.25, s * 0.5, s * 0.36, fill=color, alpha=alpha, rot=-0.35)
        stroke(ctx, [(s * 1.9, -s * 0.35), (s * 1.9, -s * 2.6)], color, s * 0.13, alpha)
        ctx.move_to(s * 0.45, -s * 2.4)
        ctx.line_to(s * 1.9, -s * 2.6)
        set_src(ctx, color, alpha)
        ctx.set_line_width(s * 0.2)
        ctx.stroke()
        ctx.new_path()
    ctx.restore()


def sunburst(ctx, cx, cy, r_in, r_out, n=24, color=RED, alpha=0.12, rot=0.0, width=None):
    for i in range(n):
        a0 = rot + i * TAU / n
        a1 = a0 + TAU / n * 0.5
        p0 = (cx + math.cos(a0) * r_in, cy + math.sin(a0) * r_in)
        p1 = (cx + math.cos(a0) * r_out, cy + math.sin(a0) * r_out)
        p2 = (cx + math.cos(a1) * r_out, cy + math.sin(a1) * r_out)
        p3 = (cx + math.cos(a1) * r_in, cy + math.sin(a1) * r_in)
        poly(ctx, [p0, p1, p2, p3], fill=color, alpha=alpha)


def radial_glow(ctx, cx, cy, r, color=CREAM, alpha=0.3, x0=0, y0=0, w=DW, h=DH):
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, max(r, 1))
    g.add_color_stop_rgba(0, color[0], color[1], color[2], alpha)
    g.add_color_stop_rgba(0.55, color[0], color[1], color[2], alpha * 0.45)
    g.add_color_stop_rgba(1, color[0], color[1], color[2], 0)
    ctx.set_source(g)
    ctx.rectangle(x0, y0, w, h)
    ctx.fill()
    ctx.new_path()


def liner(ctx, cx, y, half_w, color=CREAM, alpha=0.9, lw=1.4, diamond=True):
    stroke(ctx, [(cx - half_w, y), (cx - 18, y)], color, lw, alpha)
    stroke(ctx, [(cx + 18, y), (cx + half_w, y)], color, lw, alpha)
    if diamond:
        poly(ctx, [(cx, y - 6), (cx + 6, y), (cx, y + 6), (cx - 6, y)],
             fill=color, alpha=alpha)
        poly(ctx, [(cx - 30, y - 3), (cx - 26, y), (cx - 30, y + 3), (cx - 34, y)],
             fill=color, alpha=alpha * 0.8)
        poly(ctx, [(cx + 30, y - 3), (cx + 34, y), (cx + 30, y + 3), (cx + 26, y)],
             fill=color, alpha=alpha * 0.8)


def deco_corner(ctx, x, y, dx, dy, size=54, color=CREAM, alpha=0.85, lw=1.2):
    """Art-deco fan in a screen corner; dx/dy point into the frame."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(dx, dy)
    for i in range(4):
        a = -math.pi / 2 + i * 0.16
        stroke(ctx, [(0, 0), (math.cos(a) * size, math.sin(a) * size)],
               color, lw, alpha)
    arc_r = size * 0.78
    ctx.arc(0, 0, arc_r, 0, math.pi / 2)
    set_src(ctx, color, alpha)
    ctx.set_line_width(lw)
    ctx.stroke()
    ctx.new_path()
    ctx.arc(0, 0, size * 0.5, 0, math.pi / 2)
    ctx.stroke()
    ctx.new_path()
    ctx.restore()


# ---- film print ----------------------------------------------------------
def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W / 2) / (W / 2)
    ny = (yy - H / 2) / (H / 2)
    r = np.sqrt(nx * nx * 0.92 + ny * ny * 0.98)
    v = 1.0 - 0.40 * np.clip((r - 0.42) / 0.72, 0, 1) ** 1.45
    # a touch of corner falloff
    v *= 1.0 - 0.10 * np.clip((np.abs(nx) * np.abs(ny) - 0.2) / 0.8, 0, 1)
    return v.astype(np.float32)


VIGNETTE = make_vignette()


def film_dust(ctx, fi, t):
    """Scratches, dust and the odd hair, in design space."""
    rng = random.Random(fi * 92821 + 17)
    # vertical scratches (change every few frames, drift)
    for k in range(2):
        if rng.random() < 0.35:
            x = rng.uniform(40, DW - 40) + math.sin(fi * 0.06 + k * 2.1) * 8
            a = rng.uniform(0.04, 0.11)
            wob = rng.uniform(4, 12)
            pts = []
            for yy in range(-10, DH + 20, 30):
                pts.append((x + math.sin(yy * 0.02 + fi * 0.13 + k) * wob * 0.25, yy))
            stroke(ctx, pts, CREAM, rng.uniform(0.7, 1.5), a)
    # dust specks
    for _ in range(rng.randint(6, 13)):
        x = rng.uniform(8, DW - 8)
        y = rng.uniform(8, DH - 8)
        r = rng.uniform(0.5, 2.1)
        c = INK if rng.random() < 0.55 else CREAM
        circle(ctx, x, y, r, fill=c, alpha=rng.uniform(0.25, 0.6))
    # occasional hair
    if rng.random() < 0.035:
        x = rng.uniform(120, DW - 120)
        y = rng.uniform(80, DH - 80)
        pts = [(x, y)]
        for i in range(5):
            x += rng.uniform(-14, 20)
            y += rng.uniform(6, 18)
            pts.append((x, y))
        stroke(ctx, pts, INK, 1.0, 0.35)
    # reel-change cue mark
    if 29.95 < t < 30.30:
        a = 0.8 if t < 30.18 else 0.35
        circle(ctx, 898, 54, 13, fill=INK, alpha=a)
        circle(ctx, 898, 54, 7.5, fill=CREAM, alpha=a)


def apply_film(rgb, fi, t):
    """rgb uint8 HxWx3 -> graded, grainy, flickering uint8."""
    rng = np.random.default_rng()
    arr = rgb

    # gate weave
    dx = int(round(math.sin(t * 2.1) * 0.9 + math.sin(t * 5.3 + 1.0) * 0.35))
    dy = int(round(math.sin(t * 1.7 + 0.7) * 0.7))
    if dx or dy:
        p = 2
        padded = np.pad(arr, ((p, p), (p, p), (0, 0)), mode="edge")
        arr = padded[p + dy:p + dy + H, p + dx:p + dx + W]

    a = arr.astype(np.int16)
    # warm, lifted blacks, gentle print contrast
    a = (a * 0.925 + 9.0).astype(np.int16)
    a = a.astype(np.float32)
    a[..., 0] *= 1.028
    a[..., 1] *= 1.002
    a[..., 2] *= 0.945

    # exposure flicker
    flick = 1.0 + 0.013 * math.sin(t * 23.7) + float(rng.uniform(-0.008, 0.008))
    a *= flick

    # monochrome grain
    g = rng.integers(-5, 6, size=(H, W, 1), dtype=np.int16).astype(np.float32)
    g += rng.normal(0, 1.7, size=(H, W, 1)).astype(np.float32)
    a += g

    # vignette + slight edge warmth
    a *= VIGNETTE[..., None]
    a = np.clip(a, 0, 255).astype(np.uint8)
    return a


def cue_flash(alpha=1.0):
    pass
