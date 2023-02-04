# command.py
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

import subprocess
import logging

class Command:
    @staticmethod
    def execute_command(
        command: list,
        command_description: str = "",
        crash: bool = False,
        workdir: str = "",
    ) -> [str, str, str]:
        out = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            cwd=workdir if workdir.strip() is not "" else None
        )
        if out.returncode != 0 and command_description.strip() != "":
            logging.error(command_description+" failed with returncode "+out.returncode)
            if crash:
                return out.returncode
        elif out.returncode != 0:
            logging.error(command+" failed with returncode "+out.returncode)
            if crash:
                return out.returncode

        return [out.returncode, out.stdout, out.stderr]