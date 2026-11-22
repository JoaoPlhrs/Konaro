#!/bin/sh
# Konaro OS — constrói os pacotes .deb próprios (packages/*) em build/packages/.
#
# Requisitos (Debian 13): dpkg-dev debhelper librsvg2-bin
# Cada pacote é construído numa cópia temporária, para não sujar a árvore do Git.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build/packages"
WORK="$ROOT/build/pkg-work"

for tool in dpkg-buildpackage dh rsvg-convert; do
	command -v "$tool" >/dev/null 2>&1 || {
		echo "ERRO: '$tool' não encontrado. Instale: dpkg-dev debhelper librsvg2-bin" >&2
		exit 1
	}
done

mkdir -p "$OUT"
rm -f "$OUT"/*.deb "$OUT"/*.buildinfo "$OUT"/*.changes

for dir in "$ROOT"/packages/*/; do
	name="$(basename "$dir")"
	[ -f "$dir/debian/control" ] || continue
	echo "==> Construindo $name"
	rm -rf "${WORK:?}/$name"
	mkdir -p "$WORK"
	cp -a "$dir" "$WORK/$name"
	(cd "$WORK/$name" && dpkg-buildpackage -b -us -uc --no-sign >"$WORK/$name.log" 2>&1) || {
		echo "ERRO ao construir $name. Últimas linhas do log ($WORK/$name.log):" >&2
		tail -n 30 "$WORK/$name.log" >&2
		exit 1
	}
	mv "$WORK"/*.deb "$OUT"/
	rm -f "$WORK"/*.buildinfo "$WORK"/*.changes
done

echo "==> Pacotes prontos em $OUT:"
ls -1 "$OUT"
