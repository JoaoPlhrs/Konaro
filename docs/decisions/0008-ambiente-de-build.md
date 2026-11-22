# 0008 — Ambiente de build: chroot Debian 13 + proxy APT opcional

- **Estado:** Provisória
- **Data:** 2026-11-22

## Contexto
O live-build deve rodar num Debian da mesma versão do alvo. O computador de
desenvolvimento do responsável ainda não foi informado (§11.1-1/2) e pode ser Windows +
WSL, Ubuntu, etc.

## Decisão
- Caminho principal: `scripts/build-iso.sh` num **Debian 13** (máquina, VM ou chroot).
- Para outros hosts Linux: `scripts/builder-chroot.sh` cria um chroot Debian 13 com
  `debootstrap` e roda o build lá dentro. Foi o caminho usado no primeiro build
  (host Ubuntu 24.04 na nuvem).
- `KONARO_APT_PROXY` permite usar um cache/proxy APT HTTP (ex.: `apt-cacher-ng`) só
  durante o build; o sistema final sempre aponta para os mirrors oficiais em HTTPS.
  As assinaturas GPG do Debian continuam sendo verificadas pelo APT.

## Não testado
- Build dentro do WSL2 (o live-build precisa de `mount`/loop; costuma funcionar no WSL2,
  mas não foi verificado).
- Build em Docker/Podman (exigiria contêiner privilegiado). Não incluído.
