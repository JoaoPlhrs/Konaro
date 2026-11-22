#!/bin/sh
# Konaro OS — atualiza os ícones dos apps do catálogo da Loja
# (packages/konaro-tools/data/store/icons/<id>.png, 128 px).
#
# Fontes: metadados AppStream oficiais — os mesmos que as lojas de apps usam:
#   - Debian:  dists/trixie/{main,contrib}/dep11/icons-128x128.tar.gz
#   - Flathub: ramo appstream do repositório (flatpak update --appstream)
# Os ícones pertencem aos respectivos projetos; são usados só para identificar
# cada app na Loja (ver docs/LICENSES.md).
#
# Uso (num Debian 13 com flatpak e o Flathub configurado):
#   ./scripts/fetch-store-icons.sh [DIR_DE_TRABALHO]
# Variáveis: KONARO_MIRROR (padrão https://deb.debian.org/debian), http_proxy.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CATALOG="$ROOT/packages/konaro-tools/data/store/catalog.json"
OUT="$ROOT/packages/konaro-tools/data/store/icons"
WORK="${1:-$(mktemp -d)}"
MIRROR="${KONARO_MIRROR:-https://deb.debian.org/debian}"
mkdir -p "$OUT" "$WORK/dep11"

for area in main contrib; do
	curl -fsSL -o "$WORK/icons-$area.tar.gz" "$MIRROR/dists/trixie/$area/dep11/icons-128x128.tar.gz"
	tar xzf "$WORK/icons-$area.tar.gz" -C "$WORK/dep11"
done
flatpak update --appstream --system flathub >/dev/null 2>&1 || true
FLATHUB_ICONS=/var/lib/flatpak/appstream/flathub/x86_64/active/icons/128x128

python3 - "$CATALOG" "$WORK/dep11" "$FLATHUB_ICONS" "$OUT" <<'EOF'
import glob, json, os, shutil, sys
catalog, dep11, flathub, out = sys.argv[1:5]
apps = json.load(open(catalog, encoding="utf-8"))["apps"]
missing = []
for app in apps:
    dest = os.path.join(out, app["id"] + ".png")
    if app["backend"] == "flatpak":
        src = os.path.join(flathub, app["app"] + ".png")
        candidates = [src] if os.path.exists(src) else []
    else:
        pkgs = app["packages"]
        candidates = []
        for pkg in pkgs + [pkgs[0] + "-full", pkgs[0] + "-startcenter"]:
            candidates += sorted(glob.glob(os.path.join(dep11, pkg + "_*.png")))
        if app["id"] == "libreoffice":
            candidates = sorted(glob.glob(os.path.join(dep11, "libreoffice-writer_*.png"))) + candidates
    if candidates:
        shutil.copyfile(candidates[0], dest)
    else:
        missing.append(app["id"])
print("ícones copiados:", len(apps) - len(missing), "de", len(apps))
if missing:
    print("sem ícone (usará o do tema):", ", ".join(missing))
EOF
