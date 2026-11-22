# 0005 — Firewall: ufw ativo por padrão + plasma-firewall

- **Estado:** Provisória
- **Data:** 2026-11-22

## Contexto
Decisão do §5.5: segurança equilibrada com firewall. A ferramenta não foi escolhida.

## Decisão
`ufw` habilitado por padrão (política do Debian: **bloquear entrada, permitir saída**),
com o módulo gráfico `plasma-firewall` em Configurações.

## Alternativas
- **firewalld**: mais recursos (zonas), também suportado pelo `plasma-firewall`, porém
  mais complexo e mais pesado (daemon Python residente). Reavaliar se for necessário.
- **Sem firewall ativo** (padrão do Debian): contraria a direção de segurança.

## Riscos
- Bloquear entrada pode afetar compartilhamento de rede local (ex.: KDE Connect, se
  instalado no futuro). O usuário libera pelo módulo gráfico.
