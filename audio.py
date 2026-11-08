"""Soundtrack for BOUNCE! (1932).

A synthesized 1932-style ragtime band (piano, tuba, banjo, clarinet,
trumpet, drums) plus hand-made cartoon SFX.  128 BPM, 60.0 seconds.
Everything is generated from scratch with numpy/scipy.
"""
import math
import time

import numpy as np
from scipy import signal
from scipy.io import wavfile

from timeline import *

SR = 44100
NS = int(SR * DURATION)
TAU = math.tau
rng = np.random.default_rng(1932)
mix = np.zeros((NS, 2), dtype=np.float64)


# -------------------------------------------------------------------------
# utilities
# -------------------------------------------------------------------------
def mtof(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= NS:
        return
    j = min(NS, i + len(sig))
    if j <= i:
        return
    seg = sig[:j - i] * gain
    l = math.sqrt(0.5 * (1.0 - pan))
    r = math.sqrt(0.5 * (1.0 + pan))
    mix[i:j, 0] += seg * l * 1.41421356
    mix[i:j, 1] += seg * r * 1.41421356


def _t(n):
    return np.arange(n) / SR


def _lpf(x, cutoff, order=2):
    sos = signal.butter(order, cutoff, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _hpf(x, cutoff, order=2):
    sos = signal.butter(order, cutoff, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


# -------------------------------------------------------------------------
# band instruments
# -------------------------------------------------------------------------
def piano(f, dur=0.8, vel=0.8):
    n = int(dur * SR)
    if n < 8:
        return np.zeros(0)
    t = _t(n)
    out = np.zeros(n)
    for k in range(1, 9):
        amp = 1.0 / (k ** 1.55) * math.exp(-0.28 * (k - 1))
        fk = f * k * (1 + 0.00035 * k * k)
        out += amp * np.sin(TAU * fk * t + 0.7 * k)
    # honky-tonk detuned string
    for k in (1, 2, 3):
        out += 0.22 / k * np.sin(TAU * f * k * 1.0035 * t + 0.3)
    # hammer thump
    out += 0.10 * rng.standard_normal(n) * np.exp(-t * 260)
    env = (1 - np.exp(-t * 700)) * np.exp(-t * (1.8 + 1.4 * math.sqrt(f / 261.6)))
    out *= env * np.clip((dur - t) / 0.05, 0, 1)
    return out * vel * 0.42


def tuba(f, dur=0.32, vel=0.9):
    n = int(dur * SR)
    t = _t(n)
    out = (np.sin(TAU * f * t)
           + 0.45 * np.sin(TAU * 2 * f * t + 0.4)
           + 0.22 * np.sin(TAU * 3 * f * t + 0.9)
           + 0.10 * np.sin(TAU * 4 * f * t))
    out += 0.06 * rng.standard_normal(n) * np.exp(-t * 90)
    env = (1 - np.exp(-t * 150)) * np.exp(-t * 3.2)
    env *= np.clip((dur - t) / 0.04, 0, 1)
    return out * vel * 0.46


def clarinet(f, dur=0.5, vel=0.8, vibrato=5.0):
    n = int(dur * SR)
    t = _t(n)
    ramp = np.clip((t - 0.10) / 0.18, 0, 1)
    ph = TAU * f * t + (0.0045 * f / vibrato) * (1 - np.cos(TAU * vibrato * t)) * ramp
    out = np.zeros(n)
    for k in (1, 3, 5, 7, 9):
        out += np.sin(k * ph + 0.3 * k) / (k ** 1.15)
    breath = rng.standard_normal(n)
    breath = _lpf(breath, 1900)
    breath = _hpf(breath, 250)
    out += breath * 0.030
    env = np.clip(t / 0.030, 0, 1) * (0.78 + 0.22 * np.exp(-t * 3))
    env *= np.clip((dur - t) / 0.07, 0, 1)
    return out * vel * 0.33


def trumpet(f, dur=0.4, vel=0.85, mute=0.0, growl=0.0):
    n = int(dur * SR)
    t = _t(n)
    ramp = np.clip((t - 0.08) / 0.15, 0, 1)
    ph = TAU * f * t + (0.005 * f / 5.6) * (1 - np.cos(TAU * 5.6 * t)) * ramp
    if growl:
        ph += growl * 0.35 * np.sin(TAU * 31.0 * t) * ramp
    out = np.zeros(n)
    for k in range(1, 10):
        out += np.sin(k * ph + 0.2 * k) / (k ** 0.82)
    out += 0.04 * rng.standard_normal(n)
    if mute > 0.0:
        out = _lpf(out, 900 + 2200 * (1 - mute))
    env = np.clip(t / 0.028, 0, 1) * (0.70 + 0.30 * np.exp(-t * 4))
    env *= np.clip((dur - t) / 0.06, 0, 1)
    return out * vel * 0.30


def trombone_wah(f, dur=0.45, vel=0.8, start_ratio=1.10, wah=2.4):
    n = int(dur * SR)
    t = _t(n)
    ff = f * (start_ratio - (start_ratio - 1.0) * np.clip(t / max(dur, 1e-3), 0, 1))
    ph = TAU * np.cumsum(ff) / SR
    out = np.zeros(n)
    for k in range(1, 9):
        out += np.sin(k * ph + 0.4 * k) / (k ** 1.05)
    # plunger mute: one-pole lowpass with a moving cutoff
    cutoff = 380 + 1700 * (0.5 + 0.5 * np.sin(TAU * wah * t - 1.2))
    a = 1.0 - np.exp(-TAU * cutoff / SR)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += a[i] * (out[i] - acc)
        y[i] = acc
    env = np.clip(t / 0.04, 0, 1) * np.clip((dur - t) / 0.08, 0, 1)
    return y * env * vel * 0.55


def banjo(f, dur=0.35, vel=0.8):
    n = int(dur * SR)
    if n < 16:
        return np.zeros(0)
    period = max(2, int(round(SR / f)))
    buf = rng.uniform(-1.0, 1.0, period)
    # pick position: soften every other sample a touch
    out = np.empty(n)
    damp = 0.996
    for i in range(n):
        j = i % period
        cur = buf[j]
        out[i] = cur
        buf[j] = 0.5 * (cur + buf[(i + 1) % period]) * damp
    out = _hpf(out, 120)
    # pick click and body
    click = rng.standard_normal(n) * np.exp(-_t(n) * 180) * 0.12
    out = out + click
    body = np.sin(TAU * 520 * _t(n)) * np.exp(-_t(n) * 26) * 0.06
    out = out + body
    out *= np.clip((dur - _t(n)) / 0.025, 0, 1)
    peak = np.max(np.abs(out))
    if peak > 1e-6:
        out /= peak
    return out * vel * 0.34


def pizzicato(f, dur=0.22, vel=0.8):
    n = int(dur * SR)
    t = _t(n)
    out = (np.sin(TAU * f * t) + 0.35 * np.sin(TAU * 2 * f * t)
           + 0.12 * np.sin(TAU * 3 * f * t))
    env = np.clip(t / 0.004, 0, 1) * np.exp(-t * 16)
    env *= np.clip((dur - t) / 0.03, 0, 1)
    return out * env * vel * 0.45


# -------------------------------------------------------------------------
# drums
# -------------------------------------------------------------------------
def kick(vel=1.0, dur=0.30):
    n = int(dur * SR)
    t = _t(n)
    f = 42 + 95 * np.exp(-t * 30)
    ph = TAU * np.cumsum(f) / SR
    out = np.sin(ph) * np.exp(-t * 10)
    out += 0.18 * rng.standard_normal(n) * np.exp(-t * 240)
    return out * vel * 0.75


def snare(vel=1.0, dur=0.20):
    n = int(dur * SR)
    t = _t(n)
    nz = rng.standard_normal(n)
    nz = signal.lfilter([1.0, -0.92], [1.0], nz)
    out = nz * np.exp(-t * 30) * 0.75
    out += 0.30 * np.sin(TAU * 185 * t) * np.exp(-t * 24)
    return out * vel * 0.46


def hat(vel=1.0, open_=False):
    dur = 0.22 if open_ else 0.065
    n = int(dur * SR)
    t = _t(n)
    nz = rng.standard_normal(n)
    nz = signal.lfilter([1.0, -0.97], [1.0], nz)
    nz = signal.lfilter([1.0, -0.97], [1.0], nz)
    env = np.exp(-t * (14 if open_ else 70))
    return nz * env * vel * 0.25


def ride(vel=1.0):
    dur = 0.28
    n = int(dur * SR)
    t = _t(n)
    nz = rng.standard_normal(n)
    nz = signal.lfilter([1.0, -0.9], [1.0], nz)
    metal = np.zeros(n)
    for f in (3200, 4470, 5230, 6810):
        metal += np.sin(TAU * f * t + f * 0.11)
    out = nz * 0.5 + metal * 0.12
    return out * np.exp(-t * 18) * vel * 0.26


def cymbal(vel=1.0, dur=1.8):
    n = int(dur * SR)
    t = _t(n)
    nz = rng.standard_normal(n)
    nz = signal.lfilter([1.0, -0.965], [1.0], nz)
    nz = signal.lfilter([1.0, -0.965], [1.0], nz)
    metal = np.zeros(n)
    for f in (2870, 3640, 4510, 5620, 6930, 8120):
        metal += np.sin(TAU * f * t + f * 0.07)
    out = nz * 0.65 + metal * 0.10
    env = np.exp(-t * 2.4)
    return out * env * vel * 0.42


def woodblock(vel=1.0, pitch=1.0, dur=0.12):
    n = int(dur * SR)
    t = _t(n)
    out = (np.sin(TAU * 940 * pitch * t) * 0.7
           + np.sin(TAU * 1430 * pitch * t) * 0.35)
    out *= np.exp(-t * 68)
    return out * vel * 0.42


def tambourine(vel=1.0):
    n = int(0.16 * SR)
    t = _t(n)
    nz = rng.standard_normal(n)
    nz = signal.lfilter([1.0, -0.93], [1.0], nz)
    out = nz * np.exp(-t * 26)
    for f in (4400, 5900, 7300):
        out += 0.10 * np.sin(TAU * f * t) * np.exp(-t * 40)
    return out * vel * 0.30


def timpani(f=55.0, vel=1.0, dur=0.6):
    n = int(dur * SR)
    t = _t(n)
    out = (np.sin(TAU * f * t) + 0.35 * np.sin(TAU * 2.0 * f * t)
           + 0.12 * np.sin(TAU * 2.9 * f * t))
    out += 0.12 * rng.standard_normal(n) * np.exp(-t * 60)
    return out * np.exp(-t * 5.0) * vel * 0.55


# -------------------------------------------------------------------------
# cartoon SFX
# -------------------------------------------------------------------------
def boing(base=190.0, dur=0.55, depth=0.55, rate=12.5, vel=1.0):
    n = int(dur * SR)
    t = _t(n)
    f = base * (1.0 + depth * np.exp(-t * 5.5) * np.sin(TAU * rate * t))
    ph = TAU * np.cumsum(f) / SR
    out = np.sin(ph) * np.exp(-t * 4.2) + 0.22 * np.sin(2.02 * ph) * np.exp(-t * 6)
    return out * vel * 0.42


def slide_whistle(f0, f1, dur, vel=1.0, vib=6.0):
    n = int(dur * SR)
    t = _t(n)
    f = f0 * (f1 / f0) ** (t / max(dur, 1e-4))
    f *= 1.0 + 0.02 * np.sin(TAU * vib * t)
    ph = TAU * np.cumsum(f) / SR
    out = np.sin(ph) * 0.8 + 0.08 * rng.standard_normal(n)
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)
    return out * env * vel * 0.30


def alarm(dur=0.65, vel=1.0):
    n = int(dur * SR)
    t = _t(n)
    bell = (np.sin(TAU * 1820 * t) + 0.55 * np.sin(TAU * 2430 * t)
            + 0.30 * np.sin(TAU * 3070 * t))
    trem = 0.55 + 0.45 * np.sign(np.sin(TAU * 21.0 * t))
    env = np.clip(t / 0.008, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    return bell * trem * env * vel * 0.20


def ratchet(dur=1.0, rate=20.0, vel=1.0):
    n = int(dur * SR)
    out = np.zeros(n)
    click_n = int(0.006 * SR)
    tc = _t(click_n)
    click = (np.sin(TAU * 1600 * tc) * 0.6
             + rng.standard_normal(click_n) * np.exp(-tc * 400) * 0.6)
    click *= np.exp(-tc * 300)
    step = int(SR / rate)
    for i in range(0, n - click_n, step):
        out[i:i + click_n] += click
    return out * vel * 0.30


def scratch(dur=0.55, vel=1.0):
    n = int(dur * SR)
    t = _t(n)
    f = 70 + 1500 * np.exp(-t * 4.5)
    ph = TAU * np.cumsum(f) / SR
    out = np.sin(ph) * 0.55 * np.exp(-t * 4.0)
    nz = rng.standard_normal(n)
    nz = _lpf(nz, 4200)
    out += nz * 0.45 * np.exp(-t * 3.0) * np.clip(t / 0.01, 0, 1)
    # a couple of needle pops
    for tt in (0.04, 0.17, 0.31):
        i = int(tt * SR)
        k = min(n - i, 300)
        out[i:i + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / 40) * 0.5
    return out * vel * 0.45


def pop(vel=1.0):
    n = int(0.09 * SR)
    t = _t(n)
    out = (np.sin(TAU * 160 * t) * np.exp(-t * 55)
           + rng.standard_normal(n) * np.exp(-t * 220) * 0.4)
    return out * vel * 0.45


def giggle(vel=1.0):
    out = np.zeros(int(0.42 * SR))
    for k, (t0, f) in enumerate(((0.0, 1500), (0.10, 1800), (0.19, 1500))):
        n = int(0.075 * SR)
        tt = _t(n)
        s = np.sin(TAU * f * tt) * np.exp(-tt * 38) * (0.9 - 0.2 * k)
        i = int(t0 * SR)
        out[i:i + n] += s
    return out * vel * 0.32


def whoosh(dur=0.5, vel=1.0):
    n = int(dur * SR)
    t = _t(n)
    nz = rng.standard_normal(n)
    nz = _lpf(nz, 1600)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return nz * env * vel * 0.22


def crash(vel=1.0):
    out = cymbal(vel, 2.2)
    n = len(out)
    t = _t(n)
    out += np.sin(TAU * 48 * t) * np.exp(-t * 13) * 0.55
    out += 0.4 * rng.standard_normal(n) * np.exp(-t * 55)
    return out * vel


# -------------------------------------------------------------------------
# harmonic vocabulary
# -------------------------------------------------------------------------
CH = {
    "C":  dict(root=36, fifth=43, triad=(52, 55, 60), top=(64, 67, 72)),
    "G7": dict(root=43, fifth=50, triad=(50, 53, 59), top=(62, 65, 71)),
    "F":  dict(root=41, fifth=48, triad=(53, 57, 60), top=(65, 69, 72)),
    "A7": dict(root=45, fifth=52, triad=(55, 57, 61), top=(64, 67, 69)),
    "D7": dict(root=38, fifth=45, triad=(50, 54, 57), top=(62, 66, 69)),
    "E7": dict(root=40, fifth=47, triad=(52, 56, 59), top=(64, 68, 71)),
    "Am": dict(root=45, fifth=40, triad=(57, 60, 64), top=(69, 72, 76)),
    "Dm": dict(root=38, fifth=45, triad=(57, 62, 65), top=(69, 74, 77)),
}


def comp_bar(t0, chord, vel=0.7, drums="swing", banjo_chops=True):
    c = CH[chord]
    # bass, two-beat tuba
    place(tuba(mtof(c["root"]), 0.30, 0.9 * vel), t0, 0.55, -0.05)
    place(piano(mtof(c["root"]), 0.55, 0.75 * vel), t0, 0.55, -0.25)
    place(tuba(mtof(c["fifth"]), 0.28, 0.8 * vel), t0 + 2 * SPB, 0.55, -0.05)
    place(piano(mtof(c["fifth"]), 0.55, 0.65 * vel), t0 + 2 * SPB, 0.55, -0.25)
    # stride chords on 1 and 3, with an offbeat lift
    for beat in (1, 3):
        for m in c["triad"]:
            place(piano(mtof(m), 0.30, 0.50 * vel), t0 + beat * SPB, 0.60, -0.22)
        for m in c["triad"]:
            place(piano(mtof(m + 12), 0.16, 0.24 * vel),
                  t0 + (beat + 0.5) * SPB, 0.50, -0.18)
    if banjo_chops:
        for beat in (1.5, 2.5, 3.5):
            for m in c["triad"][1:]:
                place(banjo(mtof(m + 12), 0.16, 0.32 * vel),
                      t0 + beat * SPB + rng.uniform(0, 0.005), 0.45, 0.28)
    if drums == "swing":
        place(kick(0.55 * vel), t0, 0.75)
        place(kick(0.45 * vel), t0 + 2 * SPB, 0.75)
        place(snare(0.30 * vel), t0 + SPB, 0.80)
        place(snare(0.38 * vel), t0 + 3 * SPB, 0.80)
        for k in range(8):
            place(ride(0.20 * vel), t0 + k * SPB / 2, 0.25, 0.25)
        for beat in (0.5, 1.5, 2.5, 3.5):
            place(hat(0.22 * vel), t0 + beat * SPB, 0.5)
    elif drums == "soft":
        for beat in (0, 2):
            place(kick(0.25 * vel), t0 + beat * SPB, 0.7)
        for beat in (1, 3):
            place(snare(0.12 * vel), t0 + beat * SPB, 0.8)
        for k in range(4):
            place(hat(0.10 * vel), t0 + k * SPB, 0.5)
    elif drums == "chase":
        for beat in range(4):
            place(kick(0.55 * vel), t0 + beat * SPB, 0.75)
        for beat in (1, 3):
            place(snare(0.75 * vel), t0 + beat * SPB, 0.8)
        for k in range(8):
            place(hat(0.22 * vel), t0 + k * SPB / 2, 0.5, 0.2)
    elif drums == "finale":
        for beat in (0, 2):
            place(kick(0.85 * vel), t0 + beat * SPB, 0.75)
        place(kick(0.5 * vel), t0 + 3.5 * SPB, 0.75)
        for beat in (1, 3):
            place(snare(0.70 * vel), t0 + beat * SPB, 0.8)
        for k in range(8):
            place(ride(0.26 * vel), t0 + k * SPB / 2, 0.25, 0.25)
        for beat in (0.5, 1.5, 2.5, 3.5):
            place(hat(0.30 * vel), t0 + beat * SPB, 0.5)


def melody_phrase(t0, notes, kind="clarinet", vel=0.8, pan=-0.10, transpose=0):
    """notes: (beat, dur_beats, midi)."""
    for beat, dbeats, midi in notes:
        dur = max(0.12, dbeats * SPB)
        m = midi + transpose
        if kind == "clarinet":
            sig = clarinet(mtof(m), dur, vel)
        elif kind == "trumpet":
            sig = trumpet(mtof(m), dur, vel)
        elif kind == "pizz":
            sig = pizzicato(mtof(m), dur, vel)
        else:
            sig = piano(mtof(m), dur, vel)
        place(sig, t0 + beat * SPB, 1.0, pan)


# =========================================================================
# 1. TITLE CARD  (0 - 4.05)
# =========================================================================
def score_title():
    # snare roll into the main title
    for i in range(18):
        place(snare(0.16 + 0.5 * i / 17), 0.02 + i * 0.029, 0.5, 0.0)
    place(cymbal(0.9, 1.6), 0.55, 0.4, 0.0)
    place(kick(0.9), 0.55, 0.6)
    for m in (48, 52, 55, 60, 64):
        place(trumpet(mtof(m), 0.55, 0.55), 0.55, 0.5, 0.0)
        place(piano(mtof(m), 0.8, 0.45), 0.55, 0.5, -0.2)
    # ball drop lands at 1.02
    place(boing(150, 0.6, 0.45, 11.0), 1.02, 0.55)
    place(woodblock(0.7, 1.0), 1.02, 0.5)
    place(kick(0.4), 1.02, 0.4)
    # bar 1 fanfare melody
    place(cymbal(0.55, 1.2), T(1), 0.22, 0.1)
    for beat, midi, db in ((0, 67, 0.5), (0.5, 69, 0.5), (1.0, 71, 0.5),
                           (1.5, 72, 1.5)):
        place(trumpet(mtof(midi), max(0.2, db * SPB), 0.75), T(1, beat), 0.55, 0.05)
        place(clarinet(mtof(midi + 12), max(0.2, db * SPB), 0.35),
              T(1, beat), 0.45, -0.05)
    comp_bar(T(1), "C", 0.60, drums="swing")
    # piano sparkle run before the iris
    for i, m in enumerate((60, 64, 67, 72, 76, 79, 84, 88)):
        place(piano(mtof(m), 0.35, 0.30), 2.95 + i * 0.055, 0.45, -0.15)
    place(cymbal(0.30, 1.0), 3.55, 0.16, 0.2)


# =========================================================================
# 2. SLEEPY ROOM  (4.05 - 7.35)
# =========================================================================
def score_sleep():
    place(pop(0.6), 4.05, 0.4)
    # soft rocking clarinet
    for t0, m, d in ((4.15, 60, 1.6), (4.85, 64, 1.4), (5.55, 55, 2.0),
                     (6.35, 60, 1.4), (6.75, 64, 1.2)):
        place(clarinet(mtof(m), d, 0.30, vibrato=4.2), t0, 0.55, -0.1)
    for t0, chord in ((4.10, "C"), (5.35, "C"), (6.30, "G7")):
        for m in CH[chord]["triad"]:
            place(piano(mtof(m), 0.9, 0.18), t0, 0.5, -0.2)
        place(piano(mtof(CH[chord]["root"]), 1.1, 0.20), t0, 0.5, -0.25)
    # clock ticks + a soft snore
    t = 4.10
    while t < 7.05:
        place(woodblock(0.10, 1.65, 0.09), t, 0.4, 0.45)
        t += SPB
    for t0 in (4.7, 6.5):
        place(whoosh(0.7, 0.30), t0, 0.25, 0.0)
    # alarm!
    place(alarm(0.60, 0.95), 7.125, 0.55, -0.25)
    # startle hit + boing
    place(cymbal(0.8, 1.4), 7.34, 0.45)
    place(kick(0.8), 7.34, 0.55)
    place(boing(210, 0.7, 0.55, 13.0), 7.35, 0.55)
    place(slide_whistle(420, 1500, 0.55, 0.75), 7.45, 0.40, 0.1)
    place(pop(0.5), 7.95, 0.4)
    place(woodblock(0.5, 0.8), 7.98, 0.45)


# =========================================================================
# 3. MORNING  (8.15 - 11.25)
# =========================================================================
def score_morning():
    # bright little morning call
    phrase = [(0.0, 0.5, 72), (0.5, 0.5, 76), (1.0, 0.5, 79),
              (1.5, 0.5, 76), (2.0, 1.0, 72), (3.0, 0.5, 74), (3.5, 0.5, 76)]
    melody_phrase(8.15, phrase, "clarinet", 0.55, -0.08)
    comp_bar(8.15 + 0.0, "C", 0.42, drums="soft")
    # yawn / stretch: lazy trombone gliss
    place(trombone_wah(mtof(55), 0.95, 0.55, 1.16, 1.3), 8.55, 0.55, 0.0)
    place(clarinet(mtof(84), 0.8, 0.18, vibrato=6.0), 8.75, 0.45, 0.05)
    # scratch behind the ear
    place(ratchet(0.34, 26.0, 0.35), 9.55, 0.28, 0.35)
    place(pizzicato(mtof(88), 0.12, 0.3), 9.92, 0.5, 0.2)
    # wet-dog shake: tambourine + snare roll
    for i in range(10):
        place(tambourine(0.10 + 0.12 * (i % 3 == 0)), 10.15 + i * 0.05, 0.45, 0.25)
    for i in range(8):
        place(snare(0.12 + 0.20 * i / 7), 10.15 + i * 0.068, 0.5, 0.0)
    # bounces to the gramophone
    for i, (t0, base) in enumerate(((10.78, 170), (10.90, 200), (11.02, 230),
                                    (11.14, 260))):
        place(boing(base, 0.30, 0.35, 15.0), t0, 0.30, 0.05)
    for i, m in enumerate((48, 52, 55, 57)):
        place(pizzicato(mtof(m), 0.18, 0.35), 10.80 + i * 0.115, 0.4, -0.05)


# =========================================================================
# 4. GRAMOPHONE + DANCE  (11.25 - 23.72)
# =========================================================================
def score_dance():
    # walk to the machine
    for t0, chord in ((11.25, "C"), (12.1875, "G7")):
        comp_bar(t0, chord, 0.45, drums="soft")
    # cranking the handle
    place(ratchet(1.10, 21.0, 0.42), 13.05, 0.35, -0.15)
    # needle drop and motor spin-up
    place(pop(0.7), 14.40, 0.5, -0.3)
    place(whoosh(0.5, 0.35), 14.42, 0.30, -0.3)
    ph_dur = 0.55
    n = int(ph_dur * SR)
    tt = _t(n)
    f = 48 + 210 * (tt / ph_dur) ** 2
    ph = TAU * np.cumsum(f) / SR
    place(np.sin(ph) * 0.12 * np.clip((ph_dur - tt) / 0.08, 0, 1),
          14.40, 0.6, -0.25)

    # --- first dance chorus, bars 8-9 in C -------------------------------
    comp_bar(T(8), "C", 0.68, drums="swing")
    comp_bar(T(9), "C", 0.68, drums="swing")
    intro = [(0.0, 0.5, 76), (0.5, 0.5, 79), (1.0, 0.5, 76), (1.5, 0.5, 72),
             (2.0, 0.5, 74), (2.5, 0.5, 76), (3.0, 1.2, 79)]
    melody_phrase(T(8), intro, "clarinet", 0.62, -0.08)
    melody_phrase(T(8), [(0.0, 0.5, 64), (0.5, 0.5, 67), (1.0, 0.5, 64),
                         (1.5, 0.5, 60), (2.0, 0.5, 62), (2.5, 0.5, 64),
                         (3.0, 1.2, 67)], "trumpet", 0.34, 0.12)
    intro2 = [(0.0, 1.0, 72), (1.0, 0.5, 69), (1.5, 0.5, 72),
              (2.0, 1.0, 74), (3.0, 1.2, 76)]
    melody_phrase(T(9), intro2, "clarinet", 0.58, -0.08)

    # --- sing-along, word-synced (banner 17.75 - 21.30) -------------------
    word1 = 17.75
    w1_dt = 1.80 / 6.0
    line1 = [72, 72, 67, 69, 67, 64]
    for i, m in enumerate(line1):
        t0 = word1 + i * w1_dt
        dur = (1.80 - i * w1_dt) if i == len(line1) - 1 else w1_dt * 0.92
        place(clarinet(mtof(m), dur + 0.12, 0.66, vibrato=5.4), t0, 0.62, -0.10)
        place(trumpet(mtof(m - 12), dur + 0.10, 0.30), t0, 0.40, 0.10)
        place(banjo(mtof(m + 12), 0.25, 0.30), t0, 0.40, 0.25)
    word2 = 19.55
    w2_dt = (21.30 - 19.55) / 4.0
    line2 = [67, 69, 67, 72]
    for i, m in enumerate(line2):
        t0 = word2 + i * w2_dt
        dur = (21.30 - t0) if i == len(line2) - 1 else w2_dt * 0.92
        place(clarinet(mtof(m), dur + 0.15, 0.68, vibrato=5.4), t0, 0.62, -0.10)
        place(trumpet(mtof(m - 12), dur + 0.12, 0.34), t0, 0.42, 0.10)
        place(banjo(mtof(m + 12), 0.28, 0.34), t0, 0.42, 0.25)
    # harmony under the sing-along
    comp_bar(T(10), "G7", 0.52, drums="swing")
    comp_bar(T(11), "G7", 0.54, drums="swing")
    # banner slide
    place(slide_whistle(900, 420, 0.28, 0.35), 17.35, 0.35, 0.15)

    # --- piano break into the theft --------------------------------------
    # NOTE: the full bar is written by hand so the band cuts dead on the grab.
    t0 = T(12)
    c = CH["C"]
    place(tuba(mtof(c["root"]), 0.30, 0.55), t0, 0.55, -0.05)
    place(piano(mtof(c["root"]), 0.50, 0.45), t0, 0.55, -0.25)
    place(tuba(mtof(c["fifth"]), 0.28, 0.45), t0 + 2 * SPB, 0.55, -0.05)
    place(piano(mtof(c["fifth"]), 0.50, 0.40), t0 + 2 * SPB, 0.55, -0.25)
    for m in c["triad"]:
        place(piano(mtof(m), 0.30, 0.34), t0 + SPB, 0.60, -0.22)
        place(piano(mtof(m), 0.30, 0.30), t0 + 2.55 * SPB, 0.60, -0.22)
    place(kick(0.45), t0, 0.7)
    place(snare(0.30), t0 + SPB, 0.8)
    place(kick(0.40), t0 + 2 * SPB, 0.7)
    for beat in (1.5, 2.55):
        for m in c["triad"][1:]:
            place(banjo(mtof(m + 12), 0.16, 0.26),
                  t0 + beat * SPB, 0.45, 0.28)
    piano_break = [(0.0, 0.5, 72), (0.5, 0.5, 76), (1.0, 0.4, 79),
                   (1.5, 0.4, 84), (2.0, 0.4, 79)]
    for beat, db, m in piano_break:
        place(piano(mtof(m), 0.30, 0.34), T(12, beat), 0.55, -0.15)
    for i in range(8):
        place(snare(0.10 + 0.1 * i / 7), 23.30 + i * 0.05, 0.45, 0.0)
    # record snatch: scratch + sudden silence
    place(scratch(0.55, 0.95), 23.72, 0.70, -0.1)
    place(pop(0.8), 23.74, 0.5, 0.0)


# =========================================================================
# 5. CHASE  (24.2 - 33.35)
# =========================================================================
def score_chase():
    # sneaky pickup
    for i in range(6):
        place(snare(0.08 + 0.05 * i), 24.20 + i * 0.03, 0.4, 0.1)
    # A-minor sneaky vamp, bars 13-15
    for b, chord in ((13, "Am"), (14, "E7"), (15, "Am")):
        t0 = T(b)
        comp_bar(t0, chord, 0.62, drums="chase")
        # chromatic descending bass walk
        walk = (45, 44, 43, 42) if b % 2 else (45, 43, 41, 40)
        for i, m in enumerate(walk):
            place(tuba(mtof(m), 0.20, 0.55), t0 + i * SPB, 0.55, -0.05)
    # chase melody, staccato clarinet
    chase1 = [(0, 0.5, 69), (0.5, 0.25, 70), (0.75, 0.25, 69),
              (1.0, 0.5, 68), (1.5, 0.25, 69), (1.75, 0.25, 70),
              (2.0, 0.5, 72), (2.5, 0.5, 71), (3.0, 0.5, 69), (3.5, 0.5, 68)]
    melody_phrase(T(13), chase1, "clarinet", 0.55, 0.10)
    chase2 = [(0, 0.25, 76), (0.25, 0.25, 77), (0.5, 0.25, 76),
              (0.75, 0.25, 75), (1.0, 0.25, 76), (1.25, 0.25, 72),
              (1.5, 0.25, 69), (1.75, 0.25, 68), (2.0, 0.5, 69),
              (2.5, 0.5, 71), (3.0, 0.5, 72), (3.5, 0.5, 75)]
    melody_phrase(T(14), chase2, "clarinet", 0.62, 0.10)
    melody_phrase(T(14), [(0, 0.5, 57), (0.5, 0.5, 59), (1, 0.5, 60),
                          (1.5, 0.5, 62), (2, 0.5, 63), (2.5, 0.5, 62),
                          (3, 0.5, 60), (3.5, 0.5, 59)], "trumpet", 0.32, 0.05)
    melody_phrase(T(15), chase1, "clarinet", 0.58, 0.10)

    # dash from the spotlight to the wall (30.0 - 30.75), then the fight
    t0 = 30.0
    place(tuba(mtof(40), 0.26, 0.58), t0, 0.55, -0.05)
    place(tuba(mtof(47), 0.24, 0.52), t0 + 0.55, 0.55, -0.05)
    place(kick(0.55), t0, 0.7)
    place(snare(0.40), t0 + 0.28, 0.75)
    place(snare(0.52), t0 + 0.54, 0.75)
    for i, m in enumerate((64, 67, 71, 74, 76, 79)):
        place(clarinet(mtof(m), 0.10, 0.42), t0 + i * 0.12, 0.45, 0.1)

    # fight cloud: drums and biffs
    place(cymbal(0.8, 1.4), 30.75, 0.55, 0.2)
    for i, ts in enumerate((30.75, 31.10, 31.45, 31.80, 32.15)):
        chord = (63, 66, 70) if i % 2 else (60, 63, 67)
        for m in chord:
            place(trumpet(mtof(m), 0.16, 0.55), ts, 0.45, 0.15)
        place(kick(0.8), ts, 0.55)
        place(snare(0.7), ts + 0.06, 0.50)
    t = 30.90
    i = 0
    while t < 33.30:
        place(kick(0.30 + 0.35 * (i % 2)), t, 0.5)
        place(snare(0.25 + 0.30 * (i % 3 == 0)), t + 0.06, 0.5)
        place(woodblock(0.25, 1.2 + 0.2 * (i % 3)), t + 0.12, 0.45, 0.3)
        t += SPB / 2
        i += 1
    # snare roll into the crash
    for i in range(27):
        tt = 32.10 + i * 0.045
        place(snare(0.08 + 0.55 * i / 26), tt, 0.45, 0.0)
    place(cymbal(0.55, 1.0), 32.75, 0.35)


# =========================================================================
# 6. CRASH, DAZE, BANJO  (33.35 - 37.5)
# =========================================================================
def score_crash():
    place(crash(1.0), 33.35, 0.75, 0.0)
    place(timpani(52, 0.9, 0.9), 33.35, 0.65)
    for m in (36, 43, 48, 51):
        place(piano(mtof(m), 0.9, 0.50), 33.35, 0.55, -0.2)
    place(whoosh(0.4, 0.5), 33.38, 0.35, 0.2)
    # wah-wah-waaah trombones
    for i, (t0, m) in enumerate(((33.72, 60), (34.06, 59), (34.40, 58))):
        place(trombone_wah(mtof(m), 0.36, 0.55, 1.08, 3.2),
              t0, 0.55, -0.05 + i * 0.04)
    # mouse giggle
    place(giggle(1.0), 34.12, 0.55, 0.35)
    place(giggle(0.7), 34.52, 0.45, 0.35)
    # daze: woozy clarinet
    for i, (t0, m) in enumerate(((34.55, 67), (34.85, 65), (35.15, 63))):
        place(clarinet(mtof(m), 0.32, 0.30, vibrato=6.5), t0, 0.45, -0.1)
    # mouse trumpet solo (35.45 - 37.05)
    solo = [(35.45, 0.20, 72), (35.65, 0.15, 76), (35.82, 0.30, 79),
            (36.15, 0.12, 76), (36.30, 0.24, 72), (36.55, 0.12, 69),
            (36.68, 0.14, 72), (36.85, 0.12, 74), (37.00, 0.32, 79)]
    for t0, d, m in solo:
        place(trumpet(mtof(m), d, 0.62, mute=0.15, growl=0.4), t0, 0.60, 0.30)
    for i in range(4):
        place(ride(0.22), 35.5 + i * SPB, 0.25, 0.2)
    # banjo pops in at 36.95
    place(pop(0.7), 36.95, 0.5, 0.2)
    for i, m in enumerate((72, 76, 79, 84)):
        place(banjo(mtof(m), 0.20, 0.42), 36.97 + i * 0.045, 0.55, 0.25)
    # zip to the spotlight
    place(slide_whistle(330, 1200, 0.36, 0.60), 37.10, 0.45, 0.1)
    place(pop(0.6), 37.48, 0.45, 0.0)


# =========================================================================
# 7. JAM  (37.5 - 48.75)
# =========================================================================
def score_jam():
    chords = ["C", "A7", "D7", "G7", "C", "G7"]
    melody = [
        [(0, 1.0, 76), (1.5, 0.5, 79), (2, 1.0, 76), (3, 1.0, 72)],
        [(0, 0.5, 76), (0.5, 0.5, 73), (1, 1.0, 69), (2, 1.0, 67),
         (3, 1.0, 64)],
        [(0, 0.5, 78), (0.5, 0.5, 81), (1, 0.5, 78), (1.5, 0.5, 74),
         (2, 1.0, 69), (3, 1.0, 74)],
        [(0, 1.0, 79), (1, 1.0, 77), (2, 1.0, 74), (3, 1.0, 71)],
        [(0, 0.5, 76), (0.5, 0.5, 79), (1, 1.5, 84), (2.5, 0.5, 79),
         (3, 1.0, 76)],
        [(0, 1.0, 74), (1, 1.0, 77), (2, 2.0, 79)],
    ]
    for i, chord in enumerate(chords):
        t0 = T(20 + i)
        vel = 0.66 + 0.03 * i
        comp_bar(t0, chord, vel, drums="swing")
        melody_phrase(t0, melody[i], "clarinet", 0.60, -0.08)
        melody_phrase(t0, [(b, d, m - 12) for b, d, m in melody[i]],
                      "trumpet", 0.30, 0.15)

    # banjo 16th-note arpeggio weave, a bar at a time
    for i, chord in enumerate(chords):
        t0 = T(20 + i)
        c = CH[chord]
        tones = (c["top"][0], c["top"][1], c["top"][2], c["top"][1])
        for k in range(16):
            m = tones[k % 4] + (12 if k % 8 == 6 else 0)
            place(banjo(mtof(m), 0.12, 0.16 + 0.05 * (k % 2)),
                  t0 + k * SPB / 4, 0.35, 0.32)
    # spin at 41.3
    place(whoosh(0.7, 0.7), 41.30, 0.35, 0.0)
    for i in range(8):
        place(ride(0.24), 41.30 + i * 0.08, 0.30, 0.25)
    for i in range(6):
        place(snare(0.30 + 0.08 * i), 41.35 + i * 0.10, 0.40, 0.0)
    # build into the finale
    for i in range(14):
        place(tambourine(0.10 + 0.06 * (i % 3)), 46.90 + i * 0.13, 0.35, 0.3)
    for i in range(16):
        place(snare(0.08 + 0.45 * i / 15), 47.20 + i * 0.095, 0.45, 0.0)
    place(cymbal(0.35, 0.9), 48.55, 0.30)


# =========================================================================
# 8. FINALE  (48.75 - 54.25)
# =========================================================================
def score_finale():
    # F / G7 / C big finish
    comp_bar(T(26), "F", 0.70, drums="finale")
    comp_bar(T(27), "G7", 0.74, drums="finale")
    # reprise the sing-along tune, stretched across bars 26-28
    line = [(48.95, 0.30, 72), (49.25, 0.30, 72), (49.55, 0.30, 67),
            (49.85, 0.30, 69), (50.15, 0.30, 67), (50.45, 0.80, 64),
            (51.25, 0.30, 67), (51.55, 0.30, 69), (51.85, 0.30, 67),
            (52.15, 0.35, 72)]
    for t0, d, m in line:
        place(trumpet(mtof(m), d + 0.10, 0.70), t0, 0.58, 0.08)
        place(clarinet(mtof(m + 12), d + 0.10, 0.45), t0, 0.50, -0.08)
        place(banjo(mtof(m + 12), 0.20, 0.28), t0, 0.40, 0.25)
    # big chord at 52.5 (the flash) and a held finish
    place(cymbal(1.0, 2.6), BIG_CHORD, 0.75, 0.0)
    place(timpani(36, 1.0, 1.4), BIG_CHORD, 0.70)
    place(kick(1.0), BIG_CHORD, 0.65)
    for m in (36, 43, 48, 52, 55, 60, 64, 67):
        place(piano(mtof(m), 1.6, 0.42), BIG_CHORD, 0.55, -0.15)
        place(trumpet(mtof(m), 1.2, 0.30), BIG_CHORD, 0.45, 0.12)
    # piano flourish up to the bow
    for i, m in enumerate((60, 64, 67, 72, 76, 79, 84, 88)):
        place(piano(mtof(m), 0.28, 0.28), 53.25 + i * 0.045, 0.45, -0.1)
    # bow: little tuba doink
    place(tuba(mtof(43), 0.30, 0.70), 53.45, 0.55)
    place(woodblock(0.6, 0.9), 53.45, 0.45, 0.3)
    # held C chord, soft, through the hat tip
    for m in (48, 55, 60, 64):
        place(piano(mtof(m), 1.1, 0.16), 53.50, 0.45, -0.2)
    place(cymbal(0.30, 1.2), 54.25, 0.25, 0.0)


# =========================================================================
# 9. TAG + END CARD  (54.375 - 60)
# =========================================================================
def score_tag():
    # "shave and a haircut" (knock-knock rhythm)
    tag = [(54.375, 0.18, 72), (54.61, 0.10, 67), (54.72, 0.10, 67),
           (54.84, 0.10, 69), (54.96, 0.30, 67)]
    for t0, d, m in tag:
        place(clarinet(mtof(m), d + 0.05, 0.62), t0, 0.55, -0.10)
        place(banjo(mtof(m), 0.16, 0.30), t0, 0.40, 0.28)
        place(woodblock(0.55, 1.0), t0, 0.42, 0.30)
    # drum roll / cymbal swell to the punchline
    for i in range(24):
        place(snare(0.06 + 0.35 * i / 23), 55.35 + i * 0.037, 0.40, 0.0)
    place(cymbal(0.35, 1.4), 55.95, 0.30)
    # "two bits!"
    place(cymbal(0.85, 1.8), TWO_BITS, 0.55, 0.0)
    place(kick(0.9), TWO_BITS, 0.55)
    for m in (36, 43, 48, 55, 60, 64):
        place(piano(mtof(m), 0.8, 0.34), TWO_BITS, 0.45, -0.18)
    place(clarinet(mtof(71), 0.12, 0.60), TWO_BITS, 0.50, -0.05)
    place(clarinet(mtof(72), 0.45, 0.65), TWO_BITS + 0.15, 0.50, -0.05)
    place(trumpet(mtof(59), 0.12, 0.40), TWO_BITS, 0.42, 0.05)
    place(trumpet(mtof(60), 0.45, 0.45), TWO_BITS + 0.15, 0.42, 0.05)
    # ball lands on the period with a soft boing
    place(boing(170, 0.45, 0.30, 12.0), 56.66, 0.40, 0.1)
    place(woodblock(0.5, 1.2), 56.66, 0.35, 0.35)
    # gentle music-box outro
    for i, (t0, m) in enumerate(((57.0, 72), (57.35, 76), (57.7, 79),
                                  (58.05, 84), (58.45, 79), (58.8, 72))):
        place(piano(mtof(m), 0.9, 0.16), t0, 0.4, -0.1)
        place(banjo(mtof(m), 0.3, 0.10), t0, 0.35, 0.25)
    for m in (48, 55, 60):
        place(piano(mtof(m), 1.6, 0.10), 57.0, 0.4, -0.2)
        place(piano(mtof(m), 1.8, 0.08), 58.3, 0.4, -0.2)
    place(cymbal(0.18, 1.2), 59.10, 0.18, 0.0)


# =========================================================================
# surface noise / vinyl bed
# =========================================================================
def add_surface_noise():
    n = NS
    # gentle constant hiss
    hiss = rng.standard_normal(n)
    hiss = _hpf(hiss, 1800)
    hiss *= 0.0011
    # crackle: sparse pops
    imp = np.zeros(n)
    idx = rng.integers(0, n, int(DURATION * 7))
    imp[idx] = rng.standard_normal(len(idx)) * 0.9
    kernel = rng.standard_normal(18) * np.exp(-np.arange(18) / 3.0)
    pops = signal.fftconvolve(imp, kernel)[:n]
    pops = _hpf(pops, 500)
    pops *= 0.012
    # a little more dust while the record is actually spinning
    gain = np.ones(n)
    gain *= 0.55
    i0, i1 = int(14.4 * SR), int(23.72 * SR)
    gain[i0:i1] = 1.0
    i0, i1 = int(56.2 * SR), n
    gain[i0:i1] = 0.8
    bed = (hiss + pops) * gain
    mix[:, 0] += bed
    mix[:, 1] += bed


# =========================================================================
# mixdown
# =========================================================================
def mixdown():
    add_surface_noise()
    # narrow the image a little: early-30s optical track feel
    mono = mix.mean(axis=1, keepdims=True)
    out = mix * 0.58 + mono * 0.42
    # band-limit: 90 Hz .. 6.2 kHz
    out = signal.sosfilt(signal.butter(2, 90, btype="high", fs=SR, output="sos"),
                         out, axis=0)
    out = signal.sosfilt(signal.butter(2, 6200, btype="low", fs=SR, output="sos"),
                         out, axis=0)
    # a little midrange warmth
    peak_eq = signal.butter(1, [220, 900], btype="band", fs=SR, output="sos")
    out += signal.sosfilt(peak_eq, out, axis=0) * 0.18
    # room reverb
    ir_n = int(0.9 * SR)
    tt = _t(ir_n)
    env = np.exp(-tt * 4.6)
    ir_l = rng.standard_normal(ir_n) * env
    ir_r = rng.standard_normal(ir_n) * env
    ir_l = _lpf(ir_l, 4200)
    ir_r = _lpf(ir_r, 4200)
    pred = int(0.018 * SR)
    ir_l = np.concatenate((np.zeros(pred), ir_l))
    ir_r = np.concatenate((np.zeros(pred), ir_r))
    ir_l /= np.sqrt(np.sum(ir_l ** 2))
    ir_r /= np.sqrt(np.sum(ir_r ** 2))
    wet_l = signal.fftconvolve(out[:, 0], ir_l)[:NS]
    wet_r = signal.fftconvolve(out[:, 1], ir_r)[:NS]
    out += 0.11 * np.stack((wet_l, wet_r), axis=1)
    # optical-track soft clipping
    out = np.tanh(out * 1.25) / np.tanh(1.25)
    # fades
    fi = int(0.012 * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    fade_start = int(59.05 * SR)
    out[fade_start:] *= np.linspace(1, 0, NS - fade_start)[:, None] ** 1.4
    # normalize
    peak = float(np.max(np.abs(out)))
    out *= 0.88 / max(peak, 1e-9)
    return out


def main():
    t0 = time.time()
    print("scoring title...")
    score_title()
    print("scoring sleepy room...")
    score_sleep()
    print("scoring morning...")
    score_morning()
    print("scoring dance...")
    score_dance()
    print("scoring chase...")
    score_chase()
    print("scoring crash...")
    score_crash()
    print("scoring jam...")
    score_jam()
    print("scoring finale...")
    score_finale()
    print("scoring tag...")
    score_tag()
    print("mixing (%.1fs elapsed)..." % (time.time() - t0))
    out = mixdown()
    pcm = np.clip(out * 32767.0, -32768, 32767).astype(np.int16)
    wavfile.write("soundtrack.wav", SR, pcm)
    rms = math.sqrt(float(np.mean(out ** 2)))
    print("wrote soundtrack.wav  %.2fs  peak %.3f  rms %.3f" %
          (len(pcm) / SR, float(np.max(np.abs(out))), rms))
    print("done in %.1fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
