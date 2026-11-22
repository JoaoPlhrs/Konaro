"""Drivers do Konaro — detecta o hardware e sugere drivers/firmware.

Fluxo (documento mestre §5.2): identificar o dispositivo, explicar por que o
componente é recomendado, informar a origem, pedir autorização, instalar pelo
PackageKit e avisar se é preciso reiniciar. Nada é instalado automaticamente.

Fontes de detecção (ferramentas mantidas pelo Debian):
  - lspci -nnk       dispositivos PCI e driver em uso;
  - nvidia-detect    driver NVIDIA recomendado para a placa;
  - isenkram-lookup  pacotes que o Debian associa aos dispositivos presentes.
"""

import argparse
import re
import shutil
import subprocess
import sys

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import packagekit
from .i18n import _
from .worker import Worker, WorkerPool

_DEVICE = re.compile(r"^(?P<slot>\S+) (?P<cls>.+?) \[(?P<code>[0-9a-f]{4})\]: (?P<name>.+?) \[(?P<vendor>[0-9a-f]{4}):(?P<device>[0-9a-f]{4})\]")


def parse_lspci(text):
    devices, current = [], None
    for line in text.splitlines():
        match = _DEVICE.match(line)
        if match:
            current = dict(match.groupdict(), driver=None)
            devices.append(current)
        elif current and "Kernel driver in use:" in line:
            current["driver"] = line.split(":", 1)[1].strip()
    return devices


def kind(device):
    code = device["code"]
    if code.startswith("03"):
        return "Video"
    if code == "0280":
        return "Wi-Fi"
    if code.startswith("02"):
        return "Network"
    if code.startswith("0403") or code.startswith("0401"):
        return "Audio"
    return "Other"


def parse_nvidia_detect(text):
    """Extrai o(s) pacote(s) recomendados da saída do nvidia-detect."""
    packages, capture = [], False
    for line in text.splitlines():
        if "recommended to install" in line:
            capture = True
            continue
        if capture:
            word = line.strip()
            if not word or word.startswith("package"):
                if packages:
                    break
                continue
            if re.match(r"^[a-z0-9][a-z0-9.+-]+$", word):
                packages.append(word)
    return packages


def _output(cmd):
    if not shutil.which(cmd[0]):
        return ""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _installed(names):
    if not names:
        return set()
    out = _output(["dpkg-query", "-W", "-f", "${Package} ${db:Status-Status}\n"] + list(names))
    return {line.split()[0] for line in out.splitlines() if line.endswith(" installed")}


def scan(progress=None):
    devices = parse_lspci(_output(["lspci", "-nnk"]))
    interesting = [d for d in devices if kind(d) != "Other"]
    recommendations = []

    nvidia = [d for d in devices if d["vendor"] == "10de" and d["code"].startswith("03")]
    if nvidia and not any(d["driver"] == "nvidia" for d in nvidia):
        pkgs = parse_nvidia_detect(_output(["nvidia-detect"])) or ["nvidia-driver"]
        pkgs = pkgs + ["firmware-misc-nonfree", "linux-headers-amd64"]
        recommendations.append({
            "title": _("Proprietary NVIDIA driver"),
            "reason": _("Your NVIDIA graphics card ({device}) works better and faster in games with the official NVIDIA driver.").format(device=nvidia[0]["name"]),
            "origin": _("Debian non-free (proprietary, redistributable)"),
            "packages": pkgs,
            "restart": True,
        })

    suggested = [p.strip() for p in _output(["isenkram-lookup"]).split() if p.strip()]
    suggested = [p for p in suggested if not p.startswith("nvidia") and p not in _installed(suggested)]
    for pkg in sorted(set(suggested)):
        recommendations.append({
            "title": _("Additional component for your hardware") + ": " + pkg,
            "reason": _("Debian suggests this package for a device found in this computer."),
            "origin": _("Debian"),
            "packages": [pkg],
            "restart": pkg.startswith(("firmware-", "linux-")) or "dkms" in pkg,
        })

    for rec in recommendations:
        rec["packages"] = [p for p in rec["packages"] if p not in _installed(rec["packages"])] or rec["packages"]
    return {"devices": interesting, "recommendations": recommendations}


def install_recommendation(rec, progress=None):
    packagekit.install(rec["packages"], progress=progress)
    return rec.get("restart", False)


# ---------------------------------------------------------------- interface
ICONS = {"Video": "video-display", "Wi-Fi": "network-wireless", "Network": "network-wired",
         "Audio": "audio-card", "Other": "preferences-devices"}


