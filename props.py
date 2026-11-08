"""The parlor set and props for BOUNCE! — all ink and warm paper tones."""

import math

import cairo

from gfx import (
    INK, INK_SOFT, CREAM, CREAM_2, PAPER, WALL, WALL_2, FLOOR, FLOOR_2,
    RED, RED_2, GOLD, GOLD_2, OLIVE, OLIVE_2, WHITE, DUST, TAU,
    clamp, lerp, ellipse, circle, rect, rrect, poly, stroke, curve_stroke,
    filled_polygon_curve, ellipse_path, radial_glow, text, star, note,
    sunburst, liner,
)
from characters import draw_record


# -------------------------------------------------------------------------
# Room shell
# -------------------------------------------------------------------------
def draw_rug(ctx, cx=480, cy=662, rx=338, ry=76, lift=0.0):
    # soft shadow
    ellipse(ctx, cx, cy + 6, rx * 0.98, ry * 0.95, fill=INK, alpha=0.10)
    ellipse(ctx, cx, cy, rx, ry, fill=RED, stroke=INK, lw=3.0)
    ellipse(ctx, cx, cy, rx - 12, ry - 9, fill=CREAM_2, stroke=INK, lw=1.6)
    ellipse(ctx, cx, cy, rx - 24, ry - 17, fill=RED, alpha=0.92)
    ellipse(ctx, cx, cy, rx - 37, ry - 24, fill=CREAM, stroke=INK, lw=1.2)
    # deco border dashes
    for i in range(26):
        a = i * TAU / 26
        x = cx + math.cos(a) * (rx - 18)
        y = cy + math.sin(a) * (ry - 13)
        poly(ctx, [(x - 4, y), (x, y - 5), (x + 4, y), (x, y + 5)],
             fill=INK, alpha=0.55)
    # central medallion
    poly(ctx, [(cx, cy - 28), (cx + 34, cy), (cx, cy + 28), (cx - 34, cy)],
         fill=RED, stroke=INK, lw=1.4, alpha=0.9)
    poly(ctx, [(cx, cy - 15), (cx + 18, cy), (cx, cy + 15), (cx - 18, cy)],
         fill=CREAM, alpha=0.85)
    ellipse(ctx, cx, cy, 6, 5, fill=INK)
    # fringe
    for i in range(40):
        a = math.pi * 0.08 + i * (math.pi * 0.84) / 39
        x0 = cx + math.cos(a) * rx
        y0 = cy + math.sin(a) * ry
        x1 = cx + math.cos(a) * (rx + 7)
        y1 = cy + math.sin(a) * (ry + 9)
        stroke(ctx, [(x0, y0), (x1, y1)], RED_2 if i % 2 else INK, 1.0, 0.5)


def draw_room_shell(ctx, t=0.0):
    # wallpaper
    rect(ctx, 0, 0, 960, 532, fill=WALL)
    for x in range(-20, 980, 28):
        rect(ctx, x, 0, 11, 512, fill=WALL_2, alpha=0.28)
    # subtle vertical gradient of light from the lamp
    radial_glow(ctx, 480, 135, 520, CREAM, 0.17)
    # picture rail
    stroke(ctx, [(0, 300), (960, 300)], INK, 2.0, 0.20)
    for x in (90, 300, 520, 740, 910):
        rect(ctx, x - 5, 300, 10, 7, fill=WALL, stroke=INK, lw=1.2, alpha=0.5)
    # floor
    rect(ctx, 0, 520, 960, 200, fill=FLOOR)
    for i, y in enumerate(range(548, 740, 34)):
        stroke(ctx, [(0, y), (960, y)], FLOOR_2, 1.4, 0.55)
    for i in range(7):
        x = (i * 167 + 40) % 960
        stroke(ctx, [(x, 548), (x - 20, 720)], FLOOR_2, 1.0, 0.30)
    # baseboard
    rect(ctx, 0, 508, 960, 26, fill=CREAM_2)
    stroke(ctx, [(0, 508), (960, 508)], INK, 2.0, 0.8)
    stroke(ctx, [(0, 522), (960, 522)], INK, 1.0, 0.35)
    stroke(ctx, [(0, 533), (960, 533)], INK, 2.0, 0.7)
    # floor shadow at baseboard
    rect(ctx, 0, 534, 960, 18, fill=INK, alpha=0.10)
    draw_rug(ctx)


