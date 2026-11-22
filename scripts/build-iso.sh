#!/bin/sh
# Konaro OS — gera a ISO live/instalável com Debian Live Build.
#
# Uso (como root, num Debian 13 "trixie" ou dentro de scripts/builder-chroot.sh):
#   sudo ./scripts/build-iso.sh            # build incremental (reaproveita cache)
#   sudo ./scripts/build-iso.sh --clean    # descarta diretório de trabalho e cache antes
#   sudo ./scripts/build-iso.sh --resume   # continua um build interrompido (após corrigir
#                                          # um hook), sem refazer os estágios concluídos
#
# Variáveis opcionais: KONARO_MIRROR, KONARO_SECURITY_MIRROR, KONARO_APT_PROXY, KONARO_BRAVE_MIRROR,
# KONARO_LIVE_LOCALE, KONARO_LIVE_KEYBOARD, KONARO_LIVE_TIMEZONE (ver live/auto/config).
#
# Saída: build/iso/konaro-os-<versão>-amd64.hybrid.iso + .sha256 + .packages
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/build/live-work"
ISO_OUT="$ROOT/build/iso"

if [ "$(id -u)" -ne 0 ]; then
	echo "ERRO: o live-build precisa ser executado como root (use sudo)." >&2
	exit 1
fi
command -v lb >/dev/null 2>&1 || { echo "ERRO: live-build não instalado (apt install live-build)." >&2; exit 1; }

if [ -r /etc/os-release ]; then
	# shellcheck source=/dev/null
	. /etc/os-release
	if [ "${ID:-}" != "debian" ] || [ "${VERSION_CODENAME:-}" != "trixie" ]; then
		echo "AVISO: host não é Debian 13 (trixie). O caminho testado é usar" >&2
		echo "       scripts/builder-chroot.sh. Continuando mesmo assim..." >&2
	fi
fi

if [ "${1:-}" = "--clean" ] && [ -d "$WORK" ]; then
	echo "==> Limpando diretório de trabalho (inclui o cache de pacotes)"
	if cd "$WORK"; then lb clean --purge >/dev/null 2>&1 || true; cd "$ROOT"; fi
	rm -rf "${WORK:?}"
fi

RESUME=0
[ "${1:-}" = "--resume" ] && RESUME=1

if [ "$RESUME" -eq 0 ]; then
	echo "==> 1/4 Pacotes próprios"
	"$ROOT/scripts/build-packages.sh"
else
	echo "==> 1/4 Pacotes próprios: mantidos do build anterior (--resume)"
fi

echo "==> 2/4 Preparando diretório de trabalho do live-build: $WORK"
mkdir -p "$WORK"
# Copia a configuração versionada; o que o lb gera (chroot, binary, cache) fica só em $WORK.
rm -rf "$WORK/auto" "$WORK/config"
cp -a "$ROOT/live/auto" "$WORK/auto"
cp -a "$ROOT/live/config" "$WORK/config"
cp "$ROOT/VERSION" "$ROOT/build/VERSION"
mkdir -p "$WORK/config/packages.chroot"
cp "$ROOT"/build/packages/*.deb "$WORK/config/packages.chroot/"
# Repositório oficial do Brave: lista de build (pode usar um mirror/proxy HTTP via
# KONARO_BRAVE_MIRROR) e lista final do sistema (sempre HTTPS + signed-by).
BRAVE_URL="${KONARO_BRAVE_MIRROR:-https://brave-browser-apt-release.s3.brave.com}"
echo "deb [arch=amd64] ${BRAVE_URL}/ stable main" > "$WORK/config/archives/brave.list.chroot"
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
	> "$WORK/config/archives/brave.list.binary"
# A splash do menu de boot vem do pacote konaro-desktop (fonte única da arte)
cp "$ROOT/packages/konaro-desktop/artwork/grub-splash.svg" "$WORK/config/bootloaders/splash.svg"

echo "==> 3/4 lb config && lb build (isso pode levar de 20 a 60 minutos)"
cd "$WORK"
[ "$RESUME" -eq 1 ] || lb clean >/dev/null 2>&1 || true
lb config
lb build

echo "==> 4/4 Publicando artefatos em $ISO_OUT"
mkdir -p "$ISO_OUT"
for iso in "$WORK"/*.iso; do
	[ -e "$iso" ] || { echo "ERRO: nenhuma ISO gerada (veja $WORK/build.log)" >&2; exit 1; }
	base="$(basename "$iso")"
	mv "$iso" "$ISO_OUT/$base"
	(cd "$ISO_OUT" && sha256sum "$base" > "$base.sha256")
	echo "    $ISO_OUT/$base ($(du -h "$ISO_OUT/$base" | cut -f1))"
done
for list in "$WORK"/*.packages; do
	[ -e "$list" ] && cp "$list" "$ISO_OUT/"
done
cp "$WORK/build.log" "$ISO_OUT/build.log"
echo "==> Concluído. Teste com: ./scripts/test-vm.sh $ISO_OUT/<arquivo>.iso"
