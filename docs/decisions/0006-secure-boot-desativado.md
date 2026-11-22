# 0006 — Secure Boot desativado na ISO de desenvolvimento

- **Estado:** Aceita (decisão do responsável: "Secure Boot — implementar posteriormente", §6.4)
- **Data:** 2026-11-22

## Decisão
`lb config --uefi-secure-boot disable`. A ISO **não** inicia em máquinas com Secure Boot
ligado; o usuário precisa desativá-lo no firmware. Isso deve constar nas notas de versão.

## Caminho futuro (não implementado)
O Konaro usa kernel e GRUB **do Debian**, sem modificação. O caminho natural é reutilizar
a cadeia assinada do Debian (`shim-signed` + `grub-efi-amd64-signed`, opção `auto` do
live-build), sem esquema de assinatura próprio — exatamente como o §6.4 recomenda.
Precisa de testes com Secure Boot ligado em VM (OVMF com chaves MS) e em hardware real.
