"""Meu Avatar (Konamoji) — crie um personagem com a sua cara para o seu perfil.

Arte original do Konaro OS: um rosto em estilo "massinha" (volume feito só com
gradientes, porque o QtSvg não tem desfoque), olhos grandes com íris colorida e
brilho, sobrancelhas e cabelo com volume. As escolhas viram a foto do usuário:
tela de login, Iniciar e Configurações (AccountsService e ~/.face.icon).
Tudo fica no computador; nada é enviado a lugar nenhum.
"""

import argparse
import json
import math
import os
import subprocess
import sys
from collections import OrderedDict
from threading import Lock

from PyQt6.QtCore import QByteArray, QObject, QRectF, QSize, Qt, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPainter, QPainterPath
from PyQt6.QtQml import QQmlImageProviderBase
from PyQt6.QtQuick import QQuickImageProvider
from PyQt6.QtSvg import QSvgRenderer

from .i18n import _

CONFIG = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "konaro", "avatar.json")

# ------------------------------------------------------------------ paletas
SKINS = ["#FCE3D0", "#F6D2B8", "#EDBB98", "#DCA47C", "#C68A5E", "#A86F46", "#8A5534", "#5E3A24"]
HAIR = ["#1F1714", "#3B2619", "#6B4127", "#9A6236", "#C99555", "#E6C78A", "#B7B3AE", "#F1EFEA", "#A8322A", "#6E5BD3"]
EYES = ["#5B3A22", "#2E1E14", "#8A6A35", "#4F7A3A", "#3E7CC4", "#7C8895"]
SHIRTS = ["#2C2C30", "#F5F5F7", "#3C6FD8", "#E5484D", "#2FA36B", "#F2A33A", "#8E5CD9", "#E86AA6"]
BACKGROUNDS = ["#DCEBFF", "#FFE3CF", "#DDF5E3", "#EFE2FF", "#FFE1EC", "#FFF3C4", "#E6E8EC", "#CFF1F2"]

# parte -> quantidade de opções
OPTIONS = OrderedDict([
    ("skin", len(SKINS)), ("details", 4),
    ("hair", 11), ("hairColor", len(HAIR)),
    ("eyes", 5), ("eyeColor", len(EYES)),
    ("brows", 5), ("nose", 3), ("mouth", 6),
    ("beard", 5), ("glasses", 5), ("headwear", 5),
    ("shirt", len(SHIRTS)), ("background", len(BACKGROUNDS)),
])
DEFAULT = {"skin": 2, "details": 0, "hair": 2, "hairColor": 2, "eyes": 0, "eyeColor": 0, "brows": 0,
           "nose": 0, "mouth": 0, "beard": 0, "glasses": 0, "headwear": 0, "shirt": 2, "background": 0}
COLORS = {"skin": SKINS, "hairColor": HAIR, "eyeColor": EYES, "shirt": SHIRTS, "background": BACKGROUNDS}

# recortes (viewBox) para as miniaturas mostrarem só a parte que muda
CROPS = {
    "full": (0, 0, 512, 512), "head": (66, 18, 380, 380), "eyes": (150, 150, 212, 212),
    "mouth": (166, 250, 180, 180), "lower": (106, 220, 300, 300), "face": (110, 120, 292, 292),
}

# abas do editor: (id, rótulo, [(parte, tipo, recorte)])
TABS = [
    ("skin", "Skin", [("skin", "color", None), ("details", "shape", "face")]),
    ("hair", "Hair", [("hair", "shape", "head"), ("hairColor", "color", None)]),
    ("eyes", "Eyes", [("eyes", "shape", "eyes"), ("eyeColor", "color", None)]),
    ("brows", "Eyebrows", [("brows", "shape", "eyes")]),
    ("nose", "Nose", [("nose", "shape", "mouth")]),
    ("mouth", "Mouth", [("mouth", "shape", "mouth")]),
    ("beard", "Beard", [("beard", "shape", "lower")]),
    ("glasses", "Glasses", [("glasses", "shape", "face")]),
    ("headwear", "Headwear", [("headwear", "shape", "head")]),
    ("shirt", "Clothes", [("shirt", "color", None)]),
    ("background", "Background", [("background", "color", None)]),
]
SECTION_LABELS = {"skin": "Skin tone", "details": "Details", "hair": "Style", "hairColor": "Color",
                  "eyes": "Shape", "eyeColor": "Color", "brows": "Style", "nose": "Shape", "mouth": "Expression",
                  "beard": "Style", "glasses": "Style", "headwear": "Style", "shirt": "Color", "background": "Color"}


