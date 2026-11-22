# KONARO OS — Documento Mestre do Projeto

> **Documento de referência para planejamento e desenvolvimento com Claude Code**  
> **Versão:** 0.5 — consolidação das Etapas 1 a 5  
> **Estado:** visão e decisões iniciais definidas; arquitetura detalhada e ambiente de desenvolvimento ainda precisam ser validados.  
> **Idioma principal deste documento:** português brasileiro.

---

## 0. Instruções importantes para o Claude Code

Este documento reúne as decisões, preferências, ideias e discussões feitas até agora sobre o Konaro OS. Leia-o por inteiro antes de propor ou executar mudanças no projeto.

### 0.1 Como interpretar este documento

Nem tudo aqui tem o mesmo grau de decisão. Para evitar que uma sugestão seja tratada como uma ordem definitiva, cada informação deve ser interpretada conforme estas categorias:

- **DECISÃO:** escolha explicitamente feita pelo responsável pelo projeto. Deve ser respeitada, a menos que exista incompatibilidade técnica real. Se houver incompatibilidade, explique o problema e apresente alternativas antes de mudar a decisão.
- **VISÃO / REQUISITO:** comportamento ou resultado que o sistema deverá buscar. Pode exigir decisões de implementação posteriores.
- **IDEIA:** conceito mencionado, mas que ainda pode ser refinado.
- **RECOMENDAÇÃO TÉCNICA:** caminho sugerido durante o planejamento. Não é uma decisão irrevogável; valide sua viabilidade.
- **EM ABERTO:** informação que ainda não foi respondida ou escolhida. Não invente uma resposta.

Quando houver conflito entre uma decisão explícita do responsável e uma recomendação técnica, a decisão explícita prevalece como objetivo do projeto. Sua responsabilidade é explicar os custos, riscos e opções, não alterar o escopo silenciosamente.

### 0.2 Seu papel no projeto

Você, Claude Code, será a principal ferramenta de desenvolvimento assistido do Konaro OS. O responsável pelo projeto supervisionará as decisões, revisará os resultados e realizará ou acompanhará os testes necessários.

Trabalhe como um engenheiro de software experiente que está ajudando a construir uma distribuição Linux real, e não como um gerador de mockups ou de arquivos sem integração.

Regras de trabalho:

1. **Não finja que algo funciona.** Diferencie claramente código criado, código compilado, recurso testado e recurso validado em hardware real.
2. **Não invente resultados de testes.** Sempre informe quais comandos foram executados, o resultado observado e o que ainda não foi testado.
3. **Não implemente grandes partes do sistema sem arquitetura.** Primeiro entenda os módulos, interfaces, dependências e critérios de aceitação.
4. **Não substitua componentes estáveis sem motivo.** Reutilize Debian, KDE Plasma, Calamares e ferramentas maduras quando atenderem aos requisitos.
5. **Não dependa do terminal para o usuário final.** O terminal pode ser usado no desenvolvimento, na manutenção e por usuários avançados, mas as tarefas comuns do sistema devem ter interfaces gráficas.
6. **Não execute operações destrutivas sem autorização.** Isso inclui apagar discos, formatar partições, sobrescrever imagens, modificar bootloader, alterar partições, remover pacotes essenciais ou publicar versões.
7. **Explique riscos antes de alterações importantes.** Especialmente em instalador, atualizações, drivers, repositórios, permissões, Secure Boot e inicialização.
8. **Mantenha o projeto reproduzível.** Prefira scripts, configurações declarativas e instruções documentadas a procedimentos manuais difíceis de repetir.
9. **Documente decisões técnicas.** Quando uma decisão relevante for tomada, registre motivo, alternativas consideradas e consequências.
10. **Não adicione escopo por conta própria.** Não introduza funcionalidades, serviços em nuvem, telemetria, contas obrigatórias ou dependências proprietárias sem discussão e aprovação.
11. **Priorize segurança e confiabilidade.** Não crie um instalador, atualizador ou gerenciador de pacotes improvisado que possa danificar o sistema.
12. **Se faltar uma informação, marque-a como pendente.** Faça uma pergunta objetiva quando a resposta for necessária; caso contrário, siga com uma solução provisória bem identificada.

### 0.3 Ordem de prioridade

Ao tomar decisões de implementação, use esta ordem:

1. Segurança, integridade dos dados e possibilidade de inicializar/recuperar o sistema.
2. Estabilidade e compatibilidade com hardware.
3. Facilidade de uso para pessoas sem experiência com Linux.
4. Desempenho e consumo de memória.
5. Identidade visual própria do Konaro.
6. Recursos avançados e personalizações adicionais.

O visual inspirado no macOS é importante, mas nunca deve comprometer a usabilidade, acessibilidade, estabilidade ou licenças de componentes.

---

# 1. Visão geral do Konaro

## 1.1 O que é o projeto

O **Konaro OS** será uma distribuição Linux para computadores desktop, construída sobre Debian, com identidade visual e ferramentas próprias.

A proposta é oferecer uma experiência simples, intuitiva, polida e familiar para pessoas que nunca utilizaram Linux ou que não querem lidar com configurações técnicas. A experiência visual desejada é bastante inspirada no macOS, especialmente na organização da área de trabalho, no dock, na barra superior, no acabamento visual e na sensação de integração entre os componentes.

O Konaro não pretende ser apenas uma instalação do Debian com um papel de parede diferente. Ele deverá ter uma identidade própria, uma experiência de primeiro uso guiada, uma loja de aplicativos própria e utilitários integrados que façam o sistema parecer um produto coerente.

Ao mesmo tempo, o projeto não pretende desenvolver um kernel ou uma infraestrutura inteira do zero. A intenção é construir uma distribuição independente em identidade, configuração, experiência e ferramentas, reaproveitando a base e os componentes consolidados do ecossistema Debian e KDE.

## 1.2 Objetivo principal

Criar um sistema operacional desktop que:

