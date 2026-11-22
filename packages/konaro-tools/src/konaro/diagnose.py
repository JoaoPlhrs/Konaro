"""Por que está lento? — diagnóstico do computador em linguagem simples.

Olha o que costuma deixar um PC lento (memória cheia, disco quase cheio, um app
usando todo o processador, superaquecimento, muitos apps abrindo junto com o
sistema) e mostra cada achado com uma explicação e um botão para resolver.
Só lê informações do próprio computador; nada é enviado.
"""

import argparse
import os
import shutil
import subprocess
import sys

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from .i18n import _
from .launcher import launch
from .worker import Worker, WorkerPool


def _read(path, default=""):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return default


def meminfo():
    info = {}
    for line in _read("/proc/meminfo").splitlines():
        key, _sep, rest = line.partition(":")
        try:
            info[key] = int(rest.split()[0]) * 1024
        except (ValueError, IndexError):
            pass
    return info


def top_processes(limit=5):
    """[(pid, nome, %cpu, %mem)] dos processos que mais usam CPU."""
    try:
        out = subprocess.run(["ps", "-eo", "pid=,comm=,%cpu=,%mem=", "--sort=-%cpu"],
                             capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for line in out.splitlines()[:limit]:
        parts = line.split()
        if len(parts) >= 4:
            try:
                rows.append((int(parts[0]), " ".join(parts[1:-2]), float(parts[-2]), float(parts[-1])))
            except ValueError:
                pass
    return rows


def temperature():
    temps = []
    for zone in sorted(os.listdir("/sys/class/thermal")) if os.path.isdir("/sys/class/thermal") else []:
        raw = _read(os.path.join("/sys/class/thermal", zone, "temp")).strip()
        if raw.isdigit():
            temps.append(int(raw) / 1000.0)
    return max(temps) if temps else None


def autostart_count():
    paths = [os.path.expanduser("~/.config/autostart")]
    return sum(len([f for f in os.listdir(p) if f.endswith(".desktop")]) for p in paths if os.path.isdir(p))


def cache_size():
    total = 0
    for base, _dirs, files in os.walk(os.path.expanduser("~/.cache"), onerror=lambda e: None):
        for f in files:
            try:
                total += os.lstat(os.path.join(base, f)).st_size
            except OSError:
                pass
    return total


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("%.0f %s" % (n, unit)) if unit in ("B", "KB", "MB") else ("%.1f %s" % (n, unit))
        n /= 1024.0


def analyze():
    """Lista de achados: {level: ok|warn|bad, title, text, action, actionText}."""
    findings = []
    mem = meminfo()
    total, avail = mem.get("MemTotal", 0), mem.get("MemAvailable", 0)
    if total:
        used = 1 - avail / total
        if used > 0.9:
            findings.append({"level": "bad", "title": _("Memory is almost full"),
                             "text": _("{used} of {total} in use. Close apps you are not using, especially browsers with many tabs.").format(
                                 used=human(total - avail), total=human(total)),
                             "action": "monitor", "actionText": _("See what is using memory")})
        elif used > 0.75:
            findings.append({"level": "warn", "title": _("Memory is busy"),
                             "text": _("{used} of {total} in use. If things feel slow, close a few apps.").format(
                                 used=human(total - avail), total=human(total)),
                             "action": "monitor", "actionText": _("See what is using memory")})
        swap_total, swap_free = mem.get("SwapTotal", 0), mem.get("SwapFree", 0)
        if swap_total and (swap_total - swap_free) > 0.5 * swap_total:
            findings.append({"level": "warn", "title": _("The system is using the disk as memory"),
                             "text": _("This is much slower than real memory. Closing apps helps; adding RAM solves it for good."),
                             "action": "monitor", "actionText": _("Open the System Monitor")})
    disk = shutil.disk_usage("/")
    free_ratio = disk.free / disk.total if disk.total else 1
    if free_ratio < 0.08:
        findings.append({"level": "bad", "title": _("The disk is almost full"),
                         "text": _("Only {free} free. A full disk makes everything slow and can stop updates.").format(free=human(disk.free)),
                         "action": "files", "actionText": _("Free up space")})
    elif free_ratio < 0.15:
        findings.append({"level": "warn", "title": _("Little free disk space"),
                         "text": _("{free} free. Consider removing large files you no longer need.").format(free=human(disk.free)),
                         "action": "files", "actionText": _("Free up space")})
    for pid, name, cpu, _mem in top_processes(3):
        if cpu > 60 and name not in ("ps", "konaro-diagnose", "python3"):
            findings.append({"level": "warn", "title": _("{app} is using a lot of the processor").format(app=name),
                             "text": _("It is using {cpu}% of the processor right now. If you are not using it, close it.").format(cpu=round(cpu)),
                             "action": "kill:%d" % pid, "actionText": _("Close {app}").format(app=name)})
    temp = temperature()
    if temp and temp >= 85:
        findings.append({"level": "bad", "title": _("The computer is very hot ({t} °C)").format(t=round(temp)),
                         "text": _("When it overheats, the processor slows down on purpose. Check that the air vents are not blocked and clean the dust."),
                         "action": "", "actionText": ""})
    cache = cache_size()
    if cache > 2 * 1024 ** 3:
        findings.append({"level": "warn", "title": _("Apps keep {size} of temporary files").format(size=human(cache)),
                         "text": _("Cleaning them is safe: apps recreate what they need."),
                         "action": "clean-cache", "actionText": _("Clean temporary files")})
    n_auto = autostart_count()
    if n_auto > 6:
        findings.append({"level": "warn", "title": _("{n} apps open together with the system").format(n=n_auto),
                         "text": _("Each one makes startup slower. Turn off the ones you don't need."),
                         "action": "autostart", "actionText": _("Choose startup apps")})
    if not findings:
        findings.append({"level": "ok", "title": _("Everything looks fine"),
                         "text": _("Memory, disk, processor and temperature are normal. If one specific app is slow, it may be the app itself."),
                         "action": "", "actionText": ""})
    summary = {
        "memory": "%s / %s" % (human(total - avail), human(total)) if total else "—",
        "disk": _("{free} free").format(free=human(disk.free)),
        "temp": ("%d °C" % round(temp)) if temp else "—",
        "cpu": ", ".join(n for _p, n, c, _m in top_processes(3) if c > 5) or _("calm"),
    }
    return {"findings": findings, "summary": summary}


class DiagnoseBridge(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._state = "checking"
        self._result = {"findings": [], "summary": {}}
        self._pool = WorkerPool()

    @pyqtProperty(str, notify=changed)
    def state(self):
        return self._state

    @pyqtProperty("QVariantList", notify=changed)
    def findings(self):
        return self._result["findings"]

    @pyqtProperty("QVariantMap", notify=changed)
    def summary(self):
        return self._result["summary"]

    @pyqtSlot()
    def check(self):
        self._state = "checking"
        self.changed.emit()

        def done(result):
            self._result, self._state = result, "ready"
            self.changed.emit()
        self._pool.start(Worker(analyze, with_progress=False), ok=done, fail=lambda m, d: done(
            {"findings": [{"level": "warn", "title": _("Could not finish the check"), "text": m,
                           "action": "", "actionText": ""}], "summary": {}}))

    @pyqtSlot(str)
    def act(self, action):
        if action == "monitor":
            launch("plasma-systemmonitor")
        elif action == "files":
            launch("dolphin", os.path.expanduser("~"))
        elif action == "autostart":
            launch("systemsettings", "kcm_autostart")
        elif action == "clean-cache":
            cache = os.path.expanduser("~/.cache")
            for name in os.listdir(cache) if os.path.isdir(cache) else []:
                path = os.path.join(cache, name)
                if os.path.isdir(path) and not os.path.islink(path):
                    shutil.rmtree(path, ignore_errors=True)
            self.check()
        elif action.startswith("kill:"):
            try:
                os.kill(int(action[5:]), 15)
            except (OSError, ValueError):
                pass
            self.check()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-diagnose")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    from .qmlapp import run
    bridge = DiagnoseBridge()
    bridge.check()
    return run("konaro-diagnose", _("Why is it slow?"), "diagnose/Main.qml",
               context={"diag": bridge}, screenshot=args.screenshot, size=(820, 620))


if __name__ == "__main__":
    sys.exit(main())
