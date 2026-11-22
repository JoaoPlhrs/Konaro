#!/usr/bin/env python3
"""Gera os sons do Konaro OS (composição original, sintetizada aqui).

startup.wav: acorde suave e brilhante (fá maior com nona) que abre em arpejo e
some devagar — tocado ao entrar na sessão.
Uso: make-sounds.py <dir de saída>
"""
import math
import os
import struct
import sys
import wave

RATE = 48000


def tone(freq, start, dur, gain, total):
    """Nota com timbre de sino suave (parciais harmônicas que decaem em ritmos diferentes)."""
    out = [0.0] * total
    s0 = int(start * RATE)
    n = int(dur * RATE)
    partials = [(1.0, 1.0, 2.2), (2.0, 0.35, 3.5), (3.0, 0.12, 5.0), (4.01, 0.06, 7.0)]
    for i in range(n):
        t = i / RATE
        attack = min(1.0, t / 0.012)
        v = 0.0
        for mult, amp, decay in partials:
            v += amp * math.exp(-decay * t) * math.sin(2 * math.pi * freq * mult * t)
        idx = s0 + i
        if idx < total:
            out[idx] += gain * attack * v
    return out


def startup():
    total = int(3.2 * RATE)
    mix = [0.0] * total
    # F3, C4, F4, A4, G5 — arpejo rápido que vira acorde
    notes = [(174.61, 0.00, 0.30), (261.63, 0.07, 0.24), (349.23, 0.14, 0.22),
             (440.00, 0.21, 0.20), (783.99, 0.30, 0.13)]
    for freq, start, gain in notes:
        for i, v in enumerate(tone(freq, start, 3.0 - start, gain, total)):
            mix[i] += v
    # eco curto para dar espaço
    delay = int(0.11 * RATE)
    for i in range(total - 1, delay, -1):
        mix[i] += 0.22 * mix[i - delay]
    peak = max(abs(v) for v in mix) or 1.0
    fade = int(0.4 * RATE)
    data = []
    for i, v in enumerate(mix):
        if i > total - fade:
            v *= (total - i) / fade
        data.append(int(32767 * 0.8 * v / peak))
    return data


def write(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples))


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    write(os.path.join(out, "startup.wav"), startup())
    print("som", os.path.join(out, "startup.wav"))