- Seja fácil de entender e utilizar mesmo para quem nunca usou Linux.
- Tenha aparência moderna, limpa, consistente e inspirada no macOS.
- Ofereça ferramentas gráficas suficientes para que o usuário comum não precise abrir o terminal.
- Seja relativamente leve e responsivo, com atenção especial ao consumo de RAM.
- Execute aplicativos com fluidez.
- Funcione em uma variedade ampla de computadores antigos e modernos, dentro de requisitos mínimos realistas.
- Ofereça instalação, atualização, gerenciamento de aplicativos e configuração de hardware por interfaces gráficas.
- Tenha uma base estável e uma estratégia de atualizações previsível.

## 1.3 Público-alvo

**DECISÃO:** público amplo — qualquer pessoa que use um computador desktop.

O foco especial de experiência é o usuário iniciante em Linux. A interface deve ser clara sem tratar o usuário como especialista. Opções avançadas podem existir, mas não devem ocupar o caminho principal das tarefas cotidianas.

## 1.4 Independência e filosofia

**DECISÕES:**

- O Konaro será uma distribuição independente em identidade e ferramentas.
- Sua base será Debian.
- A filosofia geral será equilibrada (*balanced*): combinar aparência, desempenho, estabilidade, compatibilidade e facilidade de uso.

“Independente” não significa reescrever todos os componentes. Significa que o Konaro terá decisões próprias de produto, configurações, identidade visual, integração, experiência de instalação, ferramentas e distribuição de seus componentes próprios.

## 1.5 Princípios fundamentais do produto

### Interface gráfica em primeiro lugar

O usuário comum deve conseguir executar as tarefas mais frequentes por interfaces gráficas. O terminal continuará disponível para desenvolvimento, diagnóstico e usuários avançados, mas não deve ser necessário para:

- Instalar e remover aplicativos comuns.
- Atualizar o sistema.
- Configurar Wi-Fi, Bluetooth, áudio, tela e dispositivos comuns.
- Ajustar aparência e comportamento básicos.
- Consultar informações do computador.
- Gerenciar drivers quando houver suporte seguro para isso.
- Utilizar as ferramentas padrão do sistema.

### Desempenho sem sacrificar a experiência

A meta é um sistema responsivo e com consumo de memória controlado, mas sem tornar a interface visualmente pobre. O projeto escolheu uma abordagem equilibrada, não uma distribuição minimalista a qualquer custo.

### Estabilidade acima de novidades constantes

O sistema deverá priorizar uma base confiável. As ferramentas e a identidade do Konaro poderão evoluir entre versões, mas o projeto não seguirá um modelo *rolling release*.

### Consistência visual

A tela de login, a área de trabalho, o dock, a barra superior, o menu de aplicativos, as configurações, a loja e os diálogos próprios devem parecer partes de um mesmo sistema.

---

# 2. Decisões técnicas já tomadas

Esta seção registra escolhas explícitas realizadas até a Etapa 5.

| Área | Decisão atual | Estado |
|---|---|---|
| Tipo de sistema | Desktop OS | Definido |
| Distribuição-base | Debian | Definido |
| Identidade | Distribuição independente, com ferramentas e identidade próprias | Definido |
| Público | Everyone / público geral | Definido |
| Filosofia | Equilibrada | Definido |
| Ambiente desktop | KDE Plasma | Definido |
| Estética | Inspirada fortemente no macOS | Definido como direção visual |
| Política de RAM | Equilíbrio entre aparência e desempenho | Definido como objetivo |
| Instalação de apps | Loja própria + ferramentas gráficas | Definido |
| Formatos de apps | DEB, Flatpak, AppImage e outros compatíveis, quando viável | Definido como objetivo amplo |
| Atualizações | Estáveis e controladas pelo usuário | Definido |
| Hardware | Amplo suporte a computadores antigos e modernos | Definido como objetivo |
| Gerenciador de arquivos | Dolphin | Definido |
| Configurações | KDE System Settings personalizado | Definido |
| Boas-vindas | Experiência guiada de primeiro uso | Definido |
| Animações | Opcionais/configuráveis | Definido |
| Loja | Própria, com identidade Konaro | Definido |
| Drivers | Detecção automática com pedido de permissão antes de instalar | Definido como comportamento desejado |
| Backup | Não é prioridade na versão inicial | Definido para o escopo inicial |
| Segurança | Equilibrada: firewall, permissões e atualizações de segurança | Definido como direção |
| Jogos | Suporte amplo, com Steam, Proton, Lutris e ferramentas de compatibilidade | Definido como objetivo |
| Assistente de IA | Opcional e integrado ao sistema | Definido como ideia de produto |
| Aplicativos pré-instalados | Apenas os essenciais | Definido |
| Construção da ISO | Debian Live Build | Definido |
| Instalador | Calamares | Definido |
| Kernel | Kernel fornecido pelo Debian | Definido |
| Arquitetura inicial | x86_64 / AMD64, 64 bits | Definido |
| Secure Boot | Implementar posteriormente | Definido |
| Repositórios | Híbrido: Debian + repositório próprio do Konaro | Definido |
| Ciclo de versões | Anual | Definido |
| Hospedagem inicial | GitHub | Definido |
| Licença do projeto | Código aberto | Definido em princípio; licença exata pendente |
| Ferramenta de desenvolvimento assistido | Claude Code | Definido como principal ferramenta |

---

# 3. Base do sistema e arquitetura de alto nível

## 3.1 Base Debian

**DECISÃO:** o Konaro será baseado em Debian.

A versão específica do Debian ainda não foi travada neste documento. No início da implementação, verificar qual versão estável do Debian é apropriada, sua janela de suporte, disponibilidade do KDE Plasma e compatibilidade dos pacotes necessários.

Não escolher uma versão apenas por ser a mais nova. A decisão deve considerar estabilidade, suporte de segurança, compatibilidade com Calamares, disponibilidade dos componentes e esforço de manutenção.

## 3.2 Ambiente desktop: KDE Plasma

