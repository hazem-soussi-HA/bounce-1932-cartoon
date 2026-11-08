"""Shared musical/picture timeline for BOUNCE! (1932).

128 BPM in 4/4 means exactly 32 bars = 60.0 seconds.
Every gag is locked to this grid wherever possible.
"""

BPM = 128
SPB = 60.0 / BPM          # seconds per beat (0.46875)
BAR = 4 * SPB             # seconds per bar  (1.875)
FPS = 24
DURATION = 60.0


def T(bar, beat=0.0):
    """Absolute seconds at a given bar/beat."""
    return (bar * 4 + beat) * SPB


# ---- major picture beats -------------------------------------------------
TITLE_START = 0.0
TITLE_IRIS = T(2)               # 3.750
ROOM_IN = T(2) + 0.30           # 4.050
ALARM = T(3, 3.2)               # 7.125
STARTLE = T(3, 3.75)            # 7.383
GROOVE = T(6)                   # 11.250
RECORD_ON = T(7, 2.0)           # 13.125
BANNER_IN = T(9, 1.33)          # 17.500
BANNER_OUT = T(11, 1.33)        # 21.500
MOUSE_PEEK = 21.50
MOUSE_WHISTLE = 22.28
MOUSE_GRAB = 23.90
CHASE = T(14)                   # 26.250
DUST_CLOUD = T(16, 2.0)         # 30.750
CRASH = T(17, 3.15)             # 33.352
WAH = T(18)                     # 33.750
TRUMPET = T(19, 1.0)            # 36.094
JAM = T(20)                     # 37.500
FINALE = T(26)                  # 48.750
BIG_CHORD = T(28)               # 52.500
HAT_TIP = T(29)                 # 54.375
IRIS_OUT = 54.25
END_CARD = T(30)                # 56.250
TAG = T(29)                     # 54.375  (shave-and-a-haircut starts)
TWO_BITS = T(30)                # 56.250
FADE_OUT = 59.15
THE_END = 60.0
