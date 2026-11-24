# Konaro OS 0.1.0 "Fênix" — edições

A primeira versão com nome (constelação da Fênix) sai em duas edições, com o mesmo visual
e os mesmos apps do Konaro.

| | **Fênix** | **Fênix Lite** |
|---|---|---|
| Para quem | computadores com 4 GB de RAM ou mais | computadores antigos (ex.: notebook de 2007 com 2–3 GB de RAM) |
| Visual Konaro (tema, dock, barra superior, Iniciar, login, papéis de parede) | ✅ | ✅ |
| Loja, Atualizações, Drivers, Boas-vindas, Ajuda, Migração, Voltar no tempo, Restaurar | ✅ | ✅ |
| Vidro com desfoque e refração (Liquid Glass) | ✅ | — (painéis sólidos; o desfoque pesa em placas antigas) |
| Janelas gelatinosas, contraste atrás dos menus | ✅ | — |
| Animações | normais | mais curtas (a "lâmpada mágica" e o zoom continuam) |
| Memória comprimida (zram) | — | ✅ até 4 GB extras, comprimidos com zstd |
| Indexação de arquivos em segundo plano (Baloo) | ✅ | — (a busca de apps e configurações continua) |
| Firefox | padrão | menos processos, libera abas paradas, grava menos no disco |
| Placa de vídeo sem OpenGL 2 (ex.: Intel GMA 950) | — | interface desenhada pelo processador, automaticamente |
| Tela de login | acelerada pela placa de vídeo | desenhada pelo processador (abre em qualquer placa) |
| Temas de ícones extras, KeePassXC, atualização de firmware (fwupd) | ✅ | — (ícones e KeePassXC continuam na Loja/Boas-vindas) |
| Fontes extras de idiomas raros, cofres (Plasma Vault), backup Kup, ibus | ✅ | — |
| Modem 3G (ModemManager) | ligado | desligado (pode ser ligado) |

## Requisitos da Fênix Lite

- **Processador de 64 bits** (x86-64). Core 2 Duo, Pentium Dual-Core T23xx/T3xxx, Celeron 5xx,
  Athlon 64 / Turion 64 e mais novos funcionam. **Processadores só de 32 bits** (Core Duo T2xxx, Pentium Dual-Core T2060/T2080/T2130
  "Yonah", Pentium M, Celeron M 3xx/4xx) **não funcionam**: o Debian 13, base do Konaro, não tem
  mais versão de 32 bits.
- **2 GB de RAM** no mínimo; 3 GB ou mais é o recomendado.
- **20 GB de disco** livres (um disco de 250 GB sobra).
- Placas de vídeo Intel GMA 950/X3100, ATI Radeon X1000 e mais novas, NVIDIA GeForce 6/7/8
  (driver livre nouveau). Placas sem OpenGL 2 funcionam sem os efeitos.
- Wi-Fi: Intel (2200, 3945, 4965 e mais novos), Atheros e Realtek funcionam direto. Algumas
  placas **Broadcom antigas** (b43) precisam de um firmware que o Debian não pode distribuir;
  nesses casos use cabo de rede na primeira vez.

## Como construir

    sudo ./scripts/build-iso.sh                  # Fênix
    sudo ./scripts/build-iso.sh --edition lite   # Fênix Lite

A configuração da Lite fica em `live/editions/lite/` e as configurações leves no pacote
`konaro-lite` (gerado de `packages/konaro-desktop/lite/`).
