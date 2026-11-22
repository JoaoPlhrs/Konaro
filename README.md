<p align="center"><img src="docs/assets/banner.png" alt="Konaro OS" width="100%"></p>

<p align="center">
  <a href="https://gofile.io/d/TgNSuXQ7"><img src="https://img.shields.io/badge/⬇_Baixar-0.1.0--dev1-1d1d1f?style=for-the-badge" alt="Baixar"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/Novidades-build_4-3a3a3c?style=for-the-badge" alt="Novidades"></a>
  <a href="docs/STATUS.md"><img src="https://img.shields.io/badge/Testes-24%2F24-28c840?style=for-the-badge" alt="Testes"></a>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Debian-13_trixie-A81D33?logo=debian&logoColor=white" alt="Debian 13">
  <img src="https://img.shields.io/badge/KDE_Plasma-6.3-1D99F3?logo=kde&logoColor=white" alt="KDE Plasma 6.3">
  <img src="https://img.shields.io/badge/arquitetura-amd64-555" alt="amd64">
  <img src="https://img.shields.io/badge/boot-BIOS_%2B_UEFI-555" alt="BIOS + UEFI">
  <img src="https://img.shields.io/badge/idiomas-pt--BR_%7C_en-555" alt="Idiomas">
  <img src="https://img.shields.io/badge/estado-desenvolvimento-FEBC2E" alt="Em desenvolvimento">
</p>

<p align="center"><b>Um Linux bonito e fácil para quem nunca usou Linux.</b><br>
Visual inspirado no macOS, jeito de usar familiar para quem vem do Windows.</p>

<p align="center"><img src="docs/assets/tour.gif" alt="Tour pelo Konaro OS" width="88%"></p>

---

## ⬇️ Download rápido

