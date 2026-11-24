#!/bin/sh
# Konaro OS — gera a identidade do sistema (os-release, issue) a partir da versão.
# O sistema se apresenta como Konaro OS; ID_LIKE=debian e VERSION_CODENAME=trixie
# mantêm a compatibilidade com programas e repositórios feitos para o Debian 13.
#
# Gera duas identidades: a normal e a da edição Lite (para computadores antigos).
# O postinst do konaro-desktop escolhe qual vale conforme /etc/konaro/edition.
# Uso: make-os-release.sh VERSAO NOME_DA_VERSAO DIRETORIO_DE_SAIDA
set -eu
V="$1"
NAME="$2"
OUT="$3"
mkdir -p "$OUT"

write() {   # write SUFIXO_DO_ARQUIVO EDICAO VARIANT_ID
	cat > "$OUT/os-release$1" <<EOF
PRETTY_NAME="Konaro OS $NAME$2"
NAME="Konaro OS"
VERSION_ID="${V%%-*}"
VERSION="$V ($NAME$2)"
VERSION_CODENAME=trixie
ID=konaro
ID_LIKE=debian
VARIANT="$NAME$2"
VARIANT_ID=$3
LOGO=konaro
ANSI_COLOR="1;37"
HOME_URL="https://joaoplhrs.github.io/Konaro/"
SUPPORT_URL="https://github.com/JoaoPlhrs/Konaro"
BUG_REPORT_URL="https://github.com/JoaoPlhrs/Konaro/issues"
EOF
	printf 'Konaro OS %s%s \\n \\l\n\n' "$NAME" "$2" > "$OUT/issue$1"
	printf 'Konaro OS %s%s\n' "$NAME" "$2" > "$OUT/issue.net$1"
}
write "" "" standard
write "-lite" " Lite" lite
