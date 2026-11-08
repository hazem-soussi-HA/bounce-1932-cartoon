"""Whiskers the cat and Squeak the mouse, drawn as rubber-hose puppets."""

import math

import cairo

from gfx import (
    INK, INK_SOFT, CREAM, CREAM_2, RED, RED_2, GOLD, GOLD_2, WHITE, DUST,
    TAU, clamp, ellipse, circle, stroke, hose, poly, curve_stroke,
    filled_polygon_curve, text,
)


# =========================================================================
# Whiskers
# =========================================================================
def cat_pose(x, y, s=150.0, face=1, q=1.0, **kw):
    p = dict(
        x=x, y=y, s=s, face=face, q=q,
        hx=0.02, hy=0.0, htilt=0.0,
        arm_l=(-0.50, -0.77), arm_r=(0.50, -0.77),
        bend_l=-0.10, bend_r=0.10,
        leg_l=(-0.22, -0.02), leg_r=(0.22, -0.02),
        legbend_l=-0.10, legbend_r=0.10,
        eye="open", eye_open=1.0, look=(0.025, 0.015),
        mouth=0.0, smile=1.0, tongue=False,
        tail=0.0, tail_lift=0.0, ear=0.0,
        hat=None, hat_rot=0.0,
        blush=0.0,
    )
    p.update(kw)
    return p


def _cat_xf(p):
    s = p["s"]
    face = p["face"]
    q = p["q"]
    wq = 1.0 + (1.0 - q) * 0.38
    if q > 1.0:
        wq = 1.0 - (q - 1.0) * 0.28
    wq = clamp(wq, 0.78, 1.22)

    def P(lx, ly):
        return (p["x"] + face * lx * s * wq, p["y"] + ly * s * q)

    return s, face, q, wq, P


def _head_xf(p, P):
    s = p["s"]
    hx, hy = p["hx"], p["hy"]
    hc = P(hx, -1.335 + hy)
    ca, sa = math.cos(p["htilt"]), math.sin(p["htilt"])

    def H(lx, ly):
        x, y = lx * s, ly * s
        return (hc[0] + x * ca - y * sa, hc[1] + x * sa + y * ca)

    return hc, H


def draw_boater(ctx, cx, cy, s, rot=0.0, alpha=1.0, ink=INK):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    # brim
    ellipse(ctx, 0, s * 0.02, s * 0.40, s * 0.085, fill=CREAM, stroke=ink,
            lw=max(1.6, s * 0.014), alpha=alpha)
    # crown
    poly(ctx, [(-s * 0.26, s * 0.01), (-s * 0.23, -s * 0.18),
               (s * 0.23, -s * 0.18), (s * 0.26, s * 0.01)],
         fill=CREAM, stroke=ink, lw=max(1.6, s * 0.014), alpha=alpha)
    ellipse(ctx, 0, -s * 0.18, s * 0.23, s * 0.055, fill=CREAM_2,
            stroke=ink, lw=max(1.4, s * 0.012), alpha=alpha)
    # ribbon
    rect_pts = [(-s * 0.245, -s * 0.055), (s * 0.245, -s * 0.055),
                (s * 0.25, -s * 0.005), (-s * 0.25, -s * 0.005)]
    poly(ctx, rect_pts, fill=RED, alpha=alpha)
    ctx.restore()


def draw_glove(ctx, cx, cy, s, face=1, rot=0.0, alpha=1.0):
    lw = max(1.5, s * 0.012)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    # cuff
    ellipse(ctx, -face * 0.055 * s, 0.025 * s, 0.038 * s, 0.062 * s,
            fill=CREAM_2, stroke=INK, lw=lw, alpha=alpha)
    # mitt
    ellipse(ctx, 0, 0, 0.082 * s, 0.072 * s, fill=CREAM, stroke=INK,
            lw=lw, alpha=alpha)
    # thumb
    circle(ctx, face * 0.045 * s, -0.050 * s, 0.030 * s,
           fill=CREAM, stroke=INK, lw=lw * 0.9, alpha=alpha)
    # finger creases
    for dy in (-0.012, 0.022):
        stroke(ctx, [(face * 0.018 * s, dy * s),
                     (face * 0.058 * s, (dy + 0.012) * s)],
               INK, max(1.0, s * 0.008), 0.55 * alpha)
    ctx.restore()


