"""Choreography and scene assembly for BOUNCE! (1932)."""

import math
import random

import cairo

from gfx import (
    INK, INK_SOFT, CREAM, CREAM_2, PAPER, WALL, RED, RED_2, GOLD, GOLD_2,
    OLIVE, WHITE, DUST, TAU, clamp, lerp, smoothstep, ease_out_cubic,
    ease_in_cubic, ease_in_out, ease_out_back, pulse, ellipse, circle, rect,
    poly, stroke, text, note, star, sparkle, radial_glow, liner,
)
from characters import (
    cat_pose, draw_cat, draw_sleeping_cat, draw_zzz, mouse_pose, draw_mouse,
    draw_glove, draw_boater, draw_record,
)
from props import (
    draw_room_shell, draw_plant, draw_pendant_lamp, draw_portrait, draw_chair,
    draw_side_table, draw_mouse_hole, draw_gramophone, draw_clock,
    draw_banjo, draw_thimble_stool, draw_curtain,
)
from cards import (
    draw_title_card, draw_end_card, draw_banner, iris, draw_pow,
    draw_daze_stars, draw_confetti, draw_flash,
)
from timeline import *

FLOOR_Y = 615
MOUSE_Y = 620


def track(t, keys, ease=ease_in_out):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0)
            return lerp(v0, v1, ease(u))
    return keys[-1][1]


def cat_hand_pos(p, which):
    s = p["s"]
    q = p["q"]
    wq = 1.0 + (1.0 - q) * 0.38
    if q > 1.0:
        wq = 1.0 - (q - 1.0) * 0.28
    lx, ly = p[which]
    return (p["x"] + p["face"] * lx * s * wq, p["y"] + ly * s * q)


# -------------------------------------------------------------------------
# environment
# -------------------------------------------------------------------------
def draw_environment(ctx, t):
    draw_room_shell(ctx, t)
    music = 14.4 <= t < 23.9
    jam = JAM <= t < IRIS_OUT
    if music:
        swing = 0.25
    elif jam:
        swing = 1.0
    else:
        swing = 0.0
    draw_plant(ctx, t, swing * 0.8)
    draw_pendant_lamp(ctx, t, swing)
    bob = 0.3 if music else 0.0
    if jam:
        bob = 1.2
    draw_portrait(ctx, t, bob)
    draw_chair(ctx, t)
    draw_side_table(ctx, 398, 565)
    draw_mouse_hole(ctx)

    record_on = not (23.72 <= t < 60.0)
    spin = max(0.0, t - 14.4) * 7.0
    if 13.05 < t < 14.15:
        crank = (t - 13.05) * 20.0
    else:
        crank = 0.9
    wob = 0.0
    if 33.30 < t < 34.6:
        u = t - 33.30
        wob = math.sin(u * 40.0) * 0.13 * math.exp(-u * 3.2)
    draw_gramophone(ctx, cx=770, top=452, t=t, playing=music,
                    record_on=record_on, crank=crank, spin=spin, wobble=wob)

    # alarm clock on its little table
    ring = smoothstep(7.02, 7.08, t) * (1.0 - smoothstep(7.55, 7.72, t))
    hop = abs(math.sin((t - 7.05) * 26.0)) * 7.0 * ring
    if jam:
        hop += abs(math.sin((t - JAM) * TAU / SPB)) * 2.0
    draw_clock(ctx, 398, 548, t=t, ringing=ring, hop=hop)


# -------------------------------------------------------------------------
# little effects
# -------------------------------------------------------------------------
def exclaim(ctx, x, y, s=1.0, a=1.0, color=RED):
    text(ctx, "!", x + 4, y + 3, 52 * s, color=INK, alpha=0.5 * a)
    text(ctx, "!", x, y, 52 * s, color=color, alpha=a)


def speed_lines(ctx, x, y, face, t, a=0.35, spread=1.0):
    for k in range(4):
        yy = y - 45 - k * 34 * spread + math.sin(t * 30 + k) * 4
        x0 = x - face * (75 + k * 20)
        x1 = x0 - face * (45 + 18 * (k % 2) + 12 * math.sin(t * 23 + k))
        stroke(ctx, [(x0, yy), (x1, yy)], INK, 2.0 - k * 0.2, a)


def dust_puffs(ctx, x, y, face, t, a=0.45, spread=1.0):
    for k in range(4):
        age = (t * 3.2 + k * 0.24) % 1.0
        px = x - face * (20 + age * 90) * spread
        py = y - 3 - age * 26
        r = (7 + age * 14) * spread
        circle(ctx, px, py, r, fill=DUST, alpha=(1 - age) * a)
        circle(ctx, px - face * r * 0.4, py - r * 0.3, r * 0.6,
               fill=CREAM, alpha=(1 - age) * a * 0.5)


def note_stream(ctx, t, start, end, sx, sy, period=0.45, drift=40,
                color=INK, size=10, max_age=2.5, spread=1.0):
    k = 0
    birth = start
    while birth < end + max_age and k < 70:
        age = t - birth
        if 0.0 <= age < max_age:
            u = age / max_age
            nx = sx + drift * math.sin(age * 2.3 + k * 1.7) * u * spread
            ny = sy - 150 * u
            a = clamp(age * 6) * (1 - u) * 0.8
            kind = "eighth" if k % 3 else "double"
            note(ctx, nx, ny, size * (0.8 + 0.35 * math.sin(k * 2.1)),
                 color, alpha=a, rot=0.18 * math.sin(age * 2 + k), kind=kind)
        birth += period
        k += 1