def draw_plant(ctx, t=0.0, sway=0.0):
    x, base = 52, 620
    # pot
    ellipse(ctx, x, base, 44, 11, fill=INK, alpha=0.15)
    poly(ctx, [(x - 34, base - 86), (x + 34, base - 86),
               (x + 25, base), (x - 25, base)],
         fill=RED, stroke=INK, lw=3.0)
    rect(ctx, x - 37, base - 92, 74, 12, fill=RED_2, stroke=INK, lw=2.0)
    rect(ctx, x - 28, base - 70, 56, 8, fill=CREAM, alpha=0.75)
    # leaves
    stems = [(-62, 330, -0.35), (-35, 300, -0.1), (4, 285, 0.08),
             (38, 315, 0.3), (58, 360, 0.55)]
    for i, (dx, top, ang) in enumerate(stems):
        sw = sway * math.sin(t * 1.7 + i) * 6
        p0 = (x, base - 86)
        p1 = (x + dx * 0.4 + sw, (p0[1] + top) / 2)
        p2 = (x + dx + sw * 1.4, top)
        ctx.move_to(*p0)
        ctx.curve_to(*p1, *p1, *p2)
        ctx.set_line_width(4.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(*OLIVE_2, 0.9)
        ctx.stroke()
        ctx.new_path()
        # long leaves along the stem
        for j in range(4):
            u = 0.25 + j * 0.18
            lx = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
            ly = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
            side = 1 if j % 2 == 0 else -1
            ellipse(ctx, lx + side * 17, ly - 5, 22, 7, fill=OLIVE,
                    stroke=OLIVE_2, lw=1.0, rot=side * (0.5 + ang * 0.4))
    # a couple of art-deco leaves at the top
    for i, (dx, top, ang) in enumerate(stems):
        sw = sway * math.sin(t * 1.7 + i) * 6
        x2 = x + dx + sw * 1.4
        ellipse(ctx, x2, top + 8, 9, 22, fill=OLIVE, stroke=OLIVE_2,
                lw=1.0, rot=ang)


def draw_pendant_lamp(ctx, t=0.0, swing=0.0):
    amp = 0.012 + swing * 0.035
    ang = math.sin(t * 2.2) * amp
    ctx.save()
    ctx.translate(480, 0)
    ctx.rotate(ang)
    # cord
    stroke(ctx, [(0, 0), (0, 78)], INK, 2.0, 0.8)
    # shade
    poly(ctx, [(-44, 116), (-28, 78), (28, 78), (44, 116)],
         fill=GOLD, stroke=INK, lw=2.4)
    ellipse(ctx, 0, 78, 28, 7, fill=GOLD_2, stroke=INK, lw=1.4)
    ellipse(ctx, 0, 116, 44, 8, fill=CREAM, stroke=INK, lw=2.0)
    # bulb
    circle(ctx, 0, 128, 7, fill=CREAM)
    radial_glow(ctx, 0, 128, 95, CREAM, 0.30)
    ctx.restore()
    # soft floor pool of light
    ellipse(ctx, 480 + math.sin(t * 2.2) * amp * 320, 660, 300, 65,
            fill=CREAM, alpha=0.035)


def draw_portrait(ctx, t=0.0, bob=0.0):
    cx, cy = 532, 194
    dy = bob * math.sin(t * 4.4) * 4
    ctx.save()
    ctx.translate(cx, cy + dy)
    ctx.rotate(bob * math.sin(t * 2.2) * 0.012)
    # frame
    rrect(ctx, -79, -57, 158, 114, 4, fill=GOLD_2, stroke=INK, lw=3.0)
    rrect(ctx, -69, -47, 138, 94, 2, fill=INK, stroke=INK, lw=1.0)
    rrect(ctx, -64, -42, 128, 84, 2, fill=PAPER)
    # fish portrait
    ellipse(ctx, -2, 0, 40, 22, fill=OLIVE, stroke=INK, lw=1.6)
    poly(ctx, [(-39, -2), (-58, -20), (-56, 15)], fill=OLIVE, stroke=INK, lw=1.4)
    ellipse(ctx, 31, 0, 15, 18, fill=OLIVE, stroke=INK, lw=1.4)
    circle(ctx, 35, -4, 3.2, fill=INK)
    circle(ctx, 35.8, -4.8, 1.0, fill=CREAM)
    stroke(ctx, [(26, 9), (34, 12), (41, 8)], INK, 1.4, 0.8)
    # top hat on the fish
    rect(ctx, 20, -25, 22, 13, fill=INK)
    rect(ctx, 15, -13, 32, 4, fill=INK)
    rect(ctx, 20, -19, 22, 4, fill=RED)
    # bubbles
    for i, (bx, by, r) in enumerate(((-20, -18, 3), (-14, -26, 2), (-25, -30, 1.5))):
        circle(ctx, bx, by, r, fill=CREAM, stroke=INK, lw=0.7)
    # bow tie
    poly(ctx, [(-7, 20), (0, 17), (0, 25), (-7, 28)], fill=RED, stroke=INK, lw=0.7)
    poly(ctx, [(7, 20), (0, 17), (0, 25), (7, 28)], fill=RED, stroke=INK, lw=0.7)
    circle(ctx, 0, 22.5, 2.4, fill=RED_2, stroke=INK, lw=0.5)
    # name plate
    rect(ctx, -34, 49, 68, 13, fill=GOLD, stroke=INK, lw=1.0)
    text(ctx, "GRANDPA FINN", 0, 59, 8, color=INK, tracking=0.8)
    ctx.restore()


def draw_mouse_hole(ctx):
    # arch cut into the baseboard
    x, y = 912, 532
    ctx.move_to(x - 34, y)
    ctx.line_to(x - 34, y - 45)
    ctx.curve_to(x - 34, y - 78, x + 34, y - 78, x + 34, y - 45)
    ctx.line_to(x + 34, y)
    ctx.close_path()
    ctx.set_source_rgba(0.045, 0.035, 0.03, 1)
    ctx.fill()
    ctx.new_path()
    # rough wooden rim
    ctx.arc(x, y - 48, 37, math.pi, TAU)
    ctx.set_line_width(4.0)
    ctx.set_source_rgba(*INK, 0.85)
    ctx.stroke()
    ctx.new_path()
    # tiny welcome mat and cheese crumb
    ellipse(ctx, x, y + 4, 39, 7, fill=RED, stroke=INK, lw=1.2, alpha=0.85)
    poly(ctx, [(x + 38, y + 1), (x + 52, y + 2), (x + 50, y - 10)],
         fill=GOLD, stroke=INK, lw=1.2)
    for dx, dy in ((43, -3), (47, -5), (45, -8)):
        circle(ctx, x + dx, y + dy, 1.2, fill=INK, alpha=0.7)


# -------------------------------------------------------------------------
# Furniture
# -------------------------------------------------------------------------
def draw_chair(ctx, t=0.0):
    cx = 230
    # legs
    for lx in (148, 325):
        poly(ctx, [(lx - 7, 548), (lx + 7, 548), (lx + 4, 620), (lx - 5, 620)],
             fill=FLOOR_2, stroke=INK, lw=2.0)
        ellipse(ctx, lx, 621, 12, 5, fill=FLOOR_2, stroke=INK, lw=1.4)
    # back
    rrect(ctx, 112, 335, 238, 200, 56, fill=RED, stroke=INK, lw=3.4)
    # inner back panel
    rrect(ctx, 132, 355, 198, 168, 45, fill=RED_2, alpha=0.32)
    # frosting / piping
    rrect(ctx, 128, 350, 206, 176, 48, fill=None, stroke=CREAM, lw=1.6, alpha=0.75)
    # tufting
    for x in (188, 230, 272):
        stroke(ctx, [(x, 372), (x, 464)], INK, 1.2, 0.30)
    for x, y in ((195, 395), (265, 395), (195, 440), (265, 440)):
        circle(ctx, x, y, 3.2, fill=RED_2, stroke=INK, lw=0.8, alpha=0.8)
    # arms
    for ax, flip in ((116, -1), (344, 1)):
        ellipse(ctx, ax, 498, 50, 33, fill=RED, stroke=INK, lw=3.0)
        ellipse(ctx, ax, 493, 39, 22, fill=RED_2, alpha=0.4)
        stroke(ctx, [(ax - flip * 24, 477), (ax + flip * 18, 477)],
               CREAM, 1.8, 0.55)
    # seat cushion
    rrect(ctx, 116, 498, 226, 60, 25, fill=RED, stroke=INK, lw=3.2)
    rrect(ctx, 128, 505, 202, 44, 19, fill=CREAM, alpha=0.10)
    stroke(ctx, [(135, 526), (322, 526)], CREAM, 1.4, 0.35)
    # antimacassar doily
    ctx.save()
    ctx.translate(cx, 365)
    ellipse(ctx, 0, 0, 52, 17, fill=CREAM, alpha=0.92)
    for i in range(12):
        a = i * TAU / 12
        circle(ctx, math.cos(a) * 52, math.sin(a) * 14, 4.5, fill=CREAM, alpha=0.92)
    ctx.arc(0, 0, 31, 0, TAU)
    ctx.set_line_width(1.0)
    ctx.set_source_rgba(*RED, 0.35)
    ctx.stroke()
    ctx.new_path()
    ctx.restore()
    # slight shadow
    ellipse(ctx, cx, 624, 152, 10, fill=INK, alpha=0.12)


def draw_gramophone(ctx, cx=770, top=452, t=0.0, playing=False,
                    record_on=True, crank=0.0, spin=0.0, wobble=0.0):
    # cabinet
    ellipse(ctx, cx + 4, 630, 122, 10, fill=INK, alpha=0.12)
    rrect(ctx, cx - 92, top, 184, 132, 5, fill=FLOOR_2, stroke=INK, lw=3.2)
    rect(ctx, cx - 92, top + 8, 184, 13, fill=CREAM_2, alpha=0.35)
    rrect(ctx, cx - 72, top + 36, 144, 72, 3, fill=None, stroke=INK, lw=1.4, alpha=0.5)
    # art-deco inlay
    poly(ctx, [(cx - 36, top + 58), (cx, top + 42), (cx + 36, top + 58),
               (cx + 36, top + 88), (cx, top + 104), (cx - 36, top + 88)],
         fill=None, stroke=GOLD, lw=1.4, alpha=0.85)
    poly(ctx, [(cx, top + 58), (cx + 16, top + 73), (cx, top + 88), (cx - 16, top + 73)],
         fill=GOLD, alpha=0.25)
    # knobs
    circle(ctx, cx - 58, top + 120, 4, fill=GOLD, stroke=INK, lw=1.0)
    circle(ctx, cx + 58, top + 120, 4, fill=GOLD, stroke=INK, lw=1.0)
    # little legs
    for lx in (cx - 72, cx + 72):
        poly(ctx, [(lx - 5, top + 132), (lx + 5, top + 132), (lx + 3, 620), (lx - 3, 620)],
             fill=FLOOR_2, stroke=INK, lw=1.5)

    # horn (behind base)
    ctx.save()
    ctx.translate(cx - 58, top - 52)
    ctx.rotate(wobble)
    # neck
    ctx.move_to(31, 5)
    ctx.curve_to(8, -30, -5, -62, -32, -90)
    ctx.curve_to(-45, -104, -62, -110, -77, -107)
    ctx.line_to(-73, -78)
    ctx.curve_to(-55, -78, -37, -64, -28, -48)
    ctx.curve_to(-20, -33, -8, -8, 14, 14)
    ctx.close_path()
    ctx.set_source_rgba(*GOLD, 1)
    ctx.fill_preserve()
    ctx.set_line_width(2.8)
    ctx.set_source_rgba(*INK, 1)
    ctx.stroke()
    ctx.new_path()
    # bell
    ellipse(ctx, -81, -93, 27, 45, fill=GOLD_2, stroke=INK, lw=3.0, rot=-0.35)
    ellipse(ctx, -84, -93, 17, 34, fill=(0.16, 0.12, 0.09), rot=-0.35)
    ellipse(ctx, -84, -93, 14, 28, fill=GOLD, alpha=0.20, rot=-0.35)
    # ribs
    for k in range(3):
        a = -0.35 + (k - 1) * 0.25
        x0 = -81 + math.cos(a) * 8
        y0 = -93 + math.sin(a) * 8
        x1 = -81 + math.cos(a) * 26
        y1 = -93 + math.sin(a) * 44
        stroke(ctx, [(x0, y0), (x1, y1)], INK, 1.0, 0.35)
    ctx.restore()

    # base box
    rrect(ctx, cx - 58, top - 52, 116, 52, 4, fill=FLOOR, stroke=INK, lw=2.8)
    rect(ctx, cx - 50, top - 46, 100, 9, fill=CREAM, alpha=0.18)
    # turntable
    ellipse(ctx, cx, top - 54, 46, 15, fill=GOLD_2, stroke=INK, lw=2.2)
    if record_on:
        rot = spin
        draw_record(ctx, cx, top - 58, 38, rot=rot)
        # tone arm
        stroke(ctx, [(cx + 47, top - 47), (cx + 29, top - 64), (cx + 10, top - 62)],
               GOLD, 3.4, 0.95)
        circle(ctx, cx + 47, top - 47, 4.5, fill=GOLD, stroke=INK, lw=1.2)
        circle(ctx, cx + 10, top - 62, 3.0, fill=INK)
        # little sound waves
        if playing:
            for k in range(3):
                phase = (t * 1.3 + k / 3) % 1
                a = 0.28 * (1 - phase)
                rr = 50 + phase * 42
                ctx.arc(cx - 160, top - 135, rr, math.pi * 0.62, math.pi * 1.25)
                ctx.set_line_width(2.0)
                ctx.set_source_rgba(*CREAM, a)
                ctx.stroke()
                ctx.new_path()
    # crank on the left face
    bx, by = cx - 64, top - 20
    cang = crank
    ex = bx + math.cos(cang) * 27
    ey = by + math.sin(cang) * 15
    stroke(ctx, [(bx, by), (ex, ey)], GOLD_2, 4.0, 1.0)
    circle(ctx, ex, ey, 5.0, fill=GOLD, stroke=INK, lw=1.4)
    circle(ctx, bx, by, 3.5, fill=GOLD_2, stroke=INK, lw=1.0)


def draw_clock(ctx, x=398, y=550, t=0.0, ringing=0.0, hop=0.0):
    """Alarm clock perched on the chair's armrest."""
    y = y - hop
    shake = math.sin(t * 55) * 2.0 * ringing
    ctx.save()
    ctx.translate(x + shake, y)
    # bells
    for side in (-1, 1):
        circle(ctx, side * 18, -37, 12, fill=GOLD, stroke=INK, lw=2.0)
        stroke(ctx, [(side * 18, -49), (side * 18, -55)], INK, 1.6, 0.8)
    # body
    circle(ctx, 0, -14, 30, fill=CREAM, stroke=INK, lw=2.8)
    circle(ctx, 0, -14, 23, fill=CREAM_2, stroke=INK, lw=1.2)
    # hands at 7:00
    stroke(ctx, [(0, -14), (-9, -20)], INK, 2.0)
    stroke(ctx, [(0, -14), (7, -3)], INK, 2.0)
    circle(ctx, 0, -14, 2.4, fill=INK)
    for i in range(12):
        a = i * TAU / 12
        stroke(ctx, [(math.cos(a) * 20, -14 + math.sin(a) * 20),
                     (math.cos(a) * 23, -14 + math.sin(a) * 23)],
               INK, 1.0, 0.55)
    # legs
    for side in (-1, 1):
        stroke(ctx, [(side * 14, 13), (side * 20, 22)], INK, 2.0)
    # little hammer
    stroke(ctx, [(0, -48), (0, -55)], INK, 1.8, 0.8)
    if ringing > 0.05:
        for side in (-1, 1):
            for k in range(3):
                rr = 36 + k * 11
                ctx.arc(0, -20, rr, side * 0.5 + (0 if side > 0 else math.pi),
                        (0 if side > 0 else math.pi) + math.pi - side * 0.5)
                ctx.set_line_width(1.6)
                ctx.set_source_rgba(*INK, 0.5 * ringing)
                ctx.stroke()
                ctx.new_path()
    ctx.restore()


# -------------------------------------------------------------------------
# Banjo + assorted stage dressing
# -------------------------------------------------------------------------
def draw_banjo(ctx, x, y, s=150, t=0.0, strum=0.0, face=1):
    """A banjo held across the cat's body. x,y = cat feet."""
    # neck from body to upper left, kept low so it never crosses the face
    nx0, ny0 = x + 0.10 * s, y - 0.60 * s
    nx1, ny1 = x - 0.55 * s, y - 1.00 * s
    # resonator / head
    bx, by = x + 0.20 * s, y - 0.58 * s
    # neck
    ang = math.atan2(ny1 - ny0, nx1 - nx0)
    ctx.save()
    ctx.translate(nx0, ny0)
    ctx.rotate(ang)
    ctx.rectangle(0, -4.5, math.hypot(nx1 - nx0, ny1 - ny0), 9)
    ctx.set_source_rgba(0.46, 0.29, 0.16, 1)
    ctx.fill_preserve()
    ctx.set_line_width(1.8)
    ctx.set_source_rgba(*INK, 1)
    ctx.stroke()
    ctx.new_path()
    for k in range(7):
        xx = 12 + k * 13
        stroke(ctx, [(xx, -5), (xx, 5)], INK, 1.0, 0.4)
    ctx.restore()
    # headstock
    ctx.save()
    ctx.translate(nx1, ny1)
    ctx.rotate(ang)
    rrect(ctx, -10, -9, 26, 18, 5, fill=(0.40, 0.25, 0.14), stroke=INK, lw=1.6)
    for k in range(3):
        circle(ctx, 2 + k * 5, -11, 1.8, fill=CREAM, stroke=INK, lw=0.5)
    ctx.restore()
    # body
    circle(ctx, bx, by, 0.27 * s, fill=CREAM, stroke=INK, lw=3.0)
    circle(ctx, bx, by, 0.235 * s, fill=CREAM_2, stroke=INK, lw=1.0)
    circle(ctx, bx, by, 0.155 * s, fill=CREAM, stroke=INK, lw=1.0)
    for k in range(8):
        a = k * TAU / 8
        circle(ctx, bx + math.cos(a) * 0.20 * s, by + math.sin(a) * 0.20 * s,
               2.0, fill=INK, alpha=0.6)
    # strings
    for off in (-4, 0, 4):
        stroke(ctx, [(bx + off * 0.5, by - 0.20 * s),
                     (nx1 + off * 0.35, ny1 + 6)], CREAM, 1.0, 0.65)
    # bridge
    stroke(ctx, [(bx - 12, by + 28), (bx + 12, by + 28)], (0.40, 0.25, 0.14), 4.0, 1.0)
    # strumming hand blur
    if strum:
        hy = by + 0.05 * s + strum * 12
        for k in range(3):
            stroke(ctx, [(bx + 0.20 * s + k * 2, hy - 10 + k * 7),
                         (bx + 0.31 * s + k * 2, hy + 10 + k * 7)],
                   INK, 1.2, 0.35)
    return (bx, by), (nx1, ny1)


def draw_thimble_stool(ctx, x=620, y=620, s=1.0):
    ellipse(ctx, x, y, 57 * s, 14 * s, fill=RED, stroke=INK, lw=2.2)
    ellipse(ctx, x, y - 6 * s, 49 * s, 11 * s, fill=RED_2)
    for k in range(4):
        a = k * TAU / 4 + math.pi / 4
        stroke(ctx, [(x + math.cos(a) * 35 * s, y - 6 * s),
                     (x + math.cos(a) * 42 * s, y + 18 * s)], INK, 3.0 * s, 0.75)


def draw_side_table(ctx, x=398, top=565):
    """Small round table for the alarm clock, right of the chair."""
    ellipse(ctx, x, 626, 52, 8, fill=INK, alpha=0.12)
    # top
    ellipse(ctx, x, top, 56, 14, fill=FLOOR_2, stroke=INK, lw=2.6)
    ellipse(ctx, x, top - 4, 49, 11, fill=CREAM, alpha=0.28)
    # doily
    ellipse(ctx, x, top - 6, 43, 9, fill=CREAM, alpha=0.55)
    for i in range(10):
        a = i * TAU / 10
        circle(ctx, x + math.cos(a) * 43, top - 6 + math.sin(a) * 8.5, 3.0,
               fill=CREAM, alpha=0.55)
    # legs
    for dx in (-32, 0, 32):
        stroke(ctx, [(x + dx * 0.75, top + 4),
                     (x + dx, 624)], INK, 3.0, 0.9)
    # lower ring
    ctx.arc(x, top + 34, 30, 0.1 * math.pi, 0.9 * math.pi)
    ctx.set_line_width(1.6)
    ctx.set_source_rgba(*INK, 0.55)
    ctx.stroke()
    ctx.new_path()


def draw_curtain(ctx, t=0.0):
    """Little velvet curtain bunches at the screen edges (stage feel)."""
    for side in (-1, 1):
        x = 0 if side < 0 else 960
        pts = [(x, 0), (x + side * 74, 0), (x + side * 58, 130),
               (x + side * 86, 250), (x + side * 54, 380), (x + side * 40, 500),
               (x, 540)]
        poly(ctx, pts, fill=RED_2, alpha=0.98)
        for k in range(4):
            xx = x + side * (12 + k * 17)
            stroke(ctx, [(xx, 0), (xx + side * 7, 520)], INK, 2.2, 0.35)
        stroke(ctx, [(x + side * 62, 0), (x + side * 46, 520)], GOLD, 2.0, 0.35)