# ------------------------------------------------------------------ cores
def _rgb(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in rgb)


def shade(c, f):
    """f < 1 escurece, f > 1 clareia (em direção ao branco)."""
    r = _rgb(c)
    if f >= 1:
        return _hex([v + (255 - v) * (f - 1) for v in r])
    return _hex([v * f for v in r])


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


# ------------------------------------------------------------------ desenho
HEAD = ("M256,72 C352,72 394,142 394,226 C394,304 362,372 302,400 C284,408 268,412 256,412 "
        "C244,412 228,408 210,400 C150,372 118,304 118,226 C118,142 160,72 256,72 Z")
EYE_Y = 236
EYE_X = (202, 310)


def _almond(x, y, w=36, up=27, down=22):
    return ("M%d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d Z"
            % (x - w, y, x - w * 0.62, y - up, x + w * 0.62, y - up, x + w, y,
               x + w * 0.62, y + down, x - w * 0.62, y + down, x - w, y))


def _eye_open(x, o, iris, sleepy=False, big=False):
    skin = SKINS[o["skin"] % len(SKINS)]
    w, up, down = (40, 31, 26) if big else (36, 27, 22)
    out = ['<path d="%s" fill="url(#sclera)"/>' % _almond(x, EYE_Y, w, up, down)]
    r = 18 if big else 16
    cy = EYE_Y + 1
    out.append('<circle cx="%d" cy="%d" r="%d" fill="url(#iris)"/>' % (x, cy, r))
    out.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="2.5" opacity="0.55"/>'
               % (x, cy, r, shade(iris, 0.45)))
    out.append('<circle cx="%d" cy="%d" r="%d" fill="#120D0B"/>' % (x, cy, int(r * 0.48)))
    out.append('<circle cx="%d" cy="%d" r="%.1f" fill="white"/>' % (x - r * 0.38, cy - r * 0.42, r * 0.32))
    out.append('<circle cx="%d" cy="%d" r="%.1f" fill="white" opacity="0.8"/>' % (x + r * 0.42, cy + r * 0.4, r * 0.14))
    if sleepy:   # pálpebra caída cobrindo o terço de cima
        out.append('<path d="M%d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d Z" fill="%s"/>'
                   % (x - w - 2, EYE_Y, x - w * 0.6, EYE_Y - up - 6, x + w * 0.6, EYE_Y - up - 6, x + w + 2, EYE_Y,
                      x + w * 0.5, EYE_Y - 9, x - w * 0.5, EYE_Y - 9, x - w - 2, EYE_Y, shade(skin, 0.93)))
    # linha da pálpebra superior com um traço de cílio no canto externo
    side = -1 if x < 256 else 1
    lid_top = EYE_Y - up + (12 if sleepy else 0)
    out.append('<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="#2A1B15" stroke-width="5" stroke-linecap="round"/>'
               % (x - w, EYE_Y, x - w * 0.6, lid_top, x + w * 0.6, lid_top, x + w, EYE_Y))
    out.append('<path d="M%d,%d q%d,%d %d,%d" fill="none" stroke="#2A1B15" stroke-width="4" stroke-linecap="round"/>'
               % (x + side * w, EYE_Y, side * 8, -3, side * 12, -10))
    # dobra da pálpebra
    out.append('<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
               % (x - w * 0.8, EYE_Y - up + 2, x - w * 0.4, EYE_Y - up - 10, x + w * 0.4, EYE_Y - up - 10,
                  x + w * 0.8, EYE_Y - up + 2, shade(skin, 0.72)))
    return "".join(out)


def _eye_closed(x, happy=True):
    if happy:   # "olhinho sorrindo"
        return ('<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="#2A1B15" stroke-width="6" stroke-linecap="round"/>'
                % (x - 30, EYE_Y + 6, x - 16, EYE_Y - 18, x + 16, EYE_Y - 18, x + 30, EYE_Y + 6))
    return ('<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="#2A1B15" stroke-width="6" stroke-linecap="round"/>'
            % (x - 30, EYE_Y - 2, x - 14, EYE_Y + 14, x + 14, EYE_Y + 14, x + 30, EYE_Y - 2))


