"""Acesso a aplicativos Flatpak (Flathub) via a ferramenta `flatpak`.

Instalações são feitas no escopo do sistema (`--system`); o próprio Flatpak
pede autorização via polkit quando necessário.
"""

import configparser
import re
import subprocess

from .i18n import _
from .packagekit import PackageError, friendly_error

REMOTE = "flathub"
_PERCENT = re.compile(r"(\d{1,3})%")


def _run(args, progress=None):
    """Executa `flatpak` lendo a saída linha a linha para informar o progresso."""
    proc = subprocess.Popen(["flatpak"] + args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    output = []
    for line in iter(proc.stdout.readline, ""):
        line = line.rstrip()
        output.append(line)
        if progress:
            match = _PERCENT.findall(line)
            if match:
                progress(min(100, int(match[-1])), None)
            elif line:
                progress(None, line[:80])
    proc.wait()
    text = "\n".join(output)
    if proc.returncode != 0:
        raise PackageError(friendly_error(text), text)
    return text


def available():
    try:
        subprocess.run(["flatpak", "--version"], capture_output=True, check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def installed_apps():
    """{app_id: "system"|"user"} dos aplicativos Flatpak instalados."""
    try:
        out = subprocess.run(["flatpak", "list", "--app", "--columns=application,installation"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    apps = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if parts and parts[0]:
            apps[parts[0]] = parts[1] if len(parts) > 1 else "system"
    return apps


def install(app_id, progress=None):
    return _run(["install", "--system", "-y", "--noninteractive", REMOTE, app_id], progress)


def uninstall(app_id, installation="system", progress=None):
    scope = "--user" if installation == "user" else "--system"
    out = _run(["uninstall", scope, "-y", "--noninteractive", app_id], progress)
    try:
        _run(["uninstall", scope, "-y", "--noninteractive", "--unused"])
    except PackageError:
        pass
    return out


def updates():
    """[{id, name}] de apps/runtimes Flatpak com atualização disponível."""
    try:
        out = subprocess.run(["flatpak", "remote-ls", "--updates", "--system",
                              "--columns=application,name"],
                             capture_output=True, text=True, check=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    result = []
    for line in out.splitlines():
        parts = line.split("\t")
        if parts and parts[0] and parts[0] != "Application ID":
            result.append({"id": parts[0], "name": parts[1] if len(parts) > 1 else parts[0]})
    return result


def update_all(progress=None):
    return _run(["update", "--system", "-y", "--noninteractive"], progress)


def describe_permissions(metadata_text):
    """Traduz a seção [Context] do metadata de um Flatpak em frases simples."""
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    try:
        parser.read_string(metadata_text)
    except configparser.Error:
        return []
    if not parser.has_section("Context"):
        return [_("No special permissions")]
    ctx = parser["Context"]

    def items(key):
        return [v for v in ctx.get(key, "").split(";") if v]

    shared, sockets, devices, files = items("shared"), items("sockets"), items("devices"), items("filesystems")
    perms = []
    if "network" in shared:
        perms.append(_("Network access"))
    if "host" in files or "host-os" in files:
        perms.append(_("Full access to the whole system's files"))
    elif "home" in files:
        perms.append(_("Full access to your home folder"))
    elif any(f.startswith("xdg-download") for f in files):
        perms.append(_("Access to your Downloads folder"))
    elif files:
        perms.append(_("Access to some of your folders"))
    if "all" in devices:
        perms.append(_("Access to devices (cameras, controllers…)"))
    elif "dri" in devices:
        perms.append(_("Hardware graphics acceleration"))
    if "pulseaudio" in sockets:
        perms.append(_("Sound"))
    if any(s in sockets for s in ("x11", "wayland", "fallback-x11")):
        perms.append(_("Display (window)"))
    if "bluetooth" in devices or "bluetooth" in sockets:
        perms.append(_("Bluetooth"))
    return perms or [_("No special permissions")]


def permissions(app_id):
    try:
        out = subprocess.run(["flatpak", "remote-info", "--system", "-m", REMOTE, app_id],
                             capture_output=True, text=True, check=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return describe_permissions(out)
