# Konaro OS — numa máquina virtual, sem desligar a tela nem suspender por inatividade
# (/etc/xdg/konaro-vm). Num computador de verdade, a economia de energia é a normal.
if command -v systemd-detect-virt >/dev/null 2>&1 && systemd-detect-virt --vm --quiet; then
	case ":${XDG_CONFIG_DIRS:-}:" in
		*:/etc/xdg/konaro-vm:*) ;;
		*) export XDG_CONFIG_DIRS="/etc/xdg/konaro-vm:${XDG_CONFIG_DIRS:-/etc/xdg}" ;;
	esac
fi
