# Konaro OS Fênix Lite — edição para computadores antigos

Construída com `scripts/build-iso.sh --edition lite`. Parte da configuração normal
(`live/config`) e aplica por cima:

- `remove.list` — pacotes tirados das listas (efeito de vidro, temas de ícones extras,
  gerenciador de senhas, atualização de firmware);
- `config/package-lists` — pacotes que só a Lite tem (`konaro-lite`: memória comprimida,
  efeitos leves, Firefox mais leve, desenho por software em placas sem OpenGL 2);
- `config/archives` — impede que pacotes pesados entrem por "recomendação";
- `config/hooks` — marca a edição e desliga serviços dispensáveis.

O visual (tema, dock, barra superior, Iniciar, tela de login, papéis de parede e os
apps do Konaro) é o mesmo da edição normal.
