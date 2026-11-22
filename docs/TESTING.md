# Como testar

> Nunca teste o instalador num disco real sem backup. Os scripts deste repositório só
> usam **arquivos de imagem** (`build/vm/disk.qcow2`); nenhum deles grava em `/dev/*`.

## Teste de sistema sem VM (systemd-nspawn)
Inicia o sistema da imagem recém-construída com systemd, num contêiner efêmero (nada é
gravado), e testa serviços, PackageKit (incluindo instalar/remover um pacote), Flatpak,
Wine/Steam/Lutris, análise de drivers e a renderização das quatro ferramentas Konaro:
```sh
sudo apt install systemd-container
sudo ./scripts/test-system.sh                 # resultado e capturas em build/system-test/
```

## Máquina virtual (QEMU)
```sh
sudo apt install qemu-system-x86 qemu-utils ovmf
./scripts/test-vm.sh build/iso/konaro-os-*.iso              # BIOS
./scripts/test-vm.sh --uefi build/iso/konaro-os-*.iso       # UEFI
./scripts/test-vm.sh --uefi --disk 30G build/iso/...iso     # com disco virtual para o instalador
./scripts/test-vm.sh --uefi --boot-disk                     # iniciar o sistema instalado
```
Com `/dev/kvm` a VM é rápida. Sem KVM (ex.: dentro de outra VM ou contêiner) o QEMU usa
emulação TCG: funciona, mas o desktop leva vários minutos para aparecer.

Modo sem janela, com capturas periódicas (usado nos testes automatizados):
```sh
./scripts/test-vm.sh --headless --interval 60 --duration 1200 build/iso/...iso
```

VirtualBox/VMware também funcionam: crie uma VM Linux 64 bits com 4 GB de RAM,
EFI ligado ou desligado, e use a ISO como CD.

## Pendrive (hardware real)
A ISO é *hybrid*: pode ser gravada num pendrive com Ventoy, Rufus (modo DD),
balenaEtcher ou GNOME Disks. **Escolher o dispositivo errado apaga os dados dele.**
Lembre-se de desativar o Secure Boot (ver decisions/0006).

## Roteiro manual mínimo (sessão live)
1. Menu de boot com a identidade Konaro: "Português (Brasil)", "English" e modo de
   compatibilidade de vídeo; inicia sozinho em 5 segundos.
2. Splash de boas-vindas ("Olá", "Hello"... "Welcome to Konaro").
3. Abre o assistente **Boas-vindas** (com o botão "Instalar o Konaro OS").
4. Desktop: barra superior (logo, menu global, bandeja, relógio) e dock centralizado com
   Instalar, Dolphin, navegador, Loja, Steam, Lutris, Configurações e Lixeira.
5. A tela não bloqueia nem apaga sozinha na sessão live.
6. **Loja**: categorias, busca, detalhes com permissões; instalar e remover um app (requer internet).
7. **Atualizações**, **Drivers**: abrem e analisam o sistema.
8. Firefox, Brave e Ungoogled Chromium abrem; Steam e Lutris abrem.
9. Configurações > Aparência > Tema global: **Konaro Claro** ↔ **Konaro Escuro**.
10. Configurações > Firewall: ativo.
11. "Instalar o Konaro OS": Calamares com identidade Konaro e página **Navegadores**.

## Instalação (disco virtual)
1. `./scripts/test-vm.sh --uefi --disk 30G <iso>` e instalar com "Apagar disco".
2. Reiniciar com `--boot-disk`, criar usuário no instalador e entrar.
3. Conferir: layout Konaro aplicado, Boas-vindas abre uma vez, só os navegadores escolhidos
   estão instalados, Calamares removido, `apt update` funciona (Debian + Brave, se escolhido).
