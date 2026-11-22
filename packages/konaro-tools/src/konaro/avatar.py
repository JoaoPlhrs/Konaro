"""Avatares do Konaro — crie um rostinho personalizado para o seu perfil.

Arte original do projeto, desenhada em SVG a partir das escolhas da pessoa (pele,
cabelo, olhos, sobrancelhas, boca, barba, óculos, chapéu e fundo). O resultado vira
a foto do usuário: tela de login, Iniciar e Configurações (AccountsService e
~/.face.icon). Tudo fica no computador; nada é enviado a lugar nenhum.
"""

import argparse
import json
import os
import subprocess
import sys

from PyQt6.QtCore import QByteArray, QObject, QRectF, QSize, Qt, pyqtProperty, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtQuick import QQuickImageProvider
from PyQt6.QtSvg import QSvgRenderer

from .i18n import _

CONFIG = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "konaro", "avatar.json")

SKINS = ["#FFDFC4", "#F0C8A0", "#E0AC69", "#C68642", "#8D5524", "#5C3A21"]
HAIR_COLORS = ["#2B1D14", "#5A3825", "#A0522D", "#D9A066", "#E8E2D0", "#C0392B", "#6C5CE7"]
BACKGROUNDS = ["#FFD6A5", "#CAFFBF", "#9BF6FF", "#BDB2FF", "#FFC6FF", "#E5E5EA", "#FDFFB6"]

OPTIONS = {
    "skin": len(SKINS),
    "hair": 8,            # 0 careca, 1 curto, 2 topete, 3 cacheado, 4 longo, 5 coque, 6 black power, 7 franja
    "hairColor": len(HAIR_COLORS),
    "eyes": 4,            # 0 redondos, 1 sorrindo, 2 piscando, 3 grandes
    "brows": 3,           # 0 finas, 1 grossas, 2 arqueadas
    "mouth": 5,           # 0 sorriso, 1 sorrisão, 2 neutro, 3 surpreso, 4 língua
    "beard": 4,           # 0 nenhuma, 1 bigode, 2 barba curta, 3 barba cheia
    "glasses": 4,         # 0 nenhum, 1 redondo, 2 quadrado, 3 de sol
    "hat": 4,             # 0 nenhum, 1 gorro, 2 boné, 3 laço
    "background": len(BACKGROUNDS),
}
DEFAULT = {"skin": 1, "hair": 1, "hairColor": 1, "eyes": 0, "brows": 0, "mouth": 0,
           "beard": 0, "glasses": 0, "hat": 0, "background": 2}

LABELS = {
    "skin": "Skin", "hair": "Hair", "hairColor": "Hair color", "eyes": "Eyes", "brows": "Eyebrows",
    "mouth": "Mouth", "beard": "Beard", "glasses": "Glasses", "hat": "Hat", "background": "Background",
}


def _shade(hex_color, factor):
    c = hex_color.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    f = lambda v: max(0, min(255, int(v * factor)))
    return "#%02X%02X%02X" % (f(r), f(g), f(b))


