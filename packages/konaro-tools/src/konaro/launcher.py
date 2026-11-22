"""Abrir outros programas sem bloquear a interface."""

import shutil
import subprocess


def launch(*cmd):
    """Abre um programa em segundo plano (ignora se não existir)."""
    if cmd and shutil.which(cmd[0]):
        subprocess.Popen(list(cmd), start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False


def open_desktop_app(desktop_id):
    """Abre um aplicativo pelo seu arquivo .desktop."""
    return (launch("kioclient", "exec", "/usr/share/applications/%s" % desktop_id)
            or launch("gtk-launch", desktop_id.removesuffix(".desktop")))
