"""Acesso aos pacotes Debian via PackageKit (API GLib, chamadas síncronas).

Todas as operações que alteram o sistema passam pelo daemon do PackageKit,
que pede autorização via polkit (diálogo de senha do Plasma). As funções
são bloqueantes: chame-as a partir de uma thread de trabalho (ui.Worker).
"""

import gi

gi.require_version("PackageKitGlib", "1.0")
from gi.repository import GLib, PackageKitGlib as PK  # noqa: E402

from .i18n import _  # noqa: E402


class PackageError(Exception):
    """Erro com mensagem amigável (`str(e)`) e detalhes técnicos (`e.details`)."""

    def __init__(self, message, details=""):
        super().__init__(message)
        self.details = details


def friendly_error(details):
    text = (details or "").lower()
    if any(k in text for k in ("not authorized", "authorization", "dismissed", "cancelled", "canceled")):
        return _("The operation was cancelled or the password was not confirmed.")
    if any(k in text for k in ("offline", "no network", "network", "could not resolve", "failed to fetch",
                               "temporary failure")):
        return _("No internet connection. Connect to a network and try again.")
    if any(k in text for k in ("lock", "another transaction", "in use", "already running")):
        return _("Another installation or update is already running. Wait for it to finish and try again.")
    if any(k in text for k in ("not found", "no packages", "unable to locate")):
        return _("The package was not found in the configured sources.")
    if "space" in text:
        return _("There is not enough free disk space.")
    if any(k in text for k in ("serviceunknown", "name has no owner", "dbus")):
        return _("The package system service is not available.")
    return _("Something went wrong")


def _client():
    client = PK.Client()
    client.set_interactive(True)
    return client


def _bitfield_filter(name):
    return PK.filter_bitfield_from_string(name)


def _trusted():
    return PK.transaction_flag_bitfield_from_string("only-trusted")


def _progress(callback):
    """Adapta o progresso do PackageKit para callback(percent|None, status|None)."""

    def handler(progress, ptype, *user_data):
        if callback is None:
            return
        try:
            if ptype == PK.ProgressType.PERCENTAGE:
                pct = progress.get_property("percentage")
                if 0 <= pct <= 100:
                    callback(pct, None)
            elif ptype == PK.ProgressType.STATUS:
                status = progress.get_property("status")
                callback(None, PK.status_enum_to_string(status))
        except Exception:  # progresso nunca deve derrubar a operação
            pass

    return handler


def _run(method, *args, progress=None):
    try:
        results = method(*args, None, _progress(progress), None)
    except GLib.Error as exc:
        raise PackageError(friendly_error(exc.message), exc.message) from exc
    error = results.get_error_code()
    if error is not None:
        details = "%s: %s" % (PK.error_enum_to_string(error.get_code()), error.get_details())
        raise PackageError(friendly_error(details), details)
    return results


def refresh(progress=None):
    _run(_client().refresh_cache, False, progress=progress)


def resolve(names, progress=None):
    """Devolve {nome: {"installed": bool, "id": package_id_preferido}}."""
    names = [n for n in names if n]
    if not names:
        return {}
    results = _run(_client().resolve, _bitfield_filter("none"), names, progress=progress)
    found = {}
    for pkg in results.get_package_array():
        name = pkg.get_name()
        entry = found.setdefault(name, {"installed": False, "id": None})
        if pkg.get_info() == PK.InfoEnum.INSTALLED:
            entry["installed"] = True
            entry["installed_id"] = pkg.get_id()
        elif entry["id"] is None:
            entry["id"] = pkg.get_id()
    return found


def install(names, progress=None):
    info = resolve(names)
    ids = []
    for name in names:
        entry = info.get(name)
        if not entry or (not entry["id"] and not entry["installed"]):
            raise PackageError(_("The package was not found in the configured sources."), name)
        if not entry["installed"]:
            ids.append(entry["id"])
    if ids:
        return _run(_client().install_packages, _trusted(), ids, progress=progress)
    return None


def remove(names, progress=None):
    info = resolve(names)
    ids = [info[n]["installed_id"] for n in names if n in info and info[n]["installed"]]
    if ids:
        return _run(_client().remove_packages, _trusted(), ids, True, True, progress=progress)
    return None


SECURITY_INFOS = {PK.InfoEnum.SECURITY}


def get_updates(progress=None):
    """Lista atualizações: [{id, name, version, summary, security, konaro}]."""
    results = _run(_client().get_updates, _bitfield_filter("none"), progress=progress)
    updates = []
    for pkg in results.get_package_array():
        data = (pkg.get_data() or "").lower()
        updates.append({
            "id": pkg.get_id(),
            "name": pkg.get_name(),
            "version": pkg.get_version(),
            "summary": pkg.get_summary() or "",
            "security": pkg.get_info() in SECURITY_INFOS or "security" in data,
            "konaro": pkg.get_name().startswith("konaro-"),
        })
    return updates


RESTART_HINTS = ("linux-image", "linux-headers", "systemd", "libc6", "nvidia", "firmware-",
                 "dbus", "mesa", "kwin", "plasma-workspace", "intel-microcode", "amd64-microcode")


def may_need_restart(names):
    return any(n.startswith(h) or h in n for n in names for h in RESTART_HINTS)


def update(package_ids, progress=None):
    if not package_ids:
        return False
    results = _run(_client().update_packages, _trusted(), list(package_ids), progress=progress)
    worst = results.get_require_restart_worst()
    return worst in (PK.RestartEnum.SYSTEM, PK.RestartEnum.SECURITY_SYSTEM)