def _hair_paths(style):
    """(atrás da cabeça, na frente) para cada estilo de cabelo."""
    back, front = "", ""
    if style == 1:      # curto
        front = ("M128,236 C112,170 128,90 210,66 C250,54 300,56 338,76 C390,104 404,170 386,236 "
                 "C380,206 372,184 360,170 C344,156 330,152 318,150 C296,160 272,148 250,140 C222,150 196,152 176,160 C156,170 142,192 128,236 Z")
    elif style == 2:    # repartido de lado
        front = ("M124,238 C106,150 140,80 220,62 C300,48 384,82 396,170 C400,200 394,226 388,240 "
                 "C380,200 366,176 344,160 C304,142 252,150 216,126 C206,150 182,168 162,180 C146,192 134,212 124,238 Z")
    elif style == 3:    # topete
        front = ("M126,232 C110,160 136,104 186,82 C196,48 260,30 316,46 C364,60 398,110 392,176 "
                 "C390,200 388,220 384,236 C378,200 366,176 348,162 C320,146 290,150 262,142 C236,150 212,146 192,156 C164,168 142,196 126,232 Z")
    elif style == 4:    # cacheado curto
        front = ""
    elif style == 5:    # black power
        back = "M60,240 C40,110 140,20 256,22 C372,20 472,110 452,240 C446,300 410,330 392,300 L392,220 C392,150 340,110 256,110 C172,110 120,150 120,220 L120,300 C102,330 66,300 60,240 Z"
        front = ("M118,224 C112,150 170,104 256,102 C342,104 400,150 394,224 C380,180 340,150 256,148 "
                 "C172,150 132,180 118,224 Z")
    elif style == 6:    # longo liso
        back = "M106,220 C96,120 170,56 256,56 C342,56 416,120 406,220 L414,452 C380,470 336,470 318,452 L318,260 L194,260 L194,452 C176,470 132,470 98,452 Z"
        front = ("M114,250 C102,130 176,60 256,60 C336,60 410,130 398,250 C392,200 380,170 362,152 "
                 "C330,124 300,118 256,120 C226,150 180,170 152,174 C136,190 124,216 114,250 Z")
    elif style == 7:    # chanel (bob)
        back = "M100,236 C92,120 170,56 256,56 C342,56 420,120 412,236 L414,350 C394,372 360,372 346,350 L346,250 L166,250 L166,350 C152,372 118,372 98,350 Z"
        front = ("M112,262 C100,134 172,58 256,58 C340,58 412,134 400,262 C392,214 384,188 372,174 L370,160 "
                 "C340,170 300,174 256,172 C212,174 172,170 142,160 L140,174 C128,188 120,214 112,262 Z")
    elif style == 8:    # coque
        back = "M206,62 C206,20 306,20 306,62 C306,96 206,96 206,62 Z"
        front = ("M124,224 C116,140 172,82 256,80 C340,82 396,140 388,224 C376,186 356,160 330,148 "
                 "C300,136 280,140 256,148 C232,140 212,136 182,148 C156,160 136,186 124,224 Z")
    elif style == 9:    # ondulado médio
        back = "M104,230 C94,120 172,58 256,58 C340,58 418,120 408,230 C422,280 404,330 384,350 C362,330 372,300 360,270 L152,270 C140,300 150,330 128,350 C108,330 90,280 104,230 Z"
        front = ("M114,246 C104,132 176,62 256,62 C336,62 408,132 398,246 C390,206 376,180 356,162 "
                 "C330,140 300,160 276,138 C250,160 220,142 196,160 C166,166 136,196 114,246 Z")
    elif style == 10:   # raspado
        front = ("M122,214 C120,134 178,76 256,76 C334,76 392,134 390,214 C376,170 330,136 256,134 "
                 "C182,136 136,170 122,214 Z")
    return back, front


