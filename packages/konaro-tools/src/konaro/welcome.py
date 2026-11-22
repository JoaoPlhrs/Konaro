"""Boas-vindas do Konaro — experiência guiada de primeiro uso (interface em QML).

Abre automaticamente no primeiro login de cada usuário (autostart) e pode ser
aberta de novo pelo menu. Na sessão live, mostra também o botão de instalar.
Não exige conta nem conecta serviços externos.
"""

import argparse
import os
import subprocess
import sys

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import desktopwidgets, fonts, i18n
from .i18n import _
from .launcher import launch

CONFIG_DIR = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "konaro")
DONE_FILE = os.path.join(CONFIG_DIR, "welcome-done")
LNF = "/usr/share/plasma/look-and-feel/%s/contents/previews/preview.png"
CHANGEICONS = "/usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons"


def is_live():
    try:
        with open("/proc/cmdline", encoding="utf-8") as fh:
            return "boot=live" in fh.read()
    except OSError:
        return False


def _run(*cmd):
    try:
        return subprocess.run(list(cmd), capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def online():
    return _run("nmcli", "-t", "networking", "connectivity") == "full"


def apply_theme(dark):
    """Troca claro/escuro SEM reaplicar o layout da área de trabalho.

    `plasma-apply-lookandfeel` também reaplica o layout (painéis/dock) e o usuário
    perderia os atalhos fixados; por isso aplicamos as partes separadamente.
    O papel de parede Konaro troca sozinho (images_dark) com o esquema escuro.
    """
    _run("plasma-apply-colorscheme", "KonaroDark" if dark else "KonaroLight")
    _run("plasma-apply-desktoptheme", "konaro")
    _run(CHANGEICONS, "breeze-dark" if dark else "breeze")
    _run("kwriteconfig6", "--file", "kdeglobals", "--group", "KDE", "--key", "LookAndFeelPackage",
         "org.konaro.desktop.dark" if dark else "org.konaro.desktop")
    _run("kwriteconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "theme",
         "__aurorae__svg__KonaroDark" if dark else "__aurorae__svg__Konaro")
    _run("qdbus6", "org.kde.KWin", "/KWin", "reconfigure")


def current_is_dark():
    return _run("kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "ColorScheme") == "KonaroDark"


def set_reduced_animations(reduced):
    _run("kwriteconfig6", "--file", "kdeglobals", "--group", "KDE", "--key", "AnimationDurationFactor",
         "0" if reduced else "1")
    _run("qdbus6", "org.kde.KWin", "/KWin", "reconfigure")


def set_system_language(lang):
    value = "pt_BR:en_US" if lang == "pt" else "en_US"
    _run("kwriteconfig6", "--file", "plasma-localerc", "--group", "Translations", "--key", "LANGUAGE", value)


def set_feedback(enabled):
    _run("kwriteconfig6", "--file", "PlasmaUserFeedback", "--group", "Global", "--key", "FeedbackLevel",
         "16" if enabled else "0")


def mark_done(done):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if done:
        open(DONE_FILE, "w").close()
    elif os.path.exists(DONE_FILE):
        os.remove(DONE_FILE)


class WelcomeBridge(QObject):
    langChanged = pyqtSignal()
    widgetsChanged = pyqtSignal()
    onlineChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._widgets = desktopwidgets.current()
        self._online = online()

    @pyqtProperty(str, notify=langChanged)
    def lang(self):
        return i18n.LANG

    @pyqtProperty(bool, constant=True)
    def live(self):
        return is_live()

    @pyqtProperty(bool, constant=True)
    def dark(self):
        return current_is_dark()

    @pyqtProperty(str, constant=True)
    def lightPreview(self):
        return LNF % "org.konaro.desktop"

    @pyqtProperty(str, constant=True)
    def darkPreview(self):
        return LNF % "org.konaro.desktop.dark"

    @pyqtProperty(bool, notify=onlineChanged)
    def online(self):
        return self._online

    @pyqtProperty("QVariantList", notify=widgetsChanged)
    def widgets(self):
        result = []
        for w in desktopwidgets.WIDGETS:
            enabled = self._widgets.get(w["id"], w["default"]) if self._widgets is not None else w["default"]
            result.append({"id": w["id"], "name": _(w["name"]), "description": _(w["description"]),
                           "icon": w["icon"], "enabled": enabled, "available": self._widgets is not None})
        return result

    @pyqtSlot(str)
    def setLanguage(self, lang):
        set_system_language(lang)
        i18n.set_language(lang)
        self.langChanged.emit()
        self.widgetsChanged.emit()

    @pyqtSlot(bool)
    def setDark(self, dark):
        apply_theme(dark)

    @pyqtProperty("QVariantList", constant=True)
    def fonts(self):
        return [{"id": f["id"], "family": f["family"], "name": f["name"], "description": _(f["description"])}
                for f in fonts.FONTS]

    @pyqtProperty(str, constant=True)
    def font(self):
        return fonts.current_user()

    @pyqtProperty("QVariantList", constant=True)
    def iconThemes(self):
        themes = [{"id": "breeze", "name": _("Konaro (default)")},
                  {"id": "Papirus", "name": _("Minimalist")},
                  {"id": "Papirus-Dark", "name": _("Minimalist dark")}]
        return [t for t in themes if t["id"] == "breeze" or os.path.isdir("/usr/share/icons/" + t["id"])]

    @pyqtSlot(str)
    def setIconTheme(self, theme):
        _run(CHANGEICONS, theme)

    @pyqtSlot(str)
    def setFont(self, font_id):
        fonts.apply_user(font_id)

    @pyqtSlot(bool)
    def setReducedAnimations(self, reduced):
        set_reduced_animations(reduced)

    @pyqtSlot(bool)
    def setFeedback(self, enabled):
        set_feedback(enabled)

    @pyqtSlot(str, bool)
    def setWidget(self, widget_id, enabled):
        if desktopwidgets.set_enabled(widget_id, enabled) and self._widgets is not None:
            self._widgets[widget_id] = enabled
        self.widgetsChanged.emit()

    @pyqtSlot()
    def refreshOnline(self):
        self._online = online()
        self.onlineChanged.emit()

    @pyqtSlot()
    def openNetwork(self):
        launch("systemsettings", "kcm_networkmanagement")

    @pyqtSlot(str)
    def openTool(self, name):
        if name in ("konaro-updater", "konaro-drivers", "konaro-avatar"):
            launch(name)
        elif name.startswith("store"):
            category = name.partition(":")[2]
            launch("konaro-store", "--category", category) if category else launch("konaro-store")

    @pyqtSlot()
    def install(self):
        launch("calamares-install-debian")

    @pyqtSlot(bool)
    def finish(self, show_again):
        if not is_live():
            mark_done(not show_again)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-welcome")
    parser.add_argument("--autostart", action="store_true",
                        help="só abre se o usuário ainda não concluiu as boas-vindas")
    parser.add_argument("--page", type=int, default=0, help=argparse.SUPPRESS)
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.autostart and os.path.exists(DONE_FILE) and not is_live():
        return 0
    from .qmlapp import run
    bridge = WelcomeBridge()
    return run("konaro-welcome", _("Welcome to Konaro"), "welcome/Main.qml",
               context={"welcome": bridge, "startPage": args.page}, screenshot=args.screenshot)


if __name__ == "__main__":
    sys.exit(main())
