#!/bin/sh
# Konaro OS — ambiente de build Debian 13 isolado (chroot), para hosts que
# não são Debian trixie (Ubuntu, WSL2 com Ubuntu, outras distros).
#
#   sudo ./scripts/builder-chroot.sh setup      # cria o chroot (uma vez)
#   sudo ./scripts/builder-chroot.sh build-iso  # roda scripts/build-iso.sh lá dentro
#   sudo ./scripts/builder-chroot.sh shell      # shell interativo no chroot
#   sudo ./scripts/builder-chroot.sh umount     # desmonta /proc, /sys, /dev, projeto
#
# Variáveis: KONARO_BUILDER (padrão /srv/konaro-builder), KONARO_MIRROR,
#            KONARO_APT_PROXY (repassado ao build e ao apt do chroot).
# Requisitos no host: debootstrap, debian-archive-keyring.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILDER="${KONARO_BUILDER:-/srv/konaro-builder}"
MIRROR="${KONARO_MIRROR:-http://deb.debian.org/debian}"
SECURITY_MIRROR="${KONARO_SECURITY_MIRROR:-http://security.debian.org/debian-security}"
KEYRING=/usr/share/keyrings/debian-archive-keyring.gpg
PROJECT_MNT=/konaro-os

[ "$(id -u)" -eq 0 ] || { echo "ERRO: execute como root (sudo)." >&2; exit 1; }

in_chroot() {
	chroot "$BUILDER" /usr/bin/env -i \
		HOME=/root TERM="${TERM:-xterm}" LANG=C.UTF-8 \
		PATH=/usr/sbin:/usr/bin:/sbin:/bin \
		DEBIAN_FRONTEND=noninteractive \
		KONARO_MIRROR="$MIRROR" KONARO_SECURITY_MIRROR="$SECURITY_MIRROR" \
		KONARO_APT_PROXY="${KONARO_APT_PROXY:-}" \
		KONARO_BRAVE_MIRROR="${KONARO_BRAVE_MIRROR:-}" \
		KONARO_LIVE_LOCALE="${KONARO_LIVE_LOCALE:-}" \
		KONARO_LIVE_KEYBOARD="${KONARO_LIVE_KEYBOARD:-}" \
		KONARO_LIVE_TIMEZONE="${KONARO_LIVE_TIMEZONE:-}" \
		"$@"
}

do_mount() {
	for d in proc sys dev dev/pts; do
		mountpoint -q "$BUILDER/$d" || mount --bind "/$d" "$BUILDER/$d"
	done
	mkdir -p "$BUILDER$PROJECT_MNT"
	mountpoint -q "$BUILDER$PROJECT_MNT" || mount --bind "$ROOT" "$BUILDER$PROJECT_MNT"
	cp /etc/resolv.conf "$BUILDER/etc/resolv.conf"
}

do_umount() {
	for d in "$PROJECT_MNT" dev/pts dev sys proc; do
		d="${d#/}"
		if mountpoint -q "$BUILDER/$d"; then umount -l "$BUILDER/$d"; fi
	done
}

do_setup() {
	command -v debootstrap >/dev/null 2>&1 || { echo "ERRO: instale debootstrap." >&2; exit 1; }
	[ -r "$KEYRING" ] || { echo "ERRO: instale debian-archive-keyring ($KEYRING)." >&2; exit 1; }
	if [ ! -x "$BUILDER/usr/bin/apt-get" ]; then
		echo "==> debootstrap trixie em $BUILDER"
		mkdir -p "$BUILDER"
		debootstrap --keyring="$KEYRING" --variant=minbase --include=ca-certificates \
			trixie "$BUILDER" "$MIRROR"
	fi
	cat > "$BUILDER/etc/apt/sources.list" <<-EOF
	deb $MIRROR trixie main contrib non-free non-free-firmware
	deb $MIRROR trixie-updates main contrib non-free non-free-firmware
	deb $SECURITY_MIRROR trixie-security main contrib non-free non-free-firmware
	EOF
	if [ -n "${KONARO_APT_PROXY:-}" ]; then
		echo "Acquire::http::Proxy \"$KONARO_APT_PROXY\";" > "$BUILDER/etc/apt/apt.conf.d/01konaro-proxy"
	else
		rm -f "$BUILDER/etc/apt/apt.conf.d/01konaro-proxy"
	fi
	do_mount
	echo "==> Instalando ferramentas de build no chroot"
	in_chroot sh -c 'apt-get update -q && apt-get install -y -q --no-install-recommends \
		live-build debootstrap dpkg-dev debhelper librsvg2-bin xorriso \
		squashfs-tools mtools dosfstools ca-certificates shellcheck python3'
	echo "==> Builder pronto: $BUILDER"
}

case "${1:-}" in
	setup)     do_setup ;;
	build-iso) shift; do_mount; in_chroot "$PROJECT_MNT/scripts/build-iso.sh" "$@" ;;
	shell)     do_mount; in_chroot bash -l ;;
	run)       shift; do_mount; in_chroot "$@" ;;
	umount)    do_umount ;;
	*) sed -n '2,13p' "$0"; exit 2 ;;
esac
