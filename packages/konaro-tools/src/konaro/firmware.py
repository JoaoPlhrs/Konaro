"""Atualização de firmware (BIOS/UEFI, SSD, periféricos) via fwupd / LVFS.

Usa a ferramenta oficial `fwupdmgr`. Só lista e instala quando o usuário pede, pelo
app Atualizações; o fwupd pede a senha de administrador quando necessário.
"""

import json
import shutil
import subprocess


def available():
    return shutil.which("fwupdmgr") is not None


def updates():
    """Lista de atualizações de firmware: [{id, name, summary, version}]."""
    if not available():
        return []
    try:
        res = subprocess.run(["fwupdmgr", "get-updates", "--json", "--no-unreported-check"],
                             capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return []
    try:
        data = json.loads(res.stdout or "{}")
    except ValueError:
        return []
    out = []
    for dev in data.get("Devices", []):
        for rel in dev.get("Releases", [])[:1]:
            out.append({"id": dev.get("DeviceId", ""), "name": dev.get("Name", "Firmware"),
                        "summary": rel.get("Summary", ""), "version": rel.get("Version", "")})
    return out


def update_all(progress=None):
    """Instala todas as atualizações de firmware (pode exigir reiniciar)."""
    if progress:
        progress(None, "firmware")
    res = subprocess.run(["fwupdmgr", "update", "--assume-yes", "--no-reboot-check"],
                         capture_output=True, text=True, timeout=3600)
    if res.returncode not in (0, 2):     # 2 = nada a fazer
        raise RuntimeError(res.stderr.strip() or res.stdout.strip() or "fwupdmgr failed")
    return True
