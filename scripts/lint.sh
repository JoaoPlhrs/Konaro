#!/bin/sh
# Konaro OS — verificações estáticas rápidas (não precisam de root).
# Requisitos: shellcheck, python3. Opcional: qmllint (qt6-declarative-dev-tools).
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
rc=0

echo "==> shellcheck"
shellcheck -s sh scripts/*.sh live/auto/* live/config/hooks/normal/*.hook.chroot live/editions/*/config/hooks/normal/*.hook.chroot packages/konaro-installer/data/usr/lib/live/config/* || rc=1

echo "==> JSON"
find packages -name '*.json' -exec python3 -m json.tool {} \; >/dev/null || { echo "JSON inválido"; rc=1; }

echo "==> Arte compartilhada idêntica entre pacotes"
cmp packages/konaro-desktop/artwork/konaro-logo.svg packages/konaro-installer/artwork/konaro-logo.svg \
	|| { echo "konaro-logo.svg divergiu entre konaro-desktop e konaro-installer"; rc=1; }

echo "==> Listas de pacotes sem duplicatas"
dups="$(grep -hv '^#' live/config/package-lists/*.list.* | grep -v '^$' | sort | uniq -d)"
[ -z "$dups" ] || { echo "Duplicados: $dups"; rc=1; }

echo "==> Python: compilação e testes das ferramentas Konaro"
python3 -m py_compile packages/konaro-tools/src/konaro/*.py packages/konaro-installer/data/usr/lib/calamares/modules/konarofonts/main.py || rc=1
if python3 -c 'import gi; gi.require_version("PackageKitGlib", "1.0")' 2>/dev/null; then
	PYTHONPATH=packages/konaro-tools/src python3 -m unittest discover -s packages/konaro-tools/tests -q || rc=1
else
	echo "   (testes pulados: instale python3-gi e gir1.2-packagekitglib-1.0)"
fi

if command -v qmllint >/dev/null 2>&1 || [ -x /usr/lib/qt6/bin/qmllint ]; then
	echo "==> qmllint (avisos de import de módulos KDE são esperados fora do Plasma)"
	QMLLINT="$(command -v qmllint || echo /usr/lib/qt6/bin/qmllint)"
	find packages -name '*.qml' -exec "$QMLLINT" {} \; || true
fi

[ "$rc" -eq 0 ] && echo "==> lint OK" || echo "==> lint FALHOU"
exit "$rc"
