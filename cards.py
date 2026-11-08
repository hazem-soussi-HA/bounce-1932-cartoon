"""Title cards, iris, sing-along banner and other showbiz overlays."""

import math
import random

import cairo

from gfx import (
    INK, INK_SOFT, CREAM, CREAM_2, PAPER, RED, RED_2, GOLD, WHITE,
    TAU, clamp, lerp, smoothstep, ease_out_cubic, ease_in_cubic, ease_out_back,
    ellipse, circle, rect, rrect, poly, stroke, text, text_width, layout_words,
    sunburst, radial_glow, liner, deco_corner, star, note, BLACK,
)


def _damped_bounce(u, amp=60.0, freq=2.15, decay=3.1):
    if u <= 0:
        return 0.0
    return -amp * abs(math.sin(u * math.pi * freq)) * math.exp(-u * decay)


def draw_title_card(ctx, t):
    # black velvet background
    rect(ctx, 0, 0, 960, 720, fill=BLACK)
    radial_glow(ctx, 480, 350, 520, (0.32, 0.20, 0.12), 0.45)
    # very faint deco rays
    sunburst(ctx, 480, 360, 80, 720, 40, CREAM, 0.030, rot=0.05)
    sunburst(ctx, 480, 360, 120, 620, 20, RED, 0.035, rot=0.11)

    # double border + corners
    rect(ctx, 27, 25, 906, 670, fill=None, stroke=CREAM, lw=2.2, alpha=0.9)
    rect(ctx, 39, 37, 882, 646, fill=None, stroke=RED, lw=1.0, alpha=0.55)
    deco_corner(ctx, 27, 25, 1, 1, 58, CREAM, 0.7, 1.2)
    deco_corner(ctx, 933, 25, -1, 1, 58, CREAM, 0.7, 1.2)
    deco_corner(ctx, 27, 695, 1, -1, 58, CREAM, 0.7, 1.2)
    deco_corner(ctx, 933, 695, -1, -1, 58, CREAM, 0.7, 1.2)
    # little diamonds at border midpoints
    for x, y in ((480, 25), (480, 695), (27, 360), (933, 360)):
        poly(ctx, [(x, y - 7), (x + 7, y), (x, y + 7), (x - 7, y)],
             fill=RED, stroke=CREAM, lw=0.8, alpha=0.9)

    # fade the whole centre in
    a = smoothstep(0.05, 0.55, t)
    dy = (1 - ease_out_cubic((t - 0.05) / 0.6)) * 16
    ctx.save()
    ctx.translate(0, dy)

    text(ctx, "A  H A Z E M  P I C T U R E", 480, 127, 15.0,
         color=CREAM, tracking=4.6, alpha=0.80 * a)
    star(ctx, 275, 122, 7, 3, fill=RED, alpha=0.85 * a)
    star(ctx, 685, 122, 7, 3, fill=RED, alpha=0.85 * a)

    # ---- big title ------------------------------------------------------
    size = 132
    tracking = 7.0
    tw = text_width(ctx, "BOUNCE", size, tracking=tracking)
    bar_w = 20
    gap = 26
    group_w = tw + gap + bar_w
    x0 = 480 - group_w / 2
    title_alpha = smoothstep(0.15, 0.75, t) * a
    ybase = 395

    # red offset shadow
    text(ctx, "BOUNCE", x0 + 6, ybase + 7, size, color=RED,
         tracking=tracking, align="left", alpha=0.92 * title_alpha)
    text(ctx, "BOUNCE", x0, ybase, size, color=CREAM,
         tracking=tracking, align="left", alpha=title_alpha)

    # exclamation bar (the ball is its dot)
    bx = x0 + tw + gap + bar_w / 2
    poly(ctx, [(bx - 8, 302), (bx + 8, 302), (bx + 10, 358),
               (bx - 10, 358)], fill=CREAM, alpha=title_alpha)
    # ball drop
    ball_a = smoothstep(0.55, 0.62, t)
    if t < 0.62:
        ball_y = -40
    elif t < 1.02:
        u = (t - 0.62) / 0.40
        ball_y = lerp(-40, 384, ease_in_cubic(u))
    else:
        u = t - 1.02
        ball_y = 384 + _damped_bounce(u, 52, 2.0, 3.4)
    # restful micro-bob
    if t > 2.2:
        ball_y += math.sin(t * 3.1) * 2.2
    squash = 1.0
    if t > 1.02:
        u = t - 1.02
        squash = 1.0 - 0.35 * max(0.0, math.exp(-u * 7) * math.cos(u * 14))
    ellipse(ctx, bx, ball_y, 21.5 / max(0.7, squash), 21.5 * squash,
            fill=RED, stroke=CREAM, lw=1.6, alpha=ball_a)
    circle(ctx, bx - 7, ball_y - 8, 4.0, fill=CREAM, alpha=0.7 * ball_a)

    # rule
    liner(ctx, 480, 438, 170, CREAM, 0.75 * a, 1.2)

    text(ctx, "s t a r r i n g", 480, 476, 14.5, color=CREAM,
         tracking=3.6, alpha=0.78 * a)
    text(ctx, "Whiskers the Cat", 480, 526, 49, family="Z003",
         color=CREAM, weight=cairo.FONT_WEIGHT_NORMAL, alpha=a)
    text(ctx, "w i t h   S Q U E A K", 480, 559, 12.5,
         color=CREAM, tracking=3.2, alpha=0.62 * a)

    liner(ctx, 480, 586, 116, CREAM, 0.5 * a, 1.0)
    text(ctx, "ALL TALKING  •  ALL DANCING  •  ALL BOUNCING", 480, 620, 10.5,
         color=CREAM, tracking=2.4, alpha=0.58 * a)
    text(ctx, "M C M X X X I I", 480, 656, 12.0,
         color=CREAM, tracking=4.0, alpha=0.55 * a)
    ctx.restore()


