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
import base64
import hashlib
import hmac
import logging
import os
import subprocess
import ujson
from collections import namedtuple
from concurrent.futures import ALL_COMPLETED
from typing import Any, List, Tuple, Union

from stlib import client

__STEAM_ALPHABET = ['2', '3', '4', '5', '6', '7', '8', '9',
                    'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                    'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                    'X', 'Y']

Checks = namedtuple('Commands', ('connected', 'root_available', 'logged', 'guard_enabled'))
CHECKS_RESULT = Checks(*[False for _ in Checks._fields])


class AndroidDebugBridge(object):
    def __init__(
            self,
            adb_path: str,
            app_path: str = '/data/data/com.valvesoftware.android.steam.community/'
    ) -> None:

        self.adb_path = adb_path
        self.app_path = app_path

        if not os.path.isfile(adb_path):
            raise FileNotFoundError(f'Unable to find adb. Please, check if path is correct:\n{self.adb_path}')

    async def __do_check(self, parameters: List[str]) -> bool:
        try:
            await self._run(parameters)
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    async def _do_checks(self) -> None:
        global CHECKS_RESULT

        await self._run(['root'])

        tasks = [
            self.__do_check(['shell', 'true']),
            self.__do_check(['shell', 'su', '-c', 'true']),
            self.__do_check(['shell', 'su', '-c', 'cat', f'{self.app_path}/app_cache_i/login.json']),
            self.__do_check(['shell', 'su', '-c', 'cat', f'{self.app_path}/files/Steamguard-*']),
        ]

        done, _ = await asyncio.wait(tasks, return_when=ALL_COMPLETED)
        CHECKS_RESULT = Checks(*[task.result() for task in done])

        for field in CHECKS_RESULT._fields:
            attribute = getattr(CHECKS_RESULT, field)
            if attribute is False:
                logging.debug(f'{field} is {attribute}')
                if field == 'connected':
                    raise AttributeError('Phone is not connected')
                elif field == 'root_available':
                    raise AttributeError('Root is not available')
                elif field == 'logged':
                    raise AttributeError('user is not logged-in on Mobile Authenticator')
                elif field == 'guard_enabled':
                    raise AttributeError('Steam Guard is not enabled')

    async def _run(self, params: List[Any]) -> str:
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

    async def _get_data(self, path: str) -> str:
        await self._do_checks()

        data = await self._run([
            'shell',
            'su -c "cat {}"'.format(os.path.join(self.app_path, path))
        ])

        if not data or 'No such file' in data:
            raise FileNotFoundError('Something wrong with the Steam Mobile App.')

        return data

    async def get_secret(self, type_: str) -> bytes:
        data = await self._get_data('files/Steamguard-*')
        secret = ujson.loads(data)[f'{type_}_secret']

        return secret.encode()


def get_code(shared_secret: Union[str, bytes]) -> Tuple[List[str], int]:
    with client.SteamGameServer() as server:
        server_time = server.get_server_time()

    msg = int(server_time / 30).to_bytes(8, 'big')
    key = base64.b64decode(shared_secret)
    auth = hmac.new(key, msg, hashlib.sha1)
    digest = auth.digest()
    start = digest[19] & 0xF
    code = digest[start:start + 4]
    auth_code_raw = int.from_bytes(code, byteorder='big') & 0x7FFFFFFF

    auth_code = []
    for _ in range(5):
        auth_code.append(__STEAM_ALPHABET[int(auth_code_raw % len(__STEAM_ALPHABET))])
        auth_code_raw //= len(__STEAM_ALPHABET)

    return auth_code, server_time
