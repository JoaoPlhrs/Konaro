"""Konaro OS — biblioteca comum das ferramentas gráficas (loja, atualizador,
drivers e boas-vindas).

As ferramentas são interfaces sobre mecanismos maduros do sistema:
PackageKit (pacotes Debian, com autorização via polkit) e Flatpak (Flathub).
Nenhuma delas executa comandos de pacote por conta própria como root.
"""

__version__ = "0.1.0"