**DECISÃO:** utilizar KDE Plasma como ambiente desktop.

O Plasma deverá ser configurado e personalizado para entregar a experiência Konaro. A intenção não é construir um ambiente desktop totalmente novo.

A personalização poderá abranger:

- Tema global e cores.
- Tema claro e escuro.
- Ícones.
- Fontes e tipografia.
- Painéis e widgets.
- Dock inferior centralizado.
- Barra superior própria ou painel personalizado.
- Menu/lançador de aplicativos.
- Tela de login.
- Tela de bloqueio.
- Papéis de parede.
- Animações e efeitos.
- Configurações padrão do Plasma.
- Integração entre aplicativos próprios e componentes KDE.

A implementação deve aproveitar as capacidades nativas do Plasma sempre que possível, evitando duplicar funções existentes.

## 3.3 Kernel

**DECISÃO:** usar o kernel fornecido pelo Debian inicialmente.

Não desenvolver um kernel próprio nem aplicar otimizações personalizadas sem uma necessidade comprovada. O objetivo inicial é compatibilidade e manutenção simples.

Caso no futuro haja uma necessidade concreta de desempenho ou compatibilidade, qualquer mudança deverá ser comparada com o kernel Debian e testada em hardware real.

## 3.4 Sistema de pacotes e formatos

**VISÃO / DECISÃO DE PRODUTO:** o usuário deverá conseguir instalar aplicativos por uma loja gráfica própria e lidar com formatos comuns do ecossistema Linux.

Formatos e origens considerados:

- **DEB:** formato nativo do ecossistema Debian.
- **Flatpak:** suporte desejado para aplicativos distribuídos por esse formato.
- **AppImage:** compatibilidade desejada quando tecnicamente viável.
- **Outras fontes compatíveis:** podem ser consideradas, desde que não prejudiquem segurança e manutenção.

Não afirmar que todo pacote de qualquer distribuição será compatível. A compatibilidade precisa ser validada por formato, dependências, arquitetura, bibliotecas e versão do sistema.

### Recomendação técnica para a loja

A loja Konaro deve ser uma camada de interface sobre mecanismos de gerenciamento maduros, e não um substituto improvisado para o APT ou para o Flatpak.

Uma direção inicial possível é integrar-se a ferramentas e serviços existentes, como PackageKit (se adequado e suportado no conjunto escolhido), APT e Flatpak. Antes de escolher a implementação final, verificar a compatibilidade real com a versão Debian e o KDE Plasma selecionados.

A loja deverá apresentar, quando possível:

- Nome, descrição, ícone e capturas de tela do aplicativo.
- Origem do aplicativo.
- Formato do pacote.
- Permissões relevantes, especialmente em Flatpak.
- Situação de instalação e atualização.
- Mensagens de erro compreensíveis.
- Confirmação antes de operações que alterem o sistema.

Para arquivos DEB externos e AppImages baixados pelo usuário, apresentar avisos claros sobre origem e confiança. Não executar arquivos baixados automaticamente nem esconder de onde o aplicativo veio.

## 3.5 Repositórios

**DECISÃO:** modelo híbrido.

- Os repositórios oficiais Debian fornecerão a maior parte dos pacotes-base e componentes comuns.
- Um repositório Konaro fornecerá os pacotes, configurações, identidade e ferramentas específicas do projeto.

O repositório próprio deve começar pequeno, hospedando apenas o que o Konaro realmente mantém.

### Requisitos importantes

- Metadados assinados e verificação de integridade.
- Chaves e procedimentos de assinatura documentados.
- Separação clara entre pacotes Debian e pacotes Konaro.
- Processo de publicação controlado.
- Histórico e versionamento.
- Testes antes de liberar atualizações.
- Plano de recuperação caso uma atualização própria apresente problemas.

Não distribuir pacotes do sistema por links improvisados ou sem mecanismo de verificação.

---

# 4. Identidade visual e experiência do usuário

## 4.1 Direção visual geral

**DECISÃO:** a aparência será moderna, limpa e fortemente inspirada no macOS.

A inspiração abrange o estilo e a organização da experiência, mas o Konaro deve possuir identidade própria. Não utilizar logotipos, ícones proprietários, fontes não licenciadas, papéis de parede protegidos ou recursos de terceiros sem autorização. Criar ou utilizar recursos com licença compatível.

O objetivo é que a interface pareça intencional e consistente, não um KDE padrão com alguns elementos recoloridos.

## 4.2 Paleta de cores

**DECISÃO:** paleta neutra.

- Preto.
- Branco.
- Tons de cinza.

A interface deverá oferecer modo claro e modo escuro adaptativos ou selecionáveis. A definição final dos valores exatos de cor, contraste e estados de interação permanece pendente.

## 4.3 Dock

**DECISÃO:** dock inspirado no macOS, centralizado na parte inferior da tela.

O dock deverá ser coerente com a área de trabalho e configurado para uso diário. Detalhes como ocultação automática, indicadores de aplicativos abertos, animação, tamanho, espaçamento e personalização ainda precisarão ser definidos e testados.

## 4.4 Barra superior

**DECISÃO:** o Konaro terá uma barra superior personalizada.

A disposição exata dos elementos ainda está aberta. Projetar pensando em acesso rápido a informações e controles comuns sem sobrecarregar a tela.

## 4.5 Menu/lançador de aplicativos e animação de início

O responsável mencionou a intenção de ter um **menu de iniciar próprio** e descreveu uma sequência na qual a tela mostra rapidamente “olá” em várias línguas e, em seguida, “Welcome to Konaro”.

A discussão também sugeriu que essa sequência seja tratada como animação de inicialização/boas-vindas separada da tela de login, para não comprometer a confiabilidade do boot.

**Ponto ainda a esclarecer:** não está totalmente definido se “menu de iniciar próprio” significa:

1. Um lançador/menu de aplicativos próprio, substituindo ou personalizando o menu padrão do Plasma;
2. Uma animação/tela de inicialização própria;
3. Ambos.