def draw_end_card(ctx, t):
    """t is absolute time (56.25 .. 60)."""
    rect(ctx, 0, 0, 960, 720, fill=PAPER)
    radial_glow(ctx, 480, 350, 500, CREAM, 0.65)
    sunburst(ctx, 480, 355, 60, 620, 36, RED, 0.055, rot=0.04)
    sunburst(ctx, 480, 355, 80, 520, 24, INK, 0.03, rot=0.09)
    # border
    rect(ctx, 28, 26, 904, 668, fill=None, stroke=INK, lw=2.4)
    rect(ctx, 40, 38, 880, 644, fill=None, stroke=RED, lw=1.1, alpha=0.7)
    deco_corner(ctx, 28, 26, 1, 1, 54, INK, 0.55, 1.1)
    deco_corner(ctx, 932, 26, -1, 1, 54, INK, 0.55, 1.1)
    deco_corner(ctx, 28, 694, 1, -1, 54, INK, 0.55, 1.1)
    deco_corner(ctx, 932, 694, -1, -1, 54, INK, 0.55, 1.1)

    text(ctx, "A  H A Z E M  P I C T U R E", 480, 155, 14,
         color=INK, tracking=4.2, alpha=0.7)

    size = 142
    tracking = 6.0
    tw = text_width(ctx, "THE END", size, tracking=tracking)
    ball_gap = 34
    ball_r = 20
    group_w = tw + ball_gap + ball_r * 2
    x0 = 480 - group_w / 2
    ybase = 398
    text(ctx, "THE END", x0 + 7, ybase + 8, size, color=RED,
         tracking=tracking, align="left", alpha=0.9)
    text(ctx, "THE END", x0, ybase, size, color=INK,
         tracking=tracking, align="left")

    # ball becomes the full stop after THE END
    bx = x0 + tw + ball_gap + ball_r
    # drop/bounce begins right at the start of the end card
    tt = t - 56.20
    if tt < 0.15:
        ba = smoothstep(0.0, 0.15, tt)
        by = -30
    elif tt < 0.46:
        u = (tt - 0.15) / 0.31
        ba = 1.0
        by = lerp(-30, 378, ease_in_cubic(u))
    else:
        ba = 1.0
        by = 378 + _damped_bounce(tt - 0.46, 30, 2.4, 5.0)
    ellipse(ctx, bx, by, ball_r, ball_r, fill=RED, stroke=INK, lw=1.8, alpha=ba)
    circle(ctx, bx - 6, by - 7, 3.6, fill=CREAM, alpha=0.65 * ba)
    # tiny motion arc above the ball
    if 56.2 < t < 57.4:
        ctx.arc(bx, 378, 35, -math.pi * 0.85, -math.pi * 0.15)
        ctx.set_line_width(1.2)
        ctx.set_source_rgba(*INK, 0.25)
        ctx.stroke()
        ctx.new_path()

    text(ctx, "starring Whiskers & Squeak", 480, 480, 38, family="Z003",
         color=RED_2, weight=cairo.FONT_WEIGHT_NORMAL)
    liner(ctx, 480, 512, 150, INK, 0.55, 1.1)
    text(ctx, "ANY SIMILARITY TO ACTUAL CATS IS PURELY COINCIDENTAL",
         480, 548, 10.5, color=INK, tracking=1.55, alpha=0.62)
    text(ctx, "M C M X X X I I", 480, 612, 12.5, color=INK,
         tracking=4.0, alpha=0.62)

    # little end-card MGM-style flourish
    for side in (-1, 1):
        for k in range(3):
            x = 480 + side * (250 + k * 14)
            y = 640 - k * 9
            star(ctx, x, y, 6 - k, 2.4, fill=RED, alpha=0.55 - k * 0.1)


