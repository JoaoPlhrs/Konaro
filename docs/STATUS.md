# Estado do projeto — o que foi criado, compilado, testado e validado

> Regra do documento mestre (§8.4): "arquivo criado" ≠ "funciona"; "funciona numa VM" ≠
> "compatível com hardware real". Cada item abaixo diz **como** foi verificado.
> Atualizado em 2026-11-22, build `0.1.0~dev1` (ISO de 4,0 GB, 2.100 pacotes, build completo do zero; SHA-256 `c05bdb08…f071b9`).

Legenda: ✅ verificado · 🟡 verificado em parte · ⬜ não testado

## Ambiente de teste usado
Sessão Claude Code na nuvem: Ubuntu 24.04, 4 CPUs, 15 GB de RAM, **sem KVM** (o QEMU só
roda em emulação TCG, muito lenta). Build dentro de um chroot Debian 13
(`scripts/builder-chroot.sh`). **Nenhum teste em hardware físico foi feito.**

Três níveis de teste:
1. **`verify-iso.sh`** — inspeciona a ISO pronta (estrutura de boot, arquivos, pacotes, fontes APT).
2. **`test-system.sh`** — inicia o sistema da imagem com **systemd de verdade** (systemd-nspawn,
   efêmero) e testa serviços, PackageKit, Flatpak, jogos e as interfaces. **24/24 ok.**
3. **`test-vm.sh`** — boot completo da ISO no QEMU (UEFI), com capturas de tela.

## Rodada "visual elegante" (2026-11-22)

| Item | Estado | Como foi verificado |
|---|---|---|
| Sistema de design + Loja em QML | ✅ | Capturas claro/escuro (offscreen) e **na sessão real da VM** |
| Ícones oficiais dos apps na Loja | ✅ | 44 de 47 via AppStream; os 3 restantes usam o tema |
| Boas-vindas (9 passos, página Widgets) | 🟡 | Renderização e navegação na VM; ligar/desligar widgets ao vivo **não testado** (precisa de plasmashell com D-Bus de sessão real) |
| Atualizações e Drivers redesenhados | ✅ | Renderização com dados de exemplo; lógica coberta pelo teste de sistema (24/24) |
| Decoração "semáforo" (Aurorae) | ✅ | Na VM: botões vermelho/amarelo/verde à esquerda, cantos arredondados, sombra. Corrigida depois: listras na borda (bordas agora esticadas) |
| Vidro só no que flutua | ✅ | Na VM: menu de apps e calendário translúcidos com desfoque; janelas opacas |
| Dock Konaro (sobe e cresce sob o ponteiro) | 🟡 | Efeito confirmado no `plasmoidviewer`. **Dois bugs achados nos testes e corrigidos:** (1) ignorava a lista de atalhos do layout; (2) na ISO seguinte mostrava um único ícone em branco — o layout gravava os atalhos como um texto com vírgulas, lido pelo Plasma como um só atalho inválido. Agora grava uma lista de verdade e o dock também aceita o formato antigo. Conferido numa **sessão Plasma real** (usuário novo, 1º login): Instalar, Arquivos, Firefox, Loja, Steam, Lutris, Configurações, Lixeira. Passar o mouse na VM não foi possível (o QEMU só envia movimento relativo) |
| Widgets nos cantos | 🟡 | Relógio, calendário e notas aparecem nos cantos. Corrigidos: calendário fora do canto (largura mínima), widget de memória vazio na VM (desligado por padrão) e o ícone "Instalar" do Debian na área de trabalho, que ficava sob o relógio (removido: a instalação já está no dock e nas Boas-vindas) |
| Instalador redesenhado | ✅ | Capturas do Calamares: barra lateral grafite, botões em pílula, cartões dos navegadores |
| "Centro de boas-vindas" do KDE duplicado | ✅ corrigido | Removido do build (o Konaro tem o próprio) |

## Resultados por área

| Área | Estado | Como foi verificado |
|---|---|---|
| Build reproduzível (lb + pacotes Konaro) | ✅ | `build-iso.sh` no chroot Debian 13; 8 pacotes `.deb` compilam; lintian sem erros |
| ISO híbrida BIOS + UEFI | ✅ | `verify-iso.sh`: El Torito BIOS e UEFI, kernel/initrd, GRUB |
| Menu de boot PT/EN, tempo de espera 5 s | 🟡 | Arquivos verificados; na VM o boot seguiu sozinho (sem ficar parado no menu) |
| Sem resíduos do build (proxy, pins, mirrors locais) | ✅ | `verify-iso.sh` |
| Idiomas pt_BR + en (demais traduções excluídas) | ✅ | Filtro do dpkg presente; checado no hook de build |
| Tema Konaro, barra superior, dock, splash | 🟡 | Arquivos e tema padrão verificados; visual do desktop na VM: ver abaixo |
| Sessão live sem bloqueio/apagar tela | 🟡 | Script do live-config presente na imagem; efeito real: ver VM |
| **Loja Konaro** | ✅ | Renderização (pt/en); no sistema da imagem: detecta apps instalados (deb e Flatpak); **instalou e removeu um pacote via PackageKit** |
| **Atualizações** | ✅ | No sistema da imagem: atualizou índices, listou e classificou atualizações (0 pendentes na imagem nova); timer habilitado para usuários |
| Notificação de atualizações | ⬜ | Precisa de uma sessão gráfica real com atualizações pendentes |
| **Drivers** | 🟡 | Análise real no contêiner (dispositivo virtio, sem recomendações); recomendação NVIDIA testada só com dados simulados e testes unitários |
| **Boas-vindas** | 🟡 | Todas as páginas renderizam (pt/en); ações (tema, rede) só numa sessão real |
| Firefox / Brave (repo oficial) / Ungoogled Chromium | ✅ | Instalados na imagem; repositório do Brave com HTTPS + `signed-by`; Flatpak via Flathub HTTPS |
| Página "Navegadores" no instalador | 🟡 | O Calamares da imagem (sob Xvfb, no contêiner) mostra a etapa "Navegadores" com Firefox, Brave e Ungoogled Chromium; exige ao menos uma escolha. **A remoção dos não escolhidos (módulo `konarobrowsers`) só roda numa instalação real — não executada** |
| Identidade Konaro no instalador | ✅ | Captura do Calamares: "Bem-vindo ao instalador de Konaro OS 0.1", barra lateral Konaro, etapas em português |
| Steam (Flatpak) + i386 + Proton | 🟡 | Steam e runtimes 32 bits instalados; abrir o Steam e rodar um jogo exige login e GPU — não testado |
| Wine 32+64, duplo clique em `.exe` | 🟡 | `wine --version` ok; associação de `.exe` configurada; nenhum programa Windows executado ainda |
| Lutris, GameMode, MangoHud, Vulkan 32/64 | ✅ | Instalados (verificado no sistema da imagem) |
| Firewall ufw | 🟡 | Habilitado para o boot; não carrega dentro de contêiner (limitação do teste) |
| **Instalação com o Calamares em disco** | ⬜ | Não executada (sem KVM, levaria horas na emulação) |
| Hardware físico | ⬜ | Nenhum teste |
| Consumo de RAM / tempo de boot | ⬜ | Sem medição válida (a emulação TCG distorce os números) |