class DriversBridge(QObject):
    changed = pyqtSignal()
    failed = pyqtSignal(str, str)
    restartNeeded = pyqtSignal()

    def __init__(self, demo=None):
        super().__init__()
        self._result = demo or {"devices": [], "recommendations": []}
        self._state = "ready" if demo else "scanning"     # scanning | ready | installing
        self._busy_index = -1
        self._progress = -1.0
        self._pool = WorkerPool()

    @pyqtProperty(str, notify=changed)
    def state(self):
        return self._state

    @pyqtProperty(int, notify=changed)
    def busyIndex(self):
        return self._busy_index

    @pyqtProperty(float, notify=changed)
    def progress(self):
        return self._progress

    @pyqtProperty("QVariantList", notify=changed)
    def recommendations(self):
        return [dict(r, packagesText=", ".join(r["packages"])) for r in self._result["recommendations"]]

    @pyqtProperty("QVariantList", notify=changed)
    def devices(self):
        return [{"kind": _(kind(d)), "name": d["name"], "icon": ICONS[kind(d)],
                 "status": _("Working (driver: {driver})").format(driver=d["driver"]) if d.get("driver")
                 else _("No driver in use"), "ok": bool(d.get("driver"))}
                for d in self._result["devices"]]

    def _set(self, state):
        self._state = state
        self.changed.emit()

    @pyqtSlot()
    def scan(self):
        self._set("scanning")

        def done(result):
            self._result = result
            self._set("ready")

        def fail(message, details):
            self._set("ready")
            self.failed.emit(message, details)

        self._pool.start(Worker(scan, parent=self), ok=done, fail=fail)

    @pyqtSlot(int)
    def install(self, index):
        recs = self._result["recommendations"]
        if not 0 <= index < len(recs) or self._state != "ready":
            return
        self._busy_index, self._progress = index, 0.0
        self._set("installing")

        def progress(pct, _status):
            if pct is not None:
                self._progress = pct / 100.0
                self.changed.emit()

        def finish():
            self._busy_index, self._progress = -1, -1.0

        def done(restart):
            finish()
            if restart:
                self.restartNeeded.emit()
            self.scan()

        def fail(message, details):
            finish()
            self._set("ready")
            self.failed.emit(message, details)

        self._pool.start(Worker(install_recommendation, recs[index], parent=self),
                         ok=done, fail=fail, progress=progress)

    @pyqtSlot()
    def reboot(self):
        from .launcher import launch
        if not launch("qdbus6", "org.kde.LogoutPrompt", "/LogoutPrompt", "promptReboot"):
            launch("systemctl", "reboot")


def run_gui(screenshot=None, demo=None):
    from .qmlapp import run
    bridge = DriversBridge(demo)
    if demo is None:
        bridge.scan()
    return run("konaro-drivers", _("Konaro Drivers"), "drivers/Main.qml",
               context={"drivers": bridge}, screenshot=screenshot)


DEMO = {
    "devices": [
        {"code": "0300", "name": "NVIDIA Corporation TU106 [GeForce RTX 2060]", "driver": "nouveau", "vendor": "10de"},
        {"code": "0280", "name": "Intel Corporation Wi-Fi 6 AX200", "driver": "iwlwifi", "vendor": "8086"},
        {"code": "0403", "name": "Intel Corporation Cannon Lake PCH cAVS", "driver": "snd_hda_intel", "vendor": "8086"},
    ],
    "recommendations": [{
        "title": "Proprietary NVIDIA driver",
        "reason": "Your NVIDIA graphics card (GeForce RTX 2060) works better and faster in games with the official NVIDIA driver.",
        "origin": "Debian non-free (proprietary, redistributable)",
        "packages": ["nvidia-driver", "firmware-misc-nonfree", "linux-headers-amd64"], "restart": True}],
}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-drivers")
    parser.add_argument("--list", action="store_true", help="mostra o resultado da análise no terminal")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    parser.add_argument("--demo", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.list:
        result = scan()
        for rec in result["recommendations"]:
            print("RECOMMEND:", rec["title"], "->", " ".join(rec["packages"]))
        for dev in result["devices"]:
            print("DEVICE:", kind(dev), "|", dev["name"], "|", dev["driver"] or "-")
        return 0
    if args.demo:
        demo = {"devices": DEMO["devices"], "recommendations": [
            dict(r, title=_(r["title"]), reason=_(r["reason"]).replace("({device})", "(GeForce RTX 2060)"),
                 origin=_(r["origin"])) for r in DEMO["recommendations"]]}
        demo["recommendations"][0]["reason"] = _("Your NVIDIA graphics card ({device}) works better and faster in games with the official NVIDIA driver.").format(device="GeForce RTX 2060")
        return run_gui(args.screenshot, demo)
    return run_gui(args.screenshot)


if __name__ == "__main__":
    sys.exit(main())
