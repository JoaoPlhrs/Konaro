# 0004 — Animação "olá → Welcome to Konaro" como splash do Plasma

- **Estado:** Provisória (o documento mestre deixa em aberto se "menu de iniciar próprio"
  significa lançador, animação ou ambos — §4.5. Esta ADR trata **só da animação**.)
- **Data:** 2026-11-22

## Contexto
O §4.5 pede saudações rápidas em vários idiomas terminando em "Welcome to Konaro",
**separadas** do boot/login para não comprometer a confiabilidade, curta, sem bloquear e
com tratamento para hardware lento ou sem animação.

## Decisão
Implementar como **tela de abertura (splash) do Plasma** — `Splash.qml` no tema global
`org.konaro.desktop`, exibida pelo `ksplashqml` enquanto a sessão carrega.

- Não participa do boot (GRUB/kernel/initramfs) nem do login (SDDM).
- Fecha sozinha quando o Plasma termina de carregar — nunca atrasa a sessão.
- Se as animações estiverem desligadas (`Kirigami.Units.longDuration` = 0), mostra só a mensagem final.
- Pode ser trocada/desativada em *Configurações > Aparência > Tela de abertura*.

## Alternativas
- **Plymouth** (durante o boot): roda antes do sistema gráfico e no caminho crítico do boot. Rejeitada para esta função.
- **Tema do SDDM**: misturaria a animação com o login. Rejeitada.
- **App de boas-vindas próprio**: será necessário para o onboarding (Fase D), mas não para a animação.

## Pendências
- Lista final de idiomas (§11.2). A provisória usa só escritas latina, grega e cirílica,
  que a fonte Inter cobre; incluir CJK/árabe/devanágari exige fontes adicionais (+ tamanho da ISO).
- Em computadores rápidos a sessão pode carregar antes de a sequência terminar; nesse caso
  a animação é cortada (comportamento intencional: não bloquear).