Não assumir que a animação substitui o menu de aplicativos. Preservar essa questão como pendência para a próxima etapa.

### Sequência de boas-vindas desejada

1. Durante a apresentação de início, exibir rapidamente saudações em diferentes idiomas.
2. Finalizar com a mensagem **“Welcome to Konaro”**.
3. Em seguida, continuar o fluxo normal de inicialização e/ou primeiro acesso.

A sequência deve ser visualmente agradável, curta e não bloquear indefinidamente o boot. Deve haver tratamento para inicialização sem animação, falha gráfica ou hardware lento. As saudações e traduções finais ainda não foram escolhidas.

## 4.6 Gerenciador de arquivos

**DECISÃO:** utilizar **Dolphin**.

O projeto não planeja substituir o Dolphin por um gerenciador de arquivos escrito do zero. Ele poderá receber configurações, tema, ícones, integração e comportamento padrão apropriados ao Konaro.

## 4.7 Configurações

**DECISÃO:** utilizar as configurações do KDE (KDE System Settings), personalizadas para o Konaro.

A meta é manter as configurações robustas e maduras do Plasma, enquanto se organiza a experiência para iniciantes e se dá identidade visual própria ao sistema.

Evitar criar um segundo painel de configurações que duplique tudo sem necessidade. Uma central de configurações própria poderá existir para atalhos, onboarding ou tarefas específicas, mas deverá integrar-se às ferramentas existentes.

## 4.8 Primeiro uso / boas-vindas

**DECISÃO:** haverá uma experiência guiada de primeiro uso.

Ela deve apresentar o Konaro e ajudar o usuário a concluir configurações essenciais sem exigir terminal. O conteúdo específico ainda será projetado.

Possíveis tópicos a avaliar, sem tratá-los ainda como requisitos fechados:

- Escolha de idioma e região.
- Tema claro/escuro.
- Conexão de rede.
- Configuração de privacidade básica.
- Detecção de atualizações.
- Introdução à loja de aplicativos.
- Atalhos e navegação da área de trabalho.

A experiência deve ser opcional ou fácil de concluir, sem obrigar o usuário a criar conta ou conectar serviços externos.

## 4.9 Animações

**DECISÃO:** animações devem ser configuráveis/opcionais.

Não sacrificar desempenho ou acessibilidade por efeitos visuais. Respeitar configurações de redução de movimento quando houver suporte e oferecer uma experiência adequada em computadores modestos.

---

# 5. Funcionalidades do sistema

## 5.1 Loja de aplicativos Konaro

**DECISÃO:** o sistema terá uma loja própria.

A loja deve ter identidade visual Konaro e facilitar a descoberta, instalação, atualização e remoção de aplicativos.

Ela não deve reinventar o gerenciamento de pacotes. Deve utilizar ferramentas consolidadas como backend, escolhidas após validação técnica.

### Objetivos funcionais

- Pesquisar aplicativos.
- Navegar por categorias.
- Ver detalhes e descrição.
- Instalar e remover aplicativos.
- Mostrar progresso e estado da operação.
- Informar a origem e o formato do aplicativo.
- Mostrar permissões relevantes quando disponíveis.
- Informar sobre atualizações.
- Apresentar erros em linguagem compreensível.

### Critérios de segurança

- Solicitar autorização adequada para mudanças no sistema.
- Não executar operações privilegiadas sem controle.
- Não ocultar origem desconhecida.
- Não tratar todo pacote externo como confiável.
- Não interromper operações de pacote de maneira que deixe o banco de pacotes inconsistente.
- Evitar múltiplas instalações concorrentes quando isso puder causar conflito.

O escopo exato da primeira versão da loja deve ser definido depois de validar o backend.

## 5.2 Drivers e dispositivos

**DECISÃO DE COMPORTAMENTO:** o sistema deve detectar hardware e orientar o usuário sobre drivers, mas pedir permissão antes de instalar.

Fluxo desejado:

1. Identificar um dispositivo que precise de um driver ou componente adicional.
2. Explicar qual dispositivo foi detectado e por que o componente é recomendado.
3. Informar a origem do driver/pacote.
4. Solicitar autorização do usuário.
5. Instalar usando mecanismos seguros do sistema.
6. Informar o resultado e se é necessário reiniciar.

Não prometer suporte universal a qualquer dispositivo. A compatibilidade depende do kernel, firmware, drivers disponíveis e licenças. Não instalar drivers desconhecidos automaticamente.

## 5.3 Atualizações

**DECISÃO:** o Konaro deverá avisar o usuário quando houver atualizações e permitir que ele escolha quando instalá-las.

O sistema não deverá forçar silenciosamente a instalação de atualizações comuns durante uma sessão de trabalho.

O mecanismo precisa distinguir, de maneira compreensível:

- Atualizações de segurança.
- Correções de estabilidade.
- Atualizações de aplicativos.
- Atualizações dos componentes próprios do Konaro.
- Atualizações que exigem reinicialização.

A política específica para atualizações críticas de segurança ainda não está definida. O usuário deve receber avisos claros sobre a importância e os riscos de adiar atualizações importantes.

## 5.4 Backup

**DECISÃO:** backup integrado não é prioridade para a primeira versão.

Não construir um sistema de backup completo como requisito inicial. Isso não significa que o Konaro deva impedir a instalação ou o uso de ferramentas de backup de terceiros.

## 5.5 Segurança

**DECISÃO:** abordagem equilibrada.

Recursos e objetivos mencionados:

- Firewall.
- Controle e apresentação de permissões.
- Atualizações de segurança.
- Opções avançadas de segurança quando apropriado.

A implementação deve usar componentes confiáveis e configurações seguras por padrão. Não criar mecanismos de segurança personalizados sem necessidade e revisão.

Secure Boot foi explicitamente deixado para uma etapa posterior. Portanto, a primeira versão não deve prometer suporte próprio completo a Secure Boot.