def sparkle_burst(ctx, x, y, t, t0, a=1.0):
    age = t - t0
    if age < 0 or age > 0.55:
        return
    for k in range(6):
        ang = k * TAU / 6 + 0.3
        r = 15 + age * 80
        sparkle(ctx, x + math.cos(ang) * r, y + math.sin(ang) * r,
                8 * (1 - age / 0.55), CREAM, a, 2.0)


# -------------------------------------------------------------------------
# acts
# -------------------------------------------------------------------------
def sleep_and_startle(ctx, t):
    if t < 7.35:
        eyes = t > 7.16
        draw_sleeping_cat(ctx, 232, 505, s=145, breath=t * 4.2, eyes_open=eyes)
        draw_zzz(ctx, 355, 380, t, 1.0)
        if t > 7.16:
            exclaim(ctx, 255, 390, 0.7, smoothstep(7.16, 7.22, t))
        return

    # pop out of the chair, sail across the room, land on the rug
    u = clamp((t - 7.35) / 0.60)
    x = lerp(267, 475, ease_in_out(u))
    y = 505 + (FLOOR_Y - 505) * u - 155 * math.sin(math.pi * u)
    q = 1.06 - 0.20 * smoothstep(0.82, 1.0, u)
    eye = "wide"
    p = cat_pose(x, y, s=150, face=1, q=q, eye=eye, look=(0.02, -0.02),
                 arm_l=(-0.66, -1.55), arm_r=(0.66, -1.52),
                 leg_l=(-0.30, -0.16), leg_r=(0.32, -0.12),
                 mouth=0.55, tongue=True, tail=14.0 * t, tail_lift=0.8,
                 blush=1.0)
    draw_cat(ctx, p)
    speed_lines(ctx, x, y - 40, -1, t, 0.25, 1.2)
    # pop cloud at the chair
    if u < 0.3:
        for k in range(5):
            ang = k * TAU / 5
            circle(ctx, 270 + math.cos(ang) * 40, 470 + math.sin(ang) * 30,
                   16, fill=CREAM, alpha=0.55 * (1 - u / 0.3))
    exclaim(ctx, x + 35, y - 270, 1.0, smoothstep(0.0, 0.15, u))
    # startle motion arcs
    for k in range(3):
        ctx.arc(x, y - 115, 95 + k * 18, -2.6 + k * 0.1, -1.2 + k * 0.1)
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(*INK, 0.20)
        ctx.stroke()
        ctx.new_path()


def morning(ctx, t):
    x = 475
    q = 1.0
    arm_l = (-0.52, -0.78)
    arm_r = (0.52, -0.78)
    eye = "open"
    look = (0.03, 0.0)
    mouth = 0.0
    smile = 1.0
    htilt = 0.0
    hy = 0.0
    tongue = False
    if t < 8.5:
        q = lerp(0.82, 1.0, smoothstep(8.12, 8.46, t))
        eye = "open"
    elif t < 9.45:
        # big yawn and stretch
        u = smoothstep(8.48, 8.75, t) * (1 - smoothstep(9.15, 9.45, t))
        q = 1.0 + 0.10 * u
        arm_l = (-0.42, -1.72)
        arm_r = (0.42, -1.72)
        htilt = -0.15 * u
        hy = -0.02 * u
        eye = "happy"
        mouth = u
        tongue = True
        smile = 0.4
    elif t < 10.15:
        # scratch behind the ear
        u = smoothstep(9.55, 9.7, t)
        arm_r = (0.30, -1.43)
        arm_l = (-0.32, -0.70)
        htilt = 0.10
        eye = "wink" if u > 0.4 else "open"
        mouth = 0.1
        look = (-0.02, -0.01)
        x = 475 + 2 * math.sin(t * 25)
    elif t < 10.72:
        # wet-dog shake
        u = (t - 10.15) / 0.57
        x = 475 + 8 * math.sin(u * 42)
        q = 1.0 + 0.04 * math.sin(u * 55)
        htilt = 0.08 * math.sin(u * 42)
        eye = "happy"
        mouth = 0.25
        arm_l = (-0.62, -0.82 + 0.12 * math.sin(u * 42))
        arm_r = (0.62, -0.82 - 0.12 * math.sin(u * 42))
        tail = 30 * u
        for k in range(3):
            ctx.arc(x, 430, 100 + k * 14, 0.4, 2.4)
            ctx.set_line_width(1.6)
            ctx.set_source_rgba(*INK, 0.18)
            ctx.stroke()
            ctx.new_path()
    else:
        # bounce toward the gramophone, face the new groove
        u = smoothstep(10.72, 11.25, t)
        x = 475 + 60 * u
        hop = abs(math.sin(u * math.pi * 2)) * 12
        q = 0.96 + 0.04 * math.sin(u * math.pi * 4)
        y = FLOOR_Y - hop
        arm_l = (-0.55, -0.85)
        arm_r = (0.58, -0.9)
        eye = "happy"
        mouth = 0.35
        tongue = True
        p = cat_pose(x, y, s=150, face=1, q=q, eye=eye, look=look,
                     arm_l=arm_l, arm_r=arm_r, mouth=mouth, smile=smile,
                     tongue=tongue, htilt=htilt, hy=hy, blush=0.7)
        draw_cat(ctx, p)
        note_stream(ctx, t, 10.8, 11.25, x + 40, 360, 0.5, 25, RED_2, 9)
        return

    p = cat_pose(x, FLOOR_Y, s=150, face=1, q=q, eye=eye, look=look,
                 arm_l=arm_l, arm_r=arm_r, mouth=mouth, smile=smile,
                 tongue=tongue, htilt=htilt, hy=hy, blush=0.6)
    draw_cat(ctx, p)
    if t >= 9.45 and t < 10.15:
        # scratch lines
        for k in range(2):
            ctx.arc(x + 52, 405, 30 + k * 8, -1.2, 1.0)
            ctx.set_line_width(1.4)
            ctx.set_source_rgba(*INK, 0.35)
            ctx.stroke()
            ctx.new_path()


