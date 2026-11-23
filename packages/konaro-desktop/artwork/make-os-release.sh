#!/bin/sh
# Konaro OS — gera a identidade do sistema (os-release, issue) a partir da versão.
# O sistema se apresenta como Konaro OS; ID_LIKE=debian e VERSION_CODENAME=trixie
# mantêm a compatibilidade com programas e repositórios feitos para o Debian 13.
# Uso: make-os-release.sh VERSAO DIRETORIO_DE_SAIDA
set -eu
V="$1"
OUT="$2"
mkdir -p "$OUT"
cat > "$OUT/os-release" <<EOF
PRETTY_NAME="Konaro OS"
NAME="Konaro OS"
VERSION_ID="${V%%-*}"
VERSION="$V"
VERSION_CODENAME=trixie
ID=konaro
ID_LIKE=debian
LOGO=konaro
ANSI_COLOR="1;37"
HOME_URL="https://joaoplhrs.github.io/Konaro/"
SUPPORT_URL="https://github.com/JoaoPlhrs/Konaro"
BUG_REPORT_URL="https://github.com/JoaoPlhrs/Konaro/issues"
EOF
printf 'Konaro OS \\n \\l\n\n' > "$OUT/issue"
printf 'Konaro OS\n' > "$OUT/issue.net"
