# Konaro — sistema de design das ferramentas próprias

Vale para a Loja, Boas-vindas, Atualizações, Drivers e a identidade do instalador.

## Conceito: "o sistema é neutro; a cor vem dos apps"
A interface é grafite e névoa, sem cor de destaque. A única cor da tela vem dos
**ícones dos aplicativos**, que aparecem ampliados e desfocados como uma luz atrás do
destaque (*spotlight*). É o único elemento ousado; todo o resto é quieto.

## Cores
| Token | Claro | Escuro | Uso |
|---|---|---|---|
| `paper` | `#F5F5F7` | `#161618` | fundo da janela |
| `surface` | `#FFFFFF` | `#1F1F22` | cartões, páginas |
| `raised` | `#FFFFFF` | `#2A2A2E` | destaque, popups |
| `rail` | `#ECECEF` | `#1B1B1E` | trilho de navegação |
| `ink` | `#1D1D1F` | `#F5F5F7` | texto principal e botão principal |
| `stone` | `#6E6E73` | `#A1A1A6` | texto secundário (≥ 4,5:1) |
| `hairline` | `#D2D2D7` | `#38383C` | divisórias, contornos |
| `fill` | `#E8E8ED` | `#2C2C30` | hover, campos |
Cores de estado só em mensagens: sucesso `#1F8A4C`/`#32D74B`, erro `#C42B1C`/`#FF6961`.

## Tipografia
Inter Display (títulos, 700, espaçamento −0,5 px) e Inter (texto). Escala: 32 · 24 · 18 · 15 · 13 · 11.
Frases em caixa normal; sem rótulos em maiúsculas.

## Forma e espaço
Raios por hierarquia: destaque 20, blocos 16, cartões 14, controles 10, botões em pílula.
Espaçamento 4 · 8 · 12 · 16 · 24 · 32 · 48. Divisórias finas em vez de sombras; sombra só no que flutua.

## Movimento
Só como resposta a uma ação: pressionar, abrir página, progresso de instalação.
Respeita "Reduzir animações" do sistema.

## Familiaridade para quem vem do Windows
Trilho lateral com ícone + nome (como a Microsoft Store), busca no topo, botão
"Instalar"/"Abrir" sempre no mesmo lugar, página do app dentro da janela com "Voltar".

## Área de trabalho
- Só o que **flutua** é translúcido com desfoque: barra superior, dock, menus, popups,
  dicas, widgets e notificações. Janelas de aplicativos continuam opacas.
- Botões de janela "semáforo" (fechar, minimizar, maximizar) à esquerda, cinza em
  janelas inativas.
- Dock: os ícones sobem e crescem suavemente sob o ponteiro.
