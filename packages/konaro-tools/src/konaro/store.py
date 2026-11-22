"""Loja Konaro — descobrir, instalar e remover aplicativos (interface em QML).

Camada de interface sobre backends maduros:
  - pacotes Debian (.deb) via PackageKit;
  - aplicativos Flatpak via Flathub.
O catálogo é uma seleção curada (/usr/share/konaro/store/catalog.json).
"""

import argparse
import glob
import json
import os
import sys

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import flatpak, packagekit
from .i18n import _, pick
from .worker import Worker, WorkerPool

CATALOG = os.environ.get("KONARO_STORE_CATALOG", "/usr/share/konaro/store/catalog.json")

ORIGINS = {
    "debian": "Debian (official)",
    "brave": "Brave (official repository)",
    "flathub": "Flathub (community)",
}
CATEGORY_NAMES = {
    "games": "Games", "windows": "Windows apps", "internet": "Internet",
    "productivity": "Productivity", "multimedia": "Multimedia", "graphics": "Graphics",
    "development": "Development", "utilities": "Utilities",
}


def load_catalog(path=CATALOG):
    with open(path, encoding="utf-8") as fh:
        apps = json.load(fh)["apps"]
    brave_repo = bool(glob.glob("/etc/apt/sources.list.d/brave*"))
    icons_dir = os.path.join(os.path.dirname(path), "icons")
    result = []
    for app in apps:
        app.setdefault("origin", "flathub" if app["backend"] == "flatpak" else "debian")
        if app["origin"] == "brave" and not brave_repo and not os.environ.get("KONARO_STORE_ALL"):
            continue  # sem o repositório oficial do Brave, não há de onde instalar
        shipped = os.path.join(icons_dir, app["id"] + ".png")
        if os.path.exists(shipped):
            app["icon"] = shipped   # ícone oficial do app (AppStream), mesmo sem estar instalado
        app["summaryText"] = pick(app["summary"])
        app["originText"] = _(ORIGINS[app["origin"]])
        app["formatText"] = _("Flatpak (isolated)") if app["backend"] == "flatpak" else _("Debian package (.deb)")
        app["categoryText"] = _(CATEGORY_NAMES.get(app["category"], app["category"]))
        result.append(app)
    return result


class StoreBridge(QObject):
    appsChanged = pyqtSignal()
    busyChanged = pyqtSignal()
    toast = pyqtSignal(str, bool, str)          # mensagem, é erro?, detalhes técnicos
    permissionsReady = pyqtSignal(str, "QVariantList")

    def __init__(self, catalog=None):
        super().__init__()
        self._apps = catalog if catalog is not None else load_catalog()
        self._apt = None            # {pacote: instalado?} — None enquanto carrega
        self._flatpak = None        # {app_id: "system"|"user"}
        self._busy_id = ""
        self._progress = -1.0
        self._pool = WorkerPool()

    # ------------------------------------------------------------ estado
    def _state(self, app):
        if app["backend"] == "flatpak":
            if self._flatpak is None:
                return "unknown"
            return "installed" if app["app"] in self._flatpak else "available"
        if self._apt is None:
            return "unknown"
        return "installed" if self._apt.get(app["packages"][0]) else "available"

    def _find(self, app_id):
        return next((a for a in self._apps if a["id"] == app_id), None)

    @pyqtProperty("QVariantList", notify=appsChanged)
    def apps(self):
        result = []
        for app in self._apps:
            item = dict(app)
            item["state"] = self._state(app)
            item["canOpen"] = app["backend"] == "flatpak" or bool(app.get("desktop"))
            result.append(item)
        return result

    @pyqtProperty(str, notify=busyChanged)
    def busyId(self):
        return self._busy_id

    @pyqtProperty(float, notify=busyChanged)
    def progress(self):
        return self._progress

    @pyqtSlot()
    def refresh(self):
        names = sorted({a["packages"][0] for a in self._apps if a["backend"] == "apt"})

        def check(progress=None):
            try:
                apt = {n: v["installed"] for n, v in packagekit.resolve(names).items()}
            except packagekit.PackageError:
                apt = {}
            return apt, flatpak.installed_apps()

        def done(result):
            self._apt, self._flatpak = result
            self.appsChanged.emit()

        self._pool.start(Worker(check, parent=self), ok=done)

    # ------------------------------------------------------------ ações
    def _operation(self, app, func, args, done_text):
        self._busy_id, self._progress = app["id"], 0.0
        self.busyChanged.emit()

        def progress(pct, _status):
            if pct is not None:
                self._progress = pct / 100.0
                self.busyChanged.emit()

        def finish():
            self._busy_id, self._progress = "", -1.0
            self.busyChanged.emit()

        def ok(_result):
            finish()
            self.toast.emit(done_text, False, "")
            self.refresh()

        def fail(message, details):
            finish()
            self.toast.emit(message, True, details)

        self._pool.start(Worker(func, *args, parent=self), ok=ok, fail=fail, progress=progress)

    @pyqtSlot(str)
    def install(self, app_id):
        app = self._find(app_id)
        if not app or self._busy_id:
            return
        if app["backend"] == "flatpak":
            self._operation(app, flatpak.install, (app["app"],), _("{name} was installed.").format(name=app["name"]))
        else:
            self._operation(app, packagekit.install, (app["packages"],), _("{name} was installed.").format(name=app["name"]))

    @pyqtSlot(str)
    def remove(self, app_id):
        app = self._find(app_id)
        if not app or self._busy_id:
            return
        if app["backend"] == "flatpak":
            scope = (self._flatpak or {}).get(app["app"], "system")
            self._operation(app, flatpak.uninstall, (app["app"], scope), _("{name} was removed.").format(name=app["name"]))
        else:
            self._operation(app, packagekit.remove, (app["packages"][:1],), _("{name} was removed.").format(name=app["name"]))

    @pyqtSlot(str)
    def open(self, app_id):
        from .launcher import launch, open_desktop_app
        app = self._find(app_id)
        if not app:
            return
        if app["backend"] == "flatpak":
            launch("flatpak", "run", app["app"])
        elif app.get("desktop"):
            open_desktop_app(app["desktop"])

    @pyqtSlot(str)
    def loadPermissions(self, app_id):
        app = self._find(app_id)
        if not app or app["backend"] != "flatpak":
            return
        worker = Worker(flatpak.permissions, app["app"], parent=self, with_progress=False)
        self._pool.start(worker, ok=lambda perms: self.permissionsReady.emit(
            app_id, perms if perms is not None else [_("Could not read the permissions (are you online?).")]))

    @pyqtSlot()
    def openUpdater(self):
        from .launcher import launch
        launch("konaro-updater")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-store")
    parser.add_argument("--category", default="home")
    parser.add_argument("--app", default="", help="abre direto a página de um app")
    parser.add_argument("--search", default="", help=argparse.SUPPRESS)
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    from .qmlapp import run
    bridge = StoreBridge()
    bridge.refresh()
    start = {"category": args.category, "app": args.app, "search": args.search}
    return run("konaro-store", _("Konaro Store"), "store/Main.qml",
               context={"store": bridge, "startup": start}, screenshot=args.screenshot)


if __name__ == "__main__":
    sys.exit(main())
