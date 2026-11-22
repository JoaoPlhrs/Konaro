# 0007 — Padrões provisórios para destravar a primeira ISO

- **Estado:** Provisória — cada item abaixo responde a uma pergunta **em aberto** do
  documento mestre e deve ser confirmado ou trocado pelo responsável.
- **Data:** 2026-11-22

| Pergunta em aberto | Valor provisório | Onde mudar |
|---|---|---|
| Idiomas da 1ª versão (§11.1-5) | **DECIDIDO:** português (Brasil) e inglês. Menu de boot com as duas opções; traduções de outros idiomas não são instaladas (`/etc/dpkg/dpkg.cfg.d/50-konaro-languages`) | `live/config/includes.chroot_before_packages/` |
| Navegador padrão (§11.2) | **DECIDIDO:** Firefox, Brave e Ungoogled Chromium, escolhidos no instalador — ver [0010](0010-navegadores.md) | — |
| Apps pré-instalados (§5.8) | Dolphin, Konsole, KWrite, Ark, Gwenview, Okular, Spectacle | `40-konaro-apps.list.chroot` |
| Loja (§5.1) | Loja Konaro com catálogo curado; Flathub configurado — ver [0009](0009-ferramentas-proprias-python-qt.md) | `packages/konaro-tools/` |
| Menu/lançador (§4.5) | Kickoff (padrão do Plasma) com o logo Konaro na barra superior | layout em `konaro-desktop` |
| Ordem dos botões da janela | Esquerda: fechar, minimizar, maximizar (inspiração macOS) | `/etc/xdg/kwinrc` em `konaro-desktop` |
| Fonte da interface | **Inter** (OFL, pacote `fonts-inter` do Debian) | `/etc/xdg/kdeglobals` |
| Logotipo | Marca **provisória** geométrica ("K" num círculo), arte original | `packages/*/artwork/` |
| Usuário da sessão live | `konaro` (senha `live`, padrão do live-config) | `live/auto/config` |
| Requisitos mínimos (§11.1-4) | Não definidos; o Calamares usa os do Debian (15 GB de disco, 1 GB de RAM) | — |
