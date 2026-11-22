#!/usr/bin/env python3
"""Gera as decorações de janela Aurorae "Konaro" e "Konaro Dark".

- Barra de título na cor do cabeçalho do esquema Konaro (une título e barra de ferramentas).
- Botões "semáforo" à esquerda: fechar (vermelho), minimizar (amarelo), maximizar
  (verde); o símbolo aparece ao passar o mouse; em janelas inativas ficam cinza.
- Cantos superiores arredondados e sombra suave.

Uso: make-aurorae.py <dir de saída>   (ex.: data/usr/share/aurorae/themes)
Arte original do projeto.
"""

import os
import sys

# Geometria (px). O SVG é um "frame" de 9 partes; a parte de cima inclui a barra de título.
PAD_SIDE, PAD_TOP, PAD_BOTTOM = 18, 10, 26     # espaço da sombra
TITLE = 34                                     # altura da barra de título
RADIUS = 11
BORDER = 1                                     # contorno lateral/inferior
W = 160                                        # largura do desenho de referência
H = PAD_TOP + TITLE + 40 + BORDER + PAD_BOTTOM

THEMES = {
    "Konaro": {
        "active": "#E4E4E8", "inactive": "#ECECEE", "edge": "#C9C9CE", "edge_inactive": "#D6D6DA",
        "text": "29,29,31", "text_inactive": "120,120,125", "shadow": 0.30,
        "idle": "#C7C7CC", "idle_edge": "#B4B4B9",
    },
    "KonaroDark": {
        "active": "#2A2A2E", "inactive": "#1F1F22", "edge": "#45454A", "edge_inactive": "#36363A",
        "text": "242,242,247", "text_inactive": "140,140,146", "shadow": 0.55,
        "idle": "#4A4A4F", "idle_edge": "#5A5A5F",
    },
}
LIGHTS = {"close": ("#FF5F57", "#E0443E"), "minimize": ("#FEBC2E", "#DEA123"), "maximize": ("#28C840", "#1AAB29")}


def frame_art(fill, edge, shadow):
    """Moldura completa (sombra + corpo com cantos superiores arredondados) como SVG."""
    x0, y0 = PAD_SIDE, PAD_TOP
    x1, y1 = W - PAD_SIDE, H - PAD_BOTTOM
    body = ('<path d="M%d,%d V%d A%d,%d 0 0 1 %d,%d H%d A%d,%d 0 0 1 %d,%d V%d Z" fill="%s" stroke="%s" stroke-width="1"/>'
            % (x0, y1, y0 + RADIUS, RADIUS, RADIUS, x0 + RADIUS, y0, x1 - RADIUS, RADIUS, RADIUS, x1, y0 + RADIUS, y1,
               fill, edge))
    shadow_rect = ('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="#000" opacity="%.2f" filter="url(#blur)"/>'
                   % (x0, y0 + 4, x1 - x0, y1 - y0, RADIUS, shadow))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
            '<defs><filter id="blur" x="-50%%" y="-50%%" width="200%%" height="200%%">'
            '<feGaussianBlur stdDeviation="7"/></filter></defs>%s%s</svg>' % (W, H, W, H, shadow_rect, body))


def parts():
    cut_top = PAD_TOP + TITLE                 # parte de cima: sombra + barra de título
    cut_bot = H - PAD_BOTTOM - BORDER         # parte de baixo: contorno + sombra
    left_cut, right_cut = PAD_SIDE + RADIUS + 2, W - PAD_SIDE - RADIUS - 2
    return {
        "topleft": (0, 0, left_cut, cut_top),
        "top": (left_cut, 0, right_cut - left_cut, cut_top),
        "topright": (right_cut, 0, W - right_cut, cut_top),
        "left": (0, cut_top, left_cut, cut_bot - cut_top),
        "center": (left_cut, cut_top, right_cut - left_cut, cut_bot - cut_top),
        "right": (right_cut, cut_top, W - right_cut, cut_bot - cut_top),
        "bottomleft": (0, cut_bot, left_cut, H - cut_bot),
        "bottom": (left_cut, cut_bot, right_cut - left_cut, H - cut_bot),
        "bottomright": (right_cut, cut_bot, W - right_cut, H - cut_bot),
    }


def rasterize(svg_text, scale=2):
    """SVG -> PNG (rsvg-convert) -> QImage-free recorte via Python puro (PNG por parte)."""
    import subprocess, tempfile, base64
    with tempfile.TemporaryDirectory() as tmp:
        src, png = os.path.join(tmp, "f.svg"), os.path.join(tmp, "f.png")
        open(src, "w").write(svg_text)
        subprocess.run(["rsvg-convert", "-z", str(scale), src, "-o", png], check=True)
        pieces = {}
        for name, (x, y, w, h) in parts().items():
            out = os.path.join(tmp, name + ".png")
            subprocess.run(["convert", png, "-crop", "%dx%d+%d+%d" % (w * scale, h * scale, x * scale, y * scale),
                            "+repage", out], check=True)
            pieces[name] = base64.b64encode(open(out, "rb").read()).decode()
        return pieces


def frame(prefix, fill, edge, shadow, offset_y=0):
    pieces = rasterize(frame_art(fill, edge, shadow))
    out = []
    for name, (x, y, w, h) in parts().items():
        out.append('<image id="%s-%s" x="%d" y="%d" width="%d" height="%d" preserveAspectRatio="none" '
                   'xlink:href="data:image/png;base64,%s"/>' % (prefix, name, x, y + offset_y, w, h, pieces[name]))
    return "\n".join(out)