def _shoe(ctx, cx, cy, s, face, lw, alpha=1.0, angle=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(angle)
    ellipse(ctx, face * 0.018 * s, 0.005 * s, 0.145 * s, 0.062 * s,
            fill=CREAM, stroke=INK, lw=lw, alpha=alpha)
    # sole
    stroke(ctx, [(-0.105 * s, 0.043 * s), (0.125 * s, 0.043 * s)],
           INK, lw * 0.7, 0.55 * alpha)
    # toe cap
    ctx.arc(face * 0.085 * s, 0.0, 0.045 * s, -1.1, 1.1)
    ctx.set_line_width(lw * 0.75)
    ctx.set_source_rgba(INK[0], INK[1], INK[2], 0.6 * alpha)
    ctx.stroke()
    ctx.new_path()
    ctx.restore()


def _cat_eye(ctx, H, side, p, s):
    ex, ey = 0.145 * side, -0.035
    mode = p["eye"]
    look = p["look"]
    lw = max(1.5, s * 0.012)
    cx, cy = H(ex, ey)
    rx, ry = 0.100 * s, 0.132 * s
    if mode in ("closed", "happy", "wink"):
        if mode == "wink" and side * p["face"] > 0:
            pass  # this eye stays open
        else:
            # closed eye: cheerful upward arc
            up = -1 if mode == "happy" else 1
            pts = []
            for i in range(13):
                u = i / 12
                xx = cx + (u - 0.5) * rx * 1.8
                yy = cy + up * (0.018 * s) * math.sin(math.pi * u)
                pts.append((xx, yy))
            stroke(ctx, pts, INK, max(2.0, s * 0.018), 0.95)
            if mode == "happy":
                stroke(ctx, [(cx - rx * 0.55, cy - 0.052 * s),
                             (cx - rx * 0.45, cy - 0.07 * s)],
                       INK, max(1.0, s * 0.008), 0.6)
                stroke(ctx, [(cx + rx * 0.45, cy - 0.07 * s),
                             (cx + rx * 0.55, cy - 0.052 * s)],
                       INK, max(1.0, s * 0.008), 0.6)
            return
    if mode == "x":
        ellipse(ctx, cx, cy, rx * 0.95, ry * 0.92, fill=CREAM, stroke=INK, lw=lw)
        for a in (-1, 1):
            stroke(ctx, [(cx - rx * 0.38 * a, cy - ry * 0.32),
                         (cx + rx * 0.38 * a, cy + ry * 0.32)],
                   INK, max(1.8, s * 0.016))
        return
    if mode == "spiral":
        ellipse(ctx, cx, cy, rx * 0.95, ry * 0.92, fill=CREAM, stroke=INK, lw=lw)
        pts = []
        for i in range(40):
            u = i / 39
            ang = u * TAU * 2.5
            rr = u * rx * 0.62
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 1.25))
        stroke(ctx, pts, INK, max(1.2, s * 0.011), 0.9)
        return

    openness = clamp(p["eye_open"], 0.0, 1.15)
    big = 1.10 if mode == "wide" else 1.0
    erx, ery = rx * big, ry * big * max(0.10, openness)
    if mode == "wide":
        ery = ry * big
    ey_shift = (ry * big - ery) * 0.55
    ellipse(ctx, cx, cy + ey_shift, erx, ery, fill=CREAM, stroke=INK, lw=lw)
    if openness > 0.22:
        pr = s * (0.040 if mode != "wide" else 0.030)
        px = cx + look[0] * s
        py = cy + ey_shift + look[1] * s
        px = clamp(px, cx - erx + pr * 0.9, cx + erx - pr * 0.9)
        py = clamp(py, cy + ey_shift - ery + pr * 0.9, cy + ey_shift + ery - pr * 0.9)
        circle(ctx, px, py, pr, fill=INK)
        circle(ctx, px - pr * 0.32, py - pr * 0.38, pr * 0.28, fill=CREAM, alpha=0.95)
        # classic pie-cut notch
        poly(ctx, [(px - pr * 0.1, py - pr * 0.55),
                   (px - pr * 0.75, py - pr * 0.6),
                   (px - pr * 0.25, py - pr * 0.05)],
             fill=CREAM, alpha=0.9)


