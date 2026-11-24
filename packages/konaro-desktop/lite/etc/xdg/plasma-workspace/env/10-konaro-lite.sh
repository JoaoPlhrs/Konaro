# Konaro OS Fênix Lite — ajustes da sessão para computadores antigos.
# 1) As configurações leves (/etc/xdg/konaro-lite) têm prioridade sobre as padrão.
case ":${XDG_CONFIG_DIRS:-}:" in
	*:/etc/xdg/konaro-lite:*) ;;
	*) export XDG_CONFIG_DIRS="/etc/xdg/konaro-lite:${XDG_CONFIG_DIRS:-/etc/xdg}" ;;
esac
# 2) Placas de vídeo muito antigas (sem OpenGL 2, ex.: Intel GMA 950): a interface
#    passa a ser desenhada pelo processador, em vez de não abrir.
if command -v glxinfo >/dev/null 2>&1; then
	glv="$(glxinfo -B 2>/dev/null | sed -n 's/^OpenGL version string: \([0-9]*\)\..*/\1/p' | head -n1)"
	if [ -n "$glv" ] && [ "$glv" -lt 2 ]; then
		export QT_QUICK_BACKEND=software
		export KWIN_COMPOSE=N
	fi
fi
