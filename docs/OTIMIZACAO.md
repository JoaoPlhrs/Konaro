# Teste de otimização — Konaro OS (build 6) × Windows 11

Data: 2026-11-22 · Konaro OS 0.1.0-dev6 (build 6 "Leve")

> **Leia antes:** o Konaro foi medido por nós, numa máquina virtual. O Windows 11 **não
> foi rodado** neste ambiente (não temos licença nem hardware para isso); os números dele
> vêm de testes publicados por terceiros e da Microsoft, em outros computadores. Por isso
> a comparação é **indicativa**, não um benchmark lado a lado. Para um teste justo, rode os
> dois no mesmo PC (instruções no fim).

## Números

| Item | Konaro OS (build 6) | Windows 11 | Fonte do Windows |
|---|---|---|---|
| Tamanho do instalador (ISO) | **2,7 GB** | — (não encontrado em fonte oficial) | — |
| Espaço em disco depois de instalado | **~6,3 GB** (sistema completo, sem pontos de restauração) | requisito mínimo: **64 GB** livres | [Microsoft — requisitos](https://learn.microsoft.com/windows/whats-new/windows-11-requirements) |
| RAM mínima | 2 GB funciona; **4 GB recomendado** | **4 GB** (mínimo oficial) | [Microsoft — requisitos](https://learn.microsoft.com/windows/whats-new/windows-11-requirements) |
| RAM em uso, sistema parado | **~1,5 GB** (área de trabalho + widgets + terminal aberto, sessão live) | ~2,8–4,1 GB (PC de 8 GB, instalação nova, 25H2/26H2) | [Windows Central](https://windowscentral.com/microsoft/windows-11/windows-11-25h2-26h2-tested-8gb-pc), [Windows Latest](https://www.windowslatest.com/2026/10/21/microsoft-says-its-optimizing-windows-11-for-8gb-pcs-so-i-tested-26h2-on-an-8gb-laptop/) |
| RAM em uso em PCs com muita memória | não muda muito (o Linux usa o resto como cache, liberado na hora) | 6–9 GB no boot em PCs de 16–32 GB | [HWBusters](https://hwbusters.com/news/windows-11-26h2-trims-up-to-2gb-of-ram-at-boot-but-8gb-pcs-still-see-nothing/), [Microsoft Tech Community](https://techcommunity.microsoft.com/t5/windows-11/is-it-normal-for-windows-11-to-occupy-6-8gb-of-memory-on-startup/m-p/4486332) |
| Pacotes/apps de fábrica | 1.819 pacotes; apps visíveis: Firefox, Arquivos, Terminal, Bloco de notas, Fotos, PDF, Captura, Compactador + ferramentas Konaro | inclui apps e serviços pré-instalados (varia por edição/fabricante) | — |
| Telemetria | **nenhuma** | coleta de diagnóstico (configurável, não desligável por completo nas edições Home/Pro) | — |
| Exige TPM 2.0 / CPU recente | **não** (roda em PCs antigos de 64 bits) | **sim** (TPM 2.0, UEFI, lista de CPUs) | [Microsoft — requisitos](https://learn.microsoft.com/windows/whats-new/windows-11-requirements) |

### Como o Konaro foi medido
- VM QEMU com 6 GB de RAM, firmware UEFI **com Secure Boot ligado**, emulação de CPU (sem
  aceleração), sessão live do Konaro com a área de trabalho, os widgets e o Konsole abertos.
- `free -m`: 1.513–1.581 MB "usada" (o "buff/cache" de ~1,2 GB é cache de disco, liberado
  automaticamente quando um app precisa).
- `pgrep -c .`: 147 processos — **inclui threads do kernel**, que o Gerenciador de Tarefas do
  Windows não mostra; por isso não comparamos contagem de processos.
- Espaço instalado: tamanho do sistema de arquivos da imagem (6,3 GB).

### O que estas medidas NÃO mostram (ainda)
- **Tempo de boot**: a emulação sem aceleração é várias vezes mais lenta que um PC real;
  o número não seria representativo. Precisa de hardware real.
- **Desempenho em jogos e apps**: precisa de hardware real com GPU.
- **Sistema instalado** (não live): deve usar um pouco menos de RAM que a sessão live,
  que guarda alterações na memória.

## Conclusão
Pelos números disponíveis, o Konaro **está otimizado**: cabe numa ISO de 2,7 GB, ocupa
~6 GB instalado (contra o mínimo de 64 GB do Windows 11), usa **cerca de metade ou menos da
RAM** que o Windows 11 usa parado num PC de 8 GB, não exige TPM nem CPU recente e não tem
telemetria. A confirmação definitiva é um teste lado a lado no mesmo computador.

## Teste justo no seu PC (recomendado)
1. Instale os dois no mesmo computador (ou em VMs iguais, mesma RAM/CPU).
2. Ligue, faça login, **espere 5 minutos** sem abrir nada.
3. Konaro: abra o Terminal e rode `free -m` (coluna "usada") e `systemd-analyze` (tempo de boot).
   Windows: Gerenciador de Tarefas → Desempenho → Memória "Em uso"; tempo de boot com um cronômetro
   ou `Get-WinEvent` (evento 100 do Diagnostics-Performance).
4. Anote também o espaço usado no disco (Konaro: `df -h /`; Windows: Explorador → Este Computador).
