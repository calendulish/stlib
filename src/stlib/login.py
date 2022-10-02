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
"""
`login` interface is used to interact with undocumented steam login methods
it supports both desktop and mobile login at steam services
"""

import asyncio
import http.cookies
import json
import logging
import time
from typing import Any, Dict, NamedTuple, Optional

import rsa

from . import universe, utils

log = logging.getLogger(__name__)


class LoginData(NamedTuple):
    auth: Dict[str, Any]
    """Auth data"""
    oauth: Dict[str, Any]
    """OAuth data"""


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
class Login(utils.Base):
    def __init__(
            self,
            *,
            login_url: str = 'https://steamcommunity.com/login',
            mobile_login_url: str = 'https://steamcommunity.com/mobilelogin',
            steamguard_url: str = 'https://steamcommunity.com/steamguard',
            api_url: str = 'https://api.steampowered.com',
            **kwargs: Any,
    ) -> None:
        """
        Main login class used to login a user on steam session

        Example:

            ```
            login_session = await Login.new_session(0)
            login_session.username = 'SteamUserName'
            login_session.password = 'SteamPassword'
            await login_session.do_login()
            ```
        """
        super().__init__(**kwargs)
        self._username: Optional[str] = None
        self.__password: Optional[str] = None
        self.login_url = login_url
        self.mobile_login_url = mobile_login_url
        self.steamguard_url = steamguard_url
        self.api_url = api_url
        self.login_trial = 3

    @property
    def username(self) -> str:
        """Steam username"""
        if not self._username:
            raise AttributeError('Username is required to login')

        return self._username

    @username.setter
    def username(self, username: str) -> None:
        self._username = username

    @property
    def password(self) -> None:
        """Protected steam password"""
        raise PermissionError('Passwords are protected')

    @password.setter
    def password(self, __password: str) -> None:
        self.__password = __password

    async def _new_login_data(
            self,
            authenticator_code: str = '',
            emailauth: str = '',
            captcha_gid: int = -1,
            captcha_text: str = '',
            mobile_login: bool = False,
    ) -> Dict[str, Any]:
        steam_key = await self.get_steam_key(self.username)

        if not self.__password:
            raise AttributeError('Password is required to login')

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
            data['oauth_client_id'] = universe.STEAM_UNIVERSE['public']

        return data

    async def get_steam_key(self, username: str) -> universe.SteamKey:
        """
        Get `SteamKey`
        :param username: Steam username as string
        :return: `SteamKey`
        """
        params = {'username': username}
        json_data = await self.request_json(f'{self.login_url}/getrsakey/', params=params)

        if json_data['success']:
            public_mod = int(json_data['publickey_mod'], 16)
            public_exp = int(json_data['publickey_exp'], 16)
            timestamp = int(json_data['timestamp'])
        else:
            raise ValueError('Failed to get public key.')

        return universe.SteamKey(rsa.PublicKey(public_mod, public_exp), timestamp)

    async def get_captcha(self, gid: int) -> bytes:
        """
        Get captcha image
        :param gid: Captcha GID
        :return: Image
        """
        params = {'gid': str(gid)}
        response = await self.request(f'{self.login_url}/rendercaptcha/', params=params, raw_data=True)
        assert isinstance(response.content, bytes), "rendercaptcha response is not bytes"
        return response.content

    async def has_phone(self, sessionid: str) -> bool:
        """
        Check if user has a phone registered on steam account
        :param sessionid: steam session id
        :return: True if success
        """
        data = {
            'op': "has_phone",
            'sessionid': sessionid,
        }

        json_data = await self.request_json(f'{self.steamguard_url}/phoneajax', data=data)

        if not json_data['success']:
            if 'error_text' in json_data:
                raise LoginError(json_data['error_text'])

            raise LoginError("Current session is invalid")

        log.debug("User has phone? %s", json_data["has_phone"])

        return json_data["has_phone"]

    async def do_login(
            self,
            shared_secret: str = '',
            emailauth: str = '',
            captcha_gid: int = -1,
            captcha_text: str = '',
            mobile_login: bool = False,
            authenticator_code: str = '',
    ) -> LoginData:
        """
        Login an user on Steam
        :param shared_secret: User shared secret
        :param emailauth: OTP received by email
        :param captcha_gid: gid of received captcha
        :param captcha_text: text of received captcha
        :param mobile_login: True to request mobile session instead desktop one
        :param authenticator_code: OTP from steam authenticator
        :return: Updated `LoginData`
        """
        _original_fargs = locals().copy()
        _original_fargs.pop('self')

        if shared_secret:
            json_data = await self.request_json(f'{self.api_url}/ISteamWebAPIUtil/GetServerInfo/v1')
            server_time = json_data['servertime']
            authenticator_code = universe.generate_steam_code(server_time, shared_secret)
        else:
            if authenticator_code:
                log.warning("Using external authenticator code to log-in")
            else:
                log.warning("Logging without two-factor authentication.")

        data = await self._new_login_data(authenticator_code, emailauth, captcha_gid, captcha_text, mobile_login)

        if mobile_login:
            login_url = self.mobile_login_url
            cookies: http.cookies.SimpleCookie[str] = http.cookies.SimpleCookie()
            cookies['mobileClientVersion'] = '0 (2.3.1)'
            cookies['mobileClient'] = "android"
            self.update_cookies(cookies)
        else:
            login_url = self.login_url

        json_data = await self.request_json(f'{login_url}/dologin', data=data)

        if json_data['success']:
            oauth_data = {}

            if mobile_login:
                oauth_data = json.loads(json_data.pop('oauth'))

            return LoginData(json_data, oauth_data)

        if 'message' in json_data and 'too many login failures' in json_data['message']:
            raise LoginBlockedError("Your network is blocked. Please, try again later")

        if 'emailauth_needed' in json_data and json_data['emailauth_needed']:
            raise MailCodeError("Mail code requested")

        if 'requires_twofactor' in json_data and json_data['requires_twofactor']:
            if self.login_trial > 0:
                self.login_trial -= 1
                await asyncio.sleep(5)
                login_data = await self.do_login(**_original_fargs)
                return login_data

            raise TwoFactorCodeError("Authenticator code requested")

        if 'captcha_needed' in json_data and json_data['captcha_needed']:
            if captcha_text and captcha_gid:
                if 'message' in json_data and 'verify your humanity' not in json_data['message']:
                    raise LoginError(json_data['message'])

            captcha = await self.get_captcha(json_data['captcha_gid'])
            raise CaptchaError(json_data['captcha_gid'], captcha, "Captcha code requested")

        if mobile_login and 'oauth' not in json_data:
            raise LoginError(f"Unable to log-in on mobile session: {json_data['message']}")

        raise LoginError(f"Unable to log-in: {json_data['message']}")

    async def is_logged_in(self, steamid: universe.SteamId) -> bool:
        try:
            response = await self.request(f'{steamid.profile_url}/edit', allow_redirects=False, raise_for_status=False)
        except LoginError:
            return False

        if 'profile could not be found' in response.content:
            log.error("steamid %s seems invalid", steamid.id64)

        return response.status == 200

    def restore_login(self, steamid: universe.SteamId, token: str, token_secure: str) -> None:
        """
        Restore a previous saved session
        :param steamid: `SteamId`
        :param token: Login token code
        :param token_secure: Login token secure code
        """
        cookies: http.cookies.SimpleCookie[str] = http.cookies.SimpleCookie()
        cookies['steamLogin'] = f'{steamid.id64}%7C%7C{token}'
        cookies['steamLoginSecure'] = f'{steamid.id64}%7C%7C{token_secure}'
        self.update_cookies(cookies)
