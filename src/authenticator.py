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
import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional, Union
from xml.etree import ElementTree

log = logging.getLogger(__name__)

__STEAM_ALPHABET = ['2', '3', '4', '5', '6', '7', '8', '9',
                    'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                    'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                    'X', 'Y']


class DeviceError(Exception): pass


class RootError(Exception): pass


class LoginError(Exception): pass


class SteamGuardError(Exception): pass


class MobileAppError(SteamGuardError): pass


class AndroidDebugBridge:
    def __init__(
            self,
            adb_path: str,
            app_path: str = '/data/data/com.valvesoftware.android.steam.community/'
    ) -> None:

        self.adb_path = adb_path
        self.app_path = app_path

        if not os.path.isfile(adb_path):
            raise FileNotFoundError(f'Unable to find adb. Please, check if path is correct:\n{self.adb_path}')

    async def _do_checks(self) -> None:
        pre_tasks = [
            ['shell', 'true'],
            ['root'],
        ]

        log.info('Your phone can be reconnected to switch adb to root mode')
        pre_tasks_result = await asyncio.gather(*[self._run(pre_task) for pre_task in pre_tasks],
                                                return_exceptions=True)

        if isinstance(pre_tasks_result[0], Exception):
            raise DeviceError('Phone is not connected')

        if isinstance(pre_tasks_result[1], Exception):
            raise RootError('Unable switch to root mode')

        await self._run(['wait-for-device'])

        tasks = [
            ['shell', 'su', '-c', 'true'],
            ['shell', 'su', '-c', f'"cat {self.app_path}/app_cache_i/login.json"'],
            ['shell', 'su', '-c', f'"cat {self.app_path}/files/Steamguard-*"'],
        ]

        tasks_result = await asyncio.gather(*[self._run(task) for task in tasks], return_exceptions=True)
        log.debug('tasks_result: %s', tasks_result)

        for index, result in enumerate(tasks_result):
            if isinstance(result, Exception):
                if index == 0:
                    raise RootError('Root is not available')
                elif index == 1:
                    raise LoginError('User is not logged-in on Mobile Authenticator')
                else:
                    raise SteamGuardError('Steam Guard is not enabled')

    async def _run(self, params: List[Any]) -> str:
        process = await asyncio.create_subprocess_exec(
            self.adb_path,
            *params,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, params)

        return stdout.decode().rstrip()

    async def _get_data(self, path: str) -> str:
        await self._do_checks()

        logging.debug('Getting data from %s', path)
        data = await self._run(['shell', 'su', '-c', f'"cat {os.path.join(self.app_path, path)}"'])

        if not data or 'No such file' in data:
            raise MobileAppError('Something wrong with the Steam Mobile App.')

        return data

    async def get_json(self, *names: str) -> Dict[str, str]:
        data = await self._get_data('files/Steamguard-*')

        json_data = {}

        for name in names:
            json_data[name] = json.loads(data)[name]

        return json_data

    async def get_device_id(self) -> str:
        data = await self._get_data('shared_prefs/steam.uuid.xml')
        xml_data = ElementTree.fromstring(data)

        assert isinstance(xml_data[0].text, str), "No device id on xml_data"
        return xml_data[0].text[8:]


def get_code(server_time: int, shared_secret: Union[str, bytes]) -> str:
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

    return ''.join(auth_code)


def generate_device_id(identity_secret: Optional[str] = None, token: Optional[str] = None) -> str:
    if identity_secret:
        data = identity_secret.encode()
    elif token:
        data = token.encode()
    else:
        raise AttributeError("You must provide at least one argument")

    digest = hashlib.sha1(data).hexdigest()
    device_id = ['android:']

    for start, end in ([0, 8], [8, 12], [12, 16], [16, 20], [20, 32]):
        device_id.append(digest[start:end])
        device_id.append('-')

    device_id.pop(-1)
    return ''.join(device_id)