def svg(o):
    """Desenha o avatar (512x512). `o` = dicionário de escolhas."""
    o = dict(DEFAULT, **(o or {}))
    skin = SKINS[o["skin"] % len(SKINS)]
    hair = HAIR_COLORS[o["hairColor"] % len(HAIR_COLORS)]
    bg = BACKGROUNDS[o["background"] % len(BACKGROUNDS)]
    dark = _shade(skin, 0.82)
    p = []
    p.append('<defs>'
             '<radialGradient id="face" cx="0.42" cy="0.36" r="0.75"><stop offset="0" stop-color="%s"/>'
             '<stop offset="0.75" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>'
             '<radialGradient id="bg" cx="0.5" cy="0.35" r="0.8"><stop offset="0" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s"/></radialGradient>'
             '<linearGradient id="hair" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/>'
             '<stop offset="1" stop-color="%s"/></linearGradient>'
             '</defs>' % (_shade(skin, 1.06), skin, dark, _shade(bg, 1.05), _shade(bg, 0.86), _shade(hair, 1.25), hair))
    p.append('<circle cx="256" cy="256" r="256" fill="url(#bg)"/>')
    # cabelo de trás (longo / coque / black power)
    h = o["hair"] % OPTIONS["hair"]
    if h == 4:
        p.append('<path d="M120,230 C110,380 150,470 256,470 C362,470 402,380 392,230 Z" fill="url(#hair)"/>')
    if h == 6:
        p.append('<circle cx="256" cy="200" r="175" fill="url(#hair)"/>')
    if h == 5:
        p.append('<circle cx="256" cy="72" r="52" fill="url(#hair)"/>')
    # pescoço e ombros
    p.append('<path d="M206,380 L206,430 C206,450 306,450 306,430 L306,380 Z" fill="%s"/>' % dark)
    p.append('<path d="M86,512 C96,440 170,415 256,415 C342,415 416,440 426,512 Z" fill="%s"/>' % _shade(bg, 0.55))
    # orelhas e rosto
    p.append('<ellipse cx="136" cy="262" rx="26" ry="36" fill="%s"/><ellipse cx="376" cy="262" rx="26" ry="36" fill="%s"/>' % (dark, dark))
    p.append('<ellipse cx="256" cy="250" rx="122" ry="146" fill="url(#face)"/>')
    # bochechas
    p.append('<ellipse cx="186" cy="300" rx="24" ry="14" fill="#FF7A7A" opacity="0.22"/>'
             '<ellipse cx="326" cy="300" rx="24" ry="14" fill="#FF7A7A" opacity="0.22"/>')
    # cabelo da frente
    front = {
        1: '<path d="M134,220 C130,130 190,96 256,96 C330,96 384,130 378,222 C350,170 300,150 256,152 C210,152 160,172 134,220 Z" fill="url(#hair)"/>',
        2: '<path d="M134,222 C126,120 200,80 270,86 C340,92 392,140 378,224 C360,180 330,150 300,140 C320,120 260,110 230,130 C190,140 150,180 134,222 Z" fill="url(#hair)"/>',
        3: '<g fill="url(#hair)">' + "".join('<circle cx="%d" cy="%d" r="34"/>' % (x, y) for x, y in
                                              [(150, 200), (180, 150), (226, 120), (280, 116), (330, 140), (366, 190), (256, 140)]) + '</g>',
        4: '<path d="M130,250 C120,130 190,92 256,92 C326,92 396,130 382,250 C370,190 330,150 256,148 C186,150 140,190 130,250 Z" fill="url(#hair)"/>',
        5: '<path d="M136,215 C134,135 192,104 256,104 C322,104 380,136 376,216 C346,168 300,154 256,154 C212,154 166,168 136,215 Z" fill="url(#hair)"/>',
        6: '<path d="M140,205 C150,150 200,130 256,130 C312,130 362,150 372,205 C340,180 300,172 256,172 C212,172 172,180 140,205 Z" fill="%s"/>' % _shade(hair, 0.9),
        7: '<path d="M132,230 C126,128 196,92 258,92 C326,92 388,128 380,230 C372,206 360,190 340,186 L332,206 L300,180 L286,206 L254,182 L236,208 L206,184 L190,210 L168,190 C150,196 138,210 132,230 Z" fill="url(#hair)"/>',
    }
    if h in front:
        p.append(front[h])
    # sobrancelhas
    b = o["brows"] % OPTIONS["brows"]
    bw = [5, 10, 6][b]
    by = [196, 196, 190][b]
    curve = [-6, -4, -14][b]
    for x in (206, 306):
        p.append('<path d="M%d,%d q26,%d 52,0" stroke="%s" stroke-width="%d" fill="none" stroke-linecap="round"/>'
                 % (x - 26, by, curve, _shade(hair, 0.8), bw))
    # olhos
    e = o["eyes"] % OPTIONS["eyes"]
    for i, x in enumerate((206, 306)):
        if e == 1 or (e == 2 and i == 1):
            p.append('<path d="M%d,236 q20,-18 40,0" stroke="#2B2B2B" stroke-width="7" fill="none" stroke-linecap="round"/>' % (x - 20))
        else:
            r = 22 if e == 3 else 17
            p.append('<ellipse cx="%d" cy="236" rx="%d" ry="%d" fill="white"/>' % (x, r, r + 3))
            p.append('<circle cx="%d" cy="239" r="%d" fill="#3B2A1E"/>' % (x, r - 6))
            p.append('<circle cx="%d" cy="233" r="%d" fill="white"/>' % (x + 4, max(3, r // 4)))
    # nariz
    p.append('<path d="M256,250 q-10,30 0,40 q8,2 14,-4" stroke="%s" stroke-width="6" fill="none" stroke-linecap="round"/>' % _shade(skin, 0.7))
    # barba e bigode
    bd = o["beard"] % OPTIONS["beard"]
    if bd == 2:
        p.append('<path d="M152,300 C160,380 210,400 256,400 C302,400 352,380 360,300 C340,350 300,362 256,362 C212,362 172,350 152,300 Z" fill="%s" opacity="0.85"/>' % hair)
    if bd == 3:
        p.append('<path d="M140,270 C140,390 200,420 256,420 C312,420 372,390 372,270 C356,340 320,360 256,360 C192,360 156,340 140,270 Z" fill="url(#hair)"/>')
    # boca
    m = o["mouth"] % OPTIONS["mouth"]
    mouths = {
        0: '<path d="M222,326 q34,28 68,0" stroke="#7A2E2E" stroke-width="8" fill="none" stroke-linecap="round"/>',
        1: '<path d="M214,318 q42,56 84,0 Z" fill="#7A2E2E"/><path d="M226,322 q30,10 60,0 l-4,10 q-26,8 -52,0 Z" fill="white"/>',
        2: '<path d="M226,332 h60" stroke="#7A2E2E" stroke-width="8" stroke-linecap="round"/>',
        3: '<ellipse cx="256" cy="334" rx="18" ry="22" fill="#7A2E2E"/>',
        4: '<path d="M214,318 q42,56 84,0 Z" fill="#7A2E2E"/><ellipse cx="262" cy="344" rx="18" ry="14" fill="#FF6B81"/>',
    }
    p.append(mouths[m])
    if bd == 1 or bd == 3:
        p.append('<path d="M206,312 C226,290 250,300 256,306 C262,300 286,290 306,312 C286,306 270,312 256,316 C242,312 226,306 206,312 Z" fill="%s"/>' % hair)
    # óculos
    g = o["glasses"] % OPTIONS["glasses"]
    if g in (1, 3):
        fill = 'fill="#1D1D1F" fill-opacity="0.85"' if g == 3 else 'fill="white" fill-opacity="0.12"'
        for x in (206, 306):
            p.append('<circle cx="%d" cy="238" r="36" %s stroke="#1D1D1F" stroke-width="7"/>' % (x, fill))
        p.append('<path d="M242,236 q14,-10 28,0" stroke="#1D1D1F" stroke-width="7" fill="none"/>')
    if g == 2:
        for x in (206, 306):
            p.append('<rect x="%d" y="208" width="76" height="58" rx="12" fill="white" fill-opacity="0.12" stroke="#1D1D1F" stroke-width="7"/>' % (x - 38))
        p.append('<path d="M244,232 h24" stroke="#1D1D1F" stroke-width="7"/>')
    # chapéu
    hat = o["hat"] % OPTIONS["hat"]
    if hat == 1:
        p.append('<path d="M128,200 C128,90 384,90 384,200 Z" fill="#E5484D"/><rect x="118" y="184" width="276" height="40" rx="20" fill="#F2F2F7"/>'
                 '<circle cx="256" cy="92" r="26" fill="#F2F2F7"/>')
    if hat == 2:
        p.append('<path d="M134,196 C134,96 378,96 378,196 Z" fill="#0A84FF"/><path d="M300,190 C350,186 410,196 424,214 C380,214 330,206 300,204 Z" fill="#0A6AD6"/>')
    if hat == 3:
        p.append('<g fill="#FF4F8B"><path d="M256,118 L206,92 L210,148 Z"/><path d="M256,118 L306,92 L302,148 Z"/><circle cx="256" cy="120" r="14"/></g>')
    defs, body = p[0], "".join(p[1:])
    defs = defs.replace("</defs>", '<clipPath id="round"><circle cx="256" cy="256" r="256"/></clipPath></defs>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">%s'
            '<g clip-path="url(#round)">%s</g></svg>' % (defs, body))


def render(o, size=512):
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg(o).encode()))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return image


def load():
    try:
        with open(CONFIG, encoding="utf-8") as fh:
            return dict(DEFAULT, **json.load(fh))
    except (OSError, ValueError):
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
    """image://avatar/<json> — prévia ao vivo das escolhas."""

    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)

    def requestImage(self, image_id, requested_size):
        try:
            o = json.loads(image_id.split("#", 1)[0])
        except ValueError:
            o = {}
        size = requested_size.width() if requested_size and requested_size.width() > 0 else 512
        image = render(o, size)
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
    def parts(self):
        return [{"id": k, "label": _(LABELS[k]), "count": n} for k, n in OPTIONS.items()]

    @pyqtSlot(str, int)
    def set(self, part, value):
        self._o = dict(self._o, **{part: int(value) % OPTIONS[part]})
        self.changed.emit()

    @pyqtSlot(str, int, result=str)
    def variant(self, part, value):
        """Chave de prévia do avatar com uma única troca (miniaturas das opções)."""
        return json.dumps(dict(self._o, **{part: value}), sort_keys=True)

    @pyqtSlot()
    def randomize(self):
        import random
        self._o = {k: random.randrange(n) for k, n in OPTIONS.items()}
        self.changed.emit()

    @pyqtSlot()
    def save(self):
        save(self._o)
        self.saved.emit()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-avatar")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    parser.add_argument("--export", help="salva o avatar atual neste arquivo PNG e sai")
    args = parser.parse_args(argv)
    from .qmlapp import run
    if args.export:
        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication(sys.argv)  # noqa: F841
        render(load()).save(args.export, "PNG")
        return 0
    bridge = AvatarBridge()
    return run("konaro-avatar", _("My Avatar"), "avatar/Main.qml", context={"avatar": bridge},
               screenshot=args.screenshot, size=(920, 640), providers={"avatar": AvatarProvider()})


if __name__ == "__main__":
    sys.exit(main())