def gramophone_act(ctx, t):
    if t < 12.75:
        u = clamp((t - 11.25) / 1.50)
        x = lerp(535, 650, ease_in_out(u))
        hop = 38 * abs(math.sin(math.pi * u * 2.2)) * (1 - 0.25 * u)
        y = FLOOR_Y - hop
        q = 1.0 - 0.06 * math.cos(math.pi * u * 4.4)
        arm_l = (-0.60, -1.02 + 0.22 * math.sin(u * 9))
        arm_r = (0.60, -1.02 - 0.22 * math.sin(u * 9))
        p = cat_pose(x, y, s=150, face=1, q=q, eye="happy",
                     arm_l=arm_l, arm_r=arm_r, mouth=0.3, tongue=True,
                     tail=t * 10, blush=0.8)
        draw_cat(ctx, p)
        dust_puffs(ctx, x, FLOOR_Y, 1, t, 0.25, 0.7)
        return

    if t < 14.12:
        x = 650
        bob = 0.5 + 0.5 * math.sin(t * 12)
        q = 1.0 - 0.015 * bob
        ang = (t - 13.05) * 20.0
        crank_x = 706 + math.cos(ang) * 6
        crank_y = 432 + math.sin(ang) * 5
        lx = (crank_x - x) / 150
        ly = (crank_y - FLOOR_Y) / 150
        p = cat_pose(x, FLOOR_Y, s=150, face=1, q=q, eye="open",
                     look=(0.04, -0.04),
                     arm_l=(-0.33, -0.70), arm_r=(lx, ly),
                     mouth=0.12, tongue=True, htilt=0.05,
                     tail=2 + 0.5 * math.sin(t * 7), blush=0.6)
        draw_cat(ctx, p)
        # little ratchet sparks
        for k in range(3):
            a = t * 17 + k * 0.9
            sparkle(ctx, crank_x + math.cos(a) * 14, crank_y + math.sin(a) * 14,
                    3.5, RED, 0.65, 1.2)
        return

    if t < 14.45:
        u = smoothstep(14.12, 14.3, t)
        p = cat_pose(650, FLOOR_Y, s=150, face=1, q=1.0, eye="happy",
                     arm_l=(-0.55, -1.15), arm_r=(0.55, -1.55),
                     mouth=0.35, tongue=True, htilt=-0.05, blush=1.0)
        draw_cat(ctx, p)
        sparkle(ctx, 650, 340, 14, GOLD, 0.8, 2.5)
        return

    # step back into the spotlight
    u = smoothstep(14.45, 14.95, t)
    x = lerp(650, 512, ease_in_out(u))
    y = FLOOR_Y - 12 * abs(math.sin(u * math.pi * 2))
    p = cat_pose(x, y, s=150, face=1, q=1.0, eye="happy",
                 arm_l=(-0.58, -0.86), arm_r=(0.58, -0.86),
                 mouth=0.35, tongue=True, tail=t * 12, blush=1.0)
    draw_cat(ctx, p)


def dance_pose(t):
    b = (t - 14.95) / SPB
    sway = math.sin(TAU * b / 8)
    x = 512 + 36 * sway
    hop = abs(math.sin(math.pi * b))
    y = FLOOR_Y - 7.0 * hop
    q = 1.0 - 0.055 * math.cos(TAU * b)
    lift_l = max(0.0, math.sin(TAU * b / 2)) * 0.18
    lift_r = max(0.0, -math.sin(TAU * b / 2)) * 0.18
    leg_l = (-0.28 + 0.02 * sway, -lift_l)
    leg_r = (0.28 + 0.02 * sway, -lift_r)
    arm_l = (-0.62, -0.92 + 0.24 * math.sin(TAU * b / 2))
    arm_r = (0.62, -0.92 - 0.24 * math.sin(TAU * b / 2))
    eye = "happy" if int(b) % 2 == 0 else "open"
    mouth = 0.22 + 0.28 * max(0.0, math.sin(TAU * b / 2))
    tongue = mouth > 0.3
    htilt = 0.055 * math.sin(TAU * b / 2)
    hy = 0.012 * math.sin(TAU * b)
    look = (0.03, 0.02)
    if 17.5 < t < 19.15:
        arm_r = (0.52, -1.72)
        look = (0.03, -0.05)
        mouth = 0.4
        eye = "open"
    if 21.3 < t < 21.55:
        x = 512
        y = FLOOR_Y
        q = 1.0
        eye = "wide"
        arm_l = (-0.64, -0.86)
        arm_r = (0.64, -0.86)
        mouth = 0.2
        tongue = False
        look = (0.05, 0.0)
        htilt = 0.0
    return cat_pose(x, y, s=150, face=1, q=q, eye=eye, look=look,
                    arm_l=arm_l, arm_r=arm_r, leg_l=leg_l, leg_r=leg_r,
                    mouth=mouth, tongue=tongue, htilt=htilt, hy=hy,
                    tail=t * 9, tail_lift=0.15, blush=1.0)


def dance_act(ctx, t):
    p = dance_pose(t)
    draw_cat(ctx, p)
    # notes from the horn and from the happy cat
    note_stream(ctx, t, 14.5, 21.5, 655, 305, 0.42, 50, INK, 9, 2.8, 1.0)
    note_stream(ctx, t, 15.0, 21.5, p["x"] + 30, 380, 0.55, 55, RED_2, 8, 2.4, 0.8)


