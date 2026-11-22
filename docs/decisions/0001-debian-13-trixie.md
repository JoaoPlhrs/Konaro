# 0001 — Base Debian 13 "trixie" com KDE Plasma 6.3

- **Estado:** Provisória — aguarda aprovação do responsável (o documento mestre deixa a versão em aberto, §3.1).
- **Data:** 2026-11-22

## Contexto
O documento mestre decide "Debian" e "KDE Plasma", mas não a versão. Pede que a
escolha considere estabilidade, suporte de segurança, Calamares e esforço de manutenção.

## Verificado (2026-11-22)
- `deb.debian.org/debian/dists/stable/Release` → **Version 13.8, Codename trixie**.
- No trixie: `plasma-workspace 4:6.3.6`, `kwin 6.3.6`, `calamares 3.3.14`,
  `calamares-settings-debian 13.0.13`, `live-build 1:20250505+deb13u1`.
- Debian 14 "forky" ainda é *testing* (não é estável).

## Decisão
Usar **Debian 13 "trixie" (stable)** com o **Plasma 6.3** empacotado pelo Debian.

## Alternativas
- **Debian 12 "bookworm"**: Plasma 5.27 (fim de vida no KDE), Debian já o trata como *oldstable*. Rejeitada.
- **Debian testing (forky)**: Plasma mais novo, mas muda continuamente — contradiz "estabilidade" e "sem rolling release". Rejeitada.
- **Backports do Plasma**: aumenta manutenção; reavaliar só se houver necessidade concreta.

## Consequências
- Suporte de segurança do Debian para o trixie até ~2028 (+ LTS ~2030). O ciclo anual
  do Konaro precisará definir como acompanha o Debian (pendente, §6.6).
- Recursos do Plasma posteriores a 6.3 (ex.: troca automática claro/escuro) não estão
  disponíveis; por isso há dois temas globais (claro e escuro) selecionáveis.