## 5.6 Jogos

**DECISÃO DE PRODUTO:** suporte a jogos será uma prioridade relevante; a experiência deve ser ampla.

Tecnologias mencionadas pelo responsável:

- Steam.
- Proton.
- Lutris.
- Ferramentas de compatibilidade relacionadas.

Não pré-instalar obrigatoriamente todas essas ferramentas sem avaliar tamanho, licenças, dependências e experiência inicial. Pode ser melhor oferecer instalação simples pela loja ou por uma seção de jogos.

Não prometer compatibilidade com todos os jogos, anti-cheats ou plataformas. A compatibilidade depende de cada jogo, driver, versão do Proton, serviço e hardware.

## 5.7 Assistente de IA

**DECISÃO DE PRODUTO:** o Konaro poderá oferecer um assistente de IA integrado, mas ele será opcional.

Ainda não foram definidos:

- Se será local, remoto ou híbrido.
- Qual modelo ou provedor será utilizado.
- Se funcionará offline.
- Quais permissões terá.
- Quais tarefas poderá executar.
- Como serão tratados privacidade, custos, telemetria e dados.

Não implementar conexão com serviços de IA, envio de dados ou execução de comandos por IA sem decisão explícita. A opção de IA não pode ser requisito para utilizar o sistema.

## 5.8 Aplicativos pré-instalados

**DECISÃO:** instalar apenas aplicativos essenciais.

A seleção exata ainda não foi fechada. A intenção é evitar excesso de aplicativos, duplicidade e consumo desnecessário de espaço e memória.

Aplicativos mencionados como exemplos de necessidades básicas:

- Navegador.
- Gerenciador de arquivos (Dolphin).
- Configurações.
- Utilitários essenciais do desktop.

Não escolher ou promover navegador específico sem decisão posterior. Evitar instalar várias aplicações para a mesma função.

---

# 6. Construção da distribuição e infraestrutura

## 6.1 Construção da ISO

**DECISÃO:** usar **Debian Live Build** para construir as imagens iniciais.

O objetivo é gerar uma ISO instalável e inicializável com o sistema, configurações, identidade e pacotes do Konaro.

O processo de construção deve ser automatizável e documentado. Uma pessoa deve conseguir reconstruir a ISO a partir do repositório seguindo as instruções, sem depender de passos secretos ou arquivos locais não documentados.

### Recomendação de engenharia

Começar usando Live Build de maneira próxima ao fluxo suportado pelo Debian. Criar ferramentas próprias para automatizar e organizar o processo somente quando houver necessidade clara.

A ideia de um sistema híbrido foi discutida como recomendação, mas a escolha efetivamente registrada pelo responsável foi simplesmente **Live Build**. Não tratar a criação de um sistema de build totalmente próprio como requisito.

## 6.2 Instalador

**DECISÃO:** utilizar **Calamares**.

A intenção é personalizar aparência, configuração e fluxo para que o instalador pareça parte do Konaro, sem construir um instalador inteiro do zero.

Validar a integração entre Calamares e a imagem produzida pelo Debian Live Build. O instalador deve ser testado cuidadosamente em máquinas virtuais e, antes de qualquer lançamento, em hardware físico.

### Requisitos críticos

- Identificação clara do disco de destino.
- Avisos explícitos sobre apagamento e particionamento.
- Não iniciar formatação sem confirmação do usuário.
- Informações compreensíveis sobre as consequências da instalação.
- Tratamento de falhas.
- Logs úteis para diagnóstico.
- Testes com UEFI e configurações de disco suportadas.
- Não alegar compatibilidade com todos os cenários antes de testá-los.

## 6.3 Arquitetura de hardware

**DECISÃO:** arquitetura inicial x86_64/AMD64, 64 bits.

ARM64 não faz parte do primeiro alvo definido. A expansão para ARM poderá ser avaliada no futuro, considerando o esforço extra de compilação, empacotamento, firmware, drivers e testes.

## 6.4 Secure Boot

**DECISÃO:** suporte a Secure Boot será implementado posteriormente.

Não colocar isso como bloqueio para a primeira prova de conceito, mas também não ocultar a limitação. Documentar o estado real do recurso na ISO e nas notas de versão.

Ao implementar no futuro, estudar a cadeia de inicialização assinada e os mecanismos compatíveis com Debian, shim, GRUB e kernel. Evitar inventar um esquema de assinatura próprio para a primeira versão.

## 6.5 Modelo de repositório

**DECISÃO:** repositórios híbridos.

- Debian para o sistema-base e pacotes mantidos pelo Debian.
- Konaro para pacotes e ferramentas desenvolvidos ou mantidos pelo projeto.

A hospedagem inicial será no GitHub. O uso do GitHub não significa necessariamente que todos os artefatos de distribuição, repositórios APT e ISOs devam ficar permanentemente armazenados no mesmo local; a infraestrutura de publicação pode evoluir.

## 6.6 Ciclo de versões

**DECISÃO:** ciclo anual de versões.

O Konaro pretende lançar uma versão principal por ano. Isso não implica que correções e atualizações só ocorram uma vez por ano.

É necessário definir uma política de manutenção que inclua:

- Correções de bugs.
- Atualizações de segurança.
- Atualizações pontuais dos pacotes próprios.
- Correções emergenciais.
- Período de suporte de cada versão.
- Processo de atualização de uma versão principal para a seguinte.

A relação entre o calendário anual do Konaro e os lançamentos estáveis do Debian ainda precisará ser especificada. Não criar um modelo rolling release.

## 6.7 Código aberto e licenças

**DECISÃO:** o projeto será de código aberto.

**PENDÊNCIA:** a licença exata ainda não foi escolhida.

O Konaro incorporará componentes de terceiros, cada um com sua própria licença. A decisão de tornar o projeto aberto não altera nem elimina as licenças originais do Debian, KDE Plasma, Calamares, drivers, bibliotecas e demais softwares incluídos.

