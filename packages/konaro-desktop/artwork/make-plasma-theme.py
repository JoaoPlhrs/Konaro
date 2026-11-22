#!/usr/bin/env python3
"""Gera o tema do Plasma "Konaro" (vidro) a partir das molduras translúcidas do Breeze.

Só o que FLUTUA fica translúcido com desfoque por trás: painéis (barra superior e
dock), popups e menus do Plasma, dicas e widgets da área de trabalho. Janelas de
aplicativos não são afetadas (elas não usam o tema do Plasma).

Uso: make-plasma-theme.py <dir do tema Breeze "default"> <dir de saída>
O resultado é versionado em data/usr/share/plasma/desktoptheme/konaro/.
Derivado do Breeze (KDE, LGPL); ver docs/LICENSES.md.
"""

import gzip
import json
import os
import re
import sys

# opacidade do fundo de cada superfície (Breeze usa ~0,85–0,9)
TARGETS = {
    "translucent/dialogs/background.svgz": 0.74,        # popups, menus do Plasma, lançador
    "translucent/widgets/panel-background.svgz": 0.62,  # barra superior e dock
    "translucent/widgets/background.svgz": 0.66,        # widgets na área de trabalho
    "translucent/widgets/tooltip.svgz": 0.82,           # dicas
}

PLASMARC = """[ContrastEffect]
enabled=true
contrast=0.25
intensity=1.0
saturation=1.9

[BlurBehindEffect]
enabled=true

[AdaptiveTransparency]
enabled=true
"""

METADATA = {
    "KPlugin": {
        "Authors": [{"Name": "Konaro OS Project"}, {"Name": "KDE Visual Design Group (Breeze)"}],
        "Category": "",
        "Description": "Konaro glass: translucent, blurred panels, popups and widgets",
        "Description[pt_BR]": "Vidro Konaro: painéis, popups e widgets translúcidos com desfoque",
        "Id": "konaro",
        "License": "LGPL",
        "Name": "Konaro",
        "Version": "0.1",
    },
    "X-Plasma-API": "5.0",
}


def soften(svg, opacity):
    """Ajusta a opacidade dos elementos de fundo (classe ColorScheme-Background)."""
    count = 0

    def fix(match):
        nonlocal count
        element = match.group(0)
        if "ColorScheme-Background" not in element:
            return element
        count += 1
        element = re.sub(r"(?<![-\w])opacity:[0-9.]+", "opacity:%.2f" % opacity, element)
        element = re.sub(r"fill-opacity:[0-9.]+", "fill-opacity:1", element)
        if "opacity:" not in re.sub(r"fill-opacity|stop-opacity", "", element):
            element = element.replace('style="', 'style="opacity:%.2f;' % opacity, 1)
        return element

    svg = re.sub(r"<(?:rect|path)\b[^>]*>", fix, svg, flags=re.S)
    return svg, count


def main(src, out):
    for rel, opacity in TARGETS.items():
        with gzip.open(os.path.join(src, rel), "rt", encoding="utf-8") as fh:
            svg = fh.read()
        svg, count = soften(svg, opacity)
        if count == 0:
            sys.exit("nenhum elemento de fundo encontrado em %s" % rel)
        dest = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with gzip.open(dest, "wt", encoding="utf-8") as fh:
            fh.write(svg)
        print("%-46s %2d elementos -> opacidade %.2f" % (rel, count, opacity))
    with open(os.path.join(out, "plasmarc"), "w", encoding="utf-8") as fh:
        fh.write(PLASMARC)
    with open(os.path.join(out, "metadata.json"), "w", encoding="utf-8") as fh:
        json.dump(METADATA, fh, indent=4, ensure_ascii=False)
        fh.write("\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