def draw_cat(ctx, p, skip_gloves=False):
    s, face, q, wq, P = _cat_xf(p)
    hc, H = _head_xf(p, P)
    lw = max(1.6, s * 0.012)
    eye_mode = p["eye"]
    blink = p["eye_open"]

    # ---- tail (behind everything)
    tw = p["tail"]
    lift = p["tail_lift"]
    base = P(-0.19, -0.49)
    c1 = P(-0.50, -0.57 + 0.05 * math.sin(tw))
    c2 = P(-0.76 + 0.05 * math.sin(tw + 0.8),
           -0.98 + 0.10 * math.sin(tw + 0.4) - 0.18 * lift)
    tip = P(-0.54 + 0.06 * math.sin(tw + 0.4),
            -1.28 + 0.07 * math.sin(tw) - 0.24 * lift)
    curve_stroke(ctx, [base, c1, c2, tip], INK, 0.072 * s, 1.0)

    # ---- legs
    for side, hip, foot, bend in (
        (-1, (-0.13, -0.47), p["leg_l"], p["legbend_l"]),
        (1, (0.13, -0.47), p["leg_r"], p["legbend_r"]),
    ):
        p0 = P(*hip)
        p3 = P(*foot)
        bx = face * bend * s * wq
        by = -0.015 * s
        hose(ctx, p0, p3, bend=(bx, by), width=0.080 * s, color=INK)
        fx = p3[0] + face * 0.012 * s
        fy = p3[1] + 0.005 * s
        _shoe(ctx, fx, fy, s, face, lw)

    # ---- body
    body = [
        (P(0.00, -1.19), None, None),
    ]
    ctx.move_to(*P(0.0, -1.20))
    ctx.curve_to(*P(0.17, -1.20), *P(0.305, -1.05), *P(0.315, -0.80))
    ctx.curve_to(*P(0.325, -0.55), *P(0.25, -0.37), *P(0.10, -0.305))
    ctx.curve_to(*P(0.03, -0.28), *P(-0.03, -0.28), *P(-0.10, -0.305))
    ctx.curve_to(*P(-0.25, -0.37), *P(-0.325, -0.55), *P(-0.315, -0.80))
    ctx.curve_to(*P(-0.305, -1.05), *P(-0.17, -1.20), *P(0.0, -1.20))
    ctx.close_path()
    ctx.set_source_rgba(*INK, 1.0)
    ctx.fill()
    ctx.new_path()

    # cream waistcoat / chest patch
    ellipse(ctx, *P(0.015, -0.735), 0.135 * s, 0.185 * s,
            fill=CREAM, alpha=0.97, rot=0.0)
    ellipse(ctx, *P(0.015, -0.79), 0.075 * s, 0.11 * s,
            fill=CREAM_2, alpha=0.55)

    # ---- bow tie
    bx, by = H(0.0, 0.355)
    ctx.save()
    ctx.translate(bx, by)
    ctx.rotate(p["htilt"])
    poly(ctx, [(-0.145 * s, -0.065 * s), (-0.012 * s, -0.025 * s),
               (-0.012 * s, 0.055 * s), (-0.145 * s, 0.075 * s)],
         fill=RED, stroke=INK, lw=lw * 0.8)
    poly(ctx, [(0.145 * s, -0.065 * s), (0.012 * s, -0.025 * s),
               (0.012 * s, 0.055 * s), (0.145 * s, 0.075 * s)],
         fill=RED, stroke=INK, lw=lw * 0.8)
    circle(ctx, 0, 0.018 * s, 0.036 * s, fill=RED_2, stroke=INK, lw=lw * 0.75)
    ctx.restore()

    # ---- arms
    for side, shoulder, hand, bend in (
        (-1, (-0.255, -1.03), p["arm_l"], p["bend_l"]),
        (1, (0.255, -1.03), p["arm_r"], p["bend_r"]),
    ):
        p0 = P(*shoulder)
        p3 = P(*hand)
        hose(ctx, p0, p3, bend=(face * bend * s * 0.9, 0.105 * s),
             width=0.072 * s, color=INK)
        if not skip_gloves:
            draw_glove(ctx, p3[0], p3[1], s, face)

    # ---- ears (behind head circle)
    for side in (-1, 1):
        outer = [H(side * 0.10, -0.30), H(side * 0.34, -0.56),
                 H(side * 0.38, -0.20)]
        inner = [H(side * 0.17, -0.29), H(side * 0.32, -0.47),
                 H(side * 0.34, -0.24)]
        poly(ctx, outer, fill=INK)
        poly(ctx, inner, fill=RED_2, alpha=0.9)

    # ---- head
    circle(ctx, hc[0], hc[1], 0.330 * s, fill=INK)
    # muzzle
    ellipse(ctx, *H(0.0, 0.135), 0.270 * s, 0.190 * s, fill=CREAM)
    # cheek blush
    if p["blush"] > 0:
        for side in (-1, 1):
            circle(ctx, *H(side * 0.205, 0.155), 0.045 * s,
                   fill=RED, alpha=0.18 * p["blush"])

    # ---- eyes
    _cat_eye(ctx, H, -1, p, s)
    _cat_eye(ctx, H, 1, p, s)

    # ---- nose + mouth
    nx, ny = H(0.0, 0.065)
    poly(ctx, [(nx - 0.043 * s, ny - 0.022 * s),
               (nx + 0.043 * s, ny - 0.022 * s),
               (nx, ny + 0.045 * s)],
         fill=INK)
    circle(ctx, nx - 0.012 * s, ny - 0.012 * s, 0.010 * s, fill=CREAM, alpha=0.45)
    mouth = p["mouth"]
    if mouth < 0.08:
        # smile: two little arcs from under the nose
        for side in (-1, 1):
            p0 = (nx + side * 0.008 * s, ny + 0.055 * s)
            p1 = (nx + side * 0.085 * s, ny + 0.125 * s * p["smile"])
            p2 = (nx + side * 0.175 * s, ny + 0.070 * s * p["smile"])
            pts = []
            for i in range(10):
                u = i / 9
                xx = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
                yy = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
                pts.append((xx, yy))
            stroke(ctx, pts, INK, max(1.4, s * 0.011), 0.95)
    else:
        mw = 0.10 * s * (0.75 + 0.45 * mouth)
        mh = 0.095 * s * mouth
        mx, my = H(0.0, 0.175)
        ellipse(ctx, mx, my + mh * 0.25, mw, mh, fill=INK)
        if p["tongue"]:
            ellipse(ctx, mx, my + mh * 0.72, mw * 0.62, mh * 0.40,
                    fill=(0.70, 0.30, 0.25))
        # upper lip
        stroke(ctx, [(mx - mw, my - mh * 0.25), (mx, my - mh * 0.42),
                     (mx + mw, my - mh * 0.25)], INK, max(1.4, s * 0.011), 0.8)

    # ---- whiskers
    wig = math.sin(p["tail"] * 1.7) * 0.08
    for side in (-1, 1):
        root = H(side * 0.185, 0.115)
        for k, (dy, ln) in enumerate(((-0.03, 0.23), (0.025, 0.25), (0.075, 0.22))):
            end = H(side * (0.185 + ln), 0.115 + dy + wig * (k + 1))
            stroke(ctx, [root, end], INK, max(0.9, s * 0.0065), 0.75)

    # ---- hat
    if p["hat"] == "boater":
        bx, by = H(0.0, -0.315)
        draw_boater(ctx, bx, by, s * 0.92, rot=p["htilt"] + p["hat_rot"])


