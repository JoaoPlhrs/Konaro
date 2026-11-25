"""Boas-vindas do Konaro — experiência guiada de primeiro uso (interface em QML).

Abre automaticamente no primeiro login de cada usuário (autostart) e pode ser
aberta de novo pelo menu. Na sessão live, mostra também o botão de instalar.
Não exige conta nem conecta serviços externos.
"""

import argparse
import os
import subprocess
import sys
import threading

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import desktopwidgets, fonts, i18n
from .i18n import _
from .launcher import launch

CONFIG_DIR = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "konaro")
DONE_FILE = os.path.join(CONFIG_DIR, "welcome-done")
LNF = "/usr/share/plasma/look-and-feel/%s/contents/previews/preview.png"
CHANGEICONS = "/usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons"


def _mem_kb():
    try:
        with open("/proc/meminfo", encoding="utf-8") as fh:
            return int(fh.readline().split()[1])
    except (OSError, ValueError, IndexError):
        return 0


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


ACCENT_FILE = os.path.join(CONFIG_DIR, "accent")
ICONS_FILE = os.path.join(CONFIG_DIR, "icons")
ACCENTS = [("", "Graphite", "#3A3A3C"), ("Blue", "Blue", "#0A84FF"), ("Purple", "Purple", "#BF5AF2"),
           ("Pink", "Pink", "#FF4580"), ("Green", "Green", "#30D158"), ("Orange", "Orange", "#FF9F0A"),
           ("Teal", "Teal", "#40C8E0")]
# temas de ícones livres (nenhum copia ícones da Apple ou da Microsoft); os que não
# vêm instalados são baixados na hora, pela internet
ICON_THEMES = [
    {"id": "breeze", "dark": "breeze-dark", "name": "Konaro (default)", "package": ""},
    {"id": "Papirus", "dark": "Papirus-Dark", "name": "Minimalist", "package": "papirus-icon-theme"},
    {"id": "Numix-Circle", "dark": "Numix-Circle", "name": "Round", "package": "numix-icon-theme-circle"},
    {"id": "Suru", "dark": "Suru", "name": "Soft", "package": "suru-icon-theme"},
    {"id": "elementary-xfce", "dark": "elementary-xfce-dark", "name": "Classic", "package": "elementary-xfce-icon-theme"},
    {"id": "Moka", "dark": "Moka", "name": "Colorful", "package": "moka-icon-theme"},
    {"id": "Yaru", "dark": "Yaru-dark", "name": "Warm", "package": "yaru-theme-icon"},
]


def _read(path, default=""):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return default


def _write(path, value):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(value)


def icon_theme_for(dark):
    chosen = _read(ICONS_FILE, "breeze")
    for theme in ICON_THEMES:
        if theme["id"] == chosen:
            return theme["dark"] if dark else theme["id"]
    return "breeze-dark" if dark else "breeze"


def apply_theme(dark):
    """Troca claro/escuro SEM reaplicar o layout da área de trabalho.

    `plasma-apply-lookandfeel` também reaplica o layout (painéis/dock) e o usuário
    perderia os atalhos fixados; por isso aplicamos as partes separadamente.
    O papel de parede Konaro troca sozinho (images_dark) com o esquema escuro.
    """
    _run("plasma-apply-colorscheme", ("KonaroDark" if dark else "KonaroLight") + _read(ACCENT_FILE))
    _run("plasma-apply-desktoptheme", "konaro")
    _run(CHANGEICONS, icon_theme_for(dark))
    _run("kwriteconfig6", "--file", "kdeglobals", "--group", "KDE", "--key", "LookAndFeelPackage",
         "org.konaro.desktop.dark" if dark else "org.konaro.desktop")
    _run("kwriteconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "theme",
         "__aurorae__svg__KonaroDark" if dark else "__aurorae__svg__Konaro")
    _run("qdbus6", "org.kde.KWin", "/KWin", "reconfigure")


def current_is_dark():
    return _run("kreadconfig6", "--file", "kdeglobals", "--group", "General", "--key", "ColorScheme").startswith("KonaroDark")


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


SET_PASSWORD = "/usr/lib/konaro/konaro-set-password"