## Teste em VM (QEMU UEFI, emulação TCG, 6 GB de RAM)

Capturas em [`docs/screenshots/`](screenshots/).

| Verificação | Resultado |
|---|---|
| Menu de boot inicia sozinho (5 s) | ✅ o sistema iniciou sem intervenção |
| Desktop Konaro (barra superior, dock, papel de parede) | ✅ ~6 min após o boot (emulação lenta) |
| Dock: Instalar, Arquivos, navegador padrão (Firefox), Loja, Steam, Lutris, Configurações, Lixeira | ✅ |
| Boas-vindas abre sozinha, em português, com "Instalar o Konaro OS" | ✅ navegação entre páginas por teclado ok |
| Menu (logo Konaro + Meta) encontra "Loja Konaro" pela busca | ✅ |
| Loja na sessão real: ícones, categorias, apps instalados como "Abrir" | ✅ |
| Menu global na barra superior (Arquivo, Editar…) | ✅ |
| Sessão live não bloqueia a tela | ✅ 14+ min sem bloqueio (a ISO anterior bloqueava aos ~10 min) |
| Tema Konaro Escuro aplicado | ✅ — mas `plasma-apply-lookandfeel` reaplicou o layout do dock (corrigido nas Boas-vindas) |
| **RAM usada na sessão live** | **1,9 GB** (`free -m`: 1899 MB usados de 5923, Konsole aberto, após abrir Loja e Boas-vindas) |
| **ISO final:** dock com todos os atalhos no 1º login | ✅ Instalar, Arquivos, Firefox, Loja, Steam, Lutris, Configurações, Lixeira; canto do relógio livre |
| **ISO final:** janela de app com botões semáforo e menu global | ✅ Dolphin: vermelho/amarelo/verde à esquerda, cantos arredondados, menu na barra superior |
| Abrir o instalador (Calamares) | ✅ com a CPU emulada `Nehalem` (ISO final): abre com identidade Konaro e etapa "Navegadores"; sessão estável. ❌ com `-cpu max`: o KWin caiu (ver diagnóstico) |

**Diagnóstico do erro do instalador:** log serial com o journal do systemd mostrou
`kwin_wayland ... terminated abnormally with signal 11` com a pilha em
`libgallium-25.0.7` (Mesa llvmpipe), executando código gerado em tempo de execução, sob
emulação de CPU `-cpu max` do QEMU. O mesmo Calamares, iniciado no sistema da imagem com
systemd (contêiner), carregou todos os módulos, a identidade Konaro e a página
"Navegadores" (3 itens) sem erros. Indício forte de limitação do ambiente de teste
(emulação sem KVM): repetindo com `-cpu Nehalem` (sem AVX), o instalador abriu normalmente.
Ainda **não confirmado** em hardware real ou VM acelerada.

## Correções feitas após o primeiro teste em VM (incluídas na ISO final)
- Boas-vindas: trocar claro/escuro não reaplica mais o layout (o dock do usuário é preservado).
- Plasma Discover removido (era uma segunda loja, puxada como recomendação do KDE).
- Mensagem "sem internet" quando o PackageKit está offline (antes: "Algo deu errado").
- Texto secundário das ferramentas com mais contraste (5,7:1 claro / 7,9:1 escuro).
- `test-vm.sh`: CPU emulada sem AVX sob TCG.

## Problemas conhecidos / limitações
- **ISO de 4,0 GB** — o Flatpak (Ungoogled Chromium + Steam + runtimes 32 bits) responde por boa parte.
- A Loja mostra um catálogo curado (47 apps), não todo o Debian/Flathub; sem capturas de tela de apps.
- Sem repositório Konaro: os pacotes `konaro-*` do sistema instalado não recebem atualizações.
- Secure Boot não suportado (desative no firmware).
- Broadcom b43 antigo sem firmware automático.
- Steam: licença proprietária da Valve, aceita pelo usuário no primeiro uso.
- **Firefox desenha a própria barra de título** (abas na barra) com botões cinza no estilo
  GTK, em vez dos botões semáforo do Konaro. Correção prevista: preferência padrão
  `browser.tabs.inTitlebar = 0` (barra de título do sistema). Não aplicada nesta ISO.
