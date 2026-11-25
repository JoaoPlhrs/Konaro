# Histórico de versões

Todas as versões do Konaro OS, da mais nova para a mais antiga. Versão atual: **0.1.1 "Fênix"** — [Fênix](https://gofile.io/d/IMrf2TPM), [Fênix Lite](https://gofile.io/d/WWvc6XnI) e [Fênix Lite 32](https://gofile.io/d/42gKQkbY) (computadores antigos).

Legenda: ✨ novo · 🎨 visual · 🐛 correção · ⚠️ limitação conhecida

---

## 🔥 0.1.1 "Fênix" (correções) · 2026-11-25 · **atual**

Correções importantes. Se você baixou a 0.1.0, baixe a 0.1.1. Quem já instalou recebe as correções pelas **Atualizações do Konaro**.

| Edição | Para quem | Baixar | Tamanho | SHA-256 |
|---|---|---|---|---|
| **Fênix** | computadores com 4 GB de RAM ou mais | [**⬇ Gofile**](https://gofile.io/d/IMrf2TPM) | 2,4 GB | `030d7025131a75331b7b2fa3e2fceab883cfc12542b8c13546e91188855ef1db` |
| **Fênix Lite** | computadores antigos de 64 bits | [**⬇ Gofile**](https://gofile.io/d/WWvc6XnI) | 1,7 GB | `01b82a740d0ff6a25a27d662485e238becf2b482cfd973ceb863f3b74ecba396` |
| **Fênix Lite 32** | computadores antigos de 32 bits | [**⬇ Gofile**](https://gofile.io/d/42gKQkbY) | 1,8 GB | `f9cb5733e8e90d8c33ccda12eac50e96a2dac028bbe328d34a99a5fd5b0ec8ee` |

- 🐛 **A Loja fechava ao buscar ou abrir uma categoria.** Esse erro existia desde a chegada dos apps do GitHub (Hydra e outros). Está corrigido e coberto por teste.
- 🐛 **Apps que não abriam e tela preta depois de alguns minutos.** Em computadores e máquinas virtuais com pouca memória, a RAM acabava e o sistema fechava programas à força, inclusive a área de trabalho. Agora:
  - todas as edições têm **memória comprimida (zram)**;
  - a Loja usa ~30 MB em vez de ~550 MB ao buscar, porque o catálogo vem pronto na imagem e não é mais carregado duas vezes;
  - um erro inesperado não fecha mais os apps do Konaro.
- 🐛 **Em máquina virtual a tela ficava preta.** A economia de energia desligava a tela e suspendia o sistema, e a máquina virtual não acordava. Numa máquina virtual o Konaro agora não desliga a tela nem suspende, e só bloqueia a tela depois de 15 minutos.
- ✨ **Modo leve automático sem aceleração 3D** (ex.: VirtualBox sem 3D): sem vidro e sem efeitos pesados, para não deixar tudo lento. Com placa de vídeo de verdade, nada muda.
- 🐛 **Baixar pela internet não funcionava** (temas de ícones, ambientes gráficos, apps, Wine). A imagem vinha sem a lista de pacotes. Agora o Konaro baixa a lista antes de instalar, mesmo que um repositório esteja fora do ar. Sem internet, ele avisa isso claramente.
- 🐛 **Senha nas Boas-vindas:** funciona também na sessão live. No sistema instalado, a senha da Carteira do KDE (senhas de Wi-Fi) é atualizada junto.
- 🎨 **Chapéus do avatar:** o gorro e o boné agora cobrem a cabeça inteira, sem cabelo aparecendo por cima e sem esconder as sobrancelhas.
- ✨ Com menos de 3 GB de RAM, as Boas-vindas sugerem a Fênix Lite.
- Testes: Fênix, Fênix Lite e Fênix Lite 32 — `verify-iso` OK e teste de sistema 19/19 nas três; numa sessão Plasma real: apps abrem, a Loja abre as categorias (90 apps em Jogos) e fica aberta, modo leve automático sem 3D, instalar com a lista de pacotes vazia funciona e, sem internet, a mensagem certa aparece.

## 🔥 0.1.0 "Fênix" · 2026-11-23 — primeira versão com nome

A primeira versão do Konaro com nome de constelação: **Fênix**. Sai em três edições, com o mesmo visual e os mesmos apps.

| Edição | Para quem | Baixar | Tamanho | SHA-256 |
|---|---|---|---|---|
| **Fênix** | computadores com 4 GB de RAM ou mais | substituída pela 0.1.1 | 2,4 GB | `018b3422aa6af2c1a5a8ca4d36371b014f2fc73e1b0a2f0a901fb3585bc3e1bd` |
| **Fênix Lite** | computadores antigos de 64 bits (ex.: notebook de 2007 com 3 GB de RAM) | substituída pela 0.1.1 | 1,8 GB | `504b09255b95d5960e28d19b2aa5aa0b7024b05dc75f4e7ca0a06af2145e52ca` |
| **Fênix Lite 32** | computadores antigos de **32 bits** (Pentium 4, Pentium M, Core Duo, Atom) | substituída pela 0.1.1 | 1,8 GB | `cbf569a0193583cfc9ed264265cc54ffeedfca5803e0a5364a302f4b54ae3cd7` |

- 🔥 **Nome Fênix** no sistema: "Sobre este sistema", fastfetch, tela de login em modo texto e o nome do arquivo da ISO.
- ✨ **Fênix Lite**, a edição para computadores antigos. Mantém o design do Konaro e todos os apps do Konaro, mas:
  - liga a **memória comprimida** (zram), que rende como se o computador tivesse bem mais RAM;
  - painéis **sólidos**, sem o vidro e sem as janelas gelatinosas, que pesam em placas de vídeo antigas;
  - **animações mais curtas** e sem indexação de arquivos em segundo plano;
  - **Firefox mais leve** e menos gravações no disco;
  - em placas de vídeo **sem OpenGL 2** (ex.: Intel GMA 950), a interface e o login são desenhados pelo processador e funcionam mesmo assim;
  - saem pacotes pesados dispensáveis num PC antigo: fontes de idiomas raros, cofres criptografados, backup Kup, ibus, Vulkan, firmware de servidores, temas de ícones extras, KeePassXC e fwupd. Tudo continua instalável pela Loja.
- ✨ **Fênix Lite 32**: a mesma Fênix Lite (KDE Plasma 6, Debian 13, visual e apps do Konaro) para processadores de **32 bits**. Como o Debian 13 não tem mais kernel de 32 bits, só o kernel vem do Debian 12 (Linux 6.1 LTS, com atualizações de segurança até 2028). Inicia por BIOS ou UEFI (sem Secure Boot). Na Loja aparecem só os apps do Debian, porque Flathub e GitHub não publicam versões de 32 bits.
- 🐛 **O Wine não vem mais dentro da ISO.** Desde a build 6 ele entrava por engano (~740 MB). Agora ele vem só quando você instala "Jogos e apps do Windows" pela Loja ou abre um .exe.
- Requisitos da Lite: processador de **64 bits** (Core 2 Duo, Pentium Dual-Core T23xx/T3xxx, Athlon 64/Turion 64 ou mais novo), 2 GB de RAM (3 GB recomendado) e 20 GB de disco. Para processadores de 32 bits, use a **Fênix Lite 32**. Detalhes em [docs/EDICOES.md](docs/EDICOES.md).
- Testes: Fênix — `verify-iso` OK · teste de sistema 19/19 · boot em VM com Secure Boot até a área de trabalho. Fênix Lite — `verify-iso` OK · teste de sistema 19/19 · sessão Plasma real com as configurações leves ativas (sem vidro, sem janelas gelatinosas). Boot da Lite em VM com **BIOS antiga e 3 GB de RAM** até a área de trabalho: com Boas-vindas e Konsole abertos, 1,1 GB ainda disponível e 2,9 GB de memória comprimida (zram) prontos (no modo live parte da RAM guarda o próprio sistema; instalado sobra mais). Fênix Lite 32 — `verify-iso` OK · teste de sistema 19/19 · boot em VM com processador **Core Duo de 32 bits** e 2 GB de RAM até a área de trabalho e as Boas-vindas. Nenhuma das três foi testada em computador físico ainda.

## 0.1.0-dev9 · build 9 — "Vidro" · 2026-11-23

ISO: (download encerrado — substituída pela Fênix) · `konaro-os-0.1.0-dev9-amd64.iso` · 2,6 GB · SHA-256
`9842dcaed392d996982219adce402570f7ca84cd022ac7e1bb98bb4da32645d8`

- ✨ **Liquid Glass**: o desfoque do sistema agora tem **refração nas bordas** (o vidro "dobra a luz" nas beiradas), com mais cor por trás. Efeito livre (GPL-3) adaptado pelo Konaro ao KWin do sistema.
- ✨ **Loja com mais fontes**: apps publicados pelos próprios desenvolvedores no **GitHub** — **Hydra Launcher**, YouTube Music (desktop) e LocalSend. A Loja baixa sempre a versão mais nova (.deb ou AppImage).
- ✨ **Instalar .deb e AppImage com dois cliques** (ou pela Loja > *Instalar de um arquivo*): o .deb é instalado com as dependências; o AppImage vai para a pasta Aplicativos e ganha ícone no menu — sem precisar de terminal.
- ✨ **Senha nas Boas-vindas**: troque a senha já no primeiro uso e escolha se ela é pedida ao voltar da suspensão.
- ✨ **Firewall na Central de controle**: liga e desliga com um toque (pede a senha).
- ✨ **Outros ambientes gráficos**: nova seção da Loja com **GNOME, Xfce, Cinnamon e MATE**, e a tela de login ganhou o **seletor de sessão** (Wayland, X11 ou outro ambiente) no canto inferior esquerdo. A tela de login do Konaro é mantida.
- ✨ **O sistema se chama Konaro OS** em todo lugar: "Sobre este sistema", fastfetch, terminal de login (`/etc/issue`), menu de inicialização (GRUB) e links do instalador. Continua compatível com programas feitos para Debian 13.
- 🎨 **12 novas aparências**: cores de destaque Azul, Roxo, Rosa, Verde, Laranja e Turquesa (claro e escuro), além do Grafite padrão.
- 🎨 **Novos temas de ícones**: Redondo, Suave, Clássico, Colorido e Acolhedor (baixados na hora ao escolher), além de Konaro e Minimalista. Nova página **Ícones e fontes** nas Boas-vindas.
- Testes: `verify-iso` OK · teste de sistema 19/19 · instalação de .deb solto via PackageKit, firewall liga/desliga, identidade Konaro e efeito Liquid Glass conferidos na imagem · TESTVM.

## 0.1.0-dev8 · build 8 — "Detalhes" · 2026-11-22

ISO: (download encerrado — substituída pela Fênix) · `konaro-os-0.1.0-dev8-amd64.iso` · 2,8 GB · SHA-256
`5da6c147720f9e4d2272492014ec0e526f1e12cb4ae67c4d128b7e59e7655206`

- ✨ **Tela de bloqueio Konaro de verdade**: é a tela do sistema ao bloquear e ao voltar da suspensão — data e hora grandes, foto, nome e senha em pílula de vidro, sobre o papel de parede do sistema. A autenticação continua sendo a do KDE.
- ✨ Tela de login usa o **papel de parede do sistema** (dá para trocar em Configurações > Tela de login).
- ✨ **fastfetch** (também pelo comando `neofetch`) com o **logo do Konaro**.
- ✨ **Animações**: janelas crescem ao abrir, "escorrem" para o dock ao minimizar (lâmpada mágica) e se deformam de leve ao serem arrastadas.
- ✨ **Vidro** mais transparente e com mais cor por trás (painéis, menus, widgets).
- ✨ **Som de inicialização** (composição original).
- ✨ Tela de entrada: os **"olás" em 24 idiomas** se repetem durante todo o carregamento; "Welcome to Konaro" só quando a área de trabalho fica pronta.
- ✨ Apps novos: **Por que está lento?** e **Restaurar o Konaro** (configurações, Voltar no tempo e restauração de fábrica mantendo os arquivos).
- ✨ **.exe com dois cliques**: se o Wine não estiver instalado, o Konaro oferece instalar na hora e abre o programa.
- ✨ **Gerenciador de senhas** (KeePassXC) e tema de ícones **Minimalista** (Papirus), escolhível nas Boas-vindas.
- 🎨 Barra superior enxuta (Wi-Fi, som, brilho e bateria ficam na Central de controle) e relógio no estilo "dom. 22 de nov.".
- 🇧🇷 Créditos: criado por João Palhares · Feito no Brasil (Sobre este sistema e fastfetch).
- Testes: `verify-iso` OK · teste de sistema 19/19 · boot em VM com Secure Boot · bloqueio e desbloqueio testados na VM.

## 0.1.0-dev7 · build 7 — "Avatares" · 2026-11-22

ISO **inteira**: (substituída pela build 8) · `konaro-os-0.1.0-dev7-amd64.iso` · 2,7 GB · SHA-256
`3e03e19c9c534cfa1fa591833c99ebff36aeadbb51c49062bbe447a5c39b3974`

- 🎨 **Meu Avatar refeito** (arte original do Konaro): rosto com volume, olhos com íris colorida e brilho, sobrancelhas e cabelos com mechas, 11 penteados, 10 cores de cabelo, 8 tons de pele, 6 cores de olhos, 5 formatos de olhos, 6 expressões, barba, óculos, acessórios de cabeça, sardas/pinta/brincos, roupa e fundo.
- ✨ Editor novo: **cores em amostras redondas** (dá para ver qual tom de pele está escolhido), **miniaturas ampliadas só da parte que muda** (olhos, boca, cabelo…), visto na opção escolhida e imagens desenhadas em segundo plano — sem travar.
- 🐛 As miniaturas e a prévia mostravam sempre o avatar padrão (o endereço da imagem chegava codificado).
- Quem tem a build 6 instalada recebe esta versão pelas **Atualizações do Konaro** (repositório próprio).
- Testes: `verify-iso` OK · teste de sistema 19/19 · editor renderizado no sistema da imagem.

## 0.1.0-dev6 · build 6 — "Leve" · 2026-11-22

ISO **inteira**: (substituída pela build 7) · `konaro-os-0.1.0-dev6-amd64.iso` · **2,7 GB** (antes 4,1 GB) · SHA-256
`6f03eddc48efe9e827a46808f67d25f2982aa39d7506d24392ac5b8b25e636f6`

- ✨ **Sistema mínimo**: só o Firefox vem instalado. Brave, Ungoogled Chromium, Steam e o pacote "Jogos e apps do Windows" ficam a um clique na Loja. Saíram KDE Connect, Ajuda do KDE, gerenciador de partições, vim, entre outros. 1.819 pacotes (antes 2.100).
- ✨ **Voltar no tempo**: o sistema é instalado em Btrfs e o Timeshift vem configurado — ponto de restauração ao terminar a instalação, todo dia e **antes de cada atualização**. App "Voltar no tempo" para restaurar.
- ✨ **Repositório próprio do Konaro** (assinado), servido por este GitHub em `apt/`: as ferramentas, temas e correções do Konaro agora chegam pelas Atualizações.
- ✨ **Central de controle** na barra superior: Wi-Fi, Bluetooth, modo avião, Não perturbe, modo escuro, modo de energia (Economia/Equilibrado/Desempenho), tela, som e bateria com a saúde dela.
- ✨ **Spotlight**: Alt + Espaço abre a busca no centro da tela.
- ✨ **Firmware** (BIOS/UEFI, SSD, periféricos) nas Atualizações do Konaro (fwupd/LVFS).
- ✨ **Meu Avatar**: crie um avatar personalizado (pele, cabelo, olhos, boca, barba, óculos, chapéu, fundo) que vira sua foto no login, no Iniciar e nas Configurações. Arte original do Konaro.
- 🎨 Papéis de parede **Fluxo**, **Terminal** e **Anel**.
- Testes: `verify-iso` OK · teste de sistema 19/19 · boot completo em VM **com Secure Boot ligado**.
- ⚠️ Não testados ainda: instalação em disco (Btrfs/Timeshift na prática), restauração de um ponto, atualização de firmware em hardware real.

## 0.1.0-dev1 · build 5 — "Mac + Windows" · 2026-11-22

ISO **inteira**: (substituída pela build 6) · `konaro-os-0.1.0-dev1-build5-amd64.iso` · 4,1 GB · SHA-256
`f3b7559b656f749a0097962b444a06619799f9de65910c2aea6248b398f97fe9`

- ✨ **Tela de login no estilo do macOS** (tema próprio do SDDM): data e hora grandes, foto/inicial, nome e senha em pílula de vidro; teclado e menu de energia no canto.
- ✨ **Iniciar em tela cheia** pela tecla Super/Windows (mistura de Launchpad e Iniciar do Windows 11): busca, fixados, todos os apps, usuário e energia.
- ✨ **Widgets em cartões** no estilo do macOS: relógio analógico, calendário do mês, notas editáveis e sistema (CPU, memória, disco).
- ✨ **Escolha da fonte** na instalação e nas Boas-vindas: Inter (padrão, parecida com a do macOS), Noto Sans, Manrope e Roboto.
- ✨ **Ajuda "Onde está…?"**: o nome que você conhece do Windows e onde fica no Konaro, com botão para abrir; atalhos e perguntas frequentes.
- ✨ **Migrar do Windows**: copia documentos, fotos, músicas, vídeos, favoritos dos navegadores e o papel de parede, abrindo o Windows só para leitura.
- ✨ **Loja com catálogo completo** (Debian + Flathub) na busca e nas categorias.
- ✨ **Secure Boot**: cadeia assinada do Debian; testado em VM com Secure Boot ligado. Drivers NVIDIA explicam o registro da chave (MOK).
- 🎨 Novos papéis de parede: **Serra**, **Dunas** e **Pinguim** (mascote original do Konaro).
- ⚠️ Não testados ainda: instalação em disco, migração com um disco NTFS real, hardware físico.

## 0.1.0-dev1 · build 4 — "Boot Konaro" · 2026-11-22

ISO **inteira** (um único arquivo): (substituída pela build 5) · `konaro-os-0.1.0-dev1-amd64.iso` · 4,0 GB · SHA-256
`02a60c7cde3b21e81eb6a7327ca95e95e18d6ec40f6c26a3057cf1a2f24b113a`

- 🎨 **Tela de carregamento do sistema (Plymouth)**: logo Konaro branco no fundo preto, com três pontos pulsando — sem texto rolando durante o boot. Também mostra o pedido de senha de discos criptografados.
- Inclui tudo da build 3.
- Testes: `verify-iso` OK · boot em VM com a nova tela confirmado.

## 0.1.0-dev1 · build 3 — "Visual elegante" · 2026-11-22 · 

ISO: `konaro-os-0.1.0-dev1-amd64.iso` · 4,0 GB · SHA-256
`c05bdb082686a78581a3181b439a989dd7157b45342b624748e9f744d0f071b9`

- 🎨 **Sistema de design próprio** (tons neutros, fonte Inter, botões em pílula) aplicado a tudo.
- 🎨 **Vidro só no que flutua**: barra superior, dock, menus, calendário e pop-ups translúcidos com desfoque; janelas sólidas.
- 🎨 **Botões semáforo** (vermelho/amarelo/verde) à esquerda das janelas, cantos arredondados, sombra suave.
- ✨ **Dock Konaro**: o ícone sob o ponteiro sobe e cresce, os vizinhos acompanham em curva.
- ✨ **Widgets nos cantos** (relógio, calendário, notas; memória e "tocando agora" opcionais), ligáveis nas Boas-vindas.
- 🎨 **Loja redesenhada** no estilo da Microsoft Store: trilho lateral, destaques, fileiras, página do app com permissões, 47 apps com ícones oficiais.
- 🎨 Boas-vindas (9 passos, nova página de Widgets), Atualizações e Drivers redesenhados.
- 🎨 **Instalador** com barra lateral grafite, botões em pílula e cartões para escolher os navegadores.
- 🐛 Dock mostrava um único ícone em branco no 1º login (atalhos gravados como texto).
- 🐛 Ícone "Instalar" do Debian ficava sob o widget de relógio (removido; a instalação está no dock).
- 🐛 Central de boas-vindas do KDE duplicada removida; listras na borda das janelas corrigidas.
- ⚠️ Firefox desenha a própria barra de título (botões cinza em vez de semáforo).
- Testes: `verify-iso` OK (2.100 pacotes) · teste de sistema 24/24 · boot e sessão em VM.

## 0.1.0-dev1 · build 2 — "Ferramentas" · 2026-11-22

- ✨ **Loja Konaro** (PackageKit + Flathub), **Atualizações** agrupadas com aviso periódico (nunca instala sem permissão), **Drivers** (NVIDIA e firmware), **Boas-vindas** de primeiro uso.
- ✨ Navegadores **Firefox, Brave e Ungoogled Chromium**, escolhidos durante a instalação.
- ✨ **Jogos e Windows**: Steam (Proton), Lutris, Wine 32+64 (duplo clique em `.exe`), GameMode, MangoHud, Vulkan.
- ✨ Idiomas português (Brasil) e inglês; menu de boot com as duas opções.
- 🐛 Sessão live não bloqueia mais a tela; Plasma Discover removido (segunda loja).

## 0.1.0-dev1 · build 1 — "Fundação" · 2026-11-22

- ✨ Base Debian 13 "trixie" + KDE Plasma 6.3, ISO híbrida BIOS/UEFI via Debian Live Build.
- ✨ Instalador Calamares com identidade Konaro, tema claro/escuro, papéis de parede, tela "Welcome to Konaro".
- ✨ Firewall `ufw`, firmware `non-free-firmware`, scripts de build, verificação e teste em VM.
