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
import contextlib
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, List, NamedTuple, Optional

import aiohttp
import rsa
from bs4 import BeautifulSoup


class SteamKey(NamedTuple):
    key: rsa.PublicKey
    timestamp: int


class Confirmation(NamedTuple):
    mode: str
    id: int
    key: int
    give: List[str]
    to: str
    receive: List[str]


class TradeInfo(NamedTuple):
    id: str
    title: str
    html: str


class LoginError(Exception): pass


class TradeClosedError(Exception):
    def __init__(self, trade_info: TradeInfo, message: str) -> None:
        super().__init__(message)

        self.id = trade_info.id
        self.title = trade_info.title


class TradeNotReadyError(Exception):
    def __init__(self, trade_info: TradeInfo, time_left: int, message: str) -> None:
        super().__init__(message)

        self.time_left = time_left
        self.id = trade_info.id
        self.title = trade_info.title


class NoTradesError(Exception): pass


class SteamWebAPI(object):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            api_url: str = 'https://api.steampowered.com',
            login_url: str = 'https://steamcommunity.com/login',
            openid_url: str = 'https://steamcommunity.com/openid',
            mobileconf_url: str = 'https://steamcommunity.com/mobileconf',
            economy_url: str = 'https://steamcommunity.com/economy',
            headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.session = session
        self.api_url = api_url
        self.login_url = login_url
        self.openid_url = openid_url
        self.mobileconf_url = mobileconf_url
        self.economy_url = economy_url

        if not headers:
            headers = {'User-Agent': 'Unknown/0.0.0'}

        self.headers = headers

    async def _new_query(self, deviceid: str, steamid: int, identity_secret: str, tag: str) -> Dict[str, Any]:
        server_time = await self.get_server_time()

        params = {
            'p': deviceid,
            'a': steamid,
            'k': new_time_hash(server_time, tag, identity_secret),
            't': server_time,
            'm': 'android',
            'tag': tag,
        }

        return params

    async def _get_data(
            self,
            interface: str,
            method: str,
            version: int,
            payload: Optional[Dict[str, str]] = None,
            data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        kwargs = {
            'method': 'POST' if data else 'GET',
            'url': f'{self.api_url}/{interface}/{method}/v{version}/',
            'params': payload,
            'json': data,
        }

        async with self.session.request(**kwargs) as response:
            json_data = await response.json()
            assert isinstance(json_data, dict), "Json data from SteamWebAPI is not a dict"
            return json_data

    async def get_server_time(self) -> int:
        data = await self._get_data('ISteamWebAPIUtil', 'GetServerInfo', 1)
        return int(data['servertime'])

    async def get_user_id(self, nickname: str) -> int:
        data = await self._get_data('ISteamUser', 'ResolveVanityURL', 1, {'vanityurl': nickname})

        if not data['response']['success'] is 1:
            raise ValueError('Failed to get user id.')

        return int(data['response']['steamid'])

    async def get_steam_key(self, username: str) -> SteamKey:
        async with self.session.get(f'{self.login_url}/getrsakey/', params={'username': username}) as response:
            json_data = await response.json()

        if json_data['success']:
            public_mod = int(json_data['publickey_mod'], 16)
            public_exp = int(json_data['publickey_exp'], 16)
            timestamp = int(json_data['timestamp'])
        else:
            raise ValueError('Failed to get public key.')

        return SteamKey(rsa.PublicKey(public_mod, public_exp), timestamp)

    async def get_captcha(self, gid: int) -> bytes:
        async with self.session.get(f'{self.login_url}/rendercaptcha/', params={'gid': gid}) as response:
            data = await response.read()
            assert isinstance(data, bytes), "rendercaptcha response is not bytes"
            return data

    async def do_login(
            self,
            username: str,
            encrypted_password: bytes,
            key_timestamp: int,
            authenticator_code: str = '',
            emailauth: str = '',
            captcha_gid: int = -1,
            captcha_text: str = '',
    ) -> Dict[str, Any]:
        data = {
            'username': username,
            "password": encrypted_password.decode(),
            "emailauth": emailauth,
            "twofactorcode": authenticator_code,
            "captchagid": captcha_gid,
            "captcha_text": captcha_text,
            "loginfriendlyname": "stlib",
            "rsatimestamp": key_timestamp,
            "remember_login": 'true',
            "donotcache": ''.join([str(int(time.time())), '000']),
        }

        async with self.session.post(f'{self.login_url}/dologin', data=data) as response:
            json_data = await response.json()
            assert isinstance(json_data, dict), "Json data from dologin is not a dict"

            return json_data

    async def do_openid_login(self, custom_login_page: str) -> Dict[str, Any]:
        async with self.session.get(custom_login_page, headers=self.headers) as response:
            form = BeautifulSoup(await response.text(), 'html.parser').find('form')
            data = {}

            for input_ in form.findAll('input'):
                with contextlib.suppress(KeyError):
                    data[input_['name']] = input_['value']

        async with self.session.post(f'{self.openid_url}/login', headers=self.headers, data=data) as response:
            avatar = BeautifulSoup(await response.text(), 'html.parser').find('a', class_='nav_avatar')

            if avatar:
                json_data = {'success': True, 'steamid': avatar['href'].split('/')[2]}
            else:
                raise LoginError('Unable to log-in')

            json_data.update(data)

            return json_data

    async def __get_names_from_item_list(
            self,
            item_list: BeautifulSoup,
    ) -> List[str]:
        result = []
        for tradeoffer_item in item_list.find_all('div', class_="trade_item"):
            appid, classid = tradeoffer_item['data-economy-item'].split('/')[1:3]

            async with self.session.get(
                    f"{self.economy_url}/itemclasshover/{appid}/{classid}",
                    params={'content_only': 1},
            ) as response:
                html = BeautifulSoup(await response.text(), "html.parser")
                javascript = html.find('script')

            json_data = js_to_json(javascript)

            if json_data:
                if json_data['market_name']:
                    result.append(f"{json_data['market_name']} ({json_data['type']})")
                else:
                    result.append(json_data['name'])
            else:
                result.append('')

        return result

    async def get_confirmations(self, identity_secret: str, steamid: int, deviceid: str) -> List[Confirmation]:
        params = await self._new_query(deviceid, steamid, identity_secret, 'conf')

        async with self.session.get(f'{self.mobileconf_url}/conf', params=params, allow_redirects=False) as response:
            html = BeautifulSoup(await response.text(), 'html.parser')

            if response.status == 302:
                raise LoginError('User is not logged in')

        confirmations = []
        for confirmation in html.find_all('div', class_='mobileconf_list_entry'):
            details_params = await self._new_query(
                deviceid, steamid, identity_secret, f"details{confirmation['data-confid']}"
            )

            async with self.session.get(
                    f"{self.mobileconf_url}/details/{confirmation['data-confid']}",
                    params=details_params,
            ) as response:
                json_data = await response.json()

                if not json_data['success']:
                    raise AttributeError(f"Unable to get details for confirmation {confirmation['data-confid']}")

                html = BeautifulSoup(json_data["html"], 'html.parser')

            if confirmation['data-type'] == "1" or confirmation['data-type'] == "2":
                to = html.find('span', class_="trade_partner_headline_sub").get_text()

                item_list = html.find_all('div', class_="tradeoffer_item_list")
                give = await self.__get_names_from_item_list(item_list[0])
                receive = await self.__get_names_from_item_list(item_list[1])
            elif confirmation['data-type'] == "3":
                to = "Market"

                listing_prices = html.find('div', class_="mobileconf_listing_prices")
                prices = [item.next_sibling.strip() for item in listing_prices.find_all("br")]
                receive = ["{} ({})".format(*prices)]

                javascript = html.find_all("script")[2]
                json_data = js_to_json(javascript)
                give = [f"{json_data['market_name']} - {json_data['type']}"]
            else:
                raise NotImplementedError(f"Data Type: {confirmation['data-type']}")

            confirmations.append(
                Confirmation(
                    confirmation['data-accept'],
                    int(confirmation['data-confid']),
                    int(confirmation['data-key']),
                    give, to, receive,
                )
            )

        return confirmations

    async def finalize_confirmation(
            self,
            server_time: int,
            identity_secret: str,
            steamid: int,
            deviceid: str,
            trade_id: int,
            trade_key: int,
            action: str
    ) -> Dict[str, Any]:
        extra_params = {'cid': trade_id, 'ck': trade_key, 'op': action}
        params = await self._new_query(deviceid, steamid, identity_secret, 'conf')

        async with self.session.get(f'{self.mobileconf_url}/ajaxop', params={**params, **extra_params}) as response:
            json_data = await response.json()
            assert isinstance(json_data, dict), "Json data from ajaxop is not a dict"
            return json_data


class SteamTrades(SteamWebAPI):
    def __init__(
            self,
            session: aiohttp.ClientSession,
            server: str = 'https://www.steamtrades.com',
            bump_script: str = 'ajax.php',
            headers: Optional[Dict[str, str]] = None,
            *args: Any,
            **kwargs: Any,
    ) -> None:
        super().__init__(session, *args, **kwargs)

        self.session = session
        self.server = server
        self.bump_script = bump_script

        if not headers:
            headers = {'User-Agent': 'Unknown/0.0.0'}

        self.headers = headers

    async def get_trade_info(self, trade_id: str) -> TradeInfo:
        async with self.session.get(f'{self.server}/trade/{trade_id}/', headers=self.headers) as response:
            id = response.url.path.split('/')[2]
            title = os.path.basename(response.url.path).replace('-', ' ')
            html = await response.text()
            return TradeInfo(id, title, html)

    async def bump(self, trade_info: TradeInfo) -> bool:
        soup = BeautifulSoup(trade_info.html, 'html.parser')

        if not soup.find('a', class_='nav_avatar'):
            raise LoginError("User is not logged in")

        if soup.find('div', class_='js_trade_open'):
            raise TradeClosedError(trade_info, f"Trade {trade_info.id} is closed")

        form = soup.find('form')
        data = {}

        try:
            for input_ in form.findAll('input'):
                data[input_['name']] = input_['value']
        except AttributeError:
            raise NoTradesError("No trades available to bump")

        payload = {
            'code': data['code'],
            'xsrf_token': data['xsrf_token'],
            'do': 'trade_bump',
        }

        async with self.session.post(
                f'{self.server}/{self.bump_script}',
                data=payload,
                headers=self.headers,
        ) as response:
            html = await response.text()
            if 'Please wait another' in html:
                error = json.loads(html)['popup_heading_h2'][0]
                minutes_left = int(error.split(' ')[3])
                raise TradeNotReadyError(trade_info, minutes_left, f"Trade {trade_info.id} is not ready")
            else:
                async with self.session.post(f'{self.server}/trades', headers=self.headers) as response:
                    text = await response.text()

                if trade_info.id in text:
                    return True
                else:
                    return False


def encrypt_password(steam_key: SteamKey, password: str) -> bytes:
    encrypted_password = rsa.encrypt(password.encode(), steam_key.key)

    return base64.b64encode(encrypted_password)


def new_time_hash(server_time: int, tag: str, secret: str) -> str:
    key = base64.b64decode(secret)
    msg = server_time.to_bytes(8, 'big') + tag.encode()
    auth = hmac.new(key, msg, hashlib.sha1)
    code = base64.b64encode(auth.digest())

    return code.decode()


def js_to_json(javascript: BeautifulSoup) -> Dict[str, Any]:
    json_data = {}

    for line in str(javascript).split('\t+'):
        if "BuildHover" in line:
            for item in line.split(','):
                with contextlib.suppress(ValueError):
                    key_raw, value_raw = item.split(':"')
                    key = key_raw.replace('"', '')
                    value = bytes(value_raw.replace('"', ''), 'utf-8').decode('unicode_escape')
                    json_data[key] = value
        break

    return json_data