BANNER_LINE1 = "OH, I'M A HAPPY LITTLE CAT"
BANNER_LINE2 = "I BOUNCE ALL DAY!"


def draw_banner(ctx, t):
    """Slide-down sing-along card; t absolute. Returns nothing."""
    if t < 17.35 or t > 21.75:
        return
    if t < 17.75:
        u = (t - 17.35) / 0.40
        dy = -170 * (1 - ease_out_back(u, 1.3))
        a = smoothstep(0.0, 0.4, u)
    elif t > 21.30:
        u = (t - 21.30) / 0.35
        dy = -170 * ease_in_cubic(u)
        a = 1 - smoothstep(0.3, 1.0, u)
    else:
        dy, a = 0.0, 1.0
    ctx.save()
    ctx.translate(0, dy)

    x, y, w, h = 92, 30, 776, 146
    # shadow
    rrect(ctx, x + 6, y + 7, w, h, 5, fill=INK, alpha=0.18 * a)
    rrect(ctx, x, y, w, h, 5, fill=CREAM, stroke=INK, lw=3.0, alpha=a)
    rrect(ctx, x + 9, y + 9, w - 18, h - 18, 3, fill=None,
          stroke=RED, lw=1.1, alpha=0.65 * a)
    # deco corner ticks
    for cx, cy, sx, sy in ((x + 15, y + 15, 1, 1), (x + w - 15, y + 15, -1, 1),
                           (x + 15, y + h - 15, 1, -1),
                           (x + w - 15, y + h - 15, -1, -1)):
        stroke(ctx, [(cx, cy + sy * 14), (cx, cy), (cx + sx * 14, cy)],
               INK, 1.2, 0.6 * a)

    text(ctx, "SING ALONG WITH WHISKERS!", 480, y + 23, 10.5,
         color=RED_2, tracking=2.5, alpha=0.9 * a)

    line1_words = layout_words(ctx, BANNER_LINE1, 480, y + 82, 24.5,
                               color=INK, tracking=0.8, space_extra=2.0)
    line2_words = layout_words(ctx, BANNER_LINE2, 480, y + 127, 31,
                               color=RED_2, tracking=0.8, space_extra=2.0)

    # bouncing ball over the current word
    start = 17.75
    end = 21.30
    if start <= t <= end:
        u = t - start
        if u < 1.80:
            words = line1_words
            idx = int(u / (1.80 / len(words)))
            local = (u % (1.80 / len(words))) / (1.80 / len(words))
            base_y = y + 82 - 24
        else:
            v = u - 1.80
            words = line2_words
            span = max(0.2, end - (start + 1.80))
            idx = min(len(words) - 1, int(v / (span / len(words))))
            local = (v % (span / len(words))) / (span / len(words))
            base_y = y + 127 - 27
        idx = min(idx, len(words) - 1)
        wob = math.sin((t - start) * 19.0) * 2
        bx = words[idx][1]
        by = base_y - abs(math.sin(local * math.pi * 2)) * 18 + wob
        # little trailing arc
        ctx.arc(bx, base_y + 2, 18, math.pi * 1.08, math.pi * 1.92)
        ctx.set_line_width(1.0)
        ctx.set_source_rgba(*RED, 0.35 * a)
        ctx.stroke()
        ctx.new_path()
        circle(ctx, bx, by, 8.0, fill=RED, stroke=INK, lw=1.1, alpha=a)
        circle(ctx, bx - 2.5, by - 3, 2.0, fill=CREAM, alpha=0.75 * a)
    # notes at the ends
    note(ctx, x + 42, y + h - 35, 10, RED_2, 0.55 * a, rot=-0.2)
    note(ctx, x + w - 46, y + h - 30, 9, INK, 0.40 * a, rot=0.25, kind="double")
    ctx.restore()


def iris(ctx, cx, cy, r):
    """Black mask with a circular hole."""
    ctx.save()
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.rectangle(-30, -30, 1020, 780)
    ctx.arc(cx, cy, max(0.5, r), 0, TAU)
    ctx.set_source_rgb(*BLACK)
    ctx.fill()
    ctx.restore()


