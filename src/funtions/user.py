# user.py
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
from shard_installer.utils.log import setup_logging
logger = setup_logging()

class User:

    @staticmethod
    def create_user(
        password: str,
        username: str = "user",
        hasWheel: bool = True,
    ):
        password=User.hash_password(password)
        Command.execute_chroot(
            command=[
                "useradd",
                "-m",
                "-p",
                str(password),
                username
            ],
            command_description="Add user "+username,
            crash=True
        )
        if hasWheel:
            Command.execute_chroot(
                command=[
                    "usermod",
                    "-aG",
                    "wheel",
                    username
                ],
                command_description="Add "+username+" to wheel group"
            )
            FileUtils.replace_file(
                path="/mnt/etc/sudoers",
                search="# %wheel ALL=(ALL:ALL) ALL",
                replace="%wheel ALL=(ALL:ALL) ALL"
            )
            Fileutils.append_file(
                path="/mnt/etc/sudoers",
                content="\nDefaults pwfeedback\n"
            )
        # usermod --add-subuids 100000-165535 --add-subgids 100000-165535
        Command.execute_chroot(
            command=[
                "usermod",
                "--add-subuids",
                "100000-165535",
                "--add-subgids",
                "100000-165535",
                username
            ],
            command_description="Add podman subuids and subgids to "+username
        )
    
    @staticmethod
    def set_root_password(
        password: str
    ):
        password=User.hash_password(password)
        Command.execute_chroot(
            command=[
                "usermod",
                "--password",
                str(password)
            ],
            command_description="Set root password",
            crash=True
        )

    @staticmethod
    def hash_password(
        password: str
    ) -> str:
        output = Command.execute_command(
            command=[
                "openssl",
                "passwd",
                "-1",
                password
            ],
            command_description="Encrypt password",
            crash=False,
        )
        logger.debug(output)
        return output[1].decode("utf-8").strip()