Antes de publicar uma imagem ou pacote:

- Identificar licenças dos componentes distribuídos.
- Respeitar avisos de copyright.
- Incluir textos de licença quando exigido.
- Verificar obrigações de redistribuição e disponibilização de código-fonte.
- Não copiar recursos visuais proprietários sem permissão.
- Escolher uma licença para os componentes originais do Konaro.

## 6.8 Hospedagem e colaboração

**DECISÃO:** GitHub será a hospedagem inicial do projeto.

A organização dos repositórios, permissões, nome da organização, política de contribuição, issues, releases e automações ainda não foi decidida.

---

# 7. Sugestão de arquitetura modular

Esta seção é uma **RECOMENDAÇÃO TÉCNICA**, não uma estrutura já aprovada ou criada. Ela serve como ponto de partida para discutir a organização do código.

A recomendação é manter os componentes separados de modo que possam ser desenvolvidos, testados e atualizados sem misturar a distribuição inteira em um único programa.

Possível divisão lógica:

| Módulo sugerido | Responsabilidade |
|---|---|
| `konaro-build` | Configuração e automação do Debian Live Build; geração reproduzível da ISO |
| `konaro-desktop` | Temas, ícones, layouts, painéis, dock, configurações padrão e identidade visual do Plasma |
| `konaro-welcome` | Experiência guiada de primeiro uso e, se aprovado, elementos de boas-vindas |
| `konaro-installer` | Configuração e integração do Calamares com a imagem Konaro |
| `konaro-store` | Loja gráfica de aplicativos |
| `konaro-updater` | Interface de notificações e controle de atualizações, caso não seja melhor integrar uma ferramenta existente |
| `konaro-settings` | Configurações ou central de atalhos própria, apenas onde o KDE não atender bem |
| `konaro-repo` | Metadados, publicação e manutenção do repositório próprio |
| `konaro-core` | Configurações, metapacotes e integração central do sistema |

### Princípios para os módulos

- Não criar um módulo só para dar aparência de organização.
- Um componente só deve ser próprio quando houver valor real em mantê-lo.
- Reutilizar componentes do KDE e Debian quando forem suficientes.
- Definir interfaces claras entre os módulos.
- Manter documentação de instalação, compilação e teste.
- Evitar dependências circulares.
- Preferir dependências disponíveis e mantidas no Debian sempre que possível.

### Linguagens e tecnologias

Nenhuma linguagem de programação foi escolhida definitivamente para os aplicativos próprios.

Durante a discussão, Rust e Qt/QML foram mencionados como opções possíveis para ferramentas nativas. Tecnologias web também foram citadas como possibilidade para determinadas interfaces.

Essas menções são apenas alternativas para avaliação. Não assumir que o projeto inteiro será escrito em Rust, Qt, QML ou tecnologias web. Escolher por módulo, considerando integração com KDE, acessibilidade, manutenção, desempenho, empacotamento e experiência de desenvolvimento.

---

# 8. Orientações específicas para o uso do Claude Code

## 8.1 Estratégia geral

Claude Code será a principal ferramenta de desenvolvimento assistido, com o responsável pelo projeto supervisionando o trabalho.

Ainda não foi definido se o fluxo usará múltiplos agentes especialistas, automações externas ou somente uma sessão principal do Claude Code. Não presumir que uma arquitetura multiagente foi aprovada.

## 8.2 Antes de escrever código

Comece por:

1. Ler este documento.
2. Inspecionar o estado real dos repositórios e arquivos existentes.
3. Verificar as versões e ferramentas disponíveis no ambiente.
4. Identificar os requisitos que podem ser validados tecnicamente.
5. Apontar decisões em aberto que bloqueiem a implementação.
6. Propor uma estrutura de diretórios e um plano incremental.
7. Esperar aprovação para decisões que alterem escopo, licenças, segurança, particionamento ou distribuição.

Não criar imediatamente dezenas de aplicativos próprios. Primeiro prove que é possível gerar uma ISO Debian Live com KDE Plasma e configurações Konaro.

## 8.3 Desenvolvimento incremental sugerido

Uma sequência técnica inicial possível, sujeita a revisão:

**Fase A — Fundação**
- Preparar repositório e documentação.
- Criar configuração mínima do Debian Live Build.
- Selecionar os pacotes essenciais.
- Incluir KDE Plasma e Dolphin.
- Gerar a primeira ISO de teste.
- Testar inicialização em máquina virtual.

**Fase B — Identidade visual**
- Aplicar tema claro/escuro.
- Criar identidade visual própria.
- Configurar dock e barra superior.
- Ajustar menu/lançador conforme decisão pendente.
- Personalizar tela de login e tela de bloqueio.
- Integrar papéis de parede e animações configuráveis.

**Fase C — Instalação**
- Integrar Calamares.
- Configurar particionamento e instalação.
- Testar instalação em disco virtual.
- Confirmar que o sistema instalado inicia corretamente.

**Fase D — Experiência inicial**
- Criar onboarding.
- Implementar experiência de boas-vindas.
- Validar idioma, tema e configurações iniciais.

**Fase E — Gerenciamento do sistema**
- Definir backend da loja.
- Implementar uma primeira versão funcional da loja.
- Integrar notificações de atualização.
- Planejar fluxo de drivers com consentimento.

**Fase F — Qualidade e distribuição**
- Testes em hardware físico.
- Testes de instalação e atualização.
- Verificação de consumo de RAM e desempenho.
- Auditoria de licenças e segurança.
- Documentação de usuário e notas de versão.
- Publicação de uma versão de teste.

Esta sequência é uma sugestão de planejamento, não um compromisso de prazo ou uma promessa de que cada fase será simples.

## 8.4 Padrão de qualidade para cada funcionalidade

Antes de marcar uma funcionalidade como concluída, registrar:

- O que ela deveria fazer.
- Como foi implementada.
- Quais componentes e dependências utiliza.
- Como compilar ou instalar.
- Como testar.
- Resultado dos testes executados.
- Limitações conhecidas.
- Riscos e permissões necessárias.

