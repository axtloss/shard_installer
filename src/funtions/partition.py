# partition.py
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
from shard_installer.utils.diskutils import DiskUtils
from shard_installer.utils.log import setup_logging
logger=setup_logging()


class Partition:
    partitions=[]

    def __init__(self, disk: str):
        self.disk = disk
        print("Partitioning "+self.disk)
        if "nvme" in disk:
            self.partitions=[disk+"p1", disk+"p2"]
        else:
            self.partitions=[disk+"1", disk+"2"]

    def start_partition(self):
        self.partition_disk()
        if "nvme" in self.disk or "mmcblk" in self.disk:
            self.part_nvme()
        else:
            self.part_disk()

    def partition_disk(self):
        logger.debug("Using "+self.disk)
        Command.execute_command(command=["parted", "-s", self.disk, "mklabel", "gpt"], command_description="Create gpg label on "+self.disk, crash=True)
        Command.execute_command(command=["parted", "-s", self.disk, "mkpart", "fat32", "0", "512M"], command_description="Create fat32 EFI partition on "+self.disk, crash=True)
        Command.execute_command(command=["parted", "-s", self.disk, "mkpart", "btrfs", "512M", "100%"], command_description="Create Shard Linux Root partition on "+self.disk, crash=True)

    def part_nvme(self):
        logger.debug("Partitioning "+self.disk+" as nvme device")
        Command.execute_command(command=["mkfs.vfat", "-F32", self.partitions[0]], command_description="Format "+self.partitions[0]+" as fat32", crash=True)
        Command.execute_command(command=["mkfs.btrfs", "-f", self.partitions[1]], command_description="Format "+self.partitions[1]+" as btrfs", crash=True)
        self.setup_volumes()

    def part_disk(self):
        logger.debug("Partitioning "+self.disk+" as non nvme block device")
        Command.execute_command(command=["mkfs.vfat", "-F32", self.partitions[0]], command_description="Format "+self.partitions[0]+" as fat32", crash=True)
        Command.execute_command(command=["mkfs.btrfs", "-f", self.partitions[1]], command_description="Format "+self.partitions[1]+" as btrfs", crash=True)
        self.setup_volumes()


    def setup_volumes(self):
        logger.debug("Setting up shards on"+self.disk)
        DiskUtils.mount(source=self.partitions[1], destination="/mnt")
        Command.execute_command(command=["btrfs", "subvol", "create", "Root"], command_description="Create Root shard", crash=True, workdir="/mnt")
        Command.execute_command(command=["btrfs", "subvol", "create", "System"], command_description="Create System shard", crash=True, workdir="/mnt")
        Command.execute_command(command=["btrfs", "subvol", "create", "Data"], command_description="Create Data shard", crash=True, workdir="/mnt")
        Command.execute_command(command=["btrfs", "subvol", "create", "Recovery"], command_description="Create Recovery shard", crash=True, workdir="/mnt")
        Command.execute_command(command=["btrfs", "subvol", "create", "Desktop"], command_description="Create Desktop shard", crash=True, workdir="/mnt")
        Command.execute_command(command=["btrfs", "subvol", "create", "Users"], command_description="Create Users shard", crash=True, workdir="/mnt")
        DiskUtils.unmount("/mnt")
