"""Render test sheets for visual review."""
import cairo
from gfx import *
from characters import *
from props import *
from cards import *
import time


def new_ctx():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.scale(SCALE, SCALE)
    return surf, ctx


def cat_sheet(path):
    surf, ctx = new_ctx()
    rect(ctx, 0, 0, DW, DH, fill=PAPER)
    for i in range(4):
        x = 150 + i * 220
        ctx.save()
        ctx.rectangle(x - 100, 90, 200, 520)
        ctx.clip()
        if i == 0:
            p = cat_pose(x, 590, s=125, q=1.0)
        elif i == 1:
            p = cat_pose(x, 590, s=125, q=1.0, eye="happy", mouth=0.35,
                         tongue=True, arm_r=(0.55, -1.58), arm_l=(-0.48, -0.9),
                         blush=1.0)
        elif i == 2:
            p = cat_pose(x, 590, s=125, q=0.92, arm_l=(-0.66, -1.1),
                         arm_r=(0.7, -0.95), leg_l=(-0.35, -0.22),
                         leg_r=(0.28, 0.0), tail=1.3, eye="wide", mouth=0.5,
                         tongue=True)
        else:
            p = cat_pose(x, 590, s=125, q=1.0, eye="wink", hat="boater",
                         arm_r=(0.62, -1.55), arm_l=(-0.35, -0.7), blush=1.0,
                         mouth=0.0)
        draw_cat(ctx, p)
        ctx.restore()
        text(ctx, ["NEUTRAL", "HAPPY", "DANCE", "WINK"][i], x, 655, 14, color=INK,
             tracking=2)
    surf.write_to_png(path)


def mouse_sheet(path):
    surf, ctx = new_ctx()
    rect(ctx, 0, 0, DW, DH, fill=PAPER)
    poses = [
        mouse_pose(160, 590, s=85, eye="open", look=(0.03, 0)),
        mouse_pose(360, 590, s=85, eye="happy", mouth=0.3, arm_l=(-0.3, -0.9),
                   arm_r=(0.3, -0.9)),
        mouse_pose(560, 590, s=85, eye="open", record=True, arm_l=(-0.28, -1.0),
                   arm_r=(0.28, -1.0), tail=1.2),
        mouse_pose(760, 590, s=85, eye="happy", trumpet=True, mouth=0.2,
                   arm_l=(-0.2, -0.8), arm_r=(0.28, -0.8)),
    ]
    for i, p in enumerate(poses):
        draw_mouse(ctx, p)
        text(ctx, ["SQUEAK", "GIGGLE", "RECORD", "TRUMPET"][i], p["x"], 655,
             14, color=INK, tracking=2)
    surf.write_to_png(path)


def room_test(path):
    surf, ctx = new_ctx()
    draw_room_shell(ctx)
    draw_plant(ctx, 2.0)
    draw_pendant_lamp(ctx, 2.0)
    draw_portrait(ctx, 2.0, 0.0)
    draw_chair(ctx)
    draw_side_table(ctx, 398, 565)
    draw_mouse_hole(ctx)
    draw_gramophone(ctx, cx=770, t=2.0, playing=True, record_on=True, crank=0.8, spin=1.2)
    draw_sleeping_cat(ctx, 232, 505, s=145, breath=1.2)
    draw_zzz(ctx, 360, 380, 2.0, 1.0)
    draw_clock(ctx, 398, 548, t=2.0, ringing=0)
    surf.write_to_png(path)


def cards_test():
    surf, ctx = new_ctx()
    draw_title_card(ctx, 2.6)
    surf.write_to_png("preview_title.png")

    surf, ctx = new_ctx()
    draw_end_card(ctx, 57.4)
    surf.write_to_png("preview_end.png")

    surf, ctx = new_ctx()
    draw_room_shell(ctx)
    draw_plant(ctx, 2.0)
    draw_pendant_lamp(ctx, 2.0)
    draw_portrait(ctx, 2.0, 0.0)
    draw_chair(ctx)
    draw_side_table(ctx, 398, 565)
    draw_mouse_hole(ctx)
    draw_gramophone(ctx, cx=770, t=19.0, playing=True, record_on=True, crank=0.0, spin=4.0)
    p = cat_pose(470, 615, s=150, eye="happy", mouth=0.4, tongue=True,
                 arm_l=(-0.65, -1.15), arm_r=(0.55, -1.3), leg_l=(-0.3, -0.15),
                 tail=2.0, blush=1.0)
    draw_cat(ctx, p)
    draw_banner(ctx, 19.0)
    surf.write_to_png("preview_banner.png")


if __name__ == "__main__":
    t0 = time.time()
    cat_sheet("preview_cat.png")
    mouse_sheet("preview_mouse.png")
    room_test("preview_room.png")
    cards_test()
    print("done in %.2fs" % (time.time() - t0))