def draw_pow(ctx, cx, cy, s=1.0, alpha=1.0, shake=0.0):
    ctx.save()
    ctx.translate(cx + math.sin(shake * 60) * 6, cy)
    ctx.rotate(-0.06)
    # starburst
    pts = []
    n = 14
    for i in range(n * 2):
        a = i * math.pi / n
        r = (110 if i % 2 == 0 else 62) * s
        pts.append((math.cos(a) * r * 1.15, math.sin(a) * r))
    poly(ctx, pts, fill=CREAM, stroke=INK, lw=4.0 * s, alpha=alpha)
    poly(ctx, [(x * 0.82, y * 0.82) for x, y in pts], fill=None,
         stroke=RED, lw=2.0 * s, alpha=alpha * 0.8)
    text(ctx, "POW!", 0, 24 * s, 62 * s, color=INK, alpha=alpha)
    # speed lines
    for i in range(6):
        a = -2.5 + i * 0.28
        r0 = 125 * s
        r1 = (150 + 12 * (i % 3)) * s
        stroke(ctx, [(math.cos(a) * r0, math.sin(a) * r0),
                     (math.cos(a) * r1, math.sin(a) * r1)],
               INK, 3.0 * s, alpha * 0.55)
    ctx.restore()


def draw_daze_stars(ctx, cx, cy, t, s=1.0):
    for k in range(5):
        a = t * 3.4 + k * TAU / 5
        x = cx + math.cos(a) * 78 * s
        y = cy + math.sin(a) * 24 * s
        star(ctx, x, y, 12 * s, 5 * s, fill=CREAM, stroke_c=INK, lw=1.6 * s,
             rot=a)


# ---- confetti ------------------------------------------------------------
_rng = random.Random(1932)
_CONFETTI = []
for i in range(150):
    _CONFETTI.append(dict(
        birth=_rng.uniform(48.8, 53.2),
        x0=_rng.uniform(40, 920),
        vx=_rng.uniform(-45, 45),
        vy=_rng.uniform(95, 190),
        phase=_rng.uniform(0, TAU),
        spin=_rng.uniform(-4, 4),
        size=_rng.uniform(3.5, 8.5),
        color=_rng.choice([RED, CREAM, GOLD, INK, RED_2]),
        shape=_rng.choice(["rect", "rect", "circle"]),
    ))
_BURST = []
for i in range(65):
    a = _rng.uniform(0, TAU)
    sp = _rng.uniform(120, 360)
    _BURST.append(dict(
        vx=math.cos(a) * sp,
        vy=math.sin(a) * sp - 80,
        phase=_rng.uniform(0, TAU),
        spin=_rng.uniform(-8, 8),
        size=_rng.uniform(3.0, 7.0),
        color=_rng.choice([RED, CREAM, GOLD, INK]),
        shape=_rng.choice(["rect", "circle"]),
    ))


def draw_confetti(ctx, t):
    if t < 48.8 or t > 58.5:
        return
    for c in _CONFETTI:
        age = t - c["birth"]
        if age < 0 or age > 7.5:
            continue
        x = c["x0"] + c["vx"] * age + math.sin(age * 2.2 + c["phase"]) * 16
        y = -20 + c["vy"] * age
        if y > 730:
            continue
        a = clamp(age * 2) * clamp((7.5 - age) / 1.2)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(c["phase"] + c["spin"] * age)
        if c["shape"] == "rect":
            rect(ctx, -c["size"] / 2, -c["size"] / 4, c["size"], c["size"] / 2,
                 fill=c["color"], alpha=a * 0.9)
        else:
            circle(ctx, 0, 0, c["size"] * 0.4, fill=c["color"], alpha=a * 0.9)
        ctx.restore()
    # central burst at the big chord
    if t >= 52.45:
        age = t - 52.45
        if age < 3.2:
            for c in _BURST:
                x = 480 + c["vx"] * age
                y = 400 + c["vy"] * age + 190 * age * age
                if y > 730:
                    continue
                a = clamp(age * 8) * clamp((3.2 - age) / 1.0)
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(c["phase"] + c["spin"] * age)
                if c["shape"] == "rect":
                    rect(ctx, -c["size"] / 2, -c["size"] / 4,
                         c["size"], c["size"] / 2, fill=c["color"], alpha=a)
                else:
                    circle(ctx, 0, 0, c["size"] * 0.4, fill=c["color"], alpha=a)
                ctx.restore()


def draw_flash(ctx, t):
    """Camera flash at the big finish."""
    if 52.47 < t < 52.75:
        a = 0.65 * (1 - smoothstep(52.47, 52.75, t))
        rect(ctx, 0, 0, 960, 720, fill=WHITE, alpha=a)
