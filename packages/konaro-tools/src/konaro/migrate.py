"""Migração do Windows — traz documentos, fotos, músicas, vídeos, favoritos e o papel
de parede de uma instalação do Windows no mesmo computador.

Segurança:
- a partição do Windows é montada SOMENTE PARA LEITURA (udisks, sem senha de root);
  nada é alterado, apagado ou movido nela;
- os arquivos vão para uma subpasta "Do Windows" dentro de cada pasta do usuário,
  sem sobrescrever nada que já exista;
- antes de copiar, conferimos se há espaço livre suficiente.
"""

import argparse
import html
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from .i18n import _
from .launcher import launch
from .worker import Worker, WorkerPool

SUBFOLDER = "Do Windows"
SKIP_USERS = {"public", "default", "default user", "all users", "defaultapppool", "wdagutilityaccount"}

# id, pasta no Windows, pasta XDG de destino, nome, ícone
FOLDERS = [
    ("documents", "Documents", "DOCUMENTS", "Documents", "folder-documents"),
    ("desktop", "Desktop", "DESKTOP", "Desktop", "user-desktop"),
    ("downloads", "Downloads", "DOWNLOAD", "Downloads", "folder-download"),
    ("pictures", "Pictures", "PICTURES", "Pictures", "folder-pictures"),
    ("music", "Music", "MUSIC", "Music", "folder-music"),
    ("videos", "Videos", "VIDEOS", "Videos", "folder-videos"),
]
BROWSERS = [
    ("Microsoft Edge", ["AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Bookmarks"]),
    ("Google Chrome", ["AppData", "Local", "Google", "Chrome", "User Data", "Default", "Bookmarks"]),
    ("Brave", ["AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Default", "Bookmarks"]),
]
WALLPAPER = ["AppData", "Roaming", "Microsoft", "Windows", "Themes", "TranscodedWallpaper"]


class MigrateError(Exception):
    pass


# ------------------------------------------------------------------ partições
def _run(cmd, timeout=60):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def ntfs_partitions():
    """Partições NTFS do computador (lsblk)."""
    try:
        out = _run(["lsblk", "-J", "-b", "-o", "PATH,FSTYPE,LABEL,SIZE,MOUNTPOINT"]).stdout
        data = json.loads(out)
    except (OSError, subprocess.SubprocessError, ValueError):
        return []
    found = []

    def walk(nodes):
        for n in nodes:
            if (n.get("fstype") or "").lower() in ("ntfs", "ntfs3"):
                found.append({"device": n["path"], "label": n.get("label") or "", "size": int(n.get("size") or 0),
                              "mountpoint": n.get("mountpoint") or ""})
            walk(n.get("children") or [])
    walk(data.get("blockdevices", []))
    return found


def mount_readonly(device):
    """Monta a partição só para leitura via udisks e devolve o ponto de montagem."""
    res = _run(["udisksctl", "mount", "--no-user-interaction", "-b", device, "-o", "ro"])
    if res.returncode != 0:
        msg = (res.stderr or res.stdout).strip()
        if "already mounted" in msg.lower():
            for p in ntfs_partitions():
                if p["device"] == device and p["mountpoint"]:
                    return p["mountpoint"]
        raise MigrateError(_("Could not open the Windows drive. Shut Windows down completely "
                             "(turn off Fast Startup) and try again."))
    # "Mounted /dev/sda3 at /media/user/Windows"
    text = res.stdout.strip().rstrip(".")
    return text.split(" at ", 1)[1] if " at " in text else ""


def unmount(device):
    _run(["udisksctl", "unmount", "--no-user-interaction", "-b", device])


def is_windows(root):
    return os.path.isdir(os.path.join(root, "Windows", "System32")) and os.path.isdir(os.path.join(root, "Users"))


def windows_users(root):
    users_dir = os.path.join(root, "Users")
    try:
        names = sorted(os.listdir(users_dir))
    except OSError:
        return []
    return [n for n in names if n.lower() not in SKIP_USERS
            and os.path.isdir(os.path.join(users_dir, n)) and not n.startswith(".")]