def sneak_act(ctx, t):
    # cat stands / listens / tiptoes after the mouse
    cat_x = track(t, [(21.5, 512), (22.3, 518), (23.65, 642), (24.2, 648)])
    q = 1.0
    arm_l = (-0.55, -0.8)
    arm_r = (0.55, -0.8)
    leg_l = (-0.22, 0.0)
    leg_r = (0.22, 0.0)
    eye = "open"
    look = (0.05, 0.0)
    htilt = 0.03
    mouth = 0.0
    if t < 22.35:
        q = 0.96
        arm_l = (-0.52, -0.88)
        arm_r = (0.52, -0.88)
        look = (0.06, -0.01)
    elif t < 23.55:
        # tiptoe, finger to lips, knees high
        u = t * 8.0
        q = 0.92
        arm_l = (-0.30, -1.12)
        arm_r = (0.30, -1.12)
        leg_l = (-0.28, -0.15 * max(0, math.sin(u)))
        leg_r = (0.28, -0.15 * max(0, -math.sin(u)))
        eye = "open"
        look = (0.06, -0.02)
        htilt = 0.06
        mouth = 0.10
    elif t < 23.95:
        # the gasp
        q = 1.06
        arm_l = (-0.62, -1.38)
        arm_r = (0.62, -1.38)
        eye = "wide"
        look = (0.04, -0.06)
        mouth = 0.85
        htilt = -0.08
        leg_l = (-0.25, 0.0)
        leg_r = (0.25, 0.0)
    else:
        q = 1.02
        arm_l = (-0.62, -1.25)
        arm_r = (0.62, -1.25)
        eye = "wide"
        mouth = 0.6
        look = (0.02, -0.08)
    p = cat_pose(cat_x, FLOOR_Y, s=150, face=1, q=q, eye=eye, look=look,
                 arm_l=arm_l, arm_r=arm_r, leg_l=leg_l, leg_r=leg_r,
                 mouth=mouth, htilt=htilt, tail=t * 8, blush=0.7)
    draw_cat(ctx, p)
    if 21.5 < t < 24.2:
        if 23.9 < t < 24.2:
            exclaim(ctx, cat_x + 28, 335, 1.0, 1.0)

    # Mouse: peek, whistle, sneak, climb, grab
    if t < 22.30:
        u = smoothstep(21.5, 21.75, t)
        mx = 905
        my = 620 + (1 - u) * 30
        mq = 0.85 + 0.15 * u
        eye = "open"
        look = (-0.05, 0.0)
        mouth = 0.0
        giggle = False
        arm_l = (-0.24, -0.62)
        arm_r = (0.24, -0.62)
        scale = 55
        draw_mouse(ctx, mouse_pose(mx, my, s=scale, face=-1, q=mq, eye=eye,
                                   look=look, mouth=mouth, arm_l=arm_l,
                                   arm_r=arm_r, tail=t * 7))
        if t > 21.9:
            for k in range(2):
                ctx.arc(920, 555, 18 + k * 8, 2.6, 4.2)
                ctx.set_line_width(1.5)
                ctx.set_source_rgba(*INK, 0.35)
                ctx.stroke()
                ctx.new_path()
    elif t < 23.35:
        # whistle, then scurry to the table
        if t < 22.7:
            mx, my = 895, 620
            eye, mouth = "happy", 0.55
            arm_l, arm_r = (-0.28, -0.8), (0.28, -0.8)
        else:
            u = smoothstep(22.7, 23.35, t)
            mx = lerp(895, 755, u)
            my = 620 - abs(math.sin(u * math.pi * 4)) * 8
            eye, mouth = "open", 0.1
            arm_l, arm_r = (-0.3, -0.7), (0.3, -0.7)
        draw_mouse(ctx, mouse_pose(mx, my, s=55, face=-1, eye=eye,
                                   look=(-0.05, 0.0), mouth=mouth,
                                   arm_l=arm_l, arm_r=arm_r, tail=t * 14))
        if t < 22.7:
            note(ctx, 880, 520, 8, RED_2, 0.8, rot=-0.2)
    elif t < 24.2:
        # leap onto the gramophone table and snatch the record
        if t < 23.72:
            u = smoothstep(23.35, 23.72, t)
            mx = lerp(755, 772, u)
            my = 620 + (452 - 620) * u - 55 * math.sin(math.pi * u)
            mq = 1.0
            rec = False
            arm_l, arm_r = (-0.3, -0.75), (0.3, -0.75)
            eye = "open"
            mouth = 0.1
        else:
            mx, my = 772, 452
            mq = 1.0 - 0.04 * abs(math.sin((t - 23.72) * 22))
            rec = True
            arm_l, arm_r = (-0.26, -1.15), (0.26, -1.15)
            eye = "happy"
            mouth = 0.35
        draw_mouse(ctx, mouse_pose(mx, my, s=55, face=-1, q=mq, eye=eye,
                                   look=(-0.03, -0.02), mouth=mouth,
                                   arm_l=arm_l, arm_r=arm_r, record=rec,
                                   tail=t * 12))
        if t > 23.86:
            sparkle_burst(ctx, mx, my - 100, t, 23.86, 0.8)
        if t > 23.92 and t < 24.2:
            for k in range(2):
                ctx.arc(mx, my - 130, 60 + k * 14, -2.4, -0.4)
                ctx.set_line_width(1.8)
                ctx.set_source_rgba(*INK, 0.3)
                ctx.stroke()
                ctx.new_path()


