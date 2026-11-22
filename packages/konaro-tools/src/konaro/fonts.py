"""Fonte do sistema — escolhida na instalação (Calamares) e nas Boas-vindas.

Todas são livres e vêm do Debian. A padrão é a Inter, de desenho muito próximo da
fonte do macOS (a fonte da Apple não pode ser redistribuída).
"""

import os
import re
import subprocess

DEFAULT = "inter"
FONTS = [
    {"id": "inter", "family": "Inter", "name": "Inter",
     "description": "Clean and modern, very close to the macOS system font. Recommended."},
    {"id": "noto", "family": "Noto Sans", "name": "Noto Sans",
     "description": "Friendly and very readable, KDE's standard font. Covers almost every language."},
    {"id": "manrope", "family": "Manrope", "name": "Manrope",
     "description": "Geometric and contemporary, with a touch of personality."},
    {"id": "roboto", "family": "Roboto", "name": "Roboto",
     "description": "Familiar from Android and many websites; compact and neutral."},
]
KEYS = {"font": 10, "menuFont": 10, "toolBarFont": 10, "smallestReadableFont": 8}


def by_id(font_id):
    return next((f for f in FONTS if f["id"] == font_id), None)


def _font_value(family, size):
    # formato do Qt usado pelo KDE: família,tamanho
    return "%s,%d" % (family, size)


def apply_user(font_id):
    """Aplica a fonte para o usuário atual (kdeglobals) — vale para os apps novos."""
    font = by_id(font_id)
    if font is None:
        return False
    ok = True
    for key, size in KEYS.items():
        try:
            subprocess.run(["kwriteconfig6", "--file", "kdeglobals", "--group", "General", "--key", key,
                            _font_value(font["family"], size)], check=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            ok = False
    # avisa os apps abertos (KDE) que as configurações mudaram
    subprocess.run(["dbus-send", "--session", "--type=signal", "/KGlobalSettings",
                    "org.kde.KGlobalSettings.notifyChange", "int32:0", "int32:0"],
                   capture_output=True, timeout=10)
    return ok


def apply_system(root, font_id):
    """Grava a fonte como padrão do sistema instalado (todos os usuários e a tela de login)."""
    font = by_id(font_id) or by_id(DEFAULT)
    kdeglobals = os.path.join(root, "etc/xdg/kdeglobals")
    if os.path.exists(kdeglobals):
        with open(kdeglobals, encoding="utf-8") as fh:
            text = fh.read()
        for key, size in KEYS.items():
            text = re.sub(r"(?m)^%s=.*$" % key, "%s=%s" % (key, _font_value(font["family"], size)), text)
        with open(kdeglobals, "w", encoding="utf-8") as fh:
            fh.write(text)
    sddm = os.path.join(root, "etc/sddm.conf.d/10-konaro.conf")
    if os.path.exists(sddm):
        with open(sddm, encoding="utf-8") as fh:
            text = fh.read()
        text = re.sub(r"(?m)^Font=.*$", "Font=%s" % _font_value(font["family"], 10), text)
        with open(sddm, "w", encoding="utf-8") as fh:
            fh.write(text)
    return font["id"]


def current_user():
    """Id da fonte atual do usuário (ou a padrão)."""
    try:
        out = subprocess.run(["kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "font"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    family = out.split(",")[0] if out else ""
    return next((f["id"] for f in FONTS if f["family"] == family), DEFAULT)
