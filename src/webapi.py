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
import hashlib
import hmac
import time
from typing import Any, Dict, List, NamedTuple, Optional

import aiohttp
import rsa
from bs4 import BeautifulSoup
from stlib import client


class SteamKey(NamedTuple):
    key: rsa.PublicKey
    timestamp: int


class Confirmation(NamedTuple):
    mode: str
    id: str
    key: str
    give: str
    to: str
    receive: str
    created: str


class Http(object):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            api_server: str = 'https://api.steampowered.com',
            login_server: str = 'https://steamcommunity.com/login',
            openid_server: str = 'https://steamcommunity.com/openid',
            mobileconf_server: str = 'https://steamcommunity.com/mobileconf',
            headers: Optional[Dict[str, str]] = None,
    ):
        self.session = session
        self.api_server = api_server
        self.login_server = login_server
        self.openid_server = openid_server
        self.mobileconf_server = mobileconf_server

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

    async def get_steam_key(self, username: str) -> SteamKey:
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

    async def get_confirmations(self, identity_secret: str, steamid: int, deviceid: str) -> List[Confirmation]:
        with client.SteamGameServer() as server:
            server_time = server.get_server_time()

        params = {
            'p': deviceid,
            'a': steamid,
            'k': generate_time_hash(server_time, 'conf', identity_secret),
            't': server_time,
            'm': 'android',
            'tag': 'conf',
        }

        async with self.session.get(f'{self.mobileconf_server}/conf', params=params) as response:
            html = BeautifulSoup(await response.text(), 'html.parser')

        with open('test.html', 'w', encoding='utf-8') as file:
            file.write(str(html))

        confirmations = []
        for confirmation in html.find_all('div', class_='mobileconf_list_entry'):
            description = confirmation.find('div', class_='mobileconf_list_entry_description').find_all()

            if confirmation['data-type'] == "1" or confirmation['data-type'] == "2":
                give_raw = description[0].get_text()[6:]
                give = give_raw[:give_raw.index(" to ")]
                to = give_raw[give_raw.index(" to ") + 4:]

                if description[1].get_text() == 'You will receive nothing':
                    receive = "nothing"
                else:
                    receive = description[1].get_text()[11:]

                created = description[2].get_text()
            elif confirmation['data-type'] == "3":
                give = description[0].get_text()[7:]
                to = 'Market'
                receive = description[1].get_text()
                created = description[2].get_text()
            else:
                raise NotImplementedError(f"Data Type: {confirmation['data-type']}")

            confirmations.append(
                Confirmation(
                    confirmation['data-accept'],
                    confirmation['data-confid'],
                    confirmation['data-key'],
                    give, to, receive, created,
                )
            )

        return confirmations

    async def finalize_confirmation(
            self,
            identity_secret: str,
            steamid: int,
            deviceid: str,
            trade_id: int,
            trade_key: int,
            action: str
    ):
        with client.SteamGameServer() as server:
            server_time = server.get_server_time()

        params = {
            'p': deviceid,
            'a': steamid,
            'k': generate_time_hash(server_time, 'conf', identity_secret),
            't': server_time,
            'm': 'android',
            'tag': 'conf',
            'cid': trade_id,
            'ck': trade_key,
            'op': action
        }

        async with self.session.get(f'{self.mobileconf_server}/ajaxop', params=params) as response:
            return await response.json()


def encrypt_password(steam_key: SteamKey, password: bytes) -> bytes:
    encrypted_password = rsa.encrypt(password, steam_key.key)

    return base64.b64encode(encrypted_password)


def generate_time_hash(server_time, tag, secret):
    key = base64.b64decode(secret)
    msg = server_time.to_bytes(8, 'big') + tag.encode()
    auth = hmac.new(key, msg, hashlib.sha1)
    code = base64.b64encode(auth.digest())

    return code.decode()
