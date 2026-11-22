# Histórico de versões

Todas as versões do Konaro OS, da mais nova para a mais antiga. A ISO mais recente está inteira em [**https://gofile.io/d/xAf862BJ**](https://gofile.io/d/xAf862BJ).

Legenda: ✨ novo · 🎨 visual · 🐛 correção · ⚠️ limitação conhecida

---

## 0.1.0-dev6 · build 6 — "Leve" · 2026-11-22 · **atual**

ISO **inteira**: [**baixar no Gofile**](https://gofile.io/d/xAf862BJ) · `konaro-os-0.1.0-dev6-amd64.iso` · **2,7 GB** (antes 4,1 GB) · SHA-256
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
