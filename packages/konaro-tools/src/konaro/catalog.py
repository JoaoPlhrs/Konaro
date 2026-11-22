"""Catálogo completo da Loja: todos os apps do Debian e do Flathub (AppStream).

A página Início continua curada (catalog.json); a busca e as categorias somam a
ela o catálogo completo, lido dos metadados AppStream que já estão no sistema:
- Debian: /var/lib/swcatalog (baixado pelo apt junto com as listas de pacotes);
- Flathub: /var/lib/flatpak/appstream/flathub/x86_64/active (baixado pelo Flatpak).
Tudo é lido localmente; ícones remotos só são mostrados se houver internet.
"""

import os
import threading

from .i18n import _

FLATHUB_DATA = "/var/lib/flatpak/appstream/flathub/x86_64/active"
CATEGORY_MAP = {
    "games": ["Game"],
    "internet": ["Network", "WebBrowser", "Email", "Chat"],
    "productivity": ["Office"],
    "multimedia": ["AudioVideo", "Audio", "Video"],
    "graphics": ["Graphics"],
    "development": ["Development"],
    "utilities": ["Utility", "System"],
}
_lock = threading.Lock()
_pool = None


def _appstream():
    import gi
    gi.require_version("AppStream", "1.0")
    from gi.repository import AppStream
    return AppStream


def pool():
    """Carrega (uma vez) o catálogo AppStream do sistema + Flathub."""
    global _pool
    with _lock:
        if _pool is None:
            AppStream = _appstream()
            p = AppStream.Pool()
            if os.path.isdir(FLATHUB_DATA):
                p.add_extra_data_location(FLATHUB_DATA, AppStream.FormatStyle.CATALOG)
            p.load(None)
            _pool = p
        return _pool


def _category(cats):
    for ours, theirs in CATEGORY_MAP.items():
        if any(c in theirs for c in cats):
            return ours
    return "utilities"


def _icon(component):
    AppStream = _appstream()
    best, name = None, None
    for ic in component.get_icons():
        kind = ic.get_kind()
        if kind == AppStream.IconKind.CACHED or kind == AppStream.IconKind.LOCAL:
            path = ic.get_filename()
            if path and os.path.exists(path):
                if best is None or ic.get_width() > best[1]:
                    best = (path, ic.get_width())
        elif kind == AppStream.IconKind.STOCK:
            name = ic.get_name()
        elif kind == AppStream.IconKind.REMOTE and best is None:
            url = ic.get_url()
            if url and url.startswith("https://"):
                best = (url, ic.get_width())
    if best:
        return best[0]
    return name or "application-x-executable"


def to_app(component):
    """Converte um componente AppStream no formato de app da Loja (ou None)."""
    AppStream = _appstream()
    if component.get_kind() != AppStream.ComponentKind.DESKTOP_APP:
        return None
    name = component.get_name()
    if not name:
        return None
    bundle = component.get_bundle(AppStream.BundleKind.FLATPAK)
    pkg = component.get_pkgname()
    app = {"name": name, "summaryText": component.get_summary() or "", "icon": _icon(component),
           "category": _category(component.get_categories() or []), "featured": False, "full": True}
    launch = component.get_launchable(AppStream.LaunchableKind.DESKTOP_ID)
    desktop = launch.get_entries()[0] if launch and launch.get_entries() else ""
    # atalhos "como root" e variantes duplicadas não interessam a quem está começando
    if desktop.endswith("-root.desktop") or "(as root)" in name or "(root)" in name:
        return None
    if bundle is not None:
        ref = bundle.get_id()                    # app/org.example.App/x86_64/stable
        parts = ref.split("/")
        flat_id = parts[1] if len(parts) > 1 else component.get_id()
        app.update({"id": flat_id, "backend": "flatpak", "app": flat_id, "origin": "flathub"})
    elif pkg:
        app.update({"id": "deb:" + pkg, "backend": "apt", "packages": [pkg], "origin": "debian", "desktop": desktop})
    else:
        return None
    return app


def _decorate(app):
    from .store import CATEGORY_NAMES, ORIGINS
    app["originText"] = _(ORIGINS[app["origin"]])
    app["formatText"] = _("Flatpak (isolated)") if app["backend"] == "flatpak" else _("Debian package (.deb)")
    app["categoryText"] = _(CATEGORY_NAMES.get(app["category"], app["category"]))
    return app


def _collect(box, limit, skip):
    out, seen = [], set(skip)
    for i in range(box.get_size()):
        app = to_app(box.index_safe(i))
        if not app:
            continue
        key = app["packages"][0] if app["backend"] == "apt" else app["app"]
        if app["id"] in seen or key in seen:
            continue
        seen.update((app["id"], key))
        out.append(_decorate(app))
        if len(out) >= limit:
            break
    return out


def search(query, limit=60, skip=()):
    query = (query or "").strip()
    if len(query) < 2:
        return []
    return _collect(pool().search(query), limit, skip)


def browse(category, limit=80, skip=()):
    cats = CATEGORY_MAP.get(category)
    if not cats:
        return []
    apps = _collect(pool().get_components_by_categories(cats), limit * 3, skip)
    apps.sort(key=lambda a: a["name"].lower())
    return apps[:limit]
