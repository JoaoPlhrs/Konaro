#!/usr/bin/env python3
"""Konaro OS — gera variantes de cor (destaque) dos esquemas Konaro Claro/Escuro.

O Konaro vem em grafite. Estas variantes trocam só a cor de destaque (seleção,
foco e realces), mantendo o resto do visual. Cores escolhidas pelo projeto.
Uso: make-color-variants.py PASTA_DOS_ESQUEMAS PASTA_DE_SAIDA
"""
import os
import re
import sys

ACCENTS = [
    # id, nome en, nome pt, destaque (claro), destaque (escuro)
    ("Blue", "Blue", "Azul", (0, 113, 227), (10, 132, 255)),
    ("Purple", "Purple", "Roxo", (137, 68, 196), (191, 90, 242)),
    ("Pink", "Pink", "Rosa", (214, 51, 108), (255, 69, 128)),
    ("Green", "Green", "Verde", (36, 138, 61), (48, 209, 88)),
    ("Orange", "Orange", "Laranja", (201, 102, 0), (255, 159, 10)),
    ("Teal", "Teal", "Turquesa", (0, 125, 140), (64, 200, 224)),
]


def rgb(c):
    return "%d,%d,%d" % c


def variant(text, base, accent, en, pt, dark):
    acc = rgb(accent)
    old = "174,174,178" if dark else "58,58,60"
    text = text.replace("DecorationFocus=" + old, "DecorationFocus=" + acc)
    text = text.replace("DecorationHover=" + old, "DecorationHover=" + acc)
    sel = re.search(r"\[Colors:Selection\]\n(.*?)\n\n", text, re.S)
    block = sel.group(1)
    new = re.sub(r"^BackgroundNormal=.*$", "BackgroundNormal=" + acc, block, flags=re.M)
    new = re.sub(r"^ForegroundNormal=.*$", "ForegroundNormal=255,255,255", new, flags=re.M)
    new = re.sub(r"^ForegroundActive=.*$", "ForegroundActive=255,255,255", new, flags=re.M)
    text = text.replace(block, new)
    text = re.sub(r"^ColorScheme=.*$", "ColorScheme=" + base + en, text, flags=re.M)
    text = re.sub(r"^Name=(.*)$", lambda m: "Name=%s · %s" % (m.group(1), en), text, flags=re.M)
    text = re.sub(r"^Name\[pt_BR\]=(.*)$", lambda m: "Name[pt_BR]=%s · %s" % (m.group(1), pt), text, flags=re.M)
    return text


def main(src, out):
    os.makedirs(out, exist_ok=True)
    for base, dark in (("KonaroLight", False), ("KonaroDark", True)):
        text = open(os.path.join(src, base + ".colors"), encoding="utf-8").read()
        for ident, en, pt, light_acc, dark_acc in ACCENTS:
            result = variant(text, base, dark_acc if dark else light_acc, ident, pt, dark)
            with open(os.path.join(out, base + ident + ".colors"), "w", encoding="utf-8") as fh:
                fh.write(result)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
