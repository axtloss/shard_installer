# shards.py
#
# Copyright 2023 axtlos <axtlos@getcryst.al>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0

from shard_installer.utils.command import Command
from shard_installer.utils.fileutils import FileUtils
from shard_installer.utils.diskutils import DiskUtils
import logging
import logging.config
import yaml

with open("logging.yaml", "r") as f:
    config = yaml.safe_load(f.read())
    f.close()

logging.config.dictConfig(config)
logger=logging.getLogger("shard_logging")
class Shards:

    @staticmethod
    def setupRoot(
        mountpoint: str,
        disks: list,
    ):
        Command.execute(command=["pacstrap", "-K", mountpoint, "base"], command_description="Setup base package on Root", crash=True)
        FileUtils.create_file("/mnt/init")
        FileUtils.write_file("/mnt/init", "#!/bin/bash")
        init = '''
        echo -e "\\x1b[35;1m --STARTING PROJECT SHARD STAGE 1-- \\x1b[39m"
        echo "Mounting Shards"
        mount {partition2} /Shards/Data -t btrfs -o rw{ssd},relatime,space_cache=v2,compress,subvol=/Data
        mount {partition2} /Shards/Desktop -t btrfs -o ro{ssd},relatime,space_cache=v2,compress,subvol=/Desktop
        mount {partition2} /Shards/System -t btrfs -o ro{ssd},relatime,space_cache=v2,compress,subvol=/System
        mount {partition2} /Shards/Users -t btrfs -o rw{ssd},relatime,space_cache=v2,compress,subvol=/Users
        echo "Creating overlays"
        mount -t overlay overlay -o lowerdir=/Shards/System/opt:/Shards/Desktop/opt,upperdir=/Shards/Data/opt,workdir=/Shards/Data/tmp/opt /opt
        mount -t overlay overlay -o lowerdir=/Shards/System/usr:/Shards/Desktop/usr,upperdir=/Shards/Data/usr,workdir=/Shards/Data/tmp/usr /usr
        mount -t overlay overlay -o lowerdir=/Shards/System/var:/Shards/Desktop/var,upperdir=/Shards/Data/var,workdir=/Shards/Data/tmp/var /var
        echo "Mounting bind mounts"
        mount --bind /Shards/System/boot /boot
        mount --bind /Shards/Users /home
        mount --bind /Shards/Data/etc /etc
        echo -e "\\x1b[35;1m --STARTING PROJECT SHARD STAGE 2-- \\x1b[39m"
        exec /Shards/System/sbin/init
        '''.format(partition2=disks[1], ssd=",ssd" if DiskUtils.is_ssd(disks[0]) else "")

    @staticmethod
    def setupSystem(
        mountpoint: str,
    ):
        Command.execute(
            command=[
                "pacstrap",
                "-K",
                mountpoint,
                "base",
                "linux",
                "linux-firmware",
                "networkmanager",
                "btrfs-progs",
                "grub",
                "efibootmgr",
                "systemd-sysvcompat",
                "man-db",
                "man-pages",
                "texinfo",
                "nano",
                "sudo",
                "curl",
                "archlinux-keyring",
                "which",
                "base-devel",
                "bash-completion",
                "zsh-completions",
                "bluez",
                "podman",
            ],
            command_description="Setup install packages on System",
            crash=True,
        )

        Command.execute(
            command=[
                "systemctl",
                "enable",
                "NetworkManager",
            ],
            command_description="Enable NetworkManager",
            crash=False,
        )

        Command.execute(
            command=[
                "systemctl",
                "enable",
                "bluetooth",
            ],
            command_description="Enable bluetooth",
            crash=False,
        )

    @staticmethod
    def setupDesktop(
        mountpoint: str,
    ):
        Command.execute(
            command=[
                "pacstrap",
                "-K",
                mountpoint,
                "xorg",
                "gnome",
                "sushi",
                "pipewire",
                "pipewire-pulse",
                "pipewire-alsa",
                "pipewire-jack",
                "wireplumber",
                "noto-fonts",
                "noto-fonts-cjk",
                "noto-fonts-emoji",
                "noto-fonts-extra",
                "ttf-nerd-fonts-symbols-common",
                "power-profiles-daemon",
                "cups",
                "cups-pdf",

            ],
        )
        Command.execute(
            command=[
                "systemctl",
                "enable",
                "gdm",
            ]
        )

    @staticmethod
    def setupData(
        mountpoint: str,
    ):
        FileUtils.create_directory(mountpoint + "/etc")
        FileUtils.create_directory(mountpoint + "/opt")
        FileUtils.create_directory(mountpoint + "/usr")
        FileUtils.create_directory(mountpoint + "/var")
        # System shard packages:
        # base linux linux-firmware intel-ucode networkmanager grub
        # base shard packages:
        # base
