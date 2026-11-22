#!/usr/bin/env python3
"""Konaro OS — "Voltar no tempo": configura o Timeshift no sistema instalado.

Se a raiz foi instalada em Btrfs (padrão do Konaro, com os subvolumes @ e @home),
grava /etc/timeshift/timeshift.json apontando para esse disco, com pontos de
restauração diários (5 guardados) e sem incluir a pasta pessoal. O primeiro ponto
é criado no primeiro boot (konaro-snapshot.service) e outro antes de cada
atualização (Atualizações do Konaro). Em ext4/XFS nada é feito.
"""

import json
import os

import libcalamares


def pretty_name():
    return "Configurando o Voltar no tempo / Setting up system snapshots"


def run():
    root = libcalamares.globalstorage.value("rootMountPoint")
    partitions = libcalamares.globalstorage.value("partitions") or []
    rootpart = next((p for p in partitions if p.get("mountPoint") == "/"), None)
    if not rootpart or rootpart.get("fs") != "btrfs":
        libcalamares.utils.debug("konarosnapshots: raiz não é btrfs, nada a fazer")
        return None
    uuid = rootpart.get("uuid", "")
    if rootpart.get("luksMapperName"):
        # disco criptografado: o Timeshift usa o UUID do volume aberto
        uuid = rootpart.get("luksUuid", uuid) or uuid
    config = {
        "backup_device_uuid": uuid,
        "parent_device_uuid": "",
        "do_first_run": "false",
        "btrfs_mode": "true",
        "include_btrfs_home_for_backup": "false",
        "include_btrfs_home_for_restore": "false",
        "stop_cron_emails": "true",
        "schedule_monthly": "false",
        "schedule_weekly": "false",
        "schedule_daily": "true",
        "schedule_hourly": "false",
        "schedule_boot": "false",
        "count_monthly": "2",
        "count_weekly": "3",
        "count_daily": "5",
        "count_hourly": "6",
        "count_boot": "5",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "exclude": [],
        "exclude-apps": [],
    }
    path = os.path.join(root, "etc/timeshift/timeshift.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
    libcalamares.utils.target_env_call(["systemctl", "enable", "konaro-snapshot-first-boot.service"])
    libcalamares.utils.target_env_call(["systemctl", "enable", "konaro-snapshot.timer"])
    libcalamares.utils.debug("konarosnapshots: Timeshift configurado em %s" % uuid)
    return None
