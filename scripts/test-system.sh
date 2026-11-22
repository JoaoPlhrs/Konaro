#!/bin/sh
# Konaro OS — teste de sistema SEM máquina virtual: inicia o sistema da imagem
# (build/live-work/chroot) com systemd dentro de um contêiner efêmero
# (systemd-nspawn --volatile=overlay: nada é gravado na árvore da imagem) e
# executa verificações reais: serviços, PackageKit, Flatpak, ferramentas Konaro.
#
#   sudo ./scripts/test-system.sh [--proxy http://127.0.0.1:3142]
#
# --proxy: usa um proxy APT HTTP para as operações de rede do PackageKit
#          (somente dentro do contêiner efêmero).
# Requisitos: systemd-container. Saída: build/system-test/ (log + capturas).
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TREE="$ROOT/build/live-work/chroot"
OUT="$ROOT/build/system-test"
PROXY=""
[ "${1:-}" = "--proxy" ] && PROXY="${2:-}"

[ "$(id -u)" -eq 0 ] || { echo "ERRO: execute como root." >&2; exit 1; }
[ -x "$TREE/usr/lib/systemd/systemd" ] || { echo "ERRO: árvore da imagem não encontrada: $TREE" >&2; exit 1; }
command -v systemd-nspawn >/dev/null || { echo "ERRO: instale systemd-container." >&2; exit 1; }
mkdir -p "$OUT"
: > "$OUT/test.log"

NAME="konaro-test-$$"
systemd-nspawn -q --register=no --keep-unit --volatile=overlay -M "$NAME" \
	-D "$TREE" -b systemd.mask=sddm.service systemd.mask=display-manager.service \
	> "$OUT/boot.log" 2>&1 &
NSPAWN=$!
trap 'kill $NSPAWN 2>/dev/null || true; wait $NSPAWN 2>/dev/null || true' EXIT

# PID do systemd (PID 1) do contêiner
LEADER=""
for _i in $(seq 1 60); do
	# procura o processo "systemd" descendente do systemd-nspawn
	for child in $(pgrep -P "$NSPAWN" 2>/dev/null || true); do
		if [ "$(cat "/proc/$child/comm" 2>/dev/null)" = "systemd" ]; then LEADER="$child"; break; fi
		for grandchild in $(pgrep -P "$child" 2>/dev/null || true); do
			if [ "$(cat "/proc/$grandchild/comm" 2>/dev/null)" = "systemd" ]; then LEADER="$grandchild"; break; fi
		done
		[ -n "$LEADER" ] && break
	done
	[ -n "$LEADER" ] && break
	sleep 1
done
[ -n "$LEADER" ] || { echo "ERRO: o sistema não iniciou (veja $OUT/boot.log)" >&2; exit 1; }

run() { nsenter -t "$LEADER" -a env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin HOME=/root LANG=pt_BR.UTF-8 "$@"; }

# Espera o boot terminar
for _i in $(seq 1 120); do
	state="$(run systemctl is-system-running 2>/dev/null || true)"
	case "$state" in running|degraded) break ;; esac
	sleep 2
done

PASS=0; FAIL=0
check() { # descrição, comando...
	desc="$1"; shift
	if run sh -c "$*" >>"$OUT/test.log" 2>&1; then
		echo "  ok    $desc"; PASS=$((PASS + 1))
	else
		echo "  FALHA $desc"; FAIL=$((FAIL + 1))
	fi
}

echo "== Boot: estado do systemd: $(run systemctl is-system-running 2>/dev/null || true)"
run systemctl --failed --no-legend --plain > "$OUT/failed-units.txt" 2>&1 || true
echo "   unidades com falha: $(wc -l < "$OUT/failed-units.txt") (lista em $OUT/failed-units.txt)"

