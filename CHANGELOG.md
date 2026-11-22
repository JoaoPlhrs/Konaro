# Histórico de versões

Todas as versões do Konaro OS, da mais nova para a mais antiga. A ISO mais recente está inteira em [**https://gofile.io/d/TgNSuXQ7**](https://gofile.io/d/TgNSuXQ7).

Legenda: ✨ novo · 🎨 visual · 🐛 correção · ⚠️ limitação conhecida

---

## 0.1.0-dev1 · build 4 — "Boot Konaro" · 2026-11-22 · **atual**

ISO **inteira** (um único arquivo): [**baixar no Gofile**](https://gofile.io/d/TgNSuXQ7) · `konaro-os-0.1.0-dev1-amd64.iso` · 4,0 GB · SHA-256
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
