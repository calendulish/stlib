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
import time
from typing import Any, Dict, NamedTuple, Optional

import aiohttp
import rsa
from bs4 import BeautifulSoup


class SteamKey(NamedTuple):
    key: rsa.PublicKey
    timestamp: int


class Http(object):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            api_server: str = 'https://api.steampowered.com',
            login_server: str = 'https://steamcommunity.com/login',
            openid_server: str = 'https://steamcommunity.com/openid',
            headers: Optional[Dict[str, str]] = None,
    ):
        self.session = session
        self.api_server = api_server
        self.login_server = login_server
        self.openid_server = openid_server

        if not headers:
            headers = {'User-Agent': 'Unknown/0.0.0'}

        self.headers = headers

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

    async def get_user_id(self, nickname: str) -> int:
        data = await self.__get_data('ISteamUser', 'ResolveVanityURL', 1, {'vanityurl': nickname})

        if not data['response']['success'] is 1:
            raise ValueError('Failed to get user id.')

        return int(data['response']['steamid'])

    async def get_public_key(self, username: str) -> SteamKey:
        async with self.session.get(f'{self.login_server}/getrsakey/', params={'username': username}) as response:
            json_data = await response.json()

        if json_data['success']:
            public_mod = int(json_data['publickey_mod'], 16)
            public_exp = int(json_data['publickey_exp'], 16)
            timestamp = int(json_data['timestamp'])
        else:
            raise ValueError('Failed to get public key.')

        return SteamKey(rsa.PublicKey(public_mod, public_exp), timestamp)

    async def get_captcha(self, gid):
        async with self.session.get(f'{self.login_server}/rendercaptcha/', params={'gid': gid}) as response:
            return await response.read()

    async def do_login(
            self,
            username: str,
            encrypted_password: bytes,
            key_timestamp: int,
            authenticator_code: str = '',
            emailauth: str = '',
            captcha_gid: int = -1,
            captcha_text: str = '',
    ):
        data = {
            'username': username,
            "password": encrypted_password.decode(),
            "emailauth": emailauth,
            "twofactorcode": authenticator_code,
            "captchagid": captcha_gid,
            "captcha_text": captcha_text,
            "loginfriendlyname": "stlib",
            "rsatimestamp": key_timestamp,
            "remember_login": 'false',
            "donotcache": ''.join([str(int(time.time())), '000']),
        }

        async with self.session.post(f'{self.login_server}/dologin', data=data) as response:
            json_data = await response.json()

            return json_data

    async def do_openid_login(self, custom_login_page: str):
        async with self.session.get(custom_login_page, headers=self.headers) as response:
            form = BeautifulSoup(await response.text(), 'html.parser').find('form')
            data = {}

            for input_ in form.findAll('input'):
                try:
                    data[input_['name']] = input_['value']
                except KeyError:
                    pass

        async with self.session.post(f'{self.openid_server}/login', headers=self.headers, data=data) as response:
            avatar = BeautifulSoup(await response.text(), 'html.parser').find('a', class_='nav_avatar')

            if avatar:
                json_data = {'success': True, 'steamid': avatar['href'].split('/')[2]}
            else:
                json_data = {'success': False}

            json_data.update(data)

            return json_data


def encrypt_password(public_key: rsa.PublicKey, password: bytes) -> bytes:
    encrypted_password = rsa.encrypt(password, public_key)

    return base64.b64encode(encrypted_password)