# ------------------------------------------------------------------- tamanhos
def folder_size(path, limit_files=200000):
    total, count = 0, 0
    for base, dirs, files in os.walk(path, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith("$")]
        for f in files:
            try:
                total += os.lstat(os.path.join(base, f)).st_size
            except OSError:
                pass
            count += 1
            if count > limit_files:
                return total, count
    return total, count


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("%.0f %s" % (n, unit)) if unit in ("B", "KB") else ("%.1f %s" % (n, unit))
        n /= 1024.0


def xdg_dir(kind):
    try:
        out = _run(["xdg-user-dir", kind], timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    return out or os.path.expanduser("~")


# ------------------------------------------------------------ favoritos (HTML)
def _chromium_to_entries(node, out):
    if node.get("type") == "url":
        out.append(("link", node.get("name", ""), node.get("url", "")))
    elif node.get("type") == "folder" or "children" in node:
        out.append(("open", node.get("name", ""), ""))
        for child in node.get("children", []):
            _chromium_to_entries(child, out)
        out.append(("close", "", ""))


def chromium_bookmarks(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    entries = []
    for root_name in ("bookmark_bar", "other", "synced"):
        node = data.get("roots", {}).get(root_name)
        if node and node.get("children"):
            _chromium_to_entries(node, entries)
    return entries


def firefox_bookmarks(places):
    """Lê os favoritos do places.sqlite (cópia temporária; o original fica intocado)."""
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "places.sqlite")
        shutil.copy2(places, copy)
        con = sqlite3.connect(copy)
        rows = con.execute("SELECT b.title, p.url FROM moz_bookmarks b JOIN moz_places p ON p.id = b.fk "
                           "WHERE b.type = 1 AND p.url LIKE 'http%'").fetchall()
        con.close()
    return [("open", "Firefox", "")] + [("link", t or u, u) for t, u in rows] + [("close", "", "")]


def write_bookmarks_html(groups, dest):
    """Arquivo de favoritos no formato padrão (Netscape), que qualquer navegador importa."""
    lines = ["<!DOCTYPE NETSCAPE-Bookmark-file-1>",
             '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
             "<TITLE>Bookmarks</TITLE>", "<H1>Favoritos do Windows</H1>", "<DL><p>"]
    for title, entries in groups:
        lines.append("<DT><H3>%s</H3>" % html.escape(title))
        lines.append("<DL><p>")
        for kind, name, url in entries:
            if kind == "link":
                lines.append('<DT><A HREF="%s">%s</A>' % (html.escape(url, quote=True), html.escape(name or url)))
            elif kind == "open":
                lines.append("<DT><H3>%s</H3>" % html.escape(name))
                lines.append("<DL><p>")
            elif kind == "close":
                lines.append("</DL><p>")
        lines.append("</DL><p>")
    lines.append("</DL><p>")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def find_bookmarks(user_dir):
    found = []
    for name, parts in BROWSERS:
        path = os.path.join(user_dir, *parts)
        if os.path.isfile(path):
            found.append((name, "chromium", path))
    profiles = os.path.join(user_dir, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")
    if os.path.isdir(profiles):
        for prof in sorted(os.listdir(profiles)):
            places = os.path.join(profiles, prof, "places.sqlite")
            if os.path.isfile(places):
                found.append(("Firefox", "firefox", places))
                break
    return found


# ------------------------------------------------------------------- análise
def scan_user(root, user):
    """O que dá para trazer deste usuário do Windows (com tamanhos)."""
    user_dir = os.path.join(root, "Users", user)
    items = []
    for fid, win_name, xdg, label, icon in FOLDERS:
        src = os.path.join(user_dir, win_name)
        if os.path.isdir(src):
            size, count = folder_size(src)
            if count:
                items.append({"id": fid, "name": label, "icon": icon, "size": size, "count": count,
                              "source": src, "xdg": xdg})
    marks = find_bookmarks(user_dir)
    if marks:
        items.append({"id": "bookmarks", "name": "Bookmarks", "icon": "bookmarks", "size": 0,
                      "count": len(marks), "browsers": [m[0] for m in marks], "sources": marks})
    wp = os.path.join(user_dir, *WALLPAPER)
    if os.path.isfile(wp):
        items.append({"id": "wallpaper", "name": "Wallpaper", "icon": "preferences-desktop-wallpaper",
                      "size": os.path.getsize(wp), "count": 1, "source": wp})
    return items


def _unique(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 2
    while os.path.exists("%s (%d)%s" % (base, n, ext)):
        n += 1
    return "%s (%d)%s" % (base, n, ext)


def copy_items(items, home=None, progress=None, dest_for=None):
    """Copia os itens escolhidos. Nunca sobrescreve; erros de arquivos isolados são contados."""
    dest_for = dest_for or xdg_dir
    total = sum(i.get("size", 0) for i in items) or 1
    free = shutil.disk_usage(home or os.path.expanduser("~")).free
    if total > free - 512 * 1024 * 1024:
        raise MigrateError(_("Not enough free space: you need {need}, but only {free} is free.").format(
            need=human(total), free=human(free)))
    done, copied, skipped = 0, 0, 0
    report = {}
    for item in items:
        if item["id"] in [f[0] for f in FOLDERS]:
            dest_root = os.path.join(dest_for(item["xdg"]), SUBFOLDER)
            for base, dirs, files in os.walk(item["source"], onerror=lambda e: None):
                dirs[:] = [d for d in dirs if not d.startswith("$")]
                rel = os.path.relpath(base, item["source"])
                target_dir = os.path.normpath(os.path.join(dest_root, rel))
                os.makedirs(target_dir, exist_ok=True)
                for f in files:
                    src = os.path.join(base, f)
                    if f.lower() in ("desktop.ini", "thumbs.db"):
                        continue
                    try:
                        size = os.lstat(src).st_size
                        if os.path.islink(src):
                            continue
                        shutil.copy2(src, _unique(os.path.join(target_dir, f)))
                        copied += 1
                    except OSError:
                        skipped += 1
                        size = 0
                    done += size
                    if progress:
                        progress(min(99.0, done * 100.0 / total), item["name"])
            report[item["id"]] = dest_root
        elif item["id"] == "bookmarks":
            groups = []
            for name, kind, path in item["sources"]:
                try:
                    groups.append((name, chromium_bookmarks(path) if kind == "chromium" else firefox_bookmarks(path)))
                except (OSError, ValueError, sqlite3.Error):
                    skipped += 1
            if groups:
                dest = _unique(os.path.join(dest_for("DOCUMENTS"), "Favoritos do Windows.html"))
                write_bookmarks_html(groups, dest)
                report["bookmarks"] = dest
        elif item["id"] == "wallpaper":
            dest = _unique(os.path.join(dest_for("PICTURES"), "Papel de parede do Windows.jpg"))
            shutil.copy2(item["source"], dest)
            done += item["size"]
            report["wallpaper"] = dest
    if progress:
        progress(100.0, "")
    return {"copied": copied, "skipped": skipped, "paths": report}


# ---------------------------------------------------------------- interface
DEMO = {"device": "/dev/nvme0n1p3", "label": "Windows", "users": ["Ana"], "root": "/demo"}


class MigrateBridge(QObject):
    changed = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, demo=False):
        super().__init__()
        self._demo = demo
        self._state = "scanning"   # scanning | none | choose | copying | done
        self._message = ""
        self._windows = []         # [{device, label, root}]
        self._users = []
        self._items = []
        self._progress = -1.0
        self._status = ""
        self._result = {}
        self._device = ""
        self._root = ""
        self._pool = WorkerPool()

    def _set(self, state, message=""):
        self._state, self._message = state, message
        self.changed.emit()

    @pyqtProperty(str, notify=changed)
    def state(self):
        return self._state

    @pyqtProperty(str, notify=changed)
    def message(self):
        return self._message

    @pyqtProperty("QVariantList", notify=changed)
    def users(self):
        return self._users

    @pyqtProperty("QVariantList", notify=changed)
    def items(self):
        out = []
        for i in self._items:
            detail = (_("{n} files").format(n=i["count"]) + " · " + human(i["size"])) if i["id"] not in ("bookmarks", "wallpaper") \
                else (", ".join(i.get("browsers", [])) if i["id"] == "bookmarks" else human(i["size"]))
            out.append({"id": i["id"], "name": _(i["name"]), "icon": i["icon"], "detail": detail})
        return out

    @pyqtProperty(float, notify=changed)
    def progress(self):
        return self._progress

    @pyqtProperty(str, notify=changed)
    def status(self):
        return self._status

    @pyqtProperty("QVariantMap", notify=changed)
    def result(self):
        return self._result

    @pyqtProperty(str, notify=changed)
    def windowsName(self):
        return self._windows[0]["label"] if self._windows else ""

    # ---- 1. procurar o Windows
    @pyqtSlot()
    def scan(self):
        if self._demo:
            self._windows = [{"device": DEMO["device"], "label": "Windows", "root": DEMO["root"]}]
            self._users = DEMO["users"]
            self._items = [
                {"id": "documents", "name": "Documents", "icon": "folder-documents", "size": 1_800_000_000, "count": 2310},
                {"id": "desktop", "name": "Desktop", "icon": "user-desktop", "size": 240_000_000, "count": 58},
                {"id": "pictures", "name": "Pictures", "icon": "folder-pictures", "size": 12_400_000_000, "count": 8420},
                {"id": "music", "name": "Music", "icon": "folder-music", "size": 3_100_000_000, "count": 640},
                {"id": "bookmarks", "name": "Bookmarks", "icon": "bookmarks", "size": 0, "count": 2,
                 "browsers": ["Microsoft Edge", "Google Chrome"]},
                {"id": "wallpaper", "name": "Wallpaper", "icon": "preferences-desktop-wallpaper", "size": 420_000, "count": 1},
            ]
            self._set("choose")
            return
        self._set("scanning")
        self._pool.start(Worker(self._find, with_progress=False), ok=self._found, fail=self._fail)

    def _find(self):
        result = []
        for part in ntfs_partitions():
            mounted_here = not part["mountpoint"]
            try:
                root = part["mountpoint"] or mount_readonly(part["device"])
            except MigrateError:
                continue
            if root and is_windows(root):
                result.append({"device": part["device"], "label": part["label"] or "Windows", "root": root,
                               "users": windows_users(root)})
            elif mounted_here:
                unmount(part["device"])
        return result

    def _found(self, result):
        self._windows = result
        if not result:
            self._set("none")
            return
        self._device, self._root = result[0]["device"], result[0]["root"]
        self._users = result[0]["users"]
        if not self._users:
            self._set("none")
            return
        self.chooseUser(self._users[0])

    @pyqtSlot(str)
    def chooseUser(self, user):
        if self._demo:
            return
        self._set("scanning")
        self._pool.start(Worker(scan_user, self._root, user, with_progress=False),
                         ok=self._scanned, fail=self._fail)

    def _scanned(self, items):
        self._items = items
        self._set("choose" if items else "none")

    # ---- 2. copiar
    @pyqtSlot("QVariantList")
    def start(self, ids):
        chosen = [i for i in self._items if i["id"] in ids]
        if not chosen:
            return
        self._progress, self._status = 0.0, ""
        self._set("copying")
        if self._demo:
            return
        self._pool.start(Worker(copy_items, chosen), ok=self._copied, fail=self._fail, progress=self._on_progress)

    def _on_progress(self, pct, status):
        if pct is not None:
            self._progress = float(pct)
        if status:
            self._status = _(status)
        self.changed.emit()

    def _copied(self, result):
        self._result = {"copied": result["copied"], "skipped": result["skipped"]}
        if self._device:
            unmount(self._device)
        self._set("done")

    def _fail(self, message, details=""):
        self._set("error", message)

    @pyqtSlot()
    def openFiles(self):
        launch("dolphin", os.path.join(xdg_dir("DOCUMENTS"), SUBFOLDER))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-migrate")
    parser.add_argument("--demo", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    from .qmlapp import run
    bridge = MigrateBridge(demo=args.demo)
    bridge.scan()
    return run("konaro-migrate", _("Bring from Windows"), "migrate/Main.qml",
               context={"migrate": bridge}, screenshot=args.screenshot, size=(860, 640))


if __name__ == "__main__":
    sys.exit(main())
