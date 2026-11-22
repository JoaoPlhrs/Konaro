"""Ajuda Konaro — "Onde está…?" para quem vem do Windows (e do macOS).

Uma busca simples: o usuário digita o nome que conhece ("Painel de Controle",
"Gerenciador de Tarefas", "Windows Update"…) e vê onde fica no Konaro, com um
botão para abrir direto. Também traz atalhos de teclado e perguntas frequentes.
Funciona sem internet.
"""

import argparse
import sys

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSlot


from .i18n import _
from .launcher import launch, open_desktop_app

# (o que a pessoa conhece, onde fica no Konaro, como chegar lá, ícone, ação)
# ação: "app:<arquivo .desktop>" ou "cmd:<programa> <args>"
WHERE = [
    ("Control Panel", "System Settings", "Open it from the dock or search for \"Settings\".",
     "preferences-system", "app:systemsettings.desktop"),
    ("File Explorer", "Files (Dolphin)", "The folder icon in the dock. Shortcut: Super + E.",
     "system-file-manager", "app:org.kde.dolphin.desktop"),
    ("Task Manager (Ctrl+Alt+Del)", "System Monitor", "Search for \"Monitor\" or press Ctrl + Esc.",
     "utilities-system-monitor", "app:org.kde.plasma-systemmonitor.desktop"),
    ("Microsoft Store", "Konaro Store", "The bag icon in the dock. Apps install with one click.",
     "konaro-store", "app:konaro-store.desktop"),
    ("Windows Update", "Konaro Updates", "Notifies you when there are updates and never installs without asking.",
     "system-software-update", "app:konaro-updater.desktop"),
    ("Device Manager / drivers", "Konaro Drivers", "Finds the right driver for your graphics card and Wi-Fi.",
     "preferences-desktop-peripherals", "app:konaro-drivers.desktop"),
    ("Start menu", "Konaro Start", "Press the Windows (Super) key or click the logo at the top left.",
     "konaro-start", ""),
    ("Add or remove programs", "Konaro Store > Library", "Open the Store and go to Library to remove apps.",
     "edit-delete", "cmd:konaro-store --category installed"),
    ("Command Prompt / PowerShell", "Terminal (Konsole)", "Search for \"Terminal\". Shortcut: Ctrl + Alt + T.",
     "utilities-terminal", "app:org.kde.konsole.desktop"),
    ("Notepad", "KWrite", "A simple text editor.", "accessories-text-editor", "app:org.kde.kwrite.desktop"),
    ("Photos", "Gwenview", "Opens images when you double-click them.", "gwenview", "app:org.kde.gwenview.desktop"),
    ("PDF reader (Adobe Reader)", "Okular", "Opens PDF files and lets you sign and annotate them.",
     "okular", "app:org.kde.okular.desktop"),
    ("Snipping Tool (Win+Shift+S)", "Spectacle", "Press Print Screen, or Meta + Shift + S for an area.",
     "spectacle", "app:org.kde.spectacle.desktop"),
    ("WinRAR / 7-Zip", "Ark", "Double-click a .zip or .rar file to open it.", "ark", "app:org.kde.ark.desktop"),
    ("Clipboard history (Win+V)", "Clipboard", "Press Meta + V to see what you copied.", "klipper",
     "app:org.kde.klipper.desktop"),
    ("Wi-Fi and network", "Network icon in the top bar", "Click the network icon at the top right.",
     "network-wireless", "cmd:systemsettings kcm_networkmanagement"),
    ("Bluetooth", "Bluetooth settings", "Click the Bluetooth icon at the top right, or open here.",
     "preferences-system-bluetooth", "app:kcm_bluetooth.desktop"),
    ("Printers", "Settings > Printers", "Most printers are found automatically.", "printer",
     "cmd:systemsettings kcm_printer_manager"),
    ("Personalize / wallpaper", "Right-click the desktop", "Choose \"Desktop and Wallpaper\".",
     "preferences-desktop-wallpaper", "app:kcm_wallpaper.desktop"),
    ("Running a .exe program", "Wine (already installed)", "Double-click the .exe file. Games run best through Steam or Lutris.",
     "wine", ""),
    ("Recycle Bin", "Trash", "The trash can at the end of the dock.", "user-trash", "cmd:dolphin trash:/"),
]

SHORTCUTS = [
    ("Windows (Super)", "Open Start"),
    ("Super + E", "Open Files"),
    ("Ctrl + Alt + T", "Open the Terminal"),
    ("Alt + Tab", "Switch between windows"),
    ("Super + D", "Show the desktop"),
    ("Super + L", "Lock the screen"),
    ("Print Screen", "Take a screenshot"),
    ("Meta + V", "Clipboard history"),
    ("Ctrl + Esc", "System Monitor (like Task Manager)"),
    ("Super + ← / →", "Snap a window to half the screen"),
]

FAQ = [
    ("How do I install apps?",
     "Open the Konaro Store, search for the app and click Install. Everything comes from trusted sources (Debian and Flathub)."),
    ("Do I need an antivirus?",
     "Usually not. Linux viruses are very rare, the firewall is on, and apps from the Store are verified. Keep the system updated."),
    ("Will my Windows programs work?",
     "Many games work through Steam (Proton). Many programs work with Wine or Bottles. For common needs there are free alternatives in the Store."),
    ("How do I update the system?",
     "Konaro Updates warns you when there is something new. Click Install when it suits you; nothing installs without your permission."),
    ("Where are my files?",
     "In Files, under Home: Documents, Downloads, Pictures, Music and Videos, just like on Windows."),
    ("How do I bring my files from Windows?",
     "Use the Windows Migration assistant (search for \"Migrate\" in Start) to copy documents, photos and favorites."),
]


def _action(spec):
    if spec.startswith("app:"):
        return open_desktop_app(spec[4:])
    if spec.startswith("cmd:"):
        return launch(*spec[4:].split())
    return False


class HelpBridge(QObject):
    @pyqtProperty("QVariantList", constant=True)
    def places(self):
        return [{"known": _(k), "konaro": _(n), "how": _(h), "icon": i, "action": a}
                for k, n, h, i, a in WHERE]

    @pyqtProperty("QVariantList", constant=True)
    def shortcuts(self):
        return [{"keys": k, "what": _(w)} for k, w in SHORTCUTS]

    @pyqtProperty("QVariantList", constant=True)
    def faq(self):
        return [{"q": _(q), "a": _(a)} for q, a in FAQ]

    @pyqtSlot(str, result=bool)
    def open(self, action):
        return _action(action)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="konaro-help")
    parser.add_argument("--search", default="")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    from .qmlapp import run
    return run("konaro-help", _("Konaro Help"), "help/Main.qml",
               context={"helpApp": HelpBridge(), "initialSearch": args.search}, screenshot=args.screenshot,
               size=(980, 700))


if __name__ == "__main__":
    sys.exit(main())
