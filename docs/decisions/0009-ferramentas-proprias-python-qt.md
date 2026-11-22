# 0009 — Ferramentas próprias em Python 3 + Qt 6 sobre PackageKit e Flatpak

- **Estado:** Provisória (o documento mestre deixa a linguagem em aberto, §7)
- **Data:** 2026-11-22

## Contexto
O responsável pediu loja, atualizador, gerenciador de drivers e boas-vindas antes do
primeiro teste em VM. O §3.4/§10.3 exige que a loja seja uma **camada de interface** sobre
mecanismos maduros, nunca um instalador improvisado.

## Decisão
- Pacote-fonte `konaro-tools` → binários `konaro-common`, `konaro-store`, `konaro-updater`,
  `konaro-drivers`, `konaro-welcome`, `konaro-gaming`.
- **Python 3 + PyQt6 (Qt Widgets)**: está no Debian 13, herda o estilo Breeze e as cores
  do esquema Konaro automaticamente, sem compilação, fácil de revisar.
- **Pacotes Debian só via PackageKit** (API `PackageKitGlib` pelo PyGObject): o daemon faz a
  transação, o polkit pede a senha, há bloqueio contra operações concorrentes.
- **Flatpak via a ferramenta `flatpak`** com `--system`; o próprio Flatpak pede autorização.
- Uma operação por vez em cada ferramenta; erros traduzidos para mensagens simples,
  com os detalhes técnicos disponíveis em "Mostrar detalhes".
- Idiomas: textos-fonte em inglês e tradução pt_BR em `konaro/i18n.py`; um teste garante
  que nenhum texto fique sem tradução.

## Alternativas
- **Plasma Discover rebatizado**: maduro, mas sem identidade/curadoria Konaro e sem seção
  de jogos/apps do Windows. Pode virar backend no futuro (AppStream completo).
- **Rust ou C++/QML**: melhor desempenho, porém muito mais código e tempo para o mesmo
  resultado nesta fase.

## Limitações conhecidas
- A loja mostra um **catálogo curado** (47 apps), não todo o Debian/Flathub.
- Sem capturas de tela dos apps nem avaliações (AppStream ainda não integrado).
