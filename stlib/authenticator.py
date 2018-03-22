#!/usr/bin/env python
#
# Lara Maia <dev@lara.click> 2015 ~ 2018
#
# The stlib is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# The stlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#

import asyncio
import ujson
import logging
import os
import subprocess
from collections import namedtuple
from typing import List, Union
from concurrent.futures import ALL_COMPLETED

__STEAM_ALPHABET = ['2', '3', '4', '5', '6', '7', '8', '9',
                    'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                    'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                    'X', 'Y']

Checks = namedtuple('Commands', ('connected', 'root_available', 'logged', 'guard_enabled'))
CHECKS_RESULT = Checks(*[False for _ in Checks._fields])


class AndroidDebugBridge(object):
    def __init__(self, adb_path: str, app_path: str) -> None:
        self.adb_path = adb_path
        self.app_path = app_path

        if not os.path.isfile(adb_path):
            raise FileNotFoundError('Unable to find adb.')

    async def __do_check(self, parameters: List[str]):
        try:
            result = await self._run(parameters)
        except subprocess.CalledProcessError as exception:
            return False
        else:
            return True

    async def _do_checks(self):
        global CHECKS_RESULT

        tasks = [
            self.__do_check(['shell', 'true']),
            self.__do_check(['shell', 'su', '-c', 'true']),
            self.__do_check(['shell', 'su', '-c', 'cat', f'{self.app_path}/app_cache_i/login.json']),
            self.__do_check(['shell', 'su', '-c', 'cat', f'{self.app_path}/files/Steamguard-*']),
        ]

        done, _ = await asyncio.wait(tasks, return_when=ALL_COMPLETED)
        CHECKS_RESULT = Checks(*[task.result() for task in done])

        for field in CHECKS_RESULT._fields:
            atribute = getattr(CHECKS_RESULT, field)
            if atribute is False:
                logging.debug(f'{field} is {atribute}')
                if field is 'connected':
                    raise AttributeError('Phone is not connected')
                elif field is 'root_available':
                    raise AttributeError('Root is not available')
                elif field is 'logged':
                    raise AttributeError('user is not logged-in on Mobile Authenticator')
                elif field is 'guard_enabled':
                    raise AttributeError('Steam Guard is not enabled')

    async def _run(self, params: list) -> str:
        process = await asyncio.create_subprocess_exec(
                self.adb_path,
                *params,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if stderr:
            raise subprocess.CalledProcessError(process.returncode, params)

        return stdout.decode().rstrip()

    async def _get_data(self, path: str):
        await self._do_checks()

        data = await self._run([
            'shell',
            'su -c "cat {}"'.format(os.path.join(self.app_path, path))
        ])

        if 'No such file' in data:
            raise FileNotFoundError('Something wrong with the Steam Mobile App.')

        return data

    async def get_secret(self, type_: str) -> Union[str, bytes]:
        data = await self._get_data('files/Steamguard-*')
        secret = ujson.loads(data)[f'{type_}_secret']

        return secret
