#!/bin/sh
# Konaro OS — verificações automáticas de uma ISO já gerada (sem iniciá-la).
#
#   ./scripts/verify-iso.sh build/iso/konaro-os-*.iso
#
# Confere: estrutura de boot BIOS/UEFI, ausência de resíduos do ambiente de build
# (proxy APT, pins temporários), fontes APT finais, arquivos e serviços Konaro.
# Requisitos: xorriso, squashfs-tools.
# Os helpers ok/bad nunca falham, então "teste && ok || bad" é seguro aqui.
# shellcheck disable=SC2015
set -eu

ISO="${1:?uso: $0 <arquivo.iso>}"
[ -f "$ISO" ] || { echo "ERRO: ISO não encontrada: $ISO" >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
rc=0
ok()   { echo "  ok    $*"; }
bad()  { echo "  FALHA $*"; rc=1; }

echo "==> Estrutura da ISO"
xorriso -indev "$ISO" -find / -type f 2>/dev/null > "$TMP/files"
for f in /live/filesystem.squashfs /live/vmlinuz /live/initrd.img /boot/grub/grub.cfg /EFI/boot/bootx64.efi; do
	# kernel e initrd levam a versão no nome (ex.: /live/vmlinuz-6.12...)
	if grep -q "^'\{0,1\}$f" "$TMP/files"; then ok "$f*"; else bad "ausente: $f"; fi
done
xorriso -indev "$ISO" -report_el_torito plain 2>/dev/null | grep -qi "BIOS" && ok "El Torito BIOS" || bad "sem boot BIOS"
xorriso -indev "$ISO" -report_el_torito plain 2>/dev/null | grep -qi "UEFI" && ok "El Torito UEFI" || bad "sem boot UEFI"
# Secure Boot: o carregador UEFI da ISO tem que ser o shim assinado (não um GRUB sem assinatura)
TMPEFI=$(mktemp -d)
xorriso -osirrox on -indev "$ISO" -extract /EFI/boot "$TMPEFI/boot" >/dev/null 2>&1 || true
if [ -f "$TMPEFI/boot/bootx64.efi" ] && grep -aq "Microsoft Corporation UEFI CA" "$TMPEFI/boot/bootx64.efi"; then
	ok "Secure Boot: bootx64.efi é o shim assinado pela Microsoft"
else
	bad "Secure Boot: bootx64.efi não é o shim assinado"
fi
[ -f "$TMPEFI/boot/grubx64.efi" ] && ok "Secure Boot: GRUB assinado presente (grubx64.efi)" || bad "Secure Boot: grubx64.efi ausente"
rm -r "$TMPEFI"

echo "==> Extraindo arquivos selecionados do squashfs"
xorriso -osirrox on -indev "$ISO" -extract /live/filesystem.squashfs "$TMP/fs.sqfs" >/dev/null 2>&1
xorriso -osirrox on -indev "$ISO" -extract /boot/grub "$TMP/grub" >/dev/null 2>&1
unsquashfs -q -d "$TMP/root" "$TMP/fs.sqfs" \
	etc/apt etc/xdg etc/sddm.conf.d etc/ufw etc/calamares etc/systemd/system/multi-user.target.wants \
	usr/share/plasma/look-and-feel usr/share/calamares/branding usr/share/applications/konaro-install.desktop \
	usr/share/calamares/helpers var/lib/dpkg/status var/lib/dpkg/arch var/lib/flatpak/repo/config \
	usr/share/keyrings/brave-browser-archive-keyring.gpg usr/lib/systemd/user etc/systemd/user >/dev/null 2>&1 || true
unsquashfs -l "$TMP/fs.sqfs" 2>/dev/null > "$TMP/fs.list"
R="$TMP/root"

echo "==> Resíduos do ambiente de build (não podem ir para a imagem)"
if grep -rqsi "proxy" "$R/etc/apt/apt.conf.d/" "$R/etc/apt/apt.conf" 2>/dev/null; then
	bad "configuração de proxy APT encontrada em /etc/apt"
else
	ok "sem proxy APT"
fi
if grep -rqs "konqueror" "$R/etc/apt/preferences.d/" "$R/etc/apt/preferences" 2>/dev/null; then
	bad "pin de build (konqueror) vazou para /etc/apt"
else
	ok "sem pins de build"
fi
if grep -rqs "127.0.0.1" "$R/etc/apt/" 2>/dev/null; then bad "endereço local em /etc/apt"; else ok "sem mirrors locais"; fi

if grep -qs "http://" "$R/var/lib/flatpak/repo/config"; then bad "Flathub configurado com URL HTTP de build"; else ok "Flathub via HTTPS"; fi

echo "==> Fontes APT do sistema final"
cat "$R"/etc/apt/sources.list "$R"/etc/apt/sources.list.d/*.list "$R"/etc/apt/sources.list.d/*.sources 2>/dev/null \
	| grep -Ev '^\s*(#|$)' | sed 's/^/        /'
grep -rqs "https://deb.debian.org/debian" "$R/etc/apt/" && ok "mirror HTTPS oficial" || bad "mirror HTTPS oficial ausente"

echo "==> Identidade Konaro"
grep -q '^LookAndFeelPackage=org.konaro.desktop$' "$R/etc/xdg/kdeglobals" && ok "tema global padrão" || bad "kdeglobals"
[ -f "$R/usr/share/plasma/look-and-feel/org.konaro.desktop/contents/splash/Splash.qml" ] && ok "splash" || bad "splash"
grep -q '^branding: konaro$' "$R/etc/calamares/settings.conf" && ok "Calamares com identidade Konaro" || bad "branding do Calamares"
grep -q "'konaro-installer'" "$R/etc/calamares/modules/packages.conf" && ok "instalador remove konaro-installer" || bad "packages.conf"
grep -q '^ENABLED=yes' "$R/etc/ufw/ufw.conf" && ok "ufw habilitado" || bad "ufw.conf"
[ -L "$R/etc/systemd/system/multi-user.target.wants/ufw.service" ] && ok "ufw.service ativo" || bad "ufw.service"
[ -f "$TMP/grub/splash.png" ] && ok "fundo do menu de boot" || bad "grub splash.png"

echo "==> Navegadores, jogos e ferramentas"
grep -qs "signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg\] https://brave-browser-apt-release.s3.brave.com" "$R"/etc/apt/sources.list.d/*.list \
	&& ok "repositório oficial do Brave (HTTPS + signed-by)" || bad "lista do Brave"
[ -f "$R/usr/share/keyrings/brave-browser-archive-keyring.gpg" ] && ok "chave do Brave" || bad "chave do Brave"
for app in io.github.ungoogled_software.ungoogled_chromium com.valvesoftware.Steam; do
	grep -q "var/lib/flatpak/app/$app/" "$TMP/fs.list" && ok "Flatpak $app" || bad "Flatpak ausente: $app"
done
grep -qx i386 "$R/var/lib/dpkg/arch" && ok "arquitetura i386 (Wine/Steam 32 bits)" || bad "i386 não habilitado"
grep -q 'packagechooser@browsers' "$R/etc/calamares/settings.conf" && ok "instalador: página Navegadores" || bad "página Navegadores"
grep -q '^  - konarobrowsers$' "$R/etc/calamares/settings.conf" && ok "instalador: aplica escolha de navegadores" || bad "konarobrowsers"
grep -q 'contrib non-free non-free-firmware' "$R/usr/share/calamares/helpers/calamares-sources-final" && ok "fontes finais com contrib/non-free" || bad "sources-final"
[ -f "$R/usr/lib/systemd/user/konaro-update-check.timer" ] && ok "timer de verificação de atualizações" || bad "timer do atualizador"

echo "==> Visual Konaro"
for f in usr/share/plasma/plasmoids/org.konaro.dock/contents/ui/main.qml usr/share/plasma/desktoptheme/konaro/plasmarc \
	usr/share/aurorae/themes/Konaro/decoration.svg usr/share/plasma/plasmoids/org.kde.plasma.notes/metadata.json \
	usr/lib/python3/dist-packages/konaro/qml/store/Main.qml usr/share/konaro/installer/browser-brave.png; do
	grep -q "$f" "$TMP/fs.list" && ok "$f" || bad "ausente: $f"
done

echo "==> Pacotes"
for p in konaro-desktop konaro-installer konaro-common konaro-store konaro-updater konaro-drivers konaro-welcome konaro-gaming \
	plasma-workspace kwin-wayland sddm calamares dolphin linux-image-amd64 packagekit \
	firefox-esr brave-browser wine lutris steam-devices gamemode mangohud; do
	if awk -v p="$p" '$1=="Package:"{n=$2} $1=="Status:" && n==p && /installed/{f=1} END{exit !f}' "$R/var/lib/dpkg/status"; then
		ok "$p"
	else
		bad "não instalado: $p"
	fi
done
for p in chromium konqueror falkon; do
	if awk -v p="$p" '$1=="Package:"{n=$2} $1=="Status:" && n==p && /installed/{f=1} END{exit !f}' "$R/var/lib/dpkg/status"; then
		bad "navegador fora da lista decidida: $p"
	fi
done
echo "        total de pacotes: $(grep -c '^Status: install ok installed' "$R/var/lib/dpkg/status")"

echo "==> Tamanho: $(du -h "$ISO" | cut -f1)"
[ "$rc" -eq 0 ] && echo "==> verify-iso: OK" || echo "==> verify-iso: FALHOU"
exit "$rc"
