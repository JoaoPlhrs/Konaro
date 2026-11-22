# Pendências e perguntas em aberto

Itens que **não** podem ser decididos pelo Claude Code. Os marcados com *(provisório)*
têm um valor temporário só para destravar o build — ver
[decisions/0007](decisions/0007-padroes-provisorios.md).

## Perguntas da Etapa 6 (documento mestre §11.1)
1. **Computador de desenvolvimento** (CPU, RAM, disco, sistema). — sem resposta
2. **Onde o Claude Code roda** (Windows 11 + WSL, Linux, VM, servidor). — sem resposta.
   O primeiro build foi feito numa sessão Claude Code na nuvem (Ubuntu 24.04, sem KVM).
3. **Ferramentas de teste.** O responsável ainda não tem VM (resposta de 2026-11-22).
4. **Requisitos mínimos oficiais.** Sugestão anterior (4 GB RAM, 2 núcleos 64 bits,
   25 GB) **não aprovada**. Medições de RAM da ISO estão em [STATUS.md](STATUS.md).
5. **Idiomas da 1ª versão.** ✅ Decidido: português (Brasil) e inglês.
6. **Ordem de desenvolvimento.** Seguida a recomendação §13: ISO primeiro, em fases pequenas.

## Produto e identidade
- Nome/identidade final: logotipo, símbolo, tipografia, manual de marca. *(provisório: marca geométrica "K")*
- "Menu de iniciar próprio" = lançador próprio, animação, ou ambos? *(animação feita; lançador ainda é o Kickoff do Plasma)*
- Lista final do catálogo da Loja *(provisório: 47 apps curados)*.
- Idiomas da animação de boas-vindas. *(provisório: 11 saudações em escrita latina/grega/cirílica)*
- Navegadores: ✅ decidido — Firefox, Brave e Ungoogled Chromium, escolhidos no instalador.
- Seleção final de aplicativos pré-instalados. *(provisório: 7 apps KDE)*
- Detalhes do dock (ocultação, tamanho, indicadores) e da barra superior — validar com uso real.

## Técnica e infraestrutura
- Licença do código e da arte originais do Konaro (ver [LICENSES.md](LICENSES.md)). O responsável
  disse que "não é necessária agora" (MIT foi citada como aceitável). **Bloqueia publicação.**
- Organização/conta GitHub e estrutura de repositórios.
- Repositório APT Konaro: hospedagem, chaves de assinatura, processo de publicação.
  *(o responsável pediu para deixar para depois; sem ele, os pacotes `konaro-*` do sistema
  instalado não recebem atualizações)*
- Loja: integrar AppStream (capturas de tela, catálogo completo) — hoje é catálogo curado.
- Política de atualizações de segurança, suporte de cada versão anual e upgrade entre versões.
- Relação entre o calendário anual do Konaro e as versões estáveis do Debian.
- Ferramenta de firewall definitiva *(provisório: ufw)*.
- Assistente de IA: local/remoto, modelo, permissões, privacidade. **Nada implementado.**
- Telemetria: não solicitada; **nada implementado**.
- Estratégia de acessibilidade, impressoras, GPUs (NVIDIA proprietário), Wi-Fi.
- Secure Boot (adiado por decisão; o responsável confirmou que não é necessário agora).
