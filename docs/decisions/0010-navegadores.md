# 0010 — Navegadores: Firefox, Brave e Ungoogled Chromium, escolhidos no instalador

- **Estado:** Aceita (decisão do responsável)
- **Data:** 2026-11-22

## Decisão
Os três ficam **na imagem** (a sessão live pode experimentar todos e a instalação funciona
sem internet). O Calamares ganhou a página **Navegadores** (`packagechooser`, seleção
múltipla, pelo menos um); o módulo Python `konarobrowsers` remove do sistema instalado os
não escolhidos e define o primeiro escolhido (ordem Firefox → Brave → Ungoogled) como padrão.

| Navegador | Origem | Atualizações |
|---|---|---|
| Firefox ESR (+ pt-BR) | Debian `main` | Atualizador Konaro / APT |
| Brave | Repositório oficial do Brave (`brave-browser-apt-release.s3.brave.com`), chave `DBF1 A116 C220 B8C7 164F 9823 0686 B784 2003 8257` | Atualizador Konaro / APT |
| Ungoogled Chromium | Flathub (`io.github.ungoogled_software.ungoogled_chromium`) | Atualizador Konaro / Flatpak |

## Consequências
- A ISO cresce (o runtime Flatpak é compartilhado com o Steam).
- O Brave adiciona um repositório de terceiros ao sistema (com `signed-by`, só para os
  pacotes do Brave). Se o Brave não for escolhido, o repositório é removido.