# =========================================================================
# Sleeping Whiskers
# =========================================================================
def draw_sleeping_cat(ctx, x, y, s=145, breath=0.0, eyes_open=False):
    """Curled on the armchair. y = seat/body baseline."""
    lw = max(1.6, s * 0.012)
    bob = 0.018 * s * math.sin(breath)
    # draped tail
    tail = [(x - 0.34 * s, y - 0.05 * s),
            (x - 0.62 * s, y + 0.14 * s),
            (x - 0.64 * s, y + 0.58 * s),
            (x - 0.48 * s, y + 0.75 * s)]
    curve_stroke(ctx, tail, INK, 0.060 * s, 1.0)
    circle(ctx, tail[-1][0], tail[-1][1], 0.052 * s, fill=CREAM, stroke=INK, lw=lw * 0.8)

    # body
    ellipse(ctx, x, y - 0.16 * s + bob, 0.52 * s, 0.29 * s + bob * 0.4, fill=INK)
    # hip highlight
    ellipse(ctx, x - 0.24 * s, y - 0.18 * s, 0.20 * s, 0.16 * s,
            fill=INK_SOFT, alpha=0.35)
    # tucked front paws
    draw_glove(ctx, x + 0.17 * s, y + 0.02 * s, s * 0.92, face=1, rot=-0.3)
    draw_glove(ctx, x + 0.31 * s, y + 0.05 * s, s * 0.92, face=1, rot=-0.1)
    # head on the armrest
    hx = x + 0.43 * s
    hy = y - 0.30 * s + bob * 0.5
    hr = 0.315 * s
    # ears
    for side in (-1, 1):
        poly(ctx, [(hx + side * 0.09 * s, hy - 0.30 * s),
                   (hx + side * 0.30 * s, hy - 0.55 * s),
                   (hx + side * 0.33 * s, hy - 0.20 * s)],
             fill=INK)
        poly(ctx, [(hx + side * 0.16 * s, hy - 0.28 * s),
                   (hx + side * 0.28 * s, hy - 0.46 * s),
                   (hx + side * 0.30 * s, hy - 0.23 * s)],
             fill=RED_2, alpha=0.9)
    circle(ctx, hx, hy, hr, fill=INK)
    ellipse(ctx, hx, hy + 0.12 * s, 0.255 * s, 0.178 * s, fill=CREAM)
    # eyes
    for side in (-1, 1):
        ex = hx + side * 0.135 * s
        ey = hy - 0.025 * s
        if eyes_open:
            ellipse(ctx, ex, ey, 0.09 * s, 0.112 * s, fill=CREAM, stroke=INK,
                    lw=lw * 0.9)
            circle(ctx, ex, ey, 0.037 * s, fill=INK)
            circle(ctx, ex - 0.012 * s, ey - 0.016 * s, 0.012 * s, fill=CREAM)
        else:
            pts = []
            for i in range(11):
                u = i / 10
                pts.append((ex + (u - 0.5) * 0.17 * s,
                            ey + 0.020 * s * math.sin(math.pi * u)))
            stroke(ctx, pts, INK, max(1.8, s * 0.016))
    # nose + smile
    nx, ny = hx, hy + 0.065 * s
    poly(ctx, [(nx - 0.040 * s, ny - 0.018 * s), (nx + 0.040 * s, ny - 0.018 * s),
               (nx, ny + 0.042 * s)], fill=INK)
    for side in (-1, 1):
        pts = [(nx + side * 0.01 * s, ny + 0.05 * s),
               (nx + side * 0.09 * s, ny + 0.11 * s),
               (nx + side * 0.17 * s, ny + 0.06 * s)]
        curve_stroke(ctx, [pts[0], pts[1], pts[1], pts[2]], INK,
                     max(1.3, s * 0.010), 0.9)
    for side in (-1, 1):
        for k in range(3):
            stroke(ctx, [(hx + side * 0.18 * s, hy + 0.10 * s),
                         (hx + side * 0.42 * s, hy + 0.07 * s + k * 0.035 * s)],
                   INK, max(0.9, s * 0.006), 0.7)
    # bow tie
    by = hy + 0.345 * s
    poly(ctx, [(hx - 0.14 * s, by - 0.06 * s), (hx - 0.012 * s, by - 0.022 * s),
               (hx - 0.012 * s, by + 0.052 * s), (hx - 0.14 * s, by + 0.07 * s)],
         fill=RED, stroke=INK, lw=lw * 0.8)
    poly(ctx, [(hx + 0.14 * s, by - 0.06 * s), (hx + 0.012 * s, by - 0.022 * s),
               (hx + 0.012 * s, by + 0.052 * s), (hx + 0.14 * s, by + 0.07 * s)],
         fill=RED, stroke=INK, lw=lw * 0.8)
    circle(ctx, hx, by + 0.015 * s, 0.036 * s, fill=RED_2, stroke=INK, lw=lw * 0.7)


