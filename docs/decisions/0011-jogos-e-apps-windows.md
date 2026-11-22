# 0011 — Jogos e programas do Windows

- **Estado:** Aceita como prioridade (decisão do responsável); composição provisória
- **Data:** 2026-11-22

## Decisão
**Pré-instalado** (pacote `konaro-gaming` + hooks):
- Suporte **32 bits (i386)** habilitado: `wine32`, Mesa OpenGL/Vulkan i386, GameMode i386.
- **Wine 10** (64 e 32 bits) com duplo clique em `.exe`/`.msi` (atalho `konaro-wine.desktop`),
  Winetricks, fontes do Wine.
- **Steam** (Flatpak do Flathub; o Proton vem pelo próprio Steam) + regras de controle `steam-devices`.
- **Lutris** (Debian), **GameMode**, **MangoHud**, drivers Vulkan.

**Na Loja (seção Jogos / Apps do Windows), um clique:** Bottles, Heroic, ProtonUp-Qt
(GE-Proton), Prism Launcher, RetroArch, GOverlay, entre outros.

## Por que Steam via Flatpak
O pacote `steam-installer` do Debian exige aceitar a licença da Valve num prompt do debconf
durante a instalação, o que não funciona bem pela loja. O Flatpak do Steam é mantido pela
comunidade do Flathub com apoio da Valve e compartilha o runtime com o Ungoogled Chromium.

## Limites (documento mestre §10.7)
Nem todo jogo roda: anti-cheat e alguns DRMs bloqueiam. Drivers NVIDIA proprietários são
oferecidos pelo **Drivers do Konaro** (não vêm pré-instalados).