def svg(o, crop="full"):
    """Desenha o avatar (512x512) com as escolhas `o`; `crop` recorta uma parte."""
    o = dict(DEFAULT, **(o or {}))
    for k, n in OPTIONS.items():
        o[k] = int(o.get(k, 0)) % n
    skin = SKINS[o["skin"]]
    hair = HAIR[o["hairColor"]]
    iris = EYES[o["eyeColor"]]
    shirt = SHIRTS[o["shirt"]]
    bg = BACKGROUNDS[o["background"]]
    lips = mix(shade(skin, 0.78), "#C2485A", 0.45)
    hs = o["hair"]

    p = ['<defs>'
         '<radialGradient id="bg" cx="0.5" cy="0.32" r="0.75"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
         '<radialGradient id="face" cx="0.40" cy="0.34" r="0.78" fx="0.36" fy="0.28"><stop offset="0" stop-color="%s"/>'
         '<stop offset="0.55" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
         '<radialGradient id="ear" cx="0.5" cy="0.5" r="0.6"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
         '<linearGradient id="neck" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
         '<linearGradient id="hair" x1="0.2" y1="0" x2="0.8" y2="1"><stop offset="0" stop-color="%s"/><stop offset="0.6" stop-color="%s"/>'
         '<stop offset="1" stop-color="%s"/></linearGradient>'
         '<radialGradient id="sclera" cx="0.5" cy="0.35" r="0.7"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E4E1EA"/></radialGradient>'
         '<radialGradient id="iris" cx="0.5" cy="0.6" r="0.6"><stop offset="0" stop-color="%s"/><stop offset="0.7" stop-color="%s"/>'
         '<stop offset="1" stop-color="%s"/></radialGradient>'
         '<radialGradient id="blush" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#FF6F7D" stop-opacity="0.34"/>'
         '<stop offset="1" stop-color="#FF6F7D" stop-opacity="0"/></radialGradient>'
         '<linearGradient id="shirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
         '<linearGradient id="lips" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
         '<linearGradient id="lens" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3A3F55" stop-opacity="0.92"/>'
         '<stop offset="1" stop-color="#0E1018" stop-opacity="0.95"/></linearGradient>'
         '</defs>'
         % (shade(bg, 1.35), shade(bg, 0.88),
            shade(skin, 1.18), skin, shade(skin, 0.78),
            shade(skin, 0.95), shade(skin, 0.74),
            shade(skin, 0.66), shade(skin, 0.86),
            shade(hair, 1.32), hair, shade(hair, 0.7),
            shade(iris, 1.45), iris, shade(iris, 0.6),
            shade(shirt, 1.12), shade(shirt, 0.8),
            shade(lips, 1.12), shade(lips, 0.85))]
    p.append('<rect width="512" height="512" fill="url(#bg)"/>')

    back, front = _hair_paths(hs)
    if back:
        p.append('<path d="%s" fill="url(#hair)"/>' % back)

    # roupa, pescoço e sombra do queixo
    p.append('<path d="M60,512 C66,452 150,420 256,420 C362,420 446,452 452,512 Z" fill="url(#shirt)"/>')
    p.append('<path d="M212,380 L212,428 C232,446 280,446 300,428 L300,380 Z" fill="url(#neck)"/>')
    p.append('<path d="M206,426 C226,452 286,452 306,426 C296,444 272,452 256,452 C240,452 216,444 206,426 Z" fill="%s" opacity="0.55"/>'
             % shade(shirt, 0.55))
    # orelhas
    for cx in (120, 392):
        p.append('<ellipse cx="%d" cy="244" rx="24" ry="38" fill="url(#ear)"/>' % cx)
        p.append('<ellipse cx="%d" cy="246" rx="11" ry="20" fill="%s" opacity="0.5"/>' % (cx + (4 if cx < 256 else -4), shade(skin, 0.7)))
    # rosto
    p.append('<path d="%s" fill="url(#face)"/>' % HEAD)
    # luz de contorno na bochecha e sombra suave sob o cabelo
    p.append('<path d="M366,262 C366,316 346,356 314,384 C340,350 356,312 358,262 Z" fill="white" opacity="0.05"/>')
    if hs not in (0, 10):
        p.append('<path d="M140,170 C170,126 342,126 372,170 C340,150 172,150 140,170 Z" fill="%s" opacity="0.25"/>' % shade(skin, 0.6))
    # bochechas
    for cx in (178, 334):
        p.append('<ellipse cx="%d" cy="300" rx="44" ry="30" fill="url(#blush)"/>' % cx)

    # detalhes da pele
    d = o["details"]
    if d == 1:   # sardas
        for x, y in [(168, 282), (184, 292), (160, 298), (196, 280), (344, 282), (328, 292), (352, 298), (316, 280)]:
            p.append('<circle cx="%d" cy="%d" r="3.2" fill="%s" opacity="0.55"/>' % (x, y, shade(skin, 0.55)))
    elif d == 2:  # pinta
        p.append('<circle cx="330" cy="334" r="5" fill="%s"/>' % shade(skin, 0.42))

    # barba (antes da boca)
    bd = o["beard"]
    if bd == 1:   # por fazer
        p.append('<path d="M142,300 C150,380 210,410 256,410 C302,410 362,380 370,300 C350,360 310,372 256,372 C202,372 162,360 142,300 Z" fill="%s" opacity="0.35"/>' % hair)
    elif bd == 3:  # cavanhaque
        p.append('<path d="M222,360 C226,392 240,406 256,406 C272,406 286,392 290,360 C278,372 234,372 222,360 Z" fill="url(#hair)"/>')
    elif bd == 4:  # barba cheia
        p.append('<path d="M126,262 C126,380 196,418 256,418 C316,418 386,380 386,262 C374,330 346,350 318,354 '
                 'C300,330 212,330 194,354 C166,350 138,330 126,262 Z" fill="url(#hair)"/>')

    # nariz
    n = o["nose"]
    nose_c = shade(skin, 0.72)
    if n == 0:   # redondinho
        p.append('<ellipse cx="256" cy="292" rx="18" ry="13" fill="%s" opacity="0.35"/>' % nose_c)
        p.append('<ellipse cx="252" cy="284" rx="9" ry="6" fill="white" opacity="0.30"/>')
        p.append('<ellipse cx="246" cy="298" rx="4" ry="3" fill="%s" opacity="0.6"/><ellipse cx="266" cy="298" rx="4" ry="3" fill="%s" opacity="0.6"/>'
                 % (shade(skin, 0.5), shade(skin, 0.5)))
    elif n == 1:  # fino
        p.append('<path d="M258,252 C254,272 246,288 248,298 C252,304 262,304 268,298" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round" opacity="0.7"/>' % nose_c)
    else:         # largo
        p.append('<path d="M232,300 C236,284 246,280 256,280 C266,280 276,284 280,300 C270,308 242,308 232,300 Z" fill="%s" opacity="0.45"/>' % nose_c)
        p.append('<ellipse cx="256" cy="286" rx="10" ry="6" fill="white" opacity="0.28"/>')

    # boca
    m = o["mouth"]
    inner = "#4A1A22"
    if m == 0:    # sorriso
        p.append('<path d="M220,334 C236,356 276,356 292,334 C276,346 236,346 220,334 Z" fill="url(#lips)"/>')
        p.append('<path d="M218,332 C236,358 276,358 294,332" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % shade(lips, 0.7))
    elif m == 1:  # sorrisão
        p.append('<path d="M208,326 C224,384 288,384 304,326 C280,334 232,334 208,326 Z" fill="%s"/>' % inner)
        p.append('<path d="M216,330 C236,336 276,336 296,330 L292,344 C270,350 242,350 220,344 Z" fill="white"/>')
        p.append('<ellipse cx="256" cy="362" rx="22" ry="10" fill="#E86C7E"/>')
        p.append('<path d="M206,324 C224,388 288,388 306,324" fill="none" stroke="url(#lips)" stroke-width="6" stroke-linecap="round"/>')
    elif m == 2:  # neutro
        p.append('<path d="M228,340 C244,346 268,346 284,340" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % lips)
    elif m == 3:  # surpreso
        p.append('<ellipse cx="256" cy="346" rx="20" ry="24" fill="%s"/>' % inner)
        p.append('<ellipse cx="256" cy="360" rx="12" ry="7" fill="#E86C7E"/>')
        p.append('<ellipse cx="256" cy="346" rx="20" ry="24" fill="none" stroke="url(#lips)" stroke-width="6"/>')
    elif m == 4:  # de lado
        p.append('<path d="M226,344 C246,348 270,342 292,326" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % shade(lips, 0.85))
        p.append('<path d="M292,326 q6,-2 8,-8" fill="none" stroke="%s" stroke-width="5" stroke-linecap="round" opacity="0.7"/>' % shade(lips, 0.7))
    else:         # gargalhada
        p.append('<path d="M204,322 C214,402 298,402 308,322 Z" fill="%s"/>' % inner)
        p.append('<path d="M212,324 L300,324 L296,342 C270,348 242,348 216,342 Z" fill="white"/>')
        p.append('<path d="M226,376 C240,362 272,362 286,376 C272,390 240,390 226,376 Z" fill="#E86C7E"/>')

    if bd == 2 or bd == 4:   # bigode
        p.append('<path d="M206,328 C220,306 246,308 256,318 C266,308 292,306 306,328 C290,320 272,322 256,328 C240,322 222,320 206,328 Z" fill="url(#hair)"/>')

    # olhos
    e = o["eyes"]
    for i, x in enumerate(EYE_X):
        if e == 2:
            p.append(_eye_closed(x, happy=True))
        elif e == 3 and i == 1:
            p.append(_eye_closed(x, happy=False))
        else:
            p.append(_eye_open(x, o, iris, sleepy=(e == 4), big=(e == 1)))

    # sobrancelhas (preenchidas e afiladas)
    b = o["brows"]
    brow = shade(hair, 0.8) if o["hairColor"] not in (6, 7) else shade(hair, 0.55)
    shapes = {
        0: (-50, -60, 9),   # natural: altura início, pico, espessura
        1: (-48, -58, 14),  # grossas
        2: (-46, -70, 8),   # arqueadas
        3: (-54, -56, 10),  # retas
        4: (-50, -60, 5),   # finas
    }
    y0, peak, th = shapes[b]
    for x in EYE_X:
        s = -1 if x < 256 else 1
        inner_x, outer_x = x - s * 30, x + s * 38
        p.append('<path d="M%d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d Z" fill="%s"/>'
                 % (inner_x, EYE_Y + y0 + th / 2, inner_x + s * 14, EYE_Y + peak, outer_x - s * 20, EYE_Y + peak - 4,
                    outer_x, EYE_Y + y0 + 4, outer_x - s * 20, EYE_Y + peak + th * 0.8, inner_x + s * 12, EYE_Y + peak + th,
                    inner_x, EYE_Y + y0 + th / 2 + th, brow))

    # cabelo da frente (com mechas de luz)
    if hs == 4:   # cacheado: cachos sobrepostos
        for cx, cy, r in [(146, 198, 40), (170, 140, 44), (222, 104, 46), (290, 100, 46), (346, 134, 44), (370, 192, 40), (256, 128, 40)]:
            p.append('<circle cx="%d" cy="%d" r="%d" fill="url(#hair)"/>' % (cx, cy, r))
            p.append('<path d="M%d,%d a%d,%d 0 0 1 %d,%d" fill="none" stroke="white" stroke-width="4" opacity="0.18"/>'
                     % (cx - r * 0.5, cy - r * 0.3, r * 0.6, r * 0.6, r * 0.6, -r * 0.3))
    elif front:
        p.append('<path d="%s" fill="url(#hair)"/>' % front)
        if hs != 10:
            p.append('<path d="M196,92 C228,78 284,78 318,92" fill="none" stroke="white" stroke-width="8" stroke-linecap="round" opacity="0.16"/>')
            p.append('<path d="M168,122 C178,108 192,100 206,96" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" opacity="0.12"/>')
        else:
            p.append('<path d="%s" fill="%s" opacity="0.25"/>' % (front, skin))

    # brincos (detalhe 3)
    if d == 3:
        for cx in (116, 396):
            p.append('<circle cx="%d" cy="284" r="7" fill="#E9C46A"/><circle cx="%d" cy="282" r="2.5" fill="white" opacity="0.8"/>' % (cx, cx - 2))

    # óculos
    g = o["glasses"]
    if g in (1, 4):
        lens = 'fill="url(#lens)"' if g == 4 else 'fill="white" fill-opacity="0.08"'
        frame = "#20232B" if g == 4 else "#8A6A3A"
        for x in EYE_X:
            p.append('<circle cx="%d" cy="%d" r="44" %s stroke="%s" stroke-width="%d"/>' % (x, EYE_Y, lens, frame, 7 if g == 4 else 5))
            if g == 4:
                p.append('<path d="M%d,%d q14,-12 30,-10" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" opacity="0.35"/>' % (x - 26, EYE_Y - 16))
        p.append('<path d="M244,232 C250,224 262,224 268,232" fill="none" stroke="%s" stroke-width="5"/>' % frame)
    elif g == 2:   # quadrado grosso
        for x in EYE_X:
            p.append('<rect x="%d" y="%d" width="92" height="66" rx="16" fill="white" fill-opacity="0.08" stroke="#1C1C1E" stroke-width="9"/>' % (x - 46, EYE_Y - 34))
        p.append('<path d="M248,232 L264,232" stroke="#1C1C1E" stroke-width="8"/>')
    elif g == 3:   # gatinho
        for x in EYE_X:
            s = -1 if x < 256 else 1
            p.append('<path d="M%d,%d C%d,%d %d,%d %d,%d C%d,%d %d,%d %d,%d Z" fill="white" fill-opacity="0.08" stroke="#B0304A" stroke-width="7" stroke-linejoin="round"/>'
                     % (x - s * 40, EYE_Y - 8, x - s * 30, EYE_Y - 40, x + s * 30, EYE_Y - 44, x + s * 52, EYE_Y - 36,
                        x + s * 44, EYE_Y + 10, x + s * 10, EYE_Y + 34, x - s * 40, EYE_Y - 8))
        p.append('<path d="M246,228 C252,222 260,222 266,228" fill="none" stroke="#B0304A" stroke-width="6"/>')
    if g:
        for x in (118, 394):   # hastes até as orelhas
            p.append('<path d="M%d,%d L%d,%d" stroke="#20232B" stroke-width="5" opacity="0.6"/>'
                     % (x, 236, x + (40 if x < 256 else -40), 230))

    # chapéus e acessórios de cabeça
    hw = o["headwear"]
    if hw == 1:   # gorro
        p.append('<path d="M110,190 C110,60 402,60 402,190 Z" fill="#3C6FD8"/>')
        p.append('<rect x="100" y="172" width="312" height="48" rx="24" fill="#2D56AE"/>')
        for x in range(130, 400, 26):
            p.append('<path d="M%d,180 L%d,212" stroke="white" stroke-width="4" opacity="0.18"/>' % (x, x))
        p.append('<circle cx="256" cy="64" r="30" fill="#F2F2F7"/>')
    elif hw == 2:  # boné
        p.append('<path d="M118,196 C118,76 394,76 394,196 C320,176 192,176 118,196 Z" fill="#E5484D"/>')
        p.append('<path d="M120,196 C190,176 322,176 392,196 C380,218 132,218 120,196 Z" fill="#B8323A"/>')
        p.append('<circle cx="256" cy="86" r="9" fill="#B8323A"/>')
    elif hw == 3:  # fone de ouvido
        p.append('<path d="M108,240 C100,90 412,90 404,240" fill="none" stroke="#2C2C30" stroke-width="16" stroke-linecap="round"/>')
        for cx in (108, 404):
            p.append('<rect x="%d" y="206" width="40" height="80" rx="18" fill="#3A3A40"/>' % (cx - 20))
            p.append('<rect x="%d" y="214" width="12" height="64" rx="6" fill="#5A5A62"/>' % (cx - 6))
    elif hw == 4:  # tiara de flores
        p.append('<path d="M132,190 C170,120 342,120 380,190" fill="none" stroke="#3E8E5A" stroke-width="7" stroke-linecap="round"/>')
        for cx, cy, col in [(150, 168, "#FF8FAB"), (190, 136, "#FFD166"), (232, 122, "#FF8FAB"), (280, 122, "#FFFFFF"),
                            (322, 136, "#FFD166"), (362, 168, "#FF8FAB")]:
            for a in range(5):
                ang = a * 2 * math.pi / 5
                p.append('<circle cx="%.1f" cy="%.1f" r="8" fill="%s"/>' % (cx + 9 * math.cos(ang), cy + 9 * math.sin(ang), col))
            p.append('<circle cx="%d" cy="%d" r="5" fill="#E07A1F"/>' % (cx, cy))

    x, y, w, h = CROPS.get(crop, CROPS["full"])
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="%d %d %d %d">%s</svg>'
            % (x, y, w, h, "".join(p)))


def render(o, size=512, crop="full", round_=True):
    """Desenha em QImage. A forma redonda é recortada pelo QPainter (o QtSvg ignora clipPath)."""
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg(o, crop).encode()))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    if round_:
        path = QPainterPath()
        path.addEllipse(QRectF(0, 0, size, size))
        painter.setClipPath(path)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return image