def draw_zzz(ctx, x, y, t, s=1.0):
    for k in range(3):
        phase = (t * 0.7 + k * 0.33) % 1.0
        zx = x + math.sin((t + k) * 1.7) * 10 * s + phase * 26 * s
        zy = y - phase * 90 * s
        a = 0.85 * (1.0 - phase) * clamp(phase * 5)
        size = (16 + 13 * phase) * s
        text(ctx, "Z", zx, zy, size, family="C059", color=INK,
             weight=cairo.FONT_WEIGHT_BOLD, slant=cairo.FONT_SLANT_ITALIC,
             align="center", alpha=a * 0.55)


# =========================================================================
# Squeak the mouse
# =========================================================================
def mouse_pose(x, y, s=55.0, face=1, q=1.0, **kw):
    p = dict(
        x=x, y=y, s=s, face=face, q=q,
        arm_l=(-0.24, -0.62), arm_r=(0.24, -0.62),
        leg_l=(-0.14, -0.02), leg_r=(0.14, -0.02),
        eye="open", look=(0.0, 0.0), mouth=0.0, smile=1.0,
        tail=0.0, record=False, trumpet=False, giggle=False,
        vest=True, blink=1.0,
    )
    p.update(kw)
    return p


def draw_record(ctx, cx, cy, r, rot=0.0, alpha=1.0):
    circle(ctx, cx, cy, r, fill=(0.06, 0.05, 0.045), stroke=INK, lw=max(1.2, r * 0.05), alpha=alpha)
    circle(ctx, cx, cy, r * 0.36, fill=RED, alpha=alpha)
    circle(ctx, cx, cy, r * 0.055, fill=INK, alpha=alpha)
    # grooves
    for k in range(3):
        circle(ctx, cx, cy, r * (0.55 + k * 0.13), fill=None,
               stroke=(0.45, 0.40, 0.34), lw=max(0.7, r * 0.015), alpha=0.5 * alpha)
    # moving glint
    a = rot
    stroke(ctx, [(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55),
                 (cx + math.cos(a + 0.7) * r * 0.8, cy + math.sin(a + 0.7) * r * 0.8)],
           CREAM, max(1.0, r * 0.04), 0.35 * alpha)