def change_password(new):
    """Troca a senha da própria conta. O polkit pede a senha ATUAL antes."""
    try:
        proc = subprocess.run([SET_PASSWORD], input=new + "\n", capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    if proc.returncode == 0:
        return True, ""
    if proc.returncode in (126, 127):     # pkexec: autorização negada/cancelada
        return False, "cancelled"
    return False, (proc.stderr or proc.stdout).strip()


def update_wallet():
    """A Carteira do KDE (senhas de Wi-Fi) abre com a senha de login. Ao trocar a
    senha, abre a janela do KDE para trocar a da carteira também; senão ela pediria
    a senha antiga no próximo login. Devolve True se a janela foi aberta."""
    wallet = os.path.expanduser("~/.local/share/kwalletd/kdewallet.kwl")
    if not os.path.exists(wallet):
        return False
    try:
        subprocess.Popen(["qdbus6", "org.kde.kwalletd6", "/modules/kwalletd6", "org.kde.KWallet.changePassword",
                          "kdewallet", "0", "konaro-welcome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def lock_on_resume():
    return _run("kreadconfig6", "--file", "kscreenlockerrc", "--group", "Daemon", "--key", "LockOnResume",
                "--default", "true") != "false"


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
    passwordResult = pyqtSignal(bool, str)
    iconThemeStatus = pyqtSignal(str, str)     # id, "installing" | "ok" | mensagem de erro

    def __init__(self):
        super().__init__()
        self._widgets = desktopwidgets.current()
        self._online = online()

    @pyqtProperty(str, notify=langChanged)
    def lang(self):
        return i18n.LANG

    @pyqtProperty(str, constant=True)
    def memoryGb(self):
        return "%.1f" % (_mem_kb() / 1048576.0)

    @pyqtProperty(str, constant=True)
    def memoryHint(self):
        """Edição normal com menos de 3 GB de RAM: sugere a Fênix Lite."""
        lite = os.path.exists("/etc/xdg/konaro-lite")
        if lite or _mem_kb() == 0 or _mem_kb() >= 3 * 1024 * 1024 - 200 * 1024:
            return ""
        return ("This computer has {gb} GB of memory. Konaro Fênix Lite, made for computers "
                "like this one, will run much better.")

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
        return [{"id": t["id"], "name": _(t["name"]),
                 "installed": not t["package"] or os.path.isdir("/usr/share/icons/" + t["id"])}
                for t in ICON_THEMES]

    @pyqtProperty(str, constant=True)
    def iconTheme(self):
        return _read(ICONS_FILE, "breeze")

    @pyqtSlot(str)
    def setIconTheme(self, theme_id):
        theme = next((t for t in ICON_THEMES if t["id"] == theme_id), None)
        if not theme:
            return

        def apply():
            _write(ICONS_FILE, theme_id)
            _run(CHANGEICONS, icon_theme_for(current_is_dark()))

        if not theme["package"] or os.path.isdir("/usr/share/icons/" + theme_id):
            apply()
            self.iconThemeStatus.emit(theme_id, "ok")
            return

        def work():
            from . import packagekit
            self.iconThemeStatus.emit(theme_id, "installing")
            try:
                packagekit.install([theme["package"]])
            except packagekit.PackageError as exc:
                self.iconThemeStatus.emit(theme_id, str(exc.args[0]))
                return
            apply()
            self.iconThemeStatus.emit(theme_id, "ok")
        threading.Thread(target=work, daemon=True).start()

    @pyqtProperty("QVariantList", constant=True)
    def accents(self):
        return [{"id": a[0], "name": _(a[1]), "color": a[2]} for a in ACCENTS]

    @pyqtProperty(str, constant=True)
    def accent(self):
        return _read(ACCENT_FILE)

    @pyqtSlot(str)
    def setAccent(self, accent):
        if accent not in [a[0] for a in ACCENTS]:
            return
        _write(ACCENT_FILE, accent)
        _run("plasma-apply-colorscheme", ("KonaroDark" if current_is_dark() else "KonaroLight") + accent)

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

    @pyqtSlot(str)
    def setPassword(self, new):
        def work():
            ok, err = change_password(new)
            if ok:
                msg = _("Password changed. Use it to log in and to unlock the screen.")
                if update_wallet():
                    msg += " " + _("Also confirm it in the KDE Wallet window, where Wi-Fi passwords are kept.")
            elif err == "cancelled":
                msg = _("The current password was not confirmed. Nothing was changed.")
            else:
                msg = _("Could not change the password: {error}").format(error=err or "?")
            self.passwordResult.emit(ok, msg)
        threading.Thread(target=work, daemon=True).start()

    @pyqtProperty(bool, constant=True)
    def lockOnResume(self):
        return lock_on_resume()

    @pyqtSlot(bool)
    def setLockOnResume(self, on):
        _run("kwriteconfig6", "--file", "kscreenlockerrc", "--group", "Daemon", "--key", "LockOnResume",
             "true" if on else "false")
        _run("kwriteconfig6", "--file", "kscreenlockerrc", "--group", "Daemon", "--key", "Autolock",
             "true" if on else "false")

    @pyqtProperty(str, constant=True)
    def userName(self):
        import pwd
        entry = pwd.getpwuid(os.getuid())
        return (entry.pw_gecos.split(",")[0] or entry.pw_name)

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