def load():
    try:
        with open(CONFIG, encoding="utf-8") as fh:
            data = json.load(fh)
        return {k: int(data.get(k, v)) % OPTIONS[k] for k, v in DEFAULT.items()}
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT)


def save(o):
    """Salva as escolhas e aplica o avatar como foto do usuário."""
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    with open(CONFIG, "w", encoding="utf-8") as fh:
        json.dump(o, fh)
    face = os.path.expanduser("~/.face.icon")
    render(o).save(face, "PNG")
    try:   # ~/.face (link) também é lido por alguns programas
        if os.path.lexists(os.path.expanduser("~/.face")):
            os.remove(os.path.expanduser("~/.face"))
        os.symlink(".face.icon", os.path.expanduser("~/.face"))
    except OSError:
        pass
    # AccountsService: a tela de login (SDDM) e as Configurações usam esta foto
    try:
        uid = os.getuid()
        subprocess.run(["busctl", "call", "org.freedesktop.Accounts", "/org/freedesktop/Accounts/User%d" % uid,
                        "org.freedesktop.Accounts.User", "SetIconFile", "s", face],
                       capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        pass
    return face


class AvatarProvider(QQuickImageProvider):
    """image://avatar/<recorte>/<json> — renderizado fora da interface e guardado em cache,
    para o editor não travar enquanto as miniaturas aparecem."""

    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image,
                         QQmlImageProviderBase.Flag.ForceAsynchronousImageLoading)
        self._cache = OrderedDict()
        self._lock = Lock()

    def requestImage(self, image_id, requested_size):
        from urllib.parse import unquote
        crop, _sep, payload = unquote(image_id).partition("/")
        size = requested_size.width() if requested_size and requested_size.width() > 0 else 512
        key = (crop, payload, size)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                image = self._cache[key]
                return image, QSize(size, size)
        try:
            o = json.loads(payload)
        except ValueError:
            o = {}
        crop = crop if crop in CROPS else "full"
        image = render(o, size, crop, round_=(crop == "full"))
        with self._lock:
            self._cache[key] = image
            while len(self._cache) > 400:
                self._cache.popitem(last=False)
        return image, QSize(size, size)


