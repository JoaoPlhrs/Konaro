# 0002 — Estrutura inicial do repositório

- **Estado:** Provisória (a organização real dos repositórios GitHub está pendente, §6.8/§11.2).
- **Data:** 2026-11-22

## Decisão
Um único repositório (monorepo) com:

```
live/       configuração do Debian Live Build      (módulo sugerido: konaro-build)
packages/   pacotes .deb próprios do Konaro         (konaro-desktop, konaro-installer)
scripts/    build, chroot de build, teste em VM, lint
docs/       documento mestre, decisões, pendências, licenças, status
```

Só foram criados os módulos que já têm conteúdo real (princípio §7: "não criar um módulo
só para dar aparência de organização"). `konaro-store`, `konaro-welcome`, `konaro-updater`
etc. **não existem ainda** de propósito.

## Observação
O código está em `konaro-os/` dentro de um repositório antigo e temporário (por instrução
do responsável, o conteúdo antigo foi ignorado). O diretório é autocontido: pode ser movido
para a raiz de um repositório novo sem alterações.
