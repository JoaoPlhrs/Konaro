# Licenças — inventário inicial

> **Atenção:** a licença dos componentes **originais** do Konaro ainda **não foi escolhida**
> (decisão pendente do responsável). Até lá, a ISO e os pacotes são apenas para
> desenvolvimento e testes internos e **não devem ser publicados**.

## Componentes originais do Konaro (licença pendente)
| Componente | Local |
|---|---|
| Scripts de build e teste | `scripts/`, `live/auto/`, `live/config/hooks/` |
| Layout do Plasma, splash, metadados dos temas | `packages/konaro-desktop/data/usr/share/plasma/` |
| Arte: logotipo provisório, papéis de parede, fundo do menu de boot, imagem do instalador | `packages/*/artwork/*.svg` |
| Configurações padrão | `packages/konaro-desktop/data/etc/` |
| Identidade do Calamares | `packages/konaro-installer/` |

Toda a arte foi criada do zero para o projeto (formas geométricas e gradientes em SVG).
Nenhum logotipo, ícone, fonte ou imagem da Apple/macOS foi usado.

## Componentes derivados
| Componente | Origem | Licença |
|---|---|---|
| `KonaroLight.colors`, `KonaroDark.colors` | Estrutura do esquema Breeze (KDE) com cores próprias | LGPL-2.0-or-later |
| Tema do Plasma "Konaro" (`desktoptheme/konaro`) | Molduras translúcidas do Breeze com opacidade alterada (`artwork/make-plasma-theme.py`) | LGPL (como o Breeze) |

## Ícones de aplicativos na Loja
`packages/konaro-tools/data/store/icons/` contém os ícones oficiais dos apps do catálogo,
extraídos dos metadados AppStream do Debian e do Flathub (`scripts/fetch-store-icons.sh`).
Pertencem aos respectivos projetos e marcas e são usados só para identificar cada app na
Loja, como fazem as lojas de apps do Linux. Não fazem parte da licença do Konaro.

## Arte original (licença pendente)
Decorações de janela Aurorae "Konaro"/"Konaro Dark" (botões semáforo), Dock Konaro
(`org.konaro.dock`), ícones Loja/Atualizações/Drivers/Boas-vindas, sistema de design QML.

## Build 5: novos componentes
- **Papéis de parede Serra, Dunas e Pinguim**: arte original, gerada por
  `packages/konaro-desktop/artwork/make-wallpapers.py`. O pinguim é um mascote original do
  Konaro (não é a arte do Tux de Larry Ewing).
- **Tela de login (tema SDDM "konaro")**, **Iniciar**, **widgets** e **apps Ajuda/Migração**:
  código original do projeto (licença pendente). O Iniciar usa os modelos de apps do Plasma
  (`org.kde.plasma.private.kicker`) como biblioteca, sem copiar código do KDE.
- **Fontes oferecidas**: Inter, Noto Sans e Manrope (SIL Open Font License 1.1) e
  Roboto (Apache 2.0), todas dos pacotes do Debian.
- **Secure Boot**: `shim-signed` (assinado pela Microsoft) e `grub-efi-amd64-signed` /
  kernel do Debian (assinados pelo Debian), sem modificação.

## Componentes de terceiros incluídos na ISO
Todos vêm dos repositórios oficiais do Debian e mantêm suas licenças originais; o texto
de cada uma fica em `/usr/share/doc/<pacote>/copyright` dentro do sistema. A lista
completa de pacotes de cada ISO é gerada em `build/iso/*.packages`.

| Grupo | Exemplos | Licenças típicas |
|---|---|---|
| Kernel, base Debian | linux-image-amd64, systemd, apt | GPL-2.0, LGPL, várias |
| KDE Plasma e apps | plasma-workspace, kwin, dolphin, okular | GPL-2.0+/LGPL-2.1+ |
| Instalador | calamares, calamares-settings-debian | GPL-3.0+ |
| Fontes | fonts-inter, fonts-noto-* | SIL OFL 1.1 |
| Navegadores | firefox-esr (Debian), brave-browser (repositório do Brave), Ungoogled Chromium (Flathub) | MPL-2.0; MPL-2.0/BSD; BSD |
| Jogos e Windows | wine, lutris, winetricks, gamemode, mangohud (Debian); Steam (Flathub) | LGPL-2.1+, GPL-3, LGPL; **Steam: proprietário (licença da Valve, aceita pelo usuário no primeiro uso)** |
| Firmware e microcódigo | firmware-misc-nonfree, firmware-iwlwifi, intel-microcode... | **Proprietárias redistribuíveis** (seção `non-free-firmware` do Debian) |

### Obrigações antes de qualquer publicação
- Escolher a licença do Konaro e adicionar `LICENSE` na raiz do repositório.
- Disponibilizar o código-fonte correspondente dos pacotes GPL distribuídos na ISO
  (o live-build pode gerar uma imagem de fontes com `--source true`; não habilitado ainda).
- Revisar as licenças de firmware (`non-free-firmware`) — o Debian as redistribui, mas
  o Konaro deve documentar isso nas notas de versão.

### Seções do Debian usadas
Imagem: `main`, `non-free` e `non-free-firmware`; os pacotes `lutris` e `winetricks`
(seção `contrib`) são instalados por um hook com uma fonte temporária. O sistema instalado
usa `main contrib non-free non-free-firmware`.
**A seção `contrib` não é usada no build inteiro:** com `--firmware-chroot true`,
o live-build incluiria pacotes como `firmware-b43-installer`, que **baixam firmware
proprietário da internet durante a instalação** (de fora do Debian, sem verificação de
assinatura do APT). Isso quebrou o primeiro build e tornaria a ISO não reprodutível.
Placas Broadcom antigas (b43) ficam sem firmware automático — limitação documentada.