class AvatarBridge(QObject):
    changed = pyqtSignal()
    saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._o = load()

    @pyqtProperty("QVariantMap", notify=changed)
    def choice(self):
        return self._o

    @pyqtProperty(str, notify=changed)
    def key(self):
        return json.dumps(self._o, sort_keys=True)

    @pyqtProperty("QVariantList", constant=True)
    def tabs(self):
        out = []
        for tab_id, label, sections in TABS:
            secs = []
            for part, kind, crop in sections:
                item = {"part": part, "kind": kind, "crop": crop or "full", "count": OPTIONS[part],
                        "label": _(SECTION_LABELS[part])}
                if kind == "color":
                    item["colors"] = COLORS[part]
                secs.append(item)
            out.append({"id": tab_id, "label": _(label), "sections": secs})
        return out

    @pyqtSlot(str, int)
    def set(self, part, value):
        self._o = dict(self._o, **{part: int(value) % OPTIONS[part]})
        self.changed.emit()

    @pyqtSlot(str, int, result=str)
    def variant(self, part, value):
        """Escolhas atuais com uma única troca (para as miniaturas das opções)."""
        return json.dumps(dict(self._o, **{part: value}), sort_keys=True)

    @pyqtSlot()
    def randomize(self):
        import random
        o = {k: random.randrange(n) for k, n in OPTIONS.items()}
        # combinações mais naturais: poucos acessórios de uma vez
        if random.random() < 0.6:
            o["headwear"] = 0
        if random.random() < 0.5:
            o["glasses"] = 0
        if random.random() < 0.6:
            o["beard"] = 0
        o["eyes"] = random.choice([0, 0, 1, 2, 4])
        self._o = o
        self.changed.emit()

    @pyqtSlot()
    def save(self):
        save(self._o)
        self.saved.emit()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-avatar")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    parser.add_argument("--tab", default="skin", help=argparse.SUPPRESS)
    parser.add_argument("--export", help="salva o avatar atual neste arquivo PNG e sai")
    parser.add_argument("--gallery", help=argparse.SUPPRESS)   # PNG com vários avatares (testes)
    args = parser.parse_args(argv)
    if args.export or args.gallery:
        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication(sys.argv)  # noqa: F841
        if args.export:
            render(load()).save(args.export, "PNG")
        else:
            import random
            random.seed(7)
            sheet = QImage(4 * 260, 3 * 260, QImage.Format.Format_ARGB32_Premultiplied)
            sheet.fill(Qt.GlobalColor.white)
            painter = QPainter(sheet)
            bridge = AvatarBridge()
            for i in range(12):
                bridge.randomize()
                painter.drawImage(QRectF((i % 4) * 260 + 5, (i // 4) * 260 + 5, 250, 250), render(bridge.choice, 500))
            painter.end()
            sheet.save(args.gallery, "PNG")
        return 0
    from .qmlapp import run
    bridge = AvatarBridge()
    return run("konaro-avatar", _("My Avatar"), "avatar/Main.qml",
               context={"avatar": bridge, "startTab": args.tab},
               screenshot=args.screenshot, size=(1000, 660), providers={"avatar": AvatarProvider()})


if __name__ == "__main__":
    sys.exit(main())