“Arquivo criado” não é o mesmo que “funcionalidade pronta”. “Compila” não é o mesmo que “funciona corretamente”. “Funciona em uma VM” não é o mesmo que “compatibilidade ampla com hardware real”.

---

# 9. Metas de experiência e critérios de aceitação

As seguintes metas traduzem a visão do projeto em resultados que poderão ser testados. Os valores numéricos finais ainda precisam ser definidos.

## 9.1 Facilidade de uso

- Um usuário sem experiência em Linux deve conseguir iniciar o sistema e entender como abrir aplicativos.
- Instalar um aplicativo comum deve ser possível pela loja gráfica.
- Atualizar o sistema deve ser possível por uma interface gráfica.
- Tarefas cotidianas não devem exigir terminal.
- Mensagens de erro devem explicar o problema e, quando possível, indicar uma ação segura.

## 9.2 Aparência e consistência

- Dock inferior centralizado.
- Barra superior personalizada.
- Tema claro e escuro.
- Aparência integrada entre desktop e aplicativos próprios.
- Dolphin como gerenciador de arquivos padrão.
- Configurações KDE preservadas e personalizadas.
- Animações configuráveis.

## 9.3 Desempenho

- Consumo de RAM deve ser medido em condições definidas.
- Tempo de inicialização deve ser medido em hardware de referência.
- A interface deve permanecer responsiva em computadores que atendam aos requisitos mínimos.
- Efeitos visuais devem poder ser reduzidos.
- Não incluir serviços em segundo plano sem propósito documentado.

## 9.4 Instalação e recuperação

- A ISO deve inicializar em ambiente de teste suportado.
- Calamares deve identificar corretamente o destino de instalação.
- A instalação não pode apagar discos sem confirmação explícita.
- O sistema instalado deve inicializar e oferecer uma experiência funcional.
- Falhas devem produzir logs úteis.

## 9.5 Atualizações e pacotes

- A loja deve indicar origem dos aplicativos quando essa informação estiver disponível.
- Instalações devem ser executadas pelo backend correto.
- O sistema deve apresentar atualizações sem instalá-las silenciosamente contra a preferência do usuário.
- O repositório Konaro deve ter metadados verificáveis e assinados antes de ser utilizado em uma versão pública.

---

# 10. Riscos, limites e pontos de atenção

## 10.1 O Konaro não é um sistema operacional criado do zero

O projeto é uma distribuição Linux baseada em Debian. Ele criará integração, configuração, ferramentas, experiência e identidade próprias, mas reutilizará o kernel e muitos componentes consolidados.

Isso é intencional: desenvolver um kernel e todo o ecossistema do zero aumentaria drasticamente a complexidade sem contribuir para o objetivo principal do produto.

## 10.2 Compatibilidade ampla exige testes reais

“Funcionar em computadores antigos e modernos” é uma meta, não algo que possa ser garantido apenas pela escolha do Debian.

Compatibilidade depende de:

- CPU e arquitetura.
- GPU e driver.
- Wi-Fi e Bluetooth.
- Áudio.
- Firmware.
- UEFI/BIOS.
- Tipo de armazenamento.
- Memória disponível.
- Periféricos específicos.

A compatibilidade deve ser descrita com base em uma matriz de testes, não em suposições.

## 10.3 Loja de aplicativos é um componente sensível

Uma loja que instala software precisa tratar privilégios, dependências, transações, origem, assinaturas, falhas e atualizações. Não criar um instalador de pacotes rudimentar que execute comandos de forma insegura.

## 10.4 Calamares e Live Build precisam de integração

A escolha dessas ferramentas não elimina o trabalho de configuração. O instalador precisa funcionar corretamente no ambiente live e produzir uma instalação inicializável e consistente.

## 10.5 Atualizações podem quebrar sistemas

O ciclo anual não dispensa atualizações intermediárias. É preciso definir testes, canais, assinatura, rollback ou recuperação quando possível, e política de suporte.

## 10.6 Secure Boot ficará para depois

A ausência inicial de Secure Boot deve estar documentada. Não afirmar que o recurso é suportado até a implementação e validação correspondente.

## 10.7 Jogos não têm compatibilidade universal

Steam, Proton e Lutris facilitam o uso de jogos, mas não garantem que todo título funcione. Anti-cheats, DRM, drivers e políticas de cada desenvolvedor podem impedir a execução.

## 10.8 Licenças precisam ser respeitadas

A licença aberta do Konaro não transforma componentes de terceiros em software de licença única. Manter um inventário de licenças e cumprir obrigações de redistribuição.

---

# 11. Decisões ainda em aberto

Não inventar respostas para estes itens. Eles deverão ser definidos em etapas posteriores.

## 11.1 Perguntas da Etapa 6 — ambiente e execução

O responsável ainda não respondeu às perguntas abaixo:

1. **Computador de desenvolvimento:** processador, RAM, armazenamento e sistema operacional disponíveis.
2. **Ambiente Claude Code:** Windows 11 + WSL, Linux instalado, máquina virtual, servidor remoto ou outra opção.
3. **Testes:** disponibilidade de VirtualBox, VMware, QEMU/KVM e/ou pendrive para testes físicos.
4. **Hardware mínimo do Konaro:** a sugestão inicial discutida foi 4 GB de RAM, processador de 64 bits com 2 núcleos e 25 GB de armazenamento, mas esses números ainda NÃO foram aprovados.
5. **Idiomas:** ainda não foi escolhido se a primeira versão será apenas em português brasileiro, português e inglês, ou multilíngue.
6. **Ordem de desenvolvimento:** ainda não foi escolhida entre estruturar primeiro o GitHub/documentação, construir imediatamente uma ISO, criar primeiro protótipo visual ou fazer documentação/estrutura/protótipo em paralelo.

## 11.2 Outras decisões pendentes

