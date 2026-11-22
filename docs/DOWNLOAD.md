# Download e instalação

1. Abra a [versão mais recente](https://github.com/JoaoPlhrs/Konaro/releases/latest) e baixe **todas** as partes `konaro-os-…iso.partNN`.
2. Junte as partes na mesma pasta:
   - **Windows** (Prompt de Comando): `copy /b konaro-os-0.1.0-dev1-amd64.iso.part00+konaro-os-0.1.0-dev1-amd64.iso.part01+… konaro-os-0.1.0-dev1-amd64.iso` (todas as partes, em ordem)
   - **Linux / macOS**: `cat konaro-os-0.1.0-dev1-amd64.iso.part* > konaro-os-0.1.0-dev1-amd64.iso`
3. Confira o SHA-256 (tem que ser igual ao da release):
   - Windows (PowerShell): `Get-FileHash konaro-os-0.1.0-dev1-amd64.iso -Algorithm SHA256`
   - Linux: `sha256sum konaro-os-0.1.0-dev1-amd64.iso`
4. **Máquina virtual (recomendado)**: VirtualBox → Linux / Debian 64-bit, 4 GB+ de RAM, 2 CPUs, disco de 30 GB, vídeo VMSVGA com 128 MB.
5. **Pendrive**: Ventoy, Rufus (modo DD) ou balenaEtcher. ⚠️ Escolher o disco errado apaga os dados dele. Desative o Secure Boot.

Sessão live: usuário `konaro`, senha `live`.