# -------------------------------------------------------------------------
# chase
# -------------------------------------------------------------------------
CAT_X = [(24.20, 648), (24.55, 610), (25.55, 270), (26.05, 335),
         (27.10, 700), (27.55, 640), (28.60, 300), (29.05, 360),
         (30.20, 705), (30.75, 665), (31.62, 690), (32.20, 620),
         (32.90, 788), (33.35, 812)]
MOUSE_X = [(24.20, 772), (24.55, 742), (25.55, 160), (26.05, 230),
           (27.10, 780), (27.55, 720), (28.60, 200), (29.05, 260),
           (30.20, 800), (30.75, 728), (31.62, 600), (32.20, 520),
           (32.90, 880), (33.28, 915)]


def run_face(t):
    if t < 25.85:
        return -1
    if t < 27.35:
        return 1
    if t < 28.85:
        return -1
    return 1


def draw_runner_cat(ctx, t, x, y, face):
    ph = t * 24.0
    p = cat_pose(x, y, s=150, face=face, q=1.01, eye="wide",
                 look=(0.05 * face, 0.01),
                 arm_l=(-0.55, -0.82 + 0.28 * math.sin(ph)),
                 arm_r=(0.55, -0.82 - 0.28 * math.sin(ph)),
                 leg_l=(-0.30 + 0.10 * math.sin(ph), -0.20 * max(0.0, math.sin(ph))),
                 leg_r=(0.30 + 0.10 * math.sin(ph + math.pi), -0.20 * max(0.0, -math.sin(ph))),
                 mouth=0.32, tongue=True, htilt=0.10 * face,
                 tail=ph * 0.7, tail_lift=-0.4, blush=0.8)
    draw_cat(ctx, p)
    speed_lines(ctx, x, y - 30, face, t, 0.36, 1.0)
    dust_puffs(ctx, x, y, face, t, 0.42, 1.0)


def draw_runner_mouse(ctx, t, x, y, face):
    ph = t * 34.0
    q = 0.98 + 0.03 * abs(math.sin(ph))
    draw_mouse(ctx, mouse_pose(x, y, s=55, face=face, q=q, eye="wide",
                               look=(0.06 * face, 0.0),
                               arm_l=(-0.28, -1.15), arm_r=(0.28, -1.15),
                               leg_l=(-0.15, -0.10 * max(0.0, math.sin(ph))),
                               leg_r=(0.15, -0.10 * max(0.0, -math.sin(ph))),
                               record=True, tail=ph * 0.7, mouth=0.15))
    speed_lines(ctx, x, y - 20, face, t, 0.32, 0.6)


def draw_fight_cloud(ctx, t):
    cx, cy = 676, 520 + math.sin(t * 35) * 4
    # record spinning above the scuffle
    draw_record(ctx, cx, 395 + math.sin(t * 12) * 6, 32, rot=t * 18)
    for k in range(3):
        ctx.arc(cx, 395, 46 + k * 9, t * 7 + k, t * 7 + k + 2.2)
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(*RED, 0.4)
        ctx.stroke()
        ctx.new_path()
    # flailing limbs
    stroke(ctx, [(cx - 50, cy + 35), (cx - 90, cy + 75), (cx - 105, cy + 105)],
           INK, 12, 1.0)
    ellipse(ctx, cx - 106, cy + 112, 14, 8, fill=CREAM, stroke=INK, lw=2.0)
    stroke(ctx, [(cx + 40, cy + 40), (cx + 85, cy + 85)], INK, 10, 1.0)
    # ears poking out
    poly(ctx, [(cx - 28, cy - 55), (cx - 15, cy - 100), (cx + 4, cy - 58)],
         fill=INK)
    poly(ctx, [(cx + 25, cy - 62), (cx + 42, cy - 98), (cx + 55, cy - 54)],
         fill=(0.78, 0.72, 0.60), stroke=INK, lw=2.0)
    # cloud puff
    for i in range(10):
        a = i * TAU / 10
        r = 62 + 16 * math.sin(i * 2.3)
        circle(ctx, cx + math.cos(a) * 60, cy + math.sin(a) * 33,
               r * 0.55, fill=DUST, alpha=0.95)
    for i in range(6):
        a = i * TAU / 6 + 0.4
        circle(ctx, cx + math.cos(a) * 40, cy + math.sin(a) * 20,
               24, fill=CREAM, alpha=0.9)
    text(ctx, "BIFF!", cx + 115, cy - 120, 30, color=RED, alpha=0.85)
    for k in range(3):
        star(ctx, cx - 110 + k * 20, cy - 150 + k * 12, 9 - k * 2, 4,
             fill=CREAM, stroke_c=INK, lw=1.2)


def chase_act(ctx, t):
    mouse_x = track(t, MOUSE_X, ease_in_out)
    cat_x = track(t, CAT_X, ease_in_out)
    face = run_face(t)
    mouse_y = 620
    if t < 24.5:
        mouse_y = lerp(452, 620, smoothstep(24.2, 24.5, t))
    if 30.75 <= t < 31.62:
        draw_fight_cloud(ctx, t)
        return
    if t < 33.2:
        # draw whoever is behind first
        if mouse_x > cat_x:
            draw_runner_cat(ctx, t, cat_x, 620, face)
            draw_runner_mouse(ctx, t, mouse_x, mouse_y, face)
        else:
            draw_runner_mouse(ctx, t, mouse_x, mouse_y, face)
            draw_runner_cat(ctx, t, cat_x, 620, face)
    else:
        # mouse dives into the hole
        u = clamp((t - 33.2) / 0.12)
        draw_mouse(ctx, mouse_pose(915, 620, s=55 * (1 - 0.4 * u), face=1,
                                   eye="happy", record=True, tail=t * 14))
        circle(ctx, 915, 600, 18 + 10 * u, fill=DUST, alpha=0.5)

    if 32.9 < t < 33.35:
        # skid marks / panic lines in front of the cat
        for k in range(4):
            y = 640 - k * 12
            stroke(ctx, [(cat_x + 30 + k * 10, y), (cat_x + 100 + k * 12, y)],
                   INK, 2.0, 0.25)




