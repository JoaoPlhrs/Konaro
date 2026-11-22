"""Restaurar o Konaro — três jeitos de consertar o sistema, do mais leve ao mais forte.

1. Restaurar minhas configurações: guarda as configurações atuais numa pasta e
   volta a aparência e os apps ao padrão (arquivos pessoais não são tocados).
2. Voltar no tempo: abre os pontos de restauração (Timeshift).
3. Restaurar o sistema de fábrica: volta o sistema ao ponto "Sistema recém-instalado"
   criado logo após a instalação; documentos, fotos e downloads ficam intactos
   (a pasta pessoal não entra nos pontos de restauração). Pede a senha e reinicia.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from .i18n import _
from .launcher import launch

# configurações do usuário que voltam ao padrão (o resto de ~/.config fica)
USER_CONFIG = [
    "~/.config/plasma-org.kde.plasma.desktop-appletsrc", "~/.config/plasmashellrc", "~/.config/kdeglobals",
    "~/.config/kwinrc", "~/.config/kcminputrc", "~/.config/kglobalshortcutsrc", "~/.config/plasmarc",
    "~/.config/ksplashrc", "~/.config/kscreenlockerrc", "~/.config/dolphinrc", "~/.config/konsolerc",
    "~/.config/konaro", "~/.local/share/plasma",
]
FACTORY_HELPER = "/usr/lib/konaro/konaro-factory-restore"


def reset_user_settings():
    """Move as configurações para ~/Konaro - configurações antigas <data>/ e sai da sessão."""
    stamp = time.strftime("%Y-%m-%d %H-%M")
    backup = os.path.expanduser("~/Konaro - configurações antigas %s" % stamp)
    moved = 0
    for item in USER_CONFIG:
        path = os.path.expanduser(item)
        if os.path.lexists(path):
            dest = os.path.join(backup, os.path.relpath(path, os.path.expanduser("~")))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(path, dest)
            moved += 1
    return backup if moved else ""


def factory_available():
    return os.path.exists("/etc/timeshift/timeshift.json") and os.path.exists(FACTORY_HELPER)


class RestoreBridge(QObject):
    changed = pyqtSignal()
    message = pyqtSignal(str, bool)

    @pyqtProperty(bool, constant=True)
    def factoryAvailable(self):
        return factory_available()

    @pyqtSlot()
    def resetSettings(self):
        backup = reset_user_settings()
        self.message.emit(_("Your old settings were saved in “{folder}”. Logging out to apply…").format(
            folder=os.path.basename(backup)) if backup else _("Settings are already the default."), False)
        subprocess.Popen(["sh", "-c", "sleep 3; qdbus6 org.kde.Shutdown /Shutdown logout"],
                         start_new_session=True)

    @pyqtSlot()
    def openTimeMachine(self):
        launch("timeshift-launcher")

    @pyqtSlot()
    def factoryRestore(self):
        try:
            res = subprocess.run(["pkexec", FACTORY_HELPER], capture_output=True, text=True, timeout=3600)
        except (OSError, subprocess.SubprocessError) as exc:
            self.message.emit(str(exc), True)
            return
        if res.returncode == 0:
            self.message.emit(_("Done. The computer will restart to finish."), False)
            subprocess.Popen(["sh", "-c", "sleep 4; systemctl reboot"], start_new_session=True)
        elif res.returncode == 126:
            pass   # o usuário cancelou a senha
        else:
            self.message.emit((res.stdout + res.stderr).strip().splitlines()[-1] if (res.stdout + res.stderr).strip()
                              else _("Could not restore."), True)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-restore")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    from .qmlapp import run
    return run("konaro-restore", _("Restore Konaro"), "restore/Main.qml",
               context={"restore": RestoreBridge()}, screenshot=args.screenshot, size=(760, 600))


if __name__ == "__main__":
    sys.exit(main())