- Nome e identidade visual final (logotipo, símbolo, tipografia e manual de marca).
- Versão exata do Debian.
- Versão e composição exatas do KDE Plasma.
- Tecnologias e linguagens para cada aplicativo próprio.
- Estrutura real e quantidade de repositórios GitHub.
- Nome da organização/conta GitHub.
- Licença exata do código original do Konaro.
- Requisitos mínimos oficiais.
- Navegador padrão.
- Seleção exata de aplicativos pré-instalados.
- Backend definitivo da loja.
- Política detalhada de atualização de segurança.
- Política de suporte de cada lançamento anual.
- Processo de upgrade entre versões principais.
- Idiomas da animação de boas-vindas.
- Se haverá menu/lançador de aplicativos próprio, animação de boot própria ou ambos.
- Detalhes da assistência de IA: local/remota/híbrida, modelo, permissões e privacidade.
- Política de telemetria (não foi solicitada nem aprovada; não implementar por padrão sem discussão).
- Canal de testes e estratégia de publicação.
- Requisitos de assinatura do repositório próprio.
- Estratégia de suporte a impressoras, placas de vídeo, Wi-Fi e outros dispositivos.
- Estratégia de acessibilidade.

---

# 12. Histórico resumido das etapas de planejamento

## Etapa 1 — Identidade e visão

O responsável estabeleceu que deseja um sistema desktop baseado em Debian, para o público geral, com identidade independente e filosofia equilibrada. A visão central é uma experiência muito simples e intuitiva, especialmente para quem não conhece Linux, com aparência bastante semelhante ao macOS. O usuário comum não deverá precisar recorrer ao terminal para tarefas cotidianas. Também foram destacados desempenho, fluidez e consumo de RAM.

## Etapa 2 — Arquitetura

Foram escolhidos KDE Plasma, visual inspirado no macOS, equilíbrio entre aparência e desempenho, loja própria, ferramentas gráficas, suporte a formatos de pacotes amplos, atualizações estáveis e suporte desejado a hardware antigo e moderno.

## Etapa 3 — Identidade visual e experiência

Foram escolhidos visual moderno inspirado no macOS, cores neutras, temas claro e escuro, dock centralizado na parte inferior, barra superior personalizada, Dolphin, configurações KDE personalizadas, boas-vindas guiadas e animações configuráveis.

Também foi descrita a ideia de uma sequência de saudações em vários idiomas que termina com “Welcome to Konaro”. Foi recomendada a separação dessa animação do processo crítico de login/boot. A expressão “menu de iniciar próprio” ainda precisa ser esclarecida para saber se também significa um lançador de aplicativos próprio.

## Etapa 4 — Funcionalidades

Foram definidos loja própria, detecção de drivers com consentimento para instalação, atualizações notificadas e controladas pelo usuário, backup fora das prioridades iniciais, segurança equilibrada, foco em jogos com Steam/Proton/Lutris, assistente de IA opcional e conjunto mínimo de aplicativos pré-instalados.

Também foi reforçado que a intenção é aceitar formatos e fontes de aplicativos de maneira ampla, mas a compatibilidade real e a segurança precisam ser verificadas.

## Etapa 5 — Infraestrutura

O responsável escolheu Debian Live Build, Calamares, kernel Debian, arquitetura 64 bits x86_64, Secure Boot posteriormente, repositórios híbridos Debian + Konaro, ciclo anual, GitHub, código aberto e Claude Code como ferramenta principal de desenvolvimento.

---

# 13. Próxima ação recomendada

A próxima etapa deve transformar este documento em um plano executável, sem começar a criar funcionalidades desconectadas.

Ordem recomendada:

1. Responder às perguntas pendentes da Etapa 6.
2. Verificar o ambiente e as ferramentas disponíveis.
3. Definir a versão Debian e o conjunto de pacotes inicial.
4. Aprovar a estrutura de repositórios e diretórios.
5. Criar um protótipo mínimo do processo Debian Live Build.
6. Gerar a primeira ISO de prova de conceito.
7. Testar boot e desktop em máquina virtual antes de ampliar o escopo.

**Primeiro grande marco:** uma ISO de desenvolvimento do Konaro que inicialize, carregue KDE Plasma com configurações iniciais próprias e permita validar a direção visual. Depois disso, avançar para integração do Calamares e demais ferramentas.

---

# 14. Prompt inicial sugerido para Claude Code

O texto abaixo pode ser utilizado como instrução inicial ao abrir o projeto com Claude Code:

> Você está trabalhando no projeto Konaro OS. Leia integralmente o arquivo `KONARO_OS_MASTER_SPEC.md` antes de agir. Ele é a referência central do projeto e distingue decisões confirmadas, objetivos, ideias, recomendações e questões pendentes.
>
> Não comece criando vários aplicativos ou um sistema inteiro de uma vez. Primeiro, inspecione o ambiente e os arquivos existentes, resuma a arquitetura que entendeu e apresente um plano incremental para construir uma primeira ISO Debian Live com KDE Plasma. Use Debian Live Build, Calamares e o kernel Debian conforme as decisões do documento. O alvo inicial é x86_64.
>
> Preserve a visão central: distribuição Debian com identidade própria, experiência inspirada no macOS, interface gráfica em primeiro lugar, facilidade para iniciantes, desempenho equilibrado, estabilidade e ferramentas próprias somente onde agregarem valor.
>
> Não transforme recomendações provisórias em decisões definitivas. Não invente respostas para os pontos em aberto. Não alegue que recursos foram testados quando não foram. Antes de operações destrutivas, alterações de boot/partições, instalação em discos reais, publicação de pacotes ou mudanças de segurança, explique o risco e peça autorização.
>
> Mantenha a construção reproduzível, documente comandos e decisões, implemente em etapas pequenas e reporte sempre o que foi criado, o que foi testado, o resultado e o que permanece pendente. O responsável pelo projeto supervisiona e aprova decisões importantes.

---

**Fim do documento mestre — Konaro OS v0.5**
