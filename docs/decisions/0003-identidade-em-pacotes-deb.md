# 0003 — Identidade e ferramentas entregues como pacotes `.deb`

- **Estado:** Provisória
- **Data:** 2026-11-22

## Contexto
A identidade (temas, layout, papéis de parede) poderia ser copiada direto para a imagem
via `config/includes.chroot` do live-build. Mas o modelo de repositórios decidido é
**híbrido: Debian + repositório Konaro** (§3.5), e o sistema instalado precisa receber
atualizações desses componentes.

## Decisão
Tudo que é do Konaro vira **pacote Debian** em `packages/`, construído com `debhelper`
e incluído na ISO via `config/packages.chroot`:

- `konaro-desktop` — tema global claro/escuro, layout (barra superior + dock), splash de
  boas-vindas, esquemas de cor, papéis de parede, ícones, padrões em `/etc/xdg`, SDDM.
- `konaro-installer` — identidade do Calamares + atalho "Instalar o Konaro OS"
  (removido do sistema instalado pelo próprio instalador).

A arte é versionada como **SVG** e renderizada no build do pacote (`rsvg-convert`).

## Consequências
- Os mesmos `.deb` poderão ser publicados no futuro repositório Konaro (assinatura e
  infraestrutura ainda pendentes — §3.5).
- Padrões ficam em `/etc/xdg`: valem para quem não personalizou; nunca sobrescrevem `~/.config`.
- Hoje o sistema instalado **não** tem de onde atualizar `konaro-desktop` (não há
  repositório Konaro publicado). Limitação conhecida.