def crash_pose(ctx, t):
    if t >= 36.55:
        return
    u = clamp((t - 33.30) / 0.28)
    if t < 33.9:
        q = lerp(1.0, 0.55, smoothstep(33.30, 33.45, t))
        p = cat_pose(812, 612, s=150, face=1, q=q, eye="x",
                     arm_l=(-0.75, -1.25), arm_r=(0.78, -1.18),
                     leg_l=(-0.42, -0.05), leg_r=(0.48, -0.02),
                     mouth=0.5, tongue=True, htilt=-0.12, blush=1.0)
        draw_cat(ctx, p)
        return
    # dazed, sitting on the floor
    wob = math.sin((t - 33.9) * 8.0) * (1 - smoothstep(35.6, 36.2, t))
    p = cat_pose(800, 620, s=150, face=1, q=0.84, eye="x",
                 arm_l=(-0.52, -0.55 + 0.03 * wob), arm_r=(0.52, -0.55 - 0.03 * wob),
                 leg_l=(-0.34, -0.02), leg_r=(0.36, -0.02),
                 mouth=0.22, tongue=True, htilt=0.14 * wob, hy=0.02,
                 tail=1.0 + 0.4 * math.sin(t * 6), blush=0.8)
    if t > 35.25:
        p["eye"] = "open"
        p["look"] = (-0.05, 0.0)
        p["mouth"] = 0.08
        p["tongue"] = False
        p["htilt"] = 0.08
        p["q"] = 0.88
    if t > 35.85:
        p["eye"] = "happy"
        p["mouth"] = 0.35
        p["tongue"] = True
        p["htilt"] = -0.04
        p["arm_l"] = (-0.52, -0.72)
        p["arm_r"] = (0.40, -0.95)
        p["blush"] = 1.0
    draw_cat(ctx, p)
    if t < 35.2:
        draw_daze_stars(ctx, 800, 445, t, 0.9)
    if 36.55 < t < 37.1:
        # reach behind the back, produce a banjo
        pass


def aftermath(ctx, t):
    # ---- mouse: giggle at the hole, trumpet the "wah", then scurry to the drum
    if t < 34.6:
        draw_mouse(ctx, mouse_pose(920, 620, s=55, face=-1, q=0.88,
                                   eye="happy", look=(-0.03, 0.0),
                                   arm_l=(-0.26, -0.7), arm_r=(0.26, -0.7),
                                   mouth=0.15, giggle=True, tail=t * 7))
        if t > 34.1:
            for k in range(2):
                ctx.arc(896, 560, 16 + k * 9, 2.4, 4.4)
                ctx.set_line_width(1.4)
                ctx.set_source_rgba(*INK, 0.35)
                ctx.stroke()
                ctx.new_path()
    elif t < 35.35:
        mx = lerp(895, 850, smoothstep(34.6, 35.0, t))
        draw_mouse(ctx, mouse_pose(mx, 620, s=55, face=-1, eye="happy",
                                   look=(-0.04, -0.02), mouth=0.15,
                                   arm_l=(-0.25, -0.92), arm_r=(0.30, -0.95),
                                   giggle=True, tail=t * 8))
    elif t < 37.1:
        draw_mouse(ctx, mouse_pose(848, 620, s=55, face=-1, eye="happy",
                                   look=(-0.04, -0.03), mouth=0.3,
                                   arm_l=(-0.18, -0.8), arm_r=(0.24, -0.8),
                                   trumpet=True, tail=t * 10))
        note_stream(ctx, t, 35.45, 37.1, 805, 500, 0.38, 45, RED_2, 8, 2.2, 0.8)
    else:
        # scoot over to the thimble drum for the closing number
        u = smoothstep(37.1, 37.5, t)
        mx = lerp(848, 636, u)
        my = 620 - 30 * abs(math.sin(u * math.pi * 2))
        draw_mouse(ctx, mouse_pose(mx, my, s=55, face=-1, eye="happy",
                                   look=(-0.04, -0.02), mouth=0.2,
                                   arm_l=(-0.24, -0.85), arm_r=(0.28, -0.88),
                                   tail=t * 12))
        dust_puffs(ctx, mx, 620, 1, t, 0.3, 0.5)

    # ---- cat: produce the banjo, then zip over to the spotlight
    if 36.55 <= t < 37.1:
        cat_x = 800
        u = smoothstep(36.55, 37.0, t)
        if t < 36.95:
            # reach behind the back (hand tucked by the hip)
            arm_l, arm_r = (-0.42, -0.62), (0.30, -0.55)
        else:
            # ta-da! the banjo snaps into playing position
            arm_l, arm_r = (-0.35, -0.88), (0.36, -0.52)
        p = cat_pose(cat_x, 620, s=150, face=1, q=0.9 + 0.1 * u,
                     eye="happy", look=(-0.05, 0.0), mouth=0.3, tongue=True,
                     arm_l=arm_l, arm_r=arm_r,
                     leg_l=(-0.30, -0.02), leg_r=(0.34, -0.02),
                     htilt=-0.06, blush=1.0, tail=t * 9)
        draw_cat(ctx, p, skip_gloves=True)
        if t >= 36.95:
            draw_banjo(ctx, cat_x, 620, 150, t, 0.0, face=1)
            sparkle_burst(ctx, cat_x + 30, 430, t, 36.98, 0.9)
        draw_glove(ctx, *cat_hand_pos(p, "arm_l"), 150, 1, 0.0)
        draw_glove(ctx, *cat_hand_pos(p, "arm_r"), 150, 1, 0.0)
    elif 37.1 <= t < 37.5:
        u = smoothstep(37.1, 37.5, t)
        x = lerp(800, 500, u)
        y = 615 - 55 * math.sin(math.pi * u)
        p = cat_pose(x, y, s=150, face=1, q=1.0, eye="happy",
                     arm_l=(-0.35, -0.88), arm_r=(0.36, -0.52),
                     leg_l=(-0.30, -0.02), leg_r=(0.34, -0.02),
                     mouth=0.3, tongue=True, tail=t * 12, blush=1.0)
        draw_cat(ctx, p, skip_gloves=True)
        draw_banjo(ctx, x, y, 150, t, 0.0, face=1)
        draw_glove(ctx, *cat_hand_pos(p, "arm_l"), 150, 1, 0.0)
        draw_glove(ctx, *cat_hand_pos(p, "arm_r"), 150, 1, 0.0)
        speed_lines(ctx, x, y - 40, 1, t, 0.3, 1.0)


