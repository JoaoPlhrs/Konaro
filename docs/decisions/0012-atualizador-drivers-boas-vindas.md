# 0012 — Atualizador, Drivers e Boas-vindas

- **Estado:** Provisória
- **Data:** 2026-11-22

## Atualizações (§5.3)
- Janela agrupa: **Segurança**, **Componentes do Konaro**, **Sistema**, **Aplicativos (Flatpak)**.
- Classificação de segurança pelo PackageKit (`InfoEnum.SECURITY` / origem `-security`).
- **Nunca instala sozinho.** Um timer systemd do usuário (`konaro-update-check.timer`,
  15 min após o login e a cada 12 h) só **notifica**; desativado na sessão live.
- Avisa quando a atualização pode exigir reinicialização e oferece reiniciar pelo diálogo do Plasma.
- Fontes do sistema instalado: Debian `main contrib non-free non-free-firmware` via HTTPS.

## Drivers (§5.2)
- Detecção com ferramentas do Debian: `lspci -nnk`, `nvidia-detect`, `isenkram-lookup`.
- Para cada recomendação: dispositivo, motivo, origem e pacotes; instala só após
  confirmação, via PackageKit; avisa sobre reinicialização.
- Não instala nada automaticamente; não promete suporte universal.

## Boas-vindas (§4.8)
- 8 páginas: boas-vindas + idioma (pt/en), aparência (claro/escuro, reduzir animações),
  internet, privacidade (sem coleta de dados; estatísticas KDE desligadas por padrão),
  atualizações e drivers, jogos e apps do Windows, como usar, pronto.
- Abre no primeiro login (autostart) e uma única vez; na sessão live mostra "Instalar o Konaro OS".
- Não exige conta e não conecta serviços externos.
