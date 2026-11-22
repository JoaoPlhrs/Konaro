#!/usr/bin/env python3
"""Konaro OS — grava a fonte escolhida na página `packagechooser@fonts` como padrão
do sistema instalado (/etc/xdg/kdeglobals e a tela de login)."""

import libcalamares

from konaro import fonts


def pretty_name():
    return "Aplicando a fonte / Applying the font"


def chosen():
    gs = libcalamares.globalstorage
    value = None
    for key in gs.keys():
        if key.startswith("packagechooser_") and "fonts" in key:
            value = gs.value(key)
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if isinstance(value, str):
        value = value.split(",")[0].strip()
    return value or fonts.DEFAULT


def run():
    root = libcalamares.globalstorage.value("rootMountPoint")
    applied = fonts.apply_system(root, chosen())
    libcalamares.utils.debug("konarofonts: %s" % applied)
    return None
