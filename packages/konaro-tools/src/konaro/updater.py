"""Atualizações do Konaro — avisa e deixa o usuário escolher quando instalar.

  konaro-updater                 abre a janela
  konaro-updater --check-notify  verifica em segundo plano e, se houver
                                 atualizações, mostra uma notificação
                                 (executado por um timer systemd do usuário).

Nunca instala nada sem uma ação explícita do usuário.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import firmware, flatpak, packagekit
from .i18n import _
from .worker import Worker, WorkerPool

STATE_DIR = os.path.join(os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")), "konaro")
STATE_FILE = os.path.join(STATE_DIR, "updater.json")

GROUPS = [
    ("security", "Security updates", "Fix vulnerabilities. Recommended to install as soon as possible.", "security-high"),
    ("konaro", "Konaro components", "Konaro OS's own tools and appearance.", "konaro-start"),
    ("system", "System updates", "Bug fixes and improvements for the system and its programs.", "system-software-update"),
    ("flatpak", "Apps (Flatpak)", "Apps installed from Flathub.", "flatpak-discover"),
    ("firmware", "Firmware", "BIOS/UEFI, disks and devices, from the manufacturers (LVFS). May require a restart.", "cpu"),
]


def classify(pkg_updates, flatpak_updates, firmware_updates=()):
    groups = {key: [] for key, *_rest in GROUPS}
    for upd in pkg_updates:
        if upd["security"]:
            groups["security"].append(upd)
        elif upd["konaro"]:
            groups["konaro"].append(upd)
        else:
            groups["system"].append(upd)
    groups["flatpak"] = list(flatpak_updates)
    groups["firmware"] = list(firmware_updates)
    return groups


def check(refresh=True, progress=None):
    if refresh:
        packagekit.refresh(progress=progress)
    return classify(packagekit.get_updates(progress=progress), flatpak.updates(), firmware.updates())


def _load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def check_and_notify():
    """Modo silencioso: só notifica se o conjunto de atualizações mudou."""
    try:
        groups = check(refresh=True)
    except packagekit.PackageError:
        return 0  # sem rede ou serviço ocupado: tenta de novo no próximo timer
    ids = sorted(u["id"] for items in groups.values() for u in items)
    state = _load_state()
    state["last_check"] = time.time()
    digest = hashlib.sha256("\n".join(ids).encode()).hexdigest()
    total, security = len(ids), len(groups["security"])
    if total and digest != state.get("notified"):
        state["notified"] = digest
        body = (_("{n} update(s) available, {s} of them for security.").format(n=total, s=security)
                if security else _("{n} update(s) available.").format(n=total))
        try:
            answer = subprocess.run(
                ["notify-send", "--app-name=Konaro", "--icon=konaro-updater",
                 "--urgency=" + ("critical" if security else "normal"),
                 "--action=show=" + _("Show"), "--wait", _("Updates available"), body],
                capture_output=True, text=True, timeout=6 * 3600).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            answer = ""
        if answer == "show":
            subprocess.Popen(["konaro-updater"], start_new_session=True)
    _save_state(state)
    return 0


# ---------------------------------------------------------------- interface
def snapshot_before_update():
    """"Voltar no tempo": cria um ponto de restauração antes de atualizar o sistema.

    Só faz algo se o sistema estiver em Btrfs com o Timeshift configurado pelo
    instalador; nunca impede a atualização se falhar.
    """
    import os
    import subprocess
    if not os.path.exists("/etc/timeshift/timeshift.json"):
        return False
    try:
        return subprocess.run(["systemctl", "start", "konaro-snapshot-update.service"],
                              capture_output=True, timeout=900).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


class UpdaterBridge(QObject):
    changed = pyqtSignal()
    failed = pyqtSignal(str, str)
    restartNeeded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._groups = {}
        self._state = "checking"        # checking | ready | installing
        self._progress = -1.0
        self._last = ""
        self._pool = WorkerPool()

    @pyqtProperty(str, notify=changed)
    def state(self):
        return self._state

    @pyqtProperty(float, notify=changed)
    def progress(self):
        return self._progress

    @pyqtProperty(str, notify=changed)
    def lastCheck(self):
        return self._last

    @pyqtProperty("QVariantList", notify=changed)
    def groups(self):
        result = []
        for key, title, description, icon in GROUPS:
            items = self._groups.get(key) or []
            if not items:
                continue
            names = [i.get("name", "") for i in items]
            result.append({
                "key": key, "title": _(title), "description": _(description), "icon": icon,
                "count": len(items),
                "restart": key != "flatpak" and packagekit.may_need_restart(names),
                "items": [("%s  %s" % (i.get("name", i.get("id")), i.get("version", ""))).strip() for i in items],
            })
        return result

    @pyqtProperty(int, notify=changed)
    def total(self):
        return sum(len(v) for v in self._groups.values())

    def _set(self, state, progress=-1.0):
        self._state, self._progress = state, progress
        self.changed.emit()

    @pyqtSlot()
    def check(self):
        self._set("checking")

        def done(groups):
            self._groups = groups
            self._last = time.strftime("%H:%M")
            state = _load_state()
            state["last_check"] = time.time()
            _save_state(state)
            self._set("ready")

        def fail(message, details):
            self._set("ready")
            self.failed.emit(message, details)

        self._pool.start(Worker(check, parent=self), ok=done, fail=fail)

    @pyqtSlot("QVariantList")
    def install(self, keys):
        keys = list(keys)
        pk_ids = [u["id"] for k in keys if k not in ("flatpak", "firmware") for u in self._groups.get(k, [])]
        names = [u.get("name", "") for k in keys if k not in ("flatpak", "firmware") for u in self._groups.get(k, [])]
        do_flatpak = "flatpak" in keys and bool(self._groups.get("flatpak"))
        do_firmware = "firmware" in keys and bool(self._groups.get("firmware"))
        if not pk_ids and not do_flatpak and not do_firmware:
            return

        def work(progress=None):
            if pk_ids:
                snapshot_before_update()
            restart = packagekit.update(pk_ids, progress=progress) if pk_ids else False
            if do_flatpak:
                flatpak.update_all(progress=progress)
            if do_firmware:
                firmware.update_all(progress=progress)
                restart = True
            return restart or packagekit.may_need_restart(names)

        def progress(pct, _status):
            if pct is not None:
                self._set("installing", pct / 100.0)

        def done(restart):
            if restart:
                self.restartNeeded.emit()
            self.check()

        def fail(message, details):
            self._set("ready")
            self.failed.emit(message, details)

        self._set("installing", 0.0)
        self._pool.start(Worker(work, parent=self), ok=done, fail=fail, progress=progress)

    @pyqtSlot()
    def reboot(self):
        from .launcher import launch
        if not launch("qdbus6", "org.kde.LogoutPrompt", "/LogoutPrompt", "promptReboot"):
            launch("systemctl", "reboot")


def run_gui(screenshot=None, demo=False):
    from .qmlapp import run
    bridge = UpdaterBridge()
    if demo:
        bridge._groups = classify(
            [{"id": "a", "name": "openssl", "version": "3.5.4-1~deb13u2", "security": True, "konaro": False},
             {"id": "b", "name": "linux-image-amd64", "version": "6.12.120-1", "security": True, "konaro": False},
             {"id": "c", "name": "firefox-esr", "version": "153.8.0esr-1~deb13u1", "security": False, "konaro": False},
             {"id": "d", "name": "konaro-store", "version": "0.1.1", "security": False, "konaro": True}],
            [{"id": "com.valvesoftware.Steam", "name": "Steam"}])
        bridge._state, bridge._last = "ready", "09:41"
    else:
        bridge.check()
    return run("konaro-updater", _("Konaro Updates"), "updater/Main.qml",
               context={"updater": bridge}, screenshot=screenshot)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-updater")
    parser.add_argument("--check-notify", action="store_true")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    parser.add_argument("--demo", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.check_notify:
        return check_and_notify()
    return run_gui(args.screenshot, args.demo)


if __name__ == "__main__":
    sys.exit(main())
