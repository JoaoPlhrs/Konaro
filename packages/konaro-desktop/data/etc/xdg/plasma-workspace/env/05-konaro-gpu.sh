# Konaro OS — sem aceleração 3D (renderizador por software: llvmpipe/softpipe), a
# sessão usa o modo leve (/etc/xdg/konaro-software): sem vidro nem efeitos pesados.
# Com placa de vídeo de verdade, nada muda.
if command -v glxinfo >/dev/null 2>&1; then
	case "$(glxinfo -B 2>/dev/null | sed -n 's/^OpenGL renderer string: //p' | head -n1)" in
		*llvmpipe*|*softpipe*|*"Software Rasterizer"*)
			case ":${XDG_CONFIG_DIRS:-}:" in
				*:/etc/xdg/konaro-software:*) ;;
				*) export XDG_CONFIG_DIRS="/etc/xdg/konaro-software:${XDG_CONFIG_DIRS:-/etc/xdg}" ;;
			esac ;;
	esac
fi
