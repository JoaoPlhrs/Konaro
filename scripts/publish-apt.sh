#!/bin/sh
# Konaro OS — publica os pacotes .deb do Konaro no repositório APT assinado.
#
# O repositório fica na pasta apt/ do repositório do GitHub (JoaoPlhrs/Konaro) e é
# servido por https://raw.githubusercontent.com/JoaoPlhrs/Konaro/main/apt/.
#
# Uso: publish-apt.sh <pasta com os .deb> <checkout do repositório Konaro> <GNUPGHOME>
#   (a chave privada NUNCA vai para o Git; o GNUPGHOME fica guardado pelo responsável)
# Depois: commit + push da pasta apt/ no repositório Konaro.
set -eu
DEBS="$1"; REPO="$2"; export GNUPGHOME="$3"
KEY="CD4DDF983E99F644925B0965AD295A04EFAC9F1F"
APT="$REPO/apt"
POOL="$APT/pool/main"
DIST="$APT/dists/konaro"

mkdir -p "$POOL" "$DIST/main/binary-all" "$DIST/main/binary-amd64" "$DIST/main/binary-i386"
# guarda só a versão mais nova de cada pacote (o repositório fica pequeno)
for deb in "$DEBS"/*.deb; do
	name="$(dpkg-deb -f "$deb" Package)"
	for old in "$POOL/${name}_"*.deb; do
		[ -e "$old" ] && [ "$(basename "$old")" != "$(basename "$deb")" ] && rm -f "$old"
	done
	cp "$deb" "$POOL/"
done

cd "$APT"
# binary-amd64 tem tudo (amd64 + all); binary-all só os pacotes "all"
apt-ftparchive packages pool/main > dists/konaro/main/binary-amd64/Packages
apt-ftparchive --arch all packages pool/main > dists/konaro/main/binary-all/Packages
# binary-i386 (Fênix Lite 32): os pacotes "all" (o efeito de vidro é só amd64)
apt-ftparchive --arch i386 packages pool/main > dists/konaro/main/binary-i386/Packages
for d in binary-all binary-amd64 binary-i386; do
	gzip -9 -n -k -f "dists/konaro/main/$d/Packages"
done
apt-ftparchive \
	-o APT::FTPArchive::Release::Origin="Konaro OS" \
	-o APT::FTPArchive::Release::Label="Konaro OS" \
	-o APT::FTPArchive::Release::Suite="konaro" \
	-o APT::FTPArchive::Release::Codename="konaro" \
	-o APT::FTPArchive::Release::Architectures="amd64 i386 all" \
	-o APT::FTPArchive::Release::Components="main" \
	-o APT::FTPArchive::Release::Description="Konaro OS packages" \
	release dists/konaro > dists/konaro/Release
rm -f dists/konaro/InRelease dists/konaro/Release.gpg
gpg --batch --yes --local-user "$KEY" --clearsign -o dists/konaro/InRelease dists/konaro/Release
gpg --batch --yes --local-user "$KEY" -abs -o dists/konaro/Release.gpg dists/konaro/Release
gpg --export "$KEY" > konaro-archive-keyring.gpg
echo "Repositório atualizado em $APT"
ls -la "$POOL"
