# Como construir a ISO do Konaro OS

## Requisitos
- **Debian 13 "trixie"** (máquina, VM ou chroot) com acesso root, **ou** outro Linux
  usando o chroot de build (abaixo).
- ~25 GB livres em disco, 4 GB+ de RAM, internet (baixa ~2 GB de pacotes no 1º build).

## Opção A — Host Debian 13
```sh
sudo apt install live-build debhelper dpkg-dev librsvg2-bin xorriso shellcheck
./scripts/lint.sh
sudo ./scripts/build-iso.sh          # ou: sudo make iso
```

## Opção B — Outro Linux (Ubuntu, WSL2...) via chroot Debian 13
```sh
sudo apt install debootstrap debian-archive-keyring
sudo ./scripts/builder-chroot.sh setup        # uma vez (cria /srv/konaro-builder)
sudo ./scripts/builder-chroot.sh build-iso    # constrói a ISO lá dentro
sudo ./scripts/builder-chroot.sh umount       # ao terminar
```

## Resultado
```
build/iso/konaro-os-<versão>-amd64.hybrid.iso
build/iso/konaro-os-<versão>-amd64.hybrid.iso.sha256
build/iso/konaro-os-<versão>-amd64.packages      # lista completa de pacotes
build/iso/build.log
```

## O que o build faz
1. `scripts/build-packages.sh` constrói os `.deb` de `packages/` (renderiza a arte SVG).
2. Copia `live/` para `build/live-work/` (a árvore do Git nunca recebe arquivos gerados).
3. Coloca os `.deb` em `config/packages.chroot/` e a arte do menu de boot em `config/bootloaders/`.
4. `lb config` (opções em `live/auto/config`) e `lb build`.
5. Hooks em `live/config/hooks/normal/` ativam o firewall, aplicam a identidade ao
   Calamares e **verificam** que os arquivos essenciais do Konaro estão no lugar.

## Variáveis úteis
| Variável | Padrão | Uso |
|---|---|---|
| `KONARO_APT_PROXY` | (vazio) | Proxy/cache HTTP para o APT durante o build (ex.: `http://127.0.0.1:3142` do apt-cacher-ng) |
| `KONARO_MIRROR` | `http://deb.debian.org/debian` | Mirror usado durante o build |
| `KONARO_LIVE_LOCALE` | `pt_BR.UTF-8` | Idioma da sessão live (provisório) |
| `KONARO_LIVE_KEYBOARD` | `br` | Teclado da sessão live (provisório) |
| `KONARO_LIVE_TIMEZONE` | `America/Sao_Paulo` | Fuso da sessão live (provisório) |

O APT verifica as assinaturas GPG do Debian em qualquer caso. A ISO final sempre aponta
para `https://deb.debian.org` e `https://security.debian.org`.

## Builds seguintes
O cache de pacotes fica em `build/live-work/cache/`; builds seguintes baixam só o que mudou.
`sudo ./scripts/build-iso.sh --clean` descarta tudo (inclusive o cache).
`sudo ./scripts/build-iso.sh --resume` continua um build que falhou num hook (depois de
corrigi-lo), sem reinstalar os pacotes. Não use `--resume` se mudou pacotes Konaro.

## Rede necessária no build
`deb.debian.org`, `security.debian.org`, `brave-browser-apt-release.s3.brave.com`
(Brave) e `dl.flathub.org` (Ungoogled Chromium e Steam via Flatpak).
