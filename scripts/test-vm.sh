#!/bin/sh
# Konaro OS — inicia a ISO numa máquina virtual QEMU (nunca toca em discos reais).
#
#   ./scripts/test-vm.sh [opções] build/iso/konaro-os-*.iso
#
# Opções:
#   --uefi               firmware UEFI (OVMF) em vez de BIOS
#   --disk SIZE          cria/usa um disco virtual build/vm/disk.qcow2 (ex.: 30G),
#                        para testar o instalador. Só arquivos de imagem, nunca /dev/*.
#   --boot-disk          inicia pelo disco virtual (testar o sistema já instalado)
#   --ram MB             memória da VM (padrão 4096)
#   --cpu MODELO         modelo de processador do QEMU (ex.: coreduo = Core Duo de 32 bits,
#                        para testar a edição Fênix Lite 32)
#   --headless           sem janela; grava capturas de tela periódicas
#   --shots DIR          diretório das capturas (padrão build/vm/shots)
#   --interval SEC       intervalo entre capturas (padrão 30)
#   --duration SEC       duração total no modo headless (padrão 900)
#
# Requisitos: qemu-system-x86, qemu-utils; para --uefi: ovmf.
# Sem /dev/kvm, a VM roda em emulação pura (TCG): funciona, mas é MUITO mais lenta.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VMDIR="$ROOT/build/vm"
UEFI=0; SECURE=0; DISK=""; BOOT_DISK=0; RAM=4096; HEADLESS=0; CPU=""
SHOTS="$VMDIR/shots"; INTERVAL=30; DURATION=900; ISO=""

while [ $# -gt 0 ]; do
	case "$1" in
		--uefi) UEFI=1 ;;
		--secure-boot) UEFI=1; SECURE=1 ;;
		--disk) DISK="$2"; shift ;;
		--boot-disk) BOOT_DISK=1 ;;
		--ram) RAM="$2"; shift ;;
		--cpu) CPU="$2"; shift ;;
		--headless) HEADLESS=1 ;;
		--shots) SHOTS="$2"; shift ;;
		--interval) INTERVAL="$2"; shift ;;
		--duration) DURATION="$2"; shift ;;
		-h|--help) sed -n '2,20p' "$0"; exit 0 ;;
		*) ISO="$1" ;;
	esac
	shift
done

if [ "$BOOT_DISK" -eq 0 ]; then
	if [ -z "$ISO" ] || [ ! -f "$ISO" ]; then
		echo "ERRO: informe o caminho da ISO." >&2; exit 2
	fi
fi
mkdir -p "$VMDIR"

set -- -m "$RAM" -smp 2 -device virtio-vga -device qemu-xhci -device usb-tablet \
	-netdev user,id=n0 -device virtio-net-pci,netdev=n0 \
	-audiodev none,id=snd0 -device intel-hda -device hda-output,audiodev=snd0

if [ -w /dev/kvm ]; then
	set -- "$@" -enable-kvm -cpu "${CPU:-host}"
else
	echo "AVISO: /dev/kvm indisponível — usando emulação TCG (lenta)." >&2
	# Com "-cpu max" sob TCG, o renderizador por software do Mesa (llvmpipe) chegou a
	# derrubar o KWin (falha dentro do código JIT); uma CPU sem AVX é mais estável.
	set -- "$@" -accel tcg,thread=multi -cpu "${CPU:-Nehalem}"
fi

if [ "$UEFI" -eq 1 ]; then
	CODE=""; VARS_TEMPLATE=""
	for c in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/ovmf/OVMF.fd; do
		[ -f "$c" ] && { CODE="$c"; break; }
	done
	for v in /usr/share/OVMF/OVMF_VARS_4M.fd /usr/share/OVMF/OVMF_VARS.fd; do
		[ -f "$v" ] && { VARS_TEMPLATE="$v"; break; }
	done
	if [ "${SECURE:-0}" -eq 1 ]; then
		# firmware com Secure Boot ligado e as chaves da Microsoft já registradas
		CODE=/usr/share/OVMF/OVMF_CODE_4M.secboot.fd; VARS_TEMPLATE=/usr/share/OVMF/OVMF_VARS_4M.ms.fd
		if [ ! -f "$CODE" ] || [ ! -f "$VARS_TEMPLATE" ]; then
			echo "ERRO: OVMF com Secure Boot não encontrado." >&2; exit 1
		fi
		rm -f "$VMDIR/OVMF_VARS.fd"; cp "$VARS_TEMPLATE" "$VMDIR/OVMF_VARS.fd"
		set -- "$@" -machine q35,smm=on -global driver=cfi.pflash01,property=secure,value=on \
			-drive if=pflash,format=raw,unit=0,readonly=on,file="$CODE" \
			-drive if=pflash,format=raw,unit=1,file="$VMDIR/OVMF_VARS.fd"
	else
	[ -n "$CODE" ] || { echo "ERRO: OVMF não encontrado (apt install ovmf)." >&2; exit 1; }
	[ -f "$VMDIR/OVMF_VARS.fd" ] || cp "$VARS_TEMPLATE" "$VMDIR/OVMF_VARS.fd"
	set -- "$@" -machine q35 \
		-drive if=pflash,format=raw,readonly=on,file="$CODE" \
		-drive if=pflash,format=raw,file="$VMDIR/OVMF_VARS.fd"
	fi
else
	set -- "$@" -machine q35
fi

if [ -n "$DISK" ] || [ "$BOOT_DISK" -eq 1 ]; then
	if [ ! -f "$VMDIR/disk.qcow2" ]; then
		qemu-img create -f qcow2 "$VMDIR/disk.qcow2" "${DISK:-30G}" >/dev/null
		echo "Disco virtual criado: $VMDIR/disk.qcow2"
	fi
	set -- "$@" -drive file="$VMDIR/disk.qcow2",if=virtio,format=qcow2
fi

if [ "$BOOT_DISK" -eq 0 ]; then
	set -- "$@" -drive file="$ISO",media=cdrom,readonly=on -boot order=d
else
	set -- "$@" -boot order=c
fi

if [ "$HEADLESS" -eq 0 ]; then
	exec qemu-system-x86_64 "$@"
fi

# ---- modo headless: capturas de tela periódicas via monitor do QEMU
mkdir -p "$SHOTS"
MON="$VMDIR/monitor.sock"
rm -f "$MON"
qemu-system-x86_64 "$@" -display none -monitor unix:"$MON",server,nowait \
	-serial file:"$VMDIR/serial.log" &
QPID=$!
trap 'kill $QPID 2>/dev/null || true' EXIT INT TERM

elapsed=0
while [ "$elapsed" -lt "$DURATION" ] && kill -0 "$QPID" 2>/dev/null; do
	sleep "$INTERVAL"
	elapsed=$((elapsed + INTERVAL))
	shot="$SHOTS/$(printf '%05d' "$elapsed")s.ppm"
	if command -v socat >/dev/null 2>&1; then
		echo "screendump $shot" | socat - UNIX-CONNECT:"$MON" >/dev/null 2>&1 || true
	else
		python3 - "$MON" "$shot" <<-'EOF'
		import socket, sys, time
		s = socket.socket(socket.AF_UNIX); s.connect(sys.argv[1])
		time.sleep(0.2); s.recv(65536)
		s.sendall(("screendump %s\n" % sys.argv[2]).encode()); time.sleep(1); s.close()
		EOF
	fi
	echo "[$elapsed s] captura: $shot"
done
echo "Fim do teste headless. Capturas em $SHOTS (formato PPM)."