def draw_trumpet(ctx, x, y, s, face=1, alpha=1.0):
    # a tiny vaudeville trumpet, bell pointing forward
    lw = max(1.2, s * 0.03)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(face, 1)
    # tube
    poly(ctx, [(-0.12 * s, -0.03 * s), (0.62 * s, -0.075 * s),
               (0.62 * s, 0.055 * s), (-0.12 * s, 0.035 * s)],
         fill=GOLD, stroke=INK, lw=lw, alpha=alpha)
    # bell
    poly(ctx, [(0.60 * s, -0.08 * s), (0.92 * s, -0.19 * s),
               (0.98 * s, 0.0), (0.92 * s, 0.19 * s), (0.60 * s, 0.08 * s)],
         fill=GOLD, stroke=INK, lw=lw, alpha=alpha)
    ellipse(ctx, 0.95 * s, 0.0, 0.035 * s, 0.18 * s, fill=GOLD_2,
            stroke=INK, lw=lw * 0.8, alpha=alpha)
    # valves
    for vx in (0.18, 0.32):
        stroke(ctx, [(vx * s, -0.16 * s), (vx * s, -0.015 * s)], INK, lw * 0.8, alpha)
        circle(ctx, vx * s, -0.17 * s, 0.03 * s, fill=GOLD_2, stroke=INK,
               lw=lw * 0.6, alpha=alpha)
    ctx.restore()