def jam_act(ctx, t):
    b = (t - JAM) / SPB
    hop = abs(math.sin(math.pi * b)) * 5
    cat_x = 500 + 9 * math.sin(TAU * b / 8)
    strum = math.sin(TAU * b * 2)
    p = cat_pose(cat_x, FLOOR_Y - hop, s=150, face=1, q=1.0 - 0.03 * math.cos(TAU * b),
                 eye="happy" if int(b) % 2 == 0 else "wink",
                 look=(0.04, -0.02),
                 arm_l=(-0.35, -0.88), arm_r=(0.36, -0.52 + 0.02 * strum),
                 leg_l=(-0.28, -0.03), leg_r=(0.28, -0.03),
                 mouth=0.28 + 0.18 * max(0.0, math.sin(TAU * b / 2)),
                 tongue=True, htilt=0.04 * math.sin(TAU * b / 2),
                 hy=0.01 * math.sin(TAU * b), tail=b * 1.2,
                 blush=1.0)
    spin = 0.0
    if 41.3 < t < 41.95:
        u = clamp((t - 41.3) / 0.65)
        spin = u * TAU
        p["y"] = FLOOR_Y - 45 * math.sin(math.pi * u)
        p["q"] = 1.0
    if spin:
        ctx.save()
        ctx.translate(cat_x, FLOOR_Y - 100)
        ctx.rotate(spin)
        ctx.translate(-cat_x, -(FLOOR_Y - 100))
    draw_cat(ctx, p, skip_gloves=True)
    (bbx, bby), (bhx, bhy) = draw_banjo(ctx, cat_x, p["y"], 150, t, strum, face=1)
    draw_glove(ctx, *cat_hand_pos(p, "arm_l"), 150, 1, 0.0)
    draw_glove(ctx, *cat_hand_pos(p, "arm_r"), 150, 1, 0.0)
    if spin:
        ctx.restore()
        for k in range(3):
            ctx.arc(cat_x, FLOOR_Y - 60, 80 + k * 20, 0.3, 2.7)
            ctx.set_line_width(2.0)
            ctx.set_source_rgba(*INK, 0.25)
            ctx.stroke()
            ctx.new_path()

    # Squeak on his thimble drum
    mhop = abs(math.sin(math.pi * b + 0.5)) * 4
    mq = 1.0 - 0.05 * math.cos(TAU * b)
    mx = 636 + 5 * math.sin(TAU * b / 8)
    draw_thimble_stool(ctx, 640, 620, 0.9)
    draw_mouse(ctx, mouse_pose(mx, 612 - mhop, s=55, face=-1, q=mq,
                               eye="happy" if int(b) % 2 else "open",
                               look=(-0.03, -0.02),
                               arm_l=(-0.2, -0.8), arm_r=(0.24, -0.8),
                               mouth=0.32, trumpet=True, tail=b * 1.6))
    # notes pour out of both instruments
    period = lerp(0.44, 0.26, smoothstep(JAM, 48.5, t))
    note_stream(ctx, t, 37.9, 48.75, bhx, bhy + 8, period, 60, INK, 9, 2.6, 1.0)
    note_stream(ctx, t, 38.3, 48.75, 584, 560, period * 1.1, 55, RED_2, 8, 2.4, 0.9)
    if 45.5 < t < 48.75:
        for k in range(3):
            ang = t * 2.2 + k * TAU / 3
            note(ctx, 570 + math.cos(ang) * 150, 390 + math.sin(ang) * 70,
                 9, GOLD, 0.55, rot=ang)


