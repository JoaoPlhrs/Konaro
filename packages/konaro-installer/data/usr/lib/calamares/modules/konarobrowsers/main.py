#!/usr/bin/env python3
"""Konaro OS — mantém no sistema instalado apenas os navegadores escolhidos.

A escolha vem da página `packagechooser@browsers` (chave de GlobalStorage
"packagechooser_browsers"). Os navegadores não escolhidos são removidos do
sistema de destino e o primeiro escolhido vira o navegador padrão.
"""

import configparser
import os

import libcalamares
from libcalamares.utils import target_env_call

ORDER = ["firefox", "brave", "ungoogled"]
BROWSERS = {
    "firefox": {"apt": ["firefox-esr", "firefox-esr-l10n-pt-br"], "desktop": "firefox-esr.desktop"},
    "brave": {"apt": ["brave-browser", "brave-keyring"], "desktop": "brave-browser.desktop",
              "files": ["/etc/apt/sources.list.d/brave.list",
                        "/etc/apt/sources.list.d/brave-browser-release.list"]},
    "ungoogled": {"flatpak": "io.github.ungoogled_software.ungoogled_chromium",
                  "desktop": "io.github.ungoogled_software.ungoogled_chromium.desktop"},
}
MIME = ["text/html", "application/xhtml+xml", "x-scheme-handler/http", "x-scheme-handler/https"]


def pretty_name():
    return "Configurando navegadores / Configuring browsers"


def chosen():
    gs = libcalamares.globalstorage
    value = None
    for key in gs.keys():
        if key.startswith("packagechooser_") and "browsers" in key:
            value = gs.value(key)
    if value is None and gs.contains("packagechooser_browsers"):
        value = gs.value("packagechooser_browsers")
    if isinstance(value, str):
        value = [v.strip() for v in value.split(",")]
    selected = [b for b in ORDER if value and b in value]
    libcalamares.utils.debug("konarobrowsers: selection %r -> %r" % (value, selected))
    return selected


def set_default(root, desktop):
    path = os.path.join(root, "etc/xdg/mimeapps.list")
    parser = configparser.ConfigParser(interpolation=None, delimiters=("=",))
    parser.optionxform = str
    if os.path.exists(path):
        parser.read(path, encoding="utf-8")
    if not parser.has_section("Default Applications"):
        parser.add_section("Default Applications")
    for mime in MIME:
        parser.set("Default Applications", mime, desktop)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        parser.write(fh, space_around_delimiters=False)


def run():
    selected = chosen()
    if not selected:
        # Nada escolhido (não deveria acontecer: a página exige ao menos um).
        return None
    root = libcalamares.globalstorage.value("rootMountPoint")
    for name in ORDER:
        if name in selected:
            continue
        info = BROWSERS[name]
        if "apt" in info:
            target_env_call(["env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "purge", "-y"] + info["apt"])
        if "flatpak" in info:
            target_env_call(["flatpak", "uninstall", "--system", "-y", "--noninteractive", info["flatpak"]])
            target_env_call(["flatpak", "uninstall", "--system", "-y", "--noninteractive", "--unused"])
        for path in info.get("files", []):
            full = os.path.join(root, path.lstrip("/"))
            if os.path.exists(full):
                os.remove(full)
    target_env_call(["env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "autoremove", "-y"])
    set_default(root, BROWSERS[selected[0]]["desktop"])
    return None
