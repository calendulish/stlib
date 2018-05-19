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

import base64
from typing import Any, Dict, Optional, Tuple

import aiohttp
import rsa


class Http(object):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            api_server: str = 'https://api.steampowered.com',
            login_server: str = 'https://store.steampowered.com/login',
    ):
        self.session = session
        self.api_server = api_server
        self.login_server = login_server

    async def __get_data(
            self,
            interface: str,
            method: str,
            version: int,
            payload: Optional[Dict[str, str]] = None,
            data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        kwargs = {
            'method': 'POST' if data else 'GET',
            'url': f'{self.api_server}/{interface}/{method}/v{version}/',
            'params': payload,
            'json': data,
        }

        async with self.session.request(**kwargs) as response:
            return await response.json()

    async def get_user_id(self, username: str) -> int:
        data = await self.__get_data('ISteamUser', 'ResolveVanityURL', 1, {'vanityurl': username})

        if not data['response']['success'] is 1:
            raise ValueError('Failed to get user id.')

        return int(data['response']['steamid'])

    async def get_public_key(self, username: str) -> Tuple[rsa.PublicKey, int]:
        data = await self.__get_data('login', 'getrsakey', 0, {'username': username})

        if data['success']:
            public_mod = int(data['publickey_mod'], 16)
            public_exp = int(data['publickey_exp'], 16)
            timestamp = int(data['timestamp'])
        else:
            raise ValueError('Failed to get public key.')

        return rsa.PublicKey(public_mod, public_exp), timestamp


def encrypt_password(public_key: rsa.PublicKey, password: bytes) -> bytes:
    encrypted_password = rsa.encrypt(password, public_key)

    return base64.b64encode(encrypted_password)