if [ -n "$PROXY" ]; then
	run sh -c "echo 'Acquire::http::Proxy \"$PROXY\";' > /etc/apt/apt.conf.d/99konaro-test-proxy
		sed -i 's#https://deb.debian.org#http://deb.debian.org#; s#https://security.debian.org#http://security.debian.org#' /etc/apt/sources.list /etc/apt/sources.list.d/*.list /etc/apt/sources.list.d/*.sources 2>/dev/null || true
		sed -i 's#https://raw.githubusercontent.com#http://raw.githubusercontent.com#' /etc/apt/sources.list.d/*.sources 2>/dev/null || true
		# No contêiner o NetworkManager não gerencia a rede e o PackageKit se acha offline;
		# sem ele, o PackageKit usa a detecção de rede do kernel.
		systemctl stop NetworkManager; systemctl restart packagekit; sleep 5"
fi

echo "== Serviços"
# O ufw não consegue carregar regras dentro de um contêiner (sem CAP_NET_ADMIN);
# aqui só dá para conferir que o serviço está habilitado para o boot real.
check "ufw (firewall) habilitado no boot" "systemctl is-enabled ufw.service && grep -q '^ENABLED=yes' /etc/ufw/ufw.conf"
check "NetworkManager habilitado" "systemctl is-enabled NetworkManager.service"
check "polkit ativo" "systemctl is-active polkit.service"
check "timer de atualizações habilitado para usuários" "test -e /etc/systemd/user/timers.target.wants/konaro-update-check.timer"

echo "== PackageKit (backend da Loja, Atualizações e Drivers)"
check "PackageKit responde (resolve via biblioteca Konaro)" \
	"python3 -c 'from konaro import packagekit; r = packagekit.resolve([\"dolphin\", \"vlc\"]); print(r); assert r[\"dolphin\"][\"installed\"]'"
if [ -n "$PROXY" ]; then
	check "atualiza índices (refresh)" "python3 -c 'from konaro import packagekit; packagekit.refresh()'"
	check "lista atualizações e classifica (segurança/sistema/Konaro)" \
		"python3 -c 'from konaro import updater; g = updater.check(refresh=False); print({k: len(v) for k, v in g.items()})'"
	check "instala um pacote pela Loja (cowsay)" "python3 -c 'from konaro import packagekit; packagekit.install([\"cowsay\"])' && test -x /usr/games/cowsay"
	check "remove o pacote (cowsay)" "python3 -c 'from konaro import packagekit; packagekit.remove([\"cowsay\"])' && ! test -e /usr/games/cowsay"
fi

echo "== Flatpak"
check "Flathub configurado (HTTPS)" "flatpak remotes --system -d | grep -q 'https://dl.flathub.org/repo/'"
check "biblioteca Konaro lista apps Flatpak" "python3 -c 'from konaro import flatpak; a = flatpak.installed_apps(); print(a); assert a == {} or isinstance(a, dict)'"
check "catálogo do Flathub (AppStream) presente" "test -d /var/lib/flatpak/appstream/flathub/x86_64/active"
check "imagem mínima: só o Firefox de navegador" "! dpkg -s brave-browser >/dev/null 2>&1 && ! flatpak info --system com.valvesoftware.Steam >/dev/null 2>&1"

echo "== 32 bits pronto para jogos"
check "arquitetura i386 habilitada" "dpkg --print-foreign-architectures | grep -qx i386"

echo "== Drivers"
check "análise de hardware (konaro-drivers --list)" "konaro-drivers --list"

echo "== Interfaces (renderização real, tema do sistema)"
for app in store updater drivers welcome; do
	check "konaro-$app abre e renderiza" \
		"QT_QPA_PLATFORM=offscreen timeout 90 konaro-$app --screenshot /tmp/konaro-$app.png; test -s /tmp/konaro-$app.png"
	run cat "/tmp/konaro-$app.png" > "$OUT/konaro-$app.png" 2>/dev/null || true
done

echo "== Resultado: $PASS ok, $FAIL falha(s). Log: $OUT/test.log"
run systemctl poweroff >/dev/null 2>&1 || true
[ "$FAIL" -eq 0 ]