def draw_mouse(ctx, p):
    s = p["s"]
    face = p["face"]
    q = p["q"]
    x, y = p["x"], p["y"]
    wq = 1.0 + (1.0 - q) * 0.35
    lw = max(1.1, s * 0.030)

    def P(lx, ly):
        return (x + face * lx * s * wq, y + ly * s * q)

    # tail
    tw = p["tail"]
    base = P(-0.22, -0.45)
    c1 = P(-0.52, -0.50 + 0.06 * math.sin(tw))
    c2 = P(-0.60, -0.18 + 0.10 * math.sin(tw + 0.8))
    tip = P(-0.80, 0.04 + 0.06 * math.sin(tw + 1.3))
    curve_stroke(ctx, [base, c1, c2, tip], INK, 0.044 * s, 1.0)

    # feet
    for foot in (p["leg_l"], p["leg_r"]):
        fx, fy = P(*foot)
        ellipse(ctx, fx, fy, 0.11 * s, 0.05 * s, fill=CREAM, stroke=INK, lw=lw * 0.8)
    # legs
    for hip, foot in (((-0.10, -0.30), p["leg_l"]), ((0.10, -0.30), p["leg_r"])):
        stroke(ctx, [P(*hip), P(*foot)], INK, 0.035 * s, 1.0)

    # body
    ellipse(ctx, *P(0.0, -0.55), 0.285 * s, 0.36 * s,
            fill=(0.78, 0.72, 0.60), stroke=INK, lw=lw)
    ellipse(ctx, *P(0.03, -0.48), 0.17 * s, 0.23 * s, fill=CREAM, alpha=0.85)
    if p["vest"]:
        # little red vest
        ctx.move_to(*P(-0.24, -0.66))
        ctx.curve_to(*P(-0.10, -0.80), *P(0.14, -0.80), *P(0.25, -0.66))
        ctx.curve_to(*P(0.28, -0.44), *P(0.20, -0.30), *P(0.0, -0.28))
        ctx.curve_to(*P(-0.20, -0.30), *P(-0.28, -0.44), *P(-0.24, -0.66))
        ctx.set_source_rgba(*RED, 1)
        ctx.fill()
        ctx.new_path()
        circle(ctx, *P(0.0, -0.53), 0.025 * s, fill=GOLD, stroke=INK, lw=lw * 0.5)
        stroke(ctx, [P(-0.02, -0.68), P(0.02, -0.45)], INK, lw * 0.5, 0.5)
    # arms
    for hand, shoulder in ((p["arm_l"], (-0.22, -0.64)), (p["arm_r"], (0.22, -0.64))):
        p0 = P(*shoulder)
        p3 = P(*hand)
        hose(ctx, p0, p3, bend=(face * -0.04 * s, 0.07 * s), width=0.033 * s)
        circle(ctx, p3[0], p3[1], 0.055 * s, fill=CREAM, stroke=INK, lw=lw * 0.8)

    # ears
    for side in (-1, 1):
        ex, ey = P(side * 0.29, -1.22)
        circle(ctx, ex, ey, 0.245 * s, fill=(0.78, 0.72, 0.60), stroke=INK, lw=lw)
        circle(ctx, ex, ey, 0.145 * s, fill=(0.55, 0.32, 0.27), alpha=0.9)
    # head
    hc = P(0.0, -1.00)
    circle(ctx, hc[0], hc[1], 0.36 * s, fill=(0.80, 0.74, 0.62), stroke=INK, lw=lw)
    # muzzle
    ellipse(ctx, *P(face * 0.11, -0.93), 0.20 * s, 0.15 * s, fill=CREAM)
    # eyes
    for side in (-1, 1):
        ex, ey = P(side * 0.13, -1.05)
        mode = p["eye"]
        if mode in ("happy", "giggle") or (mode == "wink" and side * face < 0):
            pts = []
            for i in range(9):
                u = i / 8
                pts.append((ex + (u - 0.5) * 0.13 * s,
                            ey - 0.02 * s * math.sin(math.pi * u)))
            stroke(ctx, pts, INK, max(1.6, s * 0.035))
        else:
            openness = clamp(p["blink"], 0.15, 1.0)
            ellipse(ctx, ex, ey, 0.065 * s, 0.085 * s * openness, fill=CREAM,
                    stroke=INK, lw=lw * 0.75)
            if openness > 0.4:
                px = ex + p["look"][0] * s
                py = ey + p["look"][1] * s
                circle(ctx, px, py, 0.036 * s, fill=INK)
                circle(ctx, px - 0.01 * s, py - 0.013 * s, 0.011 * s, fill=CREAM)
    # nose
    nx, ny = P(face * 0.11, -0.90)
    circle(ctx, nx, ny, 0.055 * s, fill=RED_2, stroke=INK, lw=lw * 0.6)
    # mouth / teeth
    if p["mouth"] > 0.15:
        ellipse(ctx, *P(face * 0.11, -0.80), 0.065 * s, 0.06 * s * p["mouth"], fill=INK)
        if p["mouth"] > 0.5:
            ellipse(ctx, *P(face * 0.11, -0.77), 0.038 * s, 0.028 * s,
                    fill=(0.70, 0.30, 0.25))
    else:
        stroke(ctx, [(nx - 0.02 * s, ny + 0.045 * s),
                     (nx + 0.02 * s, ny + 0.06 * s),
                     (nx + 0.06 * s, ny + 0.045 * s)], INK, lw * 0.7, 0.9)
        # buck teeth
        poly(ctx, [(nx + 0.005 * s, ny + 0.052 * s),
                   (nx + 0.040 * s, ny + 0.052 * s),
                   (nx + 0.036 * s, ny + 0.095 * s),
                   (nx + 0.010 * s, ny + 0.092 * s)],
             fill=WHITE, stroke=INK, lw=lw * 0.5)
    # whiskers
    for side in (-1, 1):
        for k in range(2):
            stroke(ctx, [(nx + side * 0.10 * s, ny + 0.03 * s + k * 0.03 * s),
                         (nx + side * 0.39 * s, ny - 0.01 * s + k * 0.06 * s)],
                   INK, max(0.7, s * 0.012), 0.65)

    # props
    if p["record"]:
        rx, ry = P(0.0, -1.80)
        draw_record(ctx, rx, ry, 0.66 * s, rot=p["tail"] * 0.4)
    if p["trumpet"]:
        tx, ty = P(face * 0.12, -0.86)
        draw_trumpet(ctx, tx, ty, s * 0.85, face=face)
    if p["giggle"]:
        # little laugh lines
        for side in (-1, 1):
            for k in range(2):
                ex, ey = P(side * (0.48 + k * 0.13), -1.12 - k * 0.06)
                stroke(ctx, [(ex, ey - 0.06 * s), (ex, ey + 0.06 * s)],
                       INK, max(0.8, s * 0.018), 0.55)
