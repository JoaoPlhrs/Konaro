# Registro de decisões técnicas (ADRs)

Cada arquivo registra uma decisão: contexto, escolha, alternativas e consequências.
Estado possível: **Aceita** (decisão do responsável ou consequência direta dela),
**Provisória** (escolha técnica para destravar o trabalho; precisa de aprovação),
**Substituída**.

| Nº | Decisão | Estado |
|---|---|---|
| [0001](0001-debian-13-trixie.md) | Base Debian 13 "trixie" + Plasma 6.3 | Provisória (aguarda aprovação) |
| [0002](0002-estrutura-do-repositorio.md) | Estrutura inicial do repositório (monorepo) | Provisória |
| [0003](0003-identidade-em-pacotes-deb.md) | Identidade e ferramentas entregues como pacotes `.deb` | Provisória |
| [0004](0004-boas-vindas-no-splash-do-plasma.md) | Animação "olá → Welcome to Konaro" como splash do Plasma | Provisória |
| [0005](0005-firewall-ufw.md) | Firewall: ufw ativo + plasma-firewall | Provisória |
| [0006](0006-secure-boot-desativado.md) | Secure Boot desativado na ISO de desenvolvimento | Aceita (decisão: "posteriormente") |
| [0007](0007-padroes-provisorios.md) | Padrões provisórios (idioma, apps, sem navegador) | Provisória |
| [0008](0008-ambiente-de-build.md) | Build em chroot Debian + proxy APT opcional | Provisória |
| [0009](0009-ferramentas-proprias-python-qt.md) | Ferramentas próprias em Python + Qt 6 sobre PackageKit/Flatpak | Provisória |
| [0010](0010-navegadores.md) | Firefox, Brave e Ungoogled Chromium escolhidos no instalador | Aceita |
| [0011](0011-jogos-e-apps-windows.md) | Jogos e programas do Windows | Aceita (composição provisória) |
| [0012](0012-atualizador-drivers-boas-vindas.md) | Atualizador, Drivers e Boas-vindas | Provisória |
