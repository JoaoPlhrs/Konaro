"""Apps de fora dos repositórios: pacotes .deb soltos, AppImage e GitHub Releases.

- .deb: instalado pelo PackageKit (pede a senha de administrador pelo polkit),
  que também baixa as dependências que faltarem.
- AppImage: vai para ~/Aplicativos (ou ~/Applications), vira executável e ganha
  um atalho no menu com o ícone e o nome do próprio app. Não precisa de senha.
- GitHub Releases: a Loja busca a versão mais recente publicada pelo projeto e
  escolhe o arquivo certo (.deb amd64 ou AppImage x86_64).

Também serve de "abrir com" para arquivos .deb e .AppImage (konaro-install-file).
"""

import configparser
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request

from .i18n import _
from .packagekit import PackageError

STATE = os.path.expanduser("~/.local/share/konaro/store-installed.json")
DOWNLOADS = os.path.expanduser("~/.cache/konaro/downloads")
DESKTOP_DIR = os.path.expanduser("~/.local/share/applications")
ICON_DIR = os.path.expanduser("~/.local/share/icons/konaro-appimage")
UA = "KonaroStore/1.0"


# ------------------------------------------------------------------ estado
def load_state():
    try:
        with open(STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=1)
    os.replace(tmp, STATE)


def apps_dir():
    """Pasta dos AppImage: segue o idioma das pastas do usuário."""
    for name in ("Aplicativos", "Applications"):
        path = os.path.expanduser("~/" + name)
        if os.path.isdir(path):
            return path
    lang = os.environ.get("LANG", "")
    path = os.path.expanduser("~/Aplicativos" if lang.startswith("pt") else "~/Applications")
    os.makedirs(path, exist_ok=True)
    return path


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "app"