def finale_act(ctx, t):
    # cat gets his boater, then the mouse rides the shoulder
    cat_x = 500 + 10 * math.sin((t - FINALE) * 2.0)
    b = (t - FINALE) / SPB
    hop = abs(math.sin(math.pi * b)) * 7
    q = 1.0 - 0.04 * math.cos(TAU * b)
    hat = None
    if t > 49.75:
        hat = "boater"
    arm_l = (-0.62, -1.05 + 0.18 * math.sin(TAU * b / 2))
    arm_r = (0.62, -1.05 - 0.18 * math.sin(TAU * b / 2))
    eye = "happy"
    htilt = 0.05 * math.sin(TAU * b / 2)
    hy = 0.012 * math.sin(TAU * b)
    mouth = 0.25
    tongue = True
    y = FLOOR_Y - hop

    if 49.1 < t < 49.75:
        # hat held up in the right hand
        arm_r = (0.55, -1.62)
        eye = "open"
        mouth = 0.15
    if 52.95 < t < 53.45:
        # big bow
        q = 0.93
        htilt = 0.32
        hy = 0.055
        arm_l = (-0.52, -0.92)
        arm_r = (0.52, -0.92)
        eye = "happy"
        hat = "boater"
    if t > 53.5:
        # straighten up, tip the hat to the audience
        q = 1.0
        htilt = -0.06
        hy = -0.01
        arm_l = (-0.52, -0.85)
        arm_r = (0.66, -1.52)
        eye = "wink"
        mouth = 0.2
        hat = None

    p = cat_pose(cat_x, y, s=150, face=1, q=q, eye=eye,
                 look=(0.03, -0.02), arm_l=arm_l, arm_r=arm_r,
                 mouth=mouth, tongue=tongue, htilt=htilt, hy=hy,
                 tail=t * 8, blush=1.0, hat=hat)
    draw_cat(ctx, p)

    # held/tip hat in the right hand
    if 49.1 < t < 49.75 or t > 53.5:
        hx, hyy = cat_hand_pos(p, "arm_r")
        draw_boater(ctx, hx, hyy - 10, 150 * 0.78,
                    rot=(-0.5 if t < 49.75 else -0.9), alpha=1.0)

    # mouse leaps to the shoulder
    if t >= 50.35:
        if t < 50.95:
            u = smoothstep(50.35, 50.95, t)
            mx = lerp(636, cat_x - 52, u)
            my = lerp(608, 458, u) - 95 * math.sin(math.pi * u)
        else:
            mx = cat_x - 52
            my = 458 + hop * 0.5
        mouse_face = 1
        mq = 0.97
        marm_l = (-0.28, -1.02)
        marm_r = (0.28, -1.02)
        if t > 53.0 and t < 53.5:
            mq = 0.90
            marm_l = (-0.3, -0.72)
            marm_r = (0.3, -0.72)
        if t > 53.6:
            marm_r = (0.38, -1.35)
            marm_l = (-0.25, -0.85)
        draw_mouse(ctx, mouse_pose(mx, my, s=50, face=mouse_face, q=mq,
                                   eye="happy", look=(0.02, -0.02),
                                   mouth=0.3, arm_l=marm_l, arm_r=marm_r,
                                   tail=t * 9, vest=True))
    else:
        mx = 636
        my = 608 - abs(math.sin(math.pi * b + 0.5)) * 5
        draw_mouse(ctx, mouse_pose(mx, my, s=55, face=-1, q=1.0,
                                   eye="happy", mouth=0.3,
                                   arm_l=(-0.25, -0.92), arm_r=(0.32, -0.95),
                                   tail=t * 8))

    # big finish flash of sparkles
    if t > 52.45:
        sparkle_burst(ctx, cat_x, 360, t, 52.45, 1.0)
        sparkle_burst(ctx, cat_x + 60, 300, t, 52.45, 1.0)
    if t > 53.55:
        sparkle(ctx, cat_x + 85, 390, 14, RED, 0.8, 2.2)


# -------------------------------------------------------------------------
# frame assembly
# -------------------------------------------------------------------------
def draw_living(ctx, t):
    draw_environment(ctx, t)

    if t < 8.15:
        sleep_and_startle(ctx, t)
    elif t < 11.25:
        morning(ctx, t)
    elif t < 14.95:
        gramophone_act(ctx, t)
    elif t < 21.5:
        dance_act(ctx, t)
    elif t < 24.2:
        sneak_act(ctx, t)
    elif t < 33.35:
        chase_act(ctx, t)
    elif t < 37.5:
        crash_pose(ctx, t)
        aftermath(ctx, t)
    elif t < 48.75:
        jam_act(ctx, t)
    else:
        finale_act(ctx, t)

    # overlays that sit above everybody
    if 33.30 < t < 33.95:
        draw_pow(ctx, 800, 360, 0.78, 1.0, t)
        for k in range(3):
            star(ctx, 730 + k * 60, 250 + (k % 2) * 40, 12, 5,
                 fill=CREAM, stroke_c=INK, lw=1.4, alpha=0.9)
    draw_banner(ctx, t)
    if 48.75 < t < 58.5:
        draw_confetti(ctx, t)
    if 52.45 < t < 52.8:
        draw_flash(ctx, t)
    if t > 48.95 and t < 49.9:
        sparkle_burst(ctx, 470, 380, t, 48.95, 0.8)

    # iris out at the very end
    if t >= IRIS_OUT:
        u = clamp((t - IRIS_OUT) / (56.10 - IRIS_OUT))
        r = lerp(760, 0, ease_in_out(u))
        iris(ctx, 500, 402, r)


def draw_frame(ctx, t):
    if t < ROOM_IN:
        draw_title_card(ctx, t)
        if t >= TITLE_IRIS:
            u = smoothstep(TITLE_IRIS, ROOM_IN, t)
            iris(ctx, 480, 360, lerp(780, 0, ease_in_cubic(u)))
    elif t < END_CARD:
        draw_living(ctx, t)
        if t < ROOM_IN + 0.34:
            u = smoothstep(ROOM_IN, ROOM_IN + 0.34, t)
            iris(ctx, 480, 380, lerp(0, 820, ease_out_cubic(u)))
    else:
        draw_end_card(ctx, t)
        if t < END_CARD + 0.28:
            u = smoothstep(END_CARD, END_CARD + 0.28, t)
            iris(ctx, 480, 360, lerp(0, 900, ease_out_cubic(u)))
        if t > FADE_OUT:
            a = smoothstep(FADE_OUT, 59.92, t)
            rect(ctx, 0, 0, 960, 720, fill=(0.02, 0.015, 0.012), alpha=a * 0.96)
