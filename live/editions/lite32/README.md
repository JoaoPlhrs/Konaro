# Konaro OS Fênix Lite 32 — computadores antigos de 32 bits

`scripts/build-iso.sh --edition lite32`. Parte da edição **lite** (`base`) e troca a
arquitetura para **i386** (`arch`). É a mesma Fênix Lite (visual, apps e ajustes leves),
com estas diferenças obrigatórias:

- **Kernel do Debian 12** (linux 6.1 `686-pae`, LTS até 2028): o Debian 13 não tem
  kernel de 32 bits. Só o kernel vem de lá (preferências do APT em `config/archives`);
  todo o resto é Debian 13 + KDE Plasma 6, como nas outras edições.
- **Boot por BIOS (e UEFI sem Secure Boot)**: computadores de 32 bits quase sempre usam BIOS; não há Secure Boot em 32 bits.
  A opção `forcepae` deixa iniciar Pentium M e Celeron M que não anunciam PAE.
- **Loja**: sem apps do Flathub e do GitHub (eles não publicam versões de 32 bits);
  os milhares de apps do Debian continuam.
