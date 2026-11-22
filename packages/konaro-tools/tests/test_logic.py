"""Testes da lógica das ferramentas Konaro (sem interface gráfica).

Executar: PYTHONPATH=packages/konaro-tools/src python3 -m unittest discover packages/konaro-tools/tests
Requer python3-gi e gir1.2-packagekitglib-1.0 (importados pelos módulos).
"""

import json
import os
import unittest

from konaro import drivers, flatpak, i18n, packagekit, updater

HERE = os.path.dirname(__file__)
CATALOG = os.path.join(HERE, "..", "data", "store", "catalog.json")

LSPCI = """\
00:02.0 VGA compatible controller [0300]: Intel Corporation CometLake-H GT2 [UHD Graphics] [8086:9bc4] (rev 05)
\tSubsystem: Dell Device [1028:097d]
\tKernel driver in use: i915
\tKernel modules: i915
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation TU117M [GeForce GTX 1650 Mobile / Max-Q] [10de:1f91] (rev a1)
\tKernel driver in use: nouveau
02:00.0 Network controller [0280]: Intel Corporation Wi-Fi 6 AX201 [8086:02f0]
\tKernel driver in use: iwlwifi
00:1f.3 Audio device [0403]: Intel Corporation Comet Lake PCH cAVS [8086:06c8]
\tKernel driver in use: sof-audio-pci-intel-cnl
03:00.0 Non-Volatile memory controller [0108]: Samsung Electronics NVMe SSD [144d:a808]
\tKernel driver in use: nvme
"""

NVIDIA_DETECT = """\
Detected NVIDIA GPUs:
01:00.0 3D controller [0302]: NVIDIA Corporation TU117M [10de:1f91] (rev a1)

Checking card:  NVIDIA Corporation TU117M (rev a1)
Your card is supported by all driver versions.
Your card is also supported by the Tesla 535 drivers series.
It is recommended to install the
    nvidia-driver
package.
"""

STEAM_METADATA = """\
[Application]
name=com.valvesoftware.Steam

[Context]
shared=ipc;network;
sockets=x11;wayland;pulseaudio;
devices=all;
filesystems=xdg-music:ro;xdg-pictures:ro;xdg-run/app/com.discordapp.Discord:create;
"""


class DriversTest(unittest.TestCase):
    def test_parse_lspci(self):
        devices = drivers.parse_lspci(LSPCI)
        self.assertEqual(len(devices), 5)
        self.assertEqual(devices[1]["vendor"], "10de")
        self.assertEqual(devices[1]["driver"], "nouveau")
        self.assertEqual([drivers.kind(d) for d in devices], ["Video", "Video", "Wi-Fi", "Audio", "Other"])

    def test_parse_nvidia_detect(self):
        self.assertEqual(drivers.parse_nvidia_detect(NVIDIA_DETECT), ["nvidia-driver"])
        self.assertEqual(drivers.parse_nvidia_detect("No NVIDIA GPU detected."), [])


class FlatpakTest(unittest.TestCase):
    def test_permissions(self):
        i18n.set_language("en")
        perms = flatpak.describe_permissions(STEAM_METADATA)
        self.assertIn("Network access", perms)
        self.assertIn("Access to devices (cameras, controllers…)", perms)
        self.assertIn("Sound", perms)
        self.assertIn("Access to some of your folders", perms)

    def test_no_context(self):
        i18n.set_language("en")
        self.assertEqual(flatpak.describe_permissions("[Application]\nname=x\n"), ["No special permissions"])

    def test_portuguese(self):
        i18n.set_language("pt")
        self.assertIn("Acesso à rede", flatpak.describe_permissions(STEAM_METADATA))
        i18n.set_language("en")


class UpdaterTest(unittest.TestCase):
    def test_classify(self):
        pk = [
            {"id": "a", "name": "openssl", "security": True, "konaro": False},
            {"id": "b", "name": "konaro-store", "security": False, "konaro": True},
            {"id": "c", "name": "vim", "security": False, "konaro": False},
        ]
        groups = updater.classify(pk, [{"id": "org.x.App", "name": "App"}])
        self.assertEqual([u["id"] for u in groups["security"]], ["a"])
        self.assertEqual([u["id"] for u in groups["konaro"]], ["b"])
        self.assertEqual([u["id"] for u in groups["system"]], ["c"])
        self.assertEqual(len(groups["flatpak"]), 1)

    def test_restart_hint(self):
        self.assertTrue(packagekit.may_need_restart(["linux-image-6.12.0-amd64"]))
        self.assertFalse(packagekit.may_need_restart(["vim", "curl"]))


class ErrorsTest(unittest.TestCase):
    def test_friendly(self):
        i18n.set_language("en")
        self.assertIn("password", packagekit.friendly_error("Not authorized"))
        self.assertIn("internet", packagekit.friendly_error("Failed to fetch http://x Could not resolve"))
        self.assertIn("internet", packagekit.friendly_error("Cannot download packages whilst offline"))


class CatalogTest(unittest.TestCase):
    def test_catalog(self):
        with open(CATALOG, encoding="utf-8") as fh:
            apps = json.load(fh)["apps"]
        ids = [a["id"] for a in apps]
        self.assertEqual(len(ids), len(set(ids)), "ids duplicados")
        for app in apps:
            self.assertIn(app["backend"], ("apt", "flatpak"))
            self.assertTrue(app["summary"]["en"] and app["summary"]["pt"], app["id"])
            if app["backend"] == "apt":
                self.assertTrue(app["packages"], app["id"])
            else:
                self.assertTrue(app["app"].count(".") >= 2, app["id"])


class I18nTest(unittest.TestCase):
    def test_all_used_strings_translated(self):
        import ast
        import glob
        missing = set()
        for path in glob.glob(os.path.join(HERE, "..", "src", "konaro", "*.py")):
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_"
                        and node.args and isinstance(node.args[0], ast.Constant)):
                    if node.args[0].value not in i18n.PT:
                        missing.add(node.args[0].value)
        import re
        for path in glob.glob(os.path.join(HERE, "..", "src", "konaro", "qml", "**", "*.qml"), recursive=True):
            with open(path, encoding="utf-8") as fh:
                source = fh.read()
                found = re.findall(r'(?:i18n\.tr|ctl\.t|root\.t|\bt)\("((?:[^"\\]|\\.)+)"\)', source)
                for one, many in re.findall(r'i18n\.plural\([^,]+,\s*"([^"]+)",\s*"([^"]+)"\)', source):
                    found += [one, many]
                for text in found:
                    if text not in i18n.PT:
                        missing.add(text)
        self.assertEqual(sorted(missing), [])


if __name__ == "__main__":
    unittest.main()
