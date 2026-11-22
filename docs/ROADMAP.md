# Recursos recomendados para as próximas versões

Lista proposta pelo Claude Code em 2026-11-22, a pedido do responsável. Nada aqui foi
aprovado ainda; a ordem reflete impacto para quem vem do Windows ou do macOS.

## ✅ Aprovados pelo responsável (2026-11-22)
- [x] **Secure Boot** (shim + GRUB + kernel assinados pelo Debian) — build 5.
- [x] **Assistente de migração do Windows** (documentos, fotos, músicas, favoritos, papel de parede) — build 5.
- [x] **Fontes escolhíveis já na instalação** (build 5: Inter, Noto Sans, Manrope, Roboto), com padrão igual ou parecido com a do macOS
      (a SF Pro da Apple não pode ser redistribuída; candidatas livres: Inter — já usada —,
      Geist, Manrope; decisão pendente).
- [x] **Widgets no estilo do macOS** (relógio, calendário, notas, sistema) — build 5.
- [x] **Loja com catálogo completo** (AppStream do Debian + Flathub) — build 5.
- [x] **Novos papéis de parede exclusivos** (build 5: Serra, Dunas e Pinguim — um pinguim
      original do Konaro no lugar da arte oficial do Tux).
- [x] **App de ajuda "Onde está…?"** para quem vem do Windows — build 5.
- [x] **Tela de login no estilo do macOS** (build 5) — fundo com o papel de parede,
      data e hora grandes no topo, foto do usuário, nome e campo de senha em pílula de vidro
      embaixo, layout do teclado e menu de energia no canto superior direito. Tema próprio do SDDM.
- [x] **Tela de boot do sistema** (Plymouth): logo Konaro centralizado com indicador de
      progresso, no lugar do texto que rola durante a inicialização — build 4.
- [x] **Iniciar em tela cheia (tecla Super)**, no estilo Launchpad/Windows 11 — build 5.

## Alta prioridade
1. **"Voltar no tempo" (snapshots do sistema).** Instalar em Btrfs com Snapper e criar
   um ponto de restauração antes de cada atualização, com opção no menu de boot para
   iniciar no estado anterior. É a maior proteção contra uma atualização que quebre o
   sistema — e um equivalente direto ao "Restauração do Sistema" do Windows.
2. **Repositório APT do Konaro, assinado.** Sem ele, Loja, Dock, temas e correções
   do Konaro não chegam a quem já instalou.
3. **Secure Boot** com a cadeia assinada do Debian (shim + GRUB + kernel). Muitos PCs
   novos vêm com Secure Boot ligado e o usuário iniciante não sabe desligá-lo.
4. **Tela de login e tela de boot com a identidade Konaro.** Tema próprio do SDDM (hoje
   é o Breeze com o papel de parede Konaro) e um splash Plymouth com o logo, sem texto
   rolando no boot.
5. **Assistente de migração do Windows.** Detecta a partição do Windows e copia
   Documentos, Imagens, Músicas, favoritos do navegador e papel de parede.
6. **Central de controle na barra superior** (como a do macOS): Wi-Fi, Bluetooth, som,
   brilho, modo escuro, "não perturbe" e perfil de energia num único painel de vidro.

## Média prioridade
7. **Atualização de firmware (fwupd)** dentro do Atualizações do Konaro (BIOS/UEFI, SSD,
   periféricos), com o mesmo modelo de "avisar e pedir permissão".
8. **Impressoras e scanners sem configuração**: impressão "driverless" (IPP Everywhere),
   `ipp-usb` e um assistente gráfico para os casos que precisam de driver.
9. **Ajuda Konaro**: um app de ajuda com "Onde está…?" para quem vem do Windows
   (Painel de Controle → Configurações, Explorador → Arquivos, Ctrl+Alt+Del → Monitor do
   sistema) e respostas para as dúvidas mais comuns.
10. **Acessibilidade de primeira classe**: leitor de tela Orca pronto para ligar no
    menu de boot e no instalador, alto contraste, texto maior e "Reduzir movimento"
    nas Boas-vindas.
11. **Loja com catálogo completo** (AppStream do Debian + Flathub), capturas de tela e
    avaliações — mantendo a curadoria na página Início.
12. **Jogos**: gerenciar versões do Proton (GE-Proton) e ativar o GameMode/MangoHud
    pela própria Loja, sem terminal.

## Para avaliar
13. **Integração com o celular** (KDE Connect) configurada nas Boas-vindas.
14. **Perfis de energia e saúde da bateria** em notebooks.
15. **Controle dos pais** (limites de apps e tempo de uso).
16. **Assistente de IA opcional e local** — depende das decisões pendentes de
    privacidade, modelo e permissões (documento mestre §5.7).
17. **Matriz de compatibilidade de hardware** pública, construída com testes reais.