| Versão | Data | Tamanho | O que mudou | Baixar |
|---|---|---|---|---|
| **0.1.0-dev1 · build 4** "Boot Konaro" | 2026-11-22 | 4,0 GB | Nova tela de carregamento com o logo Konaro + tudo da build 3 | [**⬇ Baixar ISO inteira**](https://gofile.io/d/TgNSuXQ7) |
| 0.1.0-dev1 · build 3 "Visual elegante" | 2026-11-22 | 4,0 GB | Vidro, botões semáforo, dock animado, widgets, nova Loja e instalador | substituída pela build 4 |
| 0.1.0-dev1 · build 2 "Ferramentas" | 2026-11-22 | — | Loja, Atualizações, Drivers, Boas-vindas, navegadores, jogos | substituída pela build 3 |
| 0.1.0-dev1 · build 1 "Fundação" | 2026-11-22 | — | Base Debian 13 + Plasma 6, instalador, identidade | substituída pela build 3 |

Detalhes de cada versão em **[CHANGELOG.md](CHANGELOG.md)**. SHA-256 da build 4:
`02a60c7cde3b21e81eb6a7327ca95e95e18d6ec40f6c26a3057cf1a2f24b113a`

> ⚠️ **Build de desenvolvimento.** Teste primeiro numa máquina virtual. O que foi e o que
> não foi testado está em [docs/STATUS.md](docs/STATUS.md).

## ✨ Destaques

<table>
<tr>
<td width="50%"><img src="docs/screenshots/11-area-de-trabalho-widgets.png" alt="Área de trabalho"><br><b>Área de trabalho</b> — widgets nos cantos, barra superior e dock de vidro.</td>
<td width="50%"><img src="docs/screenshots/20-janela-semaforo.png" alt="Janela"><br><b>Janelas</b> — botões semáforo e menu global na barra superior.</td>
</tr>
<tr>
<td><img src="docs/screenshots/13-loja-na-sessao.png" alt="Loja"><br><b>Loja Konaro</b> — fácil como a Microsoft Store, com apps do Debian e do Flathub.</td>
<td><img src="docs/screenshots/10-boas-vindas-semaforo.png" alt="Boas-vindas"><br><b>Boas-vindas</b> — 9 passos: idioma, tema, widgets, internet, privacidade, drivers e jogos.</td>
</tr>
</table>

<p align="center"><img src="docs/screenshots/21-tela-de-boot.png" alt="Boot" width="60%"><br><i>A nova tela de carregamento do sistema.</i></p>

<p align="center"><img src="docs/assets/dock.gif" alt="Dock" width="70%"><br><i>O dock: o ícone sob o ponteiro sobe e cresce.</i></p>

## 📦 O que vem no sistema

| Área | Implementação |
|---|---|
| Base | Debian 13, kernel do Debian, x86_64, ISO híbrida BIOS + UEFI (sem Secure Boot) |
| Desktop | KDE Plasma 6.3 (Wayland, com sessão X11), SDDM, Dolphin |
| Identidade | Temas **Konaro Claro/Escuro** (paleta neutra), papéis de parede, fonte Inter, tela "Olá… → Welcome to Konaro" — sistema de design em [docs/design/DESIGN.md](docs/design/DESIGN.md) |
| Área de trabalho | **Vidro só no que flutua** (barra superior, dock, menus, popups, widgets) com desfoque; janelas com botões **semáforo** à esquerda; **Dock Konaro** com ícones que sobem e crescem sob o ponteiro; **widgets nos cantos** (relógio, calendário, memória, notas), cada um pode ser ligado/desligado |
| Idiomas | Português (Brasil) e inglês — menu de boot com as duas opções |
| Instalador | Calamares (fluxo do Debian) com identidade Konaro e página **Navegadores** |
| Navegadores | **Firefox**, **Brave** e **Ungoogled Chromium** — o usuário escolhe quais manter na instalação |
| Loja Konaro | Visual de loja moderna (trilho lateral como a Microsoft Store, destaque, fileiras, página do app); 47 apps curados com ícones oficiais; origem, formato e permissões Flatpak; instala/remove via PackageKit e Flathub |
| Atualizações | Janela agrupada (segurança, sistema, Konaro, Flatpak) + aviso periódico; **nunca instala sem permissão** |
| Drivers | Detecta placa NVIDIA e outros dispositivos (`nvidia-detect`, `isenkram`), explica, pede permissão e instala |
| Boas-vindas | Assistente de primeiro uso: idioma, claro/escuro, internet, privacidade, atualizações, drivers, jogos, dicas |
| Jogos e Windows | Steam (Proton), Lutris, Wine 32+64 bits (duplo clique em `.exe`), GameMode, MangoHud, Vulkan; Bottles, Heroic, ProtonUp-Qt na Loja |
| Segurança | Firewall `ufw` ativo (bloqueia entrada) + módulo gráfico |
| Hardware | Firmware livre e `non-free-firmware` do Debian, microcódigo Intel/AMD |

## 🗺️ Próximos passos

Planejados e aguardando aprovação: Secure Boot, assistente de migração do Windows,
tela de login e boot com a identidade Konaro, widgets no estilo do macOS, novas fontes,
Loja com catálogo completo, novos papéis de parede e o app de ajuda "Onde está…?".
Veja **[docs/ROADMAP.md](docs/ROADMAP.md)**.

## 🛠️ Para desenvolvedores

### Compilar e testar

```sh
./scripts/lint.sh                              # verificações estáticas + testes
sudo ./scripts/build-iso.sh                    # num Debian 13
# ou, em outro Linux:
sudo ./scripts/builder-chroot.sh setup && sudo ./scripts/builder-chroot.sh build-iso

./scripts/verify-iso.sh build/iso/konaro-os-*.iso     # confere a imagem
sudo ./scripts/test-system.sh                          # testa o sistema com systemd (sem VM)
./scripts/test-vm.sh --uefi build/iso/konaro-os-*.iso  # inicia numa VM QEMU
```

Detalhes: [docs/BUILDING.md](docs/BUILDING.md) e [docs/TESTING.md](docs/TESTING.md).

## Estrutura

```
live/                    configuração do Debian Live Build
  auto/config            opções do lb config (versão Debian, mirrors, boot, ISO)
  config/package-lists/  pacotes da imagem, agrupados e comentados
  config/hooks/normal/   i386, Flatpak, padrões, Calamares, verificações
  config/archives/       repositório do Brave (chave) e preferências do build
  config/bootloaders/    menu GRUB (PT/EN, tempo de espera, tema)
packages/
  konaro-desktop/        tema global, layout, splash, cores, papéis de parede, padrões (/etc/xdg)
  konaro-installer/      identidade do Calamares, página Navegadores, ajustes da sessão live
  konaro-tools/          Loja, Atualizações, Drivers, Boas-vindas, jogos (Python + Qt 6)
scripts/                 build, chroot de build, verificação da ISO, teste de sistema, VM, lint
docs/                    documento mestre, decisões, pendências, licenças, status
```

Documento mestre: [docs/KONARO_OS_MASTER_SPEC.md](docs/KONARO_OS_MASTER_SPEC.md) ·
decisões: [docs/decisions/](docs/decisions/) · pendências: [docs/PENDING.md](docs/PENDING.md) ·
design: [docs/design/DESIGN.md](docs/design/DESIGN.md).

## 📄 Licença

Ainda **não definida** para os componentes originais (veja [docs/LICENSES.md](docs/LICENSES.md)).
Os pacotes do Debian, do KDE e dos apps mantêm as próprias licenças.
