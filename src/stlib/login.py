#!/usr/bin/env python
#
# Lara Maia <dev@lara.monster> 2015 ~ 2022
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
import http
import json
import logging
import time
from typing import Any, Dict, Optional, NamedTuple

import aiohttp
import rsa

from . import universe

log = logging.getLogger(__name__)
session_list = []


class LoginData(NamedTuple):
    auth: Dict[str, Any]
    oauth: Dict[str, Any]


class LoginError(ValueError):
    """Raised when login can`t be completed"""
    pass


class LoginBlockedError(LoginError):
    """Raised when user is temporarily blocked from login session"""
    pass


class CaptchaError(LoginError):
    """Raised when captcha is requested"""

    def __init__(self, captcha_gid: int, captcha: bytes, message: str) -> None:
        super().__init__(message)

        self.captcha_gid = captcha_gid
        self.captcha = captcha


class MailCodeError(LoginError):
    """Raised when mail code is requested"""
    pass


class TwoFactorCodeError(LoginError):
    """Raised when two factor code is requested"""
    pass


# Don't instantiate this class directly!
# Use get_session to support multiple sessions!
class Login:
    def __init__(
            self,
            username: str,
            password: str,
            *,
            login_url: str = 'https://steamcommunity.com/login',
            mobile_login_url: str = 'https://steamcommunity.com/mobilelogin',
            steamguard_url: str = 'https://steamcommunity.com/steamguard',
            headers: Optional[Dict[str, str]] = None,
            http_session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.username = username
        self.__password = password
        self.login_url = login_url
        self.mobile_login_url = mobile_login_url
        self.steamguard_url = steamguard_url
        self._headers = headers
        self._http_session = http_session

    @property
    def headers(self) -> Dict[str, str]:
        if not self._headers:
            self._headers = {'User-Agent': 'Unknown/0.0.0'}

        return self._headers

    @property
    def http(self) -> aiohttp.ClientSession:
        if not self._http_session:
            self._http_session = aiohttp.ClientSession(raise_for_status=True)

        return self._http_session

    async def _new_login_data(
            self,
            authenticator_code: str = '',
            emailauth: str = '',
            captcha_gid: int = -1,
            captcha_text: str = '',
            mobile_login: bool = False,
    ) -> Dict[str, Any]:
        steam_key = await self.get_steam_key(self.username)
        encrypted_password = universe.encrypt_password(steam_key, self.__password)

        data = {
            'username': self.username,
            "password": encrypted_password.decode(),
            "emailauth": emailauth,
            "twofactorcode": authenticator_code,
            "captchagid": captcha_gid,
            "captcha_text": captcha_text,
            "loginfriendlyname": "stlib",
            "rsatimestamp": steam_key.timestamp,
            "remember_login": 'true',
            "donotcache": ''.join([str(int(time.time())), '000']),
        }

        if mobile_login:
            data['oauth_client_id'] = universe._STEAM_UNIVERSE['public']

        return data

    async def get_steam_key(self, username: str) -> universe.SteamKey:
        async with self.http.get(
                f'{self.login_url}/getrsakey/',
                params={'username': username},
                headers=self.headers,
        ) as response:
            json_data = await response.json()

        if json_data['success']:
            public_mod = int(json_data['publickey_mod'], 16)
            public_exp = int(json_data['publickey_exp'], 16)
            timestamp = int(json_data['timestamp'])
        else:
            raise ValueError('Failed to get public key.')

        return universe.SteamKey(rsa.PublicKey(public_mod, public_exp), timestamp)

    async def get_captcha(self, gid: int) -> bytes:
        async with self.http.get(
                f'{self.login_url}/rendercaptcha/',
                params={'gid': gid},
                headers=self.headers,
        ) as response:
            data = await response.read()
            assert isinstance(data, bytes), "rendercaptcha response is not bytes"
            return data

    async def has_phone(self, sessionid: str) -> bool:
        data = {
            'op': "has_phone",
            'sessionid': sessionid,
        }

        async with self.http.post(
                f'{self.steamguard_url}/phoneajax',
                data=data,
                headers=self.headers,
        ) as response:
            json_data = await response.json()
            assert isinstance(json_data, dict), "phoneajax is not a dict"

        if not json_data['success']:
            if 'error_text' in json_data:
                raise LoginError(json_data['error_text'])
            else:
                raise LoginError("Current session is invalid")

        log.debug("User has phone? %s", json_data["has_phone"])

        if json_data["has_phone"]:
            return True
        else:
            return False

    async def do_login(
            self,
            shared_secret: str = '',
            emailauth: str = '',
            captcha_gid: int = -1,
            captcha_text: str = '',
            mobile_login: bool = False,
            time_offset: int = 0,
            authenticator_code: str = '',
    ) -> LoginData:
        if shared_secret:
            server_time = int(time.time()) - time_offset
            authenticator_code = universe.generate_steam_code(server_time, shared_secret)
        else:
            if authenticator_code:
                log.warning("Using external authenticator code to log-in")
            else:
                log.warning("Logging without two-factor authentication.")

        data = await self._new_login_data(authenticator_code, emailauth, captcha_gid, captcha_text, mobile_login)

        if mobile_login:
            login_url = self.mobile_login_url
            cookies = http.cookies.SimpleCookie()
            cookies['mobileClientVersion'] = '0 (2.3.1)'
            cookies['mobileClient'] = "android"
            self.http.cookie_jar.update_cookies(cookies)
        else:
            login_url = self.login_url

        async with self.http.post(
                f'{login_url}/dologin',
                data=data,
                headers=self.headers,
        ) as response:
            json_data = await response.json()
            assert isinstance(json_data, dict), "Json data from dologin is not a dict"

            if json_data['success']:
                oauth_data = {}

                if mobile_login:
                    oauth_data = json.loads(json_data.pop('oauth'))

                return LoginData(json_data, oauth_data)

            if 'message' in json_data and 'too many login failures' in json_data['message']:
                raise LoginBlockedError("Your network is blocked. Please, try again later")
            elif 'emailauth_needed' in json_data and json_data['emailauth_needed']:
                raise MailCodeError("Mail code requested")
            elif 'requires_twofactor' in json_data and json_data['requires_twofactor']:
                raise TwoFactorCodeError("Authenticator code requested")
            elif 'captcha_needed' in json_data and json_data['captcha_needed']:
                if captcha_text and captcha_gid:
                    if 'message' in json_data and not 'verify your humanity' in json_data['message']:
                        raise LoginError(json_data['message'])

                captcha = await self.get_captcha(json_data['captcha_gid'])
                raise CaptchaError(json_data['captcha_gid'], captcha, "Captcha code requested")
            elif mobile_login and 'oauth' not in json_data:
                raise LoginError(f"Unable to log-in on mobile session: {json_data['message']}")
            else:
                raise LoginError(f"Unable to log-in: {json_data['message']}")


def get_session(session_number: int, username: str, password: str, **kwargs) -> Login:
    if len(session_list) <= session_number:
        log.debug(f"Creating a new login session at index {session_number}")
        session = Login(username, password, **kwargs)

        if len(session_list) < session_number:
            log.error(f"Session number is invalid. Session will be created at index {len(session_list)}")

        session_list.insert(session_number, session)
    else:
        log.info(f"Using existent login session at index {session_number}")
        session = session_list[session_number]
        session.username = username
        session.__password = password

    return session