# ------------------------------------------------------------------ .deb
def deb_info(path):
    """Campos do pacote (.deb) sem instalar nada."""
    try:
        out = subprocess.run(["dpkg-deb", "-f", path, "Package", "Version", "Description", "Architecture"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise PackageError(_("This file is not a valid .deb package."), str(exc)) from exc
    info = {}
    for line in out.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            info[key.strip()] = value.strip()
    return info


def install_deb(path, progress=None):
    """Instala um .deb local pelo PackageKit (resolve dependências)."""
    from .packagekit import _client, _run
    info = deb_info(path)
    arch = info.get("Architecture", "")
    if arch not in ("amd64", "all", "i386", ""):
        raise PackageError(_("This package is for another kind of processor ({arch}).").format(arch=arch), arch)
    _run(_client().install_files, 0, [os.path.abspath(path)], progress=progress)
    return info.get("Package", "")


def deb_desktop_file(package):
    """O atalho (.desktop) que um pacote instalado colocou no menu, se houver."""
    try:
        files = subprocess.run(["dpkg", "-L", package], capture_output=True, text=True).stdout.split()
    except OSError:
        return ""
    found = [f for f in files if f.startswith("/usr/share/applications/") and f.endswith(".desktop")]
    return found[0] if found else ""


def remove_deb(package, progress=None):
    from . import packagekit
    return packagekit.remove([package], progress=progress)


# ------------------------------------------------------------------ AppImage
def _squashfs_offset(path):
    """Onde começa o sistema de arquivos dentro do AppImage (fim do cabeçalho ELF)."""
    with open(path, "rb") as fh:
        head = fh.read(64)
    if head[:4] != b"\x7fELF":
        raise PackageError(_("This file is not a valid AppImage."), "no ELF header")
    if head[4] == 2:   # 64 bits
        shoff, = struct.unpack_from("<Q", head, 0x28)
        shentsize, shnum = struct.unpack_from("<HH", head, 0x3A)
    else:
        shoff, = struct.unpack_from("<I", head, 0x20)
        shentsize, shnum = struct.unpack_from("<HH", head, 0x2E)
    return shoff + shentsize * shnum


def _appimage_meta(path):
    """Lê o .desktop e o ícone de dentro do AppImage SEM executá-lo."""
    meta = {"name": os.path.basename(path).split(".AppImage")[0].split("-")[0], "icon": "application-x-executable",
            "categories": "Utility;", "comment": ""}
    if not shutil.which("unsquashfs"):
        return meta
    try:
        offset = _squashfs_offset(path)
    except (OSError, PackageError, struct.error):
        return meta
    work = tempfile.mkdtemp(prefix="konaro-appimage-")
    try:
        listing = subprocess.run(["unsquashfs", "-o", str(offset), "-lc", path],
                                 capture_output=True, text=True, timeout=60).stdout.splitlines()
        names = [ln.strip().split("squashfs-root/", 1)[1] for ln in listing if "squashfs-root/" in ln]
        root = [p for p in names if "/" not in p]
        desktops = [p for p in root if p.endswith(".desktop")]
        wanted = desktops[:1] + [p for p in root if p == ".DirIcon" or p.endswith((".png", ".svg"))]
        if wanted:
            subprocess.run(["unsquashfs", "-o", str(offset), "-f", "-d", work, path] + wanted,
                           capture_output=True, timeout=120)
        if desktops:
            cfg = configparser.ConfigParser(interpolation=None, strict=False)
            cfg.optionxform = str
            cfg.read(os.path.join(work, desktops[0]), encoding="utf-8")
            if cfg.has_section("Desktop Entry"):
                entry = cfg["Desktop Entry"]
                meta["name"] = entry.get("Name", meta["name"])
                meta["comment"] = entry.get("Comment", "")
                meta["categories"] = entry.get("Categories", meta["categories"])
                icon_name = entry.get("Icon", "")
                for cand in (icon_name + ".png", icon_name + ".svg", ".DirIcon"):
                    src = os.path.join(work, cand)
                    if cand and os.path.isfile(src) and not os.path.islink(src):
                        os.makedirs(ICON_DIR, exist_ok=True)
                        ext = ".svg" if cand.endswith(".svg") else ".png"
                        dest = os.path.join(ICON_DIR, slug(meta["name"]) + ext)
                        shutil.copyfile(src, dest)
                        meta["icon"] = dest
                        break
    except (OSError, subprocess.SubprocessError):
        pass
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return meta


def install_appimage(path, progress=None, move=True):
    """Coloca o AppImage na pasta de aplicativos e cria o atalho do menu.

    Devolve o caminho do atalho (.desktop) criado."""
    meta = _appimage_meta(path)
    if progress:
        progress(40, None)
    name = slug(meta["name"])
    dest = os.path.join(apps_dir(), meta["name"].replace("/", "-") + ".AppImage")
    if os.path.abspath(path) != os.path.abspath(dest):
        if move:
            shutil.move(path, dest)
        else:
            shutil.copyfile(path, dest)
    os.chmod(dest, 0o755)
    os.makedirs(DESKTOP_DIR, exist_ok=True)
    desktop = os.path.join(DESKTOP_DIR, "konaro-appimage-%s.desktop" % name)
    with open(desktop, "w", encoding="utf-8") as fh:
        fh.write("[Desktop Entry]\nType=Application\n")
        fh.write("Name=%s\n" % meta["name"])
        if meta["comment"]:
            fh.write("Comment=%s\n" % meta["comment"])
        fh.write('Exec="%s" %%U\n' % dest)
        fh.write("Icon=%s\n" % meta["icon"])
        fh.write("Categories=%s\n" % meta["categories"])
        fh.write("Terminal=false\nX-Konaro-AppImage=%s\n" % dest)
    subprocess.run(["update-desktop-database", DESKTOP_DIR], capture_output=True)
    if progress:
        progress(100, None)
    return desktop


def remove_appimage(desktop, progress=None):
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.optionxform = str
    cfg.read(desktop, encoding="utf-8")
    target = cfg.get("Desktop Entry", "X-Konaro-AppImage", fallback="")
    icon = cfg.get("Desktop Entry", "Icon", fallback="")
    for f in (target, desktop, icon if icon.startswith(ICON_DIR) else ""):
        if f and os.path.isfile(f):
            os.remove(f)


# ------------------------------------------------------------------ GitHub Releases
def pick_asset(assets, prefer=("deb", "appimage")):
    """Escolhe o arquivo para PC comum (x86-64) entre os publicados no release."""
    def ok_arch(n):
        return not re.search(r"arm64|aarch64|armhf|armv7|i386|i686|\.sha|\.sig|\.zsync|\.blockmap", n)

    kinds = {
        "deb": [a for a in assets if a["name"].lower().endswith(".deb") and ok_arch(a["name"].lower())],
        "appimage": [a for a in assets if a["name"].lower().endswith(".appimage") and ok_arch(a["name"].lower())],
    }
    for kind in prefer:
        found = kinds.get(kind) or []
        found.sort(key=lambda a: ("amd64" not in a["name"] and "x86_64" not in a["name"], len(a["name"])))
        if found:
            return kind, found[0]
    return None, None


def latest_release(repo):
    req = urllib.request.Request("https://api.github.com/repos/%s/releases/latest" % repo,
                                 headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except OSError as exc:
        raise PackageError(_("Could not reach the app's download page. Check the internet."), str(exc)) from exc


def download(url, name, progress=None):
    os.makedirs(DOWNLOADS, exist_ok=True)
    dest = os.path.join(DOWNLOADS, os.path.basename(name))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest + ".part", "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = resp.read(1 << 16)
                if not chunk:
                    break
                out.write(chunk)
                done += len(chunk)
                if progress and total:
                    progress(int(done * 80 / total), None)   # download = 80% da barra
    except OSError as exc:
        raise PackageError(_("The download failed. Check the internet and try again."), str(exc)) from exc
    os.replace(dest + ".part", dest)
    return dest


def install_github(app, progress=None):
    """Baixa o release mais recente do projeto e instala. Devolve o registro do estado."""
    release = latest_release(app["repo"])
    kind, asset = pick_asset(release.get("assets", []), tuple(app.get("prefer", ("deb", "appimage"))))
    if not asset:
        raise PackageError(_("This version of the app has no file for Linux PCs."), release.get("tag_name", ""))
    path = download(asset["browser_download_url"], asset["name"], progress)

    def rest(pct, status):
        if progress and pct is not None:
            progress(80 + pct // 5, status)

    if kind == "deb":
        record = {"kind": "deb", "package": install_deb(path, rest)}
        os.remove(path)
    else:
        record = {"kind": "appimage", "desktop": install_appimage(path, rest)}
    record["version"] = release.get("tag_name", "")
    state = load_state()
    state[app["id"]] = record
    save_state(state)
    return record


def remove_github(app, progress=None):
    state = load_state()
    record = state.get(app["id"])
    if not record:
        return
    if record["kind"] == "deb":
        remove_deb(record["package"], progress)
    else:
        remove_appimage(record["desktop"], progress)
    state.pop(app["id"], None)
    save_state(state)


def installed_github(apps):
    """{app_id: registro} dos apps do GitHub que ainda estão instalados."""
    state = load_state()
    result = {}
    for app_id, rec in state.items():
        if rec.get("kind") == "appimage" and not os.path.isfile(rec.get("desktop", "")):
            continue
        if rec.get("kind") == "deb" and not os.path.exists("/var/lib/dpkg/info/%s.list" % rec.get("package", "-")) \
                and not os.path.exists("/var/lib/dpkg/info/%s:amd64.list" % rec.get("package", "-")):
            continue
        result[app_id] = rec
    return result


# ------------------------------------------------------------------ abrir com (dois cliques)
def _kdialog(*args):
    return subprocess.run(["kdialog", "--title", _("Install app")] + list(args)).returncode == 0


def main(argv=None):
    """konaro-install-file ARQUIVO — instala um .deb ou .AppImage com dois cliques."""
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("uso: konaro-install-file ARQUIVO.deb|ARQUIVO.AppImage", file=sys.stderr)
        return 2
    path = os.path.abspath(argv[0])
    lower = path.lower()
    try:
        if lower.endswith(".deb"):
            info = deb_info(path)
            name = info.get("Package", os.path.basename(path))
            text = _("Install “{name}” {version}?\n\n{desc}\n\nOnly install files from sites you trust: "
                     "a package can change anything in the system. Your password will be asked.").format(
                name=name, version=info.get("Version", ""), desc=info.get("Description", "").split("\n")[0])
            if not _kdialog("--yes-label", _("Install"), "--no-label", _("Cancel"), "--yesno", text):
                return 0
            subprocess.Popen(["kdialog", "--title", _("Install app"), "--passivepopup",
                              _("Installing {name}…").format(name=name), "8"])
            install_deb(path)
            _kdialog("--msgbox", _("{name} was installed. You will find it in the apps menu.").format(name=name))
        elif lower.endswith(".appimage"):
            meta_name = os.path.basename(path)
            text = _("Add “{name}” to your apps?\n\nThe file goes to the Applications folder in your home and "
                     "gets an icon in the apps menu. Only use files from sites you trust.").format(name=meta_name)
            if not _kdialog("--yes-label", _("Add to apps"), "--no-label", _("Just run it once"), "--yesno", text):
                os.chmod(path, os.stat(path).st_mode | 0o755)
                os.execv(path, [path])
            desktop = install_appimage(path)
            _kdialog("--msgbox", _("Done! The app is in the apps menu."))
            cfg = configparser.ConfigParser(interpolation=None, strict=False)
            cfg.optionxform = str
            cfg.read(desktop, encoding="utf-8")
            target = cfg.get("Desktop Entry", "X-Konaro-AppImage", fallback="")
            if target:
                subprocess.Popen([target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
        else:
            _kdialog("--sorry", _("This kind of file cannot be installed here."))
            return 1
    except PackageError as exc:
        _kdialog("--detailedsorry", str(exc.args[0]), str(exc.args[1]) if len(exc.args) > 1 else "")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