def decoration_svg(t):
    return """<?xml version="1.0" encoding="UTF-8"?>
<!-- Konaro OS — decoração de janela (Aurorae). Arte original do projeto, gerada por
     artwork/make-aurorae.py: cada parte do "frame" é uma imagem 2x embutida. -->
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">
<!-- bordas esticadas (não repetidas): evita "listras" nas laterais e na base -->
<rect id="hint-stretch-borders" x="0" y="0" width="1" height="1" fill="none"/>
<rect id="decoration-hint-stretch-borders" x="0" y="0" width="1" height="1" fill="none"/>
<rect id="decoration-inactive-hint-stretch-borders" x="0" y="0" width="1" height="1" fill="none"/>
%s
%s
</svg>
""" % (W, H * 2, W, H * 2,
       frame("decoration", t["active"], t["edge"], t["shadow"]),
       frame("decoration-inactive", t["inactive"], t["edge_inactive"], t["shadow"] * 0.6, offset_y=H))


GLYPHS = {
    "close": '<path d="M5.6,5.6 L10.4,10.4 M10.4,5.6 L5.6,10.4" stroke="#4D0000" stroke-opacity="0.75" stroke-width="1.3" stroke-linecap="round"/>',
    "minimize": '<path d="M5,8 H11" stroke="#5A3A00" stroke-opacity="0.75" stroke-width="1.4" stroke-linecap="round"/>',
    "maximize": '<path d="M5.4,8 H10.6 M8,5.4 V10.6" stroke="#003F00" stroke-opacity="0.75" stroke-width="1.4" stroke-linecap="round"/>',
}


def button_svg(kind, t):
    color, edge = LIGHTS["maximize" if kind == "restore" else kind]
    glyph = GLYPHS["maximize" if kind == "restore" else kind]

    def circle(state, fill, stroke, with_glyph=False, dim=False):
        g = glyph if with_glyph else ""
        overlay = '<circle cx="8" cy="8" r="6" fill="#000" opacity="0.15"/>' if dim else ""
        return ('<g id="%s-center"><rect width="16" height="16" fill="none"/>'
                '<circle cx="8" cy="8" r="6" fill="%s" stroke="%s" stroke-width="0.6"/>%s%s</g>'
                % (state, fill, stroke, overlay, g))

    states = [
        circle("active", color, edge),
        circle("hover", color, edge, with_glyph=True),
        circle("pressed", color, edge, with_glyph=True, dim=True),
        circle("inactive", t["idle"], t["idle_edge"]),
        circle("deactivated", t["idle"], t["idle_edge"]),
    ]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- Konaro OS — botão %s (arte original). -->\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">\n%s\n</svg>\n'
            % (kind, "\n".join(states)))


def rc(t):
    return """[General]
ActiveTextColor=%s
InactiveTextColor=%s
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=120
UseTextShadow=false
Shadow=true
DecorationPosition=0

[Layout]
BorderLeft=%d
BorderRight=%d
BorderBottom=%d
TitleEdgeTop=0
TitleEdgeBottom=0
TitleEdgeLeft=12
TitleEdgeRight=12
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=12
TitleEdgeRightMaximized=12
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight=%d
ButtonWidth=16
ButtonHeight=16
ButtonSpacing=6
ButtonMarginTop=%d
ExplicitButtonSpacer=8
PaddingTop=%d
PaddingBottom=%d
PaddingLeft=%d
PaddingRight=%d
""" % (t["text"], t["text_inactive"], BORDER, BORDER, BORDER, TITLE, (TITLE - 16) // 2,
       PAD_TOP, PAD_BOTTOM, PAD_SIDE, PAD_SIDE)


def metadata(name, label, label_pt):
    return """[Desktop Entry]
Name=%s
Name[pt_BR]=%s
Comment=Konaro OS window decoration with traffic-light buttons
Comment[pt_BR]=Decoração de janela do Konaro OS com botões semáforo
X-KDE-PluginInfo-Author=Konaro OS Project
X-KDE-PluginInfo-Name=%s
X-KDE-PluginInfo-Version=0.1
X-KDE-PluginInfo-Category=
X-KDE-PluginInfo-License=Pending
X-KDE-PluginInfo-EnabledByDefault=true
""" % (label, label_pt, name)


def main(out):
    labels = {"Konaro": ("Konaro", "Konaro"), "KonaroDark": ("Konaro Dark", "Konaro Escuro")}
    for name, t in THEMES.items():
        d = os.path.join(out, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "decoration.svg"), "w", encoding="utf-8") as fh:
            fh.write(decoration_svg(t))
        for kind in ("close", "minimize", "maximize"):
            with open(os.path.join(d, kind + ".svg"), "w", encoding="utf-8") as fh:
                fh.write(button_svg(kind, t))
        with open(os.path.join(d, "restore.svg"), "w", encoding="utf-8") as fh:
            fh.write(button_svg("restore", t).replace("botão restore", "botão restaurar"))
        with open(os.path.join(d, name + "rc"), "w", encoding="utf-8") as fh:
            fh.write(rc(t))
        with open(os.path.join(d, "metadata.desktop"), "w", encoding="utf-8") as fh:
            fh.write(metadata(name, *labels[name]))
        print("tema", name, "->", d)


if __name__ == "__main__":
    main(sys.argv[1])
